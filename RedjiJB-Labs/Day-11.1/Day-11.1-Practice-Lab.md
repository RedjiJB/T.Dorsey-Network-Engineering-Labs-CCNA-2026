# Day 11.1 Practice Lab — Configuring Static Routes (Self-Guided)

This is the **no-answers companion** to [`Day-11.1-Lab-Manual.md`](Day-11.1-Lab-Manual.md). Same topology and brief, addressing plan and CLI withheld. Attempt every section before checking the manual.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1–1.5 hours |
| **What you'll need** | Packet Tracer or your GNS3 build, a blank sheet for your addressing plan |

---

## 1. The Brief

> Your company has two offices connected through a small routed backbone: three routers in a line, with a LAN full of end users on each end. Each router only knows about the networks directly attached to it — nothing more, unless you tell it. Your job is to make every network reachable from every other network using static routes only.

### Your task

- [ ] Sketch the topology: how many routers, how many LANs, how many router-to-router links?
- [ ] For each router, list which networks it's *directly* connected to, and which networks it will need an explicit route to reach.

---

## 2. Design Your Own IP Addressing Plan

**Constraints:**

- Two LAN subnets (one per edge router), sized for normal user growth.
- Two router-to-router transit links.
- Use private RFC 1918 space throughout.

### Your task

1. Choose two `/24`s for the LANs.
2. Decide: will your transit links be `/24` (matching the original lab's simple scheme) or `/30` (the address-efficient, textbook-correct choice)? Justify your choice in one sentence.
3. If you choose `/30`, show the `2^h − 2 ≥ 2` math and derive the mask from binary by hand.
4. Build a full device address table (Device / Interface / IP / Mask / Connects To) before touching the CLI.

---

## 3. Build and Cable

- [ ] Place 3 routers, 2 switches, 2 PCs.
- [ ] Cable per your sketch, confirm link lights are active.

---

## 4. Configure Every Device — Prompts Only

### 4.1 Edge routers (R1, R3)

- [ ] Hostname, LAN-facing interface with IP + `no shutdown`, transit-facing interface with IP + `no shutdown`.
- [ ] Write the static route(s) each edge router needs. How many routes does an edge router need if it only has one way out? Why?

### 4.2 Middle router (R2)

- [ ] Configure both transit-facing interfaces.
- [ ] Write the static routes R2 needs. Think carefully: does R2 need routes in one direction or two? Why is R2's situation different from R1's or R3's?

### 4.3 End devices

- [ ] Assign IP, mask, and default gateway to PC1 and PC2 per your plan.

---

## 5. Verify — Predict Before You Run

- [ ] On each router, predict what `show ip route` will show — which lines will be `C`, which `L`, which `S` — before running the command.
- [ ] Ping PC1 to PC2. If it fails, which specific router's route table would you check first, and why?
- [ ] Explain what the TTL value on a successful ping tells you about the number of hops traversed.

---

## 6. Explain Your Design

Answer in writing, without the manual:

1. Why does R2 need routes in two directions while R1 and R3 only need routes in one?
2. Why is static routing an appropriate choice for exactly this topology, and what change to the topology would make it a poor choice?
3. What's the difference between a `/24` and a `/30` transit link, and which would you actually use in production? Why?

---

## 7. Troubleshoot Yourself

Break your own lab in 2 of these ways, then diagnose using only `show` commands:

- Remove a static route from the middle router.
- Point a static route at the wrong next-hop.
- Forget `no shutdown` on one transit interface.

For each: symptom observed, diagnostic command used, fix applied.

---

## 8. Self-Check

- [ ] I designed the addressing plan myself, including justifying `/24` vs `/30` for transit links.
- [ ] I wrote every static route from memory, understanding the next-hop logic (not copy-pasting from one router to another).
- [ ] I predicted `show ip route` output before running it.
- [ ] I could explain, out loud, why R2's routing needs differ from R1's and R3's.
- [ ] I broke and fixed at least 2 things without the troubleshooting table.

Once done, open [`Day-11.1-Lab-Manual.md`](Day-11.1-Lab-Manual.md) and diff your work against Sections 4, 6, 7, and 9.
