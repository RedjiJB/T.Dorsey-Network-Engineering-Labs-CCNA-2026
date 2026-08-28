# GNS3 Lab — Day 52: STP & HSRP Synchronization

Automated build script for the Day 52 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Distribution switches (DSW1, DSW2) | VyOS | Routed SVIs + VRRP |
| Access switch (ASW1) | Open vSwitch | Built into GNS3, no download needed |
| End hosts | Alpine Linux | VLAN 10 / VLAN 20 test hosts |

## Prerequisites

1. GNS3 installed and running, local server reachable at `http://localhost:3080`.
2. Python 3.8+ with `requests`: `pip install requests`
3. Template imported for VyOS. Open vSwitch and Alpine are otherwise covered.

## Running the build

```bash
python build_lab.py
```

Checks the server, checks templates, creates the `Day-52-STP-HSRP-Sync` project, creates 5 nodes and 5 links. Safe to re-run.

## HSRP vs. VRRP — concept mapping

VyOS does not support Cisco's proprietary HSRP. It uses the open standard **VRRP**, which serves the identical purpose (shared virtual gateway IP, active/backup election, preemption) with slightly different terminology:

| Cisco HSRP | VRRP (VyOS) | Concept |
|---|---|---|
| `standby <group> ip <vip>` | `set ... vrrp group <group> virtual-address <vip>` | Virtual gateway IP |
| `standby <group> priority <n>` (default 100, higher wins) | `set ... vrrp group <group> priority <n>` (default 100, higher wins) | Election priority — same direction as HSRP |
| `standby <group> preempt` | `set ... vrrp group <group> preempt true` (VRRP preempts by default) | Reclaim active/master role |
| Active / Standby | Master / Backup | Role naming |

VyOS's `spanning-tree vlan <id> root primary/secondary` equivalent uses `set protocols stp <bridge> ...` with a manually set bridge priority (VyOS does not have a one-command automatic-root macro like IOS) — you must calculate and set the lowest priority explicitly on the intended root switch. Use this table alongside the lab manual's IOS walkthrough to translate the commands onto the VyOS distribution switches in this build.
