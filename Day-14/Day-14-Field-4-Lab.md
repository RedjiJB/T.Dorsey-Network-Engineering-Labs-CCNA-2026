# Day 14: VLAN Troubleshooting & Advanced Trunking (Security Field)

## 0. Metadata
- **Objective:** Troubleshoot VLAN trunking while maintaining VACL security enforcement; diagnose without breaking audit trail
- **Research Field:** Field-4: Security
- **Proof Obligations:** VLAN troubleshooting preserves security isolation; all diagnostic commands logged; zero unauthorized access during troubleshooting
- **Haiti Deployment Phase:** P38 (healthcare security)
- **Relevant RFC/Standards:** IEEE 802.1Q, HIPAA audit logging
- **Prerequisites:** Days 1-13 + Field-4 prerequisites
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 3 switches with VACL support, 4 PCs, syslog server
- **Key Concepts:** Secure troubleshooting, audit trail preservation, VACL-aware diagnostics

## 1. Business Context (Field-4: Security)
Field-4 proves VLAN troubleshooting can proceed **without compromising security isolation**. Scenario: Healthcare network (HIPAA-regulated) has intermittent VLAN connectivity issue. Troubleshooting must resolve problem while:
1. Maintaining VACL enforcement (Patient VLAN 10 cannot reach Admin VLAN 20)
2. Logging all diagnostic steps for audit
3. Zero unauthorized access during repair

**Success Metric:** Fix VLAN misconfiguration, verify security still enforced, produce audit trail proving zero breach.

## 2. Topology Diagram (Secure Troubleshooting)
```
[Patient-Data-VLAN-10]──[VACL-Enforced]──[Admin-VLAN-20]
   |                      (logged)              |
[SW1]--[SW2]-------[SW3]              [Audit Log]
 |      |            |                 (syslog)
PC1    PC2          PC3
V10    V10          V20
```

## 3. IP Addressing Plan (Audited, Isolated)
| Device | VLAN | IP Address | VACL Status | Notes |
|--------|------|-----------|-------------|-------|
| PC1 | 10 | 10.0.10.10 | Allowed intra-VLAN | Patient data |
| PC2 | 10 | 10.0.10.20 | Allowed intra-VLAN | Patient data |
| PC3 | 20 | 10.0.20.10 | Allowed intra-VLAN | Admin data |

## 4. Field-4-Specific Configuration

### 4.1 Create Misconfiguration + VACL Active
```
! Misconfiguration: SW2 trunk missing VLAN 10
Switch-2(config-if)# switchport trunk allowed vlan 1,20

! VACL policy active (Patient 10 ≠ Admin 20)
Switch-1(config)# vlan access-map SECURITY_ISOLATION 1
Switch-1(config-access-map)# deny ip 10.0.10.0 0.0.0.255 10.0.20.0 0.0.0.255 log
! All deny attempts logged for audit

! Start syslog server for audit capture
```

### 4.2 Secure Troubleshooting Procedure
```
! Diagnostic steps logged automatically (VACL "log" keyword)

! Step 1: Identify problem (with audit trail)
Switch-1# show int g0/1 switchport | include Allowed Vlans
! Expected: Shows VLAN 10 missing on SW2-to-SW3 trunk
! This command logged for audit: "Operator viewed trunk config at [timestamp]"

! Step 2: Verify VACL still active
Switch-1# show vlan access-map
! Confirm SECURITY_ISOLATION map in place

! Step 3: Fix misconfiguration (audit captures change)
Switch-2(config-if)# switchport trunk allowed vlan add 10
! Change logged: "Modified trunk allowed VLANs on [date/time] by [user]"

! Step 4: Verify fix without breaking security
PC1> ping 10.0.10.20  ← Allowed (intra-VLAN)
PC1> ping 10.0.20.10  ← Denied (VACL blocks, logged)

! Audit log entry created: "Denied: 10.0.10.1 → 10.0.20.1 [timestamp]"
```

## 5. Field-4-Specific Verification Steps

### 5.1 Security Preservation During Troubleshooting
```
! Before fix:
PC1> ping 10.0.10.20  ← Fails (trunk misconfigured)

! Apply fix
Switch-2(config-if)# switchport trunk allowed vlan add 10

! After fix:
PC1> ping 10.0.10.20  ← SUCCESS (intra-VLAN allowed)
PC1> ping 10.0.20.10  ← FAILS (VACL denies inter-VLAN)

! Verify VACL logged the denial
Switch-1# show log | grep 10.0.10 | grep 10.0.20
! Expected: Entry showing "Denied" with timestamp and packet count
```

### 5.2 Audit Trail Completeness
```
! Extract full troubleshooting audit trail
Switch-1# show log > troubleshooting_audit.txt

! Verify log contains:
! 1. Timestamp of initial ping failure
! 2. Timestamp of diagnostic commands
! 3. Timestamp of configuration change
! 4. Timestamp of successful ping
! 5. All VACL deny attempts logged

! Generate HIPAA-compliant audit report
! "All troubleshooting steps logged and verified secure"
```

## 6. Expected Output Gallery

### 6.1 Trunk Status During Troubleshooting
```
Switch-2# show int g0/3 switchport | include Allowed
Allowed Vlans: 1,20  ← Initially missing 10

! After fix:
Allowed Vlans: 1,10,20  ← VLAN 10 added
```

### 6.2 Audit Log Entries (Security Preserved)
```
Switch-1# show log | include "10.0"
Sep 11 14:22:33.456 UTC: %ACL-4-ACLLOG_FLOW_INTERVAL: Denied src 10.0.10.10 dest 10.0.20.10, 1 packet
Sep 11 14:22:34.789 UTC: %CONFIG-5-CONFIG_I: Configured from console by admin
Sep 11 14:22:35.012 UTC: %ACL-4-ACLLOG_FLOW_INTERVAL: Denied src 10.0.10.10 dest 10.0.20.10, 2 packets
```

## 7. Common Field-4-Specific Mistakes

### 7.1 MISTAKE: Temporarily Disabling VACL to Troubleshoot
```
! Error: Remove VACL to make "fix easier" (violates HIPAA)
! Field-4 Fix: NEVER disable security during troubleshooting
! Alternative: Log all diagnostic steps instead
```

### 7.2 MISTAKE: Not Reviewing Audit Log After Repair
```
! Error: Fix issue but don't verify audit trail
! Field-4 Fix: Always generate audit report proving security maintained
```

## 8. Troubleshooting by Field

### 8.1 Audit Log Gaps (Missing Entries)
```
! Symptom: VACL deny attempts not appearing in log

! Field-4 Fix:
! 1. Verify logging enabled: show logging | include enabled
! 2. Verify ACL has "log" keyword: show access-list | include log
! 3. Check log buffer size: show logging buffer-size
! 4. If still missing: Enable terminal monitor to see real-time logs
```

## 9. Design Analysis (Why for Field-4)
Healthcare troubleshooting must maintain **compliance during operations**. This lab proves security isolation can be preserved while diagnosing and fixing network problems, essential for HIPAA certification.

## 10. Real-World Parallel
**Haiti P38 Healthcare Network:** When VLAN issues occur, IT must fix problem while maintaining patient data isolation and creating audit trail proving no breach occurred.

## 11. Stretch Goals
1. Generate monthly HIPAA audit report (all troubleshooting steps + security proof)
2. Implement alerting for unauthorized inter-VLAN attempts during troubleshooting
3. Train IT staff on secure troubleshooting procedures

## 12. Self-Assessment (Field-4 BSL)
- **BSL-1:** Troubleshoot VLAN issue with VACL active
- **BSL-2:** Fix problem, verify security still enforced, review audit log
- **BSL-3:** Generate HIPAA-compliant audit report
- **BSL-4:** Deploy to Haiti P38 healthcare pilot, maintain 100% audit trail

---

**End of Day-14 Field-4 Lab**
**Research Field:** Security | **Haiti Phase:** P38
**Generated for:** CCNA VLAN & STP Research Program
