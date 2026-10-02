# LAB 05 — DHCP server + relay cho 2 VLAN

| | |
|---|---|
| **Phase** | 0 |
| **Lesson liên quan** | [Lesson 08 — DNS · DHCP (DORA)](../00-foundation/lesson-08-dns-va-dhcp.md) |
| **Công cụ** | Cisco Packet Tracer + Wireshark *(hoặc Simulation mode)* |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Cấu hình router làm **DHCP server** cho VLAN cùng subnet
- [ ] Cấu hình **DHCP relay** *(`ip helper-address`)* cho VLAN khác subnet
- [ ] Bắt trọn **4 bước DORA** và chỉ ra `Src = 0.0.0.0` ở Discover
- [ ] Hiểu vì sao relay là **bắt buộc** khi DHCP server không cùng broadcast domain
- [ ] Tự gây & sửa 3 lỗi DHCP phổ biến

## 2. Prerequisite

- [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md) — DORA, lease, relay
- [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md) — broadcast domain
- [LAB 12](lab12-inter-vlan-routing.md) — inter-VLAN routing *(nền tảng)*

---

## 3. Topology

```text
   VLAN 10 (10.0.10.0/24)          VLAN 20 (10.0.20.0/24)
   PC-A1   PC-A2                    PC-B1   PC-B2
     │       │                        │       │
     └───┬───┘                        └───┬───┘
       SW-ACCESS ────── trunk ────── R1 (router-on-a-stick)
                                      │   Gi0/0.10  = 10.0.10.1
                                      │   Gi0/0.20  = 10.0.20.1
                                      │
                                   DHCP server cho CẢ HAI VLAN
```

> 💡 R1 là DHCP server cho VLAN 10 *(cùng subnet nên "tự phục vụ")* và
> cũng phục vụ VLAN 20. Để thấy rõ **relay**, Phần nâng cao tách DHCP server
> sang một thiết bị riêng ở VLAN khác.

## 4. IP Addressing Table

| Device | Interface | IP | Ghi chú |
|---|---|---|---|
| R1 | Gi0/0.10 | `10.0.10.1/24` | GW + DHCP VLAN 10 |
| R1 | Gi0/0.20 | `10.0.20.1/24` | GW + DHCP VLAN 20 |
| SW-ACCESS | — | L2 thuần | Fa0/1-12 → VLAN 10; Fa0/13-23 → VLAN 20; Gi0/1 trunk |
| PC-A1..A2 | Fa0 | **DHCP** | VLAN 10 |
| PC-B1..B2 | Fa0 | **DHCP** | VLAN 20 |
| DNS giả | — | `10.0.10.53` | khai trong pool |

---

## 5. Yêu cầu LAB

- [ ] Cả 4 PC nhận IP đúng VLAN, đúng gateway, đúng DNS
- [ ] `10.0.10.1`–`10.0.10.9` *(và tương tự VLAN 20)* bị **excluded**
- [ ] Bắt DORA bằng Wireshark/Simulation
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Nền: VLAN + router-on-a-stick

```cisco
! ══ SW-ACCESS ══
vlan 10
vlan 20
interface range Fa0/1 - 12
 switchport mode access
 switchport access vlan 10
interface range Fa0/13 - 23
 switchport mode access
 switchport access vlan 20
interface Gi0/1
 switchport mode trunk

! ══ R1 ══
interface Gi0/0
 no shutdown
interface Gi0/0.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
interface Gi0/0.20
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
```

### Bước 2 — DHCP pool

```cisco
R1(config)# ip dhcp excluded-address 10.0.10.1 10.0.10.9
R1(config)# ip dhcp excluded-address 10.0.20.1 10.0.20.9

R1(config)# ip dhcp pool VLAN10
R1(dhcp-config)# network 10.0.10.0 255.255.255.0
R1(dhcp-config)# default-router 10.0.10.1
R1(dhcp-config)# dns-server 10.0.10.53
R1(dhcp-config)# lease 0 12
R1(dhcp-config)# exit

R1(config)# ip dhcp pool VLAN20
R1(dhcp-config)# network 10.0.20.0 255.255.255.0
R1(dhcp-config)# default-router 10.0.20.1
R1(dhcp-config)# dns-server 10.0.10.53
R1(dhcp-config)# lease 0 12
```

> 🔑 **Vì sao VLAN 20 không cần `ip helper-address`?**
> Vì R1 **chính là** DHCP server và có một chân *(Gi0/0.20)* nằm **trong** VLAN 20.
> Router nhận broadcast DHCP trực tiếp trên subinterface đó. Relay chỉ cần khi
> server ở **subnet khác** — xem Phần nâng cao.

### Bước 3 — Lấy IP từ client

Trên mỗi PC: **IP Configuration → DHCP**.

> 🔴 **DỰ ĐOÁN trước:** PC-A1 sẽ nhận IP nào? *(nhớ dải excluded `.1`–`.9`)*

```text
Dự đoán PC-A1: 10.0.10.___
Thực tế:       10.0.10.___
```

### Bước 4 — Bắt DORA

Chuyển sang **Simulation mode**, lọc chỉ DHCP, rồi trên PC-A2 bấm
**renew**. Quan sát 4 gói:

| Bước | Tên gói | Src IP | Dst IP | Src/Dst MAC |
|:---:|---|---|---|---|
| D | Discover | `0.0.0.0` | `255.255.255.255` | PC / broadcast |
| O | Offer | `10.0.10.1` | `255.255.255.255` *(hoặc unicast)* | R1 / PC |
| R | Request | `0.0.0.0` | `255.255.255.255` | PC / broadcast |
| A | ACK | `10.0.10.1` | `255.255.255.255` | R1 / PC |

> 🔑 Chỉ ra cho được: **Discover có `Src = 0.0.0.0`** *(client chưa có IP)* và
> **Request vẫn broadcast** *(báo cho mọi server biết nó chọn ai)*.

### Phần nâng cao — DHCP Relay thật

Tách DHCP server ra một router **R-DHCP** đặt ở VLAN 99 *(subnet khác)*.
Giờ VLAN 10 và 20 **không còn** server trong broadcast domain → cần relay:

```cisco
! Trên R1 — trỏ broadcast DHCP của mỗi VLAN tới server
R1(config)# interface Gi0/0.10
R1(config-subif)# ip helper-address 10.0.99.10
R1(config)# interface Gi0/0.20
R1(config-subif)# ip helper-address 10.0.99.10
```

> 🔑 `ip helper-address` biến broadcast DHCP thành **unicast** gửi tới server,
> và router **nhét subnet của mình** vào trường `giaddr` để server biết cấp từ pool nào.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp binding
IP address       Client-ID/            Lease expiration        Type
                 Hardware address
10.0.10.10       0100.0 a00.0a00.0a    Oct 02 2026 09:14 PM     Automatic
10.0.20.10       0100.0 b00.0b00.0b    Oct 02 2026 09:15 PM     Automatic
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp pool VLAN10
Pool VLAN10 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 2
 Excluded addresses             : 9
 Pending event                  : none
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp conflict
IP address        Detection method   Detection time
(trống nếu không có xung đột)
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | PC-A1 nhận IP | `10.0.10.10`+ *(không phải .1–.9)* | |
| 2 | PC-B1 nhận IP | `10.0.20.10`+ | |
| 3 | PC-A1 gateway | `10.0.10.1` | |
| 4 | PC-A1 ping PC-B1 | ✅ *(qua inter-VLAN)* | |
| 5 | `show ip dhcp binding` | 4 entry | |
| 6 | Discover `Src` | `0.0.0.0` | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Thiếu `ip helper-address` *(phần nâng cao)* ⭐

```cisco
R1(config)# interface Gi0/0.20
R1(config-subif)# no ip helper-address 10.0.99.10
```

PC-B1 bấm renew.

| | |
|---|---|
| PC-B1 nhận được IP không? *(hay `169.254.x.x`?)* | |
| VLAN 10 có bị ảnh hưởng không? Vì sao? | |
| Dùng Simulation: Discover của PC-B1 đi tới đâu rồi dừng? | |
| Vì sao broadcast DHCP **không tự** vượt qua router? | |

### Lỗi 2 — Thiếu `default-router` trong pool

```cisco
R1(config)# ip dhcp pool VLAN10
R1(dhcp-config)# no default-router 10.0.10.1
```

PC-A1 renew *(release trước)*.

| | |
|---|---|
| PC-A1 có nhận IP không? | |
| PC-A1 ping `10.0.10.2` *(cùng VLAN)*: được? | |
| PC-A1 ping `10.0.20.10` *(khác VLAN)*: được? | |
| Giải thích: thiếu gateway thì mất khả năng gì? | |

### Lỗi 3 — Quên excluded → xung đột IP

```cisco
R1(config)# no ip dhcp excluded-address 10.0.10.1 10.0.10.9
! Đặt PC-A2 về IP TĨNH 10.0.10.10 (trùng dải DHCP sẽ cấp)
! Xoá binding rồi cho PC-A1 xin IP mới
R1# clear ip dhcp binding *
```

| | |
|---|---|
| `show ip dhcp conflict` hiện gì? | |
| PC-A1 có thể nhận trúng `10.0.10.10` không? | |
| Khi trùng, ai bị mất mạng? | |
| Vì sao `excluded-address` lại quan trọng với **gateway/server IP tĩnh**? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Pool cấu hình `network 10.0.20.0 255.255.255.0` nhưng SVI VLAN 20 là
   `10.0.20.1/25`. Chuyện gì xảy ra với client?
2. Có **2 DHCP server** cùng phục vụ một VLAN. Client chọn cái nào?
   Làm sao để chúng không cấp trùng IP?
3. Công ty 500 máy, lease 8 ngày, pool `/24`. Vấn đề là gì và sửa thế nào?
4. `ip helper-address` còn chuyển tiếp những dịch vụ UDP nào khác ngoài DHCP?

<details>
<summary>Đáp án</summary>

**1.** Client nhận IP như `10.0.20.150/24`, gateway `10.0.20.1`. Nhưng SVI chỉ `/25`
→ gateway `10.0.20.1` thuộc dải `10.0.20.0/25` *(.0–.127)*. Client `.150` nghĩ mình
cùng subnet `/24` với gateway, nhưng gateway lại ở subnet `/25` khác.

Hậu quả: client `.1`–`.126` hoạt động được; client `.128`–`.254` **không ping được
gateway** *(gateway coi chúng ngoài subnet)*. Lỗi "lúc được lúc không" theo IP được cấp.

Sửa: pool mask phải **khớp** mask của interface → `network 10.0.20.0 255.255.255.128`.

**2.** Client chọn **Offer đến trước** *(thường server gần nhất)*. DHCP không có cơ chế
ưu tiên server "chính".

Chống cấp trùng: **chia pool không chồng nhau** giữa 2 server —
VD server A cấp `.10–.150`, server B cấp `.151–.254`. Hoặc dùng DHCP failover
*(server đồng bộ lease với nhau)*. Nếu để hai server cùng dải, chúng sẽ cấp trùng
vì không biết nhau cấp gì.

**3.** Vấn đề: `/24` chỉ có **254 IP khả dụng**, không đủ cho 500 máy. Lease 8 ngày
càng làm IP "kẹt" lâu — máy tắt vẫn giữ IP 8 ngày.

Sửa:
- Mở rộng subnet: `/23` *(510 host)* hoặc tách VLAN.
- **Giảm lease** xuống 1 ngày *(hoặc 8 giờ cho khách)* → IP quay vòng nhanh.
- Kết hợp cả hai với mạng có nhiều máy di động.

**4.** `ip helper-address` mặc định chuyển tiếp **8 dịch vụ UDP** *(default forwarding)*:
TFTP (69), **DNS (53)**, Time (37), **NetBIOS Name/Datagram (137/138)**,
BOOTP/DHCP (67/68), TACACS (49). Kiểm soát bằng `ip forward-protocol udp <port>`.

> Lưu ý thực tế: điều này có thể vô tình chuyển tiếp cả NetBIOS → nên tắt bớt
> bằng `no ip forward-protocol udp 137` nếu không cần.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — thiếu helper-address ⭐:**

| Quan sát | Giải thích |
|---|---|
| PC-B1 nhận `169.254.x.x` *(APIPA)* | Không server nào trả lời |
| VLAN 10 **vẫn chạy** | Mỗi VLAN độc lập — chỉ VLAN 20 mất relay |
| Discover dừng tại R1, không qua được | Router **không forward broadcast** theo mặc định |

**Cốt lõi:** DHCP Discover là **broadcast lớp 2** *(`255.255.255.255`)*. Router là
ranh giới broadcast domain → **chặn** broadcast. `ip helper-address` là cách bảo router
*"gặp broadcast DHCP thì đổi thành unicast gửi tới server này"*.

**Lỗi 2 — thiếu default-router:**

| Quan sát | Giải thích |
|---|---|
| PC vẫn **nhận IP** | Pool vẫn cấp địa chỉ |
| Ping cùng VLAN: **OK** | Cùng subnet, không cần gateway |
| Ping khác VLAN: **FAIL** | Không có gateway → không biết gửi gói ra ngoài subnet đi đâu |

👉 Thiếu gateway = "mạng nội bộ dùng được, ra ngoài thì không". Triệu chứng kinh điển.

**Lỗi 3 — xung đột IP:**

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp conflict
IP address      Detection method   Detection time
10.0.10.10      Gratuitous ARP     Oct 02 2026 09:20 PM
```

DHCP server trước khi cấp sẽ **ping/ARP** thử IP đó. Nếu có máy tĩnh đang dùng
`10.0.10.10`, server phát hiện xung đột, **đánh dấu** IP đó và cấp IP khác.
Nhưng nếu phát hiện trượt *(máy tĩnh tắt lúc kiểm tra)*, hai máy cùng IP → một máy
mất mạng ngẫu nhiên.

`excluded-address` quan trọng vì **gateway, server, switch** đều dùng IP tĩnh trong
cùng subnet — phải loại chúng khỏi dải DHCP để không bao giờ bị cấp trùng.

### Bảng tổng kết

| Dòng cấu hình | Thiếu thì sao |
|---|---|
| `ip helper-address` *(khi server khác subnet)* | VLAN đó không nhận được IP |
| `default-router` | Nhận IP nhưng không ra được ngoài subnet |
| `excluded-address` | Nguy cơ cấp trùng IP tĩnh |
| `dns-server` | Có mạng nhưng không phân giải tên miền |
| mask pool khớp interface | Một nửa client không ping được gateway |

</details>

---

## 📝 Ghi chú & bài học rút ra

- DORA: gói nào `Src = 0.0.0.0`? Vì sao Request vẫn broadcast? ___
- Lỗi 1 (relay) — tôi hiểu vì sao router chặn broadcast chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
