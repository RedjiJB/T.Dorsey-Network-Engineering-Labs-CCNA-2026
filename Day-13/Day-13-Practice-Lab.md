# Day 13 Practice Lab: Inter-VLAN Routing with Router-on-a-Stick

**Objective:** Configure ROAS from scratch with minimal guidance; troubleshoot a broken setup

## Part 1: Configuration Challenge (No Answers Provided)

**Scenario:** You have two switches already configured with VLANs 10 and 20, trunked to a router. The router g0/0 interface is up, but inter-VLAN communication is failing.

**Your tasks:**
1. Configure subinterface g0/0.10 for VLAN 10 (10.0.10.0/24)
2. Configure subinterface g0/0.20 for VLAN 20 (10.0.20.0/24)
3. Verify both subinterfaces are up with correct IPs
4. Test: PC in VLAN 10 should ping PC in VLAN 20
5. Explain why the parent interface (g0/0) must be up for subinterfaces to work

**Verification checklist:**
- [ ] show int g0/0 shows "up, up"
- [ ] show int g0/0.10 shows encapsulation dot1Q 10
- [ ] show int g0/0.20 shows encapsulation dot1Q 20
- [ ] show ip route shows two connected routes (10.0.10.0/24 and 10.0.20.0/24)
- [ ] ping from VLAN 10 to VLAN 20 succeeds
- [ ] ping from VLAN 20 to VLAN 10 succeeds

---

## Part 2: Troubleshooting Exercise

**Given Scenario:** A technician configured ROAS but inter-VLAN traffic is still blocked. You see this output:

```
Router# show int g0/0.10 | include (up|down)
GigabitEthernet0/0.10 is down, line protocol is down
```

**Questions (answer in your own words):**
1. What is the most likely cause of this state?
2. What single command might fix this?
3. Why would the parent interface status matter here?

**Next scenario:** Now g0/0.10 is up, but pings still fail:

```
Router# show ip route connected
C 10.0.10.0/24 is directly connected, GigabitEthernet0/0.10
C 10.0.20.0/24 is directly connected, GigabitEthernet0/0.20

Switch1# show int g0/1 switchport | include Allowed
Allowed Vlans: 1,10
```

4. What's wrong here and how do you fix it on the switch?

---

## Part 3: Design Scenario

**Context:** Your company has grown to four departments (Sales, Marketing, IT, Finance) with VLANs 10, 20, 30, 40 respectively. All traffic between departments must route through the router for security policy enforcement.

**Your questions:**
1. How many subinterfaces would you need on the router?
2. What would you name them for clarity?
3. Would ROAS still be a good choice, or should you recommend a different approach? Why?
4. If you added a second router for redundancy, how would you connect both routers to the switch network?

---

## Part 4: Prediction Exercise

For each scenario, predict the result before running it:

**Scenario A:** You create subinterface g0/0.30 with no shutdown, but parent interface g0/0 is administratively down.
- Prediction: Will g0/0.30 activate? Why or why not?
- Verification command: _________________

**Scenario B:** VLAN 10 on the switch is allowed on trunk port g0/1, but the router's g0/0.10 subinterface is configured with encapsulation dot1Q 11 instead of dot1Q 10.
- Prediction: Can a PC in VLAN 10 ping the router's g0/0.10 gateway IP?
- Why would this mismatch be problematic?

**Scenario C:** You configure g0/0.10 with IP 10.0.10.1 /24 and g0/0.20 with IP 10.0.10.2 /24 (same subnet by mistake).
- Prediction: What routing table entries would you see?
- What error might the router produce during configuration?

---

## Part 5: Self-Check Walkthrough

Complete this checklist after finishing the lab:

**Understanding:**
- [ ] I can explain why subinterfaces are needed instead of physical interfaces
- [ ] I know what 802.1Q encapsulation does
- [ ] I understand why the parent interface must be up
- [ ] I can predict what "show ip route" will show after ROAS config

**Hands-On Skills:**
- [ ] I configured multiple subinterfaces without syntax errors
- [ ] I verified subinterfaces with show commands
- [ ] I tested inter-VLAN ping successfully
- [ ] I can troubleshoot a broken ROAS setup

**Design Thinking:**
- [ ] I know when ROAS is appropriate vs. overkill
- [ ] I can explain the bottleneck of ROAS
- [ ] I thought about redundancy implications

---

## Part 6: Stretch Challenges

**Challenge 1 (Advanced Troubleshooting):**
After three weeks of operation, VLAN 10 suddenly cannot reach VLAN 20. The router shows:
```
GigabitEthernet0/0.10 is up, line protocol is down
GigabitEthernet0/0.20 is up, line protocol is up
```

What could cause line protocol to be down on one subinterface while the parent is up?

**Challenge 2 (Design Debate):**
Your manager asks: "Can we just add more subinterfaces to handle 50 VLANs?" Argue for or against ROAS at that scale, and propose an alternative.

**Challenge 3 (Redundancy):**
Design a ROAS setup with two routers, where both can route between VLANs but one is active. Draw the topology and explain how failover would work.

---

## Expected Outcomes

**After this practice lab, you should be able to:**
- [ ] Configure ROAS with multiple VLANs from a blank slate
- [ ] Explain the relationship between physical and subinterfaces
- [ ] Troubleshoot connectivity failures in a ROAS network
- [ ] Recommend when ROAS is the right solution
