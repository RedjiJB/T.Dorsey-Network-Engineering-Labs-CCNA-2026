# Day 14: VLAN Troubleshooting & Advanced Trunking

## 0. Metadata
- **Objective:** Diagnose and resolve VLAN and trunking issues in a multi-switch topology
- **Relevant RFC/Standards:** IEEE 802.1Q, IEEE 802.1D (STP interactions)
- **Prerequisites:** Days 1-13 (VLAN basics, ROAS, trunking)
- **Estimated Time:** 120 minutes
- **Difficulty:** Intermediate-Advanced
- **Hardware Required:** 2-3 switches, 1 router, 4-6 PCs

## 1. Overview
Real-world VLAN deployments experience connectivity issues: misconfigured trunks, native VLAN mismatches, STP topology changes. This lab teaches systematic troubleshooting: from "I can't ping" to root cause identification.

## 2. Business Context
- Downtime costs: $5,600/minute for average business
- VLAN misconfiguration is the #1 Layer 2 failure mode
- IT must resolve connectivity issues within SLA (15-30 minutes)
- Preventative monitoring and documentation reduce MTTR (Mean Time To Repair)

## 3. Topology Reference
```
         [Router R1]
            |
         [SW1 (core)]
        /    |    \
    [SW2] [SW3]  [SW4]
    /  |    |  \
  PC1 PC2  PC3 PC4
  (V10)(V10)(V20)(V20)
```

## 4. IP Addressing Plan
| Device | VLAN | IP | Subnet | Role |
|--------|------|----|----|------|
| PC1 | 10 | 10.0.10.10 | 255.255.255.0 | Test client |
| PC2 | 10 | 10.0.10.20 | 255.255.255.0 | Test client |
| PC3 | 20 | 10.0.20.10 | 255.255.255.0 | Test client |
| PC4 | 20 | 10.0.20.20 | 255.255.255.0 | Test client |

## 5. Pre-Config Checklist
- [ ] All switches have VLANs 10, 20 created
- [ ] All trunks configured between switches
- [ ] ROAS configured on router
- [ ] Baseline connectivity tested (you'll break it intentionally)

## 6. Configuration

### 6.1 Core Switch (SW1)
```
Switch# conf t
Switch(config)# vlan 10
Switch(config-vlan)# name ENGINEERING
Switch(config)# vlan 20
Switch(config-vlan)# name SALES

! Trunk to all neighbors
Switch(config)# int range g0/1-4
Switch(config-if-range)# switchport mode trunk
Switch(config-if-range)# switchport trunk encapsulation dot1Q
Switch(config-if-range)# switchport trunk allowed vlan 1,10,20
Switch(config-if-range)# no shutdown
Switch(config-if-range)# exit

Switch(config)# end
```

### 6.2 Access Switches (SW2, SW3, SW4)
```
! Same VLAN creation
Switch# conf t
Switch(config)# vlan 10
Switch(config)# vlan 20

! Trunk to core
Switch(config)# int g0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20
Switch(config-if)# no shutdown

! Access ports for PCs
Switch(config)# int f0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# end
```

## 7. Verification & Expected Output

### 7.1 Verify VLAN Exists on All Switches
```
Switch# show vlan brief | include (10|20)
 10   ENGINEERING   active   f0/1
 20   SALES         active   f0/3

(Should appear on all three switches)
```

### 7.2 Verify Trunk Status
```
Switch# show int g0/1 switchport | include (Encapsulation|Access List|Trunking|Allowed)
Encapsulation Negotiation: On
Operational Mode: trunk
Allowed Vlans: 1,10,20
Trunking VLANs Enabled: 1,10,20
```

### 7.3 Verify Connectivity
```
PC1> ping 10.0.10.20 (same VLAN, should succeed)
PC1> ping 10.0.20.10 (different VLAN, test ROAS)
```

## 8. Common Mistakes
1. **Trunk mode mismatch:** One side set to trunk, other to auto (fails in some IOS)
2. **Native VLAN mismatch:** Default is VLAN 1; if routed subinterface uses VLAN 1, conflict arises
3. **VLANs not allowed on trunk:** Admin forgets to add VLAN to allowed list
4. **Encapsulation mismatch:** One side dot1Q, other side ISL (legacy)
5. **Wrong spanning-tree priority:** Root placed at access layer instead of core

## 9. Troubleshooting Guide

### 9.1 "Ping within VLAN fails"
```
! Verify VLAN membership
Switch# show vlan | include <vlan_id>

! Check access port configuration
Switch# show int f0/1 switchport | include (Access VLAN|Operational Mode)

! Test MAC address learning
Switch# show mac address-table | include <vlan_id>
```

### 9.2 "Ping across VLANs fails"
```
! Check ROAS subinterfaces
Router# show int g0/0.10 | include (up|encapsulation)

! Verify trunk allows VLAN
Switch# show int g0/1 switchport | include Allowed

! Check routing table
Router# show ip route
```

### 9.3 "Trunk shows negotiation fail"
```
! Check both sides explicitly
Switch1# show int g0/1 switchport | include Mode
Switch2# show int g0/2 switchport | include Mode

! Both must show "Mode: trunk" (not "dynamic auto")
! Fix: set mode to "trunk" explicitly on BOTH sides
```

## 10. Design Analysis
**Hierarchical VLAN Topology:**
- Core layer: All VLANs present, all trunks converge
- Distribution/Access: Subset of VLANs, trunks to core
- Reduces VLAN sprawl; centralizes routing

## 11. Real-World Parallel
**Fortune 500 Network Architecture:**
- Data center switches trunk 100+ VLANs to aggregation layer
- Access layer switches trunk only their local VLANs to distribution
- Any VLAN change follows Change Control Board review
- Monitoring tools alert on unexpected VLAN additions

## 12. Stretch Goals
1. Simulate STP topology change; verify VLAN recovery
2. Configure VLAN access control list (VACL) to restrict inter-VLAN traffic
3. Monitor link utilization across trunks with "show int [port] statistics"
4. Design a redundant core (two-core VLAN architecture) with load balancing

## 13. Self-Assessment (BSL Scale)
- **BSL-1:** Identify one misconfigured trunk via show commands
- **BSL-2:** Fix three VLAN issues (missing VLAN, wrong access port, trunk mismatch)
- **BSL-3:** Explain native VLAN role and STP interaction
- **BSL-4:** Design VLAN topology for 30-person office with two departments
- **BSL-5:** Troubleshoot asymmetric routing scenario (packet goes one way, reply stuck)
- **BSL-6:** Propose VLAN migration strategy (merge two VLAN schemes) with zero downtime
- **BSL-7:** Design and defend VLAN scalability plan for 10,000-host network

## 14. Key Concepts
- **VLAN Mismatch:** Access port in wrong VLAN, or trunk missing VLAN
- **Native VLAN:** Untagged traffic on trunk; usually VLAN 1 (configure identical on both sides)
- **Trunk Negotiation:** 802.1Q, ISL, DTP negotiation protocol (manual mode safest)
- **STP Interaction:** Spanning tree runs per VLAN (PVST+); topology change flushes MAC tables

## 15. What I Learned
- VLAN issues manifest as Layer 2 loop symptoms or silent packet loss
- Verification commands form a checklist: show vlan → show int switchport → show mac-addr-table
- Preventative: Document all VLAN assignments and trunk configurations

## 16. Skills Practiced
- ✓ Configuring and verifying VLAN membership
- ✓ Setting up trunks with allowed VLAN lists
- ✓ Troubleshooting step-by-step using show commands
- ✓ Isolating failures to Layer 2 (switch) vs. Layer 3 (router)

## 17. GNS3 Lab Info
**Topology:** 3x 2960 Switches, 1x 2911 Router, 4x VPCs
**Time:** 60 minutes
**Intentional Faults to Fix:**
1. One trunk in "dynamic auto" mode (fix by manual trunk)
2. One access port in wrong VLAN (fix by switchport access vlan command)
3. One VLAN missing from trunk allowed list (fix by adding to allowed vlans)
