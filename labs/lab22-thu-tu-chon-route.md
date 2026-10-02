# LAB 22 — Thứ tự chọn route: Longest Prefix · AD · Metric

| | |
|---|---|
| **Phase** | 2 |
| **Lesson liên quan** | [Lesson 20 — AD, Metric, Longest Prefix Match](../02-routing/lesson-20-ad-metric-longest-prefix.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] **Chứng minh bằng thực nghiệm** rằng longest prefix match xét **trước** AD
- [ ] Quan sát static (AD 1) **đè** OSPF (AD 110) cho cùng một prefix
- [ ] Tạo và quan sát **ECMP** — hai đường cùng cost
- [ ] Chứng minh nguy hiểm của việc dùng static đè route động
- [ ] Dùng `show ip route <ip>` thay vì đọc cả bảng

## 2. Prerequisite

- [LAB 21](./lab21-static-default-floating.md) — static route
- [Lesson 20](../02-routing/lesson-20-ad-metric-longest-prefix.md) — thứ tự 3 tiêu chí, bảng AD

---

## 3. Topology

```text
                    ┌──────── R2 ────────┐
                    │                     │
      PC-A ──── R1 ─┤                     ├─ R4 ──── PC-D
   10.1.1.10/24     │                     │        10.4.4.0/24
                    └──────── R3 ────────┘
                                                    + 10.4.4.128/25
                                                      (subnet con)
```

| Link | Subnet |
|---|---|
| R1 ↔ R2 | `10.0.12.0/30` |
| R1 ↔ R3 | `10.0.13.0/30` |
| R2 ↔ R4 | `10.0.24.0/30` |
| R3 ↔ R4 | `10.0.34.0/30` |

> 💡 Topology có **hai đường song song** từ R1 tới R4 — điều kiện để tạo ECMP.

## 4. IP Addressing Table

| Device | Interface | IP |
|---|---|---|
| R1 | Gi0/0 *(LAN-A)* | `10.1.1.1/24` |
| R1 | Gi0/1 *(→R2)* | `10.0.12.1/30` |
| R1 | Gi0/2 *(→R3)* | `10.0.13.1/30` |
| R2 | Gi0/1 *(→R1)* | `10.0.12.2/30` |
| R2 | Gi0/2 *(→R4)* | `10.0.24.1/30` |
| R3 | Gi0/1 *(→R1)* | `10.0.13.2/30` |
| R3 | Gi0/2 *(→R4)* | `10.0.34.1/30` |
| R4 | Gi0/1 *(→R2)* | `10.0.24.2/30` |
| R4 | Gi0/2 *(→R3)* | `10.0.34.2/30` |
| R4 | Gi0/0 *(LAN-D)* | `10.4.4.1/24` |
| R4 | Lo1 | `10.4.4.129/25` ← **subnet con nằm trong `/24`** |
| PC-A | Fa0 | `10.1.1.10/24`, GW `10.1.1.1` |
| PC-D | Fa0 | `10.4.4.10/24`, GW `10.4.4.1` |

> 🔑 `Lo1 = 10.4.4.129/25` tạo ra prefix `10.4.4.128/25` — **nằm trong** `10.4.4.0/24`.
> Đây là chìa khoá để thử longest prefix match.

---

## 5. Yêu cầu LAB

- [ ] Chạy OSPF trên mọi router → R1 học được `10.4.4.0/24` và `10.4.4.128/25` qua OSPF
- [ ] Quan sát **ECMP** — hai đường cùng cost tới R4
- [ ] Thêm static route đè OSPF → chứng minh AD quyết định
- [ ] Thêm static `/25` → chứng minh **longest prefix thắng cả AD thấp hơn**
- [ ] Hoàn thành mục **8. BREAK**

---

## 6. Step-by-step

### Bước 1 — OSPF cơ bản

```cisco
! Làm trên cả 4 router (đổi router-id)
hostname R1
no ip domain-lookup

interface Loopback0
 ip address 1.1.1.1 255.255.255.255

router ospf 1
 router-id 1.1.1.1
 auto-cost reference-bandwidth 100000
 passive-interface default
 no passive-interface GigabitEthernet0/1
 no passive-interface GigabitEthernet0/2
 network 10.0.12.1 0.0.0.0 area 0
 network 10.0.13.1 0.0.0.0 area 0
 network 10.1.1.1 0.0.0.0 area 0
```

R4 nhớ khai cả `Lo1`:

```cisco
R4(config-router)# network 10.4.4.1 0.0.0.0 area 0
R4(config-router)# network 10.4.4.129 0.0.0.0 area 0
```

### Bước 2 — Quan sát ECMP

```cisco
R1# show ip route 10.4.4.0
```

| Câu hỏi | Trả lời |
|---|---|
| Có mấy `Routing Descriptor Blocks`? | |
| Cost của mỗi đường? | |
| Vì sao chúng bằng nhau? | |
| `tracert` từ PC-A tới PC-D đi qua R2 hay R3? | |

### Bước 3 — Static đè OSPF *(cùng prefix)*

> 🔴 **Dự đoán trước:** sau lệnh dưới, `show ip route 10.4.4.10` trả về route nào?

```cisco
R1(config)# ip route 10.4.4.0 255.255.255.0 10.0.12.2 name EP-DI-R2
```

| | Dự đoán | Thực tế |
|---|---|---|
| Route thắng | | |
| AD hiển thị | | |
| Route OSPF còn trong bảng không? | | |
| `tracert` PC-A → PC-D đi hướng nào? | | |

### Bước 4 — Longest prefix thắng AD ⭐

> 🔴 Bài quan trọng nhất của lab. **Dự đoán trước khi gõ.**

Hiện tại R1 có:
- `S 10.4.4.0/24 [1/0] via 10.0.12.2` *(static, AD 1 — bạn vừa thêm)*
- `O 10.4.4.128/25 [110/x] via ...` *(OSPF, AD 110 — học từ R4)*

| Gói tới | Dự đoán route thắng | Vì sao | Thực tế |
|---|---|---|---|
| `10.4.4.10` | | | |
| `10.4.4.200` | | | |

```cisco
R1# show ip route 10.4.4.10
R1# show ip route 10.4.4.200
```

> 🔑 Nếu kết quả của `10.4.4.200` làm bạn bất ngờ — **đó chính là bài học của lab này**.

### Bước 5 — Đổi AD của static

```cisco
R1(config)# no ip route 10.4.4.0 255.255.255.0 10.0.12.2
R1(config)# ip route 10.4.4.0 255.255.255.0 10.0.12.2 200
```

| | Trả lời |
|---|---|
| `show ip route 10.4.4.10` giờ trả về route nào? | |
| Vì sao? | |
| Static route đi đâu? Còn trong `show run` không? | |

---

## 7. Verification

```text
# output điển hình — ECMP, trước khi thêm static
R1# show ip route 10.4.4.0
Routing entry for 10.4.4.0/24
  Known via "ospf 1", distance 110, metric 300, type intra area
  Routing Descriptor Blocks:
  * 10.0.12.2, from 4.4.4.4, 00:05:12 ago, via GigabitEthernet0/1
      Route metric is 300, traffic share count is 1
    10.0.13.2, from 4.4.4.4, 00:05:12 ago, via GigabitEthernet0/2
      Route metric is 300, traffic share count is 1
```

```text
# output điển hình — sau khi thêm static AD 1
R1# show ip route 10.4.4.10
Routing entry for 10.4.4.0/24
  Known via "static", distance 1, metric 0
  Routing Descriptor Blocks:
  * 10.0.12.2
```

```text
# output điển hình — longest prefix match
R1# show ip route 10.4.4.200
Routing entry for 10.4.4.128/25
  Known via "ospf 1", distance 110, metric 301, type intra area
  Routing Descriptor Blocks:
  * 10.0.12.2, from 4.4.4.4, via GigabitEthernet0/1
```

**Bảng kiểm chứng:**

- [ ] Bước 2: thấy **2 Routing Descriptor Blocks** cùng metric
- [ ] Bước 3: route OSPF `/24` **biến mất** khỏi bảng, static thay thế
- [ ] Bước 4: `10.4.4.10` → static `/24`; `10.4.4.200` → **OSPF `/25`**
- [ ] Bước 5: static AD 200 biến mất khỏi bảng, OSPF quay lại

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Static đè OSPF rồi đường static chết ⭐

> Đây là lỗi nguy hiểm nhất khi dùng static đè route động.

```cisco
! Đảm bảo static AD 1 đang hoạt động
R1(config)# ip route 10.4.4.0 255.255.255.0 10.0.12.2

! Giờ "làm chết" đường qua R2 — NHƯNG GIỮ interface R1 up
R2(config)# interface GigabitEthernet0/2
R2(config-if)# shutdown
```

| | |
|---|---|
| Interface Gi0/1 trên R1 còn up không? | |
| `show ip route 10.4.4.10` vẫn trỏ `10.0.12.2`? | |
| OSPF có hội tụ sang đường R3 không? *(xem `show ip route \| include 10.4.4`)* | |
| PC-A ping PC-D được không? | |
| **Vì sao traffic không tự chuyển sang đường R3?** | |

### Lỗi 2 — ECMP ngoài ý muốn với NAT

```cisco
R1(config)# ip route 0.0.0.0 0.0.0.0 10.0.12.2
R1(config)# ip route 0.0.0.0 0.0.0.0 10.0.13.2
```

| | |
|---|---|
| `show ip route \| include 0.0.0.0` hiện mấy dòng? | |
| `tracert` từ PC-A tới PC-D vài lần — đường có đổi không? | |
| Nếu R1 đang làm NAT, điều này gây vấn đề gì? | |

### Lỗi 3 — Đổi AD của OSPF chỉ trên một router

```cisco
R1(config)# router ospf 1
R1(config-router)# distance 150
```

| | |
|---|---|
| Route OSPF trên R1 hiển thị AD mấy? | |
| Trên R2, R3 thì sao? | |
| Vì sao đây là việc nguy hiểm? | |

### Lỗi 4 *(tự chọn)* — Thêm route `/32` cho một host

```cisco
R1(config)# ip route 10.4.4.10 255.255.255.255 10.0.13.2
```

| | |
|---|---|
| Gói tới `10.4.4.10` đi hướng nào? | |
| Gói tới `10.4.4.11` đi hướng nào? | |
| Hai máy cùng subnet nhưng đi **hai đường khác nhau** — vì sao? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

> Cho bảng định tuyến này trên R1. Trả lời **không nhìn đáp án**.

```text
S*    0.0.0.0/0        [1/0]      via 10.0.12.2
O     10.0.0.0/8       [110/50]   via 10.0.13.2
S     10.4.0.0/16      [1/0]      via 10.0.12.2
O     10.4.4.0/24      [110/300]  via 10.0.12.2
C     10.4.4.128/25    is directly connected, Loopback9
S     10.4.4.200/32    [200/0]    via 10.0.13.2
```

Gói tới các đích sau đi route nào, và **vì sao**?

1. `10.4.4.5`
2. `10.4.4.150`
3. `10.4.4.200`
4. `10.4.9.1`
5. `10.9.9.9`
6. `172.16.1.1`

<details>
<summary>Đáp án</summary>

| # | Đích | Route thắng | Giải thích |
|:---:|---|---|---|
| 1 | `10.4.4.5` | **`O 10.4.4.0/24`** | Khớp `/8`, `/16`, `/24`, `/0`. Không khớp `/25` *(`.5` < `.128`)*. **Prefix 24 dài nhất** |
| 2 | `10.4.4.150` | **`C 10.4.4.128/25`** | `.150` nằm trong `.128–.255` → khớp `/25`. **Prefix 25 dài nhất** |
| 3 | `10.4.4.200` | **`S 10.4.4.200/32`** | ⭐ Khớp cả `/25` lẫn `/32`. **Prefix 32 dài nhất → thắng, bất kể AD 200 là cao nhất bảng** |
| 4 | `10.4.9.1` | **`S 10.4.0.0/16`** | Không khớp `/24` *(`.9` ≠ `.4`)*. Khớp `/16` và `/8` → **`/16` dài hơn** |
| 5 | `10.9.9.9` | **`O 10.0.0.0/8`** | Chỉ khớp `/8` và `/0` → `/8` dài hơn |
| 6 | `172.16.1.1` | **`S* 0.0.0.0/0`** | Không khớp gì khác |

**Ba bài học từ bảng này:**

1. **Câu 3 là điểm mấu chốt:** route `/32` có **AD 200** *(cao nhất bảng, kém tin cậy nhất)*
   vẫn **thắng** route `/25` có AD 0 *(connected, tin cậy nhất)*.
   → **Longest prefix match luôn xét TRƯỚC AD.**

2. **Câu 1 và 2** cho thấy longest prefix match hoạt động ở mức **từng địa chỉ**,
   không phải từng mạng — hai IP cùng `10.4.4.0/24` đi hai đường khác nhau.

3. Không câu nào phải xét tới **metric** — vì không có hai route nào **cùng prefix**
   **và** cùng AD. Metric là tiêu chí hiếm khi dùng tới trong bài tập.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Bước 2 — ECMP

Hai đường R1→R2→R4 và R1→R3→R4 có **cùng số link, cùng loại link** → cost bằng nhau
→ OSPF cài **cả hai** vào bảng.

```text
2 Routing Descriptor Blocks, cùng metric
→ traffic chia tải (per-destination theo mặc định của CEF)
```

`tracert` nhiều lần tới **các đích khác nhau** sẽ thấy đường khác nhau.
Tới **cùng một đích** thì thường đi cùng đường *(CEF per-destination load sharing)*.

### Bước 3 — Static đè OSPF

| | Kết quả |
|---|---|
| Route thắng | **`S 10.4.4.0/24 [1/0] via 10.0.12.2`** |
| AD | **1** |
| Route OSPF `/24` | **Biến mất khỏi bảng** *(vẫn còn trong LSDB, chỉ không được cài)* |
| `tracert` | Luôn đi qua **R2**, không còn chia tải |

### Bước 4 — Longest prefix thắng AD ⭐

| Gói tới | Route thắng | Vì sao |
|---|---|---|
| `10.4.4.10` | **`S 10.4.4.0/24` (AD 1)** | `.10 < .128` → không khớp `/25`. Chỉ có `/24` khớp |
| `10.4.4.200` | **`O 10.4.4.128/25` (AD 110)** | ⭐ `.200` khớp **cả** `/24` và `/25`. **Prefix 25 dài hơn → thắng**, dù AD 110 > AD 1 |

👉 **Đây là bằng chứng thực nghiệm**: AD **không được xét** khi hai route có
prefix length khác nhau.

### Bước 5 — Static AD 200

```text
S 10.4.4.0/24 [200/0]  → AD 200 > AD 110 của OSPF
→ Static BỊ ĐẨY RA khỏi bảng
→ Route OSPF /24 QUAY LẠI (và ECMP cũng quay lại)
```

Static vẫn còn trong `show running-config` nhưng **không** trong `show ip route`.
Đây chính là cơ chế **floating static**.

### Giải thích các lỗi BREAK

| # | Quan sát | Giải thích |
|:---:|---|---|
| **1** | Gi0/1 trên R1 **vẫn up**; route vẫn `via 10.0.12.2`; OSPF **đã** hội tụ sang R3 nhưng không được dùng; PC-A **không** ping được PC-D | ⭐ **Static route không biết đường phía sau đã chết.** Nó chỉ mất khi next-hop `10.0.12.2` không reachable — mà R2 vẫn sống. OSPF đã tính lại đúng nhưng AD 110 > AD 1 nên thua |
| **2** | 2 dòng default route; `tracert` đổi đường tuỳ đích | **ECMP**. Với NAT: traffic của **cùng một kết nối** có thể đi ra hai IP public khác nhau → server phía xa thấy hai nguồn → **đứt session**; firewall stateful cũng không khớp được |
| **3** | R1 hiện AD **150**, R2/R3 vẫn **110** | **Bất đối xứng.** R1 có thể ưu tiên static/RIP hơn OSPF trong khi router khác thì không → **traffic đi một đường, về đường khác**, hoặc tệ hơn là **routing loop** |
| **4** | `10.4.4.10` đi **R3**; `10.4.4.11` đi **R2** | Route `/32` chỉ khớp **đúng một địa chỉ**. `.11` không khớp `/32` nên rơi xuống route `/24` |

**Bài học từ lỗi 1 — quan trọng nhất:**

```text
Dùng static đè route động = TẮT khả năng tự hội tụ của routing protocol.

Chỉ dùng khi:
  - Tạm thời, có kế hoạch gỡ
  - Hoặc kèm IP SLA + track (Lesson 39) để static tự rút lui
```

### Bảng tổng kết thực nghiệm

| Thí nghiệm | Chứng minh được điều gì |
|---|---|
| Bước 2 | Cùng prefix + cùng AD + cùng metric → **ECMP** |
| Bước 3 | Cùng prefix, **AD thấp hơn thắng** |
| **Bước 4** | ⭐ **Prefix dài hơn thắng, BẤT KỂ AD** |
| Bước 5 | AD cao hơn → route bị đẩy ra khỏi bảng *(floating static)* |
| BREAK 1 | Static đè route động **vô hiệu hoá khả năng tự hội tụ** |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Kết quả bước 4 có đúng dự đoán của tôi không? ___
- Lỗi BREAK 1 dạy tôi điều gì về việc dùng static đè OSPF? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
