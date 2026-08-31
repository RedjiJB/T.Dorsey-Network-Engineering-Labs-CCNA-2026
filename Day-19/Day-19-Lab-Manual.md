# Day 19 Lab Manual — VTP, Trunking, and VLAN Management

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Build a three-switch campus topology with trunked inter-switch links and centralized VLAN management via VTP, demonstrating Server, Transparent, and Client mode behavior side by side. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): VLANs, trunking (802.1Q), access vs. trunk ports. Domain 2 (Network Access): VTP, DTP, native VLAN, VLAN trunking configuration/verification/troubleshooting — this is one of the most heavily tested Domain 2 topics. |
| **Prerequisites** | Day 01 (device roles, IOS CLI fundamentals, addressing basics). Comfort with `interface`, `switchport`, and `show` command syntax on IOS switches. No addressing-plan math required for this lab. |
| **Time Estimate** | 2 – 3 hours (first attempt); 30–45 minutes on repeat/review. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the CLI commands themselves are short, but VTP's *stateful, sometimes destructive* behavior (revision numbers, domain propagation) makes this a lab where understanding *why* matters more than memorizing commands. |

---

## 1. Lab Overview

This lab builds a three-switch topology — **SW1, SW2, SW3** — connected by trunk links, and uses **VTP (VLAN Trunking Protocol)** to centralize VLAN database management across them. Each switch runs a different VTP mode on purpose, so you see all three behaviors in one lab instead of reading about them in isolation:

- **SW1 — VTP Server.** Creates VLANs 10, 20, 30 and propagates them to the rest of the domain.
- **SW2 — VTP Transparent.** Forwards VTP advertisements it hears, but keeps its own local VLAN database (VLAN 40) completely separate — nothing it creates locally propagates, and nothing SW1 creates shows up as "belonging to" SW2's local decisions either way (it still learns SW1's VLANs off the wire because Transparent mode relays advertisements, but its *own* database is independent).
- **SW3 — VTP Client.** Receives VLANs from SW1 automatically but is structurally prevented from creating or modifying any VLAN locally.

Every inter-switch link is manually forced to trunk mode with DTP negotiation disabled — a deliberate hardening step, not just a formality — and every host-facing port is manually forced to access mode in a specific VLAN.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Configure and verify 802.1Q trunk ports, including manually disabling DTP negotiation
- Explain the difference between a trunk's *administrative* mode and its *operational* mode
- Configure VTP domain name, password, and mode (Server/Client/Transparent) on multiple switches
- Predict and verify which VLANs propagate across a VTP domain and which don't, based on mode
- Explain why VTP's configuration revision number is the single most dangerous number in a campus network
- Configure access ports correctly, including a hardened default that resists DTP-based VLAN hopping
- Articulate, in business terms, why many real-world networks have moved away from VTP entirely

---

## 2. Business Context

**Why would a real company do this?**

Imagine you're the network engineer for a company with a single building split across three wiring closets — one per floor — each with its own access switch (SW1, SW2, SW3) uplinked to a shared distribution layer. Leadership and other teams' requirements, translated into network language, look like this:

- **"Every floor needs the same set of VLANs — Sales, Engineering, Guest Wi-Fi — and we can't have someone manually re-typing `vlan 10 / name SALES` on all three switches every time HR adds a department."** → This is the textbook justification for VTP: define the VLAN database once, on one switch, and let it propagate.
- **"The security team's testing switch on floor 2 should never be able to push its lab VLANs onto the production floors."** → This is exactly why SW2 sits in **Transparent** mode: it participates in the trunk topology and passes VTP advertisements through, but its own local VLAN (40) stays local, and it can't accidentally overwrite anyone else's database (nor can it be overwritten by database changes it merely relays).
- **"Floor 3's switch is closet-only, no one should be creating new VLANs down there without going through change control."** → SW3 in **Client** mode enforces this structurally — it's not a policy someone has to remember, the CLI itself refuses `vlan 50` on a Client-mode switch.
- **"We had an incident once where a shelved lab switch was plugged back in and it wiped out half our VLANs — how do we stop that from happening again?"** → This is the single most important real-world lesson VTP teaches, covered in depth in Section 8 (Common Mistakes) and Section 10 (Design Analysis): VTP trusts whichever switch has the **highest configuration revision number**, not whichever switch an admin currently considers authoritative. A stale switch with a higher revision number than your live network can silently overwrite your entire VLAN database the moment it's plugged into a trunk in the same domain — a genuinely famous outage cause in real networking history.
- **"We need every port that isn't explicitly a switch-to-switch uplink to be locked to access mode — no auto-negotiated trunks."** → Handled by disabling DTP everywhere (`switchport nonegotiate`) and hard-setting `switchport mode access` on every host port, closing off VLAN-hopping attacks that rely on a port auto-negotiating into trunk mode.

This is the kind of topology and the exact set of gotchas a network engineer runs into during their first campus-switching rotation — VTP looks like a convenience feature until the day it isn't.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-19-Lab-DTP-%26-VTP.png" alt="Day 19 VTP and Trunking Lab" width="900">
</p>

### 3.1 Traffic Flow / Trunk Topology Summary

```text
SW1 (VTP Server, domain CCNA) --- trunk Gi0/1 --- SW2 (VTP Transparent, domain CCNA)
SW2 (VTP Transparent, domain CCNA) --- trunk Gi0/2 --- SW3 (VTP Client, domain CCNA)

SW1 host ports:  Fa0/1-2 -> VLAN 10 (SALES)   | Fa0/3 -> VLAN 20 (ENG)
SW2 host ports:  Fa0/3-4 -> VLAN 20 (ENG)
SW3 host ports:  Fa0/1-2 -> VLAN 30 (GUEST)
```

> **Note on the SW1–SW2–SW3 chain:** SW2 sits *between* SW1 and SW3 in this topology, which matters for VTP: because Transparent-mode switches still forward VTP advertisements out their trunk ports even though they don't act on them locally, SW1's advertisements pass *through* SW2 and still reach SW3. This is a commonly misunderstood point — Transparent mode is not the same as "VTP off," and it does not break the domain's propagation path for other switches.

### 3.2 Equipment List

| Device | Role | Model | VTP Mode | VTP Domain |
|---|---|---|---|---|
| `SW1` | Access switch, floor 1 | Cisco 2960-24TT | Server | CCNA |
| `SW2` | Access switch, floor 2 | Cisco 2960-24TT | Transparent | CCNA |
| `SW3` | Access switch, floor 3 | Cisco 2960-24TT | Client | CCNA |
| `PC10-1`, `PC10-2` | End hosts, VLAN 10 | Generic PC | n/a | n/a |
| `PC20-1` | End host, VLAN 20 (SW1 side) | Generic PC | n/a | n/a |
| `PC20-2`, `PC20-3` | End hosts, VLAN 20 (SW2 side) | Generic PC | n/a | n/a |
| `PC30-1`, `PC30-2` | End hosts, VLAN 30 | Generic PC | n/a | n/a |

> **Note on realism:** This lab has no routers, firewalls, or WAN — it is a pure Layer 2 lab. Inter-VLAN routing (needed for PC10-1 to reach PC20-1, for example) is a **later** topic (SVIs/Router-on-a-Stick); don't expect cross-VLAN pings to succeed here, and don't troubleshoot toward that goal — see Section 10.3 for the reachability matrix that reflects this correctly.

---

## 4. IP Addressing Plan

This lab is **purely Layer 2** — VTP, trunking, and VLAN database management. No new IP subnets are introduced, and no interface on any switch needs a newly-derived address beyond what management access already requires.

For end-host and switch management IP addressing conventions, reuse the addressing plan and derivation method from **Day 01, Section 4** (the `/24` LAN sizing rationale and `/30` transit-link math there still apply anywhere this lab's topology is extended with routing later). If you want each VLAN in this lab to have a real subnet for later inter-VLAN routing labs, a clean forward-compatible scheme is:

| VLAN | Suggested future subnet | Purpose |
|---|---|---|
| 10 (SALES) | 192.168.10.0/24 | Matches Day 01's NY LAN convention |
| 20 (ENG) | 192.168.20.0/24 | Matches Day 01's Tokyo LAN convention |
| 30 (GUEST) | 192.168.30.0/24 | New — guest/isolated segment |
| 40 (SW2-LOCAL) | 192.168.40.0/24 | Local-only, never routed off SW2 in this lab |

These are **not required for this lab to function** — VLANs exist and propagate at Layer 2 regardless of whether an SVI or IP address is ever assigned to them. They're included here only so the addressing scheme stays consistent if/when you revisit this topology for a Router-on-a-Stick or SVI-based inter-VLAN routing lab later in the course.

---

## 5. Pre-Configuration Checklist

Before typing a single command:

1. Place SW1, SW2, and SW3 in Packet Tracer, chained SW1—SW2—SW3 as shown in Section 3.
2. Cable the inter-switch links with copper straight-through (Packet Tracer auto-detects; verify link lights turn green/amber-then-green).
3. Cable each PC to its assigned access port per Section 3.2 / Section 6.4.
4. Confirm interface numbering matches what's used below (`GigabitEthernet0/1`, `FastEthernet0/1`, etc.) — substitute if your platform assigns different port numbers.
5. **Before configuring VTP mode on any switch, decide your build order: SW1 (Server) first, then SW2 (Transparent), then SW3 (Client).** Building in this order means VLANs exist on the Server before a Client switch ever needs to receive them, avoiding a confusing "why isn't my VLAN here yet" moment.
6. If any switch was previously used in another lab, check its **VTP configuration revision number** (`show vtp status`) and domain name *before* trunking it into this topology — see Section 8, Mistake #1, for why this single step prevents the worst VTP failure mode.

---

## 6. Configuration Tasks

### 6.1 SW1 — VTP Server

**Step 1: Hostname and basic hardening**

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW1
SW1(config)#enable secret class
SW1(config)#service password-encryption
SW1(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. SW1 - Authorized Use Only.
#
```

- **Mode:** User EXEC → Privileged EXEC → Global Config. Same reasoning as Day 01 — `enable secret` over `enable password` for hashed storage, `service password-encryption` to obscure remaining plaintext secrets in `show run`.

**Step 2: Configure the trunk link toward SW2**

```text
SW1(config)#interface gigabitEthernet0/1
SW1(config-if)#description Trunk to SW2
SW1(config-if)#switchport trunk encapsulation dot1q
SW1(config-if)#switchport mode trunk
SW1(config-if)#switchport nonegotiate
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

- **`switchport trunk encapsulation dot1q`** — required on switches that support both ISL and 802.1Q (older 2960 models default to needing this explicitly; newer ones are dot1q-only and will reject/ignore the command harmlessly). 802.1Q is the IEEE standard trunking encapsulation — it's what tags frames with a 12-bit VLAN ID as they cross the trunk, and it's the only encapsulation you'll see on the exam (ISL is Cisco-proprietary and deprecated).
- **`switchport mode trunk`** — this is the command that actually forces the port into trunking, independent of what the far end negotiates. *Memory aid: "trunk" carries multiple VLANs the way a tree trunk carries multiple branches' worth of nutrients through one shared path.*
- **`switchport nonegotiate`** — disables **DTP (Dynamic Trunking Protocol)** on this port. DTP is what lets two switches auto-negotiate whether a link becomes a trunk. Disabling it is a deliberate hardening choice: an attacker (or a careless technician) plugging into a DTP-enabled access port configured as `dynamic auto`/`dynamic desirable` can potentially trick a switch into forming a trunk, gaining access to every VLAN on that trunk instead of just one. Manually setting `trunk` + `nonegotiate` removes that entire attack surface. *Memory aid: "nonegotiate" = "we already decided, stop asking."*
- **Why `no shutdown` still matters here:** trunk ports boot administratively down exactly like any other physical interface — this is the single most common Day 01-style mistake reappearing in a new context.

**Step 3: Restrict allowed VLANs and set the native VLAN (hardening, recommended even though the source lab didn't require it)**

```text
SW1(config)#interface gigabitEthernet0/1
SW1(config-if)#switchport trunk allowed vlan 10,20,30,40,99
SW1(config-if)#switchport trunk native vlan 99
SW1(config-if)#exit
SW1(config)#vlan 99
SW1(config-vlan)#name NATIVE-UNUSED
SW1(config-vlan)#exit
```

- **`switchport trunk allowed vlan`** — by default, a trunk carries *every* VLAN 1–4094. Explicitly listing only the VLANs actually in use (10, 20, 30, 40, plus the native VLAN 99) shrinks the broadcast domain crossing the trunk and limits what a compromised device on one segment could ever reach, even hypothetically, via VLAN-hopping. *Why 40 is included even though it "shouldn't" propagate:* VTP Transparent-mode advertisements for VLAN 40 still cross this trunk as relayed traffic even though SW1 never uses VLAN 40 itself — the allowed-VLAN list controls what data-plane traffic can cross, which is a separate concern from VTP control-plane propagation.
- **Native VLAN** — the one VLAN on a trunk whose frames are sent **untagged**. By default this is VLAN 1 on every switch, which is a real security problem: VLAN 1 also carries CDP, PAgP, and other control-plane chatter by default, and an untagged native VLAN mismatch between two ends of a trunk is a classic misconfiguration that silently leaks traffic between VLANs. Moving the native VLAN to an unused ID (99 here, never assigned to any host) and confirming both trunk ends agree on it is standard hardening practice. *Memory aid: "native" = the VLAN that gets to travel without a passport (tag) — so don't let it be a VLAN anyone is actually using.*

> Repeat Step 2 and Step 3's trunk configuration on `gigabitEthernet0/2` only if your build gives SW1 a second physical trunk; in this three-switch chain SW1 only needs the one trunk toward SW2.

**Step 4: Configure the VTP domain and mode**

```text
SW1(config)#vtp domain CCNA
SW1(config)#vtp mode server
SW1(config)#vtp password Cisco123
SW1(config)#vtp version 2
```

- **`vtp domain CCNA`** — the domain name is what scopes VTP advertisements; two switches only exchange VLAN database updates if they're configured with the **exact same domain name, and domain names are case-sensitive** (`CCNA` and `ccna` are different domains as far as VTP is concerned — see Section 8, Mistake #3).
- **`vtp mode server`** — Server is actually the *default* VTP mode on most switches out of the box, but setting it explicitly documents intent and protects against an unexpected mode left over from a prior lab.
- **`vtp password`** — without a password, *any* switch that's plugged into this domain with a matching domain name and a higher revision number can start influencing (or overwriting) the VLAN database. The password doesn't stop propagation, but it does stop a switch that doesn't know the password from being accepted into the domain in the first place. *Memory aid: domain name gets you in the room, the password proves you're supposed to be there.*
- **`vtp version 2`** (or 3, if your platform supports it) — VTPv1 and v2 are mostly interchangeable for VLANs 1–1005 but v2 adds support for Token Ring VLANs and slightly different consistency checks; VTPv3 (where available) adds support for extended-range VLANs and a primary-server election model that removes the "highest revision wins blindly" danger described in Section 8. For CCNA purposes, know that a version mismatch across the domain can also block propagation — all switches should run the same VTP version where possible.

**Step 5: Create VLANs 10, 20, and 30**

```text
SW1(config)#vlan 10
SW1(config-vlan)#name SALES
SW1(config-vlan)#exit
SW1(config)#vlan 20
SW1(config-vlan)#name ENG
SW1(config-vlan)#exit
SW1(config)#vlan 30
SW1(config-vlan)#name GUEST
SW1(config-vlan)#exit
```

> Every `vlan` command that changes the database (create, rename, delete) increments SW1's **VTP configuration revision number** by 1. This number is how every other switch in the domain decides whether an incoming advertisement is "newer" than what it currently has — see Section 8 for why this matters so much.

**Step 6: Configure host-facing access ports**

```text
SW1(config)#interface range fastEthernet0/1-2
SW1(config-if-range)#switchport mode access
SW1(config-if-range)#switchport access vlan 10
SW1(config-if-range)#switchport nonegotiate
SW1(config-if-range)#spanning-tree portfast
SW1(config-if-range)#no shutdown
SW1(config-if-range)#exit
SW1(config)#interface fastEthernet0/3
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 20
SW1(config-if)#switchport nonegotiate
SW1(config-if)#spanning-tree portfast
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

- **`switchport mode access`** — manually forces access mode, refusing to ever negotiate into a trunk regardless of what's plugged in.
- **`switchport nonegotiate` on an access port** — belt-and-suspenders: even though `mode access` already prevents trunking, explicitly disabling DTP means this port never even *sends* a DTP frame, reducing what a device plugged into it can learn about the switch.
- **`spanning-tree portfast`** — same reasoning as Day 01: skips the ~30-second STP listening/learning delay on host-facing ports. Never apply this to a trunk/uplink port.

**Step 7: Save**

```text
SW1#copy running-config startup-config
```

---

### 6.2 SW2 — VTP Transparent

**Step 1: Hostname and hardening**

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW2
SW2(config)#enable secret class
SW2(config)#service password-encryption
SW2(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. SW2 - Authorized Use Only.
#
```

**Step 2: Configure both trunk links (toward SW1 and toward SW3)**

```text
SW2(config)#interface gigabitEthernet0/1
SW2(config-if)#description Trunk to SW1
SW2(config-if)#switchport trunk encapsulation dot1q
SW2(config-if)#switchport mode trunk
SW2(config-if)#switchport nonegotiate
SW2(config-if)#switchport trunk allowed vlan 10,20,30,40,99
SW2(config-if)#switchport trunk native vlan 99
SW2(config-if)#no shutdown
SW2(config-if)#exit
SW2(config)#interface gigabitEthernet0/2
SW2(config-if)#description Trunk to SW3
SW2(config-if)#switchport trunk encapsulation dot1q
SW2(config-if)#switchport mode trunk
SW2(config-if)#switchport nonegotiate
SW2(config-if)#switchport trunk allowed vlan 10,20,30,40,99
SW2(config-if)#switchport trunk native vlan 99
SW2(config-if)#no shutdown
SW2(config-if)#exit
```

> SW2 sits in the *middle* of the chain, so it needs two trunk ports configured identically in principle — same encapsulation, same allowed list, same native VLAN — because a native VLAN mismatch on either link independently breaks that link's untagged traffic handling.

**Step 3: Configure VTP domain and Transparent mode**

```text
SW2(config)#vtp domain CCNA
SW2(config)#vtp mode transparent
SW2(config)#vtp password Cisco123
```

- **Why the domain name and password still matter in Transparent mode:** even though SW2 doesn't *act on* VTP advertisements to change its own database, it still needs to match the domain name to correctly relay (forward) advertisements between SW1 and SW3 rather than silently dropping them. Transparent mode is best understood as "pass it along, but don't obey it."
- **`vtp mode transparent`** — this is the mode where the local VLAN database becomes fully independent. Local VLAN creates/deletes on SW2 do **not** increment a domain-wide revision number the way Server mode does, and they never propagate to SW1 or SW3.

**Step 4: Create the local-only VLAN 40**

```text
SW2(config)#vlan 40
SW2(config-vlan)#name SW2-LOCAL
SW2(config-vlan)#exit
```

> This VLAN exists **only on SW2**. `show vlan brief` on SW1 or SW3 will never list VLAN 40 — that's expected, correct behavior, not a propagation failure. See Section 7.2 for exactly what this looks like in `show vtp status` and `show vlan brief` output.

**Step 5: Configure host-facing access ports**

```text
SW2(config)#interface range fastEthernet0/3-4
SW2(config-if-range)#switchport mode access
SW2(config-if-range)#switchport access vlan 20
SW2(config-if-range)#switchport nonegotiate
SW2(config-if-range)#spanning-tree portfast
SW2(config-if-range)#no shutdown
SW2(config-if-range)#exit
```

> These ports use VLAN 20 (ENG) — a VLAN that SW2 *learned from SW1 via VTP relay*, not one it created locally. This is a useful checkpoint: it proves a Transparent-mode switch can still assign its own access ports into a VLAN ID that exists in its database because it heard about it on the wire, even though it can't originate new VLANs into the domain.

**Step 6: Save**

```text
SW2#copy running-config startup-config
```

---

### 6.3 SW3 — VTP Client

**Step 1: Hostname and hardening**

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW3
SW3(config)#enable secret class
SW3(config)#service password-encryption
SW3(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. SW3 - Authorized Use Only.
#
```

**Step 2: Configure the trunk link toward SW2**

```text
SW3(config)#interface gigabitEthernet0/1
SW3(config-if)#description Trunk to SW2
SW3(config-if)#switchport trunk encapsulation dot1q
SW3(config-if)#switchport mode trunk
SW3(config-if)#switchport nonegotiate
SW3(config-if)#switchport trunk allowed vlan 10,20,30,40,99
SW3(config-if)#switchport trunk native vlan 99
SW3(config-if)#no shutdown
SW3(config-if)#exit
```

**Step 3: Configure VTP domain and Client mode**

```text
SW3(config)#vtp domain CCNA
SW3(config)#vtp mode client
SW3(config)#vtp password Cisco123
```

- **Client mode** keeps a full copy of the VLAN database, synced from the Server, and can even act as a relay point for advertisements further down a chain — but the CLI structurally refuses any command that would locally create, rename, or delete a VLAN.

**Step 4: Attempt to create a local VLAN (expected to fail — this is the point of the exercise)**

```text
SW3(config)#vlan 50
```

Expected result:

```text
VTP VLAN configuration not allowed when device is in CLIENT mode.
```

> Don't troubleshoot this as an error — this is the CLI correctly enforcing Client-mode restrictions. If SW1 later creates VLAN 50, it will propagate to SW3 automatically without you doing anything.

**Step 5: Configure host-facing access ports**

```text
SW3(config)#interface range fastEthernet0/1-2
SW3(config-if-range)#switchport mode access
SW3(config-if-range)#switchport access vlan 30
SW3(config-if-range)#switchport nonegotiate
SW3(config-if-range)#spanning-tree portfast
SW3(config-if-range)#no shutdown
SW3(config-if-range)#exit
```

**Step 6: Save**

```text
SW3#copy running-config startup-config
```

---

### 6.4 End Hosts

Open each PC → **Desktop tab → IP Configuration** and assign an address from the VLAN's future subnet (Section 4) if your build includes IP addressing at this stage; otherwise these hosts can remain unconfigured for a pure Layer 2 VLAN-propagation verification pass.

| Device | Access Port | VLAN |
|---|---|---|
| PC10-1 | SW1 Fa0/1 | 10 |
| PC10-2 | SW1 Fa0/2 | 10 |
| PC20-1 | SW1 Fa0/3 | 20 |
| PC20-2 | SW2 Fa0/3 | 20 |
| PC20-3 | SW2 Fa0/4 | 20 |
| PC30-1 | SW3 Fa0/1 | 30 |
| PC30-2 | SW3 Fa0/2 | 30 |

---

## 7. Verification Steps

### 7.1 Device-level verification commands

| Device | Command | What to check |
|---|---|---|
| All switches | `show vtp status` | Operating Mode, Domain Name, Configuration Revision |
| All switches | `show vlan brief` | Which VLANs exist locally and which ports belong to them |
| All switches | `show interface <trunk-port> switchport` | Administrative/Operational Mode = trunk, Negotiation of Trunking = Off, Native VLAN |
| All switches | `show interface trunk` | Quick summary of all trunk ports, allowed VLANs, and VLANs in spanning-tree forwarding state |
| Access ports | `show interface <port> switchport` | Administrative Mode: static access, Negotiation of Trunking: Off |

### 7.2 Expected Output Gallery

**`SW1# show vtp status`**

```text
VTP Version capable             : 1 to 3
VTP version running             : 2
VTP Domain Name                 : CCNA
VTP Pruning Mode                : Disabled
VTP Traps Generation            : Disabled
Device ID                       : 0001.42a3.0001
Configuration last modified by 0.0.0.0 at 0-0-00 00:00:00

Feature VLAN:
--------------
VTP Operating Mode                : Server
Maximum VLANs supported locally   : 255
Number of existing VLANs          : 8
Configuration Revision            : 3
MD5 digest                        : 0xA1 0xB2 0xC3 0xD4 0xE5 0xF6 0x11 0x22
                                     0x33 0x44 0x55 0x66 0x77 0x88 0x99 0xAA
```

The **Configuration Revision: 3** reflects the three `vlan` create commands from Step 6.1.5 — each one incremented it by 1 from a fresh baseline of 0.

**`SW2# show vtp status`**

```text
VTP Operating Mode                : Transparent
VTP Domain Name                   : CCNA
Configuration Revision            : 0
Number of existing VLANs          : 6
```

Note `Configuration Revision: 0` even after creating VLAN 40 locally — Transparent mode does not participate in domain-wide revision numbering, because its local changes are never advertised as authoritative for the domain.

**`SW3# show vtp status`**

```text
VTP Operating Mode                : Client
VTP Domain Name                   : CCNA
Configuration Revision            : 3
Number of existing VLANs          : 8
```

SW3's revision number **matches SW1's (3)** — proof that it received and adopted SW1's VLAN database via VTP relay through SW2, even though SW2 itself never "agreed" to those VLANs locally.

**`SW1# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active
10   SALES                            active    Fa0/1, Fa0/2
20   ENG                              active    Fa0/3
30   GUEST                            active
99   NATIVE-UNUSED                    active
```

Notice VLAN 30 shows **active but with no ports** on SW1 — it was created here but its access ports live on SW3, three hops of database sync away. VLAN 40 does **not** appear here at all — this is expected (see below).

**`SW2# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active
10   SALES                            active
20   ENG                              active    Fa0/3, Fa0/4
30   GUEST                            active
40   SW2-LOCAL                        active
99   NATIVE-UNUSED                    active
```

SW2 shows **all of SW1's VLANs (10, 20, 30) plus its own local VLAN 40** — Transparent mode still learns the domain's VLANs off the wire for local port assignment purposes, it just doesn't treat its own creations as domain-authoritative.

**`SW3# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active
10   SALES                            active
20   ENG                              active
30   GUEST                            active    Fa0/1, Fa0/2
99   NATIVE-UNUSED                    active
```

VLAN 40 is **absent** here too — confirming it never left SW2. This single comparison across all three `show vlan brief` outputs is the clearest proof-of-concept in the whole lab.

**`SW1# show interface gigabitEthernet0/1 switchport`**

```text
Name: Gi0/1
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Negotiation of Trunking: Off
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 99 (NATIVE-UNUSED)
Trunking VLANs Enabled: 10,20,30,40,99
```

`Administrative Mode` and `Operational Mode` both reading `trunk`, with `Negotiation of Trunking: Off`, confirms the port is hard-set (not DTP-negotiated) — exactly what Step 6.1.2's `nonegotiate` was for.

### 7.3 VLAN Propagation Matrix

| VLAN | Created on | Appears on SW1? | Appears on SW2? | Appears on SW3? | Why |
|---|---|---|---|---|---|
| 10, 20, 30 | SW1 (Server) | Yes (origin) | Yes (learned) | Yes (learned) | Server-originated changes propagate domain-wide |
| 40 | SW2 (Transparent) | **No** | Yes (origin, local-only) | **No** | Transparent mode never advertises local changes as domain-authoritative |
| 50 | Attempted on SW3 (Client) | n/a | n/a | **Rejected — never created** | Client mode cannot create VLANs locally |

### 7.4 What This Proves

- **VTP Server mode is the single source of truth** for domain-wide VLANs — create once, it shows up everywhere in the domain.
- **VTP Transparent mode is a firewall for the local VLAN database** — it relays what it hears but never lets local changes leak out, and never lets domain changes it disagrees with silently overwrite what it has locally (because it has no domain-authoritative database to overwrite in the first place).
- **VTP Client mode is read-only by design** — not a suggestion enforced by policy, but a hard CLI restriction.
- **Trunk hardening (`nonegotiate`, restricted allowed-VLAN list, non-default native VLAN) works independently of VTP** — even if VTP were disabled entirely, these three settings would still be correct practice on every inter-switch link.

---

## 8. Common Mistakes (the 80/20)

1. **Plugging in a "recycled" switch with a higher VTP revision number and the same domain name than your live network.** This is the single most damaging VTP mistake that exists — a switch that was previously a Server in some other lab, still holding domain "CCNA" and a configuration revision of, say, 40, will silently **overwrite every VLAN on every switch in your live domain** the instant it's trunked in, because VTP trusts the highest revision number it sees, not which switch an administrator considers "real." Always check `show vtp status` on a switch before trunking it into any domain — if in doubt, reset its VTP revision to 0 first (see Section 9, Step 1) or change its domain name before connecting it.
2. **Forgetting `switchport nonegotiate` and assuming `switchport mode trunk` alone is enough.** `switchport mode trunk` forces the *local* end into trunking, but DTP frames can still be sent/received unless negotiation is explicitly disabled — leaving a theoretical (and, on some exam questions, tested) inconsistency between "administrative mode" and what actually happens if the far end's configuration changes later.
3. **Typing the VTP domain name with different capitalization on different switches.** `vtp domain CCNA` and `vtp domain ccna` are treated as **different domains** — VTP domain names are case-sensitive. Two switches in the same physical trunk topology but different-cased domain names will not exchange any VLAN information, and `show vtp status` will show two completely separate, "correct-looking" domains that just never talk to each other.
4. **Expecting VLAN 40 to show up on SW1 or SW3 and treating its absence as a bug.** This is the most common conceptual (not typo) mistake in this specific lab — re-read Section 7.3 before assuming something is broken.
5. **Trying to create/modify a VLAN on a Client-mode switch and not understanding why it's refused.** Not a bug, not a missing permission to grant — this is VTP Client mode functioning exactly as designed. Change the VLAN on the Server instead.
6. **Native VLAN mismatch between the two ends of a trunk.** If one end is set to native VLAN 99 and the other is left at the default (VLAN 1), you'll see a `%CDP-4-NATIVE_VLAN_MISMATCH` warning and untagged traffic will land in the wrong VLAN on each side. Always configure the native VLAN identically on both ends of every trunk.
7. **Setting a VTP password on some switches in the domain but not all of them.** A password mismatch (or a password set on only one side) prevents those switches from trusting each other's advertisements, which looks identical to a domain-name mismatch in symptoms — always verify `show vtp password` (if supported) or reconfigure the password consistently everywhere at once.
8. **Forgetting `no shutdown` on a trunk port** — identical to Day 01's #1 mistake, just recurring in trunk-port form; `show interface trunk` will simply omit a shutdown trunk port entirely, which is easy to misread as "the trunk isn't configured" rather than "the trunk is configured but down."

---

## 9. Troubleshooting Guide

Work through these **in order** — each step assumes the previous one passed.

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | A switch's VLAN database was unexpectedly overwritten after connecting it | Higher-revision switch joined the domain | `show vtp status` (check Configuration Revision on the newly-connected switch) | Isolate the switch, reset its revision to 0 by changing its `vtp domain` to a bogus name and back (or to `transparent` mode and back to `server`), then reconnect |
| 2 | Trunk port shows `Operational Mode: static access` instead of `trunk` | `switchport mode trunk` missing, or far end refused negotiation | `show interface <port> switchport` | Set `switchport mode trunk` on both ends explicitly; don't rely on DTP auto-negotiation |
| 3 | VLAN created on SW1 doesn't appear on SW3 | Domain name mismatch (including case), VTP password mismatch, or trunk down between them | `show vtp status` on both switches; `show interface trunk` | Match domain name exactly (case-sensitive) and VTP password on all switches; verify trunk is up |
| 4 | VLAN 40 doesn't appear on SW1 or SW3 | **Not a fault** — Transparent-mode local VLANs never propagate | `show vtp status` (Operating Mode: Transparent) | No fix needed — confirm this is the expected behavior from Section 7.3 |
| 5 | `vlan 50` refused on SW3 with a CLIENT-mode error | **Not a fault** — Client mode cannot create local VLANs | `show vtp status` (Operating Mode: Client) | Create the VLAN on the Server (SW1) instead; it will propagate automatically |
| 6 | CDP native VLAN mismatch warning appears | Native VLAN differs between the two ends of a trunk | `show interface <port> switchport` (compare Native VLAN on both ends) | Set the same native VLAN on both ends of the trunk |
| 7 | Access port unexpectedly negotiates into trunk mode | DTP left enabled, and the port defaulted to `dynamic auto`/`dynamic desirable` | `show interface <port> switchport` (Administrative Mode) | Set `switchport mode access` and `switchport nonegotiate` explicitly |
| 8 | Trunk port administratively down | Forgot `no shutdown` | `show interface trunk` / `show ip interface brief` | `no shutdown` on the interface |
| 9 | Two switches in the same domain show completely different VLAN databases with no errors | VTP version mismatch, or one switch is in Transparent mode and was mistaken for Server/Client | `show vtp status` on both (check VTP version running and Operating Mode) | Align VTP version across the domain; confirm intended mode on each switch |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why use VTP at all instead of manually configuring the same VLANs on every switch?** At three switches, manual configuration is barely a burden — but the moment a real campus network reaches dozens of access switches, retyping the same `vlan`/`name` pairs on every device (and keeping them perfectly consistent) becomes both tedious and a genuine source of human-error outages. VTP's original value proposition was "define it once, on one authoritative switch, and never touch the others for routine VLAN changes."
- **Why does this lab deliberately include a Transparent-mode switch?** Not every switch in a real network should trust a central VTP Server blindly — a lab bench, a DMZ switch, a switch owned by a different team, or any device where local VLAN decisions genuinely need to be independent of the production VLAN database is a legitimate use case for Transparent mode. It's the "look but don't touch, and don't be touched" mode.
- **Why does this lab deliberately fail to create VLAN 50 on the Client switch?** This demonstrates that VTP Client mode is a genuine **access control mechanism at the CLI level**, not just documentation of "who's supposed to make changes." On the exam and in the field, this distinction (structurally prevented vs. merely discouraged) is exactly the kind of nuance that separates understanding VTP from having memorized its command syntax.
- **Why do so many real-world networks avoid VTP entirely today, even though it's still on the CCNA exam?** VTP's core danger — a stale switch with a higher revision number silently overwriting a live production VLAN database — is a **real, well-documented, and genuinely catastrophic failure mode** that has caused multi-site outages in actual companies. VTPv3 mitigates this somewhat (primary-server election, MST/extended-VLAN support), but many organizations decided the operational risk still outweighs the convenience, especially now that VLAN counts per switch are usually small enough that manual configuration (or configuration-management tooling like Ansible pushing consistent VLAN configs to every switch) is a safer, equally scalable alternative. The modern default in a lot of shops is: **VTP Transparent mode everywhere** (so the *feature* is technically "on" for compliance/consistency reasons, but no switch can ever silently overwrite another) combined with automated configuration push for actual VLAN rollout — getting VTP's original consistency goal without its blast-radius risk.
- **Why disable DTP on every trunk regardless of VTP mode?** DTP and VTP are two entirely separate protocols that happen to be used together — DTP negotiates *whether* a link becomes a trunk; VTP manages *what VLAN database* flows across it once it is one. Hardening DTP (`nonegotiate`) protects against a completely different attack (VLAN hopping via a rogue trunk negotiation) than anything VTP mode selection addresses, which is why both are configured independently in Section 6, and why real CCNA exam questions test them as separate concepts even though they show up on the same physical port.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a mid-size company's IT team is debating whether to enable VTP Server mode campus-wide, and someone in the room says "didn't a stale lab switch wipe out VLANs at my last job?" — that's this lab's central lesson, told as an anecdote instead of a diagram.
- ...you're the new hire handed a "decommissioned" switch to reuse, and the very first thing a senior engineer tells you to check is `show vtp status` before you plug it into anything — a five-second habit this lab is designed to build.
- ...a security audit flags that access ports are left in `dynamic auto` mode, and the finding cites exactly the VLAN-hopping risk that `switchport nonegotiate` + `switchport mode access` closes.
- ...a network diagram shows "VTP domain: CORP" on every switch, but two floors mysteriously don't share VLANs — and the root cause, after an hour of investigation, turns out to be a domain name typed with different capitalization on one switch six months ago.
- ...a team decides to migrate off VTP Server mode entirely in favor of Transparent-mode-everywhere plus Ansible-managed VLAN configs — a real, common architectural decision directly informed by the Design Analysis reasoning above.

---

## 12. Stretch Goal

Once the base lab works end-to-end, try one or more of the following without referring back to the steps above:

1. **Simulate the classic VTP disaster:** take SW3 offline, change it to Server mode, create/delete a few VLANs to push its revision number above SW1's, then reconnect it to the domain. Watch SW1 and SW2's VLAN databases get overwritten. Then explain, in writing, the exact sequence of `show vtp status` checks that would have prevented this in a real environment.
2. **Migrate the whole domain to VTP version 3** (if your platform supports it) and configure a **primary server** election. Explain how VTPv3's primary-server model specifically closes the "highest revision wins blindly" gap from Stretch Goal 1.
3. **Add a fourth switch (SW4) in VTP Transparent mode with its own local VLAN (60), attached off SW3.** Verify that VLAN 60 stays local to SW4 exactly the way VLAN 40 stayed local to SW2, and that SW4 still correctly relays SW1's advertisements further down the chain if a fifth switch were added.
4. **Convert this entire lab to VTP off (`vtp mode off` or set every switch to Transparent) and manually configure identical VLANs 10/20/30 on all three switches by hand.** Time how long it takes versus the VTP-based approach, and write 2–3 sentences on which approach you'd recommend for a 40-switch campus and why.

---

## 13. Self-Assessment

Before moving to the next lab, close this manual and try to answer without looking:

- [ ] Can you explain, from memory, why VLAN 40 never appears on SW1 or SW3?
- [ ] Can you explain why SW3 was refused when it tried to create VLAN 50?
- [ ] Can you state, without looking, what happens if a switch with a higher VTP revision number and a matching domain name is connected to a live VTP domain?
- [ ] Can you write the 3 commands needed to force a port into a hardened trunk (mode, encapsulation, DTP), from memory?
- [ ] Can you explain why VTP domain names are case-sensitive and what symptom a case mismatch produces?
- [ ] Can you explain the difference between a trunk's Administrative Mode and Operational Mode, and give an example of when they'd differ?
- [ ] Could you explain, in under 2 minutes, why many companies today choose not to run VTP Server mode in production, even though it's a valid exam topic?
- [ ] Can you name, without looking at Section 8, at least 4 of the 8 common mistakes?

If you answered "no" to more than two of these, re-do the lab from scratch (not by copy-pasting commands) before moving on.

---

## 14. Key Concepts Demonstrated

- **802.1Q trunking** — tagging frames with VLAN IDs to carry multiple VLANs over one physical link
- **DTP (Dynamic Trunking Protocol) and its risks** — auto-negotiated trunking as a security surface, closed by `nonegotiate`
- **VTP Server/Transparent/Client modes** — centralized VLAN propagation vs. local independence vs. read-only synchronization
- **VTP configuration revision number** — the single value that determines whose VLAN database "wins" in a domain
- **Native VLAN handling** — untagged trunk traffic and the risk of leaving it at the default
- **Access port hardening** — manual mode + DTP disabled as a VLAN-hopping mitigation
- **VLAN database propagation boundaries** — understanding exactly what does and doesn't cross a VTP domain

---

## 15. What I Learned

Building the same three-switch chain with three different VTP modes side by side made the propagation rules concrete in a way that reading about them never quite does — watching VLAN 40 exist on SW2 and nowhere else, while VLANs 10/20/30 show up everywhere, is a much stronger mental model than memorizing a table of "Server propagates, Transparent doesn't, Client receives but can't create."

The VTP revision number is the single most important (and most dangerous) concept in this lab. It's easy to configure VTP correctly and still get burned by it later, because the danger isn't a syntax error — it's an operational habit (checking `show vtp status` before trunking in any switch) that has to become automatic. This is also the strongest argument for why so many real networks now default to VTP Transparent mode everywhere, or skip VTP altogether in favor of configuration management tooling.

This lab is the foundation for what comes next:

- Spanning Tree Protocol (STP) and how it interacts with trunk topologies
- Router-on-a-Stick and SVI-based inter-VLAN routing (finally letting PC10-1 reach PC20-1)
- EtherChannel/link aggregation across trunk links
- Layer 3 switching and distribution-layer design

---

## 16. Skills Practiced

- 802.1Q trunk configuration and verification
- DTP negotiation control (`nonegotiate`) and its security rationale
- VTP domain, password, mode, and version configuration across a multi-switch topology
- VLAN database creation, propagation, and boundary verification
- Native VLAN and allowed-VLAN trunk hardening
- Access port hardening against VLAN hopping
- Structured VTP/trunk troubleshooting

---

## 17. GNS3 Lab

This lab has a companion GNS3 topology mirroring the design above, built automatically by [`GNS3/build_lab.py`](../GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| Switches (SW1, SW2, SW3) | Cisco 2960-24TT | Open vSwitch |
| End hosts (PC10-x, PC20-x, PC30-x) | Generic PC | Alpine Linux |

**Important limitation:** Open vSwitch does **not** implement Cisco's proprietary VTP or DTP protocols — it supports standard 802.1Q trunking and VLAN tagging, but has no concept of VTP domains, modes, or revision numbers, and no DTP negotiation to disable. This means the GNS3 build is useful for practicing **trunk port configuration syntax and muscle memory** (interface config, `switchport` commands generally, general L2 topology building), but it **cannot demonstrate actual VTP propagation behavior** — Sections 7 and 8's core lesson (VTP revision numbers, Server/Transparent/Client propagation differences) must be verified on real Cisco hardware or in Packet Tracer, not in this GNS3 build. See [`GNS3/README.md`](../GNS3/README.md) for details.
