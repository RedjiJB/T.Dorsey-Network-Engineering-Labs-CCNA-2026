# Day 25 Lab Manual — EIGRP Multi-Autonomous System, Auto-Summary, and Unequal-Cost Load Balancing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a 4-router EIGRP AS 100 partial-mesh, disable legacy auto-summary, apply correct passive-interface design, and configure unequal-cost load balancing with `variance`. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): EIGRP configuration, `no auto-summary`, passive interfaces, load balancing, metric interpretation, DUAL basics. |
| **Prerequisites** | Static routing, basic subnetting, understanding of administrative distance and metrics conceptually. |
| **Time Estimate** | 2 – 2.5 hours first attempt; 30–40 minutes on repeat. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the config is short per router, but `variance` and classful `network` statements are genuinely confusing the first time through. |

---

## 1. Lab Overview + Learning Objectives

Four routers (R1 hub, R2/R3 transit, R4 LAN edge) form a partial-mesh topology running EIGRP Autonomous System 100. R1 has two paths to R4's LAN (192.168.4.0/24) — via R2 and via R3 — with different bandwidth on each path, making this the canonical lab for understanding EIGRP's DUAL-based unequal-cost load balancing.

By the end of this lab you will be able to:

- Explain, at a teaching level, how EIGRP's DUAL algorithm picks a successor and feasible successor
- Configure EIGRP with a classful `network` statement and understand why it still works on classless subnets
- Disable auto-summary and explain why leaving it enabled breaks discontiguous networks
- Apply passive-interface design correctly to loopbacks and stub LAN interfaces
- Read and interpret the EIGRP composite metric (bandwidth + delay)
- Configure and verify `variance` for unequal-cost load balancing, and calculate traffic share ratios

---

## 2. Business Context

**Why would a real company do this?**

- **"Our network isn't one big /8 — why is EIGRP acting like it is?"** → this is exactly what auto-summary causes: two discontiguous subnets both inside 10.0.0.0/8 get silently summarized to the same classful boundary, and routers on the far side can no longer tell them apart — a real, still-occurring cause of "random" unreachability in legacy EIGRP networks. `no auto-summary` is close to a mandatory best practice in any modern deployment.
- **"We have two links to the data center — one is fiber, one is a slower backup circuit. Can we use both, not just failover?"** → unequal-cost load balancing via `variance` is precisely this: instead of a purely idle backup link, EIGRP proportionally sends more traffic over the faster path and some over the slower one, extracting value from a link that would otherwise sit unused.
- **"Every router in our WAN is chatting EIGRP hellos even to interfaces with nothing but a server on them"** → passive-interface design isn't just cosmetic; it reduces unnecessary hello traffic, prevents forming accidental EIGRP adjacencies with a device that shouldn't be a routing peer (a real security/stability concern), and keeps DUAL from re-running computations tied to interfaces that will never have a neighbor.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-25-Lab-EIGRP-Configuration.png" alt="Day 25 EIGRP Lab" width="900">
</p>

```text
              R1 (hub)
             /        \
           R2          R3
             \        /
              R4 (LAN edge) -- SW1 -- PC1
```

| Device | Model | Interfaces | Role |
|---|---|---|---|
| R1 | 2911 | G0/0 (to R2), F1/0 (to R3), Lo0 | Hub router |
| R2 | 2911 | G0/0 (to R1), F1/0 (to R4) | Transit router |
| R3 | 2911 | F1/0 (to R1), F2/0 (to R4) | Transit router |
| R4 | 2911 | F1/0 (to R2), F2/0 (to R3), G0/0 (LAN), Lo0 | LAN edge router |
| SW1 | 2960-24TT | G0/0 | Access switch |
| PC1 | PC | — | 192.168.4.0/24 |

---

## 4. IP Addressing Plan

| Segment | Network | Usable Range | Sizing Reason |
|---|---|---|---|
| R1–R2 | 10.0.12.0 /30 | .1 – .2 | Point-to-point, always 2 hosts |
| R1–R3 | 10.0.13.0 /30 | .1 – .2 | Point-to-point |
| R2–R4 | 10.0.24.0 /30 | .1 – .2 | Point-to-point |
| R3–R4 | 10.0.34.0 /30 | .1 – .2 | Point-to-point |
| R4 LAN | 192.168.4.0 /24 | .1 – .254 | User segment, room for growth |
| Loopbacks | 1.1.1.1, 2.2.2.2, 3.3.3.3, 4.4.4.4 /32 | single address each | A loopback represents exactly one router-id-style address, never more |

### 4.1 Manual Calculation — Transit Links

**Step 1:** every R1–R2/R1–R3/R2–R4/R3–R4 link needs exactly 2 usable hosts (point-to-point).

**Step 2:**
```text
2^h − 2 ≥ 2  →  h = 2  →  prefix = /30
```

**Step 3 — mask derivation:**
```text
/30 = 11111111.11111111.11111111.11111100 = 255.255.255.252
```

**Step 4 — worked example for 10.0.12.0/30:**
```text
Network:   10.0.12.0
First:     10.0.12.1  (R1)
Last:      10.0.12.2  (R2)
Broadcast: 10.0.12.3
```

**Block-size shortcut:** block size = 4, so the four transit /30s land cleanly at .12.0, .13.0, .24.0, .34.0 within the 10.0.0.0/8 space — deliberately scattered octets to make clear that EIGRP's classful `network 10.0.0.0` statement in Task 2 will match *all* of them at once, regardless of the third octet.

### 4.2 Loopback Addressing Note

Each loopback uses a /32 mask — "all bits are network bits, zero host bits" — because a loopback interface represents a single logical endpoint (commonly used as a router ID or a stable interface for management/testing), never a broadcast domain with multiple hosts.

---

## 5. Pre-Configuration Checklist

- [ ] Physical/serial interface types and numbers match your actual platform (this manual uses `Gi0/0`/`Fa1/0` naming from the original 2911 lab; adjust to your gear).
- [ ] Every interface has `no shutdown` applied — EIGRP won't form an adjacency over a down interface no matter how correct the config is.
- [ ] Loopback addresses assigned before enabling EIGRP so `network 10.0.0.0` picks them up in the same pass (loopbacks here are not in the 10.0.0.0/8 range, so note they need their own `network` statement or fall under a wildcard — see Task 2).
- [ ] Decide passive interfaces *before* enabling EIGRP: any interface facing a stub LAN or a loopback should be passive from the first `no auto-summary` commit, not bolted on afterward.

---

## 6. Configuration Tasks

### 6.1 Task 1 — Base IP Addressing

```cisco
! R1
hostname R1
interface g0/0
 ip address 10.0.12.1 255.255.255.252
 no shutdown
interface f1/0
 ip address 10.0.13.1 255.255.255.252
 no shutdown
interface loopback0
 ip address 1.1.1.1 255.255.255.255
 no shutdown
```
- `interface loopback0` (global config mode): creates a virtual interface that never goes physically down — used here as a stable router identifier, common in real EIGRP/OSPF/BGP deployments for router-id stability regardless of physical link flaps.

Repeat analogous addressing on R2 (10.0.12.2, 10.0.24.1, Lo0 2.2.2.2), R3 (10.0.13.2, 10.0.34.1, Lo0 3.3.3.3), and R4 (10.0.24.254, 10.0.34.2, 192.168.4.254/24, Lo0 4.4.4.4).

### 6.2 Task 2 — Enable EIGRP AS 100, Disable Auto-Summary, Set Passive Interfaces

```cisco
! R1
router eigrp 100
 no auto-summary
 network 10.0.0.0
 passive-interface loopback0
```
- `router eigrp 100` (global config mode): enables the EIGRP process for **Autonomous System 100** — this number must match on every router that should peer; it's a local-significance tag, not tied to any real-world AS registry.
- `network 10.0.0.0` (router config mode): EIGRP's `network` command uses a **classful** match by default when no wildcard mask is given — `10.0.0.0` covers the entire 10.0.0.0/8 range, so it silently enables EIGRP on every interface whose IP falls anywhere in 10.x.x.x, regardless of the actual subnet mask configured on that interface. **Memory aid:** "the network statement doesn't set the mask on the wire, it only decides which interfaces EIGRP looks at."
- `no auto-summary` (router config mode): disables automatic summarization to classful boundaries at every EIGRP autonomous-system boundary — without it, EIGRP would advertise `10.0.0.0/8` instead of the real /30 and /24 subnets, which breaks routing the instant two routers own discontiguous pieces of the same classful network (a very common real-world trap).
- `passive-interface loopback0` (router config mode): suppresses EIGRP hello packets on Loopback0 while still advertising the loopback's own /32 into the topology — loopbacks never have a neighbor on the other end, so sending hellos there is pure waste.

On R4, also mark the LAN-facing interface passive since no EIGRP neighbor is expected on the PC segment:
```cisco
! R4
router eigrp 100
 no auto-summary
 network 10.0.0.0
 passive-interface loopback0
 passive-interface gigabitEthernet0/0
```

**Note on `network 192.168.4.0`:** R4's LAN is outside 10.0.0.0/8, so it needs its own `network` statement (`network 192.168.4.0`) alongside `network 10.0.0.0` for EIGRP to advertise that subnet at all — `network 10.0.0.0` only ever matches 10.x.x.x interfaces.

### 6.3 Task 3 — Verify Adjacencies and Routing Tables

```cisco
R1# show ip eigrp neighbors
R4# show ip route
```
On R1, expect **two equal-cost** entries for 192.168.4.0/24 — one via R2, one via R3 — both showing the identical composite metric, because both transit paths were built with identical bandwidth/delay in this topology.

### 6.4 Task 4 — Unequal-Cost Load Balancing with `variance`

```cisco
R1(config)# router eigrp 100
R1(config-router)# variance 2
```
- `variance <multiplier>` (router config mode): by default EIGRP's "variance" is implicitly 1, meaning only paths tied for the exact best metric are installed (pure equal-cost load balancing). `variance 2` tells EIGRP to also install any **feasible successor** whose metric is at most 2× the best successor's metric — this is what unlocks a genuinely slower second path for active use instead of leaving it as a cold standby.
- **DUAL feasibility condition, taught simply:** a feasible successor must have a reported distance (its own metric to the destination, from the neighbor's perspective) lower than the current successor's *full* metric — this guarantees the alternate path can never be part of a routing loop back through the router itself. `variance` only widens *which* feasible successors get installed into the routing table for load-sharing; it never bypasses the loop-safety feasibility check itself.
- **Traffic share calculation:** IOS distributes traffic in inverse proportion to each path's metric, rounded to a `traffic share count`. If the best path's metric is 2,681,856 and the alternate's is 5,363,712 (exactly double), the traffic share count comes out 2:1 — the better path gets roughly two-thirds of the flows, the worse path about one-third.
- **Memory aid:** "variance is a dial, not a switch" — `variance 1` (default) = only the best path; higher values progressively admit worse (but still loop-safe) paths, always weighted so the better path still carries more.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show ip eigrp neighbors` | Confirms adjacency formed, holds SRTT/RTO/queue counters |
| `show ip protocols` | Confirms AS number, auto-summary state, passive interfaces, network statements |
| `show ip eigrp topology` | Shows successors and feasible successors per destination |
| `show ip route` | Confirms `D` (EIGRP) routes and which are installed |
| `show ip route 192.168.4.0` | Detailed metric and traffic-share-count breakdown |

### Expected Output Gallery

```text
R1# show ip eigrp neighbors
H   Address          Interface       Hold   Uptime   SRTT   RTO  Q  Seq
0   10.0.12.2        Gi0/0            12    00:01:23   10    50  0  3
1   10.0.13.2        Fa1/0            14    00:01:21   12    60  0  2
```

```text
R1# show ip protocols
Routing Protocol is "eigrp 100"
  Automatic network summarization is not in effect
  Maximum path: 4
  Routing for Networks:
    10.0.0.0
  Passive Interface(s):
    Loopback0
```

```text
R1# show ip route 192.168.4.0
Routing entry for 192.168.4.0/24
  Known via "eigrp 100", distance 90, metric 2681856
  Maximum path variance: 2
  Routing Descriptor Blocks:
  * 10.0.12.2, from 10.0.12.2, via GigabitEthernet0/0
      Route metric 2681856, traffic share count 2
  10.0.13.2, from 10.0.13.2, via FastEthernet1/0
      Route metric 5363712, traffic share count 1
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Leaving auto-summary enabled** — the single most common EIGRP config error; always issue `no auto-summary` as one of the first lines of router config mode.
2. **Assuming `network 10.0.0.0` needs a wildcard mask like OSPF** — without one, EIGRP treats it as a classful match; adding a wrong wildcard (e.g., `255.255.255.255`) doesn't behave the way beginners expect and can under- or over-match interfaces.
3. **Forgetting a `network` statement for a subnet outside the classful block already covered** (e.g., R4's 192.168.4.0/24 needs its own line — `network 10.0.0.0` never touches it).
4. **Configuring `variance` without checking `show ip route` first** — if the alternate path's metric is *more* than the variance multiplier times the best metric, it still won't install; `variance 2` doesn't guarantee a second path appears, it only raises the ceiling.
5. **Not marking LAN/loopback interfaces passive** — leaving them active risks forming an unintended adjacency (e.g., to a rogue device on the LAN) and wastes hello bandwidth.

---

## 9. Troubleshooting Guide

| Step | Check | Command | Likely Finding |
|---|---|---|---|
| 1 | Are interfaces up? | `show ip interface brief` | An interface is administratively down |
| 2 | Do neighbors form? | `show ip eigrp neighbors` | Missing neighbor — mismatched AS number, or K-values mismatch |
| 3 | Right networks advertised? | `show ip protocols` | Auto-summary still enabled, or missing `network` line |
| 4 | Routes present but not both? | `show ip eigrp topology` | Second path isn't a feasible successor at all — check the reported distance |
| 5 | Second path still not installed after variance? | `show ip route <prefix>` | Alternate metric exceeds variance × best metric — raise variance or check for a metric miscalculation (bandwidth/delay misconfigured on that link) |
| 6 | Unexpected adjacency to unrelated device? | `show ip eigrp neighbors` | Forgot to mark a LAN interface passive |

---

## 10. Design Analysis

**EIGRP vs. OSPF for this topology.** EIGRP was chosen here because its per-route metric (bandwidth + delay composite) directly supports proportional unequal-cost load balancing via `variance` — something OSPF's cost-based SPF simply doesn't offer without additional mechanisms (like policy routing). Where OSPF strictly picks the single lowest-cost path (or ties), EIGRP's DUAL algorithm can maintain and actively use multiple loop-safe paths of different quality simultaneously. The tradeoff: EIGRP's classful defaults (auto-summary, classful `network` matching) are legacy baggage that OSPF doesn't carry, which is part of why OSPF has become the more common enterprise IGP choice overall — EIGRP earns its keep specifically in unequal-cost multi-path scenarios like this one.

**Why passive-interface rather than simply omitting the `network` statement for the LAN.** Omitting the `network` line entirely for R4's LAN would stop EIGRP from advertising 192.168.4.0/24 at all — the LAN would become unreachable from the rest of the topology. `passive-interface` gets the best of both: the subnet is still advertised (because it's still covered by a `network` statement), but no hello packets are sent out that interface and no adjacency can form there.

---

## 11. Real-World Parallel

Enterprises with a primary MPLS/fiber WAN link and a secondary, slower backup circuit (DSL, LTE failover, or a cheaper regional carrier) use `variance` to actually use the backup link for a portion of traffic instead of leaving it idle until failure — squeezing value out of a circuit the company is already paying for. Passive-interface design shows up in literally every production EIGRP deployment, on every loopback and every access-layer LAN interface.

---

## 12. Stretch Goal

Change R3's link bandwidth (`bandwidth <kbps>` on the interface) so the R1→R3→R4 path's metric becomes *more* than double R1→R2→R4's metric, then re-check `show ip route 192.168.4.0` and confirm the second path drops out of the routing table even with `variance 2` still configured — proving variance is a ceiling, not a guarantee.

---

## 13. Self-Assessment Checklist

- [ ] I can explain why `network 10.0.0.0` matches subnets with masks other than /8
- [ ] I can state, from memory, why `no auto-summary` is close to mandatory in modern EIGRP deployments
- [ ] I correctly identify which interfaces should be passive and why, without prompting
- [ ] I can calculate a traffic-share-count ratio given two path metrics and a variance value
- [ ] I understand the feasibility condition well enough to explain why `variance` can't cause a routing loop

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

`network 10.0.0.0` is correct for EIGRP because it matches the class A boundary — it doesn't take a wildcard mask the way OSPF does. Auto-summary being enabled by default is legacy behavior; every modern EIGRP config should start with `no auto-summary`, and disabling it after neighbors already formed triggers a visible resync (`%DUAL-5-NBRCHANGE...summary configured`). Passive interfaces on loopbacks and stub LANs are close to mandatory — no traffic is lost (the subnet is still advertised), only unnecessary hello traffic and useless DUAL computation are avoided. Variance is the EIGRP feature most engineers forget exists: equal-cost load balancing is the default, unequal-cost requires `variance`, and traffic share count reflects the metric ratio between the successor and feasible successor.

**Skills practiced:** multi-router EIGRP configuration, classful `network` statement reasoning, auto-summary troubleshooting, passive-interface design, DUAL feasible-successor concepts, `variance`-based unequal-cost load balancing.

---

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-25/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers.
