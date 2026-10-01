# 🗺️ ROADMAP — Network Fundamentals → CCNA → CCNP → Automation

> Tick `[x]` khi **đã học chắc**: hiểu được *tại sao*, cấu hình được, verify được, troubleshoot được.
> Đọc qua một lần **không** tính là xong.

---

## Cách dùng file này

| | |
|---|---|
| 🎯 | Mỗi mục là một **đơn vị kiến thức**, thường tương ứng 1 lesson (1–2 buổi học) |
| ⭐ | Mục có dấu sao = **trọng tâm**, sai chỗ này thì các phase sau sẽ tắc |
| 🧪 | Mục có dấu này **bắt buộc có LAB**, không lab không được tick |
| ⏱ | Ước lượng theo nhịp **8–10 giờ/tuần** |

---

## 📊 Tổng quan thời lượng

| Phase | Chủ đề | Lesson ước tính | Thời lượng | Repo |
|:---:|---|:---:|:---:|---|
| 0 | Foundation | 10 | 3 tuần | *(đây)* |
| 1 | Switching | 7 | 3 tuần | *(đây)* |
| 2 | Routing | 7 | 3 tuần | *(đây)* |
| 3 | Services | 4 | 2 tuần | *(đây)* |
| 4 | IPv6 | 3 | 1.5 tuần | *(đây)* |
| 5 | Wireless | 3 | 1 tuần | *(đây)* |
| 6 | Security | 4 | 2 tuần | *(đây)* |
| 7 | WAN / VPN | 3 | 1.5 tuần | *(đây)* |
| 🏁 | **Final CCNA Project** | 1 | 1–2 tuần | *(đây)* |
| 8 | CCNP Enterprise | — | ~20 tuần | [CCNP-Encor](https://github.com/hiepnguyen775/CCNP-Encor) |
| 9 | Network Automation | — | ~16 tuần | [Network-Automation](https://github.com/hiepnguyen775/Network-Automation) |

**Tổng Phase 0 → Final CCNA: ~18–20 tuần.**

---

## PHASE 0 — NETWORK FOUNDATION
📁 [`00-foundation/`](./00-foundation/) · ⏱ ~3 tuần

- [ ] Network là gì · LAN/WAN · Client-Server vs Peer-to-Peer
- [ ] OSI Model · TCP/IP Model · Encapsulation / Decapsulation ⭐
- [ ] Ethernet · MAC Address · Frame · Switch học MAC thế nào
- [ ] IPv4 · Subnet Mask · CIDR · Binary
- [ ] **Subnetting**: Network / Broadcast / First / Last host · số host · VLSM · tính nhanh ⭐🧪
- [ ] Default Gateway · ARP · ICMP 🧪
- [ ] TCP vs UDP · Port · 3-way handshake ⭐
- [ ] DNS · DHCP · HTTP/HTTPS · NAT (mức khái niệm)
- [ ] Unicast / Broadcast / Multicast · Broadcast domain
- [ ] IPv6 (giới thiệu — học sâu ở Phase 4)

> **Cổng ra Phase 0:** subnet bất kỳ `/x` trong đầu dưới 30 giây, và vẽ được đường đi của gói tin
> từ PC1 sang PC2 khác subnet, nói rõ MAC/IP đổi ở đâu.

---

## PHASE 1 — SWITCHING
📁 [`01-switching/`](./01-switching/) · ⏱ ~3 tuần

- [ ] Switching · MAC address table · Collision vs Broadcast domain · Hub vs Switch
- [ ] Cisco IOS CLI · config modes · interface · speed/duplex · lưu config 🧪
- [ ] VLAN · Access port · Trunk · 802.1Q · Native VLAN ⭐🧪
- [ ] Inter-VLAN Routing · Router-on-a-Stick · L3 Switch (SVI) ⭐🧪
- [ ] STP · RSTP · Root bridge election · Port roles/states ⭐🧪
- [ ] EtherChannel · LACP · PAgP 🧪
- [ ] Port Security 🧪

> **Cổng ra Phase 1:** dựng được 2 switch + 2 VLAN + trunk + inter-VLAN routing từ con số 0,
> và tự tìm được lỗi khi cố tình đặt sai native VLAN.

---

## PHASE 2 — ROUTING
📁 [`02-routing/`](./02-routing/) · ⏱ ~3 tuần

- [ ] Routing fundamentals · Routing table · Connected / Local route
- [ ] Static route · Default route · Floating static 🧪
- [ ] Administrative Distance · Metric · Longest prefix match ⭐
- [ ] Dynamic routing (khái niệm) · RIPv2 (chỉ concept/lịch sử)
- [ ] OSPF single-area · Neighbor · States · DR/BDR ⭐🧪
- [ ] OSPF Cost · Router ID · LSDB · LSA (mức CCNA) ⭐
- [ ] OSPF multi-area 🧪

> **Cổng ra Phase 2:** đọc `show ip route` và giải thích được **mọi ký tự** ở đầu dòng,
> vì sao route này thắng route kia. OSPF không lên neighbor → biết lần theo thứ tự nào.

---

## PHASE 3 — SERVICES
📁 [`03-services/`](./03-services/) · ⏱ ~2 tuần

- [ ] DHCP (server, relay, DORA) · DNS · phân giải tên 🧪
- [ ] NAT: static · dynamic · PAT ⭐🧪
- [ ] NTP · Syslog · SNMP
- [ ] SSH · FTP/TFTP · HTTP/HTTPS · QoS fundamentals 🧪

> **Cổng ra Phase 3:** PC trong LAN private ra được Internet qua PAT, và bạn chỉ ra được
> địa chỉ nguồn bị dịch ở đúng hop nào.

---

## PHASE 4 — IPv6
📁 [`04-ipv6/`](./04-ipv6/) · ⏱ ~1.5 tuần

- [ ] Format · Global Unicast · Link-local · Unique Local · Multicast ⭐
- [ ] SLAAC · DHCPv6 · Neighbor Discovery · ICMPv6 ⭐🧪
- [ ] IPv6 routing · OSPFv3 · so sánh IPv4 vs IPv6 🧪

> **Cổng ra Phase 4:** giải thích được vì sao IPv6 **không có ARP** và cái gì thay thế nó.

---

## PHASE 5 — WIRELESS (mức CCNA)
📁 [`05-wireless/`](./05-wireless/) · ⏱ ~1 tuần

- [ ] WLAN · AP · WLC · SSID / BSSID · kiến trúc autonomous vs lightweight
- [ ] 2.4 / 5 / 6 GHz · Channels · Channel width · Roaming
- [ ] Authentication · WPA2 · WPA3 · Enterprise Wi-Fi (802.1X)

> **Cổng ra Phase 5:** nói được vì sao 2.4 GHz chỉ có 3 kênh không chồng lấn và điều đó
> ảnh hưởng gì tới thiết kế văn phòng.

---

## PHASE 6 — SECURITY FUNDAMENTALS
📁 [`06-security/`](./06-security/) · ⏱ ~2 tuần

- [ ] CIA Triad · AAA · RADIUS · TACACS+
- [ ] Standard ACL · Extended ACL ⭐🧪
- [ ] DHCP Snooping · Dynamic ARP Inspection · IP Source Guard 🧪
- [ ] Port Security nâng cao · L2 attacks (VLAN hopping, MAC flooding, rogue DHCP)

> **Cổng ra Phase 6:** viết được ACL chặn đúng thứ cần chặn mà không chặn nhầm,
> và biết đặt nó ở interface nào, hướng nào — **và vì sao**.

---

## PHASE 7 — WAN / ENTERPRISE
📁 [`07-wan-vpn/`](./07-wan-vpn/) · ⏱ ~1.5 tuần

- [ ] WAN concepts · Leased line · MPLS · Internet VPN · VPN fundamentals
- [ ] Site-to-Site VPN · Remote Access VPN
- [ ] GRE · IPsec fundamentals · SD-WAN concepts

> ⚠️ Packet Tracer không mô phỏng đủ IPsec — phần này chuyển sang **GNS3 / EVE-NG**.

---

## 🏁 FINAL CCNA PROJECT

📁 [`labs/`](./labs/) · ⏱ 1–2 tuần

> **Đề:** thiết kế + triển khai network cho công ty **100–300 users**, 2 tầng, 1 phòng server,
> 2 đường WAN.

Phải có đủ: VLAN · inter-VLAN · DHCP · DNS · static + OSPF · NAT/PAT · ACL · SSH ·
STP · EtherChannel · wireless · và một buổi **troubleshooting do người khác phá**.

Nộp kèm: topology, IP plan (VLSM), cấu hình đầy đủ, output verify, và **bản ghi lỗi đã gặp**.

---

## PHASE 8 — CCNP ENTERPRISE
📁 [`08-ccnp/`](./08-ccnp/) → **học tại [`CCNP-Encor`](https://github.com/hiepnguyen775/CCNP-Encor)**

Ở repo này chỉ giữ checklist để biết mình đang ở đâu trên bản đồ lớn:

- [ ] OSPF advanced · EIGRP concepts
- [ ] **BGP** fundamentals → advanced
- [ ] Route redistribution · Route filtering · PBR · Route-map · Summarization
- [ ] STP advanced · EtherChannel nâng cao · L2 design
- [ ] FHRP: HSRP · VRRP · GLBP
- [ ] High Availability: redundancy, convergence, failure domains
- [ ] Enterprise design: Access → Distribution → Core
- [ ] Overlay / virtualization · QoS · Network Assurance · Security · Automation

---

## PHASE 9 — NETWORK AUTOMATION
📁 [`09-automation/`](./09-automation/) → **học tại [`Network-Automation`](https://github.com/hiepnguyen775/Network-Automation)**

- [ ] REST API · JSON · YAML · HTTP methods · API auth
- [ ] Python cho Network Engineer
- [ ] Netmiko · Paramiko · NAPALM
- [ ] Ansible for Network Automation
- [ ] NETCONF · RESTCONF · YANG
- [ ] Idempotency · Git · CI/CD cho network config
- [ ] Source of Truth · GitOps · Production architecture

---

## 🏆 Cột mốc lớn

- [ ] Hoàn tất Entry Assessment + có roadmap cá nhân hoá
- [ ] Xong Phase 0 — subnetting thành phản xạ
- [ ] Xong Phase 1 — dựng được hạ tầng L2 hoàn chỉnh
- [ ] Xong Phase 2 — OSPF multi-area chạy và troubleshoot được
- [ ] Xong Phase 3–7
- [ ] **Final CCNA Project**
- [ ] 🎓 Đậu CCNA 200-301
- [ ] Xong Phase 8 → 🎓 CCNP ENCOR
- [ ] Xong Phase 9 → tự động hoá được công việc network hằng ngày
