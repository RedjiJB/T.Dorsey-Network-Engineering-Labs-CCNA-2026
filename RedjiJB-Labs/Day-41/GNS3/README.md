# Day 41 GNS3 Lab — Syslog Configuration, Logging Destinations, and Remote Device Monitoring

Automation script to build the Day 41 Syslog topology in GNS3 using free, open-source images.

## Image mapping

| Lab role | GNS3 template |
|---|---|
| R1 (router) | VyOS |
| SW1 (switch) | Open vSwitch (built into GNS3) |
| PC1 (Telnet client), PC2 (console workstation) | Alpine Linux |
| SRV1 (Syslog server) | Alpine Linux (install `rsyslog`) |

## Usage

1. Ensure GNS3 is running and reachable at `http://localhost:3080`.
2. `pip install requests`
3. `python build_lab.py`
4. The script checks for required templates before doing anything and will never download an image without an explicit `y` prompt.
5. Open the built project in the GNS3 GUI and start the nodes.

## What you'll configure once nodes are running

- R1 (VyOS): `set system syslog host <SRV1-ip> facility all level debug`, plus local buffer equivalents
- SRV1 (Alpine): `apk add rsyslog`, enable UDP 514 listening, `rc-service rsyslog start`
- PC1: Telnet or SSH into R1 and test that `terminal monitor` (or VyOS equivalent) is required to see live messages
- Trigger interface up/down events on R1 and confirm they arrive on SRV1 in `/var/log/messages` (or the configured rsyslog target)

Refer to `../Day-41-Lab-Manual.md` for full severity-level reference and troubleshooting steps.

## Re-running the script

Idempotent — existing project, nodes, and links are detected and skipped, safe to re-run.
