# Day 45 — Dynamic NAT & PAT

## Overview

Day 45 focused on configuring and comparing **Dynamic NAT** and **PAT (Port Address Translation / NAT Overload)**.

The lab demonstrated an important limitation of Dynamic NAT: the number of devices that can receive translations is limited by the number of available public IP addresses in the NAT pool.

After testing Dynamic NAT, I removed the configuration and switched R1 to PAT using its public interface IP address.

---

## Network Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT.png" alt="Day 45 Dynamic NAT and PAT Topology" width="900">
</p>

### Addressing

| Device | IP Address |
|---|---|
| PC1 | 172.16.0.1/24 |
| PC2 | 172.16.0.2/24 |
| PC3 | 172.16.0.3/24 |
| R1 G0/1 | 172.16.0.254/24 |
| R1 G0/0 | 203.0.113.1/30 |
| Internet Router | 203.0.113.2/30 |
| Server | 8.8.8.8 |
| NAT Pool | 100.0.0.1 - 100.0.0.2 |

---

## Lab Objectives

1. Configure Dynamic NAT on R1.
   - Configure the appropriate inside/outside interfaces.
   - Translate traffic from `172.16.0.0/24`.
   - Create a pool of `100.0.0.1` to `100.0.0.2`.

2. Ping `google.com` from PC1 and PC2, then ping it from PC3.
   - Determine what happens to PC3's traffic.

3. Clear the NAT translations and remove the Dynamic NAT configuration.
   - Switch the configuration to PAT using R1's public IP address.

4. Ping `google.com` from each PC.
   - Verify connectivity.
   - Examine the NAT translations on R1.

---

## Step 1 — Configure Dynamic NAT

First, I configured R1's LAN-facing interface as the NAT inside interface.

```cisco
R1(config)# interface g0/1
R1(config-if)# ip nat inside
R1(config-if)# exit
```

R1's Internet-facing interface was configured as the NAT outside interface.

```cisco
R1(config)# interface g0/0
R1(config-if)# ip nat outside
R1(config-if)# exit
```

I then created an ACL matching the entire `172.16.0.0/24` inside network.

```cisco
R1(config)# access-list 1 permit 172.16.0.0 0.0.0.255
```

Next, I created a Dynamic NAT pool containing two addresses.

```cisco
R1(config)# ip nat pool POOL1 100.0.0.1 100.0.0.2 netmask 255.255.255.0
```

The ACL was then associated with the NAT pool.

```cisco
R1(config)# ip nat inside source list 1 pool POOL1
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-1.1.png" alt="Dynamic NAT Configuration on R1" width="900">
</p>

---

## Step 2 — Test Dynamic NAT

The NAT pool only contains:

```text
100.0.0.1
100.0.0.2
```

However, the LAN contains three devices:

```text
PC1 — 172.16.0.1
PC2 — 172.16.0.2
PC3 — 172.16.0.3
```

I generated outside traffic from PC1.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-2.1.png" alt="PC1 Dynamic NAT Test" width="900">
</p>

I then generated outside traffic from PC2.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-2.2.png" alt="PC2 Dynamic NAT Test" width="900">
</p>

At this point, both addresses from the Dynamic NAT pool could be assigned.

Conceptually:

```text
172.16.0.1 → 100.0.0.1
172.16.0.2 → 100.0.0.2
```

I then attempted to generate traffic from PC3.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-2.3.png" alt="PC3 Dynamic NAT Test" width="900">
</p>

This demonstrated the limitation of Dynamic NAT.

Dynamic NAT uses a **one-to-one translation** from an inside local address to an available inside global address.

Because the pool only contains two addresses, a third device may be unable to receive a translation while both addresses are already allocated.

```text
PC1 → 100.0.0.1
PC2 → 100.0.0.2
PC3 → No available NAT pool address
```

---

## Step 3 — Examine NAT Translations

I examined the translation table on R1.

```cisco
R1# show ip nat translations
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-3.1.png" alt="Dynamic NAT Translation Table" width="900">
</p>

The NAT translation table contains four important address types:

| NAT Term | Meaning |
|---|---|
| Inside Local | Actual private address of the inside host |
| Inside Global | Address representing the inside host externally |
| Outside Local | Outside address as seen from the inside |
| Outside Global | Actual globally reachable address of the outside host |

For example:

```text
Inside Local:   172.16.0.1
Inside Global:  100.0.0.1
```

This allowed me to see exactly how R1 translated the private addresses before forwarding traffic toward the outside network.

---

## Step 4 — Clear Dynamic NAT

Before switching to PAT, I cleared the existing NAT translations.

```cisco
R1# clear ip nat translation *
```

I then removed the Dynamic NAT mapping.

```cisco
R1(config)# no ip nat inside source list 1 pool POOL1
```

The ACL could still be used because the same `172.16.0.0/24` network needed to be translated.

```cisco
access-list 1 permit 172.16.0.0 0.0.0.255
```

The inside and outside interface configuration also remained applicable.

---

## Step 5 — Configure PAT

Instead of translating hosts using a pool of public addresses, I configured PAT using R1's outside interface.

```cisco
R1(config)# ip nat inside source list 1 interface GigabitEthernet0/0 overload
```

The `overload` keyword enables PAT.

PAT allows multiple inside devices to share the same public IP address while using port numbers to distinguish their individual sessions.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-4.1.png" alt="PAT Configuration on R1" width="900">
</p>

---

## Step 6 — Verify PC1

I tested external connectivity from PC1.

```text
PC1> ping google.com
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-4.2.png" alt="PC1 PAT Test" width="900">
</p>

PC1 successfully reached the outside destination.

---

## Step 7 — Verify PC2

I then tested PC2.

```text
PC2> ping google.com
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-4.3.png" alt="PC2 PAT Test" width="900">
</p>

PC2 was also able to communicate externally.

---

## Step 8 — Verify PC3

Finally, I tested PC3.

```text
PC3> ping google.com
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-45-Lab-Dynamic-NAT-4.4.png" alt="PC3 PAT Test" width="900">
</p>

PC3 could now communicate externally as well.

Unlike the Dynamic NAT configuration, PAT was not restricted to the two-address pool.

All three internal devices could share R1's public IP address.

---

## Dynamic NAT vs PAT

| Feature | Dynamic NAT | PAT |
|---|---|---|
| Translation | One-to-One | Many-to-One |
| Public IP Usage | One public IP per active translation | Multiple hosts share one public IP |
| Port Numbers | Not required to distinguish hosts | Used to distinguish sessions |
| Address Pool | Required | Not required when using interface address |
| Pool Exhaustion | Possible | Much more scalable |
| Also Known As | Dynamic NAT | NAT Overload |

---

## Dynamic NAT Example

Dynamic NAT can create mappings such as:

```text
172.16.0.1 → 100.0.0.1
172.16.0.2 → 100.0.0.2
```

Once both addresses are allocated, another inside host may have to wait until an address becomes available.

This means:

```text
2 available public IP addresses
=
2 available one-to-one Dynamic NAT mappings
```

---

## PAT Example

PAT allows multiple internal hosts to use the same public address.

Conceptually:

```text
172.16.0.1:1024 → 203.0.113.1:1024
172.16.0.2:1025 → 203.0.113.1:1025
172.16.0.3:1026 → 203.0.113.1:1026
```

The public IP can remain the same:

```text
203.0.113.1
```

while different port numbers help identify the individual sessions.

This is why PAT is called:

```text
NAT Overload
```

---

## Important Commands

### Configure NAT Inside

```cisco
interface g0/1
 ip nat inside
```

### Configure NAT Outside

```cisco
interface g0/0
 ip nat outside
```

### Match the Inside Network

```cisco
access-list 1 permit 172.16.0.0 0.0.0.255
```

### Create the Dynamic NAT Pool

```cisco
ip nat pool POOL1 100.0.0.1 100.0.0.2 netmask 255.255.255.0
```

### Enable Dynamic NAT

```cisco
ip nat inside source list 1 pool POOL1
```

### Configure PAT

```cisco
ip nat inside source list 1 interface GigabitEthernet0/0 overload
```

### View NAT Translations

```cisco
show ip nat translations
```

### View NAT Statistics

```cisco
show ip nat statistics
```

### Clear NAT Translations

```cisco
clear ip nat translation *
```

---

## Key Takeaways

### Dynamic NAT

Dynamic NAT automatically selects an available public address from a configured pool.

The translation is essentially:

```text
Inside Local → Inside Global
```

The limitation is that the public pool contains a finite number of addresses.

In this lab:

```text
3 inside hosts
2 available NAT pool addresses
```

This allowed me to observe what happens when more hosts need translations than there are addresses available.

### PAT

PAT solves this scalability problem by allowing multiple private hosts to share one public IPv4 address.

Instead of relying only on IP addresses, PAT can distinguish connections using transport-layer information such as port numbers.

```text
Many Private Hosts
        ↓
One Public IPv4 Address
```

This dramatically reduces the number of public IPv4 addresses required.

---

## What I Practiced

- Dynamic NAT
- Dynamic NAT pools
- NAT inside interfaces
- NAT outside interfaces
- Standard ACLs for NAT
- Inside Local addresses
- Inside Global addresses
- Outside Local addresses
- Outside Global addresses
- NAT pool exhaustion
- NAT translation verification
- Clearing NAT translations
- Removing Dynamic NAT
- PAT
- NAT Overload
- Interface-based PAT
- Connectivity testing
- NAT troubleshooting

---

## Final Result

- ✅ Configured Dynamic NAT
- ✅ Configured NAT inside/outside interfaces
- ✅ Matched `172.16.0.0/24` using an ACL
- ✅ Created the `100.0.0.1 - 100.0.0.2` NAT pool
- ✅ Tested PC1
- ✅ Tested PC2
- ✅ Observed the Dynamic NAT pool limitation with PC3
- ✅ Examined NAT translations
- ✅ Cleared existing NAT translations
- ✅ Removed the Dynamic NAT configuration
- ✅ Configured PAT using R1's public interface
- ✅ Verified PC1 connectivity with PAT
- ✅ Verified PC2 connectivity with PAT
- ✅ Verified PC3 connectivity with PAT
- ✅ Compared Dynamic NAT and PAT behavior

---

## Day 45 Complete

**Dynamic NAT & PAT ✅**

The biggest takeaway from this lab was seeing why **PAT scales much better than Dynamic NAT**.

Dynamic NAT provides one-to-one translations from a limited pool of addresses.

PAT allows many internal devices to share a single public IPv4 address by distinguishing individual connections.

This lab helped connect the configuration commands with what is actually happening inside the router's NAT translation table.
