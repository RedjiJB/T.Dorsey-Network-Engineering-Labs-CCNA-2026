# Day 02 Practice Lab — Connecting Network Devices (Self-Guided)

This is the **no-answers companion** to `Day-02-Lab-Manual.md`. It gives you the same business requirements and topology, but withholds cable-selection answers, the addressing plan, and CLI commands — you derive them yourself. Only check the full manual after a genuine attempt.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–3 hours. |
| **What you'll need** | Packet Tracer (or your GNS3 build), pencil/spreadsheet for your addressing plan. Don't have the full manual open while attempting each section. |

---

## 1. The Brief

> Your company has two branch sites. Site A has two routers (R1, R2), four switches, and two PCs. Site B has two routers (R3, R4), four switches, a PC, and a server. R1 and R2 are 50 meters apart. R3 and R4 are 250 meters apart. R1 and R3 (the two sites) are 3 kilometers apart. Everything within a site connects through a standard switch fabric down to the end devices.

### Your task

- [ ] Sketch both site topologies from the device list alone — don't copy Section 3 of the manual.
- [ ] For each of the three router-to-router distances given, decide: copper, multi-mode fiber, or single-mode fiber? Write your reasoning for each before checking anything.

---

## 2. Cable Selection — Work It Out

Answer these from first principles, not by looking anything up in the manual:

1. What is the rule for choosing straight-through vs. crossover cable? State it in terms of "like" vs. "unlike" devices, and give 3 example device pairs for each.
2. Copper Ethernet is reliable up to approximately what distance? What happens electrically beyond that distance that makes fiber necessary?
3. What is the core physical difference between multi-mode and single-mode fiber that explains why single-mode goes farther?
4. For each of the following, pick copper / multi-mode / single-mode and justify in one sentence:
   - Router to switch, 3 meters
   - Switch to switch, 15 meters
   - Building to building, 400 meters
   - Site to site, 3 kilometers
   - Data center row to row, 30 meters

Only after answering all of the above, check Section 6 of the full manual.

---

## 3. Design Your Own IP Addressing Plan

**Constraints:**

- Each site's LAN needs a `/24` from private address space.
- Every router-to-router point-to-point link (regardless of medium) should use the smallest subnet that fits exactly 2 hosts.

### Your task

1. Choose two different `/24`s for the two site LANs.
2. For each of the 3 router-to-router links, calculate by hand: how many host bits does exactly 2 usable addresses require? What prefix length results? Derive the dotted-decimal mask from binary.
3. For one of your `/30` links, write out the network address, first usable host, last usable host, and broadcast address.
4. Build a full device address table (Device / Interface / IP / Mask / Connects To) for all 12 addressed devices (4 routers + 2 PCs + 1 server, with routers having 2 interfaces each).
5. Decide which router needs the most static routes, and why — think about topology shape (who's the "hub"?), not just device count.

Compare against Section 4 of the full manual only after finishing all 5 steps.

---

## 4. Configure — Prompts Only

### 4.1 Cabling
- [ ] Cable both sites' switch fabrics using your Section 2 answers.
- [ ] Cable all three router-to-router links with the correct medium — remember you may need to swap a router's interface module before a fiber cable will even attach in Packet Tracer.

### 4.2 Routers
- [ ] Hostname each router.
- [ ] Configure each router's LAN-facing and inter-router interfaces with your Section 3 addressing plan. Don't forget the one command every fresh interface needs before it will pass traffic.
- [ ] Work out which router in this topology needs specific routes to *both* remote LANs, and which routers only need a single default route. Configure accordingly.

### 4.3 End devices
- [ ] Assign IP/mask/gateway to each PC and the server per your plan.

---

## 5. Verify — Predict First

- [ ] Before running it, predict what `show ip interface brief` should show on each router. Then run it.
- [ ] Before running it, predict what `show interfaces` on a fiber-connected interface should report for `Media type`. Run it and compare.
- [ ] Predict a full ping matrix (at least 5 source/destination pairs, including one crossing both fiber links) before testing.
- [ ] What specific line in `show interfaces` output tells you a fiber link is up at Layer 1 versus just administratively enabled? Find it by testing a working link, then (if your platform allows) deliberately breaking one strand and comparing.

---

## 6. Explain Your Design

1. Why is "fiber everywhere" the wrong default answer, even though fiber technically works at short distances too?
2. Why are single-mode and multi-mode fiber different products instead of one universal fiber type?
3. Why does subnet size have nothing to do with cable distance? Give a one-sentence explanation you could give a non-technical manager.
4. Which router in your topology ended up with the most routing configuration, and why does its position in the topology explain that?

---

## 7. Troubleshoot Yourself

Break your lab in 3 of these ways, diagnose using only `show` commands, then fix:

- Assign the wrong cable type to a router-switch link (if your platform allows forcing it).
- Remove `no shutdown` from a fiber interface.
- Delete a static route from the hub router.
- Swap the subnet mask on one end of a `/30` link so it no longer matches the other end.

---

## 8. Self-Check

- [ ] I derived the straight-through/crossover rule and the copper/multi-mode/single-mode distance rule from first principles before checking the manual.
- [ ] I built the addressing plan and derived at least one mask from binary by hand.
- [ ] I correctly identified which router needed the most routes and why.
- [ ] I predicted verification output before running each command.
- [ ] I broke and fixed at least 3 things without looking at the troubleshooting table first.

Once done, open `Day-02-Lab-Manual.md` and diff your work against Sections 4, 6, 7, and 9.
