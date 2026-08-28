# Day 20 GNS3 Lab — Analyzing STP: Port Roles Across Four Switches

## Running the build script

1. Start GNS3 with the local server reachable (default `http://localhost:3080`).
2. `pip install requests`
3. `python build_lab.py`

Builds a redundant four-switch mesh (SW3 linked to all three others, which are also cross-linked to each other) using Open vSwitch — no download needed.

## Limitation: Open vSwitch's STP support

GNS3's Open vSwitch node runs a basic STP/RSTP implementation sufficient to prevent loops, but its `show`-equivalent output (accessed via its own CLI, not IOS syntax) does **not** match Cisco's `show spanning-tree detail` format used throughout this lab's manual, and its bridge priority defaults and path-cost values may not line up with the specific numbers (24577, 32769, path cost 19/4, etc.) used in the manual's worked example.

**Recommended:** for accurate `show spanning-tree detail` output that matches this lab's exact analysis, substitute a **Cisco IOSvL2** or **vIOS-L2** image for all four switches if you have access to one. Use this Open vSwitch build for practicing the physical topology and observing *that* STP prevents a loop (some links block, traffic still flows), even if the exact CLI syntax and bridge ID values differ from the manual's worked numbers.

## Setting bridge priority to reproduce the manual's exact scenario (IOSvL2/vIOS-L2 only)

```text
SW3(config)#spanning-tree vlan 1 priority 24576
```

Cisco IOS only accepts priority values in multiples of 4096 — `24577` in the manual's `show` output is `24576` (the multiple-of-4096 priority you configure) plus `1` (the VLAN ID, automatically appended as the low-order bits of the Bridge ID's extended system ID). This is worth knowing: **you never type "24577" directly** — you configure `24576` and IOS displays the VLAN-adjusted value.
