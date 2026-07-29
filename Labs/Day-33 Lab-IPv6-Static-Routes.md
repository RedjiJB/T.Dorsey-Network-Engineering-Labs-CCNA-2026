# Day 33 — IPv6 Static Routes, SLAAC, and Backup Paths

## Overview

Today's lab was an **IPv6 static routing** exercise across three routers with two paths between R1 and R3. I used **SLAAC** to auto-configure PC addresses, configured static routes on all three routers, and set up R2 as a backup path with a higher administrative distance.

This is the lab that bridges IPv6 theory with production routing. SLAAC replaces DHCPv6 for host addressing. Static routes replace dynamic protocols when you need precise control over path selection.

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes.png">
  </a>
</p>

---

## Lab Scenario

> "IPv6 addresses have been pre-configured on the routers. The serial connections use link-local addresses only."

You are configuring IPv6 routing and host addressing across a 3-router, 2-LAN network with two paths between endpoints.

---

## Topology Summary

| Device | Role | Interface | IPv6 Address | Prefix |
|--------|------|-----------|--------------|--------|
| R1 | Router | G0/0 | 2001:DB8:0:1::1 | /64 (PC1 LAN) |
| R1 | Router | G0/1 | 2001:DB8:0:13::1 | /64 (R1–R3 direct) |
| R1 | Router | S0/0/0 | link-local only | DCE serial to R2 |
| R2 | Backup router | S0/0/0 | link-local only | DCE serial to R1 |
| R2 | Backup router | S0/0/1 | link-local only | DCE serial to R3 |
| R3 | Router | G0/0 | 2001:DB8:0:3::1 | /64 (PC2 LAN) |
| R3 | Router | G0/1 | 2001:DB8:0:13::2 | /64 (R1–R3 direct) |
| R3 | Router | S0/0/0 | link-local only | DCE serial to R2 |
| PC1 | Host | Fa0 | 2001:DB8:0:1::2 | /64 (via SLAAC) |
| PC2 | Host | Fa0 | 2001:DB8:0:3::2 | /64 (via SLAAC) |

Subnets:
- `2001:DB8:0:1::/64` — PC1 LAN
- `2001:DB8:0:3::/64` — PC2 LAN
- `2001:DB8:0:13::/64` — R1–R3 direct link
- Serial segments R1–R2 and R2–R3: link-local only

---

## Lab Questions and Solutions

**1. Enable IPv6 routing on each router.**

Same as Day 31 — global on/off switch.

```cisco
R1(config)#ipv6 unicast-routing
R2(config)#ipv6 unicast-routing
R3(config)#ipv6 unicast-routing
```

---

**2. Use SLAAC to configure IPv6 addresses on the PCs. What IPv6 address was configured on each PC?**

**SLAAC (Stateless Address Autoconfiguration):**
- Router sends Router Advertisements (RA) on the LAN
- RA contains the /64 prefix
- PC generates its own interface ID (typically EUI-64 or random privacy address)
- PC configures itself — no DHCPv6 needed

**PC1 Configuration (Packet Tracer Config → IPv6 → Automatic):**
```
IPv6 Address: 2001:DB8:0:1::2
Prefix Length: /64
Default Gateway: 2001:DB8:0:1::1
```

**PC2 Configuration:**
```
IPv6 Address: 2001:DB8:0:3::2
Prefix Length: /64
Default Gateway: 2001:DB8:0:3::1
```

**Why SLAAC works here:**
- R1 G0/0 is configured with `ipv6 enable` (implied by having a global address)
- R1 G0/0 has `2001:DB8:0:1::1/64`
- R1 sends Router Advertisements with prefix `2001:DB8:0:1::/64`
- PC1 uses SLAAC to generate `2001:DB8:0:1::2`

**Verification on PC1:**
```cisco
PC1>ipconfig
```
```
IPv6 Address: 2001:DB8:0:1::2
Default Gateway: 2001:DB8:0:1::1
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-1.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-1.2.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-1.3.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-2.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-2.2.png">
  </a>
</p>

---

**3. Configure static routes on the routers to allow PC1 and PC2 to ping each other. The path via R2 should be used only as a backup path.**

**Topology for routing:**

```
PC1 (2001:DB8:0:1::2)
    |
    v
  R1 [G0/0: 2001:DB8:0:1::1] — [G0/1: 2001:DB8:0:13::1] — R3 [G0/1: 2001:DB8:0:13::2] [G0/0: 2001:DB8:0:3::1]
    |                                                  |
    v                                                  v
  PC1 LAN                                          R3 ←←← R2 (backup path)
```

Primary path: R1 → R3 via G0/1/G0/1 (2001:DB8:0:13::/64)
Backup path: R1 → R2 → R3 via serial links (link-local only)

**R1 Static Routes:**

R1 already knows 2001:DB8:0:1::/64 (direct). R1 needs a route to 2001:DB8:0:3::/64 (PC2 LAN):
```cisco
! Primary route via R3 direct (AD 1)
R1(config)#ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:13::2

! Backup route via R2 (AD 100)
R1(config)#ipv6 route 2001:DB8:0:3::/64 FE80::<R2-S0/0/0-link-local> 100
```

**R2 Static Routes:**

R2 is the backup path. It needs routes for both LANs:
```cisco
! Route to PC1's LAN via R1
R2(config)#ipv6 route 2001:DB8:0:1::/64 Serial0/0/0

! Route to PC2's LAN via R3
R2(config)#ipv6 route 2001:DB8:0:3::/64 Serial0/0/1
```

**R3 Static Routes:**

R3 already knows 2001:DB8:0:3::/64 (direct). R3 needs a route to 2001:DB8:0:1::/64:
```cisco
! Primary route via R1 direct (AD 1)
R3(config)#ipv6 route 2001:DB8:0:1::/64 2001:DB8:0:13::1

! Backup route via R2 (AD 100)
R3(config)#ipv6 route 2001:DB8:0:1::/64 FE80::<R2-S0/0/0-link-local> 100
```

**Verification on R1:**
```cisco
R1#show ipv6 route
```
```
C    2001:DB8:0:1::/64 is directly connected, GigabitEthernet0/0
C    2001:DB8:0:13::/64 is directly connected, GigabitEthernet0/1
S    2001:DB8:0:3::/64 [1/0] via 2001:DB8:0:13::2
S    2001:DB8:0:3::/64 [100/0] via FE80::<R2-link-local>
```

**Verification on R3:**
```cisco
R3#show ipv6 route static
```
```
* 2001:DB8:0:1::/64 via 2001:DB8:0:13::1, GigabitEthernet0/1, distance 1
* 2001:DB8:0:1::2/128 via 2001:DB8:0:13::1, GigabitEthernet0/1, distance 1
* 2001:DB8:0:1::/64 via FE80::20B:BEFF:FE7D:4901, Serial0/0/0, distance 100
```

Notice: the primary route has distance 1. The backup route has distance 100. The /128 host route to PC1 specifically ensures R3 has a precise entry for the actual host.

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-3.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-3.2.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes-3.3.png">
  </a>
</p>

**End-to-End Ping:**
```cisco
PC1>ping 2001:DB8:0:3::2
```
```
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
TTL=255
```

Traffic flows: PC1 → R1 G0/0 → R1 G0/1 → R3 G0/1 → PC2

---

## SLAAC (Stateless Address Autoconfiguration)

| Feature | Detail |
|---------|--------|
| DHCPv6 required? | No |
| Router involved? | Yes — sends Router Advertisements |
| Address source | MAC-based EUI-64 or random privacy |
| Prefix source | RA from the local router |
| DNS | Not provided by SLAAC (DHCPv6 needed for DNS) |

**Router Advertisement (RA) triggers:**
- Router has `ipv6 enable` on the interface
- RA multicast to `FF02::1` (all nodes)

In Packet Tracer, enabling SLAAC on the PC (Config tab → IPv6 → Automatic) makes the PC listen for RAs and generate its own address from the received prefix.

**SLAAC on PC1:**
- Router R1 advertises `2001:DB8:0:1::/64`
- PC1 generates EUI-64: `2001:DB8:0:1::2`
- PC1 set gateway: `2001:DB8:0:1::1`

---

## Administrative Distance for Backup Paths

| Route Type | AD | Notes |
|------------|----|-------|
| Connected | 0 | Always preferred |
| Static (default) | 1 | Primary static route |
| Static (custom) | 100-255 | Backup path |
| OSPFv3 intra-area | 110 | Dynamic |
| OSPFv3 inter-area | 115 | Dynamic |

**Setting backup static routes:**
```cisco
! Primary route (default AD = 1)
ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:13::2

! Backup route (higher AD = less preferred)
ipv6 route 2001:DB8:0:3::/64 FE80::<R2-link-local> 100
```

When the primary (AD 1) fails, the router automatically falls back to the backup (AD 100). No protocol re-convergence needed; it's still static.

**The screenshots confirmed:** R3's `show ipv6 route static` showed the primary route via `2001:DB8:0:13::1` with distance 1, and the backup via `FE80::20B:BEFF:FE7D:4901` (R2's link-local) with distance 100.

---

## Serial Links with IPv6

Serial links don't need global IPv6 addresses. The screenshots showed:
```cisco
interface Serial0/0/0
 ipv6 enable
 ipv6 address autoconfig
```

`ipv6 address autoconfig` uses SLAAC to generate a link-local address. This is useful when you want a stable link-local for routing but don't want to consume global address space.

However, if the serial link also uses SLAAC for global addressing (RA from the other side), both ends can get global /128s. The screenshots showed R2's serial interfaces with `ipv6 address autoconfig` — this generates EUI-64 global addresses on the serial links.

For static route next-hops with no global address on the serial link, use the **link-local address**:
```cisco
ipv6 route 2001:DB8:0:3::/64 FE80::20B:BEFF:FE7D:4901
```

---

## Commands Practiced

```cisco
! Global IPv6 routing
ipv6 unicast-routing

! SLAAC autoconfig on interface
interface g0/0
 ipv6 enable
 ipv6 address autoconfig

! Static routes
ipv6 route <prefix/length> <next-hop> [AD]
ipv6 route <prefix/length> <outgoing-interface> [AD]

! SLAAC on PC (Packet Tracer)
Desktop → IP Configuration → IPv6 → Automatic

! Verification
show ipv6 route
show ipv6 route static
show ipv6 interface brief
show ipv6 protocols
```

---

## What I Learned

**SLAAC is IPv6's killer feature for hosts.** No DHCP server, no manual address entry. Router advertises prefix. PC generates its own address from its MAC. The screenshots showed PC1 with `2001:DB8:0:1::2` and PC2 with `2001:DB8:0:3::2` — both derived from RA prefixes.

**Backup paths need administrative distance.** Two static routes to the same prefix with the same AD = ECMP (load balancing). Different ADs = primary/backup. AD 1 is default. AD 100+ for backup.

**Serial links don't need global IPv6.** `ipv6 enable` gives you a link-local. That's enough for routing if you use link-local next-hops. The serial link R1–R2–R3 used link-local only, conserving global address space.

**Host routes (`/128`) are valid and useful.** R3 had a `/128` route to PC1 specifically. This gives the most precise path for traffic to that single host.

**R2 didn't need global IPv6 addresses anywhere.** All its interfaces were either serials with autoconfig or unused. R2's role was relay — passing traffic from R1 to R3 (or vice versa) using link-local next-hops on the serials.

---

## Lab Status

✅ Day 33 Complete

### Topics Covered

* SLAAC: router advertisements, PC self-configuration
* IPv6 static routes with global next-hop addresses
* IPv6 static routes with link-local next-hop addresses
* Administrative distance: primary vs backup paths
* Serial link IPv6 configuration (link-local only)
* Host routes (`/128`) for specific destination precision
* `show ipv6 route static` verification
* End-to-end IPv6 ping across 3 routers

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
