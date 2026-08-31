# Day 06 Lab Manual — Ethernet LAN Switching & MAC Address Tables

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a two-switch, four-PC LAN, generate traffic to observe dynamic MAC address learning, frame forwarding vs. flooding, ARP resolution, and manually clear/rebuild the MAC address tables to observe the "unknown destination" behavior directly. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): 2.1 (switching concepts — frame forwarding, MAC learning, frame flooding). ARP and MAC table behavior are near-guaranteed exam topics, often tested as "what does the switch do when it doesn't know the destination MAC?" |
| **Prerequisites** | Day 01–02 (device roles, cabling). No prior switching-specific experience required. |
| **Time Estimate** | 1 – 1.5 hours. |
| **Difficulty** | ⭐☆☆☆☆ (Beginner) — no hardening or routing, but the underlying mechanism (flood vs. forward) is one of the most-tested single concepts in the whole CCNA. |

---

## 1. Lab Overview

This lab builds the simplest possible topology that can demonstrate real switch learning behavior: two switches, four PCs, one flat `/24`. Everything interesting happens by *watching* — generating a single ping, capturing it in Simulation Mode, and inspecting each switch's MAC address table before and after traffic, then deliberately clearing it to watch the "empty table" behavior recur.

The mechanism under the microscope: a switch makes every forwarding decision by looking up the **destination MAC address** in a table it built by watching **source MAC addresses** go by. When it doesn't have an entry, it doesn't guess — it floods the frame out every port except the one it arrived on, and lets the correct destination self-identify by replying (at which point the switch learns *that* device's MAC too, from the reply's source address).

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain, step by step, how a switch builds its MAC address table from observed source MAC addresses
- Distinguish frame *forwarding* (known destination, sent out one port) from frame *flooding* (unknown destination, sent out all ports except the ingress port)
- Explain what ARP is for and why it must complete before the first ICMP packet of a new conversation can be sent
- Read and interpret `show mac address-table` output, including VLAN, MAC, type, and port columns
- Deliberately clear a switch's dynamic MAC table and predict/observe the resulting flood-then-relearn behavior
- Explain why switches forward based on MAC addresses, not IP addresses, and why this matters at Layer 2 vs. Layer 3

---

## 2. Business Context

**Why would a real company do this?**

Nobody sits around a production network deliberately clearing MAC tables for fun — but every network engineer eventually needs to understand *exactly* this mechanism to answer real operational questions:

- **"Why did we see a burst of traffic on every port right after that switch reboot?"** → a rebooted switch has an empty MAC table; every frame it receives for the first few seconds after boot gets flooded until the table repopulates. Understanding this prevents a panicked "are we being attacked" reaction to perfectly normal post-reboot flooding.
- **"A user moved their laptop to a different port and now things are slow for a second."** → the switch has to relearn that MAC address on the new port; until it does (or until the stale entry ages out), some frames may briefly flood or misforward. This is normal, expected, and short-lived — but only if you understand the mechanism do you *know* it's expected.
- **"Security wants to know: can a rogue device on our LAN see traffic that isn't addressed to it?"** → this is directly the flooding scenario. During any flood event (unknown destination, or genuinely malicious MAC table exhaustion attacks), traffic goes out ports it wouldn't normally reach — the basis for real Layer 2 security controls like port security, which builds directly on the MAC table concept this lab teaches.
- **"Why does the helpdesk keep telling users 'try again in a few seconds' after a network change?"** → MAC table aging and relearning is often the literal, correct answer.

This lab is small because the concept is small — but it's foundational to spanning tree, port security, VLANs, and Layer 2 troubleshooting, all of which assume you already understand exactly how a switch decides where a frame goes.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-06-Ethernet-LAN-Switching-1.png" alt="Day 06 Ethernet LAN Switching Topology" width="900">
</p>

```text
PC1 \            / PC3
     SW1 ---- SW2
PC2 /            \ PC4
```

| Device | Connects To |
|---|---|
| PC1, PC2 | SW1 |
| PC3, PC4 | SW2 |
| SW1 ↔ SW2 | Inter-switch link |

All four PCs and both switches sit on the same flat broadcast domain — no VLANs, no routing, single `/24`.

---

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

A single `/24` easily covers 4 PCs with generous room to grow, and there is no point-to-point transit link in this lab requiring a `/30` — every connection here is either PC-to-switch or switch-to-switch, all within the same broadcast domain.

### 4.2 Full Device Address Table

| Device | IP Address | Mask | Connects To |
|---|---|---|---|
| PC1 | 192.168.1.1 | 255.255.255.0 | SW1 |
| PC2 | 192.168.1.2 | 255.255.255.0 | SW1 |
| PC3 | 192.168.1.3 | 255.255.255.0 | SW2 |
| PC4 | 192.168.1.4 | 255.255.255.0 | SW2 |

No default gateway is required for local-LAN communication in this lab — every device is on the same subnet, so no routing decision is ever made; every conversation here stays entirely at Layer 2.

---

## 5. Pre-Configuration Checklist

1. Place SW1, SW2, PC1–PC4 and cable per Section 3 (straight-through PC-to-switch, crossover or auto-sensing switch-to-switch).
2. Assign static IPs to all 4 PCs per Section 4.2.
3. Do **not** generate any traffic yet — the whole point of Step 6.2 is observing what an empty MAC table looks like *before* anything happens.
4. Have Packet Tracer's Simulation Mode ready.

---

## 6. Configuration Tasks

No CLI configuration is strictly required on the switches for basic operation (default VLAN 1, all ports already forwarding) — this lab is entirely about *observation*, but a few verification-only commands anchor the process.

### 6.1 Confirm Empty MAC Tables (baseline)

```text
SW1>enable
SW1#show mac address-table
```

```text
SW2>enable
SW2#show mac address-table
```

> **Mode:** User EXEC → Privileged EXEC. At this point, before any traffic has been generated, both tables should show **no dynamic entries** (only, at most, a few static/system entries depending on platform). This is the deliberate starting condition — write down that both tables are empty before moving on, so Step 6.4's comparison actually means something.

### 6.2 Generate Traffic: PC1 Pings PC3

On PC1's command prompt (Desktop → Command Prompt):

```text
PC1> ping 192.168.1.3
```

> PC1 does not know PC3's MAC address yet (only its IP, `192.168.1.3`, from the ping command itself) — so before ICMP can be sent, PC1's own ARP process runs automatically: it broadcasts "who has 192.168.1.3, tell 192.168.1.1" to `FFFF.FFFF.FFFF`. Both switches, having empty MAC tables, **flood** this broadcast frame out every port except the one it arrived on — this is not a special "broadcast handling" behavior, it's the same flooding rule applied to a frame whose destination MAC (`FFFF.FFFF.FFFF`) will never appear as a *learned* single-port entry, since it's not a real device's address.

### 6.3 Step Through in Simulation Mode

Switch Packet Tracer to **Simulation Mode**, re-run the ping, and click through each PDU:

1. **ARP Request** — PC1 → broadcast. Watch it flood out of SW1's non-ingress ports, cross to SW2, and flood again there.
2. **ARP Reply** — PC3 → PC1, now a **unicast** frame (PC3 knows PC1's MAC from the request it just received). Watch SW2 and SW1 forward this out exactly one port each, since by now each switch has learned at least the sender's MAC from the frames it has already seen.
3. **ICMP Echo Request** — PC1 → PC3, unicast, forwarded directly.
4. **ICMP Echo Reply** — PC3 → PC1, unicast, forwarded directly.

### 6.4 Verify Learned MAC Addresses

```text
SW1#show mac address-table
```

```text
SW2#show mac address-table
```

> **Mode:** Privileged EXEC. Compare against Step 6.1's empty baseline — both switches should now show dynamic entries for at least PC1 and PC3 (the two devices that generated traffic), and likely the inter-switch link's learned addresses too, since ARP flooding crossed both switches.

### 6.5 Clear Dynamic Entries and Observe Reset Behavior

```text
SW1#clear mac address-table dynamic
SW2#clear mac address-table dynamic
```

> **Mode:** Privileged EXEC. This purges every *dynamically learned* entry (any statically configured entries, rare in this lab, would survive). Immediately re-run `show mac address-table` on both switches to confirm they're empty again — you've manually recreated the Step 6.1 starting condition without a reboot.

### 6.6 Re-Ping and Observe the Flood-Then-Relearn Cycle

```text
PC1> ping 192.168.1.3
```

> Even though PC1's own ARP cache may still hold PC3's MAC from the earlier exchange (ARP entries and switch MAC table entries are two *separate* things, learned and aged independently), the **switches'** MAC tables are now empty again, so the very first frame of this new ping — even a unicast ICMP frame, since the switches have no record of the destination port — gets **flooded**, not forwarded, until each switch relearns the relevant MACs from the traffic's source addresses.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show mac address-table` | VLAN, MAC address, Type (Dynamic/Static), Port columns; entries should match which PCs have recently sent traffic |
| `clear mac address-table dynamic` | Removes learned entries only |
| `show mac address-table dynamic` | Filters the table view to dynamic entries only, useful once static entries are added in later labs |

### 7.1 Expected Output Gallery

**`SW1# show mac address-table`** (baseline, before any traffic)

```text
          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
```

Empty — no dynamic entries yet.

**`SW1# show mac address-table`** (after PC1 pings PC3)

```text
          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    0060.2f7a.11e1    DYNAMIC     Fa0/1
   1    0060.2f9c.3b02    DYNAMIC     Fa0/24
```

`Fa0/1` is PC1's directly-connected port (learned from PC1's own frames); `Fa0/24` is the inter-switch uplink, where SW1 learned PC3's MAC because that's the port PC3's replies arrived through — SW1 doesn't know or care that PC3 is two hops away logically, it only knows "traffic from this MAC arrives on this port."

**`SW1# clear mac address-table dynamic`** then **`show mac address-table`**

```text
          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
```

Back to empty, confirming the manual clear worked exactly like the original boot-time baseline.

**Simulation Mode PDU inspection — ARP Request leaving PC1**

```text
[Layer 2 - Ethernet]
Src MAC: 0060.2F7A.11E1
Dst MAC: FFFF.FFFF.FFFF   (broadcast — flooded by both switches)

[ARP]
Opcode: REQUEST
Sender IP: 192.168.1.1
Sender MAC: 0060.2F7A.11E1
Target IP: 192.168.1.3
Target MAC: 0000.0000.0000  (unknown — this is what's being asked)
```

**`PC1> ping 192.168.1.3`** (successful result)

```text
Pinging 192.168.1.3 with 32 bytes of data:

Reply from 192.168.1.3: bytes=32 time=1ms TTL=128
Reply from 192.168.1.3: bytes=32 time<1ms TTL=128
Reply from 192.168.1.3: bytes=32 time<1ms TTL=128
Reply from 192.168.1.3: bytes=32 time<1ms TTL=128

Ping statistics for 192.168.1.3:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

### 7.2 Forward vs. Flood Decision Table

| Condition | Switch behavior |
|---|---|
| Destination MAC known in table, maps to a specific port | **Forward** — sent out that one port only |
| Destination MAC unknown (no table entry) | **Flood** — sent out every port except the ingress port |
| Destination MAC is broadcast (`FFFF.FFFF.FFFF`) | **Always flood** — broadcast addresses are never "learned" as a single-port entry |
| Destination MAC known, but maps to the *same* port the frame arrived on | Frame is dropped (source and destination are on the same segment; the switch doesn't echo a frame back out its own ingress port) |

---

## 8. Common Mistakes (the 80/20)

1. **Assuming the switch "asks" for the destination MAC.** It never asks anything — it only ever floods and passively learns from what comes back. The learning is entirely a side effect of watching source addresses.
2. **Confusing the PC's ARP cache with the switch's MAC address table.** They're two completely separate tables maintained by two completely separate devices for two different purposes (IP→MAC mapping vs. MAC→port mapping) — clearing one does not clear the other, exactly as demonstrated in Step 6.6.
3. **Expecting the second ping (after clearing MAC tables) to flood forever.** It only floods the *first* frame(s) until relearning completes — usually within the same ping sequence, so later ICMP replies in the same 4-packet ping often already show normal forwarding.
4. **Forgetting that flooding still excludes the ingress port.** A flooded frame goes out every port *except* the one it arrived on — never back out the same port, which would be pointless and could create loops.
5. **Not distinguishing forwarding decisions from filtering decisions.** A switch doesn't "block" unknown traffic — it floods it. Filtering (deliberately dropping) is a different, later concept (ACLs, port security violations).

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Ping fails entirely, not just delayed | IP misconfiguration on a PC, or a cabling/port issue | `ipconfig` (PC), `show interfaces status` (switch) | Verify IP/mask and that the port shows `connected` |
| 2 | MAC table stays empty even after a successful ping | Checked too soon, or captured the wrong switch's table | `show mac address-table` immediately after traffic, on both switches | Re-check both switches, not just one |
| 3 | Unexpected extra entries appear in the MAC table | Background broadcast/multicast traffic (e.g., ARP from unrelated activity) also crossed the switch | `show mac address-table` | Expected in a busy simulated network — not an error |
| 4 | `clear mac address-table dynamic` appears to do nothing | Command run on the wrong switch, or checked before the clear actually completed | Re-run `show mac address-table` immediately after | Confirm you're on the correct device (`SW1#` vs `SW2#` prompt) |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why does the switch flood instead of dropping unknown-destination frames?** Dropping would mean any new device could never receive its very first frame — there'd be no way to ever "discover" it. Flooding trades a small amount of unnecessary bandwidth (frames going to ports that don't need them) for guaranteed reachability the first time, self-correcting the moment the switch observes a reply.
- **Why does a switch forward based on MAC address instead of IP address?** MAC addresses are a Layer 2 concept, and switches — by definition — operate at Layer 2. IP addressing and routing decisions belong to Layer 3 devices (routers). This separation of concerns is why a switch can forward traffic for *any* Layer 3 protocol (IPv4, IPv6, or anything else riding on Ethernet) without needing to understand any of them.
- **Why is the MAC table dynamic (aging out, clearable) rather than permanent?** Devices move, get replaced, or go offline. A permanent table would eventually be full of stale entries pointing traffic at ports where the device no longer exists. Dynamic aging (and the manual clear demonstrated here) keeps the table representative of the network's *current* state.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a switch reboots after a firmware upgrade and network monitoring briefly shows a spike in traffic on every port — this is completely normal MAC-table-repopulation flooding, not an incident.
- ...you're diagnosing "traffic seems to reach devices it shouldn't" and the root cause is a temporary flood window, which becomes the entry point into learning about port security and DHCP snooping later in the CCNA track.
- ...a user reports "my connection dropped for a second when I moved desks" — often just the switch relearning their MAC on a new port after unplugging from one and plugging into another.
- ...you're asked in an interview "what does a switch do when it receives a frame for a MAC it's never seen" — this exact lab's Section 6.6 behavior, described from memory, is a very common CCNA/junior-network-engineer interview question.

---

## 12. Stretch Goal

1. Add a third switch (SW3) between SW1 and SW2, forcing a 3-hop path between PC1 and PC3, and trace how many switches flood the initial ARP request vs. how many ultimately learn PC1's and PC3's MAC addresses.
2. Research and explain, in 2–3 sentences, how `show mac address-table` entries eventually **age out** on their own even without a manual clear — what's the default aging timer, and why does it exist?
3. Predict, then test: if PC2 (not PC1) pings PC3 right after Step 6.4 (without clearing anything), does SW1 already have enough information to avoid flooding? Explain your prediction before testing.

---

## 13. Self-Assessment

- [ ] Can you explain, from memory, exactly how a switch builds its MAC address table (what triggers a new entry)?
- [ ] Can you state the difference between forwarding and flooding, and the exact condition that triggers each?
- [ ] Can you explain why a broadcast destination MAC is always flooded, never "learned" as a single-port entry?
- [ ] Can you explain the difference between a PC's ARP cache and a switch's MAC address table — two entirely separate tables on two entirely separate devices?
- [ ] Could you predict, for a fresh scenario you haven't tested, whether a given frame would be forwarded or flooded?

---

## 14. Key Concepts Demonstrated

- Dynamic MAC address learning from source addresses
- Frame forwarding (known destination) vs. flooding (unknown destination, and always for broadcast)
- ARP request/reply mechanics and its dependency relationship with the first ICMP packet of a new conversation
- `show mac address-table` / `clear mac address-table dynamic` verification commands

## What I Learned

Stepping through the ARP-then-ICMP sequence in Simulation Mode made concrete something that's easy to state abstractly but hard to really internalize: a switch has no idea where any device is until it happens to see traffic *from* that device. Everything downstream — forwarding, flooding, the brief "flood again" behavior after clearing the table — falls directly out of that one fact. This lab also reinforced that a PC's ARP cache and a switch's MAC table are two independent systems that happen to interact but don't share state, which explains a specific, common source of confusion when the two get mixed up.

## Skills Practiced

- MAC address table interpretation
- Frame forwarding vs. flooding analysis
- ARP mechanics
- Packet Tracer Simulation Mode traffic tracing
- Basic Layer 2 verification and reset commands

---

## 15. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| SW1, SW2 | Cisco 2960 | Open vSwitch |
| PC1-PC4 | Generic PC | Alpine Linux |

Note: Open vSwitch's MAC learning is functionally equivalent to a Cisco switch's, but its inspection commands differ (`ovs-appctl fdb/show <bridge>` instead of `show mac address-table`). Use `tcpdump`/Wireshark on a link to observe the ARP-flood-then-unicast pattern from Section 6.3 directly on the wire.

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script.
