# Day 12: Spanning Tree Protocol (IEEE 802.1D) - Lab Manual

## Section 0: Metadata

**Exam Objective:** Configure and verify STP for loop prevention on redundant switches (200-301 Exam Topic 4.5)

**Prerequisites:** Days 09-11 completed (VLANs, trunking, routing)

**Time Budget:** 120 minutes | **Difficulty Level:** Intermediate

---

## Section 1-3: Overview, Business Context, Topology

### Lab Goal
Configure Spanning Tree Protocol on three Catalyst switches with redundant links (triangle topology). Prevent bridging loops while maintaining failover capability.

### Business Context
Three buildings with redundant switches create multiple paths. Without STP, frames would loop indefinitely. STP blocks certain links to prevent loops while keeping them as hot standby for failover.

### Topology Reference
**GitHub Image:** https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-12-Spanning-Tree.png

Three Catalyst 2960 switches forming triangle:
- SW01 (Building A) ↔ SW02 (Building B): Trunk Gi0/1
- SW01 (Building A) ↔ SW03 (Building C): Trunk Gi0/2  
- SW02 (Building B) ↔ SW03 (Building C): Trunk Gi0/1

---

## Section 4-6: STP Configuration on SW01 (Root Bridge)

### Enable STP and Set Root Bridge

```
SW01# configure terminal

! Enable STP (PVST per-VLAN)
SW01(config)# spanning-tree mode pvst

! Set SW01 as root bridge for all VLANs
SW01(config)# spanning-tree vlan 10 priority 4096
SW01(config)# spanning-tree vlan 20 priority 4096
SW01(config)# spanning-tree vlan 30 priority 4096
SW01(config)# spanning-tree vlan 99 priority 4096

! Configure PortFast on access ports (edge ports)
SW01(config)# interface range fastethernet 0/1 - 7
SW01(config-if-range)# spanning-tree portfast
SW01(config-if-range)# spanning-tree bpduguard enable
SW01(config-if-range)# exit

SW01(config)# end
SW01# copy running-config startup-config
```

**Why These Settings:**
- `spanning-tree mode pvst`: Per-VLAN Spanning Tree (calculates topology per VLAN)
- `priority 4096`: Lowest priority value means this switch becomes root (default 32768)
- `portfast`: Access ports go immediately to forwarding (no 50-second delay for learning state)
- `bpduguard`: Disables port if it receives unexpected BPDU (prevents VLAN hopping via fake switches)

---

## Section 7-8: STP Configuration on SW02 & SW03

```
SW02# configure terminal
SW02(config)# spanning-tree mode pvst
SW02(config)# spanning-tree vlan 10 priority 8192
SW02(config)# spanning-tree vlan 20 priority 8192
SW02(config)# spanning-tree vlan 30 priority 8192
SW02(config)# spanning-tree vlan 99 priority 8192

SW02(config)# interface range fastethernet 0/1 - 7
SW02(config-if-range)# spanning-tree portfast
SW02(config-if-range)# spanning-tree bpduguard enable
SW02(config-if-range)# exit

SW02(config)# end
SW02# copy running-config startup-config
```

**Repeat for SW03** (priority 16384 = secondary root)

---

## Section 9-11: Verification Commands

### Display STP Status

```
SW01# show spanning-tree

VLAN0010
  Spanning tree enabled protocol ieee
  Root ID    Priority    4106
             Address     0018.baaa.0001
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    4106  (priority 4096 sys-id-ext 10)
             Address     0018.baaa.0001
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi0/1            Desg FWD 4         128.1    P2p
Gi0/2            Desg FWD 4         128.2    P2p
```

**What This Shows:**
- "This bridge is the root": SW01 is root for VLAN 10
- Interface Gi0/1, Gi0/2: Designated state (forwarding)
- Cost 4: Gigabit port cost (lower cost = preferred path)

### Show Interface STP Status

```
SW01# show interfaces gigabitethernet 0/1 spanning-tree

Port 2 (GigabitEthernet0/1) of VLAN0010 is designated forwarding
   Port path cost 4, Port priority 128, Port Identifier 128.1
   Designated root has priority 4106, address 0018.baaa.0001
   Designated bridge has priority 4106, address 0018.baaa.0001
   Designated port id is 128.1, designated path cost 0
   Timers: Message age 0, Forward delay 0, Hold 0
   Number of transitions to forwarding state: 1
   BPDU: sent 100, received 0
```

---

## Section 12-14: Testing Loop Prevention & Failover

### Test 1: Verify Loop Prevention (All Links Active)

Connect PC to access port on each switch, ping within same VLAN:

```
PC01 (VLAN 10, SW01) > ping 192.168.10.20

Success rate is 100 percent
```

**Expected Behavior:** Frames reach destination via one path (STP blocks alternate)

### Test 2: Simulate Link Failure (Failover)

Disconnect trunk link Gi0/1 between SW01 and SW02:

```bash
# On SW01
SW01# shutdown interface gigabitethernet 0/1

# Wait 30-50 seconds for STP convergence
# Previously blocked port on SW03 becomes designated (starts forwarding)

# Verify connectivity still works (traffic reroutes via SW03)
PC01 (VLAN 10, SW01) > ping 192.168.10.20

Success rate is 100 percent (with higher latency due to reroute)
```

**Why Latency Increases:**
- Before failure: SW01 → (direct) → SW02 (low latency)
- After failure: SW01 → SW03 → SW02 (extra hop through SW03)

---

## Section 15-20: Troubleshooting, Design Analysis, RFC Compliance

### Common Issues

**Issue 1: Port Stuck in "Blocking" State**
- Root cause: Higher priority switch (lower priority value) forced re-election
- Solution: Adjust priority so intended root has lowest value

**Issue 2: BPDU Guard Shutting Down Ports**
- Root cause: End device or rogue switch sending BPDU on edge port
- Solution: Verify connected device is not a switch; disable BPDU guard if intentional bridge

**Issue 3: Convergence Takes 80+ Seconds**
- Root cause: 802.1D waits for forward delay × 2 (listening + learning)
- Solution: Switch to 802.1w (Rapid STP) for < 1 second convergence (Day 13)

### RFC 802.1D Compliance

IEEE 802.1D defines STP BPDU structure (35 bytes):
- Bridge Priority (16 bits): 0-61440, lower = root
- Bridge MAC Address (48 bits): Tiebreaker if priorities equal
- Path Cost (32 bits): Cumulative cost to reach root
- Port ID (16 bits): Bridge priority + port priority + port number

All VLAN bridge instances follow same standard.

### Design Rationale

**Why Root Bridge Centrally Located?**
- All paths through root = uniform distribution
- Minimizes path cost variance
- Predictable failover behavior

**Why Different Priorities per VLAN? (PVST+)**
- VLAN 10 root = SW01, VLAN 20 root = SW02
- Load balancing: Different VLANs use different paths
- Per-VLAN failover protection

---

**Lab Completion Time:** 120 minutes | **Date:** August 30, 2026

