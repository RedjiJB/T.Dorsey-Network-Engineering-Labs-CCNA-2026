# Day 18: STP (DePIN)
## 0. Metadata
- **Objective:** Deploy STP in full-mesh topology, verify distributed root election and convergence without central core
- **Research Field:** Field-3: DePIN
- **Proof:** STP elects root in mesh, any node offline doesn't break tree, convergence distributed
- **Hardware:** 6 switches (full mesh)

## 1-12. Field-3 STP Mesh Deployment
**Context:** Haiti P45 mesh needs STP to prevent loops. Distributed election: root may shift based on priority, no central authority decides. Mesh convergence must handle any node failure.

**Topology:** 6 switches full mesh, STP prevents loops.

**Verification:**
- STP converges in < 30s with all 6 active
- Disable 1 switch (Byzantine), other 5 re-converge in < 30s
- No central core needed

**Expected:** STP works distributedly in mesh, Byzantine-resilient.

**Real-World:** Haiti P45 Mesh: Each branch has same STP priority (equal voting power). If branch loses connection, other 5 mesh nodes re-elect root from remaining 5. No single authority.

**Self-Assessment:** BSL-1=Deploy STP in 6-node mesh; BSL-2=Test Byzantine failure; BSL-3=Verify distributed convergence; BSL-4=Deploy P45 mesh STP.

---
