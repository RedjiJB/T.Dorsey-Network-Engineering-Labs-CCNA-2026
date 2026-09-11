# Day 42: SSH for Black Start (Field 1 - Offline Key Storage)

## 0. Metadata

- **Objective:** Master SSH with offline-stored keys and manual key deployment during recovery
- **Research Field:** Field 1: Black Start (Offline Resilience)
- **Proof Obligations:** SSH keys remain accessible during 6+ hour power loss; manual key deployment during recovery works within 5 minutes of restoration
- **Haiti Deployment Phase:** P38 (Power loss resilience)
- **Relevant RFC/Standards:** RFC 4251 (SSH Protocol), RFC 4252 (SSH Authentication)
- **Prerequisites:** Days 1-41 + Field 1 materials
- **Estimated Time:** 120 minutes
- **Difficulty:** Advanced
- **Hardware Required:** Router, SSH server, offline USB key storage, manual deployment procedures
- **Key Concepts:** Offline key storage, manual key deployment, recovery procedures, USB-based key recovery

## 1. Business Context

In Black Start scenarios, SSH access to network devices must survive power loss. Standard SSH implementations require live RADIUS/TACACS+ servers. This lab proves SSH keys can be cached offline and deployed manually during recovery, allowing administrators to regain control within minutes of power restoration.

## 2. Topology Diagram (Modified for Offline Key Storage)

```
Pre-Blackout State              Post-Blackout Recovery
[SSH Server]                    [SSH Server]
    |                           (NVRAM-cached keys active)
[Key CA/Distribution]                |
    |                           [USB Key Store]
[Router]                        (Contains offline backup)
    |                                |
[Admin Workstation]             [Admin (Manual Key Deploy)]
(Public Key Infrastructure)     (Restores access from USB)
```

## 3. IP Addressing Plan

| Device | IP Address | VLAN | Purpose | Notes |
|--------|-----------|------|---------|-------|
| SSH Server | 192.168.1.10 | Mgmt | SSH endpoint | UPS-backed during blackout |
| Router (G0/0) | 192.168.1.1 | Mgmt | Management interface | UPS-backed |
| Admin Workstation | 192.168.1.50 | Mgmt | SSH client | Powered down during blackout |

## 4. Field-Specific Configuration

### 4.1 SSH Server Pre-Blackout Setup

```cisco
SSHServer> ssh-keygen -t rsa -b 4096 -f /etc/ssh/ssh_host_rsa_key -N ""
SSHServer> ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ""

! Configure SSH to use pre-loaded authorized keys
SSHServer# cat /etc/ssh/sshd_config
PubkeyAuthentication yes
AuthorizedKeysFile /var/lib/ssh/authorized_keys.offline  ! Offline keys
PermitRootLogin no
PasswordAuthentication no  ! Keys only; no password fallback

! Test SSH connectivity before blackout
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.10
Welcome to SSH Server (Offline Mode)
! Connection successful; keys working
```

### 4.2 Backup SSH Keys to USB

```cisco
! On SSH Server
SSHServer# cp /etc/ssh/ssh_host_* /mnt/usb-backup/
SSHServer# cp /var/lib/ssh/authorized_keys.offline /mnt/usb-backup/
SSHServer# sha256sum /mnt/usb-backup/* > /mnt/usb-backup/CHECKSUM.txt
SSHServer# umount /mnt/usb-backup

! On Admin Workstation
Admin$ cp ~/.ssh/offline_admin_key* /mnt/usb-backup/
Admin$ cp ~/.ssh/known_hosts /mnt/usb-backup/
Admin$ sha256sum /mnt/usb-backup/* > /mnt/usb-backup/ADMIN_CHECKSUM.txt
Admin$ umount /mnt/usb-backup
```

### 4.3 SSH Configuration for Black Start Mode

```cisco
! Router SSH configuration (UPS-powered, survives blackout)
Router> enable
Router# configure terminal

! Generate RSA key for offline survival
Router(config)# crypto key generate rsa modulus 2048 exportable
! Key name: ssh-rsa-offline
! Modulus size: 2048

! SSH server configuration
Router(config)# ip ssh version 2
Router(config)# ip ssh authentication retries 2
Router(config)# ip ssh time-out 120

! Enable SSH on VTY lines
Router(config)# line vty 0 15
Router(config-line)# transport input ssh
Router(config-line)# exec-timeout 15 0
Router(config-line)# exit

! Create offline local user database (no RADIUS needed)
Router(config)# username admin privilege 15 password OfflineAdminPassword123!
! (In production, this would be a pre-shared encrypted password)

! Disable RADIUS authentication (not available during blackout)
Router(config)# no aaa new-model
! (This reverts to local authentication)

Router(config)# end
Router# write memory
```

## 5. Field-Specific Verification Steps

### 5.1 Verify SSH Keys Exist (Pre-Blackout)

```cisco
Router# show crypto key mypubkey rsa
% Key pair already exists
! RSA key exists and is ready

! List key details
Router# show crypto key mypubkey rsa
Key ID: ABC123DEF456...
Key size: 2048 bits
Key usage: SSH
Created: 2026-04-11 10:00:00
Exportable: Yes  ! Important: can be backed up to USB
```

### 5.2 Verify Offline USB Backup Integrity

```cisco
Admin$ cd /mnt/usb-backup
Admin$ sha256sum -c CHECKSUM.txt
ssh_host_rsa_key: OK
ssh_host_ed25519_key: OK
authorized_keys.offline: OK
! All key files match backup checksums
```

### 5.3 Simulate Power Loss and Verify SSH Access

```cisco
! Before power loss: Verify SSH works
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.10
Welcome to SSH Server
admin@SSH-Server:~$ whoami
admin
admin@SSH-Server:~$ exit

! Simulate power loss
Lab# simulate-power-loss duration 6hours

! After 6 hours (simulated)
Lab# power-restore

! SSH Server boots from UPS (still powered)
! Verify SSH is accessible
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.10
Connection established (from NVRAM cache)
Welcome to SSH Server
admin@SSH-Server:~$ uptime
up 6 hours, 2 minutes  ! Server never powered down
```

### 5.4 Verify Manual Key Deployment

```cisco
! Scenario: Admin workstation powered down during blackout
! After restoration: Admin uses USB key to restore SSH access to router

Admin$ ls /mnt/usb-backup/
offline_admin_key
offline_admin_key.pub
ssh_host_rsa_key
ssh_host_ed25519_key
authorized_keys.offline

! Copy USB keys back to ~/.ssh/
Admin$ cp /mnt/usb-backup/offline_admin_key* ~/.ssh/
Admin$ chmod 600 ~/.ssh/offline_admin_key

! Re-establish SSH connection using offline key
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.1
Welcome to Router (Post-Blackout)
admin@Router:~$ show users
Name     Channel IP Address         State    Idle     Time

admin    vty 0    192.168.1.50      S exec    00:00    00:00:30
! SSH session restored
```

## 6. Expected Output Gallery

```
=== PRE-BLACKOUT SSH ===
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.10
admin@SSH-Server:~$ uptime
up 2 days, 3 hours

=== OFFLINE USB KEYS ===
Admin$ ls -la /mnt/usb-backup/
-rw------- offline_admin_key
-rw-r--r-- offline_admin_key.pub
-rw------- ssh_host_rsa_key
-rw------- ssh_host_ed25519_key

=== POST-BLACKOUT SSH RECOVERY ===
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.1
admin@Router:~$ show clock
*14:45:20.123 UTC Sat Apr 11 2026
! Timestamp shows 6+ hour gap (during blackout)

admin@Router:~$ show startup-config | include crypto key
! Verify SSH key survived power cycle in NVRAM
```

## 7. Common Field-Specific Mistakes

### Mistake 1: Not Backing Up SSH Keys
**Problem:** SSH keys lost during power failure; cannot restore access
```
SSHServer# ls /etc/ssh/ssh_host_*
! No files (keys were deleted or corrupted during power loss)
! Admin cannot SSH back in
```
**Fix:** Back up keys to offline USB
```
SSHServer# cp /etc/ssh/ssh_host_* /mnt/usb-backup/
```

### Mistake 2: Using Password Authentication Fallback
**Problem:** After blackout, admin tries password authentication; router requires keys only
```
Admin$ ssh -u admin admin@192.168.1.1
Permission denied (publickey).
```
**Fix:** Use offline USB keys
```
Admin$ ssh -i /mnt/usb-backup/offline_admin_key admin@192.168.1.1
```

### Mistake 3: Enabling RADIUS During Black Start
**Problem:** RADIUS server is offline (power loss); SSH authentication fails
```cisco
Router(config)# aaa new-model
Router(config)# aaa authentication login default group radius local
! During blackout: RADIUS unreachable; local auth never attempted; SSH LOCKED
```
**Fix:** Disable RADIUS; use local authentication
```cisco
Router(config)# no aaa new-model
! Falls back to local username/password (which should also be pre-configured)
```

## 8. Troubleshooting by Field

### Symptom: SSH Key Files Corrupted After Power Loss

**Diagnostic:**
```cisco
Router# show crypto key mypubkey rsa
% Key file corrupted or not found
! Can't use SSH with damaged key
```

**Solution:**
```
! 1. Restore from USB backup
Admin$ scp /mnt/usb-backup/ssh_host_rsa_key root@192.168.1.1:/etc/ssh/

! 2. Verify permissions
Router# file permissions /etc/ssh/ssh_host_rsa_key
-rw------- (600)  ! Correct

! 3. Reload SSH service
Router# reload
! (Router reloads and reads ssh_host_rsa_key from disk)

! 4. Verify SSH works
Admin$ ssh -i ~/.ssh/offline_admin_key admin@192.168.1.1
Connection established
```

## 9. Design Analysis

### Why Offline SSH Keys for Black Start?

Standard SSH assumes RADIUS server is always available. Under power loss:
- **Availability:** RADIUS server powered down; authentication fails
- **Fallback:** Admin cannot SSH in to troubleshoot
- **Recovery time:** Must manually re-establish key distribution; 30+ minutes

Offline key storage:
- **Availability:** Keys backed up on USB; accessible anytime
- **Fallback:** Admin restores from USB; SSH works immediately
- **Recovery time:** <5 minutes of manual key deployment

## 10. Real-World Parallel

Haiti P38 pilot sites experience frequent power loss. Without offline SSH keys, network staff would:
1. Power loss occurs → SSH server offline → Admin can't connect
2. Wait for power restoration → Power back on → Still waiting for RADIUS startup
3. RADIUS finally available → SSH works; 15+ minutes of downtime

With offline keys:
1. Power loss occurs → SSH keys still accessible from USB → Staff can connect to UPS-powered routers
2. Power restoration → Immediate access; no waiting for RADIUS startup
3. Recovery time: 5 minutes (manual key deploy) vs. 15 minutes (RADIUS startup)

## 11. Stretch Goals

### 11.1 Implement Hardware Security Module (HSM) for Offline Key Storage

Store SSH keys in tamper-resistant USB HSM instead of plain USB drive.

### 11.2 Automate Key Recovery on Power Restoration

Use event manager to automatically restore keys from USB backup when power returns.

### 11.3 Create Key Rotation Policy for Offline Storage

Rotate offline keys every 30 days; maintain multiple USB backups across different sites.

### 11.4 Test With Haiti P38 Load

Deploy with 50 concurrent SSH sessions; verify all recover within 5 minutes post-blackout.

## 12. Self-Assessment (Field 1 Black Start - SSH - BSL)

- **BSL-1:** Generate SSH keys; backup to USB; verify SSH works pre-blackout
- **BSL-2:** Simulate 6-hour power loss; verify SSH keys accessible after restoration
- **BSL-3:** Test manual key deployment; restore SSH access from USB within 5 minutes
- **BSL-4:** Verify NVRAM-cached keys persist through power cycle; no RADIUS dependency
- **BSL-5:** Test with Haiti P38 load (50 concurrent SSH); all users restore within 5 minutes
- **BSL-6:** Create SSH offline resilience procedures document; train field operators
- **BSL-7:** Deploy to Haiti P38 pilot site; measure real-world SSH recovery time

---

**Lab Duration:** 120 minutes  
**Difficulty:** Advanced  
**Prerequisites:** CCNA Days 1-42 + Field 1 materials

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
