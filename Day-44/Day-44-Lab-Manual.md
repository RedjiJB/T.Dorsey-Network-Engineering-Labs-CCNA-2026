# Day 44 Lab Manual — Static NAT

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure permanent one-to-one Static NAT mappings for three internal hosts, verify translation behavior with real traffic, and understand which entries survive a translation-table clear |
| CCNA 200-301 Domains | 4.0 IP Services (NAT — static, inside/outside, translation table) |
| Prerequisites | Interface addressing, basic routing, ICMP/DNS fundamentals |
| Estimated Time | 45–60 minutes |
| Difficulty | Beginner–Intermediate |

## 1. Lab Overview + Learning Objectives

Static NAT gives an internal host a permanent, dedicated public-facing address — the classic use case is "this internal server needs a fixed public IP that never changes, e.g. because DNS points at it." This lab configures three such one-to-one mappings, proves they work with real ICMP and DNS traffic, and then demonstrates a subtle but important distinction: not everything in the NAT table is equal — some entries are permanent configuration, others are ephemeral traffic byproducts.

By the end of this lab you will be able to:

1. Correctly use and distinguish all four NAT terminology terms: inside local, inside global, outside local, outside global.
2. Configure `ip nat inside`/`ip nat outside` and explain why both are required.
3. Configure static one-to-one NAT mappings with `ip nat inside source static`.
4. Read and interpret `show ip nat translations` output, distinguishing static entries from traffic-generated ones.
5. Explain why `clear ip nat translation *` removes dynamic/traffic entries but not static mappings.

## 2. Business Context

A company might host an internal mail server, a VPN concentrator, or a partner-facing API server that needs a fixed, predictable public IP — DNS records, firewall rules, and partner allowlists all depend on that address never changing. Static NAT is exactly the tool for this: unlike dynamic NAT or PAT (which reuse a pool of addresses on demand), static NAT guarantees the same public address maps to the same internal host permanently, whether or not there's active traffic.

## 3. Topology Reference

- PC1, PC2, PC3 on an internal `172.16.0.0/24` LAN
- R1 — NAT router, `G0/1` faces the internal LAN (**inside**), `G0/0` faces the internet (**outside**)
- Internet Router — represents the ISP/internet edge
- External server at `8.8.8.8`

| Device | Interface | Address |
|---|---|---|
| PC1 | NIC | 172.16.0.1/24 |
| PC2 | NIC | 172.16.0.2/24 |
| PC3 | NIC | 172.16.0.3/24 |
| R1 | G0/1 (inside) | 172.16.0.254/24 |
| R1 | G0/0 (outside) | 203.0.113.1/30 |
| Internet Router | G0/0 | 203.0.113.2/30 |
| Server | NIC | 8.8.8.8 |

Topology image (original author's diagram, reused here — note the original file references the Day 43 image path by mistake; the correct Day 44 diagrams are the numbered `Day-44-Lab-Static-NAT-*.png` images referenced throughout the source lab):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/`

## 4. IP Addressing Plan — With Full NAT Terminology

### 4.1 Why Sized This Way

`172.16.0.0/24` is a private RFC 1918 range — correct choice for an internal LAN, since these addresses are never supposed to be globally routable. `203.0.113.0/30` (from the TEST-NET-3 documentation range, commonly reused in labs to represent "public" addressing without using real internet space) is right-sized for the point-to-point WAN link. `100.0.0.0/24` is used here purely as the pool of "inside global" addresses R1 will present to the outside world — in a real deployment this would be a block of addresses actually assigned to the company by their ISP or RIR.

### 4.2 Manual Calculation Walkthrough

```
172.16.0.0/24 → 255.255.255.0 → 254 usable hosts
203.0.113.0/30 → 255.255.255.252 → 2 usable hosts (R1 outside, Internet Router)
```

### 4.3 NAT Terminology — Be Explicit

Static NAT (and NAT generally) uses four precise terms. Getting these exactly right is one of the most commonly missed CCNA concepts:

| Term | Definition | This Lab's Example |
|---|---|---|
| **Inside local** | The actual address configured on the inside host, as it exists on the internal network | 172.16.0.1 (PC1's real address) |
| **Inside global** | The address that represents the inside host to the outside world | 100.0.0.1 (what the internet sees for PC1) |
| **Outside local** | The address of the outside host, as it appears from the inside network's perspective | 8.8.8.8 in this lab, since no NAT is applied to the outside host — outside local and outside global are identical here |
| **Outside global** | The actual, real address of the outside host | 8.8.8.8 — same as outside local because R1 does not translate destination/outside addresses in this lab |

Memory aid: "**Local** = how it looks **from the inside**. **Global** = how it looks **from the outside**. **Inside/Outside** = which side of the NAT boundary the real device lives on." A host's own "local" address is always its literal configured address; its "global" address is the one NAT substitutes for it when crossing the boundary.

### 4.4 Static NAT Mapping Table

| Inside Local | Inside Global |
|---|---|
| 172.16.0.1 | 100.0.0.1 |
| 172.16.0.2 | 100.0.0.2 |
| 172.16.0.3 | 100.0.0.3 |

## 5. Pre-Configuration Checklist

- [ ] Confirm PC1's ping to `8.8.8.8` fails before configuring NAT — proves the baseline problem NAT solves
- [ ] Decide the full inside local → inside global mapping table before touching the CLI
- [ ] Know exactly which interface is inside (LAN-facing) and which is outside (WAN-facing) — reversing these is the single most common NAT misconfiguration
- [ ] Confirm basic routing exists so R1 can reach the outside network at all — NAT doesn't fix a missing route

## 6. Configuration Tasks

### 6.1 Baseline test (before NAT)

```
C:\> ping 8.8.8.8
Request timed out. (x4)
```
This confirms the private `172.16.0.0/24` address is not (and should not be) routable across the public internet — this is the exact problem NAT exists to solve.

### 6.2 Designate inside and outside interfaces

```
R1(config)# interface g0/1
R1(config-if)# ip nat inside
R1(config-if)# exit
R1(config)# interface g0/0
R1(config-if)# ip nat outside
R1(config-if)# exit
```
Mode: interface config. NAT needs to know which side of the router is "inside" (private) and which is "outside" (where translation applies) — every NAT command elsewhere on the router depends on this designation being correct. Memory aid: "inside faces your users, outside faces the internet — get this backwards and NAT silently does nothing."

### 6.3 Configure static one-to-one mappings

```
R1(config)# ip nat inside source static 172.16.0.1 100.0.0.1
R1(config)# ip nat inside source static 172.16.0.2 100.0.0.2
R1(config)# ip nat inside source static 172.16.0.3 100.0.0.3
```
Mode: global config. Each line permanently binds one inside local address to one inside global address — this mapping exists in the NAT table whether or not there's active traffic, which is the defining characteristic of static NAT versus dynamic NAT or PAT. Memory aid: "static = set it once, it never changes, traffic or no traffic."

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `ping 8.8.8.8` | PC1 (before and after NAT) | Prove NAT is what enables outside reachability |
| `show ip nat translations` | R1 | View the translation table (static and dynamic entries) |
| `show ip nat statistics` | R1 | Confirm inside/outside interfaces and translation counts |
| `clear ip nat translation *` then `show ip nat translations` | R1 | Confirm static entries persist; dynamic entries don't |

### Expected Output Gallery

```
C:\> ping 8.8.8.8
Reply from 8.8.8.8: bytes=32 time=1ms TTL=128
Reply from 8.8.8.8: bytes=32 time=1ms TTL=128
Reply from 8.8.8.8: bytes=32 time=1ms TTL=128
Reply from 8.8.8.8: bytes=32 time=1ms TTL=128
```

```
R1# show ip nat translations
Pro  Inside global    Inside local     Outside local    Outside global
---  100.0.0.1        172.16.0.1       ---              ---
---  100.0.0.2        172.16.0.2       ---              ---
---  100.0.0.3        172.16.0.3       ---              ---
icmp 100.0.0.1:1      172.16.0.1:1     8.8.8.8:1        8.8.8.8:1
udp  100.0.0.1:1025   172.16.0.1:1025  8.8.8.8:53       8.8.8.8:53
```

```
R1# show ip nat statistics
Total translations: 5 (3 static, 2 dynamic; 0 extended)
Outside Interfaces: GigabitEthernet0/0
Inside Interfaces: GigabitEthernet0/1
```

```
R1# clear ip nat translation *
R1# show ip nat translations
Pro  Inside global    Inside local     Outside local    Outside global
---  100.0.0.1        172.16.0.1       ---              ---
---  100.0.0.2        172.16.0.2       ---              ---
---  100.0.0.3        172.16.0.3       ---              ---
```
Only the static (config-derived) entries survive the clear; the ICMP and UDP (DNS) entries generated by live traffic are removed.

## 8. Common Mistakes (80/20)

1. **Reversing inside/outside interface designation** — NAT will simply not translate anything, with no obvious error.
2. **Confusing "inside global" with "outside global"** — these are two completely different concepts (your host's public face vs. the actual remote host's real address); mixing them up is the single most common exam and real-world error.
3. **Forgetting that Static NAT entries never expire on their own** — unlike dynamic entries, they persist until explicitly removed with `no ip nat inside source static ...`, even if unused for months.
4. **Assuming NAT alone fixes connectivity** — if routing to the outside network is broken, NAT translation succeeding does nothing; both must work together.
5. **Not testing before AND after** — skipping the pre-NAT failing ping means you can't actually prove NAT was the fix, versus some other coincidental change.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Are host IP/gateway addresses correct? | Check PC IP config | Correct addressing |
| 2 | Is routing working end to end (ignoring NAT)? | `show ip route` on R1 | Fix routing/default route toward the internet |
| 3 | Is `ip nat inside` on the LAN interface? | `show ip interface g0/1 \| include NAT` or `show running-config` | Add `ip nat inside` on the correct interface |
| 4 | Is `ip nat outside` on the WAN interface? | Same as above for g0/0 | Add `ip nat outside` on the correct interface |
| 5 | Are the static mappings actually configured? | `show running-config \| include ip nat inside source` | Add missing `ip nat inside source static` lines |
| 6 | Does traffic actually generate translations? | `show ip nat translations` after pinging | If no entries appear, re-check inside/outside designation |

## 10. Design Analysis

Static NAT trades address efficiency for predictability: every internal host that needs one gets a dedicated, permanently reserved public address, even if it's idle most of the time — the opposite of PAT (port address translation), which multiplexes many internal hosts behind one public address using port numbers, maximizing address efficiency at the cost of every internal host looking identical from the outside. Static NAT is the right choice specifically when a stable, individually addressable public identity matters (servers, VPN endpoints); PAT is the right choice for general internet access from a large pool of client devices — which is why real networks typically use both simultaneously for different purposes.

## 11. Real-World Parallel

Any company hosting an on-premises server that needs a fixed public IP (a mail relay, a VPN gateway, a partner-facing API) uses exactly this static NAT pattern — and their firewall/NAT change requests almost always specify "inside local X maps to inside global Y" using this exact terminology, because ambiguity here causes real outages.

## 12. Stretch Goal

Add a fourth PC using dynamic NAT (a pool, not a static one-to-one mapping) alongside the three static entries, generate traffic from all four, and compare how `show ip nat translations` differs between static and dynamic entries — then observe how dynamic entries age out on their own over time while static ones do not.

## 13. Self-Assessment

- [ ] I can define all four NAT terms (inside local, inside global, outside local, outside global) correctly without notes
- [ ] I can explain why `ip nat inside`/`ip nat outside` must both be configured, and what happens if only one is set
- [ ] I proved NAT was the fix by testing connectivity both before and after configuration
- [ ] I can explain, precisely, why static entries survive `clear ip nat translation *` and dynamic ones don't
- [ ] I generated real ICMP and DNS traffic myself and observed the resulting dynamic translation entries

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Static NAT, inside/outside interface designation, inside local vs. inside global vs. outside local vs. outside global, one-to-one address mapping, NAT translation table entry types (static vs. dynamic).

**What I Learned:** The NAT table holds two fundamentally different kinds of entries — permanent configuration-derived static mappings and ephemeral traffic-derived dynamic ones — and confusing the two is a common source of both exam mistakes and real production troubleshooting confusion.

**Skills Practiced:** Static NAT configuration, NAT inside/outside interface designation, one-to-one IP mapping, ICMP/DNS connectivity testing, NAT translation table reading, NAT statistics interpretation, clearing NAT translations, Cisco IOS verification and troubleshooting.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-44/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers (NAT), Alpine Linux end hosts, and a pfSense CE firewall representing the Internet-edge boundary.
