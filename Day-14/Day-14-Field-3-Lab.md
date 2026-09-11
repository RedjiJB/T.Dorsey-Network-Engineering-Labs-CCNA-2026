# Day 14: VLAN Troubleshooting & Advanced Trunking (DePIN Field)

## 0. Metadata
- **Objective:** Troubleshoot VLAN trunking in mesh topology; verify distributed spanning tree across full-mesh switches
- **Research Field:** Field-3: DePIN (Distributed Consensus)
- **Proof Obligations:** Mesh VLAN troubleshooting successful with any single node offline; STP converges without central core
- **Haiti Deployment Phase:** P45 (community mesh, 200 nodes)
- **Relevant RFC/Standards:** IEEE 802.1D, 802.1Q, Byzantine consensus
- **Prerequisites:** Days 1-13 + Field-3 prerequisites
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 6 switches (full mesh), 6 PCs, no central core
- **Key Concepts:** Mesh VLAN troubleshooting, distributed STP, Byzantine-resilient diagnostics

## 1. Business Context (Field-3: DePIN)
Field-3 proves VLAN troubleshooting works in **full-mesh topology with no central switch**. Scenario: Rural Haiti community with 6 branches interconnected in mesh. One branch reports "can't reach other VLANs." Troubleshoot must work without relying on any single core switch (distributed diagnosis).

**Success Metric:** Identify VLAN misconfiguration by inspecting any 2 of 6 mesh nodes (no single authority).

## 2. Topology Diagram (Full-Mesh VLAN Troubleshooting)
```
[SW-A]-----[SW-B]-----[SW-C]
 | \        / |  \    / |
 |  +------+  |   +--+  |
 | /        \ | /    \  |
[SW-D]-----[SW-E]-----[SW-F]
(All pairs connected)
```

## 3. IP Addressing Plan (Mesh Gateways)
| Device | VLAN | IP Address | Mesh Node | Notes |
|--------|------|-----------|-----------|-------|
| PC1-A | 10 | 10.0.10.10 | Branch A | ROAS on SW-A |
| PC2-B | 10 | 10.0.10.11 | Branch B | ROAS on SW-B |
| PC3-C | 10 | 10.0.10.12 | Branch C | ROAS on SW-C |
| PC4-D | 20 | 10.0.20.10 | Branch D | ROAS on SW-D |
| PC5-E | 20 | 10.0.20.11 | Branch E | ROAS on SW-E |
| PC6-F | 20 | 10.0.20.12 | Branch F | ROAS on SW-F |

## 4. Field-3-Specific Configuration

### 4.1 Introduce Distributed Misconfiguration
```
! Misconfiguration spread across mesh (simulates distributed problem)
! Branch C: VLAN 20 not allowed on trunk to SW-E
Switch-C(config-if)# switchport trunk allowed vlan 1,10  ! Missing 20

! But other SW-C trunks to SW-B, SW-F have VLAN 20
! This creates asymmetric reachability (Field-3 challenge)
```

### 4.2 Mesh Troubleshooting Without Central Authority
```
! Operator at Branch A (no central admin access)
! Problem: PC3-C cannot reach PC5-E (both VLAN 10 to 20)

! Step 1: Check SW-A perspective
Switch-A# show int status trunk
! All trunks up

! Step 2: Check SW-C perspective (remote console)
Switch-C# show int status trunk
! Notice: SW-C-to-E trunk missing VLAN 20!

! This is distributed diagnosis: multiple nodes needed for root cause
```

## 5. Field-3-Specific Verification Steps

### 5.1 Mesh Path Analysis (No Central Authority)
```
! Verify all 6 nodes can reach each other
! PC1-A ping matrix:
PC1-A> ping 10.0.10.11  (via SW-A→B direct)
PC1-A> ping 10.0.10.12  (via SW-A→C or A→B→C)

! Identify broken path:
PC1-A> ping 10.0.20.11  (PC5-E via B or D or F - all work)

! If PC3-C → PC5-E fails despite VLAN 10 connectivity
! → Indicates asymmetric VLAN allowed list
```

### 5.2 Distributed STP Convergence (Field-3 Proof)
```
! Verify STP converges in mesh without central root
Switch-A# show spanning-tree brief
! Should show root elected among 6 switches (distributed voting)

! Disable Switch-D (Byzantine node failure)
Switch-D# shutdown

! Verify other 5 switches re-converge without D
Switch-A# show spanning-tree brief
! Root bridge may change, but STP stabilizes quickly
! Expected: < 30 seconds to new convergence
```

## 6. Expected Output Gallery

### 6.1 Mesh Trunk Status (Distributed View)
```
Switch-C# show int status trunk
Port        Status       Vlan Trunking
Gi0/2       trunking     1,10    ← VLAN 20 missing (asymmetric!)
Gi0/3       trunking     1,10,20
Gi0/4       trunking     1,10,20
```

### 6.2 Mesh Reachability Matrix (Partial Failure)
```
PC1-A pings:
  PC2-B (VLAN 10):  SUCCESS (direct A→B)
  PC3-C (VLAN 10):  SUCCESS (direct A→C)
  PC5-E (VLAN 10→20): FAIL (via broken C→E trunk)
  PC6-F (VLAN 10→20): SUCCESS (via A→B→E→F alternate path)
```

## 7. Common Field-3-Specific Mistakes

### 7.1 MISTAKE: Assuming Central Root Cause
```
! Error: "Problem must be on core switch" (Field-3 has no core)
! Field-3 Fix: Distributed diagnosis - check multiple nodes
```

### 7.2 MISTAKE: Not Checking All Mesh Paths
```
! Error: Only checked direct path A→C, missed C→E misconfiguration
! Field-3 Fix: Verify all n(n-1)/2 paths work (6 nodes = 15 paths)
```

## 8. Troubleshooting by Field

### 8.1 Asymmetric Connectivity (Mesh-Specific)
```
! Symptom: PC1-A can ping PC2-B but B cannot ping A
! Field-3 Diagnostic: This indicates asymmetric VLAN allowed
! Fix: Verify both directions of each trunk have same VLAN list
```

## 9. Design Analysis (Why for Field-3)
Mesh troubleshooting requires **distributed thinking**—no single switch has full picture. This lab proves field operators can diagnose problems by inspecting multiple nodes (consensus-based diagnosis).

## 10. Real-World Parallel
**Haiti P45 Community Mesh:** Each branch has peer-level responsibility for network health. Troubleshooting requires collaboration (one branch checks its trunk, another verifies spanning tree). No central authority.

## 11. Stretch Goals
1. Diagnose issue using ONLY three switches (minimum distributed consensus)
2. Create mesh troubleshooting flowchart for field operators
3. Test with 2 simultaneous misconfigurations

## 12. Self-Assessment (Field-3 BSL)
- **BSL-1:** Identify trunk misconfiguration by checking one mesh node
- **BSL-2:** Identify asymmetric VLAN misconfiguration across mesh
- **BSL-3:** Verify all 15 mesh paths functional
- **BSL-4:** Troubleshoot while one node offline (Byzantine resilience)
- **BSL-5:** Deploy to Haiti P45 mesh, validate field operator diagnosis

---

**End of Day-14 Field-3 Lab**
**Research Field:** DePIN | **Haiti Phase:** P45
**Generated for:** CCNA VLAN & STP Research Program
