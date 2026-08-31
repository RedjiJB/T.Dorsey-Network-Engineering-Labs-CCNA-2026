# Day 22 Lab Manual — RSTP: Root Bridge Behavior and Link Types

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Analyze Rapid Spanning Tree Protocol (RSTP) port roles across a 4-switch, 2-hub topology; explain why the root bridge itself can have a non-Designated port; correctly classify and configure RSTP link types (point-to-point, shared, edge). |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): configure and verify spanning tree protocols (RSTP, PVST+), compare and contrast redundancy protocols, describe the interface and cable types. |
| **Prerequisites** | Basic switching concepts (MAC learning, broadcast domains), Day 01–Day 11 device configuration fluency. No prior STP-specific lab required — this is the introductory RSTP lab. |
| **Time Estimate** | 1.5 – 2 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the topology is small, but reasoning about port roles on shared (hub) segments trips up most first-time RSTP students, including the very idea that a root bridge can have a blocking port. |

---

## 1. Lab Overview

Most CCNA students learn STP with a clean assumption: the root bridge has every port in the Designated/Forwarding role, full stop. This lab deliberately breaks that assumption by inserting two **hubs** into an otherwise normal 4-switch topology. Hubs create shared, multi-access Layer 1 segments — and RSTP has specific, correct behavior for that scenario that looks wrong until you understand *why* it's happening.

You'll examine port roles across all four switches, predict roles you haven't yet verified, and then correctly classify and configure each interface's RSTP **link type** — the single most commonly misconfigured RSTP setting in real switched networks.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Identify the root bridge using bridge ID (priority + MAC)
- Explain why a hub-connected segment can place a port into the Backup role, even on the root bridge
- Distinguish RSTP port roles: Root, Designated, Alternate, Backup
- Predict port roles on a topology before verifying with the CLI
- Correctly classify and configure RSTP link types: point-to-point (P2p), shared (Shr), and edge
- Explain why `spanning-tree portfast` is the correct fix for a misclassified PC-facing port

---

## 2. Business Context

**Why would a real company do this?**

Almost no modern enterprise network runs hubs on purpose anymore — but this lab isn't really about hubs. It's about a lesson that generalizes to any shared-medium scenario an engineer will eventually encounter: wireless bridges acting as a shared segment, old legacy equipment still in a closet somewhere, or a misconfigured switchport accidentally running half-duplex.

- **"Why is this one port on our core switch blocking, when the core switch is supposed to be the root?"** → this is a real ticket pattern. An engineer who only knows "the root bridge has all Designated ports" will misdiagnose this as a fault. An engineer who understands shared-segment Backup ports recognizes it as correct, expected behavior.
- **"Our helpdesk says a user's PC takes 30+ seconds to get network access after plugging in"** → almost always a missing `spanning-tree portfast` on an edge port that RSTP is (correctly, by its own rules) treating as a non-edge link, running full listening/learning delay before forwarding.
- **"We need switches to converge fast when a link fails"** → RSTP's entire value proposition over classic STP is sub-second convergence, but *only* if link types are classified correctly. A shared-classified point-to-point link doesn't get RSTP's fast transition — it falls back to timer-based convergence, silently undoing the reason you're running RSTP in the first place.

Getting link-type classification right isn't cosmetic — it's the difference between RSTP actually delivering fast convergence and RSTP quietly behaving like slow classic STP everywhere it thinks it might be on a shared segment.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-22-Lab-Rapid-STP.png" width="900">
</p>

### 3.1 Switch Inventory

| Device | Model | Priority | MAC Address | Role |
|---|---|---|---|---|
| SW1 | 2960-24TT | 32769 | 0005.5E4E.714B | Root Bridge |
| SW2 | 2960-24TT | 32769 | 00D0.5882.4834 | Non-root |
| SW3 | 2960-24TT | 32769 | 000C.8519.6EBA | Non-root |
| SW4 | 2960-24TT | 32769 | 00E0.A381.AD46 | Non-root |
| Hub0 | Hub-PT | N/A | N/A | Shared medium |
| Hub1 | Hub-PT | N/A | N/A | Shared medium |

All four switches share the same priority (32769 — the Cisco default of 32768 plus a system extended-ID offset), so **SW1 wins the root bridge election purely on lowest MAC address** — this is worth internalizing, because priority ties resolved by MAC are a recurring CCNA exam pattern.

### 3.2 Traffic Flow Summary

```text
SW1 (Root) -- Fa0/1 (P2p) -- SW2
SW1 (Root) -- Fa0/2 (Shr, via Hub0) -- SW3
SW1 (Root) -- Fa0/3 (Shr, via Hub0) -- SW4  [Backup port lands here]
SW1 (Root) -- Fa0/24 (PC-facing, misclassified as Shr) -- PC-Root

SW2 -- Fa0/2 (via Hub1) -- SW3, SW4 (redundant path)
SW3 -- access port -- PC3
SW4 -- access port -- PC6
```

---

## 4. IP Addressing Plan

This lab operates entirely at Layer 2 — no IP addressing plan is required. All switches communicate via BPDUs on their default VLAN, and end devices (if present) only need enough IP configuration to be reachable for ping-based convergence testing, which is out of scope for the RSTP analysis itself.

---

## 5. Pre-Configuration Checklist

1. Place 4 switches and 2 hubs matching the topology image.
2. Cable exactly as shown — the *specific* pattern of which switch connects through which hub is what creates the Backup-port scenario; a different cabling pattern will produce different (but analyzable) results.
3. Leave RSTP link types at their **default (auto-detected)** state initially — you want to observe the misclassification before fixing it.
4. Ensure all switches are running RSTP, not classic STP: `spanning-tree mode rapid-pvst` (global config, all switches).

---

## 6. Configuration Tasks

### 6.1 Step 1 — Confirm RSTP mode and identify the root bridge

```text
SW1(config)#spanning-tree mode rapid-pvst
```

> **Mode:** Global Config. Cisco switches default to PVST+ (classic STP behavior per-VLAN) unless explicitly set to `rapid-pvst`. Repeat on all four switches — RSTP requires every switch in the topology to speak the same STP variant to interoperate correctly.

```text
SW1#show spanning-tree
```

Look for `This bridge is the root` in the output — confirms SW1's role.

### 6.2 Step 2 — Examine port roles on the root bridge itself

```text
SW1#show spanning-tree interface fastEthernet 0/1
SW1#show spanning-tree interface fastEthernet 0/2
SW1#show spanning-tree interface fastEthernet 0/3
SW1#show spanning-tree interface fastEthernet 0/24
```

**What you'll find:**

| Interface | Role | Status | Link Type |
|---|---|---|---|
| Fa0/1 | Designated | FWD | P2p |
| Fa0/2 | Designated | FWD | Shr |
| Fa0/3 | **Backup** | **BLK** | Shr |
| Fa0/24 | Designated | FWD | Shr (misclassified — see Step 4) |

> **Why Fa0/3 is Backup, not Designated:** Hub0 connects SW1's Fa0/2 and Fa0/3 to the *same* shared collision domain as SW3 and SW4. Because it's a hub (Layer 1 repeater, not a switch), SW1 hears its **own BPDUs echoed back** through the shared segment on Fa0/3. RSTP recognizes this as "I am already the Designated bridge for this segment via another of my own ports," and places the redundant port into **Backup** role, blocking it — preventing SW1 from forwarding duplicate frames onto a segment it's already forwarding onto via Fa0/2. This is unique to shared-medium topologies: on a fully switched (point-to-point only) network, a Backup port cannot occur, because two of a single switch's ports are never on the same collision domain.

### 6.3 Step 3 — Predict, then verify, port roles on SW2, SW3, SW4

Before running any command, work out on paper: for each remaining switch, which port has the best (lowest-cost) path back to the root — that becomes the **Root port**. Any port facing an end device becomes **Designated**. Any redundant path to the root that isn't the best one becomes **Alternate**.

```text
SW2#show spanning-tree
SW3#show spanning-tree
SW4#show spanning-tree
```

**Confirmed results:**

- **SW3:** Fa0/2 = Root/FWD (best path to SW1); access port to PC3 = Designated/FWD
- **SW4:** Fa0/1 = Root/FWD (best path); Fa0/2 = Alternate/BLK (redundant path via Hub1); access port to PC6 = Designated/FWD
- **SW2:** mixed Designated/Root roles depending on which side of each link is closer to the root

### 6.4 Step 4 — Correct the misclassified edge port

`show spanning-tree interface fastEthernet 0/24` on SW1 shows **Shr** even though Fa0/24 connects directly to a PC, not a hub or another switch. This is wrong: a single end device on a modern full-duplex switchport is a point-to-point link to an edge device, not a shared segment.

```text
SW1(config)#interface fastEthernet 0/24
SW1(config-if)#switchport mode access
SW1(config-if)#spanning-tree portfast
SW1(config-if)#exit
```

> **Mode:** Interface Config. `spanning-tree portfast` does two things at once: it implicitly marks the port as an RSTP **edge** port (skipping the Listening/Learning delay entirely — forwarding starts immediately), and it signals RSTP that this port will never see a BPDU from another switch. **Never** apply `portfast` to a port facing another switch or a hub with multiple devices behind it — doing so risks a forwarding loop going undetected, since portfast ports skip loop-prevention delay.

**Alternative (explicit link-type override, without portfast):**

```text
SW1(config)#interface fastEthernet 0/24
SW1(config-if)#spanning-tree link-type point-to-point
```

> This tells RSTP to treat the port as P2p for fast-transition purposes, without also marking it as an edge port. `portfast` is the more common real-world choice for pure end-device ports because it does both jobs (edge + fast link type) in one command, plus enables immediate forwarding.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show spanning-tree` | Root bridge identity, per-VLAN port roles/states |
| `show spanning-tree interface <type> <number>` | Single-port role, state, and link type in detail |
| `show running-config interface <type> <number>` | Confirms `portfast`/`link-type` commands applied |

### 7.1 Expected Output Gallery

**`SW1# show spanning-tree`**

```text
VLAN0001
  Spanning tree enabled protocol rstp
  Root ID    Priority    32769
             Address     0005.5E4E.714B
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Interface           Role Sts Cost      Prio.Nbr Type
-------------------- ---- --- --------- -------- --------------------------------
Fa0/1                Desg FWD 19        128.1    P2p
Fa0/2                Desg FWD 19        128.2    Shr
Fa0/3                Back BLK 19        128.3    Shr
Fa0/24               Desg FWD 19        128.24   P2p Edge
```

Notice Fa0/24's Type column now reads `P2p Edge` — confirming the fix from Step 4 took effect.

**`SW4# show spanning-tree interface fastEthernet 0/2`**

```text
Fa0/2 (VLAN0001) - Blocking

Role: Alternate
Port Identifier: 128.2
Designated root has priority 32769, address 0005.5E4E.714B
Designated port id is 128.2, designated path cost 38
Timers: message age 2, forward delay 0, hold 0
Number of transitions to forwarding state: 0
Link type: shared
```

Confirms SW4's prediction from Step 3: Fa0/2 is Alternate/Blocking, the redundant path through Hub1.

---

## 8. Common Mistakes (the 80/20)

1. **Assuming the root bridge always has 100% Designated ports.** This lab exists specifically to break that assumption — a Backup port on the root is correct behavior on a shared segment, not a misconfiguration.
2. **Applying `portfast` to a port that isn't actually an edge port** (e.g., a port connected to a hub with multiple hosts, or to another switch). This can allow a forwarding loop, since portfast ports skip the delay that would otherwise catch a loop before it causes duplicate frames.
3. **Confusing Backup and Alternate roles.** Both block. Alternate = a redundant path to the *root* through a different switch. Backup = redundant reachability to the *same segment* through the *same switch's* own other port (only possible on shared media).
4. **Forgetting to set `spanning-tree mode rapid-pvst` on every switch.** If even one switch stays on classic PVST+, RSTP's fast-transition benefits degrade at that switch's boundary.
5. **Not checking `Type` (link-type) at all**, only checking `Role`/`Sts`. A port can have the "right" role but still be running slow (shared-segment) convergence timers because its link type was auto-detected wrong.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Unexpected switch is root bridge | Lower MAC or lower priority elsewhere | `show spanning-tree` (check Bridge ID) | Lower priority on the intended root with `spanning-tree vlan 1 priority <value>` |
| 2 | A port on the root bridge is blocking | Shared-medium (hub) segment causing a Backup port | `show spanning-tree interface <if>` | Expected behavior on shared segments — verify it's Backup, not a fault |
| 3 | PC takes 30+ seconds to get network access after plugging in | Port not classified as Edge, running full Listening/Learning delay | `show spanning-tree interface <if>` (check Type) | Apply `spanning-tree portfast` on that access port |
| 4 | RSTP not converging quickly after a link failure | Link-type misclassified as shared instead of point-to-point | `show spanning-tree interface <if>` | `spanning-tree link-type point-to-point` (only if genuinely full-duplex, switch-to-switch) |
| 5 | Two switches report different STP modes / instability | One switch left on PVST+, others on rapid-pvst | `show spanning-tree summary` on each switch | Set `spanning-tree mode rapid-pvst` consistently everywhere |

---

## 10. Design Analysis

Why does this lab intentionally use hubs when no modern network would? Because hubs are the cleanest possible way to force a shared-medium scenario without needing exotic wireless-bridge or half-duplex-mismatch setups that are harder to reproduce in a simulator. The lesson transfers directly: any time two of a switch's own ports can hear each other's traffic on the same collision domain — which happens with old hubs, but can also happen with certain wireless bridge configurations or misconfigured half-duplex links — RSTP's Backup-port logic applies identically.

The choice to have a PC-facing port default to `Shr` instead of `P2p Edge` is also deliberate: it's exactly what happens in the real world when a port's duplex/speed negotiation goes wrong (stuck at half-duplex) or when `portfast` was simply never configured. This lab teaches you to *notice* that state and fix it, rather than trusting RSTP's auto-detection blindly.

---

## 11. Real-World Parallel

You'd see the Backup-port scenario in any legacy environment where an old hub or unmanaged switch (functioning as a de facto hub if oversubscribed or looped) still exists in a closet, feeding two ports on the same upstream switch. You'd see the missing-portfast scenario constantly — it's one of the most common "why does it take so long for my computer to get on the network after I plug it in" tickets a helpdesk escalates to network engineering, and the fix is almost always this lab's Step 4.

---

## 12. Stretch Goal

1. Change SW1's priority to a non-default, explicit value (e.g., `4096`) and confirm the root election still resolves the same way — then lower SW3's priority below SW1's and observe the root bridge election change.
2. Remove Hub0 entirely and replace it with a direct switch-to-switch link; re-run the same `show spanning-tree` commands and confirm the Backup port disappears — explain why in one sentence.
3. Deliberately misconfigure `portfast` on a switch-to-switch link, then create a physical loop and observe (carefully, and only in simulation) what happens differently versus a correctly classified link.

---

## 13. Self-Assessment

- [ ] Can you explain, without notes, why a root bridge can have a non-Designated port?
- [ ] Can you distinguish Alternate from Backup port roles in one sentence each?
- [ ] Can you identify, from a `show spanning-tree interface` output, whether a link type is correctly classified?
- [ ] Do you know the two things `spanning-tree portfast` does simultaneously?
- [ ] Could you predict port roles on an unfamiliar 4-switch topology with a shared segment, before running any `show` command?

---

## 14. Key Concepts Demonstrated

- RSTP port roles: Root, Designated, Alternate, Backup
- Root bridge election via bridge ID (priority + MAC)
- Shared-medium (hub) impact on RSTP topology
- RSTP link types: point-to-point, shared, edge
- PortFast as implicit edge-port signaling

---

## 15. What I Learned

The single biggest correction to my mental model from this lab: the root bridge is not automatically "all clean, all forwarding." RSTP's Backup-port behavior on shared segments is a deliberate, correct safeguard against a switch forwarding duplicate frames onto a collision domain it's already reachable through. The second correction was realizing that "link type" is a separate axis from "port role" — a port can have the right role (Designated) while still running on the wrong link-type assumption (Shared instead of Point-to-Point), quietly costing you RSTP's fast-convergence benefit without any obvious symptom until a failure actually happens.

---

## 16. Skills Practiced

- RSTP mode configuration (`rapid-pvst`)
- Root bridge identification and bridge-ID analysis
- Port role prediction and CLI verification
- RSTP link-type classification and correction
- PortFast configuration on edge ports

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology built by [`GNS3/build_lab.py`](GNS3/build_lab.py). **Important limitation:** GNS3's built-in Open vSwitch nodes have limited/no native STP support (OVS is typically deployed with STP disabled by default in cloud/virtualization contexts). This means the root-bridge Backup-port behavior from Section 6.2 **cannot be fully reproduced** using Open vSwitch alone.

| Role | Packet Tracer device | GNS3 image | Note |
|---|---|---|---|
| Switches (SW1–SW4) | Cisco 2960 | Open vSwitch | Limited STP support — see below |
| Hubs (Hub0, Hub1) | Hub-PT | (simulated via an unmanaged OVS bridge with STP disabled) | No true "hub" GNS3 image exists |
| PCs | Generic PC | Alpine Linux | |

See [`GNS3/README.md`](GNS3/README.md) for a discussion of this limitation and an alternative: using Cisco IOU/IOL switch images (if you have access to them through a personal Cisco license) instead of Open vSwitch, which *does* support full RSTP behavior identical to the Packet Tracer/real-IOS lab above.
