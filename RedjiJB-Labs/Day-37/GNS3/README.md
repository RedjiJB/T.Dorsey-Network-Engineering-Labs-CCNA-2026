# Day 37 GNS3 Lab — NTP: Network Time Synchronization

Run `build_lab.py` to stand up the Day 37 topology: three VyOS routers in a
full mesh, plus an Alpine Linux host (`NTP-REF`) standing in for the lab
manual's external stratum-1 server (1.1.1.1).

```bash
pip install requests
python build_lab.py
```

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2, R3) | Cisco router | VyOS |
| External NTP server (1.1.1.1) | (simulated internet host) | Alpine Linux running chrony as a local reference |

## NTP-REF setup (Alpine Linux)

```sh
apk add chrony
# Configure chrony to act as a local reference clock (stratum 1-like) instead
# of reaching out to the real internet:
cat >> /etc/chrony/chrony.conf <<'EOF'
local stratum 1
allow 0.0.0.0/0
EOF
rc-service chronyd restart
```

## VyOS NTP equivalents

| Concept | Cisco IOS | VyOS |
|---|---|---|
| Set software clock | `clock set 12:00:00 Dec 30 2020` | `set date "2020-12-30 12:00:00"` |
| Set timezone | `clock timezone EST -5` | `set system time-zone America/New_York` |
| NTP client (upstream server) | `ntp server 1.1.1.1` | `set system ntp server 1.1.1.1` |
| NTP master (no upstream) | `ntp master 8` | VyOS has no direct `ntp master` equivalent -- chrony/ntpd can be configured as a `local stratum` source; the closest analog is running chrony's `local stratum <n>` directive as shown above on NTP-REF |
| NTP authentication | `ntp authentication-key 1 md5 CCNA` + `ntp trusted-key 1` | `set system ntp server <ip> key <id>` plus a key defined under `set system ntp authentication` (syntax varies by VyOS version -- confirm against your installed release) |
| View associations | `show ntp associations` | `show ntp` |
| View sync status | `show ntp status` | `show system ntp` |

**Practical note:** VyOS's NTP stack is built on chrony under the hood, and
its `ntp master`-equivalent behavior is less direct than Cisco IOS's single
command. For hands-on practice of the *authenticated client* configuration
(Phase 4b/4c of the lab manual, R2 and R3 syncing to R1), configure R1 as a
standard NTP client of NTP-REF, then have R2/R3 point their `ntp server` at
R1's directly-connected interface IP -- mirroring the lab manual's addressing
exactly.

## Verifying synchronization

```
R1:~$ show ntp
R1:~$ show system ntp
```

Confirm stratum increases by one at each hop away from NTP-REF, exactly as
worked out in the lab manual's stratum table.
