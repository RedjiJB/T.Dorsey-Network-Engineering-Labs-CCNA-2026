# Day 29 Lab Manual — OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Fix OSPF's broken default cost metric for modern link speeds via reference bandwidth, understand the Hello/Dead timer relationship, and configure an ASBR to inject a default route into OSPF |
| CCNA 200-301 Domains | 3.0 IP Connectivity (OSPFv2 configuration, cost metric, `auto-cost reference-bandwidth`, ASBR, default route origination), 1.0 Network Fundamentals (routing concepts) |
| Prerequisites | OSPF single-area configuration, `network`/`area` statements, passive interfaces, static/default routing concepts |
| Estimated Time | 75–90 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

OSPF picks best paths using cost, and cost is derived from bandwidth — but the formula it uses by default was written in 1991, when 100 Mbps was the fastest link anyone had. That default silently breaks on any network with Gigabit or faster links, because every interface at or above 100 Mbps collapses to the same cost of 1. This lab fixes that by hand-deriving and configuring a modern reference bandwidth, then goes on to configure one router as an Autonomous System Boundary Router (ASBR) injecting a default route into the OSPF domain — the standard way an internal OSPF network gets a path to the outside world — and finally uses packet-level inspection of OSPF Hello messages to make the neighbor-formation process concrete rather than assumed.

By the end of this lab you will be able to:

1. Explain why OSPF's default reference bandwidth (100 Mbps) produces incorrect path selection on modern networks.
2. Derive a new reference bandwidth value from a target cost, and configure it consistently across every router in the OSPF domain.
3. Explain the relationship between Hello interval and Dead interval, and why mismatches block adjacency.
4. Configure a router as an ASBR that injects a default route (`default-information originate`) into OSPF as a Type-5 external LSA.
5. Verify OSPF costs, neighbor states, and externally-learned default routes using `show` commands.
6. Read and interpret real OSPF Hello packet fields captured at the packet level.

## 2. Business Context

Any mid-size-or-larger enterprise network running OSPF eventually hits this exact problem: the network was built (or grew) past FastEthernet, and nobody adjusted `auto-cost reference-bandwidth` — so OSPF is silently making path decisions as if all links were equally fast, potentially routing traffic across a slower link instead of a faster one. This is a real, commonly-audited misconfiguration in production networks, not a textbook-only concern. Separately, every OSPF network that connects to an ISP or other outside network needs exactly one (or a small controlled number of) router acting as the boundary between "known via OSPF" and "everything else" — that's the ASBR default-route pattern used here, identical to how a real edge router hands off default routing to an entire internal OSPF domain without every internal router needing its own path to the internet.

## 3. Topology Reference

| Device | Role | Interfaces |
|---|---|---|
| R1 | ASBR — connects to simulated ISP, injects default route into OSPF | G0/0 (to R2), F1/0 (to R3), G3/0 (to ISP), Lo0 |
| R2 | Internal OSPF router | G0/0 (to R1), F1/0 (to R4), Lo0 |
| R3 | Internal OSPF router | F1/0 (to R1), F2/0 (to R4), Lo0 |
| R4 | Internal OSPF router, LAN edge | F1/0 (to R2), F2/0 (to R3), G0/0 (LAN), Lo0 |
| SW1 | LAN switch off R4 | — |
| PC1 | End host on R4's LAN | — |

All four routers plus R1's ISP-facing link sit in a single OSPF Area 0 (backbone) — this is intentionally a single-area design so the lab isolates cost/reference-bandwidth and ASBR behavior without adding multi-area complexity.

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-27-Lab-OSPF-(Part%202).png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

Every inter-router link is a point-to-point connection needing exactly 2 usable host addresses, so each is sized as a `/30` (2 usable hosts) — the standard, minimum-waste choice for router-to-router links. The LAN off R4 needs to support many future end hosts, so it's sized generously as a `/24`. Each router also carries a `/32` loopback used as a stable OSPF router ID, unaffected by any physical interface flapping.

### 4.2 Manual Calculation Walkthrough (point-to-point /30)

```
10.0.12.0/30
Host bits = 32 - 30 = 2 host bits → 2^2 = 4 total addresses
Usable hosts = 4 - 2 (network + broadcast) = 2  ✓ exactly enough for a point-to-point link
Block size = 256 - 255 (last octet mask 252) = 4

Network address:    10.0.12.0
First usable host:  10.0.12.1   (R1's side)
Last usable host:    10.0.12.2   (R2's side)
Broadcast address:   10.0.12.3
```
The same math (block size 4, mask 255.255.255.252) applies to every other `/30` in this topology — only the network address changes.

For the LAN off R4:
```
192.168.4.0/24
Host bits = 32 - 24 = 8 host bits → 2^8 = 256 total addresses
Usable hosts = 256 - 2 = 254
Network address:    192.168.4.0
First usable host:  192.168.4.1
Last usable host:    192.168.4.254   (assigned to R4's G0/0 as the LAN gateway)
Broadcast address:   192.168.4.255
```

### 4.3 Address Table

| Link/Interface | Network | R1 | R2 | R3 | R4 |
|---|---|---|---|---|---|
| R1–R2 | 10.0.12.0/30 | .1 (G0/0) | .2 (G0/0) | — | — |
| R1–R3 | 10.0.13.0/30 | .1 (F1/0) | — | .2 (F1/0) | — |
| R2–R4 | 10.0.24.0/30 | — | .1 (F1/0) | — | .2 (F1/0) |
| R3–R4 | 10.0.34.0/30 | — | — | .1 (F2/0) | .2 (F2/0) |
| R1–ISP | 203.0.113.0/30 | .1 (G3/0) | — | — | — |
| R4 LAN | 192.168.4.0/24 | — | — | — | .254 (G0/0) |
| Loopbacks | /32 each | 1.1.1.1 | 2.2.2.2 | 3.3.3.3 | 4.4.4.4 |

## 5. Pre-Configuration Checklist

- [ ] Confirm every point-to-point link uses a `/30` and every loopback is a `/32` before touching OSPF
- [ ] Decide the OSPF process ID and area (this lab: process 1, single Area 0) — consistent across all routers
- [ ] Decide which interfaces should be passive (any interface with no OSPF neighbor expected — LAN-facing, ISP-facing, and all loopbacks)
- [ ] Decide the target FastEthernet cost before calculating reference bandwidth (this lab targets cost 100, forcing reference bandwidth = 10,000 Mbps)
- [ ] Confirm which single router will be the ASBR (R1, the one with ISP connectivity) — injecting a default route from more than one router without care can create routing black holes or asymmetric paths

## 6. Configuration Tasks

### 6.1 Base interface configuration

```
R1(config)# interface g0/0
R1(config-if)# ip address 10.0.12.1 255.255.255.252
R1(config-if)# no shutdown
R1(config)# interface f1/0
R1(config-if)# ip address 10.0.13.1 255.255.255.252
R1(config-if)# no shutdown
R1(config)# interface g3/0
R1(config-if)# ip address 203.0.113.1 255.255.255.252
R1(config-if)# no shutdown
R1(config)# interface loopback0
R1(config-if)# ip address 1.1.1.1 255.255.255.255
```
Repeat the equivalent addressing on R2, R3, R4 per the address table above. Mode: interface configuration. Loopbacks never go administratively down on their own (no physical link to fail), which is exactly why OSPF prefers them as router IDs — the router ID stays stable even if a physical interface flaps.

### 6.2 Enable OSPF and mark passive interfaces

```
R1(config)# router ospf 1
R1(config-router)# network 10.0.12.0 0.0.0.3 area 0
R1(config-router)# network 10.0.13.0 0.0.0.3 area 0
R1(config-router)# network 1.1.1.1 0.0.0.0 area 0
R1(config-router)# passive-interface g3/0
R1(config-router)# passive-interface loopback0
```
Mode: router configuration submode (`router ospf 1`). The `network <address> <wildcard> area 0` statement enables OSPF on any interface whose IP falls inside that wildcard range and places it in area 0. `passive-interface` still advertises the interface's subnet into OSPF, but suppresses Hello packets on it — used here on G3/0 (facing the ISP, no OSPF neighbor expected there) and on every loopback (no physical neighbor exists on a loopback, so sending Hellos there is pure waste and a minor security exposure). Memory aid: "passive = advertise the route, don't try to make friends on that interface." Repeat equivalent `network`/`passive-interface` statements on R2, R3, R4, each only covering their own directly-connected subnets and their own loopback.

### 6.3 Fix the reference bandwidth

**The problem, worked from the formula:**
```
OSPF Cost = Reference Bandwidth (Mbps) / Interface Bandwidth (Mbps)

Default reference bandwidth = 100 Mbps
FastEthernet (100 Mbps):     cost = 100 / 100 = 1
GigabitEthernet (1000 Mbps): cost = 100 / 1000 = 0.1 → rounded up to 1 (OSPF cost is an integer, minimum 1)
```
With the default, FastEthernet and GigabitEthernet both compute to cost 1 — OSPF literally cannot tell them apart, and will treat a 100 Mbps path and a 1000 Mbps path as equally good, potentially load-balancing traffic onto the slower link.

**Deriving the fix — target: FastEthernet should cost exactly 100:**
```
100 = Reference Bandwidth / 100
Reference Bandwidth = 100 × 100 = 10,000 Mbps  (10 Gbps)
```

```
R1(config)# router ospf 1
R1(config-router)# auto-cost reference-bandwidth 10000
```
Mode: router configuration submode. This must be run **identically** on every router in the OSPF domain — IOS even prints a warning to say so:
```
% OSPF: Reference bandwidth is changed.
Please ensure reference bandwidth is consistent across all routers.
```
If routers disagree on reference bandwidth, the *same physical link* computes a different cost on each end, corrupting the metrics inside Type-1/Type-2 LSAs and producing inconsistent — potentially loop-prone — path selection across the domain. Memory aid: "reference bandwidth isn't a per-router setting, it's a domain-wide agreement — change it everywhere or not at all."

**Result with reference bandwidth 10000:**

| Interface Type | Bandwidth | Cost (default 100) | Cost (ref 10000) |
|---|---|---|---|
| FastEthernet | 100 Mbps | 1 (broken — indistinguishable from Gig) | 100 |
| GigabitEthernet | 1000 Mbps | 1 (broken) | 10 |
| Serial (T1) | 1544 Kbps | 64 | 6477 |

### 6.4 Configure R1 as ASBR injecting a default route

```
R1(config)# router ospf 1
R1(config-router)# default-information originate
```
Mode: router configuration submode. This tells R1 — which already has a static or learned default route toward the ISP outside OSPF — to originate a `0.0.0.0/0` default route into OSPF as a Type-5 external LSA, flooded to every router in the domain. Any internal router (R2, R3, R4) that has no other way to reach the internet now gets exactly that path, without needing individual static routes or its own ISP connection. This single command is what makes R1 an ASBR — a router that redistributes routing information from outside the OSPF domain into it. Memory aid: "`default-information originate` = 'I'll be everyone's exit door.'"

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show ip ospf interface <if>` | any router | Confirm per-interface OSPF cost, area, and network type |
| `show ip protocols` | any router | Confirm passive interfaces and OSPF process settings |
| `show ip ospf neighbor` | any router | Confirm adjacency state (should reach `FULL`) with each expected neighbor |
| `show ip route ospf` | R2/R3/R4 | Confirm the default route was learned as `O*E2` |
| `show ip ospf` | R1 | Confirm R1 reports itself as an ASBR and shows external LSA count |
| `show ip route` | R4 | Confirm gateway of last resort and full routing table |

### Expected Output Gallery

```
R1# show ip ospf interface f1/0
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.0.13.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 100
  Transmit Delay is 1 sec, State DR, Priority 1
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```

```
R1# show ip ospf interface g0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.0.12.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 10
```

```
R1# show ip protocols
Routing Protocol is "ospf 1"
  ...
  Passive Interface(s):
    GigabitEthernet3/0
    Loopback0
  Routing for Networks:
    10.0.12.0 0.0.0.3 area 0
    10.0.13.0 0.0.0.3 area 0
    1.1.1.1 0.0.0.0 area 0
```

```
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2         1     FULL/DR         00:00:38    10.0.12.2       GigabitEthernet0/0
3.3.3.3         1     FULL/BDR        00:00:33    10.0.13.2       FastEthernet1/0
```

```
R4# show ip route ospf
O    10.0.12.0/30 [110/20] via 10.0.24.1, 00:05:44, FastEthernet1/0
O    10.0.13.0/30 [110/110] via 10.0.34.1, 00:05:41, FastEthernet2/0
O*E2 0.0.0.0/0 [110/1] via 10.0.24.1, 00:02:12, FastEthernet1/0
     [110/1] via 10.0.34.1, 00:02:12, FastEthernet2/0
```

```
R1# show ip ospf
Routing Process "ospf 1" with ID 1.1.1.1
  ...
  It is an autonomous system boundary router
  Redistributing External Routes from,
  Number of external LSA 1, checksum sum ...
```

## 8. Common Mistakes (80/20)

1. **Changing reference bandwidth on only one router** — the single most common error on this exact topic; produces inconsistent costs domain-wide and triggers the IOS warning, which is often ignored.
2. **Forgetting `passive-interface` on the ISP-facing link and loopbacks** — wastes Hello traffic and, worse, exposes an OSPF-speaking interface toward an untrusted external network.
3. **Assuming `[110/1]` in `show ip route` means "cost 1 total"** — the second number is the OSPF metric for that specific route, not a universal indicator; for external (E2) routes it defaults to reflecting the *external* cost R1 assigned, not the internal path cost to reach R1.
4. **Injecting a default route from more than one router without a plan** — can create asymmetric routing or routing black holes if the two ASBRs don't have equivalent actual paths out.
5. **Confusing "advertise the network" with "form adjacency"** — a `network` statement without the interface actually being in that mode's supported network type (or with mismatched Area ID/authentication) advertises nothing if adjacency never forms in the first place; always check `show ip ospf neighbor` for `FULL`, not just the routing table.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Are interfaces up/up with correct IPs? | `show ip interface brief` | Fix addressing, `no shutdown` |
| 2 | Is OSPF enabled on the expected interfaces? | `show ip protocols` | Correct `network` statements/wildcard masks |
| 3 | Did neighbors form and reach FULL? | `show ip ospf neighbor` | Check Area ID match, Hello/Dead timer match, ACLs, MTU mismatch |
| 4 | Is reference bandwidth consistent across all routers? | `show ip ospf interface <if>` on each router, compare cost for same link | Re-run `auto-cost reference-bandwidth 10000` on any router missed |
| 5 | Did R1 advertise itself as ASBR? | `show ip ospf` on R1 | Re-verify `default-information originate` is present under `router ospf 1` |
| 6 | Did internal routers learn the default route? | `show ip route ospf` on R2/R3/R4 | Confirm adjacency to R1 (directly or transitively) is FULL, not just that the command was typed |

## 10. Design Analysis

The alternative to fixing reference bandwidth is leaving it at default and accepting that OSPF can't distinguish FastEthernet from 10 Gigabit — acceptable only on a lab network that will never grow, unacceptable on anything resembling production. The alternative to a single ASBR injecting a default route is configuring individual default or static routes on every internal router pointing at their own ISP connection — far more hardware, far more config to maintain, and no single point of control if the exit policy changes. Centralizing default-route origination at one (or a small, deliberately-chosen number of) ASBR trades a single point of failure for dramatically simpler operations — which is why real networks pair this design with redundancy (a second ASBR, or HSRP/VRRP upstream) rather than avoiding the pattern altogether.

## 11. Real-World Parallel

Every enterprise network with a single internet edge router (or a small redundant pair) uses exactly this pattern: the edge router(s) hold the actual default route toward the ISP (via static route or BGP), and `default-information originate` (or the BGP/EIGRP equivalent) hands that reachability to the entire internal IGP domain — internal routers never need to know or care how the edge actually reaches the internet, they just trust the injected default. Reference bandwidth correction is likewise a standard item on any OSPF network health/migration checklist the moment a network upgrades past 100 Mbps core links.

## 12. Stretch Goal

Add a second ASBR (a router with its own path to a different, redundant ISP connection) also running `default-information originate`, and observe how internal routers pick between the two default routes using OSPF cost — then intentionally fail one path and confirm OSPF reconverges onto the surviving default route automatically.

## 13. Self-Assessment

- [ ] I can derive the reference-bandwidth value needed for a target FastEthernet cost, from the formula, without looking it up
- [ ] I can explain why an inconsistent reference bandwidth across routers is dangerous, not just "against best practice"
- [ ] I configured OSPF, passive interfaces, and reference bandwidth on all four routers myself
- [ ] I configured R1 as an ASBR and verified it reports itself as such in `show ip ospf`
- [ ] I verified the default route actually propagated to R2, R3, and R4 with `show ip route ospf`
- [ ] I can state the Hello/Dead interval defaults and explain why Dead is a multiple of Hello

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** OSPF cost formula, `auto-cost reference-bandwidth`, domain-wide consistency requirements, passive interfaces, ASBR, `default-information originate`, Type-5 external LSAs, OSPF Hello/Dead timers, DR/BDR election.

**What I Learned:** OSPF's default reference bandwidth (100 Mbps) is a historical artifact that actively breaks path selection on any modern network — this isn't an edge case, it's the default state of an unconfigured OSPF network today. Fixing it is a single command, but that command is meaningless unless applied identically everywhere, because OSPF cost only makes sense as a domain-wide agreement, not a per-router setting.

**Skills Practiced:** Multi-router OSPF single-area configuration, manual OSPF cost derivation from the reference-bandwidth formula, passive-interface planning, ASBR configuration and verification, reading external (E2) routes in a routing table, packet-level Hello inspection.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-29/GNS3/build_lab.py` and its companion `README.md` for an automated build of this five-router-equivalent topology (R1–R4 plus a simulated ISP edge) using VyOS routers, an Open vSwitch LAN switch, and an Alpine Linux end host, with notes on translating the IOS OSPF commands above to VyOS's `set protocols ospf` syntax.
