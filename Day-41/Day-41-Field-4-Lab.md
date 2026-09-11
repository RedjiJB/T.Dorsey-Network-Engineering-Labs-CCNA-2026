# Day 41: NAT/PAT for Security (Field 4 - Cryptographic Attestation)

## 0. Metadata

- **Objective:** Master NAT/PAT with immutable audit trail and cryptographic attestation of all translation events
- **Research Field:** Field 4: Security (Attestation, Cryptographic Proofs, Tampering Detection)
- **Proof Obligations:** Every NAT translation event must be logged with cryptographic signature; audit trail must be immutable; unauthorized modifications must be detectable
- **Haiti Deployment Phase:** P45 (Security audit phase; compliance requires proof that all network translations are accounted for)
- **Relevant RFC/Standards:** RFC 3022 (NAT Overview), RFC 2663 (IP NAT Terminology), RFC 3161 (Timestamping)
- **Prerequisites:** Days 1-40 + Field 4 security preparatory materials + cryptography fundamentals
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 2 routers (with syslog support + crypto modules), dedicated syslog server, cryptographic hash generator
- **Key Concepts:** Immutable audit trails, cryptographic signatures, tamper detection, real-time logging, security attestation

## 1. Business Context

In security-critical deployments (Field 4), NAT is not just a network function—it's a compliance requirement. Every packet translation must be logged, timestamped, signed, and stored in an immutable audit trail. Regulatory bodies (e.g., Haitian healthcare boards for Haiti deployment) require proof that:

1. **Every translation was logged** (nothing was hidden)
2. **Timestamps are accurate** (NTP-synchronized)
3. **Signatures are cryptographically valid** (SHA-256 or stronger)
4. **Logs cannot be tampered with** (signed by router's private key)

This lab demonstrates how to implement NAT with real-time cryptographic attestation, enabling auditors to verify that the translation table was never corrupted or manipulated.

## 2. Topology Diagram (Modified for Security Attestation)

```
External Network                 Secure Internal Network
    [ISP Router]                    [NAT Router R1]
    (200.1.1.1)                    (Crypto Module)
         |                                |
         |                          [Syslog Server]
         |                      (Stores signed logs)
    [NAT Router R1]         [Cryptographic Hash DB]
    (200.1.1.2 WAN)          (Tamper-detection enabled)
         |                                |
    [Switch SW1]                   [Security Auditor]
         |                         (Verifies signatures)
    [10.0.1.0/24]
         |
    [Internal Clients]
    (Subject to NAT audit)
```

**Key difference from base:** All NAT translations are cryptographically signed and logged in real-time; unauthorized modifications are detectable via signature verification.

## 3. IP Addressing Plan

| Device | Interface | IP Address | Subnet Mask | Purpose | Notes |
|--------|-----------|-----------|------------|---------|-------|
| NAT Router R1 | G0/0 | 200.1.1.2 | 255.255.255.0 | WAN (External) | Translates outbound traffic |
| NAT Router R1 | G0/1 | 10.0.1.1 | 255.255.255.0 | LAN (Internal) | Gateway for internal clients |
| Syslog Server | NIC | 10.0.1.100 | 255.255.255.0 | Log aggregation | Stores all signed NAT translation logs |
| PC1 | NIC | 10.0.1.10 | 255.255.255.0 | Internal client | Traffic subject to NAT |
| PC2 | NIC | 10.0.1.11 | 255.255.255.0 | Internal client | Traffic subject to NAT |

## 4. Field-Specific Configuration

### 4.1 NAT Router with Cryptographic Logging

```cisco
Router> enable
Router# configure terminal

! Enable syslog with reliable transport (TCP)
Router(config)# logging host 10.0.1.100 transport tcp port 514

! Set logging buffer to capture all NAT events
Router(config)# logging buffered 1000000
Router(config)# logging level local6 debug

! Enable NAT detailed logging
Router(config)# debug ip nat detailed

! Create ACL for NAT translation
Router(config)# access-list 1 permit 10.0.1.0 0.0.0.255

! Configure NAT with dynamic pool
Router(config)# ip nat pool EXTERNAL 200.1.1.3 200.1.1.254 netmask 255.255.255.0
Router(config)# ip nat inside source list 1 pool EXTERNAL overload

! Interface configuration
Router(config)# interface g0/0
Router(config-if)# ip nat outside
Router(config-if)# exit

Router(config)# interface g0/1
Router(config-if)# ip nat inside
Router(config-if)# exit

! Configure crypto module for signing logs
Router(config)# crypto key generate rsa modulus 2048
Router(config)# crypto key pubkey-chain rsa
Router(pubkey-chain)# addressed-key 200.1.1.2 255.255.255.255
Router(pubkey-chain-addr)# key-string
Router(pubkey-key-str)# ! Paste public key here (or auto-generate)
Router(pubkey-key-str)# quit

Router(config)# end
Router# write memory
```

### 4.2 Real-Time NAT Signature Generation (Syslog Event Handler)

```cisco
! Configure event manager to sign each NAT translation
Router# configure terminal

Router(config)# event manager applet SIGN_NAT_ENTRY
 event syslog occurs 1 pattern "%IP_NAT.*created\|%IP_NAT.*deleted\|%IP_NAT.*modified"
 action 1.0 syslog priority info msg "NAT-EVENT: Generating cryptographic signature"
 action 2.0 cli command "show ip nat translations | hash 256 >> flash:/nat-signatures.log"

Router(config)# end
Router# write memory
```

### 4.3 Immutable Log Storage Configuration

```cisco
! Configure syslog server to append-only mode (no deletion/modification)
! This must be done on the syslog server itself (e.g., rsyslog on Linux)

! On Syslog Server (10.0.1.100):
syslog# cat >> /etc/rsyslog.conf << 'EOF'
# Immutable NAT translation log (append-only, no overwrites)
:programname, isequal, "Router" /var/log/router/nat-translations.log
& ~

# Enable file access restrictions
$FileGroup wheel
$FileMode 0640
$Umask 0022
$PrivDropToUser syslog
EOF

# Restart syslog daemon
syslog# systemctl restart rsyslog

! Configure immutable flag on log file
syslog# chattr +a /var/log/router/nat-translations.log  ! Append-only, no deletion
syslog# chattr +c /var/log/router/nat-translations.log  ! Prevent compression
```

### 4.4 Signature Verification Database

```cisco
! Maintain SHA-256 hash of each logged NAT event for tamper detection
Router# show ip nat translations | while read line; do
  echo "$line" | sha256sum >> flash:/nat-hashes.db
done

! Verify database integrity
Router# sha256sum -c flash:/nat-hashes.db.sig
```

## 5. Field-Specific Verification Steps

### 5.1 Verify Syslog Server Receives Signed NAT Events

```cisco
! On Syslog Server (10.0.1.100):
syslog# tail -20 /var/log/router/nat-translations.log

2026-04-11T14:22:15.234Z Router[12345]: NAT-EVENT: 
  Proto=tcp Inside=10.0.1.10:47321 Outside=200.1.1.3:80
  Signature=sha256:a1b2c3d4...e5f6 Timestamp=2026-04-11T14:22:15Z

2026-04-11T14:22:16.456Z Router[12345]: NAT-EVENT: 
  Proto=tcp Inside=10.0.1.11:50001 Outside=200.1.1.4:443
  Signature=sha256:b2c3d4e5...f6g7 Timestamp=2026-04-11T14:22:16Z
```

### 5.2 Verify Cryptographic Signatures

```cisco
! Download and verify signatures on auditor's machine
auditor$ gpg --verify /var/log/router/nat-hashes.db.sig /var/log/router/nat-hashes.db
gpg: Signature made Mon 11 Apr 2026 14:22:15 UTC
gpg: Good signature from "NAT Router R1 <r1@example.com>"
```

### 5.3 Detect Tampered Log Entries

```cisco
! Simulate tampering (unauthorized modification)
syslog# sed -i 's/200.1.1.3/200.1.1.99/g' /var/log/router/nat-translations.log  ! TAMPERED

! Verify signatures detect tampering
auditor$ sha256sum -c flash:/nat-hashes.db
/var/log/router/nat-translations.log: FAILED
! 
! Output indicates entry #234 has mismatched hash; tampering detected
```

### 5.4 Query NAT Audit Trail by Date Range

```cisco
! Find all NAT events for specific time period
syslog# grep "2026-04-11T14:2[0-3]:" /var/log/router/nat-translations.log | wc -l
127  ! 127 unique NAT translation events logged in the 4-minute window

! Export for auditor review
syslog# grep "2026-04-11T14:2[0-3]:" /var/log/router/nat-translations.log > audit-2026-04-11.log
syslog# sha256sum audit-2026-04-11.log > audit-2026-04-11.log.sig
```

### 5.5 Verify No Unauthorized Access to NAT Table

```cisco
! Check router's access log for configuration changes
Router# show log | include "crypto\|signature\|nat pool"

%SYS-5-CONFIG_I: Configured from console by admin on vty0
! Only authorized admin should appear in logs
```

## 6. Expected Output Gallery

```
=== SYSLOG SERVER OUTPUT (Signed NAT Events) ===
2026-04-11T14:22:15.234Z NAT-EVENT: tcp 10.0.1.10:47321 -> 200.1.1.3:80 CREATED
  Signature: sha256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 Timestamp: 2026-04-11T14:22:15Z

2026-04-11T14:22:16.456Z NAT-EVENT: tcp 10.0.1.11:50001 -> 200.1.1.4:443 CREATED
  Signature: sha256:b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6t7 Timestamp: 2026-04-11T14:22:16Z

2026-04-11T14:25:32.789Z NAT-EVENT: tcp 10.0.1.10:47321 -> 200.1.1.3:80 DELETED
  Signature: sha256:d4e5f6g7h8i9j0k1l2m3n4o5p6t7u8v9 Timestamp: 2026-04-11T14:25:32Z

=== SIGNATURE VERIFICATION (No Tampering) ===
$ sha256sum -c nat-hashes.db
/var/log/router/nat-translations.log: OK
! All signatures match; no tampering detected

=== TAMPER DETECTION (Unauthorized Modification) ===
$ sha256sum -c nat-hashes.db
/var/log/router/nat-translations.log: FAILED
! Entry #234: hash mismatch detected
! Alert: Log entry modified after initial logging
```

## 7. Common Field-Specific Mistakes

### Mistake 1: Logging Without Cryptographic Signatures
**Problem:** Attacker modifies logs; auditor cannot detect tampering
```
syslog# echo "FAKE-ENTRY" >> /var/log/router/nat-translations.log  ! No signature to verify
```
**Fix:** Sign every log entry with router's private key
```
Router# event manager applet SIGN_NAT
 action 2.0 cli command "show ip nat translations | gpg --sign > /dev/syslog"
```

### Mistake 2: Syslog Server Allows Modification
**Problem:** Attacker (or rogue admin) modifies logs after logging
```
syslog# chmod 666 /var/log/router/nat-translations.log  ! WRONG: world-writable
syslog# sed -i 's/200.1.1.3/200.1.1.99/' /var/log/router/nat-translations.log  ! Easy tampering
```
**Fix:** Make log file append-only, remove write permission
```
syslog# chattr +a /var/log/router/nat-translations.log
syslog# chmod 640 /var/log/router/nat-translations.log  ! Only owner + group readable
```

### Mistake 3: Not Synchronizing Time (NTP)
**Problem:** Syslog timestamps drift; auditor cannot verify chronological order
```
Router# show clock
14:22:15.234  ! Router's clock is accurate
Syslog# date
Mon Apr 11 10:15:00 EDT 2026  ! Syslog server is 4 hours behind! WRONG
```
**Fix:** Configure NTP on both router and syslog server
```
Router(config)# ntp server 8.8.8.8
Syslog# ntpdate -s 8.8.8.8 && hwclock -w
```

### Mistake 4: Storing Private Key on Router Without Protection
**Problem:** Private key is readable by any administrator
```
Router# show crypto key rsa
Key ID: F09B6E1D46C9E21A
Modulus: [READABLE TO ANYONE WITH ADMIN ACCESS]
Private exponent: [ALSO READABLE!]
```
**Fix:** Protect private key with PIN/password
```
Router(config)# crypto key zeroize rsa  ! Delete old key
Router(config)# crypto key generate rsa modulus 2048 encryption  ! Requires passphrase
```

## 8. Troubleshooting by Field

### Symptom: Syslog Server Not Receiving NAT Events

**Diagnostic:**
```
Router# show logging
Syslog logging: disabled  ! PROBLEM
```

**Solution:**
```
Router# configure terminal
Router(config)# logging host 10.0.1.100 transport tcp port 514
Router(config)# end
Router# write memory

! Verify connectivity
Router# ping 10.0.1.100
Reply from 10.0.1.100: bytes=32 time=2ms
```

### Symptom: Signature Verification Fails on All Entries

**Diagnostic:**
```
$ sha256sum -c nat-hashes.db
/var/log/router/nat-translations.log: FAILED
! ALL entries failed
```

**Root Cause:** Syslog server's hash database is corrupted or not synchronized with router

**Solution:**
```
! 1. Verify both systems are on same NTP source
Router# show ntp associations

! 2. Re-generate hash database from scratch
Router# show ip nat translations | sha256sum > flash:/nat-hashes-new.db

! 3. Transfer to syslog server
Router# copy flash:/nat-hashes-new.db tftp://10.0.1.100/nat-hashes-new.db

! 4. Verify
$ sha256sum -c nat-hashes-new.db
```

### Symptom: Private Key Passphrase Lost; Cannot Verify Signatures

**Diagnostic:**
```
$ gpg --verify nat-signatures.log.sig
gpg: WARNING: unable to decrypt using passphrase
! Cannot verify signatures without passphrase
```

**Solution:** This is a security feature; without the passphrase, no one can forge signatures. Maintain passphrase in secure location (e.g., hardware security module, not text file).

If passphrase is truly lost:
```
Router# crypto key zeroize rsa
Router# crypto key generate rsa modulus 2048 encryption
! Generate new keypair with new passphrase
! Old logs remain signed and verifiable, but cannot create new signatures
```

## 9. Design Analysis

### Why Cryptographic Signatures for NAT?

In security-critical deployments, **trust is not assumed; it's verified**. Standard syslog logging can be tampered with, corrupted, or manipulated. Cryptographic signatures solve this by:

1. **Authenticity:** Proves that router (not attacker) created the log entry
2. **Integrity:** Proves that no one modified the log entry after creation
3. **Non-repudiation:** Router cannot deny having logged the event

**Field 4 Design Principle:** Every security-critical event must be tamper-evident.

| Logging Approach | Tamper-Detection | Compliance Score | Cost | Field 4 Fit |
|------------------|------------------|------------------|------|------------|
| Plain syslog | None | Low | $0 | Poor |
| Syslog + append-only | Deletion-evident | Medium | $100 | Medium |
| Syslog + hash DB | Modification-evident | High | $500 | Good |
| Syslog + crypto sig | Full cryptographic attestation | Very High | $1000 | Excellent |

**Why crypto signatures win:** They provide absolute proof of tampering; auditors can verify logs without trusting router administrators.

### Timeout Design Rationale

All NAT translations are logged instantly, regardless of timeout. The timeout only affects when the translation is *garbage-collected* from the router's memory; the log entry remains permanently in the audit trail.

## 10. Real-World Parallel

Haiti's Autonomous Governance Phase (Field 6) will eventually require that all network translation decisions be appealable. Field 4 (Security) provides the foundation:

- **Every NAT event is logged with cryptographic proof**
- **Auditors can verify logs were never tampered with**
- **Non-repudiation: Router cannot deny having logged the event**

This enables Field 6 to build appeals processes on top of cryptographically-verified facts.

## 11. Stretch Goals

### 11.1 Implement Blockchain-Style Hashing for Multi-Entry Immutability

```
Entry N: sha256(Entry N-1 || Current Event) -> Hash N
Entry N+1: sha256(Entry N || Current Event) -> Hash N+1
! Modifying any historical entry breaks all subsequent hashes; tampering detected with 100% certainty
```

### 11.2 Create Real-Time Audit Dashboard

Build a web dashboard that displays:
- Live NAT translation events (updated in real-time from syslog)
- Signature verification status (green = valid, red = tampered)
- Timestamp accuracy (NTP sync status)
- Quarterly audit reports (export signed logs)

### 11.3 Implement Multi-Signature Requirements

Require that critical NAT policy changes (e.g., opening new port translation) are signed by both router AND a security officer before taking effect.

### 11.4 Test With Haiti P45+ Load (Security Audit Phase)

Deploy this lab with 500+ concurrent NAT translations and verify that signature generation + logging does not exceed 10ms additional latency per event.

## 12. Self-Assessment (Field 4 Security - BSL)

- **BSL-1:** Configure NAT + syslog logging; verify events are logged to external server
- **BSL-2:** Add cryptographic signatures to NAT log entries; verify signatures with gpg
- **BSL-3:** Make syslog server append-only; demonstrate that tampering is detected
- **BSL-4:** Implement automated signature verification; generate tamper-detection reports
- **BSL-5:** Test with Haiti P45 load (500 concurrent NAT events); verify <10ms logging latency
- **BSL-6:** Create audit trail analysis tool; publish security findings
- **BSL-7:** Deploy to Haiti P45 pilot site; achieve SOC 2 Type II compliance for NAT logging

---

**Lab Duration:** 150 minutes  
**Difficulty:** Advanced  
**Prerequisites:** CCNA Days 1-40 + Field 4 security preparatory labs + cryptography basics

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
