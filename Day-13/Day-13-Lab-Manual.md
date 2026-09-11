# Day 13: VLAN Routing & Inter-VLAN Communication (Router-on-a-Stick)

## 0. Metadata
- **Objective:** Implement router-on-a-stick (ROAS) architecture to enable inter-VLAN communication
- **Relevant RFC/Standards:** IEEE 802.1Q (VLAN tagging), RFC 3232 (assigned numbers)
- **Prerequisites:** Days 1-12 (basic switching, VLANs, routing fundamentals)
- **Estimated Time:** 120 minutes
- **Difficulty:** Intermediate (VLAN + routing combined)
- **Hardware Required:** 1 router, 2-3 switches, 3-4 PCs
- **Key Concepts:** Subinterfaces, 802.1Q tagging, VLAN database, interVLAN routing

## 1. Overview
Router-on-a-stick (ROAS) allows a single physical interface on a router to route traffic between multiple VLANs by using subinterfaces and 802.1Q tagging. This is essential for medium-scale networks that don't yet justify a multilayer switch.

## 2. Business Context
Inter-VLAN communication is critical in real organizations:
- **Department segregation:** Marketing (VLAN 10), IT (VLAN 20), Finance (VLAN 30) need to communicate
- **Security:** VLANs isolate traffic; only authorized flows cross via routing
- **Cost-efficiency:** One router with multiple subinterfaces vs. multiple routers
- **Flexibility:** Route between any VLANs without purchasing additional hardware

## 3. Topology Reference
```
         [Router R1]
          |  .1/30
          | (G0/0 tagged)
          |
     -----+-----
     |         |
    [SW1]     [SW2]
  (access)  (trunk)
     |         |
    PC1       PC2
  (VLAN 10)  (VLAN 20)
  10.0.10.0/24
```

## 4. IP Addressing Plan
| Device | VLAN | Interface | IP Address | Subnet Mask | Gateway |
|--------|------|-----------|-----------|------------|---------|
| PC1 | 10 | NIC | 10.0.10.10 | 255.255.255.0 | 10.0.10.1 |
| PC2 | 20 | NIC | 10.0.20.10 | 255.255.255.0 | 10.0.20.1 |
| R1 | 10 | G0/0.10 | 10.0.10.1 | 255.255.255.0 | N/A |
| R1 | 20 | G0/0.20 | 10.0.20.1 | 255.255.255.0 | N/A |
| SW1 | N/A | VLAN 10 | 10.0.10.254 | 255.255.255.0 | 10.0.10.1 |
| SW2 | N/A | VLAN 1 | 192.168.1.2 | 255.255.255.0 | 192.168.1.1 |

## 5. Pre-Config Checklist
- [ ] Console cable connected to all devices
- [ ] IOS image verified on router and switches
- [ ] Physical cabling complete (trunks, access links)
- [ ] VLANs created on all switches (10, 20, etc.)
- [ ] Trunk links configured (if using multiple switches)
- [ ] Router powered on and ready for configuration

## 6. Configuration

### 6.1 Switch Configuration (SW1 - Access Switch)
```
Switch> en
Switch# conf t

! Create VLANs
Switch(config)# vlan 10
Switch(config-vlan)# name MARKETING
Switch(config-vlan)# exit

Switch(config)# vlan 20
Switch(config-vlan)# name IT
Switch(config-vlan)# exit

! Configure access port
Switch(config)# int f0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# description PC1_Marketing
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Configure trunk port to R1 (if using trunk)
Switch(config)# int g0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Configure management IP
Switch(config)# int vlan 10
Switch(config-if)# ip address 10.0.10.254 255.255.255.0
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# ip default-gateway 10.0.10.1
Switch(config)# end
Switch# write memory
```

### 6.2 Router Configuration (R1)
```
Router> en
Router# conf t

! Enable IP routing (enabled by default on routers)
Router(config)# ip routing

! Configure physical interface (no IP, just encapsulation)
Router(config)# int g0/0
Router(config-if)# no shutdown
Router(config-if)# exit

! Configure VLAN 10 subinterface
Router(config)# int g0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 10.0.10.1 255.255.255.0
Router(config-subif)# description MARKETING_VLAN
Router(config-subif)# no shutdown
Router(config-subif)# exit

! Configure VLAN 20 subinterface
Router(config)# int g0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 10.0.20.1 255.255.255.0
Router(config-subif)# description IT_VLAN
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# end
Router# write memory
```

## 7. Verification & Expected Output

### 7.1 Verify Subinterfaces
```
Router# show int g0/0.10
GigabitEthernet0/0.10 is up, line protocol is up (connected)
  Hardware is iGbE, address is 0012.0001.0001
  Encapsulation 802.1Q, VLAN ID 10
  inet 10.0.10.1 netmask 255.255.255.0
  
Router# show int g0/0.20
GigabitEthernet0/0.20 is up, line protocol is up (connected)
  Hardware is iGbE, address is 0012.0001.0001
  Encapsulation 802.1Q, VLAN ID 20
  inet 10.0.20.1 netmask 255.255.255.0
```

### 7.2 Verify Routing Table
```
Router# show ip route
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       ...
C     10.0.10.0/24 is directly connected, GigabitEthernet0/0.10
C     10.0.20.0/24 is directly connected, GigabitEthernet0/0.20
```

### 7.3 Test Inter-VLAN Communication
```
PC1> ping 10.0.20.10
Request sent from ICMP seq=1
Reply from 10.0.20.10: bytes=32 time=5ms TTL=63

PC2> ping 10.0.10.10
Reply from 10.0.10.10: bytes=32 time=5ms TTL=63
```

## 8. Common Mistakes
1. **Forgetting to set physical interface to no shutdown** — Subinterfaces won't activate without parent interface up
2. **Using incorrect encapsulation** — Must match VLAN ID on both switch and router
3. **Wrong subinterface naming** — Naming is flexible but standardize (use VLAN ID for clarity)
4. **Missing IP addresses** — Each subinterface needs its own IP in the VLAN's subnet
5. **Switch trunk configuration** — If using trunk to router, must allow VLANs explicitly

## 9. Troubleshooting Guide

### 9.1 Subinterface Not Activating
```
! Check parent interface status
Router# show int g0/0 | include (is up|is down)

! Solution: Ensure g0/0 is up
Router# conf t
Router(config)# int g0/0
Router(config-if)# no shutdown
```

### 9.2 Cannot Ping Across VLANs
```
! Verify subinterface has IP
Router# show int g0/0.10 | include inet

! Verify switch allowed VLAN on trunk
Switch# show int g0/1 switchport | include Allowed

! Check routing table
Router# show ip route connected
```

### 9.3 Switch Can't Ping Gateway
```
! Verify management VLAN IP is configured
Switch# show int vlan 10

! Verify default gateway
Switch# show ip default-gateway

! Ensure VLANs exist on switch
Switch# show vlan brief
```

## 10. Design Analysis
**Why Router-on-a-Stick?**
- Cost: One WAN-facing interface vs. three separate routers
- Scalability: Can add more VLANs without new hardware (just subinterfaces)
- Security: Router can apply ACLs between VLANs at routing layer

**Limitations:**
- Single point of failure (one physical link)
- Bandwidth bottleneck (all inter-VLAN traffic through one interface)
- Better solution: Multilayer switch (L3) for large deployments

## 11. Real-World Parallel
**Cisco Campus Network:**
- Core layer uses multilayer switches (3560, 6500)
- Access layer uses 2960 switches with VLAN trunks to distribution
- Distribution layer routes with L3 modules (faster than ROAS)
- Small branch offices often use ROAS with a small 1921 router

## 12. Stretch Goals
1. Add a third VLAN (VLAN 30: Finance) and configure ROAS for it
2. Implement static route between two remote networks via ROAS
3. Configure DHCP relay on router to provide IPs from VLAN-specific pools
4. Test asymmetric routing scenario (reply takes different VLAN than request)

## 13. Self-Assessment (Black Start Levels)
- **BSL-1:** One subinterface can ping the other VLAN
- **BSL-2:** Both VLANs can ping each other; routing table shows both connected routes
- **BSL-3:** Can explain encapsulation dot1Q purpose and show int output
- **BSL-4:** Can design ROAS for three VLANs and troubleshoot dead trunk
- **BSL-5:** Can argue ROAS vs. L3 switch tradeoffs; can add VLAN without packet loss
- **BSL-6:** Can explain subinterface numbering flexibility; can isolate VLAN communication with ACL
- **BSL-7:** Can mentor others through ROAS setup; can design redundant ROAS (active-standby)

## 14. Key Concepts
- **Subinterface:** Virtual interface on a single physical port, identified by dot notation (g0/0.10)
- **802.1Q Tagging:** Adds 4-byte VLAN header to Ethernet frame; must match on both sides
- **Native VLAN:** Untagged VLAN on trunk; avoid for routed subinterfaces
- **Trunking:** Links carrying traffic for multiple VLANs; both switch and router must agree

## 15. What I Learned
After this lab, you should:
- Understand subinterface creation and why they're needed for ROAS
- Know how 802.1Q encapsulation works and when it's applied
- Recognize when ROAS is appropriate vs. when L3 switching is better
- Troubleshoot inter-VLAN communication failures methodically

## 16. Skills Practiced
- ✓ Creating and assigning VLANs on switches
- ✓ Configuring trunk links (802.1Q)
- ✓ Enabling routing on router subinterfaces
- ✓ Testing connectivity across VLAN boundaries
- ✓ Reading and interpreting routing tables
- ✓ Verifying encapsulation and interface status

## 17. GNS3 Lab Info
**Recommended Topology:**
- 1x Cisco 2911 Router (1 GigabitEthernet interface)
- 1-2x Cisco 2960 Switches (for VLAN trunking)
- 4x VPCs (one per VLAN, plus one for testing)

**Pre-built Config:**
- Load base-config with VLANs already created
- Subinterfaces must be configured from scratch

**Time Estimate:** 45 minutes in GNS3
