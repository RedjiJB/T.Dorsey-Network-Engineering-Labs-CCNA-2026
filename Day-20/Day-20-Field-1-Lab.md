# Day 20: MSTP (Multiple Spanning Tree) (Black Start)
## 0. Metadata
- **Objective:** Deploy offline-resilient MSTP with region-aware STP instances
- **Research Field:** Field-1: Black Start
- **Proof:** MSTP reduces STP instances (per-VLAN inefficient for 20+ VLANs), VLAN groups use shared STP tree, offline-capable
- **Haiti Phase:** P38 (offline MSTP)

## 1-12. Field-1 Offline MSTP Deployment
**Context:** Haiti P38 has 20 VLANs. Instead of 20 PVST+ instances, use MSTP to group VLANs (e.g., Health VLANs 10-19 share one STP tree, other VLANs share another). Reduces CPU/memory, maintains offline caching.

**Config:** Enable MSTP on all switches. Define region + VLAN mapping (2-3 STP instances instead of 20). Cache MSTP configs to NVRAM.

**Offline Test:** Power loss → verify MSTP region and tree assignments persist, convergence < 5s on reload.

**Verification:** MSTP reduces STP overhead while offline-capable.

**Real-World:** Haiti P38 MSTP: Health VLANs (10-19) mapped to MSTI 1, Commerce/Gov VLANs (30-49) mapped to MSTI 2. Single Education VLAN (20-29) mapped to CIST (CST—Common Spanning Tree). Only 3 STP trees instead of 20, offline-cacheable.

**Self-Assessment:** BSL-1=Configure MSTP regions; BSL-2=Verify offline caching; BSL-3=Deploy P38 MSTP.

---
