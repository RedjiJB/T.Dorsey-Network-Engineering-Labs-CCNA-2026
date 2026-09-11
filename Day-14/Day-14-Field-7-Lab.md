# Day 14: VLAN Troubleshooting & Advanced Trunking (Haiti P38+ Deployment)

## 0. Metadata
- **Objective:** Troubleshoot VLAN trunking at Haiti P38 scale (20 VLANs, 50 nodes) while maintaining offline resilience, geomagnetic stress handling, mesh integrity, and security enforcement
- **Research Field:** Field-7: Haiti Unified Deployment
- **Proof Obligations:** Troubleshoot 5-site mesh network offline; identify and fix misconfiguration under stress; preserve audit trail; restore service < 60s
- **Haiti Deployment Phase:** P38 (pilot, 50 nodes, 5 hubs)
- **Relevant RFC/Standards:** IEEE 802.1D, 802.1Q, HIPAA, geomagnetic resilience, Byzantine consensus
- **Prerequisites:** Days 1-13 + all Fields 1-6 prerequisites
- **Estimated Time:** 240 minutes
- **Difficulty:** Expert
- **Hardware Required:** 5-6 routers, 15-20 switches, 30-50 PCs, jitter injectors, syslog, cache storage, UPS
- **Key Concepts:** Integrated troubleshooting, distributed diagnostics, stress-tested repair, security-aware fixes, mesh resilience

## 1. Business Context (Field-7: Haiti P38 Operations)
Field-7 represents **operational reality of Haiti P38 pilot**: Troubleshoot VLAN issues across 5 regional hubs (50 nodes) while simultaneously managing offline operation, geomagnetic stress, mesh reliability, and HIPAA compliance.

**Real Scenario:** Network alarm: "Healthcare VLAN 15 unreachable from 3 sites." Operator must:
1. Diagnose offline (internet down during power outage)
2. Fix with geomagnetic jitter active (convergence will be slow)
3. Verify mesh didn't break (no single hub should be critical)
4. Prove security maintained (audit trail for healthcare)

**Success Metric:** Resolve connectivity issue in < 60 minutes, restore service < 30s after fix, audit trail complete, security verified.

## 2. Topology Diagram (P38 Troubleshooting Scenario)
```
┌─────────────────────────────────────────────┐
│   Haiti P38 VLAN Troubleshooting Scenario   │
│   (5 Hubs × 10 Sites = 50 Nodes)           │
│   (20 VLANs, mesh + stress + offline)       │
│                                             │
│  Port-au-Prince ↔ Cap-Haitian ↔ Jérémie   │
│        ↓              ↓              ↓      │
│   [Mesh Trunks][Jitter: ±20%][Stress]     │
│        ↓              ↓              ↓      │
│  Les-Cayes  ↔  Fort-Liberté                │
│                                             │
│  Issue: Healthcare VLAN 15 blocked on      │
│  Port-au-Prince↔Cap-Haitian trunk          │
│  (Misconfiguration under stress)            │
│                                             │
│  Troubleshooting tools: Console only       │
│  (Internet down, offline operation)         │
│                                             │
│  Security: VACL enforcing isolation        │
│  (all diagnoses logged for HIPAA)          │
└─────────────────────────────────────────────┘
```

## 3. IP Addressing Plan (P38 Schema)
| Hub | VLANs | Subnets | Stress Profile | Mesh Links | Notes |
|-----|-------|---------|----------------|-----------|-------|
| Port-au-Prince | 10-19 (Health), 20-29 (Education) | 10.0.x.0/24 | ±20% jitter | 4 (to other hubs) | Hub 1 (affected) |
| Cap-Haitian | 10-19, 20-29 | 10.0.x.0/24 | ±20% jitter | 4 | Hub 2 |
| Jérémie | 10-19, 20-29, 30-39 | 10.0.x.0/24 | ±20% jitter | 4 | Hub 3 |
| Les-Cayes | 30-39 (Commerce), 40-49 (Gov) | 10.0.x.0/24 | ±20% jitter | 3 | Hub 4 |
| Fort-Liberté | 40-49 | 10.0.x.0/24 | ±20% jitter | 3 | Hub 5 |

## 4. Field-7-Specific Configuration

### 4.1 Introduce P38-Scale Misconfiguration
```
! Misconfiguration: Port-au-Prince→Cap-Haitian trunk blocks VLAN 15
Switch-hub1(config-if)# switchport trunk allowed vlan 1,10-14,16-29,30-49
! ← VLAN 15 missing (Health service, critical)

! Problem occurs under stress (jitter masks root cause)
! Operator thinks jitter broke convergence, but it's misconfiguration
```

### 4.2 Offline Troubleshooting Procedure (Field-1 + Field-7)
```
! Operator at Port-au-Prince (no internet, console-only)

! Step 1: Verify startup-config cached (offline resilience)
Switch-hub1# show startup-config | include vlan 15
! Confirms VLAN 15 defined, should be active

! Step 2: Check running-config for divergence
Switch-hub1# show running-config | include switchport trunk allowed
! Comparing to startup, identify missing VLAN 15 in trunk allowed

! Step 3: Verify mesh connectivity (distributed diagnosis)
Switch-hub1# show int status  ← All trunks should be up (mesh healthy)

! Step 4: Identify misconfigured trunk specifically
Switch-hub1# show int g0/1 switchport | include (Port|Allowed)
! Port: GigabitEthernet0/1 (to Cap-Haitian)
! Allowed Vlans: 1,10-14,16-29,30-49  ← VLAN 15 missing!
```

### 4.3 Stress-Aware Fix (Field-2 + Field-7)
```
! Under geomagnetic stress, convergence will be slow
! Apply fix knowing convergence may take 30-60s

Switch-hub1(config-if)# switchport trunk allowed vlan add 15
! Convergence will begin (expect latency increase during VLAN 15 recomputation)

! Verify fix with knowledge of stress impact
PC(Healthcare)> ping 10.0.15.1  (Cap-Haitian health gateway)
! May timeout first 30 seconds while STP recomputes with jitter
! Expected: replies resume within 60s under geomagnetic stress
```

### 4.4 Mesh Verification (Field-3 + Field-7)
```
! Verify fix didn't break other hubs (mesh should route around any failure)
Switch-hub1# ping 10.0.30.1  (Jérémie commerce VLAN via mesh)
! Should work (via alternate paths Cap-Haitian or Les-Cayes)

! Disable Port-au-Prince (Byzantine test)
Switch-hub1# shutdown
! Other 4 hubs should remain connected (mesh healed)
```

### 4.5 Security Audit (Field-4 + Field-7)
```
! Verify VACL enforcement during troubleshooting
Switch-hub1# show log | grep "10.0"
! Expected: VACL violations logged (Health VLAN denied from other depts)
! Confirms security maintained during fix

! Generate audit report
show log > p38_troubleshooting_audit.txt
! Proves: 1) Issue identified, 2) Fix applied, 3) Security maintained
```

## 5. Field-7-Specific Verification Steps

### 5.1 Integrated Verification (All Fields)
```
! Verify offline operation (Field-1)
Switch# show startup-config | include vlan 15
! ✓ Cached

! Verify geomagnetic stress handled (Field-2)
Switch# show int g0/1 status
! ✓ Trunks stable despite jitter

! Verify mesh still connected (Field-3)
Switch-hub1# ping 10.0.40.1  (across mesh to Fort-Liberté)
! ✓ Replies (mesh functional)

! Verify security enforced (Field-4)
Switch# show log | grep "Denied"
! ✓ VACL violations logged, isolation maintained

! Verify P38 scale (Field-7)
Switch# show int brief | grep Ethernet0/0
! ✓ All 20 subinterfaces active
```

### 5.2 Convergence Under Integrated Stress
```
! Measure time from fix applied to service restoration
! Baseline (no stress): 5-10 seconds
! With ±20% jitter: 25-35 seconds
! With Byzantine node offline: 40-60 seconds

! Record actual convergence time
! Expected: < 60 seconds under all Field-7 stresses combined
```

## 6. Expected Output Gallery

### 6.1 Misconfiguration Identified
```
Switch-hub1# show int g0/1 switchport
Switchport Mode: trunk
Allowed Vlans: 1,10-14,16-29,30-49
! ← VLAN 15 missing (root cause identified)
```

### 6.2 Fix Applied, Convergence Under Stress
```
! After "switchport trunk allowed vlan add 15"
! Convergence time with stress: 32 seconds

[Operator monitors ping]
PC(Healthcare)> ping 10.0.15.1
[30 seconds of timeouts]
Reply from 10.0.15.1: bytes=32 time=28ms TTL=63  ← Convergence complete
```

### 6.3 Audit Trail (HIPAA Compliance)
```
Switch# show log | grep "Sep 11 14:"
Sep 11 14:22:00.000 UTC: %SYS-6-RESTART: Reload requested
Sep 11 14:22:15.123 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to down
Sep 11 14:22:20.456 UTC: %CONFIG-5-CONFIG_I: Configured from console
Sep 11 14:22:25.789 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up
Sep 11 14:22:35.012 UTC: %ACL-4-ACLLOG_FLOW_INTERVAL: Denied src 10.0.15.x dest 10.0.20.x  ← VACL still enforcing
[All steps timestamped and logged]
```

## 7. Common Field-7-Specific Mistakes

### 7.1 MISTAKE: Troubleshooting Only One Field at a Time
```
! Error: Assume problem is just misconfiguration (ignore jitter + offline + mesh)
! Field-7 Fix: Consider all fields simultaneously
! Reality: Convergence will be slow due to jitter + mesh rerouting + offline constraints
```

### 7.2 MISTAKE: Not Verifying Mesh After Fix
```
! Error: Fix one trunk, assume all hubs work (incorrect for mesh)
! Field-7 Fix: Test connectivity to all 5 hubs after fix
! Verify: Other 4 hubs still reach each other (mesh still intact)
```

### 7.3 MISTAKE: Ignoring Audit Trail During Emergency
```
! Error: "This is urgent, we can troubleshoot offline, document later"
! Field-7 Fix: Log commands continuously (automatic via syslog)
! HIPAA requires: Proof that troubleshooting maintained security
```

## 8. Troubleshooting by Field (P38 Integration)

### 8.1 Convergence Exceeds 60s
```
! Symptom: Service restoration takes 90+ seconds
! Field-7 Analysis: Multiple stresses compound
! Causes: Jitter delays STP BPDUs + mesh rerouting complex + VLAN 15 affects multiple paths

! Root Cause: Usually one more misconfiguration lurking
! Solution: Check all 5 hub trunks for VLAN 15 completeness
! (Problem may be on Port-au-Prince→Cap-Haitian AND Cap-Haitian→Jérémie)
```

### 8.2 Mesh Broken After Fix
```
! Symptom: Disabling one hub now isolates others (mesh broken)
! Field-7 Fix: Verify you didn't modify trunk neighbor lists
! Ensure: All 5 hubs still have 4+ connections each
! Redundancy check: Remove one hub, verify others connected
```

## 9. Design Analysis (Why for Field-7)

**Why Integrated Troubleshooting at P38 Scale?**

1. **Real-World Complexity:** No production system operates with single stress—combine offline + jitter + mesh + security
2. **Operator Training:** Must prepare for multi-factor problems (not textbook scenarios)
3. **SLA Validation:** Prove P38 can recover from issues < 60s even under all stresses
4. **Scalability Path:** P38 foundation for P45 (200 nodes) and P52 (national)

## 10. Real-World Parallel
**Haiti P38 Pilot Operations:** When network fails, operators face: power loss (offline), space weather (jitter), partial site failures (mesh), healthcare regulations (HIPAA). Troubleshooting must handle all simultaneously.

## 11. Stretch Goals
1. **Run 10 stress cycles:** Introduce + fix 10 different VLAN misconfigurations, measure consistency
2. **Scale to 100 nodes:** Add 5 more hubs, verify troubleshooting scales
3. **Automate diagnosis:** Create script that identifies VLAN misconfiguration across 5 hubs without manual inspection

## 12. Self-Assessment (Field-7 Haiti Levels)

- **BSL-1 (P38 Ready):** Troubleshoot single VLAN issue at baseline (no stress)
- **BSL-2 (P38 Stress):** Identify issue while jitter + offline active
- **BSL-3 (P38 Validation):** Fix issue, verify mesh intact, convergence < 60s, audit trail complete
- **BSL-4 (P38 Operations):** Run 5-site simultaneous troubleshooting scenario, maintain 99% uptime
- **BSL-5 (Haiti P38 Pilot):** Deploy to live 5-hub network, troubleshoot real-world issues, meet SLA
- **BSL-6 (Haiti P45 Expansion):** Expand troubleshooting to 200 nodes, 15 sites, maintain consistency
- **BSL-7 (Haiti Deployment Authority):** Lead P38/P45/P52 operations, troubleshoot at national scale, mentor field teams, publish operational manual

---

**End of Day-14 Field-7 Lab**
**Research Field:** Haiti Unified Deployment | **Haiti Phases:** P38 → P45 → P52
**Generated for:** CCNA VLAN & STP Research Program
