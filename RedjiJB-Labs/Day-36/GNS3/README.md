# Day 36 GNS3 Lab — CDP & LLDP: Network Discovery Protocols

Run `build_lab.py` to stand up the Day 36 topology: three VyOS routers in a
triangle, each with its own Open vSwitch access switch and Alpine Linux PC.

```bash
pip install requests
python build_lab.py
```

## Device role mapping

| Lab role | Packet Tracer device | GNS3 image |
|---|---|---|
| Routers (R1, R2, R3) | Cisco router | VyOS |
| Access switches (SW1-3) | Cisco switch | Open vSwitch |
| PCs (PC1-3) | Generic PC | Alpine Linux |

## Important: CDP has no VyOS equivalent

CDP is Cisco-proprietary — VyOS (and Open vSwitch) do not implement it. There
is no meaningful way to practice Phases 1-3 of the lab manual (CDP discovery
and disable) against this GNS3 topology. Practice those phases in Packet
Tracer or a Cisco-image-based GNS3 build if you have access to one.

This topology exists to practice **Phase 4 (LLDP)** hands-on, since LLDP is
an open standard VyOS supports natively.

## VyOS LLDP equivalents

| Concept | Cisco IOS | VyOS |
|---|---|---|
| Enable LLDP globally | `lldp run` | `set service lldp` |
| Enable Tx/Rx on all interfaces | `interface range ...` + `lldp transmit` / `lldp receive` | `set service lldp interface all` |
| Enable Tx/Rx on one interface only | `interface g0/2` + `lldp transmit` / `lldp receive` | `set service lldp interface eth1` |
| Disable on a specific interface | `no lldp transmit` / `no lldp receive` | `delete service lldp interface eth1` |
| View neighbors | `show lldp neighbors` | `show lldp neighbors` |
| View global status | `show lldp` | `show lldp` |

Example — enabling LLDP on R1 with the same "inter-device links only" scoping
as the lab manual's Phase 4 (assume eth0/eth1 face R2/R3, eth2 faces SW1):

```
set service lldp interface eth0
set service lldp interface eth1
set service lldp interface eth2
commit
```

On each Open vSwitch access switch, do **not** enable LLDP relay/forwarding
toward the PC-facing port — leave that port's LLDP behavior untouched, the
same "never advertise to an access port" principle from the lab manual.

## Alpine Linux verification

Alpine doesn't run LLDP by default. Install `lldpd` to observe advertisements
from the routers for verification purposes:

```sh
apk add lldpd
rc-service lldpd start
lldpcli show neighbors
```
