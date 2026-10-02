# LAB 15 — EtherChannel LACP + Port Security

| | |
|---|---|
| **Phase** | 1 |
| **Lesson liên quan** | [Lesson 17 — EtherChannel (LACP) · Port Security](../01-switching/lesson-17-etherchannel-port-security.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Gộp 2 link vật lý thành **1 EtherChannel** bằng LACP
- [ ] Chứng minh STP coi bundle là **một** cổng *(không chặn link thừa)*
- [ ] Chứng minh **failover**: rút 1 link, bundle vẫn chạy
- [ ] Hiểu các chế độ `active/passive/on` và vì sao **mismatch** làm hỏng
- [ ] Cấu hình **Port Security** 3 chế độ violation và quan sát khác biệt

## 2. Prerequisite

- [Lesson 17](../01-switching/lesson-17-etherchannel-port-security.md) — EtherChannel, Port Security
- [LAB 14](lab14-rstp-bpduguard.md) — STP/RSTP *(hiểu vì sao cần bundle)*

---

## 3. Topology

```text
         ┌──────── SW1 ────────┐
         │  Gi0/1   Gi0/2       │  ← 2 link gộp thành Po1
         └───┬────────┬─────────┘
             │        │
         ┌───┴────────┴─────────┐
         │  Gi0/1   Gi0/2       │
         │       SW2            │
         │  Fa0/5               │ ← PC-A (test Port Security)
         └──────────────────────┘
```

| Thiết bị | Vai trò |
|---|---|
| SW1, SW2 | Nối nhau bằng 2 link → EtherChannel Po1 |
| PC-A | Fa0/5 SW2, test Port Security |
| PC-B | dùng để giả MAC thứ hai khi test violation |

## 4. IP Addressing Table

| Device | Interface | IP | Ghi chú |
|---|---|---|---|
| SW1 | Vlan1 | `10.0.0.1/24` | quản trị |
| SW2 | Vlan1 | `10.0.0.2/24` | quản trị |
| PC-A | Fa0 | `10.0.0.10/24` | — |
| PC-B | Fa0 | `10.0.0.11/24` | — |

---

## 5. Yêu cầu LAB

- [ ] Po1 gồm 2 link, LACP, trạng thái `SU` + cổng con `P`
- [ ] Rút 1 link → ping SW1↔SW2 không đứt
- [ ] Port Security trên Fa0/5: thử lần lượt `protect` / `restrict` / `shutdown`
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Tạo EtherChannel bằng LACP

> ⚠️ **Cấu hình trên interface RANGE, không phải từng cổng rời** — nếu không,
> hai cổng có thể vào channel-group theo cách không khớp.

```cisco
! ══ SW1 ══
SW1(config)# interface range Gi0/1 - 2
SW1(config-if-range)# channel-group 1 mode active     ! LACP active
SW1(config-if-range)# exit
SW1(config)# interface Port-channel 1
SW1(config-if)# switchport mode trunk

! ══ SW2 (phải tương thích: active-active hoặc active-passive) ══
SW2(config)# interface range Gi0/1 - 2
SW2(config-if-range)# channel-group 1 mode active
SW2(config)# interface Port-channel 1
SW2(config-if)# switchport mode trunk
```

> 🔑 **Ma trận tương thích LACP:**
> | SW1 | SW2 | Lên bundle? |
> |---|---|---|
> | active | active | ✅ |
> | active | passive | ✅ |
> | passive | passive | ❌ *(không ai khởi xướng)* |
> | on | active/passive | ❌ *(on = không dùng LACP)* |
> | on | on | ✅ *(nhưng không có cơ chế kiểm tra)* |

### Bước 2 — Kiểm tra bundle

```cisco
SW1# show etherchannel summary
```

> 🔴 **DỰ ĐOÁN:** `show spanning-tree` giờ hiển thị **mấy** cổng tới SW2 —
> hai cổng Gi0/1, Gi0/2 riêng lẻ, hay một cổng Po1? Cổng nào bị STP chặn?

### Bước 3 — Test failover ⭐

```cisco
! Ping liên tục SW1 → SW2
SW1# ping 10.0.0.2 repeat 10000
! Trong lúc ping: rút (shutdown) MỘT cổng con
SW1(config)# interface Gi0/1
SW1(config-if)# shutdown
```

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| Ping có đứt khi rút 1 link? | Gần như không *(0-1 gói)* | |
| `show etherchannel summary` | Po1 vẫn `SU`, còn 1 cổng `P` | |
| Băng thông bundle | Giảm một nửa nhưng vẫn thông | |

### Bước 4 — Port Security 3 chế độ

```cisco
SW2(config)# interface Fa0/5
SW2(config-if)# switchport mode access
SW2(config-if)# switchport port-security
SW2(config-if)# switchport port-security maximum 1
SW2(config-if)# switchport port-security mac-address sticky
SW2(config-if)# switchport port-security violation protect     ! thử lần lượt
```

Thử vi phạm: cắm PC-B *(MAC thứ hai)* vào cùng cổng qua một hub, hoặc đổi MAC PC-A.
Lần lượt đổi `violation` giữa 3 chế độ và quan sát:

| violation | Frame vi phạm | Đếm counter | Log | Cổng |
|---|:---:|:---:|:---:|---|
| `protect` | Drop | ❌ Không | ❌ Không | Vẫn up |
| `restrict` | Drop | ✅ Có | ✅ Có | Vẫn up |
| `shutdown` | Drop | ✅ Có | ✅ Có | **err-disabled** |

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show etherchannel summary
Flags:  D - down        P - bundled in port-channel
        I - stand-alone  s - suspended
        S - Layer2       U - in use
Number of channel-groups in use: 1
Group  Port-channel  Protocol    Ports
------+-------------+-----------+----------------------------------
1      Po1(SU)        LACP        Gi0/1(P)    Gi0/2(P)
```

```text
# output điển hình — sau khi rút 1 link
SW1# show etherchannel summary
1      Po1(SU)        LACP        Gi0/1(D)    Gi0/2(P)      ← còn 1 cổng, bundle vẫn U
```

```text
# output điển hình — STP coi bundle là 1 cổng
SW1# show spanning-tree vlan 1 | include Po1
Po1              Desg FWD 3         128.27   P2p
```

```text
# output điển hình — Port Security violation (shutdown)
SW2# show port-security interface Fa0/5
Port Security              : Enabled
Port Status                : Secure-shutdown
Violation Mode             : Shutdown
Maximum MAC Addresses      : 1
Total MAC Addresses        : 1
Security Violation Count   : 1
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | Po1 = `SU`, 2 cổng `P` | ✅ | |
| 2 | STP thấy 1 cổng Po1 *(không chặn link thừa)* | ✅ | |
| 3 | Rút 1 link → ping không đứt | ✅ | |
| 4 | `protect` → drop im lặng | ✅ | |
| 5 | `restrict` → drop + counter tăng | ✅ | |
| 6 | `shutdown` → cổng err-disabled | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — LACP mode mismatch ⭐

```cisco
! SW2 đổi sang passive, SW1 giữ... passive luôn
SW2(config)# interface range Gi0/1 - 2
SW2(config-if-range)# channel-group 1 mode passive
SW1(config)# interface range Gi0/1 - 2
SW1(config-if-range)# channel-group 1 mode passive
```

| | |
|---|---|
| `show etherchannel summary` — Po1 trạng thái gì? | |
| Vì sao passive-passive **không** lên bundle? | |
| Cặp mode nào hợp lệ? | |

### Lỗi 2 — Trộn `on` với LACP

```cisco
SW1(config)# interface range Gi0/1 - 2
SW1(config-if-range)# channel-group 1 mode on          ! on = không LACP
! SW2 giữ active
```

| | |
|---|---|
| Bundle có lên không? | |
| Rủi ro của `mode on` so với LACP là gì? *(gợi ý: không kiểm tra hai đầu)* | |
| Vì sao production nên dùng LACP thay vì `on`? | |

### Lỗi 3 — Cấu hình hai cổng không đồng nhất

```cisco
! Gi0/1 là trunk, Gi0/2 là access → đưa cả hai vào channel-group
SW1(config)# interface Gi0/1
SW1(config-if)# switchport mode trunk
SW1(config)# interface Gi0/2
SW1(config-if)# switchport mode access
```

| | |
|---|---|
| Cổng nào vào được bundle, cổng nào bị loại? | |
| `show etherchannel summary` hiện flag gì cho cổng bị loại? | |
| Các tham số nào phải **giống nhau** giữa các cổng con? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Vì sao gộp 2 link **không** bị STP chặn, trong khi 2 link rời thì một cái bị block?
2. EtherChannel load-balance theo gì? Hai PC nói chuyện qua bundle có dùng **cả hai**
   link không?
3. Port Security: khi nào chọn `restrict`, khi nào chọn `shutdown`? Vì sao ít ai dùng
   `protect`?
4. Cổng Port Security `err-disabled` cả đêm, sáng ra nhân viên không vào mạng được.
   Nêu quy trình xử lý và cách phòng ngừa.

<details>
<summary>Đáp án</summary>

**1.** Hai link rời = STP thấy **hai đường** giữa hai switch → có vòng lặp → chặn một.
Khi gộp thành EtherChannel, STP coi cả bundle là **một cổng logic duy nhất (Po1)** →
không có vòng lặp để chặn → **cả hai link cùng forward**. Đó chính là lợi ích:
tận dụng toàn bộ băng thông thay vì để một link "ngủ".

**2.** EtherChannel **không** chia nhỏ một luồng — nó băm *(hash)* theo src/dst
MAC/IP/port để chọn link cho **mỗi luồng**. Mặc định thường theo **src-dst MAC** hoặc
**src-dst IP**.

Hai PC nói chuyện = **một** cặp src-dst → hash ra **một** link duy nhất → chỉ dùng
một link, **không** được gấp đôi tốc độ cho một luồng. Băng thông gộp chỉ thể hiện khi
có **nhiều luồng khác nhau** chia đều qua các link.

```cisco
! Đổi thuật toán hash
SW1(config)# port-channel load-balance src-dst-ip
```

**3.**

| Chế độ | Khi nào dùng |
|---|---|
| `shutdown` *(mặc định)* | Môi trường **an ninh cao** — vi phạm = ngắt cổng, buộc admin kiểm tra. An toàn nhất |
| `restrict` | Môi trường cần **tiếp tục hoạt động** nhưng vẫn muốn biết — drop MAC thừa, vẫn log/đếm để giám sát |
| `protect` | **Hiếm dùng** — drop im lặng, không log không đếm → bạn **không biết** đang bị tấn công. Chỉ hợp vài kịch bản đặc biệt |

Lý do ít dùng `protect`: nó "giấu" sự cố → mất khả năng phát hiện. `restrict` làm
đúng việc đó mà vẫn báo.

**4.** Quy trình:

```text
1. show interfaces status err-disabled  → xác nhận cổng + lý do (psecure-violation)
2. show port-security interface Fa0/x    → xem MAC vi phạm là gì
3. Điều tra: nhân viên đổi máy? cắm thêm switch? bị tấn công?
4. Nếu hợp lệ: cập nhật sticky MAC / tăng maximum
5. Phục hồi cổng: shutdown → no shutdown (hoặc clear port-security)
```

Phòng ngừa:
```cisco
! Tự hồi sau 5 phút (cân nhắc rủi ro)
errdisable recovery cause psecure-violation
errdisable recovery interval 300
! Hoặc dùng restrict thay shutdown cho cổng ít rủi ro
! Và đặt maximum hợp lý (2-3 cho cổng có IP phone)
```

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — passive-passive ⭐:**

```text
# output điển hình — tự verify trên lab của bạn
SW1# show etherchannel summary
1      Po1(SD)        LACP        Gi0/1(I)    Gi0/2(I)
```

`passive` nghĩa là *"tôi chờ đối phương mời"*. Cả hai cùng chờ → **không ai gửi lời
mời LACP** → bundle không hình thành. Cổng ở trạng thái `I` *(stand-alone)*, Po1 `SD`
*(down)*.

Cặp hợp lệ: **active-active** hoặc **active-passive** *(ít nhất một bên active)*.

**Lỗi 2 — `on` + LACP:**

```text
# output điển hình — tự verify trên lab của bạn
SW1# show etherchannel summary
1      Po1(SD)        -           Gi0/1(s)    Gi0/2(s)
```

`mode on` = **ép** bundle, **không** chạy LACP. SW1 (on) không gửi LACP, SW2 (active)
chờ LACP mãi không thấy → không khớp → bundle không ổn định/down.

Rủi ro `on`: **không có cơ chế kiểm tra hai đầu**. Nếu một bên cấu hình sai *(chỉ một
cổng vào group)*, `on` vẫn "gộp" → tạo vòng lặp hoặc đen traffic. LACP phát hiện
mismatch và **từ chối** gộp → an toàn hơn. Vì thế production dùng **LACP**.

**Lỗi 3 — cổng không đồng nhất:**

```text
# output điển hình — tự verify trên lab của bạn
SW1# show etherchannel summary
1      Po1(SU)        LACP        Gi0/1(P)    Gi0/2(w)      ← Gi0/2 bị loại
```

EtherChannel yêu cầu các cổng con **giống hệt nhau** về: speed, duplex, **switchport
mode** *(trunk/access)*, allowed VLAN, native VLAN. Gi0/2 là access trong khi Po1 là
trunk → **không tương thích** → bị loại khỏi bundle *(flag `w` — waiting / không đủ
điều kiện)*.

Sửa: đảm bảo mọi cổng con cùng cấu hình L2 trước khi vào channel-group. Tốt nhất
cấu hình trên `interface Port-channel 1` rồi để cổng con kế thừa.

### Bảng tổng kết

| Khái niệm | Điểm cốt lõi |
|---|---|
| Bundle vs STP | STP thấy 1 cổng → không chặn → dùng cả 2 link |
| LACP mode | ít nhất 1 bên active; passive-passive fail; on không kiểm tra |
| Load-balance | theo luồng *(hash)*, 1 luồng = 1 link |
| Cổng con | phải đồng nhất speed/duplex/mode/VLAN |
| Port Security violation | shutdown *(an toàn)* / restrict *(giám sát)* / protect *(ẩn, ít dùng)* |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Rút 1 link bundle mất mấy gói? ___
- Lỗi 1 (passive-passive) — tôi nhớ ma trận LACP chưa? ___
- 3 chế độ violation khác nhau thế nào? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
