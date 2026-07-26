# Day 29 — HSRP Gateway Redundancy: Failover, Preemption, and Virtual IPs

## Overview

Today's lab was **HSRP (Hot Standby Router Protocol)** — Cisco's proprietary first-hop redundancy protocol. The goal: give the network two routers sharing one virtual IP so that if the active router dies, the standby takes over instantly. PCs never know the difference.

This is the protocol behind "failover" in enterprise networks. Without it, a single router failure brings down the entire LAN's Internet access.

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration.png">
  </a>
</p>

---

## Lab Scenario

> The network is pre-configured with IP addressing and OSPF. You are configuring HSRP for first-hop redundancy on the LAN edge.

---

## Topology Summary

| Device | Type | Role |
|--------|------|------|
| R1 | 2911 | Active HSRP router, priority 120 |
| R2 | 2911 | Standby HSRP router, priority 50 |
| R3 | 2911 | WAN/ISP edge, not in HSRP group |
| SW1/SW2 | 2960-24TT | LAN switches |
| SW3/SW4 | 2960-24TT | Distribution switches |
| PC1 | PC-PT | 10.0.1.1/24 |
| PC2 | PC-PT | 10.0.1.2/24 |

Subnets:
- `10.0.1.0/24` — LAN segment (PC1, PC2, R1, R2, switches)
- `203.0.113.0/30` — R3–R1 WAN link
- `203.0.113.4/30` — R3–R2 WAN link

---

## Lab Questions and Solutions

**1. Ping 8.8.8.8 from PC1/PC2. What is the default gateway configured as?**

Before HSRP is configured, the PCs have a physical router IP as their gateway.

```cisco
PC1>ipconfig
```
```
Default Gateway: 10.0.1.253  (R1's physical IP)
```

```cisco
PC1>ping 8.8.8.8
```
```
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
Minimum = 0ms, Maximum = 1ms, Average = 0ms
```

Connectivity works because R1 is up and routing. But if R1 dies, PC1's traffic has nowhere to go.

---

**2. Configure HSRPv2 on R1 and R2. Raise R1's priority above default, lower R2's priority below default. Enable preemption.**

**R1 Configuration (Active router):**
```cisco
interface g0/0
 standby 1 ip 10.0.1.254
 standby 1 priority 120
 standby 1 preempt
```

**R2 Configuration (Standby router):**
```cisco
interface g0/0
 standby 1 ip 10.0.1.254
 standby 1 priority 50
```

**No preemption on R2.** R2 becomes standby but won't try to take over if a higher-priority router comes back.

**Verification on R1:**
```cisco
R1#show standby
```
```
GigabitEthernet0/0 - Group 1 (version 2)
  State is Active
  Virtual IP address is 10.0.1.254
  Active router is local
  Standby router is 10.0.1.252
  Priority 120 (configured 120)
  Preemption enabled
```

**Verification on R2:**
```cisco
R2#show standby
```
```
GigabitEthernet0/0 - Group 1 (version 2)
  State is Standby
  Virtual IP address is 10.0.1.254
  Active router is 10.0.1.253
  Standby router is local
  Priority 50 (default 100)
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-1.1.png">
     <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-1.2.png">
  </a>
</p>

---

**3. Configure the VIP (10.0.1.254) as the default gateway on PC1 and PC2. Ping 8.8.8.8 again. Check the ARP table. What MAC is mapped to the VIP?**

**PC Configuration:**
```cisco
PC1>ipconfig
```
Change default gateway from `10.0.1.253` to `10.0.1.254`.

```cisco
PC2>ipconfig
```
Change default gateway from `10.0.1.253` to `10.0.1.254`.

**Ping Verify:**
```cisco
PC1>ping 8.8.8.8
```
```
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
Average = 17ms
```

```cisco
PC1>arp -a
```
```
Internet Address    Physical Address    Type
10.0.1.253          00d0.585b.7501     dynamic
10.0.1.254          0000.0c9f.f001     dynamic
```

**The VIP MAC address is `0000.0c9f.f001`.**

This is the **Active Virtual MAC address** — HSRP v2 uses `0000.0C9F.F001` + group number in the last byte. It's the same on both routers because they share the same virtual MAC.

**Why this matters:** When a PC ARPs for the default gateway, it gets the active router's MAC. If the active router fails, the standby assumes the virtual MAC and IP. The PCs never have to update their ARP tables (within the hold time).

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-2.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-2.2.png">
        <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-3.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-3.2.png">
  </a>
</p>

---

**4. Turn off R1 (save the config first). After it restarts, ping from PC1 to 8.8.8.8 again. Is R2 used as the default gateway?**

**Step 1 — Save R1 config:**
```cisco
R1#write memory
Building configuration...
[OK]
```

**Step 2 — Shut down R1:**
```cisco
R1(config)#interface g0/0
R1(config-if)#shutdown
```

**HSRP state change (observed on R2):**
```
%HSRP-6-STATECHANGE: GigabitEthernet0/0 Grp 1 state Standby -> Active
```

**PC1 ARP after failover:**
```cisco
PC1>arp -a
```
```
10.0.1.254 → 0000.0c9f.f001 (still the same virtual MAC)
```

**PC1 ping during failover:**
```cisco
PC1>ping 8.8.8.8
```
```
Packets: Sent = 4, Received = 3, Lost = 1 (25% loss)
```
One packet loss during state transition, then full recovery.

**Yes, R2 becomes the active router.** Its G0/0 transitions from Standby → Active. The VIP 10.0.1.254 is now physically hosted on R2. The MAC address didn't change.

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-4.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration-5.1.png">
  </a>
</p>

---

**5. Turn R1 back on. Does it become the active router again?**

**R1 comes back online:**
```cisco
R1(config)#interface g0/0
R1(config-if)#no shutdown
```

**HSRP state transitions (observed on R1):**
```
%HSRP-6-STATECHANGE: GigabitEthernet0/0 Grp 1 state Speak -> Standby
%HSRP-6-STATECHANGE: GigabitEthernet0/0 Grp 1 state Standby -> Active
```

**Yes, R1 becomes active again.** Because:
1. R1's priority is **120** (higher than R2's 50)
2. Preemption is **enabled** on R1
3. When R1 detects R2 is in Standby state, it immediately reclaims the active role

**Verification:**
```cisco
R1#show standby
```
```
State is Active
Priority 120
Preemption enabled
Standby router is 10.0.1.252 (R2)
```

```cisco
R2#show standby
```
```
State is Standby
Priority 50
Active router is 10.0.1.253 (R1)
```

---

## HSRP Protocol Details

| Feature | Value | Notes |
|---------|-------|-------|
| Version | HSRPv2 | Supports IPv6, faster convergence |
| Group | 1 | 0-255 for v2 (0-255 for v1) |
| VIP | 10.0.1.254 | Shared virtual IP |
| Active Router | R1 (10.0.1.253) | Priority 120 |
| Standby Router | R2 (10.0.1.252) | Priority 50 |
| Active Virtual MAC | 0000.0C9F.F001 | Shared on both routers |
| Hello Time | 3 seconds | v2 default |
| Hold Time | 10 seconds | v2 default (3x hello) |
| Preemption | Enabled on R1 | Higher-priority router reclaims active role |

**HSRP State Machine:**
```
Initial → Learn → Listen → Speak → Standby → Active
```

- **Listen:** Router learns the hello from the current active router
- **Speak:** Router participates in election but hasn't qualified as standby
- **Standby:** Router is ready to take over if active dies
- **Active:** Router is forwarding traffic with the VIP

**VIP MAC Address:**
- HSRP v1: `0000.0C07.ACXX` (XX = group number in hex)
- HSRP v2: `0000.0C9F.FXXX` (XXX = group number in hex)

Both routers in the same group use the same virtual MAC. PCs ARP for the VIP and get the virtual MAC, not the physical MAC of either router.

---

## Commands Practiced

```cisco
! HSRP configuration
interface g0/0
 standby <group> ip <virtual-ip>
 standby <group> priority <0-255>
 standby <group> preempt

! Verification
show standby [brief]
show standby [interface]
show standby neighbors

! From PC
ipconfig
ping <gateway>
arp -a
```

---

## What I Learned

**HSRP is transparent to end devices.** The PC's default gateway is the VIP (10.0.1.254), not a physical router IP. When the active router fails, the standby assumes the VIP and the same MAC. The PC's ARP table doesn't expire or change.

The screenshots proved this: after R1 went down and R2 took over, PC1's ARP table still showed `10.0.1.254 → 0000.0c9f.f001`. The MAC address is the same because both routers share the active virtual MAC.

**Preemption is the "take back" mechanism.** When R1 came back online, it immediately transitioned Speak → Standby → Active because its priority (120) exceeded R2's (50) and preemption was enabled. Without preemption, R1 would have stayed in Standby until R2 failed.

**Priority range is 0-255.** Default is 100. The active router must have the highest priority. In a tie, the router with the highest IP wins the election.

**HSRP v2 vs v1:** The screenshots confirmed v2 (`version 2`). v2 is required for IPv6 support, larger group numbers (0-255 vs 0-255 in v1 actually, but v2 uses a different MAC format), and faster hello timers.

**The `show standby` command is your best friend.** It shows state, active IP, standby IP, priority, preemption status, and active virtual MAC in one output. On R2, it shows `State is Standby`, `Active router is 10.0.1.253`, `Standby router is local`. On R1, it shows `State is Active`, `Active router is local`.

---

## Lab Status

✅ Day 29 Complete

### Topics Covered

* HSRPv2 gateway redundancy concepts
* Virtual IP (VIP) and active virtual MAC
* Priority-based active/standby election
* Preemption configuration and behavior
* PC gateway configuration and ARP behavior
* Active router failover and state transitions
* Automatic recovery when the higher-priority router returns
* HSRP state machine: Initial → Learn → Listen → Speak → Standby → Active
* Command reference: `show standby`, `arp -a`, `ipconfig`

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
