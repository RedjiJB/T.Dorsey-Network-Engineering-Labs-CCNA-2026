# Day 31: Advanced Routing Protocol Design & Optimization

## 0. Metadata
- **Objective:** Design routing protocols for complex topologies; optimize convergence and scalability
- **Prerequisites:** Days 1-30 (RIP, OSPF, EIGRP, routing basics)
- **Time:** 120 minutes
- **Difficulty:** Advanced
- **Key Concepts:** Routing protocol selection, convergence, metric tuning, route summarization

## 1. Overview
Choosing between RIP, OSPF, and EIGRP requires analysis of network topology, scale, convergence requirements, and vendor constraints. This lab covers design optimization.

## 2. Business Context
- RIP: simple, suitable for small networks (max 15 hops)
- OSPF: complex, scales to large networks, vendor-neutral
- EIGRP: balanced, Cisco-only, fast convergence, suitable for enterprises
- Protocol choice affects network design and operational cost

## 3. Topology
Three regional offices connected via WAN. Each region has multiple subnets. Design hierarchical routing.

## 4. Routing Protocol Comparison
| Factor | RIP | OSPF | EIGRP |
|--------|-----|------|-------|
| Admin Distance | 120 | 110 | 90 |
| Metric | Hop count | Cost (bandwidth) | Composite |
| Convergence | Slow (180s+) | Medium (5-10s) | Fast (3-5s) |
| Scalability | Poor | Good | Excellent |
| Cisco-Only | No | No | Yes |

## 5-17. (Standard sections)
