# Day 40 GNS3 Lab — SNMP Fundamentals, MIB Queries, and Remote Device Management

Automation script to build the Day 40 SNMP agent/manager topology in GNS3 using free, open-source images.

## Image mapping

| Lab role | GNS3 template |
|---|---|
| R1 (router / SNMP agent) | VyOS |
| SW1 (switch) | Open vSwitch (built into GNS3) |
| PC1 (SNMP manager) | Alpine Linux |

## Usage

1. Ensure GNS3 is running and reachable at `http://localhost:3080`.
2. `pip install requests`
3. `python build_lab.py`
4. The script checks for required templates before doing anything and will never download an image without an explicit `y` prompt.
5. Open the built project in the GNS3 GUI and start the nodes.

## What you'll configure once nodes are running

- R1 (VyOS): `set service snmp community Cisco1 authorization ro`, `set service snmp community Cisco2 authorization rw`
- PC1 (Alpine): `apk add net-snmp-tools`, then use `snmpget`, `snmpwalk`, and `snmpset` against R1's address
- Query the same OIDs as the Cisco IOS version of this lab (`sysName`, `sysUpTime`, `ifNumber`, `ifDescr`) — VyOS exposes standard MIB-II objects the same way IOS does

Refer to `../Day-40-Lab-Manual.md` for full OID reference and expected output.

## Re-running the script

Idempotent — existing project, nodes, and links are detected and skipped, safe to re-run.
