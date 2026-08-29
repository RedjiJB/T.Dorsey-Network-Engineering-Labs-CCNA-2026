# Day 46 Lab Manual — Voice VLANs & Router-on-a-Stick (ROAS)

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure a single switch port to carry both untagged data traffic and 802.1Q-tagged voice traffic, then route between the two VLANs using Router-on-a-Stick |
| CCNA 200-301 Domains | 2.0 Network Access (VLANs, trunking, voice VLAN, 802.1Q), 1.0 Network Fundamentals (subinterfaces, inter-VLAN routing) |
| Prerequisites | Basic VLAN and trunk configuration, subnetting, IOS subinterface syntax |
| Estimated Time | 60–75 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

Most office desks have one Ethernet drop but two devices that need network access: a PC and an IP phone, daisy-chained through the phone. Voice VLANs solve this by letting a single access port carry two logically separate VLANs simultaneously — untagged data traffic and 802.1Q-tagged voice traffic — without needing two cable runs or two switch ports. This lab configures that exact setup and then uses frame inspection to *prove*, not just assert, which traffic is tagged and which isn't.

By the end of this lab you will be able to:

1. Configure `switchport access vlan` and `switchport voice vlan` on the same interface and explain what each does.
2. Explain, precisely, why PC traffic is untagged while phone traffic is 802.1Q-tagged on the identical physical port.
3. Configure a trunk between the switch and router carrying both VLANs.
4. Configure Router-on-a-Stick using dot1q subinterfaces to provide Layer 3 gateways for both VLANs.
5. Predict and verify — using frame-level inspection — where 802.1Q tags appear and where they don't in this topology.
6. Explain the operational reasons (QoS, security policy, DHCP scoping) for separating voice and data onto different VLANs in the first place.

## 2. Business Context

Every VoIP deployment in a modern office runs this exact pattern. Wiring a separate cable run for phones and PCs to every desk is expensive and often physically impractical in older buildings; voice VLANs let IT reuse the existing single drop per desk while still keeping voice traffic on its own logical network — which matters because voice traffic is latency-sensitive (jitter and delay cause audible call quality problems) and typically needs its own QoS priority, DHCP scope, and sometimes separate security policy from general user data traffic.

## 3. Topology Reference

| VLAN | Purpose | Network |
|---|---|---|
| VLAN 10 | Data | 192.168.10.0/24 |
| VLAN 20 | Voice | 192.168.20.0/24 |

| Device | Role |
|---|---|
| PC1, PC2 | Data endpoints |
| PH1, PH2 | IP Phones (PCs connect through the phones — daisy-chained) |
| SW1 | Access switch |
| R1 | Router providing Router-on-a-Stick (ROAS) |

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

Two separate `/24`s, one per VLAN — standard practice when data and voice are logically segmented, since they're different broadcast domains and therefore need different subnets by definition. Voice VLANs are conventionally numbered distinctly from data VLANs (here, 10 for data, 20 for voice) as a naming convention that makes intent obvious at a glance in `show vlan brief` output.

### 4.2 Manual Calculation Walkthrough

```
192.168.10.0/24 → 255.255.255.0 → 254 usable hosts (VLAN 10, data)
192.168.20.0/24 → 255.255.255.0 → 254 usable hosts (VLAN 20, voice)
```
Each VLAN is sized generously relative to actual phone/PC count today — standard convention, leaving room to grow without renumbering.

### 4.3 Address Table

| Interface | VLAN | Address |
|---|---|---|
| R1 F0/0.1 (subinterface) | 10 | 192.168.10.1/24 |
| R1 F0/0.2 (subinterface) | 20 | 192.168.20.1/24 |
| PC1, PC2 | 10 | 192.168.10.0/24 range |
| PH1, PH2 | 20 | 192.168.20.0/24 range |

## 5. Pre-Configuration Checklist

- [ ] Decide VLAN numbering (data vs. voice) before configuring any port — this lab uses VLAN 10/20
- [ ] Confirm the trunk between SW1 and R1 will need to carry BOTH VLANs — a common oversight is trunking only the data VLAN
- [ ] Know which physical router interface will host the ROAS subinterfaces, and confirm the physical interface itself is `no shutdown` (subinterfaces won't pass traffic if the parent is down)
- [ ] Plan to verify with `show interfaces switchport` (not just `show vlan brief`) to see the access/voice VLAN distinction clearly

## 6. Configuration Tasks

### 6.1 Configure access ports carrying both data and voice VLANs

```
SW1(config)# interface g1/0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport voice vlan 20
```
Repeat identically for `g1/0/3` (the second phone/PC pair). Mode: interface config. `switchport access vlan 10` sets the VLAN for **untagged** traffic on the port (the PC's traffic). `switchport voice vlan 20` is a special IOS construct that tells the switch to expect **802.1Q-tagged** traffic for VLAN 20 on the *same* physical port, and also signals Cisco IP phones (via CDP) which VLAN to tag their voice traffic with. Memory aid: "access vlan = default bucket for anything untagged; voice vlan = the one exception that's allowed to arrive tagged on an access port."

### 6.2 Configure the trunk toward R1

```
SW1(config)# interface g1/0/1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20
```
The link to R1 must carry both VLANs, since R1 needs to route between them — a common mistake is trunking only the data VLAN and forgetting voice traffic also needs to reach the router (or a voice gateway) at Layer 3.

### 6.3 Configure Router-on-a-Stick on R1

```
R1(config)# interface f0/0.1
R1(config-subif)# encapsulation dot1q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
R1(config)# interface f0/0.2
R1(config-subif)# encapsulation dot1q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
R1(config)# interface f0/0
R1(config-if)# no shutdown
```
Each subinterface is a logical construct on top of the single physical F0/0 — `encapsulation dot1q <vlan>` tells that subinterface which VLAN's tagged traffic to accept, and each gets its own IP address, becoming that VLAN's Layer 3 gateway. Memory aid: "one wire, many logical routers — each subinterface behaves like its own dedicated interface for its VLAN."

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show interfaces switchport` | SW1 | Confirm each port's access VLAN and voice VLAN assignment |
| `show interfaces trunk` | SW1 | Confirm VLANs 10 and 20 are both allowed across the trunk |
| `show ip interface brief` | R1 | Confirm both subinterfaces are up/up with correct addresses |
| `show interfaces f0/0.1` / `f0/0.2` | R1 | Confirm encapsulation and VLAN ID per subinterface |
| Frame inspection (Simulation Mode or packet capture) | PC1→PC2 ping, PH2→PH1 call | Directly observe presence/absence of an 802.1Q header |

### Expected Output Gallery

```
SW1# show interfaces switchport
Name: Gi1/0/2
Switchport: Enabled
Administrative Mode: static access
Access Mode VLAN: 10 (data)
Voice VLAN: 20 (voice)
```

```
SW1# show interfaces trunk
Port        Mode   Encapsulation  Status        Native vlan
Gi1/0/1     on     802.1q         trunking      1

Port        Vlans allowed on trunk
Gi1/0/1     10,20
```

```
R1# show ip interface brief
Interface              IP-Address       OK? Method Status   Protocol
FastEthernet0/0         unassigned      YES NVRAM  up       up
FastEthernet0/0.1       192.168.10.1    YES manual up       up
FastEthernet0/0.2       192.168.20.1    YES manual up       up
```

**Frame inspection results:**
- PC1 → PC2 ping: plain **Ethernet II** header — no 802.1Q tag observed entering the switch (untagged, access-VLAN traffic).
- PH2 → PH1 call: **Dot1q Header** observed with VLAN ID 20 — voice traffic is tagged by the phone itself before it reaches the switch.

## 8. Common Mistakes (80/20)

1. **Forgetting `switchport mode access`** — some switches default to dynamic trunking negotiation, which behaves unpredictably combined with a voice VLAN.
2. **Only allowing the data VLAN on the trunk to R1** — voice traffic never reaches its gateway, phones can't route calls off-subnet even though local switching still works.
3. **Assuming PC traffic is tagged because it "belongs to a VLAN"** — VLAN membership and 802.1Q tagging are not the same thing; untagged traffic on an access port is still assigned to a VLAN, just implicitly by the port's configuration, not by an explicit tag in the frame.
4. **Forgetting `no shutdown` on the physical parent interface** — subinterfaces stay down if the parent physical interface is administratively down, regardless of their own configuration.
5. **Skipping frame-level verification** — assuming tagging behavior instead of actually inspecting a captured frame is how this exact CCNA concept gets memorized wrong.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Is the access port correctly configured with both VLANs? | `show interfaces switchport` | Correct `switchport access vlan`/`switchport voice vlan` |
| 2 | Does the trunk allow both VLANs? | `show interfaces trunk` | Add missing VLAN to `switchport trunk allowed vlan` |
| 3 | Are both router subinterfaces up/up? | `show ip interface brief` | Check `no shutdown` on physical and subinterfaces, correct addressing |
| 4 | Does each subinterface have the correct VLAN encapsulation? | `show interfaces f0/0.1`/`f0/0.2` | Correct `encapsulation dot1q <vlan>` |
| 5 | Can a data host ping its own VLAN's gateway? | `ping 192.168.10.1` from PC1 | Isolate to VLAN 10 path specifically |
| 6 | Can a voice host reach its VLAN's gateway? | `ping 192.168.20.1` from a device on VLAN 20 | Isolate to VLAN 20 / voice VLAN path specifically |

## 10. Design Analysis

The alternative to voice VLANs — running separate cabling and switch ports for phones and PCs — doubles cabling/port cost and is often physically infeasible in existing buildings. The alternative to Router-on-a-Stick — a router with one physical interface per VLAN — doesn't scale past a handful of VLANs and wastes physical router ports. ROAS trades a small amount of throughput (all inter-VLAN traffic funnels through one physical link, a potential bottleneck at high volume) for dramatically simpler cabling and hardware requirements — which is why ROAS is common in small/branch deployments, while larger sites typically graduate to a Layer 3 switch doing inter-VLAN routing natively, removing the single-link bottleneck.

## 11. Real-World Parallel

Any office with desk-phone VoIP deployment (a huge fraction of enterprises, even ones that have also adopted softphones) runs exactly this pattern: one cable per desk, phone in the middle, PC daisy-chained through it, voice VLAN tagged by the phone, data VLAN untagged from the PC — CDP-based auto voice VLAN discovery (the phone learns its voice VLAN from the switch via CDP) is standard in real deployments and builds directly on the manual configuration shown here.

## 12. Stretch Goal

Add QoS: trust the 802.1Q priority bits (802.1p) coming from the voice VLAN, and configure a basic priority queue on the trunk so voice traffic is never delayed behind bulk data traffic — connecting this lab's tagging concept to its actual operational purpose.

## 13. Self-Assessment

- [ ] I can explain, precisely, why PC traffic is untagged and phone traffic is tagged on the identical physical port
- [ ] I can state what `switchport voice vlan` does that `switchport access vlan` alone would not
- [ ] I configured the trunk to R1 myself and confirmed both VLANs are allowed
- [ ] I configured ROAS subinterfaces and verified each is up with the correct VLAN encapsulation
- [ ] I directly inspected frames (or captures) myself and observed the Dot1q header on voice traffic but not data traffic

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Voice VLANs, `switchport access vlan` vs. `switchport voice vlan`, 802.1Q tagging, access vs. trunk ports, Router-on-a-Stick, dot1q subinterfaces, inter-VLAN routing, CDP's role in phone VLAN discovery.

**What I Learned:** VLAN membership and 802.1Q tagging are two separate concepts that are easy to conflate — a frame can belong to a VLAN (by port configuration) without ever carrying an explicit tag, and the type of link (access vs. trunk, data vs. voice) determines whether tagging actually happens, not the VLAN membership itself.

**Skills Practiced:** Data and voice VLAN configuration on a single access port, trunk configuration carrying multiple VLANs, Router-on-a-Stick subinterface configuration, inter-VLAN routing, frame-level traffic inspection, Layer 2/Layer 3 verification and troubleshooting.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-46/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using a VyOS router (ROAS), Open vSwitch switch, and Alpine Linux hosts (data endpoints; voice endpoints simulated since GNS3's free image set has no native Cisco IP phone equivalent — see the README for how to approximate 802.1Q-tagged traffic generation from a Linux host).
