# Day 17 Lab Manual — VLANs Part 2: Troubleshooting and Verification

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Diagnose and fix a multi-switch VLAN/trunk topology with deliberately introduced faults — a missing/incorrect trunk allowed-VLAN list, a native VLAN mismatch, and a broken router-on-a-stick subinterface — using only `show` commands, then verify end-to-end inter-VLAN connectivity. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): VLANs, trunking, 802.1Q. Domain 2 (Network Access): configure/verify VLANs, trunking, and Layer 2/3 connectivity including router-on-a-stick. Domain 5 (Security Fundamentals, tangential): native VLAN as a hardening concern. |
| **Prerequisites** | Day 16 (VLANs Part 1 — VLAN creation, access ports, IP addressing plan) completed. Comfortable with `switchport mode access/trunk`, subinterfaces, and basic `show` command syntax. |
| **Time Estimate** | 2 – 2.5 hours (first attempt); 30–40 minutes on repeat/review. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the configuration itself is short; the difficulty is entirely in diagnosing symptoms (mismatched native VLANs, an incomplete allowed list, a down subinterface) from `show` output alone, without being told what's broken. |

---

## 1. Lab Overview

Day 16 built the VLAN structure — three VLANs (Engineering, Sales, HR), access ports assigned, and an IP addressing plan reused unchanged in this lab. Day 17 is about what happens **between** switches and **up to** the router once VLANs exist: trunks, allowed-VLAN lists, native VLAN agreement, and router-on-a-stick subinterfaces — and, critically, what it looks like when any one of those pieces is wrong.

This lab is deliberately troubleshooting-first. Rather than configuring a clean topology from a blank slate, you will bring up trunking between two switches and a router-on-a-stick, then work through — and deliberately reproduce — three realistic fault conditions that show up constantly in real switched networks:

1. A trunk that is technically "up" but is silently dropping one or more VLANs because the allowed-VLAN list is incomplete.
2. A **native VLAN mismatch** between two ends of a trunk — a fault that does *not* bring the trunk down, which is exactly why it's dangerous.
3. A router-on-a-stick subinterface that is administratively fine but can't ping across VLANs because of a subinterface-specific misconfiguration (missing `encapsulation dot1Q`, mismatched VLAN tag, or the subinterface simply down).

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Verify access port VLAN assignment and trunk state using `show vlan brief` and `show interfaces trunk`
- Explain what a trunk allowed-VLAN list does and diagnose when a VLAN is silently excluded from it
- Recognize a native VLAN mismatch from CDP console messages and `show interfaces trunk` output, and explain why the trunk stays up despite the mismatch
- Configure and verify router-on-a-stick subinterfaces (802.1Q encapsulation, per-VLAN IP addressing)
- Follow a **sequential diagnostic methodology** — Layer 1 → access port → trunk → allowed list → native VLAN → subinterface — rather than guessing at fixes
- Read `show` command output critically enough to tell "configured" apart from "actually working"

---

## 2. Business Context

**Why would a real company run into this?**

By the time a company has three departments on three VLANs (Day 16's build), it almost never has all three departments plugged into a single switch. Engineering, Sales, and HR sit on different floors or different switches, and everything meets at a router (or Layer 3 switch) for inter-VLAN routing. That means trunks — and trunks are where a disproportionate share of real-world "some people can't reach some things" tickets originate:

- **"Sales can reach the printer but HR can't, and both are on the same trunk"** → this is almost always an incomplete trunk allowed-VLAN list. Someone added VLAN 10 and 20 to the trunk during a project and forgot VLAN 30 existed, because the omission produces *no error* — the trunk stays up, everything looks fine in `show interfaces trunk | include line protocol`, and only the missing VLAN's traffic silently vanishes.
- **"CDP is throwing a warning but nothing seems broken"** → a native VLAN mismatch is the textbook example of a fault that doesn't cause an outage on day one but is a landmine for later: traffic tagged for the native VLAN on one switch is treated as untagged and delivered to the *wrong* VLAN on the other switch, which under the right conditions is a VLAN-hopping security exposure, not just a cosmetic warning.
- **"We added a new department and inter-VLAN routing doesn't work for them"** → router-on-a-stick requires a subinterface per VLAN, and every subinterface independently needs `encapsulation dot1Q <vlan-id>` plus the correct IP — forgetting either on the newest VLAN is one of the most common "we rolled out VLAN 40 and it just doesn't route" incidents in small-to-mid enterprises still running router-on-a-stick instead of a Layer 3 switch with SVIs.
- **"How do we even know where to look first?"** → this is why every serious network team works troubleshooting *top-down or bottom-up*, never randomly. This lab's Section 9 (Troubleshooting Guide) models the bottom-up sequence — physical, then access port, then trunk, then allowed list, then native VLAN, then Layer 3 subinterface — the same order a competent engineer works a live outage in, instead of jumping straight to "let me just reconfigure everything."

This is the kind of lab you'd be handed in your first few months on a helpdesk-to-network-engineer track: the VLANs already exist, something in the plumbing between them is broken, and your job is to find exactly which layer failed without touching anything that already works.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2017%20Lab%20-%20VLANs%20(Part%202).png" alt="Day 17 Network Topology - VLANs 10, 20, 30" width="900">
</p>

### 3.1 Traffic Flow Summary

```text
SW1 (trunk to R1, trunk to SW2)
SW2 -- PC2, PC3 (VLAN 10 - Engineering)
SW2 -- PC5 (VLAN 20 - Sales)
SW2 -- PC4 (VLAN 30 - HR)
SW2 == trunk (Gi0/1, Gi0/2) == SW1
SW1 == trunk (Gi0/1) == R1 (router-on-a-stick, subinterfaces .10/.20/.30)
```

### 3.2 Equipment List

| Device | Model | Role |
|---|---|---|
| `SW1` | Cisco 2960-24TT | Distribution switch — trunks to SW2 and to R1 |
| `SW2` | Cisco 2960-24TT | Access switch — PC2/PC3 (VLAN 10), PC5 (VLAN 20), PC4 (VLAN 30) |
| `R1` | Cisco 2911 | Router-on-a-stick — one physical interface, three 802.1Q subinterfaces |
| `PC2`, `PC3` | Generic PC | VLAN 10 — Engineering |
| `PC4` | Generic PC | VLAN 30 — HR |
| `PC5` | Generic PC | VLAN 20 — Sales |

> **Note:** This lab reuses SW2's access-port assignments and IP addressing exactly as built in Day 16 — nothing about the access-layer VLAN membership changes here. What's new in Day 17 is everything above the access port: the SW1↔SW2 and SW1↔R1 trunks, and R1's router-on-a-stick configuration.

---

## 4. IP Addressing Plan

This lab has **no addressing of its own** — it reuses the exact VLAN-to-subnet scheme built in **Day 16's IP Addressing Plan** unchanged. Reproduced here for reference only (do not recalculate; this is Day 16's math, not new work):

| VLAN | Name | Subnet | Usable Range | Devices |
|---|---|---|---|---|
| 10 | Engineering | `10.0.0.0/26` | .1 – .62 | PC2, PC3 |
| 20 | Sales | `10.0.0.64/26` | .65 – .126 | PC5 |
| 30 | HR | `10.0.0.128/26` | .129 – .190 | PC4 |

R1's router-on-a-stick subinterfaces take the **first usable address** of each VLAN's block as the default gateway for that VLAN (`10.0.0.1`, `10.0.0.65`, `10.0.0.129` — see Section 6.3). If you need the host-bit math, block-size derivation, or binary walkthrough behind these `/26` boundaries, that work belongs to Day 16's manual, Section 4 — go there rather than re-deriving it here.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Confirm Day 16's build is intact: SW2's access ports are already assigned to VLANs 10/20/30, and PCs already have their Day 16 IP configuration.
2. Cable SW1 Gi0/1 ↔ SW2 Gi0/1, SW1 Gi0/2 ↔ SW2 Gi0/2 (redundant link between switches, both used per the allowed-list config below), and SW1 Gi0/1 (or a separate uplink port) ↔ R1's single physical interface.
3. Confirm interface numbering — this manual uses `GigabitEthernet0/1`/`0/2` on the switches and `GigabitEthernet0/0` (with subinterfaces `.10`/`.20`/`.30`) on R1; substitute if your platform differs.
4. Have Section 4's VLAN/subnet table and Section 6's fault-injection steps open for reference — this lab is meant to be worked with faults introduced on purpose, not avoided.

---

## 6. Configuration Tasks — Diagnostic CLI Walkthrough

This section builds the trunk/router-on-a-stick layer from scratch, then walks through **three deliberately introduced faults** (mirroring what the original lab's screenshots actually captured happening) so you practice recognizing and fixing each one instead of only building a topology that works on the first try.

### 6.1 SW1 — Baseline Trunk Configuration

**Step 1: Confirm current trunk state before changing anything**

```text
SW1#show interfaces trunk
```

- **Mode:** Privileged EXEC (this is a `show`, not a config command — always establish a baseline before you touch anything).
- **What it does:** Lists every interface currently operating as a trunk, its encapsulation, native VLAN, and which VLANs are allowed/active.
- **Why first:** You cannot tell whether your changes *caused* a problem if you never captured what "before" looked like. This single habit — baseline, then change, then re-verify — is the difference between confident troubleshooting and guessing.
- **Memory aid:** "Show before you go" — always run the relevant `show` command immediately before and immediately after any change.

**Step 2: Configure the trunk toward SW2**

```text
SW1(config)#interface gigabitEthernet 0/1
SW1(config-if)#switchport mode trunk
SW1(config-if)#switchport trunk allowed vlan 10,20,30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

> `switchport mode trunk` forces 802.1Q trunking rather than negotiating it (Cisco's default DTP behavior is a security concern — always hard-set trunk mode explicitly in production and in this lab). `switchport trunk allowed vlan 10,20,30` is the **allowed-VLAN list** — by default a new trunk allows *all* VLANs (1–4094), but explicitly listing only the VLANs that should traverse this link is best practice: it prevents unrelated broadcast traffic from crossing links that don't need it, and it's the exact knob this lab's fault scenarios revolve around.

**Step 3: Configure the trunk toward R1**

```text
SW1(config)#interface gigabitEthernet 0/2
SW1(config-if)#switchport mode trunk
SW1(config-if)#switchport trunk allowed vlan 10,20,30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

> R1's router-on-a-stick subinterfaces need to see all three VLANs tagged on this single physical trunk — without VLAN 30 in this link's allowed list, HR would never be able to route anywhere, even though its access port and switch-to-switch trunk are both fine.

### 6.2 SW2 — Trunk Configuration Toward SW1

```text
SW2(config)#interface gigabitEthernet 0/1
SW2(config-if)#switchport mode trunk
SW2(config-if)#switchport trunk allowed vlan add 10
SW2(config-if)#switchport trunk allowed vlan add 20
SW2(config-if)#no shutdown
SW2(config-if)#exit
SW2(config)#interface gigabitEthernet 0/2
SW2(config-if)#switchport mode trunk
SW2(config-if)#switchport trunk allowed vlan add 10
SW2(config-if)#switchport trunk allowed vlan add 20
SW2(config-if)#switchport trunk allowed vlan add 30
SW2(config-if)#no shutdown
SW2(config-if)#exit
```

> Note the deliberate difference between these two links: `add` appends to the allowed list instead of replacing it (useful when building the list incrementally, but also the single easiest way to accidentally end up with two trunk ports carrying *different* VLAN sets when you meant them to match). **Gi0/1 only carries VLANs 10 and 20 — VLAN 30 (HR) is missing on purpose.** This is Fault #1, built into the baseline configuration so you diagnose it in Section 6.4 rather than starting from a fully-working state.

### 6.3 R1 — Router-on-a-Stick Subinterfaces

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/0.10
R1(config-subif)#encapsulation dot1Q 10
R1(config-subif)#ip address 10.0.0.1 255.255.255.192
R1(config-subif)#exit
R1(config)#interface gigabitEthernet 0/0.20
R1(config-subif)#encapsulation dot1Q 20
R1(config-subif)#ip address 10.0.0.65 255.255.255.192
R1(config-subif)#exit
R1(config)#interface gigabitEthernet 0/0.30
R1(config-subif)#encapsulation dot1Q 30
R1(config-subif)#ip address 10.0.0.129 255.255.255.192
R1(config-subif)#exit
```

> The **physical** interface (`Gi0/0`) carries no IP of its own in router-on-a-stick — it only needs `no shutdown`, because all Layer 3 work happens on the subinterfaces. `encapsulation dot1Q <vlan-id>` is what ties a subinterface to a specific VLAN tag; without it, the subinterface exists but drops every frame, because it has no idea which VLAN's traffic belongs to it. This is the single most-forgotten command in router-on-a-stick labs — a subinterface with an IP address but no `encapsulation dot1Q` line will show `up/up` in `show ip interface brief` and still fail every ping, which is exactly why Fault #3 below targets this line specifically.
>
> **Memory aid:** subinterface number and VLAN ID *look* related (`Gi0/0.10` ↔ VLAN 10) but Cisco IOS does not enforce that connection automatically — the subinterface number is just a locally significant label. The `encapsulation dot1Q 10` line is what actually makes the binding to VLAN 10; you could technically name the subinterface `Gi0/0.999` and encapsulate VLAN 10 on it and it would still work, but matching the numbers is a readability convention every real engineer follows anyway.

### 6.4 Fault #1 — Incomplete Trunk Allowed List (Diagnose and Fix)

**Symptom to notice:** PC4 (HR, VLAN 30) cannot reach its default gateway (`10.0.0.129`) even though its access port, IP configuration, and R1's subinterface all check out individually.

**Diagnose:**

```text
SW2#show interfaces trunk
```

```text
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1
Gi0/2       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       10,20
Gi0/2       10,20,30
```

> Compare the two `Vlans allowed on trunk` rows side by side — `Gi0/2` carries all three VLANs, but `Gi0/1` (SW2's trunk toward SW1) is missing `30`. The trunk is `trunking` (technically healthy at Layer 2 negotiation) and would give zero indication anything is wrong unless you specifically read the allowed-VLAN column — this is exactly why "the trunk shows up" is not the same question as "does this trunk carry the VLAN I need."

**Fix:**

```text
SW2(config)#interface gigabitEthernet 0/1
SW2(config-if)#switchport trunk allowed vlan add 30
SW2(config-if)#exit
```

> `add` here is deliberate — using `switchport trunk allowed vlan 30` instead (without `add`) would *replace* the entire list with just `30`, silently dropping VLANs 10 and 20 from this trunk and creating a brand-new outage while fixing the old one. This distinction is worth memorizing on its own.

### 6.5 Fault #2 — Native VLAN Mismatch (Diagnose and Fix)

**Symptom to notice:** A console message appears without you changing anything that should have caused it, and something about inter-switch traffic seems subtly wrong (in production, this often shows up as CDP/STP inconsistency warnings or, worse, VLAN leakage — in this lab, focus on recognizing and correcting the message itself).

**Fault, introduced deliberately for practice:**

```text
SW1(config)#interface gigabitEthernet 0/1
SW1(config-if)#switchport trunk native vlan 1001
SW1(config-if)#exit
```

**Diagnose:**

```text
%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1001), with SW2 GigabitEthernet0/1 (1)
```

```text
SW1#show interfaces trunk
```

```text
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1001
```

> **This is the core lesson of Fault #2: the trunk stays `trunking`.** A native VLAN mismatch is not a link-down event — untagged/native traffic on one side is simply delivered into whatever VLAN the *other* side considers native, silently. CDP is the only reason you found out at all; if CDP were disabled (common in hardened production networks, since CDP itself leaks topology information to anyone listening), this mismatch would produce no warning whatsoever and you'd only discover it through symptomatic troubleshooting — one more reason the diagnostic habit in Section 9 matters more than memorizing this one message.

**Fix:**

```text
SW1(config)#interface gigabitEthernet 0/1
SW1(config-if)#switchport trunk native vlan 1
SW1(config-if)#exit
```

> Set both ends to agree — VLAN 1 is IOS's default native VLAN and what SW2 is already using. (In a hardened production network you would instead move the native VLAN on *both* ends to an unused VLAN ID as a defense against VLAN-hopping attacks — noted in Section 10, not required for this lab's baseline fix.)

### 6.6 Fault #3 — Broken Router-on-a-Stick Subinterface (Diagnose and Fix)

**Symptom to notice:** PC4 can reach its own gateway `10.0.0.129` (Layer 2/local path fine) but cannot reach PC2 or PC5 in other VLANs — inter-VLAN routing for VLAN 30 specifically is broken while VLANs 10 and 20 route fine.

**Fault, introduced deliberately for practice:**

```text
R1(config)#interface gigabitEthernet 0/0.30
R1(config-subif)#no encapsulation dot1Q 30
R1(config-subif)#exit
```

**Diagnose:**

```text
R1#show ip interface brief
```

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES manual up                    up
GigabitEthernet0/0.10      10.0.0.1        YES manual up                    up
GigabitEthernet0/0.20      10.0.0.65       YES manual up                    up
GigabitEthernet0/0.30      10.0.0.129      YES manual up                    up
```

> This is the trap: `show ip interface brief` shows `up/up` for `Gi0/0.30` — the subinterface is administratively fine and has an IP. This alone tells you almost nothing is wrong. Dig one level deeper:

```text
R1#show interfaces gigabitEthernet 0/0.30
```

```text
GigabitEthernet0/0.30 is up, line protocol is up
  Hardware is CNGigabitEthernet, address is 0090.2140.5401 (bia 0090.2140.5401)
  Internet address is 10.0.0.129/26
  ARP type: ARPA, ARP Timeout 04:00:00
```

> Notice there's no `802.1Q Virtual LAN, Vlan ID 30` line here — that line only appears when `encapsulation dot1Q 30` is actually configured. Its absence, not any error message, is the fingerprint of this fault. Without it, the subinterface can't tell which tagged frames belong to it, so it silently drops all VLAN 30 traffic while still reporting `up/up` for its own administrative and IP state.

**Fix:**

```text
R1(config)#interface gigabitEthernet 0/0.30
R1(config-subif)#encapsulation dot1Q 30
R1(config-subif)#exit
```

**Re-verify:**

```text
R1#show interfaces gigabitEthernet 0/0.30
```

```text
GigabitEthernet0/0.30 is up, line protocol is up
  Hardware is CNGigabitEthernet, address is 0090.2140.5401 (bia 0090.2140.5401)
  Internet address is 10.0.0.129/26
  MTU 1500 bytes, ...
  Encapsulation 802.1Q Virtual LAN, Vlan ID 30, loopback not set
```

---

## 7. Verification Steps

### 7.1 Verification Command Table

| Device | Command | What to check |
|---|---|---|
| SW1, SW2 | `show interfaces trunk` | Both ends `trunking`, matching native VLAN, matching (or intentionally scoped) allowed-VLAN lists |
| SW1, SW2 | `show vlan brief` | Access ports still mapped to VLANs 10/20/30 as Day 16 left them |
| SW2 | `show interfaces status` | All access + trunk ports `connected`, not `err-disabled` |
| R1 | `show ip interface brief` | All three subinterfaces `up/up` with correct IPs |
| R1 | `show interfaces gi0/0.10` (and `.20`, `.30`) | `Encapsulation 802.1Q Virtual LAN, Vlan ID <n>` line present for every subinterface |
| R1 | `show cdp neighbors detail` | Confirms adjacency to SW1 and that native VLAN mismatch (if reintroduced) surfaces here too |
| PCs | `ping <gateway>` then `ping <cross-VLAN host>` | Local gateway reachable first, then cross-VLAN reachability |

### 7.2 Expected Output Gallery

**`SW1# show interfaces trunk`** (fully fixed state)

```text
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1
Gi0/2       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       10,20,30
Gi0/2       10,20,30

Port        Vlans allowed and active in management domain
Gi0/1       10,20,30
Gi0/2       10,20,30

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       10,20,30
Gi0/2       10,20,30
```

Both native VLANs read `1`, both allowed-VLAN lists read `10,20,30` — this is the target state after Faults #1 and #2 are both fixed.

**`SW2# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1, Gi0/2
10   VLAN0010                         active    Fa0/2, Fa0/3
20   VLAN0020                         active    Fa0/1
30   VLAN0030                         active    Fa0/4
```

Access ports are unchanged from Day 16 — this lab never touched them, and this output confirms that.

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES manual up                    up
GigabitEthernet0/0.10      10.0.0.1        YES manual up                    up
GigabitEthernet0/0.20      10.0.0.65       YES manual up                    up
GigabitEthernet0/0.30      10.0.0.129      YES manual up                    up
```

**`PC4> ping 10.0.0.1`** (HR pinging Engineering's gateway, full path test after all fixes)

```text
Pinging 10.0.0.1 with 32 bytes of data:

Reply from 10.0.0.1: bytes=32 time=2ms TTL=254
Reply from 10.0.0.1: bytes=32 time=1ms TTL=254
Reply from 10.0.0.1: bytes=32 time=1ms TTL=254
Reply from 10.0.0.1: bytes=32 time=2ms TTL=254

Ping statistics for 10.0.0.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Four replies, 0% loss, from a VLAN 30 host to a VLAN 10 subinterface — this single ping proves the trunk allowed-lists, native VLAN agreement, and router-on-a-stick encapsulation are all correct end to end.

### 7.3 Reachability Matrix

| From | To | Expected Result | Why |
|---|---|---|---|
| PC4 (VLAN 30) | R1 Gi0/0.30 (10.0.0.129) | Success | Directly connected gateway via local access port |
| PC4 (VLAN 30) | PC2 (VLAN 10) | Success (after all fixes) | Trunk carries VLAN 30 end-to-end, router routes between subinterfaces |
| PC4 (VLAN 30) | PC2 (VLAN 10) | **Fail** (with Fault #1 present) | SW2 Gi0/1 trunk doesn't carry VLAN 30 — frames never reach SW1 |
| PC2 (VLAN 10) | PC5 (VLAN 20) | Success | Both VLANs present on every trunk link throughout this lab |
| PC5 (VLAN 20) | R1 Gi0/0.20 | Success | Directly connected gateway |
| SW1 | SW2 (CDP neighbor check) | Native VLAN mismatch warning | Only when Fault #2 is deliberately reintroduced (Section 6.5) |

---

## 8. Common Mistakes (the 80/20)

1. **Confusing "trunk is up" with "trunk carries the VLAN I need."** `show interfaces trunk` reporting `trunking` in the Status column tells you Layer 2 negotiation succeeded — it says nothing about whether a specific VLAN is in the allowed list. Always read the `Vlans allowed on trunk` section separately.
2. **Using `switchport trunk allowed vlan <list>` instead of `... add <list>` when building the list incrementally.** The first form *replaces* the entire allowed list; the second *appends*. Using the replace form a second time is the single fastest way to accidentally re-break a trunk you just fixed.
3. **Assuming a native VLAN mismatch brings the trunk down.** It doesn't. Students who don't see an obvious outage assume the mismatch "doesn't matter" — it does, it's just silent, which is precisely what makes it a real security/operational risk instead of a cosmetic one.
4. **Forgetting `encapsulation dot1Q <vlan-id>` on a new router-on-a-stick subinterface.** The subinterface will still show `up/up` with a valid IP — the missing encapsulation line is invisible in `show ip interface brief` and only shows up if you check `show interfaces <subif>` specifically.
5. **Mismatching the subinterface number and the VLAN ID it encapsulates**, e.g. naming it `Gi0/0.30` but writing `encapsulation dot1Q 20`. IOS allows this (the subinterface number is just a label), but it will silently misroute traffic and confuse the next engineer reading the config.
6. **Forgetting `no shutdown` on the physical trunk-facing interface itself**, not just the subinterfaces — a shut physical interface takes every subinterface down with it, which can look confusingly like three simultaneous subinterface faults instead of one physical one.
7. **Not re-checking access ports after touching trunks.** Since Day 17 builds directly on Day 16's access-port config, it's easy to assume access ports are fine and spend an hour debugging the trunk when the actual regression was an accidental `switchport mode trunk` typed on an access port.
8. **Troubleshooting top-down when the fault is at the bottom.** Jumping straight to "let me recheck the router config" before confirming Layer 1/2 (cabling, access port, trunk, allowed list) wastes time — Section 9's sequence exists specifically to prevent this.

---

## 9. Troubleshooting Guide

Work through these **in strict sequential order** — this lab is built around the idea that VLAN/trunk problems live at a specific layer, and skipping ahead wastes time. Each step assumes the previous one passed.

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC can't reach its own local gateway | Cabling, access port down, or wrong VLAN on the access port | `show interfaces status` | Verify cable/link light; correct `switchport access vlan <id>` |
| 2 | PC reaches its own gateway but no other local-VLAN host | Access port assigned to wrong VLAN, or PC IP misconfigured | `show vlan brief` | Reassign port to correct VLAN; fix PC IP config |
| 3 | Trunk interface won't come up at all | Missing `no shutdown`, or one side set to `access` instead of `trunk` | `show interfaces trunk` / `show interfaces status` | `no shutdown`; ensure both ends run `switchport mode trunk` |
| 4 | Trunk is `trunking`, but one specific VLAN never crosses it | Incomplete allowed-VLAN list (Fault #1) | `show interfaces trunk` — check `Vlans allowed on trunk` | `switchport trunk allowed vlan add <vlan-id>` (never the bare replace form on a live trunk) |
| 5 | CDP logs a native VLAN mismatch warning | Native VLAN set differently on each end of the trunk (Fault #2) | Console message, or `show interfaces trunk` — check `Native vlan` column | Set matching native VLAN on both ends: `switchport trunk native vlan <id>` |
| 6 | Two hosts in different VLANs both reach their own gateways but not each other | Router-on-a-stick subinterface issue, or a missing VLAN in the *router-facing* trunk's allowed list | `show ip interface brief` (router) and `show interfaces trunk` (switch facing router) | Confirm VLAN is allowed on that trunk; check subinterface encapsulation (Step 7) |
| 7 | A specific subinterface shows `up/up` with a correct IP but still can't route that VLAN's traffic | Missing or wrong `encapsulation dot1Q <vlan-id>` (Fault #3) | `show interfaces <subinterface>` — look for the `Encapsulation 802.1Q ... Vlan ID` line | `encapsulation dot1Q <vlan-id>` under the subinterface |
| 8 | Everything above checks out but ping still fails | Missing default gateway on the PC, or ACL/firewall elsewhere in the path (not present in this lab's baseline) | `ipconfig`/PC IP config; `show run \| include access-list` | Correct PC default gateway; remove/adjust any unexpected ACL |
| 9 | Config disappears after a device reload | Forgot to save | `show startup-config` vs. `show running-config` | `copy running-config startup-config` |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why an explicit allowed-VLAN list instead of leaving trunks open to all VLANs (the IOS default)?** An unrestricted trunk forwards broadcast/multicast traffic for *every* VLAN across every trunk link, even VLANs that have no business being on that segment — wasted bandwidth at best, an unintended attack surface at worst. Explicitly scoping `switchport trunk allowed vlan` to only the VLANs that legitimately need to cross a given link is standard hardening practice, and it's also exactly why Fault #1 (an *incomplete* list) is realistic — the safer practice of explicit scoping is the same practice that creates the failure mode when someone forgets one VLAN.
- **Why does a native VLAN mismatch not take the trunk down?** 802.1Q trunking was designed for backward compatibility with untagged Ethernet — native VLAN traffic is deliberately sent *without* a tag so legacy untagged devices could still participate. That backward-compatibility design choice is precisely why a mismatch is silent instead of fatal: neither side has any protocol mechanism to detect "the untagged VLAN you assume for this traffic isn't the untagged VLAN I assume." CDP native VLAN mismatch detection is a Cisco-proprietary bolt-on warning, not a property of 802.1Q itself — which is also why disabling CDP (a real hardening practice) removes your only automatic warning for this specific fault.
- **Why router-on-a-stick here instead of a Layer 3 switch with SVIs?** Router-on-a-stick is deliberately used in this lab (and commonly in early-stage/small networks) because it needs only one router interface regardless of how many VLANs exist — cheap and simple for 2-3 VLANs. Its downside — all inter-VLAN traffic funnels through one physical link and one router's forwarding capacity — is exactly why real enterprises move to SVIs on a Layer 3 switch once VLAN count or inter-VLAN traffic volume grows; this trade-off is what a later CCNA lab on multilayer switching will revisit.
- **Why does this lab drill fault *diagnosis* instead of just showing a clean build?** Because in the field, VLANs and trunks are rarely built wrong from scratch — they're built right once and then drift: someone adds a VLAN and forgets one trunk link, someone reconfigures a native VLAN during a "quick fix" and doesn't tell the other switch's owner. The realistic failure mode isn't "nothing was configured," it's "something that used to work now doesn't," which is exactly what Section 6's fault-injection steps simulate.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a help desk ticket says "HR can't print to the shared printer but Engineering can," and the root cause turns out to be one trunk link missing VLAN 30 from its allowed list — a five-minute fix once you know to check `show interfaces trunk` instead of restarting switches.
- ...a network audit or a pen test flags a native VLAN mismatch that's been sitting silently in the config for months, because nobody was watching the console log the day it appeared and CDP messages scroll past unnoticed in a busy NOC.
- ...a company adds a fourth VLAN for a new department and inter-VLAN routing "just doesn't work" for the new VLAN specifically — almost always a missed `encapsulation dot1Q` line or a trunk allowed-list that wasn't updated on every hop.
- ...you inherit documentation that says a topology is "fully trunked and routing" and your first move, correctly, is to run `show interfaces trunk` and `show ip interface brief` yourself rather than trusting the documentation — this lab's verification-before-trust habit is a direct rehearsal for that.
- ...a senior engineer asks you to "walk the OSI layers" on a connectivity ticket instead of guessing — Section 9's sequential table is literally that muscle memory being built.

---

## 12. Stretch Goal

Once the base lab works end-to-end with all three faults fixed, try one or more of the following without referring back to the steps above:

1. **Reintroduce all three faults simultaneously** (incomplete allowed list, native VLAN mismatch, missing subinterface encapsulation) in a single session, then diagnose and fix all three using only the sequential method in Section 9 — no peeking at which fault is which.
2. **Add a fourth VLAN (IT, VLAN 40, a new `/26` block)** end-to-end: create the VLAN, assign an access port on SW2, add it to every trunk's allowed list, and add a matching router-on-a-stick subinterface on R1. This directly exercises the "we added a new department" real-world scenario from Section 11.
3. **Deliberately move the native VLAN on both trunk ends to an unused VLAN ID (e.g., VLAN 999)** instead of leaving it at the default VLAN 1 — a real hardening practice — and verify the mismatch warning disappears once both ends agree on the new native VLAN.
4. **Simulate a trunk-to-access-mode misconfiguration**: set one end of the SW1↔SW2 trunk to `switchport mode access` while the other stays `trunk`, observe what `show interfaces trunk` and `show interfaces status` report on each side, and explain why this failure looks different from both Fault #1 and Fault #2.

---

## 13. Self-Assessment

Before moving to Day 18, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, the difference between a trunk being "up" and a trunk correctly carrying a specific VLAN?
- [ ] Can you write the two different forms of `switchport trunk allowed vlan` (replace vs. `add`) and explain when using the wrong one causes an outage?
- [ ] Can you explain why a native VLAN mismatch doesn't bring a trunk down, referencing 802.1Q's untagged-traffic design?
- [ ] Can you name the exact command whose absence causes a router-on-a-stick subinterface to show `up/up` yet still fail to route?
- [ ] Given a topology where two VLANs route fine but a third doesn't, can you list — in the correct sequential order — every layer you'd check before touching the router config?
- [ ] Can you explain, without looking at Section 9, at least 5 of the 9 troubleshooting sequence steps?
- [ ] Could you explain to a non-technical manager, in under 2 minutes, why "the trunk shows up" isn't proof that everything is working?

If you answered "no" to more than two of these, redo Section 6's fault-injection steps from scratch (not by copy-pasting commands) before moving on.

---

## 14. Key Concepts Demonstrated

- **802.1Q trunking** — encapsulation, trunk negotiation, and the distinction between trunk state and allowed-VLAN scope
- **Trunk allowed-VLAN lists** — explicit scoping as both a hardening practice and a common fault surface
- **Native VLAN behavior** — why untagged/native traffic mismatches are silent rather than link-breaking
- **Router-on-a-stick** — per-VLAN subinterfaces, 802.1Q encapsulation, and its distinction from Layer 3 SVIs
- **Sequential/layered troubleshooting methodology** — physical → access port → trunk → allowed list → native VLAN → Layer 3 subinterface
- **Verification discipline** — the gap between "administratively fine" (`up/up`) and "actually functioning" output

---

## 15. What I Learned

Building this lab around deliberately injected faults instead of a clean build made a specific lesson land much harder than it would reading about it: `show ip interface brief` reporting `up/up` on a subinterface is not proof that VLAN traffic is actually being routed. That gap — between "administratively configured" and "actually forwarding the traffic you expect" — is where most of Day 17's real troubleshooting time went, especially with Fault #3.

The native VLAN mismatch was the most conceptually important fault, because it's the one that produces zero connectivity symptoms in isolation — the trunk works, pings across the *matching* VLANs still succeed, and only CDP's console warning (or, without CDP, a much harder-to-spot symptom down the line) reveals anything is wrong. That silence is exactly why real production networks treat native VLAN hygiene as a standing security practice, not a one-time configuration step.

This lab is the foundation for what comes next:

- Layer 3 switching and SVIs (replacing router-on-a-stick as VLAN count grows)
- Spanning Tree Protocol interactions with trunk links
- VLAN hardening (native VLAN relocation, unused VLAN pruning)
- Dynamic routing across a multi-VLAN, multi-switch topology

---

## 16. Skills Practiced

- 802.1Q trunk configuration and allowed-VLAN list scoping
- Native VLAN mismatch recognition and remediation
- Router-on-a-stick subinterface configuration and verification
- Sequential, layer-by-layer network troubleshooting methodology
- Reading `show` command output critically (administrative state vs. actual function)

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology that mirrors the design above using free, open-source images, built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Switches (SW1, SW2) | Cisco 2960-24TT | Open vSwitch |
| Router (R1) | Cisco 2911 | VyOS |
| PCs (PC2–PC5) | Generic PC | Linux (Alpine) |

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script and how VyOS's trunk/subinterface syntax maps to the IOS commands used throughout this manual.
