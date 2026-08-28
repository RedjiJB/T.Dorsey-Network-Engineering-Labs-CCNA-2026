# Day 27 Lab Manual — OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Fix OSPF's broken default cost calculation on modern high-speed links by tuning reference bandwidth, and study the OSPF Hello packet's fields and timers at a byte level. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): OSPF cost calculation, `auto-cost reference-bandwidth`, Hello/Dead intervals, DR/BDR election basics, ASBR default-route injection (reinforced from Day 26). |
| **Prerequisites** | Day 26 (OSPF single-area, passive interfaces, ASBR) — this lab builds directly on that topology and adds cost tuning plus protocol internals. |
| **Time Estimate** | 1.5 – 2 hours first attempt; 20–30 minutes on repeat. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the config is one line per router, but the *why* behind reference bandwidth is a frequently-misunderstood, frequently-tested concept. |

---

## 1. Lab Overview + Learning Objectives

Same four-router-plus-ASBR topology as Day 26, but this lab's focus shifts to **OSPF cost math**. By default, OSPF calculates interface cost as `reference bandwidth ÷ interface bandwidth`, with a reference bandwidth of 100 Mbps that hasn't changed since OSPF's 1991 origins. On any interface 100 Mbps or faster, that formula produces cost 1 for everything — Gigabit and 10-Gigabit links become indistinguishable to OSPF's path-selection math. This lab fixes that by raising the reference bandwidth domain-wide, then inspects the OSPF Hello packet itself to understand exactly what's inside the messages that build and maintain every adjacency in this course.

By the end of this lab you will be able to:

- Explain why OSPF's default reference bandwidth is effectively broken on any modern network
- Calculate OSPF interface cost by hand for any bandwidth and any reference-bandwidth value
- Configure `auto-cost reference-bandwidth` consistently across an OSPF domain and explain why inconsistency is dangerous
- Identify every field in an OSPF Hello packet and state its purpose
- State the default Hello/Dead interval values for broadcast and non-broadcast network types
- Reconfirm ASBR default-route injection from Day 26 in a topology with corrected costs

---

## 2. Business Context

**Why would a real company do this?**

- **"Our OSPF core is Gigabit and 10-Gig everywhere — why does traffic sometimes take a weird path?"** → the default 100 Mbps reference bandwidth caps out at cost 1 for anything 100 Mbps or faster, meaning OSPF literally cannot tell a 1G link from a 10G link from a 100G link — it's guaranteed to sometimes prefer a slower path purely because the math ran out of resolution. Any network with links faster than Fast Ethernet needs this fixed on day one.
- **"A new engineer changed the reference bandwidth on one router during a maintenance window and now routing looks wrong"** → this is exactly the scenario IOS's own warning message is trying to prevent (`Please ensure reference bandwidth is consistent across all routers`) — a domain-wide mismatch produces inconsistent cost calculations for the *same physical link* depending on which end you check, which can silently create suboptimal or asymmetric routing.
- **"Our NOC needs to explain, precisely, why an OSPF adjacency dropped"** → understanding the Hello/Dead interval relationship (Dead = 4× Hello by default) is the difference between correctly diagnosing "we missed four hellos in a row, here's why" versus guessing.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-27-Lab-OSPF-(Part%202).png" alt="Day 27 OSPF Reference Bandwidth Lab" width="900">
</p>

```text
ISP -- R1 (ASBR)
           /   \
         R2     R3
           \   /
            R4 -- SW1 -- PC1
```

Same device roles and interfaces as Day 26: R1 (ASBR, ISP-facing), R2/R3 (internal transit), R4 (LAN edge). See Day 26's manual for the full equipment table — this lab reuses that exact topology.

---

## 4. IP Addressing Plan

Identical addressing to Day 26 (see that manual's section 4 for the full derivation): 203.0.113.0/30 (ISP), 10.0.12.0/30, 10.0.13.0/30, 10.0.24.0/30, 10.0.34.0/30 (transit links), 192.168.4.0/24 (LAN), and four /32 loopbacks. This lab adds no new subnets — the addressing plan is reused unchanged so the focus stays entirely on cost calculation and protocol internals.

### 4.1 The Cost Calculation "Addressing" — OSPF Cost Math By Hand

This is the numeric derivation this lab actually centers on:

**Formula:**
```text
OSPF Cost = Reference Bandwidth (Mbps) ÷ Interface Bandwidth (Mbps)
```

**Step 1 — see the default formula break down.** Default reference bandwidth = 100 Mbps.
```text
FastEthernet (100 Mbps):     100 / 100 = 1
GigabitEthernet (1000 Mbps): 100 / 1000 = 0.1 → rounds up to 1 (OSPF cost is always a whole number ≥ 1)
```
Both interfaces get cost **1** — OSPF cannot distinguish a 10x bandwidth difference. This is the "broken by default" problem.

**Step 2 — solve for the reference bandwidth that gives FastEthernet a distinguishable cost of 100:**
```text
100 = Reference Bandwidth / 100
Reference Bandwidth = 100 × 100 = 10,000 Mbps (10 Gbps)
```

**Step 3 — recompute all interface costs at reference bandwidth 10000:**
```text
FastEthernet (100 Mbps):      10000 / 100  = 100
GigabitEthernet (1000 Mbps):  10000 / 1000 = 10
Serial T1 (1.544 Mbps):       10000 / 1.544 ≈ 6477
```
Now every interface type has a distinct, meaningfully-different cost — OSPF's SPF calculation can correctly prefer the faster path when multiple routes exist.

**Memory aid:** "10000 is the FastEthernet-100 magic number" — any time you need FastEthernet to land on cost exactly 100 (a very common CCNA lab requirement), reference bandwidth 10000 is the answer, because 10000 ÷ 100 = 100.

---

## 5. Pre-Configuration Checklist

- [ ] Day 26's base topology (addressing, OSPF area 0, passive interfaces, ASBR default-route injection) is already working — this lab builds on it rather than starting from scratch.
- [ ] Decide the target reference bandwidth **once**, and plan to apply it identically on every single router in the domain in the same maintenance window — a partial rollout is the single most dangerous state this lab can produce.
- [ ] Know your interface types and physical bandwidths before predicting costs — you cannot sanity-check `show ip ospf interface` output without doing the math yourself first.

---

## 6. Configuration Tasks

### 6.1 Task 1 — Apply Consistent Reference Bandwidth Domain-Wide

```cisco
! On R1, R2, R3, and R4 — identical command, router config mode
router ospf 1
 auto-cost reference-bandwidth 10000
```
- `auto-cost reference-bandwidth <value-in-Mbps>` (router config mode): changes the denominator-independent constant used in every interface's cost calculation on this router. **This command must be applied to every router in the OSPF domain, with the identical value, in the same change window** — a router still on the old value (100) will calculate different costs for the same physical links than routers already on the new value (10000), producing internally-inconsistent LSAs.
- Expected warning on every router the moment you commit this:
```text
% OSPF: Reference bandwidth is changed.
    Please ensure reference bandwidth is consistent across all routers.
```
This is IOS actively warning you about the exact failure mode described above — it is not a bug notice, it's a checklist item.

### 6.2 Task 2 — Verify Corrected Costs

```cisco
R1# show ip ospf interface f1/0
R1# show ip ospf interface g0/0
```
Expect FastEthernet interfaces to now show `Cost: 100` and GigabitEthernet interfaces to show `Cost: 10` — confirming the formula from Section 4.1 landed correctly in the live configuration.

### 6.3 Task 3 — Reconfirm ASBR Default-Route Injection (from Day 26, now with corrected costs)

```cisco
R1(config)# router ospf 1
R1(config-router)# default-information originate
```
Same command and mechanics as Day 26 — see that manual's Task 3 for the full teaching explanation of Type-5 LSAs and ASBR status. The only difference here: verify the default route's *path selection* on R4 now correctly reflects interface-speed-aware costs rather than the old "everything is cost 1" behavior.

```cisco
R4# show ip route
```
Look specifically at the second number in each OSPF route's `[110/X]` bracket — that `X` is now a meaningful, speed-differentiated total path cost rather than a near-useless hop count.

### 6.4 Task 4 — Inspect the OSPF Hello Packet

If your platform supports packet-level simulation/capture (e.g., Packet Tracer's Simulation mode, or a packet capture tool against a live lab), locate an OSPF Hello packet and identify each field:

| Field | Typical Value | Purpose |
|---|---|---|
| Version | 2 | OSPFv2 for IPv4 |
| Type | 1 | Identifies this as a Hello packet (types 2–5 are DBD, LSR, LSU, LSAck) |
| Router ID | e.g. 1.1.1.1 | Uniquely identifies the originating router — normally the highest loopback IP |
| Area ID | 0.0.0.0 | Must match exactly on both sides of a link or the adjacency never forms |
| Auth Type | 0 (none) unless configured | Authentication method for OSPF exchanges |
| Hello Interval | 10 sec (broadcast/point-to-point), 30 sec (NBMA) | How often Hellos are sent — must match between neighbors |
| Dead Interval | 40 sec (broadcast), 120 sec (NBMA) | Time without a Hello before the neighbor is declared down — always 4× the Hello interval by convention |
| Router Priority | 0–255 (default 1) | Used in DR/BDR election on multi-access segments; 0 means "never eligible to be DR" |
| DR / BDR | IP addresses | The currently-elected Designated Router / Backup Designated Router on this segment |
| Neighbor List | list of Router IDs | Every neighbor this router has already heard from — this is what makes adjacency formation **bidirectional**: a neighbor only becomes fully adjacent once it sees its own Router ID listed in the other side's Hello |

**Teaching point — why Hello/Dead/Area must match exactly.** OSPF treats a Hello/Dead mismatch or Area ID mismatch as an immediate adjacency-blocking condition, not a warning — this is deliberate: allowing mismatched timers would mean each side has a different definition of "the neighbor is still alive," which could cause one side to declare a healthy neighbor dead while the other still thinks everything's fine.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show ip ospf interface <if>` | Confirms per-interface cost after reference-bandwidth change |
| `show ip protocols` | Confirms current reference bandwidth setting (implied via consistent cost) |
| `show ip ospf neighbor` | Confirms Hello/Dead timers didn't break existing adjacencies |
| `show ip route ospf` | Confirms path costs are now meaningfully differentiated |
| Packet capture / Simulation mode | Confirms Hello packet field values match the table above |

### Expected Output Gallery

```text
R1# show ip ospf interface f1/0
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.0.13.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 100
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```

```text
R1# show ip ospf interface g0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.0.12.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 10
```

```text
R4# show ip route
Gateway of last resort is 10.0.24.1 to network 0.0.0.0

O    10.0.12.0/30 [110/20] via 10.0.24.1, FastEthernet1/0
O    10.0.13.0/30 [110/110] via 10.0.34.1, FastEthernet2/0
O*E2 0.0.0.0/0 [110/1] via 10.0.24.1, FastEthernet1/0
             [110/1] via 10.0.34.1, FastEthernet2/0
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Changing reference bandwidth on only some routers** — the #1 mistake this lab exists to teach against; always roll out the same value everywhere in the same window.
2. **Picking an arbitrary reference bandwidth value without doing the math** — always solve backward from the cost you want a known interface type to land on (e.g., 10000 for FastEthernet = 100).
3. **Forgetting OSPF cost always rounds up to a minimum of 1** — a link fast enough to compute to less than 1 (e.g., 10 Gbps interface with reference bandwidth still at default 100) doesn't get cost 0, it gets cost 1, which re-creates the exact "everything looks the same" problem the fix is meant to solve.
4. **Assuming Hello/Dead mismatches produce a warning rather than a hard block** — IOS won't form or will drop the adjacency outright; there's no "best effort" here.
5. **Confusing administrative distance (110, constant for OSPF) with cost (the variable second number in brackets)** — these are two completely different numbers serving two completely different purposes (AD picks between routing *protocols*; cost picks between paths *within* OSPF).

---

## 9. Troubleshooting Guide

| Step | Check | Command | Likely Finding |
|---|---|---|---|
| 1 | Did the reference bandwidth actually change? | `show ip ospf interface <if>` | Cost still shows old value — command not committed, or wrong process ID |
| 2 | Consistent across the domain? | Same command on every router | One router still shows old costs for the same link — mismatch |
| 3 | Adjacency dropped after the change? | `show ip ospf neighbor` | Reference bandwidth change alone shouldn't drop adjacencies — check Hello/Dead timers instead |
| 4 | Path selection still looks wrong? | `show ip route <prefix>`, manually recompute expected cost | Miscalculated the reference bandwidth needed, or a link's actual bandwidth differs from assumption (`show interfaces` bandwidth line) |
| 5 | Adjacency won't form on a new link? | `show ip ospf interface <if>` on both ends | Hello/Dead interval mismatch, or Area ID mismatch |

---

## 10. Design Analysis

**Why 10000 and not some other round number.** 10000 is chosen specifically because it makes FastEthernet (100 Mbps) land on a clean cost of 100 — a convenient, CCNA-standard value. Real production networks often go higher (100000 or more) if the core includes 10G/40G/100G links, so that even those top-tier links remain distinguishable from each other rather than all collapsing back to cost 1 at the new ceiling. The core lesson generalizes: pick a reference bandwidth at least as large as your fastest link's actual bandwidth, ideally with headroom for future upgrades.

**Why OSPF didn't just default to something modern.** Reference bandwidth has stayed at 100 Mbps since OSPF's RFC 1131 era (1991) specifically for backward compatibility — changing the default would silently re-cost every existing OSPF deployment on earth the moment routers upgraded IOS versions, a far more dangerous outcome than requiring engineers to explicitly opt in.

---

## 11. Real-World Parallel

Any enterprise or ISP network built after roughly 2005 hits this immediately — a mixed Fast Ethernet/Gigabit/10G core is now the norm, not the exception, and every serious OSPF deployment guide treats `auto-cost reference-bandwidth` tuning as close to mandatory, not optional. NOC engineers diagnosing flapping adjacencies rely on exact Hello/Dead timer knowledge daily — "we missed 4 consecutive hellos over a saturated link" is a real, common root-cause finding.

---

## 12. Stretch Goal

Tune the Hello and Dead intervals directly on one link (`ip ospf hello-interval <sec>` / `ip ospf dead-interval <sec>`) to something faster than default (e.g., Hello 1 sec / Dead 4 sec) to get near-instant failure detection, and observe how much faster OSPF reconverges after a simulated link failure compared to the default 40-second dead timer — while confirming both ends of the link must match exactly or the adjacency drops.

---

## 13. Self-Assessment Checklist

- [ ] I can compute OSPF cost by hand for any interface bandwidth and any reference bandwidth
- [ ] I can explain, from memory, why the default reference bandwidth is considered broken on modern networks
- [ ] I know the default Hello/Dead intervals for both broadcast and NBMA network types
- [ ] I can list every major field in an OSPF Hello packet and its purpose
- [ ] I can explain why reference bandwidth inconsistency across a domain is dangerous, not merely untidy

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

The default reference bandwidth of 100 Mbps is a legacy value from 1991; any interface 100 Mbps or faster collapses to cost 1, making OSPF unable to distinguish a Gigabit link from a 10-Gigabit one. `auto-cost reference-bandwidth 10000` fixes this by giving FastEthernet cost 100 and Gigabit cost 10 — but it must be applied identically across every router in the domain, or the same physical link ends up with inconsistent costs depending which end you check, which IOS explicitly warns about. The Hello packet carries Router ID, Area ID, Hello/Dead intervals, DR/BDR information, and a neighbor list that must include the recipient's own Router ID before a two-way adjacency can form — Hello/Dead/Area mismatches hard-block adjacency formation rather than merely degrading it.

**Skills practiced:** OSPF cost calculation, reference bandwidth tuning, domain-wide consistency discipline, OSPF Hello packet field identification, Hello/Dead timer reasoning, ASBR default-route reconfirmation.

---

## 15. GNS3 Lab

This lab reuses the exact topology built in `RedjiJB-Labs/Day-26/GNS3/build_lab.py` (ISPR1, R1–R4, SW1, PC1) — no separate build script is needed. Run the Day 26 script if you haven't already, then apply this lab's `auto-cost reference-bandwidth` configuration on top of that same running topology. See `RedjiJB-Labs/Day-26/GNS3/README.md` for build instructions.
