# Day 17: VLAN Troubleshooting & PVST+ (Security)
## 0. Metadata
- **Objective:** Troubleshoot PVST+ while maintaining security isolation via VACL; all diagnostics logged
- **Research Field:** Field-4: Security
- **Proof:** STP changes don't break security, all topology changes logged for audit
- **Haiti Phase:** P38 (healthcare security)
- **Hardware:** 3 switches with VACL, PVST+ with logging

## 1-12. Field-4 Secure PVST+ Troubleshooting
**Context:** Healthcare PVST+ troubleshooting must maintain HIPAA compliance. When STP root changes (e.g., due to priority modification), ensure Health VLAN (10) isolation still enforced. All STP changes logged.

**Config:** PVST+ with VACL denying Health (10) to other VLANs. Create STP misconfiguration (e.g., SW3 incorrectly has lower priority for VLAN 10).

**Troubleshooting While Secure:**
1. Identify misconfigured root: show spanning-tree vlan 10 | include "This bridge"
2. Verify VACL still active: show vlan access-map
3. Fix STP by adjusting priority on correct switch
4. Monitor VACL audit log during fix to ensure no breaches
5. Verify: STP converged + VLAN 10 still isolated

**Verification:**
- Before fix: STP root correct, VACL enforced
- During fix: Modify priority, STP recalculates
- After fix: Root changed to intended switch, VACL still denies cross-VLAN traffic, all changes logged

**Expected:** PVST+ corrected, security maintained, audit trail complete.

**Mistakes:** Disabling VACL to troubleshoot (violates HIPAA), no logging of STP changes.

**Design Analysis:** Healthcare STP changes must not introduce security loopholes. Logging proves no breach occurred.

**Real-World:** Haiti P38 Healthcare: IT team modifies PVST+ priority during maintenance. Audit log captures: timestamp of change, old/new root, VACL enforcement status before/after. This proves STP work didn't compromise patient data isolation.

**Stretch:** Implement automated STP change alerts, archive audit logs for compliance review.

**Self-Assessment:** BSL-1=Troubleshoot PVST+ with VACL active; BSL-2=Verify security during STP changes; BSL-3=Generate audit report; BSL-4=Deploy to healthcare with logging.

---
