# Day 29 Lab Manual — OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure OSPF area 0 across a 4-router + ISP-edge topology; correct OSPF's broken default cost calculation using reference bandwidth; configure R1 as an ASBR injecting a default route into the OSPF domain; inspect OSPF Hello packet structure. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): configure and verify single-area OSPFv2, describe the OSPF metric, differentiate route types (intra-area, external), describe DR/BDR election and Hello/Dead timers. |
| **Prerequisites** | A working single-area OSPF lab (basic `router ospf` / `network` statement configuration); comfort with `show ip route` output. |
| **Time Estimate** | 2 – 2.5 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the OSPF configuration itself is routine; the reference-bandwidth math and ASBR concept are where most students slow down. |

---

## 1. Lab Overview

OSPF calculates path cost from interface bandwidth using a formula that hasn't changed its default since 1991: `cost = reference bandwidth ÷ interface bandwidth`, with a default reference bandwidth of just **100 Mbps**. In a network built entirely from 100+ Mbps links (which is every network built after roughly 2005), that default silently breaks OSPF's ability to tell a slow link from a fast one — every interface at or above 100 Mbps collapses to the same cost of 1.

This lab has two connected halves: fixing that broken cost calculation with `auto-cost reference-bandwidth`, and configuring one router (R1) as an **ASBR** (Autonomous System Boundary Router) that injects a default route into the OSPF domain — the mechanism that lets an entire multi-router network reach the internet through a single upstream router, without every router needing its own default route configured by hand.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Configure single-area OSPF across multiple routers, including passive interfaces
- Explain why the default OSPF reference bandwidth (100 Mbps) is inadequate for modern networks
- Calculate the correct `auto-cost reference-bandwidth` value to make a target interface type hit a target cost
- Configure and verify `default-information originate` on an ASBR
- Explain Type-5 external LSA propagation and equal-cost multipath default routes
- Read OSPF Hello packet fields and explain their role in neighbor adjacency formation

---

## 2. Business Context

**Why would a real company do this?**

- **"Our OSPF network has both Gigabit and 10-Gigabit backbone links, but traffic sometimes takes the slower path"** → this is *exactly* the symptom of an unfixed reference bandwidth. With the default 100 Mbps reference, both a 1 Gbps and a 10 Gbps interface calculate to OSPF cost 1 — OSPF genuinely cannot distinguish them, and may pick either path with no preference for the faster one. Every real-world OSPF deployment beyond a very small, all-identical-speed network needs this fixed on day one.
- **"We only want one router to actually touch the internet, but every internal router needs to be able to reach it"** → this is the ASBR pattern. Rather than configuring a default route by hand on every internal router (which doesn't scale and creates a maintenance nightmare when the ISP circuit changes), one router injects a single default route that OSPF automatically propagates everywhere.
- **"New engineers keep getting confused reading `show ip route` after we changed reference bandwidth"** → the critical rule that reference bandwidth must be identical on *every* router in the OSPF domain is a real operational hazard: a partial rollout (some routers updated, some not) causes inconsistent LSA metrics and can produce genuinely bad path selection, not just cosmetic differences.

This is the lab where OSPF stops being "type `network` statements and it just works" and starts requiring you to actually understand what number you're putting into the protocol and why.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-27-Lab-OSPF-(Part%202).png" width="900">
</p>

### 3.1 Topology Summary

| Device | Type | Interfaces | IP Assignments |
|---|---|---|---|
| R1 | 2911 | G0/0, F1/0, F1/1, G3/0, Lo0 | 10.0.12.1/30, 10.0.13.1/30, 203.0.113.1/30, 1.1.1.1/32 |
| R2 | 2911 | G0/0, F1/0, F2/0, Lo0 | 10.0.12.2/30, 10.0.24.1/30, 2.2.2.2/32 |
| R3 | 2911 | F1/0, F2/0, Lo0 | 10.0.13.2/30, 10.0.34.1/30, 3.3.3.3/32 |
| R4 | 2911 | F1/0, F2/0, G0/0, Lo0 | 10.0.24.2/30, 10.0.34.2/30, 192.168.4.254/24, 4.4.4.4/32 |
| SW1 | 2960-24TT | — | — |
| PC1 | PC-PT | — | 192.168.4.1 |
| ISP | (edge, off R1's G3/0) | — | 203.0.113.2/30 |

### 3.2 Traffic Flow Summary

```text
ISP -- G3/0 -- R1 (ASBR) -- G0/0 -- R2 -- F1/0 -- R4 -- SW1 -- PC1
                 |                                |
                F1/0 --------- R3 -------------- F2/0
```

R1 is the ASBR: the only router with a path to the ISP. R2 and R3 form two redundant middle paths to R4, giving R4 equal-cost paths for its default route.

---

## 4. IP Addressing Plan

### 4.1 Why Each Subnet Is Sized the Way It Is

| Segment | Hosts needed | Why this prefix |
|---|---|---|
| Every router-to-router link | Exactly 2 | `/30` — point-to-point links never need more than 2 addresses |
| R1–ISP | Exactly 2 | `/30` — same reasoning, models a real WAN handoff |
| R4 LAN (PC1 + growth room) | dozens eventually | `/24` |
| Loopbacks (Router IDs) | 1 each | `/32` — a loopback is a single logical address, not a subnet with neighbors |

### 4.2 How to Calculate These by Hand

**Router link `/30` (e.g., 10.0.12.0/30):**

```text
2^h - 2 >= 2
2^2 - 2 = 2   -> h = 2 host bits -> /30
mask = 11111111.11111111.11111111.11111100 = 255.255.255.252
```

```text
Network:    10.0.12.0
First host: 10.0.12.1  (R1)
Last host:  10.0.12.2  (R2)
Broadcast:  10.0.12.3
```

**Loopback `/32`:** a `/32` has zero host bits — `2^0 = 1`, exactly one address, which is the point: a loopback interface represents the router itself, not a network segment with multiple hosts. This is also why loopbacks are the standard choice for OSPF Router ID — they're always up as long as the router itself is up, unlike a physical interface that can go down independently.

### 4.3 Full Device Address Table

| Device | Interface | IP Address | Mask | Connects To |
|---|---|---|---|---|
| R1 | G0/0 | 10.0.12.1 | 255.255.255.252 | R2 G0/0 |
| R1 | F1/0 | 10.0.13.1 | 255.255.255.252 | R3 F1/0 |
| R1 | G3/0 | 203.0.113.1 | 255.255.255.252 | ISP |
| R1 | Lo0 | 1.1.1.1 | 255.255.255.255 | (Router ID) |
| R2 | G0/0 | 10.0.12.2 | 255.255.255.252 | R1 G0/0 |
| R2 | F1/0 | 10.0.24.1 | 255.255.255.252 | R4 F1/0 |
| R2 | Lo0 | 2.2.2.2 | 255.255.255.255 | (Router ID) |
| R3 | F1/0 | 10.0.13.2 | 255.255.255.252 | R1 F1/0 |
| R3 | F2/0 | 10.0.34.1 | 255.255.255.252 | R4 F2/0 |
| R3 | Lo0 | 3.3.3.3 | 255.255.255.255 | (Router ID) |
| R4 | F1/0 | 10.0.24.2 | 255.255.255.252 | R2 F1/0 |
| R4 | F2/0 | 10.0.34.2 | 255.255.255.252 | R3 F2/0 |
| R4 | G0/0 | 192.168.4.254 | 255.255.255.0 | SW1 (LAN) |
| R4 | Lo0 | 4.4.4.4 | 255.255.255.255 | (Router ID) |
| PC1 | NIC | 192.168.4.1 | 255.255.255.0 | SW1 |

---

## 5. Pre-Configuration Checklist

1. Place 4 routers, 1 switch, 1 PC, and an ISP-edge device/cloud matching the topology.
2. Cable per the address table above.
3. Confirm interface numbering — this manual uses the 2911's mixed Gig/Fast interfaces exactly as listed; substitute if your platform differs.
4. Have Sections 4.3 and 6 open for reference.

---

## 6. Configuration Tasks

### 6.1 Step 1 — Hostnames, interfaces, loopbacks (all 4 routers)

```text
! R1
Router(config)#hostname R1
R1(config)#interface g0/0
R1(config-if)#ip address 10.0.12.1 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface f1/0
R1(config-if)#ip address 10.0.13.1 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface g3/0
R1(config-if)#ip address 203.0.113.1 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface loopback0
R1(config-if)#ip address 1.1.1.1 255.255.255.255
R1(config-if)#no shutdown
R1(config-if)#exit
```

> **Mode:** Global Config → Interface Config. Repeat the same pattern for R2, R3, R4 using the addresses in Section 4.3. **Memory aid:** loopbacks are the one interface type that's virtual — no cable, no `no shutdown` risk of a "link down," which is exactly why OSPF prefers them as Router IDs.

### 6.2 Step 2 — Enable OSPF, configure passive interfaces

```text
! R1
R1(config)#router ospf 1
R1(config-router)#network 10.0.12.0 0.0.0.3 area 0
R1(config-router)#network 10.0.13.0 0.0.0.3 area 0
R1(config-router)#network 1.1.1.1 0.0.0.0 area 0
R1(config-router)#passive-interface g3/0
R1(config-router)#passive-interface loopback0
```

> **Mode:** Global Config → Router Config (`router ospf 1`). The `network` statement uses a **wildcard mask** (inverse of a subnet mask) — `0.0.0.3` matches exactly the 4 addresses in a `/30`. `passive-interface` stops OSPF from sending Hellos out an interface (no neighbor will ever exist there — the ISP edge and the loopback itself) while *still* advertising that interface's network into OSPF. **Why passive on G3/0:** you don't want the ISP accidentally becoming an OSPF neighbor; you still want R1's other routers to know that subnet exists.

```text
! R2
R2(config)#router ospf 1
R2(config-router)#network 10.0.12.0 0.0.0.3 area 0
R2(config-router)#network 10.0.24.0 0.0.0.3 area 0
R2(config-router)#network 2.2.2.2 0.0.0.0 area 0
R2(config-router)#passive-interface loopback0

! R3
R3(config)#router ospf 1
R3(config-router)#network 10.0.13.0 0.0.0.3 area 0
R3(config-router)#network 10.0.34.0 0.0.0.3 area 0
R3(config-router)#network 3.3.3.3 0.0.0.0 area 0
R3(config-router)#passive-interface loopback0

! R4
R4(config)#router ospf 1
R4(config-router)#network 10.0.24.0 0.0.0.3 area 0
R4(config-router)#network 10.0.34.0 0.0.0.3 area 0
R4(config-router)#network 192.168.4.0 0.0.0.255 area 0
R4(config-router)#network 4.4.4.4 0.0.0.0 area 0
R4(config-router)#passive-interface g0/0
R4(config-router)#passive-interface loopback0
```

### 6.3 Step 3 — Fix the reference bandwidth (every router)

**The math:** OSPF cost = reference bandwidth ÷ interface bandwidth. FastEthernet is 100 Mbps. To make FastEthernet land on cost 100 (the CCNA-standard target):

```text
100 = Reference Bandwidth / 100
Reference Bandwidth = 10,000 Mbps  (10 Gbps)
```

```text
! Run identically on R1, R2, R3, R4
R1(config)#router ospf 1
R1(config-router)#auto-cost reference-bandwidth 10000
% OSPF: Reference bandwidth is changed.
Please ensure reference bandwidth is consistent across all routers.
```

> **Mode:** Router Config. This is the single most important rule in this lab: **every router in the OSPF domain must use the identical reference bandwidth value.** If R1 uses 10000 and R4 is left at the default 100, the two routers calculate different costs for the *same physical link*, and their LSAs will disagree — OSPF may then make inconsistent or suboptimal path decisions across the domain, which is a subtle, hard-to-diagnose fault precisely because OSPF doesn't refuse to work, it just works *wrong*.

With the fix applied: FastEthernet interfaces now show cost 100 (`10000/100`), GigabitEthernet interfaces show cost 10 (`10000/1000`) — OSPF can finally tell the two apart.

### 6.4 Step 4 — Configure R1 as ASBR with default route injection

```text
R1(config)#router ospf 1
R1(config-router)#default-information originate
```

> **Mode:** Router Config. This single command tells OSPF: "if I (R1) have a default route in my own routing table (typically a static route to the ISP, or a directly connected path), advertise `0.0.0.0/0` into OSPF as a **Type-5 external LSA**." Every other router in the domain installs this as an `O*E2` route without needing any default route configured locally — this is the entire point of an ASBR: centralize the "how do we reach the internet" knowledge in one place.

> **Note:** For `default-information originate` to actually advertise anything, R1 typically needs its own default route already present (e.g., `ip route 0.0.0.0 0.0.0.0 203.0.113.2` toward the ISP, or the `always` keyword to originate regardless: `default-information originate always`).

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip interface brief` | All interfaces `up/up`, correct IPs |
| `show ip protocols` | OSPF process running, passive interfaces listed correctly |
| `show ip ospf interface <if>` | Cost per interface matches your reference-bandwidth math |
| `show ip route ospf` | `O` and `O*E2` routes present |
| `show ip ospf` | Confirms ASBR role on R1 |
| `show ip ospf neighbor` | Full adjacency state with each expected neighbor |

### 7.1 Expected Output Gallery

**`R1# show ip ospf interface f1/0`**

```text
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.0.13.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 100
```

**`R1# show ip ospf interface g0/0`**

```text
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.0.12.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 10
```

**`R1# show ip ospf`**

```text
Routing Process "ospf 1" with ID 1.1.1.1
 ...
 It is an autonomous system boundary router
 ...
 Number of external LSA 1.
```

**`R4# show ip route`**

```text
Gateway of last resort is 10.0.24.1 to network 0.0.0.0

C    4.4.4.4/32 is directly connected, Loopback0
O    10.0.12.0/30 [110/20] via 10.0.24.1, FastEthernet1/0
C    10.0.24.0/30 is directly connected, FastEthernet1/0
O    10.0.13.0/30 [110/200] via 10.0.34.1, FastEthernet2/0
C    10.0.34.0/30 is directly connected, FastEthernet2/0
C    192.168.4.0/24 is directly connected, GigabitEthernet0/0
O*E2 0.0.0.0/0 [110/1] via 10.0.24.1, FastEthernet1/0
              [110/1] via 10.0.34.1, FastEthernet2/0
```

R4 receives **two equal-cost default routes** — one via R2, one via R3 — and installs both (Equal-Cost Multi-Path). `O*E2` marks it as an OSPF external Type-2 route (the default type for `default-information originate`, meaning the external cost stays constant regardless of internal path cost).

---

## 8. OSPF Hello Message Deep-Dive

**Accessing Simulation Mode (Packet Tracer):** click the Simulation icon, add an OSPF Simple-PDU filter, and observe a Hello packet's structure directly.

| Field | Value | Purpose |
|---|---|---|
| Version | 2 | OSPFv2 for IPv4 |
| Type | 1 | Hello packet |
| Router ID | 1.1.1.1 | Originating router's identity |
| Area ID | 0.0.0.0 | Must match on both sides for adjacency |
| Hello Interval | 10 sec | How often Hellos are sent (broadcast default) |
| Dead Interval | 40 sec | Neighbor declared down after this silence (4x Hello) |
| Router Priority | 1 | DR/BDR election tiebreaker |
| DR / BDR IP | (segment-specific) | Elected on multi-access networks |
| Neighbor List | [2.2.2.2, 3.3.3.3, ...] | Routers this speaker has already seen — required for bidirectional adjacency |

**Key exam facts:**

- Hello: 10 sec (broadcast/point-to-point), 30 sec (NBMA)
- Dead: 40 sec (broadcast), 120 sec (NBMA) — always 4x Hello
- Area ID mismatch = adjacency never forms, silently
- Two routers must see **each other** in their neighbor list before the adjacency completes — this is why it's called bidirectional communication, not just "I heard a Hello."

---

## 9. Common Mistakes (the 80/20)

1. **Setting `auto-cost reference-bandwidth` on only some routers.** The IOS warning message is not a suggestion — inconsistent reference bandwidth across the OSPF domain produces mismatched LSA costs and unpredictable path selection.
2. **Forgetting `passive-interface` on the ISP-facing and loopback interfaces.** Without it, OSPF may attempt to form a neighbor relationship out an interface that should never have one (like the ISP edge), or waste Hello traffic on a loopback that has no neighbor to begin with.
3. **Expecting `default-information originate` to work with no default route present on the ASBR.** Without `always`, R1 needs its own default route (static or otherwise) before it will originate one into OSPF.
4. **Misreading `[110/1]`** as "cost 1" for the whole path. The bracket is `[administrative-distance/cost]` — `110` is OSPF's AD, `1` is the metric assigned to the external route (constant for E2 routes, regardless of internal path cost).
5. **Confusing Hello interval mismatches with Area ID mismatches.** Both prevent adjacency, but `show ip ospf neighbor` combined with `debug ip ospf adj` (used carefully) distinguishes them — Hello/Dead mismatches show up differently than Area ID mismatches in the log output.

---

## 10. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | No OSPF neighbors form | Area ID mismatch, or `network` statement wildcard mask wrong | `show ip ospf neighbor` / `show ip protocols` | Correct the `network` statement or Area ID |
| 2 | Neighbor forms then flaps | Hello/Dead interval mismatch between the two routers | `show ip ospf interface <if>` (compare timers) | Match Hello/Dead intervals on both sides |
| 3 | FastEthernet and GigabitEthernet show the same OSPF cost | Reference bandwidth not yet changed, or changed inconsistently | `show ip ospf interface <if>` on both ends | Apply `auto-cost reference-bandwidth 10000` on every router |
| 4 | R1 doesn't show as ASBR | `default-information originate` missing, or no default route present on R1 | `show ip ospf` | Add the command; add `always` or a real default route |
| 5 | R4 only sees one default route instead of two | One of R2/R3's paths is down or missing an OSPF `network` statement | `show ip route ospf` on R4, `show ip ospf neighbor` on R2/R3 | Fix the missing/broken OSPF adjacency on that path |

---

## 11. Design Analysis

**Why fix reference bandwidth instead of just leaving OSPF cost-blind above 100 Mbps?** Because the entire value of a link-state protocol like OSPF is picking the objectively best path using real metrics — if every fast link looks identical to OSPF, you've effectively downgraded it to "pick any path that isn't explicitly slower," losing the precision that's the whole reason to run OSPF instead of a simpler distance-vector protocol.

**Why `default-information originate` on one router instead of a static default route on every router?** Centralizing the default route means the ISP relationship — the one thing most likely to change (new circuit, new ISP, new next-hop) — only needs to be updated in one place. Every internal router automatically re-learns the new default the moment R1's LSA updates, with zero manual touch on R2, R3, or R4.

**Why let R4 keep two equal-cost default routes instead of picking one?** Equal-cost multipath isn't a compromise — it's free load-balancing and, more importantly, automatic failover. If the R2 path dies, R4 still has the R3-derived default route with zero convergence delay for that specific route, because it was already installed.

---

## 12. Real-World Parallel

You'd see the reference-bandwidth problem the moment any real enterprise upgrades its backbone from Fast Ethernet/Gigabit to 10G or 40G without revisiting OSPF settings — a shockingly common oversight, because the network "still works," it's just picking suboptimal paths silently. You'd see the ASBR/default-route-injection pattern in literally any OSPF network with exactly one (or a small number of) internet-facing router(s) — it's the standard design, not an edge case.

---

## 13. Stretch Goal

1. Set reference bandwidth to `100000` instead of `10000` (common in dense 10G+ cores) and recalculate what cost FastEthernet and GigabitEthernet interfaces would show.
2. Add a second ISP-facing router with its own default route and `default-information originate`, and observe how R4's routing table changes with a third equal-cost (or unequal-cost, if you vary the path) default route.
3. Use `debug ip ospf adj` (carefully, and only briefly) to watch a neighbor adjacency form in real time, correlating it against the Hello/Dead interval fields from Section 8.

---

## 14. Self-Assessment

- [ ] Can you state the OSPF cost formula from memory and calculate cost for any given reference bandwidth and interface speed?
- [ ] Can you explain why reference bandwidth must match across the entire OSPF domain?
- [ ] Can you write `default-information originate` and explain what LSA type it generates?
- [ ] Do you know the default Hello/Dead intervals for broadcast networks, and the ratio between them?
- [ ] Could you explain to a non-technical manager why "we fixed OSPF's math" was worth doing?

---

## 15. Key Concepts Demonstrated

- Single-area OSPF configuration with passive interfaces
- OSPF cost calculation and the reference-bandwidth formula
- ASBR role and Type-5 (E2) external route injection
- Equal-cost multipath default routing
- OSPF Hello packet structure and neighbor adjacency requirements

---

## 16. What I Learned

The reference-bandwidth default being unchanged since 1991 is a genuinely useful fact to internalize — it's a reminder that a protocol's defaults are historical artifacts, not universal truths, and that "the default is probably fine" is a dangerous assumption once your network exceeds the speeds that existed when the default was set. The ASBR/default-route-injection piece reinforced a broader design principle that shows up constantly in networking: centralize the thing that changes (the ISP relationship) so it only has to be maintained in one place, and let the routing protocol propagate the consequence everywhere automatically.

---

## 17. Skills Practiced

- Multi-router single-area OSPF configuration
- OSPF cost/reference-bandwidth calculation
- ASBR configuration and default-route injection
- OSPF Hello packet field analysis
- Equal-cost multipath verification

---

## 18. GNS3 Lab

This lab has a companion GNS3 topology built by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1-R4) | Cisco 2911 | VyOS |
| Switch (SW1) | Cisco 2960 | Open vSwitch |
| PC1 | Generic PC | Alpine Linux |
| ISP edge | (edge router) | VyOS |

See [`GNS3/README.md`](GNS3/README.md). VyOS supports OSPF natively (`set protocols ospf`), including reference bandwidth (`set protocols ospf auto-cost reference-bandwidth`) and default-route origination (`set protocols ospf default-information originate`) — the README includes the syntax translation table.
