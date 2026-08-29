#!/usr/bin/env python3
"""
GNS3 automation script for Day 27 - OSPF Reference Bandwidth, Hello
Protocol, and ASBR Default Route Injection.

Builds the same ISPR1/R1/R2/R3/R4/SW1/PC1 topology used in Day 26 (this
lab layers `auto-cost reference-bandwidth` tuning and Hello-packet study
on top of that base), using free, open-source images:

    Role                       Image
    -------------------------  ----------------------------
    Routers (ISPR1, R1-R4)     VyOS
    Switch (SW1)               Open vSwitch (GNS3 built-in)
    PC1                        Alpine Linux

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

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: run `pip install requests` and try again.")

GNS3_URL = "http://localhost:3080/v2"
PROJECT_NAME = "Day-27-OSPF-Reference-Bandwidth"

REQUIRED_TEMPLATES = {
    "VyOS": {
        "download_url": "https://s3.amazonaws.com/s3-us.vyos.io/rolling/current/vyos-rolling-latest.iso",
        "note": "Router role (ISPR1, R1, R2, R3, R4). Open-source, Cisco-like CLI, "
        "supports OSPF cost tuning via `set protocols ospf area 0.0.0.0 ...` "
        "and reference bandwidth-equivalent interface cost overrides.",
    },
    "Open vSwitch": {
        "download_url": None,
        "note": "Switch role (SW1). Built into GNS3 -- no image download needed.",
    },
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "End device (PC1). Lightweight full Linux.",
    },
}

NODES = [
    {"name": "ISPR1", "template": "VyOS", "x": -300, "y": -250},
    {"name": "R1", "template": "VyOS", "x": 0, "y": -200},
    {"name": "R2", "template": "VyOS", "x": -200, "y": -50},
    {"name": "R3", "template": "VyOS", "x": 200, "y": -50},
    {"name": "R4", "template": "VyOS", "x": 0, "y": 100},
    {"name": "SW1", "template": "Open vSwitch", "x": 0, "y": 250},
    {"name": "PC1", "template": "Alpine Linux", "x": 0, "y": 400},
]

LINKS = [
    ("ISPR1", "R1"),
    ("R1", "R2"),
    ("R1", "R3"),
    ("R2", "R4"),
    ("R3", "R4"),
    ("R4", "SW1"),
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
            f"Could not reach GNS3 server at {GNS3_URL}. Is GNS3 running? "
            "Start it and try again."
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
        print(
            f"Please download {name} manually from {info['download_url']} and "
            "import it via Edit > Preferences > Appliances -- this script does "
            "not fetch or install images for you."
        )

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
        f"\nDay 27 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes, then apply "
        "`auto-cost reference-bandwidth`-equivalent cost tuning on every "
        "router identically -- see GNS3/README.md and the Lab Manual."
    )


if __name__ == "__main__":
    main()
