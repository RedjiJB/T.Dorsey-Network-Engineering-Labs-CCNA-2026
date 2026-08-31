# Day 30 Practice Lab — HSRP Gateway Redundancy: Failover, Preemption, and Virtual IPs

Same topology and business scenario as the Day 30 Lab Manual. Addressing and CLI are stripped into guided questions — work them out yourself, then check against the manual.

## Scenario

R1 and R2 both sit on the same LAN segment as PC1 and PC2, and both have a path out through R3 toward the internet. You need PC1 and PC2 to keep working even if R1 (the router you want normally handling traffic) goes down for any reason — planned maintenance or an actual failure — without anyone touching the PCs.

## Topology

| Device | Role |
|---|---|
| R1 | Should normally be the active gateway |
| R2 | Should take over only when R1 is unavailable |
| R3 | WAN/ISP edge, not part of the redundancy group |
| PC1, PC2 | End hosts on the shared LAN |

Topology image (original author's diagram):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-29-Lab-HSRR-Configuration.png`

## Part 1 — Addressing

1. Design the LAN subnet for R1, R2, PC1, PC2, and a shared virtual gateway address, all in the same `/24`. Show the host-bit math.
2. Which address should the virtual IP be, and does it matter that it's not tied to either router's physical interface? Why or why not?
3. Design the two WAN point-to-point links off R3, sized appropriately, with full network/first/last/broadcast math.

## Part 2 — Before Redundancy Exists

4. Before configuring any redundancy protocol, what does PC1's default gateway point to? What happens to PC1's internet access if that router goes down?
5. Test this yourself conceptually: what specific single point of failure exists in this design right now?

## Part 3 — Configuring the Redundancy Protocol

6. What Cisco protocol lets two routers share a single virtual IP and virtual MAC address for first-hop redundancy?
7. What command creates a redundancy group on an interface and assigns it a shared virtual IP? What has to match exactly between the two routers for them to join the same group?
8. R1 should normally be the active router. What single value do you configure, and in which direction (higher or lower than default), to make that happen in the election?
9. What is the default priority value if you don't configure one at all?
10. Configure R1 and R2 with a shared virtual IP, with R1 favored to win the election.

## Part 4 — Preemption

11. After configuring priority alone, would R1 automatically reclaim active status if it recovered from a failure while R2 was active? Why or why not?
12. What command changes that behavior?
13. Should you enable that command on both routers, or just one? Justify your answer in terms of what could go wrong with the other choice.
14. Configure preemption appropriately.

## Part 5 — Pointing End Hosts at the Redundancy

15. What should PC1 and PC2's default gateway be set to — a physical router IP, or something else? Why does this choice determine whether the redundancy you just configured is actually useful?
16. Reconfigure PC1 and PC2 accordingly.

## Part 6 — Verification and the Virtual MAC

17. What command on a router shows you its current state (Active/Standby), the virtual IP, priority, and preemption status all at once?
18. From a PC, what command lets you see what MAC address the virtual IP currently resolves to?
19. Why is it significant that both routers are configured to answer to the *same* virtual MAC, not just the same virtual IP?

## Part 7 — Triggering and Observing Failover

20. Save R1's configuration, then shut down its LAN-facing interface to simulate a failure. What log message would you expect to see on R2?
21. From PC1, check the ARP entry for the gateway again. Did it change? Should it have?
22. Ping through the (now-failed-over) gateway. Do you expect zero packet loss, or a small amount? Why?
23. Bring R1 back online. Does it reclaim the active role? Walk through exactly why, citing both configuration items you set earlier.

## Part 8 — Design Thinking

24. What real operational task (besides an actual hardware failure) does this redundancy setup make safer to perform during business hours?
25. What's the risk of enabling preemption on both routers instead of just one?
26. If you wanted the two routers to share the traffic load instead of one sitting fully idle as standby, what Cisco protocol would you look into instead of HSRP?

## Self-Check

- [ ] I derived the addressing plan myself before checking the manual
- [ ] I can explain the difference between what priority controls and what preemption controls
- [ ] I configured the redundancy group, priority, and preemption myself without copying commands verbatim
- [ ] I pointed end hosts at the virtual IP and can explain why that step is what makes the redundancy actually useful
- [ ] I triggered a real failover and observed the state-change behavior
- [ ] I verified R1 reclaimed active status after recovering and can explain precisely why
