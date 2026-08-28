#!/usr/bin/env python3
"""
GNS3 automation script for Day 28 - OSPF Troubleshooting: Serial Links,
Neighbor Failures, and Missing Routes.

Builds the R1-R5 topology from
Labs/Day-28-OSPF-Troubleshooting...md using free, open-source images:

    Role                    Image
    ----------------------  ----------------------------
    Routers (R1-R5)         VyOS
    Switches (SW1-SW3)      Open vSwitch (GNS3 built-in)
    PC1, PC2                Alpine Linux

This script builds the topology CORRECTLY CONFIGURED end-to-end. To
practice the troubleshooting scenario itself, deliberately introduce the
five faults described in the lab manual (missing serial clock rate, missing
R3 LAN network statement, mismatched area ID on the SW3 segment, missing
static default route or `default-information originate` on R5) before
handing the lab to a study partner or attempting the diagnosis yourself.

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
PROJECT_NAME = "Day-28-OSPF-Troubleshooting"

REQUIRED_TEMPLATES = {
    "VyOS": {
        "download_url": "https://s3.amazonaws.com/s3-us.vyos.io/rolling/current/vyos-rolling-latest.iso",
        "note": "Router role (R1-R5). Open-source, Cisco-like CLI, supports OSPF.",
    },
    "Open vSwitch": {
        "download_url": None,
        "note": "Switch role (SW1, SW2, SW3). Built into GNS3 -- no image download needed.",
    },
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "End devices (PC1, PC2). Lightweight full Linux.",
    },
}

NODES = [
    {"name": "PC1", "template": "Alpine Linux", "x": -600, "y": -200},
    {"name": "SW1", "template": "Open vSwitch", "x": -450, "y": -200},
    {"name": "R1", "template": "VyOS", "x": -300, "y": -200},
    {"name": "R2", "template": "VyOS", "x": -100, "y": -300},
    {"name": "SW3", "template": "Open vSwitch", "x": 100, "y": -100},
    {"name": "R5", "template": "VyOS", "x": -100, "y": 0},
    {"name": "R4", "template": "VyOS", "x": 300, "y": -200},
    {"name": "R3", "template": "VyOS", "x": 500, "y": -100},
    {"name": "SW2", "template": "Open vSwitch", "x": 650, "y": -100},
    {"name": "PC2", "template": "Alpine Linux", "x": 800, "y": -100},
]

LINKS = [
    ("PC1", "SW1"),
    ("SW1", "R1"),
    ("R1", "R2"),   # serial link, Task 1 fault site
    ("R1", "R5"),   # serial link
    ("R2", "SW3"),
    ("R4", "SW3"),
    ("R5", "SW3"),  # Task 3 fault site (area mismatch)
    ("R4", "R3"),   # serial link
    ("R3", "SW2"),  # Task 2 fault site (missing network statement)
    ("SW2", "PC2"),
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
        f"\nDay 28 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes."
    )


if __name__ == "__main__":
    main()
