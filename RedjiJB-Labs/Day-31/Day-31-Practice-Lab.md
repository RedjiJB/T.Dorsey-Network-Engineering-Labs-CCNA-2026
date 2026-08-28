# Day 31 Practice Lab — IPv6 Dual-Stack Configuration (Self-Guided)

This is the **no-answers companion** to [`Day-31-Lab-Manual.md`](Day-31-Lab-Manual.md). Same topology and brief, but the addressing plan and CLI commands are withheld — you derive them yourself.

Do not open the full manual until you've made a genuine attempt at each section. Stuck for more than ~15 minutes? Peek at the corresponding section, note what you missed, and continue.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 45–75 minutes. |
| **What you'll need** | Packet Tracer or your GNS3 build, and a blank sheet for your addressing plan. |

---

## 1. The Brief

> Your company has one router (R1) with three already-working IPv4 LANs, each with one PC. Leadership wants IPv6 added to all three LANs without touching the working IPv4 configuration — a dual-stack rollout.

### Your task

- [ ] What is the one router-wide command that must be issued before IPv6 will ever route between LANs, even if every interface already has a valid IPv6 address? (Don't look it up yet — write your best guess, then verify later.)
- [ ] Explain in your own words what "dual-stack" means, and why a company would choose it over an all-at-once IPv6 cutover.

---

## 2. Design Your Own IPv6 Addressing Plan

**Constraints:**

- Use the documentation prefix `2001:DB8::/32` (never used in production, safe for labs).
- Each LAN gets its own /64.
- The router's address in each LAN should follow the ordinary convention for "first usable address" in an IPv6 subnet — what is that convention, and how is it different from IPv4's "first usable address is typically .1" habit?

### Your task — pencil and paper first

1. Assign a distinct /64 to each of the three LANs, using the 4th hextet to distinguish them (e.g., `2001:DB8:0:1::/64`, `...0:2::/64`, `...0:3::/64`). Write out all three in full expanded form (no `::` shorthand) first, then compress them by hand — show your work.
2. For each LAN, assign the router's address and the PC's address.
3. Explain why you did **not** need to calculate host bits or a subnet mask the way you did for IPv4 subnetting in Day 1. What is structurally different about how IPv6 LANs are sized?
4. IPv6 subnetting is sometimes described as working on "nibble boundaries" instead of arbitrary bit counts. Looking at your three /64s above, which hex digit (nibble) is the only one that changes between them? What would it mean, structurally, to subnet mid-nibble instead — why is that avoided in practice?

Only after completing all 4 steps, compare against Section 4 of the full manual.

---

## 3. Build and Cable the Topology

- [ ] Place R1, three switches, and three PCs in Packet Tracer/GNS3, matching one router with three separate LANs.
- [ ] Confirm IPv4 is already fully working (ping between all three PCs) before adding any IPv6 configuration — this isolates any later failure as IPv6-specific.

---

## 4. Configure Every Device — Prompts Only

### 4.1 R1

- [ ] What one global-configuration command enables IPv6 forwarding on the router? What happens if you skip it — does the router give an error, or fail silently?
- [ ] For each of R1's three LAN interfaces: what two commands are needed to give it a global IPv6 address and ensure IPv6 is active on that interface?
- [ ] Every IPv6-enabled interface automatically gets a second kind of address you never explicitly configure. What is it called, what prefix range does it come from, and what is its scope (local link only, or routable across the network)?

### 4.2 PC1, PC2, PC3

- [ ] Each PC needs entries in **four** fields to be a working dual-stack host. List all four (hint: two are IPv4, two are IPv6).
- [ ] Why does a dual-stack host need two separate default gateway entries instead of one? What would happen to IPv6 traffic if only the IPv4 gateway were configured?

---

## 5. Verify — Predict Before You Run

- [ ] Before running it, predict what `show ipv6 interface brief` will show for each of R1's three interfaces — how many addresses per interface, and what type is each?
- [ ] Before running it, predict how many routes `show ipv6 route` will show, and what the `C` and `L` prefixes mean.
- [ ] Predict: will `ping 2001:DB8:0:2::2` from PC1 succeed? What has to be true on R1 for that to work? Test it.
- [ ] Run `ipconfig` on a PC and identify which line is the link-local address versus the global address, before checking the manual's answer.

---

## 6. Explain Your Design

Answer these without referencing the full manual:

1. Why is dual-stack the standard IPv6 migration strategy instead of a direct IPv4-to-IPv6 cutover?
2. Why does every IPv6 LAN in this lab use a /64, regardless of how many hosts are actually on it? Contrast this with how you sized IPv4 subnets in Day 1.
3. What is `2001:DB8::/32` and why is it safe to use in a lab (or any textbook) without ever conflicting with a real network?
4. Explain, in your own words, the two rules that let you compress a full 8-hextet IPv6 address into shorthand with `::`. Why can you only use `::` once per address?

---

## 7. Troubleshoot Yourself

Deliberately break your own lab in 2–3 ways, then diagnose and fix using only `show` commands:

- Remove `ipv6 unicast-routing` after everything else is configured — predict the symptom before you do it.
- Assign the wrong prefix length to one PC (e.g., /48 instead of /64).
- Leave the IPv6 gateway blank on one PC while the IPv4 gateway is still correct.

For each: write down the symptom, the diagnostic command you used, and the fix.

---

## 8. Self-Check

- [ ] I derived the IPv6 addressing plan by hand, including full-to-compressed conversion, without a subnet calculator.
- [ ] I could explain why IPv6 LAN sizing is structurally different from IPv4 subnetting, not just "because it's convention."
- [ ] I configured every device from memory/lookup, not by copying the full manual.
- [ ] I predicted verification output before running each command.
- [ ] I intentionally broke and fixed at least 2 things without looking at the troubleshooting table first.

Once complete, open [`Day-31-Lab-Manual.md`](Day-31-Lab-Manual.md) and diff your work against Sections 4, 6–10.
