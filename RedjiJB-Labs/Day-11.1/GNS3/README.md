# Day 11.1 GNS3 Lab — Configuring Static Routes

Automates the build of the 3-router line topology (`PC1 - SW1 - R1 - R2 - R3 - SW2 - PC2`) from the Day 11.1 Lab Manual, using free/open-source images in place of Cisco IOS/Packet Tracer devices.

## Image mapping

| Packet Tracer device | GNS3 image | Notes |
|---|---|---|
| Cisco 2911 (R1, R2, R3) | VyOS | Cisco-like CLI, supports static routing |
| Cisco 2960 (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| Generic PC (PC1, PC2) | Alpine Linux | Lightweight, fast boot |

## Usage

```bash
pip install requests
python build_lab.py
```

The script checks the GNS3 server is reachable, verifies all required templates exist, and only offers to download an image if you explicitly type `y`. It is safe to re-run — it skips nodes/links that already exist.

## VyOS static route syntax (vs. Cisco IOS)

| IOS | VyOS |
|---|---|
| `ip route 192.168.3.0 255.255.255.0 192.168.12.2` | `set protocols static route 192.168.3.0/24 next-hop 192.168.12.2` |
| `interface g0/0` / `ip address 192.168.1.254 255.255.255.0` | `set interfaces ethernet eth0 address 192.168.1.254/24` |
| `show ip route` | `show ip route` (same command, VyOS mirrors this one) |

After `set` commands, VyOS requires `commit` then `save` to apply and persist configuration — there's no direct equivalent of IOS's `copy running-config startup-config` until you run `save`.
