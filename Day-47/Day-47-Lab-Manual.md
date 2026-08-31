# Day 47 Lab Manual — Quality of Service (QoS), DSCP Marking & Traffic Classification

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Classify HTTPS, HTTP, and ICMP traffic on R1, mark each class with a distinct DSCP value, and enforce a bandwidth/priority policy outbound on R1's WAN interface. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity) touches queuing/QoS conceptually; QoS *configuration* itself is explicitly **not** an exam configuration objective, but Domain 4's "describe the concepts of ... QoS" line item is directly this lab. Treat this as a conceptual-fluency lab, not a command-memorization one. |
| **Prerequisites** | TCP/UDP port numbers (HTTP=80, HTTPS=443), basic IPv4 header structure, static routing between R1 and R2 already working. |
| **Time Estimate** | 1.5 – 2 hours. |
| **Difficulty** | ⭐⭐⭐☆☆ (Intermediate) — the CLI itself is short, but the concepts (classification vs. marking vs. queuing, DSCP-to-hex conversion) trip up first-timers more than the typing does. |

---

## 1. Lab Overview + Learning Objectives

This lab builds a two-router topology (R1—R2) carrying three traffic types from PC1 to SRV1: HTTPS, HTTP, and ICMP. R1 classifies each type with a `class-map`, assigns it differentiated treatment in a `policy-map`, and applies that policy outbound on its WAN-facing interface. Packet Tracer Simulation Mode is then used to inspect the DSCP field inside real packets and confirm the marking actually happened.

By the end you will be able to:

- Explain the difference between traffic **classification** and traffic **marking**
- Build `class-map` → `policy-map` → `service-policy` configurations from scratch
- Convert between DSCP names (AF31, AF32, CS2), decimal values, and hex values by hand
- Explain the difference between a `priority` queue and a `bandwidth` guarantee
- Verify QoS markings both from the CLI and by inspecting packets directly

---

## 2. Business Context

**Why would a real company do this?**

Picture a mid-sized company whose single WAN link between its HQ and a remote site carries everything: customer-facing HTTPS traffic, general web browsing, IT monitoring pings, video calls, and nightly backup jobs — all competing for the same finite bandwidth. Without QoS, a large backup job kicked off at 2pm can make a customer's HTTPS checkout page feel sluggish, because the router has no concept of "this packet matters more than that one" — it forwards everything first-come-first-served.

- **"Our checkout page needs to stay fast even when the link is busy"** → HTTPS gets a priority queue with a guaranteed minimum slice of bandwidth, so it's never fully starved by bulk traffic.
- **"Our monitoring system needs pings to get through so we know when something's down"** → ICMP gets its own guaranteed minimum, smaller than the two web classes but still protected, so "the network is fine but monitoring can't tell" never happens.
- **"We can't just buy more bandwidth every time this comes up"** → QoS is explicitly a policy tool, not a capacity tool — this lab's biggest lesson (Section 8.1 below) is that QoS decides *who goes first when the link is busy*, it does not create bandwidth from nothing.
- **"We need to be able to prove to a manager why HTTP and HTTPS aren't treated identically"** → this lab intentionally uses two different DSCP values (AF31 vs AF32) for two similar-looking traffic types, forcing you to articulate the business reason (checkout/security-sensitive traffic vs. general browsing) rather than lump both into one class out of laziness.

This is the exact conversation a network engineer has with an application owner during a "why is X slow" incident review — and being able to point at a `show policy-map interface` counter is far more persuasive than an opinion.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-47-Lab-QoS.png" alt="Day 47 QoS Topology" width="900">
</p>

```text
PC1 (192.168.0.10) -- SW1 -- R1(G0/0/1) ... R1(G0/0/0) === R2(G0/0/0) -- R2(G0/0/1) -- SRV1 (10.0.0.100)
                                                  ^
                                      QoS policy applied OUTBOUND here
```

The policy is applied only on R1's `G0/0/0` — traffic returning from SRV1 to PC1 is **not** marked by this lab's configuration, which is worth noticing: QoS direction matters, and this is a one-way policy by design (see Section 10).

---

## 4. IP Addressing Plan

This lab reuses a fixed addressing scheme rather than one you design — the interesting math here is DSCP arithmetic, not subnetting. Still, understand the plan:

| Device | Interface | Address | Mask |
|---|---|---|---|
| PC1 | NIC | 192.168.0.10 | /24 |
| R1 | G0/0/1 | 192.168.0.1 | /24 |
| R1 | G0/0/0 | 172.16.0.1 | /30 |
| R2 | G0/0/0 | 172.16.0.2 | /30 |
| R2 | G0/0/1 | 10.0.0.1 | /24 |
| SRV1 | NIC | 10.0.0.100 | /24 |

**Why sized this way:** the R1↔R2 link is a point-to-point transit between exactly two router interfaces, so it's a `/30` (2 usable hosts) — the same reasoning as Day 01 Section 4.1. The PC and server LANs are `/24`s sized for headroom.

### 4.1 DSCP "addressing" — the math that actually matters in this lab

DSCP is a 6-bit field inside the IPv4 header's former Type-of-Service byte, so its value space is 0–63. This lab uses three DSCP code points; work out the decimal and hex values by hand instead of memorizing them:

**AF31 (Assured Forwarding, class 3, drop precedence 1):** AF naming encodes class and drop precedence as `AFxy`, where `x` = class (1–4) and `y` = drop precedence (1–3, low is preferred). The decimal value formula is:

```text
DSCP = (class × 8) + (drop_precedence × 2)
AF31 = (3 × 8) + (1 × 2) = 24 + 2 = 26
```

Convert 26 to hex: `26 = 16 + 8 + 2 = 0001 1010₂ = 0x1A`.

**AF32 (class 3, drop precedence 2):**

```text
AF32 = (3 × 8) + (2 × 2) = 24 + 4 = 28
28 = 16 + 8 + 4 = 0001 1100₂ = 0x1C
```

**CS2 (Class Selector 2):** CS values are simpler — `CSn = n × 8`.

```text
CS2 = 2 × 8 = 16
16 = 0001 0000₂ = 0x10
```

| Traffic | DSCP Name | Decimal | Hex |
|---|---:|---:|---:|
| HTTPS | AF31 | 26 | 0x1A |
| HTTP | AF32 | 28 | 0x1C |
| ICMP | CS2 | 16 | 0x10 |

Notice AF31 (26) < AF32 (28) even though both are "class 3" — the lower drop-precedence value (AF31) is the one that survives congestion *first*, which lines up with giving HTTPS the priority queue.

---

## 5. Pre-Configuration Checklist

1. R1↔R2 static/default routing already functional, confirmed with a plain ping from PC1 to SRV1 before touching QoS.
2. Know which interface is the "outbound" edge for this policy: `R1 G0/0/0` (facing R2/WAN), not `G0/0/1` (facing the LAN).
3. Have Packet Tracer Simulation Mode ready — you'll need it to actually see DSCP values change, not just trust the config.
4. `jeremysitlab.com` (or the lab's configured DNS/HTTP target) reachable from PC1 for the HTTP/HTTPS traffic generation steps.

---

## 6. Configuration Tasks

### 6.1 Verify baseline connectivity

```text
PC1> ping 10.0.0.100
```

**Mode:** PC command prompt. Confirms the underlying routing is solid *before* QoS is layered on — QoS never fixes a reachability problem, and troubleshooting QoS on top of a broken path wastes time diagnosing the wrong layer.

### 6.2 Build the classification (`class-map`) — identify what a packet *is*

```text
R1(config)#class-map match-all HTTPS_MAP
R1(config-cmap)#match protocol https
R1(config-cmap)#exit
R1(config)#class-map match-all HTTP_MAP
R1(config-cmap)#match protocol http
R1(config-cmap)#exit
R1(config)#class-map match-all ICMP_MAP
R1(config-cmap)#match protocol icmp
R1(config-cmap)#exit
```

**Mode:** Global Config → class-map sub-mode. **What it does:** each `class-map` is a named filter that answers "does this packet belong to me?" — `match-all` means every match condition listed must be true (here there's only one condition each, so it's a simple pass/fail on protocol). **Why it matters:** you cannot mark or queue what you haven't first identified — classification is always step one. **Memory aid:** class-map = "what is it," policy-map (next) = "what do I do about it."

### 6.3 Build the treatment (`policy-map`) — decide what happens to each class

```text
R1(config)#policy-map G0/0/0_OUT
R1(config-pmap)#class HTTPS_MAP
R1(config-pmap-c)#priority percent 10
R1(config-pmap-c)#set ip dscp af31
R1(config-pmap-c)#exit
R1(config-pmap)#class HTTP_MAP
R1(config-pmap-c)#bandwidth percent 10
R1(config-pmap-c)#set ip dscp af32
R1(config-pmap-c)#exit
R1(config-pmap)#class ICMP_MAP
R1(config-pmap-c)#bandwidth percent 5
R1(config-pmap-c)#set ip dscp cs2
R1(config-pmap-c)#exit
R1(config-pmap)#exit
```

**Mode:** Global Config → policy-map → class sub-mode. **`priority percent 10`** creates a strict low-latency priority queue guaranteed (and capped at) 10% of the link — used for HTTPS because checkout/security-sensitive traffic is treated as delay-sensitive in this design. **`bandwidth percent`** is a *minimum guarantee*, not a hard cap or a priority queue — HTTP and ICMP get "at least this much when congested" rather than jump-the-line treatment. **`set ip dscp`** rewrites the DSCP field in the IP header to the value computed in Section 4.1. **Why it matters:** this is the actual decision-making logic of the whole lab — everything before this step only identified traffic, this step is where differentiated treatment is defined. **Memory aid:** "priority for the pickiest, bandwidth-percent for everyone else."

### 6.4 Apply the policy to an interface — nothing happens until this step

```text
R1(config)#interface gigabitEthernet 0/0/0
R1(config-if)#service-policy output G0/0/0_OUT
R1(config-if)#exit
```

**Mode:** Interface config. **What it does:** attaches the policy-map to actual traffic flow, in the outbound direction, on this specific interface. **Why it matters:** a `policy-map` with no `service-policy` applied is inert — this is the single most common way this lab "doesn't work" (see Common Mistakes). **Why outbound, why this interface:** the requirement was to shape traffic as it leaves R1 toward R2/WAN — inbound policies exist too, but this lab is specifically an egress-shaping scenario, which is the far more common real-world case (shaping what you send onto a link you don't fully control the far end of).

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show policy-map` | Policy-map exists with all 3 classes and correct actions |
| `show policy-map interface g0/0/0` | Policy is attached, packet/byte counters incrementing per class |
| `show running-config \| section policy` | Full applied config, sanity check against Section 6 |
| `show running-config \| section class-map` | Class-map match statements correct |

### 7.1 Expected Output Gallery

**`R1# show policy-map interface g0/0/0`** (after generating some HTTP/HTTPS/ICMP traffic)

```text
GigabitEthernet0/0/0

  Service-policy output: G0/0/0_OUT

    Class-map: HTTPS_MAP (match-all)
      6 packets, 612 bytes
      Match: protocol https
      priority 10%
      Set ip dscp af31

    Class-map: HTTP_MAP (match-all)
      4 packets, 388 bytes
      Match: protocol http
      bandwidth 10%
      Set ip dscp af32

    Class-map: ICMP_MAP (match-all)
      4 packets, 256 bytes
      Match: protocol icmp
      bandwidth 5%
      Set ip dscp cs2

    Class-map: class-default (match-any)
      0 packets, 0 bytes
```

Non-zero packet counters per class prove classification is actually matching live traffic, not just sitting in the config unused.

**Packet Tracer packet inspection — ICMP echo, PDU details:**

```text
IP Header
  DSCP: 0x10 (16)
  Protocol: ICMP
```

**HTTP GET packet:**

```text
IP Header
  DSCP: 0x1C (28)
TCP Header
  Destination Port: 80
```

**HTTPS packet:**

```text
IP Header
  DSCP: 0x1A (26)
TCP Header
  Destination Port: 443
```

If any of these three show `DSCP: 0x00`, the marking never happened for that traffic type — see Troubleshooting.

---

## 8. Common Mistakes (80/20 rule)

1. **Building the class-map and policy-map but forgetting `service-policy output ...` on the interface.** The most common failure — config is syntactically perfect and does nothing.
2. **Applying the policy `input` instead of `output`, or on the wrong interface** (`G0/0/1`, the LAN side, instead of `G0/0/0`, the WAN side). Direction and interface both matter — a `service-policy input` on `G0/0/0` marks traffic arriving *from* R2, not leaving toward it.
3. **Confusing `priority percent` with `bandwidth percent`.** Using `bandwidth` for HTTPS won't create a genuine low-latency queue — it only guarantees a minimum share, no jump-the-line behavior.
4. **Mistyping `match protocol https` as `match protocol http` for the HTTPS class-map** (or vice versa) — both classes then silently misclassify, and you won't notice until you inspect actual DSCP values in Simulation Mode.
5. **Forgetting `match-all` vs `match-any` distinction** — with only one match condition per class here it's moot, but the habit of specifying it matters once class-maps grow more conditions.
6. **Assuming class-map order in the policy-map doesn't matter.** It generally does for NBAR-classified traffic priority resolution when multiple classes could match — always list the most specific/highest-priority class first.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | DSCP stays 0x00 for all traffic | Policy never applied to an interface | `show policy-map interface g0/0/0` | Add `service-policy output G0/0/0_OUT` under the interface |
| 2 | HTTPS not marked, HTTP is | `match protocol https` typo or missing | `show running-config \| section class-map` | Correct the `match protocol` line |
| 3 | Marking correct but no priority behavior visible | Used `bandwidth` instead of `priority` for HTTPS | `show policy-map` | Change `bandwidth percent 10` to `priority percent 10` under HTTPS_MAP class |
| 4 | Return traffic (SRV1→PC1) unmarked | Expected — policy is outbound-only on R1 G0/0/0 | `show policy-map interface g0/0/0` (input side) | Not a bug; add a second policy on R2 if return-path marking is desired |
| 5 | Class-map packet counters stay 0 despite traffic flowing | Wrong interface, wrong direction, or traffic not actually matching the protocol (e.g., HTTPS redirected to HTTP) | `show policy-map interface` | Confirm actual traffic type in Simulation Mode PDU details |

---

## 10. Design Analysis

**Why this design over alternatives?**

- **Why NBAR-style `match protocol` instead of ACL-based classification?** `match protocol https/http/icmp` uses Cisco's built-in protocol recognition, which is simpler to write and read than an equivalent `access-list permit tcp any any eq 443` + `class-map match access-group`. For well-known ports, protocol matching is both more explicit in intent and less error-prone.
- **Why give HTTPS a priority queue but not HTTP?** Both are "web" traffic, but the business reasoning (Section 2) treats HTTPS as carrying more delay-sensitive, often transactional traffic (login, checkout) — general HTTP browsing tolerates a little queuing delay without a user-visible problem. This is a deliberate business decision encoded in the config, not a technical requirement of the protocols themselves.
- **Why mark ICMP at all?** Many networks are tempted to treat ICMP as low-priority "noise," but it's frequently the transport for uptime/latency monitoring — starving it entirely can blind ops teams exactly when the network is under the stress they need to observe. A modest 5% guarantee balances "don't let ping dominate the link" against "don't let monitoring go blind."
- **Why apply the policy only outbound on R1, not also inbound or on R2?** This lab is scoped to demonstrate the classify→mark pipeline once, cleanly. Real deployments typically mark once as close to the traffic source as possible ("mark at the edge, trust the marking downstream") and configure queuing policies (not necessarily re-marking) at each subsequent hop — which is exactly the kind of extension proposed in the Stretch Goal.

---

## 11. Real-World Parallel

**You'd see this when...**

- ...a company's single MPLS or broadband WAN link needs voice, video, and bulk file transfer to coexist without VoIP calls dropping every time someone kicks off a backup.
- ...a SaaS company wants to guarantee their customer-facing HTTPS API stays responsive even during a DDoS-adjacent traffic spike of unrelated HTTP scraping traffic.
- ...a network engineer is asked "why is monitoring flaky during business hours" and the root cause turns out to be ICMP getting zero bandwidth guarantee on a congested link.
- ...an auditor asks to see evidence that "critical traffic is prioritized" as part of a compliance framework, and `show policy-map interface` with non-zero counters is exactly that evidence.

---

## 12. Stretch Goal

1. Add a fourth class for `SSH` or `DNS` traffic marked as `CS6` (control-plane-equivalent priority) and justify the choice in a sentence.
2. Apply a second, inbound-focused policy on R2's `G0/0/0` that trusts (does not re-mark) DSCP values already set by R1 — this models the "mark once at the edge, trust downstream" pattern used in real WANs.
3. Change HTTP's `bandwidth percent 10` to a hard `police` rate instead, and explain in your own words the difference between "guarantee a minimum" and "cap a maximum."
4. Predict, then test, what `show policy-map interface` looks like if you send only ICMP traffic and no HTTP/HTTPS at all — does HTTP's guaranteed 10% get "stolen" by ICMP, or sit idle?

---

## 13. Self-Assessment

- [ ] Can you compute the decimal and hex value of AF33 and CS4 from the formulas in Section 4.1 without looking them up?
- [ ] Can you explain, without notes, the difference between `priority percent` and `bandwidth percent`?
- [ ] Can you state which two CLI steps are required before a `service-policy` command has any effect?
- [ ] Could you explain to a non-technical manager why HTTP and HTTPS receive different treatment in this lab?
- [ ] Can you name the interface and direction this lab's policy was applied to, and explain why that specific combination was chosen?

---

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key concepts:** classification vs. marking vs. queuing as three distinct QoS operations; DSCP encoding (AF and CS naming conventions); the `class-map` → `policy-map` → `service-policy` hierarchy; priority queuing vs. bandwidth guarantees; direction- and interface-specific policy application.

**What I learned:** QoS does not create bandwidth — it decides who wins when bandwidth is contested. Classification always comes first; nothing downstream (marking, queuing) can happen for traffic that was never correctly identified. The DSCP field is directly inspectable in the IP header, which turns an abstract "trust me it's prioritized" claim into a verifiable fact via Simulation Mode or `show policy-map interface` counters.

**Skills practiced:** traffic classification and marking, DSCP-to-decimal-to-hex conversion, Cisco IOS QoS configuration (`class-map`, `policy-map`, `service-policy`), packet-level verification, business-driven QoS policy design.

---

## 15. GNS3 Lab

See [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md) for an automated build of this topology using VyOS routers and Alpine Linux end hosts. Note VyOS's QoS/traffic-policy syntax differs substantially from IOS `class-map`/`policy-map` (VyOS uses `traffic-policy` with `class` blocks under `set traffic-policy shaper ...`) — the GNS3 README maps the underlying concepts (classification, marking, priority queue vs. bandwidth share) across both syntaxes so the *concepts* transfer even though commands don't.
