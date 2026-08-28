# Day 51 Practice Lab — Dynamic ARP Inspection (Self-Guided)

No-answers companion to `Day-51-Lab-Manual.md`. Requires Day 50's DHCP Snooping lab already working — DAI has nothing to validate against without it.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1–1.5 hours. |
| **Prerequisite** | Day 50 (DHCP Snooping) fully working, with a real entry in `show ip dhcp snooping binding`. |

---

## 1. The Brief

> On top of your already-working DHCP Snooping deployment (R1 as DHCP server, SW1/SW2 snooping-enabled), add Dynamic ARP Inspection to defeat ARP spoofing attacks. Infrastructure links (router-to-switch, switch-to-switch) should be trusted for ARP purposes; end-user ports must remain untrusted and fully inspected. Add extra validation so spoofed packets that manipulate the Ethernet-header-vs-ARP-body relationship are also caught, not just simple IP/MAC mismatches.

### Your task

- [ ] Before configuring anything: what single existing data structure does DAI need to already exist and be populated in order to validate anything at all? Why can't DAI work on a switch that has never run DHCP Snooping?
- [ ] Sketch which interfaces on SW1 and SW2 should be trusted for DAI. Is this necessarily identical to which interfaces were trusted for DHCP Snooping in Day 50? Reason through it before checking.

---

## 2. Configure — Prompts Only

### 2.1 Enable DAI

- [ ] What single command enables ARP inspection for a given VLAN? What happens to ARP traffic in that VLAN before you also configure trust states?

### 2.2 Trust boundary

- [ ] On SW1, which interface(s) should be trusted for DAI? Consider all infrastructure-facing links, not just the one that carries DHCP server traffic.
- [ ] On SW2, which interface should be trusted?
- [ ] Write the exact commands for both switches.

### 2.3 Additional validation

- [ ] DAI's base check compares an ARP packet's claimed IP-to-MAC binding against a table populated by a different feature — which one, and which command populates it?
- [ ] There are three additional validation keywords you can add to a single command to catch spoofing techniques the base check misses. What does each of the three actually compare? (Hint: think about what fields exist in an Ethernet frame header versus what fields exist inside the ARP payload itself.)
- [ ] Write the command enabling all three.

---

## 3. Verify — Predict First

- [ ] Before running it, predict what `show ip arp inspection interfaces` will show for each interface's trust state on both switches.
- [ ] Predict what would happen if you enabled DAI on a switch where `show ip dhcp snooping binding` is completely empty. Then, if you can safely test it in your lab, try it and observe.
- [ ] Run `show ip arp inspection` and identify which of the three additional validation checks are enabled.

---

## 4. Explain Your Design

1. Describe an ARP spoofing attack in plain language, as if explaining to a non-technical manager, including what an attacker gains from it.
2. Why does DAI depend on DHCP Snooping's binding table instead of maintaining its own independent record?
3. Why might DAI's trusted-interface set differ from DHCP Snooping's trusted-interface set on the same switch, even though both features are "trust infrastructure, inspect the edge"?
4. What's the practical difference in what DHCP Snooping protects versus what DAI protects? Could a device pass one and still attempt an attack the other catches?
5. Why would a network with statically-assigned (non-DHCP) devices need special handling (like an ARP ACL) for DAI to work correctly for those devices?

---

## 5. Troubleshoot Yourself

Break your lab 2–3 ways, diagnose with `show` commands only, then fix:

- Enable DAI on a VLAN where the DHCP Snooping binding table is empty (simulate by clearing it if your platform allows, or reasoning through the predicted symptom).
- Forget to trust an infrastructure link for DAI and observe legitimate traffic get inspected/dropped.
- Enable only one of the three additional validation checks and reason about what kind of spoofing would still get through.

---

## 6. Self-Check

- [ ] I confirmed my DHCP Snooping binding table was populated before enabling DAI.
- [ ] I configured DAI's trust boundary from memory/reasoning, not by copying Day 50's DHCP Snooping trust set blindly.
- [ ] I could explain what each of the three additional validation checks catches.
- [ ] I could explain all 5 design questions in Section 4 out loud.
- [ ] I broke and fixed at least 2 things myself.

Once complete, open `Day-51-Lab-Manual.md` and diff against Sections 6, 7, and 9.
