# Day 12: Basic Routing (Inter-VLAN) (Field 1: Black Start)

## 0. Metadata

- **Objective:** Prove Basic Routing (Inter-VLAN) functionality in Black Start (Field 1) constraints
- **Research Field:** Field 1: Black Start
- **Proof Obligations:**
  - Validate Basic Routing (Inter-VLAN) works without external dependencies (Field 1) / under stress (Field 2) / in mesh topology (Field 3) / at Haiti scale (Field 7)
  - Document convergence time and resource usage
  - Prove resilience to field-specific failure modes
- **Haiti Deployment Phase:** P38 (50-node pilot)
- **Relevant RFC/Standards:** IEEE 802.3 (Ethernet), RFC 791 (IPv4), RFC 1918 (Private Addresses)
- **Prerequisites:** Day 12 base lab manual + Field 1 environment setup
- **Estimated Time:** 150-180 minutes (includes stress testing)
- **Difficulty:** Advanced
- **Hardware Required:** 4-6 routers/switches, 6-8 PCs, stress injection appliance (Field 2) or mesh topology (Field 3)
- **Key Concepts:** Field-optimized Basic Routing (Inter-VLAN), Black Start-specific validation, proof obligations, real-world constraints

## 1. Business Context

Haiti P38 pilot sites experience frequent power losses (avg. 6 hours/day) and unreliable internet.
This lab validates that Basic Routing (Inter-VLAN) works in **offline-only mode**:
- Network must function without external connectivity
- Cached configurations and routing tables must be stable
- No dynamic updates expected until power/internet restored
- Cold-start scenarios are realistic and must work flawlessly

**Why this matters:** Operators in remote areas cannot rely on central management. Basic Routing (Inter-VLAN) must work autonomously.

## 2. Topology Diagram (Field 1: Black Start)

```
        [Offline Cache Storage Node]
                    |
                    |
         +----------+----------+
         |                     |
      [R1]                  [SW1]
      Core           Access Switch
      (no internet)        |
         |                 +---[PC1]
         |                 +---[PC2]
         |
      [R2]
    (backup)

Key: No internet gateway. All routes must be pre-configured or cached.
Topology notes:
- Remove all external connectivity (internet gateways, cloud links)
- Add offline storage/cache node for state persistence
- Test: Can Basic Routing (Inter-VLAN) survive power loss? Is state recovered from cache?
- Offline operation model: Routing tables static until power restored
```

**Modifications for Field 1:**
- Remove internet gateway / external connectivity
- Add offline cache storage to archive routing tables
- Test Basic Routing (Inter-VLAN) in "dark mode" (no external dependencies)
- Validate cold-start after simulated power loss

## 3. IP Addressing Plan

| Device | Role | Subnet | Address | Mask | Notes |
|--------|------|--------|---------|------|-------|
| R1 | Primary | 10.0.12.0/24 | 10.0.12.1 | /24 | Field 1 core router |
| R2 | Secondary | 10.0.12.0/24 | 10.0.12.2 | /24 | Backup/mesh peer |
| SW1 | Access | 10.0.12.0/24 | 10.0.12.254 | /24 | Access switch VLAN |
| PC1 | Client | 10.0.12.0/24 | 10.0.12.10 | /24 | Test client 1 |
| PC2 | Client | 10.0.12.0/24 | 10.0.12.20 | /24 | Test client 2 |

**Field 1 specific notes:**
- Subnets chosen to test Day 12 concepts in isolation
- Avoid public IP ranges; use RFC 1918 private addresses throughout
- No external connectivity in Field 1 (black start)
- Stress injection may cause addresses to become unreachable temporarily (Field 2)
- Mesh topology (Field 3) requires all nodes reachable by some path

## 4. Pre-Config Checklist

- [ ] Console cable connected to all devices
- [ ] IOS/GNS3 image verified on routers and switches
- [ ] Physical cabling complete
- [ ] Management IP configured on switches
- [ ] Router power-on and initial config ready
- [ ] Offline cache storage node powered and ready
- [ ] All internet gateways disabled (no external connectivity)
- [ ] Power loss simulator ready (simulate outages)
- [ ] Cold-start validation plan documented

## 5. Field-Specific Configuration

### 5.1 Common Configuration (All Fields)

```
! Standard initial configuration for Day 12: Basic Routing (Inter-VLAN)
Router> en
Router# conf t

! Hostname
Router(config)# hostname R1

! Clock setting
Router(config)# clock rate 64000

! Line configuration
Router(config)# line con 0
Router(config-line)# logging synchronous
Router(config-line)# exit

Router(config)# line vty 0 4
Router(config-line)# password class
Router(config-line)# login
Router(config-line)# exit

! Save
Router(config)# end
Router# write memory
```

### 5.2 Field 1 Specific Configuration


```
! Field 1: Black Start - Configure offline operation
! Remove dynamic updates, rely on cached tables

Router(config)# int g0/0
Router(config-if)# ip address 10.0.12.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

! Disable routing protocol updates (no dynamic routing for offline)
! Static routes only
Router(config)# ip route 10.0.12.0 255.255.255.0 10.0.12.1

! Cache configuration to startup-config
Router# write memory

! Test offline mode: Unplug internet gateway, verify routing works
! Verification step below in Section 5
```

## 6. Field-Specific Verification Steps

### 6.1 Basic Connectivity Test
```
Router# show ip int brief
Router# show ip route
Router# ping 10.0.12.10
```

### 6.2 Field 1 Specific Verification


### 6.2.1 Offline Operation Validation (Field 1)
```
! Step 1: Verify cached routing table
Router# show ip route
C 10.0.12.0/24 is directly connected, GigabitEthernet0/0

! Step 2: Unplug internet gateway (simulate offline)
! (Do this physically or via shutdown)

! Step 3: Verify routing still works
PC1# ping 10.0.12.10
Reply from 10.0.12.10: bytes=32 time=5ms

! Expected: Routing works without internet for at least 2 hours (cache expiry)
! Success: All pings reply within SLA
```

## 7. Expected Output Gallery (Field 1)

### 7.1 Router Interface Status
```
Router# show ip int brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.12.1    YES manual up                    up
GigabitEthernet0/1         10.0.12.11   YES manual up                    up
Serial0/0                  10.0.12.2    YES manual up                    up
```

### 7.2 Routing Table (Field 1)
```
Router# show ip route
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area

C     10.0.12.0/24 is directly connected, GigabitEthernet0/0
C     10.0.12.11/24 is directly connected, GigabitEthernet0/1
C     10.0.12.2/24 is directly connected, Serial0/0
```

### 7.3 Ping Output (Normal and Under Stress)
```
PC1# ping 10.0.12.10 -c 5
Request sent from ICMP seq=1, timeout=20ms
Reply from 10.0.12.10: bytes=32 time=5ms TTL=63
Reply from 10.0.12.10: bytes=32 time=6ms TTL=63
Reply from 10.0.12.10: bytes=32 time=7ms TTL=63
Reply from 10.0.12.10: bytes=32 time=5ms TTL=63
Reply from 10.0.12.10: bytes=32 time=6ms TTL=63
Sent=5, Received=5, Lost=0% (0), Minimum=5ms, Average=5.8ms, Maximum=7ms
```

## 8. Common Mistakes (Field 1: Black Start)

1. **Leaving internet gateway enabled**
   - Problem: Cache never tested because live internet is available
   - Fix: Explicitly disable all external connectivity before test
   - Verify: No ping to 8.8.8.8 succeeds

2. **Not pre-populating cache before offline test**
   - Problem: Routes disappear when internet disconnected
   - Fix: Run network normally for 5+ minutes, then test offline
   - Verify: `show ip route` shows routes even after disconnect

3. **Timeout too short for offline validation**
   - Problem: Cache expires before test completes
   - Fix: Extend routing table expiry to 2+ hours
   - Verify: Tables persist through entire offline window

## 9. Troubleshooting (Field 1: Black Start)

**Problem: Routes disappear after internet disconnect**
```
Router# show ip route
Router#  ! Empty! Routes gone.
```
**Diagnosis:**
- Check cache timeout: `show running-config | include route cache`
- Verify cache is populated: Before disconnecting, `show ip route` should show 10+ routes

**Solution:**
```
Router(config)# ip cache timeout 7200  ! 2 hours
Router# write memory
! Then reconnect internet, wait 2 minutes, then test disconnect
```

**Problem: Power loss not simulated correctly**
**Diagnosis:**
- Not actually powering off router (just shutting down interface)
- Fix: Use actual power loss simulator or GNS3's power loss feature

**Solution:**
```
! In GNS3, right-click router → Stop (power off)
! Wait 30 seconds
! Right-click router → Start (power on)
! Verify cache and offline operation still work
```

## 10. Design Analysis (Field 1: Black Start)

**Why offline-only topology for Basic Routing (Inter-VLAN)?**

In Haiti P38 sites:
- Power cuts are frequent (avg. 6 hours/day)
- Internet is unreliable (latency 500ms+, loss 10%+)
- Operators cannot rely on central management or cloud backup

The offline-only design proves Basic Routing (Inter-VLAN) works **without** these dependencies:
1. **No internet dependency:** Network functions in complete isolation
2. **Cached state:** Routing tables, configurations pre-stored locally
3. **Cold-start validation:** Power loss → recovery → full operation in < 5 minutes
4. **Autonomous operation:** No central controller, no cloud sync

**Key metric:** Time to recover from power loss
- Expected: < 5 minutes to full operational status
- Validates: Basic Routing (Inter-VLAN) is truly offline-capable for Haiti deployment

## 11. Real-World Parallel (Field 1: Black Start)

**Haiti P38 Pilot Site (Port-au-Prince region):**

Location: Rural area, 40km from Port-au-Prince
- Power: Diesel backup generator (runs 6 hours during outages)
- Internet: Satellite link via Intelsat (500ms latency)
- Operators: 2-3 technicians per site (no central network team)

Actual deployment scenario:
1. Site powers up after overnight outage
2. Generator boots, network must be operational within 5 minutes
3. Technician verifies: Routing tables cached and intact
4. Basic Routing (Inter-VLAN) works autonomously without cloud sync
5. Satellite link eventually comes up (operator manually restarts)

**This lab simulates steps 1-4:**
- Power loss: Use GNS3 power-down feature
- Offline operation: No internet connectivity enabled
- Recovery: Verify all routes present after boot
- Success: Basic Routing (Inter-VLAN) validated for real Haiti deployment

## 12. Stretch Goals (Field 1: Black Start)

1. **Cache invalidation handling**
   - Implement cache expiry timer (e.g., 2 hours)
   - Test: Verify routes expire gracefully
   - Bonus: Implement manual cache flush command

2. **Cold-start from completely empty state**
   - Delete all routing tables
   - Power up device with zero configuration
   - Test: Boot-strap minimal routing (1-2 static routes)

3. **Backup generator timing validation**
   - Simulate power loss during convergence
   - Measure: Time to regain stability after generator boot
   - Document: Max acceptable switchover time (< 5 minutes)

4. **Prove offline operation with 10+ hour power outage**
   - Extended test (10+ hours without internet)
   - Verify: Network still operational
   - Monitor: Resource usage (cache doesn't bloat)

## 13. Self-Assessment (Field 1: Black Start)

**BSL-1 (Remember):** Understand offline operation concept
- [ ] Explain why offline mode matters for Haiti P38
- [ ] Name 3 constraints of black-start networks
- [ ] Describe cache expiry timeout

**BSL-2 (Understand):** Configure and verify offline operation
- [ ] Configure router with offline cache
- [ ] Disable internet connectivity and test routing
- [ ] Measure cache persistence time

**BSL-3 (Apply):** Design offline-capable network
- [ ] Design 10-node network with offline cache
- [ ] Calculate cache size needed for 2-hour operation
- [ ] Document cold-start procedure

**BSL-4 (Analyze):** Troubleshoot offline failures
- [ ] Identify why routes expired (cache issue?)
- [ ] Propose cache optimization for larger networks
- [ ] Compare offline vs. online convergence times

**BSL-5 (Evaluate):** Prove offline operation for Haiti
- [ ] Run 10-hour offline test, document results
- [ ] Verify cache never corrupted during stress
- [ ] Assess: Is this design production-ready?

**BSL-6 (Create):** Optimize offline design for Haiti scale
- [ ] Propose cache compression (reduce storage footprint)
- [ ] Design hybrid online/offline mode (fallback strategy)
- [ ] Create operations manual for Haiti technicians

**BSL-7 (Publish):** Deploy and validate in Haiti
- [ ] Deploy lab design to Haiti P38 pilot site
- [ ] Collect 30+ days operational data
- [ ] Publish findings (research paper, deployment guide)
