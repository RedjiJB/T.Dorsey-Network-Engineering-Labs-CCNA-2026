# Day 16 Practice Lab: Advanced VLAN Configuration & Voice VLAN

**Objective:** Configure VLANs for data and voice traffic; implement QoS tagging and management separation

---

## Part 1: Voice VLAN Design

**Scenario:** Your company deployed VoIP phones on the network. Each phone and its adjacent PC need different VLANs:
- **Data VLAN 10:** PC traffic
- **Voice VLAN 110:** IP phone traffic
- **Management VLAN 1:** Switch management

**Your Tasks:**
1. Design how a single access port on a switch can carry both data and voice traffic
2. Document which VLAN is tagged/untagged for the phone
3. Plan how a PC connected to a phone (phone has built-in switch) would work

**Key Concept:** Voice VLAN uses 802.1Q tagging on the phone; PC gets untagged data traffic

---

## Part 2: Configuration Challenge - Voice VLAN Setup

**Given:** Switch with voice-capable access ports, IP phones with data passthrough, PCs

**Configure:**
1. Enable voice VLAN on selected access ports
2. Set data VLAN to 10, voice VLAN to 110
3. Verify the phone learns both VLANs
4. Ensure PCs only see data VLAN

**Commands to Research:**
- `switchport voice vlan [vlan-id]` (Cisco syntax)
- `show int [port] switchport | include Voice`

**Verification:**
- [ ] Phone sends traffic tagged with VLAN 110
- [ ] PC sends traffic untagged (defaults to VLAN 10)
- [ ] Both can communicate with their respective servers
- [ ] Isolate voice and data traffic for QoS

---

## Part 3: VLAN Security - Private VLAN (PVLAN)

**Scenario:** You need to isolate certain devices from each other while keeping them in the same IP subnet. Example: Guest wireless devices should not see each other.

**Challenge:**
1. Research Private VLANs (community VLAN, isolated VLAN)
2. Design a PVLAN scheme for a guest network
3. Explain why PVLAN is better than separate VLANs for this use case

**Questions:**
- What's the advantage of PVLAN over just creating separate VLANs?
- Can isolated VLAN members communicate with the primary VLAN?
- How would you configure a community VLAN?

---

## Part 4: VLAN Access Control List (VACL)

**Scenario:** You want to block certain VLANs from communicating, even though routing normally would allow it. Example: Guest VLAN (99) should not reach Finance VLAN (20).

**Configure:**
1. Create a VACL that denies traffic from VLAN 99 to VLAN 20
2. Apply the VACL on all switches
3. Verify that Guest users cannot reach Finance servers
4. Verify that Finance can reach other VLANs normally

**Commands to Research:**
- `vlan access-map [name] [sequence]`
- `match [protocol] [source] [destination]`
- `action forward/drop`
- `vlan filter [map-name] vlan-list [vlan-id]`

**Verification Checklist:**
- [ ] `show vlan access-map` displays configured rules
- [ ] `show vlan filter` shows active VACL on VLANs
- [ ] Guest PC cannot ping Finance server
- [ ] Finance PC can ping other departments

---

## Part 5: Troubleshooting Exercise - Voice VLAN Issue

**Given Broken Scenario:**
IP phones are configured but can't reach the voice VLAN gateway. Data traffic works fine.

**Investigation Steps:**
1. `show int g0/1 switchport | include Voice` — Is voice VLAN configured?
2. `show vlan id 110 | include ACTIVE` — Does voice VLAN exist and is active?
3. `show int vlan 110` — Does the switch have management IP for voice VLAN?
4. `show ip route | include 10.0.110` — Does router have route to voice VLAN?
5. On the phone: Can you manually assign VLAN 110? Or is it DHCP-provided?

**Propose:** Write steps to fix the issue

---

## Part 6: Design Scenario - Multi-Building VLAN Strategy

**Context:** Your company has two buildings connected by a redundant fiber link. Each building has:
- 5 switches (access layer)
- 2 core switches (distribution layer)
- Router connecting to WAN

**Challenge:**
1. Design a VLAN scheme for 100 users across 10 departments
2. Decide which VLANs span multiple buildings vs. site-local
3. Plan trunk links (which trunks carry which VLANs?)
4. Propose how to scale if you add a third building

**Document:**
- VLAN assignment table (VLAN ID, name, subnet, sites)
- Trunk link diagram
- Core switch configuration (which VLANs on which trunks)

---

## Part 7: Prediction Exercise

**Scenario A:** You configure a port for VLAN 10 data and VLAN 110 voice, but accidentally set VLAN 110 as the access VLAN instead of voice VLAN.
- **Prediction:** What happens when the phone plugs in? Will it get a voice IP address?
- **Symptom:** Phone is unresponsive; PC connected to phone can ping

**Scenario B:** You create VACL to block VLAN 30 ↔ VLAN 40, but forget to apply it with `vlan filter`.
- **Prediction:** Can VLAN 30 users ping VLAN 40 users?
- **Why?** VACLs only work if applied; without `vlan filter`, they're just config

**Scenario C:** Native VLAN is VLAN 1 on the switch, but you configure voice VLAN as native on the phone.
- **Prediction:** Will the phone get voice services?
- **Issue:** Untagged traffic from phone goes to VLAN 1, not VLAN 110

---

## Part 8: Advanced Challenge - Dynamic VLAN Assignment (802.1X)

**Research Question:** What is 802.1X port-based authentication?

**Scenario:** You want to assign users to VLANs based on their login credentials (not just physical port).

**Questions:**
1. How does 802.1X work at a high level?
2. What components are needed (supplicant, authenticator, authentication server)?
3. Once authenticated, how is the VLAN assigned?
4. What's the advantage over static VLAN assignment?

**Note:** This is advanced and likely beyond CCNA scope, but valuable for enterprise networks.

---

## Part 9: Self-Check Walkthrough

**Understanding:**
- [ ] I can explain why voice VLANs are separate from data VLANs
- [ ] I know the difference between access VLAN and voice VLAN
- [ ] I understand VACL and when it's needed
- [ ] I can design a VLAN scheme for a realistic network

**Configuration:**
- [ ] I configured voice VLAN on access ports
- [ ] I verified phone and PC have correct VLAN membership
- [ ] I created and applied a VACL
- [ ] I tested isolation and normal routing

**Troubleshooting:**
- [ ] I can identify why voice VLAN isn't working
- [ ] I know the difference between configured but not applied VACL
- [ ] I can distinguish between switch-level and router-level VLAN issues

---

## Expected Outcomes

After this practice lab, you should be able to:
- [ ] Configure voice VLAN on IP phone access ports
- [ ] Design VLAN schemes that separate user types (data, voice, management)
- [ ] Implement VACL for inter-VLAN security
- [ ] Troubleshoot voice VLAN connectivity issues
- [ ] Explain modern VLAN design best practices (security, scalability)
