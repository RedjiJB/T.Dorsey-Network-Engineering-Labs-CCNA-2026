# Day 19 Lab Manual — VTP, Trunking, and VLAN Management

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure a three-switch topology with VTP-based centralized VLAN management, comparing Server, Transparent, and Client mode behavior, and harden trunk ports against DTP negotiation. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): VTP, trunking, DTP. VTP mode behavior is a frequently-tested exam topic precisely because its failure modes are counter-intuitive. |
| **Prerequisites** | Day 17 (trunking fundamentals, allowed-VLAN lists). |
| **Time Estimate** | 2 – 2.5 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the three VTP modes behave in ways that are easy to state but easy to misremember under pressure; this lab is built around observing the *differences*, not just configuring one mode. |

---

## 1. Lab Overview

VTP (VLAN Trunking Protocol) lets one switch (the **Server**) create and delete VLANs once, and have every other switch in the same VTP domain **learn** those VLANs automatically over trunk links — without an administrator manually running `vlan 10` / `name Engineering` on every switch in the building. This lab builds a three-switch topology where each switch runs a different VTP mode (Server, Transparent, Client) specifically so you observe, hands-on, how differently each one behaves when a VLAN is created.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Configure trunk ports and disable DTP negotiation with `switchport nonegotiate`
- Configure and verify VTP domain membership and mode on multiple switches
- Explain and demonstrate the behavioral difference between VTP Server, Transparent, and Client modes
- Explain the security risk of an unprotected VTP Server and why revision number matters
- Configure host-facing access ports and verify VLAN propagation with `show vlan brief`

---

## 2. Business Context

**Why would a real company do this?**

A campus with 30 switches and 40 VLANs is a nightmare to manage by hand — one VLAN added to the Server propagates everywhere automatically via VTP, instead of an admin manually touching 30 devices (and inevitably missing one). But VTP is a double-edged sword: it's also the mechanism behind one of networking's classic "how did the whole campus VLAN database just get wiped" incidents — plug in a switch that happens to be in VTP Server mode, in the same domain name, with a higher revision number than production, and it can silently overwrite every switch's VLAN database on connection. This lab is built to make both sides of that trade-off concrete: the convenience of automatic propagation (Server → Client) and the safety of deliberately opting out of it (Transparent mode), which is exactly why real production networks are increasingly built with VTP Transparent (or VTP off entirely) as the default, treating VLAN creation as a manual, reviewed, per-switch change instead.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-19-Lab-DTP-%26-VTP.png" alt="Day 19 Topology" width="800">
</p>

```text
SW1 (VTP Server) ===trunk=== SW2 (VTP Transparent) ===trunk=== SW3 (VTP Client)
```

| Switch | VTP Mode | Domain | VLANs Created Locally |
|---|---|---|---|
| SW1 | Server | CCNA | 10, 20, 30 |
| SW2 | Transparent | CCNA | 40 (local only — does not propagate) |
| SW3 | Client | CCNA | Cannot create local VLANs |

---

## 4. IP Addressing Plan

This lab is Layer 2 only — no IP addressing is required for the VTP/trunking behavior itself. Host-facing access ports are assigned to VLANs 10, 20, and 30 in Step 5, but IP address assignment to end hosts is out of scope; the focus is entirely on VLAN database propagation and trunk configuration. (If extending this lab with live PCs, reuse the `/26` addressing convention from Day 16.)

---

## 5. Pre-Configuration Checklist

1. Place SW1, SW2, SW3 in a line topology (SW1↔SW2↔SW3).
2. Cable the two inter-switch links; leave host-facing ports unconfigured until Step 5.
3. Confirm no VLANs exist yet on any switch (`show vlan brief` should show only the default VLAN 1) — a clean starting VTP revision number matters (see Common Mistakes #1).

---

## 6. Configuration Tasks

### 6.1 Trunk Ports with DTP Disabled (all three switches)

```text
SW1(config)#interface gigabitEthernet0/1
SW1(config-if)#switchport mode trunk
SW1(config-if)#switchport nonegotiate
SW1(config-if)#exit
```

Repeat the equivalent for SW2's two trunk interfaces (toward SW1 and SW3) and SW3's one trunk interface (toward SW2).

> **Mode:** Interface config. `switchport mode trunk` forces the port into trunking regardless of what the far end negotiates. `switchport nonegotiate` disables **DTP (Dynamic Trunking Protocol)** — the protocol that would otherwise let two connected switches auto-negotiate whether a link becomes a trunk or stays access. **Why disable it:** leaving DTP on means the port's actual mode depends on what the far end announces — if someone accidentally misconfigures the far end as access, DTP can silently negotiate your side down to access too, breaking VLAN traffic with no error message. Manually forcing `trunk` + `nonegotiate` guarantees the port's behavior is exactly what you configured, regardless of what's plugged into the other end.

**Verify:**

```text
SW1#show interface gigabitEthernet0/1 switchport
```

Expected indicators: `Administrative Mode: trunk`, `Operational Mode: trunk`, `Negotiation of Trunking: Off`, `Trunking Encapsulation: dot1q`.

### 6.2 SW1 — VTP Server, create VLANs

```text
SW1(config)#vtp domain CCNA
SW1(config)#vtp mode server
SW1(config)#vlan 10
SW1(config-vlan)#name VLAN10
SW1(config-vlan)#exit
SW1(config)#vlan 20
SW1(config-vlan)#name VLAN20
SW1(config-vlan)#exit
SW1(config)#vlan 30
SW1(config-vlan)#name VLAN30
SW1(config-vlan)#exit
```

> **Server mode is the default VTP mode** on most Cisco switches, so `vtp mode server` may be a no-op if it's already the default — but setting it explicitly is good practice so the config is self-documenting. `vtp domain CCNA` establishes the domain name every switch must match to exchange VTP information at all — a switch in a different domain (or no domain set) ignores VTP advertisements entirely, by design.

**Verify:**

```text
SW1#show vtp status
```

Expected: `VTP Operating Mode: Server`, `VTP Domain Name: CCNA`, and a **Configuration Revision** number that increments by 1 with each VLAN database change (this number is the crux of the VTP security risk discussed in Section 8).

### 6.3 SW2 — VTP Transparent, add a local-only VLAN

```text
SW2(config)#vtp domain CCNA
SW2(config)#vtp mode transparent
SW2(config)#vlan 40
SW2(config-vlan)#name VLAN40
SW2(config-vlan)#exit
```

> **Transparent mode does not create or delete VLANs on behalf of other switches, and does not apply VLAN changes it receives to its own database** — but (this is the counter-intuitive part most students miss) it still **forwards** VTP advertisements it receives out its other trunk ports, without acting on them. SW1's VLANs 10/20/30 still reach SW3 *through* SW2, even though SW2 itself ignores them.

**Verify — the key finding of this step:**

```text
SW2#show vlan brief
```

VLAN 40 shows as active **only on SW2**. Check `show vlan brief` on SW1 and SW3 — **neither shows VLAN 40.** This is expected, correct Transparent-mode behavior, not a misconfiguration: a Transparent-mode switch's own local VLANs never propagate outward.

### 6.4 SW3 — VTP Client, attempt to create a VLAN (expect failure)

```text
SW3(config)#vtp domain CCNA
SW3(config)#vtp mode client
SW3(config)#vlan 50
```

**Result:**

```text
SW3 VLAN configuration not allowed when device is in CLIENT mode.
```

> **Client mode cannot create, delete, or rename VLANs locally — full stop.** It receives and applies whatever the Server (SW1) advertises (via SW2's pass-through, since SW2 is Transparent) and nothing else. This is the mode's entire purpose: guarantee every Client switch's VLAN database is *always* a mirror of the Server's, with zero risk of local drift.

**Verify:**

```text
SW3#show vlan brief
```

VLANs 10, 20, 30 (from SW1, the Server) appear as active on SW3 — proving VTP propagation crossed SW2 even though SW2 itself is Transparent. VLAN 40 (SW2's local-only VLAN) and VLAN 50 (the failed attempt) do **not** appear.

### 6.5 Access Ports (all three switches)

```text
! SW1 host ports
SW1(config)#interface range fastEthernet0/1 - 2
SW1(config-if-range)#switchport mode access
SW1(config-if-range)#switchport access vlan 10
SW1(config-if-range)#exit
SW1(config)#interface fastEthernet0/3
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 20
SW1(config-if)#exit

! SW2 host ports
SW2(config)#interface range fastEthernet0/3 - 4
SW2(config-if-range)#switchport mode access
SW2(config-if-range)#switchport access vlan 20
SW2(config-if-range)#exit

! SW3 host ports
SW3(config)#interface range fastEthernet0/1 - 2
SW3(config-if-range)#switchport mode access
SW3(config-if-range)#switchport access vlan 30
SW3(config-if-range)#exit
```

> SW3 can assign ports to VLAN 30 even though SW3 is a **Client** and never created VLAN 30 itself — Client mode can still *use* any VLAN the Server has propagated to it; it just can't create new ones locally. This distinction (can't create, can use) is one of the most commonly tested VTP details on the exam.

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| All switches | `show interface <id> switchport` | Administrative Mode: trunk, Negotiation of Trunking: Off |
| All switches | `show vtp status` | Mode, domain name, revision number |
| All switches | `show vlan brief` | Which VLANs are present, and on which switches |
| Access ports | `show interface <id> switchport` | Administrative Mode: static access, Negotiation of Trunking: Off |

### 7.1 Expected Output Gallery

**`SW1# show vtp status`**

```text
VTP Version capable             : 1 to 3
VTP version running             : 2
VTP Domain Name                 : CCNA
VTP Pruning Mode                : Disabled
VTP Traps Generation            : Disabled
Device ID                       : 0001.42AB.11C0
Configuration last modified by 0.0.0.0 at ...

Feature VLAN:
--------------
VTP Operating Mode                : Server
Maximum VLANs supported locally   : 255
Number of existing VLANs          : 8
Configuration Revision            : 3
```

**`SW3# show vlan brief`** (after propagation)

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active
10   VLAN10                           active
20   VLAN20                           active
30   VLAN30                           active    Fa0/1, Fa0/2
```

Note VLAN 10 and 20 show `active` on SW3 with **no ports assigned** — this is normal: VTP propagates the VLAN's existence, not which ports on a remote switch belong to it. Port assignment is always local, per-switch, manual work regardless of VTP mode.

---

## 8. Common Mistakes (the 80/20)

1. **Never setting a VTP domain password on a Server, in a real network.** Any switch that joins the domain (matching name, and — critically — a **higher** configuration revision number) can silently overwrite the entire VLAN database of every Client and Server in the domain. This lab doesn't require a password for learning purposes, but flag it explicitly: production VTP Servers should always use `vtp password <secret>`.
2. **Confusing Transparent mode's "doesn't apply changes" with "doesn't forward them."** Students frequently assume Transparent = "VTP stops here." It doesn't — Transparent switches still relay VTP advertisements to further switches down the chain; they just don't act on the content themselves.
3. **Trying to create a VLAN on a Client switch and being surprised by the rejection.** This is correct, expected behavior, not a bug — Client mode structurally cannot create local VLANs.
4. **Leaving DTP enabled on trunk links.** Without `switchport nonegotiate`, a misconfigured neighbor can silently negotiate your trunk down to access mode.
5. **Forgetting that a factory-default switch with a stale but higher VTP revision number is dangerous to plug into a live network**, even in Client mode — an old lab switch, still holding a revision number from a previous exercise, can override current production VLANs the moment it joins the domain.
6. **Not matching the domain name exactly (including case) across all three switches** — VTP information is silently ignored between mismatched domains, with no propagation and no error either.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Trunk shows access or `desirable` instead of `on`/`trunking` | DTP negotiated incorrectly, or one side isn't forced to trunk | `show interface <id> switchport` | `switchport mode trunk` + `switchport nonegotiate` on both ends |
| 2 | VLANs created on SW1 never appear on SW3 | Domain name mismatch, or SW2's link to SW3 isn't trunking | `show vtp status` on all switches, `show interface trunk` | Match domain names exactly; confirm trunk status |
| 3 | VLAN 40 unexpectedly appears on SW1 or SW3 | SW2 wasn't actually in Transparent mode when VLAN 40 was created | `show vtp status` on SW2 | Correct SW2's mode, recreate VLAN 40 if needed |
| 4 | Can't create a VLAN on SW3 | SW3 is (correctly) in Client mode | `show vtp status` | Expected behavior — create the VLAN on the Server (SW1) instead |
| 5 | A newly connected switch wipes out existing VLANs | Its VTP revision number was higher than the domain's current Server | `show vtp status` before connecting any new switch | Reset revision to 0 (change domain name, then change back, or use `vtp mode transparent` temporarily) before connecting an unknown switch |
| 6 | Access port shows unexpected VLAN membership | Port assignment was never actually made locally, or is stale from a previous VLAN | `show vlan brief`, `show running-config interface <id>` | Re-apply `switchport access vlan <id>` |

---

## 10. Design Analysis

**Why VTP at all, instead of manually configuring VLANs on every switch?** At small scale (this lab's 3 switches) manual configuration is trivial. At real campus scale (dozens to hundreds of switches), VTP turns "add a new VLAN" from a multi-hour, error-prone, per-device task into a single command on one Server. **Why does this lab deliberately include a Transparent-mode switch?** To demonstrate that VTP isn't all-or-nothing — a switch can participate in the trunk topology (forwarding VTP advertisements onward) while explicitly opting its own local VLAN database out of automatic changes, which is exactly the safety pattern many real production networks now use for *every* switch (VTP Transparent as the default, VLANs created deliberately per-switch) precisely because of the revision-number overwrite risk in Section 8, Mistake #1.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a network engineer plugs in what they think is a fresh switch, and it turns out to hold a stale VTP configuration from a previous job with a higher revision number in the same domain name — and the production VLAN database vanishes within seconds. This is a real, well-documented outage pattern, not a hypothetical.
- ...you're auditing a campus network and find every switch in VTP Transparent mode — that's not a mistake, it's a deliberate security posture many organizations now prefer over the operational convenience of Server/Client.
- ...you troubleshoot "the new VLAN works on some switches but not others" and the root cause turns out to be a domain name mismatch (often just a typo or case difference) silently blocking propagation to one branch of the topology.

---

## 12. Stretch Goal

1. Configure a VTP password on SW1 and confirm SW2/SW3 fail to synchronize until they're given the same password.
2. Deliberately create a "rogue switch" scenario: build a fourth switch with VTP Server mode, the same domain name, and a higher revision number than SW1, then connect it and observe what happens to SW1/SW2/SW3's VLAN databases. Document the outcome, then explain how a VTP password would have prevented it.
3. Convert the entire topology to VTP Transparent (or VTP off) and manually recreate VLANs 10/20/30/40 identically on every switch — compare the administrative overhead against the Server/Client model you just tore down.

---

## 13. Self-Assessment

- [ ] Can you state, from memory, what each of the three VTP modes can and cannot do to its local VLAN database?
- [ ] Can you explain why a Transparent-mode switch still forwards VTP advertisements it doesn't act on?
- [ ] Can you explain the VTP revision number overwrite risk and the one command that mitigates it?
- [ ] Can you explain the difference between `switchport mode trunk` and `switchport nonegotiate`, and why both matter together?
- [ ] Could you explain, to a non-technical manager, why an old lab switch is dangerous to plug into a live production network?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** VTP Server/Transparent/Client mode behavior, VTP domain and revision number, DTP and its risks, trunk port hardening, VLAN propagation vs. local port assignment.

**What I Learned:** VTP is powerful but dangerous if misunderstood. The Server creates and propagates VLANs, Transparent mode keeps VLANs local while still relaying advertisements onward, and Client mode receives VLANs but cannot create them. The key security takeaway: never leave a switch in VTP Server mode without a domain password — a rogue switch can overwrite an entire VLAN database if domain name and revision number align. DTP should be disabled on all trunk ports; leaving it on means a port could negotiate down to access mode if the other side is misconfigured, silently breaking VLAN traffic. Access ports should never negotiate trunks — manual `switchport mode access` plus DTP off guarantees the port stays in access mode regardless of what connects to it.

**Skills Practiced:** Trunk port configuration and verification, DTP disable with `switchport nonegotiate`, VTP Server/Transparent/Client mode configuration and behavior verification, VLAN database propagation rules, access port VLAN assignment, switchport mode verification via CLI, understanding VTP domain boundaries.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) — Open vSwitch does **not** support VTP at all, so this lab specifically requires a Cisco IOSvL2/vIOS-L2 substitute to actually demonstrate VTP mode behavior; the README explains the limitation and the alternative in detail.
