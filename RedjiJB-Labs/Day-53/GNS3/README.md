# GNS3 Lab — Day 53: GRE Tunnels

This folder contains an automation script that builds the Day 53 topology (PC1, SW1, R1, SPR1, SPR2, R2, SW2, PC2) in GNS3 using free/open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| R1, R2, SPR1, SPR2 | VyOS | Open-source, Cisco-like CLI. Supports GRE tunnel interfaces and OSPF (via FRRouting) natively. |
| SW1, SW2 | Open vSwitch | Built into GNS3, no download needed. |
| PC1, PC2 | Alpine Linux | Lightweight Linux end hosts. |

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
- Creates the `Day-53-GRE-Tunnels` project (or reuses it if it already exists).
- Creates all 8 nodes and the 7 **underlay** links matching the topology in [`../Day-53-Lab-Manual.md`](../Day-53-Lab-Manual.md).
- Is safe to re-run — it skips nodes/links that already exist.

## Important: the GRE tunnel itself is not a GNS3 link

This script only wires up the **physical/underlay** topology (PC↔SW↔R↔SPR↔SPR↔R↔SW↔PC). The GRE tunnel between R1 and R2 is a **logical overlay** — it does not correspond to a cable or a GNS3 link object at all. You create it entirely from inside R1's and R2's own configuration once the underlay is addressed and reachable, the same way the Lab Manual describes for IOS:

```text
# VyOS equivalent, R1 (adapt addressing per the Lab Manual's Section 4)
set interfaces tunnel tun0 address '192.168.1.1/30'
set interfaces tunnel tun0 encapsulation 'gre'
set interfaces tunnel tun0 source-address '100.0.0.2'
set interfaces tunnel tun0 remote '200.0.0.2'
commit
```

This is a good practical reinforcement of the Lab Manual's central point: the tunnel is not something you "build" in the topology diagram, it's something you configure on top of an already-working underlay.

## After the build

Open the `Day-53-GRE-Tunnels` project in the GNS3 GUI, start all nodes, and:

1. Address and verify the underlay first (R1↔SPR1, SPR1↔SPR2, SPR2↔R2) — confirm R1 can ping R2's provider-facing address before touching the tunnel.
2. Configure the GRE tunnel on R1 and R2 (VyOS `set interfaces tunnel tun0 ...` as shown above, or translate the IOS commands from the Lab Manual if you have an IOSv template imported instead).
3. Configure OSPF over the tunnel and the LANs (VyOS `set protocols ospf ...`).
4. Verify with `show interfaces tunnel0`, `show ip ospf neighbor` (or their VyOS/FRR equivalents: `show interfaces tunnel tun0`, `show ip ospf neighbor`), and a ping from PC1 to PC2.

See [`../Day-53-Lab-Manual.md`](../Day-53-Lab-Manual.md) for the full addressing plan and command walkthrough.
