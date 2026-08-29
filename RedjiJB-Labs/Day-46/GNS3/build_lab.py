#!/usr/bin/env python3
"""
GNS3 automation script for Day 46 - Voice VLANs & Router-on-a-Stick (ROAS).

Builds a single-switch, single-router topology demonstrating access ports
carrying both a data VLAN (untagged) and a voice VLAN (802.1Q-tagged), with
Router-on-a-Stick providing Layer 3 gateways for both, using free,
open-source images:

    Role                  Image
    --------------------  ----------------------------
    Router (R1)           VyOS
    Switch (SW1)          Open vSwitch (GNS3 built-in)
    PCs / Phones          Linux (Alpine)

NOTE: GNS3's free image set has no native Cisco IP phone equivalent. PH1 and
PH2 are represented as Alpine Linux hosts. To approximate real phone
behavior (802.1Q-tagged voice traffic on an access port), configure a
VLAN-tagged subinterface on the Alpine host, e.g.:

    apk add vlan
    modprobe 8021q
    ip link add link eth0 name eth0.20 type vlan id 20
    ip addr add 192.168.20.10/24 dev eth0.20
    ip link set eth0.20 up

This sends 802.1Q-tagged frames from the host itself, mirroring what a real
IP phone does when it tags voice traffic before it ever reaches the switch.
PC1/PC2 stay untagged (plain DHCP/static IP on eth0) to represent data
traffic, matching the manual's frame-inspection results.

Requirements:
    - GNS3 running locally with the server API reachable (default http://localhost:3080)
    - Python 3.8+, `requests` installed (pip install requests)

Usage:
    python build_lab.py

The script NEVER downloads an image without asking first. If a required
template is missing from your GNS3 install, it will show you what's missing,
ask whether to attempt a download of the open-source image, and only proceed
on an explicit "y".
"""

import sys
import urllib.request
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: run `pip install requests` and try again.")

GNS3_URL = "http://localhost:3080/v2"
PROJECT_NAME = "Day-46-Voice-VLANs"

REQUIRED_TEMPLATES = {
    "VyOS": {
        "download_url": "https://s3.amazonaws.com/s3-us.vyos.io/rolling/current/vyos-rolling-latest.iso",
        "note": "Router role (R1), providing Router-on-a-Stick. Open-source, Cisco-like CLI.",
    },
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "End devices (PC1, PC2 = data; PH1, PH2 = voice, simulated via a tagged subinterface).",
    },
    "Open vSwitch": {
        "download_url": None,
        "note": "Access/trunk switch role (SW1). Built into GNS3 — no image download needed.",
    },
}

# Topology definition: nodes and the links between them.
NODES = [
    {"name": "PC1", "template": "Alpine Linux", "x": -400, "y": -150},
    {"name": "PH1", "template": "Alpine Linux", "x": -400, "y": -50},
    {"name": "PC2", "template": "Alpine Linux", "x": -400, "y": 150},
    {"name": "PH2", "template": "Alpine Linux", "x": -400, "y": 250},
    {"name": "SW1", "template": "Open vSwitch", "x": -200, "y": 50},
    {"name": "R1", "template": "VyOS", "x": 0, "y": 50},
]

# PC1 daisy-chains through PH1's second port in the real topology, but since
# Alpine hosts here are single-NIC stand-ins, both connect directly to SW1
# on separate access ports, each carrying its data/voice VLAN assignment.
LINKS = [
    ("PC1", "SW1"),
    ("PH1", "SW1"),
    ("PC2", "SW1"),
    ("PH2", "SW1"),
    ("SW1", "R1"),
]


def gns3_get(path):
    r = requests.get(f"{GNS3_URL}{path}")
    r.raise_for_status()
    return r.json()


def gns3_post(path, json=None):
    r = requests.post(f"{GNS3_URL}{path}", json=json)
    r.raise_for_status()
    return r.json()


def check_server():
    try:
        requests.get(f"{GNS3_URL}/version", timeout=3)
    except requests.exceptions.ConnectionError:
        sys.exit(
            "Could not reach GNS3 server at "
            f"{GNS3_URL}. Is GNS3 running? Start it and try again."
        )


def check_templates():
    """Verify every required template exists; prompt before any download."""
    existing = {t["name"] for t in gns3_get("/templates")}
    missing = [name for name in REQUIRED_TEMPLATES if name not in existing]

    if not missing:
        print("All required templates found in GNS3.")
        return

    print("\nThe following templates are missing from your GNS3 install:\n")
    for name in missing:
        info = REQUIRED_TEMPLATES[name]
        print(f"  - {name}: {info['note']}")

    print(
        "\nThese must be imported as GNS3 templates (Edit > Preferences > "
        "Appliances, or drag-and-drop a .gns3a) before this script can build "
        "the topology.\n"
    )

    for name in missing:
        info = REQUIRED_TEMPLATES[name]
        if info["download_url"] is None:
            continue
        answer = (
            input(f"Attempt to download the {name} image now? [y/N]: ")
            .strip()
            .lower()
        )
        if answer != "y":
            print(f"Skipping download of {name}. You'll need to import it manually.")
            continue
        dest = Path.cwd() / f"{name.replace(' ', '_')}_download"
        print(f"Downloading {name} from {info['download_url']} ...")
        try:
            urllib.request.urlretrieve(info["download_url"], dest)
            print(
                f"Downloaded to {dest}. Import it into GNS3 as a template "
                "(Edit > Preferences > Appliances > New Template) before "
                "re-running this script."
            )
        except Exception as e:
            print(f"Download failed: {e}")

    sys.exit(
        "\nImport the missing templates above into GNS3, then re-run this script."
    )


def get_or_create_project():
    for p in gns3_get("/projects"):
        if p["name"] == PROJECT_NAME:
            print(f"Using existing project '{PROJECT_NAME}'.")
            return p
    print(f"Creating project '{PROJECT_NAME}'.")
    return gns3_post("/projects", {"name": PROJECT_NAME})


def get_template_id(name):
    for t in gns3_get("/templates"):
        if t["name"] == name:
            return t["template_id"]
    raise RuntimeError(f"Template '{name}' not found even after check_templates().")


def create_nodes(project_id):
    node_ids = {}
    existing = {n["name"]: n for n in gns3_get(f"/projects/{project_id}/nodes")}
    for node in NODES:
        if node["name"] in existing:
            print(f"Node '{node['name']}' already exists, skipping creation.")
            node_ids[node["name"]] = existing[node["name"]]["node_id"]
            continue
        template_id = get_template_id(node["template"])
        created = gns3_post(
            f"/projects/{project_id}/templates/{template_id}",
            {"x": node["x"], "y": node["y"]},
        )
        node_ids[node["name"]] = created["node_id"]
        print(f"Created node '{node['name']}' ({node['template']}).")
    return node_ids


def create_links(project_id, node_ids):
    existing_links = gns3_get(f"/projects/{project_id}/links")
    linked_pairs = set()
    next_port = {}  # node_id -> next free port_number, tracks ports already in use

    for link in existing_links:
        names = tuple(sorted(n["node_id"] for n in link["nodes"]))
        linked_pairs.add(names)
        for n in link["nodes"]:
            next_port[n["node_id"]] = max(
                next_port.get(n["node_id"], 0), n["port_number"] + 1
            )

    for a, b in LINKS:
        node_a, node_b = node_ids[a], node_ids[b]
        pair = tuple(sorted((node_a, node_b)))
        if pair in linked_pairs:
            print(f"Link {a} <-> {b} already exists, skipping.")
            continue

        port_a = next_port.get(node_a, 0)
        port_b = next_port.get(node_b, 0)

        gns3_post(
            f"/projects/{project_id}/links",
            {
                "nodes": [
                    {"node_id": node_a, "adapter_number": 0, "port_number": port_a},
                    {"node_id": node_b, "adapter_number": 0, "port_number": port_b},
                ]
            },
        )
        next_port[node_a] = port_a + 1
        next_port[node_b] = port_b + 1
        linked_pairs.add(pair)
        print(f"Linked {a} (port {port_a}) <-> {b} (port {port_b}).")


def main():
    check_server()
    check_templates()
    project = get_or_create_project()
    node_ids = create_nodes(project["project_id"])
    create_links(project["project_id"], node_ids)
    print(
        f"\nDay 46 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes. See README.md for the "
        "SW1 access/voice VLAN and R1 ROAS subinterface configuration to "
        "apply once the nodes are running, and for how to simulate tagged "
        "voice traffic from the Alpine PH1/PH2 hosts."
    )


if __name__ == "__main__":
    main()
