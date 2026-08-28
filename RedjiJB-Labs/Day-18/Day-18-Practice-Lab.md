# Day 18 Practice Lab — Multilayer Switching: SVIs and Inter-VLAN Routing (Self-Guided)

No-answers companion to `Day-18-Lab-Manual.md`.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2 hours. |
| **What you'll need** | Your Day 17 lab (or a fresh build), Packet Tracer/GNS3. |

---

## 1. The Brief

> Replace router-on-a-stick with a Layer 3 switch (SW2) that performs inter-VLAN routing itself, using SVIs. SW2 connects to the internet-edge router (R1) over a **routed** point-to-point link, not a trunk. VLAN addressing stays the same as your Day 16/17 plan; you need to design the new P2P subnet yourself, carved from whatever address space is still unused.

### Your task

- [ ] In your own words, explain what specifically was the bottleneck in the ROAS design that this lab's design removes.

---

## 2. Design the New P2P Link Yourself

1. Identify which portion of `10.0.0.0/24` is still unused after your three VLAN `/26`s.
2. Size a subnet for exactly 2 hosts using `2^h − 2 ≥ 2`. Derive the prefix length and mask from binary.
3. Pick the specific `/30` block from the unused space, aligned to its own block-size boundary.
4. Compute network, first-usable, last-usable, and broadcast addresses for that `/30` by hand.
5. Decide which end (SW2 or R1) gets which usable address, and justify your choice (hint: is there a convention from earlier labs you could reuse, or does it not matter here?).

---

## 3. Build and Cable

- [ ] Keep SW1 as an access switch, trunked to SW2.
- [ ] Connect SW2 directly to R1 (this will become a routed link, not a trunk).

---

## 4. Configure — Prompts Only

### 4.1 Remove the old ROAS configuration

- [ ] Remove R1's VLAN subinterfaces. What should R1's physical interface configuration look like once ROAS is gone — does it need any VLAN awareness at all?

### 4.2 Convert SW2's link to R1 into a routed port

- [ ] What single command turns a switch port from a Layer 2 switchport into a Layer 3 routed port? Apply it, then assign the IP from your Part 2 plan.
- [ ] Add whatever route SW2 needs to reach anything beyond R1.

### 4.3 Configure SVIs

- [ ] Create one SVI per VLAN on SW2 using your existing VLAN addressing plan. Does an SVI need an `encapsulation` command the way a ROAS subinterface did? Why or why not?

---

## 5. Verify — Predict First

- [ ] Predict SW2's `show ip route` output before running it — how many connected routes, how many static? What does the route source label for the default route look like?
- [ ] Predict whether an SVI can be correctly configured yet still show as down. What condition would cause that?
- [ ] Test an inter-VLAN ping and an internet-bound ping. Which one now avoids R1 entirely, and which one still needs it?

---

## 6. Explain Your Design

1. What specifically bottlenecks in the ROAS design, and how does moving routing onto SW2 remove it?
2. What does `no switchport` actually do to an interface, and why is it required before assigning an IP to a switch port?
3. Why does an SVI depend on Layer 2 activity elsewhere on the switch, unlike a router's physical interface?
4. Why does R1 still exist in this design instead of retiring it entirely in favor of SW2 doing everything?
5. Why did the new P2P link need its own dedicated `/30` instead of reusing an existing VLAN's `/26`?

---

## 7. Troubleshoot Yourself

Break your lab in 3 of these ways and diagnose using only `show` commands:

- Leave the SW2↔R1 port in switchport mode and try to assign it an IP.
- Remove the default route from SW2.
- Bring down every port in one VLAN and observe what happens to that VLAN's SVI.
- Leave a stale ROAS subinterface on R1 alongside the new physical-interface configuration.

---

## 8. Self-Check

- [ ] I derived the new P2P `/30` subnet by hand, including which unused block it came from.
- [ ] I configured the routed port and SVIs from memory/lookup, not by copying the full manual.
- [ ] I predicted `show ip route` output before running it and understood every line.
- [ ] I can explain all 5 design questions in Section 6 out loud.

Once done, open `Day-18-Lab-Manual.md` and diff your work against Sections 4, 6, and 7.
