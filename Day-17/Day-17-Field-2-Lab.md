# Day 17: VLAN Troubleshooting & PVST+ (Geomagnetic)
## 0. Metadata  
- **Objective:** Troubleshoot PVST+ under geomagnetic stress; verify STP converges < 60s with jitter
- **Research Field:** Field-2: Geomagnetic
- **Proof:** PVST+ stable under ±20% jitter, STP BPDUs arrive reliably, topology doesn't flap
- **Haiti Phase:** P38 (stress-tested)
- **Hardware:** 3 switches, jitter injector

## 1-12. Field-2 PVST+ Stress Troubleshooting
**Context:** During geomagnetic storm, STP timers affected by jitter (Hello delays, Forward Delay lengthens). Troubleshoot by identifying which VLAN converges slowly, why, and fix.

**Config:** Same PVST+ setup as Day-17 Field-1, but add jitter on all switch links (±20% variance). Intentionally create misconfiguration where one VLAN's root bridge far away (bad topology for stress testing).

**Troubleshooting Under Stress:**
1. Measure baseline convergence (no stress): ~10s per VLAN
2. Inject jitter (±20%), measure convergence: expect 25-40s per VLAN
3. Identify slow VLAN (one taking > 40s)
4. Root cause: VLAN's STP root bridge far away, BPDUs delayed by jitter
5. Fix: Re-assign root bridge closer to most switches, reducing BPDU path length

**Verification:**
- Before fix under stress: VLAN 20 converges in 52s (too slow)
- After fix: VLAN 20 converges in 35s (acceptable < 60s)
- All VLANs converge < 60s under ±20% jitter (P38 requirement met)

**Expected:** PVST+ stability under geomagnetic profiles, convergence time acceptable.

**Mistakes:** Not measuring per-VLAN convergence, assuming same time for all VLANs.

**Design Analysis:** Geomagnetic jitter affects STP Hello timer (delays BPDU arrival). PVST+ design must account for this—root bridge proximity matters under stress.

**Real-World:** Haiti P38 Geomagnetic Event: Field ops monitor PVST+ convergence during storm warning. If VLAN convergence time rises above 60s, activate alternate path (modify root bridge priority to switch closer to affected areas). This troubleshooting requires understanding PVST+ interaction with jitter.

**Stretch:** Test 5+ VLANs under varying jitter levels, map convergence time vs. jitter intensity.

**Self-Assessment:** BSL-1=Measure per-VLAN convergence baseline; BSL-2=Measure under stress, identify slow VLAN; BSL-3=Fix PVST+ root bridge priority, re-measure; BSL-4=Deploy P38 with optimized PVST+ for geomagnetic resilience.

---
