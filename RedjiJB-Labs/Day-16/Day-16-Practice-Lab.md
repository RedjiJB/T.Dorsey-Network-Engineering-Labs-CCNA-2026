# Day 16 Practice Lab — VLANs Part 1 (Self-Guided)

No-answers companion to `Day-16-Lab-Manual.md`. Same brief and topology; you derive the VLAN plan, addressing, and configuration yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2 hours. |
| **What you'll need** | Packet Tracer/GNS3, pencil and paper. No subnet calculators. |

---

## 1. The Brief

> You have `10.0.0.0/24` and three departments — Engineering, HR, Sales — two hosts each today, room to grow. Each department must be its own VLAN and its own broadcast domain. Inter-VLAN routing must work, but you may **not** use trunking or router subinterfaces in this version of the lab — each VLAN gets its own dedicated physical link to the router. Every VLAN's gateway should be the **last usable address** in its subnet, not the first.

### Your task

- [ ] Sketch the topology: how many physical links does R1 need to SW1, and why exactly that many given the "no trunking" constraint?

---

## 2. Design Your Own Addressing Plan

1. Split `10.0.0.0/24` into equal-size blocks large enough to comfortably hold each department's current 2 hosts with real room to grow, using the smallest number of host bits that still gives you at least 3 usable blocks. Show the math for how many total blocks a `/26` split produces and why.
2. Derive the `/26` subnet mask from binary, not memory.
3. Lay out the three subnets on their block-size boundaries, and note whether a 4th block remains unused.
4. For one subnet, calculate by hand: network address, first usable host, last usable host, broadcast address — then identify which one is the **gateway** given this lab's convention.
5. Assign IPs to all 6 PCs and 3 router interfaces, building a full device table.

Compare against Section 4 of the full manual only after finishing all 5 steps.

---

## 3. Build and Cable

- [ ] Place SW1, R1, PC1–PC6.
- [ ] Cable R1 to SW1 — how many separate physical links, and why?
- [ ] Cable each PC to an access port.

---

## 4. Configure — Prompts Only

### 4.1 R1

- [ ] Configure each of R1's interfaces with the correct gateway IP for its VLAN, per your own plan. Bring each up.
- [ ] Why doesn't R1 need any special "VLAN-aware" configuration in this version of the lab?

### 4.2 SW1

- [ ] Create the three VLANs and name them.
- [ ] Assign each PC's access port to the correct VLAN.
- [ ] Assign each of SW1's three uplink ports (toward R1) to the matching VLAN. What mode should these uplink ports be in — access or trunk — given this lab's no-trunking constraint, and why?

### 4.3 PCs

- [ ] Configure IP, mask, gateway per your plan.

---

## 5. Verify — Predict First

- [ ] Predict what `show vlan brief` will show (which ports under which VLAN) before running it.
- [ ] Predict which pings succeed: same-VLAN, different-VLAN, and to a nonexistent host. Test and compare.
- [ ] For an inter-VLAN ping, predict what the TTL value tells you about whether the packet was switched or routed. Test and check.
- [ ] Design a test to prove broadcast traffic stays inside one VLAN. What would you observe if it didn't?

---

## 6. Explain Your Design

1. Why is a VLAN a separate broadcast domain, and why does a broadcast need a router (not a switch) to reach a different VLAN — except it *never* does, even with a router. What's actually happening instead?
2. Why does this lab need three separate physical links between R1 and SW1 instead of one?
3. What two separate configuration steps are required before a switch port actually forwards a specific VLAN's traffic?
4. Why might "gateway = last usable address" be a deliberately different convention from another lab that uses "gateway = first usable address"? Does either choice have a technical advantage?
5. What would break if you assigned SW1's uplink port toward R1's Gi0/1 to VLAN 10 instead of VLAN 20?

---

## 7. Troubleshoot Yourself

Break your lab in 3 of these ways and diagnose with only `show` commands:

- Leave one uplink port in the default VLAN.
- Assign a PC's access port to the wrong VLAN.
- Forget `no shutdown` on one router interface.
- Create a VLAN but never assign any port to it, then look for it in traffic.

---

## 8. Self-Check

- [ ] I derived the /26 split and subnet boundaries by hand.
- [ ] I built the full addressing table myself before checking the manual.
- [ ] I configured VLANs, port assignments, and router interfaces from memory/lookup.
- [ ] I predicted verification output before testing.
- [ ] I can explain all 5 design questions in Section 6 out loud.

Once done, open `Day-16-Lab-Manual.md` and diff your work against Sections 4, 6, and 7.
