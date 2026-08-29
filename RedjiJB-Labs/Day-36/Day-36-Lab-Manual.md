# Day 36 Lab Manual — CDP & LLDP: Network Discovery Protocols

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Use CDP to document an unknown three-router, three-switch topology, then lock discovery protocols down: disable CDP on PC-facing access ports, disable CDP globally, and migrate to LLDP enabled only on inter-device links. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals: device discovery), Domain 5 (Security Fundamentals: reducing information leakage on access ports). |
| **Prerequisites** | Basic router/switch CLI navigation, interface addressing, `interface range` syntax. |
| **Time Estimate** | 60–75 minutes. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner–Intermediate) — commands are simple, but the four-phase workflow (discover → lock down access → lock down globally → re-enable selectively via LLDP) requires careful interface-by-interface reasoning. |

---

## 1. Lab Overview + Learning Objectives

This lab treats CDP and LLDP as what they really are: reconnaissance tools that are equally useful to you and to an attacker. You start with an undocumented triangle of three routers, each with its own access-layer switch and PC, and use CDP — on by default, no configuration required — to map the entire topology without touching a single running-config. Then you flip the posture: disable CDP everywhere it isn't needed, and replace it with LLDP, enabled only where it's actually useful (inter-device links), never on ports facing end-user devices.

By the end of this lab you will be able to:

- Use `show cdp neighbors [detail]` to build a topology map with zero prior documentation
- Explain why CDP is enabled globally and per-interface by default, and why that default is a liability on access ports
- Disable CDP surgically (`no cdp enable` per-interface) versus globally (`no cdp run`)
- Enable LLDP globally and understand why, unlike CDP, it requires explicit per-interface `lldp transmit`/`lldp receive`
- Explain the CDP-vs-LLDP tradeoff (proprietary + more detail vs. open standard + less information leakage)
- Verify a discovery protocol's on/off state precisely, per interface, using `show run` and protocol-specific `show` commands

---

## 2. Business Context

**Why would a real company do this?**

- **"We inherited this network with zero documentation — map it before we touch anything."** This is the single most common real use of CDP/LLDP: a new engineer, an acquired site, or a network that predates any current employee. `show cdp neighbors detail` across every device is often the fastest way to reconstruct an accurate topology diagram from scratch.
- **"Our last security audit flagged that our switches leak hostname, IOS version, and VLAN info to anyone who plugs a laptop into a wall jack."** CDP information is exactly what a would-be attacker wants during network reconnaissance — device models feed CVE lookups, VLAN/native VLAN info feeds VLAN-hopping attempts. Disabling CDP on access ports (Phase 2) is a standard hardening checklist item.
- **"We're merging in a non-Cisco vendor's switches and need a discovery protocol that works across both."** CDP is Cisco-only; LLDP (IEEE 802.1AB) is the interoperable answer, which is exactly why Phase 4 migrates the topology to LLDP.
- **"We want ongoing neighbor visibility for monitoring, but with the smallest possible information footprint."** LLDP's default-off, opt-in-per-interface posture (Phase 4) combined with restricting Tx/Rx to inter-device links only is the industry-standard "least information leaked, most operational visibility retained" compromise.

---

## 3. Topology Reference

Three routers in a triangle (R1–R2, R1–R3, R2–R3), each router also connected to its own access switch, each switch connected to one PC. The interfaces and neighbor relationships below were reconstructed using CDP in Phase 1 — that reconstruction *is* the first lab task.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP.png" alt="Day 36 CDP and LLDP Topology" width="900">
</p>

| Device | Type | Interfaces | Neighbors |
|---|---|---|---|
| R1 | Router | G0/0, G0/1, G0/2 | R2 (G0/1), R3 (G0/0), SW1 (G0/2) |
| R2 | Router | G0/0, G0/2 | R1 (G0/0), R3 (S0/0/0), SW2 (G0/2) |
| R3 | Router | G0/0, G0/1, G0/2 | R1 (G0/1), R2 (G0/0), SW3 (G0/0) |
| SW1 | Switch | G0/1, G0/2 | R1 (G0/2), PC1 (Fa0/1) |
| SW2 | Switch | G0/1, G0/2 | R2 (G0/2), PC2 (Fa0/1) |
| SW3 | Switch | G0/1, G0/2 | R3 (G0/0), PC3 (Fa0/1) |

This lab has no IP addressing plan of its own — it assumes the routers/switches are already addressed and reachable (or, for a pure discovery-protocol exercise, addressing is irrelevant since CDP/LLDP operate at Layer 2 regardless of IP configuration).

---

## 4. Pre-Configuration Checklist

1. Confirm all six devices (R1–R3, SW1–SW3) and three PCs are physically cabled per the topology above, with interfaces administratively up (`no shutdown`).
2. Do **not** pre-document the topology from a diagram — the point of Phase 1 is to derive it live from CDP output, which is the actual skill being practiced.
3. Confirm you can distinguish, before starting, which interfaces on each switch face a router (uplink) versus a PC (access) — Phases 2 and 4 both depend on getting this distinction right per-interface.

---

## 5. Configuration Tasks

### 5.1 Phase 1 — Document the network with CDP

CDP is enabled by default, globally and per-interface, on every Cisco IOS device — no configuration is required to use it for discovery.

```cisco
R2#show cdp
R2#show cdp neighbors
R2#show cdp neighbors detail
R2#show cdp interface
```

- **Mode:** Privileged EXEC (`show` commands, no configuration needed).
- **`show cdp neighbors`** — the workhorse discovery command. Output columns: Device ID (neighbor hostname), Local Intrf (your interface facing them), Hold-time, Capability (R=Router, S=Switch, H=Host, etc.), Platform (hardware model), Port ID (their interface facing you).
- **`show cdp neighbors detail`** — adds IP address, native VLAN, duplex, and IOS version per neighbor. This is the single most information-dense discovery command in IOS — reach for it first during any undocumented-network audit.
- **Memory aid:** "CDP tells you two interfaces for every cable: mine and theirs" — Local Intrf is always your own interface, Port ID is always the neighbor's.

**R2's neighbor table:**
```
Device ID   Local Intrf   Hold-time   Capability   Platform   Port ID
R1          Gig0/0        120         R            2911       Gig0/1
```

**R3's neighbor table:**
```
Device ID   Local Intrf   Hold-time   Capability   Platform   Port ID
R1          Gig0/1        120         R            2911       Gig0/2
R2          Gig0/2        120         R            2911       Gig0/0
```

Cross-referencing R2's and R3's tables against each other (R2 sees R1 on G0/0↔G0/1; R3 sees R1 on G0/1↔G0/2 and R2 on G0/2↔G0/0) is exactly how the full topology table in Section 3 gets built without ever opening a pre-existing diagram.

**CDP timers:** advertisement interval 60 seconds; hold-time 180 seconds default (an entry is purged if no CDP frame arrives within the hold-time). CDP frames are sent to the multicast MAC `01:00:0C:CC:CC:CC` — a non-routable, link-local destination, which is why CDP only ever discovers *directly* connected neighbors, never anything beyond one hop.

### 5.2 Phase 2 — Disable CDP on PC-facing switch ports

**Why?** CDP information (hostname, IOS version, model, VLAN) handed to a PC port is handed to whoever plugs into that jack — a legitimate laptop, or an attacker's. Since the switch has no way to distinguish the two, the fix is to stop advertising to access ports entirely.

```cisco
SW1(config)#interface range fastethernet 0/1
SW1(config-if-range)#no cdp enable

SW2(config)#interface range fastethernet 0/1
SW2(config-if-range)#no cdp enable

SW3(config)#interface range fastethernet 0/1
SW3(config-if-range)#no cdp enable
```

- **Mode:** Interface (range) configuration.
- **`no cdp enable`** — disables CDP on this specific interface only. CDP remains fully active on every other interface (notably the router-facing uplink), and remains active globally on the switch.
- **Memory aid:** "`no cdp enable` is a scalpel, `no cdp run` (Phase 3) is the whole limb" — one is per-interface, one is global.
- **Why `interface range` here even for one interface?** Habit/consistency — if a switch had multiple PC ports (Fa0/1–Fa0/24 in a real deployment), the exact same command with a wider range would disable CDP on all of them in one shot; using `interface range` even for a single port keeps the syntax identical to the real-world multi-port case.

### 5.3 Phase 3 — Disable CDP globally

```cisco
R1(config)#no cdp run
R2(config)#no cdp run
R3(config)#no cdp run
SW1(config)#no cdp run
SW2(config)#no cdp run
SW3(config)#no cdp run
```

- **Mode:** Global configuration.
- **`no cdp run`** — turns CDP off entirely on the device: no advertisements sent or received, on any interface, regardless of any per-interface `cdp enable` state. This is the "we don't use CDP at all, anywhere, on this box" switch.
- **Memory aid:** "`run` is the whole engine — turn off `cdp run`, nothing CDP-related happens anywhere on the device."
- **Why do this at all, if Phase 2 already secured the access ports?** Defense in depth, and because CDP information on the *inter-device* links (router-to-router, router-to-switch) is still being transmitted at this point — visible to anyone who can tap those links. Phase 3 removes that exposure entirely, in preparation for replacing it with LLDP (Phase 4), which leaks less information by design.

### 5.4 Phase 4 — Enable LLDP globally, then Tx/Rx only on inter-device links

```cisco
R1(config)#lldp run
R2(config)#lldp run
R3(config)#lldp run
SW1(config)#lldp run
SW2(config)#lldp run
SW3(config)#lldp run
```

- **`lldp run`** — the global LLDP enable. Unlike CDP, LLDP ships **off** by default — this command is mandatory, not optional, before any LLDP advertisement happens anywhere on the device.

```cisco
R1(config)#interface range g0/0-2
R1(config-if-range)#lldp transmit
R1(config-if-range)#lldp receive

R2(config)#interface range g0/0-2
R2(config-if-range)#lldp transmit
R2(config-if-range)#lldp receive

R3(config)#interface range g0/0-2
R3(config-if-range)#lldp transmit
R3(config-if-range)#lldp receive

SW1(config)#interface g0/2
SW1(config-if)#lldp transmit
SW1(config-if)#lldp receive

SW2(config)#interface g0/2
SW2(config-if)#lldp transmit
SW2(config-if)#lldp receive

SW3(config)#interface g0/1
SW3(config-if)#lldp transmit
SW3(config-if)#lldp receive
```

- **`lldp transmit` / `lldp receive`** — unlike CDP's single `cdp enable` toggle, LLDP splits transmit and receive into two independent switches. Both must be on for full bidirectional discovery; if only `transmit` is set, your device advertises itself but can't see anyone else's advertisements, and vice versa.
- **Why `interface range g0/0-2` on the routers but a single interface on each switch?** Every router interface in this topology faces another network device (router or switch) — the full range is appropriate. Each switch has exactly one uplink facing a router and one access port facing a PC; only the uplink gets LLDP, exactly mirroring the Phase 2 logic (never advertise device info to a PC port).
- **Memory aid:** "LLDP is opt-in twice — once globally (`lldp run`), once per direction per interface (`transmit`/`receive`)." CDP's default-on-everywhere posture is the opposite of LLDP's default-off-everywhere posture — this is the single most important conceptual difference to retain.

---

## 6. Verification Steps

| Command | What to check |
|---|---|
| `show cdp neighbors [detail]` | Confirms discovered topology during Phase 1; confirms CDP is fully disabled after Phase 3 |
| `show cdp interface` | Confirms per-interface CDP state after Phase 2 (PC ports show "CDP is disabled") |
| `show run \| section interface <if>` | Confirms exact `no cdp enable` / `lldp transmit`/`receive` state per interface |
| `show lldp` | Confirms LLDP is globally active and shows its timers |
| `show lldp neighbors [detail]` | Confirms LLDP is discovering the same inter-device topology as CDP originally did |
| `show lldp interface` | Confirms Tx/Rx state per interface |

### 6.1 Expected Output Gallery

**`SW1#show cdp interface`** (after Phase 2)
```
GigabitEthernet0/2 is up, line protocol is up
  Sending CDP packets every 60 seconds
  Hold-time is 180 seconds
FastEthernet0/1 is up, line protocol is up
  CDP is disabled
```

**`R1#show cdp` / `show cdp neighbors`** (after Phase 3)
```
R1#show cdp
% CDP is not enabled

R1#show cdp neighbors
% CDP is not enabled
```

**`R3#show lldp neighbors`** (after Phase 4)
```
Capability codes:
(R) Router, (B) Bridge, (T) Telephone, (P) Repeater,
(S) Station, (O) Other, (C) DOCSIS Cable Device, (E) WLAN

Device ID   Local Intrf   Hold-time   Capability   Port ID
R1          Gig0/1        120         R            Gig0/2
R2          Gig0/2        120         R            Gig0/0
Total entries displayed: 2
```

**`R1#show lldp`**
```
Global LLDP Information:
  Status: ACTIVE
  LLDP advertisements are sent every 30 seconds
  LLDP hold time advertised is 120 seconds
  LLDP interface reinitialisation delay is 2 seconds
```

**`SW2#show run | s 0/1`** (confirms PC port never got LLDP either)
```
interface FastEthernet0/1
 no lldp receive
 no lldp transmit
 no cdp enable
```

---

## 7. Common Mistakes (the 80/20)

1. **Forgetting `lldp run` before configuring per-interface `transmit`/`receive`.** Without the global enable, per-interface LLDP commands have no effect — always set the global switch first.
2. **Assuming LLDP defaults match CDP's defaults.** CDP is on everywhere by default; LLDP is off everywhere by default. Muscle memory from CDP ("it just works") leads to skipping the required LLDP enable steps.
3. **Enabling LLDP Tx/Rx on PC-facing ports "just to be safe."** This defeats the entire point of Phase 4 — LLDP on an access port leaks exactly the same class of information CDP did, just via a different protocol.
4. **Using `no cdp run` (global) when only one port needed to be quiet, or `no cdp enable` (per-interface) on every port instead of the global switch when the goal was to disable CDP everywhere.** Match the scope of the command to the scope of the requirement.
5. **Forgetting that `no cdp run` doesn't touch LLDP, and `lldp run` doesn't touch CDP.** They are entirely independent features; disabling one has zero effect on the other's state.
6. **Trying to use non-contiguous `interface range` syntax (e.g., mixing Gig and Fast interfaces in one range command).** Range syntax requires the same interface type and contiguous numbering; non-contiguous sets require separate `interface range` commands.

---

## 8. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | `show cdp neighbors` returns nothing on a device that should see neighbors | CDP disabled globally (`no cdp run`) or not yet configured on this specific device | `show cdp` | `cdp run` (re-enable) if discovery is still needed |
| 2 | One specific neighbor missing from `show cdp neighbors` | `no cdp enable` was applied to that one interface (Phase 2 leaking into a link that should still have CDP) | `show cdp interface` | Re-enable with `cdp enable` on the correct interface only |
| 3 | `show lldp neighbors` is empty even after configuring `lldp transmit`/`receive` | `lldp run` was never issued globally | `show lldp` | Issue `lldp run`, then re-check |
| 4 | LLDP neighbor seen in one direction only, or not at all despite correct global config | Only `lldp transmit` or only `lldp receive` was set, not both | `show lldp interface` | Add the missing direction |
| 5 | PC-facing port still shows device info being leaked | Phase 2 or Phase 4's port-scoping was applied to the wrong interface number | `show run \| section interface <if>` | Correct the interface reference and reapply `no cdp enable` / leave LLDP off |

---

## 9. Design Analysis

- **Why discover with CDP first instead of going straight to LLDP?** CDP is on by default with zero configuration — it is the fastest possible way to map an unknown topology. LLDP would require enabling it everywhere first, which assumes you already know where "everywhere" is — a chicken-and-egg problem CDP's default-on posture neatly avoids.
- **Why disable CDP entirely (Phase 3) rather than just locking down access ports (Phase 2) and calling it done?** Phase 2 alone still leaks CDP information across every inter-device link to anyone who can tap those links (rare, but not impossible, e.g., a compromised switch or a rogue device plugged into what should be a router-only segment). Migrating fully to LLDP is the more complete security posture, and LLDP's default-off nature makes the resulting configuration self-documenting: every enabled interface was a deliberate choice, not a leftover default.
- **Why not just leave CDP on everywhere since it's "only internal"?** "Internal" doesn't mean "trusted" — a compromised endpoint, a rogue device on an access port, or an unauthorized laptop are exactly the threat model discovery-protocol hardening defends against. Treating every access port as untrusted by default is standard least-privilege thinking, the same posture explored in this course's ACL labs (Days 33–35).

---

## 10. Real-World Parallel

**You'd see this when...**

- ...onboarding into a new team and being handed a network with no accurate diagram — CDP/LLDP audit is often literally step one.
- ...a compliance or security audit specifically calls out "discovery protocols enabled on user-facing ports" as a finding that must be remediated (this is a common item on hardening checklists like CIS Benchmarks for network devices).
- ...planning a multi-vendor merger or acquisition integration, where CDP simply won't discover the acquired company's non-Cisco gear and LLDP becomes mandatory.

---

## 11. Stretch Goal

1. Write the exact `show run | section interface <if>` output you'd expect to see on R1's G0/2 (facing SW1) after all four phases are complete, and justify each line.
2. SW1, SW2, and SW3 in this lab only ever get LLDP enabled on their single uplink. Extend the topology mentally: if SW1 gained a second uplink to a redundant router, would you enable LLDP Tx/Rx on that link too? Why?
3. Research `show cdp entry <device-name>` versus `show cdp neighbors detail` — what's the practical difference, and when would you reach for one over the other during a live audit?

---

## 12. Self-Assessment

- [ ] Can you explain from memory why CDP defaults to "on everywhere" while LLDP defaults to "off everywhere"?
- [ ] Can you state the difference between `no cdp enable` and `no cdp run` without looking it up?
- [ ] Can you explain why `lldp transmit` and `lldp receive` are separate commands, and what happens if only one is configured?
- [ ] Given an unfamiliar topology, could you reconstruct an accurate neighbor map using only `show cdp neighbors detail` output from each device?
- [ ] Can you justify, in security terms, why PC-facing ports should never run CDP or LLDP?

---

## 13. Key Concepts Demonstrated

- CDP-based topology discovery on a fully undocumented network
- Per-interface vs. global protocol disable (`no cdp enable` vs `no cdp run`)
- LLDP's default-off, explicit-opt-in-per-interface model (`lldp run` + `transmit`/`receive`)
- CDP vs LLDP: proprietary/detailed vs. open-standard/minimal-leakage
- Security-driven interface scoping: discovery protocols on inter-device links only, never on access ports

## 14. What I Learned

CDP and LLDP are simultaneously the most useful and the most dangerous "free" features on a Cisco device — useful for legitimate discovery and documentation, dangerous because they broadcast device identity to whatever's plugged into a port, trusted or not. The defaults matter as much as the commands: CDP's on-by-default posture makes it a great first-pass discovery tool but a liability left running; LLDP's off-by-default posture makes it the safer long-term choice precisely because every enabled interface is a conscious decision, not an inherited default. The four-phase workflow in this lab — discover, lock down access, lock down globally, re-enable selectively via the safer protocol — is a pattern that generalizes well beyond discovery protocols to any "feature on by default that leaks information" situation.

## 15. Skills Practiced

- CDP neighbor-table interpretation and topology reconstruction
- Per-interface and global protocol enable/disable syntax (CDP and LLDP)
- `interface range` usage for bulk interface configuration
- Verification via multiple `show` commands cross-referenced against expected state
- Security-driven interface scoping decisions

---

## 16. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for a script that builds this lab's six-device triangle topology (three routers, three switches, three PCs) using VyOS routers, Open vSwitch switches, and Alpine Linux end hosts, along with the LLDP-equivalent configuration mapping (VyOS doesn't run Cisco CDP, so the GNS3 build focuses on LLDP, which VyOS supports natively).
