# Day 29 Practice Lab — OSPF Reference Bandwidth, Hello Protocol, and ASBR Default Route Injection

Same topology and business scenario as the Day 29 Lab Manual. Addressing and CLI are stripped into guided questions — work them out yourself, then check against the manual.

## Scenario

You're bringing up a 4-router OSPF backbone (R1–R4) plus a router acting as the boundary to a simulated ISP. R1 has the only connection to the outside world. You need every internal router to correctly prefer faster links over slower ones, and every internal router needs a way to reach the internet without each one needing its own ISP connection.

## Topology

| Device | Role |
|---|---|
| R1 | Connects to ISP; will become the ASBR |
| R2, R3, R4 | Internal OSPF routers |
| R4 | Also has a LAN with PC1 behind SW1 |

Topology image (original author's diagram):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-27-Lab-OSPF-(Part%202).png`

## Part 1 — Addressing

1. Each router-to-router link needs exactly 2 usable addresses. What mask gives you exactly that, with the least waste? Derive the host-bit math yourself.
2. R4's LAN needs to support many future hosts. What size subnet would you choose, and why not just reuse the point-to-point sizing?
3. Design your own addressing table for: R1–R2, R1–R3, R2–R4, R3–R4, R1–ISP, and the R4 LAN. Also assign each router a `/32` loopback.
4. Why is a loopback address, specifically, the conventional choice for an OSPF router ID rather than a physical interface's address?

## Part 2 — Basic OSPF

5. What command family enables OSPF on a specific interface, and what does the "wildcard mask" in that command actually represent (versus a subnet mask)?
6. Which interfaces in this topology should be `passive-interface`, and why those specifically? (Hint: think about where you do and don't expect an OSPF neighbor.)
7. Configure OSPF area 0 on all four routers, matching your addressing plan, with the correct passive interfaces.
8. What command would you use to confirm neighbors actually reached `FULL` state — and why isn't seeing a route in the routing table sufficient proof that adjacency succeeded?

## Part 3 — Reference Bandwidth

9. Without changing anything, what OSPF cost will a FastEthernet interface show? What cost will a GigabitEthernet interface show? Work this out from the default formula before configuring anything.
10. Why is it a problem that those two costs come out the same?
11. You want FastEthernet to end up with a cost of exactly 100. Using `OSPF Cost = Reference Bandwidth / Interface Bandwidth`, solve for the reference bandwidth value you need.
12. Configure that reference bandwidth. What warning does IOS print, and why does it matter that you apply the exact same value on every router, not just one?
13. After configuring it, what cost do you expect Serial (1544 Kbps) to show? Work out the math, then verify.

## Part 4 — ASBR Default Route Injection

14. Which single router in this topology is the natural candidate to become the ASBR? Why?
15. What OSPF router-config command makes a router advertise a default route into the OSPF domain?
16. What kind of LSA does that route show up as, and what does the "E2" in `O*E2` mean when you see it in a routing table?
17. Configure the default-route injection on your chosen ASBR.
18. From R4 (the router furthest from R1), verify the default route was learned. What does `show ip route` on R4 show as the gateway of last resort?

## Part 5 — Hello Protocol

19. What are the default Hello and Dead interval values on a broadcast (Ethernet) network? What's the mathematical relationship between them?
20. Name three fields inside an OSPF Hello packet and what each is used for.
21. If Area ID doesn't match between two potential neighbors, what happens to adjacency? What about a Hello/Dead timer mismatch?
22. Using Simulation Mode (or a packet capture), inspect an actual Hello packet leaving one of your routers. Confirm the Router ID, Area ID, and timer values match what you configured.

## Part 6 — Design Thinking

23. What's the risk of changing reference bandwidth on only some routers instead of all of them?
24. Why does centralizing default-route origination at one ASBR (instead of giving every internal router its own ISP connection and static default route) make operational sense — and what's the corresponding risk you're accepting?
25. If you wanted redundancy for the ASBR role, what would you add, and how would OSPF pick between two competing default routes?

## Self-Check

- [ ] I derived the addressing plan and reference-bandwidth value myself, from the formulas, before checking the manual
- [ ] I can explain, without notes, why the default reference bandwidth breaks path selection on modern networks
- [ ] I configured OSPF, passive interfaces, and reference bandwidth on all routers myself
- [ ] I configured and verified the ASBR default-route injection, including confirming it reached the furthest router
- [ ] I can state the Hello/Dead timer defaults and explain the 4x relationship
- [ ] I inspected an actual Hello packet and can identify at least four of its fields
