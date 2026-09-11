# Day 13: VLAN Routing & Inter-VLAN Communication (Haiti P38+ Deployment)

## 0. Metadata
- **Objective:** Implement ROAS + VACL + mesh networking in Haiti-scale production topology (50 nodes, 20+ VLANs)
- **Research Field:** Field-7: Haiti Unified Deployment (Combined all fields: offline, stress-tested, mesh, secure, scaled)
- **Proof Obligations:** All Fields 1-6 requirements met simultaneously; 50-node pilot network operational; ROAS scales to 20 VLANs without performance degradation
- **Haiti Deployment Phase:** P38 (pilot, 50 nodes, 5 sites) → P45 (expansion, 200+ nodes, 15 sites) → P52 (national, 1000+ nodes)
- **Relevant RFC/Standards:** IEEE 802.1Q, RFC 5737, geomagnetic resilience, Byzantine fault tolerance, HIPAA compliance
- **Prerequisites:** Days 1-12 + all Fields 1-6 prerequisites
- **Estimated Time:** 240 minutes
- **Difficulty:** Expert (full-stack integration, field deployment)
- **Hardware Required:** 5-6 routers, 15-20 switches, 30-50 PCs, cache storage, jitter injectors, syslog, UPS
- **Key Concepts:** Scaled ROAS, multi-site VLAN design, geomagnetic resilience, security enforcement, mesh networking, operational automation

## 1. Business Context (Field-7: Haiti National Deployment)
Field-7 represents **Haiti's digital transformation initiative**: 50+ sites (health clinics, schools, cooperatives, government offices) interconnected via mesh + ROAS + security. This lab validates the complete P38 pilot can:

1. **Offline-first operation** (Field-1): Power loss doesn't break VLAN routing
2. **Geomagnetic resilience** (Field-2): Space-weather events don't cause convergence failures
3. **Distributed mesh** (Field-3): No single point of failure (any node can go offline)
4. **Security enforcement** (Field-4): Healthcare and government data isolated and audited
5. **Scalability** (Field-7): 20+ VLANs, 50+ nodes, all working together seamlessly

**Real Scenario:** Haiti launches P38 pilot with 5 regional hubs (Port-au-Prince, Cap-Haïtien, Jérémie, Les Cayes, Fort-Liberté). Each hub has 10 sites (50 total). Network must survive: power loss, geomagnetic storms, equipment failures, security audits.

**Success Metric:** P38 pilot achieves 99.5% uptime; zero HIPAA violations; inter-VLAN routing converges < 30s under stress.

## 2. Topology Diagram (Haiti P38 Production Scale)
```
┌────────────────────────────────────────────────────────────────┐
│                   HAITI P38 PILOT NETWORK                      │
│                    (50 Nodes, 20 VLANs)                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Port-au-     │  │ Cap-Haïtien  │  │ Jérémie      │         │
│  │ Prince Hub   │  │ Hub          │  │ Hub          │         │
│  │ (8 sites)    │  │ (8 sites)    │  │ (8 sites)    │         │
│  │              │  │              │  │              │         │
│  │ [Router+     │  │ [Router+     │  │ [Router+     │         │
│  │  SW1-4]--+   │  │  SW5-8]--+   │  │  SW9-12]--+  │         │
│  │           \  │  │            \ │  │           \  │         │
│  └────────────\─┘  └─────────────\┘  └────────────\─┘         │
│                \                  \                \            │
│                 +--[Mesh Interconnect]────────────+            │
│                      (geomagnetic stress, jitter)              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ Les Cayes    │  │ Fort-Liberté │                           │
│  │ Hub (9 sites)│  │ Hub (9 sites)│                           │
│  │              │  │              │                           │
│  │ [Router+     │  │ [Router+     │                           │
│  │  SW13-16]    │  │  SW17-20]    │                           │
│  └──────────────┘  └──────────────┘                           │
│                                                                 │
│  [VLAN Structure]                                              │
│   VLAN 10-19: Health (encrypted, HIPAA-compliant)             │
│   VLAN 20-29: Education (school networks)                      │
│   VLAN 30-39: Commerce (cooperative finance)                   │
│   VLAN 40-49: Government (administrative)                      │
│                                                                 │
│  [Field-7 Requirements]                                        │
│   ✓ Offline caching (NVRAM persistence)                       │
│   ✓ Geomagnetic stress testing (jitter + loss)               │
│   ✓ Mesh topology (no single point of failure)                │
│   ✓ VACL security enforcement (HIPAA audit trail)            │
│   ✓ Byzantine resilience (any node failure)                   │
│   ✓ Operational automation (monitoring, alerts)               │
└────────────────────────────────────────────────────────────────┘
```

## 3. IP Addressing Plan (Haiti P38 Schema)
| VLAN Range | Department | Subnets | Gateway | Security | Notes |
|-----------|-----------|---------|---------|----------|-------|
| 10-19 | Health | 10.0.10.0/24-10.0.19.0/24 | .1 per VLAN | VACL enforce | HIPAA encrypted |
| 20-29 | Education | 10.0.20.0/24-10.0.29.0/24 | .1 per VLAN | Standard | Open access |
| 30-39 | Commerce | 10.0.30.0/24-10.0.39.0/24 | .1 per VLAN | VACL enforce | Finance isolated |
| 40-49 | Government | 10.0.40.0/24-10.0.49.0/24 | .1 per VLAN | VACL enforce | Admin audited |

## 4. Field-7-Specific Configuration (Integrated)

### 4.1 Multi-VLAN ROAS (All 20 VLANs)
```
! Configure ROAS for all 20 VLANs (one per regional hub)
Router> en
Router# conf t

Router(config)# int g0/0
Router(config-if)# no shutdown
Router(config-if)# exit

! Health VLANs 10-19
Router(config)# int g0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 10.0.10.1 255.255.255.0
Router(config-subif)# description VLAN10_Health
Router(config-subif)# no shutdown
Router(config-subif)# exit

! [Repeat for VLANs 11-19]
! [Similar for VLANs 20-49 (Education, Commerce, Government)]

! Example: VLAN 20 (Education)
Router(config)# int g0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 10.0.20.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

! [... and so on for VLANs 21-49 ...]

Router(config)# end
Router# write memory
```

### 4.2 Field-7 Offline Persistence (Field-1 Integration)
```
! Verify all 20 subinterfaces cached to NVRAM
Router# show startup-config | include interface g0/0
! Expected: All subinterfaces present

! Simulate power loss
Router# reload
! **After reload:** Verify all subinterfaces active without reconfiguration
```

### 4.3 Field-7 Geomagnetic Stress Injection (Field-2 Integration)
```
! Apply jitter to mesh interconnect between hubs
Router(config)# int g0/0
Router(config-if)# delay 20000  ! 20ms baseline
! + ±20% jitter on mesh backbone
Router(config-if)# exit
```

### 4.4 Field-7 Mesh Topology (Field-3 Integration)
```
! Configure all 5 hubs in partial mesh
! Port-au-Prince ↔ Cap-Haïtien
! Port-au-Prince ↔ Jérémie
! Cap-Haïtien ↔ Jérémie
! [All hubs interconnected, no central core]

! Trunk configuration on each hub router:
Router(config)# int s0/0
Router(config-if)# description Trunk_to_Cap-Haitian
Router(config-if)# encapsulation 802.1q  (if using serial)
Router(config-if)# no shutdown
Router(config-if)# exit
```

### 4.5 Field-7 VACL Security Enforcement (Field-4 Integration)
```
! Define policies: Health (VLAN 10-19) isolated from others
Switch(config)# ip access-list extended HEALTH_ISOLATION
Switch(config-ext-acl)# deny ip 10.0.10.0 0.0.0.255 10.0.20.0 0.0.0.255
Switch(config-ext-acl)# deny ip 10.0.10.0 0.0.0.255 10.0.30.0 0.0.0.255
Switch(config-ext-acl)# deny ip 10.0.10.0 0.0.0.255 10.0.40.0 0.0.0.255
Switch(config-ext-acl)# permit ip any any
Switch(config-ext-acl)# exit

! Create VACL map
Switch(config)# vlan access-map HEALTH_SECURITY 1
Switch(config-access-map)# match ip address HEALTH_ISOLATION
Switch(config-access-map)# action deny log
Switch(config-access-map)# exit

Switch(config)# vlan access-map HEALTH_SECURITY 2
Switch(config-access-map)# match ip address any
Switch(config-access-map)# action forward
Switch(config-access-map)# exit

! Apply to Health VLANs
Switch(config)# vlan filter HEALTH_SECURITY vlan-list 10-19

Switch(config)# end
Switch# write memory
```

### 4.6 Field-7 Operational Automation (Monitoring)
```
! Script: Monitor ROAS convergence after link failure
! (In field, this runs automatically)

! Monitor subinterface status
Router# show int g0/0.10 | include (up|down)

! Monitor routing table
Router# show ip route connected

! Monitor VLAN ACL violations
Switch# show log | include VLAN10_to
! Export to syslog for Haiti field ops center
```

## 5. Field-7-Specific Verification Steps

### 5.1 Haiti P38 Pilot Integration Test
```
! Phase 1: All 20 VLANs operational
Router# show int brief | include g0/0
! Expected: 20 subinterfaces (g0/0.10 through g0/0.49) all up

! Phase 2: Inter-site connectivity
Hub-A# ping 10.0.20.1 (Hub-B education gateway)
! Expected: Reply (mesh routed)

Hub-A# ping 10.0.40.1 (Hub-C government gateway)
! Expected: Reply (mesh routed, different path)

! Phase 3: All departmental VLANs reachable
! Test matrix: 50 nodes × 20 VLANs
! Expected: > 99% connectivity (failures = Byzantine nodes only)
```

### 5.2 Field-7 Byzantine Resilience (Integrated)
```
! Simulate one hub offline
Hub-D# shutdown

! Verify other hubs remain connected
Hub-A# ping 10.0.30.1  (Commerce VLAN)  ← Should work (rerouted)
Hub-A# ping 10.0.40.1  (Government VLAN) ← Should work (rerouted)

! Verify Byzantine hub connectivity broken
Hub-A# ping 10.0.50.1  (Hypothetical on Hub-D) ← FAILS (expected)

! Field-7 Success: Mesh heals around failed node
```

### 5.3 Field-7 Extended Stress Test (All Fields Integrated)
```
! Simultaneously test all field requirements:
! 1. Power loss simulation (Field-1)
! 2. Geomagnetic jitter injection (Field-2)
! 3. Mesh node failure (Field-3)
! 4. VACL policy enforcement (Field-4)
! 5. 20-VLAN routing at scale (Field-7)

! Run 1-hour comprehensive test:
! - Continuous ping on all 20 VLANs
! - Inject jitter + loss on backbone
! - Disable one hub for 10 minutes (Byzantine)
! - Trigger VACL violations (monitor logging)
! - Record all metrics: latency, loss, convergence time, audit trail

! Expected Results:
!   - Latency: 20-30ms baseline, 25-35ms with jitter
!   - Loss: < 5% during Byzantine failure
!   - Convergence: < 30 seconds after hub comes back
!   - VACL: 100% enforcement, all violations logged
!   - Uptime: > 99.5% (only down during Byzantine test)
```

## 6. Expected Output Gallery (P38 Production Metrics)

### 6.1 Multi-VLAN Subinterface Status
```
Router# show int brief | grep Ethernet0/0
Ethernet0/0                        unassigned      up                    up
Ethernet0/0.10                     10.0.10.1       up                    up
Ethernet0/0.11                     10.0.11.1       up                    up
[... VLAN 12-49 ...]
Ethernet0/0.49                     10.0.49.1       up                    up
```

### 6.2 Mesh Connectivity (Haiti P38)
```
Hub-A# ping 10.0.40.1  (Route to Hub-C via D)
Reply from 10.0.40.1: bytes=32 time=28ms TTL=63
[Mesh rerouting transparent to user]
```

### 6.3 Convergence Metrics (Stress Test)
```
Test: 60-minute stress with all fields integrated
  Baseline latency: 22ms
  Peak latency (with jitter): 34ms
  Byzantine failure convergence: 24 seconds
  VACL violations logged: 47 (100% detected)
  Audit trail completeness: 100% (all violations timestamped)
  Network uptime: 99.67% (only down during planned Byzantine test)
```

## 7. Common Field-7-Specific Mistakes

### 7.1 MISTAKE: Not Testing All 20 VLANs
```
! Error: Only tested VLAN 10, assumed others work
! Field-7 Fix: Verify all 20 subinterfaces and test connectivity
! Expected: 20/20 VLANs routable
```

### 7.2 MISTAKE: VACL Policy Too Permissive
```
! Error: Allowed Health→Commerce (violates HIPAA)
! Field-7 Fix: Audit VACL rules match security policy
! Expected: Health (10-19) isolated from others
```

### 7.3 MISTAKE: Single Point of Failure Remains
```
! Error: All hubs connect through one "master" router
! Field-7 Fix: Implement true mesh (every hub to every other)
! Verify: Each hub has 4+ connections (redundancy)
```

## 8. Troubleshooting by Field (Field-7: Integrated Systems)

### 8.1 One Hub Offline Breaks Other Hubs
```
! Symptom: If Hub-D fails, Hub-A can't reach Hub-E

! Field-7 Fix: This indicates NON-MESH topology
! Correct: All hubs should reach each other via alternate paths
! Verify mesh density: 5 hubs should have 5×4/2 = 10 interconnects
```

### 8.2 High Latency During Stress Test
```
! Symptom: Latency exceeds 50ms during jitter + Byzantine

! Field-7 Expected: Latency should stay < 40ms even under stress
! If > 40ms: Check if subinterfaces flapping or mesh rerouting slowly

! Fix: Verify all trunks are high-speed (1Gbps) and jitter realistic
```

## 9. Design Analysis (Why for Field-7)

**Why Complete Integration for Haiti?**

1. **Real-World Complexity:** P38 pilot is not just ROAS—it's ROAS + offline + stress + mesh + security
2. **Proof Obligation:** Prove all 5 fields work *together*, not in isolation
3. **Operational Readiness:** Haiti field ops need a system they can deploy, manage, and troubleshoot
4. **Scalability Path:** P38 → P45 → P52 requires foundation that's proven at each scale

## 10. Real-World Parallel (Haiti Deployment)

**Haiti P38 Pilot (Q4 2026 - Q2 2027):**
- 5 regional hubs, 50 total sites
- 20 VLANs (Health, Education, Commerce, Government)
- Mesh topology (any hub can be offline)
- VACL security (HIPAA compliance for health data)
- **SLA:** 99.5% uptime, < 30s convergence on failure, zero HIPAA violations

**Validation Gate:** If P38 pilot meets all metrics → Approved for P45 expansion (200+ nodes, 15 sites)

## 11. Stretch Goals (Field-7 Advanced)

1. **Scale to 200 Nodes (P45)**
   - Add 10 additional sites per hub
   - Verify ROAS scales (20 VLANs, 50+ nodes)
   - Measure impact on convergence time

2. **Integrate Real Geomagnetic Data**
   - Use NOAA DSCOVR solar wind data
   - Map actual geomagnetic storms to jitter profiles
   - Simulate real space-weather events during P38

3. **Automated Failover Testing**
   - Create script that randomly disables nodes
   - Measure recovery time for each failure scenario
   - Accumulate statistics over 1 week of continuous testing

4. **Compliance Report Automation**
   - Generate monthly HIPAA audit report from logs
   - Certify zero unauthorized VLAN crossings
   - Export metrics for Haiti health ministry approval

## 12. Self-Assessment (Field-7 Haiti Deployment Levels)

- **BSL-1 (P38 Ready):** Configure all 20 VLANs + ROAS, test connectivity, verify offline persistence
- **BSL-2 (P38 Stress):** Add geomagnetic jitter + VACL security, run integrated test, document metrics
- **BSL-3 (P38 Validation):** Run 1-hour comprehensive test (all fields), achieve > 99% uptime, verify compliance
- **BSL-4 (P38 Pre-Deployment):** Run 24-hour burn-in, measure consistency, train Haiti field ops team
- **BSL-5 (Haiti P38 Pilot):** Deploy to 5 regional hubs, validate metrics in field, support operations
- **BSL-6 (Haiti P45 Expansion):** Scale to 200 nodes across 15 sites, maintain SLA, mentor P52 planning
- **BSL-7 (Haiti National Authority):** Lead P38/P45/P52 deployments, validate at country scale, publish research, mentor international teams

---

**End of Day-13 Field-7 Lab**
**Research Field:** Haiti Unified Deployment (All Fields) | **Haiti Phases:** P38 (Pilot) → P45 (Expansion) → P52 (National)
**Generated for:** CCNA VLAN & STP Research Program
