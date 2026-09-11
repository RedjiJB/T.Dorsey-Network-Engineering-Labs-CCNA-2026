# Day 17: VLAN Troubleshooting & PVST+ (Haiti P38+ Deployment)
## 0. Metadata
- **Objective:** Troubleshoot PVST+ at P38 scale (20 VLANs, 50 nodes, 5 hubs) integrating all fields
- **Research Field:** Field-7: Haiti Unified
- **Proof:** Troubleshoot PVST+ issues offline, under stress, in mesh, securely, at scale
- **Haiti Phases:** P38 → P45 → P52
- **Hardware:** Full P38 infrastructure

## 1-12. Field-7 Haiti P38 PVST+ Troubleshooting
**Context:** Haiti P38 has 20 VLANs running PVST+. Troubleshoot per-VLAN STP issues while simultaneously managing: offline operation (cached STP state), geomagnetic stress (jitter-delayed BPDUs), mesh topology (no central root), security enforcement (VACL during STP changes), and 50-node scale.

**Real Scenario:** Healthcare VLAN 15 converges too slowly (60+ seconds) during P38 operations. Troubleshoot root cause while keeping other 19 VLANs operational and maintaining security.

**Integrated Troubleshooting:**
1. **Offline Context:** Verify VLAN 15 STP state cached in NVRAM (VLAN 15 root bridge, port priorities)
2. **Stress Impact:** Measure convergence time for VLAN 15 under ±20% jitter (baseline may be wrong under geomagnetic events)
3. **Mesh Analysis:** Verify VLAN 15 root is mesh-central (not edge), reducing BPDU path length
4. **Security Check:** Ensure VACL still enforcing Health VLAN (10-19) isolation during STP changes
5. **Root Cause:** VLAN 15's current root is edge switch (bad for mesh mesh under stress). Fix: Modify priority to elect mesh-central switch
6. **Verification:** After fix, VLAN 15 converges in <40s even with ±20% jitter

**Expected:** PVST+ optimized for all 20 VLANs, each converges < 60s under P38 conditions.

**Integration Points:**
- Field-1 (Offline): VLAN 15 STP state cached, same root after reload
- Field-2 (Geomagnetic): Convergence time measured under ±20% jitter, root placement optimized
- Field-3 (Mesh): VLAN 15 root chosen from mesh-central switches (not edge)
- Field-4 (Security): VACL enforced during STP fix, audit trail complete
- Field-7 (Scale): All 20 VLANs converging properly, 50 nodes stable

**Mistakes:** Not considering offline VLAN state, ignoring jitter impact on STP, choosing edge switch as root (bad for mesh).

**Design Analysis:** P38 troubleshooting requires integration thinking—single VLAN issue (15) may stem from multiple field concerns (offline caching, geomagnetic jitter, mesh topology, security constraints).

**Real-World:** Haiti P38 VLAN 15 Troubleshooting:
- Reported issue: "Healthcare VLAN 15 slow"
- Initial diagnosis: Check offline cache (✓ VLAN 15 cached correctly)
- Stress test: Run convergence test with geomagnetic jitter (✗ Converges in 52s, below 60s SLA but degraded)
- Root analysis: VLAN 15 root is SW-C (Cap-Haitian, edge node), STP BPDUs must traverse 4+ hops
- Fix: Modify VLAN 15 priority on SW-B (Port-au-Prince, mesh-central), elect SW-B as root
- Result: Convergence improves to 28s under jitter (above target)
- Audit: Log shows VLAN 15 STP change, VACL still enforcing Health isolation, no breaches

**Stretch:** Optimize all 20 VLANs' roots simultaneously for max parallelism (different roots per VLAN), measure overall P38 convergence time.

**Self-Assessment:**
- BSL-1 (P38 PVST+ Ready): Verify per-VLAN STP state, identify slow VLANs
- BSL-2 (P38 PVST+ Stressed): Measure convergence under jitter, identify mesh-suboptimal roots
- BSL-3 (P38 PVST+ Optimized): Fix VLAN root placement, achieve < 40s convergence per VLAN under stress
- BSL-4 (Haiti P38 Operations): Support P38 PVST+ operations, troubleshoot issues in field
- BSL-5 (Haiti P45 PVST+): Scale PVST+ optimization to 200 nodes, 8 hubs
- BSL-6 (Haiti P52 PVST+): Manage PVST+ at national scale
- BSL-7 (Haiti PVST+ Authority): Lead P38/P45/P52 STP deployment, mentor teams, publish PVST+ design guide

---
**Field-7 Focus:** P38 PVST+ troubleshooting integrating all field requirements, proving network stable at scale.
