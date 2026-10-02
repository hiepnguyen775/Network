# LAB 70 — Dual-WAN với IP SLA + track

| | |
|---|---|
| **Phase** | 7 |
| **Lesson liên quan** | [Lesson 39 — WAN concepts · SLA · dual-WAN](../07-wan-vpn/lesson-39-wan-concepts.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Chứng minh **giới hạn của floating static** *(không phát hiện lỗi ở xa)*
- [ ] Dùng **IP SLA** để thăm dò đích thật, **track** để liên kết với route
- [ ] Failover **tự động** khi đường chính lỗi — kể cả lỗi ở xa
- [ ] Đo thời gian chuyển đổi
- [ ] Tự gây & sửa 3 lỗi dual-WAN

## 2. Prerequisite

- [Lesson 39](../07-wan-vpn/lesson-39-wan-concepts.md) — dual-WAN, IP SLA, track
- [LAB 21](lab21-static-default-floating.md) — floating static *(và giới hạn của nó)*
- [LAB 32](lab32-nat-nang-cao.md) — dual-WAN NAT

---

## 3. Topology

```text
                  ISP-A (chính)
                 / 203.0.113.1
   LAN ── R1 ───┤
   10.0.0.0/24   \ 198.51.100.1
                  ISP-B (dự phòng)
                        │
                  cả hai tới  8.8.8.8
```

## 4. IP Addressing Table

| Device | Interface | IP | Vai trò |
|---|---|---|---|
| R1 | Gi0/0 | `10.0.0.1/24` | LAN |
| R1 | Gi0/1 | `203.0.113.2/30` | WAN-A *(chính)* |
| R1 | Gi0/2 | `198.51.100.2/30` | WAN-B *(dự phòng)* |
| ISP-A | Gi · Lo | `203.0.113.1/30` · `8.8.8.8` | — |
| ISP-B | Gi · Lo | `198.51.100.1/30` · `8.8.8.8` | — |

---

## 5. Yêu cầu LAB

- [ ] Phần A: floating static — chứng minh **không** failover khi lỗi ở xa
- [ ] Phần B: IP SLA + track — failover tự động kể cả lỗi ở xa
- [ ] Đo thời gian chuyển đổi
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Phần A — Floating static và giới hạn của nó ⭐

```cisco
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1        ! AD 1, đường chính
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 10    ! AD 10, floating backup
```

> 🔴 **DỰ ĐOÁN 1:** rút cáp **Gi0/1** *(link trực tiếp xuống)* → failover không?
> **DỰ ĐOÁN 2:** nếu ISP-A hỏng ở **xa** *(link Gi0/1 vẫn up, nhưng `8.8.8.8` không tới
> được qua A)* → failover không?

```text
Test 1: shutdown Gi0/1  → floating static CÓ failover (route biến mất khi interface down)
Test 2: để Gi0/1 up, nhưng chặn traffic ở ISP-A (mô phỏng lỗi xa)
        → floating static KHÔNG failover → traffic đổ vào hố đen
```

👉 Đây là **giới hạn cốt lõi**: floating static chỉ thấy **trạng thái interface của
chính nó**, mù với lỗi ở xa.

### Phần B — IP SLA + track

```cisco
! 1. IP SLA: ping 8.8.8.8 QUA đường A liên tục
R1(config)# ip sla 1
R1(config-ip-sla)# icmp-echo 8.8.8.8 source-interface Gi0/1
R1(config-ip-sla-echo)# frequency 5
R1(config)# ip sla schedule 1 life forever start-time now

! 2. Track: theo dõi IP SLA 1
R1(config)# track 1 ip sla 1 reachability

! 3. Gắn track vào route chính → route chỉ tồn tại khi track UP
R1(config)# no ip route 0.0.0.0 0.0.0.0 203.0.113.1
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 1
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 10
```

> 🔑 Giờ route chính **phụ thuộc vào việc ping `8.8.8.8` thành công qua A**. Nếu A hỏng
> ở bất kỳ đâu *(gần hay xa)*, ping fail → track DOWN → route chính bị gỡ → floating
> backup lên. **Phát hiện được lỗi ở xa** — điều floating static không làm được.

> ⚠️ Cần route riêng ép IP SLA đi đúng đường A, nếu không probe có thể đi đường B:
> ```cisco
> R1(config)# ip route 8.8.8.8 255.255.255.255 203.0.113.1
> ```

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip sla statistics 1
IPSLA operation id: 1
        Latest RTT: 2 ms
Latest operation return code: OK
Number of successes: 48
Number of failures: 0
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show track 1
Track 1
  IP SLA 1 reachability
  Reachability is Up
    3 changes, last change 00:04:12
  Tracked by:
    STATIC-IP-ROUTING 0
```

```text
# output điển hình — khi đường A lỗi, track DOWN, route đổi
R1# show ip route static
S*   0.0.0.0/0 [10/0] via 198.51.100.1          ← đã chuyển sang WAN-B (AD 10)
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | *(A)* shutdown Gi0/1 → failover | ✅ | |
| 2 | *(A)* lỗi xa → **KHÔNG** failover | ❌ *(chứng minh giới hạn)* | |
| 3 | *(B)* IP SLA return code OK | ✅ | |
| 4 | *(B)* track reachability Up | ✅ | |
| 5 | *(B)* lỗi xa → track DOWN → failover | ✅ | |
| 6 | Thời gian chuyển ≈ frequency × threshold | ~vài giây | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — IP SLA đi nhầm đường ⭐

```cisco
! Xoá route ép probe đi đường A
R1(config)# no ip route 8.8.8.8 255.255.255.255 203.0.113.1
```

| | |
|---|---|
| Khi đường A lỗi, IP SLA probe đi đường nào? | |
| Track có DOWN không? Vì sao? | |
| Failover có xảy ra không — và điều đó đúng hay sai? | |
| Vì sao probe phải bị **ép** đi đúng đường cần giám sát? | |

### Lỗi 2 — Quên gắn `track` vào route

```cisco
R1(config)# no ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 1
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1        ! không track
```

| | |
|---|---|
| IP SLA và track vẫn chạy chứ? | |
| Khi đường A lỗi xa, route chính có bị gỡ không? | |
| Track "biết" đường chết nhưng route không đổi — vì sao? | |

### Lỗi 3 — AD backup thấp hơn hoặc bằng chính

```cisco
R1(config)# no ip route 0.0.0.0 0.0.0.0 198.51.100.1 10
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1        ! AD 1, bằng chính
```

| | |
|---|---|
| Giờ có mấy default route trong bảng? | |
| Traffic đi đường nào — hay chia cả hai *(ECMP)*? | |
| Vì sao backup phải có AD **cao hơn**? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Giải thích chuỗi **IP SLA → track → route** bằng lời. Mỗi thành phần làm gì?
2. Floating static vs IP SLA+track: nêu đúng một tình huống mỗi cái phù hợp.
3. Bạn muốn failover **và** cân bằng tải *(dùng cả 2 WAN khi bình thường)*. Cách tiếp cận?
4. IP SLA ping `8.8.8.8` — rủi ro gì nếu chính `8.8.8.8` *(không phải đường A)* có vấn đề?

<details>
<summary>Đáp án</summary>

**1.** Chuỗi ba tầng:

```text
IP SLA   = "cảm biến": chủ động ping 8.8.8.8 qua đường A mỗi 5s, trả OK/fail
   ↓
TRACK    = "công tắc": đọc kết quả IP SLA → trạng thái Up/Down
   ↓
ROUTE    = "hành động": route chính chỉ tồn tại khi track Up;
           track Down → route bị gỡ → floating backup (AD cao hơn) lên
```

Tách 3 tầng cho linh hoạt: một track có thể gắn nhiều route; một IP SLA nuôi nhiều track.

**2.**

| Cái | Phù hợp khi |
|---|---|
| **Floating static** | Lỗi gần như luôn là **đứt link trực tiếp** *(interface down)* — đơn giản, không tốn probe |
| **IP SLA + track** | Cần phát hiện **lỗi ở xa** *(ISP hỏng nhưng link mình vẫn up)* — gần như mọi dual-WAN thật |

**3.** Cân bằng tải + failover:
- **PBR (Policy-Based Routing)** chia traffic theo nguồn/dịch vụ ra 2 WAN, mỗi WAN có
  track riêng → đường nào chết thì PBR dồn sang đường còn lại.
- Hoặc 2 default route **ECMP** *(cùng AD)* mỗi cái có track → cân bằng khi cả hai Up,
  tự bỏ đường chết.
- Lưu ý NAT phải dùng **route-map theo interface** *(LAB 32)* để ra đúng IP.

**4.** Nếu `8.8.8.8` *(đích probe)* sập mà **đường A vẫn tốt** → IP SLA fail → track DOWN
→ failover **nhầm** *(đường A vẫn dùng được!)*. Giảm rủi ro: probe một **đích ổn định,
gần ISP-A** *(vd gateway/DNS của ISP-A)* thay vì một IP công cộng xa, hoặc probe **nhiều
đích** và chỉ failover khi tất cả fail. Chọn đích probe là quyết định thiết kế quan trọng.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Phần A — vì sao floating static mù với lỗi xa

Static route bị gỡ khỏi bảng **chỉ khi**: (a) interface next-hop **down**, hoặc
(b) không có route tới next-hop. Khi ISP-A hỏng ở xa mà **link Gi0/1 vẫn up**, R1 thấy
next-hop `203.0.113.1` vẫn "tới được" *(cùng subnet, link up)* → **giữ nguyên** route
chính → traffic tiếp tục đổ ra A → **hố đen**. Floating static không có cách nào biết
`8.8.8.8` không còn tới được qua A.

### Giải thích các lỗi BREAK

**Lỗi 1 — probe đi nhầm đường ⭐:** Không ép route cho `8.8.8.8` qua Gi0/1, probe có thể
theo default route hiện hành. Khi A lỗi, nếu probe lỡ đi qua B *(vẫn tới `8.8.8.8`)* →
track vẫn **Up** → **không failover** dù A đã chết. Phải `ip route 8.8.8.8/32 203.0.113.1`
để probe **luôn** đo đúng đường A.

**Lỗi 2 — quên gắn track:** IP SLA + track chạy và **biết** A chết *(track DOWN)*, nhưng
route chính không có `track 1` → nó **không liên kết** với track → route vẫn nằm đó →
không failover. Track chỉ có tác dụng khi **route tham chiếu nó**.

**Lỗi 3 — AD bằng nhau:** Hai default route cùng AD 1 → cả hai vào bảng → **ECMP** chia
tải. Không phải "chính/phụ" nữa. Backup **phải AD cao hơn** để chỉ xuất hiện khi chính
biến mất. AD thấp hơn hoặc bằng phá vỡ mô hình failover.

### Bảng tổng kết

| Thành phần | Vai trò | Lệnh verify |
|---|---|---|
| IP SLA | Thăm dò đích thật | `show ip sla statistics` |
| Track | Biến kết quả thành Up/Down | `show track` |
| Route + track | Gỡ route khi track Down | `show ip route static` |
| Floating static | Backup đơn giản, mù lỗi xa | `show ip route` |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Giới hạn floating static tôi tự chứng minh được chưa? ___
- Lỗi 1 (probe nhầm đường) — vì sao phải ép route cho đích probe? ___
- Chuỗi IP SLA→track→route tôi giải thích lại được chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
