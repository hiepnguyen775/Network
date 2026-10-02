# MODULE REVIEW — Phase 3: Services

| | |
|---|---|
| **Phase** | 3 — Services |
| **Số lesson** | 4 (25 → 28) |
| **Thời lượng dự kiến** | 2 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 3 trong 8 câu

1. Phase 0 dạy *khái niệm* DHCP/DNS/NAT; Phase 3 dạy **triển khai và vận hành** chúng.
2. DHCP cấp cả một **bộ cấu hình** qua option: gateway (3), DNS (6), lease (51), TFTP (150).
3. **`giaddr`** cho DHCP server biết client ở subnet nào → chọn đúng pool.
4. **Split-DNS**: cùng tên, trả IP nội bộ cho người trong, IP public cho người ngoài.
5. ⭐ **Giảm TTL xuống 300s trước vài ngày** khi sắp chuyển server.
6. ⭐ Gói **đi ra**: routing → NAT. Gói **đi vào**: NAT → routing.
   ACL trên outside inbound thấy **IP public**.
7. Traffic VPN **phải được `deny`** trong NAT-ACL, nếu không tunnel không lên.
8. ⭐ **NTP là nền móng** — thiếu nó thì syslog, chứng chỉ, AD đều hỏng.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| DHCP option 150 | TFTP server cho IP phone — thiếu là phone không đăng ký được | 25 |
| `client-identifier` | `01` + MAC, **không phải** MAC thuần | 25 |
| `giaddr` | IP của SVI nhận gói → server chọn pool theo nó | 25 |
| Lease strategy | Văn phòng 8h · guest 1–2h · voice 7 ngày · server reservation | 25 |
| Authoritative vs recursive | Giữ dữ liệu gốc vs đi hỏi hộ và cache | 26 |
| Reverse zone / PTR | IP→tên, IP viết ngược; cần cho mail server | 26 |
| Split-DNS | Trả IP khác nhau tuỳ người hỏi từ đâu | 26 |
| TTL strategy | Giảm trước khi chuyển, tăng lại sau | 26 |
| Thứ tự NAT/routing | Ra: route→NAT · Vào: NAT→route | 27 |
| `deny` trong NAT-ACL | Nghĩa là **"không NAT"**, không phải "chặn" | 27 |
| Dual-WAN NAT | Cần **route-map** với `match interface` | 27 |
| NAT ALG | FTP active, SIP, IPsec AH — NAT phá giao thức nhúng IP | 27 |
| Stratum | Khoảng cách tới nguồn thời gian chuẩn; 16 = không đồng bộ | 28 |
| 8 severity | 0 Emergency → 7 Debugging; cấu hình N = gửi 0→N | 28 |
| SNMP polling vs trap | NMS hỏi (161) vs thiết bị báo (162) | 28 |
| DSCP EF (46) | Nhãn ưu tiên cao nhất, dành cho thoại | 28 |
| Policing vs Shaping | Drop vs Đệm | 28 |
| Trust boundary | Ranh giới ngừng tin nhãn QoS từ bên ngoài | 28 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `show ip dhcp pool` | ⭐ Pool còn bao nhiêu IP (>80% là mở rộng) | 25 |
| `show ip dhcp binding` | Ai giữ IP nào, `Automatic` vs `Manual` | 25 |
| `debug ip dhcp server packet` | ⭐ Thấy từng gói DORA | 25 |
| `ip helper-address <ip>` | Relay — đặt trên SVI **phía client** | 25 |
| `option 150 ip <ip>` | IP phone | 25 |
| `nslookup <tên> <server>` | ⭐ So kết quả giữa các DNS server | 26 |
| `dig -x <ip>` | Reverse lookup | 26 |
| `ipconfig /flushdns` | Xoá cache sau khi đổi record | 26 |
| `no ip domain-lookup` | Tắt treo 30s khi gõ nhầm | 26 |
| `ip nat inside source static tcp ...` | Port forwarding | 27 |
| `ip nat inside source route-map X interface Y overload` | Dual-WAN | 27 |
| `show ip nat statistics` | ⭐ Hits/Misses, đã khai hướng chưa | 27 |
| `clear ip nat translation *` | Sau failover WAN | 27 |
| `ntp server <ip>` + `clock timezone ICT 7` | ⭐ Luôn làm đầu tiên | 28 |
| `service timestamps log datetime msec localtime` | Log có giờ thật | 28 |
| `logging host <ip>` + `logging trap notifications` | Syslog tập trung | 28 |
| `snmp-server community X RO <acl>` | ⚠️ Luôn kèm ACL | 28 |
| `show ntp status` / `show ntp associations` | Đã đồng bộ chưa | 28 |

## 4. Common Mistakes

| Sai lầm | Hậu quả |
|---|---|
| `client-identifier` dùng MAC thuần | Reservation **im lặng** không chạy |
| Pool subnet không khớp SVI | Client nhận IP khác subnet gateway |
| DHCP server không có route về subnet client | Relay đi được nhưng reply không về |
| Quên option 150 | IP phone có IP nhưng không đăng ký |
| Chỉ mở UDP/53 trên firewall | Một số domain "lúc được lúc không" |
| Đổi IP mà không giảm TTL trước | Một phần thế giới vào IP cũ cả ngày |
| Quên cập nhật một bên split-DNS | Trong vào được, ngoài không — hoặc ngược lại |
| ACL outside khớp IP private | ACL **không bao giờ khớp** |
| Không loại trừ traffic VPN khỏi NAT | **Tunnel không lên** |
| Dual-WAN dùng một quy tắc NAT | Traffic ra WAN2 mang IP private |
| Failover xong không clear NAT | Kết nối cũ chết |
| Không cấu hình NTP | Log vô nghĩa, chứng chỉ lỗi, AD hỏng |
| Quên `clock timezone` / `service timestamps` | Log lệch 7 tiếng, hoặc chỉ có uptime |
| `logging trap 7` trên production | Ngập log, chôn vùi thông tin quan trọng |
| SNMP v2c không ACL, community mặc định | Lộ toàn bộ cấu hình mạng |
| Nghĩ QoS giải quyết thiếu băng thông | Nó chỉ chọn ai bị hy sinh |

## 5. Interview Questions

1. **Q:** DHCP server đặt ở VLAN 10, client ở VLAN 20. Cần gì và cơ chế hoạt động ra sao?
   **A:** Cần `ip helper-address <server>` trên **SVI của VLAN 20** (phía client).
   Router đổi broadcast Discover thành unicast tới server, và **điền `giaddr`** = IP của
   SVI VLAN 20. Server đọc `giaddr` để biết chọn pool của subnet `10.0.20.0/24`.
   Server cũng **phải có route về** subnet đó để gửi reply.

2. **Q:** Split-DNS là gì? Vì sao doanh nghiệp cần?
   **A:** Cùng một tên trả IP khác nhau tuỳ người hỏi từ trong hay ngoài.
   Lý do: (a) nhân viên truy cập server nội bộ không phải đi vòng ra Internet;
   (b) không phụ thuộc NAT hairpin; (c) không lộ cấu trúc IP nội bộ.
   Cái giá: phải cập nhật **hai** zone — quên một bên là lỗi phổ biến.

3. **Q:** Bạn viết ACL trên interface WAN chiều `in` để chỉ cho HTTPS tới web server
   nội bộ `10.0.50.20` (public `203.0.113.5`). ACL khớp IP nào?
   **A:** **`203.0.113.5`**. Vì với gói đi vào, thứ tự là: ACL inbound → NAT → routing.
   Lúc ACL chạy, NAT ngược chưa xảy ra nên gói vẫn mang IP public.

4. **Q:** VPN site-to-site không lên sau khi bật NAT. Nguyên nhân?
   **A:** Traffic đi VPN bị NAT thành IP public → không khớp crypto ACL của tunnel →
   không được mã hoá. Sửa: thêm dòng `deny ip <local> <remote>` **đứng trước** `permit`
   trong NAT-ACL, rồi `clear ip nat translation *`.

5. **Q:** Vì sao NTP phải cấu hình trước syslog?
   **A:** Vì syslog không có giờ đúng thì **không correlate được sự kiện giữa các thiết bị**.
   Hai switch lệch 3 phút → không biết sự kiện nào là nguyên nhân, cái nào là hệ quả.
   Ngoài ra NTP còn ảnh hưởng chứng chỉ TLS, Kerberos/AD, backup theo lịch.

6. **Q:** Policing và Shaping khác nhau thế nào?
   **A:** Cả hai giới hạn tốc độ. **Policing drop** gói vượt ngưỡng (nghiêm khắc,
   không tốn buffer, gây mất gói). **Shaping đệm** gói vượt rồi gửi sau (mềm dẻo,
   tốn buffer, tăng delay). ISP thường police; khách hàng thường shape để khớp
   tốc độ đã mua.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | Máy nhận `169.254.x.x` | Không có mạng | `debug ip dhcp server packet` | Thiếu helper, hoặc pool hết |
| 2 | Có OFFER không có ACK | IP sai dải | Wireshark lọc `dhcp`, xem Src của OFFER | **Rogue DHCP** |
| 3 | Web mở chậm 5–10s rồi mới load | "Mạng chậm" | `nslookup <tên> <dns1>` | DNS#1 chết, đang timeout rồi fallback |
| 4 | Trong vào được, ngoài không | Khách hàng báo lỗi | `nslookup` từ mạng 4G | Split-DNS lệch |
| 5 | Server nội bộ không vào được từ Internet | Port đóng | `show ip nat translations`, `show access-lists` | ACL khớp IP private |
| 6 | Failover WAN xong vẫn mất mạng | "Đợi vài phút mới được" | `show ip nat translations` | Entry NAT cũ còn IP WAN chết |
| 7 | Mạng chậm giờ cao điểm | Chiều nào cũng chậm | `show ip nat statistics` — `Misses` tăng | Bảng NAT đầy |
| 8 | Không điều tra được sự cố đa thiết bị | Log lộn xộn | `show ntp status` | NTP chưa đồng bộ |
| 9 | Thoại rè, méo tiếng | VoIP kém | `show policy-map interface` | Jitter cao, thiếu LLQ hoặc trust boundary sai |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa sang Phase 4.

### Phần A — Lý thuyết (10 câu)

1. Kể 5 DHCP option quan trọng và chúng cấp gì.
2. `giaddr` là gì, do ai điền, để làm gì?
3. `client-identifier` khác MAC address thế nào?
4. Authoritative và recursive DNS server khác nhau thế nào? Vì sao không nên gộp?
5. Forward zone và reverse zone khác nhau thế nào? PTR cần cho việc gì?
6. Split-DNS là gì? Nêu 2 lợi ích và 1 rủi ro vận hành.
7. Khi nào DNS dùng TCP thay vì UDP? Kể 3 trường hợp.
8. Thứ tự xử lý NAT/routing/ACL cho gói **đi ra** và gói **đi vào**?
9. Kể 8 severity level của syslog theo thứ tự. `logging trap 5` gửi những mức nào?
10. QoS: 3 vấn đề nó giải quyết? Ngưỡng VoIP cho từng cái?

### Phần B — Cấu hình (6 câu)

11. Viết pool DHCP cho VLAN 60 (IP phone): `10.0.60.0/24`, gateway `.1`,
    TFTP `10.0.50.20`, lease 7 ngày, loại trừ `.1`–`.49`.
12. Viết NAT-ACL loại trừ traffic VPN giữa `10.0.0.0/24` và `10.1.0.0/24`,
    NAT phần còn lại ra `Gi0/1`.
13. Viết port forwarding cho web server `10.0.50.20:443` ra `203.0.113.5:443`,
    kèm ACL chỉ cho HTTPS vào.
14. Viết cấu hình NTP: server `10.0.50.30`, timezone Việt Nam, timestamp có mili-giây.
15. Viết cấu hình syslog: server `10.0.50.40`, mức notifications, source từ Loopback0.
16. Viết cấu hình SNMP v2c RO với community `Str0ng123`, chỉ cho NMS `10.0.50.41`.

### Phần C — Tình huống (4 câu)

17. Client ở VLAN 20 không nhận được IP. `debug` trên router thấy DISCOVER được relay
    đi nhưng không có gì về. Nêu 2 nguyên nhân.
18. Bạn đổi A record của `web.cty.vn` lúc 9h sáng. 15h chiều vẫn có người vào IP cũ.
    Vì sao? Lần sau làm gì khác?
19. Sau khi bật NAT, VPN site-to-site không lên. Giải thích cơ chế và cách sửa.
20. Hai switch log cùng một sự cố nhưng lệch 3 phút. Hậu quả? Sửa thế nào?

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Cấu hình | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20** | ✅ Sang [Phase 4 — IPv6](../04-ipv6/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai |
| < 12 | ❌ Học lại Phase 3 |

> ⚠️ Sai **câu 8, 19, hoặc 20** thì dù tổng điểm cao vẫn phải ôn lại.

### Yêu cầu bổ sung để qua phase

- [ ] LAN 2 VLAN → DHCP từ router (1 VLAN trực tiếp, 1 VLAN qua relay) → PAT ra Internet
      → SSH quản trị, chạy end-to-end
- [ ] Giải thích được toàn bộ DORA kèm địa chỉ nguồn/đích từng bước
- [ ] Đã bổ sung khối NTP + Syslog + SNMP vào "config chuẩn"
- [ ] Đã làm LAB 30 → 33, mỗi lab có mục BREAK điền đầy đủ

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
