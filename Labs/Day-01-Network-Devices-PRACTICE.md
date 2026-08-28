# Day 01 Practice Lab — Network Devices & Enterprise Topology (Self-Guided)

This is the **no-answers companion** to [`Day-01-Network-Devices.md`](Day-01-Network-Devices.md). It gives you the same business requirements and topology, but withholds the addressing plan and CLI commands — you work them out yourself. Use the full manual only to check your work after you've attempted each part, not before.

Do not open the full manual until you've made a genuine attempt at each section below. If you get stuck for more than ~15 minutes on any one step, that's the signal to peek at the corresponding section of the full manual, note what you missed, and continue — not to copy the rest wholesale.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | Give yourself 3–4 hours. This will take longer than the guided version — that's expected and correct. |
| **What you'll need** | Packet Tracer (or your GNS3 build of this lab), a blank sheet/spreadsheet for your addressing plan, and nothing else. Do not have the full manual open in a second tab while attempting each section. |
| **Grading yourself** | After each part, compare against the full manual's corresponding section. Note discrepancies — did you make a typo, a conceptual error, or choose a *valid but different* design? Only the third is acceptable to leave uncorrected. |

---

## 1. The Brief (read this like a client requirements doc)

> Your company operates two branch offices: **New York** and **Tokyo**. New York is a small user-facing office — a couple of employee workstations that need internet access. Tokyo hosts sensitive production servers and needs its security controls placed as close to those servers as possible, not several hops downstream.
>
> Both offices connect to a shared WAN/internet core, represented by a router named `ISP-RTR`. An external laptop, `ATTACKER`, sits on that WAN core to represent an outside party — your design must prevent it from reaching internal hosts by default, while still allowing your Tokyo web server to be reached from outside if you explicitly choose to publish it.
>
> Each branch needs a switch, a router, and a firewall. New York's firewall should protect the WAN edge, after the router has made its routing decisions. Tokyo's firewall should sit immediately off the switch, inspecting traffic before it ever reaches the router — because the servers are the most sensitive asset in that branch.
>
> This is a small, static network — you don't yet have a reason to run a dynamic routing protocol. Use static and default routes.

### Your task

Sketch (on paper or in Packet Tracer) a topology that satisfies this brief. Before checking the manual:

- [ ] How many total devices does this require? List them by role (not hostname yet).
- [ ] Draw the traffic flow through each branch as an arrow diagram, the way `PC → Switch → Router → Firewall → Internet` was shown in the full manual — but derive New York's and Tokyo's flows yourself from the brief above, don't copy that example.
- [ ] Explain, in your own words, *why* Tokyo's firewall placement differs from New York's. Write 2–3 sentences — you'll need this reasoning again in Part 6.

---

## 2. Design Your Own IP Addressing Plan

You are given only the following constraints. Everything else is your decision.

**Constraints:**

- Use private address space for all internal LANs (RFC 1918).
- Use `203.0.113.0/24` (a documentation range, standing in for public IP space) for anything WAN-facing/public in this lab.
- New York's LAN needs to comfortably support a few dozen future devices, not just the 2 PCs it starts with.
- Tokyo's LAN needs the same headroom.
- Every router-to-router and router-to-firewall point-to-point link should use the *smallest* subnet that correctly fits exactly 2 hosts — no larger.
- The link between `ISP-RTR` and `ATTACKER` should be sized for up to 6 hosts (not 2, not 254) — pick the correct prefix length for that requirement and justify it.

### Your task — do this with pencil and paper (or a spreadsheet), not a subnet calculator

1. Choose a `/24` for the New York LAN and a different `/24` for the Tokyo LAN, both from private address space. Write out which RFC 1918 range you chose and why.
2. For each of the 4 point-to-point links in your topology (NY router↔NY firewall, NY firewall↔ISP-RTR, Tokyo firewall↔Tokyo router, Tokyo router↔ISP-RTR), calculate by hand:
   - How many host bits are required for exactly 2 usable addresses? Show the `2^h − 2` math.
   - What prefix length does that give you?
   - What is the resulting subnet mask in dotted decimal? Derive it from binary — don't just recall it.
3. For the ISP-RTR ↔ Attacker link (sized for 6 hosts), do the same calculation: find the smallest `h` such that `2^h − 2 ≥ 6`, and derive the prefix length and mask.
4. For **one** of your `/30` links, write out by hand:
   - The network address
   - The first usable host address
   - The last usable host address
   - The broadcast address
5. Assign every device's IP address, building a full address table like the one in the full manual (Device / Interface / IP / Mask / Connects To). Make sure every point-to-point link's two ends fall in the *same* subnet, and every LAN device's default gateway matches its router/firewall's LAN-facing IP.

Only after completing all 5 steps above, compare against Section 4 of the full manual. If your subnet sizes or structure differ but are still internally consistent and correctly sized, that's fine — the goal is correct methodology, not an identical answer.

---

## 3. Build and Cable the Topology

- [ ] Place all devices in Packet Tracer (or GNS3) per your Part 1 sketch.
- [ ] Cable everything, verifying link lights are green/active before moving on.
- [ ] Double check interface numbering matches what your platform actually assigned — don't assume `Gi0/0` exists if your router model uses `Fa0/0`.

---

## 4. Configure Every Device — Prompts Only

For each device below, you're given **what to accomplish**, not the commands. Work from your own knowledge of Cisco IOS/ASA syntax and mode structure. If you don't remember a command, that's useful information — write down what you had to look up, and review it afterward.

### 4.1 Both switches (New York and Tokyo)

- [ ] Set an appropriate hostname reflecting the branch and role.
- [ ] Set a privileged-mode password using the *encrypted* method (not the plaintext one) — which command is that, and why does it matter?
- [ ] Apply weak encryption to any remaining plaintext passwords in the config with a single global command.
- [ ] Add a legal warning banner shown at login.
- [ ] Configure the management VLAN interface with an IP from your LAN plan, bring it up, and set the correct command (not a routing command — switches don't route) so the switch can reach devices off its own subnet for management purposes.
- [ ] Configure access ports for each end device (PC or server), including a label describing what's connected and a feature that skips the STP startup delay for host-facing ports.
- [ ] Configure the uplink port toward the router/firewall.
- [ ] Enable SSH: what three prerequisites does IOS require before SSH will function (hint: one relates to naming, one to cryptography, one to authentication)? Configure all three, then restrict remote access to SSH only.
- [ ] Save your configuration using the correct command — what's the difference between the two ways to do this (`copy running-config startup-config` vs. its shorthand)?

### 4.2 Both routers (New York and Tokyo branch routers)

- [ ] Hostname, encrypted privileged password, password encryption service, banner (same reasoning as the switch).
- [ ] Disable the router's tendency to try DNS-resolving mistyped commands — what's the command, and what problem does skipping this cause if you forget it?
- [ ] Console and SSH access, same prerequisites as the switch.
- [ ] Configure the LAN-facing interface with the correct IP from your plan, and bring it up. (What's the single most common reason a freshly configured interface stays down?)
- [ ] Configure the interface facing your branch's firewall.
- [ ] Add whatever static/default route each router needs to reach the rest of the topology. Think carefully about direction: does New York's router route toward its firewall, or does something else happen given the two different firewall placements? Justify your route choice per branch.
- [ ] Save.

### 4.3 ISP-RTR (the WAN core router)

- [ ] Basic hostname/hardening/banner as above.
- [ ] Configure all interfaces facing New York, Tokyo, and the Attacker.
- [ ] Does ISP-RTR need any static routes beyond its directly connected interfaces? Think about which branch's firewall sits *behind* an extra router hop, and what that implies for how ISP-RTR learns to reach that firewall's outside address.
- [ ] Save.

### 4.4 Both firewalls (New York and Tokyo, Cisco ASA 5505)

This is the hardest part — ASA syntax is a different CLI family from IOS. Prompts only:

- [ ] Basic hostname, domain name, enable and login passwords (note: the ASA's plaintext privileged password command has a different name than IOS's — look it up rather than guessing IOS syntax here).
- [ ] The ASA 5505 has 8 built-in switchports split across two VLANs. Assign the correct physical port to VLAN 2 (outside) and another to VLAN 1 (inside) for your topology — which physical port faces which neighbor depends on your branch's firewall placement, so this differs between New York and Tokyo. Work out which is which before configuring.
- [ ] Configure both VLAN interfaces: each needs a name (`nameif`), a trust level (`security-level`, 0–100), and an IP address from your plan. Which VLAN gets the higher trust level, and why?
- [ ] Add static routes so the ASA knows how to reach: (a) any internal subnet not directly connected to it, and (b) everything else via a default route out the outside interface.
- [ ] Configure NAT so internal private addresses can reach the internet — what ASA feature translates many internal IPs to one interface IP, and what are the two configuration objects/commands needed to set it up?
- [ ] **Tokyo only, optional stretch:** publish one server's web service (TCP/80) to the outside world using a *static* NAT (different from the dynamic NAT above) plus an explicit ACL permitting only that port. Why does this need a different NAT type than your general outbound traffic?
- [ ] Save (note: the ASA's save command differs from IOS's `copy running-config startup-config`).

### 4.5 End devices (PCs, servers, attacker laptop)

- [ ] Assign IP address, subnet mask, and default gateway to each, per your Part 2 addressing plan.
- [ ] The attacker laptop needs no further configuration — but make sure you can articulate *why* it has no route back into either private LAN by design.

---

## 5. Verify — Without Being Told What "Success" Looks Like First

Before checking the full manual's Expected Output Gallery, predict what you *should* see, then run the command and compare.

- [ ] On each router, run the command that lists every interface with its IP and up/down status. **Before running it**, predict: which interfaces should show `up/up`? Which (if any) should show `administratively down`, and why would that ever be correct?
- [ ] On each router, run the command that lists the routing table. **Before running it**, write out on paper what routes you expect to see (connected + static) and compare.
- [ ] On each ASA, find the command that shows configured NAT rules, and the command that shows *active* translations. Run the first one before generating any traffic, and the second one after pinging from an internal host — what changes between the two, and why?
- [ ] Build a ping/reachability matrix yourself: for at least 6 source/destination pairs across your topology, predict success or failure *before* testing, and write your reasoning. Then test and compare. Include at least one pair involving the attacker laptop.
- [ ] Run a traceroute from a New York PC to a Tokyo server. Predict the hop-by-hop path first.

---

## 6. Explain Your Design

Answer these in your own words, in writing, without referencing the full manual:

1. In business terms, why would a company actually build a network shaped like this? (Don't just describe the topology — explain the business reasoning, the way Section 2 of the full manual does.)
2. Why does New York's firewall sit after its router, while Tokyo's sits before? Use the phrase "closest to the asset" somewhere in your answer if it applies, and explain why it does or doesn't.
3. Why did you choose static routing instead of a dynamic routing protocol for this design? Under what circumstances would that choice change?
4. Why is a `/30` the right size for a router-to-router link, and why would using a `/24` there be a design smell even though it would technically still function?
5. What's the difference between the dynamic NAT/PAT you configured for general outbound traffic and the static NAT you'd use to publish a server? Why can't one mechanism do both jobs?

---

## 7. Troubleshoot Yourself

Before opening the full manual's troubleshooting table, deliberately break your own lab in 3 different ways (pick 3 from below), then diagnose and fix each one using only `show` commands:

- Remove `no shutdown` from one interface.
- Delete a static/default route from one router.
- Remove the NAT configuration from one firewall.
- Set `login` without a `password` (or vice versa) on a VTY line, then try to SSH in.
- Assign the wrong VLAN to a physical port on one of the ASAs.

For each, write down: the symptom you observed, the diagnostic command(s) you used to narrow it down, and the fix. Compare your process against Section 12 of the full manual afterward — did you find it faster, slower, or the same way?

---

## 8. Self-Check

- [ ] I designed the addressing plan by hand, including deriving at least one subnet mask from binary, without a subnet calculator.
- [ ] I configured every device from memory/lookup, not by copying the full manual.
- [ ] I predicted verification output before running each command, and compared afterward.
- [ ] I could explain all 5 design-reasoning questions in Section 6 out loud to someone else.
- [ ] I intentionally broke and fixed at least 3 things without looking at the troubleshooting table first.

If any box is unchecked, that's your specific gap — go back to that section specifically rather than re-doing the whole lab.

Once you've completed this practice pass, open [`Day-01-Network-Devices.md`](Day-01-Network-Devices.md) and diff your work against Sections 4, 6–10, 12, and 13 in detail.
