# Day 27 Practice Lab — OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

Self-derivation companion to the Day 27 Lab Manual. No CLI commands are given — work through the math and reasoning yourself first. This lab reuses the Day 26 topology, so review that practice lab's addressing derivation if you need a refresher.

---

## Brief

The same four-router-plus-ASBR OSPF domain from Day 26 has a problem: FastEthernet and Gigabit Ethernet interfaces both show OSPF cost 1, meaning OSPF cannot tell them apart. You need to fix the reference bandwidth domain-wide, verify the corrected costs, and understand exactly what's inside an OSPF Hello packet.

## Topology

Same as Day 26:
```text
ISP -- R1 (ASBR)
           /   \
         R2     R3
           \   /
            R4 -- SW1 -- PC1
```

---

## Part 1 — Diagnose the Problem

1. Write out OSPF's cost formula from memory. What is the default reference bandwidth value?
2. Using the default reference bandwidth, compute the cost of a FastEthernet (100 Mbps) interface and a GigabitEthernet (1000 Mbps) interface. What do you notice, and why is it a problem for path selection?
3. OSPF cost is always a whole number with a floor of 1 — it never rounds to 0. Given that rule, what happens to a 10 Gbps interface's cost if the reference bandwidth is still at the default 100 Mbps?

---

## Part 2 — Derive the Fix

1. You want FastEthernet (100 Mbps) to land on a cost of exactly 100. Set up the equation `100 = ReferenceBandwidth / 100` and solve for the reference bandwidth in Mbps.
2. Using the reference bandwidth you just derived, compute the cost for: GigabitEthernet (1000 Mbps), a T1 serial link (1.544 Mbps), and a 10 Gbps interface. Show your work for each.
3. If your network core actually included some 10 Gbps and 40 Gbps links, would 10000 (10 Gbps) still be a good reference bandwidth choice? What problem would recur, and what value would you choose instead?

---

## Part 3 — Domain-Wide Consistency

1. What specific IOS warning message appears the moment you change `auto-cost reference-bandwidth` on a router? What is it actually warning you about?
2. If R1 is set to reference bandwidth 10000 but R4 is still at the default 100, describe concretely what goes wrong — not just "it's inconsistent," but what a router on each side would calculate differently for the *same physical link*, and what routing decision could go wrong as a result.
3. What operational practice (in terms of change management, not CLI syntax) prevents this problem in a real network with a dozen routers?

---

## Part 4 — Hello Packet Fields

Without looking at a reference, try to recall or reason out:

1. What are the default Hello interval and Dead interval values on a broadcast network type? What's the mathematical relationship between them?
2. What field in the Hello packet must match exactly between two routers for an adjacency to even be considered, let alone form?
3. What does it mean for adjacency formation to be "bidirectional," and what specific field in the Hello packet is the mechanism that proves bidirectionality?
4. What is Router Priority used for, and what does a priority of 0 mean?

---

## Part 5 — Predict Before Verifying

1. After applying reference bandwidth 10000 domain-wide, predict what `show ip ospf interface f1/0` will show for Cost on a FastEthernet link, and what `show ip ospf interface g0/0` will show for a Gigabit link.
2. On R4, predict how the `[110/X]` bracket values in `show ip route` will change compared to before the reference bandwidth fix. Will the *paths chosen* necessarily change, or just the displayed cost numbers? Under what circumstance would the actual best-path choice change?

---

## Part 6 — Troubleshooting Scenarios

For each, state your first diagnostic command and reasoning:

1. After changing reference bandwidth on all four routers, an OSPF adjacency that was previously stable drops.
2. `show ip ospf interface` on R1 shows the new cost, but on R4 the same link type still shows the old cost.
3. Two routers with matching Area IDs and matching reference bandwidth still fail to form an adjacency.

---

## Self-Check Checklist

- [ ] I derived the reference-bandwidth-10000 fix from the cost formula myself, without looking at the manual first
- [ ] I correctly predicted what happens to a 10G link's cost under a too-low reference bandwidth
- [ ] I correctly explained the domain-wide-consistency danger in concrete terms, not just "it's inconsistent"
- [ ] I recalled the default Hello/Dead intervals and their 4x relationship without checking
- [ ] I correctly identified the bidirectional-adjacency mechanism (neighbor list containing your own Router ID)
- [ ] I worked through all three troubleshooting scenarios before reading the manual's troubleshooting table
