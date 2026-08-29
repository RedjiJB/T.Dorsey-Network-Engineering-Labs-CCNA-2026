# Day 38 Lab Manual — DNS Configuration and Name Resolution

## 0. Metadata

| Field | Value |
|---|---|
| Objective | Configure DNS resolution on end hosts and a Cisco router, including a default route toward simulated internet, local static host entries, and external name resolution — and clearly separate what DNS does from what routing does |
| CCNA 200-301 Domains | 4.0 IP Services (DNS operation and configuration), 3.0 IP Connectivity (default/static routing), 1.0 Network Fundamentals (client configuration) |
| Prerequisites | Basic static routing, IPv4 addressing, client IP configuration (address/mask/gateway) |
| Estimated Time | 45–60 minutes |
| Difficulty | Beginner–Intermediate |

## 1. Lab Overview + Learning Objectives

Every time a user types a website name instead of an IP address, DNS is doing the translation work behind the scenes — and that translation is a completely separate process from the routing that actually delivers the resulting packets. This lab builds both halves explicitly: a default route so R1 can reach a simulated internet, and DNS configuration (on both R1 and three client PCs) so names can actually be resolved to addresses — then uses packet-level inspection to show, step by step, that DNS resolution happens *before* any ICMP traffic is even generated.

By the end of this lab you will be able to:

1. Configure a default static route so an edge router can forward traffic for any network it doesn't have a specific route to.
2. Configure DNS server settings on end hosts (`ipconfig`-visible) and on a Cisco router (`ip name-server`).
3. Create and verify local static hostname-to-IP entries on a router (`ip host`), and explain how they differ from a DNS server lookup.
4. Trace the full order of operations when a client resolves a hostname: local cache, DNS query, response, then (only then) the actual ICMP traffic.
5. Clearly separate what DNS is responsible for (name → address) from what routing is responsible for (address → path), and explain why a failure in one looks similar to, but is diagnosed differently from, a failure in the other.
6. Apply a systematic, ordered troubleshooting method that isolates a DNS failure from a routing/connectivity failure.

## 2. Business Context

No end user in a real company navigates by IP address — every internal application, file share, and external website is reached by name, and DNS is the invisible infrastructure making that possible. When DNS breaks (wrong server configured, DNS server unreachable, or a missing/incorrect record), the symptom users report is usually "the internet is down" or "I can't get to the file server," even though routing and connectivity are often completely fine — the destination just can't be *found* by name. This lab builds the specific skill of recognizing that distinction quickly: is this a DNS problem (can't resolve a name) or a routing/connectivity problem (can't reach an address)? Misdiagnosing one as the other is one of the most common early-career troubleshooting mistakes, and this lab's structured troubleshooting method exists specifically to prevent it.

## 3. Topology Reference

| Device | Role |
|---|---|
| R1 | Internal gateway router; has a default route to the simulated internet, and its own DNS server configured |
| SW1 | Internal LAN switch |
| PC1, PC2, PC3 | Internal clients, each configured to use the DNS server at 1.1.1.1 |
| Internet Router | Simulated ISP edge, connected to R1 via a point-to-point link |
| DNS Server | Answers DNS queries at 1.1.1.1 |
| Web Server | Represents an external site (`youtube.com`), reached only after DNS resolves its name |

Topology image (original author's diagram, reused here):
`https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-38-Lab-DNS.png`

## 4. IP Addressing Plan

### 4.1 Why Sized This Way

The internal LAN is a single `/24`, generously sized for the three clients present with room to grow — standard access-layer sizing. The R1–Internet Router link is a `/30`, the minimum-waste sizing for a point-to-point connection. The DNS server's address (`1.1.1.1`) sits outside both of these ranges, representing an external, internet-reachable resource — deliberately not part of the internal addressing scheme, to make clear that DNS in this lab is being resolved *across* the default route, not locally.

### 4.2 Manual Calculation Walkthrough

```
192.168.0.0/24  (internal LAN)
Host bits = 32 - 24 = 8 → 2^8 = 256 total addresses
Usable hosts = 256 - 2 = 254
Network address:    192.168.0.0
First usable host:  192.168.0.1
Last usable host:    192.168.0.254   (assigned to R1's G0/1 as the LAN gateway)
Broadcast address:   192.168.0.255
```

```
203.0.113.0/30  (R1-Internet Router link)
Host bits = 32 - 30 = 2 → 2^2 = 4 total addresses
Usable hosts = 4 - 2 = 2   ✓ exactly enough for a point-to-point link
Network address: 203.0.113.0, usable: .1 (R1) - .2 (Internet Router), broadcast: .3
```

### 4.3 Address Table

| Device | Interface | IPv4 Address | Default Gateway | DNS Server |
|---|---|---|---|---|
| R1 | G0/0 | 203.0.113.1/30 | — | 1.1.1.1 |
| R1 | G0/1 | 192.168.0.254/24 | — | 1.1.1.1 |
| Internet Router | connected interface | 203.0.113.2/30 | — | — |
| PC1 | Fa0 | 192.168.0.1/24 | 192.168.0.254 | 1.1.1.1 |
| PC2 | Fa0 | 192.168.0.2/24 | 192.168.0.254 | 1.1.1.1 |
| PC3 | Fa0 | 192.168.0.3/24 | 192.168.0.254 | 1.1.1.1 |
| DNS Server | server interface | 1.1.1.1 | configured | — |
| Web Server | server interface | resolved via DNS | configured | — |

## 5. Pre-Configuration Checklist

- [ ] Confirm internal LAN addressing and R1's interfaces are already up before configuring DNS — DNS is meaningless without underlying IP connectivity
- [ ] Plan the default route on R1 before DNS — a client can successfully query DNS and get an answer, but still fail to reach the destination if R1 has no route to it
- [ ] Decide the DNS server address every client and R1 itself will point to (this lab: 1.1.1.1, consistent everywhere)
- [ ] Plan local static host entries on R1 (`ip host`) as a separate, non-DNS mechanism for internal name resolution — useful for router-to-router or router-to-server names that don't need a full DNS infrastructure

## 6. Configuration Tasks

### 6.1 Configure a default route on R1

```
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2
```
Mode: global configuration. This is a static route matching *any* destination (`0.0.0.0 0.0.0.0` as network/wildcard means "no bits need to match") and forwards it to `203.0.113.2`, the next hop toward the simulated internet. Without this, R1 has no way to forward traffic for any external network — including the DNS query itself, and the eventual ICMP traffic to the resolved address. Memory aid: "the default route is the router's own fallback gateway — the same concept as a PC's default gateway, one level up."

### 6.2 Configure DNS on the client PCs

```
PC1> ipconfig
   IPv4 Address:    192.168.0.1
   Subnet Mask:     255.255.255.0
   Default Gateway: 192.168.0.254
   DNS Server:      1.1.1.1
```
Repeat identically for PC2 (`192.168.0.2`) and PC3 (`192.168.0.3`), same gateway and DNS server. The DNS Server field tells the client where to send name-resolution queries — this is a completely separate setting from the default gateway, even though both are commonly the same device in small networks. Here they're deliberately different (gateway = 192.168.0.254, DNS server = 1.1.1.1) to make clear DNS traffic still has to be *routed* to reach its server, exactly like any other traffic.

### 6.3 Configure DNS resolver and local host entries on R1

```
R1(config)# ip name-server 1.1.1.1
R1(config)# ip host PC1 192.168.0.1
R1(config)# ip host PC2 192.168.0.2
R1(config)# ip host PC3 192.168.0.3
```
Mode: global configuration. `ip name-server` sets which DNS server *R1 itself* uses when told to resolve a name (relevant if you ever `ping <hostname>` from R1 for something not in its local host table). `ip host <name> <ip>` creates a static local entry — this is not DNS at all, it's IOS's own local table, checked first and requiring no external server or network reachability. Memory aid: "`ip host` = router's own local phonebook; `ip name-server` = who to call when the local phonebook doesn't have the entry."

## 7. Verification Steps

| Command | Where | Purpose |
|---|---|---|
| `show ip route` | R1 | Confirm the default route is installed |
| `ipconfig /all` | PC1/PC2/PC3 | Confirm IP, gateway, and DNS server settings took effect |
| `show hosts` | R1 | Confirm local static host entries are present |
| `ping PC1` | R1 | Confirm R1 resolves the local hostname via `ip host`, not DNS |
| `ping youtube.com` | PC1 | Confirm end-to-end DNS resolution plus routed connectivity to the resolved address |
| Simulation Mode / packet capture | PC1 | Directly observe the DNS query/response occurring before any ICMP packet |

### Expected Output Gallery

```
R1# show ip route
Gateway of last resort is 203.0.113.2 to network 0.0.0.0

S*   0.0.0.0/0 [1/0] via 203.0.113.2
C    192.168.0.0/24 is directly connected, GigabitEthernet0/1
C    203.0.113.0/30 is directly connected, GigabitEthernet0/0
```
`S*` identifies a static route flagged as the candidate default route.

```
PC1> ipconfig /all
IP Address..........: 192.168.0.1
Subnet Mask..........: 255.255.255.0
Default Gateway......: 192.168.0.254
DNS Server...........: 1.1.1.1
```

```
R1# show hosts
Host    Address
PC1     192.168.0.1
PC2     192.168.0.2
PC3     192.168.0.3
```

```
R1# ping PC1
Translating "PC1"...domain server (1.1.1.1) [OK]
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.0.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms
```
Note IOS still says "Translating... domain server" even for a local `ip host` entry — the local table is simply checked first, and only a genuine miss would fall through to an actual DNS query against `1.1.1.1`.

```
PC1> ping youtube.com
Pinging youtube.com [172.217.6.78] with 32 bytes of data:
Request timed out.
Reply from 172.217.6.78: bytes=32 time=45ms TTL=115
Reply from 172.217.6.78: bytes=32 time=41ms TTL=115
Reply from 172.217.6.78: bytes=32 time=44ms TTL=115
```
The first request commonly times out while DNS resolution and/or ARP completes; subsequent replies confirm the name resolved correctly and the resulting address is reachable.

## 8. Common Mistakes (80/20)

1. **Forgetting the default route and assuming it's a DNS problem** — a client can successfully resolve a name (DNS working correctly) but still fail to ping it if R1 has no path to the resolved address; always check `show ip route` before assuming DNS is broken.
2. **Configuring the DNS server address wrong on only some clients** — inconsistent behavior across PCs is a classic symptom of exactly this, easy to miss if you only test from one client.
3. **Confusing `ip host` (local static entry) with actual DNS** — `ip host` entries work with zero network dependency and don't involve the configured `ip name-server` at all unless there's a miss; assuming a working `ping <hostname>` from R1 proves DNS is configured correctly is a common false conclusion.
4. **Not distinguishing "DNS server unreachable" from "DNS server has no record"** — both produce a failed name lookup, but the fix and the diagnostic command are different (routing verification vs. checking the record itself).
5. **Testing with a hostname first instead of the DNS server's IP** — jumping straight to `ping youtube.com` skips confirming basic reachability to the DNS server itself, wasting time when the underlying problem is actually routing, not DNS.

## 9. Troubleshooting Guide

| Step | Check | Command | If it fails |
|---|---|---|---|
| 1 | Is the client's own IP configuration correct? | `ipconfig /all` | Correct IP/mask/gateway/DNS server |
| 2 | Can the client reach its default gateway? | `ping <gateway>` | Fix local Layer 2/3 connectivity |
| 3 | Can the client reach the DNS server by IP? | `ping 1.1.1.1` | If this fails, it's a routing problem, not DNS |
| 4 | Is the correct DNS server configured? | `ipconfig /all` (again, deliberately) | Correct the DNS Server field |
| 5 | Does the hostname resolve at all? | `nslookup <hostname>` or `ping <hostname>` | If resolution fails but step 3 succeeded, the record may not exist — check the DNS server itself |
| 6 | Does R1 have a route to the resolved address? | `show ip route` on R1 | Add/correct the default or specific route |
| 7 | Does the resolved address respond directly? | `ping <resolved-IP>` | If this also fails, isolate to a routing/connectivity problem entirely separate from DNS |

## 10. Design Analysis

The alternative to DNS — requiring users to know and type IP addresses — doesn't scale past a handful of destinations and breaks immediately if a server's address ever changes; DNS decouples "what humans refer to" from "where it actually lives," which is precisely why it's foundational internet infrastructure rather than a convenience feature. Static `ip host` entries are a lightweight alternative for small, stable, internal-only name sets (a handful of routers or servers) where standing up full DNS infrastructure would be overkill — but they don't scale (every device needs its own copy) and don't update dynamically, which is exactly why real networks use them only for a small number of core infrastructure devices, not for general client name resolution.

## 11. Real-World Parallel

Every enterprise network runs internal DNS (often Microsoft AD-integrated DNS, or BIND) for internal names, and forwards or relies on external DNS (their ISP's, or a public resolver like this lab's `1.1.1.1`) for internet names — the client-side configuration in this lab (a DNS server address handed out alongside IP/gateway, commonly via DHCP in real deployments) is exactly how every corporate laptop gets its DNS settings. The "DNS identifies the address, routing reaches the address" distinction taught here is the first diagnostic split any network or help-desk engineer makes when a user reports "I can't get to X."

## 12. Stretch Goal

Configure a second, secondary DNS server on the clients and simulate the primary DNS server becoming unreachable — observe how long resolution takes (or whether it fails) before falling back, and consider what that implies about DNS server redundancy in a real deployment. Separately, try `ip domain-lookup` behavior on R1 (enabled by default) versus disabling it (`no ip domain-lookup`) and observe how that changes what happens when you mistype a command at the R1 CLI.

## 13. Self-Assessment

- [ ] I can state, precisely, what DNS is responsible for versus what routing is responsible for
- [ ] I configured the default route, client DNS settings, and R1's `ip name-server`/`ip host` entries myself
- [ ] I can explain why `ping PC1` succeeding on R1 doesn't necessarily prove DNS (versus the local host table) is working
- [ ] I traced the full order of operations for `ping youtube.com`, from local cache check through DNS query through ICMP traffic
- [ ] I can use the ordered troubleshooting method to isolate a DNS failure from a routing failure, not just guess
- [ ] I verified my configuration with `show ip route`, `show hosts`, `ipconfig /all`, and actual ping tests

## 14. Key Concepts Demonstrated / What I Learned / Skills Practiced

**Key Concepts:** DNS name resolution, `ip name-server`, `ip host` static entries, default static routing, DNS-vs-routing separation of concerns, DNS query/response order of operations, structured DNS-vs-connectivity troubleshooting.

**What I Learned:** DNS and routing solve genuinely independent problems that only look related because a failure in either one produces the same user-visible symptom ("can't reach the website"). A successful DNS resolution proves nothing about whether the resolved address is actually reachable, and a working route to an address proves nothing about whether that address can be found by name in the first place — which is exactly why the troubleshooting method in this lab tests them as separate, ordered steps rather than as one combined check.

**Skills Practiced:** Default static route configuration, client DNS configuration, router-side DNS resolver and local host table configuration, `show ip route`/`show hosts` verification, packet-level tracing of DNS query/response order, structured DNS-vs-routing troubleshooting.

## 15. GNS3 Lab

See `RedjiJB-Labs/Day-38/GNS3/build_lab.py` and its companion `README.md` for an automated build of this topology using a VyOS router (R1), an Open vSwitch LAN switch, and Alpine Linux end hosts and servers — see the README for how to stand up a lightweight DNS server on an Alpine node (`dnsmasq`) as an open-source stand-in for the lab's simulated DNS server.
