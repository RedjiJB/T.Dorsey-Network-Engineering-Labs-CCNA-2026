# Day 16: Advanced VLAN Implementation - Voice VLAN & Security

## 0. Metadata
- **Objective:** Configure VLANs for data and voice traffic; implement QoS tagging and VLAN security
- **Prerequisites:** Days 1-15 (VLAN fundamentals, multi-VLAN design)
- **Time:** 120 minutes
- **Difficulty:** Intermediate-Advanced
- **Key Concepts:** Voice VLAN, 802.1p CoS, VACL, port security

## 1. Overview
Modern networks carry both data and voice traffic. This lab implements voice VLAN (separate from data) and security controls to protect network resources.

## 2. Business Context
- VoIP phones send voice traffic tagged with different VLAN than data PCs
- Quality of Service (QoS) prioritizes voice over bulk data transfers
- Port security prevents MAC flooding attacks
- VLAN access lists (VACL) enforce inter-VLAN security policies

## 3. Topology
Data VLAN 10, Voice VLAN 110, Management VLAN 1. IP phones have built-in switch (passthrough for PC).

## 4. Configuration

### Voice VLAN Setup
```
Switch(config)# int f0/1
Switch(config-if)# switchport voice vlan 110
Switch(config-if)# switchport access vlan 10
```

### Port Security
```
Switch(config)# int f0/1
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security violation restrict
```

## 5-17. (Standard sections following Day-15 template)
