# GNS3 Lab — Day 04: Basic Device Security & Cisco IOS Administration

Automated build script for the Day 04 hardening topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Router (R1) | VyOS | Open-source, Cisco-like CLI |
| Switch (SW1) | Open vSwitch | Built into GNS3, no download needed |
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
- Creates the `Day-04-Basic-Device-Security` project (or reuses it).
- Creates 5 nodes and 4 links matching the companion manual's topology.
- Is safe to re-run.

## A note on syntax differences

VyOS uses its own `set`/`commit` configuration syntax, not Cisco IOS commands. The hardening *concepts* in the companion manual (hashed credentials, SSH-only remote access, disabling weak transport, banners) all map onto VyOS, but the exact commands differ — this GNS3 build is for practicing the concepts and topology, not for memorizing IOS syntax, which you should do against Packet Tracer or a Cisco IOS image instead.

## After the build

Open the `Day-04-Basic-Device-Security` project in the GNS3 GUI, start the nodes, and follow the [Configuration Tasks](../Day-04-Lab-Manual.md#6-configuration-tasks) section of the manual, translating each IOS command to its VyOS equivalent.
