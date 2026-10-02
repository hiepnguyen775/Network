# LAB 20 — Routing table cơ bản

| | |
|---|---|
| **Phase** | 2 |
| **Lesson liên quan** | [Lesson 18 — Router & Routing Table](../02-routing/lesson-18-router-va-routing-table.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~1.5 giờ |
| **Độ khó** | ⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Quan sát route `C` và `L` **xuất hiện và biến mất** khi bật/tắt interface
- [ ] Chứng minh `L` là route cho **chính IP của router**, `C` là cho cả subnet
- [ ] Đọc `show ip route <ip>` và hiểu router thật sự chọn gì
- [ ] Nhận ra ICMP *Destination Unreachable* khi không có route

## 2. Prerequisite

- [Lesson 18](../02-routing/lesson-18-router-va-routing-table.md) — 5 bước router xử lý gói, mã route
- [LAB 01](./lab01-vlsm-cong-ty-4-phong-ban.md) — gán IP cho interface

---

## 3. Topology

```text
   PC-A                                              PC-B
10.0.1.10/24                                     10.0.2.10/24
     │                                                │
   Gi0/0                                            Gi0/0
  10.0.1.1                                        10.0.2.1
     R1 ──────────Gi0/1────Gi0/1──────────────────── R2
          10.0.12.1/30    10.0.12.2/30
```

| Thiết bị | Model gợi ý |
|---|---|
| R1, R2 | ISR 2911 |
| PC-A, PC-B | PC-PT |

## 4. IP Addressing Table

| Device | Interface | IP | Mask | Gateway |
|---|---|---|---|---|
| R1 | Gi0/0 | `10.0.1.1` | `255.255.255.0` | — |
| R1 | Gi0/1 | `10.0.12.1` | `255.255.255.252` | — |
| R2 | Gi0/0 | `10.0.2.1` | `255.255.255.0` | — |
| R2 | Gi0/1 | `10.0.12.2` | `255.255.255.252` | — |
| PC-A | Fa0 | `10.0.1.10` | `255.255.255.0` | `10.0.1.1` |
| PC-B | Fa0 | `10.0.2.10` | `255.255.255.0` | `10.0.2.1` |

---

## 5. Yêu cầu LAB

- [ ] Gán IP đúng bảng, mọi interface `up/up`
- [ ] **Chưa cấu hình route nào** → PC-A **không** ping được PC-B *(đây là kết quả đúng)*
- [ ] Đếm được chính xác số route trên mỗi router
- [ ] Giải thích được từng dòng trong `show ip route`
- [ ] Hoàn thành mục **8. BREAK**

---

## 6. Step-by-step

### Bước 1 — Cấu hình cơ bản

```cisco
! ───── R1 ─────
hostname R1
no ip domain-lookup

interface GigabitEthernet0/0
 description LAN-A
 ip address 10.0.1.1 255.255.255.0
 no shutdown
exit

interface GigabitEthernet0/1
 description WAN-TO-R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
exit
end
```

R2 tương tự, đổi IP theo bảng.

PC: gán IP + gateway theo bảng.

### Bước 2 — ĐẾM route trước khi xem

> 🔴 Trả lời trước khi gõ `show ip route`.

| Câu hỏi | Dự đoán |
|---|---|
| R1 có bao nhiêu route? | |
| Liệt kê prefix của từng route | |
| Vì sao có cả `C` và `L` cho mỗi interface? | |

### Bước 3 — Kiểm chứng

```cisco
R1# show ip route
R1# show ip route connected
R1# show ip route 10.0.1.10
R1# show ip route 10.0.1.1
```

| Lệnh | Kết quả | Khớp dự đoán? |
|---|---|:---:|
| Tổng số route trên R1 | | |
| `show ip route 10.0.1.10` khớp route nào | | |
| `show ip route 10.0.1.1` khớp route nào | | |

### Bước 4 — Thử ping

| Từ | Tới | Kết quả mong đợi | Thực tế |
|---|---|---|---|
| PC-A | `10.0.1.1` *(gateway)* | ✅ Được | |
| PC-A | `10.0.12.1` *(interface kia của R1)* | ✅ Được | |
| PC-A | `10.0.12.2` *(R2)* | ❓ Thử xem | |
| PC-A | `10.0.2.10` *(PC-B)* | ❌ **Không** được | |

> 🔑 Dòng thứ 3 là câu hỏi hay: R1 **có** route tới `10.0.12.0/30`, nhưng PC-A ping
> `10.0.12.2` có được không? Thử rồi giải thích.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route
Codes: L - local, C - connected, S - static, O - OSPF

      10.0.0.0/8 is variably subnetted, 4 subnets, 3 masks
C        10.0.1.0/24 is directly connected, GigabitEthernet0/0
L        10.0.1.1/32 is directly connected, GigabitEthernet0/0
C        10.0.12.0/30 is directly connected, GigabitEthernet0/1
L        10.0.12.1/32 is directly connected, GigabitEthernet0/1
```

**Bằng chứng lab đúng:**

- [ ] R1 có **đúng 4 route** *(2 interface × 2 route)*
- [ ] Mọi route `L` đều là `/32`
- [ ] `show ip route 10.0.1.1` trả về route `L`
- [ ] `show ip route 10.0.1.10` trả về route `C`
- [ ] PC-A **không** ping được PC-B *(chưa có route)*

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Shutdown một interface

```cisco
R1(config)# interface GigabitEthernet0/1
R1(config-if)# shutdown
```

| | |
|---|---|
| Dự đoán: mất mấy route? | |
| Thực tế: `show ip route` còn mấy route? | |
| Những route nào biến mất? | |
| Bài học | |

Bật lại: `no shutdown`.

### Lỗi 2 — Ping một mạng không có route

```cisco
PC-A> ping 192.168.99.1
```

| | |
|---|---|
| Thông báo chính xác là gì? | |
| Ai gửi thông báo đó — PC-A hay R1? | |
| ICMP type/code là gì? *(bắt bằng Simulation mode)* | |

### Lỗi 3 — Gán IP trùng subnet trên 2 interface

```cisco
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip address 10.0.1.5 255.255.255.0
```

| | |
|---|---|
| IOS có nhận lệnh không? | |
| Thông báo là gì? | |
| Vì sao IOS chặn được lỗi này? | |

### Lỗi 4 *(tự chọn)* — Xoá gateway của PC-A

Xoá default gateway trên PC-A, rồi ping `10.0.1.1` và `10.0.12.1`.

| | |
|---|---|
| Ping `10.0.1.1` còn được không? Vì sao? | |
| Ping `10.0.12.1` còn được không? Vì sao? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Thêm interface thứ ba cho R1 (`Gi0/2`, IP `10.0.3.1/24`). Bây giờ R1 có mấy route?
2. R1 có route `C 10.0.12.0/30`. PC-A ping `10.0.12.2` — gói đi tới đâu rồi chết?
   *(Gợi ý: nghĩ về chiều về)*
3. Vì sao `show ip route 10.0.1.1` và `show ip route 10.0.1.10` cho kết quả khác nhau,
   dù cả hai đều nằm trong `10.0.1.0/24`?
4. Nếu bạn gán `ip address 10.0.1.1 255.255.255.0` cho Gi0/0 rồi **không** `no shutdown`,
   route nào xuất hiện?

<details>
<summary>Đáp án</summary>

**1.** **6 route** — mỗi interface có đúng 2 route *(`C` cho subnet, `L` cho chính IP)*:

```text
C  10.0.1.0/24      L  10.0.1.1/32
C  10.0.12.0/30     L  10.0.12.1/32
C  10.0.3.0/24      L  10.0.3.1/32
```

**2.** Gói **đi tới được** `10.0.12.2` nhưng **không về được**.

```text
Đi:  PC-A → R1 (route C 10.0.12.0/30) → R2 nhận ✅
Về:  R2 muốn trả lời 10.0.1.10
     → tra routing table của R2: KHÔNG CÓ route tới 10.0.1.0/24
     → DROP ❌
```

👉 Đây chính là **"ping một chiều"** — triệu chứng của **thiếu route chiều về**.
Bài học: luôn kiểm tra `show ip route` ở **cả hai đầu**.

**3.** Vì **longest prefix match**:

| Đích | Route khớp | Thắng | Router làm gì |
|---|---|---|---|
| `10.0.1.1` | `C /24` và **`L /32`** | **`L /32`** *(prefix dài hơn)* | **Xử lý tại chỗ** — tự trả lời |
| `10.0.1.10` | Chỉ `C /24` | `C /24` | **Chuyển tiếp** — ARP rồi gửi ra interface |

Đây là lý do route `L` tồn tại: để router phân biệt *"gói cho tôi"* và *"gói qua tôi"*.

**4.** **Không có route nào.**

Route `C` và `L` chỉ xuất hiện khi interface ở trạng thái **`up/up`**.
Interface `administratively down` → không có route nào, dù đã gán IP.

Kiểm chứng: `show ip interface brief` thấy `administratively down`,
`show ip route` không có dòng nào cho interface đó.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Số route đúng

| Router | Số route | Chi tiết |
|---|:---:|---|
| R1 | **4** | `C 10.0.1.0/24` · `L 10.0.1.1/32` · `C 10.0.12.0/30` · `L 10.0.12.1/32` |
| R2 | **4** | `C 10.0.2.0/24` · `L 10.0.2.1/32` · `C 10.0.12.0/30` · `L 10.0.12.2/32` |

Công thức: **số route = số interface up/up × 2**.

### Bảng ping — kết quả đúng

| Từ PC-A tới | Kết quả | Vì sao |
|---|---|---|
| `10.0.1.1` | ✅ | Cùng subnet với PC-A |
| `10.0.12.1` | ✅ | R1 có route `L` cho IP này — nó tự trả lời |
| `10.0.12.2` | ❌ | Đi tới được nhưng R2 **không có route về** `10.0.1.0/24` |
| `10.0.2.10` | ❌ | R1 không có route tới `10.0.2.0/24` |

### Giải thích các lỗi BREAK

| # | Quan sát | Giải thích |
|:---:|---|---|
| 1 | Mất **2 route**: `C 10.0.12.0/30` và `L 10.0.12.1/32` | Route connected chỉ tồn tại khi interface `up/up` |
| 2 | `Reply from 10.0.1.1: Destination host unreachable` | **R1 gửi**, không phải PC-A. ICMP **Type 3** *(Destination Unreachable)*, Code 0 hoặc 1 |
| 3 | IOS **từ chối**: `% 10.0.1.0 overlaps with GigabitEthernet0/0` | IOS kiểm tra chồng lấn subnet **trên cùng một router** |
| 4 | Ping `10.0.1.1` **vẫn được**; ping `10.0.12.1` **fail** | `10.0.1.1` cùng subnet → PC gửi thẳng, không cần gateway.<br>`10.0.12.1` khác subnet → cần gateway mà PC không có |

> 🔑 Lỗi 4 là bài học tinh tế: **mất gateway không mất hết** — máy vẫn nói chuyện được
> trong cùng subnet. Triệu chứng người dùng: *"ping được máy bên cạnh, không ra được Internet"*.

### Lưu ý về lỗi 3

IOS chỉ phát hiện chồng lấn **trong phạm vi một thiết bị**. Hai router khác nhau cùng
cấu hình `10.0.1.0/24` thì **không ai báo gì** — chỉ khi routing chạy mới vỡ lở.
Đây là lý do tài liệu IP plan *(Lesson 07)* quan trọng.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Số route tôi dự đoán vs thực tế: ___
- Thứ bất ngờ nhất: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
