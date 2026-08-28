# Day 26 GNS3 Lab — OSPF ASBR Default Route Injection and Passive Interface Design

This folder contains an automation script that builds the Day 26 topology (ISPR1, R1, R2, R3, R4, SW1, PC1) in GNS3 using free/open-source images.

## Requirements

- GNS3 Desktop or GNS3 VM running, with the server API reachable at `http://localhost:3080` (default)
- Python 3.8+ with `requests` installed: `pip install requests`

## Images Used

| Role | Image | Notes |
|---|---|---|
| ISPR1, R1, R2, R3, R4 | VyOS | Open-source, Cisco-like CLI, supports OSPF single-area and default-route redistribution (`set protocols ospf ...`, `set protocols static route 0.0.0.0/0 ...`). |
| SW1 | Open vSwitch | Built into GNS3, no download needed. |
| PC1 | Alpine Linux | Lightweight Linux end host. |

## Usage

```bash
python build_lab.py
```

The script never downloads an image without asking first. If a required template is missing, it lists what's missing and prompts before attempting anything.

## After Building

Open the `Day-26-OSPF-ASBR` project in the GNS3 GUI, start all nodes, and console into each router to follow the addressing, OSPF, and ASBR configuration in `Day-26-Lab-Manual.md`. Translate the IOS commands to VyOS `set`/`commit` syntax, or substitute a Cisco IOSv template if you have one imported for exact CLI parity.
