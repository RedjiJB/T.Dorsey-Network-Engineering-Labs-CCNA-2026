# Day 41: NAT/PAT for Healthcare AI (Field 5 - PII Protection)

## 0. Metadata

- **Objective:** Master NAT/PAT with PII-aware translation and HIPAA-compliant data protection
- **Research Field:** Field 5: Healthcare AI (Privacy/Fairness, PII Protection, Data Anonymization)
- **Proof Obligations:** Patient data is never exposed via NAT translation; all health information remains encrypted end-to-end; NAT rules prevent accidental PII leakage
- **Haiti Deployment Phase:** P45 (Healthcare data phase; HIPAA-equivalent compliance required)
- **Relevant RFC/Standards:** RFC 3022 (NAT Overview), HIPAA Security Rule (45 CFR § 164.300-316)
- **Prerequisites:** Days 1-40 + Field 5 healthcare privacy preparatory materials
- **Estimated Time:** 140 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 2 routers (with VLAN tagging), 2 switches, dedicated DLP (Data Loss Prevention) appliance, encryption appliances
- **Key Concepts:** Data classification, PII protection, HIPAA compliance, encryption enforcement, access control

## 1. Business Context

Healthcare deployments (Field 5) process Protected Health Information (PHI). NAT in healthcare must ensure that:

1. **No patient data leaves encrypted channels:** NAT rules block any unencrypted healthcare data
2. **Data access is logged:** Every patient record access is audit-logged
3. **Segregation of duties:** Clinical staff, research staff, and administrative staff have separate NAT rules
4. **Encryption is mandatory:** No healthcare data traverses NAT without end-to-end encryption

This lab demonstrates NAT rules that automatically prevent PII leakage, enforcing HIPAA compliance at the network layer.

## 2. Topology Diagram (Modified for Healthcare Privacy)

```
External Network               Healthcare Internal Network
    (Public Internet)          
         |                     [Clinical Data Network]
         |                     10.0.1.0/24 (Encrypted PHI)
    [NAT Router R1]                  |
    (HIPAA-aware)              [Patient Records DB]
         |                     [Care Provider Laptops]
    [DLP Appliance]                  |
    (Blocks PII exposure)      [Research Data Network]
         |                     10.0.2.0/24 (De-identified)
    [Firewall]                      |
         |                     [ML Inference Servers]
    [Switch SW1]               [Statistical Analysis]
         |
    [Clinical & Research]
    (Subject to Data Classification)
```

**Key difference from base:** NAT rules are segregated by data sensitivity; clinical data (PII) cannot traverse NAT; research data (anonymized) can.

## 3. IP Addressing Plan

| Device | Interface | IP Address | Subnet Mask | VLAN | Data Type | Encryption | Notes |
|--------|-----------|-----------|------------|------|-----------|------------|-------|
| NAT Router R1 | G0/0 | 200.1.1.2 | 255.255.255.0 | N/A | Public | TLS/IPsec | WAN gateway |
| NAT Router R1 | G0/1.1 | 10.0.1.1 | 255.255.255.0 | 10 | Clinical PHI | Required | HIPAA-regulated |
| NAT Router R1 | G0/1.2 | 10.0.2.1 | 255.255.255.0 | 20 | Research (De-id) | Required | De-identified data |
| Patient DB | NIC | 10.0.1.50 | 255.255.255.0 | 10 | Clinical | Encrypted | Contains raw PHI |
| Care Provider 1 | NIC | 10.0.1.10 | 255.255.255.0 | 10 | Clinical | Encrypted | Licensed clinician |
| Care Provider 2 | NIC | 10.0.1.11 | 255.255.255.0 | 10 | Clinical | Encrypted | Licensed clinician |
| Research Server | NIC | 10.0.2.20 | 255.255.255.0 | 20 | Research | De-identified | Limited NAT rules |

## 4. Field-Specific Configuration

### 4.1 Healthcare Data Classification

```cisco
! Define data classification tags for NAT rules
Router> enable
Router# configure terminal

! VLAN 10: Clinical Data (Contains PHI - Protected Health Information)
Router(config)# vlan 10
Router(config-vlan)# name CLINICAL_PHI
Router(config-vlan)# description Patient records, diagnoses, medications
Router(config-vlan)# exit

! VLAN 20: Research Data (De-identified, safe for external sharing)
Router(config)# vlan 20
Router(config-vlan)# name RESEARCH_DEIDENTIFIED
Router(config-vlan)# description Aggregated statistics, anonymized cohorts
Router(config-vlan)# exit

! VLAN 99: Administrative (Staff logins, billing - also sensitive)
Router(config)# vlan 99
Router(config-vlan)# name ADMIN_STAFF
Router(config-vlan)# description Administrative staff; credentials handled
Router(config-vlan)# exit

Router(config)# end
```

### 4.2 HIPAA-Compliant NAT Rules

```cisco
! Configure NAT rules that enforce data classification
Router# configure terminal

! Clinical data: DENY any unencrypted outbound traffic
Router(config)# access-list 110 deny ip 10.0.1.0 0.0.0.255 any
! (This prevents clinical data from leaving network unencrypted)

! Research data: ALLOW only de-identified data (encrypted)
Router(config)# access-list 120 permit tcp 10.0.2.0 0.0.0.255 any eq 443
Router(config)# access-list 120 permit tcp 10.0.2.0 0.0.0.255 any eq 22
Router(config)# access-list 120 deny ip 10.0.2.0 0.0.0.255 any log

! NAT pool for allowed research traffic
Router(config)# ip nat pool RESEARCH_EXTERNAL 200.1.1.10 200.1.1.20 netmask 255.255.255.0

! Configure NAT for research data only
Router(config)# ip nat inside source list 120 pool RESEARCH_EXTERNAL overload

! Enable interfaces
Router(config)# interface g0/0
Router(config-if)# ip nat outside
Router(config-if)# exit

Router(config)# interface g0/1.1
Router(config-if)# ip nat inside
Router(config-if)# description CLINICAL_VLAN_10
Router(config-if)# exit

Router(config)# interface g0/1.2
Router(config-if)# ip nat inside
Router(config-if)# description RESEARCH_VLAN_20
Router(config-if)# exit

Router(config)# end
Router# write memory
```

### 4.3 DLP (Data Loss Prevention) Appliance Configuration

```cisco
! Configure DLP to inspect traffic and detect PII patterns
! (This would typically run on a dedicated DLP appliance)

DLP-Appliance# configure
! Detect patient identification patterns (SSN, medical record number, etc.)
DLP-Appliance# content-filter rule DETECT_SSN
 regex-pattern "^\d{3}-\d{2}-\d{4}$"  ! Social security number
 action "BLOCK_AND_LOG"
 notify "Alert: SSN detected in unencrypted traffic"

DLP-Appliance# content-filter rule DETECT_MEDICAL_RECORD_NUMBER
 regex-pattern "^MRN[\d]{6,8}$"  ! Medical record number format
 action "BLOCK_AND_LOG"

DLP-Appliance# content-filter rule DETECT_PATIENT_NAME_DOB
 regex-pattern "^(Dr\.|Mr\.|Ms\.|Mrs\.)[\w\s]+\d{4}-\d{2}-\d{2}$"  ! Name + DOB pattern
 action "BLOCK_AND_LOG"

DLP-Appliance# apply content-filter-rules to VLAN 10  ! Clinical data
DLP-Appliance# save
```

### 4.4 Encryption Enforcement

```cisco
! Router inspection to ensure healthcare data is encrypted
Router# configure terminal

! Create inspection rule that only allows encrypted protocols from clinical network
Router(config)# class-map CLINICAL_TRAFFIC
 match access-group 1  ! Clinical VLAN 10
 
Router(config)# policy-map CLINICAL_ENCRYPTION
 class CLINICAL_TRAFFIC
  inspect https  ! Allow HTTPS only
  inspect ssh    ! Allow SSH only
  inspect tls    ! Allow TLS-encrypted protocols
  
! Drop any unencrypted clinical traffic
Router(config)# policy-map CLINICAL_ENCRYPTION
 class CLINICAL_TRAFFIC
  drop           ! Deny unencrypted traffic

Router(config)# service-policy input CLINICAL_ENCRYPTION interface g0/1.1

Router(config)# end
Router# write memory
```

## 5. Field-Specific Verification Steps

### 5.1 Verify VLAN Segregation

```cisco
Router# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- --...
1    default                          active    Gi0/1
10   CLINICAL_PHI                     active    Gi0/1.1
20   RESEARCH_DEIDENTIFIED            active    Gi0/1.2
99   ADMIN_STAFF                      active    Gi0/1.99
```

### 5.2 Verify NAT Rules Block Clinical Data

```cisco
! From clinical client (10.0.1.10), attempt HTTP (unencrypted)
Care-Provider-1> telnet 200.1.1.1 80
% Connection attempt failed  ! GOOD: Unencrypted traffic blocked

! Verify via router logs
Router# show access-list | include CLINICAL_PHI
Extended IP access list 110
 deny ip 10.0.1.0 0.0.0.255 any (5 matches)  ! Blocked 5 attempts
```

### 5.3 Verify Research Data Allowed (HTTPS Only)

```cisco
! From research client (10.0.2.20), test HTTPS connectivity
Research-Server> curl https://200.1.1.1
Success! Connected to external HTTPS server

! Verify NAT translation for research traffic
Router# show ip nat translations | grep 10.0.2
tcp 10.0.2.20:47321     200.1.1.10:443      200.1.1.10:443  10.0.2.20:47321
! NAT translation created for research data
```

### 5.4 Verify DLP Blocks Unencrypted PII

```cisco
! Simulate a rogue application attempting to send PHI unencrypted
Care-Provider-1# echo "Patient: John Doe, SSN: 123-45-6789" | nc 200.1.1.1 9999

! DLP appliance detects and blocks
DLP# show logs | grep DETECT_SSN
Alert: SSN detected in unencrypted traffic from 10.0.1.10
Action: BLOCKED and LOGGED
Timestamp: 2026-04-11T14:30:45Z

Router# show access-list 110 | include "deny"
deny ip 10.0.1.0 0.0.0.255 any (12 matches)  ! Increased from 5
```

### 5.5 Verify Encryption is End-to-End

```cisco
! Inspect traffic with packet sniffer to confirm all clinical data is encrypted
Router# debug ip packet detail
! (In production, use packet sniffer like tcpdump)

! Expected output: All packets from 10.0.1.0/24 show TLS/HTTPS headers only; no plaintext healthcare data
```

## 6. Expected Output Gallery

```
=== VLAN SEGREGATION ===
Router# show vlan id 10
VLAN Name                             Status    Ports
---- -------------------------------- --------- --...
10   CLINICAL_PHI                     active    Gi0/1.1

Router# show vlan id 20
VLAN Name                             Status    Ports
---- -------------------------------- --------- --...
20   RESEARCH_DEIDENTIFIED            active    Gi0/1.2

=== NAT RULES IN EFFECT ===
Router# show access-list
Extended IP access list 110 (CLINICAL - DENY UNENCRYPTED)
 deny ip 10.0.1.0 0.0.0.255 any (12 matches)

Extended IP access list 120 (RESEARCH - ALLOW ENCRYPTED)
 permit tcp 10.0.2.0 0.0.0.255 any eq 443
 permit tcp 10.0.2.0 0.0.0.255 any eq 22
 deny ip 10.0.2.0 0.0.0.255 any log

=== DLP ALERT LOG ===
Alert: SSN detected in unencrypted traffic from 10.0.1.10
Action: BLOCKED and LOGGED
Timestamp: 2026-04-11T14:30:45Z
Pattern: 123-45-6789 (SSN Format)

=== NAT TRANSLATION (Research Only) ===
Router# show ip nat translations
Proto Inside            Outside           Inside           Outside
tcp   10.0.2.20:47321   200.1.1.10:443   200.1.1.10:443  10.0.2.20:47321
! Note: NO translations from clinical VLAN 10; traffic is blocked before NAT
```

## 7. Common Field-Specific Mistakes

### Mistake 1: Allowing Unencrypted Clinical Data Traversal
**Problem:** Healthcare data leaves encrypted zone, violating HIPAA
```cisco
! WRONG: No encryption enforcement
Router(config)# ip nat inside source list 1 pool EXTERNAL overload
! (This allows any traffic from 10.0.1.0/24, including plaintext)
```
**Fix:** Enforce encryption before NAT
```cisco
! Inspect all traffic and only NAT encrypted connections
Router(config)# policy-map CLINICAL_ENCRYPTION
 class CLINICAL_TRAFFIC
  inspect https
  inspect ssh
  drop  ! Drop unencrypted
```

### Mistake 2: Not Detecting PII Patterns
**Problem:** Rogue application exfiltrates patient data; DLP doesn't detect it
```
App# send "SSN: 123-45-6789" to external server
! No DLP rules; data leaks
```
**Fix:** Implement comprehensive DLP rules
```
DLP# content-filter rule DETECT_SSN
 regex-pattern "^\d{3}-\d{2}-\d{4}$"
 action "BLOCK_AND_LOG"
```

### Mistake 3: Mixing Clinical and Research VLANs
**Problem:** Researcher accidentally queries patient database
```cisco
! WRONG: Same NAT pool for both
Router(config)# ip nat inside source list 1 pool SHARED_POOL overload
! (Clinical and research both use same external IPs; no segregation)
```
**Fix:** Separate NAT pools and ACLs
```cisco
Router(config)# ip nat inside source list 110 pool RESEARCH_ONLY overload
! Only 10.0.2.0/24 (research) can traverse NAT
```

### Mistake 4: Not Logging Access to Patient Data
**Problem:** Auditors cannot verify HIPAA compliance
```cisco
! WRONG: No logging configured
Router# show access-list 110 | grep log
! (No log keyword; access is hidden)
```
**Fix:** Log all denied access
```cisco
Router(config)# access-list 110 deny ip 10.0.1.0 0.0.0.255 any log  ! Add 'log'
```

## 8. Troubleshooting by Field

### Symptom: Research Server Cannot Access HTTPS Endpoint

**Diagnostic:**
```cisco
Research-Server> curl https://200.1.1.1 -v
* Attempting connection...
* Connection refused
```

**Root Cause:** NAT rule allows HTTPS but firewall may be blocking port 443

**Solution:**
```cisco
! 1. Verify NAT rule is configured
Router# show access-list 120 | grep 443
permit tcp 10.0.2.0 0.0.0.255 any eq 443  ! Present

! 2. Verify interface is configured
Router# show run | grep nat
ip nat inside source list 120 pool RESEARCH_EXTERNAL overload

! 3. Test connectivity from router
Router# ping 200.1.1.1
Reply from 200.1.1.1: bytes=32  ! Router can reach it

! 4. Check if firewall between NAT and internet is blocking
! (If firewall shows traffic, but research server still can't connect,
!  firewall may be dropping port 443; update firewall rules)
```

### Symptom: DLP Alerts Showing False Positives (Blocking Legitimate Data)

**Diagnostic:**
```
DLP# show logs | grep ALERT
Alert: SSN detected in text "Reason: HR2345"
! (False positive: "HR2345" matches SSN pattern "\d{3}-\d{2}-\d{4}" partially)
```

**Solution:** Refine DLP regex patterns to reduce false positives
```
! Use more specific pattern that requires hyphens
DLP# content-filter rule DETECT_SSN
 regex-pattern "^\d{3}-\d{2}-\d{4}$"  ! Hyphens required
 action "BLOCK_AND_LOG"
```

### Symptom: Clinical Staff Cannot Access Internal Encrypted Services

**Diagnostic:**
```
Care-Provider-1> curl https://10.0.1.50  ! Internal patient DB
! Connection attempt failed
```

**Root Cause:** Internal-to-internal traffic is blocked by NAT rules designed for external traffic

**Solution:** Create separate ACL for internal encrypted traffic
```cisco
Router(config)# access-list 130 permit tcp 10.0.1.0 0.0.0.255 10.0.1.50 eq 443
Router(config)# access-list 130 permit tcp 10.0.1.0 0.0.0.255 10.0.1.51 eq 3306
! (Internal database connections don't need NAT; just firewall rules)
```

## 9. Design Analysis

### Why Healthcare Needs Special NAT Rules?

Standard NAT assumes all network traffic is equivalent and equally safe. Healthcare NAT must distinguish between:

1. **Clinical data (PHI):** Must stay encrypted end-to-end; never traverses public internet
2. **Research data (de-identified):** Can traverse NAT if encrypted
3. **Administrative data (Credentials):** Sensitive but not patient data; different rules

| NAT Approach | PHI Protection | Compliance | Audit Trail | Field 5 Fit |
|--------------|---|---|---|---|
| Standard NAT | None | Poor | Poor | Bad |
| VLAN-based NAT | Partial | Medium | Medium | Good |
| VLAN + DLP | Good | High | High | Excellent |
| Zero-Trust NAT (Field 6) | Perfect | Very High | Perfect | (Future) |

**Why VLAN + DLP wins for Field 5:** Separates data by sensitivity, enforces encryption, and detects PII patterns before exfiltration.

## 10. Real-World Parallel

Haiti P45 will include clinics in Port-au-Prince that access patient records remotely. This lab's healthcare NAT prevents:
- Accidental exfiltration of patient names, DOBs, or medical record numbers
- Unencrypted clinical data traversing public internet
- Research staff accidentally querying patient data

Compliance with HIPAA-equivalent regulations is required before rolling out to Haiti P45 clinics.

## 11. Stretch Goals

### 11.1 Implement AI-Based Anomaly Detection

```
DLP# machine-learning-rule DETECT_PII
 train-on: Known PHI patterns (SSN, MRN, patient names, DOBs)
 detect: Anomalous character sequences resembling PHI
 action: "BLOCK_AND_LOG" if confidence > 95%
```

### 11.2 Implement Differential Privacy for Research Data

Ensure that aggregated statistics don't leak individual-level information even after de-identification.

### 11.3 Implement Granular Role-Based Access

Different NAT rules for different staff roles:
- **Attending Physicians:** Full access to all patient records
- **Residents:** Access to assigned patients only
- **Researchers:** De-identified data only
- **Administrative Staff:** Billing data only

### 11.4 Test With Haiti P45 Healthcare Deployment

Deploy this lab with 100+ care providers, 1000+ patient records, and verify that DLP does not exceed 5ms latency per packet.

## 12. Self-Assessment (Field 5 Healthcare - BSL)

- **BSL-1:** Configure VLAN-based NAT; verify clinical and research VLANs are segregated
- **BSL-2:** Implement encryption enforcement; block all unencrypted clinical traffic
- **BSL-3:** Deploy DLP appliance; detect and block PII patterns (SSN, MRN, names)
- **BSL-4:** Configure audit logging; verify HIPAA compliance checklist is met
- **BSL-5:** Test with Haiti P45 healthcare load (100+ providers, 1000+ patient records); verify <5ms DLP latency
- **BSL-6:** Create healthcare NAT security audit report; identify compliance gaps
- **BSL-7:** Deploy to Haiti P45 clinic pilot site; achieve HIPAA-equivalent certification

---

**Lab Duration:** 140 minutes  
**Difficulty:** Advanced  
**Prerequisites:** CCNA Days 1-40 + Field 5 healthcare privacy preparatory labs

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
