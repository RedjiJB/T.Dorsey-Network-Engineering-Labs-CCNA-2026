# Research-Lab Standard: Field-Specific Lab Variant Template

## Overview

This document defines how to create field-specific lab variants for the CCNA curriculum. Each base lab (Day-NN-Lab-Manual.md) can be extended into multiple field-specific variants, each optimized for a particular research field's proof obligations.

## Why Separate Field-Specific Topologies?

Each research field has fundamentally different success criteria:

| Field | Focus | Topology Implication |
|-------|-------|----------------------|
| **1. Black Start** | Offline resilience, minimal dependencies | Remove external connectivity; add offline cache storage; test cold restart scenarios |
| **2. Geomagnetic** | Convergence under space-weather stress | Add jitter/packet loss injection; simulate latency spikes; verify recovery time |
| **3. DePIN** | Distributed consensus, no single hub | Change from centralized to full mesh; add Byzantine failure scenarios |
| **4. Security** | Attestation, cryptographic proofs | Add verification chains; test tampering detection; validate isolation |
| **5. Healthcare AI** | Privacy/fairness, PII protection | Separate sensitive data nodes; test anonymization; verify inference equity |
| **6. Autonomous Law** | Governance audit trails, immutability | Record all decisions; verify appeal mechanisms; test vote recording |
| **7. Haiti** | All of above + scale (50→1000+ nodes) | Combine previous fields; test cost models; validate real-world conditions |

A single topology optimized for Field 1 (offline) would be over-engineered for Field 3 (mesh efficiency). Separate topologies let each field be the protagonist of its own proof story.

---

## Base Lab vs. Field-Specific Lab

### Base Lab (Day-NN-Lab-Manual.md)
- **Audience:** CCNA students, general networking engineers
- **Scope:** Comprehensive, teaches the concept end-to-end
- **Coverage:** Touches all applicable fields lightly
- **Example:** Day-24 OSPF covers standard convergence, load-balancing, multi-area design
- **Use case:** General CCNA study, foundational knowledge

### Field-Specific Lab (Day-NN-Field-F-Lab.md)
- **Audience:** Researchers, field deployment engineers
- **Scope:** Deep dive into one field's proof obligations
- **Coverage:** One field, heavily optimized for that field's metrics
- **Example:** Day-24-Field-2-Lab.md tests OSPF convergence under simulated geomagnetic stress (±20% latency jitter, ±5% packet loss)
- **Use case:** Validating Haiti deployment phase, proving research claims

---

## Field-Specific Lab Template (12 Sections)

Each `Day-NN-Field-F-Lab.md` contains:

### 0. Metadata
```markdown
- **Objective:** [Field-specific proof claim]
- **Research Field:** Field-F: [Field Name]
- **Proof Obligations:** [What this lab proves for this field]
- **Haiti Deployment Phase:** [P38/P45/P52/P55+]
- **Relevant RFC/Standards:** [Same as base, plus field-specific]
- **Prerequisites:** Days 1-NN + [Field-specific prep]
- **Estimated Time:** [Usually longer than base due to stress testing]
- **Difficulty:** Advanced
- **Hardware Required:** [Modified from base to add stress injection]
- **Key Concepts:** [Field-specific adaptations]
```

### 1. Business Context
Same framing as base, but explicitly for this field.

Example (Day-24 Field-2):
```
Real-world OSPF deployment in geomagnetic-stress environments requires 
proving convergence time under simulated space-weather events. This lab 
validates that OSPF can re-converge in < 60 seconds even when links 
experience ±20% latency variation and ±5% packet loss.
```

### 2. Topology Diagram (MODIFIED)
Different from base topology to emphasize field-specific concerns.

**Example modifications per field:**

**Field 1 (Black Start):**
- Remove internet gateway
- Add offline cache/storage node
- Test: Can network reconstruct from stored state?

**Field 2 (Geomagnetic):**
- Same base topology, but add stress injection points
- WAN links get jittered/lossy simulators
- Test: Does convergence time meet SLA under stress?

**Field 3 (DePIN):**
- Change from hub-and-spoke to full mesh
- Remove centralized core switch
- Test: Can mesh reach consensus without central authority?

**Field 4 (Security):**
- Add attestation/verification servers
- Separate sensitive data path
- Test: Can all packets be traced/verified?

**Field 5 (Healthcare AI):**
- Tag nodes by data sensitivity (PII, health records, public)
- Add encryption/anonymization appliances
- Test: Does inference work without exposing raw data?

**Field 6 (Autonomous Law):**
- Add governance/voting nodes
- Create immutable decision log
- Test: Can actions be justified to governance layer?

**Field 7 (Haiti):**
- Combine all previous modifications
- Scale: 50 nodes (P38) → 200 (P45) → 1000+ (P52+)
- Test: Full stack works at production scale

### 3. IP Addressing Plan
Same methodology as base, but with field-specific annotations.

Example (Field-5 Healthcare):
```
VLAN 10 (Patient Data): 10.0.10.0/24 [Encrypted, PII]
VLAN 20 (Public Health): 10.0.20.0/24 [Anonymized, sharable]
VLAN 30 (AI Inference): 10.0.30.0/24 [Encrypted input/output only]
```

### 4. Field-Specific Configuration
Step-by-step commands, but optimized for this field's proof obligations.

Example (Field-2 Geomagnetic):
```
! OSPF configuration for geomagnetic stress testing
Router(config-router)# timers spf 100 150 150  ! Faster SPF for resilience
Router(config-router)# timers lsa-arrival 100  ! Tighter LSA pacing

! Simulate geomagnetic jitter on WAN link
interface Serial0/0
  delay 20000  ! Baseline 20ms
  bandwidth 1000  ! 1Mbps (reduce available for stress testing)
```

### 5. Field-Specific Verification Steps
Unique to this field's metrics (not just "ping works").

Example (Field-2):
```
! Verify convergence time under stress
! Step 1: Enable continuous ping
PC1# ping 10.0.30.1 -c 1000 > /tmp/ping.log &

! Step 2: Inject simulated geomagnetic stress
Router(config)# int Serial0/0
Router(config-if)# delay 24000  ! 20ms + 20% jitter = 24ms
Router(config-if)# exit

! Step 3: Measure time until pings resume
! Expected: < 60 seconds for convergence

! Step 4: Verify OSPF neighbors recovered
show ip ospf neighbor | include FULL
```

### 6. Expected Output Gallery
Realistic console output under field-specific stress.

### 7. Common Field-Specific Mistakes
What breaks when trying to optimize for this field.

Example (Field-1 Black Start):
```
MISTAKE: Leaving internet gateway enabled
  → Cache never tested, cold-start fails when connectivity lost
  
FIX: Disable internet connectivity before starting lab
  → Verify cache-only operation works
```

### 8. Troubleshooting by Field
Diagnostic steps specific to proof obligations.

Example (Field-3 DePIN):
```
If mesh consensus fails:
  1. Check byzantine node isolation (show ip route, is one node unreachable?)
  2. Verify voting quorum has majority (n/2 + 1 of m nodes)
  3. Test leader election: Disable primary node, verify backup elected
  4. Measure consensus time: Use timestamps in logs
```

### 9. Design Analysis
Why this topology's design choices matter for *this field*.

Example (Field-2 Geomagnetic):
```
Why add jitter instead of just reducing bandwidth?
- Geomagnetic events cause packet delay variation, not just loss
- A single reduced-bandwidth link doesn't replicate this
- Jitter stress-tests OSPF's SPF calculation speed
- Result: Proves resilience to actual space-weather profiles
```

### 10. Real-World Parallel
Haiti deployment precedent for this field-specific design.

Example (Field-1):
```
Haiti P38 pilot sites experience frequent power losses (avg. 6 hours/day).
This lab's offline-only mode simulates that reality. Operators rely on 
cached routing tables and don't expect dynamic updates until power restores.
```

### 11. Stretch Goals
Advanced proof obligations.

Example (Field-4 Security):
```
1. Formalize convergence proof in model checker (SPIN/TLA+)
2. Prove: "No packet leaves encrypted VLAN without attestation"
3. Test: Replay attack scenario (re-inject old captured packet)
4. Verify: Timestamp + signature prevents replay
```

### 12. Self-Assessment (Field-Specific BSL)
Field-specific mastery levels.

Example (Field-2):
```
- BSL-1: Configure OSPF and jitter injection; measure baseline convergence
- BSL-2: Tune OSPF timers for < 30s convergence under 20% jitter
- BSL-3: Prove convergence meets SLA; document actual vs. target times
- BSL-4: Propose OSPF variant optimized for geomagnetic events
- BSL-5: Validate proof with space-weather simulator or real DSCOVR data
- BSL-6: Submit convergence research for publication
- BSL-7: Deploy to Haiti P38 pilot; measure real-world convergence
```

---

## Lab-to-Field Mapping

| Days | Base Topic | Field 1 | Field 2 | Field 3 | Field 4 | Field 5 | Field 6 | Field 7 |
|------|-----------|--------|--------|--------|--------|--------|--------|--------|
| 1-10 | Fundamentals | ✓ | ✓ | | | | | ✓ |
| 11-14 | VLAN Basics | ✓ | | | ✓ | ✓ | | ✓ |
| 15-17 | VLAN Design | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| 18-22 | Spanning Tree | ✓ | ✓ | | ✓ | | | ✓ |
| 23-30 | OSPF/EIGRP | ✓ | ✓ | ✓ | | | ✓ | ✓ |
| 31-37 | IPv6/ACLs | | ✓ | | ✓ | ✓ | | ✓ |
| 38-47 | Services/Security | ✓ | | | ✓ | ✓ | ✓ | ✓ |
| 48-57 | Wireless | | | | ✓ | ✓ | | ✓ |
| 58 | Capstone | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Total field-specific labs:** ~108 variants across the 58 base labs

---

## When to Use Each Type

**Use Base Lab if:**
- Teaching CCNA fundamentals
- Preparing for 200-301 exam
- Learning protocol mechanics
- Don't have field-specific constraints

**Use Field-Specific Lab if:**
- Validating Haiti deployment phase
- Proving research claims
- Optimizing for specific constraints (offline, geomagnetic, mesh, etc.)
- Publishing research
- Training field operators

---

## Example: Complete Day-24 Progression

### Day-24-Lab-Manual.md (Base)
- OSPF fundamentals
- Multi-area design
- Cost calculation
- Load-balancing
- All fields touched lightly

### Day-24-Field-1-Lab.md (Black Start)
- OSPF in offline mode
- Cached routing tables
- No dynamic updates
- Cold-start validation

### Day-24-Field-2-Lab.md (Geomagnetic)
- OSPF with jitter injection
- Convergence under stress
- Meets SLA testing
- Space-weather resilience

### Day-24-Field-3-Lab.md (DePIN)
- OSPF in full-mesh topology
- Byzantine fault tolerance
- Distributed leader election
- Consensus validation

### Day-24-Research-Paper.md (Section 2.6)
- References all 3 field-specific variants
- Names which Haiti phase each proves
- Links to Harvard publications
- Validation gates before deployment

---

## File Organization

```
RedjiJB-Labs/
├─ Day-NN/
│  ├─ Day-NN-Lab-Manual.md           [Base — teaches CCNA]
│  ├─ Day-NN-Practice-Lab.md         [Base — hands-on exercises]
│  ├─ Day-NN-Field-1-Lab.md          [Black Start variant]
│  ├─ Day-NN-Field-2-Lab.md          [Geomagnetic variant]
│  ├─ Day-NN-Field-3-Lab.md          [DePIN variant]
│  ├─ Day-NN-Field-4-Lab.md          [Security variant]
│  ├─ Day-NN-Field-5-Lab.md          [Healthcare AI variant]
│  ├─ Day-NN-Field-6-Lab.md          [Autonomous Law variant]
│  ├─ Day-NN-Field-7-Lab.md          [Haiti combined variant]
│  └─ Day-NN-Research-Paper.md       [5-section + Field Linkage]
├─ RESEARCH-LAB-STANDARD.md          [This file]
├─ RESEARCH-PAPER-STANDARD.md        [Section 2.6 standard]
└─ RESEARCH-LABS-ROADMAP.md          [Master index + timeline]
```

---

## Next Steps

1. Create RESEARCH-PAPER-STANDARD.md (Section 2.6 specification)
2. Create field-specific lab variants (12 sequential agent batches, ~9 labs each)
3. Create research papers (6 sequential agent batches, ~8 papers each)
4. Create RESEARCH-LABS-ROADMAP.md master index
5. Commit and push all ~155 new files to GitHub

**Total new documentation:** ~158 files (108 field-specific labs + 47 research papers + 3 standards)
