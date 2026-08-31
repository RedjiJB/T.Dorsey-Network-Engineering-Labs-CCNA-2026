# Day 26 Lab Manual — OSPF ASBR Default Route Injection and Passive Interface Design

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a 4-router single-area OSPF domain, exclude the Internet-facing link from the OSPF process, apply correct passive-interface design, and configure R1 as an ASBR that injects a default route for the rest of the domain. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): OSPF single-area configuration, `network` statements with wildcard masks, passive interfaces, `default-information originate`, ASBR concept, E1/E2 route types. |
| **Prerequisites** | Static default routing, subnetting/wildcard masks, basic OSPF area/neighbor concepts. |
| **Time Estimate** | 2 – 2.5 hours first attempt; 30–40 minutes on repeat. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the config is routine, but understanding *why* OSPF never auto-advertises a static default route trips up almost everyone the first time. |

---

## 1. Lab Overview + Learning Objectives

Four routers (R1–R4) form a single-area (Area 0) OSPF partial mesh. R1 additionally has a link to an ISP edge router (ISPR1) carrying a static default route toward the Internet. That link is deliberately excluded from OSPF, and instead R1 is configured as an **ASBR** (Autonomous System Boundary Router) that injects the default route into OSPF so R2, R3, and R4 automatically learn "where the Internet is" without any static configuration of their own.

By the end of this lab you will be able to:

- Configure OSPF `network` statements with the correct wildcard mask for each subnet size
- Explain why loopback and Internet-facing interfaces should be passive, and configure them that way
- Explain why OSPF never automatically shares a locally-configured static default route with the rest of the domain
- Configure `default-information originate` (with and without `always`) and verify the resulting ASBR status
- Distinguish OSPF E1 vs E2 external route metrics and explain when the difference actually changes path selection
- Verify default-route propagation and equal-cost multipath behavior across a partial mesh

---

## 2. Business Context

**Why would a real company do this?**

- **"Every router configuring its own static route to the ISP is a maintenance nightmare"** → with `default-information originate`, only R1 (the router that actually touches the ISP) needs to know the ISP's address. Every other router in the OSPF domain learns "send unknown traffic toward R1" automatically and dynamically — if R1's ISP circuit changes, only one router's config needs to change.
- **"We don't want internal routers accidentally forming an adjacency with the ISP's router"** → excluding R1's Internet-facing interface from OSPF (via passive-interface, or simply never covering it with a `network` statement) prevents a misconfigured or hostile device on the ISP side from ever becoming an OSPF neighbor of R1 — a real security boundary, not just tidiness.
- **"How do downstream routers know to reach the Internet through R1 specifically, and not get confused if there's more than one path?"** → this is the equal-cost multipath scenario R4 hits at the end of the lab: R4 has two internal paths back toward R1 (via R2 and via R3), and OSPF installs the default route via *both*, load-balancing outbound Internet traffic automatically.
- **"Our design review keeps asking: is this route type 1 or type 2?"** → E1 vs E2 is a very real production question the instant a topology becomes asymmetric — the wrong choice can silently pick a suboptimal Internet exit path in a multi-ASBR design.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-26-Lab-OSPF-(Part%201).png" alt="Day 26 OSPF ASBR Lab" width="900">
</p>

```text
ISPR1 -- R1 (ASBR)
             /   \
           R2     R3
             \   /
              R4 -- SW1 -- PC1
```

| Device | Model | Interfaces | Role |
|---|---|---|---|
| ISPR1 | 2911 | G3/0 | ISP edge (outside OSPF domain) |
| R1 | 2911 | G3/0 (ISP), G0/0 (to R2), F1/0 (to R3), Lo0 | ASBR |
| R2 | 2911 | G0/0 (to R1), F1/0 (to R4), Lo0 | Internal router |
| R3 | 2911 | F1/0 (to R1), F2/0 (to R4), Lo0 | Internal router |
| R4 | 2911 | F1/0 (to R2), F2/0 (to R3), G0/0 (LAN), Lo0 | Internal router, LAN edge |
| SW1 | 2960-24TT | G0/0 | Access switch |
| PC1 | PC | — | 192.168.4.0/24 |

---

## 4. IP Addressing Plan

| Segment | Network | Usable Range | Sizing Reason |
|---|---|---|---|
| ISPR1–R1 | 203.0.113.0 /30 | .1 – .2 | Point-to-point |
| R1–R2 | 10.0.12.0 /30 | .1 – .2 | Point-to-point |
| R1–R3 | 10.0.13.0 /30 | .1 – .2 | Point-to-point |
| R2–R4 | 10.0.24.0 /30 | .1 – .2 | Point-to-point |
| R3–R4 | 10.0.34.0 /30 | .1 – .2 | Point-to-point |
| R4 LAN | 192.168.4.0 /24 | .1 – .254 | User segment |
| Loopbacks | x.x.x.x /32 each | single address | OSPF router ID stability |

### 4.1 Manual Calculation — Wildcard Masks (the OSPF-specific twist)

OSPF `network` statements use a **wildcard mask** — the inverse of a subnet mask — rather than the subnet mask itself.

**Step 1 — derive the subnet mask normally.** All transit links here are /30 (2 usable hosts): `255.255.255.252`.

**Step 2 — invert every octet (255 − each octet) to get the wildcard mask:**
```text
Subnet mask:   255 . 255 . 255 . 252
Wildcard mask: 255-255 . 255-255 . 255-255 . 255-252
             =   0    .   0    .   0    .   3
```
So a /30 subnet mask (`255.255.255.252`) becomes wildcard `0.0.0.3` in the `network` command:
```cisco
network 10.0.12.0 0.0.0.3 area 0
```

**Step 3 — same process for the /24 LAN:**
```text
Subnet mask:   255 . 255 . 255 . 0
Wildcard mask:   0 .   0 .   0 . 255
```
```cisco
network 192.168.4.0 0.0.0.255 area 0
```

**Step 4 — loopback /32 wildcard is always `0.0.0.0`** (every bit must match exactly — zero tolerance, matching the fact a /32 has zero host bits):
```cisco
network 1.1.1.1 0.0.0.0 area 0
```

**Memory aid:** subnet mask says "these bits matter, ignore the rest"; wildcard mask says "these bits can vary, the rest must match" — they're literal bitwise opposites, and CCNA candidates who mix them up end up either matching far too much or nothing at all.

---

## 5. Pre-Configuration Checklist

- [ ] Loopbacks configured with /32 masks on all four internal routers before enabling OSPF — the router ID election (highest loopback IP, or highest active interface IP if no loopback exists) happens at process startup, so configure loopbacks first for predictable router IDs.
- [ ] Decide, before typing anything, exactly which interface on R1 must **never** run OSPF (the ISP-facing G3/0) and confirm no `network` statement will accidentally cover it.
- [ ] R1 already has (or you will configure) a static default route toward ISPR1 before attempting `default-information originate` — without `always`, this command silently does nothing if no default route exists in R1's own table.
- [ ] Identify every stub interface (loopbacks, R4's LAN) that should be passive.

---

## 6. Configuration Tasks

### 6.1 Task 1 — Base Addressing (abbreviated; same pattern all four routers)

```cisco
! R1
hostname R1
interface g0/0
 ip address 10.0.12.1 255.255.255.252
 no shutdown
interface f1/0
 ip address 10.0.13.1 255.255.255.252
 no shutdown
interface g3/0
 ip address 203.0.113.1 255.255.255.252
 no shutdown
interface loopback0
 ip address 1.1.1.1 255.255.255.255
 no shutdown
```
Repeat the analogous pattern for R2 (10.0.12.2, 10.0.24.1, Lo0 2.2.2.2), R3 (10.0.13.2, 10.0.34.1, Lo0 3.3.3.3), and R4 (10.0.24.2, 10.0.34.2, 192.168.4.254/24, Lo0 4.4.4.4).

### 6.2 Task 2 — OSPF Area 0, Excluding R1's Internet Link

```cisco
! R1
router ospf 1
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.13.0 0.0.0.3 area 0
 network 1.1.1.1 0.0.0.0 area 0
 passive-interface g3/0
 passive-interface loopback0
```
- `router ospf 1` (global config mode): `1` here is the **process ID**, locally significant only — it does not need to match between routers (unlike EIGRP's AS number).
- Notice **no `network` statement covers G3/0's 203.0.113.0/30** — the Internet link is simply never included in the OSPF process at all. `passive-interface g3/0` is added anyway as defense-in-depth in case a future network engineer widens a `network` statement to accidentally cover it.
- `passive-interface loopback0`: same reasoning as EIGRP Day 25 — the /32 is still advertised via the `network 1.1.1.1 0.0.0.0` line, but no hello packets go out an interface that will never have a neighbor.

```cisco
! R2
router ospf 1
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.24.0 0.0.0.3 area 0
 network 2.2.2.2 0.0.0.0 area 0
 passive-interface loopback0

! R3
router ospf 1
 network 10.0.13.0 0.0.0.3 area 0
 network 10.0.34.0 0.0.0.3 area 0
 network 3.3.3.3 0.0.0.0 area 0
 passive-interface loopback0

! R4
router ospf 1
 network 10.0.24.0 0.0.0.3 area 0
 network 10.0.34.0 0.0.0.3 area 0
 network 192.168.4.0 0.0.0.255 area 0
 network 4.4.4.4 0.0.0.0 area 0
 passive-interface loopback0
 passive-interface g0/0
```
`passive-interface g0/0` on R4: the LAN segment has only end hosts behind SW1 — no OSPF router will ever be a neighbor there, so suppress hellos while still advertising 192.168.4.0/24 via the `network` line.

### 6.3 Task 3 — R1 as ASBR: Inject the Default Route

R1 must already have a static default route toward the ISP:
```cisco
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2
```
Then:
```cisco
R1(config)# router ospf 1
R1(config-router)# default-information originate
```
- `default-information originate` (router config mode): tells OSPF to generate a **Type-5 External LSA** for `0.0.0.0/0` and flood it into the OSPF domain — but only if R1's own routing table already contains a default route from some other source (here, the static route above). This is the single most common gotcha in this lab: the command is silent and does nothing if R1 has no default route of its own to advertise.
- **`always` variant:** `default-information originate always` forces the LSA to be generated regardless of whether R1 itself has a working default route — useful in a lab/test environment, dangerous in production if the ISP link is actually down (downstream routers would still be told "send unreachable traffic to R1," creating a black hole).
- **Memory aid:** "originate" = R1 is *creating* new routing information from outside OSPF's normal internal-link-state process — this is exactly the definition of an ASBR: a router that injects external routing information into an OSPF domain.

### 6.4 Task 4 — Optional: Control the Metric Type

```cisco
R1(config-router)# default-information originate metric 20 metric-type 1
```
- **E2 (default, no keyword needed):** the metric downstream routers see for `0.0.0.0/0` is *only* the seed metric set at R1 (default 20 if unspecified, or 1 as commonly shown in verification output) — it does **not** grow as the LSA propagates further from R1. Every router in the domain sees the exact same external cost, regardless of how many internal hops away it is.
- **E1:** the metric is the seed cost **plus** the internal OSPF cost to reach the ASBR — so a router two hops from R1 sees a higher total cost than a router one hop away. In an asymmetric topology with more than one ASBR, E1 lets OSPF correctly prefer the *closer* ASBR; E2 would tie-break arbitrarily (or worse, prefer the wrong one) because it ignores internal distance entirely.
- In this lab's symmetric partial mesh (both R2 and R3 are exactly one hop from R1), E1 and E2 happen to produce identical path preference — the difference only becomes visible in an asymmetric or multi-ASBR topology, which is exactly why it's worth understanding rather than memorizing.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show ip protocols` | Confirms networks covered, passive interfaces, process ID |
| `show ip ospf neighbor` | Confirms adjacencies with R2/R3/R4 (and confirms *no* neighbor on G3/0) |
| `show ip route ospf` | Shows `O`, `O IA`, and `O*E2` entries |
| `show ip ospf` | Confirms `It is an autonomous system boundary router` and external LSA count |
| `ping`/`traceroute` from PC1 toward a simulated Internet address | End-to-end proof of default-route propagation |

### Expected Output Gallery

```text
R1# show ip ospf
 Routing Process "ospf 1" with ID 1.1.1.1
 ...
 It is an autonomous system boundary router
 Redistributing External Routes from,
 Number of external LSA 1
```

```text
R2# show ip route
Gateway of last resort is 10.0.12.1 to network 0.0.0.0

C    2.2.2.2 is directly connected, Loopback0
C    10.0.12.0/30 is directly connected, GigabitEthernet0/0
O    10.0.13.0/30 [110/2] via 10.0.12.1, GigabitEthernet0/0
O    10.0.34.0/30 [110/2] via 10.0.12.1, GigabitEthernet0/0
C    10.0.24.0/30 is directly connected, FastEthernet1/0
O*E2 0.0.0.0/0 [110/1] via 10.0.12.1, GigabitEthernet0/0
```

```text
R4# show ip route
Gateway of last resort is 10.0.24.1 to network 0.0.0.0
...
O*E2 0.0.0.0/0 [110/1] via 10.0.24.1, FastEthernet1/0
             [110/1] via 10.0.34.1, FastEthernet2/0
```
R4 shows the default route via **two equal-cost paths** — through R2 and through R3 — because both are exactly one OSPF hop from R1 with identical cost. This is OSPF's built-in equal-cost multipath (ECMP), no extra configuration required.

---

## 8. Common Mistakes (80/20 Rule)

1. **Running `default-information originate` before R1 has an actual default route** — the command silently succeeds and does nothing; downstream routers see no `O*E2` entry at all.
2. **Confusing subnet mask and wildcard mask** in a `network` statement — inverting the wrong way either matches nothing (adjacency never forms) or matches far more than intended.
3. **Forgetting to exclude R1's ISP-facing interface** — if a broad `network` statement accidentally covers it, R1 may attempt to form an OSPF adjacency with the ISP's router, which is both unnecessary and a security exposure.
4. **Assuming `default-information originate always` is always the safer choice** — it removes the safety check that ties the advertisement to a real, working default route, risking a black hole if the ISP link fails.
5. **Not realizing loopback `network` statements need wildcard `0.0.0.0`** — using a /30-style wildcard on a /32 loopback either fails to match or (worse) accidentally matches unintended addresses.

---

## 9. Troubleshooting Guide

| Step | Check | Command | Likely Finding |
|---|---|---|---|
| 1 | Are internal adjacencies up? | `show ip ospf neighbor` | Missing neighbor — wildcard mask error, or area mismatch |
| 2 | Is R1 truly excluded from advertising OSPF on G3/0? | `show ip ospf interface brief` | G3/0 listed as an OSPF interface — remove/narrow the covering `network` statement |
| 3 | Does R1 have a default route to redistribute? | `show ip route static` on R1 | No static default route present — `default-information originate` has nothing to advertise |
| 4 | Is R1 recognized as ASBR? | `show ip ospf` | "It is an autonomous system boundary router" missing — re-check `default-information originate` was actually committed |
| 5 | Downstream router missing the default route? | `show ip route ospf` | No `O*E2` line — LSA not flooding, check adjacency state first |
| 6 | Wrong exit path chosen in asymmetric topology? | `show ip route 0.0.0.0` | E2 metric ignoring internal distance — consider `metric-type 1` |

---

## 10. Design Analysis

**Why inject a default route instead of redistributing full BGP/ISP routing tables into OSPF.** A full Internet routing table has hundreds of thousands of entries — flooding that into an internal OSPF domain would overwhelm every router's LSDB and CPU for zero practical benefit, since internal routers only ever need to know "send anything unrecognized toward the ASBR." A single default route accomplishes exactly that with one LSA.

**Why passive-interface rather than simply never writing a `network` statement for the ISP link.** Both approaches stop OSPF from forming an adjacency there, but `passive-interface` is the more defensive, explicit choice: it documents clear intent ("this interface deliberately does not participate") and continues to protect the design even if someone later widens a `network` statement in a way that would otherwise have accidentally covered the link.

**E1 vs. E2 — why E2 is the default and when to override it.** E2 is simpler to reason about in small, symmetric labs (as this one demonstrates — the choice doesn't even change behavior here), which is likely why Cisco made it the default. The instant a design has more than one ASBR at different distances from various internal routers, E1 becomes the correct choice so OSPF's path selection accounts for real internal cost rather than treating every ASBR's advertisement as equally "close."

---

## 11. Real-World Parallel

Any enterprise with a single OSPF-routed campus and one (or two) Internet-facing edge routers uses exactly this pattern — `default-information originate` at the edge, internal routers carrying zero static configuration for reaching the Internet. Multi-ASBR designs (dual data-center Internet exits) are where the E1/metric-type conversation becomes a real design decision rather than a trivia question.

---

## 12. Stretch Goal

Add a second ASBR (e.g., configure R4 with its own simulated ISP link and static default route, then `default-information originate` there too) and switch both ASBRs to `metric-type 1`. Watch how routers closer to one ASBR than the other now correctly prefer the nearer exit, and compare against what happens if you revert to E2.

---

## 13. Self-Assessment Checklist

- [ ] I can convert any subnet mask to its OSPF wildcard mask by hand, without a calculator
- [ ] I can explain, unprompted, why `default-information originate` can silently do nothing
- [ ] I correctly identify which interfaces should be excluded from OSPF and why
- [ ] I can explain the practical difference between E1 and E2 in a topology where it actually matters
- [ ] I can read `show ip ospf` and identify ASBR status and external LSA count

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

OSPF doesn't automatically advertise a locally-configured static default route to other routers — you must explicitly issue `default-information originate`. Doing so generates a Type-5 External LSA that floods area 0, and downstream routers install it as `O*E2 0.0.0.0/0`. `show ip ospf` confirms ASBR status directly: "It is an autonomous system boundary router." The E2 metric doesn't accumulate internal OSPF cost as it propagates — in a symmetric mesh this doesn't matter, but in an asymmetric one it can produce suboptimal path selection, which is what `metric-type 1` (E1) fixes. Passive interfaces are required on loopbacks and LAN edges — no adjacency is lost since the subnet is still advertised via the `network` statement, only unnecessary hello traffic and adjacency risk are removed.

**Skills practiced:** OSPF single-area configuration, wildcard mask derivation, passive-interface design, ASBR configuration, default-route redistribution, E1/E2 metric reasoning, ECMP verification.

---

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-26/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers.
