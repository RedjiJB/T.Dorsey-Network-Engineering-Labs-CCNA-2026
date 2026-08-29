# Day 11.2 GNS3 Lab — Troubleshooting Static Routes

Builds the same 3-router line topology as Day 11.1 (`PC1 - SW1 - R1 - R2 - R3 - SW2 - PC2`) in its own GNS3 project, so you can seed deliberate faults without disturbing your working Day 11.1 build.

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

Safe to re-run — skips nodes/links that already exist. Once built, manually seed the three faults described in the Lab Manual Section 5 using VyOS `set`/`delete` commands, then practice the diagnostic walkthrough.

## Seeding faults in VyOS syntax

```text
# Wrong destination network (R1 equivalent fault)
set protocols static route 192.168.30.0/24 next-hop 192.168.12.2
delete protocols static route 192.168.3.0/24

# Missing route in one direction (R2 equivalent fault)
delete protocols static route 192.168.3.0/24 next-hop 192.168.13.3

# Wrong interface IP (R3 equivalent fault)
set interfaces ethernet eth0 address 192.168.3.253/24
delete interfaces ethernet eth0 address 192.168.3.254/24
```

Remember to `commit` after each `set`/`delete` block for it to take effect.
