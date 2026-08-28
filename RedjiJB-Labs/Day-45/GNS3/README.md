# Day 45 GNS3 Lab — Dynamic NAT & PAT

Automation script to build the Day 45 Dynamic NAT / PAT topology in GNS3 using free, open-source images.

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

- Phase 1 (Dynamic NAT): a 2-address pool-based source NAT rule on R1, tested against all 3 PCs to observe exhaustion on the third
- Phase 2 (PAT): remove the pool-based rule, replace it with a `masquerade` rule (VyOS's PAT/NAT-Overload equivalent) using R1's own outside interface address, re-test all 3 PCs

Refer to `../Day-45-Lab-Manual.md` for the full Cisco IOS command sequence, NAT terminology reference, and the Dynamic NAT vs. PAT comparison.

## Re-running the script

Idempotent — existing project, nodes, and links are detected and skipped, safe to re-run.
