# Day 15 Lab Manual — VLSM & Static Routing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Subnet a single `192.168.5.0/24` block using Variable Length Subnet Masking (VLSM) to fit four LANs of different sizes plus one point-to-point link, configure two routers with static routes, and verify full end-to-end reachability. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): IPv4 addressing, subnetting. Domain 4 (IP Connectivity): static routing, `ip route`. VLSM math is one of the highest-yield manual-calculation skills tested on the exam. |
| **Prerequisites** | Day 01 (device roles, basic IOS config), comfort with binary-to-decimal conversion, fixed-length subnetting (`/24` splitting). |
| **Time Estimate** | 2 – 3 hours (first attempt); 30–45 minutes on repeat. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the topology is small, but the VLSM math is unforgiving: one block-size mistake cascades into every subnet after it. |

---

## 1. Lab Overview

VLSM takes a single address block and splits it into subnets of **different sizes**, each sized to what it actually needs, instead of cutting the block into equal pieces the way fixed-length subnetting does. This lab takes `192.168.5.0/24` and carves it into four LANs (45, 64, 14, and 9 hosts) plus one router-to-router point-to-point link, using the smallest block that fits each requirement.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Rank subnetting requirements largest-to-smallest and allocate address blocks without overlap or waste
- Derive host bits, prefix length, and dotted-decimal mask by hand from a host-count requirement
- Calculate network address, first/last usable host, and broadcast address for any subnet by hand
- Configure router interfaces and static routes to connect VLSM-subnetted LANs
- Verify routing tables and end-to-end reachability across multiple subnet sizes

---

## 2. Business Context

**Why would a real company do this?**

Imagine four departments sharing one small ISP-assigned block, `192.168.5.0/24` — 254 usable addresses total. Sales has 45 people. Engineering has grown to 64 (the biggest team). A server closet needs 14 addresses (servers + management interfaces). A small satellite team needs 9. If you handed every department an equal `/26` (62 hosts), Engineering wouldn't fit (over 62) and the satellite team would waste 53 addresses it will never use. VLSM is the tool that makes "one block, four differently-sized departments" actually work — this is the exact math a network engineer does before requesting address space from an ISP or before carving up an internal RFC 1918 allocation, and it's tested this explicitly on the CCNA because it comes up constantly in the field: every time a company's total address budget is finite (it always is) and its departments aren't uniformly sized (they never are).

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-15-Lab-VLSM.png" alt="Day 15 VLSM Topology" width="800">
</p>

```text
PC1 (LAN1) --\
              R1 --- P2P link --- R2
PC2 (LAN2) --/                        \
                                        PC3 (LAN3)
                                        PC4 (LAN4)
```

| Device | Role |
|---|---|
| R1 | Router — hosts LAN1 (PC1) and LAN2 (PC2), one end of the P2P link |
| R2 | Router — hosts LAN3 (PC3) and LAN4 (PC4), other end of the P2P link |
| PC1–PC4 | End hosts, one per LAN |

---

## 4. IP Addressing Plan

### 4.1 Why VLSM Instead of a Fixed Split

A fixed `/26` split of `192.168.5.0/24` gives exactly four equal blocks of 62 usable hosts each. That fails immediately: LAN2 needs 64 hosts, which doesn't fit in 62. VLSM instead **sizes each subnet independently, largest requirement first**, so no block is bigger than it needs to be and none is too small to fit its requirement.

| Network | Hosts Needed | Purpose |
|---|---:|---|
| LAN 2 | 64 | PC2 network |
| LAN 1 | 45 | PC1 network |
| LAN 3 | 14 | PC3 network |
| LAN 4 | 9  | PC4 network |
| P2P   | 2  | R1 ↔ R2 link |

**Rule:** always allocate largest-to-smallest. If you allocate small subnets first, a later large requirement may not fit in the remaining fragmented space — the classic VLSM mistake.

### 4.2 Manual Calculation Walkthrough

**Step 1 — Solve host bits for each requirement using `usable hosts = 2^h − 2`.**

| Requirement | Test | Host bits (h) | Prefix | Usable hosts |
|---|---|---|---|---|
| 64 | 2⁶−2=62 (too small) → 2⁷−2=126 | 7 | /25 | 126 |
| 45 | 2⁵−2=30 (too small) → 2⁶−2=62 | 6 | /26 | 62 |
| 14 | 2⁴−2=14 (exact fit) | 4 | /28 | 14 |
| 9  | 2³−2=6 (too small) → 2⁴−2=14 | 4 | /28 | 14 |
| 2  | 2¹−2=0 (too small) → 2²−2=2 | 2 | /30 | 2 |

**Step 2 — Convert each prefix to a dotted-decimal mask** (32 − h bits of 1, rest 0):

| Prefix | Binary (last octet) | Mask |
|---|---|---|
| /25 | 1000000 → 1**0000000** | 255.255.255.**128** |
| /26 | 11000000 | 255.255.255.**192** |
| /28 | 11110000 | 255.255.255.**240** |
| /30 | 11111100 | 255.255.255.**252** |

Shortcut used throughout this course: **last-octet mask value = 256 − 2^h**. For /25: 256−128=128. For /26: 256−64=192. For /28: 256−16=240. For /30: 256−4=252.

**Step 3 — Allocate blocks in descending size order, starting at `192.168.5.0`, snapping each subnet to its own block-size boundary.**

Block size = 256 − mask's last octet. A subnet's network address must be a multiple of its own block size.

| Order | Subnet | Block size | Network | Range | Broadcast |
|---|---|---|---|---|---|
| 1 (LAN2, /25) | 192.168.5.**0**/25 | 128 | .0 | .1–.126 | .127 |
| 2 (LAN1, /26) | 192.168.5.**128**/26 | 64 | .128 | .129–.190 | .191 |
| 3 (LAN3, /28) | 192.168.5.**192**/28 | 16 | .192 | .193–.206 | .207 |
| 4 (LAN4, /28) | 192.168.5.**208**/28 | 16 | .208 | .209–.222 | .223 |
| 5 (P2P, /30) | 192.168.5.**224**/30 | 4 | .224 | .225–.226 | .227 |

Each network's starting address is the previous subnet's broadcast address + 1 — this is what "no wasted space, no overlap" looks like when VLSM is done correctly. `.228`–`.255` remain unused, reserved for future growth.

**Worked example — deriving LAN1 (192.168.5.128/26) by hand:**

```text
Network address:   192.168.5.128   (all 6 host bits = 0)
First usable host: 192.168.5.129   (network + 1)
Last usable host:  192.168.5.190   (broadcast − 1)
Broadcast address: 192.168.5.191   (all 6 host bits = 1 → 128 + 63)
```

**Worked example — deriving the P2P link (192.168.5.224/30) by hand:**

```text
Network address:   192.168.5.224   (all 2 host bits = 0)
First usable host: 192.168.5.225   (R1 side)
Last usable host:  192.168.5.226   (R2 side)
Broadcast address: 192.168.5.227   (all 2 host bits = 1)
```

### 4.3 Address Assignment Convention

Per the lab objectives: **PCs get the first usable address** in their subnet, **routers get the last usable address** (the gateway). This is a deliberate convention (not the only valid one) that makes it easy to eyeball, at a glance, which address in any subnet is the gateway.

### 4.4 Full Device Address Table

| Device | Interface | IP Address | Mask | Subnet | Connects To |
|---|---|---|---|---|---|
| PC2 | NIC | 192.168.5.1 | 255.255.255.**128** | LAN2 /25 | R1 Gi0/1 |
| R1 | Gi0/1 | 192.168.5.126 | 255.255.255.128 | LAN2 /25 | PC2 (gateway) |
| PC1 | NIC | 192.168.5.129 | 255.255.255.**192** | LAN1 /26 | R1 Gi0/0 |
| R1 | Gi0/0 | 192.168.5.190 | 255.255.255.192 | LAN1 /26 | PC1 (gateway) |
| PC3 | NIC | 192.168.5.193 | 255.255.255.**240** | LAN3 /28 | R2 Gi0/0 |
| R2 | Gi0/0 | 192.168.5.206 | 255.255.255.240 | LAN3 /28 | PC3 (gateway) |
| PC4 | NIC | 192.168.5.209 | 255.255.255.**240** | LAN4 /28 | R2 Gi0/1 |
| R2 | Gi0/1 | 192.168.5.222 | 255.255.255.240 | LAN4 /28 | PC4 (gateway) |
| R1 | Gi0/0/0 | 192.168.5.225 | 255.255.255.**252** | P2P /30 | R2 Gi0/0/0 |
| R2 | Gi0/0/0 | 192.168.5.226 | 255.255.255.252 | P2P /30 | R1 Gi0/0/0 |

---

## 5. Pre-Configuration Checklist

1. Place R1, R2, and PC1–PC4 in the topology matching Section 3.
2. Cable PC1/PC2 to R1's LAN interfaces, PC3/PC4 to R2's LAN interfaces, and R1↔R2 directly for the P2P link.
3. Have the address table above open for reference — VLSM labs are where addressing typos cost the most time.
4. Confirm each router's actual interface names (`Gi0/0`, `Gi0/1`, `Gi0/0/0`, or `Fa` equivalents) match your platform.

---

## 6. Configuration Tasks

### 6.1 R1 — LAN1, LAN2, and the P2P link

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description LAN1 - PC1
R1(config-if)#ip address 192.168.5.190 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description LAN2 - PC2
R1(config-if)#ip address 192.168.5.126 255.255.255.128
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/0/0
R1(config-if)#description P2P to R2
R1(config-if)#ip address 192.168.5.225 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
```

- **Mode:** Global Config → Interface Config for each of the three interfaces.
- Every physical interface boots administratively down — **`no shutdown`** is what actually brings the link up; this is the single most common point of failure in this lab (see Common Mistakes #1).
- The mask on each interface must match the VLSM plan **exactly** — a `/26` typed as `/24` silently breaks the subnet boundary and every host on it.
- **Memory aid:** "PCs get first, routers get last" — if you type an IP ending in an even-looking round number like `.128` or `.192` on a router interface, stop: those are network addresses, not usable host addresses, and IOS will reject them.

### 6.2 R2 — LAN3, LAN4, and the P2P link

```text
Router>enable
Router#configure terminal
Router(config)#hostname R2
R2(config)#interface gigabitEthernet 0/0
R2(config-if)#description LAN3 - PC3
R2(config-if)#ip address 192.168.5.206 255.255.255.240
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#description LAN4 - PC4
R2(config-if)#ip address 192.168.5.222 255.255.255.240
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface gigabitEthernet 0/0/0
R2(config-if)#description P2P to R1
R2(config-if)#ip address 192.168.5.226 255.255.255.252
R2(config-if)#no shutdown
R2(config-if)#exit
```

### 6.3 PC Addressing

| PC | IP Address | Mask | Default Gateway |
|---|---|---|---|
| PC1 | 192.168.5.129 | 255.255.255.192 | 192.168.5.190 |
| PC2 | 192.168.5.1   | 255.255.255.128 | 192.168.5.126 |
| PC3 | 192.168.5.193 | 255.255.255.240 | 192.168.5.206 |
| PC4 | 192.168.5.209 | 255.255.255.240 | 192.168.5.222 |

Configure each via **Desktop → IP Configuration**. A wrong mask here is the second most common VLSM mistake — it makes the PC believe part of its own subnet, or a neighboring one, is "off-subnet" when it isn't (or vice versa).

### 6.4 Static Routes

Each router needs a route to the two remote LANs it isn't directly connected to.

```text
R1(config)#ip route 192.168.5.192 255.255.255.240 192.168.5.226
R1(config)#ip route 192.168.5.208 255.255.255.240 192.168.5.226
```

```text
R2(config)#ip route 192.168.5.0 255.255.255.128 192.168.5.225
R2(config)#ip route 192.168.5.128 255.255.255.192 192.168.5.225
```

> **Syntax:** `ip route <destination-network> <subnet-mask> <next-hop>`. The next-hop is always the *other router's* P2P interface address — never a LAN address, since the P2P link is the only path between R1 and R2. **Memory aid:** "route to the network, hop to the neighbor" — the first two arguments describe *where you're trying to go*, the third describes *who to ask next*.

### 6.5 Save

```text
R1#copy running-config startup-config
R2#copy running-config startup-config
```

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| R1, R2 | `show ip interface brief` | All configured interfaces `up/up` with correct IPs |
| R1, R2 | `show ip route` | Connected subnets + 2 static routes on each router |
| PC1–PC4 | `ipconfig` | Correct IP/mask/gateway per Section 6.3 |
| Any PC | `ping <gateway>` | Local LAN connectivity |
| Any PC | `ping <remote PC>` | Full routed path across the P2P link |

### 7.1 Expected Output Gallery

**`R1# show ip interface brief`**

```text
Interface                  IP-Address       OK? Method Status                Protocol
GigabitEthernet0/0         192.168.5.190    YES manual up                    up
GigabitEthernet0/1         192.168.5.126    YES manual up                    up
GigabitEthernet0/0/0       192.168.5.225    YES manual up                    up
```

**`R1# show ip route`**

```text
      192.168.5.0/24 is variably subnetted, 6 subnets, 4 masks
C        192.168.5.0/25 is directly connected, GigabitEthernet0/1
C        192.168.5.128/26 is directly connected, GigabitEthernet0/0
S        192.168.5.192/28 [1/0] via 192.168.5.226
S        192.168.5.208/28 [1/0] via 192.168.5.226
C        192.168.5.224/30 is directly connected, GigabitEthernet0/0/0
```

The `variably subnetted ... 4 masks` line is IOS explicitly telling you this is a VLSM design — a single major network (`192.168.5.0/24`) broken into subnets of different prefix lengths. This line does **not** appear in a fixed-length subnetting lab.

**`PC1> ping 192.168.5.209`** (PC1 → PC4, full path across both routers)

```text
Pinging 192.168.5.209 with 32 bytes of data:

Reply from 192.168.5.209: bytes=32 time=2ms TTL=126
Reply from 192.168.5.209: bytes=32 time=1ms TTL=126
Reply from 192.168.5.209: bytes=32 time=1ms TTL=126
Reply from 192.168.5.209: bytes=32 time=1ms TTL=126

Ping statistics for 192.168.5.209:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

TTL of 126 (started at 128, minus 2 router hops) confirms the packet actually crossed both R1 and R2 rather than being answered locally.

---

## 8. Common Mistakes (the 80/20)

1. **Allocating subnets smallest-first instead of largest-first.** This is the #1 VLSM-specific error — it fragments the address space so the largest requirement no longer fits, forcing a redo of the entire plan.
2. **Forgetting `no shutdown`** on a freshly configured router interface — same as every IOS lab, and still the single most common reason `show ip interface brief` disappoints.
3. **Typing the wrong mask for a subnet** (e.g., using `/26` on the P2P link instead of `/30`) — wastes address space and can silently break which addresses IOS considers "on-link."
4. **Off-by-one errors on network/broadcast addresses** — assigning `.128` (the network address) or `.191` (the broadcast) to a device instead of a usable host address. IOS will reject an interface configured with a network or broadcast address, but a *PC* often won't complain until you try to actually communicate.
5. **Static route destination doesn't match the subnet exactly** — typing `192.168.5.192 255.255.255.0` instead of `255.255.255.240` either matches too much or fails to match the intended subnet at all.
6. **Pointing the static route next-hop at a LAN address instead of the P2P interface** — there is only one path between R1 and R2, and it's the P2P link; the next-hop must always be the neighbor's P2P address.
7. **Not re-deriving the block size after changing one requirement.** If you resize LAN2's host requirement mid-lab, every subnet allocated after it needs to be re-checked against the new boundary — VLSM allocations are sequential and dependent on what came before.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Interface `administratively down` | Missing `no shutdown` | `show ip interface brief` | Enter interface, run `no shutdown` |
| 2 | PC can't reach its own gateway | Wrong IP/mask on PC, or mismatched mask vs. router interface | `ipconfig` (PC), `show ip interface brief` (router) | Re-check both ends against Section 4.4 |
| 3 | PC reaches gateway but not the other LAN on the *same* router | Missing `no shutdown` on the second LAN interface, or wrong mask | `show ip interface brief` | Bring up/re-check the second interface |
| 4 | PC can't reach a PC on the *other* router | Missing or incorrect static route | `show ip route` | Add/correct the `ip route` statement, verify mask matches exactly |
| 5 | `show ip route` shows the static route but ping still fails | Next-hop unreachable (P2P link down) | `show ip interface brief` on the P2P interfaces | Bring up the P2P link on both ends |
| 6 | Everything up, routes present, still no ping | Return-path route missing on the *other* router | `show ip route` on both routers | Static routes are not automatically bidirectional — configure both directions |

---

## 10. Design Analysis

**Why VLSM over four separate `/24`s (or four public blocks)?** A company is rarely handed unlimited address space. VLSM makes one allocated block do the work of four, sized honestly to what each segment needs — this is directly why the CCNA weights subnetting so heavily: it's the daily skill of "make a finite resource fit a real requirement."

**Why largest-first allocation?** Allocating smallest-first can strand a later large requirement in a fragmented remainder that's too small to hold it, forcing a full redesign. Largest-first guarantees every later, smaller allocation always has room, because smaller blocks fit into whatever space remains.

**Why "PCs get first usable, routers get last usable"?** This is a convention, not a technical requirement — but a consistent one, applied lab-wide, makes every address table self-documenting: anyone glancing at an IP ending near the top of a range instantly knows it's a gateway.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...your company gets a single `/24` from an ISP and IT needs to carve it across Engineering, Sales, a server room, and a small branch — exactly this lab's four-LAN shape.
- ...you inherit a network where someone subnetted everything as equal `/26`s and a department outgrows its 62-host ceiling — you'll need to VLSM-replan around the existing allocations without breaking what's already running.
- ...you're studying for the CCNA exam itself: VLSM math (deriving host bits, mask, and the four key addresses by hand, under time pressure) is one of the single highest-frequency question types on the real exam.

---

## 12. Stretch Goal

1. Add a fifth requirement — a 100-host LAN — to the existing `192.168.5.0/24` plan. Does it still fit after the five subnets already allocated? Show your math.
2. Re-derive the entire plan starting from `10.0.0.0/22` (a much larger block) sized for LANs of 500, 200, 50, and 10 hosts, plus 3 P2P links.
3. Convert one of the two static routes on R1 into a default route (`0.0.0.0 0.0.0.0`) pointing at R2, and explain in writing why that only works safely if R2 has no other exit path of its own.

---

## 13. Self-Assessment

- [ ] Can you derive host bits from a host-count requirement using `2^h − 2` without a calculator?
- [ ] Can you convert a prefix length to a dotted-decimal mask from binary, not memory, for at least one non-classful prefix?
- [ ] Can you explain why VLSM allocations must proceed largest-to-smallest?
- [ ] Can you compute network, first-usable, last-usable, and broadcast addresses for a `/28` by hand?
- [ ] Can you write the two-line static route pair needed on each router in this topology, from memory?
- [ ] Can you explain what "variably subnetted ... N masks" in `show ip route` means and why it appears here?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** VLSM allocation order, host-bit derivation, block-size subnet boundaries, static routing between VLSM subnets, first/last-usable addressing convention.

**What I Learned:** VLSM is really just fixed-length subnetting applied repeatedly and independently to each requirement, provided you always allocate from largest to smallest so no later requirement gets stranded. The math (`2^h − 2`, mask-from-prefix, block-size boundaries) is mechanical once practiced, but a single earlier mistake compounds into every subnet that follows — which is exactly why laying out the full plan on paper before touching a router CLI is non-negotiable.

**Skills Practiced:** VLSM planning, manual subnetting math, router interface configuration, static routing across VLSM boundaries, routing table verification, end-to-end connectivity testing.

---

## 15. GNS3 Lab

A companion GNS3 build is provided in [`GNS3/build_lab.py`](GNS3/build_lab.py) — see [`GNS3/README.md`](GNS3/README.md) for usage. It maps R1/R2 to VyOS and PC1–PC4 to Alpine Linux (no switches needed; each PC connects directly to its router's LAN interface in this topology, matching the Packet Tracer original).
