# Day 44 GNS3 Lab — Static NAT

Automation script to build the Day 44 Static NAT topology in GNS3 using free, open-source images.

## Image mapping

| Lab role | GNS3 template |
|---|---|
| R1 (NAT router), Internet Router | VyOS |
| PC1, PC2, PC3, Server | Alpine Linux |
| SW1 (switch, optional grouping for the 3 PCs) | Open vSwitch (built into GNS3) |

Note: the original lab has no distinct firewall/ASA device — R1 itself performs NAT — so no pfSense node is included in this build.

## Usage

1. Ensure GNS3 is running and reachable at `http://localhost:3080`.
2. `pip install requests`
3. `python build_lab.py`
4. The script checks for required templates before doing anything and will never download an image without an explicit `y` prompt.
5. Open the built project in the GNS3 GUI and start the nodes.

## What you'll configure once nodes are running

- PC1/PC2/PC3: static private addresses on `172.16.0.0/24`
- R1 (VyOS): inside/outside NAT rules using `set nat source rule` (VyOS's equivalent of `ip nat inside source static`)
- Test ICMP connectivity from each PC to the Server node before and after NAT is configured, matching the lab's before/after methodology

Refer to `../Day-44-Lab-Manual.md` for full NAT terminology (inside local/global, outside local/global) and the exact Cisco IOS command sequence.

## Re-running the script

Idempotent — existing project, nodes, and links are detected and skipped, safe to re-run.
