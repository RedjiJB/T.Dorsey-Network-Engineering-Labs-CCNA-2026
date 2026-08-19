# Day 50 Complete — DHCP Snooping

**Status:** ✅ Complete  
**Lab:** Jeremy's IT Lab — Day 50  
**Topic:** DHCP Snooping  
**Exam Relevance:** CCNA 200-301

---

## Objective

Configure **R1 as a DHCP server**, enable **DHCP Snooping** on SW1 and SW2, configure the correct trusted interfaces, troubleshoot a failed DHCP lease, and identify why DHCP Snooping initially prevents PC1 from receiving an IP address.

### Network

```text
192.168.1.0/24
```

### DHCP Requirements

- DHCP Server: **R1**
- Default Gateway: **192.168.1.1**
- Excluded Addresses: **192.168.1.1 – 192.168.1.9**
- DHCP Clients: **PC1, PC2, PC3**

### DHCP Snooping Requirements

- Enable DHCP Snooping on **SW1**
- Enable DHCP Snooping on **SW2**
- Trust the uplink interfaces
- Troubleshoot the failed DHCP process

---

## Topology

```text
                                      PC1
                                       |
                                      F0/1
                                       |
R1 G0/0 ---- G0/2 SW1 G0/1 ---- G0/1 SW2 ---- F0/2 ---- PC2
                                       |
                                      F0/3
                                       |
                                      PC3

                192.168.1.0/24
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping.png width="900">
</p>

---

## Skills Practiced

- Configuring a Cisco router as a DHCP server
- Creating a DHCP address pool
- Excluding addresses from DHCP allocation
- Configuring a DHCP default gateway
- Enabling DHCP Snooping
- Configuring DHCP Snooping trusted interfaces
- Understanding trusted vs untrusted switch ports
- Troubleshooting DHCP failures
- Understanding DHCP Discover, Offer, Request, and ACK
- Identifying DHCP Snooping drops
- Understanding the DHCP Snooping Information Option / Option 82
- Using `ipconfig /renew`
- Verifying switch and router configurations

---

# Part 1 — Configure R1 as the DHCP Server

R1 was configured as the DHCP server for:

```text
192.168.1.0/24
```

R1's G0/0 interface uses:

```text
192.168.1.1/24
```

This address also serves as the default gateway for the PCs.

The first nine addresses were excluded from DHCP allocation:

```text
192.168.1.1 - 192.168.1.9
```

### R1 Configuration

```cisco
enable
configure terminal

ip dhcp excluded-address 192.168.1.1 192.168.1.9

ip dhcp pool POOL1
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1
end
```

The DHCP pool therefore provides addresses beginning after the excluded range.

```text
192.168.1.10
192.168.1.11
192.168.1.12
...
```

---

## Verify the DHCP Configuration

The DHCP configuration was verified on R1.

```cisco
show running-config | section dhcp
```

The configuration showed:

```text
ip dhcp excluded-address 192.168.1.1 192.168.1.9

ip dhcp pool POOL1
 default-router 192.168.1.1
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping-1.1.png" width="900">
</p>

R1 was now ready to dynamically provide IPv4 addresses to the PCs.

---

# Part 2 — Configure DHCP Snooping

DHCP Snooping was enabled on both SW1 and SW2.

DHCP Snooping is a Layer 2 security feature designed to protect a network from unauthorized or rogue DHCP servers.

The switch classifies interfaces as either:

```text
Trusted
```

or:

```text
Untrusted
```

By default, switch interfaces are **untrusted**.

---

## SW1 Configuration

SW1's connection toward the legitimate DHCP server is:

```text
SW1 G0/2 → R1 G0/0
```

Therefore, G0/2 must be trusted.

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1

interface g0/2
 ip dhcp snooping trust
end
```

SW1 G0/1 connects downstream toward SW2 and does not need to be trusted for DHCP server messages entering SW1 because legitimate DHCP server responses enter SW1 through G0/2.

---

## SW2 Configuration

SW2 receives legitimate DHCP server responses from SW1 through:

```text
SW2 G0/1
```

Therefore, G0/1 must be configured as trusted.

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1

interface g0/1
 ip dhcp snooping trust
end
```

The client-facing interfaces remain untrusted:

```text
F0/1 → PC1
F0/2 → PC2
F0/3 → PC3
```

This is intentional.

---

## Trusted vs Untrusted Ports

The resulting DHCP Snooping trust design is:

```text
DHCP SERVER
    R1
     |
     | DHCP OFFER / ACK
     |
SW1 G0/2
  TRUSTED
     |
    SW1
     |
SW1 G0/1
     |
     |
SW2 G0/1
  TRUSTED
     |
    SW2
   / | \
  /  |  \
PC1 PC2 PC3
UNTRUSTED
```

DHCP server messages should only be accepted when they arrive on trusted interfaces.

---

## Verify SW1

The running configuration confirmed that SW1 G0/2 was trusted.

```cisco
show running-config
```

The relevant configuration was:

```text
interface GigabitEthernet0/1
!
interface GigabitEthernet0/2
 ip dhcp snooping trust
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping-2.1.png" width="900">
</p>

---

## Verify SW2

SW2's G0/1 interface was also configured as trusted.

```cisco
interface GigabitEthernet0/1
 ip dhcp snooping trust
```

The client-facing FastEthernet ports remained untrusted.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping-2.2.png" width="900">
</p>

This creates the expected trust boundary:

```text
R1 ← trusted → SW1 ← trusted path → SW2 ← untrusted → PCs
```

---

# Part 3 — Request an IP Address from PC1

With DHCP Snooping enabled, PC1 attempted to obtain an IP address using:

```powershell
ipconfig /renew
```

Instead of receiving an address, PC1 returned:

```text
DHCP request failed.
```

Repeated attempts produced the same result.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping-3.1.png" width="900">
</p>

At this point, the DHCP server itself was configured correctly and the trusted ports were configured correctly.

However, DHCP still failed.

This required troubleshooting the interaction between **Packet Tracer's DHCP server behavior and DHCP Snooping**.

---

# Part 4 — Why Did DHCP Fail?

The issue involved the **DHCP Snooping Information Option**, also known as:

```text
DHCP Option 82
```

DHCP Snooping can insert Option 82 information into DHCP messages.

Option 82 provides information about where a DHCP request entered the network.

Conceptually:

```text
PC1
 |
 | DHCP Discover
 v
SW2
 |
 | DHCP Snooping / Option 82
 v
SW1
 |
 v
R1 DHCP Server
```

In this Packet Tracer lab, the inserted DHCP Snooping information caused the DHCP process to fail.

The PC therefore could not complete the normal DHCP exchange:

```text
DISCOVER
   ↓
OFFER
   ↓
REQUEST
   ↓
ACK
```

Instead:

```text
PC1
 |
 | DHCP Discover
 v
SW2
 |
 | DHCP Snooping processing
 v
DHCP process fails
 |
 v
PC1 receives no lease
```

---

# Part 5 — Identify the DHCP Snooping Problem

Simulation mode was used to inspect the DHCP traffic.

The packet was observed as a Layer 2 broadcast:

```text
Destination MAC:
FFFF.FFFF.FFFF
```

This is expected because a DHCP client initially does not know the address of the DHCP server.

The switch also identified the DHCP packet while DHCP Snooping was active.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping-4.1.png" width="900">
</p>

The troubleshooting process showed that simply trusting the uplinks was not enough.

A DHCP Snooping configuration change was required.

---

# Part 6 — Disable DHCP Snooping Information Option

The necessary fix was to disable insertion of the DHCP Snooping Information Option.

On both switches:

```cisco
configure terminal

no ip dhcp snooping information option

end
```

The resulting configuration includes:

```text
no ip dhcp snooping information option
```

This prevents the switch from inserting Option 82 information into the DHCP messages.

---

## SW1 Final DHCP Snooping Configuration

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1
no ip dhcp snooping information option

interface g0/2
 ip dhcp snooping trust

end
```

---

## SW2 Final DHCP Snooping Configuration

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1
no ip dhcp snooping information option

interface g0/1
 ip dhcp snooping trust

end
```

---

# Part 7 — Renew PC1's Address Again

After disabling DHCP Snooping Option 82 insertion, PC1 attempted another renewal.

```powershell
ipconfig /renew
```

This time the DHCP request succeeded.

PC1 received:

```text
IP Address...............: 192.168.1.12
Subnet Mask..............: 255.255.255.0
Default Gateway..........: 192.168.1.1
```

<p align="center">
  <img src="Lab-Photos/Day-50-Lab-DHCP-Snooping-4.1.png" width="900">
</p>

This confirmed that the DHCP server and DHCP Snooping configuration were now functioning correctly.

---

# DHCP Process

The successful DHCP exchange follows the DORA process:

```text
D = Discover
O = Offer
R = Request
A = Acknowledge
```

### Step 1 — DHCP Discover

PC1 does not have an IP address or know the DHCP server.

It sends:

```text
DHCP DISCOVER
```

as a broadcast.

```text
PC1
 |
 | DISCOVER
 v
SW2
 |
 v
SW1
 |
 v
R1
```

---

### Step 2 — DHCP Offer

R1 receives the request and offers an available address from the pool.

Example:

```text
192.168.1.12
```

```text
R1
 |
 | OFFER
 v
SW1
 |
 v
SW2
 |
 v
PC1
```

Because the DHCP Offer originates from the DHCP server, it must enter the switches through trusted ports.

---

### Step 3 — DHCP Request

PC1 requests the offered address.

```text
PC1
 |
 | REQUEST
 v
R1
```

---

### Step 4 — DHCP ACK

R1 confirms the lease using a DHCP ACK.

```text
R1
 |
 | ACK
 v
PC1
```

PC1 can now configure:

```text
IP Address
Subnet Mask
Default Gateway
```

---

# Why DHCP Snooping Uses Trusted Ports

One of the primary purposes of DHCP Snooping is protection against **rogue DHCP servers**.

Without DHCP Snooping:

```text
Legitimate DHCP Server
        |
        v
      Switch
        ^
        |
Rogue DHCP Server
```

Both devices could potentially respond to clients.

A rogue server could provide malicious information such as:

```text
Incorrect Default Gateway
Incorrect DNS Server
Incorrect Network Configuration
```

This could redirect client traffic through an attacker-controlled system.

---

## With DHCP Snooping

DHCP Snooping establishes a trust boundary.

```text
                R1
         Legitimate DHCP
                |
          TRUSTED PORT
                |
               SW1
                |
          TRUSTED PATH
                |
               SW2
           /    |    \
          /     |     \
       PC1     PC2    PC3
     UNTRUSTED PORTS
```

DHCP server messages received on untrusted interfaces can be dropped.

---

# Trusted Port Rule

A useful rule from this lab is:

```text
Trust ports toward the legitimate DHCP server.
```

For this topology:

```text
SW1 G0/2 → Trusted
SW2 G0/1 → Trusted
```

The PC-facing ports remain:

```text
Untrusted
```

---

# DHCP Snooping Binding Table

DHCP Snooping can dynamically build a binding table containing information about legitimate DHCP clients.

A binding can associate:

```text
MAC Address
IP Address
Lease Time
VLAN
Interface
```

The table can be viewed with:

```cisco
show ip dhcp snooping binding
```

This information can also be used by other Layer 2 security mechanisms.

---

# Verification Commands

### Verify DHCP Snooping

```cisco
show ip dhcp snooping
```

### View DHCP Snooping Bindings

```cisco
show ip dhcp snooping binding
```

### Check Running Configuration

```cisco
show running-config
```

### Check DHCP Configuration on R1

```cisco
show running-config | section dhcp
```

### View DHCP Bindings on R1

```cisco
show ip dhcp binding
```

### Renew DHCP Address on PC

```powershell
ipconfig /renew
```

### View PC IP Configuration

```powershell
ipconfig
```

---

# Important Commands

### Enable DHCP Snooping

```cisco
ip dhcp snooping
```

### Enable DHCP Snooping for VLAN 1

```cisco
ip dhcp snooping vlan 1
```

### Configure a Trusted Port

```cisco
interface g0/1
 ip dhcp snooping trust
```

### Disable Option 82 Insertion

```cisco
no ip dhcp snooping information option
```

### Configure DHCP Excluded Addresses

```cisco
ip dhcp excluded-address 192.168.1.1 192.168.1.9
```

### Create DHCP Pool

```cisco
ip dhcp pool POOL1
```

### Configure DHCP Network

```cisco
network 192.168.1.0 255.255.255.0
```

### Configure Default Gateway

```cisco
default-router 192.168.1.1
```

---

# Troubleshooting Flow

The lab demonstrated a useful DHCP troubleshooting process.

```text
PC receives no DHCP address
          |
          v
Check DHCP server configuration
          |
          v
Check DHCP pool
          |
          v
Check excluded addresses
          |
          v
Check DHCP Snooping
          |
          v
Check trusted interfaces
          |
          v
Inspect DHCP packets
          |
          v
Check Option 82 behavior
          |
          v
Disable information option
          |
          v
ipconfig /renew
          |
          v
DHCP SUCCESS
```

---

# Lessons Learned

## 1. DHCP Snooping Protects Against Rogue DHCP Servers

DHCP Snooping controls where DHCP server messages are allowed to enter the switched network.

This helps prevent unauthorized DHCP servers from distributing malicious network configuration.

---

## 2. Switch Ports Are Untrusted by Default

After DHCP Snooping is enabled, interfaces are considered untrusted unless explicitly configured otherwise.

Trusted ports must therefore be selected carefully.

---

## 3. Trust the Path Toward the DHCP Server

In this topology:

```text
R1 → SW1 → SW2 → PCs
```

The trusted interfaces are:

```text
SW1 G0/2
SW2 G0/1
```

These interfaces form the path back toward the legitimate DHCP server.

---

## 4. DHCP Snooping Can Affect Legitimate DHCP Traffic

Security features can cause connectivity problems when they are configured incorrectly or when additional behavior such as Option 82 affects the DHCP exchange.

This lab demonstrated that a network can have:

```text
Correct DHCP Server
+
Correct IP Network
+
Correct Physical Connectivity
```

and DHCP can still fail because of a Layer 2 security configuration.

---

## 5. Option 82 Was the Key Troubleshooting Point

The important fix in this lab was:

```cisco
no ip dhcp snooping information option
```

After applying the change, PC1 successfully received its DHCP lease.

---

## 6. Simulation Mode Helps Explain Packet Behavior

Packet Tracer simulation mode made it possible to observe DHCP packets as they crossed the switches.

Instead of only seeing:

```text
DHCP request failed.
```

the packet flow could be inspected to determine where the process was being interrupted.

---

# Final Verification

The completed lab successfully demonstrated:

- ✅ R1 configured as a DHCP server
- ✅ 192.168.1.1 – 192.168.1.9 excluded
- ✅ DHCP pool created for 192.168.1.0/24
- ✅ Default gateway configured as 192.168.1.1
- ✅ DHCP Snooping enabled on SW1
- ✅ DHCP Snooping enabled on SW2
- ✅ SW1 G0/2 configured as trusted
- ✅ SW2 G0/1 configured as trusted
- ✅ PC-facing interfaces left untrusted
- ✅ Initial DHCP failure reproduced
- ✅ DHCP packets inspected
- ✅ Option 82 behavior identified
- ✅ DHCP Snooping Information Option disabled
- ✅ PC1 successfully renewed its DHCP lease
- ✅ PC1 received 192.168.1.12/24
- ✅ PC1 received 192.168.1.1 as its default gateway
- ✅ DHCP Snooping troubleshooting completed

---

## Next Steps

Continue building on Layer 2 security by combining DHCP Snooping with other switch security mechanisms that use DHCP Snooping information to validate legitimate hosts and prevent spoofing attacks.

---

# Day 50 Complete ✅

**DHCP Snooping — Trusted Ports, Rogue DHCP Protection, Option 82 & Troubleshooting**
