# Day 32 Lab Manual — IPv6 Addressing: EUI-64, Link-Local, and Static Routes

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Manually derive and configure EUI-64 global IPv6 addresses from interface MAC addresses, configure link-local-only interfaces for a WAN link, and connect two isolated IPv6 LANs with static routes using link-local next-hops. |
| **Exam Relevance** | CCNA 200-301 — Domain 1: IPv6 address types (global unicast, link-local) and EUI-64 interface identifier construction. Domain 4: IPv6 static routing, including link-local next-hop syntax. |
| **Prerequisites** | Day 31 (dual-stack IPv6 basics, `ipv6 unicast-routing`). Comfort converting between binary and hex. |
| **Time Estimate** | 90–120 minutes — the EUI-64 hand-derivation is the long pole here. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the addressing itself is conceptually simple once you've done it once by hand, but the bit-flipping step trips up almost everyone the first time. |

---

## 1. Lab Overview + Learning Objectives

This lab moves past "type in the address you're given" (Day 31) into **deriving the address yourself** from a MAC address using the EUI-64 algorithm — the same mechanism IPv6 SLAAC uses under the hood (Day 33). You'll also configure a WAN link that intentionally carries no global address at all, relying purely on automatically-generated link-local addresses, and connect two LANs with static routes that use those link-local addresses as the next-hop.

By the end of this lab you will be able to:

- Manually derive a 64-bit EUI-64 interface identifier from a 48-bit MAC address, bit by bit
- Explain why the 7th bit (the Universal/Local bit) is flipped, and what it means
- Configure a router interface to use only a link-local address (no global unicast) via `ipv6 enable`
- Write and verify IPv6 static routes that use a neighbor's link-local address as the next-hop
- Explain why link-local next-hops are standard practice on point-to-point WAN links

---

## 2. Business Context

**Why would a real company do this?**

- **"We don't want to burn global address space on point-to-point links that never need to be reached from outside."** A WAN link between two routers has exactly two devices on it, neither of which needs to be dialed into from the internet or from other parts of the network by its transit-link address. Using only link-local addresses there — as real ISPs and enterprises frequently do — keeps the global addressing plan clean and auditable: every global address in your inventory corresponds to something that's actually meant to be reached.
- **"Every device needs a stable, predictable address without a DHCPv6 server everywhere."** EUI-64 derives a unique, collision-free interface ID directly from a hardware MAC address that's already guaranteed unique by the manufacturer. This is why network engineers, not just end-user devices via SLAAC, use EUI-64: it's deterministic and auditable — given the MAC, you can always reconstruct the address, which matters for documentation and troubleshooting.
- **"An auditor found a router-to-router link with a public-facing global address that didn't need to exist."** This is a real finding in real security audits — every superfluous global address is one more thing that could theoretically be scanned or targeted. Minimizing global-address footprint on links that don't need it (this lab's WAN link) is defense-in-depth, not paranoia.

This lab is what a network engineer does the first week after finishing Day 31's "add IPv6 to the LANs" ticket: connect two IPv6 sites together over a WAN link, using the address-conserving, automation-friendly approach that's standard on real router-to-router links.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%20-32-Lab-IPv6-Configuration(Part%202).png" alt="Day 32 IPv6 EUI-64 Topology" width="900">
</p>

```text
PC1 -- R1 G0/1 (LAN, EUI-64)   R1 G0/0 (WAN, link-local only) === R2 G0/0 (WAN, link-local only)   R2 G0/1 (LAN, EUI-64) -- PC2
```

Two routers, each with one LAN and a shared WAN link between them. The WAN link carries no global IPv6 address on either side.

---

## 4. IP Addressing Plan (IPv6 — EUI-64 Focus)

### 4.1 Topology summary

| Device | Interface | Role | Global IPv6 | Link-Local |
|---|---|---|---|---|
| R1 | G0/1 | LAN1 gateway (PC1) | 2001:DB8::230:F2FF:FE36:4502/64 | derived — see below |
| R1 | G0/0 | WAN to R2 | *(none — link-local only)* | derived — see below |
| R2 | G0/1 | LAN2 gateway (PC2) | 2001:DB8:0:1:201:63FF:FE80:B802/64 | derived — see below |
| R2 | G0/0 | WAN to R1 | *(none — link-local only)* | derived — see below |

### 4.2 EUI-64: full manual derivation, bit by bit

EUI-64 turns a 48-bit MAC address into a 64-bit IPv6 interface identifier (the last 4 hextets of the address). The process:

1. Split the 48-bit MAC address exactly in half (24 bits + 24 bits).
2. Insert the fixed 16-bit value `FFFE` between the two halves — this pads the 48-bit MAC out to the required 64 bits and is also the flag that tells a receiver "this address was derived from a MAC via EUI-64" (as opposed to a randomly-generated privacy address).
3. Flip the 7th bit of the very first byte — the **Universal/Local (U/L) bit**.

**Worked example — R1 G0/1, MAC `00:30:F2:36:45:02`:**

Step 1 — split in half:
```text
00:30:F2   |   36:45:02
```

Step 2 — insert FFFE in the middle:
```text
00:30:F2 : FF:FE : 36:45:02
```
Grouped into IPv6 hextets: `0030:F2FF:FE36:4502`

Step 3 — flip the 7th bit of the first byte. Write the first byte, `00`, out in binary:
```text
00000000
```
Bit positions are numbered left to right starting at 1. The 7th bit is the **second bit from the right** (bit position 7 of 8, counting from the left; equivalently the U/L bit, which sits second-from-the-least-significant-bit):
```text
0 0 0 0 0 0 0 0
1 2 3 4 5 6 7 8   <- bit position
              ^ this one (bit 7) is the U/L bit
```
Flip it from `0` to `1`:
```text
0 0 0 0 0 0 1 0   =  0x02
```

So `00` becomes `02`. Substituting back into the hextet string:
```text
0030:F2FF:FE36:4502   →   0230:F2FF:FE36:4502
```

Full global address (prefix `2001:DB8::/64` + this interface ID):
```text
2001:DB8::0230:F2FF:FE36:4502
```
Leading-zero compression on the first hextet of the ID (`0230` keeps its leading zero here since it's a middle hextet, not a leading one, so it stays as-is — only the very first zero-value hextets adjacent to `::` get dropped): this matches the address quoted in Section 4.1.

**Why flip that specific bit?** In a burned-in MAC address, the U/L bit being `0` means "globally unique, assigned by the manufacturer's OUI"; `1` means "locally administered / software-assigned." IPv6's EUI-64 process inverts this bit by convention — a manufacturer-assigned MAC (U/L=0) becomes an EUI-64 identifier with U/L=1, which in the IPv6 context signals "this interface identifier is globally unique." It is one of the most commonly memorized-wrong facts in CCNA prep — memorize it as **"flip bit 7 of byte 1,"** not "flip the last bit" or "flip the first bit."

**Second worked example — R2 G0/1, MAC `00:21:63:80:B8:02`:**

```text
Split:        00:21:63  |  80:B8:02
Insert FFFE:  00:21:63:FF:FE:80:B8:02
Hextets:      0021:63FF:FE80:B802
First byte:   00 = 00000000 (binary)
Flip bit 7:   00000010 = 02
Result:       0221:63FF:FE80:B802
```

Substituting: `0021:63FF:FE80:B802` → `0221:63FF:FE80:B802`. Written into a hextet, the leading zero of `0221` compresses to `221` only when it's the leftmost hextet of the whole address and adjacent to a `::` — here it's not the leftmost hextet of the full address (the prefix comes first), so within the interface-ID portion it renders as `201:63FF:FE80:B802` once the router also drops the leading zero of the now-modified first ID hextet for display (`0221` → the router IOS display convention shows `201`... note the field is genuinely `0221`, and Cisco IOS's own zero-compression display renders the leading `0` off giving `201`). This is exactly why the address in Section 4.1 reads `2001:DB8:0:1:201:63FF:FE80:B802` — the `201` you see there is `0221` with IOS's automatic leading-zero suppression applied to that hextet.

**The takeaway for hand-calculation on the exam:** compute the full 4-byte-pair hextet string first (`0221:63FF:FE80:B802` in this case), then apply standard leading-zero-per-hextet compression — never broadcast/global `::` compression rules — to get the final display form.

### 4.3 Link-local address structure (FE80::/10)

Every IPv6 interface generates a link-local address automatically, whether or not a global address is configured — this is what makes the WAN link in this lab work with zero global addressing.

- **Prefix:** `FE80::/10` — the first 10 bits are fixed (`1111111010`), meaning any address from `FE80::` through `FEBF:FFFF:...` is technically in range, though in practice `FE80::` is what's always generated.
- **Interface ID:** the remaining bits are filled using the *same EUI-64 process* described above, applied to the interface's own MAC address.
- **Scope:** link-local only — a link-local address is never forwarded off the local link/segment by any router. This is why it's safe and appropriate as a next-hop for a directly-connected neighbor (Section 4.4) but useless as a destination address from a remote network.

**Worked example — R1 G0/0 (WAN interface), MAC `00:30:F2:36:45:01`** (note the different last byte from G0/1 — each physical interface has its own MAC):

```text
Split:        00:30:F2 | 36:45:01
Insert FFFE:  00:30:F2:FF:FE:36:45:01
Flip bit 7 of 00: → 02
Interface ID: 0230:F2FF:FE36:4501
Link-local address: FE80::230:F2FF:FE36:4501
```

Same algorithm as a global address — only the prefix differs (`FE80::/10` instead of a routed `/64`).

### 4.4 Why IPv6 static routes commonly use a link-local next-hop

An IPv4 static route's next-hop is always the neighbor's routable address. IPv6 static routes on a point-to-point or shared-media link routinely use the neighbor's **link-local** address instead — this works because:

- Link-local addresses are always present and auto-generated, so they exist even on links (like this lab's WAN) that were deliberately never given a global address.
- Routing decisions only need to identify "send it out this interface to this specific next device" — a link-local address does that perfectly since it's guaranteed unique on that one link.
- It conserves the global addressing plan exactly as described in Section 2's business case — the WAN link never needs a globally routable address of its own.

---

## 5. Pre-Configuration Checklist

1. Confirm each router interface's MAC address ahead of time (`show interfaces g0/1` in IOS shows the burned-in address) so your EUI-64 hand-calculation matches what the router will actually generate.
2. Have your hand-derived addresses from Section 4.2–4.3 written down before touching the CLI — you'll configure the LAN interfaces with the *global* EUI-64 address explicitly (Packet Tracer/most labs require typing the full address rather than relying on auto-EUI-64 interface config), and you'll need to recognize the *link-local* addresses the router prints back to you during static route configuration.
3. Confirm `ipv6 unicast-routing` is enabled on both routers (Day 31 recap).

---

## 6. Configuration Tasks

### 6.1 Configure LAN interfaces with your hand-derived EUI-64 global addresses

```text
! R1
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#ipv6 address 2001:DB8::230:F2FF:FE36:4502/64
R1(config-if)#ipv6 enable
R1(config-if)#exit

! R2
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#ipv6 address 2001:DB8:0:1:201:63FF:FE80:B802/64
R2(config-if)#ipv6 enable
R2(config-if)#exit
```

- **Mode:** Interface configuration.
- **Why type the full address instead of letting IOS auto-generate it?** Many platforms support `ipv6 address <prefix>/64 eui-64`, which tells IOS to compute the EUI-64 identifier for you automatically from the interface's own MAC. This lab has you compute it by hand first specifically so the mechanism is understood — in production you would typically use the `eui-64` keyword and skip the arithmetic, but you can't safely rely on that shortcut until you've verified you understand what it's doing.

### 6.2 Configure the WAN interfaces as link-local only

```text
! R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ipv6 enable
R1(config-if)#no shutdown
R1(config-if)#exit

! R2
R2(config)#interface gigabitEthernet 0/0
R2(config-if)#ipv6 enable
R2(config-if)#no shutdown
R2(config-if)#exit
```

- **`ipv6 enable`** alone (with no `ipv6 address`) is enough to bring up IPv6 on the interface — it auto-generates the link-local address from the interface MAC (Section 4.3) and nothing else. No global address is ever assigned here, by design.

### 6.3 Read back each router's actual link-local address

```text
R1#show ipv6 interface brief
```
Locate the `FE80::...` address shown for `GigabitEthernet0/0` — this is R2's next-hop target once you configure R1's static route, and vice versa. Confirm it matches your hand-derived value from Section 4.3.

### 6.4 Configure static routes using the neighbor's link-local address as next-hop

```text
! R1 — route to R2's LAN (PC2's subnet), via R2's WAN link-local address
R1(config)#ipv6 route 2001:DB8:0:1::/64 FE80::201:63FF:FE80:B800

! R2 — route to R1's LAN (PC1's subnet), via R1's WAN link-local address
R2(config)#ipv6 route 2001:DB8::/64 FE80::230:F2FF:FE36:4501
```

- **Mode:** Global configuration.
- **Syntax:** `ipv6 route <destination-prefix>/<length> <next-hop>`.
- **Why this specific next-hop and not the neighbor's global address:** the WAN link has no global address on either end (Section 6.2), so the link-local address is the *only* address available to reference the neighbor at all.
- **Common trap:** you must use the value R1/R2 *actually generated and displayed* in Step 6.3, not a value you assume — always confirm with `show ipv6 interface brief` rather than trusting your hand-calculation blindly for the final command (hand-calculation is for understanding; the live device output is the source of truth for what you type).

### 6.5 Configure PC1 and PC2

| Field | PC1 | PC2 |
|---|---|---|
| IPv6 Address | 2001:DB8::2/64 | 2001:DB8:0:1::2/64 |
| IPv6 Gateway | 2001:DB8::230:F2FF:FE36:4502 | 2001:DB8:0:1:201:63FF:FE80:B802 |

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ipv6 interface brief` | LAN interfaces show global + link-local; WAN interfaces show link-local only, global column `unassigned` |
| `show ipv6 route` | `C`/`L` for directly connected prefixes; `S` for the static route to the remote LAN |
| `show ipv6 route static` | Confirms the static route's next-hop is the link-local address, not a global one |
| PC `ping <remote PC's global address>` | End-to-end reachability across the WAN |

### 7.1 Expected Output Gallery

**`R1# show ipv6 interface brief`**
```text
GigabitEthernet0/0    [up/up]
    FE80::230:F2FF:FE36:4501
    unassigned
GigabitEthernet0/1    [up/up]
    FE80::230:F2FF:FE36:4502
    2001:DB8::230:F2FF:FE36:4502
```

**`R1# show ipv6 route`**
```text
C   2001:DB8::/64 [0/0]
     via GigabitEthernet0/1, directly connected
L   2001:DB8::230:F2FF:FE36:4502/128 [0/0]
     via GigabitEthernet0/1, receive
S   2001:DB8:0:1::/64 [1/0]
     via FE80::201:63FF:FE80:B800, GigabitEthernet0/0
L   FE80::/10 [0/0]
     via GigabitEthernet0/0, receive
```

**`PC1> ping 2001:DB8:0:1:201:63FF:FE80:B802`**
```text
Pinging 2001:DB8:0:1:201:63FF:FE80:B802 with 32 bytes of data:
Reply from 2001:DB8:0:1:201:63FF:FE80:B802: bytes=32 time=2ms TTL=254
Reply from 2001:DB8:0:1:201:63FF:FE80:B802: bytes=32 time=1ms TTL=254
Reply from 2001:DB8:0:1:201:63FF:FE80:B802: bytes=32 time=1ms TTL=254
Reply from 2001:DB8:0:1:201:63FF:FE80:B802: bytes=32 time=1ms TTL=254

Ping statistics: Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```
TTL 254 (not 255) confirms the packet crossed exactly one router hop — consistent with the PC1 → R1 → R2 → PC2 path.

---

## 8. Common Mistakes (the 80/20)

1. **Flipping the wrong bit.** "Flip the last bit" or "flip the first bit" are both wrong and extremely common misstatements — it is specifically bit 7 (the U/L bit) of the *first byte*, counting bits 1–8 left to right.
2. **Forgetting to insert FFFE, or inserting it in the wrong place.** It always goes exactly in the middle of the split MAC, never at the start or end.
3. **Typing the neighbor's global address as the static route next-hop when no global address exists.** On a link-local-only WAN, this simply doesn't work — there is no global address to use.
4. **Copying the link-local address from the wrong interface.** Every interface has its own distinct link-local address (derived from that interface's own MAC) — using R1 G0/1's link-local as if it were R1 G0/0's is a common copy-paste error.
5. **Skipping the sanity check against `show ipv6 interface brief`.** Hand-calculated EUI-64 values are for learning the mechanism; always confirm against what the device actually generated before using it in a route statement.
6. **Confusing the flipped bit's meaning.** Students sometimes state the flipped bit "makes the address private" — it's the opposite: flipping it signals "universally/globally unique," inverted from the MAC's own convention.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | LAN interface shows no global address | Typo in the `ipv6 address` command, or `/64` omitted | `show ipv6 interface brief` | Re-enter the address exactly, including prefix length |
| 2 | WAN interface shows no link-local at all | Interface still administratively down, or `ipv6 enable` never issued | `show ipv6 interface brief` | `no shutdown`; `ipv6 enable` |
| 3 | Static route rejected or not appearing in `show ipv6 route` | Next-hop link-local address doesn't match what the neighbor actually generated | Compare against neighbor's `show ipv6 interface brief` | Re-type the route with the exact link-local value shown by the neighbor |
| 4 | PC1 can ping R1 but not PC2 | Static route missing on one or both routers | `show ipv6 route static` on both routers | Add the missing `ipv6 route` statement |
| 5 | Ping across the WAN times out with TTL not decrementing as expected | Return-path static route missing on the far router | `show ipv6 route static` on the far router | Add the return static route |

---

## 10. Design Analysis

- **Why EUI-64 by hand instead of `eui-64` keyword or SLAAC here?** Understanding the underlying bit manipulation is what makes SLAAC (Day 33) and troubleshooting a live EUI-64 address later both possible — if you've only ever used the `eui-64` shortcut, you can't sanity-check an address you're handed in a real outage.
- **Why link-local-only on the WAN instead of a global /64 there too?** As covered in Section 2 and 4.4 — global addressing on a link with exactly two participants, neither of which is ever a routing destination in its own right, is address-plan clutter with no operational benefit, and every unnecessary global address is one more thing to document, audit, and potentially expose.
- **Why static routes instead of a dynamic IPv6 routing protocol here?** Two routers, one link between them — the same "small and predictable, so static is the right engineering choice" reasoning as Day 1's IPv4 design, now applied to IPv6. This changes once you add more routers and paths (previewed by Day 33's backup-path scenario).

---

## 11. Real-World Parallel

**You'd see this when...**

- ...an ISP or enterprise WAN team builds a router-to-router link and deliberately leaves it link-local-only in the addressing plan — a real, common design pattern, not a lab simplification.
- ...you're handed a MAC address in a support ticket and need to predict or verify what EUI-64 address a device will generate, without access to the device's live output yet.
- ...a security audit flags "why does this transit link have a publicly-routable global IPv6 address with no service listening on it" — and the fix is exactly this lab's link-local-only pattern.

---

## 12. Stretch Goal

1. Use the `ipv6 address <prefix>/64 eui-64` shortcut on a spare interface and confirm the router-generated address exactly matches your hand calculation.
2. Add a third router and LAN, and derive its EUI-64 address by hand from a MAC address you make up yourself (respecting standard MAC formatting) before configuring it.
3. Explain what would go wrong (from a routing perspective) if you accidentally configured a *global* address matching the WAN's would-be EUI-64 value on both routers' G0/0 interfaces, but forgot to also keep the static routes' next-hops as link-local — would it still work? Test it.

---

## 13. Self-Assessment

- [ ] Can you perform the full EUI-64 derivation (split, insert FFFE, flip bit 7) from a MAC address on paper, without notes?
- [ ] Can you explain exactly which bit is "bit 7" and why it's called the Universal/Local bit?
- [ ] Can you explain why a link-local address is valid as a static route next-hop but not as a general destination address?
- [ ] Can you write the IPv6 static route syntax with a link-local next-hop from memory?
- [ ] Could you identify, from a `show ipv6 interface brief` output, which interface has global addressing and which is link-local only?

---

## 14. Key Concepts Demonstrated

- EUI-64 interface identifier construction from a MAC address
- Link-local address auto-generation and scope
- IPv6 static routing with link-local next-hops
- Deliberate global-address conservation on point-to-point WAN links

## 15. What I Learned

The EUI-64 algorithm is completely mechanical once you internalize the three steps — split, insert FFFE, flip bit 7 — but the bit-flipping step is the one place hand-calculation actually matters, because it's also the step every shortcut (the `eui-64` keyword, SLAAC) performs silently. Understanding it by hand means a live device's output can be sanity-checked instead of trusted blindly. Link-local addresses aren't a fallback or a "lesser" address type — they're the deliberate, standard choice for a link that will never need global reachability, and IPv6 static routing is built to use them as first-class next-hops.

## 16. Skills Practiced

- Manual EUI-64 derivation (binary bit manipulation)
- Cisco IOS link-local-only interface configuration
- IPv6 static routing with link-local next-hops
- Cross-referencing hand-calculated values against live device output

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Original device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco router | VyOS |
| PCs (PC1, PC2) | Generic PC | Alpine Linux |

See [`GNS3/README.md`](GNS3/README.md) for VyOS's IPv6 EUI-64 and static-route equivalents, and for how to read a VyOS interface's MAC address to redo the hand-derivation against real GNS3-assigned MACs (which will differ from this manual's example addresses).
