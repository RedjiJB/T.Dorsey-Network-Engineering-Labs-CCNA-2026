# Day 16 Lab Manual — VLANs Part 1: Configuration and Inter-VLAN Routing

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Segment a single switch into three VLANs, address each VLAN as an independent subnet with the gateway on the last usable address, and provide inter-VLAN routing using one router interface per VLAN (no trunking yet). |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): VLANs, access ports, broadcast domains. Domain 1: subnetting for VLAN address planning. |
| **Prerequisites** | Day 01 (device basics), Day 15 (subnetting math) — this lab reuses the "gateway = last usable address" convention. |
| **Time Estimate** | 1.5 – 2.5 hours. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner-Intermediate) — the VLAN/subnet concepts are simple; the "one router interface per VLAN" design is the part students most often get backwards. |

---

## 1. Lab Overview

This lab segments a flat network into three VLANs — Engineering, HR, and Sales — each its own broadcast domain, each its own `/26` subnet carved from `10.0.0.0/24`. Because this is the first VLAN lab, inter-VLAN routing is done the simplest possible way: **one physical router interface per VLAN**, each cabled to its own switch access port set to that VLAN. Trunking and router-on-a-stick come in Day 17.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Explain what a VLAN is and why it creates a separate broadcast domain
- Subnet `10.0.0.0/24` into three `/26` blocks and assign the gateway to each subnet's last usable address
- Create and name VLANs on a switch, and assign access ports to them
- Configure one router interface per VLAN to provide inter-VLAN routing without trunking
- Verify that unicast traffic crosses VLANs (via the router) while broadcast traffic does not

---

## 2. Business Context

**Why would a real company do this?**

A small office with Engineering, HR, and Sales sitting on one flat switch has two problems: everyone hears everyone else's broadcast traffic (ARP requests, DHCP discovers) even though they have no business reason to, and there's no way to apply different security policy to HR (which handles sensitive employee data) versus Sales (which doesn't). VLANs solve both: each department becomes its own broadcast domain, and because each VLAN is also its own IP subnet, you can later apply ACLs, QoS, or firewall policy per department without re-cabling anything. This lab intentionally uses the simplest form of inter-VLAN routing (one router port per VLAN) because it's the version that makes "a VLAN is a subnet is a broadcast domain" concrete before adding the complexity of trunking.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2016%20Lab%20-%20VLANs%20(Part%201).png" alt="Day 16 VLAN Topology" width="800">
</p>

```text
PC1, PC2 (VLAN10) --\
PC3, PC4 (VLAN20) ----  SW1  ===(3 physical links)===  R1
PC5, PC6 (VLAN30) --/
```

R1 connects to SW1 with **three separate physical links** — one per VLAN — because this lab does not yet use trunking.

| Device | Role |
|---|---|
| SW1 | Access switch, hosts VLANs 10/20/30 |
| R1 | Router, one interface per VLAN |
| PC1–PC6 | End hosts, two per VLAN |

---

## 4. IP Addressing Plan

### 4.1 Why Each VLAN Is a `/26`

`10.0.0.0/24` is split into three equal `/26` blocks (64 addresses each, 62 usable) — a **fixed-length** split, unlike Day 15's VLSM plan, because all three departments have the same modest size requirement (2 hosts today, comfortable room to grow to 62 without redesigning).

### 4.2 Manual Calculation Walkthrough

**Step 1 — Splitting a /24 into three same-size blocks.** The nearest power-of-two split that gives ≥3 equal blocks is 4 blocks of `/26` each (a `/24` split into 4 always uses 2 extra bits: 24 + 2 = 26). Three of the four `/26` blocks are used; the fourth is spare for future growth.

```text
/26 = 11111111.11111111.11111111.11000000 = 255.255.255.192
Block size = 256 − 192 = 64
```

**Step 2 — Lay out the three subnets on 64-address boundaries:**

| VLAN | Subnet | Range | Broadcast |
|---|---|---|---|
| 10 (Engineering) | 10.0.0.**0**/26 | .1–.62 | .63 |
| 20 (HR) | 10.0.0.**64**/26 | .65–.126 | .127 |
| 30 (Sales) | 10.0.0.**128**/26 | .129–.190 | .191 |

(10.0.0.192/26 is unused, reserved for a future VLAN.)

**Step 3 — Worked example, VLAN 20 (10.0.0.64/26):**

```text
Network address:    10.0.0.64    (all 6 host bits = 0)
First usable host:  10.0.0.65    (network + 1)
Last usable host:   10.0.0.126   (broadcast − 1)
Broadcast address:  10.0.0.127   (all 6 host bits = 1 → 64 + 63)
```

**Gateway convention:** every VLAN's gateway is the **last usable address** in its subnet (`.62`, `.126`, `.190`) rather than the more common "first usable" — a deliberate choice in this lab series so you practice both conventions and don't assume gateways are always `.1`.

### 4.3 Full Device Address Table

| Device | Interface / VLAN | IP Address | Mask | Connects To |
|---|---|---|---|---|
| PC1 | VLAN10 | 10.0.0.1 | 255.255.255.192 | SW1 (access, VLAN10) |
| PC2 | VLAN10 | 10.0.0.2 | 255.255.255.192 | SW1 (access, VLAN10) |
| R1 | Gi0/0 (VLAN10) | 10.0.0.62 | 255.255.255.192 | SW1 (VLAN10 uplink) |
| PC3 | VLAN20 | 10.0.0.65 | 255.255.255.192 | SW1 (access, VLAN20) |
| PC4 | VLAN20 | 10.0.0.66 | 255.255.255.192 | SW1 (access, VLAN20) |
| R1 | Gi0/1 (VLAN20) | 10.0.0.126 | 255.255.255.192 | SW1 (VLAN20 uplink) |
| PC5 | VLAN30 | 10.0.0.129 | 255.255.255.192 | SW1 (access, VLAN30) |
| PC6 | VLAN30 | 10.0.0.130 | 255.255.255.192 | SW1 (access, VLAN30) |
| R1 | Gi0/2 (VLAN30) | 10.0.0.190 | 255.255.255.192 | SW1 (VLAN30 uplink) |

**Default gateways:** PC1/PC2 → 10.0.0.62; PC3/PC4 → 10.0.0.126; PC5/PC6 → 10.0.0.190.

---

## 5. Pre-Configuration Checklist

1. Place SW1, R1, and PC1–PC6 to match the topology.
2. Cable R1 to SW1 with **three separate physical links** (not one trunk).
3. Cable each PC to an access port on SW1.
4. Have the address table above open before starting.

---

## 6. Configuration Tasks

### 6.1 R1 — one interface per VLAN

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description VLAN10 gateway
R1(config-if)#ip address 10.0.0.62 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/1
R1(config-if)#description VLAN20 gateway
R1(config-if)#ip address 10.0.0.126 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
R1(config)#interface gigabitEthernet 0/2
R1(config-if)#description VLAN30 gateway
R1(config-if)#ip address 10.0.0.190 255.255.255.192
R1(config-if)#no shutdown
R1(config-if)#exit
```

> **Why three interfaces instead of one trunked interface?** Because this lab specifically teaches the *non-trunked* model of inter-VLAN routing — each physical link carries exactly one VLAN's traffic, so the router doesn't need to understand 802.1Q tagging at all. Each interface is simply a normal Layer 3 interface that happens to be the gateway for one VLAN's subnet. **Memory aid:** "no trunk, no tag, no problem — one wire, one VLAN, one subnet."

### 6.2 SW1 — create VLANs

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW1
SW1(config)#vlan 10
SW1(config-vlan)#name Engineering
SW1(config-vlan)#exit
SW1(config)#vlan 20
SW1(config-vlan)#name HR
SW1(config-vlan)#exit
SW1(config)#vlan 30
SW1(config-vlan)#name Sales
SW1(config-vlan)#exit
```

> **Mode:** `vlan <id>` enters VLAN configuration mode from global config — a distinct mode from interface config. The switch maintains a VLAN database (visible with `show vlan brief`) independent of which ports are assigned to which VLAN; creating the VLAN and assigning ports to it are two separate steps.

### 6.3 SW1 — assign access ports

```text
SW1(config)#interface range fastEthernet 0/1 - 2
SW1(config-if-range)#switchport mode access
SW1(config-if-range)#switchport access vlan 10
SW1(config-if-range)#no shutdown
SW1(config-if-range)#exit
SW1(config)#interface range fastEthernet 0/3 - 4
SW1(config-if-range)#switchport mode access
SW1(config-if-range)#switchport access vlan 20
SW1(config-if-range)#no shutdown
SW1(config-if-range)#exit
SW1(config)#interface range fastEthernet 0/5 - 6
SW1(config-if-range)#switchport mode access
SW1(config-if-range)#switchport access vlan 30
SW1(config-if-range)#no shutdown
SW1(config-if-range)#exit
```

> `switchport mode access` forces the port to never negotiate a trunk. `switchport access vlan <id>` assigns it to that VLAN's broadcast domain — untagged frames in, untagged frames out, only ever exchanged with other ports in the same VLAN (or routed out via the uplink to R1). `interface range` lets you configure multiple contiguous ports with one command block instead of repeating it per port.

### 6.4 SW1 — uplink ports to R1

Each of SW1's three uplink ports toward R1 must be an **access** port in the matching VLAN (not a trunk — R1 has no trunking configured in this lab):

```text
SW1(config)#interface fastEthernet 0/23
SW1(config-if)#description Uplink to R1 Gi0/0 (VLAN10)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 10
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/22
SW1(config-if)#description Uplink to R1 Gi0/1 (VLAN20)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 20
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/21
SW1(config-if)#description Uplink to R1 Gi0/2 (VLAN30)
SW1(config-if)#switchport mode access
SW1(config-if)#switchport access vlan 30
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

### 6.5 PC Addressing

Configure each PC per Section 4.3's table via **Desktop → IP Configuration**.

### 6.6 Save

```text
SW1#copy running-config startup-config
R1#copy running-config startup-config
```

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| SW1 | `show vlan brief` | VLANs 10/20/30 active, correct ports listed under each |
| SW1 | `show interfaces status` | Access ports connected, correct VLAN column |
| R1 | `show ip interface brief` | All three interfaces `up/up` with correct IPs |
| PC1–PC6 | `ipconfig` | Correct IP/mask/gateway |
| Any PC | `ping <own gateway>` | Local VLAN connectivity |
| Any PC | `ping <PC in different VLAN>` | Inter-VLAN routing via R1 |

### 7.1 Expected Output Gallery

**`SW1# show vlan brief`**

```text
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/7, Fa0/8, ... Fa0/20
10   Engineering                      active    Fa0/1, Fa0/2, Fa0/23
20   HR                               active    Fa0/3, Fa0/4, Fa0/22
30   Sales                            active    Fa0/5, Fa0/6, Fa0/21
```

**`R1# show ip interface brief`**

```text
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.62       YES manual up                    up
GigabitEthernet0/1         10.0.0.126      YES manual up                    up
GigabitEthernet0/2         10.0.0.190      YES manual up                    up
```

**`PC1> ping 10.0.0.65`** (VLAN10 → VLAN20, inter-VLAN)

```text
Pinging 10.0.0.65 with 32 bytes of data:

Reply from 10.0.0.65: bytes=32 time=1ms TTL=127
Reply from 10.0.0.65: bytes=32 time=1ms TTL=127
Reply from 10.0.0.65: bytes=32 time=1ms TTL=127
Reply from 10.0.0.65: bytes=32 time=1ms TTL=127

Ping statistics for 10.0.0.65:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

TTL=127 (one hop lower than a fresh-boot default of 128) confirms the packet was routed through R1, not switched locally — a same-VLAN ping would show TTL=128 (or whatever the source OS's default is, unchanged).

### 7.2 Broadcast Domain Verification

Send a broadcast-generating request (e.g., an ARP request or a `ping 10.0.0.63` to VLAN10's broadcast address) from a VLAN10 host and confirm — via a `debug` or packet capture in Packet Tracer's simulation mode — that no VLAN20 or VLAN30 host receives it. This is the concrete proof that VLANs are separate broadcast domains: unicast crosses via routing, broadcast does not cross at all.

---

## 8. Common Mistakes (the 80/20)

1. **Cabling R1 to SW1 with fewer than three links**, then wondering why only one VLAN routes. This lab specifically requires **one physical link per VLAN** — there is no trunk to carry all three over one wire yet.
2. **Forgetting to assign the uplink ports (SW1 side) to the matching VLAN.** A router interface with a perfect IP address still won't route for a VLAN if SW1's corresponding uplink port is left in VLAN 1 (the default) instead of VLAN 10/20/30.
3. **Setting the gateway to the first usable address out of habit**, instead of the last usable address this lab specifically requires (`.62`, `.126`, `.190`).
4. **Creating the VLAN but never assigning any port to it** — `vlan 10` / `name Engineering` alone does nothing to actual traffic until `switchport access vlan 10` is applied to real ports.
5. **Leaving PCs' switch ports in VLAN 1** because the port-assignment commands were only run on the "obviously VLAN" ports and the uplinks/PC ports were overlooked.
6. **Confusing `switchport access vlan <id>` (assigns the port) with `vlan <id>` (creates the VLAN in the database)** — both are required, and the exam tests whether you know these are two separate steps.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC can't reach its own gateway | Port not in the right VLAN, or interface down | `show vlan brief`, `show interfaces status` | Re-assign port to correct VLAN, `no shutdown` |
| 2 | PC reaches its gateway but not another VLAN | R1 interface for that VLAN is down or misaddressed | `show ip interface brief` on R1 | Fix IP/mask or `no shutdown` the interface |
| 3 | R1 interface is up but inter-VLAN ping still fails | SW1's uplink port for that VLAN isn't in the matching VLAN | `show vlan brief` | Correct `switchport access vlan` on the uplink port |
| 4 | `show vlan brief` shows the VLAN with 0 ports | Ports were never assigned, or assigned to the wrong VLAN entirely | `show running-config interface <id>` | Re-apply `switchport access vlan <id>` |
| 5 | Broadcast reaches hosts in a different VLAN | Ports incorrectly bridged into the same VLAN, or trunk misconfigured | `show vlan brief`, `show interfaces trunk` | Re-verify no unintended trunk exists between VLANs |

---

## 10. Design Analysis

**Why one router interface per VLAN instead of trunking from day one?** Pedagogically, it isolates the *routing* concept (a router forwards between subnets) from the *trunking* concept (a single link can carry multiple VLANs' tagged traffic) so each is learned independently before combining them in Day 17's router-on-a-stick. Operationally, it also mirrors a real (if unusual) design choice: dedicating a physical NIC per VLAN avoids 802.1Q entirely, trading router port count for simplicity — a legitimate trade-off in small deployments where the router has spare interfaces and administrators want to avoid trunk misconfiguration risk.

**Why gateway = last usable address here (vs. first usable in other labs)?** No technical reason favors one over the other — but seeing both conventions across this course prevents you from hard-coding an assumption ("gateways are always `.1`") that real networks won't always honor.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a small office's IT admin has a router with enough spare interfaces and wants to avoid trunk configuration entirely for a first VLAN rollout — exactly this lab's design.
- ...you're troubleshooting "my computer can't see the file server in another department" and the root cause turns out to be a switch port never assigned to the right VLAN — Common Mistake #5, constantly seen in the field.
- ...an auditor asks you to prove that Engineering's broadcast traffic never reaches HR — the broadcast domain verification in Section 7.2 is literally that proof.

---

## 12. Stretch Goal

1. Add a fourth VLAN (40, "Guest") using the fourth `/26` block (`10.0.0.192/26`) and a fourth physical link from R1. Follow the same gateway convention.
2. Convert this lab's design to trunking on a single R1↔SW1 link without changing any IP addressing — what commands change, and what stays the same? (Full answer arrives in Day 17.)
3. Predict, then verify, what happens to VLAN10↔VLAN20 connectivity if you shut down only the SW1↔R1 VLAN20 uplink port while leaving R1's Gi0/1 interface itself up.

---

## 13. Self-Assessment

- [ ] Can you explain why VLANs are separate broadcast domains, in one sentence?
- [ ] Can you list, from memory, the two separate steps required before a switch port actually carries VLAN 10 traffic (VLAN creation vs. port assignment)?
- [ ] Can you subnet a `/24` into equal `/26` blocks and identify the network/broadcast/last-usable address of each, by hand?
- [ ] Can you explain why this lab needs three physical links between R1 and SW1 instead of one?
- [ ] Could you predict, before testing, which pings in a VLAN topology will succeed and which need a router in the path?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** VLAN creation and naming, access port assignment, one-interface-per-VLAN inter-VLAN routing, broadcast domain isolation, gateway addressing convention (last usable).

**What I Learned:** VLANs create separate broadcast domains, and a router can provide inter-VLAN routing using one physical interface per VLAN without any trunking at all. Gateway placement is a convention, not a technical requirement — this lab's "last usable address" choice is just as valid as "first usable," provided every device consistently agrees on it. Before configuring the router interfaces, pings between VLANs failed entirely; after adding all three interfaces and assigning gateways, inter-VLAN communication succeeded while broadcast traffic stayed correctly contained inside its own VLAN.

**Skills Practiced:** VLAN creation and naming, router interface configuration for each VLAN, switch port VLAN assignment, PC IP and gateway configuration, inter-VLAN connectivity verification, broadcast domain behavior analysis, TTL interpretation.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md). R1 maps to VyOS, SW1 to Open vSwitch, PC1–PC6 to Alpine Linux.
