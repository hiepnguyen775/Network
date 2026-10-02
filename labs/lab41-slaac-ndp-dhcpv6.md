# LAB 41 — SLAAC, NDP, DHCPv6

| | |
|---|---|
| **Phase** | 4 |
| **Lesson liên quan** | [Lesson 30 — SLAAC · NDP · ICMPv6 · DHCPv6](../04-ipv6/lesson-30-slaac-ndp-dhcpv6.md) |
| **Công cụ** | Cisco Packet Tracer + Wireshark/Simulation |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Cho PC tự nhận địa chỉ bằng **SLAAC** *(không server)*
- [ ] Bắt và đọc **RS / RA / NS / NA** — 4 gói NDP cốt lõi
- [ ] So sánh **3 chế độ** cấp địa chỉ: SLAAC / SLAAC+DHCPv6 stateless / DHCPv6 stateful
- [ ] Hiểu **M/O flag** trong RA quyết định client làm gì
- [ ] Tự gây & sửa 3 lỗi IPv6 autoconfig

## 2. Prerequisite

- [Lesson 30](../04-ipv6/lesson-30-slaac-ndp-dhcpv6.md) — SLAAC, NDP, DHCPv6
- [LAB 40](lab40-ipv6-addressing.md) — địa chỉ IPv6, solicited-node

---

## 3. Topology

```text
   PC1 ── SW1 ── R1 ── (gửi RA)
   PC2         DHCPv6 server (tuỳ chế độ)
```

| Thiết bị | Vai trò |
|---|---|
| R1 | Gửi RA, có thể làm DHCPv6 server |
| PC1, PC2 | Client IPv6 autoconfig |

## 4. Prefix

- LAN: `2001:db8:acad:10::/64`
- R1 Gi0/0: `2001:db8:acad:10::1/64`, `fe80::1`
- DNS IPv6: `2001:db8:acad:20::53`

---

## 5. Yêu cầu LAB

- [ ] PC nhận GUA bằng SLAAC, đọc được RA
- [ ] Chuyển lần lượt qua 3 chế độ, quan sát M/O flag
- [ ] Bắt đủ RS/RA/NS/NA trong Simulation
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — SLAAC thuần

```cisco
R1(config)# ipv6 unicast-routing
R1(config)# interface Gi0/0
R1(config-if)# ipv6 address 2001:db8:acad:10::1/64
R1(config-if)# ipv6 address fe80::1 link-local
R1(config-if)# no shutdown
! mặc định: router gửi RA với M=0 O=0 → client dùng SLAAC
```

Trên PC: IPv6 Configuration → **Automatic**.

> 🔴 **DỰ ĐOÁN:** PC sẽ tạo địa chỉ GUA bằng cách nào? Lấy prefix từ đâu, interface ID
> từ đâu? Nó có hỏi server nào không?

### Bước 2 — Bắt 4 gói NDP ⭐

Simulation mode, lọc ICMPv6, bật/tắt lại card PC:

| Gói | Từ → Đến | Mục đích |
|---|---|---|
| **RS** *(Router Solicitation)* | PC → `ff02::2` | "Router nào đây, cho tôi RA" |
| **RA** *(Router Advertisement)* | R1 → `ff02::1` | "Prefix là `...10::/64`, M=0 O=0" |
| **NS** *(Neighbor Solicitation)* | PC → solicited-node | "Ai giữ địa chỉ này?" *(DAD + thay ARP)* |
| **NA** *(Neighbor Advertisement)* | đích → PC | "Tôi giữ, MAC đây" |

> 🔑 **DAD (Duplicate Address Detection):** trước khi dùng địa chỉ vừa tạo, PC gửi NS
> hỏi "có ai dùng địa chỉ này chưa?". Không ai trả lời → an toàn dùng.

### Bước 3 — Ba chế độ, đọc M/O flag

```cisco
! ── Chế độ 2: SLAAC + DHCPv6 stateless (địa chỉ tự tạo, DNS từ DHCPv6) ──
R1(config-if)# ipv6 nd other-config-flag            ! O=1
R1(config)# ipv6 dhcp pool STATELESS
R1(config-dhcpv6)# dns-server 2001:db8:acad:20::53
R1(config-dhcpv6)# domain-name cty.local
R1(config)# interface Gi0/0
R1(config-if)# ipv6 dhcp server STATELESS

! ── Chế độ 3: DHCPv6 stateful (server cấp cả địa chỉ) ──
R1(config-if)# ipv6 nd managed-config-flag          ! M=1
R1(config-if)# ipv6 nd prefix default no-autoconfig  ! tắt SLAAC
R1(config)# ipv6 dhcp pool STATEFUL
R1(config-dhcpv6)# address prefix 2001:db8:acad:10::/64
R1(config-dhcpv6)# dns-server 2001:db8:acad:20::53
```

| Chế độ | M flag | O flag | Địa chỉ từ | DNS từ |
|---|:---:|:---:|---|---|
| SLAAC thuần | 0 | 0 | tự tạo *(RA prefix + EUI-64)* | RA *(RDNSS)* hoặc không |
| SLAAC + DHCPv6 stateless | 0 | 1 | tự tạo | **DHCPv6** |
| DHCPv6 stateful | 1 | 1 | **DHCPv6** | **DHCPv6** |

> 🔑 **M = Managed** *(địa chỉ từ DHCPv6)*, **O = Other** *(cấu hình khác như DNS từ
> DHCPv6)*. Client đọc 2 cờ này trong RA để quyết định hỏi DHCPv6 hay không.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
PC> ipv6config
   Link-local IPv6 Address . . . : FE80::2D0:BAFF:FE11:1111
   IPv6 Address. . . . . . . . . : 2001:DB8:ACAD:10:2D0:BAFF:FE11:1111
   Default Gateway . . . . . . . : FE80::1
```

> 🔑 Để ý gateway là **FE80::1 (link-local)**, KHÔNG phải GUA — client luôn dùng
> link-local của router làm default gateway.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 neighbors
IPv6 Address                    Age Link-layer Addr  State Interface
2001:DB8:ACAD:10:2D0:BAFF:FE11:1111  0 00d0.ba11.1111 REACH Gi0/0
FE80::2D0:BAFF:FE11:1111             0 00d0.ba11.1111 REACH Gi0/0
```

```text
# output điển hình — kiểm tra RA flags
R1# show ipv6 interface Gi0/0 | include config|advertis
  Hosts use stateless autoconfig for addresses.
  ND router advertisements are sent every 200 seconds
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | SLAAC: PC tự có GUA, không server | ✅ | |
| 2 | Bắt được đủ RS/RA/NS/NA | ✅ | |
| 3 | Gateway của PC là `fe80::1` | ✅ | |
| 4 | Chế độ 2: PC có DNS từ DHCPv6 | ✅ | |
| 5 | Chế độ 3: PC có địa chỉ từ DHCPv6 *(không EUI-64)* | ✅ | |
| 6 | `show ipv6 neighbors` thấy PC | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Router không gửi RA ⭐

```cisco
R1(config)# no ipv6 unicast-routing
! hoặc:  interface Gi0/0 → ipv6 nd ra suppress
```

| | |
|---|---|
| PC có tự nhận GUA bằng SLAAC không? | |
| PC gửi RS nhưng có RA trả lời không? | |
| PC còn link-local không? *(tự sinh không cần RA)* | |
| Vì sao "không RA = không SLAAC"? | |

### Lỗi 2 — M/O flag mâu thuẫn với cấu hình

```cisco
R1(config-if)# ipv6 nd managed-config-flag     ! M=1 (bảo client hỏi DHCPv6)
! nhưng KHÔNG cấu hình DHCPv6 server
```

| | |
|---|---|
| PC thấy M=1 → nó làm gì? | |
| Có server trả lời không? | |
| PC có nhận được địa chỉ không? | |
| Bài học: flag và dịch vụ phải **khớp** nhau? | |

### Lỗi 3 — Trùng địa chỉ (DAD phát hiện)

```text
Gán tĩnh cho PC2 đúng địa chỉ PC1 đang dùng → quan sát DAD
```

| | |
|---|---|
| PC2 có dùng được địa chỉ đó không? | |
| Gói NS của DAD trông thế nào? | |
| Ai trả lời khiến PC2 biết trùng? | |
| IPv4 có cơ chế tương đương không? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. So sánh NDP *(IPv6)* với ARP + ICMP redirect + router discovery *(IPv4)*.
   NDP gộp những chức năng gì?
2. Vì sao PC dùng **link-local của router** làm gateway thay vì GUA? Lợi ích?
3. Chọn chế độ nào *(3 chế độ)* cho: mạng khách đơn giản / data center cần kiểm soát IP?
4. SLAAC privacy extension *(temporary address)* giải quyết vấn đề gì?

<details>
<summary>Đáp án</summary>

**1.** NDP dùng ICMPv6 để **gộp nhiều chức năng** mà IPv4 phải dùng nhiều giao thức rời:

| Chức năng | IPv4 | IPv6 (NDP) |
|---|---|---|
| Phân giải MAC | ARP *(broadcast)* | NS/NA *(multicast solicited-node)* |
| Tìm router | ICMP router discovery / cấu hình tay | RS/RA |
| Phát hiện trùng IP | gratuitous ARP *(thô sơ)* | **DAD** *(chuẩn hoá)* |
| Redirect | ICMP redirect | NDP redirect |

NDP hiệu quả hơn: dùng **multicast** thay broadcast → chỉ máy liên quan xử lý.

**2.** Link-local **không đổi** dù prefix GUA thay đổi *(renumber)*. Nếu gateway là GUA
và ISP đổi prefix, mọi client phải cập nhật gateway. Dùng **fe80::1** → gateway **ổn định
vĩnh viễn**, renumber không ảnh hưởng định tuyến nội bộ. Đây là thiết kế có chủ ý của IPv6.

**3.**

| Mạng | Chế độ | Vì sao |
|---|---|---|
| Khách đơn giản | **SLAAC** *(+stateless cho DNS)* | Không cần server, tự chạy, nhẹ |
| Data center / cần log IP | **DHCPv6 stateful** | Kiểm soát chính xác IP nào cho ai, có lease/log để truy vết |

Stateful cho khả năng kiểm toán *(biết IP nào của máy nào, khi nào)* — quan trọng cho
bảo mật/tuân thủ. SLAAC khó truy vết hơn.

**4.** SLAAC thường tạo interface ID từ **EUI-64 (MAC)** → địa chỉ **tiết lộ MAC** và
**không đổi** → website có thể **theo dõi** thiết bị qua các mạng. Privacy extension tạo
interface ID **ngẫu nhiên, đổi định kỳ** *(temporary address)* dùng cho kết nối ra ngoài
→ chống theo dõi. Địa chỉ EUI-64 vẫn giữ để nhận kết nối vào.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### SLAAC hoạt động thế nào

```text
1. PC bật lên → tự tạo link-local fe80::EUI-64 → DAD kiểm tra
2. PC gửi RS tới ff02::2 (all-routers): "cho tôi thông tin mạng"
3. R1 trả RA tới ff02::1: "prefix = 2001:db8:acad:10::/64, M=0 O=0, tôi là gateway fe80::1"
4. PC ghép: prefix (từ RA) + interface ID (EUI-64 của chính nó) = GUA
5. PC chạy DAD cho GUA → không ai dùng → OK
→ PC có địa chỉ mà KHÔNG cần bất kỳ server nào
```

### Giải thích các lỗi BREAK

**Lỗi 1 — không RA ⭐:** SLAAC **phụ thuộc hoàn toàn** vào RA để biết prefix. Không RA →
PC không biết prefix GUA → chỉ có **link-local** *(tự sinh, không cần RA)* → ping được
trong link nhưng **không ra ngoài**. `no ipv6 unicast-routing` hoặc `ra suppress` đều
làm router ngừng gửi RA.

**Lỗi 2 — M/O mâu thuẫn:** M=1 bảo client "địa chỉ lấy từ DHCPv6". PC gửi DHCPv6 Solicit
nhưng **không server** → không ai trả lời → PC **không có GUA** *(và cũng không dùng
SLAAC vì đã bị bảo đừng)*. Flag và dịch vụ **phải khớp**: bật M thì phải có DHCPv6 server.

**Lỗi 3 — DAD:** PC2 gán tĩnh địa chỉ trùng → trước khi dùng, PC2 gửi **NS (DAD)** hỏi
"ai giữ địa chỉ này?". PC1 *(đang dùng)* trả **NA** "tôi giữ" → PC2 biết trùng → **từ chối
dùng**, báo lỗi duplicate. IPv4 chỉ có gratuitous ARP thô sơ; IPv6 chuẩn hoá DAD thành
bước bắt buộc.

### Bảng tổng kết

| Gói NDP | Vai trò |
|---|---|
| RS / RA | Tìm router + nhận prefix |
| NS / NA | Phân giải MAC + DAD |
| M flag | Địa chỉ từ DHCPv6 |
| O flag | DNS/config khác từ DHCPv6 |

</details>

---

## 📝 Ghi chú & bài học rút ra

- 4 gói NDP: RS/RA/NS/NA — tôi bắt được hết chưa? ___
- Lỗi 1 (không RA) — vì sao SLAAC chết mà link-local vẫn sống? ___
- M/O flag quyết định gì? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
