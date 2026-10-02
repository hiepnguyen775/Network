# LAB 21 — Static · Default · Floating Static

| | |
|---|---|
| **Phase** | 2 |
| **Lesson liên quan** | [Lesson 19 — Static & Default Route](../02-routing/lesson-19-static-default-route.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Cấu hình static route **hai chiều** cho 3 router nối chuỗi
- [ ] Cấu hình default route ra "Internet" và hiểu vì sao nó luôn thua route cụ thể
- [ ] Cấu hình **floating static** và chứng minh failover bằng số liệu
- [ ] Chứng minh static route **không vào bảng** nếu next-hop không reachable
- [ ] Tự tìm ra lỗi "ping một chiều"

## 2. Prerequisite

- [LAB 20](./lab20-routing-table-co-ban.md) — đã làm xong
- [Lesson 19](../02-routing/lesson-19-static-default-route.md) — cú pháp, AD, floating static

---

## 3. Topology

```text
                              ┌─── ISP1 ───┐  203.0.113.1
   PC-A          R1 ══════ R2 ┤            │
10.1.1.10/24     │        │   └─── ISP2 ───┘  198.51.100.1
                 │        │
                 │        └──────── R3 ──── PC-C
                 │                           10.3.3.10/24
          10.0.12.0/30    10.0.23.0/30
```

Chi tiết link:

```text
R1 Gi0/1 (10.0.12.1/30) ──── (10.0.12.2/30) Gi0/1 R2
R2 Gi0/2 (10.0.23.1/30) ──── (10.0.23.2/30) Gi0/1 R3
R2 Gi0/3 (203.0.113.2/30)  ──── ISP1 (203.0.113.1)
R2 Gi0/4 (198.51.100.2/30) ──── ISP2 (198.51.100.1)
```

> 💡 Trong Packet Tracer, dùng **2 router phụ** làm ISP1/ISP2, mỗi con có một loopback
> `8.8.8.8/32` và `1.1.1.1/32` để đóng vai "Internet".

## 4. IP Addressing Table

| Device | Interface | IP | Mask |
|---|---|---|---|
| R1 | Gi0/0 *(LAN-A)* | `10.1.1.1` | `/24` |
| R1 | Gi0/1 *(tới R2)* | `10.0.12.1` | `/30` |
| R2 | Gi0/1 *(tới R1)* | `10.0.12.2` | `/30` |
| R2 | Gi0/2 *(tới R3)* | `10.0.23.1` | `/30` |
| R2 | Gi0/3 *(tới ISP1)* | `203.0.113.2` | `/30` |
| R2 | Gi0/4 *(tới ISP2)* | `198.51.100.2` | `/30` |
| R3 | Gi0/1 *(tới R2)* | `10.0.23.2` | `/30` |
| R3 | Gi0/0 *(LAN-C)* | `10.3.3.1` | `/24` |
| ISP1 | Gi0/0 · Lo0 | `203.0.113.1/30` · `8.8.8.8/32` | |
| ISP2 | Gi0/0 · Lo0 | `198.51.100.1/30` · `1.1.1.1/32` | |
| PC-A | Fa0 | `10.1.1.10/24`, GW `10.1.1.1` | |
| PC-C | Fa0 | `10.3.3.10/24`, GW `10.3.3.1` | |

---

## 5. Yêu cầu LAB

- [ ] PC-A ping được PC-C *(qua 2 router, static route hai chiều)*
- [ ] PC-A ping được `8.8.8.8` *(qua default route + ISP1)*
- [ ] `shutdown` Gi0/3 trên R2 → traffic **tự chuyển** sang ISP2
- [ ] `show ip route` hiển thị AD đổi từ `[1/0]` sang `[200/0]`
- [ ] Hoàn thành mục **8. BREAK** với đủ 4 lỗi

---

## 6. Step-by-step

### Bước 1 — Static route cho LAN

> 🔴 **Nguyên tắc: mỗi route phải có cặp đôi chiều ngược lại.** Viết ra giấy trước.

| Router | Cần route tới mạng nào | Next-hop |
|---|---|---|
| R1 | `10.3.3.0/24` | `10.0.12.2` *(R2)* |
| R2 | `10.1.1.0/24` | `10.0.12.1` *(R1)* |
| R2 | `10.3.3.0/24` | `10.0.23.2` *(R3)* |
| R3 | `10.1.1.0/24` | `10.0.23.1` *(R2)* |

```cisco
! ───── R1 ─────
ip route 10.3.3.0 255.255.255.0 10.0.12.2 name TOI-LAN-C

! ───── R2 ─────
ip route 10.1.1.0 255.255.255.0 10.0.12.1 name TOI-LAN-A
ip route 10.3.3.0 255.255.255.0 10.0.23.2 name TOI-LAN-C

! ───── R3 ─────
ip route 10.1.1.0 255.255.255.0 10.0.23.1 name TOI-LAN-A
```

> 🔧 **Luôn gõ `show ip route <network>` sau mỗi dòng** để xác nhận route thật sự vào bảng.

### Bước 2 — Default route ra Internet

```cisco
! ───── R2 — router biên ─────
ip route 0.0.0.0 0.0.0.0 203.0.113.1 name ISP1-CHINH

! ───── R1 và R3 — trỏ về R2 ─────
R1(config)# ip route 0.0.0.0 0.0.0.0 10.0.12.2 name RA-INTERNET
R3(config)# ip route 0.0.0.0 0.0.0.0 10.0.23.1 name RA-INTERNET
```

Kiểm chứng: PC-A ping `8.8.8.8` → phải được.

### Bước 3 — Floating static

```cisco
R2(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 200 name ISP2-BACKUP
```

> 🔴 **Dự đoán trước:** sau khi gõ dòng này, `show ip route | include 0.0.0.0`
> hiện **mấy dòng**? Viết ra rồi mới kiểm tra.

### Bước 4 — Đo failover

```text
1. Từ PC-A: ping -t 8.8.8.8
2. Trên R2: shutdown Gi0/3 (ISP1)
3. ĐẾM số gói mất trước khi ping chạy lại
4. Ghi lại
```

| Sự kiện | Số gói mất | `show ip route \| include 0.0.0.0` |
|---|:---:|---|
| Bình thường | — | |
| Sau khi shutdown Gi0/3 | | |
| Sau khi `no shutdown` Gi0/3 | | |

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R2# show ip route static
      10.0.0.0/8 is variably subnetted, 6 subnets, 2 masks
S        10.1.1.0/24 [1/0] via 10.0.12.1
S        10.3.3.0/24 [1/0] via 10.0.23.2
S*    0.0.0.0/0 [1/0] via 203.0.113.1
```

```text
# output điển hình — SAU KHI shutdown Gi0/3
R2# show ip route | include 0.0.0.0
S*    0.0.0.0/0 [200/0] via 198.51.100.1
```

> 🔑 Con số **`[200/0]`** là bằng chứng đang chạy đường backup.

**Bảng kiểm chứng:**

| Từ | Tới | Mong đợi | Thực tế |
|---|---|---|---|
| PC-A | PC-C | ✅ | |
| PC-C | PC-A | ✅ | |
| PC-A | `8.8.8.8` | ✅ | |
| PC-A | `1.1.1.1` | ❓ *(chỉ được khi đang chạy ISP2)* | |
| `tracert` PC-A → PC-C | 2 hop | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Next-hop không tồn tại

```cisco
R1(config)# ip route 10.5.5.0 255.255.255.0 10.0.99.99
```

| | |
|---|---|
| IOS có nhận lệnh không? | |
| `show ip route 10.5.5.0` hiện gì? | |
| `show running-config \| include ip route` có thấy dòng đó không? | |
| Giải thích: vì sao lệnh được nhận mà route không vào bảng | |

> 🔑 Đây là bẫy nguy hiểm: **cấu hình có, route không có, không báo lỗi gì**.

### Lỗi 2 — Chỉ cấu hình route một chiều

```cisco
R3(config)# no ip route 10.1.1.0 255.255.255.0 10.0.23.1
```

| | |
|---|---|
| PC-A ping PC-C: kết quả? | |
| PC-C ping PC-A: kết quả? | |
| Trên R2, `debug ip icmp` thấy gì? | |
| Lệnh nào phát hiện nhanh nhất? | |

### Lỗi 3 — Floating static đặt AD = 1

```cisco
R2(config)# no ip route 0.0.0.0 0.0.0.0 198.51.100.1 200
R2(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1
```

| | |
|---|---|
| `show ip route \| include 0.0.0.0` hiện mấy dòng? | |
| Hiện tượng này gọi là gì? | |
| Vì sao nó **không phải** điều bạn muốn ở đây? | |

### Lỗi 4 — Giới hạn của floating static ⭐

> Đây là lỗi quan trọng nhất của lab — nó chuẩn bị cho Lesson 39.

```cisco
! GIỮ Gi0/3 trên R2 ở trạng thái UP
! Thay vào đó, shutdown interface PHÍA ISP1
ISP1(config)# interface GigabitEthernet0/0
ISP1(config-if)# shutdown
```

| | |
|---|---|
| Interface Gi0/3 trên R2 còn `up/up` không? | |
| `show ip route \| include 0.0.0.0` hiện gì? | |
| Route có chuyển sang ISP2 không? | |
| PC-A ping `8.8.8.8` còn được không? | |
| **Kết luận về giới hạn của floating static** | |

> ⚠️ Trong Packet Tracer, shutdown một đầu có thể làm đầu kia cũng down.
> Nếu vậy, mô phỏng bằng cách **shutdown loopback `8.8.8.8` trên ISP1** —
> link vẫn up nhưng đích không còn reachable.

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Trên R1, thêm `ip route 10.3.3.0 255.255.255.0 GigabitEthernet0/1` *(exit-interface)*
   thay vì next-hop. Có chạy không? Có vấn đề gì tiềm ẩn?
2. Thêm `ip route 10.0.0.0 255.0.0.0 Null0` trên R2. Gói tới `10.9.9.9` đi đâu?
   Gói tới `10.1.1.10` đi đâu?
3. R2 có cả `S 10.3.3.0/24 via 10.0.23.2` và `S* 0.0.0.0/0 via 203.0.113.1`.
   Gói tới `10.3.3.50` đi đường nào? Vì sao?
4. Muốn traffic tới `8.8.8.8` đi ISP1 nhưng traffic tới `1.1.1.1` đi ISP2.
   Viết lệnh.

<details>
<summary>Đáp án</summary>

**1.** **Chạy được**, nhưng có vấn đề tiềm ẩn trên link **Ethernet**:

```text
Trỏ exit-interface trên link multi-access (Ethernet):
→ Router KHÔNG biết gửi cho MAC nào
→ Phải ARP cho MỌI địa chỉ đích trong 10.3.3.0/24
→ Bảng ARP phình to
→ Phụ thuộc PROXY ARP của R2 (nếu R2 tắt proxy ARP thì hỏng)
```

Trên link **serial point-to-point** thì không sao *(chỉ có một thiết bị đầu kia)*.

Cách an toàn trên Ethernet: dùng **next-hop**, hoặc **fully specified**:

```cisco
ip route 10.3.3.0 255.255.255.0 GigabitEthernet0/1 10.0.12.2
```

**2.**

| Gói tới | Route khớp | Đi đâu |
|---|---|---|
| `10.9.9.9` | `S 10.0.0.0/8 → Null0` *(prefix 8)* và `S* 0.0.0.0/0` *(prefix 0)* | **Null0** → **bị vứt bỏ** |
| `10.1.1.10` | `S 10.0.0.0/8 → Null0` và **`S 10.1.1.0/24`** | **`10.1.1.0/24`** → về R1 ✅ |

👉 Longest prefix match: `/24` thắng `/8`. Null0 chỉ bắt những phần của `10.0.0.0/8`
**chưa có route cụ thể hơn** — đây chính là kỹ thuật chống loop khi summarize.

**3.** Gói đi tới `10.3.3.50` qua **`S 10.3.3.0/24 via 10.0.23.2`**.

Lý do: **longest prefix match**. Route `/24` khớp 24 bit, default route `/0` khớp 0 bit.
Prefix dài hơn **luôn thắng**, bất kể AD *(ở đây cả hai đều AD 1)*.

Default route chỉ được dùng khi **không có route nào cụ thể hơn** khớp.

**4.** Dùng static route cho từng host `/32`:

```cisco
R2(config)# ip route 8.8.8.8 255.255.255.255 203.0.113.1
R2(config)# ip route 1.1.1.1 255.255.255.255 198.51.100.1
R2(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

Hai route `/32` có prefix dài nhất → luôn thắng default route.
Mọi đích khác vẫn đi ISP1 qua default route.

*(Cách linh hoạt hơn cho traffic theo nguồn/ứng dụng là **PBR — Policy-Based Routing**,
học ở CCNP.)*

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Cấu hình đầy đủ

```cisco
! ══════════ R1 ══════════
ip route 10.3.3.0 255.255.255.0 10.0.12.2 name TOI-LAN-C
ip route 0.0.0.0 0.0.0.0 10.0.12.2 name RA-INTERNET

! ══════════ R2 ══════════
ip route 10.1.1.0 255.255.255.0 10.0.12.1 name TOI-LAN-A
ip route 10.3.3.0 255.255.255.0 10.0.23.2 name TOI-LAN-C
ip route 0.0.0.0 0.0.0.0 203.0.113.1 name ISP1-CHINH
ip route 0.0.0.0 0.0.0.0 198.51.100.1 200 name ISP2-BACKUP

! ══════════ R3 ══════════
ip route 10.1.1.0 255.255.255.0 10.0.23.1 name TOI-LAN-A
ip route 0.0.0.0 0.0.0.0 10.0.23.1 name RA-INTERNET
```

### Bước 3 — dự đoán đúng

`show ip route | include 0.0.0.0` hiện **đúng MỘT dòng**:

```text
S*    0.0.0.0/0 [1/0] via 203.0.113.1
```

Route AD 200 **không hiện** — nó "trôi nổi" ngoài bảng, chờ route AD 1 biến mất.

### Bước 4 — kết quả failover tham khảo

| Sự kiện | Số gói mất | Routing table |
|---|:---:|---|
| Bình thường | 0 | `[1/0] via 203.0.113.1` |
| Shutdown Gi0/3 | **1–3** | `[200/0] via 198.51.100.1` |
| `no shutdown` Gi0/3 | 0–1 | `[1/0] via 203.0.113.1` |

Chuyển rất nhanh vì interface down được phát hiện ngay lập tức.

### Giải thích các lỗi BREAK

| # | Quan sát | Giải thích |
|:---:|---|---|
| 1 | Lệnh được nhận, `show run` **có** dòng đó, nhưng `show ip route 10.5.5.0` **trống** | **Recursive lookup thất bại** — R1 không có route tới `10.0.99.99` nên không biết gửi ra interface nào |
| 2 | PC-A ping PC-C: **"Request timed out"**<br>PC-C ping PC-A: **"Request timed out"** | Gói **đi được** tới PC-C, nhưng R3 không có route về `10.1.1.0/24` → reply bị drop |
| 3 | Hiện **2 dòng** cùng prefix `0.0.0.0/0` | **ECMP** — router chia tải luân phiên 2 đường. Không phải điều bạn muốn: traffic ra Internet đi ngẫu nhiên 2 hướng gây vấn đề với NAT và firewall stateful |
| 4 | Gi0/3 **vẫn up/up**, route **vẫn `[1/0] via 203.0.113.1`**, ping `8.8.8.8` **fail** | ⭐ **Floating static chỉ biết interface LOCAL down** — nó mù hoàn toàn với lỗi ở xa |

**Chi tiết lỗi 2 — lệnh phát hiện nhanh nhất:**

```cisco
R3# show ip route 10.1.1.0
% Network not in table          ← ra ngay nguyên nhân
```

Hoặc trên R2:

```cisco
R2# debug ip icmp
ICMP: echo reply sent, src 10.3.3.10, dst 10.1.1.10   ← có reply
! nhưng không bao giờ tới đích
```

**Chi tiết lỗi 4 — bài học quan trọng nhất:**

```text
Floating static phát hiện được:
  ✅ Cáp bị rút (interface down)
  ✅ Next-hop không reachable (recursive lookup fail)

Floating static KHÔNG phát hiện được:
  ❌ Router ISP chết nhưng cáp vẫn up
  ❌ Upstream của ISP đứt
  ❌ ISP hoạt động nhưng mất gói 50%
```

→ Đây chính là lý do tồn tại của **IP SLA + track**, học ở
[Lesson 39](../07-wan-vpn/lesson-39-wan-concepts.md) — và LAB 70 của phase đó.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Số gói mất khi failover: ___
- Lỗi 4 chứng minh cho tôi điều gì về floating static? ___
- Lỗi khó tìm nhất: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
