# Day 02 Lab Manual — Connecting Network Devices (Cabling & Physical Layer)

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a two-site enterprise topology and select the correct cable type (straight-through copper, crossover copper, multi-mode fiber, single-mode fiber) for every connection based on device type and transmission distance, then layer a basic IP addressing plan on top so the physical design has something real to carry. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): 1.2 (physical interfaces and cabling types), 1.3 (interface and cable issues), 1.1 (device roles). This is one of the few labs that is tested almost entirely by "given a scenario, pick the right cable" — a recurring exam question type. |
| **Prerequisites** | Day 01 (device roles and basic topology reading). No prior addressing experience required — a light addressing pass is included here, but the emphasis is physical layer. |
| **Time Estimate** | 1.5 – 2 hours (first attempt); 30 minutes on repeat/review. |
| **Difficulty** | ⭐☆☆☆☆ (Beginner) — no CLI configuration risk, but the cable-selection reasoning is a genuine, frequently-missed exam skill. |

---

## 1. Lab Overview

This lab builds two independent branch topologies (Site A and Site B) and focuses entirely on **choosing the correct physical medium** for each link — copper straight-through, copper crossover, multi-mode fiber, or single-mode fiber — based on two factors: what kind of device is on each end, and how far apart they are.

Unlike Day 01, there is no firewall and no NAT here. The lesson is deliberately narrow: get the *physical* layer right first, because nothing above Layer 1 works if the cabling is wrong, and Packet Tracer (and real hardware) will silently refuse to link an interface if you pick the wrong cable type for the two endpoints involved.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- State the rule for when a straight-through cable is required vs. a crossover cable, including the "unlike devices vs. like devices" heuristic and why modern hardware often makes this rule less strict (Auto-MDI-X)
- Choose between multi-mode and single-mode fiber based on realistic distance requirements
- Build a two-site topology in Packet Tracer with correctly cabled routers, switches, and end devices
- Apply a basic IP addressing plan across both sites
- Verify Layer 1/2 connectivity using `show` commands and interpret link-light/status behavior
- Explain, in business terms, why cable and medium selection is a real cost and reliability decision, not a checkbox

---

## 2. Business Context

**Why would a real company do this?**

A network engineer rarely gets to redesign a whole enterprise from scratch — far more often, the job is "we're opening Site B, and it needs to talk to Site A." That single sentence hides a string of physical-layer decisions that cost real money if you get them wrong:

- **"Site A and Site B are in different buildings on the same campus."** → this is exactly the 250-meter R3–R4 link in this lab. Copper Ethernet is only rated for reliable operation up to 100 meters before signal degradation becomes a problem — so anything building-to-building on a campus needs fiber. Multi-mode fiber is the standard, cost-effective choice at this distance; it's cheaper than single-mode transceivers and more than sufficient.
- **"Site A and Site C are across town, 3 km apart."** → this is the R1–R3 link. Multi-mode fiber's practical range tops out well under a kilometer for most transceiver classes; anything genuinely long-haul needs single-mode fiber, which uses a narrower core and a laser (not LED) light source to travel kilometers with minimal attenuation. ISPs and telecom carriers build entire businesses on single-mode fiber for exactly this reason.
- **"We're just wiring a wiring closet — router to switch, switch to PCs."** → ordinary copper Ethernet, well under the 100 m limit, is the correct and cheapest answer. Over-speccing fiber for a 2-meter patch-panel run wastes money on transceivers the link will never need.
- **"Procurement wants to know why the fiber budget line item exists at all."** → this is precisely the kind of question a junior engineer must be able to answer with the reasoning in Section 2 of this manual, not just "the diagram said so."

The underlying business truth: cable and medium selection is a **capital cost decision** disguised as a technical one. A company that runs single-mode fiber into every wiring closet is wasting money; a company that tries to run copper between buildings is signing up for a support ticket the day someone measures the actual distance.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-02-Connecting-Devices.png" alt="Day 02 Connecting Devices Lab" width="1000">
</p>

### 3.1 Site A (Branch Office)

```text
PC1 -- SW3 \
             SW1 -- R2 (LAN)
PC2 -- SW4 /  \
            SW2 --/
```

Devices: `R1`, `R2`, `SW1`, `SW2`, `SW3`, `SW4`, `PC1`, `PC2`

### 3.2 Site B (Second Branch)

```text
PC3  -- SW7 \
              SW5 -- R4 (LAN)
SRV1 -- SW8 /  \
             SW6 --/
```

Devices: `R3`, `R4`, `SW5`, `SW6`, `SW7`, `SW8`, `PC3`, `SRV1`

### 3.3 Inter-Site / Router Links

| Link | Distance | Medium |
|---|---|---|
| R1 ↔ R2 (within Site A) | 50 m | Copper straight-through |
| R3 ↔ R4 (within Site B) | 250 m | Multi-mode fiber |
| R1 ↔ R3 (Site A ↔ Site B) | 3 km | Single-mode fiber |

---

## 4. IP Addressing Plan

This lab's focus is physical media, so the addressing plan is intentionally lightweight — but every real cabling job eventually carries real traffic, so we assign one anyway.

### 4.1 Why Sized This Way

| Segment | Hosts needed | Why this prefix |
|---|---|---|
| Site A LAN (behind R2) | PC1, PC2, headroom | `/24` — standard user LAN sizing, same reasoning as Day 01 |
| Site B LAN (behind R4) | PC3, SRV1, headroom | `/24` — same reasoning |
| R1 ↔ R2 (copper) | Exactly 2 | `/30` — point-to-point link, never needs a third address |
| R3 ↔ R4 (multi-mode fiber) | Exactly 2 | `/30` — same reasoning; the *medium* changes, the addressing math doesn't |
| R1 ↔ R3 (single-mode fiber) | Exactly 2 | `/30` — same reasoning again |

**Key teaching point:** the cable/medium you choose (copper, multi-mode, single-mode) is a *physical layer* decision. The subnet size is a *Layer 3* decision driven purely by host count. Students commonly (wrongly) assume "long fiber link = bigger subnet" — it doesn't. A 3 km single-mode link between two router interfaces is still exactly 2 hosts, still a `/30`.

### 4.2 Manual Calculation Walkthrough

Worked example for any of the three router-to-router `/30` links:

```text
Requirement: exactly 2 usable host addresses (one per router interface)

usable hosts = 2^h − 2
2^1 − 2 = 0   → too small
2^2 − 2 = 2   → exactly fits

h = 2 host bits → prefix = 32 − 2 = /30
```

Binary mask derivation:

```text
/30 = 11111111.11111111.11111111.111111 00
    =     255  .    255 .    255 .    252
```

Applied to `10.0.12.0/30` (R1 ↔ R2):

```text
Network address:    10.0.12.0     (all host bits = 0)
First usable host:  10.0.12.1     (R1's interface)
Last usable host:   10.0.12.2     (R2's interface)
Broadcast address:  10.0.12.3     (all host bits = 1)
```

**Block-size shortcut:** for `/30`, block size = `256 − 252 = 4`. So consecutive `/30` networks land on `.0, .4, .8, .12...` — this is why the three router links below use `.0`, `.4`, and `.8` rather than arbitrary numbers.

### 4.3 Full Device Address Table

| Device | Interface | IP Address | Mask | Connects To |
|---|---|---|---|---|
| PC1 | NIC | 192.168.1.10 | 255.255.255.0 | SW3 |
| PC2 | NIC | 192.168.1.11 | 255.255.255.0 | SW4 |
| R2 | Gi0/0 (LAN) | 192.168.1.1 | 255.255.255.0 | SW1 |
| R1 | Gi0/0 | 10.0.12.1 | 255.255.255.252 | R2 Gi0/1 |
| R2 | Gi0/1 | 10.0.12.2 | 255.255.255.252 | R1 Gi0/0 |
| R1 | Gi0/1 (fiber) | 10.0.20.1 | 255.255.255.252 | R3 Gi0/1 (fiber) |
| R3 | Gi0/1 (fiber) | 10.0.20.2 | 255.255.255.252 | R1 Gi0/1 (fiber) |
| R3 | Gi0/0 (fiber) | 10.0.8.1 | 255.255.255.252 | R4 Gi0/1 (fiber) |
| R4 | Gi0/1 (fiber) | 10.0.8.2 | 255.255.255.252 | R3 Gi0/0 (fiber) |
| R4 | Gi0/0 (LAN) | 192.168.2.1 | 255.255.255.0 | SW5 |
| PC3 | NIC | 192.168.2.10 | 255.255.255.0 | SW7 |
| SRV1 | NIC | 192.168.2.11 | 255.255.255.0 | SW8 |

**Default gateways:** PC1/PC2 → `192.168.1.1`; PC3/SRV1 → `192.168.2.1`.

---

## 5. Pre-Configuration Checklist

1. Place all 8 Site A devices and all 8 Site B devices in Packet Tracer per the topology.
2. Before cabling anything, write next to each planned link which cable type you intend to use — this lab is graded on that decision as much as the result.
3. Have the Cable Selection Summary table (Section 6.4) open for reference while cabling.
4. Confirm Packet Tracer's automatic cable-type suggestion (the small icon shown when you hover a connection type in the cable palette) matches your own reasoning — don't just trust it blindly; know *why*.

---

## 6. Configuration Tasks

### 6.1 The Cabling Rule (learn this before touching Packet Tracer)

**Straight-through cable** — used between **unlike devices** (their pin-outs are wired to naturally match): router↔switch, switch↔PC, switch↔server.

**Crossover cable** — used between **like devices** (same pin-out on both ends, so the cable itself must cross transmit/receive pairs): switch↔switch, router↔router (copper), PC↔PC.

> **Memory aid:** "Like needs a cross, unlike needs a straight line between them." If you're connecting two of the *same kind* of device, you cross the wires; if you're connecting *two different kinds*, they already talk past each other correctly.

> **Modern caveat worth knowing for the exam and for real life:** most switches and NICs made since the mid-2000s support **Auto-MDI-X**, which senses the cable and electrically swaps pairs as needed — meaning a straight-through cable often "just works" even switch-to-switch on real hardware today. CCNA still tests the traditional straight-through/crossover rule because Packet Tracer enforces it strictly and because you need to recognize wrong cabling on legacy gear that lacks Auto-MDI-X.

### 6.2 Fiber Medium Selection

**Multi-mode fiber (MMF)** uses a wider core and an LED or low-cost laser source. Light bounces (multiple modes) down the core, which causes modal dispersion — signal degradation that limits reliable distance to roughly 300–2000 m depending on the transceiver class (this lab's 250 m R3–R4 link sits comfortably inside that range).

**Single-mode fiber (SMF)** uses a much narrower core so only one path (mode) of light travels straight down the fiber, avoiding modal dispersion. Paired with a laser source, SMF reliably carries signal for kilometers to tens of kilometers — the 3 km R1–R3 link requires it.

> **Memory aid:** "Single mode, single path, long-haul. Multi mode, multiple paths, medium-haul." If the distance is measured in kilometers, default to single-mode; if it's measured in tens to a few hundred meters, multi-mode is usually the economical choice; if it's measured in meters, copper is almost always both cheaper and sufficient.

### 6.3 Building Site A

**Step 1 — Place devices:** `R1`, `R2`, `SW1`, `SW2`, `SW3`, `SW4`, `PC1`, `PC2` per Section 3.1.

**Step 2 — Cable using straight-through:**
- `R2` → `SW1` (router to switch = unlike devices)
- `R2` → `SW2` (same reasoning; R2 has two LAN-facing interfaces feeding two switches for redundancy)
- `SW3` → `PC1` (switch to PC = unlike devices)
- `SW4` → `PC2` (same reasoning)

**Step 3 — Cable using crossover:**
- `SW1` → `SW2` (switch to switch = like devices)
- `SW1` → `SW3`
- `SW2` → `SW4`

**Step 4 — Cable R1 to R2 (50 m, within the same site):**
- Copper straight-through STP/UTP. At 50 m, well inside copper's 100 m reliable range — no fiber justified.

> In Packet Tracer, router-to-router links use a straight-through cable even though routers are "like devices," because router Ethernet ports are wired like switch/host ports on the interface itself, not like a second switch — always check your platform's actual cabling logic if the like/unlike rule seems to disagree with what connects. Packet Tracer will refuse a link if you pick the wrong type, which is your built-in check.

### 6.4 Building Site B

Repeat Site A's pattern with fiber for the inter-router link:

- `R4` → `SW5`, `R4` → `SW6`: straight-through
- `SW7` → `PC3`, `SW8` → `SRV1`: straight-through
- `SW5` → `SW6`, `SW5` → `SW7`, `SW6` → `SW8`: crossover
- `R3` ↔ `R4`: **multi-mode fiber**, 250 m — select the fiber port/module on both routers in Packet Tracer (not the copper FastEthernet/GigabitEthernet port) before attempting the link.

### 6.5 The Inter-Site Link: R1 ↔ R3

- **Medium: single-mode fiber**, 3 km.
- In Packet Tracer, this requires adding a fiber interface module (if not present by default on the router model used) to both R1 and R3, then running the single-mode fiber cable type between them.

### 6.6 Basic Router Configuration (so the addressing plan in Section 4 is actually live)

For each router (`R1`, `R2`, `R3`, `R4`), repeat this pattern — shown here for `R2`:

```text
Router>enable
Router#configure terminal
Router(config)#hostname R2
R2(config)#interface gigabitEthernet 0/0
R2(config-if)#description LAN - SW1/SW2
R2(config-if)#ip address 192.168.1.1 255.255.255.0
R2(config-if)#no shutdown
R2(config-if)#exit
R2(config)#interface gigabitEthernet 0/1
R2(config-if)#description To R1
R2(config-if)#ip address 10.0.12.2 255.255.255.252
R2(config-if)#no shutdown
R2(config-if)#exit
```

> **Mode:** Global Config → Interface Config. `no shutdown` is required on every interface — Cisco IOS interfaces boot administratively down by default, fiber ports included. On a fiber interface, `no shutdown` alone isn't sufficient if the far end isn't also up and the correct cable type isn't in place — unlike copper, a fiber link needs both strands (transmit/receive) correctly connected, so a single reversed fiber pair will show `up/down` (line protocol down) even with `no shutdown` issued.

Apply the equivalent addressing to `R1`, `R3`, and `R4` per the table in Section 4.3. Add static routes so PCs on each site can reach the other:

```text
R1(config)#ip route 192.168.2.0 255.255.255.0 10.0.20.2
R2(config)#ip route 0.0.0.0 0.0.0.0 10.0.12.1
R3(config)#ip route 192.168.1.0 255.255.255.0 10.0.20.1
R3(config)#ip route 10.0.12.0 255.255.255.252 10.0.20.1
R4(config)#ip route 0.0.0.0 0.0.0.0 10.0.8.1
```

> R1 sits at the "hub" of this design (it touches both R2 and R3), so it needs specific routes to both remote LANs; R2 and R4 (the branch-facing routers) only need a default route pointing back at R1's local interface, since everything not on their own LAN is "somewhere past R1."

### 6.7 End Devices

Assign IPs per Section 4.3 via each PC/Server's Desktop → IP Configuration tab.

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| Any router | `show ip interface brief` | Every configured interface `up/up` |
| Any router | `show interfaces gigabitEthernet 0/1` | `Media type` line — confirms fiber vs. copper is correctly detected |
| Any switch | `show interfaces status` | All ports `connected`, correct duplex/speed |
| Any router | `show ip route` | Connected + static/default routes present |

### 7.1 Expected Output Gallery

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.12.1       YES manual up                    up
GigabitEthernet0/1         10.0.20.1       YES manual up                    up
```

**`R3# show interfaces gigabitEthernet 0/1`** (fiber link to R1)

```text
GigabitEthernet0/1 is up, line protocol is up
  Hardware is Gigabit Ethernet, address is 00E0.8F1A.2C01
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec
  Media type is fiber, 1000BaseSX/LX
  Full-duplex, 1000Mb/s, media type is SX/LX
```

`line protocol is up` on a fiber interface confirms both strands are correctly connected end to end — if only one strand is wired correctly, you'd see `up, line protocol is down`.

**`SW3# show interfaces status`**

```text
Port      Name               Status       Vlan       Duplex  Speed Type
Fa0/1     Link to PC1        connected    1          a-full  a-100 10/100BaseTX
Fa0/2                        notconnect   1          auto    auto  10/100BaseTX
```

**`PC1> ping 192.168.2.11`** (full inter-site path test)

```text
Pinging 192.168.2.11 with 32 bytes of data:

Reply from 192.168.2.11: bytes=32 time=2ms TTL=125
Reply from 192.168.2.11: bytes=32 time=1ms TTL=125
Reply from 192.168.2.11: bytes=32 time=1ms TTL=125
Reply from 192.168.2.11: bytes=32 time=1ms TTL=125

Ping statistics for 192.168.2.11:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Success here proves every cable choice, every interface, and every static route across both sites and both media types (copper + multi-mode + single-mode) is correct end to end.

### 7.2 Reachability Matrix

| From | To | Expected | Why |
|---|---|---|---|
| PC1 | PC2 | Success | Same LAN, switched locally |
| PC1 | R2 (gateway) | Success | Directly connected |
| PC1 | SRV1 | Success | Routed across the 3 km single-mode + 250 m multi-mode chain |
| PC3 | SRV1 | Success | Same LAN |
| R1 | R3 (fiber interface) | Success | Directly connected via SMF |

---

## 8. Common Mistakes (the 80/20)

1. **Using a crossover cable between a router and a switch, or straight-through between two switches.** This is the single most common Day 02 error — students memorize "copper = straight-through" without the unlike/like qualifier.
2. **Forgetting to swap the router's port type to a fiber module before attempting the R1–R3 or R3–R4 link.** Packet Tracer will simply refuse the connection if you try to run fiber into a copper GigabitEthernet port.
3. **Choosing multi-mode fiber for the 3 km link instead of single-mode** (or vice versa for the 250 m link) — always match distance to medium, not "fiber is fiber."
4. **Forgetting `no shutdown` on fiber interfaces**, then assuming the fiber module itself is broken when the real issue is the same one from Day 01.
5. **Not verifying `line protocol is up` specifically on fiber links** — fiber can be "administratively up" but still down at Layer 1 if the strands are swapped (TX on one end wired to TX, not RX, on the other).
6. **Skipping the static routes on R1** (the hub router) — R2 and R4 each only know their own LAN and a default route; without R1 having explicit routes to both remote LANs, cross-site ping fails even though every cable is correct.
7. **Assuming subnet size should scale with cable distance.** A 3 km fiber link between two router interfaces is still just a `/30` — physical medium and Layer 3 addressing are unrelated decisions.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Packet Tracer won't let you draw the cable at all | Wrong cable type selected for the two endpoint types | N/A (visual) | Re-check Section 6.1's like/unlike rule and reselect the correct cable |
| 2 | Interface shows `administratively down` | Forgot `no shutdown` | `show ip interface brief` | Enter interface, `no shutdown` |
| 3 | Fiber interface shows `up, line protocol down` | Strands reversed, or far-end interface still down | `show interfaces gi0/1` | Verify both ends have `no shutdown`; try reconnecting the fiber pair |
| 4 | PC reaches its own gateway but not the other site | Missing static/default route on R1 (the hub) | `show ip route` | Add the missing route from Section 6.6 |
| 5 | Switch port shows `notconnect` | Wrong cable type, or device on the other end is powered off/interface down | `show interfaces status` | Re-verify cable type and remote end status |
| 6 | Link "connects" visually in Packet Tracer but ping still fails | IP/mask mismatch between the two ends of a `/30` | `show run \| section interface` | Confirm both ends of each transit link are in the *same* /30 subnet |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why not run fiber everywhere, "to be safe"?** Fiber transceivers and modules cost meaningfully more per port than copper Ethernet, and offer zero practical benefit at 50 m — copper's 100 m limit isn't even close to being tested at that distance. Over-speccing every link with fiber is a real, recurring line-item waste that a network engineer is expected to catch.
- **Why multi-mode instead of single-mode for the 250 m link?** Single-mode transceivers (and the lasers they use) cost more than multi-mode ones. Multi-mode comfortably covers 250 m, so choosing single-mode here would be paying for range the link will never use.
- **Why does R1 act as the hub between the two sites instead of a direct SW-to-SW inter-site link?** Routers are required at Layer 3 boundaries between the two `/24` LANs — switches operate at Layer 2 and have no concept of routing between different IP subnets. The physical fiber link only makes cross-site traffic *possible*; it's R1's routing table that makes it *work*.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...facilities tells you a new building is going up 3 km from headquarters, and you're asked to spec the interconnect before construction finishes — this is precisely the R1–R3 decision.
- ...a vendor quote comes back with single-mode transceivers priced into a 30-meter closet run, and you have to push back because it's the wrong medium for the distance.
- ...a "the new switch won't link up" ticket turns out to be someone using a crossover cable on hardware without Auto-MDI-X.
- ...you're doing a site survey and need to justify, line by line, why the fiber budget is what it is to a non-technical finance stakeholder.

---

## 12. Stretch Goal

1. Add a third site (Site C) 900 m from Site B, and justify your medium choice with the same distance-based reasoning used in Section 6.2.
2. Convert the R1–R2 copper link to fiber and calculate whether the swap is ever justified purely on distance grounds (it isn't at 50 m) — write two sentences explaining why "more expensive medium" isn't automatically "better."
3. Deliberately reverse a fiber pair (if your platform allows simulating that) and observe the exact `show interfaces` output difference from a correctly wired link.

---

## 13. Self-Assessment

- [ ] Can you state the straight-through vs. crossover rule from memory, including the "like vs. unlike" reasoning?
- [ ] Can you explain why multi-mode and single-mode fiber exist as separate products rather than one fiber type covering all distances?
- [ ] Given a new distance requirement you've never seen before, could you correctly choose copper vs. multi-mode vs. single-mode?
- [ ] Can you explain why subnet size and cable distance are unrelated decisions?
- [ ] Can you name the router that needed the most static routes in this topology, and explain why?

---

## 14. Key Concepts Demonstrated

- Straight-through vs. crossover cabling and the like/unlike device rule
- Multi-mode vs. single-mode fiber selection based on distance
- Basic router interface addressing and static routing across mixed media
- Physical layer verification via `show interfaces` and `show interfaces status`

## What I Learned

This lab made clear that Layer 1 decisions are business decisions wearing a technical hat — the "right" cable is the cheapest one that reliably meets the distance requirement, not the most impressive-sounding one. It also reinforced that physical medium and Layer 3 addressing are independent axes: a link's cable type never changes how you size its subnet.

## Skills Practiced

- Cable type identification and selection
- Fiber optic medium selection by distance
- Router interface addressing across mixed-media links
- Physical and data-link layer verification

---

## 15. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1–R4) | Cisco 2911 | VyOS |
| Switches (SW1–SW8) | Cisco 2960 | Open vSwitch |
| PCs/Server | Generic PC/Server | Alpine Linux |

Note: GNS3's virtual links don't model fiber vs. copper distance/medium physically — the multi-mode/single-mode distinction in this lab is a *design exercise* that Packet Tracer enforces visually but GNS3 does not. Use the GNS3 build to practice addressing and routing; use Packet Tracer (or the manual reasoning in Section 6) for the cable-selection exercise itself.

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script.
