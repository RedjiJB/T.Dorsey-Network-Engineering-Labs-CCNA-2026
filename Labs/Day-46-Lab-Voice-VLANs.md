# Day 46 — Voice VLANs & Router-on-a-Stick (ROAS)

## Overview

Day 46 focused on combining **data VLANs and voice VLANs on the same physical switch ports**.

The topology uses Cisco IP phones with PCs connected through the phones. This creates an important distinction:

- PC traffic belongs to **VLAN 10**
- Voice traffic belongs to **VLAN 20**
- The switch port carries both traffic types
- PC traffic is sent untagged on the access VLAN
- Voice traffic is tagged with an **802.1Q VLAN ID**
- Router-on-a-Stick provides Layer 3 routing between the VLANs

This lab also used Packet Tracer Simulation Mode to inspect Ethernet frames and verify when an **802.1Q tag** is actually present.

---

## Network Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs.png" alt="Day 46 Voice VLANs Topology" width="900">
</p>

### VLAN Addressing

| VLAN | Purpose | Network |
|---|---|---|
| VLAN 10 | Data | 192.168.10.0/24 |
| VLAN 20 | Voice | 192.168.20.0/24 |

### End Devices

| Device | Role |
|---|---|
| PC1 | Data endpoint |
| PC2 | Data endpoint |
| PH1 | IP Phone |
| PH2 | IP Phone |
| SW1 | Layer 3 capable switch used for VLAN connectivity |
| R1 | Router providing ROAS |

---

## Lab Objectives

1. Configure SW1's interfaces in the appropriate VLANs.

2. Configure Router-on-a-Stick between SW1 and R1.

3. In Simulation Mode, ping PC2 from PC1.
   - Determine whether the traffic is tagged with a VLAN ID.

4. In Simulation Mode, call PH1 from PH2.
   - Determine whether the voice traffic is tagged with a VLAN ID.

---

## Step 1 — Configure the Data and Voice VLANs

The PCs belong to VLAN 10.

The IP phones belong to VLAN 20.

The switch ports connected to the phones therefore need both:

```cisco
switchport access vlan 10
switchport voice vlan 20
```

This configuration allows a single physical switch interface to support:

```text
PC traffic   → VLAN 10
Voice traffic → VLAN 20
```

---

## Step 2 — Configure SW1 Access Ports

The first phone and PC pair connects to `GigabitEthernet1/0/2`.

```cisco
SW1(config)# interface g1/0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport voice vlan 20
```

The second phone and PC pair connects to `GigabitEthernet1/0/3`.

```cisco
SW1(config)# interface g1/0/3
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport voice vlan 20
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-1.1.png" alt="Day 46 SW1 Voice VLAN Configuration" width="900">
</p>

---

## Step 3 — Verify the Voice VLAN Configuration

I verified the switch port configuration.

The relevant information showed:

```text
Access Mode VLAN: 10
Voice VLAN: 20
```

This confirmed that the ports were carrying:

```text
Data → VLAN 10
Voice → VLAN 20
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-1.2.png" alt="Day 46 Voice VLAN Verification" width="900">
</p>

The important configuration concept is:

```cisco
switchport access vlan 10
switchport voice vlan 20
```

Both traffic types use the same physical switch port, but they are logically separated.

---

## Step 4 — Configure the Trunk Toward R1

The connection between SW1 and R1 must carry traffic for both VLAN 10 and VLAN 20.

I configured the switch-facing router connection as a trunk.

```cisco
SW1(config)# interface g1/0/1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20
```

Verification:

```cisco
SW1# show interfaces trunk
```

The trunk allows:

```text
VLAN 10
VLAN 20
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-2.1.png" alt="Day 46 Trunk Configuration" width="900">
</p>

---

## Step 5 — Configure Router-on-a-Stick

R1 uses subinterfaces to provide Layer 3 gateways for the two VLANs.

### VLAN 10 Subinterface

```cisco
R1(config)# interface f0/0.1
R1(config-subif)# encapsulation dot1q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
```

### VLAN 20 Subinterface

```cisco
R1(config)# interface f0/0.2
R1(config-subif)# encapsulation dot1q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
```

The physical interface must also be enabled.

```cisco
R1(config)# interface f0/0
R1(config-if)# no shutdown
```

---

## Step 6 — Verify the Router Subinterfaces

I verified the subinterfaces on R1.

The VLAN 10 subinterface showed:

```text
Internet address is 192.168.10.1/24
Encapsulation 802.1Q Virtual LAN, VLAN ID 10
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-2.2.png" alt="Day 46 VLAN 10 Router Subinterface" width="900">
</p>

The VLAN 20 subinterface showed:

```text
Internet address is 192.168.20.1/24
Encapsulation 802.1Q Virtual LAN, VLAN ID 20
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-2.3.png" alt="Day 46 VLAN 20 Router Subinterface" width="900">
</p>

At this point R1 can route between:

```text
192.168.10.0/24
192.168.20.0/24
```

---

## Step 7 — PC Traffic Simulation

The next step was to inspect traffic from PC1 to PC2 in Packet Tracer Simulation Mode.

Both PCs belong to:

```text
VLAN 10
```

I initiated traffic from PC1 to PC2 and inspected the Layer 2 frame.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-3.1.png" alt="Day 46 PC Traffic Simulation" width="900">
</p>

The PDU displayed a normal:

```text
Ethernet II Header
```

There was no 802.1Q header shown for the frame entering the switch from the PC/phone access port.

### Is PC traffic tagged with a VLAN ID?

**No — the PC-generated traffic is untagged when it enters the switch.**

The switch knows that untagged traffic arriving on this port belongs to VLAN 10 because of:

```cisco
switchport access vlan 10
```

Conceptually:

```text
PC1
 ↓
untagged Ethernet frame
 ↓
IP Phone
 ↓
SW1 access port
 ↓
SW1 associates frame with VLAN 10
```

The PC itself does not need to understand VLAN tagging.

---

## Step 8 — Voice Traffic Simulation

Next, I initiated a phone call from PH2 to PH1.

The IP phones are assigned to:

```text
VLAN 20
```

I inspected the frame in Simulation Mode.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs-4.1.png" alt="Day 46 Voice VLAN Tagged Traffic" width="900">
</p>

This time Packet Tracer displayed:

```text
Dot1q Header
```

This confirms that the voice traffic contains an **802.1Q VLAN tag**.

### Is the phone traffic tagged with a VLAN ID?

**Yes.**

The IP phone tags its voice traffic for VLAN 20 before sending it toward the switch.

Conceptually:

```text
PH2
 ↓
802.1Q tagged frame
VLAN ID = 20
 ↓
SW1
```

---

## Why PC Traffic and Voice Traffic Behave Differently

The switch port is effectively carrying two logical networks.

```text
                  Switch Port
                      │
             ┌────────┴────────┐
             │                 │
          VLAN 10           VLAN 20
           Data              Voice
             │                 │
         Untagged           802.1Q
             │               Tagged
             │                 │
            PC              IP Phone
```

### PC Traffic

PC traffic uses:

```cisco
switchport access vlan 10
```

The PC sends ordinary Ethernet frames.

The switch assigns those frames to VLAN 10 based on the access-port configuration.

### Voice Traffic

Voice traffic uses:

```cisco
switchport voice vlan 20
```

The phone understands VLAN tagging and sends voice frames using an 802.1Q header identifying VLAN 20.

---

## Why Voice VLANs Are Useful

Without a voice VLAN, PC and phone traffic would share the same Layer 2 broadcast domain.

Voice VLANs allow the network to logically separate:

```text
User Data
and
VoIP Traffic
```

even though both devices can share the same physical switch interface.

This allows administrators to apply different policies to voice traffic, including:

- QoS
- Security policies
- DHCP options
- Access control
- Traffic monitoring
- Separate IP addressing
- Voice-specific network services

---

## Router-on-a-Stick Operation

Router-on-a-Stick allows a router to route multiple VLANs using a single physical interface.

Instead of requiring one physical interface for every VLAN:

```text
VLAN 10 → Router Interface 1
VLAN 20 → Router Interface 2
```

ROAS uses logical subinterfaces:

```text
F0/0
 ├── F0/0.1 → VLAN 10
 └── F0/0.2 → VLAN 20
```

Each subinterface has its own:

```text
802.1Q VLAN ID
IP address
Layer 3 gateway
```

---

## Packet Flow — PC Traffic

PC1 sends traffic toward PC2.

```text
PC1
192.168.10.11
        │
        ▼
PH1
        │
        │ Untagged
        ▼
SW1 G1/0/2
Access VLAN 10
        │
        ▼
SW1
        │
        ▼
PH2
        │
        ▼
PC2
192.168.10.12
```

Because both PCs are in VLAN 10, the traffic can remain within the same Layer 2 VLAN.

---

## Packet Flow — Voice Traffic

PH2 sends voice traffic toward PH1.

```text
PH2
 │
 │ 802.1Q
 │ VLAN 20
 ▼
SW1
 │
 │ VLAN 20
 ▼
PH1
```

The phone adds the VLAN tag itself.

Packet Tracer confirmed this by displaying:

```text
Dot1q Header
```

in the PDU information.

---

## Important Commands

### Create VLANs

```cisco
vlan 10
vlan 20
```

### Configure Data VLAN

```cisco
interface g1/0/2
 switchport mode access
 switchport access vlan 10
```

### Configure Voice VLAN

```cisco
interface g1/0/2
 switchport voice vlan 20
```

### Configure Both on Another Port

```cisco
interface g1/0/3
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
```

### Configure Trunk

```cisco
interface g1/0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

### Configure VLAN 10 ROAS Subinterface

```cisco
interface f0/0.1
 encapsulation dot1q 10
 ip address 192.168.10.1 255.255.255.0
```

### Configure VLAN 20 ROAS Subinterface

```cisco
interface f0/0.2
 encapsulation dot1q 20
 ip address 192.168.20.1 255.255.255.0
```

### Verify Switch Port

```cisco
show interfaces switchport
```

### Verify Trunk

```cisco
show interfaces trunk
```

### Verify Router Subinterfaces

```cisco
show ip interface brief
```

```cisco
show interfaces f0/0.1
```

```cisco
show interfaces f0/0.2
```

---

## Key Takeaways

### One Physical Port Can Carry Two VLANs

An IP phone allows a PC and phone to share one physical switch port while remaining in separate VLANs.

```text
PC    → VLAN 10
Phone → VLAN 20
```

### Data Traffic Is Untagged

The PC sends normal Ethernet frames.

The switch associates the untagged traffic with the configured access VLAN.

```text
switchport access vlan 10
```

### Voice Traffic Is Tagged

The IP phone tags its own traffic using 802.1Q.

```text
switchport voice vlan 20
```

Packet Tracer confirmed this by showing a:

```text
Dot1q Header
```

for the voice traffic.

### Router-on-a-Stick Provides Inter-VLAN Routing

R1 uses subinterfaces to route between the two networks.

```text
F0/0.1 → VLAN 10 → 192.168.10.1
F0/0.2 → VLAN 20 → 192.168.20.1
```

### VLAN Tags Exist Where They Are Needed

A major lesson from this lab was that traffic is not automatically tagged simply because it belongs to a VLAN.

The VLAN tag depends on the type of link.

```text
PC → Switch
Untagged

Phone Voice Traffic → Switch
Tagged

Switch → Router Trunk
Tagged
```

---

## What I Practiced

- Voice VLANs
- Data VLANs
- Cisco IP phone switch ports
- `switchport access vlan`
- `switchport voice vlan`
- Access ports
- 802.1Q tagging
- VLAN IDs
- Trunk links
- Allowed VLAN lists
- Router-on-a-Stick
- Router subinterfaces
- Inter-VLAN routing
- Packet Tracer Simulation Mode
- Ethernet II frame inspection
- 802.1Q frame inspection
- Voice vs data traffic behavior
- Layer 2 packet analysis

---

## Final Result

- ✅ Configured VLAN 10 for data traffic
- ✅ Configured VLAN 20 for voice traffic
- ✅ Configured SW1 access ports
- ✅ Configured voice VLANs
- ✅ Configured the SW1-to-R1 trunk
- ✅ Allowed VLANs 10 and 20 across the trunk
- ✅ Configured ROAS on R1
- ✅ Configured VLAN 10 router subinterface
- ✅ Configured VLAN 20 router subinterface
- ✅ Verified router subinterfaces
- ✅ Tested PC-to-PC traffic in Simulation Mode
- ✅ Confirmed PC traffic entered the switch untagged
- ✅ Tested phone traffic in Simulation Mode
- ✅ Confirmed voice traffic used an 802.1Q VLAN tag
- ✅ Observed the Dot1q header directly in Packet Tracer

---

## Day 46 Complete

**Voice VLANs & Router-on-a-Stick ✅**

The biggest takeaway from this lab was seeing the difference between **data traffic and voice traffic on the exact same physical switch port**.

The PC can send ordinary untagged Ethernet frames while the IP phone tags its voice traffic for VLAN 20.

The switch separates both traffic types logically:

```text
Untagged PC Traffic → Access VLAN 10
Tagged Voice Traffic → Voice VLAN 20
```

Then Router-on-a-Stick allows the separate VLANs to communicate at Layer 3.

Seeing the actual `Dot1q Header` in Simulation Mode made the difference between an access VLAN, voice VLAN, and tagged trunk traffic much easier to visualize.
