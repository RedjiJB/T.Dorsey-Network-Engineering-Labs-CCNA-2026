# Day 08 Lab Manual — IPv4 Address Configuration & Router Interface Setup

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure IPv4 addressing on a single Cisco 2911 router's three interfaces (a `/8`, a `/16`, and a `/24`), configure matching end-device addressing and default gateways, and verify full inter-network routing through one router acting as gateway for three otherwise-isolated LANs. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): 1.6/1.7 (IPv4 addressing, subnetting math). This lab is exam-critical: it deliberately uses three *different* prefix lengths (/8, /16, /24) so you practice host-bit math across the full range instead of only ever seeing `/24`. |
| **Prerequisites** | Day 01–06 (topology building, cabling, switching). Comfort with binary-to-decimal conversion is assumed but re-derived from scratch here. |
| **Time Estimate** | 1.5 – 2 hours. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner-Intermediate) — the CLI is simple, but the addressing math across three different prefix lengths is where real understanding is built or exposed. |

---

## 1. Lab Overview

This lab is the first in the course to put real Layer 3 routing weight on IP addressing math: one router, three interfaces, three completely different prefix lengths (`/8`, `/16`, `/24`), each representing a different-sized network. The original three networks — `15.0.0.0/8`, `182.98.0.0/16`, `201.191.20.0/24` — are used exactly as given, because they're an excellent teaching set: a student who can only subnet `/24`s hasn't actually learned subnetting, they've memorized one special case.

Each network gets exactly one router interface as its gateway, one switch, and one PC — deliberately minimal, so 100% of the cognitive effort goes into the addressing math and the "why does the router need one interface per network" concept, not topology complexity.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Calculate host bits, usable host counts, and dotted-decimal subnet masks for any prefix length, not just `/24`
- Explain why a router needs a separate interface (and separate IP) per directly-connected network it routes between
- Configure IPv4 addresses on router interfaces with matching non-`/24` masks, bring them up, and verify status
- Configure end-device IP/mask/gateway settings correctly matched to their network's actual prefix length
- Verify Layer 3 connectivity end-to-end across three different-sized networks through a single router
- Explain, in business terms, why organizations end up with wildly different-sized subnets like `/8` and `/24` coexisting

---

## 2. Business Context

**Why would a real company do this?**

Real IP addressing plans are rarely tidy collections of same-sized `/24`s. In business terms:

- **"We inherited a legacy address block from an acquisition."** → `15.0.0.0/8` (this lab's Network A) is a realistic stand-in for a company that was allocated (or, in the private-network-analog sense, chose) a huge address block years ago, long before right-sizing subnets was standard practice — and now has to route it alongside newer, correctly-sized allocations.
- **"Our data center network and our office network were designed by different teams, at different times, with different needs."** → `182.98.0.0/16` (65,534 usable hosts) might represent a large campus or datacenter block, while `201.191.20.0/24` (254 usable hosts) represents a small branch office — same company, wildly different scale requirements, same router doing the routing between them.
- **"A junior engineer needs to be able to read *any* CIDR notation on a diagram, not just `/24`."** → this is the single most common real gap in early-career networking skill: engineers who are fluent with `/24` freeze up the moment they see a `/19` or `/12` on a real diagram, because they memorized one case instead of the underlying method. This lab exists specifically to break that habit early.

The router in this lab is doing exactly what enterprise core/distribution routers do daily: sitting at the boundary between differently-sized networks and moving traffic between them, regardless of how oddly each one is sized.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2008%20Lab%20-%20IPv4%20Addresses.png" alt="Day 08 IPv4 Addressing Lab" width="1000">
</p>

```text
Network A (/8)   PC1 -- SW1 -- R1 Gi0/0
Network B (/16)  PC2 -- SW2 -- R1 Gi0/1
Network C (/24)  PC3 -- SW3 -- R1 Gi0/2
```

One router (`R1`), three switches (`SW1`, `SW2`, `SW3`), three PCs (`PC1`, `PC2`, `PC3`) — three completely independent LANs, unified only by R1 routing between them.

---

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

| Network | Prefix | Usable hosts | Realistic use case represented |
|---|---|---|---|
| A | /8 | 16,777,214 | A legacy or intentionally oversized allocation — vastly more than this lab's single PC needs, included specifically to force `/8` math practice |
| B | /16 | 65,534 | A large campus/datacenter-scale block |
| C | /24 | 254 | A typical branch-office LAN — the size used in almost every other lab in this course |

**Key teaching point:** this lab is not telling you to *design* networks this way for real (a single-PC LAN on a `/8` would be an enormous, deliberate waste in production) — it's giving you three prefix lengths on purpose so the math below can't be shortcut by memorizing one case.

### 4.2 Manual Calculation Walkthrough — All Three Prefixes

**Network A — `15.0.0.0/8`**

```text
Prefix /8 → network portion = first 8 bits, host portion = remaining 24 bits
h = 24 host bits

usable hosts = 2^24 − 2 = 16,777,216 − 2 = 16,777,214

Mask derivation:
/8 = 11111111.00000000.00000000.00000000
   =     255 .      0 .      0 .      0
```

```text
Network address:    15.0.0.0        (all 24 host bits = 0)
First usable host:  15.0.0.1
Last usable host:   15.255.255.254  (all 24 host bits = 1, minus 1)
Broadcast address:  15.255.255.255  (all 24 host bits = 1)
```

Notice the gateway address used in this lab, `15.255.255.254`, is deliberately the *second-to-last* usable address in the block rather than `.0.1` — a valid, if slightly unconventional, design choice. There is no rule requiring the gateway to be the first usable address; it simply has to be a valid usable host address inside the block, consistently applied.

**Network B — `182.98.0.0/16`**

```text
Prefix /16 → network portion = first 16 bits, host portion = remaining 16 bits
h = 16 host bits

usable hosts = 2^16 − 2 = 65,536 − 2 = 65,534

Mask derivation:
/16 = 11111111.11111111.00000000.00000000
    =     255 .     255 .      0 .      0
```

```text
Network address:    182.98.0.0
First usable host:  182.98.0.1
Last usable host:   182.98.255.254
Broadcast address:  182.98.255.255
```

**Network C — `201.191.20.0/24`**

```text
Prefix /24 → network portion = first 24 bits, host portion = remaining 8 bits
h = 8 host bits

usable hosts = 2^8 − 2 = 256 − 2 = 254

Mask derivation:
/24 = 11111111.11111111.11111111.00000000
    =     255 .     255 .     255 .      0
```

```text
Network address:    201.191.20.0
First usable host:  201.191.20.1
Last usable host:   201.191.20.254
Broadcast address:  201.191.20.255
```

### 4.3 Memory Aid Table (Common Prefixes)

| Prefix | Host bits | Usable hosts | Mask |
|---|---|---|---|
| /8  | 24 | 16,777,214 | 255.0.0.0 |
| /16 | 16 | 65,534     | 255.255.0.0 |
| /24 | 8  | 254        | 255.255.255.0 |

**The pattern to internalize:** every full octet of `255` in the mask represents 8 bits fully consumed by the network portion; the first non-`255` octet is where host bits begin. `/8`, `/16`, `/24` are the three "clean octet boundary" prefixes — the easiest to reason about, and exactly why this lab chose them before later labs introduce prefixes that split a single octet (`/27`, `/29`, etc., as seen in Days 01 and 02).

### 4.4 Full Device Address Table

| Device | Interface | IP Address | Mask | Network |
|---|---|---|---|---|
| PC1 | NIC | 15.0.0.1 | 255.0.0.0 | A |
| R1 | Gi0/0 | 15.255.255.254 | 255.0.0.0 | A |
| PC2 | NIC | 182.98.0.1 | 255.255.0.0 | B |
| R1 | Gi0/1 | 182.98.255.254 | 255.255.0.0 | B |
| PC3 | NIC | 201.191.20.1 | 255.255.255.0 | C |
| R1 | Gi0/2 | 201.191.20.254 | 255.255.255.0 | C |

**Default gateways:** PC1 → `15.255.255.254`; PC2 → `182.98.255.254`; PC3 → `201.191.20.254`.

---

## 5. Pre-Configuration Checklist

1. Place R1, SW1–SW3, PC1–PC3 and cable per Section 3 (straight-through everywhere: router-switch, switch-PC).
2. Have the mask-derivation table (Section 4.2/4.3) open — do not type a mask you haven't personally verified against the binary math at least once in this lab.
3. Confirm R1 has at least 3 usable LAN interfaces (Gi0/0, Gi0/1, Gi0/2 on a 2911) before starting.

---

## 6. Configuration Tasks

### 6.1 Hostname

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
```

> **Mode:** User EXEC → Privileged EXEC → Global Config.

### 6.2 Verify Baseline (before touching interfaces)

```text
R1(config)#do show ip interface brief
```

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES unset  administratively down down
GigabitEthernet0/1         unassigned      YES unset  administratively down down
GigabitEthernet0/2         unassigned      YES unset  administratively down down
```

> `do` is a useful shortcut that lets you run an EXEC-level command (like `show`) from inside Global Config mode without first exiting — saves a round trip of `exit` / command / `configure terminal` again.

### 6.3 Configure GigabitEthernet0/0 (Network A)

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description Network A - /8 - PC1 segment
R1(config-if)#ip address 15.255.255.254 255.0.0.0
R1(config-if)#no shutdown
R1(config-if)#exit
```

> **Mode:** Interface Config. `ip address` here takes a full dotted-decimal mask, not a `/8` prefix — IOS's `ip address` command syntax always wants the expanded mask form (this is why deriving `255.0.0.0` from `/8` in Section 4.2 matters: you can't type `/8` directly into this command). `no shutdown` is required — every interface on a fresh router boots administratively down.

### 6.4 Configure GigabitEthernet0/1 (Network B)

```text
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description Network B - /16 - PC2 segment
R1(config-if)#ip address 182.98.255.254 255.255.0.0
R1(config-if)#no shutdown
R1(config-if)#exit
```

### 6.5 Configure GigabitEthernet0/2 (Network C)

```text
R1(config)#interface gigabitEthernet 0/2
R1(config-if)#description Network C - /24 - PC3 segment
R1(config-if)#ip address 201.191.20.254 255.255.255.0
R1(config-if)#no shutdown
R1(config-if)#exit
```

### 6.6 Verify All Interfaces

```text
R1#show ip interface brief
```

### 6.7 Save

```text
R1#copy running-config startup-config
```

### 6.8 End Devices

Configure via Desktop → IP Configuration on each PC, per Section 4.4's table — static, not DHCP.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip interface brief` | All 3 interfaces `up/up`, correct IPs |
| `show ip route` | 3 directly connected routes, one per network |
| `ping` (from each PC to its own gateway, then to the other two PCs) | Success at every stage |

### 7.1 Expected Output Gallery

**`R1# show ip interface brief`**

```text
Interface                  IP-Address       OK? Method Status                Protocol
GigabitEthernet0/0         15.255.255.254   YES manual up                    up
GigabitEthernet0/1         182.98.255.254   YES manual up                    up
GigabitEthernet0/2         201.191.20.254   YES manual up                    up
```

**`R1# show ip route`**

```text
      15.0.0.0/8 is directly connected, GigabitEthernet0/0
      15.255.255.254/32 is directly connected, GigabitEthernet0/0
      182.98.0.0/16 is directly connected, GigabitEthernet0/1
      182.98.255.254/32 is directly connected, GigabitEthernet0/1
      201.191.20.0/24 is directly connected, GigabitEthernet0/2
      201.191.20.254/32 is directly connected, GigabitEthernet0/2
```

No static routes were configured or needed — because all three networks are *directly connected* to R1 (one on each interface), IOS automatically installs a connected route for each the moment the interface comes `up/up` with a valid IP. This is a key distinction from Day 01/02/03, where routes to *non-directly-connected* networks required manual `ip route` statements.

**`PC1> ping 182.98.0.1`** (PC1 to PC2, across two different-sized networks)

```text
Pinging 182.98.0.1 with 32 bytes of data:

Reply from 182.98.0.1: bytes=32 time=1ms TTL=127
Reply from 182.98.0.1: bytes=32 time=1ms TTL=127
Reply from 182.98.0.1: bytes=32 time=1ms TTL=127
Reply from 182.98.0.1: bytes=32 time=1ms TTL=127

Ping statistics for 182.98.0.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Note the TTL of 127 (not 128) — it decremented by exactly 1, confirming the packet passed through exactly one router hop (R1) to get from Network A to Network B.

### 7.2 Reachability Matrix

| From | To | Expected | Why |
|---|---|---|---|
| PC1 | R1 Gi0/0 (own gateway) | Success | Directly connected |
| PC1 | PC2 | Success | Routed via R1, connected routes only, no static routing needed |
| PC1 | PC3 | Success | Same reasoning |
| PC2 | PC3 | Success | Same reasoning |

---

## 8. Common Mistakes (the 80/20)

1. **Typing a CIDR prefix (`/8`, `/16`) directly into `ip address` instead of the expanded dotted-decimal mask.** IOS's `ip address` command requires the full mask (`255.0.0.0`), not slash notation — a very common first-timer syntax error.
2. **Deriving the wrong mask for `/8` or `/16` by pattern-matching from `/24` instead of doing the actual binary math.** Students who've only ever worked with `/24` sometimes guess `255.255.255.0` reflexively for every network in this lab — always re-derive from host-bit count.
3. **Forgetting `no shutdown` on any of the three interfaces** — same universal mistake from every prior lab, now three times over instead of once.
4. **Assigning a PC an address outside its network's valid range** (e.g., accidentally typing an address from Network B onto a Network A device) — always double check the address matches the *directly connected* network for that segment.
5. **Expecting to need static routes.** Since every network here is directly attached to R1 (one per interface), no `ip route` statements are needed at all — a student who adds them anyway hasn't broken anything, but it signals a misunderstanding of directly-connected vs. remote routes.
6. **Confusing which router interface belongs to which network** when there are three of them — always double-check the interface description against the addressing table before assuming.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Interface shows `administratively down` | Forgot `no shutdown` | `show ip interface brief` | Enter interface, `no shutdown` |
| 2 | PC can't reach its own gateway | Wrong mask on PC (doesn't match the router's mask for that network) | `ipconfig` (PC) vs. router interface config | Correct the mismatched mask |
| 3 | PC reaches its own gateway but not another PC's network | Wrong IP typed on the router interface (off by a network) | `show ip interface brief` vs. addressing table | Correct the interface's IP/mask |
| 4 | `show ip route` missing an expected connected route | Interface is down, or has no IP assigned | `show ip interface brief` | Fix IP/mask/`no shutdown` on that interface |
| 5 | Ping fails with "Destination host unreachable" from a PC | PC's default gateway is wrong or unreachable | Check PC's IP config | Correct default gateway to match its network's router interface |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why does each network get its own router interface instead of trying to share one?** A router interface is inherently one physical (or logical, with subinterfaces/trunking — a later-course topic) connection to one broadcast domain. Three genuinely separate Layer 2 segments require three separate Layer 3 gateway presences — this is the literal definition of what makes a router a router, as opposed to a switch.
- **Why no static routes needed here, unlike Day 01–03?** Because every network in this lab is *directly connected* — R1 has a live interface with a valid IP on all three. IOS auto-populates a connected route the instant an interface comes `up/up` with an address. Static routes only become necessary once a router needs to reach a network it isn't directly touching (as in every multi-router lab in this course).
- **Why practice `/8` and `/16` instead of only `/24`, given real branch-office design almost always uses `/24` or smaller?** Because the exam — and real enterprise diagrams you'll eventually be handed — will absolutely include non-`/24` prefixes, and a candidate who can only reason about `/24` will freeze on the first `/19` VPC subnet or `/12` legacy allocation they encounter. This lab deliberately builds the muscle before it's urgently needed.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...you inherit documentation showing a `/8` or `/16` block from a company's early days, long before subnet right-sizing was standard practice, and you need to route alongside newer `/24` allocations without touching the legacy block.
- ...a cloud VPC diagram hands you a `/19` or `/20` subnet and you need to instantly know its usable host count without reaching for a subnet calculator — the muscle this lab is training.
- ...a router in a small business is the *only* Layer 3 device on-site, directly connected to every VLAN/subnet in the building, and "no static routes needed, everything is directly connected" is simply the accurate state of that network, not a simplification.

---

## 12. Stretch Goal

1. Add a fourth network on a `/28` (16 addresses, 14 usable) connected to a new R1 interface, and do the full manual calculation (host bits, mask, network/broadcast/first/last host) from scratch.
2. Given a hypothetical `172.16.0.0/12`, calculate the usable host count and dotted-decimal mask without looking anything up — this prefix splits a single octet unevenly and is a good stress test of the method beyond this lab's clean-octet-boundary prefixes.
3. Explain, in writing, what would need to change if Network A's single PC needed to become 5 separate departmental subnets carved out of the existing `/8` block (a preview of VLSM, covered formally in a later lab).

---

## 13. Self-Assessment

- [ ] Can you derive the dotted-decimal mask for any prefix length from `/1` through `/32`, from binary, without memorizing a lookup table?
- [ ] Can you explain why IOS's `ip address` command requires the full mask instead of slash notation?
- [ ] Can you explain why this lab needed zero static routes, when Days 01–03 needed several?
- [ ] Given a new prefix you've never worked with before (e.g., `/13`), could you calculate its usable host count on the spot?
- [ ] Can you explain, in one sentence, why a router needs one interface per network it directly serves?

---

## 14. Key Concepts Demonstrated

- IPv4 subnetting math across multiple, differently-sized prefixes (/8, /16, /24)
- Router interface addressing and the `ip address <ip> <mask>` IOS syntax
- Directly-connected routes and why they require no static configuration
- End-to-end Layer 3 connectivity verification across heterogeneous network sizes

## What I Learned

Working through `/8`, `/16`, and `/24` side by side in the same lab was the first time the subnetting math stopped feeling like a `/24`-only trick and started feeling like a general method — the same `2^h − 2` formula and binary mask derivation applied cleanly to all three, regardless of how different the resulting networks looked in size. It also clarified, very concretely, the difference between a directly-connected route (automatic, the moment an interface is up with an IP) and a route to a remote network (requires explicit static or dynamic configuration) — a distinction that had been implicit in earlier labs but became obvious here specifically because this lab needed zero static routes.

## Skills Practiced

- Manual IPv4 subnet mask derivation across multiple prefix lengths
- Router interface IP configuration
- Directly-connected route verification
- End-to-end multi-network connectivity testing

---

## 15. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| R1 | Cisco 2911 | VyOS |
| SW1, SW2, SW3 | Cisco 2960 | Open vSwitch |
| PC1, PC2, PC3 | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script.
