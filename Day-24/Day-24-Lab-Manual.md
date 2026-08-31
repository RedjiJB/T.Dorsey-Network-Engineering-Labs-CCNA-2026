# Day 24 Lab Manual — Floating Static Routes and Failover Testing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Deploy floating static routes as automatic backups to an OSPF-learned LAN route and to a primary Internet default route, then prove failover works by shutting down the primary path. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): static routing, floating static routes, administrative distance, route selection/longest-prefix-match, default routing. |
| **Prerequisites** | OSPF single-area basics, static routing syntax, administrative distance concept, `show ip route` table literacy. |
| **Time Estimate** | 1.5 – 2 hours first attempt; 25–35 minutes on repeat. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the config itself is short, but reasoning about *which* AD wins *when* trips up almost everyone the first time. |

---

## 1. Lab Overview + Learning Objectives

R1 and R2 are enterprise edge routers, each dual-homed to its own ISP border router (ISPBR1 and ISPBR2 respectively) for Internet access, and connected to each other over an OSPF-routed backbone link carrying the internal 10.0.1.0/24 (PC side) and 10.0.2.0/24 (server side) LANs. Every path in this design has a **primary** (OSPF-learned, or a directly-connected ISP default route) and a **floating static backup** configured with a higher administrative distance so it only activates when the primary disappears.

By the end of this lab you will be able to:

- Explain administrative distance and predict which route Cisco IOS installs when multiple sources learn the same destination
- Configure a floating static route that stays dormant until its primary route withdraws
- Simulate a link failure and observe automatic failover in `show ip route`
- Verify failover with `ping`/`traceroute` and interpret OSPF adjacency-change syslog messages
- Explain why a floating static route with an unreachable next hop is worse than having no backup at all

---

## 2. Business Context

**Why would a real company do this?**

- **"We can't have server access go down just because one router's uplink flaps"** → the OSPF-learned route to the server LAN is the fast, dynamically-maintained path; the floating static is the safety net that requires zero human intervention when OSPF loses its neighbor.
- **"Our ISP has had two outages this year"** → each enterprise router is dual-homed to its own ISP border router, and each ISP border router itself carries floating statics back toward the enterprise LANs — redundancy that cascades through every hop, not just the edge.
- **"We're not ready to run BGP with two ISPs yet"** → floating static routes are the pre-BGP, pre-dynamic-multihoming way small and mid-sized companies get "good enough" redundancy without the operational overhead of a routing protocol with an external ISP.
- **"A backup path that doesn't actually work is worse than no backup"** → this lab deliberately makes you verify the floating static's next hop is truly reachable before trusting it, mirroring a very common real-world failure: someone configures a backup route once, it's never tested, and the day it's needed it points at a dead interface.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-24-Lab-Floating-Static-Routes.png" alt="Day 24 Floating Static Routes Lab" width="900">
</p>

```text
PC1 -- SW1 -- R1 ===OSPF backbone=== R2 -- SW2 -- SRV1
              |                        |
           ISPBR1                   ISPBR2
              \________ISP cloud________/
```

| Device | Model | Interfaces | Role |
|---|---|---|---|
| R1 | 2911 | G0/1 (LAN), G0/2/0 (to R2), G0/0/0 (to ISPBR1) | Enterprise edge router 1 |
| R2 | 2911 | G0/1 (LAN), G0/0/0 (to R1), G0/1/0 (to ISPBR2) | Enterprise edge router 2 |
| ISPBR1 | 2911 | G0/0/0 (to R1) | ISP border router 1 |
| ISPBR2 | 2911 | G0/0/0 (to R2) | ISP border router 2 |
| SW1 | 2960-24TT | G0/1 | Access switch, PC segment |
| SW2 | 2960-24TT | G0/1 | Access switch, server segment |
| PC1 | PC | — | 10.0.1.0/24 |
| SRV1 | Server | — | 10.0.2.0/24 |

---

## 4. IP Addressing Plan

| Segment | Network | Usable Range | Sizing Reason |
|---|---|---|---|
| PC LAN (behind R1) | 10.0.1.0 /24 | .1 – .254 | User segment, room for growth |
| Server LAN (behind R2) | 10.0.2.0 /24 | .1 – .254 | Server segment, room for growth |
| R1 ↔ R2 backbone | 10.0.0.0 /30 | .1 – .2 | Point-to-point, always exactly 2 hosts |
| R1 ↔ ISPBR1 | 203.0.113.0 /30 | .1 – .2 | Point-to-point |
| R2 ↔ ISPBR2 | 203.0.113.4 /30 | .1 – .2 | Point-to-point |

### 4.1 Manual Calculation — Backbone Link (10.0.0.0/30)

**Step 1:** a router-to-router backbone link needs exactly 2 usable hosts.

**Step 2 — solve for host bits:**
```text
2^h − 2 ≥ 2  →  2^2 − 2 = 2  →  h = 2  →  prefix = 32 − 2 = /30
```

**Step 3 — binary-to-decimal mask:**
```text
/30 = 11111111.11111111.11111111.11111100 = 255.255.255.252
```

**Step 4 — network/host/broadcast for 10.0.0.0/30:**
```text
Network address:    10.0.0.0
First usable host:  10.0.0.1   (R1)
Last usable host:   10.0.0.2   (R2)
Broadcast address:  10.0.0.3
```

**Block-size shortcut:** block size = 2^h = 4, so consecutive /30 blocks land at .0, .4, .8, .12 — this is exactly why the two ISP-facing /30s in this plan sit at 203.0.113.0 and 203.0.113.4, four apart, with zero wasted or overlapping space.

---

## 5. Pre-Configuration Checklist

- [ ] OSPF process is already running between R1 and R2 over the backbone link before you touch static routes — floating statics only make sense as a backup to a primary that already exists.
- [ ] Confirm each router's default route to its ISP is in place and working (`ping` to a simulated Internet host) before adding a float.
- [ ] Note the administrative distance of your primary route type: OSPF = 110, directly-connected static default = 1.
- [ ] Pick a float AD **higher** than the primary you're backing up (120 is the CCNA-standard convention) but lower than "unreachable" (255, which IOS treats as a route it will never install).
- [ ] Confirm the floating static's next hop is reachable via a path that does *not* depend on the primary you're testing failover against — otherwise the float is dead weight.

---

## 6. Configuration Tasks

### 6.1 Task 1 — Confirm the Dynamic Routing Protocol In Use

```cisco
R1# show ip route
R1# show ip ospf neighbor
R1# show ip protocols
```
Look for `O` entries in the routing table and a `FULL` neighbor state — this confirms OSPF is the protocol carrying the 10.0.1.0/24 ↔ 10.0.2.0/24 route between R1 and R2, with administrative distance 110 (visible via `show ip protocols` or implied by the `[110/2]` in the route entry).

### 6.2 Task 2 — Trace the Path for Internal and Internet Traffic

```cisco
R1# traceroute 10.0.2.1
R1# traceroute 1.1.1.1
```
- `10.0.2.1` (SRV1): longest-prefix match picks the OSPF-learned `/24` over any less-specific route — this traffic crosses the R1↔R2 backbone.
- `1.1.1.1` (simulated Internet): no specific route exists for it, so IOS falls back to the default route `0.0.0.0/0` pointing at ISPBR1 — this traffic never touches R2 at all under normal conditions.

### 6.3 Task 3 — Configure the Floating Static Backup for the Server LAN

```cisco
! On R1 — floating static conf mode
conf t
ip route 10.0.2.0 255.255.255.0 203.0.113.5 120
```
- `ip route <destination> <mask> <next-hop> <AD>` (global config mode): the trailing `120` is what makes this route "float" — IOS only installs it in the routing table when nothing better (i.e., nothing with a lower AD, here OSPF's 110) is available for that destination.
- **Next hop reasoning:** `203.0.113.5` is ISPBR2's interface facing R2. This works because the ISP cloud itself carries a path back to 10.0.2.0/24 (via the reciprocal floating statics on the ISP border routers, configured in Task 6) — the backup deliberately routes around the OSPF backbone entirely, through the ISP, so it survives an outage of the direct R1↔R2 link.
- **Memory aid:** "float above the waterline only when the primary sinks" — a floating static with AD 120 stays submerged (unused) as long as OSPF's AD 110 is present; it surfaces the instant OSPF's route disappears.

```cisco
! On R2 — mirror image
conf t
ip route 10.0.1.0 255.255.255.0 203.0.113.1 120
```

### 6.4 Task 4 — Simulate Primary Link Failure

```cisco
! On R1
conf t
interface g0/2/0
 shutdown
```
Expected syslog:
```
%OSPF-5-ADJCHG: Process 1, Nbr 10.0.0.2 on GigabitEthernet0/2/0 from FULL to DOWN
```
Shutting down the backbone interface tears down the OSPF adjacency; the OSPF-learned `10.0.2.0/24` route is immediately withdrawn from the routing table.

### 6.5 Task 5 — Verify Automatic Failover

```cisco
R1# show ip route
R1# ping 10.0.2.1
```
The `O 10.0.2.0/24 [110/2] via 10.0.0.2` entry vanishes and is replaced by `S 10.0.2.0/24 [120/0] via 203.0.113.5` with zero manual intervention — IOS re-evaluates the RIB the instant the OSPF route withdraws and installs the next-best (and now only) candidate.

### 6.6 Task 6 — Floating Statics on the ISP Border Routers

```cisco
! ISPBR1 — backup path toward the server LAN, routing around R1
conf t
ip route 10.0.2.0 255.255.255.0 g0/1/0 120

! ISPBR2 — backup path toward the PC LAN, routing around R2
conf t
ip route 10.0.1.0 255.255.255.0 g0/0/0 120
```
This is the redundancy-cascades-through-every-hop principle: R1 and R2's floats depend on ISPBR1/ISPBR2 actually knowing how to reach the far-side LAN, so those routers need their own backup entries too. Without this step, R1's floating static in Task 3 would point at a next hop that itself has no idea how to reach 10.0.2.0/24, and the "backup" would silently blackhole traffic.

### 6.7 Task 7 — Restore the Primary Link

```cisco
R1(config)# interface g0/2/0
R1(config-if)# no shutdown
```
OSPF re-forms its adjacency, the `O` route at AD 110 reappears, and IOS automatically prefers it over the still-configured (but now dormant again) floating static — no cleanup required.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show ip route` | Confirms which route (OSPF vs. static) is currently installed |
| `show ip ospf neighbor` | Confirms adjacency state, catches the DOWN transition |
| `show ip protocols` | Confirms OSPF process ID and administrative distance |
| `ping` / `traceroute` | End-to-end proof the active route actually forwards traffic |
| `show logging \| include OSPF` | Timestamped adjacency change events |

### Expected Output Gallery

```text
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.0.0.2          1   FULL/DR         00:00:31    10.0.0.2        GigabitEthernet0/2/0
```

```text
R1# show ip route
     10.0.0.0/30 is subnetted, 1 subnets
C       10.0.0.0 is directly connected, GigabitEthernet0/2/0
O    10.0.2.0/24 [110/2] via 10.0.0.2, 00:12:44, GigabitEthernet0/2/0
C    10.0.1.0/24 is directly connected, GigabitEthernet0/1
S*   0.0.0.0/0 [1/0] via 203.0.113.1
```

```text
! After shutting down G0/2/0
R1# show ip route
C    10.0.1.0/24 is directly connected, GigabitEthernet0/1
S    10.0.2.0/24 [120/0] via 203.0.113.5
C    203.0.113.0/30 is directly connected, GigabitEthernet0/0/0
S*   0.0.0.0/0 [1/0] via 203.0.113.1
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Forgetting the trailing AD number** — `ip route 10.0.2.0 255.255.255.0 203.0.113.5` with no `120` installs at AD 1, instantly outranking OSPF and permanently hijacking the route even while the primary is healthy.
2. **Pointing the floating static's next hop through the very link you're testing failover on** — if the "backup" also depends on the failed interface, it can never activate.
3. **Using an exit interface instead of a next-hop IP on a multi-access segment** for a floating default route — causes excessive ARP requests and unpredictable behavior; always use a next-hop IP unless the link is point-to-point serial.
4. **Forgetting the reciprocal floating statics on upstream routers** (the ISP border routers here) — the backup path silently fails even though the local floating static looks perfectly configured.
5. **Setting AD equal to or lower than the primary's** — this doesn't create a backup, it creates a route that competes with (or replaces) the primary permanently.

---

## 9. Troubleshooting Guide

| Step | Check | Command | Likely Finding |
|---|---|---|---|
| 1 | Is the floating static even configured? | `show run \| include ip route` | Missing AD argument, or typo in next hop |
| 2 | Did it install after the primary failed? | `show ip route 10.0.2.0` | Still shows old OSPF entry — OSPF adjacency hasn't actually gone down yet |
| 3 | Is the OSPF neighbor really down? | `show ip ospf neighbor` | Neighbor still listed — check the correct interface was shut |
| 4 | Is the float's next hop reachable? | `ping <next-hop>` | Next hop unreachable — backup path itself is broken |
| 5 | Does the upstream router know the route? | `show ip route` on ISPBR1/ISPBR2 | Missing reciprocal floating static |
| 6 | End-to-end still fails? | `traceroute` | Identifies exactly which hop is blackholing |

---

## 10. Design Analysis

**Floating static vs. a second dynamic routing protocol.** A floating static is deliberately "dumb" — it doesn't monitor path quality, doesn't reroute around partial failures, and only reacts to the primary route's complete disappearance from the RIB. That's a feature here, not a limitation: enterprises that aren't ready for the operational complexity (and cost) of running BGP with two ISPs get "good enough" failover with three lines of config per router. The tradeoff: floating statics react only to routes vanishing, not to degraded-but-still-up paths (e.g., high packet loss on a link that's technically still "up"), which a protocol like EIGRP/OSPF combined with IP SLA tracking would catch.

**Why AD 120 specifically.** It's comfortably above OSPF's 110 (and EIGRP's 90/170) but well below "unreachable" (255), leaving headroom to layer additional floats at different priorities (e.g., 120 for the first backup, 130 for a third path) if a design ever needs more than one tier of redundancy.

---

## 11. Real-World Parallel

Small and mid-sized businesses on a single OSPF/EIGRP core with a primary and backup Internet circuit almost always use exactly this pattern before they're large enough to justify BGP multihoming. It's also common inside a company's own WAN — a primary MPLS circuit with a floating static backup route over a cheaper IPsec VPN link, activating automatically the moment the MPLS circuit's routing protocol adjacency drops.

---

## 12. Stretch Goal

Add IP SLA tracking (`ip sla` + `track`) to the primary default route on R1 so that instead of waiting for the *interface* to go down, the router periodically pings a reachability target and withdraws the primary route (letting the floating static take over) the moment that ping starts failing — even while the physical link stays up. This models a much more realistic "the ISP is up but broken" failure.

---

## 13. Self-Assessment Checklist

- [ ] I can state the default administrative distances for connected, static, EIGRP, and OSPF routes from memory
- [ ] I can write a floating static route with correct syntax and a sensible AD on the first try
- [ ] I can predict exactly what disappears/appears in `show ip route` before and after a link failure
- [ ] I understand why a floating static needs a reciprocal route on the far-side router to actually work
- [ ] I can explain why AD 120 rather than AD 1 or AD 200

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

OSPF and static routes race by administrative distance — OSPF default 110, static default 1. A static backup for an OSPF-learned route needs AD higher than 110, conventionally 120. When the OSPF neighbor went down, the `O` route vanished from the table in milliseconds and the AD-120 static became best path automatically, no manual intervention needed — but only because the backup path actually had a way to reach the destination. The ISP border routers needed their own floating statics too: redundancy cascades through every hop in the path, not just the enterprise edge. One trap: never configure a floating default route with an interface (rather than an IP) as next-hop on a multi-access network — it causes excessive ARP traffic.

**Skills practiced:** administrative-distance-based route selection, floating static configuration, OSPF adjacency monitoring, link-failure simulation, multi-hop redundancy design.

---

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-24/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers.
