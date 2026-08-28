# Day 31 Lab Manual — IPv6 Dual-Stack Configuration on a Multi-LAN Router

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Convert an existing IPv4-only, single-router, three-LAN topology into a fully functional IPv4/IPv6 dual-stack network, without disturbing the working IPv4 configuration. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): IPv6 addressing types, IPv6 vs IPv4 comparison. Domain 4 (IP Connectivity): enabling IPv6 unicast routing, verifying IPv6 routes. |
| **Prerequisites** | Comfort with IPv4 addressing and Cisco IOS interface configuration (Days 1–10 material). No prior IPv6 experience required — this is the first IPv6 lab in the sequence. |
| **Time Estimate** | 60–90 minutes (first attempt); 20–30 minutes on repeat. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner) — one router, no subnetting math required (every LAN is a clean /64), the main challenge is unlearning IPv4 habits. |

---

## 1. Lab Overview + Learning Objectives

This lab takes a router (`R1`) with three already-working IPv4 LANs and adds IPv6 addressing on top — a **dual-stack** configuration, meaning both protocols run simultaneously on the same physical interfaces with no tunneling or translation between them.

By the end of this lab you will be able to:

- Explain what "dual-stack" means and why it's the standard IPv6 migration strategy
- Enable IPv6 forwarding globally on a Cisco router with `ipv6 unicast-routing`
- Assign global unicast IPv6 addresses to multiple router interfaces
- Understand and identify link-local addresses (`FE80::/10`) that exist automatically on every IPv6-enabled interface
- Configure dual-stack addressing (both IPv4 and IPv6) on end hosts, including two separate default gateways
- Verify IPv6 connectivity with `show ipv6 interface brief`, `show ipv6 route`, and IPv6 ping
- Read and write IPv6 addresses correctly, including `::` zero-compression rules

---

## 2. Business Context

**Why would a real company do this?**

- **"We can't switch off IPv4 overnight, but we need to support IPv6 now."** Every major ISP, mobile carrier, and cloud provider (AWS, Azure, GCP) now offers IPv6 alongside IPv4. A company whose external-facing services don't answer on IPv6 is invisible to a growing share of IPv6-only mobile clients and to any partner who mandates IPv6 reachability in a contract. Dual-stack is the transition mechanism virtually every enterprise uses — it doesn't require picking a side.
- **"Our address space is a mess and IPv4 is running out internally too."** Even inside a private network, IPv4 exhaustion (or overlapping RFC 1918 space after a merger/acquisition) is a real, recurring problem. IPv6's enormous address space (a single /64 has more addresses than the entire IPv4 internet) sidesteps that problem permanently once fully adopted.
- **"Auditors and government contracts increasingly require IPv6 readiness."** US federal agencies and their contractors have IPv6-mandated deadlines (OMB M-21-07). A network engineer who can't stand up dual-stack on request is not compliant-ready.
- **"We want zero downtime while we test IPv6."** Because dual-stack runs both protocols independently on the same interface, you can validate IPv6 reachability, monitoring, and firewall rules in production without touching the IPv4 path that users currently depend on. If IPv6 breaks, IPv4 keeps working — this is precisely why dual-stack, not a hard cutover, is the default strategy taught here and used industry-wide.

This is usually one of the first tickets a network engineer gets when a company begins its IPv6 rollout: "add IPv6 to the existing LANs without breaking anything." That's exactly this lab.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-31-Lab-IPv6-Configuration-(Part%201).png" alt="Day 31 IPv6 Dual-Stack Topology" width="900">
</p>

```text
PC1 (LAN1) -- SW1 -- R1 G0/0
PC2 (LAN2) -- SW2 -- R1 G0/1
PC3 (LAN3) -- SW3 -- R1 G0/2
```

One router, three directly connected LANs, each with a single PC. IPv4 is already fully configured and working; this lab adds IPv6 only.

---

## 4. IP Addressing Plan (IPv6)

### 4.1 The existing IPv4 plan (untouched)

| Segment | Network |
|---|---|
| LAN1 | 192.168.1.0/24 |
| LAN2 | 192.168.2.0/24 |
| LAN3 | 192.168.3.0/24 |

### 4.2 The IPv6 plan you're adding

| Segment | IPv6 Prefix | Router Address | Host Address |
|---|---|---|---|
| LAN1 | 2001:DB8:0:1::/64 | 2001:DB8:0:1::1 | 2001:DB8:0:1::2 |
| LAN2 | 2001:DB8:0:2::/64 | 2001:DB8:0:2::1 | 2001:DB8:0:2::2 |
| LAN3 | 2001:DB8:0:3::/64 | 2001:DB8:0:3::1 | 2001:DB8:0:3::2 |

### 4.3 Why every LAN is a /64 — and why that's different from IPv4 subnetting

IPv4 subnetting is a math problem: count hosts, solve for host bits, shrink the mask to fit. IPv6 subnetting is almost the opposite philosophy — **the LAN prefix is fixed at /64 by convention and by protocol dependency**, regardless of how many hosts actually sit on it.

Why /64 specifically, not /60 or /112 to "save space" the way IPv4 thinking would suggest:

- **SLAAC and EUI-64 require exactly 64 bits of host space.** Both stateless autoconfiguration mechanisms (used starting Day 33) construct a 64-bit interface identifier from the MAC address. If the prefix isn't /64, the host portion isn't 64 bits, and EUI-64/SLAAC math breaks.
- **There is no address exhaustion pressure at the LAN level.** A /64 provides 2^64 (about 18 quintillion) addresses — you will never run out, so there is no engineering reason to shrink it the way you would shrink an IPv4 /24 down to a /29 for a 6-host segment.
- **The address space is so large that "wasting" a /64 on a point-to-point link (2 hosts) is standard practice**, not the anti-pattern it would be in IPv4. (You'll see /64 used even on 2-host WAN links in Day 32/33 — some shops use /127 there instead, but /64 remains the LAN default everywhere.)

**The structural difference from IPv4 subnetting, concretely:**

| | IPv4 | IPv6 |
|---|---|---|
| Unit of subnetting math | Bits within a decimal octet | Hex **nibbles** (4 bits each) within a hextet |
| Typical LAN size | Sized to exact host count (/24, /27, /29…) | Always /64, regardless of host count |
| Boundary alignment | Falls on any bit position after calculation | Almost always falls on a nibble (hex digit) boundary for readability |
| "Wasting" space | A design smell (Day 1's `/30` reasoning) | Expected and irrelevant — 2^64 addresses cannot be meaningfully exhausted |

**Nibble-boundary thinking, worked example.** In this lab, the only distinguishing digit between LAN1, LAN2, and LAN3 is the 4th hextet: `...0:1::`, `...0:2::`, `...0:3::`. Each hextet is 16 bits = 4 hex nibbles (4 bits each). Because the /64 boundary lands exactly at the end of the 4th hextet, you never have to do binary math to find where a subnet starts — you just read the hex digits directly, the way you'd read `.0`, `.64`, `.128`, `.192` in an IPv4 /26 table, except now it's nibble-clean instead of needing a calculator: hextet 4 = `0001` → LAN1, `0002` → LAN2, `0003` → LAN3. This is why enterprise IPv6 plans almost always subnet on nibble boundaries (every 4 bits) instead of arbitrary bit counts — it keeps every prefix human-readable in hex without conversion.

### 4.4 Reading and writing IPv6 addresses

An IPv6 address is 128 bits, written as eight 16-bit **hextets** separated by colons: `2001:0DB8:0000:0001:0000:0000:0000:0002`.

Two compression rules make this readable:

1. **Leading zeros within a hextet can be dropped.** `0DB8` → `DB8`, `0001` → `1`.
2. **Exactly one run of consecutive all-zero hextets can be collapsed to `::`.** `2001:DB8:0:1:0:0:0:2` → `2001:DB8:0:1::2`.

You cannot use `::` twice in the same address — the decompression would be ambiguous (the router wouldn't know how many zero hextets each `::` represents). `2001:DB8::0:1::2` is invalid for exactly this reason.

**2001:DB8::/32** is IANA's reserved documentation prefix (RFC 3849) — like `192.0.2.0/24` and `203.0.113.0/24` in IPv4, it will never be assigned to a real network, which is why every lab and every textbook example uses it.

---

## 5. Pre-Configuration Checklist

1. Confirm IPv4 is already working end-to-end (ping between PCs across R1) before touching IPv6 — this isolates any later failure as IPv6-specific.
2. Have the IPv6 addressing table (Section 4.2) open for reference.
3. Confirm each interface's existing IPv4 config with `show ip interface brief` so you don't accidentally overwrite it.
4. Know your platform's IPv6 PC configuration path (Packet Tracer: Desktop → IP Configuration; GNS3 Alpine hosts: `ip -6 addr add`).

---

## 6. Configuration Tasks

### 6.1 Enable IPv6 unicast routing (global, one command, one time)

```text
R1>enable
R1#configure terminal
R1(config)#ipv6 unicast-routing
```

- **Mode:** Global configuration.
- **What it does:** Turns on IPv6 packet forwarding between interfaces. Without it, a router can have perfectly valid IPv6 addresses on every interface and still refuse to route between them — `ipv6 enable`/`ipv6 address` only turn IPv6 *on* for a given interface, they don't turn the router into an IPv6 router.
- **Why it matters:** This is the single most-forgotten command in every IPv6 lab. `show ipv6 route` will simply stay empty of anything beyond directly-connected/local entries if you skip it, and there's no obvious error message — the omission is silent.
- **Memory aid:** Unicast-routing is IPv6's version of "ip routing" being on by default in IPv4 — except in IPv6 it is **off** by default and must be explicitly switched on. Say it as "the IPv6 on-switch."

### 6.2 Configure each LAN interface with a global IPv6 address

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ipv6 address 2001:DB8:0:1::1/64
R1(config-if)#ipv6 enable
R1(config-if)#exit

R1(config)#interface gigabitEthernet 0/1
R1(config-if)#ipv6 address 2001:DB8:0:2::1/64
R1(config-if)#ipv6 enable
R1(config-if)#exit

R1(config)#interface gigabitEthernet 0/2
R1(config-if)#ipv6 address 2001:DB8:0:3::1/64
R1(config-if)#ipv6 enable
R1(config-if)#exit
```

- **Mode:** Interface configuration.
- **`ipv6 address <prefix>/64`** assigns the router's global unicast address for that LAN. By convention the router/gateway takes the first usable address in the prefix, `::1` — exactly like `.1` in an IPv4 LAN.
- **`ipv6 enable`** ensures IPv6 (and its automatic link-local address) is active on the interface even if you hadn't already implied it by assigning a global address. Technically redundant once a global `ipv6 address` is configured (which auto-enables IPv6), but including it explicitly is good practice and required on interfaces that will carry only a link-local address later (Day 32).
- **Why `::1` for the gateway, every time:** it's a readability convention, not a protocol requirement — but following it consistently (as this whole lab series does) means anyone reading your addressing table instantly knows which address is the gateway without cross-referencing a legend.
- **No subnet mask math needed here** — every LAN is /64 by the reasoning in Section 4.3, so there's no host-bit calculation step the way there was in Day 1's IPv4 plan.

### 6.3 Configure PC1, PC2, PC3 with dual-stack addressing

At each PC's Desktop → IP Configuration (or equivalent), set both stacks:

| Field | PC1 | PC2 | PC3 |
|---|---|---|---|
| IPv4 Address | 192.168.1.2 | 192.168.2.2 | 192.168.3.2 |
| IPv4 Gateway | 192.168.1.1 | 192.168.2.1 | 192.168.3.1 |
| IPv6 Address | 2001:DB8:0:1::2/64 | 2001:DB8:0:2::2/64 | 2001:DB8:0:3::2/64 |
| IPv6 Gateway | 2001:DB8:0:1::1 | 2001:DB8:0:2::1 | 2001:DB8:0:3::1 |

- **Why two gateways:** IPv4 and IPv6 are entirely independent routing tables and forwarding paths sharing the same wire. A dual-stack host must know where to send IPv4 traffic and, separately, where to send IPv6 traffic — there's no shared "the gateway" concept across protocols.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ipv6 interface brief` | Every LAN interface shows a link-local (`FE80::`) and global address, status `up/up` |
| `show ipv6 route` | One `C` (connected) and one `L` (local /128) entry per LAN |
| `show ipv6 protocols` | Confirms `ipv6 unicast-routing` took effect (shows "connected" and "static" as active sources) |
| `show ipv6 interface g0/0` | Full detail: global address, joined multicast groups |
| PC `ipconfig` | Shows both IPv4 and IPv6 address/gateway pairs |

### 7.1 Expected Output Gallery

**`R1# show ipv6 interface brief`**
```text
GigabitEthernet0/0    [up/up]
    FE80::221:A1FF:FE23:1101
    2001:DB8:0:1::1
GigabitEthernet0/1    [up/up]
    FE80::221:A1FF:FE23:1102
    2001:DB8:0:2::1
GigabitEthernet0/2    [up/up]
    FE80::221:A1FF:FE23:1103
    2001:DB8:0:3::1
```

**`R1# show ipv6 route`**
```text
IPv6 Routing Table - default - 7 entries
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
```

**`PC1> ipconfig`**
```text
FastEthernet0 Connection:

Link-local IPv6 Address........: FE80::2D0:97FF:FE12:71A1
IPv6 Address....................: 2001:DB8:0:1::2
IPv4 Address....................: 192.168.1.2
Subnet Mask......................: 255.255.255.0
Default Gateway..................: 2001:DB8:0:1::1
                                    192.168.1.1
```

**`PC1> ping 2001:DB8:0:2::2`**
```text
Pinging 2001:DB8:0:2::2 with 32 bytes of data:
Reply from 2001:DB8:0:2::2: bytes=32 time=1ms
Reply from 2001:DB8:0:2::2: bytes=32 time=1ms
Reply from 2001:DB8:0:2::2: bytes=32 time=1ms
Reply from 2001:DB8:0:2::2: bytes=32 time=1ms

Ping statistics: Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

### 7.2 Reachability Matrix

| From | To | Expected | Why |
|---|---|---|---|
| PC1 | PC2 (IPv4) | Success | R1 routes IPv4 normally |
| PC1 | PC2 (IPv6) | Success | `ipv6 unicast-routing` enables inter-LAN IPv6 forwarding |
| PC1 | R1 G0/0 link-local | Success (from R1's own interfaces, not typically pinged from PCs) | link-local is scoped to the local link only |
| PC1 | PC3 (IPv6) | Success | Same reasoning, third LAN |

---

## 8. Common Mistakes (the 80/20)

1. **Forgetting `ipv6 unicast-routing`.** Everything else can be perfect and `show ipv6 route` will still be empty of anything beyond the directly-connected LAN the PC pinging from sits on. This is by far the most common miss.
2. **Typing `ip address` instead of `ipv6 address`.** Muscle memory from years of IPv4 labs. IOS will silently accept an `ipv6 address` command with the wrong syntax family if you're not careful about the command prefix.
3. **Forgetting the `/64`.** Omitting the prefix length either errors out or (on some platforms) silently defaults incorrectly — always include it explicitly.
4. **Assuming the PC only needs one gateway.** Dual-stack means two independent gateway fields; leaving the IPv6 gateway blank breaks inter-LAN IPv6 reachability even though the address itself looks correct in `ipconfig`.
5. **Using two `::` in one address by hand-typing a "simplified" address.** `2001:db8::1::2` is invalid — this typically appears when someone tries to compress an address without checking there's only one run of zeros.
6. **Confusing link-local with global.** A link-local address (`FE80::...`) will never successfully be used as a PC's default gateway across a WAN-scale ping test outside this LAN's context — it's link-scoped by definition, covered in depth in Day 32.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | `show ipv6 route` shows only local LANs, no other subnets ever appear even with static routes later | `ipv6 unicast-routing` missing | `show ipv6 protocols` | `ipv6 unicast-routing` in global config |
| 2 | Interface has no IPv6 addresses at all | `ipv6 enable`/`ipv6 address` never applied, or interface administratively down | `show ipv6 interface brief` | Configure IPv6 address; `no shutdown` |
| 3 | PC has an IPv6 address but can't ping its own gateway | Wrong prefix length or gateway typo on the PC | `ipconfig` on PC, compare to Section 4.2 table | Re-enter PC's IPv6 config exactly |
| 4 | PC pings its own gateway fine but not a PC on another LAN | `ipv6 unicast-routing` missing on R1, or wrong gateway configured on source/destination PC | `show ipv6 route` on R1 | Add missing command; correct PC gateway |
| 5 | IPv4 stops working after IPv6 config | Accidentally typed an IPv4 command wrong while in the same interface context | `show running-config interface g0/0` | Compare against known-good IPv4 config, correct the stray line |

---

## 10. Design Analysis

- **Why dual-stack instead of a straight cutover to IPv6-only?** A cutover is all-or-nothing risk: every device, every application, every monitoring tool must support IPv6 simultaneously or connectivity breaks. Dual-stack lets IPv4 keep working exactly as before while IPv6 is validated independently — this is why virtually every real-world IPv6 migration (including this lab series' own Day 31→32→33 progression) is dual-stack first, IPv6-only (if ever) years later.
- **Why not translation (NAT64) instead of dual-stack?** NAT64/DNS64 exists for IPv6-only clients that need to reach IPv4-only resources — it's a bridge for a specific asymmetric scenario, not a general strategy, and it adds a translation point that can fail or need scaling. Dual-stack avoids a translation layer entirely by running both protocols natively.
- **Why /64 on every LAN even though 3 PCs "only need" a handful of addresses?** Covered in depth in Section 4.3 — IPv6 address abundance and SLAAC/EUI-64's structural dependency on a 64-bit host portion make sub-/64 LAN subnetting both unnecessary and, in the SLAAC case, actually broken.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...your company's cloud provider (AWS/Azure/GCP) announces IPv6-only pricing tiers or mandates dual-stack VPCs, and someone has to bring the on-prem network up to parity.
- ...a customer or government contract requires proof of IPv6 support before renewal — this exact "enable it on the existing LANs without breaking anything" task is the first deliverable.
- ...a junior engineer asks "why does every device suddenly have two IP addresses?" after a rollout — the FE80 link-local address showing up unexplained in `ipconfig` output is one of the most common first-encounter IPv6 questions in real NOC environments.

---

## 12. Stretch Goal

1. Add a fourth LAN interface with its own /64 and PC, and verify full-mesh IPv6 reachability across all four LANs.
2. Disable IPv4 entirely on one interface (leave IPv6 only) and observe that IPv6 continues to work independently — this previews what an IPv6-only network looks like.
3. Use `show ipv6 interface g0/0` to identify every multicast group the interface has joined, and explain what each one (`FF02::1`, `FF02::2`, `FF02::1:FFxx:xxxx`) is used for.

---

## 13. Self-Assessment

- [ ] Can you state, from memory, the one command that turns a router into an IPv6 router (as opposed to just having IPv6 addresses)?
- [ ] Can you explain why link-local addresses exist on every interface even when you never configured one?
- [ ] Can you compress `2001:0DB8:0000:0001:0000:0000:0000:0002` to its shortest valid form by hand?
- [ ] Can you explain why IPv6 LANs are always /64 while IPv4 LANs are sized to fit host count?
- [ ] Could you configure a PC's dual-stack addressing (both gateways) without looking at Section 6.3?

---

## 14. Key Concepts Demonstrated

- IPv4/IPv6 dual-stack architecture on shared physical interfaces
- Global IPv6 unicast routing enablement
- Global unicast vs link-local address scope
- IPv6 address notation and `::` compression rules
- Nibble-boundary subnetting philosophy vs IPv4 host-bit subnetting

## 15. What I Learned

`ipv6 unicast-routing` is the on-switch for IPv6 forwarding — everything else can be configured perfectly and the router still won't route between LANs without it. Every IPv6-enabled interface always carries a link-local address automatically, completely independent of whether a global address is assigned; this is structurally different from IPv4, which has no equivalent always-on address. The `/64` convention for LANs isn't an arbitrary choice carried over from IPv4 habits — it's a hard dependency for SLAAC and EUI-64 later in this course, and IPv6's address abundance means there's no engineering reason to shrink it the way IPv4 subnetting always does.

## 16. Skills Practiced

- Cisco IOS IPv6 interface configuration
- Global IPv6 routing enablement and verification
- Dual-stack end-host configuration
- IPv6 address notation and compression

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Original device | GNS3 image |
|---|---|---|
| Router (R1) | Cisco router | VyOS |
| Switches (SW1–SW3) | Cisco 2960 | Open vSwitch |
| PCs (PC1–PC3) | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script and the VyOS-equivalent IPv6 commands (VyOS uses `set interfaces ethernet ethN address <prefix>/64` rather than IOS's `ipv6 address`/`ipv6 unicast-routing` pair).
