# LAB 14 — RSTP, PortFast, BPDU Guard — đo thời gian hội tụ

| | |
|---|---|
| **Phase** | 1 |
| **Lesson liên quan** | [Lesson 16 — RSTP · PortFast · BPDU Guard · Root Guard](../01-switching/lesson-16-rstp-portfast-bpduguard.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] **Đo** thời gian hội tụ của STP cổ điển vs RSTP bằng ping liên tục
- [ ] Chứng minh **PortFast** cho PC lên mạng ngay, không chờ 30 giây
- [ ] Chứng minh **BPDU Guard** shut cổng khi có switch lạ / tấn công
- [ ] Hiểu các vai trò port RSTP: root / designated / **alternate** / backup
- [ ] Ép và kiểm tra **root bridge**

## 2. Prerequisite

- [Lesson 15](../01-switching/lesson-15-stp.md) — STP cơ bản, root election
- [Lesson 16](../01-switching/lesson-16-rstp-portfast-bpduguard.md) — RSTP, các bảo vệ
- [LAB 13](lab13-stp.md) — STP *(nền tảng)*

---

## 3. Topology

```text
            SW1 (muốn làm root)
           /   \
       Gi0/1    Gi0/2
         /         \
       SW2 ──────── SW3
          Gi0/3 (link dự phòng)
        │
      PC-A (Fa0/5)
```

Tam giác 3 switch → có **vòng lặp vật lý** → STP phải chặn một cổng.

| Thiết bị | Vai trò |
|---|---|
| SW1 | Root bridge *(ép priority thấp nhất)* |
| SW2, SW3 | Non-root |
| PC-A | Cắm Fa0/5 SW2, dùng để đo & test PortFast |

## 4. IP Addressing Table

| Device | Interface | IP | Ghi chú |
|---|---|---|---|
| SW1 | Vlan1 | `10.0.0.1/24` | quản trị |
| SW2 | Vlan1 | `10.0.0.2/24` | quản trị |
| SW3 | Vlan1 | `10.0.0.3/24` | quản trị |
| PC-A | Fa0 | `10.0.0.10/24` | đích ping: `10.0.0.1` |

---

## 5. Yêu cầu LAB

- [ ] SW1 là root cho VLAN 1 *(kiểm tra bằng `show spanning-tree`)*
- [ ] Đo và ghi lại thời gian mất gói khi đứt link, STP vs RSTP
- [ ] PortFast + BPDU Guard trên Fa0/5
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Ép root bridge

```cisco
! Trên SW1
SW1(config)# spanning-tree vlan 1 priority 0
! (hoặc) spanning-tree vlan 1 root primary
```

```cisco
SW1# show spanning-tree vlan 1
! xác nhận: "This bridge is the root"
```

### Bước 2 — Đo hội tụ STP cổ điển ⭐

```cisco
! Đảm bảo đang chạy STP cũ (pvst)
SW1(config)# spanning-tree mode pvst
SW2(config)# spanning-tree mode pvst
SW3(config)# spanning-tree mode pvst
```

Tìm cổng **blocking** *(trên SW2 hoặc SW3)*:

```cisco
SW2# show spanning-tree vlan 1 | include BLK|Altn
```

> 🔴 **DỰ ĐOÁN:** từ PC-A ping liên tục `10.0.0.1`, rồi **tắt** link đang forward
> *(shutdown cổng root của SW2)*. Mất bao nhiêu gói trước khi thông lại?
> STP cũ: ___ giây? RSTP: ___ giây?

```cisco
PC> ping -t 10.0.0.1          ! ping liên tục (Packet Tracer: ping 10.0.0.1 -n 10000)
! Trên SW2: shutdown cổng đang forward về root
SW2(config)# interface Gi0/1
SW2(config-if)# shutdown
```

| | STP cổ điển (pvst) |
|---|---|
| Số gói mất | |
| Thời gian ước tính *(gói × 1s)* | |

> 💡 STP cũ: Blocking→Listening *(15s)* → Learning *(15s)* → Forwarding = **~30-50s**.

### Bước 3 — Đo hội tụ RSTP

```cisco
SW1(config)# spanning-tree mode rapid-pvst
SW2(config)# spanning-tree mode rapid-pvst
SW3(config)# spanning-tree mode rapid-pvst
```

Lặp lại đo như Bước 2.

| | RSTP (rapid-pvst) |
|---|---|
| Số gói mất | |
| Thời gian ước tính | |

> 💡 RSTP hội tụ **dưới 1 giây** nhờ cổng **alternate** đã tính sẵn, chuyển ngay.

### Bước 4 — PortFast + BPDU Guard

```cisco
SW2(config)# interface Fa0/5
SW2(config-if)# spanning-tree portfast
SW2(config-if)# spanning-tree bpduguard enable
```

**Test PortFast:** rút rồi cắm lại cáp PC-A, đo thời gian link lên forwarding.

**Test BPDU Guard:** rút PC-A, cắm một **switch** vào Fa0/5 *(hoặc bật một thiết bị
gửi BPDU)*.

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| PC-A cắm vào → forwarding ngay *(~0s)* | ✅ | |
| Cắm switch vào Fa0/5 | Cổng `err-disabled` | |
| `show interfaces status err-disabled` | Fa0/5 xuất hiện | |

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show spanning-tree vlan 1
VLAN0001
  Spanning tree enabled protocol rstp
  Root ID    Priority    1
             Address     00D0.SW1.0001
             This bridge is the root

  Interface        Role Sts Cost      Prio.Nbr Type
  ---------------- ---- --- --------- -------- --------
  Gi0/1            Desg FWD 4         128.1    P2p
  Gi0/2            Desg FWD 4         128.2    P2p
```

```text
# output điển hình — cổng alternate trên switch non-root
SW2# show spanning-tree vlan 1
  Interface        Role Sts Cost      Prio.Nbr Type
  ---------------- ---- --- --------- -------- --------
  Gi0/1            Root FWD 4         128.1    P2p
  Gi0/3            Altn BLK 4         128.3    P2p      ← chặn vòng lặp
  Fa0/5            Desg FWD 19        128.5    P2p Edge ← PortFast
```

```text
# output điển hình — BPDU Guard bắt được switch lạ
%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port Fa0/5 with BPDU Guard enabled.
Disabling port.
%PM-4-ERR_DISABLE: bpduguard error detected on Fa0/5, putting Fa0/5 in err-disable
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | SW1 là root VLAN 1 | "This bridge is the root" | |
| 2 | Có cổng `Altn BLK` trên non-root | ✅ | |
| 3 | Hội tụ STP cũ | ~30-50s | |
| 4 | Hội tụ RSTP | <1-2s | |
| 5 | PC-A qua PortFast lên ngay | ✅ | |
| 6 | Switch lạ vào Fa0/5 → err-disable | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — PortFast trên cổng nối switch ⭐

```cisco
SW2(config)# interface Gi0/1          ! cổng NỐI SW1 (uplink)
SW2(config-if)# spanning-tree portfast
```

| | |
|---|---|
| IOS có cảnh báo gì khi bật PortFast trên cổng này? | |
| Nếu có vòng lặp, PortFast gây hậu quả gì? *(gợi ý: bỏ qua listening/learning)* | |
| Vì sao PortFast **chỉ** dành cho cổng nối host? | |

### Lỗi 2 — Hai switch tranh root không mong muốn

```cisco
! Cho SW3 priority thấp hơn SW1
SW3(config)# spanning-tree vlan 1 priority 0
! SW1 vẫn priority 0 → hoà priority → so MAC
```

| | |
|---|---|
| Ai thành root? Dựa vào tiêu chí nào khi priority bằng nhau? | |
| `show spanning-tree` trên từng switch cho thấy gì? | |
| Topology có bị đổi đường forward không? | |
| Cách ép đúng root là gì? | |

### Lỗi 3 — Trộn RSTP và STP cũ

```cisco
! SW3 quay về pvst, SW1 & SW2 giữ rapid-pvst
SW3(config)# spanning-tree mode pvst
```

| | |
|---|---|
| Link giữa SW2 (rapid) và SW3 (cũ) hoạt động không? | |
| RSTP có "rớt" về tốc độ STP cũ trên link đó không? | |
| Hội tụ toàn mạng giờ nhanh hay chậm? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Giải thích 4 vai trò port RSTP: root, designated, **alternate**, backup.
   Cái nào thay thế "blocking" của STP cũ?
2. Vì sao RSTP hội tụ nhanh hơn hẳn? Nêu 2 cơ chế chính.
3. Bạn muốn SW1 là root, SW2 là **root dự phòng** *(backup)*. Cấu hình thế nào?
4. Một cổng err-disabled vì BPDU Guard. Nêu 2 cách phục hồi và khi nào dùng cách nào.

<details>
<summary>Đáp án</summary>

**1.** Bốn vai trò:

| Vai trò | Ý nghĩa | Trạng thái |
|---|---|---|
| **Root port** | Cổng tốt nhất **hướng về** root bridge | Forwarding |
| **Designated** | Cổng tốt nhất **của một segment** *(gửi BPDU ra)* | Forwarding |
| **Alternate** | Đường **dự phòng** tới root — thay thế root port nếu nó hỏng | Blocking *(discarding)* |
| **Backup** | Dự phòng cho một designated port *(hiếm, chỉ khi hub)* | Blocking |

**Alternate** chính là cái thay thế "blocking" của STP cũ — nhưng RSTP **tính sẵn**
nó, nên khi root port hỏng, alternate chuyển sang forwarding **ngay lập tức**.

**2.** Hai cơ chế:
- **Cổng alternate tính sẵn:** không chờ 2×forward-delay *(30s)* như STP cũ, mà
  chuyển ngay vì đã biết trước đường thay thế.
- **Proposal/Agreement handshake trên link point-to-point:** hai switch "bắt tay"
  trực tiếp để đồng ý ai là designated → bỏ qua listening/learning.

Thêm: **edge port (PortFast)** lên forwarding tức thì.

**3.**

```cisco
SW1(config)# spanning-tree vlan 1 root primary     ! priority 24576
SW2(config)# spanning-tree vlan 1 root secondary   ! priority 28672
```

`root primary` đặt priority 24576 *(hoặc thấp hơn root hiện tại)*; `root secondary`
đặt 28672 → SW2 thắng mọi switch khác nhưng thua SW1. Nếu SW1 chết, SW2 lên root.

**4.** Hai cách:

| Cách | Khi nào dùng |
|---|---|
| **Thủ công:** `shutdown` → `no shutdown` trên cổng | Khi đã **xác minh** nguyên nhân *(gỡ switch lạ)* và muốn bật lại ngay |
| **Tự động:** `errdisable recovery cause bpduguard` + `errdisable recovery interval 300` | Môi trường production muốn tự hồi sau N giây mà không cần admin — nhưng **cẩn thận**: nếu tấn công còn đó, cổng sẽ shut lại liên tục |

Nguyên tắc: điều tra nguyên nhân **trước**, rồi mới phục hồi. Tự động chỉ hợp lý khi
sự cố thường là thoáng qua.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Kết quả đo điển hình

| Giao thức | Gói mất | Thời gian |
|---|:---:|:---:|
| STP cổ điển (pvst) | ~30-50 | ~30-50s |
| RSTP (rapid-pvst) | 0-2 | <2s |

Chênh lệch khổng lồ này là lý do **không ai dùng STP cũ nữa** — mọi switch hiện đại
chạy RSTP/MST.

### Giải thích các lỗi BREAK

**Lỗi 1 — PortFast trên uplink ⭐:**

```text
# output điển hình — tự verify trên lab của bạn
%SPANTREE-2-PORTFAST_PORT_ ... : PortFast has been configured on Gi0/1 but
should only be enabled on ports connected to a single host.
```

PortFast bỏ qua listening/learning → cổng lên forwarding **ngay**. Trên cổng nối
switch, nếu có vòng lặp, frame được forward **trước khi** STP kịp chặn →
**broadcast storm** tạm thời. Vì thế PortFast chỉ cho cổng nối **một host duy nhất**
*(PC, server, máy in)* — nơi chắc chắn không có vòng lặp.

**Lỗi 2 — tranh root:**

Khi priority **bằng nhau** *(cả hai = 0)*, tiêu chí phân thắng bại là
**MAC address thấp hơn** thắng. SW nào MAC nhỏ hơn thành root → có thể **không phải**
switch bạn muốn → đường forward bị bẻ.

Cách ép đúng: dùng `root primary`/`root secondary` *(tự chọn priority phù hợp)*,
hoặc đặt priority rõ ràng khác nhau *(SW1=0, SW2=4096)*. Đừng để hai switch cùng
priority.

**Lỗi 3 — trộn RSTP/STP cũ:**

| Quan sát | Giải thích |
|---|---|
| Link SW2↔SW3 vẫn chạy | RSTP **tương thích ngược** |
| Nhưng trên link đó RSTP **rớt** về STP cũ | RSTP phát hiện hàng xóm nói STP cũ → dùng timer cũ *(30s)* trên cổng đó |
| Phần mạng rapid-pvst vẫn nhanh | Chỉ link lai bị chậm |

👉 Bài học: **đồng bộ mode trên toàn mạng**. Một switch cũ kéo tụt cả vùng quanh nó.

### Bảng tổng kết

| Tính năng | Đặt ở đâu | Tác dụng |
|---|---|---|
| `root primary/secondary` | Switch lõi | Kiểm soát root bridge |
| `rapid-pvst` | Mọi switch | Hội tụ <1s |
| `portfast` | Cổng host | Lên mạng ngay |
| `bpduguard` | Cổng host | Chặn switch lạ/tấn công |
| `guard root` | Uplink | Chặn switch ngoài thành root |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Hội tụ STP cũ vs RSTP tôi đo được: ___ vs ___ giây
- Lỗi 1 (PortFast sai chỗ) — tôi nhớ quy tắc "chỉ cổng host" chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
