# Day 14: VLAN Troubleshooting & Advanced Trunking (Geomagnetic Field)

## 0. Metadata
- **Objective:** Troubleshoot VLAN trunking under geomagnetic stress; verify STP stability with jitter-induced topology changes
- **Research Field:** Field-2: Geomagnetic (Space-Weather Resilience)
- **Proof Obligations:** Trunk convergence < 60 seconds under ±20% jitter + 5% loss; STP BPDUs remain valid despite link stress
- **Haiti Deployment Phase:** P38 (stress-tested pilot)
- **Relevant RFC/Standards:** IEEE 802.1D (STP/RSTP), geomagnetic event profiles
- **Prerequisites:** Days 1-13 + Field-2 prerequisites
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 3 switches, 1 router, 4-6 PCs, jitter/loss injector
- **Key Concepts:** VLAN convergence under stress, STP BPDU health, jitter impact on spanning tree

## 1. Business Context (Field-2: Geomagnetic)
Field-2 proves VLAN troubleshooting works **under geomagnetic stress conditions** (jitter + loss). Scenario: During space-weather event, VLAN trunks experience latency variance. Field operators need confirmation that STP spanning tree remains stable and VLAN troubleshooting is still possible.

**Success Metric:** Identify and resolve VLAN misconfigurations while geomagnetic stress (jitter + loss) active; convergence time < 60 seconds.

## 2. Topology Diagram (Stress-Tested VLAN Troubleshooting)
```
[SW1: Core]────Jitter Injected────[SW2]
    |              (±20%,5%)          |
    ↓              (stress)           ↓
[SW3]                              [SW4]
 |                                   |
PC1                                 PC2
V10                                 V20

STP BPDUs crossing jittered link
VLAN traffic convergence measured under stress
```

## 3. IP Addressing Plan (Stress Profile)
| Device | VLAN | IP Address | Latency | Loss | Notes |
|--------|------|-----------|---------|------|-------|
| PC1 | 10 | 10.0.10.10 | +20% jitter | 5% | Geomagnetic |
| PC2 | 20 | 10.0.20.10 | +20% jitter | 5% | Geomagnetic |

## 4. Field-2-Specific Configuration

### 4.1 Introduce Misconfiguration (Intentional for Learning)
```
Switch-2(config-if)# switchport trunk allowed vlan 1,10  ! Missing VLAN 20
! This creates troubleshooting scenario under stress
```

### 4.2 Inject Jitter on Trunk Link
```
! Apply geomagnetic stress to SW1-SW2 link
Router(config)# int serial0/0
Router(config-if)# delay 20000  ! 20ms baseline
Router(config-if)# exit
! GNS3/PT: Add ±20% jitter, 5% loss to this link

! Simulate BPDU jitter impact
! STP uses Hello timers (default 2s) - jitter may delay BPDUs
```

## 5. Field-2-Specific Verification Steps

### 5.1 Baseline Trunk Status (Before Stress)
```
Switch-1# show int status trunk
! Expected: All trunks up

! Measure STP convergence time (before stress)
! Disable SW2 trunk, time until SW3 recovers traffic
! Record baseline convergence: ~15 seconds
```

### 5.2 Stress-Induced Convergence Test
```
! Phase 1: Apply jitter + loss
! (Enable network impairment on SW1-SW2 link)

! Phase 2: Simulate trunk misconfiguration (SW2 blocks VLAN 20)
Switch-2(config-if)# switchport trunk allowed vlan 1,10
Switch-2(config-if)# exit

! Phase 3: Measure convergence under stress
PC1> ping 10.0.20.10 -t
! Record time until pings resume (through alternate path via SW3)
! Under geomagnetic stress, convergence may take 30-60 seconds

! Phase 4: Verify STP still converged correctly
Switch-1# show int status trunk
! All trunks should show consistent state despite jitter
```

### 5.3 BPDU Health Monitoring Under Stress
```
Switch# debug spanning-tree bpdu  ! Enable logging
! Observe BPDU arrival times during jitter
! Expected: BPDUs arrive but with increased latency variance
! If BPDU gap > 3× hello time (6 seconds) → port blocked

Switch# show spanning-tree summary  ! Verify STP converged
! Root bridge, root port, designated ports should be stable
```

## 6. Expected Output Gallery (Stress-Induced Troubleshooting)

### 6.1 Trunk Status with Misconfiguration + Stress
```
Switch-1# show int g0/1 switchport | include Allowed
Allowed Vlans: 1,10
! VLAN 20 missing (misconfiguration)

Switch-1# show int status trunk
Port        Status       Vlan Trunking
Gi0/1       trunking     1,10  (VLAN 20 blocked due to jitter-induced BPDU loss?)
```

### 6.2 Convergence Time Under Geomagnetic Stress
```
PC1> ping 10.0.20.10 (during stress injection)
[Ping fails for ~45 seconds during VLAN 20 traffic reroute]
Reply from 10.0.20.10: bytes=32 time=34ms TTL=63
[Convergence time: 45 seconds under ±20% jitter]
```

## 7. Common Field-2-Specific Mistakes

### 7.1 MISTAKE: Assuming Convergence = No Misconfiguration
```
! Error: Assume VLAN 20 unreachable due to jitter, not config error
! Field-2 Fix: Always check trunk allowed list first
! show int trunk | include allowed
```

### 7.2 MISTAKE: Not Measuring Convergence Under Stress
```
! Error: Assume same convergence time as baseline (wrong!)
! Field-2 Fix: Measure convergence with AND without stress
! Document both times, understand difference
```

## 8. Troubleshooting by Field

### 8.1 STP Flapping During Jitter
```
! Symptom: Spanning tree changes root port repeatedly during stress

! Field-2 Diagnostic:
Switch# show spanning-tree detail | include "port state changes"
! Record number of topology changes during 5-min stress test
! Expected: < 5 changes (if > 10 → STP instability)

! Root Cause: BPDU loss due to packet loss
! Fix: Verify jitter is only ±20% (not higher)
```

## 9. Design Analysis (Why for Field-2)
Geomagnetic stress testing for VLAN troubleshooting ensures Haiti field operators can diagnose issues **even during space-weather events**. Proves troubleshooting methodology robust to environmental stress.

## 10. Real-World Parallel
**Haiti P38 During Geomagnetic Event:** Field operator receives report "VLAN 20 not reachable." Must determine if misconfiguration or jitter-induced STP instability. This lab teaches diagnostic process under stress.

## 11. Stretch Goals
1. Measure convergence time across 10 stress cycles, calculate statistics
2. Implement STP BPDU rate-limiting to handle jitter better
3. Document geomagnetic impact on spanning tree recovery time

## 12. Self-Assessment (Field-2 BSL)
- **BSL-1:** Identify trunk misconfiguration under baseline conditions
- **BSL-2:** Identify same misconfiguration while jitter active
- **BSL-3:** Measure convergence time under stress, document vs. baseline
- **BSL-4:** Troubleshoot STP instability during geomagnetic events
- **BSL-5:** Deploy to Haiti P38, validate troubleshooting SLA during actual geomagnetic events

---

**End of Day-14 Field-2 Lab**
**Research Field:** Geomagnetic | **Haiti Phase:** P38
**Generated for:** CCNA VLAN & STP Research Program
