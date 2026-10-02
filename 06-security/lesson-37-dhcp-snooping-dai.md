# LESSON 37 — DHCP Snooping · Dynamic ARP Inspection · IP Source Guard

> 📌 Ba tính năng này **phải triển khai theo đúng thứ tự** — DAI và IPSG đều dựa vào
> bảng binding do DHCP Snooping tạo ra. Bật sai thứ tự là sập mạng.

| | |
|---|---|
| **Phase** | 6 — Security |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md), [Lesson 25](../03-services/lesson-25-dhcp-trien-khai.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Giải thích **rogue DHCP** và **ARP spoofing** tấn công thế nào
- [ ] Cấu hình DHCP Snooping với **trust port** đúng chỗ
- [ ] Hiểu **binding table** là nền tảng của cả DAI và IPSG
- [ ] Triển khai 3 tính năng **đúng thứ tự**, không gây gián đoạn
- [ ] Xử lý các tình huống đặc biệt: IP tĩnh, server, hypervisor

## 2. Prerequisite

- ARP hoạt động thế nào, ARP spoofing *(Lesson 05)*
- DORA, rogue DHCP *(Lesson 25)*
- `err-disabled` và cách khôi phục *(Lesson 16)*

---

## 3. Concept

### Hai tấn công L2 kinh điển

#### Rogue DHCP server

```text
1. Kẻ tấn công (hoặc nhân viên vô tình) cắm một router Wi-Fi vào mạng
2. Router đó bật DHCP sẵn
3. Máy nào xin IP mà nhận OFFER của nó trước → lấy IP sai
4. Gateway trỏ về kẻ tấn công → MITM, hoặc đơn giản là MẤT MẠNG
```

> 🔑 Triệu chứng đặc trưng: *"một số máy mất mạng, một số vẫn bình thường,
> bật tắt lại thì khác nhau"* — vì phụ thuộc server nào trả lời nhanh hơn.

#### ARP spoofing (ARP poisoning)

```text
1. Kẻ tấn công liên tục gửi ARP Reply giả:
      "10.0.10.1 (gateway) đang ở MAC-của-tôi"
2. Mọi máy cập nhật ARP cache theo gói giả
3. Traffic ra Internet đi qua máy kẻ tấn công
4. Hắn chuyển tiếp đi (để không ai nghi) nhưng ĐỌC ĐƯỢC HẾT
```

> ⚠️ **ARP không có cơ chế xác thực nào.** Bất kỳ ai cũng gửi được ARP Reply,
> và máy nhận **tin ngay** — kể cả khi không hỏi *(gratuitous ARP)*.
> Đây là lỗ hổng thiết kế từ 1982, không sửa được, chỉ **vá bằng DAI**.

### Ba tính năng — phụ thuộc lẫn nhau

```text
┌─────────────────────────────────────────┐
│       DHCP SNOOPING                     │
│  → tạo BINDING TABLE                    │
│    (MAC, IP, VLAN, port, lease)         │
└────────────┬────────────────┬───────────┘
             │                │
       ┌─────▼─────┐    ┌─────▼──────┐
       │    DAI    │    │   IPSG     │
       │ kiểm ARP  │    │ kiểm IP    │
       └───────────┘    └────────────┘
```

| Tính năng | Chống gì | Kiểm tra gì |
|---|---|---|
| **DHCP Snooping** | **Rogue DHCP** | Chỉ port `trust` được gửi DHCP **reply** |
| **DAI** | **ARP spoofing** | Gói ARP có khớp binding table không |
| **IPSG** | **IP spoofing** | Source IP của gói có khớp binding table không |

> ⭐ **DAI và IPSG KHÔNG hoạt động nếu không có binding table.**
> Bật DAI khi chưa có DHCP Snooping *(hoặc bảng còn rỗng)* → **mọi ARP bị drop** →
> **cả VLAN mất mạng**.

### DHCP Snooping — binding table

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip dhcp snooping binding
MacAddress          IpAddress       Lease(sec)  Type           VLAN  Interface
------------------  --------------  ----------  -------------  ----  --------------
00:1A:2B:3C:4D:5E   10.0.10.57      86215       dhcp-snooping  10    Fa0/5
00:1A:2B:3C:4D:6F   10.0.10.58      86190       dhcp-snooping  10    Fa0/6
```

Bảng này ghi lại **mọi máy đã nhận IP qua DHCP**: MAC nào, IP nào, VLAN nào, port nào.
Nó là **nguồn sự thật** cho DAI và IPSG.

### Trust vs Untrust

| Loại port | Cho phép gửi DHCP reply? | Đặt ở đâu |
|---|:---:|---|
| **Trust** | ✅ Có | Port nối **DHCP server thật**, hoặc **uplink** lên switch/router |
| **Untrust** *(mặc định)* | ❌ **Không** | Port nối **người dùng** |

```text
Port untrust nhận DHCPOFFER/ACK  →  DROP + có thể err-disable port
```

> ⚠️ **Lỗi phổ biến nhất: quên trust uplink.** Switch access nối lên distribution
> qua uplink; DHCP reply từ server đi xuống qua uplink đó. Nếu uplink là untrust →
> **toàn bộ switch không ai nhận được IP**.

### Option 82 — chỗ hay hỏng

DHCP Snooping mặc định **chèn Option 82** (DHCP Relay Information) vào gói Discover
khi chuyển tiếp, ghi lại port và switch nguồn.

```text
Vấn đề: switch chèn Option 82 nhưng giaddr vẫn là 0.0.0.0
     → nhiều DHCP server (đặc biệt IOS) TỪ CHỐI gói này
     → client không nhận được IP
```

**Sửa:**

```cisco
! Cách 1 — tắt chèn Option 82 (đơn giản nhất)
SW1(config)# no ip dhcp snooping information option

! Cách 2 — bảo server chấp nhận gói có Option 82 mà giaddr = 0
R1(config)# ip dhcp relay information trust-all
```

> 🏭 Đây là lỗi **rất hay gặp** khi bật DHCP Snooping lần đầu, và triệu chứng
> *("bật snooping xong cả VLAN mất mạng")* làm nhiều người tưởng mình cấu hình sai trust port.

### DAI — Dynamic ARP Inspection

```text
Gói ARP đi vào port UNTRUST:
  1. Lấy Sender MAC và Sender IP từ gói ARP
  2. Tra BINDING TABLE: cặp (MAC, IP, VLAN, port) này có tồn tại không?
     ├─ CÓ    → cho qua ✅
     └─ KHÔNG → DROP + log ❌
```

Port **trust** của DAI: bỏ qua kiểm tra — đặt ở **uplink** và port nối router.

### IPSG — IP Source Guard

```text
Gói IP đi vào port:
  Source IP có khớp binding table của port đó không?
  ├─ CÓ    → cho qua
  └─ KHÔNG → DROP
```

> 💡 IPSG chống **IP spoofing** — máy giả mạo IP của người khác.
> Nó mạnh nhất khi bật kèm `port-security` *(kiểm tra cả MAC)*.

### Xử lý IP tĩnh — ARP ACL

Máy có **IP tĩnh** không qua DHCP → **không có trong binding table** → DAI chặn.

```cisco
! Khai báo thủ công cho server IP tĩnh
SW1(config)# arp access-list SERVER-TINH
SW1(config-arp-nacl)# permit ip host 10.0.50.20 mac host 001a.2b3c.4d5e
SW1(config)# ip arp inspection filter SERVER-TINH vlan 50

! Hoặc thêm binding tĩnh
SW1(config)# ip source binding 001a.2b3c.4d5e vlan 10 10.0.10.20 interface Fa0/8
```

> ⚠️ **Đây là việc bắt buộc phải làm trước** khi bật DAI. Liệt kê mọi thiết bị
> dùng IP tĩnh: server, máy in, camera, AP, UPS — và khai báo hết.

---

## 4. Why?

> **Vì sao không chỉ dùng Port Security là đủ?**

| Tính năng | Chống được gì |
|---|---|
| **Port Security** *(Lesson 17)* | Giới hạn **số MAC** / MAC cụ thể trên port |
| **DHCP Snooping** | Rogue DHCP server |
| **DAI** | ARP spoofing |
| **IPSG** | IP spoofing |

Port Security **không** chặn được rogue DHCP (vì nó chỉ nhìn MAC, không nhìn nội dung gói),
cũng **không** chặn được ARP spoofing (MAC hợp lệ nhưng nội dung ARP giả).

> ⭐ Bốn tính năng này **bổ sung cho nhau**, không thay thế nhau.
> Bộ đầy đủ cho access port:
> ```
> Port Security + DHCP Snooping + DAI + IPSG + BPDU Guard
> ```

> **Vì sao không dùng firewall thay thế?**

Vì cả rogue DHCP và ARP spoofing xảy ra **trong cùng một VLAN** — traffic
**không đi qua router/firewall**. Chỉ có **switch** mới chặn được.

> 🔑 Đây là bài học quan trọng: **bảo mật L2 phải làm ở L2.**
> Firewall ở biên không nhìn thấy gì xảy ra bên trong một broadcast domain.

---

## 5. How does it work? — thứ tự triển khai an toàn

```text
GIAI ĐOẠN 1 — Chuẩn bị (không gián đoạn)
  1. Liệt kê MỌI thiết bị dùng IP tĩnh trong VLAN
  2. Xác định port nào là uplink, port nào nối DHCP server

GIAI ĐOẠN 2 — DHCP Snooping
  3. Bật snooping toàn cục + cho VLAN cụ thể
  4. Khai TRUST cho uplink và port DHCP server    ← QUAN TRỌNG NHẤT
  5. Tắt Option 82 (hoặc cấu hình server chấp nhận)
  6. CHỜ 1–2 NGÀY cho binding table đầy đủ
     (mọi client gia hạn lease sẽ được ghi vào bảng)

GIAI ĐOẠN 3 — DAI
  7. Thêm binding tĩnh / ARP ACL cho các IP tĩnh đã liệt kê
  8. Khai TRUST cho uplink
  9. Bật DAI cho VLAN
 10. Theo dõi log — nếu có drop bất thường, bổ sung binding

GIAI ĐOẠN 4 — IPSG (tuỳ chọn)
 11. Bật trên từng port người dùng
```

> ⭐ **Bước 6 là bước hay bị bỏ qua nhất.** Bật DAI ngay sau khi bật snooping →
> binding table còn rỗng → **mọi ARP bị drop** → cả VLAN mất mạng ngay lập tức.

---

## 6. Packet Flow — DAI chặn ARP spoofing

```text
Kẻ tấn công (MAC-X, port Fa0/9) gửi ARP Reply giả:
  "10.0.10.1 (gateway) is at MAC-X"

DAI trên Fa0/9 (untrust):
  1. Trích: Sender IP = 10.0.10.1, Sender MAC = MAC-X
  2. Tra binding table:
       Fa0/9 có binding nào không?
       → có: (MAC-X, 10.0.10.57, VLAN 10, Fa0/9)
  3. SO SÁNH: gói khai 10.0.10.1 nhưng binding nói 10.0.10.57
  4. KHÔNG KHỚP → DROP ❌
  5. Log: %SW_DAI-4-DHCP_SNOOPING_DENY
```

> 🔑 DAI không cần biết "ai là gateway" — nó chỉ cần biết
> **"port này được phép khai IP nào"**. Đơn giản và hiệu quả.

---

## 7. Real-world Example

🏭 **Cấu hình chuẩn cho switch access**

```cisco
! ───── DHCP Snooping ─────
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 10,20,90
SW1(config)# no ip dhcp snooping information option     ! tránh lỗi Option 82

SW1(config)# interface GigabitEthernet1/0/48
SW1(config-if)# description UPLINK-TO-DIST
SW1(config-if)# ip dhcp snooping trust                   ! ⭐ BẮT BUỘC
SW1(config-if)# ip arp inspection trust

! ───── DAI ─────
SW1(config)# ip arp inspection vlan 10,20,90
SW1(config)# ip arp inspection validate src-mac dst-mac ip

! ───── Port người dùng: bộ đầy đủ ─────
SW1(config)# interface range GigabitEthernet1/0/1 - 44
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 10
SW1(config-if-range)# switchport port-security
SW1(config-if-range)# switchport port-security maximum 2
SW1(config-if-range)# switchport port-security violation restrict
SW1(config-if-range)# ip verify source                   ! IPSG
SW1(config-if-range)# spanning-tree portfast
SW1(config-if-range)# spanning-tree bpduguard enable
SW1(config-if-range)# ip dhcp snooping limit rate 15      ! chống DHCP starvation

! ───── Khôi phục tự động ─────
SW1(config)# errdisable recovery cause dhcp-rate-limit
SW1(config)# errdisable recovery cause arp-inspection
SW1(config)# errdisable recovery interval 300
```

> 🔑 `ip dhcp snooping limit rate 15` chống **DHCP starvation attack** — kẻ tấn công
> gửi hàng nghìn Discover với MAC giả để **vét cạn pool DHCP**. Giới hạn 15 gói/giây
> trên port người dùng là quá đủ.

🏭 **Sự cố: bật DAI xong cả VLAN mất mạng**

| Nguyên nhân | Dấu hiệu | Cách sửa |
|---|---|---|
| **Binding table rỗng** *(bật DAI ngay sau snooping)* | Mọi ARP bị drop | Tắt DAI, chờ 1–2 ngày, bật lại |
| **Quên trust uplink** | Switch access không ai có IP | `ip dhcp snooping trust` trên uplink |
| **Thiết bị IP tĩnh không khai báo** | Chỉ server/máy in mất mạng | Thêm `ip source binding` hoặc ARP ACL |
| **Option 82** | Client không nhận được IP | `no ip dhcp snooping information option` |

🏭 **Hypervisor và DAI — tình huống khó**

Server ảo hoá có **nhiều VM, nhiều MAC, nhiều IP tĩnh** đi qua một port vật lý.
DAI sẽ chặn hết vì không có binding.

| Giải pháp | Đánh đổi |
|---|---|
| Đặt port hypervisor thành **`ip arp inspection trust`** | Đơn giản, nhưng mất bảo vệ ở port đó |
| Khai `ip source binding` cho **từng VM** | An toàn, nhưng phải cập nhật mỗi khi tạo VM mới |
| **Không bật DAI** cho VLAN server | Chấp nhận — VLAN server thường ít rủi ro hơn VLAN user |

> 🔧 Thực tế: nhiều nơi bật DAI **chỉ cho VLAN người dùng**, không bật cho VLAN server.
> Đó là đánh đổi hợp lý giữa bảo mật và vận hành.

---

## 8. Cisco CLI

```cisco
! ═══════ DHCP SNOOPING ═══════
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 10,20,90
SW1(config)# no ip dhcp snooping information option
SW1(config)# ip dhcp snooping database flash:dhcp-snooping.db   ! lưu bảng qua reboot

SW1(config)# interface GigabitEthernet1/0/48
SW1(config-if)# ip dhcp snooping trust

SW1(config)# interface range GigabitEthernet1/0/1 - 44
SW1(config-if-range)# ip dhcp snooping limit rate 15

! Binding tĩnh cho thiết bị IP tĩnh
SW1(config)# ip source binding 001a.2b3c.4d5e vlan 10 10.0.10.20 interface Gi1/0/8

! ═══════ DYNAMIC ARP INSPECTION ═══════
SW1(config)# ip arp inspection vlan 10,20,90
SW1(config)# ip arp inspection validate src-mac dst-mac ip
SW1(config-if)# ip arp inspection trust                  ! trên uplink
SW1(config-if)# ip arp inspection limit rate 20

! ARP ACL cho IP tĩnh
SW1(config)# arp access-list SERVER-TINH
SW1(config-arp-nacl)# permit ip host 10.0.50.20 mac host 001a.2b3c.4d5e
SW1(config)# ip arp inspection filter SERVER-TINH vlan 50

! ═══════ IP SOURCE GUARD ═══════
SW1(config-if)# ip verify source                         ! chỉ kiểm IP
SW1(config-if)# ip verify source port-security            ! kiểm cả IP và MAC

! ═══════ KIỂM TRA ═══════
SW1# show ip dhcp snooping
SW1# show ip dhcp snooping binding
SW1# show ip dhcp snooping statistics
SW1# show ip arp inspection
SW1# show ip arp inspection statistics vlan 10
SW1# show ip verify source
SW1# show errdisable recovery
```

| Lệnh | Lưu ý |
|---|---|
| `ip dhcp snooping` | Bật toàn cục — **phải có cả lệnh cho VLAN** mới chạy |
| `ip dhcp snooping trust` | ⭐ **Uplink và port DHCP server** |
| `no ip dhcp snooping information option` | ⭐ Tránh lỗi Option 82 |
| `ip dhcp snooping database flash:...` | Giữ binding table qua reboot |
| `ip arp inspection validate src-mac dst-mac ip` | Kiểm tra chặt hơn |
| `ip verify source port-security` | IPSG kiểm cả MAC — mạnh hơn |
| `ip source binding ...` | Khai báo thủ công cho IP tĩnh |

> ⚠️ Không có `ip dhcp snooping database` → **reboot switch là mất sạch binding table**
> → DAI chặn hết cho tới khi client gia hạn lease. Luôn cấu hình database.

> **Khác biệt platform:** NX-OS cần `feature dhcp` và dùng `ip dhcp snooping` tương tự.
> Catalyst đời mới có thể lưu database lên server qua TFTP/FTP.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip dhcp snooping
Switch DHCP snooping is enabled
DHCP snooping is configured on following VLANs:
10,20,90
Insertion of option 82 is disabled
Interface                  Trusted    Rate limit (pps)
------------------------   -------    ----------------
GigabitEthernet1/0/1       no         15
GigabitEthernet1/0/48      yes        unlimited
```

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `DHCP snooping is enabled` | Bật toàn cục ✅ | |
| `configured on following VLANs` | VLAN nào được bảo vệ | Thiếu VLAN → không bảo vệ |
| `Insertion of option 82 is disabled` | Đã tắt ✅ | `enabled` → có thể gây lỗi |
| `Trusted: yes` ở uplink | ⭐ **Phải có** | `no` → cả switch không ai có IP |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip arp inspection statistics vlan 10
 Vlan      Forwarded        Dropped     DHCP Drops      ACL Drops
 ----      ---------        -------     ----------      ---------
   10          18422             14             14              0

 Vlan   DHCP Permits    ACL Permits   Source MAC Failures
 ----   ------------    -----------   -------------------
   10          18422              0                     0
```

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `Forwarded` | ARP hợp lệ đã cho qua | |
| **`Dropped`** | ARP bị chặn | **Tăng liên tục** → có ARP spoofing, hoặc thiếu binding |
| `DHCP Drops` | Drop vì không khớp binding table | Nguyên nhân phổ biến nhất |
| `Source MAC Failures` | MAC trong gói ARP ≠ MAC Ethernet | Dấu hiệu tấn công rõ ràng |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip verify source
Interface  Filter-type  Filter-mode  IP-address      Mac-address       Vlan
---------  -----------  -----------  --------------  ----------------  ----
Gi1/0/5    ip           active       10.0.10.57                        10
Gi1/0/6    ip-mac       active       10.0.10.58      001A.2B3C.4D6F    10
```

```text
# output điển hình — log khi phát hiện tấn công
%SW_DAI-4-DHCP_SNOOPING_DENY: 1 Invalid ARPs (Req) on Gi1/0/9, vlan 10.
   ([001a.2b3c.9999/10.0.10.1/0000.0000.0000/10.0.10.57/14:23:51 ICT])
%DHCP_SNOOPING-5-DHCP_SNOOPING_UNTRUSTED_PORT: DHCP_SNOOPING drop message on
   untrusted port, message type: DHCPOFFER, MAC sa: 001a.2b3c.8888
```

> 🔑 Dòng log thứ hai là **bằng chứng rogue DHCP** — có ai đó gửi `DHCPOFFER`
> từ một port untrust. Ghi lại MAC để truy ra thiết bị.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| **Bật snooping xong cả VLAN mất mạng** | Quên **trust uplink** | `show ip dhcp snooping` xem cột Trusted | `ip dhcp snooping trust` trên uplink |
| Client không nhận IP sau khi bật snooping | **Option 82** bị server từ chối | `show ip dhcp snooping` | `no ip dhcp snooping information option` |
| **Bật DAI xong mọi thứ chết** | **Binding table rỗng** | `show ip dhcp snooping binding` | Tắt DAI, chờ 1–2 ngày, bật lại |
| Chỉ server/máy in mất mạng | IP tĩnh **không có binding** | `show ip arp inspection statistics` | `ip source binding` hoặc ARP ACL |
| Sau reboot switch, DAI chặn hết | Binding table mất | `show ip dhcp snooping binding` trống | `ip dhcp snooping database flash:...` |
| `Dropped` của DAI tăng liên tục | Có ARP spoofing, hoặc thiếu binding | `show logging \| include DAI` | Xem MAC trong log, truy ra thiết bị |
| Port `err-disabled` lý do `arp-inspection` | Vượt rate limit | `show interfaces status err-disabled` | Tăng rate limit, hoặc xử lý nguồn |
| Hypervisor mất mạng | Nhiều VM, không có binding | `show ip verify source` | Trust port đó, hoặc khai binding từng VM |
| Có người cắm router Wi-Fi | Log `DHCP_SNOOPING_UNTRUSTED_PORT` | `show logging` | Truy MAC → tìm port → xử lý |

---

## 11. LAB

🧪 **LAB 62 — DHCP Snooping, DAI, IPSG** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- 1 switch, 1 router làm DHCP server, 3 PC — mọi PC nhận IP bình thường **trước khi** bật gì
- Thêm một router thứ hai làm **rogue DHCP** → chứng minh PC nhận IP sai
- Bật DHCP Snooping, trust đúng port → chứng minh rogue bị chặn, log xuất hiện
- Xem `show ip dhcp snooping binding` → bảng có đủ 3 PC
- Bật DAI → mọi thứ vẫn chạy; thử giả mạo ARP → bị chặn
- **BREAK bắt buộc:** (1) **quên trust uplink** → cả VLAN mất mạng;
  (2) bật DAI khi binding table rỗng → quan sát mọi ARP bị drop;
  (3) đặt một PC dùng IP tĩnh → quan sát DAI chặn nó, rồi sửa bằng `ip source binding`

## 12. Challenge

1. Bạn bật DHCP Snooping trên switch access. Ngay lập tức **không ai nhận được IP**.
   Nêu 2 nguyên nhân theo thứ tự khả năng.
2. Vì sao DAI không hoạt động nếu chưa có DHCP Snooping?
3. Server IP tĩnh `10.0.50.20` MAC `001a.2b3c.4d5e` ở `Gi1/0/8` VLAN 50.
   Viết **2 cách** cho phép nó qua DAI.
4. Port Security đã bật rồi, vẫn cần DHCP Snooping và DAI không? Vì sao?

<details>
<summary>Đáp án</summary>

**1.** Theo thứ tự khả năng:

| # | Nguyên nhân | Kiểm chứng | Sửa |
|:---:|---|---|---|
| **1** | **Quên trust uplink** — DHCP reply từ server đi xuống qua uplink bị drop | `show ip dhcp snooping` xem cột `Trusted` của uplink | `ip dhcp snooping trust` |
| **2** | **Option 82** — switch chèn Option 82 nhưng `giaddr = 0.0.0.0`, server từ chối | `show ip dhcp snooping` thấy `Insertion of option 82 is enabled` | `no ip dhcp snooping information option` |

Nguyên nhân 1 phổ biến hơn nhiều.

**2.** Vì **DAI kiểm tra gói ARP bằng cách đối chiếu với binding table**, mà
binding table **do DHCP Snooping tạo ra**.

Không có snooping → bảng rỗng → **mọi** gói ARP đều "không khớp" → DAI drop hết →
không ai phân giải được IP→MAC → **cả VLAN mất mạng**.

Đây là lý do thứ tự triển khai bắt buộc: **snooping trước, chờ bảng đầy, rồi mới DAI**.

**3.** Hai cách:

```cisco
! Cách 1 — thêm binding tĩnh vào bảng
SW1(config)# ip source binding 001a.2b3c.4d5e vlan 50 10.0.50.20 interface Gi1/0/8
```

```cisco
! Cách 2 — ARP ACL
SW1(config)# arp access-list SERVER-TINH
SW1(config-arp-nacl)# permit ip host 10.0.50.20 mac host 001a.2b3c.4d5e
SW1(config)# ip arp inspection filter SERVER-TINH vlan 50
```

| | Cách 1 *(binding)* | Cách 2 *(ARP ACL)* |
|---|---|---|
| Ưu | Đơn giản, dùng chung bảng với IPSG | Gom nhiều host vào một ACL, dễ quản lý |
| Nhược | Mỗi host một dòng | Không dùng được cho IPSG |

**4.** **Vẫn cần**, vì chúng chống những thứ **khác nhau**:

| Tính năng | Chống | Port Security có chặn được không? |
|---|---|:---:|
| Port Security | Nhiều MAC trên một port, MAC lạ | — |
| **DHCP Snooping** | **Rogue DHCP server** | ❌ **Không** — MAC của rogue là hợp lệ, Port Security không nhìn nội dung gói |
| **DAI** | **ARP spoofing** | ❌ **Không** — kẻ tấn công dùng đúng MAC của mình, chỉ nội dung ARP là giả |
| **IPSG** | **IP spoofing** | ❌ **Không** — Port Security chỉ nhìn MAC, không nhìn IP |

Port Security hoạt động ở tầng **địa chỉ MAC**; ba tính năng kia hoạt động ở tầng
**nội dung gói**. Chúng bổ sung cho nhau.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 tính năng chống gì · trust port đặt ở đâu · binding table chứa gì | ⬜ |
| **L2** Explain | Giải thích vì sao DAI phụ thuộc DHCP Snooping | ⬜ |
| **L3** Configure | Cấu hình đủ bộ cho switch access, đúng thứ tự | ⬜ |
| **L4** Troubleshoot | "Bật snooping xong mất mạng" → tìm nguyên nhân | ⬜ |
| **L5** Design | Lập kế hoạch triển khai cho 10 switch access đang chạy production | ⬜ |

## 14. Summary

**Key concepts**

- **DHCP Snooping** chống **rogue DHCP** — chỉ port `trust` được gửi DHCP reply
- ⭐ **Binding table** `(MAC, IP, VLAN, port)` là **nền tảng** của DAI và IPSG
- **DAI** chống **ARP spoofing** — đối chiếu gói ARP với binding table
- **IPSG** chống **IP spoofing** — đối chiếu source IP với binding table
- ⭐ **Thứ tự bắt buộc: Snooping → chờ bảng đầy (1–2 ngày) → DAI → IPSG**
- ⭐ **Trust port**: uplink + port nối DHCP server. Quên trust uplink = mất mạng cả switch
- ⚠️ **Option 82** gây lỗi với nhiều server → `no ip dhcp snooping information option`
- IP tĩnh phải khai `ip source binding` hoặc **ARP ACL** trước khi bật DAI
- `ip dhcp snooping database` để giữ bảng qua reboot
- `limit rate` chống **DHCP starvation**
- ⭐ **Bảo mật L2 phải làm ở L2** — firewall ở biên không thấy gì trong một VLAN
- Bộ đầy đủ cho access port: **Port Security + DHCP Snooping + DAI + IPSG + BPDU Guard**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip dhcp snooping` + `ip dhcp snooping vlan N` | Bật snooping |
| `ip dhcp snooping trust` | ⭐ **Uplink và port DHCP server** |
| `no ip dhcp snooping information option` | ⭐ Tránh lỗi Option 82 |
| `ip dhcp snooping database flash:...` | Giữ bảng qua reboot |
| `ip arp inspection vlan N` | Bật DAI |
| `ip source binding <mac> vlan N <ip> interface X` | Khai IP tĩnh |
| `ip verify source port-security` | IPSG kiểm cả IP và MAC |
| `show ip dhcp snooping binding` | ⭐ Bảng binding — nguồn sự thật |
| `show ip arp inspection statistics vlan N` | Bao nhiêu ARP bị drop |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên trust uplink | **Cả switch không ai nhận được IP** |
| Bật DAI ngay sau snooping | Binding rỗng → **mọi ARP bị drop** |
| Không khai IP tĩnh trước khi bật DAI | Server, máy in, camera mất mạng |
| Để Option 82 bật | Client không nhận được IP |
| Không cấu hình snooping database | Reboot là mất bảng, DAI chặn hết |
| Bật DAI cho VLAN có hypervisor | Nhiều VM không có binding → bị chặn |
| Nghĩ Port Security là đủ | Không chặn được rogue DHCP hay ARP spoofing |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 62 với đủ 3 lỗi BREAK — đặc biệt lỗi 2 *(bật DAI khi bảng rỗng)*,
   nó cho bạn thấy đúng cảm giác "mạng chết trong 1 giây".
2. Viết **kế hoạch 4 giai đoạn** triển khai cho một switch access đang chạy production,
   lưu vào `06-security/ke-hoach-trien-khai-l2-security.md`.
3. Liệt kê mọi thiết bị dùng IP tĩnh trong một VLAN ở công ty bạn — đây chính là
   danh sách bạn cần trước khi bật DAI.

```markdown
- [YYYY-MM-DD] Lesson 37 — DHCP Snooping, DAI, IPSG: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 3 tính năng chống gì, trust port, binding table, thứ tự phụ thuộc |
| 🔧 **Engineer** | Trust uplink; tắt Option 82; snooping database; khai IP tĩnh trước |
| 🏭 **Production** | Thứ tự triển khai 4 giai đoạn; chờ bảng đầy trước khi bật DAI; hypervisor là ngoại lệ |

### 🔗 Liên kết

- ⬅️ [Lesson 36 — ACL](./lesson-36-acl.md)
- ➡️ [Lesson 38 — L2 attacks](./lesson-38-l2-attacks.md)
- 📚 ARP spoofing: [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md)
- 📚 Rogue DHCP: [Lesson 25](../03-services/lesson-25-dhcp-trien-khai.md)
