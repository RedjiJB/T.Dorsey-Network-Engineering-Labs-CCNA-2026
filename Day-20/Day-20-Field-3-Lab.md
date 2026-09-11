# Day 20: MSTP (DePIN)
## 0. Metadata
- **Objective:** Deploy MSTP in full-mesh, region-aware STP with distributed root per region
- **Research Field:** Field-3: DePIN
- **Proof:** MSTP enables different root per region (no central authority), convergence < 10s per region
- **Hardware:** 6 switches (full mesh), 20 VLANs

## 1-12. Field-3 MSTP Mesh Deployment
**Context:** MSTP regions enable distributed authority: each region elects independent root bridge. Haiti P45 mesh can assign regions to branches—no central master.

**Topology:** 6 switches full mesh, MSTP with regions (Health region, Education region, etc.).

**Verification:** Each region converges independently, Byzantine failure isolated to affected region, other regions unimpacted.

**Expected:** Distributed MSTP with mesh resilience.

**Real-World:** Haiti P45 Mesh MSTP: Port-au-Prince hosts Health region root, Cap-Haitian hosts Education region root. Independent convergence, distributed governance.

**Self-Assessment:** BSL-1=Configure MSTP regions; BSL-2=Test Byzantine failure; BSL-3=Verify distributed convergence; BSL-4=Deploy P45 MSTP.

---
