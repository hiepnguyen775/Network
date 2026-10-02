# LESSON 36 — Access Control List (ACL) ⭐

> 📌 Lesson được dùng nhiều nhất trong đời thực. Mọi câu hỏi *"chặn được cái này không?"*
> đều quy về ACL.

| | |
|---|---|
| **Phase** | 6 — Security |
| **Thời lượng** | ~4 giờ |
| **Prerequisite** | [Lesson 02](../00-foundation/lesson-02-ipv4-va-subnetting.md), [Lesson 06](../00-foundation/lesson-06-tcp-udp-port.md), [Lesson 27](../03-services/lesson-27-nat-nang-cao.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Viết **wildcard mask** không cần nghĩ
- [ ] Phân biệt **standard** và **extended** ACL — và biết đặt ở đâu
- [ ] Giải thích **implicit deny** và thứ tự xử lý dòng
- [ ] Đặt ACL đúng **interface và hướng** — và nói được vì sao
- [ ] Debug ACL bằng counter, không đoán mò

## 2. Prerequisite

- Wildcard mask *(Lesson 02, Lesson 07)*
- Port và protocol number *(Lesson 06)*
- Thứ tự NAT/routing/ACL *(Lesson 27)*

---

## 3. Concept

### Ba quy tắc bất biến

```text
1. Xử lý TỪ TRÊN XUỐNG, DỪNG ở dòng khớp đầu tiên
2. Cuối ACL luôn có IMPLICIT DENY ANY (ẩn, không hiện trong show run)
3. Một interface — một hướng — một ACL (cho mỗi protocol)
```

> ⭐ Quy tắc 1 nghĩa là **thứ tự dòng quyết định tất cả**. Đặt `permit ip any any`
> ở dòng đầu → mọi dòng sau vô nghĩa.

> ⭐ Quy tắc 2 nghĩa là **ACL chỉ có `deny` thì chặn hết**. Phải có ít nhất một `permit`.

### Standard vs Extended

| | **Standard** | **Extended** |
|---|---|---|
| Số hiệu | **1–99**, 1300–1999 | **100–199**, 2000–2699 |
| Lọc theo | **CHỈ source IP** | Source + **dest** + protocol + **port** |
| Đặt ở đâu | **GẦN ĐÍCH** | **GẦN NGUỒN** |
| Dùng khi | Hạn chế truy cập quản trị, lọc route | ⭐ Hầu hết trường hợp thực tế |

> 🔑 **Vì sao standard đặt gần đích:** nó chỉ biết source IP, không biết đích.
> Đặt gần nguồn sẽ chặn luôn mọi đường đi của host đó, kể cả đường bạn muốn cho phép.
>
> **Vì sao extended đặt gần nguồn:** nó biết chính xác source + dest + port,
> nên chặn sớm **tiết kiệm băng thông** — không chở gói đi khắp mạng rồi mới vứt.

### Wildcard mask — ôn nhanh

**Wildcard = nghịch đảo subnet mask.** `0` = phải khớp, `1` = bỏ qua.

| Muốn khớp | Wildcard | Viết tắt |
|---|---|---|
| Một host `10.0.1.5` | `0.0.0.0` | **`host 10.0.1.5`** |
| Cả subnet `/24` | `0.0.0.255` | — |
| Cả subnet `/25` | `0.0.0.127` | — |
| Cả subnet `/26` | `0.0.0.63` | — |
| Cả subnet `/30` | `0.0.0.3` | — |
| Cả `/16` | `0.0.255.255` | — |
| **Mọi địa chỉ** | `255.255.255.255` | **`any`** |

```cisco
access-list 10 permit 10.0.1.5 0.0.0.0        ≡  permit host 10.0.1.5
access-list 10 permit 0.0.0.0 255.255.255.255 ≡  permit any
```

> ⚠️ **Nhầm wildcard với subnet mask là lỗi số 1 ở lesson này.** IOS **nhận lệnh
> bình thường** nhưng ACL khớp sai hoàn toàn, và không có thông báo nào.

### Cú pháp Extended ACL

```cisco
access-list <100-199> {permit|deny} <protocol> <src> <wildcard> [eq port]
                                                <dst> <wildcard> [eq port] [log]
```

| Toán tử port | Nghĩa |
|---|---|
| `eq 443` | Bằng |
| `neq 23` | Khác |
| `gt 1023` | Lớn hơn |
| `lt 1024` | Nhỏ hơn |
| `range 1024 65535` | Trong khoảng |

```cisco
! Cho HTTPS từ bất kỳ đâu tới web server
access-list 110 permit tcp any host 10.0.50.20 eq 443

! Cho VLAN 10 ra Internet, chặn vào VLAN 50
access-list 110 deny   ip 10.0.10.0 0.0.0.255 10.0.50.0 0.0.0.255
access-list 110 permit ip 10.0.10.0 0.0.0.255 any

! Cho DNS (cả TCP và UDP)
access-list 110 permit udp any host 10.0.50.10 eq 53
access-list 110 permit tcp any host 10.0.50.10 eq 53
```

### Named ACL — nên dùng

```cisco
ip access-list extended CHAN-GUEST
 remark Chan guest vao mang noi bo
 deny   ip 10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255
 permit ip 10.0.90.0 0.0.0.255 any
```

| Named ACL hơn ở đâu |
|---|
| **Tên có nghĩa** — `CHAN-GUEST` dễ đọc hơn `110` |
| **Sửa được từng dòng** *(thêm số thứ tự)* |
| **`remark`** để ghi chú |
| Không giới hạn số lượng |

```cisco
! Sửa một dòng cụ thể
ip access-list extended CHAN-GUEST
 no 20                               ! xoá dòng 20
 15 permit tcp any host 10.0.50.20 eq 443   ! chèn dòng mới ở vị trí 15
```

### Đặt ở đâu, hướng nào

```text
         ┌──────── R1 ────────┐
  LAN ──▶│ Gi0/0        Gi0/1 │──▶ WAN
         │  in ──▶  ◀── out   │
         └────────────────────┘

in  = gói ĐI VÀO interface  (từ dây vào router)
out = gói ĐI RA interface   (từ router ra dây)
```

| Muốn chặn | Đặt ở đâu |
|---|---|
| LAN → WAN | `Gi0/0 in` *(sớm nhất)* hoặc `Gi0/1 out` |
| WAN → LAN | `Gi0/1 in` *(sớm nhất)* |
| VLAN 10 → VLAN 50 | SVI VLAN 10 `in` |

> 🔑 **Nguyên tắc: đặt càng sớm càng tốt** — chặn ngay khi gói vào router,
> tiết kiệm CPU và băng thông.

> ⚠️ Nhớ từ [Lesson 27](../03-services/lesson-27-nat-nang-cao.md): với gói **đi vào**
> từ WAN, ACL inbound chạy **trước NAT** → phải khớp **IP public**, không phải IP private.

### Established — mẹo quan trọng

```cisco
! Cho LAN ra Internet, nhưng Internet KHÔNG chủ động vào được
access-list 110 permit tcp any 10.0.0.0 0.0.255.255 established
access-list 110 deny   ip any any
```

`established` khớp gói TCP có cờ **ACK** hoặc **RST** — tức là gói **trả lời** cho
một kết nối đã mở, không phải gói `SYN` mở kết nối mới.

> 💡 Đây là cách làm "stateless firewall" thô sơ. Firewall thật dùng
> **stateful inspection** (theo dõi bảng kết nối), chính xác hơn nhiều.
> Nhưng `established` đủ dùng cho nhiều tình huống đơn giản.

---

## 4. Why?

> **Vì sao implicit deny tồn tại?**

Nguyên tắc bảo mật: **"default deny"** — mặc định cấm, chỉ cho phép thứ bạn
**chủ động cho phép**. An toàn hơn "default permit" vì:

- Quên một dòng `deny` → lỗ hổng *(default permit)*
- Quên một dòng `permit` → dịch vụ không chạy, bạn phát hiện ngay *(default deny)*

> ⭐ **Lỗi an toàn hơn lỗ hổng.** Thà service không chạy còn hơn mở cửa cho kẻ xấu.

> **Vì sao ACL không thay được firewall?**

| | **ACL trên router** | **Firewall** |
|---|---|---|
| Theo dõi trạng thái kết nối | ❌ *(trừ `established` thô sơ)* | ✅ **Stateful** |
| Kiểm tra nội dung (L7) | ❌ | ✅ |
| Phát hiện xâm nhập | ❌ | ✅ IPS |
| Log chi tiết, báo cáo | ⚠️ Hạn chế | ✅ |
| Hiệu năng | ✅ Rất nhanh *(TCAM)* | Chậm hơn |

> 🔧 ACL là **lớp lọc thô, nhanh, gần hạ tầng**. Firewall là **lớp kiểm soát sâu**.
> Thiết kế tốt dùng **cả hai**: ACL ở distribution/core lọc theo IP/port,
> firewall ở biên kiểm tra sâu.

---

## 5. How does it work? — thứ tự xử lý

```text
Gói tới interface Gi0/0, hướng IN

1. Lấy dòng ACL đầu tiên
2. Gói có khớp dòng này không?
   ├─ KHỚP + permit → CHO QUA, dừng xử lý ACL
   ├─ KHỚP + deny   → VỨT BỎ, dừng xử lý ACL
   └─ KHÔNG khớp    → sang dòng tiếp theo
3. Hết dòng mà chưa khớp → IMPLICIT DENY → VỨT BỎ
```

### Ví dụ thứ tự sai

```cisco
! ❌ SAI — dòng 1 cho qua hết, dòng 2 không bao giờ chạy
access-list 110 permit ip any any
access-list 110 deny   ip 10.0.90.0 0.0.0.255 10.0.50.0 0.0.0.255

! ✅ ĐÚNG — deny cụ thể trước, permit chung sau
access-list 110 deny   ip 10.0.90.0 0.0.0.255 10.0.50.0 0.0.0.255
access-list 110 permit ip any any
```

> 🔑 **Quy tắc viết ACL: cụ thể trước, chung sau.**
> Dòng `deny` hẹp đứng trên, dòng `permit` rộng đứng dưới.

---

## 6. Packet Flow — ACL ở đâu trong luồng xử lý

```text
Gói ĐI VÀO router:
  1. ACL inbound trên interface nhận     ← lọc sớm nhất
  2. Giải mã VPN
  3. NAT (outside→inside)
  4. ROUTING
  5. ACL outbound trên interface gửi
  6. Gửi đi
```

> ⚠️ Hai hệ quả thực tế:
> 1. **ACL inbound trên WAN thấy IP public** *(trước NAT)*
> 2. ACL inbound chặn gói **trước cả routing** → tiết kiệm CPU nhất

---

## 7. Real-world Example

🏭 **ACL cô lập VLAN guest — tình huống phổ biến nhất**

```cisco
ip access-list extended GUEST-ISOLATE
 remark Guest chi duoc ra Internet, cam vao noi bo
 permit udp 10.0.90.0 0.0.0.255 host 10.0.50.10 eq 53    ! cho DNS nội bộ
 deny   ip  10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255     ! cấm mọi dải nội bộ
 permit ip  10.0.90.0 0.0.0.255 any                       ! còn lại ra Internet
!
interface vlan 90
 ip access-group GUEST-ISOLATE in
```

> 🔑 Dòng `permit DNS` phải đứng **trước** dòng `deny` — vì DNS server nằm trong dải
> nội bộ bị cấm. Đây là ví dụ rõ nhất của quy tắc "cụ thể trước, chung sau".

🏭 **Bảo vệ thiết bị mạng — chỉ IT được SSH**

```cisco
ip access-list standard CHI-IT
 permit 10.0.30.0 0.0.0.255
 deny   any log
!
line vty 0 15
 access-class CHI-IT in
 transport input ssh
```

> 🔧 Dùng `access-class` cho **line vty**, không phải `ip access-group`.
> Đây là cách bảo vệ **management plane** — khác với bảo vệ traffic đi qua.

🏭 **ACL cho WAN interface — bảo vệ biên**

```cisco
ip access-list extended TU-INTERNET
 remark Chi cho phep ket noi can thiet tu Internet
 permit tcp any host 203.0.113.5 eq 443          ! web server (IP PUBLIC!)
 permit tcp any host 203.0.113.6 eq 25           ! mail server
 permit icmp any any echo-reply                   ! cho ping ra ngoài có reply
 permit icmp any any packet-too-big               ! ⭐ PMTUD — đừng chặn!
 permit icmp any any time-exceeded                ! traceroute hoạt động
 deny   ip 10.0.0.0 0.255.255.255 any log         ! chống giả mạo IP private
 deny   ip 172.16.0.0 0.15.255.255 any log
 deny   ip 192.168.0.0 0.0.255.255 any log
 deny   ip any any log
!
interface GigabitEthernet0/1
 ip access-group TU-INTERNET in
```

> ⚠️ Ba dòng `deny` dải private ở cuối chống **IP spoofing** — gói từ Internet
> mà có source là IP private thì chắc chắn là giả mạo.

> ⚠️ **`permit icmp any any packet-too-big` rất quan trọng** — chặn nó làm hỏng
> **PMTUD**, gây triệu chứng "web có ảnh lớn thì treo" *(đã gặp ở Lesson 30)*.

🏭 **Sự cố kinh điển: tự khoá mình ra ngoài**

```text
1. Kỹ sư áp ACL lên interface WAN để chặn truy cập trái phép
2. ACL không có dòng permit cho IP của chính kỹ sư
3. Gõ Enter → mất SSH ngay lập tức
4. Phải chạy tới chỗ cắm console
```

**Phòng ngừa:**

| Cách | Chi tiết |
|---|---|
| **Luôn permit IP quản trị ở dòng đầu** | `permit ip host <ip-cua-ban> any` |
| Dùng **`reload in 10`** | Nếu không `reload cancel` trong 10 phút, thiết bị tự khởi động lại về config cũ |
| Thử trên **một thiết bị** trước | Đừng đẩy đồng loạt |

```cisco
R1# reload in 10                    ! hẹn reload sau 10 phút
R1(config)# ip access-group ...     ! áp ACL
! ...kiểm tra, nếu OK:
R1# reload cancel                   ! huỷ hẹn
```

---

## 8. Cisco CLI

```cisco
! ═══════ STANDARD ACL (numbered) ═══════
R1(config)# access-list 10 permit 10.0.30.0 0.0.0.255
R1(config)# access-list 10 deny   any log

! ═══════ EXTENDED ACL (numbered) ═══════
R1(config)# access-list 110 permit tcp any host 10.0.50.20 eq 443
R1(config)# access-list 110 deny   ip any any log

! ═══════ NAMED ACL — NÊN DÙNG ═══════
R1(config)# ip access-list extended TU-INTERNET
R1(config-ext-nacl)# remark Bao ve bien mang
R1(config-ext-nacl)# permit tcp any host 203.0.113.5 eq 443
R1(config-ext-nacl)# permit icmp any any packet-too-big
R1(config-ext-nacl)# deny ip any any log

! Sửa từng dòng
R1(config-ext-nacl)# no 20                                    ! xoá dòng 20
R1(config-ext-nacl)# 15 permit tcp any host 10.0.50.21 eq 80  ! chèn ở vị trí 15
R1(config-ext-nacl)# resequence 10 10                         ! đánh số lại 10,20,30...

! ═══════ ÁP VÀO INTERFACE ═══════
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip access-group TU-INTERNET in

! ═══════ BẢO VỆ LINE VTY ═══════
R1(config)# line vty 0 15
R1(config-line)# access-class CHI-IT in

! ═══════ TIME-BASED ACL ═══════
R1(config)# time-range GIO-HANH-CHINH
R1(config-time-range)# periodic weekdays 8:00 to 17:30
R1(config)# ip access-list extended CHAN-NGOAI-GIO
R1(config-ext-nacl)# permit ip 10.0.10.0 0.0.0.255 any time-range GIO-HANH-CHINH

! ═══════ ACL IPv6 ═══════
R1(config)# ipv6 access-list V6-WAN-IN
R1(config-ipv6-acl)# permit icmp any any nd-ns
R1(config-ipv6-acl)# permit icmp any any nd-na
R1(config-ipv6-acl)# permit icmp any any packet-too-big
R1(config-ipv6-acl)# deny ipv6 any any log
R1(config-if)# ipv6 traffic-filter V6-WAN-IN in

! ═══════ KIỂM TRA ═══════
R1# show access-lists
R1# show access-lists TU-INTERNET
R1# show ip interface GigabitEthernet0/1 | include access list
R1# clear access-list counters
R1# show ipv6 access-list
```

| Lệnh | Lưu ý |
|---|---|
| `ip access-group <acl> in\|out` | Áp ACL IPv4 lên interface |
| `access-class <acl> in` | ⚠️ Cho **line vty**, không phải `ip access-group` |
| `ipv6 traffic-filter <acl> in` | ⚠️ ACL IPv6 dùng lệnh **khác** |
| `log` cuối dòng | Ghi log khi khớp — ⚠️ tốn CPU, dùng có chủ đích |
| `resequence 10 10` | Đánh số lại để chèn dòng mới dễ hơn |
| `clear access-list counters` | Reset counter trước khi test |

> **Khác biệt platform:** NX-OS dùng `ip access-list <name>` (không có `extended`),
> và áp bằng `ip access-group <name> in`. ASA firewall dùng mô hình
> `access-list ... extended permit ...` + `access-group ... in interface <name>`.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show access-lists TU-INTERNET
Extended IP access list TU-INTERNET
    10 permit tcp any host 203.0.113.5 eq 443 (18422 matches)
    20 permit tcp any host 203.0.113.6 eq smtp (342 matches)
    30 permit icmp any any echo-reply (89 matches)
    40 permit icmp any any packet-too-big (12 matches)
    50 deny ip 10.0.0.0 0.255.255.255 any log (7 matches)
    60 deny ip any any log (1843 matches)
```

**Đọc gì — đây là kỹ năng debug ACL quan trọng nhất:**

| Dấu hiệu | Ý nghĩa |
|---|---|
| **`(N matches)` tăng** | Dòng đó **đang khớp** — ACL hoạt động |
| **`(0 matches)`** ở dòng permit | ⚠️ Traffic **không bao giờ tới dòng này** — hoặc bị dòng trên bắt, hoặc ACL đặt sai chỗ |
| `deny ip any any log` có nhiều matches | Nhiều gói bị chặn — xem log để biết là gì |
| Dòng `deny` private có matches | **Có IP spoofing** — đáng điều tra |

> 🔑 **Counter là công cụ debug ACL mạnh nhất.** Quy trình:
> `clear access-list counters` → tạo traffic test → `show access-lists` →
> xem dòng nào khớp.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip interface GigabitEthernet0/1 | include access list
  Outgoing access list is not set
  Inbound  access list is TU-INTERNET
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show logging | include ACCESSLOG
%SEC-6-IPACCESSLOGP: list TU-INTERNET denied tcp 198.51.100.7(51234) -> 203.0.113.5(22), 1 packet
```

> 🔧 Log ACL cho biết **chính xác gói nào bị chặn** — IP, port, protocol.
> Nhưng `log` tốn CPU; chỉ bật trên dòng cần điều tra, không bật mọi dòng.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| ACL không có tác dụng gì | Chưa áp vào interface | `show ip interface <int> \| include access` | `ip access-group` |
| ACL chặn hết mọi thứ | Thiếu dòng `permit`, chỉ còn implicit deny | `show access-lists` | Thêm `permit` phù hợp |
| Dòng permit `(0 matches)` | Dòng trên đã bắt hết, hoặc sai hướng/interface | `show access-lists` | Đổi thứ tự, hoặc đổi chỗ áp |
| ACL trên WAN không khớp | ⭐ Khớp **IP private** thay vì public | `show access-lists` counter = 0 | Đổi sang **IP public** |
| Mất SSH ngay sau khi áp ACL | **Tự khoá mình** | Console vào | Thêm `permit` cho IP quản trị |
| Web có ảnh lớn bị treo | Chặn **`packet-too-big`** | `show access-lists` | Permit ICMP packet-too-big |
| Chặn được TCP nhưng UDP vẫn qua | Chỉ viết `permit tcp`, quên UDP | `show access-lists` | Thêm dòng cho UDP |
| DNS không chạy | Chỉ permit UDP/53, thiếu TCP/53 | `show access-lists` | Thêm `permit tcp ... eq 53` |
| CPU router tăng cao sau khi áp ACL | Quá nhiều dòng có `log` | `show processes cpu sorted` | Bỏ bớt `log` |
| ACL IPv6 không có tác dụng | Dùng nhầm `ip access-group` | `show run interface <int>` | `ipv6 traffic-filter` |

---

## 11. LAB

🧪 **LAB 61 — ACL standard và extended** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- 3 VLAN: User (10), Server (50), Guest (90) + một "Internet"
- **Standard ACL**: chỉ VLAN 10 được SSH vào router *(dùng `access-class`)*
- **Extended ACL**: Guest ra Internet được, **cấm** vào VLAN 50, nhưng **được dùng DNS**
  ở VLAN 50 → chứng minh quy tắc "cụ thể trước, chung sau"
- Dùng `clear access-list counters` + `show access-lists` để chứng minh từng dòng khớp
- **BREAK bắt buộc:** (1) đảo thứ tự dòng `permit any` lên đầu → quan sát ACL mất tác dụng;
  (2) áp ACL sai hướng *(`out` thay vì `in`)* → quan sát `(0 matches)`;
  (3) dùng subnet mask thay wildcard → quan sát ACL khớp sai;
  (4) áp ACL chặn SSH lên vty mà quên permit IP của mình → **tự khoá**
  *(dùng `reload in 5` trước khi thử!)*

## 12. Challenge

1. Viết ACL: VLAN 10 (`10.0.10.0/24`) được truy cập web server `10.0.50.20` port 80 và 443,
   được dùng DNS `10.0.50.10`, **cấm** mọi thứ khác vào VLAN 50, nhưng **được** ra Internet.
2. ACL của bạn có `permit ip any any` ở dòng 10 và `deny tcp any any eq 23` ở dòng 20.
   Telnet có bị chặn không? Vì sao?
3. Bạn áp ACL lên `Gi0/1 in` (WAN) để chỉ cho HTTPS tới web server nội bộ `10.0.50.20`
   (NAT ra `203.0.113.5`). Viết đúng dòng permit.
4. Nêu 3 cách tránh tự khoá mình khi áp ACL trên thiết bị production.

<details>
<summary>Đáp án</summary>

**1.**

```cisco
ip access-list extended VLAN10-POLICY
 remark Cho phep web va DNS toi server, cam con lai vao VLAN 50
 permit tcp 10.0.10.0 0.0.0.255 host 10.0.50.20 eq 80
 permit tcp 10.0.10.0 0.0.0.255 host 10.0.50.20 eq 443
 permit udp 10.0.10.0 0.0.0.255 host 10.0.50.10 eq 53
 permit tcp 10.0.10.0 0.0.0.255 host 10.0.50.10 eq 53
 deny   ip  10.0.10.0 0.0.0.255 10.0.50.0 0.0.0.255
 permit ip  10.0.10.0 0.0.0.255 any
!
interface vlan 10
 ip access-group VLAN10-POLICY in
```

Thứ tự quan trọng: các dòng `permit` cụ thể **trước**, rồi `deny` cả dải VLAN 50,
rồi `permit any` cuối cùng.

**2.** **Telnet KHÔNG bị chặn.**

Dòng 10 `permit ip any any` khớp **mọi** gói IP — kể cả gói Telnet. ACL
**dừng ở dòng khớp đầu tiên** → dòng 20 không bao giờ được xét.

Sửa: đảo thứ tự.

```cisco
deny   tcp any any eq 23
permit ip  any any
```

**3.**

```cisco
permit tcp any host 203.0.113.5 eq 443
```

Khớp **IP public `203.0.113.5`**, không phải `10.0.50.20`.

Lý do: với gói **đi vào**, thứ tự xử lý là `ACL inbound → NAT → routing`.
Khi ACL chạy, NAT ngược **chưa xảy ra**, gói vẫn mang IP đích là IP public.

Viết `host 10.0.50.20` ở đây → ACL **không bao giờ khớp** → gói rơi vào
implicit deny → web server không truy cập được từ Internet.

**4.** Ba cách:

| # | Cách | Chi tiết |
|:---:|---|---|
| 1 | **Permit IP quản trị ở dòng đầu** | `permit ip host <ip-cua-ban> any` — đơn giản nhất |
| 2 | **`reload in 10`** | Hẹn thiết bị tự khởi động lại sau 10 phút về config cũ. Nếu mọi thứ ổn thì `reload cancel` |
| 3 | **Thử trên một thiết bị trước** | Đừng đẩy đồng loạt. Giữ một phiên SSH đang mở trong lúc thử phiên thứ hai |

Cách 2 là lưới an toàn mạnh nhất — nó cứu bạn kể cả khi quên cách 1.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 quy tắc ACL · dải số standard/extended · wildcard của `/24`, `/26`, `/30` | ⬜ |
| **L2** Explain | Giải thích vì sao standard đặt gần đích, extended gần nguồn | ⬜ |
| **L3** Configure | Viết ACL cho một yêu cầu bằng tiếng Việt, áp đúng chỗ | ⬜ |
| **L4** Troubleshoot | ACL có `(0 matches)` → tìm ra nguyên nhân | ⬜ |
| **L5** Design | Thiết kế bộ ACL cho công ty: guest, user, server, WAN | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **3 quy tắc**: từ trên xuống dừng ở dòng khớp đầu · **implicit deny any** ở cuối ·
  một interface một hướng một ACL
- ⭐ **Cụ thể trước, chung sau** — `deny` hẹp trên, `permit` rộng dưới
- **Standard** (1–99): chỉ source IP → đặt **gần đích**
- **Extended** (100–199): source + dest + protocol + port → đặt **gần nguồn**
- **Wildcard = nghịch đảo subnet mask**; `host x` ≡ `x 0.0.0.0`; `any` ≡ `0.0.0.0 255.255.255.255`
- ⭐ ACL inbound trên WAN thấy **IP public** *(trước NAT)*
- `established` khớp gói TCP có ACK/RST — "stateless firewall" thô sơ
- **Named ACL** nên dùng: có tên, có `remark`, sửa được từng dòng
- `access-class` cho **vty**; `ipv6 traffic-filter` cho **IPv6**
- ⭐ **Luôn permit `packet-too-big`** trong ACL — nếu không hỏng PMTUD
- ⭐ **Counter `(N matches)` là công cụ debug mạnh nhất**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip access-list extended <TEN>` | ⭐ Named ACL |
| `ip access-group <acl> in` | Áp lên interface |
| `access-class <acl> in` | Bảo vệ line vty |
| `ipv6 traffic-filter <acl> in` | ACL IPv6 |
| `show access-lists` | ⭐ Xem counter từng dòng |
| `clear access-list counters` | Reset trước khi test |
| `reload in 10` | ⭐ Lưới an toàn khi áp ACL |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Dùng subnet mask thay wildcard | ACL khớp sai, **IOS không báo lỗi** |
| `permit any` ở dòng đầu | Mọi dòng sau vô nghĩa |
| ACL chỉ có `deny` | Implicit deny chặn hết |
| Áp sai hướng (`in` vs `out`) | `(0 matches)` — không có tác dụng |
| ACL WAN khớp IP private | Không bao giờ khớp |
| Quên permit IP quản trị | **Tự khoá mình**, phải chạy tới console |
| Chặn `packet-too-big` | Web có nội dung lớn bị treo |
| Permit UDP/53 mà quên TCP/53 | DNS "lúc được lúc không" |
| Bật `log` mọi dòng | CPU router tăng cao |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 61 với đủ 4 lỗi BREAK — nhớ dùng `reload in 5` trước khi thử lỗi 4.
2. Viết ACL cho 3 yêu cầu tự nghĩ ra, áp vào lab, dùng counter để chứng minh đúng.
3. Trên thiết bị công ty (nếu có quyền): `show access-lists` — có dòng nào
   `(0 matches)` không? Vì sao?

```markdown
- [YYYY-MM-DD] Lesson 36 — ACL: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 3 quy tắc, wildcard, standard vs extended, đặt ở đâu hướng nào |
| 🔧 **Engineer** | Named ACL + `remark`; dùng counter để debug; `reload in` làm lưới an toàn |
| 🏭 **Production** | ACL WAN khớp IP public; permit `packet-too-big`; chống IP spoofing; `log` tốn CPU |

### 🔗 Liên kết

- ⬅️ [Lesson 35 — CIA, AAA, RADIUS vs TACACS+](./lesson-35-cia-aaa-radius-tacacs.md)
- ➡️ [Lesson 37 — DHCP Snooping, DAI, IPSG](./lesson-37-dhcp-snooping-dai.md)
- 📚 Thứ tự NAT/ACL: [Lesson 27](../03-services/lesson-27-nat-nang-cao.md)
- 🧮 Wildcard mask: [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md#5-wildcard-mask-dùng-trong-ospf--acl)
