# Day 44 Practice Lab — Static NAT

Work through these prompts yourself before checking the full lab manual.

## Brief

Three internal PCs on a private LAN need permanent, individually dedicated public-facing addresses so they can reach the internet, each always presenting the same public identity.

## Topology

- PC1, PC2, PC3 on a private `172.16.0.0/24` LAN
- R1 connects the private LAN to a WAN link toward an "Internet Router"
- A pool of public addresses (`100.0.0.0/24`) is available for NAT use

(Same topology as the original Day 44 lab.)

## Guided Questions

**Terminology (get this exactly right)**
1. Define, in your own words, all four of: inside local, inside global, outside local, outside global. Then map each term to a specific address in this lab's topology.
2. In this lab, outside local and outside global happen to be identical addresses. Why? Under what circumstance would they differ?

**Why NAT is needed**
3. Predict what happens if PC1 tries to ping `8.8.8.8` before any NAT is configured. Why, specifically, does this fail (what's true about `172.16.0.0/24` that makes this predictable)?

**Configuration**
4. What two interface-level commands does NAT require before any translation can happen, and on which physical interfaces (LAN-facing vs. WAN-facing) does each belong?
5. Write the static NAT command that maps 172.16.0.2 to 100.0.0.2. What happens (be specific) if you get the source/destination order backwards?

**Verification and behavior**
6. After configuring static NAT and generating a ping and a DNS lookup from PC1, you check `show ip nat translations`. Predict how many entries you'll see and what protocol each one will show.
7. You run `clear ip nat translation *`. Predict which entries disappear and which remain. Justify your prediction using what "static" actually means.

**Static vs. other NAT types**
8. What's the key operational difference between static NAT (this lab) and PAT (port address translation, used for general internet access from many clients)? When would you choose one over the other?

## Configuration Checklist (write the commands yourself)

- [ ] Test connectivity before NAT (expect failure)
- [ ] Designate the inside and outside interfaces
- [ ] Configure three static one-to-one NAT mappings
- [ ] Test connectivity again (expect success)
- [ ] Generate ICMP and DNS traffic from each PC
- [ ] Examine the translation table and statistics
- [ ] Clear translations and verify which entries remain

## Self-Check

- [ ] I can correctly define and place all four NAT terms without checking notes
- [ ] I correctly predicted the pre-NAT ping failure and explained why
- [ ] I correctly predicted which entries survive `clear ip nat translation *`
- [ ] I can explain the operational tradeoff between static NAT and PAT
- [ ] I configured and tested this myself, not just read the manual's output
