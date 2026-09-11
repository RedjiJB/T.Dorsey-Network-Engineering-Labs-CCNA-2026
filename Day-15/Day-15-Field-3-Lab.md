# Day 15: VLAN Design & Multi-VLAN Topology (DePIN)
## 0. Metadata: Field-3 Mesh VLAN Design
- **Objective:** Design multi-VLAN topology for full-mesh (no central core) network
- **Research Field:** Field-3: DePIN (Distributed)
- **Proof:** Mesh VLAN routing works without central aggregation; any node offline doesn't isolate others
- **Haiti Phase:** P45 (community mesh, 200 nodes)
- **Hardware:** 6 switches (full mesh), 6 PCs, no central core
- **Prerequisites:** Days 1-14 + Field-3

## 1-12. Field-3 Mesh Design
**Context:** Design Haiti P45 community mesh VLAN topology. 6 branches (50+ distributed sites) interconnect in full mesh. No "head office" core—all switches equal.

**Topology:** 6 switches in full mesh (15 interconnects), each with local VLAN gateways (10-40 for Health/Education/Commerce/Government).

**IP Plan:** Each branch provides gateway for all 4 VLANs (distributed architecture).
- Branch A: 10.0.10.1, 10.0.20.1, etc.
- Branch B: 10.0.10.2, 10.0.20.2, etc.
- [Repeat for Branches C-F]

**Config:** Create all VLANs on all 6 switches, configure trunks to every other switch (full mesh). Enable VLAN routing on each switch.

**Verification:** 
1. Mesh connectivity: All 15 pairs reachable
2. Byzantine resilience: Disable 1 switch, verify other 5 remain connected
3. Quorum test: With 4+ switches active, routing works; < 4 cannot route

**Expected:** Full mesh active, all VLANs routable via multiple paths, Byzantine failure handled gracefully.

**Mistakes:** Adding central core (defeats mesh), not verifying all 15 paths work, asymmetric VLAN allowed lists.

**Troubleshooting:** If mesh breaks on node failure, topology is hierarchical (not true mesh). Verify each node has 5 trunk connections.

**Design Analysis:** Mesh design reflects Field-3 principle: distributed authority, no single point of failure. Haiti P45 requires this for community-operated networks.

**Real-World:** Haiti P45 Mesh Deployment: Each branch operates independently; if one loses power, other 5 continue routing. Community governance (voting) on network policy replaces centralized IT authority.

**Stretch:** Scale to 10 nodes, implement voting protocol, add Byzantine-aware routing.

**Self-Assessment:** BSL-1=Design 6-node mesh; BSL-2=Verify all 15 paths; BSL-3=Test Byzantine failure; BSL-4=Deploy P45 mesh+validate resilience.

---
**Field-3 Design Focus:** Prove distributed VLAN design works in full-mesh topology.
