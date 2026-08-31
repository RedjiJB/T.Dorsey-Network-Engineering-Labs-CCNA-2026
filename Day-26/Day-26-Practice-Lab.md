# Day 26 Practice Lab — OSPF ASBR Default Route Injection and Passive Interface Design

Self-derivation companion to the Day 26 Lab Manual. No addressing plan and no CLI commands — derive them yourself first.

---

## Brief

R1 sits between an ISP edge router and a four-router internal OSPF domain (R1–R4). You need OSPF running internally, R1's ISP link deliberately excluded from OSPF, and R1 configured to inject a default route so R2/R3/R4 don't need any static configuration to reach the Internet.

## Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-26-Lab-OSPF-(Part%201).png" alt="Day 26 OSPF ASBR Lab" width="900">
</p>

```text
ISPR1 -- R1 (ASBR)
             /   \
           R2     R3
             \   /
              R4 -- SW1 -- PC1
```

---

## Part 1 — Derive the Addressing and Wildcard Masks

1. Derive the subnet mask for each router-to-router link (all point-to-point) using the host-bits formula.
2. OSPF `network` statements use a wildcard mask, not a subnet mask. Given a /30 subnet mask, derive the wildcard mask by inverting each octet. Show your work.
3. Do the same conversion for the R4 LAN's /24.
4. What wildcard mask does a loopback's /32 always use, and why does that make intuitive sense given what a wildcard mask actually represents (which bits are allowed to vary vs. must match exactly)?

---

## Part 2 — Reasoning About Exclusion

1. R1's link to ISPR1 must never run OSPF. Name two different CLI approaches that could accomplish this, and explain the practical difference between them (hint: one is purely "don't mention it," the other is an explicit statement of intent).
2. Why is it a security/stability concern, not just a configuration nicety, to let OSPF form an adjacency across R1's ISP-facing link?

---

## Part 3 — ASBR and Default-Route Injection

1. R1 has a static default route pointing at the ISP. What single OSPF command makes R2, R3, and R4 automatically learn "send unrecognized traffic toward R1," without any static configuration on their end?
2. This command has a gotcha: under what specific condition does it succeed as a command but produce zero actual effect (no LSA generated)? What variant of the command removes that condition, and what new risk does that variant introduce?
3. What LSA type does OSPF use to advertise an externally-injected default route? What does `show ip ospf` on R1 say to confirm R1 has become an ASBR?
4. Downstream routers show the default route with a specific route-type flag in `show ip route`. What is it, and what does the letter/number combination mean?

---

## Part 4 — E1 vs E2 Reasoning

1. What's the practical difference between how an E1 metric and an E2 metric are calculated as an external route propagates further from the ASBR?
2. In this lab's specific topology (R2 and R3 both exactly one hop from R1), would you expect E1 and E2 to produce different path preference for R4's default route? Why or why not?
3. Describe a topology change (add a detail — a second ASBR, or make one internal path longer than another) that WOULD make E1 vs E2 produce genuinely different routing behavior. Explain what would go wrong with E2 in that scenario.

---

## Part 5 — Predict the Routing Tables

Before checking the manual, sketch (in your own words, not full CLI syntax) what you expect `show ip route` to show on R4 for the default route entry, given that R4 has two internal paths back toward R1 (via R2 and via R3) with identical cost. What OSPF behavior does this demonstrate, and does it require any special configuration to enable?

---

## Part 6 — Troubleshooting Scenarios

For each, state your first diagnostic command and reasoning:

1. `default-information originate` is configured on R1, but R2 shows no `O*E2` route at all.
2. R1's `show ip ospf` doesn't say "It is an autonomous system boundary router" even though you configured the origination command.
3. An OSPF neighbor relationship unexpectedly forms across R1's link toward ISPR1.
4. R4 only shows the default route via one path (through R2), when you expected two.

---

## Self-Check Checklist

- [ ] I derived every wildcard mask by hand without checking the manual first
- [ ] I correctly explained why `default-information originate` can silently do nothing
- [ ] I identified the LSA type and the ASBR confirmation message unaided
- [ ] I correctly reasoned through when E1 vs E2 actually changes routing behavior
- [ ] I predicted the equal-cost multipath default route on R4 before reading the manual
- [ ] I worked through all four troubleshooting scenarios before reading the manual's troubleshooting table
