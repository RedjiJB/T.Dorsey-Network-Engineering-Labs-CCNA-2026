# Day 03 Lab Manual — OSI Model & DHCP Packet Analysis

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a small routed topology with a DHCP server, capture and dissect the DHCP Discover/Offer/Request/Ack (DORA) exchange in Packet Tracer Simulation Mode, and map each observed field back to its OSI layer. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): 1.4 (OSI/TCP-IP model comparison), 1.5 (encapsulation). Domain 4 (IP Connectivity): DHCP operation and relay concepts appear directly on the exam blueprint. |
| **Prerequisites** | Day 01–02 (device roles, cabling, basic addressing). Comfort reading a table of layer names top-to-bottom or bottom-to-top. |
| **Time Estimate** | 1.5 – 2 hours. |
| **Difficulty** | ⭐☆☆☆☆ (Beginner) — no hard configuration, but the DORA sequence and the "why broadcast" reasoning trip up a lot of first-time students on the exam. |

---

## 1. Lab Overview

This lab uses a client-server DHCP exchange as a lens for understanding the OSI model — not as an abstract 7-layer diagram to memorize, but as something you can literally watch happen inside Packet Tracer's Simulation Mode, one PDU at a time.

The star of this lab is a single DHCP Discover frame. We will trace it from the moment PC1's application layer decides it needs an IP address, through UDP, through IP, through Ethernet, down to the wire — and then do the same for the server's replies going the opposite direction.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain what a DHCP client does before it has any IP configuration, and why its first packet must be a broadcast
- Walk through the full DORA (Discover, Offer, Request, Ack) exchange and state which frames are broadcast vs. unicast and why
- Identify Layer 2 (MAC), Layer 3 (IP), Layer 4 (UDP port), and Layer 7 (DHCP message type) fields inside a captured packet
- Explain encapsulation and de-encapsulation as data moves down and back up the stack
- Configure a DHCP server and DHCP-enabled client interfaces in Packet Tracer
- Use Simulation Mode to capture and step through the exchange frame by frame

---

## 2. Business Context

**Why would a real company do this?**

Nobody manually types an IP address into 400 laptops. Every enterprise, from a 10-person startup to a Fortune 500 company, runs DHCP so that:

- **"New hires should be productive on day one"** → plug a laptop into any wall jack or join any Wi-Fi SSID, and it gets a working IP address, gateway, and DNS server automatically — no help-desk ticket required.
- **"We can't run out of addresses or hand out duplicates"** → a DHCP server tracks lease state centrally, which is the only way to guarantee two devices never collide on the same IP in a network with hundreds of hosts joining and leaving constantly.
- **"Our security team needs to see exactly what got what address, when"** → DHCP lease logs are a standard part of incident response; "who had 192.168.1.87 at 2:14pm on Tuesday" is a question DHCP answers and static addressing can't.
- **"An engineer needs to actually debug 'the network is slow' tickets"** → understanding *which* layer a problem lives at (is the client not even getting an IP — Layer 3/DHCP problem — or does it have an IP but can't resolve names — Layer 7/DNS problem?) is the single most valuable diagnostic skill a junior engineer develops, and it comes directly from understanding the OSI model as a troubleshooting tool, not a trivia list.

This lab is small on purpose — the entire point is that the OSI model stops being an abstract chart the moment you've watched one broadcast DHCP Discover frame leave a NIC and get answered.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-03-OSI-Model-1.png" alt="Day 03 OSI Model Lab 1" width="1000">
</p>
<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-03-OSI-Model-2.png" alt="Day 03 OSI Model Lab 2" width="1000">
</p>

```text
PC1 -- SW1 -- R1 -- R2 -- SW2 -- SRV1 (DHCP Server)
```

| Device | Role |
|---|---|
| PC1 | DHCP client |
| SW1 | Access switch, PC1's local segment |
| R1 | Local-segment router / DHCP relay point |
| R2 | Second router (WAN hop toward the server segment) |
| SW2 | Access switch, server segment |
| SRV1 | DHCP server |

---

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

| Segment | Hosts needed | Why this prefix |
|---|---|---|
| Local network (PC1's LAN, behind R1) | Handful of clients, all DHCP-assigned | `/24` (254 usable) — a DHCP scope is almost always sized generously since its entire purpose is absorbing however many clients show up |
| WAN link (R1 ↔ R2) | Exactly 2 | `/24` is used in the original lab for simplicity, but the *correct* engineering answer for a 2-host point-to-point link is a `/30` — see the calculation below for why |

### 4.2 Manual Calculation Walkthrough

The original lab's WAN network (`10.0.0.0/24`) is oversized for a 2-host router-to-router link — a good teaching moment for "just because it works doesn't mean it's right-sized." Here's the correct-sizing math:

```text
Requirement: exactly 2 usable hosts (R1's WAN interface + R2's WAN interface)

usable hosts = 2^h − 2
2^1 − 2 = 0   → too small
2^2 − 2 = 2   → exactly fits

h = 2 → prefix = 32 − 2 = /30
```

```text
/30 = 11111111.11111111.11111111.111111 00
    =     255  .    255 .    255 .    252
```

Applied to `10.0.0.0/30`:

```text
Network address:    10.0.0.0    (all host bits = 0)
First usable host:  10.0.0.1    (R1)
Last usable host:   10.0.0.2    (R2)
Broadcast address:  10.0.0.3    (all host bits = 1)
```

Using `10.0.0.0/24` here (as the plain overview suggests) wastes 251 usable addresses on a link that will only ever have 2 devices — this lab's manual configuration below uses the correctly-sized `/30` instead.

### 4.3 Full Device Address Table

| Device | Interface | IP Address | Mask | Assignment Method |
|---|---|---|---|---|
| PC1 | NIC | 192.168.1.10 (leased) | 255.255.255.0 | **DHCP** |
| R1 | LAN-facing (Gi0/0) | 192.168.1.1 | 255.255.255.0 | Static (default gateway for PC1) |
| R1 | WAN-facing (Gi0/1) | 10.0.0.1 | 255.255.255.252 | Static |
| R2 | WAN-facing (Gi0/0) | 10.0.0.2 | 255.255.255.252 | Static |
| R2 | Server-side (Gi0/1) | 192.168.2.1 | 255.255.255.0 | Static (default gateway for SRV1's segment) |
| SRV1 | NIC | 192.168.2.100 | 255.255.255.0 | Static (a DHCP server needs a fixed address itself) |

**DHCP pool served to PC1's segment:** network `192.168.1.0/24`, default router `192.168.1.1`, DNS server `8.8.8.8` (placeholder), lease range excluding `.1` (the gateway) and `.100`–`.110` (reserved).

---

## 5. Pre-Configuration Checklist

1. Place PC1, SW1, R1, R2, SW2, and SRV1 per the topology.
2. Cable with straight-through everywhere here (router-switch, switch-PC, switch-server) except R1–R2, which is router-to-router straight-through in Packet Tracer's auto-sensing model.
3. Set PC1's IP configuration mode to **DHCP** (not static) — this is the entire point of the lab.
4. Have Packet Tracer's **Simulation Mode** (not Realtime) ready before you generate any traffic — you need to step through PDUs one at a time to see each layer.

---

## 6. Configuration Tasks

### 6.1 R1 — LAN and WAN interfaces

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description LAN - PC1 segment
R1(config-if)#ip address 192.168.1.1 255.255.255.0
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description WAN to R2
R1(config-if)#ip address 10.0.0.1 255.255.255.252
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#ip route 192.168.2.0 255.255.255.0 10.0.0.2
```

> **Mode:** Global Config → Interface Config. The static route tells R1 how to reach SRV1's subnet across R2 — without it, PC1 could get a lease from a *local* DHCP source but never reach a server sitting behind another router (this is why real deployments often use a DHCP *relay* — see Section 10).

### 6.2 R2 — WAN and server-side interfaces

```text
Router>enable
Router#configure terminal
Router(config)#hostname R2
R2(config)#interface gigabitEthernet 0/0
R2(config-if)#description WAN to R1
R2(config-if)#ip address 10.0.0.2 255.255.255.252
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#description Server segment
R2(config-if)#ip address 192.168.2.1 255.255.255.0
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#ip route 192.168.1.0 255.255.255.0 10.0.0.1
```

### 6.3 SRV1 — static IP and DHCP service

In Packet Tracer, open SRV1 → **Desktop → IP Configuration**, set it static:

| Field | Value |
|---|---|
| IP Address | 192.168.2.100 |
| Subnet Mask | 255.255.255.0 |
| Default Gateway | 192.168.2.1 |

Then **Services → DHCP**, and configure a pool:

| Field | Value |
|---|---|
| Default Gateway | 192.168.1.1 |
| DNS Server | 8.8.8.8 |
| Start IP Address | 192.168.1.11 |
| Subnet Mask | 255.255.255.0 |
| Max Users | 200 |
| Service | **On** |

> A DHCP server itself must always use a static, unchanging address — a server that DHCP'd its own address would create a bootstrapping paradox (it can't hand out leases if it doesn't reliably exist at a known address).

### 6.4 PC1 — enable DHCP

Open PC1 → **Desktop → IP Configuration → DHCP** (radio button, not Static). Do not type anything — this is the point.

> **Important architectural note:** in this topology, R1 and SRV1 are on *different subnets*, separated by R2. By default, routers do **not** forward broadcast traffic (DHCP Discover is a broadcast, destination `255.255.255.255`), so this design only works if R1 is configured to relay DHCP requests toward SRV1's subnet — see Section 6.5.

### 6.5 DHCP relay on R1 (`ip helper-address`)

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#ip helper-address 192.168.2.100
R1(config-if)#exit
```

> **Mode:** Interface config, applied on the interface *facing the DHCP clients* (R1's LAN side). `ip helper-address` converts an incoming broadcast DHCP request into a **unicast** packet addressed directly to the specified DHCP server, forwarding it across the WAN link that would otherwise silently drop it. This single command is the resolution to "why is my DHCP client stuck if the server is on a different subnet" — one of the most common real-world DHCP tickets.

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| R1, R2 | `show ip interface brief` | All interfaces `up/up` |
| R1 | `show ip route` | Route to `192.168.2.0/24` present |
| R1 | `show run \| include helper` | `ip helper-address 192.168.2.100` present on Gi0/0 |
| PC1 | `ipconfig` (PC1's terminal, or Desktop → IP Config) | PC1 shows a leased `192.168.1.x` address, not `0.0.0.0` |

### 7.1 Expected Output Gallery

**`PC1> ipconfig`** (after DHCP succeeds)

```text
IP Address......................: 192.168.1.11
Subnet Mask......................: 255.255.255.0
Default Gateway..................: 192.168.1.1
DNS Server........................: 8.8.8.8
```

**`R1# show run | include helper`**

```text
 ip helper-address 192.168.2.100
```

**Simulation Mode — DHCP Discover frame captured leaving PC1**, inspected via the PDU details window:

```text
[Layer 7 - DHCP]
Message Type: DHCPDISCOVER

[Layer 4 - UDP]
Src Port: 68 (DHCP Client)
Dst Port: 67 (DHCP Server)

[Layer 3 - IP]
Src IP: 0.0.0.0        (PC1 has no address yet)
Dst IP: 255.255.255.255 (limited broadcast)

[Layer 2 - Ethernet]
Src MAC: 0060.2F3D.9A21 (PC1's real MAC)
Dst MAC: FFFF.FFFF.FFFF (broadcast)
```

Notice the source IP is `0.0.0.0`, not `192.168.1.10` as an oversimplified description might suggest — a device that has never had an address literally cannot claim one as a source address yet. This is a detail many students get wrong until they see the actual captured packet.

**DHCP Offer returning from SRV1** (now unicast at Layer 2 once the server knows the client's MAC, but still broadcast at Layer 3 until the client has confirmed the address):

```text
[Layer 7 - DHCP]
Message Type: DHCPOFFER
Offered IP: 192.168.1.11

[Layer 3 - IP]
Src IP: 192.168.2.100
Dst IP: 255.255.255.255
```

### 7.2 The Full DORA Sequence

| Step | Frame | Direction | L2 Dst | L3 Src → Dst | Purpose |
|---|---|---|---|---|---|
| 1 | Discover | Client → * | Broadcast (FFFF.FFFF.FFFF) | 0.0.0.0 → 255.255.255.255 | "Is there a DHCP server anywhere?" |
| 2 | Offer | Server → Client | Unicast (client MAC known) | Server IP → 255.255.255.255 | "I can offer you this address" |
| 3 | Request | Client → * | Broadcast | 0.0.0.0 → 255.255.255.255 | "I accept that offer" (broadcast so any *other* DHCP server that also offered knows it lost) |
| 4 | Ack | Server → Client | Unicast | Server IP → 255.255.255.255 | "Confirmed, lease is yours" |

> **Memory aid:** **D**o **O**ver **R**eal-quick **A**greement — DORA. Discover, Offer, Request, Ack, in that order, every time.

---

## 8. Common Mistakes (the 80/20)

1. **Forgetting `ip helper-address` when the DHCP server is on a different subnet than the client.** By far the most common cause of "PC1 shows 0.0.0.0 / Automatic Private IP" in a routed DHCP lab — the Discover broadcast never leaves the client's local segment without it.
2. **Assuming the DHCP Discover's source IP is the address the client is about to get.** It's `0.0.0.0` — the client has no address yet, by definition.
3. **Forgetting to make the DHCP server's own address static.** A DHCP server on DHCP is a bootstrapping contradiction.
4. **Leaving PC1 on Static IP configuration mode instead of switching the radio button to DHCP.** Trivial, but a very common miss in Packet Tracer specifically.
5. **Not excluding the DHCP server, gateway, or router addresses from the DHCP pool's range**, causing an eventual lease collision with a statically-assigned device.
6. **Confusing "the Request in step 3 is broadcast" with a mistake** — students often assume once the client has an offer, subsequent messages should immediately go unicast. The Request stays broadcast specifically so any other DHCP server that made a competing offer also hears it and releases its offered address.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC1 shows `0.0.0.0` or an Automatic Private IP (169.254.x.x) | DHCP Discover never reached the server (no relay, wrong subnet) | `show run \| include helper` on R1 | Add `ip helper-address <DHCP-server-IP>` on the client-facing interface |
| 2 | PC1 gets no response at all, even locally | DHCP service not enabled on SRV1, or wrong pool subnet configured | Check SRV1 → Services → DHCP → ON, pool matches PC1's subnet | Enable service, correct pool |
| 3 | PC1 gets an IP, but it's outside the expected `192.168.1.0/24` range | Wrong pool subnet/mask configured on SRV1 | Inspect DHCP pool config on SRV1 | Correct the pool's network/mask |
| 4 | Static devices (R1, SRV1) can't reach each other | Missing static route on R1 or R2 | `show ip route` | Add the missing route from Section 6.1/6.2 |
| 5 | Simulation Mode shows the Discover frame dying at R1 | No `ip helper-address`, and routers don't forward broadcasts by design | Watch the PDU list step-by-step in Simulation Mode | Same fix as Step 1 |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why put the DHCP server on a different subnet than the client instead of directly on the same LAN?** In real enterprises, DHCP servers are almost always centralized (often colocated with other core services) rather than one per branch LAN — this lab deliberately places SRV1 across a WAN hop to force the `ip helper-address` lesson, which is exactly the scenario a junior engineer will hit in production the first time they build a routed network with a central DHCP server.
- **Why not just give R1 its own local DHCP pool instead of relaying?** A router *can* act as a DHCP server itself (`ip dhcp pool`), and that's a valid design for small branch offices. But centralizing DHCP (with relay) scales far better — one team manages one pool with consistent policy, instead of dozens of branch routers each running independent, potentially inconsistent DHCP configuration.
- **Why does the DHCP Request stay broadcast in step 3 of DORA instead of going straight to unicast?** Because more than one DHCP server might have answered the original Discover with competing Offers — broadcasting the Request lets every server that offered see whether the client accepted *their* offer or someone else's, so the losing server(s) know to release the address they tentatively reserved.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a new office's laptops all show "limited connectivity" and the fix turns out to be a missing `ip helper-address` on the branch router, because the company's DHCP server lives in a central datacenter.
- ...you're troubleshooting "some users get IPs, some don't" and the actual cause is a DHCP pool that's simply run out of leases — a scope-sizing problem, not a routing problem.
- ...security asks "can you tell me which device had this IP address at 3pm yesterday" and the answer comes straight from DHCP lease logs.
- ...you're explaining to a non-technical manager why "the network is down" could mean five completely different things depending on which OSI layer actually failed — this lab is the first time that distinction becomes concrete rather than academic.

---

## 12. Stretch Goal

1. Add a second DHCP scope on a different VLAN/subnet and configure a second `ip helper-address` so R1 relays to both a primary and secondary DHCP server, then simulate the primary server going down.
2. Capture and diagram the *full* encapsulation/de-encapsulation stack for a DHCP Offer as it crosses from SRV1's NIC to PC1's NIC, labeling every header added and removed at each hop (including at R1 and R2, where the L2 header is stripped and rebuilt on every hop while the L3 header survives unchanged).
3. Explain, without looking anything up, what would break if `ip helper-address` pointed at the wrong IP — trace the failure using only Simulation Mode.

---

## 13. Self-Assessment

- [ ] Can you name all four DORA messages in order, from memory, and explain why the acronym has that abbreviation?
- [ ] Can you explain why a DHCP Discover's source IP is `0.0.0.0`, not "whatever address it's about to get"?
- [ ] Can you explain what `ip helper-address` does and where it's applied (which interface, which router)?
- [ ] Can you name the OSI layer and protocol responsible for each of: MAC addressing, IP addressing, port numbers, and the DHCP message itself?
- [ ] Could you diagram encapsulation (top-down) and de-encapsulation (bottom-up) from memory?

---

## 14. Key Concepts Demonstrated

- OSI model layers mapped to real captured packet fields
- DHCP DORA sequence and broadcast vs. unicast behavior at each step
- Encapsulation/de-encapsulation across a routed hop
- DHCP relay (`ip helper-address`) across subnet boundaries

## What I Learned

Watching a single DHCP Discover frame move through Simulation Mode made the OSI model concrete in a way no diagram ever did — the source IP being `0.0.0.0`, the destination MAC being all-Fs, the same UDP ports appearing on every exchange. It also surfaced a genuinely important real-world skill: recognizing that a client stuck with no IP address, sitting across a router from its DHCP server, is a routing/relay problem, not a "DHCP is broken" problem — those are very different tickets with very different fixes.

## Skills Practiced

- OSI model layer identification from live packet captures
- DHCP DORA sequence analysis
- DHCP server and scope configuration
- DHCP relay agent configuration
- Packet Tracer Simulation Mode packet inspection

---

## 15. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco 2911 | VyOS |
| Switches (SW1, SW2) | Cisco 2960 | Open vSwitch |
| PC1, SRV1 | Generic PC/Server | Alpine Linux |

Note: GNS3's Alpine Linux and VyOS both support real DHCP client/server behavior, but there is no built-in packet-capture "Simulation Mode" equivalent to Packet Tracer's PDU inspector — use Wireshark against a GNS3 link (right-click a link → Start capture) to replicate the DORA packet inspection from Section 7.

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script.
