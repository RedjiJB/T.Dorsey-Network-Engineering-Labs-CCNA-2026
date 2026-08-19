# Commit: Day 58 Complete — Wireless LANs & WLC Configuration

**Status:** ✅ Complete  
**Lab:** Jeremy's IT Lab — Day 58  
**Topic:** Wireless LANs, Wireless LAN Controllers, WLANs & WPA2-PSK  
**Exam Relevance:** CCNA 200-301

---

## Objective

Use a Cisco Wireless LAN Controller (WLC) to configure and manage multiple WLANs, connect lightweight access points, create dynamic interfaces for wireless VLANs, secure WLANs with WPA2-PSK, and associate wireless clients to the network.

### Requirements

1. Access the WLC GUI from PC1 using HTTPS.
2. Explore the WLC interface and review the current wireless network state.
3. Configure dynamic interfaces for the Internal and Guest WLANs.
4. Create the Internal and Guest WLANs using WPA2-PSK.
5. Add wireless clients and associate them with the access points.

---

## Topology

```text
                           WLC1
                       172.16.1.10
                            |
                         G1/0/1
                            |
                           SW1
                    3650 Multilayer Switch
                   /         |         \
              G1/0/2      G1/0/3      G1/0/4
                |            |            |
               AP1          AP2           PC1
                |
          Wireless Clients
        Laptop / Smartphone
```

### VLAN / WLAN Information

```text
VLAN 10  — Management
Network: 172.16.1.0/24

VLAN 100 — Internal WLAN
Network: 10.0.0.0/24
SSID: Internal

VLAN 200 — Guest WLAN
Network: 10.1.0.0/24
SSID: Guest
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs.png" width="900">
</p>

---

## Skills Practiced

- Accessing a Cisco Wireless LAN Controller through HTTPS
- Navigating the Cisco WLC GUI
- Monitoring controller status
- Viewing lightweight access points
- Configuring dynamic interfaces
- Mapping VLANs to WLANs
- Creating wireless SSIDs
- Configuring WPA2-PSK security
- Understanding centralized wireless architecture
- Associating lightweight APs with a WLC
- Connecting wireless clients
- Separating wireless networks using VLANs
- Verifying WLAN operational status

---

# Part 1 — Access the Wireless LAN Controller

The first task was to access the WLC management interface from PC1.

Management address:

```text
172.16.1.10
```

Because the controller requires HTTPS, the browser address is:

```text
https://172.16.1.10
```

Credentials:

```text
Username: admin
Password: Cisco123
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs-1.1.png" width="900">
</p>

The WLC GUI provides centralized configuration and monitoring for the wireless infrastructure.

---

# Part 2 — Centralized Wireless Architecture

This lab uses a Cisco Wireless LAN Controller and lightweight access points.

Instead of configuring each access point independently, the APs register with the WLC.

Conceptually:

```text
                    WLC
                     |
              Central Management
                     |
            ---------------------
            |                   |
           AP1                 AP2
            |                   |
      Wireless Clients    Wireless Clients
```

The controller manages functions such as:

- WLAN configuration
- SSIDs
- Security policies
- VLAN mappings
- AP management
- Client monitoring
- Radio configuration

This allows wireless infrastructure to be managed from a central location.

---

# Part 3 — Explore the WLC GUI

The WLC GUI includes several major sections.

```text
MONITOR
WLANs
CONTROLLER
WIRELESS
SECURITY
MANAGEMENT
COMMANDS
```

Each section serves a different purpose.

---

## MONITOR

The Monitor section displays the current operational status of the wireless network.

Information includes:

```text
Controller status
Controller uptime
Management IP
Software version
Access point information
Wireless clients
System utilization
Radio status
```

The controller showed both:

```text
802.11a Network State: Enabled
802.11b/g Network State: Enabled
```

This confirmed that both wireless radio networks were operational.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs-2.1.png" width="900">
</p>

---

## WIRELESS

The Wireless section provides information about the access points managed by the controller.

The controller detected two lightweight APs:

```text
AP1
AP2
```

Both APs had joined the WLC and received management IP addresses.

This confirmed that the centralized wireless infrastructure was operational.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs-2.2.png" width="900">
</p>

---

# Part 4 — WLC Interfaces

The controller uses logical interfaces to connect WLANs to VLANs.

The management interface was already configured.

```text
Management Interface

IP Address: 172.16.1.10
VLAN: Management VLAN
```

Two additional dynamic interfaces were required:

```text
Internal
Guest
```

These interfaces connect WLAN traffic to their respective VLANs.

---

# Part 5 — Configure the Internal Dynamic Interface

The Internal WLAN uses:

```text
VLAN 100
Network: 10.0.0.0/24
```

A dynamic interface named:

```text
Internal
```

was created on the controller.

Example configuration:

```text
Interface Name: Internal
VLAN ID: 100
IP Address: 10.0.0.10
```

This interface acts as the WLC's Layer 3 presence for the Internal WLAN.

---

# Part 6 — Configure the Guest Dynamic Interface

The Guest WLAN uses:

```text
VLAN 200
Network: 10.1.0.0/24
```

A second dynamic interface was created:

```text
Guest
```

Example:

```text
Interface Name: Guest
VLAN ID: 200
IP Address: 10.1.0.10
```

The WLC interface table then contained:

```text
Guest
Internal
Management
Virtual
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs-3.1.png" width="900">
</p>

---

# Part 7 — WLAN and VLAN Mapping

Each wireless network is mapped to a specific dynamic interface and VLAN.

```text
SSID Internal
     |
     v
Internal Dynamic Interface
     |
     v
VLAN 100
     |
     v
10.0.0.0/24
```

Guest traffic follows a separate path:

```text
SSID Guest
     |
     v
Guest Dynamic Interface
     |
     v
VLAN 200
     |
     v
10.1.0.0/24
```

This allows wireless clients connected to different SSIDs to remain logically separated.

---

# Part 8 — Create the Internal WLAN

The Internal wireless network was created through:

```text
WLANs
```

Configuration:

```text
Profile Name: Internal
SSID: Internal
```

The WLAN was mapped to:

```text
Dynamic Interface: Internal
VLAN: 100
```

---

# Part 9 — Configure Internal WLAN Security

The Internal WLAN uses:

```text
WPA2
PSK
```

WPA2-PSK uses a shared password between the wireless client and wireless infrastructure.

Conceptually:

```text
Wireless Client
      |
      | WPA2-PSK Authentication
      |
      v
Access Point
      |
      v
Wireless LAN Controller
```

The WLAN was then enabled.

---

# Part 10 — Create the Guest WLAN

The Guest WLAN was created separately.

Configuration:

```text
Profile Name: Guest
SSID: Guest
```

It was mapped to:

```text
Dynamic Interface: Guest
VLAN: 200
```

The Guest WLAN was also configured with:

```text
WPA2-PSK
```

This created two separate wireless networks:

```text
Internal
Guest
```

---

# Part 11 — Verify WLAN Configuration

The WLAN page displayed both wireless networks.

```text
WLAN ID 1
Profile Name: Internal
SSID: Internal

WLAN ID 2
Profile Name: Guest
SSID: Guest
```

Security policies showed:

```text
WPA2
Authentication: PSK
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs-4.1.png" width="900">
</p>

---

# Part 12 — Wireless Client Association

Wireless clients were added to the topology.

The completed wireless infrastructure included:

```text
Laptop
Smartphone
```

These devices associated wirelessly with the lightweight access points.

The APs then forwarded wireless traffic toward the WLC.

Conceptually:

```text
Laptop
   ))
   ))
  AP1
   |
   |
  SW1
   |
  WLC
```

and:

```text
Smartphone
     ))
     ))
    AP2
     |
     |
    SW1
     |
    WLC
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs-4.2.png" width="900">
</p>

---

# Part 13 — How Client Traffic Is Handled

When a wireless client connects to the Internal SSID:

```text
Wireless Client
      |
      v
SSID: Internal
      |
      v
AP
      |
      v
WLC
      |
      v
Dynamic Interface: Internal
      |
      v
VLAN 100
      |
      v
10.0.0.0/24
```

For the Guest SSID:

```text
Wireless Client
      |
      v
SSID: Guest
      |
      v
AP
      |
      v
WLC
      |
      v
Dynamic Interface: Guest
      |
      v
VLAN 200
      |
      v
10.1.0.0/24
```

The SSID therefore determines which VLAN the client's traffic enters.

---

# Part 14 — Lightweight Access Points

AP1 and AP2 operate as lightweight access points.

Their primary configuration is controlled centrally by the WLC rather than individually on each AP.

This architecture provides:

```text
Centralized SSID management
Centralized security policies
Centralized AP management
Centralized client monitoring
Centralized radio management
```

The WLC showed both APs as registered devices.

---

# Part 15 — Management VLAN

The controller itself is managed through:

```text
VLAN 10
172.16.1.0/24
```

WLC address:

```text
172.16.1.10
```

This network is separate from the client WLAN networks.

```text
Management VLAN 10
172.16.1.0/24

Internal VLAN 100
10.0.0.0/24

Guest VLAN 200
10.1.0.0/24
```

Separating management traffic from client traffic is an important network design concept.

---

# Part 16 — Wireless Network Separation

Using different VLANs provides logical separation between wireless networks.

```text
Internal WLAN
SSID: Internal
VLAN 100
10.0.0.0/24
```

and:

```text
Guest WLAN
SSID: Guest
VLAN 200
10.1.0.0/24
```

This means users connected to the Guest SSID do not automatically become part of the Internal network.

Additional routing, ACL, and firewall policies can then be used to control communication between the networks.

---

# Part 17 — WPA2-PSK

WPA2-PSK stands for:

```text
Wi-Fi Protected Access 2
Pre-Shared Key
```

A shared password is configured on the WLAN and entered by wireless clients.

The general process is:

```text
Client selects SSID
        |
        v
Client provides PSK
        |
        v
Authentication succeeds
        |
        v
Client associates with AP
        |
        v
Traffic enters assigned WLAN/VLAN
```

---

# Verification

The final topology demonstrated successful centralized wireless configuration.

Verified items included:

```text
WLC reachable through HTTPS
Management interface operational
AP1 registered
AP2 registered
Internal dynamic interface created
Guest dynamic interface created
Internal WLAN created
Guest WLAN created
WPA2-PSK configured
Wireless client association established
```

---

# Key Concepts

## 1. WLC

```text
Wireless LAN Controller
```

Centralizes wireless network configuration and management.

---

## 2. Lightweight AP

A lightweight AP relies on a wireless LAN controller for centralized management.

---

## 3. WLAN

A WLAN represents a wireless network configuration.

Example:

```text
SSID: Internal
```

---

## 4. SSID

SSID stands for:

```text
Service Set Identifier
```

This is the wireless network name displayed to clients.

Examples:

```text
Internal
Guest
```

---

## 5. Dynamic Interface

A WLC dynamic interface maps wireless traffic to a VLAN.

Example:

```text
Internal WLAN
      ↓
Internal Interface
      ↓
VLAN 100
```

---

## 6. Management Interface

The management interface is used to access and manage the WLC.

In this lab:

```text
172.16.1.10
```

---

## 7. WPA2-PSK

Provides wireless authentication using a pre-shared key.

---

# Important Wireless Architecture Relationship

```text
SSID
 |
 v
WLAN
 |
 v
Dynamic Interface
 |
 v
VLAN
 |
 v
IP Subnet
```

For the Internal network:

```text
Internal
   |
WLAN 1
   |
Internal Interface
   |
VLAN 100
   |
10.0.0.0/24
```

For Guest:

```text
Guest
   |
WLAN 2
   |
Guest Interface
   |
VLAN 200
   |
10.1.0.0/24
```

---

# Troubleshooting Workflow

If a wireless client cannot connect, verify the network in layers.

```text
1. Is the WLAN enabled?

2. Is the SSID correct?

3. Is WPA2/PSK configured correctly?

4. Is the AP registered with the WLC?

5. Is the WLAN mapped to the correct dynamic interface?

6. Is the dynamic interface mapped to the correct VLAN?

7. Is the switch trunk carrying the required VLAN?

8. Does the client receive a valid IP address?

9. Can the client reach its default gateway?
```

This provides a structured troubleshooting process rather than changing configurations randomly.

---

# Lessons Learned

## 1. Wireless Networks Still Depend on Wired Infrastructure

Although the client connection is wireless, the AP ultimately forwards traffic into the wired network.

```text
Wireless Client
      ))
      AP
      |
    Switch
      |
     WLC
      |
    VLAN
      |
   Network
```

---

## 2. SSIDs Can Map to Different VLANs

Multiple wireless networks can use the same physical access points while remaining logically separated.

```text
AP1
 ├── Internal → VLAN 100
 └── Guest    → VLAN 200
```

---

## 3. The WLC Centralizes Management

Instead of independently configuring every AP:

```text
AP1
AP2
AP3
AP4
```

the network administrator manages wireless settings from:

```text
WLC
```

This becomes increasingly important as wireless environments scale.

---

## 4. Management Traffic Should Be Separate

The WLC management network:

```text
172.16.1.0/24
```

is separate from client WLAN traffic.

This supports better security and network organization.

---

## 5. Wireless Troubleshooting Requires Both Wired and Wireless Knowledge

A failed wireless connection can involve:

```text
SSID
Security
AP
WLC
Trunk
VLAN
DHCP
Routing
```

Wireless troubleshooting therefore often crosses multiple layers of the network.

---

# Final Verification

The completed lab successfully demonstrated:

- ✅ WLC GUI accessed through HTTPS
- ✅ Controller management interface verified
- ✅ WLC monitoring interface explored
- ✅ Wireless controller operational state reviewed
- ✅ AP1 successfully registered with the controller
- ✅ AP2 successfully registered with the controller
- ✅ Internal dynamic interface configured
- ✅ Guest dynamic interface configured
- ✅ VLAN 100 mapped to the Internal WLAN
- ✅ VLAN 200 mapped to the Guest WLAN
- ✅ Internal SSID created
- ✅ Guest SSID created
- ✅ WPA2-PSK configured
- ✅ WLAN configuration verified through the WLC GUI
- ✅ Wireless clients added to the network
- ✅ Wireless clients associated through the AP infrastructure
- ✅ Centralized wireless architecture demonstrated

---

# Day 58 Complete ✅

**Wireless LANs — WLC Management, Lightweight APs, WLANs, VLAN Mapping & WPA2-PSK**
