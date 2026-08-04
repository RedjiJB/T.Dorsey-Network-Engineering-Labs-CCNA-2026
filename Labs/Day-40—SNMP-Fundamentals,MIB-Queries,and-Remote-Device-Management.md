# Day 40 — SNMP Fundamentals, MIB Queries, and Remote Device Management

## 📖 Overview

Today’s CCNA lab focused on **Simple Network Management Protocol (SNMP)** and how network administrators can remotely monitor and manage network devices.

In this lab, I configured SNMP community strings on a Cisco router, used the MIB Browser on PC1 to retrieve information from R1, and performed an SNMP `Set` operation to remotely change the router’s hostname.

Packet Tracer provides limited SNMP functionality, but the lab still demonstrated the core relationship between:

- SNMP managers
- SNMP agents
- Management Information Bases
- Object Identifiers
- Read-only access
- Read/write access
- SNMP Get operations
- SNMP Set operations

---

## 🖥️ Network Topology

The topology contains:

- One Cisco 2911 router named `R1`
- One Cisco 2960 switch
- One management workstation named `PC1`
- One IPv4 LAN using `192.168.1.0/24`
- R1 using `192.168.1.254`
- PC1 using `192.168.1.1`

PC1 acts as the **SNMP manager**, while R1 acts as the **SNMP agent**.

<p align="center">
  <a href="PASTE-DAY-40-TOPOLOGY-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP.png" alt="Day 40 SNMP Network Topology" width="1000">
  </a>
</p>

---

## 🎯 Lab Objectives

1. Configure a read-only SNMP community on R1.
2. Configure a read/write SNMP community on R1.
3. Use SNMP Get messages to retrieve information from R1.
4. Determine R1’s system uptime.
5. Retrieve the current hostname.
6. Determine how many interfaces R1 has.
7. Identify the names of those interfaces.
8. Explore other available MIB information.
9. Use an SNMP Set operation to remotely change R1’s hostname.

---

## 📋 Addressing Table

| Device | Interface | IPv4 Address | Role |
|---|---|---:|---|
| R1 | G0/0 | 192.168.1.254/24 | SNMP agent |
| PC1 | FastEthernet0 | 192.168.1.1/24 | SNMP manager |
| SW1 | Layer 2 switch | N/A | LAN connectivity |

---

# Phase 1 — Configure SNMP Communities on R1

Two SNMP community strings were configured on R1.

The first community provides **read-only access**:

```text
Cisco1
```

The second community provides **read/write access**:

```text
Cisco2
```

The Cisco IOS configuration was:

```cisco
R1>enable
R1#configure terminal

R1(config)#snmp-server community Cisco1 RO
R1(config)#snmp-server community Cisco2 RW
```

The configuration was verified with:

```cisco
R1(config)#do show running-config | section snmp
```

Expected output:

```text
snmp-server community Cisco1 RO
snmp-server community Cisco2 RW
```

The `RO` community allows the management station to retrieve information.

The `RW` community allows the management station to retrieve and modify supported information.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-1.1-IMAGE-LINK-HERE">
    <img src=" https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-1.1.png" alt="SNMP Community Configuration on R1" width="1000">
  </a>
</p>

---

# Phase 2 — Retrieve the Router Hostname

Using the MIB Browser on PC1, I queried the `sysName` object.

## Object Identifier

```text
1.3.6.1.2.1.1.5.0
```

## MIB Object

```text
sysName.0
```

The SNMP Get request returned:

```text
R1
```

This confirmed that the management workstation could remotely retrieve the hostname currently configured on the router.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-2.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-2.1.png" alt="SNMP Get Request for Router Hostname" width="1000">

  </a>
</p>

---

# Phase 3 — Retrieve the Router System Uptime

The `sysUpTime` object was queried from PC1.

## Object Identifier

```text
1.3.6.1.2.1.1.3.0
```

## MIB Object

```text
sysUpTime.0
```

The returned value was:

```text
10 hours, 28 minutes, 13 seconds
```

The value type was displayed as:

```text
TimeTicks
```

System uptime represents how long the SNMP agent has been operational since the device was last initialized or restarted.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-3.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-2.1.png" alt="SNMP Get Request for System Uptime" width="1000">
  </a>
</p>

---

# Phase 4 — Determine the Number of Interfaces

The `ifNumber` object was queried to determine the total number of interfaces recognized by R1.

## Object Identifier

```text
1.3.6.1.2.1.2.1.0
```

## MIB Object

```text
ifNumber.0
```

The returned value was:

```text
4
```

This indicated that R1 had four interfaces represented within the interface MIB table.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-4.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-2.2.png" alt="SNMP Get Request for Interface Count" width="1000">
  </a>
</p>

---

# Phase 5 — Identify the Router Interfaces

The interface description table was queried to identify the interfaces on R1.

## Object Identifier

```text
1.3.6.1.2.1.2.2.1.2
```

## MIB Object

```text
ifDescr
```

The returned interface names were:

```text
Vlan1
GigabitEthernet0/0
GigabitEthernet0/1
GigabitEthernet0/2
```

The response matched the value returned by `ifNumber`, confirming that four interfaces were present.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-5.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-2.3.png" alt="SNMP Interface Description Table" width="1000">
  </a>
</p>

---

# Phase 6 — Explore Additional MIB Information

The Packet Tracer MIB Browser allowed additional information to be explored within the standard MIB tree.

Available categories included:

```text
system
interfaces
ip
ospf
rip2
private
```

Examples of information that may be queried include:

- System description
- System uptime
- System contact
- System name
- System location
- Interface count
- Interface descriptions
- Interface types
- Interface speed
- Interface administrative status
- Interface operational status
- Interface IP information
- Routing-protocol information

One example was querying interface type information through the interface table.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-6.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-2.4.png" alt="Exploring Additional Interface MIB Information" width="1000">
  </a>
</p>

---

# Phase 7 — Change the Router Hostname with SNMP Set

The final portion of the lab used an SNMP `Set` operation to remotely modify R1’s hostname.

The target object was:

```text
sysName.0
```

The Object Identifier was:

```text
1.3.6.1.2.1.1.5.0
```

The value was changed from:

```text
R1
```

to:

```text
Router1
```

Because this operation modified information on the router, the read/write community string was required.

```text
Community: Cisco2
Access: Read/Write
Operation: Set
Data Type: OctetString
Value: Router1
```

<p align="center">
  <a href="PASTE-DAY-40-SNMP-7.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-3.1.png" alt="SNMP Set Operation Changing Router Hostname" width="1000">
  </a>
</p>

---

# Phase 8 — Verify the Hostname Change

After completing the SNMP Set operation, another SNMP Get request was sent for `sysName.0`.

The MIB Browser returned:

```text
Router1
```

The Cisco IOS CLI also changed from:

```text
R1>
```

to:

```text
Router1>
```

This confirmed that the SNMP Set operation successfully modified the hostname on the device.

<p align="center">
  <a href="PASTE-DAY-40-SNMP-8.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP-3.2.png" alt="Verification of Hostname Change Through SNMP" width="1000">
  </a>
</p>

---

## 🔍 SNMP Architecture

SNMP uses several important components.

### SNMP Manager

The manager is the centralized system that monitors or manages network devices.

In this lab:

```text
PC1 = SNMP Manager
```

### SNMP Agent

The agent is software running on the managed device.

It collects device information and responds to the manager.

In this lab:

```text
R1 = SNMP Agent
```

### Management Information Base

The **Management Information Base**, or MIB, organizes management information into a hierarchical database.

The manager uses the MIB to locate information about a device.

### Object Identifier

An **Object Identifier**, or OID, identifies a specific object inside the MIB.

Example:

```text
1.3.6.1.2.1.1.5.0
```

This OID identifies:

```text
sysName.0
```

---

## SNMP Get vs SNMP Set

| Operation | Purpose |
|---|---|
| Get | Retrieves information from a managed device |
| Set | Modifies a supported value on a managed device |
| GetNext | Retrieves the next object in the MIB |
| Trap | Allows an agent to notify a manager of an event |
| Inform | Sends an acknowledged notification |

This lab focused specifically on:

```text
Get
Set
```

---

## SNMP Community Access

| Community | Access Type | Purpose |
|---|---|---|
| Cisco1 | Read-only | Retrieve device information |
| Cisco2 | Read/write | Retrieve and modify supported values |

Community strings operate similarly to passwords in SNMPv1 and SNMPv2c.

In production environments, community strings should not use simple or predictable values.

---

## Important OIDs Used

| MIB Object | OID | Result |
|---|---|---|
| sysUpTime.0 | `1.3.6.1.2.1.1.3.0` | 10 hours, 28 minutes, 13 seconds |
| sysName.0 | `1.3.6.1.2.1.1.5.0` | R1, later changed to Router1 |
| ifNumber.0 | `1.3.6.1.2.1.2.1.0` | 4 |
| ifDescr | `1.3.6.1.2.1.2.2.1.2` | Interface names |

---

## 🛠️ Commands Practiced

### Configure SNMP Communities

```cisco
snmp-server community Cisco1 RO
snmp-server community Cisco2 RW
```

### Verify SNMP Configuration

```cisco
show running-config | section snmp
```

### Verify the Hostname

```cisco
show running-config | include hostname
```

---

## 📚 Skills Practiced

- SNMP fundamentals
- SNMP manager and agent roles
- Community-string configuration
- Read-only SNMP access
- Read/write SNMP access
- SNMP Get messages
- SNMP Set messages
- MIB navigation
- OID identification
- Remote device monitoring
- Remote configuration changes
- Interface inventory collection
- System uptime monitoring
- Cisco IOS verification
- Packet Tracer MIB Browser

---

## 🧠 Troubleshooting Notes

When SNMP queries fail, verify the following:

1. Confirm IP connectivity between the manager and agent.
2. Confirm the correct destination IP address.
3. Verify the SNMP community string.
4. Verify whether the community is read-only or read/write.
5. Confirm that SNMP is configured on the router.
6. Verify that the requested OID is supported.
7. Confirm that the correct SNMP operation is selected.
8. Verify the correct data type for Set operations.
9. Check whether the platform supports the requested MIB object.

Packet Tracer provides limited SNMP functionality, so not every production SNMP command, MIB object, or operation is available.

---

## 🎯 Key Takeaways

The biggest lesson from this lab was that SNMP allows administrators to retrieve device information without directly connecting to the CLI.

Using SNMP Get requests, I was able to remotely identify:

- The router hostname
- The system uptime
- The total number of interfaces
- The names of each interface

Using an SNMP Set request, I was also able to change the hostname remotely.

The key distinction is:

```text
SNMP Get retrieves information.
SNMP Set modifies information.
```

This lab also reinforced why permissions matter. Read-only communities should be used for monitoring, while read/write access should be tightly controlled because it can modify device settings.

---

## 🔐 Security Note

SNMPv1 and SNMPv2c use community strings without strong encryption.

In a production environment, **SNMPv3** is preferred because it can provide:

- Authentication
- Message integrity
- Encryption
- User-based access controls

The community strings used in this lab were intentionally simple for demonstration purposes and should not be used in production.

---

## ✅ Lab Status

**Day 40 Complete**

### Topics Covered

- SNMP
- SNMP manager
- SNMP agent
- Community strings
- SNMP Get
- SNMP Set
- MIB
- OIDs
- System uptime
- Interface monitoring
- Remote device management
- Cisco IOS
