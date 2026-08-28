# Day 18 GNS3 Lab — Multilayer Switching: SVIs and Inter-VLAN Routing

## Running the build script

1. Start GNS3 with the local server reachable (default `http://localhost:3080`).
2. `pip install requests`
3. `python build_lab.py`

Checks server and templates first, and only offers to download a missing image after asking.

## Important limitation: Open vSwitch as SW2 (the multilayer switch)

This lab's entire point is a Layer 3 switch with **SVIs** and a **routed port** (`no switchport`) — GNS3's built-in Open vSwitch node is a Layer 2 learning switch and does **not** support Cisco-style SVIs, `no switchport`, or a routing table of its own. It is used here as a topology stand-in (to verify Layer 2 connectivity and trunking) but **cannot** actually demonstrate this lab's core Layer 3 switching behavior.

To properly complete this lab in GNS3, substitute a **Cisco IOSvL2** or **vIOS-L2** image for SW2 if you have access to one — those support `interface vlan <id>`, `no switchport`, and `ip routing` exactly as described in the manual. If you don't have access to an L3-capable image, complete this lab's actual configuration and verification in Packet Tracer (which models the 3650-24PS natively) and use this GNS3 build only for basic topology/cabling practice.

## VyOS (R1) notes

```text
configure
set interfaces ethernet eth0 address 10.0.0.194/30
commit
save
```

R1's configuration in this lab is deliberately simple — a single routed interface, no VLAN awareness at all, since VLAN routing now lives entirely on SW2.
