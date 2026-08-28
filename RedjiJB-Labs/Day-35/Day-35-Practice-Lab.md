# Day 35 Practice Lab — Extended ACLs: Destination and Port-Based Filtering (Self-Guided)

Companion to [`Day-35-Lab-Manual.md`](Day-35-Lab-Manual.md). Builds on the Day 34 topology — reuse your own Day 34 build (or the reference one) rather than starting over.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 75–100 minutes. |
| **What you'll need** | A working Day 34 topology (OSPF fully routed), and a port/protocol reference (build your own from memory first, then check). |

---

## 1. The Brief

> On top of the existing Day 34 network, enforce three new policies:
>
> A. Hosts in 172.16.2.0/24 cannot communicate with PC1 (172.16.1.1) at all — any protocol.
> B. Hosts in 172.16.1.0/24 cannot use SRV1's DNS service — but every other service on SRV1 must remain reachable.
> C. Hosts in 172.16.2.0/24 cannot access SRV2's HTTP or HTTPS services — but every other service on SRV2 must remain reachable.

### Your task

- [ ] For each of the three policies, decide: could a standard ACL (source-only) satisfy this policy without blocking more than intended? Justify your answer for each one individually — don't just assume "no" for all three without checking.

---

## 2. Design the ACL Logic — On Paper First

For **each** policy, answer these before writing any CLI:

1. What protocol keyword do you need — `ip` (any protocol), `tcp`, `udp`, or `icmp`? How do you decide?
2. What is the source match (subnet + wildcard, or a specific host)?
3. What is the destination match (subnet + wildcard, `host <ip>`, or `any`)?
4. Does this policy need a port operator? If so, which port(s), and what IOS keyword or number represents each?
5. Does the policy need one `deny` line or more than one? (Hint: think carefully about Policy C.)

### Follow-up

- [ ] Look up (or recall) the port numbers for HTTP, HTTPS, and DNS. Which protocol (TCP or UDP) does each normally use?
- [ ] Why is there no port number associated with ICMP the way there is with TCP/UDP services?
- [ ] Why can't a single ACL line with a port `range` cleanly express "port 80 or port 443" without overreaching?

Only after completing this for all three policies, compare against Section 4 and 6 of the full manual.

---

## 3. Configure Each Policy — Prompts Only

### 3.1 Policy A

- [ ] Write the extended named ACL configuration commands (creation, the deny line, the trailing permit).
- [ ] Which interface and direction should this be applied to, to stop the traffic as close to PC1 as possible without affecting LAN2's other traffic?

### 3.2 Policy B

- [ ] Write the extended named ACL for this policy, including the correct protocol and port keyword for DNS.
- [ ] This lab's stated policy only mentions standard DNS queries. What additional line would a fully DNS-blocking policy need, that this one doesn't require? Why?

### 3.3 Policy C

- [ ] Write the extended named ACL for this policy. How many `deny` lines does it need, and why?
- [ ] Both Policy B and Policy A are scoped to traffic entering R1 from a LAN. If both need to apply to R1 G0/0, what constraint do you run into, and how do you resolve it? (Hint: how many ACLs can one interface have per direction?)

---

## 4. Verify — Predict Before You Run

- [ ] Before testing, predict: will `ping` from a Policy-B-restricted host to SRV1 succeed or fail? Justify using the protocol match you wrote.
- [ ] Before testing, predict: after Policy C is applied, will a Policy-C-restricted host be able to reach SRV2 via SSH (if present)? Why or why not?
- [ ] Build a full reachability matrix (at least 8 pairs, covering all three policies plus at least 2 "should still work" cases) and predict each outcome before testing.
- [ ] Run `show ip access-lists <name>` before generating any traffic, then again after your reachability tests — what do you expect to change, and why?

---

## 5. Explain Your Design

1. For each of the three policies, explain in one or two sentences why a standard ACL could not have expressed it correctly.
2. Why does Policy C need two `deny` lines instead of one, and why would a `range` operator be the wrong tool here?
3. Explain why ICMP traffic is unaffected by a `deny tcp` or `deny udp` line, even when the same source/destination pair is named.
4. What real IOS constraint forces you to combine Policies A and B into a single ACL if they're both scoped to the same interface and direction?

---

## 6. Troubleshoot Yourself

Break your own lab in 2–3 ways, then diagnose and fix using only `show` commands:

- Write a deny line with the wrong protocol keyword (e.g., `tcp` for a UDP service).
- Forget the second `deny` line for Policy C (HTTPS).
- Omit the trailing `permit ip any any` on one ACL.

Write down: symptom, diagnostic command(s), fix.

---

## 7. Self-Check

- [ ] I determined, for each policy, whether a standard ACL could work — and correctly concluded it could not, with a specific justification each time.
- [ ] I wrote all three extended ACLs from memory/lookup before checking the manual.
- [ ] I correctly identified that Policy C needs two deny lines, not a range.
- [ ] I predicted and verified that ICMP remains unaffected by protocol-specific deny rules.
- [ ] I intentionally broke and fixed at least 2 things without looking at the troubleshooting table first.

Once complete, open [`Day-35-Lab-Manual.md`](Day-35-Lab-Manual.md) and diff your work against Sections 4, 6–10.
