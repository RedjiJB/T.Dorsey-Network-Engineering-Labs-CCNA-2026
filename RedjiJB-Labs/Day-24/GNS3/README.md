# Day 24 GNS3 Lab — Floating Static Routes and Failover Testing

This folder contains an automation script that builds the Day 24 dual-homed topology (R1, R2, ISPBR1, ISPBR2, SW1, SW2, PC1, SRV1) in GNS3 using free/open-source images.

## Requirements

- GNS3 Desktop or GNS3 VM running, with the server API reachable at `http://localhost:3080` (default)
- Python 3.8+ with `requests` installed: `pip install requests`

## Images Used

| Role | Image | Notes |
|---|---|---|
| R1, R2, ISPBR1, ISPBR2 | VyOS | Open-source, Cisco-like CLI; supports static routing and OSPF. |
| SW1, SW2 | Open vSwitch | Built into GNS3, no download needed. |
| PC1, SRV1 | Alpine Linux | Lightweight Linux end hosts. |

## Usage

```bash
python build_lab.py
```

The script never downloads an image without asking first. If a required template is missing, it lists what's missing and prompts before attempting anything.

## After Building

Open the `Day-24-Floating-Static-Routes` project in the GNS3 GUI, start all nodes, and console into R1/R2/ISPBR1/ISPBR2 to follow the OSPF and floating-static-route configuration in `Day-24-Lab-Manual.md`. VyOS uses a different CLI syntax than Cisco IOS for OSPF and static routes (`set protocols ospf ...`, `set protocols static route ...`) — translate the IOS commands in the manual to VyOS `set`/`commit` syntax, or substitute a Cisco IOSv template if you have one imported.
