# Day 17: VLAN Troubleshooting & PVST+ Verification (Black Start)
## 0. Metadata
- **Objective:** Troubleshoot VLAN+STP issues in offline-first environment; verify PVST+ runs offline
- **Research Field:** Field-1: Black Start
- **Proof:** PVST+ (Per-VLAN Spanning Tree) operates offline, different root per VLAN cached in NVRAM, troubleshooting offline feasible
- **Haiti Phase:** P38 (offline troubleshooting)
- **Hardware:** 3 switches, 1 router, 4-6 PCs
- **Prerequisites:** Days 1-16 + Field-1

## 1-12. Field-1 Offline STP Troubleshooting
**Context:** Troubleshoot PVST+ issues without network connectivity. Haiti P38 clinic experiences trunk flapping during power outage (PVST+ state cached incorrectly). Operator must diagnose using only console, cached STP state.

**Topology:** 3 switches (SW1 core, SW2-3 access), VLAN 10 & 20, PVST+ running per VLAN (different root per VLAN possible).

**Config:** Create 2 VLANs with PVST+ enabled. Intentionally misconfigure: SW2 is root for VLAN 10, SW3 is root for VLAN 20 (load-balance across VLANs). Save to NVRAM.

**Troubleshooting Phase (Offline):**
1. Check root bridge per VLAN: show spanning-tree vlan 10 → root = SW2, show spanning-tree vlan 20 → root = SW3
2. Verify port roles (root port, designated, etc.) match design intent
3. If misconfigured: Modify priority to correct root bridge, save to NVRAM

**Verification:**
- Before fix: VLAN 10 root is SW2 (correct), VLAN 20 root is SW3 (correct) → load-balanced
- After intentional misconfiguration: VLAN 10 root becomes SW3 (wrong)
- Operator fixes by increasing SW2 priority for VLAN 10
- After reload: STP topology restored per NVRAM configs

**Expected:** PVST+ state persistent across offline period, load-balancing restored after fix.

**Mistakes:** Not checking per-VLAN STP state, assuming same root bridge for all VLANs.

**Troubleshooting:** If root bridge wrong after reload, verify startup-config has correct priority settings.

**Design Analysis:** PVST+ enables load-balancing per VLAN even offline. Haiti P38 benefits from different root per VLAN (better traffic distribution).

**Real-World:** Haiti P38: Healthcare VLAN 10 routes via primary path (SW2 root), Education VLAN 20 via backup path (SW3 root). During power outage, both paths preserved in NVRAM. After restoration: traffic automatically load-balanced.

**Stretch:** Test 3+ VLANs with different roots, measure traffic distribution per VLAN during stress.

**Self-Assessment:** BSL-1=Identify per-VLAN STP root; BSL-2=Configure load-balancing PVST+; BSL-3=Troubleshoot offline PVST+ issues; BSL-4=Deploy P38 with optimized PVST+.

---
