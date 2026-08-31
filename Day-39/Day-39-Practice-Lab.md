# Day 39 Practice Lab — DHCP Server, DHCP Client, and DHCP Relay

This is the guided-discovery version of Day 39. Don't look at the full lab manual's config blocks — work through each prompt yourself, then check your answers against the manual afterward.

## Brief

You're the network engineer for a company with two sites connected by a WAN link. Headquarters (R2's site) will host the only DHCP server. The branch (R1's site) has no local DHCP server — R1 must both obtain its own WAN address dynamically and relay its LAN clients' DHCP requests back to headquarters.

## Topology

- R1 (branch) — R2 (headquarters), connected by a `/30` transit link
- PC1 behind R1 on a `/24` LAN
- PC2 behind R2 on a `/24` LAN
- R2 will run all DHCP pools

(Same topology image as the original Day 39 lab: `Lab-Photos/Day-39-Lab-DHCP.png`)

## Guided Questions

**Addressing**
1. You're told PC1's LAN needs room for at least 200 hosts. What mask do you choose, and how many usable host addresses does it actually give you? Show your work.
2. The R1–R2 transit link only ever needs two addresses. What's the smallest usable subnet mask for that, and why is using a `/24` here wasteful?
3. Why is it standard practice to exclude the first ~10 addresses of a DHCP-served LAN from the lease pool, even if nothing is using them yet?

**DHCP server design**
4. R2 needs to serve three different subnets from one device. What IOS construct lets you do that, and does the order in which you create things matter? Why or why not?
5. For each pool, what value should `default-router` be set to? Is it always R2's own address? Justify your answer per-subnet.
6. What two IOS options give clients a DNS server and a domain suffix? Why would a real business bother setting the domain-name option at all?

**DHCP client**
7. What single interface-level command turns a router interface into a DHCP client instead of requiring a static address? What is a real-world (non-lab) situation where routers commonly do this?

**DHCP relay**
8. PC1's DHCP Discover is a Layer 2 broadcast. Explain, in your own words, why that broadcast cannot reach R2 without extra configuration.
9. What command solves that problem, and — critically — on which interface of R1 does it belong? Get this wrong and explain what symptom you'd see.
10. Walk through, step by step, what happens to PC1's DHCP Discover packet from the moment PC1 sends it to the moment PC1 receives an IP address. Name every device that touches the packet.

## Configuration Checklist (fill in the commands yourself)

- [ ] Exclude infrastructure addresses on R2 for all three subnets
- [ ] Create three DHCP pools with correct network, default-router, dns-server, domain-name
- [ ] Configure R1's WAN interface as a DHCP client
- [ ] Configure `ip helper-address` on the correct R1 interface
- [ ] Confirm routing exists between R1 and R2 in both directions
- [ ] Force PC1 and PC2 to request new leases

## Verification — What Would You Check?

Before looking at the manual, write down: which three `show` commands would you run, on which devices, to prove this entire setup works end to end? What specific field in each command's output tells you "yes, this is working"?

## Self-Check

- [ ] I derived the subnet masks myself before checking the manual
- [ ] I could explain why `ip helper-address` goes on the client-facing interface, not the server-facing one
- [ ] I correctly predicted which `default-router` value belongs in each pool
- [ ] I listed the DORA steps without needing to look them up
- [ ] I identified at least 2 ways this lab could fail silently (routing missing, wrong helper interface, exhausted pool, etc.) before reading the Troubleshooting Guide
