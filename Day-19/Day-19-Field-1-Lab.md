# Day 19: RSTP (Rapid STP) (Black Start)
## 0. Metadata
- **Objective:** Deploy offline-resilient RSTP with improved convergence time
- **Research Field:** Field-1: Black Start
- **Proof:** RSTP converges 2-3x faster than STP, topology cached offline, edge ports enable fast convergence
- **Haiti Phase:** P38 (offline RSTP)

## 1-12. Field-1 Offline RSTP Deployment
**Context:** RSTP improves convergence (typically 1-3s vs. STP 15-30s) while remaining offline-capable. Haiti P38 benefits from faster convergence cached to NVRAM.

**Config:** Enable RSTP (spanning-tree mode rapid-pvst) on all switches. Configure edge ports on access links (PCs). Cache all RSTP state to NVRAM.

**Offline Test:** Power loss → reload → verify RSTP topology identical (no re-convergence needed).

**Verification:** RSTP converges 2-3x faster than Day-18 STP (3-5s vs. 15-20s baseline), topology persistent offline.

**Expected:** Fast, offline-capable RSTP deployment.

**Real-World:** Haiti P38 Clinic: RSTP edge ports on PC access links → PCs reach gateways in 1-2s after power restoration (vs. 15s with STP).

**Self-Assessment:** BSL-1=Enable RSTP, cache configs; BSL-2=Measure convergence improvement; BSL-3=Deploy P38 RSTP.

---
