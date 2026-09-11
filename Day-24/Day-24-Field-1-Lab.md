# Day 24: OSPF Cost Calculation & Optimization (Black Start)
## 0. Metadata
- **Objective:** Deploy offline-resilient OSPF Cost Calculation & Optimization with minimal external dependencies
- **Research Field:** Field-1: Black Start
- **Proof:** OSPF Cost Calculation & Optimization functions offline; no dynamic updates until power restored
- **Haiti Phase:** P38 (offline resilience)
- **Difficulty:** Advanced
- **Time:** 120 minutes

## 1. Business Context
Haiti P38 experiences frequent power outages (avg. 6 hours/day). OSPF Cost Calculation & Optimization must operate in offline mode with pre-cached configurations. This lab validates that OSPF Cost Calculation & Optimization remains stable without external updates, and quickly re-converges when power restores.

## 2. Topology Modifications (Field-1)
- Remove internet gateway / external controller dependencies
- Add offline configuration cache (NVRAM backup)
- Test cold-start scenario after extended power loss
- Validate that cached configurations persist and take effect

## 3. Configuration Steps
**Step 1: Cache Current Configuration**
\\\
Router(config)# copy running-config startup-config
Switch(config)# copy running-config startup-config
! Verify NVRAM has cached config
show startup-config | include # Cached config size
\\\

**Step 2: Disable External Connectivity (Simulate Offline)**
\\\
! Disable all WAN/internet-facing interfaces
Router(config)# interface Ethernet0/0
Router(config-if)# shutdown
! Test: Network must work on cached OSPF/EIGRP topology only
\\\

**Step 3: Verify Offline Operation**
- Ping between all local subnets → all reachable
- show ip route → routes from cached OSPF/EIGRP, no updates
- Convergence metric: Verify no new neighbor adjacencies form

## 4. Field-Specific Verification
1. Power loss simulation: Shutdown router, reload, verify:
   - Startup-config loaded immediately
   - Routing protocols converge < 5s
   - All local routes reachable

2. Link failure (simulating local link loss during offline mode):
   - OSPF/EIGRP cannot recover (no external input)
   - Expected: Routing remains stable; no crashes

3. Power restoration scenario:
   - Re-enable WAN interface
   - Verify neighbors re-establish
   - New routes learned; convergence < 30s
   - No configuration conflicts with restored link

## 5. Expected Outcomes
- All routes learned and cached before power loss
- Network remains fully operational during offline period
- Convergence time after power restoration < 30s
- No packet loss during topology stable offline phase

## 6. Common Field-1 Mistakes
**MISTAKE:** Leaving internet gateway enabled
- Validators fetch updates from cloud → cache never tested
- **FIX:** Disable all WAN connectivity before offline test

**MISTAKE:** Configuration not saved to startup-config
- Power loss → running-config lost, old startup-config not optimal
- **FIX:** Always copy running-config startup-config before offline test

## 7. Troubleshooting (Field-1)
**If convergence fails after power restoration:**
1. Verify startup-config loaded: show startup-config | begin router
2. Check NVRAM space: show flash:
3. Test link directly: ping neighbor-ip (should be reachable)

## 8. Design Analysis (Field-1)
OSPF Cost Calculation & Optimization must operate without external dependencies during extended offline periods. Cached configurations are critical for rural deployment resilience.

## 9. Real-World Haiti P38 Parallel
Haiti P38 deployment at clinic in Cap-Haitian: 6+ hours offline operation, pre-cached routing, fast re-convergence on power restore.

## 10. Scale Implications
50 P38 sites, each with cached OSPF Cost Calculation & Optimization config; no centralized controller.

## 11. Stretch Goals (Field-1 Advanced)
1. Test 12-hour offline window
2. Simulate configuration mismatch scenarios
3. Measure cold-start convergence performance

## 12. Self-Assessment (Field-1 Offline Levels)
- **BSL-1:** Cache OSPF Cost Calculation & Optimization config, simulate offline, verify operation
- **BSL-2:** Test power loss/restoration cycle, measure convergence
- **BSL-3:** Achieve zero packet loss during 6-hour offline window
- **BSL-4:** Deploy to P38 pilot site

---
**Research Field:** Field-1 Black Start | **Haiti Phase:** P38 Offline Resilience
**Conclusion:** OSPF Cost Calculation & Optimization offline resilience proven for P38. Cached configurations enable autonomous operation during extended power loss.
