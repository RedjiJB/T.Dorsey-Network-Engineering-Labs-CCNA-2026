# Day 09 Practice Lab — Interface Configuration & Device Management (Self-Guided)

No-answers companion to `Day-09-Lab-Manual.md`. Same brief and topology; you derive the commands and reasoning yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1.5–2 hours. |
| **What you'll need** | Packet Tracer. |

---

## 1. The Brief

> One router and two switches serve four PCs on a shared `172.16.0.0/16` LAN. Beyond basic addressing, you need to: manually hard-set speed and duplex on the router-facing uplinks, label every connected port with a description, verify interface state thoroughly, and — critically — disable every switch port that has nothing connected to it.

### Your task

- [ ] Sketch the topology from the brief alone.
- [ ] Before configuring anything, list which specific ports on SW1 and SW2 are "in use" vs. "unused," based on your sketch — you cannot safely disable unused ports without first knowing which ones qualify.

---

## 2. Addressing (quick — this lab's focus is elsewhere)

- [ ] Derive the `/16` mask from binary (host bits, `2^h − 2`, mask octets) even though you've done this before — treat it as a warm-up.
- [ ] Assign all 4 PCs and R1's LAN interface an address from `172.16.0.0/16`.

---

## 3. Configure — Prompts Only

- [ ] Hostname all 3 infrastructure devices, configure R1's LAN interface, and get baseline connectivity working (all 4 PCs can reach R1's interface) before touching anything else.
- [ ] On the switch-to-router uplink ports, manually configure speed and duplex instead of leaving them on auto-negotiation. What two settings need to be specified, and — critically — what happens if you configure them on only one end of the link and leave the other end on auto? Predict the specific failure mode before testing it.
- [ ] Add a description to every connected port on both switches and to R1's LAN interface. What's the operational argument for doing this even though it has zero effect on whether traffic flows?
- [ ] Using your Part 1 port inventory, disable every unused port on both switches in as few commands as possible. What single IOS feature lets you apply the same command to a contiguous block of interfaces at once?

---

## 4. Verify — Predict First

- [ ] Predict what `show interfaces status` will show for a manually-configured uplink port vs. an auto-negotiated access port — specifically, what visual difference (a prefix character) distinguishes "auto-negotiated to this value" from "manually forced to this value"?
- [ ] Predict what `show interfaces <if>` will show for a port you deliberately shut down.
- [ ] Run a full ping test across all 4 PCs after your hardening changes. If anything fails that worked before, that's a signal you disabled or misconfigured something that was actually needed — diagnose it using only `show` commands.

---

## 5. Explain Your Design

1. What is a duplex mismatch, specifically? Why is it a notoriously frustrating real-world troubleshooting scenario compared to a link that's simply down?
2. Why might an engineer choose to manually hard-set speed/duplex on a business-critical uplink, given that auto-negotiation is the generally correct default elsewhere?
3. What's the security argument for disabling unused switch ports? Frame your answer for a non-technical stakeholder who might ask "why does this matter, nothing's plugged into that port anyway?"
4. Why do interface descriptions matter operationally, even though they have zero functional effect on traffic forwarding?

---

## 6. Troubleshoot Yourself

Break your lab in 3 of these ways, diagnose with `show` commands only, then fix:

- Hard-set duplex on only one end of the SW1-R1 uplink, leaving the other on auto.
- Disable a port that's actually in use (misjudge your Part 1 inventory on purpose).
- Apply an `interface range` command to the wrong port range.
- Remove a description and try to determine, from `show interfaces status` alone, which physical device a bare port number belongs to — how much harder is this without the description?

---

## 7. Self-Check

- [ ] I correctly identified every in-use vs. unused port before disabling anything.
- [ ] I can explain duplex mismatch and predict its symptoms without notes.
- [ ] I used `interface range` correctly for bulk port disabling.
- [ ] I verified end-to-end connectivity survived my hardening changes.
- [ ] I broke and fixed at least 3 things using only diagnostic commands.

Once done, open `Day-09-Lab-Manual.md` and diff your work against Sections 6, 7, and 9.
