# CCNA Day 44: Static NAT

## Overview

Day 44 of my CCNA studies focused on **Static Network Address Translation (Static NAT)**.

In this Packet Tracer lab, I configured R1 to translate the private IP addresses of three internal PCs to dedicated inside global addresses. I then tested connectivity to an external server, generated ICMP and DNS traffic, examined the NAT translation table, and cleared the NAT translations to observe which entries remained.

---

## Network Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-%26-TFTP.png" width="900">
</p>

### Addressing

| Device | Interface | IP Address |
|---|---|---|
| PC1 | NIC | 172.16.0.1/24 |
| PC2 | NIC | 172.16.0.2/24 |
| PC3 | NIC | 172.16.0.3/24 |
| R1 | G0/1 | 172.16.0.254/24 |
| R1 | G0/0 | 203.0.113.1/30 |
| Internet Router | G0/0 | 203.0.113.2/30 |
| Server | NIC | 8.8.8.8 |

### Static NAT Mappings

| Inside Local | Inside Global |
|---|---|
| 172.16.0.1 | 100.0.0.1 |
| 172.16.0.2 | 100.0.0.2 |
| 172.16.0.3 | 100.0.0.3 |

---

# Lab Objectives

1. Attempt to ping from PC1 to `8.8.8.8`.
2. Configure Static NAT on R1.
   - Configure the appropriate inside/outside interfaces.
   - Map PC1, PC2, and PC3 to `100.0.0.x/24`.
3. Ping `8.8.8.8` from PC1 again.
4. Ping `google.com` from each PC and check the NAT translations on R1.
5. Clear the NAT translations on R1 and determine which entries remain.

---

# 1. Initial Connectivity Test

Before configuring NAT, I attempted to ping `8.8.8.8` from PC1.

```text
C:\>ping 8.8.8.8
```

The ping failed.

```text
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
```

This demonstrated that PC1 could not successfully communicate with the outside network before NAT was configured.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-1.1.png" width="900">
</p>

---

# 2. Configure Static NAT on R1

First, I configured the LAN-facing interface as the **NAT inside** interface.

```text
R1#configure terminal

R1(config)#interface g0/1
R1(config-if)#ip nat inside
R1(config-if)#exit
```

Next, I configured the Internet-facing interface as the **NAT outside** interface.

```text
R1(config)#interface g0/0
R1(config-if)#ip nat outside
R1(config-if)#exit
```

I then created a permanent Static NAT mapping for each PC.

```text
R1(config)#ip nat inside source static 172.16.0.1 100.0.0.1
R1(config)#ip nat inside source static 172.16.0.2 100.0.0.2
R1(config)#ip nat inside source static 172.16.0.3 100.0.0.3
```

The resulting mappings were:

```text
172.16.0.1 → 100.0.0.1
172.16.0.2 → 100.0.0.2
172.16.0.3 → 100.0.0.3
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-2.1.png" width="900">
</p>

---

# 3. Verify the Static NAT Configuration

I verified the NAT translation table using:

```text
R1#show ip nat translations
```

The three Static NAT entries appeared:

```text
Pro  Inside global   Inside local    Outside local   Outside global
---  100.0.0.1       172.16.0.1      ---             ---
---  100.0.0.2       172.16.0.2      ---             ---
---  100.0.0.3       172.16.0.3      ---             ---
```

I also checked the NAT statistics:

```text
R1#show ip nat statistics
```

The output confirmed:

```text
Total translations: 3 (3 static, 0 dynamic, 0 extended)

Outside Interfaces:
GigabitEthernet0/0

Inside Interfaces:
GigabitEthernet0/1
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-3.png" width="900">
</p>

---

# 4. Test Connectivity After Configuring NAT

I returned to PC1 and attempted the ping again.

```text
C:\>ping 8.8.8.8
```

This time, the ping succeeded.

```text
Reply from 8.8.8.8
Reply from 8.8.8.8
Reply from 8.8.8.8
Reply from 8.8.8.8
```

Static NAT was now translating PC1:

```text
Inside Local:  172.16.0.1
Inside Global: 100.0.0.1
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-4.1.png" width="900">
</p>

---

# 5. Generate Traffic from PC1

Next, I pinged `google.com` from PC1.

```text
C:\>ping google.com
```

The hostname successfully resolved and PC1 received replies.

This generated additional NAT translation entries for the traffic.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-4.2.png" width="900">
</p>

---

# 6. Generate Traffic from PC2

I repeated the test from PC2.

```text
C:\>ping google.com
```

PC2 successfully communicated with the external destination.

Its Static NAT mapping was:

```text
Inside Local:  172.16.0.2
Inside Global: 100.0.0.2
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-4.3.png" width="900">
</p>

---

# 7. Generate Traffic from PC3

Finally, I tested PC3.

```text
C:\>ping google.com
```

PC3 also successfully communicated with the external destination.

Its Static NAT mapping was:

```text
Inside Local:  172.16.0.3
Inside Global: 100.0.0.3
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-4.4.png" width="900">
</p>

---

# 8. Examine the NAT Translation Table

After generating traffic from all three PCs, I checked the translation table again.

```text
R1#show ip nat translations
```

The router displayed the permanent Static NAT mappings along with protocol-specific translations generated by the traffic.

The permanent mappings were:

```text
100.0.0.1 ↔ 172.16.0.1
100.0.0.2 ↔ 172.16.0.2
100.0.0.3 ↔ 172.16.0.3
```

Additional **ICMP translations** appeared because of the ping traffic.

Additional **UDP translations** appeared because DNS queries were generated when the PCs attempted to resolve `google.com`.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-5.png" width="900">
</p>

---

# 9. Understanding the NAT Address Types

The `show ip nat translations` command displays four important address types.

### Inside Local

The actual IP address assigned to the host on the internal network.

```text
172.16.0.1
172.16.0.2
172.16.0.3
```

### Inside Global

The globally represented address NAT uses for the inside host.

```text
100.0.0.1
100.0.0.2
100.0.0.3
```

### Outside Local

The address of the outside host as it appears from the perspective of the inside network.

### Outside Global

The actual address assigned to the outside host.

---

# 10. Clear the NAT Translations

Finally, I cleared the NAT translation entries.

```text
R1#clear ip nat translation *
```

I then checked the translation table again.

```text
R1#show ip nat translations
```

The temporary ICMP and UDP translation entries were removed.

However, the configured Static NAT mappings remained:

```text
Pro  Inside global   Inside local    Outside local   Outside global
---  100.0.0.1       172.16.0.1      ---             ---
---  100.0.0.2       172.16.0.2      ---             ---
---  100.0.0.3       172.16.0.3      ---             ---
```

### Which entries remained?

```text
100.0.0.1 ↔ 172.16.0.1
100.0.0.2 ↔ 172.16.0.2
100.0.0.3 ↔ 172.16.0.3
```

The **Static NAT mappings remained** because they were manually configured in R1's configuration.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-44-Lab-Static-NAT-5.png" width="900">
</p>

---

# Full R1 NAT Configuration

```text
enable
configure terminal

interface GigabitEthernet0/1
 ip nat inside
 exit

interface GigabitEthernet0/0
 ip nat outside
 exit

ip nat inside source static 172.16.0.1 100.0.0.1
ip nat inside source static 172.16.0.2 100.0.0.2
ip nat inside source static 172.16.0.3 100.0.0.3

end
```

---

# Verification Commands

```text
show ip nat translations
show ip nat statistics
```

Clear translations:

```text
clear ip nat translation *
```

---

# Key Takeaways

- **Static NAT** creates a permanent one-to-one IP address mapping.
- **Inside Local** is the actual address assigned to the internal device.
- **Inside Global** is the address representing that internal device to the outside network.
- `ip nat inside` identifies the LAN-facing interface.
- `ip nat outside` identifies the WAN-facing interface.
- `ip nat inside source static` creates a permanent Static NAT mapping.
- Static mappings appear in the NAT table even when no traffic is actively being translated.
- ICMP traffic can generate protocol-specific NAT entries.
- DNS queries can generate UDP NAT entries.
- `show ip nat translations` displays the translation table.
- `show ip nat statistics` provides additional NAT information.
- Clearing translations removes temporary traffic entries, while the configured Static NAT mappings remain.

---

# Troubleshooting Workflow

```text
1. Verify host IP addresses
        ↓
2. Verify default gateways
        ↓
3. Verify router interfaces
        ↓
4. Verify routing
        ↓
5. Verify ip nat inside
        ↓
6. Verify ip nat outside
        ↓
7. Verify Static NAT mappings
        ↓
8. Generate traffic
        ↓
9. show ip nat translations
        ↓
10. show ip nat statistics
```

---

# What I Practiced

- Static NAT
- Network Address Translation
- Inside Local addresses
- Inside Global addresses
- NAT inside/outside interfaces
- One-to-one IP mappings
- ICMP connectivity testing
- DNS traffic
- NAT translation tables
- NAT statistics
- Clearing NAT translations
- Cisco IOS verification
- Cisco IOS troubleshooting

---

# Day 44 Complete

Day 44 gave me hands-on experience configuring and troubleshooting **Static NAT** in Cisco IOS.

The biggest takeaway from this lab was understanding the relationship between:

```text
Inside Local
     ↓
NAT Translation
     ↓
Inside Global
```

and seeing how permanent Static NAT mappings behave differently from the temporary protocol-specific translations generated by actual network traffic.
