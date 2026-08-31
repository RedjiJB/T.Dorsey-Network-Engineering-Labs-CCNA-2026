# Day 12: Spanning Tree Protocol - Practice Lab

## Section 0: Before You Start
**Time Budget:** 120 minutes | **Grading:** Excellent (90%+): All ports in correct roles, convergence < 80 sec, documented design

---

## Section 1: The Brief

**Client:** Multi-building company with 3 switches and redundant links. Prevent bridging loops while maintaining failover.

**Tasks:**
1. Identify which switch should be root (most central location)
2. Calculate port costs and predict blocked ports
3. Configure STP to match topology
4. Test failover (simulate link failure, verify recovery)

---

## Section 2-4: Design Your Spanning Tree Topology

**Questions:**
1. Which switch location should be root bridge? (Hint: central, reliable, high-capacity)
2. Should secondary root be in Building B or Building C?
3. What port cost values would optimize traffic flow? (Default: 1Gbps = 4, Fast = 19)

---

## Section 5-6: Implement STP - HOW-TO

### Step 1: Enable STP on All Switches

```bash
SW01# configure terminal
SW01(config)# spanning-tree mode pvst
SW01(config)# end

# Repeat on SW02 and SW03
```

### Step 2: Set Root Bridge (SW01)

```bash
SW01# configure terminal
SW01(config)# spanning-tree vlan 10,20,30,99 priority 4096
SW01(config)# exit
```

### Step 3: Set Secondary Root (SW02)

```bash
SW02# configure terminal
SW02(config)# spanning-tree vlan 10,20,30,99 priority 8192
SW02(config)# exit
```

### Step 4: Configure PortFast on Access Ports

```bash
SW01# configure terminal
SW01(config)# interface range fastethernet 0/1 - 7
SW01(config-if-range)# spanning-tree portfast
SW01(config-if-range)# spanning-tree bpduguard enable
SW01(config-if-range)# no shutdown
SW01(config-if-range)# exit
SW01(config)# end

# Repeat on SW02, SW03
```

### Step 5: Verify STP Status

```bash
SW01# show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol ieee
  Root ID    Priority    4106
             Address     0018.baaa.0001
             This bridge is the root

  Interface        Role Sts Cost      Prio.Nbr Type
  -----------      ---- --- --------- -------- ----
  Gi0/1            Desg FWD 4         128.1    P2p
  Gi0/2            Desg FWD 4         128.2    P2p
```

---

## Troubleshooting Scenarios

### Scenario: Port Stuck in Blocking

**Symptom:** Show spanning-tree shows port in "BLK" state permanently

**Solution:**
1. Check if this is expected (topology should have some blocked ports for loop prevention)
2. Verify port cost: `show interfaces gigabitethernet 0/1 spanning-tree`
3. Adjust cost if needed to prefer different path

### Scenario: Wrong Root Bridge Elected

**Symptom:** SW03 became root instead of SW01

**Solution:** Check priority values: `show spanning-tree vlan 10`
- SW01 priority should be 4096 (lowest = root)
- Re-apply priority if configuration didn't save

---

## Section 6: Explain Your Design

**Technical Memo Questions:**

1. **Why is SW01 the best root bridge?** (Central location, best redundancy, etc.)

2. **What is the purpose of PortFast on access ports?** (Skips listening/learning delays)

3. **How long does convergence take with 802.1D?** (80+ seconds = 20s listening + 15s learning × 2)

4. **What happens when you disconnect the link between SW01 and SW02?** (STP reconverges, previously blocked port becomes forwarding)

---

**Lab Completion Time:** 120 minutes

