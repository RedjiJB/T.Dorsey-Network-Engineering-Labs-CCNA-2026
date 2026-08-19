# Commit: Day 53 Complete — GRE Tunnels

**Status:** ✅ Complete  
**Lab:** Jeremy's IT Lab — Day 53  
**Topic:** GRE (Generic Routing Encapsulation) Tunnels  
**Exam Relevance:** CCNA 200-301

---

## Objective

Configure a **GRE tunnel between R1 and R2** across a service provider network, then configure **OSPF over the GRE tunnel** so that PC1 in Office A and PC2 in Office B can communicate.

### Requirements

1. Configure a GRE tunnel to connect R1 and R2.
2. Configure OSPF on the tunnel interfaces of R1 and R2.
3. Advertise the Office A and Office B LANs through OSPF.
4. Verify that PC1 and PC2 can communicate through the GRE tunnel.

---

## Topology

```text
Office A                                             Office B

10.0.1.0/24                                         10.0.2.0/24
     |                                                    |
    PC1                                                  PC2
 .100 |                                                    | .100
     SW1                                                  SW2
      |                                                    |
      R1                                                  R2
      | .2                                              .2 |
      |                                                    |
100.0.0.0/30                                        200.0.0.0/30
      |                                                    |
    SPR1 ---------------- Service Provider ------------- SPR2
     .1                                                    .1


             ===== GRE TUNNEL =====>

             192.168.1.0/30

             R1 .1 <-------> .2 R2
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels.png" width="900">
</p>

---

## Skills Practiced

- Configuring GRE tunnels
- Creating Cisco tunnel interfaces
- Configuring tunnel source and destination addresses
- Understanding GRE encapsulation
- Configuring IP addressing on tunnel interfaces
- Configuring OSPF over GRE
- Advertising remote LANs through OSPF
- Understanding overlay and underlay networks
- Verifying OSPF routes
- Verifying GRE connectivity
- Troubleshooting end-to-end communication

---

# Part 1 — Understanding GRE

GRE stands for:

```text
Generic Routing Encapsulation
```

GRE allows packets from one network to be encapsulated inside another IP packet and transported across an intermediate network.

In this lab:

```text
Office A
   |
   R1
   |
   |========= GRE Tunnel =========|
   |                               |
Service Provider Network           |
   |                               |
   R2
   |
Office B
```

The service provider routers do not need to know about the internal Office A and Office B networks.

The GRE tunnel creates a logical connection between:

```text
R1 <----------------------> R2
```

---

# Part 2 — Underlay Network

The physical/service-provider network is the **underlay**.

R1 connects to the service provider using:

```text
R1 G0/0/0
100.0.0.2/30
```

R2 connects using:

```text
R2 G0/0/0
200.0.0.2/30
```

The service provider-facing next hops are:

```text
R1 → 100.0.0.1
R2 → 200.0.0.1
```

R1 and R2 already have default routes allowing them to reach each other's public-facing addresses.

### R1

```cisco
ip route 0.0.0.0 0.0.0.0 100.0.0.1
```

### R2

```cisco
ip route 0.0.0.0 0.0.0.0 200.0.0.1
```

This underlay connectivity is required before the GRE tunnel can operate.

---

# Part 3 — GRE Tunnel Addressing

The GRE tunnel uses:

```text
192.168.1.0/30
```

Tunnel addresses:

```text
R1 Tunnel0 → 192.168.1.1/30
R2 Tunnel0 → 192.168.1.2/30
```

The tunnel therefore appears logically as:

```text
R1                                  R2

Tunnel0                            Tunnel0
192.168.1.1/30 ---------------- 192.168.1.2/30
                  GRE
```

---

# Part 4 — Configure GRE on R1

Create the tunnel interface:

```cisco
enable
configure terminal

interface tunnel 0
 ip address 192.168.1.1 255.255.255.252
 tunnel source gigabitEthernet0/0/0
 tunnel destination 200.0.0.2

end
```

### Tunnel Source

```cisco
tunnel source gigabitEthernet0/0/0
```

R1 uses its service-provider-facing interface as the GRE source.

### Tunnel Destination

```cisco
tunnel destination 200.0.0.2
```

The destination is R2's service-provider-facing IP address.

---

# Part 5 — Configure GRE on R2

Create the matching tunnel interface:

```cisco
enable
configure terminal

interface tunnel 0
 ip address 192.168.1.2 255.255.255.252
 tunnel source gigabitEthernet0/0/0
 tunnel destination 100.0.0.2

end
```

R2 uses:

```text
Source      → G0/0/0
Destination → 100.0.0.2
```

The tunnel destinations point to the **physical/underlay IP address of the opposite router**.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels-1.1.png" width="900">
</p>

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels-1.2.png" width="900">
</p>

---

# Part 6 — GRE Packet Flow

Suppose PC1 sends traffic to PC2:

```text
Source IP:      10.0.1.100
Destination IP: 10.0.2.100
```

R1 receives the packet and sends it through Tunnel0.

GRE encapsulates the original packet.

Conceptually:

```text
+--------------------------------------+
| Outer IP Header                      |
| Source:      100.0.0.2               |
| Destination: 200.0.0.2               |
+--------------------------------------+
| GRE Header                           |
+--------------------------------------+
| Original IP Packet                   |
| Source:      10.0.1.100              |
| Destination: 10.0.2.100              |
+--------------------------------------+
```

The service provider network only needs to route the **outer IP packet**.

When R2 receives it, the GRE information is removed and the original packet continues toward PC2.

---

# Part 7 — Configure OSPF Over GRE

Now that R1 and R2 have a logical tunnel connection, OSPF can operate across it.

The tunnel network is:

```text
192.168.1.0/30
```

OSPF allows the routers to dynamically learn the remote office LANs.

---

# Part 8 — Configure OSPF on R1

R1 needs to advertise:

```text
192.168.1.0/30 → GRE Tunnel
10.0.1.0/24    → Office A LAN
```

Configure OSPF:

```cisco
configure terminal

router ospf 1
 network 192.168.1.0 0.0.0.3 area 0
 network 10.0.1.1 0.0.0.0 area 0
 passive-interface gigabitEthernet0/0

end
```

The LAN-facing interface is made passive because there should be no OSPF neighbor on the PC LAN.

OSPF advertisements are still sent for the LAN network, but OSPF hello packets are not sent from that interface.

---

# Part 9 — Configure OSPF on R2

R2 needs to advertise:

```text
192.168.1.0/30 → GRE Tunnel
10.0.2.0/24    → Office B LAN
```

Configure:

```cisco
configure terminal

router ospf 1
 network 192.168.1.0 0.0.0.3 area 0
 network 10.0.2.1 0.0.0.0 area 0
 passive-interface gigabitEthernet0/0

end
```

R1 and R2 should now establish an OSPF adjacency through:

```text
Tunnel0
```

---

# Part 10 — Verify the Routing Table

On R1:

```cisco
show ip route
```

The routing table shows the remote Office B network learned through OSPF:

```text
O 10.0.2.0/24 via 192.168.1.2, Tunnel0
```

The route tells R1:

```text
To reach 10.0.2.0/24
        ↓
Send traffic to 192.168.1.2
        ↓
Through Tunnel0
```

The GRE tunnel itself appears as directly connected:

```text
C 192.168.1.0/30 is directly connected, Tunnel0
L 192.168.1.1/32 is directly connected, Tunnel0
```

---

# Part 11 — Verify OSPF

Use:

```cisco
show ip ospf database
```

R1's OSPF database contains LSAs from both routers.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels-2.1.png" width="900">
</p>

R2 also learns OSPF information from R1.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels-2.2.png" width="900">
</p>

Additional useful verification commands:

```cisco
show ip ospf neighbor
show ip ospf interface tunnel 0
show ip route ospf
```

---

# Part 12 — Verify the GRE Tunnel

Check the tunnel interface:

```cisco
show interfaces tunnel 0
```

You can also verify the tunnel configuration:

```cisco
show running-config interface tunnel 0
```

Expected R1 configuration:

```text
interface Tunnel0
 ip address 192.168.1.1 255.255.255.252
 tunnel source GigabitEthernet0/0/0
 tunnel destination 200.0.0.2
```

Expected R2 configuration:

```text
interface Tunnel0
 ip address 192.168.1.2 255.255.255.252
 tunnel source GigabitEthernet0/0/0
 tunnel destination 100.0.0.2
```

---

# Part 13 — Test PC1 to PC2

From PC1:

```text
ping 10.0.2.100
```

The first attempt may lose packets while the network finishes learning ARP information.

After convergence, the ping succeeds:

```text
Reply from 10.0.2.100
Reply from 10.0.2.100
Reply from 10.0.2.100
Reply from 10.0.2.100

Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-53-Lab-GRE-Tunnels-2.3.png" width="900">
</p>

This confirms successful end-to-end connectivity:

```text
PC1
 |
10.0.1.0/24
 |
R1
 |
Tunnel0
 |
====== GRE ======
 |
Tunnel0
 |
R2
 |
10.0.2.0/24
 |
PC2
```

---

# Final Configuration

## R1

```cisco
enable
configure terminal

interface tunnel 0
 ip address 192.168.1.1 255.255.255.252
 tunnel source gigabitEthernet0/0/0
 tunnel destination 200.0.0.2

router ospf 1
 network 192.168.1.0 0.0.0.3 area 0
 network 10.0.1.1 0.0.0.0 area 0
 passive-interface gigabitEthernet0/0

end
```

---

## R2

```cisco
enable
configure terminal

interface tunnel 0
 ip address 192.168.1.2 255.255.255.252
 tunnel source gigabitEthernet0/0/0
 tunnel destination 100.0.0.2

router ospf 1
 network 192.168.1.0 0.0.0.3 area 0
 network 10.0.2.1 0.0.0.0 area 0
 passive-interface gigabitEthernet0/0

end
```

---

# Verification Commands

### GRE Tunnel

```cisco
show interfaces tunnel 0
```

### Tunnel Configuration

```cisco
show running-config interface tunnel 0
```

### OSPF Neighbors

```cisco
show ip ospf neighbor
```

### OSPF Database

```cisco
show ip ospf database
```

### OSPF Routes

```cisco
show ip route ospf
```

### Full Routing Table

```cisco
show ip route
```

### End-to-End Connectivity

From PC1:

```text
ping 10.0.2.100
```

---

# GRE Underlay vs Overlay

One of the most important concepts from this lab is understanding the difference between the **underlay** and **overlay**.

### Underlay

The real routed network:

```text
R1 → SPR1 → SPR2 → R2
```

Uses:

```text
100.0.0.0/30
200.0.0.0/30
```

### Overlay

The logical GRE connection:

```text
R1 Tunnel0 ================= R2 Tunnel0

192.168.1.1                  192.168.1.2
```

OSPF operates across this logical connection.

---

# GRE Does Not Provide Encryption

GRE creates a tunnel, but GRE itself does **not encrypt traffic**.

```text
GRE = Encapsulation
GRE ≠ Encryption
```

GRE can transport traffic across another IP network, but additional technologies such as IPsec are required when encryption is needed.

---

# Key Commands

### Create Tunnel

```cisco
interface tunnel 0
```

### Assign Tunnel IP

```cisco
ip address 192.168.1.1 255.255.255.252
```

### Configure Tunnel Source

```cisco
tunnel source gigabitEthernet0/0/0
```

### Configure Tunnel Destination

```cisco
tunnel destination 200.0.0.2
```

### Advertise Tunnel Through OSPF

```cisco
network 192.168.1.0 0.0.0.3 area 0
```

### Verify Tunnel

```cisco
show interfaces tunnel 0
```

### Verify OSPF

```cisco
show ip ospf neighbor
show ip ospf database
```

---

# Lessons Learned

## 1. GRE Creates a Logical Point-to-Point Connection

Even though R1 and R2 are separated by a service provider network, GRE makes them appear logically connected.

```text
R1 ======================== R2
          GRE Tunnel
```

---

## 2. The Underlay Must Work First

Before GRE can function, R1 must be able to reach R2's tunnel destination and R2 must be able to reach R1's tunnel destination.

```text
Underlay connectivity
        ↓
GRE Tunnel
        ↓
Routing Protocol
        ↓
End-to-End Connectivity
```

---

## 3. Routing Protocols Can Operate Through GRE

OSPF treats the GRE tunnel as another Layer 3 interface.

```text
R1
 |
Tunnel0
 |
OSPF
 |
Tunnel0
 |
R2
```

This allows routes from remote locations to be dynamically exchanged.

---

## 4. Tunnel IPs and Tunnel Destinations Are Different

The tunnel IP address identifies the logical interface:

```text
R1 → 192.168.1.1
R2 → 192.168.1.2
```

The tunnel destination identifies the remote router's reachable **underlay address**:

```text
R1 destination → 200.0.0.2
R2 destination → 100.0.0.2
```

These serve completely different purposes.

---

## 5. OSPF Learns the Remote LAN Through the Tunnel

R1 learns:

```text
10.0.2.0/24 → Tunnel0
```

R2 learns:

```text
10.0.1.0/24 → Tunnel0
```

This allows Office A and Office B to communicate without the service provider learning the internal office networks.

---

# Final Verification

The completed lab successfully demonstrated:

- ✅ GRE tunnel configured between R1 and R2
- ✅ Tunnel0 configured on both routers
- ✅ R1 tunnel address configured as `192.168.1.1/30`
- ✅ R2 tunnel address configured as `192.168.1.2/30`
- ✅ Correct tunnel source interfaces configured
- ✅ Correct remote tunnel destinations configured
- ✅ OSPF configured over the GRE tunnel
- ✅ Office A LAN advertised into OSPF
- ✅ Office B LAN advertised into OSPF
- ✅ OSPF adjacency established through Tunnel0
- ✅ Remote LAN routes learned dynamically
- ✅ OSPF database verified
- ✅ GRE routes verified in the routing table
- ✅ PC1 successfully reached PC2
- ✅ Final ping completed with 0% packet loss

---

# Day 53 Complete ✅

**GRE Tunnels — Overlay Networking, Tunnel Interfaces & OSPF over GRE**
