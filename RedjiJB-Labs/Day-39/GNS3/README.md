# Day 39 GNS3 Lab — DHCP Server, DHCP Client, and DHCP Relay

This folder contains an automation script that builds the Day 39 topology in GNS3 using free, open-source images so you can practice the lab hands-on without Cisco licensing.

## Image mapping

| Lab role | GNS3 template |
|---|---|
| R1, R2 (routers) | VyOS |
| SW1, SW2 (switches) | Open vSwitch (built into GNS3) |
| PC1, PC2 (end hosts) | Alpine Linux |

## Usage

1. Make sure GNS3 is running locally and its server API is reachable at `http://localhost:3080`.
2. Install dependencies: `pip install requests`
3. Run: `python build_lab.py`
4. The script checks your GNS3 install for the required templates first. It will **never download an image without asking** — if something's missing, it lists exactly what and prompts for a `y/N` before attempting anything.
5. Once the topology is built, open the project in the GNS3 GUI and start the nodes.

## What you'll configure once nodes are running

- R2: DHCP server with three scopes (two LAN pools + the transit link pool)
- R1: DHCP client on its WAN-facing interface, DHCP relay on its LAN-facing interface
- PC1 / PC2: DHCP clients (`udhcpc` on Alpine)

Refer to `../Day-39-Lab-Manual.md` for full command syntax (note: VyOS syntax differs from Cisco IOS — translate the `dhcp-server`, `dhcp-client`, and `dhcp-relay` sections of VyOS's `set service dhcp-server` / `set interfaces ethernet ethX address dhcp` / `set service dhcp-relay` command trees).

## Re-running the script

The script is idempotent: existing projects, nodes, and links are detected and skipped rather than duplicated, so it's safe to re-run after a partial build.
