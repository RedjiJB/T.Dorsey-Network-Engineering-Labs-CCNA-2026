# Day 15: VLAN Design & Multi-VLAN Topology (Black Start)
## 0-12. Field-1 Offline-First Design
- **Objective:** Design 4-VLAN offline-first topology (Haiti P38)
- **Research Field:** Field-1: Black Start
- **Proof:** All VLANs cached offline, functional without management access
- **Phases:** P38 (offline pilot design)
- **Design:** Health/Education/Commerce/Government VLANs (10-40), all IPs static and cached to NVRAM/Flash
- **Verification:** After 12-hour offline: all subinterfaces active, all VLANs routable, zero reconfiguration needed
- **Real-World:** Haiti P38 deploy VLAN design for power-loss scenarios (6+ hour outages)
- **Stretch:** Cache design to USB drive, train field operators with laminated reference cards

**Field-1 BSL:** BSL-1=Design 4 VLANs/cache configs; BSL-2=Verify offline after reload; BSL-3=Create operator playbook; BSL-4=Deploy to P38 pilot
---
