#!/usr/bin/env python3
"""
GNS3 automation script for Day 29 - OSPF Reference Bandwidth, Hello Protocol,
and ASBR Default Route Injection.

Builds a 4-router OSPF area-0 backbone (R1-R4) plus a simulated ISP edge
router, an access switch and end host on R4's LAN, using free, open-source
images:

    Role                          Image
    --------------------------    ----------------------------
    Routers (R1, R2, R3, R4, ISP) VyOS
    Switch (SW1)                  Open vSwitch (GNS3 built-in)
    PC (PC1)                      Linux (Alpine)

VyOS OSPF configuration uses a different syntax family than IOS. Roughly:

    IOS:
        router ospf 1
         network 10.0.12.0 0.0.0.3 area 0
         passive-interface loopback0
         auto-cost reference-bandwidth 10000
         default-information originate

    VyOS:
        set protocols ospf area 0 network 10.0.12.0/30
        set protocols ospf passive-interface lo
        set protocols ospf auto-cost reference-bandwidth 10000
        set protocols ospf default-information originate
        commit

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
PROJECT_NAME = "Day-29-OSPF-Reference-Bandwidth-ASBR"

REQUIRED_TEMPLATES = {
    "VyOS": {
        "download_url": "https://s3.amazonaws.com/s3-us.vyos.io/rolling/current/vyos-rolling-latest.iso",
        "note": "Router role (R1-R4, ISP). Open-source, Cisco-like CLI.",
    },
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "End host (PC1).",
    },
    "Open vSwitch": {
        "download_url": None,
        "note": "LAN switch role (SW1). Built into GNS3 — no image download needed.",
    },
}

NODES = [
    {"name": "ISP", "template": "VyOS", "x": 300, "y": -150},
    {"name": "R1", "template": "VyOS", "x": 100, "y": -150},
    {"name": "R2", "template": "VyOS", "x": -100, "y": -250},
    {"name": "R3", "template": "VyOS", "x": -100, "y": -50},
    {"name": "R4", "template": "VyOS", "x": -300, "y": -150},
    {"name": "SW1", "template": "Open vSwitch", "x": -500, "y": -150},
    {"name": "PC1", "template": "Alpine Linux", "x": -650, "y": -150},
]

LINKS = [
    ("R1", "ISP"),      # 203.0.113.0/30
    ("R1", "R2"),       # 10.0.12.0/30
    ("R1", "R3"),       # 10.0.13.0/30
    ("R2", "R4"),       # 10.0.24.0/30
    ("R3", "R4"),       # 10.0.34.0/30
    ("R4", "SW1"),      # 192.168.4.0/24 (R4 LAN)
    ("SW1", "PC1"),
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
        f"\nDay 29 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes. See README.md for the "
        "VyOS OSPF, reference-bandwidth, and default-information-originate "
        "configuration to apply on each router once they're running."
    )


if __name__ == "__main__":
    main()
