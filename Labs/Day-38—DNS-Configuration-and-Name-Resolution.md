# Day 38 — DNS Configuration and Name Resolution

## 📖 Overview

Today’s CCNA lab focused on the **Domain Name System (DNS)** and how network devices translate human-readable names into IPv4 addresses.

Instead of requiring users to remember the IP address of every server, DNS allows devices to communicate using names such as `youtube.com`.

During this lab, I configured:

- A default route from R1 toward the simulated internet
- DNS server settings on three client PCs
- DNS server settings on R1
- Local hostname entries on R1
- Hostname-based ping testing
- External DNS resolution
- Packet Tracer Simulation Mode to observe DNS and ICMP traffic

This lab demonstrated that DNS and routing work together but perform different jobs:

- **DNS identifies the destination IP address**
- **Routing determines how traffic reaches that address**

---

## 🖥️ Network Topology

The topology contains:

- One Cisco 2911 router serving as the internal gateway
- One Cisco 2960 switch
- Three client PCs
- One simulated internet router
- One DNS server using `1.1.1.1`
- One external server representing `youtube.com`
- Internal network `192.168.0.0/24`
- External point-to-point network `203.0.113.0/30`

<p align="center">
  <a href="PASTE-DAY-38-TOPOLOGY-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS.png" alt="Day 38 DNS Network Topology" width="1000">
  </a>
</p>

---

## 🎯 Lab Objectives

1. Configure a default route toward the simulated internet.
2. Configure PC1, PC2, and PC3 to use `1.1.1.1` as their DNS server.
3. Configure R1 to use `1.1.1.1` as its DNS server.
4. Create local hostname entries on R1.
5. Verify local hostname resolution from R1.
6. Ping `youtube.com` by name from a client.
7. Analyze the DNS and ICMP messages in Simulation Mode.

---

## 📋 Addressing Table

| Device | Interface | IPv4 Address | Default Gateway | DNS Server |
|---|---|---:|---:|---:|
| R1 | G0/0 | 203.0.113.1/30 | N/A | 1.1.1.1 |
| R1 | G0/1 | 192.168.0.254/24 | N/A | 1.1.1.1 |
| Internet Router | Connected interface | 203.0.113.2/30 | N/A | N/A |
| PC1 | FastEthernet0 | 192.168.0.1/24 | 192.168.0.254 | 1.1.1.1 |
| PC2 | FastEthernet0 | 192.168.0.2/24 | 192.168.0.254 | 1.1.1.1 |
| PC3 | FastEthernet0 | 192.168.0.3/24 | 192.168.0.254 | 1.1.1.1 |
| DNS Server | Server interface | 1.1.1.1 | Configured | N/A |
| Web Server | Server interface | Resolved through DNS | Configured | N/A |

---

# Phase 1 — Configure and Verify the Default Route

R1 required a default route so traffic destined for networks outside the internal routing table could be forwarded toward the simulated internet router.

```cisco
R1(config)#ip route 0.0.0.0 0.0.0.0 203.0.113.2
```

The route was verified with:

```cisco
R1#show ip route
```

Expected routing-table entry:

```text
S* 0.0.0.0/0 [1/0] via 203.0.113.2
```

The `S` identifies a static route, while the asterisk identifies it as the candidate default route.

<p align="center">
  <a href="PASTE-DAY-38-DNS-1.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS-1.1.png" alt="R1 Default Route Verification" width="1000">
  </a>
</p>

---

# Phase 2 — Configure DNS on the Client PCs

Each client was manually configured to use the DNS server at:

```text
1.1.1.1
```

This allows the clients to resolve names such as `youtube.com` into destination IPv4 addresses.

## PC1 DNS Configuration

PC1 was configured with:

```text
IPv4 Address:     192.168.0.1
Subnet Mask:      255.255.255.0
Default Gateway:  192.168.0.254
DNS Server:       1.1.1.1
```

The configuration was verified using:

```text
ipconfig /all
```

<p align="center">
  <a href="PASTE-DAY-38-DNS-2.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS-2.1.png" alt="PC1 DNS Configuration" width="1000">
  </a>
</p>

---

## PC2 DNS Configuration

PC2 was configured with:

```text
IPv4 Address:     192.168.0.2
Subnet Mask:      255.255.255.0
Default Gateway:  192.168.0.254
DNS Server:       1.1.1.1
```

<p align="center">
  <a href="PASTE-DAY-38-DNS-2.2-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS-2.2.png" alt="PC2 DNS Configuration" width="1000">
  </a>
</p>

---

## PC3 DNS Configuration

PC3 was configured with:

```text
IPv4 Address:     192.168.0.3
Subnet Mask:      255.255.255.0
Default Gateway:  192.168.0.254
DNS Server:       1.1.1.1
```

<p align="center">
  <a href="PASTE-DAY-38-DNS-2.3-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS-2.3.png" alt="PC3 DNS Configuration" width="1000">
  </a>
</p>

---

# Phase 3 — Configure DNS and Local Host Entries on R1

R1 was configured to use `1.1.1.1` as its DNS server.

```cisco
R1(config)#ip name-server 1.1.1.1
```

Local hostname entries were then created for the three internal client devices.

```cisco
R1(config)#ip host PC1 192.168.0.1
R1(config)#ip host PC2 192.168.0.2
R1(config)#ip host PC3 192.168.0.3
```

The entries were verified with:

```cisco
R1#show hosts
```

Example result:

```text
Host    Address
PC1     192.168.0.1
PC2     192.168.0.2
PC3     192.168.0.3
```

R1 was then able to ping PC1 using its hostname instead of its IPv4 address.

```cisco
R1#ping PC1
```

The successful result proved that R1 correctly translated the locally configured hostname into `192.168.0.1`.

<p align="center">
  <a href="PASTE-DAY-38-DNS-3.1-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS-3.1.png" alt="R1 Local Hostname Resolution and Ping Verification" width="1000">
  </a>
</p>

---

# Phase 4 — Resolve and Ping an External Domain

From PC1, I tested DNS resolution by entering:

```text
ping youtube.com
```

The client did not initially know the server’s IPv4 address.

PC1 first sent a DNS request to `1.1.1.1`. The DNS server returned the IP address associated with `youtube.com`, allowing PC1 to generate ICMP Echo Requests toward that destination.

```text
C:\>ping youtube.com
```

The command successfully resolved `youtube.com` to:

```text
172.217.6.78
```

Some of the initial ICMP requests timed out while Packet Tracer completed ARP and DNS-related processing. Later Echo Requests received replies, confirming successful name resolution and connectivity.

<p align="center">
  <a href="PASTE-DAY-38-DNS-4-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS-4.png" alt="External DNS Resolution and Ping to YouTube" width="1000">
  </a>
</p>

---

## 🔍 DNS Resolution Process

When PC1 entered `ping youtube.com`, the following process occurred:

1. PC1 checked its local DNS cache.
2. PC1 determined that it did not already know the address.
3. PC1 created a DNS query for `youtube.com`.
4. The query was sent to the configured DNS server at `1.1.1.1`.
5. PC1 forwarded the traffic to its default gateway, `192.168.0.254`.
6. R1 used its default route to forward the query toward the internet.
7. The DNS server returned the IPv4 address associated with `youtube.com`.
8. PC1 used the returned IPv4 address as the destination for ICMP traffic.
9. The external server returned ICMP Echo Replies.

The DNS request occurs before the destination can be contacted by name.

---

## DNS vs Routing

DNS and routing are connected, but they solve different problems.

### DNS

DNS answers:

```text
What IP address belongs to this hostname?
```

Example:

```text
youtube.com → 172.217.6.78
```

### Routing

Routing answers:

```text
Where should the packet be forwarded to reach that IP address?
```

A DNS response can successfully return an address, but communication will still fail if there is no route to that destination.

Likewise, a client may have working IP connectivity but still fail to reach services by name if DNS is incorrectly configured.

---

## Important Protocols

| Protocol | Port or Type | Purpose |
|---|---:|---|
| DNS | UDP 53 | Standard DNS queries and responses |
| DNS | TCP 53 | Large DNS responses and zone transfers |
| ICMP | No TCP/UDP port | Ping and reachability testing |
| ARP | Layer 2 protocol | Resolves local IPv4 addresses to MAC addresses |

---

## 🛠️ Commands Practiced

### Router Configuration

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.2
ip name-server 1.1.1.1
ip host PC1 192.168.0.1
ip host PC2 192.168.0.2
ip host PC3 192.168.0.3
```

### Router Verification

```cisco
show ip route
show hosts
ping PC1
```

### Client Verification

```text
ipconfig /all
ping youtube.com
```

---

## 📚 Skills Practiced

- DNS configuration
- DNS name resolution
- Client DNS configuration
- Cisco IOS name-server configuration
- Cisco IOS local hostname entries
- Default static routing
- Routing-table verification
- Name-based connectivity testing
- ICMP troubleshooting
- Packet Tracer Simulation Mode
- DNS request and response analysis
- Layer 3 troubleshooting

---

## 🧠 Troubleshooting Method

When a client cannot access a destination by hostname, I can now troubleshoot the problem in this order:

1. Verify the client’s IPv4 address.
2. Verify the subnet mask.
3. Verify the default gateway.
4. Ping the default gateway.
5. Ping the DNS server by IP address.
6. Confirm the correct DNS server is configured.
7. Attempt to resolve the hostname.
8. Verify the DNS record exists.
9. Confirm that routing exists to the resolved destination.
10. Test the destination using its IPv4 address.

This helps separate a DNS failure from a routing or general connectivity failure.

---

## 🎯 Key Takeaways

The biggest lesson from this lab was that DNS does not forward user traffic.

DNS only returns the IPv4 address associated with a hostname. Once the client receives that address, normal routing and packet forwarding take over.

This lab also reinforced the importance of a default route. Even with the correct DNS server configured, the query would fail if R1 did not know how to reach the external network.

The troubleshooting distinction is:

```text
DNS identifies the address.
Routing reaches the address.
```

---

## ✅ Lab Status

**Day 38 Complete**

### Topics Covered

- Domain Name System
- DNS server configuration
- Client DNS settings
- Local hostname entries
- Default static routes
- Name resolution
- ICMP connectivity
- Packet Tracer Simulation Mode
- DNS troubleshooting
- Cisco IOS verification
