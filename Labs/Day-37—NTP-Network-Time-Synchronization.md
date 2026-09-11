# Day 37 — NTP: Network Time Synchronization

## Overview

Today's lab was about **keeping time across the network**. Routers don't have their own reliable time source — they need NTP (Network Time Protocol) to stay synchronized. Accurate timestamps are critical for logging, debugging, certificate validation, and security.

The lab had five phases:
1. Set software clocks on all routers
2. Configure timezones
3. Sync R1 to external NTP server 1.1.1.1
4. Configure R1 as NTP master and sync R2/R3 with authentication
5. Enable hardware calendar updates

---

## Network Topology

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP.png">
  </a>
</p>

---

## Lab Scenario

> "ROUTING HAS BEEN PRECONFIGURED (default route on R1, OSPF on all routers)"
> 1. Configure the software clock on R1, R2, and R3 to 12:00:00 Dec 30 2020 (UTC).
> 2. Configure the time zone of R1, R2, and R3 to match your own.
> 3. Configure R1 to synchronize to NTP server 1.1.1.1. What stratum is 1.1.1.1? What stratum is R1?
> 4. Configure R1 as a stratum 8 NTP master. Synchronize R2 and R3 to R1 with authentication.
> 5. Configure NTP to update the hardware calendars.

Routing and IP addressing are preconfigured. Focus: time.

---

## Topology Summary

| Link | Network | R1 IP | R2 IP | R3 IP |
|------|---------|-------|-------|-------|
| R1—R2 | 192.168.12.0/30 | 192.168.12.1 | 192.168.12.2 | — |
| R1—R3 | 192.168.13.0/30 | 192.168.13.1 | — | 192.168.13.2 |
| R2—R3 | 192.168.23.0/30 | — | 192.168.23.1 | 192.168.23.2 |
| R1—Internet | 203.0.113.0/30 | 203.0.113.1 | — | — |

---

## Phase 1: Configure Software Clock

```cisco
R1(config)#clock set 12:00:00 Dec 30 2020
R2(config)#clock set 12:00:00 Dec 30 2020
R3(config)#clock set 12:00:00 Dec 30 2020
```

**Verification:**
```cisco
R1#show clock
12:00:16.967 UTC Wed Dec 30 2020

R2#show clock
12:00:06.540 UTC Wed Dec 30 2020

R3#show clock
12:00:04.2 UTC Wed Dec 30 2020
```

**Important:** `clock set` must be run from **privileged EXEC mode** (`R1#`), NOT configuration mode. If you're in config mode, use `do clock set`.

**Syntax:**
```
clock set HH:MM:SS MONTH DAY YEAR
```
- Time is **24-hour format**
- Month is the full name: `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`
- If no timezone is set, the clock displays in **UTC**

<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-1.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-1.2 .png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-1.3.png">
  </a>
</p>

---

## Phase 2: Configure Timezone

```cisco
R1(config)#clock timezone EST -5
R2(config)#clock timezone EST -5
R3(config)#clock timezone EST -5
```

**Verification:**
```cisco
R2#show clock
7:25:22.590 EST Wed Dec 30 2020

R1#show clock
7:25:41.818 EST Wed Dec 30 2020
```

**`clock timezone` syntax:**
```
clock timezone <name> <offset-hours> [<offset-minutes>]
```

| Timezone | Offset | Example |
|----------|--------|---------|
| EST | -5 | Eastern Standard (winter) |
| EDT | -4 | Eastern Daylight (summer) |
| CST | -6 | Central Standard |
| PST | -8 | Pacific Standard |

**Cisco IOS doesn't automatically handle DST.** If your region observes daylight saving time, you need `clock summer-time` in addition to `clock timezone`.


<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-2.1.png">
   <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-2.2.png">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-2.3.png">
  </a>
</p>

---

## Phase 3: Configure NTP Client on R1

R1 synchronizes to external NTP server **1.1.1.1** over the Internet.

```cisco
R1(config)#ntp server 1.1.1.1
```

**Verification:**
```cisco
R1(config)#do show ntp associations
```
```
address         ref clock    st   when   poll   reach   delay   offset
~1.1.1.1        127.127.1.1  1     17     32     377     0.00    0.00
~127.127.1.1   .LOCL.        7     1      64     3       0.00    0.01
```

**NTP association table fields:**
| Field | Meaning |
|-------|---------|
| `~` prefix | Configured peer/server |
| `address` | NTP server IP |
| `ref clock` | What this server is syncing to (127.127.1.1 = local, .LOCL. = local clock) |
| `st` | Stratum level |
| `when` | Seconds since last NTP packet |
| `poll` | Polling interval (2^poll seconds) |
| `reach` | Octal reachability register (377 = all last 8 attempts succeeded) |
| `delay` | Round-trip delay (ms) |
| `offset` | Time difference from local clock (ms) |

**Stratum hierarchy:**
- Stratum 0: Atomic clock, GPS, radio reference (not reachable via NTP)
- Stratum 1: Directly connected to Stratum 0
- Stratum 2: Syncs to Stratum 1
- Stratum 3: Syncs to Stratum 2
- ...and so on, up to Stratum 15

**1.1.1.1** is Stratum 1 (Cloudflare's NTP server, backed by atomic/GPS reference). R1, once synced to it, becomes **Stratum 2** (one hop away from the reference).

**To view detailed NTP status:**
```cisco
R1#show ntp status


```
<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-4.1.png">
  </a>
</p>

---

## Phase 4: Configure R1 as NTP Master + R2/R3 Sync with Auth

### Step 4a: Configure R1 as Stratum 8 NTP Master

When R1 has no upstream NTP server, it can act as a master clock using `ntp master`. Stratum 8 means "I'm not directly connected to a reference clock."

```cisco
R1(config)#ntp master 8
```

**Verify R1 is now advertising as master:**
```cisco
R1#show ntp associations
```
```
~127.127.1.1   .LOCL.  7   ...
~1.1.1.1       127.127.1.1  1   ...
```

After `ntp master 8`, R1's local clock is stratum 7 (because 8 + 1 = 9? Actually in NTP, `ntp master 8` sets it to stratum 8. The 127.127.1.1 entry shows stratum 7 in some Packet Tracer versions due to implementation details).

### Step 4b: Configure NTP Authentication

NTP authentication prevents rogue devices from poisoning the time source.

```cisco
! On ALL devices (R1, R2, R3)
R1(config)#ntp authentication-key 1 md5 CCNA
R2(config)#ntp authentication-key 1 md5 CCNA
R3(config)#ntp authentication-key 1 md5 CCNA

! Mark key 1 as trusted on ALL devices
R1(config)#ntp trusted-key 1
R2(config)#ntp trusted-key 1
R3(config)#ntp trusted-key 1
```

### Step 4c: Configure R2 and R3 to Sync to R1

R2 uses its interface IP toward R1 (192.168.12.1):
```cisco
R2(config)#ntp server 192.168.12.1 key 1
```

R3 uses its interface IP toward R1 (192.168.13.1):
```cisco
R3(config)#ntp server 192.168.13.1 key 1
```

**Why use the physical interface IP instead of `ntp source`?** Packet Tracer doesn't support `ntp source`. In real IOS, `ntp source <interface>` tells NTP which source IP to use for outgoing packets. Without it, NTP uses the routing table to pick the source — usually the outgoing interface IP.

### Step 4d: Verification

**R2:**
```cisco
R2#show ntp associations
```
```
address         ref clock    st   when   poll   reach   delay   offset
~192.168.12.1   1.1.1.1      2     27     32     377     0.00    0.00
```

R2 is syncing to R1 (192.168.12.1), which appears as stratum 2 because R1 is stratum 1 relative to R2.

**R3:**
```cisco
R3#show ntp associations
```
```
address         ref clock    st   when   poll   reach   delay   offset
~192.168.13.1   1.1.1.1      2     14     16     37      0.00    0.00
```

R3 is syncing to R1 (192.168.13.1), stratum 2.

**`show clock` confirms synchronized time:**
```cisco
R3#show clock
1:41:41.450 UTC Wed Dec 30 2020
Time source is NTP
```
<p align="center">
  <a href="PASTE-IMAGE-LINK-HERE">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-4.1.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-4.2.png">
    <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP-4.3.png">
  </a>
</p>

`Time source is NTP` confirms the router is getting its time from NTP, not its local clock.

---

## Phase 5: Hardware Calendar Update

The hardware calendar (battery-backed real-time clock) persists across reboots. By default, NTP only updates the software clock. `ntp update-calendar` makes NTP also write to the hardware calendar.

```cisco
R1(config)#ntp update-calendar
R2(config)#ntp update-calendar
R3(config)#ntp update-calendar
```

**Note:** Packet Tracer doesn't have a `show calendar` command, so you can't verify this visually. On real hardware:
```cisco
R1#show calendar
```

**Why this matters:** After a reboot, a router with `ntp update-calendar` will have the correct time immediately. Without it, the router boots with 00:00:00 Jan 1 1992 (or whatever the hardware clock was last set to) and has to wait for NTP to re-sync.

---

## NTP Commands Reference

```cisco
! Set software clock (EXEC mode only)
clock set 12:00:00 Dec 30 2020

! Set timezone
clock timezone EST -5
clock summer-time EDT recurring 2 Sun Mar 1 Sun Nov

! View clock
show clock
show clock detail

! NTP server (upstream)
ntp server 1.1.1.1
ntp server 192.168.12.1 key 1

! NTP master (make this router a time source)
ntp master 8

! NTP authentication
ntp authentication-key 1 md5 CCNA
ntp trusted-key 1

! Hardware calendar sync
ntp update-calendar

! View NTP status
show ntp associations
show ntp associations detail
show ntp status
show ntp servers
```

---

## NTP Authentication Flow

```
                          +------------+
                          | NTP Server |
                          | 1.1.1.1    |
                          | Stratum 1  |
                          +-----+------+
                                |
                          NTP sync (unauthenticated)
                                |
    +--------+--------+---------+---------+
    |        |        |                    |
  R1       R2       R3              (Internet)
  203.0.113.1 192.168.12.1/2  192.168.13.1/2
```

**With authentication:**
```
R3 ---(NTP with key 1)---> R1 (master, stratum 8)
R2 ---(NTP with key 1)---> R1 (master, stratum 8)
```

Authentication key exchange:
1. Both sides share key 1 with password `CCNA`
2. NTP packets include an MD5 hash of the packet content + key
3. Receiver verifies hash before accepting time update
4. Without matching key, NTP association stays unsynced

---

## Stratum Calculation

| Device | NTP Role | Stratum |
|--------|----------|---------|
| 1.1.1.1 | External reference (GPS/atomic) | 1 |
| R1 (synced to 1.1.1.1) | Client of stratum 1 | 2 |
| R1 (ntp master 8, no upstream) | Standalone master | 8 |
| R2 (synced to R1) | Client of R1 | 3 |
| R3 (synced to R1) | Client of R1 | 3 |

**Stratum rule:** A device's stratum = upstream stratum + 1. The highest valid stratum is 15. Stratum 16 means "unsynced / invalid."

---

## Common NTP Mistakes

| Mistake | Result |
|---------|--------|
| `clock set` in config mode without `do` | Command not recognized in config mode |
| Wrong timezone offset | Clock shows wrong local time |
| Forgetting `ntp trusted-key` | Authentication configured but not trusted |
| Mismatched auth keys between devices | Association won't sync |
| Using `ntp master` AND `ntp server` simultaneously | Can cause loop or priority conflict |
| Missing `ntp update-calendar` | Time resets to old hardware clock value after reboot |
| Not waiting for sync | `show ntp associations` shows `~` but no `*` — still syncing |

---

## What I Learned

**NTP is the backbone of network reliability.** Logs with wrong timestamps are useless for forensics. Certificate validation fails if clocks drift. Routing protocol adjacencies can be affected by timestamp mismatches. Accurate time isn't optional — it's infrastructure.

**Stratum is a trust hierarchy.** Stratum 1 devices have atomic/GPS clocks. Stratum 2 devices sync to Stratum 1. Every hop adds 1 to the stratum number. A Stratum 16 clock means "I have no idea what time it is" — NTP treats it as unsynced.

**Authentication matters.** Without NTP auth, any device on your network can broadcast fake time updates. In production, always use `ntp authentication-key` + `ntp trusted-key`. The shared secret ensures only authorized devices can influence your clock.

**The software clock vs hardware calendar distinction is critical.** `clock set` only changes the running software clock. After a reboot, the router reverts to the hardware calendar. `ntp update-calendar` bridges the gap — it writes the synced NTP time to the hardware clock so it persists across reboots.

**Packet Tracer doesn't support `ntp source`.** In real IOS, `ntp source <interface>` controls which source IP NTP packets use. Without it, NTP picks the IP of the outgoing interface based on the routing table. This usually works, but in multi-homed scenarios you need `ntp source` to force a specific interface.

**The `show ntp associations` reach field is octal.** A value of 377 (octal) = 255 (decimal) = all 8 most recent NTP attempts succeeded. If you see 0, the server is unreachable.

---

## Lab Status

✅ Day 37 Complete

### Topics Covered

* NTP: purpose, stratum hierarchy, association table
* Software clock configuration: `clock set`
* Timezone configuration: `clock timezone EST -5`
* NTP client: `ntp server 1.1.1.1`
* NTP master: `ntp master 8`
* NTP authentication: `ntp authentication-key 1 md5`, `ntp trusted-key 1`
* `show ntp associations` interpretation (st, when, poll, reach, delay, offset)
* Hardware calendar: `ntp update-calendar`
* Stratum calculation: upstream stratum + 1
* Packet Tracer limitation: no `ntp source` command

---

**Repository:** [Network-Engineering-Labs-CCNA-2026](https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026)
