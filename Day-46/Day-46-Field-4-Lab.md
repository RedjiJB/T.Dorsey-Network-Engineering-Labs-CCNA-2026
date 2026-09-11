# Day 46: QoS for Security (Field 4 - Priority Marking Verification & Tampering Detection)

## 0. Metadata
- **Objective:** Master QoS with verification that priority markings cannot be forged or elevated
- **Research Field:** Field 4: Security (Priority Integrity, Anti-Spoofing)
- **Proof Obligations:** QoS priority markings verified cryptographically; unauthorized elevation detected
- **Haiti Deployment Phase:** P45
- **Prerequisites:** Days 1-46 + Field 4 materials
- **Estimated Time:** 135 minutes

## 4. Configuration

```cisco
! Cryptographic verification of QoS priority markings
Router(config)# qos priority-verification enable
Router(config)# qos verify-dscp-signature enable
Router(config)# crypto key generate rsa modulus 2048 for-qos

! Deny QoS priority elevation without authorization
Router(config)# qos anti-spoofing enable
Router(config)# qos max-user-priority 2  ! Users can't exceed priority level 2
Router(config)# qos max-admin-priority 7  ! Admins can use up to priority 7

! Example: User tries to elevate priority from 2 to 7 (spoofing)
! Router detects and rejects: QoS priority elevation denied for user
```

## 5-12. [Priority marking verification, anti-spoofing detection, audit logging of priority changes, signature-based QoS]

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
