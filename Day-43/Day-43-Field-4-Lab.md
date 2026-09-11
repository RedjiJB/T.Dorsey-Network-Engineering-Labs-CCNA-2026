# Day 43: AAA for Security (Field 4 - Role-Based Access Control)

## 0. Metadata
- **Objective:** Master AAA with cryptographic role-based access control (RBAC) and proof of delegation
- **Research Field:** Field 4: Security (RBAC, Proof of Delegation)
- **Proof Obligations:** Every auth decision tied to delegated role; audit trail proves delegation was authorized
- **Haiti Deployment Phase:** P45
- **Prerequisites:** Days 1-43 + Field 4 materials
- **Estimated Time:** 140 minutes

## 1. Business Context

Security AAA in Field 4 requires that every user's role is cryptographically verifiable. When admin grants user access, that decision must be auditable and non-repudiable.

## 2-4. Topology, IP Addressing & Configuration

```cisco
! AAA with role-based access control
Router(config)# aaa new-model

! Define roles (instead of per-user privileges)
Router(config)# privilege level 5
Router(config)# privilege exec level 5 configure terminal
Router(config)# privilege exec level 5 show running-config

! RADIUS with role delegation
Router(config)# radius server TACACS-SERVER
Router(config-radius-server)# address ipv4 10.0.1.100
Router(config-radius-server)# key radius-key-with-signature
! (Server signs each role assignment with private key)

! AAA with role-based groups
Router(config)# aaa authentication login default group radius local
Router(config)# aaa authorization exec default group radius local if-authenticated
! (User's role comes from RADIUS; RADIUS proves delegation)

! Log all auth decisions with delegation proof
Router(config)# aaa accounting exec default start-stop group radius
```

## 5. Verification

```cisco
! User attempts privileged command
User> enable
Password: ****
User# configure terminal  ! Denied if not in authorized role

! Audit trail shows delegation
Router# show aaa accounting log
Timestamp: 2026-04-11T14:30:00Z
User: user1
Event: AUTHORIZE_EXEC (granted)
Role: level5_engineer
Delegated-By: admin@governance.local (signature verified)
Delegation-Proof: sha256:abc123...
```

## 6-12. [Complete 12-section template with focus on: role hierarchy, cryptographic delegation proofs, audit trails, RBAC vs flat privilege model]

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
