# Day 19: RSTP (DePIN)
## 0. Metadata
- **Objective:** Deploy RSTP in full-mesh, distributed root election with rapid convergence
- **Research Field:** Field-3: DePIN
- **Proof:** RSTP converges < 10s in mesh, Byzantine resilience maintained with faster recovery
- **Hardware:** 6 switches (full mesh)

## 1-12. Field-3 RSTP Mesh Deployment
**Context:** RSTP in mesh improves over STP by faster convergence via Proposal-Agreement. Mesh root election remains distributed (no central authority).

**Topology:** 6 switches full mesh, RSTP (rapid-pvst mode).

**Verification:** RSTP converges < 10s with all 6 active, < 10s re-convergence after Byzantine failure.

**Expected:** Fast, mesh-compatible RSTP.

**Real-World:** Haiti P45 Mesh: RSTP converges faster than STP, improving community branch response times.

**Self-Assessment:** BSL-1=Deploy RSTP in mesh; BSL-2=Test Byzantine failure; BSL-3=Achieve < 10s convergence; BSL-4=Deploy P45 RSTP.

---
