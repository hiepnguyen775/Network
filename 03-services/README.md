# Phase 3 — SERVICES

> Những dịch vụ làm cho network "dùng được". Người làm infra thường đã quen phần này ở mức dùng — ở đây học ở mức **cấu hình trên thiết bị mạng**.

| | |
|---|---|
| **Chủ đề** | DHCP · DNS · NAT/PAT · NTP · Syslog · SNMP · SSH · QoS cơ bản |
| **Số lesson** | 4 |
| **Thời lượng** | ~2 tuần |
| **Công cụ lab** | Packet Tracer |
| **Prerequisite** | Phase 0, 1, 2 |

---

## 🎯 Mục tiêu phase

- [ ] Cấu hình router làm DHCP server **và** DHCP relay, giải thích được khi nào cần relay
- [ ] PC trong LAN private ra Internet qua PAT, chỉ ra được địa chỉ nguồn bị dịch ở **hop nào**
- [ ] Bật SSH đúng cách (không còn telnet), hiểu vì sao cần `crypto key generate rsa`
- [ ] Đọc được syslog và biết severity level nào đáng báo động

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 25 | **DHCP triển khai**: option, reservation, relay nhiều server | [`lesson-25-dhcp-trien-khai.md`](./lesson-25-dhcp-trien-khai.md) | LAB 30 | ⬜ |
| 26 | **DNS doanh nghiệp**: zone, split-DNS, TTL strategy | [`lesson-26-dns-doanh-nghiep.md`](./lesson-26-dns-doanh-nghiep.md) | LAB 31 | ⬜ |
| 27 | **NAT nâng cao**: port forwarding, dual-WAN, NAT+VPN ⭐ | [`lesson-27-nat-nang-cao.md`](./lesson-27-nat-nang-cao.md) | LAB 32 | ⬜ |
| 28 | NTP · Syslog · SNMP · QoS fundamentals | [`lesson-28-ntp-syslog-snmp-qos.md`](./lesson-28-ntp-syslog-snmp-qos.md) | LAB 33 | ⬜ |

📝 **Kết thúc phase:** [`review-phase03.md`](./review-phase03.md) — tổng kết + Mini Exam 20 câu

> 📦 **Phase 3 xây trên Phase 0.** Lesson 08 (DNS/DHCP) và 09 (NAT) đã dạy **khái niệm**;
> phase này dạy **triển khai & vận hành**. Mỗi lesson có hộp "Phase 0 đã dạy gì —
> lesson này thêm gì" ở đầu.

---

## 🧪 Lab của phase

| Lab | Lesson | Nội dung | File |
|---|:---:|---|---|
| LAB 30 | 25 | DHCP server + relay + reservation | *(tự tạo từ template)* |
| LAB 31 | 26 | DNS nội bộ, nslookup so sánh, file hosts | *(tự tạo từ template)* |
| LAB 32 | 27 | PAT, port forwarding, dual-WAN NAT | *(tự tạo từ template)* |
| LAB 33 | 28 | NTP + Syslog + SNMP (management plane) | *(tự tạo từ template)* |

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| Nhầm `ip nat inside` / `ip nat outside` | Đặt sai interface → NAT im lặng không chạy, không báo lỗi |
| DHCP không tới được client ở VLAN khác | DHCP Discover là broadcast — cần `ip helper-address`, không phải route |
| Quên `ip dhcp excluded-address` | DHCP cấp luôn IP của gateway/server → xung đột IP |
| Bật SSH mà quên `transport input ssh` | Telnet vẫn mở, tưởng đã an toàn |
| Thiết bị sai giờ, log vô nghĩa | NTP không phải chuyện nhỏ — không có NTP thì không correlate được log |
| Học QoS quá sâu ở CCNA | CCNA chỉ cần khái niệm. Đào sâu ở [`CCNP-Encor` Module 09](https://github.com/hiepnguyen775/CCNP-Encor) |

---

## 🚪 Cổng ra phase

- [ ] LAB: LAN 2 VLAN → DHCP từ router → PAT ra "Internet" → SSH quản trị, chạy end-to-end
- [ ] Giải thích được toàn bộ 4 bước DORA kèm địa chỉ nguồn/đích của từng bước
- [ ] Mini Exam Phase 3 ≥ 80%

---

## 🔗 Tài nguyên

- 🔌 [`cheatsheets/ports-va-protocols.md`](../cheatsheets/ports-va-protocols.md)
- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md)
