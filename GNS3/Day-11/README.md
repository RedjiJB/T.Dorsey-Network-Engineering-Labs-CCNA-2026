# GNS3 Day 11: Inter-VLAN Routing - Base & Field Topologies

## Prerequisites & Image Requirements

**Required Appliances:** Cisco ISR 4321 Router, Catalyst 2960 Switches, Alpine Linux PCs  
**Resource Requirements:** 6 GB RAM, 4+ CPU cores

---

## Base Topology Build

### Network Diagram
```
[PC01-PC07]──[SW01]─[Trunk Gi0/1]════════════[Trunk]
(VLANs)           ↓ (VLAN 10,20,30,99)      ↓
                                        [ISR 4321 Router]
                                        [Gi0/0/0 Main Int]
                                        ├─ Gi0/0/0.10 (VLAN 10)
                                        ├─ Gi0/0/0.20 (VLAN 20)
                                        ├─ Gi0/0/0.30 (VLAN 30)
                                        └─ Gi0/0/0.99 (VLAN 99)
```

### Node Configuration

| Node | Type | Role |
|------|------|------|
| Router1 | ISR 4321 | Inter-VLAN routing via subinterfaces |
| SW01 | Catalyst 2960 | Access + trunk to router |
| SW02 | Catalyst 2950 | Access ports only (optional) |
| PC01-PC07 | Alpine Linux | End devices, VLAN access ports |

### Router Configuration Template

```
interface gigabitethernet 0/0/0
 no shutdown
exit

interface gigabitethernet 0/0/0.10
 encapsulation dot1q 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
exit

interface gigabitethernet 0/0/0.20
 encapsulation dot1q 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
exit

interface gigabitethernet 0/0/0.30
 encapsulation dot1q 30
 ip address 192.168.30.1 255.255.255.0
 no shutdown
exit

interface gigabitethernet 0/0/0.99
 encapsulation dot1q 99
 ip address 192.168.99.1 255.255.255.0
 no shutdown
exit
```

---

## Field Variants

### Field-1: Dual-Router HSRP (Hot Standby Router Protocol)
**Objective:** Implement router redundancy for failover.
**Configuration:** Two routers in HSRP group, VIP 192.168.X.254, automatic failover

### Field-2: Static Route Control
**Objective:** Block inter-VLAN routing for security (only static routes for needed paths).
**Configuration:** `no ip routing`, add static routes per VLAN only

### Field-3: Dynamic Routing with OSPF
**Objective:** Automatic failover with redundant routers via OSPF.
**Configuration:** OSPF process, subinterface networks as OSPF areas

### Field-4: Layer 3 Switch (Catalyst 3560)
**Objective:** Replace router-on-stick with multilayer switch for performance.
**Configuration:** SVI interfaces on 3560 instead of subinterfaces

### Field-5: Multiple Subnets per VLAN (Secondary Addressing)
**Objective:** Support legacy subnets in same VLAN.
**Configuration:** Primary IP 192.168.10.1, secondary 10.10.10.1 on same subinterface

### Field-6: QoS with CoS to DSCP Mapping
**Objective:** Implement Quality of Service for prioritized inter-VLAN traffic.
**Configuration:** Trust CoS, map to DSCP, policing per subinterface

### Field-7: WAN Connectivity via Serial Link
**Objective:** Connect branch office via WAN router with subinterface routing.
**Configuration:** Serial0/0/0 subinterfaces for WAN traffic, VLAN traffic on Gi0/0/0

---

## Verification Commands

```bash
Router# show interfaces gigabitethernet 0/0/0.10
Router# show ip interface brief
Router# show ip route
Router# show ip protocol
Router# ping 192.168.20.1 (from VLAN 10 PC)
```

---

**Last Updated:** August 30, 2026 | **GNS3 Version:** 2.2.30+

