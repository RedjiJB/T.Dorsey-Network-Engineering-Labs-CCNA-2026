# Day 16 Lab Manual — VLANs Part 1: Configuration and Inter-VLAN Routing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Segment a single flat network into three VLANs (Engineering, HR, Sales) on one access switch, assign each VLAN a `/26` subnet with the gateway placed on the *last usable address*, provide inter-VLAN routing using one physical router interface per VLAN (no trunking, no router-on-a-stick), and verify both unicast reachability and broadcast domain isolation. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): VLANs, broadcast domains, switch/router roles, subnetting. Domain 2 (Network Access): VLAN configuration and access port assignment, the primary topic this exam domain covers. |
| **Prerequisites** | Day 01 (device roles, static routing, basic IOS hardening) and comfort with binary/decimal subnet math (used again here, this time on a `/26`). No prior VLAN experience required — this is the first VLAN lab in the series. |
| **Time Estimate** | 1.5 – 2 hours (first attempt); 30–40 minutes on repeat/review. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner) — few devices (1 switch, 1 router, 6 PCs) and no ASA firewall, but the VLAN concept itself and the "no trunking yet" router design are new and easy to get subtly wrong. |

---

## 1. Lab Overview

Up to this point (Day 01), every device you configured lived on one flat, single-VLAN network — every port was implicitly part of `VLAN 1`, and a switch just forwarded frames between whatever was plugged into it. That works for a two-PC branch office. It does not work once a company has an Engineering team, an HR team, and a Sales team all sharing the same physical switch, because by default every one of those devices sits in the **same broadcast domain** — every broadcast frame (ARP requests, DHCP discovers, etc.) from any one PC is flooded to *all* of them, and there is no logical separation between departments even though there should be.

This lab fixes that using **VLANs (Virtual LANs)** — a way to logically partition a single physical switch into multiple, isolated broadcast domains, each with its own IP subnet. You'll create three VLANs (Engineering, HR, Sales) on one switch, assign PCs to the correct VLAN via their access ports, and give each VLAN a **router interface** so devices in different VLANs can still reach each other — because right now, with three separate Layer 2 broadcast domains and no routing between them, HR could not ping Engineering even though they're plugged into the exact same physical switch.

Critically, this lab does **not** use trunking or router-on-a-stick (subinterfaces with `dot1q` encapsulation) — those come later in the Day 16+ series. Here, inter-VLAN routing is done the most literal way possible: **one dedicated physical router interface per VLAN**, each cabled to a separate access port on the switch. This is intentionally the "hard way" so the underlying mechanics (a router interface's IP must be *in* the VLAN's subnet; the switch must trunk nothing and just forward access-mode traffic) are fully visible before router-on-a-stick abstracts the physical-cabling requirement away.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain what a VLAN is and why it creates a separate broadcast domain from every other VLAN on the same switch
- Subnet a `/24` into multiple `/26` blocks by hand, and place a gateway at a subnet's *last* usable address (not the conventional first)
- Create and name VLANs in a switch's VLAN database
- Assign physical switch ports to VLANs in access mode
- Configure one router interface per VLAN to provide inter-VLAN routing without trunking
- Configure PCs with VLAN-appropriate IP addresses and gateways
- Verify inter-VLAN unicast reachability with `ping` and confirm broadcast traffic stays contained to its own VLAN
- Explain, in business terms, why a company segments departments into VLANs instead of leaving everyone on one flat network

---

## 2. Business Context

**Why would a real company do this?**

Picture a 40-person company that just moved into a new office with one switch stack serving three departments — Engineering, HR, and Sales — all plugged into ports on the same physical switches. Leadership's requirements, translated into network language, look like this:

- **"HR handles payroll and personnel records — Sales shouldn't be able to see HR's network traffic at all."** → without VLANs, every device on the switch is in the same broadcast domain and, more importantly, the same *Layer 2 segment* — anyone with a packet sniffer plugged into any port could see ARP traffic (and, if misconfigured, more) from every department. VLANs create hard logical separation even though the cabling is identical.
- **"We don't want an intern's laptop malfunctioning and broadcast-storming the entire building."** → broadcast traffic (ARP, DHCP discover, etc.) is flooded to every port *within* a VLAN, but never crosses into a different VLAN. Segmenting into VLANs is the single most effective way to shrink the blast radius of a broadcast storm or a misbehaving NIC.
- **"Engineering, HR, and Sales all still need to email each other and hit the same file server — they can't be totally isolated."** → this is exactly why VLANs need routing *between* them. Segmentation isn't the same as isolation; the business still needs controlled, deliberate paths between departments, which is what the router's per-VLAN interfaces provide.
- **"We're not ready to invest in a trunking-capable design yet — keep this simple for now."** → this lab deliberately uses one physical interface per VLAN instead of trunking, mirroring how a very small company (or a lab building up skills incrementally) would start: it's more cabling and less scalable, but it's conceptually the simplest possible inter-VLAN routing design, and it's exactly what you'd do if you only had 3 VLANs and ports to spare. Trunking becomes worth the added complexity once VLAN count and switch count grow — that's Day 16 Part 2+ territory.
- **"IT needs to be able to grow each department's network later without renumbering everyone."** → each VLAN was sized with room to grow within its /26 (62 usable addresses per department, versus 2 PCs today), the same "size for the future, not just today" principle from Day 01.

This is the exact scenario a network engineer walks into during their first few months at almost any company larger than a single-office startup: a flat network that "worked" during a small pilot, now needing real departmental segmentation as headcount grows.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2016%20Lab%20-%20VLANs%20(Part%201).png" alt="Day 16 VLAN Network Topology" width="900">
</p>

### 3.1 Traffic Flow Summary

```text
VLAN 10 (Engineering)   PC1, PC2 -- SW1 (Fa0/1-0/2, VLAN 10) -- R1 Gi0/0 (10.0.0.62)
VLAN 20 (HR)            PC3, PC4 -- SW1 (Fa0/3-0/4, VLAN 20) -- R1 Gi0/1 (10.0.0.126)
VLAN 30 (Sales)         PC5, PC6 -- SW1 (Fa0/5-0/6, VLAN 30) -- R1 Gi0/2 (10.0.0.190)
```

R1 is cabled to SW1 with **three separate physical links**, one per VLAN — each SW1 port facing R1 is an access port in that VLAN, not a trunk. This is the "one interface per VLAN" design described in Section 1.

### 3.2 Equipment List

| Role         | Device            | Model              | Hostname Used Below |
|--------------|-------------------|---------------------|----------------------|
| Switch       | Access switch      | Cisco 2960-24TT     | `SW1`                |
| Router       | Inter-VLAN router  | Cisco 2911          | `R1`                 |
| PC x2        | Engineering        | Generic PC          | `PC1`, `PC2`         |
| PC x2        | HR                  | Generic PC          | `PC3`, `PC4`         |
| PC x2        | Sales               | Generic PC          | `PC5`, `PC6`         |

> **Note on scope:** This lab intentionally has no firewall and no WAN — it's a single-site, single-switch lab focused purely on VLAN mechanics and inter-VLAN routing. Security hardening (banners, SSH, `enable secret`) still applies to SW1 and R1 the same way it did in Day 01, and is included below for consistency, but is not the focus of this lab.

---

## 4. IP Addressing Plan

This lab has its **own** addressing plan — unlike a lab that reuses a prior day's subnetting, Day 16 introduces a new technique: splitting one `/24` into three `/26` blocks and placing each VLAN's gateway at the **last** usable address of its subnet instead of the conventional first. Do the math by hand; don't just copy the table.

### 4.1 Why `/26`, and Why Three of Them

The whole `10.0.0.0/24` block is being split evenly into 3 department subnets. The requirement is "a few dozen hosts of headroom per department, today only 2 PCs each" — nowhere near the 254 hosts a full `/24` would offer, but more than a `/27` (30 usable) comfortably supports if the department later doubles or triples in size. A `/26` gives 62 usable hosts per VLAN — enough headroom for real department growth without wasting the entire `/24` on one VLAN.

**The rule of thumb from Day 01, applied again here:** count the realistic maximum host count for the broadcast domain, then pick the smallest power-of-two block that covers it. A department LAN isn't a point-to-point link — it needs growth room, so here that means `/26` rather than a tightly-fit `/30`-style block.

### 4.2 How to Calculate These by Hand

**Step 1 — Convert the requirement to a number of usable hosts.**

Same formula as Day 01:

```text
usable hosts = 2^h − 2
```

**Step 2 — Solve for the smallest `h` that satisfies "a few dozen hosts."**

```text
2^h − 2 ≥ 30  (want more than a /27's 30 hosts)
2^5 − 2 = 30   → not quite enough headroom
2^6 − 2 = 62   → comfortably covers "a few dozen," plenty of room to grow
```

So `h = 6` host bits → prefix length = `32 − 6 = /26`.

**Step 3 — Convert the prefix length to a dotted-decimal subnet mask.**

```text
/26 = 11111111.11111111.11111111.11000000
    =     255  .    255 .    255 .    192
```

**Memory aid** (same table from Day 01, /26 row highlighted):

| Prefix | Host bits | Usable hosts | Last octet (decimal) |
|---|---|---|---|
| /24 | 8 | 254 | .0 |
| /25 | 7 | 126 | .128 |
| **/26** | **6** | **62** | **.192** |
| /27 | 5 | 30  | .224 |
| /28 | 4 | 14  | .240 |

Recall the shortcut from Day 01: last-octet mask value = `256 − 2^h`. For `/26`, `256 − 2^6 = 256 − 64 = 192`. Same formula, different exponent.

**Step 4 — Find the block size and lay out all three subnets.**

Block size = `256 − 192 = 64`. `/26` subnets always land on multiples of 64: `.0, .64, .128, .192`. With 3 departments needed, use the first three blocks:

```text
VLAN 10 (Engineering):  10.0.0.0/26     (block 1: .0   – .63)
VLAN 20 (HR):            10.0.0.64/26    (block 2: .64  – .127)
VLAN 30 (Sales):         10.0.0.128/26   (block 3: .128 – .191)
                          (.192–.255 reserved for a future VLAN 40)
```

**Step 5 — Identify network, first host, last host, and broadcast address for each block.**

Worked example, VLAN 10 (`10.0.0.0/26`):

```text
Network address:    10.0.0.0     (all 6 host bits = 0)
First usable host:  10.0.0.1     (network address + 1)
Last usable host:   10.0.0.62    (broadcast address − 1)
Broadcast address:  10.0.0.63    (all 6 host bits = 1 → 0 + 63)
```

Same pattern for VLAN 20 (`10.0.0.64/26`): network `.64`, first host `.65`, last host `.126`, broadcast `.127`. And VLAN 30 (`10.0.0.128/26`): network `.128`, first host `.129`, last host `.190`, broadcast `.191`.

### 4.3 Why the Gateway Sits at the *Last* Usable Address (Not the First)

Most labs so far have put the router/gateway at the first usable host address (`.1`) out of convention. This lab deliberately does the opposite — the gateway is the *last* usable address in each block (`.62`, `.126`, `.190`) — for one reason: **it's a convention, not a technical requirement, and CCNA candidates need to be comfortable with both.** On the exam and in real job environments you will see both patterns (some shops standardize gateways at the bottom of the range, others at the top, often to leave the low addresses free for infrastructure like DHCP reservations or servers). The math to find "last usable address" is identical to finding the broadcast address, minus one:

```text
Last usable host = broadcast address − 1 = (network address + block size − 1) − 1
```

For VLAN 10: `10.0.0.0 + 64 − 1 = 10.0.0.63` (broadcast), so last usable host = `10.0.0.62`. This is exactly what the table below uses.

### 4.4 Full Device Address Table

| VLAN | Name | Subnet | Mask | Gateway (last usable) | Devices |
|---|---|---|---|---|---|
| 10 | Engineering | 10.0.0.0/26   | 255.255.255.192 | 10.0.0.62  | PC1, PC2 |
| 20 | HR          | 10.0.0.64/26  | 255.255.255.192 | 10.0.0.126 | PC3, PC4 |
| 30 | Sales       | 10.0.0.128/26 | 255.255.255.192 | 10.0.0.190 | PC5, PC6 |

| Device | Interface | IP Address | Mask | Connects To |
|---|---|---|---|---|
| PC1 | NIC | 10.0.0.1  | 255.255.255.192 | SW1 Fa0/1 (VLAN 10) |
| PC2 | NIC | 10.0.0.2  | 255.255.255.192 | SW1 Fa0/2 (VLAN 10) |
| PC3 | NIC | 10.0.0.65 | 255.255.255.192 | SW1 Fa0/3 (VLAN 20) |
| PC4 | NIC | 10.0.0.66 | 255.255.255.192 | SW1 Fa0/4 (VLAN 20) |
| PC5 | NIC | 10.0.0.129 | 255.255.255.192 | SW1 Fa0/5 (VLAN 30) |
| PC6 | NIC | 10.0.0.130 | 255.255.255.192 | SW1 Fa0/6 (VLAN 30) |
| R1 | Gi0/0 | 10.0.0.62  | 255.255.255.192 | SW1 Fa0/22 (VLAN 10 access) |
| R1 | Gi0/1 | 10.0.0.126 | 255.255.255.192 | SW1 Fa0/23 (VLAN 20 access) |
| R1 | Gi0/2 | 10.0.0.190 | 255.255.255.192 | SW1 Fa0/24 (VLAN 30 access) |

**Default gateways:** PC1/PC2 → `10.0.0.62`; PC3/PC4 → `10.0.0.126`; PC5/PC6 → `10.0.0.190`.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Place SW1, R1, and all six PCs in Packet Tracer matching the topology image.
2. Cable **three separate copper straight-through links** between SW1 and R1 — one per VLAN. Do not use a single trunk link; that's a different lab.
3. Cable each PC to its designated access port per the table above, and confirm link lights turn green.
4. Have the VLAN and addressing tables (Sections 3.2 and 4.4) open in a second window for reference.
5. Double-check your Packet Tracer router model's interface names — substitute `FastEthernet0/0` etc. if your platform doesn't have `GigabitEthernet0/0-0/2`.

---

## 6. Configuration Tasks

### 6.1 SW1 (Cisco 2960-24TT)

**Step 1: Hostname and basic hardening**

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW1
SW1(config)#enable secret class
SW1(config)#service password-encryption
SW1(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. SW1 - Authorized Use Only.
#
```

> Same reasoning as Day 01: `enable secret` is MD5-hashed and always preferred over plaintext `enable password`; `service password-encryption` weakly obscures any remaining plaintext passwords; the banner strengthens an unauthorized-access case legally.

**Step 2: Create and name the VLANs**

```text
SW1(config)#vlan 10
SW1(config-vlan)#name Engineering
SW1(config-vlan)#exit
SW1(config)#vlan 20
SW1(config-vlan)#name HR
SW1(config-vlan)#exit
SW1(config)#vlan 30
SW1(config-vlan)#name Sales
SW1(config-vlan)#exit
```

> **Mode:** Global Config → VLAN Config (a sub-mode entered by `vlan <id>`). Creating a VLAN just adds an entry to the switch's VLAN database (visible in `show vlan brief`) — it does nothing to traffic on its own until ports are actually assigned to it. `name` is optional but strongly recommended: `show vlan brief` with unnamed VLANs (`VLAN0010`) is far harder to read once you have more than 2-3 VLANs.
>
> **Memory aid:** VLAN IDs 1–1005 are the "normal range" available on virtually every switch without special licensing; this lab's 10/20/30 numbering (rather than 1/2/3) is a common real-world convention — it leaves room to insert VLAN 11, 12, etc. later without renumbering everything, the same reason IP subnetting plans leave gaps.

**Step 3: Assign PC-facing ports to their VLANs**

```text
SW1(config)#interface fastEthernet 0/1
SW1(config-if)#description Link to PC1 (Engineering)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 10
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/2
SW1(config-if)#description Link to PC2 (Engineering)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 10
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/3
SW1(config-if)#description Link to PC3 (HR)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 20
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/4
SW1(config-if)#description Link to PC4 (HR)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 20
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/5
SW1(config-if)#description Link to PC5 (Sales)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 30
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/6
SW1(config-if)#description Link to PC6 (Sales)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 30
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

> `switchport mode access` explicitly forces the port into access mode (carries exactly one VLAN, untagged) rather than leaving it to Dynamic Trunking Protocol negotiation — always set this explicitly on end-host ports; never trust the DTP default. `switchport access vlan <id>` is the command that actually does the segmentation — without it, the port stays in VLAN 1 by default even though the VLAN itself was created in Step 2. This is the single most commonly forgotten step in this entire lab. `spanning-tree portfast` again skips the ~30 second STP listening/learning delay on host-facing ports, same as Day 01.

**Step 4: Configure the three access ports facing R1**

```text
SW1(config)#interface fastEthernet 0/22
SW1(config-if)#description Link to R1 Gi0/0 (Engineering gateway)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 10
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/23
SW1(config-if)#description Link to R1 Gi0/1 (HR gateway)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 20
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/24
SW1(config-if)#description Link to R1 Gi0/2 (Sales gateway)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

> This is the crux of the "one interface per VLAN, no trunking" design: each link to R1 is an ordinary **access port**, just like a PC port, carrying exactly one VLAN untagged. R1 doesn't need to understand 802.1Q tags at all in this design — from R1's point of view, each of its three interfaces is just plugged into a normal, single-VLAN Ethernet segment. This is what makes this design conceptually simple but physically expensive: 3 VLANs cost you 3 switch ports and 3 router interfaces, and a 4th VLAN would need a 4th of each. Router-on-a-stick (later in the course) solves that scaling problem with one trunk link instead.

**Step 5: Management SVI and SSH (VLAN 1, unused for data but still needed for switch management)**

```text
SW1(config)#interface vlan 1
SW1(config-if)#ip address 10.0.0.254 255.255.255.192
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#ip default-gateway 10.0.0.62
SW1(config)#ip domain-name labnet.local
SW1(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
SW1(config)#username admin secret cisco123
SW1(config)#line vty 0 15
SW1(config-line)#login local
SW1(config-line)#transport input ssh
SW1(config-line)#exit
```

> Note: VLAN 1 is still the switch's *default* management VLAN here since no port is explicitly assigned to it for data — this is fine for a lab this size, but in a production network, best practice is to never use VLAN 1 for anything (including management) precisely because it's the factory default and an easy target. That hardening step is out of scope for Day 16 but worth remembering for later labs.

**Step 6: Save**

```text
SW1#copy running-config startup-config
```

---

### 6.2 R1 (Cisco 2911)

**Step 1: Hostname and basic hardening**

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

**Step 2: Console and SSH access**

```text
R1(config)#line console 0
R1(config-line)#password cisco
R1(config-line)#login
R1(config-line)#exit
R1(config)#ip domain-name labnet.local
R1(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
R1(config)#username admin secret cisco123
R1(config)#line vty 0 4
R1(config-line)#login local
R1(config-line)#transport input ssh
R1(config-line)#exit
```

**Step 3: Configure one interface per VLAN**

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description Engineering (VLAN 10) gateway
R1(config-if)#ip address 10.0.0.62 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description HR (VLAN 20) gateway
R1(config-if)#ip address 10.0.0.126 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/2
R1(config-if)#description Sales (VLAN 30) gateway
R1(config-if)#ip address 10.0.0.190 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
```

> Each router interface's IP **must** fall inside the subnet of the VLAN it serves — Gi0/0 is `10.0.0.62/26`, which is inside `10.0.0.0/26` (Engineering); Gi0/1 is `10.0.0.126/26`, inside `10.0.0.64/26` (HR); Gi0/2 is `10.0.0.190/26`, inside `10.0.0.128/26` (Sales). If any of these were mismatched — say Gi0/0 accidentally used `10.0.0.126` — the interface would still come up, but PCs on VLAN 10 would have a gateway address that doesn't exist on their own subnet, and connectivity would silently fail. This is why matching each interface's IP to the correct VLAN subnet is the single most important detail in this whole configuration task.
>
> **No routing protocol and no static routes are needed here.** Because R1 has a directly connected interface in *every* VLAN's subnet, all three networks already appear in `show ip route` as `directly connected` entries the moment each interface comes up (`no shutdown` + correct IP is all it takes). This is different from Day 01, where NY-R1 needed an explicit static route to reach a network it wasn't directly attached to. Inter-VLAN routing via one-interface-per-VLAN is, structurally, the simplest possible routing scenario: everything is directly connected.

**Step 4: Save**

```text
R1#copy running-config startup-config
```

---

### 6.3 PC1–PC6

In Packet Tracer, open each PC → **Desktop tab → IP Configuration**:

| PC | IP Address | Subnet Mask | Default Gateway |
|---|---|---|---|
| PC1 | 10.0.0.1   | 255.255.255.192 | 10.0.0.62  |
| PC2 | 10.0.0.2   | 255.255.255.192 | 10.0.0.62  |
| PC3 | 10.0.0.65  | 255.255.255.192 | 10.0.0.126 |
| PC4 | 10.0.0.66  | 255.255.255.192 | 10.0.0.126 |
| PC5 | 10.0.0.129 | 255.255.255.192 | 10.0.0.190 |
| PC6 | 10.0.0.130 | 255.255.255.192 | 10.0.0.190 |

---

## 7. Verification Steps

### 7.1 Device-level verification commands

| Device | Command | What to check |
|---|---|---|
| SW1 | `show vlan brief` | VLANs 10/20/30 exist, named correctly, correct ports listed under each |
| SW1 | `show interfaces status` | All access ports `connected`, correct VLAN column, not `err-disabled` |
| R1 | `show ip interface brief` | All three Gi interfaces `up/up` with correct IPs |
| R1 | `show ip route` | Three `directly connected` /26 networks, one per VLAN, no static routes needed |
| PC | `ipconfig` | Correct IP/mask/gateway per the table in Section 6.3 |

### 7.2 Expected Output Gallery

**`SW1# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/7, Fa0/8, Fa0/9, Fa0/10
                                                 Fa0/11, Fa0/12 ...
10   Engineering                      active    Fa0/1, Fa0/2, Fa0/22
20   HR                               active    Fa0/3, Fa0/4, Fa0/23
30   Sales                            active    Fa0/5, Fa0/6, Fa0/24
```

Each VLAN shows exactly the ports you assigned to it — 2 PC ports plus 1 R1-facing port each. If a port you configured is missing from its expected VLAN row (or still shows under VLAN 1), you forgot `switchport access vlan <id>` on that interface — see Common Mistakes.

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.62       YES manual up                    up
GigabitEthernet0/1         10.0.0.126      YES manual up                    up
GigabitEthernet0/2         10.0.0.190      YES manual up                    up
```

All three interfaces `up/up` — this alone confirms cabling and `no shutdown` were done correctly on both ends of all three SW1↔R1 links.

**`R1# show ip route`**

```text
      10.0.0.0/26 is subnetted, 3 subnets
C        10.0.0.0 is directly connected, GigabitEthernet0/0
C        10.0.0.64 is directly connected, GigabitEthernet0/1
C        10.0.0.128 is directly connected, GigabitEthernet0/2
```

All three department subnets appear as `C` (directly connected) — no `S` (static) entries needed, unlike Day 01. This is the direct evidence that this design's routing requires zero manual route configuration; it's entirely a byproduct of correct interface addressing.

**`PC1> ping 10.0.0.65`** (Engineering PC pinging an HR PC — inter-VLAN test)

```text
Pinging 10.0.0.65 with 32 bytes of data:

Reply from 10.0.0.65: bytes=32 time=1ms TTL=127
Reply from 10.0.0.65: bytes=32 time=1ms TTL=127
Reply from 10.0.0.65: bytes=32 time=1ms TTL=127
Reply from 10.0.0.65: bytes=32 time=1ms TTL=127

Ping statistics for 10.0.0.65:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Notice the **TTL of 127**, not 128 — it decremented by 1 because this packet crossed exactly one router hop (R1) to get from VLAN 10 to VLAN 20. A same-VLAN ping (PC1 → PC2) would show TTL 128 (or the platform's own default, undecremented), since it never leaves the switch. TTL behavior is a useful sanity check for "did this actually get routed, or did it stay local?"

### 7.3 Ping / Reachability Matrix

| From | To | Expected Result | Why |
|---|---|---|---|
| PC1 | PC2 | Success | Same VLAN (10), switched locally, no routing involved |
| PC1 | R1 Gi0/0 (10.0.0.62) | Success | Directly connected gateway |
| PC1 | PC3 (10.0.0.65) | Success (routed) | Different VLANs, R1 routes between its directly connected interfaces |
| PC3 | PC6 (10.0.0.130) | Success (routed) | Different VLANs (20 → 30), same mechanism |
| PC1 broadcast (e.g. ARP request) | PC3, PC5 | **Not received** | Broadcasts stay inside their own VLAN/broadcast domain; routers do not forward broadcast traffic by default |
| PC5 | 10.0.0.191 (VLAN 30 broadcast address) | No reply, but no error | Broadcast address itself isn't a host; used to demonstrate broadcast scope, not a real ping target |

---

## 8. Common Mistakes (the 80/20)

1. **Creating the VLAN but never assigning any port to it.** `vlan 10` / `name Engineering` only adds a database entry — until `switchport access vlan 10` is applied to a specific interface, that port stays in VLAN 1 (or whatever it was before), and the device plugged into it silently sits on the wrong subnet.
2. **Forgetting `switchport mode access` before `switchport access vlan`.** On most switch platforms this doesn't block the VLAN assignment, but leaving the port's mode to DTP's default negotiation is a bad habit that will bite you the moment trunking enters the picture in later labs — always set it explicitly.
3. **Putting a router interface's IP in the wrong VLAN's subnet.** E.g., accidentally configuring Gi0/1 (meant for HR, `10.0.0.64/26`) with an Engineering-range address. The interface still comes up fine — IOS has no way to know it's "wrong" — but PCs in that VLAN can't reach their gateway, and this is one of the harder mistakes to spot without carefully re-checking Section 6.4's table.
4. **Computing the gateway as the *first* usable address out of habit.** This lab specifically uses the *last* usable address (`.62`, `.126`, `.190`) — muscle memory from other labs (including Day 01) leads students to default to `.1`-style addressing. Double-check Section 4.3 before assigning PC gateways.
5. **Cabling all three SW1↔R1 links to the same VLAN by mistake.** If, say, Fa0/22, Fa0/23, and Fa0/24 are all left in VLAN 10 (or all accidentally assigned to VLAN 1), R1 will have three interfaces that all report reachable but inter-VLAN routing will behave unpredictably. Verify each R1-facing port's VLAN individually with `show vlan brief`.
6. **Forgetting `no shutdown` on either the switch access port or the router interface.** Same as every prior lab — this remains the single most common root cause of "it's cabled and configured but still doesn't work."
7. **Expecting a broadcast (e.g., a discovery protocol or `255.255.255.255`) to cross VLANs.** Some students initially read a failed cross-VLAN broadcast as a misconfiguration bug. It's expected, correct behavior — that's the entire point of Section 7.3's broadcast row, and confirms VLANs are working, not that something is broken.
8. **Not saving before power-cycling.** `copy running-config startup-config` — same as always.

---

## 9. Troubleshooting Guide

Work through these **in order** — each step assumes the previous one passed.

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC can't reach its own gateway | Wrong IP/mask/gateway on the PC, or its switch port isn't `no shutdown` | `ipconfig` (PC), `show interfaces status` (SW1) | Correct the PC's IP config; bring up the switch port |
| 2 | PC's port shows `connected` but in the wrong VLAN column | Missing or wrong `switchport access vlan <id>` | `show vlan brief` | Re-apply the correct `switchport access vlan` command on that interface |
| 3 | R1 interface shows `administratively down` | Forgot `no shutdown` on R1's side of the link | `show ip interface brief` | Enter the interface and run `no shutdown` |
| 4 | R1 interface is `up/up` but a whole VLAN can't reach its gateway | R1's interface IP is in the wrong subnet for that VLAN | `show run \| section interface` and compare against Section 6.4 | Correct the IP address on the mismatched R1 interface |
| 5 | Same-VLAN PCs can ping each other but no inter-VLAN traffic works at all | R1-facing switch port is in the wrong VLAN, or that R1 interface is down | `show vlan brief` + `show ip interface brief` on R1 | Fix the port's VLAN assignment or bring up the router interface |
| 6 | Inter-VLAN ping works from A to B but not B to A | Asymmetric misconfiguration — one PC has a wrong gateway or mask | `ipconfig` on both PCs | Correct whichever PC's gateway/mask doesn't match Section 6.3 |
| 7 | Broadcast traffic unexpectedly appears in a different VLAN | A port was left in the wrong VLAN, effectively bridging two departments' broadcast domains | `show vlan brief`, verify every port's VLAN membership | Reassign the misplaced port to its correct VLAN |
| 8 | SSH fails to SW1 or R1 | RSA key not generated, or `transport input ssh` missing | `show crypto key mypubkey rsa` | Re-run `crypto key generate rsa`, verify `line vty` settings |
| 9 | Config disappears after a reload | Forgot to save | `show startup-config` vs `show running-config` | `copy running-config startup-config` |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why VLANs at all, instead of just using ACLs on one flat network?** ACLs filter traffic after the fact, on a single shared broadcast domain — every device still receives every broadcast frame regardless of ACL policy, because ACLs operate above Layer 2. VLANs solve the problem at the layer where it actually exists: they create genuinely separate broadcast domains, so an ARP storm or misbehaving NIC in Sales physically cannot flood Engineering's segment, no ACL required.
- **Why one physical interface per VLAN instead of trunking (router-on-a-stick) here?** This lab is deliberately the "long way" to teach the underlying mechanics before abstracting them. With one interface per VLAN, every design decision is visible and physical: this cable is Engineering's gateway path, full stop. Router-on-a-stick (a later lab) replaces 3 physical links with 1 trunk + 3 logical subinterfaces — more scalable, but it hides exactly how VLAN tagging and interface-to-subnet mapping work unless you've built the "hard way" version first.
- **Why size each department at `/26` instead of giving each its own `/24`?** Three separate `/24`s would work but wastes 90%+ of each block's address space on departments with single-digit host counts today. A `/26` gives 62 usable addresses per department — generous room to grow — while still fitting all three inside one `10.0.0.0/24` block, leaving `.192/26` free for a future 4th department without renumbering anyone.
- **Why place the gateway at the last usable address instead of the first?** There's no technical advantage either way — IOS doesn't care. This lab uses "last usable" specifically so you practice the *general* skill (computing broadcast address minus 1) rather than memorizing "gateway is always `.1`," which would leave you stuck the first time you inherit a network built with a different convention.
- **Why no trunking, no VTP, no inter-switch links here?** This is a single-switch lab. Trunking exists to carry multiple VLANs across a link between two switches (or a switch and a router-on-a-stick router) — with only one switch and every VLAN terminating locally, there's nothing that needs to carry more than one VLAN over any single physical link yet.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a growing company moves from a single open-plan office (flat network) into a floor with clearly defined departments, and IT is asked to make sure "HR's stuff doesn't leak onto the general network" — this is the exact VLAN segmentation shown here, minus the "we'll add trunking later" caveat.
- ...you're auditing a small business's network and find every department on VLAN 1 — a real and common finding — and have to design a segmentation plan like this one as a remediation step.
- ...a junior engineer asks "why can't Sales ping Engineering even though they're on the same switch" and the answer is exactly what Section 7.3's broadcast row demonstrates: VLANs are separate broadcast domains, and routing (not switching) is what connects them.
- ...you inherit a network that mixes gateway-at-`.1` and gateway-at-last-usable conventions across different sites (common after a merger or acquisition) and need to be equally comfortable reading either.
- ...a company outgrows the "one router port per VLAN" design (as this lab uses) once they need a 10th or 20th VLAN and don't have that many spare router/switch ports — this is precisely the business trigger that justifies migrating to router-on-a-stick or a Layer 3 switch.

---

## 12. Stretch Goal

Once the base lab works end-to-end, try one or more of the following without referring back to the steps above:

1. **Add a 4th VLAN (VLAN 40, "Guest")** using the remaining `10.0.0.192/26` block. Compute its network, gateway (last usable address), first host, last host, and broadcast address by hand, then wire and configure it exactly like the other three — noting that R1 will need a 4th physical interface, which is precisely the scaling limitation Section 10 describes.
2. **Break VLAN assignment on purpose, then fix it using only `show` commands** (no peeking at your own running-config) — move one PC's port to the wrong VLAN, confirm it can no longer reach its gateway, diagnose using `show vlan brief`, then correct it.
3. **Predict, then verify, what happens to `show ip route` if you `shutdown` one of R1's three interfaces.** Which VLAN loses connectivity, and does it affect the other two VLANs' inter-VLAN routing?
4. **Research (don't configure yet) how router-on-a-stick would replace this entire design with a single trunk link and 3 subinterfaces** — sketch what the R1 config would look like, to prime yourself for the lab that introduces it.

---

## 13. Self-Assessment

Before moving to the next lab, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, why VLANs create separate broadcast domains while a single flat switch does not?
- [ ] Can you compute a `/26` subnet mask in binary and decimal without looking it up?
- [ ] Given any `/26` network address, can you find its last usable host address by hand (broadcast − 1)?
- [ ] Can you write the two commands needed to create and name a VLAN, and the two commands needed to assign a port to it, without looking?
- [ ] Can you explain why this lab needed zero static routes on R1, and how that differs from Day 01?
- [ ] Can you explain what a TTL of 127 (instead of 128) on a ping result tells you about the path the packet took?
- [ ] Can you name at least 4 of the 8 common mistakes from Section 8 without looking?
- [ ] Could you explain, in under 2 minutes, why a business would segment departments into VLANs, to a non-technical manager?

If you answered "no" to more than two of these, re-do the lab from scratch before moving on.

---

## 14. Key Concepts Demonstrated

- **VLANs as separate broadcast domains** — logical segmentation of a single physical switch into isolated Layer 2 segments
- **Access port VLAN assignment** — `switchport mode access` + `switchport access vlan <id>` as the two commands that actually place a port in a VLAN
- **Inter-VLAN routing without trunking** — one router interface per VLAN, each directly connected to that VLAN's subnet
- **Subnetting a /24 into multiple /26 blocks** — block-size math and boundary alignment, reused from Day 01 at a different prefix length
- **Non-conventional gateway placement** — computing "last usable address" instead of defaulting to `.1`
- **Broadcast domain verification** — confirming, empirically, that routers do not forward broadcast traffic between VLANs

---

## 15. What I Learned

This lab made the distinction between switching and routing concrete in a way flat-network labs can't. Before R1's interfaces were configured, VLANs 10/20/30 existed and PCs could reach devices in their own VLAN, but there was no way for HR to reach Engineering — not because of any security policy, but because nothing was routing between the three separate broadcast domains yet. Adding one directly-connected router interface per VLAN was enough to enable full inter-VLAN reachability, with zero static routes required, since every subnet was directly attached to R1.

The broadcast domain test was the most convincing part of the lab: watching a broadcast stay contained to its own VLAN, while unicast pings crossed VLANs cleanly through R1, is the clearest possible demonstration of why VLANs matter — segmentation isn't about blocking all traffic between departments, it's about controlling exactly what crosses (unicast, routed, intentional) versus what never should (broadcast, flooded, incidental).

This lab is the foundation for what comes next:
- Trunking and 802.1Q tagging
- Router-on-a-stick (subinterfaces replacing one-interface-per-VLAN)
- VTP and multi-switch VLAN propagation
- Layer 3 switching (SVIs performing inter-VLAN routing without an external router)

---

## 16. Skills Practiced

- VLAN creation, naming, and port assignment
- Subnetting a /24 into multiple /26 department blocks by hand
- Non-conventional gateway placement (last usable address)
- Inter-VLAN routing via directly connected router interfaces
- PC IP/gateway configuration across multiple subnets
- Broadcast domain verification and TTL-based path analysis
- Structured troubleshooting of VLAN/port/interface mismatches

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology that mirrors the design above using free, open-source images, built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Router (R1) | Cisco 2911 | VyOS |
| Switch (SW1) | Cisco 2960 | Open vSwitch |
| PCs (PC1–PC6) | Generic PC | Linux (Alpine) |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script. Note that VyOS's VLAN/interface syntax differs from Cisco IOS, and Open vSwitch's VLAN tagging is configured differently from IOS `switchport` commands — a brief command-mapping section is included in the GNS3 README so the *concepts* (access ports, per-VLAN router interfaces) transfer even though the exact commands don't.
