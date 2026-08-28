# Day 33 Lab Manual — IPv6 Static Routes, SLAAC, and Backup Paths

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure IPv6 static routing across a three-router network with two paths between endpoints, use SLAAC for host addressing, and implement a higher-administrative-distance backup route via a third router. |
| **Exam Relevance** | CCNA 200-301 — Domain 1: SLAAC/RA-based address autoconfiguration. Domain 4: IPv6 static routes (global and link-local next-hop), administrative distance, floating static routes for backup paths. |
| **Prerequisites** | Day 31 (dual-stack basics), Day 32 (EUI-64, link-local next-hops, static route syntax). |
| **Time Estimate** | 75–100 minutes. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — no new addressing math, but the three-router backup-path logic requires careful directional thinking. |

---

## 1. Lab Overview + Learning Objectives

This lab connects three routers (R1, R2, R3) where R1 and R3 have a **direct** link between them (the primary path) and R2 sits as an alternate, indirect path between them (the backup). PC hosts use **SLAAC** — the IPv6 mechanism that lets a host generate its own address automatically from router advertisements, with zero DHCP server needed — instead of manual or hand-derived addressing.

By the end of this lab you will be able to:

- Explain how SLAAC works end-to-end: Router Advertisement → prefix learned → host generates its own interface ID
- Configure IPv6 static routes for both a primary and a backup path using administrative distance
- Use link-local next-hops on serial WAN links that carry no global address
- Explain host routes (`/128`) and when they appear
- Verify which path is actually being used with `show ipv6 route static`

---

## 2. Business Context

**Why would a real company do this?**

- **"Our two main sites need a backup path if the primary WAN link goes down."** A single point-to-point link between two sites is a single point of failure. Routing traffic through a third site (even one that's otherwise unrelated to the primary traffic, like a regional hub) as a backup path is standard resilience design — exactly what R2 represents here.
- **"We can't afford a DHCPv6 server just to hand out addresses to a few dozen hosts per site."** SLAAC removes the operational burden of running and maintaining a DHCPv6 server for basic address assignment — the router itself, which already exists for routing, does the job via Router Advertisements. This is why so many IPv6 deployments default to SLAAC for host addressing rather than replicating the DHCP-everywhere model IPv4 required.
- **"We need the network to fail over automatically, not require someone to notice and manually reroute traffic."** Administrative distance-based backup static routes fail over automatically the instant the primary route's directly-connected interface goes down — no human intervention, no routing protocol convergence delay to wait on, because it's still just static routing underneath.

This is the natural next step after Day 32's two-router WAN link: a real company rarely has just two sites connected by a single link with no resilience story — this lab is "add a backup path" turned into a hands-on exercise.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-33%20Lab-IPv6-Static-Routes.png" alt="Day 33 IPv6 Static Routes Topology" width="900">
</p>

```text
PC1 -- R1 --------------- R3 -- PC2      (primary path: R1 G0/1 <-> R3 G0/1, direct)
        \                 /
         \--- R2 (backup)/               (R1 -- R2 -- R3 via serial links, link-local only)
```

---

## 4. IP Addressing Plan

| Device | Interface | Role | IPv6 Address |
|---|---|---|---|
| R1 | G0/0 | PC1 LAN | 2001:DB8:0:1::1/64 |
| R1 | G0/1 | Direct link to R3 (primary) | 2001:DB8:0:13::1/64 |
| R1 | S0/0/0 | Serial to R2 (backup) | link-local only |
| R2 | S0/0/0 | Serial to R1 | link-local only |
| R2 | S0/0/1 | Serial to R3 | link-local only |
| R3 | G0/0 | PC2 LAN | 2001:DB8:0:3::1/64 |
| R3 | G0/1 | Direct link to R1 (primary) | 2001:DB8:0:13::2/64 |
| R3 | S0/0/0 | Serial to R2 | link-local only |
| PC1 | Fa0 | Host | 2001:DB8:0:1::2/64 (via SLAAC) |
| PC2 | Fa0 | Host | 2001:DB8:0:3::2/64 (via SLAAC) |

### 4.1 SLAAC — how a host builds its own address with no DHCPv6 server

SLAAC (Stateless Address Autoconfiguration) is the mechanism that lets PC1 and PC2 obtain their addresses automatically:

1. The router (R1 for PC1, R3 for PC2) periodically sends **Router Advertisement (RA)** multicast messages out its LAN interface, to the all-nodes multicast address `FF02::1`.
2. The RA contains the router's `/64` prefix for that LAN (e.g., `2001:DB8:0:1::/64`) — but not a specific host address.
3. The host receiving the RA generates its own 64-bit interface identifier — historically via EUI-64 from its own MAC (the same algorithm from Day 32), though modern OSes often use a randomized "privacy" identifier instead for security reasons.
4. The host combines the learned prefix with its self-generated interface ID to form a complete, unique global address, and sets its default gateway to the RA's source address.

**The key structural point:** SLAAC is exactly the EUI-64 process from Day 32, just automated end-to-end — the router doesn't compute or assign the host's address at all, it only advertises the /64 prefix; the host does its own EUI-64 (or privacy-random) math locally. This is why SLAAC requires the LAN to be a /64: EUI-64 needs exactly 64 bits of host space, tying directly back to Day 31's explanation of why IPv6 LANs are never subnetted smaller.

**What SLAAC does NOT provide:** DNS server addresses. A network using pure SLAAC still needs either DHCPv6 (in "stateless" mode, providing only DNS info while SLAAC handles addressing) or router-advertised RDNSS options for hosts to learn DNS servers automatically.

### 4.2 Administrative distance and backup paths

| Route Type | Default AD | Role in this lab |
|---|---|---|
| Connected | 0 | Always preferred, never competes with static |
| Static (default) | 1 | Primary route — R1↔R3 direct link |
| Static (custom, higher) | 100 (chosen here) | Backup route — via R2 |

A router installs the **lowest** administrative-distance route to a given destination in its forwarding table. Two static routes to the same destination prefix with different AD values means: use the low-AD one always, and only fall back to the high-AD one if the low-AD route's next-hop/interface becomes unreachable. This is a **floating static route** — the same resilience pattern used in pure IPv4 networks, now applied to IPv6.

---

## 5. Pre-Configuration Checklist

1. Confirm `ipv6 unicast-routing` is enabled on all three routers.
2. Confirm serial interfaces are clocked correctly on the DCE side if using physical/simulated serial links (Packet Tracer default topologies usually pre-set this).
3. Have the primary-vs-backup path clearly sketched (Section 3) before writing any static route — direction confusion is the single biggest source of errors in this lab.

---

## 6. Configuration Tasks

### 6.1 Enable IPv6 routing on all three routers

```text
R1(config)#ipv6 unicast-routing
R2(config)#ipv6 unicast-routing
R3(config)#ipv6 unicast-routing
```

### 6.2 Configure LAN interfaces for SLAAC (R1 and R3)

```text
! R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ipv6 address 2001:DB8:0:1::1/64
R1(config-if)#ipv6 enable
R1(config-if)#exit

! R3
R3(config)#interface gigabitEthernet 0/0
R3(config-if)#ipv6 address 2001:DB8:0:3::1/64
R3(config-if)#ipv6 enable
R3(config-if)#exit
```

- Assigning a global address and enabling IPv6 on the interface is all that's required for the router to begin sending Router Advertisements — no separate "enable SLAAC" command exists on the router side, because RA transmission is implicit once the interface is IPv6-active. The host side (Section 6.3) is where SLAAC is explicitly selected.

### 6.3 Configure PC1 and PC2 for SLAAC

In Packet Tracer: Desktop → IP Configuration → IPv6 → select **Automatic (DHCP)** or the dedicated "Automatic" radio button that triggers SLAAC (not manual/static entry).

```text
PC1 IPv6: Automatic
PC2 IPv6: Automatic
```

- **What "Automatic" actually does:** the PC listens for the next RA on its link, extracts the advertised prefix, and computes its own interface ID — it does not contact any server.

### 6.4 Configure the direct primary link (R1 G0/1 ↔ R3 G0/1)

```text
! R1
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#ipv6 address 2001:DB8:0:13::1/64
R1(config-if)#ipv6 enable
R1(config-if)#exit

! R3
R3(config)#interface gigabitEthernet 0/1
R3(config-if)#ipv6 address 2001:DB8:0:13::2/64
R3(config-if)#ipv6 enable
R3(config-if)#exit
```

### 6.5 Configure the serial (backup path) interfaces as link-local only

```text
! R1
R1(config)#interface serial0/0/0
R1(config-if)#ipv6 enable
R1(config-if)#no shutdown
R1(config-if)#exit

! R2 (both serials)
R2(config)#interface serial0/0/0
R2(config-if)#ipv6 enable
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface serial0/0/1
R2(config-if)#ipv6 enable
R2(config-if)#no shutdown
R2(config-if)#exit

! R3
R3(config)#interface serial0/0/0
R3(config-if)#ipv6 enable
R3(config-if)#no shutdown
R3(config-if)#exit
```

- Same reasoning as Day 32's WAN link: this is a two-device serial segment that never needs to be reached by its own address, so link-local is sufficient.

### 6.6 Read back each router's actual serial link-local addresses

```text
R1#show ipv6 interface brief
R2#show ipv6 interface brief
R3#show ipv6 interface brief
```
Note R1's S0/0/0 link-local, R2's S0/0/0 and S0/0/1 link-locals, and R3's S0/0/0 link-local — you need all of these for Step 6.7.

### 6.7 Configure static routes — primary (direct) and backup (via R2)

```text
! R1 — primary route to PC2's LAN, via R3's direct-link global address (AD 1, default)
R1(config)#ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:13::2

! R1 — backup route to PC2's LAN, via R2's serial link-local, AD 100
R1(config)#ipv6 route 2001:DB8:0:3::/64 FE80::<R2-S0/0/0-link-local> 100

! R3 — primary route to PC1's LAN, via R1's direct-link global address (AD 1, default)
R3(config)#ipv6 route 2001:DB8:0:1::/64 2001:DB8:0:13::1

! R3 — backup route to PC1's LAN, via R2's serial link-local, AD 100
R3(config)#ipv6 route 2001:DB8:0:1::/64 FE80::<R2-S0/0/0-toward-R3-link-local> 100
```

- **Note the asymmetry:** R1's backup route references R2's *S0/0/0* (the interface facing R1), while R3's backup route references R2's *S0/0/1* (the interface facing R3) — R2 has a distinct link-local address on each serial interface, so you must reference the correct one for each direction.

### 6.8 Configure R2's static routes (the relay/backup router)

R2 has no LAN of its own — it exists purely to relay traffic between R1 and R3 when the primary path is down.

```text
! R2 — route to PC1's LAN, out the interface facing R1
R2(config)#ipv6 route 2001:DB8:0:1::/64 Serial0/0/0

! R2 — route to PC2's LAN, out the interface facing R3
R2(config)#ipv6 route 2001:DB8:0:3::/64 Serial0/0/1
```

- **Why an outgoing-interface-only route (no next-hop address) works here:** on a genuinely point-to-point serial link, specifying just the exit interface is enough — there's only one possible neighbor on the other end, so IOS doesn't need an explicit next-hop address to resolve where the packet goes next. This is different from the multi-access Ethernet links elsewhere in this lab, where an interface-only route would be ambiguous.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ipv6 interface brief` | LAN interfaces have global + link-local; serials have link-local only |
| `show ipv6 route` | Primary static route shows `[1/0]`; backup shows `[100/0]` and normally is NOT installed in the forwarding table while the primary is up |
| `show ipv6 route static` | Explicitly lists both static routes per destination with their distances |
| PC `ipconfig` | Confirms SLAAC-derived address and gateway |
| `show ipv6 route 2001:DB8:0:3::/64` | Shows exactly which route (primary or backup) is currently active |

### 7.1 Expected Output Gallery

**`PC1> ipconfig`**
```text
FastEthernet0 Connection:

Link-local IPv6 Address...: FE80::2D0:97FF:FE12:71A1
IPv6 Address...............: 2001:DB8:0:1:2D0:97FF:FE12:71A1
Default Gateway............: 2001:DB8:0:1::1
```
Notice PC1's global address is much longer than the router's hand-typed `::2` style — this is the actual EUI-64-derived value from PC1's own MAC, generated automatically by SLAAC, not a value anyone typed in.

**`R1# show ipv6 route static`**
```text
IPv6 Routing Table - default - 9 entries
S   2001:DB8:0:3::/64 [1/0]
     via 2001:DB8:0:13::2
S   2001:DB8:0:3::/64 [100/0]
     via FE80::201:63FF:FE80:B801, Serial0/0/0
```
Both routes are listed by `show ipv6 route static`, but only the `[1/0]` entry is actually used for forwarding while the primary link is up — `show ipv6 route 2001:DB8:0:3::/64` (without `static`) will show only the active one.

**`PC1> ping 2001:DB8:0:3::2`** (or the SLAAC-derived long form of PC2's address)
```text
Pinging 2001:DB8:0:3::2 with 32 bytes of data:
Reply from 2001:DB8:0:3::2: bytes=32 time=1ms TTL=254
Reply from 2001:DB8:0:3::2: bytes=32 time=1ms TTL=254
Reply from 2001:DB8:0:3::2: bytes=32 time=1ms TTL=254
Reply from 2001:DB8:0:3::2: bytes=32 time=1ms TTL=254

Ping statistics: Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

---

## 8. Common Mistakes (the 80/20)

1. **Configuring the backup route with the same AD as the primary (or forgetting the AD parameter entirely).** Without specifying `100` (or any value higher than 1) on the backup route, both routes have AD 1 and the router load-balances between them (ECMP) instead of treating one as a strict backup — breaking the "backup only" requirement.
2. **Using the wrong R2 serial interface's link-local for R1's vs R3's backup route.** R2 has two distinct link-local addresses (one per serial interface) — mixing them up means the backup route points nowhere useful.
3. **Forgetting R2 needs static routes too.** R2 isn't just a wire — it's a router that needs to be explicitly told how to reach both LANs, or it will silently drop backup-path traffic even though the interfaces are all up.
4. **Not testing the backup path at all.** It's easy to verify only the primary path works and assume the backup is fine — always shut down the primary link and confirm traffic actually reroutes through R2 before considering the lab complete.
5. **Assuming SLAAC gives PC1 a short, predictable address like `::2`.** SLAAC-derived addresses are the full EUI-64 (or privacy-random) form based on the PC's actual MAC — expect a long address, not a hand-typed-looking one, and don't be alarmed when it doesn't match a "clean" pattern.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC has no IPv6 address at all | Router's LAN interface not IPv6-enabled, so no RAs are being sent | `show ipv6 interface g0/0` on the router | Confirm `ipv6 address`/`ipv6 enable` applied; interface `no shutdown` |
| 2 | PC1 can't ping PC2 even though primary link is up | Static route missing or wrong next-hop on R1 or R3 | `show ipv6 route static` on both | Correct the static route |
| 3 | Backup path doesn't work when primary is shut down | R2 missing a static route for one or both LANs | `show ipv6 route static` on R2 | Add the missing route |
| 4 | Backup route always active even when primary is up (unexpected load-balancing) | Backup route's AD matches the primary's (both defaulted to 1) | `show ipv6 route static` — check `[x/0]` values | Re-enter the backup route with an explicit higher AD |
| 5 | R1's backup route references the wrong R2 interface | Copy-paste of R2's other serial link-local | Compare against `show ipv6 interface brief` on R2 | Re-enter with the correct interface's link-local |

---

## 10. Design Analysis

- **Why a floating static route instead of a dynamic routing protocol for automatic failover?** At three routers with a simple primary/backup shape, a dynamic protocol's convergence machinery (neighbor relationships, LSA/update flooding) is overkill — administrative-distance-based static failover achieves the same practical outcome (automatic reroute on primary link failure) with none of the added complexity, consistent with the same reasoning used in Day 1 and Day 32.
- **Why SLAAC instead of manually typing PC addresses, given this course otherwise emphasizes hand-deriving addresses?** Day 32 deliberately taught EUI-64 by hand so you'd understand the mechanism; this lab deliberately automates it via SLAAC to show the mechanism's real-world application — a network engineer configures the router side (prefix, RA), not each individual host's address, at any meaningful scale.
- **Why give the backup route AD 100 specifically, not some other value?** Any value greater than 1 (the default static AD) and less than a dynamic routing protocol's typical AD (110 for OSPF) works structurally — 100 is a conventional, memorable choice used throughout Cisco documentation for "floating static, definitely not primary, but still preferred over most dynamic protocols if one were later added."

---

## 11. Real-World Parallel

**You'd see this when...**

- ...two data centers or branch offices have a direct fiber/leased-line connection as their primary path and a secondary path through a regional carrier hub or a different provider — exactly R1↔R3 direct, with R2 as the indirect backup.
- ...a new employee's laptop gets an IPv6 address the instant it joins the corporate Wi-Fi, with no visible "DHCP request" step for IPv6 the way there is for IPv4 — that's SLAAC working silently in the background.
- ...an ops team runs a planned maintenance window, shutting down a primary WAN link, and traffic reroutes automatically without a ticket or manual intervention — the value floating static routes (or their dynamic-protocol equivalents) deliver in production.

---

## 12. Stretch Goal

1. Shut down the R1↔R3 direct link and confirm, via `show ipv6 route` (not `static`), that the backup route via R2 is now the active one — then bring the primary back up and confirm it reverts automatically.
2. Add a second PC to one of the LANs and confirm it also receives a SLAAC address from the same RA, with a different (but same-prefix) interface ID.
3. Investigate what a host route (`/128`) is, find one in your own `show ipv6 route` output (Cisco IOS often installs one alongside the connected LAN route), and explain what specific purpose it serves versus the `/64` route for the same LAN.

---

## 13. Self-Assessment

- [ ] Can you explain SLAAC end-to-end, including exactly what information the router provides and what the host computes itself?
- [ ] Can you explain why SLAAC requires a /64 prefix, tying back to the EUI-64 mechanism from Day 32?
- [ ] Can you write both a primary and backup IPv6 static route from memory, including the AD syntax?
- [ ] Can you explain why R2 needs its own static routes even though it's "just" the backup path?
- [ ] Could you predict, without testing, what `show ipv6 route` (not `static`) would show while the primary link is down?

---

## 14. Key Concepts Demonstrated

- SLAAC: Router Advertisements, prefix learning, host-side EUI-64/privacy address generation
- IPv6 static routing: global and link-local next-hops
- Administrative distance and floating static routes for automatic backup paths
- Multi-router IPv6 topology with primary/backup path design

## 15. What I Learned

SLAAC is the automated, production-scale version of the exact EUI-64 mechanism hand-derived in Day 32 — the router's only job is advertising a /64 prefix, and the host does the rest locally, with no server round-trip required. Administrative distance turns two static routes to the same destination into an automatic primary/backup pair with zero extra logic — the router already knows to prefer the lower-AD route and fail over the instant it becomes unreachable. The router acting purely as a backup relay (R2) still needs its own explicit routing configuration; being "in the middle" of a topology diagram doesn't mean a router routes correctly by default.

## 16. Skills Practiced

- SLAAC configuration and verification (router and host side)
- Multi-router IPv6 static routing with primary/backup paths
- Administrative distance manipulation for floating static routes
- Link-local next-hop routing on point-to-point serial links

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Original device | GNS3 image |
|---|---|---|
| Routers (R1, R2, R3) | Cisco router | VyOS |
| PCs (PC1, PC2) | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for VyOS's SLAAC/RA and floating static route equivalents.
