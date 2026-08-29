# Day 36 Practice Lab — CDP & LLDP: Network Discovery Protocols

Use this as a self-test companion to the [Day 36 Lab Manual](Day-36-Lab-Manual.md). Work through the prompts before checking the manual for the full command walkthrough.

---

## Scenario

You've just been handed access to an undocumented network: three routers (R1, R2, R3) wired in a triangle, each with its own access-layer switch (SW1, SW2, SW3), each switch with one PC attached (PC1, PC2, PC3). No diagram exists. You need to (1) discover the topology, (2) lock discovery protocols down on user-facing ports, (3) disable the legacy discovery protocol entirely, and (4) migrate to the more secure alternative — enabled only where it's actually useful.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-36-Lab-CDP-%26-LLDP.png" alt="Day 36 Topology" width="900">
</p>

---

## Phase 1 — Discovery

1. Without looking at any diagram, what single command would you run on each device to list its directly-connected neighbors?
2. What's the difference in information between that command and its `detail` variant? Name at least three fields only available in the detailed view.
3. Two devices (say, R2 and R3) both see R1 as a neighbor. How would you use their two neighbor tables together to figure out that R1 has at least three interfaces facing other network devices?
4. What are CDP's default advertisement interval and hold-time? What happens if a neighbor's hold-time expires without a new advertisement?
5. Given only what CDP can tell you (no IP addressing, no diagram), could you determine which device is a router and which is a switch? What field tells you that?

---

## Phase 2 — Lock down access ports

6. Why is it a security problem to leave the discovery protocol running on a switch port connected to a PC, specifically?
7. What is the exact per-interface command to disable this discovery protocol on one port, without affecting any other interface on the same device?
8. If a switch had 24 PC-facing ports (Fa0/1–Fa0/24) instead of just one, how would the command from Q7 change to cover all of them in a single line?
9. After disabling it on a PC port, what would you expect `show cdp interface` to report for that specific interface, compared to an uplink interface where it's still active?

---

## Phase 3 — Global disable

10. What is the global (device-wide) command to turn this discovery protocol off entirely, and how does its scope differ from the per-interface command in Q7?
11. If you already disabled the protocol on all access ports (Phase 2), what additional exposure does the global disable in this phase close that Phase 2 alone did not?
12. What would `show cdp` and `show cdp neighbors` report after the global disable is applied?

---

## Phase 4 — Migrate to the safer protocol

13. Unlike the protocol from Phases 1–3, the replacement protocol is **off** by default everywhere. What is the one command that must be issued before any per-interface configuration will have any effect?
14. This protocol splits "send advertisements" and "receive advertisements" into two separate commands instead of one on/off toggle. Name both commands, and explain what happens if only one is configured on an interface.
15. On the routers in this topology, every interface faces another network device, so the safer protocol gets enabled on all of them via one `interface range` command. On the switches, only one interface per device gets it enabled. Which interface, and why not the others?
16. Why might `interface range g0/0-2` fail or behave unexpectedly if you tried to use it to also include a switch's `fa0/1` port in the same command?

---

## Verification Practice

17. Write out (without checking the manual) what you'd expect `show run | section interface <if>` to display for a switch's PC-facing port after all four phases are complete. Which lines confirm both protocols are off on that port?
18. What command shows you the safer protocol's global status (active/inactive, advertisement interval, hold time) — analogous to `show cdp` for the legacy protocol?
19. How would you confirm, from R3, that it can see both R1 and R2 as neighbors using the replacement protocol, and that the neighbor table matches what CDP originally showed in Phase 1?

---

## Design Reasoning

20. Why does this lab start with the protocol that's on by default (for discovery) rather than starting directly with the safer, off-by-default protocol?
21. Compare the two protocols on: vendor scope (proprietary vs. standard), amount of information revealed per neighbor, and default state. Which factor matters most for a mixed-vendor network, and which matters most for a security-conscious all-Cisco network?
22. A colleague argues "we don't need to bother disabling anything on access ports — no one's going to plug in a rogue device on our internal network." What's the counter-argument, in your own words?

---

## Self-Check

- [ ] I can name the discovery command and its `detail` variant, and explain the difference
- [ ] I can state the two commands that disable the legacy protocol per-interface vs. globally, and when to use each
- [ ] I can state the global-enable command for the replacement protocol and both of its per-interface direction commands
- [ ] I can explain, without notes, why the two protocols have opposite default states
- [ ] I can justify, in one or two sentences, why discovery protocols should never run on PC-facing ports
- [ ] I reconstructed the full six-device topology from neighbor-table cross-referencing alone, without looking at the topology diagram first
