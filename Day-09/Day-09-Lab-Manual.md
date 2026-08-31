# Day 09 Lab Manual — Interface Configuration & Device Management

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure a router and two switches on a shared `/16` LAN, then move beyond basic addressing into real device-management tasks: manual speed/duplex, interface descriptions, verification, and disabling unused ports to shrink attack surface. |
| **Exam Relevance** | CCNA 200-301 — Domain 1 (Network Fundamentals): 1.2 (interfaces, speed/duplex, auto-negotiation issues). Domain 5 (Security Fundamentals): unused port hardening. Duplex mismatch troubleshooting is a classic, frequently-tested scenario. |
| **Prerequisites** | Day 01–08 (topology, cabling, switching, IPv4 addressing). |
| **Time Estimate** | 1.5 hours. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner-Intermediate) — the commands are simple, but duplex mismatch reasoning and the security logic behind disabling unused ports carry real operational weight. |

---

## 1. Lab Overview

This lab moves past "get an IP address working" and into the day-2 operational tasks every network engineer does routinely: setting explicit speed/duplex instead of relying purely on auto-negotiation, documenting every interface with a description, verifying interface state methodically, and — critically — disabling every switch port that isn't actively in use.

One router (R1), two switches (SW1, SW2), four PCs, all on a single `172.16.0.0/16` LAN. The addressing is intentionally simple here (all on one `/24`-sized-in-practice segment of a larger `/16`) so the lab's cognitive load goes toward interface-level administration, not subnetting.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Manually configure interface speed and duplex, and explain why auto-negotiation sometimes needs to be overridden
- Explain what a duplex mismatch is, why it's one of the most maddening real-world Layer 1/2 problems to diagnose, and how to prevent it
- Apply meaningful interface descriptions across every connected port
- Use `show ip interface brief`, `show interfaces status`, and `show interfaces <if>` to verify device and interface state
- Administratively disable every unused switch port and explain the security rationale
- Explain, in business terms, why "leave everything on defaults" is not an acceptable production posture

---

## 2. Business Context

**Why would a real company do this?**

Interface-level hygiene is unglamorous, but it's one of the most consistently graded items in real network audits and real outage postmortems:

- **"Our help desk gets recurring 'slow network' tickets from one specific closet."** → duplex mismatches (one side auto-negotiating, the other hard-set, landing on mismatched settings) are a textbook cause of intermittent, hard-to-reproduce slowness — exactly the kind of ticket that looks like "the network is flaky" but is actually a specific, fixable Layer 1/2 misconfiguration.
- **"An auditor found 12 open switch ports in an empty conference room."** → every enabled-but-unused port is a potential entry point for an unauthorized device to plug in and reach the network. Disabling unused ports (Step 6.6 below) is one of the cheapest, highest-value security controls available on a switch — it costs nothing and closes a real, exploitable gap.
- **"New hire needs to trace a physical cable without walking the building."** → interface descriptions (`description PC1`, `description Uplink to SW2`) are what make `show running-config` or `show interfaces status` actually useful six months after the initial build, when nobody remembers off the top of their head which port goes where.
- **"We need to explain, in a change-management ticket, exactly what's connected to a given port before we touch it."** → this is precisely what a well-maintained interface description and status baseline gives you — the alternative is tracing cables by hand during a maintenance window, which is slow and error-prone.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2009%20Lab%20-%20Interface%20Configuration.png" alt="Day 09 Interface Configuration Lab" width="1000">
</p>

```text
PC1 \                    / PC3
     SW1 ---- R1 ---- SW2
PC2 /                    \ PC4
```

| Device | Connects To |
|---|---|
| PC1, PC2 | SW1 |
| PC3, PC4 | SW2 |
| SW1 | R1 |
| SW2 | R1 |

All devices share the `172.16.0.0/16` address space.

---

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

`172.16.0.0/16` (65,534 usable hosts) is far larger than the 4 PCs here require — this lab reuses the original's oversized `/16` deliberately as-is because the *point* of this lab isn't addressing efficiency (that was Day 08's focus), it's interface administration. A real deployment would right-size this to a `/24` or smaller; this lab doesn't, and that's fine — not every lab needs to optimize every axis at once.

### 4.2 Manual Calculation Walkthrough (brief, since Day 08 covered this method in depth)

```text
/16 → h = 16 host bits
usable hosts = 2^16 − 2 = 65,534

Mask: /16 = 11111111.11111111.00000000.00000000 = 255.255.0.0
```

```text
Network address:    172.16.0.0
First usable host:  172.16.0.1
Last usable host:   172.16.255.254
Broadcast address:  172.16.255.255
```

### 4.3 Full Device Address Table

| Device | Interface | IP Address | Mask |
|---|---|---|---|
| PC1 | NIC | 172.16.0.1 | 255.255.0.0 |
| PC2 | NIC | 172.16.0.2 | 255.255.0.0 |
| PC3 | NIC | 172.16.0.3 | 255.255.0.0 |
| PC4 | NIC | 172.16.0.4 | 255.255.0.0 |
| R1 | Gi0/0 | 172.16.255.254 | 255.255.0.0 |

**Default gateway for all 4 PCs:** `172.16.255.254`.

> Note this lab treats SW1 and SW2 as pure Layer 2 devices in this LAN's data path (no SVI/management IP is strictly required for the connectivity test itself, though a management VLAN IP is good practice — see Stretch Goal).

---

## 5. Pre-Configuration Checklist

1. Place R1, SW1, SW2, PC1–PC4 and cable per Section 3.
2. Assign PC IPs statically per Section 4.3.
3. Identify, on paper, every switch port that is and is not actually connected to a device before starting Step 6.6 — you cannot correctly disable "unused" ports without first knowing which ones are used.

---

## 6. Configuration Tasks

### 6.1 Hostnames

```text
Router(config)#hostname R1
```
```text
Switch(config)#hostname SW1
```
```text
Switch(config)#hostname SW2
```

### 6.2 Router LAN Interface

```text
R1(config)#interface gigabitEthernet 0/0
R1(config-if)#description LAN 172.16.0.0/16 - SW1/SW2 uplinks
R1(config-if)#ip address 172.16.255.254 255.255.0.0
R1(config-if)#no shutdown
R1(config-if)#exit
```

### 6.3 End Devices

Assign PC1–PC4 per Section 4.3 via Desktop → IP Configuration.

### 6.4 Verify Baseline Interface Status

```text
R1#show ip interface brief
```

> Confirm Gi0/0 shows `up/up` before proceeding — every later step in this lab assumes the base LAN connectivity already works.

### 6.5 Manually Configure Speed and Duplex on Uplinks

Applied to the switch-to-switch-adjacent and router-facing uplink ports (illustrated here on SW1's uplink toward R1; repeat the same pattern on SW2):

```text
SW1(config)#interface fastEthernet 0/24
SW1(config-if)#description Uplink to R1 Gi0/0
SW1(config-if)#speed 1000
SW1(config-if)#duplex full
SW1(config-if)#no shutdown
SW1(config-if)#exit
```

> **Mode:** Interface Config. By default, Cisco interfaces auto-negotiate speed and duplex with whatever the far end offers. Auto-negotiation is usually correct and is the recommended default in most modern gear — but it can fail silently on older hardware, certain NICs, or misbehaving auto-neg implementations, producing a **duplex mismatch**: one side settles on full-duplex, the other on half-duplex. Manually hard-setting both ends to matching values (as done here) eliminates that failure mode entirely, at the cost of losing automatic adaptation if the physical medium changes. This is a genuine trade-off, not a strictly "better" choice — see Design Analysis.
>
> **Memory aid:** "If you set one side manually, you must set the other side manually too — half-set duplex is worse than no duplex setting at all." A hard-set full-duplex port paired with an auto-negotiating port that falls back to half-duplex is the single most classic duplex mismatch scenario in networking.

### 6.6 Interface Descriptions on Every Connected Port

```text
SW1(config)#interface fastEthernet 0/1
SW1(config-if)#description Link to PC1
SW1(config-if)#exit
SW1(config)#interface fastEthernet 0/2
SW1(config-if)#description Link to PC2
SW1(config-if)#exit
```

Repeat the equivalent pattern for SW2's PC3/PC4 ports and for R1's Gi0/0 (already labeled in Step 6.2).

> A description costs nothing operationally and pays for itself the very first time someone other than you (or you, six months later) needs to trace a connection from `show interfaces status` output alone, without physically walking to the closet.

### 6.7 Disable Every Unused Port

```text
SW1(config)#interface range fastEthernet 0/3 - 23
SW1(config-if-range)#shutdown
SW1(config-if-range)#exit
```

> **Mode:** Interface range config. `interface range` applies a command to a contiguous (or comma-separated) block of interfaces in one operation instead of repeating the same 2 lines 21 times. `shutdown` here is the **opposite** action from every other lab in this course — every previous lab's lesson was "don't forget `no shutdown`"; this step deliberately shuts down ports **on purpose**, specifically *because* they have nothing connected. An enabled port with nothing plugged in is a live, reachable network entry point sitting exposed in an empty room, a conference table, or an unused cubicle — exactly the kind of finding a security audit flags. Repeat the equivalent range on SW2.

### 6.8 Save

```text
R1#copy running-config startup-config
SW1#copy running-config startup-config
SW2#copy running-config startup-config
```

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip interface brief` (R1) | Gi0/0 `up/up`, correct IP |
| `show interfaces status` (SW1, SW2) | Connected ports show `connected`, correct speed/duplex; unused ports show `disabled` |
| `show interfaces fastEthernet 0/24` | Confirms manually-set speed/duplex took effect (not "auto") |
| `show running-config \| section interface` | Descriptions present on every connected port |

### 7.1 Expected Output Gallery

**`SW1# show interfaces status`**

```text
Port      Name                    Status       Vlan   Duplex  Speed Type
Fa0/1     Link to PC1             connected    1      a-full  a-100 10/100BaseTX
Fa0/2     Link to PC2             connected    1      a-full  a-100 10/100BaseTX
Fa0/3                             disabled     1        auto  auto  10/100BaseTX
Fa0/4                             disabled     1        auto  auto  10/100BaseTX
...
Fa0/24    Uplink to R1 Gi0/0      connected    1        full  1000  10/100/1000BaseTX
```

Notice `Fa0/24`'s Duplex/Speed columns show `full` / `1000` without the `a-` prefix that `Fa0/1` and `Fa0/2` show — the `a-` prefix means "auto-negotiated to this value"; its absence on Fa0/24 confirms the value was manually hard-set, exactly as configured in Step 6.5.

**`SW1# show interfaces fastEthernet 0/24`**

```text
FastEthernet0/24 is up, line protocol is up (connected)
  Hardware is Fast Ethernet, address is 0007.EC4A.5B18
  Description: Uplink to R1 Gi0/0
  ...
  Full-duplex, 1000Mb/s, media type is 10/100/1000BaseTX
```

**`SW1# show interfaces fastEthernet 0/3`** (a deliberately disabled, unused port)

```text
FastEthernet0/3 is administratively down, line protocol is down (disabled)
```

### 7.2 Ping Verification

```text
PC1> ping 172.16.0.3
```

```text
Pinging 172.16.0.3 with 32 bytes of data:

Reply from 172.16.0.3: bytes=32 time=1ms TTL=127
Reply from 172.16.0.3: bytes=32 time=1ms TTL=127
Reply from 172.16.0.3: bytes=32 time=1ms TTL=127
Reply from 172.16.0.3: bytes=32 time=1ms TTL=127

Ping statistics for 172.16.0.3:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Success confirms the interface-level changes (speed/duplex, descriptions, disabled unused ports) did not break the underlying connectivity — a critical check, since it's entirely possible to correctly harden a network into a state where it no longer works.

---

## 8. Common Mistakes (the 80/20)

1. **Setting speed/duplex manually on only one end of a link.** This *creates* the exact duplex mismatch problem the manual configuration was supposed to prevent — always match both ends, or leave both on auto.
2. **Disabling a port that's actually in use because it wasn't correctly identified during the pre-configuration checklist.** Always verify `show interfaces status` shows `connected` (not `notconnect`) before assuming a port is safe to shut down.
3. **Using `interface range` syntax incorrectly** (wrong port range boundaries, or forgetting the switch's actual port count) — always confirm the platform's actual interface count before writing a range.
4. **Forgetting that `shutdown` in this lab is intentional**, and "fixing" it back to `no shutdown` out of habit from every prior lab.
5. **Skipping descriptions on the router's LAN interface**, treating descriptions as a "switch-only" task — every connected interface on every device benefits equally.
6. **Not re-verifying end-to-end connectivity after hardening** — it's entirely possible to disable a port that turns out to matter, or to introduce a duplex mismatch by only half-configuring speed/duplex, and not notice until a ping test is actually run.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | A device that should be connected shows `notconnect` | Wrong port shut down, or cabling issue | `show interfaces status` | Verify the correct port and re-enable if mistakenly shut |
| 2 | Link is up but intermittently slow / high error counters | Duplex mismatch (one end auto, one end hard-set, landed on different values) | `show interfaces <if>` — look for `input errors`, `collisions`, or "half-duplex" on one side | Match speed/duplex explicitly on both ends, or set both back to auto |
| 3 | PC can't reach anything after Step 6.7 | The wrong port range was disabled, catching an in-use port | `show interfaces status` | Re-enable the mistakenly disabled port with `no shutdown` |
| 4 | Description doesn't appear in `show interfaces status` | Description applied to wrong interface, or command typo | `show running-config \| section interface` | Correct the interface and re-apply |
| 5 | Manually set duplex doesn't seem to "stick" — still shows `auto` | Command applied but interface not re-checked, or applied to wrong interface entirely | `show interfaces <if>` | Re-verify correct interface, re-apply `speed`/`duplex` |

---

## 10. Design Analysis

**Why this design over the alternatives?**

- **Why manually set speed/duplex on uplinks instead of leaving everything on auto-negotiation?** Auto-negotiation is the *generally* correct default and modern hardware handles it reliably — but on uplinks specifically (the highest-traffic, most business-critical links in a wiring closet), many engineers still prefer to eliminate the auto-negotiation failure mode entirely by hard-setting both ends, accepting the small maintenance cost (both ends must be updated together if the medium ever changes) for the reliability gain on a critical path.
- **Why disable unused ports instead of just leaving them enabled with no device attached?** An enabled-but-empty port costs nothing to a legitimate user (there's no device there to reach it) but represents free reconnaissance/entry surface to anyone with brief physical access — plugging a rogue device into an empty, live port is one of the simplest and most common physical-security bypass techniques. Disabling costs nothing operationally and removes the exposure entirely.
- **Why use `interface range` instead of configuring each unused port individually?** Pure efficiency and consistency — with potentially 20+ unused ports across two switches, individually retyping the same 2-line block invites transcription errors (a missed port, a typo) that a single `interface range` command structurally can't produce.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a help desk ticket says "the network in Conference Room B is randomly slow" and the root cause, after real diagnosis, turns out to be a duplex mismatch on an old projector's Ethernet NIC that never correctly auto-negotiated.
- ...a physical security audit walks the building and finds live, unlabeled, unused switch ports in an empty office — exactly the finding this lab's Step 6.7 prevents.
- ...a new engineer inherits a switch with zero interface descriptions and has to trace cables physically, port by port, before making any change — the direct cost of skipping Step 6.6 on a real deployment.
- ...a change-management ticket requires you to state, in writing, exactly which ports are in use and which are disabled before a planned maintenance window — this lab's verification output (Section 7) is exactly that kind of evidence.

---

## 12. Stretch Goal

1. Add a management VLAN SVI (`interface vlan 1`) with an IP on both SW1 and SW2, enable SSH per the Day 04 pattern, and explain why a switch used purely for Layer 2 forwarding still benefits from remote manageability.
2. Deliberately create a duplex mismatch (hard-set one end full-duplex, leave the other on auto/half) and capture the resulting `show interfaces` error counters as evidence — then fix it and confirm the counters stop climbing.
3. Write a short "port inventory" table for SW1 and SW2 (Port / Status / Description / Connected Device) as a document you'd hand to another engineer — this is a realistic deliverable, not just a lab exercise.

---

## 13. Self-Assessment

- [ ] Can you explain what a duplex mismatch is and why it's notoriously hard to diagnose from user reports alone?
- [ ] Can you explain the trade-off between manual speed/duplex and auto-negotiation, rather than just picking one as "always correct"?
- [ ] Can you explain the security rationale for disabling unused switch ports, in terms a non-technical stakeholder would accept?
- [ ] Can you write the `interface range` syntax from memory?
- [ ] Given `show interfaces status` output you've never seen before, could you identify which ports are manually configured (no `a-` prefix) vs. auto-negotiated?

---

## 14. Key Concepts Demonstrated

- Manual speed/duplex configuration and the duplex mismatch failure mode
- Interface descriptions as an operational/documentation practice
- `interface range` for efficient bulk configuration
- Disabling unused ports as a physical-security control
- Interface state verification via multiple `show` commands

## What I Learned

This lab was the first time "disable an interface" was the *goal* instead of the mistake to avoid — a useful reversal that clarified that `shutdown`/`no shutdown` aren't inherently good or bad, they're tools applied deliberately based on whether a port should or shouldn't be reachable. The duplex mismatch discussion also reframed auto-negotiation: it's not a "beginner setting" to be immediately overridden everywhere, it's the generally correct default, with manual hard-setting reserved specifically for high-value uplinks where eliminating a subtle failure mode is worth the small ongoing maintenance cost.

## Skills Practiced

- Manual interface speed/duplex configuration
- Interface documentation via descriptions
- Bulk interface configuration with `interface range`
- Unused port hardening
- Multi-command interface state verification

---

## 15. GNS3 Lab

This lab has a companion GNS3 topology built automatically by [`GNS3/build_lab.py`](GNS3/build_lab.py):

| Role | Packet Tracer device | GNS3 image |
|---|---|---|
| R1 | Cisco 2911 | VyOS |
| SW1, SW2 | Cisco 2960 | Open vSwitch |
| PC1-PC4 | Generic PC | Alpine Linux |

Note: Open vSwitch ports don't expose Cisco-style `speed`/`duplex` sub-commands directly through the GNS3 GUI in the same way IOS does — use `ovs-vsctl` on the GNS3 host to inspect/adjust virtual link parameters if practicing this specific command set matters to you; otherwise treat the GNS3 build as primarily useful for the addressing, descriptions-as-documentation, and unused-port-disabling portions of this lab.

See [`GNS3/README.md`](GNS3/README.md) for how to run the build script.
