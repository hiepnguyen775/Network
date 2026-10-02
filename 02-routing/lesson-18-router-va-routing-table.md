# LESSON 18 — Router hoạt động thế nào · Routing Table

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md), [Lesson 14](../01-switching/lesson-14-inter-vlan-routing.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Mô tả **5 bước** router xử lý một gói tin, theo đúng thứ tự
- [ ] Đọc `show ip route` và giải thích **từng ký tự** ở đầu dòng
- [ ] Phân biệt route `C` và `L` — và nói được vì sao `L` luôn là `/32`
- [ ] Giải thích RIB và FIB khác nhau thế nào
- [ ] Biết router làm gì khi **không có route** tới đích

## 2. Prerequisite

- ARP, default gateway, TTL *(Lesson 05)*
- SVI, inter-VLAN routing *(Lesson 14)*

---

## 3. Concept

### Router làm gì — 5 bước

```text
1. NHẬN frame  → kiểm FCS → bóc Ethernet header
2. ĐỌC IP header → lấy Destination IP
3. TRA routing table → tìm route khớp nhất
   ├─ Không có route  → DROP + gửi ICMP Destination Unreachable
   └─ Có route        → biết next-hop và exit interface
4. GIẢM TTL đi 1
   └─ TTL = 0 → DROP + gửi ICMP Time Exceeded
5. ĐÓNG GÓI LẠI → ARP tìm MAC của next-hop → tạo frame MỚI → gửi
```

> 🔑 Bước 5 là chỗ quy tắc *"MAC đổi mỗi hop, IP giữ nguyên"* xảy ra.
> Router **vứt bỏ hoàn toàn** Ethernet header cũ và tạo một cái mới.

### Routing table chứa gì

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route
Codes: L - local, C - connected, S - static, O - OSPF, D - EIGRP, B - BGP
       * - candidate default

Gateway of last resort is 203.0.113.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 203.0.113.1
      10.0.0.0/8 is variably subnetted, 4 subnets, 3 masks
C        10.0.1.0/24 is directly connected, GigabitEthernet0/0
L        10.0.1.1/32 is directly connected, GigabitEthernet0/0
O        10.0.2.0/24 [110/2] via 10.0.1.2, 00:12:34, GigabitEthernet0/0
S        10.0.9.0/30 [1/0] via 10.0.1.254
```

### Giải mã từng thành phần

| Thành phần | Nghĩa |
|---|---|
| `S` / `C` / `L` / `O` | **Nguồn** route — xem bảng dưới |
| `*` | Candidate default route |
| `10.0.2.0/24` | **Prefix** đích |
| `[110/2]` | `[Administrative Distance / Metric]` |
| `via 10.0.1.2` | **Next-hop** — gửi cho ai |
| `00:12:34` | Route này đã tồn tại bao lâu |
| `GigabitEthernet0/0` | **Exit interface** — ra cổng nào |

### Bảng mã nguồn route

| Mã | Nguồn | AD |
|:---:|---|:---:|
| `C` | **Connected** — interface up và có IP | 0 |
| `L` | **Local** — chính IP của interface, luôn `/32` | 0 |
| `S` | Static | 1 |
| `S*` | Static default route | 1 |
| `O` | OSPF | 110 |
| `O IA` | OSPF inter-area | 110 |
| `O E1` / `O E2` | OSPF external | 110 |
| `D` | EIGRP | 90 |
| `D EX` | EIGRP external | 170 |
| `R` | RIP | 120 |
| `B` | BGP | 20 (eBGP) / 200 (iBGP) |
| `i` | IS-IS | 115 |

### `C` và `L` — vì sao cần cả hai

```text
Interface Gi0/0 có IP 10.0.1.1/24

C  10.0.1.0/24  → "cả subnet này nằm ở Gi0/0, tôi route tới đó được"
L  10.0.1.1/32  → "địa chỉ này là CỦA TÔI, gói tới đây thì tôi xử lý, không chuyển tiếp"
```

> 🔑 `L` tồn tại để router phân biệt *"gói gửi **cho tôi**"* và *"gói gửi **qua tôi**"*.
> Ping `10.0.1.1` → khớp `L` → router tự trả lời.
> Ping `10.0.1.50` → khớp `C` → router ARP rồi chuyển tiếp.

### RIB vs FIB

| | **RIB** (Routing Information Base) | **FIB** (Forwarding Information Base) |
|---|---|---|
| Là gì | Bảng định tuyến "logic" | Bảng chuyển tiếp đã tối ưu cho phần cứng |
| Xem bằng | `show ip route` | `show ip cef` |
| Ai dùng | Control plane (CPU) | **Data plane (ASIC/CEF)** |
| Chứa gì | Mọi route đã học, kèm AD/metric | Chỉ route **tốt nhất** + MAC next-hop sẵn sàng |

Quá trình: routing protocol → **RIB** → chọn route tốt nhất → nạp xuống **FIB** →
ASIC dùng FIB để chuyển gói ở wire-speed.

> 🔧 Đây là lý do gói tin đầu tiên tới một đích mới đôi khi chậm hơn — FIB chưa có entry,
> phải nhờ CPU xử lý rồi mới cache lại.

---

## 4. Why? — vì sao cần routing table

> **Nếu router cứ gửi gói ra mọi interface thì sao?**

| Vấn đề | Thực tế |
|---|---|
| Nhân gói tin vô hạn | Giống broadcast storm, nhưng ở quy mô Internet |
| Lãng phí băng thông | Mỗi gói đi mọi hướng |
| Không bao giờ hội tụ | Không có cách nào biết đường nào đúng |

Routing table là **bản đồ** của router: *"muốn tới mạng X, đưa cho thằng Y"*.
Mỗi router chỉ cần biết **hop tiếp theo** — không cần biết toàn bộ đường đi.

> 💡 Đây là nguyên lý **hop-by-hop forwarding**: không ai nắm toàn bộ bản đồ Internet,
> mỗi router chỉ biết "bước kế tiếp đi đâu". Giống như hỏi đường từng chặng
> thay vì cần một tấm bản đồ toàn thế giới.

---

## 5. How does it work? — route đến từ đâu

| Cách | Lệnh/cơ chế | Khi nào xuất hiện |
|---|---|---|
| **Connected** | Gán IP + `no shutdown` | Interface `up/up` → route tự xuất hiện |
| **Static** | `ip route <net> <mask> <next-hop>` | Gõ tay |
| **Dynamic** | OSPF, EIGRP, BGP… | Router tự học từ láng giềng |

> ⚠️ **Connected route biến mất khi interface down.** Và mọi static route trỏ qua
> interface đó cũng **biến mất theo** — vì next-hop không còn reachable.
> Đây là nguyên nhân rất hay gặp của "route tự nhiên mất".

### Khi không có route

```text
Router nhận gói tới 8.8.8.8
→ Tra routing table: không có 8.8.8.8, không có default route
→ DROP gói
→ Gửi về nguồn: ICMP Type 3 Code 0 (Network Unreachable)
```

Người dùng thấy: `Destination host unreachable` — và đây là thông tin quý,
vì nó nói rõ **router nào** không biết đường.

---

## 6. Packet Flow

**PC `10.0.1.50` → Server `10.0.2.50`**, qua R1.

| Bước | Ở đâu | Chuyện gì |
|:---:|---|---|
| 1 | PC | AND → khác subnet → gửi cho gateway `10.0.1.1`, ARP tìm MAC-R1 |
| 2 | R1 | Nhận frame, bóc Ethernet header, đọc Dst IP `10.0.2.50` |
| 3 | R1 | Tra RIB: khớp `O 10.0.2.0/24 via 10.0.1.2` |
| 4 | R1 | **TTL 128 → 127** |
| 5 | R1 | ARP tìm MAC của `10.0.1.2`, tạo **frame mới** |
| 6 | R1 | Gửi ra `Gi0/0` |

**IP nguồn/đích không đổi. MAC đổi hoàn toàn. TTL giảm 1.**

---

## 7. Real-world Example

🏭 **"Route tự nhiên mất"** — ba nguyên nhân thật:

| Nguyên nhân | Dấu hiệu |
|---|---|
| Interface down | `C` và `L` của interface đó biến mất, kéo theo mọi static trỏ qua đó |
| Route có AD thấp hơn xuất hiện | Route cũ bị đẩy ra khỏi RIB, không mất hẳn nhưng không còn active |
| Routing protocol mất neighbor | `O` route hết hạn và bị xoá |

🏭 **Ping được 1 chiều** — kinh điển và luôn cùng một nguyên nhân:

```text
R1 có route tới 10.0.2.0/24   ✅ gói đi được
R2 KHÔNG có route về 10.0.1.0/24  ❌ gói trả lời không về được
```

> 🔧 Phản xạ nghề: khi thấy ping một chiều, **kiểm tra `show ip route` ở CẢ HAI đầu**.
> Đừng chỉ nhìn đầu mình.

---

## 8. Cisco CLI

```cisco
! ───── Xem routing table ─────
R1# show ip route
R1# show ip route 10.0.2.50              ! router CHỌN route nào cho đích này
R1# show ip route connected
R1# show ip route static
R1# show ip route ospf
R1# show ip route | include 10.0.2        ! lọc

! ───── FIB ─────
R1# show ip cef
R1# show ip cef 10.0.2.50

! ───── Thông tin chi tiết một route ─────
R1# show ip route 10.0.2.0 255.255.255.0

! ───── Kiểm tra protocol đang chạy ─────
R1# show ip protocols
```

| Lệnh | Trả lời câu hỏi | Lưu ý |
|---|---|---|
| `show ip route <ip>` | Router **thật sự** chọn route nào | ⭐ Hữu dụng hơn đọc cả bảng |
| `show ip cef <ip>` | Data plane thấy gì | Khác RIB → có vấn đề |
| `show ip protocols` | Protocol nào chạy, network nào được quảng bá | Luôn xem khi route thiếu |

> **Khác biệt platform:** NX-OS dùng `show ip route` tương tự nhưng có thêm khái niệm
> **VRF** mặc định — nhiều lệnh cần `vrf <name>`. IOS-XE giống IOS.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route 10.0.2.50
Routing entry for 10.0.2.0/24
  Known via "ospf 1", distance 110, metric 2, type intra area
  Last update from 10.0.1.2 on GigabitEthernet0/0, 00:15:22 ago
  Routing Descriptor Blocks:
  * 10.0.1.2, from 2.2.2.2, 00:15:22 ago, via GigabitEthernet0/0
      Route metric is 2, traffic share count is 1
```

**Đọc gì:**

| Dòng | Ý nghĩa |
|---|---|
| `Known via "ospf 1"` | Route học từ đâu |
| `distance 110, metric 2` | AD và metric |
| `type intra area` | Trong cùng area OSPF |
| `Last update ... 00:15:22 ago` | Route ổn định 15 phút |
| `*` trước next-hop | Đường đang được dùng |
| Nhiều `Routing Descriptor Blocks` | **ECMP** — cân bằng tải nhiều đường |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| `Destination host unreachable` | Router không có route | `show ip route <ip>` | Thêm route hoặc default route |
| Ping được 1 chiều | Thiếu route **chiều về** | `show ip route` ở **cả 2 đầu** | Thêm route còn thiếu |
| Route biến mất | Interface down | `show ip interface brief` | `no shutdown`, kiểm tra cáp |
| `show ip route` trống trên L3 switch | Chưa `ip routing` | `show run \| include ip routing` | Bật `ip routing` |
| Route có nhưng gói vẫn không đi | ACL chặn, hoặc FIB lệch RIB | `show access-lists`, `show ip cef <ip>` | Sửa ACL / `clear ip route *` |
| Gói đi sai đường | Route khác khớp cụ thể hơn | `show ip route <ip>` | Xem longest prefix match *(Lesson 20)* |

---

## 11. LAB

🧪 **[LAB 20 — Routing table cơ bản](../labs/lab20-routing-table-co-ban.md)**

Yêu cầu tối thiểu:

- 2 router nối nhau, mỗi router 1 LAN, chưa có route nào → PC không ping được nhau
- Quan sát `show ip route` chỉ có `C` và `L`
- Chứng minh ping tới IP của chính router khớp `L`, ping tới host trong LAN khớp `C`
- **BREAK:** (1) `shutdown` interface → quan sát `C`/`L` biến mất;
  (2) ping một mạng không có route → đọc đúng thông báo ICMP;
  (3) đặt IP trùng subnet trên 2 interface → quan sát IOS từ chối

## 12. Challenge

1. Interface `Gi0/0` có IP `10.0.1.1/24`. Có **mấy** route xuất hiện? Prefix của từng cái?
2. Vì sao route `L` luôn là `/32` chứ không phải `/24`?
3. Router nhận gói tới `10.0.1.1` (chính IP của nó). Nó làm gì khác với gói tới `10.0.1.50`?
4. `show ip route` có route tới đích, nhưng ping vẫn fail. Nêu **3 nguyên nhân**.

<details>
<summary>Đáp án</summary>

**1.** **Hai** route:

```text
C  10.0.1.0/24   is directly connected, GigabitEthernet0/0
L  10.0.1.1/32   is directly connected, GigabitEthernet0/0
```

**2.** Vì `L` đại diện cho **đúng một địa chỉ** — IP của chính router.
`/32` nghĩa là "chỉ mình địa chỉ này". Nếu là `/24` thì nó trùng với route `C`
và router không phân biệt được "gói cho tôi" với "gói qua tôi".

**3.**

| Gói tới | Khớp route | Router làm gì |
|---|---|---|
| `10.0.1.1` | `L 10.0.1.1/32` | **Xử lý tại chỗ** — tự trả lời ICMP, hoặc đưa lên control plane (SSH, OSPF…) |
| `10.0.1.50` | `C 10.0.1.0/24` | **Chuyển tiếp** — ARP tìm MAC của `.50` rồi gửi ra interface |

Longest prefix match đảm bảo `/32` thắng `/24`.

**4.** Ba nguyên nhân phổ biến:

| # | Nguyên nhân | Kiểm chứng |
|:---:|---|---|
| 1 | Thiếu route **chiều về** ở đầu kia | `show ip route` ở router đối diện |
| 2 | **ACL** chặn | `show access-lists` — xem counter có tăng |
| 3 | Next-hop không reachable (ARP fail, interface down ở chặng sau) | `show ip arp`, `ping <next-hop>` |

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 5 bước router xử lý gói · mã `C`/`L`/`S`/`O` · `[AD/metric]` | ⬜ |
| **L2** Explain | Giải thích vì sao cần cả `C` và `L` | ⬜ |
| **L3** Configure | Gán IP 3 interface, verify `show ip route connected` | ⬜ |
| **L4** Troubleshoot | Ping một chiều → tìm ra thiếu route chiều về | ⬜ |
| **L5** Design | Vẽ routing table dự kiến của một topology 3 router | ⬜ |

## 14. Summary

**Key concepts**

- 5 bước: nhận frame → đọc Dst IP → tra RIB → giảm TTL → đóng gói mới + gửi
- `C` = subnet của interface · **`L` = IP của chính router, luôn `/32`**
- `[110/2]` = `[AD / Metric]`
- **RIB** = bảng logic (`show ip route`) · **FIB** = bảng phần cứng (`show ip cef`)
- Không có route → **DROP + ICMP Destination Unreachable**
- ⭐ Interface down → mất `C`, `L`, **và mọi static trỏ qua đó**
- ⭐ Ping một chiều = thiếu route **chiều về** → luôn kiểm tra **cả hai đầu**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip route` | Luôn luôn |
| `show ip route <ip>` | Router **thật sự** chọn route nào |
| `show ip route connected` | Interface nào đang up và có IP |
| `show ip protocols` | Protocol nào chạy, quảng bá gì |

**Common mistakes**

| Sai | Đúng |
|---|---|
| Chỉ xem routing table ở một đầu | Ping một chiều → xem **cả hai** |
| Nghĩ `L` là lỗi hiển thị | Nó là route riêng, có mục đích rõ ràng |
| Quên `ip routing` trên L3 switch | `show ip route` trống |
| Nghĩ có route là chắc chắn thông | Còn ACL, còn next-hop reachability |

## 15. Homework + cập nhật PROGRESS

1. Trên lab: gán IP cho 3 interface, chạy `show ip route`. Đếm số route — có đúng 6 không?
2. `shutdown` một interface, chạy lại. Mất mấy route?
3. Chạy `show ip route 8.8.8.8` trên router có default route — đọc kỹ output.

```markdown
- [YYYY-MM-DD] Lesson 18 — Router & Routing Table: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Mã route, `[AD/metric]`, `C` vs `L`, 5 bước forwarding |
| 🔧 **Engineer** | `show ip route <ip>` thay vì đọc cả bảng; kiểm tra 2 đầu khi ping 1 chiều |
| 🏭 **Production** | Interface down kéo theo static route; RIB/FIB lệch nhau là dấu hiệu bất thường |

### 🔗 Liên kết

- ⬅️ [Lesson 17 — EtherChannel & Port Security](../01-switching/lesson-17-etherchannel-port-security.md)
- ➡️ [Lesson 19 — Static & Default Route](./lesson-19-static-default-route.md)
- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md#3-layer-3--routing)
