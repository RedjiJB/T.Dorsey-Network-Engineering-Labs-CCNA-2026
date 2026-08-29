# Day 58 Practice Lab — Wireless LANs & WLC Configuration (Self-Guided)

This is the **no-answers companion** to [`Day-58-Lab-Manual.md`](Day-58-Lab-Manual.md). It gives you the same business requirements and topology, but withholds the addressing plan and exact GUI steps — you work them out yourself. Use the full manual only to check your work after you've attempted each part, not before.

---

## 0. Before You Start

| Field | Value |
|---|---|
| **Time budget** | 2 hours. |
| **What you'll need** | Packet Tracer (this lab needs its WLC/AP simulation — GNS3 cannot simulate real wireless, see the GNS3 README) and a blank sheet for your addressing plan. |
| **Grading yourself** | Compare each section against the full manual's corresponding section only after attempting it. |

---

## 1. The Brief

> Your company needs wireless coverage across an office floor served by a Cisco Wireless LAN Controller and two lightweight access points. You need two logically separate wireless networks: one for trusted employee devices, one for visiting guests. Guest devices must not be able to reach anything on the employee network. The controller itself needs its own separate management network, reachable independent of whether any wireless client traffic is even flowing.
>
> Design the wireless architecture and the VLAN/subnet plan that supports it.

### Your task

- [ ] Name the architecture being described here (centralized controller + lightweight APs) and contrast it in one paragraph with the alternative (standalone/autonomous APs each configured independently). Which one is being used, and why does that matter at scale?
- [ ] List, in your own words, every distinct "network" this design needs (hint: there are three, and they serve three genuinely different purposes — not just three arbitrary VLAN numbers).
- [ ] Draw the full chain from "a client picks a wireless network name" to "the client's traffic lands on a specific IP subnet." You'll need every link in this chain correct before configuring anything.

---

## 2. Design Your Own Addressing Plan

You're given only the following constraints. Work out everything else yourself.

**Constraints:**

- Three separate networks are required: controller management, an Internal (employee) WLAN, and a Guest WLAN.
- Each needs to comfortably support at least 200 devices with room to grow — pick an appropriately sized subnet for each.
- The three networks must not overlap with each other.

### Your task

1. Choose three non-overlapping subnets — one per network — sized appropriately for the device-count requirement above. Justify your prefix-length choice for at least one of them with the `2^h − 2` host-count math.
2. Assign a VLAN ID to each of the three networks (any non-conflicting numbers are fine — this isn't the same tightly-constrained decision as an addressing plan, but explain your reasoning for keeping them clearly distinct, e.g. not sequential/easily confused numbers for a lab this security-sensitive).
3. For each of your two client-facing networks (Internal, Guest), assign an IP address the WLC's own dynamic interface for that network will use — and explain why that address needs to be *on* that subnet, not just near it.
4. Write out, explicitly, why the controller's management address must NOT be on either client-facing subnet — argue this from a security perspective, not just "because the lab says so."

Only after finishing all 4 steps, compare against Section 4 of the full manual.

---

## 3. Build the Topology (Packet Tracer)

- [ ] Place a WLC, two lightweight APs, a multilayer switch, and at least one wired PC plus two wireless clients (one for each SSID you'll create).
- [ ] Cable the WLC and both APs to the switch, and configure the necessary trunk/VLAN carrying on those switchports — figure out which VLANs need to traverse which links before configuring anything on the WLC itself.
- [ ] Confirm you can reach the WLC's management GUI from your wired PC before proceeding — if you can't, you have a wired-side problem to solve first (see Section 5 of this practice lab for why that distinction matters).

---

## 4. Configure — Prompts Only

### 4.1 Controller-level setup

- [ ] What must be true about an access point's relationship to the controller before that AP can broadcast any SSID at all? Where in the WLC GUI would you check this?
- [ ] What are the WLC's two 802.11 radio bands, and where would you confirm both are enabled?

### 4.2 Dynamic interfaces

- [ ] What piece of information does a WLC dynamic interface actually configure — is it primarily about wireless security, or about something else entirely (think back to your Section 2 answers)?
- [ ] Create two dynamic interfaces using your own addressing plan. What three pieces of information does each one need at minimum?
- [ ] What has to exist *before* you can map a WLAN to one of these interfaces — in other words, what's the correct order of operations here, and what happens if you get it backwards?

### 4.3 WLANs (SSIDs)

- [ ] Create two WLAN profiles. For each, what interface does it map to, and how does that determine which VLAN a client's traffic ultimately lands on?
- [ ] Why can't a single WLAN profile serve both the Internal and Guest use case — what specifically about a WLAN profile's structure prevents that?
- [ ] Configure WPA2-PSK security on each WLAN, using a different passphrase for each. What's the actual security consequence of reusing the same passphrase across both networks, even though nothing would technically stop you?
- [ ] What's the single most common reason a fully configured WLAN doesn't actually broadcast its SSID? (You'll want this answer memorized, not looked up, for the self-check later.)

### 4.4 Client association

- [ ] Associate a wireless client with each SSID, supplying the correct PSK for each.
- [ ] Predict, before checking, which IP subnet each client will receive an address from — write your prediction down.

---

## 5. Verify — Predict Before You Check

- [ ] In the WLC's interface table, predict what you'll see for each dynamic interface (name, VLAN ID, IP address) before opening that page.
- [ ] In the WLANs table, predict the Admin Status and Security Policy column values before opening that page.
- [ ] In the client monitoring page, predict which AP and which WLAN profile each of your two wireless clients will show under, and what IP address range each will fall into.
- [ ] From the Guest wireless client, attempt to ping a device on the Internal subnet. Predict success or failure and explain your reasoning *before* testing — then explain why VLAN separation alone might or might not be sufficient to guarantee your predicted outcome (hint: think about what a router with routes to both subnets could still do).

---

## 6. Explain Your Design

Answer without referencing the full manual:

1. Draw the full SSID → WLAN → Dynamic Interface → VLAN → Subnet chain from memory, for both of your two networks.
2. Why is a centralized WLC architecture more manageable than configuring each AP independently once you have more than a handful of APs?
3. Why does the WLC's own management interface need to be on a separate VLAN from both client-facing WLANs?
4. A client successfully authenticates and associates to an SSID but never receives a usable IP address. Is this more likely a wireless-configuration problem or a wired-configuration problem? Explain your reasoning — this is the single biggest "aha" this lab is trying to produce.
5. Why would a real company likely prefer WPA2/3-Enterprise (802.1X) over WPA2-PSK for its Internal network, even though PSK is simpler to set up?

---

## 7. Troubleshoot Yourself

Deliberately break your own lab in 3 different ways (pick 3), then diagnose using the layered workflow you designed in Section 1:

- Leave one WLAN in a Disabled state and try to find it from a client.
- Configure a client with the wrong PSK.
- Remove one required VLAN from a switch trunk carrying traffic to an AP.
- Swap which dynamic interface a WLAN is mapped to (Internal WLAN mapped to the Guest interface).
- Assign the WLC's management interface to the same VLAN as one of the client WLANs, and explain — without needing to prove it maliciously — why this is a real problem even if nothing "breaks" in an observable way during your test.

For each: write the symptom, which layer of the troubleshooting workflow caught it, and the fix.

---

## 8. Self-Check

- [ ] I designed three non-overlapping subnets and justified their sizing before opening the WLC GUI.
- [ ] I can draw the SSID → WLAN → Dynamic Interface → VLAN → Subnet chain from memory.
- [ ] I predicted verification output before checking each WLC page, and compared afterward.
- [ ] I could explain all 5 design-reasoning questions in Section 6 out loud to someone else.
- [ ] I intentionally broke and fixed at least 3 things without looking at the troubleshooting table first.

Once complete, open [`Day-58-Lab-Manual.md`](Day-58-Lab-Manual.md) and diff your work against Sections 4, 6–10, and 13 in detail.
