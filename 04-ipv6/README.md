# Phase 4 — IPv6

> Đừng học IPv6 như "IPv4 nhưng dài hơn". Nó bỏ hẳn vài khái niệm cũ (broadcast, ARP) và thêm cơ chế mới.

| | |
|---|---|
| **Chủ đề** | Address types · SLAAC · DHCPv6 · Neighbor Discovery · ICMPv6 · OSPFv3 |
| **Số lesson** | 3 |
| **Thời lượng** | ~1.5 tuần |
| **Công cụ lab** | Packet Tracer + Wireshark |
| **Prerequisite** | Phase 0 (IPv4 vững), Phase 2 (OSPF) |

---

## 🎯 Mục tiêu phase

- [ ] Nhìn một địa chỉ IPv6 → nói ngay nó thuộc loại nào (GUA / LLA / ULA / Multicast)
- [ ] Giải thích được **vì sao IPv6 không có ARP** và cái gì thay thế
- [ ] Giải thích được **vì sao IPv6 không có broadcast** và cái gì thay thế
- [ ] Rút gọn / mở rộng địa chỉ IPv6 không cần nghĩ

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 29 | Format · rút gọn · Global Unicast · Link-local · ULA · Multicast ⭐ | — | | ⬜ |
| 30 | SLAAC · DHCPv6 (stateless/stateful) · Neighbor Discovery · ICMPv6 ⭐ | — | ✅ | ⬜ |
| 31 | IPv6 routing · static v6 · OSPFv3 · so sánh IPv4 ↔ IPv6 | — | ✅ | ⬜ |

---

## 🔁 Bảng đối chiếu IPv4 ↔ IPv6 — học thuộc bảng này là xong một nửa phase

| IPv4 | IPv6 | Ghi chú |
|---|---|---|
| ARP | **NDP** (Neighbor Solicitation / Advertisement) | Chạy trên ICMPv6, dùng multicast thay broadcast |
| Broadcast | **Multicast** (`ff02::1`, `ff02::2`) | IPv6 **không có** broadcast |
| DHCP bắt buộc (thường) | **SLAAC** hoặc DHCPv6 | Host tự sinh được địa chỉ từ RA |
| APIPA `169.254.x.x` | **Link-local** `fe80::/10` | IPv6 **luôn** có link-local trên mọi interface |
| Private `10/172.16/192.168` | **ULA** `fc00::/7` | |
| ICMP | **ICMPv6** | ICMPv6 gánh thêm NDP, RA/RS, MLD — chặn hết là chết mạng |
| Fragment ở router | Chỉ fragment ở **host nguồn** | Router IPv6 không fragment |

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| Chặn sạch ICMPv6 bằng ACL "cho an toàn" | NDP chết → mạng IPv6 ngừng hoạt động |
| Rút gọn `::` hai lần trong một địa chỉ | Chỉ được dùng `::` **một lần** |
| Quên `ipv6 unicast-routing` trên router | Router không route IPv6, không gửi RA |
| Nghĩ link-local là "không quan trọng" | Next-hop của route IPv6 thường **là** link-local |

---

## 🚪 Cổng ra phase

- [ ] Dựng OSPFv3 2 router, ping được bằng GUA
- [ ] Bắt được RA/NS/NA trong Wireshark và đọc hiểu
- [ ] Mini Exam Phase 4 ≥ 80%
