# Day 31 Practice Lab: Advanced Routing Protocols & Design

**Objective:** Master dynamic routing protocol design, implementation, and troubleshooting; compare RIP, OSPF, and EIGRP; optimize network convergence

---

## Part 1: Routing Protocol Selection Challenge

**Scenario:** Your company has three office locations connected via WAN links:
- **HQ (Site A):** 50 networks, high redundancy needed
- **Branch 1 (Site B):** 10 networks, minimal configuration preferred
- **Branch 2 (Site C):** 15 networks, unstable WAN link

**Your Tasks:**

1. **Choose a routing protocol** for each scenario:
   - RIP v2 (simplicity)
   - OSPF (complexity, convergence speed)
   - EIGRP (balance, Cisco-only)
   - Static routes (no automation)

2. **Justify your choice** by answering:
   - How many networks will the protocol handle?
   - What's the max hop count requirement?
   - Is bandwidth critical (slow WAN links)?
   - Does the company use only Cisco, or mixed vendors?

3. **Document trade-offs:**
   - Configuration complexity vs. network size
   - Memory/CPU overhead vs. convergence time
   - Scalability vs. number of routers

---

## Part 2: OSPF Configuration & Verification from Scratch

**Given:** Three routers (R1 HQ, R2 Branch1, R3 Branch2) with interconnected links

**Configure (No Answers Provided):**

1. **Enable OSPF on all routers:**
   - Set router-id (1.1.1.1 for R1, etc.)
   - Enable OSPF process 1
   - Advertise networks with correct area (0 for all)
   - Set reference bandwidth if needed

2. **Verify OSPF operation:**
   ```
   show ip ospf neighbor
   show ip ospf interface brief
   show ip route ospf
   ```

3. **Test failover behavior:**
   - Disable a link between R1-R2
   - Measure time for R2 to learn alternate route via R3
   - Document convergence time

4. **Troubleshoot if neighbors don't form:**
   - Check hello/dead timer intervals match
   - Verify area IDs match
   - Ensure MTU doesn't block large packets
   - Check for ACL blocking OSPF packets

**Verification Checklist:**
- [ ] `show ip ospf neighbor` shows all expected neighbors in FULL state
- [ ] `show ip route ospf` displays learned routes from other areas
- [ ] `ping` between loopback IPs of all routers succeeds
- [ ] Disabling a link triggers convergence (check time with repeated pings)

---

## Part 3: OSPF Cost Tuning & Load Balancing

**Scenario:** R1 reaches R3 via two paths:
- Path 1: R1→R2→R3 (cost 100)
- Path 2: R1→R4→R3 (cost 100)

Currently, traffic uses only Path 1. You want to load-balance.

**Challenge:**
1. Modify link costs so traffic splits 50/50 between paths
2. Verify with `show ip route ospf` (should show both paths)
3. Test with traffic generator to confirm split

**Commands to Use:**
```
interface g0/0
ip ospf cost 50
```

**Questions:**
- Why would you adjust costs instead of just configuring equal-cost paths?
- What's OSPF's default cost calculation? (10^8 / bandwidth)

---

## Part 4: EIGRP Routing - Comparison Exercise

**Scenario:** You have the same three-router topology, but this time configure EIGRP instead of OSPF.

**Configure:**
1. Enable EIGRP AS 100
2. Advertise networks with `network [subnet] [wildcard]`
3. Verify neighbor adjacency
4. Compare convergence with OSPF

**Questions:**
- Why does EIGRP advertise networks differently than OSPF?
- What's a wildcard mask? Why use `0.0.0.0` vs. `0.0.0.255`?
- How does EIGRP calculate feasible successors? (backup routes)

**Comparison Table (Fill In):**

| Feature | RIP v2 | OSPF | EIGRP |
|---------|--------|------|-------|
| Admin Distance | | | |
| Max Hop Count | | | |
| Convergence Speed | | | |
| Scalability | | | |
| Cisco-Only? | | | |
| Metric Calc | | | |

---

## Part 5: Troubleshooting Exercise - Routes Not Appearing

**Given Broken Scenario:**
You configured OSPF on three routers, but R2 is not learning routes from R1 and R3 (even though neighbors show FULL).

**Investigation Checklist:**
1. **Verify OSPF is enabled:**
   ```
   show running-config | include router ospf
   show ip ospf interface brief
   ```

2. **Verify networks are advertised:**
   ```
   show running-config | include network
   (check for typos, wrong areas)
   ```

3. **Verify no ACL blocks OSPF packets:**
   ```
   show access-lists
   (OSPF uses protocol 89; check if blocked)
   ```

4. **Check if interface is passive:**
   ```
   show ip ospf interface brief | include Passive
   (if marked "passive", neighbors won't form)
   ```

5. **Verify area matches:**
   ```
   show ip ospf interface g0/0 | include Area
   (all routers must have same area for neighborships)
   ```

**Propose:** What went wrong? How would you fix it?

---

## Part 6: Default Route Propagation

**Scenario:** Your HQ router (R1) has the default route to the ISP. Branch routers (R2, R3) need to send all non-local traffic to R1.

**Challenge:**
1. Configure R1 to advertise the default route via OSPF/EIGRP
2. Verify R2 and R3 learn it
3. Test: Can a branch PC reach a public IP (via R1)?

**Commands to Research:**
- OSPF: `default-information originate` (with or without `always`)
- EIGRP: `redistribute static` or `default-information originate`

**Questions:**
- Why advertise default route dynamically instead of configuring static on each branch?
- What's the difference between `originate` and `originate always`?

---

## Part 7: Metric Analysis & Route Selection

**Given:** Network with four routes to the same destination:

| Route | Protocol | Metric | Learned Via |
|-------|----------|--------|-------------|
| 10.0.1.0/24 | OSPF | 150 | R1 |
| 10.0.1.0/24 | EIGRP | 2000000 | R2 |
| 10.0.1.0/24 | RIP | 5 | R3 |
| 10.0.1.0/24 | Static | N/A | Config |

**Questions:**
1. Which route will the router prefer? (Hint: AD is lower first)
2. Order the admin distances: Static, OSPF, EIGRP, RIP
3. If two OSPF routers advertise the same route with different costs (150 vs. 200), which wins?
4. If two EIGRP routers advertise the same route with the same metric, will the router load-balance?

---

## Part 8: Convergence Time Measurement

**Scenario:** You've configured a redundant network (primary and backup paths). A failure occurs. How fast does convergence happen?

**Experiment:**
1. Set up continuous ping from PC to distant server
2. Fail the primary link (unplug cable)
3. Record time until pings resume (convergence time)
4. Repeat 3 times and average

**Expected Times:**
- RIP: 30-180 seconds (broadcast updates every 30s)
- OSPF: 5-10 seconds (fast hello/dead timers)
- EIGRP: 3-5 seconds (uses reliable multicast)

**Challenge:**
1. Optimize convergence time by tuning hello/dead intervals
2. Measure improvement
3. Explain the trade-off (faster convergence = more overhead)

---

## Part 9: Design & Troubleshooting Scenarios

### Scenario A: "Suboptimal Routing"
Users in a branch office access the data center, but traffic routes through an expensive satellite link instead of a cheaper fiber link. Both paths use OSPF.

**Investigation:**
- Check metrics on both paths (`show ip ospf interface | include Cost`)
- Verify actual link bandwidth matches OSPF calculation
- Adjust costs if needed

**Fix:** Lower cost on preferred path

### Scenario B: "Routing Loop"
Pings to a destination show increasing TTL (goes 64, 63, 62, ..., 0). The network is looping traffic.

**Causes to Check:**
- Mismatched router-IDs (can cause redistribution issues)
- Incorrectly redistributing routes between protocols
- Static routes conflicting with dynamic routes
- Unequal-cost load balancing misconfigured

**Fix:** Debug and remove loop cause (usually redistribution)

### Scenario C: "Neighbor Not Forming"
R1 and R2 should peer via OSPF, but `show ip ospf neighbor` is empty.

**Checklist:**
- [ ] Interfaces have IP addresses (check `show ip int brief`)
- [ ] Interfaces are UP and in correct areas
- [ ] No ACLs blocking OSPF (protocol 89)
- [ ] MTU is at least 576 bytes (OSPF has large packets)
- [ ] Hello/dead intervals match (or will negotiate)

---

## Part 10: Real-World Topology Design

**Context:** Your company is designing a network for:
- HQ: 100 networks
- Regional Offices: 5 regions, 20 networks each
- Branch Offices: 50 branches, 2 networks each

**Design Requirements:**
- Minimize WAN bandwidth usage
- Ensure convergence < 30 seconds on failure
- Support growth to 1000 networks over 5 years
- Use only Cisco routers (EIGRP is fine)

**Your Design:**
1. Choose a routing protocol
2. Propose a hierarchy (backbone area, regional areas, etc.)
3. Plan for summarization (aggregate routes at region level)
4. Document convergence strategy on link failures

---

## Part 11: Self-Check Walkthrough

**Conceptual Understanding:**
- [ ] I can explain how each routing protocol (RIP, OSPF, EIGRP) works
- [ ] I know admin distance and why it matters
- [ ] I understand metrics and how they're calculated
- [ ] I can predict which route will be chosen

**Configuration:**
- [ ] I configured OSPF/EIGRP from scratch without errors
- [ ] I verified neighbors formed and routes appeared
- [ ] I adjusted costs and observed load balancing
- [ ] I advertised default routes correctly

**Troubleshooting:**
- [ ] I diagnosed neighbor formation failures
- [ ] I identified routes not appearing and fixed it
- [ ] I measured convergence time and optimized it
- [ ] I identified and resolved routing loops

**Design:**
- [ ] I can choose the right protocol for a scenario
- [ ] I can justify my choice with metrics/convergence/scalability
- [ ] I can design a hierarchical network with summarization
- [ ] I understand trade-offs between simplicity and optimization

---

## Expected Outcomes

After this practice lab, you should be able to:
- [ ] Compare RIP, OSPF, EIGRP and select the right protocol
- [ ] Configure and verify dynamic routing from scratch
- [ ] Troubleshoot neighbor formation and route advertisement
- [ ] Optimize network performance through metric tuning
- [ ] Design scalable hierarchical routing architectures
- [ ] Measure and optimize convergence time
- [ ] Handle real-world scenarios (loops, suboptimal routing, migration)
