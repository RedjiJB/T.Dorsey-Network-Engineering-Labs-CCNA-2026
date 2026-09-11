# Day 14 Practice Lab: VLAN Troubleshooting Scenarios

**Part 1: Given Broken Topology - Fix Three Issues**

You have a 3-switch network. Users in VLAN 10 can't reach users in VLAN 10 on SW3. Here's what you see:

```
SW1# show vlan brief | include 10
 10   VLAN0010    active   g0/1, g0/2

SW2# show vlan brief | include 10
 10   VLAN0010    active   f0/1

SW3# show vlan brief | include 10
 10   VLAN0010    active   f0/3
```

But SW1's trunk to SW3 shows:
```
SW1# show int g0/2 switchport | include Allowed
Allowed Vlans: 1,20
```

**Tasks:**
1. Identify the problem
2. Write the commands to fix it on SW1
3. Verify the fix with show commands
4. Predict whether users can now communicate

**Part 2: Prediction Exercise**

**Scenario:** You configure a trunk between two switches with:
- SW1: `switchport trunk mode trunk` 
- SW2: `switchport trunk mode dynamic auto`

Question: Will the trunk negotiate up? Why or why not?

**Scenario:** Native VLAN mismatch:
- SW1: `switchport trunk native vlan 10`
- SW2: `switchport trunk native vlan 1` (default)

Untagged traffic arrives from SW1 on SW2. Which VLAN will SW2 assign it to? Is this a problem?

**Part 3: Design Challenge**

You have four departments (Eng, Sales, HR, Ops) on three switches:
- SW1: Eng + Sales trunked to core
- SW2: HR trunked to core
- SW3: Ops trunked to core

Design the VLAN scheme and trunk configuration. Answer:
1. How many VLANs do you need?
2. Which VLANs should be allowed on each trunk?
3. Where should the default gateway (router) connect?

**Part 4: Hands-On Troubleshooting**

Given a broken lab, run these commands in order and record output:
1. `show vlan brief` - Are all required VLANs present on all switches?
2. `show int g0/1 switchport | include Allowed` - Is each trunk allowing its VLANs?
3. `show mac address-table | include <vlan>` - Are MAC addresses learning per VLAN?
4. Test: `ping` within VLAN, then across VLAN
5. If still broken, check router: `show ip route`

Document your findings and propose a fix.
