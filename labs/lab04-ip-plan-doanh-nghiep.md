# LAB 04 — Thiết kế IP Plan cho doanh nghiệp

| | |
|---|---|
| **Phase** | 0 |
| **Lesson liên quan** | [Lesson 07 — VLSM & IP Plan](../00-foundation/lesson-07-vlsm-va-ip-plan.md) |
| **Công cụ** | Giấy bút trước, Packet Tracer sau |
| **Thời lượng** | ~3 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Chia VLSM cho 8 nhu cầu từ một `/23`, không chồng lấn, có dự phòng
- [ ] Viết được tài liệu `ip-plan.md` bàn giao được cho người khác
- [ ] Triển khai plan đó lên thiết bị và chứng minh nó chạy
- [ ] Nhận ra hậu quả thực tế khi chia sai

## 2. Prerequisite

- [Lesson 02](../00-foundation/lesson-02-ipv4-va-subnetting.md) — subnetting thành phản xạ
- [Lesson 07](../00-foundation/lesson-07-vlsm-va-ip-plan.md) — quy tắc cấp lớn trước
- [LAB 01](./lab01-vlsm-cong-ty-4-phong-ban.md) — đã làm xong

---

## 3. Đề bài

> Công ty **Hasa Tech** chuyển sang văn phòng mới. Bạn được cấp **`10.20.0.0/23`**
> và phải thiết kế toàn bộ IP plan.

### Nhu cầu hiện tại

| # | Bộ phận / Mục đích | Số thiết bị hiện tại | Ghi chú |
|:---:|---|:---:|---|
| 1 | Kinh doanh | 85 | Dự kiến tuyển thêm trong năm |
| 2 | Kỹ thuật | 45 | |
| 3 | Kế toán | 18 | Ổn định, ít tăng |
| 4 | Server nội bộ | 22 | Đang ảo hoá, sẽ tăng nhanh |
| 5 | Wi-Fi khách | 60 | Cao điểm có thể gấp đôi |
| 6 | Camera IP | 30 | Sẽ lắp thêm tầng 3 |
| 7 | Management (switch, AP, UPS) | 12 | |
| 8 | WAN link tới ISP 1 | 2 | Point-to-point |
| 9 | WAN link tới ISP 2 | 2 | Point-to-point |

### Ràng buộc

- Mỗi bộ phận là **một VLAN riêng** *(trừ 2 WAN link)*
- Dự phòng tăng trưởng: **30%** cho VLAN người dùng; **100%** cho Server và Camera;
  **0%** cho WAN link
- Gateway luôn là **first usable** của subnet
- Phải còn **ít nhất 15%** dải trống cho VLAN phát sinh sau này

---

## 4. Phần A — Thiết kế trên giấy *(làm trước, chưa mở Packet Tracer)*

### A1. Tính nhu cầu thực

| # | Bộ phận | Hiện tại | Dự phòng | Cần | Prefix | Host khả dụng |
|:---:|---|:---:|:---:|:---:|:---:|:---:|
| 1 | Kinh doanh | 85 | +30% | | | |
| 2 | Kỹ thuật | 45 | +30% | | | |
| 3 | Kế toán | 18 | +30% | | | |
| 4 | Server | 22 | +100% | | | |
| 5 | Wi-Fi khách | 60 | +30% | | | |
| 6 | Camera | 30 | +100% | | | |
| 7 | Management | 12 | +30% | | | |
| 8 | WAN 1 | 2 | 0% | 2 | `/30` | 2 |
| 9 | WAN 2 | 2 | 0% | 2 | `/30` | 2 |

### A2. Sắp xếp giảm dần rồi cấp

> ⚠️ Nhớ quy tắc: **cấp lớn trước**. Cấp sai thứ tự sẽ phân mảnh và không đủ dải.

| Thứ tự cấp | VLAN | Tên | Prefix | Network | First | Last | Broadcast |
|:---:|:---:|---|:---:|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | — | WAN 1 | `/30` | | | | |
| 9 | — | WAN 2 | `/30` | | | | |

### A3. Kiểm tra

- [ ] Tổng số địa chỉ đã dùng: ______ / 512
- [ ] Còn trống: ______ địa chỉ = ______ % *(phải ≥ 15%)*
- [ ] Không có subnet nào chồng lấn *(vẽ trục số, tô từng khoảng để kiểm tra)*
- [ ] Mỗi subnet đủ host + dự phòng

### A4. Quy ước gán địa chỉ

Điền quy ước áp dụng cho **mọi** VLAN:

| Vị trí trong subnet | Dùng cho |
|---|---|
| `.1` | |
| `.2` – `.9` | |
| `.10` – `.49` | |
| `.50` trở đi | |

---

## 5. Phần B — Triển khai một phần lên Packet Tracer

Không cần dựng cả 9 subnet. Dựng **4 cái** để chứng minh plan chạy được:

```text
         VLAN 10 (Kinh doanh)      VLAN 50 (Server)
              PC1                      SRV1
               │                         │
             SW1 ═══════ trunk ═══════ SW2
               │                         │
               └────── L3-SW / R1 ───────┘
                          │
                      WAN 1 /30
                          │
                        R-ISP
```

| Bước | Việc |
|:---:|---|
| 1 | Tạo VLAN 10, 50, 99 trên switch |
| 2 | Gán SVI (gateway) cho từng VLAN theo đúng plan |
| 3 | Cấu hình WAN link `/30` giữa R1 và R-ISP |
| 4 | Gán IP cho PC1, SRV1 theo quy ước (PC dùng DHCP hoặc tĩnh đều được) |
| 5 | Ping được giữa 2 VLAN qua inter-VLAN routing |
| 6 | Ping được từ PC1 ra R-ISP |

---

## 6. Phần C — Viết tài liệu `ip-plan.md`

Tạo file `ip-plan.md` trong thư mục lab của bạn, theo đúng khuôn:

```markdown
# IP PLAN — Hasa Tech
Dải được cấp : 10.20.0.0/23
Ngày lập     : YYYY-MM-DD
Người lập    : <tên bạn>

## 1. Bảng subnet
| VLAN | Tên | Prefix | Network | Gateway | Dải DHCP | Broadcast | Host max | Dùng thực tế |
|------|-----|--------|---------|---------|----------|-----------|----------|--------------|

## 2. Quy ước gán địa chỉ
.1 = gateway · .2-.9 = hạ tầng · .10-.49 = tĩnh · .50+ = DHCP

## 3. Dải còn trống
<liệt kê>

## 4. Lý do chọn prefix cho từng VLAN
<giải thích ngắn, đặc biệt các chỗ có dự phòng khác nhau>

## 5. Lịch sử thay đổi
| Ngày | Thay đổi | Người |
```

> 🔑 Phần 4 là phần quan trọng nhất với người đọc sau bạn. Một bảng số không giải thích
> được *vì sao* sẽ bị người kế nhiệm sửa bừa.

---

## 7. Verification

- [ ] `show ip interface brief` — mọi SVI và interface `up/up`, IP đúng plan
- [ ] `show ip route connected` — thấy `variably subnetted ... N masks` với `N > 1`
- [ ] PC1 ping được gateway của nó
- [ ] PC1 ping được SRV1 *(khác VLAN)*
- [ ] PC1 ping được R-ISP *(qua WAN link)*
- [ ] File `ip-plan.md` đầy đủ 5 mục

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip route connected
      10.0.0.0/8 is variably subnetted, 8 subnets, 4 masks
C        10.20.0.0/25   is directly connected, Vlan10
L        10.20.0.1/32   is directly connected, Vlan10
C        10.20.1.0/26   is directly connected, Vlan50
```

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

| # | Cố tình làm sai | Dự đoán | Quan sát | Giải thích |
|:---:|---|---|---|---|
| 1 | Gán SVI VLAN 10 mask `/24` thay vì `/25` theo plan | | | |
| 2 | Đặt gateway là `.254` (last usable) cho VLAN 10, nhưng PC vẫn trỏ `.1` | | | |
| 3 | Cấu hình VLAN 50 trùng dải với VLAN 10 | | | |
| 4 | Gán WAN link `/24` thay vì `/30`, rồi thêm một VLAN mới vào dải bị chiếm | | | |

**Với mỗi lỗi:**

- IOS có báo lỗi không? *(nhiều lỗi IP plan **không** có thông báo nào)*
- Triệu chứng xuất hiện ngay hay chỉ lộ ra sau này?
- Nếu đây là mạng thật đang chạy, sửa tốn bao nhiêu công?

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Sáu tháng sau, công ty mở thêm **VLAN IoT 40 thiết bị**. Dải trống của bạn còn đủ không?
   Nếu đủ thì đặt ở đâu? Nếu không thì phương án là gì?
2. Công ty mở **chi nhánh thứ hai**. Thiết kế lại từ `10.20.0.0/16` sao cho mỗi chi nhánh
   **gom được thành 1 route**.
3. Nếu chỉ được cấp `10.20.0.0/24` *(một nửa)*, bạn phải hy sinh gì? Nêu 2 phương án
   và đánh đổi.

---

## 10. Solution

<details>
<summary>⚠️ Chỉ mở sau khi đã làm xong Phần A</summary>

### A1 — Nhu cầu thực

| # | Bộ phận | Hiện tại | Dự phòng | Cần | Prefix | Host khả dụng |
|:---:|---|:---:|:---:|:---:|:---:|:---:|
| 1 | Kinh doanh | 85 | +30% | 111 | **`/25`** | 126 |
| 5 | Wi-Fi khách | 60 | +30% | 78 | **`/25`** | 126 |
| 2 | Kỹ thuật | 45 | +30% | 59 | **`/26`** | 62 |
| 6 | Camera | 30 | +100% | 60 | **`/26`** | 62 |
| 4 | Server | 22 | +100% | 44 | **`/26`** | 62 |
| 3 | Kế toán | 18 | +30% | 24 | **`/27`** | 30 |
| 7 | Management | 12 | +30% | 16 | **`/27`** | 30 |
| 8 | WAN 1 | 2 | 0% | 2 | `/30` | 2 |
| 9 | WAN 2 | 2 | 0% | 2 | `/30` | 2 |

### A2 — Cấp theo thứ tự lớn → nhỏ

| # | VLAN | Tên | Prefix | Network | First | Last | Broadcast |
|:---:|:---:|---|:---:|---|---|---|---|
| 1 | 10 | KINHDOANH | `/25` | `10.20.0.0` | `.1` | `.126` | `.127` |
| 2 | 60 | GUEST-WIFI | `/25` | `10.20.0.128` | `.129` | `.254` | `.255` |
| 3 | 20 | KYTHUAT | `/26` | `10.20.1.0` | `.1` | `.62` | `.63` |
| 4 | 70 | CAMERA | `/26` | `10.20.1.64` | `.65` | `.126` | `.127` |
| 5 | 50 | SERVER | `/26` | `10.20.1.128` | `.129` | `.190` | `.191` |
| 6 | 30 | KETOAN | `/27` | `10.20.1.192` | `.193` | `.222` | `.223` |
| 7 | 99 | MGMT | `/27` | `10.20.1.224` | `.225` | `.254` | `.255` |

❗ **Vấn đề:** hết sạch `/23` mà **chưa cấp được 2 WAN link**, và không còn dải trống.

### Cách xử lý — và bài học thật của lab này

Đây **không phải lỗi tính toán của bạn**. Đề bài cố tình chật để bạn gặp đúng tình huống
thực tế: **dải được cấp không đủ cho thiết kế lý tưởng.**

Ba phương án, theo thứ tự nên ưu tiên:

| # | Phương án | Cách làm | Đánh đổi |
|:---:|---|---|---|
| **1** | **Xin thêm dải** ⭐ | Đề nghị cấp `/22` thay vì `/23` | Tốt nhất. Dải private không mất tiền — không có lý do gì phải chật. |
| 2 | **Dùng dải riêng cho WAN** | WAN link lấy từ `10.255.0.0/24`, tách khỏi `/23` của LAN | Rất phổ biến trong thực tế: hạ tầng và người dùng dùng block riêng. Giữ nguyên thiết kế LAN. |
| 3 | **Giảm dự phòng** | Camera và Server dùng `/27` thay `/26`, Guest dùng `/26` | Tiết kiệm được 128 địa chỉ nhưng **nợ kỹ thuật** — sẽ phải đổi mask trong 1–2 năm |

**Phương án 2 làm đầy đủ:**

```text
LAN  : 10.20.0.0/23       →  7 VLAN như bảng trên
WAN  : 10.255.0.0/30      →  WAN 1  (R1 .1  ↔  ISP1 .2)
       10.255.0.4/30      →  WAN 2  (R1 .5  ↔  ISP2 .6)
Loopback: 10.255.255.1/32 →  R1
```

> 🔑 **Bài học lớn nhất của lab:** việc đầu tiên khi làm IP plan không phải là chia —
> mà là **kiểm tra dải được cấp có đủ không**. Phát hiện thiếu ở giai đoạn thiết kế
> tốn 10 phút; phát hiện sau khi triển khai tốn một đêm làm ngoài giờ.

### A4 — Quy ước gán địa chỉ

| Vị trí | Dùng cho |
|---|---|
| `.1` | Gateway (SVI) |
| `.2` – `.9` | Hạ tầng: HSRP standby, switch management |
| `.10` – `.49` | IP tĩnh: server, máy in, camera, AP |
| `.50` trở đi | DHCP pool |

### Giải thích các lỗi BREAK

| # | IOS báo lỗi? | Triệu chứng | Khi nào lộ ra |
|:---:|---|---|---|
| 1 | ❌ Không | VLAN 10 "mượn" dải của VLAN 60. PC VLAN 10 nhận IP `.130` sẽ xung đột khi VLAN 60 lắp đặt | **Vài tháng sau**, khi VLAN 60 đi vào hoạt động |
| 2 | ❌ Không | PC trỏ `.1` nhưng gateway thật ở `.254` → **mất mạng ngay** | Ngay lập tức |
| 3 | ✅ Có — `% ... overlaps with VlanX` | Lệnh bị từ chối | Ngay khi gõ |
| 4 | ❌ Không | WAN `/24` chiếm `10.20.1.0` – `.255`; VLAN mới đặt vào đó sẽ chồng | Khi thêm VLAN mới |

**Điểm chung đáng sợ:** 3/4 lỗi **IOS không báo gì**. IOS chỉ phát hiện chồng lấn
giữa các interface **trên cùng một thiết bị**. Tài liệu IP plan là lớp phòng vệ duy nhất.

### Challenge

**1.** Với phương án 2, dải `/23` đã dùng hết cho 7 VLAN. VLAN IoT 40 thiết bị
(+100% dự phòng = 80 → `/25`) **không còn chỗ**. Phương án: xin thêm một `/24` liền kề
(`10.20.2.0/24`), hoặc chuyển Camera/IoT sang block hạ tầng riêng.
👉 Củng cố bài học: `/23` là **quá chật** ngay từ đầu.

**2.** Cấp mỗi chi nhánh một `/20` từ `10.20.0.0/16`:

```text
10.20.0.0/20    → Chi nhánh 1   (gom thành 1 route)
10.20.16.0/20   → Chi nhánh 2
10.20.32.0/20   → Chi nhánh 3 (dự phòng)
10.20.240.0/20  → Hạ tầng dùng chung: WAN link, loopback
```

Router lõi chỉ cần **1 route cho mỗi chi nhánh** thay vì 7–9 route.

**3.** Với `/24` (256 địa chỉ) — tổng nhu cầu kể cả dự phòng đã vượt 400.
**Bắt buộc phải hy sinh:**

| Phương án | Cách làm | Đánh đổi |
|---|---|---|
| Bỏ dự phòng, gộp VLAN | Gộp Camera + Management, Kế toán + Kỹ thuật | Mất tách biệt bảo mật — thứ chính VLAN sinh ra để làm |
| Guest Wi-Fi dùng dải riêng | Guest lấy `192.168.100.0/24` tách hẳn | ✅ Hợp lý: guest vốn nên tách, và dải private không thiếu |

👉 Phương án 2 tốt hơn. Và kết luận vẫn là: **đừng chấp nhận dải chật khi không có lý do.**

</details>

---

## 📝 Ghi chú & bài học rút ra

- Tôi phát hiện dải không đủ ở bước nào? ___
- Nếu làm lại, việc đầu tiên tôi sẽ làm khác là: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
