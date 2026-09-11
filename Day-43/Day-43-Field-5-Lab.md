# Day 43: AAA for Healthcare AI (Field 5 - Clinical vs Research Access Separation)

## 0. Metadata
- **Objective:** Master AAA with separation of clinical staff vs research staff permissions
- **Research Field:** Field 5: Healthcare AI (Access Control, Data Sensitivity)
- **Proof Obligations:** Clinical staff can only access patient records; research staff only access de-identified data
- **Haiti Deployment Phase:** P45
- **Prerequisites:** Days 1-43 + Field 5 healthcare materials
- **Estimated Time:** 135 minutes

## 1. Business Context

Healthcare AAA separates clinical and research access paths. A researcher cannot accidentally query raw patient data; a clinician has no access to research algorithms.

## 4. Field-Specific Configuration

```cisco
! Clinical staff role (can access patient records)
Router(config)# privilege level 10
Router(config)# privilege exec level 10 show patient-database
Router(config)# privilege exec level 10 exec 0x0A:CLINICAL_ACCESS

! Research staff role (can access de-identified data only)
Router(config)# privilege level 11
Router(config)# privilege exec level 11 show research-database
Router(config)# privilege exec level 11 exec 0x0B:RESEARCH_ACCESS
Router(config)# privilege deny level 11 show patient-database

! RADIUS authentication with role separation
Router(config)# aaa authentication login default group radius local
! (Each user's RADIUS record includes role: clinical or research)
```

## 5-12. [Clinical vs research access separation, audit logging of data access by role, HIPAA compliance verification]

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
