# Day 36 — Network Discovery: CDP and LLDP

## Overview

Today's lab was about **seeing what's actually connected**. Before you configure anything, you need to know what's there. That's where **CDP** (Cisco Discovery Protocol) and **LLDP** (Link Layer Discovery Protocol) come in.

CDP is Cisco-proprietary. LLDP is the open standard (IEEE 802.1AB). Both do the same thing: they advertise device identity, capabilities, and interface details to directly connected neighbors.

The lab had four phases:
1. Use CDP to document the network
2. Disable CDP on PC-facing switch ports
3. Disable CDP globally
4. Enable LLDP globally and on inter-device interfaces only

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP.png">
  </a>
</p>

---


## Lab Scenario

> "Use CDP (and other commands) to identify and label the missing IP addresses and interface IDs of the devices in the network."
> "Disable CDP on the switch interfaces currently connected to PCs."
> "Disable CDP globally on each network device."
> "Enable LLDP globally on each network device, and enable Tx/Rx on the interfaces connected to other network devices."

This is a **documentation-first, then lockdown** workflow. CDP reveals the hidden topology. Then you shut it down and switch to LLDP.

---

## Discovered Topology (from CDP)

| Device | Type | Interfaces | Neighbors |
|--------|------|-----------|-----------|
| R1 | Router | G0/0, G0/1, G0/2 | R2 (G0/1), R3 (G0/0), SW1 (G0/2) |
| R2 | Router | G0/0, G0/2 | R1 (G0/0), R3 (S0/0/0), SW2 (G0/2) |
| R3 | Router | G0/0, G0/1, G0/2 | R1 (G0/1), R2 (G0/0), SW3 (G0/0) |
| SW1 | Switch | G0/1, G0/2 | R1 (G0/2), PC1 (Fa0/1) |
| SW2 | Switch | G0/1, G0/2 | R2 (G0/2), PC2 (Fa0/1) |
| SW3 | Switch | G0/1, G0/2 | R3 (G0/0), PC3 (Fa0/1) |

**CDP neighbor table on R2:**
```cisco
R2#show cdp neighbors
```
```
Device ID   Local Intrf   Hold-time   Capability   Platform   Port ID
R1          Gig0/0        120         R            2911       Gig0/1
```

**CDP neighbor table on R3:**
```cisco
R3#show cdp neighbors
```
```
Device ID   Local Intrf   Hold-time   Capability   Platform   Port ID
R1          Gig0/1        120         R            2911       Gig0/2
R2          Gig0/2        120         R            2911       Gig0/0
```

---

## Phase 1: Document the Network with CDP

```cisco
! View CDP status
show cdp

! View CDP neighbors
show cdp neighbors

! View CDP neighbors with detail (IP, capabilities, platform)
show cdp neighbors detail

! View CDP interface status
show cdp interface
```

**Key CDP output fields:**
| Field | Example | Meaning |
|-------|---------|---------|
| Device ID | R1 | Hostname of neighbor |
| Local Intrf | Gig0/0 | My interface connected to neighbor |
| Hold-time | 120 | Seconds until entry expires |
| Capability | R | R=Router, B=Bridge, T=Telephone, S=Switch, H=Host |
| Platform | 2911 | Device model |
| Port ID | Gig0/1 | Neighbor's interface connected to me |

**CDP runs by default on all Cisco devices.** Every 60 seconds, a multicast frame is sent to `01:00:0C:CC:CC:CC`. Neighbors receive it and build a table.

**CDP timers:**
- Advertisement interval: 60 seconds
- Hold-time: 180 seconds (default)
- If no CDP packet received within hold-time, entry is removed

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-1.1.png">
  </a>
</p>

---

## Phase 2: Disable CDP on Switch Interfaces Connected to PCs

**Why?** CDP reveals device information. You don't want a compromised PC on a switch port learning about your router topology via CDP. CDP on access ports is a security risk.

```cisco
! SW1 — disable CDP on Fa0/1 (PC1)
SW1(config)#interface range fastethernet 0/1
SW1(config-if-range)#no cdp enable

! SW2 — disable CDP on Fa0/1 (PC2)
SW2(config)#interface range fastethernet 0/1
SW2(config-if-range)#no cdp enable

! SW3 — disable CDP on Fa0/1 (PC3)
SW3(config)#interface range fastethernet 0/1
SW3(config-if-range)#no cdp enable
```

**Verification:**
```cisco
SW1#show cdp interface
```
```
GigabitEthernet0/2 is up, line protocol is up
  Sending CDP packets every 60 seconds
  Hold-time is 180 seconds
FastEthernet0/1 is up, line protocol is up
  CDP is disabled
```

**CDP is enabled by default on all interfaces.** `no cdp enable` turns it off on a specific interface. CDP remains active on uplink/inter-device interfaces.


<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-2.1.png">
      <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-2.2.png">
      <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-2.3.png">
  </a>
</p>

---

## Phase 3: Disable CDP Globally

```cisco
! R1
R1(config)#no cdp run

! R2
R2(config)#no cdp run

! R3
R3(config)#no cdp run

! SW1
SW1(config)#no cdp run

! SW2
SW2(config)#no cdp run

! SW3
SW3(config)#no cdp run
```

**Verification:**
```cisco
R1#show cdp
% CDP is not enabled

R1#show cdp neighbors
% CDP is not enabled
```

**CDP vs LLDP decision:**
- CDP = Cisco-only, easier syntax, more detail
- LLDP = open standard (IEEE), interoperable with non-Cisco gear

If you're in a mixed-vendor environment, LLDP is the only option. If you're all-Cisco, CDP has richer information (VLAN, native VLAN, power info, etc.).

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-3.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-3.2.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-3.3.png">
  </a>
</p>

---

## Phase 4: Enable LLDP Globally and on Inter-Device Interfaces

```cisco
! Enable LLDP globally on all devices
R1(config)#lldp run
R2(config)#lldp run
R3(config)#lldp run
SW1(config)#lldp run
SW2(config)#lldp run
SW3(config)#lldp run
```

**Enable Tx/Rx on interfaces connected to OTHER network devices (not PCs):**

```cisco
! R1
R1(config)#interface range g0/0-2
R1(config-if-range)#lldp transmit
R1(config-if-range)#lldp receive

! R2
R2(config)#interface range g0/0-2
R2(config-if-range)#lldp transmit
R2(config-if-range)#lldp receive

! R3
R3(config)#interface range g0/0-2
R3(config-if-range)#lldp transmit
R3(config-if-range)#lldp receive

! SW1 — uplink only (G0/2 to R1), NOT Fa0/1 (PC1)
SW1(config)#interface g0/2
SW1(config-if)#lldp transmit
SW1(config-if)#lldp receive

! SW2 — uplink only (G0/2 to R2), NOT Fa0/1 (PC2)
SW2(config)#interface g0/2
SW2(config-if)#lldp transmit
SW2(config-if)#lldp receive

! SW3 — uplink only (G0/1 to R3), NOT Fa0/1 (PC3)
SW3(config)#interface g0/1
SW3(config-if)#lldp transmit
SW3(config-if)#lldp receive
```

**Why range on routers but single interface on switches?** Routers have point-to-point serial and Gig links to other routers — every interface faces a network device. Switches have one uplink to a router and the rest are access ports to PCs. Only the uplink gets LLDP.

**Verification on R3:**
```cisco
R3#show lldp neighbors
```
```
Capability codes:
(R) Router, (B) Bridge, (T) Telephone, (P) Repeater,
(S) Station, (O) Other, (C) DOCSIS Cable Device, (E) WLAN

Device ID   Local Intrf   Hold-time   Capability   Port ID
R1          Gig0/1        120         R            Gig0/2
R2          Gig0/2        120         R            Gig0/0
Total entries displayed: 2
```

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-4.1.png">
     <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-4.2.png">
     <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP-4.3.png">
  </a>
</p>

**Verification on R2:**
```cisco
R2#show lldp neighbors
```
```
Device ID   Local Intrf   Hold-time   Capability   Port ID
R1          Gig0/0        120         R            Gig0/1
Total entries displayed: 1
```

**Verification on R1:**
```cisco
R1#show lldp
```
```
Global LLDP Information:
  Status: ACTIVE
  LLDP advertisements are sent every 30 seconds
  LLDP hold time advertised is 120 seconds
  LLDP interface reinitialisation delay is 2 seconds
```

**Verification on SW2 (interface-level LLDP check):**
```cisco
SW2#show run | s 0/1
```
```
interface FastEthernet0/1
 no lldp receive
 no lldp transmit
 no cdp enable
```

This confirms LLDP Tx/Rx are still **disabled** on the PC-facing interface — exactly as required.

---

## CDP vs LLDP Comparison

| Feature | CDP | LLDP |
|---------|-----|------|
| Standard | Cisco proprietary | IEEE 802.1AB |
| Multicast MAC | 01:00:0C:CC:CC:CC | 01:80:C2:00:00:0E |
| Advert interval | 60 seconds | 30 seconds (default) |
| Hold-time | 180 seconds | 120 seconds |
| Commands | `show cdp neighbors` | `show lldp neighbors` |
| Enable global | `cdp run` (default) | `lldp run` |
| Enable interface | `cdp enable` (default) | `lldp transmit` / `lldp receive` |
| Extra info | VLAN, native VLAN, power, duplex | Basic device info only |
| Multi-vendor? | No | Yes |
| Discovery scope | Directly connected | Directly connected |

**Key difference:** CDP is on by default on every interface. LLDP is off by default on every interface. With CDP, you disable it per-interface or globally. With LLDP, you have to explicitly enable it everywhere.

**LLDP Tx/Rx syntax:**
```cisco
interface g0/1
 lldp transmit    ! Send LLDP advertisements out this interface
 lldp receive     ! Accept LLDP advertisements on this interface
```

Both must be enabled for bidirectional discovery. If only transmit is on, you can see neighbors but they can't see you. If only receive is on, you can see neighbors but your advertisements aren't sent.

---

## Interface Range Configuration

```cisco
! Configure multiple interfaces at once
R1(config)#interface range g0/0-2
R1(config-if-range)#lldp transmit
R1(config-if-range)#lldp receive
```

**Syntax:**
- `interface range g0/0-2` — Gig0/0, Gig0/1, Gig0/2
- `interface range fastethernet 0/1-24` — All FastEthernet ports
- `interface range gigabitethernet 0/1-2` — G0/1 and G0/2 only

**Note:** Range syntax only works on contiguous interfaces. For non-contiguous interfaces, use multiple range commands or configure individually.

---

## Commands Practiced

```cisco
! CDP discovery
show cdp
show cdp neighbors
show cdp neighbors detail
show cdp interface
show cdp entry *

! CDP disable per-interface
interface g0/1
 no cdp enable

! CDP disable globally
no cdp run

! LLDP enable globally
lldp run

! LLDP enable per-interface
interface g0/0
 lldp transmit
 lldp receive

! LLDP verification
show lldp
show lldp neighbors
show lldp neighbors detail
show lldp interface
```

---

## Security Implications

| Protocol | Security Risk | Mitigation |
|----------|---------------|------------|
| CDP | Reveals hostname, IP, model, IOS version, VLAN info to any connected device | Disable on access ports + globally if not needed |
| LLDP | Reveals device identity, capabilities, port info to any connected device | Enable only on inter-device links |
| Both | Reconnaissance vector for attackers | Don't run either on ports facing untrusted devices |

**CDP on PC-facing ports is dangerous.** A compromised host can use Wireshark to capture CDP frames and learn:
- Router hostnames and IPs
- Interface names and VLANs
- Device models (IOS version fingerprinting)
- Network topology

**Best practice:**
1. CDP for initial documentation (turn it on, document, turn it off)
2. LLDP for ongoing neighbor discovery (less info leaked, open standard)
3. LLDP only on inter-device interfaces, never on access ports
4. `no cdp enable` on all access ports as a default switch config template

---

## What I Learned

**CDP is your network's autobiography.** Before configuring anything, CDP tells you exactly what's connected to what. The screenshots showed R3 with two LLDP neighbors (R1 on G0/1, R2 on G0/2) and R2 with one neighbor (R1 on G0/0). That's the complete topology in two commands.

**LLDP is CDP with less information leakage.** CDP reveals VLANs, native VLAN, power info. LLDP only reveals device ID, capabilities, and port ID. For security-conscious environments, LLDP is the better default.

**The default states are opposite:**
- CDP: ON by default everywhere. You must disable it.
- LLDP: OFF by default everywhere. You must enable it.

This means LLDP is naturally more secure out of the box — it doesn't advertise until you tell it to.

**Interface-level CDP control is granular.** `no cdp enable` on a switch port stops CDP advertisements to that specific port while keeping CDP active on uplinks. This is exactly what the lab required: CDP documentation first, then lockdown on PC-facing ports.

**CDP and LLDP can coexist temporarily.** During a network audit, you can have both running. Once documentation is complete, disable CDP and keep LLDP for ongoing monitoring.

**`show cdp neighbors detail`** is the most valuable command. It shows IP addresses, native VLAN, duplex, and software version. Use it during initial discovery, then disable CDP.

---

## Lab Status

✅ Day 36 Complete

### Topics Covered

* CDP: discovery, neighbor table, detailed device info
* CDP global disable: `no cdp run`
* CDP per-interface disable: `no cdp enable` on switch PC-facing ports
* LLDP: global enable, interface Tx/Rx control
* LLDP neighbor verification on multi-router topology
* CDP vs LLDP: Cisco proprietary vs IEEE standard
* Security implications of discovery protocols
* Interface range configuration for bulk LLDP enable
* `show lldp`, `show lldp neighbors`, `show lldp interface`
* `show cdp neighbors detail` for comprehensive documentation

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
