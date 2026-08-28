# Day 15 GNS3 Lab — VLSM & Static Routing

## Running the build script

1. Install and start GNS3, with the local server running (default `http://localhost:3080`).
2. `pip install requests`
3. `python build_lab.py`

The script checks the GNS3 server is reachable, checks that the required templates (VyOS, Alpine Linux) exist, and only offers to download an image after asking — it never downloads silently. If a template is missing, import it manually via **Edit > Preferences > Appliances** (or drag a `.gns3a` file in) and re-run the script.

## What gets built

Two VyOS routers (R1, R2) and four Alpine Linux end hosts (PC1–PC4), wired directly per the topology in `Day-15-Lab-Manual.md` — no switches are needed since each PC connects straight to its router's LAN interface.

| Packet Tracer device | GNS3 image |
|---|---|
| Router (2911-class) | VyOS |
| PC | Alpine Linux |

## VyOS vs. Cisco IOS syntax notes

VyOS uses its own configuration-mode CLI rather than IOS commands. Rough equivalents for this lab:

```text
# IOS
interface gigabitEthernet 0/0
 ip address 192.168.5.190 255.255.255.192
 no shutdown

# VyOS
configure
set interfaces ethernet eth0 address 192.168.5.190/26
commit
save
```

```text
# IOS
ip route 192.168.5.192 255.255.255.240 192.168.5.226

# VyOS
set protocols static route 192.168.5.192/28 next-hop 192.168.5.226
commit
save
```

VyOS accepts CIDR notation directly (`/26`, `/28`, `/30`) rather than dotted-decimal masks — this is actually a good way to sanity-check your VLSM math from the manual, since you're forced to re-derive the CIDR prefix rather than just copying a mask.

Alpine Linux hosts are configured with `ip addr add <ip>/<prefix> dev eth0` and `ip route add default via <gateway>`, or via `/etc/network/interfaces` for persistence across reboots.
