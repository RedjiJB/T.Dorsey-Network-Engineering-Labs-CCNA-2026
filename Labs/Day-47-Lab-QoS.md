# Day 47 — Quality of Service (QoS), DSCP Marking & Traffic Classification

## Overview

Day 47 focused on **Quality of Service (QoS)** and how routers can classify, mark, and prioritize different types of network traffic.

The lab used three traffic types:

- HTTPS
- HTTP
- ICMP

Each traffic class was assigned a different **DSCP marking** and bandwidth policy.

The policy was then applied outbound on R1's `G0/0/0` interface.

Packet Tracer Simulation Mode was used to inspect the packets and verify that the DSCP values changed depending on the type of traffic being generated.

> QoS configuration itself is not a CCNA exam configuration topic, but understanding QoS concepts, traffic classification, marking, and DSCP values is useful for understanding how enterprise networks prioritize traffic.

---

## Network Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS.png" alt="Day 47 QoS Topology" width="900">
</p>

### Addressing

| Device | Interface | Address |
|---|---|---|
| PC1 | NIC | 192.168.0.10/24 |
| R1 | G0/0/1 | 192.168.0.1/24 |
| R1 | G0/0/0 | 172.16.0.1/30 |
| R2 | G0/0/0 | 172.16.0.2/30 |
| R2 | G0/0/1 | 10.0.0.1/24 |
| SRV1 | NIC | 10.0.0.100/24 |

The QoS policy is applied outbound from:

```text
R1 G0/0/0
```

Traffic flows:

```text
PC1
192.168.0.10
   |
   |
  SW1
   |
   |
R1 G0/0/1
192.168.0.1
   |
   |
R1 G0/0/0
172.16.0.1
   |
   |
172.16.0.0/30
   |
   |
R2
172.16.0.2
   |
   |
10.0.0.0/24
   |
   |
SRV1
10.0.0.100
```

---

## Lab Objectives

Configure the following QoS settings on R1 and apply them outbound on interface `G0/0/0`.

### HTTPS

```text
Mark HTTPS traffic as AF31
Provide minimum 10% bandwidth as a priority queue
```

### HTTP

```text
Mark HTTP traffic as AF32
Provide minimum 10% bandwidth
```

### ICMP

```text
Mark ICMP traffic as CS2
Provide minimum 5% bandwidth
```

Finally, use Packet Tracer Simulation Mode to verify the DSCP markings when:

```text
Pinging jeremysitlab.com from PC1

Accessing jeremysitlab.com from PC1 using HTTP

Accessing jeremysitlab.com from PC1 using HTTPS
```

---

# Step 1 — Verify Connectivity

Before configuring QoS, I verified that PC1 could reach the destination network.

```text
PC1 → 10.0.0.100
```

The ping succeeded.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-1.1.png" alt="Day 47 Initial Connectivity Verification" width="900">
</p>

Successful connectivity is important because QoS classification and marking will only matter once traffic is actually passing through R1.

---

# Step 2 — Create Traffic Classes

QoS starts by identifying different types of traffic.

For this lab, I created three class maps:

```text
HTTPS_MAP
HTTP_MAP
ICMP_MAP
```

Each class identifies a protocol.

### HTTPS Class

```cisco
class-map match-all HTTPS_MAP
 match protocol https
```

### HTTP Class

```cisco
class-map match-all HTTP_MAP
 match protocol http
```

### ICMP Class

```cisco
class-map match-all ICMP_MAP
 match protocol icmp
```

These class maps allow R1 to classify packets based on the protocol being used.

Conceptually:

```text
Incoming Traffic
      |
      v
+----------------+
| Classification |
+----------------+
   |     |     |
   |     |     |
 HTTPS  HTTP  ICMP
```

---

# Step 3 — Create the QoS Policy Map

After identifying the traffic, I created a policy map.

```cisco
policy-map G0/0/0_OUT
```

Each class receives a different QoS treatment.

---

## HTTPS QoS Policy

HTTPS traffic receives:

```text
DSCP AF31
Priority queue
10% bandwidth
```

Configuration:

```cisco
policy-map G0/0/0_OUT

 class HTTPS_MAP
  priority percent 10
  set ip dscp af31
```

This provides HTTPS with priority treatment.

The `priority` command creates a low-latency priority queue for the traffic class.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-2.1.png" alt="Day 47 HTTPS AF31 Priority Queue" width="900">
</p>

The configuration verifies:

```text
class HTTPS_MAP
 priority percent 10
 set ip dscp af31
```

---

## HTTP QoS Policy

HTTP traffic receives:

```text
DSCP AF32
Minimum 10% bandwidth
```

Configuration:

```cisco
class HTTP_MAP
 bandwidth percent 10
 set ip dscp af32
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-3.1.png" alt="Day 47 HTTP AF32 QoS Configuration" width="900">
</p>

The HTTP class uses:

```text
bandwidth percent 10
```

rather than the priority queue used by HTTPS.

---

## ICMP QoS Policy

ICMP traffic receives:

```text
DSCP CS2
Minimum 5% bandwidth
```

Configuration:

```cisco
class ICMP_MAP
 bandwidth percent 5
 set ip dscp cs2
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-4.1.png" alt="Day 47 ICMP CS2 QoS Configuration" width="900">
</p>

---

# Complete Policy Map

The completed QoS configuration appears as:

```cisco
policy-map G0/0/0_OUT

 class HTTPS_MAP
  priority percent 10
  set ip dscp af31

 class HTTP_MAP
  bandwidth percent 10
  set ip dscp af32

 class ICMP_MAP
  bandwidth percent 5
  set ip dscp cs2
```

This means R1 now treats the traffic classes differently.

```text
HTTPS
   |
   +--> AF31
   +--> Priority Queue
   +--> 10%

HTTP
   |
   +--> AF32
   +--> Minimum 10%

ICMP
   |
   +--> CS2
   +--> Minimum 5%
```

---

# Step 4 — Apply the QoS Policy

The QoS policy must be attached to an interface before it affects traffic.

The lab required the policy to be applied outbound on:

```text
R1 G0/0/0
```

Configuration:

```cisco
interface g0/0/0
 service-policy output G0/0/0_OUT
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-4.2.png" width="900">
</p>

The configuration confirms:

```text
interface GigabitEthernet0/0/0
 ip address 172.16.0.1 255.255.255.252
 service-policy output G0/0/0_OUT
```

The policy affects traffic leaving R1 toward R2.

---

# QoS Packet Processing

Packets traveling from PC1 toward SRV1 take this path:

```text
PC1
 |
 v
SW1
 |
 v
R1 G0/0/1
 |
 | Packet classified
 |
 v
QoS Policy
 |
 | DSCP value changed
 |
 v
R1 G0/0/0
 |
 v
R2
 |
 v
SRV1
```

The important part is that the policy is configured as:

```cisco
service-policy output G0/0/0_OUT
```

Therefore, classification and marking occur as packets leave R1's `G0/0/0`.

---

# Step 5 — Verify ICMP DSCP Marking

I generated ICMP traffic by pinging the remote server.

The policy identifies the traffic using:

```cisco
match protocol icmp
```

and marks it:

```cisco
set ip dscp cs2
```

CS2 corresponds to a DSCP decimal value of:

```text
16
```

Packet Tracer represents the DSCP value in hexadecimal.

```text
16 decimal = 0x10
```

The packet inspection confirms that ICMP traffic is marked according to the configured QoS policy.

---

# Step 6 — Verify HTTP DSCP Marking

Next, I accessed:

```text
jeremysitlab.com
```

using HTTP.

HTTP uses:

```text
TCP destination port 80
```

The policy matches the traffic with:

```cisco
match protocol http
```

and marks it:

```cisco
set ip dscp af32
```

AF32 corresponds to DSCP decimal:

```text
28
```

Decimal 28 converts to hexadecimal:

```text
0x1c
```

Packet Tracer shows:

```text
DSCP: 0x1c
```

and:

```text
Destination Port: 80
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-4.3.png" alt="Day 47 HTTP AF32 DSCP Verification" width="900">
</p>

This confirms:

```text
TCP 80
   |
   v
HTTP_MAP
   |
   v
AF32
   |
   v
DSCP = 28
   |
   v
0x1c
```

---

# Step 7 — Verify HTTPS DSCP Marking

Next, I generated HTTPS traffic.

HTTPS uses:

```text
TCP destination port 443
```

The policy matches:

```cisco
match protocol https
```

and applies:

```cisco
set ip dscp af31
```

AF31 corresponds to:

```text
DSCP decimal 26
```

Decimal 26 converts to:

```text
0x1a
```

Packet Tracer displays:

```text
DSCP: 0x1a
```

and:

```text
Destination Port: 443
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS-4.4.png" alt="Day 47 HTTPS AF31 DSCP Verification" width="900">
</p>

This confirms:

```text
TCP 443
   |
   v
HTTPS_MAP
   |
   v
AF31
   |
   v
DSCP = 26
   |
   v
0x1a
```

---

# DSCP Verification Table

| Traffic | Protocol | DSCP Name | Decimal | Hex |
|---|---|---:|---:|---:|
| HTTPS | TCP 443 | AF31 | 26 | 0x1A |
| HTTP | TCP 80 | AF32 | 28 | 0x1C |
| ICMP | ICMP | CS2 | 16 | 0x10 |

This was one of the most useful parts of the lab because Packet Tracer shows the actual DSCP field inside the IP header.

---

# Understanding DSCP

DSCP stands for:

```text
Differentiated Services Code Point
```

The DSCP field exists inside the IPv4 header.

Its purpose is to tell network devices how a packet should be treated.

Conceptually:

```text
IPv4 Header
+---------------------------------------------------+
| Version | IHL | DSCP | ECN | Length | ...        |
+---------------------------------------------------+
                  ^
                  |
             QoS Marking
```

Routers and switches can inspect the DSCP value and make forwarding decisions based on it.

---

# Classification vs Marking

This lab demonstrated two separate QoS operations.

## Classification

Classification determines:

```text
"What type of traffic is this?"
```

Examples:

```cisco
match protocol https
match protocol http
match protocol icmp
```

---

## Marking

Marking determines:

```text
"What QoS label should this packet receive?"
```

Examples:

```cisco
set ip dscp af31
set ip dscp af32
set ip dscp cs2
```

The process looks like:

```text
Packet Arrives
     |
     v
Identify Protocol
     |
     v
Classify Packet
     |
     v
Assign DSCP Value
     |
     v
Forward Packet
```

---

# QoS Policy Structure

Cisco QoS configuration follows a logical hierarchy.

```text
CLASS-MAP
    |
    v
Identify traffic

POLICY-MAP
    |
    v
Define treatment

SERVICE-POLICY
    |
    v
Apply policy to interface
```

For this lab:

```text
class-map HTTPS_MAP
class-map HTTP_MAP
class-map ICMP_MAP
        |
        v
policy-map G0/0/0_OUT
        |
        v
interface G0/0/0
        |
        v
service-policy output G0/0/0_OUT
```

This structure is extremely useful for understanding Cisco QoS.

---

# Priority Queue vs Bandwidth Guarantee

The HTTPS class received:

```cisco
priority percent 10
```

HTTP received:

```cisco
bandwidth percent 10
```

ICMP received:

```cisco
bandwidth percent 5
```

These commands do not provide identical treatment.

---

## Priority Queue

```cisco
priority percent 10
```

gives the class priority scheduling.

In this lab:

```text
HTTPS → Priority Queue
```

This is useful for traffic that is more sensitive to delay.

---

## Bandwidth Guarantee

```cisco
bandwidth percent 10
```

guarantees a minimum percentage of bandwidth during congestion.

HTTP receives:

```text
10%
```

ICMP receives:

```text
5%
```

---

# QoS Policy Summary

```text
                 R1 G0/0/0
                     |
                     v
              G0/0/0_OUT
                     |
        +------------+------------+
        |            |            |
        v            v            v
     HTTPS         HTTP          ICMP
        |            |            |
      AF31         AF32           CS2
        |            |            |
 Priority 10%    Bandwidth 10%  Bandwidth 5%
```

---

# Why QoS Matters

Without QoS, network devices generally forward packets without understanding which applications may be more important.

During congestion, all traffic competes for available bandwidth.

QoS allows an administrator to classify traffic and apply different treatment.

Examples include:

```text
Voice
Video
Business Applications
Web Traffic
Management Traffic
File Transfers
Backups
ICMP
```

A network administrator could give latency-sensitive applications better treatment while allowing less important traffic to wait.

---

# Example Enterprise QoS Scenario

Imagine a WAN connection carrying:

```text
VoIP
Microsoft Teams
Web Browsing
File Transfers
Backups
Monitoring Traffic
```

If the link becomes congested, large file transfers could potentially interfere with voice or video traffic.

QoS allows the network to recognize these different applications.

```text
Incoming Traffic
      |
      v
Classification
      |
      +--> Voice
      |
      +--> Video
      |
      +--> Business Apps
      |
      +--> Web
      |
      +--> Bulk Data
```

Each class can then receive different forwarding behavior.

---

# Important Commands

## HTTPS Class Map

```cisco
class-map match-all HTTPS_MAP
 match protocol https
```

## HTTP Class Map

```cisco
class-map match-all HTTP_MAP
 match protocol http
```

## ICMP Class Map

```cisco
class-map match-all ICMP_MAP
 match protocol icmp
```

---

## QoS Policy

```cisco
policy-map G0/0/0_OUT

 class HTTPS_MAP
  priority percent 10
  set ip dscp af31

 class HTTP_MAP
  bandwidth percent 10
  set ip dscp af32

 class ICMP_MAP
  bandwidth percent 5
  set ip dscp cs2
```

---

## Apply Policy

```cisco
interface g0/0/0
 service-policy output G0/0/0_OUT
```

---

## Useful Verification

```cisco
show running-config | section policy
```

```cisco
show running-config | section class-map
```

```cisco
show running-config | section policy-map
```

```cisco
show policy-map
```

```cisco
show policy-map interface
```

---

# Packet Analysis

Packet Tracer Simulation Mode made it possible to inspect the actual IP packet.

For HTTP traffic I observed:

```text
Destination TCP Port: 80
DSCP: 0x1c
```

That corresponds to:

```text
HTTP
AF32
DSCP 28
```

For HTTPS traffic I observed:

```text
Destination TCP Port: 443
DSCP: 0x1a
```

That corresponds to:

```text
HTTPS
AF31
DSCP 26
```

This directly demonstrated that R1 was modifying the DSCP field based on the traffic class.

---

# Traffic Flow Comparison

## HTTP

```text
PC1
 |
 | TCP/80
 v
R1
 |
 | Match HTTP_MAP
 | Mark AF32
 v
DSCP 28
 |
 v
R2
 |
 v
SRV1
```

---

## HTTPS

```text
PC1
 |
 | TCP/443
 v
R1
 |
 | Match HTTPS_MAP
 | Mark AF31
 | Priority Queue
 v
DSCP 26
 |
 v
R2
 |
 v
SRV1
```

---

## ICMP

```text
PC1
 |
 | ICMP Echo
 v
R1
 |
 | Match ICMP_MAP
 | Mark CS2
 v
DSCP 16
 |
 v
R2
 |
 v
SRV1
```

---

# Key Takeaways

### QoS Does Not Create Bandwidth

QoS does not magically increase the capacity of a link.

It determines how available bandwidth is used when different types of traffic compete for the link.

---

### Classification Comes First

Before traffic can receive different treatment, the router must identify it.

This lab classified traffic using:

```text
HTTPS
HTTP
ICMP
```

---

### DSCP Marks Packets

The router can modify the DSCP field in the IP header.

This provides downstream devices with information about the intended QoS treatment.

---

### AF31 and AF32 Are Different Markings

Although both are part of the Assured Forwarding group, they have different DSCP values.

```text
AF31 = 26
AF32 = 28
```

Packet Tracer displayed these values as:

```text
AF31 → 0x1A
AF32 → 0x1C
```

---

### CS2 Represents DSCP 16

ICMP was marked:

```text
CS2
```

which corresponds to:

```text
DSCP 16
```

---

### QoS Policies Must Be Applied to an Interface

Creating class maps and policy maps alone does not affect traffic.

The policy became active when I configured:

```cisco
service-policy output G0/0/0_OUT
```

on R1.

---

### Direction Matters

The policy was configured as:

```text
output
```

Therefore it processes packets as they leave R1's `G0/0/0` interface.

QoS policies can be direction-specific.

---

# What I Practiced

- Quality of Service fundamentals
- Traffic classification
- Traffic marking
- DSCP
- AF31
- AF32
- CS2
- Class maps
- Policy maps
- Service policies
- HTTP classification
- HTTPS classification
- ICMP classification
- Priority queues
- Bandwidth guarantees
- Outbound QoS policies
- Packet Tracer Simulation Mode
- IPv4 header inspection
- TCP port inspection
- DSCP verification
- Enterprise traffic prioritization concepts

---

# Final Result

- ✅ Verified end-to-end connectivity
- ✅ Created HTTPS traffic classification
- ✅ Created HTTP traffic classification
- ✅ Created ICMP traffic classification
- ✅ Marked HTTPS traffic as AF31
- ✅ Assigned HTTPS to a 10% priority queue
- ✅ Marked HTTP traffic as AF32
- ✅ Guaranteed HTTP a minimum 10% bandwidth
- ✅ Marked ICMP traffic as CS2
- ✅ Guaranteed ICMP a minimum 5% bandwidth
- ✅ Created the `G0/0/0_OUT` policy map
- ✅ Applied the QoS policy outbound on R1 G0/0/0
- ✅ Generated ICMP traffic
- ✅ Generated HTTP traffic
- ✅ Generated HTTPS traffic
- ✅ Inspected packets in Simulation Mode
- ✅ Verified TCP destination port 80 for HTTP
- ✅ Verified TCP destination port 443 for HTTPS
- ✅ Verified AF32 DSCP marking on HTTP traffic
- ✅ Verified AF31 DSCP marking on HTTPS traffic
- ✅ Observed QoS markings directly inside the IPv4 header

---

# Day 47 Complete

**Quality of Service — Classification, Marking & DSCP ✅**

The biggest takeaway from this lab was seeing that QoS is not simply about assigning "priority" to traffic.

There is a complete process:

```text
Identify traffic
      ↓
Classify traffic
      ↓
Apply a QoS policy
      ↓
Mark the IP packet
      ↓
Queue traffic appropriately
      ↓
Forward the packet
```

The most valuable part was inspecting the packets in Packet Tracer and seeing the DSCP field actually change.

```text
HTTPS → AF31 → DSCP 26 → 0x1A

HTTP  → AF32 → DSCP 28 → 0x1C

ICMP  → CS2  → DSCP 16 → 0x10
```

Instead of QoS being just a set of CLI commands, this lab made it possible to see exactly where the classification and marking appear inside the packet itself.
