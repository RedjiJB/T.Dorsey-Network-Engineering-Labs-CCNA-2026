# Day 09: Routing Protocols Intro (Field 2: Geomagnetic)

## 0. Metadata

- **Objective:** Prove Routing Protocols Intro functionality in Geomagnetic (Field 2) constraints
- **Research Field:** Field 2: Geomagnetic
- **Proof Obligations:**
  - Validate Routing Protocols Intro works without external dependencies (Field 1) / under stress (Field 2) / in mesh topology (Field 3) / at Haiti scale (Field 7)
  - Document convergence time and resource usage
  - Prove resilience to field-specific failure modes
- **Haiti Deployment Phase:** P45 (200-node expansion)
- **Relevant RFC/Standards:** IEEE 802.3 (Ethernet), RFC 791 (IPv4), RFC 1918 (Private Addresses)
- **Prerequisites:** Day 09 base lab manual + Field 2 environment setup
- **Estimated Time:** 150-180 minutes (includes stress testing)
- **Difficulty:** Advanced
- **Hardware Required:** 4-6 routers/switches, 6-8 PCs, stress injection appliance (Field 2) or mesh topology (Field 3)
- **Key Concepts:** Field-optimized Routing Protocols Intro, Geomagnetic-specific validation, proof obligations, real-world constraints

## 1. Business Context

Geomagnetic storms (Kp index 8-9) cause ionospheric disturbances that affect satellite and terrestrial links.
This lab simulates **space-weather stress** on Routing Protocols Intro:
- Links experience ±20% latency variation (jitter)
- Packet loss spikes to 5-10% during storms
- Convergence must complete in < 60 seconds
- Recovery must be deterministic and documented

**Why this matters:** Satellite networks and high-latitude deployments must handle geomagnetic events gracefully.

## 2. Topology Diagram (Field 2: Geomagnetic)

```
        [Internet Gateway]
             |
          [WAN Link w/ Jitter Injection]
             | (±20% latency, ±5% packet loss)
             |
         [R1]----------+
         Core          |
          |            |
          |         [Stress Generator]
          |      (simulates geomagnetic events)
          |            |
       [SW1]--------[R2]
       Local       Secondary
        |
     +--+--+
     |     |
   [PC1] [PC2]

Key: WAN links experience latency variation and packet loss.
Topology notes:
- Add jitter/loss injection points on WAN links
- Stress generator simulates ±20% latency spikes
- Test: Does Routing Protocols Intro converge within SLA under stress?
- Geomagnetic events = unpredictable latency, not just bandwidth reduction
```

**Modifications for Field 2:**
- Add latency/jitter injection on WAN links (±20%)
- Add packet loss injection (±5%)
- Baseline delay: 20ms → stressed: 24ms (±4ms jitter)
- Test Routing Protocols Intro convergence time under stress

## 3. IP Addressing Plan

| Device | Role | Subnet | Address | Mask | Notes |
|--------|------|--------|---------|------|-------|
| R1 | Primary | 10.0.09.0/24 | 10.0.09.1 | /24 | Field 2 core router |
| R2 | Secondary | 10.0.09.0/24 | 10.0.09.2 | /24 | Backup/mesh peer |
| SW1 | Access | 10.0.09.0/24 | 10.0.09.254 | /24 | Access switch VLAN |
| PC1 | Client | 10.0.09.0/24 | 10.0.09.10 | /24 | Test client 1 |
| PC2 | Client | 10.0.09.0/24 | 10.0.09.20 | /24 | Test client 2 |

**Field 2 specific notes:**
- Subnets chosen to test Day 09 concepts in isolation
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
- [ ] Latency/jitter injection appliance ready (or TC/netem configured)
- [ ] Baseline ping time measured (should be ~20ms)
- [ ] Packet loss injection configured (5%)
- [ ] Stress test timeline documented (when to inject stress)

## 5. Field-Specific Configuration

### 5.1 Common Configuration (All Fields)

```
! Standard initial configuration for Day 09: Routing Protocols Intro
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

### 5.2 Field 2 Specific Configuration


```
! Field 2: Geomagnetic - Simulate stress injection on WAN
! Add latency variation (jitter) and packet loss

Router(config)# int s0/0
Router(config-if)# ip address 10.0.09.2 255.255.255.0
Router(config-if)# bandwidth 1000
Router(config-if)# delay 20000  ! Baseline 20ms (in tens of microseconds)
Router(config-if)# no shutdown
Router(config-if)# exit

! On external stress appliance or GNS3, configure:
! tc qdisc add dev eth0 root netem delay 20ms 4ms jitter loss 5%

! This simulates:
! - Base delay: 20ms
! - Jitter: ±4ms (20% variation)
! - Packet loss: 5%

Router# write memory
```

## 6. Field-Specific Verification Steps

### 6.1 Basic Connectivity Test
```
Router# show ip int brief
Router# show ip route
Router# ping 10.0.09.10
```

### 6.2 Field 2 Specific Verification


### 6.2.2 Geomagnetic Stress Verification (Field 2)
```
! Step 1: Measure baseline convergence time
PC1# ping 10.0.09.2 -c 100 > /tmp/baseline.log &

! Step 2: Inject simulated geomagnetic stress
! On appliance/GNS3:
! tc qdisc change dev eth0 root netem delay 24ms 4ms loss 5%

! Step 3: Measure time until pings resume (convergence)
! Watch /tmp/baseline.log
! Expected: < 60 seconds for convergence

! Step 4: Verify neighbor relationships recovered
Router# show ip route
Router# show ip ospf neighbor

! Success metric: Convergence time documented and < 60 seconds
```

## 7. Expected Output Gallery (Field 2)

### 7.1 Router Interface Status
```
Router# show ip int brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.09.1    YES manual up                    up
GigabitEthernet0/1         10.0.09.11   YES manual up                    up
Serial0/0                  10.0.09.2    YES manual up                    up
```

### 7.2 Routing Table (Field 2)
```
Router# show ip route
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area

C     10.0.09.0/24 is directly connected, GigabitEthernet0/0
C     10.0.09.11/24 is directly connected, GigabitEthernet0/1
C     10.0.09.2/24 is directly connected, Serial0/0
```

### 7.3 Ping Output (Normal and Under Stress)
```
PC1# ping 10.0.09.10 -c 5
Request sent from ICMP seq=1, timeout=20ms
Reply from 10.0.09.10: bytes=32 time=5ms TTL=63
Reply from 10.0.09.10: bytes=32 time=6ms TTL=63
Reply from 10.0.09.10: bytes=32 time=7ms TTL=63
Reply from 10.0.09.10: bytes=32 time=5ms TTL=63
Reply from 10.0.09.10: bytes=32 time=6ms TTL=63
Sent=5, Received=5, Lost=0% (0), Minimum=5ms, Average=5.8ms, Maximum=7ms
```

## 8. Common Mistakes (Field 2: Geomagnetic)

1. **Only reducing bandwidth instead of adding jitter**
   - Problem: Latency variation is different from reduced bandwidth
   - Fix: Use `tc netem delay X variance Y` (jitter, not just loss)
   - Verify: `ping` shows variation in RTT (e.g., 20ms, 22ms, 19ms, 24ms)

2. **Not measuring baseline before stress injection**
   - Problem: Can't tell if improvement is real
   - Fix: Capture baseline convergence time first
   - Verify: Baseline document exists before starting stress tests

3. **Stress level too high (unrealistic)**
   - Problem: Test doesn't match actual geomagnetic events
   - Fix: Use NOAA Kp index data as reference (typically Kp ≤ 8 = ±20% jitter)
   - Verify: Stress parameters documented with Kp index reference

## 9. Troubleshooting (Field 2: Geomagnetic)

**Problem: Convergence time not measuring correctly**
```
Router# show ip ospf neighbor
! No output, but convergence time still long
```
**Diagnosis:**
- Jitter not actually applied to link
- Use `show int s0/0` to verify `delay` parameter

**Solution:**
```
Router# show int s0/0 | include delay
  delay 20000 microseconds
! (Should see delay configured)

! If not applied, use GNS3 built-in stress (right-click link → Bandwidth/Delay)
```

**Problem: Stress too high, convergence never happens**
**Diagnosis:**
- Jitter variance too large (e.g., ±50% instead of ±20%)
- Packet loss too high (e.g., 20% instead of 5%)

**Solution:**
- Reduce jitter to ±20% (4ms on 20ms baseline)
- Reduce loss to 5%
- Verify: Baseline works first, then incrementally increase stress

## 10. Design Analysis (Field 2: Geomagnetic)

**Why add jitter instead of just reducing bandwidth for Routing Protocols Intro?**

Geomagnetic storms cause **latency variation**, not just bandwidth reduction:
- Solar wind pressure → ionospheric disturbance
- Affected frequencies: Satellite, HF, some terrestrial links
- Effect: Packet delay becomes unpredictable (±20%)

Standard reduced-bandwidth simulation:
- Packet loss is predictable
- Latency is constant
- **Does NOT test:** Real geomagnetic effects

Jitter-based stress simulation:
- Latency varies unpredictably (±20%)
- Packet loss bursty (5% average, peaks higher)
- **Tests:** Real convergence resilience

**Key metric:** Convergence time under ±20% jitter + 5% loss
- Baseline (no stress): ~10 seconds
- Under stress (Field 2): ~30-60 seconds
- Success: Convergence always < 60 seconds

## 11. Real-World Parallel (Field 2: Geomagnetic)

**NOAA Space Weather Warning (Kp Index 8 Event):**

Date: May 11, 2024
- Kp Index: 8 (Major geomagnetic storm)
- Impact: ISS solar array tracking issues, some satellite comms degraded
- Regional effect: Haiti-US satellite link latency spike to 140ms (from 100ms)
- Duration: 4-6 hours

Network impact:
1. Routing convergence slows (delayed LSAs)
2. TCP retransmit timeouts increased
3. Recovery time extended from 10 seconds to 40 seconds

**This lab simulates the latency/loss impact:**
- Baseline: 20ms latency, 0% loss
- During event (Field 2): 24ms ±4ms jitter, 5% loss
- Success: Convergence still < 60 seconds
- Validates: Routing Protocols Intro survives real geomagnetic storms

## 12. Stretch Goals (Field 2: Geomagnetic)

1. **Replicate actual DSCOVR/GOES space weather data**
   - Download real geomagnetic storm logs from NOAA
   - Replay actual latency/loss patterns
   - Test: Does {topic} survive real events?

2. **Convergence time SLA validation**
   - Target: < 30 seconds under 20% jitter + 5% loss
   - Test: Run 100 convergence cycles
   - Document: Mean, median, P95, P99 convergence times

3. **Stress escalation ladder**
   - Start: 0% jitter, 0% loss (baseline)
   - Step 1: 10% jitter, 2% loss
   - Step 2: 20% jitter, 5% loss
   - Step 3: 30% jitter, 10% loss (catastrophic)
   - Test: At what point does convergence fail?

4. **Prove Kp-index correlation**
   - Collect real Kp index data (NOAA)
   - Map to latency variation: Kp 6-7 → ±15%, Kp 8 → ±20%, Kp 9 → ±30%
   - Validate: {topic} tuning for specific Kp levels

## 13. Self-Assessment (Field 2: Geomagnetic)

**BSL-1 (Remember):** Understand geomagnetic stress concept
- [ ] Explain Kp index and geomagnetic storms
- [ ] Name 3 effects of geomagnetic events on networks
- [ ] Describe jitter injection method

**BSL-2 (Understand):** Simulate and measure geomagnetic stress
- [ ] Inject 20% jitter + 5% loss on WAN link
- [ ] Measure baseline convergence time (no stress)
- [ ] Measure convergence time under stress

**BSL-3 (Apply):** Design convergence SLA for geomagnetic stress
- [ ] Calculate SLA: Convergence must complete in < 60 seconds under Kp 8
- [ ] Tune OSPF timers for faster convergence
- [ ] Document trade-offs (fast convergence vs. stability)

**BSL-4 (Analyze):** Compare convergence behaviors
- [ ] Analyze convergence traces (Wireshark LSA logs)
- [ ] Identify bottlenecks (SPF calculation? Neighbor timeout?)
- [ ] Propose optimizations for geomagnetic events

**BSL-5 (Evaluate):** Prove convergence SLA for Haiti
- [ ] Run 100 convergence cycles under geomagnetic stress
- [ ] Calculate: Mean, P95, P99 convergence times
- [ ] Assess: Does design meet SLA?

**BSL-6 (Create):** Optimize routing for geomagnetic resilience
- [ ] Design OSPF timer configuration optimized for space weather
- [ ] Propose alternative routing protocols (EIGRP, ISIS)
- [ ] Create geomagnetic event playbook (how to respond)

**BSL-7 (Publish):** Validate against real NOAA data
- [ ] Replay real geomagnetic storm logs from NOAA GOES
- [ ] Publish: "OSPF Resilience to Geomagnetic Storms" paper
- [ ] Present findings at networking conference
