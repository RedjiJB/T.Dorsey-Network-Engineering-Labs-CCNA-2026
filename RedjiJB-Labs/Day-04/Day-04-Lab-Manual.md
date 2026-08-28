# Day 04 Lab Manual — Basic Device Security & Cisco IOS Administration

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Harden a Cisco router and switch with hostnames, layered password security (enable password vs. enable secret), global password encryption, console/VTY line security, SSH, and a legal banner — then verify and persist the configuration. |
| **Exam Relevance** | CCNA 200-301 — Domain 5 (Security Fundamentals): 5.1 (security concepts), 5.2 (device access control), and Domain 1 device administration basics. This is a heavily tested topic area — expect direct exam questions on `enable password` vs. `enable secret` and on what `login`/`login local` actually do. |
| **Prerequisites** | Day 01–03 (topology building, basic addressing). No prior security-config experience required. |
| **Time Estimate** | 1 – 1.5 hours. |
| **Difficulty** | ⭐☆☆☆☆ (Beginner) — short command list, but a genuinely high-yield topic for the exam and for real device security posture. |

---

## 1. Lab Overview

This lab hardens a single router (R1) and single switch (SW1) using the baseline security configuration every Cisco device should have applied before it's ever placed into production — hostnames, layered enable-mode passwords, console/VTY line protection, SSH remote access, password encryption, and a legal banner. Three end-user PCs are present to represent a normal LAN, but they receive no special configuration; this lab is entirely about the *infrastructure* devices' own security posture, not the traffic flowing through them.

The original lab correctly identifies the core distinction this lab teaches — `enable password` vs. `enable secret` — but stops short of console/VTY line security, SSH, and banners. This expanded version completes that picture, because "secure the enable password" without also securing *how someone reaches the device in the first place* (console and remote access lines) is an incomplete security posture.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Configure device hostnames for unambiguous multi-device management
- Explain the difference between `enable password` and `enable secret`, and state which one production networks should always use
- Apply `service password-encryption` and explain its real (weak, reversible) security value
- Secure console and VTY lines with `password` + `login`, and understand why one without the other fails
- Configure local username-based authentication (`login local`) and SSH as the preferred remote-access method over Telnet
- Add a legal warning banner and explain its role in an "unauthorized access" legal argument
- Verify a device's security posture using `show running-config` and explain why credentials should never appear in plaintext in that output
- Persist configuration changes so they survive a reload

---

## 2. Business Context

**Why would a real company do this?**

Every single network breach post-mortem that starts with "an attacker got console/Telnet/SSH access to a router" traces back to some subset of the steps in this lab being skipped or done wrong. In business terms:

- **"We just got funded and need to pass a basic security audit before our first enterprise customer signs."** → auditors check exactly the things this lab configures: is `enable secret` used (not the plaintext `enable password` alone)? Are passwords visible in `show running-config`? Is there a banner establishing legal notice? Is remote management done over SSH, not Telnet?
- **"An ex-employee still knows our old router password."** → this is a direct argument for `login local` with per-admin usernames instead of one shared line password: you can revoke *one* person's credential without changing a password every admin has memorized.
- **"We got hit with a login banner lawsuit question."** → a network genuinely without a banner has a weaker "unauthorized access" case in court; "implied consent" arguments are legally shakier than an explicit banner stating access is monitored and restricted.
- **"IT keeps forgetting to save configs, and a power blip wipes an hour of work."** → `copy running-config startup-config` (or its shorthand `write memory`) is the unglamorous but critical last step of literally every device change in this course, and it's worth calling out explicitly here because it's the step most often skipped under time pressure.

This lab is deliberately small so the security *reasoning* — not command volume — is what sticks.

---

## 3. Topology Reference

```text
PC1 \
PC2  -- SW1 -- R1
PC3 /
```

| Device | Role |
|---|---|
| R1 | Cisco 2911 router — the device being hardened |
| SW1 | Cisco 2960 switch — the device being hardened |
| PC1, PC2, PC3 | End-user devices, present to complete the topology; no special config required |

---

## 4. IP Addressing Plan

This lab's focus is device *administration* security, not routing — the addressing plan exists only so the topology is complete and SW1's management interface is reachable.

| Device | Interface | IP Address | Mask | Notes |
|---|---|---|---|---|
| PC1 | NIC | 192.168.1.10 | 255.255.255.0 | |
| PC2 | NIC | 192.168.1.11 | 255.255.255.0 | |
| PC3 | NIC | 192.168.1.12 | 255.255.255.0 | |
| R1 | Gi0/0 | 192.168.1.1 | 255.255.255.0 | Default gateway for PC1–PC3 |
| SW1 | VLAN 1 (mgmt) | 192.168.1.2 | 255.255.255.0 | For SSH management of the switch |

A single `/24` (192.168.1.0/24) is used for the whole LAN — with only 3 PCs plus 2 infrastructure management addresses, a `/24` provides generous headroom for growth, and there is no point-to-point link in this lab requiring a `/30`.

---

## 5. Pre-Configuration Checklist

1. Place R1, SW1, PC1, PC2, PC3 and cable with straight-through connections (router-switch, switch-PC).
2. Assign static IPs to PC1–PC3 and R1's LAN interface per Section 4.
3. Confirm both R1 and SW1 boot to a default `Router>`/`Switch>` prompt before starting.

---

## 6. Configuration Tasks

### 6.1 Hostnames

```text
Router>enable
Router#configure terminal
Router(config)#hostname R1
```

```text
Switch>enable
Switch#configure terminal
Switch(config)#hostname SW1
```

> **Mode:** User EXEC → Privileged EXEC → Global Config. `enable` unlocks Privileged EXEC (view-only until you also enter Global Config). Hostnames matter more than they look: once you're managing more than 2–3 devices, an undifferentiated `Router#` prompt in your terminal history is a real source of "which device did I just configure" mistakes.

### 6.2 Enable Password (weak — configure it first to observe the problem)

```text
R1(config)#enable password CCNA
```

> This sets the Privileged EXEC password, but stores it in **plaintext** in `show running-config` unless `service password-encryption` is separately applied. We deliberately configure this first so Step 6.4's verification can show you the problem directly, the way the original lab's Step 3 intended.

### 6.3 Verify the Problem

```text
R1#show running-config
```

```text
!
enable password CCNA
!
```

> Notice `CCNA` appears in cleartext. Anyone who can read the running-config (a shoulder-surfed terminal, a config backup left on a file share, a misconfigured TFTP export) now has the enable password. This is the exact vulnerability the rest of this lab closes.

### 6.4 Enable Secret (the correct, production-standard method)

```text
R1(config)#enable secret Cisco
```

> `enable secret` stores an MD5 hash of the password, not the password itself, and **always takes precedence over `enable password`** if both are configured — IOS will use the secret and ignore the plaintext password entirely if both exist. Production networks should configure `enable secret` and never rely on `enable password` alone.
>
> **Memory aid:** "secret is secret because it's hashed; password is a password because it's just... a password sitting there in plain sight."

### 6.5 Global Password Encryption

```text
R1(config)#service password-encryption
```

> This weakly (type-7, trivially reversible with widely available tools) obscures any *remaining* plaintext passwords in the config — console/VTY line passwords, the leftover `enable password` if you kept it, etc. It is **not** cryptographically strong and should never be relied on as your only protection, but it's standard practice: a `show running-config` glanced at over someone's shoulder shouldn't hand over a password in clear text, even if a determined attacker could still decode it.

### 6.6 Console Line Security

```text
R1(config)#line console 0
R1(config-line)#password consolepass
R1(config-line)#login
R1(config-line)#exit
```

> **Mode:** Line config. `password` sets what's typed; `login` is what actually *enforces* the prompt — set `password` without `login` and IOS never asks for it at all, leaving the console line **effectively open**. This pairing is one of the single most common real-world and exam mistakes: always configure both together, never one alone.

### 6.7 Local Username and SSH (VTY lines)

```text
R1(config)#ip domain-name labnet.local
R1(config)#crypto key generate rsa
How many bits in the modulus [512]: 1024
R1(config)#username admin secret AdminPass1
R1(config)#line vty 0 4
R1(config-line)#login local
R1(config-line)#transport input ssh
R1(config-line)#exit
```

> SSH needs a domain name and an RSA keypair before it can operate — the keypair is what encrypts the session itself. `login local` authenticates against locally-defined usernames (here, `admin`) instead of one shared line password, which is what lets you attribute logins to a specific person and revoke one admin's access without resetting a password everyone else also uses. `transport input ssh` (instead of the default `all`, which includes Telnet) forces remote access over an encrypted protocol only — Telnet sends credentials in plaintext across the wire and should never be enabled on a production device.

### 6.8 Legal Banner

```text
R1(config)#banner motd #
UNAUTHORIZED ACCESS IS PROHIBITED. R1 - Authorized Use Only. All activity may be monitored and reported.
#
```

> The `#` delimiter marks the message boundaries — any character not used inside the message text works as the delimiter. This isn't decorative: an explicit banner meaningfully strengthens a legal "unauthorized access" case, whereas a device with no banner at all relies on weaker "implied consent" arguments.

### 6.9 Repeat All of the Above on SW1

Apply the identical pattern (hostname already set in 6.1; then enable password → verify → enable secret → password encryption → console line → SSH/local login → banner) to SW1, plus the switch-specific management IP:

```text
SW1(config)#interface vlan 1
SW1(config-if)#ip address 192.168.1.2 255.255.255.0
SW1(config-if)#no shutdown
SW1(config-if)#exit
SW1(config)#ip default-gateway 192.168.1.1
```

> A Layer 2 switch has no routing capability, but it still needs an IP on its management VLAN to be reachable for SSH — `ip default-gateway` (not `ip route`, which is a router-only concept) is how a switch reaches off-subnet management traffic.

### 6.10 Save Both Devices

```text
R1#copy running-config startup-config
```

```text
SW1#copy running-config startup-config
```

> `write memory` is the older-syntax shorthand for the same action on IOS devices; both are acceptable, but `copy running-config startup-config` is the more explicit, universally-taught form.

---

## 7. Verification Steps

| Device | Command | What to check |
|---|---|---|
| R1, SW1 | `show running-config` | `enable secret` present as a hash (`$1$...` or similar), no plaintext `enable password` line producing a readable value, line passwords showing as type-7 encrypted strings |
| R1, SW1 | `show ip interface brief` (R1) / `show interfaces vlan 1` (SW1) | Correct IPs, `up/up` |
| R1, SW1 | `show crypto key mypubkey rsa` | Confirms the RSA keypair was generated (SSH prerequisite) |
| R1, SW1 | `show startup-config` vs `show running-config` | Should match after Step 6.10 — confirms the save actually took effect |

### 7.1 Expected Output Gallery

**`R1# show running-config`** (relevant excerpt, after all steps)

```text
!
hostname R1
!
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
enable password 7 104D000A0618
!
username admin secret 5 $1$abcd$xyzExampleHash1234
!
line con 0
 password 7 08204E5A0A16
 login
!
line vty 0 4
 login local
 transport input ssh
!
```

The `5` after `enable secret` indicates an MD5 hash; the `7` after `enable password` and the console `password` indicates weak type-7 encryption from `service password-encryption` — neither shows the actual password text.

**`R1# show crypto key mypubkey rsa`**

```text
% Key pair was generated at: 00:03:12 UTC
Key name: R1.labnet.local
Usage: General Purpose Key
Key is not exportable.
Key Data:
   305C300D 06092A86 4886F70D ...
```

### 7.2 Attempted-Login Behavior Table

| Scenario | Result | Why |
|---|---|---|
| Console login with correct `consolepass` | Prompted, succeeds | `password` + `login` correctly paired |
| Telnet to R1's VTY line | Refused/fails to connect | `transport input ssh` excludes Telnet |
| SSH with username `admin` and correct secret | Succeeds | `login local` authenticates against the local username database |
| SSH with a wrong username | Fails | No matching local account |
| `show running-config` viewed by an unauthorized shoulder-surfer | No usable plaintext credential visible | `enable secret` (hashed) + `service password-encryption` (obscured) |

---

## 8. Common Mistakes (the 80/20)

1. **Setting `password` on a line but forgetting `login`.** The device never prompts for the password at all — the single most common mistake in this entire lab category.
2. **Relying on `enable password` alone and skipping `enable secret`.** It's the weaker, plaintext-storable option; production standard is `enable secret` only (or both, since secret always wins, but never secret-less).
3. **Forgetting `service password-encryption` and being surprised that `show running-config` still shows a readable console/VTY password.**
4. **Trying to configure SSH without first setting a domain name and generating an RSA key.** Both are hard prerequisites — SSH will not come up without them.
5. **Leaving `transport input all` on VTY lines instead of restricting to `ssh`.** This silently leaves Telnet available, which sends credentials in plaintext.
6. **Forgetting to save.** An hour of hardening work disappears on the next reload if `copy running-config startup-config` is skipped.
7. **Applying the hardening to the router but forgetting to repeat it on the switch** (or vice versa) — every device in the topology needs the same baseline posture, not just the "main" one.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | Console never prompts for a password | `login` missing after `password` | `show run \| section line con` | Add `login` under `line console 0` |
| 2 | SSH connection refused entirely | RSA key never generated, or domain name not set | `show crypto key mypubkey rsa` | Set domain name, run `crypto key generate rsa` |
| 3 | SSH prompts but rejects valid-looking credentials | Using the wrong username, or `login local` not applied | `show run \| section line vty` | Confirm `login local` present and `username` entries exist |
| 4 | Telnet still works despite intending SSH-only | `transport input` still set to `all` (default) | `show run \| section line vty` | Set `transport input ssh` explicitly |
| 5 | `show running-config` still shows a readable password | `service password-encryption` never applied | `show run \| include service password-encryption` | Apply the command |
| 6 | Config reverts after a reload | Never saved | `show startup-config` vs `show running-config` | `copy running-config startup-config` |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why configure `enable password` at all if `enable secret` is strictly better?** This lab deliberately configures it first specifically to demonstrate the vulnerability (Section 6.3) before fixing it — in a from-scratch production build, you'd simply configure `enable secret` directly and skip `enable password` entirely.
- **Why local usernames (`login local`) instead of a single shared VTY password?** A shared password can't be revoked for one person without changing it for everyone; per-user accounts (or, at greater scale, centralized AAA/TACACS+/RADIUS — the natural next step after this lab) let you attribute and individually revoke access.
- **Why SSH instead of Telnet, given both are "remote CLI access"?** Telnet transmits every keystroke — including the login password — unencrypted. Anyone positioned to observe the network path (a compromised switch, a rogue access point, a tap) can trivially capture Telnet credentials. SSH encrypts the entire session using the RSA keypair generated in Step 6.7.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a compliance audit (PCI-DSS, SOC 2, or an internal security review) flags every device still allowing Telnet or using `enable password` without `enable secret` — this is a near-universal audit finding at companies that never formalized a device hardening baseline.
- ...an employee leaves the company and IT needs to revoke *their* device access specifically, without resetting a password every other admin also has memorized — this only works cleanly if `login local` with individual accounts was configured from day one.
- ...a legal team asks whether unauthorized-access banners exist on network infrastructure before pursuing action against someone who accessed a device without permission.
- ...a new engineer inherits a device with no saved config and loses an afternoon of prior work to a routine reload, learning the `copy running-config startup-config` lesson the hard way.

---

## 12. Stretch Goal

1. Configure a second local user with a different privilege level (`privilege 15` vs. a restricted level) and explain what changes about what that user can do once logged in.
2. Research and write 3–4 sentences on how TACACS+ or RADIUS-based AAA would replace the local username database used here at enterprise scale, and why centralizing authentication matters once you have more than a handful of devices.
3. Deliberately configure `login` without `password` on a line, observe the resulting behavior (IOS's default response differs depending on platform/line type), and document what you found.

---

## 13. Self-Assessment

- [ ] Can you state, from memory, the difference between `enable password` and `enable secret`, and which one always wins if both are configured?
- [ ] Can you explain why `password` alone on a line isn't enough, and what else is required?
- [ ] Can you list the three prerequisites SSH needs before it will function on an IOS device?
- [ ] Can you explain what `service password-encryption` actually protects against, and what it does *not* protect against?
- [ ] Can you explain, in one sentence, why an explicit banner matters legally?

---

## 14. Key Concepts Demonstrated

- Enable password vs. enable secret and IOS precedence behavior
- Global password encryption (type-7) vs. hashed secrets (MD5)
- Console and VTY line security (`password` + `login` pairing)
- Local username authentication and SSH prerequisites
- Legal warning banners
- Configuration persistence (`copy running-config startup-config`)

## What I Learned

This lab reinforced that "device security" isn't one setting — it's a small stack of independent controls (hashed enable credentials, encrypted line passwords, restricted transport, individually attributable logins, a legal banner) that each close a different gap, and skipping any single one leaves a real, specific weakness rather than a generically "less secure" device. The `password` without `login` mistake in particular is a good example of how a security control can be silently ineffective — the config *looks* complete but does nothing until the second command is added.

## Skills Practiced

- Cisco IOS hostname, enable-mode, and line-level security configuration
- SSH configuration and Telnet elimination
- Local authentication (`login local`) setup
- Configuration verification and persistence

---

## 15. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| R1 | Cisco 2911 | VyOS |
| SW1 | Cisco 2960 | Open vSwitch |
| PC1, PC2, PC3 | Generic PC | Alpine Linux |

Note: VyOS's own hardening syntax differs from IOS (`set system login user admin authentication plaintext-password`, `set service ssh port 22`, etc.) — use the GNS3 build to practice the underlying *concepts* (hashed credentials, SSH-only remote access, banners) even though the exact command syntax won't transfer 1:1 to the CCNA exam's IOS-based questions.

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script.
