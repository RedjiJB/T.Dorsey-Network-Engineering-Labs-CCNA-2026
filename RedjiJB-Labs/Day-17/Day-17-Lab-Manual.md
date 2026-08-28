# Day 17 Lab Manual — VLANs Part 2: Trunking, Native VLAN Mismatch, and Router-on-a-Stick

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Replace Day 16's "one link per VLAN" design with a single trunked link carrying all VLANs, configure trunk allowed-VLAN lists, recognize a native VLAN mismatch, and implement router-on-a-stick (ROAS) using subinterfaces for inter-VLAN routing. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): trunking, 802.1Q, native VLAN, DTP, router-on-a-stick. |
| **Prerequisites** | Day 16 (VLAN creation, access ports, non-trunked inter-VLAN routing). |
| **Time Estimate** | 2 – 2.5 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — trunk allowed-VLAN syntax and native VLAN mismatches are where most students get tripped up. |

---

## 1. Lab Overview

This lab takes the same three VLANs from Day 16 and collapses R1↔SW1's three physical links into a **single trunk**, then adds a second switch (SW2) connected to SW1 by its own trunk. Instead of one router interface per VLAN, R1 now uses **subinterfaces** (one per VLAN, all sharing one physical link) — this is router-on-a-stick. Along the way, you'll deliberately observe a **native VLAN mismatch**, a very common real-world misconfiguration that CDP will warn about but that doesn't necessarily take the trunk down.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Configure a trunk port and verify its operational state with `show interfaces trunk`
- Explain and configure trunk allowed-VLAN lists (`switchport trunk allowed vlan add`)
- Recognize a native VLAN mismatch from CDP output and explain the risk it introduces
- Configure router-on-a-stick using 802.1Q subinterfaces, one per VLAN
- Verify VLAN-to-VLAN connectivity across a two-switch trunked topology

---

## 2. Business Context

**Why would a real company do this?**

Day 16's one-link-per-VLAN design doesn't scale — a company with 20 VLANs would need 20 router ports and 20 switch uplink ports just for inter-VLAN routing. Trunking solves this by carrying every VLAN's traffic, tagged with an 802.1Q header identifying which VLAN each frame belongs to, over a single physical (or logical, in the case of an EtherChannel) link. Router-on-a-stick applies the same idea to the router side: one physical interface, split into logical subinterfaces, each handling one VLAN's traffic. This is exactly how a real branch office scales VLANs without buying a switch port or router port for every department — and the native VLAN mismatch scenario in this lab is deliberately included because it's one of the most common "the network is flaky but nothing is technically down" tickets a junior engineer will ever see.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2017%20Lab%20-%20VLANs%20(Part%202).png" alt="Day 17 Topology" width="800">
</p>

```text
PC2, PC3 (VLAN10) --\
                      SW2 ===trunk=== SW1 ===trunk=== R1 (subinterfaces)
PC5 (VLAN20) --------/
PC4 (VLAN30) -- SW1 (direct access port)
```

**Devices:** SW1, SW2, R1, PC2, PC3, PC4, PC5

**VLANs and subnets** (reused from Day 16's plan):

| VLAN | Name | Subnet | Devices |
|---|---|---|---|
| 10 | Engineering | 10.0.0.0/26 | PC2, PC3 (on SW2) |
| 20 | Sales | 10.0.0.64/26 | PC5 (on SW2) |
| 30 | HR | 10.0.0.128/26 | PC4 (on SW1) |

---

## 4. IP Addressing Plan

This lab reuses Day 16's `/26` addressing exactly — the VLAN subnets and gateway convention (last usable address) don't change; only *how* the router reaches each VLAN changes (subinterfaces instead of physical interfaces). See Day 16 Section 4 for the full derivation; the relevant addresses are:

| VLAN | Gateway (R1 subinterface) | Mask |
|---|---|---|
| 10 | 10.0.0.62 | 255.255.255.192 |
| 20 | 10.0.0.126 | 255.255.255.192 |
| 30 | 10.0.0.190 | 255.255.255.192 |

**Why this matters conceptually:** the IP plan is identical to Day 16's — this lab proves that trunking and ROAS are purely a *Layer 2/framing* change (how VLAN traffic physically gets from switch to router) with **zero impact** on the Layer 3 addressing plan already designed. This is a useful thing to internalize: subnetting design and trunk design are independent decisions.

---

## 5. Pre-Configuration Checklist

1. Place SW1, SW2, R1, and PC2/PC3/PC4/PC5 per the topology.
2. Cable SW1↔SW2 and SW1↔R1 as single links (trunks, not multiple parallel links like Day 16).
3. Cable PC2/PC3 and PC5 to SW2; PC4 directly to SW1.
4. Have both the Day 16 addressing table and this lab's VLAN-to-switch mapping open.

---

## 6. Configuration Tasks

### 6.1 SW2 — access ports

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW2
SW2(config)#interface fastEthernet 0/1
SW2(config-if)#switchport mode access
SW2(config-if)#switchport access vlan 20
SW2(config-if)#no shutdown
SW2(config-if)#exit
SW2(config)#interface range fastEthernet 0/2 - 3
SW2(config-if-range)#switchport mode access
SW2(config-if-range)#switchport access vlan 10
SW2(config-if-range)#no shutdown
SW2(config-if-range)#exit
```

> **Verification habit to build now:** run `show vlan brief` immediately after any access port assignment, before moving to the next step — it's the fastest way to catch a wrong VLAN assignment before it compounds with later trunk configuration.

### 6.2 SW1 — verify baseline trunk, then configure allowed VLANs

**Step 1 — check what's already trunking:**

```text
SW1#show interfaces trunk
```

```text
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1001
Port        Vlans allowed and active in management domain
Gi0/1       1,10,30
```

> Notice VLAN 20 is missing from "allowed and active" — this is expected until Step 3 explicitly adds it. Also notice the native VLAN here is `1001`, not the default `1` — flag this for Step 3, it's the source of this lab's native VLAN mismatch.

**Step 2 — attempt to bring the trunk up cleanly and observe the CDP warning:**

```text
SW1(config)#interface gigabitEthernet 0/1
SW1(config-if)#switchport mode trunk
SW1(config-if)#exit
```

```text
%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1001), with SW2 GigabitEthernet0/1 (1)
```

> **What this means:** SW1's native VLAN on this trunk is `1001`, but SW2's is the default `1`. The **native VLAN** is the one VLAN on a trunk whose frames are sent *untagged* — both ends must agree on which VLAN that is, or a frame SW1 thinks is untagged-VLAN-1001 traffic gets interpreted by SW2 as untagged-VLAN-1 traffic (and vice versa), silently leaking traffic between VLANs that were never supposed to talk to each other. **This is a security-relevant misconfiguration, not just a cosmetic warning** — it's the mechanism behind "VLAN hopping" via double-tagging attacks. Notice: **the trunk stays up anyway.** CDP warns; it doesn't block. This is exactly why a working trunk is not proof of a correctly configured trunk.

**Step 3 — allowed-VLAN list on SW1's trunk to R1:**

```text
SW1(config)#interface gigabitEthernet 0/2
SW1(config-if)#switchport mode trunk
SW1(config-if)#switchport trunk allowed vlan 10,20,30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

> `switchport trunk allowed vlan <list>` **replaces** the allowed list outright; `switchport trunk allowed vlan add <list>` **adds** to whatever's already allowed without removing anything. Mixing these up is Common Mistake #2 below — using the non-`add` form when you meant to add one VLAN will silently strip every other VLAN off the trunk.

### 6.3 SW2 — trunk allowed VLANs (using the `add` form, incrementally)

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

**Verify:**

```text
SW2#show interface trunk
```

```text
Port        Vlans allowed and active in management domain
Gi0/1       10,20
Gi0/2       10,20,30
```

### 6.4 R1 — router-on-a-stick subinterfaces

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/0.10
R1(config-subif)#encapsulation dot1Q 10
R1(config-subif)#ip address 10.0.0.62 255.255.255.192
R1(config-subif)#exit
R1(config)#interface gigabitEthernet 0/0.20
R1(config-subif)#encapsulation dot1Q 20
R1(config-subif)#ip address 10.0.0.126 255.255.255.192
R1(config-subif)#exit
R1(config)#interface gigabitEthernet 0/0.30
R1(config-subif)#encapsulation dot1Q 30
R1(config-subif)#ip address 10.0.0.190 255.255.255.192
R1(config-subif)#exit
```

> **Mode:** each subinterface (`Gi0/0.10`, `.20`, `.30`) is a logical interface layered on top of the single physical `Gi0/0`. `encapsulation dot1Q <vlan>` tells the router "frames tagged with this VLAN ID, arriving on the physical interface, belong to this subinterface" — without it, the subinterface has no way to know which tagged traffic is its own. Only the **physical** interface needs `no shutdown`; subinterfaces come up automatically once the parent is up and correctly encapsulated. **Memory aid:** "one stick (physical link), many branches (subinterfaces) — this is what makes it 'router-on-a-stick.'"

### 6.5 SW1 — access port for PC4 (VLAN30, direct on SW1)

```text
SW1(config)#interface fastEthernet 0/5
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| SW1, SW2 | `show interfaces trunk` | Mode `trunk`, status `trunking`, correct allowed VLANs |
| SW1, SW2 | `show vlan brief` | Access ports in correct VLANs |
| SW1, SW2 | `show interfaces <id> switchport` | Administrative/Operational mode, native VLAN, trunking encapsulation |
| SW1, SW2 | `show cdp neighbors detail` | Confirms/denies native VLAN mismatch |
| R1 | `show ip interface brief` | All three subinterfaces `up/up` |
| Any PC | `ping <cross-VLAN host>` | Full ROAS path works |

### 7.1 Expected Output Gallery

**`SW1# show interfaces trunk`**

```text
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1001
Gi0/2       on           802.1q         trunking      1

Port        Vlans allowed and active in management domain
Gi0/1       1,10,30
Gi0/2       10,20,30
```

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES unset  up                    up
GigabitEthernet0/0.10      10.0.0.62       YES manual up                    up
GigabitEthernet0/0.20      10.0.0.126      YES manual up                    up
GigabitEthernet0/0.30      10.0.0.190      YES manual up                    up
```

The physical interface itself shows `unassigned` — it carries no IP of its own; only its subinterfaces do. This is correct and expected for ROAS.

**`PC2> ping 10.0.0.63`** (testing gateway reachability across the trunk + ROAS path)

```text
Pinging 10.0.0.63 with 32 bytes of data:

Reply from 10.0.0.63: bytes=32 time=2ms TTL=254

Ping statistics for 10.0.0.63:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

---

## 8. Common Mistakes (the 80/20)

1. **Ignoring the CDP native VLAN mismatch warning because "the trunk still works."** It works right up until someone crafts a double-tagged frame or a device gets plugged into the wrong native VLAN's untagged path — this is a real security gap, not noise.
2. **Using `switchport trunk allowed vlan <list>` when `add` was intended**, wiping out every previously allowed VLAN on that trunk without realizing it.
3. **Forgetting `encapsulation dot1Q <vlan>` on a subinterface**, or setting the wrong VLAN number — the subinterface will never come up correctly and traffic for that VLAN silently has nowhere to go.
4. **Forgetting `no shutdown` on the physical parent interface** — subinterfaces cannot come up if their physical parent is down, even if each subinterface's own configuration is perfect.
5. **Mismatched allowed-VLAN lists between the two ends of a trunk** — SW1 allowing 10,20,30 but SW2 only allowing 10,20 silently blackholes VLAN 30 traffic across that specific link, with no error on either side.
6. **Confusing access port config (`switchport access vlan`) with trunk config (`switchport trunk allowed vlan`)** on the same interface — a port can't sensibly have both; decide access vs. trunk first, and configuring the wrong one for a port's actual role (e.g., trunk syntax on what should be an access port) leaves the port not doing what you think it's doing.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Trunk shows `desirable`/negotiating instead of `trunking` | DTP hasn't settled, or one side is access-only | `show interfaces trunk` | Explicitly set `switchport mode trunk` on both ends |
| 2 | One VLAN's traffic doesn't cross a specific trunk link | VLAN missing from that link's allowed list | `show interfaces trunk` (check "Vlans allowed") | `switchport trunk allowed vlan add <vlan>` |
| 3 | CDP reports native VLAN mismatch | Native VLAN differs between trunk ends | `show cdp neighbors detail`, `show interfaces trunk` | `switchport trunk native vlan <id>` to match on both ends |
| 4 | R1 subinterface never comes up | Physical parent interface shutdown, or `encapsulation` missing/wrong VLAN | `show ip interface brief`, `show running-config interface <subif>` | `no shutdown` on physical, correct `encapsulation dot1Q` |
| 5 | PC pings its own gateway but not a cross-VLAN host | Missing VLAN from an intermediate trunk's allowed list | `show interfaces trunk` on every switch in the path | Add the missing VLAN to every trunk between source and R1 |
| 6 | Access port shows `trunking` unexpectedly | DTP negotiated a trunk because the port wasn't explicitly locked to access | `show interfaces <id> switchport` | `switchport mode access` explicitly, disable DTP with `switchport nonegotiate` |

---

## 10. Design Analysis

**Why trunk instead of Day 16's one-link-per-VLAN design?** Trunking decouples the number of VLANs from the number of physical ports needed — critical the moment a company has more than a handful of VLANs. **Why ROAS instead of a Layer 3 switch (Day 18's topic)?** ROAS is cheaper when you already have spare router capacity and don't have (or don't yet need) a multilayer switch — but every VLAN's traffic now funnels through one physical link and one router CPU, a real bottleneck at scale, which is exactly the limitation Day 18's multilayer switching design solves. **Why does the CDP native VLAN mismatch matter even though the trunk stays up?** Because "up" and "correctly and securely configured" are different claims — a trunk can pass all your test pings while still leaking VLAN 1 traffic across a mismatched native boundary that an attacker (or a misconfigured device) could exploit.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...your company outgrows Day 16's "one router port per VLAN" model the moment it adds an 8th VLAN and runs out of router interfaces — trunking + ROAS (or Day 18's L3 switch) is the next step every growing network takes.
- ...a "the network feels weird sometimes" ticket turns out to be exactly this lab's native VLAN mismatch — everything mostly works, so it goes unnoticed for months until someone runs `show cdp neighbors detail` during an unrelated troubleshooting session.
- ...you're auditing trunk configuration across a campus and find one link where someone used `switchport trunk allowed vlan 20` (replace) instead of `add 20`, silently cutting off three other VLANs that used to work fine over that link.

---

## 12. Stretch Goal

1. Deliberately mismatch the native VLAN back to a non-default value on both SW1 and SW2's trunk, this time matching them to each other but differing from VLAN 1 — does CDP still warn? Why or why not?
2. Add a fourth VLAN and a fourth subinterface on R1 without touching any existing configuration — confirm it comes up and routes correctly.
3. Convert one of SW1's trunk ports to `switchport nonegotiate` and explain, from `show interfaces switchport` output, what specifically changes about DTP behavior on that port.

---

## 13. Self-Assessment

- [ ] Can you explain what a native VLAN is and why both trunk ends must agree on it?
- [ ] Can you state the difference between `switchport trunk allowed vlan <list>` and `switchport trunk allowed vlan add <list>` from memory?
- [ ] Can you write the three-line subinterface config block (encapsulation + ip address) for a VLAN, from `configure terminal`, without looking?
- [ ] Can you explain why the physical interface in ROAS shows `unassigned` for its IP and why that's correct?
- [ ] Could you explain the security risk of a native VLAN mismatch to someone non-technical in two sentences?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** 802.1Q trunking, trunk allowed-VLAN lists, native VLAN and its mismatch risk, DTP, router-on-a-stick subinterfaces.

**What I Learned:** The important lesson from this lab is not just what to configure, but what to verify after configuring it. `show vlan brief` is the fastest proof that access ports landed in the right VLAN. `show interfaces trunk` tells you both mode and allowed VLANs on one line. CDP native VLAN mismatch messages are useful, but a trunk can stay up despite them — "working" and "correctly configured" are not the same claim. Router-on-a-stick isn't done until the subinterfaces are `up/up` and a cross-VLAN ping actually succeeds.

**Skills Practiced:** Trunk configuration and verification, allowed-VLAN list management, native VLAN mismatch recognition via CDP, router-on-a-stick subinterface configuration, end-to-end inter-VLAN ping validation across a two-switch topology.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md). R1 maps to VyOS, SW1/SW2 to Open vSwitch, PCs to Alpine Linux.
