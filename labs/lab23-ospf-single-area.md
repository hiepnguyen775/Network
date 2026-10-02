# LAB 23 — OSPF single-area: neighbor, DR/BDR, đọc LSDB

| | |
|---|---|
| **Phase** | 2 |
| **Lesson liên quan** | [Lesson 22](../02-routing/lesson-22-ospf-single-area.md), [Lesson 23](../02-routing/lesson-23-ospf-cost-lsdb-lsa.md) |
| **Công cụ** | Packet Tracer (GNS3 nếu muốn chỉnh MTU thật) |
| **Thời lượng** | ~3.5 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |

---

## 1. Mục tiêu

- [ ] Dựng OSPF single-area 4 router, mọi neighbor lên FULL (hoặc 2-WAY đúng chỗ)
- [ ] **Dự đoán trước** ai làm DR/BDR rồi kiểm chứng
- [ ] **Vẽ lại topology chỉ từ LSDB**, không nhìn sơ đồ
- [ ] Tự tạo và tự tìm ra 4 lỗi OSPF kinh điển
- [ ] Đo thời gian hội tụ, so với RIP ở Lesson 21

## 2. Prerequisite

- [Lesson 22](../02-routing/lesson-22-ospf-single-area.md) — 7 state, 6 thứ phải khớp, DR/BDR
- [Lesson 23](../02-routing/lesson-23-ospf-cost-lsdb-lsa.md) — cost, LSDB, LSA

---

## 3. Topology

```text
                  ┌──────── SEGMENT ETHERNET CHUNG ────────┐
                  │   10.0.12.0/24                          │
                 R1          R2          R3          R4
              .1 │       .2 │        .3 │        .4 │
                 └──────────┴───────────┴───────────┘
                            (qua switch SW1)
                 │                                   │
            10.1.1.0/24                         10.4.4.0/24
              PC-A                                 PC-B
```

| Thiết bị | Loopback | IP segment chung | LAN |
|---|---|---|---|
| R1 | `1.1.1.1/32` | `10.0.12.1/24` | `10.1.1.1/24` |
| R2 | `2.2.2.2/32` | `10.0.12.2/24` | — |
| R3 | `3.3.3.3/32` | `10.0.12.3/24` | — |
| R4 | `4.4.4.4/32` | `10.0.12.4/24` | `10.4.4.1/24` |

> 💡 Dùng **segment Ethernet chung** (qua switch) để có DR/BDR — đây là điểm khác
> với lab nối chuỗi thông thường.

---

## 4. Yêu cầu LAB

- [ ] Mọi router có Router ID lấy từ loopback, đặt bằng `router-id`
- [ ] OSPF area 0, `passive-interface default` + mở đúng interface cần
- [ ] `auto-cost reference-bandwidth 100000` trên **mọi** router
- [ ] PC-A ping được PC-B
- [ ] Dự đoán đúng DR/BDR trước khi kiểm chứng
- [ ] Vẽ lại topology từ LSDB
- [ ] Hoàn thành mục **8. BREAK** với đủ 4 lỗi

---

## 5. Step-by-step

### Cấu hình mẫu (R1 — các router khác tương tự)

```cisco
hostname R1
no ip domain-lookup

interface Loopback0
 ip address 1.1.1.1 255.255.255.255
exit

interface GigabitEthernet0/0
 description SEGMENT-CHUNG
 ip address 10.0.12.1 255.255.255.0
 no shutdown
exit

interface GigabitEthernet0/1
 description LAN-A
 ip address 10.1.1.1 255.255.255.0
 no shutdown
exit

router ospf 1
 router-id 1.1.1.1
 auto-cost reference-bandwidth 100000
 passive-interface default
 no passive-interface GigabitEthernet0/0
 network 10.0.12.1 0.0.0.0 area 0
 network 10.1.1.1 0.0.0.0 area 0
exit

end
copy running-config startup-config
```

> ⚠️ Chú ý: `passive-interface default` rồi `no passive-interface` **chỉ** cho
> interface nối router. LAN vẫn được **quảng bá** (vì có `network`), chỉ là
> không gửi hello ra đó.

### Bước DỰ ĐOÁN — làm trước khi gõ `show`

> 🔴 Phần có giá trị nhất của lab. Đừng bỏ qua.

| Câu hỏi | Dự đoán của tôi |
|---|---|
| Ai sẽ là **DR**? Vì sao? | |
| Ai sẽ là **BDR**? | |
| R1 sẽ thấy bao nhiêu neighbor? | |
| State của từng neighbor trên R1? | |
| Có bao nhiêu LSA **Type 2**? Ai tạo? | |
| Cost từ R1 tới `10.4.4.0/24`? | |

---

## 6. Verification

```cisco
R1# show ip ospf neighbor
R1# show ip ospf interface GigabitEthernet0/0
R1# show ip ospf
R1# show ip ospf database
R1# show ip route ospf
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address      Interface
2.2.2.2           1   2WAY/DROTHER    00:00:35    10.0.12.2    GigabitEthernet0/0
3.3.3.3           1   FULL/BDR        00:00:33    10.0.12.3    GigabitEthernet0/0
4.4.4.4           1   FULL/DR         00:00:31    10.0.12.4    GigabitEthernet0/0
```

### Bảng kiểm chứng

| Mục | Dự đoán | Thực tế | Khớp? |
|---|---|---|:---:|
| DR | | | |
| BDR | | | |
| Số neighbor trên R1 | | | |
| Số LSA Type 2 | | | |
| Cost R1 → `10.4.4.0/24` | | | |

| | |
|---|---|
| Dự đoán sai ở đâu? | |
| Tôi hiểu nhầm điều gì? | |

### Bài đọc LSDB — vẽ lại topology

```cisco
R1# show ip ospf database
R1# show ip ospf database router 1.1.1.1
R1# show ip ospf database router 2.2.2.2
R1# show ip ospf database router 3.3.3.3
R1# show ip ospf database router 4.4.4.4
R1# show ip ospf database network
```

> 🎯 **Nhiệm vụ:** chỉ dùng output trên, vẽ lại sơ đồ mạng ra giấy —
> ai nối với ai, cost bao nhiêu, LAN nào ở đâu. Rồi so với sơ đồ mục 3.

| Câu hỏi | Trả lời |
|---|---|
| `Link count` của R1 là bao nhiêu? Gồm những link nào? | |
| LSA Type 2 có `Link ID` là gì? Vì sao là địa chỉ đó? | |
| Số LSA trên R1 và trên R4 có bằng nhau không? | |

---

## 7. Đo thời gian hội tụ

```text
1. Từ PC-A: ping -t <IP PC-B>
2. Shutdown interface trên router đang là DR
3. ĐẾM số gói mất
4. Ghi lại
```

| Sự kiện | Số gói mất | Thời gian |
|---|:---:|:---:|
| Shutdown LAN của R4 | | |
| Shutdown interface DR trên segment chung | | |
| So với RIP *(Lesson 21)* | | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

> Với mỗi lỗi: **dự đoán** → tạo lỗi → quan sát → tự tìm bằng **9 bước** ở Lesson 22,
> không nhìn lại chỗ vừa sửa.

### Lỗi 1 — Area ID lệch

```cisco
R2(config-router)# no network 10.0.12.2 0.0.0.0 area 0
R2(config-router)# network 10.0.12.2 0.0.0.0 area 1
```

| | |
|---|---|
| Dự đoán | |
| `show ip ospf neighbor` trên R1 hiện gì | |
| Lệnh nào lộ ra nguyên nhân | |
| Cách sửa | |

### Lỗi 2 — Hello/Dead timer lệch

```cisco
R3(config)# interface GigabitEthernet0/0
R3(config-if)# ip ospf hello-interval 5
```

| | |
|---|---|
| Dự đoán | |
| Neighbor rớt sau bao lâu? | |
| Lệnh nào so sánh được timer 2 đầu | |
| Vì sao đổi hello cũng đổi dead? | |

### Lỗi 3 — Passive interface

```cisco
R4(config-router)# passive-interface GigabitEthernet0/0
```

| | |
|---|---|
| Dự đoán | |
| R1 còn thấy R4 không? | |
| Mạng LAN của R4 còn trong routing table không? **Vì sao?** | |
| Lệnh phát hiện | |

### Lỗi 4 — Router ID trùng

```cisco
R3(config-router)# router-id 2.2.2.2
R3# clear ip ospf process
```

| | |
|---|---|
| Dự đoán | |
| Log console hiện gì | |
| Hành vi neighbor ra sao | |
| Cách sửa | |

### Lỗi 5 *(tự chọn)* — MTU mismatch

> ⚠️ Packet Tracer **không mô phỏng** MTU mismatch. Làm trên **GNS3/EVE-NG** nếu có.

```cisco
R2(config-if)# ip mtu 1400
```

Quan sát neighbor kẹt ở **EXSTART/EXCHANGE** — trải nghiệm đáng giá nhất của lab này.

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Ép R1 làm DR mà **không** đổi Router ID. Viết lệnh. Có hiệu lực ngay không?
2. Đổi segment chung thành `ip ospf network point-to-point` trên mọi router.
   Chuyện gì xảy ra với DR/BDR và với LSA Type 2?
3. Đặt `ip ospf cost 500` trên interface LAN của R4. Quan sát:
   LSA nào đổi? `SPF executed` trên R1 có tăng không?
4. Vì sao `passive-interface` làm mất neighbor nhưng **không** làm mất route của mạng đó?

<details>
<summary>Đáp án</summary>

**1.**

```cisco
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip ospf priority 255
```

**Không có hiệu lực ngay.** OSPF **không có preemption** — DR đã bầu thì giữ nguyên.
Phải `clear ip ospf process` trên **tất cả** router của segment, hoặc shutdown/no shutdown
interface, để bầu lại.

**2.** Với `network point-to-point`:

| Thay đổi | Kết quả |
|---|---|
| DR/BDR | **Không bầu nữa** — `show ip ospf neighbor` hiện `FULL/-` |
| LSA Type 2 | **Biến mất** — Type 2 chỉ do DR tạo |
| Adjacency | Mọi router FULL với **mọi** router (không còn 2WAY/DROTHER) |
| Hội tụ | Nhanh hơn — không mất thời gian bầu DR |

⚠️ Chỉ nên dùng khi segment thật sự **chỉ có 2 router**. Với 4 router như lab này,
mọi cặp sẽ peer đầy đủ → `4×3/2 = 6` adjacency, mất hết lợi ích của DR.

**3.**

| Quan sát | Kết quả |
|---|---|
| LSA đổi | **LSA Type 1 của R4** — `Seq#` tăng, cost của link LAN đổi thành 500 |
| `SPF executed` trên R1 | **Có tăng** — mọi router trong area phải tính lại |
| Routing table R1 | Cost tới `10.4.4.0/24` tăng thêm 499 |

Đây là minh hoạ trực tiếp của cơ chế flood: R4 đổi một con số → **mọi router trong area**
nhận LSA mới và chạy lại SPF.

**4.** Vì `passive-interface` và `network` statement làm **hai việc khác nhau**:

| | Tác dụng |
|---|---|
| `network <ip> 0.0.0.0 area 0` | (a) Bật OSPF trên interface · (b) **Quảng bá** subnet đó vào area |
| `passive-interface <int>` | Tắt **(a)** — không gửi/nhận hello → **không lên neighbor** |

`passive-interface` **không** tắt (b). Subnet vẫn được quảng bá trong LSA Type 1 của
router đó, nên các router khác vẫn học được route.

👉 Đây chính là lý do ta dùng `passive-interface` cho **LAN người dùng**: vẫn quảng bá
mạng đó cho cả area, nhưng không gửi hello ra chỗ không có router nào.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Dự đoán DR/BDR

Mọi router priority mặc định **1** → hoà → so **Router ID cao nhất**:

| Router | Router ID | Vai trò |
|---|---|---|
| R4 | `4.4.4.4` | **DR** (cao nhất) |
| R3 | `3.3.3.3` | **BDR** (cao thứ hai) |
| R2 | `2.2.2.2` | DROTHER |
| R1 | `1.1.1.1` | DROTHER |

**Trên R1** (DROTHER) sẽ thấy **3 neighbor**:

```text
2.2.2.2   2WAY/DROTHER    ← DROTHER ↔ DROTHER, dừng ở 2-WAY
3.3.3.3   FULL/BDR
4.4.4.4   FULL/DR
```

**LSA Type 2: đúng 1 cái**, do **R4 (DR)** tạo, `Link ID` = `10.0.12.4`
(địa chỉ interface của DR trên segment đó).

> ⚠️ Nếu kết quả thật khác dự đoán, khả năng cao là **thứ tự bật router** —
> router lên trước thành DR và **giữ nguyên** (không preemption). Reset bằng
> `clear ip ospf process` trên mọi router để bầu lại theo đúng Router ID.

### Cost R1 → `10.4.4.0/24`

Với `auto-cost reference-bandwidth 100000` (100 Gbps) và link Gigabit:

```text
Cost mỗi link Gi = 100000 / 1000 = 100

R1 → segment chung : 100
R4 → LAN           : 100
──────────────────────────
TỔNG               : 200
```

### Giải thích các lỗi BREAK

| # | Triệu chứng | Lệnh phát hiện | Nguyên nhân |
|:---:|---|---|---|
| 1 | R2 **biến mất** khỏi `show ip ospf neighbor` của mọi router | `show ip ospf interface Gi0/0` 2 đầu — so dòng `Area` | Area ID lệch (0 vs 1) |
| 2 | R3 rớt sau ~**40 giây** (dead interval của R1) rồi không lên lại | `show ip ospf interface Gi0/0` — so `Hello` và `Dead` | Timer lệch |
| 3 | R4 biến mất khỏi neighbor, **nhưng route `10.4.4.0/24` vẫn còn** | `show ip protocols` — thấy Gi0/0 trong danh sách Passive | `passive-interface` |
| 4 | Log `%OSPF-4-DUP_RTRID1`; neighbor nhấp nháy liên tục | `show ip ospf` ở R2 và R3 | Router ID trùng |
| 5 | Kẹt vĩnh viễn ở `EXSTART`/`EXCHANGE` | `show interfaces \| include MTU` 2 đầu | MTU mismatch |

**Chi tiết lỗi 2 — vì sao đổi hello cũng đổi dead:**
IOS tự đặt `dead-interval = 4 × hello-interval`. Đổi hello thành 5 → dead tự thành 20.
R1 vẫn giữ 10/40. Cả hai giá trị đều lệch → neighbor không lên.

**Chi tiết lỗi 3 — điểm tinh tế nhất của lab:**
Route `10.4.4.0/24` **vẫn còn** vì `network` statement vẫn quảng bá nó trong LSA Type 1
của R4. Nhưng R4 không còn là neighbor của ai → nếu segment chung là đường duy nhất,
R4 bị **cô lập hoàn toàn** và cuối cùng LSA của nó hết hạn (60 phút) rồi route mới mất.

Trong lab bạn sẽ thấy route còn một lúc rồi mới biến mất — đó là LSA aging.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Dự đoán DR/BDR của tôi sai ở đâu? ___
- Vẽ lại topology từ LSDB có khó không? Chỗ nào khó nhất? ___
- Thời gian hội tụ OSPF tôi đo được: ___ giây (RIP: ___ giây)
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
