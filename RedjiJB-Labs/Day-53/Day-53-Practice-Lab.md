# Day 53 Practice Lab — GRE Tunnels (Self-Guided)

This is the **no-answers companion** to [`Day-53-Lab-Manual.md`](Day-53-Lab-Manual.md). It gives you the same topology and business requirements, but withholds the addressing plan and CLI commands — you work them out yourself. Use the full manual only to check your work after you've attempted each part, not before.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–2.5 hours. This will take longer than the guided version — that's expected. |
| **What you'll need** | Packet Tracer (or your GNS3 build of this lab) and a blank sheet/spreadsheet for your addressing plan. |
| **Grading yourself** | Compare each section against the full manual's corresponding section only after attempting it. |

---

## 1. The Brief

> Office A and Office B are separated by a service-provider network your company doesn't own. Both offices have their own private LAN. You need the two offices to be able to route to each other's LANs dynamically — without the service provider ever seeing or needing to route either office's internal address space.
>
> R1 sits at the edge of Office A; R2 sits at the edge of Office B. Each already has basic IP connectivity to its own provider-facing router (SPR1 and SPR2 respectively) — that underlay is a given starting point, not something you're building from scratch.
>
> Design a solution that creates a logical connection between R1 and R2, and run a routing protocol across it so each office learns the other's LAN automatically.

### Your task

- [ ] Name the specific technology that solves "create a logical point-to-point link between two routers separated by a network you don't control." Don't just say "VPN" — be specific about the mechanism.
- [ ] Sketch the topology, labeling clearly which parts of your diagram are the **underlay** (real, provider-routed) and which are the **overlay** (logical, tunnel-only). If you can't yet articulate the difference between those two terms, that's the first thing to research before continuing.
- [ ] In your own words, explain why the service provider should never need a route to either office's internal LAN subnet in this design.

---

## 2. Design Your Own Addressing Plan

You're given only the following constraints. Work out everything else yourself.

**Constraints:**

- Both underlay links (R1↔SPR1 and R2↔SPR2) need exactly 2 usable host addresses each — pick appropriately sized subnets from any address space that makes sense for a provider-facing link.
- The tunnel's own logical addressing also needs exactly 2 usable addresses — again, derive the correct prefix length yourself.
- Office A's LAN is 10.0.1.0/24; Office B's LAN is 10.0.2.0/24 (given, not yours to choose).

### Your task — pencil and paper first

1. For a link needing exactly 2 usable host addresses, derive the required host-bit count from `2^h − 2 ≥ 2`, then derive the resulting prefix length and dotted-decimal mask. Show your work.
2. Choose an address block for the tunnel's overlay subnet. It must not collide with either LAN's addressing or either underlay link's addressing. Justify your choice.
3. Build a full addressing table: for each of R1's and R2's interfaces (LAN-facing, provider-facing, and tunnel), list the IP address, mask, and what it connects to.
4. Before touching a CLI, write out — separately, in two clearly labeled lists — which of your addresses are "underlay/real-world" addresses and which are "overlay/tunnel-only" addresses. You'll need this distinction to avoid the single most common mistake in this lab (see Section 4 below).

Only after finishing all 4 steps, compare against Section 4 of the full manual.

---

## 3. Build and Cable the Topology

- [ ] Place R1, R2, SPR1, SPR2, SW1, SW2, PC1, PC2 in Packet Tracer or your GNS3 build.
- [ ] Cable the underlay: R1↔SPR1, SPR1↔SPR2 (or however your specific topology connects the provider core), SPR2↔R2. Cable each office's LAN normally (PC↔SW↔R).
- [ ] Confirm SPR1 and SPR2 already have basic routing between themselves so that R1's and R2's provider-facing addresses can reach each other — this lab assumes that piece is a given starting condition, not something you're troubleshooting.

---

## 4. Configure — Prompts Only

### 4.1 Before any tunnel configuration

- [ ] Verify, with the appropriate command, that R1 can reach R2's provider-facing address (and vice versa) using ordinary IP routing — no GRE involved yet. If this fails, what is the *only* thing worth troubleshooting before you touch a tunnel command? (This is the single highest-value checkpoint in the whole lab — don't skip writing down why.)
- [ ] What routes (static or otherwise) does each edge router need so that this ping succeeds?

### 4.2 Creating the tunnel — R1

- [ ] What command creates a new logical tunnel interface? What number do you give it, and does that number need to match on the remote router?
- [ ] Which address do you assign directly to the tunnel interface with an `ip address` command — one of your underlay addresses, or one of your overlay addresses? Why?
- [ ] There are two more commands the tunnel interface needs, one specifying where the encapsulated packet originates from (an interface you already own) and one specifying where it should be delivered to (an address on the *other* router). For each, is it an underlay address or an overlay address? Get this wrong on purpose once in a lab (not production) and observe what breaks — write down what you saw.

### 4.3 Creating the tunnel — R2

- [ ] Mirror your R1 configuration. Before typing anything, write out on paper: what does R2 use as its tunnel source? What does R2 use as its tunnel destination? How does each of those relate to what you configured on R1?

### 4.4 Routing across the tunnel

- [ ] Choose and configure a routing protocol across the tunnel that will let each office learn the other's LAN automatically. What network(s) need to be included in that protocol's configuration on each router — just the tunnel subnet, or the LAN subnet too?
- [ ] Each router's LAN-facing interface needs one additional routing-protocol setting so that it stops sending protocol hello/discovery traffic toward end-user devices while still advertising that LAN's route. What is that setting called, and why is it good practice even though the lab would technically still function without it?

---

## 5. Verify — Predict Before You Run

For each command below, write your prediction first, then run it and compare.

- [ ] The command that shows a tunnel interface's up/down status and its configured source/destination. Predict: what should the "line protocol" state be if your underlay is healthy?
- [ ] The command that shows your routing protocol's neighbor table. Predict: what interface should the neighbor relationship with the remote router show up on?
- [ ] The full routing table on R1. Predict: how should the tunnel's own subnet appear (directly connected, or learned via the protocol)? How should Office B's LAN appear?
- [ ] A ping from PC1 to PC2. Predict success or failure, and if you predict success, predict roughly how many extra "hops" of encapsulation overhead are involved compared to a same-office ping (conceptually, not exact byte count).

---

## 6. Explain Your Design

Answer without referencing the full manual:

1. In one or two sentences each, define "underlay" and "overlay" using this lab's own topology as the example.
2. A tunnel interface configuration has (at minimum) three pieces of addressing information on it. Name all three and, for each, state whether it's an underlay or overlay address.
3. Why does the tunnel's own subnet show up as "directly connected" in the routing table, even though the two routers are separated by an entire provider network?
4. Does GRE, by itself, encrypt the traffic passing through it? If a manager asked you whether this design is "secure," what would your honest answer be, and what additional technology would you mention?
5. Why couldn't you achieve this design's goal with static routes across the underlay alone, without a tunnel at all?

---

## 7. Troubleshoot Yourself

Deliberately break your own lab in 3 different ways (pick 3), then diagnose and fix each using only `show` commands:

- Swap the tunnel destination address for the remote router's tunnel/overlay address instead of its underlay address.
- Remove the underlay default route on one router.
- Mismatch the tunnel interface's subnet mask between the two routers.
- Forget the passive-interface setting on a LAN-facing interface and observe whether anything actually breaks (this one's a trick — think about what *doesn't* break here and why).
- Shut down the tunnel source interface and observe what happens to the tunnel line protocol.

For each: write the symptom, the diagnostic command(s) you used, and the fix.

---

## 8. Self-Check

- [ ] I derived the /30 math for both the underlay and overlay links by hand, without a subnet calculator.
- [ ] I can state from memory which parts of a GRE tunnel configuration are underlay addresses and which are overlay addresses.
- [ ] I predicted verification output before running each command, and compared afterward.
- [ ] I could explain all 5 design-reasoning questions in Section 6 out loud to someone else.
- [ ] I intentionally broke and fixed at least 3 things without looking at the troubleshooting table first.

Once complete, open [`Day-53-Lab-Manual.md`](Day-53-Lab-Manual.md) and diff your work against Sections 4, 6–10, and 13 in detail.
