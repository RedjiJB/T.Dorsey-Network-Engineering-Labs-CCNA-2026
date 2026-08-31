# Day 25 Practice Lab — EIGRP Multi-Autonomous System, Auto-Summary, and Unequal-Cost Load Balancing

Self-derivation companion to the Day 25 Lab Manual. No addressing plan and no CLI commands — derive them yourself first.

---

## Brief

Four routers (R1 hub, R2/R3 transit, R4 LAN edge) need EIGRP AS 100 running across a partial mesh. R1 has two physically different paths to R4's LAN. You need EIGRP configured classlessly, with correct passive-interface design, and then tuned so R1 actually uses both paths to the LAN instead of just the best one.

## Topology

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-25-Lab-EIGRP-Configuration.png" alt="Day 25 EIGRP Lab" width="900">
</p>

```text
              R1 (hub)
             /        \
           R2          R3
             \        /
              R4 (LAN edge) -- SW1 -- PC1
```

---

## Part 1 — Derive the Addressing

1. Four router-to-router links exist (R1-R2, R1-R3, R2-R4, R3-R4). Each is point-to-point. Derive the prefix length by hand using `2^h − 2 ≥ hosts`.
2. R4's LAN needs room for growth. What prefix would you choose and why is a /30 wrong for it?
3. Each router has a loopback interface. What mask goes on a loopback address, and why is it different in kind (not just size) from every other mask in this lab?
4. Pick four non-overlapping /30 networks for the transit links, using whatever addressing scheme you like, and show the block-size math proving they don't overlap.

---

## Part 2 — EIGRP Fundamentals Reasoning

1. EIGRP's `network` command, used without a wildcard mask, matches addresses classfully. What does `network 10.0.0.0` actually match — does it care what mask is configured on the interface itself?
2. R4's LAN is 192.168.4.0/24 — not in the 10.0.0.0/8 range. Will `network 10.0.0.0` cause that LAN to be advertised? What do you need to add?
3. What does `auto-summary` do by default, and what specific real-world topology shape (hint: think about two separate sites each owning a slice of the same classful /8) does it break if left enabled?
4. Which interfaces in this topology should be passive, and for each one, explain in one sentence *why* — don't just say "loopback," explain the underlying reasoning so it would generalize to a topology you've never seen.

---

## Part 3 — Predict Before Verifying

Before running anything, answer:

1. On R1, how many EIGRP neighbors do you expect, and on which interfaces?
2. On R1, how many paths to 192.168.4.0/24 do you expect to see in `show ip route`, assuming both transit paths (via R2 and via R3) have identical bandwidth/delay? What would `show ip route` need to show for you to call these "equal-cost"?

---

## Part 4 — Unequal-Cost Load Balancing (derive before checking the manual)

1. What is EIGRP's *default* variance value, and what does that default mean in terms of which paths get installed in the routing table?
2. If you want R1 to also use a second path to 192.168.4.0/24 whose metric is up to double the best path's metric, what `variance` value do you configure?
3. Suppose the best path's metric is 2,681,856 and the second path's metric is exactly double that. Predict the `traffic share count` values IOS will show for each path in `show ip route 192.168.4.0`, and explain the proportion of traffic each path will carry.
4. Why can't `variance` ever cause a routing loop, no matter how high you set it? (Hint: think about what condition a feasible successor must satisfy, independent of variance.)
5. If you set `variance` very high (say, 10) but the second path's actual metric is still, say, 20x the best path's metric, will it get installed? Why or why not?

---

## Part 5 — Troubleshooting Scenarios

For each, state your first diagnostic command and reasoning:

1. R1 and R2 never form an EIGRP neighbor relationship even though both interfaces show up/up.
2. `show ip route` on a remote router only shows a classful summary (e.g., `10.0.0.0/8`) instead of the actual /30 and /24 subnets.
3. You configured `variance 2` but `show ip route 192.168.4.0` on R1 still shows only one path.
4. R4's EIGRP process appears to have formed a neighbor relationship over its LAN interface, which you didn't expect.

---

## Self-Check Checklist

- [ ] I derived all four transit /30s and the loopback /32 reasoning without checking the manual first
- [ ] I correctly explained what `network 10.0.0.0` does and does not match
- [ ] I identified which interfaces need to be passive and why, in my own words
- [ ] I correctly predicted the traffic-share-count ratio for a 2x metric difference under `variance 2`
- [ ] I can explain why variance is loop-safe without looking it up
- [ ] I worked through all four troubleshooting scenarios before reading the manual's troubleshooting table
