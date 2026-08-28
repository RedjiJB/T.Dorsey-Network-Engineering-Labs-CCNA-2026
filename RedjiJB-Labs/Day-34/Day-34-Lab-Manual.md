# Day 34 Lab Manual — Standard ACLs with OSPF-Routed Connectivity

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Establish full OSPF connectivity across two routers and four subnets, then enforce five source-based traffic policies using both numbered and named standard ACLs. |
| **Exam Relevance** | CCNA 200-301 — Domain 3 (IP Connectivity continued)/Domain 4: single-area OSPF configuration and passive interfaces. Domain 5 (Security Fundamentals): standard ACL syntax, wildcard masks, and placement logic. |
| **Prerequisites** | Basic IPv4 addressing/subnetting (Day 1). No prior ACL or OSPF experience required — this is the first ACL lab and a light first touch of OSPF. |
| **Time Estimate** | 90–120 minutes. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — OSPF setup is quick, but getting ACL placement/direction right for five distinct policies takes careful reasoning. |

---

## 1. Lab Overview + Learning Objectives

This lab has two phases: first, get every PC and server routing to every other subnet via OSPF (a working, fully-open network); second, layer five specific traffic policies on top using standard ACLs — some numbered, some named — without breaking OSPF itself.

By the end of this lab you will be able to:

- Configure single-area OSPF across two routers and verify full adjacency and route propagation
- Use `passive-interface` to stop routing protocol traffic from being sent out LAN-facing interfaces unnecessarily
- Write standard numbered ACLs (1–99) and standard named ACLs, understanding they are functionally identical apart from naming/editing convenience
- Correctly reason about ACL placement (which interface, which direction) to satisfy a stated policy with minimal collateral blocking
- Explain the source-only limitation of standard ACLs and when it forces you toward extended ACLs instead (Day 35)

---

## 2. Business Context

**Why would a real company do this?**

- **"Get everyone talking first, then lock it down."** This is the actual sequence almost every real network follows: build full routed connectivity, verify it works, then apply security policy in layers. Building ACLs before routing works makes every problem ambiguous — is it a routing issue or a policy issue? — so this lab deliberately teaches the phases in the field-realistic order.
- **"Our finance server should only be reachable by finance's own subnet and one other trusted subnet — nobody else."** Policy 1 in this lab (only PC1 and PC3 may reach SRV1) is exactly this kind of real access-control requirement — a resource that legitimately needs to be reachable from more than one place, but not from everywhere.
- **"Our two office segments shouldn't be able to talk to each other directly, even though they share a router."** Policies 2 and 3 (172.16.1.0/24 and 172.16.2.0/24 blocked from each other) model internal network segmentation — a very common requirement between, e.g., a guest/lab network and a production network that happen to share infrastructure.
- **"We use both numbered and named ACLs across our fleet — some legacy devices, some newer configs — and engineers need to be fluent in both."** Many real networks have a mix of numbered ACLs from older configurations and named ACLs from newer standards-compliant builds; being able to read, write, and reason about both without confusion is a genuine day-to-day skill, which is why this lab deliberately splits the two ACL styles across R1 and R2.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-34-Lab-Standard-ACLs.png" alt="Day 34 Standard ACLs Topology" width="900">
</p>

```text
PC1, PC2 -- R1 G0/0 (172.16.1.0/24)
PC3, PC4 -- R1 G0/1 (172.16.2.0/24)
R1 S0/0/0 === R2 S0/0/0  (203.113.0.0/30, OSPF area 0)
SRV1 -- R2 G0/0 (192.168.1.0/24)
SRV2 -- R2 G0/1 (192.168.2.0/24)
```

---

## 4. IP Addressing Plan

| Device | Interface | IP Address | Subnet |
|---|---|---|---|
| R1 | G0/0 | 172.16.1.254 | 172.16.1.0/24 |
| R1 | G0/1 | 172.16.2.254 | 172.16.2.0/24 |
| R1 | S0/0/0 | 203.113.0.1 | 203.113.0.0/30 |
| R2 | G0/0 | 192.168.1.254 | 192.168.1.0/24 |
| R2 | G0/1 | 192.168.2.254 | 192.168.2.0/24 |
| R2 | S0/0/0 | 203.113.0.2 | 203.113.0.0/30 |
| PC1 | Fa0 | 172.16.1.1 | 172.16.1.0/24 |
| PC2 | Fa0 | 172.16.1.2 | 172.16.1.0/24 |
| PC3 | Fa0 | 172.16.2.1 | 172.16.2.0/24 |
| PC4 | Fa0 | 172.16.2.2 | 172.16.2.0/24 |
| SRV1 | Fa0 | 192.168.1.100 | 192.168.1.0/24 |
| SRV2 | Fa0 | 192.168.2.100 | 192.168.2.0/24 |

### 4.1 How to derive the wildcard masks by hand (standard ACL prerequisite)

A wildcard mask is the *inverse* of a subnet mask: wherever the subnet mask has a `1` bit (must-match), the wildcard mask has a `0` (must-match); wherever the subnet mask has a `0` (don't-care/host bits), the wildcard mask has a `1` (don't-care).

**Worked example — 172.16.1.0/24:**

```text
Subnet mask:    255.255.255.  0   = 11111111.11111111.11111111.00000000
Wildcard mask:  0.0.0.255           = 00000000.00000000.00000000.11111111
                                       (bitwise NOT of the subnet mask)
```

Shortcut: for a "clean" /24, /16, /8 boundary, the wildcard mask is simply `255 − maskoctet` per octet — `255 − 255 = 0`, `255 − 0 = 255`. This matches the `0.0.0.255` used throughout this lab's `access-list ... 172.16.2.0 0.0.0.255` statements.

**A `host` match is a wildcard of all zeros:** `access-list 3 permit 172.16.1.1` (with no wildcard shown) is IOS shorthand for `172.16.1.1 0.0.0.0` — every bit must match exactly, i.e., exactly one address.

---

## 5. Pre-Configuration Checklist

1. Confirm every interface's IPv4 addressing is complete and `no shutdown` before starting OSPF.
2. Have the five policy statements (Section 6.3–6.4) written out in plain English before writing any ACL line — translating a business requirement into source/destination/direction is the actual skill being tested, not ACL syntax memorization.
3. Know which interfaces are LAN-facing (never want routing protocol chatter) versus WAN-facing (need OSPF hellos) before configuring `passive-interface`.

---

## 6. Configuration Tasks

### Phase 1: OSPF Routing

```text
! R1
R1(config)#router ospf 1
R1(config-router)#router-id 1.1.1.1
R1(config-router)#network 172.16.1.0 0.0.0.255 area 0
R1(config-router)#network 172.16.2.0 0.0.0.255 area 0
R1(config-router)#network 203.113.0.0 0.0.0.3 area 0
R1(config-router)#passive-interface g0/0
R1(config-router)#passive-interface g0/1

! R2
R2(config)#router ospf 1
R2(config-router)#router-id 2.2.2.2
R2(config-router)#network 203.113.0.0 0.0.0.3 area 0
R2(config-router)#network 192.168.1.0 0.0.0.255 area 0
R2(config-router)#network 192.168.2.0 0.0.0.255 area 0
R2(config-router)#passive-interface g0/0
R2(config-router)#passive-interface g0/1
```

- **Mode:** Router configuration (`router ospf 1`).
- **`router-id`** is a 32-bit value (formatted like an IP, but not required to correspond to a real interface) that uniquely identifies this router within the OSPF domain — set explicitly here rather than left to auto-selection, which is best practice so the ID is stable and predictable across reboots.
- **`network <addr> <wildcard> area 0`** tells OSPF which directly-connected interfaces to run on, using a wildcard mask (Section 4.1) rather than a subnet mask — this is the same wildcard concept ACLs use, which is not a coincidence; both features predate a unified "just use CIDR everywhere" convention in IOS.
- **`passive-interface`** stops OSPF hello packets from being sent out the specified interface while still advertising that interface's connected network — applied to the LAN-facing interfaces because there are no other OSPF routers on those segments, so sending hellos there is pure waste and a minor information-disclosure/security surface with zero benefit.
- **Memory aid:** "Passive interfaces still advertise, they just stop talking to neighbors that will never exist there."

### Phase 2: Standard Numbered ACLs on R1

**Policy 1 — Only PC1 and PC3 can reach SRV1 (192.168.1.0/24):**

```text
R1(config)#access-list 3 permit 172.16.1.1
R1(config)#access-list 3 permit 172.16.2.1
R1(config)#access-list 3 deny any
R1(config)#interface serial0/0/0
R1(config-if)#ip access-group 3 out
```
- Applied **outbound** on the WAN interface — because standard ACLs can't see destination, the only way to scope this policy to "traffic heading toward SRV1's segment" is to place it on the interface that traffic must cross to reach that segment at all, right as it leaves R1.

**Policy 2 — 172.16.1.0/24 cannot access 172.16.2.0/24:**

```text
R1(config)#access-list 1 deny 172.16.1.0 0.0.0.255
R1(config)#access-list 1 permit any
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#ip access-group 1 in
```
- Applied **inbound on G0/1** — the interface where 172.16.2.0/24 traffic would need to re-enter if it were replying, but more importantly this blocks 172.16.1.0/24-sourced traffic the moment it tries to *enter* the 172.16.2.0/24 segment, which is the earliest point this specific direction of traffic can be stopped.

**Policy 3 — 172.16.2.0/24 cannot access 172.16.1.0/24:**

```text
R1(config)#access-list 2 deny 172.16.2.0 0.0.0.255
R1(config)#access-list 2 permit any
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ip access-group 2 in
```
- Mirror image of Policy 2, applied inbound on G0/0.

### Phase 3: Standard Named ACLs on R2

**Policy 4 — 172.16.2.0/24 cannot access SRV2 (192.168.2.0/24):**

```text
R2(config)#ip access-list standard TENANT2-BLOCK
R2(config-std-nacl)# deny 172.16.2.0 0.0.0.255
R2(config-std-nacl)# permit any
R2(config-std-nacl)#exit
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#ip access-group TENANT2-BLOCK in
```

**Policy 5 — 172.16.1.0/24 cannot access 172.16.2.0/24, enforced from R2's side too:**

```text
R2(config)#ip access-list standard SEGMENT-ISO
R2(config-std-nacl)# deny 172.16.1.0 0.0.0.255
R2(config-std-nacl)# permit any
R2(config-std-nacl)#exit
R2(config)#interface serial0/0/0
R2(config-if)#ip access-group SEGMENT-ISO in
```

- **Named vs numbered — purely syntactic, not functional.** `ip access-list standard NAME` followed by rule lines (no `access-list` prefix inside) is the named form; it supports sequence-number editing (`no 10`, insert at `15`) that numbered ACLs don't. Both filter source-IP-only, both use the same wildcard logic, both get an implicit `deny any` at the end whether you write it or not.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip protocols` | OSPF process active, correct networks listed, passive interfaces shown |
| `show ip ospf neighbor` | Full adjacency (`FULL` state) with the other router |
| `show ip route ospf` | Remote subnets learned via OSPF (`O` prefix) |
| `show ip access-lists` | All ACLs and their current hit counts |
| `show ip interface g0/0` | Confirms which ACL, if any, is bound and in which direction |

### 7.1 Expected Output Gallery

**`R1# show ip ospf neighbor`**
```text
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2         0     FULL/  -        00:00:32    203.113.0.2     Serial0/0/0
```

**`R1# show ip access-lists`**
```text
Standard IP access list 1
    10 deny 172.16.1.0 0.0.0.255
    20 permit any (34 matches)
Standard IP access list 2
    10 deny 172.16.2.0 0.0.0.255
    20 permit any (28 matches)
Standard IP access list 3
    10 permit 172.16.1.1 (12 matches)
    20 permit 172.16.2.1 (9 matches)
    30 deny any (6 matches)
```

**`R2# show ip access-lists TENANT2-BLOCK`**
```text
Standard IP access list TENANT2-BLOCK
    10 deny 172.16.2.0 0.0.0.255 (4 matches)
    20 permit any (19 matches)
```

### 7.2 Ping / Reachability Matrix

| From | To | Expected | Enforced by |
|---|---|---|---|
| PC1 (172.16.1.1) | SRV1 | Success | ACL 3 permit |
| PC2 (172.16.1.2) | SRV1 | **Fail** | ACL 3 implicit path to `deny any` |
| PC1 | PC3 (172.16.2.1) | **Fail** | ACL 2 (inbound R1 G0/0) |
| PC3 | PC1 | **Fail** | ACL 1 (inbound R1 G0/1) |
| PC3 | SRV2 | **Fail** | TENANT2-BLOCK (inbound R2 G0/1) |
| PC1 | SRV2 | Success | No policy restricts this path |

---

## 8. Common Mistakes (the 80/20)

1. **Forgetting the implicit `deny any` isn't visible but is always there.** Every standard ACL ends with an invisible `deny any` — if you only write `permit` lines and expect everything else to pass, you'll be surprised when unrelated traffic is silently dropped.
2. **Applying an ACL on the wrong interface or direction.** The same rule text produces a completely different effect depending on placement — Section 6's Design Analysis (below) and the golden "block near the source" rule are what actually determine correctness, not the ACL syntax itself.
3. **Blocking OSPF hellos by accident with a LAN-facing ACL.** This lab avoids it because `passive-interface` already stops hellos on the LAN side, so the ACLs there never interact with OSPF traffic — but on the WAN interface, always double check a broad `deny` doesn't also catch OSPF's multicast (224.0.0.5/6).
4. **Mixing up numbered ACL ranges.** Standard is 1–99 (or 1300–1999 for expanded range); using 100+ accidentally creates an *extended* ACL with different (and here, incompatible) syntax expectations.
5. **Assuming named and numbered ACLs behave differently.** They don't — the only difference is editability and readability, not filtering capability.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | No OSPF neighbor forms | Interface not `no shutdown`, or `network` statement wildcard wrong | `show ip ospf neighbor`, `show ip protocols` | Correct wildcard mask or bring interface up |
| 2 | LAN hosts can't reach any remote subnet | Missing `network` statement for a LAN subnet | `show ip route` | Add the missing OSPF `network` line |
| 3 | A policy that should block traffic doesn't | ACL applied to wrong interface/direction, or rule order wrong | `show ip access-lists` (check match counters) | Reapply on correct interface/direction |
| 4 | A policy blocks more than intended (collateral damage) | ACL wildcard too broad, or missing the specific-host permits before the deny | `show ip access-lists` | Narrow the wildcard or reorder rules |
| 5 | OSPF adjacency drops after ACL applied | ACL accidentally denies OSPF multicast on the WAN interface | `show ip ospf neighbor` before/after ACL | Add explicit `permit` for OSPF traffic or verify placement avoids the WAN interface |

---

## 10. Design Analysis

- **Why route everything first, then apply ACLs, instead of building policy into the routing design?** Separating "can this ever reach that" (routing) from "should this be allowed to reach that" (security policy) keeps each layer independently testable — exactly the phased approach this lab teaches, and the approach real network engineers use to isolate whether a failure is topological or policy-driven.
- **Why passive-interface instead of just not running OSPF on the LAN interfaces at all?** The LAN subnets still need to be advertised into OSPF so remote routers know how to reach them — `passive-interface` gets you "advertise the network, don't chatter with nonexistent neighbors," which omitting the `network` statement entirely would not achieve (that would hide the subnet from OSPF altogether).
- **Why standard ACLs are sufficient for these five policies specifically:** every policy here is phrased purely in terms of *source* ("PC1 and PC3 can," "172.16.2.0/24 cannot") — none of them says "block this subnet from reaching this OTHER subnet but only for this service," which is the trigger for needing destination/port awareness (Day 35's extended ACLs).
- **Why enforce Policy 1 outbound on the WAN link rather than inbound on R2's G0/0?** Either technically works for the "who reaches SRV1" outcome, but stopping it at R1 (closer to the source, before the WAN link is even crossed) avoids wasting the WAN link's capacity on traffic that's going to be dropped anyway — the same "block near the source" principle applied at the router-hop level instead of the local-LAN level.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a company's finance and engineering departments share a router but must be walled off from each other for compliance reasons — Policies 2/3's mutual isolation is exactly this.
- ...a new hire asks why they can ping the file server but not the finance server from the same desk — that's Policy 1's asymmetric access working as designed, not a bug.
- ...you inherit a network with some devices running numbered ACLs from a decade-old build and others running named ACLs from a newer standard, and you need to read and modify both without missing anything — the R1/R2 split in this lab is deliberately built to give you that exact mixed experience once.

---

## 12. Stretch Goal

1. Convert R1's two numbered ACLs (1 and 2) into named ACLs, and vice versa for R2's two named ACLs, without changing their filtering behavior — verify with `show ip access-lists` that the effective policy is identical.
2. Add a sixth policy: PC2 specifically (not all of 172.16.1.0/24) should be blocked from SRV2, while PC1 remains allowed. Determine whether a standard ACL can express this cleanly, or whether you're starting to hit the limits that motivate Day 35.
3. Investigate what happens to `show ip access-lists` match counters over time — clear them with `clear ip access-list counters` and re-run the reachability matrix to watch the counts increment in real time.

---

## 13. Self-Assessment

- [ ] Can you derive a wildcard mask from a subnet mask by hand, for any /8–/30 boundary?
- [ ] Can you explain why `passive-interface` is applied to LAN interfaces and not the WAN interface?
- [ ] Can you write a standard ACL statement that permits exactly two specific hosts and denies everything else, from memory?
- [ ] Can you explain, without looking, why standard ACLs can't express "block this subnet from this specific service on that server"?
- [ ] Given a new policy requirement in plain English, could you correctly determine both the ACL rule text AND its correct interface/direction placement?

---

## 14. Key Concepts Demonstrated

- Single-area OSPF configuration and passive interfaces
- Wildcard mask derivation and its shared logic with OSPF `network` statements
- Standard numbered vs named ACLs
- ACL placement logic: interface and direction selection based on policy intent
- The implicit `deny any` at the end of every ACL

## 15. What I Learned

Routing and security policy are genuinely separate layers, and building them in that order — full connectivity first, then restrictions — makes every subsequent problem easier to diagnose, because a failure is either "OSPF isn't right" or "an ACL is blocking this," never an ambiguous mix of both discovered simultaneously. Standard ACLs are a blunt instrument by design: they only ever see where traffic came from, never where it's going or what it is — which is exactly right for policies phrased as "this subnet can/can't," and exactly wrong the moment a policy needs to mention a specific server or service, which is where Day 35's extended ACLs take over. ACL placement (which interface, which direction) is not incidental — the same rule text produces entirely different real-world behavior depending on where it's applied, and reasoning about that placement is the actual skill, more than the syntax itself.

## 16. Skills Practiced

- Single-area OSPF configuration, verification, and passive-interface tuning
- Standard numbered and named ACL authoring
- Wildcard mask derivation
- ACL placement and directional reasoning against stated business policy

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Original device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco router | VyOS |
| PCs/Servers (PC1-4, SRV1-2) | Generic PC/Server | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for VyOS's OSPF and firewall-rule (ACL-equivalent) syntax, since VyOS uses `set firewall` rule-sets rather than Cisco-style numbered/named ACLs.
