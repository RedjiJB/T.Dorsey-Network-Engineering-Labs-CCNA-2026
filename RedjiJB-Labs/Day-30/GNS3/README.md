# GNS3 Lab — Day 30: HSRP Gateway Redundancy

Automated build script for the Day 30 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| R1, R2, R3 | VyOS | R1/R2 run VRRP — the open-standard equivalent to HSRP |
| SW1 | Open vSwitch | Built into GNS3, no download needed |
| PC1, PC2 | Alpine Linux | End hosts on the shared LAN |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. VyOS and Alpine Linux templates imported into GNS3 (the script will ask before attempting any download). Open vSwitch ships with GNS3.

## Running the build

```bash
python build_lab.py
```

The script checks the GNS3 server is reachable, checks all required templates exist (asking before downloading anything missing), then creates the project, nodes, and links — safe to re-run, it skips anything already created.

## Why VRRP instead of HSRP

HSRP is a Cisco-proprietary protocol — it only runs on Cisco IOS. VyOS (built on FRRouting) implements VRRP instead, the IETF open-standard equivalent. The underlying concept the lab manual teaches — a shared virtual IP, priority-based election, and preemption behavior — is identical; only the command syntax and a couple of naming/default differences change.

| HSRP (Cisco IOS) | VRRP (VyOS) |
|---|---|
| `standby <group> ip <vip>` | `set high-availability vrrp group <name> virtual-address <vip>` |
| `standby <group> priority <n>` | `set high-availability vrrp group <name> priority <n>` |
| `standby <group> preempt` | Preemption is VRRP's **default** behavior — opt out with `set high-availability vrrp group <name> no-preempt` |
| `show standby` | `show vrrp` |

## Applying the lab configuration after nodes are running

On R1 (intended master/active):
```
configure
set interfaces ethernet eth0 address 10.0.1.253/24
set high-availability vrrp group LAN-GW virtual-address 10.0.1.254
set high-availability vrrp group LAN-GW interface eth0
set high-availability vrrp group LAN-GW priority 120
commit
save
```

On R2 (intended backup/standby):
```
configure
set interfaces ethernet eth0 address 10.0.1.252/24
set high-availability vrrp group LAN-GW virtual-address 10.0.1.254
set high-availability vrrp group LAN-GW interface eth0
set high-availability vrrp group LAN-GW priority 50
commit
save
```

Verify with `show vrrp` on each router — it reports Master/Backup state, priority, and the virtual address, directly analogous to `show standby`'s Active/Standby output.

## Simulating failover

Shut down R1's LAN-facing interface (`set interfaces ethernet eth0 disable`, commit) and watch R2 transition to Master via `show vrrp`. Bring R1 back up and confirm it reclaims Master status (VRRP preempts by default, unlike HSRP which requires explicitly enabling it).

## Caveats

- VRRP's default virtual MAC format (`00:00:5E:00:01:<VRID>`) differs from HSRP's (`0000.0C9F.F<group>` for v2) — expect a different MAC in `arp -a`/`show arp` output than the manual's IOS example, but the *behavior* (a shared MAC that doesn't change across failover) is the same concept.
- VRRP preempts by default, the opposite default from HSRP — if you want to replicate the manual's "no preempt on the standby" behavior exactly, add `no-preempt` on R2's group configuration.
