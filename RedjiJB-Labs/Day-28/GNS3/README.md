# Day 28 GNS3 Lab — OSPF Troubleshooting

This folder contains an automation script that builds the Day 28 five-router OSPF troubleshooting topology (R1-R5, SW1-SW3, PC1, PC2) in GNS3 using free/open-source images.

## Requirements

- GNS3 Desktop or GNS3 VM running, with the server API reachable at `http://localhost:3080` (default)
- Python 3.8+ with `requests` installed: `pip install requests`

## Images Used

| Role | Image | Notes |
|---|---|---|
| R1, R2, R3, R4, R5 | VyOS | Open-source, Cisco-like CLI, supports OSPF. |
| SW1, SW2, SW3 | Open vSwitch | Built into GNS3, no download needed. |
| PC1, PC2 | Alpine Linux | Lightweight Linux end hosts. |

## Usage

```bash
python build_lab.py
```

The script never downloads an image without asking first. If a required template is missing, it lists what's missing and prompts before attempting anything.

## Important: This Builds a Working Topology

Unlike a typical build script, this one is meant to support a **troubleshooting** exercise. It wires up the topology correctly. To actually practice Day 28's lab, deliberately introduce the five faults described in `Day-28-Lab-Manual.md` Section 6 after building:

1. Remove the serial clock rate on the R1↔R2 DCE side
2. Remove R3's LAN `network` statement from its OSPF process
3. Mismatch the area ID on one of R2/R4/R5's SW3-facing interfaces
4. Remove R5's static default route, or its `default-information originate` line (or both)
5. (Optional) introduce your own sixth fault for extra practice

Then either work through the diagnosis yourself, or hand the broken topology to a study partner cold.

## After Building

Open the `Day-28-OSPF-Troubleshooting` project in the GNS3 GUI, start all nodes, and console into each router to follow the diagnosis and repair steps in `Day-28-Lab-Manual.md`.
