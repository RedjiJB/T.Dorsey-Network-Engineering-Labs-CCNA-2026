# Day 49 Practice Lab — Port Security (Self-Guided)

No-answers companion to `Day-49-Lab-Manual.md`. Same topology and brief, prompts only.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1–1.5 hours. |
| **What you'll need** | Packet Tracer/GNS3, a second device or MAC-spoofing method to trigger violations. |

---

## 1. The Brief

> SW1's ports F0/1–F0/3 each serve exactly one known, static device in a security-sensitive area — treat any second MAC address as a serious event that should fully disable the port until investigated. SW2's G0/1 serves a shared room where up to 4 legitimate devices may appear over time, and you don't want to hand-type their MAC addresses — but a 5th device should be blocked without taking the room offline.

### Your task

- [ ] Before writing any config, decide: which violation mode fits SW1's requirement, and which fits SW2's? Write your reasoning in 1–2 sentences each.
- [ ] Which port security feature avoids hand-typing SW2's expected MAC addresses?

---

## 2. Configure — Prompts Only

### 2.1 SW1 (F0/1–F0/3)

- [ ] What must be true about a port's switchport mode before `switchport port-security` will be accepted?
- [ ] Set the correct maximum MAC count for "exactly one device, ever."
- [ ] Set the violation mode that fully disables the port (which of the three modes is this?).
- [ ] Add an aging time so a decommissioned device's MAC doesn't permanently occupy the slot — what unit does aging time use?

### 2.2 SW2 (G0/1)

- [ ] Set the correct maximum for "up to 4 legitimate devices."
- [ ] Set the violation mode that keeps the port operational but still logs and drops excess traffic — how does this differ from the third, "silent" violation mode you're not using here?
- [ ] Enable the feature that dynamically learns and saves secure MACs from observed traffic instead of static typing.

---

## 3. Trigger and Recover — Do This Without Looking Ahead

- [ ] Introduce a second MAC address on one of SW1's ports (swap a device or spoof a MAC). Predict what you'll see in `show interfaces status` before checking.
- [ ] Introduce a 5th MAC on SW2's port. Predict whether the port stays up or goes down, and whether legitimate traffic under the limit keeps working.
- [ ] For the SW1 port you just disabled, work out — without looking at documentation — the two-command sequence that manually recovers an err-disabled interface.

---

## 4. Verify — Predict First

- [ ] Before running it, predict what fields `show port-security interface f0/1` will display, and what "Port Status" value you expect on a normal (no violation) port vs. a violated shutdown-mode port.
- [ ] Run `show port-security interface g0/1` after a violation. What's different about "Port Status" compared to SW1's violated port? Why?
- [ ] Check whether your sticky-learned MACs show up in `show running-config`. What do you need to do to make sure they survive a reload?

---

## 5. Explain Your Design

1. Why might the same company use two different violation modes on two different ports, rather than one policy everywhere?
2. What's the practical difference between `restrict` and `protect` violation modes? Why would a security team almost always prefer `restrict`?
3. Why does sticky learning require a config save to persist, when the switch already "knows" the MAC the moment it's learned?
4. What does port security fundamentally identify traffic by, and what's one way an attacker could try to get around a MAC-based control like this?
5. Why is 802.1X often described as a stronger control than port security, and why might a company still choose port security anyway for some ports?

---

## 6. Troubleshoot Yourself

Break your lab 2–3 ways, diagnose with `show` commands only, then fix:

- Try enabling port security on a port still in trunk mode.
- Set a `maximum` lower than the number of legitimate devices actually present on SW2's port.
- Forget to save config after sticky MACs are learned, then simulate a reload (or just check `show startup-config` vs `show running-config`).

---

## 7. Self-Check

- [ ] I chose the correct violation mode for each switch based on the brief, before checking the manual.
- [ ] I configured both switches from memory/lookup, not by copying the manual.
- [ ] I predicted verification output before running each command.
- [ ] I could explain all 5 design questions in Section 5 out loud.
- [ ] I broke and recovered at least 2 things myself.

Once complete, open `Day-49-Lab-Manual.md` and diff against Sections 6, 7, and 9.
