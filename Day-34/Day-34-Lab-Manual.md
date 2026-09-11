# Day 34: IPv6 Access Control Lists

## 0. Metadata
- **Objective:** Configure and apply IPv6 ACLs for traffic filtering
- **Prerequisites:** Days 1-33, ACL knowledge
- **Time:** 90 minutes

## Key Concept
IPv6 ACLs similar to IPv4 but use IPv6 notation. Named ACLs preferred.

## Configuration Example
```
Router(config)# ipv6 access-list ALLOW-ICMP
Router(config-ipv6-acl)# permit icmp any any
Router(config-ipv6-acl)# exit
Router(config)# int g0/0
Router(config-if)# ipv6 traffic-filter ALLOW-ICMP in
```

## Verification
```
Router# show ipv6 access-list
```
