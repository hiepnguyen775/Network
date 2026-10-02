# LESSON 20 — Administrative Distance · Metric · Longest Prefix Match ⭐

> 📌 Lesson ngắn nhưng **quan trọng bậc nhất của cả CCNA**. Nó trả lời đúng một câu hỏi:
> *khi có nhiều route cùng khớp, router chọn cái nào?*

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 18](./lesson-18-router-va-routing-table.md), [Lesson 19](./lesson-19-static-default-route.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Nói đúng **thứ tự 3 tiêu chí** router dùng để chọn route
- [ ] Giải thích vì sao **longest prefix match xét TRƯỚC** AD
- [ ] Thuộc bảng AD của các nguồn route
- [ ] Phân biệt AD và Metric — hai thứ rất hay bị nhầm
- [ ] Dự đoán được route nào thắng khi cho một bảng định tuyến

## 2. Prerequisite

- Đọc được `show ip route`, hiểu `[AD/metric]` *(Lesson 18)*
- Static route, floating static *(Lesson 19)*

---

## 3. Concept

### Thứ tự quyết định — ba bước, không được đảo

```text
1. LONGEST PREFIX MATCH   →  route nào khớp CỤ THỂ nhất?
   │
   │  (nếu nhiều route cùng prefix length)
   ▼
2. ADMINISTRATIVE DISTANCE →  nguồn nào ĐÁNG TIN hơn?
   │
   │  (nếu cùng AD, tức cùng một routing protocol)
   ▼
3. METRIC                  →  đường nào TỐT hơn theo protocol đó?
```

> ⭐ **Đây là câu hỏi phỏng vấn kinh điển và là chỗ sai nhiều nhất.**
> Rất nhiều người trả lời "AD trước" — **sai**. Longest prefix match luôn xét trước.

### Bước 1 — Longest Prefix Match

Router chọn route có **số bit mạng nhiều nhất** mà vẫn khớp đích.

```text
Gói tới 10.0.2.50

S   10.0.0.0/8      [1/0]    → khớp  (8 bit)
O   10.0.2.0/24     [110/2]  → khớp  (24 bit)   ← THẮNG
S   10.0.2.48/30    [1/0]    → khớp  (30 bit)   ← THẮNG THẬT SỰ
S*  0.0.0.0/0       [1/0]    → khớp  (0 bit)
```

`10.0.2.48/30` bao `10.0.2.48` – `10.0.2.51` → chứa `.50` → **30 bit, cụ thể nhất → thắng**.

> 🔑 Chú ý: route `/30` có AD=1 (static) và route `/24` có AD=110 (OSPF).
> **AD không được xét** vì chúng khác prefix length. Prefix dài hơn thắng, hết chuyện.

### Bước 2 — Administrative Distance

AD = **mức độ tin cậy của NGUỒN route**. Thấp hơn = đáng tin hơn.

| Nguồn | AD |
|---|:---:|
| **Connected** | **0** |
| **Static** | **1** |
| EIGRP summary | 5 |
| **eBGP** | **20** |
| **EIGRP (internal)** | **90** |
| IGRP | 100 |
| **OSPF** | **110** |
| IS-IS | 115 |
| **RIP** | **120** |
| EIGRP (external) | 170 |
| **iBGP** | **200** |
| **Unknown / không dùng** | **255** |

> 💡 Nhớ 5 con số quan trọng nhất: **0 · 1 · 90 · 110 · 120**
> (Connected · Static · EIGRP · OSPF · RIP).

> ⚠️ **AD = 255** nghĩa là route **không bao giờ được dùng**. Một số kỹ thuật
> dùng AD=255 để vô hiệu hoá route mà không xoá nó.

### Bước 3 — Metric

Metric = **giá trị đường đi** *trong cùng một protocol*. Mỗi protocol tính khác nhau:

| Protocol | Metric dựa trên |
|---|---|
| **OSPF** | **Cost** = `reference bandwidth / bandwidth` |
| **EIGRP** | Công thức tổng hợp: bandwidth + delay (mặc định) |
| **RIP** | **Hop count** — số router phải qua (tối đa 15) |
| Static | Luôn **0** |
| BGP | Không dùng metric đơn giản — có cả một quy trình chọn đường riêng |

> ⚠️ **Không so metric giữa hai protocol khác nhau.** Metric 2 của OSPF và metric 2 của RIP
> hoàn toàn không liên quan. Đó chính là lý do **AD tồn tại** — để so sánh *giữa các nguồn*.

### AD vs Metric — bảng phân biệt

| | **Administrative Distance** | **Metric** |
|---|---|---|
| So sánh cái gì | **Giữa các nguồn khác nhau** | **Trong cùng một protocol** |
| Ai đặt | Cisco quy định sẵn (sửa được) | Protocol tự tính |
| Ví dụ | OSPF 110 vs RIP 120 → OSPF thắng | OSPF cost 4 vs cost 8 → cost 4 thắng |
| Vị trí trong `[110/2]` | **110** | **2** |

---

## 4. Why?

> **Vì sao cần AD?**

Router có thể học **cùng một mạng** từ nhiều nguồn:

```text
10.0.5.0/24 học được từ:
  - Static (ai đó gõ tay)        AD 1
  - OSPF (láng giềng quảng bá)   AD 110
  - RIP (láng giềng khác)        AD 120
```

Không thể so metric — chúng dùng đơn vị khác nhau. Cần một thang đo chung về
**độ tin cậy của nguồn**. Đó là AD.

Logic xếp hạng rất hợp lý:

| Vì sao thứ tự này | |
|---|---|
| Connected (0) | Tôi **nhìn thấy tận mắt** — không thể sai |
| Static (1) | **Con người** đã quyết định — tin hơn máy tự học |
| EIGRP (90) < OSPF (110) | Cisco tin EIGRP hơn *(thiên vị sản phẩm nhà)* |
| OSPF (110) < RIP (120) | OSPF thông minh hơn RIP nhiều |
| iBGP (200) | Rất chậm hội tụ, chỉ dùng khi không còn gì khác |

> **Vì sao longest prefix match xét trước AD?**

Vì **mục đích của routing là đi tới đúng chỗ**, không phải tin ai hơn.

```text
Gói tới 10.0.2.50

O   10.0.0.0/8    [110/2]   → "tôi biết đường tới cả 10.x.x.x"
S   10.0.2.0/24   [1/0]     → "tôi biết đường tới ĐÚNG mạng 10.0.2.x"
```

Route `/24` **biết chính xác hơn** về đích. Route `/8` chỉ biết chung chung.
Thông tin cụ thể hơn luôn có giá trị hơn — bất kể ai cung cấp.

> 💡 Hình ảnh dễ nhớ: hỏi đường tới "số 15 ngõ 3 phố X".
> Người nói *"đi về hướng quận Y"* (prefix ngắn) và người nói *"ngõ 3 ở ngay kia, số 15 bên trái"*
> (prefix dài). Bạn nghe ai? Người cụ thể hơn — kể cả khi người kia đáng tin hơn về mặt lý lịch.

---

## 5. How does it work? — ví dụ đầy đủ

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route
S*    0.0.0.0/0        [1/0]     via 203.0.113.1
      10.0.0.0/8 is variably subnetted, 5 subnets, 4 masks
O        10.0.0.0/8    [110/10]  via 10.0.12.2
C        10.0.1.0/24   is directly connected, Gi0/0
S        10.0.2.0/24   [1/0]     via 10.0.12.2
O        10.0.2.0/24   [110/2]   ← KHÔNG hiển thị (đã thua static)
D        10.0.3.0/24   [90/28416] via 10.0.12.2
S        10.0.3.128/25 [1/0]     via 10.0.12.3
```

| Gói tới | Route khớp | Route thắng | Vì sao |
|---|---|---|---|
| `10.0.1.50` | `/8`, `/24` (C), `/0` | **`C 10.0.1.0/24`** | Prefix dài nhất (24) |
| `10.0.2.50` | `/8`, `/24` (S và O), `/0` | **`S 10.0.2.0/24`** | Prefix 24 thắng 8 → rồi AD 1 < 110 |
| `10.0.3.50` | `/8`, `/24` (D), `/0` | **`D 10.0.3.0/24`** | Prefix 24 |
| `10.0.3.200` | `/8`, `/24` (D), **`/25` (S)**, `/0` | **`S 10.0.3.128/25`** | Prefix **25** dài nhất |
| `8.8.8.8` | Chỉ `/0` | **`S* 0.0.0.0/0`** | Chỉ có nó khớp |

> 🔑 Dòng `10.0.3.200` là ví dụ đắt giá: route `/25` thắng route `/24` **dù cả hai đều hợp lệ**,
> và AD không được xét tới.

### ECMP — khi hoà hoàn toàn

Nếu **cùng prefix, cùng AD, cùng metric** → router dùng **cả hai**, chia tải:

```text
O   10.0.5.0/24 [110/20] via 10.0.12.2, Gi0/0
                [110/20] via 10.0.13.2, Gi0/1
```

Đây là **Equal-Cost Multi-Path**. OSPF mặc định dùng tới 4 đường (chỉnh được).

---

## 6. Packet Flow — không áp dụng

Lesson này về **quyết định**, không về đường đi. Nhưng đáng nhớ: toàn bộ quá trình
chọn route diễn ra **trong RIB**, kết quả nạp xuống **FIB**, và gói thật đi theo FIB.

---

## 7. Real-world Example

🏭 **Floating static** — ứng dụng trực tiếp của AD *(đã gặp ở Lesson 19)*:

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1          ! AD 1   → chính
ip route 0.0.0.0 0.0.0.0 198.51.100.1 200     ! AD 200 → backup
```

Cùng prefix `/0` → so AD → AD 1 thắng. Khi route AD 1 biến mất, AD 200 vào thay.

🏭 **Static route "đè" OSPF — kỹ thuật hữu dụng nhưng nguy hiểm**

```cisco
! OSPF đang quảng bá 10.0.5.0/24 qua đường A
! Bạn muốn tạm ép nó đi đường B:
ip route 10.0.5.0 255.255.255.0 10.0.99.1
```

Static (AD 1) thắng OSPF (AD 110) → traffic đi đường B.

> ⚠️ **Nguy hiểm:** static **không tự rút lui** khi đường B chết (trừ khi interface local down).
> OSPF có thể đã hội tụ sang đường khác, nhưng static vẫn ép traffic vào ngõ cụt.
> Dùng kỹ thuật này thì phải nhớ gỡ, hoặc kèm IP SLA + track.

🏭 **Lỗi thật: default route /0 không bao giờ được dùng**

Kỹ sư gõ default route nhưng traffic vẫn không ra Internet. Lý do: có một route
`10.0.0.0/8` hoặc thậm chí `0.0.0.0/1` + `128.0.0.0/1` đang khớp cụ thể hơn
và trỏ sai chỗ.

> 🔧 Phản xạ: **đừng đọc cả bảng** — dùng `show ip route <đích cụ thể>`
> để xem router *thật sự* chọn gì.

---

## 8. Cisco CLI

```cisco
! ───── Xem router chọn route nào cho một đích ─────
R1# show ip route 10.0.2.50               ! ⭐ lệnh quan trọng nhất của lesson này

! ───── Xem AD của các protocol đang chạy ─────
R1# show ip protocols

! ───── Đổi AD của static route ─────
R1(config)# ip route 10.0.5.0 255.255.255.0 10.0.12.2 200

! ───── Đổi AD của cả một protocol ─────
R1(config)# router ospf 1
R1(config-router)# distance 150                    ! đổi AD của OSPF thành 150

! Đổi AD cho route từ một nguồn cụ thể
R1(config-router)# distance 150 10.0.12.2 0.0.0.0

! ───── Số đường ECMP tối đa ─────
R1(config-router)# maximum-paths 4

! ───── Kiểm tra ─────
R1# show ip route 10.0.2.0 255.255.255.0
R1# show ip cef 10.0.2.50
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `show ip route <ip>` | Router thật sự chọn gì | ⭐ Dùng cái này, đừng đọc cả bảng |
| `distance <N>` trong router mode | Đổi AD toàn bộ protocol | ⚠️ Rất dễ gây loop — hiếm khi nên dùng |
| `maximum-paths` | Số đường ECMP | Mặc định OSPF 4, EIGRP 4 |

> ⚠️ **Đổi AD là việc nguy hiểm.** Nếu các router trong cùng mạng có AD khác nhau cho
> cùng một protocol, chúng sẽ chọn đường khác nhau → **routing loop**.
> Trong CCNA, biết nó tồn tại là đủ.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route 10.0.3.200
Routing entry for 10.0.3.128/25
  Known via "static", distance 1, metric 0
  Routing Descriptor Blocks:
  * 10.0.12.3
      Route metric is 0, traffic share count is 1
```

> 🔑 Lệnh này trả về **đúng một route** — chính là route router sẽ dùng.
> Nếu kết quả khác với dự đoán của bạn, đó là lúc bạn học được điều gì đó.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip protocols
Routing Protocol is "ospf 1"
  Router ID 1.1.1.1
  Number of areas in this router is 1
  Routing for Networks:
    10.0.1.0 0.0.0.255 area 0
  Distance: (default is 110)
```

**Kiểm tra ECMP:**

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route 10.0.5.0
Routing entry for 10.0.5.0/24
  Known via "ospf 1", distance 110, metric 20
  Routing Descriptor Blocks:
  * 10.0.12.2, from 2.2.2.2, via GigabitEthernet0/0
      Route metric is 20, traffic share count is 1
    10.0.13.2, from 3.3.3.3, via GigabitEthernet0/1
      Route metric is 20, traffic share count is 1
```

Hai `Routing Descriptor Blocks` cùng metric → **ECMP đang hoạt động**.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Traffic đi sai đường | Có route cụ thể hơn khớp trước | `show ip route <đích>` | Xem prefix nào thắng |
| Default route "không có tác dụng" | Route khác khớp cụ thể hơn | `show ip route 8.8.8.8` | Đúng thiết kế — sửa route kia |
| Route OSPF biến mất khỏi bảng | Có static cùng prefix, AD thấp hơn | `show ip route <net>` | Xoá static hoặc đặt AD cao hơn |
| Floating static không kích hoạt | AD không cao hơn route chính | `show run \| include ip route` | Tăng AD |
| Traffic chia hai đường ngoài ý muốn | ECMP do hoà hoàn toàn | `show ip route <net>` | Đặt AD/metric khác nhau |
| Thêm static xong mạng loạn | Static đè route động đang đúng | `show ip route <net>` | Gỡ static, hoặc đặt AD = 200+ |

---

## 11. LAB

🧪 **LAB 22 — Thứ tự chọn route** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- Tạo tình huống router học **cùng một mạng** từ cả static và OSPF → quan sát ai thắng
- Thêm một route `/25` nằm trong một route `/24` → chứng minh longest prefix match
- Tạo ECMP bằng 2 đường OSPF cùng cost → quan sát 2 Routing Descriptor Blocks
- **BREAK bắt buộc:** (1) thêm static đè OSPF rồi shutdown đường static →
  quan sát traffic **không** tự quay về OSPF nếu interface vẫn up;
  (2) đặt `distance 150` cho OSPF trên **một** router → quan sát bất đối xứng;
  (3) thêm `0.0.0.0/1` + `128.0.0.0/1` → chứng minh chúng đè default route

## 12. Challenge

> Cho bảng định tuyến này. Trả lời **không nhìn đáp án**.

```text
S*    0.0.0.0/0       [1/0]      via 203.0.113.1
O     10.0.0.0/8      [110/10]   via 10.1.1.2
D     10.5.0.0/16     [90/28416] via 10.1.1.3
S     10.5.5.0/24     [1/0]      via 10.1.1.4
C     10.5.5.64/26    is directly connected, Gi0/1
R     192.168.1.0/24  [120/3]    via 10.1.1.5
```

Gói tới các đích sau sẽ đi đường nào, và **vì sao**?

1. `10.5.5.100`
2. `10.5.5.200`
3. `10.5.9.1`
4. `10.9.9.9`
5. `192.168.1.10`
6. `172.16.0.1`

<details>
<summary>Đáp án</summary>

| # | Đích | Route thắng | Vì sao |
|:---:|---|---|---|
| 1 | `10.5.5.100` | **`C 10.5.5.64/26`** | `/26` bao `.64`–`.127` → chứa `.100`. Prefix **26** dài nhất |
| 2 | `10.5.5.200` | **`S 10.5.5.0/24`** | `.200` **nằm ngoài** `/26` (chỉ tới `.127`) → route dài nhất còn khớp là `/24` |
| 3 | `10.5.9.1` | **`D 10.5.0.0/16`** | Không khớp `/24` hay `/26`. Khớp `/16` (và `/8`) → `/16` dài hơn |
| 4 | `10.9.9.9` | **`O 10.0.0.0/8`** | Chỉ khớp `/8` và `/0` → `/8` dài hơn |
| 5 | `192.168.1.10` | **`R 192.168.1.0/24`** | Khớp `/24` và `/0` → `/24` dài hơn. AD 120 **không bị xét** vì không có route nào khác cùng prefix |
| 6 | `172.16.0.1` | **`S* 0.0.0.0/0`** | Không khớp gì khác → default route |

**Ba bài học từ bảng này:**

1. **Câu 1 và 2** — cùng nằm trong `10.5.5.0/24` nhưng đi **hai đường khác nhau**,
   chỉ vì `.100` lọt vào `/26` còn `.200` thì không. Longest prefix match hoạt động
   ở mức **từng địa chỉ**, không phải từng mạng.

2. **Câu 5** — route RIP có AD 120 (cao nhất trong bảng) vẫn được dùng, vì
   **không có route nào khác cùng prefix để so**. AD chỉ dùng khi có cạnh tranh.

3. Không có câu nào xét tới **metric**, vì không có hai route nào cùng prefix **và** cùng AD.
   Metric là tiêu chí hiếm khi phải dùng tới trong bài tập — nhưng rất quan trọng
   khi chạy OSPF thật.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Thứ tự 3 tiêu chí · AD của Connected/Static/EIGRP/OSPF/RIP | ⬜ |
| **L2** Explain | Giải thích vì sao longest prefix match xét trước AD | ⬜ |
| **L3** Configure | Tạo tình huống static đè OSPF, rồi đảo ngược bằng AD | ⬜ |
| **L4** Troubleshoot | Default route "không hoạt động" → tìm route đè nó | ⬜ |
| **L5** Design | Thiết kế backup path cho 3 đường WAN bằng AD | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **Thứ tự: Longest Prefix Match → Administrative Distance → Metric**
- **Longest prefix match xét TRƯỚC AD** — thông tin cụ thể hơn luôn thắng
- **AD** so sánh **giữa các nguồn**; **Metric** so sánh **trong cùng protocol**
- AD cần nhớ: **Connected 0 · Static 1 · eBGP 20 · EIGRP 90 · OSPF 110 · RIP 120 · iBGP 200**
- AD = **255** → route không bao giờ được dùng
- Không bao giờ so metric giữa hai protocol khác nhau
- Cùng prefix + cùng AD + cùng metric → **ECMP**, chia tải

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip route <ip>` | ⭐ Router **thật sự** chọn gì |
| `show ip protocols` | AD hiện tại của protocol |
| `ip route ... <AD>` | Floating static |
| `maximum-paths N` | Số đường ECMP |

**Common mistakes**

| Sai | Đúng |
|---|---|
| "AD xét trước" | **Longest prefix match** xét trước |
| So metric OSPF với metric RIP | Không so được — đó là lý do AD tồn tại |
| Đọc cả bảng để đoán route nào thắng | Dùng `show ip route <đích>` |
| Nghĩ default route luôn dùng được | Nó có prefix ngắn nhất, luôn thua |
| Thêm static mà không nghĩ tới AD | Vô tình đè route động đang đúng |

## 15. Homework + cập nhật PROGRESS

1. Làm Challenge mục 12 **không nhìn đáp án**, chấm lại.
2. Trên lab: tạo cùng lúc static và OSPF tới một mạng, chạy `show ip route <net>` —
   xác nhận static thắng. Rồi đặt static AD=200, chạy lại.
3. Tự tạo một bảng định tuyến 6 dòng và 5 câu hỏi "gói này đi đâu", đưa cho người khác làm.

```markdown
- [YYYY-MM-DD] Lesson 20 — AD, Metric, Longest Prefix: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Thứ tự 3 tiêu chí, bảng AD, đọc bảng định tuyến và dự đoán route thắng |
| 🔧 **Engineer** | `show ip route <đích>` thay vì đọc bảng; dùng AD làm backup path |
| 🏭 **Production** | Static đè route động rất nguy hiểm nếu quên gỡ; đổi `distance` gây routing loop |

### 🔗 Liên kết

- ⬅️ [Lesson 19 — Static & Default Route](./lesson-19-static-default-route.md)
- ➡️ [Lesson 21 — Dynamic Routing & RIP](./lesson-21-dynamic-routing-rip.md)
- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md#administrative-distance--bảng-phải-thuộc)
