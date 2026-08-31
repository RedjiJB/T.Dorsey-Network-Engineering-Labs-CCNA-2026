# Day 51 Lab Manual — Dynamic ARP Inspection (DAI)

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Layer DAI on top of an already-working DHCP Snooping deployment (R1 as DHCP server, SW1/SW2 snooping-enabled) to inspect and validate ARP traffic on untrusted interfaces, defeating ARP spoofing/poisoning attacks. |
| **Exam Relevance** | CCNA 200-301 — Domain 5 (Security Fundamentals): "configure and verify Layer 2 security features (DHCP snooping, dynamic ARP inspection)" — DAI and DHCP Snooping are explicitly grouped together on the exam blueprint. |
| **Prerequisites** | **Day 50 (DHCP Snooping) completed and working** — DAI in this design depends directly on the DHCP Snooping binding table; this is a hard prerequisite, not optional background. ARP fundamentals (Request/Reply, IP-to-MAC resolution). |
| **Time Estimate** | 1 – 1.5 hours (shorter than Day 50 since the DHCP Snooping foundation is already built). |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the DAI commands are short, but explaining *why* DAI needs DHCP Snooping's binding table is the real exam-relevant concept. |

---

## 1. Lab Overview + Learning Objectives

This lab picks up exactly where Day 50 left off: R1 is the DHCP server, SW1 and SW2 already run DHCP Snooping with the correct trust boundary and Option 82 disabled. Dynamic ARP Inspection is now enabled on top of that foundation, using the same VLAN, and trusting the same infrastructure-facing interfaces DHCP Snooping already trusts — because DAI validates untrusted ARP traffic *against* the DHCP Snooping binding table, the two features are designed to be deployed together.

By the end you will be able to:

- Explain why DAI requires DHCP Snooping's binding table to function correctly
- Enable DAI per-VLAN and configure trusted/untrusted interfaces
- Enable additional DAI validation checks (source MAC, destination MAC, IP address)
- Explain the ARP spoofing/poisoning attack DAI defends against, step by step
- Distinguish DHCP Snooping's role from DAI's role even though they're configured almost identically
- Verify DAI status and interpret its output

---

## 2. Business Context

**Why would a real company do this?**

ARP has no authentication built in — any device on a LAN segment can send a gratuitous ARP reply claiming to own any IP address, and every other device on that segment will simply believe it and update their ARP cache. This is the mechanism behind **ARP spoofing/poisoning**, one of the oldest and still most effective LAN-based man-in-the-middle attacks: an attacker sends forged ARP replies claiming "I am 192.168.1.1" (the real default gateway), and every victim device on the segment starts sending its gateway-bound traffic — including credentials, session tokens, anything unencrypted — straight to the attacker's machine instead.

- **"We already deployed DHCP Snooping — doesn't that cover this?"** → No. DHCP Snooping only protects the DHCP lease process itself; it does nothing to stop a device from later sending forged ARP traffic completely independent of DHCP. DAI closes that separate gap, which is exactly why the two are almost always deployed as a pair.
- **"How do we know an ARP reply is legitimate without a central authority for IP-to-MAC mappings?"** → DAI doesn't invent a new authority — it reuses the DHCP Snooping binding table (which already recorded "this MAC leased this IP on this port") as its source of truth, comparing every untrusted ARP packet's claimed IP-to-MAC mapping against that record.
- **"Our finance team handles wire transfers over the LAN — an ARP spoofing MITM there is a real financial risk, not just an IT inconvenience"** → this is the direct business translation of "protect ARP traffic on untrusted ports" — DAI is specifically the control that prevents a compromised or malicious device on the LAN from silently repositioning itself as the gateway for sensitive traffic.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-51-Lab-Dynamic-ARP-Inspection.png" alt="Day 51 DAI Topology" width="900">
</p>

Identical topology to Day 50: `R1 (DHCP server) -- SW1 -- SW2 -- PC1`, reusing R1, SW1, and SW2 from that lab unchanged. DAI's trust boundary mirrors DHCP Snooping's exactly: SW1 trusts **both** G0/1 (toward SW2) and G0/2 (toward R1) for DAI, while SW2 trusts only G0/1 (toward SW1). This is broader than DHCP Snooping's trust set on SW1 — see Section 10 for why.

---

## 4. IP Addressing Plan

Unchanged from Day 50 — `192.168.1.0/24`, exclusion `192.168.1.1`–`.9`, R1 as gateway and DHCP server. DAI introduces no new addressing of its own; it validates the *existing* address bindings DHCP Snooping already recorded. If you're doing this lab standalone, complete Day 50's Section 4 addressing walkthrough first — DAI has nothing to validate against without it.

---

## 5. Pre-Configuration Checklist

1. Confirm Day 50's DHCP Snooping configuration is fully working: `show ip dhcp snooping binding` must show a real entry for PC1 before DAI is meaningfully testable.
2. Know that DAI's trust boundary is configured *separately* from DHCP Snooping's, even though it usually mirrors it closely — `ip dhcp snooping trust` and `ip arp inspection trust` are two different commands that must both be applied where needed.
3. Note the subtle difference in this lab's trust design: SW1 trusts G0/1 for DAI (even though G0/1 was *not* trusted for DHCP Snooping) — read Section 10 before assuming this is a typo.

---

## 6. Configuration Tasks

### 6.1 Enable DAI on SW1's VLAN

```text
SW1(config)#ip arp inspection vlan 1
```

**Mode:** Global Config. **What it does:** turns on ARP inspection for VLAN 1 — every ARP packet arriving on an *untrusted* interface in this VLAN will now be checked against the DHCP Snooping binding table before being allowed to pass. **Why it matters:** like DHCP Snooping, DAI is VLAN-scoped and does nothing until the VLAN is explicitly enabled. **Threat model this defends against:** a device on an untrusted port sending a forged ARP reply claiming to be `192.168.1.1` (the gateway) using a MAC address that doesn't match the DHCP Snooping binding table's record for that IP — DAI drops it before it ever reaches another host's ARP cache.

### 6.2 Trust SW1's infrastructure-facing interfaces for DAI

```text
SW1(config)#interface g0/1
SW1(config-if)#ip arp inspection trust
SW1(config-if)#exit
SW1(config)#interface g0/2
SW1(config-if)#ip arp inspection trust
SW1(config-if)#exit
```

**Mode:** Interface config. **What it does:** exempts G0/1 (toward SW2) and G0/2 (toward R1) from DAI inspection — ARP traffic crossing switch-to-switch or switch-to-router infrastructure links is trusted by design, the same logic DHCP Snooping uses for server-facing uplinks. **Why both interfaces here, unlike DHCP Snooping which trusted only G0/2 on SW1:** DAI's threat model cares about *any* infrastructure-to-infrastructure link potentially carrying legitimate ARP traffic that wasn't necessarily part of a DHCP transaction — a router-to-switch or switch-to-switch link is inherently trusted infrastructure for ARP purposes even if it wasn't the DHCP server path specifically. **Memory aid:** "DHCP Snooping trusts the path to the server; DAI trusts all infrastructure links."

### 6.3 Enable additional DAI validation checks

```text
SW1(config)#ip arp inspection validate src-mac dst-mac ip
```

**Mode:** Global Config. **What each check does:**
- **`src-mac`** — compares the sender MAC address in the Ethernet header against the sender MAC in the ARP body; a mismatch (a classic spoofing signature) is dropped.
- **`dst-mac`** — for ARP replies, compares the target MAC in the Ethernet header against the target MAC in the ARP body.
- **`ip`** — validates the sender/target IP addresses in the ARP body against invalid or unexpected values (e.g., 0.0.0.0, broadcast, or multicast addresses claimed as a sender IP).

**Why it matters:** the base `ip arp inspection vlan 1` command alone only checks IP-to-MAC binding against the DHCP Snooping table; these three checks add defense against additional spoofing techniques that manipulate the Ethernet-header-vs-ARP-body relationship, which a binding-table-only check wouldn't catch.

### 6.4 Repeat on SW2

```text
SW2(config)#ip arp inspection vlan 1
SW2(config)#ip arp inspection validate src-mac dst-mac ip
SW2(config)#interface g0/1
SW2(config-if)#ip arp inspection trust
SW2(config-if)#exit
```

**Why only G0/1 trusted here, not any client-facing port:** SW2's client-facing FastEthernet ports are exactly where DAI's protection matters most — end-user devices are the ones capable of sending forged ARP traffic, so they must remain untrusted (inspected) by design, mirroring the same "protect the edge, trust the infrastructure" logic from Day 50.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip arp inspection` | Global enable state, VLAN scope, validation checks enabled |
| `show ip arp inspection interfaces` | Per-interface trusted/untrusted state |
| `show ip dhcp snooping binding` | The table DAI is validating against — confirm it's populated |
| `show ip arp inspection statistics` | Counts of forwarded vs. dropped ARP packets per VLAN |

### 7.1 Expected Output Gallery

**`SW1# show ip arp inspection interfaces`**

```text
Interface        Trust State     Rate (pps)    Burst Interval
---------------   -----------     ----------    --------------
GigabitEthernet0/1  Trusted       None            N/A
GigabitEthernet0/2  Trusted       None            N/A
FastEthernet0/1     Untrusted     15              1
FastEthernet0/2     Untrusted     15              1
```

**`SW1# show ip arp inspection`**

```text
Source Mac Validation      : Enabled
Destination Mac Validation : Enabled
IP Address Validation      : Enabled

Vlan     Configuration    Operation State    ACL Match    Static ACL
----     -------------    ---------------    ---------    ----------
1        Enabled          Active

Vlan     ACL Logging      DHCP Logging
----     -----------      ------------
1        Deny             Deny
```

**Simulated attack — a spoofed ARP reply arriving on an untrusted port with a MAC/IP pairing that does not match the DHCP Snooping binding table:**

```text
%SW-4-DYNAMIC_ARP_ADD_FAILURE: Adding ARP entry failed for ... interface FastEthernet0/2, vlan 1
%ASIC-4-DAI_ARP_SPOOF: ARP validation failed on Fa0/2 - dropped
```

(Exact syslog wording varies by platform; the key signal is a drop specifically attributed to ARP inspection, distinct from a DHCP Snooping drop.)

---

## 8. Common Mistakes (80/20 rule)

1. **Enabling DAI before DHCP Snooping's binding table has any entries in it.** DAI with an empty binding table will drop essentially all untrusted ARP traffic, because it has nothing legitimate to compare against — always confirm `show ip dhcp snooping binding` is populated first.
2. **Assuming DAI's trust boundary automatically mirrors DHCP Snooping's.** They're separate commands (`ip dhcp snooping trust` vs. `ip arp inspection trust`) and, as this lab shows, don't necessarily trust the exact same interface set.
3. **Forgetting `ip arp inspection vlan 1`.** Trusting/untrusting individual interfaces has zero effect if the VLAN itself isn't enabled for inspection.
4. **Enabling all three additional validation checks (`src-mac dst-mac ip`) without understanding what each individually catches**, then being unable to explain a specific drop during troubleshooting.
5. **Confusing DAI's protection scope with DHCP Snooping's.** DHCP Snooping protects the DHCP *lease process*; DAI protects *ARP resolution* — a device could pass DHCP Snooping fine (get a legitimate lease) and still attempt an ARP spoofing attack afterward, which is exactly why both features exist independently.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | All untrusted-port ARP traffic dropped, even legitimate | DHCP Snooping binding table empty (Day 50 not actually working) | `show ip dhcp snooping binding` | Fix DHCP Snooping/DHCP lease process first — DAI is not independently functional without it |
| 2 | Infrastructure link (SW1↔SW2) traffic unexpectedly inspected/dropped | Forgot `ip arp inspection trust` on that interface | `show ip arp inspection interfaces` | Add `ip arp inspection trust` to the infrastructure-facing interface |
| 3 | DAI enabled, but nothing appears to be validated | Forgot `ip arp inspection vlan 1` | `show ip arp inspection` | Add the VLAN to DAI's scope |
| 4 | A legitimate device's ARP is dropped after a valid DHCP renewal | Binding table entry not yet reflecting the renewed lease (timing) | `show ip dhcp snooping binding` | Wait for binding table update or manually verify renewal completed |
| 5 | Can't tell if a drop was DAI or DHCP Snooping | Similar-looking syslog messages | Check message source tag (`DAI`/`ARP` vs. `DHCP_SNOOPING`) | Cross-reference `show ip arp inspection statistics` vs. `show ip dhcp snooping` counters |

---

## 10. Design Analysis

**Why this design over alternatives?**

- **Why does DAI depend on DHCP Snooping instead of maintaining its own independent trust database?** Building and maintaining a second, separate source of truth for IP-to-MAC bindings would be redundant and could drift out of sync with DHCP Snooping's own table, creating exactly the kind of inconsistency an attacker could exploit. Reusing DHCP Snooping's binding table means there's exactly one authoritative record, populated by exactly one process (legitimate DHCP leases), that both features rely on.
- **Why trust G0/1 for DAI on SW1 when DHCP Snooping does not trust it?** DHCP Snooping's trust decision is about "does legitimate DHCP server traffic arrive here" (only G0/2, toward R1, qualifies). DAI's trust decision is about "is this an infrastructure link where ARP traffic can be assumed legitimate" — G0/1 (SW1↔SW2) qualifies for that even though no DHCP server traffic originates from that direction. The two features ask genuinely different questions of the same physical topology, which is why their trust sets can legitimately differ.
- **Why enable all three additional validation checks instead of relying on the base binding-table check alone?** The base check alone only validates the IP-to-MAC pairing against the binding table; it does not catch a spoofed packet where the Ethernet header and ARP body disagree on MAC addresses (a different spoofing technique). Layering all three checks closes multiple distinct spoofing vectors rather than just one.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a penetration test report flags "ARP spoofing possible on internal VLAN" as a finding, and DAI-with-DHCP-Snooping is the textbook remediation to cite.
- ...a help desk ticket describes intermittent, hard-to-reproduce connectivity issues that turn out to be a misbehaving device (not malicious, just buggy) sending malformed gratuitous ARP — DAI's validation checks catch this as a side effect even without an actual attacker present.
- ...a compliance framework (PCI-DSS, for example) requires documented Layer 2 network segmentation and anti-spoofing controls for any segment handling payment data — DAI plus DHCP Snooping is concrete evidence of that control.
- ...a new switch is added to a network that already has DAI deployed, and the engineer forgets to trust the new switch's uplink for DAI, causing legitimate infrastructure traffic to be silently dropped until diagnosed via `show ip arp inspection interfaces`.

---

## 12. Stretch Goal

1. Configure `ip arp inspection limit rate <pps>` on a client-facing port to rate-limit ARP packets, mitigating an ARP-flood-based denial-of-service in addition to the spoofing protection DAI already provides.
2. Build an ARP ACL (`arp access-list`) for a device with a statically-assigned IP that never goes through DHCP (and therefore has no DHCP Snooping binding entry) so its legitimate ARP traffic isn't wrongly dropped — explain why a purely DHCP-Snooping-backed DAI deployment has a gap for static-IP devices.
3. Deliberately spoof an ARP reply from a client-facing port (in Packet Tracer's simulation tooling, or a scripted approach) and capture the exact `show ip arp inspection statistics` counter increment it produces.

---

## 13. Self-Assessment

- [ ] Can you explain, from memory, why DAI depends on DHCP Snooping's binding table?
- [ ] Can you name the single VLAN-scoping command required before DAI does anything?
- [ ] Can you explain the difference between what `src-mac`, `dst-mac`, and `ip` validation each individually check?
- [ ] Can you explain why SW1's DAI trust set differs from its DHCP Snooping trust set in this lab, without looking?
- [ ] Could you describe an ARP spoofing attack, and DAI's defense against it, to a non-technical manager in under 2 minutes?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** ARP spoofing/poisoning as an attack; Dynamic ARP Inspection as a Layer 2 mitigation; DAI's dependency on the DHCP Snooping binding table; trusted/untrusted DAI interfaces; additional MAC/IP validation checks.

**What I learned:** DHCP Snooping and DAI are designed as a pair, not two independent features that happen to be configured similarly — DAI has no meaningful protection to offer without a populated DHCP Snooping binding table to validate against. The two features' trust boundaries can legitimately differ even on the same physical topology, because each is answering a subtly different question about the same links. Layer 2 security in general benefits from this "stack of complementary controls" approach rather than any single feature trying to do everything.

**Skills practiced:** DAI configuration (global, per-VLAN, per-interface trust, additional validation checks), understanding feature interdependencies between DHCP Snooping and DAI, ARP-spoofing threat modeling, structured Layer 2 security verification.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md). This reuses the Day 50 topology (VyOS R1, Open vSwitch SW1/SW2, Alpine PC1). As with Day 50, Open vSwitch does not implement `ip arp inspection` — the README documents the same limitation and suggests using Linux `arptables`/static ARP entries on the Alpine hosts to observe (not enforce) ARP spoofing behavior for conceptual practice only.
