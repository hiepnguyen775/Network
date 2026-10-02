# LAB 42 — IPv6 routing & OSPFv3

| | |
|---|---|
| **Phase** | 4 |
| **Lesson liên quan** | [Lesson 31 — IPv6 routing · OSPFv3 · dual-stack](../04-ipv6/lesson-31-ipv6-routing-ospfv3.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Cấu hình **static route IPv6** *(gồm default `::/0`)*
- [ ] Dựng **OSPFv3** 3 router, kiểm tra neighbor và bảng định tuyến
- [ ] Hiểu OSPFv3 dùng **link-local** làm next-hop và **router-id IPv4-format**
- [ ] Chạy **dual-stack** *(IPv4 + IPv6 song song)* trên cùng interface
- [ ] Tự gây & sửa 3 lỗi routing IPv6

## 2. Prerequisite

- [Lesson 31](../04-ipv6/lesson-31-ipv6-routing-ospfv3.md) — static IPv6, OSPFv3, dual-stack
- [LAB 23](lab23-ospf-single-area.md) — OSPFv2 *(so sánh)*
- [LAB 40](lab40-ipv6-addressing.md), [LAB 41](lab41-slaac-ndp-dhcpv6.md)

---

## 3. Topology

```text
   PC1 ── R1 ═══ R2 ═══ R3 ── PC3
          (OSPFv3 area 0, dual-stack)
```

| Link | IPv6 | IPv4 *(dual-stack)* |
|---|---|---|
| R1-R2 | `2001:db8:12::/64` | `10.0.12.0/30` |
| R2-R3 | `2001:db8:23::/64` | `10.0.23.0/30` |
| R1 LAN | `2001:db8:1::/64` | `10.0.1.0/24` |
| R3 LAN | `2001:db8:3::/64` | `10.0.3.0/24` |

## 4. IP Addressing Table

| Device | Interface | IPv6 | IPv4 |
|---|---|---|---|
| R1 | Gi0/0 *(LAN)* | `2001:db8:1::1/64` | `10.0.1.1/24` |
| R1 | Gi0/1 *(→R2)* | `2001:db8:12::1/64` | `10.0.12.1/30` |
| R2 | Gi0/1 *(→R1)* | `2001:db8:12::2/64` | `10.0.12.2/30` |
| R2 | Gi0/2 *(→R3)* | `2001:db8:23::2/64` | `10.0.23.2/30` |
| R3 | Gi0/2 *(→R2)* | `2001:db8:23::3/64` | `10.0.23.3/30` |
| R3 | Gi0/0 *(LAN)* | `2001:db8:3::1/64` | `10.0.3.1/24` |

---

## 5. Yêu cầu LAB

- [ ] Phần A: static route IPv6 cho R1↔R3 thông nhau
- [ ] Phần B: thay bằng OSPFv3, neighbor FULL, PC1 ping PC3 qua IPv6
- [ ] Dual-stack: ping được cả IPv4 lẫn IPv6
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Phần A — Static route IPv6

```cisco
R1(config)# ipv6 unicast-routing
! R1 cần tới LAN của R3 (2001:db8:3::/64) qua R2
R1(config)# ipv6 route 2001:db8:3::/64 2001:db8:12::2
! hoặc default:
R1(config)# ipv6 route ::/0 2001:db8:12::2

R3(config)# ipv6 route 2001:db8:1::/64 2001:db8:23::2
R2(config)# ! R2 connected cả hai, không cần static
```

> 🔴 **DỰ ĐOÁN:** với static route, R2 có cần route gì để chuyển tiếp giữa R1-LAN và
> R3-LAN không? Vì sao?

### Phần B — OSPFv3 ⭐

```cisco
! ══ R1 ══
R1(config)# no ipv6 route ::/0 2001:db8:12::2     ! gỡ static
R1(config)# ipv6 router ospf 1
R1(config-rtr)# router-id 1.1.1.1                 ! BẮT BUỘC: định dạng IPv4
R1(config)# interface Gi0/0
R1(config-if)# ipv6 ospf 1 area 0
R1(config)# interface Gi0/1
R1(config-if)# ipv6 ospf 1 area 0

! ══ R2 ══
R2(config)# ipv6 router ospf 1
R2(config-rtr)# router-id 2.2.2.2
R2(config)# interface Gi0/1
R2(config-if)# ipv6 ospf 1 area 0
R2(config)# interface Gi0/2
R2(config-if)# ipv6 ospf 1 area 0

! ══ R3: tương tự, router-id 3.3.3.3, bật OSPFv3 trên Gi0/2 và Gi0/0 ══
```

> 🔑 Khác OSPFv2: **không** `network` statement — bật OSPFv3 **trực tiếp trên
> interface** bằng `ipv6 ospf 1 area 0`. Và **router-id phải đặt tay** *(định dạng
> IPv4)* vì OSPFv3 chạy trên IPv6 không có IP v4 để tự chọn.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 ospf neighbor
Neighbor ID     Pri   State      Dead Time   Interface ID    Interface
2.2.2.2           1   FULL/DR    00:00:34    5               GigabitEthernet0/1
```

```text
# output điển hình — next-hop là LINK-LOCAL, không phải GUA
R1# show ipv6 route ospf
O   2001:DB8:3::/64 [110/2]
     via FE80::2, GigabitEthernet0/1          ← next-hop fe80 (link-local của R2)
O   2001:DB8:23::/64 [110/2]
     via FE80::2, GigabitEthernet0/1
```

```text
# output điển hình — dual-stack: cả hai routing table song song
R1# show ipv6 route summary
R1# show ip route ospf
O    10.0.3.0/24 [110/2] via 10.0.12.2, GigabitEthernet0/1
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | *(A)* static: PC1 ping PC3 IPv6 | ✅ | |
| 2 | *(B)* OSPFv3 neighbor R1-R2, R2-R3 FULL | ✅ | |
| 3 | Route OSPF có next-hop **fe80::** | ✅ | |
| 4 | PC1 ping PC3 qua IPv6 | ✅ | |
| 5 | PC1 ping PC3 qua IPv4 *(dual-stack)* | ✅ | |
| 6 | router-id đúng `X.X.X.X` | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Quên router-id trên OSPFv3 ⭐

```cisco
R2(config)# ipv6 router ospf 1
R2(config-rtr)# no router-id 2.2.2.2
! R2 không có IPv4 nào trên interface
```

| | |
|---|---|
| OSPFv3 process có khởi động được không? | |
| Thông báo lỗi là gì? | |
| Vì sao OSPFv3 **không tự** chọn được router-id như OSPFv2 có thể? | |
| router-id có bắt buộc định dạng IPv4 không? | |

### Lỗi 2 — Thiếu `ipv6 unicast-routing`

```cisco
R2(config)# no ipv6 unicast-routing
```

| | |
|---|---|
| OSPFv3 neighbor còn FULL không? | |
| R2 có **forward** gói IPv6 giữa R1 và R3 không? | |
| Phân biệt: OSPFv3 chạy ≠ router forward được? | |

### Lỗi 3 — Bật OSPFv3 thiếu một interface

```cisco
R2(config)# interface Gi0/2
R2(config-if)# no ipv6 ospf 1 area 0
```

| | |
|---|---|
| R1 có học được route tới `2001:db8:3::/64` không? | |
| `show ipv6 ospf neighbor` trên R2 còn thấy R3 không? | |
| So với OSPFv2: thiếu `network` statement gây lỗi tương tự thế nào? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Liệt kê **3 khác biệt** chính giữa cấu hình OSPFv2 và OSPFv3.
2. Vì sao OSPFv3 dùng **link-local** làm next-hop? Điều gì xảy ra nếu link-local thiếu?
3. Dual-stack: ưu nhược so với chỉ IPv6? Vì sao giai đoạn chuyển đổi cần nó?
4. PC1 ping PC3 IPv6 fail nhưng IPv4 OK. OSPFv3 neighbor FULL. Nêu 3 chỗ cần kiểm tra.

<details>
<summary>Đáp án</summary>

**1.** Ba khác biệt OSPFv2 vs OSPFv3:

| | OSPFv2 | OSPFv3 |
|---|---|---|
| Bật trên interface | `network` statement dưới process | `ipv6 ospf 1 area 0` **trên interface** |
| Router-id | tự chọn từ IP cao nhất *(hoặc đặt tay)* | **bắt buộc đặt tay** *(không có IPv4)* |
| Next-hop | IP interface hàng xóm | **link-local** của hàng xóm |
| Vận chuyển | trực tiếp IPv4 | trên IPv6, dùng link-local |

**2.** OSPFv3 dùng link-local vì nó **luôn tồn tại** và **không đổi** khi prefix GUA
renumber → quan hệ neighbor ổn định. Thiếu link-local *(gần như không xảy ra vì IOS tự
sinh)* → OSPFv3 **không hình thành neighbor** được, vì hello và next-hop đều dựa vào nó.

**3.** Dual-stack:

| | Ưu | Nhược |
|---|---|---|
| Dual-stack | Tương thích **cả** dịch vụ IPv4 lẫn IPv6; chuyển đổi mượt | **Gấp đôi** việc quản lý *(2 bảng route, 2 ACL, 2 bộ firewall)* |

Giai đoạn chuyển đổi cần dual-stack vì **Internet chưa toàn IPv6** — nhiều dịch vụ vẫn
chỉ IPv4. Chạy song song để truy cập được cả hai, dần tắt IPv4 khi mọi thứ hỗ trợ IPv6.

**4.** PC1→PC3 IPv6 fail, IPv4 OK, neighbor FULL:

```text
1. Địa chỉ IPv6 của PC: ipv6config — PC có GUA + gateway fe80::1 đúng chưa?
   (dual-stack có thể IPv4 OK nhưng PC chưa nhận IPv6)
2. Route IPv6 trên router: show ipv6 route — R1 có route tới 2001:db8:3::/64?
   Nếu interface LAN của R3 CHƯA bật ipv6 ospf → route LAN không quảng bá
   (neighbor vẫn FULL vì link R2-R3 OK, nhưng LAN không vào OSPF)
3. Gateway/forwarding: ipv6 unicast-routing bật trên MỌI router?
   firewall/ACL IPv6 chặn? PC3 có trả lời ICMPv6 echo?
```

Điểm bẫy hay gặp: **neighbor FULL nhưng LAN interface chưa cho vào OSPFv3** → router
thấy nhau nhưng không quảng bá mạng LAN. Đây chính là Lỗi 3.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Phần A — vì sao R2 không cần static

R2 **connected trực tiếp** cả `2001:db8:12::/64` và `2001:db8:23::/64`, và cả hai LAN
`2001:db8:1::/64`... khoan — R2 **không** connected tới LAN của R1/R3. Nhưng với static,
R1 trỏ `::/0` về R2, R3 trỏ về R2. R2 cần route tới **cả hai LAN**:

```cisco
R2(config)# ipv6 route 2001:db8:1::/64 2001:db8:12::1
R2(config)# ipv6 route 2001:db8:3::/64 2001:db8:23::3
```

*(Nếu dùng default `::/0` hai đầu mà R2 không có route về LAN → gói tới R2 rồi **drop**.
Đây là lý do static nhiều mạng rất dễ sót — OSPFv3 giải quyết tự động.)*

### Giải thích các lỗi BREAK

**Lỗi 1 — thiếu router-id ⭐:** OSPFv2 có thể tự chọn router-id từ **IP interface cao
nhất**. OSPFv3 chạy trên IPv6 **không có IPv4** để chọn → nếu không có interface IPv4
nào, process **không khởi động** và báo:
```text
%OSPFv3-4-NORTRID: Process OSPFv3-1-IPv6 could not pick a router-id, please configure manually
```
router-id **bắt buộc định dạng IPv4** *(32-bit)* — chỉ là định danh, không phải địa chỉ.

**Lỗi 2 — thiếu unicast-routing:** OSPFv3 **vẫn chạy** và neighbor có thể FULL *(hello
dùng link-local)*, nhưng R2 **không forward** gói IPv6 → traffic qua R2 chết. Bài học
kinh điển: **"giao thức định tuyến chạy" ≠ "router forward được"**. Cần cả hai.

**Lỗi 3 — thiếu interface trong OSPF:** Gỡ `ipv6 ospf 1 area 0` khỏi Gi0/2 của R2 →
**mất neighbor R2-R3** → R1 không học route tới LAN R3. Tương đương OSPFv2 quên `network`
cho một interface. Mỗi interface muốn tham gia OSPF phải được bật tường minh.

### Bảng tổng kết

| Điểm | OSPFv3 |
|---|---|
| Bật | trên interface: `ipv6 ospf 1 area 0` |
| Router-id | bắt buộc tay, định dạng IPv4 |
| Next-hop | link-local |
| unicast-routing | phải bật để forward |
| Dual-stack | OSPFv2 + OSPFv3 chạy song song độc lập |

</details>

---

## 📝 Ghi chú & bài học rút ra

- 3 khác biệt OSPFv2 vs OSPFv3 tôi nhớ được: ___
- Lỗi 1 (router-id) — vì sao OSPFv3 không tự chọn được? ___
- "Neighbor FULL nhưng LAN chưa vào OSPF" — tôi hiểu bẫy này chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
