# Day 35 GNS3 Lab — Extended ACLs: Destination and Port-Based Filtering

Run `build_lab.py` to stand up the Day 35 topology. It is identical to
[Day 34's topology](../../Day-34/GNS3/build_lab.py) (two routers, four subnets,
OSPF, per-subnet switches) — this lab is a **policy upgrade** (standard ACLs →
extended ACLs), not a new network build, so no new devices or links are
introduced.

```bash
pip install requests
python build_lab.py
```

If you already built Day 34's project in GNS3, you can reuse it directly
instead of running this script — it exists so Day 34 and Day 35 can also be
worked as independent projects side by side.

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2) | Cisco router | VyOS |
| PCs/Servers (PC1-4, SRV1-2) | Generic PC/Server | Alpine Linux |
| LAN fan-out switches | Cisco 2960 (implied) | Open vSwitch |

## VyOS firewall rule-sets — extended ACL equivalents

VyOS firewall rule-sets natively support protocol and destination-port match
criteria, so translating this lab's three extended ACL policies is direct:

**Policy A — LAN2 blocked from PC1 (any protocol):**
```
set firewall name BLOCK-PC1 rule 10 action 'reject'
set firewall name BLOCK-PC1 rule 10 source address '172.16.2.0/24'
set firewall name BLOCK-PC1 rule 10 destination address '172.16.1.1/32'
set firewall name BLOCK-PC1 rule 20 action 'accept'
set firewall name BLOCK-PC1 default-action 'accept'
set interfaces ethernet eth0 firewall in name BLOCK-PC1
```

**Policy B — LAN1 blocked from SRV1's DNS (UDP/53) only:**
```
set firewall name BLOCK-DNS-SRV1 rule 10 action 'reject'
set firewall name BLOCK-DNS-SRV1 rule 10 protocol 'udp'
set firewall name BLOCK-DNS-SRV1 rule 10 source address '172.16.1.0/24'
set firewall name BLOCK-DNS-SRV1 rule 10 destination address '192.168.1.100/32'
set firewall name BLOCK-DNS-SRV1 rule 10 destination port '53'
set firewall name BLOCK-DNS-SRV1 rule 20 action 'accept'
set firewall name BLOCK-DNS-SRV1 default-action 'accept'
```

**Policy C — LAN2 blocked from SRV2's HTTP/HTTPS only:**
```
set firewall name BLOCK-WEB-SRV2 rule 10 action 'reject'
set firewall name BLOCK-WEB-SRV2 rule 10 protocol 'tcp'
set firewall name BLOCK-WEB-SRV2 rule 10 source address '172.16.2.0/24'
set firewall name BLOCK-WEB-SRV2 rule 10 destination address '192.168.2.100/32'
set firewall name BLOCK-WEB-SRV2 rule 10 destination port '80,443'
set firewall name BLOCK-WEB-SRV2 rule 20 action 'accept'
set firewall name BLOCK-WEB-SRV2 default-action 'accept'
set interfaces ethernet eth1 firewall in name BLOCK-WEB-SRV2
```

Note VyOS's `destination port` field accepts a comma-separated list
(`'80,443'`) in one rule — the Cisco IOS equivalent requires two separate
`deny` lines (see the lab manual, Section 6.3) because standard extended ACL
syntax has no multi-port list operator, only `eq`, `range`, `gt`/`lt`/`neq`.
Also remember VyOS needs an explicit `default-action` (no automatic
implicit-deny), unlike Cisco IOS's implicit deny at the end of every ACL.

## Alpine Linux verification

```sh
ping -c 4 172.16.1.1        # Policy A check (from a LAN2 host)
ping -c 4 192.168.1.100      # Policy B check — ICMP should still succeed
nslookup somehost 192.168.1.100   # Policy B check — DNS query should fail/timeout
wget -T 3 http://192.168.2.100    # Policy C check — should fail from LAN2
```
