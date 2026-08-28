# Day 31 GNS3 Lab — IPv6 Dual-Stack Configuration

Run `build_lab.py` to automatically stand up the Day 31 topology in GNS3 (one router, three LANs, three PCs).

```bash
pip install requests
python build_lab.py
```

The script checks for a running GNS3 server, verifies the required templates (VyOS, Open vSwitch, Alpine Linux) are already imported, creates the project, places the nodes, and wires the links. It never downloads an image without asking first.

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Router (R1) | Cisco router | VyOS |
| Switches (SW1-SW3) | Cisco 2960 | Open vSwitch |
| PCs (PC1-PC3) | Generic PC | Alpine Linux |

## VyOS IPv6 command equivalents

Cisco IOS and VyOS use different syntax families for the same IPv6 concepts. Once the topology is built, use this translation table to reproduce the lab manual's configuration on VyOS:

| Concept | Cisco IOS | VyOS |
|---|---|---|
| Enter config mode | `configure terminal` | `configure` |
| Assign IPv6 to interface | `interface g0/0` / `ipv6 address 2001:db8:0:1::1/64` | `set interfaces ethernet eth0 address 2001:db8:0:1::1/64` |
| Enable IPv6 routing | `ipv6 unicast-routing` | On by default — VyOS (Linux-based) forwards IPv6 automatically once `net.ipv6.conf.all.forwarding=1`; no separate command needed |
| View interfaces | `show ipv6 interface brief` | `show interfaces` |
| View routes | `show ipv6 route` | `show ipv6 route` |
| Save config | `copy running-config startup-config` | `commit` then `save` |

## Alpine Linux dual-stack host configuration

```sh
# IPv4
ip addr add 192.168.1.2/24 dev eth0
ip route add default via 192.168.1.1

# IPv6
ip -6 addr add 2001:db8:0:1::2/64 dev eth0
ip -6 route add default via 2001:db8:0:1::1
```

Verify with `ip -6 addr show` and `ping6 2001:db8:0:2::2`.

Because the underlying protocol concepts (dual-stack, global vs link-local scope, /64 LAN sizing) are identical across vendors, everything in Sections 4, 7, and 8 of the lab manual transfers directly — only the command syntax changes.
