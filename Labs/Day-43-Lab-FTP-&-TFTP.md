# Day 43 — FTP & TFTP: Cisco IOS File Transfer & Upgrade

## 📖 Overview

Day 43 of my CCNA lab journey focused on using **TFTP (Trivial File Transfer Protocol)** and **FTP (File Transfer Protocol)** to transfer Cisco IOS images between a server and Cisco routers.

In this lab, R1 and R2 were connected through the `192.168.12.0/30` network, while R1 provided connectivity to the `10.0.0.0/24` network containing SRV1.

After configuring the appropriate IP addresses and routing, I used **TFTP on R1** and **FTP on R2** to retrieve a newer Cisco IOS image from SRV1. The routers were then configured to boot using the new IOS image, and the old IOS files were removed from flash.

This lab combined several important CCNA concepts:

- IPv4 addressing
- Router interface configuration
- Routing
- Connectivity verification
- Cisco IOS file management
- Flash memory
- TFTP
- FTP
- IOS image transfers
- IOS upgrades
- Boot system configuration
- Network troubleshooting

---

# 🖥️ Network Topology

The topology contains SRV1 on the `10.0.0.0/24` LAN connected to R1. R1 and R2 communicate across the `192.168.12.0/30` point-to-point network.

```text
                 10.0.0.0/24                  192.168.12.0/30

SRV1 -------- SW1 -------- R1 ---------------------- R2
 .1                       G0/1                     G0/0
                           .254      G0/0   G0/0      .2
                                      .1
```

### Addressing

| Device | Interface | Address |
|---|---|---|
| SRV1 | NIC | `10.0.0.1/24` |
| R1 | G0/1 | `10.0.0.254/24` |
| R1 | G0/0 | `192.168.12.1/30` |
| R2 | G0/0 | `192.168.12.2/30` |

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP.png" alt="Day 43 FTP TFTP Lab Topology" width="1000">
</p>

---

# 🎯 Lab Objectives

The goal of this lab was to configure network connectivity and practice transferring and managing Cisco IOS images.

### Requirements

1. Configure the appropriate IP addresses on each device.
2. Configure routing on the routers to allow full connectivity.
3. Use TFTP on R1 to retrieve the IOS image from SRV1.
4. Upgrade R1's IOS and delete the old IOS image from flash.
5. Use FTP on R2 to retrieve the IOS image from SRV1.
6. Upgrade R2's IOS and delete the old IOS image from flash.

### IOS Image

```text
c2900-universalk9-mz.SPA.155-3.M4a.bin
```

### FTP Credentials

```text
Username: jeremy
Password: ccna
```

---

# Phase 1 — Configure Router IP Addressing

The first step was configuring the router interfaces with the appropriate IPv4 addresses.

R1's G0/0 interface connects to R2 across the `/30` point-to-point network.

```cisco
R1>enable
R1#configure terminal

R1(config)#interface g0/0
R1(config-if)#ip address 192.168.12.1 255.255.255.252
R1(config-if)#no shutdown
```

R1's G0/1 interface connects toward the server LAN.

```cisco
R1(config)#interface g0/1
R1(config-if)#ip address 10.0.0.254 255.255.255.0
R1(config-if)#no shutdown
```

The interfaces can be verified with:

```cisco
show ip interface brief
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP-1.1.png" alt="R1 Interface Configuration" width="1000">
</p>

---

# Phase 2 — Configure R2

R2's G0/0 interface was configured on the other side of the point-to-point link.

```cisco
R2>enable
R2#configure terminal

R2(config)#interface g0/0
R2(config-if)#ip address 192.168.12.2 255.255.255.252
R2(config-if)#no shutdown
```

Verification:

```cisco
show ip interface brief
```

The expected interface address is:

```text
GigabitEthernet0/0    192.168.12.2    up    up
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP-1.2.png" alt="R2 Interface Configuration" width="1000">
</p>

---

# 🧠 Why Use a /30 Network Between Routers?

The R1-to-R2 connection uses:

```text
192.168.12.0/30
```

A `/30` subnet provides four total addresses:

```text
192.168.12.0     Network
192.168.12.1     R1
192.168.12.2     R2
192.168.12.3     Broadcast
```

Only two usable host addresses are available.

That makes `/30` networks useful for traditional point-to-point IPv4 links because only two devices need addresses.

---

# Phase 3 — Configure Routing

R2 must know how to reach the server network:

```text
10.0.0.0/24
```

The next hop toward that network is R1:

```text
192.168.12.1
```

A route was configured so R2 could reach SRV1 through R1.

```cisco
R2(config)#ip route 10.0.0.0 255.255.255.0 192.168.12.1
```

The routing table can be verified with:

```cisco
show ip route
```

The route should point toward R1 through G0/0.

Connectivity was then tested:

```cisco
ping 10.0.0.1
```

A successful ping confirmed that R2 could communicate with SRV1.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP-2.1.png" alt="Routing and Connectivity Verification" width="1000">
</p>

---

# 🧠 Why Routing Must Work Before File Transfer

TFTP and FTP operate using IP connectivity.

Before a router can retrieve a file from SRV1, it must be able to reach:

```text
10.0.0.1
```

This means the underlying network must already have:

```text
Correct IP addressing
        +
Operational interfaces
        +
Correct routing
        +
End-to-end connectivity
```

If a router cannot successfully ping the server, an FTP or TFTP transfer will normally fail as well.

This makes basic connectivity testing an important troubleshooting step before attempting a file transfer.

---

# Phase 4 — Transfer the IOS Image to R1 Using TFTP

R1 used **TFTP** to retrieve the new IOS image from SRV1.

The command was:

```cisco
R1#copy tftp: flash:
```

R1 then requested the TFTP server address:

```text
Address or name of remote host []? 10.0.0.1
```

The source filename was:

```text
c2900-universalk9-mz.SPA.155-3.M4a.bin
```

The router then copied the IOS image into flash memory.

Example:

```text
Accessing tftp://10.0.0.1/c2900-universalk9-mz.SPA.155-3.M4a.bin...
Loading c2900-universalk9-mz.SPA.155-3.M4a.bin from 10.0.0.1:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[OK]
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP-3.1.png" alt="R1 TFTP IOS Transfer" width="1000">
</p>

---

# 🧠 What Is TFTP?

TFTP stands for:

```text
Trivial File Transfer Protocol
```

TFTP provides a very simple method for transferring files across an IP network.

Important characteristics include:

```text
Transport: UDP
Port: 69
Authentication: None
Encryption: None
```

TFTP is commonly encountered in networking environments for transferring:

- IOS images
- Configuration files
- Device backups

Because it does not provide authentication or encryption, it should only be used in appropriate trusted environments.

---

# Phase 5 — Verify the IOS Image in Flash

After transferring the IOS image, flash memory was checked.

```cisco
show flash:
```

or:

```cisco
dir flash:
```

The new image should appear:

```text
c2900-universalk9-mz.SPA.155-3.M4a.bin
```

This verification is important before modifying the router's boot configuration.

---

# 🧠 Cisco Router Flash Memory

Cisco routers commonly store their IOS image in **flash memory**.

Conceptually:

```text
Router powers on
      ↓
Bootstrap runs
      ↓
Router examines boot instructions
      ↓
IOS image loaded from flash
      ↓
IOS starts
```

Therefore, transferring a new IOS image into flash is only one part of the upgrade process.

The router must also be instructed to boot using that image.

---

# Phase 6 — Upgrade R1's IOS

After confirming the new image was present in flash, R1 could be configured to boot from it.

```cisco
R1(config)#boot system flash c2900-universalk9-mz.SPA.155-3.M4a.bin
```

The configuration should then be saved.

```cisco
R1#copy running-config startup-config
```

or:

```cisco
R1#write memory
```

After reloading the router:

```cisco
reload
```

the IOS version can be verified with:

```cisco
show version
```

---

# Phase 7 — Remove the Old IOS Image

Once the router successfully boots using the new IOS image, the old IOS image can be removed from flash.

First verify the files:

```cisco
show flash:
```

Then delete the old image:

```cisco
delete flash:<old-ios-filename>
```

Deleting the old image frees flash storage.

However, the old image should not be removed until the new image has been successfully transferred and verified.

---

# ⚠️ Safe IOS Upgrade Workflow

A safer upgrade process follows this order:

```text
1. Verify network connectivity
        ↓
2. Check available flash storage
        ↓
3. Transfer new IOS image
        ↓
4. Verify image exists
        ↓
5. Configure boot system
        ↓
6. Save configuration
        ↓
7. Reload router
        ↓
8. Verify new IOS
        ↓
9. Delete old IOS
```

Deleting the old image too early could leave the router without a usable IOS image if the new image is corrupted or incorrectly configured.

---

# Phase 8 — Configure FTP on R2

R2 used **FTP** instead of TFTP.

The lab provided the following credentials:

```text
Username: jeremy
Password: ccna
```

The FTP credentials were configured on R2:

```cisco
R2(config)#ip ftp username jeremy
R2(config)#ip ftp password ccna
```

These credentials allow R2 to authenticate with the FTP service running on SRV1.

---

# Phase 9 — Transfer the IOS Image to R2 Using FTP

The FTP transfer was initiated with:

```cisco
R2#copy ftp: flash:
```

The server address was:

```text
10.0.0.1
```

The IOS filename was:

```text
c2900-universalk9-mz.SPA.155-3.M4a.bin
```

Because FTP uses TCP and Packet Tracer simulates the transfer process, the transfer may take longer than the TFTP operation.

---

# 🧠 FTP vs TFTP

Although both protocols can transfer files, they operate differently.

| Feature | TFTP | FTP |
|---|---|---|
| Transport | UDP | TCP |
| Ports | UDP 69 | TCP 20/21 |
| Authentication | ❌ No | ✅ Yes |
| Reliability | Basic | TCP reliability |
| Encryption | ❌ No | ❌ No |
| Complexity | Very simple | More complex |
| Lab Router | R1 | R2 |

One major difference demonstrated in this lab was authentication.

R1's TFTP transfer did not require credentials.

R2's FTP transfer required:

```cisco
ip ftp username jeremy
ip ftp password ccna
```

---

# Phase 10 — Verify R2 Flash

After the FTP transfer completed, R2's flash storage was checked.

```cisco
show flash:
```

The new IOS image appeared in the system flash directory:

```text
c2900-universalk9-mz.SPA.155-3.M4a.bin
```

This confirmed that the FTP transfer completed successfully.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP-4.1.png" alt="R2 Flash IOS Verification" width="1000">
</p>

---

# Phase 11 — Upgrade R2's IOS

R2 can now be configured to boot using the newly transferred IOS image.

```cisco
R2(config)#boot system flash c2900-universalk9-mz.SPA.155-3.M4a.bin
```

Save the configuration:

```cisco
R2#copy running-config startup-config
```

Reload:

```cisco
R2#reload
```

After the router boots, verify the IOS:

```cisco
show version
```

Finally, verify flash:

```cisco
show flash:
```

The old IOS image can then be removed:

```cisco
delete flash:<old-ios-filename>
```

---

# 🔎 Verification

Several commands are useful when performing Cisco IOS file management.

## Verify Interfaces

```cisco
show ip interface brief
```

Confirms that the required interfaces are correctly addressed and operational.

---

## Verify Routing

```cisco
show ip route
```

Confirms that remote networks are reachable through the correct next hop.

---

## Verify Connectivity

```cisco
ping 10.0.0.1
```

Confirms connectivity to the file server before attempting a transfer.

---

## Verify Flash

```cisco
show flash:
```

or:

```cisco
dir flash:
```

Confirms that the IOS image exists in flash.

---

## Verify IOS Version

```cisco
show version
```

Confirms which Cisco IOS version the router is currently running.

---

## Verify Boot Configuration

```cisco
show running-config
```

Look for the configured boot system command:

```cisco
boot system flash c2900-universalk9-mz.SPA.155-3.M4a.bin
```

---

# 📋 Major Configuration Commands

The major commands used throughout the lab can be summarized as:

```cisco
enable
configure terminal

interface g0/0
 ip address 192.168.12.1 255.255.255.252
 no shutdown

interface g0/1
 ip address 10.0.0.254 255.255.255.0
 no shutdown

show ip interface brief

show ip route

ping 10.0.0.1

copy tftp: flash:

show flash:

boot system flash c2900-universalk9-mz.SPA.155-3.M4a.bin

copy running-config startup-config

show version

ip ftp username jeremy
ip ftp password ccna

copy ftp: flash:

delete flash:<old-ios-filename>
```

---

# 🧠 Troubleshooting Checklist

If a TFTP or FTP transfer fails, check:

1. Are the router interfaces up/up?
2. Are the IP addresses correct?
3. Is SRV1 using the correct IP address?
4. Can the router ping SRV1?
5. Does the routing table contain the required route?
6. Is the correct server address being used?
7. Is the IOS filename entered exactly?
8. Is TFTP or FTP enabled on the server?
9. For FTP, are the username and password correct?
10. Is there enough space available in flash?
11. Does the new IOS image appear in `show flash:`?
12. Is the correct image specified by the boot configuration?

Useful commands:

```cisco
show ip interface brief
show ip route
ping 10.0.0.1
show flash:
dir flash:
show running-config
show version
```

---

# 📚 Skills Practiced

- Cisco IOS CLI
- IPv4 addressing
- Router interface configuration
- `/30` point-to-point networks
- Routing
- Routing table verification
- ICMP connectivity testing
- Cisco flash memory management
- TFTP
- FTP
- File transfer troubleshooting
- FTP authentication
- Cisco IOS image transfers
- IOS upgrades
- Boot system configuration
- IOS version verification
- Network troubleshooting
- Device administration

---

# 🎯 Key Takeaways

The biggest takeaway from Day 43 was that **upgrading a network device requires more than simply downloading a new IOS file**.

The complete process depends on several layers working together:

```text
IP Addressing
      +
Routing
      +
Connectivity
      +
File Transfer
      +
Flash Storage
      +
Boot Configuration
      +
Verification
```

TFTP provides a lightweight way to transfer files using UDP, while FTP provides a TCP-based file transfer mechanism with username and password authentication.

The lab also reinforced the importance of verifying connectivity before troubleshooting application-layer services.

The overall IOS upgrade workflow was:

```text
SRV1
 |
 | TFTP / FTP
 ↓
Router
 |
 ↓
Flash Memory
 |
 ↓
New IOS Image
 |
 ↓
Boot Configuration
 |
 ↓
Reload
 |
 ↓
Verify IOS
 |
 ↓
Remove Old Image
```

Understanding this process is important for real-world network administration because network engineers frequently need to manage device software, backups, configurations, and system images.

---

## ✅ Lab Status

**Day 43 Complete**

### Topics Covered

- TFTP
- FTP
- Cisco IOS images
- IOS file transfers
- Flash memory
- IOS upgrades
- Boot system configuration
- IPv4 addressing
- `/30` networks
- Routing
- Connectivity verification
- FTP authentication
- File management
- IOS verification
- Cisco router administration
- Network troubleshooting
