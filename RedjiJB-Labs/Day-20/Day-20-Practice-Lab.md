# Day 20 Practice Lab — Analyzing STP: Port Roles Across Four Switches (Self-Guided)

No-answers companion to `Day-20-Lab-Manual.md`. This lab is analysis-only in both versions — the practice version withholds the worked-out port role table so you build it yourself from raw priority/MAC and path cost data.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1.5–2 hours. |
| **What you'll need** | Packet Tracer/GNS3 with link lights disabled, pencil and paper. Do not run `show spanning-tree detail` until instructed. |

---

## 1. The Brief

> You're handed a four-switch topology with redundant links and default STP settings already running. You are given each switch's bridge priority and MAC address, and the physical topology (which ports connect to which). Your job: determine the root bridge and predict every port's role and state, by hand, before verifying anything in the CLI.

### Your task

- [ ] Write out the Bridge ID (priority + MAC) for all four switches exactly as given in the topology.

---

## 2. Determine the Root Bridge — By Hand

1. Compare all four priorities. Which field is compared first, priority or MAC address? Which one is the tiebreaker?
2. Identify the root bridge. State your reasoning in one sentence.
3. What is immediately, automatically true about every port on the root bridge, without any further per-port calculation?

---

## 3. Determine Root Ports — By Hand

For each of the three non-root switches:

1. List every port that has *some* path back to the root (direct or indirect).
2. For the direct path (if one exists), note the interface speed and look up its default STP path cost from memory or by deriving it (hint: cost roughly scales inversely with speed).
3. Compare all candidate paths' total cost-to-root. The lowest-cost path's port becomes the Root Port. Do this for all three non-root switches.

---

## 4. Determine Designated and Alternate Ports — By Hand

For every remaining port not yet classified:

1. Identify which LAN segment (link) it belongs to, and which other port sits on the far end of that same segment.
2. Compare the two switches' cost-to-root. The port belonging to the switch with the lower cost-to-root becomes Designated (forwarding) on that segment; the other becomes Alternate/Non-Designated (blocking).
3. Build a complete table: Switch / Port / Role / State / Path Cost for all 14 ports in the topology.

Only after completing your full table, compare it against Section 6.4 of the full manual.

---

## 5. Verify — Predict Before You Run

- [ ] Predict exactly what `show spanning-tree detail` will show for the root bridge's "This bridge is the root" line and its port states, before running it on that switch.
- [ ] Predict what the "Root Identifier" field will show on a non-root switch, and why every switch in a converged topology reports this even about a switch that isn't itself.
- [ ] Run `show spanning-tree detail` on all four switches and check every row of your Section 4 table against the real output.

---

## 6. Explain Your Design (Analysis, Not Configuration)

1. Why does STP guarantee exactly one root port per non-root switch and exactly one designated port per LAN segment?
2. Why does a lower path cost number represent a *better*, preferred path rather than a worse one?
3. Why are Alternate/blocking ports not a sign of a problem, but a deliberate safety mechanism?
4. If the current root bridge failed, how would you determine, by hand, which switch becomes the new root and how every other port role would change?
5. Explain, in your own words, why priority dominates the root bridge election over MAC address, and when MAC address actually matters.

---

## 7. Self-Check

- [ ] I determined the root bridge from raw priority/MAC data without looking at CLI output first.
- [ ] I derived every root port using path cost comparison, not guessing.
- [ ] I classified every remaining port as Designated or Alternate using segment-by-segment cost comparison.
- [ ] I verified my full 14-port table against real `show spanning-tree detail` output and understood any discrepancies.
- [ ] I can answer all 5 questions in Section 6 out loud, from memory.

Once done, open `Day-20-Lab-Manual.md` and diff your full table against Section 6.4 and the Expected Output Gallery in Section 7.
