# GNS3 Lab — Day 58: Wireless LANs & WLC Configuration

## There is no `build_lab.py` for this lab

Every other lab in this series ships an automated GNS3 build script. This one deliberately doesn't, and it's worth explaining why rather than shipping something that would quietly mislead you.

### Why GNS3 can't do this lab

GNS3 is a network-topology emulator built around real router/switch/firewall operating systems (VyOS, Open vSwitch, pfSense, IOS images you supply) talking to each other over emulated Ethernet links. It has **no open-source appliance that emulates**:

- Real 802.11 RF behavior (channels, signal strength, roaming, interference)
- A Cisco WLC's CAPWAP control-plane relationship with lightweight APs
- SSID broadcast and client association/authentication (WPA2-PSK handshake, etc.)

There is no free, GNS3-importable "virtual WLC" or "virtual lightweight AP" image that reproduces this lab's actual subject matter. Some commercial/proprietary options exist outside the GNS3 open-source ecosystem, but importing them isn't something this script can respect the "never download without asking" rule for, and they're not realistically available to most students working through this course. Rather than build a topology that *looks* like it's testing wireless concepts while silently testing nothing of the sort, this lab's GNS3 folder stays honest about the gap.

### What actually simulates this lab correctly: Packet Tracer

Cisco Packet Tracer **does** include working WLC and lightweight AP models with SSID configuration, WPA2-PSK, and simulated wireless client association — this is exactly why the original lab (`Labs/Day-58-Lab-Wireless-LANs.md`) and this expanded manual (`../Day-58-Lab-Manual.md`) are both written around Packet Tracer's WLC GUI. If your goal is to actually practice Sections 6–8 of the Lab Manual (dynamic interfaces, WLAN creation, WPA2-PSK, client association), Packet Tracer is the right tool for this specific lab — not GNS3.

### If you still want to practice the wired half in GNS3

The topology's *wired* portion — SW1 trunking VLANs 10 (management), 100 (Internal), and 200 (Guest) toward the WLC and both APs — is ordinary switching and is genuinely useful to practice, since real-world wireless troubleshooting so often turns out to be a wired VLAN/trunking problem in disguise (see the Lab Manual's Section 9 and Section 10). You can build that portion by hand in GNS3 using Open vSwitch for SW1 and VyOS or Alpine Linux standing in for the WLC/APs/PCs as generic Layer 3 endpoints on their respective VLANs — but be aware this only exercises the *wired* prerequisite infrastructure. It does not, and cannot, exercise anything about SSIDs, WPA2-PSK, or wireless client association, since none of the substitute images speak 802.11 or CAPWAP. If you build this manually, treat it strictly as "does my switch trunk carry all three VLANs correctly" practice, not as a wireless lab.

### Bottom line

Use Packet Tracer for this lab's actual wireless configuration (Sections 6–8 of the Lab Manual). If you want additional wired-switching repetition, a hand-built Open vSwitch trunk topology in GNS3 can reinforce that specific prerequisite skill, but it is not a substitute for the wireless portions this lab is actually about.
