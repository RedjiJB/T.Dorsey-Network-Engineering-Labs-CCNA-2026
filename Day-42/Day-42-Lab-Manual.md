# Day 42 Lab Manual — SSH: Secure Remote Access & Management

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Fully secure a newly installed switch for remote administration: local auth, SSH-only VTY, RSA keys, and ACL-restricted management access |
| CCNA 200-301 Domains | 5.0 Security Fundamentals (secure remote access, ACLs, management-plane security), 4.0 IP Services (SSH), 2.0 Network Access (SVI, default gateway on an L2 switch) |
| Prerequisites | Basic IOS config, static routing between two LANs, standard ACL syntax |
| Estimated Time | 60–75 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

This lab takes a switch from zero configuration to fully hardened remote management in one sequence: hostname, local accounts, SVI/gateway, console hardening, SSH key generation, VTY lockdown to SSH-only, and finally a standard ACL restricting management access to exactly one host. This is the realistic "day one" checklist for any newly racked switch before it's trusted on a production network.

By the end of this lab you will be able to:

1. Explain why a Layer 2 switch needs an SVI and a default gateway for remote management, even though it doesn't route.
2. Configure local username authentication for console and VTY lines.
3. Generate RSA keys and explain why they're a prerequisite for SSH.
4. Lock VTY lines to SSH-only using `transport input ssh`.
5. Correctly distinguish `access-class` from `access-group` and apply a standard ACL to restrict management access to one host.
6. Trace a full connection attempt through every security layer, from source IP filtering to authentication to encryption.

## 2. Business Context

Every newly deployed switch is, by default, a wide-open door: no passwords, no encryption, Telnet-accessible from anywhere on the segment. Before a switch goes into production, it must be hardened — and "hardened" specifically means layering multiple independent controls (who can even reach the management plane, how they authenticate, whether the session is encrypted, and how long an idle session survives) so that no single misconfiguration is catastrophic. This exact checklist — SSH-only, local auth, restrictive ACL, timeout — is what a change-management runbook looks like at any company that takes device security seriously.

## 3. Topology Reference

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

| Device | Interface | Address |
|---|---|---|
| PC1 | NIC | 192.168.1.1/24 |
| R1 | G0/1 | 192.168.1.254/24 |
| R1 | G0/0 | 10.0.0.1/30 |
| R2 | G0/0 | 10.0.0.2/30 |
| R2 | G0/1 | 192.168.2.254/24 |
| SW1 | VLAN 1 | 192.168.1.253/24 |
| SW2 | VLAN 1 | 192.168.2.253/24 |

Laptop1 connects directly to SW2's console for initial (out-of-band) configuration, since SW2 arrives with no management IP at all.

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-42-Lab-SSH.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

Two `/24` LANs connected by a `/30` transit link — the standard pattern (see Day 39/40/41 for the same rationale on the /24 side). The `/30` transit between R1 and R2 (`10.0.0.0/30`) needs only 2 usable addresses for a point-to-point WAN-style link, so a `/30` is exactly right-sized, not wasteful like a `/24` would be here.

### 4.2 Manual Calculation Walkthrough

```
192.168.1.0/24 and 192.168.2.0/24 → 255.255.255.0 → 254 usable hosts each

10.0.0.0/30 → mask 255.255.255.252 → 2^2 - 2 = 2 usable hosts
Network:    10.0.0.0
R1 G0/0:    10.0.0.1
R2 G0/0:    10.0.0.2
Broadcast:  10.0.0.3
```

Switch SVIs are given `.253` on each LAN — one below the router's `.254` gateway address — a convention that keeps "infrastructure management" addresses clustered at the top of each range, visually distinct from end-host addresses at the bottom.

### 4.3 Address Table

(see Topology Reference table above — identical content, single source of truth)

## 5. Pre-Configuration Checklist

- [ ] Confirm inter-LAN routing (R1↔R2) already works before layering SSH on top — SSH from PC1 to SW2 crosses two routers and will fail for routing reasons that have nothing to do with SSH if this isn't solid first
- [ ] Decide the local username/password and enable secret before starting (write them down — losing console+SSH access simultaneously means a physical reset)
- [ ] Know PC1's exact source IP before writing the ACL — a typo here silently locks out the only permitted host
- [ ] Confirm you have out-of-band (console) access as a fallback in case the SSH lockdown breaks remote access mid-lab

## 6. Configuration Tasks

### 6.1 Initial identity and local account

```
Switch> enable
Switch# configure terminal
Switch(config)# hostname SW2
SW2(config)# enable secret ccna
SW2(config)# username jeremy secret ccna
```
Mode: global config. `enable secret` protects privileged EXEC mode with an MD5/SHA-hashed secret (never use `enable password`, which is reversible cleartext). `username ... secret` creates a locally stored, hashed credential used by both console and VTY authentication later. Memory aid: "secret is hashed, password is not — always prefer secret."

### 6.2 Management SVI and default gateway

```
SW2(config)# interface vlan 1
SW2(config-if)# ip address 192.168.2.253 255.255.255.0
SW2(config-if)# no shutdown
SW2(config)# ip default-gateway 192.168.2.254
```
A Layer 2 switch has no routing table for user traffic, but its own management traffic (Telnet/SSH/SNMP originating *from* the switch, or destined *to* it) still needs a next hop for any off-subnet request. `ip default-gateway` — not `ip route` — is the correct command on a Layer 2 IOS device (a Layer 3 switch or router would instead use `ip route 0.0.0.0 0.0.0.0 <next-hop>`). Memory aid: "an L2 switch still needs to know *where to knock* to leave its own subnet, even if it can't route traffic through itself."

### 6.3 Console hardening

```
SW2(config)# line console 0
SW2(config-line)# login local
SW2(config-line)# exec-timeout 5 0
```
`login local` switches authentication from "no password" or a shared line password to the per-user local database. `exec-timeout 5 0` (5 minutes, 0 seconds) auto-terminates an idle session — a walked-away, still-logged-in console session is a classic physical-access risk.

### 6.4 SSH prerequisites: domain name and RSA keys

```
SW2(config)# ip domain-name jeremysitlab.com
SW2(config)# crypto key generate rsa
How many bits in the modulus [512]: 2048
```
SSH requires a domain name (IOS uses hostname + domain to derive the key's identity) and an RSA key pair (asymmetric cryptography underpins the SSH key exchange). 2048 bits is the current minimum recommended modulus size — 512/1024-bit keys are considered weak by modern standards. Memory aid: "no domain name, no keys, no SSH — all three preconditions, no exceptions."

### 6.5 Lock VTY to SSH-only

```
SW2(config)# line vty 0 4
SW2(config-line)# login local
SW2(config-line)# exec-timeout 5 0
SW2(config-line)# transport input ssh
```
`transport input ssh` is the critical line: it removes Telnet (the IOS default `transport input` typically allows both, or Telnet-only on older defaults) so that only encrypted sessions are accepted going forward. Memory aid: "SSH-only isn't the default — you have to say so explicitly."

### 6.6 Restrict management access to PC1 only

```
SW2(config)# access-list 1 permit host 192.168.1.1
SW2(config)# line vty 0 4
SW2(config-line)# access-class 1 in
```
Standard ACL 1 permits only PC1's exact address; the implicit `deny any` at the end blocks everyone else. `access-class` — not `access-group` — is the command that binds an ACL to a **line** (VTY/console) rather than a physical/logical interface. Memory aid: "access-**class** — think **class**room roster of who's allowed in the (management) door; access-**group** is for data-plane traffic on interfaces."

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show ip interface brief` | SW2 | Confirm VLAN 1 SVI is up/up with correct address |
| `show ip ssh` | SW2 | Confirm SSH is enabled, key size, version |
| `show access-lists` | SW2 | Confirm ACL 1 contains exactly the permitted host |
| `show running-config` | SW2 | Confirm VTY block matches `access-class`, `login local`, `transport input ssh` |
| `ssh -l jeremy 192.168.2.253` | PC1 | End-to-end functional test |

### Expected Output Gallery

```
SW2# show ip interface brief
Interface              IP-Address       OK? Method Status                Protocol
Vlan1                  192.168.2.253    YES manual up                    up
```

```
SW2# show ip ssh
SSH Enabled - version 1.99
Authentication timeout: 120 secs; Authentication retries: 3
```

```
SW2# show access-lists
Standard IP access list 1
    10 permit 192.168.1.1
```

```
SW2# show running-config | section vty
line vty 0 4
 access-class 1 in
 exec-timeout 5 0
 login local
 transport input ssh
```

```
PC1$ ssh -l jeremy 192.168.2.253
Password:
SW2> enable
Password:
SW2#
```

## 8. Common Mistakes (80/20)

1. **Forgetting `ip default-gateway`** — SVI comes up fine locally, but remote SSH from PC1 (a different subnet) never reaches SW2 because SW2 has no way to route its own reply traffic back.
2. **Using `access-group` instead of `access-class`** — the ACL simply never takes effect on the VTY lines, and the mistake is easy to miss because IOS doesn't error on it.
3. **Skipping the domain name before `crypto key generate rsa`** — the command fails or silently behaves unexpectedly without it.
4. **Applying the ACL before testing basic reachability** — if PC1 itself is misconfigured, you can't tell whether the ACL, routing, or SSH itself is the problem; verify connectivity in stages.
5. **Locking yourself out** — testing the ACL/SSH lockdown without a console fallback session open; always keep console access available until remote access is confirmed working.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Is the VLAN 1 SVI up/up? | `show ip interface brief` | Add `no shutdown`, correct the address |
| 2 | Does SW2 have a default gateway? | `show running-config \| include default-gateway` | Add `ip default-gateway <R2-address>` |
| 3 | Can PC1 ping SW2 at all? | `ping 192.168.2.253` from PC1 | Fix inter-LAN routing (R1↔R2) first — this is a prerequisite, not an SSH issue |
| 4 | Are RSA keys present? | `show crypto key mypubkey rsa` | Configure domain name, then `crypto key generate rsa` |
| 5 | Does the local username exist and match what's being typed? | `show running-config \| include username` | Recreate the account, check for typos |
| 6 | Is VTY set to `login local` and `transport input ssh`? | `show running-config \| section vty` | Correct the VTY line config |
| 7 | Is the ACL blocking the legitimate host? | `show access-lists` (check hit counters) | Correct the permitted host address, or confirm `access-class ... in` direction |

## 10. Design Analysis

Layering ACL + local auth + SSH + timeout is defense in depth: even if one control is misconfigured or bypassed, the others still constrain risk. The alternative of relying on SSH encryption alone (no ACL) would still let any host on the network *attempt* authentication against SW2 — an ACL removes that attack surface entirely for unauthorized source IPs before authentication is even attempted, which is strictly stronger than authentication-only defenses. The tradeoff is operational: if PC1's IP ever changes, the ACL has to be updated or management access silently breaks — a real operational cost worth documenting in change-management notes.

## 11. Real-World Parallel

This exact pattern — SSH-only, ACL-restricted VTY, local or centralized (TACACS+/RADIUS) auth, idle timeout — is standard on every enterprise switch/router before it's allowed into a production VLAN, often enforced by a compliance/security baseline template rather than manual per-device configuration.

## 12. Stretch Goal

Replace local authentication with centralized AAA via TACACS+ (or RADIUS), so credentials aren't stored per-device, and add `logging` of failed SSH attempts forwarded to a Syslog server (tying this lab back to Day 41) for a security-monitoring integration.

## 13. Self-Assessment

- [ ] I can explain why an L2 switch needs `ip default-gateway`, using this lab's exact topology
- [ ] I can state the difference between `access-class` and `access-group` from memory
- [ ] I can list every prerequisite for SSH to function (hostname, domain, RSA keys, local user, VTY config) without checking notes
- [ ] I configured and tested the ACL myself, confirming a non-PC1 source would be denied
- [ ] I kept a console fallback session open while testing the SSH lockdown, and can explain why that matters

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** SVI/default-gateway on a Layer 2 switch, local authentication (`login local`), enable secret vs. enable password, RSA key generation, `transport input ssh`, standard ACLs, `access-class` vs `access-group`, management-plane defense in depth.

**What I Learned:** Remote access and *secure* remote access are not the same thing. SSH provides encryption, but authentication, source-IP restriction, and session timeout are all separate, independently necessary controls — a network device isn't "secured" just because Telnet was replaced with SSH.

**Skills Practiced:** Initial switch configuration, SVI/default-gateway configuration, local authentication, console security, RSA key generation, VTY hardening, standard ACL creation, `access-class` application, management-plane security, Cisco IOS troubleshooting and verification.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-42/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers, Open vSwitch switches, and Alpine Linux end hosts (using OpenSSH client to test SSH access).
