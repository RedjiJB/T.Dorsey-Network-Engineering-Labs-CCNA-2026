# Day 43 Practice Lab — FTP & TFTP: Cisco IOS File Transfer & Upgrade

Work through these prompts yourself before checking the full lab manual.

## Brief

You need to upgrade the IOS on two routers. One will fetch its new image via TFTP, the other via FTP, from a server two hops (well, one hop and one point-to-point link) away.

## Topology

```text
SRV1 -- SW1 -- R1 --(/30 link)-- R2
```
Server LAN is a `/24`; the R1–R2 link is a point-to-point subnet.

(Same topology image as the original Day 43 lab: `Lab-Photos/Day-43-Lab-FTP-TFTP.png`)

## Guided Questions

**Addressing**
1. The R1–R2 link only needs 2 usable host addresses. What's the smallest correctly-sized mask, and what are the 4 addresses in that block (network, host, host, broadcast)?
2. Why would a `/24` be considered poor practice for a link like this, beyond "it wastes addresses"?

**Prerequisites for file transfer**
3. R2 needs to reach SRV1's subnet, but has no directly connected path there. What do you need to configure, and what verification command proves it worked before you even attempt TFTP or FTP?
4. Why does the lab manual insist on testing plain ICMP connectivity before troubleshooting a failed file transfer? What would a routing failure and a TFTP failure look like if you didn't check connectivity first?

**TFTP vs FTP**
5. Fill in this comparison table yourself, then check your answers: transport protocol, port(s), authentication (yes/no) for each of TFTP and FTP.
6. R1 uses TFTP with no extra configuration beyond the transfer command itself. R2 needs two extra lines before it can use FTP. What are they, and why does TFTP not need an equivalent?

**Upgrade workflow**
7. Put these steps in the correct order: reload, verify new IOS is running, transfer image, delete old image, save config, configure boot system, verify image landed in flash. Why does this order matter — what specifically breaks if you delete the old image too early?
8. What command tells the router which image to boot from, and what happens if you forget to save configuration before reloading?

## Configuration Checklist (write the commands yourself)

- [ ] Address both routers' interfaces
- [ ] Configure the static route R2 needs to reach the server subnet
- [ ] Verify connectivity with ping before any transfer
- [ ] TFTP the IOS image onto R1, verify it landed in flash
- [ ] Configure FTP credentials on R2, then FTP the image onto R2
- [ ] Configure `boot system` on both, save, reload, verify `show version`
- [ ] Only then delete the old images

## Self-Check

- [ ] I calculated the /30 addresses correctly before checking the manual
- [ ] I explained why ping-testing first matters, in my own words
- [ ] I correctly filled in the TFTP vs FTP comparison table before checking
- [ ] I put the 7-step upgrade workflow in the correct order without help
- [ ] I can explain specifically what could go wrong if you delete the old image too early
