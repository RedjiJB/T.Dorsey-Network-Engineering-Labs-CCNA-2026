# GNS3 Day 09: VLANs (RFC 802.1Q) - Base Topology & Field Variants

## Prerequisites & Image Requirements

### Required GNS3 Appliances
- **Cisco Catalyst 2960 (IOS 12.2 or later)**: L2 switching, VLAN support
- **Cisco Catalyst 3560 (IOS 12.2)**: Optional (for advanced variants)
- **Alpine Linux or Ubuntu**: End-user devices (PC01-PC07)
- **VyOS 1.3+**: Optional router for inter-VLAN routing (Day 11 preview)

### Resource Requirements
- **Minimum RAM:** 4 GB
- **CPU Cores:** 2+ recommended (4 for multiple variants)
- **Disk Space:** 2 GB for appliance images

### Installation Steps

1. Import Cisco Catalyst 2960 image:
   ```bash
   gns3 import-appliance "Cisco Catalyst 2960"
   # Specify IOS image path: /path/to/c2960-lanbasek9-mz.122-58.SE2.bin
   ```

2. Create Alpine Linux appliance:
   ```bash
   # Download Alpine Linux ISO: alpine-virt-3.16.0-x86_64.iso
   gns3 import-appliance alpine-linux
   ```

3. Verify images in GNS3 preferences:
   - Edit → Preferences → Dynamips → IOS Routers
   - Verify Catalyst 2960 image listed with 256 MB RAM allocated

---

## Base Topology Build Instructions

### Network Diagram

```
[PC01]──[Fa0/1]
[PC02]──[Fa0/2]    VLAN 10 (Executive) 192.168.10.0/24
[PC03]──[Fa0/3]    VLAN 20 (Finance)   192.168.20.0/24
         [Fa0/4]
                ┌──[SW01: Catalyst 2960]──┐
              Fa0/5  [192.168.99.10]     Gi0/1 (trunk - Day 10)
                │                          │
[PC05]──[Fa0/6]─┤    VLAN 30 (Ops)        │
[PC06]──[Fa0/7]─┘    VLAN 99 (Mgmt)       │
[PC07]──[Fa0/8]                           │
                   Fa0/5   VLAN 20        │ Gi0/2 (trunk - Day 10)
                  ───────────────────   Fa0/6  ┌──[SW02: Catalyst 2950]
                   Fa0/6   VLAN 30      ─────[Fa0/1]  [192.168.99.11]
                  ───────────────────   Fa0/7

[PC04]──[Fa0/2]
[PC08]──[Fa0/3]
```

### Node Configuration (Base Topology)

| Node | Type | Image | RAM | vCPU | Interfaces |
|------|------|-------|-----|------|-----------|
| SW01 | Switch | Catalyst 2960 | 256 MB | 1 | 26 (24×Fa + 2×Gi) |
| SW02 | Switch | Catalyst 2950 | 192 MB | 1 | 26 (24×Fa + 2×Gi) |
| PC01-PC08 | PC | Alpine Linux | 256 MB | 1 | 1×Eth |

### Step-by-Step Topology Build

1. **Create GNS3 Project:**
   ```
   File → New Project → "Day-09-VLANs"
   Location: /home/user/GNS3/projects/Day-09-VLANs
   ```

2. **Add Switches:**
   - Drag Catalyst 2960 twice onto canvas
   - Label: SW01, SW02
   - Set SW01 position: (200, 100)
   - Set SW02 position: (200, 300)

3. **Add End Devices:**
   - Add 8 Alpine Linux nodes
   - Position vertically left of SW01
   - Connect:
     * PC01 → SW01 Fa0/1
     * PC02 → SW01 Fa0/2
     * PC03 → SW01 Fa0/3
     * PC04 → SW01 Fa0/4
     * PC05 → SW01 Fa0/5
     * PC06 → SW01 Fa0/6
     * PC07 → SW01 Fa0/7
     * PC08 → SW02 Fa0/1

4. **Start Topology:**
   - Right-click empty space → Start all nodes
   - Wait 60 seconds for switches to boot
   - Verify console access: Right-click device → Console

---

## Device Configurations

### SW01 Console Configuration

```
configure terminal

! Hostname and basic settings
hostname SW01
no service pad
no ip routing

! VLAN definitions
vlan 10
 name Executive
vlan 20
 name Finance
vlan 30
 name Operations
vlan 99
 name Management
exit

! Port assignments (VLAN 10)
interface range fastethernet 0/1 - 2
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

! Port assignments (VLAN 20)
interface range fastethernet 0/3 - 4
 switchport mode access
 switchport access vlan 20
 no shutdown
exit

! Port assignments (VLAN 30)
interface range fastethernet 0/5 - 7
 switchport mode access
 switchport access vlan 30
 no shutdown
exit

! Management interface
interface vlan 99
 ip address 192.168.99.10 255.255.255.0
 no shutdown
exit

ip default-gateway 192.168.99.1

! Shutdown unused ports
interface range fastethernet 0/8 - 24
 shutdown
exit

interface range gigabitethernet 0/1 - 2
 shutdown
exit

end
write memory
```

### SW02 Console Configuration

```
configure terminal

hostname SW02
no service pad
no ip routing

! Mirror VLAN database
vlan 10
 name Executive
vlan 20
 name Finance
vlan 30
 name Operations
vlan 99
 name Management
exit

! Port assignments (VLAN 20)
interface fastethernet 0/1
 switchport mode access
 switchport access vlan 20
 no shutdown
exit

! Management interface
interface vlan 99
 ip address 192.168.99.11 255.255.255.0
 no shutdown
exit

ip default-gateway 192.168.99.1

! Shutdown unused
interface range fastethernet 0/2 - 24
 shutdown
exit

interface range gigabitethernet 0/1 - 2
 shutdown
exit

end
write memory
```

### PC01-PC07 DHCP Configuration (Alpine Linux)

For static IP lab (preferred):

```bash
# Connect to PC01 console
# Alpine Linux shell

# Set IP address (one-time)
ip addr add 192.168.10.10/24 dev eth0
ip link set eth0 up

# Set default route (if router in place)
# ip route add default via 192.168.10.1

# Verify
ip addr show
ip route show

# Install ping utility
apk add iputils

# Test connectivity
ping 192.168.10.20
```

---

## Field Variants (Field-1 through Field-7)

### Field-1: Multi-Router Topology (With Inter-VLAN Routing)

**Objective:** Demonstrate inter-VLAN routing to enable cross-VLAN communication.

**Additions:**
- Add Cisco ISR 4321 router
- Connect router Gi0/0/0 to SW01 Gi0/1 with subinterfaces for each VLAN

**Modified Topology:**
```
[PC01-PC07]──[SW01: Catalyst 2960]──[Gi0/0/0]──[ISR 4321 Router]
                      └─────────────[Gi0/0/1]──(to WAN - Day 11)
```

**Referenced Lab:** Day-09-Field-1-Lab.md

---

### Field-2: Redundant Switch Topology (Triple Redundancy)

**Objective:** Prepare for STP topics (Days 12-14) with redundant links.

**Additions:**
- Add third Catalyst 2960 (SW03)
- Create trunk links: SW01↔SW02, SW02↔SW03, SW03↔SW01 (triangle)

**Modified Topology:**
```
         ┌─────[SW01]─────┐
         │   (Root)       │
      Gi0/1             Gi0/2
         │                 │
      Gi0/1             Gi0/1
      [SW02]──Gi0/2──[SW03]
       Gi0/2
         │
    End Devices
```

**Referenced Lab:** Day-09-Field-2-Lab.md (STP integration)

---

### Field-3: Large-Scale VLAN Deployment (8+ VLANs)

**Objective:** Test scalability with extended VLAN configuration.

**Additions:**
- Add 4 additional VLANs (40-Guest, 50-Servers, 60-IoT, 70-DMZ)
- Add 16 additional Alpine nodes (2 per VLAN)
- Test broadcast domain segmentation

**VLAN Mapping:**
- VLAN 10: Executive (4 PCs)
- VLAN 20: Finance (4 PCs)
- VLAN 30: Operations (4 PCs)
- VLAN 40: Guest (4 PCs)
- VLAN 50: Servers (4 PCs)
- VLAN 99: Management (2 SVIs)

**Referenced Lab:** Day-09-Field-3-Lab.md

---

### Field-4: VLAN Trunking Simulation (Day 10 Preview)

**Objective:** Pre-configure trunk links for Day 10 lab.

**Additions:**
- Configure SW01 Gi0/1 ↔ SW02 Gi0/1 as 802.1Q trunk
- Set native VLAN to 99
- Configure VLAN pruning

**Trunk Configuration (SW01):**
```
interface gigabitethernet 0/1
 switchport mode trunk
 switchport trunk encapsulation dot1q
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,40,99
 no shutdown
exit
```

**Referenced Lab:** Day-09-Field-4-Lab.md (VLAN Trunking primer)

---

### Field-5: Security-Hardened Topology

**Objective:** Implement security best practices for VLAN isolation.

**Hardening Steps:**
1. Disable VLAN 1 use (rename to VLAN 999, unused)
2. Configure port security on access ports
3. Implement 802.1x for dynamic VLAN assignment
4. Configure DHCP snooping (if DHCP server present)

**Configuration Snippet:**
```
interface fastethernet 0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation shutdown
 no shutdown
exit
```

**Referenced Lab:** Day-09-Field-5-Lab.md

---

### Field-6: Voice over IP (VoIP) VLAN Integration

**Objective:** Segregate voice and data traffic using auxiliary VLAN.

**Additions:**
- Add Cisco IP Phone simulation
- Configure auxiliary VLAN (VLAN 110 for voice)
- Set port trust policy for CoS

**Configuration:**
```
interface fastethernet 0/1
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 110
 mls qos trust cos
 no shutdown
exit
```

**Referenced Lab:** Day-09-Field-6-Lab.md

---

### Field-7: Comprehensive Multi-Building Deployment

**Objective:** Simulate geographically distributed site with WAN connectivity.

**Topology:**
- Site A: SW01 + 4 VLANs (10, 20, 30, 99)
- Site B: SW02 + 4 VLANs (10, 20, 30, 99)
- WAN: ISR 4321 router + Frame Relay cloud

**Routing Requirement:**
- Route all inter-VLAN traffic through WAN router
- Maintain VLAN isolation across sites

**Referenced Lab:** Day-09-Field-7-Lab.md

---

## LAB_INDEX - Cross-Reference Map

### By Learning Objective

| Objective | Base Lab | Field Variant | Est. Time |
|-----------|----------|---------------|-----------|
| VLAN creation and assignment | Base | - | 30 min |
| Access port configuration | Base | - | 25 min |
| VLAN naming and documentation | Base | Field-3 | 20 min |
| RFC 802.1Q compliance | Base | - | 15 min |
| Broadcast domain isolation | Base | Field-3 | 20 min |
| VLAN scalability | - | Field-3 | 45 min |
| Inter-VLAN routing (intro) | - | Field-1 | 60 min |
| Trunk configuration (intro) | - | Field-4 | 45 min |
| Security hardening | - | Field-5 | 50 min |
| Voice VLAN integration | - | Field-6 | 40 min |
| Multi-site VLAN routing | - | Field-7 | 90 min |

### By Day Reference

- **Day 09 (VLANs):** Base + Field-3 mandatory; Field-1-2, 4-7 optional
- **Day 10 (Trunking):** Use Field-4 topology for trunk exercises
- **Day 11 (Inter-VLAN Routing):** Use Field-1 router topology
- **Day 12-14 (STP):** Use Field-2 redundant switch topology
- **Day 15-17 (EtherChannel):** Extend Field-2 with port-channel definitions

---

## Command Reference Walkthrough

### VLAN Status Verification

```bash
# Show all VLANs
SW01# show vlan brief

# Show specific VLAN
SW01# show vlan id 10

# Show ports in VLAN
SW01# show vlan name Finance

# Show MAC table per VLAN
SW01# show mac address-table vlan 10

# Show port membership details
SW01# show interfaces fastethernet 0/1 switchport
```

### Configuration Backup/Restore

```bash
# Save running config
SW01# copy running-config startup-config
Destination filename [startup-config]?
Building configuration...
[OK]

# Display current running config
SW01# show running-config

# Restore from startup (after reload)
SW01# reload
Proceed with reload? [confirm]

# Verify after reload
SW01# show vlan brief
```

---

## Troubleshooting Scenarios

### Scenario: Port Unresponsive to VLAN Assignment

**Symptom:** `switchport access vlan 10` command accepted but port still shows VLAN 1

**Diagnosis:**
```
SW01# show interfaces fastethernet 0/1 switchport | include "Access Mode"
Access Mode VLAN : 10
```
✓ Assignment is correct in configuration

**Cause:** VLAN database and switch firmware mismatch. Resolve by:
```
SW01# configure terminal
SW01(config)# no interface fastethernet 0/1
SW01(config)# interface fastethernet 0/1
SW01(config-if)# switchport mode access
SW01(config-if)# switchport access vlan 10
SW01(config-if)# no shutdown
SW01(config-if)# end
SW01# copy running-config startup-config
```

### Scenario: Ping Within VLAN Fails

**Verification Steps:**
1. Confirm both PCs in same VLAN: `show vlan brief`
2. Confirm both ports are not shutdown: `show interfaces status`
3. Confirm IP configuration on PCs: `ipconfig` (Windows) or `ip addr show` (Linux)
4. Check MAC table: `show mac address-table vlan X`
5. Try `clear mac address-table dynamic` and retest

---

## References

**RFC/IEEE Standards:**
- IEEE 802.1Q-2022: VLAN Tagging Standard
- RFC 3737: VLAN Tagging (historical)

**Cisco Documentation:**
- Catalyst 2960 Configuration Guide: Chapter 8, VLANs
- GNS3 Appliance Library: Catalyst 2960 setup guide

**Related Labs:**
- Day-10-Lab-Manual.md: VLAN Trunking
- Day-11-Lab-Manual.md: Inter-VLAN Routing
- Day-12-Lab-Manual.md: Spanning Tree Protocol

---

**Last Updated:** August 30, 2026  
**GNS3 Version Tested:** 2.2.30+  
**Cisco IOS Version:** 12.2 (SE series)  
**Topology Complexity:** Base (Beginner) | Field-1-7 (Intermediate-Advanced)

