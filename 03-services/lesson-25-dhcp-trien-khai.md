# LESSON 25 — DHCP: triển khai & vận hành

> 📦 **Phase 0 đã dạy gì — lesson này thêm gì**
>
> | [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md) *(khái niệm)* | Lesson này *(triển khai)* |
> |---|---|
> | DORA là gì, địa chỉ từng bước | **DHCP option** chi tiết, cách client dùng chúng |
> | `ip helper-address` cơ bản | Relay nhiều server, nhiều VLAN, `giaddr` sâu |
> | Pool đơn giản | **Reservation**, lease tuning, nhiều pool, sizing |
> | — | **DHCPv6** cơ bản · **DHCP snooping** liên hệ · debug thật |

| | |
|---|---|
| **Phase** | 3 — Services |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md), [Lesson 14](../01-switching/lesson-14-inter-vlan-routing.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Thiết kế pool DHCP đúng kích thước và lease phù hợp từng loại mạng
- [ ] Cấu hình reservation theo MAC, hiểu `client-identifier`
- [ ] Triển khai relay tới **nhiều** server, hiểu `giaddr` quyết định pool nào
- [ ] Biết các **DHCP option** quan trọng và khi nào cần chúng
- [ ] Troubleshoot DHCP bằng `debug`, không đoán mò

## 2. Prerequisite

- DORA, `Src IP = 0.0.0.0`, vì sao cần relay *(Lesson 08)*
- SVI, inter-VLAN routing *(Lesson 14)*

---

## 3. Concept

### DHCP Option — thứ Phase 0 chưa nói

DHCP không chỉ cấp IP. Nó cấp cả một **bộ cấu hình** qua các "option":

| Option | Tên | Cấp gì | Lệnh IOS |
|:---:|---|---|---|
| **1** | Subnet Mask | Mask | *(từ `network`)* |
| **3** | Router | **Default gateway** | `default-router` |
| **6** | DNS Server | DNS | `dns-server` |
| **15** | Domain Name | Tên miền | `domain-name` |
| **42** | NTP Server | NTP | `option 42 ip <ip>` |
| **51** | Lease Time | Thời hạn thuê | `lease` |
| **66** | TFTP Server | Máy chủ boot | `option 66 ascii <host>` |
| **67** | Bootfile | File boot | `option 67 ascii <file>` |
| **150** | TFTP (Cisco) | Config cho **IP phone** | `option 150 ip <ip>` |

> 🏭 **Option 150** là thứ bạn sẽ gặp ngay khi công ty triển khai IP phone —
> điện thoại dùng nó để tải file cấu hình từ server. Thiếu option này, phone
> có IP nhưng không đăng ký được.

### Lease time — chọn thế nào

| Loại mạng | Lease khuyến nghị | Vì sao |
|---|---|---|
| Văn phòng cố định | **8 giờ – 1 ngày** | Máy ở nguyên chỗ, ít quay vòng |
| Wi-Fi khách | **1–2 giờ** | Khách đến rồi đi, cần trả IP nhanh |
| Hội thảo / sự kiện | **15–30 phút** | Mật độ cao, IP phải quay vòng liên tục |
| Server, máy in | **Reservation** *(vô thời hạn thực tế)* | IP phải ổn định |

> 🔑 Nguyên tắc: **lease dài = ổn định nhưng phí IP; lease ngắn = quay vòng nhanh
> nhưng tăng traffic DHCP.** Cân theo tỷ lệ `số thiết bị / số IP khả dụng`.

### Sizing pool — tính thế nào

```text
Số IP cần = (số thiết bị cao điểm) × 1.3  +  số IP tĩnh/reservation

Ví dụ: 180 máy, cao điểm 200, có 15 server/máy in tĩnh
  → 200 × 1.3 + 15 = 275 IP  →  cần /24 (254) là CHẬT  →  nên dùng /23
```

### Reservation — ba cách

```cisco
! Cách 1 — pool riêng cho một host (cổ điển, rõ ràng)
ip dhcp pool PRINTER-TANG1
 host 10.0.10.20 255.255.255.0
 client-identifier 0100.1a2b.3c4d.5e
 default-router 10.0.10.1

! Cách 2 — dùng hardware-address (một số IOS)
ip dhcp pool CAMERA-01
 host 10.0.70.11 255.255.255.0
 hardware-address 001a.2b3c.4d5e
```

> ⚠️ **`client-identifier` ≠ MAC address.** Nó là `01` (loại Ethernet) **cộng** MAC.
> MAC `001a.2b3c.4d5e` → client-identifier `0100.1a2b.3c4d.5e`.
> Gõ nhầm thành MAC thuần là reservation **không hoạt động** và không báo lỗi.

### Relay nhiều server — `giaddr` làm gì

```cisco
R1(config)# interface vlan 20
R1(config-if)# ip helper-address 10.0.10.50
R1(config-if)# ip helper-address 10.0.10.51     ! server dự phòng
```

Router gửi gói Discover tới **cả hai** server. Mỗi server nhìn **`giaddr`**
(= IP của SVI nhận gói) để biết cấp IP từ pool nào.

```text
giaddr = 10.0.20.1  →  server biết client ở subnet 10.0.20.0/24
                    →  cấp IP từ pool của subnet đó
```

> ⚠️ `ip helper-address` **không chỉ** chuyển tiếp DHCP. Mặc định nó relay **8 UDP port**:
> DHCP (67/68), **TFTP (69)**, **DNS (53)**, Time (37), NetBIOS (137/138), TACACS (49).
>
> Thường vô hại, nhưng nếu cần chỉ DHCP:
> ```cisco
> R1(config)# no ip forward-protocol udp tftp
> R1(config)# no ip forward-protocol udp domain
> ```

---

## 4. Why?

> **Vì sao không cho mỗi VLAN một DHCP server riêng?**

| Tập trung (1 server + relay) | Phân tán (mỗi VLAN 1 server) |
|---|---|
| ✅ Một chỗ quản lý, một chỗ xem log | ❌ 10 VLAN = 10 nơi phải sửa |
| ✅ Đổi DNS cho cả công ty = sửa 1 dòng | ❌ Sửa 10 lần |
| ✅ Dễ backup, dễ audit | ❌ Dễ sót |
| ⚠️ Server chết = cả công ty không có IP | ✅ Hỏng một chỗ chỉ ảnh hưởng một VLAN |

> 🔧 Thực tế: **tập trung + 2 server dự phòng** (hai `ip helper-address`).
> Vừa dễ quản lý vừa có HA.

> **Vì sao router Cisco làm DHCP server được nhưng ít ai dùng?**

| Router làm DHCP | Server chuyên dụng (Windows/Linux/NetBox) |
|---|---|
| Tiện cho lab, chi nhánh nhỏ | ✅ Giao diện quản lý, báo cáo |
| ❌ Không có HA thật | ✅ DHCP failover |
| ❌ Khó audit "ai từng dùng IP nào" | ✅ Log đầy đủ |
| ❌ Tốn CPU router | ✅ Tách bạch vai trò |

> 🏭 Quy tắc thực tế: **chi nhánh nhỏ → router làm DHCP. Trụ sở → server chuyên dụng + relay.**

---

## 5. How does it work? — DHCP qua relay, chi tiết

```text
Client (VLAN 20)          R1 (SVI 10.0.20.1)         Server (10.0.10.50)

1. DISCOVER broadcast
   Src 0.0.0.0:68
   Dst 255.255.255.255:67
        ─────────────────▶
2.                        Nhận trên SVI VLAN 20
                          ĐIỀN giaddr = 10.0.20.1
                          Đổi thành UNICAST
                          Src 10.0.20.1:67
                          Dst 10.0.10.50:67
                                ──────────────────▶
3.                                                 Đọc giaddr → chọn pool
                                                   10.0.20.0/24
                                                   Tạo OFFER
                                ◀──────────────────
4. Gửi xuống client
        ◀─────────────────
5-8. REQUEST / ACK đi cùng đường
```

> 🔑 Ba điều quyết định relay chạy đúng:
> 1. `ip helper-address` đặt trên **interface phía client** *(SVI của VLAN đó)*
> 2. Server có **pool khớp với `giaddr`**
> 3. Server có **route về** subnet của client *(để gửi reply)* — rất hay bị quên

---

## 6. Packet Flow — DHCPv6 khác gì

| | **DHCPv4** | **DHCPv6** |
|---|---|---|
| Port | 67 / 68 | **546 / 547** |
| Địa chỉ | Broadcast `255.255.255.255` | Multicast `ff02::1:2` |
| Bốn bước | DORA | **SOLICIT → ADVERTISE → REQUEST → REPLY** |
| Có cần không | Gần như luôn cần | ⚠️ Thường **không** — SLAAC đủ |

| Chế độ DHCPv6 | Cấp gì |
|---|---|
| **Stateless** | Chỉ cấp DNS, domain name. Địa chỉ do **SLAAC** |
| **Stateful** | Cấp cả địa chỉ như DHCPv4 |

> 💡 Ở CCNA chỉ cần biết DHCPv6 tồn tại và phân biệt stateless/stateful.
> Chi tiết ở [Phase 4 — IPv6](../04-ipv6/README.md), lesson 30.

---

## 7. Real-world Example

🏭 **Cấu hình DHCP cho một văn phòng 5 VLAN**

```cisco
! Loại trừ TRƯỚC khi tạo pool
ip dhcp excluded-address 10.0.10.1 10.0.10.49
ip dhcp excluded-address 10.0.20.1 10.0.20.49
ip dhcp excluded-address 10.0.90.1 10.0.90.49

! VLAN 10 — nhân viên
ip dhcp pool VLAN10-NHANVIEN
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 10.0.50.10 10.0.50.11
 domain-name cty.local
 lease 0 8 0

! VLAN 60 — IP phone (cần option 150)
ip dhcp pool VLAN60-VOICE
 network 10.0.60.0 255.255.255.0
 default-router 10.0.60.1
 option 150 ip 10.0.50.20
 lease 7 0 0

! VLAN 90 — Wi-Fi khách, lease ngắn
ip dhcp pool VLAN90-GUEST
 network 10.0.90.0 255.255.255.0
 default-router 10.0.90.1
 dns-server 8.8.8.8 1.1.1.1
 lease 0 2 0
```

Ba quyết định thiết kế trong đoạn này:

| Quyết định | Vì sao |
|---|---|
| Exclude `.1` – `.49` | Chừa chỗ cho gateway, server, máy in tĩnh *(theo quy ước Lesson 07)* |
| Guest dùng **DNS công cộng** | Không cho khách phân giải được tên nội bộ |
| Voice lease **7 ngày** | Điện thoại cố định, đổi IP gây rớt đăng ký |

🏭 **Lỗi thật: DHCP chạy nhưng server không reply được**

Relay cấu hình đúng, `debug ip dhcp server packet` trên router thấy gói đi ra,
nhưng không có gì về. Nguyên nhân: **server không có route về subnet của client**.

Server nằm ở `10.0.50.0/24`, client ở `10.0.20.0/24`. Server gửi reply về `giaddr`
`10.0.20.1` — nếu bảng định tuyến của server không biết đường tới đó, gói chết.

> 🔧 Phản xạ: khi relay không chạy, kiểm tra **route hai chiều**, không chỉ cấu hình relay.

🏭 **Pool sắp hết — sự cố chờ xảy ra**

```cisco
R1# show ip dhcp pool | include Leased|Total
 Total addresses                : 254
 Leased addresses               : 241
```

241/254 — còn 13 IP. Một buổi sáng đông người là hết. Triệu chứng: *"một số máy
không vào được mạng, bật tắt lại thì được"*.

> 🔧 Theo dõi `Leased / Total` như một chỉ số giám sát. Vượt **80%** là lúc mở rộng.

---

## 8. Cisco CLI

```cisco
! ═══════ POOL ═══════
R1(config)# ip dhcp excluded-address 10.0.10.1 10.0.10.49
R1(config)# ip dhcp pool VLAN10
R1(dhcp-config)# network 10.0.10.0 255.255.255.0
R1(dhcp-config)# default-router 10.0.10.1
R1(dhcp-config)# dns-server 10.0.50.10 10.0.50.11
R1(dhcp-config)# domain-name cty.local
R1(dhcp-config)# lease 0 8 0                  ! ngày giờ phút
R1(dhcp-config)# option 150 ip 10.0.50.20     ! TFTP cho IP phone
R1(dhcp-config)# option 42 ip 10.0.50.30      ! NTP server

! ═══════ RESERVATION ═══════
R1(config)# ip dhcp pool PRINTER
R1(dhcp-config)# host 10.0.10.20 255.255.255.0
R1(dhcp-config)# client-identifier 0100.1a2b.3c4d.5e
R1(dhcp-config)# default-router 10.0.10.1

! ═══════ RELAY ═══════
R1(config)# interface vlan 20
R1(config-if)# ip helper-address 10.0.50.10
R1(config-if)# ip helper-address 10.0.50.11

! Giới hạn protocol được relay
R1(config)# no ip forward-protocol udp tftp
R1(config)# no ip forward-protocol udp domain

! ═══════ ROUTER LÀM DHCP CLIENT (nhận IP từ ISP) ═══════
R1(config-if)# ip address dhcp

! ═══════ KIỂM TRA ═══════
R1# show ip dhcp binding
R1# show ip dhcp pool
R1# show ip dhcp conflict
R1# show ip dhcp server statistics
R1# clear ip dhcp binding *
R1# clear ip dhcp conflict *

! ═══════ DEBUG ═══════
R1# debug ip dhcp server events
R1# debug ip dhcp server packet
R1# undebug all
```

| Lệnh | Lưu ý |
|---|---|
| `ip dhcp excluded-address` | ⚠️ Khai **trước** khi tạo pool |
| `lease <ngày> <giờ> <phút>` | `lease infinite` cho vô thời hạn |
| `client-identifier` | `01` + MAC, **không phải** MAC thuần |
| `option 150 ip` | Bắt buộc cho IP phone Cisco |
| `show ip dhcp conflict` | IP bị xung đột — router phát hiện qua ping trước khi cấp |
| `debug ip dhcp server packet` | ⭐ Thấy từng gói DORA — mạnh nhất khi debug |

> **Khác biệt platform:** NX-OS cần `feature dhcp` + `service dhcp`, và relay dùng
> `ip dhcp relay address <ip>` thay cho `ip helper-address`.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp pool
Pool VLAN10 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 87
 Pending event                  : none
 1 subnet is currently in the pool
 Current index    IP address range             Leased addresses
 10.0.10.137      10.0.10.1   - 10.0.10.254    87
```

| Field | Ý nghĩa | Ngưỡng cảnh báo |
|---|---|---|
| `Leased / Total` | Mức sử dụng pool | **> 80%** → mở rộng |
| `Current index` | IP tiếp theo sẽ cấp | |
| `Pending event` | Có sự kiện đang chờ | |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp server statistics
Address pools                 3
Automatic bindings            87
Manual bindings               4
Expired bindings              12
Message                       Received
BOOTREQUEST                   0
DHCPDISCOVER                  142
DHCPREQUEST                   131
DHCPDECLINE                   0
DHCPRELEASE                   8
Message                       Sent
DHCPOFFER                     142
DHCPACK                       131
DHCPNAK                       3
```

| Chỉ số | Bất thường khi |
|---|---|
| `DHCPDECLINE` > 0 | Client phát hiện IP **đã bị dùng** → nghi xung đột, hoặc có rogue |
| `DHCPNAK` cao | Client xin IP không hợp lệ cho subnet nó đang ở → thường do đổi VLAN |
| `DISCOVER` ≫ `ACK` | Nhiều client xin mà không nhận được → pool hết, hoặc relay lỗi |

```text
# output điển hình — tự verify trên lab của bạn
R1# debug ip dhcp server packet
DHCPD: DHCPDISCOVER received from client 0100.1a2b.3c4d.5e on interface Vlan20.
DHCPD: Sending DHCPOFFER to client 0100.1a2b.3c4d.5e (10.0.20.57).
DHCPD: DHCPREQUEST received from client 0100.1a2b.3c4d.5e.
DHCPD: Sending DHCPACK to client 0100.1a2b.3c4d.5e (10.0.20.57).
```

> 🔑 Nhìn đủ 4 dòng DORA là biết DHCP chạy đúng. Thiếu dòng nào thì vấn đề nằm ngay ở bước đó.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Máy nhận `169.254.x.x` | Không tới được DHCP | `debug ip dhcp server packet` | Kiểm tra theo thứ tự: cáp → VLAN port → helper → pool |
| Chỉ thấy `DISCOVER`, không có `OFFER` | Pool hết, hoặc `giaddr` không khớp pool nào | `show ip dhcp pool` | Mở rộng pool / sửa pool cho đúng subnet |
| Có `OFFER` nhưng không có `ACK` | Có **nhiều DHCP server**, client chọn cái khác | Wireshark lọc `dhcp`, xem Src của OFFER | Tìm **rogue DHCP** → DHCP Snooping *(Lesson 37)* |
| Relay không chạy | `helper-address` đặt sai interface | `show run interface vlan X` | Đặt trên SVI **phía client** |
| Gói đi ra server mà không có reply | **Server không có route** về subnet client | `ping giaddr` từ server | Thêm route trên server |
| Reservation không hoạt động | Dùng MAC thuần thay `client-identifier` | `show run \| section dhcp pool` | `01` + MAC |
| IP phone có IP nhưng không đăng ký | Thiếu **option 150** | `show run \| include option 150` | Thêm option |
| `DHCPDECLINE` tăng | Xung đột IP | `show ip dhcp conflict` | `clear ip dhcp conflict *`, kiểm tra IP tĩnh |
| Máy đổi VLAN rồi mất mạng | Giữ lease cũ của subnet cũ | — | `ipconfig /release` + `/renew` |

---

## 11. LAB

🧪 **LAB 30 — DHCP server + relay + reservation** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- L3 switch làm DHCP server cho VLAN 10, **relay** cho VLAN 20 tới một server riêng
- Reservation cho một "máy in" theo MAC — verify bằng `show ip dhcp binding` thấy `Manual`
- Bắt trọn DORA bằng Wireshark; chỉ ra `giaddr` trong gói đã relay
- Đặt lease 2 phút, quan sát client gia hạn ở mốc **50%**
- **BREAK bắt buộc:** (1) xoá `ip helper-address`; (2) tạo pool với subnet **không khớp**
  `giaddr`; (3) dùng MAC thuần làm `client-identifier`; (4) exclude thiếu → DHCP cấp
  trùng IP gateway

## 12. Challenge

1. Công ty 400 máy, pool `/24`, lease 8 ngày. Nêu 2 vấn đề và cách sửa.
2. `debug` thấy `DHCPDISCOVER` và `DHCPOFFER` nhưng client vẫn không có IP.
   Nêu 2 nguyên nhân.
3. Bạn relay tới 2 server. Client nhận được **2 OFFER**. Nó chọn cái nào?
   Server còn lại có biết không?
4. Máy in reservation `10.0.10.20` nhưng nhận được `10.0.10.57`. Nêu 3 nguyên nhân.

<details>
<summary>Đáp án</summary>

**1.** Hai vấn đề:

| Vấn đề | Chi tiết | Cách sửa |
|---|---|---|
| **Pool quá nhỏ** | `/24` = 254 IP cho 400 máy | Chia thành 2 VLAN `/24`, **không** mở rộng thành `/23` *(broadcast domain 400 host quá lớn)* |
| **Lease quá dài** | Máy rời đi vẫn giữ IP 8 ngày | Giảm xuống 8 giờ – 1 ngày |

**2.** Hai nguyên nhân:

| Nguyên nhân | Dấu hiệu |
|---|---|
| Client chọn **OFFER của server khác** (rogue DHCP) | Wireshark thấy 2 OFFER, Src IP khác nhau |
| Gói **REQUEST hoặc ACK** không về được client — thường do relay một chiều, hoặc firewall | `debug` thấy OFFER gửi đi nhưng không có REQUEST nhận về |

**3.** Client thường chọn **OFFER đến trước**. Server còn lại **có biết** — vì bước
**REQUEST là broadcast** (hoặc được relay tới cả hai), và trong đó có trường
`Server Identifier` chỉ rõ client chọn ai.

Server không được chọn sẽ **giải phóng IP nó đã tạm giữ**. Đây chính là lý do
REQUEST phải broadcast chứ không unicast *(đã nói ở Lesson 08)*.

**4.** Ba nguyên nhân:

| # | Nguyên nhân | Kiểm chứng |
|:---:|---|---|
| 1 | `client-identifier` sai — dùng MAC thuần thay vì `01`+MAC | `show run \| section PRINTER` |
| 2 | MAC khai sai *(máy in có nhiều interface: LAN, Wi-Fi)* | So với `show ip dhcp binding` xem MAC thật |
| 3 | Máy in **vẫn giữ lease cũ** chưa hết hạn | Reboot máy in, hoặc `clear ip dhcp binding 10.0.10.57` |

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Option 3/6/51/150 · port DHCPv6 · `client-identifier` là gì | ⬜ |
| **L2** Explain | Giải thích `giaddr` quyết định pool nào | ⬜ |
| **L3** Configure | Pool 3 VLAN + reservation + relay 2 server | ⬜ |
| **L4** Troubleshoot | Chỉ có DISCOVER không có OFFER → tìm nguyên nhân | ⬜ |
| **L5** Design | Thiết kế DHCP cho công ty 5 VLAN: pool size, lease, option | ⬜ |

## 14. Summary

**Key concepts**

- Option quan trọng: **3** (gateway) · **6** (DNS) · **15** (domain) · **51** (lease) · **150** (TFTP cho IP phone)
- Lease: văn phòng **8h–1 ngày** · guest **1–2h** · voice **7 ngày** · server **reservation**
- Sizing: `thiết bị cao điểm × 1.3 + số IP tĩnh`
- ⭐ **`client-identifier` = `01` + MAC**, không phải MAC thuần
- ⭐ **`giaddr`** (IP của SVI nhận gói) cho server biết chọn pool nào
- `ip helper-address` relay **8 UDP port**, không chỉ DHCP
- Server phải có **route về** subnet client, nếu không reply không tới
- Theo dõi `Leased/Total` — vượt **80%** là lúc mở rộng

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip dhcp pool` | ⭐ Pool còn bao nhiêu IP |
| `show ip dhcp binding` | Ai đang giữ IP nào, `Automatic` hay `Manual` |
| `debug ip dhcp server packet` | ⭐ Thấy từng gói DORA |
| `show ip dhcp conflict` | IP bị xung đột |
| `ip helper-address <ip>` | Relay — đặt trên SVI **phía client** |
| `option 150 ip <ip>` | IP phone |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| `client-identifier` dùng MAC thuần | Reservation **im lặng** không chạy |
| Pool subnet không khớp SVI | Client nhận IP khác subnet gateway |
| Quên route về trên server | Relay đi được nhưng reply không về |
| Quên option 150 | IP phone có IP nhưng không đăng ký |
| Lease quá dài trên mạng khách | Pool cạn dù ít người đang dùng |
| Không giám sát `Leased/Total` | Hết IP vào đúng giờ cao điểm |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 30 với đủ 4 lỗi BREAK.
2. `debug ip dhcp server packet` rồi `ipconfig /release` + `/renew` trên PC —
   chụp lại đủ 4 dòng DORA.
3. Tính pool size cho công ty bạn: bao nhiêu thiết bị cao điểm, cần prefix nào.

```markdown
- [YYYY-MM-DD] Lesson 25 — DHCP triển khai: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Option 3/6/51/150, relay, `giaddr`, DHCPv6 4 bước |
| 🔧 **Engineer** | Lease theo loại mạng; reservation đúng cú pháp; 2 helper-address |
| 🏭 **Production** | Giám sát `Leased/Total`; server phải có route về; rogue DHCP → cần snooping |

### 🔗 Liên kết

- ⬅️ [Lesson 24 — OSPF multi-area](../02-routing/lesson-24-ospf-multi-area.md)
- 📚 Nền tảng: [Lesson 08 — DNS & DHCP](../00-foundation/lesson-08-dns-va-dhcp.md)
- ➡️ [Lesson 26 — DNS trong doanh nghiệp](./lesson-26-dns-doanh-nghiep.md)
- 🔜 Chống rogue DHCP: [Lesson 37](../06-security/README.md)
