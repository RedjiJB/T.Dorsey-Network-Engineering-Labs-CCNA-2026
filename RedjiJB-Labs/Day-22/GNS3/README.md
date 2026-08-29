# Day 22 GNS3 Lab — RSTP: Root Bridge Behavior and Link Types

Builds an approximation of the 4-switch, 2-hub RSTP topology from the Day 22 Lab Manual using free/open-source GNS3 images.

## Image mapping

| Packet Tracer device | GNS3 image | Notes |
|---|---|---|
| Cisco 2960 (SW1-SW4) | Open vSwitch | Built into GNS3 |
| Hub-PT (Hub0, Hub1) | Open vSwitch (unmanaged approximation) | No true "hub" image exists in GNS3 — see limitation below |
| Generic PC | Alpine Linux | |

## Important limitation: Open vSwitch and RSTP

**Open vSwitch does not provide the same native RSTP behavior as Cisco IOS.** OVS bridges are commonly deployed with STP disabled entirely (the assumption in cloud/virtualization environments is a loop-free fabric managed elsewhere), and where OVS does support STP/RSTP, its port-role terminology and Backup-port handling on shared segments does not map 1:1 to the Cisco IOS behavior this lab is built to teach.

**Practical consequence:** you can build the topology's physical shape in GNS3 with this script, but you should not expect `ovs-vsctl` or OVS's STP output to reproduce the specific Backup-port-on-the-root-bridge scenario from Lab Manual Section 6.2. Use this GNS3 build for practicing cabling/topology layout, not for the RSTP port-role verification itself.

**Recommended alternative:** if you have access to Cisco IOU/IOL images (through a personal Cisco account/CCIE lab license, not redistributable here), substitute those for the `Open vSwitch` template in this script — IOU/IOL runs real Cisco IOS and will reproduce the Lab Manual's `show spanning-tree` output exactly. The Packet Tracer version of this lab remains the primary reference for RSTP-specific verification.

## Usage

```bash
pip install requests
python build_lab.py
```

Safe to re-run — skips nodes/links that already exist.
