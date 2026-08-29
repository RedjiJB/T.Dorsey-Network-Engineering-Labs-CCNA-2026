# Day 58 Lab Manual — Wireless LANs & WLC Configuration

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure a Cisco Wireless LAN Controller (WLC) to manage lightweight access points, create VLAN-mapped dynamic interfaces, stand up two SSIDs (Internal, Guest) secured with WPA2-PSK, and associate wireless clients — while understanding exactly which parts of this architecture are wireless and which are still ordinary wired switching underneath. |
| **Exam Relevance** | CCNA 200-301 — Domain 2 (Network Access): "describe wireless principles," "explain the role of access points," "describe WLC," "configure WLAN using WLC GUI (WPA2 PSK)" are all explicit exam blueprint items. This is the only lab in the course where the exam blueprint names a specific GUI-based configuration task rather than CLI. |
| **Prerequisites** | VLANs and trunking (Days 8–10), basic switch access-port/trunk-port configuration. No prior wireless-specific knowledge assumed. |
| **Time Estimate** | 1.5 hours. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner–Intermediate) — the GUI steps are mostly point-and-click, but the SSID → WLAN → Dynamic Interface → VLAN → Subnet chain is a genuinely new mental model this lab exists to build. |

---

## 1. Lab Overview + Learning Objectives

Unlike almost every other lab in this course, wireless networking is configured primarily through a **GUI**, not a CLI — Cisco WLCs are managed via HTTPS web interface for exactly this reason: wireless configuration (RF channels, power levels, security policies, SSIDs) doesn't map cleanly onto a line-by-line CLI the way VLANs or routing protocols do. This lab uses a Cisco Wireless LAN Controller (WLC) with two lightweight access points (AP1, AP2) to build two logically separate wireless networks — an "Internal" SSID for trusted employee devices and a "Guest" SSID for visitors — each mapped to its own VLAN, exactly the way a real enterprise separates guest Wi-Fi from the corporate network.

By the end of this lab you will be able to:

- Explain the centralized (WLC + lightweight AP) wireless architecture versus autonomous/standalone APs
- Access and navigate a WLC's HTTPS management GUI
- Configure WLC dynamic interfaces and map them to VLANs
- Create WLANs (SSIDs) and map each to the correct dynamic interface
- Configure WPA2-PSK security on a WLAN
- Trace the full path an association-and-forwarding decision takes: `SSID → WLAN → Dynamic Interface → VLAN → IP Subnet`
- Explain why wireless troubleshooting always requires wired-network knowledge too — the AP's uplink, the switch trunk, and VLAN configuration all sit underneath every wireless symptom

---

## 2. Business Context

**Why would a real company do this?**

- **"We need guest Wi-Fi that can't touch our internal file servers"** → this is the textbook driver for WLAN-to-VLAN separation. Two SSIDs sharing the same physical APs, mapped to two different VLANs (100 for Internal, 200 for Guest), gives visitors internet access without any Layer 2 or Layer 3 path into the corporate network by default — the separation happens at the VLAN boundary, identical in principle to how a wired guest port would be isolated.
- **"We have 40 access points across three floors — configuring each one individually doesn't scale"** → this is exactly what a WLC-based (lightweight AP) architecture solves. Every AP registers with the controller and inherits its SSID, security, and radio configuration centrally; changing the Guest network's password once on the WLC updates every AP simultaneously, instead of 40 separate logins.
- **"IT needs to manage the wireless infrastructure without physically touching every AP"** → the WLC's own management interface (a dedicated VLAN, separate from any client-facing WLAN) is the administrative control plane — reachable over the wired network, independent of whether any wireless client traffic is even flowing.
- **"A compliance auditor asked how we prevent guest devices from reaching payroll systems"** → "separate SSID mapped to a separate VLAN with no routed path to internal VLANs, enforced by ACLs/firewall between them" is a concrete, auditable answer built directly from this lab's design.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-58-Lab-Wireless-LANs.png" alt="Day 58 WLC Topology" width="900">
</p>

```text
                           WLC1
                       172.16.1.10
                            |
                         G1/0/1
                            |
                           SW1
                    3650 Multilayer Switch
                   /         |         \
              G1/0/2      G1/0/3      G1/0/4
                |            |            |
               AP1          AP2           PC1
                |            |
          Wireless        Wireless
           Client          Client
          (Laptop)      (Smartphone)
```

Every wireless client's traffic physically transits AP1 or AP2, then SW1, then the WLC's dynamic interface — the "wireless" part of this topology is entirely the last hop between a client and an AP. Everything past the AP is ordinary wired switching, which is the single most important thing to internalize before troubleshooting anything wireless (see Section 10).

---

## 4. IP Addressing Plan

### 4.1 The three VLANs/subnets this lab uses

| VLAN | Purpose | Subnet | WLC Interface | Interface IP |
|---|---|---|---|---|
| 10 | WLC Management | 172.16.1.0/24 | Management | 172.16.1.10 |
| 100 | Internal WLAN (SSID: Internal) | 10.0.0.0/24 | Internal (dynamic) | 10.0.0.10 |
| 200 | Guest WLAN (SSID: Guest) | 10.1.0.0/24 | Guest (dynamic) | 10.1.0.10 |

**Why three separate /24s rather than one shared subnet:** each VLAN here serves a distinct trust boundary — administrative control-plane traffic (Management), trusted employee traffic (Internal), and untrusted visitor traffic (Guest) — and mixing any of them onto one subnet would collapse a security boundary that VLANs exist specifically to enforce. A /24 is used for each simply because it comfortably fits a branch or floor's worth of wireless clients with room to grow, the same reasoning applied to wired LAN sizing in earlier labs.

**Why the WLC's own management address (172.16.1.10) is on a fourth, non-client VLAN:** if the WLC's management interface lived on the Internal or Guest VLAN instead of its own dedicated VLAN 10, a compromised guest device or an internal user could potentially reach the controller's own administrative interface directly. Separating management traffic from every client-facing WLAN is the same "don't put your control plane on a user-facing segment" principle used for switch management VLANs since Day 1.

### 4.2 The addressing chain that actually matters for this lab

This lab's core addressing concept isn't subnetting math (there's no manual calculation required here, unlike GRE's /30s) — it's understanding that **one physical radio interface on an AP can carry multiple logically separate IP subnets simultaneously**, entirely determined by which SSID the client associated to:

```text
SSID "Internal"  →  WLAN profile "Internal"  →  Dynamic Interface "Internal"  →  VLAN 100  →  10.0.0.0/24
SSID "Guest"     →  WLAN profile "Guest"     →  Dynamic Interface "Guest"     →  VLAN 200  →  10.1.0.0/24
```

A laptop and a smartphone sitting one meter apart, both associated to AP1, can be on entirely different IP subnets purely because one chose "Internal" and the other chose "Guest" from the SSID list — there is no other addressing decision happening at the RF layer at all.

---

## 5. Pre-Configuration Checklist

- [ ] SW1's ports toward the WLC and both APs are configured as trunks (or appropriately tagged) carrying VLANs 10, 100, and 200 — the WLC's dynamic interfaces cannot function if the underlying switchport doesn't carry the right VLANs. This is wired-network prerequisite work that has nothing to do with the WLC GUI.
- [ ] You can reach `https://172.16.1.10` from PC1 before attempting any WLC configuration — if the HTTPS management page won't load, nothing past that point in this lab is possible yet, and the problem is almost always wired connectivity or VLAN 10 trunking, not the WLC itself.
- [ ] You know, before opening the GUI, which VLAN ID and subnet each of your two dynamic interfaces will use (Section 4.1) — decide this on paper first, the same discipline used for every other lab's addressing plan.

---

## 6. Configuration Tasks

All configuration in this lab happens through the WLC's HTTPS GUI, not a CLI — read each step for *what* you're setting and *why*, then locate the corresponding GUI page (menu names are stable across WLC software versions, though exact button placement varies slightly).

### 6.1 Task 1 — Access the WLC

Browse to `https://172.16.1.10` from PC1 and log in with the lab's admin credentials.

**What it does:** establishes an authenticated HTTPS session to the controller's management plane. **Why it matters:** this confirms VLAN 10 management connectivity end-to-end before any wireless-specific configuration is attempted — if this step fails, stop and troubleshoot wired connectivity/VLAN 10 trunking, not wireless settings.

### 6.2 Task 2 — Review MONITOR and WIRELESS

Check the **MONITOR** page for `802.11a Network State` and `802.11b/g Network State` (both should show Enabled), and the **WIRELESS** page for AP1 and AP2 registration status.

**What it does:** confirms the controller's radios are active domain-wide, and that both lightweight APs have already joined the controller (lightweight APs auto-discover and register with a WLC on the same management network — no per-AP SSID configuration is done locally on them). **Why it matters:** an AP that hasn't joined the controller cannot broadcast any SSID you configure later, no matter how correctly you configure it — this is always the first thing to check if a client can't even see a network name.

### 6.3 Task 3 — Configure the Internal dynamic interface

**Controller → Interfaces → New**

```text
Interface Name: Internal
VLAN ID: 100
IP Address: 10.0.0.10
Subnet Mask: 255.255.255.0
```

**What it does:** creates the WLC's own Layer 3 presence on VLAN 100 — this is the interface that will terminate all traffic from clients associated to the Internal SSID once it's mapped to a WLAN. **Why it matters:** a WLAN cannot be mapped to a VLAN that doesn't already exist as a dynamic interface — this step must happen before Task 5 (creating the Internal WLAN), not after.

### 6.4 Task 4 — Configure the Guest dynamic interface

**Controller → Interfaces → New**

```text
Interface Name: Guest
VLAN ID: 200
IP Address: 10.1.0.10
Subnet Mask: 255.255.255.0
```

Same logic as Task 3, mirrored for the Guest network. After this task, the interface table shows `Guest`, `Internal`, `Management`, and `Virtual` (a built-in interface WLCs use internally for mobility/web-auth redirects — not something you configure in this lab).

### 6.5 Task 5 — Create the Internal WLAN

**WLANs → Create New**

```text
Profile Name: Internal
SSID: Internal
```

Then, on the WLAN's **General** tab, map it to the dynamic interface:

```text
Interface/Interface Group: Internal
```

**What it does:** creates WLAN ID 1, binds the broadcast SSID "Internal" to the dynamic interface (and therefore VLAN 100) configured in Task 3. **Why it matters:** this is the step that actually links a broadcast wireless network name to a specific VLAN — everything before this was preparation, this is where the mapping becomes real.

### 6.6 Task 6 — Secure the Internal WLAN with WPA2-PSK

On the WLAN's **Security → Layer 2** tab:

```text
Layer 2 Security: WPA2
Auth Key Mgmt: PSK
Pre-Shared Key: <shared passphrase>
```

Then enable the WLAN (toggle **Status: Enabled** on the General tab).

**What it does:** requires any client associating to this SSID to authenticate with a shared passphrase before being allowed to associate. **Why it matters:** an open (unsecured) WLAN broadcasting "Internal" would let any nearby device join the corporate wireless network with zero authentication — WPA2-PSK is the minimum acceptable bar for this, though a real enterprise Internal network would more likely use WPA2/3-Enterprise with 802.1X rather than a single shared PSK (see Section 12 Stretch Goal).

### 6.7 Task 7 — Repeat for the Guest WLAN

```text
Profile Name: Guest
SSID: Guest
Interface/Interface Group: Guest
Layer 2 Security: WPA2
Auth Key Mgmt: PSK
Pre-Shared Key: <different shared passphrase>
```

**Why a different WLAN profile and a different PSK, not just a second SSID on the same profile:** each WLAN profile is what actually carries the VLAN mapping — a single profile can only map to one interface/VLAN. Two independent profiles are required specifically because Internal and Guest need to land on two different VLANs; there's no way to achieve that separation with one profile.

### 6.8 Task 8 — Associate wireless clients

Connect the Laptop to SSID "Internal" and the Smartphone to SSID "Guest," supplying each PSK when prompted.

**What it does:** demonstrates the full chain from Section 4.2 end to end — a successful association means the client authenticated via WPA2-PSK, associated with an AP, and the AP forwarded the association to the WLC, which placed the client's traffic onto the correct dynamic interface/VLAN/subnet based purely on which SSID it joined.

---

## 7. Verification Steps

| Location | What to check |
|---|---|
| MONITOR → Summary | Controller uptime, management IP, both 802.11a/b/g radios Enabled |
| WIRELESS → Access Points | AP1 and AP2 both show as registered/joined |
| CONTROLLER → Interfaces | Guest, Internal, Management, and Virtual interfaces all present with correct VLAN IDs |
| WLANs | WLAN ID 1 (Internal) and WLAN ID 2 (Guest) both present, both Enabled, security shows WPA2/PSK |
| MONITOR → Clients | Laptop and Smartphone both show as associated, each under the correct SSID |

### Expected Output Gallery

```text
CONTROLLER > Interfaces

Interface Name    VLAN Identifier    IP Address    Interface Type
---------------    ---------------    -----------    ---------------
Guest              200                10.1.0.10      Dynamic
Internal           100                10.0.0.10      Dynamic
Management         10                 172.16.1.10    Static
Virtual            N/A                1.1.1.1        Static
```

```text
WLANs

WLAN ID    WLAN Profile Name    WLAN SSID    Admin Status    Security Policies
-------    ------------------    ---------    ------------    -----------------
1          Internal              Internal     Enabled          WPA2 [Auth(PSK)]
2          Guest                 Guest        Enabled          WPA2 [Auth(PSK)]
```

```text
MONITOR > Clients

Client MAC          AP Name    WLAN Profile    IP Address    Status
-----------------    -------    ------------    -----------    -------
aa:bb:cc:00:11:22    AP1        Internal        10.0.0.101     Associated
dd:ee:ff:33:44:55    AP2        Guest           10.1.0.201     Associated
```

---

## 8. Common Mistakes (80/20 Rule)

1. **Creating the WLAN before creating its dynamic interface.** The interface has to exist first — you can't map a WLAN to something that doesn't exist yet.
2. **Forgetting to enable the WLAN after configuring it.** A fully configured but disabled WLAN will not broadcast its SSID at all — a common source of "the network doesn't even show up in the client's Wi-Fi list" confusion.
3. **Assuming a wireless connectivity problem is wireless-specific.** As Section 10's troubleshooting workflow emphasizes, a client that associates fine but gets no IP address is very often a wired-side problem (the switch trunk not carrying the right VLAN, or no DHCP scope for that subnet) — not anything wrong with the WLAN/SSID configuration itself.
4. **Using the same VLAN for Internal and Guest "to keep it simple."** This defeats the entire purpose of the lab and of guest network design generally — the whole point is that the two networks must not share a broadcast domain.
5. **Confusing the WLC management interface's subnet with either client WLAN's subnet.** These are three separate VLANs/subnets by design (Section 4.1) — putting management traffic on a client-facing VLAN is a real security anti-pattern, not just an organizational preference.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Where to Check | Fix |
|---|---|---|---|---|
| 1 | Can't even reach the WLC GUI | VLAN 10 trunking/wired issue, not wireless at all | SW1 trunk configuration toward WLC | Fix the wired path first — nothing wireless-specific can be diagnosed until this works |
| 2 | SSID doesn't appear in a client's network list | WLAN disabled, or AP hasn't joined the controller | WLANs page (Admin Status), WIRELESS → Access Points | Enable the WLAN; confirm AP registration |
| 3 | Client sees the SSID but authentication fails | Wrong PSK, or Layer 2 security mismatched between client and WLAN config | WLAN → Security → Layer 2 tab | Confirm PSK matches exactly; confirm WPA2/PSK (not WPA3 or Enterprise) is what the client expects |
| 4 | Client associates successfully but gets no usable IP address | DHCP scope missing for that VLAN, or the switch trunk toward the AP/WLC doesn't carry that VLAN | Switch trunk allowed-VLAN list; DHCP server scope for that subnet | Add the VLAN to the trunk's allowed list; confirm/create the DHCP scope |
| 5 | Client on Internal can unexpectedly reach a Guest-VLAN host | No inter-VLAN ACL/firewall enforcement between VLANs 100 and 200 | Layer 3 device routing between the two VLANs | Apply an ACL or firewall policy denying Guest→Internal traffic — VLAN separation alone only stops *broadcast domain* leakage, not routed traffic between them if a router happens to have routes to both |
| 6 | Everything above checks out but the client still won't connect | AP1/AP2 not actually joined to the controller | WIRELESS → Access Points | Confirm the AP's own uplink and management-VLAN reachability to the WLC |

---

## 10. Design Analysis

**Why a centralized WLC + lightweight AP architecture instead of standalone/autonomous APs?** With standalone APs, every SSID, security policy, and radio setting must be configured on every single AP independently — at 2 APs this is a minor inconvenience, at 40+ APs across a building it becomes unmanageable and inconsistency-prone (one AP's Guest PSK drifting out of sync with the others, for example). Centralizing that configuration on a WLC means a single change (rotating the Guest PSK, say) propagates to every registered AP simultaneously.

**Why does each WLAN need its own dynamic interface rather than sharing one interface with a filter?** The dynamic interface *is* the VLAN mapping — there's no other mechanism in this architecture that determines which VLAN a given WLAN's traffic lands on. One interface can only belong to one VLAN, so two logically separate networks (Internal, Guest) inherently need two separate dynamic interfaces, the same way two VLANs on a wired switch need two separate SVIs if a router needs to reach both.

**Why WPA2-PSK here rather than something stronger like WPA2/3-Enterprise?** PSK is appropriate for a lab and for genuinely simple deployments (a single shared password for all users of a given SSID), but production Internal networks typically use WPA2/3-Enterprise with 802.1X, authenticating each user individually against a RADIUS/directory service rather than a single shared secret everyone knows — this also allows per-user revocation (disable one employee's access) without having to rotate a shared password for the entire company. PSK remains reasonable for Guest networks precisely because there's no individual-user identity to authenticate in the first place.

---

## 11. Real-World Parallel

Any office, retail location, hotel, or campus with both employee and guest Wi-Fi is running close to this exact design: a handful of SSIDs, each mapped through a controller to a distinct VLAN, each VLAN routed (or explicitly not routed) to different parts of the network based on trust level. The "SSID → WLAN → Dynamic Interface → VLAN → Subnet" chain from Section 4.2 is the mental model every wireless engineer uses when diagnosing "why did this device end up on the wrong network" — and the troubleshooting workflow in Section 9 (wireless symptoms frequently having wired root causes) is exactly how real wireless trouble tickets get triaged.

---

## 12. Stretch Goal

1. Research WPA2-Enterprise (802.1X) versus WPA2-PSK and explain, in writing, what additional infrastructure (a RADIUS server) it requires and why a real Internal corporate WLAN would typically prefer it over PSK.
2. Add a third WLAN/SSID for IoT devices, mapped to its own VLAN/dynamic interface, and design (on paper) an ACL policy that allows IoT devices to reach the internet but not any other internal VLAN.
3. Explain, without configuring it, how band steering (preferring 5GHz/802.11a over 2.4GHz/802.11b/g for capable clients) would fit into this WLC's configuration, and why it matters in a dense, multi-AP deployment.

---

## 13. Self-Assessment Checklist

- [ ] I can draw the SSID → WLAN → Dynamic Interface → VLAN → Subnet chain from memory for both the Internal and Guest networks.
- [ ] I can explain why the WLC management interface sits on its own VLAN, separate from both client WLANs.
- [ ] I can explain the difference between a lightweight AP and a standalone/autonomous AP.
- [ ] I can list, in order, the wireless troubleshooting workflow from Section 9 without looking.
- [ ] I can explain why a client that associates successfully might still fail to get a usable IP address, and whose fault that usually is (wired-side, not wireless).

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** WLC-centralized (lightweight AP) wireless architecture; dynamic interfaces as the WLAN-to-VLAN mapping mechanism; WPA2-PSK security; SSID/VLAN separation for Guest vs. Internal traffic; management-plane VLAN separation.

**What I learned:** Wireless configuration on enterprise gear happens through a GUI, not a CLI, because RF/security/SSID settings don't decompose cleanly into a line-oriented command syntax the way routing and VLAN configuration do — but the underlying concept is still just VLANs and Layer 3 addressing wearing a wireless front end. The SSID a client picks is the *only* thing determining which VLAN/subnet it lands on; everything downstream of association is ordinary wired switching and routing, which is exactly why wireless troubleshooting so often turns out to be a wired-network problem in disguise.

**Skills practiced:** WLC GUI navigation, dynamic interface configuration, WLAN/SSID creation and VLAN mapping, WPA2-PSK configuration, structured wireless-to-wired troubleshooting.

---

## 15. GNS3 Lab

See [`GNS3/README.md`](GNS3/README.md). **There is no `build_lab.py` for this lab.** GNS3 has no open-source appliance capable of simulating real 802.11 RF behavior, WLC-to-AP CAPWAP registration, or SSID-based client association — the README explains this limitation in detail and describes how to approximate the *wired* half of this topology (SW1, trunking, VLANs 10/100/200) if you want to practice that portion, while pointing you to Packet Tracer (which does simulate WLC/AP/wireless-client behavior) for the actual wireless configuration steps in Sections 6–7 above.
