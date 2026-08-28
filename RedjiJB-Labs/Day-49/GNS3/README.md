# GNS3 Lab — Day 49: Port Security

Automated build script for the Day 49 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Switches (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| PCs / hosts | Alpine Linux | Lightweight full Linux |

## Prerequisites

1. GNS3 installed and running, local server reachable at `http://localhost:3080`.
2. Python 3.8+ with `requests`: `pip install requests`
3. No image downloads needed beyond Alpine Linux (Open vSwitch is built-in).

## Running the build

```bash
python build_lab.py
```

Checks the server, checks templates, creates the `Day-49-Port-Security` project, creates 7 nodes and 6 links. Safe to re-run.

## Important limitation: Open vSwitch has no port-security equivalent

GNS3's built-in Open vSwitch node is a standard software switch and does **not** implement Cisco IOS's `switchport port-security` feature set (max MAC count, violation modes, sticky learning, aging). There is no drop-in open-source GNS3 switch appliance that replicates this behavior exactly.

This topology is provided so you can practice cabling, addressing, and observing MAC learning behavior (`ovs-appctl fdb/show <bridge>` from the GNS3 host/VM shell shows the OVS MAC table, conceptually similar to `show mac address-table`). To *approximate* the port-security violation behavior for hands-on practice:

- On the Alpine Linux hosts, use `arptables`/`ebtables` to filter frames by source MAC address on a given interface, simulating a "maximum allowed MAC" policy at the host level rather than the switch level.
- To simulate `violation shutdown`, write a small script that brings the OVS port down (`ovs-vsctl` on the GNS3 host) when an unexpected MAC is observed in `fdb/show` output.

These are approximations for lab purposes only — they do not reproduce the ASIC-level, line-rate enforcement a real Cisco switch performs. For graded/authoritative port-security practice, use Packet Tracer or a physical/virtual Cisco IOS switch image, which this GNS3 build does not substitute for.
