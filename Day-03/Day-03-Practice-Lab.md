# Day 03 Practice Lab — OSI Model & DHCP Packet Analysis (Self-Guided)

No-answers companion to `Day-03-Lab-Manual.md`. Same brief and topology, but you derive the addressing, the relay configuration, and the OSI-layer mapping yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1.5–2.5 hours. |
| **What you'll need** | Packet Tracer with Simulation Mode, a blank sheet for packet-field notes. |

---

## 1. The Brief

> PC1 needs to get its IP configuration automatically. The DHCP server, SRV1, sits two router hops away from PC1 — on the far side of R2, across a WAN link from R1. Design and build a topology that lets PC1 successfully obtain a lease from SRV1, and be ready to explain, layer by layer, what happens on the wire during that exchange.

### Your task

- [ ] Sketch the topology from the brief alone: how many routers, switches, and end devices, and how are they arranged?
- [ ] Before building anything: state, in one sentence, why a DHCP Discover can't simply be routed like a normal unicast packet would be.

---

## 2. Design Your Own IP Addressing Plan

**Constraints:**

- PC1's LAN needs a `/24` from private space, DHCP-assigned.
- SRV1's segment needs a `/24` from private space (different from PC1's), statically assigned.
- The R1–R2 WAN link needs the smallest subnet that fits exactly 2 hosts.

### Your task

1. Choose the two `/24`s.
2. For the WAN link, do the full `2^h − 2` derivation to find the correct host-bit count, prefix, and dotted-decimal mask — don't just recall `/30`, derive it.
3. Write out the network, first host, last host, and broadcast address for your WAN subnet.
4. Decide the DHCP pool's start address, range, and which addresses must be excluded (hint: think about what's already statically assigned on that subnet).

Only compare against Section 4 of the full manual after finishing.

---

## 3. Configure — Prompts Only

- [ ] Configure R1 and R2's interfaces and static routes so each router can reach the other's LAN.
- [ ] Configure SRV1 with a static IP (why must a DHCP server's own address never be DHCP-assigned?) and enable its DHCP service with the pool you designed in Part 2.
- [ ] Set PC1 to obtain an address automatically.
- [ ] Here's the key question this lab is built around: **routers do not forward broadcast traffic by default.** Given that DHCP Discover is a broadcast and SRV1 is two hops away, what single command, on which router, on which specific interface, solves this? Work it out before checking the manual — what does the command need to know (a destination address? an interface? both?) to do its job?

---

## 4. Capture and Analyze — Predict First

Using Packet Tracer's Simulation Mode, capture the DHCP exchange. Before inspecting each frame's contents, predict:

- [ ] What will the DHCP Discover's Layer 3 source IP be? (Not "whatever it's about to get" — think about what the client actually knows at that instant.)
- [ ] What will the Layer 3 and Layer 2 destination addresses be, and why?
- [ ] What UDP source and destination ports will appear, and which one belongs to the client vs. the server?
- [ ] Name all four messages in the full exchange, in order, before checking anything. What does each one accomplish?
- [ ] Why does the third message (the client's acceptance) stay broadcast instead of going straight to the server unicast, even though the client now knows exactly which server it's dealing with?

Now capture and compare against your predictions.

---

## 5. Map to the OSI Model

Without looking at Section 6/7 of the full manual, fill in this table from what you captured:

| OSI Layer | What you observed in the capture |
|---|---|
| Layer 7 (Application) | ? |
| Layer 4 (Transport) | ? |
| Layer 3 (Network) | ? |
| Layer 2 (Data Link) | ? |
| Layer 1 (Physical) | ? (this one you can't directly "see" in Packet Tracer — explain why, and what it represents anyway) |

---

## 6. Explain Your Design

1. In business terms, why does virtually every company run DHCP instead of statically assigning every device? Give at least 2 distinct business reasons, not just "it's easier."
2. Why must a DHCP server always have a static IP address itself?
3. What problem does `ip helper-address` (or your platform's equivalent) solve, specifically? What would you observe in Simulation Mode if it were missing or pointed at the wrong IP?
4. Explain encapsulation and de-encapsulation in your own words, using the DHCP Offer packet as your example, including what happens to the Layer 2 header specifically as the packet crosses each router hop.

---

## 7. Troubleshoot Yourself

Break your lab 3 ways, diagnose with `show` commands and Simulation Mode only, then fix:

- Remove the relay/helper command from R1.
- Point the relay/helper command at the wrong IP address.
- Misconfigure SRV1's DHCP pool to use the wrong subnet.
- Leave PC1 set to Static instead of DHCP.

---

## 8. Self-Check

- [ ] I derived the WAN subnet mask from binary by hand, not from memory.
- [ ] I correctly predicted the DHCP Discover's source IP before capturing it.
- [ ] I identified the relay/helper requirement before checking the manual.
- [ ] I filled in the OSI-layer mapping table before checking Section 7.
- [ ] I broke and fixed at least 3 things using only diagnostic commands and Simulation Mode.

Once done, open `Day-03-Lab-Manual.md` and diff your work against Sections 4, 6, 7, and 9.
