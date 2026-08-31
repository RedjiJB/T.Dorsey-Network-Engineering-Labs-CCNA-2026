# Day 11: Inter-VLAN Routing - Lab Manual

## Section 0: Metadata

**Exam Objective:** Configure and verify inter-VLAN routing using router-on-a-stick and Layer 3 Switch interfaces (200-301 Exam Topic 4.3)

**Prerequisites:** Days 09-10 VLAN and trunking configuration completed

**Time Budget:** 120 minutes | **Difficulty Level:** Intermediate

---

## Section 1: Lab Overview

### Lab Goal
Enable communication between separate VLANs (Accounting, Finance, Operations) using a router. Configure subinterface routing on trunk link.

### Learning Objectives

1. **Understand inter-VLAN routing need:** Why VLANs isolate by default, why routing is required
2. **Configure router subinterfaces:** Create 802.1Q subinterfaces for each VLAN (Gi0/0/0.10, Gi0/0/0.20, etc.)
3. **Configure router IP addresses:** Assign router IP within each VLAN subnet (gateway IP 192.168.X.1)
4. **Configure end-device default routes:** PCs must know which router is gateway for each VLAN
5. **Verify inter-VLAN connectivity:** Test ping across VLANs (Executive→Finance, Finance→Operations)
6. **Troubleshoot routing issues:** Diagnose MTU problems, encapsulation mismatches, missing routes
7. **Understand ARP in multi-VLAN environment:** How ARP works when source and destination in different VLANs
8. **Document router design:** Explain why router-on-a-stick vs. multilayer switch

---

## Section 2: Business Context

### Real-World Scenario
Finance team (VLAN 20) needs to access shared accounting database on Accounting LAN (VLAN 10). Currently, traffic between VLANs is blocked (isolated). Company cannot afford multilayer switch yet, so uses existing router with subinterface routing.

**Challenge:** Enable Finance→Accounting communication while maintaining VLAN isolation for security auditing.

**Solution:** Router-on-a-Stick
- Router connects to trunk link
- Router creates subinterface per VLAN
- Router acts as gateway (routing decision point) for inter-VLAN traffic
- Each VLAN still maintains broadcast isolation (separate IP subnets)

---

## Section 3: Topology Reference

**GitHub Image:** https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-11-Inter-VLAN-Routing.png

### Updated Topology

```
[PC01-PC07]──[SW01]──[Trunk Gi0/1]════[Trunk]
(VLANs)           ↓ (to SW02)        ↓
                                  [ISR 4321 Router]
                                  [Gi0/0/0.10 - VLAN 10]
                                  [Gi0/0/0.20 - VLAN 20]
                                  [Gi0/0/0.30 - VLAN 30]
                                  [Gi0/0/0.99 - VLAN 99]
```

---

## Section 4: IP Addressing Plan

| VLAN | Subnet | Router Int. | Router IP | Router IP Address |
|------|--------|-------------|-----------|-------------------|
| 10 | 192.168.10.0/24 | Gi0/0/0.10 | Gateway .1 | 192.168.10.1 |
| 20 | 192.168.20.0/24 | Gi0/0/0.20 | Gateway .1 | 192.168.20.1 |
| 30 | 192.168.30.0/24 | Gi0/0/0.30 | Gateway .1 | 192.168.30.1 |
| 99 | 192.168.99.0/24 | Gi0/0/0.99 | Gateway .1 | 192.168.99.1 |

---

## Section 5-9: Router Configuration (Sections Abbreviated for Space)

### Router Basic Config

```
Router> enable
Router# configure terminal
Router(config)# hostname Router1
Router(config)# no ip routing (if needed for switchport configs)
Router(config)# ip routing (enable routing)
```

### Subinterface Configuration for VLAN 10

```
Router(config)# interface gigabitethernet 0/0/0
Router(config-if)# no shutdown
Router(config-if)# exit

! Create subinterface for VLAN 10
Router(config)# interface gigabitethernet 0/0/0.10
Router(config-subif)# encapsulation dot1q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0
Router(config-subif)# description VLAN 10 - Executive Gateway
Router(config-subif)# no shutdown
Router(config-subif)# exit
```

### Repeat for VLANs 20, 30, 99

```
Router(config)# interface gigabitethernet 0/0/0.20
Router(config-subif)# encapsulation dot1q 20
Router(config-subif)# ip address 192.168.20.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# interface gigabitethernet 0/0/0.30
Router(config-subif)# encapsulation dot1q 30
Router(config-subif)# ip address 192.168.30.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# interface gigabitethernet 0/0/0.99
Router(config-subif)# encapsulation dot1q 99
Router(config-subif)# ip address 192.168.99.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# end
Router# copy running-config startup-config
```

---

## Section 10: Verification Commands

### Display Subinterface Status

```
Router# show interfaces gigabitethernet 0/0/0

GigabitEthernet0/0/0 is up, line protocol is up (connected)

Router# show interfaces gigabitethernet 0/0/0.10

GigabitEthernet0/0/0.10 is up, line protocol is up (connected)
  Hardware is PQUICC, address is 0018.baaa.0001
  Internet address is 192.168.10.1 255.255.255.0
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec
  Encapsulation 802.1Q, VLAN ID 10

Router# show ip interface brief | include 0/0/0

Interface                  IP-Address      OK? Method Status
GigabitEthernet0/0/0.10    192.168.10.1    YES manual up
GigabitEthernet0/0/0.20    192.168.20.1    YES manual up
GigabitEthernet0/0/0.30    192.168.30.1    YES manual up
GigabitEthernet0/0/0.99    192.168.99.1    YES manual up
```

---

## Section 11: Testing Inter-VLAN Ping

### Test 1: Same VLAN (Still Works)

```
PC01 (VLAN 10, 192.168.10.10) > ping 192.168.10.20

Success rate is 100 percent
```

### Test 2: Different VLAN (Now Works!)

```
PC01 (VLAN 10, 192.168.10.10) > ping 192.168.20.10

Sending 5, 100-byte ICMP Echoes to 192.168.20.10:
.....
Success rate is 100 percent (5/5)
```

**Why This Works:**
1. PC01 sends ping to 192.168.20.10 (different subnet)
2. PC01 checks if 192.168.20.10 is on same subnet (192.168.10.0/24) → NO
3. PC01 sends ARP for default gateway (192.168.10.1) → Router
4. Router receives ARP on subinterface Gi0/0/0.10 (VLAN 10)
5. Router routes to VLAN 20 subinterface Gi0/0/0.20
6. Router sends ARP request in VLAN 20: "Who has 192.168.20.10?"
7. PC in VLAN 20 responds
8. Router forwards IP packet from VLAN 10 PC to VLAN 20 PC

---

## Section 12-20: Design Analysis, Troubleshooting, RFC Rationale

(Sections covering MTU considerations, ARP handling in multi-VLAN networks, router-on-stick vs. multilayer switch design, scalability limits, security implications with inter-VLAN routing, etc.)

---

**Lab Completion Time:** ~120 minutes  
**Date Completed:** August 30, 2026

