# Challenge Labs Expansion Plan

## Scope

**New Files to Create:**
- 58 Challenge Labs (base, one per day)
- 261 Challenge Labs (field-specific variants)
- 58 GNS3 Build Instructions (base)
- 261 GNS3 Build Instructions (field-specific)
- 58 Automated Setup Scripts (base, reusable)
- 261 Setup Script variants (field-specific)

**Total New Files: ~896 files**

---

## Challenge Lab Format (No Hints)

### Structure
```
## Day-NN Challenge Lab: [Topic]

### Scenario
[Business problem statement - NO guidance on how to solve]

### Success Criteria
[What success looks like - testable outcomes only]
- [ ] Criterion 1 (verify with show command, not told which)
- [ ] Criterion 2 
- [ ] Criterion 3

### Time Limit
60-90 minutes

### Constraints
[Any limitations: "Use only OSPF, no static routes" or "Cannot reboot routers"]

### Hints (Hidden)
If truly stuck after 30 minutes, reveal one hint at a time
[But hints kept separate, not shown by default]
```

### Key Difference from Practice Lab
- **Practice Lab (Parts 1-3):** "Configure these steps: 1) Create VLAN, 2) Assign ports, 3) Test ping"
- **Challenge Lab:** "Users can't reach Finance servers. Make it work."

---

## GNS3 Build Instructions Format

### Structure
```
## Day-NN: [Topic] - GNS3 Build Instructions

### Required Devices
- 3x Cisco 2960 switches
- 1x Cisco 2911 router
- 4x VPCs
- 2x Links (switches), 1x Link (router connection)

### Device Configuration
Drag devices:
1. Click Device icon
2. Place on canvas at [x, y coordinates]
3. Name: [SW1, SW2, R1, PC1, PC2, PC3, PC4]

### Link Configuration
1. Drag link from SW1 g0/1 to SW2 g0/1
2. [Full step-by-step with coordinates and port assignments]

### Starting IOS Images
- Cisco 2960: [path/to/image]
- Cisco 2911: [path/to/image]
- VPCs: default

### Pre-load Configuration (Optional)
Copy this to startup-config of each device before starting
[Device-specific startup commands]

### Expected State
When topology starts, verify:
- All devices boot successfully
- No link errors
- Devices accessible via console
```

---

## Automated Setup Script Format

### Structure (Bash/Python)

```bash
#!/bin/bash
# Day-NN Setup Script: [Topic]
# Automated GNS3 topology deployment

PROJECT_NAME="CCNA-Day-NN-${FIELD}"
DEVICES=(SW1:2960 SW2:2960 R1:2911 PC1:vpc PC2:vpc PC3:vpc PC4:vpc)
LINKS=(
  "SW1:g0/1:SW2:g0/1:auto:auto"
  "SW1:g0/2:R1:g0/0:auto:auto"
  "SW2:f0/1:PC1:e0"
  "SW2:f0/2:PC2:e0"
)

# 1. Create GNS3 project
gns3-create-project "$PROJECT_NAME"

# 2. Deploy devices
for DEVICE in "${DEVICES[@]}"; do
  NAME="${DEVICE%%:*}"
  TYPE="${DEVICE##*:}"
  gns3-add-device "$NAME" "$TYPE"
done

# 3. Create links
for LINK in "${LINKS[@]}"; do
  gns3-create-link "$LINK"
done

# 4. Load startup configs (optional)
gns3-config-device SW1 < configs/SW1-startup.cfg
gns3-config-device SW2 < configs/SW2-startup.cfg
gns3-config-device R1 < configs/R1-startup.cfg

# 5. Start topology
gns3-start-project "$PROJECT_NAME"

echo "Day-NN topology deployed: $PROJECT_NAME"
```

---

## Phased Implementation

### Phase 1: Templates (This Sprint)
- Challenge Lab template
- GNS3 Build Instruction template  
- Setup Script template
- **Files: 3**

### Phase 2: Base Challenge Labs (Days 01-12)
- 12 Challenge Labs (no field variants)
- 12 GNS3 build instructions
- 6 reusable setup scripts (one per 2 days)
- **Files: 30**
- **Batches: 2 (6 labs each)**

### Phase 3: Base Challenge Labs (Days 13-30)
- 18 Challenge Labs
- 18 GNS3 build instructions
- 9 setup scripts
- **Files: 45**
- **Batches: 2 (9 labs each)**

### Phase 4: Base Challenge Labs (Days 31-58)
- 28 Challenge Labs
- 28 GNS3 build instructions
- 14 setup scripts
- **Files: 70**
- **Batches: 3 (9 labs each)**

### Phase 5: Field-Specific Challenge Labs (Fields 1, 3, 4 GNS3-Ready)
- Field 1: 56 challenge labs + 56 GNS3 docs + 28 scripts = 140 files
- Field 3: 40 challenge labs + 40 GNS3 docs + 20 scripts = 100 files
- Field 4: 46 challenge labs + 46 GNS3 docs + 23 scripts = 115 files
- **Files: 355**
- **Batches: 12 (30 labs each, sequential)**

### Phase 6: Field-Specific Challenge Labs (Fields 2, 5, 6, 7 Infrastructure Backlog)
- Marked as infrastructure backlog (same as field labs)
- **Files: 440**
- **Status: Added to INFRASTRUCTURE-BACKLOG.md, not generated yet**

---

## Total Scope by Phase

| Phase | Type | Files | Status |
|-------|------|-------|--------|
| 1 | Templates | 3 | ⏳ To do |
| 2 | Days 01-12 Challenge | 30 | ⏳ To do |
| 3 | Days 13-30 Challenge | 45 | ⏳ To do |
| 4 | Days 31-58 Challenge | 70 | ⏳ To do |
| 5 | Fields 1,3,4 Challenge | 355 | ⏳ To do |
| 6 | Fields 2,5,6,7 Challenge | 440 | 🔴 Backlog |
| | **TOTAL** | **943** | |

---

## Execution Timeline

**Phase 1 (Today):** Create templates (1-2 hours)
**Phases 2-4 (Week 1):** Base challenge labs + GNS3 docs (50 files, 2-3 days)
**Phase 5 (Week 2-3):** Field challenge labs for GNS3-ready fields (355 files, 1 week)
**Phase 6:** Add to backlog with Field 2/5/6/7 infrastructure requirements

---

## Files Per Day (Example: Day-15)

After all phases complete, Day-15 will have:

**Currently:**
- Day-15-Lab-Manual.md (comprehensive CCNA guide)
- Day-15-Practice-Lab.md (guided exercises with answers)
- Day-15-Field-1-Lab.md (Black Start variant)
- Day-15-Field-3-Lab.md (DePIN variant)
- Day-15-Field-4-Lab.md (Security variant)
- Day-15-Field-7-Lab.md (Haiti variant)
- Day-15-Research-Paper.md (Section 2.6 linkage)

**After Challenge Expansion:**
- Day-15-Challenge-Lab.md (NEW: no guidance, scenario only)
- Day-15-GNS3-Build.md (NEW: detailed topology instructions)
- Day-15-setup.sh (NEW: automated topology deployment)
- Day-15-Field-1-Challenge-Lab.md (NEW)
- Day-15-Field-1-GNS3-Build.md (NEW)
- Day-15-Field-1-setup.sh (NEW)
- Day-15-Field-3-Challenge-Lab.md (NEW)
- Day-15-Field-3-GNS3-Build.md (NEW)
- Day-15-Field-3-setup.sh (NEW)
- Day-15-Field-4-Challenge-Lab.md (NEW)
- Day-15-Field-4-GNS3-Build.md (NEW)
- Day-15-Field-4-setup.sh (NEW)
- Day-15-Field-7-Challenge-Lab.md (NEW)
- Day-15-Field-7-GNS3-Build.md (NEW)
- Day-15-Field-7-setup.sh (NEW)

**Day-15 Total: 21 files** (7 current + 14 new)

---

## Ready to Proceed?

Recommend starting with:
1. Create 3 templates (Challenge Lab, GNS3 Build, Setup Script)
2. Launch Phase 2 batch agents for Days 01-12
3. Then proceed through Phases 3-5 sequentially
4. Add Phase 6 to INFRASTRUCTURE-BACKLOG.md

**Proceed? (Y/N)**
