#!/usr/bin/env python3
"""
GNS3 automation script for Day 21 - Configuring Spanning Tree.

Builds a four-switch, redundantly-linked topology (matching Day 20's
analysis topology) using free, open-source images, for practicing active
STP configuration: root bridge assignment, cost/priority tuning, PortFast,
and BPDU Guard.

    Role                            Image
    ------------------------------  ----------------------------
    Switches (SW1, SW2, SW3, SW4)   Open vSwitch (GNS3 built-in) --
                                     see README for STP config caveats

Requirements:
    - GNS3 running locally with the server API reachable (default http://localhost:3080)
    - Python 3.8+, `requests` installed (pip install requests)

Usage:
    python build_lab.py

The script NEVER downloads an image without asking first.
"""

import sys

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: run `pip install requests` and try again.")

GNS3_URL = "http://localhost:3080/v2"
PROJECT_NAME = "Day-21-Configuring-Spanning-Tree"

REQUIRED_TEMPLATES = {
    "Open vSwitch": {
        "download_url": None,
        "note": "Switch role (SW1-SW4). Built into GNS3 -- no image "
        "download needed. Cannot configure per-VLAN root priority, cost, "
        "port-priority, PortFast, or BPDU Guard the way IOS does -- see README.",
    },
}

NODES = [
    {"name": "SW1", "template": "Open vSwitch", "x": -200, "y": -100},
    {"name": "SW2", "template": "Open vSwitch", "x": 200, "y": -100},
    {"name": "SW3", "template": "Open vSwitch", "x": -200, "y": 150},
    {"name": "SW4", "template": "Open vSwitch", "x": 200, "y": 150},
]

LINKS = [
    ("SW1", "SW2"),
    ("SW1", "SW3"),
    ("SW2", "SW4"),
    ("SW3", "SW4"),
    ("SW1", "SW4"),
    ("SW2", "SW3"),
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
            "\nREMINDER: Open vSwitch cannot reproduce IOS-style per-VLAN "
            "STP configuration (root primary/secondary, cost, port-priority, "
            "PortFast, BPDU Guard). See GNS3/README.md before relying on "
            "this build for the actual configuration steps in this lab.\n"
        )
        return

    print("\nThe following templates are missing from your GNS3 install:\n")
    for name in missing:
        info = REQUIRED_TEMPLATES[name]
        print(f"  - {name}: {info['note']}")
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
        f"\nDay 21 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes."
    )


if __name__ == "__main__":
    main()
