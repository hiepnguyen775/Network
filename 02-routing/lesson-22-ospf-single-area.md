# LESSON 22 — OSPF Single-Area: Neighbor · States · DR/BDR ⭐

> 📌 Lesson quan trọng nhất của Phase 2. Phần lớn thời gian troubleshoot routing
> trong đời thực là **"vì sao OSPF không lên neighbor"** — và lesson này trả lời câu đó.

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~4 giờ |
| **Prerequisite** | [Lesson 20](./lesson-20-ad-metric-longest-prefix.md), [Lesson 21](./lesson-21-dynamic-routing-rip.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Cấu hình OSPF single-area, hiểu `network ... wildcard ... area`
- [ ] Thuộc **7 neighbor state** và biết kẹt ở mỗi state nghĩa là gì
- [ ] Liệt kê **6 thứ phải khớp** để OSPF lên neighbor
- [ ] Giải thích **DR/BDR** sinh ra để làm gì và bầu thế nào
- [ ] Troubleshoot "OSPF không lên neighbor" theo đúng thứ tự, không đoán mò

## 2. Prerequisite

- Link-State vs Distance Vector *(Lesson 21)*
- Wildcard mask *(Lesson 02, Lesson 07)*
- AD của OSPF = 110 *(Lesson 20)*

---

## 3. Concept

### OSPF là gì

| Đặc điểm | Giá trị |
|---|---|
| Loại | **Link-State**, IGP, chuẩn mở (IETF) |
| Thuật toán | **Dijkstra (SPF)** |
| Metric | **Cost** |
| AD | **110** |
| Chạy trên | **IP protocol 89** *(không có port)* |
| Multicast | `224.0.0.5` (all OSPF routers) · `224.0.0.6` (DR/BDR) |
| Hỗ trợ VLSM | ✅ |

### Năm loại gói OSPF

| Type | Tên | Dùng để |
|:---:|---|---|
| **1** | **Hello** | Tìm và duy trì neighbor |
| **2** | DBD (Database Description) | Tóm tắt nội dung LSDB của mình |
| **3** | LSR (Link-State Request) | "Cho tôi xin LSA này" |
| **4** | LSU (Link-State Update) | Gửi LSA thật |
| **5** | LSAck | Xác nhận đã nhận |

### Bảy neighbor state — thuộc theo thứ tự

| # | State | Nghĩa | Kẹt ở đây = nghi gì |
|:---:|---|---|---|
| 1 | **Down** | Chưa nhận hello nào | Interface down, ACL chặn, passive-interface |
| 2 | **Init** | Nhận hello nhưng **chưa thấy mình** trong đó | **Một chiều** không thông — ACL, passive một bên |
| 3 | **2-Way** | Hai bên đã thấy nhau | ✅ **Bình thường** giữa 2 DROTHER |
| 4 | **ExStart** | Bầu master/slave, trao seq number | ⚠️ **MTU mismatch** |
| 5 | **Exchange** | Trao đổi DBD | ⚠️ **MTU mismatch** |
| 6 | **Loading** | Gửi LSR/LSU lấy LSA còn thiếu | Hiếm khi kẹt |
| 7 | **FULL** | ✅ **Đồng bộ hoàn toàn** | Trạng thái đích |

> ⭐ **Hai state kết thúc hợp lệ:**
> - **FULL** — với DR, BDR, và trên link point-to-point
> - **2-WAY** — giữa hai **DROTHER** trên link multi-access. **Đây là bình thường, không phải lỗi.**

### Sáu thứ phải khớp để lên neighbor

| # | Phải khớp | Kiểm tra bằng |
|:---:|---|---|
| 1 | **Cùng subnet** (và cùng mask) | `show run interface <int>` |
| 2 | **Area ID** | `show ip ospf interface <int>` |
| 3 | **Hello / Dead timer** | `show ip ospf interface <int>` |
| 4 | **Authentication** | `show ip ospf interface <int>` |
| 5 | **MTU** | `show interfaces <int>` |
| 6 | **Không bị passive-interface** | `show ip protocols` |

Và **Router ID phải KHÁC nhau** — trùng là hỏng.

> 🔑 Học thuộc danh sách này. Nó là checklist bạn sẽ chạy qua hàng trăm lần trong đời.

### Router ID — chọn thế nào

```text
1. Lệnh router-id cấu hình tay       ← ưu tiên cao nhất
2. IP cao nhất của interface LOOPBACK đang up
3. IP cao nhất của interface vật lý đang up
```

> 🔧 **Luôn đặt tay hoặc dùng loopback.** Router ID lấy từ interface vật lý sẽ **đổi**
> khi interface đó down → OSPF reset toàn bộ neighbor. Loopback không bao giờ down.

```cisco
R1(config)# interface Loopback0
R1(config-if)# ip address 1.1.1.1 255.255.255.255
R1(config)# router ospf 1
R1(config-router)# router-id 1.1.1.1
```

### Network type & DR/BDR

| Network type | Khi nào | Bầu DR/BDR? | Hello/Dead |
|---|---|:---:|---|
| **Broadcast** | Ethernet *(mặc định)* | ✅ **Có** | 10 / 40 giây |
| **Point-to-point** | Serial, hoặc cấu hình tay | ❌ **Không** | 10 / 40 giây |
| Non-broadcast (NBMA) | Frame Relay *(hiếm)* | ✅ Có | 30 / 120 giây |

### DR/BDR — vì sao cần

Trên link multi-access có **N router**, nếu mọi cặp đều peer đầy đủ:

```text
Số adjacency = N × (N−1) / 2

5 router  → 10 adjacency
10 router → 45 adjacency  😱
```

Mỗi adjacency phải đồng bộ LSDB → tốn CPU và băng thông khủng khiếp.

**Giải pháp:** bầu một **DR** (Designated Router) và một **BDR** (backup).
Mọi router chỉ peer **FULL với DR và BDR**. Giữa các DROTHER với nhau: dừng ở **2-WAY**.

```text
5 router → chỉ còn 2×(5−2) + 1 = 7 adjacency
```

### Bầu DR/BDR

```text
1. OSPF interface PRIORITY cao nhất thắng   (mặc định 1; priority 0 = KHÔNG tham gia)
2. Hoà → ROUTER ID cao nhất thắng
```

> ⚠️ **Không có preemption.** DR đã bầu rồi thì **giữ nguyên**, kể cả khi sau đó có router
> priority cao hơn lên. Muốn đổi DR phải `clear ip ospf process` hoặc reset link.
>
> Đây là chỗ gây bất ngờ thường xuyên: bạn đặt priority cao cho router core nhưng DR
> vẫn là con router cũ, vì nó lên trước.

### Cost

```text
Cost = reference bandwidth / bandwidth của interface

Mặc định reference bandwidth = 100 Mbps (100.000.000 bps)
```

| Interface | Bandwidth | Cost |
|---|---|:---:|
| Serial 1.544 Mbps | 1544 kbps | **64** |
| Ethernet 10 Mbps | 10 Mbps | **10** |
| FastEthernet 100 Mbps | 100 Mbps | **1** |
| GigabitEthernet 1 Gbps | 1 Gbps | **1** ⚠️ |
| TenGig 10 Gbps | 10 Gbps | **1** ⚠️ |

> ⚠️ **Vấn đề lớn:** mọi link từ 100 Mbps trở lên đều có cost = **1**.
> OSPF không phân biệt được link 100 Mbps với link 10 Gbps!
>
> **Sửa:** tăng reference bandwidth — và phải làm **trên MỌI router**:
> ```cisco
> R1(config-router)# auto-cost reference-bandwidth 100000   ! đơn vị Mbps → 100 Gbps
> ```

---

## 4. Why?

> **Vì sao OSPF thắng RIP?**

| Vấn đề của RIP | OSPF giải quyết thế nào |
|---|---|
| Metric = hop count | **Cost theo băng thông** — chọn đường thật sự nhanh |
| Max 15 hop | **Không giới hạn** hop |
| Hội tụ vài phút | **Vài giây** — flood LSA ngay khi có thay đổi |
| Update định kỳ 30 giây | Chỉ gửi khi **có thay đổi** (+ hello nhẹ mỗi 10 giây) |
| Không scale | **Chia area** → scale tới hàng trăm router |
| Chống loop bằng mẹo (split horizon…) | Mỗi router có **bản đồ đầy đủ** → tự tính, không loop |

> **Vì sao OSPF phức tạp hơn?**

Vì nó làm nhiều việc hơn: duy trì LSDB, bầu DR/BDR, chạy SPF, quản lý area.
Cái giá của sự thông minh.

---

## 5. How does it work? — từ lúc bật tới khi có route

```text
1. Bật OSPF trên interface
2. Gửi HELLO ra 224.0.0.5 (mỗi 10 giây trên Ethernet)
3. Nhận hello từ láng giềng → state DOWN → INIT
4. Thấy Router ID của mình trong hello của láng giềng → 2-WAY
5. Nếu là link multi-access: BẦU DR/BDR
   ├─ Là DROTHER–DROTHER → DỪNG ở 2-WAY (bình thường!)
   └─ Với DR/BDR → đi tiếp
6. EXSTART: bầu master/slave, thống nhất sequence number
7. EXCHANGE: trao đổi DBD (mục lục LSDB của nhau)
8. LOADING: gửi LSR xin những LSA mình còn thiếu, nhận LSU
9. FULL: hai bên có LSDB giống hệt nhau ✅
10. Chạy thuật toán SPF (Dijkstra) trên LSDB → tính cây đường đi ngắn nhất
11. Nạp kết quả vào routing table
```

> 🔑 Bước 10 là mấu chốt: **mỗi router tự tính** từ cùng một LSDB.
> Vì LSDB giống hệt nhau, mọi router tính ra cùng một bản đồ nhất quán — **không có loop**.

### `network` statement — hiểu đúng

```cisco
R1(config-router)# network 10.0.1.0 0.0.0.255 area 0
```

Câu lệnh này nghĩa là:

> *"Interface nào có IP khớp `10.0.1.x` thì: (a) **bật OSPF** trên nó, và
> (b) **quảng bá** subnet của nó vào area 0."*

**Hai tác dụng, không phải một.** Đây là chỗ hay hiểu nhầm.

| Wildcard | Khớp gì |
|---|---|
| `0.0.0.255` | Cả subnet `/24` |
| `0.0.0.0` | **Đúng một IP** — cách chính xác nhất |
| `0.0.255.255` | Cả `/16` |
| `255.255.255.255` | **Mọi** interface |

> 🔧 Cách an toàn và rõ ràng nhất: khai **từng interface một** bằng wildcard `0.0.0.0`.
> ```cisco
> network 10.0.1.1 0.0.0.0 area 0
> network 10.0.12.1 0.0.0.0 area 0
> ```
> Không bao giờ bật nhầm OSPF trên interface không mong muốn.

---

## 6. Packet Flow — Hello packet chứa gì

| Trường | Phải khớp? |
|---|:---:|
| Router ID | ❌ (phải **khác** nhau) |
| **Area ID** | ✅ |
| **Hello interval** | ✅ |
| **Dead interval** | ✅ |
| **Authentication** | ✅ |
| **Subnet mask** | ✅ |
| Stub area flag | ✅ |
| DR / BDR | ❌ (thông tin) |
| Neighbor list | ❌ (thông tin — dùng để lên 2-WAY) |

> 🔑 Trường **Neighbor list** là cơ chế lên 2-WAY: R1 gửi hello chứa "tôi thấy R2".
> R2 nhận, thấy tên mình → biết kết nối **hai chiều** đã thông → chuyển sang 2-WAY.
> Nếu R2 không thấy tên mình → kẹt ở **INIT** → nghĩa là chiều R2→R1 không thông.

---

## 7. Real-world Example

🏭 **Cấu hình OSPF chuẩn cho một router**

```cisco
R1(config)# interface Loopback0
R1(config-if)# ip address 1.1.1.1 255.255.255.255
R1(config-if)# exit

R1(config)# router ospf 1
R1(config-router)# router-id 1.1.1.1
R1(config-router)# auto-cost reference-bandwidth 100000
R1(config-router)# passive-interface default
R1(config-router)# no passive-interface GigabitEthernet0/1
R1(config-router)# network 10.0.1.1 0.0.0.0 area 0
R1(config-router)# network 10.0.12.1 0.0.0.0 area 0
```

Năm thói quen trong đoạn này:

| Dòng | Vì sao |
|---|---|
| Loopback + `router-id` | Router ID ổn định, không đổi khi interface down |
| `auto-cost reference-bandwidth 100000` | Phân biệt được link 1G và 10G. **Phải đặt giống nhau mọi router** |
| `passive-interface default` | Mặc định **không gửi hello** ra đâu cả |
| `no passive-interface Gi0/1` | Chỉ bật ở đúng interface nối router |
| `network ... 0.0.0.0 area 0` | Khai từng interface, không bật nhầm |

🏭 **Lỗi thật: OSPF lộ ra mạng người dùng**

Quên `passive-interface` trên port nối PC → router gửi hello ra đó. Hậu quả:

- Tốn băng thông vô ích
- **Ai cắm laptop vào cũng nhận được hello** → biết topology, thậm chí **giả làm router OSPF**
  và bơm route giả vào mạng

> 🔧 Phòng chống: `passive-interface default` + OSPF authentication.

🏭 **DR nằm sai chỗ**

Để mặc định priority 1, DR được bầu theo **Router ID cao nhất** — thường là ngẫu nhiên.
Nếu DR rơi vào một router nhỏ/yếu, nó phải gánh việc đồng bộ LSDB cho cả segment.

```cisco
! Ép router core làm DR
R-CORE(config-if)# ip ospf priority 255

! Ép router không bao giờ làm DR
R-SMALL(config-if)# ip ospf priority 0
```

---

## 8. Cisco CLI

```cisco
! ───── Cấu hình cơ bản ─────
R1(config)# router ospf 1                     ! "1" = process ID, CỤC BỘ
R1(config-router)# router-id 1.1.1.1
R1(config-router)# network 10.0.12.1 0.0.0.0 area 0
R1(config-router)# passive-interface default
R1(config-router)# no passive-interface GigabitEthernet0/1

! ───── Cấu hình trên interface (cách hiện đại, IOS-XE) ─────
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip ospf 1 area 0               ! thay cho network statement

! ───── Tinh chỉnh ─────
R1(config-if)# ip ospf cost 10                ! ép cost
R1(config-if)# ip ospf priority 255           ! ép làm DR
R1(config-if)# ip ospf priority 0             ! không bao giờ làm DR
R1(config-if)# ip ospf hello-interval 5       ! phải khớp 2 đầu
R1(config-if)# ip ospf dead-interval 20
R1(config-if)# ip ospf network point-to-point ! tắt bầu DR/BDR trên Ethernet
R1(config-router)# auto-cost reference-bandwidth 100000

! ───── Default route ─────
R1(config-router)# default-information originate

! ───── Kiểm tra ─────
R1# show ip ospf neighbor
R1# show ip ospf interface GigabitEthernet0/1
R1# show ip ospf
R1# show ip protocols
R1# show ip route ospf

! ───── Reset (mất kết nối tạm thời!) ─────
R1# clear ip ospf process
```

| Lệnh | Lưu ý |
|---|---|
| `router ospf 1` | Process ID **cục bộ** — hai router **không cần** trùng |
| `network <ip> 0.0.0.0 area 0` | ⭐ Cách rõ ràng nhất |
| `ip ospf 1 area 0` trên interface | Cách hiện đại, dễ đọc hơn `network` |
| `ip ospf network point-to-point` | Trên link Ethernet chỉ có 2 router → **bỏ bầu DR**, hội tụ nhanh hơn |
| `clear ip ospf process` | ⚠️ **Gián đoạn mạng** — chỉ dùng khi cần |

> **Khác biệt platform:** NX-OS cần `feature ospf`, và cấu hình OSPF **trên interface**
> (`ip router ospf 1 area 0`), không dùng `network` statement.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address      Interface
2.2.2.2           1   FULL/DR         00:00:35    10.0.12.2    GigabitEthernet0/1
3.3.3.3           1   FULL/BDR        00:00:33    10.0.12.3    GigabitEthernet0/1
4.4.4.4           1   2WAY/DROTHER    00:00:31    10.0.12.4    GigabitEthernet0/1
```

**Đọc gì:**

| Cột | Ý nghĩa | Bất thường |
|---|---|---|
| `Neighbor ID` | **Router ID** của láng giềng | Trùng với Router ID của mình → hỏng |
| `Pri` | OSPF priority | `0` = không tham gia bầu DR |
| `State` | Trạng thái + vai trò | Xem bảng dưới |
| `Dead Time` | Còn bao lâu thì coi là chết | **Không reset** (đếm về 0) → không nhận được hello |
| `Address` | IP của láng giềng | |

| `State` | Bình thường? |
|---|---|
| `FULL/DR`, `FULL/BDR` | ✅ Đúng |
| `FULL/-` *(point-to-point)* | ✅ Đúng |
| **`2WAY/DROTHER`** | ✅ **Đúng** — không phải lỗi |
| `INIT` | ❌ Một chiều không thông |
| `EXSTART` / `EXCHANGE` | ❌ Gần như luôn là **MTU mismatch** |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip ospf interface GigabitEthernet0/1
GigabitEthernet0/1 is up, line protocol is up
  Internet Address 10.0.12.1/24, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1
  Designated Router (ID) 2.2.2.2, Interface address 10.0.12.2
  Backup Designated router (ID) 3.3.3.3, Interface address 10.0.12.3
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
  Neighbor Count is 3, Adjacent neighbor count is 2
```

> 🔑 Đây là **lệnh quan trọng nhất** khi debug OSPF — nó hiển thị cùng lúc
> **Area, Network Type, Cost, Hello/Dead timer** — tức là 4 trong 6 thứ phải khớp.
> So output này ở hai đầu là ra ngay vấn đề.

---

## 10. Troubleshooting — thứ tự 9 bước

> 🔴 **Học thuộc thứ tự này.** Nó tiết kiệm cho bạn hàng giờ.

| # | Kiểm tra | Lệnh | Triệu chứng nếu sai |
|:---:|---|---|---|
| 1 | Interface `up/up`? | `show ip interface brief` | State `Down`, không có neighbor |
| 2 | Hai đầu **cùng subnet**? | `show run interface <int>` | Không lên neighbor |
| 3 | **Area** khớp? | `show ip ospf interface <int>` | Không lên neighbor |
| 4 | **Hello/Dead timer** khớp? | `show ip ospf interface <int>` | Không lên neighbor |
| 5 | **MTU** khớp? | `show interfaces <int>` | Kẹt **EXSTART/EXCHANGE** |
| 6 | **Authentication** khớp? | `show ip ospf interface <int>` | Không lên neighbor |
| 7 | Interface có bị **passive**? | `show ip protocols` | State `Down` hoặc `INIT` |
| 8 | **Router ID trùng**? | `show ip ospf` ở 2 router | Neighbor nhấp nháy, log cảnh báo |
| 9 | **Network type** khớp? | `show ip ospf interface <int>` | Không lên, hoặc lên rồi rớt |

### Bảng triệu chứng → nguyên nhân

| Triệu chứng | Nguyên nhân phổ biến nhất |
|---|---|
| Không có neighbor nào | Interface down · passive-interface · thiếu `network` statement |
| Kẹt **INIT** | Một chiều không thông — ACL chặn `224.0.0.5`, hoặc passive một bên |
| Kẹt **EXSTART/EXCHANGE** | ⭐ **MTU mismatch** |
| Lên **FULL** rồi rớt liên tục | Link chập chờn · MTU · Router ID trùng |
| FULL nhưng **không có route** | Thiếu `network` statement cho mạng đó · `passive-interface` |
| Route có nhưng đi đường chậm | Cost mặc định — mọi link ≥ 100M đều cost 1 → đặt `auto-cost reference-bandwidth` |
| `2WAY/DROTHER` | ✅ **Bình thường** — không phải lỗi |

```cisco
! Debug khi cần (CẨN THẬN trên production)
R1# debug ip ospf adj
R1# debug ip ospf hello
R1# undebug all
```

---

## 11. LAB

🧪 **[LAB 23 — OSPF single-area: neighbor, DR/BDR, đọc LSDB](../labs/lab23-ospf-single-area.md)**

## 12. Challenge

1. Hai router nối Ethernet, cấu hình OSPF đúng hết nhưng neighbor kẹt ở **EXSTART**.
   Nguyên nhân là gì? Kiểm chứng bằng lệnh nào?
2. R1 và R2 đều hiện neighbor nhưng R1 thấy `INIT`. Chuyện gì đang xảy ra?
3. Trên một segment Ethernet có 4 router. `show ip ospf neighbor` trên R1 (DROTHER)
   hiển thị bao nhiêu dòng, với state gì?
4. Bạn có link 1 Gbps và link 10 Gbps song song. OSPF chọn đường nào? Vì sao? Sửa thế nào?

<details>
<summary>Đáp án</summary>

**1.** **MTU mismatch.** Trong bước EXCHANGE, hai router trao đổi gói DBD. Nếu MTU khác nhau,
một bên gửi gói lớn hơn bên kia nhận được → DBD không hoàn tất → kẹt vĩnh viễn ở
EXSTART/EXCHANGE.

Kiểm chứng:

```cisco
R1# show interfaces GigabitEthernet0/1 | include MTU
R2# show interfaces GigabitEthernet0/1 | include MTU
```

Sửa: đặt MTU giống nhau, hoặc (tạm bợ) `ip ospf mtu-ignore` trên interface — nhưng
cách đúng là sửa MTU.

**2.** R1 ở `INIT` nghĩa là: **R1 nhận được hello của R2**, nhưng trong hello đó
**không có Router ID của R1** trong danh sách neighbor.

Suy ra: **chiều R1 → R2 không thông**. R2 chưa bao giờ nghe được R1.

Nguyên nhân thường gặp:

| Nguyên nhân | Kiểm chứng |
|---|---|
| ACL trên R2 chặn multicast `224.0.0.5` | `show access-lists` trên R2 |
| R2 có `passive-interface` trên interface đó | `show ip protocols` trên R2 |
| Lỗi một chiều ở tầng vật lý (hiếm) | `show interfaces` counter |

**3.** R1 là DROTHER, có 3 láng giềng (DR, BDR, và 1 DROTHER khác):

```text
Neighbor ID   Pri  State
2.2.2.2        1   FULL/DR          ← peer đầy đủ với DR
3.3.3.3        1   FULL/BDR         ← peer đầy đủ với BDR
4.4.4.4        1   2WAY/DROTHER     ← chỉ 2-WAY, KHÔNG peer đầy đủ
```

**3 dòng.** Hai FULL, một 2WAY. Đây chính là cơ chế DR/BDR giảm số adjacency.

**4.** OSPF chọn **ngẫu nhiên hoặc ECMP cả hai** — vì cả hai đều có **cost = 1**!

```text
Cost = 100 Mbps / 1 Gbps  = 0.1 → làm tròn lên 1
Cost = 100 Mbps / 10 Gbps = 0.01 → làm tròn lên 1
```

Reference bandwidth mặc định 100 Mbps quá nhỏ cho mạng hiện đại.

**Sửa** — và phải làm **trên MỌI router** trong mạng:

```cisco
R1(config-router)# auto-cost reference-bandwidth 100000    ! đơn vị Mbps = 100 Gbps
```

Kết quả: link 1G cost = `100000/1000 = 100`; link 10G cost = `100000/10000 = 10` → chọn đúng.

⚠️ Đặt khác nhau giữa các router gây tính cost bất đối xứng → đường đi không tối ưu
và khó debug.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 7 state · 6 thứ phải khớp · multicast OSPF · AD · cách chọn Router ID | ⬜ |
| **L2** Explain | Giải thích DR/BDR sinh ra để làm gì, bằng công thức số adjacency | ⬜ |
| **L3** Configure | OSPF 3 router single-area, loopback làm Router ID, passive-interface | ⬜ |
| **L4** Troubleshoot | Neighbor kẹt EXSTART → tìm ra MTU mismatch | ⬜ |
| **L5** Design | Thiết kế OSPF cho 6 router, chọn DR, đặt reference bandwidth | ⬜ |

## 14. Summary

**Key concepts**

- OSPF: **Link-State**, AD **110**, metric **cost**, IP protocol **89**, `224.0.0.5`/`224.0.0.6`
- 7 state: `Down → Init → 2-Way → ExStart → Exchange → Loading → FULL`
- ⭐ **2-WAY giữa 2 DROTHER là BÌNH THƯỜNG**, không phải lỗi
- ⭐ **Kẹt EXSTART/EXCHANGE = MTU mismatch**
- ⭐ **Kẹt INIT = một chiều không thông**
- 6 thứ phải khớp: **subnet · area · hello/dead · auth · MTU · không passive**
- Router ID: `router-id` tay → loopback cao nhất → interface vật lý cao nhất
- DR/BDR giảm adjacency từ `N(N−1)/2` xuống còn `2(N−2)+1`
- Bầu DR: **priority cao nhất** → hoà thì **Router ID cao nhất**. **Không preemption**
- ⚠️ Cost mặc định: mọi link ≥ 100 Mbps đều cost **1** → phải `auto-cost reference-bandwidth`
- `network X Y area Z` vừa **bật OSPF** vừa **quảng bá** subnet đó

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip ospf neighbor` | ⭐ Đầu tiên khi debug OSPF |
| `show ip ospf interface <int>` | ⭐ Thấy Area, Network Type, Cost, Timer cùng lúc |
| `show ip ospf` | Router ID, số area |
| `show ip protocols` | Network statement, passive-interface |
| `network <ip> 0.0.0.0 area 0` | Khai từng interface — rõ ràng nhất |
| `auto-cost reference-bandwidth 100000` | **Mọi router** phải giống nhau |
| `ip ospf network point-to-point` | Bỏ bầu DR trên link Ethernet 2 router |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Hoảng khi thấy `2WAY/DROTHER` | Đó là bình thường |
| Dùng subnet mask thay wildcard trong `network` | OSPF chạy sai interface |
| Không đặt Router ID | Đổi khi interface down → reset toàn bộ neighbor |
| Quên `auto-cost reference-bandwidth` | Link 10G và 100M cùng cost 1 |
| Đặt reference-bandwidth khác nhau giữa các router | Cost bất đối xứng, khó debug |
| Quên `passive-interface` | Lộ topology, ai cũng giả router được |
| Nghĩ DR có preemption | DR đã bầu thì giữ nguyên |

## 15. Homework + cập nhật PROGRESS

1. Làm [LAB 23](../labs/lab23-ospf-single-area.md) đầy đủ, kể cả BREAK.
2. Học thuộc **7 state** và **6 thứ phải khớp** — viết ra giấy không nhìn.
3. Trên lab: đổi MTU một đầu → quan sát neighbor kẹt EXSTART. Đây là trải nghiệm
   đáng giá nhất của lesson.
4. So thời gian hội tụ OSPF với con số RIP bạn đo ở Lesson 21.

```markdown
- [YYYY-MM-DD] Lesson 22 — OSPF single-area: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 7 state, 6 thứ phải khớp, DR/BDR election, cost, Router ID |
| 🔧 **Engineer** | Loopback làm Router ID; `passive-interface default`; `network ... 0.0.0.0`; reference-bandwidth |
| 🏭 **Production** | MTU mismatch là lỗi số 1; DR nằm sai chỗ; OSPF không authentication = ai cũng bơm route giả được |

### 🔗 Liên kết

- ⬅️ [Lesson 21 — Dynamic Routing & RIP](./lesson-21-dynamic-routing-rip.md)
- ➡️ [Lesson 23 — OSPF Cost, LSDB, LSA](./lesson-23-ospf-cost-lsdb-lsa.md)
- 🧪 [LAB 23](../labs/lab23-ospf-single-area.md)
- 🔜 Sâu hơn: [`CCNP-Encor` Module 04A](https://github.com/hiepnguyen775/CCNP-Encor)
