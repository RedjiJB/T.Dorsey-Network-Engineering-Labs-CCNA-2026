# GNS3 Lab — Day 46: Voice VLANs & Router-on-a-Stick

Automated build script for the Day 46 topology using free, open-source images.

## Images used

| Role | Image | Notes |
|---|---|---|
| SW1 | Open vSwitch | Built into GNS3, no download needed |
| R1 | VyOS | Provides Router-on-a-Stick (dot1q subinterfaces) |
| PC1, PC2, PH1, PH2 | Alpine Linux | PC1/PC2 = untagged data; PH1/PH2 simulate IP phones via a tagged subinterface (see below) |

## Prerequisites

1. GNS3 installed and running, with the local server reachable at `http://localhost:3080` (default).
2. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```
3. VyOS and Alpine Linux templates imported into GNS3 (the script will ask before attempting any download). Open vSwitch ships with GNS3.

## Running the build

```bash
python build_lab.py
```

The script checks the GNS3 server is reachable, checks all required templates exist (asking before downloading anything missing), then creates the project, nodes, and links — safe to re-run, it skips anything already created.

## Simulating a Cisco IP phone with Alpine Linux

GNS3's free image set has no native Cisco IP phone appliance. PH1 and PH2 are Alpine Linux hosts configured to tag their own traffic 802.1Q, approximating what a real IP phone does before its frames reach the switch:

```sh
apk add vlan
modprobe 8021q
ip link add link eth0 name eth0.20 type vlan id 20
ip addr add 192.168.20.10/24 dev eth0.20
ip link set eth0.20 up
```

PC1/PC2 stay plain (untagged, `eth0` directly) to represent data traffic.

## Applying the lab configuration after nodes are running

On SW1 (Open vSwitch, via its console/CLI):
```
ovs-vsctl set port <PC-port> tag=10
ovs-vsctl set port <PH-port> tag=20
```
(Open vSwitch doesn't natively replicate `switchport voice vlan`'s CDP-based signaling — the tagging behavior is approximated at the host, per above.)

On R1 (VyOS), the closest equivalent to Cisco ROAS subinterfaces:
```
set interfaces ethernet eth0 vif 10 address 192.168.10.1/24
set interfaces ethernet eth0 vif 20 address 192.168.20.1/24
commit
```

## Caveats

- Open vSwitch's `voice vlan` behavior and CDP-based auto-provisioning are Cisco-specific IOS features with no direct GNS3 open-source equivalent — this build demonstrates the *tagging mechanics* (untagged data vs. 802.1Q-tagged voice) rather than replicating Cisco phone auto-configuration.
- VyOS syntax differs from IOS (`vif` vs. `encapsulation dot1q` + subinterface), but the underlying concept — one physical interface, multiple logical Layer 3 gateways keyed by VLAN tag — is identical.
