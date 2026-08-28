# Day 45 Lab Manual — Dynamic NAT & PAT

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure Dynamic NAT with a limited address pool, observe pool exhaustion, then replace it with PAT (NAT Overload) and prove it scales past the pool limitation |
| CCNA 200-301 Domains | 4.0 IP Services (NAT — dynamic, PAT/overload, pool exhaustion), 1.0 Network Fundamentals (ACLs as NAT match criteria) |
| Prerequisites | Day 44 Static NAT concepts, standard ACL syntax, interface addressing |
| Estimated Time | 60–75 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

This lab directly demonstrates the scalability problem with Dynamic NAT — a small pool of public addresses runs out — and then fixes it with PAT (Port Address Translation, also called NAT Overload), which lets unlimited internal hosts share one public address using port numbers to keep sessions distinct. This is the single most common form of NAT in the real world; nearly every home router and small-business firewall runs PAT by default.

By the end of this lab you will be able to:

1. Configure Dynamic NAT using a standard ACL and an address pool.
2. Explain and demonstrate pool exhaustion — why a third host fails to get translated when the pool has only two addresses.
3. Cleanly remove a Dynamic NAT configuration before replacing it with a different NAT strategy.
4. Configure PAT (`overload`) using an interface's own address instead of a pool.
5. Explain, using inside-local/inside-global/outside-local/outside-global terminology, exactly how PAT differs from Dynamic NAT and Static NAT.
6. Justify why PAT scales dramatically better than Dynamic NAT for general internet access.

## 2. Business Context

No company buys one public IP address per employee laptop — that would be enormously wasteful and, for most organizations, isn't even possible given IPv4 address scarcity. Instead, PAT lets hundreds or thousands of internal devices share a small number of public addresses (often just one) for general outbound internet access, using port numbers as the "who is this" identifier. This lab first shows *why* Dynamic NAT alone can't do this at scale (finite pool), then shows the actual production-realistic solution.

## 3. Topology Reference

| Device | Address |
|---|---|
| PC1 | 172.16.0.1/24 |
| PC2 | 172.16.0.2/24 |
| PC3 | 172.16.0.3/24 |
| R1 G0/1 (inside) | 172.16.0.254/24 |
| R1 G0/0 (outside) | 203.0.113.1/30 |
| Internet Router | 203.0.113.2/30 |
| Server | 8.8.8.8 |
| NAT Pool | 100.0.0.1 – 100.0.0.2 |

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT.png`

## 4. IP Addressing Plan — With Full NAT Terminology

### 4.1 Why Sized This Way

Same private/documentation-range pattern as Day 44: `172.16.0.0/24` (RFC 1918 private) inside, `203.0.113.0/30` (documentation range standing in for a real WAN link) outside. The NAT pool is **deliberately undersized** (only 2 addresses for 3 hosts) — this isn't a mistake, it's the whole point of the lab, designed to force pool exhaustion so you can observe the failure mode firsthand.

### 4.2 Manual Calculation Walkthrough

```
172.16.0.0/24 → 255.255.255.0 → 254 usable hosts
203.0.113.0/30 → 255.255.255.252 → 2 usable hosts

NAT Pool: 100.0.0.1 - 100.0.0.2 → 2 addresses, manually defined range
(not a subnet calculation — this is an explicit start/end address pool,
independent of the /24 mask used in the pool statement's netmask argument,
which only describes the pool addresses' own subnet context)
```

### 4.3 NAT Terminology, Applied to This Lab

| Term | Meaning | Dynamic NAT Example | PAT Example |
|---|---|---|---|
| Inside local | Real address of the inside host | 172.16.0.1 | 172.16.0.1 |
| Inside global | Address representing the host externally | 100.0.0.1 (from the pool) | 203.0.113.1 (R1's own outside interface, shared) |
| Outside local | Outside host's address as seen from inside | 8.8.8.8 | 8.8.8.8 |
| Outside global | Outside host's real address | 8.8.8.8 | 8.8.8.8 |

The critical difference: under Dynamic NAT, each inside host gets its **own** inside global address from the pool (one-to-one, pool-limited). Under PAT, **all** inside hosts share the **same** inside global address (R1's outside interface) — many-to-one — distinguished instead by source port number.

## 5. Pre-Configuration Checklist

- [ ] Confirm the ACL you'll use to match "inside traffic" covers the entire `172.16.0.0/24` range, not a subset
- [ ] Know the exact NAT pool boundaries (`100.0.0.1`–`100.0.0.2`) before configuring, and deliberately note it's smaller than the number of hosts
- [ ] Plan to `clear ip nat translation *` before switching from Dynamic NAT to PAT — stale entries can cause confusing verification results otherwise
- [ ] Remove the old `ip nat inside source list ... pool ...` statement explicitly before adding the PAT statement — don't just add PAT on top

## 6. Configuration Tasks

### 6.1 Inside/outside interfaces (same pattern as Day 44)

```
R1(config)# interface g0/1
R1(config-if)# ip nat inside
R1(config)# interface g0/0
R1(config-if)# ip nat outside
```

### 6.2 Match the inside network with a standard ACL

```
R1(config)# access-list 1 permit 172.16.0.0 0.0.0.255
```
Mode: global config. Unlike Static NAT (Day 44), Dynamic NAT and PAT both need a way to say "which inside traffic is eligible for translation" — a standard ACL is the classic mechanism. Memory aid: "the ACL here isn't filtering traffic, it's *selecting* which sources NAT should even consider."

### 6.3 Create the Dynamic NAT pool

```
R1(config)# ip nat pool POOL1 100.0.0.1 100.0.0.2 netmask 255.255.255.0
```
Defines the finite set of inside-global addresses available for translation — exactly two in this lab, intentionally fewer than the number of inside hosts.

### 6.4 Bind the ACL to the pool (enable Dynamic NAT)

```
R1(config)# ip nat inside source list 1 pool POOL1
```
This is the command that actually activates Dynamic NAT: traffic matching ACL 1, sourced from the inside, gets translated using an address pulled from POOL1 — first-come, first-served.

### 6.5 Observe pool exhaustion

Generate traffic from PC1, then PC2 — both succeed, consuming both pool addresses (`172.16.0.1→100.0.0.1`, `172.16.0.2→100.0.0.2`). Then generate traffic from PC3 — **it fails**, because no pool address remains. This is Dynamic NAT's core limitation: it's still fundamentally one-to-one, just with automatic address assignment instead of manual static mapping. Memory aid: "Dynamic NAT automates *which* address you get, not *how many* are available."

### 6.6 Clean removal before switching to PAT

```
R1# clear ip nat translation *
R1(config)# no ip nat inside source list 1 pool POOL1
```
The ACL and inside/outside interface designations are reusable — only the pool-binding statement needs to be removed. Memory aid: "clear the table before you change the rules, so old entries don't confuse your next `show` command."

### 6.7 Configure PAT (NAT Overload)

```
R1(config)# ip nat inside source list 1 interface GigabitEthernet0/0 overload
```
Instead of a pool, this reuses R1's own outside interface address (`203.0.113.1`) as the single inside-global address for **all** matching inside hosts. The `overload` keyword is what enables port-based multiplexing — without it, this command would behave like a one-address Dynamic NAT pool and still exhaust after one host. Memory aid: "overload = the address gets 'overloaded' with many simultaneous sessions, told apart by port number."

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show ip nat translations` | R1 | View active mappings — compare pool-based vs. interface-based entries |
| `show ip nat statistics` | R1 | Confirm translation counts and NAT type in use |
| `ping google.com` (or equivalent) | PC1, PC2, PC3 | Functional test — before/after the PAT switch |
| `clear ip nat translation *` then re-check | R1 | Confirm no stale entries linger across the config change |

### Expected Output Gallery — Dynamic NAT (pool exhausted)

```
R1# show ip nat translations
Pro  Inside global   Inside local    Outside local   Outside global
icmp 100.0.0.1:1     172.16.0.1:1    8.8.8.8:1       8.8.8.8:1
icmp 100.0.0.2:1     172.16.0.2:1    8.8.8.8:1       8.8.8.8:1
```
PC3's ping shows "Request timed out" — no third pool address is available.

### Expected Output Gallery — PAT (all three succeed)

```
R1# show ip nat translations
Pro  Inside global      Inside local     Outside local   Outside global
icmp 203.0.113.1:1024   172.16.0.1:1     8.8.8.8:1       8.8.8.8:1
icmp 203.0.113.1:1025   172.16.0.2:1     8.8.8.8:1       8.8.8.8:1
icmp 203.0.113.1:1026   172.16.0.3:1     8.8.8.8:1       8.8.8.8:1
```
All three PCs share `203.0.113.1`, distinguished by port.

## 8. Common Mistakes (80/20)

1. **Forgetting the `overload` keyword** — without it, `ip nat inside source list 1 interface G0/0` behaves like a single-address Dynamic NAT pool, still exhausts after one host, and looks like PAT "isn't working."
2. **Not removing the old pool-based statement before adding PAT** — IOS may reject the new command or produce confusing overlapping NAT behavior.
3. **Forgetting to `clear ip nat translation *`** when switching strategies — stale entries linger and make verification output confusing.
4. **Undersizing/oversizing the ACL** — an ACL that doesn't match all intended inside hosts silently leaves some untranslated, with no explicit error.
5. **Assuming Dynamic NAT pool exhaustion means something is broken** — it's expected, deterministic behavior given a pool smaller than the host count; the lab is designed to demonstrate this, not "fix" it within the Dynamic NAT phase.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Are inside/outside interfaces correctly designated? | `show ip nat statistics` | Correct `ip nat inside`/`ip nat outside` placement |
| 2 | Does the ACL match all intended inside hosts? | `show access-lists 1` | Correct the network/wildcard mask |
| 3 | (Dynamic NAT) Is the pool exhausted? | `show ip nat translations` (count active entries vs. pool size) | Expected behavior if hosts > pool size; increase pool or switch to PAT |
| 4 | (PAT) Is `overload` present? | `show running-config \| include ip nat inside source` | Add the missing `overload` keyword |
| 5 | Are stale entries from a previous NAT strategy interfering? | `show ip nat translations` | `clear ip nat translation *` |

## 10. Design Analysis

Dynamic NAT is rarely used alone in modern networks specifically because of the exhaustion problem demonstrated here — it requires as many public addresses as simultaneous inside hosts needing translation, which doesn't scale and wastes increasingly scarce IPv4 space. PAT solves this by trading address uniqueness for port-based multiplexing, at the cost of every inside host looking identical from the outside (useful for privacy/obscurity, unhelpful if the outside network needs to distinguish individual inside hosts, e.g., for abuse investigation, which is why PAT deployments often need port-logging for accountability). This is exactly why PAT — not Dynamic NAT — is the default outbound NAT strategy on virtually every consumer router and enterprise firewall today.

## 11. Real-World Parallel

Every home internet connection uses PAT: your ISP gives your router one public IP, and every device in your house (laptop, phone, smart TV, etc.) shares it via PAT, each session distinguished by source port — this lab's `overload` command is literally what your home router runs, just automatically and invisibly configured for you.

## 12. Stretch Goal

Combine this lab with Day 44: configure Static NAT for one server that needs a fixed public identity, while the rest of the internal LAN uses PAT for general outbound access — the realistic mixed-mode NAT configuration most production edge routers actually run.

## 13. Self-Assessment

- [ ] I can explain, precisely, why Dynamic NAT's pool can be exhausted while PAT's cannot (practically)
- [ ] I demonstrated pool exhaustion myself and can describe exactly what PC3 experienced
- [ ] I can state the one keyword that differentiates PAT from a single-address Dynamic NAT pool
- [ ] I correctly removed the Dynamic NAT configuration before adding PAT, and explained why order matters
- [ ] I can map inside local/inside global/outside local/outside global correctly for both Dynamic NAT and PAT scenarios

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Dynamic NAT (pool-based, one-to-one, exhaustible), PAT/NAT Overload (many-to-one, port-multiplexed), standard ACLs as NAT match criteria, NAT pool exhaustion, `overload` keyword, clean NAT strategy transitions.

**What I Learned:** Dynamic NAT is really just "automated Static NAT" from a scalability standpoint — it's still fundamentally one-to-one and therefore still address-limited. PAT is the actual scalable solution because it stops relying on IP-address uniqueness altogether and uses the transport layer (port numbers) to disambiguate sessions instead.

**Skills Practiced:** Dynamic NAT configuration, NAT pool creation, standard ACL use with NAT, observing and diagnosing pool exhaustion, clean NAT configuration removal, PAT/NAT Overload configuration, NAT translation table analysis across two different NAT strategies.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-45/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers and Alpine Linux end hosts, practicing both pool-based and interface-based (`masquerade`) NAT — VyOS's equivalent of Dynamic NAT and PAT.
