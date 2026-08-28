# GNS3 Lab — Day 01: Network Devices & Enterprise Topology

Automated build script for the Day 01 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Routers (R1, R2, Internet) | VyOS | Open-source, Cisco-like CLI |
| Switches (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| Firewalls (FW1, FW2) | pfSense CE | Community Edition, requires manual download from Netgate (see below) |
| PCs / Servers / Attacker | Alpine Linux | Lightweight full Linux |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. Templates imported into GNS3 for VyOS, pfSense CE, and Alpine Linux. Open vSwitch is built-in.

## Running the build

```bash
python build_lab.py
```

The script:
- Checks the GNS3 server is reachable.
- Checks all required templates exist. If any are missing, it lists them and **asks before attempting any download** — nothing is downloaded silently.
- Creates the `Day-01-Network-Devices` project (or reuses it if it already exists).
- Creates all 12 nodes and 11 links matching the topology in [`Labs/Day-01-Network-Devices.md`](../../Labs/Day-01-Network-Devices.md).
- Is safe to re-run — it skips nodes/links that already exist.

## A note on pfSense

Netgate's pfSense CE download requires selecting an architecture/release from their site and doesn't offer a stable direct-download link, so this script cannot fully automate that image. Download it manually from https://www.pfsense.org/download/ and import it as a GNS3 template first; the script will detect it once imported.

## After the build

Open the `Day-01-Network-Devices` project in the GNS3 GUI, start the nodes, and follow the [command walkthrough](../../Labs/Day-01-Network-Devices.md#command-walkthrough--initial-device-setup) to configure each device.
