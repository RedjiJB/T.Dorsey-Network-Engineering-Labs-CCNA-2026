# Day 15: VLAN Design & Multi-VLAN Topology (Security)
## 0. Metadata: Field-4 Secure VLAN Design
- **Objective:** Design VLAN topology with VACL enforcement and audit trail
- **Research Field:** Field-4: Security
- **Proof:** VLAN isolation enforced; all traffic violations logged; HIPAA-compliant audit trail
- **Haiti Phase:** P38 (healthcare security)
- **Hardware:** 4 switches with VACL support, 1 router, 8 PCs, syslog server
- **Prerequisites:** Days 1-14 + Field-4

## 1-12. Field-4 Secure Design
**Context:** Design Haiti P38 healthcare VLAN topology with security isolation. Health VLAN (10) must be completely isolated from other departments (20-40). All violations logged for HIPAA audit.

**Topology:** 4 switches, 4 departments (Health 10, Education 20, Commerce 30, Government 40), all trunks have VACL enforcing isolation.

**IP Plan:** Same as base (10.0.10/24 through 10.0.40/24), but all IPs in Health VLAN tagged as encrypted/PII.

**Config:** Create VLANs + trunks (baseline), then add VACL:
- Deny Health (10) to other VLANs (20-40)
- Allow intra-VLAN (10↔10, 20↔20, etc.)
- Log all denies for audit trail

**Verification:**
1. Intra-VLAN traffic allowed (Health PC1 → Health PC2 works)
2. Inter-VLAN traffic denied (Health PC1 → Admin PC3 blocked)
3. All denies logged with timestamp, source MAC, dest MAC

**Expected:** VACL active, 100% enforcement, no breaches.

**Mistakes:** VACL too permissive, logging not enabled, missing audit trail.

**Troubleshooting:** If Health→Admin allowed, VACL incorrect. Verify deny ACL exists and VLAN filter applied.

**Design Analysis:** Healthcare deployment requires audit trail proving isolation maintained. VACL + logging provides this proof for HIPAA certification.

**Real-World:** Haiti P38 Healthcare: Monthly audit report generated from VACL logs, proving no unauthorized access occurred. Required for regulatory approval.

**Stretch:** Implement syslog export, generate monthly HIPAA reports, test encryption on Health VLAN.

**Self-Assessment:** BSL-1=Design VLANs+add VACL; BSL-2=Verify enforcement+logging; BSL-3=Generate audit report; BSL-4=Deploy to Haiti P38 healthcare+pass HIPAA audit.

---
**Field-4 Design Focus:** Prove secure VLAN design maintains isolation and audit trail.
