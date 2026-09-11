# Day 17: VLAN Troubleshooting & Multi-Switch Verification

## 0. Metadata
- **Objective:** Master VLAN troubleshooting in complex topologies; verify spanning tree interaction with VLANs
- **Prerequisites:** Days 1-16 (VLAN knowledge, STP basics)
- **Time:** 120 minutes
- **Difficulty:** Advanced
- **Key Concepts:** VLAN troubleshooting flowchart, PVST+, asymmetric routing

## 1. Overview
Large networks with multiple switches, multiple VLANs, and redundant links require systematic troubleshooting. Spanning tree interacts differently with each VLAN (PVST+).

## 2. Business Context
- PVST+ (Per-VLAN Spanning Tree) runs separate STP instance per VLAN
- Load balancing: different VLANs can have different root bridges
- Topology changes affect different VLANs independently
- Troubleshooting must account for VLAN-specific STP state

## 3. Topology
Multiple switches (3+), multiple VLANs (10, 20, 30), redundant links, ROAS router.

## 4. Configuration
(Same as Day-15/16, but add PVST+ verification commands)

## 5-17. (Standard sections)
