# Day 24 Practice Lab — Floating Static Routes and Failover Testing

Self-derivation companion to the Day 24 Lab Manual. No addressing plan and no CLI commands are given — work them out yourself first.

---

## Brief

Two enterprise edge routers, R1 and R2, run OSPF between themselves and each dual-home to their own ISP border router. You need to add floating static backups so that if the OSPF backbone link fails, traffic between the PC LAN and server LAN keeps flowing through the ISP cloud instead.

## Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-24-Lab-Floating-Static-Routes.png" alt="Day 24 Floating Static Routes Lab" width="900">
</p>

```text
PC1 -- SW1 -- R1 ===OSPF backbone=== R2 -- SW2 -- SRV1
              |                        |
           ISPBR1                   ISPBR2
              \________ISP cloud________/
```

---

## Part 1 — Derive the Addressing

1. The R1↔R2 backbone link and each router's link to its ISP border router are all point-to-point. How many usable hosts does each one need, and what prefix length follows from that?
2. Using `2^h − 2 ≥ required hosts`, solve for `h` and derive the mask in binary, then decimal.
3. Pick network addresses for the backbone link and each ISP-facing link so that none overlap. Using the block-size shortcut (2^h), show your work for why consecutive /30 blocks are 4 apart.
4. For the backbone /30 you chose, write out network address, first host, last host, and broadcast.

---

## Part 2 — Administrative Distance Reasoning

1. What is the default AD for OSPF? For a directly-configured static route? Which one wins when both claim to know a route to the same destination?
2. You want a static route to act as a *backup* to an OSPF-learned route, never interfering while OSPF is healthy. What AD value should you assign it, and why does it need to be higher (not lower, not equal) than OSPF's default?
3. What happens if you forget the AD argument entirely on your floating static command? Predict the exact behavior — will it break anything even while OSPF is fully up?

---

## Part 3 — Path Selection Reasoning (before any failure)

1. When PC1 sends traffic to SRV1, which route type (OSPF vs. static default) matches, and why does the more specific route win even though a default route also exists?
2. When PC1 sends traffic to an Internet address like 1.1.1.1, which route matches, and does that traffic ever cross the R1↔R2 backbone under normal conditions?

---

## Part 4 — Configure the Floating Statics (write these out yourself, then compare to the manual)

1. Write the floating static command on R1 that backs up the OSPF route to the server LAN, using the ISP border router as next hop. Justify your choice of next hop — why does it need to route *around* the backbone link rather than through it?
2. Write the mirror-image command on R2.
3. Why do the ISP border routers (ISPBR1, ISPBR2) also need their own floating statics? What happens to R1's backup route if ISPBR2 doesn't know how to reach the server LAN?

---

## Part 5 — Predict the Failover

Before running anything, answer:

1. If you shut down R1's interface facing R2, what specific syslog message would you expect to see, and what does it tell you about OSPF's detection mechanism?
2. Predict the exact `show ip route` output on R1 immediately after the shutdown — which line disappears, which line appears, and what AD is attached to the new line?
3. Will `ping 10.0.2.1` from R1 succeed immediately after the failover, assuming Part 4's reciprocal routes are correctly configured? What would cause it to fail even with a "correct-looking" floating static?

---

## Part 6 — Troubleshooting Scenarios

For each, state your first diagnostic command and your reasoning:

1. You shut down the backbone interface, but `show ip route` still shows the old OSPF entry.
2. The floating static installed correctly (AD 120, right destination) but pings still fail.
3. Traffic recovers after the primary link fails, but never switches back after you bring the primary back up.

---

## Self-Check Checklist

- [ ] I derived all three /30 subnets by hand without checking the manual first
- [ ] I correctly identified AD 120 (or explained why any value >110 and <255 would work) before reading the manual
- [ ] I wrote both floating static commands with correct syntax and next hops before checking
- [ ] I correctly predicted which routing table line disappears and which appears after failover
- [ ] I identified the reciprocal-route requirement on the ISP border routers unaided
- [ ] I worked through all three troubleshooting scenarios before reading the manual's troubleshooting table
