# MODULE REVIEW — Phase 0: Foundation

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Số lesson** | 10 |
| **Thời lượng dự kiến** | 3 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 0 trong 10 câu

1. Network = thiết bị + môi trường truyền + protocol chung.
2. OSI 7 tầng không phải để đọc thuộc — nó là **thứ tự kiểm tra khi debug**, từ dưới lên.
3. Encapsulation: mỗi tầng bọc thêm một header trả lời một câu hỏi khác nhau.
4. **MAC đổi mỗi hop, IP giữ nguyên** — trừ khi có NAT.
5. Subnet mask chia IP thành phần mạng + phần host; host dùng **phép AND** để quyết định
   gửi thẳng hay gửi qua gateway.
6. Switch **học từ source MAC**, **chuyển theo destination MAC**, không biết thì **flood**.
7. Broadcast dừng ở router → đó là biên của broadcast domain, và là lý do DHCP cần relay.
8. ARP phân giải IP → MAC, chỉ trong một broadcast domain.
9. TCP khi dữ liệu phải **đúng**, UDP khi dữ liệu phải **đúng giờ**.
10. NAT ra đời vì hết IPv4; IPv6 ra đời để không cần NAT nữa.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| Mô hình OSI | Khung khoanh vùng lỗi theo tầng | 01 |
| Encapsulation | Mỗi tầng thêm header giải một bài toán riêng | 01 |
| Subnet mask | Đường kẻ chia mạng/host; quyết định gửi thẳng hay qua GW | 02 |
| Magic number | `Block size = 256 − octet_mask` | 02 |
| MAC learning | Học source, chuyển theo destination, không biết thì flood | 03 |
| Broadcast domain | Chỉ **VLAN** và **router** chia nhỏ được | 04 |
| ARP | IP → MAC, request broadcast, reply unicast | 05 |
| TTL | Giảm mỗi hop; về 0 thì drop — nền của traceroute | 05 |
| Socket | `(SrcIP, SrcPort, DstIP, DstPort)` định danh một kết nối | 06 |
| 3-way handshake | `SYN → SYN-ACK → ACK` | 06 |
| VLSM | Cấp **lớn trước** để không phân mảnh | 07 |
| DORA | Discover → Offer → Request → ACK, `Src = 0.0.0.0` | 08 |
| DHCP relay | `ip helper-address` biến broadcast thành unicast | 08 |
| PAT | Nhiều máy chung 1 IP public, phân biệt bằng **port** | 09 |
| NDP | Thay ARP ở IPv6, chạy trên ICMPv6 | 10 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `show ip interface brief` | Lệnh đầu tiên khi debug bất cứ gì | 01 |
| `show cdp neighbors` | Dựng lại topology thật | 01 |
| `show mac address-table` | Máy X đang cắm ở port nào | 03 |
| `clear mac address-table dynamic` | Ép học lại sau khi đổi dây | 03 |
| `storm-control broadcast level 1.00` | Chống broadcast storm | 04 |
| `show ip arp` / `arp -a` | Kiểm tra IP↔MAC | 05 |
| `ping <ip> source <int>` | Debug ACL/NAT đúng source | 05 |
| `ping <ip> size 1500 df-bit` | Kiểm tra MTU | 05 |
| `traceroute <ip>` | Gói chết ở hop nào | 05 |
| `telnet <ip> <port>` | Test port nhanh nhất | 06 |
| `show ip dhcp binding` / `pool` | DHCP đã cấp gì, còn bao nhiêu | 08 |
| `ip helper-address <ip>` | Relay DHCP qua router | 08 |
| `no ip domain-lookup` | Tắt treo 30s khi gõ nhầm | 08 |
| `show ip nat translations` | Ai đang được NAT thành gì | 09 |
| `show ipv6 neighbors` | Bảng NDP | 10 |

## 4. Common Mistakes

| Sai lầm | Vì sao hay sai | Cách tránh |
|---|---|---|
| Số host = `2^n` | Quên Network + Broadcast | Luôn `2^n − 2` |
| `172.16.0.0/16` là private | Nhìn quen `/16` | Dải private là `172.16.0.0/**12**` |
| Dùng subnet mask trong `network` của OSPF | Hai thứ trông giống nhau | OSPF/ACL dùng **wildcard** |
| "PC phải ARP tìm MAC của server ở xa" | Nhầm vai trò MAC và IP | Chỉ cần MAC của **gateway** |
| "Switch học từ destination MAC" | Trực giác sai | Học **source**, chuyển theo **destination** |
| Nhầm collision domain với broadcast domain | Hai khái niệm gần nhau | VLAN đổi broadcast domain, **không** đổi collision domain |
| Chia VLSM từ nhỏ đến lớn | Không biết ràng buộc bội số | **Lớn trước** |
| Quên `default-router` trong DHCP pool | Pool trông đã đủ | Có IP mà không ra được ngoài |
| Đặt `ip helper-address` phía server | Trực giác "trỏ về server" | Đặt phía **client** |
| Quên `ip nat inside/outside` | Không có thông báo lỗi | NAT im lặng không chạy |
| Chặn hết ICMPv6 | Quen tư duy IPv4 | IPv6 **sống nhờ** ICMPv6 |

## 5. Interview Questions

> Câu hỏi phỏng vấn thật, mức junior Network Engineer.

1. **Q:** Mô tả chuyện gì xảy ra từ lúc bạn gõ `google.com` tới lúc trang hiện ra.
   **A:** DNS resolve tên → IP · kiểm tra cùng/khác subnet bằng phép AND · ARP tìm MAC gateway ·
   TCP 3-way handshake tới port 443 · TLS handshake · HTTP request/response.
   Dọc đường: NAT ghi lại source IP/port, mỗi router giảm TTL và viết lại MAC.

2. **Q:** Máy nhận IP `169.254.1.5`. Bạn làm gì?
   **A:** Đó là APIPA — DHCP không tới được. Kiểm tra theo thứ tự: cáp/port up →
   port đúng VLAN chưa → có `ip helper-address` không → pool còn IP không → có rogue DHCP không.

3. **Q:** PC A ping được gateway nhưng không ping được server ở subnet khác. Lần ra sao?
   **A:** L1–L2 đã ổn (ping được GW). Kiểm tra: router có route **đi** không;
   router phía kia có route **về** không; ACL có chặn không; NAT có sai không;
   gateway của server có đúng không.

4. **Q:** `telnet host 443` treo 30 giây rồi timeout, nhưng `telnet host 80` báo
   "Connection refused" ngay. Khác nhau chỗ nào?
   **A:** Port 80 trả `RST` → gói **tới được máy**, chỉ là không có service nghe.
   Port 443 im lặng → bị **DROP** ở đâu đó trên đường, thường là firewall.
   Suy ra máy đích tới được; vấn đề 443 nằm trên đường đi.

5. **Q:** Vì sao broadcast domain lớn là vấn đề?
   **A:** Mọi broadcast buộc **tất cả** máy xử lý rồi mới vứt → lãng phí CPU toàn mạng.
   Sự cố lan rộng, khó khoanh vùng. Ngưỡng thực tế ~250 host (một `/24`).

6. **Q:** NAT có phải firewall không?
   **A:** Không. NAT chỉ ghi lại header, không lọc theo luật, không kiểm tra nội dung,
   không ghi log như firewall. Việc nó chặn kết nối từ ngoài vào là **tác dụng phụ**
   của việc không có entry trong bảng — malware vẫn mở được đường về bằng cách
   chủ động kết nối ra.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | Hai máy ping **một chiều** | A→B được, B→A không | So mask ở cả 2 máy | **Mask mismatch** |
| 2 | Cả VLAN mất mạng sau khi bật tính năng mới | Ping gì cũng fail | `show ip arp` trống | Bật DAI mà chưa có DHCP snooping binding |
| 3 | Mạng treo, đèn port nháy đồng loạt | Tất cả chậm/đứng | `show spanning-tree` | **Loop L2** → broadcast storm |
| 4 | Một số máy mất mạng ngẫu nhiên | IP sai dải | Wireshark lọc `dhcp`, xem Src của Offer | **Rogue DHCP** |
| 5 | Web load mãi rồi lỗi | Ping OK, web treo | Wireshark: `SYN` lặp 3 lần | Firewall **drop** port |
| 6 | Tải file rất chậm, ping bình thường | Throughput thấp | `tcp.analysis.retransmission` | **Mất gói** trên đường |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**, không máy tính. Chấm xong: **< 80% thì quay lại ôn**, chưa sang Phase 1.

### Phần A — Lý thuyết (10 câu, mỗi câu 1 điểm)

1. Kể 7 tầng OSI từ dưới lên. PDU của tầng 2, 3, 4 là gì?
2. Qua mỗi router, cái gì trong header thay đổi, cái gì giữ nguyên? Ngoại lệ duy nhất là gì?
3. Switch học MAC từ field nào? Nó làm gì khi không biết destination MAC?
4. Hai thứ nào chia nhỏ broadcast domain? Switch thường có chia được không?
5. ARP phân giải gì sang gì? Request là broadcast hay unicast? Reply thì sao?
6. Vì sao ARP không qua được router?
7. Kể 3 bước của TCP 3-way handshake. Vì sao đóng kết nối cần 4 bước?
8. Port mặc định: SSH / DNS / DHCP server-client / HTTPS / SNMP / Syslog?
9. Kể 4 bước DORA. Src IP của Discover là gì và điều đó dẫn tới hệ quả gì?
10. Vì sao IPv6 không có ARP? Cái gì thay thế và nó chạy trên giao thức nào?

### Phần B — Tính toán (6 câu, mỗi câu 1 điểm)

11. `192.168.20.150/26` → Network, First, Last, Broadcast, số host usable?
12. `10.0.8.77/22` → Network, Broadcast, số host usable?
13. `/27` có mask gì? Block size? Bao nhiêu host?
14. Wildcard mask của `/25` và `/30`?
15. Chia VLSM từ `192.168.5.0/24` cho: 100, 50, 20, 10 host và 2 WAN link `/30`. Đủ không?
16. Rút gọn tối đa: `2001:0db8:0000:0000:0000:00ab:0000:1234`

### Phần C — Tình huống (4 câu, mỗi câu 1 điểm)

17. PC-A `10.0.0.5/24`, PC-B `10.0.0.200/26`, không có router.
    A ping B được không? B ping A được không? Giải thích **từng chiều**.
18. Máy nhận `169.254.x.x`. Nêu **4 bước** kiểm tra theo đúng thứ tự.
19. Bạn cấu hình NAT đầy đủ nhưng `show ip nat translations` rỗng, `Hits: 0`.
    Nêu 3 nguyên nhân theo thứ tự nên kiểm tra.
20. Một ACL IPv6 chặn hết ICMPv6. Kể 3 thứ sẽ hỏng và vì sao.

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Tính toán | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20 (80%)** | ✅ Sang [Phase 1 — Switching](../01-switching/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai, làm lại sau 3 ngày |
| < 12 | ❌ Học lại Phase 0 — đừng tự lừa mình bằng cách đi tiếp |

> ⚠️ Sai **câu 2, 6, hoặc 17** thì dù tổng điểm cao vẫn phải ôn lại.
> Ba câu đó đo đúng thứ phân biệt người hiểu network và người thuộc định nghĩa.

### Yêu cầu bổ sung để qua phase

- [ ] 20 câu subnetting liên tiếp, đúng ≥ 18, trung bình **< 30 giây/câu**
- [ ] Đã làm LAB 01 → 06, **mỗi lab có mục BREAK điền đầy đủ**
- [ ] Giải thích được packet flow PC → SW → R → R → Server cho người khác nghe hiểu

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

> Điền sau khi chấm — đây là đầu vào cho spaced repetition ở các phase sau.

-
-
