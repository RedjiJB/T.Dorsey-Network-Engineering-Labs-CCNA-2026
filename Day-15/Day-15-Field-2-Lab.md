# Day 15: VLAN Design & Multi-VLAN Topology (Geomagnetic)
## 0. Metadata: Field-2 Geomagnetic Stress-Tested Design
- **Objective:** Design VLAN topology resilient to ±20% jitter/5% loss during space-weather events
- **Research Field:** Field-2: Geomagnetic
- **Proof Obligations:** Design convergence < 60s under stress; spanning tree stable across all VLANs
- **Haiti Phase:** P38 (stress-tested design)
- **Relevant:** IEEE 802.1Q, 802.1D, geomagnetic resilience
- **Prerequisites:** Days 1-14 + Field-2
- **Hardware:** 4 switches, router, PCs, jitter injector

## 1-12. Field-2 VLAN Design (Stress-Tested)
**Business Context:** Design Haiti P38 VLAN topology proven resilient to geomagnetic events. Space-weather causes ionospheric jitter (±20% latency, 5% loss). Design must handle this without topology flaps.

**Topology:** Same 4-VLAN as base (Health 10, Education 20, Commerce 30, Government 40), plus geomagnetic stress injection on WAN links.

**IP Plan:** Standard subnets, but all gateways must converge < 60s under ±20% jitter.

**Configuration:** Create VLANs + trunks (baseline), then inject jitter on inter-switch links via network emulator. Measure STP convergence time during jitter injection.

**Verification:** 
1. Baseline convergence: 15s (no stress)
2. With ±20% jitter: 35-45s (acceptable)
3. All VLANs reachable from any switch

**Expected Output:** Convergence times logged, VLAN traffic flows through all 4 departments, no STP re-elections during jitter.

**Common Mistakes:** Not measuring convergence under stress, injecting unrealistic jitter (>50%), only testing one VLAN.

**Troubleshooting:** If convergence > 60s, check STP BPDU arrival times during jitter; verify no interface flaps.

**Design Analysis:** Geomagnetic-resilient design requires understanding STP timer interactions with jitter. Hello timers (2s default) affected by latency variance. Design proves Haiti P38 can function during space-weather events.

**Real-World:** Haiti P38 Geomagnetic Event Protocol: When NOAA forecasts geomagnetic storm, field ops monitor convergence time; if exceeds 60s, activate backup communication (satellite link). This design validates acceptable performance.

**Stretch Goals:** Implement jitter-adaptive STP timers, test with real NOAA geomagnetic data, measure actual vs. simulated convergence.

**Self-Assessment:** BSL-1=Design VLANs+measure baseline; BSL-2=Add jitter+measure stress convergence; BSL-3=Document SLA (convergence time); BSL-4=Deploy to Haiti P38+validate during actual geomagnetic event.

---
**Field-2 Design Focus:** Prove 4-VLAN topology converges < 60s under realistic geomagnetic stress profiles.
