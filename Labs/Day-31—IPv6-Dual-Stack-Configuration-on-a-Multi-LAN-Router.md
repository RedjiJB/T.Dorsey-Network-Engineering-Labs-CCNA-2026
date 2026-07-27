# Day 31 — IPv6 Dual-Stack Configuration on a Multi-LAN Router

## Overview

Today's lab was an **IPv4/IPv6 dual-stack** build — keeping existing IPv4 while adding IPv6 on the same interfaces. The mission: enable IPv6 routing, assign global IPv6 addresses to a router's three LAN interfaces, configure PCs with IPv6 addresses and gateways, then verify inter-LAN ping over both protocols.

IPv6 isn't "soon." It's here. Every enterprise network has dual-stack. This is a core CCNA skill.

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201).png">
  </a>
</p>

---

## Lab Scenario

> "The IPv4 configuration of each device is complete. Perform the following IPv6 configurations to create an IPv4/IPv6 'dual-stack' network."

IPv4 is left untouched. All work happens on the IPv6 side.

---

## Topology Summary

| Device | Role | IPv4 | IPv6 |
|--------|------|------|------|
| R1 G0/0 | LAN-1 gateway | 192.168.1.1/24 | 2001:DB8:0:1::1/64 |
| R1 G0/1 | LAN-2 gateway | 192.168.2.1/24 | 2001:DB8:0:2::1/64 |
| R1 G0/2 | LAN-3 gateway | 192.168.3.1/24 | 2001:DB8:0:3::1/64 |
| PC1 | LAN-1 host | 192.168.1.2/24 | 2001:DB8:0:1::2/64 |
| PC2 | LAN-2 host | 192.168.2.2/24 | 2001:DB8:0:2::2/64 |
| PC3 | LAN-3 host | 192.168.3.2/24 | 2001:DB8:0:3::2/64 |
| SW1/SW2/SW3 | Layer 2 | — | — |

Subnets:
- `192.168.1.0/24` ↔ `2001:DB8:0:1::/64`
- `192.168.2.0/24` ↔ `2001:DB8:0:2::/64`
- `192.168.3.0/24` ↔ `2001:DB8:0:3::/64`

---

## Lab Questions and Solutions

**1. Enable IPv6 routing on R1.**

IOS disables IPv6 forwarding by default. A router with `ipv6 enable` on interfaces still won't route between them unless global IPv6 routing is turned on.

```cisco
R1(config)#ipv6 unicast-routing
```

**Verify:**
```cisco
R1#show ipv6 protocols
```
```
IPv6 Routing Protocol is "connected"
IPv6 Routing Protocol is "static"
```

No error = routing is enabled. There's no explicit "enabled" message; absence of error is the confirmation.

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201)-1.1.png">
  </a>
</p>

---

**2. Configure the appropriate IPv6 addresses on R1.**

R1 has three LAN-facing interfaces. Each needs a global IPv6 address in the corresponding `/64` subnet.

**R1 Configuration:**
```cisco
interface g0/0
 ipv6 address 2001:DB8:0:1::1/64
 ipv6 enable

interface g0/1
 ipv6 address 2001:DB8:0:2::1/64
 ipv6 enable

interface g0/2
 ipv6 address 2001:DB8:0:3::1/64
 ipv6 enable
```

**Why `::1` for the gateway?** IPv6 convention reserves the first address in a subnet for the router. `2001:DB8:0:1::1` = gateway. Hosts get `::2`, `::3`, etc.

**Verification:**
```cisco
R1#show ipv6 interface brief
```
```
GigabitEthernet0/0    [up/up]
    FE80::...:1 (link-local)
    2001:DB8:0:1::1 (global)

GigabitEthernet0/1    [up/up]
    FE80::...:1 (link-local)
    2001:DB8:0:2::1 (global)

GigabitEthernet0/2    [up/up]
    FE80::...:1 (link-local)
    2001:DB8:0:3::1 (global)
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201)-2.1.png">
  </a>
</p>

---

**3. Confirm your configurations. What IPv6 addresses are present on each interface?**

```cisco
R1#show ipv6 interface g0/0
```
```
GigabitEthernet0/0 is up, line protocol is up
  IPv6 is enabled, link-local address is FE80::...:1
  Global unicast address(es):
    2001:DB8:0:1::1, subnet is 2001:DB8:0:1::/64
  Joined group address(es): FF02::1 FF02::2 FF02::1:FF00:1
```

| Interface | Global IPv6 | Prefix | Link-Local |
|-----------|-------------|--------|------------|
| G0/0 | 2001:DB8:0:1::1 | /64 | FE80::…:1 |
| G0/1 | 2001:DB8:0:2::1 | /64 | FE80::…:1 |
| G0/2 | 2001:DB8:0:3::1 | /64 | FE80::…:1 |

Every interface in IPv6 always has a **link-local address** (FE80::/10) automatically assigned when `ipv6 enable` is active. This is separate from the global address.

---

**4. Configure the appropriate IPv6 addresses on each PC. Configure the correct default gateway.**

**PC Configuration syntax (Packet Tracer Desktop → IP Configuration):**

PC1:
```
IPv4: 192.168.1.2 / 255.255.255.0
Gateway: 192.168.1.1
IPv6: 2001:DB8:0:1::2 / 64
Gateway: 2001:DB8:0:1::1
```

PC2:
```
IPv4: 192.168.2.2 / 255.255.255.0
Gateway: 192.168.2.1
IPv6: 2001:DB8:0:2::2 / 64
Gateway: 2001:DB8:0:2::1
```

PC3:
```
IPv4: 192.168.3.2 / 255.255.255.0
Gateway: 192.168.3.1
IPv6: 2001:DB8:0:3::2 / 64
Gateway: 2001:DB8:0:3::1
```

**Verification on PC2 (example):**
```cisco
PC2>ipconfig
```
```
FastEthernet0 Connection:

Connection-specific DNS Suffix.. :
Link-local IPv6 Address........: FE80::2D0:97FF:FE12:77E2
IPv6 Address...................: 2001:DB8:0:2::2
IPv4 Address...................: 192.168.2.2
Subnet Mask....................: 255.255.255.0
Default Gateway................: 2001:DB8:0:2::1
                               192.168.2.1
```

Note the default gateway has TWO lines: one IPv6, one IPv4. Dual-stack means dual gateways.

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201)-4.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201)-4.2.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201)-4.3.png">
  </a>
</p>

---

**5. Attempt to ping between the PCs (IPv4 and IPv6).**

**Within the same LAN (PC1 ↔ PC2 via router — inter-subnet):**

PC1 ping PC2 over IPv4:
```cisco
PC1>ping 192.168.2.2
```
```
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

PC1 ping PC2 over IPv6:
```cisco
PC1>ping 2001:DB8:0:2::2
```
```
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Both succeed because R1 is routing both protocols.

**Verification on R1:**
```cisco
R1#show ipv6 route
```
```
C    2001:DB8:0:1::/64 is directly connected, GigabitEthernet0/0
C    2001:DB8:0:2::/64 is directly connected, GigabitEthernet0/1
C    2001:DB8:0:3::/64 is directly connected, GigabitEthernet0/2
L    2001:DB8:0:1::1/128 is directly connected, GigabitEthernet0/0
L    2001:DB8:0:2::1/128 is directly connected, GigabitEthernet0/1
L    2001:DB8:0:3::1/128 is directly connected, GigabitEthernet0/2
```

Connected routes (`C`) show each LAN prefix. Local routes (`L`) show the router's own addresses.

---

## Dual-Stack Concepts

| Concept | IPv4 | IPv6 |
|---------|------|------|
| Address length | 32 bits | 128 bits |
| Notation | Dotted decimal (192.168.1.1) | Colon-separated hex (2001:DB8:0:1::1) |
| Subnet mask | 255.255.255.0 | /64 prefix length |
| Default gateway | Single IPv4 address | Separate IPv6 address (often ::1) |
| Link-local | 169.254.x.x | FE80::/10 (auto-assigned) |
| Broadcast | 255.255.255.255 | None — uses multicast FF02::1 |
| Loopback | 127.0.0.1 | ::1 |

**Dual-stack means:** the same physical interface carries both IPv4 and IPv6. No tunneling, no translation. Two independent protocol stacks running side by side.

**2001:DB8::/32** is the IANA-reserved documentation prefix. It will never be assigned to a real network. Use it in labs, examples, and exams — never in production.

---

## Commands Practiced

```cisco
! Router — enable IPv6 routing
R1(config)#ipv6 unicast-routing

! Router — interface IPv6 configuration
interface g0/0
 ipv6 address 2001:DB8:0:1::1/64
 ipv6 enable

! Router — verification
show ipv6 interface brief
show ipv6 route
show ipv6 protocols

! PC — dual-stack configuration (Packet Tracer Desktop tab)
IPv4: <address> / <mask> / <gateway>
IPv6: <address> / 64 / <gateway>

! PC — verification
ipconfig
ping <ipv4-address>
ping <ipv6-address>
```

---

## What I Learned

**`ipv6 unicast-routing` is the on-switch for IPv6 forwarding.** Without it, `ipv6 enable` and `ipv6 address` on interfaces still won't make the router route between subnets. The screenshots showed R1 with all three interfaces configured, but `show ipv6 route` would be empty without this global command.

**Every IPv6 interface always has a link-local address.** FE80::/10 is automatically generated from the interface MAC. You don't configure it. It exists whether you assign a global address or not. PCs show it in `ipconfig` output.

**`::` is the shorthand for consecutive zeros.** `2001:DB8:0:0:0:0:0:1` = `2001:DB8::1`. `2001:DB8:0:1::2` in the screenshots is shorthand for `2001:0DB8:0000:0001:0000:0000:0000:0002`.

**One `::` per address only.** You can't do `2001::0:1::2` — that's invalid. Exactly one block of all-zeros can be collapsed.

**IPv6 uses /64 subnets by convention.** An IPv6 /64 gives 2^64 addresses per subnet. You almost never use anything else. The LAN is always one /64.

**PCs need both gateways configured.** In the screenshots, PC2's `ipconfig` showed the IPv6 gateway AND the IPv4 gateway stacked vertically. That's dual-stack working correctly.

**Ping works identically across protocols.** `ping 192.168.2.2` and `ping 2001:DB8:0:2::2` both succeed because R1 is routing both. The transport layer is the same. The difference is entirely in addressing.

---

## Lab Status

✅ Day 31 Complete

### Topics Covered

* IPv4/IPv6 dual-stack architecture
* Global IPv6 routing: `ipv6 unicast-routing`
* Interface IPv6 addresses: `ipv6 address <prefix>::<host>/64`
* Auto-configured link-local addresses (FE80::/10)
* Router and PC IPv6 configuration
* PC dual-stack gateway configuration
* `show ipv6 interface brief`, `show ipv6 route`
* Inter-subnet IPv6 routing and ping verification
* IPv6 documentation prefix (2001:DB8::/32)
* IPv6 shorthand notation and `::` rules

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
