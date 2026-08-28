# Day 34 Practice Lab — Standard ACLs with OSPF-Routed Connectivity (Self-Guided)

Companion to [`Day-34-Lab-Manual.md`](Day-34-Lab-Manual.md).

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 90–130 minutes. |
| **What you'll need** | Packet Tracer/GNS3, paper for wildcard mask derivation and policy-to-placement mapping. |

---

## 1. The Brief

> Two routers connect four subnets: two internal LANs (172.16.1.0/24, 172.16.2.0/24) behind R1, and two server subnets (192.168.1.0/24 hosting SRV1, 192.168.2.0/24 hosting SRV2) behind R2. First, get full routing connectivity between all four subnets using OSPF. Then enforce these five policies:
>
> 1. Only PC1 (172.16.1.1) and PC3 (172.16.2.1) may reach SRV1.
> 2. 172.16.1.0/24 may not reach 172.16.2.0/24.
> 3. 172.16.2.0/24 may not reach 172.16.1.0/24.
> 4. 172.16.2.0/24 may not reach SRV2.
> 5. (Same restriction as #2, enforced independently from R2's side.)
>
> Use numbered ACLs on R1 and named ACLs on R2.

### Your task

- [ ] Before any configuration, write out — in plain English, not CLI — exactly what each of the five policies requires, and which router/interface is closest to each policy's "source" traffic.

---

## 2. Design the Addressing and Wildcard Masks

### Your task — pencil and paper first

1. Write out the IPv4 addressing table yourself (device, interface, IP, subnet) based on the brief above — you may choose any valid addressing scheme consistent with the four subnets stated.
2. For each subnet, derive its wildcard mask by hand from its subnet mask — show the bitwise-NOT working, don't just state the answer.
3. Explain, in one sentence, the relationship between a wildcard mask used in an ACL and a wildcard mask used in an OSPF `network` statement — are they the same concept, or different?
4. What is the wildcard mask equivalent of matching exactly one host address? What is the ACL keyword shortcut for it?

Only after completing all 4 steps, compare against Section 4 of the full manual.

---

## 3. Configure OSPF — Prompts Only

- [ ] What router-mode command starts an OSPF process, and what optional-but-recommended identifier should you set explicitly rather than let auto-select?
- [ ] For each directly-connected subnet you want OSPF to advertise, what's the command pattern (including wildcard mask) to include it?
- [ ] Both routers have LAN-facing interfaces with real end hosts and no other routers. What OSPF feature stops hello packets from being sent out those interfaces, while still advertising the subnet? Apply it to the correct interfaces on both routers.
- [ ] Predict, before testing: will removing `passive-interface` from a LAN interface break anything visible in a lab this small? Why might it still be considered best practice regardless?

---

## 4. Configure the Five ACL Policies — Prompts Only

For each policy, answer three questions before writing any CLI: **(a)** what rule logic satisfies it, **(b)** which router and interface should the ACL be applied to, and **(c)** which direction (in/out)?

### 4.1 Policy 1 (R1, numbered ACL): Only PC1 and PC3 reach SRV1

- [ ] Since standard ACLs can't match on destination, how do you scope this policy to "only affects traffic toward SRV1's subnet" using interface placement alone?
- [ ] Write the ACL (a) permitting exactly two specific hosts and (b) denying everything else. What's the ACL-line shortcut for matching a single host without writing out a wildcard?

### 4.2 Policies 2 and 3 (R1, numbered ACLs): mutual isolation between 172.16.1.0/24 and 172.16.2.0/24

- [ ] These are two separate ACLs, not one — why can't a single ACL enforce a bidirectional block?
- [ ] For each direction, which interface and which direction (in/out) stops the traffic earliest, closest to its source?

### 4.3 Policy 4 (R2, named ACL): 172.16.2.0/24 cannot reach SRV2

- [ ] Write the named ACL creation syntax (not the numbered form) for this policy.
- [ ] What's the practical difference between a named and numbered standard ACL — is it a filtering-capability difference or something else?

### 4.4 Policy 5 (R2, named ACL): reinforce the 172.16.1.0/24 → 172.16.2.0/24 block from R2's side

- [ ] Where on R2 would this ACL need to be applied to catch traffic before it reaches R1's segment from the other direction?

---

## 5. Verify — Predict Before You Run

- [ ] Predict, before running it, what `show ip ospf neighbor` will show once both routers are configured — what state indicates full adjacency?
- [ ] Predict how many entries `show ip access-lists` will show for ACL 3, and what the match counters will read immediately after configuration (before any traffic is generated).
- [ ] Build your own reachability matrix (at least 6 source/destination pairs, including at least one from each policy) — predict success/fail for each before testing.

---

## 6. Explain Your Design

1. Why build full OSPF connectivity before applying any ACLs, instead of designing routing and security together from the start?
2. What's the practical difference between a standard ACL and having simply not run OSPF's `network` statement for a subnet at all — both "hide" a subnet in some sense, don't they? Why are they not equivalent?
3. Explain, without notes, why a standard ACL cannot express "block this subnet from this specific service on that server, but allow everything else to that server."
4. For each of the five policies, justify your placement choice (interface + direction) using the "block near the source" principle — where does it apply cleanly, and is there any policy where the "right" placement is less obvious?

---

## 7. Troubleshoot Yourself

Break your own lab in 2–3 ways, then diagnose and fix using only `show` commands:

- Apply one of the ACLs to the wrong interface.
- Apply an ACL in the wrong direction (in instead of out, or vice versa).
- Forget the trailing `permit any` on one ACL and observe what breaks beyond the intended policy.

Write down: symptom, diagnostic command(s), fix.

---

## 8. Self-Check

- [ ] I derived every wildcard mask by hand from a subnet mask, without guessing or copying a memorized table.
- [ ] I configured OSPF and confirmed full adjacency before writing a single ACL line.
- [ ] I reasoned through interface/direction placement for each policy before checking the manual's answer.
- [ ] I built and tested a reachability matrix covering all five policies.
- [ ] I intentionally broke and fixed at least 2 things without looking at the troubleshooting table first.

Once complete, open [`Day-34-Lab-Manual.md`](Day-34-Lab-Manual.md) and diff your work against Sections 4, 6–10.
