#!/usr/bin/env python3
"""
GNS3 automation script for Day 23 - EtherChannel: LACP, PAgP, Static, and Load Balancing.

Builds the ASW1/ASW2/DSW1/DSW2 topology from Labs/Day-23-EtherChannel...md
using free, open-source images:

    Role                        Image
    --------------------------  ----------------------------
    Switches (ASW1/2, DSW1/2)   Open vSwitch (GNS3 built-in)
    PC1, PC2, SRV1              Alpine Linux

Note: GNS3's Open vSwitch nodes do not run Cisco IOS EtherChannel/LACP
negotiation themselves -- this script builds the physical topology (multiple
parallel links between each switch pair) so you can attach real IOS switch
images/IOSv-L2 if you have them, or use it purely to visualize the bundle
layout. If you have IOSvL2 templates imported, swap "Open vSwitch" for your
IOSvL2 template name in NODES below.

Requirements:
    - GNS3 running locally with the server API reachable (default http://localhost:3080)
    - Python 3.8+, `requests` installed (pip install requests)

Usage:
    python build_lab.py
"""

import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: run `pip install requests` and try again.")

GNS3_URL = "http://localhost:3080/v2"
PROJECT_NAME = "Day-23-EtherChannel"

REQUIRED_TEMPLATES = {
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "End devices (PC1, PC2, SRV1). Lightweight full Linux.",
    },
    "Open vSwitch": {
        "download_url": None,
        "note": "Switch role (ASW1, ASW2, DSW1, DSW2). Built into GNS3 -- no "
        "image download needed. Note: does not run real LACP/PAgP "
        "negotiation -- use for topology/wiring visualization, or "
        "substitute an IOSvL2 template if you have one imported.",
    },
}

NODES = [
    {"name": "PC1", "template": "Alpine Linux", "x": -500, "y": -150},
    {"name": "PC2", "template": "Alpine Linux", "x": -500, "y": -50},
    {"name": "ASW1", "template": "Open vSwitch", "x": -300, "y": -100},
    {"name": "DSW1", "template": "Open vSwitch", "x": -100, "y": -100},
    {"name": "DSW2", "template": "Open vSwitch", "x": 100, "y": -100},
    {"name": "ASW2", "template": "Open vSwitch", "x": 300, "y": -100},
    {"name": "SRV1", "template": "Alpine Linux", "x": 500, "y": -100},
]

# Two parallel links per bundle to reflect the EtherChannel member count.
LINKS = [
    ("PC1", "ASW1"),
    ("PC2", "ASW1"),
    ("ASW1", "DSW1"),  # LACP member 1
    ("ASW1", "DSW1"),  # LACP member 2
    ("DSW1", "DSW2"),  # Static routed member 1
    ("DSW1", "DSW2"),  # Static routed member 2
    ("DSW2", "ASW2"),  # PAgP member 1
    ("DSW2", "ASW2"),  # PAgP member 2
    ("ASW2", "SRV1"),
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
            f"Could not reach GNS3 server at {GNS3_URL}. Is GNS3 running? "
            "Start it and try again."
        )


def check_templates():
    existing = {t["name"] for t in gns3_get("/templates")}
    missing = [name for name in REQUIRED_TEMPLATES if name not in existing]

    if not missing:
        print("All required templates found in GNS3.")
        return

    print("\nThe following templates are missing from your GNS3 install:\n")
    for name in missing:
        print(f"  - {name}: {REQUIRED_TEMPLATES[name]['note']}")

    for name in missing:
        info = REQUIRED_TEMPLATES[name]
        if info["download_url"] is None:
            continue
        answer = input(f"Attempt to download the {name} image now? [y/N]: ").strip().lower()
        if answer != "y":
            print(f"Skipping download of {name}. You'll need to import it manually.")
            continue
        print(
            f"Please download {name} manually from {info['download_url']} and "
            "import it via Edit > Preferences > Appliances."
        )

    sys.exit("\nImport the missing templates above into GNS3, then re-run this script.")


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
    next_port = {}
    link_count = {}  # (a,b) sorted pair -> how many links already exist between them

    for link in existing_links:
        ids = tuple(sorted(n["node_id"] for n in link["nodes"]))
        link_count[ids] = link_count.get(ids, 0) + 1
        for n in link["nodes"]:
            next_port[n["node_id"]] = max(next_port.get(n["node_id"], 0), n["port_number"] + 1)

    # Determine how many links this script wants between each pair
    wanted = {}
    for a, b in LINKS:
        pair = (a, b)
        wanted[pair] = wanted.get(pair, 0) + 1

    created_so_far = {}
    for a, b in LINKS:
        node_a, node_b = node_ids[a], node_ids[b]
        pair_ids = tuple(sorted((node_a, node_b)))
        pair_key = (a, b)
        already = link_count.get(pair_ids, 0)
        made = created_so_far.get(pair_key, 0)
        if made < already:
            created_so_far[pair_key] = made + 1
            print(f"Link {a} <-> {b} (instance {made + 1}) already exists, skipping.")
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
        created_so_far[pair_key] = made + 1
        print(f"Linked {a} (port {port_a}) <-> {b} (port {port_b}).")


def main():
    check_server()
    check_templates()
    project = get_or_create_project()
    node_ids = create_nodes(project["project_id"])
    create_links(project["project_id"], node_ids)
    print(
        f"\nDay 23 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes."
    )


if __name__ == "__main__":
    main()
