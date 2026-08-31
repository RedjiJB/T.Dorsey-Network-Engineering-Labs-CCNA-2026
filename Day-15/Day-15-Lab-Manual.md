# Day 15 Lab Manual — VLSM & Static Routing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Subnet a single `192.168.5.0/24` block using Variable Length Subnet Masking (VLSM) to fit four LANs of different sizes plus one point-to-point link, configure two routers with static routes, and verify end-to-end connectivity across every subnet. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): IPv4 addressing, subnetting math, subnet masks. Domain 4 (IP Connectivity): static routing, routing table interpretation. VLSM is one of the highest-yield calculation topics on the exam — expect multiple subnetting questions that require exactly this workflow, often under time pressure. |
| **Prerequisites** | Comfort with binary/decimal conversion, fixed-length subnetting (dividing a network into equal-sized blocks), basic Cisco IOS interface and static route syntax (Day 01–Day 02 material). |
| **Time Estimate** | 2 – 3 hours (first attempt, including working the math by hand); 30–45 minutes on repeat/review. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the CLI configuration itself is simple; the difficulty is entirely in getting the VLSM math right, in order, without a calculator. |

---

## 1. Lab Overview

This lab takes a single `/24` block — `192.168.5.0/24` — and carves it into five subnets of very different sizes using VLSM, instead of splitting it into equal fixed-length chunks the way Day 14 (fixed-length subnetting) did. VLSM is what lets a network engineer avoid wasting addresses: a LAN that needs 9 hosts should not be handed the same 254-address block as a LAN that needs 64.

Two routers, **R1** and **R2**, each terminate two LANs and are connected to each other over a dedicated point-to-point link. Four PCs — one per LAN — sit behind their router's gateway interface. Every device's address, and every router's route table, has to be derived by hand from the host-count requirements below, in a specific order, or the whole addressing plan collapses into overlapping subnets.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain why VLSM allocates the *largest* subnet requirement first, and predict what breaks if you allocate out of order
- Convert a host-count requirement into the correct number of host bits, prefix length, and dotted-decimal subnet mask, entirely by hand
- Calculate the network address, first usable host, last usable host, and broadcast address for any subnet without a calculator
- Use the block-size shortcut to place each subsequent subnet on a valid boundary with zero wasted math
- Configure router sub-interfaces/interfaces and a point-to-point link to match a VLSM plan
- Write and verify static routes connecting non-adjacent LANs across two routers
- Read `show ip route` output and distinguish connected, local, and static route entries
- Diagnose the most common VLSM-specific configuration mistakes (misaligned block boundaries, wrong mask on the wrong subnet, off-by-one host addresses)

---

## 2. Business Context

**Why would a real company do this?**

Imagine your company was handed exactly one `/24` block — `192.168.5.0/24` — by whoever manages IP allocation (a parent company's IT department, a colo provider, or your own address-planning policy), and told "make this work for the whole floor." On that floor:

- **Sales (45 people)** needs its own LAN — printers, laptops, VoIP phones included.
- **Engineering (64 people)** is the largest team on the floor and needs the most room.
- **A small ops closet (14 devices)** — switches, APs, a couple of management hosts — needs a LAN too, but a tiny one.
- **A handful of lab/test devices (9 hosts)** needs isolation from production but doesn't need much space.
- **The two closet routers serving these LANs need to talk to each other** over a private link that will never have more than 2 devices on it.

If you naively split `192.168.5.0/24` into four equal `/26` blocks (64 addresses each), Engineering's 64-host requirement barely fits (62 usable — not even enough!) while the 9-host lab network wastes 53 addresses it will never use. Multiply that waste across every floor of every building in a real enterprise and you've burned through address space you can't get back without a renumbering project — which is exactly the kind of expensive, disruptive work senior engineers get paged for. VLSM is the discipline that prevents this: **give every subnet exactly what it needs, size-order it correctly, and nothing is wasted.**

This is also precisely the skill tested when a client hands you "here's your one supernet, make the site plan work" — a scenario every network engineer hits during their first real allocation request.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-15-Lab-VLSM.png" alt="Day 15 VLSM Network Topology" width="900">
</p>

### 3.1 Traffic Flow Summary

```text
LAN 1 (PC1) -- R1 Gi0/0
LAN 2 (PC2) -- R1 Gi0/1
                              R1 Gi0/0/0 -- [Point-to-Point] -- Gi0/0/0 R2
LAN 3 (PC3) -- R2 Gi0/0
LAN 4 (PC4) -- R2 Gi0/1
```

### 3.2 Equipment List

| Role      | Device            | Model              | Hostname Used Below |
|-----------|-------------------|---------------------|----------------------|
| Router    | R1                | Cisco 4321/2911     | `R1`                 |
| Router    | R2                | Cisco 4321/2911     | `R2`                 |
| PC        | PC1 (LAN 1)       | Generic PC          | `PC1`                 |
| PC        | PC2 (LAN 2)       | Generic PC          | `PC2`                 |
| PC        | PC3 (LAN 3)       | Generic PC          | `PC3`                 |
| PC        | PC4 (LAN 4)       | Generic PC          | `PC4`                 |

> **Note on realism:** This lab is pre-VLAN and pre-dynamic-routing (both are later topics). Each router's LAN interfaces connect directly to a single PC's network segment for simplicity — in a real deployment each of these would be a switched LAN with many hosts, but the addressing math scales identically regardless of how many devices actually populate the LAN.

---

## 4. IP Addressing Plan (VLSM)

This is the core of the lab. Read this section slowly and do the math yourself alongside it — do not just copy the final table.

### 4.1 The Requirements

| Network        | Host Requirement | Purpose       |
|----------------|------------------:|---------------|
| LAN 1          |          45 Hosts | PC1 Network   |
| LAN 2          |          64 Hosts | PC2 Network   |
| LAN 3          |          14 Hosts | PC3 Network   |
| LAN 4          |           9 Hosts | PC4 Network   |
| Point-to-Point |           2 Hosts | R1 ↔ R2 Link  |

Supernet to subnet: `192.168.5.0/24` (256 total addresses, 254 usable in the whole block before subdividing).

### 4.2 Why VLSM Allocates Largest-First

This is the single most important rule in this entire lab, and it's not arbitrary — it's a consequence of how binary block boundaries work.

Every subnet of prefix length `/n` must start on an address that's a multiple of its own block size (`256 − mask-last-octet` for masks in the last octet, or the equivalent power-of-two math for masks that fall in earlier octets). If you allocate a **small** subnet first, you plant a small "island" wherever you happen to be in the address space — and the very next subnet you carve, if it needs to be **larger** than the gap remaining before or after that island, will not align on a valid boundary anymore. You'd either have to leave a gap of wasted addresses to re-align, or the plan breaks entirely and subnets overlap.

Allocating **largest-first** avoids this completely: each subnet consumes a contiguous block starting exactly where the previous one's block ended, and because you're always placing the *next-most-restrictive* requirement, the address space never needs a realignment gap. This is why the rule is: **sort every requirement from most hosts to fewest, and assign blocks in that order, starting from the beginning of your supernet.**

Sorted order for this lab: **LAN 2 (64) → LAN 1 (45) → LAN 3 (14) → LAN 4 (9) → Point-to-Point (2)**.

### 4.3 Step-by-Step Manual Math for Every Subnet

**The core formula**, used identically for every subnet below:

```text
usable hosts = 2^h − 2
```

`h` = host bits (bits left over after the network portion). The `−2` removes the network address and broadcast address, which are never assignable to a device. To size a subnet, find the *smallest* `h` that satisfies `2^h − 2 ≥ requirement` — using more host bits than necessary wastes addresses; using fewer doesn't fit.

---

#### Subnet 1 — LAN 2 (64 hosts) — allocated first, largest

```text
2^h − 2 ≥ 64
2^6 − 2 = 62   → too small
2^7 − 2 = 126  → fits (with room to spare — 64 does not land on an exact power of 2 minus 2)
```

`h = 7` host bits → prefix length = `32 − 7 = /25`.

**Binary → decimal mask derivation:**

```text
/25 = 11111111.11111111.11111111.10000000
    =     255  .    255 .    255 .   128
```

**Placement:** This is the first block allocated, so it starts at the beginning of the supernet: `192.168.5.0`.

```text
Network address:    192.168.5.0      (all 7 host bits = 0000000)
First usable host:  192.168.5.1      (network address + 1)  → assigned to PC2
Last usable host:   192.168.5.126    (broadcast − 1)          → assigned to R1 Gi0/1 (gateway)
Broadcast address:  192.168.5.127    (all 7 host bits = 1111111)
```

**Block size check:** block size = `256 − 128 = 128`. `/25` subnets land on multiples of 128 (`.0`, `.128`). `192.168.5.0` is a valid boundary. ✅

**Next block starts at:** `192.168.5.0 + 128 = 192.168.5.128`.

---

#### Subnet 2 — LAN 1 (45 hosts) — allocated second

```text
2^h − 2 ≥ 45
2^5 − 2 = 30   → too small
2^6 − 2 = 62   → fits
```

`h = 6` host bits → prefix length = `32 − 6 = /26`.

**Binary → decimal mask derivation:**

```text
/26 = 11111111.11111111.11111111.11000000
    =     255  .    255 .    255 .   192
```

**Placement:** Starts where Subnet 1's block ended: `192.168.5.128`.

```text
Network address:    192.168.5.128    (all 6 host bits = 000000)
First usable host:  192.168.5.129    (network address + 1)  → assigned to PC1
Last usable host:   192.168.5.190    (broadcast − 1)          → assigned to R1 Gi0/0 (gateway)
Broadcast address:  192.168.5.191    (all 6 host bits = 111111)
```

**Block size check:** block size = `256 − 192 = 64`. `/26` subnets land on multiples of 64 (`.0, .64, .128, .192`). `192.168.5.128` is a valid multiple of 64. ✅

**Next block starts at:** `192.168.5.128 + 64 = 192.168.5.192`.

---

#### Subnet 3 — LAN 3 (14 hosts) — allocated third

```text
2^h − 2 ≥ 14
2^3 − 2 = 6    → too small
2^4 − 2 = 14   → fits exactly (no waste at all — 14 is a perfect 2^h − 2 value)
```

`h = 4` host bits → prefix length = `32 − 4 = /28`.

**Binary → decimal mask derivation:**

```text
/28 = 11111111.11111111.11111111.11110000
    =     255  .    255 .    255 .   240
```

**Placement:** Starts where Subnet 2's block ended: `192.168.5.192`.

```text
Network address:    192.168.5.192    (all 4 host bits = 0000)
First usable host:  192.168.5.193    (network address + 1)  → assigned to PC3
Last usable host:   192.168.5.206    (broadcast − 1)          → assigned to R2 Gi0/0 (gateway)
Broadcast address:  192.168.5.207    (all 4 host bits = 1111)
```

**Block size check:** block size = `256 − 240 = 16`. `/28` subnets land on multiples of 16 (`.0, .16, .32 ... .192, .208`). `192.168.5.192` is a valid multiple of 16. ✅

**Next block starts at:** `192.168.5.192 + 16 = 192.168.5.208`.

---

#### Subnet 4 — LAN 4 (9 hosts) — allocated fourth

```text
2^h − 2 ≥ 9
2^3 − 2 = 6    → too small
2^4 − 2 = 14   → fits
```

`h = 4` host bits → prefix length = `32 − 4 = /28` (same size class as LAN 3, coincidentally — VLSM doesn't require every subnet to be a different size, only that each is the smallest size that fits its own requirement).

**Binary → decimal mask derivation:** identical to Subnet 3 — `255.255.255.240`.

**Placement:** Starts where Subnet 3's block ended: `192.168.5.208`.

```text
Network address:    192.168.5.208    (all 4 host bits = 0000)
First usable host:  192.168.5.209    (network address + 1)  → assigned to PC4
Last usable host:   192.168.5.222    (broadcast − 1)          → assigned to R2 Gi0/1 (gateway)
Broadcast address:  192.168.5.223    (all 4 host bits = 1111)
```

**Block size check:** block size = `16`. `192.168.5.208` is a valid multiple of 16 (`.208 = 13 × 16`). ✅

**Next block starts at:** `192.168.5.208 + 16 = 192.168.5.224`.

---

#### Subnet 5 — Point-to-Point R1 ↔ R2 (2 hosts) — allocated last, smallest

```text
2^h − 2 ≥ 2
2^1 − 2 = 0    → too small
2^2 − 2 = 2    → fits exactly
```

`h = 2` host bits → prefix length = `32 − 2 = /30`.

**Binary → decimal mask derivation:**

```text
/30 = 11111111.11111111.11111111.11111100
    =     255  .    255 .    255 .   252
```

**Placement:** Starts where Subnet 4's block ended: `192.168.5.224`.

```text
Network address:    192.168.5.224    (all 2 host bits = 00)
First usable host:  192.168.5.225    (network address + 1)  → assigned to R1 Gi0/0/0
Last usable host:   192.168.5.226    (broadcast − 1)          → assigned to R2 Gi0/0/0
Broadcast address:  192.168.5.227    (all 2 host bits = 11)
```

**Block size check:** block size = `256 − 252 = 4`. `/30` subnets land on multiples of 4 (`.0, .4, .8 ... .224`). `192.168.5.224` is a valid multiple of 4 (`224 = 56 × 4`). ✅

**Remaining address space:** `192.168.5.228` through `192.168.5.255` (28 addresses) is left unused — this is normal and expected. VLSM does not have to consume every single address in the supernet; it only has to fit every stated requirement without overlap. This leftover space is exactly what you'd hand out to the *next* new LAN that shows up on this floor.

### 4.4 Memory Aid — the Mask/Host-Bit Table

Memorize this instead of re-deriving every mask from scratch on the exam:

| Prefix | Host bits | Usable hosts | Last octet (decimal) | Block size |
|---|---|---|---|---|
| /25 | 7 | 126 | .128 | 128 |
| /26 | 6 | 62  | .192 | 64  |
| /27 | 5 | 30  | .224 | 32  |
| /28 | 4 | 14  | .240 | 16  |
| /29 | 3 | 6   | .248 | 8   |
| /30 | 2 | 2   | .252 | 4   |

Notice two shortcuts that hold for every row: **last-octet value = `256 − 2^h`**, and **block size = `256 − last-octet value`** (equivalently, block size = `2^h`). Once you have the host-bit count from the `2^h − 2 ≥ requirement` formula, both the mask and the block size fall out immediately — you never need to write out full binary octets in a time-pressured exam setting once this table is memorized.

### 4.5 Full VLSM Allocation Table

| Order | Network | Requirement | Host bits | Prefix | Mask | Network Addr | First Usable | Last Usable | Broadcast |
|---|---|---:|---:|---|---|---|---|---|---|
| 1 | LAN 2 | 64 | 7 | /25 | 255.255.255.128 | 192.168.5.0   | 192.168.5.1   | 192.168.5.126 | 192.168.5.127 |
| 2 | LAN 1 | 45 | 6 | /26 | 255.255.255.192 | 192.168.5.128 | 192.168.5.129 | 192.168.5.190 | 192.168.5.191 |
| 3 | LAN 3 | 14 | 4 | /28 | 255.255.255.240 | 192.168.5.192 | 192.168.5.193 | 192.168.5.206 | 192.168.5.207 |
| 4 | LAN 4 | 9  | 4 | /28 | 255.255.255.240 | 192.168.5.208 | 192.168.5.209 | 192.168.5.222 | 192.168.5.223 |
| 5 | P2P   | 2  | 2 | /30 | 255.255.255.252 | 192.168.5.224 | 192.168.5.225 | 192.168.5.226 | 192.168.5.227 |

### 4.6 Full Device Address Table

Per the lab's convention: **PCs get the first usable address in their subnet; router LAN interfaces (gateways) get the last usable address.** This is the reverse of the "gateway = .1" convention you may have seen elsewhere — pay close attention, because muscle memory from other labs will actively work against you here.

| Device | Interface | IP Address    | Mask            | Connects To |
|--------|-----------|---------------|------------------|-------------|
| PC1    | NIC       | 192.168.5.129 | 255.255.255.192  | R1 Gi0/0    |
| R1     | Gi0/0     | 192.168.5.190 | 255.255.255.192  | PC1 (LAN 1) |
| PC2    | NIC       | 192.168.5.1   | 255.255.255.128  | R1 Gi0/1    |
| R1     | Gi0/1     | 192.168.5.126 | 255.255.255.128  | PC2 (LAN 2) |
| R1     | Gi0/0/0   | 192.168.5.225 | 255.255.255.252  | R2 Gi0/0/0  |
| R2     | Gi0/0/0   | 192.168.5.226 | 255.255.255.252  | R1 Gi0/0/0  |
| PC3    | NIC       | 192.168.5.193 | 255.255.255.240  | R2 Gi0/0    |
| R2     | Gi0/0     | 192.168.5.206 | 255.255.255.240  | PC3 (LAN 3) |
| PC4    | NIC       | 192.168.5.209 | 255.255.255.240  | R2 Gi0/1    |
| R2     | Gi0/1     | 192.168.5.222 | 255.255.255.240  | PC4 (LAN 4) |

**Default gateways:** PC1 → `192.168.5.190`; PC2 → `192.168.5.126`; PC3 → `192.168.5.206`; PC4 → `192.168.5.222`.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Place R1, R2, and PC1–PC4 in Packet Tracer matching the topology image, cabling each PC directly to its router's assigned LAN interface and R1 to R2 via a serial or Gigabit Ethernet link (whichever your platform's WIC/port availability supports — this manual uses `Gi0/0/0` on both ends).
2. Verify link lights are green/active on every connection before configuring anything.
3. Have Section 4.6's address table open in a second window — do not try to hold ten IP addresses in your head while typing.
4. Double-check your router's actual interface names (`GigabitEthernet0/0` vs `FastEthernet0/0` vs `Serial0/0/0`) match what's used below; substitute if your platform differs.

---

## 6. Configuration Tasks

### 6.1 R1 — Basic Setup and Hardening

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
R1(config)#no ip domain-lookup
R1(config)#enable secret class
R1(config)#service password-encryption
R1(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. R1 - Authorized Use Only.
#
```

> **Mode:** User EXEC → Privileged EXEC → Global Config. `hostname` renames the device so its prompt is unambiguous once you're juggling R1 and R2 output side by side. `no ip domain-lookup` stops the router from trying to DNS-resolve every mistyped command, which otherwise causes an ~30 second hang each time you fat-finger something — a real time cost when you're re-typing VLSM masks under pressure. `enable secret` sets an MD5-hashed privileged-mode password (always prefer this over the plaintext `enable password`). `service password-encryption` weakly obscures remaining plaintext passwords in the config so a shoulder-surfed `show run` doesn't hand one over in clear text.

### 6.2 R1 — LAN Interfaces (Gi0/0 → LAN 1, Gi0/1 → LAN 2)

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description LAN 1 - PC1 Gateway
R1(config-if)#ip address 192.168.5.190 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description LAN 2 - PC2 Gateway
R1(config-if)#ip address 192.168.5.126 255.255.255.128
R1(config-if)#no shutdown
R1(config-if)#exit
```

> **Mode:** Global Config → Interface Config. `ip address <ip> <mask>` assigns the interface's Layer 3 identity — this must be the **last usable address** in each subnet per Section 4.6, not the first, so double-check against the table every time. **Memory aid:** every interface boots administratively down on Cisco IOS — `no shutdown` is the single command students forget most often, and it is the #1 cause of "everything is configured correctly but the interface shows down/down."

### 6.3 R1 — Point-to-Point Link to R2

```text
R1(config)#interface gigabitEthernet 0/0/0
R1(config-if)#description P2P to R2
R1(config-if)#ip address 192.168.5.225 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
```

> This is Subnet 5 from Section 4.3 — the `/30`, sized for exactly 2 hosts and nothing more. R1 takes the first usable address (`.225`); R2 will take the second (`.226`). Either order works as long as both ends agree — but pick one convention and stay consistent so you don't cross wires when troubleshooting.

### 6.4 R1 — Static Routes to R2's LANs

```text
R1(config)#ip route 192.168.5.192 255.255.255.240 192.168.5.226
R1(config)#ip route 192.168.5.208 255.255.255.240 192.168.5.226
```

> **Mode:** Global Config. `ip route <destination-network> <destination-mask> <next-hop>` tells R1 "to reach LAN 3 or LAN 4, forward through R2's point-to-point address." Without these two lines, R1 knows about its *own* directly-connected subnets only — PC1 and PC2 could reach each other and their own gateway, but nothing on R2's side of the link. This is the single most common reason a VLSM lab "looks done" but pings across routers still fail: the interfaces and masks are all correct, but nobody told either router how to reach the *other* router's LANs.

### 6.5 R1 — Save

```text
R1#copy running-config startup-config
```

---

### 6.6 R2 — Basic Setup and Hardening

```text
Router>enable
Router#configure terminal
Router(config)#hostname R2
R2(config)#no ip domain-lookup
R2(config)#enable secret class
R2(config)#service password-encryption
R2(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. R2 - Authorized Use Only.
#
```

### 6.7 R2 — LAN Interfaces (Gi0/0 → LAN 3, Gi0/1 → LAN 4)

```text
R2(config)#interface gigabitEthernet 0/0
R2(config-if)#description LAN 3 - PC3 Gateway
R2(config-if)#ip address 192.168.5.206 255.255.255.240
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#description LAN 4 - PC4 Gateway
R2(config-if)#ip address 192.168.5.222 255.255.255.240
R2(config-if)#no shutdown
R2(config-if)#exit
```

### 6.8 R2 — Point-to-Point Link to R1

```text
R2(config)#interface gigabitEthernet 0/0/0
R2(config-if)#description P2P to R1
R2(config-if)#ip address 192.168.5.226 255.255.255.252
R2(config-if)#no shutdown
R2(config-if)#exit
```

### 6.9 R2 — Static Routes to R1's LANs

```text
R2(config)#ip route 192.168.5.128 255.255.255.192 192.168.5.225
R2(config)#ip route 192.168.5.0 255.255.255.128 192.168.5.225
```

> Mirror image of Section 6.4 — R2 needs a route to LAN 1 (`192.168.5.128/26`) and LAN 2 (`192.168.5.0/25`) via R1's point-to-point address (`192.168.5.225`). **Watch the masks closely:** it is very easy to accidentally paste R1's `/28` masks here out of habit — LAN 1 and LAN 2 use different prefix lengths (`/26` and `/25`) than LAN 3 and LAN 4 (`/28`), and mixing them up produces a route that matches the wrong range of addresses (or none at all).

### 6.10 R2 — Save

```text
R2#copy running-config startup-config
```

---

### 6.11 PC1–PC4 Addressing

In Packet Tracer, open each PC → **Desktop tab → IP Configuration**:

| Field           | PC1             | PC2           | PC3             | PC4             |
|------------------|------------------|----------------|------------------|------------------|
| IP Address       | 192.168.5.129    | 192.168.5.1    | 192.168.5.193    | 192.168.5.209    |
| Subnet Mask      | 255.255.255.192  | 255.255.255.128| 255.255.255.240  | 255.255.255.240  |
| Default Gateway  | 192.168.5.190    | 192.168.5.126  | 192.168.5.206    | 192.168.5.222    |

> Every PC gets the **first** usable address in its subnet, per Section 4.6 — this is the opposite convention from the router interfaces, which take the **last** usable address. There is no technical requirement that it be this way (any valid host address would work), but consistency within a lab's convention matters for readability of the addressing table, and mixing conventions is exactly what the exam tests you on when it hands you a table and asks "which address is invalid here."

---

## 7. Verification Steps

### 7.1 Verification Commands

| Device  | Command                  | What to check                                          |
|---------|----------------------------|-----------------------------------------------------------|
| R1, R2  | `show ip interface brief`  | All 3 interfaces `up/up`, IPs match Section 4.6           |
| R1, R2  | `show ip route`            | 2 connected LANs, 1 connected P2P, 2 static routes present |
| R1, R2  | `show run \| include ip route` | Static route syntax matches exactly, no mask typos    |
| PC1–PC4 | `ipconfig`                 | IP/mask/gateway match Section 6.11                        |

### 7.2 Expected Output Gallery

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         192.168.5.190   YES manual up                    up
GigabitEthernet0/1         192.168.5.126   YES manual up                    up
GigabitEthernet0/0/0       192.168.5.225   YES manual up                    up
```

All three interfaces show `up/up`. If any shows `administratively down`, you forgot `no shutdown` on that interface — see Section 8.

**`R1# show ip route`**

```text
      192.168.5.0/24 is variably subnetted, 6 subnets, 3 masks
C        192.168.5.0/25 is directly connected... 
```

Wait — R1 does **not** have LAN 2's subnet marked `C` unless you configured Gi0/1 correctly. The realistic full output:

```text
      192.168.5.0/25 is subnetted, 1 subnets
C        192.168.5.0 [Gi0/1] is directly connected
L        192.168.5.126/32 is directly connected, GigabitEthernet0/1
      192.168.5.128/26 is subnetted, 1 subnets
C        192.168.5.128 is directly connected, GigabitEthernet0/0
L        192.168.5.190/32 is directly connected, GigabitEthernet0/0
      192.168.5.192/28 is subnetted, 1 subnets
S        192.168.5.192 [1/0] via 192.168.5.226
      192.168.5.208/28 is subnetted, 1 subnets
S        192.168.5.208 [1/0] via 192.168.5.226
      192.168.5.224/30 is subnetted, 1 subnets
C        192.168.5.224 is directly connected, GigabitEthernet0/0/0
L        192.168.5.225/32 is directly connected, GigabitEthernet0/0/0
```

`C` = directly connected (LAN 1, LAN 2, the P2P network). `L` = the router's own interface address as a host route (normal IOS behavior, ignore for troubleshooting purposes). `S` = static — this is where LAN 3 and LAN 4 must appear, learned via the route commands in Section 6.4. **If the `S` lines are missing, the static routes were never entered or were entered with a typo'd mask** — re-check Section 6.4 character-by-character.

**`PC1> ping 192.168.5.209`** (PC1 to PC4, full cross-router path test)

```text
Pinging 192.168.5.209 with 32 bytes of data:

Reply from 192.168.5.209: bytes=32 time=2ms TTL=126
Reply from 192.168.5.209: bytes=32 time=1ms TTL=126
Reply from 192.168.5.209: bytes=32 time=1ms TTL=126
Reply from 192.168.5.209: bytes=32 time=1ms TTL=126

Ping statistics for 192.168.5.209:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

`TTL=126` (not 128 or 127) confirms the packet crossed **two** router hops (R1 and R2 each decrement TTL by 1 from a 128 starting value on many end-host stacks) — this is a quick sanity check that the traffic actually routed rather than being answered locally by mistake.

### 7.3 Ping / Reachability Matrix

| From | To | Expected Result | Why |
|---|---|---|---|
| PC1 | R1 Gi0/0 (192.168.5.190) | Success | Directly connected gateway |
| PC1 | PC2 | **Fail** without routing help — actually Success | Different subnets, but both directly connected to R1, which routes between its own interfaces automatically |
| PC1 | PC3 | Success | Requires R1's static route to 192.168.5.192/28 via R2 |
| PC2 | PC4 | Success | Requires R1's static route to 192.168.5.208/28 via R2 |
| PC3 | PC1 | Success | Requires R2's static route to 192.168.5.128/26 via R1 |
| R1 | R2 (192.168.5.226) | Success | Directly connected point-to-point link |

---

## 8. Common Mistakes (the 80/20)

1. **Allocating subnets out of order (smallest-first).** This is the #1 conceptual error specific to VLSM. If you assign the `/30` point-to-point link a block first and then try to fit the `/25` LAN 2 requirement afterward, the math no longer lands on clean boundaries. Always sort host requirements largest-to-smallest before assigning a single address.
2. **Swapping which end gets the first vs. last usable address.** This lab deliberately uses "PC = first usable, router = last usable" — the opposite of many other labs' "gateway = .1" convention. Muscle memory from earlier labs causes students to put router IPs on `.1`-style addresses here, which doesn't break connectivity by itself but does not match the addressing table and will be marked wrong against Section 4.6.
3. **Forgetting `no shutdown` on a newly configured interface.** Universal Cisco IOS mistake — every interface boots administratively down.
4. **Typo'ing the subnet mask in a static route.** `ip route 192.168.5.192 255.255.255.240 ...` — if you write `.255.255.255.255.192` (LAN 1's mask) here instead of LAN 3's actual `/28` mask, the route either matches nothing or matches the wrong range, and pings mysteriously fail only for that one destination.
5. **Confusing which router is the next hop in each static route.** R1's routes point at R2's P2P address (`.226`); R2's routes point at R1's P2P address (`.225`). Reversing this on either router produces a "no route to host" error that looks identical to a missing route.
6. **Assuming `/28` always means the same address range regardless of position.** LAN 3 (`192.168.5.192/28`) and LAN 4 (`192.168.5.208/28`) share a prefix length but are completely different subnets — copy-pasting one router's LAN 3 config onto the other's LAN 4 interface (or vice versa) produces an overlapping or wrong address.
7. **Not saving configuration before closing Packet Tracer.** `copy running-config startup-config` — skipping this erases the VLSM math you just worked out by hand.
8. **Miscounting host bits by off-by-one.** The most common calculation slip is forgetting the `−2` in `2^h − 2`, which leads to picking a prefix one bit too small (undersized subnet that doesn't actually fit the requirement) or one bit too large (wastes an entire size class of addresses).

---

## 9. Troubleshooting Guide

Work through these **in order** — each step assumes the previous one passed.

| Step | Symptom                                          | Likely Cause                                                     | Diagnostic Command | Fix |
|---|-----------------------------------------------------|-----------------------------------------------------------------|---|---|
| 1 | Interface shows `administratively down`              | Forgot `no shutdown`                                              | `show ip interface brief` | Enter the interface, run `no shutdown` |
| 2 | PC can't reach its own gateway                        | Wrong IP/mask on PC, or mismatched mask between PC and router interface | `ipconfig` (PC) vs. `show ip interface brief` (router) | Re-check both ends against Section 4.6/6.11 exactly |
| 3 | PC reaches its own LAN but not the other router's LANs | Missing static route on the local router                         | `show ip route` | Add the missing `ip route` statement from Section 6.4/6.9 |
| 4 | Static route present but ping still fails              | Wrong next-hop IP, or return-path route missing on the *other* router | `show ip route` on both routers | Static routes are one-directional — verify both R1 and R2 have a route to *each other's* LANs |
| 5 | Ping fails only to one specific LAN, others work fine  | Typo'd mask in that one `ip route` line                          | `show run \| include ip route` | Compare byte-for-byte against Section 4.5's allocation table |
| 6 | Two LANs appear to overlap or a device gets an unreachable address | VLSM subnets allocated out of order or math error during planning | Manually recompute network/broadcast addresses per Section 4.3 | Redo the VLSM allocation in largest-first order |
| 7 | R1 ↔ R2 point-to-point link won't come up              | Mismatched mask (one end `/30`, other end something else) or `no shutdown` missing on one side | `show ip interface brief` on both routers | Confirm both ends use `255.255.255.252` and both are `no shutdown` |
| 8 | Config disappears after a device reload                | Forgot to save                                                    | `show startup-config` vs `show running-config` | `copy running-config startup-config` |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why VLSM instead of fixed-length subnetting for this requirement set?** Fixed-length subnetting would force every subnet to the size of the *largest* requirement (64 hosts → `/26` for everything), which only yields 4 equal blocks from a `/24` — not enough to also carve out a separate `/30` for the point-to-point link without borrowing from an already-assigned LAN. VLSM lets each subnet be sized independently, which is the only way to fit 5 differently-sized requirements into one `/24` without waste or overlap.
- **Why largest-first allocation specifically?** As explained in Section 4.2, block-boundary alignment only works cleanly when you go from most-restrictive (largest block) to least-restrictive (smallest block). This isn't a stylistic preference — allocate out of order and you either waste address space realigning boundaries or produce an invalid, overlapping plan.
- **Why give routers the last usable address and PCs the first, instead of the more common "gateway = .1" pattern?** There's no technical advantage either way — a subnet's gateway can legally be any valid host address. This lab's convention exists specifically to break the "gateway is always .1" assumption some students form after earlier labs, because the CCNA exam will hand you addressing tables that don't follow that convention and expect you to read the table, not guess based on habit.
- **Why static routes instead of a dynamic routing protocol for a 2-router topology?** With only one point-to-point link and 4 total LANs, the entire routing table is 2 lines per router — smaller than the neighbor-relationship overhead a protocol like OSPF would add. Static routing also forces you to demonstrate you understand exactly which network needs to reach which, rather than letting a protocol discover it for you — which is the point of a VLSM-focused lab.
- **Why leave 28 addresses (`.228`–`.255`) unused at the end of the supernet?** VLSM's job is to satisfy every stated requirement without overlap — it is not required to consume literally every address in the supernet. Leftover space at the end of an allocation is normal and is exactly the reserve you'd hand to the next new LAN that gets added later, without needing to renumber anything already deployed.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...your company is issued a single `/24` (or a `/22`, or any single supernet) by a parent org, ISP, or internal IPAM policy, and told to make it work for several departments of very different sizes — this lab's exact scenario, just at a larger scale.
- ...you're auditing an existing network and find subnets that don't align on clean block boundaries — that's almost always the fingerprint of someone allocating VLSM out of order (smallest-first) at some point in the network's history, and it's a strong signal there's wasted, unreachable address space hiding somewhere in the plan.
- ...a new site needs to be added to an existing addressing scheme and you have to find (or calculate) the next available block without disturbing anything already deployed — exactly what Section 4.3's "leftover `.228`–`.255` space" demonstrates on a small scale.
- ...you're handed a legacy config with `ip route` statements and asked "why does this device work" — being able to read a static route line and immediately know which subnet and next-hop it describes (without a subnet calculator) is a baseline expected skill in any hands-on network engineering interview.

---

## 12. Stretch Goal

Once the base lab works end-to-end, try one or more of the following without referring back to the steps above:

1. **Add a fifth LAN requiring 20 hosts**, sourced from the unused `192.168.5.228–255` space. Work out by hand whether it actually fits (hint: check the available block size against the requirement before assuming it does).
2. **Renumber the point-to-point link as the smallest possible allocation (`/31`)** instead of `/30`, and explain in a sentence why `/31` point-to-point links are valid per RFC 3021 even though they have zero usable "host" addresses under the normal `2^h − 2` formula.
3. **Break a static route on purpose, then diagnose it using only `show ip route`** (no peeking at your own running-config) — delete R2's route to LAN 1, confirm PC3→PC1 pings fail exactly as Section 9 predicts, then restore it.
4. **Re-run the entire VLSM allocation from scratch using `10.10.0.0/22` instead of `192.168.5.0/24`**, keeping the same 5 host-count requirements, and verify your new plan against the same block-size-boundary rules from Section 4.3.

---

## 13. Self-Assessment

Before moving on, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, why VLSM must allocate the largest requirement first?
- [ ] Given a host-count requirement, can you derive the correct prefix length using `2^h − 2 ≥ requirement` without a calculator?
- [ ] Can you convert any `/25` through `/30` prefix to a dotted-decimal mask from binary, without recalling it from a memorized table?
- [ ] For any subnet, can you compute the network address, first usable host, last usable host, and broadcast address by hand?
- [ ] Can you explain the block-size shortcut and use it to verify a subnet lands on a valid boundary?
- [ ] Can you write the two static route commands needed on each router in this topology, from memory, including correct masks?
- [ ] Given a fresh `/24` and 5 new host-count requirements, could you produce a full VLSM allocation table like Section 4.5 yourself?
- [ ] Can you name, without looking at Section 8, at least 4 of the 8 common mistakes?

If you answered "no" to more than two of these, redo the VLSM math from scratch on paper (not by copy-pasting the table) before moving on — the goal of Day 15 isn't a working topology, it's the ability to VLSM-subnet any block on demand.

---

## 14. Key Concepts Demonstrated

- **VLSM (Variable Length Subnet Masking)** — subdividing one supernet into subnets of different sizes based on actual host requirements
- **Largest-first allocation** — the ordering rule that keeps every subnet aligned on a valid block boundary
- **Binary-to-decimal mask derivation** — deriving a dotted-decimal mask from host-bit count without memorization
- **Network/broadcast/host-range calculation** — computing all four key addresses for any subnet by hand
- **Block-size verification** — the `256 − mask` shortcut used to confirm valid subnet boundaries
- **Static routing across multiple non-adjacent subnets** — connecting LANs that sit behind different routers
- **Routing table interpretation** — distinguishing `C` (connected), `L` (local), and `S` (static) route entries

---

## 15. What I Learned

Working through this lab made the difference between *memorizing* subnet masks and *deriving* them completely clear. Fixed-length subnetting (splitting a block into equal pieces) hides the real skill — VLSM forces you to actually reason about how many host bits each individual requirement needs, and to keep track of where the next available block starts as you go. The largest-first ordering rule felt arbitrary until I tried allocating out of order and watched a smaller subnet leave a gap that broke the next block's alignment — after that it clicked as a direct consequence of binary math, not a rule to memorize.

The static routing piece reinforced something that carries forward into every future routing lab: correctly assigned IPs and masks get you exactly nowhere across a router boundary without also telling each router how to reach the *other* router's networks. That's the layer VLSM alone doesn't solve, and it's why this lab pairs subnetting with static routing rather than teaching them separately.

This lab is the foundation for what comes next:

- More advanced/nested VLSM scenarios (subnetting a subnet)
- Route summarization (the reverse skill — combining multiple VLSM subnets back into one advertised route)
- Dynamic routing protocols (OSPF), which discover what this lab required you to configure by hand
- ACL design, which depends on being able to reference exact subnet boundaries precisely

---

## 16. Skills Practiced

- VLSM subnet planning and largest-first allocation ordering
- Manual binary-to-decimal subnet mask derivation
- Network/first-host/last-host/broadcast address calculation by hand
- Block-size boundary verification
- Cisco IOS router interface configuration
- Static route configuration across a multi-router topology
- Routing table interpretation and troubleshooting
- End-to-end connectivity verification and structured diagnostics

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology that mirrors the design above using free, open-source images, built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco 4321/2911 | VyOS |
| PCs (PC1–PC4) | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script. VyOS's CLI is Cisco-like but not identical (`set`/`commit` configuration style rather than `configure terminal`/exit-per-mode) — a VyOS-equivalent command reference is included in the GNS3 README so the *VLSM and static routing concepts* transfer even though the exact syntax doesn't.
