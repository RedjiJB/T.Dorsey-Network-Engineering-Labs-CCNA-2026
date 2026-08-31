# Day 45 Practice Lab — Dynamic NAT & PAT

Work through these prompts yourself before checking the full lab manual.

## Brief

Three internal PCs need outbound internet access. You'll first configure Dynamic NAT with a deliberately small address pool to see what happens when it runs out, then replace it with PAT and prove that limitation disappears.

## Topology

- PC1, PC2, PC3 on `172.16.0.0/24`
- R1 with inside (LAN) and outside (WAN) interfaces
- A 2-address NAT pool: `100.0.0.1`–`100.0.0.2`

(Same topology as the original Day 45 lab: `Lab-Photos/Day-45-Lab-Dynamic-NAT.png`)

## Guided Questions

**Dynamic NAT setup**
1. Dynamic NAT needs a way to say "which inside hosts are eligible for translation." What tool accomplishes this, and what's the exact command to match all of `172.16.0.0/24`?
2. What command creates a pool of exactly two addresses, `100.0.0.1` and `100.0.0.2`? What command then activates Dynamic NAT using that pool and the ACL from question 1?

**Predicting exhaustion**
3. Before testing anything, predict: PC1 and PC2 both generate traffic successfully. What do you predict happens when PC3 tries? Justify your prediction using the pool size and host count.
4. Is this a bug, or expected behavior? What would you tell someone who thought this was "Dynamic NAT being broken"?

**Switching to PAT**
5. Before adding the PAT configuration, what two things should you do to the existing Dynamic NAT setup, and why does skipping them cause confusing verification output later?
6. What's the exact command that enables PAT using R1's own outside interface address? What single keyword is doing the actual work of allowing multiple hosts to share one address?

**Comparing translation tables**
7. Predict what `show ip nat translations` will show after all three PCs generate traffic under PAT. Specifically: how many distinct inside-global IP addresses will you see, and what will distinguish the three sessions from each other?

**Terminology check**
8. Under PAT, is "inside global" still a per-host concept the way it was under Static NAT (Day 44) and Dynamic NAT? Explain what changes.

## Configuration Checklist (write the commands yourself)

- [ ] Configure inside/outside interfaces
- [ ] Write the ACL matching the inside network
- [ ] Create the 2-address NAT pool and bind it via `ip nat inside source list`
- [ ] Generate traffic from all 3 PCs and observe pool exhaustion
- [ ] Clear translations and remove the Dynamic NAT pool binding
- [ ] Configure PAT with `overload`
- [ ] Generate traffic from all 3 PCs again and confirm all succeed

## Self-Check

- [ ] I correctly predicted PC3's failure under Dynamic NAT and explained why
- [ ] I identified `overload` as the specific keyword that enables port-based sharing
- [ ] I explained why cleanup (clear translations, remove old pool binding) matters before switching strategies
- [ ] I correctly predicted the PAT translation table's structure before checking
- [ ] I can explain, in NAT terminology, exactly what's different about "inside global" under PAT vs. Dynamic NAT
