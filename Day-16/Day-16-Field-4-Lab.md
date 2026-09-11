# Day 16: Voice VLAN & Security (Security)
## 0. Metadata
- **Objective:** Design Voice VLAN with security enforcement; verify voice data protected with audit trail
- **Research Field:** Field-4: Security  
- **Proof:** Voice VLAN 110 isolated from data; voice calls not recorded improperly; audit trail of voice access
- **Haiti Phase:** P38 (healthcare security)
- **Hardware:** 4 switches with VACL, 1 router, 8 PCs, 2 IP phones, syslog
- **Prerequisites:** Days 1-15 + Field-4

## 1-12. Field-4 Secure Voice Design
**Context:** Design Haiti P38 Voice VLAN with security: Healthcare facilities need voice privacy (doctor-patient calls). Voice VLAN 110 must be isolated, voice traffic encrypted, audit trail maintained.

**Topology:** Data VLAN 10 (health records), Voice VLAN 110 (calls), both with VACL enforcement preventing data→voice unauthorized access.

**IP Plan:** Voice VLAN 110 (10.0.110.0/24) - static IP phones, encrypted TLS for call signaling.

**Config:** Add VACL to deny Health Data (10) accessing Voice VLAN (110). Enable logging on voice trunk.

**Verification:** 
- Data PC cannot ping voice phone IP (VLAN 110 blocked)
- Voice phones can call each other (110↔110 allowed)
- All voice access attempts logged

**Expected:** Voice isolation enforced, audit trail shows no unauthorized access, HIPAA-compliant.

**Mistakes:** Not isolating voice VLAN, voice traffic in plaintext (unencrypted), logging not enabled.

**Troubleshooting:** If voice phones can't register after adding VLAN isolation, verify DHCP/phone provisioning separated from data network.

**Design Analysis:** Healthcare requires voice privacy—doctors need confidential calls. VLAN isolation + audit trail provides this.

**Real-World:** Haiti P38 Healthcare: Patient call center uses Voice VLAN 110 (isolated). Monthly audit shows no unauthorized call access. HIPAA-compliant.

**Stretch:** Implement voice encryption (TLS), verify voice traffic encrypted end-to-end, test call privacy under stress.

**Self-Assessment:** BSL-1=Design Voice VLAN+VACL; BSL-2=Verify isolation+logging; BSL-3=Deploy to healthcare, maintain audit trail; BSL-4=Pass security audit.

---
