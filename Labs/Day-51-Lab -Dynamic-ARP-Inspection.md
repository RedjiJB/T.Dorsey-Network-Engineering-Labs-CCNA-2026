# Commit: Day 51 Complete — Dynamic ARP Inspection (DAI)

**Status:** ✅ Complete  
**Lab:** Jeremy's IT Lab — Day 51  
**Topic:** Dynamic ARP Inspection (DAI)  
**Exam Relevance:** CCNA 200-301

---

## Objective

Configure **R1 as a DHCP server**, enable **DHCP Snooping** on SW1 and SW2, and configure **Dynamic ARP Inspection (DAI)** to protect the LAN from invalid or spoofed ARP messages.

### Network

```text
192.168.1.0/24
```

### Requirements

- Configure R1 as the DHCP server
- Exclude `192.168.1.1 - 192.168.1.9`
- Default gateway: `192.168.1.1`
- Configure DHCP Snooping on SW1 and SW2
- Configure DAI on SW1 and SW2
- Enable all additional DAI validation checks
- Trust ports connected to another router or switch

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
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab%20-Dynamic-ARP-Inspection.png" width="900">
</p>

---

## Skills Practiced

- Configuring DHCP on a Cisco router
- Configuring DHCP Snooping
- Configuring Dynamic ARP Inspection
- Understanding trusted and untrusted DAI interfaces
- Using the DHCP Snooping binding table with DAI
- Enabling additional ARP validation checks
- Protecting against ARP spoofing
- Verifying DAI configuration
- Understanding Layer 2 security relationships

---

# Part 1 — Configure R1 as the DHCP Server

R1 was configured to provide DHCP services for:

```text
192.168.1.0/24
```

The first nine addresses were excluded:

```text
192.168.1.1 - 192.168.1.9
```

R1's address:

```text
192.168.1.1/24
```

also serves as the default gateway.

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

---

## Verify DHCP

```cisco
show running-config | section dhcp
show ip dhcp pool
```

The DHCP pool confirms:

```text
Pool POOL1

Network: 192.168.1.0/24
Default Router: 192.168.1.1
Excluded Range: 192.168.1.1 - 192.168.1.9
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab%20-Dynamic-ARP-Inspection-1.1.png" width="900">
</p>

---

# Part 2 — Configure DHCP Snooping

DAI works closely with **DHCP Snooping**.

DHCP Snooping builds a binding table containing legitimate mappings between:

```text
IP Address
MAC Address
VLAN
Interface
```

DAI can then use this information to determine whether an ARP message is legitimate.

---

## SW1 DHCP Snooping

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

SW1's G0/2 interface points toward the DHCP server on R1.

---

## SW2 DHCP Snooping

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

SW2 G0/1 points toward SW1 and ultimately toward the legitimate DHCP server.

---

# Part 3 — Configure Dynamic ARP Inspection

Dynamic ARP Inspection was enabled for VLAN 1 on both switches.

```cisco
ip arp inspection vlan 1
```

DAI inspects ARP messages received on **untrusted interfaces**.

The switch can compare information contained in the ARP message against trusted information learned through DHCP Snooping.

---

# SW1 DAI Configuration

SW1 connects to:

```text
G0/2 → R1
G0/1 → SW2
```

Because these ports connect to network infrastructure, both are configured as trusted for DAI.

```cisco
enable
configure terminal

ip arp inspection vlan 1

interface g0/1
 ip arp inspection trust

interface g0/2
 ip arp inspection trust

end
```

The running configuration confirms both interfaces are trusted.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab%20-Dynamic-ARP-Inspection-2.1.png" width="900">
</p>

---

# SW2 DAI Configuration

SW2 G0/1 connects to SW1.

Therefore, G0/1 is trusted for DAI.

```cisco
enable
configure terminal

ip arp inspection vlan 1

interface g0/1
 ip arp inspection trust

end
```

The PC-facing interfaces remain untrusted.

```text
F0/1 → PC1
F0/2 → PC2
F0/3 → PC3
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab%20-Dynamic-ARP-Inspection-2.2.png" width="900">
</p>

---

# Part 4 — Enable Additional DAI Validation Checks

DAI supports additional validation checks.

The lab required all three:

```text
Source MAC
Destination MAC
IP Address
```

Configure them on both SW1 and SW2:

```cisco
configure terminal

ip arp inspection validate src-mac dst-mac ip

end
```

---

## Source MAC Validation

```text
src-mac
```

Checks that the source MAC address in the Ethernet frame matches the sender MAC address contained in the ARP message.

Conceptually:

```text
Ethernet Frame
Source MAC
     ↓
     = ?
     ↓
ARP Sender MAC
```

A mismatch can indicate a forged ARP message.

---

## Destination MAC Validation

```text
dst-mac
```

Checks the destination MAC address of the Ethernet frame against the target MAC information in the ARP message when applicable.

---

## IP Validation

```text
ip
```

Performs additional checks on IP addresses contained inside ARP packets and rejects invalid ARP information.

---

# Part 5 — Understanding DAI Trust

DAI interfaces are either:

```text
TRUSTED
```

or:

```text
UNTRUSTED
```

By default, interfaces are **untrusted**.

In this topology:

```text
                  R1
                   |
                   |
            SW1 G0/2
             TRUSTED
                   |
                  SW1
                   |
            SW1 G0/1
             TRUSTED
                   |
            SW2 G0/1
             TRUSTED
                   |
                  SW2
               /   |   \
              /    |    \
            PC1   PC2   PC3
             |     |     |
         UNTRUSTED INTERFACES
```

The infrastructure links are trusted while the end-device interfaces remain untrusted.

---

# Part 6 — How DAI Works

When an ARP message enters an **untrusted interface**, DAI inspects it.

Conceptually:

```text
ARP Packet Arrives
       |
       v
Trusted Interface?
   /         \
 YES          NO
  |            |
Forward      Inspect
               |
               v
       Check DHCP Snooping
          Binding Table
               |
          +----+----+
          |         |
        VALID     INVALID
          |         |
       Forward     DROP
```

This allows the switch to prevent invalid ARP mappings from entering the network.

---

# DHCP Snooping + DAI

The relationship between the two security features is important.

### DHCP Snooping learns:

```text
IP Address ↔ MAC Address
```

For example:

```text
192.168.1.10 ↔ AAAA.BBBB.CCCC
```

DAI can then inspect an ARP message claiming:

```text
Sender IP:  192.168.1.10
Sender MAC: AAAA.BBBB.CCCC
```

If the information matches the DHCP Snooping binding:

```text
VALID → Forward
```

If an attacker sends:

```text
Sender IP:  192.168.1.10
Sender MAC: DEAD.BEEF.1234
```

the information does not match:

```text
INVALID → Drop
```

---

# Why DAI Is Important

ARP itself does not provide authentication.

A malicious device could send forged ARP messages claiming:

```text
"The default gateway's IP address belongs to my MAC address."
```

Other hosts could update their ARP tables with the false information.

This is known as:

```text
ARP Spoofing
```

or:

```text
ARP Poisoning
```

It can potentially enable a **Man-in-the-Middle attack**.

---

# ARP Spoofing Example

Without DAI:

```text
PC1
 |
 | "Who has 192.168.1.1?"
 |
 v

Attacker
 |
 | "192.168.1.1 is at ATTACKER-MAC"
 |
 v

PC1 ARP Table

192.168.1.1 → ATTACKER-MAC
```

PC1 may now send traffic intended for R1 to the attacker.

---

# With DAI

```text
Attacker
   |
   | Forged ARP
   v
SW2 Untrusted Port
   |
   v
DAI Inspection
   |
   v
Check DHCP Snooping Binding
   |
   X
Mismatch
   |
   v
DROP
```

The invalid ARP message does not reach the other hosts.

---

# Part 7 — Verify DAI on SW1

Use:

```cisco
show ip arp inspection interfaces
```

The output confirms:

```text
G0/1    Trusted
G0/2    Trusted
```

Other interfaces remain:

```text
Untrusted
```

The additional validation checks can also be verified.

```cisco
show ip arp inspection
```

The configuration shows:

```text
Source MAC Validation      : Enabled
Destination MAC Validation : Enabled
IP Address Validation      : Enabled
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab%20-Dynamic-ARP-Inspection-3.1.png" width="900">
</p>

---

# Part 8 — Verify DAI on SW2

Run:

```cisco
show ip arp inspection interfaces
show ip arp inspection
```

SW2 shows:

```text
G0/1 → Trusted
```

while the PC-facing ports remain:

```text
Untrusted
```

The additional validation checks are also enabled:

```text
Source MAC Validation      : Enabled
Destination MAC Validation : Enabled
IP Address Validation      : Enabled
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab%20-Dynamic-ARP-Inspection-3.2.png" width="900">
</p>

---

# Final Configurations

## R1

```cisco
enable
configure terminal

ip dhcp excluded-address 192.168.1.1 192.168.1.9

ip dhcp pool POOL1
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1

end
```

---

## SW1

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1
no ip dhcp snooping information option

ip arp inspection vlan 1
ip arp inspection validate src-mac dst-mac ip

interface g0/1
 ip arp inspection trust

interface g0/2
 ip dhcp snooping trust
 ip arp inspection trust

end
```

---

## SW2

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1
no ip dhcp snooping information option

ip arp inspection vlan 1
ip arp inspection validate src-mac dst-mac ip

interface g0/1
 ip dhcp snooping trust
 ip arp inspection trust

end
```

---

# Verification Commands

### DHCP Snooping

```cisco
show ip dhcp snooping
```

### DHCP Snooping Binding Table

```cisco
show ip dhcp snooping binding
```

### DAI Configuration

```cisco
show ip arp inspection
```

### DAI Interface Trust State

```cisco
show ip arp inspection interfaces
```

### DHCP Pool

```cisco
show ip dhcp pool
```

### DHCP Bindings

```cisco
show ip dhcp binding
```

---

# Important Commands

### Enable DAI

```cisco
ip arp inspection vlan 1
```

### Trust an Interface for DAI

```cisco
interface g0/1
 ip arp inspection trust
```

### Enable All Additional Validation Checks

```cisco
ip arp inspection validate src-mac dst-mac ip
```

### Enable DHCP Snooping

```cisco
ip dhcp snooping
ip dhcp snooping vlan 1
```

### Trust DHCP Server-Facing Port

```cisco
interface g0/2
 ip dhcp snooping trust
```

---

# Key Difference — DHCP Snooping vs DAI

| Feature | Protects Against | Main Information |
|---|---|---|
| DHCP Snooping | Rogue DHCP servers | DHCP messages |
| DAI | ARP spoofing/poisoning | ARP messages |
| DHCP Snooping Binding Table | Tracks legitimate clients | IP ↔ MAC ↔ VLAN ↔ Interface |

The two features work together:

```text
DHCP Snooping
      |
      v
Build Binding Table
      |
      v
IP ↔ MAC ↔ VLAN ↔ Interface
      |
      v
     DAI
      |
      v
Validate ARP Messages
```

---

# Lessons Learned

## 1. DAI Protects ARP

Dynamic ARP Inspection helps prevent malicious hosts from sending forged ARP messages.

```text
Invalid ARP → DROP
Valid ARP   → FORWARD
```

---

## 2. DAI Uses DHCP Snooping Information

DHCP Snooping provides trusted IP-to-MAC bindings.

DAI can use those bindings when inspecting ARP packets received on untrusted interfaces.

---

## 3. DAI Ports Are Untrusted by Default

End-user ports should generally remain untrusted.

In this lab:

```text
SW2 F0/1 → Untrusted
SW2 F0/2 → Untrusted
SW2 F0/3 → Untrusted
```

---

## 4. Infrastructure Links Are Trusted

The lab required ports connected to routers or switches to be trusted.

```text
SW1 G0/1 → Trusted
SW1 G0/2 → Trusted
SW2 G0/1 → Trusted
```

---

## 5. DAI Provides Additional Validation

The three additional checks configured were:

```text
src-mac
dst-mac
ip
```

Verified as:

```text
Source MAC Validation      : Enabled
Destination MAC Validation : Enabled
IP Address Validation      : Enabled
```

---

## 6. Layer 2 Security Features Work Together

The security features from these labs build on each other:

```text
Port Security
      +
DHCP Snooping
      +
Dynamic ARP Inspection
      =
Stronger Layer 2 Security
```

Each protects against a different type of attack.

---

# Final Verification

The completed lab successfully demonstrated:

- ✅ R1 configured as the DHCP server
- ✅ `192.168.1.1 - 192.168.1.9` excluded
- ✅ DHCP pool configured for `192.168.1.0/24`
- ✅ Default gateway configured as `192.168.1.1`
- ✅ DHCP Snooping enabled on SW1
- ✅ DHCP Snooping enabled on SW2
- ✅ DHCP trusted interfaces configured
- ✅ Dynamic ARP Inspection enabled
- ✅ DAI enabled for VLAN 1
- ✅ SW1 G0/1 trusted for DAI
- ✅ SW1 G0/2 trusted for DAI
- ✅ SW2 G0/1 trusted for DAI
- ✅ PC-facing interfaces remained untrusted
- ✅ Source MAC validation enabled
- ✅ Destination MAC validation enabled
- ✅ IP address validation enabled
- ✅ DAI configuration verified

---

# Day 51 Complete ✅

**Dynamic ARP Inspection (DAI) — DHCP Snooping, ARP Validation, Trusted Ports & ARP Spoofing Protection**
