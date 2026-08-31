# Day 52 Lab Manual — STP & HSRP Synchronization

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure HSRP on two distribution switches (DSW1, DSW2) for VLANs 10 and 20 with opposite active/standby roles per VLAN, and synchronize each VLAN's STP root bridge placement with its HSRP active router. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): STP root bridge election and configuration; Domain 4/general redundancy concepts cover first-hop redundancy protocols (HSRP). This lab combines two separately-tested topics on purpose. |
| **Prerequisites** | STP fundamentals (root bridge election, bridge priority, root/designated ports), VLANs and SVIs, basic understanding of default gateway redundancy. |
| **Time Estimate** | 2 – 2.5 hours. |
| **Difficulty** | ⭐⭐⭐⭐☆ (Intermediate-Advanced) — not because any single command is hard, but because reasoning about *why* two independent protocols must be intentionally aligned is the actual skill being tested. |

---

## 1. Lab Overview + Learning Objectives

Two distribution switches, DSW1 and DSW2, serve two VLANs: VLAN 10 and VLAN 20. HSRP provides gateway redundancy for each VLAN's SVI, and each VLAN deliberately has its HSRP active router flipped — DSW1 is active for VLAN 10, DSW2 is active for VLAN 20 — which spreads gateway responsibility (and outbound traffic load) across both switches rather than idling one of them. STP is then explicitly aligned so that each VLAN's root bridge is the *same* switch as its HSRP active router, avoiding a subtle but real inefficiency: an HSRP-active router whose traffic must first traverse an inter-switch trunk to reach the actual STP root before going anywhere else.

By the end you will be able to:

- Configure HSRP with a virtual IP, custom priority, and preemption on two switches for two VLANs
- Explain HSRP's active/standby election logic and why priority direction is the opposite of STP's
- Configure STP root primary/secondary using Cisco's simplified syntax
- Explain why STP root bridge placement and HSRP active router placement should be intentionally synchronized
- Verify both protocols' state and correctly interpret "is this switch the root for this VLAN" and "is this switch active for this VLAN" independently
- Explain how this design achieves per-VLAN load balancing across two distribution switches

---

## 2. Business Context

**Why would a real company do this?**

A company with two distribution switches serving multiple VLANs faces a wasteful default: if one switch is simply "the primary" for everything, it handles 100% of gateway traffic for every VLAN while its redundant twin sits mostly idle — expensive hardware doing nothing until a failure. Splitting active HSRP responsibility per-VLAN (DSW1 active for VLAN 10, DSW2 active for VLAN 20) puts both switches to productive use simultaneously, while each still backs up the other.

- **"We paid for two identical distribution switches — we shouldn't have one sitting idle"** → per-VLAN HSRP active/standby splitting is the direct answer; both switches carry real production traffic under normal conditions.
- **"When VLAN 10's traffic leaves its access switches, it shouldn't have to hop across to the other distribution switch just to reach its own default gateway's actual forwarding path"** → this is precisely the STP/HSRP misalignment problem this lab solves. If DSW1 is HSRP-active for VLAN 10 but DSW2 is the STP root for VLAN 10, traffic still logically reaches DSW1 for routing, but the underlying Layer 2 topology's "shortest path" was actually optimized around DSW2 — creating suboptimal, sometimes doubled, traffic paths across the DSW1–DSW2 trunk.
- **"We need documented, intentional failover behavior, not something that happens to work by accident"** → `preempt` and matching STP root primary/secondary designations mean that after a failure and recovery, the network returns to its intended, documented state automatically, rather than staying in a degraded (but still functional) configuration indefinitely.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-52-Lab-STP-&-HSRP-Synchronization.png" alt="Day 52 STP HSRP Topology" width="900">
</p>

```text
                DSW1 ---- trunk ---- DSW2
                 |                    |
             Access switches carrying VLAN 10 and VLAN 20

VLAN 10:  DSW1 = HSRP Active + STP Root Primary   |  DSW2 = HSRP Standby + STP Root Secondary
VLAN 20:  DSW2 = HSRP Active + STP Root Primary   |  DSW1 = HSRP Standby + STP Root Secondary
```

Each VLAN's "primary" role (both HSRP-active and STP-root) is intentionally assigned to a *different* switch, so both distribution switches are fully utilized and mutually redundant.

---

## 4. IP Addressing Plan

| VLAN | Network | DSW1 SVI | DSW2 SVI | HSRP Virtual IP | HSRP Active | STP Root |
|---|---|---|---|---|---|---|
| VLAN 10 | 10.0.10.0/24 | 10.0.10.252 | 10.0.10.253 | 10.0.10.254 | DSW1 | DSW1 |
| VLAN 20 | 10.0.20.0/24 | 10.0.20.252 | 10.0.20.253 | 10.0.20.254 | DSW2 | DSW2 |

### 4.1 Why sized this way

Each VLAN gets its own `/24` for headroom — typical distribution-layer sizing for a user or department VLAN. The three addresses per VLAN (DSW1's real SVI, DSW2's real SVI, and the shared virtual IP) are placed at the top of the usable range (`.252`–`.254`) by convention, so a quick glance at any address in the subnet tells you whether it's an end host (typically lower in the range) or core infrastructure (top of the range) — a common real-world addressing convention worth adopting.

### 4.2 Manual calculation walkthrough

Take VLAN 10's `10.0.10.0/24`:

```text
Network address:    10.0.10.0
First usable host:  10.0.10.1
Last usable host:   10.0.10.254
Broadcast address:  10.0.10.255
```

End devices lease/are assigned from the lower portion of `10.0.10.1`–`.251`; the top three addresses (`.252`, `.253`, `.254`) are reserved for the two physical SVIs and the HSRP virtual IP, which every VLAN 10 end host uses as its default gateway — never the individual physical SVI addresses.

---

## 5. Pre-Configuration Checklist

1. VLANs 10 and 20 already exist and are trunked correctly between DSW1, DSW2, and any downstream access switches.
2. SVIs for VLAN 10 and VLAN 20 exist on both DSW1 and DSW2 with the physical (non-virtual) addresses from Section 4 above.
3. Decide *before* touching the CLI which switch is "primary" for which VLAN — write it down (Section 3's table) so your priority and STP root values are self-consistent instead of derived ad hoc mid-lab.
4. Understand that HSRP priority and STP priority use **opposite** comparison logic (higher wins for HSRP, lower wins for STP) — this is the single most common source of misconfiguration in this lab.

---

## 6. Configuration Tasks

### 6.1 VLAN 10 HSRP — DSW1 as active

```text
DSW1(config)#interface vlan 10
DSW1(config-if)#standby 1 ip 10.0.10.254
DSW1(config-if)#standby 1 priority 110
DSW1(config-if)#standby 1 preempt
DSW1(config-if)#exit
```

```text
DSW2(config)#interface vlan 10
DSW2(config-if)#standby 1 ip 10.0.10.254
DSW2(config-if)#standby 1 priority 100
DSW2(config-if)#standby 1 preempt
DSW2(config-if)#exit
```

**Mode:** Interface (SVI) config. **`standby 1 ip 10.0.10.254`** creates HSRP group 1 on this SVI with the shared virtual IP that end hosts use as their gateway — the group number must match on both switches for them to negotiate together. **`standby 1 priority 110`** (DSW1) vs. **`100`** (DSW2, the IOS default) — **higher priority wins the active role**, so DSW1 becomes active for VLAN 10 as intended. **`standby 1 preempt`** allows a higher-priority router to *reclaim* active status after recovering from a failure or reboot — without `preempt`, DSW1 would stay standby forever after any outage that let DSW2 take over, even once DSW1 is healthy again, which defeats the "documented, intentional state" goal from Section 2. **Memory aid:** "HSRP: high number, happy (active) router."

### 6.2 VLAN 20 HSRP — DSW2 as active (roles flipped)

```text
DSW1(config)#interface vlan 20
DSW1(config-if)#standby 2 ip 10.0.20.254
DSW1(config-if)#standby 2 priority 100
DSW1(config-if)#standby 2 preempt
DSW1(config-if)#exit
```

```text
DSW2(config)#interface vlan 20
DSW2(config-if)#standby 2 ip 10.0.20.254
DSW2(config-if)#standby 2 priority 110
DSW2(config-if)#standby 2 preempt
DSW2(config-if)#exit
```

**Why group 2, not group 1 again:** each VLAN's HSRP instance needs its own group number on a given switch (a switch is running two independent HSRP instances simultaneously, one per VLAN) — reusing group 1 for VLAN 20 would still technically work since groups are scoped per-interface, but using a distinct group number (2) matching the VLAN number is a strong, error-resistant convention worth adopting. **Why the priority values are exactly flipped from Section 6.1:** this is the deliberate load-balancing design from Section 2 — DSW2 (110, active) now carries VLAN 20's gateway traffic while DSW1 (100, standby) backs it up, the mirror image of VLAN 10's roles.

### 6.3 STP root for VLAN 10 — align with DSW1 (the HSRP active router)

```text
DSW1(config)#spanning-tree vlan 10 root primary
```

```text
DSW2(config)#spanning-tree vlan 10 root secondary
```

**Mode:** Global Config. **What it does:** `root primary` automatically calculates and sets a bridge priority low enough to guarantee this switch wins the VLAN 10 root election against current known bridge priorities in the network (rather than requiring you to manually compute and set a numeric priority value) — **lower STP priority wins**, the opposite direction from HSRP. `root secondary` sets a priority that will win the root election only if the primary root fails, pre-positioning DSW2 as the deliberate fallback rather than leaving the secondary root election to chance. **Why this matters — the actual point of the lab:** without this step, VLAN 10's Layer 2 topology could elect its root bridge independently of which switch is HSRP-active, meaning traffic could take a suboptimal path (crossing the DSW1–DSW2 trunk unnecessarily) before ever reaching its actual routing gateway. Aligning root placement with HSRP active placement keeps the Layer 2 forwarding topology and the Layer 3 gateway path pointed the same direction.

### 6.4 STP root for VLAN 20 — align with DSW2 (flipped, matching its HSRP active role)

```text
DSW2(config)#spanning-tree vlan 20 root primary
```

```text
DSW1(config)#spanning-tree vlan 20 root secondary
```

**Why flipped from 6.3:** DSW2 is VLAN 20's HSRP active router (Section 6.2), so DSW2 must also be VLAN 20's STP root — the same synchronization principle applied in the opposite direction, completing the per-VLAN load-balanced design.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show standby` | Full HSRP state per group: active/standby role, priority, virtual IP, preempt status |
| `show standby brief` | Condensed one-line-per-group summary |
| `show spanning-tree vlan 10` | Root bridge identity, this switch's role (Root or a numbered port role) |
| `show spanning-tree vlan 20` | Same, for VLAN 20 |
| `show ip interface brief` | Confirm SVI addressing matches Section 4's plan |

### 7.1 Expected Output Gallery

**`DSW1# show standby brief`**

```text
                     P indicates configured to preempt.
                     |
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Vl10        1    110 P Active   local           10.0.10.253     10.0.10.254
Vl20        2    100 P Standby  10.0.20.253     local           10.0.20.254
```

DSW1 is `Active` for group 1 (VLAN 10) and `Standby` for group 2 (VLAN 20) — exactly the intentional split from the design.

**`DSW2# show standby brief`**

```text
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Vl10        1    100 P Standby  10.0.10.252     local           10.0.10.254
Vl20        2    110 P Active   local           10.0.20.252     10.0.20.254
```

Exact mirror image of DSW1's output — confirming the roles are correctly flipped per VLAN.

**`DSW1# show spanning-tree vlan 10`**

```text
VLAN0010
  Spanning tree enabled protocol ieee
  Root ID    Priority    24576
             Address     0011.2233.4410
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
```

`This bridge is the root` confirms DSW1 is VLAN 10's STP root — matching its HSRP-active role for the same VLAN.

**`DSW1# show spanning-tree vlan 20`**

```text
VLAN0020
  Spanning tree enabled protocol ieee
  Root ID    Priority    24576
             Address     0011.2233.4420
  Bridge ID  Priority    28672
             Address     0011.2233.4410

  Root Port  Gi0/1
```

DSW1 is **not** the root for VLAN 20 (no "This bridge is the root" line; instead a `Root Port` is shown pointing toward DSW2) — exactly as intended, since DSW2 owns VLAN 20's root and active roles.

---

## 8. Common Mistakes (80/20 rule)

1. **Forgetting `preempt` on the higher-priority router.** Without it, a router that boots up after its peer (or recovers from a reload) never reclaims active status even though it has higher priority — HSRP state silently diverges from the documented design.
2. **Confusing HSRP priority direction with STP priority direction.** Higher wins for HSRP; lower wins for STP. Applying the wrong mental model to one or the other is the single most common conceptual error in this lab.
3. **Using the same HSRP group number for both VLANs on the same switch pair without realizing they're scoped per-interface anyway**, then being confused when troubleshooting output doesn't clearly indicate which VLAN a group belongs to — always match group number to VLAN number as a convention.
4. **Setting STP root primary/secondary but never checking whether it actually aligns with the HSRP-active switch** — a very easy copy-paste mistake is applying `root primary` to the same switch for *both* VLANs instead of flipping it for VLAN 20, silently undoing the whole point of the lab.
5. **Assuming `root primary`/`root secondary` sets a fixed, memorizable priority value.** It doesn't — it calculates a priority relative to the *current* lowest priority seen in the network at configuration time, which can differ from what you'd expect if run in a different order or against a network with unusual existing priorities.
6. **Forgetting the HSRP virtual IP must be identical on both switches within the same group** — end hosts have exactly one gateway IP; DSW1 and DSW2 must agree on it exactly.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Both switches show `Active` for the same HSRP group | Group number, virtual IP, or VLAN mismatch preventing negotiation | `show standby` | Confirm both switches use identical group number and virtual IP on the matching VLAN's SVI |
| 2 | Higher-priority switch stays Standby after recovering from an outage | `preempt` not configured | `show standby` (look for "P" preempt flag) | Add `standby <group> preempt` |
| 3 | HSRP-active switch is not the STP root for that VLAN | Root primary/secondary not aligned with HSRP roles | `show spanning-tree vlan <id>` + `show standby brief` side by side | Reconfigure `spanning-tree vlan <id> root primary` on the correct (HSRP-active) switch |
| 4 | `spanning-tree vlan 10 root primary` didn't produce the expected low priority | A third switch in the network already has an unusually low priority, so Cisco's automatic calculation couldn't go low enough | `show spanning-tree vlan 10` (compare Bridge ID priorities across all switches) | Manually set an explicit lower priority, or address the unexpected competing switch |
| 5 | End hosts intermittently lose gateway reachability during a failover | Both switches configured correctly but `preempt` timing causes a brief flap during recovery | `show standby` history / syslog | This is often expected transient behavior; confirm hold/hello timers are reasonable for the topology |

---

## 10. Design Analysis

**Why this design over alternatives?**

- **Why split active roles per-VLAN instead of making one switch active for everything?** A single "primary switch for all VLANs" design leaves the secondary switch's forwarding capacity almost entirely unused during normal operation — pure waste of provisioned hardware. Splitting by VLAN means both switches do real work simultaneously while each still fully backs up the other, which is standard distribution-layer design in real campus/enterprise networks (often called "HSRP load sharing").
- **Why must STP root and HSRP active be the *same* switch per VLAN, rather than independent?** If they're misaligned, a packet from an access-layer host can reach its Layer 2 root/forwarding path optimally, then still need to cross the DSW1–DSW2 trunk at Layer 3 to reach its actual HSRP-active gateway — an unnecessary extra hop baked into every single packet leaving that VLAN, invisible in a diagram but real in latency and trunk utilization. Aligning them means the "closest" switch at Layer 2 is also the routing gateway at Layer 3.
- **Why use `root primary`/`root secondary` instead of manually setting numeric bridge priorities?** The Cisco macro command removes an entire class of arithmetic mistakes (accidentally setting a priority that doesn't actually win against the current topology) and self-documents intent directly in the running-config — anyone reading `spanning-tree vlan 10 root primary` instantly understands the design decision, versus a bare `spanning-tree vlan 10 priority 4096` requiring the reader to know what that number means relative to the rest of the network.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a campus network's two core/distribution switches are deliberately load-balanced by VLAN so both handle real traffic — exactly this lab's design, at enterprise scale.
- ...a network engineer is asked "why does traffic between these two floors seem slower than expected" and the root cause turns out to be exactly this lab's failure mode: STP root and HSRP active pointing at different switches, forcing an extra trunk hop on every packet.
- ...a planned maintenance window on one distribution switch requires confirming, ahead of time, that `preempt` and root secondary are correctly configured so the network fails over cleanly and — just as importantly — fails *back* cleanly once maintenance is done.
- ...a new engineer inherits a network and needs to quickly understand "which switch is really in charge of what" — `show standby brief` and `show spanning-tree vlan <id>` together are the fastest way to build that mental model.

---

## 12. Stretch Goal

1. Add a third VLAN (VLAN 30) with its own HSRP group and STP root assignment, and decide — with written justification — whether to assign it to DSW1 or DSW2 based on estimated relative traffic load between VLANs 10 and 20.
2. Configure HSRP object tracking (`standby 1 track <interface> decrement <value>`) so that if DSW1 loses its uplink to the core, its HSRP priority automatically drops below DSW2's, triggering an active role handoff even though DSW1's VLAN 10 SVI itself never went down.
3. Deliberately misalign STP root and HSRP active for one VLAN, then use `traceroute`/hop analysis from an end host to observe and document the extra hop this creates — turn the Design Analysis argument into something you've personally measured.

---

## 13. Self-Assessment

- [ ] Can you state, from memory, which direction "wins" for HSRP priority and which direction wins for STP priority, and explain why they're opposite without looking it up?
- [ ] Can you write the full HSRP config (virtual IP, priority, preempt) for one VLAN on both switches from memory?
- [ ] Can you explain what `spanning-tree vlan X root primary` actually calculates, rather than just what it's "supposed to do"?
- [ ] Can you explain, in your own words, why STP root and HSRP active being on different switches for the same VLAN is a real (if subtle) problem, not just an aesthetic inconsistency?
- [ ] Could you sketch this lab's full per-VLAN role table (Section 3) from memory and explain the reasoning behind each assignment?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** HSRP virtual gateway redundancy, active/standby election and priority, preemption; STP root bridge election and the `root primary`/`root secondary` macro commands; the design principle of synchronizing Layer 2 topology (STP) with Layer 3 gateway placement (HSRP) per VLAN; per-VLAN load balancing across redundant distribution switches.

**What I learned:** two protocols can each be individually configured "correctly" in isolation and still produce a suboptimal network if their interaction isn't considered — this lab's entire point is that HSRP and STP configured independently, without deliberate alignment, silently creates extra hops that a config review focused on either protocol alone would never catch. HSRP and STP use opposite priority-comparison logic, which is a small detail with outsized potential for misconfiguration.

**Skills practiced:** HSRP configuration (virtual IP, priority, preempt, groups), STP root/secondary root configuration, cross-protocol design reasoning, side-by-side verification of two independent but related protocol states, per-VLAN redundancy design.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for an automated build using VyOS for DSW1/DSW2 and Open vSwitch for the access-layer switch. Note: VyOS uses **VRRP**, not Cisco's proprietary HSRP, as its first-hop redundancy protocol — the concepts (virtual IP, priority-based active election, preemption) map closely, but VRRP's priority range and default values differ slightly from HSRP's; the GNS3 README includes a command-mapping table.
