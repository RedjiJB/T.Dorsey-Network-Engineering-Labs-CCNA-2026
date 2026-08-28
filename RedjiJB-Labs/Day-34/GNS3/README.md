# Day 34 GNS3 Lab — Standard ACLs with OSPF-Routed Connectivity

Run `build_lab.py` to stand up the Day 34 topology (two routers, four subnets, OSPF, and per-subnet switches for the multi-host LANs).

```bash
pip install requests
python build_lab.py
```

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco router | VyOS |
| PCs/Servers (PC1-4, SRV1-2) | Generic PC/Server | Alpine Linux |
| LAN fan-out switches | Cisco 2960 (implied) | Open vSwitch |

## VyOS OSPF equivalents

| Concept | Cisco IOS | VyOS |
|---|---|---|
| Start OSPF, set router-id | `router ospf 1` / `router-id 1.1.1.1` | `set protocols ospf parameters router-id 1.1.1.1` |
| Advertise a network into area 0 | `network 172.16.1.0 0.0.0.255 area 0` | `set interfaces ethernet eth0 address 172.16.1.254/24` then `set protocols ospf area 0 network 172.16.1.0/24` |
| Passive interface | `passive-interface g0/0` | `set protocols ospf passive-interface eth0` |
| View neighbors | `show ip ospf neighbor` | `show ip ospf neighbor` |

## VyOS firewall rule-sets (ACL equivalent)

VyOS doesn't have numbered/named "ACLs" in the Cisco sense — it uses firewall rule-sets applied to an interface and direction, conceptually equivalent to `ip access-group <N> in/out`:

```
set firewall name TENANT2-BLOCK rule 10 action 'reject'
set firewall name TENANT2-BLOCK rule 10 source address '172.16.2.0/24'
set firewall name TENANT2-BLOCK rule 20 action 'accept'
set firewall name TENANT2-BLOCK default-action 'accept'
set interfaces ethernet eth1 firewall in name TENANT2-BLOCK
```

Note VyOS rule-sets need an explicit `default-action` — unlike Cisco IOS, there's no automatic implicit-deny unless you set `default-action 'drop'`, so read Section 8 (Common Mistakes) of the lab manual with this difference in mind if translating the lab's policies to VyOS syntax.

## Alpine Linux verification

```sh
ip addr show eth0        # confirm assigned address
ip route show             # confirm default gateway learned via OSPF-advertised subnet
ping 192.168.1.100        # test reachability per the lab's policy matrix
```
