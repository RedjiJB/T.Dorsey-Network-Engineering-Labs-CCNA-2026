# Day 40 Lab Manual — SNMP Fundamentals, MIB Queries, and Remote Device Management

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure SNMP read-only and read/write communities on a router, then use an SNMP manager to Get and Set MIB objects remotely |
| CCNA 200-301 Domains | 4.0 IP Services (SNMP versions/operation), 5.0 Security Fundamentals (community strings vs SNMPv3, least privilege) |
| Prerequisites | Basic IOS config mode navigation, understanding of client/server roles, IPv4 addressing |
| Estimated Time | 45–60 minutes |
| Difficulty | Beginner–Intermediate |

## 1. Lab Overview + Learning Objectives

SNMP is how most enterprise monitoring systems (SolarWinds, PRTG, LibreNMS, Zabbix, etc.) actually pull data from routers and switches at scale — nobody SSHes into 400 devices by hand to check interface counters. This lab configures a single router as an SNMP agent, uses a management workstation to Get information out of it via MIB/OID queries, and performs a Set operation to change a device value remotely.

By the end of this lab you will be able to:

1. Configure SNMP read-only and read/write community strings and explain the difference.
2. Explain the manager/agent/MIB/OID relationship from memory.
3. Translate common OIDs (`sysName`, `sysUpTime`, `ifNumber`, `ifDescr`) to what they represent.
4. Perform an SNMP Get and interpret the returned value and type.
5. Perform an SNMP Set and understand why it requires read/write access.
6. Explain why SNMPv1/v2c community strings are considered weak security and what SNMPv3 adds.

## 2. Business Context

A real network operations center does not log into every switch every morning to check CPU, memory, and interface errors. Instead, a monitoring platform polls hundreds or thousands of devices via SNMP every few minutes, graphs the results, and pages someone when a threshold is crossed (e.g., interface utilization over 90%, or a link going down and generating an SNMP trap). Community strings are the SNMPv1/v2c equivalent of a password — a company that ships default or shared community strings across its whole fleet is one leaked config file away from unauthorized read or, worse, write access to every managed device.

## 3. Topology Reference

- One Cisco 2911 router, `R1` — the SNMP **agent**
- One Cisco 2960 switch (Layer 2 only, provides LAN connectivity)
- One management workstation, `PC1` — the SNMP **manager**
- LAN: `192.168.1.0/24`
- R1 G0/0: `192.168.1.254`
- PC1: `192.168.1.1`

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-40-Lab-SNMP.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

A `/24` is used for a two-device management LAN mostly because it's the default lab convention, not because 254 hosts are needed — in a real deployment, a dedicated out-of-band management VLAN is often sized much smaller (e.g., a `/27` or `/28`) since it only ever hosts infrastructure and monitoring servers, never end-user devices. R1 is deliberately given the top of the range (`.254`) — a common convention that keeps management-plane router addresses visually distinct from the DHCP-served client range at the bottom.

### 4.2 Manual Calculation Walkthrough

```
192.168.1.0/24 → mask 255.255.255.0 → 2^8 - 2 = 254 usable hosts
Network:    192.168.1.0
Manager:    192.168.1.1     (PC1)
Agent:      192.168.1.254   (R1 G0/0)
Broadcast:  192.168.1.255
```
Only 2 of the 254 usable addresses are in use — intentional headroom for adding more managed devices or a second monitoring station later without renumbering.

### 4.3 Address Table

| Device | Interface | Address | Role |
|---|---|---|---|
| R1 | G0/0 | 192.168.1.254/24 | SNMP agent |
| PC1 | Fa0 | 192.168.1.1/24 | SNMP manager (MIB browser) |
| SW1 | — | N/A | L2 connectivity only |

## 5. Pre-Configuration Checklist

- [ ] R1 and PC1 can ping each other before layering SNMP on top
- [ ] Decide on distinct RO and RW community strings (never reuse the same string for both)
- [ ] Confirm your MIB browser/manager tool is pointed at R1's correct IP (`192.168.1.254`)
- [ ] Know the OIDs you intend to query before starting, so you can tell a "no data" response apart from a "wrong OID" mistake

## 6. Configuration Tasks

### 6.1 Configure SNMP communities

```
R1> enable
R1# configure terminal
R1(config)# snmp-server community Cisco1 RO
R1(config)# snmp-server community Cisco2 RW
```
Mode: global config. `snmp-server community <string> RO` enables the SNMP agent process and grants read-only access to anyone presenting that exact string. `RW` grants read AND write. Why it matters: this single line is effectively a password gate for remote device visibility (RO) or remote device control (RW) — treat the RW string with the same care as an enable secret. Memory aid: "RO = Read Only = look but don't touch; RW = Read Write = look AND touch."

Verify:
```
R1(config)# do show running-config | section snmp
```
Expected:
```
snmp-server community Cisco1 RO
snmp-server community Cisco2 RW
```

### 6.2 SNMP Get — retrieve `sysName`

From the manager (MIB browser or `snmpget` on Linux):
```
snmpget -v2c -c Cisco1 192.168.1.254 1.3.6.1.2.1.1.5.0
```
OID `1.3.6.1.2.1.1.5.0` = `sysName.0`, the device's configured hostname. Returns `R1`. This is a **Get** — read-only community is sufficient.

### 6.3 SNMP Get — `sysUpTime`

OID `1.3.6.1.2.1.1.3.0` = `sysUpTime.0`. Data type `TimeTicks` (hundredths of a second since last reinit). Example return: `10 hours, 28 minutes, 13 seconds`. This tells an operator how long ago the device last rebooted — critical for correlating an outage report against a possible crash/reload.

### 6.4 SNMP Get — interface inventory

`1.3.6.1.2.1.2.1.0` = `ifNumber.0` → returns `4` (total interfaces in the interface table, including `Vlan1`). `1.3.6.1.2.1.2.2.1.2` = `ifDescr` (a table, walked rather than single-Get) → returns each interface's name: `Vlan1`, `GigabitEthernet0/0`, `GigabitEthernet0/1`, `GigabitEthernet0/2`. Memory aid: "Number tells you *how many*, Descr tells you *which ones*."

### 6.5 SNMP Set — change the hostname remotely

```
Community: Cisco2   (must be RW — a Set against an RO community is rejected)
OID:       1.3.6.1.2.1.1.5.0   (sysName.0)
Operation: Set
Type:      OctetString
Value:     Router1
```
Equivalent `snmpset`:
```
snmpset -v2c -c Cisco2 192.168.1.254 1.3.6.1.2.1.1.5.0 s "Router1"
```
This is the exact same OID used for the earlier Get, which is the point: Get and Set often target identical objects — what differs is the community's write permission and the operation type. After this, R1's CLI prompt itself changes from `R1>` to `Router1>`, because `sysName` maps directly onto the device's configured hostname.

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show running-config \| section snmp` | R1 | Confirm both community strings and access levels |
| `snmpget -v2c -c Cisco1 <ip> 1.3.6.1.2.1.1.5.0` | Manager | Confirm hostname is retrievable read-only |
| `snmpset -v2c -c Cisco2 <ip> 1.3.6.1.2.1.1.5.0 s "Router1"` | Manager | Confirm write access changes the device |
| `show running-config \| include hostname` | R1 | Confirm the CLI-side hostname actually changed |

### Expected Output Gallery

```
R1(config)# do show running-config | section snmp
snmp-server community Cisco1 RO
snmp-server community Cisco2 RW
```

```
$ snmpget -v2c -c Cisco1 192.168.1.254 1.3.6.1.2.1.1.5.0
SNMPv2-MIB::sysName.0 = STRING: R1

$ snmpget -v2c -c Cisco1 192.168.1.254 1.3.6.1.2.1.1.3.0
DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (3769300) 10:28:13.00

$ snmpwalk -v2c -c Cisco1 192.168.1.254 1.3.6.1.2.1.2.2.1.2
IF-MIB::ifDescr.1 = STRING: Vlan1
IF-MIB::ifDescr.2 = STRING: GigabitEthernet0/0
IF-MIB::ifDescr.3 = STRING: GigabitEthernet0/1
IF-MIB::ifDescr.4 = STRING: GigabitEthernet0/2
```

```
Router1# show running-config | include hostname
hostname Router1
```

## 8. Common Mistakes (80/20)

1. **Using the RO community for a Set operation** — it will be silently rejected (or return an authorization error); this is by design, not a bug.
2. **Typo'd OIDs** — a single wrong digit returns "no such object," which looks identical to "SNMP isn't working," wasting troubleshooting time.
3. **No IP reachability check first** — SNMP timeouts and IP connectivity failures look the same to a beginner; always ping before blaming SNMP.
4. **Reusing the same string for RO and RW** — defeats the entire purpose of having two access levels.
5. **Assuming SNMPv2c community strings are "secure enough"** — they're sent in cleartext; anyone who can sniff the LAN segment can read or guess them.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Basic IP reachability | `ping 192.168.1.254` from PC1 | Fix Layer 1-3 connectivity before touching SNMP |
| 2 | Is SNMP configured at all on R1? | `show running-config \| section snmp` | Add `snmp-server community` lines |
| 3 | Is the manager using the exact right community string? | Re-check manager's configured community field | Correct typo, case sensitivity matters |
| 4 | Is the operation trying to Set with an RO community? | Compare operation type vs. community's access level | Use the RW community for Set |
| 5 | Is the OID correct and supported on this platform? | Cross-reference OID against a MIB reference / try `ifNumber` first as a sanity check | Correct the OID or accept the object isn't supported in this environment (Packet Tracer's SNMP support is limited) |

## 10. Design Analysis

SNMPv2c with community strings is simple to stand up (as shown here) but weak: cleartext strings, no per-user accountability, no encryption. The alternative, SNMPv3, adds authentication (username + auth password) and optional encryption (priv password) at the cost of more setup complexity. Most production shops run SNMPv2c read-only, over a restricted, ACL'd management VLAN, purely for polling — and reserve any write-capable access for a tightly controlled configuration management tool rather than ad hoc SNMP Sets, precisely because SNMP Set has no audit trail comparable to a CLI session logged through TACACS+.

## 11. Real-World Parallel

Every "network is down, dashboard didn't alert" postmortem eventually checks whether SNMP polling was failing silently — a wrong community string after a device replacement, or a firewall rule blocking UDP 161, is one of the most common causes of monitoring blind spots in real NOCs.

## 12. Stretch Goal

Configure `snmp-server contact` and `snmp-server location`, then retrieve both via Get, and configure an SNMP trap destination (`snmp-server host <manager-ip> version 2c Cisco1`) so R1 notifies the manager of a link-down event instead of only being polled.

## 13. Self-Assessment

- [ ] I can explain the manager/agent relationship using this lab's exact devices
- [ ] I can state, without looking it up, which OID maps to `sysName` and which to `sysUpTime`
- [ ] I can explain why a Set against an RO community fails
- [ ] I can name at least two weaknesses of SNMPv2c that SNMPv3 addresses
- [ ] I performed both a Get and a Set myself and confirmed the hostname change on R1's own CLI

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** SNMP manager/agent architecture, MIB hierarchy, OIDs, community-string access control, Get vs Set vs GetNext vs Trap vs Inform, SNMPv2c weaknesses vs SNMPv3.

**What I Learned:** SNMP Get and Set frequently target the exact same OID — the security boundary is entirely in which community string is presented and what access level it carries, not in the object itself. Read-only communities should be the default; write access should be the exception, tightly scoped and audited.

**Skills Practiced:** SNMP community configuration, MIB navigation, OID identification, SNMP Get/Set operations, interface inventory collection via SNMP, system uptime monitoring, remote configuration changes, Cisco IOS verification.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-40/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using a VyOS router (SNMP agent), Open vSwitch switch, and an Alpine Linux management host (SNMP manager, using `net-snmp` tools).
