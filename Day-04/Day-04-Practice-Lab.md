# Day 04 Practice Lab — Basic Device Security & Cisco IOS Administration (Self-Guided)

No-answers companion to `Day-04-Lab-Manual.md`. Same brief and topology; you derive the commands yourself.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 1–1.5 hours. |
| **What you'll need** | Packet Tracer, nothing else. |

---

## 1. The Brief

> You've been handed a fresh router (R1) and switch (SW1), both at factory defaults, with three PCs already cabled to the switch. Before this network goes anywhere near production, you need to apply baseline security: meaningful hostnames, a properly hashed privileged-mode password, encrypted line passwords, secured console and remote-access lines (SSH only, no Telnet, individually attributable logins), and a legal banner. Both the router and the switch need identical treatment.

### Your task

- [ ] Before touching the CLI, list every distinct security control this brief is asking for, one per line. You should end up with roughly 6–8 items.

---

## 2. Design a Minimal Addressing Plan

- [ ] This lab has one LAN, one router interface, and one switch management interface needing IPs, plus three PCs. Pick a `/24` from private address space and assign all 5 addresses yourself. No point-to-point link exists in this lab — why not?

---

## 3. Configure — Prompts Only

Work through these for **both** R1 and SW1. Do not look up the exact syntax until you've tried from memory first.

- [ ] Set a hostname reflecting each device's role.
- [ ] Configure a privileged-mode password using the *plaintext-storable* method first (you'll fix it in the next step) — which command is that?
- [ ] Run `show running-config` and observe the problem. Write down, in your own words, exactly what an attacker who glimpsed this output would now know.
- [ ] Configure the *correct*, hashed privileged-mode password method — which command, and why does IOS prefer it over the one you set above if both exist?
- [ ] Apply one global command that encrypts any remaining plaintext passwords in the config. What class of password does this **not** protect (hint: think about what "encryption" actually means here vs. hashing)?
- [ ] Secure the console line. What are the *two* separate commands required, and what specifically breaks if you only configure one of them?
- [ ] Configure SSH-only remote access with individually attributable logins. This requires three prerequisites before SSH will even function — name all three before configuring anything (hint: one is about naming, one about cryptography, one about authentication). Then configure a local username, and restrict the VTY transport to SSH only, explaining why the default setting is a security problem.
- [ ] Add a banner. What's the legal argument for having one at all?
- [ ] Configure SW1's management IP so it's reachable for SSH. What command does a Layer 2 switch use to reach off-subnet management traffic (it is NOT `ip route`)?
- [ ] Save both devices' configuration. What are the two equivalent ways to do this on IOS?

---

## 4. Verify — Predict First

- [ ] Before running it, predict exactly what `show running-config` will show for your enable secret line (hash-looking string, or the actual password?). Run it and compare.
- [ ] Predict what happens if you attempt Telnet to R1 after your VTY configuration. Test it.
- [ ] Predict what happens if you SSH in with a wrong username. Test it.
- [ ] Compare `show startup-config` and `show running-config` after saving — what should be true about the two outputs?

---

## 5. Explain Your Design

1. State the difference between `enable password` and `enable secret` in one sentence each, and which one IOS uses if both are configured.
2. Why does `password` alone on a line not actually secure anything?
3. Why is SSH preferred over Telnet, specifically — what does Telnet expose that SSH doesn't?
4. Why is `login local` with individual usernames better than a single shared VTY password, from a real-world incident-response perspective?
5. What does `service password-encryption` protect against, and what does it explicitly NOT protect against (compare it honestly to `enable secret`'s hashing)?

---

## 6. Troubleshoot Yourself

Break your lab in 3 of these ways, diagnose with `show` commands only, then fix:

- Set `password` on the console line without `login`.
- Leave `transport input all` on the VTY lines instead of restricting to SSH.
- Configure `enable password` but forget `enable secret` entirely, then check what `show running-config` reveals.
- Forget to generate the RSA key before configuring SSH, and observe exactly what fails.

---

## 7. Self-Check

- [ ] I listed all 6–8 security controls from the brief before starting, and configured all of them on both devices.
- [ ] I demonstrated the plaintext `enable password` vulnerability myself, then fixed it with `enable secret`.
- [ ] I could explain, without notes, the `password`+`login` pairing requirement.
- [ ] I named all three SSH prerequisites before configuring SSH.
- [ ] I broke and fixed at least 3 things using only `show` commands.

Once done, open `Day-04-Lab-Manual.md` and diff your work against Sections 6, 7, and 9.
