# Day 49 Lab Manual — Port Security

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure port security on two switches with two different enforcement policies: SW1 (F0/1–F0/3) with a strict 1-MAC shutdown policy, and SW2 (G0/1) with a looser 4-MAC restrict + sticky-learning policy. |
| **Exam Relevance** | CCNA 200-301 — Domain 5 (Security Fundamentals): "configure and verify Layer 2 security features" explicitly lists port security. |
| **Prerequisites** | Basic switching (MAC address table), access port configuration, understanding of what a "secure MAC address" means. |
| **Time Estimate** | 1 – 1.5 hours. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner-Intermediate) — commands are short, but the violation-mode behavioral differences are commonly confused. |

---

## 1. Lab Overview + Learning Objectives

Port security restricts which MAC addresses may send traffic on a switchport. This lab applies two deliberately different policies on two switches so you experience both ends of the enforcement spectrum: SW1 locks each of three access ports to exactly one MAC address and shuts the port down on any violation; SW2 allows up to four MAC addresses on one port (a common uplink/small-hub scenario) and merely restricts (drops, doesn't disable) unauthorized traffic, while using sticky learning so the switch builds its own secure MAC list from what it observes.

By the end you will be able to:

- Configure port security with a defined maximum MAC address count
- Explain and configure the three violation modes (protect, restrict, shutdown) and correctly use two of them
- Configure and explain sticky MAC learning
- Configure and explain secure MAC address aging
- Trigger a real violation and interpret the resulting log/counter/interface-state changes
- Recover an err-disabled interface

---

## 2. Business Context

**Why would a real company do this?**

Port security answers the question "what happens if someone plugs an unauthorized device into an open network jack?" — a real, common attack vector (a visitor plugs a rogue laptop into a conference-room jack, or someone adds an unauthorized switch/hub to extend a port). Two different real business scenarios map directly onto this lab's two policies:

- **SW1's strict 1-MAC/shutdown policy** mirrors a **finance or HR closet with static, known devices** — exactly one PC belongs on each jack, ever. Any second MAC address showing up (a rogue device, an accidental hub, a MAC-spoofing attempt) is treated as a security event serious enough to fully disable the port until an administrator investigates — "fail closed."
- **SW2's looser 4-MAC/restrict policy** mirrors a **shared conference-room or lab-bench uplink** where a small unmanaged hub or a docking station legitimately presents a handful of MAC addresses. Restrict mode keeps the port up (so legitimate traffic under the limit keeps flowing) but silently drops anything beyond the fourth MAC and logs it — "fail open enough to not break the room, but still enforce a ceiling."

The business lesson here isn't "always shut down" or "always restrict" — it's that **the correct violation mode depends on the criticality and expected traffic profile of what's plugged into that specific port**, exactly the kind of judgment call a network engineer makes port-by-port in a real building.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-49-Lab-Port-Security.png" alt="Day 49 Port Security Topology" width="900">
</p>

```text
SW1: F0/1, F0/2, F0/3  -- each an access port to one PC, max 1 MAC, violation = shutdown
SW2: G0/1              -- access port toward a shared segment, max 4 MAC, violation = restrict, sticky learning
```

---

## 4. IP Addressing Plan

This lab is a pure Layer 2 security feature — no new IP addressing is introduced. Port security operates on MAC addresses, not IP addresses, which is itself a key concept: **port security cannot distinguish IP-level identity; it only sees the source MAC address in each frame.** Existing PC/switch management addressing from prior labs is assumed unchanged.

---

## 5. Pre-Configuration Checklist

1. Confirm SW1 F0/1–F0/3 and SW2 G0/1 are currently plain `switchport mode access` ports with connected end devices.
2. Know the difference between `switchport port-security mac-address <static-MAC>` (manually typed) and `switchport port-security mac-address sticky` (dynamically learned and then written to the running config) — this lab uses sticky on SW2.
3. Have a spare/rogue device (or the ability to spoof a second MAC in Packet Tracer) ready to intentionally trigger a violation for testing.

---

## 6. Configuration Tasks

### 6.1 SW1 — strict policy on F0/1, F0/2, F0/3

```text
SW1(config)#interface range f0/1 - 3
SW1(config-if-range)#switchport mode access
SW1(config-if-range)#switchport port-security
SW1(config-if-range)#switchport port-security maximum 1
SW1(config-if-range)#switchport port-security violation shutdown
SW1(config-if-range)#switchport port-security aging time 60
```

**Mode:** Interface range config. **`switchport mode access`** must be set before port security will accept configuration — port security cannot be enabled on a dynamic/trunk-negotiating port. **`switchport port-security`** turns the feature on for the port (with no other options, it defaults to `maximum 1` and `violation shutdown` anyway — this lab makes both explicit for clarity). **`maximum 1`** caps the port at exactly one learned/allowed MAC — the "one desk, one device" policy. **`violation shutdown`** is the strictest of the three violation modes: on a violation, the port goes `err-disabled` (both directions stop, link light typically goes amber) until manually recovered. **`aging time 60`** removes a learned secure MAC after 60 minutes of inactivity, so a decommissioned or moved PC doesn't permanently squat the port's one MAC slot. **Threat model this prevents:** an unauthorized second device (rogue laptop, MAC-spoofing attack, small hub silently added by an end user) being able to communicate at all — the port simply stops passing traffic the instant a second MAC is seen. **Memory aid:** "shutdown = zero tolerance."

### 6.2 SW2 — looser policy on G0/1

```text
SW2(config)#interface g0/1
SW2(config-if)#switchport mode access
SW2(config-if)#switchport port-security
SW2(config-if)#switchport port-security maximum 4
SW2(config-if)#switchport port-security violation restrict
SW2(config-if)#switchport port-security mac-address sticky
```

**Mode:** Interface config. **`maximum 4`** permits up to four distinct source MAC addresses on this one port — appropriate for a small unmanaged hub, a docking station passing through a laptop plus peripherals, or a short-term lab bench. **`violation restrict`** drops frames from any MAC beyond the fourth *without* disabling the port — legitimate traffic under the limit keeps flowing, but the violation is still counted and logged (`show port-security interface g0/1` shows an incrementing violation counter). **`switchport port-security mac-address sticky`** tells the switch to dynamically learn up to `maximum` MACs from actual traffic and then convert them into secure, saved (once you `copy run start`) entries automatically — avoiding hand-typing four MAC addresses. **Threat model this addresses differently from SW1:** this port expects a *small, variable* set of legitimate devices, so a hard shutdown-on-violation would create unnecessary outages for a room that legitimately has more than one device; restrict still enforces a hard ceiling (5th+ device denied) without punishing the whole room for it. **Memory aid:** "restrict = keep the room online, just cap it."

### 6.3 Trigger and observe a violation (verification-by-attack)

Simulate a second unauthorized MAC address on one of SW1's ports (in Packet Tracer, connect a second/rogue PC to the same port, or change a connected PC's MAC).

```text
SW1#show interfaces f0/1 status
```

Expect `err-disabled` in the Status column after the violation.

### 6.4 Recover an err-disabled port (SW1 only — restrict mode never disables)

```text
SW1(config)#interface f0/1
SW1(config-if)#shutdown
SW1(config-if)#no shutdown
```

**What it does:** manually cycling the interface clears the err-disabled state after the security issue is investigated and resolved. **Why it matters:** `violation shutdown` is intentionally not self-healing — a human must acknowledge the event, which is the entire point of choosing shutdown mode for high-criticality ports.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show port-security` | Summary of all secured interfaces, max/current/violation counts |
| `show port-security interface f0/1` | Per-port detail: enabled, port status, max MACs, violation mode, sticky count |
| `show port-security address` | List of learned/static secure MAC addresses per interface |
| `show interfaces status` | Confirms `err-disabled` vs `connected` state |
| `show mac address-table` | Confirms which MACs the switch has actually learned |

### 7.1 Expected Output Gallery

**`SW1# show port-security interface f0/1`**

```text
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode              : Shutdown
Aging Time                  : 60 mins
Aging Type                  : Inactivity
SecureStatic Address Aging  : Disabled
Maximum MAC Addresses       : 1
Total MAC Addresses         : 1
Configured MAC Addresses    : 0
Sticky MAC Addresses        : 0
Last Source Address:Vlan     : 000A.CD12.34EF:1
Security Violation Count     : 0
```

**After triggering a violation on F0/1:**

```text
SW1# show interfaces f0/1 status

Port      Name               Status       Vlan       Duplex  Speed Type
Fa0/1                        err-disabled 1          auto    auto 10/100BaseTX
```

```text
%PORT_SECURITY-2-PSECURE_VIOLATION: Security violation occurred, caused by MAC address 00E0.1234.5678 on port FastEthernet0/1.
```

**`SW2# show port-security interface g0/1`** (after learning 4 sticky MACs)

```text
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode              : Restrict
Maximum MAC Addresses       : 4
Total MAC Addresses         : 4
Sticky MAC Addresses        : 4
Security Violation Count     : 2
```

Notice `Port Status: Secure-up` (still up, unlike SW1's err-disabled example) and a non-zero violation count — this is restrict mode working exactly as designed: enforcing the ceiling while keeping the port operational.

**`SW2# show run interface g0/1`** (after sticky learning + save)

```text
interface GigabitEthernet0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 4
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 switchport port-security mac-address sticky 0060.471C.1D19
```

The sticky MAC address is now written directly into the running config as if it had been typed manually — this is what "sticky" means: dynamic learning that becomes static configuration.

---

## 8. Common Mistakes (80/20 rule)

1. **Forgetting `switchport mode access` before `switchport port-security`.** Port security refuses to enable on a port still in dynamic-negotiation trunk mode.
2. **Assuming `switchport port-security` alone sets `maximum 1` / `violation shutdown` is "good enough" and skipping the explicit commands** — while true by default, being explicit avoids surprises when defaults change or when reading someone else's config later.
3. **Confusing `restrict` and `protect`.** Both keep the port up, but only `restrict` logs a violation and increments the counter; `protect` silently drops with no log — most real deployments want `restrict` specifically so violations are visible.
4. **Forgetting that `shutdown`-mode violations require a manual `shutdown`/`no shutdown` to recover** — the port will not come back on its own even after the rogue device is removed.
5. **Setting `maximum 4` on SW2 but never enabling `sticky`, then wondering why the config doesn't "remember" the learned MACs after a reload** — without sticky (or manually typed static MACs), dynamically learned secure MACs are lost on reload.
6. **Not saving configuration (`copy running-config startup-config`) after sticky MACs are learned** — the learned addresses appear in `show running-config` but are lost on reload unless saved, same as any other config change.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | `switchport port-security` command rejected | Port still in trunk/dynamic mode | `show interfaces switchport` | Set `switchport mode access` first |
| 2 | Port shows `err-disabled` and stays down | Violation triggered `shutdown` mode | `show interfaces status` | Investigate the rogue device, remove it, then `shutdown` / `no shutdown` the port |
| 3 | Legitimate 4th device on SW2 can't communicate | `maximum` set too low for the actual device count | `show port-security interface g0/1` | Raise `maximum` or investigate why more than 4 MACs are present |
| 4 | Sticky MACs disappear after reload | Config not saved | `show running-config` vs `show startup-config` | `copy running-config startup-config` |
| 5 | No violation log appears despite unauthorized device | `violation protect` used instead of `restrict`/`shutdown` | `show port-security interface` | Change violation mode to `restrict` or `shutdown` |
| 6 | Port never triggers a violation at all | Device MAC not actually different, or port security not applied to correct interface | `show mac address-table interface f0/1` | Confirm correct interface and that the rogue MAC is genuinely new |

---

## 10. Design Analysis

**Why this design over alternatives?**

- **Why two different violation modes in one lab instead of one consistent policy?** Real networks are never uniformly one policy — a security-sensitive closet and a shared conference room have different risk/availability tradeoffs, and this lab is deliberately structured to force you to justify each choice per-port rather than copy-paste one policy everywhere.
- **Why sticky learning on SW2 but manual/default learning on SW1?** SW1's ports each expect exactly one specific, known device — an administrator plausibly already knows and could type that MAC statically. SW2's port expects a variable small set of devices that isn't worth hand-typing and will change over time (visitors, different laptops docking) — sticky learning lets the switch build the list from observed traffic instead.
- **Why not use 802.1X instead of port security?** 802.1X provides identity-based authentication (username/certificate) rather than MAC-based allow-listing, and is the more robust enterprise answer — but it requires a RADIUS server and supplicant configuration on every endpoint, which is significantly more infrastructure than a lab bench or small office justifies. Port security is the appropriate, lower-overhead tool when the goal is simply "cap how many/which devices use this jack," not full identity verification.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...an employee unplugs their desk phone and plugs in a personal router to get wifi at their desk — the router's MAC differs from the original device, triggering a shutdown-mode violation on a strict port exactly like SW1's.
- ...a conference room's single wall jack legitimately serves a laptop plus a USB dock plus a video bar, all showing distinct MACs through a small integrated hub — exactly the SW2 scenario.
- ...a security audit asks "how do you prevent rogue devices on your wired network," and port security with logged violations is a concrete, demonstrable control to cite.
- ...an engineer gets a 3am page for an err-disabled port and has to determine, from `show port-security interface`, whether it's a genuine intrusion attempt or someone innocently swapping a NIC.

---

## 12. Stretch Goal

1. Configure a fourth port on SW1 with `violation protect` instead of `shutdown` or `restrict`, generate a violation, and compare what does *not* appear in the logs versus `restrict` mode.
2. Configure `errdisable recovery cause psecure-violation` with an interval, so SW1's ports auto-recover after a fixed timer instead of requiring a manual bounce — then explain the security tradeoff of doing this on a high-criticality port.
3. Statically configure (not sticky) all four expected MAC addresses on SW2's G0/1 instead of using sticky learning, and explain when static-typed MACs would be preferable to sticky learning in practice.

---

## 13. Self-Assessment

- [ ] Can you explain, from memory, the behavioral difference between `protect`, `restrict`, and `shutdown` violation modes?
- [ ] Can you write the full port-security config for a strict single-device port without looking?
- [ ] Can you explain what "sticky" learning actually does and why it needs a config save to persist?
- [ ] Can you recover an err-disabled port from memory?
- [ ] Could you justify, in business terms, why two ports in the same building might legitimately use different violation modes?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** port security fundamentals; the three violation modes and their distinct operational impact; sticky MAC learning vs. static vs. dynamic; secure MAC aging; err-disabled recovery.

**What I learned:** port security is a MAC-based, not IP-based, control — it has no concept of user identity, only "how many distinct source MACs have I seen on this wire." The choice of violation mode is a genuine security/availability tradeoff decision that should be made per-port based on what's expected to be plugged in, not applied uniformly out of habit.

**Skills practiced:** port security configuration, violation mode selection and justification, sticky MAC learning, secure MAC aging, err-disabled interface recovery, MAC-address-table verification.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md). Open vSwitch (GNS3's built-in switch) does not implement Cisco-style `switchport port-security` — the README documents this limitation and how to approximate/observe the concept using Linux `arptables`/`ebtables` MAC filtering on the attached Alpine hosts instead, since a true apples-to-apples port-security equivalent isn't available open-source in GNS3.
