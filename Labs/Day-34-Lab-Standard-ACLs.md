# Day 34 — OSPF Routing with Standard ACLs: Policy Enforcement

## Overview

Today's lab was a two-phase network build: first establishing full OSPF connectivity across two routers and four shared subnets, then applying standard ACLs to enforce strict traffic policies. This is how production networks actually work — route everything, then decide what's allowed.

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-34-Lab-Standard-ACLs.png">
  </a>
</p>

---

## Lab Scenario

> "IPv6 addresses have been pre-configured on the routers. The serial connections use link-local addresses only."

Wait. Wrong memory. This lab is **IPv4, OSPF, and access lists.** No IPv6 here.

> "Configure OSPF on R1 and R2 to allow full connectivity between the PCs and servers."
> "Configure standard numbered ACLs on R1 and standard named ACLs on R2 to fulfill network policies."

Two routers, four subnets, two servers, and four host machines.

---

## Topology Summary

| Device | Role | Interface | IP Address | Subnet |
|--------|------|-----------|------------|--------|
| R1 | Router | G0/0 | 172.16.1.254 | 172.16.1.0/24 |
| R1 | Router | G0/1 | 172.16.2.254 | 172.16.2.0/24 |
| R1 | Router | S0/0/0 | 203.113.0.1 | 203.113.0.0/30 |
| R2 | Router | G0/0 | 192.168.1.254 | 192.168.1.0/24 |
| R2 | Router | G0/1 | 192.168.2.254 | 192.168.2.0/24 |
| R2 | Router | S0/0/0 | 203.113.0.2 | 203.113.0.0/30 |
| PC1 | Host | Fa0 | 172.16.1.1 | 172.16.1.0/24 |
| PC2 | Host | Fa0 | 172.16.1.2 | 172.16.1.0/24 |
| PC3 | Host | Fa0 | 172.16.2.1 | 172.16.2.0/24 |
| PC4 | Host | Fa0 | 172.16.2.2 | 172.16.2.0/24 |
| SRV1 | Server | Fa0 | 192.168.1.100 | 192.168.1.0/24 |
| SRV2 | Server | Fa0 | 192.168.2.100 | 192.168.2.0/24 |

---

## Phase 1: OSPF Routing

```cisco
! R1
router ospf 1
 router-id 1.1.1.1
 network 172.16.1.0 0.0.0.255 area 0
 network 172.16.2.0 0.0.0.255 area 0
 network 203.113.0.0 0.0.0.3 area 0
 passive-interface g0/0
 passive-interface g0/1
```

```cisco
! R2
router ospf 1
 router-id 2.2.2.2
 network 203.113.0.0 0.0.0.3 area 0
 network 192.168.1.0 0.0.0.255 area 0
 network 192.168.2.0 0.0.0.255 area 0
 passive-interface g0/0
 passive-interface g0/1
```

**Verification on R1:**
```cisco
R1#show ip protocols
```
```
Routing Protocol is "ospf 1"
  Router ID 1.1.1.1
  Networks:
    172.16.1.0 0.0.0.255 area 0
    172.16.2.0 0.0.0.255 area 0
    203.113.0.0 0.0.0.3 area 0
  Passive Interface(s):
    GigabitEthernet0/0
    GigabitEthernet0/1
```

**Verification on R2:**
```cisco
R2#show ip protocols
```
```
Routing Protocol is "ospf 1"
  Router ID 2.2.2.2
  Networks:
    203.113.0.0 0.0.0.3 area 0
    192.168.1.0 0.0.0.255 area 0
    192.168.2.0 0.0.0.255 area 0
  Routing Information Sources:
    Gateway         Distance      Last Update
    1.1.1.1              110       00:00:59
    2.2.2.2              110       00:00:47
```

**OSPF adjacency confirmed:**
```cisco
R2#show ip ospf neighbor
```
```
Neighbor ID  Pri   State       Dead Time   Address         Interface
1.1.1.1      0     FULL/       --          203.113.0.1     Serial0/0/0
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-34-Lab-Standard-ACLs-1.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-34-Lab-Standard-ACLs-1.2.png">
  </a>
</p>

---

## Phase 2: Standard ACLs on R1 (Numbered)

**Policy 1 — Only PC1 and PC3 can access 192.168.1.0/24 (SRV1):**
```cisco
access-list 3 permit 172.16.1.1    ! PC1
access-list 3 permit 172.16.2.1    ! PC3
access-list 3 deny any
```

Apply outbound on R1's serial link (traffic heading toward SRV1):
```cisco
interface s0/0/0
 ip access-group 3 out
```

**Policy 2 — 172.16.1.0/24 cannot access 172.16.2.0/24:**
```cisco
access-list 1 deny 172.16.1.0 0.0.0.255
access-list 1 permit any
```

Apply inbound on R1's G0/1 (entering the 172.16.2.0/24 segment):
```cisco
interface g0/1
 ip access-group 1 in
```

**Policy 3 — 172.16.2.0/24 cannot access 172.16.1.0/24:**
```cisco
access-list 2 deny 172.16.2.0 0.0.0.255
access-list 2 permit any
```

Apply inbound on R1's G0/0 (entering the 172.16.1.0/24 segment):
```cisco
interface g0/0
 ip access-group 2 in
```

**Verification on R1:**
```cisco
R1#show ip access-lists
```
```
Standard IP access list 1
    10 deny 172.16.2.0 0.0.0.255
    20 permit any
Standard IP access list 2
    10 deny 172.16.1.0 0.0.0.255
    20 permit any
Standard IP access list 3
    10 permit 172.16.1.1
    20 permit 172.16.2.1
    30 deny any
```

---

## Phase 3: Standard Named ACLs on R2

**Policy 4 — Hosts in 172.16.2.0/24 can't access 192.168.2.0/24 (SRV2):**
```cisco
ip access-list standard TENANT2-BLOCK
 deny 172.16.2.0 0.0.0.255
 permit any
```

Apply inbound on R2's G0/1 (entering the 192.168.2.0/24 segment):
```cisco
interface g0/1
 ip access-group TENANT2-BLOCK in
```

**Policy 5 — 172.16.1.0/24 can't access 172.16.2.0/24 (R2 enforces from WAN side):**
```cisco
ip access-list standard SEGMENT-ISO
 deny 172.16.1.0 0.0.0.255
 permit any
```

Apply inbound on R2's S0/0/0 (traffic arriving from R1):
```cisco
interface s0/0/0
 ip access-group SEGMENT-ISO in
```

**Verification on R2:**
```cisco
R2#show ip access-lists
```
```
Standard IP access list TENANT2-BLOCK
    10 deny 172.16.2.0 0.0.0.255
    20 permit any
Standard IP access list SEGMENT-ISO
    10 deny 172.16.1.0 0.0.0.255
    20 permit any
```
<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-34-Lab-Standard-ACLs-2.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-34-Lab-Standard-ACLs-2.2.png">
  </a>
</p>


---

## Traffic Flow and Policy Logic

| Source | Destination | Allowed? | Enforced At | ACL |
|--------|------------|----------|-------------|-----|
| PC1 (172.16.1.1) | SRV1 (192.168.1.100) | YES | R1 out S0/0/0 | ACL 3 permit |
| PC2 (172.16.1.2) | SRV1 (192.168.1.100) | NO | R1 out S0/0/0 | ACL 3 deny any |
| PC3 (172.16.2.1) | SRV1 (192.168.1.100) | YES | R1 out S0/0/0 | ACL 3 permit |
| PC4 (172.16.2.2) | SRV1 (192.168.1.100) | NO | R1 out S0/0/0 | ACL 3 deny any |
| 172.16.1.0/24 | 172.16.2.0/24 | NO | R1 in G0/0 | ACL 2 |
| 172.16.2.0/24 | 172.16.1.0/24 | NO | R1 in G0/1 | ACL 1 |
| 172.16.2.0/24 | SRV2 (192.168.2.100) | NO | R2 in G0/1 | TENANT2-BLOCK |

---

## Numbered vs Named ACLs

| Feature | Numbered Standard | Named Standard |
|---------|-------------------|----------------|
| Range | 1-99 | Up to 63 chars |
| Syntax | `access-list 1 deny 172.16.2.0 0.0.0.255` | `ip access-list standard NAME` |
| Sequence control | No (append-only) | Yes (numbered sequence) |
| Edit without delete | No | Yes (`no 10` removes line 10) |
| Functionally different? | No | No |

Both filter by **source IP only**. That's the standard ACL model. For source + destination + protocol filtering, you need **extended ACLs** (100-199 numbered, or named extended).

**Why standard ACLs here?** All four policies are source-based:
- "Only these hosts can reach..." → filter by source
- "This subnet cannot access that subnet" → filter by source at the target interface

Standard ACLs are perfect for this. Extended ACLs would be overkill.

---

## ACL Application Direction

| Interface | Direction | Why |
|-----------|-----------|-----|
| R1 G0/0 | inbound | Filter 172.16.1.0/24 traffic as it enters from the LAN |
| R1 G0/1 | inbound | Filter 172.16.2.0/24 traffic as it enters from the LAN |
| R1 S0/0/0 | outbound | Filter who can reach the server segment beyond R1 |
| R2 G0/1 | inbound | Filter 172.16.2.0/24 hosts before they reach SRV2 |
| R2 S0/0/0 | inbound | Filter 172.16.1.0/24 hosts crossing from R1 side |

**The golden rule:** Block traffic as close to the **source** as possible. This prevents it from traversing unnecessary links.

---

## Common ACL Mistakes

| Mistake | Why It Fails |
|---------|--------------|
| No `permit any` at the end | Implicit deny kicks in and blocks everything not explicitly denied |
| Apply ACL on WAN interface | May accidentally block OSPF hellos if direction is wrong |
| Wrong wildcard mask | `0.0.0.255` = /24. `0.0.0.0` = single host |
| Mix numbered and named on same ACL | Each number/name is a separate list |
| Apply extended ACL on R1 when standard suffices | Overcomplicated, harder to debug |

---

## Commands Practiced

```cisco
! Numbered standard ACLs
access-list 1 deny 172.16.2.0 0.0.0.255
access-list 1 permit any
interface g0/0
 ip access-group 1 in

! Named standard ACLs
ip access-list standard TENANT2-BLOCK
 deny 172.16.2.0 0.0.0.255
 permit any
interface g0/1
 ip access-group TENANT2-BLOCK in

! Multi-host permit
access-list 3 permit 172.16.1.1
access-list 3 permit 172.16.2.1
access-list 3 deny any

! OSPF verification
show ip protocols
show ip ospf neighbor
show ip route ospf

! ACL verification
show ip access-lists
```

---

## What I Learned

**Standard ACLs are blunt but effective.** They only see source IP. For policies that say "which subnet can reach where," that's exactly what you need. Extended ACLs add destination and protocol filters — useful for "only allow HTTP to this server" scenarios.

**Named ACLs are just numbered ACLs with a better name.** Same filter capability, same source-only limitation, but with sequence numbers and edit-in-place. For enterprise environments, named ACLs are preferred because you can insert rules without deleting the whole list.

**OSPF and ACLs can coexist.** The `passive-interface` command on LANs keeps OSPF hellos off the LAN wire entirely, so ACLs on LAN-facing interfaces never interfere with neighbor adjacencies.

**ACL placement is half the battle.** The same rule (deny 172.16.2.0/24) could be applied inbound on R1's G0/0 or outbound on R1's S0/0/0. Different placement = different effect. Inbound on the source LAN stops traffic at the source. Outbound on the WAN stops it before it leaves the building.

**Test early, test often.** `show ip access-lists` after every ACL. `ping` from each PC to verify the policy is working as intended before adding the next rule.

---

## Lab Status

✅ Day 34 Complete

### Topics Covered

* OSPF multi-router configuration with passive interfaces
* Standard numbered ACLs: syntax, wildcard masks, application
* Standard named ACLs: creation, sequence editing, application
* ACL direction: inbound vs outbound on multi-homed routers
* Four network policy enforcement cases
* OSPF adjacency verification with ACLs active
* `show ip access-lists` for ACL verification
* Source-only ACL limitation and when to use extended ACLs

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
