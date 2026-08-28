# GNS3 Lab — Day 06: Ethernet LAN Switching & MAC Address Tables

Automated build script for the Day 06 flat two-switch LAN using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Switches (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| PC1-PC4 | Alpine Linux | Lightweight full Linux |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. Open vSwitch is built-in; Alpine Linux template must be imported.

## Running the build

```bash
python build_lab.py
```

The script:
- Checks the GNS3 server is reachable.
- Checks all required templates exist, asking before any download.
- Creates the `Day-06-Ethernet-LAN-Switching` project (or reuses it).
- Creates 6 nodes and 5 links matching the companion manual's topology.
- Is safe to re-run.

## A note on MAC table inspection

Open vSwitch doesn't expose `show mac address-table` — instead, from the GNS3 host (or a console attached to the vSwitch), use `ovs-appctl fdb/show <bridge-name>` to view the learned forwarding database. To directly observe the ARP-flood-then-unicast pattern from the companion manual, run Wireshark or `tcpdump` against a link in the GNS3 GUI (right-click the link → Start capture) while pinging between two Alpine nodes.

## After the build

Open the `Day-06-Ethernet-LAN-Switching` project in the GNS3 GUI, start the nodes, assign IPs to the Alpine PCs per the companion manual's addressing plan, and generate traffic while capturing to replicate the lab.
