# GNS3 Lab — Day 29: OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

Automated build script for the Day 29 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| R1, R2, R3, R4, ISP | VyOS | Open-source, Cisco-like CLI |
| SW1 | Open vSwitch | Built into GNS3, no download needed |
| PC1 | Alpine Linux | End host on R4's LAN |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. VyOS and Alpine Linux templates imported into GNS3 (the script will ask before attempting any download). Open vSwitch ships with GNS3.

## Running the build

```bash
python build_lab.py
```

The script checks the GNS3 server is reachable, checks all required templates exist (asking before downloading anything missing), then creates the project, nodes, and links — safe to re-run, it skips anything already created.

## Applying the lab configuration after nodes are running

VyOS uses a different command family than IOS. Example for R1 (adjust addresses per node/link):

```
configure
set interfaces ethernet eth0 address 10.0.12.1/30
set interfaces ethernet eth1 address 10.0.13.1/30
set interfaces ethernet eth2 address 203.0.113.1/30
set interfaces loopback lo address 1.1.1.1/32

set protocols ospf area 0 network 10.0.12.0/30
set protocols ospf area 0 network 10.0.13.0/30
set protocols ospf area 0 network 1.1.1.1/32
set protocols ospf passive-interface eth2
set protocols ospf passive-interface lo
set protocols ospf auto-cost reference-bandwidth 10000
set protocols ospf default-information originate

commit
save
```

Repeat the equivalent `set interfaces` / `set protocols ospf area 0 network` block on R2, R3, and R4, omitting `passive-interface eth2` and `default-information originate` (those apply only to R1, the ASBR).

## Verifying in VyOS

| IOS command | VyOS equivalent |
|---|---|
| `show ip ospf neighbor` | `show ip ospf neighbor` |
| `show ip ospf interface <if>` | `show ip ospf interface <if>` |
| `show ip route ospf` | `show ip route ospf` |
| `show ip ospf` | `show ip ospf` |

VyOS's OSPF implementation (FRRouting under the hood) shares most `show` command syntax with IOS, which is part of why it's a good open-source stand-in for this lab.

## Caveats

- VyOS's `set` configuration syntax and IOS's mode-based CLI are structurally different, even though the underlying OSPF concepts (cost, reference bandwidth, ASBR, passive interfaces) are identical — treat this as a chance to see the same protocol behavior expressed through a different vendor's CLI, not a 1:1 command translation.
- GNS3's simulated links don't carry real Ethernet/Gigabit bandwidth signaling by default; if `show interfaces` doesn't report the bandwidth you expect, set it explicitly per-interface in VyOS (`set interfaces ethernet eth0 bandwidth <mbps>`) so the OSPF cost calculation has something meaningful to work from.
