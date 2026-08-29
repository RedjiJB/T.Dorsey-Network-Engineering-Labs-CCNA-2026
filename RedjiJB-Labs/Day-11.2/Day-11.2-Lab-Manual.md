# Day 11.2 Lab Manual — Troubleshooting Static Routes

---

## 0. Metadata

| Field | Value |
|---|---|
| **Objective** | Diagnose and repair three independent, pre-seeded misconfigurations (one per router) in an otherwise-correct static routing topology, restoring end-to-end connectivity using a structured troubleshooting methodology. |
| **Exam Relevance** | CCNA 200-301 — Domain 4 (IP Connectivity): troubleshoot static routing; Domain 5 is lightly touched via systematic diagnosis method. This lab is process-focused, not concept-introduction-focused. |
| **Prerequisites** | Day 11.1 (Configuring Static Routes) — this lab assumes you can already build the topology correctly and is entirely about finding what's *wrong* with one that isn't. |
| **Time Estimate** | 45–75 minutes. |
| **Difficulty** | ⭐⭐☆☆☆ (Beginner-Intermediate) — the CLI is identical to Day 11.1; the added difficulty is diagnostic discipline, not new commands. |

---

## 1. Lab Overview

Day 11.1 taught you to build static routing from a blank slate. Real network engineering is overwhelmingly the opposite: staring at a network that *used to work*, or was *supposed to* work, and figuring out why it doesn't. This lab hands you the same three-router topology from Day 11.1, except each router has exactly one deliberate fault planted in it. Your job isn't to reconfigure from scratch — it's to find the *one wrong thing* on each device using `show` commands, fix only that, and verify.

### 1.1 Learning Objectives

By the end of this lab you will be able to:

- Apply a structured, repeatable troubleshooting methodology (verify → inspect → isolate → fix → validate) instead of guessing
- Distinguish an interface-layer fault from a routing-layer fault using the right `show` command
- Read a routing table critically, looking for what's *missing* or *wrong*, not just what's present
- Make a single, minimal corrective change rather than re-configuring an entire device
- Re-verify end-to-end after each fix, confirming the specific fault is resolved before moving to the next router

---

## 2. Business Context

**Why would a real company do this?**

No production network stays perfectly configured forever. A junior engineer fat-fingers a subnet mask during a maintenance window. A change ticket updates one router's route but the engineer forgets the router two hops away also needed an update. A cable gets swapped during a rack move and an interface ends up on the wrong IP. None of these are exotic failures — they are the single most common category of "the network is down" tickets a real NOC handles.

- **"Support says the office can't reach headquarters, starting an hour ago"** → this is exactly the symptom this lab opens with: a working topology that suddenly (or was always) partially broken, with the failure isolated to *one* device somewhere in the path.
- **"We can't just re-image every router when something breaks"** → hence the discipline of finding and fixing the *specific* fault instead of wiping and rebuilding, which is rarely possible on a live production network anyway.
- **"Document what you found and fixed"** → the troubleshooting table in Section 9 mirrors what a real incident postmortem or change record looks like: symptom, cause, diagnostic evidence, fix.

This lab is the single most repeated *type* of work in a network engineer's career — not building networks, but keeping already-built ones working.

---

## 3. Topology Reference

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day%2011.2%20Lab%20-%20Troubleshooting%20Static%20Routes.png" width="900">
</p>

Same physical topology as Day 11.1: `PC1 — SW1 — R1 — R2 — R3 — SW2 — PC2`. The addressing plan is identical to Day 11.1's Section 4.3 — **do not change any IP addressing that is already correct**. This lab is strictly about finding and fixing faults, not redesigning.

---

## 4. IP Addressing Plan (Reference — Correct State)

This is what the topology *should* look like once every fault is fixed. Compare your `show` output against this table at every step.

| Device | Interface | Correct IP | Mask | Connects To |
|---|---|---|---|---|
| PC1 | NIC | 192.168.1.1 | 255.255.255.0 | SW1 |
| R1 | G0/0 | 192.168.1.254 | 255.255.255.0 | SW1 |
| R1 | G0/1 | 192.168.12.1 | 255.255.255.0 | R2 G0/1 |
| R2 | G0/1 | 192.168.12.2 | 255.255.255.0 | R1 G0/1 |
| R2 | G0/2 | 192.168.13.2 | 255.255.255.0 | R3 G0/1 |
| R3 | G0/1 | 192.168.13.3 | 255.255.255.0 | R2 G0/2 |
| R3 | G0/0 | 192.168.3.254 | 255.255.255.0 | SW2 |
| PC2 | NIC | 192.168.3.1 | 255.255.255.0 | SW2 |

**Correct static routes:**

```text
R1: ip route 192.168.3.0 255.255.255.0 192.168.12.2
    ip route 192.168.13.0 255.255.255.0 192.168.12.2
R2: ip route 192.168.1.0 255.255.255.0 192.168.12.1
    ip route 192.168.3.0 255.255.255.0 192.168.13.3
R3: ip route 192.168.1.0 255.255.255.0 192.168.13.2
    ip route 192.168.12.0 255.255.255.0 192.168.13.2
```

---

## 5. Pre-Configuration Checklist — Planting the Faults

Before starting the troubleshooting exercise, seed exactly **one fault per router** (or ask a lab partner / instructor to do it, so you diagnose blind). Suggested faults, one per device, mirroring the original lab's design:

1. **R1:** Change one static route to point at the wrong destination network (e.g., `ip route 192.168.30.0 255.255.255.0 192.168.12.2` instead of `192.168.3.0`).
2. **R2:** Delete one of R2's two static routes entirely (e.g., remove the route to `192.168.3.0/24`).
3. **R3:** Misconfigure the LAN-facing interface IP (e.g., `192.168.3.253` instead of `.254`), breaking PC2's gateway reachability.

Do not look at Section 9 until you've made a genuine diagnostic attempt.

---

## 6. Configuration Tasks — Diagnostic Walkthrough

### 6.1 Step 1 — Confirm the symptom

```text
PC1> ping 192.168.3.1
```

Expect failure (100% loss) or partial failure. This confirms *something* is wrong somewhere in the path — it does not yet tell you where.

### 6.2 Step 2 — Inspect R1

```text
R1#show ip interface brief
R1#show ip route
```

- **What mode:** Privileged EXEC — `show` commands never require Global Config.
- **What to look for:** every interface `up/up`; every expected `S` route present and pointing at the correct network/next-hop pair from Section 4.

If R1's route table shows a static route to a network that doesn't match Section 4 (e.g., `192.168.30.0` instead of `192.168.3.0`), that's the fault. Fix it:

```text
R1(config)#no ip route 192.168.30.0 255.255.255.0 192.168.12.2
R1(config)#ip route 192.168.3.0 255.255.255.0 192.168.12.2
```

> `no ip route ...` removes a specific static route — you must specify it exactly as it currently exists, IOS won't let you "edit" a route in place. Always remove the wrong one before adding the right one, or you can end up with both, which usually isn't harmful here but is sloppy and confusing in `show ip route` later.

### 6.3 Step 3 — Inspect R2

```text
R2#show ip interface brief
R2#show ip route
```

If R2 is missing one of its two expected `S` routes entirely, add the missing one:

```text
R2(config)#ip route 192.168.3.0 255.255.255.0 192.168.13.3
```

> This is the fault type unique to a *middle* router: because R2 needs routes in two directions, it's easy to configure one and forget the other — exactly the mistake flagged in Day 11.1's Common Mistakes list.

### 6.4 Step 4 — Inspect R3

```text
R3#show ip interface brief
R3#show ip route
```

If R3's LAN-facing interface IP doesn't match Section 4 (e.g., `.253` instead of `.254`), that's an addressing fault, not a routing fault — it will break PC2's default gateway reachability even if every route is perfect.

```text
R3(config)#interface gigabitEthernet 0/0
R3(config-if)#ip address 192.168.3.254 255.255.255.0
R3(config-if)#exit
```

> Notice this fault wouldn't show up in `show ip route` as an obviously wrong static route — it hides in the interface configuration. This is exactly why Step 6.4 checks `show ip interface brief` *before* `show ip route` on every router: an interface-layer fault can look like a routing-layer symptom.

### 6.5 Step 5 — Final validation

```text
PC1> ping 192.168.3.1
```

Expect full success (0% loss) once all three faults are corrected.

---

## 7. Verification Steps

| Command | What to check |
|---|---|
| `show ip interface brief` | Every interface `up/up`, IP matches Section 4 exactly |
| `show ip route` | Every expected `S` route present, correct network and next-hop |
| `ping` (PC1 ↔ PC2) | 0% loss after all fixes |

### 7.1 Expected Output Gallery

**`R2# show ip route` (after fix)**

```text
     192.168.1.0/24 [1/0] via 192.168.12.1
C    192.168.12.0/24 is directly connected, GigabitEthernet0/1
L    192.168.12.2/32 is directly connected, GigabitEthernet0/1
     192.168.3.0/24 [1/0] via 192.168.13.3
C    192.168.13.0/24 is directly connected, GigabitEthernet0/2
L    192.168.13.2/32 is directly connected, GigabitEthernet0/2
S    192.168.1.0/24 [1/0] via 192.168.12.1
S    192.168.3.0/24 [1/0] via 192.168.13.3
```

**`PC1> ping 192.168.3.1` (after all fixes)**

```text
Pinging 192.168.3.1 with 32 bytes of data:
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125
Reply from 192.168.3.1: bytes=32 time=1ms TTL=125

Ping statistics for 192.168.3.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

---

## 8. Common Mistakes (the 80/20)

1. **Fixing symptoms out of order** — jumping straight to R3 because "that's probably it" instead of checking R1 first. Work end-to-end, in path order, every time.
2. **Re-typing an entire device's config instead of the one broken line** — wastes time and risks introducing a *second* fault while "fixing" the first.
3. **Forgetting `no` before removing an incorrect static route** — you can't overwrite a static route by just typing a new one if the old one's destination network is different; both stay in the table unless the wrong one is explicitly removed.
4. **Not re-testing after each individual fix** — fixing all three faults blind, then testing once, makes it impossible to tell which fix actually mattered if the ping still fails (e.g., you mistyped the "fix").
5. **Assuming every fault is a routing fault** — this lab deliberately hides one fault at the interface layer to teach you to check `show ip interface brief` before assuming `show ip route` will show everything.

---

## 9. Troubleshooting Guide

| Step | Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|---|
| 1 | PC1 → PC2 ping fails entirely | Fault somewhere in the 3-router path | `ping` from PC1 | Proceed to router-by-router inspection |
| 2 | R1's route table shows an unexpected destination network | Static route configured with wrong destination | `show ip route` on R1 | `no ip route <wrong>`, then `ip route <correct>` |
| 3 | R2 reaches one LAN but not the other | Missing static route in one direction | `show ip route` on R2 | Add the missing `ip route` statement |
| 4 | PC2 can't reach its own gateway even though routing looks correct | R3's LAN-facing interface has the wrong IP | `show ip interface brief` on R3 | Correct the interface IP to match the addressing plan |
| 5 | Ping works one direction, fails the other | A route exists only on one side of the path | `show ip route` on both endpoints' routers | Add the missing route on whichever router lacks it |

---

## 10. Design Analysis

Why plant exactly one fault per router instead of a single fault somewhere random? Because it forces disciplined, complete coverage — you can't "get lucky" and find the one fault on the first router you check and stop early; you must actually inspect every device. This mirrors how real incident response works: you rarely know in advance which single device is at fault, so the process has to be systematic (start at one end, walk the path, verify each hop) rather than a lucky guess.

The choice to plant one *interface-layer* fault (R3) alongside two *routing-layer* faults (R1, R2) is deliberate — it's the most common real-world trap: engineers instinctively jump to `show ip route` because "it's a routing lab," and miss an addressing problem sitting one layer below.

---

## 11. Real-World Parallel

This is the daily reality of a NOC or on-call network engineer: a ticket says "site B can't reach site A," and nothing in the ticket tells you which of N devices in the path is actually broken. The methodology practiced here — confirm symptom, walk the path device by device, check interfaces before routes, fix the minimum necessary change, re-verify — is the same methodology used whether the network has 3 routers or 300.

---

## 12. Stretch Goal

1. Plant a **fourth** fault of your own design (e.g., a subnet mask mismatch, or a `shutdown` interface) on a random router without telling yourself which one, then diagnose blind.
2. Time yourself finding and fixing all three original faults — then repeat with three newly, randomly planted faults and see if your time improves.
3. Write a one-paragraph incident report for one of the faults you found, in the style of a real change/incident ticket: symptom, root cause, fix, verification.

---

## 13. Self-Assessment

- [ ] Can you name, in order, the 5 troubleshooting steps this lab practiced (verify → inspect R1 → inspect R2 → inspect R3 → re-verify)?
- [ ] Can you explain why an interface-layer fault might not show up in `show ip route`?
- [ ] Do you know the correct syntax to remove a specific wrong static route without touching any correct ones?
- [ ] Could you diagnose this same fault pattern (one fault per device, unknown type) on a topology you've never seen before?

---

## 14. Key Concepts Demonstrated

- Structured troubleshooting methodology (verify → isolate → fix → validate)
- Interface-layer vs. routing-layer fault differentiation
- Minimal, targeted corrective changes
- Route removal syntax (`no ip route`)

---

## 15. What I Learned

The hardest part of this lab isn't the CLI — it's resisting the urge to "just reconfigure the whole thing." Real networks are rarely in a state where a full rebuild is acceptable; the skill being built here is finding the smallest possible change that restores correct behavior, and proving it with a `show` command before moving on. Checking interfaces before assuming a routing problem also reinforced that "the network is down" symptoms don't tell you which OSI layer the fault lives at — you have to check.

---

## 16. Skills Practiced

- Systematic network troubleshooting methodology
- Static route inspection and correction
- Interface-layer fault diagnosis
- End-to-end connectivity re-validation

---

## 17. GNS3 Lab

Reuses the exact topology and build script from Day 11.1 — see [`GNS3/build_lab.py`](GNS3/build_lab.py) and [`GNS3/README.md`](GNS3/README.md). To practice troubleshooting in GNS3, seed the same three faults described in Section 5 using VyOS's `set`/`delete` configuration commands instead of IOS's `ip route`/`no ip route`.
