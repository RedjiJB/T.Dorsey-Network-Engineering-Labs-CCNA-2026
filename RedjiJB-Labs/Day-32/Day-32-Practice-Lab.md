# Day 32 Practice Lab — IPv6 EUI-64, Link-Local, and Static Routes (Self-Guided)

Companion to [`Day-32-Lab-Manual.md`](Day-32-Lab-Manual.md). The EUI-64 math and CLI are withheld — you derive and configure everything yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 90–120 minutes. The EUI-64 hand math takes longer than you expect the first time — budget for it. |
| **What you'll need** | Paper, a calculator that can do binary (or do it by hand — recommended at least once), Packet Tracer/GNS3. |

---

## 1. The Brief

> Two routers, R1 and R2, each have one LAN with one PC. They're connected by a WAN link that will carry no global IPv6 address — only automatically-generated addresses. Each router's LAN interface must get a global IPv6 address derived directly from that interface's MAC address, not typed arbitrarily.

### Your task

- [ ] What is the name of the address-generation algorithm that turns a 48-bit MAC address into a 64-bit IPv6 interface identifier?
- [ ] What automatically-generated address type will the WAN interfaces rely on entirely, since they'll never get a global address?

---

## 2. Derive Your Own EUI-64 Addresses — By Hand

**Given MAC addresses** (use these, or substitute your own router's actual interface MACs from `show interfaces` if working in a live lab):

- R1 G0/1 (LAN): `00:30:F2:36:45:02`
- R2 G0/1 (LAN): `00:21:63:80:B8:02`
- R1 G0/0 (WAN): `00:30:F2:36:45:01`
- R2 G0/0 (WAN): `00:21:63:80:B8:01`

### Your task — show every step, do not skip to the answer

For **each** of the four MAC addresses above:

1. Split the MAC exactly in half. Write both halves out.
2. Insert the fixed value that pads a 48-bit MAC to 64 bits. What is that value, and why is it always inserted in the middle rather than at either end?
3. Take the first byte of the MAC and write it out in full 8-bit binary.
4. Identify bit position 7 (counting 1–8, left to right) — circle it.
5. Flip that bit (0→1 or 1→0) and convert the byte back to hex.
6. Assemble the final 64-bit interface identifier as four hextets.
7. For the two LAN interfaces, prepend the routed prefix (`2001:DB8::/64` for R1's LAN, `2001:DB8:0:1::/64` for R2's LAN) to get the full global address. For the two WAN interfaces, prepend `FE80::` instead — what's different about how you write out this second case, and why does it not need a routed prefix?

Only after completing this for all four MACs, compare against Section 4.2–4.3 of the full manual.

### Follow-up questions

- [ ] What does the U/L bit mean in a standard burned-in MAC address (0 vs 1)? What does it mean, by IPv6 convention, once flipped into an EUI-64 identifier?
- [ ] Why is "flip the last bit" or "flip the first bit" wrong as a description of this process? Where exactly is bit 7, precisely?

---

## 3. Build and Cable the Topology

- [ ] Place R1, R2, one switch/direct link per LAN, PC1, and PC2. Connect R1–R2 directly (WAN link).
- [ ] Confirm `ipv6 unicast-routing` is enabled on both routers before proceeding (Day 31 recap — don't skip this).

---

## 4. Configure Every Device — Prompts Only

### 4.1 LAN interfaces (R1 G0/1, R2 G0/1)

- [ ] Using your hand-derived addresses from Part 2, write the two commands needed to assign each router's LAN interface its global IPv6 address.

### 4.2 WAN interfaces (R1 G0/0, R2 G0/0)

- [ ] What single command enables IPv6 on an interface without assigning it any global address at all? What address type does the interface get automatically as a result?

### 4.3 Static routes

- [ ] Before configuring anything, run the command that shows you the *actual* link-local address each router generated on its WAN interface (don't trust your hand calculation blindly for this step — why not?).
- [ ] Write the static route command on R1 that lets it reach R2's LAN, using R2's WAN link-local address as the next-hop.
- [ ] Write the mirror-image static route on R2.
- [ ] What happens to this static route configuration if the WAN interfaces are later given global addresses instead — does the static route need to change? Why or why not?

### 4.4 PCs

- [ ] Configure PC1 and PC2 with their IPv6 addresses and gateways (the routers' LAN-side global addresses you derived in Part 2).

---

## 5. Verify — Predict Before You Run

- [ ] Before running it, predict what `show ipv6 interface brief` will show for R1's WAN interface — how many addresses, and what will the "global" column say?
- [ ] Predict what `show ipv6 route` will show as the route type (letter code) for the static route you configured, versus the directly-connected LAN.
- [ ] Predict whether `ping <R2's LAN global address>` from PC1 will show TTL=255 or something lower. Why? Test it and compare.

---

## 6. Explain Your Design

1. Why does IPv6 static routing commonly use a link-local address as the next-hop on point-to-point links, rather than requiring a global address?
2. What is the business/security reasoning for deliberately NOT assigning a global address to the WAN link in this lab?
3. In your own words, explain what the "7th bit" flip accomplishes and why it's necessary for EUI-64 addresses to be considered valid.
4. What would go wrong if you typed a static route's next-hop as a link-local address you copied from the wrong interface?

---

## 7. Troubleshoot Yourself

Break your own lab in 2-3 ways, then fix using only `show` commands:

- Configure a static route with a next-hop link-local address that's one character off from the real one.
- Forget `ipv6 enable` on one WAN interface.
- Swap which router's static route points to which prefix (misconfigure the destination prefix).

Write down: symptom, diagnostic command(s) used, fix.

---

## 8. Self-Check

- [ ] I hand-derived all four EUI-64/link-local addresses through every step (split, FFFE, bit-flip) without skipping to a shortcut.
- [ ] I can state precisely which bit position is flipped and why, without hedging.
- [ ] I configured the WAN interfaces as link-local-only and explained why.
- [ ] I wrote both static routes with link-local next-hops from memory before checking the manual.
- [ ] I intentionally broke and fixed at least 2 things without looking at the troubleshooting table first.

Once complete, open [`Day-32-Lab-Manual.md`](Day-32-Lab-Manual.md) and diff your work against Sections 4, 6–10.
