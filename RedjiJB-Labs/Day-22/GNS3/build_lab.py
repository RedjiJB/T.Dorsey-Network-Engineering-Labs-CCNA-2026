#!/usr/bin/env python3
"""
GNS3 automation script for Day 22 - RSTP: Root Bridge Behavior and Link Types.

Builds a 4-switch, 2-hub topology using free, open-source images:

    Role                     Image
    -----------------------  ----------------------------
    Switches (SW1-SW4)       Open vSwitch (GNS3 built-in)
    Hubs (Hub0, Hub1)        Open vSwitch, unmanaged/STP-disabled (approximation - see README)
    PCs                      Linux (Alpine)

IMPORTANT LIMITATION: GNS3's built-in Open vSwitch has limited/no native
RSTP support, so the root-bridge Backup-port behavior this lab is built
around cannot be fully reproduced with OVS alone. See GNS3/README.md for
the Cisco IOU/IOL alternative if you have access to those images.

Requirements:
    - GNS3 running locally with the server API reachable (default http://localhost:3080)
    - Python 3.8+, `requests` installed (pip install requests)

Usage:
    python build_lab.py

The script NEVER downloads an image without asking first.
"""

import sys
import urllib.request
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: run `pip install requests` and try again.")

GNS3_URL = "http://localhost:3080/v2"
PROJECT_NAME = "Day-22-RSTP-Root-Bridge"

REQUIRED_TEMPLATES = {
    "Open vSwitch": {
        "download_url": None,
        "note": "Switch role (SW1-SW4) and hub approximation (Hub0, Hub1). "
        "Built into GNS3 - no image download needed. NOTE: limited/no "
        "native RSTP support - see README.md for the STP-capable "
        "Cisco IOU/IOL alternative.",
    },
    "Alpine Linux": {
        "download_url": "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/",
        "note": "End devices (PCs).",
    },
}

NODES = [
    {"name": "SW1", "template": "Open vSwitch", "x": 0, "y": -200},
    {"name": "SW2", "template": "Open vSwitch", "x": -200, "y": -50},
    {"name": "SW3", "template": "Open vSwitch", "x": 0, "y": 100},
    {"name": "SW4", "template": "Open vSwitch", "x": 200, "y": -50},
    {"name": "Hub0", "template": "Open vSwitch", "x": 0, "y": -50},
    {"name": "Hub1", "template": "Open vSwitch", "x": -100, "y": 100},
    {"name": "PC-Root", "template": "Alpine Linux", "x": 0, "y": -350},
    {"name": "PC3", "template": "Alpine Linux", "x": 0, "y": 250},
    {"name": "PC6", "template": "Alpine Linux", "x": 350, "y": -50},
]

# SW1 (root) connects to SW2 via direct P2p link, and to SW3/SW4 via Hub0
# (the shared segment that produces the Backup port). SW2 also reaches
# SW3/SW4 via Hub1, providing the redundant Alternate-port path.
LINKS = [
    ("PC-Root", "SW1"),
    ("SW1", "SW2"),
    ("SW1", "Hub0"),
    ("Hub0", "SW3"),
    ("Hub0", "SW4"),
    ("SW2", "Hub1"),
    ("Hub1", "SW3"),
    ("Hub1", "SW4"),
    ("SW3", "PC3"),
    ("SW4", "PC6"),
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
            "\nReminder: Open vSwitch has limited/no native RSTP support. "
            "See GNS3/README.md before relying on this build for the "
            "root-bridge Backup-port analysis in the Lab Manual.\n"
        )
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
        f"\nDay 22 topology built in project '{PROJECT_NAME}'. "
        "Open it in the GNS3 GUI to start the nodes. "
        "Remember: OVS has limited RSTP support - see README.md."
    )


if __name__ == "__main__":
    main()
