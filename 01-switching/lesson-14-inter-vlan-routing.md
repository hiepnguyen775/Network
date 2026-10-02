# LESSON 14 — Inter-VLAN Routing: Router-on-a-Stick & SVI ⭐

> 📌 Lesson 13 dựng **tường** (VLAN). Lesson này làm **cửa**.
> Chia VLAN mà quên inter-VLAN routing là lỗi thiết kế kinh điển.

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 11](./lesson-11-kien-truc-switch.md), [Lesson 13](./lesson-13-vlan-va-trunk.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích vì sao hai VLAN **bắt buộc** cần thiết bị L3 để nói chuyện
- [ ] Cấu hình **Router-on-a-Stick** đầy đủ, hiểu subinterface làm gì
- [ ] Cấu hình **SVI** trên L3 switch, hiểu vì sao nó nhanh hơn
- [ ] Nói được khi nào chọn cách nào — bằng lý do kỹ thuật, không cảm tính
- [ ] Tự tìm được lỗi "ping được gateway của mình nhưng không ping được VLAN khác"

## 2. Prerequisite

- VLAN chia broadcast domain; access vs trunk; native VLAN *(Lesson 13)*
- SVI là gì; `ip routing` phải bật tay *(Lesson 11)*
- Phép AND quyết định cùng/khác subnet; ARP tìm MAC gateway *(Lesson 05)*

---

## 3. Concept

### Vì sao cần inter-VLAN routing

VLAN 10 và VLAN 20 là **hai broadcast domain tách biệt**. PC ở VLAN 10 gửi ARP tìm PC
ở VLAN 20 → switch chỉ flood **trong VLAN 10** → không ai trả lời.

```text
VLAN 10 (10.0.10.0/24)          VLAN 20 (10.0.20.0/24)
   PC-A 10.0.10.5                  PC-B 10.0.20.5
        │                                │
        └────────── SW1 ─────────────────┘
                     ✗
             Không thể nói chuyện
             (hai broadcast domain khác nhau,
              và cũng là hai subnet khác nhau)
```

Cần một thiết bị **có chân ở cả hai VLAN** và biết **route** giữa hai subnet.

### Ba cách triển khai

| Cách | Mô tả | Thực tế |
|---|---|---|
| **Legacy** | Mỗi VLAN một interface router vật lý | ❌ Lỗi thời — tốn port, không scale |
| **Router-on-a-Stick (RoAS)** | **Một** link trunk tới router, chia **subinterface** | Dùng khi chỉ có router + switch L2 |
| **SVI trên L3 switch** | Switch tự route giữa các VLAN | ⭐ **Chuẩn hiện nay** |

### Router-on-a-Stick

```text
                      Router R1
                   ┌──────────────┐
                   │ Gi0/0.10 ─ VLAN 10 ─ 10.0.10.1
                   │ Gi0/0.20 ─ VLAN 20 ─ 10.0.20.1
                   │ Gi0/0.99 ─ VLAN 99 ─ 10.0.99.1
                   └──────┬───────┘
                          │  một link vật lý duy nhất
                       TRUNK (802.1Q)
                          │
                        SW1
                       ╱    ╲
                   VLAN 10  VLAN 20
                    PC-A     PC-B
```

**Subinterface** = interface logic nằm trên một interface vật lý, mỗi cái gắn một VLAN.
Router nhận frame có tag → đọc tag → đẩy vào đúng subinterface → route → gắn tag mới → trả ra.

### SVI trên L3 switch

```text
                    L3 Switch SW1
            ┌─────────────────────────┐
            │  interface Vlan10 ─ 10.0.10.1
            │  interface Vlan20 ─ 10.0.20.1
            │  ip routing  ← BẮT BUỘC
            └──┬───────────────────┬──┘
               │                   │
            VLAN 10             VLAN 20
             PC-A                PC-B
```

Không có link trunk nào bị dùng cho routing — switch route **nội bộ bằng ASIC**.

### So sánh — bảng quyết định

| | **Router-on-a-Stick** | **SVI (L3 switch)** |
|---|---|---|
| Thiết bị | Router + switch L2 | L3 switch |
| Tốc độ route | Qua CPU router, **chậm hơn** | **Wire-speed** (ASIC) |
| Nút cổ chai | ⚠️ **Một link vật lý** chở traffic của mọi VLAN, cả đi lẫn về | Không — route nội bộ |
| Số VLAN hỗ trợ tốt | Ít (< 10 VLAN, traffic thấp) | Nhiều |
| Chi phí | Rẻ hơn | Đắt hơn |
| Tính năng L3 nâng cao | ✅ NAT, VPN, QoS sâu | Hạn chế |
| Dùng khi | Chi nhánh nhỏ, lab, đã có sẵn router | ⭐ **Mọi mạng doanh nghiệp** |

> 🔑 **Nút cổ chai của RoAS là điểm quan trọng nhất của lesson.**
> Traffic từ VLAN 10 sang VLAN 20 phải **đi lên** link trunk rồi **đi xuống** chính link đó.
> Link 1 Gbps thực chất chỉ phục vụ được ~500 Mbps traffic inter-VLAN.
> Càng nhiều VLAN, càng nghẽn.

---

## 4. Why? — nếu không có inter-VLAN routing

| Hậu quả | Thực tế |
|---|---|
| Chia VLAN xong thì **mạng vỡ làm nhiều mảnh** | Kế toán không vào được server, Sales không in được |
| Phải chạy dây riêng cho từng dịch vụ | Quay lại thời chưa có VLAN |
| Không có chỗ đặt ACL | ACL là L3 — không có hop L3 thì không lọc được gì |

> 🔧 Nói cách khác: **VLAN tạo ra vấn đề, inter-VLAN routing giải quyết nó.**
> Hai thứ luôn đi cùng nhau. Và chính vì traffic phải qua L3, bạn **mới có chỗ** đặt
> chính sách — đó là lợi ích chứ không phải phiền toái.

---

## 5. How does it work?

### Router-on-a-Stick — từng bước

```text
1. PC-A (10.0.10.5) muốn gửi tới PC-B (10.0.20.5)
2. Phép AND → khác subnet → gửi cho default gateway 10.0.10.1
3. PC-A ARP tìm MAC của 10.0.10.1
   → Router trả lời bằng MAC của Gi0/0 (subinterface dùng chung MAC vật lý)
4. PC-A gửi frame: Dst MAC = MAC-Router, Dst IP = 10.0.20.5
5. SW1 nhận ở access port VLAN 10 → gắn tag VLAN 10 → đẩy ra trunk
6. R1 nhận frame có tag 10 → đẩy vào Gi0/0.10
7. R1 TRA BẢNG ĐỊNH TUYẾN:
      10.0.20.0/24 là connected trên Gi0/0.20
8. R1 ARP tìm MAC của PC-B trong VLAN 20
9. R1 tạo frame MỚI: Dst MAC = MAC-PC-B, gắn tag VLAN 20, TTL giảm 1
10. Đẩy ra trunk → SW1 gỡ tag → chuyển tới PC-B
```

> ⚠️ Chú ý bước 5 và 10: frame **đi lên rồi đi xuống cùng một sợi dây**. Đó chính là
> nút cổ chai.

### SVI — khác ở chỗ nào

Các bước 1–4 giống hệt. Khác từ bước 5:

```text
5. SW1 nhận frame ở access port VLAN 10
6. Dst MAC = MAC của SVI → switch biết "gói này dành cho chính tôi, cần route"
7. ASIC tra bảng định tuyến NỘI BỘ → VLAN 20
8. Viết lại MAC, giảm TTL, chuyển thẳng ra port của PC-B
```

**Không có frame nào rời khỏi switch.** Toàn bộ xảy ra trong ASIC — đó là lý do
nó nhanh hơn hẳn.

---

## 6. Packet Flow

**PC-A `10.0.10.5` (VLAN 10) → PC-B `10.0.20.5` (VLAN 20)** — dùng SVI.

| Chặng | Src MAC | Dst MAC | Src IP | Dst IP | VLAN tag | TTL |
|---|---|---|---|---|:---:|:---:|
| PC-A → SW1 | MAC-A | **MAC-SVI** | 10.0.10.5 | 10.0.20.5 | 10 *(nội bộ)* | 128 |
| *(trong SW1)* | — | — | — | — | route | — |
| SW1 → PC-B | **MAC-SVI** | MAC-B | 10.0.10.5 | 10.0.20.5 | 20 *(nội bộ)* | **127** |

**Ba điều rút ra:**

1. **IP không đổi** — vẫn `10.0.10.5 → 10.0.20.5` suốt đường
2. **MAC bị viết lại hoàn toàn** — đúng quy tắc "MAC đổi mỗi hop"
3. **TTL giảm 1** → bằng chứng đã qua một hop L3. `tracert` từ PC-A sang PC-B
   sẽ thấy **1 hop** chính là SVI.

> 🔑 Nếu `tracert` giữa 2 máy cho thấy **0 hop**, chúng cùng VLAN.
> **1 hop** → đã qua inter-VLAN routing. Đây là cách kiểm chứng nhanh nhất.

---

## 7. Real-world Example

🏭 **Thiết kế điển hình của một văn phòng**

```text
          ┌──── SW-DIST (L3) ────┐   ← SVI của MỌI VLAN ở đây
          │  ip routing          │     Đây cũng là nơi đặt ACL
          │  Vlan10  10.0.10.1   │
          │  Vlan20  10.0.20.1   │
          │  Vlan50  10.0.50.1   │
          │  Vlan90  10.0.90.1   │
          └───┬──────────────┬───┘
         trunk│              │trunk
        ┌─────┴────┐   ┌─────┴────┐
        │ SW-ACC1  │   │ SW-ACC2  │   ← chỉ L2, không có SVI
        └──────────┘   └──────────┘
```

Quy tắc: **gateway của mọi VLAN nằm ở lớp Distribution**, không nằm ở Access.
Lý do: tập trung điểm kiểm soát, và mất một switch access không làm mất gateway.

🏭 **ACL đặt ở đâu** — đây mới là lý do thật sự của thiết kế này:

```cisco
! Guest (VLAN 90) không được vào mạng nội bộ
SW-DIST(config)# ip access-list extended GUEST-RESTRICT
SW-DIST(config-ext-nacl)# deny   ip 10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255
SW-DIST(config-ext-nacl)# permit ip 10.0.90.0 0.0.0.255 any
SW-DIST(config)# interface vlan 90
SW-DIST(config-if)# ip access-group GUEST-RESTRICT in
```

Áp ACL **trên SVI** — mọi gói rời VLAN 90 đều phải đi qua đây. Không có đường vòng.

🏭 **Khi nào vẫn dùng Router-on-a-Stick**

- Chi nhánh nhỏ đã có sẵn router (ISR) và switch L2, không muốn mua thêm L3 switch
- Cần tính năng chỉ router có: **NAT, IPsec VPN, QoS sâu, tích hợp WAN**
- Lab học tập

> 🏭 Mô hình lai rất phổ biến: **L3 switch** route giữa các VLAN nội bộ,
> **router** chỉ lo đường ra Internet + NAT + VPN. Mỗi thiết bị làm đúng việc nó giỏi.

---

## 8. Cisco CLI

### Cách 1 — Router-on-a-Stick

```cisco
! ═══════ TRÊN SWITCH: port nối router PHẢI là trunk ═══════
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# description TRUNK-TO-ROUTER
SW1(config-if)# switchport trunk encapsulation dot1q    ! chỉ switch đời cũ cần
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20,99

! ═══════ TRÊN ROUTER: interface vật lý KHÔNG gán IP ═══════
R1(config)# interface GigabitEthernet0/0
R1(config-if)# no shutdown                   ! ← bật, nhưng KHÔNG đặt IP
R1(config-if)# exit

! Subinterface cho từng VLAN
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)# description GW-VLAN10
R1(config-subif)# encapsulation dot1Q 10     ! ← VLAN ID, BẮT BUỘC, đặt TRƯỚC ip address
R1(config-subif)# ip address 10.0.10.1 255.255.255.0

R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 10.0.20.1 255.255.255.0

! Subinterface cho NATIVE VLAN — cú pháp KHÁC
R1(config)# interface GigabitEthernet0/0.99
R1(config-subif)# encapsulation dot1Q 99 native     ! ← từ khoá "native"
R1(config-subif)# ip address 10.0.99.1 255.255.255.0
```

| Điểm | Giải thích |
|---|---|
| Interface **vật lý** không có IP | IP nằm ở subinterface. Nhưng **vẫn phải `no shutdown`** |
| `encapsulation dot1Q <vlan>` | Gắn subinterface với VLAN. **Phải gõ trước `ip address`** |
| Số subinterface (`.10`) | Chỉ là nhãn — **không bắt buộc** trùng VLAN ID, nhưng **nên** trùng cho dễ đọc |
| `native` ở cuối | Dùng cho VLAN native — subinterface này nhận frame **không tag** |

> ⚠️ Hai lỗi phổ biến nhất của RoAS:
> (1) **quên `no shutdown` interface vật lý** — subinterface sẽ không bao giờ lên;
> (2) **native VLAN hai đầu lệch** hoặc quên từ khoá `native`.

### Cách 2 — SVI trên L3 switch

```cisco
SW1(config)# ip routing                      ! ⭐ BẮT BUỘC, hay bị quên nhất

SW1(config)# vlan 10
SW1(config-vlan)# name SALES
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name KETOAN
SW1(config-vlan)# exit

SW1(config)# interface vlan 10
SW1(config-if)# description GW-VLAN10-SALES
SW1(config-if)# ip address 10.0.10.1 255.255.255.0
SW1(config-if)# no shutdown

SW1(config)# interface vlan 20
SW1(config-if)# description GW-VLAN20-KETOAN
SW1(config-if)# ip address 10.0.20.1 255.255.255.0
SW1(config-if)# no shutdown

! Access port cho PC
SW1(config)# interface range GigabitEthernet1/0/1 - 12
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 10
SW1(config-if-range)# spanning-tree portfast
```

### Khác biệt platform

| | IOS / IOS-XE | NX-OS |
|---|---|---|
| Bật routing | `ip routing` | Mặc định bật |
| Tạo SVI | *(có sẵn)* | Cần `feature interface-vlan` trước |
| Subinterface | `interface Gi0/0.10` + `encapsulation dot1Q 10` | `interface Eth1/1.10` + `encapsulation dot1q 10` |
| `switchport trunk encapsulation` | Chỉ switch đời cũ có ISL | Không có lệnh này |

---

## 9. Verification

### Router-on-a-Stick

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip interface brief
Interface                  IP-Address      OK? Method Status    Protocol
GigabitEthernet0/0         unassigned      YES unset  up        up      ← vật lý, không IP
GigabitEthernet0/0.10      10.0.10.1       YES manual up        up
GigabitEthernet0/0.20      10.0.20.1       YES manual up        up
GigabitEthernet0/0.99      10.0.99.1       YES manual up        up
```

> 🔍 Nếu interface **vật lý** `administratively down`, **mọi subinterface đều down**
> dù cấu hình đúng. Đây là lỗi số 1 của RoAS.

### SVI

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip route
      10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
C        10.0.10.0/24 is directly connected, Vlan10
L        10.0.10.1/32 is directly connected, Vlan10
C        10.0.20.0/24 is directly connected, Vlan20
L        10.0.20.1/32 is directly connected, Vlan20
```

**Đọc gì:** có đủ `C` cho mọi VLAN → switch biết đường tới cả hai subnet → route được.
Nếu lệnh `show ip route` **không chạy** hoặc trống → chưa bật `ip routing`.

### Kiểm chứng end-to-end

```cisco
PC-A> ping 10.0.10.1          ! gateway của mình — phải được
PC-A> ping 10.0.20.1          ! gateway VLAN khác — phải được
PC-A> ping 10.0.20.5          ! PC-B — phải được
PC-A> tracert 10.0.20.5       ! phải thấy ĐÚNG 1 hop
```

| Kết quả | Chẩn đoán |
|---|---|
| Ping gateway mình **fail** | Vấn đề L2: sai VLAN, port down, sai IP/mask |
| Ping gateway mình OK, gateway VLAN khác **fail** | Chưa `ip routing`, hoặc SVI kia down |
| Ping cả 2 gateway OK, ping PC-B **fail** | PC-B sai gateway, hoặc firewall trên PC-B |
| `tracert` thấy **0 hop** | Hai máy **cùng VLAN** — không phải inter-VLAN |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Ping được gateway mình, **không** ping được VLAN khác | **Quên `ip routing`** | `show ip route` trống/lỗi | `ip routing` |
| Mọi subinterface của RoAS đều down | Interface **vật lý** đang shutdown | `show ip interface brief` | `no shutdown` interface vật lý |
| SVI `down/down` | VLAN chưa có port nào up | `show vlan brief` | Gán port vào VLAN, hoặc allow trên trunk |
| Một VLAN thông, VLAN khác không | VLAN không nằm trong `allowed vlan` của trunk | `show interfaces trunk` | Thêm VLAN vào allowed list |
| VLAN native không thông ở RoAS | Thiếu từ khoá `native` trên subinterface | `show run \| section Gi0/0` | Thêm `encapsulation dot1Q 99 native` |
| PC ping được gateway nhưng không ra Internet | Thiếu default route trên L3 switch | `show ip route` không có `S*` | `ip route 0.0.0.0 0.0.0.0 <next-hop>` |
| Ping được 1 chiều | PC bên kia sai default gateway | `ipconfig` trên cả 2 PC | Sửa gateway |
| Inter-VLAN chạy nhưng rất chậm | **Nút cổ chai RoAS** | `show interfaces Gi0/0` xem utilization | Chuyển sang L3 switch |
| Subinterface lên nhưng không route | Thiếu `encapsulation dot1Q` hoặc sai VLAN ID | `show run interface Gi0/0.10` | Sửa VLAN ID |

---

## 11. LAB

🧪 **[LAB 12 — Inter-VLAN Routing: Router-on-a-Stick và SVI](../labs/lab12-inter-vlan-routing.md)**

## 12. Challenge

1. RoAS cấu hình đúng hết, nhưng **không VLAN nào** ping được VLAN nào. Nguyên nhân
   phổ biến nhất là gì?
2. Công ty có 6 VLAN, mỗi VLAN ~50 user, traffic inter-VLAN cao (dùng chung file server).
   RoAS với uplink 1 Gbps có đủ không? Tính thử.
3. Bạn dùng L3 switch với SVI. PC VLAN 10 ping được PC VLAN 20, nhưng **không ra được
   Internet**, dù router biên hoạt động bình thường. Thiếu gì?
4. Vì sao số subinterface (`Gi0/0.10`) không bắt buộc phải trùng VLAN ID, nhưng nên trùng?

<details>
<summary>Đáp án</summary>

**1.** **Quên `no shutdown` trên interface vật lý** `Gi0/0`. Subinterface **kế thừa trạng thái
vật lý** — interface vật lý down thì mọi subinterface đều down, dù `show run` nhìn hoàn toàn đúng.

Nguyên nhân phổ biến thứ hai: **port switch nối router không phải trunk** (vẫn đang access).
Kiểm chứng bằng `show interfaces trunk` trên switch.

**2.** Tính thô:

```text
6 VLAN × 50 user = 300 user
Traffic inter-VLAN đi LÊN rồi XUỐNG cùng link → mỗi luồng tiêu tốn 2× băng thông
Link 1 Gbps  →  thực tế phục vụ ~500 Mbps traffic inter-VLAN
500 Mbps / 300 user ≈ 1.7 Mbps/user
```

Với file server dùng chung, 1.7 Mbps/user là **không đủ** — copy một file 1 GB đã chiếm
hết phần của hàng chục người. **Phải dùng L3 switch.**

RoAS chỉ hợp lý khi: ít VLAN (< 5), ít user, traffic inter-VLAN thấp.

**3.** Thiếu **default route** trên L3 switch:

```cisco
SW-DIST(config)# ip route 0.0.0.0 0.0.0.0 10.255.0.1    ! trỏ về router biên
```

L3 switch biết đường tới các VLAN connected, nhưng **không biết gì về phần còn lại của
thế giới**. Nó cần một default route trỏ về router biên. *(Và router biên cũng cần route
ngược về các subnet nội bộ, hoặc chạy routing protocol.)*

**4.** Số subinterface chỉ là **nhãn cục bộ** của router — thứ thật sự gắn subinterface với
VLAN là lệnh `encapsulation dot1Q <vlan-id>`. Về kỹ thuật bạn có thể đặt `Gi0/0.1` cho
VLAN 10.

**Nhưng nên trùng** vì: người đọc config sau bạn nhìn `Gi0/0.10` là biết ngay VLAN 10,
không phải dò xuống dòng `encapsulation`. Khi có 15 subinterface, chênh lệch này là
giữa "đọc được" và "không đọc nổi".

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 cách inter-VLAN routing · `encapsulation dot1Q` làm gì · `ip routing` ở đâu | ⬜ |
| **L2** Explain | Giải thích nút cổ chai của RoAS bằng đường đi gói tin | ⬜ |
| **L3** Configure | Cấu hình cả 2 cách, verify bằng `tracert` thấy 1 hop | ⬜ |
| **L4** Troubleshoot | RoAS mọi subinterface down → nêu 2 nguyên nhân | ⬜ |
| **L5** Design | Chọn RoAS hay SVI cho 3 kịch bản cho trước, giải thích từng cái | ⬜ |

## 14. Summary

**Key concepts**

- Hai VLAN = hai broadcast domain = hai subnet → **bắt buộc** cần L3 để nói chuyện
- **Router-on-a-Stick**: 1 link trunk + subinterface, mỗi subinterface 1 VLAN
- `encapsulation dot1Q <vlan>` phải gõ **trước** `ip address`
- Native VLAN cần từ khoá `native` ở cuối
- ⚠️ Interface **vật lý** của RoAS phải `no shutdown` dù không có IP
- **SVI trên L3 switch** = chuẩn hiện nay — route bằng ASIC, không nghẽn
- ⭐ **`ip routing` phải bật tay** — lỗi số 1 với SVI
- ⭐ **RoAS có nút cổ chai**: traffic đi lên rồi xuống cùng một link
- TTL giảm 1 = đã qua L3 → `tracert` thấy đúng **1 hop** giữa 2 VLAN
- Gateway nên đặt ở lớp **Distribution**, và đó cũng là nơi đặt ACL

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip routing` | **Luôn đầu tiên** trên L3 switch |
| `interface vlan N` + `ip address` | Tạo SVI |
| `interface Gi0/0.10` + `encapsulation dot1Q 10` | Subinterface cho RoAS |
| `encapsulation dot1Q 99 native` | Subinterface cho native VLAN |
| `show ip route` | Có đủ `C` cho mọi VLAN chưa |
| `tracert <ip>` | Kiểm chứng đã qua L3 (1 hop) |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `ip routing` | SVI up, ping được gateway, nhưng VLAN không thông nhau |
| Quên `no shutdown` interface vật lý (RoAS) | **Mọi** subinterface down |
| Port nối router vẫn là access | Router không nhận được frame có tag |
| Gõ `ip address` trước `encapsulation dot1Q` | Lệnh bị từ chối |
| Quên `native` trên subinterface của VLAN native | VLAN đó không thông |
| Quên default route trên L3 switch | Inter-VLAN chạy nhưng không ra Internet |
| Dùng RoAS cho mạng nhiều VLAN/traffic cao | Nghẽn link trunk |

## 15. Homework + cập nhật PROGRESS

1. Làm [LAB 12](../labs/lab12-inter-vlan-routing.md) — **cả hai cách**, đủ mục BREAK.
2. Trong lab RoAS, chạy `show interfaces Gi0/0` khi đang copy file giữa 2 VLAN.
   Quan sát utilization → tự chứng minh nút cổ chai.
3. Vẽ lại sơ đồ mạng công ty bạn, đánh dấu gateway của mỗi VLAN nằm ở thiết bị nào.
   Nó ở lớp Access hay Distribution?

```markdown
- [YYYY-MM-DD] Lesson 14 — Inter-VLAN Routing: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Cú pháp RoAS và SVI, `encapsulation dot1Q`, `ip routing`, native VLAN subinterface |
| 🔧 **Engineer** | Chọn SVI cho mạng thật; đặt gateway ở Distribution; nhớ default route |
| 🏭 **Production** | SVI là nơi đặt ACL — thiết kế gateway chính là thiết kế điểm kiểm soát; RoAS nghẽn khi scale |

### 🔗 Liên kết

- ⬅️ [Lesson 13 — VLAN & Trunk](./lesson-13-vlan-va-trunk.md)
- ➡️ [Lesson 15 — STP](./lesson-15-stp.md)
- 🧪 [LAB 12](../labs/lab12-inter-vlan-routing.md)
- 🔜 ACL trên SVI: [Lesson 36](../06-security/README.md)
