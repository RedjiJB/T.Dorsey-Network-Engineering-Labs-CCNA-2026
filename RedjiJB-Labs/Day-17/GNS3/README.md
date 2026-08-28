# Day 17 GNS3 Lab — VLANs Part 2: Trunking & Router-on-a-Stick

## Running the build script

1. Start GNS3 with the local server reachable (default `http://localhost:3080`).
2. `pip install requests`
3. `python build_lab.py`

Checks server and templates before doing anything, and only offers to download a missing image after asking. Open vSwitch is built-in — no download needed for SW1/SW2.

## Topology built

Three Alpine Linux PCs on SW2 (Open vSwitch), one Alpine Linux PC directly on SW1, SW2↔SW1 trunked, and SW1↔R1 (VyOS) trunked for router-on-a-stick.

## Trunking and native VLAN caveats with Open vSwitch

GNS3's Open vSwitch node supports 802.1Q tagging via its port VLAN configuration in the GNS3 GUI, but it does **not** expose Cisco's `switchport mode trunk` / `switchport trunk allowed vlan` / `switchport trunk native vlan` CLI syntax, and it has no CDP implementation — so **this lab's native VLAN mismatch scenario cannot be reproduced or observed on Open vSwitch**. To actually practice the CDP mismatch detection and IOS trunk CLI from the manual, substitute a **Cisco IOSvL2** or **vIOS-L2** image for SW1 and SW2 if you have access to one; note this explicitly if you're using Open vSwitch as a stand-in — treat it as good enough for basic VLAN tagging and connectivity verification, not for CDP/trunk-CLI practice.

## VyOS router-on-a-stick notes

```text
configure
set interfaces ethernet eth0 vif 10 address 10.0.0.62/26
set interfaces ethernet eth0 vif 20 address 10.0.0.126/26
set interfaces ethernet eth0 vif 30 address 10.0.0.190/26
commit
save
```

VyOS's `vif <id>` under a physical interface is the direct equivalent of an IOS `encapsulation dot1Q <id>` subinterface — no separate "encapsulation" command is needed since `vif` implies 802.1Q tagging.
