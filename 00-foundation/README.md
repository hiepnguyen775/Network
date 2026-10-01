# Phase 0 — NETWORK FOUNDATION

> Nền móng. Mọi thứ ở Phase 1–9 đều đứng trên phase này. Học ẩu ở đây = tắc ở OSPF mà không hiểu vì sao.

| | |
|---|---|
| **Chủ đề** | OSI/TCP-IP · IPv4 · **subnetting** ⭐ · ARP · ICMP · TCP/UDP · DNS/DHCP/NAT |
| **Số lesson** | 10 |
| **Thời lượng** | ~3 tuần (8–10 h/tuần) |
| **Công cụ lab** | Packet Tracer + Wireshark |
| **Prerequisite** | Không |

---

## 🎯 Mục tiêu phase

Xong phase này, bạn phải:

- [ ] Subnet một mạng `/x` bất kỳ **trong đầu, dưới 30 giây**
- [ ] Vẽ được đường đi gói tin từ PC1 → PC2 **khác subnet**, chỉ rõ MAC/IP đổi ở hop nào
- [ ] Giải thích được ARP xảy ra lúc nào, hỏi ai, và vì sao nó chỉ sống trong một broadcast domain
- [ ] Phân biệt được TCP và UDP không phải bằng định nghĩa, mà bằng **khi nào dùng cái nào**
- [ ] Đọc được một capture Wireshark của ICMP / DHCP / TCP handshake

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 01 | Network là gì · LAN/WAN · mô hình OSI & TCP/IP ⭐ | [`lesson-01-osi-va-tcp-ip.md`](./lesson-01-osi-va-tcp-ip.md) | | ⬜ |
| 02 | IPv4, subnet mask, CIDR, **subnetting** ⭐ | [`lesson-02-ipv4-va-subnetting.md`](./lesson-02-ipv4-va-subnetting.md) | ✅ | ⬜ |
| 03 | Ethernet · MAC address · Frame · switch học MAC | — | | ⬜ |
| 04 | Encapsulation / Decapsulation chi tiết | — | | ⬜ |
| 05 | Default Gateway · ARP · ICMP | — | ✅ | ⬜ |
| 06 | TCP vs UDP · Port · 3-way handshake ⭐ | — | ✅ | ⬜ |
| 07 | VLSM · chia địa chỉ cho một công ty thật | — | ✅ | ⬜ |
| 08 | DNS · DHCP (DORA) | — | ✅ | ⬜ |
| 09 | NAT — khái niệm · private vs public IP | — | | ⬜ |
| 10 | Unicast / Broadcast / Multicast · IPv6 giới thiệu | — | | ⬜ |

> Lesson chưa có file = chưa học tới. AI sẽ sinh nội dung khi bạn tới lesson đó,
> bạn copy [`templates/LESSON_TEMPLATE.md`](../templates/LESSON_TEMPLATE.md) rồi điền vào.

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| "Subnetting hiểu rồi, tính bằng máy tính là được" | Đề thi và lab thật không cho dùng máy tính. **Tốc độ là một kỹ năng riêng**, phải luyện. |
| Nhầm số host = `2^n` | Phải trừ Network + Broadcast → `2^n − 2` |
| Nghĩ ARP hỏi ra IP | ARP hỏi ra **MAC** từ IP đã biết |
| Nghĩ MAC giữ nguyên suốt đường đi | **MAC đổi mỗi hop**, chỉ IP giữ nguyên |
| Học thuộc 7 tầng OSI nhưng không dùng được | Giá trị của OSI là **khoanh vùng lỗi theo tầng**, không phải để đọc vanh vách |
| Bỏ qua Wireshark vì "thấy phiền" | Đây là lúc rẻ nhất để học đọc gói tin. Sau này không có thời gian quay lại. |

---

## 🧪 Lab của phase

| Lab | Nội dung | File |
|---|---|---|
| LAB 01 | Chia VLSM cho công ty 4 phòng ban + verify kết nối | [`labs/lab01-...`](../labs/) |
| LAB 02 | Bắt ARP + ICMP bằng Wireshark, đọc từng field | [`labs/lab02-...`](../labs/) |
| LAB 03 | Bắt TCP 3-way handshake + so sánh với UDP | [`labs/lab03-...`](../labs/) |

---

## 🚪 Cổng ra phase

Chỉ sang Phase 1 khi **tất cả** đúng:

- [ ] Làm 20 câu subnetting liên tiếp, đúng ≥ 18, trung bình < 30 giây/câu
- [ ] Mini Exam Phase 0 đạt ≥ 80%
- [ ] Giải thích được packet flow PC → SW → R → R → Server cho người khác nghe hiểu

---

## 🔗 Tài nguyên

- 🧮 [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md) — bảng magic number + cách tính nhanh
- 🔌 [`cheatsheets/ports-va-protocols.md`](../cheatsheets/ports-va-protocols.md) — port cần thuộc
- 🃏 [`flashcards/00-foundation.md`](../flashcards/00-foundation.md) — ôn 10 phút/ngày
- 📝 [`assessment/entry-assessment.md`](../assessment/entry-assessment.md) — kiểm tra đầu vào
