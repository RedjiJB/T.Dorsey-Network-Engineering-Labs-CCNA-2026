# GNS3 Lab — Day 47: QoS, DSCP Marking & Traffic Classification

Automated build script for the Day 47 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| Routers (R1, R2) | VyOS | Open-source, Cisco-like CLI |
| Switch (SW1) | Open vSwitch | Built into GNS3, no download needed |
| PC1 / SRV1 | Alpine Linux | Lightweight full Linux |

## Prerequisites

1. GNS3 installed and running, local server reachable at `http://localhost:3080`.
2. Python 3.8+ with `requests`: `pip install requests`
3. Templates imported for VyOS and Alpine Linux. Open vSwitch is built-in.

## Running the build

```bash
python build_lab.py
```

Checks the server, checks templates (asks before any download), creates the `Day-47-QoS` project, creates 5 nodes and 4 links. Safe to re-run.

## VyOS QoS vs. Cisco IOS QoS — concept mapping

The lab manual's `class-map` / `policy-map` / `service-policy` syntax is Cisco IOS-specific and does not exist on VyOS. VyOS instead uses `traffic-policy`:

```text
set traffic-policy shaper QOS-OUT bandwidth 100mbit
set traffic-policy shaper QOS-OUT class 10 match HTTPS
set traffic-policy shaper QOS-OUT class 10 bandwidth 10%
set traffic-policy shaper QOS-OUT class 10 priority 1
set interfaces ethernet eth1 traffic-policy out QOS-OUT
```

The underlying concepts still map 1:1:

| Cisco IOS | VyOS | Concept |
|---|---|---|
| `class-map` | `traffic-policy shaper <name> class <id> match` | Classification |
| `policy-map ... set ip dscp` | `traffic-policy shaper <name> class <id> mark dscp` | Marking |
| `priority percent` | `traffic-policy shaper <name> class <id> priority` | Priority queue |
| `bandwidth percent` | `traffic-policy shaper <name> class <id> bandwidth` | Bandwidth guarantee |
| `service-policy output` | `set interfaces ... traffic-policy out` | Applying the policy |

Use this table to translate the manual's IOS walkthrough onto the VyOS routers in this GNS3 build.
