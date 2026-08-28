# Day 35 Lab Manual — Extended ACLs: Destination and Port-Based Filtering

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure extended named ACLs enforcing three service/destination-specific policies on top of the Day 34 OSPF-routed topology, filtering by source, destination, protocol, and port simultaneously. |
| **Exam Relevance** | CCNA 200-301 — Domain 5 (Security Fundamentals): extended ACL syntax, protocol/port matching, ACL placement strategy for granular policy. |
| **Prerequisites** | Day 34 (standard ACLs, OSPF-routed topology, wildcard masks). |
| **Time Estimate** | 90–110 minutes. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — same topology as Day 34, but each policy now requires reasoning about protocol and port in addition to source/destination. |

---

## 1. Lab Overview + Learning Objectives

This lab reuses Day 34's OSPF-routed topology and upgrades the security layer from standard ACLs (source-only) to **extended ACLs** (source + destination + protocol + port). Three policies require exactly this granularity: blocking one specific host from one specific PC, blocking one subnet from one specific service on one server, and blocking one subnet from two specific services (HTTP and HTTPS) on another server — while leaving every other service on those same servers untouched.

By the end of this lab you will be able to:

- Write extended named ACLs matching on protocol (TCP/UDP/ICMP/IP), source, destination, and port
- Choose the correct port-matching keyword/operator (`eq`, `host`, well-known service names) for a given policy
- Explain precisely why a policy needs an extended ACL instead of a standard one
- Stack multiple deny lines for related-but-distinct services (HTTP + HTTPS) under one ACL
- Verify service-level filtering behavior (e.g., ping still works while a specific TCP port is blocked)

---

## 2. Business Context

**Why would a real company do this?**

- **"Block this one problem laptop from this one specific server — everything else on the network should be untouched."** Policy A (LAN2 blocked from PC1 specifically) models exactly this: a targeted block, not a blanket subnet-wide policy, which a standard ACL simply cannot express without collateral damage.
- **"Our DNS server should not accept lookups from the general office network — only from the DNS admin subnet — but it should still be pingable for monitoring."** Policy B (LAN1 blocked from SRV1's DNS service specifically) is a textbook case of "block this exact protocol/port, allow everything else," which is a routine requirement for any server running multiple services with different trust levels per client segment.
- **"Marketing's segment shouldn't be able to browse our internal web app, but they still need general IP connectivity to it for other internal tooling."** Policy C (LAN2 blocked from SRV2's HTTP/HTTPS specifically) demonstrates that "block the web app, not the whole server" is achievable cleanly with extended ACLs, whereas a standard ACL would have to choose between blocking everything or nothing.
- **"We need to prove to security reviewers that our firewalling is least-privilege, not just a big allow/deny hammer."** Being able to write and justify service-specific ACLs — as opposed to always reaching for a blanket subnet block — is precisely the kind of surgical policy design that separates a junior engineer's first ACL attempt from a security-review-ready configuration.

---

## 3. Topology Reference

Same physical topology as [Day 34](../Day-34/Day-34-Lab-Manual.md) — reused here because the point of this lab is a *policy upgrade*, not a new network build. Two routers, four subnets, OSPF already routing everything.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-35-Lab-Extended-ACLs.png" alt="Day 35 Extended ACLs Topology" width="900">
</p>

---

## 4. IP Addressing Plan

Reused from Day 34, with SRV1 now explicitly running DNS and SRV2 explicitly running a web service:

| Device | Interface | IP Address | Subnet | Role |
|---|---|---|---|---|
| R1 | G0/0 | 172.16.1.254 | 172.16.1.0/24 (LAN1) | |
| R1 | G0/1 | 172.16.2.254 | 172.16.2.0/24 (LAN2) | |
| R1 | S0/0/0 | 203.0.113.1 | 203.0.113.0/30 | |
| R2 | S0/0/0 | 203.0.113.2 | 203.0.113.0/30 | |
| R2 | G0/0 | 192.168.1.254 | 192.168.1.0/24 | |
| R2 | G0/1 | 192.168.2.254 | 192.168.2.0/24 | |
| PC1 | Fa0 | 172.16.1.1 | LAN1 | Target of Policy A |
| PC2 | Fa0 | 172.16.1.2 | LAN1 | |
| PC3 | Fa0 | 172.16.2.1 | LAN2 | Source of Policies A/C |
| PC4 | Fa0 | 172.16.2.2 | LAN2 | Source of Policies A/C |
| SRV1 | Fa0 | 192.168.1.100 | 192.168.1.0/24 | DNS server (Policy B) |
| SRV2 | Fa0 | 192.168.2.100 | 192.168.2.0/24 | Web server (Policy C) |

### 4.1 Why standard ACLs cannot express these three policies

Recall a standard ACL evaluates **source address only**. All three of this lab's policies require at least one more dimension:

| Policy | Needs destination? | Needs protocol/port? | Why standard ACL fails |
|---|---|---|---|
| A: LAN2 blocked from PC1 only | Yes (PC1, not "everything R1 routes") | No | A source-only rule denying LAN2 would also block LAN2 from SRV1, SRV2 — collateral damage far beyond the stated policy |
| B: LAN1 blocked from SRV1's DNS only | Yes (SRV1 specifically) | Yes (UDP/53 only) | A source-only rule would block LAN1 from SRV1 entirely, including services other than DNS that should remain reachable |
| C: LAN2 blocked from SRV2's HTTP/HTTPS only | Yes (SRV2 specifically) | Yes (TCP/80, TCP/443) | Same reasoning — blocking all of SRV2 from LAN2 would be a much bigger blast radius than "just the web app" |

### 4.2 Port and protocol reference

| Service | Protocol | Port | ACL keyword |
|---|---|---|---|
| HTTP | TCP | 80 | `eq www` or `eq 80` |
| HTTPS | TCP | 443 | `eq 443` |
| DNS | UDP | 53 | `eq domain` |
| DNS (zone transfer/large response) | TCP | 53 | `eq domain` |
| SSH | TCP | 22 | `eq 22` |
| ICMP (ping) | ICMP | n/a | `icmp` (no port keyword — ICMP has message types, not ports) |
| Everything else | IP | n/a | `ip any any` (used for the trailing permit) |

**Port operators available:** `eq` (equal), `gt` (greater than), `lt` (less than), `neq` (not equal), `range <low> <high>`.

---

## 5. Pre-Configuration Checklist

1. Confirm Day 34's OSPF and full connectivity are already working before adding these ACLs — if they're not, you can't distinguish a routing problem from a new ACL problem.
2. Have each policy's protocol/port explicitly identified (Section 4.2) before writing any ACL line.
3. Confirm you understand `host <ip>` is shorthand for `<ip> 0.0.0.0` — you'll use it for both source and destination matching in this lab.

---

## 6. Configuration Tasks

### 6.1 Policy A — LAN2 (172.16.2.0/24) cannot communicate with PC1

```text
R1(config)#ip access-list extended block_pc1
R1(config-ext-nacl)# deny ip 172.16.2.0 0.0.0.255 host 172.16.1.1
R1(config-ext-nacl)# permit ip any any
R1(config-ext-nacl)#exit
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ip access-group block_pc1 in
```

- **Mode:** Named extended ACL configuration (`ip access-list extended <name>`), then interface configuration.
- **`deny ip 172.16.2.0 0.0.0.255 host 172.16.1.1`** — `ip` (not `tcp`/`udp`) means "any protocol," since the policy says "can't communicate," not "can't use a specific service." The source is a subnet (wildcard), the destination is `host 172.16.1.1` — the shorthand for an exact single address.
- **Placement:** inbound on R1 G0/0 (PC1's own LAN interface) — this stops LAN2's traffic at the last possible point before it would reach PC1, without affecting LAN2's other traffic (to SRV1, SRV2, etc.), which is exactly the surgical scope this policy calls for.

### 6.2 Policy B — LAN1 (172.16.1.0/24) cannot access SRV1's DNS service

```text
R1(config)#ip access-list extended block_DNS_SRV1
R1(config-ext-nacl)# deny udp 172.16.1.0 0.0.0.255 host 192.168.1.100 eq domain
R1(config-ext-nacl)# permit ip any any
R1(config-ext-nacl)#exit
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ip access-group block_DNS_SRV1 in
```

- **`deny udp ... eq domain`** — protocol is UDP specifically (standard DNS queries), port is `domain` (the IOS keyword alias for port 53). ICMP, TCP/SSH, and any other service on SRV1 are untouched because this line only matches UDP/53.
- **Production note:** DNS can also use TCP/53 for zone transfers and large responses; a fully DNS-blocking policy would add a second `deny tcp ... eq domain` line. This lab's stated policy is UDP-only, so only one line is required, but recognizing this gap is worth remembering for real deployments.
- **Placement:** same interface as Policy A (R1 G0/0) — both policies originate from traffic entering R1 from a LAN, so both are scoped at the earliest point that traffic can be identified and stopped. Note: applying two ACLs to the same interface/direction isn't directly supported (an interface can have one `ip access-group` per direction) — in practice you would either combine both policies into a single ACL with multiple statements, or place them on separate interfaces/directions as this lab's structure allows (see Section 8, Common Mistake #6, for the real fix).

### 6.3 Policy C — LAN2 (172.16.2.0/24) cannot access SRV2's HTTP or HTTPS

```text
R1(config)#ip access-list extended Block_HTTP_HTTPS_SRV2
R1(config-ext-nacl)# deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www
R1(config-ext-nacl)# deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443
R1(config-ext-nacl)# permit ip any any
R1(config-ext-nacl)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#ip access-group Block_HTTP_HTTPS_SRV2 in
```

- **Two separate `deny` lines, not one.** HTTP and HTTPS are two distinct ports; there's no single wildcard-port match for "80 or 443" in a simple extended ACL line (a `range` operator only covers a contiguous span, and 80–443 would sweep in many unrelated ports) — stacking two explicit lines is the correct, precise approach.
- **Placement:** inbound on R1 G0/1 (LAN2's own interface) — this is the correct placement since this policy's source is LAN2, matching the "closest to source" principle.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip access-lists <name>` | Confirms exact rule text and match counters per line |
| `show ip interface g0/0` / `g0/1` | Confirms which ACL is bound, in which direction |
| `ping` (ICMP) vs a service-specific test | Confirms ICMP still works where only a TCP/UDP port was blocked — proves surgical scope |

### 7.1 Expected Output Gallery

**`R1# show ip access-lists Block_HTTP_HTTPS_SRV2`**
```text
Extended IP access list Block_HTTP_HTTPS_SRV2
    10 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www (14 matches)
    20 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443 (3 matches)
    30 permit ip any any (211 matches)
```

**`PC3> ping 192.168.2.100`** (Policy C in effect — ICMP still works)
```text
Pinging 192.168.2.100 with 32 bytes of data:
Reply from 192.168.2.100: bytes=32 time=2ms TTL=125
Reply from 192.168.2.100: bytes=32 time=1ms TTL=125
Reply from 192.168.2.100: bytes=32 time=1ms TTL=125
Reply from 192.168.2.100: bytes=32 time=1ms TTL=125

Ping statistics: Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```
ICMP is not TCP/UDP, so `permit ip any any` (the trailing line) still allows it — this is the proof the policy is scoped exactly to the two ports named, not the whole server.

**`PC2> ping 172.16.1.1`** (Policy A in effect — PC2 is NOT in the blocked subnet)
```text
Pinging 172.16.1.1 with 32 bytes of data:
Reply from 172.16.1.1: bytes=32 time=1ms TTL=128
Reply from 172.16.1.1: bytes=32 time=1ms TTL=128
Reply from 172.16.1.1: bytes=32 time=1ms TTL=128
Reply from 172.16.1.1: bytes=32 time=1ms TTL=128
```
PC2 is in LAN1 (172.16.1.0/24), not LAN2 — Policy A only denies LAN2, so this succeeds, confirming the ACL's scope is exactly as intended.

### 7.2 Reachability Matrix

| From | To | Expected | Why |
|---|---|---|---|
| PC3 (LAN2) | PC1 | **Fail** (all protocols) | Policy A |
| PC2 (LAN1) | PC1 | Success | Policy A only applies to LAN2 |
| PC2 (LAN1) | SRV1 ping | Success | ICMP not blocked by Policy B |
| PC2 (LAN1) | SRV1 DNS lookup | **Fail** | Policy B (UDP/53) |
| PC3 (LAN2) | SRV2 ping | Success | ICMP not blocked by Policy C |
| PC3 (LAN2) | SRV2 HTTP | **Fail** | Policy C (TCP/80) |
| PC3 (LAN2) | SRV2 HTTPS | **Fail** | Policy C (TCP/443) |
| PC3 (LAN2) | SRV2 SSH (if present) | Success | Policy C only names 80/443 |

---

## 8. Common Mistakes (the 80/20)

1. **Reaching for a standard ACL out of habit when the policy names a destination or service.** If the requirement includes "...to this specific server" or "...for this specific service," it's extended, full stop.
2. **Forgetting `permit ip any any` at the end.** Without it, the implicit deny blocks all traffic that didn't match an earlier line — including traffic completely unrelated to the stated policy.
3. **Using `eq http` instead of `eq www` or `eq 80`.** `http` is not a valid IOS keyword for this context — a common typo-by-assumption.
4. **Forgetting HTTPS needs its own line.** `eq www` only matches port 80; port 443 needs an explicit second `deny` line, as shown in Policy C.
5. **Assuming ICMP is blocked by a TCP/UDP-specific deny.** ICMP is a different protocol entirely — a `deny tcp ...` or `deny udp ...` line never matches ICMP traffic, which is exactly why ping remains a valid "is the server still generally reachable" test even under a service-specific block.
6. **Trying to apply two separate ACLs to the same interface and direction.** Cisco IOS allows only one ACL per interface per direction — if two distinct policies both need to apply to the same interface/direction, combine them into a single ACL with multiple rule lines (in match-priority order) rather than trying to stack separate ACL names.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Entire subnet loses all connectivity, not just the intended service | Standard ACL logic used by mistake, or missing `permit ip any any` | `show ip access-lists` | Rewrite with correct protocol/port matching and trailing permit |
| 2 | Ping to the target still succeeds even though it "should" be blocked | Deny line specified the wrong protocol (e.g., `tcp` when the traffic is `udp`, or vice versa) | `show ip access-lists <name>` (check match counters — 0 means never triggered) | Correct the protocol keyword |
| 3 | HTTPS still reaches the server after "blocking web access" | Only `eq www` (port 80) was written; port 443 needs its own line | `show ip access-lists <name>` | Add `deny tcp ... eq 443` |
| 4 | ACL rejected at configuration time when trying to apply a second one to the same interface/direction | IOS only allows one `ip access-group` per interface per direction | Attempt to `ip access-group` a second name — IOS silently replaces the first | Merge both policies into one ACL |
| 5 | Legitimate traffic unexpectedly blocked | Wildcard mask too broad, or destination `host` address typo'd | `show ip access-lists <name>` (compare address literally) | Correct the source/destination match |

---

## 10. Design Analysis

- **Why extended over standard here specifically?** Covered in depth in Section 4.1 — every one of this lab's three policies fails the "source only" test that standard ACLs are limited to.
- **Why two `deny` lines for HTTP+HTTPS instead of one line with a range?** `range 80 443` would also match every port number between 81 and 442 — none of which are the stated policy's target — so it would massively over-block. Two explicit lines are more verbose but precisely correct; this is a deliberate trade of a few extra lines for exact policy accuracy, which is almost always the right trade in security configuration.
- **Why keep ICMP unblocked in all three policies (via the trailing `permit ip any any`, since none of the deny lines target ICMP)?** Leaving basic reachability (ping) intact while blocking a specific service is standard practice — it keeps monitoring/alerting tools functional (which typically rely on ICMP or SNMP, not the blocked service) even while the actual service access is restricted, and it makes troubleshooting the policy itself much easier (you can immediately tell "is this a routing problem or a policy problem" by whether ping succeeds).
- **Why apply Policy A on R1 G0/0 instead of R2 (closer to nothing in particular, since PC1 isn't behind R2)?** PC1 lives on R1's own LAN — R1 G0/0 is the only interface anywhere in the topology where this traffic could be intercepted before reaching PC1, so there's no meaningful alternative placement; the "closest to source or destination, whichever stops it earliest without over-blocking" principle points here directly.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a security team asks for "least privilege" access control and a network engineer has to translate that into precise protocol/port ACL lines instead of blanket subnet blocks.
- ...an internal web application needs to be walled off from one office segment for a compliance reason, while SSH/monitoring access to the same server must remain intact for the ops team — Policy C's exact shape.
- ...a DNS server is locked down to only accept queries from designated resolvers, while remaining pingable by the monitoring system — Policy B's exact shape, and a genuinely common DNS hardening practice.

---

## 12. Stretch Goal

1. Merge Policies A and B into a single ACL applied to R1 G0/0 (since IOS only allows one ACL per interface/direction, as noted in Common Mistake #6) — verify both policies still function correctly from a single ACL.
2. Add a fourth policy: block LAN1 from SSH (TCP/22) on SRV2 specifically, while leaving HTTP/HTTPS from LAN1 to SRV2 untouched. Write the ACL and determine correct placement.
3. Investigate the `range` operator by writing (but not necessarily deploying) an ACL line that blocks TCP ports 1024–65535 from a subnet to a server — what legitimate use case would this represent, and why is it much broader than this lab's HTTP/HTTPS policy?

---

## 13. Self-Assessment

- [ ] Can you state, from memory, the four things an extended ACL can match that a standard ACL cannot (in combination)?
- [ ] Can you explain why HTTP and HTTPS require two separate `deny` lines rather than one?
- [ ] Can you explain why ICMP traffic passes even under a TCP- or UDP-specific deny rule?
- [ ] Given a plain-English policy naming a specific server and service, could you correctly choose the protocol keyword and port operator without a reference table?
- [ ] Can you explain the constraint that limits an interface to one ACL per direction, and how you'd work around it for two simultaneous policies on the same interface?

---

## 14. Key Concepts Demonstrated

- Extended named ACL syntax: protocol, source, destination, port
- Precise, surgical service-level filtering versus blanket subnet blocking
- Port/protocol reference for common services (HTTP, HTTPS, DNS)
- ICMP's independence from TCP/UDP-specific filtering rules
- The one-ACL-per-interface-per-direction constraint and how to work around it

## 15. What I Learned

Extended ACLs aren't just "standard ACLs with more options" — they represent a genuinely different design posture: least-privilege, service-specific access control instead of blanket subnet-level allow/deny. The habit of reaching for a standard ACL whenever a policy mentions a specific server or service is the single biggest tell that a redesign toward extended ACLs is needed. Stacking multiple `deny` lines for related-but-distinct ports (HTTP, HTTPS) instead of trying to compress them into one line is the correct trade — precision over brevity — and it's a pattern that scales cleanly to real production policies with many services.

## 16. Skills Practiced

- Extended named ACL authoring (protocol, source, destination, port)
- Service/port reference lookup and correct keyword usage
- ACL placement reasoning for destination-aware policies
- Verification via mixed protocol testing (ICMP vs TCP/UDP) to confirm surgical policy scope

---

## 17. GNS3 Lab

This lab reuses [Day 34's GNS3 topology](../Day-34/GNS3/build_lab.py) unchanged — no new devices or links are required, since this lab is a policy upgrade on the existing network, not a new build. Re-run `../Day-34/GNS3/build_lab.py` if you haven't already built the Day 34 topology, then apply this lab's extended ACL equivalents (VyOS firewall rule-sets with protocol/port match criteria) per [Day 34's README](../Day-34/GNS3/README.md), adding `destination port` and `protocol` match clauses to each rule.
