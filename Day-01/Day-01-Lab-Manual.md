# Day 01 Lab Manual — Network Devices & Enterprise Topology

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build and configure a two-branch enterprise topology (New York, Tokyo) connected over a simulated WAN, with two different firewall placement strategies, NAT/PAT, static routing, and basic device hardening. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): device roles, topology. Domain 4 (IP Connectivity): static routing. Domain 5 (Security Fundamentals): device hardening, ACLs, NAT concepts, firewall placement. |
| **Prerequisites** | Basic binary/decimal conversion, IPv4 addressing and subnetting fundamentals, familiarity with a terminal/console interface. No prior CCNA lab experience required — this is Day 1. |
| **Time Estimate** | 2.5 – 3.5 hours (first attempt); 45–60 minutes on repeat/review. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner-Intermediate) — conceptually simple devices, but the volume of devices (10) and the ASA firewall CLI (unfamiliar to first-time CCNA students) add real time cost. |

---

## 1. Lab Overview

This lab simulates a company with two branch offices — **New York** and **Tokyo** — connected through a simulated internet/WAN core, with an external **attacker** host used to illustrate perimeter security concepts.

The two branches intentionally use **different firewall placements**:

- **New York** — firewall sits *outside* the router (Router → Firewall → Internet), meaning the router handles internal routing before the firewall inspects traffic leaving the site.
- **Tokyo** — firewall sits *inside*, directly off the switch (Switch → Firewall → Router), meaning traffic is inspected immediately as it leaves the server segment, before it ever reaches routing infrastructure.

This manual walks through building the topology from scratch, with full CLI configuration for every device, an IP addressing plan, expected output at every verification point, common mistakes, structured troubleshooting, and design reasoning.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Identify the role of routers, switches, firewalls, endpoints, and servers in an enterprise network
- Build and cable a two-branch topology with a simulated internet core
- Assign a structured IP addressing scheme across LAN and WAN links
- Configure Cisco IOS routers and switches with basic security and routing
- Configure a Cisco ASA 5505 firewall (interfaces, NAT/PAT, routing, and ACLs) in two different placements
- Verify end-to-end reachability and explain why the attacker cannot reach internal hosts by default
- Troubleshoot common connectivity issues in a multi-device topology
- Articulate, in business terms, why a company would design a network this way

---

## 2. Business Context

**Why would a real company do this?**

Imagine you're the sole network engineer at a mid-sized company that just opened a second office in Tokyo to be closer to a manufacturing partner. Leadership's requirements, translated from a planning meeting into network language, look like this:

- **"Employees in New York need internet access to do their jobs"** → NY branch needs a LAN-to-WAN path with a firewall protecting outbound/inbound traffic.
- **"Our Tokyo office holds sensitive production data on local servers"** → Tokyo's design prioritizes protecting those servers *immediately*, not two hops downstream. This is why the firewall sits directly off the Tokyo switch instead of behind the router — the servers are the "crown jewels," so security is pushed as close to them as possible.
- **"We can't have a single global firewall policy — each site has different risk profiles"** → demonstrated by NY and Tokyo using different placements for the same device type. In the real world, this happens constantly: a retail storefront's firewall design looks nothing like a datacenter's, even inside the same company.
- **"We need to prove to auditors that external parties can't just wander into our network"** → the Attacker host isn't a toy; it's the equivalent of a penetration test host used to validate that "deny by default, permit by exception" is actually enforced, not just documented in a policy binder.
- **"We can't afford downtime figuring out routing from scratch every time something changes"** → static routing is deliberately used here (pre-OSPF) because a two-router, two-firewall network is small enough that static routes are still the *right* engineering choice — dynamic routing protocols add complexity that isn't justified yet. This mirrors real small-business/branch deployments, which frequently stay on static routing indefinitely.

This is the kind of topology a network engineer builds in their first 90 days at a growing company with 2–3 sites: nothing exotic, but every design decision has a business reason behind it.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-01-Network-Devices.png" alt="Day 01 Network Devices Lab" width="900">
</p>

### 3.1 Traffic Flow Summary

```text
NEW YORK BRANCH
PC0/PC1 -- SW1 -- R1 -- FW1(ASA) -- [WAN] -- ISP-RTR

TOKYO BRANCH
SRV1/SRV2 -- SW2 -- FW2(ASA) -- R2 -- [WAN] -- ISP-RTR

WAN / INTERNET CORE
ISP-RTR -- Attacker Laptop
```

### 3.2 Equipment List

| Branch      | Device            | Model              | Hostname Used Below |
|-------------|-------------------|---------------------|----------------------|
| New York    | Switch            | Cisco 2960-24TT     | `NY-SW1`             |
| New York    | Router            | Cisco 2911          | `NY-R1`              |
| New York    | Firewall          | Cisco ASA 5505      | `NY-FW1`             |
| New York    | PC x2             | Generic PC          | `PC0`, `PC1`         |
| Tokyo       | Switch            | Cisco 2960-24TT     | `TOKYO-SW2`          |
| Tokyo       | Firewall          | Cisco ASA 5505      | `TOKYO-FW2`          |
| Tokyo       | Router            | Cisco 2911          | `TOKYO-R2`           |
| Tokyo       | Server x2         | Generic Server      | `SRV1`, `SRV2`       |
| WAN Core    | Router            | Cisco 2911          | `ISP-RTR`            |
| External    | Laptop            | Generic Laptop      | `ATTACKER`           |

> **Note on realism:** Since this lab is pre-VLAN/pre-OSPF (those are Day 2+ topics), all switches use the default VLAN 1, and all routing is done with static/default routes rather than a dynamic routing protocol.

---

## 4. IP Addressing Plan

Plan every interface before touching the CLI — this is the single biggest time-saver in enterprise labs.

| Segment                        | Network            | Usable Range          |
|---------------------------------|---------------------|------------------------|
| New York LAN (PCs)              | 192.168.10.0 /24    | .1 – .254              |
| NY-R1 ↔ NY-FW1 transit link     | 192.168.100.0 /30   | .1 – .2                |
| NY-FW1 ↔ ISP-RTR (WAN)          | 203.0.113.0 /30     | .1 – .2                |
| Tokyo LAN (Servers)              | 192.168.20.0 /24    | .1 – .254              |
| TOKYO-FW2 ↔ TOKYO-R2 transit    | 192.168.200.0 /30   | .1 – .2                |
| TOKYO-R2 ↔ ISP-RTR (WAN)        | 203.0.113.4 /30     | .5 – .6                |
| ISP-RTR ↔ Attacker              | 203.0.113.8 /29     | .9 – .14               |

### 4.1 Why Each Subnet Is Sized the Way It Is

Every network above was sized to the **minimum block that fits the number of hosts that will ever sit on it** — no more, no less. This is deliberate: oversized subnets waste address space and make the addressing table lie about how many devices actually belong on a segment.

| Segment | Hosts needed | Why this prefix |
|---|---|---|
| New York LAN | 2 PCs today, room to grow | `/24` (254 usable) — generous headroom because this is a real user LAN that will add printers, phones, more PCs over time |
| Tokyo LAN | 2 servers today, room to grow | `/24` (254 usable) — same reasoning; server segments also tend to grow |
| NY-R1 ↔ NY-FW1 | Exactly 2 (one on each end) | `/30` (2 usable) — a point-to-point link between exactly two interfaces will *never* need a third address, so anything bigger is pure waste |
| NY-FW1 ↔ ISP-RTR | Exactly 2 | `/30` — same reasoning |
| TOKYO-FW2 ↔ TOKYO-R2 | Exactly 2 | `/30` — same reasoning |
| TOKYO-R2 ↔ ISP-RTR | Exactly 2 | `/30` — same reasoning |
| ISP-RTR ↔ Attacker | 2 today (ISP-RTR's interface + Attacker), sized with slightly more headroom to demonstrate a `/29` | `/29` (6 usable) — chosen here specifically so you practice a subnet size other than `/24` and `/30` |

**The rule of thumb used throughout this course:** *count the maximum number of hosts that will ever realistically sit on that specific broadcast domain, then pick the smallest power-of-two block that covers it (plus network and broadcast address).* A transit link between two routers is always exactly 2 hosts, forever — so it is always a `/30` (or a `/31` in point-to-point-only designs, though `/30` is what CCNA expects you to default to). A LAN full of end-user devices is sized with growth room because printers, phones, and new hires show up constantly.

### 4.2 How to Calculate These by Hand

You will not always have a table handed to you — on the exam and in the field, you derive addressing plans yourself. Here is the manual process, using two examples from this lab.

**Step 1 — Convert the requirement to a number of usable hosts.**

A point-to-point router-to-router or router-to-firewall link always needs exactly **2** usable addresses (one per end). A subnet formula host count is:

```text
usable hosts = 2^h − 2
```

where `h` is the number of *host bits* (bits left after the network portion), and the `−2` removes the network address and broadcast address, which can't be assigned to a device.

**Step 2 — Solve for the smallest `h` that satisfies your requirement.**

For the transit links (need 2 hosts):

```text
2^h − 2 ≥ 2
2^1 − 2 = 0   → too small
2^2 − 2 = 2   → exactly fits
```

So `h = 2` host bits. A /30 in binary is 11111111.11111111.11111111.111111**00** — the last 2 bits are host bits. That's your `/30`.

For the ISP-RTR ↔ Attacker segment (sized for 6 hosts):

```text
2^h − 2 ≥ 6
2^2 − 2 = 2   → too small
2^3 − 2 = 6   → exactly fits
```

So `h = 3` host bits → 32 − 3 = **/29**.

**Step 3 — Convert the prefix length to a dotted-decimal subnet mask.**

Write out 32 bits, set the first `(32 − h)` bits to 1 and the rest to 0, then convert each octet back to decimal:

```text
/30 = 11111111.11111111.11111111.11111100
    =     255  .    255 .    255 .   252
```

```text
/29 = 11111111.11111111.11111111.11111000
    =     255  .    255 .    255 .   248
```

**Memory aid for common CCNA masks** — memorize this table instead of re-deriving it every time:

| Prefix | Host bits | Usable hosts | Last octet (decimal) |
|---|---|---|---|
| /24 | 8 | 254 | .0 |
| /25 | 7 | 126 | .128 |
| /26 | 6 | 62  | .192 |
| /27 | 5 | 30  | .224 |
| /28 | 4 | 14  | .240 |
| /29 | 3 | 6   | .248 |
| /30 | 2 | 2   | .252 |

Notice the last-octet values are `256 − 2^h`. That single formula (`256 minus 2 to the host-bit power`) is the fastest mental-math shortcut for producing a mask from a host count without writing out binary at all.

**Step 4 — Identify network address, first/last usable host, and broadcast address.**

Take the `192.168.100.0/30` link (NY-R1 ↔ NY-FW1) as a worked example:

```text
Network address:    192.168.100.0    (all host bits = 0)
First usable host:  192.168.100.1    (network address + 1)
Last usable host:   192.168.100.2    (broadcast address − 1)
Broadcast address:  192.168.100.3    (all host bits = 1)
```

With only 2 usable hosts, they're always `.1` and `.2` — this is why every `/30` transit link in this lab follows the same `.1` / `.2` pattern.

For the `/29` block `203.0.113.8/29`:

```text
Network address:    203.0.113.8     (all 3 host bits = 000 → .8)
First usable host:  203.0.113.9     (.8 + 1)
Last usable host:   203.0.113.14    (.8 + 6, since 6 usable hosts)
Broadcast address:  203.0.113.15    (all 3 host bits = 111 → .8 + 7)
```

**Step 5 — Double-check with the "block size" shortcut.**

The block size (how far apart consecutive subnets of the same prefix are) equals `256 − last-octet-mask-value`. For `/29` (mask ends in .248): block size = `256 − 248 = 8`. So `/29` networks always land on multiples of 8: `.0, .8, .16, .24...`. This is how `203.0.113.8/29` was chosen to start cleanly on a block boundary rather than an arbitrary number — always snap your subnet boundaries to multiples of the block size, never split them mid-block.

### 4.3 Full Device Address Table

| Device      | Interface        | IP Address        | Mask              | Connects To            |
|-------------|-------------------|--------------------|--------------------|--------------------------|
| PC0         | NIC               | 192.168.10.10      | 255.255.255.0      | NY-SW1 Fa0/1            |
| PC1         | NIC               | 192.168.10.11      | 255.255.255.0      | NY-SW1 Fa0/2            |
| NY-SW1      | VLAN 1 (mgmt)     | 192.168.10.2       | 255.255.255.0      | n/a                      |
| NY-R1       | Gi0/0             | 192.168.10.1       | 255.255.255.0      | NY-SW1 Fa0/24           |
| NY-R1       | Gi0/1             | 192.168.100.1      | 255.255.255.252    | NY-FW1 inside (E0/1)    |
| NY-FW1      | VLAN1 (inside)    | 192.168.100.2      | 255.255.255.252    | NY-R1 Gi0/1             |
| NY-FW1      | VLAN2 (outside)   | 203.0.113.1        | 255.255.255.252    | ISP-RTR Gi0/0           |
| ISP-RTR     | Gi0/0             | 203.0.113.2        | 255.255.255.252    | NY-FW1 outside          |
| ISP-RTR     | Gi0/1             | 203.0.113.6        | 255.255.255.252    | TOKYO-R2 Gi0/1          |
| ISP-RTR     | Gi0/2             | 203.0.113.9        | 255.255.255.248    | ATTACKER                |
| ATTACKER    | NIC               | 203.0.113.10       | 255.255.255.248    | ISP-RTR Gi0/2           |
| TOKYO-R2    | Gi0/1             | 203.0.113.5        | 255.255.255.252    | ISP-RTR Gi0/1           |
| TOKYO-R2    | Gi0/0             | 192.168.200.2      | 255.255.255.252    | TOKYO-FW2 outside       |
| TOKYO-FW2   | VLAN2 (outside)   | 192.168.200.1      | 255.255.255.252    | TOKYO-R2 Gi0/0          |
| TOKYO-FW2   | VLAN1 (inside)    | 192.168.20.1       | 255.255.255.0      | TOKYO-SW2 Fa0/24        |
| TOKYO-SW2   | VLAN 1 (mgmt)     | 192.168.20.2       | 255.255.255.0      | n/a                      |
| SRV1        | NIC               | 192.168.20.10      | 255.255.255.0      | TOKYO-SW2 Fa0/1         |
| SRV2        | NIC               | 192.168.20.11      | 255.255.255.0      | TOKYO-SW2 Fa0/2         |

**Default gateways:** PC0/PC1 → `192.168.10.1`; SRV1/SRV2 → `192.168.20.1`; Attacker → `203.0.113.9`.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Place all devices in Packet Tracer matching the topology image.
2. Cable using **copper straight-through** for PC/Server-to-switch and router/firewall-to-switch links, and **copper straight-through** for router-to-router/firewall links (Packet Tracer auto-detects crossover needs on most modern platforms, but verify link lights turn green).
3. Confirm interface numbering in Packet Tracer matches what's used below — if your platform assigns different port numbers (e.g., `FastEthernet0/0` instead of `GigabitEthernet0/0`), substitute accordingly.
4. Have the addressing table above open in a second window for reference.

---

## 6. Part 1 — New York Branch Configuration

### 6.1 NY-SW1 (Cisco 2960-24TT)

**Step 1: Enter global configuration and set the hostname**

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname NY-SW1
```

- **Mode:** User EXEC → Privileged EXEC → Global Config
- **`enable`** unlocks Privileged EXEC (view-everything, change-nothing yet). **`configure terminal`** enters the mode where device-wide settings live. **`hostname`** renames the device so its prompt and `show run` output are unambiguous once you're managing 10 devices in one session.

**Step 2: Secure device access**

```text
NY-SW1(config)#enable secret class
NY-SW1(config)#service password-encryption
NY-SW1(config)#line console 0
NY-SW1(config-line)#password cisco
NY-SW1(config-line)#login
NY-SW1(config-line)#exit
```

> `enable secret` sets an MD5-hashed privileged mode password — always prefer this over the plaintext `enable password`. `service password-encryption` weakly (type-7, reversible) obscures the remaining plaintext passwords in the running-config; it's not cryptographically strong, but it's standard practice so a shoulder-surfed `show run` doesn't hand over a password in clear text. `password` sets the console password; `login` is what actually *enforces* it — without `login`, the password is stored but never asked for.

**Step 3: Add a warning banner**

```text
NY-SW1(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. NY-SW1 - Authorized Use Only.
#
```

> The `#` delimiter marks the start/end of the message (any character not used inside the message works). Legally, an explicit banner strengthens an "unauthorized access" case; without one, "implied consent" arguments are weaker.

**Step 4: Configure the management SVI (VLAN 1)**

```text
NY-SW1(config)#interface vlan 1
NY-SW1(config-if)#ip address 192.168.10.2 255.255.255.0
NY-SW1(config-if)#no shutdown
NY-SW1(config-if)#exit
NY-SW1(config)#ip default-gateway 192.168.10.1
```

> A Layer 2 switch doesn't route, but it needs an IP on its management VLAN so you can Telnet/SSH into it for remote administration. `ip default-gateway` (not `ip route`) is used on L2 switches to reach management traffic off-subnet.

**Step 5: Configure access ports for PC0 and PC1**

```text
NY-SW1(config)#interface fastEthernet 0/1
NY-SW1(config-if)#description Link to PC0
NY-SW1(config-if)#switchport mode access
NY-SW1(config-if)#spanning-tree portfast
NY-SW1(config-if)#no shutdown
NY-SW1(config-if)#exit
NY-SW1(config)#interface fastEthernet 0/2
NY-SW1(config-if)#description Link to PC1
NY-SW1(config-if)#switchport mode access
NY-SW1(config-if)#spanning-tree portfast
NY-SW1(config-if)#no shutdown
NY-SW1(config-if)#exit
```

> `spanning-tree portfast` skips the STP listening/learning delay (~30 seconds) on ports connected to end hosts (never on ports connecting to other switches — that risks a loop going undetected).

**Step 6: Configure the uplink to NY-R1**

```text
NY-SW1(config)#interface fastEthernet 0/24
NY-SW1(config-if)#description Uplink to NY-R1 Gi0/0
NY-SW1(config-if)#switchport mode access
NY-SW1(config-if)#no shutdown
NY-SW1(config-if)#exit
```

**Step 7: Enable SSH for remote management**

```text
NY-SW1(config)#ip domain-name labnet.local
NY-SW1(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
NY-SW1(config)#username admin secret cisco123
NY-SW1(config)#line vty 0 15
NY-SW1(config-line)#login local
NY-SW1(config-line)#transport input ssh
NY-SW1(config-line)#exit
```

> SSH requires a domain name and an RSA keypair to exist before it can operate (the key is what encrypts the session). `login local` authenticates against locally-defined usernames instead of a single shared line password — this is what lets you have distinct, attributable admin logins.

**Step 8: Save**

```text
NY-SW1#copy running-config startup-config
```

---

### 6.2 NY-R1 (Cisco 2911)

**Step 1: Hostname and basic hardening**

```text
Router>enable
Router#configure terminal
Router(config)#hostname NY-R1
NY-R1(config)#no ip domain-lookup
NY-R1(config)#enable secret class
NY-R1(config)#service password-encryption
NY-R1(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. NY-R1 - Authorized Use Only.
#
```

> `no ip domain-lookup` stops the router from trying to DNS-resolve mistyped commands, which otherwise causes an annoying ~30 second hang every time you fat-finger a command.

**Step 2: Console and VTY access**

```text
NY-R1(config)#line console 0
NY-R1(config-line)#password cisco
NY-R1(config-line)#login
NY-R1(config-line)#exit
NY-R1(config)#ip domain-name labnet.local
NY-R1(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
NY-R1(config)#username admin secret cisco123
NY-R1(config)#line vty 0 4
NY-R1(config-line)#login local
NY-R1(config-line)#transport input ssh
NY-R1(config-line)#exit
```

**Step 3: Configure the LAN interface (toward NY-SW1)**

```text
NY-R1(config)#interface gigabitEthernet 0/0
NY-R1(config-if)#description LAN - NY-SW1
NY-R1(config-if)#ip address 192.168.10.1 255.255.255.0
NY-R1(config-if)#no shutdown
NY-R1(config-if)#exit
```

**Step 4: Configure the link toward NY-FW1**

```text
NY-R1(config)#interface gigabitEthernet 0/1
NY-R1(config-if)#description To NY-FW1 inside
NY-R1(config-if)#ip address 192.168.100.1 255.255.255.252
NY-R1(config-if)#no shutdown
NY-R1(config-if)#exit
```

**Step 5: Default route toward the firewall**

```text
NY-R1(config)#ip route 0.0.0.0 0.0.0.0 192.168.100.2
```

> Since NY-R1 sits *before* the firewall in this design, every packet that isn't destined for its own LAN gets forwarded to NY-FW1's inside interface, which then applies security policy and NATs it before it ever reaches the WAN.

**Step 6: Save**

```text
NY-R1#copy running-config startup-config
```

---

### 6.3 NY-FW1 (Cisco ASA 5505)

The ASA 5505 has 8 switch ports built in. By default `Ethernet0/0` is the only port allowed on VLAN 2 (outside) unless reassigned; `Ethernet0/1–0/7` are on VLAN 1 (inside) on the Base license (no trunking without Security Plus).

**Step 1: Hostname and basic setup**

```text
ciscoasa>enable
Password:
ciscoasa#configure terminal
ciscoasa(config)#hostname NY-FW1
NY-FW1(config)#domain-name labnet.local
NY-FW1(config)#enable password class
NY-FW1(config)#passwd cisco
```

**Step 2: Assign physical ports to VLANs**

```text
NY-FW1(config)#interface ethernet0/0
NY-FW1(config-if)#switchport access vlan 2
NY-FW1(config-if)#no shutdown
NY-FW1(config-if)#exit
NY-FW1(config)#interface ethernet0/1
NY-FW1(config-if)#switchport access vlan 1
NY-FW1(config-if)#no shutdown
NY-FW1(config-if)#exit
```

> Ethernet0/0 (facing ISP-RTR) → VLAN 2 = outside. Ethernet0/1 (facing NY-R1) → VLAN 1 = inside.

**Step 3: Configure the VLAN interfaces**

```text
NY-FW1(config)#interface vlan 1
NY-FW1(config-if)#nameif inside
NY-FW1(config-if)#security-level 100
NY-FW1(config-if)#ip address 192.168.100.2 255.255.255.252
NY-FW1(config-if)#no shutdown
NY-FW1(config-if)#exit
NY-FW1(config)#interface vlan 2
NY-FW1(config-if)#nameif outside
NY-FW1(config-if)#security-level 0
NY-FW1(config-if)#ip address 203.0.113.1 255.255.255.252
NY-FW1(config-if)#no shutdown
NY-FW1(config-if)#exit
```

> **Security levels** are the core of ASA policy: 100 = fully trusted (inside), 0 = fully untrusted (outside). Traffic flows freely from a higher security level to a lower one (inside → outside), but traffic from a lower to a higher level (outside → inside) is denied unless explicitly permitted by an ACL — the "default deny inbound" behavior that protects the branch.

**Step 4: Static routes**

```text
NY-FW1(config)#route inside 192.168.10.0 255.255.255.0 192.168.100.1
NY-FW1(config)#route outside 0.0.0.0 0.0.0.0 203.0.113.2
```

> The `route inside` statement tells the ASA that the PC subnet lives behind NY-R1, not directly on its inside interface. The `route outside` statement is the ASA's default route to reach anything beyond the WAN.

**Step 5: NAT / PAT for internet access**

```text
NY-FW1(config)#object network NY-LAN
NY-FW1(config-network-object)#subnet 192.168.10.0 255.255.255.0
NY-FW1(config-network-object)#nat (inside,outside) dynamic interface
NY-FW1(config-network-object)#exit
```

> This translates any source address in `192.168.10.0/24` to the ASA's own outside interface IP (203.0.113.1) using **Port Address Translation (PAT)** as traffic leaves toward the WAN — the same mechanism your home router uses to share one public IP among many devices.

**Step 6: Save**

```text
NY-FW1(config)#exit
NY-FW1#write memory
```

---

### 6.4 PC0 and PC1

In Packet Tracer, open each PC → **Desktop tab → IP Configuration**:

| Field           | PC0             | PC1             |
|------------------|------------------|------------------|
| IP Address       | 192.168.10.10    | 192.168.10.11    |
| Subnet Mask      | 255.255.255.0    | 255.255.255.0    |
| Default Gateway  | 192.168.10.1     | 192.168.10.1     |

---

## 7. Part 2 — WAN Core: ISP-RTR

**Step 1: Hostname and basic hardening**

```text
Router>enable
Router#configure terminal
Router(config)#hostname ISP-RTR
ISP-RTR(config)#no ip domain-lookup
ISP-RTR(config)#enable secret class
ISP-RTR(config)#service password-encryption
ISP-RTR(config)#banner motd #
SIMULATED INTERNET CORE - ISP-RTR
#
```

**Step 2: Configure the three interfaces**

```text
ISP-RTR(config)#interface gigabitEthernet 0/0
ISP-RTR(config-if)#description To NY-FW1 outside
ISP-RTR(config-if)#ip address 203.0.113.2 255.255.255.252
ISP-RTR(config-if)#no shutdown
ISP-RTR(config-if)#exit
ISP-RTR(config)#interface gigabitEthernet 0/1
ISP-RTR(config-if)#description To TOKYO-R2
ISP-RTR(config-if)#ip address 203.0.113.6 255.255.255.252
ISP-RTR(config-if)#no shutdown
ISP-RTR(config-if)#exit
ISP-RTR(config)#interface gigabitEthernet 0/2
ISP-RTR(config-if)#description To ATTACKER
ISP-RTR(config-if)#ip address 203.0.113.9 255.255.255.248
ISP-RTR(config-if)#no shutdown
ISP-RTR(config-if)#exit
```

**Step 3: Static route to reach the Tokyo transit link**

```text
ISP-RTR(config)#ip route 192.168.200.0 255.255.255.252 203.0.113.5
```

> Unlike the New York side (where NAT happens right at the WAN edge on NY-FW1's outside interface, which ISP-RTR is *directly* connected to), Tokyo's NAT happens one hop further in — at TOKYO-FW2, whose outside address (192.168.200.1) sits behind TOKYO-R2. ISP-RTR needs this static route so return traffic for that translated address knows to go via TOKYO-R2.

**Step 4: Save**

```text
ISP-RTR#copy running-config startup-config
```

---

## 8. Part 3 — Tokyo Branch Configuration

### 8.1 TOKYO-SW2 (Cisco 2960-24TT)

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname TOKYO-SW2
TOKYO-SW2(config)#enable secret class
TOKYO-SW2(config)#service password-encryption
TOKYO-SW2(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. TOKYO-SW2 - Authorized Use Only.
#
TOKYO-SW2(config)#interface vlan 1
TOKYO-SW2(config-if)#ip address 192.168.20.2 255.255.255.0
TOKYO-SW2(config-if)#no shutdown
TOKYO-SW2(config-if)#exit
TOKYO-SW2(config)#ip default-gateway 192.168.20.1
```

**Server-facing access ports:**

```text
TOKYO-SW2(config)#interface fastEthernet 0/1
TOKYO-SW2(config-if)#description Link to SRV1
TOKYO-SW2(config-if)#switchport mode access
TOKYO-SW2(config-if)#no shutdown
TOKYO-SW2(config-if)#exit
TOKYO-SW2(config)#interface fastEthernet 0/2
TOKYO-SW2(config-if)#description Link to SRV2
TOKYO-SW2(config-if)#switchport mode access
TOKYO-SW2(config-if)#no shutdown
TOKYO-SW2(config-if)#exit
```

**Uplink to TOKYO-FW2:**

```text
TOKYO-SW2(config)#interface fastEthernet 0/24
TOKYO-SW2(config-if)#description Uplink to TOKYO-FW2 inside
TOKYO-SW2(config-if)#switchport mode access
TOKYO-SW2(config-if)#no shutdown
TOKYO-SW2(config-if)#exit
```

**Enable SSH and save:**

```text
TOKYO-SW2(config)#ip domain-name labnet.local
TOKYO-SW2(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
TOKYO-SW2(config)#username admin secret cisco123
TOKYO-SW2(config)#line vty 0 15
TOKYO-SW2(config-line)#login local
TOKYO-SW2(config-line)#transport input ssh
TOKYO-SW2(config-line)#exit
TOKYO-SW2#copy running-config startup-config
```

---

### 8.2 TOKYO-FW2 (Cisco ASA 5505)

Here the firewall sits **directly off the switch**, not behind a router — this is the key architectural difference from New York.

**Step 1: Basic setup**

```text
ciscoasa>enable
Password:
ciscoasa#configure terminal
ciscoasa(config)#hostname TOKYO-FW2
TOKYO-FW2(config)#domain-name labnet.local
TOKYO-FW2(config)#enable password class
TOKYO-FW2(config)#passwd cisco
```

**Step 2: Assign ports to VLANs**

```text
TOKYO-FW2(config)#interface ethernet0/0
TOKYO-FW2(config-if)#switchport access vlan 2
TOKYO-FW2(config-if)#no shutdown
TOKYO-FW2(config-if)#exit
TOKYO-FW2(config)#interface ethernet0/1
TOKYO-FW2(config-if)#switchport access vlan 1
TOKYO-FW2(config-if)#no shutdown
TOKYO-FW2(config-if)#exit
```

> Ethernet0/0 (facing TOKYO-R2) → VLAN 2 = outside. Ethernet0/1 (facing TOKYO-SW2) → VLAN 1 = inside.

**Step 3: VLAN interfaces**

```text
TOKYO-FW2(config)#interface vlan 1
TOKYO-FW2(config-if)#nameif inside
TOKYO-FW2(config-if)#security-level 100
TOKYO-FW2(config-if)#ip address 192.168.20.1 255.255.255.0
TOKYO-FW2(config-if)#no shutdown
TOKYO-FW2(config-if)#exit
TOKYO-FW2(config)#interface vlan 2
TOKYO-FW2(config-if)#nameif outside
TOKYO-FW2(config-if)#security-level 0
TOKYO-FW2(config-if)#ip address 192.168.200.1 255.255.255.252
TOKYO-FW2(config-if)#no shutdown
TOKYO-FW2(config-if)#exit
```

> Notice TOKYO-FW2's inside interface *is* the server gateway (192.168.20.1) — since there's no router between the switch and the firewall here, the ASA itself terminates the server LAN. This is what "security closer to the resource" means in practice.

**Step 4: Default route**

```text
TOKYO-FW2(config)#route outside 0.0.0.0 0.0.0.0 192.168.200.2
```

**Step 5: NAT/PAT for outbound server traffic**

```text
TOKYO-FW2(config)#object network TOKYO-LAN
TOKYO-FW2(config-network-object)#subnet 192.168.20.0 255.255.255.0
TOKYO-FW2(config-network-object)#nat (inside,outside) dynamic interface
TOKYO-FW2(config-network-object)#exit
```

**Step 6 (Optional but recommended): Publish SRV1's web service to the outside**

This demonstrates *controlled* inbound access — the opposite of the default-deny behavior — and is a good talking point for the attacker simulation in Part 5.

```text
TOKYO-FW2(config)#object network SRV1-WEB
TOKYO-FW2(config-network-object)#host 192.168.20.10
TOKYO-FW2(config-network-object)#nat (inside,outside) static interface service tcp www www
TOKYO-FW2(config-network-object)#exit
TOKYO-FW2(config)#access-list OUTSIDE-IN extended permit tcp any object SRV1-WEB eq www
TOKYO-FW2(config)#access-group OUTSIDE-IN in interface outside
```

> This single static NAT + ACL pair is the *only* hole in an otherwise closed firewall — it forwards outside traffic on TCP/80 to SRV1's web service and nothing else. Everything else inbound is still dropped by the implicit deny.

**Step 7: Save**

```text
TOKYO-FW2(config)#exit
TOKYO-FW2#write memory
```

---

### 8.3 TOKYO-R2 (Cisco 2911)

```text
Router>enable
Router#configure terminal
Router(config)#hostname TOKYO-R2
TOKYO-R2(config)#no ip domain-lookup
TOKYO-R2(config)#enable secret class
TOKYO-R2(config)#service password-encryption
TOKYO-R2(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. TOKYO-R2 - Authorized Use Only.
#
```

**Interfaces:**

```text
TOKYO-R2(config)#interface gigabitEthernet 0/0
TOKYO-R2(config-if)#description To TOKYO-FW2 outside
TOKYO-R2(config-if)#ip address 192.168.200.2 255.255.255.252
TOKYO-R2(config-if)#no shutdown
TOKYO-R2(config-if)#exit
TOKYO-R2(config)#interface gigabitEthernet 0/1
TOKYO-R2(config-if)#description To ISP-RTR
TOKYO-R2(config-if)#ip address 203.0.113.5 255.255.255.252
TOKYO-R2(config-if)#no shutdown
TOKYO-R2(config-if)#exit
```

**Routing:**

```text
TOKYO-R2(config)#ip route 192.168.20.0 255.255.255.0 192.168.200.1
TOKYO-R2(config)#ip route 0.0.0.0 0.0.0.0 203.0.113.6
```

> The first route tells TOKYO-R2 how to reach the actual server subnet (via TOKYO-FW2). The second is the default route out toward the simulated internet.

**SSH access and save:**

```text
TOKYO-R2(config)#ip domain-name labnet.local
TOKYO-R2(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
TOKYO-R2(config)#username admin secret cisco123
TOKYO-R2(config)#line vty 0 4
TOKYO-R2(config-line)#login local
TOKYO-R2(config-line)#transport input ssh
TOKYO-R2(config-line)#exit
TOKYO-R2#copy running-config startup-config
```

---

### 8.4 SRV1 and SRV2

Open each server → **Desktop tab → IP Configuration**:

| Field           | SRV1             | SRV2             |
|------------------|-------------------|-------------------|
| IP Address       | 192.168.20.10     | 192.168.20.11     |
| Subnet Mask      | 255.255.255.0     | 255.255.255.0     |
| Default Gateway  | 192.168.20.1      | 192.168.20.1      |

If your Packet Tracer server model supports it, enable **Services → HTTP** on SRV1 to give the NAT-published web service in step 8.2 something real to reach.

---

## 9. Part 4 — Attacker Laptop

Configure as a simple external host with no route back into either private LAN:

| Field           | Value           |
|------------------|------------------|
| IP Address       | 203.0.113.10     |
| Subnet Mask      | 255.255.255.248  |
| Default Gateway  | 203.0.113.9      |

No CLI configuration is required — this device exists purely to test what an outside party can and cannot reach.

---

## 10. Part 5 — Verification and Expected Output

### 10.1 Device-level verification commands

| Device        | Command                          | What to check                                   |
|----------------|-----------------------------------|--------------------------------------------------|
| Routers        | `show ip interface brief`         | All interfaces `up/up`, correct IPs             |
| Routers        | `show ip route`                   | Connected + static/default routes present        |
| Switches       | `show vlan brief`                 | Ports assigned to VLAN 1 as expected             |
| Switches       | `show interfaces status`          | Ports connected, not err-disabled                |
| ASA firewalls  | `show interface ip brief`         | inside/outside up with correct IPs               |
| ASA firewalls  | `show nat`                        | NAT rule(s) present and hit-count increasing      |
| ASA firewalls  | `show xlate`                      | Active translations after traffic is generated    |
| ASA firewalls  | `show access-list`                | ACL hit counts (Tokyo only)                       |

### 10.2 Expected Output Gallery

This is what **success looks like** at each key checkpoint — compare your output against these exactly.

**`NY-R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         192.168.10.1    YES manual up                    up
GigabitEthernet0/1         192.168.100.1   YES manual up                    up
Vlan1                      unassigned      YES unset  administratively down down
```

Every interface you configured shows `up / up` in the Status/Protocol columns. `Vlan1` being `administratively down / down` is normal on a router — you never configured it.

**`NY-R1# show ip route`**

```text
Gateway of last resort is 192.168.100.2 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 192.168.100.2
      192.168.10.0/24 is directly connected, GigabitEthernet0/0
      192.168.100.0/30 is directly connected, GigabitEthernet0/1
```

The `S*` line is your default route pointing at the firewall — this confirms Step 6.2/5 took effect.

**`NY-FW1# show nat`**

```text
Auto NAT Policies (Section 2)
1 (inside) to (outside) source dynamic NY-LAN interface
    translate_hits = 0, untranslate_hits = 0
```

Immediately after configuration, `translate_hits = 0` is normal — it only increments once a PC actually sends traffic outbound. If it's still 0 after you ping from PC0 to somewhere outside, that's a real problem (see Troubleshooting).

**`NY-FW1# show xlate`** (after PC0 pings ISP-RTR)

```text
1 in use, 1 most used
Flags: D - DNS, e - extended, I - identity, i - dynamic, r - portmap,
       s - static, T - twice, N - net-to-net
NAT from inside:192.168.10.10 to outside:203.0.113.1
    flags ri idle 0:00:02 timeout 0:00:30
```

This confirms PAT is actively translating PC0's real address to the firewall's outside interface.

**`TOKYO-SW2# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
                                                 Fa0/5, Fa0/6, ... Fa0/24
```

All configured ports appear under VLAN 1 with `active` status — since this lab is pre-VLAN, everything correctly lives on the default VLAN.

**`PC0> ping 192.168.20.10`** (full path test, after everything above is complete)

```text
Pinging 192.168.20.10 with 32 bytes of data:

Reply from 192.168.20.10: bytes=32 time=1ms TTL=125
Reply from 192.168.20.10: bytes=32 time=1ms TTL=125
Reply from 192.168.20.10: bytes=32 time=1ms TTL=125
Reply from 192.168.20.10: bytes=32 time=1ms TTL=125

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Four replies, 0% loss — this single command proves every device in both branches is correctly configured, cabled, routed, and NATed end to end. If you see this, the lab is functionally complete.

### 10.3 Ping / Reachability Matrix

| From        | To                          | Expected Result | Why                                                                 |
|-------------|-------------------------------|------------------|----------------------------------------------------------------------|
| PC0         | PC1                           | Success          | Same VLAN/subnet, switched locally                                    |
| PC0         | NY-R1 (192.168.10.1)          | Success          | Directly connected gateway                                            |
| PC0         | SRV1 (192.168.20.10)          | Success          | Full path routed + NATed at both firewalls                            |
| SRV1        | SRV2                          | Success          | Same VLAN/subnet, switched locally                                    |
| PC0         | ISP-RTR outside interfaces    | Success          | Routed hop, no ACL blocking outbound-initiated traffic                |
| ATTACKER    | NY-FW1 outside (203.0.113.1)  | Success (ping)   | Reaching the interface itself is allowed by default on this lab setup |
| ATTACKER    | PC0 (192.168.10.10)           | **Fail**         | Private address hidden behind PAT; no inbound path exists             |
| ATTACKER    | SRV1 (192.168.20.10) direct   | **Fail**         | Private address; not directly reachable                               |
| ATTACKER    | SRV1 web service (TCP/80) via TOKYO-FW2 outside (192.168.200.1) | Success (HTTP only) | Explicit static NAT + ACL permits *only* TCP/80 |
| ATTACKER    | SRV1 via any other port        | **Fail**         | Implicit deny — only port 80 was explicitly opened                    |

Run a `tracert 192.168.20.10` from PC0 to visually confirm the path: `PC0 → NY-R1 → NY-FW1 → ISP-RTR → TOKYO-R2 → TOKYO-FW2 → SRV1`.

### 10.4 What this proves

- **NAT/PAT works** — internal private addresses are never directly exposed to the WAN.
- **Default-deny inbound works** — the attacker cannot reach internal hosts without an explicit rule.
- **Firewall placement doesn't have to be identical everywhere** — New York protects at the WAN edge; Tokyo protects right next to the asset — and both achieve "deny by default, permit by exception."

---

## 11. Common Mistakes (the 80/20)

These account for roughly 80% of the time lost by first-time students on this lab. Check these *before* opening the full troubleshooting guide.

1. **Forgetting `no shutdown` on a newly configured interface.** By far the single most common error. Every physical interface on Cisco IOS boots administratively down. If `show ip interface brief` shows `administratively down`, this is why.
2. **Setting `password` on a VTY/console line but forgetting `login` (or `login local`).** Without it, the device never prompts for the password you just set — leaving the line either wide open or, worse, rejecting all connections depending on IOS defaults. Always pair the two.
3. **Mixing up ASA `nameif` and IOS-style `interface vlan` conventions.** Students who are used to switch VLAN SVIs try to skip `nameif`/`security-level` on the ASA — the ASA won't pass traffic through an interface without both set.
4. **Confusing which side of the ASA is "inside" and "outside" in Tokyo.** Because TOKYO-FW2's *outside* interface faces the router (not the WAN directly), students used to New York's layout mirror the wrong VLAN-to-port mapping. Re-check Step 8.2 Step 2 carefully — Tokyo's E0/0 (VLAN 2/outside) faces TOKYO-R2, not the internet directly.
5. **Forgetting the NAT `object network` + `nat` pair entirely.** Interfaces and routing can be perfect, yet nothing reaches the internet, because the ASA has no rule to translate private addresses. If `show xlate` is empty after generating traffic, this is almost always the cause.
6. **Not saving configuration before closing Packet Tracer or power-cycling a device.** `copy running-config startup-config` (IOS) / `write memory` (ASA) — skipping this erases an hour of work on the next reload.
7. **Typo'ing subnet masks on `/30` transit links** (255.255.255.25**2**, not .255.255.255.255 or .0). A `/30` typo on a point-to-point link is one of the hardest mistakes to spot visually — always double check transit link masks specifically.
8. **Trying to ping across branches before configuring NAT on *both* firewalls.** Traffic can leave New York fine, but if Tokyo's NAT/PAT isn't done yet, the ICMP echo dies trying to route from Tokyo's private subnet.

---

## 12. Troubleshooting Guide

Work through these **in order** — each step assumes the previous one passed.

| Step | Symptom                                             | Likely Cause                                                   | Diagnostic Command | Fix                                                                 |
|---|------------------------------------------------------|-------------------------------------------------------------------|---|-----------------------------------------------------------------------|
| 1 | Interface shows `administratively down`              | Forgot `no shutdown`                                            | `show ip interface brief` | Enter the interface and run `no shutdown`                            |
| 2 | PC can't reach its own gateway                        | Wrong IP/mask on PC or switch port not `no shutdown`             | `show interfaces status` (switch) | Re-check IP config; verify switch port is connected            |
| 3 | PC reaches local LAN but not the other branch          | Missing default route on router or ASA                           | `show ip route` / `show run \| include route` | Add the missing static/default route                 |
| 4 | Ping fails between branches even with routes correct    | NAT not applied, so return traffic has no path back              | `show nat` / `show xlate` | Confirm the `object network` + `nat` statements exist and match       |
| 5 | ASA won't let *any* traffic from inside to outside       | Missing `nat (inside,outside) dynamic interface`                | `show nat` | Re-check the `object network` + `nat` statements                     |
| 6 | ASA drops traffic you expect to allow inbound            | No explicit ACL/static NAT for that service                      | `show access-list` | ASA denies all inbound by default — you must explicitly permit it     |
| 7 | SSH fails to router/switch                              | RSA key not generated, or `transport input ssh` missing            | `show crypto key mypubkey rsa` | Re-run `crypto key generate rsa` and check `line vty` settings        |
| 8 | Config disappears after a device reload                 | Forgot to save                                                    | `show startup-config` vs `show running-config` | Always finish with `copy running-config startup-config` (`write memory` on ASA) |
| 9 | Switch SVI (VLAN 1) won't come up                        | No active access/trunk port in that VLAN, or SVI in `shutdown`    | `show interfaces vlan 1` | Bring up at least one port in VLAN 1, then `no shutdown` the SVI      |

---

## 13. Design Analysis

**Why this design over the alternatives?**

- **Why static routes instead of a dynamic routing protocol (e.g., OSPF)?** With only 2 branch routers and 1 core router, the total number of routes is small and rarely changes — OSPF's convergence benefits don't outweigh the added complexity (neighbor relationships, LSAs, potential misconfiguration surface) at this scale. Static routing is also more predictable for a first CCNA lab: every route in `show ip route` is one you typed, with no "why did this route appear" mystery. This trade-off flips once you add more sites or need automatic failover — that's exactly what Day 24 (Floating Static Routes) and the later OSPF labs build toward.
- **Why put NY's firewall *after* the router, but Tokyo's *before*?** This isn't an inconsistency — it's two valid, deliberately different answers to "where is the asset I most need to protect?" In New York, the protected resource is *the path to the internet* for general-purpose users — the router's normal LAN-forwarding job doesn't need firewall inspection to happen locally. In Tokyo, the protected resource is *the servers themselves* — pushing the firewall directly against the switch means literally nothing reaches the server segment without first passing through security policy, even hypothetically malicious traffic that somehow originated from a compromised device sitting on the WAN side of TOKYO-R2.
- **Why a `/30` for every transit link instead of reusing the `/24`s?** A `/30` gives exactly 2 usable addresses — precisely enough for a point-to-point link and not one address more. Using a `/24` here would "work" but wastes 252 addresses per link and, more importantly, signals to anyone reading the addressing table that this network segment might have more than 2 devices on it, when it structurally never will. Efficient subnetting is also directly tested on the CCNA exam.
- **Why PAT (dynamic NAT to one interface IP) instead of a 1:1 static NAT pool for each branch?** PAT is what virtually every small/mid-size branch network actually uses for general outbound traffic, because it doesn't consume a public IP per internal host — you only need one public IP per branch. Static NAT is reserved for the one case where the *outside* world needs to reliably reach a specific *inside* resource (SRV1's web service in Step 8.2 Step 6) — which is exactly why this lab uses PAT for general traffic but static NAT for that one exception.
- **Why an ASA instead of just extending the IOS router with an ACL?** An IOS ACL can filter traffic, but the ASA additionally provides stateful inspection (tracking connection state so return traffic is automatically permitted without a matching inbound rule), a dedicated security-level model, and dedicated NAT/PAT handling in one integrated policy engine — the standard reason a dedicated firewall appliance exists separately from a router in real enterprise design, even though a router *can* technically do basic packet filtering.

---

## 14. Real-World Parallel

**You'd see this when...**

- ...a startup with a single New York office signs its first big manufacturing client in Asia and opens a small Tokyo office — this is almost exactly how the network would be built in the first 6 months, before the company can justify a full SD-WAN or MPLS rollout.
- ...an auditor or new hire asks "why don't both offices have the same firewall placement?" and you need to explain that consistency-for-its-own-sake isn't a security goal — protecting the actual asset at each site is.
- ...you're troubleshooting "the internet is down" tickets from users, and the actual root cause is a missing NAT rule or a forgotten `no shutdown` — the two most common real-world causes of "everything is configured but nothing works," mirrored directly in this lab's Common Mistakes section.
- ...a penetration tester (playing the role the Attacker laptop plays here) reports back that they could reach one specific web service and nothing else — that's a *successful* test of a correctly scoped ACL, not a finding to panic about.
- ...you inherit a network with static routes still in place at 5+ sites and have to decide whether it's time to migrate to OSPF — a decision directly informed by the "why static routes" reasoning in the Design Analysis section above.

---

## 15. Stretch Goal

Once the base lab works end-to-end, try one or more of the following without referring back to the steps above:

1. **Add a third branch (London)** with its own LAN, router, and firewall, connected to ISP-RTR, using a firewall placement *different* from both New York and Tokyo's (e.g., router and firewall in parallel with separate policies for two VLANs). Justify your placement choice in a paragraph, the way Section 13 does for NY/Tokyo.
2. **Restrict the attacker further:** configure TOKYO-FW2's ACL so SRV1's web service is only reachable from ISP-RTR's subnet (203.0.113.0/30), not from the Attacker's subnet — simulating "only our ISP's monitoring system can reach this, no one else on the internet."
3. **Break NAT on purpose, then fix it using only `show` commands** (no peeking at your own running-config) — remove the `nat (inside,outside) dynamic interface` line on NY-FW1, confirm connectivity breaks exactly as the Troubleshooting Guide predicts, then restore it. This builds the diagnostic muscle memory that matters far more than memorizing the fix.
4. **Convert ISP-RTR's static route to Tokyo into a default route redistribution problem:** what would happen if ISP-RTR only had a default route pointing at NY-FW1 instead of the specific route to Tokyo's transit network? Predict the failure, then test it.

---

## 16. Self-Assessment

Before moving to Day 02, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, why NY-FW1 sits after NY-R1 but TOKYO-FW2 sits before TOKYO-R2?
- [ ] Can you write the 4 commands needed to bring up an IOS interface with an IP address, from `configure terminal`, without looking?
- [ ] Can you explain the difference between `enable password` and `enable secret`, and state which one you should always use?
- [ ] Can you explain why `password` alone on a VTY line isn't enough, and what else is required?
- [ ] Can you draw the ASA security-level model (100/0, which direction is allowed by default) from memory?
- [ ] Given a fresh topology diagram with IPs unlabeled, could you design and write out an addressing plan like Section 4 yourself, choosing appropriate subnet sizes?
- [ ] Can you name, without looking at Section 11, at least 4 of the 8 common mistakes?
- [ ] Could you explain this entire lab's design, in business terms (Section 2), to a non-technical manager in under 2 minutes?

If you answered "no" to more than two of these, re-do the lab from scratch (not by copy-pasting commands) before moving on — the goal of Day 01 isn't a working topology, it's the ability to build one.

---

## 17. Key Concepts Demonstrated

- **Router functions** — path determination and inter-network forwarding, shown differently at NY-R1 (LAN-facing) vs. TOKYO-R2 (WAN-facing)
- **Switch functions** — MAC-address-based local forwarding within each branch's single VLAN
- **Firewall placement and defense in depth** — perimeter (New York) vs. resource-adjacent (Tokyo) security models
- **NAT/PAT** — translating private RFC 1918 space to routable addresses at the network edge
- **Stateful default-deny** — ASA security levels enforce inside→outside allowed, outside→inside denied unless explicitly permitted
- **Static routing** — building end-to-end reachability without a dynamic routing protocol
- **Access control lists** — permitting one specific inbound service (SRV1 web) while denying everything else

---

## 18. What I Learned

Working through the two branches side by side made the practical difference between firewall placements much clearer than reading about it. In New York, the router still gets to make forwarding decisions on internal traffic before the firewall ever inspects it — meaning a compromised or misconfigured router upstream of the firewall has more room to cause damage internally. In Tokyo, the firewall inspects everything the moment it leaves the switch, which is a tighter model for protecting sensitive server resources, at the cost of the firewall also having to handle basic routing decisions that would otherwise belong to a router.

The NAT/PAT and ACL configuration on the ASA also reinforced *why* the attacker laptop matters as a topology element — it's not just decoration, it's the test case that proves the security design actually works: everything is denied by default, and the one thing that should be reachable (the web server) is reachable only because of an explicit, narrow rule.

This lab is the foundation for what comes next:

- VLANs and trunking
- Dynamic routing (OSPF)
- Extended ACL policy design
- Site-to-site VPNs between the branches
- Formal network security auditing

---

## 19. Skills Practiced

- Network device identification and role analysis
- Enterprise topology design and IP addressing planning
- Cisco IOS router and switch configuration
- Cisco ASA 5505 firewall configuration (interfaces, NAT, ACLs, routing)
- End-to-end connectivity verification and structured troubleshooting
- Security architecture reasoning (defense in depth, perimeter vs. internal controls)

---

## 20. GNS3 Lab

This lab has a companion GNS3 topology that mirrors the design above using free, open-source images, built automatically by [`GNS3/Day-01/build_lab.py`](../GNS3/Day-01/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (NY-R1, TOKYO-R2, ISP-RTR) | Cisco 2911 | VyOS |
| Switches (NY-SW1, TOKYO-SW2) | Cisco 2960 | Open vSwitch |
| Firewalls (NY-FW1, TOKYO-FW2) | Cisco ASA 5505 | pfSense CE |
| PCs, Servers, Attacker | Generic PC/Server/Laptop | Linux (Alpine) |

See [`GNS3/Day-01/README.md`](../GNS3/Day-01/README.md) for how to run the build script. Note that ASA-specific syntax (`nameif`, `security-level`, `object network`) does not carry over 1:1 to pfSense — pfSense uses a web GUI and different NAT/firewall-rule concepts. A pfSense-equivalent configuration guide is included in the GNS3 README so the *concepts* (security zones, default-deny, NAT/PAT) transfer even though the exact commands don't.
