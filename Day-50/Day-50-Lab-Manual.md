# Day 50 Lab Manual — DHCP Snooping

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Configure R1 as a DHCP server, enable DHCP Snooping on SW1 and SW2 with correct trust boundaries, and troubleshoot a real DHCP-lease failure caused by DHCP Snooping's Option 82 handling. |
| **Exam Relevance** | CCNA 200-301 — Domain 5 (Security Fundamentals): "configure and verify Layer 2 security features (DHCP snooping ...)." Domain 4 also touches DHCP operation/relay. |
| **Prerequisites** | DHCP DORA process (Discover/Offer/Request/Ack), basic switch interface configuration, VLAN 1 default behavior. |
| **Time Estimate** | 1.5 – 2 hours (longer than it looks — the Option 82 troubleshooting step is the real content of this lab). |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the config is short, but understanding *why* a correctly-trusted topology still breaks DHCP is the actual learning objective. |

---

## 1. Lab Overview + Learning Objectives

R1 is configured as the network's DHCP server for `192.168.1.0/24`. SW1 and SW2 sit between R1 and PC1, and DHCP Snooping is enabled on both to block rogue DHCP servers. The lab deliberately walks you into a real-world gotcha: even with the trust boundary configured correctly, PC1's DHCP lease still fails — because DHCP Snooping's Option 82 relay-agent information insertion conflicts with how the request is being forwarded, and must be explicitly disabled to restore correct operation in this topology.

By the end you will be able to:

- Configure a Cisco IOS router as a DHCP server (pool, network, exclusions, default gateway)
- Enable DHCP Snooping globally and per-VLAN
- Correctly identify and configure trusted vs. untrusted interfaces based on topology, not guesswork
- Explain the rogue-DHCP-server attack DHCP Snooping defends against
- Diagnose a DHCP failure that persists even after trust is configured correctly, using the DHCP Snooping binding table and Option 82 as the missing piece
- Read and interpret the DORA process end-to-end, including where in the path DHCP Snooping inspects and potentially drops each message type

---

## 2. Business Context

**Why would a real company do this?**

Every device on a typical corporate LAN gets its IP configuration from DHCP with zero authentication of the server that answers — whichever DHCP server responds first "wins" for that client. This is a serious internal threat: **anyone who plugs a rogue DHCP server into any switch port on the LAN can hand out a malicious default gateway or DNS server to every new device that boots up**, silently redirecting their traffic through an attacker-controlled machine (a textbook man-in-the-middle setup).

- **"We can't stop employees from occasionally plugging in random routers/APs that ship with DHCP enabled by default"** → DHCP Snooping doesn't rely on employee behavior; it enforces at the switch that only traffic from the *known, trusted* server-facing port(s) is allowed to answer DHCP requests at all.
- **"IT needs to know exactly which device holds which leased IP, for security investigations"** → the DHCP Snooping binding table (`show ip dhcp snooping binding`) becomes an authoritative, switch-maintained record of MAC-to-IP-to-port bindings, which is also the foundation Dynamic ARP Inspection (Day 51) builds directly on top of.
- **"We upgraded switches and now half the office can't get an IP address, but the DHCP server config looks fine"** → this is exactly the failure mode this lab reproduces and fixes: a security feature interacting unexpectedly with existing forwarding behavior (Option 82) is one of the most common real "it used to work" tickets in networks that recently enabled DHCP Snooping.

This lab is deliberately structured so that "turn on DHCP Snooping" isn't the end of the story — a naive rollout that stops at enabling the feature and trusting the uplink is exactly the kind of change that breaks production DHCP for an entire floor, which is why the Option 82 troubleshooting section is the heart of this lab.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-50-Lab-DHCP-Snooping.png" alt="Day 50 DHCP Snooping Topology" width="900">
</p>

```text
R1 (DHCP server, G0/0) -- SW1(G0/2 trusted) -- SW1(G0/1) -- SW2(G0/1 trusted) -- SW2(client ports, untrusted) -- PC1
```

Trust boundary summary: `R1 <-- trusted --> SW1 <-- trusted --> SW2 <-- untrusted --> PC1`. Only the path back toward R1 is trusted; every client-facing port stays untrusted by default.

---

## 4. IP Addressing Plan

| Segment | Network | Notes |
|---|---|---|
| PC/Server LAN | 192.168.1.0 /24 | R1's DHCP pool |
| DHCP excluded range | 192.168.1.1 – 192.168.1.9 | Reserved for static infrastructure (R1's own gateway address, switch management IPs) |
| First assignable lease | 192.168.1.10 | First address after the exclusion range |

### 4.1 Why sized this way

A `/24` LAN gives 254 usable addresses — comfortable headroom for a PC/end-device segment that will grow. The exclusion range `192.168.1.1–192.168.1.9` is a deliberate small reserved block at the *start* of the subnet for infrastructure addresses (R1's gateway interface, switch management SVIs) that must never be handed out dynamically — a collision between a DHCP lease and a statically-assigned gateway address is one of the most disruptive and hardest-to-diagnose outages in a small network, so reserving a block up front avoids it categorically rather than relying on nobody ever choosing a conflicting static IP.

### 4.2 Manual calculation walkthrough

```text
192.168.1.0/24
Network address:    192.168.1.0
First usable host:  192.168.1.1
Last usable host:   192.168.1.254
Broadcast address:  192.168.1.255
```

Excluding `.1`–`.9` leaves `192.168.1.10`–`192.168.1.254` (245 addresses) available for dynamic lease — plenty for a lab-sized client population, with room to spare for the exam-relevant lesson that exclusions always come out of the *usable* range, never the network/broadcast addresses (which were never assignable in the first place).

---

## 5. Pre-Configuration Checklist

1. R1's G0/0 interface already has a static IP in `192.168.1.0/24` (this becomes both the router's LAN gateway and the DHCP pool's default-router option).
2. Confirm the physical/logical trust path: which interface on SW1 faces R1 (directly or via SW2)? Which interface on SW2 faces SW1? These are the only two interfaces that will be trusted.
3. Know in advance that "trust the uplink" alone will not be the complete fix in this lab — budget time for the Option 82 troubleshooting section, it's not optional.

---

## 6. Configuration Tasks

### 6.1 Configure R1 as the DHCP server

```text
R1(config)#ip dhcp excluded-address 192.168.1.1 192.168.1.9
R1(config)#ip dhcp pool LAN-POOL
R1(dhcp-config)#network 192.168.1.0 255.255.255.0
R1(dhcp-config)#default-router 192.168.1.1
R1(dhcp-config)#exit
```

**Mode:** Global Config → DHCP pool sub-mode. **`ip dhcp excluded-address`** must be configured *before* the pool, and reserves the range so the DHCP process never offers it — order matters because the exclusion is a global DHCP-process setting, not a pool-scoped one, so it's set outside the pool block. **`network`** defines the pool's scope and implicitly the subnet mask handed to clients. **`default-router`** is the gateway address every DHCP client will receive — must match R1's actual LAN-facing interface IP or clients get a gateway that doesn't exist. **Threat model reminder:** none of this configuration is what defends against a rogue DHCP server — that's entirely DHCP Snooping's job on the switches, configured next. R1 being "the real DHCP server" and R1 being "the trusted DHCP server" are two different concepts.

### 6.2 Enable DHCP Snooping on SW1 and configure its trusted uplink

```text
SW1(config)#ip dhcp snooping
SW1(config)#ip dhcp snooping vlan 1
SW1(config)#interface g0/2
SW1(config-if)#ip dhcp snooping trust
SW1(config-if)#exit
```

**Mode:** Global Config, then Interface config. **`ip dhcp snooping`** turns the feature on globally but does nothing until a VLAN is also enabled for it. **`ip dhcp snooping vlan 1`** scopes enforcement to VLAN 1 (this lab's only VLAN) — DHCP Snooping is VLAN-scoped so it can be selectively rolled out. **`ip dhcp snooping trust`** on G0/2 (the interface facing R1/the legitimate DHCP server path) tells the switch "DHCP server messages (Offer, ACK) arriving here are legitimate, pass them." **Threat model this prevents:** without this trust designation, DHCP Snooping's default-deny posture (every port starts untrusted) would drop the *real* server's Offer/ACK messages too — trust isn't optional extra hardening, it's required for legitimate DHCP to keep functioning at all once snooping is enabled. **Why G0/2 specifically and not G0/1:** G0/2 is the direct path toward R1; G0/1 (toward SW2/the clients) never carries legitimate server-originated messages, so it correctly stays untrusted.

### 6.3 Enable DHCP Snooping on SW2 and configure its trusted uplink

```text
SW2(config)#ip dhcp snooping
SW2(config)#ip dhcp snooping vlan 1
SW2(config)#interface g0/1
SW2(config-if)#ip dhcp snooping trust
SW2(config-if)#exit
```

**Mode:** same pattern as SW1. **Why G0/1 here (not G0/2):** SW2's port numbering/topology differs from SW1's — G0/1 is whichever physical interface faces *back toward SW1* (the direction the real DHCP server's replies travel from). Client-facing FastEthernet ports on SW2 are left at their untrusted default deliberately — this is the actual security boundary the whole lab exists to build.

### 6.4 First DHCP attempt on PC1 — and the failure

```text
PC1> ipconfig /release
PC1> ipconfig /renew
```

At this point, with the DHCP server correctly configured and both trust boundaries correctly configured, **the lease still fails.** This is the intended learning moment, not a mistake in the lab — see Section 9 (Troubleshooting) before assuming your trust config is wrong.

### 6.5 Diagnose and fix: disable Option 82 information insertion

```text
SW1(config)#no ip dhcp snooping information option
SW2(config)#no ip dhcp snooping information option
```

**Mode:** Global Config. **What Option 82 is:** by default, DHCP Snooping-enabled switches insert "relay agent information" (Option 82 — the switch's identity, port, VLAN) into DHCP request packets as they're forwarded upstream, giving the DHCP server extra context about *where* the request physically originated. **Why it breaks this topology:** in this multi-switch path, Option 82 insertion/validation behavior between SW1 and SW2 (and R1, which isn't configured as a relay agent expecting Option 82) causes the request to be rejected or mishandled rather than correctly relayed — a very common real-world interaction when DHCP Snooping is enabled on switches that sit between clients and a DHCP server that isn't itself Option-82-aware. **The fix:** disabling information-option insertion on both switches removes the extra field from the relayed packets, restoring straightforward DORA behavior that R1 (a plain DHCP server, not a relay-agent-aware one) can process correctly. **Why this matters more than the trust config:** this is the exact kind of issue that makes DHCP Snooping rollouts break production — the trust boundary was correct from the start, and the actual root cause was a *default* behavior of the feature interacting badly with the topology.

### 6.6 Retry the DHCP lease

```text
PC1> ipconfig /renew
```

Expect a successful lease in the `192.168.1.10+` range this time.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip dhcp snooping` | Snooping enabled, correct VLAN, correct trusted interfaces listed |
| `show ip dhcp snooping binding` | MAC/IP/lease/VLAN/interface entries appear once a client successfully leases |
| `show running-config \| section dhcp` (R1) | Pool, exclusion, network, default-router all correct |
| `show ip dhcp binding` (R1) | Server-side view of the same lease |
| `ipconfig /all` (PC1) | Client-side confirmation of leased IP, mask, gateway |

### 7.1 Expected Output Gallery

**`SW1# show ip dhcp snooping`**

```text
Switch DHCP snooping is enabled
DHCP snooping is configured on following VLANs:
1
Insertion of option 82 is disabled
Interface                  Trusted     Rate limit (pps)
------------------------   -------     ----------------
GigabitEthernet0/2         yes         unlimited
```

**Before the fix (Option 82 still enabled) — PC1 output:**

```text
PC1> ipconfig /renew

DHCP Request failed - No response from server.
IP Address...............: 0.0.0.0
Subnet Mask...............: 0.0.0.0
Default Gateway...........: 0.0.0.0
```

**After the fix — PC1 output:**

```text
PC1> ipconfig /renew

DHCP request successful.
IP Address...............: 192.168.1.12
Subnet Mask...............: 255.255.255.0
Default Gateway...........: 192.168.1.1
```

**`SW2# show ip dhcp snooping binding`** (after successful lease)

```text
MacAddress          IpAddress        Lease(sec)  Type           VLAN  Interface
------------------  ---------------  ----------  -------------  ----  --------------------
00:0C:29:AB:CD:EF   192.168.1.12     86400       dhcp-snooping  1     FastEthernet0/1
```

This table is the authoritative record of who holds which lease on which port — and is exactly what Dynamic ARP Inspection (Day 51) will reference to validate ARP traffic.

---

## 8. Common Mistakes (80/20 rule)

1. **Enabling `ip dhcp snooping` globally but forgetting `ip dhcp snooping vlan 1`.** Nothing is enforced (or protected) until the VLAN is explicitly included.
2. **Trusting the wrong interface** — e.g., trusting a client-facing port instead of the uplink toward the DHCP server, which defeats the entire point of the feature.
3. **Assuming "trust the uplink" alone guarantees working DHCP.** As this lab demonstrates directly, Option 82 behavior can still break legitimate leases even with a textbook-correct trust boundary — always test end-to-end, don't just check `show ip dhcp snooping` and declare victory.
4. **Configuring the exclusion range *after* creating the pool**, or forgetting it uses global (not pool-scoped) syntax.
5. **Confusing `ip dhcp snooping trust` (a per-interface setting) with the global/VLAN-level `ip dhcp snooping` / `ip dhcp snooping vlan` commands** — all three are required together; any one alone is incomplete.
6. **Not checking the binding table when troubleshooting** — `show ip dhcp snooping binding` immediately tells you whether the client-side request even got acknowledged, narrowing down "is this a DHCP problem or a Snooping problem" fast.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC gets `0.0.0.0` / APIPA address | DHCP process not completing anywhere along the path | `show ip dhcp snooping` on each switch | Confirm snooping enabled + correct VLAN on every hop |
| 2 | Snooping enabled, VLAN correct, still fails | Wrong interface trusted (or none trusted) | `show ip dhcp snooping` (Trusted column) | Move `ip dhcp snooping trust` to the correct uplink-facing interface |
| 3 | Trust config verified correct, still fails | Option 82 insertion conflicting with a non-relay-aware DHCP server | `show running-config \| include information option` | `no ip dhcp snooping information option` on every snooping-enabled switch in the path |
| 4 | Lease works once, then fails on renewal | Binding table entry aged out or interface flapped | `show ip dhcp snooping binding` | Confirm lease time vs. renewal interval; re-trigger `ipconfig /renew` |
| 5 | R1 shows no bindings at all (`show ip dhcp binding` empty) | DHCP pool misconfigured, or DHCP Discover never reaching R1 | `show ip dhcp snooping binding` (switch side) vs. `show ip dhcp binding` (R1) | If switch-side binding is empty too, the break is on the client/switch side, not R1 |

---

## 10. Design Analysis

**Why this design over alternatives?**

- **Why enable snooping on both SW1 and SW2 instead of just the switch closest to the clients?** DHCP Snooping's protection is only as strong as its weakest untrusted hop — if SW1 (closer to the real server) were left unsnooped, a rogue server plugged into any of SW1's other ports could still inject Offers that SW2 would then treat as arriving from a "trusted-enough" upstream path. Defense needs to be continuous along the entire path, not just at the network edge closest to the attacker's likely entry point.
- **Why disable Option 82 instead of making R1 relay-agent-aware?** Making R1 (or an intermediate device) properly process Option 82 is the "correct" long-term fix in a network that wants the extra visibility Option 82 provides (knowing exactly which switch/port/VLAN a request originated from, useful for very large networks with real DHCP relay agents). For this lab's scale and R1's role as a directly-attached DHCP server rather than a multi-hop relay scenario, the extra information isn't needed, and disabling it is the simpler, correct-for-this-topology fix — a smaller network almost always should prefer the simpler fix unless the extra data has a concrete use.
- **Why not just statically assign every device's IP instead of using DHCP at all?** Static assignment eliminates the rogue-DHCP-server threat model entirely but doesn't scale — every new device, every guest laptop, every phone needs manual IP assignment, which is operationally unworkable past a handful of devices. DHCP Snooping is the standard answer that keeps DHCP's convenience while closing its biggest security gap.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...an engineer enables DHCP Snooping as a routine hardening pass and immediately gets flooded with "no internet" tickets — and the root cause turns out to be exactly this lab's Option 82 interaction, not a broken trust configuration.
- ...a security audit flags that any employee could plug in a consumer router and start handing out malicious DHCP leases, and DHCP Snooping plus a documented trust-boundary diagram is the concrete remediation.
- ...an incident responder needs to know "which device had IP 192.168.1.87 at 2:14pm last Tuesday" and the DHCP Snooping binding table (if logged/exported) is exactly that record.
- ...a network team is deploying Dynamic ARP Inspection (Day 51) and discovers it silently depends on DHCP Snooping already being enabled and populated correctly — this lab is a hard prerequisite, not an independent topic.

---

## 12. Stretch Goal

1. Re-enable Option 82 (`ip dhcp snooping information option`) and instead solve the topology's failure by configuring R1 as an actual DHCP relay-aware/trusted-Option-82 processor if your platform supports it — document what changed and whether it's a more "correct" long-term fix than disabling Option 82.
2. Add a rogue DHCP server (a second router with its own `ip dhcp pool`) attached to one of SW2's untrusted client ports, and confirm its Offers are dropped — capture the relevant `%DHCP_SNOOPING` syslog message.
3. Add rate-limiting (`ip dhcp snooping limit rate <pps>`) to the client-facing ports to mitigate a DHCP-starvation (exhaustion) attack in addition to the rogue-server defense this lab already covers, and explain in a sentence why starvation is a different threat from spoofing.

---

## 13. Self-Assessment

- [ ] Can you explain, from memory, why every switch port is untrusted by default under DHCP Snooping?
- [ ] Can you name the two commands required (global + VLAN) before any trust/untrust setting has effect?
- [ ] Can you explain what Option 82 is and why disabling it fixed this lab's DHCP failure?
- [ ] Could you draw the trust boundary for this topology from memory?
- [ ] Can you explain why the DHCP Snooping binding table matters beyond just DHCP itself (hint: Day 51)?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** DHCP Snooping fundamentals, trusted vs. untrusted interfaces, per-VLAN enforcement, the DHCP Snooping binding table, Option 82 relay-agent information insertion and its real-world interaction pitfalls.

**What I learned:** DHCP Snooping protects against rogue DHCP servers by default-denying every port and requiring explicit trust for the path back toward the legitimate server. Correctly configuring the trust boundary is necessary but not always *sufficient* — Option 82 was the actual blocker in this lab even after trust was configured perfectly, which is the single most valuable lesson here: security features can interact with existing forwarding behavior in ways that only show up in end-to-end testing, not in a review of the configuration alone.

**Skills practiced:** DHCP server configuration on Cisco IOS, DHCP Snooping global/VLAN/interface configuration, binding table interpretation, Option 82 troubleshooting, structured multi-hop DHCP failure diagnosis.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for an automated build using VyOS (R1), Open vSwitch (SW1/SW2), and Alpine Linux (PC1). Note: Open vSwitch does not implement Cisco-style `ip dhcp snooping` — the README documents this limitation and how to approximate binding-table behavior using `isc-dhcp-server` logs and manual MAC/IP tracking on the Alpine hosts instead.
