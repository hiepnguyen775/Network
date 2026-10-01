# LAB 01 — VLSM cho công ty 4 phòng ban

> 📌 **Lab mẫu.** Nó cho thấy một lab "đạt chuẩn" của repo này trông như thế nào —
> đặc biệt là mục **8. BREAK**, phần bắt buộc mà người tự học hay bỏ qua nhất.

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Lesson liên quan** | [`lesson-02-ipv4-va-subnetting.md`](../00-foundation/lesson-02-ipv4-va-subnetting.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ (1h thiết kế trên giấy + 1h dựng & phá) |
| **Độ khó** | ⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Chia VLSM từ một dải `/24` cho 4 nhu cầu khác nhau, **không chồng lấn, không lãng phí**
- [ ] Gán IP đúng cho router và PC, verify bằng `show` và `ping`
- [ ] Chứng minh được hậu quả của **mask mismatch** bằng thực nghiệm
- [ ] Nhận ra triệu chứng "ping một chiều" và truy ra nguyên nhân

## 2. Prerequisite

- [Lesson 02 — IPv4 & Subnetting](../00-foundation/lesson-02-ipv4-va-subnetting.md)
- [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md) — bảng magic number

---

## 3. Topology

```text
   PC-SALES              PC-IT              PC-KT
      │                    │                   │
     SW1 ───────────────── R1 ─────────────── SW2
                            │
                        (Gi0/2)
                            │
                           R2 ── PC-SERVER
                      WAN link /30
```

| Thiết bị | Model gợi ý | Vai trò |
|---|---|---|
| R1, R2 | ISR 2911 (hoặc 1941) | Router, mỗi interface một subnet |
| SW1, SW2 | 2960 | Switch L2 đơn giản, không cần VLAN ở lab này |
| PC × 4 | PC-PT | Máy trạm để test ping |

---

## 4. IP Addressing Table

### Đề bài

Công ty được cấp **`10.0.0.0/24`**. Nhu cầu:

| Phòng ban | Số host cần |
|---|:---:|
| Sales | 50 |
| IT | 25 |
| Kế toán | 12 |
| WAN link R1↔R2 | 2 |

**Nhiệm vụ: chia VLSM trên giấy TRƯỚC khi mở Packet Tracer.**

### Bảng chia *(tự điền — đáp án ở §10)*

| Phòng ban | Host cần | Prefix | Block | Network | First | Last | Broadcast |
|---|:---:|:---:|:---:|---|---|---|---|
| Sales | 50 | | | | | | |
| IT | 25 | | | | | | |
| Kế toán | 12 | | | | | | |
| WAN link | 2 | | | | | | |

### Bảng gán IP thiết bị *(tự điền)*

| Device | Interface | IP | Mask | Gateway |
|---|---|---|---|---|
| R1 | Gi0/0 (Sales) | | | — |
| R1 | Gi0/1 (IT) | | | — |
| R1 | Gi0/2 (WAN) | | | — |
| R2 | Gi0/0 (WAN) | | | — |
| R2 | Gi0/1 (Kế toán) | | | — |
| PC-SALES | Fa0 | | | |
| PC-IT | Fa0 | | | |
| PC-KT | Fa0 | | | |

> 📏 **Quy ước:** gateway luôn là **first usable** của subnet. Thống nhất toàn hệ thống.

---

## 5. Yêu cầu LAB

- [ ] Chia VLSM đúng, **cấp subnet lớn trước**, không chồng lấn
- [ ] Mọi interface `up/up`
- [ ] PC-SALES ping được gateway của nó
- [ ] PC-SALES ping được PC-IT *(cùng router R1)*
- [ ] PC-SALES ping được PC-KT *(qua WAN link, cần static route)*
- [ ] `show ip route` ở R1 hiển thị đủ các subnet connected
- [ ] Hoàn thành **tối thiểu 3 lỗi** ở mục BREAK

---

## 6. Step-by-step

> Ghi lại **những gì bạn thật sự đã làm**, kể cả bước làm sai rồi quay lại.

1. **Chia VLSM trên giấy.** Sắp nhu cầu giảm dần: 50 → 25 → 12 → 2. Cấp từ `10.0.0.0` đi lên.
2. Dựng topology trong Packet Tracer theo sơ đồ §3.
3. Gán IP cho R1 (3 interface), nhớ `no shutdown` từng cái.
4. Gán IP cho R2 (2 interface).
5. Gán IP + gateway cho 4 PC.
6. Verify kết nối **trong cùng subnet** trước — PC ping gateway của chính nó.
7. Thêm static route hai chiều giữa R1 và R2.
8. Verify kết nối **qua router**.
9. Sang mục 8 — BREAK.

```cisco
! R1 — ví dụ cho một interface
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip address <IP_GATEWAY_SALES> <MASK_SALES>
R1(config-if)# description LAN-SALES
R1(config-if)# no shutdown

! Static route R1 → mạng Kế toán sau R2
R1(config)# ip route <NET_KETOAN> <MASK_KETOAN> <IP_R2_WAN>

! Static route R2 → các mạng sau R1
R2(config)# ip route <NET_SALES> <MASK_SALES> <IP_R1_WAN>
R2(config)# ip route <NET_IT>    <MASK_IT>    <IP_R1_WAN>
```

> 💡 Quên static route chiều **về** là lỗi số 1 ở lab này. Triệu chứng: ping đi được, không có reply.

---

## 7. Verification

```cisco
show ip interface brief
show ip route
show ip route connected
ping <ip>
```

```text
# output điển hình để tham chiếu — dán output THẬT từ lab của bạn vào đây
R1# show ip route
      10.0.0.0/8 is variably subnetted, 7 subnets, 4 masks
C        10.0.0.0/26   is directly connected, GigabitEthernet0/0
L        10.0.0.1/32   is directly connected, GigabitEthernet0/0
C        10.0.0.64/27  is directly connected, GigabitEthernet0/1
L        10.0.0.65/32  is directly connected, GigabitEthernet0/1
C        10.0.0.112/30 is directly connected, GigabitEthernet0/2
L        10.0.0.113/32 is directly connected, GigabitEthernet0/2
S        10.0.0.96/28  [1/0] via 10.0.0.114
```

**Bằng chứng lab chạy đúng:**

- [ ] `ping` PC-SALES → gateway: thành công
- [ ] `ping` PC-SALES → PC-IT: thành công
- [ ] `ping` PC-SALES → PC-KT: thành công *(qua 2 router)*
- [ ] `show ip route` ở R1: có đủ 3 `C` + 1 `S`
- [ ] `tracert` từ PC-SALES tới PC-KT: thấy đúng 2 hop

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

> Lab chỉ **xong** khi mục này điền đủ. Mỗi lỗi: phá → quan sát triệu chứng →
> **tự tìm bằng lệnh, không nhìn lại cấu hình mình vừa sửa**.

### Lỗi bắt buộc làm

- [ ] **Lỗi 1 — Mask mismatch:** đổi mask của PC-SALES từ `/26` sang `/24`. Ping gateway còn được không? Ping PC-IT?
- [ ] **Lỗi 2 — Sai gateway:** đổi default gateway của PC-IT thành một IP không tồn tại. Ping trong subnet? Ping ra ngoài?
- [ ] **Lỗi 3 — Thiếu route chiều về:** xoá static route ở R2. Ping từ PC-SALES tới PC-KT — triệu chứng chính xác là gì?

### Lỗi tự chọn thêm

- [ ] **Lỗi 4 — `shutdown` interface Gi0/2 của R1.** Trước khi ping, **đoán trước** `show ip route` sẽ mất dòng nào.
- [ ] **Lỗi 5 — Subnet chồng lấn:** đổi IP của interface IT sang một địa chỉ nằm trong dải Sales. IOS có báo lỗi không?

### Bảng ghi nhận

| # | Lỗi đã tạo | Triệu chứng quan sát được | Lệnh đã dùng để tìm | Nguyên nhân | Cách sửa |
|:---:|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

> Mỗi lỗi tìm ra → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

### Câu hỏi sau khi BREAK

1. Lỗi nào **khó tìm nhất**? Vì sao?
2. Lỗi 1 và lỗi 3 có triệu chứng **giống nhau** ở chỗ nào? Lệnh nào phân biệt được hai cái?
3. Nếu đây là mạng thật đang chạy, lỗi nào gây hậu quả nghiêm trọng nhất?

---

## 9. Challenge

> Tự làm, chưa xem đáp án.

1. Công ty mở thêm phòng **Marketing 30 người**. Dải `10.0.0.0/24` còn chỗ không?
   Nếu có thì ở đâu, prefix nào? Nếu không thì phương án là gì?
2. Thay 2 WAN link `/30` bằng `/31`. Tiết kiệm được bao nhiêu địa chỉ? Có rủi ro gì?
3. Thiết kế lại toàn bộ với yêu cầu **mỗi phòng có dự phòng tăng trưởng 30%**.
   Dải `/24` còn đủ không?

---

## 10. Solution

<details>
<summary>⚠️ Chỉ mở sau khi đã tự chia xong và dựng lab</summary>

### Bảng VLSM

Nguyên tắc: sắp nhu cầu **giảm dần**, cấp từ địa chỉ thấp lên.

| Phòng ban | Host cần | Prefix | Block | Network | First | Last | Broadcast |
|---|:---:|:---:|:---:|---|---|---|---|
| Sales | 50 | `/26` | 64 | `10.0.0.0` | `.1` | `.62` | `.63` |
| IT | 25 | `/27` | 32 | `10.0.0.64` | `.65` | `.94` | `.95` |
| Kế toán | 12 | `/28` | 16 | `10.0.0.96` | `.97` | `.110` | `.111` |
| WAN link | 2 | `/30` | 4 | `10.0.0.112` | `.113` | `.114` | `.115` |

**Còn trống:** `10.0.0.116` → `10.0.0.255` (140 địa chỉ) cho mở rộng sau.

### Vì sao phải cấp lớn trước

Nếu cấp Kế toán (`/28`) trước từ `10.0.0.0`, nó chiếm `.0 → .15`.
Sales (`/26`, block 64) khi đó **không thể** bắt đầu ở `.16` — subnet `/26` chỉ bắt đầu được
ở bội số của 64 (`0, 64, 128, 192`). Phải nhảy lên `.64`, bỏ phí `.16 → .63` = **48 địa chỉ**.

### Gán IP

| Device | Interface | IP | Mask | Gateway |
|---|---|---|---|---|
| R1 | Gi0/0 (Sales) | `10.0.0.1` | `255.255.255.192` | — |
| R1 | Gi0/1 (IT) | `10.0.0.65` | `255.255.255.224` | — |
| R1 | Gi0/2 (WAN) | `10.0.0.113` | `255.255.255.252` | — |
| R2 | Gi0/0 (WAN) | `10.0.0.114` | `255.255.255.252` | — |
| R2 | Gi0/1 (Kế toán) | `10.0.0.97` | `255.255.255.240` | — |
| PC-SALES | Fa0 | `10.0.0.10` | `255.255.255.192` | `10.0.0.1` |
| PC-IT | Fa0 | `10.0.0.70` | `255.255.255.224` | `10.0.0.65` |
| PC-KT | Fa0 | `10.0.0.100` | `255.255.255.240` | `10.0.0.97` |

### Cấu hình

```cisco
! ───────── R1 ─────────
hostname R1
interface GigabitEthernet0/0
 description LAN-SALES
 ip address 10.0.0.1 255.255.255.192
 no shutdown
interface GigabitEthernet0/1
 description LAN-IT
 ip address 10.0.0.65 255.255.255.224
 no shutdown
interface GigabitEthernet0/2
 description WAN-TO-R2
 ip address 10.0.0.113 255.255.255.252
 no shutdown
!
ip route 10.0.0.96 255.255.255.240 10.0.0.114

! ───────── R2 ─────────
hostname R2
interface GigabitEthernet0/0
 description WAN-TO-R1
 ip address 10.0.0.114 255.255.255.252
 no shutdown
interface GigabitEthernet0/1
 description LAN-KETOAN
 ip address 10.0.0.97 255.255.255.240
 no shutdown
!
ip route 10.0.0.0  255.255.255.192 10.0.0.113
ip route 10.0.0.64 255.255.255.224 10.0.0.113
```

### Giải thích các lỗi BREAK

| # | Triệu chứng | Nguyên nhân | Lệnh phát hiện |
|:---:|---|---|---|
| 1 | PC-SALES vẫn ping được gateway, nhưng ping PC-IT thì **gửi thẳng thay vì qua gateway** → fail | `/24` làm PC nghĩ `10.0.0.70` cùng subnet → ARP trực tiếp, không ai trả lời | `ipconfig` trên PC, so với `show ip int brief` ở R1 |
| 2 | Ping trong subnet OK, ping ra ngoài **timeout ngay** | PC không biết gửi cho ai khi đích khác subnet | `ipconfig` → gateway sai |
| 3 | Ping đi được tới PC-KT nhưng **không có reply** | R2 không có route về mạng Sales | `show ip route` ở **R2** |
| 4 | `show ip route` mất cả `C 10.0.0.112/30` lẫn `S 10.0.0.96/28` | Route static mất theo vì next-hop không còn reachable | `show ip int brief` → `administratively down` |
| 5 | IOS **từ chối** lệnh với thông báo overlap | IOS kiểm tra chồng lấn subnet trên cùng router | Thông báo lỗi ngay khi gõ |

> 🔑 **Câu hỏi 2 ở §8:** lỗi 1 và lỗi 3 đều cho triệu chứng "ping không được".
> Phân biệt bằng **nơi gói tin chết**: lỗi 1 thì gói **không rời khỏi PC** (xem `arp -a` thấy
> incomplete); lỗi 3 thì gói **đi tới đích rồi chết ở chiều về** (`debug ip icmp` ở R2 vẫn thấy request).

### Challenge

1. **Marketing 30 người** → cần `/26` (62 host) vì `/27` chỉ 30 host, không có dự phòng.
   Còn chỗ: `10.0.0.128/26` (`.128` → `.191`). ✅ Vừa đẹp, vì `/26` phải bắt đầu ở bội số 64.
2. **`/31` thay `/30`:** mỗi link tiết kiệm 2 địa chỉ. Rủi ro: **thiết bị cũ không hỗ trợ RFC 3021**,
   và một số tool giám sát hiểu nhầm. Trong mạng toàn thiết bị mới thì an toàn.
3. **Dự phòng 30%:** Sales 50→65 cần `/25` (126 host); IT 25→33 cần `/26`; KT 12→16 cần `/27`
   (30 host); WAN `/30`. Tổng: 128+64+32+4 = **228/256** — vẫn đủ, nhưng chỉ còn 28 địa chỉ.
   👉 Kết luận thực tế: `/24` **quá chật** cho công ty có kế hoạch mở rộng. Nên xin `/23` ngay từ đầu.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Mất nhiều thời gian nhất ở bước: ___
- Lần sau tôi sẽ làm khác ở chỗ: ___
- Thứ tôi tưởng mình hiểu nhưng thật ra chưa: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
