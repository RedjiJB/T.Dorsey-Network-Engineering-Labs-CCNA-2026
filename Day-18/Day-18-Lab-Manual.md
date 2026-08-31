# Day 18 Lab Manual — Multilayer Switching: SVIs and Inter-VLAN Routing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Replace a Router-on-a-Stick (ROAS) inter-VLAN routing design with a true Layer 3 multilayer-switch design: a routed point-to-point uplink between the distribution switch and the edge router, Switched Virtual Interfaces (SVIs) for each VLAN, and IP routing enabled directly on the switch. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): VLANs, trunking, Layer 2 vs. Layer 3 forwarding. Domain 2 (Network Access): SVI configuration, `no switchport`, trunk configuration. Domain 4 (IP Connectivity): routing table interpretation, static/default routes, inter-VLAN routing concepts (this is one of the most heavily tested topics on the exam). |
| **Prerequisites** | Day 17 (Router-on-a-Stick / trunking) completed and understood — this lab explicitly replaces that design, so you should know what ROAS looked like before you dismantle it. Subnetting fundamentals (this lab reuses a single `/24` split into three `/26` VLANs plus a `/30` transit link). Comfort with basic IOS interface and VLAN configuration. |
| **Time Estimate** | 1.5 – 2.5 hours (first attempt); 30–45 minutes on repeat/review. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the commands themselves are short, but the conceptual shift (a switch now routes) trips up students who have only ever thought of switches as Layer 2 devices. |

---

## 1. Lab Overview

Up through Day 17, inter-VLAN routing in this course was done with **Router-on-a-Stick (ROAS)**: a single physical router interface, carved into subinterfaces with `encapsulation dot1Q`, doing all the routing work while the switch stayed strictly Layer 2. That design works, but it has a structural weakness — every packet that moves between VLANs has to leave the switch, cross the trunk, get routed by the router, and come back across the same trunk. On a busy access-layer switch, that trunk becomes a bottleneck, and the router becomes a single point of failure for traffic that never actually needed to leave the building.

Today's lab replaces that design with **multilayer switching**: SW2 (a Catalyst 3650, a device that can do both Layer 2 switching *and* Layer 3 routing) gets **Switched Virtual Interfaces (SVIs)** — one per VLAN — and takes over the inter-VLAN routing job itself. The only thing that still needs an external router is traffic leaving the building entirely (the internet), which now travels over a dedicated **routed point-to-point link** between SW2 and R1, instead of a trunk carrying tagged VLAN traffic.

This is one of the most important conceptual shifts in the entire CCNA syllabus: understanding *when* a switch is "just" doing Layer 2 forwarding and *when* it is acting as a router with switch ports attached to it.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain the structural difference between Router-on-a-Stick and SVI-based multilayer switching, including why the second scales better
- Convert a switch access/trunk port into a routed Layer 3 port using `no switchport`
- Configure a routed point-to-point link between a switch and a router
- Create and configure SVIs for multiple VLANs, and explain why an SVI needs at least one active port in that VLAN to come up
- Enable IP routing on a Layer 3 switch and explain why this step is easy to forget
- Perform host-bit math to derive VLAN subnet boundaries and SVI addresses by hand
- Verify inter-VLAN and internet connectivity through a multilayer switch, and read the resulting routing table correctly
- Compare ROAS and multilayer switching design trade-offs in business/engineering terms

---

## 2. Business Context

**Why would a real company do this?**

Picture the same company from earlier labs, a few months further along. The Day 17 ROAS design worked for the pilot office, but now IT leadership has a new set of complaints and requirements coming out of a capacity-planning review:

- **"Inter-department traffic between Sales (VLAN10), Engineering (VLAN20), and Ops (VLAN30) feels slow during business hours"** → In ROAS, *every* inter-VLAN packet — even between two departments sitting on the same switch — has to traverse the trunk to the router and back. As headcount and VLAN-to-VLAN chatter (file shares, print traffic, internal apps) grows, that round trip adds latency and eats trunk bandwidth that should be reserved for traffic that's actually leaving the building.
- **"We just bought a Catalyst 3650 — are we using its full capability?"** → A 3650 is a multilayer switch; running it in pure Layer 2 mode (as Day 17 effectively did, treating it as a dumb trunk endpoint) wastes hardware you already paid for. This lab puts that capability to work.
- **"If the router goes down, departments still on the same switch should be able to talk to each other"** → With SVI-based routing, inter-VLAN traffic no longer depends on R1 at all. R1 becomes relevant only for internet-bound traffic — a router outage now degrades *internet access*, not *internal* department-to-department communication. This is a real resilience improvement, not just a performance one.
- **"We want a cleaner boundary between 'internal routing' and 'internet edge' in our design"** → replacing the trunk-to-router link with a single routed point-to-point link mirrors how real distribution/core layers connect to edge routers: a dedicated, minimal, purpose-built link, not a general-purpose trunk doing double duty.

This is exactly the kind of redesign a network engineer performs when a company outgrows its pilot topology: not because the old design was *wrong*, but because it was a reasonable first step that a growing network needs to graduate past.

---

## 3. Topology Reference

<p align="center">
  <a href="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-18-Lab-Multilayer%20Switching.pkt.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-18-Lab-Multilayer%20Switching.pkt.png" alt="Day 18 Multilayer Switching Lab Topology" width="900">
  </a>
</p>

### 3.1 Traffic Flow Summary

```text
END HOSTS (VLAN10 / VLAN20 / VLAN30)
PC1..PC7 -- SW1 (L2 access/distribution) == trunk == SW2 (L3 multilayer switch, SVIs route between VLANs)

INTERNET EDGE
SW2 -- (routed point-to-point, no switchport) -- R1 -- Internet cloud
```

Inter-VLAN traffic (e.g., PC on VLAN10 to PC on VLAN20) never leaves SW2 — it enters one SVI and exits another, entirely inside the multilayer switch. Only traffic destined off the `10.0.0.0/24` block crosses the point-to-point link to R1.

### 3.2 Equipment List

| Device | Model | Role | Hostname Used Below |
|---|---|---|---|
| R1 | Cisco 2911 | Internet edge router | `R1` |
| SW1 | Cisco 2960-24TT | Access switch (Layer 2 only, trunks to SW2) | `SW1` |
| SW2 | Cisco 3650-24PS | Multilayer switch (Layer 3 — SVIs + routed uplink) | `SW2` |
| PC1–PC7 | Generic PC | End hosts distributed across VLAN10/20/30 | `PC1`–`PC7` |

> **Note on scope:** VLAN creation and trunk configuration between SW1 and SW2 were completed in prior days (Day 16/17) and are assumed already in place. This lab's CLI work is scoped to what changes: R1's interface, SW2's uplink port, SW2's SVIs, SW2's routing, and verification. If your SW1↔SW2 trunk isn't already up, confirm it (`show interfaces trunk`) before starting Step 1.

---

## 4. IP Addressing Plan

This lab reuses the `10.0.0.0/24` block from Day 17, split into three VLAN subnets plus one new point-to-point transit link between SW2 and R1. Because SVIs sit at the *end* of each VLAN subnet in this design (the last usable address, not the first), addressing accuracy matters more than usual — get the SVI address wrong and every host in that VLAN loses its gateway.

### 4.1 Full Subnet Table

| Segment | Network | Mask | Usable Range | Gateway (SVI) |
|---|---|---|---|---|
| VLAN10 (e.g., Sales) | 10.0.0.0/26 | 255.255.255.192 | .1 – .62 | 10.0.0.62 |
| VLAN20 (e.g., Engineering) | 10.0.0.64/26 | 255.255.255.192 | .65 – .126 | 10.0.0.126 |
| VLAN30 (e.g., Ops) | 10.0.0.128/26 | 255.255.255.192 | .129 – .190 | 10.0.0.190 |
| SW2 ↔ R1 transit | 10.0.0.192/30 | 255.255.255.252 | .193 – .194 | n/a (point-to-point) |

### 4.2 Why Sized This Way

- **Three `/26` VLANs instead of three `/24`s.** The original `10.0.0.0/24` block only has 254 usable addresses total — splitting it into three separate `/24`s per VLAN was never on the table; the whole block *is* the budget. A `/26` gives 62 usable hosts per VLAN, which comfortably covers a department-sized user population with headroom, while still leaving room in the same `/24` for two more VLANs and a `/30` transit link. This is the same "smallest block that covers the requirement plus reasonable growth" rule used in every subnetting decision in this course.
- **The `/30` transit link.** SW2 ↔ R1 is a point-to-point link between exactly two Layer 3 interfaces — it will never have a third device. A `/30` gives exactly 2 usable addresses, matching that requirement with zero waste, exactly like every router-to-router transit link in prior labs.
- **The SVI sits on the *last* usable address, not the first.** This is a deliberate convention choice for this lab (some organizations put the gateway on the first usable address instead — both are valid, but a network must be *consistent*). Putting the gateway at the top of the range keeps low addresses free for statically-addressed infrastructure (printers, servers) without renumbering the gateway later, and it demonstrates that "gateway = first host address" is a convention, not a protocol requirement — nothing in IPv4 mandates it.

### 4.3 Manual Calculation Walkthrough — VLAN10 (10.0.0.0/26)

**Step 1 — Confirm the host-bit count for a /26.**

```text
/26 = 11111111.11111111.11111111.11000000
```

24 network bits from the first three octets, plus 2 more network bits in the last octet (the leading `11`), leaves **6 host bits** in the last octet.

**Step 2 — Derive usable host count from host bits.**

```text
usable hosts = 2^h − 2 = 2^6 − 2 = 64 − 2 = 62
```

62 usable addresses — matches the table above.

**Step 3 — Convert the mask to dotted decimal.**

```text
11000000 (binary) = 128 + 64 = 192 (decimal)
```

So `/26` → last octet mask value `192` → full mask `255.255.255.192`.

**Step 4 — Identify block size and boundaries.**

```text
block size = 256 − 192 = 64
```

`/26` subnets always land on multiples of 64: `.0, .64, .128, .192`. This is exactly why VLAN10/20/30 start at `.0`, `.64`, `.128` — each one snaps cleanly to the next `/26` block boundary, and `.192` is left over for the transit link.

**Step 5 — Network, first host, last host, broadcast for VLAN10 (10.0.0.0/26).**

```text
Network address:    10.0.0.0     (all 6 host bits = 000000)
First usable host:  10.0.0.1     (network address + 1)
Last usable host:   10.0.0.62    (broadcast address − 1, i.e., network + 62)
Broadcast address:  10.0.0.63    (all 6 host bits = 111111 → 0 + 63)
```

The SVI address `10.0.0.62` is exactly the **last usable host** in this block — confirm this matches Step 2's configuration below before moving on.

### 4.4 Manual Calculation Walkthrough — Transit Link (10.0.0.192/30)

**Step 1 — Host bits for /30.**

```text
/30 = 11111111.11111111.11111111.111111 00  → 2 host bits
usable hosts = 2^2 − 2 = 2
```

**Step 2 — Mask in decimal.**

```text
11111100 = 128+64+32+16+8+4 = 252 → 255.255.255.252
```

**Step 3 — Block size and boundary.**

```text
block size = 256 − 252 = 4
```

`/30` blocks land on multiples of 4. `.192` is a clean multiple of 4 (`192 ÷ 4 = 48`), which is why the transit link starts there — it's the block immediately after VLAN30's `/26` ends (`.128` through `.191`), with no wasted or overlapping space.

**Step 4 — Network, hosts, broadcast.**

```text
Network address:    10.0.0.192
First usable host:  10.0.0.193   (assigned to SW2, the switch side)
Last usable host:   10.0.0.194   (assigned to R1, the router side)
Broadcast address:  10.0.0.195
```

### 4.5 VLAN20 and VLAN30 — Quick-Check Table

Use the same 5-step process above to verify these yourself before configuring; answers given for self-check:

| VLAN | Network | Host bits | Usable | First host | Last host (SVI) | Broadcast |
|---|---|---|---|---|---|---|
| VLAN20 | 10.0.0.64/26 | 6 | 62 | 10.0.0.65 | **10.0.0.126** | 10.0.0.127 |
| VLAN30 | 10.0.0.128/26 | 6 | 62 | 10.0.0.129 | **10.0.0.190** | 10.0.0.191 |

**Memory aid:** for any `/26`, the block size is always 64 and the last usable host is always `(block start + 62)`. Once you've derived one `/26` by hand, the other two are pure arithmetic — you don't need to re-derive the binary every time, but you should be able to if asked on the exam.

### 4.6 Full Device Address Table

| Device | Interface | IP Address | Mask | Connects To |
|---|---|---|---|---|
| R1 | G0/0 | 10.0.0.194 | 255.255.255.252 | SW2 G1/0/2 |
| SW2 | G1/0/2 (routed, `no switchport`) | 10.0.0.193 | 255.255.255.252 | R1 G0/0 |
| SW2 | VLAN10 SVI | 10.0.0.62 | 255.255.255.192 | n/a (internal) |
| SW2 | VLAN20 SVI | 10.0.0.126 | 255.255.255.192 | n/a (internal) |
| SW2 | VLAN30 SVI | 10.0.0.190 | 255.255.255.192 | n/a (internal) |
| PC1–PC7 | NIC | per VLAN, from usable range above | matches VLAN mask | SW1 access ports |

**Default gateways:** every host on VLAN10 → `10.0.0.62`; VLAN20 → `10.0.0.126`; VLAN30 → `10.0.0.190`.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Confirm Day 17's VLANs (10, 20, 30) already exist on SW2 and hosts are correctly assigned via SW1's access ports — this lab does not recreate them.
2. Confirm the SW1 ↔ SW2 trunk is up (`show interfaces trunk` on either switch) — SVIs depend on VLAN traffic actually reaching SW2.
3. Locate R1's current ROAS configuration (`show running-config interface g0/0` and any subinterfaces) so you know exactly what to remove in Step 1.
4. Have the addressing table above open in a second window.
5. Confirm SW2 is a Layer 3-capable model (3650 series) — a plain 2960 **cannot** do SVI routing no matter how it's configured; this distinction matters and is revisited in Section 10.

---

## 6. Configuration Tasks

### 6.1 Step 1 — Replace ROAS with a Routed Point-to-Point Link

#### 6.1.1 Router side (R1) — remove subinterfaces, configure the physical interface

```text
R1(config)# no interface g0/0.10
R1(config)# no interface g0/0.20
R1(config)# no interface g0/0.30
R1(config)# interface g0/0
R1(config-if)# ip address 10.0.0.194 255.255.255.252
R1(config-if)# no shutdown
```

- **Mode:** Global Config → Interface Config.
- The `no interface g0/0.X` commands delete each ROAS subinterface entirely — you cannot simply leave them configured alongside the new physical-interface IP, because a subinterface and its parent physical interface cannot both carry conflicting Layer 3 configuration for the same physical port in a way that makes sense here; ROAS is being fully retired on this link, not layered underneath the new design.
- Assigning the IP **directly to the physical interface** (not a subinterface) is what makes this a true point-to-point Layer 3 link instead of a trunk — there's no `encapsulation dot1Q` here because there's no VLAN tagging on this link at all; it only ever carries traffic between two directly-connected routed interfaces.
- **Memory aid:** ROAS = "one physical wire, many logical subinterfaces, router does all VLAN math." This step deletes the "many logical subinterfaces" half entirely.

#### 6.1.2 Switch side (SW2) — convert the uplink port to Layer 3

```text
SW2(config)# interface g1/0/2
SW2(config-if)# no switchport
SW2(config-if)# ip address 10.0.0.193 255.255.255.252
SW2(config-if)# no shutdown
```

- **`no switchport`** is the single command that converts a port from a Layer 2 switchport (which forwards frames based on MAC address and VLAN membership) into a **routed port** (which behaves exactly like a router interface — it can hold an IP address and participate in the routing table). Without this command, `ip address` on a switch physical interface is rejected — switchports don't take Layer 3 addresses.
- **Memory aid:** `no switchport` = "stop being a switch port, start being a router port." It's the mirror image of what you'd do on a router if it had a built-in switch module (rare, but conceptually the same toggle).
- This port now behaves identically to R1's G0/0 — two routed interfaces, directly connected, no VLAN tagging, no trunk.

#### 6.1.3 Enable IP routing on SW2

```text
SW2(config)# ip routing
```

- **This is the single most commonly forgotten command in this entire lab.** A Catalyst 3650 ships with IP routing globally **disabled by default** on many IOS/IOS-XE builds, even though the hardware fully supports it. Without `ip routing`, SVIs will still show `up/up` and even hold correct IP addresses, but the switch will **not** route packets between them — it will silently behave as if it were still Layer 2-only.
- **Memory aid:** SVIs give a switch the *addresses* to route with; `ip routing` gives it *permission* to actually route. Both are required — one without the other looks like it should work and doesn't.

#### 6.1.4 Default route on SW2

```text
SW2(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.194
```

- **Mode:** Global Config.
- Any destination not covered by a directly-connected VLAN subnet or the transit link gets forwarded to R1 (`10.0.0.194`) — this is what gives internet-bound traffic from any VLAN a path off the local network. Note this route lives on the **switch**, not the router — SW2 is now the device making the internal-vs-external routing decision for every VLAN, which is the core behavioral shift of this lab.

**Verification after Step 1:**

```text
SW2# show ip route

Gateway of last resort is 10.0.0.194 to network 0.0.0.0

C    10.0.0.192/30 is directly connected, GigabitEthernet1/0/2
S*   0.0.0.0/0 [1/0] via 10.0.0.194
```

At this point only the transit link and the default route appear — the VLAN subnets aren't in the routing table yet because their SVIs don't exist until Step 2.

### 6.2 Step 2 — Configure SVIs on SW2

```text
SW2(config)# interface vlan 10
SW2(config-if)# ip address 10.0.0.62 255.255.255.192
SW2(config-if)# no shutdown
SW2(config-if)# exit

SW2(config)# interface vlan 20
SW2(config-if)# ip address 10.0.0.126 255.255.255.192
SW2(config-if)# no shutdown
SW2(config-if)# exit

SW2(config)# interface vlan 30
SW2(config-if)# ip address 10.0.0.190 255.255.255.192
SW2(config-if)# no shutdown
SW2(config-if)# exit
```

- **`interface vlan X`** creates (or enters) the SVI for that VLAN — a *virtual* interface, not tied to any single physical port. It exists as long as VLAN X is defined on the switch, but it only comes **up/up** once at least one physical port that's a member of VLAN X is also up — an SVI has nothing to route for if the VLAN has no live ports, so IOS holds it down as a sanity check.
- Each SVI gets the **last usable address** in its `/26`, per the addressing plan in Section 4 — double-check these three IPs against your own math before moving on, since a typo here breaks every host's gateway in that VLAN.
- **Memory aid:** think of each SVI as "the router's LAN interface for that VLAN, except the router happens to be built into the switch." Every command here is identical in *form* to configuring a router's physical LAN interface — only the interface type (`vlan X` instead of `gigabitEthernet 0/0`) is different.
- No `no switchport` is needed here — SVIs are virtual Layer 3 interfaces by definition; that command only applies to *physical* switchports being converted to routed ports (as in Step 1.2).

**Verification after Step 2:**

```text
SW2# show ip route

Gateway of last resort is 10.0.0.194 to network 0.0.0.0

C    10.0.0.0/26 is directly connected, Vlan10
C    10.0.0.64/26 is directly connected, Vlan20
C    10.0.0.128/26 is directly connected, Vlan30
C    10.0.0.192/30 is directly connected, GigabitEthernet1/0/2
S*   0.0.0.0/0 [1/0] via 10.0.0.194
```

All three VLAN subnets now appear as directly connected — this is what makes inter-VLAN routing possible: SW2 has a route to every VLAN because it *is* the gateway for every VLAN.

### 6.3 Save Configuration

```text
SW2# copy running-config startup-config
R1# copy running-config startup-config
```

> Skipping this step erases the entire redesign on the next reload — always finish a topology change with a save on every device you touched.

---

## 7. Verification Steps

### 7.1 Command Table

| Device | Command | What to check |
|---|---|---|
| SW2 | `show ip interface brief` | VLAN10/20/30 SVIs and G1/0/2 all `up/up` with correct IPs |
| SW2 | `show ip route` | Three directly connected `/26`s, one `/30`, one default route via R1 |
| SW2 | `show vlan brief` | VLANs 10/20/30 active with expected ports assigned |
| SW2 | `show run \| include ip routing` | Confirms `ip routing` is actually enabled |
| R1 | `show ip interface brief` | G0/0 `up/up`, correct IP, no leftover subinterfaces listed |
| R1 | `show run \| section interface` | Confirms subinterfaces were actually removed, not just shut down |
| PC (any) | `ipconfig` | Correct IP, mask, and gateway for its VLAN |

### 7.2 Expected Output Gallery

**`SW2# show ip interface brief`**

```text
Interface              IP-Address      OK? Method Status                Protocol
Vlan1                   unassigned      YES unset  administratively down down
Vlan10                  10.0.0.62       YES manual up                    up
Vlan20                  10.0.0.126      YES manual up                    up
Vlan30                  10.0.0.190      YES manual up                    up
GigabitEthernet1/0/1    unassigned      YES unset  up                    up
GigabitEthernet1/0/2    10.0.0.193      YES manual up                    up
```

`Vlan1` staying administratively down is normal — it was never configured in this lab (or Day 17). Every SVI you actually configured, plus the routed uplink, should read `up/up`.

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.194      YES manual up                    up
```

No `.10`, `.20`, or `.30` subinterfaces appear at all — if you still see them here, Step 1.1's `no interface` commands didn't take effect; re-check.

**`SW2# show ip route`** (final state)

```text
Gateway of last resort is 10.0.0.194 to network 0.0.0.0

C    10.0.0.0/26 is directly connected, Vlan10
C    10.0.0.64/26 is directly connected, Vlan20
C    10.0.0.128/26 is directly connected, Vlan30
C    10.0.0.192/30 is directly connected, GigabitEthernet1/0/2
S*   0.0.0.0/0 [1/0] via 10.0.0.194
```

**`PC1> ping 10.0.0.4`** (inter-VLAN test, VLAN10 host to another VLAN's host)

```text
Pinging 10.0.0.4 with 32 bytes of data:

Reply from 10.0.0.4: bytes=32 time<1ms TTL=128
Reply from 10.0.0.4: bytes=32 time<1ms TTL=128
Reply from 10.0.0.4: bytes=32 time<1ms TTL=128
Reply from 10.0.0.4: bytes=32 time<1ms TTL=128

Ping statistics for 10.0.0.4:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

TTL of 128 (one hop's worth of decrement from a typical Windows PC's starting TTL of 128... in Packet Tracer's simplified model, TTL reflects one Layer 3 hop through SW2) confirms this traffic was routed by SW2's SVIs, not switched — a same-VLAN ping would never decrement TTL at all.

**`PC1> ping 1.1.1.1`** (internet reachability test)

```text
Pinging 1.1.1.1 with 32 bytes of data:

Request timed out.
Reply from 1.1.1.1: bytes=32 time=2ms TTL=253
Reply from 1.1.1.1: bytes=32 time=2ms TTL=253
Reply from 1.1.1.1: bytes=32 time=2ms TTL=253

Ping statistics for 1.1.1.1:
    Packets: Sent = 4, Received = 3, Lost = 1 (25% loss)
```

The first timeout is expected and normal — it's ARP resolution delay for the very first packet on a previously-idle path (SW2 resolving R1's MAC, or R1 resolving the next hop toward the internet cloud). Three successful replies after that confirm both the default route on SW2 and R1's onward path are working. Consistent 100% loss (not just one timeout) means something is actually broken — see Troubleshooting.

### 7.3 Reachability Matrix

| From | To | Expected Result | Why |
|---|---|---|---|
| PC on VLAN10 | Another PC on VLAN10 | Success | Same subnet, switched locally by SW1/SW2 — never touches an SVI |
| PC on VLAN10 | PC on VLAN20 | Success | Routed by SW2's SVIs — this is the core deliverable of this lab |
| PC on VLAN20 | PC on VLAN30 | Success | Same mechanism, different VLAN pair |
| Any VLAN PC | Its own SVI gateway | Success | Directly connected gateway, always reachable if the SVI is up |
| Any VLAN PC | 1.1.1.1 (internet) | Success (after first-packet ARP delay) | Routed via SW2's default route → R1 → internet cloud |
| SW2 | R1 (10.0.0.194) | Success | Directly connected routed link |

---

## 8. Common Mistakes (the 80/20)

1. **Forgetting `ip routing` entirely.** SVIs come up, addresses look correct, `show ip interface brief` looks perfect — and inter-VLAN pings still fail. This is the signature symptom of a missing `ip routing` command; it's easy to forget precisely because everything else *appears* configured correctly.
2. **Forgetting `no switchport` on the uplink port before assigning an IP.** IOS will reject the `ip address` command on a port still in switchport mode, but students sometimes miss the error message scrolling by and assume the IP took effect.
3. **Leaving old ROAS subinterfaces in place instead of deleting them.** If `no interface g0/0.10` etc. isn't run, R1 may still have a phantom trunk-based path that conflicts with or masks problems on the new routed link.
4. **Assigning an SVI the wrong address — off by one from the last usable host.** Since this lab intentionally uses the *last* usable address instead of the more commonly-seen first usable address, students used to the "gateway is always `.1`" habit from earlier labs often default back to it here. Recheck Section 4 before typing.
5. **Not verifying the SW1↔SW2 trunk is up before troubleshooting SVIs.** An SVI can be perfectly configured and still fail to pass traffic if no VLAN-tagged frames are actually arriving from SW1 — the fault is one layer below where students look first.
6. **Confusing a routed port with a trunk port.** The SW2↔R1 link is untagged, single-subnet, point-to-point — it must never have `switchport mode trunk` applied; that would be mixing two incompatible designs on the same link.
7. **Forgetting to save on *both* SW2 and R1.** Both devices changed in this lab — saving only one leaves the other reverting to its Day 17 ROAS config on next reload.
8. **Assuming a 2960 could do this lab.** A handful of students try to replicate this design on a Layer 2-only switch model and then can't find `ip routing` or SVI routing behavior at all — see Section 10 for why this matters.

---

## 9. Troubleshooting Guide

Work through these **in order** — each step assumes the previous one passed.

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | SW2 G1/0/2 or an SVI shows `administratively down` | Forgot `no shutdown` | `show ip interface brief` | Enter the interface, run `no shutdown` |
| 2 | `ip address` command rejected on SW2's uplink port | Port still in switchport mode | `show running-config interface g1/0/2` | Run `no switchport` first, then re-apply the IP |
| 3 | SVI shows `up/administratively down` (protocol down) even after `no shutdown` | No active port currently belongs to that VLAN | `show vlan brief` | Confirm at least one access port is assigned to and up in that VLAN |
| 4 | Same-VLAN pings work, but inter-VLAN pings fail everywhere | `ip routing` not enabled | `show run \| include ip routing` | Enable it: `ip routing` in global config |
| 5 | Inter-VLAN routing works, but internet pings fail | Missing or wrong default route on SW2, or R1's interface misconfigured | `show ip route` (both devices) | Re-check `ip route 0.0.0.0 0.0.0.0 10.0.0.194` on SW2 and R1 G0/0's IP |
| 6 | R1 shows old subinterfaces still present | ROAS not fully removed | `show run \| section interface` | Run `no interface g0/0.X` for each leftover subinterface |
| 7 | PCs can't reach their own SVI gateway | Wrong SVI IP, or SW1↔SW2 trunk down | `show interfaces trunk` (SW1/SW2), verify SVI IP against Section 4 | Fix the SVI address or restore the trunk |
| 8 | Config reverts after a reload | Forgot to save | `show startup-config` vs `show running-config` | `copy running-config startup-config` on both SW2 and R1 |

---

## 10. Design Analysis

**Router-on-a-Stick vs. Multilayer Switch (SVI) Inter-VLAN Routing**

| Factor | Router-on-a-Stick (Day 17) | Multilayer Switch / SVIs (Day 18) |
|---|---|---|
| Where routing happens | Dedicated router, over a trunk | Directly on the distribution/access switch |
| Inter-VLAN traffic path | Switch → trunk → router → trunk → switch | Stays inside the switch (SVI to SVI) |
| Latency for local inter-VLAN traffic | Higher — full round trip to the router | Lower — no extra hop |
| Scalability as VLANs/traffic grow | Router interface/trunk becomes a bottleneck | Scales with switch backplane, typically much higher throughput |
| Hardware requirement | Any router + any Layer 2 switch | Requires a Layer 3-capable ("multilayer") switch — real added cost |
| Failure impact | Router failure kills *all* inter-VLAN routing, including local traffic | Router failure only kills *internet-bound* traffic; local inter-VLAN traffic keeps working |
| Design complexity | Slightly simpler mentally — "the router does the routing" | Requires understanding that a switch can hold two roles at once |
| Typical use case | Small office, few VLANs, low inter-VLAN traffic volume, minimizing hardware cost | Any network with meaningful inter-VLAN traffic volume or a need for resilience — most real enterprise access/distribution layers |

**Why did this lab move away from ROAS specifically now?** Because the business driver was performance and resilience, not just "because it's the next topic." ROAS remains the *correct* choice in some scenarios — a tiny branch office with two VLANs and almost no VLAN-to-VLAN chatter doesn't need to spend money on a Layer 3 switch just to save a few router hops it barely uses. The decision is a cost/benefit one: multilayer switching costs more in hardware and configuration complexity, and buys back latency, throughput headroom, and partial fault isolation. This lab's company already owns a 3650 — so the marginal cost of switching designs is just engineering time, which tips the decision firmly toward SVIs.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a company's help-desk tickets shift from "the internet is slow" to "accessing the file share in the other department is slow" — that's often a sign inter-VLAN traffic is being routed inefficiently, and this exact redesign (ROAS → SVI) is a standard fix.
- ...a network team does a hardware refresh and realizes their newly-purchased access switches are multilayer-capable but are being run in pure Layer 2 mode out of habit — a common finding in infrastructure audits.
- ...a distribution-layer design review asks "why is our edge router also doing inter-VLAN routing for departments that never talk to the internet?" — this lab's redesign is the textbook answer.
- ...you're asked to explain, to a non-technical stakeholder, why a "network upgrade" project doesn't require replacing the switches — because the capability (multilayer routing) was often already sitting unused in existing hardware, and the actual work is reconfiguration, not a hardware purchase.
- ...you inherit a network with a router doing ROAS for a switch stack that's clearly Layer 3-capable, and you have to decide whether migrating to SVIs is worth the maintenance-window risk — weighing exactly the trade-offs in Section 10.

---

## 12. Stretch Goal

Once the base lab works end-to-end, try one or more of the following without referring back to the steps above:

1. **Add a fourth VLAN (VLAN40)** sized for 30 hosts, choosing an appropriately smaller subnet than the existing `/26`s (hint: think about what block size actually fits 30 hosts) that fits cleanly into unused space in `10.0.0.0/24`. Show your host-bit math the way Section 4 does.
2. **Convert the SW1↔SW2 link's VLAN assignment strategy**: what would change if SW1 also became a multilayer switch and split routing duties with SW2? Sketch how you'd divide SVI responsibility and why you would or wouldn't do this in practice.
3. **Break `ip routing` on purpose, then diagnose it using only `show` commands** (no peeking at your own config) — disable it, confirm inter-VLAN pings fail exactly as Section 9 predicts, then re-enable it. This builds the diagnostic instinct that "everything looks configured but nothing routes" almost always means this one command.
4. **Research and note (don't configure) how this design would need to change for redundancy** — specifically, look up what HSRP/VRRP are and write 2-3 sentences on why a *single* multilayer switch acting as the gateway for three VLANs is a single point of failure that a production network wouldn't accept long-term.

---

## 13. Self-Assessment

Before moving to the next lab, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, why `ip routing` is required in addition to configuring SVIs?
- [ ] Can you write the exact 3-command sequence to convert a switch physical port from a switchport to a routed port with an IP address, without looking?
- [ ] Can you explain why an SVI can show `up` on its own configuration but still be down at the protocol level?
- [ ] Given a `/24` block, could you split it into three `/26` VLANs by hand and identify the last usable host in each, the way Section 4 does?
- [ ] Can you explain, in one sentence, the core structural difference between ROAS and SVI-based inter-VLAN routing?
- [ ] Can you name at least 4 of the 8 common mistakes from Section 8 without looking?
- [ ] Could you explain to a non-technical manager, in under 2 minutes, why a "software reconfiguration" fixed a performance problem without buying new hardware?

If you answered "no" to more than two of these, re-do the lab from scratch (not by copy-pasting commands) before moving on.

---

## 14. Key Concepts Demonstrated

- **Multilayer switching** — a single device performing both Layer 2 switching and Layer 3 routing
- **Switched Virtual Interfaces (SVIs)** — virtual Layer 3 gateways bound to a VLAN rather than a physical port
- **Routed ports** — converting a physical switchport to a Layer 3 interface with `no switchport`
- **`ip routing`** — the global command that actually enables inter-VLAN forwarding on a Layer 3 switch
- **Subnetting a single block across multiple VLANs** — deriving three `/26`s and one `/30` from one `/24` by hand
- **Design trade-off analysis** — ROAS vs. multilayer switching, evaluated on latency, resilience, and cost

---

## 15. What I Learned

The biggest conceptual shift in this lab wasn't any single command — it was realizing that "switch" and "router" are roles a device can perform, not fixed categories. SW2 spent Day 17 acting purely as a Layer 2 device and, with a handful of commands (`no switchport`, SVIs, `ip routing`), became something that behaves exactly like a router for every VLAN it hosts, while still switching frames normally within each VLAN.

The most useful failure mode to understand deeply is the "everything looks right but nothing routes" scenario caused by a missing `ip routing` command — it's the kind of bug that costs real troubleshooting time in the field precisely because every individual piece of configuration checks out under inspection. Building the instinct to check `show run | include ip routing` early, not last, is a direct, practical takeaway from this lab.

This lab is the foundation for what comes next:

- HSRP/VRRP for gateway redundancy (a single multilayer switch is a single point of failure, as flagged in the Stretch Goal)
- Layer 3 EtherChannel between distribution switches
- Dynamic routing protocols replacing the static default route once multiple exit paths exist
- VLAN and SVI design at real enterprise scale (dozens of VLANs, route summarization)

---

## 16. Skills Practiced

- Converting a Router-on-a-Stick design to a multilayer-switch design
- Configuring routed ports (`no switchport`) on a Layer 3 switch
- Creating and addressing SVIs across multiple VLANs
- Enabling and verifying `ip routing` on IOS
- Manual subnetting of a single block into multiple VLAN subnets plus a transit link
- Reading and interpreting a multilayer switch's routing table
- Structured troubleshooting of inter-VLAN and internet connectivity failures
- Comparing network designs on latency, resilience, and cost trade-offs

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology that mirrors the design above using free, open-source images, built automatically by [`GNS3/build_lab.py`](../GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| R1 (edge router) | Cisco 2911 | VyOS |
| SW1 (Layer 2 access) | Cisco 2960-24TT | Open vSwitch |
| SW2 (multilayer switch) | Cisco 3650-24PS | Open vSwitch **+ VyOS L3 stand-in** (see GNS3 README for why) |
| PC1–PC7 | Generic PC | Linux (Alpine) |

See [`GNS3/README.md`](../GNS3/README.md) for how to run the build script and — importantly — for the device-substitution caveat on SW2: Open vSwitch alone cannot realistically model SVI-based inter-VLAN routing, so the GNS3 build documents a VyOS-based workaround rather than silently pretending OVS can do something it can't.
