# Day 52 Practice Lab — STP & HSRP Synchronization (Self-Guided)

No-answers companion to `Day-52-Lab-Manual.md`. Same topology and brief, prompts only.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–2.5 hours. This is a design-reasoning lab as much as a config lab — budget real thinking time, not just typing time. |
| **What you'll need** | Packet Tracer/GNS3, two distribution switches, VLANs 10 and 20 already trunked. |

---

## 1. The Brief

> Two distribution switches, DSW1 and DSW2, serve VLAN 10 and VLAN 20. You want both switches doing real work under normal conditions — not one idle backup — so split gateway responsibility: one switch should be the primary gateway for VLAN 10, the other for VLAN 20. Whichever switch is the "primary" for a VLAN's gateway should also be the Layer 2 root for that VLAN's spanning tree, so traffic doesn't take an unnecessary extra hop across the inter-switch trunk before reaching its actual gateway.

### Your task

- [ ] Before configuring anything, draw a table: for each VLAN, which switch is the HSRP active router, and which switch is the STP root? (This should be two rows, with roles deliberately flipped between them — work out why before checking the manual.)
- [ ] Write in your own words why "the HSRP active switch should also be the STP root for that VLAN" is actually a real technical requirement, not just tidiness.

---

## 2. Design the Addressing — By Hand

1. Choose a `/24` for VLAN 10 and a different `/24` for VLAN 20.
2. Each VLAN needs three addresses at the distribution layer: two real SVI addresses (one per switch) and one shared virtual IP that both switches present together. Pick a convention for where in the subnet these three addresses live (and stick to it for both VLANs).
3. Write out, for VLAN 10, the network address, first usable host, last usable host, and broadcast address by hand.

---

## 3. Configure — Prompts Only

### 3.1 HSRP for VLAN 10

- [ ] What command creates an HSRP group with a specific virtual IP on an SVI?
- [ ] Which of the two switches should get the *higher* priority value, given your Part 1 table? What's the actual comparison rule — does HSRP prefer higher or lower priority?
- [ ] What single keyword allows a recovering higher-priority router to reclaim the active role instead of staying standby forever? Why is skipping this keyword a real operational risk, not just a cosmetic gap?

### 3.2 HSRP for VLAN 20 — flipped roles

- [ ] Configure the same three elements as 3.1, but with the active/standby roles reversed between the two switches. Should you reuse HSRP group 1, or use a different group number? Why?

### 3.3 STP root alignment

- [ ] For VLAN 10, which switch needs to become the STP root, based on your Part 1 table? What single command sets this without requiring you to manually calculate a numeric bridge priority?
- [ ] What's the complementary command for the other switch, so it's positioned as an intentional fallback rather than an accidental one?
- [ ] Repeat for VLAN 20 — note this should be the *opposite* switch from VLAN 10's root.
- [ ] Does STP prefer higher or lower priority values? How does this compare to HSRP's rule from 3.1?

---

## 4. Verify — Predict First

- [ ] Before running it, predict what `show standby brief` will show for DSW1 across both VLANs — Active for one, Standby for the other. Write your prediction, then check.
- [ ] Predict what `show spanning-tree vlan 10` will say on DSW2 (the switch that should NOT be VLAN 10's root) — what specific line or field tells you it's not the root, and what does it show instead?
- [ ] Confirm your predictions match for all four combinations (2 switches × 2 VLANs, root and HSRP state each).

---

## 5. Explain Your Design

1. Why split HSRP active responsibility per-VLAN instead of making one switch the gateway for everything?
2. Explain, concretely, what extra hop happens on the network if STP root and HSRP active for the same VLAN end up on different switches. Where does the packet actually go that it wouldn't need to?
3. Why does HSRP use "higher priority wins" while STP uses "lower priority wins"? (You don't need historical trivia — just be able to state that they're opposite and not mix them up.)
4. What does `preempt` actually change about failover *and* fail-back behavior? What would you observe differently with it disabled?
5. Why might `spanning-tree vlan X root primary` not always produce the priority value you expect?

---

## 6. Troubleshoot Yourself

Break your lab 2–3 ways, diagnose with `show` commands only, then fix:

- Remove `preempt` from the higher-priority HSRP router, force a failover, then bring it back and observe it does NOT reclaim active status.
- Set `root primary` on the wrong switch for one VLAN (misaligning it with the HSRP-active switch), then use `show spanning-tree` and `show standby brief` together to spot the misalignment.
- Use mismatched virtual IPs between the two switches for the same HSRP group and observe what breaks.

---

## 7. Self-Check

- [ ] I designed the full per-VLAN role table myself before checking the manual.
- [ ] I calculated the addressing plan by hand.
- [ ] I configured HSRP and STP root alignment from memory/reasoning, not by copying the manual.
- [ ] I predicted verification output before running each command, for all four switch/VLAN combinations.
- [ ] I could explain all 5 design questions in Section 5 out loud.
- [ ] I broke and fixed at least 2 things myself.

Once complete, open `Day-52-Lab-Manual.md` and diff against Sections 6, 7, and 9.
