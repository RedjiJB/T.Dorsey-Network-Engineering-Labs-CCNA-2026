# Day 16 GNS3 Lab — VLANs Part 1

## Running the build script

1. Start GNS3 with the local server reachable (default `http://localhost:3080`).
2. `pip install requests`
3. `python build_lab.py`

Checks the server and templates first, and only offers to download a missing image after asking. Open vSwitch is built into GNS3 — no download needed for SW1.

## Topology built

Six Alpine Linux PCs on Open vSwitch (SW1), with **three separate physical links** from SW1 to a VyOS router (R1) — one per VLAN, matching the "no trunking yet" design of this lab.

| Packet Tracer device | GNS3 image |
|---|---|
| Router (R1) | VyOS |
| Switch (SW1) | Open vSwitch |
| PCs (PC1-PC6) | Alpine Linux |

## Open vSwitch VLAN notes

Open vSwitch's default GNS3 template acts as a simple learning switch without a CLI-driven VLAN database the way Cisco IOS has one. To replicate `switchport access vlan <id>` behavior:

- Use GNS3's built-in **VLAN filtering** on the Open vSwitch node's port configuration (right-click the node → configure), assigning each port an access VLAN ID directly in the GNS3 GUI rather than via IOS-style CLI commands.
- If you need full `vlan database` / `switchport` CLI semantics (e.g., to practice the exact commands from the manual), substitute a **Cisco IOSvL2** or **vIOS-L2** image if you have access to one — Open vSwitch is a functional stand-in for connectivity testing but won't teach you the IOS VLAN CLI syntax itself.

## VyOS routing notes

Each of R1's three interfaces is a plain Layer 3 interface with a static IP — no VLAN-awareness needed on the router side in this lab:

```text
configure
set interfaces ethernet eth0 address 10.0.0.62/26
set interfaces ethernet eth1 address 10.0.0.126/26
set interfaces ethernet eth2 address 10.0.0.190/26
commit
save
```

Alpine Linux PCs: `ip addr add <ip>/26 dev eth0` and `ip route add default via <gateway>`.
