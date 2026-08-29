# Day 46 Practice Lab — Voice VLANs & Router-on-a-Stick (ROAS)

Same topology and business scenario as the Day 46 Lab Manual. Here, addressing and CLI are stripped out — work them out yourself, then check against the manual.

## Scenario

You're setting up a small office where each desk has one Ethernet drop, one PC, and one IP phone (PC connects through the phone). You need the phone traffic on its own VLAN, separate from PC traffic, and a router providing Layer 3 gateways for both VLANs over a single trunk link — no extra cabling or ports.

## Topology

| Device | Role |
|---|---|
| PC1, PC2 | Data endpoints |
| PH1, PH2 | IP Phones (PCs daisy-chain through them) |
| SW1 | Access switch |
| R1 | Router (Router-on-a-Stick) |

Topology image (original author's diagram):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-46-Lab-Voice-VLANs.png`

## Part 1 — Addressing

1. You need two separate subnets, one for data, one for voice. Why can't data and voice traffic share a subnet if they're on separate VLANs?
2. Pick two `/24` networks (or derive your own sizing) — one for VLAN 10 (data), one for VLAN 20 (voice). Write out the network address, usable host range, and broadcast address for each.
3. What IP address will R1 need on each VLAN, and why does a single physical router interface need two of them?

## Part 2 — Access Port Configuration

4. On SW1, what command puts an interface into access mode?
5. What command assigns the port's *untagged* VLAN? What separate command tells the switch to also accept 802.1Q-tagged traffic for a second VLAN on that same port?
6. Before you configure it: predict — will PC1's traffic arrive at the switch tagged or untagged? Will PH1's? Write your prediction down before verifying it later.
7. Configure both access ports (the phone/PC pairs) with the appropriate data and voice VLAN assignments.

## Part 3 — Trunk to the Router

8. What mode does the SW1-to-R1 link need to be in, and why can't it be a second access port?
9. Which VLANs need to be explicitly allowed across that trunk? What breaks if you forget one?
10. Configure the trunk.

## Part 4 — Router-on-a-Stick

11. R1 has a single physical interface facing the switch. How can it provide a Layer 3 gateway for two different VLANs over one wire?
12. What IOS construct lets you create multiple logical interfaces on top of one physical interface, each tied to a specific VLAN's tagged traffic?
13. Configure the subinterfaces with the correct encapsulation and IP addressing from Part 1.
14. What administrative state does the *physical* parent interface need to be in for the subinterfaces to pass traffic? Configure it.

## Part 5 — Verification

15. What command on SW1 shows you, per interface, both the access VLAN and the voice VLAN assignment in one place?
16. What command confirms which VLANs are actually allowed across the trunk?
17. What command on R1 confirms both subinterfaces are up/up with the correct IP addresses?
18. Using Simulation Mode (or a packet capture), send a PC1→PC2 ping and a PH2→PH1 call. Inspect the frames. Does your Part 2 prediction hold? Which traffic carries an 802.1Q header and which doesn't — and why, precisely?

## Part 6 — Design Thinking

19. Why is a dedicated voice VLAN preferable to just letting phone and PC traffic mix on VLAN 10?
20. What's the throughput trade-off of Router-on-a-Stick compared to a Layer 3 switch doing inter-VLAN routing natively? When would you outgrow ROAS?
21. Real IP phones learn their voice VLAN automatically via CDP rather than being told manually. Why does that matter for large deployments (hundreds of phones)?

## Self-Check

- [ ] I derived both subnets myself before looking at the manual
- [ ] I correctly predicted which traffic (PC vs. phone) would be tagged before verifying
- [ ] I configured access ports, the trunk, and ROAS subinterfaces without copying the manual's commands verbatim
- [ ] I verified with `show interfaces switchport`, `show interfaces trunk`, and `show ip interface brief`
- [ ] I inspected actual frames and can explain the tagging behavior in my own words
- [ ] I can explain why ROAS doesn't scale indefinitely and what replaces it at larger sites
