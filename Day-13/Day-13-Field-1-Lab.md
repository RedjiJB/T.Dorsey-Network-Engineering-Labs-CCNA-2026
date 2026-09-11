# Day 13: VLAN Routing & Inter-VLAN Communication (Black Start Field)

## 0. Metadata
- **Objective:** Implement ROAS in offline-resilient mode for deployment without external management access
- **Research Field:** Field-1: Black Start (Offline Resilience)
- **Proof Obligations:** Cached ROAS configuration persists across complete power loss; inter-VLAN routing functions without network connectivity
- **Haiti Deployment Phase:** P38 (pilot, 50 nodes, offline-first)
- **Relevant RFC/Standards:** IEEE 802.1Q, RFC 3232, RFC 5737 (documentation prefixes)
- **Prerequisites:** Days 1-12 + Field-1 prerequisites (offline cache design, power loss simulation)
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced (offline-first optimization)
- **Hardware Required:** 1 router, 2 switches, 3 PCs, UPS (optional), cache storage device
- **Key Concepts:** Offline ROAS, configuration persistence, cached routing tables, cold-start validation

## 1. Business Context (Field-1: Black Start)
In Haiti pilot sites (P38), power is unreliable (average 6 hours/day outage). Field-1 optimization proves that ROAS routing tables can be:
1. Pre-cached to non-volatile storage
2. Loaded on cold restart without network connectivity
3. Function during full network isolation

Real-world scenario: Site has UPS-backed core switch and router. Power fails, internet gateway goes offline. Network must route between VLANs for 6+ hours using only cached state. This lab proves cold-start ROAS works with zero external dependency.

**Success Metric:** After simulated power-loss and restart, inter-VLAN communication resumes in < 30 seconds with no management access.

## 2. Topology Diagram (Black Start Variant)
```
┌─────────────────────────────────────────┐
│   [Router R1 + Cache Storage]           │
│   (UPS-backed, offline-capable)         │
│     | .1/24 (VLAN 10, 20)               │
│     |                                   │
│   ┌─────────────────────────────────┐   │
│   │  [SW1: Core - No Internet Link] │   │
│   │  (Local storage for VLAN state) │   │
│   │  /            |             \   │   │
│   │[SW2-Local]  [SW3-Local]  [SW4] │   │
│   │  |             |           |    │   │
│   │ PC1           PC2         PC3   │   │
│   │(V10-cached) (V20-cached) (V30)  │   │
│   │             **NO INTERNET**     │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Field-1 Modifications:**
- Remove internet gateway link (simulate offline)
- Add local cache storage on router (simulate persistent config)
- No management access required after cold-start
- VLAN database replicated to all switches' non-volatile storage

## 3. IP Addressing Plan (Offline-Optimized)
| Device | VLAN | Interface | IP Address | Cached | Notes |
|--------|------|-----------|-----------|---------|-------|
| PC1 | 10 | NIC | 10.0.10.10 | Static | Pre-provisioned, no DHCP |
| PC2 | 20 | NIC | 10.0.20.10 | Static | Pre-provisioned, no DHCP |
| R1 | 10 | G0/0.10 | 10.0.10.1 | NVRAM | Persists power loss |
| R1 | 20 | G0/0.20 | 10.0.20.1 | NVRAM | Persists power loss |
| SW1 | 10 | VLAN 10 | 10.0.10.254 | NVRAM | Local management |

**Field-1 Annotation:** All IPs statically assigned; no DHCP relay required. Configuration must survive power-loss cycle.

## 4. Field-1-Specific Configuration

### 4.1 Pre-Deployment: Verify Offline Capability
```
! Step 1: On router, verify startup-config saved to NVRAM
Router# show startup-config | include interface|ip address
! Expected: All subinterfaces and IPs present

! Step 2: Simulate cache validation
Router# copy startup-config flash:offline-cache.cfg
! Backup config to flash for offline validation

! Step 3: On switches, verify VLAN database persisted
Switch# show vlan brief
! Expected: All VLANs show "active" even after power loss simulation
```

### 4.2 Cold-Start Configuration (Power Loss Recovery)
```
! Router Configuration (persists via NVRAM)
Router> en
Router# conf t

! Physical interface (no IP, enables subinterfaces)
Router(config)# int g0/0
Router(config-if)# no shutdown
Router(config-if)# exit

! VLAN 10 subinterface (cached in NVRAM)
Router(config)# int g0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 10.0.10.1 255.255.255.0
Router(config-subif)# description VLAN10_OFFLINE
Router(config-subif)# no shutdown
Router(config-subif)# exit

! VLAN 20 subinterface (cached in NVRAM)
Router(config)# int g0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 10.0.20.1 255.255.255.0
Router(config-subif)# description VLAN20_OFFLINE
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# end
Router# write memory
! **CRITICAL:** write memory saves to NVRAM; this survives power-loss
```

### 4.3 Switch Configuration (Field-1 Offline-First)
```
Switch> en
Switch# conf t

! Create VLANs (stored in NVRAM via flash:vlan.dat)
Switch(config)# vlan 10
Switch(config-vlan)# name FIELD1_VLAN10
Switch(config-vlan)# exit

Switch(config)# vlan 20
Switch(config-vlan)# name FIELD1_VLAN20
Switch(config-vlan)# exit

! Configure access port (persistent)
Switch(config)# int f0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# int f0/2
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 20
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Trunk to router (supports offline ROAS)
Switch(config)# int g0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 1,10,20
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Management IP (optional for offline operation)
Switch(config)# int vlan 10
Switch(config-if)# ip address 10.0.10.254 255.255.255.0
Switch(config-if)# no shutdown
Switch(config-if)# exit

Switch(config)# end
Switch# write memory
```

### 4.4 Offline Validation (Field-1 Specific)
```
! Simulate power loss on router by unplugging (or reload in sim)
Router# reload
! Expected: After reload, startup-config loads automatically

! Verify subinterfaces active WITHOUT console access
! (After reload, subinterfaces should auto-enable)

! From PC1 (VLAN 10):
PC1> ping 10.0.20.10
! Expected within 30 seconds: Reply from 10.0.20.10

! If reply succeeds, Field-1 cold-start validation PASSED
```

## 5. Field-1-Specific Verification Steps

**Offline-Resilient ROAS Verification Checklist:**

### 5.1 Pre-Power-Loss Baseline
```
! 1. Verify all subinterfaces operational
Router# show int g0/0.10 | include (is up|Encapsulation|inet)
! Expected: "is up, line protocol is up", "Encapsulation 802.1Q, VLAN ID 10", IP address

Router# show int g0/0.20 | include (is up|Encapsulation|inet)
! Expected: Same for VLAN 20

! 2. Verify routing table (all subnets reachable)
Router# show ip route connected
! Expected: Two connected routes (10.0.10.0/24 via g0/0.10, 10.0.20.0/24 via g0/0.20)

! 3. Test connectivity before power loss
PC1> ping 10.0.20.1 (router VLAN 20)
! Expected: Reply in < 5ms

PC1> ping 10.0.20.10 (PC2 via router)
! Expected: Reply via router (TTL 63)
```

### 5.2 Simulated Power Loss & Recovery
```
! **POWER LOSS SIMULATION:**
! Option A (Hardware): Unplug router/switch power for 30 seconds
! Option B (Simulator): Router# reload (in GNS3/Cisco PT)

! **After power restored (or reload completes):**
! Wait 30 seconds for subinterfaces to stabilize

! 3. Verify cached configuration loaded
Router# show int g0/0.10 | include (is up|Encapsulation|inet)
! Expected: Subinterface active, IP present, NO serial console input required

! 4. Test inter-VLAN communication immediately
PC1> ping 10.0.20.10
! Expected: Reply within 30 seconds (proves cold-start worked)

! 5. Verify routing table persisted
Router# show ip route connected
! Expected: Both subnets visible without re-configuration
```

### 5.3 Extended Offline Operation (Field-1 Success Proof)
```
! Simulate 6+ hours without external access
! (In lab: just keep network isolated and verify periodic pings work)

! After 60 minutes of isolation:
PC1> ping 10.0.20.10
! Expected: Still works (proves no external dependency)

! Verify no DHCP requests logged (config is static)
Switch# show ip dhcp binding
! Expected: No active bindings (static IPs only)

! Verify no management access attempts
Router# show log | include failed|authentication
! Expected: No failed authentication entries (proves offline-capable)
```

## 6. Expected Output Gallery (Offline-Resilient ROAS)

### 6.1 Post-Power-Loss Subinterface Status
```
Router# show int g0/0.10
GigabitEthernet0/0.10 is up, line protocol is up (connected)
  Hardware is iGbE, address is 0012.0001.0001
  Encapsulation 802.1Q, VLAN ID 10
  inet 10.0.10.1 netmask 255.255.255.0
  [Output continues without any console configuration]
```

### 6.2 Offline Ping Success (Core Proof)
```
PC1> ping 10.0.20.10 -c 4
Pinging 10.0.20.10 with 32 bytes of data:
Reply from 10.0.20.10: bytes=32 time=6ms TTL=63
Reply from 10.0.20.10: bytes=32 time=5ms TTL=63
Reply from 10.0.20.10: bytes=32 time=5ms TTL=63
Reply from 10.0.20.10: bytes=32 time=6ms TTL=63

Sent: 4 packets, Received: 4 packets, Lost: 0 (0% loss)
```

### 6.3 Routing Table (Persisted via NVRAM)
```
Router# show ip route
Codes: C - connected, S - static, ...

C     10.0.10.0/24 is directly connected, GigabitEthernet0/0.10
C     10.0.20.0/24 is directly connected, GigabitEthernet0/0.20
```

## 7. Common Field-1-Specific Mistakes

### 7.1 MISTAKE: Not Writing Startup Config
```
Router# copy running-config startup-config  ← MUST DO THIS
! Error: Config in RAM only; lost on power cycle
! Fix: Always "write memory" after ROAS config
```

### 7.2 MISTAKE: DHCP Relay Configured
```
Router(config)# ip helper-address 10.0.0.1  ← NO! External dependency
! Error: Cold-start fails if DHCP server unreachable
! Fix: Use static IPs for Field-1 deployments
```

### 7.3 MISTAKE: Trunk to Router Misconfigured
```
Switch(config-if)# switchport trunk allowed vlan 10,20
! Error: Missing VLAN 1 (management); trunk negotiation fails
! Fix: Include VLAN 1 in allowed list (or native VLAN mismatch)
```

### 7.4 MISTAKE: Physical Interface Not Activated
```
Router(config)# ! Forgot "no shutdown" on g0/0
! Error: Subinterfaces won't activate
! Fix: Always enable parent interface before subinterfaces
```

### 7.5 MISTAKE: Testing with DHCP Clients
```
PC1# ipconfig /all  ← Shows DHCP server configured
! Error: Proves network depends on external connectivity
! Fix: Pre-provision all PCs with static IPs for Field-1
```

## 8. Troubleshooting by Field (Field-1: Offline Diagnostics)

### 8.1 Subinterface Won't Activate After Cold-Start
```
! Diagnostic approach:
! 1. Check if parent interface is down
Router# show int g0/0 | include (is up|is down)
! If down → parent needs "no shutdown"

! 2. Check if config is in running-config
Router# show running-config | include interface g0/0

! 3. Check NVRAM has startup-config
Router# show startup-config | include interface g0/0

! Field-1 Fix:
! a) Power cycle (or reload)
! b) Verify startup-config loads automatically
! c) If not → use "config-register 0x2102" to boot from NVRAM
```

### 8.2 Inter-VLAN Ping Fails Offline
```
! Diagnostic: Does ping work while plugged into internet?
PC1> ping 10.0.20.10  ← Works with external access
! Then unplug internet and retry
PC1> ping 10.0.20.10  ← Fails
! Problem: Config has external dependency (DHCP, NTP, etc.)

! Field-1 Fix:
! 1. Verify PCs have static IPs (no DHCP)
! 2. Verify router has no external routes (no DHCP relay)
! 3. Check: Router# show ip route | exclude (dynamic|static)
!    Should show ONLY connected routes
```

### 8.3 VLAN Database Lost After Power Loss
```
! Symptom: After power cycle, VLANs show only 1, 1002, 1003, etc.
Switch# show vlan brief
! Expected: VLAN 10, 20 present

! Diagnostic:
Switch# show flash:vlan.dat
! File should exist (stores VLAN database)

! Field-1 Fix:
! 1. Erase VLAN database and recreate
Switch# delete vlan.dat
Switch# reload
! 2. Reconfigure VLANs (they'll be saved to vlan.dat)
```

## 9. Design Analysis (Why for Field-1)

**Why Offline-Resilient ROAS for Haiti P38?**

1. **Power Unreliability:** Haiti pilot sites lose power 6+ hours/day
   - Internet connectivity dependent on power
   - Network must route between departments during outages
   - ROAS scales better than static routes for 4-8 VLANs

2. **No Management Access During Outages**
   - Cannot SSH into router when network is down
   - Configuration must be pre-cached in NVRAM
   - Cold-start must succeed with zero human intervention
   - Proves "self-healing" capability

3. **ROAS vs. Alternatives**
   - **L3 Switch:** More expensive, higher power consumption (defeats offline goal)
   - **Static Routes:** Scales poorly (one route per subnet pair)
   - **ROAS:** Good tradeoff—simple, low-power, scales to 8-10 VLANs
   
4. **Offline Validation Proof**
   - This lab demonstrates ROAS can be deployed "write once, run 6+ hours offline"
   - Proves Haiti P38 pilot can operate departments during power loss
   - Enables realistic field deployment without grid power dependency

## 10. Real-World Parallel (Haiti Deployment)

**Haiti P38 Pilot (50 nodes, Q4 2026):**
- 5 sites with multiple departments: Education, Health, Commerce, Governance
- Average 6 hours/day power loss
- Internet available only during backup generator operation (4 hours/day)

**ROAS Deployment at Port-au-Prince Hub:**
- 4 VLANs: Education (VLAN 10), Health (VLAN 20), Commerce (VLAN 30), Governance (VLAN 40)
- UPS-backed core switch + 1921 router with SFP + 2960 access switches
- All VLAN configs cached in NVRAM on power-up
- **SLA:** Inter-VLAN routing available within 30 seconds of power restoration

**P38 Validation Gate:**
- ✓ Ping across VLANs works after 6-hour power outage
- ✓ No network management access required post-outage
- ✓ All PCs reconnect and reach gateways autonomously (static IPs pre-configured)
- ✓ No external dependency (DNS, NTP, DHCP) required

**Phase Gate:** Approved for P38 pilot if cold-start ROAS works 5 consecutive times.

## 11. Stretch Goals (Field-1 Advanced)

1. **Add Third VLAN (VLAN 30) Offline**
   - Configure VLAN 30 on all switches, save to NVRAM
   - Power-cycle and verify VLAN 30 persists
   - Prove inter-VLAN routing for all 3 VLANs works offline

2. **Measure Cold-Start Speed**
   - Use Wireshark to capture packets BEFORE/AFTER reload
   - Record time from power-on to first successful inter-VLAN ping
   - Target: < 30 seconds (document actual time)

3. **Simulate 12-Hour Offline Operation**
   - Isolate network from internet for 12 hours
   - Periodically ping across VLANs (every 2 hours)
   - Verify zero configuration drift

4. **Implement Emergency Shutdown Sequence**
   - Document pre-outage checklist (all configs saved, NVRAM verified)
   - Create "cold-start playbook" for field operator
   - Test playbook with new operator (no prior network experience)

5. **Test with Corrupted Config**
   - Intentionally corrupt startup-config (hex editor)
   - Verify reload fails gracefully (doesn't hang)
   - Demonstrate manual recovery (restore from flash:offline-cache.cfg)

## 12. Self-Assessment (Field-1 Black Start Levels)

- **BSL-1 (Offline Deploy Ready):** Configure ROAS with 2 VLANs, write memory, verify cold-start works after reload
- **BSL-2 (Offline Operations):** Add third VLAN, demonstrate inter-VLAN ping survives 6-hour isolation, document config persistence
- **BSL-3 (Field Validation):** Measure cold-start time (record <30s), verify no external dependencies (no DHCP/DNS logs), create operator playbook
- **BSL-4 (Offline Resilience Proof):** Test 5 consecutive power cycles, measure average cold-start time, document variance
- **BSL-5 (Haiti P38 Pre-Deployment):** Deploy to 3-node testbed, survive 12-hour isolation, train field operators, pass validation gate
- **BSL-6 (Operational Excellence):** Implement monitoring for VLAN state, create automated cold-start verification, design redundant ROAS with failover
- **BSL-7 (Field Deployment Authority):** Deploy to 5-site Haiti P38 pilot, validate all nodes meet cold-start SLA, author field ops manual, mentor remote teams

---

**End of Day-13 Field-1 Lab**
**Research Field:** Black Start (Offline Resilience) | **Haiti Phase:** P38 (Pilot)
**Generated for:** CCNA VLAN & STP Research Program
