# Day 30 Lab Manual — HSRP Gateway Redundancy: Failover, Preemption, and Virtual IPs

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure HSRPv2 between two routers sharing a virtual IP so LAN clients keep a single, unchanging default gateway even when the active router fails |
| CCNA 200-301 Domains | 3.0 IP Connectivity (First Hop Redundancy Protocols — HSRP concepts), 1.0 Network Fundamentals (default gateway concepts) |
| Prerequisites | Basic router interface configuration, OSPF or static routing already in place on the LAN edge, ARP fundamentals |
| Estimated Time | 60–75 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

Every host on a LAN has exactly one default gateway configured, and if that gateway's router goes down, every host loses its path off the local subnet — a single point of failure that's unacceptable in any network expected to stay up. HSRP (Hot Standby Router Protocol) solves this by letting two (or more) routers share a single virtual IP and virtual MAC address: hosts point their default gateway at the virtual IP, never a physical router IP, so control over which physical router is actually forwarding traffic can shift transparently without any host needing to notice, re-ARP, or reconfigure anything.

By the end of this lab you will be able to:

1. Configure HSRPv2 with a virtual IP shared between two routers.
2. Explain priority-based active/standby election and configure priority to control which router should normally be active.
3. Configure and explain preemption — the mechanism that lets a higher-priority router reclaim the active role after recovering from a failure.
4. Explain what the Active Virtual MAC is, why it's identical on both routers, and why that's what makes failover transparent to end hosts.
5. Trigger a real failover, observe the HSRP state machine transition, and verify which router picked up the virtual IP.
6. Interpret `show standby` output to determine group state, priority, and preemption status on any router.

## 2. Business Context

Any enterprise LAN with more than one edge/distribution router uses a first-hop redundancy protocol — HSRP is Cisco's proprietary version of this pattern (VRRP is the open standard equivalent). Without it, upgrading, rebooting, or losing the single router that hosts a LAN's default gateway takes the entire segment offline until that one router comes back. HSRP is the mechanism that lets IT perform planned maintenance on a router (patch, reboot, replace) during business hours with zero perceived downtime for end users, and it's also what keeps a LAN alive automatically during an unplanned router failure — this is one of the most common "why did the network survive that outage" answers in real enterprise environments.

## 3. Topology Reference

| Device | Role |
|---|---|
| R1 | Active HSRP router (priority 120, preemption enabled) |
| R2 | Standby HSRP router (priority 50, no preemption) |
| R3 | WAN/ISP edge router — not part of the HSRP group |
| SW1/SW2 | LAN access switches |
| SW3/SW4 | Distribution switches |
| PC1, PC2 | End hosts on the LAN, using the HSRP virtual IP as their default gateway |

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

The LAN segment is a single `/24`, sized generously for both current hosts and headroom for growth — standard practice for an access-layer subnet. Both WAN links off R3 are `/30`s, the minimum-waste sizing for a point-to-point connection. The HSRP virtual IP lives inside the LAN `/24` but is not tied to either physical router — it exists only as long as at least one HSRP group member is alive to answer for it.

### 4.2 Manual Calculation Walkthrough

```
10.0.1.0/24 (LAN segment)
Host bits = 32 - 24 = 8 → 2^8 = 256 total addresses
Usable hosts = 256 - 2 = 254
Network address:    10.0.1.0
First usable host:  10.0.1.1
Last usable host:    10.0.1.254
Broadcast address:   10.0.1.255
```
Within that range, this lab assigns R1's physical IP as `.253`, R2's physical IP as `.252`, and reserves `.254` as the HSRP virtual IP — a common convention of placing the VIP at the top of the usable range so it's visually distinct from individual host/router addresses at a glance.

```
203.0.113.0/30 (R3-R1 WAN link)
Host bits = 32 - 30 = 2 → 2^2 = 4 total addresses
Usable hosts = 4 - 2 = 2   ✓ exactly enough for a point-to-point link
Network address: 203.0.113.0, usable: .1-.2, broadcast: .3
```
The R3–R2 WAN link (`203.0.113.4/30`) uses identical math, just the next block over.

### 4.3 Address Table

| Device/Object | Address |
|---|---|
| R1 physical (G0/0) | 10.0.1.253/24 |
| R2 physical (G0/0) | 10.0.1.252/24 |
| HSRP Virtual IP (group 1) | 10.0.1.254/24 |
| PC1 | 10.0.1.1/24, gateway 10.0.1.254 |
| PC2 | 10.0.1.2/24, gateway 10.0.1.254 |
| R3–R1 WAN | 203.0.113.0/30 |
| R3–R2 WAN | 203.0.113.4/30 |

## 5. Pre-Configuration Checklist

- [ ] Confirm the physical IP addressing and any underlying routing protocol (OSPF/static) is already working before adding HSRP — HSRP redundancy is meaningless if the routers can't reach anywhere in the first place
- [ ] Decide which router should normally be active (this lab: R1) and plan its priority above the HSRP default of 100
- [ ] Decide the standby router's priority below default (this lab: R2, priority 50)
- [ ] Decide the HSRP version (this lab: v2 — required for larger group numbers and IPv6, and generally preferred over legacy v1 today)
- [ ] Plan preemption deliberately: enable it only on the router that should reliably reclaim active status after recovering

## 6. Configuration Tasks

### 6.1 Baseline: gateway before HSRP exists

Before configuring HSRP, PC1/PC2 point directly at R1's physical IP as their gateway:
```
PC1> ipconfig
Default Gateway: 10.0.1.253
```
This works while R1 is up, but is a single point of failure — if R1 goes down, PC1 has no path off the subnet until someone manually reconfigures its gateway or R1 recovers. This is exactly the problem HSRP exists to solve.

### 6.2 Configure HSRPv2 on R1 (intended active router)

```
R1(config)# interface g0/0
R1(config-if)# standby version 2
R1(config-if)# standby 1 ip 10.0.1.254
R1(config-if)# standby 1 priority 120
R1(config-if)# standby 1 preempt
```
Mode: interface configuration. `standby version 2` selects HSRPv2 (larger MAC address space, faster default timers, IPv6 support) over the legacy v1 default. `standby 1 ip 10.0.1.254` creates HSRP group 1 on this interface and assigns it the shared virtual IP — both routers must use the identical group number and VIP to participate in the same group. `standby 1 priority 120` raises this router above the HSRP default priority of 100, making it the preferred active router in the election. `standby 1 preempt` tells this router that if it ever comes up and sees a lower-priority router currently active, it should immediately take over rather than staying passively in standby. Memory aid: "priority decides who *should* be active; preempt decides whether a router is allowed to *act* on that."

### 6.3 Configure HSRPv2 on R2 (standby router)

```
R2(config)# interface g0/0
R2(config-if)# standby version 2
R2(config-if)# standby 1 ip 10.0.1.254
R2(config-if)# standby 1 priority 50
```
Same group number and identical virtual IP — required for R2 to join the same HSRP group as R1. Priority 50 is deliberately below the default of 100, guaranteeing R1 wins the election whenever both are healthy. **No `preempt` on R2** is intentional: if R2 ever becomes active (because R1 failed) and R1 later comes back, R2 should *not* immediately hand control back and forth — R1's own preemption is what pulls the active role back, keeping the failback behavior predictable and controlled from one side.

### 6.4 Point end hosts at the virtual IP

```
PC1> ipconfig
   change default gateway to 10.0.1.254
PC2> ipconfig
   change default gateway to 10.0.1.254
```
This is the step that actually makes HSRP useful — as long as PC1/PC2 point at a physical router IP, they're still exposed to that specific router's failure. Pointing at the virtual IP is what makes failover invisible to them.

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show standby` | R1, R2 | Confirm group state (Active/Standby), VIP, priority, preemption status |
| `show standby brief` | R1, R2 | Compact one-line-per-group summary |
| `ipconfig` | PC1, PC2 | Confirm default gateway is the VIP, not a physical router IP |
| `arp -a` | PC1, PC2 | Confirm the VIP resolves to the shared Active Virtual MAC |
| `ping 8.8.8.8` | PC1, PC2 | Confirm end-to-end reachability through whichever router is currently active |

### Expected Output Gallery

```
R1# show standby
GigabitEthernet0/0 - Group 1 (version 2)
  State is Active
  Virtual IP address is 10.0.1.254
  Active router is local
  Standby router is 10.0.1.252
  Priority 120 (configured 120)
  Preemption enabled
```

```
R2# show standby
GigabitEthernet0/0 - Group 1 (version 2)
  State is Standby
  Virtual IP address is 10.0.1.254
  Active router is 10.0.1.253
  Standby router is local
  Priority 50 (default 100)
```

```
PC1> arp -a
Internet Address    Physical Address    Type
10.0.1.253          00d0.585b.7501     dynamic
10.0.1.254          0000.0c9f.f001     dynamic
```
`0000.0c9f.f001` is the Active Virtual MAC for HSRPv2 group 1 (`0000.0C9F.F` + group number in hex, `001` for group 1). Both R1 and R2 are configured to answer to this same MAC when active — that's the mechanism that lets the PC's ARP entry stay valid across a failover.

**During failover (R1 shut down):**
```
%HSRP-6-STATECHANGE: GigabitEthernet0/0 Grp 1 state Standby -> Active
```
```
PC1> arp -a
10.0.1.254 → 0000.0c9f.f001   (unchanged — same virtual MAC, now hosted on R2)
```
```
PC1> ping 8.8.8.8
Packets: Sent = 4, Received = 3, Lost = 1 (25% loss)
```
One packet lost during the brief state transition, then full recovery — this is the expected, realistic behavior of a working failover, not a failure.

**After R1 returns (preemption reclaims active):**
```
%HSRP-6-STATECHANGE: GigabitEthernet0/0 Grp 1 state Speak -> Standby
%HSRP-6-STATECHANGE: GigabitEthernet0/0 Grp 1 state Standby -> Active
```

## 8. Common Mistakes (80/20)

1. **Mismatched group numbers or virtual IPs between the two routers** — they simply won't form a group; each thinks it's alone and both become Active, which is a silent, dangerous failure (duplicate IP behavior on the LAN).
2. **Forgetting `preempt` on the router that should reliably reclaim active status** — without it, R1 stays in Standby indefinitely after recovering, even though its priority is higher, defeating the purpose of setting a high priority in the first place.
3. **Enabling preemption on both routers** — can cause unnecessary back-and-forth active/standby flapping if priorities or link states are unstable; preemption is usually intentional on exactly one side.
4. **Pointing end hosts at a physical router IP instead of the VIP** — HSRP is configured correctly but provides zero actual redundancy because the hosts never benefit from it.
5. **Assuming failover is instant with zero packet loss** — HSRP's hello/hold timers mean there's a brief real transition window (a small number of dropped packets is normal and expected, not a misconfiguration).

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Do both routers agree on group number and VIP? | `show standby` on each | Correct mismatched `standby <group> ip` |
| 2 | Is exactly one router Active and the other Standby? | `show standby` on each | If both show Active, check for a VIP/group mismatch or a network partition between them |
| 3 | Is the intended router the higher priority one? | `show standby` — check Priority field | Correct `standby <group> priority` |
| 4 | Does the intended router reclaim active status after recovering? | Shut/no-shut test, watch `%HSRP-6-STATECHANGE` logs | Confirm `standby <group> preempt` is present on that router |
| 5 | Do end hosts actually point at the VIP? | `ipconfig` on PC1/PC2 | Correct the configured default gateway |
| 6 | Does the VIP resolve to the expected virtual MAC? | `arp -a` on a PC | Confirm HSRP version and group number are correct (affects the MAC's last bytes) |

## 10. Design Analysis

The alternative to HSRP — a single router as the LAN's only gateway — is simpler to configure but makes that router's failure (or even a planned reboot) a full outage for the whole segment. HSRP trades a small amount of configuration complexity and a brief failover window (seconds, governed by hello/hold timers) for eliminating that single point of failure entirely. The priority + preempt design specifically lets an operator declare *intent* — "R1 should normally be active" — while still guaranteeing automatic failover if that intent can't be honored, which is a deliberate middle ground between full automatic election (no operator control over which router is preferred) and a purely manual failover process (too slow for production).

## 11. Real-World Parallel

Any enterprise or campus network with redundant edge/distribution routers uses a first-hop redundancy protocol at the LAN gateway — HSRP if the environment is Cisco-only, VRRP if it needs to be vendor-neutral, GLBP if load-sharing across both routers (not just failover) is also wanted. This is a foundational, near-universal pattern anywhere uptime matters, and it's frequently the first thing verified during a "why didn't the outage take down the LAN" postmortem.

## 12. Stretch Goal

Add a third router to the same HSRP group as a second standby, and observe how HSRP elects Active vs. Standby vs. simply "Listen" state among three candidates. Then explore HSRP interface tracking (`standby 1 track <interface> decrement <value>`) so that R1's priority automatically drops if its WAN-facing interface toward R3 fails — forcing a failover to R2 even though R1's LAN-facing interface is still healthy, because a router that can't reach the WAN shouldn't stay the active gateway.

## 13. Self-Assessment

- [ ] I can explain why pointing end hosts at the VIP (not a physical router IP) is the step that actually delivers redundancy
- [ ] I can explain what the Active Virtual MAC is and why it stays the same across a failover
- [ ] I configured priority and preemption myself, and can explain the difference between what each one controls
- [ ] I triggered a real failover (shutting down the active router) and observed the state-change log messages
- [ ] I verified R1 reclaimed the active role after recovering, and can explain precisely why (priority + preempt together)
- [ ] I can read `show standby` output and identify state, VIP, priority, and preemption status at a glance

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** HSRPv2, virtual IP (VIP), Active Virtual MAC, priority-based election, preemption, HSRP state machine (Initial → Learn → Listen → Speak → Standby → Active), hello/hold timers.

**What I Learned:** HSRP's transparency to end hosts comes specifically from the shared virtual MAC, not just the shared virtual IP — a PC's ARP entry for its gateway doesn't need to change during failover because the MAC it already has cached is answered by whichever router is currently active. Priority and preemption are two separate levers: priority decides who *should* be active, preemption decides whether a router is *allowed* to act on that once it's back online — configuring only one without the other produces working-but-incomplete redundancy.

**Skills Practiced:** HSRPv2 group configuration, priority and preemption tuning, end-host default gateway configuration pointed at a VIP, triggering and observing a live failover, reading HSRP state-change log messages and `show standby` output.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-30/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers (VRRP as the open-standard equivalent to HSRP, since VyOS doesn't support Cisco's proprietary HSRP), Open vSwitch switches, and Alpine Linux end hosts — see the README for a full HSRP-to-VRRP concept mapping.
