# GNS3 Lab — Day 08: IPv4 Address Configuration & Router Interface Setup

Automated build script for the Day 08 three-network topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Router (R1) | VyOS | Open-source, Cisco-like CLI |
| Switches (SW1-3) | Open vSwitch | Built into GNS3, no download needed |
| PC1-PC3 | Alpine Linux | Lightweight full Linux |

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
- Checks all required templates exist, asking before any download.
- Creates the `Day-08-IPv4-Addresses` project (or reuses it).
- Creates 7 nodes and 6 links matching the companion manual's topology.
- Is safe to re-run.

## A note on mask syntax

Cisco IOS's `ip address` command requires the expanded dotted-decimal mask (e.g. `255.0.0.0`); VyOS accepts CIDR slash notation directly (e.g. `15.255.255.254/8`) when assigning an interface address. This is a useful contrast to notice while working through the companion manual's addressing math.

## After the build

Open the `Day-08-IPv4-Addresses` project in the GNS3 GUI, start the nodes, and follow the [Configuration Tasks](../Day-08-Lab-Manual.md#6-configuration-tasks) section of the manual, translating each IOS command to VyOS's `set interfaces ethernet` syntax.
