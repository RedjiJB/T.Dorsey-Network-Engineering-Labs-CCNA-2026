# Day 21 Lab Manual — Configuring Spanning Tree

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Actively configure STP behavior on a four-switch, two-VLAN topology: set primary/secondary root bridges per VLAN, influence root port selection via cost and port priority, and harden edge ports with PortFast and BPDU Guard. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): STP configuration, root bridge tuning, PortFast, BPDU Guard. Directly builds on Day 20's analysis skills. |
| **Prerequisites** | Day 20 (STP analysis, root bridge election, port role theory) — this lab is the "now configure what you previously only analyzed" follow-up. |
| **Time Estimate** | 2 – 2.5 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the commands are short, but predicting *whether* a cost or priority change will actually alter port roles requires real understanding, not memorization. |

---

## 1. Lab Overview

Day 20 taught you to read STP's default decisions. This lab teaches you to **change** them: assign specific switches as root (and backup root) for specific VLANs, deliberately shift a root port election by raising a link's cost, deliberately (attempt to) shift a different election by changing port priority, and lock down edge ports so end-user devices can never accidentally participate in STP calculations at all.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Configure primary and secondary root bridges per VLAN with `spanning-tree vlan <id> root primary/secondary`
- Explain what priority values those macros actually set, and why
- Influence (or correctly predict when you *cannot* influence) root port selection using interface cost
- Use port priority as a tiebreaker between otherwise-equal-cost paths
- Harden access ports with PortFast and BPDU Guard, and explain why both matter together

---

## 2. Business Context

**Why would a real company do this?**

Default STP timers and priorities work, but they don't reflect *your* network's actual topology preferences — the switch STP happens to elect as root by default might be an access-layer switch in a wiring closet, not the powerful, centrally-located distribution switch that should obviously be handling that role. Real network designs deliberately pin root bridge placement (and a backup, in case the primary fails) so STP's behavior matches the engineer's intent rather than an accident of default MAC addresses. PortFast and BPDU Guard exist because the single most common way a real office network suffers an accidental STP-related outage is an employee plugging a cheap unmanaged switch or a mis-wired cable into a wall jack that loops back into itself — BPDU Guard is the safety net that shuts that port down in milliseconds instead of letting it destabilize the whole spanning tree.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-21-Lab-Configuring-Spanning-Tree.png" alt="Day 21 Topology" width="800">
</p>

Four switches (SW1–SW4), each running two VLANs (VLAN1 and VLAN2), interconnected with FastEthernet links (Fa0/1, Fa0/2, Fa0/3 on each switch).

| Switch | VLAN1 Bridge ID (initial) | VLAN2 Bridge ID (initial) |
|---|---|---|
| SW1 | Priority 24577, MAC 0060.2F90.D14A | Priority 28674, MAC 0060.2F90.D14A |
| SW2 | Priority 28673, MAC 0001.4301.4B81 | Priority 24578, MAC 0001.4301.4B81 |
| SW3 | Priority 32769, MAC 0040.0B50.AA56 | Priority 32770, MAC 0040.0B50.AA56 |
| SW4 | Priority 32769, MAC 0090.0C03.2D70 | Priority 32770, MAC 0090.0C03.2D70 |

**Initial state (before this lab's changes):** SW1 is already root for VLAN1; SW2 is already root for VLAN2 — this lab's Section 6.1 configuration makes that arrangement explicit and adds a defined backup, rather than leaving it to accident.

---

## 4. IP Addressing Plan

No new IP addressing in this lab — STP configuration operates entirely below Layer 3. If extending this lab with live hosts, reuse the VLAN `/26` addressing convention from Day 16 (VLAN1 and VLAN2 would each need their own subnet).

---

## 5. Pre-Configuration Checklist

1. Confirm the four-switch topology matches Section 3, with VLAN1 and VLAN2 both present on all four switches.
2. Run `show spanning-tree vlan 1` and `show spanning-tree vlan 2` on all four switches **before making any changes** — this is your Day 20-style baseline, and Lab Question 1 requires it.
3. Have the priority table (Section 3) open for reference.

---

## 6. Configuration Tasks

### 6.1 Configure Primary/Secondary Root Bridges Per VLAN

```text
! On SW1
SW1(config)#spanning-tree vlan 1 root primary
SW1(config)#spanning-tree vlan 2 root secondary

! On SW2
SW2(config)#spanning-tree vlan 2 root primary
SW2(config)#spanning-tree vlan 1 root secondary
```

> **What `root primary` and `root secondary` actually do:** these are convenience macros, not magic. `root primary` checks the current lowest priority in the topology for that VLAN and sets the local switch's priority to **24576** (or, if something in the topology is already lower, drops further in steps of 4096 until it wins) — guaranteeing this switch becomes root without you manually calculating the exact number needed. `root secondary` sets priority to **28672**, guaranteeing second-lowest-priority standing (a designated backup) without requiring the primary to actually fail first to find out who takes over. **Memory aid:** "primary = 24576, secondary = 28672 — both suspiciously close to the default 32768, just two clean steps lower." **Mode:** global config, no VLAN sub-mode required — the VLAN ID is a parameter of the command itself.

**Result:** SW1 becomes root for VLAN1 (secondary root for VLAN2); SW2 becomes root for VLAN2 (secondary root for VLAN1). Every switch recalculates port roles based on the new root bridges. Root ports shift to the best path toward each VLAN's respective new root. Any port that was previously a root port on SW1 or SW2 for the *other* VLAN typically becomes designated instead, since SW1/SW2 are now guaranteed favorable priority standing on both VLANs.

**Verify:**

```text
SW1#show spanning-tree vlan 1
SW1#show spanning-tree vlan 2
```

Confirm "This bridge is the root" appears for VLAN1 on SW1 and for VLAN2 on SW2.

### 6.2 Influence Root Port Selection with Interface Cost

```text
SW4(config)#interface FastEthernet0/2
SW4(config-if)#spanning-tree vlan 1 cost 100
```

> **What this does and doesn't guarantee:** raising F0/2's VLAN1 cost to 100 only changes SW4's root port selection **if** the resulting total path cost through F0/2 becomes worse than SW4's best alternative path. If SW4's other available path to the VLAN1 root already has an equal or lower total cost, nothing changes — SW4 simply keeps its current root port. **This is the single most commonly misunderstood STP configuration concept:** modifying one interface's cost is a *relative* change, evaluated against whatever else is available, not an absolute command that "makes this port worse in isolation." Always compare the *total* path cost of every candidate path before predicting the outcome of a cost change.

**Verify:**

```text
SW4#show spanning-tree vlan 1
```

Check whether the Root Port field changed. If it didn't, that's a valid, informative result — it tells you SW4's alternate path was already cost-competitive even before this change.

### 6.3 Influence Root Port Selection with Port Priority (Tiebreaker Only)

```text
SW1(config)#interface FastEthernet0/1
SW1(config-if)#spanning-tree vlan 1 port-priority 240
```

> **Port priority only matters when path costs tie.** It's a secondary tiebreaker (after Bridge ID for root election, after path cost for root port election) used to decide between two otherwise-equal-cost paths. Lowering a port's priority number makes it *more* preferred (same "lower number wins" pattern as Bridge ID priority); raising it to 240 (a high number = low preference) makes SW1's F0/1 *less* attractive as the designated/preferred path if some other port has equal cost and a lower priority number. **If SW3's path through SW1 was already strictly the lowest-cost path** (not tied with anything), this change won't alter SW3's root port choice at all — cost is compared before priority, and a strict cost advantage is never overridden by a priority change on the losing side.

**Verify:**

```text
SW3#show spanning-tree vlan 1
```

Compare SW3's root port before and after — same reasoning as Section 6.2: no change is a valid, expected outcome unless a genuine cost tie existed.

### 6.4 Harden Edge Ports — PortFast and BPDU Guard

```text
! On SW3
SW3(config)#interface FastEthernet0/3
SW3(config-if)#switchport mode access
SW3(config-if)#spanning-tree portfast
SW3(config-if)#spanning-tree bpduguard enable
SW3(config-if)#exit

! On SW4
SW4(config)#interface FastEthernet0/3
SW4(config-if)#switchport mode access
SW4(config-if)#spanning-tree portfast
SW4(config-if)#spanning-tree bpduguard enable
SW4(config-if)#exit
```

> **PortFast:** on an access port, immediately transitions to the forwarding state, skipping STP's listening and learning delays (roughly 30 seconds total on classic STP). Essential for end-user devices, which don't run STP themselves and gain nothing from those delays — but genuinely dangerous if applied to a port that connects to another switch, since it bypasses the loop-detection window that protects the network while a new link comes up. **BPDU Guard:** if the port ever receives a BPDU (a sign that something running STP — most likely another switch, expected or rogue — is connected instead of a genuine end device), the port is immediately error-disabled (shut down), rather than allowed to participate in the spanning tree at all. **Why both together, always, on access ports:** PortFast alone makes a bad assumption ("nothing here will ever run STP") without enforcing it; BPDU Guard is what actually *enforces* that assumption and protects the network the moment it turns out to be wrong.

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| Every switch | `show spanning-tree vlan 1` / `vlan 2` | Root bridge identity, local bridge priority, port roles |
| SW1, SW2 | `show spanning-tree vlan 1` / `vlan 2` | "This bridge is the root" appears on the correct switch for the correct VLAN |
| SW4 | `show spanning-tree vlan 1` | Root port before/after the cost change in Section 6.2 |
| SW3 | `show spanning-tree vlan 1` | Root port before/after the port-priority change in Section 6.3 |
| SW3, SW4 | `show running-config interface FastEthernet0/3` | `spanning-tree portfast` and `spanning-tree bpduguard enable` both present |

### 7.1 Expected Output Gallery

**`SW1# show spanning-tree vlan 1`** (after Section 6.1)

```text
VLAN0001
  Spanning tree enabled protocol ieee
  Root ID    Priority    24577
             Address     0060.2F90.D14A
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24577  (priority 24576 sys-id-ext 1)
             Address     0060.2F90.D14A
```

**`SW3# show spanning-tree interface FastEthernet0/3 detail`** (after Section 6.4)

```text
Port 3 (FastEthernet0/3) of VLAN0001 is designated forwarding
   Port path cost 19, Port priority 128, Port Identifier 128.3
   Designated root has priority 24577, address 0060.2F90.D14A
   The port is in the portfast mode
   BPDU: sent 0, received 0
```

If a rogue device or switch sends a BPDU into this port, the next check would show:

```text
%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port FastEthernet0/3 with BPDU Guard enabled. Disabling port.
%PM-4-ERR_DISABLE: bpduguard error detected on Fa0/3, putting Fa0/3 in err-disable state
```

---

## 8. Common Mistakes (the 80/20)

1. **Assuming a cost or priority change always alters port roles.** Both are *relative* changes evaluated against whatever else is available — no visible change after a correctly-typed command is a completely valid, expected outcome and not proof the command failed.
2. **Confusing `root primary`/`root secondary` with manually calculating and typing a specific priority number.** The macros exist precisely so you don't have to do that math by hand every time — but you should still understand what values they set (24576 / 28672) so you can reason about the result.
3. **Applying PortFast to a port that connects to another switch**, bypassing the loop-detection delay on a link that genuinely could introduce a loop — PortFast is for end-user/host-facing ports only.
4. **Enabling PortFast without BPDU Guard.** PortFast alone is an assumption; BPDU Guard is the enforcement. Configuring one without the other leaves either a false sense of security (PortFast alone) or an access port that never gets the fast-forwarding benefit (BPDU Guard alone, less common but still incomplete).
5. **Forgetting that port priority only breaks ties in path cost, and does nothing when one path already strictly costs less.** Expecting a priority change to override a real cost difference is a fundamental misunderstanding of STP's comparison order (Bridge ID → path cost → sender Bridge ID → port priority → port ID).
6. **Not re-running baseline verification (Lab Question 1's `show spanning-tree` snapshot) before making changes.** Without a documented "before" state, it's impossible to confidently attribute a change in port roles to the specific command you just ran versus something that was already true.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | `root primary` didn't make this switch root | Another switch in the topology has an even lower manually-configured priority | `show spanning-tree vlan <id>` on all switches | Lower this switch's priority further, or fix the conflicting switch |
| 2 | Cost change had no visible effect | The alternate path's total cost was already equal or lower | `show spanning-tree vlan <id>` — compare total path cost on all candidate ports | Expected result if true; verify by computing the alternate path's total cost by hand |
| 3 | Port priority change had no visible effect | No genuine cost tie existed between candidate paths | Same as above | Expected result; port priority is a tiebreaker only |
| 4 | PortFast port doesn't skip listening/learning | `spanning-tree portfast` applied at the wrong scope, or port isn't in access mode | `show running-config interface <id>` | Re-apply, confirm `switchport mode access` is set |
| 5 | BPDU Guard didn't shut the port down when a switch was connected | BPDU Guard not actually enabled, only PortFast | `show spanning-tree interface <id> detail` | Add `spanning-tree bpduguard enable` explicitly |
| 6 | Port went into err-disabled state unexpectedly | BPDU Guard correctly triggered — something sending BPDUs is connected to what should be a host-only port | `show interfaces status`, check physical connection | Investigate what's actually connected before re-enabling with `shutdown` / `no shutdown` |

---

## 10. Design Analysis

**Why explicitly configure root bridges instead of trusting the default election?** Default election depends on MAC addresses, which have no relationship to which switch is actually best positioned (physically central, highest capacity) to serve as root — explicit configuration lets the network's logical design match its intended traffic flow, not an accident of hardware serial numbers. **Why configure a secondary root at all?** Without one, a root bridge failure triggers a full re-election among whatever switches happen to have the next-lowest default priorities — possibly an underpowered access switch nobody intended for that role. A pre-configured secondary guarantees a known, tested, intentional failover target. **Why is port priority rarely useful compared to cost?** Because ties in path cost are relatively uncommon in real topologies with varied link speeds — cost differences usually already decide the outcome, which is why the CCNA exam tests understanding that priority is a tiebreaker, not a primary lever.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a network design review flags that the current STP root bridge is a small access-layer switch in a closet rather than the core switch — the fix is exactly Section 6.1's `root primary`/`root secondary` pattern, deliberately pinning root placement.
- ...an engineer needs to force traffic away from a link scheduled for maintenance without physically unplugging it — raising that link's STP cost (Section 6.2) is a legitimate, non-disruptive way to make STP prefer an alternate path in advance.
- ...IT security policy mandates BPDU Guard on every access port campus-wide, specifically because an employee plugging in a cheap switch (intentionally or not) is one of the most common real-world causes of accidental network loops and outages.

---

## 12. Stretch Goal

1. Manually calculate and configure a specific priority value (not using `root primary`/`root secondary`) that makes SW3 root for VLAN1, and verify it against a hand-calculated comparison of all four switches' priorities.
2. Deliberately create a scenario where two paths tie in cost, then use port priority to break the tie predictably — document before/after root port selection.
3. Simulate a rogue switch plugged into a BPDU-Guard-protected port and walk through the full err-disable recovery process (`shutdown` / `no shutdown`, or configuring `errdisable recovery cause bpduguard` for automatic recovery after a timeout).

---

## 13. Self-Assessment

- [ ] Can you state, from memory, the exact priority values `root primary` and `root secondary` configure?
- [ ] Can you explain why a cost or priority change might produce zero visible effect, and why that's not a failure?
- [ ] Can you explain the STP tiebreaker order (Bridge ID → path cost → sender Bridge ID → port priority → port ID) at a high level?
- [ ] Can you explain why PortFast alone is incomplete without BPDU Guard?
- [ ] Could you walk a colleague through recovering an err-disabled BPDU Guard port?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Per-VLAN root bridge configuration, primary/secondary root macros, interface cost and port priority as STP tuning levers, PortFast, BPDU Guard.

**What I Learned:** Configuring STP is different from analyzing it. Analysis tells you what's happening; configuration tells the switch what *should* happen. The biggest insight from this lab: `root primary` and `root secondary` are convenience macros that set bridge priority to 24576 or 28672 automatically — you don't have to manually calculate priority values. The second insight: changing interface cost only matters relative to other available paths. If you raise one interface's cost but the backup path is also expensive, nothing changes — STP compares *best* paths, not individual links in isolation. PortFast and BPDU Guard are non-negotiable on access ports: without them, a user plugging in a rogue switch can create a broadcast storm within seconds. BPDU Guard is the safety net that PortFast's speed assumption depends on.

**Skills Practiced:** STP root bridge configuration per VLAN, primary/secondary root bridge election, interface cost modification, port priority modification, PortFast and BPDU Guard configuration, multi-VLAN STP behavior, verifying STP role/state changes across a four-switch topology.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for the Open vSwitch STP limitation and the Cisco IOSvL2/vIOS-L2 alternative needed to fully reproduce this lab's per-VLAN priority and BPDU Guard behavior.
