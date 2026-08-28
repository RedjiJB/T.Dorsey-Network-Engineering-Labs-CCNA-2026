# Day 20 Lab Manual — Analyzing STP: Port Roles Across Four Switches

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Analyze an existing (unconfigured-by-you) four-switch redundant topology to identify the root bridge and correctly classify every port's STP role, then verify each prediction against live CLI output. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): Spanning Tree Protocol fundamentals, root bridge election, port roles and states. This is one of the most heavily tested topics on the real exam. |
| **Prerequisites** | Day 17–19 (trunking, multi-switch topologies). No prior STP configuration experience required — this lab teaches STP theory through analysis before Day 21 teaches configuration. |
| **Time Estimate** | 1.5 – 2 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — no configuration required, but correctly reasoning through port roles from priorities and path costs is a genuine skill, not memorization. |

---

## 1. Lab Overview

This lab is deliberately different from every prior lab: **you don't configure anything.** A four-switch topology with redundant links already has STP running with default settings. Your job is to *read* the topology, determine the root bridge from bridge priorities, predict every port's role and state, and then verify your predictions against `show spanning-tree detail`. This "analyze first, verify second" structure mirrors how STP troubleshooting actually works in the field — you rarely configure STP from scratch; you far more often have to read an existing topology's STP state to understand why a link is blocking or why traffic is taking an unexpected path.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Determine a topology's root bridge by comparing Bridge IDs (priority + MAC)
- Explain why every port on the root bridge is always Designated/Forwarding
- Classify every non-root switch's ports as Root, Designated, or Alternate/Non-Designated
- Explain how path cost (not just priority) determines root port selection on non-root switches
- Interpret `show spanning-tree detail` output and map it back to the physical topology

---

## 2. Business Context

**Why would a real company do this?**

Redundant links between switches exist specifically so a single cable or switch failure doesn't take down the network — but redundant Layer 2 links, left unmanaged, create loops that broadcast storms exploit catastrophically within seconds. STP is what makes redundancy safe: it mathematically determines exactly one loop-free active path between any two points, while keeping the redundant links in reserve (blocking, not disconnected) ready to take over instantly if the primary path fails. Every real enterprise campus has multiple links between distribution switches for exactly this reason, and every network engineer needs to be able to look at a live topology and answer "why is this specific port blocking, and what would happen if that link there failed?" without touching a single configuration command — which is exactly the skill this lab isolates and practices before Day 21 teaches you to actively *influence* those outcomes.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2020%20Lab%20-%20Analyzing%20STP.png" alt="Day 20 Topology" width="800">
</p>

> **Lab-specific instruction:** turn off Packet Tracer's link lights for this lab (Options → Preferences → uncheck "Show Link Lights") — the goal is to reason from configuration data, not from the simulator's visual forwarding/blocking indicators.

```text
        SW3 (root bridge)
       /   |   \    \
     F0/1 F0/2 F0/3  G0/1
     /      |      \      \
   SW1    SW2      SW4    (redundant paths interconnect SW1/SW2/SW4 too)
```

| Switch | Priority | MAC Address |
|---|---|---|
| SW1 | 32769 | 0001.4338.79D8 |
| SW2 | 28673 | 0002.16D6.D0B8 |
| SW3 | 24577 | 00E0.F9E6.44A5 |
| SW4 | 32769 | 0090.0C01.9587 |

---

## 4. Root Bridge Election Theory (No Addressing in This Lab)

This lab has no IP addressing component — it's pure Layer 2 STP analysis. In its place, Section 4 covers the equivalent "derive it by hand" skill for this lab's topic: **root bridge election math**.

### 4.1 Bridge ID Composition

```text
Bridge ID = Bridge Priority (16 bits) + MAC Address (48 bits)
```

The switch with the **numerically lowest** Bridge ID becomes the root bridge. Priority is compared first (it dominates the comparison since it's the higher-order field); MAC address is only used as a tiebreaker when two switches share the same priority.

### 4.2 Manual Comparison Walkthrough

| Switch | Priority | Comparison |
|---|---|---|
| SW1 | 32769 | Higher than SW3 → not root |
| SW2 | 28673 | Higher than SW3 → not root |
| SW3 | **24577** | **Lowest priority in the topology → root bridge** |
| SW4 | 32769 | Higher than SW3 → not root (tied with SW1 on priority, but irrelevant — neither is lowest) |

**Rule:** compare priorities first, numerically, across all switches. The lowest wins regardless of MAC address, unless there's an exact priority tie — in that case (not present in this lab, since SW1 and SW4 tie at 32769 but neither is the *lowest* overall) the lowest MAC address would be the tiebreaker.

**Immediate consequence of SW3 winning:** *every single port on SW3* becomes a **Designated Port in the Forwarding state** — this is not something you calculate per-port on the root bridge; it's a direct, mechanical consequence of being the root. The root bridge is, by definition, the designated switch for every LAN segment it touches.

### 4.3 Path Cost Reference (Memorize This Table)

| Interface Speed | Default STP Path Cost |
|---|---|
| 10 Mbps (Ethernet) | 100 |
| 100 Mbps (FastEthernet) | 19 |
| 1 Gbps (GigabitEthernet) | 4 |
| 10 Gbps | 2 |

**Memory aid:** cost goes down as speed goes up — STP always prefers the fastest available path to root, all else equal. This is why, on any non-root switch with both a FastEthernet and a GigabitEthernet path toward the root, the GigabitEthernet path wins the root port election every time (barring an administrator overriding it, which Day 21 covers).

---

## 5. Pre-Analysis Checklist

1. Confirm link lights are disabled in Packet Tracer (see Section 3 note).
2. Have the Bridge ID table (Section 3) and path cost table (Section 4.3) open.
3. Resist the urge to run `show spanning-tree detail` before making your own prediction for each port — the entire value of this lab is in reasoning first, verifying second.

---

## 6. "Configuration" Tasks (Analysis Steps, No CLI Changes)

### 6.1 Step 1 — Identify the Root Bridge

Compare all four switches' priorities (Section 4.2). **SW3 (priority 24577) is the root.** Every SW3 port is Designated/Forwarding — no further analysis needed for SW3 itself.

### 6.2 Step 2 — For Each Non-Root Switch, Find the Root Port

The **root port** is the one port on a non-root switch with the lowest total path cost back to the root bridge. Every non-root switch has **exactly one** root port — never zero, never more than one (in a converged, healthy topology).

| Switch | Candidate Ports Toward Root | Path Cost | Root Port |
|---|---|---|---|
| SW1 | F0/4 (FastEthernet, direct to SW3) | 19 | **F0/4** |
| SW2 | G0/1 (GigabitEthernet, direct to SW3) | 4 | **G0/1** (beats any FastEthernet alternative) |
| SW4 | G0/2 (GigabitEthernet, direct to SW3) | 4 | **G0/2** |

**Reasoning demonstrated:** SW2 has other ports (F0/1, F0/2, F0/3) that could theoretically reach the root through a different switch, but none of those paths beat a direct Gigabit link's cost of 4 — so G0/1 wins outright.

### 6.3 Step 3 — For Each Remaining Port, Determine Designated vs. Alternate

For every LAN segment (link) in the topology, **exactly one** port is Designated (forwarding) — the port, among the (typically two) ports on that segment, with the lower cost-to-root. The other port on that same segment becomes **Alternate / Non-Designated (blocking)**.

**SW1's remaining ports (F0/1, F0/2, F0/3):** each connects to a segment where the comparison against the far-end switch's cost-to-root loses — SW1's own cost-to-root (19, via F0/4) is higher than the alternative paths already available through SW2/SW4 on those same segments, so **all three become Alternate/blocking.**

**SW2's remaining ports (F0/1, F0/2):** SW2's cost-to-root (4, the lowest in the topology besides the root itself) wins the comparison on those segments, so **both become Designated/forwarding** — SW2 is the best path to root for whatever's on the far end of those links. **F0/3 becomes Alternate/blocking** — a redundant path to the root that isn't needed.

**SW4's remaining port (G0/1):** SW4's cost-to-root (4) wins its segment comparison, so **G0/1 becomes Designated/forwarding.**

### 6.4 Full Port Role Table (Your Predictions — Verify in Section 7)

| Switch | Port | Role | State | Path Cost |
|---|---|---|---|---|
| SW3 | F0/1 | Designated | Forwarding | 19 |
| SW3 | F0/2 | Designated | Forwarding | 19 |
| SW3 | F0/3 | Designated | Forwarding | 19 |
| SW3 | G0/1 | Designated | Forwarding | 4 |
| SW1 | F0/4 | Root | Forwarding | 19 |
| SW1 | F0/1 | Alternate | Blocking | 19 |
| SW1 | F0/2 | Alternate | Blocking | 19 |
| SW1 | F0/3 | Alternate | Blocking | 19 |
| SW2 | G0/1 | Root | Forwarding | 4 |
| SW2 | F0/1 | Designated | Forwarding | 19 |
| SW2 | F0/2 | Designated | Forwarding | 19 |
| SW2 | F0/3 | Alternate | Blocking | 19 |
| SW4 | G0/2 | Root | Forwarding | 4 |
| SW4 | G0/1 | Designated | Forwarding | 4 |

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| Any switch | `show spanning-tree detail` | Bridge ID, root ID, every port's role/state/cost |
| Any switch | `show spanning-tree interface <id>` | Single-port focused role/state check |
| Root bridge (SW3) | `show spanning-tree detail` | Confirms "This bridge is the root" and all-Designated ports |

### 7.1 Expected Output Gallery

**`SW3# show spanning-tree detail`** (root bridge)

```text
VLAN0001 is executing the ieee compatible Spanning Tree protocol
  Bridge Identifier has priority 24577, address 00E0.F9E6.44A5
  This bridge is the root
  Port 1 (FastEthernet0/1) of VLAN0001 is designated forwarding
  Port 2 (FastEthernet0/2) of VLAN0001 is designated forwarding
  Port 3 (FastEthernet0/3) of VLAN0001 is designated forwarding
  Port 25 (GigabitEthernet0/1) of VLAN0001 is designated forwarding
```

**`SW1# show spanning-tree detail`** (non-root, mixed root/alternate)

```text
VLAN0001 is executing the ieee compatible Spanning Tree protocol
  Bridge Identifier has priority 32769, address 0001.4338.79D8
  Root Identifier has priority 24577, address 00E0.F9E6.44A5
  Port 4 (FastEthernet0/4) of VLAN0001 is root forwarding
  Port 1 (FastEthernet0/1) of VLAN0001 is alternate blocking
  Port 2 (FastEthernet0/2) of VLAN0001 is alternate blocking
  Port 3 (FastEthernet0/3) of VLAN0001 is alternate blocking
```

The **Root Identifier** field (SW3's priority/MAC) appearing on a non-root switch is exactly how you confirm, from any switch in the topology, which one is the root without needing to check SW3 directly — every switch in a converged topology knows and reports the root's identity.

---

## 8. Common Mistakes (the 80/20)

1. **Assuming the switch with the lowest MAC address is always root**, forgetting priority is compared first and dominates unless there's an exact priority tie.
2. **Forgetting that the root bridge's ports are automatically all Designated** — students sometimes try to run the "compare cost-to-root on each segment" logic on the root bridge itself, when the answer is immediate and requires no calculation.
3. **Assuming a lower path cost number means a *worse* path.** It's the opposite — STP path cost is literally a cost, and lower cost paths are preferred, the same as shortest-path routing metrics elsewhere in networking.
4. **Confusing "Alternate" (a port that could become the root port if the current one fails) with "the port is broken."** Alternate/blocking ports are healthy, intentional, and instantly ready to take over — that's the entire point of STP redundancy.
5. **Not recognizing that path cost, not just priority, decides root port selection on non-root switches.** Priority only decides *which switch* is root; path cost decides which *port on a non-root switch* becomes that switch's own root port.

---

## 9. Troubleshooting Guide

Since this lab makes no configuration changes, "troubleshooting" here means **verifying your analysis against reality**, not fixing a broken config:

| Step | Symptom (Discrepancy) | Likely Cause | Diagnostic Command | Resolution |
|---|---|---|---|---|
| 1 | Your predicted root bridge doesn't match CLI output | Priority misread, or a tiebreaker (MAC) situation you missed | `show spanning-tree detail` on any switch — check "Root Identifier" | Re-compare all four priorities carefully, including tiebreaker logic |
| 2 | A port you predicted Designated shows Alternate (or vice versa) | Path cost miscalculated, or an indirect path is actually cheaper than assumed | `show spanning-tree detail`, cross-check path cost table | Recompute total cost-to-root along every candidate path, not just the direct link |
| 3 | A switch shows two ports both claiming "root forwarding" | Misreading output — this should never happen in a converged topology | `show spanning-tree detail` again, confirm convergence (`show spanning-tree summary`) | If genuinely true, the topology hasn't finished converging yet — wait and re-check |

---

## 10. Design Analysis

**Why does STP guarantee exactly one root port per non-root switch and exactly one designated port per segment?** Because a loop-free tree, by definition, has exactly one path between any two points — if a switch had two root ports, or a segment had two designated ports, a loop would exist. STP's entire algorithm exists to enforce this "exactly one" invariant automatically, without requiring administrators to manually calculate and disable redundant links themselves. **Why prefer path cost over hop count?** Hop count doesn't account for link speed — a 3-hop path over Gigabit links is very likely faster in practice than a 1-hop path over a slow link, and STP's cost model reflects that reality rather than naively counting switches crossed.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...you inherit a campus network and need to understand, purely by reading `show spanning-tree` output across several switches, which links are actively forwarding and which are held in reserve — before touching any configuration.
- ...a "why is traffic between these two switches taking the slow path" ticket turns out to have a perfectly logical STP explanation once you trace root port and designated port assignments across the topology, exactly as done in Section 6.
- ...you're asked in an interview to explain root bridge election and port roles from memory — this is one of the single most common CCNA-adjacent interview questions for junior network engineer roles.

---

## 12. Stretch Goal

1. If SW3 (the current root) were powered off, which switch becomes the new root, and how would every port role in the topology change? Work it out by hand, then simulate the failure and verify.
2. Add a fifth switch and a fifth redundant link to the topology, and predict its complete port role table before running any `show` command.
3. Explain, without looking anything up, what would happen to convergence time and port roles if this topology were running RSTP instead of classic STP (a preview of Day 22).

---

## 13. Self-Assessment

- [ ] Can you determine a root bridge from a table of priorities and MAC addresses, by hand, in under a minute?
- [ ] Can you explain why every port on the root bridge is Designated/Forwarding without further calculation?
- [ ] Can you determine a non-root switch's root port using the path cost table from memory?
- [ ] Can you explain the difference between a Root Port, a Designated Port, and an Alternate/Non-Designated Port in one sentence each?
- [ ] Could you read `show spanning-tree detail` output cold (without a topology diagram) and correctly reconstruct which switch is root?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Root bridge election via Bridge ID comparison, root port selection via path cost, designated vs. alternate port roles per LAN segment, `show spanning-tree detail` interpretation.

**What I Learned:** STP analysis is pattern recognition. Once you know the root bridge, every other switch has exactly one root port, and every LAN segment has exactly one designated port — everything else is either alternate or non-designated blocking. The key insight from this lab: priority wins the root election, but path cost determines which port becomes the root port on non-root switches. GigabitEthernet interfaces have lower path cost (4) than FastEthernet (19), so Gigabit links were preferred as root ports wherever available — this explains why SW2 and SW4 both chose their Gig interfaces as root ports instead of FastEthernet alternate paths.

**Skills Practiced:** Root bridge identification from bridge priority, port role classification (Root/Designated/Alternate), interpreting `show spanning-tree detail` output, mapping logical STP roles to physical topology, understanding path cost differences between FastEthernet and GigabitEthernet, recognizing alternate blocking ports as loop prevention rather than failure.

---

## 15. GNS3 Lab

This lab is pure analysis of existing STP behavior with **no configuration performed by the student** — the entire lesson is reading and reasoning about a live topology. A GNS3 build is provided in [`GNS3/build_lab.py`](GNS3/build_lab.py) so you can reproduce a similarly redundant four-switch topology and observe real STP convergence and role assignment; see [`GNS3/README.md`](GNS3/README.md) for the Open vSwitch STP-support caveat and the Cisco IOSvL2/vIOS-L2 alternative.
