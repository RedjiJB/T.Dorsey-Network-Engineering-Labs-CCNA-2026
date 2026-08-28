# Day 06 Practice Lab — Ethernet LAN Switching & MAC Address Tables (Self-Guided)

No-answers companion to `Day-06-Lab-Manual.md`. Same brief and topology; you predict and derive the behavior yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1–1.5 hours. |
| **What you'll need** | Packet Tracer with Simulation Mode. |

---

## 1. The Brief

> Build a flat LAN: two switches, four PCs (two per switch), all on one subnet, no VLANs, no routing. Both switches start with empty MAC address tables. You'll generate one ping between two PCs on different switches and observe exactly how the switches behave before they've learned anything, and again after you manually clear what they've learned.

### Your task

- [ ] Sketch the topology from the brief alone.
- [ ] Before running anything, write down: what do you predict happens to the very first frame PC1 sends toward PC3, given that neither switch has ever seen either device's MAC address?

---

## 2. Design a Minimal Addressing Plan

- [ ] Choose one `/24` from private space and assign all 4 PCs an address. Do any devices in this topology need a default gateway? Why or why not?

---

## 3. Predict the Mechanism Before Testing

Answer these from what you already know about switching, before touching Packet Tracer:

1. How does a switch learn a MAC address — what triggers a new entry in its table?
2. What does a switch do with a frame whose destination MAC it doesn't have an entry for?
3. Why must ARP happen before the very first ICMP packet of a new ping, specifically?
4. Is a switch's MAC address table the same thing as a PC's ARP cache, or two separate systems? Justify your answer.
5. When PC1's ARP request (a broadcast) reaches SW1, does SW1 send it out one port or every port (except the one it arrived on)? What about when it reaches SW2?

---

## 4. Build and Test

- [ ] Cable the topology per your Part 1 sketch.
- [ ] Before generating any traffic, run the command that displays a switch's MAC table on both switches. What do you expect to see?
- [ ] From PC1, ping PC3. Switch to Simulation Mode and step through every PDU. For each one, note: is it broadcast or unicast? Is it flooded or forwarded?
- [ ] Run the MAC table command again on both switches. What changed, and does it match your Part 3 predictions?

---

## 5. Clear and Retest — Predict First

- [ ] What command clears only the *dynamically learned* entries from a switch's MAC table (leaving any static entries untouched)?
- [ ] Before running it: will PC1's own ARP cache also be cleared by this command? Why or why not?
- [ ] Run the clear command on both switches, verify they're empty again, then re-ping PC1 → PC3. Predict what happens to the very first frame of this second ping, given that the switches' tables are empty again but the PCs' ARP caches might not be. Test and compare.

---

## 6. Explain Your Design

1. Why does a switch flood an unknown-destination frame instead of just dropping it?
2. Why does a switch forward based on MAC address rather than IP address? What layer does each address type belong to?
3. Why is the MAC address table dynamic (ages out, can be cleared) instead of permanent?
4. Give a real-world scenario (not from the manual) where understanding "the switch just rebooted, so it's flooding everything for a moment" would keep you from panicking on an on-call shift.

---

## 7. Troubleshoot Yourself

- [ ] Predict what you'd see in `show mac address-table` if PC2 (not PC1) pinged PC3 right after your Part 4 test, without clearing anything first. Test it — did SW1 already have enough information to avoid flooding this time?
- [ ] Add a third switch between SW1 and SW2 (if time allows) and trace how the flood pattern changes with an extra hop.

---

## 8. Self-Check

- [ ] I predicted the flood-vs-forward behavior correctly before testing, for both the first ping and the post-clear ping.
- [ ] I can explain the difference between a switch's MAC table and a PC's ARP cache without notes.
- [ ] I correctly identified which PDUs in the Simulation Mode capture were broadcast vs. unicast, and flooded vs. forwarded.
- [ ] I could explain, out loud, why flooding is the correct design choice rather than a flaw.

Once done, open `Day-06-Lab-Manual.md` and diff your work against Sections 6, 7, and 10.
