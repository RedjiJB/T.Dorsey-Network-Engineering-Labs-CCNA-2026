# Day 37 Lab Manual — NTP: Network Time Synchronization

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Synchronize software clocks across a three-router topology using NTP: set/verify local time, configure timezone, sync a router to an external stratum-1 server, promote that router to an authenticated NTP master for its peers, and persist time across reboots via the hardware calendar. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Services: NTP client/server operation), Domain 5 (Security Fundamentals: NTP authentication). |
| **Prerequisites** | Basic router CLI navigation; OSPF/default-route connectivity already in place (this lab assumes routing is preconfigured). |
| **Time Estimate** | 60–80 minutes. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner–Intermediate) — commands are short, but stratum arithmetic and the authentication chain require careful attention. |

---

## 1. Lab Overview + Learning Objectives

Routers have no reliable sense of time on their own — no atomic clock, no GPS, just a free-running oscillator that drifts. NTP (Network Time Protocol) fixes this by letting devices synchronize to a trusted time source, hop by hop, through a hierarchy called **stratum**. This lab builds that hierarchy from the ground up: manually set clocks (so you can see what "wrong" looks like), configure timezones, sync one router to a real external stratum-1 source, then have that router become the trusted internal time source for its two peers — with authentication, so a rogue device on the network can't feed them false time.

By the end of this lab you will be able to:

- Set and verify a router's software clock and timezone
- Configure an NTP client (`ntp server`) and interpret `show ntp associations` output
- Explain stratum and calculate a device's stratum from its upstream source
- Configure a router as an NTP master for devices with no external time source
- Configure NTP authentication (`ntp authentication-key`, `ntp trusted-key`) and explain what it protects against
- Explain the software clock vs. hardware calendar distinction and why `ntp update-calendar` matters after a reboot

---

## 2. Business Context

**Why would a real company do this?**

- **"Our security team can't correlate log events across three different firewalls because their timestamps don't agree."** This is the single most common real-world reason NTP exists on every piece of network infrastructure: incident response and forensics are impossible if Router A's 2:00 PM doesn't match Router B's 2:00 PM. Synchronized time is a prerequisite for any centralized logging or SIEM deployment.
- **"Our internal CA-issued certificates are being rejected as 'not yet valid' or 'expired' even though they shouldn't be."** Certificate validation (TLS handshakes, 802.1X, site-to-site VPN) checks a certificate's validity window against the device's local clock — a clock that's drifted even a few hours can cause a hard authentication failure. NTP is the fix.
- **"We don't want a rogue device on our network broadcasting fake time to trick our systems into accepting an expired certificate, or to throw off audit logs."** This is exactly what NTP authentication (Phase 4b) defends against — without it, any device that can reach a router's NTP port can attempt to influence its clock.
- **"We need our routers to boot with the correct time immediately, not wait several minutes for NTP to re-sync after every power event."** `ntp update-calendar` (Phase 5) is exactly this: writing the synced time to the battery-backed hardware clock so a reboot doesn't start the router back at a stale, meaningless timestamp.

---

## 3. Topology Reference

Three routers (R1, R2, R3), fully meshed via point-to-point links, with R1 also facing an external "Internet" link toward an NTP reference server. Routing (default route on R1, OSPF everywhere) is preconfigured — this lab is entirely about the time layer on top of already-working connectivity.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP.png" alt="Day 37 NTP Topology" width="900">
</p>

---

## 4. IP Addressing Plan

Addressing is preconfigured for this lab (the focus is time synchronization, not IP design), but understanding it is required to reason about which interface IP each router uses as its NTP source:

| Link | Network | R1 IP | R2 IP | R3 IP |
|---|---|---|---|---|
| R1—R2 | 192.168.12.0/30 | 192.168.12.1 | 192.168.12.2 | — |
| R1—R3 | 192.168.13.0/30 | 192.168.13.1 | — | 192.168.13.2 |
| R2—R3 | 192.168.23.0/30 | — | 192.168.23.1 | 192.168.23.2 |
| R1—Internet | 203.0.113.0/30 | 203.0.113.1 | — | — |

**Why this matters for NTP specifically:** R2 and R3 each reach R1 over their own dedicated /30 link, so when they configure `ntp server`, they must point at R1's IP *on that specific link* (192.168.12.1 for R2, 192.168.13.1 for R3) — not some other interface's address, since NTP (like most protocols) needs a specific, reachable source/destination pairing, not just "any IP that happens to belong to R1."

---

## 5. Pre-Configuration Checklist

1. Confirm routing (OSPF + R1's default route) is already functional — `ping` across all three routers before touching any clock command, since a broken NTP association is much harder to debug on top of a broken routing problem.
2. Decide on a timezone offset before starting Phase 2 (Section 6.2 has a reference table) so you're not guessing during configuration.
3. Agree on the NTP authentication key number and password ahead of time (this lab uses key `1`, password `CCNA`) — all three routers must match exactly, or authentication silently fails.

---

## 6. Configuration Tasks

### 6.1 Phase 1 — Set the software clock

```cisco
R1#clock set 12:00:00 Dec 30 2020
R2#clock set 12:00:00 Dec 30 2020
R3#clock set 12:00:00 Dec 30 2020
```

- **Mode:** Privileged EXEC — **not** configuration mode. `clock set` is an EXEC-level command because it's an immediate action, not a persistent configuration line. If you're already in config mode, prefix it with `do`: `R1(config)#do clock set 12:00:00 Dec 30 2020`.
- **Syntax:** `clock set HH:MM:SS MONTH DAY YEAR`, 24-hour time, full month name (`Dec`, not `December` or `12`).
- **Memory aid:** "`clock set` is a verb you do right now, not a fact you configure for later" — that's why it lives in EXEC mode.
- Without a timezone configured yet, this displays as UTC — that gets fixed in Phase 2.

### 6.2 Phase 2 — Configure timezone

```cisco
R1(config)#clock timezone EST -5
R2(config)#clock timezone EST -5
R3(config)#clock timezone EST -5
```

- **Mode:** Global configuration.
- **Syntax:** `clock timezone <name> <offset-hours> [<offset-minutes>]`. The name is a label you choose (commonly the standard abbreviation); the offset is hours from UTC.

| Timezone | Offset |
|---|---|
| EST | -5 |
| EDT | -4 |
| CST | -6 |
| PST | -8 |

- **Cisco IOS does not auto-handle Daylight Saving Time.** If your region observes DST, you additionally need `clock summer-time EDT recurring 2 Sun Mar 1 Sun Nov` (or equivalent) — otherwise the clock will be an hour off for roughly half the year.
- **Memory aid:** "Timezone is a display filter on top of UTC, not a different clock" — the router still tracks UTC internally; `clock timezone` only changes what's shown.

### 6.3 Phase 3 — Sync R1 to external NTP server 1.1.1.1

```cisco
R1(config)#ntp server 1.1.1.1
```

- **Mode:** Global configuration.
- **What it does:** Adds 1.1.1.1 as an NTP peer R1 will poll for time. R1 does not need to be told this is "the" server versus "a" server — you can configure multiple `ntp server` lines and IOS will select the best one using NTP's own selection algorithm.
- **`1.1.1.1` is stratum 1** — it's directly connected to a reference clock (Cloudflare's NTP service, GPS/atomic-backed). Once R1 syncs to it, **R1 becomes stratum 2** — one hop removed from the reference.
- **Stratum rule:** a device's stratum = upstream stratum + 1, all the way to a maximum of 15. Stratum 16 means "unsynced / invalid," not "very far from the reference."
- **Memory aid:** "Stratum counts hops from the atomic clock, like a family tree counting generations from a common ancestor."

### 6.4 Phase 4a — Configure R1 as a stratum 8 NTP master

```cisco
R1(config)#ntp master 8
```

- **What it does:** Tells R1 to advertise *itself* as a time source, even without any upstream server, for any device that syncs to it. The `8` is the stratum R1 will claim — a deliberately high (i.e., "low trust/low precision") number, signaling "I'm a fallback/local master, not a real reference-grade source."
- **When to use this over `ntp server`:** when a router has no reachable external time source (an isolated lab network, an air-gapped segment) but downstream devices still need a consistent internal clock.
- **Caution:** running `ntp master` and `ntp server` on the same router simultaneously can create ambiguity about which is authoritative — see Common Mistakes.

### 6.5 Phase 4b — Configure NTP authentication (all three routers)

```cisco
R1(config)#ntp authentication-key 1 md5 CCNA
R2(config)#ntp authentication-key 1 md5 CCNA
R3(config)#ntp authentication-key 1 md5 CCNA

R1(config)#ntp trusted-key 1
R2(config)#ntp trusted-key 1
R3(config)#ntp trusted-key 1
```

- **`ntp authentication-key 1 md5 CCNA`** — defines key ID 1 with password `CCNA`, MD5-hashed. This must be configured **identically** (same key ID, same password) on every device that needs to authenticate with each other.
- **`ntp trusted-key 1`** — marks key 1 as acceptable for authenticating incoming NTP updates. Defining a key without marking it trusted means it exists but is never actually used to validate anything — a common gap (see Common Mistakes).
- **Why this matters:** without authentication, any device that can reach a router's NTP service could attempt to feed it false time — potentially breaking certificate validation or covering an attacker's tracks in logs by skewing timestamps. Authentication ensures only devices holding the shared key can influence the clock.
- **Memory aid:** "Two steps, like a lock and a key: `authentication-key` cuts the key, `trusted-key` puts it on your keyring."

### 6.6 Phase 4c — Configure R2 and R3 to sync to R1, authenticated

```cisco
R2(config)#ntp server 192.168.12.1 key 1
R3(config)#ntp server 192.168.13.1 key 1
```

- Each router points at **R1's IP on its own direct link** (Section 4) — R2 uses 192.168.12.1, R3 uses 192.168.13.1.
- **`key 1`** appended to `ntp server` tells IOS to authenticate this specific association using key 1 — matching what was configured in 6.5.
- **Why not use `ntp source` to be explicit about the outgoing interface?** In real IOS, `ntp source <interface>` pins the source IP used for outgoing NTP packets, useful in multi-homed scenarios where the routing table might otherwise pick an unexpected interface. This lab's simulated environment doesn't support it, so NTP falls back to the routing table's natural choice of outgoing interface IP, which happens to be correct here since each router only has one path to R1.

### 6.7 Phase 5 — Enable hardware calendar updates

```cisco
R1(config)#ntp update-calendar
R2(config)#ntp update-calendar
R3(config)#ntp update-calendar
```

- **What it does:** By default, NTP only updates the router's **software clock** (the running, in-memory clock). The **hardware calendar** — a battery-backed real-time clock chip that persists across power loss — is separate and does not get updated automatically. `ntp update-calendar` bridges that gap.
- **Why this matters:** without it, a router that loses power reboots with whatever stale time was last written to the hardware calendar (sometimes a meaningless default like Jan 1 1992), and has to wait for NTP to re-sync before its clock is trustworthy again — a window during which logs and certificate checks may be wrong.
- **Memory aid:** "Software clock is RAM, hardware calendar is a wristwatch with its own battery — `ntp update-calendar` keeps the wristwatch set too."

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show clock` | Current time, timezone label, and whether "Time source is NTP" appears (confirms sync, not just a manually-set clock) |
| `show ntp associations` | Peer list, stratum, reachability register, offset — the core NTP health check |
| `show ntp associations detail` | Per-peer authentication status and more granular timing stats |
| `show ntp status` | This device's own synchronization state and stratum |

### 7.1 Expected Output Gallery

**`R1(config)#do show ntp associations`** (after Phase 3, synced to 1.1.1.1)
```
address         ref clock    st   when   poll   reach   delay   offset
~1.1.1.1        127.127.1.1  1     17     32     377     0.00    0.00
~127.127.1.1   .LOCL.        7     1      64     3       0.00    0.01
```

**`R2#show ntp associations`** (after Phase 4, synced to R1 with authentication)
```
address         ref clock    st   when   poll   reach   delay   offset
~192.168.12.1   1.1.1.1      2     27     32     377     0.00    0.00
```

**`R3#show clock`** (after successful sync)
```
1:41:41.450 UTC Wed Dec 30 2020
Time source is NTP
```

**Field reference for `show ntp associations`:**

| Field | Meaning |
|---|---|
| `~` prefix | Configured peer/server |
| `ref clock` | What this server is itself syncing to |
| `st` | Stratum level |
| `when` | Seconds since last NTP packet received |
| `poll` | Polling interval, expressed as 2^poll seconds |
| `reach` | Octal reachability register — `377` (octal) = 255 (decimal) = all 8 of the last 8 poll attempts succeeded |
| `delay` | Round-trip delay to that peer, in ms |
| `offset` | Time difference between local clock and peer, in ms |

`Time source is NTP` in `show clock` output is the definitive confirmation that a device is running on synchronized time rather than a manually-set or free-running clock.

---

## 8. Common Mistakes (the 80/20)

1. **Running `clock set` in configuration mode without `do`.** It's an EXEC command — config mode will reject it (or, with `do`, execute it correctly from within config mode).
2. **Setting the wrong timezone offset direction.** EST is `-5` (behind UTC), not `+5` — a common sign error that produces a clock exactly 10 hours off from correct.
3. **Forgetting `ntp trusted-key` after `ntp authentication-key`.** The key exists but authentication won't actually validate against it — a silent gap that looks configured but doesn't function as expected.
4. **Mismatched authentication keys between devices** (different key numbers, or different passwords). The association will never authenticate, and depending on IOS behavior, may silently stay unsynced rather than throwing an obvious error.
5. **Running `ntp master` and `ntp server` on the same device without understanding the interaction.** This can create ambiguity about which source is authoritative — generally, decide whether a router is a client (has `ntp server` pointing upstream) or a master (has `ntp master`, no upstream), not both, unless you specifically understand the fallback behavior you're configuring.
6. **Not waiting long enough before checking sync status.** `show ntp associations` showing only `~` (configured) without a `*` (currently synced, in real IOS output) means the association is still stabilizing — NTP sync isn't instantaneous, especially on the first few polls.
7. **Forgetting `ntp update-calendar` and being surprised time resets after a reboot.** The software clock and hardware calendar are genuinely separate state — Section 6.7 covers why.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | `clock set` rejected in config mode | Command issued at the wrong CLI level | (observe the error) | Exit to EXEC mode, or prefix with `do` |
| 2 | `show clock` shows a plausible time but wrong by several hours | Timezone offset wrong or missing | `show clock` (compare against known correct local time) | Correct `clock timezone <name> <offset>` |
| 3 | `show ntp associations` shows the peer with `reach` = 0 | No connectivity to the NTP server, or wrong IP configured | `ping <ntp-server-ip>` | Fix underlying routing/reachability, or correct the configured server IP |
| 4 | Association exists but never authenticates / stratum stays at 16 (unsynced) | Authentication key mismatch, or `trusted-key` missing on one side | `show ntp associations detail` on both ends | Ensure `authentication-key` and `trusted-key` match exactly on every device in the chain |
| 5 | R2/R3 stratum doesn't match "R1's stratum + 1" as expected | R2/R3 pointed at the wrong R1 interface IP, or R1 itself isn't yet synced | `show ntp associations` on R1 first, then R2/R3 | Confirm R1 is synced/master before troubleshooting downstream clients |
| 6 | Time reverts to a very old date after a simulated reboot | `ntp update-calendar` was never configured | (observe post-reboot `show clock`) | Add `ntp update-calendar` on the affected device |

---

## 10. Design Analysis

- **Why sync R1 to an external source but make R1 itself the master for R2/R3, rather than having all three sync to 1.1.1.1 directly?** This mirrors real deployments: internal devices typically shouldn't all independently reach out to the internet for time (more attack surface, more external dependency, more traffic). Instead, one edge device syncs externally and becomes the trusted internal source — a hub-and-spoke trust model that's easier to secure (one authenticated boundary) and easier to audit.
- **Why authenticate the internal R1→R2/R3 relationship but not the R1→1.1.1.1 relationship?** Public NTP servers like 1.1.1.1 don't offer authentication to arbitrary clients in the way described here (real-world NTP authentication to public pools is a separate, more complex topic — NTS, symmetric keys distributed out of band, etc.) — but the internal relationship is fully under your control, so there's no reason not to authenticate it, and every reason to (Section 2's rogue-device scenario).
- **Why `ntp master 8` and not `ntp master 1` or some lower number?** A low stratum number signals "close to a real reference clock" — claiming stratum 1 for a router with no actual reference clock would be misleading to any other device that might later peer with it. Stratum 8 is a deliberately conservative, clearly-not-a-real-reference number for a fallback/local master role.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a SOC (security operations center) requires all network devices to sync to an internal, authenticated NTP hierarchy specifically so log correlation across devices is trustworthy during an incident investigation.
- ...a PKI deployment (site-to-site VPNs, 802.1X, internal HTTPS) starts failing intermittently and the root cause turns out to be clock drift on one device pushing it outside a certificate's validity window.
- ...a data center standard mandates `ntp update-calendar` (or equivalent) on every router/switch specifically so a power event doesn't leave devices booting with garbage timestamps until NTP re-converges.

---

## 12. Stretch Goal

1. Add a second external NTP server to R1 (e.g., `ntp server 1.1.1.2`) and observe how `show ntp associations` selects between the two — which one does IOS prefer, and what fields would you check to understand why?
2. R2 and R3 currently only sync to R1. What would happen, in terms of stratum and resiliency, if you also configured R2 and R3 to sync to each other as a backup? Would this create any issues?
3. Research `ntp source <interface>` (not available in this lab's simulated environment) and explain a specific multi-homed scenario where omitting it would cause NTP to select the wrong outgoing interface.

---

## 13. Self-Assessment

- [ ] Can you explain, from memory, why `clock set` requires EXEC mode instead of configuration mode?
- [ ] Can you calculate a device's stratum given its upstream server's stratum, without looking at a reference table?
- [ ] Can you name both commands required for NTP authentication and explain what happens if only one is configured?
- [ ] Can you explain the difference between the software clock and the hardware calendar, and why `ntp update-calendar` matters?
- [ ] Given `show ntp associations` output, can you identify whether a peer is currently reachable, and roughly how recently it was polled?

---

## 14. Key Concepts Demonstrated

- Software clock configuration (EXEC-mode `clock set`) vs. persistent configuration (`clock timezone`)
- NTP client configuration and stratum-based trust hierarchy
- NTP master role for networks with no external reference
- NTP authentication (`authentication-key` + `trusted-key`) as a defense against rogue time sources
- Software clock vs. hardware calendar and the role of `ntp update-calendar`

## 15. What I Learned

Accurate time isn't a "nice to have" — it's infrastructure that logging, certificate validation, and security investigations all silently depend on. The stratum system is an elegant way to express "how many hops from ground truth" without every device needing to know the whole hierarchy — a device just needs to know its immediate upstream's stratum and add one. Authentication turns a shared "everyone trusts everyone" assumption into an explicit, provable trust relationship, which matters because time is exactly the kind of thing an attacker would want to quietly manipulate to cover their tracks. And the software-clock-vs-hardware-calendar split is a good reminder that "the router's time is right" and "the router's time survives a reboot" are two different guarantees that need two different commands.

## 16. Skills Practiced

- Manual clock configuration and timezone math
- NTP client/server/master role configuration
- Stratum calculation and NTP association table interpretation
- NTP authentication configuration and verification
- Distinguishing software-clock from hardware-calendar persistence

---

## 17. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for a script that builds this lab's three-router topology (plus a simulated "Internet" NTP reference host) using VyOS routers and an Alpine Linux stand-in for the external NTP server, with the VyOS NTP configuration equivalents for each phase of this lab.
