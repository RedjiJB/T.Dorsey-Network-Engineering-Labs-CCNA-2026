# GNS3 Lab — Day 21: Configuring Spanning Tree

Automated build script for the Day 21 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Switches (SW1, SW2, SW3, SW4) | Open vSwitch | Built into GNS3, no download needed — see caveat below |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. No template imports needed — Open vSwitch ships with GNS3.

## Running the build

```bash
python build_lab.py
```

The script:
- Checks the GNS3 server is reachable.
- Checks the Open vSwitch template exists (it always should — built in).
- Creates the `Day-21-Configuring-Spanning-Tree` project (or reuses it if it already exists).
- Creates all 4 switch nodes and the 6 redundant links (a full mesh) that give STP something to block.
- Is safe to re-run — it skips nodes/links that already exist.

## Important caveat: Open vSwitch is not a substitute for IOS STP

This is the one lab in the series where the GNS3 build is closer to a **wiring diagram** than a functional lab. Open vSwitch runs a Linux bridge with basic STP/RSTP support, but it does **not** expose IOS-style per-VLAN spanning-tree controls. Specifically, you cannot:

- Set root bridge priority per VLAN (`spanning-tree vlan X priority Y`)
- Tune per-port cost or port-priority the way IOS does
- Configure PortFast or BPDU Guard as IOS commands
- Verify with `show spanning-tree` output matching what's in the Lab Manual

**Use this build to see the physical topology and redundant links come together**, and to understand *why* STP is needed (four switches, six links, multiple loops). For the actual configuration walkthrough — root bridge election, cost/priority tuning, PortFast, BPDU Guard, and the `show spanning-tree` verification gallery — follow the CLI steps in the [Day-21 Lab Manual](../Day-21-Lab-Manual.md) against real IOS devices (physical switches, IOS on UNL/EVE-NG, or Packet Tracer), not this GNS3 build.

## After the build

Open the `Day-21-Configuring-Spanning-Tree` project in the GNS3 GUI to see the four switches and six links laid out. Then work through the [Day-21 Lab Manual](../Day-21-Lab-Manual.md) on IOS-capable devices for the actual spanning-tree configuration and verification.
