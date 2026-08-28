# Day 43 Lab Manual — FTP & TFTP: Cisco IOS File Transfer & Upgrade

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Transfer a Cisco IOS image to two routers using TFTP and FTP respectively, then perform a full safe IOS upgrade workflow including boot configuration and old-image cleanup |
| CCNA 200-301 Domains | 4.0 IP Services (FTP/TFTP), 1.0 Network Fundamentals (routing, `/30` addressing), 5.0 Security Fundamentals (FTP auth vs. TFTP's lack of it) |
| Prerequisites | Static routing, IOS interface configuration, `show` command fluency |
| Estimated Time | 60–75 minutes |
| Difficulty | Intermediate |

## 1. Lab Overview + Learning Objectives

Upgrading router IOS isn't a single command — it's a multi-stage workflow: get the image onto the device (via TFTP or FTP), verify it landed correctly, tell the router to actually boot from it, save the change, reload, verify the new version is running, and only then clean up the old image. This lab does that workflow twice, once with each protocol, so you can directly compare TFTP's simplicity against FTP's authentication.

By the end of this lab you will be able to:

1. Configure `/30` point-to-point addressing and static routing correctly before attempting any file transfer.
2. Explain why file transfers depend entirely on working Layer 3 connectivity first.
3. Perform a TFTP-based IOS transfer and understand TFTP's lack of authentication/encryption.
4. Perform an FTP-based IOS transfer, including configuring the router's FTP client credentials.
5. Configure `boot system` and correctly sequence a safe IOS upgrade (transfer → verify → boot config → save → reload → verify → cleanup).
6. Compare TFTP and FTP across transport, authentication, and reliability.

## 2. Business Context

Every network engineer eventually has to patch a production router — for a security fix, a bug fix, or a feature they need. Doing this wrong (deleting the old image before confirming the new one boots, or botching the boot statement) can brick a device that's now unreachable except by physical console access, potentially in a remote site. This lab's staged workflow — never delete the old image until the new one is proven — is exactly the discipline that separates a routine maintenance window from a multi-hour outage.

## 3. Topology Reference

```text
                 10.0.0.0/24                  192.168.12.0/30

SRV1 -------- SW1 -------- R1 ---------------------- R2
 .1                       G0/1                     G0/0
                           .254      G0/0   G0/0      .2
                                      .1
```

| Device | Interface | Address |
|---|---|---|
| SRV1 | NIC | 10.0.0.1/24 |
| R1 | G0/1 | 10.0.0.254/24 |
| R1 | G0/0 | 192.168.12.1/30 |
| R2 | G0/0 | 192.168.12.2/30 |

IOS image used: `c2900-universalk9-mz.SPA.155-3.M4a.bin`. FTP credentials: `jeremy` / `ccna`.

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-43-Lab-FTP-TFTP.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

`10.0.0.0/24` gives the server LAN generous headroom (254 hosts) even for one server today — standard convention. `192.168.12.0/30` between R1 and R2 is deliberately minimal: a point-to-point WAN-style link only ever needs 2 usable addresses, so a `/30` wastes nothing.

### 4.2 Manual Calculation Walkthrough

```
10.0.0.0/24 → 255.255.255.0 → 254 usable hosts
Network:    10.0.0.0
SRV1:       10.0.0.1
R1 G0/1:    10.0.0.254
Broadcast:  10.0.0.255

192.168.12.0/30 → 255.255.255.252 → 2 usable hosts
Network:    192.168.12.0
R1 G0/0:    192.168.12.1
R2 G0/0:    192.168.12.2
Broadcast:  192.168.12.3
```

### 4.3 Address Table

(see Topology Reference table above — identical content, single source of truth)

## 5. Pre-Configuration Checklist

- [ ] Both router interfaces addressed and `no shutdown` before touching routing
- [ ] R2 has a route to `10.0.0.0/24` via `192.168.12.1` before attempting any transfer
- [ ] `ping 10.0.0.1` succeeds from both R1 and R2 before starting TFTP/FTP
- [ ] Confirm available flash space (`show flash:`) is large enough for the new image before transferring — a failed transfer mid-copy due to insufficient space can leave a corrupt partial file
- [ ] Do not delete the old IOS image until the new one is confirmed booted and working

## 6. Configuration Tasks

### 6.1 Interface addressing

```
R1(config)# interface g0/0
R1(config-if)# ip address 192.168.12.1 255.255.255.252
R1(config-if)# no shutdown
R1(config)# interface g0/1
R1(config-if)# ip address 10.0.0.254 255.255.255.0
R1(config-if)# no shutdown
```
```
R2(config)# interface g0/0
R2(config-if)# ip address 192.168.12.2 255.255.255.252
R2(config-if)# no shutdown
```

### 6.2 Routing

```
R2(config)# ip route 10.0.0.0 255.255.255.0 192.168.12.1
```
Mode: global config. R2 has no directly connected path to `10.0.0.0/24`, so it needs a static route pointing at R1 as the next hop. Verify with `show ip route`, then confirm actual reachability with `ping 10.0.0.1` — this ping is the single most important sanity check in the whole lab, because if it fails, TFTP/FTP will fail for reasons that have nothing to do with TFTP/FTP itself.

### 6.3 TFTP transfer on R1

```
R1# copy tftp: flash:
Address or name of remote host []? 10.0.0.1
Source filename []? c2900-universalk9-mz.SPA.155-3.M4a.bin
```
Mode: privileged EXEC. TFTP runs over UDP port 69, has no authentication, and no encryption — it's the "trivial" in Trivial File Transfer Protocol. This is why it's appropriate only on trusted, controlled networks (e.g., an isolated management VLAN), never across the open internet. Memory aid: "TFTP: fast and simple, but anyone on the wire could intercept or spoof it."

Verify: `show flash:` or `dir flash:` — confirm the new filename is now present.

### 6.4 Boot configuration and safe upgrade sequence on R1

```
R1(config)# boot system flash c2900-universalk9-mz.SPA.155-3.M4a.bin
R1# copy running-config startup-config
R1# reload
```
`boot system` tells IOS which image in flash to load on next boot — without this, the router falls back to its default boot behavior (often the first valid image found), which may not be the one you intended. Always save (`copy running-config startup-config` / `write memory`) before reloading, or the boot statement is lost. After reload, confirm with `show version`. **Only then** remove the old image:
```
R1# delete flash:<old-ios-filename>
```
Memory aid for the whole sequence: "transfer, verify, point, save, reload, verify again, THEN delete."

### 6.5 FTP credentials and transfer on R2

```
R2(config)# ip ftp username jeremy
R2(config)# ip ftp password ccna
R2# copy ftp: flash:
Address or name of remote host []? 10.0.0.1
Source filename []? c2900-universalk9-mz.SPA.155-3.M4a.bin
```
FTP runs over TCP (control on port 21, data on port 20), and unlike TFTP it requires authentication — the router acts as an FTP *client* here, so it needs credentials configured before it can log into SRV1's FTP service. Memory aid: "FTP asks who you are; TFTP doesn't ask at all."

### 6.6 Boot configuration on R2 (identical pattern to 6.4)

```
R2(config)# boot system flash c2900-universalk9-mz.SPA.155-3.M4a.bin
R2# copy running-config startup-config
R2# reload
```
Verify with `show version`, then `show flash:`, then delete the old image only after confirming the new one is running.

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show ip interface brief` | R1, R2 | Confirm interfaces are addressed and up/up |
| `show ip route` | R2 | Confirm the static route to 10.0.0.0/24 exists |
| `ping 10.0.0.1` | R1, R2 | Confirm connectivity to SRV1 before any transfer |
| `show flash:` / `dir flash:` | R1, R2 | Confirm image presence before/after transfer, and before deleting the old one |
| `show version` | R1, R2 | Confirm the router actually booted the new image |
| `show running-config \| include boot` | R1, R2 | Confirm the `boot system` statement is correct |

### Expected Output Gallery

```
R1# copy tftp: flash:
Address or name of remote host []? 10.0.0.1
Source filename []? c2900-universalk9-mz.SPA.155-3.M4a.bin
Destination filename [c2900-universalk9-mz.SPA.155-3.M4a.bin]?
Accessing tftp://10.0.0.1/c2900-universalk9-mz.SPA.155-3.M4a.bin...
Loading c2900-universalk9-mz.SPA.155-3.M4a.bin from 10.0.0.1:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[OK - 33591768 bytes]
```

```
R1# show flash:
Directory of flash:/
    3  -rw-  28282492   <date>  c2900-universalk9-mz.SPA.155-2.T.bin
    4  -rw-  33591768   <date>  c2900-universalk9-mz.SPA.155-3.M4a.bin
```

```
R2# show version
Cisco IOS Software, ... Version 15.3(3)M4a ...
```

## 8. Common Mistakes (80/20)

1. **Attempting a transfer before confirming `ping` connectivity** — wastes time debugging a TFTP/FTP-specific problem that's actually a routing problem.
2. **Deleting the old image before confirming the new one boots** — if the new image is corrupt or the boot statement is wrong, the router now has nothing to fall back to.
3. **Mistyping the exact IOS filename** — file transfer commands don't tab-complete remote filenames; a single character error causes a clean failure that looks like a connectivity issue at first glance.
4. **Forgetting to save configuration before `reload`** — the `boot system` statement (and everything else since the last save) is lost, and the router reloads with the old boot behavior.
5. **Not checking available flash space first** — a transfer that runs out of space mid-copy can leave a corrupted partial file consuming space.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Are interfaces up/up with correct addresses? | `show ip interface brief` | Fix addressing/`no shutdown` |
| 2 | Does the routing table have the needed route? | `show ip route` | Add the missing static route |
| 3 | Can the router actually ping the server? | `ping 10.0.0.1` | Fix routing/addressing before touching TFTP/FTP |
| 4 | Is the filename exactly correct? | Re-check spelling against the source | Retype exactly, case-sensitive |
| 5 | (FTP only) Are credentials correct? | `show running-config \| include ip ftp` | Correct `ip ftp username`/`ip ftp password` |
| 6 | Is there enough flash space? | `show flash:` (check free space) | Delete unneeded files first, or use external storage if available |
| 7 | Did the boot statement take effect? | `show running-config \| include boot`, then `show version` after reload | Correct the `boot system` line, re-save, reload again |

## 10. Design Analysis

TFTP's total lack of authentication makes it faster to set up but appropriate only for isolated, trusted networks (e.g., a dedicated OOB management VLAN) — exactly why it's still common for internal IOS-image or config-backup transfers within a secured network segment. FTP's authentication is a meaningful security improvement but still transmits credentials and data in cleartext (unlike SFTP/FTPS) — in a modern production environment, SCP or SFTP over SSH would be preferred over either protocol shown here, since this lab's tools reflect what's testable on CCNA-era equipment rather than current best practice.

## 11. Real-World Parallel

This exact staged upgrade discipline — never delete the fallback until the new version is proven — mirrors blue/green deployment practice in software engineering, and is standard operating procedure in any network change-management runbook before a maintenance window touching production routers or switches.

## 12. Stretch Goal

Simulate a failed upgrade: configure `boot system` pointing at a deliberately misspelled filename, reload, and observe what the router falls back to. Then practice recovering using ROMmon or the fallback boot behavior — a realistic "what if this goes wrong" exercise that most CCNA labs skip.

## 13. Self-Assessment

- [ ] I can explain why routing must work before attempting any file transfer
- [ ] I can state the transport-layer and authentication differences between TFTP and FTP from memory
- [ ] I can recite the safe upgrade sequence (transfer → verify → boot config → save → reload → verify → delete) without notes
- [ ] I performed both a TFTP and an FTP transfer myself and compared the CLI prompts/behavior
- [ ] I did NOT delete an old image before confirming the new one booted successfully

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** `/30` point-to-point addressing, static routing, TFTP (UDP 69, no auth), FTP (TCP 20/21, authenticated), Cisco flash memory, `boot system`, safe IOS upgrade sequencing.

**What I Learned:** Upgrading a device is a workflow, not a single copy command — it depends on connectivity, storage, correct boot configuration, and a save/reload/verify discipline that protects against a bad upgrade turning into an outage. TFTP and FTP solve the same basic problem (move a file) with very different security postures.

**Skills Practiced:** IPv4 addressing, `/30` networks, static routing, connectivity verification, Cisco flash memory management, TFTP and FTP transfers, FTP authentication, IOS upgrade workflow, boot system configuration, IOS version verification, network troubleshooting.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-43/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using VyOS routers and an Alpine Linux server running both `tftpd-hpa` and `vsftpd` to serve files to the routers.
