# 🃏 Flashcards — Phase 0: Foundation

> Che phần **A** lại, tự trả lời **thành tiếng** trước khi xem.
> Nói ra được mới tính là nhớ — nghĩ trong đầu "à đúng rồi" là ảo giác thuộc bài.
>
> **Nhịp ôn:** ngày 1 → ngày 3 → ngày 7 → ngày 21.

---

## 🔹 OSI & Encapsulation

**Q:** OSI có mấy tầng, kể từ dưới lên?
**A:** 7 — Physical, Data Link, Network, Transport, Session, Presentation, Application.

**Q:** Đơn vị dữ liệu (PDU) ở tầng 2, 3, 4 lần lượt là gì?
**A:** L2 = **Frame**, L3 = **Packet**, L4 = **Segment** (TCP) / Datagram (UDP).

**Q:** MAC address nằm ở tầng OSI nào? IP address ở tầng nào?
**A:** MAC = **L2** (Data Link); IP = **L3** (Network).

**Q:** Switch hoạt động ở tầng nào? Router?
**A:** Switch = L2 (L3 switch làm được cả L3). Router = L3.

**Q:** Giá trị thực của mô hình OSI khi đi làm là gì?
**A:** **Khoanh vùng lỗi theo tầng** — debug từ dưới lên, không nhảy thẳng lên tầng ứng dụng.

---

## 🔹 Địa chỉ & đường đi

**Q:** Qua mỗi hop (router), cái gì thay đổi, cái gì giữ nguyên?
**A:** Source/Destination **MAC thay đổi** mỗi hop; Source/Destination **IP giữ nguyên** (trừ khi NAT).

**Q:** ARP dùng để làm gì?
**A:** Phân giải **IP → MAC**, trong cùng một broadcast domain.

**Q:** ARP request gửi tới địa chỉ MAC nào?
**A:** Broadcast `FF:FF:FF:FF:FF:FF`. ARP reply thì là unicast.

**Q:** Default gateway dùng khi nào?
**A:** Khi đích nằm **khác subnet** — host gửi frame tới **MAC của gateway**, nhưng **IP đích vẫn là IP của máy đích**.

**Q:** Host biết đích nằm cùng subnet hay khác subnet bằng cách nào?
**A:** Lấy IP đích **AND** với subnet mask của chính mình, so với network của mình.

**Q:** TTL để làm gì? Nó giảm ở đâu?
**A:** Chống gói tin chạy vòng vô tận. **Mỗi router giảm 1**; về 0 thì drop và gửi ICMP Time Exceeded.

---

## 🔹 Broadcast / Collision domain

**Q:** Broadcast domain vs Collision domain — switch ảnh hưởng thế nào?
**A:** Mỗi port switch = **1 collision domain** riêng. Cả switch (1 VLAN) = **1 broadcast domain**.

**Q:** Cái gì chia nhỏ broadcast domain?
**A:** **VLAN** và **router** (interface router là biên của broadcast domain).

**Q:** Hub khác switch ở điểm cốt lõi nào?
**A:** Hub = **một** collision domain cho tất cả port, lặp tín hiệu mù. Switch học MAC và chuyển có chọn lọc.

---

## 🔹 TCP / UDP

**Q:** TCP khác UDP ở điểm cốt lõi nào?
**A:** TCP: connection-oriented, reliable, có 3-way handshake + ACK + retransmit.
UDP: connectionless, không đảm bảo, header chỉ 8 byte, nhanh/nhẹ.

**Q:** TCP 3-way handshake gồm?
**A:** **SYN → SYN-ACK → ACK**.

**Q:** Thấy `RST` ngay sau `SYN` trong Wireshark nghĩa là gì?
**A:** Không có dịch vụ nào nghe ở port đó, **hoặc** firewall chặn kiểu *reject* (khác với drop im lặng = timeout).

**Q:** DNS dùng TCP hay UDP?
**A:** **Cả hai.** UDP/53 cho query thường; TCP/53 cho zone transfer và reply quá lớn.

---

## 🔹 Port

**Q:** Port mặc định: HTTP / HTTPS / SSH / Telnet?
**A:** **80 / 443 / 22 / 23**.

**Q:** Port mặc định: DNS / DHCP server–client / NTP / Syslog / SNMP?
**A:** **53 / 67–68 / 123 / 514 / 161** (trap: 162).

**Q:** OSPF dùng port nào?
**A:** **Không dùng port** — OSPF là **protocol number 89**, chạy thẳng trên IP.

**Q:** ICMP / TCP / UDP có protocol number là gì?
**A:** **1 / 6 / 17**.

---

## 🔹 Subnetting

**Q:** Công thức số host usable?
**A:** `2^(32 − prefix) − 2` — trừ Network và Broadcast.

**Q:** Block size tính thế nào?
**A:** `256 − octet_mask` tại octet "thú vị".

**Q:** `/26` có mask gì, block size bao nhiêu, bao nhiêu host?
**A:** `255.255.255.192`, block **64**, **62** host.

**Q:** `/30` dùng để làm gì và được mấy host?
**A:** **Link point-to-point**, đúng **2** host.

**Q:** 192.168.10.100/26 → Network và Broadcast là gì?
**A:** Network `192.168.10.64`, Broadcast `192.168.10.127` (host: .65 → .126).

**Q:** Wildcard mask của `/24` và `/26`?
**A:** `0.0.0.255` và `0.0.0.63` — **nghịch đảo** subnet mask.

**Q:** Ba dải private RFC 1918?
**A:** `10.0.0.0/8` · `172.16.0.0/**12**` · `192.168.0.0/16`.

**Q:** Máy nhận IP `169.254.x.x` nghĩa là gì?
**A:** **APIPA** — không nhận được DHCP. Kiểm tra: cáp → VLAN của port → `ip helper-address` → pool còn IP không.

---

## 🔹 Dịch vụ nền

**Q:** 4 bước DHCP tên là gì?
**A:** **DORA** — Discover, Offer, Request, Acknowledge.

**Q:** DHCP Discover là unicast hay broadcast? Hệ quả?
**A:** **Broadcast** → không qua được router → VLAN khác cần `ip helper-address` (DHCP relay).

**Q:** NAT giải quyết vấn đề gì?
**A:** Thiếu IPv4 public — nhiều host private dùng chung IP public. PAT phân biệt bằng **port**.

**Q:** Unicast / Broadcast / Multicast khác nhau thế nào?
**A:** Unicast = 1→1; Broadcast = 1→tất cả trong broadcast domain; Multicast = 1→một nhóm đăng ký.

---

## 📊 Theo dõi ôn tập

| Lần ôn | Ngày | Số câu sai | Câu cần ôn lại |
|:---:|---|:---:|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
