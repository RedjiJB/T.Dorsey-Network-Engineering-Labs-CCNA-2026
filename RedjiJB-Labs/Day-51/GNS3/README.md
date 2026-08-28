# GNS3 Lab — Day 51: Dynamic ARP Inspection

## No separate build script for this lab

Day 51 reuses the **exact same topology** as Day 50 (R1 DHCP server, SW1, SW2, PC1) — DAI is configured on top of an already-built DHCP Snooping deployment, not a new physical/logical topology. There is nothing distinct to build here.

To work this lab in GNS3:

1. Run [`../../Day-50/GNS3/build_lab.py`](../../Day-50/GNS3/build_lab.py) to build (or reuse, if already built) the `Day-50-DHCP-Snooping` project.
2. Follow `Day-51-Lab-Manual.md`'s configuration steps on top of that same set of nodes.

## Same limitation as Day 50 applies

Open vSwitch (GNS3's built-in switch, used for SW1/SW2) does not implement Cisco IOS's `ip arp inspection` any more than it implements `ip dhcp snooping`. See [`../../Day-50/GNS3/README.md`](../../Day-50/GNS3/README.md) for the full explanation and the Linux-based approximation approach (arptables/static ARP entries on the Alpine hosts) for conceptual, non-enforced practice only. For graded/authoritative DAI practice, use Packet Tracer or a physical/virtual Cisco IOS switch image.
