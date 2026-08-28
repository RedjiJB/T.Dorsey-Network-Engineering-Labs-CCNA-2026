# Day 23 Lab Manual — EtherChannel: LACP, PAgP, Static, and Load Balancing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Bundle redundant switch-to-switch links into single logical interfaces using LACP, PAgP, and static EtherChannel, at both Layer 2 (trunk) and Layer 3 (routed), and tune load-balancing hashing. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): EtherChannel (LACP/PAgP), trunking. Domain 4 (IP Connectivity): routed port-channels, static routing over a bundled link. |
| **Prerequisites** | VLANs and trunking (802.1Q), basic switch interface configuration, static routing fundamentals. |
| **Time Estimate** | 2 – 2.5 hours first attempt; 30–40 minutes on repeat. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — conceptually simple, but negotiation-protocol mismatches are a classic exam and real-world trap. |

---

## 1. Lab Overview + Learning Objectives

Two access switches (ASW1, ASW2) each connect to a distribution switch (DSW1, DSW2) over **two physical links** that get bundled into one logical `Port-channel` interface. DSW1 and DSW2 are then connected to each other over a **Layer 3 routed** EtherChannel, carrying inter-VLAN traffic between the two access-layer subnets.

By the end of this lab you will be able to:

- Explain the difference between LACP (IEEE 802.3ad, `active`/`passive`), PAgP (Cisco proprietary, `desirable`/`auto`), and static (`on`) EtherChannel negotiation
- Bundle multiple physical interfaces into a Layer 2 trunk port-channel
- Bundle multiple physical interfaces into a Layer 3 routed port-channel with its own IP address
- Read `show etherchannel summary` flags to diagnose bundle state
- Identify and change a switch's global EtherChannel load-balancing hash
- Route between two subnets across a redundant, load-balanced core link

---

## 2. Business Context

**Why would a real company do this?**

A single 1G or 10G uplink between an access switch and its distribution switch is both a bandwidth bottleneck and a single point of failure. Buying a faster (and pricier) uplink module is one option; the cheaper, more common option is to run two or four ordinary links in parallel and logically bundle them into one fat pipe with EtherChannel. This is standard practice in almost every wiring closet:

- **"We keep losing the switch uplink during patch-panel work"** → bundling two physical links means one can be unplugged, re-terminated, or fail outright, and traffic keeps flowing on the survivor with zero reconvergence delay (no STP recalculation, no routing protocol reconvergence — the bundle just drops a member).
- **"Our distribution-to-distribution link is saturated"** → a Layer 3 routed EtherChannel between DSW1 and DSW2 doubles available core bandwidth without buying new hardware.
- **"IT keeps plugging things in with mismatched settings and breaking the uplink"** → this is exactly why the lab deliberately breaks PAgP with a DTP mismatch: it is the single most common real-world EtherChannel outage, and every engineer needs to recognize the symptom instantly (`suspended` ports, halved bandwidth, no obvious link-down alarm because the physical link is still up).
- **"How do we keep both links actually busy instead of one idle backup?"** → load-balancing hash configuration. Without deliberate tuning, all traffic between the same MAC/IP pair rides one physical member and the second sits mostly idle "just in case," defeating half the purpose of bundling.

This is the kind of link a network engineer touches constantly at the access/distribution boundary — get the negotiation mode wrong and you have silently halved your bandwidth without a single interface going "down."

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-23-Lab-EtherChannel.png" alt="Day 23 EtherChannel Lab" width="900">
</p>

```text
PC1 -- ASW1 ==LACP(2 links)== DSW1 ==Static L3 PortChannel(2 links)== DSW2 -- ASW2 ==PAgP(2 links)-- SRV1(via ASW2 subnet)
```

| Device | Model | Interfaces Used | Role |
|---|---|---|---|
| ASW1 | 2960-24TT | G1/0/3, G1/0/4 | Access switch, LACP trunk to DSW1 |
| ASW2 | 2960-24TT | G1/0/3, G1/0/4 | Access switch, PAgP trunk to DSW2 |
| DSW1 | 3650-24PS | G1/0/1-2 (to DSW2), G1/0/3-4 (to ASW1) | Distribution switch |
| DSW2 | 3650-24PS | G1/0/1-2 (to DSW1), G1/0/3-4 (to ASW2) | Distribution switch |
| PC1/PC2 | PC | — | 172.16.1.0/24, behind ASW1/DSW1 |
| SRV1 | Server | — | 172.16.2.0/24, behind ASW2/DSW2 |

---

## 4. IP Addressing Plan

| Segment | Network | Usable Range | Sizing Reason |
|---|---|---|---|
| ASW1 access VLAN (PCs) | 172.16.1.0 /24 | .1 – .254 | User LAN, sized for growth |
| ASW2 access VLAN (server) | 172.16.2.0 /24 | .1 – .254 | Server segment, sized for growth |
| DSW1 ↔ DSW2 L3 port-channel | 10.0.0.0 /30 | .1 – .2 | Point-to-point routed link between exactly two devices, never needs more than 2 hosts |

### 4.1 Manual Calculation — the DSW1↔DSW2 Link

**Step 1 — hosts needed.** A routed port-channel between two distribution switches is still logically *one link between two endpoints*, no matter how many physical members are bundled underneath it — the Port-channel interface itself gets exactly one IP per side. So: 2 usable hosts.

**Step 2 — solve for host bits `h`:**
```text
2^h − 2 ≥ 2
2^1 − 2 = 0   too small
2^2 − 2 = 2   fits exactly
```
`h = 2` → prefix = 32 − 2 = **/30**.

**Step 3 — binary-to-decimal mask derivation:**
```text
/30 = 11111111.11111111.11111111.11111100
    =     255 .     255 .     255 .    252
```

**Step 4 — network/host/broadcast for 10.0.0.0/30:**
```text
Network address:    10.0.0.0     (host bits all 0)
First usable host:  10.0.0.1     (DSW1 Port-channel12)
Last usable host:   10.0.0.2     (DSW2 Port-channel12)
Broadcast address:  10.0.0.3     (host bits all 1)
```
Block size shortcut: with `h = 2`, block size = 2^2 = 4 → networks fall on 10.0.0.0, 10.0.0.4, 10.0.0.8… so the next /30 after this one starts at 10.0.0.4, useful if this lab is later expanded with a third distribution switch.

---

## 5. Pre-Configuration Checklist

- [ ] Confirm which physical interfaces are cabled between each switch pair before configuring anything — mismatched port numbers is the #1 cause of "the channel just won't come up."
- [ ] Verify no IP address is pre-configured on any physical member interface destined for the L3 port-channel (duplicate/conflicting IP errors block bundling).
- [ ] Verify VLAN 1 (or whatever native/access VLAN carries PC/SRV traffic) exists on all four switches before trunking.
- [ ] Decide negotiation mode per link *before* touching the CLI: LACP=`active/active`, PAgP=`desirable/desirable`, static=`on/on`. Mixing modes across a single bundle is the deliberate failure case in Task 2 of this lab.
- [ ] Have `show etherchannel summary` output memorized well enough to read the flag legend without looking it up mid-lab.

---

## 6. Configuration Tasks

### 6.1 Task 1 — Layer 2 LACP EtherChannel (ASW1 ↔ DSW1)

```cisco
! ASW1 — global config mode
conf t
interface range GigabitEthernet1/0/3 - 4
 channel-group 1 mode active
 spanning-tree portfast trunk
 no shutdown
interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
```
- `channel-group 1 mode active` (interface config mode): places both physical interfaces into logical bundle 1 using **LACP**, and `active` means "I will start negotiating unprompted." **Memory aid:** LACP is the open-standard (IEEE 802.3ad) protocol — "**a**ctive **a**sks" first.
- `spanning-tree portfast trunk`: tells STP this trunk-mode edge won't create a loop through an unknown switch, skipping the listening/learning delay. Only safe here because we know exactly what's on the other end.
- `switchport trunk encapsulation dot1q` (Port-channel interface mode): required on platforms supporting both ISL and 802.1Q before `switchport mode trunk` will accept — sets the tagging standard.
- `switchport mode trunk`: makes the *logical* Port-channel interface a trunk; this setting rides down to the member ports automatically once bundled.

```cisco
! DSW1 — mirror the LACP config
conf t
interface range GigabitEthernet1/0/3 - 4
 channel-group 1 mode active
 no shutdown
interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
```
Both ends use `active` — LACP requires at least one side to be `active`; `active/active` and `active/passive` both work, but `passive/passive` never negotiates (neither side speaks first).

### 6.2 Task 2 — Layer 2 PAgP EtherChannel (ASW2 ↔ DSW2), including the deliberate mismatch

```cisco
! ASW2
conf t
interface range GigabitEthernet1/0/3 - 4
 channel-group 1 mode desirable
 spanning-tree portfast trunk
 no shutdown
interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk

! DSW2 — must also be desirable (or auto) to negotiate
conf t
interface range GigabitEthernet1/0/3 - 4
 channel-group 1 mode desirable
 no shutdown
interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
```
- `channel-group 1 mode desirable`: PAgP (Cisco proprietary) equivalent of LACP `active` — **memory aid:** "PAgP" and "**P**roactive" — `desirable` proactively negotiates, `auto` waits passively, same active/passive relationship as LACP.

**Deliberately break it** to see the failure mode (set one side to `on` instead of `desirable`):
```cisco
! On DSW2 only, for demonstration
interface range GigabitEthernet1/0/3 - 4
 channel-group 1 mode on
```
Result:
```
%EC-5-CANNOT_BUNDLE2: Gig1/0/3 is not compatible with Gig1/0/3
and will be suspended (dtp mode of Gig1/0/3 is on, Gig1/0/3 is off)
```
`mode on` never sends negotiation frames at all, so a `desirable` peer waiting for a PAgP reply gets nothing and suspends the port. Revert DSW2 back to `desirable` before continuing.

### 6.3 Task 3 — Layer 3 Static EtherChannel (DSW1 ↔ DSW2)

```cisco
! DSW1
conf t
interface range GigabitEthernet1/0/1 - 2
 channel-group 12 mode on
 no switchport
 no shutdown
interface Port-channel12
 no switchport
 ip address 10.0.0.1 255.255.255.252

! DSW2
conf t
interface range GigabitEthernet1/0/1 - 2
 channel-group 12 mode on
 no switchport
 no shutdown
interface Port-channel12
 no switchport
 ip address 10.0.0.2 255.255.255.252
```
- `mode on`: static bundling, no negotiation protocol at all — both sides simply assume the other is also bundling. Works instantly but gives zero protection against a misconfigured or half-cabled peer; production networks prefer LACP specifically because it *tells you* when something's wrong instead of silently forwarding into a black hole.
- `no switchport` (interface config mode, both physical members **and** the Port-channel interface): converts from Layer 2 switchport to a Layer 3 routed port. Must be applied consistently — a Layer 3 bundle cannot mix switchport and routed members.
- IP address is assigned to the **Port-channel interface only**, never the physical members — assigning it to a member interface is a common misconfiguration that either errors out or creates duplicate-IP chaos.

### 6.4 Task 4 — Static Routes for PC-to-Server Reachability

```cisco
! DSW1 — route to the ASW2/server subnet via DSW2
conf t
ip route 172.16.2.0 255.255.255.0 10.0.0.2

! DSW2 — route to the ASW1/PC subnet via DSW1
conf t
ip route 172.16.1.0 255.255.255.0 10.0.0.1
```
- `ip route <destination-network> <mask> <next-hop>` (global config mode): tells each distribution switch how to reach the subnet on the *other* switch's side, using the routed Port-channel's IP as next hop. Because the underlying link is bundled, this single static route survives the loss of one physical member with no route recalculation.

### 6.5 Task 5 — Identify Default Load-Balancing Method

```cisco
show etherchannel load-balance
```
On Catalyst 2960/3560/3650 platforms the factory default is `src-mac` (Source MAC address only). This means every frame between the same two MAC addresses always hashes to the *same* physical member — fine for many-to-many traffic, poor for two devices exchanging heavy sustained traffic (all of it rides one link).

### 6.6 Task 6 — Configure Source/Destination IP Load Balancing (global, all four switches)

```cisco
! On ASW1, ASW2, DSW1, and DSW2 — identical command, global config mode
conf t
port-channel load-balance src-dst-ip
```
- **Why it matters:** this setting is *global per switch* — it applies to every port-channel on that device, there is no per-bundle override on most Catalyst platforms. `src-dst-ip` hashes on the XOR of source and destination IP, spreading traffic between many host pairs more evenly than `src-mac` alone, especially useful on the DSW1↔DSW2 routed link carrying many different PC-to-server flows.
- **Memory aid:** think of the hash inputs as a funnel — the more distinct fields you feed it (src+dst rather than src alone), the more evenly flows spray across members.

---

## 7. Verification Steps

| Command | Purpose |
|---|---|
| `show etherchannel summary` | Bundle membership and state flags — the primary health check |
| `show interfaces port-channel 1` | Line/protocol status, bandwidth of the logical interface |
| `show interfaces trunk` | Confirms trunk is active and which VLANs are allowed |
| `show ip interface brief` | Confirms Port-channel12's IP is up/up on DSW1/DSW2 |
| `show ip route` | Confirms static routes installed |
| `show etherchannel load-balance` | Confirms active hashing algorithm |
| `ping 172.16.2.1` (from a PC1-side host) | End-to-end reachability across the bundled core |

### Expected Output Gallery

```text
DSW1# show etherchannel summary
Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        R - Layer3      S - Layer2
        U - in use       N - not in use, no aggregation

Group  Port-channel  Protocol   Ports
------+-------------+-----------+-----------------------------------------------
1      Po1(SU)       LACP       Gi1/0/3(P)   Gi1/0/4(P)
12     Po12(RU)      -          Gi1/0/1(P)   Gi1/0/2(P)
```

```text
DSW1# show ip route
      10.0.0.0/30 is subnetted, 1 subnets
C        10.0.0.0 is directly connected, Port-channel12
S     172.16.2.0/24 [1/0] via 10.0.0.2
```

```text
ASW2# show etherchannel summary  (during the deliberate PAgP mismatch)
Group  Port-channel  Protocol   Ports
------+-------------+-----------+-----------------------------------------------
1      Po1(SD)       PAgP       Gi1/0/3(I)   Gi1/0/4(I)
```

```text
DSW1# show etherchannel load-balance
EtherChannel Load-Balancing Operational State (src-dst-ip):
Non-IP: Source XOR Destination MAC address
IPv4:   Source XOR Destination IP address
IPv6:   Source XOR Destination IP address
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Mismatched negotiation modes across the two ends** (`active`/`on`, `desirable`/`on`) — accounts for the overwhelming majority of "why won't my channel bundle" issues. Fix: match modes exactly.
2. **Assigning an IP to a physical member interface** instead of only the Port-channel interface on a routed bundle.
3. **Forgetting `no switchport` on both member interfaces AND the Port-channel** when building a Layer 3 bundle — leaving even one member as Layer 2 blocks the routed bundle from forming cleanly.
4. **Different trunk encapsulation or VLAN allowed-list on each end** of a Layer 2 bundle, producing a `Po(susp)` pending state distinct from the DTP mismatch.
5. **Assuming load-balancing config is per-port-channel** — it's global to the switch; forgetting to apply it identically on every switch in the path causes uneven, hard-to-diagnose traffic distribution.

---

## 9. Troubleshooting Guide

| Step | Check | Command | Likely Finding |
|---|---|---|---|
| 1 | Are both physical links up? | `show interfaces status` | A member is `notconnect` (bad cable/port) |
| 2 | Do bundle flags show `(P)` on both ends? | `show etherchannel summary` | `(I)` means stand-alone — negotiation failed |
| 3 | Do negotiation modes match? | `show run interface <member>` on both switches | One side `active`, other `on` — mismatch |
| 4 | Any suspend/error log? | `show logging \| include EC-5` | `%EC-5-CANNOT_BUNDLE2` confirms DTP/mode mismatch |
| 5 | Trunk settings identical? | `show interfaces trunk` | Native VLAN or allowed-VLAN mismatch |
| 6 | Routed bundle up but no reachability? | `show ip route`, `ping` | Missing static route on one distribution switch |
| 7 | Traffic all riding one member? | `show etherchannel load-balance`, `show interfaces port-channel <n>` member counters | Load-balance method mismatched or too few distinct src/dst pairs to spread |

---

## 10. Design Analysis

**LACP vs. PAgP vs. static — why LACP wins in production.** LACP is an open IEEE standard (802.3ad), works across vendors, and actively negotiates — if the peer's configuration changes or a link degrades, LACP notices and can react. PAgP is Cisco-proprietary (Catalyst-to-Catalyst only) but functions almost identically; it exists in this lab primarily to contrast against LACP and to demonstrate the DTP-mismatch failure mode. Static (`mode on`) negotiates nothing at all — fast to configure, works with any device including some that don't speak LACP/PAgP, but gives zero protection: if a peer isn't actually bundling on its side, static mode still forwards traffic into the void. Real deployments default to LACP unless connecting to legacy gear that can't speak it.

**Why a routed (Layer 3) bundle between distribution switches instead of a Layer 2 trunk + SVI.** Routing directly on the Port-channel interface avoids running STP across the DSW1–DSW2 link entirely (no blocked/forwarding calculations, no convergence delay on failover) and keeps the distribution-to-distribution link a pure Layer 3 hop, which is the standard "routed core" design pattern — Layer 2 domains stay contained at the access layer, Layer 3 boundaries start at distribution.

---

## 11. Real-World Parallel

You'll see this exact pattern in almost any enterprise wiring closet: access switches home-run two (or four) uplinks to distribution/core switches, bundled with LACP for resilience and throughput. Hypervisor hosts (VMware, Hyper-V) bundle NICs to ToR switches the same way. Data-center fabrics use the Layer-3-routed-bundle pattern between spine and leaf switches constantly, precisely to avoid running STP in the core.

---

## 12. Stretch Goal

Add a third physical link to the ASW1↔DSW1 LACP bundle, then shut down one of the three members mid-`ping -t` and observe that the flow continues uninterrupted while `show etherchannel summary` reflects one fewer bundled port. Then experiment with `port-channel min-links` to require a minimum number of active members before the bundle stays up at all.

---

## 13. Self-Assessment Checklist

- [ ] I can explain LACP `active`/`passive` vs PAgP `desirable`/`auto` vs static `on` without notes
- [ ] I can read `show etherchannel summary` flags and identify a suspended vs bundled port
- [ ] I can configure a Layer 3 routed EtherChannel from scratch, including `no switchport`
- [ ] I know load-balancing configuration is global per switch, not per-bundle
- [ ] I can diagnose a DTP/negotiation-mode mismatch from log output alone

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

LACP vs PAgP matters in real environments — mismatched negotiation modes don't gracefully fall back, they leave standby ports that silently halve bandwidth. Reading summary flags correctly (`P`=bundled, `I`=stand-alone, `D`=down, `S`=Layer2, `R`=Layer3) is the core diagnostic skill. Layer 3 EtherChannel is just a routed Port-channel — same channel-group mechanics, `no switchport` plus IP on the Port-channel interface instead of trunk config. Load-balancing symmetry across switches matters: mismatched hash algorithms on either side of the same bundle cause uneven distribution and can overload one physical link.

**Skills practiced:** LACP/PAgP/static EtherChannel configuration, Layer 2 vs Layer 3 bundling, DTP negotiation troubleshooting, static routing over a bundled core link, global load-balance tuning.

---

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-23/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using Open vSwitch (switch roles) and VyOS (routed-port-channel roles).
