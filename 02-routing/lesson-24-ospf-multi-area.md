# LESSON 24 — OSPF Multi-Area · ABR · Summarization

> 📌 Lesson cuối Phase 2. Nó trả lời: *OSPF scale lên hàng trăm router bằng cách nào?*

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 22](./lesson-22-ospf-single-area.md), [Lesson 23](./lesson-23-ospf-cost-lsdb-lsa.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Giải thích **3 vấn đề** mà multi-area giải quyết
- [ ] Phân biệt vai trò **Internal · ABR · ASBR · Backbone router**
- [ ] Giải thích vì sao **mọi area phải nối với Area 0**
- [ ] Cấu hình OSPF multi-area và đọc route `O IA`
- [ ] Cấu hình summarization trên ABR và nói được nó tiết kiệm gì

## 2. Prerequisite

- LSDB, LSA Type 1/2/3 *(Lesson 23)*
- Neighbor state, DR/BDR *(Lesson 22)*
- IP plan có quy hoạch để summarize được *(Lesson 07)*

---

## 3. Concept

### Vấn đề của single-area khi mạng lớn

| Vấn đề | Chi tiết |
|---|---|
| **LSDB khổng lồ** | 200 router = 200+ LSA Type 1, mỗi router phải giữ hết |
| **SPF chạy liên tục** | Bất kỳ link nào ở bất kỳ đâu thay đổi → **mọi** router tính lại toàn bộ |
| **Flooding tràn lan** | Một link flap ở góc mạng làm cả mạng phải xử lý LSA |

### Giải pháp: chia area

```text
                    ┌─────────────────┐
         Area 1 ────┤    AREA 0       ├──── Area 2
                ABR │   (BACKBONE)    │ ABR
                    └────────┬────────┘
                             │ ABR
                          Area 3
```

| Hiệu quả | Giải thích |
|---|---|
| **LSDB nhỏ hơn** | Mỗi router chỉ giữ LSDB của **area mình** |
| **SPF phạm vi hẹp** | Thay đổi trong Area 1 → chỉ router Area 1 chạy lại SPF |
| **Flooding bị chặn** | LSA Type 1/2 **không vượt qua** ABR |
| **Summarization** | ABR gom nhiều subnet thành một route |

> 🔑 **Area là ranh giới của LSA flooding và của SPF.** Đó là toàn bộ ý nghĩa của nó.

### Bốn vai trò router

| Vai trò | Định nghĩa |
|---|---|
| **Internal Router** | Mọi interface nằm trong **cùng một** area |
| **Backbone Router** | Có ít nhất một interface trong **Area 0** |
| **ABR** (Area Border Router) | Có interface ở **Area 0** **và** ít nhất một area khác |
| **ASBR** (Autonomous System Boundary Router) | Nối OSPF với **thế giới bên ngoài** — redistribute route từ static/BGP/EIGRP vào |

> ⚠️ **ABR bắt buộc phải có một chân trong Area 0.** Router nối Area 1 với Area 2
> mà không chạm Area 0 thì **không phải ABR hợp lệ** — và route sẽ không lan đúng.

### Quy tắc Area 0

```text
MỌI area phải nối TRỰC TIẾP với Area 0 (backbone).
```

```text
✅ ĐÚNG                        ❌ SAI
   Area 1 ─ ABR ─ Area 0          Area 1 ─ R ─ Area 2 ─ ABR ─ Area 0
   Area 2 ─ ABR ─ Area 0          (Area 1 không chạm Area 0)
```

**Vì sao:** OSPF chống loop **trong** một area bằng SPF (mọi router có bản đồ đầy đủ).
Nhưng **giữa các area**, router chỉ nhận LSA Type 3 — một "lời kể" kiểu distance vector,
không kèm bản đồ. Nếu các area nối vòng với nhau, loop sẽ xảy ra.

Topology **hình sao quanh Area 0** đảm bảo không có vòng.

> 💡 Trường hợp bất khả kháng có **virtual link** để nối area lạc sang Area 0 —
> nhưng đó là giải pháp tạm, không phải thiết kế. Học ở CCNP.

### LSA vượt biên thế nào

```text
AREA 1                      ABR                      AREA 0
──────────────────────      ───                      ────────────────
LSA Type 1 (router)     ──▶ DỪNG — không qua
LSA Type 2 (network)    ──▶ DỪNG — không qua
                            │
                            │ ABR DỊCH thành:
                            ▼
                        LSA Type 3 (summary) ──────▶ lan vào Area 0
                        "Area 1 có các mạng: 10.1.0.0/24, 10.1.1.0/24..."
```

> 🔑 **ABR là bộ phiên dịch.** Nó không chuyển tiếp chi tiết topology của area này
> sang area kia — nó chỉ nói *"bên kia có những mạng này, cost bấy nhiêu"*.
>
> Đây chính là lý do LSDB nhỏ lại: router Area 0 không cần biết Area 1 có bao nhiêu
> router nối với nhau thế nào.

### Route code trong routing table

| Code | Nghĩa |
|---|---|
| `O` | **Intra-area** — mạng trong cùng area |
| `O IA` | **Inter-area** — mạng ở area khác, học qua ABR (LSA Type 3) |
| `O E1` | External Type 1 — cost ngoài **+ cost nội bộ** |
| `O E2` | External Type 2 — **chỉ cost ngoài** *(mặc định khi redistribute)* |

### Summarization

```text
Không summarize — ABR quảng bá 4 LSA Type 3:
  10.1.0.0/24
  10.1.1.0/24
  10.1.2.0/24
  10.1.3.0/24

Có summarize — ABR quảng bá 1 LSA Type 3:
  10.1.0.0/22        ← bao trọn cả 4 subnet
```

```cisco
ABR(config-router)# area 1 range 10.1.0.0 255.255.252.0
```

| Lợi ích | Chi tiết |
|---|---|
| **LSDB nhỏ hơn** | 1 LSA thay vì 4 |
| **Routing table nhỏ hơn** | 1 route thay vì 4 |
| **Ổn định hơn** ⭐ | Một subnet trong Area 1 flap → **route tổng hợp không đổi** → area khác **không phải chạy lại SPF** |

> ⭐ Lợi ích thứ ba mới là quan trọng nhất. Summarization **cách ly sự bất ổn**:
> sự cố trong một area không làm rung chuyển cả mạng.

> ⚠️ Summarization **chỉ khả thi nếu IP plan được quy hoạch theo area** —
> đúng như đã học ở [Lesson 07](../00-foundation/lesson-07-vlsm-va-ip-plan.md).
> Chia IP lộn xộn thì không gom được gì.

---

## 4. Why?

> **Khi nào cần chia area?**

| Dấu hiệu | Ngưỡng tham khảo |
|---|---|
| Số router trong một area | **> 50** → cân nhắc chia |
| SPF chạy quá thường xuyên | `show ip ospf` thấy số lần tăng nhanh |
| LSDB lớn, router yếu CPU cao | |
| Mạng nhiều site địa lý | Mỗi site một area là tự nhiên |

> 🔧 Với mạng doanh nghiệp vừa (< 30 router), **single-area là đủ và đơn giản hơn**.
> Đừng chia area chỉ vì "thấy chuyên nghiệp" — nó thêm độ phức tạp.

> **Vì sao không dùng nhiều area nhỏ cho mọi thứ?**

Mỗi ABR phải giữ LSDB của **mọi area nó chạm vào**. Chia quá nhỏ → ABR gánh nặng,
và số LSA Type 3 tăng lên bù lại phần tiết kiệm được.

---

## 5. How does it work? — ví dụ đầy đủ

```text
         Area 1                Area 0              Area 2
   R1 ──── R2 ──────── [ABR-A] ──── [ABR-B] ──────── R5 ──── R6
  10.1.x            (backbone)                      10.2.x
```

| Router | Vai trò | LSDB chứa gì |
|---|---|---|
| R1, R2 | Internal (Area 1) | LSA Type 1/2 của **Area 1** + Type 3 từ ABR-A |
| ABR-A | **ABR** | LSDB của **Area 1 VÀ Area 0** |
| ABR-B | **ABR** | LSDB của **Area 0 VÀ Area 2** |
| R5, R6 | Internal (Area 2) | LSA Type 1/2 của **Area 2** + Type 3 từ ABR-B |

### R1 học về mạng `10.2.5.0/24` (Area 2) thế nào

```text
1. R5 tạo LSA Type 1: "tôi nối 10.2.5.0/24, cost 1"  → flood trong Area 2
2. ABR-B nhận, DỊCH thành LSA Type 3: "10.2.5.0/24, cost 2" → gửi vào Area 0
3. ABR-A nhận Type 3 từ Area 0, TẠO Type 3 MỚI: "10.2.5.0/24, cost 3" → gửi vào Area 1
4. R1 nhận, cài route:
      O IA  10.2.5.0/24 [110/4] via <ABR-A>
```

> 🔑 R1 **không biết gì** về topology Area 2 — không biết R5, R6 tồn tại, không biết
> chúng nối với nhau thế nào. Nó chỉ biết *"mạng đó ở hướng ABR-A, cost 4"*.
>
> Đó chính là cách multi-area giảm LSDB.

---

## 6. Packet Flow — không áp dụng

Gói tin đi qua area không có gì đặc biệt — không có tag, không có encapsulation thêm.
Area là khái niệm **chỉ tồn tại trong control plane** của OSPF.

---

## 7. Real-world Example

🏭 **Thiết kế multi-area cho doanh nghiệp 3 site**

```text
                    ┌──── AREA 0 ────┐
                    │  Core HN ══ Core SG  │
                    └───┬──────────┬───┘
                   ABR  │          │  ABR
              ┌─────────┴──┐    ┌──┴─────────┐
              │  AREA 1    │    │  AREA 2    │
              │  Hà Nội    │    │  Sài Gòn   │
              │ 10.1.0.0/16│    │ 10.2.0.0/16│
              └────────────┘    └────────────┘
```

IP plan theo area → summarize được gọn gàng:

```cisco
ABR-HN(config-router)# area 1 range 10.1.0.0 255.255.0.0
ABR-SG(config-router)# area 2 range 10.2.0.0 255.255.0.0
```

Kết quả: router ở Hà Nội chỉ thấy **một route** `10.2.0.0/16` cho toàn bộ Sài Gòn,
thay vì 20 route `/24`.

Và quan trọng hơn: một switch ở Sài Gòn reboot → route `10.2.0.0/16` **không đổi** →
Hà Nội **không phải chạy lại SPF**.

🏭 **Lỗi thiết kế: area không chạm Area 0**

```text
Area 1 ─── R ─── Area 2 ─── ABR ─── Area 0
```

Area 1 không nối trực tiếp Area 0 → route của Area 1 **không lan ra ngoài**.
Triệu chứng: Area 1 thấy được mọi nơi, nhưng mọi nơi **không thấy** Area 1.

Sửa: đổi thiết kế, hoặc (tạm) dùng virtual link.

🏭 **Summarize sai dải — gây blackhole**

```cisco
ABR(config-router)# area 1 range 10.1.0.0 255.255.0.0
```

ABR quảng bá `10.1.0.0/16` — nhưng Area 1 thực tế chỉ dùng `10.1.0.0/24` và `10.1.1.0/24`.
Gói tới `10.1.99.5` sẽ được route vào Area 1 rồi **bị drop** vì không có ai dùng dải đó.

> 🔧 IOS tự thêm một route `Null0` cho dải summarize trên ABR để tránh loop.
> Nhưng gói vẫn bị **drop im lặng** — thiết kế IP plan đúng ngay từ đầu vẫn là cách tốt nhất.

---

## 8. Cisco CLI

```cisco
! ═══════ ABR — có chân ở 2 area ═══════
ABR-A(config)# router ospf 1
ABR-A(config-router)# router-id 10.10.10.10
ABR-A(config-router)# network 10.1.0.1 0.0.0.0 area 1      ! chân trong Area 1
ABR-A(config-router)# network 10.0.0.1 0.0.0.0 area 0      ! chân trong Area 0

! ═══════ SUMMARIZATION (chỉ trên ABR) ═══════
ABR-A(config-router)# area 1 range 10.1.0.0 255.255.0.0

! Không quảng bá dải này ra ngoài
ABR-A(config-router)# area 1 range 10.1.9.0 255.255.255.0 not-advertise

! ═══════ ROUTER BÌNH THƯỜNG trong Area 1 ═══════
R1(config)# router ospf 1
R1(config-router)# router-id 1.1.1.1
R1(config-router)# network 10.1.1.1 0.0.0.0 area 1
R1(config-router)# network 10.1.0.2 0.0.0.0 area 1

! ═══════ DEFAULT ROUTE từ ASBR ═══════
ASBR(config-router)# default-information originate
ASBR(config-router)# default-information originate always   ! quảng bá kể cả khi mình không có

! ═══════ KIỂM TRA ═══════
R1# show ip ospf
R1# show ip ospf border-routers
R1# show ip ospf database summary
R1# show ip route ospf
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `network <ip> 0.0.0.0 area N` | Gán interface vào area | Một router có thể ở nhiều area |
| `area N range <net> <mask>` | **Summarize** | ⚠️ Chỉ chạy trên **ABR** |
| `not-advertise` | Giấu dải này khỏi area khác | Dùng để che mạng quản trị |
| `default-information originate` | Quảng bá default route vào OSPF | Thường chạy trên router biên |
| `show ip ospf border-routers` | Đường tới ABR/ASBR | |

> ⚠️ `area range` **chỉ có tác dụng trên ABR**. Gõ trên router thường thì không lỗi
> nhưng cũng không làm gì cả — một bẫy im lặng.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route ospf
      10.0.0.0/8 is variably subnetted, 8 subnets, 3 masks
O        10.1.2.0/24 [110/2] via 10.1.0.1, 00:10:12, GigabitEthernet0/0
O IA     10.0.0.0/24 [110/3] via 10.1.0.1, 00:09:55, GigabitEthernet0/0
O IA     10.2.0.0/16 [110/4] via 10.1.0.1, 00:09:55, GigabitEthernet0/0
O*E2     0.0.0.0/0   [110/1] via 10.1.0.1, 00:09:50, GigabitEthernet0/0
```

| Code | Nghĩa ở đây |
|---|---|
| `O` | Mạng **trong Area 1** (cùng area với R1) |
| `O IA` | Mạng ở **area khác**, học qua ABR |
| `O IA 10.2.0.0/16` | **Route đã được summarize** — cả Sài Gòn gom thành 1 dòng ✅ |
| `O*E2` | Default route **external**, do ASBR quảng bá |

```text
# output điển hình — tự verify trên lab của bạn
ABR-A# show ip ospf
 Routing Process "ospf 1" with ID 10.10.10.10
 It is an area border router
 Number of areas in this router is 2. 2 normal 0 stub 0 nssa
    Area BACKBONE(0)
        Number of interfaces in this area is 1
        SPF algorithm executed 12 times
        Number of LSA 9
    Area 1
        Number of interfaces in this area is 1
        SPF algorithm executed 8 times
        Number of LSA 6
```

**Đọc gì:**

| Dòng | Ý nghĩa |
|---|---|
| `It is an area border router` | ✅ Xác nhận đây là **ABR** |
| `Number of areas in this router is 2` | Nó chạm 2 area |
| Mỗi area có `SPF executed` và `Number of LSA` **riêng** | ⭐ Bằng chứng area cách ly nhau |

> 🔑 Nhìn hai dòng `SPF algorithm executed` khác nhau là thấy ngay giá trị của multi-area:
> SPF của Area 1 chạy **độc lập** với SPF của Area 0.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip ospf border-routers
OSPF Process 1 internal Routing Table

Codes: i - Intra-area route, I - Inter-area route

i 10.10.10.10 [1] via 10.1.0.1, GigabitEthernet0/0, ABR, Area 1, SPF 8
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Area X thấy mọi nơi, nhưng mọi nơi không thấy Area X | **Area không chạm Area 0** | `show ip ospf` trên ABR nghi ngờ | Thiết kế lại, hoặc virtual link |
| Không có route `O IA` nào | ABR không hoạt động đúng | `show ip ospf \| include border` | Kiểm tra ABR có chân Area 0 |
| `area range` không có tác dụng | Gõ trên router **không phải ABR** | `show ip ospf \| include border` | Chuyển lệnh sang đúng ABR |
| Route summarize nhưng traffic bị drop | Dải summarize **rộng hơn** thực tế | `show ip route` trên ABR có `Null0` | Thu hẹp dải, hoặc sửa IP plan |
| Neighbor không lên giữa 2 area | **Area ID lệch** trên cùng một link | `show ip ospf interface <int>` 2 đầu | Đồng bộ area |
| LSDB vẫn lớn dù đã chia area | ABR giữ LSDB của mọi area nó chạm | `show ip ospf` | Giảm số area trên mỗi ABR |
| Default route không lan vào area | Thiếu `default-information originate` | `show ip route \| include O\*` | Thêm trên ASBR |

---

## 11. LAB

🧪 **LAB 24 — OSPF multi-area & summarization** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- 5 router: 2 trong Area 1, 1 ABR, 2 trong Area 0
- Verify route `O` vs `O IA` trên router Area 1
- So `show ip ospf database` ở router Area 1 và router Area 0 → **khác nhau**
  (bằng chứng area cách ly LSA)
- Cấu hình `area 1 range`, so số dòng routing table **trước và sau**
- **BREAK bắt buộc:** (1) tạo Area 2 **không chạm Area 0** → quan sát route không lan;
  (2) `area range` với dải rộng hơn thực tế → tạo blackhole;
  (3) đặt area ID lệch một đầu link → neighbor không lên

## 12. Challenge

1. Router có 3 interface: Area 0, Area 1, Area 2. Nó là loại router gì? LSDB của nó
   chứa bao nhiêu area?
2. Area 1 có các mạng `10.1.0.0/24` → `10.1.7.0/24`. Viết lệnh summarize gọn nhất.
   Dải summarize là gì?
3. Vì sao thay đổi trong Area 1 **không** làm router Area 2 chạy lại SPF?
4. Bạn thấy `O E2 192.168.50.0/24 [110/20]`. Route này đến từ đâu? Vì sao metric
   không đổi dù đi qua nhiều hop?

<details>
<summary>Đáp án</summary>

**1.** Đó là **ABR** (có chân trong Area 0 và area khác). LSDB của nó chứa **3 area** —
mỗi area một LSDB riêng biệt.

```text
show ip ospf  →  "Number of areas in this router is 3"
                 "It is an area border router"
```

👉 Đây cũng là lý do không nên để một ABR gánh quá nhiều area: nó phải giữ và tính SPF
cho tất cả.

**2.** Các mạng `10.1.0.0/24` → `10.1.7.0/24` là 8 subnet liên tiếp:

```text
10.1.0.0  →  10.1.7.255
8 subnet /24 = 2^3 → mượn ngược 3 bit → /24 − 3 = /21
```

```cisco
ABR(config-router)# area 1 range 10.1.0.0 255.255.248.0
```

Dải summarize: **`10.1.0.0/21`** (bao `10.1.0.0` – `10.1.7.255`).

**3.** Vì **LSA Type 1 và Type 2 không vượt qua ABR**. ABR chỉ dịch thành LSA Type 3
("có mạng này, cost bấy nhiêu").

Khi một link trong Area 1 chết:
- Router **trong Area 1** nhận LSA Type 1 mới → chạy lại SPF
- ABR cập nhật, có thể gửi Type 3 mới (nếu cost đổi)
- Router Area 2 chỉ nhận **Type 3** → cập nhật route, **không chạy SPF đầy đủ**

Và nếu có **summarization**, route tổng hợp thậm chí **không đổi** → Area 2
**không nhận được gì cả**. Hoàn toàn cách ly.

**4.** `O E2` = **External Type 2** — route từ ngoài OSPF được **redistribute** vào
bởi một **ASBR** (từ static, BGP, EIGRP, hoặc protocol khác).

Metric không đổi vì **đó là định nghĩa của E2**:

| | **E1** | **E2** |
|---|---|---|
| Metric | Cost ngoài **+ cost nội bộ tới ASBR** | **Chỉ cost ngoài**, không cộng gì |
| Mặc định khi redistribute | | ✅ **Đây là mặc định** |
| Dùng khi | Muốn chọn ASBR gần nhất | Mọi đường ra ngoài tương đương nhau |

⚠️ Hệ quả thực tế: với E2, nếu có **2 ASBR** cùng quảng bá một route với cùng metric,
router có thể chọn ASBR **ở xa hơn** — vì nó không tính cost nội bộ. Khi đó nên dùng E1.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 4 vai trò router · quy tắc Area 0 · `O` vs `O IA` vs `O E1/E2` | ⬜ |
| **L2** Explain | Giải thích vì sao LSA Type 1/2 không vượt ABR | ⬜ |
| **L3** Configure | OSPF 2 area + summarization trên ABR | ⬜ |
| **L4** Troubleshoot | Area không chạm Area 0 → nhận ra từ triệu chứng | ⬜ |
| **L5** Design | Thiết kế area + IP plan cho công ty 3 site, 60 router | ⬜ |

## 14. Summary

**Key concepts**

- Multi-area giải quyết: **LSDB lớn · SPF chạy liên tục · flooding tràn lan**
- ⭐ **Area là ranh giới của LSA flooding và của SPF**
- 4 vai trò: **Internal · Backbone · ABR · ASBR**
- ⭐ **Mọi area phải nối trực tiếp Area 0** — để chống loop giữa các area
- **LSA Type 1/2 không vượt ABR**; ABR dịch thành **Type 3**
- `O` = intra-area · `O IA` = inter-area · `O E1/E2` = external
- `area N range` **chỉ chạy trên ABR**
- ⭐ Giá trị lớn nhất của summarization: **cách ly sự bất ổn** giữa các area
- Summarization chỉ khả thi nếu **IP plan quy hoạch theo area**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `network <ip> 0.0.0.0 area N` | Gán interface vào area |
| `area N range <net> <mask>` | Summarize — **chỉ trên ABR** |
| `show ip ospf` | Có phải ABR không, SPF mỗi area chạy mấy lần |
| `show ip ospf border-routers` | Đường tới ABR/ASBR |
| `show ip route ospf` | Phân biệt `O` và `O IA` |
| `default-information originate` | Quảng bá default route vào OSPF |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Area không chạm Area 0 | Route của area đó không lan ra ngoài |
| `area range` trên router không phải ABR | Không lỗi, nhưng **không có tác dụng** |
| Summarize dải rộng hơn thực tế | Blackhole — gói bị drop im lặng |
| Chia area khi mạng còn nhỏ | Thêm phức tạp không cần thiết |
| Để một ABR gánh quá nhiều area | ABR giữ LSDB của tất cả → mất lợi ích |
| Area ID lệch trên cùng một link | Neighbor không lên |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 24 với đủ 3 lỗi BREAK.
2. So `show ip ospf database` ở router Area 1 và Area 0 — ghi lại số LSA mỗi bên.
   Đây là bằng chứng trực tiếp của việc area cách ly LSA.
3. Đếm số dòng `show ip route ospf` **trước và sau** khi bật summarization.

```markdown
- [YYYY-MM-DD] Lesson 24 — OSPF multi-area: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 2

Làm **[Mini Exam Phase 2](./review-phase02.md)** trước khi sang
[Phase 3 — Services](../03-services/README.md).

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 4 vai trò, quy tắc Area 0, `O IA`, `area range`, LSA nào vượt biên |
| 🔧 **Engineer** | Summarize theo IP plan; không chia area khi mạng nhỏ; ABR đừng gánh quá nhiều area |
| 🏭 **Production** | Summarization cách ly sự bất ổn — một site flap không làm cả mạng chạy SPF |

### 🔗 Liên kết

- ⬅️ [Lesson 23 — OSPF Cost, LSDB, LSA](./lesson-23-ospf-cost-lsdb-lsa.md)
- 📝 [Mini Exam Phase 2](./review-phase02.md)
- ➡️ [Phase 3 — Services](../03-services/README.md)
- 🔜 Stub area, NSSA, virtual link: [`CCNP-Encor` Module 04B](https://github.com/hiepnguyen775/CCNP-Encor)
