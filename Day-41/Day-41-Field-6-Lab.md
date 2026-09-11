# Day 41: NAT/PAT for Autonomous Law (Field 6 - Governance & Appeals)

## 0. Metadata

- **Objective:** Master NAT/PAT with justification logging and appeal mechanisms for governance
- **Research Field:** Field 6: Autonomous Law (Governance Audit Trails, Immutability, Appeal Mechanisms)
- **Proof Obligations:** Every NAT translation decision is logged with justification; denied translations are appealable; governance vote required for policy changes
- **Haiti Deployment Phase:** P52+ (Governance scaling phase; all network decisions must be justifiable and appealable)
- **Relevant RFC/Standards:** RFC 3022 (NAT Overview), Governance Protocol (IETF draft)
- **Prerequisites:** Days 1-40 + Field 6 autonomous governance preparatory materials
- **Estimated Time:** 160 minutes
- **Difficulty:** Very Advanced
- **Hardware Required:** 2 routers (governance module), governance voting node, immutable ledger storage
- **Key Concepts:** Justification logging, appeal mechanisms, governance voting, policy immutability, autonomous verification

## 1. Business Context

Autonomous governance (Field 6) requires that all network decisions—including NAT translation policy—be transparent, justifiable, and appealable. Every NAT rule must answer: **"Why was this translation allowed? Can someone appeal?"**

In Field 6, decisions are not made by a single administrator but by a distributed governance system. This lab demonstrates:

1. **Justification:** Why each NAT translation was allowed
2. **Immutability:** Decisions are recorded permanently and cannot be retroactively changed
3. **Appeals:** Users can challenge NAT denials and request policy review
4. **Voting:** Policy changes require governance vote (e.g., 2/3 majority)

## 2. Topology Diagram (Modified for Autonomous Governance)

```
External Network                 Governance Network
                            [Governance Voting Nodes]
    [ISP Router]           (Quorum: 3/5 required for policy change)
         |                              |
         |                        [Immutable Ledger]
    [NAT Router R1]          (Records all decisions + votes)
    (Governance Module)             |
         |                     [Appeal Queue]
    [Appeal Handler]          (Reviews denied translations)
         |                              |
    [Switch SW1]              [Internal Clients]
         |                     (Can appeal NAT denials)
    [10.0.1.0/24]
```

**Key difference from base:** Every NAT decision is logged with justification, voters, and appeal status; policy changes require governance vote.

## 3. IP Addressing Plan

| Device | Interface | IP Address | Subnet Mask | Role | Notes |
|--------|-----------|-----------|------------|------|-------|
| NAT Router R1 | G0/0 | 200.1.1.2 | 255.255.255.0 | WAN/NAT Gateway | Governance module attached |
| NAT Router R1 | G0/1 | 10.0.1.1 | 255.255.255.0 | LAN Gateway | Subject to NAT governance |
| Governance Node 1 | NIC | 10.0.200.10 | 255.255.255.0 | Voting Member 1 | Quorum participant |
| Governance Node 2 | NIC | 10.0.200.11 | 255.255.255.0 | Voting Member 2 | Quorum participant |
| Governance Node 3 | NIC | 10.0.200.12 | 255.255.255.0 | Voting Member 3 | Quorum participant (tie-breaker) |
| Immutable Ledger | NIC | 10.0.200.50 | 255.255.255.0 | Decision Log Storage | Append-only; no deletion |
| Appeal Queue | NIC | 10.0.200.60 | 255.255.255.0 | Appeal Handler | Reviews rejected translations |
| PC1 (User) | NIC | 10.0.1.10 | 255.255.255.0 | Internal Client | Can appeal NAT denials |

## 4. Field-Specific Configuration

### 4.1 NAT Router with Governance Module

```cisco
Router> enable
Router# configure terminal

! Create NAT pool
Router(config)# ip nat pool EXTERNAL 200.1.1.3 200.1.1.254 netmask 255.255.255.0

! Create ACL for allowed translations
Router(config)# access-list 1 permit 10.0.1.0 0.0.0.255

! Configure NAT with governance logging
Router(config)# ip nat inside source list 1 pool EXTERNAL overload

! Enable NAT with decision logging
Router(config)# ip nat statistics logging

! Configure interfaces
Router(config)# interface g0/0
Router(config-if)# ip nat outside
Router(config-if)# exit

Router(config)# interface g0/1
Router(config-if)# ip nat inside
Router(config-if)# exit

! Enable governance event handler
Router(config)# event manager run GOVERNANCE_NAT_HANDLER

Router(config)# end
Router# write memory
```

### 4.2 NAT Decision Logging with Justification

```cisco
! Configure event manager to log NAT decisions with justification
Router# configure terminal

Router(config)# event manager applet LOG_NAT_DECISION
 event syslog occurs 1 pattern "%IP_NAT.*created\|%IP_NAT.*denied"
 
 action 1.0 syslog priority notice msg "NAT-GOVERNANCE-EVENT"
 action 2.0 cli command "show clock | include Time"  ! Timestamp
 action 3.0 cli command "show ip nat translations | tail 1"  ! Decision details
 action 4.0 cli command "show access-list 1 | include permit"  ! Justification (why allowed)
 action 5.0 cli command "syslog send-to 10.0.200.50 GOVERNANCE_LOG"  ! Send to ledger

! Justification: Rule ACL 1 created by: admin@governance.local on 2026-04-11
! Policy vote: 4/5 approved; voter1, voter2, voter3, voter4 voted YES; voter5 abstained
! Expiration: 2026-05-11 (30-day policy lifetime)

Router(config)# end
Router# write memory
```

### 4.3 Appeal Mechanism Configuration

```cisco
! Configure appeal queue for rejected NAT translations
Router# configure terminal

Router(config)# access-list 2 deny 10.0.1.20 0.0.0.0  ! PC that requested appeal
Router(config)# access-list 2 permit 10.0.1.0 0.0.0.255

! Reason for denial: "User 10.0.1.20 requested access to 200.1.1.99; not in approved pool"
! Appeal Mechanism:
! 1. User submits appeal to appeal@governance.local
! 2. Governance votes on appeal (3/5 majority required)
! 3. If approved, ACL is updated and policy vote recorded in ledger
! 4. Result is communicated back to user

! Configure appeal handler to listen for appeal requests
Router(config)# event manager applet PROCESS_APPEAL_REQUEST
 event syslog occurs 1 pattern "APPEAL_REQUEST"
 
 action 1.0 syslog priority info msg "Processing appeal from user"
 action 2.0 cli command "copy running-config tftp://10.0.200.60/current-policy.cfg"  ! Save current policy
 action 3.0 cli command "syslog send-to 10.0.200.50 APPEAL_LOGGED"  ! Log appeal
 ! Governance voting occurs out-of-band (via voting nodes)
 ! Policy update follows vote result

Router(config)# end
Router# write memory
```

### 4.4 Immutable Ledger Configuration

```cisco
! Configure immutable ledger on dedicated storage
Ledger-Server# configure

! All NAT decisions are appended and never deleted
Ledger# create-immutable-log /var/ledger/nat-decisions.log

! Each log entry format:
! {
!   "timestamp": "2026-04-11T14:30:00Z",
!   "event_type": "NAT_TRANSLATION_CREATED",
!   "inside_ip": "10.0.1.10",
!   "outside_ip": "200.1.1.3",
!   "port": "80",
!   "protocol": "tcp",
!   "justification": "Rule ACL-1 approved by vote 4/5",
!   "voters": ["voter1", "voter2", "voter3", "voter4"],
!   "policy_expiration": "2026-05-11",
!   "hash": "sha256:abc123def456..."
! }

Ledger# enable-append-only /var/ledger/nat-decisions.log
Ledger# enable-integrity-checking /var/ledger/nat-decisions.log  ! SHA-256 hashing
```

## 5. Field-Specific Verification Steps

### 5.1 Verify NAT Decision Logging with Justification

```cisco
! Query immutable ledger for NAT decisions
Auditor# curl https://ledger.governance.local/nat-decisions?date=2026-04-11

{
  "decisions": [
    {
      "timestamp": "2026-04-11T14:22:00Z",
      "event": "NAT_CREATED",
      "inside": "10.0.1.10:80",
      "outside": "200.1.1.3:80",
      "justification": "ACL-1 vote 4/5 approved",
      "voters": ["voter1", "voter2", "voter3", "voter4"],
      "hash": "sha256:abc123def456...",
      "appeal_status": "none"
    },
    {
      "timestamp": "2026-04-11T14:23:00Z",
      "event": "NAT_DENIED",
      "inside": "10.0.1.20:443",
      "outside": "N/A",
      "denial_reason": "Request denied; user not in approved ACL",
      "appeal_available": true,
      "appeal_deadline": "2026-04-18T14:23:00Z",
      "hash": "sha256:def456ghi789..."
    }
  ]
}
```

### 5.2 Verify Appeal Mechanism

```cisco
! User 10.0.1.20 attempts to appeal NAT denial
User# curl -X POST https://appeal.governance.local/submit-appeal \
  -d '{"user": "10.0.1.20", "destination": "200.1.1.99", "reason": "Need external access for work"}'

Response:
{
  "appeal_id": "APPEAL-2026-04-11-001",
  "status": "SUBMITTED",
  "next_vote": "2026-04-12T09:00:00Z",
  "voters": ["voter1", "voter2", "voter3"],
  "decision_deadline": "2026-04-13T17:00:00Z"
}
```

### 5.3 Verify Governance Vote on Policy Change

```cisco
! Governance nodes vote on proposed NAT policy change
Voter1# curl -X POST https://governance.local/vote \
  -d '{"policy_id": "NAT-POOL-EXPAND", "vote": "YES"}'

Voter2# curl -X POST https://governance.local/vote \
  -d '{"policy_id": "NAT-POOL-EXPAND", "vote": "YES"}'

Voter3# curl -X POST https://governance.local/vote \
  -d '{"policy_id": "NAT-POOL-EXPAND", "vote": "YES"}'

Voter4# curl -X POST https://governance.local/vote \
  -d '{"policy_id": "NAT-POOL-EXPAND", "vote": "NO"}'

Voter5# curl -X POST https://governance.local/vote \
  -d '{"policy_id": "NAT-POOL-EXPAND", "vote": "ABSTAIN"}'

! Vote Result: 3/3 YES (excluding abstentions), PASSES (3/5 quorum met)
! Policy is applied and logged with vote data
```

### 5.4 Verify Immutable Ledger Cannot Be Tampered

```cisco
! Auditor attempts to modify a historical log entry
Attacker# curl -X PUT https://ledger.governance.local/nat-decisions/1 \
  -d '{"outside_ip": "200.1.1.99"}'  ! Try to change historical translation

Response: 403 FORBIDDEN
{
  "error": "Immutable ledger does not allow modifications to historical entries",
  "attempted_modification": "2026-04-11T14:22:00Z entry",
  "alert": "Tampering attempt logged and reported to governance nodes"
}

! Ledger integrity check
Auditor# curl https://ledger.governance.local/integrity-check

{
  "status": "OK",
  "total_entries": 1247,
  "integrity_verified": true,
  "hash_chain_valid": true,
  "last_verified": "2026-04-11T15:00:00Z"
}
```

### 5.5 Verify Policy Expiration and Renewal

```cisco
! Query current policy status
Auditor# curl https://governance.local/current-nat-policy

{
  "policy_id": "NAT-POOL-ACL-1",
  "created": "2026-03-11T10:00:00Z",
  "expires": "2026-04-11T10:00:00Z",  ! Expires TODAY
  "status": "EXPIRING",
  "voters": ["voter1", "voter2", "voter3", "voter4"],
  "action_required": "Renewal vote required within 7 days"
}

! After renewal vote:
{
  "policy_id": "NAT-POOL-ACL-1-RENEWED",
  "created": "2026-04-11T11:00:00Z",
  "expires": "2026-05-11T11:00:00Z",  ! New 30-day term
  "status": "ACTIVE",
  "voters": ["voter1", "voter2", "voter3", "voter4"],
  "changes_from_prior": "none"  ! Same policy, but re-approved by governance
}
```

## 6. Expected Output Gallery

```
=== IMMUTABLE LEDGER QUERY ===
$ curl https://ledger.governance.local/nat-decisions?date=2026-04-11 | jq '.'
{
  "decisions": [
    {
      "timestamp": "2026-04-11T14:22:00Z",
      "event": "NAT_CREATED",
      "inside": "10.0.1.10:80",
      "outside": "200.1.1.3:80",
      "justification": "ACL-1 vote 4/5 approved",
      "voters": ["voter1", "voter2", "voter3", "voter4"],
      "hash": "sha256:abc123def456..."
    }
  ]
}

=== APPEAL STATUS ===
$ curl https://appeal.governance.local/status/APPEAL-2026-04-11-001
{
  "appeal_id": "APPEAL-2026-04-11-001",
  "status": "VOTED",
  "votes": {
    "YES": 2,
    "NO": 1
  },
  "result": "DENIED (2/3 < 3/5 majority)",
  "appeal_deadline": "2026-04-18T17:00:00Z",
  "can_re_appeal": true
}

=== POLICY VOTE TALLY ===
$ curl https://governance.local/vote-results/NAT-POOL-EXPAND
{
  "policy_id": "NAT-POOL-EXPAND",
  "status": "PASSED",
  "votes": {
    "YES": 3,
    "NO": 1,
    "ABSTAIN": 1
  },
  "quorum_required": "3/5",
  "quorum_met": true,
  "decision": "POLICY UPDATE APPROVED",
  "timestamp": "2026-04-11T15:30:00Z",
  "policy_effective": "2026-04-12T00:00:00Z"
}

=== IMMUTABLE LEDGER INTEGRITY ===
$ curl https://ledger.governance.local/integrity-check
{
  "status": "OK",
  "total_entries": 1247,
  "integrity_verified": true,
  "hash_chain_valid": true,
  "tampering_detected": false,
  "last_verified": "2026-04-11T15:00:00Z"
}
```

## 7. Common Field-Specific Mistakes

### Mistake 1: Not Logging Justification for Each Decision
**Problem:** Auditors cannot verify why decisions were made
```cisco
! WRONG: No justification logging
Router(config)# ip nat inside source list 1 pool EXTERNAL overload
! (No record of "why" this NAT rule was approved)
```
**Fix:** Log justification with each decision
```cisco
! Include voter list and vote count in log
! "NAT-POOL-ACL-1 approved by vote 4/5: voter1, voter2, voter3, voter4"
```

### Mistake 2: Allowing Policy Changes Without Governance Vote
**Problem:** Admin unilaterally changes NAT rules; bypasses governance
```cisco
! WRONG: No vote required
Router# configure terminal
Router(config)# access-list 1 permit 10.0.1.25  ! Add new user to NAT ACL
! (No governance vote; no audit trail)
```
**Fix:** Require vote before policy changes
```
Policy Change Request: Add 10.0.1.25 to NAT ACL
Governance Vote Initiated (quorum: 3/5)
Voters: voter1 (YES), voter2 (NO), voter3 (YES), voter4 (YES), voter5 (ABSTAIN)
Result: PASSED (3/3 quorum met)
Policy Applied: 2026-04-11T16:00:00Z
```

### Mistake 3: Not Implementing Appeal Mechanism
**Problem:** Users cannot contest NAT denials; no recourse
```
User attempts to appeal: "I was denied NAT access, but I need external connectivity"
Response: "No appeal mechanism; decision is final"
! User has no recourse; Field 6 principle violated
```
**Fix:** Implement appeal queue
```
Appeal Submitted: User 10.0.1.20 appeals NAT denial
Governance Vote: 2026-04-12T09:00:00Z
Decision: Appeal GRANTED by 3/5 vote
New Policy: User 10.0.1.20 added to NAT ACL (30-day trial)
```

### Mistake 4: Storing Policy in Mutable Database
**Problem:** Attacker modifies historical decisions; auditors cannot verify
```
Attacker# UPDATE nat_decisions SET voters='attacker' WHERE date='2026-04-11'
! Historical vote record modified; audit trail corrupted
```
**Fix:** Use append-only immutable ledger
```
Ledger: /var/ledger/nat-decisions.log (append-only, no deletions)
Integrity: SHA-256 hash chain prevents modification
Auditor: Can verify all historical decisions are unchanged
```

## 8. Troubleshooting by Field

### Symptom: Appeal Vote Not Reflected in NAT Policy

**Diagnostic:**
```
$ curl https://appeal.governance.local/status/APPEAL-2026-04-11-001
"status": "VOTED",
"result": "GRANTED",
"policy_update_applied": false  ! PROBLEM: Vote passed but policy not applied
```

**Root Cause:** Policy update automation failed after vote passed

**Solution:**
```
! 1. Verify governance vote quorum was met
$ curl https://governance.local/appeal-vote/APPEAL-2026-04-11-001
"votes_for": 3, "votes_against": 1, "quorum_required": 3, "met": true

! 2. Manually apply policy if automation failed
Router# configure terminal
Router(config)# access-list 1 permit 10.0.1.20  ! Add appealee to NAT ACL
Router(config)# end
Router# write memory

! 3. Log manual policy application to ledger
$ curl -X POST https://ledger.governance.local/append-entry \
  -d '{"event": "POLICY_APPLIED_MANUAL", "reason": "automation_failed", ...}'
```

### Symptom: Immutable Ledger Reports Hash Mismatch

**Diagnostic:**
```
$ curl https://ledger.governance.local/integrity-check
"status": "FAILED",
"hash_chain_valid": false,
"tampering_detected": true,
"failed_entry": "2026-04-11T14:25:30Z"
```

**Root Cause:** Ledger entry was modified or corrupted

**Solution:**
```
! This is a critical security alert; investigate immediately
! 1. Isolate ledger from network
Ledger# sudo ifconfig down

! 2. Verify on backup copy
$ sha256sum /var/ledger/nat-decisions.log.backup
! Compare hash with reported value

! 3. Determine if modification was authorized governance vote or tampering
$ grep "2026-04-11T14:25:30" /var/ledger/nat-decisions.log.history
! Look for corresponding governance vote record

! 4. If tampering: Alert security team; preserve forensic evidence
```

## 9. Design Analysis

### Why Governance Voting for NAT?

Traditional network administration: Admin makes decisions → Changes applied immediately

Field 6 principle: **Decisions must be justifiable and appealable**

For NAT specifically:
- Each translation allows a user to access external resources
- In autonomous systems, this is a privilege that can be appealed
- Policy changes affect all users; should require democratic vote

| Decision Approach | Appeal Available | Justification Logged | Voter Transparency | Field 6 Fit |
|------------------|---|---|---|---|
| Single admin | No | No | No | Poor |
| Single admin + logging | No | Yes | No | Medium |
| Governance vote + logging | Yes | Yes | Yes | Excellent |
| Autonomous (AI-based) | Partially | Yes | No | (Experimental) |

**Why governance voting wins:** It combines transparency (justification logging) with democratization (voting) and recourse (appeals).

## 10. Real-World Parallel

Haiti P52+ will include elected governance councils that approve major infrastructure changes. This lab's appeal mechanism parallels:

- **Clinic director** receives NAT denial for emergency external access
- **Files appeal:** "I need to access WHO emergency database"
- **Governance council votes:** 7/11 approve; policy updated to allow clinic director's access
- **Decision logged:** Immutable record of who voted, when, and why
- **Precedent set:** Future clinic directors can reference this decision

This ensures network access decisions are not arbitrary but are reviewable by community.

## 11. Stretch Goals

### 11.1 Implement Ranked-Choice Voting for Policy Disputes

Instead of simple Yes/No, allow voters to rank preferences (Approve, Conditional, Deny) and aggregate using Condorcet method.

### 11.2 Implement Time-Locked Policy Rollback

Policy changes that are controversial (e.g., 4/5 or 5/6 vote) can be automatically rolled back after 30 days if enough users appeal.

### 11.3 Create Historical Policy Analysis Dashboard

Track policy decisions over time; show which rules have been most appealed, which voters tend to approve/deny appeals, etc.

### 11.4 Test With Haiti P52+ Governance Load

Deploy with 500+ users, 20+ governance votes per day, 100+ appeals/month; verify system doesn't exceed 50ms decision latency.

## 12. Self-Assessment (Field 6 Autonomous Law - BSL)

- **BSL-1:** Configure NAT with governance voting; verify vote is required before policy changes
- **BSL-2:** Implement appeal mechanism; verify denied users can submit appeals and appeals are logged
- **BSL-3:** Deploy immutable ledger; verify historical decisions are tamper-evident
- **BSL-4:** Verify governance quorum enforcement (3/5 for major decisions, 2/3 for policy renewal)
- **BSL-5:** Test with Haiti P52 governance load (500+ users, 20+ votes/day); verify <50ms decision latency
- **BSL-6:** Create governance audit report; analyze appeal patterns and voter behavior
- **BSL-7:** Deploy to Haiti P52+ pilot site; achieve autonomous governance certification for network access

---

**Lab Duration:** 160 minutes  
**Difficulty:** Very Advanced  
**Prerequisites:** CCNA Days 1-40 + Field 6 autonomous governance preparatory labs

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
