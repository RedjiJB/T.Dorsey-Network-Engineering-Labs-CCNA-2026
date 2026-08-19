Day 49 Complete — Port Security

**Status:** ✅ Complete  
**Lab:** Jeremy's IT Lab — Day 49  
**Topic:** Port Security  
**Exam Relevance:** CCNA 200-301

---

## Objective

Configure and verify **Port Security** on SW1 and SW2 using different security policies.

### SW1 — F0/1, F0/2, F0/3

- Violation mode: **Shutdown**
- Maximum secure MAC addresses: **1**
- Sticky learning: **Disabled**
- Aging time: **1 hour**

### SW2 — G0/1

- Violation mode: **Restrict**
- Maximum secure MAC addresses: **4**
- Sticky learning: **Enabled**

After configuration, trigger port-security violations and observe how each switch responds.

---

## Topology

```text
                    10.0.0.0/24

PC1 (.1) ---- F0/1
                   \
PC2 (.2) ---- F0/2 ---- SW1 ---- G0/1 ---- SW2 ---- G0/2 ---- R1
                   /
PC3 (.3) ---- F0/3
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-49-Lab-Port-Security.png" width="900">
</p>

---

## Skills Practiced

- Configuring switch port security
- Configuring maximum secure MAC addresses
- Configuring port-security violation modes
- Configuring secure MAC aging
- Using sticky MAC learning
- Verifying port-security status
- Viewing dynamically learned secure MAC addresses
- Comparing `shutdown` and `restrict` violation modes
- Understanding secure-up and secure-shutdown states
- Troubleshooting Layer 2 access security

---

# Part 1 — Configure Port Security on SW1

The first requirement was to configure port security on:

```text
F0/1
F0/2
F0/3
```

Each interface was limited to **one secure MAC address**.

The violation mode was configured as **shutdown**, sticky learning was disabled, and the secure MAC aging timer was set to **60 minutes**.

### SW1 Configuration

```cisco
enable
configure terminal

interface range f0/1 - 3
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation shutdown
 switchport port-security aging time 60
end
```

The important commands are:

```cisco
switchport port-security
switchport port-security maximum 1
switchport port-security violation shutdown
switchport port-security aging time 60
```

Because sticky learning was supposed to remain disabled, the following command was **not** configured on SW1:

```cisco
switchport port-security mac-address sticky
```

---

## Verify SW1 Port Security

I verified each secured interface using:

```cisco
show port-security interface f0/1
show port-security interface f0/2
show port-security interface f0/3
```

The output confirmed:

```text
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 60 mins
Aging Type                 : Absolute
Maximum MAC Addresses      : 1
Sticky MAC Addresses       : 0
Security Violation Count   : 0
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-49-Lab-Port-Security-1.1.png" width="900">
</p>

F0/1 successfully showed:

```text
Port Security: Enabled
Port Status: Secure-up
Violation Mode: Shutdown
Maximum MAC Addresses: 1
Aging Time: 60 mins
```

---

## Verify F0/2

The same configuration was verified on F0/2.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-49-Lab-Port-Security-1.2.png" width="900">
</p>

F0/2 showed:

```text
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 60 mins
Maximum MAC Addresses      : 1
Sticky MAC Addresses       : 0
```

---

## Verify F0/3

F0/3 was also checked individually.

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-49-Lab-Port-Security-1.3.png" width="900">
</p>

The interface confirmed the same security policy:

```text
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 60 mins
Maximum MAC Addresses      : 1
Sticky MAC Addresses       : 0
```

All three SW1 access ports were now protected.

---

# Part 2 — Configure Port Security on SW2

SW2 required a different port-security policy.

The secured interface was:

```text
G0/1
```

Requirements:

```text
Violation Mode: Restrict
Maximum Addresses: 4
Sticky Learning: Enabled
```

### SW2 Configuration

```cisco
enable
configure terminal

interface g0/1
 switchport port-security
 switchport port-security maximum 4
 switchport port-security violation restrict
 switchport port-security mac-address sticky
end
```

---

## Sticky MAC Learning

Unlike SW1, SW2 was configured to dynamically learn secure MAC addresses using:

```cisco
switchport port-security mac-address sticky
```

Sticky learning allows the switch to dynamically learn source MAC addresses and add them to the running configuration as secure MAC addresses.

After traffic crossed G0/1, the running configuration showed a learned sticky MAC address.

```text
switchport port-security
switchport port-security maximum 4
switchport port-security mac-address sticky
switchport port-security violation restrict
switchport port-security mac-address sticky 0060.471C.1D19
```

<p align="center">
  <img src="https://github.com/TushanDorsey/Network-Engineering-Labs-CCNA-2026/blob/main/Lab-Photos/Day-49-Lab-Port-Security-1.4.png" width="900">
</p>

This confirmed that sticky learning was functioning correctly.

---

# Part 3 — Understanding the Maximum MAC Address Limit

SW1 was configured with:

```cisco
switchport port-security maximum 1
```

That means each access port can learn or accept only **one secure MAC address**.

The intended design is:

```text
SW1 F0/1 → PC1
SW1 F0/2 → PC2
SW1 F0/3 → PC3
```

Each interface should normally see only the MAC address belonging to its connected PC.

If another device introduces another source MAC address after the limit has been reached, a port-security violation occurs.

---

## SW2 Maximum MAC Addresses

SW2 G0/1 was configured with:

```cisco
switchport port-security maximum 4
```

This allows SW2 to learn multiple secure MAC addresses through the link toward SW1.

Conceptually:

```text
PC1 MAC ----\
PC2 MAC ----- SW1 ---- SW2 G0/1
PC3 MAC ----/
```

Multiple source MAC addresses can arrive through G0/1, so its maximum secure MAC limit needs to be higher than the individual PC access ports.

---

# Part 4 — Shutdown Violation Mode

SW1 uses:

```cisco
switchport port-security violation shutdown
```

Shutdown is the default and most aggressive port-security violation mode.

When an unauthorized MAC address causes a violation:

```text
Unauthorized MAC detected
          |
          v
Port-Security Violation
          |
          v
Interface enters secure-shutdown
          |
          v
Traffic stops
```

This protects the network by disabling the affected interface.

The interface must then be recovered before normal communication can continue.

---

# Part 5 — Restrict Violation Mode

SW2 uses:

```cisco
switchport port-security violation restrict
```

Restrict mode behaves differently.

When an unauthorized source MAC causes a violation:

```text
Unauthorized MAC detected
          |
          v
Port-Security Violation
          |
          +----> Unauthorized frame dropped
          |
          +----> Violation counter increases
          |
          +----> Port remains operational
```

Authorized traffic can continue using the interface.

---

## Port Security Violation Modes

| Mode | Unauthorized Traffic | Port Status | Violation Counter |
|---|---|---|---|
| Protect | Dropped | Remains Up | No |
| Restrict | Dropped | Remains Up | Yes |
| Shutdown | Dropped | Shuts Down | Yes |

For this lab:

```text
SW1 → Shutdown
SW2 → Restrict
```

This allowed me to compare two different responses to a security violation.

---

# Part 6 — Secure MAC Aging

SW1 was configured with:

```cisco
switchport port-security aging time 60
```

The value is configured in minutes.

Therefore:

```text
60 minutes = 1 hour
```

The verification output showed:

```text
Aging Time : 60 mins
Aging Type : Absolute
```

Secure MAC aging prevents dynamically learned secure MAC addresses from remaining indefinitely.

---

# Part 7 — Trigger Port Security Violations

The final part of the lab was to trigger violations by introducing another device or MAC address.

For example:

```text
PC1
 |
F0/1
 |
SW1
```

If F0/1 already has its maximum allowed secure MAC address and another device is connected, the switch detects a new source MAC.

Because SW1 uses:

```text
Maximum Addresses: 1
Violation Mode: Shutdown
```

the violation can cause the port to shut down.

---

## SW1 Violation Behavior

```text
Known MAC
   |
   v
Allowed

Unknown additional MAC
   |
   v
Maximum MAC limit exceeded
   |
   v
Port Security Violation
   |
   v
SHUTDOWN
```

The interface stops forwarding traffic.

---

## SW2 Violation Behavior

SW2 behaves differently because it uses:

```text
Violation Mode: Restrict
```

When the secure MAC limit is exceeded:

```text
Unknown MAC
   |
   v
Maximum MAC limit exceeded
   |
   v
Port Security Violation
   |
   +----> Frame dropped
   |
   +----> Violation recorded
   |
   +----> Interface remains up
```

This was the major behavioral difference demonstrated in the lab.

---

# Verification Commands

### View Port Security Summary

```cisco
show port-security
```

### Verify F0/1

```cisco
show port-security interface f0/1
```

### Verify F0/2

```cisco
show port-security interface f0/2
```

### Verify F0/3

```cisco
show port-security interface f0/3
```

### Verify SW2 G0/1

```cisco
show port-security interface g0/1
```

### View Secure MAC Addresses

```cisco
show port-security address
```

### View MAC Address Table

```cisco
show mac address-table
```

### Check Running Configuration

```cisco
show running-config
```

---

# Important Commands

### Enable Port Security

```cisco
switchport port-security
```

### Maximum Secure MAC Addresses

```cisco
switchport port-security maximum 1
```

### Shutdown Violation Mode

```cisco
switchport port-security violation shutdown
```

### Restrict Violation Mode

```cisco
switchport port-security violation restrict
```

### Enable Sticky Learning

```cisco
switchport port-security mac-address sticky
```

### Configure Aging

```cisco
switchport port-security aging time 60
```

---

# Lessons Learned

## 1. Port Security Limits Which Devices Can Use an Interface

Port security allows a switch to control access based on source MAC addresses.

This can prevent unauthorized devices from simply connecting to an available switch port.

---

## 2. Maximum MAC Addresses Matter

The command:

```cisco
switchport port-security maximum
```

controls how many secure MAC addresses are permitted on an interface.

In this lab:

```text
SW1 F0/1 = 1
SW1 F0/2 = 1
SW1 F0/3 = 1
SW2 G0/1 = 4
```

---

## 3. Shutdown and Restrict Behave Differently

Shutdown mode provides stronger enforcement because a violation disables the interface.

Restrict mode drops unauthorized traffic while allowing legitimate traffic to continue.

```text
Shutdown → Port goes down
Restrict → Port stays up
```

---

## 4. Sticky Learning Simplifies Secure MAC Configuration

Instead of manually configuring each MAC address, sticky learning allows the switch to dynamically learn secure addresses.

```cisco
switchport port-security mac-address sticky
```

The learned MAC can then appear directly in the running configuration.

---

## 5. Port Security Is a Layer 2 Security Feature

Port security operates primarily by examining source MAC addresses.

It provides an additional layer of protection at the switch access layer and helps prevent unauthorized devices from gaining network connectivity.

---

# Final Verification

The completed lab successfully demonstrated:

- ✅ Port security enabled on SW1 F0/1
- ✅ Port security enabled on SW1 F0/2
- ✅ Port security enabled on SW1 F0/3
- ✅ Maximum of 1 secure MAC configured on SW1 ports
- ✅ Shutdown violation mode configured
- ✅ Sticky learning disabled on SW1
- ✅ 60-minute aging configured
- ✅ Port security enabled on SW2 G0/1
- ✅ Maximum of 4 secure MAC addresses configured
- ✅ Restrict violation mode configured
- ✅ Sticky MAC learning enabled
- ✅ Sticky MAC address successfully learned
- ✅ Port-security settings verified
- ✅ Shutdown and restrict behavior compared

---

## Next Steps

Continue into the next CCNA security topic and build on Layer 2 switch security concepts, including additional protections used to secure the access layer.

---

# Day 49 Complete ✅

**Port Security — Shutdown vs Restrict, Secure MAC Limits, Sticky Learning & Aging**
