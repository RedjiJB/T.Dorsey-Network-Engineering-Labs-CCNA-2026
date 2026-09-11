# Day 19: RSTP (Geomagnetic)
## 0. Metadata
- **Objective:** Deploy RSTP with convergence < 30s under geomagnetic stress (faster than STP's 60s)
- **Research Field:** Field-2: Geomagnetic
- **Proof:** RSTP faster convergence (1-3s offline, 10-30s under stress vs. STP 15-60s)
- **Hardware:** 3 switches, jitter injector

## 1-12. Field-2 RSTP Stress-Tested
**Context:** RSTP's faster convergence (Proposal-Agreement vs. STP's Hello Timer) handles geomagnetic jitter better. Even under ±20% jitter, RSTP converges 2-3x faster than STP.

**Stress Test:** Measure RSTP convergence under ±20% jitter. Expected: 8-15s (vs. STP 30-45s under same jitter).

**Verification:** RSTP convergence < 30s under stress, acceptable for Haiti P38.

**Real-World:** Haiti P38 Geomagnetic Event: RSTP convergence faster means less time without connectivity during space-weather events.

**Self-Assessment:** BSL-1=Deploy RSTP under baseline; BSL-2=Measure under jitter; BSL-3=Achieve < 30s target; BSL-4=Deploy P38 RSTP for geomagnetic resilience.

---
