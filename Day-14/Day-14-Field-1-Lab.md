# Day 14: VLAN Troubleshooting & Advanced Trunking (Black Start Field)

## 0. Metadata
- **Objective:** Troubleshoot VLAN trunking issues in offline-resilient multi-switch topology
- **Research Field:** Field-1: Black Start
- **Proof Obligations:** Offline VLAN troubleshooting achievable without network connectivity; cached state sufficient for diagnosis; recovery from misconfigured trunks
- **Haiti Deployment Phase:** P38 (offline troubleshooting playbook)
- **Relevant RFC/Standards:** IEEE 802.1D, 802.1Q
- **Prerequisites:** Days 1-13 + Field-1 prerequisites
- **Estimated Time:** 150 minutes
- **Difficulty:** Advanced
- **Hardware Required:** 3 switches, 1 router, 4-6 PCs, cache storage
- **Key Concepts:** Offline trunk diagnostics, cached VLAN state, cold-start troubleshooting

## 1. Business Context (Field-1: Black Start)
Field-1 troubleshooting proves Haiti field operators can **diagnose VLAN issues without internet connectivity**. Scenario: P38 pilot site experiences trunk misconfiguration during offline period (power loss). Operator must restore service using only cached state and local tools.

**Success Metric:** Operator resolves 5 common trunk misconfigurations using only show commands and NVRAM configs, no SSH/remote access.

## 2. Topology Diagram (Offline Troubleshooting)
```
[SW1: Core - Cached State Only]
  /          |          \
[SW2]      [SW3]       [SW4]
 |            |          |
PC1          PC2         PC3
V10          V20         V30

**NO INTERNET CONNECTION**
All troubleshooting via console only
All configs cached in NVRAM
```

## 3. IP Addressing Plan (Static, Cached)
| Device | VLAN | IP Address | Cached | Notes |
|--------|------|-----------|---------|-------|
| PC1 | 10 | 10.0.10.10 | Yes | Static, no DHCP |
| PC2 | 20 | 10.0.20.10 | Yes | Static, no DHCP |
| SW1 | 1 | 10.0.0.1 | Yes | Mgmt (local) |

## 4. Field-1-Specific Configuration

### 4.1 Pre-Deployment: Create Intentional Misconfigurations
```
! This lab teaches troubleshooting, so create these errors intentionally:

! Error 1: Switch-2 trunk not allowed VLAN 20
Switch-2(config-if)# switchport trunk allowed vlan 1,10,30  ! Missing 20

! Error 2: Switch-3 native VLAN mismatch
Switch-3(config-if)# switchport trunk native vlan 20  ! Mismatch with Switch-1 native=1

! Error 3: Switch-4 access port in wrong VLAN
Switch-4(config-if)# switchport access vlan 20  ! Should be 30

! Save all configs to NVRAM
all-switches# write memory
```

### 4.2 Offline Troubleshooting Playbook
```
! Operator arrives at site (no power, no internet, console-only access)

! Step 1: Verify startup-config loaded
Switch# show startup-config | include vlan
! Expected: All VLANs present (cached in NVRAM)

! Step 2: Check current running-config for differences
Switch# show running-config | include switchport trunk allowed
! Compare to startup-config
! Look for: Missing VLANs in allowed list

! Step 3: Identify problematic trunk
Switch# show int status  | include notconnect
! Notconnect = potential trunk issue

! Step 4: Restore from cached config
! Copy startup to running (activate cached state):
Switch# copy startup-config running-config  ! NO, doesn't change behavior
! Better: Manually reload to get clean startup:
Switch# reload
! After reload, startup-config auto-loads (this is field-1 offline resilience)
```

## 5. Field-1-Specific Verification Steps

### 5.1 Identify Misconfiguration
```
! Before Fix:
PC1> ping 10.0.20.10  ← FAILS (VLAN 20 blocked by trunk filter)

! Diagnostic:
Switch-1# show int g0/1 switchport | include Allowed
! Shows: "Allowed Vlans: 1,10,30"  ← VLAN 20 missing!

! Verify with show vlan brief
Switch-1# show vlan brief
! VLAN 20 exists but PC2 not connected (trunk doesn't carry it)
```

### 5.2 Offline Fix (Field-1 Style)
```
! Fix: Modify trusted startup-config manually, then reload

! Edit running-config (this changes behavior until reload)
Switch-1(config)# int g0/2
Switch-1(config-if)# switchport trunk allowed vlan add 20
Switch-1(config-if)# exit
Switch-1(config)# exit

! Verify fix works
PC1> ping 10.0.20.10  ← Should work now

! Save to NVRAM (persistent for next offline period)
Switch-1# write memory

! Verify NVRAM change
Switch-1# show startup-config | include allowed vlan
! Should show "1,10,20,30" now
```

## 6. Expected Output Gallery (Offline Troubleshooting)

### 6.1 Trunk Misconfiguration Detected
```
Switch# show int g0/1 switchport
Switchport Mode: trunk
Allowed Vlans: 1,10,30
! ← VLAN 20 missing
```

### 6.2 After Fix Applied
```
Switch# show int g0/1 switchport
Switchport Mode: trunk
Allowed Vlans: 1,10,20,30
! ← VLAN 20 now included
```

## 7. Common Field-1-Specific Mistakes

### 7.1 MISTAKE: Forgetting to write memory
```
! Fix applied to running-config but lost on reload
! Field-1 Fix: ALWAYS write memory after changes
```

### 7.2 MISTAKE: Not Checking Startup-Config
```
! Assumes running-config matches startup (they diverged)
! Field-1 Fix: Compare both: show running-config vs. show startup-config
```

## 8. Troubleshooting by Field

### 8.1 VLAN Still Blocked After Trunk Fix
```
! Check access port configuration
Switch# show int f0/1 switchport | include Access VLAN
! If access VLAN != intended VLAN → Reconfigure

! Example: PC2 on port f0/1, should be VLAN 20
Switch(config-if)# switchport access vlan 20
```

## 9. Design Analysis (Why for Field-1)
Offline troubleshooting is **essential for Haiti P38** because power loss is frequent and internet unavailable. Field operators must diagnose issues with only console access and cached knowledge.

## 10. Real-World Parallel
**Haiti P38 Field Operator Playbook:** When network fails offline, follow cached troubleshooting tree (show int status → show trunk allowed → modify startup-config → reload → verify).

## 11. Stretch Goals
1. Create offline troubleshooting flowchart for field operators
2. Memorize 5 most common trunk misconfigurations
3. Practice 10 cold-start troubleshooting scenarios

## 12. Self-Assessment (Field-1 BSL)
- **BSL-1:** Identify 1 trunk misconfiguration using show commands
- **BSL-2:** Fix misconfiguration offline (no internet), verify cached state
- **BSL-3:** Troubleshoot all 5 common errors from memory
- **BSL-4:** Create field operator playbook
- **BSL-5:** Deploy to P38 pilot, train field operators, validate offline troubleshooting works
- **BSL-6:** Implement automated cold-start validation
- **BSL-7:** Lead P38 field operations, mentor remote troubleshooting

---

**End of Day-14 Field-1 Lab**
**Research Field:** Black Start | **Haiti Phase:** P38
**Generated for:** CCNA VLAN & STP Research Program
