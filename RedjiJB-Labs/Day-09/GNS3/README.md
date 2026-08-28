# GNS3 Lab — Day 09: Interface Configuration & Device Management

Automated build script for the Day 09 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Router (R1) | VyOS | Open-source, Cisco-like CLI |
| Switches (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| PC1-PC4 | Alpine Linux | Lightweight full Linux |

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
- Creates the `Day-09-Interface-Configuration` project (or reuses it).
- Creates 7 nodes and 6 links matching the companion manual's topology.
- Is safe to re-run.

## A note on speed/duplex and unused ports

Open vSwitch doesn't expose Cisco IOS-style `speed`/`duplex` interface sub-commands through the GNS3 GUI; use `ovs-vsctl` on the GNS3 host for virtual link parameters if you want to explore that specifically. The interface-description and unused-port-disabling concepts, however, map directly — practice those against this build, and do the speed/duplex portion of the lab against Packet Tracer or a real/virtual Cisco IOS image.

## After the build

Open the `Day-09-Interface-Configuration` project in the GNS3 GUI, start the nodes, and follow the [Configuration Tasks](../Day-09-Lab-Manual.md#6-configuration-tasks) section of the manual.
