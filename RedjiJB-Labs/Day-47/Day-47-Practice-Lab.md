# Day 47 Practice Lab — QoS, DSCP Marking & Traffic Classification (Self-Guided)

This is the no-answers companion to `Day-47-Lab-Manual.md`. Same topology and brief, but you derive the DSCP math and CLI yourself. Don't open the full manual until you've made a genuine attempt at each section.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1.5–2 hours. |
| **What you'll need** | Packet Tracer (or your GNS3 build), Simulation Mode, and a calculator-free approach to DSCP math — do it by hand. |

---

## 1. The Brief

> Your company runs one WAN link between R1 and R2. Three traffic types cross it: HTTPS (checkout/transactional, treat as delay-sensitive), HTTP (general browsing), and ICMP (monitoring). You need HTTPS to get a small guaranteed slice of bandwidth *and* jump-the-line priority treatment. HTTP and ICMP just need guaranteed minimums, no priority queue, with HTTP getting double ICMP's share.

### Your task

- [ ] Identify which interface, on which router, is the correct place to apply an *outbound* shaping policy for traffic leaving toward the WAN, given the topology.
- [ ] Write out, in your own words, the difference between "priority queue" and "bandwidth guarantee" before reading any further.

---

## 2. Derive the DSCP Values Yourself

You are given only the naming convention formulas:

```text
AFxy = (x × 8) + (y × 2)     where x = class (1-4), y = drop precedence (1-3)
CSn  = n × 8
```

**Your task — pencil and paper, no lookup tables:**

1. HTTPS should be marked AF31. Compute its decimal value by hand, then convert to hex.
2. HTTP should be marked AF32. Compute its decimal value, then convert to hex.
3. ICMP should be marked CS2. Compute its decimal value, then convert to hex.
4. Bonus: what decimal/hex value would AF33 be? What about CS4? Compute both without looking anything up.

Only after you've written all of these down, verify against Section 4.1 of the full manual.

---

## 3. Configure — Prompts Only

### 3.1 Classification

- [ ] Create three class-maps, one per traffic type. What Cisco IOS feature lets you match traffic by protocol name (`https`, `http`, `icmp`) instead of writing raw ACLs for TCP port 443/80? What match-type keyword do you use when a class only has one condition?

### 3.2 Policy definition

- [ ] Build a policy-map. For HTTPS: which command gives a class a genuine low-latency priority queue, distinct from a plain bandwidth guarantee? Assign it 10%.
- [ ] For HTTP: which command guarantees a *minimum* bandwidth share without priority treatment? Assign it 10%.
- [ ] For ICMP: same command type as HTTP, but assign 5%.
- [ ] Add the correct `set` command under each class to mark it with the DSCP value you derived in Part 2.

### 3.3 Apply

- [ ] Which single command actually makes a policy-map affect real traffic? What two things must you specify (direction, and where)?
- [ ] Apply it on the correct interface and direction based on your Part 1 answer.

---

## 4. Verify — Predict Before You Run

- [ ] Before running any command, predict what `show policy-map interface <your-interface>` will show immediately after configuration, with zero traffic generated yet. Then run it and compare — were the byte/packet counters what you expected?
- [ ] Generate an ICMP ping from PC1 to SRV1, then re-run the same command. What should have changed?
- [ ] Open a packet in Simulation Mode for each of the three traffic types. Before expanding the IP header, predict the DSCP hex value you should see, then confirm.
- [ ] For an HTTP packet, what TCP destination port do you expect? For HTTPS?

---

## 5. Explain Your Design

Answer in writing, without the full manual open:

1. Why does QoS not "create" bandwidth? What does it actually control?
2. Why is classification always the first step, before marking or queuing can happen?
3. Why might a company deliberately mark HTTPS differently from HTTP even though both are "web traffic"?
4. Why does this lab's policy only affect traffic in one direction? What would you need to add to also shape the return path from SRV1 to PC1?
5. What's the practical difference between `priority percent 10` and `bandwidth percent 10` if the link becomes fully congested?

---

## 6. Troubleshoot Yourself

Deliberately break your own lab in 2–3 ways, then diagnose using only `show` commands:

- Remove the `service-policy` command from the interface.
- Swap the `match protocol` value between the HTTP and HTTPS class-maps.
- Apply the policy `input` instead of `output`.

For each: write the symptom, the diagnostic command you used, and the fix.

---

## 7. Self-Check

- [ ] I derived all three DSCP decimal/hex values by hand, plus the two bonus values, without a lookup table.
- [ ] I could write the full `class-map` → `policy-map` → `service-policy` config from memory.
- [ ] I predicted verification output before running each command.
- [ ] I could explain all 5 design questions in Section 5 out loud to someone else.
- [ ] I broke and fixed at least 2 things without looking at the troubleshooting table first.

Once complete, open `Day-47-Lab-Manual.md` and diff your work against Sections 4, 6, 7, and 9 in detail.
