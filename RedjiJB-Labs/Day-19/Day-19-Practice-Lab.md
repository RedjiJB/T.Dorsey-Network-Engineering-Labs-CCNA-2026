# Day 19 Practice Lab — VTP, Trunking, and VLAN Management (Self-Guided)

No-answers companion to `Day-19-Lab-Manual.md`.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2–2.5 hours. |
| **What you'll need** | Packet Tracer/GNS3 (or an IOSvL2/vIOS-L2 image — VTP requires real VTP support). |

---

## 1. The Brief

> Build a three-switch line topology (SW1–SW2–SW3). SW1 will be a VTP Server creating three VLANs. SW2 will be VTP Transparent and create one VLAN of its own. SW3 will be a VTP Client. All inter-switch links must be trunks with DTP disabled. You need to predict, before testing, exactly which VLANs will appear on which switches.

### Your task

- [ ] Before configuring anything, predict: after SW1 creates VLANs 10/20/30 and SW2 creates VLAN 40, which VLANs will `show vlan brief` display on each of the three switches? Write your prediction down now — you'll check it in Section 5.

---

## 2. Design Your Own Configuration Plan

1. Decide the VTP domain name (any name — just note it must match exactly on all three switches) and write out the mode assignment for each switch.
2. For each of the two inter-switch links, write the exact two-command sequence needed to make it a trunk that will never renegotiate to access mode regardless of what's plugged into the other end.
3. Decide which VLAN(s) each switch's local access ports will be assigned to, and note that SW3 (a Client) needs to have received a VLAN from the Server *before* it can assign a port to it — why?

---

## 3. Build and Cable

- [ ] Place SW1, SW2, SW3 in a line and cable the two inter-switch links.

---

## 4. Configure — Prompts Only

### 4.1 Trunk hardening (all switches)

- [ ] Force trunk mode and disable negotiation on every inter-switch link. What's the risk of leaving DTP enabled instead?

### 4.2 VTP configuration

- [ ] Set the domain name and mode on SW1 (Server), create three VLANs.
- [ ] Set the domain name and mode on SW2 (Transparent), create one VLAN locally.
- [ ] Set the domain name and mode on SW3 (Client), then attempt to create a VLAN. What happens, and why is that correct behavior rather than a bug?

### 4.3 Access ports

- [ ] Assign host-facing ports on each switch to appropriate VLANs. On SW3 specifically — can you assign a port to a VLAN you never created locally? Why or why not?

---

## 5. Verify — Compare Against Your Prediction

- [ ] Run `show vlan brief` on all three switches and compare against your Section 1 prediction. Where were you right? Where were you wrong, and why?
- [ ] Run `show vtp status` on all three and record the Configuration Revision number on each. Which one(s) actually change as you create VLANs, and which stay static?
- [ ] Verify trunk state and DTP negotiation status on every inter-switch link.

---

## 6. Explain Your Design

1. Why does SW2's VLAN 40 not appear on SW1 or SW3, even though SW2 is directly trunked between them?
2. Why does VTP information from SW1 still reach SW3, passing *through* SW2, even though SW2 is Transparent?
3. What's the actual security risk of an unprotected VTP Server, and what single configuration item mitigates it?
4. Why can SW3 (a Client) assign a port to VLAN 30, but not create VLAN 50 locally?
5. What's the practical difference between `switchport mode trunk` alone and adding `switchport nonegotiate`?

---

## 7. Troubleshoot Yourself

Break your lab in 3 of these ways and diagnose using only `show` commands:

- Set a domain name typo (different case or spelling) on one switch.
- Leave DTP enabled on one trunk link and set the far end to access mode.
- Attempt to create a VLAN on the Client switch.
- Simulate a "rogue switch" scenario by configuring SW3 as a Server with the same domain and a manually higher revision number (if your platform allows direct revision manipulation), then observe what happens to SW1's and SW2's VLAN databases.

---

## 8. Self-Check

- [ ] I predicted VLAN propagation behavior before testing, and understood every discrepancy from my prediction.
- [ ] I configured trunk hardening, VTP modes, and access ports from memory/lookup.
- [ ] I can state what each of the three VTP modes can and cannot do to its local VLAN database, without looking it up.
- [ ] I can explain the VTP revision-number security risk and its mitigation.
- [ ] I can explain all 5 design questions in Section 6 out loud.

Once done, open `Day-19-Lab-Manual.md` and diff your work against Sections 6, 7, and 9.
