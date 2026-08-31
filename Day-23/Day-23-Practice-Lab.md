# Day 23 Practice Lab — EtherChannel: LACP, PAgP, Static, and Load Balancing

This is the self-derivation companion to the Day 23 Lab Manual. No addressing plan and no CLI commands are given here — your job is to work them out and write them down before checking the manual.

---

## Brief

You're the engineer wiring a new distribution layer. Two access switches (ASW1, ASW2) each need a resilient, high-bandwidth uplink to their respective distribution switch (DSW1, DSW2), and the two distribution switches need a resilient routed core link between them so PCs on one side can reach a server on the other.

## Topology (same as the manual)

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-23-Lab-EtherChannel.png" alt="Day 23 EtherChannel Lab" width="900">
</p>

```text
PC1/PC2 -- ASW1 ==(2 links)== DSW1 ==(2 links, routed)== DSW2 ==(2 links)== ASW2 -- SRV1
```

- ASW1 ↔ DSW1: build with **LACP**
- ASW2 ↔ DSW2: build with **PAgP**
- DSW1 ↔ DSW2: build with **static** mode, routed (Layer 3)
- PCs live on one subnet behind ASW1/DSW1, SRV1 lives on a different subnet behind ASW2/DSW2

---

## Part 1 — Derive the Addressing

Before opening the manual, answer these yourself:

1. The PC-side and server-side subnets each just need "room to grow" for a normal access-layer LAN. What prefix length would you choose, and why is it not tighter?
2. The DSW1↔DSW2 routed port-channel is a point-to-point link between exactly two Layer 3 interfaces — even though it has two *physical* cables underneath it. How many usable host addresses does the **logical** Port-channel interface actually need? What prefix length does that imply?
3. Using the host-bits formula `2^h − 2 ≥ required hosts`, solve for `h` for the DSW1↔DSW2 link, then convert to a dotted-decimal mask by hand (write out all 32 bits).
4. For whatever network address you pick for that /30, write out: network address, first usable host, last usable host, broadcast address.
5. What's the "block size shortcut" (256 − 2^h) for this prefix length, and what does it tell you about where the *next* available /30 block would start if you needed to add a third distribution switch?

---

## Part 2 — Protocol Negotiation Reasoning

Answer these before checking the manual's Task 1/2 config:

1. LACP has two negotiation modes and PAgP has two negotiation modes. Name all four and explain the active/passive relationship — which mode(s) can pair with which?
2. If ASW2 is configured `channel-group 1 mode desirable` and DSW2 is accidentally left at `channel-group 1 mode on`, what happens? Predict the exact `show etherchannel summary` flag you'd see on the suspended ports, and predict roughly what a `%EC-5-CANNOT_BUNDLE2` log message would say.
3. Why does `mode on` (static) never produce this kind of negotiation error, even when badly misconfigured? What's the tradeoff of that silence?
4. Which of the three modes (LACP, PAgP, static) is the one production engineers default to, and why?

---

## Part 3 — Layer 2 vs Layer 3 Bundling

1. What CLI difference distinguishes a Layer 2 (trunk) EtherChannel from a Layer 3 (routed) EtherChannel, at both the member-interface level and the Port-channel interface level?
2. Where should the IP address for a routed bundle be configured — on each physical member, or on the logical Port-channel interface? What goes wrong if you get this backwards?
3. Why would a network designer choose to route directly on a distribution-to-distribution link instead of trunking it and using SVIs on each side? (Hint: think about what protocol has to run across a Layer 2 trunk that doesn't have to run across a routed link.)

---

## Part 4 — Reachability

1. Once the routed Port-channel12 link is up between DSW1 and DSW2, what single static route does DSW1 need to reach the server subnet? What single static route does DSW2 need to reach the PC subnet? Write both out in full `ip route` syntax (use your own addressing from Part 1).
2. Why is one static route per switch enough, given there are two physical links underneath the routed bundle?

---

## Part 5 — Load Balancing

1. What is the factory-default EtherChannel load-balancing method on Catalyst 2960/3560/3650 switches? What single field does it hash on, and what's the practical downside of hashing on only that field for two devices that exchange a lot of traffic?
2. Is `port-channel load-balance` a global (per-switch) setting or a per-port-channel setting on these platforms? What breaks if ASW1 uses one method and DSW1 uses a different one for the same bundle?
3. Name the command you'd run to change the switch to hash on source and destination IP, and the command you'd run to verify it took effect.

---

## Part 6 — Troubleshooting Scenarios

For each scenario, state what you'd check first and what command you'd run:

1. `show etherchannel summary` shows `Po1(SD)` with both member ports flagged `(I)`.
2. The routed Port-channel12 shows up/up on both switches, but PCs still can't reach the server.
3. Traffic between the same PC and server always seems to ride the same physical member, even though the bundle has two links.
4. `show interfaces status` shows one member port as `notconnect`.

---

## Self-Check Checklist

- [ ] I derived the /30 addressing for the routed core link by hand, without looking at the manual first
- [ ] I can state which LACP/PAgP modes pair with which without guessing
- [ ] I correctly predicted the suspended-port flag before checking the manual
- [ ] I identified the Layer 2 vs Layer 3 EtherChannel CLI differences unaided
- [ ] I wrote both static routes correctly on the first attempt
- [ ] I correctly identified load-balancing as a global, not per-bundle, setting
- [ ] I worked through all four troubleshooting scenarios before reading the manual's troubleshooting table
