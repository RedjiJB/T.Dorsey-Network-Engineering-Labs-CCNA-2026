# Day 10: VLAN Trunking (802.1Q) - Practice Lab

## Section 0: Before You Start

**Time Budget:** 120 minutes  
**Grading Rubric:** Excellent (90-100%): All trunk links configured with native VLAN 99, VLAN pruning, successful cross-switch same-VLAN ping. Good (80-89%): Trunk active but 1-2 configuration issues. Acceptable (70-79%): Trunk partially configured. Needs Work (<70%): Trunk not functional or major configuration gaps.

---

## Section 1: The Brief

**Client:** Horizon Financial Services (continued from Day 09)

The company is expanding Finance operations to a second office on the same building network. SW02 has been installed 50 meters away in Building B. You need to:

1. **Create a trunk link** between SW01 (Building A) and SW02 (Building B)
2. **Propagate all VLANs** (10, 20, 30, 99) across the trunk
3. **Change native VLAN** from 1 to 99 for security
4. **Implement VLAN pruning** to reduce unnecessary broadcast traffic
5. **Enable Finance expansion:** New Finance users in Building B can now access Finance VLAN 20
6. **Verify cross-switch connectivity** within same VLANs
7. **Document trunk design** with RFC 802.1Q reasoning

**Success Criteria:**
- Trunk link operational (show interfaces trunk shows "trunking")
- Native VLAN = 99 on both sides
- All 4 VLANs (10,20,30,99) listed in trunk allowed VLANs
- PC in VLAN 20 on SW01 can ping PC in VLAN 20 on SW02
- Configuration persists through reload

---

## Section 2: Design Your Trunk Architecture

**Considerations:**
1. Which ports on each switch should be trunk? (Gi0/1 vs Fa0/24?)
2. What native VLAN? (1, 99, or other?)
3. Which VLANs to allow? (all 4, or selective pruning?)
4. What about redundant trunks? (single link or dual for redundancy?)
5. Spanning Tree behavior? (passive acceptance or DTP negotiation?)

**Your Trunk Design (Fill in):**

```
Trunk Link:       SW01 Port: ___________  ↔  SW02 Port: ___________

Encapsulation:    802.1Q (dot1q)  [Circle: Yes/No]

Native VLAN:      _____ (justify: ____________________________________________)

Allowed VLANs:    _____, _____, _____, _____  (which 4?)

DTP Mode:         SW01: ____________  SW02: ____________
                  (on/auto/desirable/nonegotiate - which pair?)

Pruning Strategy: Prune to only necessary VLANs? [Yes/No] Why?
                  ________________________________________________________________
```

**Design Rationale:**
1. Why did you choose those specific ports as trunks?
2. Why is native VLAN 99 better than native VLAN 1?
3. How does VLAN pruning save bandwidth?

---

## Section 3: Implement Your Design - HOW-TO Walkthrough

### Step 1: Configure SW01 Trunk Port

**What You're Doing:** Converting SW01 Gi0/1 from shutdown state to active trunk, tagging all VLAN traffic.

```bash
# Enter switch console (if not already)
SW01> enable
SW01# configure terminal

# Navigate to trunk port
SW01(config)# interface gigabitethernet 0/1
SW01(config-if)# description Trunk to SW02 - RFC 802.1Q dot1q

# Set to trunk mode (must do first before encapsulation)
SW01(config-if)# switchport mode trunk

# Specify 802.1Q encapsulation
SW01(config-if)# switchport trunk encapsulation dot1q

# Set native VLAN to 99 (security - prevents VLAN 1 hopping)
SW01(config-if)# switchport trunk native vlan 99

# Configure pruning: only allow needed VLANs
SW01(config-if)# switchport trunk allowed vlan 10,20,30,99

# Bring port online
SW01(config-if)# no shutdown

# Exit interface mode
SW01(config-if)# exit

# Save configuration
SW01(config)# end
SW01# copy running-config startup-config
Destination filename [startup-config]? (press ENTER)
Building configuration...
[OK]
```

**Why Each Command:**
- `switchport mode trunk`: Opens port to carry multiple VLANs (required before anything else)
- `encapsulation dot1q`: Adds 802.1Q 4-byte headers to frames in this VLAN
- `native vlan 99`: Untagged traffic belongs to VLAN 99 (aligns with management)
- `allowed vlan`: VLAN pruning - only these 4 VLANs get tagged and forwarded
- `no shutdown`: Enables port (was in admin-down state if Gigabit port unused)

**Verify Step 1:**
```bash
SW01# show interfaces gigabitethernet 0/1 switchport

Name : Gi0/1
Switchport : Enabled
Administrative Mode : static trunk ✓
Operational Mode : trunk (waiting for SW02 config)
Administrative Trunking Encapsulation : dot1q ✓
Operational Trunking Encapsulation : native (may show "native" until SW02 matches)
Trunking Native Mode VLAN : 99 ✓
Trunking VLANs Enabled : 10,20,30,99 ✓
```

---

### Step 2: Configure SW02 Trunk Port (MUST MATCH SW01)

**Critical:** Both ends of trunk must have identical settings for trunk to become "trunking."

```bash
SW02> enable
SW02# configure terminal

SW02(config)# interface gigabitethernet 0/1
SW02(config-if)# description Trunk to SW01 - RFC 802.1Q dot1q

# Important: Do switchport mode trunk FIRST
SW02(config-if)# switchport mode trunk

# Then encapsulation
SW02(config-if)# switchport trunk encapsulation dot1q

# Native VLAN MUST match SW01 (both 99)
SW02(config-if)# switchport trunk native vlan 99

# Allowed VLANs MUST match SW01
SW02(config-if)# switchport trunk allowed vlan 10,20,30,99

SW02(config-if)# no shutdown
SW02(config-if)# exit

SW02(config)# end
SW02# copy running-config startup-config
```

**Verify Step 2:**
```bash
SW02# show interfaces trunk

Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      99 ✓

Port        Vlans allowed on trunk
Gi0/1       10,20,30,99 ✓
```

**Both sides should show Status = "trunking" now.**

---

### Step 3: Verify Trunk Propagation

**What's Happening:** VLANs defined on SW01 are now available on SW02 via trunk propagation (if using VTP or manual sync).

```bash
# Check if VLAN 20 now exists on SW02 (should, since it exists on SW01)
SW02# show vlan brief | include 20

20   Finance                       active    Gi0/1 ← NOW INCLUDES TRUNK

# Compare port listing before/after trunk
SW02# show vlan id 20

VLAN Name                             Status    Ports
---- -------------------------------- --------- ------ ------
20   Finance                          active    Fa0/1, Fa0/2, Gi0/1

(Gi0/1 now listed = trunk port showing VLAN 20 participation)
```

---

### Step 4: Test Cross-Switch Same-VLAN Connectivity

**What You're Testing:** Can PC in VLAN 20 on SW01 reach PC in VLAN 20 on SW02?

**Setup:**
- PC01: VLAN 20, SW01 Fa0/3, IP 192.168.20.10
- PC02: VLAN 20, SW02 Fa0/1, IP 192.168.20.11

**Ping Test (should succeed):**
```bash
PC01> ping 192.168.20.11

Sending 5, 100-byte ICMP Echoes to 192.168.20.11:
.....
Success rate is 100 percent (5/5), round-trip min/avg/max = 2/2/2 ms ✓
```

**If Ping Fails, Troubleshoot:**
1. Check both PCs are in VLAN 20: `show vlan id 20`
2. Check trunk is "trunking": `show interfaces trunk`
3. Check native VLAN matches: Both should show "Native vlan: 99"
4. Check VLAN 20 in allowed list: Both trunks should list VLAN 20
5. Ping SW02 from PC01 (test management connectivity): `ping 192.168.99.11`

---

## Section 4: Design Analysis - RFC 802.1Q & Trunk Architecture

**Answer These Questions:**

### Q1: Why Does 802.1Q Tagging Enable Trunking?

_Your Answer (explain what tagging does):_

```
802.1Q adds a 4-byte header to each frame on trunk links:

┌────────────────────────────────────────────────────────┐
│ Ethernet Frame Before Trunk (Access Link)              │
│ [DA][SA][EtherType][Payload][FCS]                      │
│ No VLAN information in frame                           │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ Ethernet Frame After Trunk (Trunk Link - 802.1Q)       │
│ [DA][SA][TPID:0x8100][PCP|DEI|VID][EtherType][...][FCS]
│ TPID tells switch "I have VID field"                   │
│ VID tells switch "I belong to VLAN X"                  │
│ This allows ONE physical link to carry multiple VLANs  │
└────────────────────────────────────────────────────────┘

Why This Matters:
- Before: 1 VLAN = 1 physical cable between switches (4 VLANs = 4 cables)
- After: 4 VLANs = 1 cable (with 802.1Q tagging inside)
- Cost Savings: Fewer cables, fewer ports needed
```

### Q2: Native VLAN Security Trade-off

_Your Answer (why change from 1 to 99?):_

```
Native VLAN = untagged traffic on trunk link

Native VLAN 1 (Default):
✓ Advantage: Compatible with older devices (ISL → 802.1Q migration)
✗ Risk: Attackers could exploit VLAN 1 for hopping attacks
✗ Problem: VLAN 1 is globally used (standard default), makes targeting easy

Native VLAN 99 (Best Practice):
✓ Advantage: Matches management VLAN, isolates management traffic
✓ Advantage: Prevents VLAN 1 default hopping attacks
✓ Advantage: Makes network harder to attack (non-standard VLAN)
✗ Disadvantage: Requires configuration on all switches (more work)

You Chose: Native VLAN = _____ because _______________________________
```

### Q3: Why Limit Allowed VLANs?

_Your Answer (explain pruning benefit):_

```
Without Pruning (switchport trunk allowed vlan all):
- Trunk carries all 4094 VLANs
- Even unused VLANs get flooded to both switches
- Wastes bandwidth (broadcast traffic for VLANs with no devices)
- Increases VLAN database size
- More configuration to manage

With Pruning (switchport trunk allowed vlan 10,20,30,99):
- Only specified VLANs tagged and forwarded
- VLANs 1-9, 11-19, 31-98, 100-4094 not allowed on trunk
- Reduces unnecessary broadcast traffic ~90%
- Simplifies troubleshooting (fewer VLANs to track)
- Improves switch performance (fewer MAC table entries)

Your Pruning Strategy: Allow only _____, _____, _____, _____ because:
_________________________________________________________________
```

---

## Section 5: Troubleshooting Exercises

### Scenario A: "Trunk Stuck in 'notconnect' State"

**Reported:** SW02 shows trunk status as "notconnect" even though link is connected.

**Your Troubleshooting:**

1. **Check both sides configured as trunk:**
   ```bash
   SW02# show interfaces gigabitethernet 0/1 switchport | include "Mode"
   Administrative Mode : dynamic auto ← NOT TRUNK!
   Operational Mode : ? (depends on other side)
   ```

2. **Problem Found:** SW02 Gi0/1 is in dynamic auto mode, not static trunk.

3. **Fix:** Force static trunk mode
   ```bash
   SW02# configure terminal
   SW02(config)# interface gigabitethernet 0/1
   SW02(config-if)# switchport mode trunk
   SW02(config-if)# end
   ```

4. **Verify:**
   ```bash
   SW02# show interfaces trunk
   Port        Status
   Gi0/1       trunking ✓
   ```

### Scenario B: "VLAN 40 Not Propagating Across Trunk"

**Reported:** Added VLAN 40 to SW01, but it doesn't appear on SW02.

**Your Troubleshooting:**

1. **Check VLAN exists on SW01:**
   ```bash
   SW01# show vlan id 40
   VLAN Name                             Status    Ports
   40   HR                               active    Fa0/8
   ```
   ✓ Exists

2. **Check if VLAN 40 in trunk allowed list:**
   ```bash
   SW01# show interfaces trunk | include "Vlans allowed"
   Port        Vlans allowed on trunk
   Gi0/1       10,20,30,99 ← VLAN 40 NOT LISTED
   ```

3. **Problem Found:** VLAN 40 not in pruning list.

4. **Fix:** Add VLAN 40 to allowed list
   ```bash
   SW01# configure terminal
   SW01(config)# interface gigabitethernet 0/1
   SW01(config-if)# switchport trunk allowed vlan 10,20,30,40,99
   SW01(config-if)# end
   
   SW02# configure terminal
   SW02(config)# interface gigabitethernet 0/1
   SW02(config-if)# switchport trunk allowed vlan 10,20,30,40,99
   SW02(config-if)# end
   
   ! Create VLAN 40 on SW02
   SW02# configure terminal
   SW02(config)# vlan 40
   SW02(config-vlan)# name HR
   SW02(config-vlan)# exit
   SW02(config)# end
   ```

5. **Verify:**
   ```bash
   SW02# show vlan id 40
   VLAN Name                             Status    Ports
   40   HR                               active    Gi0/1 ✓
   ```

---

## Section 6: Explain Your Trunk Design (Technical Memo)

**Write a Technical Memo addressing these points:**

1. **Trunk Link Selection:** Why did you choose Gi0/1 for trunk (vs. Fa0/24)?

2. **RFC 802.1Q Compliance:** Explain the 4-byte 802.1Q header structure and why it enables VLAN trunking.

3. **Native VLAN Strategy:** Why is native VLAN 99 (vs. 1) a security improvement?

4. **VLAN Pruning Rationale:** How does pruning to 10,20,30,99 reduce bandwidth vs. "allowed vlan all"?

5. **Scalability:** If you added 20 new VLANs next month, how would your trunk handle it? Would pruning list change?

6. **Redundancy Limitation:** What happens if the trunk link Gi0/1 fails? (This will be addressed in Day 12 with STP.)

---

**Lab Completion Time:** ~120 minutes  
**Estimated Difficulty:** Intermediate (CCNA Core)  
**Next Steps:** Day 11 (Inter-VLAN Routing) to enable communication between VLANs

