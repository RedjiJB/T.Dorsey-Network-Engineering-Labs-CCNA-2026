# Day 41 Lab Manual — Syslog Configuration, Logging Destinations, and Remote Device Monitoring

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure Cisco IOS logging across all four destinations (console, monitor, buffer, remote server) and understand severity-level filtering |
| CCNA 200-301 Domains | 4.0 IP Services (Syslog operation and severity levels), 5.0 Security Fundamentals (centralized logging as a detective control) |
| Prerequisites | Console and Telnet access basics, IOS config mode navigation, IPv4 addressing |
| Estimated Time | 45–60 minutes |
| Difficulty | Beginner–Intermediate |

## 1. Lab Overview + Learning Objectives

Syslog is the backbone of network operational visibility — it's how you know an interface flapped at 3 AM, or that a device crashed and reloaded, without staring at a terminal 24/7. This lab walks through every logging destination IOS supports and demonstrates the single most common beginner trap: generating a log message and being confused when it doesn't show up somewhere you expected.

By the end of this lab you will be able to:

1. Generate and interpret standard IOS Syslog messages (`%LINK-5-CHANGED`, `%LINEPROTO-5-UPDOWN`).
2. Recite all 8 Syslog severity levels from memory and explain the threshold/inclusion behavior.
3. Explain why a Telnet/SSH session does not see live messages by default, and fix it with `terminal monitor`.
4. Configure buffered logging and understand its tradeoffs versus console/monitor output.
5. Configure and verify remote logging to a centralized Syslog server.
6. Explain why centralized logging matters operationally and for security investigations.

## 2. Business Context

When an outage happens at 2 AM, nobody is sitting at a console watching text scroll by. Centralized logging means every device — routers, switches, firewalls, servers — ships its events to one place (a Syslog server, or more commonly today a SIEM like Splunk or an ELK stack) where they can be searched, correlated, and alerted on automatically. This lab's `logging host` + `logging trap debugging` pattern is the exact mechanism that feeds those platforms in production, just scaled up from one router to thousands of devices.

## 3. Topology Reference

- One Cisco 2911 router, `R1`
- One Cisco 2960 switch, `SW1`
- `PC1` — Telnet client
- `PC2` — console-management workstation
- `SRV1` — centralized Syslog server
- LAN: `192.168.1.0/24`

| Device | Interface | Address | Purpose |
|---|---|---|---|
| R1 | G0/0 | 192.168.1.1/24 | Default gateway, managed router |
| PC1 | Fa0 | 192.168.1.12/24 | Telnet client |
| SRV1 | Fa0 | 192.168.1.100/24 | Syslog server |
| PC2 | Console | N/A | Direct console access to R1 |

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-41-Lab-Syslog.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

A single `/24` covers router, two workstations, and a server comfortably with room to grow. SRV1 is placed at `.100`, a common convention that visually separates "infrastructure services" (servers, syslog, DNS, NTP — typically parked in the `.50`–`.150` range) from client workstation addresses.

### 4.2 Manual Calculation Walkthrough

```
192.168.1.0/24 → mask 255.255.255.0 → 2^8 - 2 = 254 usable hosts
Network:    192.168.1.0
Gateway:    192.168.1.1     (R1)
Client:     192.168.1.12    (PC1)
Server:     192.168.1.100   (SRV1)
Broadcast:  192.168.1.255
```

### 4.3 Address Table

(see Topology Reference table above — identical content, single source of truth)

## 5. Pre-Configuration Checklist

- [ ] Console cable connectivity to R1 confirmed from PC2 before starting
- [ ] PC1 can reach R1 via Telnet before testing monitor logging
- [ ] SRV1 has IP reachability to R1 before configuring `logging host`
- [ ] Know your target severity threshold before configuring `logging trap` — decide if you actually want every debug message forwarded in a real deployment (usually you don't; `debugging` is used here to prove filtering works end to end)

## 6. Configuration Tasks

### 6.1 Console access and generating events

```
R1> enable
Password: ccna
R1# configure terminal
R1(config)# interface g0/0
R1(config-if)# shutdown
```
Mode: interface config. Shutting down an active interface forces IOS to emit state-change Syslog messages — this is a safe, repeatable way to generate log traffic on demand for testing.

```
%LINK-5-CHANGED: Interface GigabitEthernet0/0, changed state to administratively down
%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to down
```

```
R1(config-if)# no shutdown
```
Re-enabling generates the mirror-image up messages. The `5` in `%LINK-5-CHANGED` is the severity level — Notifications.

### 6.2 Severity levels

| Level | Name | Description |
|---:|---|---|
| 0 | Emergencies | System is unusable |
| 1 | Alerts | Immediate action required |
| 2 | Critical | Critical condition |
| 3 | Errors | Error condition |
| 4 | Warnings | Warning condition |
| 5 | Notifications | Normal but significant event |
| 6 | Informational | General informational messages |
| 7 | Debugging | Detailed troubleshooting information |

Memory aid: lower number = more severe. "0 is the end of the world, 7 is a firehose of detail." Interface up/down events sit at level 5 — significant enough to always want visibility on, but not an emergency.

### 6.3 Timestamps

```
R1(config)# service timestamps log datetime msec
R1(config)# service timestamps debug datetime msec
```
Mode: global config. Adds date/time (with milliseconds) to every log and debug message. Without this, messages only carry an uptime counter — nearly useless when correlating events across multiple devices with different uptimes. Memory aid: "no timestamp, no timeline."

### 6.4 Monitor logging (the classic gotcha)

From PC1: `telnet 192.168.1.1`, then enable G0/1:
```
R1(config)# interface g0/1
R1(config-if)# no shutdown
```
No message appears in the Telnet session. This is expected, not a bug: **console logging and monitor logging are separate destinations.** A VTY (Telnet/SSH) session must explicitly opt in:
```
R1# terminal monitor
```
Mode: privileged EXEC, and it only applies to the *current* VTY session (not persistent, not global). Memory aid: "console gets it for free; VTY has to ask for it, every session."

### 6.5 Buffered logging

```
R1(config)# logging buffered 8192
```
Mode: global config. Stores the most recent messages in router RAM (8192 bytes here), viewable anytime with `show logging`, independent of whether anyone was watching live. Tradeoff: it's volatile — a reload wipes it — and it wraps once full, silently discarding the oldest entries. Memory aid: "buffer = a rearview mirror with a size limit."

### 6.6 Remote Syslog server

```
R1(config)# logging host 192.168.1.100
R1(config)# logging trap debugging
```
`logging host` sets the destination (SRV1). `logging trap` sets the severity **threshold** for what gets forwarded — `debugging` (7) means "forward everything, levels 0 through 7," because trap thresholds are inclusive of everything more severe. Memory aid: "trap level is a floor for verbosity, not a ceiling for severity — debugging is maximum floor depth, so nothing is excluded."

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show running-config \| include service timestamps` | R1 | Confirm timestamp config |
| `show running-config \| include logging` | R1 | Confirm buffer size, host, trap level |
| `show logging` | R1 | View buffered messages and logging config summary |
| `terminal monitor` then trigger an event | PC1 (via Telnet) | Confirm VTY session now sees live messages |

### Expected Output Gallery

```
R1# show running-config | include logging
logging buffered 8192
logging trap debugging
logging host 192.168.1.100
```

```
R1# show logging
Syslog logging: enabled (0 messages dropped, ... )
    Console logging: level debugging, ... 
    Monitor logging: level debugging, ...
    Buffer logging: level debugging, 8192 bytes, 6 messages logged
    Trap logging: level debugging, 6 message lines logged
        Logging to 192.168.1.100

*Aug 28 2026 06:10:03.221: %LINK-5-CHANGED: Interface GigabitEthernet0/0, changed state to administratively down
*Aug 28 2026 06:10:04.556: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to down
*Aug 28 2026 06:11:12.109: %LINK-5-CHANGED: Interface GigabitEthernet0/0, changed state to up
*Aug 28 2026 06:11:13.442: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to up
```

## 8. Common Mistakes (80/20)

1. **Expecting Telnet/SSH sessions to show logs automatically** — they don't; `terminal monitor` is required every session.
2. **Confusing `logging buffered <size>` (a byte count) with a message count** — the buffer wraps based on space consumed, not number of entries.
3. **Setting `logging trap` too permissively in production** (`debugging` everywhere) — floods the Syslog server with noise; fine for a lab, bad for a live network with hundreds of devices.
4. **Forgetting `service timestamps`** — messages without timestamps are nearly useless once you have more than one device's logs to correlate.
5. **Assuming `logging host` alone is enough** — without a matching `logging trap` severity, the default trap level may not forward what you expect.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Did the event actually happen? | Re-trigger with `shutdown`/`no shutdown` | Confirm you're watching the right interface |
| 2 | Is this a console or VTY session? | Check how you connected | If VTY, run `terminal monitor` |
| 3 | Is the desired destination enabled? | `show running-config \| include logging` | Add `logging buffered`, `logging host`, etc. |
| 4 | Is the severity threshold too restrictive? | `show logging` (check trap/buffer level) | Lower the threshold number's name (e.g., `warnings` → `debugging`) to include more |
| 5 | Is the Syslog server address correct and reachable? | `ping 192.168.1.100` from R1 | Fix IP config or connectivity to SRV1 |
| 6 | Is the buffer actually populated? | `show logging` | If empty, confirm `logging buffered` is configured and an event has occurred since |

## 10. Design Analysis

Four destinations exist because they solve different problems: console for hands-on-keyboard troubleshooting, monitor for remote hands-on-keyboard troubleshooting, buffer for "what just happened, even if I wasn't watching," and remote server for permanent, centralized, cross-device correlation. A network relying only on console/buffer logging loses all history on reload and can never correlate events across devices — which is why every serious operations team treats "ship logs to a central collector" as non-negotiable, even though it adds a dependency (the Syslog server must itself be reliable and reachable).

## 11. Real-World Parallel

This is the exact mechanism behind "why didn't we get paged" postmortems: if `logging trap` is set too restrictively, or the Syslog server's IP changed and nobody updated `logging host`, devices keep generating events that simply vanish into a black hole nobody's watching — a very common real incident-review finding.

## 12. Stretch Goal

Configure a UDP-based Syslog listener on SRV1 (e.g., `rsyslog`), point R1 at it, generate a mix of severities, and build a simple filter that only alerts on level 0–3 messages — practicing the exact triage pattern a real NOC uses to avoid alert fatigue.

## 13. Self-Assessment

- [ ] I can recite all 8 severity levels in order, from memory
- [ ] I can explain, without notes, why a Telnet session doesn't see logs by default
- [ ] I can explain the difference between `logging buffered` and `logging host`/`logging trap`
- [ ] I generated real log messages myself and captured them with `show logging`
- [ ] I can explain why `logging trap debugging` might be inappropriate in a large production network

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** Syslog severity levels, console vs. monitor vs. buffered vs. remote logging, `terminal monitor`, `logging buffered`, `logging host`/`logging trap`, timestamp configuration.

**What I Learned:** Generating a log message and a destination actually receiving it are two separate things — IOS logging is destination-based and severity-filtered, and a message you expect to see can silently not appear simply because the destination or threshold wasn't configured, with zero error message telling you so.

**Skills Practiced:** Cisco Syslog fundamentals, severity-level reasoning, console/monitor/buffered/remote logging configuration, logging timestamps, Telnet administration, VTY session monitoring, log verification, centralized network monitoring, interface-event troubleshooting.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-41/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using a VyOS router, Open vSwitch switch, and Alpine Linux hosts (one as Telnet client, one running `rsyslogd` as the centralized Syslog server).
