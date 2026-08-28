# Day 28 Lab Manual — OSPF Troubleshooting: Serial Links, Neighbor Failures, and Missing Routes

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Diagnose and repair a pre-configured 5-router OSPF network containing five deliberate, realistic misconfigurations, using a structured decision tree rather than a rebuild-from-scratch approach. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): OSPF troubleshooting, serial DCE/DTE clocking, area mismatches, passive interfaces, default-route/ASBR verification, LSDB inspection (Type-1/2/5 LSAs). |
| **Prerequisites** | Days 26–27 (OSPF single-area, passive interfaces, ASBR, reference bandwidth) — this lab assumes solid OSPF fundamentals and tests diagnosis speed, not new configuration concepts. |
| **Time Estimate** | 2 – 3 hours first attempt (troubleshooting is inherently slower than building); 30–45 minutes once the decision tree is internalized. |
| **Difficulty** | ⭐⭐⭐⭐☆ (Intermediate-Advanced) — nothing here is conceptually new, but diagnosing *silent* failures (no error message, just "it doesn't work") under time pressure is the actual skill being tested. |

---

## 1. Lab Overview + Learning Objectives

A 5-router OSPF network (R1–R5) has been pre-configured and handed to you with **five specific, realistic problems**: a newly-added serial link that won't come up, a LAN subnet missing from one router's neighbors' routing tables, a multi-access segment where two routers refuse to peer with a third, no Internet reachability from either PC, and a request to audit the Link-State Database directly to confirm the domain's health. This is deliberately the most "real job" lab in the series — you inherit broken networks far more often than you build clean ones.

By the end of this lab you will be able to:

- Diagnose a serial link that's administratively up but won't pass OSPF traffic (DCE/DTE clocking)
- Diagnose a missing route by tracing backward from "no route" to "wrong or missing `network` statement"
- Diagnose a silent neighbor-formation failure across a multi-access (switched) segment
- Diagnose missing Internet reachability by checking both halves of default-route injection (static route + `default-information originate`)
- Read `show ip ospf database` and correctly categorize Type-1, Type-2, and Type-5 LSAs
- Apply a structured, repeatable troubleshooting decision tree instead of guessing

---

## 2. Business Context

**Why would a real company do this?**

- **"The last engineer left no documentation and now something's broken"** → this is the single most common real-world scenario new hires face. You will spend far more of your career fixing other people's networks than building greenfield ones, and the skill that matters is systematic diagnosis, not memorized "correct" configs.
- **"A new site's WAN link went in yesterday and users there report no connectivity"** → the serial DCE/DTE clocking issue in Task 1 is a genuinely common Day-1 problem when a new circuit is provisioned — the physical link looks "up" in casual inspection but never actually passes control-plane traffic.
- **"One office can reach everything except the branch across town"** → the missing-route scenario in Task 2 mirrors a shockingly common real incident: someone edits a router's OSPF config, narrows or drops a `network` statement by accident, and an entire subnet silently disappears from the rest of the company's routing tables with zero alarms.
- **"Support says three sites should all see each other over the shared switch but only two do"** → the multi-access neighbor-formation failure in Task 3 is exactly how area-ID and passive-interface misconfigurations manifest on a real switched segment — silently, with no obvious error.
- **"Auditors want proof the routing domain is healthy, not just 'it seems to work'"** → Task 5's LSDB inspection is the closest thing to a network health certificate available at the CLI — counting LSA types tells you exactly how many routers, multi-access segments, and external routes exist, independent of what any individual routing table shows.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-28-Lab-OSPF-(Part%203).png" alt="Day 28 OSPF Troubleshooting Lab" width="900">
</p>

```text
PC1 -- SW1 -- R1 ===Serial=== R2 --+
                |                   \
             (to R5, serial)         SW3 (multi-access) -- R4 -- SW2 -- PC2 -- R3
                |                   /                              |
               R5 ------------------                              R3
```

| Device | Model | Interfaces | Role |
|---|---|---|---|
| R1 | 2911 | G0/0 (LAN), S0/0/0 (to R2), S0/0/1 (to R5), Lo0 | Edge/LAN router |
| R2 | 2911 | S0/0/0 (to R1), G0/0 (to SW3), G0/1 (to R3), Lo0 | Transit router |
| R3 | 2911 | G0/0 (LAN), G0/1 (to R4), Lo0 | LAN router |
| R4 | 2911 | G0/0 (to SW3), G0/1 (to R3), Lo0 | Transit router |
| R5 | 2911 | G0/0 (to SW3), S0/0/0 (to R1), Lo0 | ASBR, ISP-facing |
| SW1, SW2 | 2960-24TT | G0/0 | Access switches for PC1/PC2 |
| SW3 | 2960-24TT | G0/0-2 | Multi-access segment joining R2, R4, R5 |
| PC1 | PC | — | 10.0.1.0/24 |
| PC2 | PC | — | 10.0.2.0/24 |
| ISP | Cloud | — | represents 8.8.8.8, external reachability target |

---

## 4. IP Addressing Plan

| Segment | Network | Usable Range | Sizing Reason |
|---|---|---|---|
| PC1 LAN | 10.0.1.0 /24 | .1 – .254 | User segment |
| PC2 LAN | 10.0.2.0 /24 | .1 – .254 | User segment |
| R1–R2 serial | 192.168.12.0 /30 | .1 – .2 | Point-to-point |
| R3–R4 serial | 192.168.34.0 /30 | .1 – .2 | Point-to-point |
| SW3 multi-access (R2, R4, R5) | 192.168.245.0 /29 | .1 – .6 | Exactly 3 routers today, sized with headroom for a 4th |
| R1–R5 / R5–ISP | 203.0.113.0 /30 | .1 – .2 | Point-to-point |

### 4.1 Manual Calculation — the SW3 Multi-Access Segment (/29)

This is the one non-trivial subnet size in this lab — worth deriving carefully.

**Step 1 — hosts needed.** Three routers (R2, R4, R5) sit on this shared segment today, with reasonable headroom for a fourth in the near future: 4 hosts to plan for.

**Step 2 — solve for host bits:**
```text
2^h − 2 ≥ 4
2^2 − 2 = 2   too small
2^3 − 2 = 6   fits with headroom
```
`h = 3` → prefix = 32 − 3 = **/29**.

**Step 3 — mask derivation:**
```text
/29 = 11111111.11111111.11111111.11111000 = 255.255.255.248
```

**Step 4 — network/host/broadcast for 192.168.245.0/29:**
```text
Network:    192.168.245.0
First host: 192.168.245.1  (R2)
...
Last host:  192.168.245.6
Broadcast:  192.168.245.7
```
R2, R4, and R5 occupy three of the six usable addresses, leaving three spare — enough for one more router or a management host without renumbering.

**OSPF wildcard for this /29:** invert the mask octet-by-octet: `255.255.255.248` → `0.0.0.7`, giving `network 192.168.245.0 0.0.0.7 area 0`.

---

## 5. Pre-Configuration Checklist

- [ ] Resist the urge to `no router ospf 1` and rebuild — this lab is explicitly a diagnose-and-repair exercise; wiping the config defeats the entire point and the lesson.
- [ ] Start every unfamiliar router with `show running-config | section router ospf` and `show ip interface brief` before touching anything — build a mental map of current state first.
- [ ] Keep the troubleshooting decision tree (Section 9) open and actually follow it in order rather than jumping to guesses — the discipline of ruling out layers systematically is the actual skill being graded here, in a real job as much as in this lab.

---

## 6. Configuration Tasks (Diagnose-Then-Fix Format)

### 6.1 Task 1 — New R1↔R2 Serial Link Won't Come Up

**Symptom:** the newly-cabled S0/0/0 link between R1 and R2 shows as administratively up in config but no OSPF adjacency ever forms.

**Diagnosis:**
```cisco
R1# show ip interface brief
R2# show ip interface brief
```
Both interfaces may show `up/down` (line protocol down) — a classic serial-link symptom.

**Root cause:** on a back-to-back (non-provider) serial link in a lab environment, one end must act as **DCE** (Data Communications Equipment) and supply clocking via `clock rate`; the other acts as **DTE** (Data Terminal Equipment) and simply uses the clock it's given. Without a clock rate configured on the DCE end, the line protocol never comes up, and OSPF — which requires a fully up/up interface before it will even attempt to send a Hello — never gets a chance to negotiate anything.

**Fix:**
```cisco
! R1 -- the DCE side (identify with "show controllers serial 0/0/0")
interface s0/0/0
 ip address 192.168.12.1 255.255.255.252
 clock rate 128000
 no shutdown

! R2 -- the DTE side, no clock rate needed
interface s0/0/0
 ip address 192.168.12.2 255.255.255.252
 no shutdown
```
- `clock rate 128000` (interface config mode, DCE side only): sets the line clock in bits per second — this is a **lab-only** command; in production, the provider's CSU/DSU supplies clocking and this command is never needed on customer equipment. **Memory aid:** "DCE Controls the Clock" — same first letter, easy to remember which side needs the command.
- Add OSPF `network` statements to cover the new link on both routers if not already present:
```cisco
! R1
router ospf 1
 network 192.168.12.0 0.0.0.3 area 0

! R2
router ospf 1
 network 192.168.12.0 0.0.0.3 area 0
```

### 6.2 Task 2 — Only R3 Has a Route to 10.0.2.0/24

**Symptom:** R3's own LAN (10.0.2.0/24) is invisible to every other router in the domain.

**Diagnosis:**
```cisco
R2# show ip route 10.0.2.0
R3# show ip protocols
```
`show ip protocols` on R3 reveals which networks are actually covered by a `network` statement — if 10.0.2.0/24 isn't listed under "Routing for Networks," OSPF was never told to advertise it, regardless of whether the interface is physically fine.

**Root cause:** R3's LAN-facing interface was never included in an OSPF `network` statement — either missing entirely, or present with a wildcard mask that doesn't actually match the interface's IP.

**Fix:**
```cisco
R3(config)# router ospf 1
R3(config-router)# network 10.0.2.0 0.0.0.255 area 0
```

### 6.3 Task 3 — R2 and R4 Won't Peer with R5 Across SW3

**Symptom:** three routers (R2, R4, R5) sit on the same Layer 2 switched segment (SW3) and should all form OSPF adjacencies with each other, but R5 shows no neighbors.

**Diagnosis:**
```cisco
R2# show ip ospf neighbor
R4# show ip ospf neighbor
R5# show ip ospf interface g0/0
```
Check each router's OSPF-enabled interface list and **Area ID** for the SW3-facing interface specifically.

**Root cause:** an **Area ID mismatch** is the single most common reason for a completely silent neighbor-formation failure on a shared segment — unlike a Hello/Dead timer mismatch (which at least tries and logs something), a wrong area on even one side simply means that router never considers the others eligible neighbors at all, with no error message. Verify every router's `network` statement covering 192.168.245.0/29 explicitly says `area 0`.

**Fix:**
```cisco
! Confirm identical area 0 on all three
R2(config-router)# network 192.168.245.0 0.0.0.7 area 0
R4(config-router)# network 192.168.245.0 0.0.0.7 area 0
R5(config-router)# network 192.168.245.0 0.0.0.7 area 0
```

### 6.4 Task 4 — PC1 and PC2 Cannot Reach 8.8.8.8

**Symptom:** internal OSPF routing works fine, but neither LAN can reach the external ISP target.

**Diagnosis:**
```cisco
R1# show ip route 0.0.0.0
```
No default route present anywhere in the domain.

**Root cause:** default-route injection into OSPF is a **two-part** requirement (reinforced from Day 26): (1) R5, the router actually facing the ISP, needs its own static default route, **and** (2) R5 needs `default-information originate` to convert that static route into a Type-5 LSA the rest of the domain can learn. Missing either half means zero downstream routers get a default route, with no error on either end.

**Fix:**
```cisco
! R5
R5(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2
R5(config)# router ospf 1
R5(config-router)# default-information originate
```

### 6.5 Task 5 — Audit the LSDB

```cisco
R5# show ip ospf database
```
- **Type-1 (Router LSA):** one per router in the area, describing that router's own directly-connected links. Five routers in area 0 → expect exactly five Type-1 entries.
- **Type-2 (Network LSA):** one per multi-access segment, originated by the segment's elected DR. SW3 is the only multi-access (switched) segment in this topology → expect exactly one Type-2 entry.
- **Type-5 (External LSA):** one per externally-injected route. A single default route from R5 → expect exactly one Type-5 entry for 0.0.0.0/0.

**Teaching point:** the LSDB is a direct, protocol-level health certificate — five routers, one shared segment, one external route in, matches the design intent exactly. A mismatch here (e.g., only four Type-1 LSAs) means a router isn't fully participating in the domain even if its own local routing table looks fine.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show ip interface brief` | Physical/line-protocol status — catches the serial clocking issue first |
| `show ip ospf neighbor` | Confirms adjacency state per interface |
| `show ip protocols` | Confirms which networks and areas are actually configured |
| `show ip ospf interface <if>` | Per-interface area, cost, network type, and timers |
| `show ip route` / `show ip route ospf` | Confirms routes actually installed |
| `show ip ospf database` | LSDB audit — Type-1/2/5 counts |
| `ping 8.8.8.8` from PC1/PC2 | End-to-end proof of the full fix chain |

### Expected Output Gallery

```text
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2          1   FULL/  -        00:00:31    192.168.12.2    Serial0/0/0
```

```text
R5# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
192.168.245.1    1   FULL/BDR        00:00:32    192.168.245.1   GigabitEthernet0/0
192.168.245.2    1   FULL/DROTHER    00:00:38    192.168.245.2   GigabitEthernet0/0
```

```text
R1# show ip route
O*E2 0.0.0.0/0 [110/1] via 203.0.113.2, Serial0/0/1
```

```text
R5# show ip ospf database

            OSPF Router with ID (5.5.5.5) (Process ID 1)

                Router Link States (Area 0)
Link ID         ADV Router      Age    Seq#       Checksum Link count
1.1.1.1         1.1.1.1         420    0x8000004  0x00abcd 3
2.2.2.2         2.2.2.2         418    0x8000005  0x00bcde 3
3.3.3.3         3.3.3.3         415    0x8000003  0x00cdef 2
4.4.4.4         4.4.4.4         417    0x8000004  0x00defa 2
5.5.5.5         5.5.5.5         410    0x8000006  0x00efab 2

                Net Link States (Area 0)
Link ID         ADV Router      Age    Seq#       Checksum
192.168.245.3   5.5.5.5         410    0x80000002 0x00f1ca

                Type-5 AS External Link States
Link ID         ADV Router      Age    Seq#       Checksum Tag
0.0.0.0         5.5.5.5         405    0x80000001 0x00d2c1  1
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Rebuilding OSPF from scratch instead of diagnosing** — defeats the point of a troubleshooting lab and wastes far more time than reading `show ip protocols` carefully.
2. **Assuming a serial link "up" administratively means it's functionally up** — always distinguish administrative status from line-protocol status; DCE/DTE clocking is invisible until you check `show controllers` or `show ip interface brief` closely.
3. **Treating a silent neighbor-formation failure as a cabling problem first** — area mismatches produce zero error messages and are far more common than physical faults on an already-working switch segment.
4. **Fixing only one half of default-route injection** — a static route with no `default-information originate`, or vice versa, both look "almost done" but produce zero downstream effect.
5. **Not cross-checking the LSDB against your own topology diagram** — a wrong LSA count is often the fastest way to notice a router isn't fully participating, faster than chasing individual routing tables one at a time.

---

## 9. Troubleshooting Decision Tree

```text
OSPF problem?
├── Adjacency not forming?
│   ├── Check interface status: show ip interface brief (admin AND line protocol)
│   ├── Check OSPF enabled on that interface: show ip ospf interface brief
│   ├── Check area match on both ends: show running-config | include area
│   ├── Check Hello/Dead timers match: show ip ospf interface <if>
│   └── Check subnet mask matches on both ends (broadcast networks)
├── Route missing on a remote router?
│   ├── Confirm the advertising router even has the route locally: show ip route
│   ├── Confirm the advertising router's network statement covers it: show ip protocols
│   ├── Confirm the interface isn't accidentally passive: show ip protocols
│   └── Confirm no area boundary is blocking it (inter-area needs an ABR)
└── No Internet / no default route downstream?
    ├── Confirm the ASBR has its own default route: show ip route 0.0.0.0
    ├── Confirm default-information originate is configured: show run | section router ospf
    ├── Confirm ASBR status: show ip ospf ("It is an autonomous system boundary router")
    └── Confirm the external LSA exists: show ip ospf database external
```

---

## 10. Design Analysis

**Why troubleshooting labs matter more than build labs for career readiness.** Building a clean topology from a blank slate tests whether you know the syntax. Troubleshooting a pre-broken one tests whether you can form and test hypotheses under uncertainty — the actual daily skill of a working network engineer. The five problems chosen here aren't arbitrary: DCE/DTE clocking, missing `network` statements, area mismatches, incomplete default-route injection, and LSDB literacy collectively cover the failure modes responsible for the overwhelming majority of real OSPF trouble tickets.

**Why the LSDB audit (Task 5) is placed last.** Once individual symptoms are fixed, the LSDB is the tool that proves the *whole domain* is healthy, not just the specific paths you happened to test with `ping`. It's the difference between "it works for the traffic I tried" and "I can account for every router and every advertised segment."

---

## 11. Real-World Parallel

Every NOC and every network engineer inherits configurations they didn't write. A ticket that reads "branch office can't reach headquarters, was working yesterday" is functionally identical to this lab's Task 2 or Task 3 — something silently stopped being advertised or stopped forming an adjacency, with no alarm bells, and the fix is a methodical process of elimination, not a rebuild.

---

## 12. Stretch Goal

Introduce a sixth deliberate fault of your own design (e.g., mismatched Hello/Dead timers on one link, or an authentication mismatch) into a working copy of this topology, hand it to a study partner without telling them what you changed, and have them apply the decision tree in Section 9 to find and fix it independently.

---

## 13. Self-Assessment Checklist

- [ ] I can distinguish administrative interface status from line-protocol status and know what a serial clocking issue looks like in `show ip interface brief`
- [ ] I know DCE supplies the clock and DTE does not, without having to look it up
- [ ] I can diagnose a missing route by checking the advertising router's `network` statements before assuming a remote-side problem
- [ ] I can explain why an area-ID mismatch produces a silent, error-free adjacency failure
- [ ] I can state both halves of default-route injection into OSPF from memory
- [ ] I can read `show ip ospf database` and correctly count Type-1, Type-2, and Type-5 LSAs against a known topology

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

Serial links require a clock rate on the DCE side — without it, the interface stays administratively up but line-protocol down, and OSPF can never form across it. Area mismatches are the number-one silent neighbor-formation killer — no error, no log, adjacency just never appears; `show ip ospf interface` is the tool that reveals per-interface area assignment. Passive interfaces silently prevent OSPF hellos on an otherwise-healthy segment. Default-route propagation requires two separate steps (a static default route on the ASBR, plus `default-information originate`) — missing either one produces zero effect with zero error. The LSDB tells the full story of domain health: one Type-1 LSA per router, one Type-2 LSA per multi-access segment, one Type-5 LSA per externally redistributed route — cross-checking these counts against the known topology is a faster health check than tracing individual routing tables.

**Skills practiced:** serial DCE/DTE troubleshooting, missing-route diagnosis via `network`-statement auditing, area-mismatch diagnosis on multi-access segments, two-part default-route verification, LSDB (Type-1/2/5 LSA) literacy, structured troubleshooting methodology.

---

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-28/GNS3/build_lab.py` and its companion `README.md` for an automated build of this 5-router topology using VyOS routers. Note: this build script constructs the topology **correctly configured** — to practice the troubleshooting scenario itself, deliberately introduce the five faults described in Section 6 (remove the clock rate, remove R3's LAN `network` statement, mismatch an area ID on SW3, remove R5's static default route or `default-information originate`) before handing it to a study partner or attempting the diagnosis fresh.
