# Day 42 — SSH: Secure Remote Access & Management

## 📖 Overview

Day 42 of my CCNA lab journey focused on configuring **SSH (Secure Shell)** for secure remote management of a Cisco switch.

In this lab, a newly installed switch (`SW2`) had no management configuration. I connected to the switch through its console port, configured its management SVI and security settings, enabled SSH, and then used an ACL to ensure that **only PC1** could remotely access the switch.

This lab combined several important CCNA concepts:

- Initial switch configuration
- Management IP addressing
- Switch default gateways
- Local username authentication
- Console security
- SSH configuration
- RSA key generation
- VTY line configuration
- Standard ACLs
- Management-plane access control
- Remote device administration

---

# 🖥️ Network Topology

The topology contains two LANs connected through R1 and R2.

```text
PC1
 |
SW1
 |
R1 -------- R2
              |
             SW2
              |
           Laptop1
```

### Addressing

| Device | Interface | Address |
|---|---|---|
| PC1 | NIC | `192.168.1.1/24` |
| R1 | G0/1 | `192.168.1.254/24` |
| R1 | G0/0 | `10.0.0.1/30` |
| R2 | G0/0 | `10.0.0.2/30` |
| R2 | G0/1 | `192.168.2.254/24` |
| SW1 | VLAN 1 | `192.168.1.253/24` |
| SW2 | VLAN 1 | `192.168.2.253/24` |

Laptop1 was connected directly to the **console port of SW2** for the initial configuration.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH.png" alt="Day 42 SSH Lab Topology" width="1000">
</p>

---

# 🎯 Lab Objectives

The goal was to configure the newly installed SW2 for secure local and remote administration.

### Initial SW2 Configuration

```text
Hostname: SW2
Enable secret: ccna
Username: jeremy
Password: ccna
VLAN 1 SVI: 192.168.2.253/24
Default gateway: R2 (192.168.2.254)
```

### Console Security

```text
Authentication: Local user
EXEC timeout: 5 minutes
```

### SSH Requirements

```text
Domain: jeremysitlab.com
RSA key size: 2048 bits
Authentication: Local user
EXEC timeout: 5 minutes
Protocol: SSH only
Remote access: PC1 ONLY
```

---

# Phase 1 — Initial Console Configuration

Because SW2 was newly added to the network and had no management configuration, Laptop1 was connected directly to its console port.

The first step was configuring the hostname:

```cisco
Switch>enable
Switch#configure terminal

Switch(config)#hostname SW2
SW2(config)#
```

The enable secret was configured:

```cisco
SW2(config)#enable secret ccna
```

A local user account was then created:

```cisco
SW2(config)#username jeremy secret ccna
```

This local account would later be used for both console and SSH authentication.

---

# Phase 2 — Configure the Management SVI

A Layer 2 switch requires a **Switch Virtual Interface (SVI)** to have an IP address for remote management.

VLAN 1 was configured with:

```cisco
SW2(config)#interface vlan 1
SW2(config-if)#ip address 192.168.2.253 255.255.255.0
SW2(config-if)#no shutdown
```

The switch now had a management address of:

```text
192.168.2.253/24
```

Because PC1 is located on a different network, SW2 also needed a default gateway.

```cisco
SW2(config)#ip default-gateway 192.168.2.254
```

R2's G0/1 interface at `192.168.2.254` serves as SW2's default gateway.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH-1.1.png" width="1000">
</p>

---

# 🧠 Why Does a Layer 2 Switch Need a Default Gateway?

SW2 does not perform routing.

It can communicate directly with devices inside:

```text
192.168.2.0/24
```

However, PC1 is located in:

```text
192.168.1.0/24
```

Therefore, traffic destined for PC1 must be sent to R2.

The command:

```cisco
ip default-gateway 192.168.2.254
```

tells SW2 where to send management traffic destined for remote networks.

---

# Phase 3 — Secure the Console Line

The console was configured to authenticate using the local username database.

```cisco
SW2(config)#line console 0
SW2(config-line)#login local
SW2(config-line)#exec-timeout 5 0
```

### `login local`

```cisco
login local
```

tells IOS to authenticate users using locally configured usernames and passwords.

In this lab:

```text
Username: jeremy
Password: ccna
```

### `exec-timeout 5 0`

```cisco
exec-timeout 5 0
```

means:

```text
5 minutes
0 seconds
```

If the console session remains inactive for five minutes, IOS terminates the session.

This prevents an unattended management session from remaining open indefinitely.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH-1.2.png" alt="SW2 Console Security Configuration" width="1000">
</p>

---

# Phase 4 — Prepare SW2 for SSH

SSH requires several components before it can operate.

The switch needs:

1. A hostname
2. A domain name
3. RSA keys
4. A local user account
5. VTY authentication
6. SSH permitted on the VTY lines
7. IP connectivity

The hostname was already configured:

```cisco
hostname SW2
```

The domain name was configured as:

```cisco
SW2(config)#ip domain-name jeremysitlab.com
```

---

# Phase 5 — Generate RSA Keys

SSH uses asymmetric cryptography.

RSA keys were generated with a modulus size of **2048 bits**.

```cisco
SW2(config)#crypto key generate rsa
```

When prompted for the modulus size:

```text
How many bits in the modulus [512]: 2048
```

The completed configuration gives SW2 the cryptographic keys necessary to support SSH.

---

# 🔐 Why RSA Keys Are Required

SSH provides encrypted communication between the administrator and network device.

Unlike Telnet, SSH does not send the management session as unencrypted plaintext.

The RSA key pair allows the switch to participate in the cryptographic processes required to establish the secure SSH connection.

This is one of the major reasons SSH is preferred over Telnet for network administration.

---

# Phase 6 — Configure the VTY Lines

Remote sessions enter Cisco devices through the **VTY lines**.

The VTY lines were configured for:

- Local authentication
- 5-minute timeout
- SSH only

```cisco
SW2(config)#line vty 0 4
SW2(config-line)#login local
SW2(config-line)#exec-timeout 5 0
SW2(config-line)#transport input ssh
```

The important security command is:

```cisco
transport input ssh
```

This prevents Telnet from being used on those VTY lines.

Only SSH connections are accepted.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH-2.1.png" alt="SW2 VTY SSH Configuration" width="1000">
</p>

---

# Telnet vs SSH

| Feature | Telnet | SSH |
|---|---|---|
| Encryption | ❌ No | ✅ Yes |
| Secure authentication | ❌ No | ✅ Yes |
| Default TCP port | 23 | 22 |
| CLI remote access | ✅ | ✅ |
| Recommended for production | ❌ | ✅ |

The biggest difference is encryption.

With Telnet, management traffic can potentially be intercepted and read.

SSH protects the remote administrative session through encryption.

---

# Phase 7 — Restrict SSH Access to PC1

The final requirement was especially important:

> **Only PC1 should be allowed to remotely access SW2.**

PC1 has the address:

```text
192.168.1.1
```

A standard ACL was created:

```cisco
SW2(config)#access-list 1 permit host 192.168.1.1
```

A standard ACL contains an implicit deny at the end.

Conceptually:

```text
permit host 192.168.1.1
deny any
```

Therefore, PC1 is permitted while other source IP addresses are denied.

---

# Phase 8 — Apply the ACL to the VTY Lines

Creating an ACL alone does not make it active.

The ACL must be applied to the appropriate location.

For management access, it was applied to the VTY lines:

```cisco
SW2(config)#line vty 0 4
SW2(config-line)#access-class 1 in
```

The completed VTY configuration included:

```cisco
line vty 0 4
 access-class 1 in
 exec-timeout 5 0
 login local
 transport input ssh
```

This means:

```text
PC1
 ↓
Standard ACL
 ↓
VTY
 ↓
SSH authentication
 ↓
SW2 CLI
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH-3.1.png" alt="Restricting SSH Access to PC1" width="1000">
</p>

---

# 🧠 `access-group` vs `access-class`

This lab reinforced an important Cisco distinction.

### `ip access-group`

Normally applies an ACL to traffic entering or leaving a physical or logical interface.

Example:

```cisco
interface g0/1
 ip access-group 10 in
```

### `access-class`

Applies an ACL specifically to management access through VTY lines.

Example:

```cisco
line vty 0 4
 access-class 1 in
```

For this lab, the goal was not to block PC traffic from crossing SW2.

The goal was specifically to control:

> **Who is allowed to remotely manage SW2?**

Therefore:

```cisco
access-class
```

was the correct tool.

---

# Phase 9 — Test SSH From PC1

PC1 was used to remotely connect to SW2.

The SSH command was:

```text
ssh -l jeremy 192.168.2.253
```

PC1 was prompted for the password:

```text
Password:
```

After authentication, the remote CLI session opened successfully.

```text
SW2>
```

Privileged EXEC mode could then be entered:

```cisco
SW2>enable
Password:
SW2#
```

This verified:

- Routing between the two LANs works
- SW2's default gateway works
- VLAN 1 management connectivity works
- SSH is operational
- Local authentication works
- The VTY configuration works
- PC1 is permitted by the ACL

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH-3.2.png" alt="Successful SSH Connection from PC1 to SW2" width="1000">
</p>

---

# 🔎 Verification

Several commands can be used to verify the configuration.

## Verify the Management Interface

```cisco
show ip interface brief
```

Expected result:

```text
Vlan1    192.168.2.253    YES manual    up    up
```

---

## Verify SSH

```cisco
show ip ssh
```

This can confirm whether SSH is enabled and display SSH-related parameters.

---

## Verify the ACL

```cisco
show access-lists
```

Expected ACL:

```text
Standard IP access list 1
    permit 192.168.1.1
```

---

## Verify VTY Configuration

```cisco
show running-config
```

Look for:

```cisco
line vty 0 4
 access-class 1 in
 exec-timeout 5 0
 login local
 transport input ssh
```

---

# 📋 Final SW2 Configuration

The major configuration commands from the lab can be summarized as:

```cisco
enable
configure terminal

hostname SW2

enable secret ccna

username jeremy secret ccna

interface vlan 1
 ip address 192.168.2.253 255.255.255.0
 no shutdown
exit

ip default-gateway 192.168.2.254

line console 0
 login local
 exec-timeout 5 0
exit

ip domain-name jeremysitlab.com

crypto key generate rsa
2048

access-list 1 permit host 192.168.1.1

line vty 0 4
 login local
 exec-timeout 5 0
 transport input ssh
 access-class 1 in
exit

end
```

---

# 🔐 Management-Plane Security

One of the most important concepts from this lab was that configuring SSH is only one part of securing a network device.

SW2 now has several layers of protection:

```text
Layer 1 — Local username/password authentication

Layer 2 — Enable secret protecting privileged EXEC mode

Layer 3 — SSH encryption

Layer 4 — VTY restricted to SSH only

Layer 5 — ACL restricting remote access to PC1

Layer 6 — EXEC timeout terminating inactive sessions
```

Together, these controls provide significantly stronger management-plane security than simply enabling remote access.

---

# 🛠️ Commands Practiced

```cisco
hostname SW2

enable secret ccna

username jeremy secret ccna

interface vlan 1
ip address 192.168.2.253 255.255.255.0
no shutdown

ip default-gateway 192.168.2.254

line console 0
login local
exec-timeout 5 0

ip domain-name jeremysitlab.com

crypto key generate rsa

line vty 0 4
login local
exec-timeout 5 0
transport input ssh
access-class 1 in

access-list 1 permit host 192.168.1.1

show ip interface brief
show ip ssh
show access-lists
show running-config
```

---

# 🧠 Troubleshooting Checklist

If SSH does not work, check:

1. Is the VLAN 1 SVI up/up?
2. Does SW2 have the correct management IP?
3. Is the default gateway configured?
4. Can the client ping SW2?
5. Is a hostname configured?
6. Is a domain name configured?
7. Were RSA keys generated?
8. Does the local username exist?
9. Does the VTY line use `login local`?
10. Does the VTY line permit SSH?
11. Is an ACL blocking the client?
12. Was `access-class` applied in the correct direction?

Useful commands:

```cisco
show ip interface brief
show running-config
show ip ssh
show access-lists
```

---

# 📚 Skills Practiced

- Cisco IOS CLI
- Initial switch configuration
- Layer 2 switch management
- Switch Virtual Interfaces
- Default gateways
- Local authentication
- Console security
- VTY configuration
- SSH
- RSA cryptography
- Remote network administration
- Standard ACLs
- `access-class`
- Management-plane security
- Secure device administration
- Cisco troubleshooting
- Configuration verification

---

# 🎯 Key Takeaways

The biggest takeaway from Day 42 was that **remote access and secure remote access are not the same thing**.

A network device might be remotely reachable, but proper administrative access should include:

```text
Authentication
      +
Encryption
      +
Authorization / Access Control
      +
Session Timeout
```

SSH provides encrypted remote access, `login local` provides authentication, `access-class` restricts which hosts can reach the VTY lines, and `exec-timeout` protects against abandoned sessions.

The final design allowed:

```text
PC1 (192.168.1.1)
        |
        | SSH
        ↓
   Routers R1/R2
        |
        ↓
SW2 (192.168.2.253)
        |
 Standard ACL 1
        |
        ↓
    VTY Lines
        |
        ↓
Local Authentication
```

Only the authorized PC was permitted to remotely administer SW2.

---

## ✅ Lab Status

**Day 42 Complete**

### Topics Covered

- SSH
- Secure remote administration
- Switch management
- VLAN 1 SVI
- Default gateways
- RSA keys
- Local authentication
- Console security
- VTY lines
- Standard ACLs
- `access-class`
- EXEC timeout
- Management-plane security
- Cisco IOS verification
