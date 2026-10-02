# MODULE REVIEW — Phase 6: Security

| | |
|---|---|
| **Phase** | 6 — Security |
| **Số lesson** | 4 (35 → 38) |
| **Thời lượng dự kiến** | 2 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 6 trong 8 câu

1. **CIA**: Confidentiality *(mã hoá)* · Integrity *(hash)* · Availability *(dự phòng)* —
   ba trụ cột đánh đổi lẫn nhau.
2. **AAA**: *"anh là ai"* · *"được làm gì"* · *"đã làm gì"*. Accounting là thứ trả lời
   **"ai đã làm sập mạng"**.
3. ⭐ **RADIUS cho người dùng vào mạng · TACACS+ cho kỹ sư vào thiết bị.**
4. ⭐ **Luôn có `local` ở cuối câu lệnh AAA** — quên là mất quyền vào mọi thiết bị.
5. ⭐ ACL: **từ trên xuống, dừng ở dòng khớp đầu** · **implicit deny** · **cụ thể trước, chung sau**.
6. ⭐ ACL inbound trên WAN thấy **IP public** *(chạy trước NAT)*.
7. ⭐ **DAI và IPSG phụ thuộc binding table của DHCP Snooping** — sai thứ tự là sập mạng.
8. ⭐ **Bảo mật L2 phải làm ở L2** — firewall ở biên mù với traffic trong cùng VLAN.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| CIA Triad | Confidentiality · Integrity · Availability | 35 |
| AAA | Authentication · Authorization · Accounting | 35 |
| RADIUS | UDP 1812/1813, chỉ mã hoá password, gộp Auth+Authz, chuẩn mở | 35 |
| TACACS+ | TCP 49, mã hoá toàn bộ, tách 3 A, **command authorization** | 35 |
| `local` fallback | ⭐ Dây an toàn khi AAA server chết | 35 |
| Privilege level | Phân cấp bậc thang — hạn chế so với TACACS+ | 35 |
| 3 quy tắc ACL | Trên xuống · implicit deny · 1 interface 1 hướng 1 ACL | 36 |
| Standard vs Extended | Chỉ source → gần đích · đủ thông tin → gần nguồn | 36 |
| Wildcard mask | Nghịch đảo subnet mask; `host x` ≡ `x 0.0.0.0` | 36 |
| `established` | Khớp gói TCP có ACK/RST — stateless firewall thô sơ | 36 |
| Counter `(N matches)` | ⭐ Công cụ debug ACL mạnh nhất | 36 |
| DHCP Snooping | Chống rogue DHCP; tạo **binding table** | 37 |
| Binding table | `(MAC, IP, VLAN, port)` — nền tảng của DAI và IPSG | 37 |
| DAI | Chống ARP spoofing — đối chiếu ARP với binding | 37 |
| IPSG | Chống IP spoofing — đối chiếu source IP với binding | 37 |
| Option 82 | Hay gây lỗi — thường phải tắt | 37 |
| VLAN hopping | Switch spoofing *(DTP)* và double tagging *(native VLAN)* | 38 |
| MAC flooding | Làm đầy CAM table → switch hoá hub | 38 |
| STP attack | Gửi BPDU priority thấp → cướp root bridge | 38 |
| `vlan dot1q tag native` | Triệt tiêu double tagging | 38 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `username admin-local privilege 15 secret X` | ⭐ **Trước** khi bật AAA | 35 |
| `aaa authentication login default group X local` | ⭐ Có fallback | 35 |
| `aaa authorization commands 15 default group X local` | Kiểm soát từng lệnh | 35 |
| `aaa accounting commands 15 default start-stop group X` | Ghi log mọi lệnh | 35 |
| `test aaa group X <user> <pass> legacy` | ⭐ Test an toàn trước khi áp dụng | 35 |
| `show aaa servers` | Server UP hay DOWN | 35 |
| `ip access-list extended <TEN>` | Named ACL | 36 |
| `ip access-group <acl> in` / `access-class <acl> in` | Áp lên interface / vty | 36 |
| `ipv6 traffic-filter <acl> in` | ACL IPv6 | 36 |
| `show access-lists` | ⭐ Counter từng dòng | 36 |
| `reload in 10` | ⭐ Lưới an toàn khi áp ACL | 36 |
| `ip dhcp snooping` + `trust` uplink | ⭐ Chống rogue DHCP | 37 |
| `no ip dhcp snooping information option` | Tránh lỗi Option 82 | 37 |
| `ip dhcp snooping database flash:...` | Giữ bảng qua reboot | 37 |
| `ip arp inspection vlan N` | Bật DAI | 37 |
| `ip source binding <mac> vlan N <ip> interface X` | Khai IP tĩnh | 37 |
| `switchport nonegotiate` | ⭐ Tắt DTP — chống switch spoofing | 38 |
| `vlan dot1q tag native` | Chống double tagging | 38 |
| `show interfaces status err-disabled` | ⭐ Port nào bị tắt, vì sao | 38 |
| `show logging \| include SECURITY\|DAI\|SNOOPING` | ⭐ Nhật ký tấn công L2 | 38 |

## 4. Common Mistakes

| Sai lầm | Hậu quả |
|---|---|
| Quên `local` ở cuối AAA | **Mất quyền vào mọi thiết bị** khi server chết |
| `aaa new-model` khi chưa có user local | Mất quyền **ngay lập tức** |
| Console dùng chung method với vty | Không còn đường cứu |
| Dùng TACACS+ cho 802.1X | 802.1X phải dùng **RADIUS** |
| Dùng subnet mask thay wildcard | ACL khớp sai, IOS không báo lỗi |
| `permit any` ở dòng đầu ACL | Mọi dòng sau vô nghĩa |
| ACL WAN khớp IP private | Không bao giờ khớp |
| Quên permit IP quản trị trong ACL | **Tự khoá mình** |
| Chặn `packet-too-big` | Web có nội dung lớn bị treo |
| Quên trust uplink khi bật snooping | **Cả switch không ai nhận được IP** |
| Bật DAI khi binding table rỗng | **Mọi ARP bị drop** — cả VLAN chết |
| Không khai IP tĩnh trước khi bật DAI | Server, máy in, camera mất mạng |
| Để port ở `dynamic auto` | Kẻ tấn công thương lượng thành trunk |
| Dùng VLAN 1 làm native | Mở đường double tagging |
| Bật `dot1q tag native` một đầu | Mất kết nối trunk |
| Làm hết cấu hình nhưng không khoá tủ mạng | Mọi biện pháp vô dụng |

## 5. Interview Questions

1. **Q:** Khi nào dùng RADIUS, khi nào dùng TACACS+?
   **A:** **RADIUS** cho người dùng vào mạng *(802.1X, VPN, Wi-Fi)* — chuẩn mở, UDP nhẹ,
   mọi hãng hỗ trợ. **TACACS+** cho kỹ sư vào thiết bị — tách Authorization riêng nên
   kiểm soát được **từng lệnh**, mã hoá **toàn bộ** payload, dùng TCP đáng tin.

2. **Q:** Vì sao câu lệnh AAA phải có `local` ở cuối?
   **A:** Vì nếu AAA server chết mà không có phương án dự phòng, **không ai vào được
   thiết bị nào** — phải chạy tới chỗ cắm console hoặc password recovery.
   `local` cho phép fallback về tài khoản local khi server không phản hồi.

3. **Q:** Standard ACL đặt gần đích, extended gần nguồn. Vì sao?
   **A:** Standard **chỉ biết source IP**, không biết đích — đặt gần nguồn sẽ chặn luôn
   mọi đường đi của host đó, kể cả đường bạn muốn cho phép. Extended biết đủ
   source + dest + port nên chặn sớm **tiết kiệm băng thông** — không chở gói đi khắp
   mạng rồi mới vứt.

4. **Q:** Bạn áp ACL trên WAN interface chiều `in` để cho HTTPS tới web server nội bộ
   `10.0.50.20` (NAT ra `203.0.113.5`). ACL khớp IP nào?
   **A:** **`203.0.113.5`** — IP public. Với gói đi vào, thứ tự là
   `ACL inbound → NAT → routing`. Khi ACL chạy, NAT ngược chưa xảy ra.

5. **Q:** Vì sao phải bật DHCP Snooping **trước** DAI, và chờ 1–2 ngày?
   **A:** DAI kiểm tra gói ARP bằng cách đối chiếu với **binding table** do DHCP Snooping
   tạo. Bật DAI khi bảng còn rỗng → **mọi ARP đều "không khớp"** → bị drop hết →
   cả VLAN mất mạng. Phải chờ client gia hạn lease để bảng đầy đủ.

6. **Q:** Giải thích VLAN hopping bằng double tagging.
   **A:** Kẻ tấn công ở **native VLAN**, gửi frame có **2 tag**. Switch A gỡ tag ngoài
   (vì là native → không tag khi ra trunk), đẩy ra trunk với tag trong còn nguyên.
   Switch B thấy tag đó và đưa gói vào VLAN đích. Chống bằng: native VLAN là
   **VLAN rỗng không dùng**, và `vlan dot1q tag native`.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | Không SSH được vào thiết bị nào | Mọi nơi đều fail | Console vào, `show run \| include aaa` | Thiếu `local` + server chết |
| 2 | ACL không có tác dụng | Traffic vẫn qua | `show access-lists` → `(0 matches)` | Chưa áp, hoặc sai hướng |
| 3 | Web server không vào được từ Internet | Port đóng | `show access-lists` counter = 0 | ACL WAN khớp IP private |
| 4 | Mất SSH ngay sau khi áp ACL | Đứt kết nối | Console | Tự khoá mình |
| 5 | Bật snooping xong cả VLAN mất mạng | Không ai nhận IP | `show ip dhcp snooping` cột Trusted | Quên trust uplink |
| 6 | Bật DAI xong mọi thứ chết | Ping fail hết | `show ip dhcp snooping binding` trống | Binding table rỗng |
| 7 | Chỉ server/máy in mất mạng sau DAI | Một số thiết bị | `show ip arp inspection statistics` | IP tĩnh chưa khai binding |
| 8 | Port người dùng trong `show interfaces trunk` | — | `show interfaces trunk` | DTP tự thương lượng |
| 9 | "Một số máy mất mạng ngẫu nhiên" | IP sai dải | `show logging \| include SNOOPING` | Rogue DHCP |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa sang Phase 7.

### Phần A — Lý thuyết (10 câu)

1. CIA Triad gồm gì? Mỗi trụ cột bảo vệ bằng cơ chế nào?
2. Giải thích 3 chữ A bằng ví dụ đời thường.
3. So sánh RADIUS và TACACS+ ở **6 khía cạnh**. Dùng cái nào cho việc nào?
4. Kể 3 quy tắc bất biến của ACL.
5. Standard và extended ACL khác nhau thế nào? Đặt ở đâu và vì sao?
6. Wildcard mask của `/24`, `/26`, `/30`? `host x` và `any` tương đương gì?
7. Thứ tự xử lý gói đi vào router: ACL, NAT, routing — cái nào trước?
8. DHCP Snooping, DAI, IPSG — mỗi cái chống gì, và chúng phụ thuộc nhau thế nào?
9. Kể 2 kỹ thuật VLAN hopping và cách phòng thủ từng cái.
10. Kể 6 tấn công L2 và biện pháp tương ứng.

### Phần B — Cấu hình (6 câu)

11. Viết cấu hình AAA đầy đủ: TACACS+ `10.0.50.60`, có fallback local,
    console dùng method riêng.
12. Viết ACL: VLAN 90 (`10.0.90.0/24`) được dùng DNS `10.0.50.10`, **cấm** mọi thứ khác
    vào `10.0.0.0/16`, **được** ra Internet.
13. Viết ACL trên WAN `in` cho phép HTTPS tới `203.0.113.5` và chống IP spoofing.
14. Viết cấu hình DHCP Snooping cho VLAN 10,20 với uplink `Gi1/0/48`.
15. Viết `ip source binding` cho server IP tĩnh `10.0.50.20`, MAC `001a.2b3c.4d5e`,
    VLAN 50, port `Gi1/0/8`.
16. Viết khối cấu hình chuẩn cho access port *(ít nhất 8 dòng bảo mật)*.

### Phần C — Tình huống (4 câu)

17. Kỹ sư gõ `aaa authentication login default group tacacs+` rồi `wr`.
    Ba tháng sau server chết. Chuyện gì xảy ra? Khôi phục thế nào?
18. ACL có dòng `permit ip any any` ở vị trí 10 và `deny tcp any any eq 23` ở vị trí 20.
    Telnet có bị chặn không? Vì sao?
19. Bật DHCP Snooping xong cả VLAN mất mạng. Nêu 2 nguyên nhân theo thứ tự khả năng.
20. Mọi biện pháp L2 đã bật đầy đủ. Còn lỗ hổng nào **không có lệnh nào vá được**?

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
| **≥ 16/20** | ✅ Sang [Phase 7 — WAN/VPN](../07-wan-vpn/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai |
| < 12 | ❌ Học lại Phase 6 |

> ⚠️ Sai **câu 7, 8, hoặc 18** thì dù tổng điểm cao vẫn phải ôn lại.

### Yêu cầu bổ sung để qua phase

- [ ] Viết được ACL cho một yêu cầu bằng tiếng Việt, áp đúng chỗ, verify đúng
- [ ] Dựng lab rogue DHCP → chứng minh DHCP Snooping chặn được
- [ ] Đã lưu **khối cấu hình chuẩn** vào `06-security/config-chuan-access-port.txt`
- [ ] Đã làm LAB 60 → 63, mỗi lab có mục BREAK điền đầy đủ

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
