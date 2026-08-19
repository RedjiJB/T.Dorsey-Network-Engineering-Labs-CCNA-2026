# Day 52 Complete — STP & HSRP Synchronization

**Status:** ✅ Complete  
**Lab:** Jeremy's IT Lab — Day 52  
**Topic:** HSRP & Spanning Tree Protocol Synchronization  
**Exam Relevance:** CCNA 200-301

---

## Objective

Configure **HSRP on DSW1 and DSW2** while synchronizing the HSRP active router with the **STP root bridge** for VLANs 10 and 20.

The goal is to make sure traffic follows the most efficient Layer 2 and Layer 3 path.

### Requirements

### VLAN 10

- DSW1 = HSRP Active
- DSW1 = STP Root
- DSW2 = HSRP Standby
- DSW2 = STP Secondary Root

### VLAN 20

- DSW2 = HSRP Active
- DSW2 = STP Root
- DSW1 = HSRP Standby
- DSW1 = STP Secondary Root

---

## Topology

```text
                         G1/0/3
              DSW1 ================= DSW2
               |  \                   / |
               |   \                 /  |
          G1/0/1    \ G1/0/2 G1/0/2/   G1/0/1
               |     \             /    |
               |      \           /     |
              G0/1     \         /     G0/1
               |        \       /        |
              ASW1       \     /        ASW2
               |                         |
              PC1                       PC2
               |                         |
            VLAN 10                   VLAN 20
          10.0.10.10                10.0.20.10
```

### SVI Addressing

```text
DSW1 VLAN 10/20 SVI → .1
DSW2 VLAN 10/20 SVI → .2
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-52-Lab-STP-%26-HSRP-Synchronization.png" width="900">
</p>

---

## Skills Practiced

- Configuring HSRP
- Configuring HSRP virtual IP addresses
- Manipulating HSRP priority
- Understanding HSRP active and standby routers
- Configuring STP root bridges
- Configuring STP secondary root bridges
- Synchronizing Layer 2 and Layer 3 redundancy
- Load balancing between distribution switches
- Verifying HSRP state
- Verifying STP root bridge placement

---

# Part 1 — Understanding the Design

The network contains two distribution switches:

```text
DSW1
DSW2
```

Both switches provide redundant paths for the access layer.

Instead of making one distribution switch responsible for both VLANs, the network divides responsibility.

```text
VLAN 10 → DSW1 preferred
VLAN 20 → DSW2 preferred
```

This creates a basic form of load balancing.

---

# Part 2 — HSRP

HSRP provides **default gateway redundancy**.

Instead of PCs using the physical SVI address of DSW1 or DSW2 as their gateway, they use an HSRP **virtual IP address**.

Conceptually:

```text
                    Virtual Gateway
                         |
                    HSRP Virtual IP
                      /         \
                     /           \
                  DSW1           DSW2
                 Active         Standby
```

If the active router fails, the standby router can take over the virtual gateway.

---

# Part 3 — Configure VLAN 10 HSRP

For VLAN 10:

```text
DSW1 = Active
DSW2 = Standby
```

DSW1 should therefore have the higher HSRP priority.

## DSW1

```cisco
enable
configure terminal

interface vlan 10
 standby 1 ip 10.0.10.254
 standby 1 priority 110
 standby 1 preempt

end
```

## DSW2

```cisco
enable
configure terminal

interface vlan 10
 standby 1 ip 10.0.10.254
 standby 1 priority 100
 standby 1 preempt

end
```

The hosts in VLAN 10 can use:

```text
10.0.10.254
```

as their default gateway.

---

# Part 4 — Configure VLAN 20 HSRP

For VLAN 20:

```text
DSW2 = Active
DSW1 = Standby
```

DSW2 receives the higher priority.

## DSW1

```cisco
configure terminal

interface vlan 20
 standby 2 ip 10.0.20.254
 standby 2 priority 100
 standby 2 preempt

end
```

## DSW2

```cisco
configure terminal

interface vlan 20
 standby 2 ip 10.0.20.254
 standby 2 priority 110
 standby 2 preempt

end
```

The hosts in VLAN 20 can use:

```text
10.0.20.254
```

as their default gateway.

---

# Part 5 — Synchronize STP with HSRP

HSRP controls the preferred **Layer 3 gateway**.

STP controls the preferred **Layer 2 forwarding path**.

These should be synchronized.

For VLAN 10:

```text
HSRP Active = DSW1
STP Root    = DSW1
```

For VLAN 20:

```text
HSRP Active = DSW2
STP Root    = DSW2
```

This avoids unnecessarily sending traffic across the link between DSW1 and DSW2.

---

# Part 6 — Configure STP for VLAN 10

DSW1 should be the root bridge.

## DSW1

```cisco
configure terminal

spanning-tree vlan 10 root primary

end
```

DSW2 should be the secondary root.

## DSW2

```cisco
configure terminal

spanning-tree vlan 10 root secondary

end
```

The resulting design is:

```text
VLAN 10

        DSW1
    HSRP ACTIVE
      STP ROOT
         |
         |
        ASW1
         |
        PC1
```

---

# Part 7 — Configure STP for VLAN 20

DSW2 should be the root bridge.

## DSW2

```cisco
configure terminal

spanning-tree vlan 20 root primary

end
```

DSW1 should be the secondary root.

## DSW1

```cisco
configure terminal

spanning-tree vlan 20 root secondary

end
```

The resulting design is:

```text
VLAN 20

        DSW2
    HSRP ACTIVE
      STP ROOT
         |
         |
        ASW2
         |
        PC2
```

---

# Part 8 — Verify DSW1

Use:

```cisco
show standby
show spanning-tree vlan 10
show spanning-tree vlan 20
```

For VLAN 10, DSW1 shows:

```text
State is Active
Active router is local
```

DSW1 is also the STP root for VLAN 10:

```text
This bridge is the root
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-52-Lab-STP-%26-HSRP-Synchronization-1.1.png" width="900">
</p>

---

# Part 9 — Verify DSW2

For VLAN 20, DSW2 shows:

```text
State is Active
Active router is local
```

DSW2 is also the STP root for VLAN 20:

```text
This bridge is the root
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-52-Lab-STP-%26-HSRP-Synchronization-1.2.png" width="900">
</p>

---

# Part 10 — Verify STP Synchronization

### DSW1 VLAN 20

DSW1 should NOT be the VLAN 20 root.

Instead, DSW2 is the root bridge.

```cisco
show spanning-tree vlan 20
```

The output identifies a root port leading toward DSW2.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-52-Lab-STP-%26-HSRP-Synchronization-2.1.png" width="900">
</p>

---

### DSW2 VLAN 20

DSW2 confirms:

```text
This bridge is the root
```

and HSRP confirms:

```text
State is Active
Active router is local
```

Therefore:

```text
VLAN 20

HSRP Active = DSW2
STP Root    = DSW2

SYNCHRONIZED ✅
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-52-Lab-STP-%26-HSRP-Synchronization-2.2.png" width="900">
</p>

---

# Final Configuration

## DSW1

```cisco
enable
configure terminal

interface vlan 10
 standby 1 ip 10.0.10.254
 standby 1 priority 110
 standby 1 preempt

interface vlan 20
 standby 2 ip 10.0.20.254
 standby 2 priority 100
 standby 2 preempt

spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary

end
```

---

## DSW2

```cisco
enable
configure terminal

interface vlan 10
 standby 1 ip 10.0.10.254
 standby 1 priority 100
 standby 1 preempt

interface vlan 20
 standby 2 ip 10.0.20.254
 standby 2 priority 110
 standby 2 preempt

spanning-tree vlan 10 root secondary
spanning-tree vlan 20 root primary

end
```

---

# Verification Commands

### Check HSRP

```cisco
show standby
```

or:

```cisco
show standby brief
```

### Check VLAN 10 STP

```cisco
show spanning-tree vlan 10
```

### Check VLAN 20 STP

```cisco
show spanning-tree vlan 20
```

### Check SVI Configuration

```cisco
show ip interface brief
```

---

# Expected Final State

| VLAN | HSRP Active | HSRP Standby | STP Root | STP Secondary |
|---|---|---|---|---|
| VLAN 10 | DSW1 | DSW2 | DSW1 | DSW2 |
| VLAN 20 | DSW2 | DSW1 | DSW2 | DSW1 |

This is the key result of the lab.

---

# Why Synchronization Matters

Imagine VLAN 10 had:

```text
HSRP Active → DSW1
STP Root    → DSW2
```

A host connected through the access layer might need to send traffic:

```text
PC
 |
ASW
 |
DSW2 ← STP preferred path
 |
DSW1 ← HSRP active gateway
 |
Destination
```

Traffic crosses an unnecessary distribution link.

When HSRP and STP are synchronized:

```text
PC
 |
ASW
 |
DSW1
 |
HSRP Gateway
```

The forwarding path is more efficient.

---

# Load Balancing Between DSW1 and DSW2

The final configuration also distributes traffic between the two distribution switches.

```text
                VLAN 10
                   |
                   v
             +-----------+
             |   DSW1    |
             | HSRP ACT  |
             | STP ROOT  |
             +-----------+


                VLAN 20
                   |
                   v
             +-----------+
             |   DSW2    |
             | HSRP ACT  |
             | STP ROOT  |
             +-----------+
```

Instead of one switch being preferred for every VLAN:

```text
DSW1 handles VLAN 10
DSW2 handles VLAN 20
```

Both distribution switches actively participate in forwarding traffic.

---

# HSRP Election

HSRP uses priority to determine the active router.

Default priority:

```text
100
```

Higher priority wins:

```text
DSW1 Priority 110
DSW2 Priority 100

DSW1 → ACTIVE
DSW2 → STANDBY
```

The `preempt` command allows the higher-priority router to reclaim the active role after returning online.

```cisco
standby 1 preempt
```

---

# STP Root Election

STP elects the switch with the lowest Bridge ID.

Lower STP priority is preferred.

Instead of manually calculating the exact priority, Cisco provides:

```cisco
spanning-tree vlan 10 root primary
```

and:

```cisco
spanning-tree vlan 10 root secondary
```

This makes the intended root placement much easier to configure.

---

# HSRP vs STP

| HSRP | STP |
|---|---|
| Layer 3 redundancy | Layer 2 redundancy |
| Protects default gateway availability | Prevents Layer 2 loops |
| Elects Active/Standby routers | Elects Root Bridge |
| Uses virtual IP/MAC | Uses Bridge IDs |
| Higher HSRP priority preferred | Lower STP priority preferred |

The important design principle from this lab is:

```text
HSRP ACTIVE
     =
STP ROOT
```

for the preferred VLAN path.

---

# Key Commands

### HSRP Virtual Gateway

```cisco
standby 1 ip 10.0.10.254
```

### HSRP Priority

```cisco
standby 1 priority 110
```

### HSRP Preemption

```cisco
standby 1 preempt
```

### STP Root

```cisco
spanning-tree vlan 10 root primary
```

### STP Backup Root

```cisco
spanning-tree vlan 10 root secondary
```

### Verify HSRP

```cisco
show standby
```

### Verify STP

```cisco
show spanning-tree vlan 10
```

---

# Lessons Learned

## 1. HSRP Provides Gateway Redundancy

Hosts use a virtual default gateway rather than depending on one physical Layer 3 switch.

```text
PC
 |
 | Default Gateway
 v
HSRP Virtual IP
 |
 +---- DSW1
 |
 +---- DSW2
```

---

## 2. STP and HSRP Should Be Synchronized

The preferred Layer 2 path should lead toward the preferred Layer 3 gateway.

```text
HSRP Active = STP Root
```

---

## 3. Different VLANs Can Prefer Different Switches

VLAN 10:

```text
DSW1 → Active / Root
DSW2 → Standby / Secondary
```

VLAN 20:

```text
DSW2 → Active / Root
DSW1 → Standby / Secondary
```

This distributes forwarding responsibility across both switches.

---

## 4. HSRP and STP Use Opposite Priority Logic

For HSRP:

```text
HIGHER priority wins
```

For STP:

```text
LOWER priority wins
```

This is an important distinction to remember.

---

## 5. Redundancy Should Also Be Efficient

Having redundant links and gateways is only part of good network design.

The Layer 2 and Layer 3 protocols should work together so normal traffic follows the most efficient path while backup paths remain available.

---

# Final Verification

The completed lab successfully demonstrated:

- ✅ HSRP configured on DSW1 and DSW2
- ✅ VLAN 10 gateway redundancy configured
- ✅ VLAN 20 gateway redundancy configured
- ✅ DSW1 active for VLAN 10
- ✅ DSW2 standby for VLAN 10
- ✅ DSW2 active for VLAN 20
- ✅ DSW1 standby for VLAN 20
- ✅ DSW1 configured as VLAN 10 STP root
- ✅ DSW2 configured as VLAN 10 secondary root
- ✅ DSW2 configured as VLAN 20 STP root
- ✅ DSW1 configured as VLAN 20 secondary root
- ✅ HSRP and STP synchronized
- ✅ Distribution-layer load balancing implemented
- ✅ HSRP verified with `show standby`
- ✅ STP verified with `show spanning-tree`

---

# Day 52 Complete ✅

**STP & HSRP Synchronization — First-Hop Redundancy, Root Bridge Placement & Distribution-Layer Load Balancing**
