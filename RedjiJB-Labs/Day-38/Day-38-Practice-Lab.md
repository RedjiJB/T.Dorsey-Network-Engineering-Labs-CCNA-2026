# Day 38 Practice Lab — DNS Configuration and Name Resolution

Same topology and business scenario as the Day 38 Lab Manual. Addressing and CLI are stripped into guided questions — work them out yourself, then check against the manual.

## Scenario

Your internal LAN (three PCs behind R1) needs to reach external websites by name, not just by IP. You'll set up a default route toward a simulated internet, configure DNS on the clients and on R1 itself, and add a couple of local static hostname entries on R1 for internal devices.

## Topology

| Device | Role |
|---|---|
| R1 | Internal gateway, needs a default route and DNS settings |
| PC1, PC2, PC3 | Internal clients |
| Internet Router | Simulated ISP edge |
| DNS Server | Answers DNS queries |
| Web Server | Represents an external site reached only by name |

Topology image (original author's diagram):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS.png`

## Part 1 — Addressing

1. Design the internal LAN subnet for R1 and three PCs, with room to grow. Show the host-bit math.
2. Design the R1–Internet Router point-to-point link. Show the math.
3. Where should the DNS server's address sit relative to your internal addressing — inside the LAN subnet, or outside it? Why does that choice matter for what this lab is actually testing?

## Part 2 — Default Route

4. R1 has no specific route to the external DNS server or web server. What single command gives it a path to reach *any* destination it doesn't have a specific route for?
5. What does the `0.0.0.0 0.0.0.0` network/wildcard actually mean in that command?
6. Configure it, and predict what `show ip route` will show before you check.
7. What symbol in the routing table output specifically identifies this as the default route candidate?

## Part 3 — Client DNS Configuration

8. What field, separate from IP address/mask/gateway, does a client need configured to resolve names at all?
9. Is the DNS server address required to be the same device as the default gateway? Why or why not?
10. Configure all three PCs with matching IP settings and the same DNS server address.

## Part 4 — Router-Side DNS

11. What command tells R1 itself which DNS server to query if it needs to resolve a name?
12. What separate, non-DNS mechanism lets you create hostname entries directly on the router, with no dependency on any external server?
13. Configure R1's DNS resolver setting and create local entries for PC1, PC2, and PC3.
14. If you `ping PC1` from R1 right after configuring the local entry, does it actually use the DNS server, or something else first? How would you prove which one it used?

## Part 5 — Resolving a Name End to End

15. From PC1, what happens, step by step, when you type `ping youtube.com`? List every step from "check local cache" through "ICMP reply received," in order.
16. Why might the very first ping attempt time out even though the name resolves and the destination is reachable?
17. Using Simulation Mode (or a packet capture), confirm the actual order of the DNS query/response versus the ICMP packets.

## Part 6 — DNS vs. Routing

18. A client's DNS query succeeds and returns a valid IP address, but the subsequent ping to that address fails. Is this a DNS problem or a routing problem? How do you know?
19. A client's ping to a known-good IP address succeeds, but `ping <hostname>` fails for that same address. Is this a DNS problem or a routing problem? How do you know?
20. Write out, in your own words, the one-sentence distinction between what DNS does and what routing does.

## Part 7 — Troubleshooting Method

21. Put these checks in the correct diagnostic order, and explain why that order matters: (a) ping the resolved IP directly, (b) verify the client's own IP configuration, (c) ping the DNS server by IP, (d) attempt to resolve the hostname, (e) ping the default gateway, (f) verify R1 has a route to the resolved address.

## Self-Check

- [ ] I derived the addressing plan myself before checking the manual
- [ ] I configured the default route, client DNS settings, and router-side DNS/host entries myself
- [ ] I can explain, without notes, the difference between `ip host` and actual DNS resolution
- [ ] I traced the full DNS-then-ICMP order of operations for a name-based ping
- [ ] I can state the one-sentence DNS-vs-routing distinction and apply it to diagnose a given symptom
- [ ] I put the troubleshooting steps in the correct order and can justify that order
