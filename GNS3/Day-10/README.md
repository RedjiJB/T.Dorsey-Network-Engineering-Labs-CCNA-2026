# GNS3 Day 10: VLAN Trunking (802.1Q) - Base & Field Topologies

## Prerequisites & Image Requirements

**Required Appliances:** Cisco Catalyst 2960, Alpine Linux nodes  
**Resource Requirements:** 4 GB RAM, 2+ CPU cores, 2 GB disk space

**Build Instructions:**
1. Import Catalyst 2960 images (same as Day 09)
2. Create GNS3 project: "Day-10-VLAN-Trunking"
3. Add SW01 and SW02 (reuse from Day 09 project)
4. Add trunk link: SW01 Gi0/1 ↔ SW02 Gi0/1
5. Start topology, verify both switches boot

---

## Base Topology Build

### Network Diagram

```
[PC01-PC07]──[SW01]─[Gi0/1]════════════[Gi0/1]─[SW02]
(VLANs)   (Fa0/1-7) [802.1Q Trunk]      (Fa0/1) (VLANs)
                  [Tagged]             [Tagged]
                  [VLAN 99 Native]     [VLAN 99 Native]
                  [Pruned: 10,20,30,99]
```

### Node Configuration

| Node | Type | Config |
|------|------|--------|
| SW01 | Catalyst 2960 | Gi0/1: Trunk (dot1q, native 99, allowed 10,20,30,99) |
| SW02 | Catalyst 2950 | Gi0/1: Trunk (dot1q, native 99, allowed 10,20,30,99) |
| PC01-PC07 | Alpine Linux | VLAN 10/20/30 access ports (Day 09 setup) |

### Trunk Configuration (Auto-Applied)

**SW01:**
```
interface gigabitethernet 0/1
 description Trunk to SW02
 switchport mode trunk
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
exit
```

**SW02:** (Mirror configuration)
```
interface gigabitethernet 0/1
 description Trunk to SW01
 switchport mode trunk
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
exit
```

---

## Field Variants

### Field-1: Dynamic Trunk Negotiation (DTP)

**Objective:** Configure trunk negotiation using Dynamic Trunking Protocol.

**Configuration:**
```
! SW01 - negotiate trunk (DTP desirable)
interface gigabitethernet 0/1
 switchport mode dynamic desirable
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
exit

! SW02 - accept negotiation (DTP auto)
interface gigabitethernet 0/1
 switchport mode dynamic auto
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
exit
```

**Outcome:** Trunk negotiated automatically (SW01 initiates, SW02 accepts).

---

### Field-2: Redundant Trunk Links (Dual Trunk)

**Objective:** Add second trunk for redundancy (preparation for Day 12 STP).

**Topology:**
```
         ┌─[SW01]─[Gi0/1]─────[Gi0/1]─[SW02]
[PC01-07]─┤       ├─[Gi0/2]─────[Gi0/2]─┤
         └─────────┘ (Primary & Secondary)
```

**Configuration:**
- SW01 Gi0/1 & Gi0/2: Both configured as trunks (same settings)
- SW02 Gi0/1 & Gi0/2: Both configured as trunks
- STP will select one as active, other as backup (Day 12)

---

### Field-3: Extended VLAN Range (1006-4094)

**Objective:** Use extended VLANs (VTP transparent mode required).

**Configuration:**
```
! Enable VTP transparent mode (required for extended VLANs)
SW01# vlan database
SW01(vlan)# vtp mode transparent
SW01(vlan)# exit

! Create extended VLAN
SW01# configure terminal
SW01(config)# vlan 2000
SW01(config-vlan)# name ExtendedVLAN
SW01(config-vlan)# exit

! Add to trunk
SW01(config)# interface gigabitethernet 0/1
SW01(config-if)# switchport trunk allowed vlan 10,20,30,99,2000
SW01(config-if)# end
```

---

### Field-4: VLAN Pruning Optimization

**Objective:** Test broadcast traffic reduction with pruning.

**Comparison:**
- Before: `switchport trunk allowed vlan all` (4094 VLANs)
- After: `switchport trunk allowed vlan 10,20,30,99` (4 VLANs)

**Monitoring:**
```
SW01# show interfaces gigabitethernet 0/1 switching

Protocol Switching Path Analysis for interface Gi0/1
IOS Software switching (Unknown) enabled/disabled
IP Switching for unknown ip protocols disabled
IP CEF switching enabled
...
```

---

### Field-5: Native VLAN Security Testing

**Objective:** Demonstrate VLAN hopping prevention with native VLAN 99.

**Attack Simulation (without exploit tools):**
1. Create PC with misconfigured double-tagged frame
2. Attempt to reach VLAN 1 management network
3. Verify rejection due to native VLAN mismatch

---

### Field-6: Trunk Link Monitoring & Verification

**Objective:** Use show commands to monitor trunk health.

**Commands:**
```
SW01# show interfaces trunk
SW01# show interfaces gigabitethernet 0/1 switchport
SW01# show vlan id 20 (verify VLAN across trunk)
SW01# show mac address-table vlan 20 (see MAC learning across trunk)
SW01# show port-channel summary (if using EtherChannel - Day 15)
```

---

### Field-7: Multi-Site Trunk Mesh

**Objective:** Three switches in triangle topology with multiple trunks.

**Topology:**
```
         ┌─[SW01]─[Gi0/1]────[Gi0/1]─[SW02]
[PC01-07]─┤       ├─[Gi0/2]────[Gi0/2]─┤
         └─[SW03]─[Gi0/1]───(SW03 link to SW01/SW02)
```

**Configuration:** Each pair of switches has trunk link(s), all with same VLAN settings.

---

## LAB_INDEX Cross-Reference

| Topic | Base | Field | Time |
|-------|------|-------|------|
| Basic trunking | ✓ | - | 30 min |
| 802.1Q tagging | ✓ | - | 15 min |
| Native VLAN config | ✓ | Field-5 | 20 min |
| VLAN pruning | ✓ | Field-4 | 25 min |
| DTP negotiation | - | Field-1 | 20 min |
| Redundant trunks | - | Field-2 | 45 min |
| Extended VLAN range | - | Field-3 | 30 min |
| Security hardening | - | Field-5 | 40 min |
| Multi-site design | - | Field-7 | 60 min |

---

## Command Reference

### Trunk Verification
```bash
show interfaces trunk
show interfaces gigabitethernet 0/1 switchport
show vlan brief
show vlan id <vlan#>
```

### Trunk Configuration
```bash
interface gigabitethernet 0/1
 switchport mode trunk
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
```

### Troubleshooting
```bash
debug spanning-tree all (see STP interactions)
show interfaces gigabitethernet 0/1 status
show mac address-table dynamic
```

---

**Last Updated:** August 30, 2026  
**GNS3 Version:** 2.2.30+  
**Complexity:** Base (Intermediate) | Field-1-7 (Advanced)

