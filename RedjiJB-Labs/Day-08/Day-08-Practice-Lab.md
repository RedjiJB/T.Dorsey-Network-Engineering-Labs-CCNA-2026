# Day 08 Practice Lab — IPv4 Address Configuration & Router Interface Setup (Self-Guided)

No-answers companion to `Day-08-Lab-Manual.md`. Same brief and topology; you derive the addressing math yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2 hours. |
| **What you'll need** | Packet Tracer, pencil/spreadsheet. No subnet calculator. |

---

## 1. The Brief

> One Cisco router connects three completely separate networks, one per interface: a `/8`, a `/16`, and a `/24`. One PC and one switch sit on each network. Every PC needs to reach every other PC through the router.

### Your task

- [ ] Sketch the topology from the brief alone.
- [ ] Before calculating anything: which of the three networks has the most usable host addresses? Which has the fewest? Answer from the prefix lengths alone, before doing any math — does a smaller number after the slash mean more hosts or fewer? Explain why.

---

## 2. Derive the Addressing Math Yourself

You are given only the three network addresses: `15.0.0.0/8`, `182.98.0.0/16`, `201.191.20.0/24`. Do all of the following by hand:

1. For each network, state the number of host bits.
2. For each, calculate usable hosts using `2^h − 2`.
3. For each, derive the dotted-decimal subnet mask from binary — write out all 32 bits, then convert each octet.
4. For each, calculate the network address, first usable host, last usable host, and broadcast address.
5. Choose a gateway address for each network (any valid usable host address — it does not have to be `.1`) and a PC address (a different valid usable host address).

Only after finishing all 5 steps, compare against Section 4 of the full manual. If your masks and ranges are mathematically correct but you chose different specific host addresses than the manual, that's fine.

---

## 3. Configure — Prompts Only

- [ ] Hostname the router.
- [ ] Before configuring anything, run the command that shows interface status with the `do` shortcut from Global Config mode — what does `do` let you avoid doing?
- [ ] Configure all 3 router interfaces with your Part 2 addressing. Remember: IOS's `ip address` command wants which mask format — CIDR slash notation, or the expanded dotted-decimal form? Get this wrong once on purpose and see what IOS says.
- [ ] Bring each interface up.
- [ ] Save.
- [ ] Configure all 3 PCs with static IP/mask/gateway matching your plan.

---

## 4. Verify — Predict First

- [ ] Predict `show ip interface brief` output before running it.
- [ ] Predict `show ip route` output before running it. Specifically: will you need to configure any static routes for full connectivity in this topology? Why or why not — think about what "directly connected" means for a router interface with a valid, up IP address.
- [ ] Predict, then test, a full ping matrix across all 3 PCs.
- [ ] On a successful cross-network ping, look at the TTL value in the reply. What does it tell you about how many router hops the packet crossed?

---

## 5. Explain Your Design

1. Why does a network with a smaller prefix number (like `/8`) have *more* usable hosts than one with a larger prefix number (like `/24`)? Explain the relationship between prefix length and host bits.
2. Why did this lab need zero static routes, when earlier labs in this course needed several?
3. In a real company, what kind of situation would actually produce a `/8` sitting next to a `/24` on the same router, the way this lab's topology does?
4. Why does IOS's `ip address` command require the expanded mask instead of accepting CIDR notation directly?

---

## 6. Troubleshoot Yourself

Break your lab in 3 of these ways, diagnose with `show` commands only, then fix:

- Assign a PC the wrong mask (matching a different network's prefix than the one it's actually on).
- Skip `no shutdown` on one router interface.
- Type an IP address on a router interface that's outside the intended network's valid range.
- Point a PC's default gateway at the wrong interface's IP.

---

## 7. Self-Check

- [ ] I derived all three subnet masks from binary by hand, without a calculator.
- [ ] I correctly predicted that no static routes would be needed, and explained why.
- [ ] I correctly interpreted a ping's TTL value as evidence of hop count.
- [ ] I could explain the prefix-length-to-host-count relationship without notes.
- [ ] I broke and fixed at least 3 things using only diagnostic commands.

Once done, open `Day-08-Lab-Manual.md` and diff your work against Sections 4, 6, 7, and 9.
