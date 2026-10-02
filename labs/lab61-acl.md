# LAB 61 — ACL standard và extended

> ⚠️ **Lỗi BREAK 4 làm bạn tự khoá mình ra khỏi thiết bị.**
> Dùng `reload in 5` trước khi thử.

| | |
|---|---|
| **Phase** | 6 |
| **Lesson liên quan** | [Lesson 36 — ACL](../06-security/lesson-36-acl.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~3 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Viết ACL cho một yêu cầu bằng tiếng Việt, áp đúng interface và hướng
- [ ] Dùng **counter `(N matches)`** để debug — không đoán mò
- [ ] Chứng minh **thứ tự dòng quyết định tất cả**
- [ ] Chứng minh ACL trên WAN khớp **IP public**, không phải IP private
- [ ] Bảo vệ line vty bằng `access-class`

## 2. Prerequisite

- [Lesson 36](../06-security/lesson-36-acl.md) — 3 quy tắc, wildcard, standard vs extended
- [Lesson 27](../03-services/lesson-27-nat-nang-cao.md) — thứ tự NAT/routing/ACL
- Wildcard mask *(Lesson 02)*

---

## 3. Topology

```text
                              ┌─ Server-WEB  10.0.50.20
   VLAN 10 ──┐                │  (HTTP + HTTPS)
   USER      │                │
             ├── SW-L3 ── R1 ─┤─ Server-DNS  10.0.50.10
   VLAN 90 ──┘   (L3)    (NAT)│
   GUEST                      │
                              └─ "Internet"  203.0.113.0/30 → 8.8.8.8
```

| VLAN | Tên | Subnet | Gateway (SVI) |
|:---:|---|---|---|
| 10 | USER | `10.0.10.0/24` | `10.0.10.1` |
| 50 | SERVER | `10.0.50.0/24` | `10.0.50.1` |
| 90 | GUEST | `10.0.90.0/24` | `10.0.90.1` |
| — | WAN | `203.0.113.0/30` | R1 Gi0/1 = `203.0.113.2` |

## 4. IP Addressing Table

| Device | Interface | IP | VLAN |
|---|---|---|:---:|
| SW-L3 | Vlan10 | `10.0.10.1/24` | 10 |
| SW-L3 | Vlan50 | `10.0.50.1/24` | 50 |
| SW-L3 | Vlan90 | `10.0.90.1/24` | 90 |
| SW-L3 | Gi1/0/24 *(routed port → R1)* | `10.0.99.1/30` | — |
| R1 | Gi0/0 *(→ SW-L3)* | `10.0.99.2/30` | — |
| R1 | Gi0/1 *(WAN)* | `203.0.113.2/30` | — |
| PC-USER | Fa0 | `10.0.10.10/24`, GW `10.0.10.1` | 10 |
| PC-GUEST | Fa0 | `10.0.90.10/24`, GW `10.0.90.1` | 90 |
| Server-WEB | Fa0 | `10.0.50.20/24`, GW `10.0.50.1` | 50 |
| Server-DNS | Fa0 | `10.0.50.10/24`, GW `10.0.50.1` | 50 |
| ISP | Gi0/0 · Lo0 | `203.0.113.1/30` · `8.8.8.8/32` | — |

> 💡 Bật HTTP và HTTPS trên Server-WEB *(tab Services)*, bật DNS trên Server-DNS.

---

## 5. Yêu cầu LAB

Ba chính sách phải thực hiện:

| # | Chính sách | Loại ACL |
|:---:|---|---|
| **A** | **Chỉ VLAN 10** được SSH vào SW-L3 | **Standard** + `access-class` |
| **B** | **GUEST** được dùng DNS nội bộ và ra Internet, nhưng **cấm** mọi thứ khác vào `10.0.0.0/16` | **Extended** |
| **C** | Từ Internet **chỉ** vào được web server qua HTTPS *(NAT ra `203.0.113.2`)* | **Extended** trên WAN |

- [ ] Cả 3 chính sách hoạt động đúng
- [ ] Dùng `clear access-list counters` + `show access-lists` chứng minh từng dòng khớp
- [ ] Hoàn thành mục **8. BREAK** với đủ 4 lỗi

---

## 6. Step-by-step

### Bước 0 — Cấu hình nền (chưa có ACL)

```cisco
! ══ SW-L3 ══
ip routing
vlan 10
 name USER
vlan 50
 name SERVER
vlan 90
 name GUEST
exit

interface vlan 10
 ip address 10.0.10.1 255.255.255.0
 no shutdown
interface vlan 50
 ip address 10.0.50.1 255.255.255.0
 no shutdown
interface vlan 90
 ip address 10.0.90.1 255.255.255.0
 no shutdown

interface GigabitEthernet1/0/24
 no switchport
 ip address 10.0.99.1 255.255.255.252
 no shutdown

ip route 0.0.0.0 0.0.0.0 10.0.99.2

! ══ R1 ══
interface GigabitEthernet0/0
 ip address 10.0.99.2 255.255.255.252
 ip nat inside
 no shutdown
interface GigabitEthernet0/1
 ip address 203.0.113.2 255.255.255.252
 ip nat outside
 no shutdown

ip route 10.0.0.0 255.255.0.0 10.0.99.1
ip route 0.0.0.0 0.0.0.0 203.0.113.1

access-list 1 permit 10.0.0.0 0.0.255.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
ip nat inside source static tcp 10.0.50.20 443 203.0.113.2 443
```

**Verify nền trước khi thêm ACL:**

| Từ | Tới | Mong đợi |
|---|---|---|
| PC-USER | Server-WEB | ✅ |
| PC-GUEST | Server-WEB | ✅ *(chưa có ACL)* |
| PC-GUEST | `8.8.8.8` | ✅ |
| PC-USER | `8.8.8.8` | ✅ |

### Bước 1 — Chính sách A: Standard ACL cho vty

```cisco
SW-L3(config)# ip access-list standard CHI-VLAN10-SSH
SW-L3(config-std-nacl)# remark Chi VLAN 10 duoc quan tri switch
SW-L3(config-std-nacl)# permit 10.0.10.0 0.0.0.255
SW-L3(config-std-nacl)# deny any log
SW-L3(config-std-nacl)# exit

SW-L3(config)# line vty 0 15
SW-L3(config-line)# access-class CHI-VLAN10-SSH in
SW-L3(config-line)# transport input ssh
```

> ⚠️ Dùng **`access-class`**, không phải `ip access-group`. Đây là ACL bảo vệ
> **management plane**, khác với ACL lọc traffic đi qua.

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| SSH từ PC-USER vào `10.0.10.1` | ✅ | |
| SSH từ PC-GUEST vào `10.0.90.1` | ❌ Bị từ chối | |

### Bước 2 — Chính sách B: Extended ACL cho GUEST

> 🔴 **Viết ra giấy trước.** Thứ tự dòng rất quan trọng.

Yêu cầu: GUEST được dùng DNS `10.0.50.10`, **cấm** mọi thứ khác vào `10.0.0.0/16`,
**được** ra Internet.

| Thứ tự | Dòng | Vì sao ở vị trí này |
|:---:|---|---|
| 1 | permit DNS tới `10.0.50.10` | DNS server **nằm trong** dải bị cấm → phải đứng trước |
| 2 | deny `10.0.90.0/24` → `10.0.0.0/16` | Cấm nội bộ |
| 3 | permit `10.0.90.0/24` → any | Ra Internet |

```cisco
SW-L3(config)# ip access-list extended GUEST-POLICY
SW-L3(config-ext-nacl)# remark 1. Cho DNS noi bo (phai dung TRUOC dong deny)
SW-L3(config-ext-nacl)# permit udp 10.0.90.0 0.0.0.255 host 10.0.50.10 eq 53
SW-L3(config-ext-nacl)# permit tcp 10.0.90.0 0.0.0.255 host 10.0.50.10 eq 53
SW-L3(config-ext-nacl)# remark 2. Cam moi thu khac vao noi bo
SW-L3(config-ext-nacl)# deny   ip  10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255
SW-L3(config-ext-nacl)# remark 3. Con lai ra Internet
SW-L3(config-ext-nacl)# permit ip  10.0.90.0 0.0.0.255 any
SW-L3(config-ext-nacl)# exit

SW-L3(config)# interface vlan 90
SW-L3(config-if)# ip access-group GUEST-POLICY in
```

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| PC-GUEST ping `8.8.8.8` | ✅ | |
| PC-GUEST ping Server-WEB `10.0.50.20` | ❌ | |
| PC-GUEST ping PC-USER `10.0.10.10` | ❌ | |
| PC-GUEST phân giải DNS *(nslookup)* | ✅ | |

### Bước 3 — Chính sách C: ACL trên WAN ⭐

> 🔴 **Câu hỏi quan trọng nhất của lab:** ACL này khớp IP nào —
> `10.0.50.20` hay `203.0.113.2`? Trả lời trước khi gõ.

```cisco
R1(config)# ip access-list extended TU-INTERNET
R1(config-ext-nacl)# remark Chi cho HTTPS toi web server
R1(config-ext-nacl)# permit tcp any host 203.0.113.2 eq 443
R1(config-ext-nacl)# permit icmp any any echo-reply
R1(config-ext-nacl)# permit icmp any any packet-too-big
R1(config-ext-nacl)# permit icmp any any time-exceeded
R1(config-ext-nacl)# remark Chong IP spoofing
R1(config-ext-nacl)# deny   ip 10.0.0.0 0.255.255.255 any log
R1(config-ext-nacl)# deny   ip 172.16.0.0 0.15.255.255 any log
R1(config-ext-nacl)# deny   ip 192.168.0.0 0.0.255.255 any log
R1(config-ext-nacl)# deny   ip any any log
R1(config-ext-nacl)# exit

R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip access-group TU-INTERNET in
```

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| PC-USER ping `8.8.8.8` | ✅ *(nhờ `echo-reply`)* | |
| Từ ISP, truy cập `https://203.0.113.2` | ✅ | |
| Từ ISP, ping `203.0.113.2` | ❌ *(không permit echo-request)* | |

### Bước 4 — Debug bằng counter ⭐

```cisco
SW-L3# clear access-list counters
! ... tạo traffic test từ PC-GUEST ...
SW-L3# show access-lists GUEST-POLICY
```

| Dòng | Số matches | Nghĩa là gì |
|---|:---:|---|
| permit udp ... eq 53 | | |
| deny ip ... 10.0.0.0 | | |
| permit ip ... any | | |

> 🔑 Dòng nào có **`(0 matches)`** → traffic **không bao giờ tới dòng đó**.
> Hoặc dòng trên đã bắt hết, hoặc ACL đặt sai chỗ.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW-L3# show access-lists GUEST-POLICY
Extended IP access list GUEST-POLICY
    10 permit udp 10.0.90.0 0.0.0.255 host 10.0.50.10 eq domain (14 matches)
    20 permit tcp 10.0.90.0 0.0.0.255 host 10.0.50.10 eq domain (0 matches)
    30 deny ip 10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255 (8 matches)
    40 permit ip 10.0.90.0 0.0.0.255 any (142 matches)
```

```text
# output điển hình — tự verify trên lab của bạn
SW-L3# show ip interface vlan 90 | include access list
  Inbound  access list is GUEST-POLICY
  Outgoing access list is not set
```

```text
# output điển hình — log khi ACL chặn
%SEC-6-IPACCESSLOGP: list TU-INTERNET denied tcp 198.51.100.7(51234)
   -> 203.0.113.2(22), 1 packet
```

**Bảng kiểm chứng tổng hợp:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | SSH từ VLAN 10 vào SW-L3 | ✅ | |
| 2 | SSH từ VLAN 90 vào SW-L3 | ❌ | |
| 3 | GUEST → `8.8.8.8` | ✅ | |
| 4 | GUEST → Server-WEB | ❌ | |
| 5 | GUEST → DNS `10.0.50.10` | ✅ | |
| 6 | USER → Server-WEB | ✅ | |
| 7 | Internet → `https://203.0.113.2` | ✅ | |
| 8 | Internet → ping `203.0.113.2` | ❌ | |
| 9 | Mọi dòng `permit` đều có matches > 0 | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Đảo thứ tự: `permit any` lên đầu

```cisco
SW-L3(config)# ip access-list extended GUEST-POLICY
SW-L3(config-ext-nacl)# 5 permit ip any any
```

| | |
|---|---|
| PC-GUEST ping Server-WEB: kết quả? | |
| `show access-lists` — dòng nào có matches, dòng nào `(0 matches)`? | |
| Vì sao các dòng sau không chạy? | |
| Quy tắc nào bị vi phạm? | |

Gỡ: `no 5`.

### Lỗi 2 — Áp sai hướng

```cisco
SW-L3(config)# interface vlan 90
SW-L3(config-if)# no ip access-group GUEST-POLICY in
SW-L3(config-if)# ip access-group GUEST-POLICY out
```

| | |
|---|---|
| PC-GUEST ping Server-WEB: kết quả? | |
| `show access-lists` sau khi test — có matches không? | |
| Giải thích: chiều `out` của Vlan90 là traffic đi **từ đâu tới đâu**? | |

### Lỗi 3 — ACL WAN khớp IP private ⭐

> 🔴 Đây là lỗi quan trọng nhất của lab.

```cisco
R1(config)# ip access-list extended TU-INTERNET
R1(config-ext-nacl)# no 10
R1(config-ext-nacl)# 10 permit tcp any host 10.0.50.20 eq 443
```

| | |
|---|---|
| Từ ISP, truy cập `https://203.0.113.2`: kết quả? | |
| `show access-lists TU-INTERNET` — dòng 10 có matches không? | |
| **Vì sao ACL không bao giờ khớp?** | |
| Nhắc lại thứ tự xử lý gói đi **vào** router | |

### Lỗi 4 — Tự khoá mình ⚠️

> 🔴 **Gõ `reload in 5` TRƯỚC KHI làm bước này.**

```cisco
SW-L3# reload in 5
SW-L3(config)# ip access-list standard CHI-VLAN10-SSH
SW-L3(config-std-nacl)# no permit 10.0.10.0 0.0.0.255
SW-L3(config-std-nacl)# permit 10.0.20.0 0.0.0.255     ! dải KHÔNG tồn tại
```

| | |
|---|---|
| SSH từ PC-USER còn được không? | |
| Phiên SSH đang mở có bị ngắt ngay không? *(thử gõ lệnh)* | |
| Sau 5 phút chuyện gì xảy ra? | |
| Nếu không có `reload in 5` thì phải làm sao? | |

Nếu kịp: `reload cancel` rồi sửa ACL.

### Lỗi 5 *(tự chọn)* — Dùng subnet mask thay wildcard

```cisco
SW-L3(config-ext-nacl)# 15 deny ip 10.0.90.0 255.255.255.0 any
```

| | |
|---|---|
| IOS có nhận lệnh không? | |
| `show access-lists` hiển thị dòng đó thế nào? | |
| Nó khớp những IP nào? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Viết ACL: VLAN 10 được truy cập web server `10.0.50.20` port 80 và 443,
   được dùng DNS `10.0.50.10`, **cấm** mọi thứ khác vào VLAN 50, nhưng **được** ra Internet.
2. ACL của bạn chặn được TCP nhưng người dùng vẫn phân giải DNS được qua UDP.
   Nguyên nhân và cách sửa.
3. Bạn muốn **chặn ping từ Internet** nhưng vẫn cho người dùng nội bộ ping ra ngoài.
   Viết dòng ACL cần thiết trên WAN interface.
4. Sau khi áp ACL trên WAN, nhân viên báo "web có ảnh lớn thì treo". Nguyên nhân?

<details>
<summary>Đáp án</summary>

**1.**

```cisco
ip access-list extended VLAN10-POLICY
 remark Cho web + DNS, cam con lai vao VLAN 50
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

Thứ tự: **permit cụ thể trước** → **deny dải** → **permit chung cuối**.

**2.** Nguyên nhân: bạn chỉ viết `permit tcp ... eq 53` mà **quên UDP**, hoặc ngược lại —
chỉ `deny tcp` mà không `deny udp`.

DNS dùng **cả UDP/53 và TCP/53** *(Lesson 06, 26)*. Phải viết **cả hai dòng**:

```cisco
permit udp <src> <wildcard> host 10.0.50.10 eq 53
permit tcp <src> <wildcard> host 10.0.50.10 eq 53
```

Đây cũng là lý do lỗi DNS kiểu "lúc được lúc không" rất khó tìm — phần lớn truy vấn
chạy UDP nên bình thường, chỉ reply lớn mới cần TCP.

**3.**

```cisco
! Chặn ping TỪ Internet vào (echo-request), nhưng cho reply của ping NỘI BỘ đi ra
ip access-list extended TU-INTERNET
 permit icmp any any echo-reply          ! ← reply cho ping nội bộ gửi ra
 permit icmp any any packet-too-big      ! ← PMTUD, BẮT BUỘC
 permit icmp any any time-exceeded       ! ← traceroute nội bộ hoạt động
 deny   icmp any any echo                ! ← chặn ping TỪ ngoài vào
 ...
```

Nguyên lý: khi bạn ping ra ngoài, gói **đi ra** là `echo-request`, gói **về** là
`echo-reply`. ACL inbound trên WAN chỉ thấy gói **về** → permit `echo-reply` là đủ
cho ping nội bộ ra ngoài, trong khi `deny echo` chặn người ngoài ping vào.

**4.** Nguyên nhân: ACL **chặn `packet-too-big`** *(ICMP Type 3 Code 4 với IPv4,
Type 2 với IPv6)* → **PMTUD hỏng**.

```text
Server gửi gói 1500 byte
→ Trên đường có link MTU nhỏ hơn (PPPoE 1492, tunnel 1400...)
→ Router gửi về "Packet Too Big"
→ ACL CHẶN gói đó
→ Server không bao giờ biết phải thu nhỏ
→ Gói lớn bị drop IM LẶNG
```

Triệu chứng đặc trưng: **ping được, trang text load được, trang có ảnh/file lớn thì treo**.

Sửa: luôn có dòng này trong **mọi** ACL trên WAN:

```cisco
permit icmp any any packet-too-big
```

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Bảng kiểm chứng — kết quả đúng

| # | Kiểm tra | Kết quả | Vì sao |
|:---:|---|:---:|---|
| 1 | SSH từ VLAN 10 | ✅ | Khớp dòng `permit 10.0.10.0` của standard ACL |
| 2 | SSH từ VLAN 90 | ❌ | Rơi vào `deny any log` |
| 3 | GUEST → `8.8.8.8` | ✅ | Khớp dòng 40 `permit ip ... any` |
| 4 | GUEST → Server-WEB | ❌ | Khớp dòng 30 `deny ip ... 10.0.0.0/16` |
| 5 | GUEST → DNS | ✅ | Khớp dòng 10 — **đứng trước** dòng deny |
| 6 | USER → Server-WEB | ✅ | VLAN 10 không bị ACL nào chặn |
| 7 | Internet → HTTPS | ✅ | Khớp `permit tcp any host 203.0.113.2 eq 443` |
| 8 | Internet → ping | ❌ | Không có dòng permit `echo`, rơi vào `deny ip any any` |

### Giải thích các lỗi BREAK

**Lỗi 1 — `permit any` lên đầu:**

```text
5  permit ip any any                 (150 matches)   ← bắt HẾT
10 permit udp ... eq 53              (0 matches)
20 permit tcp ... eq 53              (0 matches)
30 deny ip ... 10.0.0.0              (0 matches)     ← không bao giờ chạy
40 permit ip ... any                 (0 matches)
```

ACL xử lý **từ trên xuống, dừng ở dòng khớp đầu tiên**. Dòng 5 khớp mọi gói IP →
mọi dòng sau **vô nghĩa**. GUEST ping được Server-WEB.

**Quy tắc bị vi phạm:** *cụ thể trước, chung sau*.

**Lỗi 2 — áp sai hướng:**

```text
Vlan90 hướng "in"  = traffic TỪ GUEST đi vào switch   ← đúng chỗ cần lọc
Vlan90 hướng "out" = traffic TỪ switch đi RA VLAN 90  ← chiều ngược lại
```

Với ACL ở chiều `out`, gói từ GUEST đi tới Server-WEB **không bị kiểm tra**
*(nó đi `in` ở Vlan90, `out` ở Vlan50)*. Gói **trả lời** mới bị kiểm tra —
nhưng ACL được viết với source là `10.0.90.0/24`, mà gói trả lời có source là
`10.0.50.20` → **không khớp dòng nào** → rơi vào implicit deny.

Kết quả: ping fail, nhưng **vì lý do sai** — và `show access-lists` cho thấy
các dòng permit đều `(0 matches)`.

**Lỗi 3 — ACL WAN khớp IP private ⭐:**

```text
Thứ tự xử lý gói ĐI VÀO router:
  1. ACL inbound trên interface nhận   ← chạy ở đây
  2. NAT (outside → inside)             ← NAT ngược xảy ra SAU
  3. ROUTING

Khi ACL chạy, gói vẫn mang:  Dst = 203.0.113.2
ACL của bạn khớp:            Dst = 10.0.50.20
→ KHÔNG BAO GIỜ KHỚP
```

`show access-lists` xác nhận: dòng 10 có **`(0 matches)`** dù có traffic.
Gói rơi xuống `deny ip any any` → web server không truy cập được từ Internet.

**Lỗi 4 — tự khoá mình:**

| Quan sát | Giải thích |
|---|---|
| SSH mới từ PC-USER: **bị từ chối** | ACL vty chỉ cho `10.0.20.0/24` — dải không tồn tại |
| Phiên SSH **đang mở**: vẫn gõ lệnh được | `access-class` chỉ kiểm tra lúc **thiết lập** kết nối |
| Sau 5 phút | Thiết bị **reload** về `startup-config` *(chưa có ACL sai)* → khôi phục tự động |
| Không có `reload in` | Phải vào bằng **console** |

> 🔑 Chi tiết "phiên đang mở không bị ngắt" rất quan trọng: nó cho bạn **cơ hội sửa**
> nếu phát hiện kịp. Đây là lý do quy tắc *"giữ một phiên SSH đang mở khi thử ACL"*.

**Lỗi 5 — subnet mask thay wildcard:**

IOS **nhận lệnh** nhưng hiểu `255.255.255.0` là **wildcard**:

```text
Wildcard 255.255.255.0  nghĩa là:
  - 3 octet đầu: BỎ QUA (bit 1)
  - octet cuối:  PHẢI KHỚP (bit 0)

→ Khớp MỌI IP có octet cuối = 0
→ 10.0.90.0, 192.168.1.0, 8.8.8.0 ...
```

Hoàn toàn không phải ý định ban đầu — và **không có thông báo lỗi nào**.

### Bảng tổng kết kỹ năng debug ACL

| Triệu chứng | Lệnh | Kết luận |
|---|---|---|
| ACL không có tác dụng | `show ip interface <int> \| include access` | Chưa áp vào interface |
| Dòng permit `(0 matches)` | `show access-lists` | Dòng trên bắt hết, hoặc sai hướng/interface |
| Chặn hết mọi thứ | `show access-lists` | Thiếu `permit`, chỉ còn implicit deny |
| ACL WAN không khớp | `show access-lists` counter = 0 | Khớp IP private thay vì public |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Dòng nào trong ACL của tôi có `(0 matches)`? Vì sao? ___
- Lỗi 3 (IP public vs private) — tôi đã trả lời đúng trước khi gõ chưa? ___
- `reload in 5` đã cứu tôi chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
