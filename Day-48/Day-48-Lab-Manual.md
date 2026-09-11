# Day 48: Device Management - SNMP, Logging, CDP

## 0. Metadata
- **Objective:** Configure SNMP for monitoring, syslog for logging, CDP for discovery
- **Prerequisites:** Days 1-40
- **Time:** 120 minutes

## SNMP Configuration
```
Router(config)# snmp-server community CCNA ro
Router(config)# snmp-server trap link-status
Router(config)# snmp-server host 192.168.1.100 CCNA
```

## Syslog Configuration
```
Router(config)# logging 192.168.1.50
Router(config)# logging trap informational
```

## Verification
```
Router# show snmp
Router# show logging
Router# show cdp neighbors
```
