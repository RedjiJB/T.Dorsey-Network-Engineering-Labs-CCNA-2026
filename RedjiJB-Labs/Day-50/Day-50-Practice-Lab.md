# Day 50 Practice Lab — DHCP Snooping (Self-Guided)

No-answers companion to `Day-50-Lab-Manual.md`. Same topology and brief, prompts only.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1.5–2 hours. Budget extra time — this lab has a real troubleshooting twist, don't rush to the manual when it doesn't work the first time. |
| **What you'll need** | Packet Tracer/GNS3, patience for a legitimate multi-step diagnostic. |

---

## 1. The Brief

> R1 needs to be the sole authoritative DHCP server for 192.168.1.0/24, with the first 9 usable addresses reserved for static infrastructure. SW1 and SW2 sit between R1 and the clients and must run DHCP Snooping so that only R1's replies are ever accepted — any rogue DHCP server plugged into a client port must be silently defeated. Configure this, then get a real client (PC1) a working lease.

### Your task

- [ ] Before configuring anything, sketch the trust boundary: which single interface on SW1, and which single interface on SW2, should be trusted? Justify each choice from the topology, not by guessing.

---

## 2. Design the Addressing — By Hand

1. For `192.168.1.0/24`, write out the network address, first usable host, last usable host, and broadcast address.
2. The first 9 usable addresses are reserved for static infrastructure. What is the first address that should actually be available for dynamic lease?
3. How many total addresses remain available for DHCP lease after the exclusion? Show your subtraction.

---

## 3. Configure — Prompts Only

### 3.1 R1 as DHCP server

- [ ] Which command reserves an address range from ever being dynamically leased, and does it go inside or outside the DHCP pool block? Why does that ordering matter?
- [ ] Create a DHCP pool. What two pieces of information does it minimally need to hand out a usable IP configuration (beyond the network/mask itself)?

### 3.2 DHCP Snooping on both switches

- [ ] What two commands are required globally/per-VLAN before any per-interface trust setting has any effect at all?
- [ ] On SW1, which single interface should be marked trusted? On SW2, which one?
- [ ] What happens, by default, to every interface you do *not* explicitly trust?

### 3.3 First lease attempt

- [ ] Release and renew PC1's IP configuration. Does it succeed on the first try? If not, resist the urge to immediately assume your trust configuration is wrong — what else could be interfering, given that DHCP Snooping inserts additional information into forwarded DHCP packets by default?

---

## 4. Diagnose the Failure Yourself

If PC1 didn't get a lease:

- [ ] Check the DHCP Snooping status on each switch. Is the correct interface trusted? If yes, trust isn't your problem — what's the next thing DHCP Snooping does to packets besides trust enforcement?
- [ ] Research (or recall) what "Option 82" / "relay agent information" insertion is. Why might a switch inserting extra information into a DHCP packet cause a plain (non-relay-aware) DHCP server to reject or mishandle the request?
- [ ] What single global command on each snooping-enabled switch removes this behavior?
- [ ] After applying your fix, retry the lease. Did it succeed this time?

---

## 5. Verify — Predict First

- [ ] Before running it, predict what `show ip dhcp snooping` will show for the Trusted column on each switch.
- [ ] After a successful lease, predict what fields will appear in `show ip dhcp snooping binding` before running it.
- [ ] Why does this binding table matter for a completely different security feature covered in Day 51? (You don't need to have done Day 51 yet — just reason about what a MAC-to-IP-to-port table could be used to validate.)

---

## 6. Explain Your Design

1. Why is every switch port untrusted by default under DHCP Snooping, rather than trusted by default?
2. What specific attack does DHCP Snooping defend against? Describe it in your own words as if explaining to a non-technical manager.
3. Why did trusting the correct uplink interfaces alone not fully fix this lab? What extra factor was involved?
4. Why is DHCP Snooping enabled on *both* switches in the path instead of just the one closest to the clients?
5. Why does this lab reserve the first 9 addresses of the subnet instead of, say, the last 9?

---

## 7. Troubleshoot Yourself

Break your lab 2–3 ways, diagnose with `show` commands only, then fix:

- Trust the wrong interface on one switch (e.g., a client-facing port instead of the uplink).
- Forget to add the VLAN to DHCP Snooping's scope after enabling it globally.
- Re-enable Option 82 insertion after having disabled it, and confirm the lease breaks again.

---

## 8. Self-Check

- [ ] I calculated the full addressing plan by hand, including the exclusion math.
- [ ] I configured DHCP Snooping trust boundaries from memory/lookup, not by copying the manual.
- [ ] I hit the Option 82 failure myself (or deliberately re-triggered it) and diagnosed it without immediately jumping to the manual's answer.
- [ ] I could explain all 5 design questions in Section 6 out loud.
- [ ] I broke and fixed at least 2 things myself.

Once complete, open `Day-50-Lab-Manual.md` and diff against Sections 6, 7, and 9.
