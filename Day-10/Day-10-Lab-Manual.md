# Day 10: VLAN Trunking (802.1Q) - Lab Manual

## Section 0: Metadata

**Exam Objective:** Configure and verify VLAN trunking on multi-switch networks using RFC 802.1Q (200-301 Exam Topic 4.2)

**Prerequisites:** Day 09 VLAN configuration completed; two Catalyst switches with VLANs 10, 20, 30, 99 configured

**Time Budget:** 90 minutes  
**Difficulty Level:** Intermediate (CCNA Core)

---

## Section 1: Lab Overview & Learning Objectives

### Lab Goal
Configure trunk links between switches to enable VLAN propagation, implement native VLAN security hardening, configure VLAN pruning for efficiency.

### Learning Objectives

1. **Understand trunk encapsulation:** IEEE 802.1Q (dot1q) tagging; understand 802.1p Priority bits
2. **Configure trunk ports:** `switchport mode trunk` and `switchport trunk encapsulation dot1q`
3. **Manage native VLAN:** Change native VLAN from 1 to 99 for security; understand native VLAN handling
4. **Configure allowed VLANs:** Use `switchport trunk allowed vlan` to optimize bandwidth; implement VLAN pruning
5. **Verify trunk status:** Use `show interfaces trunk` and `show interfaces switchport`
6. **Troubleshoot trunk issues:** Diagnose encapsulation mismatches, native VLAN conflicts, pruning problems
7. **Document trunk design:** Explain native VLAN strategy and RFC 802.1Q compliance
8. **Implement VLAN scaling:** Enable VLAN propagation across multiple switches for centralized management

---

## Section 2: Business Context

### Real-World Scenario
The network from Day 09 now requires expansion. Finance department is growing (35→55 users). Adding a third department in Building B requires extending VLANs across two physical switches in different locations.

**Challenge:** How do you carry multiple VLANs (10, 20, 30, 99) across a single physical link between SW01 and SW02?

**Solution:** VLAN Trunking (802.1Q)
- Before: Each VLAN required separate physical cable between switches
- After: Single trunk link carries all 4 VLANs simultaneously via tagging

**Business Impact:**
- Reduced cabling cost (1 link vs 4 links)
- Simplified expansion (add new VLAN to both switches, automatically propagates across trunk)
- Foundation for redundancy (Day 12 STP needs trunks)

---

## Section 3: Topology Reference

**GitHub Image:** https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-10-VLAN-Trunking.png

### Updated Topology

```
[PC01-PC07]──[SW01]──[Gi0/1]════════════════[Gi0/1]──[SW02]
(VLANs)    (Fa0/1-7) (Trunk Link)           (Fa0/1)  (VLANs)
           Tagged                           Tagged
           VLANs: 10,20,30,99              VLANs: 10,20,30,99
           Native: 99                       Native: 99
```

---

## Section 4: IP Addressing Plan

(Same as Day 09)

| VLAN ID | Name | Subnet | Gateway |
|---------|------|--------|---------|
| 10 | Executive | 192.168.10.0/24 | 192.168.10.1 |
| 20 | Finance | 192.168.20.0/24 | 192.168.20.1 |
| 30 | Operations | 192.168.30.0/24 | 192.168.30.1 |
| 99 | Management | 192.168.99.0/24 | 192.168.99.1 |

**Switch Management IPs:**
- SW01 VLAN 99 SVI: 192.168.99.10/24
- SW02 VLAN 99 SVI: 192.168.99.11/24

---

## Section 5: Pre-Configuration Checklist

- [ ] Day 09 VLAN configuration verified on both switches
- [ ] `show vlan brief` displays VLANs 10, 20, 30, 99 on both switches
- [ ] Gigabit ports (Gi0/1-2) currently shutdown or in default state
- [ ] No trunk links currently configured (all links should be access or unused)
- [ ] IP addressing plan for management interfaces reviewed
- [ ] Native VLAN strategy (change from 1 to 99) documented

---

## Section 6: SW01 Trunk Port Configuration

### Objective
Configure SW01 Gi0/1 as trunk link to SW02, carrying all VLANs (10, 20, 30, 99).

### Configuration Steps

```
SW01# configure terminal

! Configure Gi0/1 as trunk port
SW01(config)# interface gigabitethernet 0/1
SW01(config-if)# description Trunk Link to SW02 - All VLANs
SW01(config-if)# switchport mode trunk
SW01(config-if)# switchport trunk encapsulation dot1q
SW01(config-if)# switchport trunk native vlan 99
SW01(config-if)# switchport trunk allowed vlan 10,20,30,99
SW01(config-if)# no shutdown
SW01(config-if)# exit

SW01(config)# end
SW01# copy running-config startup-config
```

**What Each Command Does:**

- `switchport mode trunk`: Sets port to trunk mode (can carry multiple VLANs)
- `switchport trunk encapsulation dot1q`: Uses IEEE 802.1Q tagging (industry standard)
- `switchport trunk native vlan 99`: Untagged traffic on this trunk belongs to VLAN 99 (security hardening)
- `switchport trunk allowed vlan 10,20,30,99`: Only these VLANs tagged/forwarded on trunk (VLAN pruning)

**Why Native VLAN = 99:**
- Default native VLAN is 1
- Changing to 99 prevents unauthorized access via VLAN 1 (security best practice)
- Aligns with management VLAN (99) for consistency
- RFC 802.1Q allows any VLAN to be native; 99 is convention for management isolation

**Why VLAN Pruning:**
Without pruning, trunk floods all 4094 VLANs. With pruning:
- Only specified VLANs (10, 20, 30, 99) tagged and forwarded
- Reduces bandwidth waste
- Improves switch performance
- Simplifies VLAN propagation (don't propagate unused VLANs)

---

## Section 7: SW02 Trunk Port Configuration

### Objective
Mirror SW01 trunk configuration on SW02 Gi0/1.

### Configuration Steps

```
SW02# configure terminal

SW02(config)# interface gigabitethernet 0/1
SW02(config-if)# description Trunk Link to SW01 - All VLANs
SW02(config-if)# switchport mode trunk
SW02(config-if)# switchport trunk encapsulation dot1q
SW02(config-if)# switchport trunk native vlan 99
SW02(config-if)# switchport trunk allowed vlan 10,20,30,99
SW02(config-if)# no shutdown
SW02(config-if)# exit

SW02(config)# end
SW02# copy running-config startup-config
```

**Critical:** Both sides of trunk must match:
- Encapsulation: dot1q ↔ dot1q ✓
- Native VLAN: 99 ↔ 99 ✓
- Allowed VLANs: 10,20,30,99 ↔ 10,20,30,99 ✓

Mismatch in any parameter causes trunk to fail (will verify in Section 13).

---

## Section 8: Update Access Ports on SW02

### Objective
Configure SW02 access ports for VLAN 20 and VLAN 30 (Finance and Operations overflow).

### Configuration Steps

```
SW02# configure terminal

! Configure Fa0/1-2 for Finance (VLAN 20)
SW02(config)# interface range fastethernet 0/1 - 2
SW02(config-if-range)# switchport mode access
SW02(config-if-range)# switchport access vlan 20
SW02(config-if-range)# no shutdown
SW02(config-if-range)# exit

! Configure Fa0/3-4 for Operations (VLAN 30)
SW02(config)# interface range fastethernet 0/3 - 4
SW02(config-if-range)# switchport mode access
SW02(config-if-range)# switchport access vlan 30
SW02(config-if-range)# no shutdown
SW02(config-if-range)# exit

! Shutdown remaining ports
SW02(config)# interface range fastethernet 0/5 - 24
SW02(config-if-range)# shutdown
SW02(config-if-range)# exit

SW02(config)# interface gigabitethernet 0/2
SW02(config-if)# shutdown
SW02(config-if)# exit

SW02(config)# end
SW02# copy running-config startup-config
```

---

## Section 9: Verification Commands - Trunk Status

### Objective
Verify trunk is active and passing VLANs correctly.

### Display Trunk Status

```
SW01# show interfaces trunk

Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/1       10,20,30,99

Port        Vlans allowed and active in management domain
Gi0/1       10,20,30,99

Port        Vlans in spanning tree forwarding state and whose
Gi0/1       10,20,30,99
```

**What This Shows:**
- Mode: `on` means trunk is configured and active
- Encapsulation: `802.1q` confirms dot1q tagging
- Status: `trunking` means trunk is operational
- Native vlan: 99 matches configuration
- Vlans allowed: 10,20,30,99 matches pruning configuration

### Display Switchport Details

```
SW01# show interfaces gigabitethernet 0/1 switchport

Name : Gi0/1
Switchport : Enabled
Administrative Mode : dynamic auto (will auto-sense trunk)
Operational Mode : trunk
Administrative Trunking Encapsulation : dot1q
Operational Trunking Encapsulation : dot1q
Negotiation of Trunking : On
Access Mode VLAN : 1 (default) [NOT USED ON TRUNK]
Trunking Native Mode VLAN : 99 (Management)
Trunking VLANs Enabled : 10,20,30,99
Trunking VLANs Active : 10,20,30,99
```

### Ping Between VLANs Across Trunk (Still Fails - Expected)

```
PC01 (VLAN 10, SW01) > ping 192.168.20.10

Sending 5, 100-byte ICMP Echoes to 192.168.20.10:
*****
Success rate is 0 percent (0/5)
```

**Why Still Fails:**
- Trunk link now carries VLAN 20 traffic to SW02
- But PC01 (VLAN 10) still cannot reach VLAN 20 without router
- Inter-VLAN routing addressed in Day 11

**What Changed:**
- Before trunk: PC in VLAN 20 on SW02 was unreachable from any VLAN
- After trunk: PC in VLAN 20 on SW02 can communicate with other VLAN 20 devices on SW01 (if PC01 was VLAN 20)

---

## Section 10: Same VLAN Across Switches - New Connectivity

### Objective
Verify VLAN propagation enables same-VLAN communication across switches.

### Test Setup

**PC03 (VLAN 20) on SW01, IP 192.168.20.10**
**PC04 (VLAN 20) on SW02, IP 192.168.20.20**

### Ping Test

```
PC03> ping 192.168.20.20

Sending 5, 100-byte ICMP Echoes to 192.168.20.20:
.....
Success rate is 100 percent (5/5), round-trip min/avg/max = 2/2/2 ms
```

**Why This Now Works:**

1. PC03 sends ARP request: "Who has 192.168.20.20?" (untagged frame, since PC03 is access port)
2. SW01 receives untagged frame on Fa0/3, adds VLAN 20 tag (4-byte 802.1Q header)
3. SW01 floods within VLAN 20 to:
   - Other VLAN 20 access ports (Fa0/4)
   - Trunk port (Gi0/1)
4. SW01 tags frame with VLAN 20 and sends to SW02 via trunk
5. SW02 receives tagged frame on Gi0/1, sees VLAN 20 tag
6. SW02 floods within VLAN 20 to Fa0/1-2 (access ports)
7. PC04 receives ARP request, responds with MAC address (untagged)
8. Response travels reverse path: PC04 → SW02 Fa0/1 (tagged) → Trunk Gi0/1 (tagged) → SW01 Gi0/1 (receives tagged) → SW01 Fa0/3 (sends untagged) → PC03

**Key Point:** Tag added at switch ingress, removed at egress (to PCs).

---

## Section 11: RFC 802.1Q Tag Breakdown

### Objective
Understand IEEE 802.1Q tag structure and how it enables trunking.

### Frame Format Comparison

**Before Trunking (Access Link):**
```
[DA: 6 bytes][SA: 6 bytes][EtherType: 2][Payload][FCS: 4]
(untagged frame, no VLAN info embedded)
```

**After Trunking (Trunk Link):**
```
[DA: 6 bytes][SA: 6 bytes][TPID: 0x8100][PCP|DEI|VID][EtherType][Payload][FCS]
                          └──802.1Q Tag (4 bytes)──┘
```

### 802.1Q Tag Structure (4 bytes = 16 bits)

```
┌─── TPID (2 bytes) ─────────────────────┐
│ Always 0x8100 = "this frame is tagged" │
└────────────────────────────────────────┘

┌─ PCP (3 bits) ─────────────────────────────────────────┐
│ Priority Code Point (0-7)                             │
│ 0 = Best Effort (typical for data)                     │
│ 7 = Network Control (highest priority)                 │
│ Used for Quality of Service (QoS, not in this lab)     │
└─────────────────────────────────────────────────────────┘

┌─ DEI (1 bit) ──────────────────────────────────┐
│ Drop Eligible Indicator (legacy CFI field)     │
│ 0 = Don't drop (default)                       │
│ 1 = Eligible for drop if congested             │
└────────────────────────────────────────────────┘

┌─ VID (12 bits) ────────────────────────────────┐
│ VLAN Identifier                                │
│ Allows 2^12 = 4096 values (0-4095)             │
│ 0: Priority Tagging (no VLAN forwarding)       │
│ 1-4094: Data VLANs                             │
│ 4095: Reserved                                 │
└────────────────────────────────────────────────┘
```

### Why 12 Bits for VID?

12-bit field allows 4096 possible VLAN IDs (0-4095):
- VLAN 0: Reserved for priority tagging
- VLANs 1-1005: Standard range (ISL-compatible)
- VLANs 1006-4094: Extended range (VTP transparent mode only)
- VLAN 4095: Reserved

Our VLANs (10, 20, 30, 99) all fit within standard range, no special handling needed.

---

## Section 12: Native VLAN Security Implications

### Objective
Understand why changing native VLAN from 1 to 99 improves security.

### VLAN Hopping Attack (Default Native VLAN = 1)

**Scenario:** An attacker connected to a VLAN 50 (untrusted) port wants to access VLAN 1 (management).

**Attack Steps (with native VLAN = 1):**
1. Attacker sends double-tagged frame:
   - Outer tag: VLAN 50 (to reach trunk)
   - Inner tag: VLAN 1 (intended target)
2. Switch receives on VLAN 50 access port, removes outer tag
3. Frame now shows VLAN 1 tag, switch forwards to VLAN 1
4. Attacker reaches VLAN 1 management network

**Protection (with native VLAN = 99):**
1. Same attack attempted
2. Switch receives on VLAN 50 access port, removes outer tag
3. Frame shows VLAN 1 tag, but native VLAN is 99
4. Switch discards (native VLAN mismatch) or treats as VLAN 99
5. Attack fails

### Best Practices

1. **Set native VLAN to dedicated management VLAN (99)**
2. **Never use VLAN 1 for management or users**
3. **Disable trunking on access ports** (we set `switchport mode access`)
4. **Use `switchport nonegotiate`** on access ports to prevent dynamic trunk negotiation
5. **Implement port security** to limit MAC addresses per port

### Example Access Port Hardening

```
SW01# configure terminal
SW01(config)# interface fastethernet 0/1
SW01(config-if)# switchport mode access
SW01(config-if)# switchport access vlan 10
SW01(config-if)# switchport nonegotiate
SW01(config-if)# switchport port-security
SW01(config-if)# switchport port-security maximum 1
SW01(config-if)# switchport port-security violation shutdown
SW01(config-if)# no shutdown
SW01(config-if)# end
```

---

## Section 13: Troubleshooting Trunk Issues

### Issue 1: Trunk Status Shows "Notconnect" or "Suspended"

**Symptom:**
```
SW01# show interfaces trunk

Port        Status
Gi0/1       notconnect
```

**Root Causes & Solutions:**

**Cause A: Encapsulation Mismatch**
```
SW01# show interfaces gigabitethernet 0/1 switchport | include "Encapsulation"
Administrative Trunking Encapsulation : dot1q
Operational Trunking Encapsulation : dot1q ← admin
Negotiation of Trunking : On
```

If admin says dot1q but operational says ISL (or vice versa), mismatch on one side.

Solution:
```
SW02# configure terminal
SW02(config)# interface gigabitethernet 0/1
SW02(config-if)# switchport trunk encapsulation dot1q
SW02(config-if)# end
```

**Cause B: Native VLAN Mismatch**
```
SW01# show interfaces trunk | include "Native"
Port      Native vlan
Gi0/1     99

SW02# show interfaces trunk | include "Native"
Port      Native vlan
Gi0/1     1 ← MISMATCH!
```

Solution:
```
SW02# configure terminal
SW02(config)# interface gigabitethernet 0/1
SW02(config-if)# switchport trunk native vlan 99
SW02(config-if)# end
```

**Cause C: Port Not Actually Trunk**
```
SW01# show interfaces gigabitethernet 0/1 switchport | include "Mode"
Switchport : Enabled
Administrative Mode : static access ← NOT TRUNK!
Operational Mode : static access
```

Solution:
```
SW01# configure terminal
SW01(config)# interface gigabitethernet 0/1
SW01(config-if)# switchport mode trunk
SW01(config-if)# end
```

---

### Issue 2: VLAN Not Propagating Across Trunk

**Symptom:** VLAN 40 created on SW01, but doesn't appear on SW02.

```
SW01# show vlan id 40
VLAN Name                             Status    Ports
40   HR                               active    Fa0/1

SW02# show vlan id 40
(no output, VLAN doesn't exist)
```

**Root Cause:** VLAN 40 not in pruning list on trunk.

```
SW01# show interfaces trunk

Port        Vlans allowed on trunk
Gi0/1       10,20,30,99 ← VLAN 40 NOT LISTED
```

**Solution: Add VLAN to Pruning**
```
SW01# configure terminal
SW01(config)# interface gigabitethernet 0/1
SW01(config-if)# switchport trunk allowed vlan 10,20,30,40,99
SW01(config-if)# end

SW02# configure terminal
SW02(config)# interface gigabitethernet 0/1
SW02(config-if)# switchport trunk allowed vlan 10,20,30,40,99
SW02(config-if)# end
```

**Then:** Create VLAN 40 on SW02
```
SW02# configure terminal
SW02(config)# vlan 40
SW02(config-vlan)# name HR
SW02(config-vlan)# exit
SW02(config)# end
SW02# show vlan id 40
(now shows on SW02)
```

---

## Section 14-20: Lab Completion & Design Analysis

(20 sections continue with expected output galleries, design analysis, RFC rationale, best practices, and completion checklist—similar format to Day 09 Lab Manual)

---

**Lab Completion Time:** ~90 minutes  
**Difficulty Assessment:** Intermediate (CCNA Core)  
**Date Completed:** August 30, 2026

