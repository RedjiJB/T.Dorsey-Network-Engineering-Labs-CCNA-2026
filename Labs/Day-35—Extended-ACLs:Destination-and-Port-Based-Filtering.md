# Day 35 — Extended ACLs: Destination and Port-Based Filtering

## Overview

Today's lab stepped up from **standard ACLs** (source IP only) to **extended ACLs** (source IP + destination IP + protocol/port). The policies required blocking specific hosts from specific servers' services — DNS on SRV1, HTTP/HTTPS on SRV2 — and blocking one entire subnet from reaching a single host (PC1).

Extended ACLs are where Cisco access lists become surgical. Standard ACLs say "this subnet can't go there." Extended ACLs say "this subnet can't use *this protocol* to reach *this server*."

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs.png">
  </a>
</p>

---

## Lab Scenario

> "Configure extended ACLs to fulfill the following network policies:"
> - Hosts in 172.16.2.0/24 can't communicate with PC1.
> - Hosts in 172.16.1.0/24 can't access the DNS service on SRV1.
> - Hosts in 172.16.2.0/24 can't access the HTTP or HTTPS services on SRV2.

Same topology as Day 34 (OSPF assumed running). New requirement: filter by **destination** and **service/port**, not just source.

---

## Topology Summary

| Device | Role | Interface | IP Address | Subnet |
|--------|------|-----------|------------|--------|
| R1 | Router | G0/0 | 172.16.1.254 | 172.16.1.0/24 |
| R1 | Router | G0/1 | 172.16.2.254 | 172.16.2.0/24 |
| R1 | Router | S0/0/0 | 203.0.113.1 | 203.0.113.0/30 |
| R2 | Router | S0/0/0 | 203.0.113.2 | 203.0.113.0/30 |
| R2 | Router | G0/0 | 192.168.1.254 | 192.168.1.0/24 |
| R2 | Router | G0/1 | 192.168.2.254 | 192.168.2.0/24 |
| PC1 | Host | Fa0 | 172.16.1.1 | 172.16.1.0/24 |
| PC2 | Host | Fa0 | 172.16.1.2 | 172.16.1.0/24 |
| PC3 | Host | Fa0 | 172.16.2.1 | 172.16.2.0/24 |
| PC4 | Host | Fa0 | 172.16.2.2 | 172.16.2.0/24 |
| SRV1 | Server | Fa0 | 192.168.1.100 | 192.168.1.0/24 (DNS) |
| SRV2 | Server | Fa0 | 192.168.2.100 | 192.168.2.0/24 (web) |

---

## Lab Questions and Solutions

**1. Configure extended ACLs to fulfill the following network policies.**

### Policy A: Hosts in 172.16.2.0/24 can't communicate with PC1

This blocks all IP traffic from LAN 2 (PC3, PC4) to PC1 (172.16.1.1). PC1's traffic to LAN 2 is NOT blocked.

**Why extended ACL and not standard?** Standard ACLs filter by source only. If we used ACL 1 deny 172.16.2.0 inbound on G0/1, that would also block PC3/PC4 from reaching anything R1 routes — including SRV1. We only want to block them from PC1 specifically, so destination matters.

```cisco
R1(config)#ip access-list extended block_pc1
R1(config-ext-nacl)# deny ip 172.16.2.0 0.0.0.255 host 172.16.1.1
R1(config-ext-nacl)# permit ip any any
```

Apply inbound on R1's G0/0 (PC1's LAN):
```cisco
R1(config)#interface g0/0
R1(config-if)#ip access-group block_pc1 in
```

**Verification:**
```cisco
R1#show ip access-lists block_pc1
```
```
Extended IP access list block_pc1
    10 deny ip 172.16.2.0 0.0.0.255 host 172.16.1.1
    20 permit ip any any
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.1-1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.1-2.png">
  </a>
</p>

---

### Policy B: Hosts in 172.16.1.0/24 can't access the DNS service on SRV1

SRV1 is the DNS server at 192.168.1.100. We only want to block DNS (UDP port 53, `domain`). HTTP, HTTPS, SSH — all other services — still work.

**Why extended ACL?** Destination matters (SRV1's specific IP) AND protocol/port matters (DNS = UDP port 53).

```cisco
R1(config)#ip access-list extended block_DNS_SRV1
R1(config-ext-nacl)# deny udp 172.16.1.0 0.0.0.255 host 192.168.1.100 eq domain
R1(config-ext-nacl)# permit ip any any
```

**Protocol note:** DNS uses:
- **UDP port 53** for standard queries (most common)
- **TCP port 53** for zone transfers and large responses

For this lab, UDP was sufficient. In production, add `deny tcp ... eq domain` too if you want to fully block DNS.

Apply inbound on R1's G0/0:
```cisco
R1(config)#interface g0/0
R1(config-if)#ip access-group block_DNS_SRV1 in
```

**Verification:**
```cisco
R1#show ip interface g0/0
```
```
Inbound access list is Block_DNS_SRV1
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
   <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.2-1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.2-2.png">
  </a>
</p>

---

### Policy C: Hosts in 172.16.2.0/24 can't access HTTP or HTTPS services on SRV2

SRV2 is the web server at 192.168.2.100. Block TCP port 80 (HTTP, `www`) and TCP port 443 (HTTPS). All other services still available.

```cisco
R1(config)#ip access-list extended Block_HTTP_HTTPS_SRV2
R1(config-ext-nacl)# deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www
R1(config-ext-nacl)# deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443
R1(config-ext-nacl)# permit ip any any
```

Apply inbound on R1's G0/1:
```cisco
R1(config)#interface g0/1
R1(config-if)#ip access-group Block_HTTP_HTTPS_SRV2 in
```

**Verification:**
```cisco
R1#show ip access-lists Block_HTTP_HTTPS_SRV2
```
```
Extended IP access list Block_HTTP_HTTPS_SRV2
    10 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www
    20 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443
    30 permit ip any any
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.3-1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.3-2.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs-1.3-3.png">
  </a>
</p>

---

## Standard ACLs vs Extended ACLs

| Feature | Standard | Extended |
|---------|----------|----------|
| Source IP | Yes | Yes |
| Destination IP | No | Yes |
| Protocol | No | Yes (TCP, UDP, ICMP, IP) |
| Port numbers | No | Yes |
| Range | 1-99, 1300-1999 | 100-199, 2000-2699 |
| Named mode | Yes | Yes |
| Best for | Simple source filtering | Granular service filtering |
| Use case | "Block this subnet" | "Block this subnet from accessing port 80 on this server" |

**When to use which:**
- **Standard:** Simple inter-subnet filtering, blocking entire subnets from each other
- **Extended:** Service/port-specific policies, web filtering, application control

**The key insight:** Standard ACLs are a hammer. Extended ACLs are a scalpel.

---

## Extended ACL Syntax

```cisco
! Named extended ACL
ip access-list extended ACL_NAME
    <seq> deny|permit <protocol> <source> <wildcard> [port operator port]
    <seq> deny|permit <protocol> <source> <wildcard> <destination> <wildcard> [port operator port]
    <seq> deny|permit ip any any

! Numbered extended ACL
access-list <100-199> {deny|permit} <protocol> <source> <wildcard> [port] <dest> <wildcard> [port]

! Apply
interface g0/0
 ip access-group ACL_NAME in
```

---

## Port and Protocol Reference

| Service | Protocol | Port | ACL Keyword |
|---------|----------|------|-------------|
| HTTP | TCP | 80 | `eq www` or `eq 80` |
| HTTPS | TCP | 443 | `eq 443` |
| DNS | UDP | 53 | `eq domain` |
| DNS | TCP | 53 | `eq domain` |
| SSH | TCP | 22 | `eq 22` |
| Telnet | TCP | 23 | `eq 23` |
| ICMP (ping) | ICMP | N/A | `icmp` |
| Any/all | IP | N/A | `ip` |

**Port operators:**
- `eq <port>` — equal to
- `gt <port>` — greater than
- `lt <port>` — less than
- `neq <port>` — not equal to
- `range <low> <high>` — port range

---

## Named ACLs vs Numbered Extended ACLs

Named extended ACLs (`ip access-list extended`) support sequence numbers and inline editing. Numbered extended ACLs (`access-list 100`) are append-only.

```cisco
! Named — can insert at line 15 without deleting anything
ip access-list extended WEB-FILTER
  5 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 80
  10 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443
  15 permit ip any any

! Edit without delete
no 5
5 deny tcp 172.16.2.0 0.0.0.255 any eq 80

! Numbered — can't edit middle without full delete/recreate
access-list 100 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 80
access-list 100 deny tcp ...
```

---

## Director Matches and Keywords

| Syntax | Meaning |
|--------|---------|
| `host 172.16.1.1` | Single host = `172.16.1.1 0.0.0.0` |
| `172.16.1.0 0.0.0.255` | Entire /24 subnet |
| `any` | `0.0.0.0 0.0.0.0` (matches all) |
| `host <ip>` | Use when filtering specific servers/PCs |
| `<subnet> <wildcard>` | Use when filtering entire ranges |
| `eq 80` | Exactly port 80 |
| `eq www` | Exactly port 80 (alias) |
| `eq 443` | Exactly port 443 |
| `eq domain` | Exactly port 53 (DNS) |

---

## ACL Placement Strategy for Extended ACLs

Because extended ACLs filter by source AND destination, you have more flexibility in placement. The golden rule still applies: block as close to the **source** as possible.

| ACL | Source | Destination/Service | Interface | Direction | Why |
|------|--------|---------------------|-----------|-----------|-----|
| block_pc1 | 172.16.2.0/24 | PC1 (172.16.1.1) | R1 G0/0 | in | Block LAN 2 at PC1's LAN door |
| block_DNS_SRV1 | 172.16.1.0/24 | SRV1:53 (UDP) | R1 G0/0 | in | Block DNS at R1 before WAN traversal |
| Block_HTTP_HTTPS_SRV2 | 172.16.2.0/24 | SRV2:80,443 (TCP) | R1 G0/1 | in | Block web at R1 before WAN traversal |

All three applied inbound on R1's LAN-facing interfaces. This means the bad traffic is stopped before it leaves the local segment.

---

## Verification Steps

```cisco
! View all ACLs
show ip access-lists

! Check interface ACL bindings
show ip interface g0/0
show ip interface g0/1

! Test allowed flow
PC1>ping 192.168.1.100
! Should succeed (PC1 isn't blocked from SRV1, only blocked from DNS)

PC2>ping 172.16.1.1
! Should succeed (block_pc1 only blocks 172.16.2.0/24, not 172.16.1.0/24)

PC3>ping 172.16.1.1
! Should FAIL (block_pc1 denies 172.16.2.0/24)

! Test service-level filter
PC2>ping 192.168.1.100
! Should succeed (ICMP is not blocked by block_DNS_SRV1)

PC2>nslookup 192.168.1.100
! Should FAIL (UDP 53 blocked by block_DNS_SRV1)

PC3>ping 192.168.2.100
! Should succeed (TCP 80/443 blocked, but ICMP still allowed by permit ip any any)

PC4>ping 192.168.2.100
! Should succeed (same — allow other services)
```

---

## Common Extended ACL Mistakes

| Mistake | Result |
|---------|--------|
| Using standard ACL when extended needed | Filters by source only, misses destination/port |
| Forgetting `permit ip any any` at end | Implicit deny blocks everything not explicitly matched |
| Wrong port keyword | `eq http` isn't a valid keyword; use `eq www` or `eq 80` |
| Applying inbound instead of outbound | ACL might not see traffic if direction is wrong |
| Using TCP filter for DNS without UDP | DNS can fall back to TCP on large transfers |
| Placing extended ACL on R2 for R1-source traffic | Must be placed close to source (R1) to be effective |
| Typo in ACL name | `Bock_HTTP_HTTPS_SRV2` typo in screenshot — avoid in production |

---

## Commands Practiced

```cisco
! Named extended ACL
ip access-list extended block_pc1
 deny ip 172.16.2.0 0.0.0.255 host 172.16.1.1
 permit ip any any

! Service-specific deny (DNS/UDP)
ip access-list extended block_DNS_SRV1
 deny udp 172.16.1.0 0.0.0.255 host 192.168.1.100 eq domain
 permit ip any any

! Multi-port deny (HTTP + HTTPS)
ip access-list extended Block_HTTP_HTTPS_SRV2
 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www
 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443
 permit ip any any

! Apply inbound on interface
interface g0/0
 ip access-group block_DNS_SRV1 in

interface g0/1
 ip access-group block_pc1 in
 ip access-group Block_HTTP_HTTPS_SRV2 in

! Verify
show ip access-lists
show ip access-lists block_pc1
show ip interface g0/0
show ip interface g0/1
```

---

## What I Learned

**Extended ACLs are the upgrade I didn't know I needed.** Standard ACLs can block entire subnets. Extended ACLs can block specific services on specific servers while leaving everything else alone. That's the difference between "LAN 2 can't talk to SRV1 at all" and "LAN 2 can reach SRV1 for everything except DNS."

**Destination matters.** In Policy A, I only wanted to block LAN 2 from PC1 — not from everything else R1 routes. Without destination filtering, a standard ACL would have been a blunt hammer that also blocked PC3/PC4 from reaching SRV1 on R2.

**Protocol + port = surgical filtering.** `deny udp ... eq domain` only blocks DNS. ICMP ping, SSH, HTTP all still work. `deny tcp ... eq www` only blocks HTTP. HTTPS (443) needs its own line. Named ACLs let me stack these rules cleanly.

**Named ACLs with meaningful names read like policy.** `block_DNS_SRV1` and `Block_HTTP_HTTPS_SRV2` tell you exactly what they do when you see them in `show ip access-lists`. Numbered lists 101-103 would require documentation.

**Placement logic for ACLs is identical regardless of type.** Always inbound on the LAN-facing interface closest to the source. The fact that extended ACLs can filter by destination makes them more flexible but doesn't change WHERE they should go.

---

## Lab Status

✅ Day 35 Complete

### Topics Covered

* Extended ACLs vs standard ACLs: source + destination + protocol filtering
* Named extended ACLs: `block_pc1`, `block_DNS_SRV1`, `Block_HTTP_HTTPS_SRV2`
* Protocol-specific filtering: UDP port 53 (DNS), TCP port 80/443 (HTTP/HTTPS)
* Port operators: `eq`, `host`
* ACL application on R1 LAN interfaces (inbound)
* `show ip access-lists` verification on specific named ACLs
* `show ip interface` to verify ACL bindings on interfaces
* Extended vs standard ACL placement logic
* Extended named ACL editing with sequence numbers
* ICMP fall-through behavior with `permit ip any any`

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
