# Day 13: VLAN Routing & Inter-VLAN Communication (Security Field)

## 0. Metadata
- **Objective:** Implement ROAS with VLAN Access Control Lists (VACL) and packet-level attestation between VLANs
- **Research Field:** Field-4: Security (Cryptographic Attestation & Audit Trails)
- **Proof Obligations:** All inter-VLAN traffic enforces VACL policy; packets include attestation headers; routing decisions logged and verifiable
- **Haiti Deployment Phase:** P38 (security-hardened pilot, 50 nodes)
- **Relevant RFC/Standards:** IEEE 802.1Q, RFC 2827 (ingress filtering), RFC 5737 (documentation)
- **Prerequisites:** Days 1-12 + Field-4 prerequisites (VACL configuration, packet inspection)
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced (security + routing)
- **Hardware Required:** 1-2 routers, 2-3 switches with VACL support, 3-4 PCs, packet analyzer
- **Key Concepts:** VACL (VLAN ACLs), inter-VLAN isolation, traffic inspection, audit logging

## 1. Business Context (Field-4: Security)
Field-4 optimizes for **encrypted healthcare networks, financial systems, or government data**. Haiti P38 healthcare site must prove VLAN isolation prevents unauthorized access between departments:

**Real Scenario:** Hospital network has Patient Data VLAN (10) and Admin VLAN (20). Must prove no Patient data leaks to Admin VLAN (HIPAA compliance). VACL enforces per-packet inspection; all violations logged for audit.

**Success Metric:** 100% enforcement of inter-VLAN policy; zero policy violations in 1-hour test; all violations logged with timestamp, source MAC, destination MAC, packet content.

## 2. Topology Diagram (Secure VLAN Isolation)
```
┌──────────────────────────────────────────────┐
│      [VLAN Inspection Layer]                 │
│  (VACL on all switch trunk ports)            │
│                                              │
│  [Patient-Data-VLAN-10]  [Admin-VLAN-20]    │
│         (Encrypted)         (Encrypted)      │
│         |                   |                │
│     [SW1: Access]-------[SW2: Access]       │
│      /    \              /    \              │
│   PC1      PC2        PC3      PC4          │
│   Patient  Health     Admin    Finance      │
│   (VLAN10) (VLAN10)   (VLAN20) (VLAN20)    │
│                                              │
│  [VACL Policy Matrix]                        │
│   VLAN 10 ↔ VLAN 20: DENY (audit all)      │
│   VLAN 10 ↔ VLAN 10: ALLOW (same dept)     │
│   VLAN 20 ↔ VLAN 20: ALLOW (same dept)     │
│                                              │
│  [Audit Log]                                 │
│   - Timestamp                                │
│   - Source VLAN, Source MAC                 │
│   - Dest VLAN, Dest MAC                     │
│   - Action (ALLOW/DENY)                     │
│   - Packet hash (for forensics)              │
└──────────────────────────────────────────────┘
```

**Field-4 Modifications:**
- Add VACL on all trunks (deny inter-VLAN by default)
- Log all VLAN-crossing attempts (even denied)
- Add packet inspection (verify headers valid)
- Implement audit trail (timestamp, MAC, action, hash)

## 3. IP Addressing Plan (Secure, Isolated)
| Device | VLAN | IP Address | Isolation Level | Notes |
|--------|------|-----------|-----------------|-------|
| PC1-Patient | 10 | 10.0.10.10 | Encrypted, Logged | PII protected |
| PC2-Health | 10 | 10.0.10.20 | Encrypted, Logged | Same VLAN (allow) |
| PC3-Admin | 20 | 10.0.20.10 | Encrypted, Logged | Separate domain |
| PC4-Finance | 20 | 10.0.20.20 | Encrypted, Logged | Separate domain |
| Router-ROAS | 10 | 10.0.10.1 | Encrypted | Inter-VLAN only if approved |
| Router-ROAS | 20 | 10.0.20.1 | Encrypted | Inter-VLAN only if approved |

## 4. Field-4-Specific Configuration

### 4.1 ROAS Configuration (Baseline)
```
! Standard ROAS setup (same as Day-13 base)
Router> en
Router# conf t

Router(config)# int g0/0
Router(config-if)# no shutdown
Router(config-if)# exit

Router(config)# int g0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 10.0.10.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# int g0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 10.0.20.1 255.255.255.0
Router(config-subif)# no shutdown
Router(config-subif)# exit

Router(config)# end
Router# write memory
```

### 4.2 VACL (VLAN ACL) Configuration (Field-4 Specific)
```
! Define which VLANs can communicate (security policy)
! Policy: VLAN 10 (Patient) cannot talk to VLAN 20 (Admin)

Switch> en
Switch# conf t

! Create ACL for inter-VLAN traffic (deny 10→20)
Switch(config)# ip access-list extended VLAN10_to_VLAN20
Switch(config-ext-acl)# deny ip 10.0.10.0 0.0.0.255 10.0.20.0 0.0.0.255
Switch(config-ext-acl)# permit ip any any
Switch(config-ext-acl)# exit

! Create VLAN ACL (VACL) that applies ACL to inter-VLAN traffic
Switch(config)# vlan access-map VLAN_ISOLATION 1
Switch(config-access-map)# match ip address VLAN10_to_VLAN20
Switch(config-access-map)# action deny
Switch(config-access-map)# exit

Switch(config)# vlan access-map VLAN_ISOLATION 2
Switch(config-access-map)# match ip address any
Switch(config-access-map)# action forward
Switch(config-access-map)# exit

! Apply VACL to VLAN 10 and 20 (enforce policy on both)
Switch(config)# vlan filter VLAN_ISOLATION vlan-list 10,20

! Enable logging (Field-4 audit requirement)
Switch(config)# access-list 101 deny ip 10.0.10.0 0.0.0.255 10.0.20.0 0.0.0.255 log
Switch(config)# access-list 101 permit ip any any

Switch(config)# int vlan 10
Switch(config-if)# ip access-group 101 in
Switch(config-if)# exit

Switch(config)# end
Switch# write memory
```

### 4.3 Audit Logging Configuration (Field-4 Governance)
```
! Enable comprehensive logging for compliance audit
Switch# conf t

! Log all denied packets (security violations)
Switch(config)# logging enable
Switch(config)# logging buffered 4096
Switch(config)# logging buffer-size 32768

! Set timestamp format for audit trail
Switch(config)# service timestamps debug datetime msec
Switch(config)# service timestamps log datetime msec

! Log to external server (for P38 field deployment)
! Switch(config)# logging 192.168.1.100  ← Syslog server IP (field-deployed)

Switch(config)# end
Switch# write memory

! Verify logging active
Switch# show logging | include enabled
! Expected: "Syslog logging: enabled"
```

## 5. Field-4-Specific Verification Steps

### 5.1 VACL Policy Enforcement Test
```
! Test 1: VLAN 10→10 (same VLAN, should allow)
PC1-Patient> ping 10.0.10.20  (PC2-Health, same VLAN)
! Expected: Reply (allowed by VACL)

! Test 2: VLAN 10→20 (different VLAN, should deny)
PC1-Patient> ping 10.0.20.10  (PC3-Admin, different VLAN)
! Expected: Request timeout (denied by VACL)

! Test 3: VLAN 20→20 (same VLAN, should allow)
PC3-Admin> ping 10.0.20.20  (PC4-Finance, same VLAN)
! Expected: Reply (allowed by VACL)

! Field-4 Success: Isolation enforced at packet level
```

### 5.2 Audit Log Verification
```
! Check system log for denied packets
Switch# show log | include VLAN10_to_VLAN20
! Expected output:
! *Sep 11 12:34:56.123 UTC: %ACL-4-ACLLOG_FLOW_INTERVAL: ...
!   Denied flow: VLAN 10 src 10.0.10.10 → dest 10.0.20.10

! Verify timestamp present (audit trail requirement)
! Extract CSV for compliance report:
Switch# show log | include "10.0.10" > audit.log
! Then process audit.log for HIPAA/SOC2 compliance
```

### 5.3 Logging Configuration Validation
```
! Verify VACL logging active
Switch# show vlan filter
! Expected: "VLAN_ISOLATION vlan-list 10,20"

! Verify ACL statistics
Switch# show access-list VLAN10_to_VLAN20
! Expected: Match count > 0 (if tests ran)

! Test logging to remote syslog (P38 field deployment)
! Switch# terminal monitor  (enables log output to console)
! Then run ping test, watch for log output
```

## 6. Expected Output Gallery (Security Audit)

### 6.1 Allowed Traffic (Same VLAN)
```
PC1-Patient> ping 10.0.10.20
Reply from 10.0.10.20: bytes=32 time=3ms TTL=64
[VACL allows same-VLAN traffic; no log entry]
```

### 6.2 Denied Traffic (Cross-VLAN)
```
PC1-Patient> ping 10.0.20.10
Request timeout
[VACL denied; log entry created]
```

### 6.3 Audit Log Entry
```
Switch# show log | grep 10.0.10
Sep 11 12:35:00.456 UTC: %ACL-4-ACLLOG_FLOW_INTERVAL: Src 10.0.10.10, 
  Dest 10.0.20.10, Proto TCP, Deny, 5 packets in 1 second
```

## 7. Common Field-4-Specific Mistakes

### 7.1 MISTAKE: VACL Applies to All VLANs Globally
```
! Error: vlan filter applied to entire device, not just VLAN 10/20
! Field-4 Fix: Explicitly list allowed VLANs in vlan filter command
! Correct: vlan filter VLAN_ISOLATION vlan-list 10,20
! Wrong: vlan filter VLAN_ISOLATION vlan-list all
```

### 7.2 MISTAKE: Not Logging VACL Violations
```
! Error: Denying traffic but no audit trail (fails compliance)
! Field-4 Fix: Add "log" keyword to ACL deny statements
! Correct: deny ip 10.0.10.0 0.0.0.255 10.0.20.0 0.0.0.255 log
```

### 7.3 MISTAKE: Timestamp Missing in Logs
```
! Error: Logs show "Denied VLAN 10→20" but no timestamp
! Field-4 Fix: Enable service timestamps
! Switch(config)# service timestamps log datetime msec
```

## 8. Troubleshooting by Field (Field-4: Security Enforcement)

### 8.1 VACL Denies All Traffic (Too Restrictive)
```
! Symptom: Even allowed VLANs cannot communicate

! Diagnostic:
Switch# show vlan access-map VLAN_ISOLATION
! Check if "action forward" present in map 2

! Field-4 Fix:
! Verify ACL order: deny first (specific), then permit (catch-all)
! Verify action: deny → map stops, forward → continue processing
```

### 8.2 Audit Logs Empty (Logging Not Working)
```
! Symptom: Denied traffic occurs but no log entries

! Diagnostic:
Switch# show logging | include enabled
! If disabled → enable first

! Field-4 Fix:
! 1. Verify logging enabled: logging enable
! 2. Verify ACL includes "log": show access-list VLAN10_to_VLAN20
! 3. Test with verbose output: terminal monitor
! 4. Run test traffic and watch for log output
```

## 9. Design Analysis (Why for Field-4)

**Why VACL Security Enforcement for Haiti Healthcare?**

1. **Compliance Requirement (HIPAA)**
   - Patient data (VLAN 10) must not leak to Admin systems (VLAN 20)
   - Proof obligation: Document all inter-VLAN denials
   - Audit trail: Timestamp + packet details for investigation

2. **Packet-Level Enforcement**
   - VLAN routing alone doesn't prevent cross-VLAN attacks
   - VACL intercepts packets at Layer 2, before Layer 3 routing
   - Proves medical data separated at packet level (not just VLAN tag)

3. **Attestation for Field Operations**
   - Logs prove "Patient data was not accessed by Admin systems during P38"
   - Signed log file serves as audit trail for certification
   - Required for healthcare deployment approval

## 10. Real-World Parallel (Haiti Deployment)

**Haiti P38 Healthcare Site (Security Hardened):**
- Hospital network: Patient Data (VLAN 10), Admin/Finance (VLAN 20)
- VACL policy enforced: VLAN 10 ↔ 20 deny, same-VLAN allow
- All cross-VLAN attempts logged to syslog server
- **Audit Requirement:** Monthly review of denied packets (expect ~100-200/day attempts)

**Field-4 Validation Gate:**
- ✓ VACL policy active (deny cross-VLAN)
- ✓ Logging functional (5+ denied packets captured in test)
- ✓ Timestamp accurate (audit-admissible format)
- ✓ Same-VLAN traffic allowed (no false positives)

**P38 Deployment Decision:**
- IF: Zero false positive denies + proper logging → Approved
- IF: Logging failures → Resolve before healthcare deployment

## 11. Stretch Goals (Field-4 Advanced)

1. **Add Conditional Allow Policy**
   - Allow specific Patient→Admin flows (e.g., backup server IP)
   - Configure VLAN_ISOLATION map with conditional permit
   - Test whitelist works while denying others

2. **Syslog Integration**
   - Deploy syslog server (internal or cloud)
   - Configure switch to log all denies to server
   - Verify log rotation and storage for 90 days (healthcare retention)

3. **Compliance Report Generation**
   - Extract logs for audit period (1 month)
   - Generate report: Total denies, top sources, top destinations
   - Sign report for healthcare auditor approval

4. **Encryption Validation**
   - Capture packets crossing VLAN (should be encrypted if PII)
   - Verify no plaintext Patient data in captured packets
   - Generate forensic report

## 12. Self-Assessment (Field-4 Security Levels)

- **BSL-1 (VACL Ready):** Create ACL, apply VACL to 2 VLANs, test deny/allow
- **BSL-2 (Security Enforcement):** Verify cross-VLAN denied, same-VLAN allowed, logging active
- **BSL-3 (Audit Trail):** Capture 10+ denied packets, verify timestamp, generate compliance report
- **BSL-4 (Security Hardening):** Test edge cases (fragmented packets, encapsulated traffic), verify all denied
- **BSL-5 (Haiti P38 Pre-Deployment):** Deploy to hospital testbed, run 24-hour audit, train IT staff on logging
- **BSL-6 (Compliance Operations):** Implement automated audit reports, create alert for anomalies, train security team
- **BSL-7 (Healthcare Deployment Authority):** Deploy to Haiti P38 hospital, maintain audit trail, support regulatory inspection, mentor P45 healthcare expansion

---

**End of Day-13 Field-4 Lab**
**Research Field:** Security (Cryptographic Attestation) | **Haiti Phase:** P38 (Healthcare Deployment)
**Generated for:** CCNA VLAN & STP Research Program
