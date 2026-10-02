# LESSON 31 — IPv6 Routing · OSPFv3 · Dual-stack

| | |
|---|---|
| **Phase** | 4 — IPv6 |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 30](./lesson-30-slaac-ndp-dhcpv6.md), [Lesson 22](../02-routing/lesson-22-ospf-single-area.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Cấu hình static route IPv6, hiểu vì sao next-hop thường là **link-local**
- [ ] Cấu hình **OSPFv3** và nói được nó khác OSPFv2 ở những điểm nào
- [ ] Giải thích **dual-stack** và thuật toán Happy Eyeballs
- [ ] Đọc `show ipv6 route` và phân biệt các mã route
- [ ] Troubleshoot IPv6 routing theo phương pháp

## 2. Prerequisite

- SLAAC, NDP, link-local *(Lesson 30)*
- OSPF: neighbor state, DR/BDR, area, cost *(Lesson 22, 23, 24)*

---

## 3. Concept

### Static route IPv6

```cisco
! Trỏ next-hop GLOBAL (giống IPv4)
ipv6 route 2001:db8:20::/64 2001:db8:12::2

! Trỏ next-hop LINK-LOCAL — PHẢI kèm interface
ipv6 route 2001:db8:20::/64 GigabitEthernet0/1 FE80::2

! Trỏ exit-interface (chỉ cho point-to-point)
ipv6 route 2001:db8:20::/64 GigabitEthernet0/1

! Default route
ipv6 route ::/0 2001:db8:12::2

! Floating static (AD cao)
ipv6 route ::/0 2001:db8:13::2 200
```

> ⭐ **Vì sao next-hop thường là link-local:**
> Link-local **không bao giờ đổi** — nó tự sinh và tồn tại ngay cả khi GUA chưa được cấp
> hoặc bị đổi prefix. Route trỏ link-local **ổn định hơn**.
>
> Cái giá: link-local **không duy nhất toàn cục** (`fe80::1` có thể ở mọi router),
> nên **bắt buộc phải kèm tên interface** để router biết gửi ra đâu.

### Mã route trong `show ipv6 route`

| Mã | Nghĩa |
|:---:|---|
| `C` | Connected |
| `L` | **Local** — chính địa chỉ của interface, `/128` |
| `S` | Static |
| `O` | OSPFv3 intra-area |
| `OI` | OSPFv3 **inter-area** |
| `OE1` / `OE2` | OSPFv3 external |
| `D` | EIGRPv6 |
| `B` | BGP |
| `ND` | **Học từ Router Advertisement** — mới, không có ở IPv4 |

> 💡 Mã **`ND`** là đặc trưng IPv6: route default học được từ RA khi router đóng vai
> host trên một link nào đó.

### OSPFv3 — khác OSPFv2 ở đâu

| | **OSPFv2 (IPv4)** | **OSPFv3 (IPv6)** |
|---|---|---|
| Chuẩn | RFC 2328 | RFC 5340 |
| Cấu hình ở đâu | **`network` statement** | **Trên interface** |
| Neighbor nhận diện bằng | IP interface | **Link-local** |
| Multicast | `224.0.0.5` / `224.0.0.6` | **`ff02::5` / `ff02::6`** |
| Router ID | 32 bit, tự lấy từ IP | 32 bit, **PHẢI cấu hình tay** nếu không có IPv4 |
| Authentication | Trong protocol | **Dùng IPsec** của IPv6 |
| Chạy nhiều address family | ❌ | ✅ *(OSPFv3 AF)* |
| Neighbor state, DR/BDR, LSA type | **Giống hệt** | **Giống hệt** |

> 🔑 **Tin tốt:** mọi thứ bạn học ở Lesson 22–24 (7 state, 6 thứ phải khớp, DR/BDR,
> cost, area, LSA) **áp dụng y nguyên** cho OSPFv3. Chỉ cú pháp cấu hình đổi.

> ⚠️ **Router ID của OSPFv3 vẫn là 32 bit** (định dạng như IPv4). Trên router
> **chỉ chạy IPv6**, không có địa chỉ IPv4 nào → OSPFv3 **không tự chọn được Router ID**
> → process không khởi động. **Phải đặt tay.**

### Hai cú pháp OSPFv3

```cisco
! ───── Cách cũ (ipv6 router ospf) ─────
R1(config)# ipv6 router ospf 1
R1(config-rtr)# router-id 1.1.1.1
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ipv6 ospf 1 area 0

! ───── Cách mới (address-family) — IOS-XE ─────
R1(config)# router ospfv3 1
R1(config-router)# router-id 1.1.1.1
R1(config-router)# address-family ipv6 unicast
R1(config-router-af)# exit-address-family
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ospfv3 1 ipv6 area 0
```

> 💡 Cách mới cho phép **một process OSPFv3 chạy cả IPv4 và IPv6** (address family).
> Ở CCNA, cách cũ là đủ và phổ biến hơn trong lab.

### Dual-stack

**Dual-stack** = thiết bị chạy **cả IPv4 và IPv6 song song**, hai ngăn xếp độc lập.

```text
            Ứng dụng
         ┌──────┴──────┐
      IPv4           IPv6
         └──────┬──────┘
           Ethernet
```

Đây là mô hình **chuyển đổi chuẩn** hiện nay — gần như không ai chạy IPv6-only.

### Happy Eyeballs — ứng dụng chọn thế nào

Khi một tên miền có **cả A và AAAA record**:

```text
1. Trình duyệt gửi TRUY VẤN DNS cho CẢ A và AAAA
2. Thử kết nối IPv6 trước (ưu tiên)
3. Nếu IPv6 không phản hồi trong ~250 ms
   → thử IPv4 SONG SONG
4. Dùng cái nào kết nối xong trước
5. Nhớ kết quả cho lần sau
```

> 🔑 **Hệ quả thực tế rất quan trọng:** nếu IPv6 cấu hình **sai nhưng không chết hẳn**
> (ví dụ có địa chỉ nhưng không ra được Internet), người dùng sẽ thấy web **chậm**
> do phải chờ timeout IPv6 rồi mới fallback.
>
> Triệu chứng: *"mạng chậm"* nhưng `ping 8.8.8.8` hoàn toàn bình thường.
> Đây là lý do **IPv6 cấu hình nửa vời còn tệ hơn không có IPv6**.

---

## 4. Why?

> **Vì sao OSPFv3 dùng link-local làm địa chỉ neighbor?**

| Lý do | Giải thích |
|---|---|
| **Luôn tồn tại** | Link-local tự sinh ngay khi bật IPv6 — không cần GUA |
| **Không đổi** | Đổi prefix GUA không ảnh hưởng adjacency |
| **Chạy được trước khi có địa chỉ** | Router có thể chạy OSPFv3 trên interface chỉ có `ipv6 enable` |

> **Vì sao không chuyển thẳng sang IPv6-only?**

| Rào cản | Thực tế |
|---|---|
| Nhiều dịch vụ Internet vẫn chỉ có IPv4 | Phải có cách truy cập |
| Ứng dụng nội bộ cũ hardcode IPv4 | Không sửa được |
| Thiết bị cũ không hỗ trợ IPv6 | Máy in, camera, SCADA |

Giải pháp chuyển đổi:

| Cơ chế | Làm gì |
|---|---|
| **Dual-stack** ⭐ | Chạy cả hai — đơn giản nhất, chuẩn thực tế |
| **NAT64 + DNS64** | Mạng IPv6-only truy cập được dịch vụ IPv4 |
| Tunneling (6to4, Teredo, GRE) | Chở IPv6 qua hạ tầng IPv4 — ngày càng ít dùng |

---

## 5. How does it work? — OSPFv3 lên neighbor

```text
1. Interface bật IPv6 → tự có link-local fe80::X
2. Bật OSPFv3 trên interface → gửi Hello tới ff02::5
   Src = LINK-LOCAL của mình
3. Nhận Hello từ láng giềng → thấy Router ID
4. DOWN → INIT → 2-WAY → (bầu DR/BDR nếu multi-access)
   → EXSTART → EXCHANGE → LOADING → FULL
5. Trao đổi LSA, xây LSDB
6. Chạy SPF → nạp routing table
```

**Giống hệt OSPFv2.** Chỉ khác: địa chỉ multicast, địa chỉ neighbor là link-local.

### 6 thứ phải khớp — vẫn thế

| # | Phải khớp |
|:---:|---|
| 1 | **Cùng link** *(không cần cùng subnet GUA!)* |
| 2 | **Area ID** |
| 3 | **Hello / Dead timer** |
| 4 | **Authentication (IPsec)** |
| 5 | **MTU** |
| 6 | Không bị passive |

> 🔑 Khác biệt nhỏ nhưng đáng chú ý ở mục 1: OSPFv2 yêu cầu hai đầu **cùng subnet IPv4**.
> OSPFv3 chỉ cần **cùng link** — vì nó dùng link-local, không quan tâm GUA.
>
> Hệ quả: hai router có GUA khác prefix vẫn lên neighbor OSPFv3 được.
> Điều này **che giấu lỗi cấu hình** — neighbor lên nhưng traffic không đi được.

---

## 6. Packet Flow — dual-stack một gói đi thế nào

```text
PC dual-stack muốn vào web.example.com

1. DNS: hỏi CẢ A và AAAA
   → nhận  A    = 93.184.x.x
   → nhận  AAAA = 2606:2800::x

2. Happy Eyeballs: thử IPv6 trước
   ├─ IPv6 OK trong 250ms  → DÙNG IPv6
   └─ Chậm/fail            → thử IPv4 song song, dùng cái xong trước

3. Gói đi: HOÀN TOÀN trong một ngăn xếp
   - Nếu IPv6: dùng NDP tìm MAC, routing IPv6, không đụng gì tới IPv4
   - Nếu IPv4: dùng ARP, routing IPv4
```

> 🔑 **Dual-stack không "trộn" hai giao thức.** Một kết nối hoàn toàn là IPv4
> hoặc hoàn toàn là IPv6. Chúng chỉ dùng chung tầng dưới (Ethernet) và tầng trên (ứng dụng).

---

## 7. Real-world Example

🏭 **Triển khai dual-stack cho doanh nghiệp — thứ tự đúng**

```text
1. Xin prefix IPv6 từ ISP (thường /48)
2. Thiết kế addressing plan (Lesson 29)
3. Bật IPv6 trên CORE và DISTRIBUTION trước, chạy OSPFv3
4. Bật trên từng VLAN một — BẮT ĐẦU TỪ VLAN IT
5. Giám sát kỹ 1–2 tuần mỗi VLAN
6. Mở rộng dần ra các VLAN còn lại
7. Cuối cùng mới bật cho VLAN guest/production quan trọng
```

> ⚠️ **Đừng bật IPv6 toàn mạng cùng lúc.** Nếu có lỗi, Happy Eyeballs sẽ che giấu nó
> dưới dạng "mạng hơi chậm" và bạn sẽ rất khó tìm.

🏭 **Sự cố kinh điển: IPv6 nửa vời**

```text
Triệu chứng: web chậm 1–3 giây mới load, nhưng ping IPv4 bình thường.

Nguyên nhân: host có địa chỉ IPv6 (SLAAC từ một router nào đó)
             nhưng đường ra Internet IPv6 KHÔNG hoạt động.

Trình duyệt thử IPv6 trước → timeout → mới fallback IPv4.
```

Chẩn đoán:

```powershell
ping -6 2606:4700:4700::1111      # Cloudflare IPv6
curl -6 https://ipv6.google.com
```

Nếu IPv6 fail: hoặc **sửa cho đúng**, hoặc **tắt hẳn** IPv6 trên VLAN đó.
**Đừng để nửa vời.**

🏭 **OSPFv3 lên neighbor nhưng không ping được**

Hai router lên FULL nhưng traffic không đi. Nguyên nhân: GUA hai đầu **khác prefix**.

```text
R1: 2001:db8:12::1/64
R2: 2001:db8:99::2/64      ← khác prefix!
```

OSPFv3 vẫn lên vì nó dùng **link-local** để peer. Nhưng khi forward gói thật,
hai router không cùng subnet → không gửi được cho nhau.

> 🔧 Đây là bẫy **không tồn tại ở OSPFv2** (vốn yêu cầu cùng subnet).
> Khi debug OSPFv3, luôn kiểm tra GUA hai đầu **ngoài** việc xem neighbor state.

---

## 8. Cisco CLI

```cisco
! ═══════ STATIC ROUTE IPv6 ═══════
R1(config)# ipv6 unicast-routing
R1(config)# ipv6 route 2001:db8:20::/64 2001:db8:12::2
R1(config)# ipv6 route 2001:db8:30::/64 GigabitEthernet0/1 FE80::2
R1(config)# ipv6 route ::/0 2001:db8:12::2
R1(config)# ipv6 route ::/0 2001:db8:13::2 200          ! floating

! ═══════ OSPFv3 ═══════
R1(config)# ipv6 router ospf 1
R1(config-rtr)# router-id 1.1.1.1                       ! ⚠️ BẮT BUỘC nếu không có IPv4
R1(config-rtr)# auto-cost reference-bandwidth 100000
R1(config-rtr)# passive-interface default
R1(config-rtr)# no passive-interface GigabitEthernet0/1
R1(config-rtr)# exit

R1(config)# interface GigabitEthernet0/1
R1(config-if)# ipv6 ospf 1 area 0                       ! bật trên interface
R1(config-if)# ipv6 ospf cost 10
R1(config-if)# ipv6 ospf priority 255                   ! ép làm DR
R1(config-if)# ipv6 ospf network point-to-point         ! bỏ bầu DR

! Quảng bá default route
R1(config-rtr)# default-information originate

! ═══════ KIỂM TRA ═══════
R1# show ipv6 route
R1# show ipv6 route ospf
R1# show ipv6 ospf neighbor
R1# show ipv6 ospf interface GigabitEthernet0/1
R1# show ipv6 ospf database
R1# show ipv6 protocols
R1# clear ipv6 ospf process
```

| Lệnh | Lưu ý |
|---|---|
| `ipv6 unicast-routing` | ⭐ Luôn đầu tiên |
| `router-id` trong OSPFv3 | ⚠️ **Bắt buộc** nếu router không có IPv4 nào |
| `ipv6 ospf 1 area 0` | Bật **trên interface** — không có `network` statement |
| `ipv6 route ... <int> FE80::X` | Next-hop link-local **phải kèm interface** |
| `show ipv6 protocols` | Protocol nào chạy, interface nào tham gia |

> **Khác biệt platform:** NX-OS cần `feature ospfv3`, cấu hình bằng
> `ipv6 router ospfv3 1` và trên interface `ipv6 router ospfv3 1 area 0`.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 route
IPv6 Routing Table - default - 7 entries
Codes: C - Connected, L - Local, S - Static, U - Per-user Static route
       O - OSPF Intra, OI - OSPF Inter, ND - ND Default

C   2001:DB8:12::/64 [0/0]
     via GigabitEthernet0/1, directly connected
L   2001:DB8:12::1/128 [0/0]
     via GigabitEthernet0/1, receive
O   2001:DB8:20::/64 [110/2]
     via FE80::2, GigabitEthernet0/1
OI  2001:DB8:99::/64 [110/4]
     via FE80::2, GigabitEthernet0/1
S   ::/0 [1/0]
     via 2001:DB8:12::2
```

**Đọc gì:**

| Dòng | Ý nghĩa |
|---|---|
| `L ... /128` | Địa chỉ của chính router — luôn `/128` *(giống `L` của IPv4)* |
| `via FE80::2, GigabitEthernet0/1` | ⭐ **Next-hop là link-local + tên interface** |
| `O` vs `OI` | Intra-area vs **Inter-area** |
| `[110/2]` | `[AD / Cost]` — AD của OSPFv3 vẫn là **110** |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 ospf neighbor

            OSPFv3 Router with ID (1.1.1.1) (Process ID 1)

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
2.2.2.2           1   FULL/DR         00:00:33    4               GigabitEthernet0/1
3.3.3.3           1   FULL/BDR        00:00:31    4               GigabitEthernet0/1
```

> 🔍 Khác OSPFv2: có thêm cột **`Interface ID`** (số hiệu interface của láng giềng),
> và **không hiển thị địa chỉ IPv6** của neighbor — vì nó peer bằng link-local.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 ospf interface GigabitEthernet0/1
GigabitEthernet0/1 is up, line protocol is up
  Link Local Address FE80::1, Interface ID 4
  Area 0, Process ID 1, Instance ID 0, Router ID 1.1.1.1
  Network Type BROADCAST, Cost: 1
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
  Designated Router (ID) 2.2.2.2
  Neighbor Count is 2, Adjacent neighbor count is 2
```

> 🔑 Lệnh này vẫn là **lệnh debug quan trọng nhất** — hiển thị Area, Network Type,
> Cost, Timer cùng lúc, y như OSPFv2.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| OSPFv3 process không chạy | **Thiếu Router ID** *(router không có IPv4)* | `show ipv6 ospf` | `router-id 1.1.1.1` |
| Không lên neighbor | Area lệch, timer lệch, MTU, passive | `show ipv6 ospf interface <int>` 2 đầu | Giống quy trình OSPFv2 |
| Kẹt EXSTART/EXCHANGE | **MTU mismatch** | `show interfaces \| include MTU` | Đồng bộ MTU |
| **FULL nhưng không ping được** | ⭐ GUA hai đầu **khác prefix** | `show ipv6 interface brief` 2 đầu | Đặt cùng prefix |
| Route IPv6 có nhưng không forward | Quên `ipv6 unicast-routing` | `show run \| include unicast-routing` | Bật lệnh đó |
| Static route IPv6 không vào bảng | Next-hop link-local **thiếu interface** | `show run \| include ipv6 route` | Thêm tên interface |
| Web chậm 1–3 giây mới load | **IPv6 nửa vời** — có địa chỉ, không ra được | `ping -6 2606:4700:4700::1111` | Sửa IPv6, hoặc tắt hẳn |
| Ping IPv6 trong LAN OK, ra ngoài fail | Thiếu default route IPv6 | `show ipv6 route ::/0` | `ipv6 route ::/0 <nh>` |

---

## 11. LAB

🧪 **LAB 42 — IPv6 routing & OSPFv3** → [`../labs/lab42-ipv6-ospfv3.md`](../labs/lab42-ipv6-ospfv3.md)

Yêu cầu tối thiểu:

- 3 router, mỗi router 1 LAN IPv6. Dùng **static route IPv6** trước → ping end-to-end
- Chuyển sang **OSPFv3 single-area** → verify `show ipv6 ospf neighbor` FULL
- Thêm area thứ hai → quan sát route `OI` xuất hiện
- Cấu hình **dual-stack**: chạy cả OSPFv2 và OSPFv3 song song trên cùng topology
- **BREAK bắt buộc:** (1) không đặt `router-id` trên router chỉ có IPv6 →
  OSPFv3 không chạy; (2) static route next-hop link-local **không kèm interface**;
  (3) đặt GUA khác prefix hai đầu → neighbor FULL nhưng không ping được

## 12. Challenge

1. Router chỉ chạy IPv6, không có địa chỉ IPv4 nào. Bạn bật OSPFv3 nhưng
   `show ipv6 ospf neighbor` trống và không có log gì. Vì sao?
2. `ipv6 route 2001:db8:20::/64 FE80::2` — lệnh này có vấn đề gì?
3. Hai router OSPFv3 lên FULL nhưng ping GUA của nhau không được. Nêu nguyên nhân
   và vì sao lỗi này **không xảy ra** với OSPFv2.
4. Người dùng báo "web chậm", nhưng `ping 8.8.8.8` chỉ 20ms. Nêu 1 nguyên nhân
   liên quan IPv6 và cách kiểm chứng.

<details>
<summary>Đáp án</summary>

**1.** **OSPFv3 không có Router ID.**

Router ID của OSPFv3 vẫn là **32 bit, định dạng như địa chỉ IPv4**. Nó tự chọn theo
thứ tự: `router-id` tay → loopback IPv4 → interface IPv4.

Router **không có địa chỉ IPv4 nào** → không có nguồn nào để lấy → **process không
khởi động**. Và IOS thường chỉ ghi một dòng log nhỏ dễ bỏ sót.

Sửa:

```cisco
R1(config)# ipv6 router ospf 1
R1(config-rtr)# router-id 1.1.1.1
```

**2.** **Thiếu tên interface.**

`FE80::2` là link-local — nó **không duy nhất toàn cục**. Mọi router đều có thể có
`fe80::2`. Router không biết gửi gói ra interface nào.

IOS sẽ từ chối lệnh hoặc route không vào bảng. Đúng phải là:

```cisco
ipv6 route 2001:db8:20::/64 GigabitEthernet0/1 FE80::2
```

**3.** Nguyên nhân: **GUA hai đầu khác prefix**.

```text
R1: 2001:db8:12::1/64
R2: 2001:db8:99::2/64
```

OSPFv3 **peer bằng link-local**, mà link-local luôn cùng link → neighbor lên FULL
bình thường. Nhưng khi forward gói thật bằng GUA, hai router **không cùng subnet** →
không gửi được cho nhau.

**Vì sao không xảy ra với OSPFv2:** OSPFv2 yêu cầu hai đầu **cùng subnet IPv4** mới lên
neighbor. Subnet lệch → neighbor **không lên** → bạn phát hiện ngay.

OSPFv3 "khoan dung" hơn, và chính sự khoan dung đó **che giấu lỗi cấu hình**.

👉 Bài học: với OSPFv3, **neighbor FULL chưa đủ** — phải kiểm tra cả GUA.

**4.** Nguyên nhân: **IPv6 nửa vời** + Happy Eyeballs.

```text
Máy có địa chỉ IPv6 (từ SLAAC) nhưng đường ra Internet IPv6 không hoạt động.
Trình duyệt thử IPv6 trước → chờ timeout (~250ms–3s tuỳ cấu hình)
→ mới fallback sang IPv4.
→ Mỗi tên miền mới = thêm độ trễ.
```

`ping 8.8.8.8` chỉ test IPv4 nên hoàn toàn bình thường.

Kiểm chứng:

```powershell
ping -6 2606:4700:4700::1111        # nếu fail → đúng là IPv6 hỏng
curl -6 https://ipv6.google.com
ipconfig /all                       # xem có địa chỉ IPv6 GUA không
```

Sửa: hoặc **làm IPv6 chạy đúng**, hoặc **tắt hẳn IPv6** trên VLAN đó
(không cấp RA). Đừng để nửa vời.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Mã route IPv6 · multicast OSPFv3 · OSPFv3 khác OSPFv2 ở đâu | ⬜ |
| **L2** Explain | Giải thích Happy Eyeballs và hệ quả của IPv6 nửa vời | ⬜ |
| **L3** Configure | Static route IPv6 + OSPFv3 2 area + dual-stack | ⬜ |
| **L4** Troubleshoot | FULL nhưng không ping được → tìm ra GUA khác prefix | ⬜ |
| **L5** Design | Lập kế hoạch triển khai dual-stack cho công ty, theo thứ tự an toàn | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **Next-hop link-local phải kèm tên interface** — link-local không duy nhất toàn cục
- Mã route: `C` `L` `S` `O` `OI` `OE1/2` **`ND`** *(học từ RA — đặc trưng IPv6)*
- OSPFv3: cấu hình **trên interface**, peer bằng **link-local**, `ff02::5`/`ff02::6`
- ⭐ **Router ID OSPFv3 vẫn 32 bit — PHẢI đặt tay nếu router không có IPv4**
- Neighbor state, DR/BDR, cost, area, LSA của OSPFv3 **giống hệt OSPFv2**
- ⚠️ OSPFv3 chỉ cần **cùng link**, không cần cùng subnet GUA → **che giấu lỗi cấu hình**
- **Dual-stack** = hai ngăn xếp độc lập, không trộn lẫn
- ⭐ **Happy Eyeballs**: thử IPv6 trước, ~250ms không được thì fallback IPv4
- ⚠️ **IPv6 nửa vời còn tệ hơn không có IPv6** — gây "mạng chậm" khó chẩn đoán

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ipv6 route <prefix> <int> FE80::X` | Static với next-hop link-local |
| `ipv6 router ospf 1` + `router-id` | ⭐ Router ID bắt buộc |
| `ipv6 ospf 1 area 0` *(trên interface)* | Bật OSPFv3 |
| `show ipv6 route` | Bảng định tuyến IPv6 |
| `show ipv6 ospf neighbor` | Neighbor state |
| `show ipv6 ospf interface <int>` | ⭐ Area, cost, timer, DR cùng lúc |
| `ping -6 2606:4700:4700::1111` | Test IPv6 ra Internet |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Không đặt `router-id` trên router IPv6-only | OSPFv3 **không khởi động** |
| Static link-local thiếu tên interface | Route không vào bảng |
| Thấy neighbor FULL là yên tâm | GUA có thể khác prefix → không forward được |
| Bật IPv6 toàn mạng cùng lúc | Lỗi bị che giấu dưới dạng "mạng chậm" |
| Để IPv6 nửa vời | Tệ hơn không có IPv6 |
| Quên `ipv6 unicast-routing` | Không route, không RA |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 42 với đủ 3 lỗi BREAK.
2. Trên máy thật: `ping -6 2606:4700:4700::1111`. Nếu fail mà `ipconfig` vẫn có
   địa chỉ IPv6 GUA → bạn đang gặp đúng tình huống "IPv6 nửa vời".
3. So `show ip ospf neighbor` và `show ipv6 ospf neighbor` trên cùng một lab dual-stack —
   liệt kê 3 khác biệt trong output.

```markdown
- [YYYY-MM-DD] Lesson 31 — IPv6 routing & OSPFv3: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 4

Làm **[Mini Exam Phase 4](./review-phase04.md)** trước khi sang
[Phase 5 — Wireless](../05-wireless/README.md).

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Mã route IPv6, cú pháp OSPFv3, khác biệt OSPFv2/v3, dual-stack |
| 🔧 **Engineer** | Luôn đặt Router ID; static link-local kèm interface; kiểm tra GUA ngoài neighbor state |
| 🏭 **Production** | Triển khai dual-stack từng VLAN một; IPv6 nửa vời gây "mạng chậm" khó tìm |

### 🔗 Liên kết

- ⬅️ [Lesson 30 — SLAAC, NDP, DHCPv6](./lesson-30-slaac-ndp-dhcpv6.md)
- 📝 [Mini Exam Phase 4](./review-phase04.md)
- ➡️ [Phase 5 — Wireless](../05-wireless/README.md)
- 📚 So sánh: [Lesson 22 — OSPF single-area](../02-routing/lesson-22-ospf-single-area.md)
