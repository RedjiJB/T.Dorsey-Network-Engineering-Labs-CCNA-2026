# Day 53 Lab Manual — GRE Tunnels

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a GRE tunnel between R1 (Office A) and R2 (Office B) across a service-provider underlay, then run OSPF over the tunnel so PC1 and PC2 can reach each other without the provider ever learning either office's internal LAN. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): "configure and verify... GRE tunneling" is on the blueprint explicitly. Also reinforces Domain 4's OSPF objectives (single-area OSPF over a non-Ethernet logical interface) and Domain 1's understanding of overlay vs. underlay concepts used across VXLAN, IPsec, and SD-WAN designs later in a career. |
| **Prerequisites** | Static/default routing, basic OSPF single-area configuration (Day 24–27), subnetting a /30. |
| **Time Estimate** | 1.5 – 2 hours first attempt. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the commands are short, but the two-layer addressing model (underlay IPs vs. tunnel IPs) is the single most common point of confusion in this entire course, and this lab exists specifically to force you to keep them straight. |

---

## 1. Lab Overview + Learning Objectives

Office A and Office B are separated by a service-provider network that neither office controls and that has no reason to know either office's private LAN addressing. GRE (Generic Routing Encapsulation) solves this by wrapping each office's traffic inside a new, provider-routable IP packet, creating a logical point-to-point link — a **tunnel** — between R1 and R2 that behaves, from OSPF's perspective, exactly like a directly connected interface.

By the end of this lab you will be able to:

- Explain, precisely, the difference between a tunnel's **source/destination** addressing and its **interface** addressing — and why confusing the two is the single most common GRE misconfiguration
- Configure a GRE tunnel interface on both ends of a point-to-point link
- Run OSPF across a GRE tunnel and advertise LANs that sit behind it
- Explain why the tunnel appears in the routing table as "directly connected" even though it crosses an entire provider network
- Diagram and explain the difference between an **underlay** network (the real, physically routed path) and an **overlay** network (the logical tunnel built on top of it)
- State clearly that GRE encapsulates but does not encrypt, and identify what technology you'd pair it with when confidentiality is required

---

## 2. Business Context

**Why would a real company do this?**

- **"We have two offices and don't want to lease a private WAN circuit between them"** → GRE lets you build a logical private link across a network you don't own or control (the internet, or a shared service-provider backbone), without paying for dedicated point-to-point circuit pricing.
- **"Our provider shouldn't need to know our internal addressing"** → the provider only ever routes the *outer* IP header (the two providers-facing router addresses). Office A's and Office B's private RFC 1918 LAN subnets never appear in a single provider routing table — they're invisible to the underlay entirely, which is both a security and an operational-simplicity win.
- **"We're about to deploy a routing protocol between sites, but our only connectivity between them is a plain IP path, not a shared broadcast segment"** → many routing protocols (OSPF included) want to form neighbor relationships. GRE turns an arbitrary IP path into something that looks and behaves like a directly connected link, letting you run OSPF (or EIGRP, or even a full mesh of them) across it as if the two offices were in the same wiring closet.
- **"We eventually need to encrypt this traffic too"** → this lab's biggest single misconception to pre-empt: GRE by itself is *not* encryption. A real production deployment of this design almost always pairs GRE with IPsec (GRE-over-IPsec) specifically because GRE alone leaves the encapsulated payload in the clear. Understanding GRE's actual job (encapsulation, not confidentiality) is what lets you correctly identify when you need to add IPsec on top.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels.png" alt="Day 53 GRE Tunnel Topology" width="900">
</p>

```text
Office A                                             Office B

10.0.1.0/24                                         10.0.2.0/24
     |                                                    |
    PC1                                                  PC2
     |                                                    |
    SW1                                                  SW2
     |                                                    |
     R1                                                  R2
     | G0/0/0                                    G0/0/0  |
     |                                                    |
100.0.0.0/30                                        200.0.0.0/30
     |                                                    |
   SPR1 ---------------- Service Provider ------------- SPR2


                  ===== GRE TUNNEL (overlay) =====>
                       192.168.1.0/30
                  R1 Tunnel0 <----> Tunnel0 R2
```

Device roles: R1 and R2 are the office edge routers and GRE tunnel endpoints. SPR1/SPR2 are the service provider's routers, carrying only the underlay /30s — they are not configured in this lab beyond providing basic IP reachability between R1's and R2's provider-facing addresses. SW1/SW2 are simple office-LAN switches. PC1/PC2 are the end hosts that ultimately need to reach each other.

---

## 4. IP Addressing Plan

This lab has **two independent addressing layers**, and keeping them mentally separate is the entire point of the exercise.

### 4.1 Layer 1 — The Underlay (the real, physically routed network)

This is the addressing the service provider actually routes. It has nothing to do with GRE yet — it's just ordinary point-to-point IP connectivity that must work *before* GRE can be configured on top of it.

| Link | Subnet | R1/SPR1 side | R2/SPR2 side |
|---|---|---|---|
| R1 ↔ SPR1 | 100.0.0.0/30 | R1 G0/0/0 = 100.0.0.2 | SPR1 = 100.0.0.1 |
| R2 ↔ SPR2 | 200.0.0.0/30 | SPR2 = 200.0.0.1 | R2 G0/0/0 = 200.0.0.2 |

**Why /30:** a point-to-point link needs exactly 2 usable host addresses. `2^h − 2 ≥ 2` requires `h = 2` host bits, which gives a /30 (255.255.255.252) — the smallest subnet that correctly fits exactly 2 hosts with no wasted addresses. This is the same sizing logic used for every router-to-router link throughout this course.

**Why this must work first:** GRE's tunnel destination is an underlay address (see 4.2). If R1 cannot already reach 200.0.0.2 via ordinary IP routing, the tunnel can never come up — GRE has nothing to encapsulate traffic *into* if the underlying path doesn't exist. This is why Part 2 of the original walkthrough configures default routes on R1 and R2 pointing at their provider next hops before touching the word "tunnel" at all.

```cisco
! R1
ip route 0.0.0.0 0.0.0.0 100.0.0.1
! R2
ip route 0.0.0.0 0.0.0.0 200.0.0.1
```

### 4.2 Layer 2 — The Overlay (the GRE tunnel's own addressing)

This is a **completely separate, second addressing decision** that has no relationship to the underlay subnets above except that it rides on top of them.

| Interface | IP Address | Role |
|---|---|---|
| R1 Tunnel0 | 192.168.1.1/30 | Tunnel endpoint, Office A side |
| R2 Tunnel0 | 192.168.1.2/30 | Tunnel endpoint, Office B side |

192.168.1.0/30 is chosen because, again, this is a point-to-point link needing exactly 2 usable addresses — same /30 logic as the underlay, but this time applied to a purely logical interface. Nothing about this subnet is routed by the service provider; it exists only inside the GRE encapsulation, known only to R1 and R2.

**The two-layer relationship, stated explicitly (read this twice):**

```text
LAYER 2 — OVERLAY (what OSPF sees, what "Tunnel0" means to routing)
    R1 Tunnel0 192.168.1.1/30  <========== GRE ==========>  R2 Tunnel0 192.168.1.2/30

LAYER 1 — UNDERLAY (what actually gets routed by the provider, carries Layer 2 inside it)
    R1 G0/0/0 100.0.0.2  --->  SPR1  --->  SPR2  --->  R2 G0/0/0 200.0.0.2
```

A GRE tunnel interface configuration has **both** kinds of address in it, and they must never be confused:

```cisco
interface tunnel 0
 ip address 192.168.1.1 255.255.255.252   ! <- LAYER 2: the tunnel interface's own IP
 tunnel source gigabitEthernet0/0/0       ! <- LAYER 1: MY underlay-facing interface
 tunnel destination 200.0.0.2             ! <- LAYER 1: the REMOTE router's underlay address
```

**The rule to memorize:** `tunnel source` and `tunnel destination` are always underlay/real-world addresses — the addresses the provider can actually route packets to. `ip address` on the tunnel interface is always overlay/logical — an address that exists purely for the two tunnel endpoints (and anything routed across the tunnel, like OSPF) to talk to each other. If you ever find yourself putting a 192.168.1.x address into a `tunnel destination` line, or a 100.0.0.x/200.0.0.x address into the tunnel's `ip address` line, stop — you've crossed the two layers.

### 4.3 LAN Addressing (unchanged from the offices' existing design)

| LAN | Subnet | Gateway |
|---|---|---|
| Office A (behind R1) | 10.0.1.0/24 | R1 LAN interface |
| Office B (behind R2) | 10.0.2.0/24 | R2 LAN interface |

---

## 5. Pre-Configuration Checklist

- [ ] R1 and R2 can each ping the other's tunnel-destination address (100.0.0.2 ↔ 200.0.0.2) across the underlay **before** any tunnel interface is configured. If this fails, stop — GRE will not come up on top of broken underlay reachability.
- [ ] You have written down, on paper, which address is underlay and which is overlay for both R1 and R2 — Section 4.2's rule — before opening the CLI.
- [ ] SW1/SW2 and PC1/PC2 already have basic LAN connectivity to their local router (this lab assumes that part is already working, same as prior labs).

---

## 6. Configuration Tasks

### 6.1 Task 1 — Confirm underlay reachability

```cisco
R1# ping 200.0.0.2
R2# ping 100.0.0.2
```
**Mode:** Privileged EXEC. **What it does:** confirms ordinary IP routing already carries a packet from R1's provider-facing interface all the way to R2's provider-facing interface (and back), with no GRE involved yet. **Why it matters:** this is the single most valuable 30 seconds in the whole lab — if it fails, every subsequent GRE symptom you'll see (tunnel line protocol down, no OSPF neighbor) has this as its actual root cause, not anything GRE-specific.

### 6.2 Task 2 — Create the GRE tunnel on R1

```cisco
R1(config)# interface tunnel 0
R1(config-if)# ip address 192.168.1.1 255.255.255.252
R1(config-if)# tunnel source gigabitEthernet0/0/0
R1(config-if)# tunnel destination 200.0.0.2
```
- `interface tunnel 0` (global config): creates a new logical interface. Tunnel interfaces don't correspond to physical hardware — the number is arbitrary and locally significant, it just has to match on the command line you type, not between routers.
- `ip address 192.168.1.1 255.255.255.252` (tunnel interface config): the **overlay** address — see Section 4.2. This is what OSPF will treat as the "network" this interface belongs to.
- `tunnel source gigabitEthernet0/0/0` (tunnel interface config): tells GRE which of R1's own interfaces to use as the *source* of the outer, provider-routable packet. **Memory aid:** "source is about ME" — my own real-world exit interface.
- `tunnel destination 200.0.0.2` (tunnel interface config): tells GRE the **underlay** address of the far end — R2's provider-facing IP, not R2's tunnel IP. **Memory aid:** "destination is about THEM, underlay-only" — you are telling the provider network where to physically deliver the outer packet.

### 6.3 Task 3 — Create the matching GRE tunnel on R2

```cisco
R2(config)# interface tunnel 0
R2(config-if)# ip address 192.168.1.2 255.255.255.252
R2(config-if)# tunnel source gigabitEthernet0/0/0
R2(config-if)# tunnel destination 100.0.0.2
```
Same logic, mirrored: R2's tunnel source is its own underlay-facing interface; its tunnel destination is R1's underlay address (100.0.0.2), not R1's tunnel address. Notice R1's destination is R2's source-facing address and vice versa — this cross-reference is exactly why writing both endpoints' addressing down before configuring (Pre-Configuration Checklist) prevents transposition errors.

### 6.4 Task 4 — Configure OSPF on R1

```cisco
R1(config)# router ospf 1
R1(config-router)# network 192.168.1.0 0.0.0.3 area 0
R1(config-router)# network 10.0.1.1 0.0.0.0 area 0
R1(config-router)# passive-interface gigabitEthernet0/0
```
- `network 192.168.1.0 0.0.0.3 area 0`: puts the tunnel interface's overlay subnet into OSPF area 0 — this is the network that will actually form the OSPF adjacency to R2, because it's the network Tunnel0 belongs to.
- `network 10.0.1.1 0.0.0.0 area 0`: advertises Office A's LAN into OSPF so R2 can learn a route to it, using a host wildcard to match only R1's specific LAN interface address rather than the whole /24 (both work; the host-specific form is more precise about intent).
- `passive-interface gigabitEthernet0/0`: suppresses OSPF Hello packets out the LAN-facing interface — the LAN is still advertised (via the `network` statement above), but no OSPF neighbor relationship should ever form with a PC. **Why it matters:** an interface facing end-user devices should never be sending routing-protocol hellos; there's no legitimate neighbor to form an adjacency with there, and leaving it non-passive is a minor but real attack surface (a rogue device could attempt to speak OSPF on that segment).

### 6.5 Task 5 — Configure OSPF on R2

```cisco
R2(config)# router ospf 1
R2(config-router)# network 192.168.1.0 0.0.0.3 area 0
R2(config-router)# network 10.0.2.1 0.0.0.0 area 0
R2(config-router)# passive-interface gigabitEthernet0/0
```
Mirror of Task 4 for Office B. Once both sides are configured, R1 and R2 should form an OSPF neighbor relationship *across the tunnel* — verify in Section 7.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show interfaces tunnel 0` | Confirms the tunnel interface itself is up/up, and reports tunnel source/destination |
| `show running-config interface tunnel 0` | Confirms the exact addressing configured, useful for spotting a transposed source/destination |
| `show ip ospf neighbor` | Confirms an OSPF adjacency formed across Tunnel0 |
| `show ip route` | Confirms the tunnel subnet shows as directly connected, and the remote LAN shows as an OSPF-learned route via the tunnel |
| `show ip ospf database` | Confirms both routers' LSAs are present in each other's database |
| `ping` from PC1 to PC2 | End-to-end confirmation that the whole stack (LAN → GRE → OSPF → LAN) works |

### Expected Output Gallery

```text
R1# show interfaces tunnel 0
Tunnel0 is up, line protocol is up
  Hardware is Tunnel
  Internet address is 192.168.1.1/30
  Tunnel source 100.0.0.2 (GigabitEthernet0/0/0), destination 200.0.0.2
  Tunnel protocol/transport GRE/IP
```

```text
R1# show ip route
      10.0.0.0/24 is subnetted, 2 subnets
C        10.0.1.0 is directly connected, GigabitEthernet0/0
O        10.0.2.0 [110/1001] via 192.168.1.2, 00:04:12, Tunnel0
      192.168.1.0/30 is subnetted, 1 subnets
C        192.168.1.0 is directly connected, Tunnel0
L        192.168.1.1/32 is directly connected, Tunnel0
```

```text
R1# show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           0   FULL/  -        00:00:38    192.168.1.2     Tunnel0
```

```text
PC1> ping 10.0.2.100

Pinging 10.0.2.100 with 32 bytes of data:
Reply from 10.0.2.100: bytes=32 time=41ms TTL=125
Reply from 10.0.2.100: bytes=32 time=39ms TTL=125
Reply from 10.0.2.100: bytes=32 time=40ms TTL=125
Reply from 10.0.2.100: bytes=32 time=39ms TTL=125

Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Setting `tunnel destination` to the remote router's tunnel IP instead of its underlay IP.** This is by far the most common GRE misconfiguration — the tunnel interface line protocol will typically stay down, or come up but fail to actually forward, because the provider network has no idea how to route to a 192.168.1.x address.
2. **Configuring the tunnel before confirming underlay reachability.** If R1 can't already ping R2's provider-facing address, no amount of tunnel configuration will fix that — the tunnel depends on the underlay, not the other way around.
3. **Forgetting `passive-interface` on the LAN-facing interfaces.** OSPF will still technically work without it, but you've now left an interface facing end users sending Hello packets unnecessarily.
4. **Mismatched tunnel IP masks between the two ends** (e.g., R1 on /30, R2 accidentally on /24) — this silently breaks the OSPF adjacency because the two ends don't agree they're in the same subnet, even though the tunnel interface itself may show up/up.
5. **Assuming GRE encrypts the traffic.** It doesn't — see Section 2 and Section 10. Students who assume this will misdiagnose a security review finding or, worse, present GRE-only as a completed encryption requirement.

---

## 9. Troubleshooting Guide

| Step | Check | Command | Likely Finding |
|---|---|---|---|
| 1 | Does the underlay even work? | `ping <remote tunnel-destination address>` from each router | If this fails, stop here — fix underlay routing before touching GRE |
| 2 | Is the tunnel interface itself up? | `show interfaces tunnel 0` | "Tunnel0 is up, line protocol is down" almost always means the underlay can't reach the configured tunnel destination |
| 3 | Is the addressing on both ends actually correct? | `show running-config interface tunnel 0` on both routers | A transposed source/destination, or a tunnel-IP-in-a-destination-field mistake (Common Mistake #1) |
| 4 | Does the OSPF adjacency form? | `show ip ospf neighbor` | Empty output despite an up/up tunnel usually means a mismatched tunnel subnet mask, mismatched OSPF area, or the `network` statement doesn't actually match the tunnel interface's address |
| 5 | Is the remote LAN actually being advertised? | `show ip route ospf` and `show ip ospf database` | Missing `network` statement for the LAN on the far router, or that LAN interface is down |
| 6 | Does the ping actually complete end-to-end? | `ping` from PC to PC | If routes look correct but the ping fails, check the PC's own default gateway and confirm the local router's LAN interface is up |

---

## 10. Design Analysis

**Why GRE instead of just running OSPF directly over the provider link?** The provider link (100.0.0.0/30 ↔ 200.0.0.0/30) only connects R1 to *its own* provider router (SPR1), not to R2 — there's no single shared Layer 3 segment between R1 and R2 without a tunnel, because a full ISP core sits between them, potentially with many hops and no reason to carry OSPF hellos. GRE manufactures a logical point-to-point segment where routing-protocol adjacency can actually form, regardless of how many real hops separate the two endpoints.

**Why not just use static routes across the underlay instead of a tunnel at all?** You could route Office A ↔ Office B with static routes referencing the provider's next hops directly, but that would require the provider to carry routes to your private RFC 1918 LAN subnets — exactly what Section 2's business context says you don't want. The tunnel keeps the provider's routing table limited to the two underlay /30s; everything about your internal addressing stays invisible to them.

**Why GRE and not something like a VPN/IPsec tunnel for this specific lab?** GRE is intentionally the simplest possible "make two remote networks look adjacent" tool — no encryption negotiation, no key management, minimal configuration. It's the right first building block to learn before layering IPsec on top (GRE-over-IPsec) in a later, more security-focused lesson. Using plain GRE here isolates the encapsulation/overlay concept from the separate concept of confidentiality.

---

## 11. Real-World Parallel

Multi-site enterprises with a WAN or internet-only connection between offices (rather than an expensive dedicated MPLS circuit) commonly build exactly this design: GRE tunnels (usually paired with IPsec for encryption) between site routers, with a routing protocol running across the tunnels to dynamically learn remote-site subnets. This is also conceptually the ancestor of technologies you'll meet later — VXLAN and other overlay/underlay networking models in data centers and SD-WAN follow the exact same two-layer addressing pattern this lab introduces at CCNA scale.

---

## 12. Stretch Goal

1. Add a second GRE tunnel between R1 and R2 using a different tunnel number and a different overlay subnet, then adjust OSPF cost on each tunnel so one is preferred and the other is a backup path — observe failover behavior by shutting down the primary tunnel's source interface.
2. Research and diagram (on paper, no configuration required) how IPsec would be layered on top of this exact GRE tunnel to add encryption — identify specifically which layer (overlay or underlay) IPsec would be protecting.
3. Calculate the GRE overhead: research the byte size of the outer IP header plus GRE header, and explain why this matters for MTU on the tunnel interface versus the LAN interfaces.

---

## 13. Self-Assessment Checklist

- [ ] I can explain, without looking, the difference between `tunnel source`/`tunnel destination` and the tunnel interface's own `ip address` — in one sentence each.
- [ ] I can explain why underlay reachability must work before GRE can come up.
- [ ] I can explain why the tunnel subnet appears as "directly connected" in the routing table despite crossing an entire provider network.
- [ ] I can state, correctly and without hedging, whether GRE alone provides encryption.
- [ ] I could diagram this lab's underlay and overlay on a whiteboard from memory.

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** GRE encapsulation; tunnel source/destination (underlay) vs. tunnel interface IP (overlay); OSPF operating across a logical, non-Ethernet interface; underlay vs. overlay network design; GRE's lack of built-in encryption.

**What I learned:** A GRE tunnel configuration always carries two independent addressing decisions at once — where the encapsulated packet is physically delivered (source/destination, underlay) and what logical network the tunnel interface itself belongs to (its `ip address`, overlay) — and mixing these up is the single most common configuration error in GRE deployments. The underlay must already work before GRE can be layered on top of it; GRE cannot create connectivity that doesn't already exist at the IP routing layer beneath it.

**Skills practiced:** GRE tunnel interface configuration, underlay/overlay addressing design, OSPF-over-tunnel configuration, `show ip route`/`show ip ospf neighbor`/`show interfaces tunnel` verification, structured GRE troubleshooting.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for an automated build of this topology (R1, R2, SPR1, SPR2, SW1, SW2, PC1, PC2) using VyOS routers, Open vSwitch switches, and Alpine Linux end hosts. VyOS supports GRE tunnel interfaces natively (`set interfaces tunnel tun0 encapsulation gre`) and OSPF via FRRouting, so this lab — unlike some later Day-5x security labs — translates to the open-source stack with full functional parity, not just a topology approximation.
