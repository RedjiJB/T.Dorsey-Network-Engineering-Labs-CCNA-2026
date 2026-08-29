# Day 11.1 Lab Manual — Configuring Static Routes

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a three-router, two-LAN topology and manually configure static routes so PC1 and PC2 — sitting behind different routers, two hops apart — can reach each other. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): configure and verify IPv4/IPv6 static routing, describe the routing table, differentiate methods of routing and routing protocols. |
| **Prerequisites** | Day 01 (device roles, basic IOS hardening), IPv4 addressing fundamentals, subnet mask notation. |
| **Time Estimate** | 1.5 – 2 hours (first attempt); 30–40 minutes on repeat. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner) — small device count, but the *routing logic* (why each router needs specific routes, not just "a route") is the real skill being tested. |

---

## 1. Lab Overview

Every previous lab in this course lived inside a single broadcast domain or a single router's directly connected networks. This lab is the first time a packet has to survive **more than one hop** to reach its destination — and a router, unlike a switch, has zero idea how to do that unless you tell it.

You will build a line topology — `PC1 — SW1 — R1 — R2 — R3 — SW2 — PC2` — and configure static routes on all three routers so that every network can reach every other network, including the two that aren't directly connected to any single router.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain why a router needs an explicit route to reach a network it isn't directly connected to
- Calculate and assign IP addressing across a chain of routed point-to-point links
- Write correct `ip route` statements from a router's own perspective (not everyone else's)
- Read a routing table and identify Connected (`C`), Local (`L`), and Static (`S`) route sources
- Verify multi-hop, end-to-end reachability
- Explain, in real-world terms, why static routing is a legitimate design choice for a small routed network

---

## 2. Business Context

**Why would a real company do this?**

Picture a small logistics company with a warehouse office (LAN 1) and a dispatch office (LAN 2) on opposite ends of a single building, connected through a small routed backbone (R1 → R2 → R3) instead of one flat switch — maybe because the two offices are on different floors with their own IT closets, or because IT wants to keep warehouse floor traffic (barcode scanners, forklifts with tablets) segmented from the dispatch office's business systems.

- **"Warehouse staff need to print to the dispatch office's shared printer"** → requires Layer 3 reachability between LAN 1 and LAN 2, which only works if every router in the path knows how to get there.
- **"We only have three routers and they rarely change"** → this is the textbook case *for* static routing instead of a dynamic protocol: three routers, a handful of routes, no redundancy to manage. Static routes are 100% predictable — nothing "elects" anything, nothing "converges," the routing table is exactly what you typed.
- **"IT is a team of one and needs to know exactly what's in the routing table"** → static routes mean no surprises. If a route is in `show ip route`, an engineer put it there on purpose.

This is the smallest possible version of a "multi-hop enterprise network" — the exact scenario every routing protocol (RIP, OSPF, EIGRP) exists to eventually replace once the network outgrows what a human can maintain by hand.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2011%20Lab%20-%20Configuring%20Static%20Routes%20.png" width="900">
</p>

### 3.1 Traffic Flow Summary

```text
PC1 -- SW1 -- R1 -- R2 -- R3 -- SW2 -- PC2
       (LAN1)         (transit)        (LAN2)
```

### 3.2 Equipment List

| Device | Model | Role |
|---|---|---|
| R1 | Cisco 2911 | LAN1 gateway / edge router |
| R2 | Cisco 2911 | Transit / middle router |
| R3 | Cisco 2911 | LAN2 gateway / edge router |
| SW1 | Cisco 2960 | LAN1 access switch |
| SW2 | Cisco 2960 | LAN2 access switch |
| PC1 | Generic PC | LAN1 end host |
| PC2 | Generic PC | LAN2 end host |

---

## 4. IP Addressing Plan

### 4.1 Why Each Subnet Is Sized the Way It Is

| Segment | Hosts needed | Why this prefix |
|---|---|---|
| LAN 1 (PC1 + gateway) | 1 host today, room to grow | `/24` — a real user LAN, always sized with headroom |
| LAN 2 (PC2 + gateway) | 1 host today, room to grow | `/24` — same reasoning |
| R1 ↔ R2 transit | Exactly 2 | `/24` is what the original lab used for simplicity, but a `/30` is the textbook-correct size for a point-to-point link — see the note below |
| R2 ↔ R3 transit | Exactly 2 | Same |

> **Design note:** This lab's original addressing (`192.168.12.0/24`, `192.168.13.0/24`) uses full `/24`s on point-to-point router links, which works but wastes 252 addresses per link. We keep the original `/24` scheme below so the addressing table matches the topology image and lab tradition, but Section 13 (Design Analysis) discusses the `/30` alternative — you should be able to redo this addressing plan with `/30` transit links as a self-test.

### 4.2 How to Calculate These by Hand

**LAN subnet — /24:**

```text
usable hosts = 2^h - 2
Need: comfortably more than 1-2 hosts, with growth room
2^8 - 2 = 254   → /24 (24 network bits, 8 host bits)
```

**If you instead sized the transit links as /30 (recommended self-check):**

```text
2^h - 2 >= 2
2^2 - 2 = 2   → exactly fits, h = 2 host bits
32 - 2 = /30
```

```text
/30 = 11111111.11111111.11111111.11111100
    =     255  .    255  .    255  .   252
```

**Network/first/last/broadcast worked example — LAN 1 (192.168.1.0/24):**

```text
Network address:    192.168.1.0     (all host bits = 0)
First usable host:  192.168.1.1
Last usable host:   192.168.1.254
Broadcast address:  192.168.1.255   (all host bits = 1)
```

**Block-size shortcut:** for a `/24`, block size = 256 (the whole third octet range); for a `/30`, block size = `256 - 252 = 4`, so `/30` networks land on multiples of 4 (`.0, .4, .8, .12...`).

### 4.3 Full Device Address Table

| Device | Interface | IP Address | Mask | Connects To |
|---|---|---|---|---|
| PC1 | NIC | 192.168.1.1 | 255.255.255.0 | SW1 |
| R1 | G0/0 | 192.168.1.254 | 255.255.255.0 | SW1 (LAN1 gateway) |
| R1 | G0/1 | 192.168.12.1 | 255.255.255.0 | R2 G0/1 |
| R2 | G0/1 | 192.168.12.2 | 255.255.255.0 | R1 G0/1 |
| R2 | G0/2 | 192.168.13.2 | 255.255.255.0 | R3 G0/1 |
| R3 | G0/1 | 192.168.13.3 | 255.255.255.0 | R2 G0/2 |
| R3 | G0/0 | 192.168.3.254 | 255.255.255.0 | SW2 (LAN2 gateway) |
| PC2 | NIC | 192.168.3.1 | 255.255.255.0 | SW2 |

**Default gateways:** PC1 → `192.168.1.254`; PC2 → `192.168.3.254`.

---

## 5. Pre-Configuration Checklist

1. Place 3 routers, 2 switches, 2 PCs matching the topology.
2. Cable PC-to-switch and switch-to-router with straight-through copper; router-to-router links use copper straight-through as well (Packet Tracer auto-detects).
3. Confirm interface numbering — this manual uses `Gi0/0`/`Gi0/1` on the 2911s; substitute if your platform differs.
4. Have the address table above open for reference.

---

## 6. Configuration Tasks

### 6.1 R1 — LAN1 Edge Router

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description LAN1 - SW1
R1(config-if)#ip address 192.168.1.254 255.255.255.0
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description To R2
R1(config-if)#ip address 192.168.12.1 255.255.255.0
R1(config-if)#no shutdown
R1(config-if)#exit
```

> **Mode:** Global Config → Interface Config. `ip address` assigns the interface's Layer 3 identity; `no shutdown` is what actually turns the interface on — every physical Cisco interface boots administratively down. **Memory aid:** "address, then wake it up."

**R1's static routes — the routing logic:**

R1 is directly connected to `192.168.1.0/24` and `192.168.12.0/24`. It needs explicit routes to reach everything else: LAN2 (`192.168.3.0/24`) and the R2–R3 transit (`192.168.13.0/24`). Since R1 only has one way out (toward R2), both routes point the same direction:

```text
R1(config)#ip route 192.168.3.0 255.255.255.0 192.168.12.2
R1(config)#ip route 192.168.13.0 255.255.255.0 192.168.12.2
```

> **Mode:** Global Config. `ip route <destination-network> <mask> <next-hop>` — read this right to left: "to reach *this* network, send it to *this* neighbor." The next-hop is always the **next router's interface IP on a network R1 is directly connected to** — never a far-away IP R1 has no path to yet.

```text
R1#copy running-config startup-config
```

---

### 6.2 R2 — Transit Router

```text
Router>enable
Router#configure terminal
Router(config)#hostname R2
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#description To R1
R2(config-if)#ip address 192.168.12.2 255.255.255.0
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface gigabitEthernet 0/2
R2(config-if)#description To R3
R2(config-if)#ip address 192.168.13.2 255.255.255.0
R2(config-if)#no shutdown
R2(config-if)#exit
```

**R2's static routes:**

R2 is directly connected to both transit networks, so it only needs routes to the two **LANs**, which sit one hop beyond each of its interfaces:

```text
R2(config)#ip route 192.168.1.0 255.255.255.0 192.168.12.1
R2(config)#ip route 192.168.3.0 255.255.255.0 192.168.13.3
```

> Notice the direction split: LAN1 traffic goes back toward R1, LAN2 traffic goes forward toward R3. This is the core skill of this lab — **each router's routes are written from its own point of view**, not copy-pasted from another router's config.

```text
R2#copy running-config startup-config
```

---

### 6.3 R3 — LAN2 Edge Router

```text
Router>enable
Router#configure terminal
Router(config)#hostname R3
R3(config)#interface gigabitEthernet 0/1
R3(config-if)#description To R2
R3(config-if)#ip address 192.168.13.3 255.255.255.0
R3(config-if)#no shutdown
R3(config-if)#exit
R3(config)#interface gigabitEthernet 0/0
R3(config-if)#description LAN2 - SW2
R3(config-if)#ip address 192.168.3.254 255.255.255.0
R3(config-if)#no shutdown
R3(config-if)#exit
```

**R3's static routes:**

```text
R3(config)#ip route 192.168.1.0 255.255.255.0 192.168.13.2
R3(config)#ip route 192.168.12.0 255.255.255.0 192.168.13.2
```

R3 mirrors R1's logic exactly — one exit path, so every remote network routes the same direction.

```text
R3#copy running-config startup-config
```

---

### 6.4 SW1, SW2, PC1, PC2

Switches need no VLAN/routing config for this lab (default VLAN 1, all ports access). Configure end hosts via **Desktop → IP Configuration**:

| Field | PC1 | PC2 |
|---|---|---|
| IP Address | 192.168.1.1 | 192.168.3.1 |
| Subnet Mask | 255.255.255.0 | 255.255.255.0 |
| Default Gateway | 192.168.1.254 | 192.168.3.254 |

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip interface brief` | All interfaces `up/up` |
| `show ip route` | Connected (`C`), Local (`L`), and Static (`S`) entries present for every network |
| `ping` (from PC1/PC2) | End-to-end reachability |

### 7.1 Expected Output Gallery

**`R2# show ip route`**

```text
Gateway of last resort is not set

     192.168.1.0/24 [1/0] via 192.168.12.1
C    192.168.12.0/24 is directly connected, GigabitEthernet0/1
L    192.168.12.2/32 is directly connected, GigabitEthernet0/1
     192.168.3.0/24 [1/0] via 192.168.13.3
C    192.168.13.0/24 is directly connected, GigabitEthernet0/2
L    192.168.13.2/32 is directly connected, GigabitEthernet0/2
S    192.168.1.0/24 [1/0] via 192.168.12.1
S    192.168.3.0/24 [1/0] via 192.168.13.3
```

The `S` lines are the ones *you* typed. `C`/`L` are automatic the moment an interface comes up with an IP.

**`PC1> ping 192.168.3.1`**

```text
Pinging 192.168.3.1 with 32 bytes of data:
Reply from 192.168.3.1: bytes=32 time=2ms TTL=125
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125

Ping statistics for 192.168.3.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

TTL of 125 (starting from 128, minus 3 hops: R1, R2, R3) confirms the packet actually traversed all three routers, not a shortcut.

---

## 8. Common Mistakes (the 80/20)

1. **Writing a route with the wrong next-hop** — pointing at a network's *own* gateway instead of the *next router toward it*. The next-hop must always be an IP the current router can already reach directly.
2. **Forgetting a route on the middle router (R2) in one direction only** — R2 needs routes in *both* directions (toward LAN1 and toward LAN2); forgetting one makes the network "half-reachable."
3. **Typo'ing the mask** — `255.255.255.0` vs `255.255.0.0` silently changes which networks match.
4. **Forgetting `no shutdown`** on a freshly configured interface — the single most common error across every lab in this course.
5. **Configuring the route on the wrong router** — e.g., putting R1's LAN2 route on R3 by accident while multitasking across three CLI windows.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Interface `administratively down` | Missing `no shutdown` | `show ip interface brief` | Enter interface, run `no shutdown` |
| 2 | PC can't reach its own gateway | Wrong PC IP/mask, or switch port down | `ipconfig` / `show interfaces status` | Fix PC config or bring up switch port |
| 3 | PC reaches R1 but nothing further | Missing static route on R1 | `show ip route` on R1 | Add the missing `ip route` |
| 4 | Reaches R2 but not R3's LAN | R2 missing route toward LAN2 | `show ip route` on R2 | Add `ip route 192.168.3.0 ... 192.168.13.3` |
| 5 | Return traffic fails (one-way ping) | Route missing on the *return path* router | `show ip route` on the far router | Add the corresponding reverse route |

---

## 10. Design Analysis

Static routing is the correct choice here specifically *because* the topology is a straight line with no redundancy — there's exactly one path between any two networks, so a dynamic protocol would spend CPU cycles and complexity discovering a topology that never changes. The moment a second path appears (e.g., a direct R1–R3 link for redundancy), static routing starts to show its weakness: you'd need floating static routes or a dynamic protocol to handle failover automatically, which is exactly what Day 24 and the OSPF labs build toward.

Using `/24` for the transit links (as this lab's original addressing does) is simple but wasteful — a `/30` would fit the same 2 hosts using 1/64th the address space. Real ISPs and enterprises default to `/30` (or `/31`) on point-to-point links for exactly this reason.

---

## 11. Real-World Parallel

You'd see this exact shape — three routers in a line connecting two edge LANs — in a small office with a routed backbone between two IT closets, or in a lab/test environment simulating a WAN hop. It's also the simplest possible illustration of why routing protocols exist: imagine this same logic at 50 routers instead of 3 — manually writing every route by hand stops being feasible almost immediately.

---

## 12. Stretch Goal

1. Re-address all transit links as `/30` instead of `/24` and rewrite every static route to match.
2. Add a 4th router in parallel between R1 and R3, creating a second path, and observe that static routing alone can't automatically prefer one path over the other without floating static routes (see Day 24).
3. Replace all static routes with a single default route (`ip route 0.0.0.0 0.0.0.0 <next-hop>`) on R1 and R3 only, and explain why that still works even though it's "less precise."

---

## 13. Self-Assessment

- [ ] Can you write, from memory, an `ip route` command and explain each field?
- [ ] Can you explain why R2 needs routes in two different directions?
- [ ] Can you identify `C`, `L`, and `S` in a routing table and explain what created each?
- [ ] Could you re-derive this addressing plan using `/30` transit links instead of `/24`?
- [ ] Can you explain, in one sentence, why static routing is the right choice for exactly this topology?

---

## 14. Key Concepts Demonstrated

- Multi-hop static routing across three routers
- Directional route logic (routes are per-router, not global)
- Routing table source codes (`C`, `L`, `S`)
- End-to-end verification with `ping` and TTL analysis

---

## 15. What I Learned

The biggest shift in this lab versus earlier ones is realizing that a routing table doesn't describe the network — it describes what *that specific router* has been told. R2 doesn't magically know about LAN1 and LAN2 just because they exist; someone has to tell it, twice, once per direction. That "someone" being a human typing `ip route` by hand is exactly the workload that dynamic routing protocols were invented to remove at scale.

---

## 16. Skills Practiced

- Static route configuration and verification
- Multi-hop IPv4 addressing design
- Routing table analysis
- End-to-end connectivity testing and troubleshooting

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2, R3) | Cisco 2911 | VyOS |
| Switches (SW1, SW2) | Cisco 2960 | Open vSwitch |
| PCs (PC1, PC2) | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script. VyOS static route syntax (`set protocols static route <net> next-hop <ip>`) differs from IOS `ip route` — the README includes a translation table.
