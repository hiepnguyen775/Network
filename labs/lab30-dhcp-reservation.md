# LAB 30 — DHCP server + relay + reservation

> 📦 **Phase 0 (LAB 05) đã dạy gì — lab này thêm gì:** LAB 05 làm DORA + relay cơ bản.
> Lab này đi sâu: **reservation** *(IP cố định theo MAC)*, **DHCP options**
> *(option 150 cho VoIP, option 66 TFTP)*, và **relay tới nhiều server** *(dự phòng)*.

| | |
|---|---|
| **Phase** | 3 |
| **Lesson liên quan** | [Lesson 25 — DHCP triển khai](../03-services/lesson-25-dhcp-trien-khai.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Cấu hình **reservation**: máy in luôn nhận `10.0.10.50` theo MAC
- [ ] Cấu hình **DHCP option** *(option 150 — TFTP server cho IP phone)*
- [ ] Relay tới **hai** DHCP server để dự phòng
- [ ] Chia pool không chồng nhau giữa 2 server để tránh cấp trùng
- [ ] Tự gây & sửa 3 lỗi DHCP nâng cao

## 2. Prerequisite

- [Lesson 25](../03-services/lesson-25-dhcp-trien-khai.md) — option, reservation, relay
- [LAB 05](lab05-dhcp-server-relay.md) — DORA + relay cơ bản *(làm trước)*

---

## 3. Topology

```text
   VLAN 10 (user + phone + printer)       VLAN 99 (servers)
   PC   PHONE   PRINTER                    DHCP-A 10.0.99.10
     \    |    /                           DHCP-B 10.0.99.11
      SW-ACCESS ─── R1 (relay) ─────────── TFTP   10.0.99.20
                 Gi0/0.10          Gi0/0.99
                 10.0.10.1         10.0.99.1
```

| Thiết bị | Vai trò |
|---|---|
| R1 | Relay *(ip helper tới cả 2 server)* |
| DHCP-A, DHCP-B | Hai DHCP server dự phòng |
| PRINTER | Cần IP cố định *(reservation)* |
| PHONE | Cần option 150 *(TFTP server)* |

## 4. IP Addressing Table

| Device | IP | Ghi chú |
|---|---|---|
| R1 Gi0/0.10 | `10.0.10.1/24` | GW VLAN 10 + relay |
| R1 Gi0/0.99 | `10.0.99.1/24` | GW servers |
| DHCP-A | `10.0.99.10/24` | cấp `.10–.150` |
| DHCP-B | `10.0.99.11/24` | cấp `.151–.250` |
| PRINTER | `10.0.10.50` *(reservation)* | MAC cố định |

---

## 5. Yêu cầu LAB

- [ ] PRINTER **luôn** nhận `10.0.10.50` dù khởi động lại
- [ ] PHONE nhận được option 150 trỏ `10.0.99.20`
- [ ] Tắt DHCP-A → client vẫn nhận IP từ DHCP-B
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Relay tới 2 server

```cisco
R1(config)# interface Gi0/0.10
R1(config-subif)# ip helper-address 10.0.99.10
R1(config-subif)# ip helper-address 10.0.99.11      ! server thứ 2
```

> 🔑 Nhiều `ip helper-address` → relay gửi Discover tới **cả hai** server.
> Client nhận **Offer đến trước**. Đây là cách dự phòng DHCP đơn giản nhất.

### Bước 2 — Pool không chồng nhau (trên IOS DHCP, mô phỏng 2 server)

```cisco
! DHCP-A (dùng R2 hoặc router thứ 2 làm server)
ip dhcp excluded-address 10.0.10.1 10.0.10.9
ip dhcp excluded-address 10.0.10.151 10.0.10.254
ip dhcp pool VLAN10-A
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 10.0.99.20

! DHCP-B — cùng network nhưng EXCLUDE dải của A
ip dhcp excluded-address 10.0.10.1 10.0.10.150
ip dhcp pool VLAN10-B
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 10.0.99.20
```

> ⚠️ Hai server cùng `network` nhưng mỗi cái **exclude** dải của cái kia →
> A cấp `.10–.150`, B cấp `.151–.250`. **Không bao giờ cấp trùng.**

### Bước 3 — Reservation cho máy in ⭐

Lấy MAC của PRINTER *(giả sử `00D0.BA12.3456`)*:

```cisco
! IOS: reservation qua pool host riêng
ip dhcp pool PRINTER-RSV
 host 10.0.10.50 255.255.255.0
 client-identifier 0100.d0ba.1234.56      ! 01 + MAC
 default-router 10.0.10.1
```

> 💡 `client-identifier` = `01` *(loại Ethernet)* + MAC. Hoặc dùng
> `hardware-address 00d0.ba12.3456` tuỳ IOS. Trên Server-PT dùng tab
> **DHCP → Add** với cột MAC.

### Bước 4 — DHCP option 150 cho IP phone

```cisco
ip dhcp pool VLAN10-A
 option 150 ip 10.0.99.20        ! TFTP server cho phone tải config
```

> 🔑 **Option 150** *(Cisco)* / **option 66** *(chuẩn)*: báo IP phone biết
> TFTP server để tải firmware/config. Thiếu nó, phone không boot lên được.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp binding
IP address       Client-ID/            Lease expiration     Type
10.0.10.10       0100.0a00.0a00.0a     Oct 03 2026 09:00    Automatic
10.0.10.50       0100.d0ba.1234.56     Infinite             Manual
```

> 🔑 Để ý `Type = Manual` và `Lease = Infinite` ở dòng printer — đó là reservation.

```text
# output điển hình — tự verify trên lab của bạn
PC> ipconfig /all
   IPv4 Address. . . . . . . . . . . : 10.0.10.10
   Default Gateway . . . . . . . . . : 10.0.10.1
   DNS Servers . . . . . . . . . . . : 10.0.99.20
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | PRINTER nhận `10.0.10.50`, reboot vẫn vậy | ✅ | |
| 2 | `show ip dhcp binding` — printer Type `Manual` | ✅ | |
| 3 | PC nhận IP trong dải `.10–.150` *(từ A)* | ✅ | |
| 4 | Tắt DHCP-A → PC mới nhận `.151+` *(từ B)* | ✅ | |
| 5 | PHONE thấy option 150 = `10.0.99.20` | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Hai server pool chồng nhau ⭐

```cisco
! Bỏ exclude trên DHCP-B → cả hai cùng cấp .10–.250
DHCP-B(config)# no ip dhcp excluded-address 10.0.10.1 10.0.10.150
```

| | |
|---|---|
| Cho nhiều PC xin IP — có máy nào trùng IP không? | |
| `show ip dhcp conflict` trên mỗi server hiện gì? | |
| Vì sao 2 server không biết nhau đã cấp gì? | |
| Cách đúng để 2 server dự phòng mà không trùng là gì? | |

### Lỗi 2 — Reservation sai client-identifier

```cisco
DHCP(config)# ip dhcp pool PRINTER-RSV
DHCP(dhcp-config)# client-identifier 0100.d0ba.1234.99    ! sai 2 ký tự cuối
```

| | |
|---|---|
| PRINTER còn nhận `10.0.10.50` không? | |
| Nó nhận IP gì thay thế? | |
| `01` ở đầu client-identifier nghĩa là gì? | |

### Lỗi 3 — Thiếu option 150, phone không boot

```cisco
DHCP(config)# ip dhcp pool VLAN10-A
DHCP(dhcp-config)# no option 150 ip 10.0.99.20
```

| | |
|---|---|
| PHONE có nhận IP không? | |
| PHONE có **boot/đăng ký** được không? Vì sao? | |
| IP phone cần TFTP server để làm gì? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Công ty muốn mọi máy in *(5 cái)* có IP cố định nhưng vẫn quản lý tập trung qua DHCP.
   Reservation hay IP tĩnh? Vì sao?
2. Hai DHCP server dự phòng kiểu "chia pool" có nhược điểm gì khi một server chết lâu?
3. Phân biệt option 66 và option 150. Khi nào dùng cái nào?
4. Reservation và `excluded-address` — khác nhau thế nào? Khi nào cần cả hai?

<details>
<summary>Đáp án</summary>

**1.** **Reservation.** Lý do:
- IP cố định *(không đổi khi reboot)* → cấu hình "in qua IP" trên máy trạm luôn đúng.
- Vẫn **quản lý tập trung** → đổi gateway/DNS cho máy in chỉ cần sửa trên DHCP server,
  không phải chạm vào từng máy in.
- IP tĩnh trên máy in mất 2 ưu điểm trên và dễ gây xung đột nếu quên exclude.

**2.** Nhược điểm "chia pool": nếu A chết, B **chỉ còn một nửa dải** *(`.151–.250` = 100 IP)*.
Nếu số client > 100, một số máy **không xin được IP** dù B vẫn sống. Chia pool không
phải failover thật — mỗi server chỉ cõng được phần của mình.

Giải pháp tốt hơn: **DHCP failover** *(server đồng bộ lease, có thể cấp toàn dải khi
đối tác chết)* — nhưng IOS DHCP không hỗ trợ; cần Windows Server / ISC DHCP.

**3.**

| Option | Chuẩn | Format | Dùng cho |
|---|---|---|---|
| **66** | RFC chuẩn | **tên** TFTP *(string)* | Cách chuẩn, đa hãng |
| **150** | Cisco | **IP** TFTP *(có thể nhiều IP)* | IP phone Cisco, cho phép dự phòng nhiều TFTP |

Phone Cisco ưu tiên 150; thiết bị đa hãng thường dùng 66. Nhiều triển khai khai **cả hai**.

**4.**

| | Reservation | excluded-address |
|---|---|---|
| Làm gì | **Gán** IP cụ thể cho một MAC | **Loại** IP khỏi dải cấp động |
| Kết quả | Máy đó luôn nhận IP đó | Không máy nào nhận IP đó qua DHCP động |

Cần **cả hai** khi: bạn muốn máy in nhận `.50` *(reservation)* **và** đảm bảo không
máy động nào vô tình nhận `.50` trước đó. Thực tế, reservation thường tự loại IP đó
khỏi pool động, nhưng với gateway/server IP tĩnh *(không qua DHCP)* thì **phải**
`excluded-address` thủ công.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — pool chồng nhau ⭐:** Hai server IOS **không đồng bộ** lease với nhau.
A cấp `.100` cho máy X, B không biết → có thể cấp `.100` cho máy Y → **xung đột IP**.
`show ip dhcp conflict` sẽ hiện IP bị trùng *(phát hiện qua gratuitous ARP)*.
Cách đúng: **chia dải không chồng** *(exclude lẫn nhau)* hoặc dùng DHCP failover thật.

**Lỗi 2 — sai client-identifier:** DHCP khớp reservation theo **client-identifier/MAC
chính xác**. Sai một ký tự → không khớp → printer rơi vào **pool động**, nhận IP bất kỳ
trong dải *(vd `.11`)* thay vì `.50`. `01` ở đầu = **mã loại phần cứng Ethernet (type 1)**
theo RFC — nó đứng trước MAC trong client-identifier.

**Lỗi 3 — thiếu option 150:** Phone **vẫn nhận IP** *(DHCP cơ bản chạy)* nhưng
**không biết TFTP server ở đâu** → không tải được config/firmware → không đăng ký với
CallManager → **không boot lên dùng được**. IP phone tải toàn bộ cấu hình từ TFTP,
nên option 150 là bắt buộc trong môi trường VoIP.

### Bảng tổng kết

| Tính năng | Lệnh | Mục đích |
|---|---|---|
| Reservation | `host` + `client-identifier` | IP cố định theo MAC, quản lý tập trung |
| Option 150/66 | `option 150 ip ...` | TFTP server cho IP phone |
| Relay đa server | nhiều `ip helper-address` | Dự phòng DHCP |
| Chia pool | `excluded-address` lẫn nhau | Tránh cấp trùng khi 2 server |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Reservation khác IP tĩnh thế nào? ___
- Lỗi 1 (pool chồng) — vì sao 2 server IOS không an toàn? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
