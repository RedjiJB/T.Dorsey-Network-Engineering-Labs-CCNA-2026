# Day 36 GNS3 Lab — Network Discovery: CDP and LLDP

Run `build_lab.py` to stand up the Day 36 topology (three routers, three switches, three PCs).

```bash
pip install requests
python build_lab.py
```

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2, R3) | Cisco router | VyOS |
| Switches (SW1-3) | Cisco 2960 | Open vSwitch |
| PCs (PC1-3) | Generic PC | Alpine Linux |

## Important limitation: Open vSwitch and CDP

Open vSwitch (GNS3's built-in switch image) does not speak CDP — CDP is a Cisco-proprietary protocol not implemented in OVS. This means Phase 1's switch-side CDP discovery (`show cdp neighbors` on SW1-3) cannot be reproduced exactly as written in the lab manual using GNS3's default switch image.

**Workaround options:**

1. Perform Phase 1's CDP discovery exercise on the VyOS routers only (R1-R3 do support CDP-like discovery via LLDP, see below) and treat the switches as pass-through devices you discover indirectly (a router's CDP/LLDP neighbor table will show the switch's uplink, even if the switch itself doesn't report back).
2. Substitute a Cisco IOSv switch image (if you have separate legal access to one) for SW1-3 if you want CDP to work identically to the lab manual on the switch side.
3. Use LLDP end-to-end instead of CDP for the GNS3 build — VyOS supports LLDP, and Alpine Linux can run `lldpd` (see below) — this actually mirrors the lab's own Phase 4 end-state better than trying to force CDP onto non-Cisco images.

## VyOS LLDP configuration

```
set service lldp interface eth0
set service lldp interface eth1
show lldp neighbors
```

VyOS's LLDP is a per-interface opt-in list, conceptually identical to the lab manual's "LLDP only on inter-device links" Phase 4 requirement — router interfaces facing other routers/switches go in the list, interfaces facing end hosts don't.

## Alpine Linux lldpd (for hands-on host-side LLDP practice)

```sh
apk add lldpd
rc-service lldpd start
lldpcli show neighbors
```

This lets PC1-3 participate in LLDP discovery if you want to extend the stretch goal (Section 12 of the lab manual) to see what a host-side LLDP neighbor entry looks like — useful context for understanding why access ports are deliberately excluded from LLDP in the lab's Phase 4 design.
