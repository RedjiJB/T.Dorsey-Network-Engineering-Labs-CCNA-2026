# Day 40 Practice Lab — SNMP Fundamentals, MIB Queries, and Remote Device Management

Work through these prompts yourself before checking the full lab manual.

## Brief

You're setting up SNMP-based monitoring for a single router so an operations team can poll it for status without logging into the CLI. You need both a monitoring-only integration and a separate, more privileged path for a config-management tool that needs to push one value remotely.

## Topology

- R1 (router) = SNMP agent
- PC1 (workstation) = SNMP manager
- Single `/24` LAN between them

(Same topology image as the original Day 40 lab: `Lab-Photos/Day-40-Lab-SNMP.png`)

## Guided Questions

**Concepts**
1. In your own words, what's the difference between the SNMP "manager" and the SNMP "agent"? Which one initiates a Get request?
2. What is a MIB, and what is an OID? How do they relate to each other?
3. List the five SNMP operation types and, for each, one sentence on what it does.

**Access control**
4. Why does it make sense to have two separate community strings instead of one? What's the security risk of only having one?
5. If you configure only an RO community, what happens when someone tries an SNMP Set? Predict the failure mode before testing it.

**OID reasoning**
6. Without looking it up, guess what these OIDs probably represent, based on naming convention alone, then verify: `1.3.6.1.2.1.1.5.0`, `1.3.6.1.2.1.1.3.0`, `1.3.6.1.2.1.2.1.0`.
7. `ifNumber` returns a count and `ifDescr` returns a list of names. How would you confirm the two results are consistent with each other?

**Get vs Set**
8. You want to remotely rename the router's hostname. Which community do you need, and what SNMP operation do you perform? What data type would you expect `sysName` to require?
9. After a successful Set, what two independent ways could you confirm the change actually took effect (one from the manager's side, one from the device's own CLI)?

## Configuration Checklist (write the commands yourself)

- [ ] Configure a read-only SNMP community
- [ ] Configure a read/write SNMP community (different string)
- [ ] Verify both via `show running-config`
- [ ] Perform a Get for hostname, uptime, and interface count/names
- [ ] Perform a Set to change the hostname
- [ ] Verify the change from both the manager and the device CLI

## Security Reasoning

10. SNMPv1/v2c community strings travel in cleartext. What does that mean for someone who can see traffic on the same LAN segment? What does SNMPv3 add that fixes this, specifically (name the three capability categories)?

## Self-Check

- [ ] I could explain manager vs. agent without referring back to this doc
- [ ] I predicted the Set-against-RO failure before testing it
- [ ] I correctly guessed at least 2 of the 3 OID meanings before verifying
- [ ] I identified two independent ways to verify the hostname Set worked
- [ ] I can name SNMPv3's three security improvements over v2c
