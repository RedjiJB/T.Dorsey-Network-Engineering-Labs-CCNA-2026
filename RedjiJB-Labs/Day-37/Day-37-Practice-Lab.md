# Day 37 Practice Lab — NTP: Network Time Synchronization

Use this as a self-test companion to the [Day 37 Lab Manual](Day-37-Lab-Manual.md). Work through the prompts before checking the manual for the full command walkthrough.

---

## Scenario

Three routers (R1, R2, R3) are already routing traffic to each other and to the internet (OSPF + a default route on R1, all preconfigured). None of them have correct or synchronized time. You need to: set clocks manually, apply the correct timezone, sync R1 to a real external time source, then make R1 the trusted internal time source for R2 and R3 — with authentication — and make sure time survives a reboot.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-37-Lab-NTP.png" alt="Day 37 Topology" width="900">
</p>

| Link | Network | R1 IP | R2 IP | R3 IP |
|---|---|---|---|---|
| R1—R2 | 192.168.12.0/30 | 192.168.12.1 | 192.168.12.2 | — |
| R1—R3 | 192.168.13.0/30 | 192.168.13.1 | — | 192.168.13.2 |
| R2—R3 | 192.168.23.0/30 | — | 192.168.23.1 | 192.168.23.2 |
| R1—Internet | 203.0.113.0/30 | 203.0.113.1 | — | — |

---

## Phase 1 — Software clock

1. What CLI mode must you be in to run `clock set`? What happens if you try it from configuration mode without a workaround?
2. What's the exact syntax pattern for `clock set` (time format, month format)? Set all three routers to noon on December 30, 2020.
3. Before any timezone is configured, what timezone does `show clock` display by default?

---

## Phase 2 — Timezone

4. What's the syntax for `clock timezone`? Configure all three routers for Eastern Standard Time.
5. Is EST's offset from UTC positive or negative? What would happen to the displayed time if you got the sign backwards?
6. Cisco IOS doesn't handle one particular seasonal time change automatically. What is it, and what additional command would you need?

---

## Phase 3 — NTP client

7. Write the command to make R1 sync to external NTP server 1.1.1.1.
8. If 1.1.1.1 is stratum 1, what stratum will R1 become once it successfully syncs to it? What's the general rule this follows?
9. In `show ntp associations` output, what does the `reach` field's value of `377` actually mean, and what number system is it in?
10. What does the `~` prefix in front of an address mean in this output?

---

## Phase 4 — NTP master + authenticated clients

11. R1 has no further upstream — how do you configure it to become a time source for R2 and R3 anyway? What stratum would you assign it, and why not stratum 1?
12. Write the two commands (in order) required to set up NTP authentication with key ID 1 and password `CCNA`. What does each one individually accomplish, and what happens if you only run one of them?
13. Write the commands for R2 and R3 to sync to R1, using authentication key 1. Which specific IP address does each router need to use, and why does it matter that it's the interface IP on their direct link to R1 rather than any other IP belonging to R1?
14. After R2 syncs to R1 (which itself is now `ntp master 8`), what stratum would you expect R2 to report? Why?
15. What real-IOS command (unavailable in this lab's simulated environment) would let you explicitly pin the source IP used for outgoing NTP packets, and in what kind of topology would omitting it actually cause a problem?

---

## Phase 5 — Hardware calendar

16. What's the difference between the "software clock" and the "hardware calendar" on a router?
17. What command bridges NTP's synced time into the hardware calendar, and what happens after a reboot if you forget it?

---

## Verification Practice

18. Without checking the manual, list every field in a `show ntp associations` row and what each one means.
19. What line in `show clock` output specifically confirms a device's time came from NTP rather than a manual `clock set`?
20. How would you distinguish, from `show ntp associations` output alone, between "not yet synced" and "actively synced and healthy"?

---

## Design Reasoning

21. Why does this lab have R1 sync externally and then become the internal master, rather than having all three routers independently sync to 1.1.1.1?
22. Why authenticate the internal R1↔R2/R3 relationship specifically, even though the R1↔1.1.1.1 relationship isn't authenticated the same way?
23. A colleague suggests configuring both `ntp master 8` and `ntp server 1.1.1.1` on R1 permanently, "just in case." What's the risk with combining these two roles without a clear understanding of the interaction?

---

## Self-Check

- [ ] I can state the stratum rule (upstream + 1) and apply it to any device in this topology given its immediate upstream's stratum
- [ ] I can list both NTP authentication commands and know what breaks if either is skipped
- [ ] I can explain the software clock vs. hardware calendar distinction without notes
- [ ] I can read a `show ntp associations` table and identify stratum, reachability, and offset for a given peer
- [ ] I can explain in my own words why time synchronization matters for logging and certificate validation
