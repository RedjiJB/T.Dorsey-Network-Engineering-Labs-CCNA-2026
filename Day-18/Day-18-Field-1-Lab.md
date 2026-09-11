# Day 18: Spanning Tree Protocol (Black Start)
## 0. Metadata
- **Objective:** Deploy offline-resilient STP topology for Haiti P38
- **Research Field:** Field-1: Black Start
- **Proof:** STP topology cached in NVRAM, root bridge persistent across power loss, bridge IDs static
- **Haiti Phase:** P38 (offline STP)
- **Hardware:** 3+ switches, no internet dependency

## 1-12. Field-1 Offline STP Deployment
**Context:** Haiti P38 STP must function offline. Root bridge election result (including bridge IDs, priorities) must persist in NVRAM. During power outage lasting 6+ hours, STP topology remains unchanged (no re-election, no topology flaps).

**Topology:** 3 switches, one designated root (lowest priority), STP running.

**Config:** Configure STP with explicit root bridge (priority 0 on SW1). Save to NVRAM. Simulate power loss.

**Offline Test:** After 6-hour offline period, reload router/switches. STP topology should be identical (same root, same port states) without any re-election or topology change.

**Verification:**
- Before offline: show spanning-tree | include "Bridge ID"
- After reload: show spanning-tree | include "Bridge ID" (should be identical)

**Expected:** No STP topology changes, network behaves identically after offline period.

**Mistakes:** Not caching STP state (rely on flash:vlan.dat), assuming STP needs dynamic re-election.

**Design Analysis:** Offline-first STP means static topology, no dynamic convergence. Field-1 prioritizes predictability over adaptability.

**Real-World:** Haiti P38 Clinic: STP root is always SW1 (locally cached). During power outage, STP topology identical when power restored. No topology flaps, predictable network behavior.

**Self-Assessment:** BSL-1=Design static STP, cache root bridge; BSL-2=Verify offline persistence; BSL-3=Deploy P38 with stable STP.

---
