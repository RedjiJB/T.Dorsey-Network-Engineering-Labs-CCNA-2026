# Day 21 Practice Lab — Configuring Spanning Tree (Self-Guided)

No-answers companion to `Day-21-Lab-Manual.md`.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–2.5 hours. |
| **What you'll need** | Your Day 20 topology (or a fresh four-switch, two-VLAN build), an IOS-based switch image if possible. |

---

## 1. The Brief

> You have a four-switch, two-VLAN topology with default STP settings. Your job: make SW1 the primary root for VLAN1 and secondary root for VLAN2; make SW2 the primary root for VLAN2 and secondary root for VLAN1. Then test whether you can influence a specific non-root switch's root port selection using cost, and separately using port priority. Finally, harden two access ports against rogue STP participants.

### Your task

- [ ] Before touching any configuration, capture the current root bridge and every port's role/state for both VLANs on all four switches — this is your baseline. Without this, you won't be able to prove any later change actually did something.

---

## 2. Predict Before You Configure

1. What priority values do you expect `spanning-tree vlan 1 root primary` to set on SW1? Do you need to calculate this by hand, or does IOS do it automatically? What if some other switch already has a lower priority — what happens then?
2. For the interface cost change you're about to make on one switch: before typing the command, work out that switch's current root port and its total path cost. Then work out the *next-best* alternative path's total cost. Will raising the current root port's cost by 100 actually change anything? Predict yes or no, and why.
3. For the port priority change: is there an existing cost tie anywhere in your topology that a priority change could actually break? If not, predict that the change will have zero visible effect.

---

## 3. Configure — Prompts Only

### 3.1 Root bridge assignment

- [ ] Configure SW1 and SW2 with the primary/secondary root relationship described in the brief. What command accomplishes this without you calculating exact priority numbers?

### 3.2 Cost-based influence

- [ ] Apply your planned cost change to the interface and switch you predicted about in Section 2, Question 2.

### 3.3 Priority-based influence

- [ ] Apply your planned port-priority change to the interface and switch you predicted about in Section 2, Question 3.

### 3.4 Edge port hardening

- [ ] Choose two access ports (one per switch, on switches that should never see another switch connected) and apply both PortFast and BPDU Guard. Why do both commands need to be present together, rather than just one?

---

## 4. Verify — Compare Against Your Predictions

- [ ] Compare the post-configuration root bridge and port roles against your Section 1 baseline. What changed, and does it match what `root primary`/`root secondary` should do?
- [ ] Check whether your cost change actually altered the root port, and compare against your Question 2 prediction. If you were wrong, work out why by computing the actual path costs involved.
- [ ] Check whether your port priority change altered anything, and compare against your Question 3 prediction.
- [ ] Verify PortFast and BPDU Guard are both present with `show running-config interface <id>`.

---

## 5. Explain Your Design

1. What are the exact priority values `root primary` and `root secondary` set, and why does IOS use macros instead of requiring you to calculate them?
2. Why can a cost change on one interface produce zero visible effect, and why is that outcome still useful information rather than a failed experiment?
3. In STP's comparison order (Bridge ID, path cost, sender Bridge ID, port priority, port ID), where does port priority sit, and what does that tell you about when it actually matters?
4. Why is PortFast dangerous on a port that connects to another switch?
5. What specifically does BPDU Guard enforce that PortFast alone does not?

---

## 6. Troubleshoot Yourself

Break your lab in 3 of these ways and diagnose using only `show` commands:

- Apply PortFast to a port that connects to another switch (in a lab environment only — never in production) and observe what STP theory says could go wrong, even if your simulator doesn't fully model the risk.
- Configure a rogue "switch" (or a device sending BPDUs) into a BPDU-Guard-protected port and walk through the resulting err-disable state and recovery.
- Set conflicting root primary commands on two different switches for the same VLAN and observe what happens.

---

## 7. Self-Check

- [ ] I captured a full baseline before making any changes.
- [ ] I predicted the outcome of every cost/priority change before applying it, and understood any mismatch between prediction and reality.
- [ ] I configured root bridges, cost, port priority, PortFast, and BPDU Guard from memory/lookup.
- [ ] I can answer all 5 questions in Section 5 out loud.

Once done, open `Day-21-Lab-Manual.md` and diff your work against Sections 6, 8, and 9.
