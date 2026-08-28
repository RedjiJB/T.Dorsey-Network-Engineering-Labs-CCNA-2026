# GNS3 Lab — Day 03: OSI Model & DHCP Packet Analysis

Automated build script for the Day 03 DHCP client/server topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Routers (R1, R2) | VyOS | Open-source, Cisco-like CLI; supports DHCP relay |
| Switches (SW1, SW2) | Open vSwitch | Built into GNS3, no download needed |
| PC1 / SRV1 | Alpine Linux | PC1 as DHCP client, SRV1 running `udhcpd` as the DHCP server |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. Templates imported into GNS3 for VyOS and Alpine Linux. Open vSwitch is built-in.

## Running the build

```bash
python build_lab.py
```

The script:
- Checks the GNS3 server is reachable.
- Checks all required templates exist, asking before any download.
- Creates the `Day-03-OSI-Model-DHCP` project (or reuses it).
- Creates 6 nodes and 5 links matching the companion manual's topology.
- Is safe to re-run.

## After the build

1. On SRV1 (Alpine), install and configure `udhcpd` to serve the client-side subnet.
2. On R1 (VyOS), configure DHCP relay pointing at SRV1's IP, on the interface facing PC1.
3. Right-click the R1–R2 link in the GNS3 GUI and start a Wireshark capture before bringing PC1's interface up, so you capture the full DORA exchange, matching Section 7 of the companion manual.
4. Follow the [Configuration Tasks](../Day-03-Lab-Manual.md#6-configuration-tasks) section for the full walkthrough (commands shown there are IOS-style; translate to VyOS `set`/`commit` syntax as needed).
