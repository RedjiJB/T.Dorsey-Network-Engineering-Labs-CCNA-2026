# Day 13: VLAN Routing & Inter-VLAN Communication (DePIN Field)

## 0. Metadata
- **Objective:** Implement ROAS in full-mesh topology (no centralized core switch); prove inter-VLAN routing without single point of failure
- **Research Field:** Field-3: DePIN (Distributed Consensus, No Central Hub)
- **Proof Obligations:** ROAS routes traffic between VLANs in full-mesh switch topology; no core aggregation required; Byzantine node isolation validated
- **Haiti Deployment Phase:** P45 (community mesh, 200+ nodes)
- **Relevant RFC/Standards:** IEEE 802.1Q, IETF mesh routing concepts
- **Prerequisites:** Days 1-12 + Field-3 prerequisites (mesh topology design, Byzantine fault tolerance)
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced (distributed systems)
- **Hardware Required:** 4-6 switches (full mesh), 1-2 routers, 6-8 PCs, no centralized switch
- **Key Concepts:** Mesh VLAN topology, distributed routing, Byzantine node testing, quorum validation

## 1. Business Context (Field-3: DePIN Mesh)
Field-3 optimizes for **distributed peer-to-peer networks** with no central authority. Haiti P45 envisions community-operated mesh networks (50-200 nodes) where each node participates equally in routing decisions.

**Real Scenario:** A rural Haiti community has 6 micro-finance branches. Each branch operates a switch and router. No single "core" switch—instead, all 6 switches interconnect in full mesh (15 trunk links). ROAS must route VLANs across mesh without relying on any single node.

**Field-3 Question:** What happens if one switch fails (Byzantine node)? Do other branches still reach each other's VLANs?

**Success Metric:** Network remains connected and all VLANs routable after any single node failure.

## 2. Topology Diagram (Full-Mesh DePIN)
```
        [PC1-A]  [PC2-B]  [PC3-C]
         V10      V10      V10
         |         |         |
    [SW-A]-----[SW-B]-----[SW-C]
    /|\   \  /  / |  \  / | /|\
   / | \___\/  _/  |   \/  |/ | \
  /  |     /\  \   |  /\   /  |  \
 /   |    /  \  \  | /  \ /   |   \
[SW-D]--[SW-E]--[SW-F]       |    |
 |  VLAN 20, 30, 40 mesh     |   /
 PC4-D  PC5-E  PC6-F        [Router]
 V20    V20    V20          (ROAS on
                             all 6)
 **Full Mesh: All switches connected**
 No hierarchy, all equal participants
```

**Field-3 Modifications:**
- 6 switches in full-mesh topology (every pair connected)
- No "core" switch (all equal)
- ROAS on all switches (VLAN routing distributed)
- Byzantine node test: Disable one switch, verify mesh heals

## 3. IP Addressing Plan (Distributed Mesh)
| Device | VLAN | IP Address | Mesh Node | Notes |
|--------|------|-----------|-----------|-------|
| PC1-A | 10 | 10.0.10.10 | Branch A | ROAS available from SW-A |
| PC2-B | 10 | 10.0.10.11 | Branch B | ROAS available from SW-B |
| PC3-C | 10 | 10.0.10.12 | Branch C | ROAS available from SW-C |
| PC4-D | 20 | 10.0.20.10 | Branch D | ROAS available from SW-D |
| PC5-E | 20 | 10.0.20.11 | Branch E | ROAS available from SW-E |
| PC6-F | 20 | 10.0.20.12 | Branch F | ROAS available from SW-F |

## 4. Field-3-Specific Configuration

### 4.1 Distributed ROAS Setup (No Central Router)
```
! Each switch runs local ROAS subinterfaces
! Configuration identical on all 6 switches (modulo management VLAN)

Switch-A> en
Switch-A# conf t

! Create VLANs (all branches need all VLANs)
Switch-A(config)# vlan 10
Switch-A(config-vlan)# name Field3_VLAN10
Switch-A(config-vlan)# exit

Switch-A(config)# vlan 20
Switch-A(config-vlan)# name Field3_VLAN20
Switch-A(config-vlan)# exit

Switch-A(config)# vlan 30
Switch-A(config-vlan)# name Field3_VLAN30
Switch-A(config-vlan)# exit

! ROAS Subinterfaces (Layer 3)
Switch-A(config)# int vlan 10
Switch-A(config-if)# ip address 10.0.10.1 255.255.255.0
Switch-A(config-if)# no shutdown
Switch-A(config-if)# exit

Switch-A(config)# int vlan 20
Switch-A(config-if)# ip address 10.0.20.1 255.255.255.0
Switch-A(config-if)# no shutdown
Switch-A(config-if)# exit

! Access port (local branch PCs connect here)
Switch-A(config)# int f0/1
Switch-A(config-if)# switchport mode access
Switch-A(config-if)# switchport access vlan 10
Switch-A(config-if)# no shutdown
Switch-A(config-if)# exit

! Trunk to all other switches (full mesh)
Switch-A(config)# int g0/1
Switch-A(config-if)# switchport mode trunk
Switch-A(config-if)# switchport trunk allowed vlan 1,10,20,30
Switch-A(config-if)# description Trunk_to_Switch-B
Switch-A(config-if)# no shutdown
Switch-A(config-if)# exit

! Repeat trunk configuration for g0/2 (to SW-C), g0/3 (to SW-D), etc.
! Goal: Each switch connects to every other switch (full mesh)

Switch-A(config)# end
Switch-A# write memory

! **Repeat for Switch-B, C, D, E, F (same config, mod IP addresses)**
! Switch-B vlan 10 gateway: 10.0.10.2 (different from Switch-A)
! This allows distributed gateway selection
```

### 4.2 Byzantine Node Test (Field-3 Critical)
```
! Simulate one branch node failure (Byzantine node)
! Procedure:
! 1. All 6 switches running ROAS (healthy mesh)
! 2. Disable Switch-D (simulate site outage)
! 3. Verify remaining 5 switches still route VLANs

! Before Byzantine Test:
PC1-A> ping 10.0.20.10 (PC4-D)  ← Works via mesh path
! Response time: ~15ms (path: A→B→C→D or similar)

! Inject Byzantine Node (Disable Switch-D):
Switch-D# shutdown  (or unplug power)

! After Byzantine Test:
PC1-A> ping 10.0.20.10 (PC4-D)  ← Should FAIL (expected—D offline)
PC1-A> ping 10.0.20.11 (PC5-E)  ← Should WORK via mesh (A→B→C→E or similar)

! Verify mesh healed (no core dependency):
Router# show ip route
! Expected: Routes via remaining 5 switches, no single-point dependency
```

## 5. Field-3-Specific Verification Steps

### 5.1 Mesh Connectivity Test (All Pairs)
```
! Verify every switch can route to every other VLAN via mesh
! Test matrix (6x6):
PC1-A (VLAN 10) pings:
  - PC2-B (10.0.10.11) via SW-B → Should work
  - PC4-D (10.0.20.10) via SW-D → Should work
  - PC6-F (10.0.20.12) via SW-F → Should work

! Expected: All 15 unique paths (6 choose 2) functional
! If any ping fails → Mesh has broken link
```

### 5.2 Byzantine Node Resilience (Field-3 Proof)
```
! Phase 1: Baseline (all 6 switches active)
PC1-A# ping 10.0.20.10 10.0.20.11 10.0.20.12
! Expected: 3/3 replies (can reach all 3 Branch D,E,F nodes)

! Phase 2: Disable Switch-D (Byzantine node)
! (Admin removes power from Branch D switch)

! Phase 3: Immediate test (should fail for D nodes)
PC1-A# ping 10.0.20.10  ← FAILS (D offline, expected)
PC1-A# ping 10.0.20.11  ← Should WORK via E (mesh routed around D)
PC1-A# ping 10.0.20.12  ← Should WORK via F (mesh routed around D)

! Field-3 Success: 2/3 nodes reachable after Byzantine failure
! Proves mesh doesn't rely on any single switch (no single point of failure)
```

### 5.3 Quorum Validation (Field-3 Governance)
```
! In distributed systems, quorum = ceil(n/2)+1
! With 6 switches: quorum = 4 (need 4+ active for decisions)

! Test: Disable 3 switches (lose quorum)
! Disable: Switch-D, Switch-E, Switch-F

! Verify remaining 3 switches (A, B, C) cannot route outside their group
Switch-A# ping 10.0.20.10 (Branch D)  ← Unreachable (quorum lost)

! Re-enable 2 switches (A, B, C, E = 4 active = quorum regained)
! Switch-F remains offline

! Verify routing resumes
Switch-A# ping 10.0.20.11 (Branch E)  ← Should work (quorum restored)
```

## 6. Expected Output Gallery (Mesh Connectivity)

### 6.1 Mesh Ping Success (Pre-Byzantine)
```
PC1-A> ping 10.0.20.12  (PC6-F via full mesh)
Reply from 10.0.20.12: bytes=32 time=12ms TTL=63
[Mesh routing successful; intermediate hops transparent to user]
```

### 6.2 Byzantine Resilience (Post-Node-Failure)
```
PC1-A> ping 10.0.20.11  (PC5-E, re-routed around dead node D)
Reply from 10.0.20.11: bytes=32 time=18ms TTL=63
[Higher latency expected (longer path around failed node)]
```

## 7. Common Field-3-Specific Mistakes

### 7.1 MISTAKE: Not Creating All VLANs on All Switches
```
! Error: Only Branch A has VLAN 10; other branches missing
! Field-3 Fix: Every switch needs all VLANs (even if no local PCs)
! Reason: Mesh routing requires global VLAN awareness
```

### 7.2 MISTAKE: Not Full Mesh (Star Topology Creeps In)
```
! Error: Added central "core" switch to simplify (defeats Field-3 goal)
! Field-3 Fix: Maintain true full mesh (every pair connected)
! Verify: 6 switches = 15 trunk links exactly
```

### 7.3 MISTAKE: Using Same IP Gateway on All Switches
```
! Error: Switch-A VLAN 10 gateway 10.0.10.1, Switch-B also 10.0.10.1
! Field-3 Fix: Use different IPs per switch (A=.1, B=.2, C=.3, ...)
! This allows distributed load-balancing
```

## 8. Troubleshooting by Field (Field-3: Mesh Routing)

### 8.1 Mesh Connectivity Fails (One Pair)
```
! Symptom: PC1-A cannot ping PC5-E (all other pairs work)

! Diagnostic: Check if trunk between A and E is broken
Switch-A# show int g0/1 | include (up|down)
! If down → Physical link broken or misconfigured

! Field-3 Fix:
! 1. Re-verify trunk configuration on both ends
! 2. Check VLAN allowed list includes all VLANs
! 3. Test alternative path: A→B→E or A→C→F→E
! 4. If all paths fail → Check spanning tree (may be blocking)
```

### 8.2 Byzantine Test Fails (Mesh Doesn't Heal)
```
! Symptom: After disabling one switch, all others lose connectivity

! Field-3 Fix: This indicates mesh is NOT truly distributed
! Check: Were all switches in full mesh or partial mesh?
! Expected: Disabling 1 of 6 should NOT isolate others
! If isolated → Mesh topology was hierarchical, not distributed
```

## 9. Design Analysis (Why for Field-3)

**Why Mesh ROAS for Haiti P45 DePIN?**

1. **Community Ownership (No Central Authority)**
   - Each branch operates independently
   - No single "head office" controls the network
   - Mesh topology reflects governance: all branches equal

2. **Resilience Without Core**
   - No single switch failure can isolate the network
   - Proves Field-3 deployment can work with low-end hardware
   - Each branch can run a basic switch (2960, not 6500)

3. **Scalability to Mesh**
   - ROAS is simple (Layer 3 on switches, not routers)
   - Avoids complex dynamic routing (OSPF too heavyweight for P45)
   - Proven to work in 4-6 node networks (basis for Haiti P45 expansion)

4. **Byzantine Fault Tolerance**
   - Test proves network survives node failures
   - Governance requirement: "Community mesh should heal from outages"
   - Field-3 provides empirical proof

## 10. Real-World Parallel (Haiti Deployment)

**Haiti P45 Community Mesh (6-8 Rural Branches, Q1-Q2 2027):**
- Each branch: Health clinic, School, Cooperative, Trading post
- All branches interconnected (no central hub)
- ROAS routes between departmental VLANs (Health, Education, Commerce)
- **Governance:** Branch committees vote on network rules (Byzantine voting simulation)

**Field-3 Validation:**
- Lab tests 6-node full mesh (matches P45 pilot size)
- Proves inter-VLAN routing works without core
- Confirms Byzantine node (equipment failure) doesn't break network
- **Gate:** If mesh heals from node failure 5/5 times → Approved for P45 deployment

**P45 Deployment Scenario:**
- Port-au-Prince launches with 6-8 community branches in mesh
- Each branch operates router/switch combo (2960L + 2911)
- If one branch loses power → Other 5-7 continue routing
- Proves community-owned network is resilient to real-world failures

## 11. Stretch Goals (Field-3 Advanced)

1. **Scale Mesh to 10+ Nodes**
   - Add 4 more switches (10 total)
   - Verify full mesh still functions (45 trunk links)
   - Measure convergence with increasing complexity

2. **Byzantine Voting Protocol**
   - Implement distributed voting on "network decisions"
   - Test: Can 6 nodes reach consensus on VLAN policy change?
   - Document quorum = 4 requirement

3. **Mesh Redundancy Paths**
   - Run continuous ping from each pair
   - Simulate link failure (not node failure)
   - Verify traffic re-routes around failed link in < 5 seconds

4. **Design P45 Mesh Expansion**
   - Start with 6 nodes
   - Add nodes 1-at-a-time
   - Prove mesh behavior remains predictable
   - Document max-nodes limit (complexity vs. reliability tradeoff)

## 12. Self-Assessment (Field-3 DePIN Levels)

- **BSL-1 (Mesh Setup):** Configure 6-node full mesh, all switches ROAS-enabled, all VLANs routable
- **BSL-2 (Mesh Validation):** Test all 15 pairs (6 choose 2), document connectivity
- **BSL-3 (Byzantine Resilience):** Disable 1 node, verify other 5 remain connected, document isolation
- **BSL-4 (Quorum Proof):** Test quorum threshold (4/6), verify routing resumes after quorum restored
- **BSL-5 (Haiti P45 Pre-Deployment):** Run 10 Byzantine tests, document success rate, train branch operators
- **BSL-6 (Operational Mesh):** Implement monitoring for mesh health, create alerts for node failures, design operator playbook
- **BSL-7 (Field Deployment Authority):** Deploy Haiti P45 6-8 node community mesh, validate Byzantine resilience in field, publish results, mentor P52 expansion

---

**End of Day-13 Field-3 Lab**
**Research Field:** DePIN (Distributed Consensus) | **Haiti Phase:** P45 (Community Mesh)
**Generated for:** CCNA VLAN & STP Research Program
