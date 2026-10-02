# 🧪 LABS

> Mỗi LAB một file: `labNN-ten-khong-dau.md`, tạo từ [`../templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md).
> Luôn giữ lại **cấu hình cuối** + **ghi chú lỗi** ở mục BREAK.

---

## ⚠️ Quy tắc bất di bất dịch

> **Lab chưa làm bước BREAK là lab chưa xong.**

Cấu hình chạy được chỉ chứng minh bạn **gõ đúng**. Cố tình phá rồi tự tìm lại được nguyên nhân
mới chứng minh bạn **hiểu**. Mỗi lab phải phá tối thiểu **3 lỗi** và ghi lại đủ 5 cột:

```
triệu chứng → lệnh đã dùng → nguyên nhân gốc → cách sửa → bài học
```

Mỗi lỗi tìm ra → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 🔢 Quy ước đánh số LAB

Mỗi phase được cấp một **dải số riêng** — nhờ vậy lesson có thể tham chiếu tới lab chưa tạo
mà không bao giờ đụng số của phase khác.

| Phase | Dải LAB | | Phase | Dải LAB |
|:---:|:---:|---|:---:|:---:|
| 0 — Foundation | `01 – 09` | | 5 — Wireless | `50 – 59` |
| 1 — Switching | `10 – 19` | | 6 — Security | `60 – 69` |
| 2 — Routing | `20 – 29` | | 7 — WAN/VPN | `70 – 79` |
| 3 — Services | `30 – 39` | | 🏁 Final CCNA Project | `99` |
| 4 — IPv6 | `40 – 49` | | | |

Tên file: `labNN-ten-khong-dau.md` — ví dụ `lab11-vlan-va-trunk.md`.

---

## 📋 Index

| # | LAB | Phase | Lesson | Công cụ | Độ khó | BREAK ✅ | Ngày |
|:---:|---|:---:|:---:|---|:---:|:---:|---|
| 01 | [VLSM cho công ty 4 phòng ban](./lab01-vlsm-cong-ty-4-phong-ban.md) | 0 | 02 | Packet Tracer | ⭐ | ⬜ | — |
| 02 | [Bắt ARP + ICMP bằng Wireshark](./lab02-arp-icmp-wireshark.md) | 0 | 05 | Wireshark | ⭐ | ⬜ | — |
| 03 | [TCP 3-way handshake vs UDP](./lab03-tcp-udp-wireshark.md) | 0 | 06 | Wireshark | ⭐ | ⬜ | — |
| 04 | [Thiết kế IP plan doanh nghiệp](./lab04-ip-plan-doanh-nghiep.md) | 0 | 07 | Giấy + PT | ⭐⭐ | ⬜ | — |
| 05 | *DHCP server + relay 2 VLAN* | 0 | 08 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 06 | *PAT + static NAT* | 0 | 09 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 10 | *Cisco IOS CLI căn bản* | 1 | 12 | Packet Tracer | ⭐ | — | *(chưa tạo)* |
| 11 | [VLAN & Trunk giữa 2 switch](./lab11-vlan-va-trunk.md) | 1 | 13 | Packet Tracer | ⭐⭐ | ⬜ | — |
| 12 | [Inter-VLAN Routing: RoAS và SVI](./lab12-inter-vlan-routing.md) | 1 | 14 | Packet Tracer | ⭐⭐ | ⬜ | — |
| 13 | [STP: root, port role, storm](./lab13-stp.md) | 1 | 15 | Packet Tracer | ⭐⭐⭐ | ⬜ | — |
| 14 | *RSTP, PortFast, BPDU Guard* | 1 | 16 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 15 | *EtherChannel + Port Security* | 1 | 17 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 20 | *Routing table cơ bản* | 2 | 18 | Packet Tracer | ⭐ | — | *(chưa tạo)* |
| 21 | *Static, default, floating static* | 2 | 19 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 22 | *Thứ tự chọn route, longest prefix* | 2 | 20 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 23 | [OSPF single-area: neighbor, DR/BDR, đọc LSDB](./lab23-ospf-single-area.md) | 2 | 22 | Packet Tracer | ⭐⭐⭐ | ⬜ | — |
| 24 | *OSPF multi-area & summarization* | 2 | 24 | Packet Tracer | ⭐⭐⭐ | — | *(chưa tạo)* |
| 30 | *DHCP server + relay + reservation* | 3 | 25 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 31 | *DNS nội bộ, nslookup, file hosts* | 3 | 26 | PT + máy thật | ⭐⭐ | — | *(chưa tạo)* |
| 32 | *PAT, port forwarding, dual-WAN NAT* | 3 | 27 | Packet Tracer | ⭐⭐⭐ | — | *(chưa tạo)* |
| 33 | *NTP + Syslog + SNMP* | 3 | 28 | Packet Tracer | ⭐⭐ | — | *(chưa tạo)* |
| 40 | *IPv6 addressing plan, EUI-64* | 4 | 29 | Giấy + PT | ⭐⭐ | — | *(chưa tạo)* |
| 41 | *SLAAC, NDP, DHCPv6 3 chế độ* | 4 | 30 | PT + Wireshark | ⭐⭐⭐ | — | *(chưa tạo)* |
| 42 | *IPv6 routing, OSPFv3, dual-stack* | 4 | 31 | Packet Tracer | ⭐⭐⭐ | — | *(chưa tạo)* |
| 50 | *Bảo mật Wi-Fi: PSK, 802.1X, ACL guest* | 5 | 34 | Packet Tracer | ⭐⭐⭐ | — | *(chưa tạo)* |
---

## 🏁 FINAL CCNA PROJECT

> Làm sau khi xong Phase 7. Đây là bài tổng hợp — nếu làm được bài này mà không mở tài liệu,
> bạn đã sẵn sàng thi và, quan trọng hơn, sẵn sàng làm việc.

### Đề bài

Thiết kế và triển khai network cho một công ty **100–300 users**:

| Hạng mục | Yêu cầu |
|---|---|
| Quy mô | 2 tầng văn phòng, 1 phòng server, ~6 phòng ban |
| WAN | 2 đường Internet (dual-WAN, có failover) |
| Wireless | Phủ sóng 2 tầng, SSID riêng cho nhân viên và khách |
| Server | DHCP, DNS, file server nội bộ |

### Bắt buộc có

- [ ] **IP plan bằng VLSM** — không lãng phí, có dự phòng tăng trưởng 30%
- [ ] **VLAN** theo phòng ban + VLAN riêng cho management, voice, guest
- [ ] **Inter-VLAN routing** bằng L3 switch (SVI)
- [ ] **STP** có root bridge được chỉ định rõ ràng (không để bầu ngẫu nhiên)
- [ ] **EtherChannel** giữa switch core và distribution
- [ ] **DHCP** (có relay cho VLAN khác) + **DNS**
- [ ] **Static + OSPF** (ít nhất 2 area)
- [ ] **NAT/PAT** ra Internet
- [ ] **ACL**: guest không vào được mạng nội bộ; chỉ IT vào được VLAN management
- [ ] **SSH** quản trị, tắt telnet
- [ ] **Wireless** với WPA2-Enterprise cho nhân viên, WPA2-PSK cho khách
- [ ] **Floating static** làm backup khi OSPF chết

### Nộp gì

| Sản phẩm | Mô tả |
|---|---|
| `topology.png` hoặc sơ đồ ASCII | Sơ đồ đầy đủ, ghi rõ interface và IP |
| `ip-plan.md` | Bảng VLSM đầy đủ, giải thích cách chia |
| `configs/` | Cấu hình đầy đủ từng thiết bị |
| `verification.md` | Output `show` chứng minh từng yêu cầu đã đạt |
| `troubleshooting.md` | **Nhật ký lỗi đã gặp** — phần quan trọng nhất |

### Buổi troubleshooting cuối

Nhờ người khác (hoặc AI) **phá 5 lỗi** trong file cấu hình của bạn mà không cho biết là lỗi gì.
Tự tìm lại trong **60 phút**. Đây là bài kiểm tra thật sự.

---

## 📂 Gợi ý tổ chức thư mục cho Final Project

```text
labs/
└── final-ccna-project/
    ├── README.md
    ├── topology.png
    ├── ip-plan.md
    ├── verification.md
    ├── troubleshooting.md
    └── configs/
        ├── CORE-SW1.txt
        ├── DIST-SW1.txt
        ├── ACCESS-SW1.txt
        └── EDGE-R1.txt
```
