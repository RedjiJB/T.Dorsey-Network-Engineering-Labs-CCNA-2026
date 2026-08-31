# Day 11: Inter-VLAN Routing - Practice Lab

## Section 0: Before You Start
**Time Budget:** 120 minutes | **Grading:** Excellent (90%+): All VLANs routable, cross-VLAN ping success, documented design

---

## Section 1: The Brief

**Client:** Horizon Financial Services

Your assignment: Enable the Finance department (VLAN 20, Building B) to communicate with Accounting department (VLAN 10, Building A) via shared database server. Operations (VLAN 30) should be able to access Finance systems with controlled routing. Executive VLAN (10) should remain isolated from Operations and Finance for security audit compliance.

---

## Section 2-3: Design Your Routing Architecture

**Questions to Answer:**
1. Should Executive VLAN (10) route to Finance (20)? Why/why not?
2. What router IP addresses will you assign to each VLAN gateway?
3. Should all departments share one router or use separate routers per VLAN? (Hint: one router with multiple subinterfaces)
4. Will you implement any static routes to control routing behavior?

---

## Section 4: Implement Router Configuration - HOW-TO

### Step 1: Configure Physical Interface

```bash
Router# configure terminal

! Bring up physical Gigabit interface
Router(config)# interface gigabitethernet 0/0/0
Router(config-if)# description Trunk Link to Switches
Router(config-if)# no shutdown
Router(config-if)# exit

! Verify interface is up
Router# show interfaces gigabitethernet 0/0/0 | include "is up"
```

### Step 2: Create Subinterface for VLAN 10 (Accounting)

```bash
Router(config)# interface gigabitethernet 0/0/0.10
Router(config-subif)# encapsulation dot1q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0
Router(config-subif)# description Accounting Gateway - VLAN 10
Router(config-subif)# no shutdown
Router(config-subif)# exit

! Verify VLAN 10 subinterface
Router# show interfaces gigabitethernet 0/0/0.10 | include "Encapsulation|Internet"
```

### Step 3: Create Subinterfaces for VLANs 20, 30, 99

(Repeat pattern for VLAN 20 at 192.168.20.1, VLAN 30 at 192.168.30.1, VLAN 99 at 192.168.99.1)

### Step 4: Save and Verify

```bash
Router(config)# end
Router# copy running-config startup-config

! Show all subinterfaces
Router# show ip interface brief | include 0/0/0
```

---

## Section 5: Testing & Verification

### Test 1: Ping Router from Each VLAN

```bash
PC01 (VLAN 10)> ping 192.168.10.1

Sending 5, 100-byte ICMP Echoes to 192.168.10.1:
.....
Success rate is 100 percent (5/5) ✓
```

### Test 2: Cross-VLAN Ping

```bash
PC03 (VLAN 20, Finance)> ping 192.168.10.10 (Accounting)

Sending 5, 100-byte ICMP Echoes to 192.168.10.10:
.....
Success rate is 100 percent (5/5) ✓
```

### Test 3: Verify Routing Table

```bash
Router# show ip route

Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP

C    192.168.10.0/24 is directly connected, GigabitEthernet0/0/0.10
C    192.168.20.0/24 is directly connected, GigabitEthernet0/0/0.20
C    192.168.30.0/24 is directly connected, GigabitEthernet0/0/0.30
C    192.168.99.0/24 is directly connected, GigabitEthernet0/0/0.99
```

---

## Section 6: Explain Your Design

**Write a Technical Memo:**

1. **Why use subinterfaces vs. separate physical interfaces?**
   - Answer: _________________________

2. **What does "encapsulation dot1q 10" do?**
   - Answer: Tells subinterface to accept frames tagged with VLAN 10 from trunk

3. **Could you use a single IP address for all VLANs?**
   - Answer: No, each VLAN needs separate subnet for IP routing

4. **What happens if you forgot to configure VLAN 99 subinterface?**
   - Answer: _________________________

5. **When would you upgrade from router-on-stick to Layer 3 switch?**
   - Answer: When you need more than ~50 VLANs or want VLAN switching at wire speed

---

**Lab Completion Time:** 120 minutes

