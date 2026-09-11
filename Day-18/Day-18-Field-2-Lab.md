# Day 18: STP (Geomagnetic)
## 0. Metadata
- **Objective:** Deploy STP resilient to geomagnetic stress (BPDU delays, topology stability under jitter)
- **Research Field:** Field-2: Geomagnetic
- **Proof:** STP converges < 60s under ±20% jitter, no topology flaps despite latency variance
- **Hardware:** 3 switches, jitter injector

## 1-12. Field-2 STP Stress-Tested Deployment
**Context:** Geomagnetic jitter delays Hello BPDUs, risking topology flaps if STP timers too aggressive. Design must use conservative timers (default or increased) to handle jitter.

**Config:** STP with default timers (Hello 2s, Forward Delay 15s). Inject ±20% jitter on all links.

**Convergence Test:** Trigger topology change (disable switch), measure convergence under jitter. Expected: 30-45 seconds (vs. baseline 10-15s without jitter).

**Verification:** Convergence < 60s achieved, no flaps observed during jitter injection.

**Expected:** Stable STP topology even with geomagnetic stress.

**Real-World:** Haiti P38 Geomagnetic Event: STP Hello BPDUs delayed by jitter (Hello 2s + jitter → 2.4-2.8s). STP still converges because Forward Delay accounts for this delay variance. Network stable during event.

**Self-Assessment:** BSL-1=Measure baseline convergence; BSL-2=Test under jitter, achieve < 60s; BSL-3=Optimize STP timers; BSL-4=Deploy P38 with stress-tested STP.

---
