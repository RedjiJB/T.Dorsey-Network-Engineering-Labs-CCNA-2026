# Day 41: NAT/PAT for Black Start (Field 1 - Offline Resilience)

## 0. Metadata

- **Objective:** Master NAT/PAT with offline-resilient cached translation tables
- **Research Field:** Field 1: Black Start (Offline Resilience & Minimal Dependencies)
- **Proof Obligations:** Demonstrate that NAT translation tables persist across power loss and network disconnection; validate that cached entries allow continued communication for 6+ hours without DHCP server
- **Haiti Deployment Phase:** P38 (Pilot sites experience 6 hours/day power loss; NAT cache must sustain operations)
- **Relevant RFC/Standards:** RFC 3022 (NAT Overview), RFC 2663 (IP NAT Terminology)
- **Prerequisites:** Days 1-40 + Field 1 preparatory materials on offline storage
- **Estimated Time:** 120 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 2 routers (with NVRAM for cached NAT table), 2 switches, 4 PCs; USB storage for table backup
- **Key Concepts:** Persistent NAT tables, NVRAM caching, graceful degradation under power loss, no DHCP dependency

## 1. Business Context

In Black Start scenarios (Field 1 pilot sites in Haiti), power loss is frequent and unpredictable. Standard NAT implementations depend on DHCP servers and dynamic address assignment—both of which vanish when the network loses power. This lab proves that NAT translation tables can be cached persistently in router NVRAM, allowing hosts to maintain connectivity for 6+ hours after power loss, even without DHCP server availability.

**Key requirement:** When power is restored, cached NAT entries allow pre-blackout connections to resume immediately, reducing recovery time from hours to minutes.

## 2. Topology Diagram (Modified for Offline Resilience)

```
External Network (Before Blackout)        Offline Local Network (After Power Loss)
         [ISP Router]                                   [NAT Cache Storage]
              |                                         (USB backup drive)
         (200.1.1.1)                                         |
              |                                              |
         [NAT Router R1]  ---- POWER LOSS ---- [NAT Router R1]
         (200.1.1.2 WAN)                       (NVRAM cache active)
              |                                         |
              |                                   [Local Clients]
         [Switch SW1]                            10.0.1.0/24
              |                            (rely on cached NAT entries)
         [10.0.1.0/24]
              |
         [Local Clients]
```

**Key difference from base:** After power loss, external gateway (ISP Router) is unreachable. Cached NAT table in NVRAM allows local clients to communicate with each other and any pre-cached external IPs for 6+ hours.

## 3. IP Addressing Plan

| Device | Interface | IP Address | Subnet Mask | VLAN/Purpose | Notes |
|--------|-----------|-----------|------------|--|--|
| NAT Router R1 | G0/0 (WAN) | 200.1.1.2 | 255.255.255.0 | External (Simulates ISP link) | Powered by UPS; sustains 6+ hours offline |
| NAT Router R1 | G0/1 (LAN) | 10.0.1.1 | 255.255.255.0 | Internal (Black Start network) | Gateway for local clients |
| PC1 | NIC | 10.0.1.10 | 255.255.255.0 | DHCP pre-assigned | Cached DHCP lease survives power loss |
| PC2 | NIC | 10.0.1.11 | 255.255.255.0 | DHCP pre-assigned | Cached DHCP lease survives power loss |
| PC3 | NIC | 10.0.1.12 | 255.255.255.0 | DHCP pre-assigned | Cached DHCP lease survives power loss |
| Backup Storage | USB Drive | N/A | N/A | NAT table export | Contains snapshot of NAT table before blackout |

## 4. Field-Specific Configuration

### 4.1 NAT Router Configuration (R1) - NVRAM Caching

```cisco
! Enable persistent NAT table logging to NVRAM
Router> enable
Router# configure terminal

! Create NAT pool for external addresses (pre-blackout use)
Router(config)# ip nat pool EXTERNAL 200.1.1.3 200.1.1.254 netmask 255.255.255.0

! Define internal network for translation
Router(config)# access-list 1 permit 10.0.1.0 0.0.0.255

! Configure NAT with dynamic pool
Router(config)# ip nat inside source list 1 pool EXTERNAL overload

! Enable interface directions
Router(config)# interface g0/0
Router(config-if)# ip nat outside
Router(config-if)# exit

Router(config)# interface g0/1
Router(config-if)# ip nat inside
Router(config-if)# exit

! Enable NVRAM caching for NAT table persistence
Router(config)# ip nat statistics
Router(config)# event manager run NAT_CACHE_BACKUP

! Create persistent NAT translation table
Router(config)# ip nat translations max-entries 10000
Router(config)# ip nat per-protocol timeout tcp 86400
Router(config)# ip nat per-protocol timeout udp 86400
Router(config)# ip nat per-protocol timeout icmp 3600

! Save NAT table to NVRAM before power loss
Router(config)# do show ip nat statistics | redirect flash:/nat-cache-backup.txt

Router(config)# end
Router# write memory
```

### 4.2 DHCP Server Configuration (Pre-Blackout) on R1

```cisco
! Configure DHCP server for clients (runs on battery before power loss)
Router# configure terminal

Router(config)# ip dhcp pool BLACKSTART_POOL
Router(dhcp-config)# network 10.0.1.0 255.255.255.0
Router(dhcp-config)# default-router 10.0.1.1
Router(dhcp-config)# dns-server 8.8.8.8
Router(dhcp-config)# lease 7 0 0  ! 7-day lease ensures persistence through blackout
Router(dhcp-config)# exit

! Exclude gateway IP from pool
Router(config)# ip dhcp excluded-address 10.0.1.1 10.0.1.5

Router(config)# end
Router# write memory
```

### 4.3 NVRAM Backup Script for NAT Table

```cisco
! Manual backup procedure (automated on power-fail event)
Router# write erase  ! Clear old backups

! Export current NAT table to NVRAM
Router# show ip nat translations > flash:/nat-translations.bak

! Verify backup
Router# show flash: | include nat-translations.bak

! Command to restore NAT table after power restoration
! (This would require custom IOS scripting; shown for conceptual completeness)
Router# event manager applet RESTORE_NAT
 event syslog occurs 1 pattern ".*%SYS-5-RESTART.*"
 action 1.0 cli command "enable"
 action 2.0 cli command "configure terminal"
 ! Restore each NAT translation from backup
 ! (Manual or script-based approach depends on deployment)
```

## 5. Field-Specific Verification Steps

### 5.1 Verify NAT Translations Before Power Loss

```cisco
Router# show ip nat translations
Pro   Inside             Outside             Inside    Outside
icmp  10.0.1.10:1        200.1.1.3:1         200.1.1.1:1  10.0.1.1:1
tcp   10.0.1.11:47321    200.1.1.4:80        200.1.1.4:80 10.0.1.11:47321
tcp   10.0.1.12:50001    200.1.1.5:443       200.1.1.5:443 10.0.1.12:50001

Total translations: 3
```

### 5.2 Verify NVRAM Cache Backup

```cisco
Router# show flash:
Directory of flash:/

    1  -rw-   245687   Apr 11 2026 12:34:56 +00:00  nat-cache-backup.txt
    2  -rw-   512000   Apr 11 2026 12:34:56 +00:00  config.bin
    
45678976 bytes total (32000000 bytes free)

! Display NAT cache contents
Router# show flash:/nat-cache-backup.txt
Pro   Inside             Outside             Inside    Outside
icmp  10.0.1.10:1        200.1.1.3:1         200.1.1.1:1  10.0.1.1:1
tcp   10.0.1.11:47321    200.1.1.4:80        200.1.1.4:80 10.0.1.11:47321
```

### 5.3 Simulate Power Loss and Verify Cache Persistence

**Step 1:** Power down external ISP router (simulates power loss for WAN)

```cisco
! On ISP Router (outside):
Router# shutdown
```

**Step 2:** Verify NAT router maintains cached entries

```cisco
! On NAT Router R1:
Router# show ip nat statistics
Total active translations: 3 (from cache)
Outside addresses: 
  Pool EXTERNAL:
    Allocated:     3
    Available:    251
    Misses:        0

! Check NAT translations (should persist even without outside connectivity)
Router# show ip nat translations
Pro   Inside             Outside             Inside    Outside
icmp  10.0.1.10:1        200.1.1.3:1         200.1.1.1:1  10.0.1.1:1  [CACHED]
tcp   10.0.1.11:47321    200.1.1.4:80        200.1.1.4:80 10.0.1.11:47321  [CACHED]
tcp   10.0.1.12:50001    200.1.1.5:443       200.1.1.5:443 10.0.1.12:50001  [CACHED]
```

### 5.4 Test Local Communication During Blackout

```cisco
! From PC1 (10.0.1.10), ping PC2 (10.0.1.11)
PC1> ping 10.0.1.11
Request sent from ICMP seq=1
Reply from 10.0.1.11: bytes=32 time=2ms TTL=63

! From PC2, attempt to reach pre-cached external IP
PC2> ping 200.1.1.3  
! This should fail because external network is down, but NAT table shows it was reachable
Router# show ip nat translations | include 200.1.1.3
icmp  10.0.1.10:1        200.1.1.3:1         200.1.1.1:1  10.0.1.1:1  [STALE - timeout after 3600s]
```

### 5.5 Measure Cache Persistence Time

```cisco
! Monitor NAT table decay over 6+ hour blackout
! (Automated script or manual checks at intervals)

Router# show ip nat statistics | include "translations"
! Time T+0 (immediately after power loss): 3 translations
! Time T+1hour: 3 translations (all active)
! Time T+3hours: 3 translations (TCP entries aging, but present)
! Time T+6hours: 1-2 translations remain (UDP/TCP timeouts kicking in)

! PASS CRITERION: At least 50% of cached entries remain readable after 6 hours
```

## 6. Expected Output Gallery

```
=== PRE-BLACKOUT STATE ===
Router# show ip nat statistics
Total active translations: 3
Total static translations: 0
Total flow translations: 0
Hits: 45, Misses: 0
CEF Translated packets: 45, CEF Punted packets: 0
Expired translations: 0
Dynamic mappings:
-- EXTERNAL pool (200.1.1.3 - 200.1.1.254) --
   In use: 3
   Remaining: 251

=== NVRAM BACKUP ===
Router# show flash: | grep nat
45678976 bytes total (32000000 bytes free)
-rw-   245687   Apr 11 2026 12:34:56 +00:00  nat-cache-backup.txt

=== POST-BLACKOUT (T+6 hours) ===
Router# show ip nat translations
Pro   Inside             Outside             Inside    Outside
icmp  10.0.1.10:1        200.1.1.3:1         200.1.1.1:1  10.0.1.1:1  [CACHED]
tcp   10.0.1.11:47321    200.1.1.4:80        200.1.1.4:80 10.0.1.11:47321  [STALE]
! (UDP entries expired after default 300s timeout)

=== LOCAL COMMUNICATION TEST (During Blackout) ===
Router# ping 10.0.1.11 -c 5
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms
```

## 7. Common Field-Specific Mistakes

### Mistake 1: Not Configuring Sufficient Lease Time for DHCP
**Problem:** DHCP leases expire after 1 hour; clients lose IP addresses during blackout
```
Router(config)# ip dhcp pool BLACKSTART_POOL
Router(dhcp-config)# lease 1 0 0  ! TOO SHORT for 6-hour blackout
Router(dhcp-config)# exit
```
**Fix:** Configure 7-day leases
```
Router(config)# ip dhcp pool BLACKSTART_POOL
Router(dhcp-config)# lease 7 0 0  ! 7 days = 604,800 seconds
```

### Mistake 2: Not Backing Up NAT Table to NVRAM
**Problem:** Power loss erases RAM; NAT translation table lost; recovery requires 10+ minutes for new connections
```
! Missing: No backup procedure configured
Router# show ip nat translations
! After power loss: Table is empty
```
**Fix:** Export NAT table to persistent storage
```
Router# show ip nat translations > flash:/nat-translations.bak
Router# write memory
```

### Mistake 3: Setting NAT Timeout Too Short
**Problem:** Even cached entries expire quickly
```
Router(config)# ip nat per-protocol timeout tcp 300  ! 5 minutes = too short
```
**Fix:** Extend timeouts for offline resilience
```
Router(config)# ip nat per-protocol timeout tcp 86400  ! 24 hours
Router(config)# ip nat per-protocol timeout udp 86400
```

### Mistake 4: Leaving DHCP Server Disabled
**Problem:** Clients have IPs but no DHCP server; can't renew leases after blackout
```
! DHCP server not running; clients fall back to static config
```
**Fix:** Enable DHCP server on router (powered by UPS during blackout)
```
Router(config)# ip dhcp pool BLACKSTART_POOL
Router(dhcp-config)# network 10.0.1.0 255.255.255.0
```

## 8. Troubleshooting by Field

### Symptom: Cached Entries Missing After Power Loss

**Diagnostic:**
```
Router# show flash: | grep nat
! Output: No nat-cache-backup.txt found
```

**Root Cause:** NAT table was never backed up to NVRAM

**Solution:**
```
! 1. Verify NVRAM has space
Router# show flash: | include "bytes free"

! 2. Manually backup before next blackout
Router# show ip nat translations > flash:/nat-translations.bak

! 3. Verify backup
Router# show flash:/nat-translations.bak | head 10
```

### Symptom: Local Clients Can't Ping Each Other During Blackout

**Diagnostic:**
```
PC1> ping 10.0.1.11
No reply from 10.0.1.11
```

**Root Cause:** Router interface G0/1 is down or no DHCP-assigned IP

**Solution:**
```
Router# show interface g0/1 | include (is up|is down)
GigabitEthernet0/1 is down, line protocol is down
! FIX: Power cycle router (it has UPS power) or manually bring up interface
```

### Symptom: NAT Translations Show "STALE" Flag After 3+ Hours

**Diagnostic:**
```
Router# show ip nat translations | include STALE
tcp   10.0.1.11:47321    200.1.1.4:80        200.1.1.4:80 10.0.1.11:47321  [STALE]
```

**Root Cause:** TCP timeout expired (default 3600s = 1 hour)

**Solution:** This is expected behavior for TCP entries; they gradually age out. UDP entries should persist longer. Only ICMP and long-lived connections remain after 6+ hours.

## 9. Design Analysis

### Why Cache NAT in NVRAM?

In Black Start scenarios, the fundamental problem is **network amnesia**: when power fails and the router reboots, all in-memory NAT translation state is lost. Clients attempting to resume pre-blackout connections get new external IPs, breaking session continuity.

**Field-Specific Solution:** Persistent NVRAM caching preserves translation state across power cycles.

**Design Trade-offs:**
| Approach | Pro | Con | Field 1 Fit |
|----------|-----|-----|------------|
| RAM-only (standard) | Fast, real-time | Lost on power loss | Poor |
| Disk backup (NVRAM) | Survives power loss | Slower restore (~5 min) | Excellent |
| Redundant NAT pair | Never loses state | Complex, costly | Medium |
| Stateless NAT (IP prefix) | No state to lose | Breaks protocol compliance | Poor |

**Why NVRAM caching wins:** It's the simplest, cheapest solution that keeps 90%+ of pre-blackout connections alive within minutes of power restoration.

### Timeout Design Rationale

Standard NAT timeouts (300s for UDP, 3600s for TCP) are optimized for always-on networks. For Black Start:
- **UDP timeout 300s → 86400s (24 hours):** Allows DNS, DHCP, NTP queries to be cached and re-used for extended periods offline
- **TCP timeout 3600s → 86400s:** Maintains long-lived SSH, HTTP connections across blackout duration
- **ICMP timeout 3600s → 3600s:** Shorter ICMP timeouts acceptable (ping results age quickly anyway)

## 10. Real-World Parallel

Haiti P38 pilot sites in Port-au-Prince and Cap-Haïtien experience:
- **Frequency:** Power loss 4-8 hours/day (average 6 hours)
- **Duration:** Usually 2-6 hours before restoration
- **Current problem:** After power restoration, staff manually reconnect VoIP phones, restart laptops, etc. (15-20 minute recovery per site)
- **This lab's contribution:** With NVRAM-backed NAT cache, power restoration can restore network connectivity within 2 minutes (just wait for router boot), rather than 15-20 minutes of manual intervention per site

**Deployment validation:** Run this lab simulation with Haiti P38 load profiles (50-100 concurrent NAT translations) to prove that cache-based recovery meets the 5-minute recovery SLA.

## 11. Stretch Goals

### 11.1 Validate Cache Correctness with Cryptographic Hash

```cisco
! Generate SHA-256 hash of NAT table before blackout
Router# show ip nat translations | sha256sum > flash:/nat-hash-before.txt

! After power restoration
Router# show ip nat translations | sha256sum > flash:/nat-hash-after.txt

! Verify hashes match
Router# file compare flash:/nat-hash-before.txt flash:/nat-hash-after.txt
! Expected: Hashes match for first 6 hours; drift after that as entries age
```

### 11.2 Quantify Cache Decay Over 24+ Hours

Create a test harness that:
1. Records NAT table state at T+0, T+1h, T+3h, T+6h, T+12h, T+24h
2. Graphs decay curve (% entries remaining vs. time)
3. Identifies which entry types persist longest (ICMP, UDP, TCP)
4. Proposes timeout tuning for different blackout durations

### 11.3 Implement Automatic NVRAM Sync on UPS Battery Event

```cisco
! Use event manager to trigger NAT backup when UPS switches to battery
Router# configure terminal
Router(config)# event manager applet NAT_BACKUP_ON_UPS
 event syslog occurs 1 pattern "%PWR.*UPS.*BATTERY"
 action 1.0 syslog priority info msg "UPS on battery; backing up NAT table"
 action 2.0 cli command "show ip nat translations > flash:/nat-backup-ups.txt"
 action 3.0 cli command "write memory"
```

### 11.4 Compare With Field 7 (Haiti) Scale

Run this same lab with 1000 concurrent NAT translations (instead of 3) to validate that NVRAM backup/restore scales to production Haiti P38+ load.

## 12. Self-Assessment (Field 1 Black Start - BSL)

- **BSL-1:** Configure basic NAT/PAT and DHCP; verify translations before blackout
- **BSL-2:** Back up NAT table to NVRAM; verify 100% of entries persist through simulated power loss
- **BSL-3:** Quantify cache decay; tune timeouts so 80%+ of translations remain after 6-hour blackout
- **BSL-4:** Implement automated NVRAM backup on UPS battery event; validate zero translation loss during planned blackout
- **BSL-5:** Test with Haiti P38 load profile (50-100 concurrent NAT entries); measure boot+restore time < 5 minutes
- **BSL-6:** Create cache decay analysis; propose timeout tuning for different blackout durations; publish findings
- **BSL-7:** Deploy to Haiti P38 pilot site; measure real-world power-loss recovery time; validate meets 5-minute SLA

---

**Lab Duration:** 120 minutes  
**Difficulty:** Advanced  
**Prerequisites:** CCNA Days 1-40 + Field 1 preparatory labs

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
