# GNS3 Lab — Day 50: DHCP Snooping

Automated build script for the Day 50 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Router (R1) | VyOS | DHCP server role |
| Switches (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| PC1 | Alpine Linux | DHCP client |

## Prerequisites

1. GNS3 installed and running, local server reachable at `http://localhost:3080`.
2. Python 3.8+ with `requests`: `pip install requests`
3. Template imported for VyOS. Open vSwitch and Alpine are otherwise covered.

## Running the build

```bash
python build_lab.py
```

Checks the server, checks templates, creates the `Day-50-DHCP-Snooping` project, creates 4 nodes and 3 links. Safe to re-run.

## VyOS as a DHCP server

VyOS's DHCP server config differs from IOS's `ip dhcp pool` syntax:

```text
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 range 0 start 192.168.1.10
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 range 0 stop 192.168.1.254
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 default-router 192.168.1.1
```

## Important limitation: Open vSwitch has no DHCP Snooping equivalent

GNS3's built-in Open vSwitch does not implement Cisco IOS's `ip dhcp snooping` feature (trust boundaries, the binding table, or Option 82 handling). There is no open-source GNS3 switch appliance that reproduces this 1:1.

To approximate DHCP Snooping concepts for hands-on practice in this GNS3 build:

- Run `isc-dhcp-server` (or `dnsmasq`) on the R1 VyOS node or a dedicated Alpine node, and manually inspect its lease log (`/var/lib/dhcp/dhcpd.leases` or equivalent) as a stand-in for the switch-maintained binding table.
- To simulate a rogue-DHCP-server attack for observation purposes, stand up a second DHCP server on an Alpine node attached to a client-facing segment and observe which server's Offer a test client accepts — since OVS won't block it, this demonstrates *why* DHCP Snooping is needed rather than demonstrating the enforcement itself.

For graded/authoritative DHCP Snooping practice (trust configuration, Option 82 behavior, binding table verification), use Packet Tracer or a physical/virtual Cisco IOS switch image, which this GNS3 build does not substitute for.
