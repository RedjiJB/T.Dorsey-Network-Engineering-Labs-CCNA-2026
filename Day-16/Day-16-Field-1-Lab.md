# Day 16: Voice VLAN & Advanced Security (Black Start)
## 0. Metadata
- **Objective:** Design offline-ready Voice VLAN topology with QoS tagging in Haiti P38
- **Research Field:** Field-1: Black Start
- **Proof:** Voice VLAN (110) functional offline, priority tagging preserved in NVRAM, static voice device IPs
- **Haiti Phase:** P38 (offline pilot)
- **Hardware:** 4 switches, 1 router, 8 PCs, 2 IP phones, cache storage
- **Prerequisites:** Days 1-15 + Field-1

## 1-12. Field-1 Voice VLAN Design
**Context:** Design Haiti P38 Voice VLAN (110) for offline operation. Voice requires priority QoS even during power loss. Data VLAN 10, Voice VLAN 110, both with static IPs and cached configs.

**Topology:** Standard with Voice VLAN 110 on trunk, QoS marking cached (802.1p CoS values preserved in NVRAM).

**IP Plan:** 
- Data VLAN 10: 10.0.10.0/24 (static, cached)
- Voice VLAN 110: 10.0.110.0/24 (static, IP phones pre-provisioned)

**Config:** Voice VLAN on access ports + IP phone switchport voice vlan 110. QoS configs cached via "write memory".

**Verification:** After reload, Voice VLAN 110 active, IP phones get VLAN 110, data PCs get VLAN 10. Cold-start validation: both VLANs functional within 30s of power restoration.

**Expected:** Voice traffic prioritized even offline, no external dependency (no DHCP for phones).

**Mistakes:** Not caching QoS configs, DHCP-assigned phone IPs (breaks offline), Voice VLAN not on all switch trunks.

**Troubleshooting:** If Voice VLAN not persisting after reload, check flash:vlan.dat and NVRAM config completeness.

**Design Analysis:** Voice prioritization must survive offline periods (Haiti's frequent power loss scenario).

**Real-World:** Haiti P38 Clinic: During power loss, phones connect to Voice VLAN 110 (cached). Voice traffic tagged 802.1p priority 5 (marked in startup-config). Regular power restoration: phones resume service without reconfiguration.

**Stretch:** Test voice QoS metrics during offline operation, verify prioritization over data traffic.

**Self-Assessment:** BSL-1=Design Data+Voice VLANs; BSL-2=Cache configs, verify cold-start; BSL-3=Deploy to P38 pilot, measure phone reconnection time.

---
