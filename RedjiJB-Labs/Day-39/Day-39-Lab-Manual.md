# Day 39 Lab Manual — DHCP Server, DHCP Client, and DHCP Relay

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Build a centralized DHCP deployment: one router as the DHCP server for multiple subnets, one router as a DHCP client, and DHCP relay across a Layer 3 boundary |
| CCNA 200-301 Domains | 4.0 IP Services (DHCP operation, relay/`ip helper-address`), 1.0 Network Fundamentals (IPv4 addressing), 5.0 Security Fundamentals (DHCP snooping awareness) |
| Prerequisites | Static routing between R1 and R2, interface addressing basics, subnetting fluency (VLSM) |
| Estimated Time | 75–90 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

This lab builds a small two-site network where a single router (R2) acts as the centralized DHCP server for three different subnets, while R1 is simultaneously a DHCP **client** (on its WAN-facing interface) and a DHCP **relay agent** (for its downstream LAN). This is the exact pattern used in real branch-office deployments where IT doesn't want to manage a DHCP server at every site.

By the end of this lab you will be able to:

1. Configure multiple DHCP pools on a single IOS device, each scoped to a different subnet.
2. Correctly exclude infrastructure addresses from a DHCP pool before creating it.
3. Configure a router interface to obtain its own address via DHCP.
4. Explain why routers do not forward broadcasts by default, and configure `ip helper-address` to work around that.
5. Trace the full DORA (Discover, Offer, Request, Acknowledge) process end to end, including which hop does what.
6. Verify and troubleshoot DHCP leases from both the server side and the client side.

## 2. Business Context

Imagine a company with a small headquarters (R2's site) and a small branch office (R1's site) connected by a WAN link. Buying, licensing, and patching a dedicated DHCP server appliance at every branch is expensive and adds a device that has to be managed remotely. Instead, most enterprises centralize DHCP at headquarters (or in a data center) and configure branch routers to relay client requests back to it. This also centralizes the DHCP lease database, DNS options, and domain settings into one place, which simplifies audits and makes IP address management (IPAM) tooling much easier to run. The tradeoff is that if the WAN link to headquarters goes down, branch clients cannot renew leases — a real operational risk we discuss in Design Analysis.

## 3. Topology Reference

- Two Cisco 2911 routers (R1, R2)
- Two Cisco 2960 switches (SW1 at R1's site, SW2 at R2's site)
- Two client PCs (PC1 behind R1, PC2 behind R2)
- LAN 1: `192.168.1.0/24` (PC1's subnet, behind R1)
- LAN 2: `192.168.2.0/24` (PC2's subnet, behind R2 — also where the DHCP server lives)
- Transit link R1↔R2: `203.0.113.0/30`
- R2 = centralized DHCP server for all three subnets
- R1 = DHCP client on its WAN interface, DHCP relay agent on its LAN interface

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-39-Lab-DHCP.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

- `192.168.1.0/24` and `192.168.2.0/24` are each sized as full /24s (254 usable hosts) even though each LAN only has one PC today — this mirrors real branch LANs, which are almost always provisioned as /24s regardless of current headcount, because renumbering later is far more disruptive than "wasting" address space now.
- The transit link between R1 and R2 uses `203.0.113.0/30`, a 2-host subnet — this is the textbook-correct sizing for a point-to-point link, since a WAN link only ever needs exactly two usable addresses.
- The first 10 addresses in each LAN (`.1`–`.10`) are excluded from the DHCP pool and reserved for infrastructure (gateway, future printers, future access points) — a standard "reserve the bottom of the range" convention.

### 4.2 Manual Calculation Walkthrough

**LAN pools (/24):**
```
192.168.1.0/24 → mask 255.255.255.0 → 2^8 - 2 = 254 usable hosts
Network:    192.168.1.0
First host: 192.168.1.1   (reserved – gateway)
Last host:  192.168.1.254
Broadcast:  192.168.1.255
```
Same math applies identically to `192.168.2.0/24`.

**Transit link (/30):**
```
203.0.113.0/30 → mask 255.255.255.252 → 2^2 - 2 = 2 usable hosts
Network:    203.0.113.0
Host 1:     203.0.113.1  (R2 side, DHCP-excluded, acts as gateway for R1's DHCP-assigned address)
Host 2:     203.0.113.2  (R1 G0/0, assigned dynamically by DHCP)
Broadcast:  203.0.113.3
```

### 4.3 Address Table

| Device | Interface | Address | Assignment |
|---|---|---|---|
| R2 | Loopback/pool source | POOL1, POOL2, POOL3 owner | Static |
| R2 | toward R1 | 203.0.113.1 | Static |
| R1 | G0/0 (WAN) | 203.0.113.2 | **DHCP (client)** |
| R1 | G0/1 (LAN) | 192.168.1.1 | Static + `ip helper-address 192.168.2.1` |
| PC1 | NIC | 192.168.1.11+ | DHCP via relay |
| PC2 | NIC | 192.168.2.11+ | DHCP direct |

## 5. Pre-Configuration Checklist

- [ ] R1↔R2 transit link is up and reachable before layering DHCP on top (`ping` the static side first)
- [ ] Static routing (or a routing protocol) exists between R1's LAN and R2 so DHCP replies have a return path
- [ ] Decide and write down the excluded-address ranges *before* creating pools — pools created first will hand out infrastructure addresses on the next lease request
- [ ] Confirm PC1 and PC2 NICs are set to "Obtain an IP address automatically"
- [ ] Confirm switches (SW1, SW2) are simple Layer 2 with the correct ports in the right VLAN/trunking mode (not part of this lab's scope, but broken switching breaks everything downstream)

## 6. Configuration Tasks

### 6.1 Phase 1 — DHCP pools on R2 (global config mode)

Exclude infrastructure addresses **first** — order matters, because IOS starts leasing from a pool the moment it's created:

```
R2(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.10
R2(config)# ip dhcp excluded-address 192.168.2.1 192.168.2.10
R2(config)# ip dhcp excluded-address 203.0.113.1
```
Mode: global config. What it does: tells the DHCP process never to offer these addresses. Why it matters: without this, the very first client to ask could be handed the gateway's own address, causing an IP conflict. Memory aid: "exclude before you include" — always run exclusions before `ip dhcp pool`.

Create each pool (DHCP config sub-mode):

```
R2(config)# ip dhcp pool POOL1
R2(dhcp-config)# network 192.168.1.0 255.255.255.0
R2(dhcp-config)# default-router 192.168.1.1
R2(dhcp-config)# dns-server 8.8.8.8
R2(dhcp-config)# domain-name jeremysitlab.com
```
`network` defines the scope the pool leases from. `default-router` is the option-3 gateway handed to clients — note this is R1's LAN address, not R2's, because R1 is the actual default gateway for PC1. `dns-server` and `domain-name` are options 6 and 15. Repeat for POOL2 (`192.168.2.0/24`, gateway `192.168.2.1`), and POOL3 for the transit link:

```
R2(config)# ip dhcp pool POOL3
R2(dhcp-config)# network 203.0.113.0 255.255.255.252
```
POOL3 has no `default-router`/`dns-server` because it only serves R1's WAN interface, which just needs an address, not host-style options.

### 6.2 Phase 2 — R1 as a DHCP client

```
R1(config)# interface g0/0
R1(config-if)# ip address dhcp
R1(config-if)# no shutdown
```
Mode: interface config. This tells IOS to run a DHCP client process on G0/0 instead of taking a static address. Memory aid: "a router can be a client too" — DHCP client behavior isn't PC-exclusive; ISPs commonly hand out DHCP addresses to CPE routers this exact way.

Verify:
```
R1# show ip interface brief
```
Expected:
```
Interface              IP-Address      Method  Status  Protocol
GigabitEthernet0/0     203.0.113.2     DHCP    up      up
GigabitEthernet0/1     192.168.1.1     NVRAM   up      up
```

### 6.3 Phase 3 — R1 as a DHCP relay agent

```
R1(config)# interface g0/1
R1(config-if)# ip helper-address 192.168.2.1
```
Mode: interface config, applied on the LAN-facing interface (the one facing the clients, not the server). What it does: converts an incoming DHCP broadcast into a unicast packet aimed at the specified server address, and forwards it out the interface toward that server. Why it matters: IOS routers do not forward broadcast traffic between interfaces by default (this is basic Layer 3 boundary behavior) — without this command, PC1's DHCP Discover simply dies at R1's LAN interface. Memory aid: "helper lives on the LAN side, points at the server."

### 6.4 Phase 4/5 — Force clients to request a lease

On PC1 and PC2 (Windows CLI or equivalent):
```
ipconfig /renew
```
This forces an immediate new DORA exchange instead of waiting for the client to retry on its own timer.

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show ip interface brief` | R1 | Confirm G0/0 shows `DHCP` as its method |
| `show ip dhcp pool` | R2 | Confirm each pool's total/leased address counts |
| `show ip dhcp binding` | R2 | List every active lease, by MAC and IP |
| `show running-config \| section interface` | R1 | Confirm `ip helper-address` is present on G0/1 |
| `ipconfig /all` | PC1, PC2 | Confirm assigned IP, gateway, DNS, domain |

### Expected Output Gallery

```
R2# show ip dhcp binding
IP address       Client-ID/           Lease expiration        Type
                  Hardware address/
                  User name
192.168.1.11      0100.5079.6675.32   Aug 28 2026 06:14 AM    Automatic
192.168.2.11      0100.5079.6675.5a   Aug 28 2026 06:15 AM    Automatic
203.0.113.2       0100.5079.6675.7f   Aug 28 2026 06:10 AM    Automatic

R2# show ip dhcp pool POOL1
Pool POOL1 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/last)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 1
 Excluded addresses             : 10
 Pending event                  : none
```

```
R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     203.0.113.2     YES DHCP   up                    up
GigabitEthernet0/1     192.168.1.1     YES NVRAM  up                    up
```

## 8. Common Mistakes (80/20)

1. **Creating the pool before excluding addresses** — the gateway address gets leased to the first client, causing a duplicate-IP conflict with the router itself.
2. **Putting `ip helper-address` on the wrong interface** — it must go on the interface facing the clients (the one that receives the broadcast), not the WAN/server-facing interface.
3. **`default-router` pointing at the DHCP server's own address instead of the local gateway** — clients need the gateway that's actually on their subnet, which for POOL1 is R1, not R2.
4. **Forgetting `no shutdown` after `ip address dhcp`** — a classic oversight that leaves the interface administratively down regardless of DHCP config.
5. **No return route from R2 back to R1's LAN** — the DHCP OFFER/ACK never makes it back, and the client just times out with no obvious error pointing at DHCP.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Is the transit link up? | `show ip interface brief` on R1/R2 | Fix physical/Layer 2 issue first |
| 2 | Does R1 have a route back to R2's networks (and vice versa)? | `show ip route` | Add static route or fix routing protocol |
| 3 | Is the pool created and not exhausted? | `show ip dhcp pool` on R2 | Recreate pool, widen `network` statement, or check exclusions eating the whole range |
| 4 | Is `ip helper-address` present and correct? | `show running-config \| section interface` on R1 | Add/correct the helper address on the client-facing interface |
| 5 | Are bindings appearing on the server? | `show ip dhcp binding` on R2 | If no binding appears, the Discover never arrived — recheck helper address and routing |
| 6 | Did the client actually request a new lease? | `ipconfig /all` then `ipconfig /renew` on PC | Force renewal; check NIC is set to DHCP, not static |

## 10. Design Analysis

Centralizing DHCP on R2 minimizes the number of devices IT has to patch and manage, and keeps the lease database in one place for auditing. The alternative — a local DHCP pool on R1 itself — would remove the WAN dependency (branch clients could still get addresses even if the WAN link died) but would decentralize configuration, meaning DNS/domain changes have to be pushed to every branch router individually instead of one central server. Most enterprises accept the WAN-down risk because outages are rare and short, while configuration drift across dozens of branch DHCP servers is a much more common, ongoing problem.

## 11. Real-World Parallel

You'd see this design in any retail chain, bank branch network, or multi-site business where headquarters IT wants one source of truth for IP configuration policy. It's also exactly how a home ISP router works from your ISP's perspective — your router's WAN interface is a DHCP client of the ISP's DHCP server, no different from R1's G0/0 here.

## 12. Stretch Goal

Add a fourth subnet behind a new router (R3) connected to R2, and extend the relay chain so R3 also relays DHCP requests back to R2 — practicing helper-address configuration on a second hop, and confirming `show ip dhcp binding` still correctly attributes leases per subnet.

## 13. Self-Assessment

- [ ] I can explain, without notes, why `ip dhcp excluded-address` must be configured before `ip dhcp pool`
- [ ] I can state which interface `ip helper-address` belongs on, and why
- [ ] I can draw the DORA sequence from memory including which device does each step
- [ ] I can explain the difference between DHCP server, client, and relay roles using this lab's exact devices
- [ ] I verified all three pools and both client leases myself, not just by reading the sample output above

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** DHCP server/client/relay roles, DORA message flow, UDP 67/68, `ip helper-address`, excluded-address ordering, centralized multi-subnet DHCP.

**What I Learned:** A single IOS router can simultaneously be a DHCP server, client, and relay for different interfaces — these roles are per-interface/per-process, not mutually exclusive per device. The `ip helper-address` command is the single most important tool for extending DHCP (and other broadcast-based UDP services) across routed boundaries.

**Skills Practiced:** Cisco IOS DHCP server configuration, DHCP pool creation, address exclusions, dynamic router interface addressing, DHCP relay configuration, DORA analysis, UDP port awareness, multi-subnet deployment, lease verification, DHCP troubleshooting.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-39/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers, Open vSwitch switches, and Alpine Linux end hosts.
