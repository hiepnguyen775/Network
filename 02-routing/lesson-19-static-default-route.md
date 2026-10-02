# LESSON 19 — Static Route · Default Route · Floating Static

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 18](./lesson-18-router-va-routing-table.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Viết static route đúng cú pháp, hiểu từng tham số
- [ ] Phân biệt trỏ **next-hop** và trỏ **exit-interface** — và hậu quả thực tế
- [ ] Cấu hình default route và giải thích vì sao nó luôn thua route cụ thể hơn
- [ ] Cấu hình **floating static** làm backup cho dual-WAN
- [ ] Biết khi nào nên dùng static, khi nào phải chuyển sang dynamic

## 2. Prerequisite

- Routing table, mã route, `[AD/metric]` *(Lesson 18)*
- Subnet mask, phép AND *(Lesson 02)*

---

## 3. Concept

### Cú pháp

```cisco
ip route <network> <mask> {<next-hop-ip> | <exit-interface>} [AD] [name <mô tả>]
```

```cisco
! Trỏ next-hop (phổ biến nhất)
R1(config)# ip route 10.0.2.0 255.255.255.0 10.0.12.2

! Trỏ exit-interface
R1(config)# ip route 10.0.2.0 255.255.255.0 Serial0/0/0

! Cả hai (fully specified) — an toàn nhất trên link multi-access
R1(config)# ip route 10.0.2.0 255.255.255.0 GigabitEthernet0/1 10.0.12.2

! Có AD tuỳ chỉnh + tên mô tả
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1 name ISP-CHINH
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 200 name ISP-BACKUP
```

### Ba kiểu trỏ — khác nhau thế nào

| Kiểu | Cú pháp | Router làm gì | Dùng khi |
|---|---|---|---|
| **Next-hop** | `ip route X Y 10.0.12.2` | Tra tiếp route tới `10.0.12.2` → **đệ quy** | ⭐ Mặc định nên dùng |
| **Exit-interface** | `ip route X Y Se0/0/0` | Gửi thẳng ra interface | Link **point-to-point** (serial) |
| **Fully specified** | `ip route X Y Gi0/1 10.0.12.2` | Cả hai — không đệ quy | Link Ethernet cần chắc chắn |

> ⚠️ **Bẫy lớn: trỏ exit-interface trên link Ethernet (multi-access).**
>
> Trên serial point-to-point, "gửi ra interface này" là rõ ràng — chỉ có một thiết bị đầu kia.
> Trên Ethernet, router **không biết gửi cho MAC nào** → nó phải **ARP cho MỌI địa chỉ đích**
> trong dải đó. Bảng ARP phình to, tốn CPU, và phụ thuộc vào **proxy ARP** của router đối diện.
>
> 👉 Trên Ethernet: dùng **next-hop** hoặc **fully specified**.

### Default route

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

`0.0.0.0/0` khớp **mọi** địa chỉ. Nhưng nó có **prefix ngắn nhất** (0 bit) →
theo **longest prefix match**, nó **luôn thua** mọi route cụ thể hơn.

```text
Gói tới 10.0.2.50:
  S*  0.0.0.0/0      → khớp (0 bit)
  O   10.0.2.0/24    → khớp (24 bit)  ← THẮNG, cụ thể hơn

Gói tới 8.8.8.8:
  S*  0.0.0.0/0      → khớp — chỉ có nó → DÙNG
```

> 💡 Vì vậy default route còn gọi là **gateway of last resort** —
> "đường cuối cùng khi không biết đi đâu".

### Floating static — backup tự động

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1          ! AD mặc định = 1  → ISP chính
ip route 0.0.0.0 0.0.0.0 198.51.100.1 200     ! AD = 200         → ISP backup
```

| Trạng thái | Routing table |
|---|---|
| Cả hai ISP sống | Chỉ route AD=1 vào bảng. Route AD=200 **nằm chờ**, không hiện |
| ISP chính chết | Route AD=1 bị gỡ → route AD=200 **tự động vào bảng** |
| ISP chính sống lại | Route AD=1 quay lại, đẩy AD=200 ra |

> 🔑 **"Floating" = trôi nổi** — route có AD cao nằm lơ lửng, chỉ hạ cánh vào bảng
> khi route tốt hơn biến mất. Đây là cách làm dual-WAN failover đơn giản nhất.

---

## 4. Why?

> **Khi nào static tốt hơn dynamic?**

| Tình huống | Vì sao static |
|---|---|
| Mạng nhỏ, ít thay đổi | Dynamic là overkill — thêm CPU, thêm thứ để hỏng |
| **Stub network** (chi nhánh chỉ có 1 đường ra) | Không có lựa chọn nào để tính — một default route là đủ |
| Default route ra Internet | ISP không chạy IGP với bạn |
| Cần **kiểm soát tuyệt đối** đường đi | Dynamic có thể tự đổi đường ngoài ý muốn |
| Bảo mật | Không quảng bá thông tin mạng ra ngoài |

> **Khi nào static không còn đủ?**

| Dấu hiệu | Hệ quả |
|---|---|
| Hơn ~10 router | Số route phải gõ tay tăng theo cấp số nhân |
| Topology có nhiều đường | Static **không tự tính lại** khi link chết |
| Mạng hay thay đổi | Mỗi thay đổi phải sửa tay nhiều thiết bị |

> 🔧 Static **không biết gì về trạng thái mạng ở xa**. Nó chỉ biến mất khi
> **interface local** down hoặc **next-hop không reachable**. Link đứt ở 3 hop nữa
> thì static vẫn nằm đó, và gói vẫn đi vào ngõ cụt.
>
> Đó là lý do có **IP SLA + track** (CCNP) và các routing protocol động.

---

## 5. How does it work? — recursive lookup

```text
ip route 10.0.2.0 255.255.255.0 10.0.12.2

Gói tới 10.0.2.50:
1. Tra bảng → khớp 10.0.2.0/24, next-hop = 10.0.12.2
2. Next-hop 10.0.12.2 ở interface nào? → TRA BẢNG LẦN NỮA (đệ quy)
3. Tìm thấy: C 10.0.12.0/30 is directly connected, Gi0/1
4. → Ra Gi0/1, ARP tìm MAC của 10.0.12.2
```

> ⚠️ Nếu **không tra được next-hop** (không có route tới `10.0.12.2`), static route
> sẽ **không vào bảng định tuyến** — dù bạn đã gõ lệnh và lệnh được chấp nhận.
> Kiểm tra: `show ip route 10.0.12.2`.

### Khi nào static route biến mất

| Nguyên nhân | Giải thích |
|---|---|
| Interface local down | Mất route connected → mất luôn next-hop |
| Next-hop không reachable | Recursive lookup thất bại |
| Có route AD thấp hơn tới cùng prefix | Bị đẩy ra khỏi bảng |

Static route **không** biến mất khi: link ở xa đứt, router đích chết, hay ACL chặn.

---

## 6. Packet Flow — dual-WAN failover

```text
          ┌─ Gi0/1 ──── ISP1 203.0.113.1  (AD 1)
   R1 ────┤
          └─ Gi0/2 ──── ISP2 198.51.100.1 (AD 200)
```

| Thời điểm | Routing table | Traffic đi đâu |
|---|---|---|
| Bình thường | `S* 0.0.0.0/0 [1/0] via 203.0.113.1` | ISP1 |
| Gi0/1 down | Route AD=1 bị gỡ → `S* 0.0.0.0/0 [200/0] via 198.51.100.1` | **ISP2** |
| Gi0/1 up lại | Route AD=1 quay lại | ISP1 |

> ⚠️ **Giới hạn quan trọng:** cơ chế này chỉ phát hiện được khi **interface local down**.
> Nếu cáp vẫn up nhưng ISP1 chết ở xa (router ISP hỏng, upstream đứt),
> route AD=1 **vẫn nằm trong bảng** → traffic vẫn đi vào ngõ cụt.
>
> Giải pháp thật: **IP SLA + track** — ping liên tục một IP bên ngoài, route chỉ sống
> khi ping còn thông. Học ở [`CCNP-Encor` Module 03](https://github.com/hiepnguyen775/CCNP-Encor).

---

## 7. Real-world Example

🏭 **Chi nhánh điển hình** — chỉ cần 2 dòng:

```cisco
! Trên router chi nhánh
ip route 0.0.0.0 0.0.0.0 10.255.0.1 name VE-TRU-SO

! Trên router trụ sở — route về chi nhánh
ip route 10.20.0.0 255.255.0.0 10.255.0.2 name CHI-NHANH-SG
```

Chi nhánh là **stub network** — chỉ có một đường ra. Chạy OSPF ở đây là thừa.

🏭 **Static route cho server DMZ**

```cisco
ip route 192.168.100.0 255.255.255.0 10.0.0.254 name DMZ
```

Kiểm soát tuyệt đối: DMZ không tham gia routing protocol, không quảng bá gì,
và chỉ đi được đường bạn chỉ định.

🏭 **Lỗi kinh điển: static route trỏ vào khoảng không**

```cisco
R1(config)# ip route 10.0.5.0 255.255.255.0 10.0.99.99    ! IP này không tồn tại
```

IOS **chấp nhận lệnh, không báo lỗi gì**. Route không vào bảng định tuyến.
Bạn cứ tưởng đã cấu hình xong.

> 🔧 Phản xạ: gõ xong static route, **luôn** `show ip route <network>` để xác nhận
> nó thật sự vào bảng.

---

## 8. Cisco CLI

```cisco
! ───── Static route cơ bản ─────
R1(config)# ip route 10.0.2.0 255.255.255.0 10.0.12.2

! ───── Default route ─────
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1

! ───── Floating static (backup) ─────
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 200

! ───── Fully specified (khuyên dùng trên Ethernet) ─────
R1(config)# ip route 10.0.2.0 255.255.255.0 GigabitEthernet0/1 10.0.12.2

! ───── Có tên mô tả ─────
R1(config)# ip route 10.0.2.0 255.255.255.0 10.0.12.2 name SANG-CHI-NHANH

! ───── Static route cho một host duy nhất ─────
R1(config)# ip route 10.0.2.50 255.255.255.255 10.0.12.2

! ───── Null route — chủ động vứt bỏ traffic ─────
R1(config)# ip route 192.168.0.0 255.255.0.0 Null0

! ───── Xoá ─────
R1(config)# no ip route 10.0.2.0 255.255.255.0 10.0.12.2

! ───── Kiểm tra ─────
R1# show ip route static
R1# show ip route 10.0.2.0
R1# show running-config | include ip route
```

| Tham số | Tác dụng | Lưu ý |
|---|---|---|
| `<next-hop>` | Gửi cho IP này | Phải **reachable**, nếu không route không vào bảng |
| `<exit-interface>` | Gửi ra cổng này | ⚠️ Chỉ dùng trên **point-to-point** |
| `[AD]` | Đặt AD tuỳ chỉnh | Cao hơn route chính → **floating static** |
| `name <text>` | Ghi chú | Rất nên dùng — `show run` dễ đọc hơn nhiều |
| `Null0` | Vứt bỏ gói | Chặn traffic, hoặc chống loop khi summarize |

> **Khác biệt platform:** NX-OS dùng `ip route <net>/<prefix> <next-hop>` (CIDR thay vì
> subnet mask), và static route nằm trong context VRF.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route static
      10.0.0.0/8 is variably subnetted, 5 subnets, 3 masks
S        10.0.2.0/24 [1/0] via 10.0.12.2
S        10.0.5.0/24 [1/0] via 10.0.12.2
S*    0.0.0.0/0 [1/0] via 203.0.113.1
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route 0.0.0.0
Routing entry for 0.0.0.0/0, supernet
  Known via "static", distance 1, metric 0, candidate default path
  Routing Descriptor Blocks:
  * 203.0.113.1
      Route metric is 0, traffic share count is 1
```

**Kiểm chứng floating static:**

```cisco
R1# show ip route | include 0.0.0.0
! Bình thường:  S* 0.0.0.0/0 [1/0] via 203.0.113.1
! Sau khi shutdown Gi0/1:
R1(config)# interface Gi0/1
R1(config-if)# shutdown
R1# show ip route | include 0.0.0.0
! Kết quả:      S* 0.0.0.0/0 [200/0] via 198.51.100.1    ← đã chuyển sang backup
```

> 🔑 Nhìn con số AD trong `[200/0]` là biết ngay đang chạy đường backup.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Gõ static route xong mà **không thấy** trong bảng | Next-hop không reachable | `show ip route <next-hop>` | Sửa next-hop, hoặc thêm route tới nó |
| Route có nhưng gói không đi | Thiếu route **chiều về** | `show ip route` ở đầu kia | Thêm route về |
| Bảng ARP phình to bất thường | Static trỏ **exit-interface** trên Ethernet | `show ip arp \| count`, `show run \| include ip route` | Đổi sang next-hop hoặc fully specified |
| Floating static không kích hoạt | AD không cao hơn route chính | `show run \| include ip route` | Đặt AD > AD của route chính |
| ISP chính chết mà traffic vẫn đi vào đó | Interface vẫn up — static không biết | `ping` qua ISP1 | Cần **IP SLA + track** |
| Default route không có tác dụng | Có route cụ thể hơn khớp trước | `show ip route <đích>` | Longest prefix match — đúng thiết kế |
| Mất route sau khi interface flap | Connected mất → static mất theo | `show logging` | Sửa lỗi vật lý |

---

## 11. LAB

🧪 **LAB 21 — Static, Default & Floating Static** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- 3 router nối chuỗi, mỗi router 1 LAN. Dùng **chỉ static route** cho mọi LAN thông nhau
- Thêm một "ISP" giả lập, cấu hình default route
- Thêm đường WAN thứ hai + **floating static**, chứng minh failover bằng
  `shutdown` interface chính và quan sát AD đổi từ `[1/0]` sang `[200/0]`
- **BREAK bắt buộc:** (1) static trỏ next-hop không tồn tại → route không vào bảng;
  (2) chỉ cấu hình route một chiều → ping một chiều; (3) floating static đặt AD = 1
  → cả hai cùng vào bảng, gây ECMP ngoài ý muốn

## 12. Challenge

1. Bạn gõ `ip route 10.0.5.0 255.255.255.0 10.0.99.99`. IOS nhận lệnh. Nhưng
   `show ip route` không thấy. Vì sao? Kiểm chứng thế nào?
2. Có 2 dòng: `ip route 0.0.0.0 0.0.0.0 1.1.1.1` và `ip route 0.0.0.0 0.0.0.0 2.2.2.2`
   (cùng AD mặc định). Chuyện gì xảy ra?
3. Vì sao trỏ exit-interface trên link Ethernet lại tệ, trong khi trên serial thì không sao?
4. Khi nào `ip route ... Null0` hữu ích?

<details>
<summary>Đáp án</summary>

**1.** Vì **recursive lookup thất bại** — router không có route nào tới `10.0.99.99`,
nên nó không biết gửi gói ra interface nào. Static route chỉ vào bảng khi next-hop
**reachable**.

Kiểm chứng: `show ip route 10.0.99.99` → không có kết quả.
Sửa: dùng next-hop đúng, hoặc thêm route tới `10.0.99.99` trước.

**2.** Cả hai cùng AD=1, cùng prefix `/0` → **cả hai vào bảng** → router làm
**ECMP (Equal-Cost Multi-Path)**, chia tải luân phiên giữa hai đường.

```text
S*    0.0.0.0/0 [1/0] via 1.1.1.1
                [1/0] via 2.2.2.2
```

Có thể là điều bạn muốn (load sharing), nhưng thường **không phải** — vì traffic
đi ra ngẫu nhiên hai hướng gây vấn đề với NAT và firewall stateful.
Muốn backup thì phải đặt AD khác nhau (floating static).

**3.**

| | Serial (point-to-point) | Ethernet (multi-access) |
|---|---|---|
| Có bao nhiêu thiết bị đầu kia | **Đúng một** | Có thể nhiều |
| "Gửi ra interface này" nghĩa là | Rõ ràng — chỉ một nơi để tới | **Mơ hồ** — gửi cho MAC nào? |
| Hệ quả | Không vấn đề | Router phải **ARP cho mọi IP đích** trong dải; bảng ARP phình to; phụ thuộc proxy ARP của router đối diện |

**4.** Ba trường hợp:

| Dùng để | Giải thích |
|---|---|
| **Chặn traffic** | Mọi gói tới dải đó bị vứt ngay tại router, không tốn băng thông đi tiếp |
| **Chống routing loop khi summarize** | Quảng bá `10.0.0.0/16` nhưng chỉ dùng `10.0.1.0/24` → thêm `ip route 10.0.0.0 255.255.0.0 Null0` để gói tới phần chưa dùng bị vứt thay vì chạy vòng |
| **Remote-triggered blackhole** | Kỹ thuật chống DDoS — đẩy traffic tấn công vào Null0 |

Null0 là interface ảo "thùng rác" — vứt gói mà **không tốn CPU**.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Cú pháp `ip route` · AD mặc định của static · `0.0.0.0/0` là gì | ⬜ |
| **L2** Explain | Giải thích floating static và vì sao nó không phát hiện được lỗi ở xa | ⬜ |
| **L3** Configure | 3 router + static đầy đủ + default + floating static | ⬜ |
| **L4** Troubleshoot | Static route không vào bảng → tìm ra next-hop không reachable | ⬜ |
| **L5** Design | Thiết kế routing cho 1 trụ sở + 3 chi nhánh dùng static | ⬜ |

## 14. Summary

**Key concepts**

- `ip route <net> <mask> <next-hop|interface> [AD] [name X]`
- **Next-hop** ⭐ mặc định · **exit-interface** chỉ cho point-to-point ·
  **fully specified** an toàn nhất trên Ethernet
- Default route `0.0.0.0/0` = gateway of last resort, **luôn thua** route cụ thể hơn
- ⭐ **Floating static** = AD cao hơn → chỉ vào bảng khi route chính biến mất
- Static route **không vào bảng** nếu next-hop không reachable
- ⚠️ Static chỉ biết **interface local down** — không biết lỗi ở xa → cần IP SLA + track
- `Null0` để vứt traffic, chống loop khi summarize

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip route <net> <mask> <next-hop>` | Static cơ bản |
| `ip route 0.0.0.0 0.0.0.0 <nh>` | Default route |
| `ip route 0.0.0.0 0.0.0.0 <nh> 200` | Floating static backup |
| `show ip route static` | Xem route tĩnh |
| `show ip route <network>` | **Luôn kiểm tra sau khi gõ** |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Next-hop không tồn tại | Route không vào bảng, **IOS không báo lỗi** |
| Chỉ cấu hình route một chiều | Ping một chiều |
| Exit-interface trên Ethernet | Bảng ARP phình to, phụ thuộc proxy ARP |
| Floating static quên đặt AD | Cả hai vào bảng → ECMP ngoài ý muốn |
| Tin floating static phát hiện được mọi sự cố | Chỉ biết interface local down |
| Quên `name` | 30 dòng `ip route` không ai đọc nổi |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 21 với đủ 3 lỗi BREAK.
2. Cấu hình floating static, `shutdown` interface chính, chạy `show ip route | include 0.0.0.0`
   trước và sau — ghi lại con số AC thay đổi.
3. Thử `ip route 10.9.9.0 255.255.255.0 1.2.3.4` (next-hop không tồn tại) rồi
   `show ip route 10.9.9.0` — xác nhận nó không vào bảng.

```markdown
- [YYYY-MM-DD] Lesson 19 — Static & Default Route: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Cú pháp, floating static, default route, longest prefix match |
| 🔧 **Engineer** | Luôn `name`; next-hop thay vì exit-interface trên Ethernet; verify sau khi gõ |
| 🏭 **Production** | Static không biết lỗi ở xa → dual-WAN thật cần IP SLA + track; Null0 chống loop |

### 🔗 Liên kết

- ⬅️ [Lesson 18 — Router & Routing Table](./lesson-18-router-va-routing-table.md)
- ➡️ [Lesson 20 — AD, Metric, Longest Prefix Match](./lesson-20-ad-metric-longest-prefix.md)
