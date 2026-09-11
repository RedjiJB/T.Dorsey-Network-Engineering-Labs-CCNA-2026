# Day 17 Practice Lab: VLAN Troubleshooting & Verification Mastery

**Objective:** Master diagnostic techniques to resolve real-world VLAN connectivity issues; verify complex multi-VLAN designs

---

## Part 1: VLAN Connectivity Troubleshooting Flowchart

**Given:** Network with 5 switches, 4 VLANs (10, 20, 30, 40), router with ROAS. Users report "can't reach server in Finance VLAN."

**Step-by-Step Diagnosis:**

### Step 1: Verify Local VLAN Membership
```
Question: Is the source PC in the correct VLAN?
Command: show vlan id 10 | include f0/1
Expected: Port f0/1 listed under VLAN 10
If wrong: Fix with switchport access vlan 10
```

### Step 2: Verify VLAN Exists on All Switches
```
Question: Does the destination Finance VLAN (20) exist on the path?
Command: (on each switch in path) show vlan brief | include 20
Expected: VLAN 20 active on Finance switch
If missing: Create with vlan 20 command
```

### Step 3: Verify Trunk Path
```
Question: Do trunks allow both source and destination VLANs?
Command: show int g0/1 switchport | include Allowed
Expected: Both VLAN 10 and VLAN 20 in allowed list
If missing: Add to allowed list with switchport trunk allowed vlan add 20
```

### Step 4: Verify MAC Address Learning
```
Question: Are MAC addresses learning per VLAN?
Command: show mac address-table | include 10
Expected: Source PC MAC in VLAN 10 table
If empty: Check if port is receiving frames (use port counters)
```

### Step 5: Verify Router Has Routes
```
Question: Can router reach both VLANs?
Command: show ip route | include (10.0.10|10.0.20)
Expected: Two connected routes for source and destination VLANs
If missing: Check ROAS subinterface configuration
```

### Step 6: Test Reachability
```
Command: ping 10.0.20.1 (router gateway for VLAN 20)
Expected: Success if all above steps pass
```

---

## Part 2: Given Broken Lab - Fix Five Issues

**Scenario:** A 3-switch network with ROAS. Users in VLAN 10 cannot reach users in VLAN 20. You have 15 minutes to diagnose and fix.

**Run These Commands In Order:**

1. **On Switch with source PC:**
   ```
   show vlan brief | include 10
   show int f0/1 switchport | include (Mode|Access VLAN)
   show mac address-table | include 10
   ```
   **Question:** Is the PC port correct? Is MAC learning?

2. **On core/distribution switch:**
   ```
   show int g0/1 switchport | include Allowed
   show int g0/2 switchport | include Mode
   show vlan brief
   ```
   **Question:** Are trunks allowing all needed VLANs?

3. **On destination switch:**
   ```
   show vlan brief | include 20
   show int f0/3 switchport | include Access VLAN
   ```
   **Question:** Does VLAN 20 exist? Is destination PC port correct?

4. **On Router:**
   ```
   show ipv6 unicast-routing
   show int g0/0.10 | include (up|encapsulation)
   show int g0/0.20 | include (up|encapsulation)
   show ip route connected
   ping 10.0.20.10
   ```
   **Question:** Are subinterfaces up? Do routes exist?

**Fix up to 5 issues. Document each fix and the command you used.**

---

## Part 3: Scenario-Based Troubleshooting

### Scenario A: The "Trunk Negotiation" Problem

**Symptoms:**
- Ports show "up, up" but no VLAN traffic crossing
- `show int g0/1 switchport` shows Mode: dynamic auto on both sides

**Investigation:**
```
SW1# show int g0/1 switchport | include Mode
Switchport Mode: dynamic auto

SW2# show int g0/2 switchport | include Mode
Switchport Mode: dynamic auto
```

**Question:** Will these negotiate to trunk? Why or why not?

**Fix:** Write the exact commands to force trunking on both sides

---

### Scenario B: The "Native VLAN Mismatch" Problem

**Symptoms:**
- Management VLAN unreachable across trunk
- User VLANs work fine

**Investigation:**
```
SW1# show int g0/1 switchport | include native
Native VLAN: 1

SW2# show int g0/2 switchport | include native
Native VLAN: 99
```

**Question:** What happens to untagged traffic from SW1 to SW2?

**Fix:** Make both native VLANs match (choose one and apply to both)

---

### Scenario C: The "Asymmetric Routing" Problem

**Symptoms:**
- PC1 in VLAN 10 can ping PC2 in VLAN 20
- PC2 in VLAN 20 cannot ping PC1 in VLAN 10

**Investigation:**
```
Source (PC1): ping 10.0.20.10 → SUCCESS
Destination (PC2): ping 10.0.10.10 → TIMEOUT

show ip route on router:
C 10.0.10.0/24 is directly connected, g0/0.10
C 10.0.20.0/24 is directly connected, g0/0.20

show mac address-table on SW2:
VLAN 20 MAC table shows both local PCs
(but VLAN 10 MAC not seen from PC1's perspective)
```

**Question:** Why would reply be stuck? What's the root cause?

**Hint:** Check if VLAN 20 frames can successfully exit the source switch via trunk

---

## Part 4: VLAN Design Review Exercise

**Context:** You're handed existing network documentation. Your job: verify it's correct.

**Review Checklist:**
- [ ] All VLAN IDs are documented (10-99 range, no gaps)
- [ ] Subnet ranges don't overlap (10.0.x.0/24 per VLAN)
- [ ] Each VLAN has a default gateway (router subinterface)
- [ ] Trunk allowed lists match VLAN deployment
- [ ] Access ports correctly assigned per user type

**Given Documentation (review for errors):**
```
VLAN 10 (Engineering): 10.0.10.0/24, Router: 10.0.10.1
VLAN 20 (Finance): 10.0.20.0/24, Router: 10.0.20.1
VLAN 30 (Sales): 10.0.20.0/24, Router: 10.0.30.1   ← ERROR?
VLAN 99 (Guest): 192.168.99.0/24, Router: 192.168.99.1

SW1 g0/1 trunk: allowed VLANs 1,10,20,30
SW2 g0/1 trunk: allowed VLANs 1,10,20,99           ← MISMATCH?
```

**Identify:** Which errors would break connectivity? Which are just documentation issues?

---

## Part 5: Prediction & Explanation Exercise

**Scenario A:** You delete VLAN 15 from a switch while it's active.
- **Prediction:** What happens to ports assigned to VLAN 15?
- **Behavior:** Ports suspend (go to "suspended" state) until VLAN is recreated
- **Question:** If you re-create VLAN 15 later, do ports automatically re-activate?

**Scenario B:** You configure a trunk with allowed VLANs 1,10,20 but later add VLAN 30 to a switch.
- **Prediction:** Can VLAN 30 traffic cross the trunk?
- **Answer:** No; VLAN 30 not in allowed list
- **Fix:** Add VLAN 30 to allowed list with `switchport trunk allowed vlan add 30`

**Scenario C:** You configure ROAS with subinterface g0/0.10 for VLAN 10, but on the switch you set native VLAN to 10.
- **Prediction:** Will routing work? Will there be conflicts?
- **Issue:** Native VLAN (untagged) on trunk should NOT be a routed VLAN to avoid confusion
- **Best Practice:** Keep native VLAN as VLAN 1 (management), not a user VLAN

---

## Part 6: Performance & Scaling Challenge

**Scenario:** Your company is adding 100 new users across 10 new departments (10 new VLANs). Current design handles 30 VLANs.

**Questions:**
1. Can a single trunk carry 40 VLANs? Any limits?
2. What's the maximum number of VLANs on a Cisco 2960 switch? (Research: 4094)
3. If each VLAN is /24 (254 IPs), what's the max IP space you need for 40 VLANs?
4. How would you organize the VLAN ranges? (e.g., 10-49 for departments, 50-99 for special purpose)

**Design a VLAN allocation scheme** that scales to 200 users with room for growth

---

## Part 7: Self-Check Mastery Test

**Knowledge Check:**
- [ ] I can systematically diagnose VLAN issues without guessing
- [ ] I understand the difference between switch-level and router-level problems
- [ ] I know when to check trunks vs. access ports vs. routing
- [ ] I can explain asymmetric routing in VLANs

**Skills Check:**
- [ ] I used show commands to isolate the problem
- [ ] I proposed and applied fixes
- [ ] I verified fixes actually worked (not just assumed)
- [ ] I documented each step

**Design Check:**
- [ ] I can review VLAN documentation for errors
- [ ] I can plan VLAN allocation for growing networks
- [ ] I understand scalability limits and best practices

---

## Part 8: Real-World Simulation

**Scenario:** You're on-call at 2 AM. Finance department just reported "can't access headquarters finance server." You have:
- 20 switches
- 5 routers (one is ROAS-only)
- 500+ users across 20 VLANs
- No direct access to user PCs (tickets only)

**What's your first action?**
- A) Reboot the router
- B) Check which VLAN Finance is on, verify trunk connectivity
- C) Ask users to restart their computers
- D) Check router routing table and ROAS subinterfaces

**Why?** (Explain your answer in terms of OSI layers and elimination)

---

## Expected Outcomes

After this practice lab, you should be able to:
- [ ] Troubleshoot VLAN issues systematically (top-to-bottom)
- [ ] Diagnose trunk, access, and routing VLAN problems
- [ ] Fix and verify connectivity restoral
- [ ] Design and review VLAN schemes for production networks
- [ ] Explain asymmetric routing and native VLAN issues
- [ ] Scale VLAN design for growing networks
