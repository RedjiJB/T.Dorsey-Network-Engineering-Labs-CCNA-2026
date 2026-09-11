# Day 16: Voice VLAN & Healthcare AI (Healthcare AI)
## 0. Metadata  
- **Objective:** Design Voice VLAN for healthcare AI deployment; medical records in Health VLAN, voice calls in Voice VLAN, AI inference in separate VLAN
- **Research Field:** Field-5: Healthcare AI (PII protection)
- **Proof:** Voice traffic separated from medical records; AI inference doesn't access voice data; anonymization enforced
- **Haiti Phase:** P38 (healthcare AI pilot)
- **Hardware:** 4 switches, 1 router, 8 PCs, 2 IP phones, AI inference appliance
- **Prerequisites:** Days 1-15 + Field-5

## 1-12. Field-5 Healthcare Voice + AI Design
**Context:** Haiti P38 healthcare network with Voice VL AN (110) and AI inference (VLAN 50). Ensure AI doesn't process voice recordings (voice is separate). Medical records (VLAN 10) encrypted, AI sees only anonymized data.

**Topology:** Health Records (VLAN 10, encrypted PII) → Voice (VLAN 110, doctor calls) → AI Inference (VLAN 50, anonymized only).

**IP Plan:**
- Health Records: 10.0.10.0/24 (encrypted, PII)
- Voice: 10.0.110.0/24 (voice traffic, not AI input)  
- AI Inference: 10.0.50.0/24 (anonymized data only)

**Config:** Separate VLANs for each data sensitivity level. Add access control: AI inference can read from Health records ONLY if anonymized; no direct access to voice data.

**Verification:**
- Health PC connects to VLAN 10 (encrypted)
- Phone connects to VLAN 110 (voice only)
- AI appliance connects to VLAN 50 (reads anonymized subsets from VLAN 10, NOT from VLAN 110)
- Audit trail shows AI access to only anonymized fields

**Expected:** Complete data separation, AI operates on PII-free subset, compliance maintained.

**Mistakes:** AI appliance on same VLAN as voice (could record calls), no anonymization filtering, medical records in plaintext.

**Troubleshooting:** If AI inference slow, check if filtering to anonymized-only is working correctly (verify access logs).

**Design Analysis:** Healthcare AI requires strict data separation—patient voice calls must not be ML training data without explicit consent. VLAN isolation enforces this.

**Real-World:** Haiti P38 AI: AI system helps diagnose diseases but NEVER processes voice recordings (separate VLAN). Uses only anonymized lab results (VLAN 10 with PII stripped). Complies with healthcare privacy regulations.

**Stretch:** Implement homomorphic encryption on AI inputs, train AI on encrypted data, verify no PII leakage in inference outputs.

**Self-Assessment:** BSL-1=Design 3 VLANs (Health/Voice/AI); BSL-2=Verify data separation+anonymization; BSL-3=Deploy AI inference, validate PII protection; BSL-4=Pass healthcare AI audit.

---
