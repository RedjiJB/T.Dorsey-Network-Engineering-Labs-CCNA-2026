# Day 23 GNS3 Lab — EtherChannel

This folder contains an automation script that builds the Day 23 EtherChannel topology (ASW1/ASW2 access switches, DSW1/DSW2 distribution switches, PC1/PC2, SRV1) in GNS3 using free/open-source images.

## Requirements

- GNS3 Desktop or GNS3 VM running, with the server API reachable at `http://localhost:3080` (default)
- Python 3.8+ with `requests` installed: `pip install requests`

## Images Used

| Role | Image | Notes |
|---|---|---|
| ASW1, ASW2, DSW1, DSW2 | Open vSwitch | Built into GNS3, no download needed. Does **not** run real Cisco LACP/PAgP negotiation — use for topology/wiring layout, or swap in an IOSvL2 template if you own one, by editing `NODES` in `build_lab.py`. |
| PC1, PC2, SRV1 | Alpine Linux | Lightweight Linux end hosts. |

## Usage

```bash
python build_lab.py
```

The script never downloads an image without asking first. If a required template is missing, it lists what's missing and prompts before attempting anything.

It builds two parallel links between each switch pair that represents an EtherChannel bundle in the lab manual (ASW1↔DSW1, DSW1↔DSW2, DSW2↔ASW2), so the physical redundancy is visible in the canvas even though GNS3's Open vSwitch node itself doesn't negotiate LACP/PAgP.

## After Building

Open the `Day-23-EtherChannel` project in the GNS3 GUI, start all nodes, and console into each switch to follow the CLI steps in `Day-23-Lab-Manual.md`. If you substituted real IOSvL2 images, the LACP/PAgP/static configuration and verification commands in the manual will work exactly as written.
