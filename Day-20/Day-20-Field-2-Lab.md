# Day 20: MSTP (Geomagnetic)
## 0. Metadata
- **Objective:** Deploy MSTP with convergence < 30s under geomagnetic stress (fewer STP trees = more stable)
- **Research Field:** Field-2: Geomagnetic
- **Proof:** MSTP convergence improved by reducing STP instances (jitter affects fewer trees)
- **Hardware:** 3 switches, jitter injector, 20 VLANs

## 1-12. Field-2 MSTP Stress-Tested
**Context:** With MSTP grouping 20 VLANs into 3 trees, geomagnetic stress affects only 3 trees (vs. 20 with PVST+). Convergence more efficient under jitter.

**Stress Test:** Trigger topology change under ±20% jitter. Measure convergence for all 20 VLAN groups.

**Verification:** MSTP convergence < 30s even with jitter (improved from PVST+ 60s for worst-case VLAN).

**Real-World:** Haiti P38 Geomagnetic: 20 VLANs grouped into 3 MSTP regions converge together, reducing jitter impact.

**Self-Assessment:** BSL-1=Deploy MSTP under jitter; BSL-2=Measure convergence; BSL-3=Achieve < 30s; BSL-4=Deploy P38 MSTP for stress resilience.

---
