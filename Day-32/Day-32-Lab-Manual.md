# Day 32: IPv6 Addressing - EUI-64, Link-Local, and Static Routes

## 0. Metadata
- **Objective:** Configure IPv6 addressing using EUI-64, link-local, and manual assignment; establish IPv6 routes
- **Relevant Standards:** RFC 4291 (IPv6 spec), RFC 4862 (IPv6 autoconfiguration)
- **Prerequisites:** Days 1-25 (IPv4 routing foundation)
- **Time:** 120 minutes
- **Difficulty:** Intermediate

## 1. Overview
IPv6 is the successor to IPv4, offering 128-bit addresses and simplified header format. This lab covers three addressing modes: auto-configured link-local, EUI-64 global unicast, and static assignment.

## 2. Business Context
- IPv4 addresses exhausted in 2011 (IANA)
- IoT deployments require IPv6 (2^128 address space)
- Dual-stack (IPv4+IPv6) is production standard
- Enterprise IPv6 adoption: 30-40% as of 2025

## 3. Topology Reference
```
    [R1: fe80::1/10]
        |
    [R2: fe80::2/10]
```

## 4. IPv6 Addressing Plan
| Device | Interface | IPv6 Address | Prefix Length | Type |
|--------|-----------|-------------|---|------|
| R1 | G0/0 | 2001:db8:1::1 | /64 | Static |
| R2 | G0/0 | 2001:db8:1::2 | /64 | Static |
| R1 | Lo0 | 2001:db8:1::1 | /128 | Loopback |

## 5. Pre-Config Checklist
- [ ] IPv6 routing enabled on routers
- [ ] Link-local addresses auto-generated (FE80::/10)
- [ ] Physical links operational

## 6. Configuration

### 6.1 Enable IPv6 Routing
```
Router# conf t
Router(config)# ipv6 unicast-routing
```

### 6.2 Configure Global Unicast Address (Static)
```
Router(config)# int g0/0
Router(config-if)# ipv6 address 2001:db8:1::1/64
Router(config-if)# no shutdown
Router(config-if)# exit
```

### 6.3 Verify Link-Local (Auto)
```
Router# show int g0/0 | include fe80
  inet6 address is fe80::1%2 (LLA)
```

## 7. Verification
```
Router# show ipv6 int g0/0
Global unicast address(es):
  2001:db8:1::1, subnet is 2001:db8:1::/64
Local Link Address(es):
  fe80::1%2

Router# ping 2001:db8:1::2 (ping IPv6 neighbor)
```

## 8. Common Mistakes
1. **Forgetting ipv6 unicast-routing** — Global enable needed on router
2. **Using IPv4 notation for IPv6** — IPv6 requires colon-separated hex, not dotted decimal
3. **Link-local only** — Can't route between subnets without global unicast addresses
4. **Wrong encapsulation** — IPv6 is native, no tunneling needed in modern networks

## 9. Troubleshooting Guide
### 9.1 No IPv6 Adjacency
```
Router# show ipv6 route
(should show connected routes for each interface)
Router# ping 2001:db8:1::2 (test reachability)
```

### 9.2 "Cannot parse address"
```
! Verify IPv6 syntax:
! Correct: 2001:db8:1::1/64
! Wrong: 2001.db8.1.1/64 (IPv4 notation)
```

## 10. Design Analysis
IPv6 simplifies subnet design: /64 is standard per-subnet (not VLSM like IPv4). Organizations use /48 for enterprises, subdividing into /64 per location.

## 11. Real-World Parallel
Google dual-stack deployment uses IPv6 for both internal and external traffic. IPv6 percentage varies by region (10-40%) but growing annually.

## 12. Stretch Goals
1. Configure EUI-64 address auto-derivation
2. Set up static IPv6 route to remote network
3. Implement IPv6 ACL for traffic filtering
4. Test dual-stack (IPv4+IPv6 on same interface)

## 13. Self-Assessment (BSL Scale)
- **BSL-1:** Configure static IPv6; verify with ping
- **BSL-2:** Configure two interfaces; explain link-local vs. global
- **BSL-3:** Describe EUI-64 conversion process
- **BSL-4:** Design /48 network with 20 /64 subnets
- **BSL-5:** Troubleshoot routing asymmetry
- **BSL-6:** Justify IPv6 implementation strategy
- **BSL-7:** Design enterprise IPv6 migration plan

## 14. Key Concepts
- **IPv6 Address:** 128 bits; written as eight hex groups (2001:db8:1::1)
- **Link-Local (fe80::/10):** Auto-generated; one-link scope
- **Global Unicast (2000::/3):** Routable globally; ISP-provided
- **EUI-64:** MAC address → interface ID conversion
- **Prefix /64:** Standard subnet size (simplifies VLSM)

## 15. What I Learned
IPv6 simplifies addressing with fixed /64 subnets. Link-local auto-configuration enables plug-and-play networking.

## 16. Skills Practiced
- ✓ Enable IPv6 unicast routing
- ✓ Configure static IPv6 addresses
- ✓ Verify link-local auto-generation
- ✓ Test IPv6 connectivity
- ✓ Read IPv6 routing tables
- ✓ Troubleshoot IPv6 issues

## 17. GNS3 Lab Info
**Setup:** 2x 2911 Routers connected via G0/0
**Time:** 45 minutes
**Focus:** Static IPv6 configuration and ping connectivity
