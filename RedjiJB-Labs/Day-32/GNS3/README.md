# Day 32 GNS3 Lab — IPv6 EUI-64, Link-Local, and Static Routes

Run `build_lab.py` to stand up the Day 32 topology (two routers, two LANs, link-local-only WAN link).

```bash
pip install requests
python build_lab.py
```

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco router | VyOS |
| Switches (SW1, SW2) | Cisco 2960 | Open vSwitch |
| PCs (PC1, PC2) | Generic PC | Alpine Linux |

## Finding a VyOS interface's real MAC address

Since GNS3-assigned MACs will differ from this lab's example addresses, redo the EUI-64 hand-derivation against the real values:

```
show interfaces ethernet eth0
```

Look for the `HWaddr` / link/ether field, then apply the same split → insert FFFE → flip bit 7 process from Section 4.2 of the lab manual.

## VyOS EUI-64 and static route equivalents

| Concept | Cisco IOS | VyOS |
|---|---|---|
| Assign a hand-derived EUI-64 global address | `ipv6 address 2001:db8::230:f2ff:fe36:4502/64` | `set interfaces ethernet eth1 address 2001:db8::230:f2ff:fe36:4502/64` |
| Auto-generate EUI-64 from MAC | `ipv6 address 2001:db8::/64 eui-64` | `set interfaces ethernet eth1 address 2001:db8::/64` (VyOS/Linux uses SLAAC-style EUI-64 automatically for the link-local address; global EUI-64 auto-assignment needs `ipv6 address eui64` under some VyOS versions — check `set interfaces ethernet eth1 ipv6 address eui64` on your image) |
| Link-local only interface | `ipv6 enable` (no `ipv6 address`) | Link-local is automatic on any Linux interface with IPv6 enabled — no explicit command needed |
| Static route via link-local next-hop | `ipv6 route 2001:db8:0:1::/64 FE80::201:63ff:fe80:b800` | `set protocols static route6 2001:db8:0:1::/64 next-hop fe80::201:63ff:fe80:b800 interface eth0` (VyOS requires the outgoing interface be specified alongside a link-local next-hop, since link-local addresses aren't globally unique) |
| View interfaces / addresses | `show ipv6 interface brief` | `show interfaces` |
| View IPv6 routes | `show ipv6 route` | `show ipv6 route` |

## Alpine Linux verification

```sh
ip -6 addr show eth0          # confirm global + link-local addresses
ip -6 route show               # confirm default route via the router's global address
ping6 2001:db8:0:1::2          # end-to-end test to the far LAN's PC
```

The EUI-64 math, link-local scope rules, and static-route-with-link-local-next-hop concept are identical to the Cisco IOS lab manual — only the command syntax differs.
