# Day 15 Practice Lab — VLSM & Static Routing (Self-Guided)

This is the **no-answers companion** to `Day-15-Lab-Manual.md`. Same requirements, same topology — you derive the subnetting math and configuration yourself. Don't open the full manual until you've made a genuine attempt at each section.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–3 hours. VLSM math takes longer to do correctly than to copy. |
| **What you'll need** | Pencil/paper or a spreadsheet, Packet Tracer (or your GNS3 build), and nothing else. No subnet calculators. |

---

## 1. The Brief

> You've been given a single `192.168.5.0/24` block to divide across four LANs of different sizes, plus one router-to-router point-to-point link. Sizes: 45 hosts, 64 hosts, 14 hosts, 9 hosts, and 2 hosts for the P2P link. Two routers (R1, R2) will host two LANs each and connect to each other over the P2P link.

### Your task

- [ ] List the five requirements in the order you should allocate them, and explain in one sentence *why* that order matters.

---

## 2. Design Your Own VLSM Plan — Pencil and Paper Only

1. For each of the five requirements, calculate the minimum host bits `h` such that `2^h − 2 ≥` the requirement. Show your work for all five — don't skip straight to the answer.
2. Convert each `h` value to a prefix length (`32 − h`), then derive the dotted-decimal subnet mask **from binary**, not from memory.
3. Starting at `192.168.5.0`, allocate each subnet **largest-first**, snapping every subnet's network address to a multiple of its own block size (`256 − last-octet-mask-value`). Write out the network address, range, and broadcast address for all five subnets.
4. For **one** `/26` subnet and **one** `/28` subnet from your plan, write out by hand: network address, first usable host, last usable host, broadcast address.
5. Decide (and justify) which two LANs belong to R1 and which two belong to R2.
6. Build a full device address table (Device / Interface / IP / Mask / Connects To) following the convention: PCs get the **first** usable address in their subnet, routers get the **last** usable address.

Only after finishing all 6 steps, compare against Section 4 of the full manual.

---

## 3. Build and Cable

- [ ] Place R1, R2, and PC1–PC4 to match your topology.
- [ ] Cable PC1/PC2 to R1, PC3/PC4 to R2, and R1↔R2 directly.
- [ ] Confirm interface names on your platform before configuring.

---

## 4. Configure — Prompts Only

### 4.1 Both routers

- [ ] Set hostname.
- [ ] Configure each LAN-facing interface with the gateway address from your own plan, and bring it up. What's the most common reason a freshly configured interface won't come up?
- [ ] Configure the P2P interface toward the other router.
- [ ] Write the static route(s) each router needs to reach the two LANs it isn't directly connected to. What must the next-hop address always be in this topology, and why is there only one valid choice?
- [ ] Save.

### 4.2 PCs

- [ ] Assign IP, mask, and gateway to each PC per your own address table.

---

## 5. Verify — Predict Before You Run

- [ ] Before running it, predict what `show ip interface brief` should show on each router. Then run it and compare.
- [ ] Before running it, sketch what `show ip route` should contain — how many connected subnets, how many static routes, and what does the phrase "variably subnetted, N masks" mean if you see it? Then run it and compare.
- [ ] Predict which pings should succeed and which (if any) should fail across this topology, then test.
- [ ] Ping from a PC on R1 to a PC on R2 and check the TTL value in the reply. What should the TTL decrease by, and why does that number confirm the packet actually routed through both devices?

---

## 6. Explain Your Design

Answer without referencing the full manual:

1. Why must VLSM allocations happen largest-requirement-first? What breaks if you allocate smallest-first?
2. What does "block size" mean, and how do you use it to decide where the *next* subnet in your plan is allowed to start?
3. Why is a router-to-router link always sized as a `/30` (2 usable hosts) rather than reusing a larger block?
4. What's the difference between a network address, a broadcast address, and a usable host address — and why will a router refuse to accept the first two as its own interface IP?
5. Why does the static route's next-hop have to be the *other router's* P2P address rather than a LAN address, in this specific topology?

---

## 7. Troubleshoot Yourself

Break your own lab in 3 of these ways, then diagnose and fix using only `show` commands:

- Remove `no shutdown` from one router interface.
- Assign the wrong mask to one PC (e.g., a `/24` on a `/28` subnet).
- Delete one static route.
- Point a static route's next-hop at the wrong address.
- Swap which PC is on which router's LAN interface without updating the addressing.

For each: write the symptom, the diagnostic command(s) you used, and the fix.

---

## 8. Self-Check

- [ ] I derived host bits and subnet masks for all five requirements by hand, without a calculator.
- [ ] I allocated all five subnets largest-first and can explain why that order is required.
- [ ] I computed network/first-usable/last-usable/broadcast for at least a /26 and a /28 by hand.
- [ ] I configured both routers and all four PCs from memory/lookup, not by copying the full manual.
- [ ] I predicted verification output before running each command, and compared afterward.
- [ ] I could explain all 5 design-reasoning questions in Section 6 out loud to someone else.

If any box is unchecked, revisit that specific section before moving on. Once done, open `Day-15-Lab-Manual.md` and diff your work against Sections 4, 6, 7, and 9 in detail.
