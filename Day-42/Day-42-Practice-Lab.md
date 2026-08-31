# Day 42 Practice Lab — SSH: Secure Remote Access & Management

Work through these prompts yourself before checking the full lab manual.

## Brief

You've just racked a brand-new switch (SW2) with zero configuration. It needs to be securely reachable for remote administration, but only from one specific management workstation (PC1), which is two hops away across a routed WAN link.

## Topology

```text
PC1 -- SW1 -- R1 -- R2 -- SW2 -- Laptop1(console)
```
Two `/24` LANs connected by a `/30` transit link between R1 and R2.

(Same topology image as the original Day 42 lab: `Lab-Photos/Day-42-Lab-SSH.png`)

## Guided Questions

**Why an L2 switch needs a gateway**
1. SW2 is a Layer 2 device and doesn't route user traffic. So why does it still need `ip default-gateway` configured for PC1 (on a different subnet) to reach it over SSH?
2. What command would you use on a Layer 3 switch or router instead of `ip default-gateway`, and why is it different?

**Local authentication**
3. What's the difference between `enable password` and `enable secret`? Which should you always use, and why?
4. What does `login local` do differently from a plain line password?

**SSH prerequisites**
5. List every single thing SSH needs configured before it will work on an IOS device. What happens if you try `crypto key generate rsa` before setting a domain name?
6. Why is 2048 bits considered a meaningfully better choice than 512 bits for the RSA modulus?

**VTY lockdown**
7. What command removes Telnet as an option on the VTY lines, leaving only SSH? What's the actual security benefit of doing this, given SSH is already available?

**Access control**
8. You need to restrict SSH access to exactly one host, PC1. What ACL type do you use, and what's the one-line command?
9. Two commands can apply an ACL: `access-group` and `access-class`. Which one applies to VTY lines, and what's the practical consequence of using the wrong one by mistake (what error would you see, if any)?

**Putting it together**
10. Draw out (on paper or in your head) the full path a connection attempt from PC1 takes to reach SW2's CLI, in order, naming every security control it passes through.

## Configuration Checklist (write the commands yourself)

- [ ] Set hostname, enable secret, and a local username/password
- [ ] Configure the VLAN 1 SVI and default gateway
- [ ] Harden the console line (local auth + timeout)
- [ ] Set domain name and generate 2048-bit RSA keys
- [ ] Lock VTY lines to SSH-only with local auth and timeout
- [ ] Write a standard ACL permitting only PC1, and apply it correctly to the VTY lines
- [ ] Test SSH from PC1 and confirm privileged EXEC still requires the enable secret

## Self-Check

- [ ] I explained why an L2 switch needs a default gateway without just repeating the manual's wording
- [ ] I correctly identified `access-class` (not `access-group`) as the VTY command before checking
- [ ] I listed all 5+ SSH prerequisites without missing one
- [ ] I could trace the full connection path through every security layer from memory
- [ ] I kept a console session open as a fallback while testing the lockdown, and understand why that matters
