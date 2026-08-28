# Day 43 GNS3 Lab — FTP & TFTP: Cisco IOS File Transfer & Upgrade

Automation script to build the Day 43 file-transfer topology in GNS3 using free, open-source images.

## Image mapping

| Lab role | GNS3 template |
|---|---|
| R1, R2 (routers) | VyOS |
| SW1 (switch) | Open vSwitch (built into GNS3) |
| SRV1 (TFTP/FTP server) | Alpine Linux (install `tftp-hpa`, `vsftpd`) |

## Usage

1. Ensure GNS3 is running and reachable at `http://localhost:3080`.
2. `pip install requests`
3. `python build_lab.py`
4. The script checks for required templates before doing anything and will never download an image without an explicit `y` prompt.
5. Open the built project in the GNS3 GUI and start the nodes.

## What you'll configure once nodes are running

- SRV1 (Alpine): `apk add tftp-hpa vsftpd`, start both services, place a sample file to transfer
- R1/R2 (VyOS): address interfaces, configure the static route on R2 to reach SRV1's subnet
- Practice generic file transfer with each router's built-in tools against SRV1's TFTP and FTP services — note that VyOS doesn't use `copy tftp: flash:`/`boot system` syntax the way Cisco IOS does, so this build is best used to practice the *networking prerequisites* (addressing, routing, connectivity) and the TFTP/FTP protocol mechanics themselves, while the exact IOS `copy`/`boot system`/`delete flash:` command syntax should be practiced in Packet Tracer or a Cisco IOS-on-GNS3 setup if available

Refer to `../Day-43-Lab-Manual.md` for the full Cisco IOS command sequence and safe upgrade workflow.

## Re-running the script

Idempotent — existing project, nodes, and links are detected and skipped, safe to re-run.
