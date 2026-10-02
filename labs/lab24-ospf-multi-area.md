# LAB 24 — OSPF Multi-Area & Summarization

| | |
|---|---|
| **Phase** | 2 |
| **Lesson liên quan** | [Lesson 24 — OSPF multi-area](../02-routing/lesson-24-ospf-multi-area.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~3 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Dựng OSPF 2 area, phân biệt route `O` và `O IA`
- [ ] **Chứng minh bằng số liệu** rằng area cách ly LSA và SPF
- [ ] Cấu hình summarization trên ABR, đếm số route **trước và sau**
- [ ] Chứng minh **area không chạm Area 0** làm route không lan
- [ ] Tạo blackhole bằng summarize sai dải

## 2. Prerequisite

- [LAB 23](./lab23-ospf-single-area.md) — đã làm xong
- [Lesson 24](../02-routing/lesson-24-ospf-multi-area.md) — ABR, quy tắc Area 0, LSA Type 3

---

## 3. Topology

```text
         ══════ AREA 1 ══════        ══ AREA 0 ══        ═══ AREA 2 ═══

   R1 ──────── R2 ──────── [ABR-A] ──────── [ABR-B] ──────── R5
10.1.0.0/24  10.1.1.0/24                                  10.2.0.0/24
10.1.2.0/24  10.1.3.0/24                                  10.2.1.0/24
```

Chi tiết:

| Router | Area | Link |
|---|---|---|
| R1 | 1 | `10.1.0.0/24` (LAN), `10.0.12.0/30` (→R2) |
| R2 | 1 | `10.1.1.0/24` (LAN), `10.0.12.0/30`, `10.0.2A.0/30` (→ABR-A) |
| **ABR-A** | **1 + 0** | `10.0.2A.0/30` (Area 1), `10.0.AB.0/30` (Area 0) |
| **ABR-B** | **0 + 2** | `10.0.AB.0/30` (Area 0), `10.0.B5.0/30` (Area 2) |
| R5 | 2 | `10.2.0.0/24` (LAN), `10.0.B5.0/30` |

> 💡 Để có nhiều mạng cho summarize, thêm **loopback** trên R1 và R2:
> `Lo1 10.1.2.1/24`, `Lo2 10.1.3.1/24` — chúng sẽ thành các route riêng.

## 4. IP Addressing Table

| Device | Interface | IP | Area |
|---|---|---|:---:|
| R1 | Lo0 *(Router ID)* | `1.1.1.1/32` | — |
| R1 | Gi0/0 | `10.1.0.1/24` | 1 |
| R1 | Lo1 | `10.1.2.1/24` | 1 |
| R1 | Gi0/1 | `10.0.12.1/30` | 1 |
| R2 | Lo0 | `2.2.2.2/32` | — |
| R2 | Gi0/0 | `10.1.1.1/24` | 1 |
| R2 | Lo1 | `10.1.3.1/24` | 1 |
| R2 | Gi0/1 | `10.0.12.2/30` | 1 |
| R2 | Gi0/2 | `10.0.20.1/30` | 1 |
| **ABR-A** | Lo0 | `10.10.10.10/32` | — |
| ABR-A | Gi0/1 | `10.0.20.2/30` | **1** |
| ABR-A | Gi0/2 | `10.0.0.1/30` | **0** |
| **ABR-B** | Lo0 | `20.20.20.20/32` | — |
| ABR-B | Gi0/1 | `10.0.0.2/30` | **0** |
| ABR-B | Gi0/2 | `10.0.25.1/30` | **2** |
| R5 | Lo0 | `5.5.5.5/32` | — |
| R5 | Gi0/1 | `10.0.25.2/30` | 2 |
| R5 | Gi0/0 | `10.2.0.1/24` | 2 |
| R5 | Lo1 | `10.2.1.1/24` | 2 |

---

## 5. Yêu cầu LAB

- [ ] Mọi router hội tụ, R1 ping được LAN của R5
- [ ] R1 thấy route `O` cho mạng Area 1 và `O IA` cho mạng Area 0/2
- [ ] `show ip ospf database` ở R1 và R5 **khác nhau** → bằng chứng area cách ly LSA
- [ ] `show ip ospf` trên ABR hiện `It is an area border router` và **SPF riêng từng area**
- [ ] Summarize Area 1 → đếm số route giảm
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Cấu hình OSPF

```cisco
! ══════════ R1 (Area 1) ══════════
hostname R1
no ip domain-lookup
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
interface Loopback1
 ip address 10.1.2.1 255.255.255.0
 ip ospf network point-to-point        ! để loopback quảng bá /24, không phải /32
interface GigabitEthernet0/0
 ip address 10.1.0.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 10.0.12.1 255.255.255.252
 no shutdown

router ospf 1
 router-id 1.1.1.1
 auto-cost reference-bandwidth 100000
 passive-interface default
 no passive-interface GigabitEthernet0/1
 network 10.1.0.1 0.0.0.0 area 1
 network 10.1.2.1 0.0.0.0 area 1
 network 10.0.12.1 0.0.0.0 area 1
```

> 🔑 `ip ospf network point-to-point` trên loopback làm nó quảng bá **đúng prefix `/24`**
> thay vì `/32`. Không có dòng này, summarize sẽ không ra kết quả như mong đợi.

```cisco
! ══════════ ABR-A — CHÂN Ở CẢ 2 AREA ══════════
hostname ABR-A
interface Loopback0
 ip address 10.10.10.10 255.255.255.255
interface GigabitEthernet0/1
 description TOI-AREA-1
 ip address 10.0.20.2 255.255.255.252
interface GigabitEthernet0/2
 description TOI-AREA-0-BACKBONE
 ip address 10.0.0.1 255.255.255.252

router ospf 1
 router-id 10.10.10.10
 auto-cost reference-bandwidth 100000
 network 10.0.20.2 0.0.0.0 area 1      ! ← chân Area 1
 network 10.0.0.1 0.0.0.0 area 0       ! ← chân Area 0
```

R2, ABR-B, R5 cấu hình tương tự theo bảng IP.

### Bước 2 — Verify phân biệt `O` và `O IA`

```cisco
R1# show ip route ospf
```

| Mạng | Mong đợi mã | Thực tế |
|---|---|---|
| `10.1.1.0/24` *(LAN R2, Area 1)* | `O` | |
| `10.1.3.0/24` *(Lo1 R2, Area 1)* | `O` | |
| `10.0.0.0/30` *(link Area 0)* | `O IA` | |
| `10.2.0.0/24` *(LAN R5, Area 2)* | `O IA` | |

### Bước 3 — Chứng minh area cách ly LSA ⭐

> 🔴 Đây là bài có giá trị nhất của lab. Đếm **chính xác**.

```cisco
R1#    show ip ospf database | include Router Link States|Net Link States|Summary Net
R5#    show ip ospf database | include Router Link States|Net Link States|Summary Net
ABR-A# show ip ospf
```

| Router | Số LSA Type 1 | Số LSA Type 3 | Tổng LSA |
|---|:---:|:---:|:---:|
| R1 *(Area 1)* | | | |
| R5 *(Area 2)* | | | |
| ABR-A *(Area 0 + 1)* | | | |

| Câu hỏi | Trả lời |
|---|---|
| R1 có thấy LSA Type 1 của R5 không? **Vì sao?** | |
| ABR-A có `SPF algorithm executed` **riêng cho từng area** không? | |
| Điều này chứng minh gì? | |

### Bước 4 — Summarization

Trước khi summarize, đếm:

```cisco
R5# show ip route ospf | include 10.1.
```

| | Số route `10.1.x.x` trên R5 |
|---|:---:|
| **Trước** summarize | |

Area 1 có các mạng: `10.1.0.0/24`, `10.1.1.0/24`, `10.1.2.0/24`, `10.1.3.0/24`
→ gom được thành **`10.1.0.0/22`**.

```cisco
ABR-A(config)# router ospf 1
ABR-A(config-router)# area 1 range 10.1.0.0 255.255.252.0
```

```cisco
R5# show ip route ospf | include 10.1.
ABR-A# show ip route | include Null0
```

| | Số route `10.1.x.x` trên R5 |
|---|:---:|
| **Sau** summarize | |

| Câu hỏi | Trả lời |
|---|---|
| Giảm từ mấy xuống mấy? | |
| ABR-A tự sinh route gì tới `Null0`? **Để làm gì?** | |
| R5 vẫn ping được `10.1.0.1` chứ? | |

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route ospf
      10.0.0.0/8 is variably subnetted, 12 subnets, 3 masks
O        10.1.1.0/24 [110/200] via 10.0.12.2, 00:10:12, GigabitEthernet0/1
O        10.1.3.0/24 [110/200] via 10.0.12.2, 00:10:12, GigabitEthernet0/1
O IA     10.0.0.0/30 [110/300] via 10.0.12.2, 00:09:55, GigabitEthernet0/1
O IA     10.2.0.0/24 [110/500] via 10.0.12.2, 00:09:55, GigabitEthernet0/1
O IA     10.2.1.0/24 [110/500] via 10.0.12.2, 00:09:55, GigabitEthernet0/1
```

```text
# output điển hình — tự verify trên lab của bạn
ABR-A# show ip ospf
 Routing Process "ospf 1" with ID 10.10.10.10
 It is an area border router                       ← ✅ XÁC NHẬN LÀ ABR
 Number of areas in this router is 2. 2 normal 0 stub 0 nssa
    Area BACKBONE(0)
        Number of interfaces in this area is 1
        SPF algorithm executed 9 times              ← SPF RIÊNG
        Number of LSA 7
    Area 1
        Number of interfaces in this area is 1
        SPF algorithm executed 14 times             ← SPF RIÊNG, SỐ KHÁC
        Number of LSA 11
```

> 🔑 Hai dòng `SPF algorithm executed` với **số khác nhau** là bằng chứng trực tiếp:
> SPF của Area 1 chạy **độc lập** với SPF của Area 0.

```text
# output điển hình — sau khi summarize
R5# show ip route ospf | include 10.1.
O IA     10.1.0.0/22 [110/600] via 10.0.25.1, 00:01:33, GigabitEthernet0/1
```

```text
# output điển hình — route Null0 tự sinh trên ABR
ABR-A# show ip route | include Null0
O        10.1.0.0/22 is a summary, 00:01:40, Null0
```

**Bằng chứng lab đúng:**

- [ ] R1 có cả `O` và `O IA`
- [ ] Số LSA ở R1 ≠ số LSA ở R5
- [ ] ABR hiện `It is an area border router` + SPF riêng từng area
- [ ] Sau summarize: R5 chỉ còn **1 route** `10.1.0.0/22` thay vì 4
- [ ] ABR-A có route `10.1.0.0/22 → Null0`
- [ ] R5 vẫn ping được mọi LAN của Area 1

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Area không chạm Area 0 ⭐

Thêm **R6** nối vào R5, đặt nó ở **Area 3**:

```text
Area 1 ── ABR-A ── Area 0 ── ABR-B ── Area 2 ── R5 ── Area 3 ── R6
                                                 ↑
                                        R5 trở thành "ABR" của Area 3
                                        NHƯNG R5 KHÔNG có chân Area 0!
```

```cisco
R5(config)# interface GigabitEthernet0/2
R5(config-if)# ip address 10.3.0.1 255.255.255.252
R5(config-if)# no shutdown
R5(config)# router ospf 1
R5(config-router)# network 10.3.0.1 0.0.0.0 area 3

R6(config)# router ospf 1
R6(config-router)# router-id 6.6.6.6
R6(config-router)# network 10.3.0.2 0.0.0.0 area 3
R6(config-router)# network 10.6.0.1 0.0.0.0 area 3
```

| | |
|---|---|
| R6 có neighbor với R5 không? | |
| R6 có thấy route của Area 1, Area 2 không? | |
| **R1 có thấy mạng `10.6.0.0/24` của R6 không?** | |
| `show ip ospf` trên R5 nói gì? | |
| Giải thích vì sao route của Area 3 không lan ra ngoài | |

### Lỗi 2 — Summarize dải rộng hơn thực tế → blackhole

```cisco
ABR-A(config-router)# no area 1 range 10.1.0.0 255.255.252.0
ABR-A(config-router)# area 1 range 10.1.0.0 255.255.0.0      ! /16 — RỘNG QUÁ
```

| | |
|---|---|
| R5 nhận được route gì? | |
| R5 ping `10.1.0.1` — được không? | |
| R5 ping `10.1.99.1` *(không ai dùng)* — chuyện gì xảy ra? | |
| Gói đó chết ở đâu? | |
| `show ip route \| include Null0` trên ABR-A hiện gì? | |

> 🔑 Gói bị **drop im lặng** tại ABR — đây gọi là **blackhole**.
> Route `Null0` do IOS tự sinh chính là thứ "nuốt" chúng.

### Lỗi 3 — `area range` trên router không phải ABR

```cisco
R2(config)# router ospf 1
R2(config-router)# area 1 range 10.1.0.0 255.255.252.0
```

| | |
|---|---|
| IOS có báo lỗi không? | |
| R5 nhận được route gì? Có đổi không? | |
| Vì sao lệnh này **không có tác dụng**? | |

### Lỗi 4 *(tự chọn)* — Area ID lệch trên cùng một link

```cisco
ABR-A(config-router)# no network 10.0.20.2 0.0.0.0 area 1
ABR-A(config-router)# network 10.0.20.2 0.0.0.0 area 2
```

| | |
|---|---|
| `show ip ospf neighbor` trên R2 hiện gì? | |
| Lệnh nào lộ ra nguyên nhân? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Area 2 có `10.2.0.0/24` và `10.2.1.0/24`. Viết lệnh summarize gọn nhất, và nói rõ
   lệnh đó chạy trên **router nào**.
2. Bạn muốn **giấu** mạng quản trị `10.1.9.0/24` của Area 1, không cho area khác thấy.
   Viết lệnh.
3. ABR-A phải giữ LSDB của mấy area? Nếu bạn thêm Area 4 và Area 5 vào ABR-A thì sao?
4. Vì sao thay đổi một link trong Area 1 **không** làm R5 (Area 2) chạy lại SPF đầy đủ?
   Nếu có summarization thì càng thế nào?

<details>
<summary>Đáp án</summary>

**1.** `10.2.0.0/24` và `10.2.1.0/24` là **2 subnet liên tiếp** → gom thành `/23`:

```cisco
ABR-B(config)# router ospf 1
ABR-B(config-router)# area 2 range 10.2.0.0 255.255.254.0
```

Chạy trên **ABR-B** — vì đó là ABR của Area 2. Chạy trên ABR-A hay R5 đều **không có
tác dụng**.

**2.**

```cisco
ABR-A(config-router)# area 1 range 10.1.9.0 255.255.255.0 not-advertise
```

Từ khoá `not-advertise` làm ABR **không quảng bá** dải này ra area khác.
Router trong Area 1 vẫn thấy nhau bình thường; area khác hoàn toàn không biết nó tồn tại.

**3.** ABR-A giữ LSDB của **2 area** *(Area 0 và Area 1)* — xác nhận bằng
`show ip ospf` → `Number of areas in this router is 2`.

Thêm Area 4 và Area 5 → ABR-A phải giữ **4 LSDB**, chạy **4 bộ SPF** riêng.

```text
→ Tốn CPU và RAM gấp bội
→ Mất đi phần lớn lợi ích của việc chia area
```

👉 Nguyên tắc: **đừng để một ABR gánh quá nhiều area** *(thực tế nên ≤ 3)*.

**4.** Vì **LSA Type 1 và Type 2 không vượt qua ABR**.

```text
Link trong Area 1 thay đổi
  → LSA Type 1 mới flood trong Area 1
  → Router Area 1 chạy lại SPF ✅
  → ABR-A cập nhật, có thể tạo LSA Type 3 MỚI (nếu cost đổi)
  → R5 nhận Type 3 → chỉ cập nhật route, KHÔNG chạy SPF đầy đủ
```

**Nếu có summarization:** route tổng hợp `10.1.0.0/22` **không đổi** dù một link
bên trong Area 1 thay đổi → ABR **không gửi Type 3 mới** → R5
**không nhận được gì cả**.

👉 Đây chính là lợi ích lớn nhất của summarization: **cách ly sự bất ổn** —
một sự cố trong Area 1 hoàn toàn vô hình với Area 2.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Bước 3 — số LSA tham khảo

| Router | LSA Type 1 | LSA Type 3 | Ghi chú |
|---|:---:|:---:|---|
| R1 *(Area 1)* | 3 *(R1, R2, ABR-A)* | nhiều | **Không** thấy LSA Type 1 của R5 |
| R5 *(Area 2)* | 2 *(R5, ABR-B)* | nhiều | **Không** thấy LSA Type 1 của R1, R2 |
| ABR-A | Area 1: 3 · Area 0: 2 | | Giữ **2 LSDB riêng biệt** |

**Vì sao R1 không thấy LSA Type 1 của R5:** LSA Type 1 **chỉ lan trong một area**.
ABR-A dịch thông tin Area 1 thành **Type 3** để gửi vào Area 0; ABR-B lại tạo Type 3 mới
để gửi vào Area 2. R1 chỉ biết *"có mạng `10.2.0.0/24` ở hướng ABR-A, cost X"* —
**không biết R5 tồn tại**.

### Bước 4 — summarization

| | Số route `10.1.x.x` trên R5 |
|---|:---:|
| Trước | **4** *(`10.1.0.0/24`, `10.1.1.0/24`, `10.1.2.0/24`, `10.1.3.0/24`)* |
| Sau | **1** *(`10.1.0.0/22`)* |

**Route `Null0` trên ABR-A:**

```text
O   10.1.0.0/22 is a summary, Null0
```

IOS **tự sinh** route này để **chống routing loop**: nếu ABR quảng bá `/22` mà có phần
chưa dùng *(vd `10.1.3.200` khi `10.1.3.0/24` tồn tại nhưng host đó không có)*,
gói tới phần đó sẽ bị **vứt tại ABR** thay vì chạy vòng giữa ABR và Area 1.

### Giải thích các lỗi BREAK

**Lỗi 1 — Area không chạm Area 0:**

| Quan sát | Giải thích |
|---|---|
| R6 **có** neighbor với R5 ✅ | Area 3 hoạt động bình thường bên trong |
| R6 **có** thấy route Area 1, 2 ✅ | R5 dịch Type 3 từ Area 2 vào Area 3 |
| **R1 KHÔNG thấy `10.6.0.0/24`** ❌ | R5 **không phải ABR hợp lệ** — nó không có chân Area 0, nên Type 3 nó tạo **không được chấp nhận** vào backbone |
| `show ip ospf` trên R5 | Hiện `It is an area border router` nhưng **không có Area 0** trong danh sách |

**Triệu chứng đặc trưng:** *"Area 3 thấy được mọi nơi, nhưng mọi nơi không thấy Area 3"* —
một chiều.

**Sửa:** thiết kế lại để Area 3 nối trực tiếp Area 0, hoặc *(giải pháp tạm)* dùng
**virtual link** qua Area 2.

**Lỗi 2 — blackhole:**

| Quan sát | Giải thích |
|---|---|
| R5 nhận `O IA 10.1.0.0/16` | ABR quảng bá dải rộng hơn thực tế |
| Ping `10.1.0.1` ✅ | Mạng này có thật |
| Ping `10.1.99.1` → **timeout im lặng** | Gói được route tới ABR-A, khớp route `10.1.0.0/16 → Null0` → **bị vứt bỏ không báo gì** |
| `show ip route \| include Null0` | `O 10.1.0.0/16 is a summary, Null0` |

> ⚠️ Nguy hiểm vì **không có thông báo lỗi**. Với dải `/16` phủ `10.1.0.0`–`10.1.255.255`
> mà chỉ 4 subnet `/24` tồn tại, **99% không gian địa chỉ là blackhole**.

**Lỗi 3 — `area range` sai chỗ:**

IOS **nhận lệnh, không báo lỗi gì**. R5 vẫn nhận **4 route riêng lẻ** như cũ.

Lý do: `area range` chỉ có tác dụng ở **điểm biên giữa hai area** — tức là **ABR**.
R2 nằm hoàn toàn trong Area 1, không dịch LSA Type 1 → Type 3, nên không có gì để gom.

👉 **Bẫy im lặng**: cấu hình trông đúng, không lỗi, nhưng không làm gì cả.

**Lỗi 4 — Area ID lệch:**

```text
# output điển hình — tự verify trên lab của bạn
R2#  show ip ospf neighbor
→ ABR-A BIẾN MẤT khỏi danh sách
```

Lệnh lộ nguyên nhân:

```cisco
R2#     show ip ospf interface Gi0/2 | include Area
   Internet Address 10.0.20.1/30, Area 1
ABR-A#  show ip ospf interface Gi0/1 | include Area
   Internet Address 10.0.20.2/30, Area 2      ← LỆCH
```

**Area ID** là một trong **6 thứ phải khớp** để OSPF lên neighbor *(Lesson 22)*.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Số LSA ở R1 vs R5: ___ / ___
- Số route trước/sau summarize: ___ → ___
- Lỗi 1 (area không chạm Area 0) có triệu chứng gì đặc trưng? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
