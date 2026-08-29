# Day 11.2 Practice Lab — Troubleshooting Static Routes (Self-Guided)

Companion to [`Day-11.2-Lab-Manual.md`](Day-11.2-Lab-Manual.md). Same faulted topology, no answers given upfront — work through the diagnosis yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 45–60 minutes |
| **What you'll need** | Your working Day 11.1 topology, and either a lab partner to seed faults for you or the discipline to seed them yourself and "forget" where |

---

## 1. The Brief

> Somewhere in your 3-router static routing topology, three faults have been introduced — one per router. PC1 cannot reach PC2. You don't know which router has which fault, or what type of fault it is (routing, addressing, or interface state). Find and fix all three using only `show` commands, one router at a time, in path order.

### Your task

- [ ] Before touching any device, write down the order you'll inspect routers in, and why that order makes sense.
- [ ] List every `show` command you know that could reveal a routing or interface fault, before you start using them.

---

## 2. Seed the Faults

Either ask someone else to modify your Day 11.1 topology, or do it yourself and then take a 10-minute break before returning to diagnose — don't rely on memory of what you changed.

Suggested fault categories (pick one per router, don't tell yourself which):

- A static route pointing at the wrong destination network
- A static route missing entirely in one direction
- An interface IP address that doesn't match the addressing plan

---

## 3. Diagnose — Step by Step

For **each** router in path order:

- [ ] Run the interface-status command. Does every interface match your known-good addressing plan exactly?
- [ ] Run the routing-table command. Does every expected static route appear, with the correct destination network and next-hop?
- [ ] If you find a discrepancy, write down: what you expected, what you saw, and what command revealed it — before fixing anything.

---

## 4. Fix — One Change at a Time

- [ ] For each fault found, apply the *minimum* corrective change (don't reconfigure the whole device).
- [ ] Re-test end-to-end connectivity after **each individual fix**, not just once at the end. Did the symptom change? How?

---

## 5. Explain Your Process

Answer without the manual:

1. Why is it important to check interface status *before* assuming a problem is routing-related?
2. What's the risk of retyping a device's entire configuration instead of fixing one specific line?
3. If PC1 → PC2 fails but PC2 → PC1 succeeds, what does that asymmetry tell you about where the fault likely is?
4. Why is testing after each fix better than testing once at the very end?

---

## 6. Self-Check

- [ ] I diagnosed all three faults using only `show` commands, without guessing or randomly reconfiguring devices.
- [ ] I found at least one fault that was NOT a routing-table problem (i.e., the interface-layer one).
- [ ] I applied minimal, targeted fixes and re-verified after each one.
- [ ] I can explain my diagnostic order and reasoning to someone else.

Once done, open [`Day-11.2-Lab-Manual.md`](Day-11.2-Lab-Manual.md) and compare your diagnostic process against Sections 6 and 9.
