# Day 33 Practice Lab — IPv6 Static Routes, SLAAC, and Backup Paths (Self-Guided)

Companion to [`Day-33-Lab-Manual.md`](Day-33-Lab-Manual.md).

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 75–110 minutes. |
| **What you'll need** | Packet Tracer/GNS3, paper for tracing the primary vs backup path logic. |

---

## 1. The Brief

> Three routers: R1 and R3 each have a LAN with one PC, and are connected directly to each other (the primary path). R2 provides an indirect backup path to R1 and R3 via serial links. Hosts should get their IPv6 addresses automatically, with no manual entry and no DHCPv6 server. If the direct R1–R3 link fails, traffic should automatically reroute through R2 with no manual reconfiguration.

### Your task

- [ ] Sketch the topology and label, in your own words, which link is "primary" and which router/path is "backup." Draw the traffic flow arrow for PC1 → PC2 under normal conditions, and again under a simulated primary-link failure.
- [ ] What IPv6 host-addressing mechanism satisfies "automatic, no manual entry, no DHCPv6 server"? What does the acronym stand for?

---

## 2. Understand SLAAC Before Configuring Anything

Without opening the manual, answer these from what you already know about IPv6 (Day 31–32):

- [ ] What does the router send out its LAN interface to trigger host autoconfiguration? What multicast address does it go to?
- [ ] What information does that message actually contain — does it include the host's eventual address, or just part of it?
- [ ] What does the host do with the part it receives, to build its own complete address? (Hint: this should feel familiar from Day 32.)
- [ ] Why does this mechanism require the LAN to be exactly a /64 — what would break if the LAN prefix were /72 or /56 instead?
- [ ] Name one piece of information SLAAC does NOT provide to a host, that a host still commonly needs.

Compare your answers against Section 4.1 of the full manual before proceeding.

---

## 3. Design the Routing — Primary and Backup

**Constraints:**

- The direct R1–R3 link should always be preferred when it's up.
- The R2 path should only be used when the direct link is down — automatically, with no manual switchover.

### Your task

1. What routing concept lets two static routes to the same destination coexist, with one preferred and one used only as a fallback? What is the default value for a static route, and what must the backup route's value be relative to it (higher or lower — and why)?
2. On R1, you'll need a static route to reach PC2's LAN two different ways. Write out, in words (not yet CLI), what the next-hop should be for each of the two routes.
3. R2 sits in the middle of the backup path. Does R2 need its own static routes, or does it just relay traffic passively once cabled correctly? Justify your answer.
4. For R2's own static routes, would you reference a next-hop address, or just an outgoing interface? Under what topology condition is "just the interface" sufficient (revisit Day 32's link-local reasoning if needed)?

---

## 4. Build and Cable the Topology

- [ ] Place R1, R2, R3, PC1, PC2 with R1↔R3 direct, R1↔R2 serial, R2↔R3 serial.
- [ ] Confirm `ipv6 unicast-routing` is enabled on all three routers first.

---

## 5. Configure Every Device — Prompts Only

### 5.1 R1 and R3 LAN + direct link

- [ ] Assign each LAN interface a global IPv6 address and confirm IPv6 is active — what happens automatically the moment you do this, that you didn't have to separately request?
- [ ] Assign the direct R1↔R3 link addresses from the same /64.

### 5.2 Serial links (backup path)

- [ ] What single command per interface is needed to bring up IPv6 on the serial links, given they'll carry no global address (same reasoning as Day 32's WAN link)?
- [ ] Before writing any static route, run the command that shows you each router's actual generated link-local addresses. Why is this step non-optional rather than just trusting a hand calculation?

### 5.3 PCs

- [ ] What setting (not a manually-typed address) do you select on each PC to trigger SLAAC?

### 5.4 Static routes — R1 and R3

- [ ] Write the primary static route on R1 to reach PC2's LAN (via the direct link's global next-hop).
- [ ] Write the backup static route on R1 to reach PC2's LAN (via R2's relevant serial link-local address), including the administrative distance parameter.
- [ ] Mirror both for R3.
- [ ] Careful: R2 has a different link-local address on each of its two serial interfaces. Which one does R1's backup route need — the one facing R1, or the one facing R3?

### 5.5 Static routes — R2

- [ ] Write R2's two static routes (one per remote LAN). What form does the next-hop take, and why does the point-to-point nature of the serial links make that form sufficient?

---

## 6. Verify — Predict Before You Run

- [ ] Predict what `PC1> ipconfig` will show for its IPv6 address — will it be a short, clean-looking address like the ones you've hand-typed in earlier labs, or something else? Why?
- [ ] Predict what `show ipv6 route static` on R1 will show for the destination prefix `2001:DB8:0:3::/64` — how many entries, and what distinguishes them?
- [ ] Predict what `show ipv6 route 2001:DB8:0:3::/64` (without `static`) will show while the primary link is up, versus after you shut it down. Test both.
- [ ] Run a full PC1-to-PC2 ping test with the primary link up, then shut down R1's G0/1 (or R3's) and re-test. Did it work automatically, or did you need to change anything?

---

## 7. Explain Your Design

1. Explain SLAAC end-to-end in your own words — what the router does, what the host does, and why no DHCPv6 server is needed for addressing alone.
2. Why is a floating static route (administrative-distance-based backup) sufficient here instead of a dynamic routing protocol?
3. Why does R2, despite being "just" a backup path, need its own explicit static routes rather than routing automatically once cabled?
4. What would happen to failover behavior if you accidentally gave the backup route the same administrative distance as the primary?

---

## 8. Troubleshoot Yourself

Break your own lab in 2–3 ways, then diagnose and fix using only `show` commands:

- Give the backup route the same AD as the primary and observe what changes in `show ipv6 route`.
- Remove one of R2's two static routes and test failover.
- Reference the wrong R2 serial interface's link-local address in R1's backup route.

Write down: symptom, diagnostic command(s), fix.

---

## 9. Self-Check

- [ ] I explained SLAAC's router-side and host-side roles separately and correctly, without conflating them.
- [ ] I wrote both primary and backup static routes with correct AD values from memory before checking the manual.
- [ ] I correctly identified that R2 needs its own static routes despite being "just" a relay.
- [ ] I tested actual failover (shutting down the primary link) rather than just assuming the backup route would work.
- [ ] I intentionally broke and fixed at least 2 things without looking at the troubleshooting table first.

Once complete, open [`Day-33-Lab-Manual.md`](Day-33-Lab-Manual.md) and diff your work against Sections 4, 6–10.
