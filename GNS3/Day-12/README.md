# GNS3 Day 12: Spanning Tree Protocol - Base & Field Variants

## Base Topology

**3-Switch Triangle:**
- SW01 (Building A - Root) ↔ SW02 (Building B): Gi0/1 trunk
- SW01 (Building A) ↔ SW03 (Building C): Gi0/2 trunk
- SW02 (Building B) ↔ SW03 (Building C): Gi0/1 trunk (one link blocked by STP)

**Configuration:**
```
spanning-tree mode pvst
spanning-tree vlan 10,20,30,99 priority 4096 (SW01)
spanning-tree vlan 10,20,30,99 priority 8192 (SW02)
spanning-tree vlan 10,20,30,99 priority 16384 (SW03)
```

## Field Variants

**Field-1:** Rapid STP (802.1w) - Convergence < 1 second
**Field-2:** Per-VLAN load balancing (different root per VLAN instance)
**Field-3:** PortFast + BPDU guard on all access ports
**Field-4:** Root bridge priority manipulation (intentional failover)
**Field-5:** Cost optimization and path selection
**Field-6:** STP with EtherChannel (Day 15 preview)
**Field-7:** MSTP regions (Day 14 preview)

---

**Last Updated:** August 30, 2026

