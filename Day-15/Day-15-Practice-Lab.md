# Day 15 Practice Lab: VLAN Design & Implementation

**Objective:** Design and implement a multi-VLAN switched network from scratch; test connectivity

---

## Part 1: VLAN Design Challenge

**Scenario:** Your company has three departments:
- **Finance** (20 users): Network 10.0.20.0/24
- **Engineering** (15 users): Network 10.0.30.0/24  
- **Operations** (25 users): Network 10.0.40.0/24

**Your Tasks:**
1. Assign VLAN numbers to each department
2. Document the VLAN scheme (create a VLAN table)
3. Design which access ports belong to which VLAN
4. Plan trunk links between switches (if using multiple switches)

**Questions to Answer:**
- Why would you use VLANs instead of one flat network?
- How many separate broadcast domains will you have after VLAN creation?
- If you have 48-port switches, how many physical ports per switch should be access vs. trunk?

---

## Part 2: Configuration from Scratch (No Answers)

**Given:** Three switches, one router, nine PCs (three per VLAN)

**Configure:**
1. Create VLANs on all switches (match your design from Part 1)
2. Assign access ports to the correct VLANs
3. Configure trunk links between switches
4. Set up management VLAN on each switch
5. Configure ROAS on the router (or verify VLAN routing works)

**Verification Checklist:**
- [ ] `show vlan brief` shows all three VLANs on all switches
- [ ] `show int [port] switchport` shows correct access VLAN for each port
- [ ] `show int [port] switchport` shows trunk mode with correct allowed VLANs
- [ ] PCs within same VLAN can ping each other
- [ ] PCs in different VLANs can ping through the router
- [ ] Switch management IP is reachable from each VLAN

---

## Part 3: Troubleshooting Exercise

**Given Broken Topology:**
You inherit a 3-switch network where Finance users can't reach Engineering users, but both can reach Operations.

**Your Investigation:**
1. Run: `show vlan brief` on all switches — what should you see?
2. Run: `show int g0/1 switchport` (check trunk) — what's wrong?
3. Run: `show mac address-table | include [vlan]` — are MAC addresses learning?
4. Check router: `show ip route` — are all VLANs showing as connected?

**Propose:**
- Write down what you think is broken
- Write the exact commands to fix it
- Verify the fix with show commands

---

## Part 4: Design Scenario

**Context:** Your company is expanding. You now need six VLANs instead of three:
- Finance (VLAN 20)
- Engineering (VLAN 30)
- Operations (VLAN 40)
- Sales (VLAN 50) — NEW
- HR (VLAN 60) — NEW
- Guest WiFi (VLAN 99) — NEW

**Challenge:**
1. Redraw the trunk configuration to accommodate all six VLANs
2. On a trunk link, show how you'd allow all six (plus management VLAN 1)
3. How many subinterfaces would the router need?
4. Document the complete configuration for one access switch

---

## Part 5: Prediction Exercise

**Scenario A:** You configure an access port in VLAN 10, but the trunk to the router doesn't allow VLAN 10.
- **Prediction:** Can the PC in VLAN 10 ping the router's VLAN 10 gateway IP? Why?
- **Verification Command:** `show int g0/1 switchport | include Allowed`

**Scenario B:** Native VLAN is set to 1 on the switch, but the router's native VLAN is set to 10.
- **Prediction:** Will untagged traffic from the switch reach the router correctly?
- **Explain:** What happens to untagged frames on a trunk?

**Scenario C:** You add VLAN 100 to three switches and configure ROAS subinterface g0/0.100, but forget to add VLAN 100 to the trunk allowed list.
- **Prediction:** Will ping from VLAN 100 PC to another VLAN's PC succeed?
- **Root Cause:** Where is the bottleneck?

---

## Part 6: Advanced Challenge

**Multi-Site Design:**
Your company has two office buildings connected by a WAN link. Each building has three VLANs:
- Building A: Finance (10.0.20.0/24), Engineering (10.0.30.0/24), Ops (10.0.40.0/24)
- Building B: Finance (10.0.120.0/24), Engineering (10.0.130.0/24), Ops (10.0.140.0/24)

**Questions:**
1. Can you use the same VLAN IDs (20, 30, 40) at both sites?
2. Should users in Finance at Building A be able to ping Finance at Building B? How would you route this?
3. Draw a topology showing how the two sites would connect
4. What's the difference between this and a simpler "one big flat network"?

---

## Part 7: Self-Check Walkthrough

**Understanding:**
- [ ] I can explain why VLANs isolate traffic
- [ ] I know the difference between access and trunk ports
- [ ] I understand why routers are needed for inter-VLAN communication
- [ ] I can design a VLAN scheme for a given network

**Configuration:**
- [ ] I created VLANs without syntax errors
- [ ] I assigned access ports correctly
- [ ] I set up trunk links with allowed VLAN lists
- [ ] I verified connectivity within and between VLANs

**Troubleshooting:**
- [ ] I can identify a broken VLAN configuration
- [ ] I know the commands to verify each layer (VLAN, trunk, routing)
- [ ] I can explain what went wrong and propose a fix

---

## Expected Outcomes

After this practice lab, you should be able to:
- [ ] Design a VLAN scheme for a given network
- [ ] Configure VLANs, access ports, and trunks from scratch
- [ ] Troubleshoot common VLAN connectivity issues
- [ ] Explain when and why VLANs are needed
- [ ] Document a VLAN deployment
