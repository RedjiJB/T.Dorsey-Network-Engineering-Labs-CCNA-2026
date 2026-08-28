# Day 25 GNS3 Lab — EIGRP Multi-Autonomous System, Auto-Summary, and Unequal-Cost Load Balancing

This folder contains an automation script that builds the Day 25 four-router EIGRP partial mesh (R1, R2, R3, R4, SW1, PC1) in GNS3 using free/open-source images.

## Requirements

- GNS3 Desktop or GNS3 VM running, with the server API reachable at `http://localhost:3080` (default)
- Python 3.8+ with `requests` installed: `pip install requests`

## Images Used

| Role | Image | Notes |
|---|---|---|
| R1, R2, R3, R4 | VyOS | Open-source, Cisco-like CLI. VyOS routes via FRR — check your build's EIGRP support before relying on it; if unsupported, substitute a Cisco IOSv template for full parity with the manual. |
| SW1 | Open vSwitch | Built into GNS3, no download needed. |
| PC1 | Alpine Linux | Lightweight Linux end host. |

## Usage

```bash
python build_lab.py
```

The script never downloads an image without asking first. If a required template is missing, it lists what's missing and prompts before attempting anything.

## After Building

Open the `Day-25-EIGRP` project in the GNS3 GUI, start all nodes, and console into R1–R4 to follow the addressing and EIGRP configuration in `Day-25-Lab-Manual.md`.
