# Day 36: Advanced ACL Configurations

## Metadata
- **Objective:** Configure extended and named ACLs for production networks
- **Prerequisites:** Days 1-34
- **Time:** 90 minutes

## Configuration
Extended ACLs filter by protocol, port, source/destination.

Named ACLs provide readability and easier modification.

## Key Commands
```
access-list 101 permit tcp any any eq 80
access-list 101 permit tcp any any eq 443
```
