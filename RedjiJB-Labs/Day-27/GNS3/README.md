# GNS3 Lab — Day 27: OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

This folder contains an automation script that builds the Day 27 topology (ISPR1, R1, R2, R3, R4, SW1, PC1) in GNS3 using free/open-source images. It is the same physical topology as Day 26 — this lab layers `auto-cost reference-bandwidth` tuning and OSPF Hello-packet study on top of it, so it gets its own project rather than reusing Day 26's live project.

## Requirements

- GNS3 Desktop or GNS3 VM running, with the server API reachable at `http://localhost:3080` (default)
- Python 3.8+ with `requests` installed: `pip install requests`

## Images Used

| Role | Image | Notes |
|---|---|---|
| ISPR1, R1, R2, R3, R4 | VyOS | Open-source, Cisco-like CLI. Supports OSPF area configuration and per-interface cost overrides; VyOS does not have a single `auto-cost reference-bandwidth` command identical to IOS — see caveat below. |
| SW1 | Open vSwitch | Built into GNS3, no download needed. |
| PC1 | Alpine Linux | Lightweight Linux end host. |

## Usage

```bash
python build_lab.py
```

The script:
- Checks the GNS3 server is reachable.
- Checks all required templates exist. If any are missing, it lists them and **asks before attempting any download** — nothing is downloaded silently.
- Creates the `Day-27-OSPF-Reference-Bandwidth` project (or reuses it if it already exists).
- Creates all 7 nodes and 7 links matching the Day 26/27 topology.
- Is safe to re-run — it skips nodes/links that already exist.

## A note on VyOS and reference bandwidth

VyOS's OSPF implementation (built on FRRouting) does not expose an identical single knob to IOS's `auto-cost reference-bandwidth <Mbps>`. In FRR/VyOS, the equivalent behavior is achieved with `set protocols ospf auto-cost reference-bandwidth <Mbps>` under `ospfd`, which works the same conceptually (recalculates every interface's advertised cost using the new reference value) — but always double-check the exact syntax against the VyOS version you have imported, since it has shifted across releases. The **cost math itself** (Section 4.1 of the Lab Manual) is protocol-standard and identical regardless of vendor.

## After Building

Open the `Day-27-OSPF-Reference-Bandwidth` project in the GNS3 GUI, start all nodes, and console into each router to follow the reference-bandwidth tuning and Hello-packet walkthrough in [`../Day-27-Lab-Manual.md`](../Day-27-Lab-Manual.md). Translate the IOS commands to VyOS `set`/`commit` syntax, or substitute a Cisco IOSv template if you have one imported for exact CLI parity with the manual's `auto-cost reference-bandwidth 10000` and `show ip ospf interface` output.

If you already have Day 26's `Day-26-OSPF-ASBR` project built and configured, you can also just apply this lab's reference-bandwidth change directly on top of that running project instead of building a fresh one — the topology is identical.
