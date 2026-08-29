# GNS3 Lab — Day 38: DNS Configuration and Name Resolution

Automated build script for the Day 38 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| R1, Internet_Router | VyOS | R1 is the internal gateway; Internet_Router simulates the ISP edge |
| SW1 | Open vSwitch | Built into GNS3, no download needed |
| PC1, PC2, PC3 | Alpine Linux | Internal clients |
| DNS_Server | Alpine Linux | Runs `dnsmasq` as an open-source DNS server stand-in |
| Web_Server | Alpine Linux | Represents the external site being resolved and reached |

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

## Setting up the DNS server (Alpine + dnsmasq)

```sh
apk add dnsmasq
cat >> /etc/dnsmasq.conf << 'EOF'
address=/example-site.lab/203.0.113.20
EOF
rc-service dnsmasq start
```
Replace `example-site.lab` / `203.0.113.20` with your own test name/address (matching the manual's `youtube.com` example isn't possible against the real internet in an isolated GNS3 lab — pick any lab-local name to resolve, pointed at your Web_Server node's address).

## Applying the lab configuration after nodes are running

On R1 (VyOS):
```
configure
set interfaces ethernet eth0 address 192.168.0.254/24
set interfaces ethernet eth1 address 203.0.113.1/30
set protocols static route 0.0.0.0/0 next-hop 203.0.113.2
set system name-server 1.1.1.1
set system static-host-mapping host-name PC1 inet 192.168.0.1
set system static-host-mapping host-name PC2 inet 192.168.0.2
set system static-host-mapping host-name PC3 inet 192.168.0.3
commit
save
```

On each Alpine PC, set `/etc/resolv.conf` to point at the DNS_Server's address:
```sh
echo "nameserver 203.0.113.20" > /etc/resolv.conf
```

## Verifying

| IOS command | VyOS / Linux equivalent |
|---|---|
| `show ip route` | `show ip route` |
| `show hosts` | `show system static-host-mapping` |
| `ping PC1` | `ping PC1` (VyOS also checks its static-host-mapping table first) |
| `ping youtube.com` (client) | `ping example-site.lab` (Alpine client, via `dnsmasq`) |

## Caveats

- VyOS's `set system static-host-mapping` is the closest equivalent to IOS's `ip host`, and `set system name-server` is the closest equivalent to `ip name-server` — command families differ but the underlying local-table-vs-external-DNS distinction taught in the manual is identical.
- This is an isolated lab network with no real internet access — `youtube.com` won't resolve. Use `dnsmasq` on the DNS_Server node to serve any lab-local name you choose, pointed at the Web_Server node, to reproduce the same DNS-then-ICMP behavior the manual demonstrates.
