# Day 33 GNS3 Lab — IPv6 Static Routes, SLAAC, and Backup Paths

Run `build_lab.py` to stand up the Day 33 topology (three routers, primary direct link plus backup path through R2).

```bash
pip install requests
python build_lab.py
```

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2, R3) | Cisco router | VyOS |
| Switches (SW1, SW2) | Cisco 2960 | Open vSwitch |
| PCs (PC1, PC2) | Generic PC | Alpine Linux |

## VyOS SLAAC and floating static route equivalents

| Concept | Cisco IOS | VyOS |
|---|---|---|
| Enable RA/SLAAC on a LAN interface | Automatic once `ipv6 address` + `ipv6 enable` are set | `set interfaces ethernet eth0 address 2001:db8:0:1::1/64` (VyOS sends RAs automatically for any configured IPv6 prefix unless RA is explicitly disabled with `set interfaces ethernet eth0 ipv6 router-advert send-advert false`) |
| Primary static route (AD 1) | `ipv6 route 2001:db8:0:3::/64 2001:db8:0:13::2` | `set protocols static route6 2001:db8:0:3::/64 next-hop 2001:db8:0:13::2` |
| Backup static route (higher AD) | `ipv6 route 2001:db8:0:3::/64 FE80::... 100` | `set protocols static route6 2001:db8:0:3::/64 next-hop fe80::... interface eth1 distance 100` |
| View routes | `show ipv6 route` / `show ipv6 route static` | `show ipv6 route` |

## Alpine Linux SLAAC verification

Alpine's networking stack accepts Router Advertisements automatically when IPv6 forwarding/autoconf is enabled on the interface:

```sh
echo 1 > /proc/sys/net/ipv6/conf/eth0/autoconf
echo 0 > /proc/sys/net/ipv6/conf/eth0/disable_ipv6
ip -6 addr show eth0     # confirm the SLAAC-derived global address appeared automatically
```

No manual `ip -6 addr add` is needed for the SLAAC-based PCs in this lab — that's the entire point of the exercise.

## Testing backup-path failover in GNS3

Shut down the R1-R3 direct link in the GNS3 GUI (right-click the link → Delete, or stop forwarding on the interface) and re-run a ping between PC1 and PC2. The static route with the higher administrative distance should take over automatically — this is the same behavior demonstrated in Section 12 (Stretch Goal) of the lab manual.
