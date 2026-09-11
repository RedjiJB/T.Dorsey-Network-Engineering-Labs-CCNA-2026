# Day 03: IPv4 Addressing & Subnetting (Field 7: Haiti)

## 0. Metadata

- **Objective:** Prove IPv4 Addressing & Subnetting functionality in Haiti (Field 7) constraints
- **Research Field:** Field 7: Haiti
- **Proof Obligations:**
  - Validate IPv4 Addressing & Subnetting works without external dependencies (Field 1) / under stress (Field 2) / in mesh topology (Field 3) / at Haiti scale (Field 7)
  - Document convergence time and resource usage
  - Prove resilience to field-specific failure modes
- **Haiti Deployment Phase:** P55+ (sustained operations)
- **Relevant RFC/Standards:** IEEE 802.3 (Ethernet), RFC 791 (IPv4), RFC 1918 (Private Addresses)
- **Prerequisites:** Day 03 base lab manual + Field 7 environment setup
- **Estimated Time:** 150-180 minutes (includes stress testing)
- **Difficulty:** Advanced
- **Hardware Required:** 4-6 routers/switches, 6-8 PCs, stress injection appliance (Field 2) or mesh topology (Field 3)
- **Key Concepts:** Field-optimized IPv4 Addressing & Subnetting, Haiti-specific validation, proof obligations, real-world constraints

## 1. Business Context

Haiti deployment combines all constraints: offline-first operation, geomagnetic stress, distributed governance, and scale.
This lab proves IPv4 Addressing & Subnetting works at **production scale** (50-1000+ nodes) under **all constraints combined**:
- Field 1: Offline-only validation
- Field 2: Geomagnetic stress injection
- Field 3: Mesh topology with Byzantine nodes
- Field 7: All above at 50→200→1000+ node scale

**Why this matters:** Haiti P38/P45/P52+ deployments must handle real-world chaos. IPv4 Addressing & Subnetting is foundational to mission success.

## 2. Topology Diagram (Field 7: Haiti - Combined)

```
        P38 (50 nodes):
          [Gateway]
            |
         [Core]--[Stress]--[Cache]
           /|\
          / | \
       Mesh|DePIN + Offline + Geomagnetic

        P45 (200 nodes):
          [Multiple gateways] (mesh backup)
            |
        [Core Hub] (but each region self-sufficient)
           /|\
          / | \
       Regional | Mesh + Stress Injection

        P52+ (1000+ nodes):
          Distributed Regional Cores
              /|\
             / | \
        Mesh + Offline-First + Geomagnetic Mitigation

Topology notes:
- Combine Field 1 (offline cache), Field 2 (stress injection), Field 3 (mesh)
- Scale progressively: 50 → 200 → 1000+ nodes
- Test IPv4 Addressing & Subnetting convergence time at each scale
- Add realism: Variable latencies, multiple ISPs, regional independence
```

**Modifications for Field 7:**
- Combine all Field 1, 2, 3 modifications
- Scale test network to 50+ nodes (P38), 200+ (P45), 1000+ (P52+)
- Add multi-region topology with mesh backbones
- Test IPv4 Addressing & Subnetting with offline-first design, stress injection, Byzantine tolerance

## 3. IP Addressing Plan

| Device | Role | Subnet | Address | Mask | Notes |
|--------|------|--------|---------|------|-------|
| R1 | Primary | 10.0.03.0/24 | 10.0.03.1 | /24 | Field 7 core router |
| R2 | Secondary | 10.0.03.0/24 | 10.0.03.2 | /24 | Backup/mesh peer |
| SW1 | Access | 10.0.03.0/24 | 10.0.03.254 | /24 | Access switch VLAN |
| PC1 | Client | 10.0.03.0/24 | 10.0.03.10 | /24 | Test client 1 |
| PC2 | Client | 10.0.03.0/24 | 10.0.03.20 | /24 | Test client 2 |

**Field 7 specific notes:**
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
- [ ] P38 scale (50 nodes) test environment built
- [ ] Combination of Field 1 (cache), Field 2 (stress), Field 3 (mesh) active
- [ ] Haiti-specific latency profiles loaded (multi-region)
- [ ] Success metrics documented (time, resource use, convergence)

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

### 5.2 Field 7 Specific Configuration


```
! Field 7: Haiti - Combine Fields 1+2+3 at scale

! Primary interface (Field 1: offline-capable)
Router(config)# int g0/0
Router(config-if)# ip address 10.0.03.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

! Secondary interface (Field 2: stress injection target)
Router(config)# int s0/0
Router(config-if)# ip address 10.0.03.2 255.255.255.0
Router(config-if)# bandwidth 1000
Router(config-if)# delay 20000
Router(config-if)# no shutdown
Router(config-if)# exit

! Mesh interfaces (Field 3: Byzantine resilience)
Router(config)# int g0/1
Router(config-if)# ip address 10.0.03.11 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

! Cache configuration
Router# write memory

! Summary:
! - Offline operation (no internet dependency)
! - Stress-resistant (latency jitter tolerance)
! - Mesh-capable (Byzantine node resilience)
! - Scale-tested (50-1000+ nodes at P38-P52+)
```

## 6. Field-Specific Verification Steps

### 6.1 Basic Connectivity Test
```
Router# show ip int brief
Router# show ip route
Router# ping 10.0.03.10
```

### 6.2 Field 7 Specific Verification


### 6.2.4 Haiti Scale Verification (Field 7)
```
! Step 1: Start with 50 nodes (P38), verify offline + stress + mesh
! (Run all Field 1 + 2 + 3 verifications above)

! Step 2: Scale to 200 nodes (P45)
Router# show ip route summary
Total routes: 200+
Connected: 200+
Memory usage: <100MB (estimate for 200-node mesh)

! Step 3: Monitor convergence time at each scale
! Expected: Linear or sub-linear scaling
P38 (50 nodes): convergence ~10-15 seconds
P45 (200 nodes): convergence ~15-20 seconds
P52 (1000 nodes): convergence ~20-30 seconds

! Step 4: Verify cache persistence (Field 1)
! Simulate power loss, verify state recovered

! Success metrics:
! - All three constraints (offline, stress, mesh) active simultaneously
! - Convergence time < 30 seconds even at 1000 nodes
! - Cache recovery takes < 5 minutes after power restore
```

## 7. Expected Output Gallery (Field 7)

### 7.1 Router Interface Status
```
Router# show ip int brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.03.1    YES manual up                    up
GigabitEthernet0/1         10.0.03.11   YES manual up                    up
Serial0/0                  10.0.03.2    YES manual up                    up
```

### 7.2 Routing Table (Field 7)
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

## 8. Common Mistakes (Field 7: Haiti Scale)

1. **Testing only one field at a time**
   - Problem: Fields interact; offline mode + geomagnetic stress is different
   - Fix: Combine all three field constraints simultaneously
   - Verify: Checklist includes offline + stress + mesh active

2. **Not scaling progressively**
   - Problem: Jump from 50 to 1000 nodes causes unexpected issues
   - Fix: Test P38 (50) → P45 (200) → P52 (1000+) incrementally
   - Verify: Document success/failure at each scale milestone

3. **Haiti-specific latencies not simulated**
   - Problem: Test doesn't match real Haiti conditions
   - Fix: Load actual ISP latency profiles (e.g., Haiti-US: 80-120ms)
   - Verify: Baseline latency from Haiti to backup site measured

## 9. Troubleshooting (Field 7: Haiti Scale)

**Problem: Convergence degrades at P45 (200 nodes) or P52 (1000 nodes)**
**Diagnosis:**
- Memory/CPU exhausted on test equipment
- Check: `show processes memory | sort`

**Solution:**
- Use more powerful hardware (or distribute across multiple devices)
- Reduce mesh degree (each node connects to 5-10 peers instead of all)
- Verify: Resource usage stays <80% on all nodes

**Problem: Offline mode + stress + mesh causes crashes**
**Diagnosis:**
- Features conflicting (cache invalidation during stress?)
- Check logs: `show log` for errors during stress periods

**Solution:**
- Test Field 1, Field 2, Field 3 independently first
- Then combine two at a time (1+2, then 1+3, then 2+3)
- Finally combine all three (1+2+3)

## 10. Design Analysis (Field 7: Haiti Combined)

**Why combine Fields 1+2+3 for Haiti deployment?**

Haiti P38-P52+ deployments face ALL constraints simultaneously:

1. **Offline-first (Field 1):** Power loss happens weekly
   - Network must cache state, survive autonomous for 2+ hours
   - Test: P38 (50 nodes) cache in < 100MB, recovery in < 5 minutes

2. **Geomagnetic stress (Field 2):** Space weather affects satellite links
   - Latency variation ±20% unpredictable
   - Test: Convergence < 60 seconds under stress

3. **Mesh resilience (Field 3):** Decentralized deployment
   - No central authority, Byzantine nodes tolerated
   - Test: Quorum maintains 51%+ even with 1/4 nodes down

**Scaling model:**
- P38 (50 nodes): Test proof of concept
- P45 (200 nodes): Test regional expansion
- P52 (1000+ nodes): Full production scale

**Key metric:** All three constraints active → Convergence still < 30 seconds at 1000 nodes
- Proves: IPv4 Addressing & Subnetting scales in Haiti deployment model

## 11. Real-World Parallel (Field 7: Haiti Production Deployment)

**Haiti P38 (50 sites), P45 (200 sites), P52 (1000+ sites) Rollout:**

Phase-by-phase deployment (2025-2027):

**P38 (Pilot, 50 nodes):**
- Location: Port-au-Prince, Cap-Haïtien, Jérémie
- Constraint: Power cuts 6 hrs/day, satellite link 500ms
- Test: This lab validates IPv4 Addressing & Subnetting at 50-node scale with all constraints

**P45 (Expansion, 200 nodes):**
- Add regional hubs: 5 regions × 40 nodes each
- Constraint: Mesh + offline-first + geomagnetic stress simultaneous
- Test: Convergence time should stay < 20 seconds even at 200 nodes

**P52 (Full production, 1000+ nodes):**
- National deployment, 10 regions
- Constraint: All above + multi-ISP failover
- Test: IPv4 Addressing & Subnetting proven at production scale (1000+ nodes)

**This lab progression (P38 → P45 → P52) proves:**
- IPv4 Addressing & Subnetting is deployment-ready for Haiti
- Scales linearly from 50 to 1000+ nodes
- Handles all three field constraints simultaneously
- Ready for 2025 Haiti rollout

## 12. Stretch Goals (Field 7: Haiti Scale)

1. **Full P52 simulation (1000+ nodes)**
   - Scale lab to 1000+ nodes
   - Measure convergence time (should be < 30 seconds)
   - Document: Resource usage, CPU, memory on each node

2. **Multi-region deployment test**
   - 10 regions × 100 nodes each = 1000 nodes total
   - Inter-regional latency: 50-100ms (realistic for Haiti multi-region)
   - Test: Regional independence + global consistency

3. **Haiti ISP failover scenario**
   - 3 ISPs: Natcom (primary), Digicel (secondary), Voilà (tertiary)
   - Simulate ISP outage: Failover to secondary ISP
   - Test: Does {topic} converge during failover?

4. **Cost model validation**
   - Calculate: Hardware cost per node (50-node, 200-node, 1000-node scale)
   - Document: Cost per Mb/s throughput
   - Prove: Haiti deployment is economically viable

5. **Real-world deployment pilot**
   - Deploy to Haiti test site (Port-au-Prince or Cap-Haïtien)
   - Run 30-day continuous operation
   - Collect: Actual outage data, convergence times, failure modes
   - Validate: Lab assumptions match real-world behavior

## 13. Self-Assessment (Field 7: Haiti Combined)

**BSL-1 (Remember):** Understand Haiti deployment constraints
- [ ] Name P38, P45, P52, P55+ phases
- [ ] Explain: Why Field 1 (offline) + Field 2 (stress) + Field 3 (mesh)?
- [ ] Describe Haiti deployment challenges

**BSL-2 (Understand):** Configure all-constraints network
- [ ] Build 50-node network with Field 1 + 2 + 3 combined
- [ ] Enable offline caching + geomagnetic stress + mesh consensus
- [ ] Verify: All three constraints active simultaneously

**BSL-3 (Apply):** Test at each Haiti phase
- [ ] P38 (50 nodes): Run full test suite, convergence < 15 seconds
- [ ] P45 (200 nodes): Scale to 200, convergence < 20 seconds
- [ ] Identify: Which constraint is bottleneck at each scale?

**BSL-4 (Analyze):** Diagnose scaling issues
- [ ] Measure: Memory/CPU usage per node (P38 vs. P45)
- [ ] Identify: Does mesh degree need reduction at P52?
- [ ] Compare: Expected vs. actual convergence times

**BSL-5 (Evaluate):** Prove Haiti deployment ready
- [ ] Run: P52 (1000+ node) full-scale test
- [ ] Document: Convergence time < 30 seconds at all scales
- [ ] Assess: Cost per node, operational feasibility

**BSL-6 (Create):** Optimize Haiti deployment architecture
- [ ] Propose: Hierarchical mesh (core mesh + access spokes)
- [ ] Design: Regional independence model (10 regions)
- [ ] Create: Operations manual for Haiti technicians

**BSL-7 (Publish & Deploy):** Haiti production deployment
- [ ] Deploy to Haiti P38 pilot (Port-au-Prince, Cap-Haïtien, Jérémie)
- [ ] Run 30+ days continuous operation
- [ ] Publish: "Network Deployment in Haiti: Lessons from 1000-node mesh"
- [ ] Submit to IEEE/ACM conference
- [ ] Prepare P45 rollout (200-node expansion)
