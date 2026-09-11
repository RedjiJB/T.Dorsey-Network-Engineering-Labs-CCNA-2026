# Day 17: VLAN Troubleshooting & PVST+ (DePIN)
## 0. Metadata
- **Objective:** Troubleshoot PVST+ in distributed mesh (no central core); verify STP converges in full-mesh
- **Research Field:** Field-3: DePIN
- **Proof:** PVST+ elects root per VLAN across 6-node mesh, convergence without central authority
- **Haiti Phase:** P45 (community mesh)
- **Hardware:** 6 switches (full mesh), no central core

## 1-12. Field-3 PVST+ Mesh Troubleshooting
**Context:** Haiti P45 community mesh: 6 branches each run STP. Each VLAN may have different root bridge (distributed election). Troubleshoot by verifying root election is fair across VLANs and mesh connectivity preserved.

**Topology:** 6 switches full mesh, 2 VLANs (10 & 20), expect each VLAN may pick different root (load-balanced).

**Troubleshooting Procedure:**
1. Identify current root per VLAN: show spanning-tree vlan 10 | include "This bridge is the root"
2. Check if root is "central" (good for mesh) or "edge" (bad)
3. If root is edge switch, modify priority to elect more central switch
4. Verify all 6 switches recognize new root (show spanning-tree vlan 10 on each)
5. Test connectivity: all 15 mesh pairs should work even after STP changes

**Verification:**
- VLAN 10 root is central (e.g., SW-B, SW-C, or SW-E)
- VLAN 20 root is different central switch (load-balanced)
- Mesh resilience: disable 1 switch, verify other 5 remain connected
- STP converges in < 30s even after node failure (distributed healing)

**Expected:** PVST+ elects reasonable roots, mesh stays intact, distributed troubleshooting works (no single authority).

**Mistakes:** All VLANs with same root (hierarchy), assuming central core needed for STP.

**Design Analysis:** Mesh PVST+ requires distributed decision-making. Different root per VLAN achieves load-balancing without central core.

**Real-World:** Haiti P45 Mesh PVST+: Each branch may be root for one VLAN, creating balanced tree topology. No single "core" switch; all branches equal. Troubleshooting happens via consensus (checking all 6 nodes' spanning-tree view).

**Stretch:** Test Byzantine failure: disable one mesh node, verify STP converges to new topology without central authority.

**Self-Assessment:** BSL-1=Verify per-VLAN root election; BSL-2=Ensure mesh stays connected; BSL-3=Optimize root placement per VLAN; BSL-4=Deploy P45 mesh PVST+.

---
