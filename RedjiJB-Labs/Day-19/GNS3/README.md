# Day 19 GNS3 Lab — VTP, Trunking, and VLAN Management

## Running the build script

1. Start GNS3 with the local server reachable (default `http://localhost:3080`).
2. `pip install requests`
3. `python build_lab.py`

Builds a three-switch line topology (SW1–SW2–SW3) using Open vSwitch — no download needed, it's built into GNS3.

## Critical limitation: Open vSwitch does not support VTP

This entire lab is about VTP Server/Transparent/Client mode behavior, and **Open vSwitch has no VTP implementation whatsoever**. The build script above gives you correct cabling and Layer 2 connectivity for basic trunking practice, but you **cannot** complete Sections 6–9 of the lab manual (VTP domain/mode configuration, VLAN propagation testing) on Open vSwitch nodes.

**To actually do this lab in GNS3**, substitute a **Cisco IOSvL2** or **vIOS-L2** image for all three switches (SW1, SW2, SW3) if you have access to one — these support `vtp domain`, `vtp mode`, `vlan`, and `show vtp status` exactly as written in the manual. If you don't have access to an IOS-based Layer 2 image, complete this lab in **Packet Tracer**, which models VTP natively on its default switch images, and use this GNS3 build only for practicing the trunk/DTP hardening commands, which Open vSwitch's VLAN tagging does support at a basic level.

## Trunk hardening on Open vSwitch

Open vSwitch's GNS3 GUI lets you set a port's VLAN mode (access/trunk) and allowed VLAN tags directly in the node's port configuration dialog, but does not expose `switchport nonegotiate` or DTP behavior — there is no DTP negotiation to disable because Open vSwitch doesn't run DTP in the first place. Treat this as another point in favor of an IOSvL2 substitute if you want to practice the exact commands from the manual.
