# Day 22 Practice Lab — RSTP: Root Bridge Behavior and Link Types (Self-Guided)

Companion to [`Day-22-Lab-Manual.md`](Day-22-Lab-Manual.md). Same topology and questions, no answers given upfront.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1.5–2 hours |
| **What you'll need** | Packet Tracer (or your GNS3 build), the topology described in Part 1 below |

---

## 1. The Brief

> Build a 4-switch topology where SW1 is intended to be the root bridge. Two of the switches (SW3 and SW4) connect back toward SW1 partly through shared hubs rather than direct switch-to-switch links, creating redundant paths on a shared collision domain. One switch has a PC connected to a port that is currently NOT configured for fast edge-port behavior.

### Your task

- [ ] Sketch the topology: 4 switches, 2 hubs, at least 2 PCs. Decide the cabling pattern that would create a shared segment touching two ports on the same switch.
- [ ] Before building anything, predict: given equal switch priorities, which switch will win the root bridge election, and why?

---

## 2. Root Bridge Identification — Do This Before Any CLI

- [ ] Given equal priority (32769) on all four switches, what single value determines the root bridge? Write the rule down.
- [ ] List the MAC addresses of your four switches (or use the ones from the manual's inventory if building from that image) and determine which one wins.

---

## 3. Build and Cable

- [ ] Place all devices per your Part 1 sketch.
- [ ] Set `spanning-tree mode rapid-pvst` on every switch — what happens to convergence behavior if you forget this on even one switch?

---

## 4. Predict Port Roles — Before Running Any show Command

For **every** port on **every** switch, predict:

- [ ] Role (Root / Designated / Alternate / Backup)
- [ ] State (Forwarding / Blocking)
- [ ] Link type (P2p / Shared / Edge)

Pay special attention to the root bridge's own ports — does classic STP theory ("root bridge = all Designated") hold here? Why or why not?

---

## 5. Verify — Compare Against Your Predictions

- [ ] Run the command that shows the full spanning-tree table on the root bridge. Compare against your Part 4 predictions. Where were you wrong, and why?
- [ ] Find the specific command that shows role/state/link-type for a single interface. Use it on the root bridge's port connected to the shared hub segment.
- [ ] If your prediction for the root bridge's ports didn't include a Backup role anywhere, go back and explain — in writing — why a hub-connected segment produces one.

---

## 6. Fix the Misclassified Edge Port

- [ ] Find the PC-facing port that is NOT currently treated as an edge port (check its Type in the spanning-tree output).
- [ ] What single command fixes this in the most common, real-world way? What does it do to (a) the forwarding delay and (b) the RSTP link-type classification, simultaneously?
- [ ] Apply it, then re-verify with the same `show` command you used before the fix.

---

## 7. Explain Your Design

Answer without the manual:

1. Why can a root bridge have a non-Designated port, when introductory STP material teaches that it can't?
2. What's the functional difference between an Alternate port and a Backup port? Give a one-sentence definition of each.
3. Why should `spanning-tree portfast` never be applied to a switch-to-switch link?
4. What real-world symptom would you expect from a PC-facing port that's misclassified as Shared instead of Edge?

---

## 8. Troubleshoot Yourself

Break your own lab, then diagnose using only `show` commands:

- Lower one non-root switch's priority below the current root's, forcing a root-bridge re-election. Predict the new root before verifying.
- Remove `portfast` from a port you previously fixed and observe the Type change.
- Physically remove one hub connection, breaking the shared segment, and observe how the Backup port role changes.

---

## 9. Self-Check

- [ ] I correctly predicted the root bridge election result using bridge-ID logic, before checking with the CLI.
- [ ] I predicted at least one root-bridge port role incorrectly at first, then understood why the actual behavior was correct.
- [ ] I identified and fixed a misclassified edge port using the correct single command.
- [ ] I can distinguish Alternate vs. Backup port roles from memory.
- [ ] I broke and fixed at least 2 things without the manual's troubleshooting table.

Once done, open [`Day-22-Lab-Manual.md`](Day-22-Lab-Manual.md) and diff your work against Sections 6, 8, and 9.
