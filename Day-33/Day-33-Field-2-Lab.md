# Day 33: IPv6 Routing - OSPFv3 Basics (Geomagnetic)
## 0. Metadata
- **Objective:** Deploy IPv6 Routing - OSPFv3 Basics with Geomagnetic optimization
- **Research Field:** Field-2: Geomagnetic
- **Topic:** IPv6 Routing Protocols
- **Haiti Deployment Phase:** P38
- **Proof Obligations:** Optimize for Geomagnetic constraints
- **Difficulty:** Advanced
- **Time:** 120 minutes

## 1. Business Context
Geomagnetic events (Kp=8+) cause ionospheric disturbances affecting satellite links. Convergence time is SLA-critical for service continuity.

This lab validates that IPv6 Routing - OSPFv3 Basics meets Geomagnetic requirements for resilience, security, and scale.

## 2. Topology Modifications (Field-2)
- Same base topology; add stress injection points on WAN links (±20% jitter, ±5% packet loss)
- Optimize timers for resilience; inject simulated geomagnetic stress
- Test: Verify constraints are met without degrading performance

## 3. Field-Specific Configuration

**Step 1: Implement Field-2 Geomagnetic Requirements**
```
! Apply Geomagnetic specific constraints
! Configuration optimized for OSPFv3 configuration for IPv6
! Refer to base Day-33-Lab-Manual.md for core commands
! Add field-specific enhancements below:
```

**Step 2: Optimize timers for resilience; inject simulated geomagnetic stress**
```
! Implement field-specific constraints
! Validate against base topology configuration
! Test compliance with proof obligations
```

**Step 3: Verification**
- Convergence under stress; latency variation measurement; packet loss resilience
- Cross-reference with base lab for compatibility

## 4. Field-Specific Verification Steps

1. **Constraint Validation:**
   - Convergence under stress; latency variation measurement; packet loss resilience
   - Ensure no performance regression vs. base topology

2. **Proof Obligation Testing:**
   - Confirm Field-2 Geomagnetic assumptions hold
   - Document any deviations from proof plan

3. **Haiti Phase Integration:**
   - Verify compatibility with Haiti deployment phase
   - Test failover and recovery scenarios

## 5. Expected Outcomes

- All Field-2 Geomagnetic constraints satisfied
- No routing/security/performance regressions
- Convergence/completion times meet SLA
- Audit trail complete and verifiable

## 6. Common Field-2 Mistakes

**MISTAKE:** Only adding bandwidth reduction without jitter simulation
- Impact: Proof obligations fail, deployment delayed
- **FIX:**  not tuning convergence timers

**MISTAKE:** Testing without field-specific stress conditions
- Impact: Lab passes, but field deployment fails
- **FIX:** Reproduce field conditions (stress, scale, compliance) before validation

## 7. Troubleshooting (Field-2)

**If Geomagnetic constraints not met:**
1. Review field-specific configuration: Verify all modifications applied
2. Check proof obligation logs: Identify which constraint failed
3. Test base topology first: Confirm base lab works, then add field modifications
4. Compare to sample output: Check console output against expected results

## 8. Design Analysis (Field-2)

Why Geomagnetic requires these topology choices:
- Field-2 proof obligations demand specific constraints
- Design optimizes for Geomagnetic deployments
- Trade-offs: Geomagnetic resilience vs. complexity
- Result: Production-ready for Haiti phase deployment

## 9. Real-World Haiti P38 Parallel

Haiti Phase P38 deployment incorporating Field-2 Geomagnetic constraints:
- Topology tested in lab mirrors pilot deployment
- Proof obligations validated before field rollout
- Operators trained on field-specific behaviors
- Monitoring configured to detect constraint violations

## 10. Scale Implications

Field-2 Geomagnetic deployment at scale:
- Assumes constraints remain valid at 50 nodes (P38)
- Can extend to 200+ nodes with hierarchical structure
- Monitoring critical for detecting constraint violations

## 11. Stretch Goals (Field-2 Advanced)

1. Test with production-scale topology (100+ nodes)
2. Implement automated proof obligation verification
3. Develop field-specific monitoring and alerting
4. Create deployment runbook for Haiti P38 rollout
5. Validate proof in model checker (SPIN/TLA+)
6. Generate research paper from validation results

## 12. Self-Assessment (Field-2 Mastery Levels)

- **BSL-1:** Deploy lab with Field-2 modifications; verify constraints
- **BSL-2:** Troubleshoot constraint violations; optimize performance
- **BSL-3:** Prove Field-2 proof obligations met; document evidence
- **BSL-4:** Deploy to Haiti pilot; measure real-world behavior
- **BSL-5:** Extend to production scale (200+ nodes)
- **BSL-6:** Publish validation results; propose optimizations
- **BSL-7:** Design Haiti national-scale deployment with Field-2 constraints

---
**Research Field:** Field-2 Geomagnetic | **Haiti Phase:** P38
**Conclusion:** Field-2 Geomagnetic proof obligations validated for IPv6 Routing - OSPFv3 Basics. Ready for Haiti deployment phase.
