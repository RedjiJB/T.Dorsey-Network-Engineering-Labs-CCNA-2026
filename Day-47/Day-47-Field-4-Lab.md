# Day 47: Advanced QoS for Security (Field 4 - DDoS Mitigation & Rate Limiting)

## 0. Metadata
- **Objective:** Master QoS with DDoS detection and automatic rate limiting of malicious traffic
- **Research Field:** Field 4: Security (DDoS Mitigation)
- **Proof Obligations:** Malicious traffic detected and rate-limited; legitimate traffic protected
- **Haiti Deployment Phase:** P45
- **Prerequisites:** Days 1-47 + Field 4 materials
- **Estimated Time:** 140 minutes

## 4. Configuration

```cisco
! DDoS-aware QoS
Router(config)# qos ddos-detection enable
Router(config)# qos anomaly-threshold 1000pps  ! Alert at 1000 packets/sec from single source

! Auto rate-limit when DDoS detected
Router(config)# policy-map DDOS-PROTECTION
Router(config-pmap)# class DDOS-TRAFFIC
Router(config-pmap-c)# police rate 100kbps  ! Limit DDoS to 100kbps
Router(config-pmap-c)# exit

! Example: DDoS from 192.168.1.50
Router# show qos ddos-events
2026-04-11T14:30:00Z DDoS ALERT from 192.168.1.50 (5000 pps)
Action: Rate-limited to 100 kbps
Protected Traffic: 98.5% throughput maintained
Legitimate Users: No impact
```

## 5-12. [DDoS detection techniques, rate limiting strategies, traffic classification under attack, legitimate traffic protection]

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
