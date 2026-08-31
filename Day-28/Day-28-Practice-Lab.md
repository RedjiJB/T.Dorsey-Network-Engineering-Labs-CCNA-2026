# Day 28 Practice Lab — OSPF Troubleshooting: Serial Links, Neighbor Failures, and Missing Routes

Self-derivation companion to the Day 28 Lab Manual. This is a troubleshooting lab, so the "practice" format here works differently: instead of deriving an addressing plan, you'll practice the diagnostic reasoning itself — predicting root causes and fixes before checking the manual's answers.

---

## Brief

A pre-configured 5-router OSPF network (R1–R5, two PCs, three switches) has five real, silent problems. You are the engineer brought in to diagnose and repair — not rebuild.

## Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-28-Lab-OSPF-(Part%203).png" alt="Day 28 OSPF Troubleshooting Lab" width="900">
</p>

```text
PC1 -- SW1 -- R1 ===Serial=== R2 --+
                |                   \
             (to R5, serial)         SW3 (multi-access) -- R4 -- SW2 -- PC2 -- R3
                |                   /                              |
               R5 ------------------                              R3
```

---

## Part 1 — Derive the SW3 Segment Addressing

1. Three routers (R2, R4, R5) share the SW3 multi-access segment today, with headroom planned for a fourth. Using `2^h − 2 ≥ hosts`, derive the prefix length.
2. Derive the subnet mask in binary, then decimal.
3. Convert that subnet mask to its OSPF wildcard mask.
4. Write out the network address, first usable host, last usable host, and broadcast address for 192.168.245.0 at your derived prefix.

---

## Part 2 — Diagnose Before Reading: Scenario 1 (New Serial Link)

R1 and R2 have a newly cabled serial link between them. Both interfaces have IP addresses configured and `no shutdown` applied, but no OSPF adjacency ever forms.

1. What is the first command you'd run, and what specific field in its output distinguishes "administratively up" from "actually passing traffic"?
2. Back-to-back serial links (no service provider in between) require one specific piece of configuration that a provider-supplied circuit would normally handle for you. What is it, which side needs it, and why does the other side not need it?
3. Predict the fix in full CLI syntax before checking the manual.

---

## Part 3 — Diagnose Before Reading: Scenario 2 (Missing Route)

Every router except R3 is missing a route to R3's own LAN, 10.0.2.0/24.

1. Where would you look first — on the routers that are missing the route, or on R3 itself? Justify your answer.
2. What specific command reveals exactly which networks a router's OSPF process has been told to advertise?
3. Name two different ways a `network` statement could fail to cover an interface even though it "looks close" — one is a missing statement entirely, the other is a subtler mistake. What is it?

---

## Part 4 — Diagnose Before Reading: Scenario 3 (Silent Neighbor Failure)

R2, R4, and R5 all sit on the same Layer 2 switched segment (SW3) and should all become OSPF neighbors with each other. R5 shows zero neighbors.

1. List at least three distinct root causes that could produce this exact symptom (no adjacency, no error message).
2. Of those, which one is described in networking folklore as "the single most common silent OSPF neighbor killer," and why does it produce literally no error message on either side?
3. What command would you run on each of the three routers to check for this specific cause?

---

## Part 5 — Diagnose Before Reading: Scenario 4 (No Internet)

PC1 and PC2 can reach every internal subnet but cannot reach 8.8.8.8, an external target reachable via R5.

1. Default-route injection into OSPF requires two separate, independent pieces of configuration on the ASBR. Name both, and explain what happens if only one is present.
2. Which command would confirm the ASBR's own default route exists locally, and which command would confirm it's actually being advertised into OSPF as an external LSA?

---

## Part 6 — LSDB Reasoning

1. Given a 5-router OSPF area with exactly one multi-access (switched) segment and one router injecting a single default route, how many Type-1, Type-2, and Type-5 LSAs would you expect to see in `show ip ospf database`? Explain your reasoning for each count.
2. If you counted only 4 Type-1 LSAs instead of the expected 5, what would that tell you about the state of the domain — even if every routing table you'd checked individually looked fine?

---

## Self-Check Checklist

- [ ] I derived the SW3 /29 addressing and wildcard mask by hand before checking the manual
- [ ] I correctly identified the DCE/DTE clocking issue and which side needs `clock rate`
- [ ] I correctly reasoned through the missing-route diagnosis path (advertising router first, not the receiving routers)
- [ ] I named area-ID mismatch as a likely cause of the silent neighbor failure, with reasoning for why it's silent
- [ ] I correctly named both halves of default-route injection into OSPF
- [ ] I correctly predicted the expected LSA counts for this topology before reading the manual
