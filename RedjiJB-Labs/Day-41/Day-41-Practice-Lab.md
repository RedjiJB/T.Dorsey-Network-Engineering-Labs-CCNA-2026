# Day 41 Practice Lab — Syslog Configuration, Logging Destinations, and Remote Device Monitoring

Work through these prompts yourself before checking the full lab manual.

## Brief

You manage a router that needs full operational visibility: local troubleshooting from the console, remote troubleshooting over Telnet, a short-term in-memory history, and permanent centralized logging to a Syslog server.

## Topology

- R1 (router), PC2 (console workstation), PC1 (Telnet client), SRV1 (Syslog server)
- Single `/24` LAN

(Same topology image as the original Day 41 lab: `Lab-Photos/Day-41-Lab-Syslog.png`)

## Guided Questions

**Severity levels**
1. Without looking it up, list what you think the 8 Cisco Syslog severity levels might be, from most to least severe. Then check yourself.
2. If a destination is configured to log at the `warnings` level, which specific severity numbers actually get logged? Is it "warnings only" or something broader?

**Destinations**
3. You SSH into R1 and shut down an interface to test something. No log message appears in your terminal. Before assuming something is broken, what should you check first?
4. What's the one command that fixes the situation in question 3, and why isn't it persistent across sessions?
5. What's the practical difference between "buffered logging" and "logging host + logging trap"? When would you want one without the other?

**Timestamps**
6. Why does `service timestamps log datetime msec` matter more as your network grows past a single device?

**Remote logging**
7. You want SRV1 to receive absolutely everything, including debug-level detail. What two commands do you need, and what does each one individually control?
8. Now imagine a 200-device production network. Would `logging trap debugging` on every device be a good idea? What's the downside?

## Configuration Checklist (write the commands yourself)

- [ ] Generate a log message by toggling an interface
- [ ] Enable timestamps on log and debug messages
- [ ] Enable monitor logging for a remote Telnet session
- [ ] Configure an 8192-byte logging buffer
- [ ] Configure a remote Syslog host and set the trap level to forward everything
- [ ] Verify with `show logging` and `show running-config | include logging`

## Self-Check

- [ ] I can recite all 8 severity levels without checking the manual
- [ ] I correctly predicted that Telnet sessions don't see logs by default, and why
- [ ] I identified the risk of setting `logging trap debugging` in a large production network
- [ ] I distinguished buffered logging (local, volatile) from remote logging (centralized, persistent) in my own words
- [ ] I generated and captured at least one real log message myself
