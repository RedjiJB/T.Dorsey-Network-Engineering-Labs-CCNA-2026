# Day 13: VLAN Routing & Inter-VLAN Communication (Geomagnetic Field)

## 0. Metadata
- **Objective:** Implement ROAS with convergence resilience under simulated geomagnetic stress (link jitter/loss)
- **Research Field:** Field-2: Geomagnetic (Space-Weather Resilience)
- **Proof Obligations:** Inter-VLAN routing converges in < 60 seconds under ±20% latency jitter and ±5% packet loss
- **Haiti Deployment Phase:** P38 (stress-tested pilot, proof of concept)
- **Relevant RFC/Standards:** IEEE 802.1Q, RFC 5737, geomagnetic event profiles (NOAA Space Weather)
- **Prerequisites:** Days 1-12 + Field-2 prerequisites (jitter injection, packet loss simulation)
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced (stress testing, timing analysis)
- **Hardware Required:** 1 router, 2 switches, 3 PCs, traffic generator, jitter/loss injection device
- **Key Concepts:** ROAS convergence timing, jitter injection, latency variance, stress-tested routing

## 1. Business Context (Field-2: Geomagnetic Resilience)
Haiti's equatorial location exposes networks to space-weather events: geomagnetic storms cause ionospheric disturbances, satellite signal degradation, and terrestrial link jitter. This lab proves ROAS inter-VLAN routing survives simulated geomagnetic stress:

**Real Scenario:** Geomagnetic storm causes link from core switch to access switch to experience ±20% latency variation (e.g., 10ms baseline → 8-12ms jitter) and occasional packet loss (5%). Field operators need confirmation that VLAN routing remains available during event.

**Success Metric:** Inter-VLAN pings resume within 60 seconds; convergence time measured and documented.

## 2. Topology Diagram (Geomagnetic Stress-Testing)
```
┌──────────────────────────────────────────────┐
│         [Router R1 + Jitter Injector]        │
│         (Subinterfaces G0/0.10, G0/0.20)     │
│            |                                 │
│       ┌────┴────┐                            │
│       │  VLAN   │ ← 802.1Q Trunk            │
│       │ Tagging │ ± 20% jitter injected     │
│       │         │ ±5% packet loss injected   │
│       └────┬────┘                            │
│            |                                 │
│       [SW1: Core]                            │
│       /           \                          │
│    (delay +jitter) (delay +jitter)          │
│   /                 \                        │
│ [SW2]             [SW3]                      │
│  |                   |                       │
│ PC1 (VLAN 10)    PC2 (VLAN 20)             │
│ 10.0.10.10       10.0.20.10                 │
│                                              │
│ **WAN Link Simulation:**                     │
│ Baseline latency: 20ms                       │
│ Jitter range: ±20% (16-24ms)                │
│ Packet loss: ±5%                             │
└──────────────────────────────────────────────┘
```

**Field-2 Modifications:**
- Inject jitter on router→switch trunk (8-12% variance)
- Add packet loss on WAN side (3-7% random loss)
- Measure convergence time when stress injected
- Monitor for routing table instability

## 3. IP Addressing Plan (Geomagnetic Stress Profile)
| Device | VLAN | IP Address | Jitter Profile | Loss Profile | Notes |
|--------|------|-----------|----------------|--------------|-------|
| PC1 | 10 | 10.0.10.10 | ±0% (local) | 0% (local) | Baseline |
| PC2 | 20 | 10.0.20.10 | ±20% (WAN) | 5% (WAN) | Geomagnetic stress |
| R1 | 10 | 10.0.10.1 | N/A | N/A | Router gateway |
| R1 | 20 | 10.0.20.1 | N/A | N/A | Router gateway |

## 4. Field-2-Specific Configuration

### 4.1 Router Configuration (Baseline ROAS)
```
Router> en
Router# conf t

! Physical interface
Router(config)# int g0/0
Router(config-if)# no shutdown
Router(config-if)# exit

! VLAN 10 subinterface
Router(config)# int g0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 10.0.10.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

! VLAN 20 subinterface
Router(config)# int g0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 10.0.20.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# end
Router# write memory
```

### 4.2 Jitter Injection on WAN Links (Field-2 Specific)
```
! Simulate geomagnetic link degradation
Router(config)# int g0/0
Router(config-if)# delay 20000  ! Baseline 20ms
! Note: Delay in tens of microseconds (20000 = 20ms)
Router(config-if)# exit

! GNS3/PT: Add Network Link Impairment module
! - Jitter: ±20% (mean 20ms, variance 4ms)
! - Packet Loss: 5% (simulate atmospheric absorption)
! - Burst Loss: 2-3 packet sequences (simulate phase shift)
```

### 4.3 Stress Testing Sequence
```
! On Router, set up baseline routing
Router# show ip route connected
! Expected: 10.0.10.0/24 and 10.0.20.0/24 connected

! On Traffic Generator or PC1:
PC1# ping 10.0.20.1 -t
! Collect baseline latency (should be ~20ms without jitter)

! Enable jitter injection (GNS3/PT:)
! Increase delay to 20-24ms range

! Monitor ping response times
! Expected: Latency increases by ~4ms, but responses continue

! Inject packet loss (5%)
! Monitor ping statistics (may see 1-5% lost packets)

! Field-2 Validation:
! - Ping responses resume within 60 seconds
! - Routing table remains stable (show ip route unchanged)
! - No subinterface flaps (show int status unchanged)
```

## 5. Field-2-Specific Verification Steps

### 5.1 Baseline Convergence Test (No Stress)
```
! Baseline latency measurement
Router# show int g0/0 | include delay
! Expected: delay 20000 (20ms baseline)

! Measure ping response time
PC1# ping 10.0.20.10 -c 10 > baseline.txt
! Document average latency (expected ~20-25ms with 802.1Q overhead)
```

### 5.2 Geomagnetic Jitter Test
```
! Phase 1: Verify baseline works
PC1# ping 10.0.20.10  ← Should work fine (no jitter yet)

! Phase 2: Inject jitter
! (GNS3/PT: Modify link impairment to add ±20% jitter)
! This means:
!   - Baseline 20ms → Jitter range 16-24ms
!   - Simulates geomagnetic-caused ionospheric delay

! Phase 3: Monitor convergence
PC1# ping 10.0.20.10 -c 100 | tee geomag_jitter.log
! Watch for:
!   - Latency increases (may see 20-24ms)
!   - Timeout count (should be 0 if routing converges)
!   - Time to first successful ping after stress (< 60 seconds)

! Phase 4: Verify routing stability
Router# show int g0/0.10 | include (up|down)
! Expected: "is up, line protocol is up" (no flaps)

Router# show ip route
! Expected: Both connected routes present (no loss)
```

### 5.3 Packet Loss Under Stress
```
! Phase 1: Inject 5% packet loss
! (GNS3/PT: Set random packet loss 5%)

! Phase 2: Run continuous ping
PC1# ping 10.0.20.10 -c 200 > stress_loss.txt
! Analyze results:
!   - Lost packets expected: ~10 out of 200 (5%)
!   - Minimum latency: Should stay >= 16ms (with jitter)
!   - Maximum latency: Should stay <= 24ms (with jitter)

! Phase 3: Verify routing resilience
! No routing updates should occur despite packet loss
Router# show ip ospf neighbor  ! (if OSPF enabled for comparison)
! Expected: Neighbors should NOT flap due to 5% loss
```

### 5.4 Convergence Time Measurement (Field-2 Critical)
```
! Setup: Continuous ping running in background
PC1# ping 10.0.20.10 -t > convergence.log &

! Simulate geomagnetic event: Disable and re-enable trunk
Router(config)# int g0/0
Router(config-if)# shutdown
Router(config-if)# exit
! [Note time: T0]

! Wait 5 seconds to ensure all pings fail
! Then restore link
Router(config)# int g0/0
Router(config-if)# no shutdown
Router(config-if)# exit
! [Note time: T1 when first ping succeeds]

! Convergence Time = T1 - T0
! Field-2 Target: < 60 seconds
! Field-2 Ideal: < 30 seconds

! Verify result:
! grep "Reply" convergence.log | head -1  ← First successful ping
! Measure time from shutdown to first reply
```

## 6. Expected Output Gallery (Geomagnetic Stress)

### 6.1 Ping with Jitter (±20% Latency Variance)
```
PC1> ping 10.0.20.10 -c 5
Pinging 10.0.20.10 with 32 bytes of data:
Reply from 10.0.20.10: bytes=32 time=20ms TTL=63
Reply from 10.0.20.10: bytes=32 time=23ms TTL=63  ← Jitter: +3ms
Reply from 10.0.20.10: bytes=32 time=17ms TTL=63  ← Jitter: -3ms
Reply from 10.0.20.10: bytes=32 time=21ms TTL=63
Reply from 10.0.20.10: bytes=32 time=22ms TTL=63

Min=17ms, Max=23ms, Avg=20.6ms, StdDev=2.1ms
→ Jitter successfully injected; ROAS converges through it
```

### 6.2 Convergence After Link Failure (With Stress)
```
PC1> ping 10.0.20.10 -t
[… pings working at ~20ms …]
[Link disabled at T=0]
Request timed out.
Request timed out.
Request timed out.
[Link restored at T=45 seconds]
Reply from 10.0.20.10: bytes=32 time=22ms TTL=63  ← T=45s: First reply
Reply from 10.0.20.10: bytes=32 time=20ms TTL=63
Reply from 10.0.20.10: bytes=32 time=21ms TTL=63

Convergence Time: 45 seconds (< 60s target) ✓
```

### 6.3 Routing Table Stability (No Flaps)
```
Router# show ip route
Codes: C - connected, S - static, ...
C     10.0.10.0/24 is directly connected, GigabitEthernet0/0.10
C     10.0.20.0/24 is directly connected, GigabitEthernet0/0.20
[Routes remain unchanged throughout jitter injection]
```

## 7. Common Field-2-Specific Mistakes

### 7.1 MISTAKE: Not Measuring Convergence Time
```
! Error: "Ping works, so routing is fine"
! Field-2 Fix: ALWAYS measure time from failure to recovery
! Use timestamps in logs to calculate convergence time
! Document actual vs. target (< 60s)
```

### 7.2 MISTAKE: Injecting Too Much Jitter
```
! Error: ±50% jitter (15-30ms) is NOT geomagnetic-realistic
! Field-2 Fix: Use ±20% jitter (16-24ms) based on NOAA profiles
! This reflects actual space-weather ionospheric delay
```

### 7.3 MISTAKE: Not Testing Under Combined Stress
```
! Error: Test jitter only, OR packet loss only
! Field-2 Fix: Combine jitter + loss (realistic geomagnetic events)
! ±20% jitter + 5% loss together
```

### 7.4 MISTAKE: Monitoring Ping Only
```
! Error: "Ping worked, so ROAS is fine"
! Field-2 Fix: Verify routing table didn't update (no flaps)
! Check: show ip route, show int status, show ip ospf neighbor
```

## 8. Troubleshooting by Field (Field-2: Geomagnetic Stress)

### 8.1 Convergence Time > 60 Seconds
```
! Symptom: After simulated geomagnetic stress, ROAS takes 90+ seconds to recover

! Diagnostic:
Router# show ip route  ← Check if routes still present
Router# show int status  ← Check for interface flaps
Router# show int g0/0 | include transitions  ← Count resets

! Field-2 Root Cause: Usually subinterface flapping (goes down/up multiple times)
! Fix: Verify subinterface uses proper encapsulation
! Router# show int g0/0.10 | include (Encapsulation|up)
! Ensure "Encapsulation 802.1Q" is present
```

### 8.2 Ping Timeouts During Jitter
```
! Symptom: ~5-10% of pings timeout even without packet loss injection

! Diagnostic: This is normal under ±20% jitter + stress
! Some packets may exceed timeout window (usually 2 seconds)

! Field-2 Fix:
! - Increase ping timeout: ping 10.0.20.10 -w 5000 (5 second timeout)
! - Or verify jitter injection is exactly ±20% (not higher)
! - Confirm this is acceptable for Haiti field ops
```

### 8.3 Routing Table Updates Observed During Stress
```
! Symptom: show ip route shows routes disappear/reappear during jitter

! Field-2 Fix: This suggests subinterface is flapping
! Check interface status during stress:
Router# debug int g0/0
[Monitor output while jitter is injected]
! Should see minimal interface state changes
! If seeing constant "up/down" transitions → investigate encapsulation
```

## 9. Design Analysis (Why for Field-2)

**Why Geomagnetic Stress Testing for Haiti?**

1. **Equatorial Vulnerability:** Haiti's latitude (19°N) is below the "auroral oval" but within ionospheric storm zone
   - Geomagnetic storms → ionospheric disturbances
   - Disturbances → satellite delay variance (±20% typical)
   - Terrestrial links also experience phase shift (simulated by jitter)

2. **Haiti Cell Tower Reality (P38 Context)**
   - Cellular backhaul often uses point-to-point links (terrestrial microwave or satellite)
   - Geomagnetic events cause phase modulation → latency variance
   - Must prove routing survives this, not just static links

3. **ROAS Convergence Under Stress**
   - ROAS doesn't have convergence like OSPF (no timers)
   - But subinterfaces can flap under extreme jitter
   - This lab proves subinterfaces stable under geomagnetic profiles

4. **Proof Obligation for P38**
   - Show that ROAS routing survives observed geomagnetic profiles
   - Document convergence time (should be < 30s for seamless)
   - Prove P38 field ops can rely on ROAS during space-weather events

## 10. Real-World Parallel (Haiti Deployment)

**Haiti P38 Pilot (Geomagnetic Stress Scenario):**
- Port-au-Prince hub site uses satellite backhaul (due to infrastructure)
- Geomagnetic storm forecast issued by NOAA
- Field operator expects network stress during event
- **Question:** Will inter-departmental VLAN routing remain available?

**ROAS Deployment with Field-2 Validation:**
- Router configured with ROAS for 4 VLANs (Education, Health, Commerce, Governance)
- Lab tests ROAS under ±20% latency + 5% loss (geomagnetic profile)
- Convergence time measured: 25 seconds average
- **Result:** ROAS meets P38 requirement (< 60s recovery, ideally < 30s)

**P38 Operational Decision:**
- IF: Convergence < 30s consistently → Deploy ROAS, accept geomagnetic risk
- IF: Convergence > 60s → Consider alternative (L3 switch or static routes)
- IF: Subinterfaces flap > 3 times → Investigate root cause before P38 deployment

## 11. Stretch Goals (Field-2 Advanced)

1. **Measure Actual Geomagnetic Event Profile**
   - Download DSCOVR solar wind data (NOAA)
   - Map latency profiles to actual Kp index (geomagnetic severity)
   - Reproduce real-world jitter + loss based on observed data

2. **Extended Stress Duration Test**
   - Apply ±20% jitter + 5% loss continuously for 30 minutes
   - Verify ROAS routing remains stable (no config drift)
   - Measure packet retransmission rate (expected minimal)

3. **Document Convergence Statistics**
   - Run 10 convergence tests (link down/up cycles)
   - Record all 10 convergence times
   - Calculate mean, stddev, min, max
   - Demonstrate consistency (variance < 10s)

4. **Test with Multiple VLANs Under Stress**
   - Add VLAN 30 to ROAS
   - Apply geomagnetic jitter to VLAN 10, 20 only (leave 30 baseline)
   - Verify VLAN 30 routing unaffected (proves isolation)

5. **Formalize SLA for Haiti P38**
   - Based on convergence test results, document Haiti SLA
   - "Inter-VLAN routing converges within 30 seconds under geomagnetic stress"
   - Sign off with field ops manager

## 12. Self-Assessment (Field-2 Geomagnetic Levels)

- **BSL-1 (Stress Test Ready):** Configure ROAS, inject ±20% jitter, measure baseline convergence time
- **BSL-2 (Geomagnetic Validation):** Add 5% packet loss, run convergence test under combined stress, document results
- **BSL-3 (Field Measurement):** Run 5 convergence tests, calculate mean + stddev, verify < 60s target
- **BSL-4 (Stress Profile Proof):** Run 30-minute extended stress test, verify routing stability, document packet loss patterns
- **BSL-5 (Haiti P38 Pre-Deployment):** Map NOAA geomagnetic data to lab profiles, document actual SLA (convergence time), train field ops
- **BSL-6 (Operational Resilience):** Implement monitoring for convergence anomalies, create automated alerts for geomagnetic events, design fallback strategy
- **BSL-7 (Field Deployment Authority):** Deploy ROAS to Haiti P38 pilot, monitor convergence during actual geomagnetic events, publish results, mentor field teams

---

**End of Day-13 Field-2 Lab**
**Research Field:** Geomagnetic (Space-Weather Resilience) | **Haiti Phase:** P38 (Stress-Tested Pilot)
**Generated for:** CCNA VLAN & STP Research Program
