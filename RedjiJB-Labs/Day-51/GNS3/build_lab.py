#!/usr/bin/env python3
"""
GNS3 automation script for Day 51 - Dynamic ARP Inspection (DAI).

Builds the same R1 (DHCP server) / SW1 / SW2 / PC1 topology used in Day 50
(this lab layers DAI on top of that already-working DHCP Snooping design)
using free, open-source images:

    Role              Image
    ----------------  ----------------------------
    Router (R1)       VyOS
    Switches          Open vSwitch (GNS3 built-in)
    PC1               Alpine Linux

IMPORTANT LIMITATION: Open vSwitch does not implement Cisco `ip arp
inspection` (or `ip dhcp snooping`, which DAI depends on). See README.md
for how to approximate the concepts for study purposes only.

Requirements:
    - GNS3 running locally, server API reachable (default http://localhost:3080)
    - Python 3.8+, `requests` installed (pip install requests)

Usage:
    python build_lab.py

Never downloads an image without asking first.
"""

import sys
import urllib.request
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: run `pip install requests` and try again.")

GNS3_URL = "http://localhost:3080/v2"
PROJECT_NAME = "Day-51-Dynamic-ARP-Inspection"

REQUIRED_TEMPLATES = {
    "VyOS": {
        "download_url": "https://s3.amazonaws.com/s3-us.vyos.io/rolling/current/vyos-rolling-latest.iso",
        "note": "DHCP server role (R1). Open-source, Cisco-like CLI.",
    },
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "DHCP client (PC1). Lightweight full Linux.",
    },
    "Open vSwitch": {
        "download_url": None,
        "note": "Switch role (SW1, SW2). Built into GNS3 - no image download needed. "
        "Does NOT support ip arp inspection or ip dhcp snooping - see README.md.",
    },
}

NODES = [
    {"name": "R1", "template": "VyOS", "x": -400, "y": 0},
    {"name": "SW1", "template": "Open vSwitch", "x": -200, "y": 0},
    {"name": "SW2", "template": "Open vSwitch", "x": 0, "y": 0},
    {"name": "PC1", "template": "Alpine Linux", "x": 200, "y": 0},
]

LINKS = [
    ("R1", "SW1"),
    ("SW1", "SW2"),
    ("SW2", "PC1"),
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
    existing = {t["name"] for t in gns3_get("/templates")}
    missing = [name for name in REQUIRED_TEMPLATES if name not in existing]

    if not missing:
        print("All required templates found in GNS3.")
        print(
            "\nREMINDER: Open vSwitch cannot enforce `ip arp inspection` or "
            "`ip dhcp snooping`. See GNS3/README.md before relying on this "
            "build for the actual DAI configuration steps in this lab.\n"
        )
        return

    print("\nThe following templates are missing from your GNS3 install:\n")
    for name in missing:
        info = REQUIRED_TEMPLATES[name]
        print(f"  - {name}: {info['note']}")

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
            print(f"Downloaded to {dest}. Import it into GNS3 as a template.")
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
    next_port = {}

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
        f"\nDay 51 topology built in project '{PROJECT_NAME}'. "
        "Remember: Open vSwitch does not enforce Dynamic ARP Inspection - "
        "see README.md."
    )


if __name__ == "__main__":
    main()
