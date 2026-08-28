# Day 17 Practice Lab — VLANs Part 2: Trunking & Router-on-a-Stick (Self-Guided)

No-answers companion to `Day-17-Lab-Manual.md`.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–3 hours. |
| **What you'll need** | Packet Tracer/GNS3, your Day 16 addressing plan. |

---

## 1. The Brief

> Replace Day 16's one-router-port-per-VLAN design with a single trunk from SW1 to R1, and a second switch (SW2) trunked to SW1, carrying the same three VLANs. R1 must route between VLANs using subinterfaces on one physical link — router-on-a-stick. Somewhere in this topology, a native VLAN mismatch exists between two trunk ends; you need to find it, not just fix a pre-labeled problem.

### Your task

- [ ] Sketch the new topology: which links are now trunks, and which stay access ports?

---

## 2. Design Your Own Configuration Plan — No CLI Yet

1. List every physical link in the topology and classify each as **access** or **trunk**. Justify each classification in one sentence.
2. For each trunk, decide what VLANs need to be allowed. Does every trunk need every VLAN, or only the ones actually used downstream of it?
3. Write out the subinterface plan for R1: how many subinterfaces, what `encapsulation dot1Q` value goes with each, and what IP address (reuse your Day 16 plan).

---

## 3. Build and Cable

- [ ] Place SW1, SW2, R1, PC2, PC3, PC4, PC5.
- [ ] Cable SW1↔SW2 and SW1↔R1 as single trunk-capable links.
- [ ] Cable end hosts to their assigned switches.

---

## 4. Configure — Prompts Only

### 4.1 Access ports

- [ ] Assign each PC's switch port to the correct VLAN in access mode.

### 4.2 Trunk ports

- [ ] Set trunk mode explicitly on every inter-switch and switch-to-router link.
- [ ] Configure the allowed-VLAN list on each trunk per your Part 2 plan. What's the difference between the command that *replaces* the allowed list and the one that *adds* to it — and which should you use when adding VLAN 20 to a trunk that already allows VLAN 10?
- [ ] Run `show interfaces trunk` on both ends of a trunk before assuming it matches. What field tells you the native VLAN, and what should you check it against on the far end?

### 4.3 Router-on-a-stick

- [ ] Configure one subinterface per VLAN on R1, using the correct `encapsulation dot1Q` value and IP address for each.
- [ ] What single command must be applied to the *physical* interface (not any subinterface) before any of the subinterfaces will come up?

---

## 5. Verify — Predict First

- [ ] Before running it, predict what `show interfaces trunk` should show for allowed VLANs on each trunk link. Test and compare.
- [ ] Run `show cdp neighbors detail` on SW1 and SW2. Is there a native VLAN mismatch? How do you know, and what's the actual risk if you leave it unfixed?
- [ ] Predict R1's `show ip interface brief` output — specifically, what should the *physical* interface's IP address column show, and why?
- [ ] Test a cross-VLAN ping and explain, step by step, every device and every VLAN tag the packet crosses on its way from source to destination.

---

## 6. Explain Your Design

1. Why does trunking let you scale VLANs without scaling router/switch port count the way Day 16's design required?
2. What is a native VLAN, and why must both ends of a trunk agree on it?
3. Why does a trunk stay operational even with a native VLAN mismatch — and why is that dangerous rather than reassuring?
4. Why does R1's physical interface show `unassigned` for its IP address in a router-on-a-stick configuration?
5. What's the practical difference between `switchport trunk allowed vlan 10,20` and `switchport trunk allowed vlan add 20` if a trunk was already configured to allow VLAN 10?

---

## 7. Troubleshoot Yourself

Break your lab in 3 of these ways and diagnose using only `show` commands:

- Use the "replace" form of the allowed-VLAN command when you meant to add one VLAN.
- Mismatch the native VLAN on purpose between two trunk ends.
- Remove `encapsulation dot1Q` from one subinterface.
- Leave the physical interface on R1 shut down while configuring subinterfaces.

---

## 8. Self-Check

- [ ] I classified every link as access or trunk and justified each choice before configuring anything.
- [ ] I configured trunks and allowed-VLAN lists from memory/lookup.
- [ ] I configured router-on-a-stick subinterfaces correctly, including the physical interface's `no shutdown`.
- [ ] I found and diagnosed the native VLAN mismatch without being told where it was.
- [ ] I can explain all 5 design questions in Section 6 out loud.

Once done, open `Day-17-Lab-Manual.md` and diff your work against Sections 6, 7, and 9.
