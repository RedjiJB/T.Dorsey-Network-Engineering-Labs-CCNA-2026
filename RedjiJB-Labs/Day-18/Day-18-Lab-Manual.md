# Day 18 Lab Manual — Multilayer Switching: SVIs and Inter-VLAN Routing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Replace router-on-a-stick with a Layer 3 switch performing inter-VLAN routing via SVIs, connected to the internet edge router over a routed point-to-point link. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): SVIs, Layer 3 switching. Domain 4 (IP Connectivity): default routing on a multilayer switch. |
| **Prerequisites** | Day 17 (trunking, router-on-a-stick) — this lab explicitly replaces that design. |
| **Time Estimate** | 1.5 – 2 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — conceptually straightforward, but `no switchport` on a multilayer switch interface is a genuinely new command students haven't seen before this lab. |

---

## 1. Lab Overview

Day 17 solved VLAN scaling with router-on-a-stick — one router interface, subinterfaces per VLAN, all traffic funneling through a single physical link and the router's CPU. This lab replaces that bottleneck with a **multilayer switch** (SW2, a 3650-24PS): VLAN routing now happens in switch hardware via **SVIs (Switched Virtual Interfaces)**, and the connection to the internet-edge router (R1) becomes a **routed point-to-point Layer 3 link** instead of a trunk.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain why multilayer switching removes the ROAS single-link bottleneck
- Convert a switch port from Layer 2 to Layer 3 with `no switchport`
- Configure SVIs (`interface vlan <id>`) to provide inter-VLAN routing at wire speed
- Configure a default route on a multilayer switch toward the internet edge router
- Verify inter-VLAN and internet connectivity end-to-end

---

## 2. Business Context

**Why would a real company do this?**

Router-on-a-stick works, but every byte of inter-VLAN traffic has to leave the switch, cross one physical link, get processed by the router's CPU, and come back — a real throughput ceiling the moment traffic volume grows past what a single router port and a general-purpose CPU can handle. A multilayer (Layer 3) switch does the routing decision in ASIC hardware, right where the traffic already is, without ever needing to leave the switch chassis for VLAN-to-VLAN traffic. This is exactly the architecture every enterprise campus network uses once it outgrows a small branch office: a Layer 3 distribution/core switch handles inter-VLAN routing at line rate, and the router is reserved for what only a router needs to do — talking to the actual internet edge.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-18-Lab-Multilayer%20Switching.pkt.png" alt="Day 18 Topology" width="800">
</p>

| Device | Model | Role |
|---|---|---|
| R1 | 2911 | Internet edge router |
| SW1 | 2960-24TT | Access switch |
| SW2 | 3650-24PS | Multilayer switch (replaces R1's ROAS role from Day 17) |
| PC1–PC7 | PC-PT | End hosts in VLAN10/20/30 |

```text
PC1-PC7 (VLAN10/20/30) -- SW1 ===trunk=== SW2 (SVIs) ===routed P2P=== R1 -- Internet
```

---

## 4. IP Addressing Plan

VLAN subnets are unchanged from Day 16/17 (`/26` blocks of `10.0.0.0/24`, gateway = last usable address) — again proving that Layer 2 topology changes (ROAS → multilayer switching) don't require re-deriving the VLAN addressing plan. The only **new** address needed is the routed P2P link between SW2 and R1.

### 4.1 Deriving the New P2P Subnet

The three VLAN `/26`s consumed `10.0.0.0/26`, `10.0.0.64/26`, and `10.0.0.128/26`, leaving `10.0.0.192/26` unused. A P2P link needs only 2 usable hosts:

```text
2^h − 2 ≥ 2  →  h = 2  →  /30
Mask: 11111111.11111111.11111111.111111 00 = 255.255.255.252
Block size = 256 − 252 = 4
```

The new `/30` is carved from the unused `10.0.0.192/26` remainder, at the first available `/30`-aligned boundary: `10.0.0.192/30`.

```text
Network address:    10.0.0.192   (all 2 host bits = 0)
First usable host:  10.0.0.193   (SW2 side)
Last usable host:   10.0.0.194   (R1 side)
Broadcast address:  10.0.0.195   (all 2 host bits = 1)
```

### 4.2 Full Device Address Table

| Device | Interface | IP Address | Mask | Role |
|---|---|---|---|---|
| SW2 | Gi1/0/2 | 10.0.0.193 | 255.255.255.252 | Routed link to R1 |
| R1  | Gi0/0   | 10.0.0.194 | 255.255.255.252 | Routed link to SW2 |
| SW2 | VLAN10 (SVI) | 10.0.0.62 | 255.255.255.192 | VLAN10 gateway |
| SW2 | VLAN20 (SVI) | 10.0.0.126 | 255.255.255.192 | VLAN20 gateway |
| SW2 | VLAN30 (SVI) | 10.0.0.190 | 255.255.255.192 | VLAN30 gateway |

---

## 5. Pre-Configuration Checklist

1. Place R1, SW1, SW2, and PC1–PC7 per the topology.
2. Cable SW1↔SW2 as a trunk (VLANs still terminate on SW2's SVIs, so SW1 needs a trunk to carry them all).
3. Cable SW2↔R1 directly — this becomes a routed link, not a trunk.
4. Remove any leftover ROAS subinterface configuration from R1 if continuing directly from Day 17's lab file.

---

## 6. Configuration Tasks

### 6.1 Replace ROAS with a Routed Point-to-Point Link

**R1 side — remove subinterfaces, configure the physical interface directly:**

```text
R1(config)#no interface gigabitEthernet 0/0.10
R1(config)#no interface gigabitEthernet 0/0.20
R1(config)#no interface gigabitEthernet 0/0.30
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ip address 10.0.0.194 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
```

> With ROAS gone, R1's Gi0/0 is now a plain routed interface with one IP — no `encapsulation dot1Q`, because there's no VLAN tagging on this link at all. R1 no longer needs to know VLANs exist; that's now SW2's job.

**SW2 side — convert the port to Layer 3:**

```text
SW2(config)#interface gigabitEthernet 1/0/2
SW2(config-if)#no switchport
SW2(config-if)#ip address 10.0.0.193 255.255.255.252
SW2(config-if)#no shutdown
SW2(config-if)#exit
```

> **`no switchport` is the single most important new command in this lab.** By default, every interface on a Layer 2-capable switch operates as a switchport (participates in VLAN forwarding, no IP of its own). `no switchport` converts it into a routed port — behaving exactly like a router interface, capable of holding an IP address and participating in the routing table. Without `ip routing` enabled globally (on by default on most L3 switch platforms in Packet Tracer, but verify with `show ip route` — if it's empty even after this config, run `ip routing` in global config) SW2 won't actually forward between this routed port and its SVIs.

**Default route on SW2, toward R1:**

```text
SW2(config)#ip route 0.0.0.0 0.0.0.0 10.0.0.194
```

**Verify:**

```text
SW2#show ip route
```

```text
Gateway of last resort is 10.0.0.194 to network 0.0.0.0

C    10.0.0.192/30 is directly connected, GigabitEthernet1/0/2
S*   0.0.0.0/0 [1/0] via 10.0.0.194
```

### 6.2 Configure SVIs on SW2

```text
SW2(config)#interface vlan 10
SW2(config-if)#ip address 10.0.0.62 255.255.255.192
SW2(config-if)#no shutdown
SW2(config-if)#exit
SW2(config)#interface vlan 20
SW2(config-if)#ip address 10.0.0.126 255.255.255.192
SW2(config-if)#no shutdown
SW2(config-if)#exit
SW2(config)#interface vlan 30
SW2(config-if)#ip address 10.0.0.190 255.255.255.192
SW2(config-if)#no shutdown
SW2(config-if)#exit
```

> An SVI is a **logical** Layer 3 interface tied to a VLAN's broadcast domain — it comes up only once at least one access or trunk port carrying that VLAN is up and forwarding somewhere on the switch. Unlike ROAS's subinterfaces, no `encapsulation dot1Q` is needed here — the SVI already knows exactly which VLAN it belongs to from its own `vlan <id>` number. **Memory aid:** "subinterface = router pretending to understand VLANs over one wire; SVI = switch that actually lives inside the VLAN."

### 6.3 SW1 — trunk to SW2 (unchanged from Day 17's pattern)

```text
SW1(config)#interface gigabitEthernet 0/1
SW1(config-if)#switchport mode trunk
SW1(config-if)#switchport trunk allowed vlan 10,20,30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

### 6.4 Save

```text
R1#copy running-config startup-config
SW2#copy running-config startup-config
SW1#copy running-config startup-config
```

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| SW2 | `show ip interface brief` | SVIs + routed port all `up/up` |
| SW2 | `show ip route` | Connected SVIs/routed link + default route |
| R1 | `show ip interface brief` | Gi0/0 up with the new routed IP, no subinterfaces remain |
| Any PC (VLAN A) | `ping <PC in VLAN B>` | Inter-VLAN routing now happens on SW2, not R1 |
| Any PC | `ping 1.1.1.1` (or any address beyond R1) | Internet-bound traffic still correctly routes through R1 |

### 7.1 Expected Output Gallery

**`SW2# show ip route`**

```text
Gateway of last resort is 10.0.0.194 to network 0.0.0.0

C    10.0.0.0/26 is directly connected, Vlan10
C    10.0.0.64/26 is directly connected, Vlan20
C    10.0.0.128/26 is directly connected, Vlan30
C    10.0.0.192/30 is directly connected, GigabitEthernet1/0/2
S*   0.0.0.0/0 [1/0] via 10.0.0.194
```

**`PC1> ping 10.0.0.4`** (inter-VLAN, now routed by SW2's ASIC, not R1's CPU)

```text
Reply from 10.0.0.4: bytes=32 time<1ms TTL=128
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

**`PC1> ping 1.1.1.1`** (internet-bound, still crosses R1)

```text
Request timed out.
Reply from 1.1.1.1: bytes=32 time=2ms TTL=253
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

The first reply timing out and later replies succeeding is normal — it reflects ARP resolution occurring on the first packet (a well-known Packet Tracer/first-hop behavior), not a real fault.

---

## 8. Common Mistakes (the 80/20)

1. **Leaving `switchport` mode on the SW2↔R1 link.** Forgetting `no switchport` means the interface stays a Layer 2 port and refuses to accept an IP address at all — this is the #1 error unique to multilayer switching labs.
2. **Leaving R1's old ROAS subinterfaces in the running-config.** They don't conflict technically, but they're stale, confusing config that no longer matches the topology — remove them explicitly.
3. **Forgetting the default route on SW2.** SVIs will happily route between VLANs without it, but nothing beyond SW2 (like the internet) is reachable until `ip route 0.0.0.0 0.0.0.0 <R1 IP>` is added.
4. **Assuming SVIs come up automatically with no dependencies.** An SVI stays down if *no* port belonging to that VLAN is currently up anywhere on the switch — it's tied to real Layer 2 activity in that VLAN, not just its own configuration.
5. **Using the same subnet mask pattern as the VLAN SVIs for the new P2P link.** The routed link to R1 needs its own dedicated `/30` sized for exactly 2 hosts, not a `/26` reused from a VLAN.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | SW2's link to R1 won't accept an IP address | Port still in switchport mode | `show running-config interface <id>` | `no switchport` before assigning the IP |
| 2 | SVI won't come up | No active port in that VLAN anywhere on the switch | `show vlan brief`, `show interfaces status` | Bring up at least one access/trunk port carrying that VLAN |
| 3 | Inter-VLAN ping fails | SVI missing `no shutdown`, or wrong IP/mask | `show ip interface brief` | Correct and bring up the SVI |
| 4 | Local VLANs work, internet doesn't | Missing default route on SW2 | `show ip route` | Add `ip route 0.0.0.0 0.0.0.0 <R1 IP>` |
| 5 | SW2↔R1 link up but no routing happens at all | `ip routing` disabled globally on the switch | `show ip route` (empty despite connected interfaces) | `ip routing` in global config |

---

## 10. Design Analysis

**Why multilayer switching over ROAS?** ROAS funnels every inter-VLAN packet through one physical link and general-purpose router CPU — fine for a handful of hosts, a real bottleneck as VLAN count and traffic volume grow. A multilayer switch routes in hardware, at the same wire speed it already switches at, with no shared-link chokepoint for intra-switch inter-VLAN traffic. **Why keep R1 at all, instead of letting SW2 do everything?** R1 still owns the boundary to the actual internet/WAN — a role a campus-grade multilayer switch typically isn't built or licensed for (NAT, WAN-facing security policy, BGP/dynamic routing to an ISP). This is the standard "distribution/core switch routes internally, edge router routes externally" split seen in real enterprise designs.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a branch office's ROAS router starts showing high CPU utilization during business hours and the fix is exactly this lab: move inter-VLAN routing onto a multilayer switch, keep the router for WAN/internet only.
- ...you're designing a new campus network from scratch and default to a Layer 3 distribution switch for inter-VLAN routing rather than routing everything through a central router, because that's simply how modern enterprise networks are built.
- ...a colleague asks "why does this switch have `no switchport` on some ports?" — being able to explain routed ports vs. SVIs vs. access/trunk ports in one breath is a core distinguishing skill between CCNA-level and pre-CCNA understanding.

---

## 12. Stretch Goal

1. Add a fourth VLAN and SVI on SW2 without touching the SW2↔R1 link at all — confirm the new VLAN routes internally without any change to the default route.
2. Replace the static default route on SW2 with a dynamic routing protocol (a preview of later labs) and predict what changes in `show ip route`'s route-source markers (`S*` vs. a protocol-specific letter).
3. Deliberately leave SW2's link to R1 in switchport mode and observe/explain the exact failure mode when trying to assign it an IP address.

---

## 13. Self-Assessment

- [ ] Can you explain, in one sentence, why a multilayer switch removes the ROAS bottleneck?
- [ ] Can you write the exact command that converts a switch port from Layer 2 to Layer 3, from memory?
- [ ] Can you explain why an SVI can be configured correctly yet still show down, and what condition brings it up?
- [ ] Can you derive the `/30` P2P subnet used in this lab by hand, including which unused block it was carved from?
- [ ] Can you explain the difference between what R1 is responsible for and what SW2 is responsible for in this design?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Routed ports (`no switchport`), SVIs, multilayer switching, default routing on a Layer 3 switch, replacing ROAS with hardware inter-VLAN routing.

**What I Learned:** Modern enterprise networks use Layer 3 switches for inter-VLAN routing to reduce latency, simplify cabling, and consolidate switching and routing into one device instead of relying on a single router link as a chokepoint. The distinction between a routed port (`no switchport`, behaves exactly like a router interface) and an SVI (a logical Layer 3 interface tied to a VLAN's Layer 2 activity) is the core new idea this lab introduces — and both types of interface show up in the same `show ip route` table alongside each other.

**Skills Practiced:** Replacing router-on-a-stick with a routed point-to-point link, default route configuration on a multilayer switch, SVI configuration, Layer 3 routing enablement, gateway configuration, inter-VLAN and internet connectivity testing, routing table verification.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md). Open vSwitch has limited Layer 3 SVI support in GNS3 — the README covers the caveat and the Cisco IOSvL2/vIOS-L2 alternative in detail.
