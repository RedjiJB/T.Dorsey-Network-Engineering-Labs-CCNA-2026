# GNS3 Lab — Day 02: Connecting Network Devices

Automated build script for the Day 02 two-site topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Routers (R1-R4) | VyOS | Open-source, Cisco-like CLI |
| Switches (SW1-SW8) | Open vSwitch | Built into GNS3, no download needed |
| PCs / Server | Alpine Linux | Lightweight full Linux |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. Templates imported into GNS3 for VyOS and Alpine Linux. Open vSwitch is built-in.

## Running the build

```bash
python build_lab.py
```

The script:
- Checks the GNS3 server is reachable.
- Checks all required templates exist. If any are missing, it lists them and **asks before attempting any download** — nothing is downloaded silently.
- Creates the `Day-02-Connecting-Devices` project (or reuses it if it already exists).
- Creates all 16 nodes and 16 links matching the topology in the companion manual.
- Is safe to re-run — it skips nodes/links that already exist.

## A note on the cable-selection exercise

GNS3 virtual Ethernet links do not model copper vs. multi-mode vs. single-mode fiber or physical distance — that distinction is a Packet Tracer / design-reasoning exercise. Use this GNS3 build to practice the addressing plan, router configuration, and routing/verification portions of the lab; use the companion manual's Section 6 (and Packet Tracer itself) for the cable-type decision-making.

## After the build

Open the `Day-02-Connecting-Devices` project in the GNS3 GUI, start the nodes, and follow the [Configuration Tasks](../Day-02-Lab-Manual.md#6-configuration-tasks) section of the manual to configure each device.
