# Day 42 GNS3 Lab — SSH: Secure Remote Access & Management

Automation script to build the Day 42 SSH-hardening topology in GNS3 using free, open-source images.

## Image mapping

| Lab role | GNS3 template |
|---|---|
| R1, R2 (routers) | VyOS |
| SW1, SW2 (switches — SW2 is the device being hardened) | Open vSwitch (built into GNS3) |
| PC1 (SSH client), Laptop1 (console-equivalent) | Alpine Linux |

## Usage

1. Ensure GNS3 is running and reachable at `http://localhost:3080`.
2. `pip install requests`
3. `python build_lab.py`
4. The script checks for required templates before doing anything and will never download an image without an explicit `y` prompt.
5. Open the built project in the GNS3 GUI and start the nodes.

## What you'll configure once nodes are running

- R1/R2 (VyOS): static routes (or OSPF) so PC1's LAN and SW2's LAN can reach each other
- SW2: since Open vSwitch nodes are pure L2, model the "management SVI" concept using a VyOS or Linux bridge host if you want literal `ip default-gateway`/ACL syntax practice — otherwise treat this build as the transport topology and do the actual SSH-hardening command practice against the VyOS routers' own `set service ssh` and firewall rule sets, which map conceptually to IOS's `crypto key generate rsa` / `access-class` / `transport input ssh`
- PC1 (Alpine): `apk add openssh-client`, then `ssh jeremy@<management-ip>`

Refer to `../Day-42-Lab-Manual.md` for full Cisco IOS command syntax and the ACL/access-class walkthrough.

## Re-running the script

Idempotent — existing project, nodes, and links are detected and skipped, safe to re-run.
