# Day 33: IPv6 Routing - OSPFv3 Basics

## 0. Metadata
- **Objective:** Configure OSPFv3 (OSPF for IPv6) and establish dynamic routing
- **Prerequisites:** Days 1-32 (IPv4 OSPF knowledge, IPv6 addressing)
- **Time:** 120 minutes
- **Difficulty:** Intermediate-Advanced

## 1. Overview
OSPFv3 extends OSPF to IPv6. Configuration is similar to OSPFv2 but uses IPv6 addresses and slightly different syntax.

## 2-17. (Reference Day-24 OSPF manual, apply to IPv6)

## Key Configuration
```
Router(config)# ipv6 router ospf 1
Router(config-rtr)# router-id 1.1.1.1
Router(config-rtr)# exit
Router(config)# int g0/0
Router(config-if)# ipv6 ospf 1 area 0
Router(config-if)# no shutdown
```

## Verification
```
Router# show ipv6 ospf neighbor
Router# show ipv6 route ospf
```
