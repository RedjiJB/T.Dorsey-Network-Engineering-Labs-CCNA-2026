# Day 03: IPv4 Addressing & Subnetting (Field 3: DePIN)

## 0. Metadata

- **Objective:** Prove IPv4 Addressing & Subnetting functionality in DePIN (Field 3) constraints
- **Research Field:** Field 3: DePIN
- **Proof Obligations:**
  - Validate IPv4 Addressing & Subnetting works without external dependencies (Field 1) / under stress (Field 2) / in mesh topology (Field 3) / at Haiti scale (Field 7)
  - Document convergence time and resource usage
  - Prove resilience to field-specific failure modes
- **Haiti Deployment Phase:** P52 (1000-node network)
- **Relevant RFC/Standards:** IEEE 802.3 (Ethernet), RFC 791 (IPv4), RFC 1918 (Private Addresses)
- **Prerequisites:** Day 03 base lab manual + Field 3 environment setup
- **Estimated Time:** 150-180 minutes (includes stress testing)
- **Difficulty:** Advanced
- **Hardware Required:** 4-6 routers/switches, 6-8 PCs, stress injection appliance (Field 2) or mesh topology (Field 3)
- **Key Concepts:** Field-optimized IPv4 Addressing & Subnetting, DePIN-specific validation, proof obligations, real-world constraints

## 1. Business Context

DePIN (Decentralized Physical Infrastructure Networks) rely on **mesh topologies** without central authority.
This lab proves IPv4 Addressing & Subnetting works in **full-mesh, Byzantine-fault-tolerant** design:
- No central hub or single point of failure
- Nodes must reach consensus on IPv4 Addressing & Subnetting without a leader
- Byzantine nodes (malicious or failed) must not break the network
- Voting quorum (n/2 + 1) must validate all state changes

**Why this matters:** Decentralized networks cannot rely on centralized control. IPv4 Addressing & Subnetting must be fault-tolerant at the core.

## 2. Topology Diagram (Field 3: DePIN - Mesh)

```
        [R1]--------[R2]
        /|\         /|\
       / | \       / | \
      /  |  \     /  |  \
    [R3][R4][R5]---[R6][R7]
     \  |  /     \  |  /
      \ | /       \ | /
       \|/         \|/
        [R8]--------[R9]

Key: Full mesh topology - every node connected to every other.
No central hub. Nodes: R1-R9 (9 total, test up to 50 for scale).

Topology notes:
- Change from hub-and-spoke to full-mesh or partial-mesh
- Test IPv4 Addressing & Subnetting with Byzantine nodes (R4 offline or lying)
- Voting consensus: Need n/2 + 1 = 5 nodes to agree
- Success metric: Network continues without Byzantine node
```

**Modifications for Field 3:**
- Full mesh connectivity (or high-degree partial mesh)
- Add Byzantine failure simulation (1-3 nodes unreachable or malicious)
- Implement voting/consensus for IPv4 Addressing & Subnetting decisions
- Test that n/2 + 1 majority rule ensures correctness

## 3. IP Addressing Plan

| Device | Role | Subnet | Address | Mask | Notes |
|--------|------|--------|---------|------|-------|
| R1 | Primary | 10.0.03.0/24 | 10.0.03.1 | /24 | Field 3 core router |
| R2 | Secondary | 10.0.03.0/24 | 10.0.03.2 | /24 | Backup/mesh peer |
| SW1 | Access | 10.0.03.0/24 | 10.0.03.254 | /24 | Access switch VLAN |
| PC1 | Client | 10.0.03.0/24 | 10.0.03.10 | /24 | Test client 1 |
| PC2 | Client | 10.0.03.0/24 | 10.0.03.20 | /24 | Test client 2 |

**Field 3 specific notes:**
- Subnets chosen to test Day 03 concepts in isolation
- Avoid public IP ranges; use RFC 1918 private addresses throughout
- No external connectivity in Field 1 (black start)
- Stress injection may cause addresses to become unreachable temporarily (Field 2)
- Mesh topology (Field 3) requires all nodes reachable by some path

## 4. Pre-Config Checklist

- [ ] Console cable connected to all devices
- [ ] IOS/GNS3 image verified on routers and switches
- [ ] Physical cabling complete
- [ ] Management IP configured on switches
- [ ] Router power-on and initial config ready
- [ ] Full-mesh topology cabling complete (R1 to R9 all connected)
- [ ] Byzantine node(s) identified (which nodes to fail)
- [ ] Voting/quorum configuration ready (n/2 + 1 consensus)
- [ ] Backup routes for each node tested

## 5. Field-Specific Configuration

### 5.1 Common Configuration (All Fields)

```
! Standard initial configuration for Day 03: IPv4 Addressing & Subnetting
Router> en
Router# conf t

! Hostname
Router(config)# hostname R1

! Clock setting
Router(config)# clock rate 64000

! Line configuration
Router(config)# line con 0
Router(config-line)# logging synchronous
Router(config-line)# exit

Router(config)# line vty 0 4
Router(config-line)# password class
Router(config-line)# login
Router(config-line)# exit

! Save
Router(config)# end
Router# write memory
```

### 5.2 Field 3 Specific Configuration


```
! Field 3: DePIN - Configure full-mesh topology
! Each router connects to multiple peers

Router(config)# int g0/0
Router(config-if)# ip address 10.0.03.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

! Add connections to other mesh peers
Router(config)# int g0/1
Router(config-if)# ip address 10.0.03.11 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

Router(config)# int g0/2
Router(config-if)# ip address 10.0.03.21 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

! Implement voting/consensus (pseudo-code):
! if (consensus_check(IPv4 Addressing & Subnetting) >= n/2 + 1):
!     accept_update()
! else:
!     reject_update()

Router# write memory
```

## 6. Field-Specific Verification Steps

### 6.1 Basic Connectivity Test
```
Router# show ip int brief
Router# show ip route
Router# ping 10.0.03.10
```

### 6.2 Field 3 Specific Verification


### 6.2.3 Byzantine Fault Tolerance Verification (Field 3)
```
! Step 1: Verify full-mesh connectivity
Router# show ip route
C 10.0.03.0/24 is directly connected, GigabitEthernet0/0
C 10.0.03.11/24 is directly connected, GigabitEthernet0/1
C 10.0.03.21/24 is directly connected, GigabitEthernet0/2

! Step 2: Identify Byzantine node(s) (take R4 offline)
! R4# shutdown

! Step 3: Verify quorum still has majority (8 of 9 nodes = 88%)
! Check: n/2 + 1 = 5 nodes minimum needed
Router# show neighbors  ! (pseudo-output)
R1: connected
R2: connected
R3: connected
R4: [OFFLINE]
R5: connected
R6: connected
R7: connected
R8: connected
R9: connected
! Total: 8 connected out of 9 = QUORUM MET (majority ≥ 5)

! Step 4: Verify network continues to function
PC1# ping 10.0.03.10
Reply from 10.0.03.10: bytes=32 time=7ms

! Success metric: Network continues despite Byzantine node offline
```

## 7. Expected Output Gallery (Field 3)

### 7.1 Router Interface Status
```
Router# show ip int brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.03.1    YES manual up                    up
GigabitEthernet0/1         10.0.03.11   YES manual up                    up
Serial0/0                  10.0.03.2    YES manual up                    up
```

### 7.2 Routing Table (Field 3)
```
Router# show ip route
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area

C     10.0.03.0/24 is directly connected, GigabitEthernet0/0
C     10.0.03.11/24 is directly connected, GigabitEthernet0/1
C     10.0.03.2/24 is directly connected, Serial0/0
```

### 7.3 Ping Output (Normal and Under Stress)
```
PC1# ping 10.0.03.10 -c 5
Request sent from ICMP seq=1, timeout=20ms
Reply from 10.0.03.10: bytes=32 time=5ms TTL=63
Reply from 10.0.03.10: bytes=32 time=6ms TTL=63
Reply from 10.0.03.10: bytes=32 time=7ms TTL=63
Reply from 10.0.03.10: bytes=32 time=5ms TTL=63
Reply from 10.0.03.10: bytes=32 time=6ms TTL=63
Sent=5, Received=5, Lost=0% (0), Minimum=5ms, Average=5.8ms, Maximum=7ms
```

## 8. Common Mistakes (Field 3: DePIN)

1. **Central node still exists (not true mesh)**
   - Problem: Byzantine resilience untested
   - Fix: Ensure full mesh or high-degree partial mesh (each node 3+ peers)
   - Verify: `show neighbors` lists multiple paths to every node

2. **Quorum calculation wrong**
   - Problem: Network tolerates more Byzantine nodes than it should
   - Fix: Quorum = n/2 + 1 (e.g., 9 nodes needs 5; 50 nodes needs 26)
   - Verify: Fail 1+ nodes and check quorum still has majority

3. **No consensus voting implemented**
   - Problem: Network doesn't actually validate decisions
   - Fix: Add voting logic (even pseudo-code is acceptable for Day 3)
   - Verify: Routing table updates require majority vote

## 9. Troubleshooting (Field 3: DePIN)

**Problem: Byzantine node offline but network still works (too well)**
**Diagnosis:**
- Quorum calculation wrong, or network has more nodes than expected
- Verify: `show neighbors | count` (how many nodes?)

**Solution:**
```
! For 9 nodes, need 5 to agree (n/2 + 1)
! Take 4 offline (not Byzantine, just down)
! If network continues: Quorum still has 5 ✓
! Take 5 offline: Network should stop converging ✗
```

**Problem: Mesh not fully connected**
**Diagnosis:**
- Some nodes unreachable from others
- Check: `traceroute 10.0.{day}.99` from each node

**Solution:**
- Add more links (physical or virtual in GNS3)
- Verify: Every node has 3+ neighbors (partial mesh minimum)

## 10. Design Analysis (Field 3: DePIN - Mesh)

**Why mesh topology for IPv4 Addressing & Subnetting?**

DePIN (Decentralized Physical Infrastructure) cannot rely on central hub:
- Nodes are independently owned
- No central authority decides routing
- Byzantine nodes may appear (offline, malicious, or compromised)

Hub-and-spoke topology (Field 1, Field 2):
- Central router is single point of failure
- NOT suitable for decentralized deployment

Mesh topology (Field 3):
- Every node has multiple paths
- Byzantine faults isolated (don't break entire network)
- Voting/consensus ensures correctness

**Key metric:** Network continues despite Byzantine nodes
- 9 nodes, 1 Byzantine: Network continues ✓ (quorum 5/8 = 62%)
- 9 nodes, 5+ Byzantine: Network halts ✗ (quorum < 50%)
- Demonstrates: Byzantine fault tolerance is real constraint on mesh design

## 11. Real-World Parallel (Field 3: DePIN - Mesh)

**Decentralized Network in Rural Haiti (Proposed):**

Deployment model: Mesh radio network, 50-100 nodes
- Each node independently owned by local community
- Mesh backhaul to nearest city
- No central router (decision-making distributed)

Byzantine failure scenario:
- Node 5: Router firmware outdated, occasionally lies about routes
- Node 12: Powered down for maintenance
- Node 31: Compromised by malware, announces wrong metrics

Network must continue despite these nodes:
1. Quorum voting: 50 nodes, need 26 for consensus
2. Node 5 (lying) isolated by other 49 nodes
3. Node 12 (down) bypassed via alternate paths
4. Node 31 (malicious) blocked from routing table updates

**This lab validates:** IPv4 Addressing & Subnetting works in Byzantine-fault-tolerant mesh
- Success: Network converges despite 3 bad nodes
- Metric: All other 47 nodes find correct routes

## 12. Stretch Goals (Field 3: DePIN)

1. **Byzantine attack patterns**
   - Sybil attack: 1 node claims to be 10 identities
   - Routing attack: Node announces better metrics to itself
   - Test: Voting system rejects malicious updates

2. **Consensus algorithm proof**
   - Implement formal Byzantine fault tolerance (PBFT or Raft)
   - Prove: n/2 + 1 majority is necessary and sufficient
   - Bonus: Model check with TLA+ or Spin model checker

3. **Full-mesh at 100+ nodes**
   - Test mesh topology at 100 nodes (not just 9)
   - Measure: Convergence time scales (linear, logarithmic, exponential?)
   - Optimize: Reduce mesh degree (each node connects to 5 peers, not all)

4. **Leader election under Byzantine conditions**
   - Implement distributed leader election (Bully algorithm or Raft)
   - Test: Leader elected even with 1 Byzantine node
   - Bonus: Leader change when leader goes Byzantine

## 13. Self-Assessment (Field 3: DePIN)

**BSL-1 (Remember):** Understand Byzantine fault tolerance
- [ ] Define Byzantine fault and Byzantine failure
- [ ] Explain quorum voting (n/2 + 1)
- [ ] Name advantages of mesh topology

**BSL-2 (Understand):** Configure mesh topology
- [ ] Create 9-node full mesh network
- [ ] Enable voting/consensus for routing decisions
- [ ] Verify quorum calculation (9 nodes → 5 needed)

**BSL-3 (Apply):** Simulate Byzantine failures
- [ ] Take 1 Byzantine node offline
- [ ] Verify network converges with 8-node quorum
- [ ] Test alternate paths (mesh redundancy)

**BSL-4 (Analyze):** Evaluate Byzantine attack resilience
- [ ] Analyze routing table after Byzantine node injected lies
- [ ] Trace consensus votes (did majority reject malicious data?)
- [ ] Compare: Hub-spoke vs. mesh Byzantine tolerance

**BSL-5 (Evaluate):** Prove Byzantine fault tolerance for DePIN
- [ ] Run 50 Byzantine attack scenarios
- [ ] Verify: Network continues despite Byzantine nodes
- [ ] Measure: Consensus latency (time to reach 51% agreement)

**BSL-6 (Create):** Design Byzantine-tolerant consensus
- [ ] Implement PBFT or Raft consensus algorithm
- [ ] Prove: f < n/3 Byzantine nodes tolerated (where f = malicious)
- [ ] Model check with TLA+ (formal verification)

**BSL-7 (Publish):** Validate DePIN design for Haiti
- [ ] Deploy mesh consensus to Haiti test site
- [ ] Publish: "Byzantine-Fault-Tolerant Mesh Networks for Haiti"
- [ ] Prove: DePIN model works in practice
