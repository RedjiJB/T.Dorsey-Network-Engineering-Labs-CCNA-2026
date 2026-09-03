# Day 32 — IPv6 Addressing: EUI-64, Link-Local, and Static Routes

## Overview

Today's lab was an **IPv6 addressing deep dive** — no manual address assignment on router-to-router links. Instead, I used **EUI-64** to auto-generate IPv6 addresses from MAC addresses, enabled IPv6 on interfaces without global addresses (link-local only), and configured **static routes** so two isolated LANs could communicate.

This is the lab that proves IPv6 isn't just "IPv4 with longer addresses." It has its own identity model, its own auto-configuration, and its own routing syntax.

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202).png">
  </a>
</p>

---

## Lab Scenario

> "Interfaces are enabled and configured with IPv4. You will configure IPv6 in the network."

IPv4 is untouched. All work is IPv6-only on top of the existing IPv4 stack.

---

## Topology Summary

| Device | Role | Interface | Global IPv6 | Link-Local |
|--------|------|-----------|-------------|------------|
| R1 | Router | G0/1 (LAN-1) | 2001:DB8::230:F2FF:FE36:4502 | FE80::230:F2FF:FE36:4502 |
| R1 | Router | G0/0 (WAN) | unassigned | FE80::230:F2FF:FE36:4502 |
| R2 | Router | G0/1 (LAN-2) | 2001:DB8:0:1:201:63FF:FE80:B802 | FE80::201:63FF:FE80:B802 |
| R2 | Router | G0/0 (WAN) | unassigned | FE80::201:63FF:FE80:B802 |
| PC1 | Host | Fa0 | 2001:DB8::2 | FE80::…:2 |
| PC2 | Host | Fa0 | 2001:DB8:0:1::2 | FE80::…:2 |

Subnets:
- `2001:DB8::/64` — PC1 LAN (R1 G0/1)
- `2001:DB8:0:1::/64` — PC2 LAN (R2 G0/1)
- WAN link between R1/R2: no global prefix, link-local only

---

## Lab Questions and Solutions

**1. Use EUI-64 to configure IPv6 addresses on G0/1 of R1/R2.**

**EUI-64 Formula:**
```
Split the 48-bit MAC address in half.
Insert FFFE in the middle.
Flip the 7th bit (the Universal/Local bit).
```

**Before configuring, calculate the EUI-64 interface IDs:**

For R1 G0/1 MAC `00:30:F2:36:45:02`:
- Split: `0030F2` + `364502`
- Insert FFFE: `0030F2:FFFE:364502`
- Flip 7th bit of first byte: `00` → `02` (bit 2 set)
- Result: `0230:F2FF:FE36:4502`

Full address: `2001:DB8::0230:F2FF:FE36:4502`

For R2 G0/1 MAC `00:21:63:80:B8:02`:
- Split: `002163` + `80B802`
- Insert FFFE: `002163:FFFE:80B802`
- Flip 7th bit: `00` → `02`
- Result: `021:63FF:FE80:B802`

Full address: `2001:DB8:0:1::021:63FF:FE80:B802`

Wait — the screenshots actually show R2's address as `2001:DB8:0:1:201:63FF:FE80:B802`. The `201` is the same flipped-bit result, just formatted with the full hextet expanded: `0201` → `201`.

**Configuration on R1:**
```cisco
interface g0/1
 ipv6 address 2001:DB8::230:F2FF:FE36:4502/64
 ipv6 enable
```

**Configuration on R2:**
```cisco
interface g0/1
 ipv6 address 2001:DB8:0:1:201:63FF:FE80:B802/64
 ipv6 enable
```

**Verification:**
```cisco
R1#show ipv6 interface brief
```
```
GigabitEthernet0/1 [up/up]
    FE80::230:F2FF:FE36:4502 (link-local)
    2001:DB8::230:F2FF:FE36:4502 (global)
```

```cisco
R2#show ipv6 interface brief
```
```
GigabitEthernet0/1 [up/up]
    FE80::201:63FF:FE80:B802 (link-local)
    2001:DB8:0:1:201:63FF:FE80:B802 (global)
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202)-1.1.png">
<img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202)-1.2.png">
  </a>
</p>

---

**2. Configure the appropriate IPv6 addresses and default gateways on PC1 and PC2.**

**PC1 Configuration:**
```
IPv4: 192.168.1.2 / 255.255.255.0 / 192.168.1.1
IPv6: 2001:DB8::2 / 64 / 2001:DB8::230:F2FF:FE36:4502
```

**PC2 Configuration:**
```
IPv4: 192.168.2.2 / 255.255.255.0 / 192.168.2.1
IPv6: 2001:DB8:0:1::2 / 64 / 2001:DB8:0:1:201:63FF:FE80:B802
```

**Verification on PC1:**
```cisco
PC1>ipconfig
```
```
FastEthernet0 Connection:

IPv6 Address: 2001:DB8::2
Link-local IPv6 Address: FE80::…
Default Gateway: 2001:DB8::230:F2FF:FE36:4502 (R1)
                192.168.1.1
```

---

**3. Enable IPv6 on G0/0 of R1/R2 without explicitly configuring an IPv6 address.**

The WAN link between R1 and R2 doesn't need a globally routable IPv6 address for this lab. The routers only need **link-local addresses** to exchange routing information.

```cisco
! R1
interface g0/0
 ipv6 enable

! R2
interface g0/0
 ipv6 enable
```

**Verification:**
```cisco
R1#show ipv6 interface brief
```
```
GigabitEthernet0/0 [up/up]
    FE80::230:F2FF:FE36:4502 (link-local only, no global address)
    unassigned
```

`ipv6 enable` auto-generates a link-local address from the interface MAC. No global prefix needed. This is how Cisco routers talk to each other on adjacent links without consuming address space.

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202)-2.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202)-2.2.png">
  </a>
</p>

---

**4. Configure static routes on R1/R2 to enable PC1 to ping PC2.**

**Diagnosis:**
```cisco
PC1>ping 2001:DB8:0:1::2
```
```
Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
```

R1 knows `2001:DB8::/64` (direct). But R1 doesn't know `2001:DB8:0:1::/64`.

```cisco
R1#show ipv6 route
```
```
C    2001:DB8::/64 is directly connected, GigabitEthernet0/1
```

No route to PC2's LAN. Need static routes on both routers.

**R1 static route:**
```cisco
R1(config)#ipv6 route 2001:DB8:0:1::/64 2001:DB8:0:1::1
```

Wait — R1 doesn't know R2's address. Use the link-local address of R2's G0/0:

```cisco
R1(config)#ipv6 route 2001:DB8:0:1::/64 FE80::201:63FF:FE80:B802
```

**R2 static route:**
```cisco
R2(config)#ipv6 route 2001:DB8::/64 FE80::230:F2FF:FE36:4502
```

**Verification:**
```cisco
R1#show ipv6 route
```
```
C    2001:DB8::/64 is directly connected, GigabitEthernet0/1
S    2001:DB8:0:1::/64 [1/0] via FE80::201:63FF:FE80:B802
```

```cisco
PC1>ping 2001:DB8:0:1:201:63FF:FE80:B802
```
```
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
TTL=255
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202)-3.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202)-4.1.png">
  </a>
</p>

---

## EUI-64 Deep Dive

**Process:**
1. Take the 48-bit MAC address: `xx:xx:xx:xx:xx:xx`
2. Split it in half: `xx:xx:xx` + `xx:xx:xx`
3. Insert `FFFE` in the middle: `xx:xx:xx:FFFE:xx:xx:xx`
4. Flip the 7th bit of the first byte (binary XOR 00000010)

**Example — MAC `00:30:F2:36:45:02`:**
```
Original:    00:30:F2:36:45:02
Split:       00:30:F2  +  36:45:02
Insert FFFE: 00:30:F2:FFFE:36:45:02
Flip 7th bit (00 → 02): 02:30:F2:FFFE:36:45:02
IPv6 tail:   230:F2FF:FE36:4502
Full addr:   2001:DB8::230:F2FF:FE36:4502
```

**Why flip the 7th bit?** The 7th bit is the Universal/Local (U/L) bit. In MAC addresses, 0 = globally unique (OUI-assigned), 1 = locally administered. IPv6 EUI-64 inverts this by convention to indicate the address is globally scoped.

**EUI-64 scope:**
- Works on any interface with a burned-in MAC
- Generates a unique, stable global address
- No DHCP or SLAAC needed for the host portion
- The `/64` prefix comes from the router

---

## Link-Local Addresses

| Feature | Detail |
|---------|--------|
| Range | FE80::/10 |
| Auto-generated? | Yes, when `ipv6 enable` is configured |
| Scope | Link only — never routed |
| Uniqueness | Unique per link, same address can exist on multiple interfaces |
| Required? | Yes — IPv6 Neighbor Discovery needs it |
| Manual config? | Optional, but rarely needed |

Every IPv6 interface has at least one link-local address, even if no global address is configured. Screenshots confirmed R1's G0/0 had only a link-local (`FE80::230:F2FF:FE36:4502`) with `unassigned` for global.

**When using `ipv6 route` with link-local next-hop:**
```cisco
ipv6 route <destination-prefix> <next-hop-link-local>
```

The router uses the link-local address of the neighbor's outgoing interface as the next-hop. This works because link-local addresses are unique per link and both routers auto-generate them.

---

## Static Route Syntax

```cisco
ipv6 route <destination-prefix> <next-hop> [administrative-distance]
```

Examples:
```cisco
! Via link-local next-hop (no global address on WAN)
ipv6 route 2001:DB8:0:1::/64 FE80::201:63FF:FE80:B802

! Via global next-hop (when neighbor has global address)
ipv6 route 2001:DB8:0:1::/64 2001:DB8:0:1::1

! Via outgoing interface only (point-to-point, no next-hop needed)
ipv6 route 2001:DB8:0:1::/64 g0/0
```

On point-to-point serial links, you can specify the interface as the next-hop. On multi-access Ethernet, you must specify the neighbor's address.

**Verification:**
```cisco
show ipv6 route
show ipv6 route static
show ipv6 route <prefix>
```

---

## Commands Practiced

```cisco
! EUI-64 global addressing
interface g0/1
 ipv6 address 2001:DB8:<prefix>::<eui64>/64
 ipv6 enable

! Link-local only (no global address)
interface g0/0
 ipv6 enable

! Static route
ipv6 route <destination-prefix> [length] <next-hop-address>

! Verification
show ipv6 interface brief
show ipv6 route
show ipv6 route static
ping <ipv6-address>
```

---

## What I Learned

**EUI-64 is elegant.** It gives every interface a unique, stable, globally routable address without manual assignment or DHCP. The MAC address is already unique — just expand it to 64 bits and stuff it into the IPv6 interface ID.

**Link-local addresses are the unsung heroes of IPv6.** They're always there, always auto-generated, and they're the backbone of neighbor discovery and static routing when you don't want to consume global address space on a WAN link.

**Static IPv6 routes feel like IPv4 routes but with longer addresses.** Syntax is nearly identical: destination prefix, next-hop, administrative distance. The mental mode shift is getting used to the `FE80::` link-local next-hop syntax.

**The screenshots confirmed everything works end-to-end.** PC1 ping PC2's EUI-64 address (`2001:DB8:0:1:201:63FF:FE80:B802`) with 0% packet loss, TTL=255. The link-local next-hop route was the missing piece.

**Note from the lab:** "We will study IPv6 static routes in depth in Day 33." This lab introduced the syntax at a surface level. Day 33 will go deeper.

---

## Lab Status

✅ Day 32 Complete

### Topics Covered

* EUI-64 interface ID generation: split, insert FFFE, flip 7th bit
* Calculating EUI-64 addresses before configuration
* Global IPv6 addressing on LAN interfaces
* Link-local addressing: `ipv6 enable` without global address
* Static IPv6 routes with link-local next-hop
* End-to-end IPv6 ping verification
* IPv6 link-local vs global scope
* IPv6 address notation and hextet formatting

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
