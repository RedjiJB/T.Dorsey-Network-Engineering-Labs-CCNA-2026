# Day 31 Lab Manual — IPv6 Dual-Stack Configuration on a Multi-LAN Router

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Convert a single-router, three-LAN IPv4 topology into a dual-stack IPv4/IPv6 network — enable IPv6 routing, assign global IPv6 addresses on every LAN interface, configure dual-stack PCs, and verify inter-LAN reachability over both protocols. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): IPv6 addressing, address types (unicast/link-local/multicast). This lab is a direct hit on the "IPv6 addressing and prefix" and "verify IP parameters" exam topics. |
| **Prerequisites** | Day 08 (IPv4 Addressing), Day 15 (VLSM), Day 09 (Interface Configuration) — you should already be fluent in IPv4 subnetting and comfortable navigating IOS configuration modes before starting this lab. |
| **Time Estimate** | 1.5 – 2.5 hours (first attempt); 30–40 minutes on repeat/review. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the CLI itself is short, but the addressing concepts (EUI-64, link-local, hex subnetting) are genuinely new material, not just IPv4 muscle memory applied to bigger numbers. |

---

## 1. Lab Overview

Today's build takes an already-working IPv4 network — one router (R1) serving three separate LANs, each behind its own access switch — and layers **IPv6 on top without touching the IPv4 configuration**. This is called **dual-stack**: the same physical interface, the same cable, the same switch port, simultaneously running two completely independent Layer 3 protocols side by side. No tunneling. No translation. No NAT64. Just two address families coexisting.

By the end of the lab, every device in the topology — R1's three LAN interfaces and the three PCs behind them — will have both an IPv4 address and a global IPv6 address, and you'll prove that both protocols route correctly between all three LANs.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain what dual-stack means and why enterprises run it instead of migrating outright to IPv6
- Enable IPv6 unicast routing globally on a Cisco IOS router
- Manually derive an EUI-64 interface identifier from a MAC address, bit by bit
- Explain link-local address structure and why every IPv6-enabled interface has one automatically
- Assign global IPv6 addresses to router interfaces, both manually and via EUI-64
- Configure dual-stack PCs with both an IPv4 and an IPv6 address/gateway
- Verify IPv6 connectivity using `show ipv6 interface brief`, `show ipv6 route`, and `ping`
- Explain how IPv6 subnetting math differs from IPv4 (hex nibble boundaries vs. decimal octets)
- Troubleshoot the most common dual-stack misconfigurations

---

## 2. Business Context

**Why would a real company do this?**

IPv6 isn't a future project — it's a present-day operational requirement, and the business drivers behind it show up constantly in real network engineering work:

- **"Our ISP just told us they're moving to CGNAT and our remote-access VPN keeps breaking"** → carrier-grade NAT (CGNAT) is what ISPs do when they run out of public IPv4 addresses to hand out — multiple customers share one public IP, which breaks protocols that expect a stable, unique public address. Native IPv6 sidesteps the problem entirely because IPv6's address space is enormous enough that every device gets a real, globally routable address again.
- **"We just acquired a company that's already IPv6-only in parts of their infrastructure"** → mergers and acquisitions are one of the most common real-world triggers for a dual-stack rollout. You can't force the acquired company to renumber everything on day one, so both networks run dual-stack during the transition period — sometimes for years.
- **"Compliance/government contracts require IPv6 support"** → the U.S. federal government (via OMB mandates) and many international regulators require IPv6 capability for networks touching government systems. If your company sells to government clients, "do we support IPv6" is a real RFP checkbox, not an academic exercise.
- **"Our mobile app users are increasingly on IPv6-only cellular networks"** → most major mobile carriers assign IPv6 addresses by default and translate to IPv4 only when necessary (464XLAT, NAT64). A company that only reaches customers over IPv4 is already depending on translation layers it doesn't control.
- **"We can't just flip a switch and turn off IPv4"** → this is the core reason dual-stack, not a hard cutover, is the dominant migration strategy. Legacy applications, older equipment, and third-party integrations may not support IPv6 for years. Dual-stack lets a network run both indefinitely, migrating workload by workload instead of all at once.

This lab's topology — one router, three LANs, dual-stack everywhere — is deliberately the smallest possible version of what a company actually does: add IPv6 as a second protocol stack on top of infrastructure that already works, rather than ripping out and replacing anything.

---

## 3. Topology Reference

<p align="center">
  <a href="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201).png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201).png" alt="Day 31 IPv6 Dual-Stack Lab Topology" width="900">
  </a>
</p>

### 3.1 Traffic Flow Summary

```text
LAN-1: PC1 -- SW1 -- R1 Gi0/0
LAN-2: PC2 -- SW2 -- R1 Gi0/1
LAN-3: PC3 -- SW3 -- R1 Gi0/2
```

R1 is the single Layer 3 boundary in this topology — every inter-LAN packet, whether IPv4 or IPv6, is routed through R1. There is no dynamic routing protocol; all three LANs are directly connected subnets on R1, so no static routes are even needed — the connected routes alone are sufficient for full inter-LAN reachability, exactly as `show ipv6 route` will confirm later.

### 3.2 Equipment List

| Device | Role | Hostname Used Below |
|---|---|---|
| Router | Single L3 gateway for all 3 LANs | `R1` |
| Switch x3 | L2 access switch, one per LAN | `SW1`, `SW2`, `SW3` |
| PC x3 | End host, one per LAN | `PC1`, `PC2`, `PC3` |

> **Note on realism:** IPv4 addressing is treated as pre-existing and unchanged — this lab is entirely additive. If you're building this from scratch rather than continuing from an earlier IPv4-only lab, configure IPv4 first exactly as shown in Section 4, then layer IPv6 on top in Section 6.

---

## 4. IP Addressing Plan

This lab lives or dies on understanding IPv6 addressing, so this section goes deep. If you already have a rock-solid IPv4 addressing plan from earlier labs, the IPv4 side below is just a recap — the IPv6 derivation is the new material.

### 4.1 Dual-Stack Addressing Table

| Device | Interface | IPv4 | IPv6 (global) | Connects To |
|---|---|---|---|---|
| R1 | Gi0/0 | 192.168.1.1/24 | 2001:DB8:0:1::1/64 | SW1 |
| R1 | Gi0/1 | 192.168.2.1/24 | 2001:DB8:0:2::1/64 | SW2 |
| R1 | Gi0/2 | 192.168.3.1/24 | 2001:DB8:0:3::1/64 | SW3 |
| PC1 | NIC | 192.168.1.2/24 | 2001:DB8:0:1::2/64 | SW1 |
| PC2 | NIC | 192.168.2.2/24 | 2001:DB8:0:2::2/64 | SW2 |
| PC3 | NIC | 192.168.3.2/24 | 2001:DB8:0:3::2/64 | SW3 |

**Default gateways:** PC1 → `192.168.1.1` / `2001:DB8:0:1::1`; PC2 → `192.168.2.1` / `2001:DB8:0:2::1`; PC3 → `192.168.3.1` / `2001:DB8:0:3::1`.

**`2001:DB8::/32`** is the IANA-reserved documentation prefix, carved out specifically so training material, RFCs, and lab exercises never accidentally collide with a real, routable network. You will see it in essentially every IPv6 example you ever read, including on the exam. Never use it in production — it is explicitly non-routable on the real internet.

### 4.2 IPv6 Address Structure — the Basics

An IPv6 address is **128 bits**, written as **eight groups of four hex digits**, separated by colons:

```text
2001:0DB8:0000:0001:0000:0000:0000:0002
```

Two shorthand rules make this readable:

1. **Leading zeros in each group may be omitted.** `0DB8` → `DB8`. `0001` → `1`.
2. **Exactly one run of consecutive all-zero groups may be collapsed to `::`.** You cannot use `::` twice in the same address — if you did, there'd be no way to tell how many zero groups each `::` represents.

Applying both rules:

```text
2001:0DB8:0000:0001:0000:0000:0000:0002
→ 2001:DB8:0:1:0:0:0:2          (leading zeros trimmed)
→ 2001:DB8:0:1::2               (one run of consecutive zero groups collapsed)
```

That's exactly the PC1 address from the table above. Every `2001:DB8:0:N::M` address in this lab is shorthand for a full 32-hex-digit address — get comfortable expanding and collapsing both directions, because the exam tests this directly.

### 4.3 IPv6 Prefix Notation and the /64 Convention

Where IPv4 uses a dotted-decimal subnet mask (`255.255.255.0`), IPv6 uses **prefix length notation exclusively** — you will essentially never see an IPv6 equivalent of `255.255.255.0` written out in modern practice. `2001:DB8:0:1::1/64` means: the first 64 bits (`2001:0DB8:0000:0001`) are the **network prefix**, and the remaining 64 bits are the **interface identifier** (host portion).

**Why /64 almost always?** IPv6 was designed around a hard architectural convention: **every LAN segment gets a /64**, full stop. This isn't a "good practice" the way right-sizing IPv4 subnets is — it's baked into how key IPv6 features work:

- **SLAAC (Stateless Address Autoconfiguration)** and **EUI-64** interface IDs both assume exactly 64 bits of host space to build an interface identifier from a 48-bit MAC address (see 4.4 below). Shrinking below /64 breaks both mechanisms.
- A /64 provides 2^64 addresses — roughly 18 quintillion — per subnet. IPv6's designers deliberately chose to be "wasteful" here because the entire address space (2^128) is so large that address conservation, the entire reason IPv4 subnetting got complicated, is simply not a design constraint anymore.

You will see /126, /127, and /128 used for router-to-router point-to-point links and loopbacks in more advanced labs, but **for any segment with actual end hosts, /64 is the answer** — don't subnet an IPv6 LAN down further just because you're used to right-sizing IPv4.

### 4.4 EUI-64 — Deriving an Interface ID from a MAC Address, by Hand

This is the single most important new mechanic in this lab. EUI-64 (Extended Unique Identifier, 64-bit) is the algorithm IOS (and SLAAC-capable hosts) use to automatically generate the 64-bit host portion of an IPv6 address directly from a 48-bit interface MAC address — no DHCP, no manual host-bit assignment required.

**Worked example.** Say R1's Gi0/0 has the MAC address:

```text
00:1A:2B:3C:4D:5E
```

**Step 1 — Split the MAC into two 24-bit halves.**

```text
OUI (first 24 bits):     00-1A-2B
Device ID (last 24 bits): 3C-4D-5E
```

**Step 2 — Insert `FFFE` in the middle**, expanding 48 bits to 64 bits:

```text
00-1A-2B-FF-FE-3C-4D-5E
```

This is the part most students find odd, so here's why: EUI-64 is actually an IEEE standard for extending a 48-bit MAC (EUI-48) into a 64-bit identifier. `FFFE` is a reserved value chosen specifically because it never appears in a real burned-in MAC's middle bytes, so inserting it is unambiguous and reversible.

**Step 3 — Flip the 7th bit of the first byte (the "Universal/Local" or U/L bit).**

This is the step that trips people up, so slow down and do it in binary. The first byte is `00`. Written out as 8 bits:

```text
00000000
```

Bit numbering here counts from the **left**, starting at bit 1 (the most significant bit). The 7th bit is the **second-to-last** bit in the byte:

```text
Bit:     1 2 3 4 5 6 7 8
Value:   0 0 0 0 0 0 0 0
                    ^
                    7th bit — flip this one
```

Flipping bit 7 from `0` to `1`:

```text
00000000 → 00000010
```

`00000010` in hex is `02`. So the first byte `00` becomes `02`.

**Why flip this specific bit?** The 7th bit (in IEEE terms, the "U/L bit," bit position 1 counting from the *right* within that byte, which is the same bit — terminology varies but the bit itself doesn't) indicates whether a MAC address is **U**niversally administered (burned into hardware by the manufacturer, bit = 0) or **L**ocally administered (assigned by software, bit = 1). EUI-64 flips this bit as a convention so that an address derived from a real hardware MAC is flagged as "locally significant" within the resulting IPv6 interface ID — it's a bookkeeping signal, not a security feature, but it's precisely why the math isn't just "insert FFFE and done."

**Step 4 — Assemble the final interface ID.**

```text
Original MAC:        00:1A:2B:3C:4D:5E
After FFFE insert:    00-1A-2B-FF-FE-3C-4D-5E
After bit-7 flip:     02-1A-2B-FF-FE-3C-4D-5E
```

Written in IPv6 hextet form (4 hex digits per group, colon-separated):

```text
021A:2BFF:FE3C:4D5E
```

**Step 5 — Combine with the /64 network prefix.**

If this MAC belongs to an interface on the `2001:DB8:0:1::/64` LAN, the full EUI-64-derived address is:

```text
2001:DB8:0:1:021A:2BFF:FE3C:4D5E
```

Note this is a *different* address than the manually-assigned `2001:DB8:0:1::1` used elsewhere in this lab's addressing table — EUI-64 and manual assignment are two different ways to fill the same 64 host bits, and Section 6.4 and Section 10 both address when you'd choose one over the other.

**Quick-reference summary of the whole algorithm:**

```text
1. Split MAC into two 24-bit halves: OUI | Device-ID
2. Insert FFFE between them: OUI-FF-FE-Device-ID  (48 bits → 64 bits)
3. Flip the 7th bit (U/L bit) of the first byte
4. Result is the 64-bit interface identifier
5. Prepend the 64-bit network prefix to get the full address
```

### 4.5 Link-Local Addresses (FE80::/10)

Every IPv6-enabled interface — whether or not it has a global address configured — automatically generates and holds a **link-local address** the moment IPv6 is enabled on it. This isn't optional and isn't something you disable in normal operation.

**Structure:** Link-local addresses always fall in the `FE80::/10` range. In practice, IOS always uses exactly `FE80::/64` as the prefix (the /10 is the full reserved block; /64 is what's actually used per-interface), followed by an interface identifier — typically EUI-64-derived from the interface's MAC, the same algorithm from Section 4.4, unless manually overridden.

```text
FE80::021A:2BFF:FE3C:4D5E
```

**Why they matter:**

- Link-local addresses are used for **on-segment-only** communication — routing protocol adjacencies (OSPFv3 neighbors, for example), Neighbor Discovery Protocol (NDP, IPv6's replacement for ARP), and the default-gateway-facing side of many host-to-router interactions all use link-local addresses under the hood, even when a global address is also present.
- They are **never routed** beyond the local segment — a router will not forward a packet sourced from or destined to an FE80::/10 address off the interface it arrived on.
- This is IPv6's structural equivalent of IPv4's APIPA range (`169.254.0.0/16`), except link-local is a *permanent, always-present, intentional* part of every interface's configuration — not a fallback that only appears when DHCP fails.

You'll see the link-local address appear automatically in `show ipv6 interface brief` output the moment `ipv6 enable` or any `ipv6 address` command is applied to an interface — you never type it directly on a router interface.

### 4.6 How IPv6 Subnetting Math Differs from IPv4

This is worth stating explicitly because the instinct from IPv4 subnetting (Day 15's VLSM work) will actively mislead you here if you don't recalibrate.

| Concept | IPv4 | IPv6 |
|---|---|---|
| Boundary unit | Octet (8 bits, base-10 friendly) | **Nibble** (4 bits, one hex digit) |
| Typical subnet math | Borrow bits *within* an octet (`/25`, `/27`, `/29`...) | Borrow bits at **nibble (hex digit) boundaries** in practice (`/48`, `/52`, `/56`, `/60`, `/64`) |
| "Interesting" boundary values | Any bit position, tracked with the `256 − 2^h` shortcut | Each hex digit represents exactly 4 bits — subnetting one hex digit deeper always multiplies available subnets by 16, not 2 |
| Host portion sizing | Carefully rationed (RFC 1918 exhaustion pressure) | Essentially never rationed — /64 is standard for any LAN regardless of host count |
| Practical takeaway for this lab | N/A (out of scope here) | You will not need to subnet *within* a /64 in this lab — R1's three LANs are three separate, already-allocated /64s (`...0:1::/64`, `...0:2::/64`, `...0:3::/64`), not one /64 split three ways |

The key mental shift: in IPv4, "how many hosts do I need" drives subnet size, because address space is scarce. In IPv6, "how many *subnets* do I need to hand out to sites/departments/VLANs" drives subnet size, because a single /64 already has more host addresses than any LAN will ever need — the scarcity math moved up a level, from hosts-per-subnet to subnets-per-allocation. A full treatment of hierarchical IPv6 subnet planning (a site getting a /48, splitting it into /56s per building, then /64s per VLAN) is out of scope for this single-router lab, but recognizing *why* the boundary math changed from octets to nibbles is squarely in scope.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Confirm IPv4 is already working end-to-end across all three LANs (ping PC-to-PC across subnets over IPv4) — if IPv4 doesn't route correctly yet, fix that first; this lab assumes it as a working baseline.
2. Have the dual-stack addressing table (Section 4.1) open in a second window.
3. Confirm which IOS image your R1 platform is running supports `ipv6 unicast-routing` — virtually all modern IOS/IOS-XE images do, but very old images or certain feature-set-limited images may not.
4. If using Packet Tracer, confirm each PC's Desktop → IP Configuration panel has separate IPv4 and IPv6 tabs/fields available — some very old Packet Tracer PC models don't expose IPv6 configuration.

---

## 6. Configuration Tasks

### 6.1 Enable IPv6 Unicast Routing on R1

```text
R1>enable
R1#configure terminal
R1(config)#ipv6 unicast-routing
```

- **Mode:** Privileged EXEC → Global Config.
- **What it does:** Turns on IPv6 packet forwarding *between* interfaces, globally, for the entire router.
- **Why it matters:** This is the single most commonly forgotten command in dual-stack labs, and it fails silently in a specific, confusing way — every interface can have a perfectly correct global IPv6 address, `show ipv6 interface brief` looks completely fine, and PCs on the *same* LAN can even ping their own gateway... but cross-LAN IPv6 pings will simply fail, with no error message pointing at the actual cause. IOS enables IPv6 addressing and link-local generation per-interface independently of whether the router is actually willing to route between interfaces — those are two separate switches, and this command is the second one.
- **Memory aid:** Compare directly to IPv4's `ip routing`, which is enabled by default on every Cisco router — `ipv6 unicast-routing` is the IPv6 equivalent, except IPv6 routing is **disabled by default** and IPv4 routing is **enabled by default**. That asymmetry is exactly why this step exists as an explicit, easy-to-forget command instead of being automatic.

### 6.2 Assign Global IPv6 Addresses to R1's LAN Interfaces (Manual Method)

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description LAN-1
R1(config-if)#ipv6 address 2001:DB8:0:1::1/64
R1(config-if)#ipv6 enable
R1(config-if)#no shutdown
R1(config-if)#exit

R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description LAN-2
R1(config-if)#ipv6 address 2001:DB8:0:2::1/64
R1(config-if)#ipv6 enable
R1(config-if)#no shutdown
R1(config-if)#exit

R1(config)#interface gigabitEthernet 0/2
R1(config-if)#description LAN-3
R1(config-if)#ipv6 address 2001:DB8:0:3::1/64
R1(config-if)#ipv6 enable
R1(config-if)#no shutdown
R1(config-if)#exit
```

- **Mode:** Global Config → Interface Config.
- **`ipv6 address 2001:DB8:0:1::1/64`** — assigns a specific, fully manual global unicast address to the interface. You are typing every one of the 128 bits yourself (via the shorthand notation) rather than letting the router derive the host portion.
- **`ipv6 enable`** — explicitly turns on IPv6 processing on the interface and forces generation of the link-local address, *even if* you hadn't also configured a global address. Technically, configuring a global address with `ipv6 address` implicitly enables IPv6 on the interface too — but including `ipv6 enable` explicitly is good practice and required if you ever configure an interface with *only* a link-local presence and no global address (uncommon, but happens on WAN transit links).
- **Why `::1` for the gateway?** Same convention as IPv4's `.1` — by community convention (not a protocol requirement), the router/gateway takes the first host address in the subnet. Hosts get `::2`, `::3`, and so on. This is purely a human-readability convention; IPv6 doesn't reserve `::1` the way IPv4 reserves the network and broadcast addresses.
- **Why not EUI-64 here?** This lab shows both methods so you can compare them directly — see 6.4 below for the EUI-64 equivalent of this exact configuration, and Section 10 for the design trade-off between the two.

### 6.3 Verify Interface-Level IPv6 State

```text
R1#show ipv6 interface brief
```

```text
GigabitEthernet0/0    [up/up]
    FE80::21A:2BFF:FE3C:4D5E
    2001:DB8:0:1::1
GigabitEthernet0/1    [up/up]
    FE80::21B:2CFF:FE3D:4E5F
    2001:DB8:0:2::1
GigabitEthernet0/2    [up/up]
    FE80::21C:2DFF:FE3E:4F60
    2001:DB8:0:3::1
```

Every interface shows **two** addresses: the auto-generated link-local (top line, `FE80::...`) and the manually configured global address (bottom line). This confirms Section 4.5's claim directly — the link-local address exists automatically and independently of the global address you typed.

### 6.4 Alternative: Assign a Global Address via EUI-64

Instead of typing the full 128-bit address, you can hand the router only the /64 network prefix and let it derive the interface ID from the interface's own MAC address using the exact algorithm you worked through by hand in Section 4.4:

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ipv6 address 2001:DB8:0:1::/64 eui-64
```

- **What it does:** IOS reads the interface's burned-in MAC address, runs the EUI-64 algorithm (insert `FFFE`, flip the U/L bit), and appends the result to the `2001:DB8:0:1::` /64 prefix you supplied.
- **Why it matters:** This is the same mechanism SLAAC-capable hosts use to self-assign an address from a router advertisement — understanding it manually (Section 4.4) is what lets you predict, read, and troubleshoot addresses you never typed yourself.
- This lab's addressing table (Section 4.1) uses the manual `::1`/`::2` method throughout for readability and predictability — Section 10 discusses when EUI-64 is preferable in real deployments instead.

### 6.5 Configure Dual-Stack PCs

**Packet Tracer Desktop → IP Configuration tab, entering both address families:**

**PC1:**
```text
IPv4 Address:    192.168.1.2
IPv4 Subnet Mask: 255.255.255.0
IPv4 Gateway:    192.168.1.1

IPv6 Address:    2001:DB8:0:1::2
IPv6 Prefix Length: 64
IPv6 Gateway:    2001:DB8:0:1::1
```

**PC2:**
```text
IPv4 Address:    192.168.2.2
IPv4 Subnet Mask: 255.255.255.0
IPv4 Gateway:    192.168.2.1

IPv6 Address:    2001:DB8:0:2::2
IPv6 Prefix Length: 64
IPv6 Gateway:    2001:DB8:0:2::1
```

**PC3:**
```text
IPv4 Address:    192.168.3.2
IPv4 Subnet Mask: 255.255.255.0
IPv4 Gateway:    192.168.3.1

IPv6 Address:    2001:DB8:0:3::2
IPv6 Prefix Length: 64
IPv6 Gateway:    2001:DB8:0:3::1
```

> Note that IPv6 uses a **prefix length field** (`64`), not a dotted-decimal mask field — this is consistent with Section 4.3: IPv6 configuration interfaces (both CLI and GUI) never ask for an equivalent of `255.255.255.0`.

---

## 7. Verification Steps

### 7.1 Verification Command Table

| Device | Command | What to check |
|---|---|---|
| R1 | `show ipv6 interface brief` | All 3 interfaces `up/up`, correct global + link-local addresses |
| R1 | `show ipv6 route` | Connected (`C`) and local (`L`) routes for all 3 `/64`s |
| R1 | `show ipv6 protocols` | `"connected"` and `"static"` listed — confirms IPv6 routing is active |
| R1 | `show ip interface brief` | Confirms IPv4 side is untouched and still `up/up` |
| PC1/PC2/PC3 | `ipconfig` | Both IPv4 and IPv6 addresses/gateways present |

### 7.2 Expected Output Gallery

**`R1# show ipv6 protocols`**

```text
IPv6 Routing Protocol is "connected"
IPv6 Routing Protocol is "static"
```

There is no explicit "IPv6 routing: enabled" banner anywhere in IOS output — this is the confirmation. If `ipv6 unicast-routing` were missing, interfaces would still show global addresses in `show ipv6 interface brief`, but `show ipv6 route` would come back essentially empty.

**`R1# show ipv6 route`**

```text
IPv6 Routing Table - default - 7 entries
Codes: C - Connected, L - Local, S - Static, U - Per-user Static route
       B - BGP, R - RIP, D - EIGRP, EX - EIGRP external
       O - OSPF Intra, OI - OSPF Inter, OE1 - OSPF ext 1, OE2 - OSPF ext 2

C   2001:DB8:0:1::/64 [0/0]
     via GigabitEthernet0/0, directly connected
L   2001:DB8:0:1::1/128 [0/0]
     via GigabitEthernet0/0, receive
C   2001:DB8:0:2::/64 [0/0]
     via GigabitEthernet0/1, directly connected
L   2001:DB8:0:2::1/128 [0/0]
     via GigabitEthernet0/1, receive
C   2001:DB8:0:3::/64 [0/0]
     via GigabitEthernet0/2, directly connected
L   2001:DB8:0:3::1/128 [0/0]
     via GigabitEthernet0/2, receive
L   FF00::/8 [0/0]
     via Null0, receive
```

Every `/64` you configured shows as `C` (connected), and every interface's own address shows as `L` (local, /128 — a route to exactly one address: itself). The `FF00::/8` entry is the multicast route, always present once IPv6 is enabled, and isn't something you configured.

**`R1# show ip interface brief`** (confirms IPv4 is untouched)

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         192.168.1.1     YES manual up                    up
GigabitEthernet0/1         192.168.2.1     YES manual up                    up
GigabitEthernet0/2         192.168.3.1     YES manual up                    up
```

**`PC2> ipconfig`**

```text
FastEthernet0 Connection:

Connection-specific DNS Suffix..:
Link-local IPv6 Address.........: FE80::2D0:97FF:FE12:77E2
IPv6 Address.....................: 2001:DB8:0:2::2
IPv6 Gateway.....................: 2001:DB8:0:2::1
IPv4 Address.....................: 192.168.2.2
Subnet Mask......................: 255.255.255.0
Default Gateway..................: 192.168.2.1
```

Both protocol stacks show fully populated addressing — this is dual-stack working correctly on the host side.

**`PC1> ping 2001:DB8:0:2::2`** (inter-LAN IPv6 ping, PC1 → PC2, routed through R1)

```text
Pinging 2001:DB8:0:2::2 with 32 bytes of data:

Reply from 2001:DB8:0:2::2: bytes=32 time=2ms
Reply from 2001:DB8:0:2::2: bytes=32 time=1ms
Reply from 2001:DB8:0:2::2: bytes=32 time=1ms
Reply from 2001:DB8:0:2::2: bytes=32 time=2ms

Ping statistics for 2001:DB8:0:2::2:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

**`PC1> ping 192.168.2.2`** (same pair, IPv4 — should also succeed, unchanged from before this lab)

```text
Pinging 192.168.2.2 with 32 bytes of data:

Reply from 192.168.2.2: bytes=32 time=1ms
Reply from 192.168.2.2: bytes=32 time=1ms
Reply from 192.168.2.2: bytes=32 time=1ms
Reply from 192.168.2.2: bytes=32 time=1ms

Ping statistics for 192.168.2.2:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Both succeed, independently, over the same physical path — this pair of results is the single clearest proof that dual-stack is working end to end.

### 7.3 Reachability Matrix

| From | To | Protocol | Expected Result | Why |
|---|---|---|---|---|
| PC1 | R1 Gi0/0 (2001:DB8:0:1::1) | IPv6 | Success | Directly connected gateway |
| PC1 | PC2 (2001:DB8:0:2::2) | IPv6 | Success | Routed via R1, both connected /64s |
| PC1 | PC3 (2001:DB8:0:3::2) | IPv6 | Success | Routed via R1 |
| PC1 | PC2 (192.168.2.2) | IPv4 | Success | Pre-existing IPv4 routing, unaffected by IPv6 config |
| PC2 | PC3 | Both | Success | Symmetric to PC1's results |

---

## 8. Common Mistakes (the 80/20)

1. **Forgetting `ipv6 unicast-routing`.** By far the most common error, and the most confusing to diagnose, because interfaces still show correct addresses — only cross-LAN routing silently fails. If `show ipv6 route` looks nearly empty despite every interface having a global address, this is almost always why.
2. **Typing the prefix length wrong or omitting it** (`ipv6 address 2001:DB8:0:1::1` with no `/64`). IOS will reject this — unlike some IPv4 shortcuts, IPv6 addresses always require an explicit prefix length in this command.
3. **Confusing link-local and global addresses when troubleshooting.** A ping sourced from or destined to an `FE80::...` address across LANs will always fail — that's correct behavior, not a bug (Section 4.5). Make sure you're testing with global addresses for inter-LAN reachability checks.
4. **Forgetting `no shutdown`** — identical failure mode to every other IOS lab; IPv6 doesn't change this. `show ipv6 interface brief` will show `[administratively down/down]`.
5. **Flipping the wrong bit during manual EUI-64 derivation.** Bit-7-from-the-left of the *first byte only* — a very specific, very easy to mis-locate single bit. If your hand-derived EUI-64 address doesn't match what `show ipv6 interface brief` produces after using the `eui-64` keyword, re-check this step first.
6. **Configuring only an IPv4 gateway on the PC and forgetting the IPv6 gateway field, or vice versa.** Dual-stack means two independent gateway configurations on the host, not one shared setting — Packet Tracer's IP Configuration panel has genuinely separate fields for each protocol, and it's easy to fill in only one.
7. **Using a prefix length other than /64 on a LAN interface "to save space,"** carrying IPv4 subnet-conservation habits into IPv6 where they don't apply (Section 4.6). This breaks EUI-64/SLAAC assumptions and isn't necessary — IPv6 address space isn't scarce.
8. **Assuming `2001:DB8::/32` will route on the real internet.** It's a documentation-only prefix (Section 4.1) — fine in a lab, permanently unusable in production.

---

## 9. Troubleshooting Guide

Work through these **in order** — each step assumes the previous one passed.

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Interface shows `[administratively down/down]` in `show ipv6 interface brief` | Forgot `no shutdown` | `show ipv6 interface brief` | Enter the interface, run `no shutdown` |
| 2 | Interface has a link-local address but no global address listed | `ipv6 address` never configured, or typo'd without a prefix length | `show ipv6 interface` (detailed) | Re-apply `ipv6 address <prefix>/64` correctly |
| 3 | PC can't ping its own gateway over IPv6 | Wrong IPv6 address/prefix on PC, or PC's IPv6 stack disabled | `ipconfig` on PC | Correct the PC's IPv6 address/prefix/gateway fields |
| 4 | PC pings its own gateway fine, but not a PC on another LAN | `ipv6 unicast-routing` missing on R1 | `show ipv6 protocols` (look for `"connected"`) / `show ipv6 route` | Add `ipv6 unicast-routing` in global config |
| 5 | `show ipv6 route` shows fewer than 3 `C` entries | One interface's `ipv6 address` command wasn't applied, or that interface is down | `show ipv6 interface brief` | Re-check and re-apply that interface's IPv6 address and `no shutdown` |
| 6 | IPv6 ping fails but IPv4 ping between the same two PCs succeeds | Confirms the physical path, switching, and IPv4 routing are all fine — problem is IPv6-specific | Re-run steps 1–5 focused only on IPv6 | Isolate to the IPv6-specific step above; don't re-troubleshoot IPv4 |
| 7 | Manually-derived EUI-64 address doesn't match router output | Bit-7 flip done on the wrong bit, or `FFFE` inserted in the wrong position | Compare your Section 4.4 math against `show ipv6 interface brief` output after applying `eui-64` | Redo the derivation slowly, bit by bit, using Section 4.4 as the template |
| 8 | Config disappears after a reload | Forgot to save | `show startup-config` vs `show running-config` | `copy running-config startup-config` |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why dual-stack instead of an IPv6-only network?** Dual-stack lets every existing IPv4-dependent system keep working unmodified while IPv6 capability is added incrementally. An IPv6-only network is the eventual destination for most organizations, but getting there requires every application, printer, security appliance, and third-party integration to support IPv6 first — which, in most real networks, is not true on day one. Dual-stack is the transition strategy, not a permanent end state, but it's a transition that can reasonably last years.
- **Why manual global address assignment instead of EUI-64 for this lab's addressing table?** Manual assignment (`::1`, `::2`, `::3`...) produces short, human-memorable, predictable addresses — exactly what you want for infrastructure devices (routers, servers, gateways) that administrators need to type, log, and recognize at a glance. EUI-64 produces addresses that are deterministic but not memorable (`2001:DB8:0:1:21A:2BFF:FE3C:4D5E`), and they change if the network card is ever replaced (new MAC → new address). Real deployments commonly use manual assignment for infrastructure/servers and EUI-64 or SLAAC for general end-user devices, which is exactly the split CCNA expects you to understand even though this lab's PCs also use manual addresses for consistency and predictability during verification.
- **Why is EUI-64 still worth knowing if manual assignment is often preferred for infrastructure?** Two reasons: first, SLAAC-based host autoconfiguration (which many real end-user devices use by default, especially non-Windows/non-domain-joined hosts) uses this exact algorithm, so you need to be able to predict and recognize the resulting addresses during troubleshooting even when you didn't configure them yourself. Second, it's directly testable on the CCNA exam as a bit-manipulation exercise, and the only way to be fast and accurate at it is to have actually done the derivation by hand, which is why Section 4.4 walks through it manually rather than just stating the rule.
- **Why no static or dynamic routing protocol needed here?** All three LANs are directly connected to R1 — there's no second router, so there's no route that isn't already known via a connected interface. This is the simplest possible topology on purpose; Day 32 and Day 33 build on this exact addressing scheme by adding static IPv6 routes once a second router enters the picture.
- **Why /64 on every LAN instead of matching each LAN's actual host count the way IPv4 subnetting would?** Covered in depth in Section 4.6 — the short version is that IPv6's addressing model was deliberately designed to make this question not worth asking. A /64 with 3 hosts and a /64 with 3,000 hosts are configured identically; there is no efficiency gained by shrinking below /64, and doing so actively breaks SLAAC/EUI-64 compatibility for no benefit.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...your company's ISP announces they're deprecating static public IPv4 blocks in favor of CGNAT for new circuits, and your team needs a rollout plan for native IPv6 on customer-facing services before that migration forces the issue.
- ...a newly acquired subsidiary's infrastructure is already dual-stack or IPv6-only, and integrating the two networks means your side needs to speak IPv6 before any east-west traffic between the companies can work.
- ...a government or enterprise RFP requires proof of IPv6 capability, and you're the engineer tasked with standing up a working dual-stack proof-of-concept exactly like this lab, on a small scale, before it's rolled out network-wide.
- ...you're debugging "our internal app works on WiFi but not on the guest network" and the actual cause turns out to be a link-local-only misconfiguration on one segment — recognizing FE80::/10 addresses on sight, as this lab trains, is what makes that diagnosis fast instead of a multi-hour mystery.
- ...you inherit a network where someone hand-typed IPv6 addresses using EUI-64 output without understanding the algorithm, and you need to predict what address a *replacement* network card will produce before you swap hardware into production.

---

## 12. Stretch Goal

Once the base lab works end-to-end, try one or more of the following without referring back to the steps above:

1. **Add a fourth LAN** off a new R1 interface, using the next sequential `2001:DB8:0:4::/64` prefix, and extend the addressing table, configuration, and verification yourself using this manual as a template only for structure, not content.
2. **Reconfigure one interface to use EUI-64** instead of a manual address (Section 6.4), then manually re-derive by hand what address you expect *before* checking `show ipv6 interface brief` — confirm your Section 4.4 math against the router's actual output.
3. **Disable `ipv6 unicast-routing` on purpose**, confirm that inter-LAN IPv6 ping breaks exactly as the Troubleshooting Guide (Section 9, Step 4) predicts, then re-enable it — this builds the diagnostic instinct that matters more than memorizing the fix.
4. **Write out, fully expanded (no `::` shorthand, no leading-zero trimming), the complete 128-bit form of all three of R1's global addresses** from Section 4.1 — this is the reverse operation of Section 4.2 and is exactly the kind of manipulation the exam tests both directions.

---

## 13. Self-Assessment

Before moving to Day 32, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, the difference between `ipv6 enable` and `ipv6 unicast-routing`, and why forgetting the latter is a silent failure?
- [ ] Given any 48-bit MAC address, can you derive its EUI-64 interface identifier by hand — including correctly flipping the 7th bit of the first byte?
- [ ] Can you explain why every IPv6 interface has a link-local address whether or not you configure a global one, and why FE80::/10 addresses never route off-segment?
- [ ] Can you expand a shorthand IPv6 address (with `::` and trimmed leading zeros) back to its full 32-hex-digit form, and collapse it back down?
- [ ] Can you explain why IPv6 subnetting math uses nibble (4-bit/hex-digit) boundaries instead of IPv4's octet boundaries, in your own words?
- [ ] Can you explain, in one sentence each, why a company would choose dual-stack over an immediate IPv6-only cutover, and over staying IPv4-only?
- [ ] Can you name at least 4 of the 8 common mistakes from Section 8 without looking?
- [ ] Could you explain this lab's business case (Section 2) to a non-technical manager in under 2 minutes?

If you answered "no" to more than two of these, re-do the lab from scratch (not by copy-pasting commands) before moving on.

---

## 14. Key Concepts Demonstrated

- **Dual-stack architecture** — IPv4 and IPv6 coexisting on identical physical infrastructure with zero interdependence between the two stacks
- **Global IPv6 unicast routing** — the `ipv6 unicast-routing` on-switch and why it's separate from per-interface IPv6 enablement
- **EUI-64 interface identifier derivation** — manual bit-level construction from a MAC address
- **Link-local addressing** — automatic, always-present, non-routable FE80::/10 addresses and their operational role
- **IPv6 address notation** — `::` collapsing rules, leading-zero trimming, and prefix-length-only subnetting
- **Nibble-boundary subnetting logic** — how IPv6's addressing math structurally differs from IPv4's octet-based approach
- **Dual-stack host configuration** — independent IPv4 and IPv6 addressing/gateway fields on a single NIC

---

## 15. What I Learned

Configuring the router side of dual-stack is almost deceptively simple — three interfaces, three addresses, one global command — which is exactly why the failure modes matter more than the happy path here. The single global command (`ipv6 unicast-routing`) failing *silently* rather than throwing an error the way a missing `no shutdown` does is the kind of thing that only becomes obvious once you've been burned by it, which is why Section 8 and Section 9 both lead with it.

The EUI-64 derivation was the part that took real, deliberate practice rather than pattern-matching from IPv4 experience. Flipping a single specific bit in the first byte of a MAC address isn't something you can eyeball — writing it out in binary, locating bit 7 explicitly, and flipping it by hand is the only way to get it reliably right, and that manual repetition is exactly what makes the exam-style version of this question fast instead of a source of careless errors.

Seeing IPv4 and IPv6 pings both succeed independently, over the identical physical path, was the clearest possible demonstration of what "dual-stack" actually means in practice — not a hybrid protocol, not a translation layer, just two complete, independent Layer 3 stacks sharing one wire.

This lab is the foundation for what comes next:

- Static IPv6 routing across multiple routers (Day 32, Day 33)
- IPv6 access control and filtering
- SLAAC and stateless/stateful DHCPv6
- IPv6-aware NAT and transition mechanisms (NAT64, 464XLAT) for eventual IPv6-only migration

---

## 16. Skills Practiced

- IPv6 global unicast, link-local, and multicast address theory
- Manual EUI-64 interface identifier derivation from a MAC address
- Cisco IOS IPv6 routing and interface configuration
- Dual-stack host configuration (Packet Tracer PC IP Configuration)
- IPv6 verification and troubleshooting (`show ipv6 interface brief`, `show ipv6 route`, `show ipv6 protocols`)
- IPv6 vs. IPv4 addressing/subnetting comparative reasoning

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology that mirrors the design above using free, open-source images, built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Original device | GNS3 image |
|---|---|---|
| Router (R1) | Cisco router | VyOS |
| Switches (SW1, SW2, SW3) | Cisco 2960-class switch | Open vSwitch |
| PCs (PC1, PC2, PC3) | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script. Note that VyOS's IPv6 CLI syntax (`set interfaces ethernet eth0 address 2001:db8:0:1::1/64`) differs from IOS syntax shown throughout this manual — the *concepts* (dual-stack, EUI-64, link-local, /64 convention) transfer directly even though the exact commands don't. A brief VyOS IPv6 command reference is included in the GNS3 README.
