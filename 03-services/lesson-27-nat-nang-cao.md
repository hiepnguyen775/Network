# LESSON 27 — NAT nâng cao: Port Forwarding · Dual-WAN · NAT + VPN

> 📦 **Phase 0 đã dạy gì — lesson này thêm gì**
>
> | [Lesson 09](../00-foundation/lesson-09-nat-private-public.md) *(khái niệm)* | Lesson này *(triển khai)* |
> |---|---|
> | Static/dynamic/PAT, 4 thuật ngữ | **Port forwarding** chi tiết, NAT pool |
> | `ip nat inside/outside` | **Thứ tự xử lý** NAT vs routing vs ACL |
> | Bảng NAT cơ bản | **Dual-WAN NAT** với route-map |
> | — | **Loại trừ traffic VPN** · NAT timeout tuning · ALG |

| | |
|---|---|
| **Phase** | 3 — Services |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 09](../00-foundation/lesson-09-nat-private-public.md), [Lesson 19](../02-routing/lesson-19-static-default-route.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Cấu hình port forwarding cho server nội bộ, hiểu rủi ro đi kèm
- [ ] Giải thích **thứ tự xử lý** NAT, routing và ACL trên router
- [ ] Cấu hình NAT cho **dual-WAN** bằng route-map
- [ ] **Loại trừ traffic VPN** khỏi NAT — và hiểu vì sao bắt buộc
- [ ] Chỉnh NAT timeout khi bảng NAT đầy

## 2. Prerequisite

- 3 kiểu NAT, 4 thuật ngữ inside/outside local/global *(Lesson 09)*
- Floating static, dual-WAN *(Lesson 19)*
- Socket 4 giá trị *(Lesson 06)*

---

## 3. Concept

### Thứ tự xử lý trên router — bảng phải thuộc

**Gói đi RA (inside → outside):**

```text
1. Kiểm tra ACL inbound trên interface inside
2. Giải mã (nếu là traffic VPN đi vào)
3. ROUTING — quyết định ra interface nào
4. NAT (inside → outside)          ← NAT SAU routing
5. Mã hoá (nếu đi ra VPN)
6. Kiểm tra ACL outbound trên interface outside
```

**Gói đi VÀO (outside → inside):**

```text
1. Kiểm tra ACL inbound trên interface outside
2. Giải mã VPN
3. NAT (outside → inside)           ← NAT TRƯỚC routing
4. ROUTING
5. ACL outbound trên interface inside
```

> ⭐ **Hệ quả quan trọng nhất:**
> ACL trên interface **outside, chiều inbound** nhìn thấy **IP PUBLIC** (chưa NAT ngược).
> ACL trên interface **inside** nhìn thấy **IP PRIVATE**.
>
> Viết ACL sai phía là nguyên nhân rất nhiều ACL "không có tác dụng".

### Port forwarding — mở server ra Internet

```cisco
! Toàn bộ IP (hiếm dùng)
ip nat inside source static 10.0.50.20 203.0.113.10

! Chỉ một port — AN TOÀN HƠN, dùng cái này
ip nat inside source static tcp 10.0.50.20 443 203.0.113.5 443
ip nat inside source static tcp 10.0.50.20 80  203.0.113.5 80

! Đổi port (ẩn port thật)
ip nat inside source static tcp 10.0.50.20 22 203.0.113.5 2222
```

| Cách | Mở gì ra Internet |
|---|---|
| Static NAT toàn IP | **Mọi port** của server — rủi ro cao |
| Static NAT theo port | **Chỉ port đó** — nên dùng |
| Đổi port | Giảm quét tự động, **không phải** bảo mật thật |

> ⚠️ Port forwarding là **quyết định bảo mật**, không phải quyết định mạng.
> Mở `3389` (RDP) ra Internet = cả thế giới gõ cửa. Luôn kèm **ACL giới hạn source**
> hoặc dùng VPN thay vì mở port.

### NAT + VPN — vì sao phải loại trừ

```text
Site A (10.0.0.0/24)  ══VPN══  Site B (10.1.0.0/24)
        │
        └── cũng có đường ra Internet qua NAT
```

Nếu không loại trừ: traffic `10.0.0.5 → 10.1.0.5` (đi VPN) **cũng bị NAT** thành
`203.0.113.5 → 10.1.0.5`. Site B nhận gói từ IP lạ, không khớp selector của tunnel →
**tunnel không lên** hoặc traffic bị drop.

```cisco
ip access-list extended NAT-ACL
 deny   ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255    ! traffic VPN → KHÔNG NAT
 permit ip 10.0.0.0 0.0.0.255 any                    ! còn lại → NAT
!
ip nat inside source list NAT-ACL interface Gi0/1 overload
```

> 🔑 **Thứ tự dòng rất quan trọng.** `deny` phải đứng **trước** `permit`.
> ACL xử lý từ trên xuống, dừng ở dòng khớp đầu tiên *(Lesson 36)*.

> ⚠️ `deny` trong **NAT-ACL** không có nghĩa "chặn traffic" — nó có nghĩa
> **"không NAT traffic này"**. Đây là chỗ hiểu nhầm phổ biến.

### Dual-WAN NAT — cần route-map

Với 2 đường Internet, **không thể** dùng `ip nat inside source list 1 interface Gi0/1 overload`
cho cả hai — mỗi interface cần một quy tắc riêng, và phải biết traffic đang đi đường nào.

```cisco
! ACL xác định mạng nội bộ
ip access-list standard NOI-BO
 permit 10.0.0.0 0.0.255.255

! Route-map gắn ACL với từng interface ra
route-map NAT-WAN1 permit 10
 match ip address NOI-BO
 match interface GigabitEthernet0/1

route-map NAT-WAN2 permit 10
 match ip address NOI-BO
 match interface GigabitEthernet0/2

! Hai quy tắc NAT riêng
ip nat inside source route-map NAT-WAN1 interface GigabitEthernet0/1 overload
ip nat inside source route-map NAT-WAN2 interface GigabitEthernet0/2 overload
```

> 🔑 `match interface` là mấu chốt: nó đảm bảo gói ra Gi0/1 được NAT thành IP của Gi0/1,
> gói ra Gi0/2 thành IP của Gi0/2.
>
> ⚠️ Khi failover, **phải xoá bảng NAT cũ** (`clear ip nat translation *`), nếu không
> các kết nối đang mở vẫn mang IP của WAN đã chết.

### NAT timeout

| Loại | Mặc định | Chỉnh khi |
|---|:---:|---|
| TCP | 24 giờ | Bảng NAT đầy → giảm xuống 1–4 giờ |
| UDP | 5 phút | Thường để nguyên |
| ICMP | 1 phút | Để nguyên |
| DNS | 1 phút | Để nguyên |
| TCP sau `FIN`/`RST` | 1 phút | Để nguyên |

```cisco
ip nat translation timeout 3600          ! TCP → 1 giờ
ip nat translation udp-timeout 300
ip nat translation max-entries 10000     ! giới hạn, tránh một máy chiếm hết
```

### NAT ALG — khi NAT phá giao thức

Một số giao thức nhúng **địa chỉ IP vào trong payload**, không chỉ trong header.
NAT đổi header nhưng không đổi payload → giao thức hỏng.

| Giao thức | Vấn đề | Giải pháp |
|---|---|---|
| **FTP active** | Client gửi IP của mình trong lệnh `PORT` | NAT ALG tự sửa payload |
| **SIP** (VoIP) | IP nằm trong SDP | SIP ALG — ⚠️ thường gây lỗi nhiều hơn là giúp |
| **IPsec AH** | Hash bao gồm cả IP header → NAT làm hỏng hash | **Không dùng được** qua NAT — phải dùng ESP + NAT-T |

> 🏭 **Lời khuyên thực tế:** nếu VoIP qua NAT bị lỗi một chiều âm thanh,
> thử **TẮT** `ip nat service sip` trước — SIP ALG của nhiều thiết bị làm hỏng nhiều hơn sửa.

---

## 4. Why?

> **Vì sao không cấp IP public cho mọi server thay vì port forwarding?**

| Port forwarding | IP public cho từng server |
|---|---|
| ✅ Tiết kiệm IP public *(đắt)* | ❌ Mỗi IP một khoản tiền |
| ✅ Một điểm kiểm soát duy nhất | ❌ Phải bảo vệ từng server |
| ✅ Đổi server nội bộ không ảnh hưởng bên ngoài | ❌ Phải thông báo IP mới |
| ❌ Thêm một lớp phức tạp khi debug | ✅ Đơn giản hơn |

> 🏭 Thực tế: doanh nghiệp vừa dùng **port forwarding + firewall**.
> Chỉ DMZ lớn hoặc hosting mới cấp IP public trực tiếp.

---

## 5. How does it work? — port forwarding từng bước

```text
Client Internet (198.51.100.7) → https://203.0.113.5

1. Gói tới router: Src 198.51.100.7:51234 → Dst 203.0.113.5:443
2. Interface Gi0/1 (outside) nhận
3. ACL inbound trên Gi0/1 kiểm tra  ← thấy IP PUBLIC 203.0.113.5
4. NAT (outside→inside): tra bảng static
   203.0.113.5:443 → 10.0.50.20:443
   GHI LẠI Dst: 198.51.100.7:51234 → 10.0.50.20:443
5. ROUTING: 10.0.50.0/24 ra interface Gi0/0
6. Gửi vào server

Chiều về:
7. Server trả lời: Src 10.0.50.20:443 → Dst 198.51.100.7:51234
8. ROUTING ra Gi0/1
9. NAT (inside→outside): GHI LẠI Src thành 203.0.113.5:443
10. Gửi ra Internet
```

> 🔑 Bước 3 là điểm mấu chốt cho ACL: nếu bạn muốn chặn ai đó truy cập server,
> ACL trên Gi0/1 inbound phải khớp **`203.0.113.5`**, không phải `10.0.50.20`.

---

## 6. Packet Flow — NAT trong bảng

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
tcp 203.0.113.5:443    10.0.50.20:443     198.51.100.7:51234 198.51.100.7:51234
tcp 203.0.113.5:443    10.0.50.20:443     198.51.100.9:49800 198.51.100.9:49800
--- 203.0.113.5:443    10.0.50.20:443     ---                ---
tcp 203.0.113.5:1024   10.0.10.15:51000   8.8.8.8:443        8.8.8.8:443
```

| Dòng | Loại |
|---|---|
| 2 dòng đầu | **Kết nối đang hoạt động** tới server qua port forwarding |
| Dòng `---` | **Entry static** của chính port forwarding (luôn tồn tại) |
| Dòng cuối | **PAT** của một PC nội bộ ra Internet |

---

## 7. Real-world Example

🏭 **Cấu hình đầy đủ cho doanh nghiệp: dual-WAN + VPN + port forwarding**

```cisco
! ───── Khai hướng ─────
interface GigabitEthernet0/0
 description LAN
 ip nat inside
interface GigabitEthernet0/1
 description WAN1-ISP-CHINH
 ip nat outside
interface GigabitEthernet0/2
 description WAN2-ISP-BACKUP
 ip nat outside

! ───── ACL: loại trừ VPN, cho phép còn lại ─────
ip access-list extended NAT-ACL
 deny   ip 10.0.0.0 0.0.255.255 10.1.0.0 0.0.255.255   ! traffic sang chi nhánh (VPN)
 permit ip 10.0.0.0 0.0.255.255 any

! ───── Route-map cho từng WAN ─────
route-map NAT-WAN1 permit 10
 match ip address NAT-ACL
 match interface GigabitEthernet0/1
route-map NAT-WAN2 permit 10
 match ip address NAT-ACL
 match interface GigabitEthernet0/2

ip nat inside source route-map NAT-WAN1 interface GigabitEthernet0/1 overload
ip nat inside source route-map NAT-WAN2 interface GigabitEthernet0/2 overload

! ───── Port forwarding cho web server ─────
ip nat inside source static tcp 10.0.50.20 443 203.0.113.5 443

! ───── ACL bảo vệ: chỉ cho HTTPS vào, chặn còn lại ─────
ip access-list extended TU-INTERNET
 permit tcp any host 203.0.113.5 eq 443
 permit icmp any any echo-reply
 deny   ip any any log
interface GigabitEthernet0/1
 ip access-group TU-INTERNET in
```

> 🔑 Chú ý ACL `TU-INTERNET` khớp **`203.0.113.5`** (IP public) chứ không phải
> `10.0.50.20` — vì nó nằm ở interface outside chiều inbound, **trước khi NAT ngược**.

🏭 **Sự cố: bảng NAT đầy vào giờ cao điểm**

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat statistics
Total active translations: 9847 (1 static, 9846 dynamic; 9846 extended)
Hits: 2847193  Misses: 18422
```

`Misses` tăng nhanh + router nhỏ giới hạn ~10000 entry → kết nối mới bị từ chối.
Triệu chứng người dùng: *"mạng chậm vào buổi chiều"*.

Cách xử lý:

```cisco
ip nat translation timeout 3600           ! giảm TCP từ 24h xuống 1h
ip nat translation max-entries per-host 300   ! một máy không chiếm quá 300 entry
```

🏭 **Lỗi failover WAN mà quên clear NAT**

ISP1 chết → floating static chuyển sang ISP2 → nhưng các kết nối đang mở vẫn có entry NAT
mang IP của ISP1. Chúng không bao giờ nhận được reply.

Triệu chứng: *"chuyển sang đường backup rồi mà vẫn không vào được, phải đợi vài phút"*.

```cisco
R1# clear ip nat translation *
```

> 🔧 Trong thiết kế thật, việc này được tự động hoá bằng **IP SLA + track + EEM script**.
> Ở CCNA chỉ cần biết tại sao phải làm.

---

## 8. Cisco CLI

```cisco
! ═══════ PAT CƠ BẢN (ôn lại) ═══════
R1(config)# interface Gi0/0
R1(config-if)# ip nat inside
R1(config)# interface Gi0/1
R1(config-if)# ip nat outside
R1(config)# access-list 1 permit 10.0.0.0 0.0.255.255
R1(config)# ip nat inside source list 1 interface Gi0/1 overload

! ═══════ PORT FORWARDING ═══════
R1(config)# ip nat inside source static tcp 10.0.50.20 443 203.0.113.5 443
R1(config)# ip nat inside source static udp 10.0.50.30 53 203.0.113.5 53

! ═══════ NAT POOL ═══════
R1(config)# ip nat pool PUBLIC-POOL 203.0.113.10 203.0.113.20 netmask 255.255.255.0
R1(config)# ip nat inside source list 1 pool PUBLIC-POOL overload

! ═══════ LOẠI TRỪ VPN ═══════
R1(config)# ip access-list extended NAT-ACL
R1(config-ext-nacl)# deny   ip 10.0.0.0 0.0.255.255 10.1.0.0 0.0.255.255
R1(config-ext-nacl)# permit ip 10.0.0.0 0.0.255.255 any
R1(config)# ip nat inside source list NAT-ACL interface Gi0/1 overload

! ═══════ DUAL-WAN ═══════
R1(config)# route-map NAT-WAN1 permit 10
R1(config-route-map)# match ip address NAT-ACL
R1(config-route-map)# match interface GigabitEthernet0/1
R1(config)# ip nat inside source route-map NAT-WAN1 interface Gi0/1 overload

! ═══════ TIMEOUT & GIỚI HẠN ═══════
R1(config)# ip nat translation timeout 3600
R1(config)# ip nat translation udp-timeout 300
R1(config)# ip nat translation max-entries 10000
R1(config)# ip nat translation max-entries per-host 300

! ═══════ ALG ═══════
R1(config)# no ip nat service sip tcp port 5060      ! tắt SIP ALG nếu gây lỗi
R1(config)# no ip nat service sip udp port 5060

! ═══════ KIỂM TRA ═══════
R1# show ip nat translations
R1# show ip nat translations verbose
R1# show ip nat statistics
R1# clear ip nat translation *
R1# debug ip nat
R1# undebug all
```

| Lệnh | Lưu ý |
|---|---|
| `ip nat inside source static tcp <local> <port> <global> <port>` | Port forwarding — an toàn hơn static toàn IP |
| `deny` trong NAT-ACL | Nghĩa là **"không NAT"**, không phải "chặn" |
| `route-map` + `match interface` | ⭐ Bắt buộc cho dual-WAN |
| `max-entries per-host` | Chống một máy chiếm hết bảng NAT |
| `no ip nat service sip` | Thử khi VoIP qua NAT bị lỗi một chiều |
| `clear ip nat translation *` | ⚠️ Ngắt mọi kết nối đang mở |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat statistics
Total active translations: 847 (2 static, 845 dynamic; 845 extended)
Peak translations: 1203, occurred 02:14:33 ago
Outside interfaces:
  GigabitEthernet0/1, GigabitEthernet0/2
Inside interfaces:
  GigabitEthernet0/0
Hits: 184723  Misses: 412
CEF Translated packets: 184311, CEF Punted packets: 412
Expired translations: 9841
Dynamic mappings:
-- Inside Source
[Id: 1] route-map NAT-WAN1 interface GigabitEthernet0/1 refcount 621
[Id: 2] route-map NAT-WAN2 interface GigabitEthernet0/2 refcount 224
```

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `Outside/Inside interfaces` | Đã khai hướng chưa | **Trống** → quên `ip nat inside/outside` |
| `Total active translations` | Số entry hiện tại | Gần giới hạn thiết bị → nghẽn |
| `Peak translations` | Đỉnh | Dùng để sizing |
| `Hits` / `Misses` | Gói được NAT / cần tạo entry mới | `Misses` tăng nhanh → bảng đầy |
| `CEF Punted packets` | Gói phải nhờ CPU xử lý | Cao → CPU router tăng |
| `refcount` mỗi mapping | Số entry của mapping đó | Thấy traffic chia 2 WAN thế nào |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| NAT không chạy, bảng rỗng | Quên `ip nat inside/outside` | `show ip nat statistics` — dòng interfaces | Khai hướng |
| `Hits: 0` dù có traffic | ACL/route-map không khớp | `show access-lists` xem counter | Sửa ACL |
| **VPN không lên** sau khi bật NAT | Traffic VPN bị NAT | `show ip nat translations \| include <peer>` | `deny` traffic VPN trong NAT-ACL |
| Server nội bộ không vào được từ ngoài | Thiếu static NAT, hoặc **ACL chặn IP public** | `show ip nat translations`, `show access-lists` | Thêm static + sửa ACL khớp IP **public** |
| Failover WAN xong vẫn mất mạng | Entry NAT cũ còn IP của WAN chết | `show ip nat translations` | `clear ip nat translation *` |
| Mạng chậm giờ cao điểm | **Bảng NAT đầy** | `show ip nat statistics` — `Misses` tăng | Giảm timeout, `max-entries per-host` |
| VoIP một chiều có tiếng | **SIP ALG** làm hỏng SDP | `show run \| include nat service` | `no ip nat service sip` |
| FTP kết nối được nhưng không liệt kê file | FTP active qua NAT | — | Dùng FTP **passive**, hoặc bật ALG |
| Một máy chiếm hết bảng NAT | P2P/torrent mở hàng nghìn kết nối | `show ip nat translations \| count <ip>` | `max-entries per-host` |

---

## 11. LAB

🧪 **LAB 32 — NAT nâng cao** → [`../labs/lab32-nat-nang-cao.md`](../labs/lab32-nat-nang-cao.md)

Yêu cầu tối thiểu:

- PAT cho LAN ra "Internet", verify bảng NAT có port global khác nhau giữa 2 PC
- **Port forwarding** cho một web server nội bộ; truy cập được từ "Internet"
- ACL trên interface outside chặn mọi thứ trừ port 443 → chứng minh ACL khớp **IP public**
- Dual-WAN với route-map, `shutdown` WAN1 → quan sát NAT chuyển sang WAN2
- **BREAK bắt buộc:** (1) quên `clear ip nat translation` sau failover → kết nối cũ chết;
  (2) viết ACL outside khớp **IP private** → không có tác dụng;
  (3) bỏ dòng `deny` VPN trong NAT-ACL → quan sát entry NAT của traffic nội bộ

## 12. Challenge

1. Bạn viết ACL trên interface outside chiều `in` để chỉ cho phép HTTPS tới web server.
   ACL phải khớp IP nào — `10.0.50.20` hay `203.0.113.5`? Vì sao?
2. Dual-WAN, cả hai đều `ip nat outside`, chỉ dùng một `ip nat inside source list 1
   interface Gi0/1 overload`. Chuyện gì xảy ra khi traffic đi ra Gi0/2?
3. VPN site-to-site không lên. `show ip nat translations` có dòng với IP của peer.
   Nguyên nhân? Sửa thế nào?
4. Bảng NAT có 9800/10000 entry, một IP nội bộ chiếm 7000. Nêu nguyên nhân và 2 cách xử lý.

<details>
<summary>Đáp án</summary>

**1.** Khớp **`203.0.113.5`** (IP public).

Vì theo thứ tự xử lý gói đi **vào**: `ACL inbound trên outside` chạy **TRƯỚC** NAT.
Lúc đó gói vẫn mang địa chỉ đích là IP public — NAT ngược chưa xảy ra.

```text
Gói vào Gi0/1:  Dst = 203.0.113.5:443   ← ACL thấy cái này
Sau NAT:        Dst = 10.0.50.20:443    ← ACL đã chạy xong rồi
```

Viết ACL khớp `10.0.50.20` ở vị trí này sẽ **không bao giờ khớp** — ACL im lặng không
có tác dụng. Đây là lỗi rất phổ biến.

**2.** Traffic ra Gi0/2 sẽ **không được NAT** — nó rời router mang **IP private**
`10.0.x.x`. ISP2 nhận gói có source là IP private → **vứt bỏ ngay**.

Triệu chứng: failover sang WAN2 thì mất Internet hoàn toàn, dù interface up và
route đã chuyển.

Sửa: dùng **route-map với `match interface`** cho từng WAN như mục 3.

**3.** Nguyên nhân: **traffic đi VPN đang bị NAT**.

Khi gói từ `10.0.0.5` tới `10.1.0.5` (bên kia tunnel) bị NAT thành `203.0.113.5`,
nó **không còn khớp crypto ACL** của tunnel (vốn định nghĩa `10.0.0.0/24 ↔ 10.1.0.0/24`)
→ không được mã hoá → gửi thẳng ra Internet → chết.

Sửa:

```cisco
ip access-list extended NAT-ACL
 deny   ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255    ! ĐẶT TRƯỚC
 permit ip 10.0.0.0 0.0.0.255 any
```

Rồi `clear ip nat translation *` để xoá entry sai đã tạo.

**4.** Nguyên nhân: một máy mở **hàng nghìn kết nối đồng thời** — gần như chắc chắn là
**P2P/torrent**, hoặc máy nhiễm malware đang quét mạng.

Hai cách xử lý:

| Cách | Lệnh / hành động |
|---|---|
| **Giới hạn kỹ thuật** | `ip nat translation max-entries per-host 300` — một máy không chiếm quá 300 entry |
| **Xử lý gốc** | Tìm máy đó (`show ip nat translations \| include 10.0.x.x`), kiểm tra nó đang chạy gì; chặn ứng dụng bằng ACL hoặc chính sách |

Kết hợp thêm: giảm `ip nat translation timeout` để entry cũ được giải phóng nhanh hơn.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Thứ tự NAT vs routing 2 chiều · timeout mặc định · ALG là gì | ⬜ |
| **L2** Explain | Giải thích vì sao ACL outside khớp IP public | ⬜ |
| **L3** Configure | Port forwarding + loại trừ VPN + dual-WAN route-map | ⬜ |
| **L4** Troubleshoot | VPN không lên do NAT → tìm và sửa | ⬜ |
| **L5** Design | Thiết kế NAT cho công ty dual-WAN, 2 VPN site, 3 server public | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ Gói **đi ra**: routing → **NAT**. Gói **đi vào**: **NAT** → routing
- ⭐ ACL trên **outside inbound** thấy **IP public**; ACL trên **inside** thấy IP private
- **Port forwarding theo port** an toàn hơn static NAT toàn IP
- ⭐ Traffic VPN **phải được `deny`** trong NAT-ACL — `deny` ở đây nghĩa là "không NAT"
- **Dual-WAN cần route-map** với `match interface`
- Failover WAN → phải `clear ip nat translation *`
- NAT timeout TCP mặc định **24 giờ** — giảm khi bảng đầy
- **ALG**: FTP active, SIP, IPsec AH — NAT phá vỡ giao thức nhúng IP trong payload

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip nat inside source static tcp <l> <p> <g> <p>` | Port forwarding |
| `deny ip <local> <remote>` trong NAT-ACL | Loại trừ VPN |
| `ip nat inside source route-map X interface Y overload` | Dual-WAN |
| `show ip nat statistics` | ⭐ Hits/Misses, đã khai hướng chưa |
| `clear ip nat translation *` | Sau failover WAN |
| `ip nat translation max-entries per-host N` | Chống một máy chiếm hết bảng |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| ACL outside khớp IP private | ACL **không bao giờ khớp**, im lặng vô dụng |
| Không loại trừ traffic VPN | **Tunnel không lên** |
| Dual-WAN dùng một quy tắc NAT | Traffic ra WAN2 mang IP private, bị ISP vứt |
| Failover xong không clear NAT | Kết nối cũ chết, "phải đợi vài phút" |
| Static NAT toàn IP cho server | Mở **mọi port** ra Internet |
| Để SIP ALG khi VoIP lỗi | Thường ALG là thủ phạm, không phải cứu tinh |
| Không giám sát bảng NAT | "Mạng chậm giờ cao điểm" không rõ nguyên nhân |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 32 với đủ 3 lỗi BREAK.
2. Vẽ sơ đồ thứ tự xử lý gói đi ra và đi vào, không nhìn lesson.
3. Trên router công ty (nếu có quyền): `show ip nat statistics` — ghi lại
   `Total active translations` và `Peak`. Bảng NAT đang dùng bao nhiêu %?

```markdown
- [YYYY-MM-DD] Lesson 27 — NAT nâng cao: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Port forwarding, 4 thuật ngữ, `overload`, đọc bảng NAT |
| 🔧 **Engineer** | Thứ tự NAT/routing/ACL; route-map cho dual-WAN; loại trừ VPN |
| 🏭 **Production** | Bảng NAT đầy = "chậm giờ cao điểm"; clear NAT sau failover; SIP ALG hay là thủ phạm |

### 🔗 Liên kết

- ⬅️ [Lesson 26 — DNS doanh nghiệp](./lesson-26-dns-doanh-nghiep.md)
- 📚 Nền tảng: [Lesson 09 — NAT](../00-foundation/lesson-09-nat-private-public.md)
- ➡️ [Lesson 28 — NTP, Syslog, SNMP, QoS](./lesson-28-ntp-syslog-snmp-qos.md)
- 🔜 NAT + IPsec: [Lesson 40](../07-wan-vpn/README.md)
