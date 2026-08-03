# Day 39 — DHCP Server, DHCP Client, and DHCP Relay
Day-39—DHCP-Server,DHCP-Client,and-DHCP-Relay

## 📖 Overview

Today’s CCNA lab focused on **Dynamic Host Configuration Protocol (DHCP)** and how network devices automatically receive IPv4 configuration.

Instead of manually assigning an IP address, subnet mask, default gateway, DNS server, and domain name to every device, DHCP allows a centralized server to provide this information automatically.

This lab covered three different DHCP roles:

- **R2 as the DHCP server**
- **R1 G0/0 as a DHCP client**
- **R1 as a DHCP relay agent**

The lab also demonstrated how a router can forward DHCP requests between different subnets using the `ip helper-address` command.

---

## 🖥️ Network Topology

The topology contains:

- Two Cisco 2911 routers
- Two Cisco 2960 switches
- Two client PCs
- LAN 1 using `192.168.1.0/24`
- LAN 2 using `192.168.2.0/24`
- A point-to-point transit network using `203.0.113.0/30`
- R2 operating as the centralized DHCP server
- R1 operating as a DHCP client and DHCP relay agent

<p align="center">
  <a href="PASTE-DAY-39-TOPOLOGY-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP.png" alt="Day 39 DHCP Network Topology" width="1000">
  </a>
</p>

---

## 🎯 Lab Objectives

1. Configure three DHCP pools on R2.
2. Reserve addresses that should not be assigned to clients.
3. Configure DNS, domain name, network, and default-gateway options.
4. Configure R1 G0/0 as a DHCP client.
5. Identify the address dynamically assigned to R1.
6. Configure R1 as a DHCP relay agent for `192.168.1.0/24`.
7. Force PC1 and PC2 to request IPv4 configuration.
8. Verify the leases received by both clients.

---

## 📋 DHCP Addressing Plan

### POOL1 — PC1 Network

```text
Network:          192.168.1.0/24
Reserved range:   192.168.1.1–192.168.1.10
Default gateway:  192.168.1.1
DNS server:       8.8.8.8
Domain name:      jeremysitlab.com
First client IP:  192.168.1.11
```

### POOL2 — PC2 Network

```text
Network:          192.168.2.0/24
Reserved range:   192.168.2.1–192.168.2.10
Default gateway:  192.168.2.1
DNS server:       8.8.8.8
Domain name:      jeremysitlab.com
First client IP:  192.168.2.11
```

### POOL3 — Router Transit Network

```text
Network:          203.0.113.0/30
Reserved address: 203.0.113.1
Available lease:  203.0.113.2
```

---

# Phase 1 — Configure DHCP Pools on R2

R2 was configured as the centralized DHCP server for all three networks.

Before creating the pools, reserved infrastructure addresses were excluded from the available lease ranges.

```cisco
R2(config)#ip dhcp excluded-address 192.168.1.1 192.168.1.10
R2(config)#ip dhcp excluded-address 192.168.2.1 192.168.2.10
R2(config)#ip dhcp excluded-address 203.0.113.1
```

## Configure POOL1

```cisco
R2(config)#ip dhcp pool POOL1
R2(dhcp-config)#network 192.168.1.0 255.255.255.0
R2(dhcp-config)#default-router 192.168.1.1
R2(dhcp-config)#dns-server 8.8.8.8
R2(dhcp-config)#domain-name jeremysitlab.com
```

## Configure POOL2

```cisco
R2(config)#ip dhcp pool POOL2
R2(dhcp-config)#network 192.168.2.0 255.255.255.0
R2(dhcp-config)#default-router 192.168.2.1
R2(dhcp-config)#dns-server 8.8.8.8
R2(dhcp-config)#domain-name jeremysitlab.com
```

## Configure POOL3

```cisco
R2(config)#ip dhcp pool POOL3
R2(dhcp-config)#network 203.0.113.0 255.255.255.252
```

The completed DHCP configuration was verified in the running configuration.

<p align="center">
  <a href="PASTE-DAY-39-DHCP-1.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP-1.1.png" alt="R2 DHCP Pool Configuration" width="1000">
  </a>
</p>

---

# Phase 2 — Configure R1 as a DHCP Client

R1’s G0/0 interface was configured to request its IPv4 address dynamically from R2.

```cisco
R1(config)#interface g0/0
R1(config-if)#ip address dhcp
R1(config-if)#no shutdown
```

R1 received the following address:

```text
IPv4 Address: 203.0.113.2
Subnet Mask:  255.255.255.252
Method:       DHCP
Status:       up/up
```

The dynamically assigned address was verified with:

```cisco
R1#show ip interface brief
```

Example output:

```text
Interface              IP-Address      Method  Status  Protocol
GigabitEthernet0/0     203.0.113.2    DHCP    up      up
GigabitEthernet0/1     192.168.1.1    NVRAM   up      up
```

<p align="center">
  <a href="PASTE-DAY-39-DHCP-2.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP-2.1.png" alt="R1 DHCP Client Configuration" width="1000">
  </a>
</p>

---

# Phase 3 — Configure R1 as a DHCP Relay Agent

PC1 is located on the `192.168.1.0/24` network, but the DHCP server is located on R2.

A new DHCP client initially sends a broadcast because it does not yet know the address of the DHCP server.

Routers do not forward broadcasts by default. Without a relay agent, PC1’s DHCP Discover message could not reach R2.

R1 was configured to relay DHCP traffic from the PC1 LAN to R2.

```cisco
R1(config)#interface g0/1
R1(config-if)#ip helper-address 192.168.2.1
```

The helper address receives the DHCP broadcast on G0/1 and forwards it as unicast traffic toward the DHCP server.

The configuration was verified with:

```cisco
R1#show running-config | section interface
```

Expected configuration:

```text
interface GigabitEthernet0/1
 ip address 192.168.1.1 255.255.255.0
 ip helper-address 192.168.2.1
```

<p align="center">
  <a href="PASTE-DAY-39-DHCP-3.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP-3.1.png" alt="R1 DHCP Relay Configuration" width="1000">
  </a>
</p>

---

# Phase 4 — Request DHCP Configuration on PC1

PC1 initially failed to receive an address while the DHCP relay configuration was incomplete.

After the DHCP pools and relay agent were correctly configured, PC1 requested a new lease using:

```text
ipconfig /renew
```

PC1 received:

```text
IPv4 Address:     192.168.1.12
Subnet Mask:      255.255.255.0
Default Gateway:  192.168.1.1
DNS Server:       8.8.8.8
```

This confirmed that:

- PC1 sent a local DHCP broadcast.
- R1 received the request.
- R1 forwarded the request to R2.
- R2 selected an address from POOL1.
- The reply successfully returned to PC1.

<p align="center">
  <a href="PASTE-DAY-39-DHCP-4.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP-4.1.png" alt="PC1 DHCP Lease Through Relay Agent" width="1000">
  </a>
</p>

---

# Phase 5 — Request DHCP Configuration on PC2

PC2 is located directly on the `192.168.2.0/24` network connected to R2.

Because PC2 and the DHCP server were on the same subnet, a relay agent was not required.

PC2 requested a lease using:

```text
ipconfig /renew
```

PC2 received:

```text
IPv4 Address:     192.168.2.11
Subnet Mask:      255.255.255.0
Default Gateway:  192.168.2.1
DNS Server:       8.8.8.8
```

<p align="center">
  <a href="PASTE-DAY-39-DHCP-4.2-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP-4.2.png" alt="PC2 DHCP Lease From Local Server" width="1000">
  </a>
</p>

---

## 🔄 The DHCP DORA Process

DHCP normally assigns an address through four messages known as **DORA**.

### 1. Discover

The client broadcasts a DHCP Discover message to locate a DHCP server.

```text
Source IP:         0.0.0.0
Destination IP:    255.255.255.255
UDP source port:   68
UDP destination:   67
```

### 2. Offer

The DHCP server responds with an available IPv4 address and configuration options.

### 3. Request

The client requests the offered IPv4 address.

### 4. Acknowledgment

The server sends a DHCP ACK confirming the lease.

```text
Discover → Offer → Request → Acknowledgment
```

---

## DHCP Server, Client, and Relay Roles

| Role | Device | Function |
|---|---|---|
| DHCP server | R2 | Maintains the pools and provides client configuration |
| DHCP client | R1 G0/0 | Dynamically requests its own IPv4 address |
| DHCP client | PC1 and PC2 | Request IP, mask, gateway, DNS, and domain information |
| DHCP relay | R1 G0/1 | Forwards DHCP messages between different subnets |

---

## Important DHCP Ports

| Traffic Direction | UDP Port |
|---|---:|
| Client to server | 67 |
| Server to client | 68 |

The client sends from UDP port 68 toward server port 67.

The server replies from UDP port 67 toward client port 68.

---

## 🛠️ Commands Practiced

### DHCP Address Exclusions

```cisco
ip dhcp excluded-address 192.168.1.1 192.168.1.10
ip dhcp excluded-address 192.168.2.1 192.168.2.10
ip dhcp excluded-address 203.0.113.1
```

### DHCP Pool Configuration

```cisco
ip dhcp pool POOL1
network 192.168.1.0 255.255.255.0
default-router 192.168.1.1
dns-server 8.8.8.8
domain-name jeremysitlab.com
```

### DHCP Client Configuration

```cisco
interface g0/0
ip address dhcp
no shutdown
```

### DHCP Relay Configuration

```cisco
interface g0/1
ip helper-address 192.168.2.1
```

### Verification Commands

```cisco
show ip interface brief
show running-config
show ip dhcp pool
show ip dhcp binding
```

### Client Commands

```text
ipconfig
ipconfig /renew
ipconfig /all
```

---

## 🧠 Troubleshooting Notes

PC1 initially displayed repeated:

```text
DHCP request failed.
```

This demonstrated that a DHCP pool alone is not enough when the client and server are on separate networks.

The following items had to be verified:

1. R2 had a correctly configured pool for `192.168.1.0/24`.
2. The default gateway in POOL1 pointed to R1.
3. R1 G0/1 had the correct IPv4 address.
4. R1 G0/1 contained the correct `ip helper-address`.
5. R1 and R2 had operational interfaces.
6. R2 had a return route toward the PC1 subnet.
7. The excluded address range did not remove all usable client addresses.

Once these conditions were met, PC1 received a valid lease.

---

## DHCP Relay Traffic Flow

When PC1 requested an address, the following process occurred:

1. PC1 broadcast a DHCP Discover message.
2. SW1 flooded the broadcast within the local LAN.
3. R1 received the broadcast on G0/1.
4. The `ip helper-address` configuration caused R1 to relay the request.
5. R1 forwarded the message as unicast traffic toward R2.
6. R2 selected an address from POOL1.
7. R2 sent the DHCP response back toward R1.
8. R1 forwarded the response to PC1.
9. PC1 completed the DORA process and installed the lease.

---

## 🎯 Key Takeaways

The biggest lesson from this lab was that DHCP can be centralized.

A business does not need a dedicated DHCP server on every subnet. A central server can support multiple LANs when routers are configured to relay the requests.

The three DHCP roles must be understood separately:

```text
The server owns the address pools.
The client requests configuration.
The relay forwards requests across Layer 3 boundaries.
```

The `ip helper-address` command is what allows DHCP broadcasts to reach a server located on another network.

---

## 📚 Skills Practiced

- Cisco IOS DHCP server configuration
- DHCP pool creation
- DHCP address exclusions
- Dynamic router interface addressing
- DHCP relay configuration
- IP helper addresses
- DORA message flow
- UDP ports 67 and 68
- DHCP lease renewal
- Multi-subnet address deployment
- Client configuration verification
- DHCP troubleshooting

---

## ✅ Lab Status

**Day 39 Complete**

### Topics Covered

- DHCP server
- DHCP client
- DHCP relay
- DHCP pools
- Excluded addresses
- IP helper address
- DORA
- UDP 67 and 68
- Dynamic IPv4 addressing
- Cisco IOS verification
