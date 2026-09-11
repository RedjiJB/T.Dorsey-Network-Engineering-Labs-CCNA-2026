# Day 15: VLAN Design & Multi-VLAN Topology Implementation

## 0. Metadata
- **Objective:** Design and implement a multi-VLAN switched network; plan VLANs for organizational structure
- **Relevant RFC/Standards:** IEEE 802.1Q (VLAN tagging), IEEE 802.1D (spanning tree)
- **Prerequisites:** Days 1-14 (basic switching, VLAN basics, trunk configuration)
- **Estimated Time:** 120 minutes
- **Difficulty:** Intermediate
- **Hardware Required:** 3-4 switches, 1 router, 6-8 PCs
- **Key Concepts:** VLAN design, scalability, documentation, access/trunk port planning

## 1. Overview
Real-world VLAN design requires planning for growth, security, and performance. This lab covers creating a multi-VLAN topology that mirrors organizational structure (departments) and scales efficiently.

## 2. Business Context
- Organizations use VLANs to isolate traffic by department (Finance, Engineering, Sales, HR)
- Each VLAN gets its own broadcast domain and security policy
- Proper design prevents broadcast storms and improves network security
- Documentation is critical for troubleshooting and staff handoff

## 3. Topology Reference
```
        [R1: ROAS]
           |
    [SW1: Core]
    /  |  |  \
 [SW2][SW3][SW4][SW5]
 (access)
   |
 [PC1-PC2]
 (VLAN 10, 20, 30, 40)
```

## 4. IP Addressing Plan
| VLAN | Department | Subnet | Router Gateway | Broadcast |
|------|-----------|--------|----------------|-----------|
| 10 | Engineering | 10.0.10.0/24 | 10.0.10.1 | 10.0.10.255 |
| 20 | Finance | 10.0.20.0/24 | 10.0.20.1 | 10.0.20.255 |
| 30 | Sales | 10.0.30.0/24 | 10.0.30.1 | 10.0.30.255 |
| 40 | HR | 10.0.40.0/24 | 10.0.40.1 | 10.0.40.255 |

## 5. Pre-Config Checklist
- [ ] All switches powered on and accessible via console
- [ ] Trunk links identified and cabled between core and access switches
- [ ] Access links identified (where PCs will connect)
- [ ] IP connectivity verified between switches
- [ ] VLAN IDs documented (10, 20, 30, 40)

## 6. Configuration

### 6.1 Design Phase (Before Configuration)
```
Document the design:
1. Create VLAN assignment table (VLAN ID, name, department, subnet)
2. Identify trunk links (core to access)
3. Identify access ports per switch (which VLAN for each port)
4. Plan router subinterfaces (one per VLAN)
5. Create network diagram showing VLAN distribution
```

### 6.2 Core Switch (SW1) Configuration
```
Switch> en
Switch# conf t

! Create all VLANs
Switch(config)# vlan 10
Switch(config-vlan)# name ENGINEERING
Switch(config-vlan)# vlan 20
Switch(config-vlan)# name FINANCE
Switch(config-vlan)# vlan 30
Switch(config-vlan)# name SALES
Switch(config-vlan)# vlan 40
Switch(config-vlan)# name HR
Switch(config-vlan)# exit

! Configure trunk links to access switches
Switch(config)# int g0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20,30,40
Switch(config-if)# description Trunk_to_SW2
Switch(config-if)# exit

Switch(config)# int g0/2
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20,30,40
Switch(config-if)# description Trunk_to_SW3
Switch(config-if)# exit

! Configure trunk to router
Switch(config)# int g0/3
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20,30,40
Switch(config-if)# description Trunk_to_Router
Switch(config-if)# exit

! Management VLAN
Switch(config)# int vlan 1
Switch(config-if)# ip address 192.168.1.1 255.255.255.0
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# ip default-gateway 192.168.1.254
Switch(config)# end
Switch# write memory
```

### 6.3 Access Switch (SW2) Configuration
```
Switch> en
Switch# conf t

! Replicate VLANs
Switch(config)# vlan 10
Switch(config)# vlan 20
Switch(config)# vlan 30
Switch(config)# vlan 40
Switch(config)# exit

! Trunk to core
Switch(config)# int g0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20,30,40
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Access ports for PCs
Switch(config)# int f0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# description PC1_Engineering
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# int f0/2
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 20
Switch(config-if)# description PC2_Finance
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# end
```

## 7. Verification & Expected Output

### 7.1 Verify VLANs on All Switches
```
Switch# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- ------------------
1    default                          active    Fa0/3, Fa0/4, ...
10   ENGINEERING                      active    Fa0/1, Fa0/2
20   FINANCE                          active    Fa0/3
30   SALES                            active    (none)
40   HR                               active    (none)
```

### 7.2 Verify Trunk Configuration
```
Switch# show int g0/1 switchport
Name: GigabitEthernet0/1
Switchport: Enabled
Switchport Mode: trunk
Operational Mode: trunk
Allowed Vlans: 1,10,20,30,40
Trunking Native VLAN: 1
```

### 7.3 Test Inter-VLAN Communication
```
PC1 (VLAN 10)> ping 10.0.20.1 (Finance gateway via router)
Reply from 10.0.20.1: bytes=32 time=5ms TTL=255

PC1 (VLAN 10)> ping 10.0.20.10 (Finance PC via router)
Reply from 10.0.20.10: bytes=32 time=5ms TTL=63
```

## 8. Common Mistakes
1. **Forgetting to create VLANs on all switches** — Each switch needs all VLANs even if no local ports
2. **Wrong ports assigned to VLANs** — Access port in wrong VLAN blocks that PC
3. **Native VLAN mismatch on trunks** — Can cause management VLAN issues
4. **Not configuring router subinterfaces** — Inter-VLAN routing fails if router doesn't know VLANs
5. **Incomplete trunk allowed lists** — New VLANs added later but not added to existing trunk allowed lists

## 9. Troubleshooting Guide

### 9.1 PC Can't Ping Outside VLAN
```
! Verify access port is in correct VLAN
Switch# show int f0/1 switchport | include Access VLAN

! Verify trunk allows VLAN
Switch# show int g0/1 switchport | include Allowed

! Verify router has subinterface
Router# show ip int brief | include g0/0.10
```

### 9.2 Trunk Not Forwarding VLAN
```
! Add VLAN to allowed list
Switch(config)# int g0/1
Switch(config-if)# switchport trunk allowed vlan add 50
```

## 10. Design Analysis
Hierarchical VLAN design (core → distribution → access) scales better than flat design. Summarization at distribution layer reduces routing table size.

## 11. Real-World Parallel
Enterprise campus networks have VLANs per building (VLAN 10-19 for Building A, 20-29 for Building B). Core aggregates all VLANs centrally.

## 12. Stretch Goals
1. Add a fifth VLAN for guest network
2. Implement VLAN-based security policy
3. Design VLAN scheme for 1000-person company
4. Plan VLAN migration strategy (merge two VLANs)

## 13. Self-Assessment (BSL Scale)
- **BSL-1:** Create 4 VLANs; configure access and trunk ports
- **BSL-2:** Design VLAN scheme for 6-department network
- **BSL-3:** Document complete VLAN design with IP addressing
- **BSL-4:** Implement VLAN scheme on multi-switch topology
- **BSL-5:** Troubleshoot VLAN connectivity issues systematically
- **BSL-6:** Design VLAN migration plan (minimal downtime)
- **BSL-7:** Design and justify VLAN architecture for 10K-user enterprise

## 14. Key Concepts
- **VLAN isolation:** Each VLAN is separate broadcast domain
- **Trunk:** Link carrying multiple VLANs (802.1Q tagged)
- **Access port:** Link to end device; untagged, single VLAN
- **ROAS:** Router-on-a-Stick enables inter-VLAN routing via subinterfaces
- **Native VLAN:** Untagged traffic on trunk; should match both sides

## 15. What I Learned
VLAN design requires planning before implementation. Proper documentation prevents errors and simplifies troubleshooting.

## 16. Skills Practiced
- ✓ Planning VLAN scheme based on organizational structure
- ✓ Creating VLANs on multiple switches
- ✓ Configuring access ports per VLAN
- ✓ Setting up trunk links with allowed VLAN lists
- ✓ Testing inter-VLAN connectivity
- ✓ Documenting network topology

## 17. GNS3 Lab Info
**Topology:** 3x 2960 Switches, 1x 2911 Router, 4x VPCs
**Time:** 60 minutes
**Base Config:** Switches preconfigured with IOS; no VLANs yet
**Verify:** All four PCs should ping each other via router
