# LESSON 11 — Kiến trúc Switch · L2 vs L3 · Mô hình phân lớp

> 📌 Lesson mở màn Phase 1. Lesson 03 đã dạy switch **học MAC thế nào**.
> Lesson này trả lời: switch **được xây ra sao**, và nó **đứng ở đâu** trong một mạng doanh nghiệp.

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 03](../00-foundation/lesson-03-ethernet-mac-frame.md), [Lesson 04](../00-foundation/lesson-04-unicast-broadcast-multicast.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Phân biệt switch L2 và L3 — và biết khi nào cần cái nào
- [ ] Giải thích vì sao switch nhanh hơn router dù cùng chuyển gói
- [ ] Phân biệt switchport và routed port, biết `no switchport` làm gì
- [ ] Mô tả mô hình **Access / Distribution / Core** và vai trò từng lớp
- [ ] Đọc thông số switch khi chọn mua: PoE, uplink, stacking, MAC table size

## 2. Prerequisite

- Switch học từ source MAC, chuyển theo destination MAC *(Lesson 03)*
- Mỗi port = 1 collision domain, mỗi VLAN = 1 broadcast domain *(Lesson 04)*

---

## 3. Concept

### Bên trong một switch

| Thành phần | Vai trò |
|---|---|
| **ASIC** | Chip chuyên dụng chuyển frame ở tốc độ wire-speed. Đây là lý do switch nhanh. |
| **CAM table** | Bộ nhớ chứa MAC table. Tra cứu **một chu kỳ clock**, không phải duyệt tuần tự. |
| **TCAM** | Bộ nhớ tra cứu nâng cao — dùng cho ACL, QoS, và routing trên L3 switch |
| **CPU** | Chỉ xử lý **control plane**: STP, CDP, SSH, SNMP. Không đụng vào frame thường. |
| **Backplane / switching fabric** | Đường truyền nội bộ nối các port |

> 🔑 **Vì sao switch nhanh hơn router?**
> Switch tra **CAM table bằng phần cứng** — địa chỉ MAC là khoá chính xác, tra một phát ra ngay.
> Router phải làm **longest prefix match** trên bảng định tuyến — phức tạp hơn nhiều.
> Router hiện đại dùng CEF + TCAM để bù lại, nhưng nguyên lý vẫn vậy.

> ⚠️ Hệ quả thực tế: traffic bình thường **không chạm vào CPU switch**. Nếu CPU switch cao,
> nghĩa là có thứ bị đẩy lên control plane — loop, storm, hoặc tấn công.

### Chuyển frame — 3 cách

| Cách | Switch làm gì | Độ trễ | Frame lỗi |
|---|---|---|---|
| **Store-and-forward** | Nhận **hết** frame, kiểm FCS, rồi mới chuyển | Cao nhất | **Bị chặn** ✅ |
| **Cut-through** | Đọc 6 byte đầu (Dst MAC) là chuyển ngay | Thấp nhất | Vẫn chuyển ❌ |
| **Fragment-free** | Đọc 64 byte đầu rồi chuyển | Trung bình | Chặn được phần lớn |

> Switch Cisco hiện đại gần như đều dùng **store-and-forward** — chênh lệch độ trễ
> đã không còn đáng kể, mà lợi ích chặn frame lỗi thì rõ ràng.
>
> Đây cũng là lý do destination MAC được đặt **trước** source MAC trong frame (Lesson 03) —
> thiết kế từ thời cut-through còn quan trọng.

### L2 switch vs L3 switch vs Router

| | **L2 Switch** | **L3 Switch** | **Router** |
|---|---|---|---|
| Chuyển theo | MAC | MAC **và** IP | IP |
| Inter-VLAN routing | ❌ | ✅ (SVI) | ✅ (subinterface) |
| Tốc độ route | — | **Wire-speed** (ASIC) | Chậm hơn |
| Số port | Nhiều (24–48) | Nhiều | Ít (2–8) |
| WAN interface | ❌ | ❌ | ✅ (serial, DSL, LTE…) |
| NAT, VPN, QoS sâu | ❌ | Hạn chế | ✅ |
| Dùng ở đâu | Access layer | **Distribution / Core** | **Biên mạng, ra WAN** |

> 🔧 Quy tắc chọn đơn giản:
> **Route trong nhà → L3 switch. Ra khỏi nhà → router.**

### Switchport vs Routed port

Trên L3 switch, mỗi port có thể ở một trong hai chế độ:

```cisco
! Switchport (mặc định) — hoạt động như port switch L2
SW1(config-if)# switchport
SW1(config-if)# switchport mode access

! Routed port — hoạt động như interface router, có IP riêng
SW1(config-if)# no switchport
SW1(config-if)# ip address 10.0.1.1 255.255.255.252
```

| | Switchport | Routed port |
|---|---|---|
| Có IP riêng? | ❌ (IP nằm ở SVI) | ✅ |
| Thuộc VLAN? | ✅ | ❌ |
| Dùng cho | Nối PC, switch khác | Nối router, hoặc link L3 giữa 2 switch core |

### SVI — Switch Virtual Interface

```cisco
SW1(config)# interface vlan 10
SW1(config-if)# ip address 10.0.10.1 255.255.255.0
```

SVI là **interface ảo đại diện cho cả một VLAN**. Nó chính là **default gateway** của mọi
máy trong VLAN đó.

> ⚠️ SVI chỉ `up/up` khi: (1) VLAN **tồn tại và active**, **và** (2) có **ít nhất một port
> up** thuộc VLAN đó (access port hoặc trunk cho phép VLAN đó). Đây là nguyên nhân số 1
> của "SVI cấu hình đúng mà vẫn down".

---

## 4. Why? — vì sao cần mô hình phân lớp

> **Nếu cắm tất cả vào một switch lớn thì sao?**

| Vấn đề | Thực tế |
|---|---|
| **Không có dự phòng** | Switch chết = cả công ty mất mạng |
| **Không scale** | 300 máy không có switch nào đủ port |
| **Cáp hỗn loạn** | Kéo dây từ mọi phòng về một chỗ |
| **Một sự cố lan toàn bộ** | Loop ở tầng 3 làm chết cả tầng 1 |
| **Không có chỗ đặt chính sách** | Mọi thứ cùng một chỗ, không phân vùng được |

### Mô hình 3 lớp

```text
            ┌──────────── CORE ────────────┐
            │   Chuyển nhanh, không lọc    │
            │   SW-CORE1 ══ SW-CORE2       │
            └───────┬──────────────┬───────┘
                    │              │
         ┌──────────┴───┐    ┌─────┴────────┐
         │ DISTRIBUTION │    │ DISTRIBUTION │   ← routing, ACL, QoS
         │   SW-DIST1   │════│   SW-DIST2   │     ranh giới VLAN
         └──┬────────┬──┘    └──┬────────┬──┘
            │        │          │        │
        ┌───┴──┐ ┌───┴──┐  ┌────┴─┐ ┌────┴─┐
        │ACCESS│ │ACCESS│  │ACCESS│ │ACCESS│   ← PoE, port security, PortFast
        └──┬───┘ └──┬───┘  └───┬──┘ └───┬──┘
          PC       PC         AP       Phone
```

| Lớp | Nhiệm vụ | Tính năng tiêu biểu |
|---|---|---|
| **Access** | Nối thiết bị đầu cuối | PoE, Port Security, PortFast, BPDU Guard, voice VLAN |
| **Distribution** | **Ranh giới L2/L3**, gom access | Inter-VLAN routing, ACL, QoS, HSRP, summarization |
| **Core** | Chuyển nhanh giữa các khu | Chỉ forwarding, **không lọc gì** — tốc độ là ưu tiên duy nhất |

> 🏭 Doanh nghiệp vừa và nhỏ thường dùng **collapsed core** — gộp Distribution và Core
> làm một. Hai switch L3 ở giữa, access ở dưới. Đủ cho tới ~1000 user.

---

## 5. How does it work? — đường đi của frame qua các lớp

**PC-A (VLAN 10, tầng 1) → Server (VLAN 50, phòng server)**

| Bước | Thiết bị | Lớp | Làm gì |
|:---:|---|---|---|
| 1 | SW-ACCESS1 | Access | Nhận frame, gắn VLAN 10, tra MAC table |
| 2 | SW-ACCESS1 | Access | Không biết MAC đích → gửi lên uplink (trunk) |
| 3 | SW-DIST1 | Distribution | Frame tới **SVI VLAN 10** — đây là gateway của PC-A |
| 4 | SW-DIST1 | Distribution | **Route** sang VLAN 50, **viết lại MAC** nguồn/đích |
| 5 | SW-DIST1 | Distribution | Áp **ACL** nếu có — đây là chỗ duy nhất đặt được luật |
| 6 | SW-ACCESS2 | Access | Nhận frame VLAN 50, chuyển tới Server |

**Điểm mấu chốt:** traffic **trong cùng VLAN** chỉ chạy ở lớp Access — nhanh, không qua L3.
Traffic **giữa các VLAN** bắt buộc lên Distribution. Đó là lý do lớp Distribution
vừa là *nút cổ chai tiềm năng*, vừa là *điểm kiểm soát duy nhất*.

---

## 6. Packet Flow — so sánh L2 và L3 switching

| | Cùng VLAN (L2 switching) | Khác VLAN (L3 switching) |
|---|---|---|
| Src/Dst MAC | **Không đổi** | **Bị viết lại** |
| Src/Dst IP | Không đổi | Không đổi |
| TTL | Không đổi | **Giảm 1** |
| Qua thiết bị nào | Chỉ switch Access | Access → **Distribution (L3)** → Access |
| Có áp được ACL? | ❌ | ✅ |

> 🔑 Nhìn bảng này là thấy ngay: **TTL giảm là dấu hiệu đã qua L3.**
> `tracert` từ PC sang VLAN khác sẽ thấy 1 hop — chính là SVI của L3 switch.

---

## 7. Real-world Example

🏭 **Chọn switch cho một tầng văn phòng 40 người** — những thông số thật sự quan trọng:

| Thông số | Vì sao quan trọng |
|---|---|
| **Số port** | 40 người → 48 port. Đừng mua vừa khít, luôn dư ~20% |
| **PoE / PoE+** | Cần nếu có IP phone, AP, camera. PoE 15.4W, PoE+ 30W, PoE++ 60–100W |
| **Ngân sách PoE tổng** | Switch 48 port PoE+ **không** cấp đủ 30W cho cả 48 port cùng lúc — xem "PoE budget" |
| **Uplink** | 2 cổng SFP+ 10G để lên Distribution. 1G uplink cho 48 user là nghẽn |
| **MAC table size** | 8K–16K là đủ cho access; thiếu thì switch bắt đầu flood |
| **Stacking** | Gộp nhiều switch thành một thiết bị logic — quản lý và EtherChannel dễ hơn nhiều |
| **L2 hay L3** | Access layer chỉ cần L2 — rẻ hơn đáng kể |

🏭 **Stacking — tính năng đáng tiền nhất ở access layer**

Nhiều switch vật lý → một thiết bị logic, một IP quản trị, một file cấu hình.
Lợi ích lớn nhất: **EtherChannel vắt qua 2 switch vật lý** (cross-stack EtherChannel) →
switch chết một con, uplink vẫn chạy, **không cần đợi STP hội tụ**.

🏭 **Lỗi thiết kế hay gặp: đặt gateway ở sai lớp**

Đặt SVI (gateway) trên switch **Access** thay vì Distribution. Hậu quả: traffic giữa
2 VLAN của 2 tầng khác nhau phải đi lòng vòng; mất switch access là mất gateway
của cả VLAN; không có chỗ tập trung đặt ACL.

---

## 8. Cisco CLI

```cisco
! ───── Xem switch là loại gì, có route được không ─────
SW1# show version
SW1# show ip route                     ! báo lỗi = switch L2 thuần

! ───── Bật routing trên L3 switch — HAY BỊ QUÊN ─────
SW1(config)# ip routing

! ───── Tạo SVI (gateway cho VLAN) ─────
SW1(config)# vlan 10
SW1(config-vlan)# name SALES
SW1(config)# interface vlan 10
SW1(config-if)# description GW-VLAN10-SALES
SW1(config-if)# ip address 10.0.10.1 255.255.255.0
SW1(config-if)# no shutdown

! ───── Routed port (nối lên core bằng link L3) ─────
SW1(config)# interface GigabitEthernet1/0/48
SW1(config-if)# description L3-UPLINK-TO-CORE
SW1(config-if)# no switchport              ! ← biến thành interface router
SW1(config-if)# ip address 10.255.0.2 255.255.255.252
SW1(config-if)# no shutdown

! ───── Quay lại làm switchport ─────
SW1(config-if)# switchport

! ───── Xem thông tin phần cứng ─────
SW1# show mac address-table count         ! CAM table dùng bao nhiêu
SW1# show processes cpu sorted            ! CPU cao = có thứ bất thường
SW1# show power inline                    ! ngân sách PoE còn bao nhiêu
SW1# show switch                          ! trạng thái stack
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `ip routing` | **Bật định tuyến** trên L3 switch | ⚠️ Thiếu dòng này: SVI có IP nhưng **không route được giữa các VLAN** |
| `no switchport` | Biến port thành routed port | Mất hết cấu hình VLAN của port đó |
| `interface vlan N` | Tạo SVI | VLAN phải tồn tại trước |
| `show power inline` | PoE budget | Cắm thêm AP mà không đủ budget → port không lên |

> **Khác biệt platform:**
> - Switch **L2 thuần** (2960 đời cũ) không có `ip routing`, không tạo được SVI định tuyến —
>   chỉ có **một** SVI để quản trị.
> - **NX-OS** cần `feature interface-vlan` trước khi tạo SVI.
> - Trên IOS-XE (Catalyst 9000), `ip routing` mặc định **tắt** — vẫn phải bật tay.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip interface brief
Interface              IP-Address      OK? Method Status    Protocol
Vlan10                 10.0.10.1       YES manual up        up
Vlan20                 10.0.20.1       YES manual up        up
Vlan50                 unassigned      YES unset  down      down     ← SVI chưa có port up
GigabitEthernet1/0/48  10.255.0.2      YES manual up        up       ← routed port
GigabitEthernet1/0/1   unassigned      YES unset  up        up       ← switchport
```

**Đọc gì:**

| Dấu hiệu | Ý nghĩa |
|---|---|
| `VlanN` có IP, `up/up` | SVI hoạt động — VLAN tồn tại và có port up |
| `VlanN` `down/down` | **VLAN chưa có port nào up**, hoặc VLAN chưa tạo |
| Port vật lý **có IP** | Đó là **routed port** (`no switchport`) |
| Port vật lý `unassigned` | Switchport bình thường |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show mac address-table count
Dynamic Address Count  : 142
Static Address Count   : 0
Total Mac Addresses    : 142
Total Mac Address Space Available: 7978
```

> `Space Available` tụt về 0 → CAM table đầy → switch bắt đầu **flood mọi thứ**
> như một cái hub. Nguyên nhân: mạng quá lớn, hoặc **MAC flooding attack**.

```text
# output điển hình — tự verify trên lab của bạn
SW1# show power inline
Available:370.0(w)  Used:124.4(w)  Remaining:245.6(w)

Interface Admin  Oper       Power   Device              Class Max
--------- ------ ---------- ------- ------------------- ----- ----
Gi1/0/1   auto   on         15.4    IP Phone 7960       2     30.0
Gi1/0/2   auto   on         30.0    AIR-AP2802I         4     30.0
Gi1/0/3   auto   off        0.0     n/a                 n/a   30.0
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| SVI cấu hình đúng mà `down/down` | **VLAN chưa có port nào up** | `show vlan brief` | Gán một port vào VLAN đó, hoặc allow VLAN trên trunk |
| Các VLAN không ping được nhau dù có SVI | **Quên `ip routing`** | `show ip route` → báo lỗi hoặc trống | `ip routing` |
| `show ip route` báo lệnh không tồn tại | Switch **L2 thuần**, không route được | `show version` | Dùng router hoặc L3 switch |
| Gán IP cho port vật lý báo lỗi | Port đang là switchport | `show run interface <int>` | `no switchport` trước |
| CPU switch cao bất thường | Traffic bị đẩy lên control plane | `show processes cpu sorted` | Nghi loop/storm → `show spanning-tree` |
| Cắm AP mới không lên nguồn | **Hết PoE budget** | `show power inline` | Tắt PoE port không dùng, hoặc nâng switch |
| Switch flood mọi thứ, mạng chậm | **CAM table đầy** | `show mac address-table count` | Chia VLAN, bật Port Security |
| Mất một switch trong stack | Cáp stack lỏng, firmware lệch | `show switch` | Kiểm tra cáp, đồng bộ IOS |

---

## 11. LAB

🧪 Lesson này chưa cấu hình nhiều — bài thực hành gộp vào
**[LAB 10 — Cisco IOS CLI căn bản](../labs/README.md)** *(lesson 12)*.

Bài quan sát làm ngay được trong Packet Tracer:

1. Thêm một **Switch 3560** (L3) và một **Switch 2960** (L2) vào workspace.
2. Trên cả hai, gõ `show ip route`. So sánh kết quả → hiểu ngay khác biệt L2/L3.
3. Trên 3560: tạo VLAN 10, tạo SVI, gán IP. Xem `show ip interface brief` →
   SVI đang `down`. Gán một port vào VLAN 10, cắm PC → SVI lên `up`.
4. Trên 3560: chọn một port, gõ `no switchport` rồi `ip address`. Quan sát port biến
   thành interface L3.

## 12. Challenge

1. Bạn có L3 switch, đã tạo SVI cho VLAN 10 và 20, cả hai `up/up`, PC hai VLAN
   ping được gateway của mình nhưng **không ping được nhau**. Nguyên nhân phổ biến nhất?
2. Vì sao lớp **Core** không nên áp ACL hay QoS phức tạp?
3. Khi nào nên dùng **routed port** thay vì SVI + trunk để nối 2 switch?
4. Công ty 80 user, 2 tầng. Có cần đủ 3 lớp không? Thiết kế tối thiểu là gì?

<details>
<summary>Đáp án</summary>

**1.** **Quên `ip routing`.** Đây là lỗi số 1 với L3 switch. SVI vẫn `up/up`, PC vẫn ping
được gateway (vì cùng subnet, không cần route), nhưng switch **không chuyển gói giữa các
subnet**. Kiểm chứng: `show ip route` trống hoặc chỉ có connected mà không route.

**2.** Vì nhiệm vụ duy nhất của Core là **chuyển nhanh nhất có thể**. Áp ACL/QoS phức tạp
làm tăng độ trễ cho **toàn bộ** traffic của mạng, và biến Core thành điểm nghẽn.
Chính sách thuộc về lớp **Distribution** — nơi traffic đã được gom lại và đã có ranh giới L3.

**3.** Dùng **routed port** khi link giữa 2 switch chỉ cần chở **traffic đã route**,
không cần chở VLAN. Lợi ích:

| Routed port | Trunk + SVI |
|---|---|
| **Không có STP** trên link đó → hội tụ nhanh | STP phải tính toán |
| Không có broadcast domain vắt qua link | Broadcast đi qua trunk |
| Đơn giản, ít thứ hỏng | Phải quản lý allowed VLAN |

Điển hình: link **Distribution ↔ Core** nên là routed port. Link **Access ↔ Distribution**
phải là trunk (vì access cần chở nhiều VLAN).

**4.** **Không cần đủ 3 lớp.** 80 user dùng **collapsed core** (2 lớp):

```text
2 × L3 switch (Distribution+Core gộp, chạy HSRP)
        │
2–3 × L2 switch Access (mỗi tầng 1–2 con, PoE)
```

Đủ dự phòng, đủ chỗ đặt ACL, chi phí hợp lý. Ba lớp đầy đủ chỉ cần từ ~500–1000 user
hoặc nhiều toà nhà.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | CAM vs TCAM · 3 cách chuyển frame · 3 lớp và nhiệm vụ từng lớp | ⬜ |
| **L2** Explain | Giải thích vì sao switch nhanh hơn router | ⬜ |
| **L3** Configure | Bật `ip routing`, tạo 2 SVI, tạo 1 routed port | ⬜ |
| **L4** Troubleshoot | SVI `down/down` → nêu 2 nguyên nhân và cách xác minh | ⬜ |
| **L5** Design | Thiết kế lớp switch cho công ty 150 user, 3 tầng — vẽ sơ đồ, chọn loại switch | ⬜ |

## 14. Summary

**Key concepts**

- Switch chuyển frame bằng **ASIC + CAM table** → nhanh hơn router (longest prefix match)
- Traffic bình thường **không chạm CPU switch** → CPU cao = có bất thường
- **Store-and-forward** là mặc định hiện nay (chặn được frame lỗi)
- **L2 switch** = access · **L3 switch** = distribution/core · **router** = ra WAN
- **SVI** = gateway của một VLAN; chỉ `up` khi VLAN có **ít nhất một port up**
- `no switchport` → **routed port**, có IP riêng, không thuộc VLAN nào
- ⭐ **`ip routing` phải bật tay** trên L3 switch — quên là VLAN không thông nhau
- Mô hình: **Access** (PoE, port security) → **Distribution** (routing, ACL) → **Core** (chỉ tốc độ)
- SME dùng **collapsed core** — gộp Distribution và Core

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip routing` | **Luôn bật đầu tiên** trên L3 switch |
| `interface vlan N` + `ip address` | Tạo gateway cho VLAN |
| `no switchport` | Biến port thành interface L3 |
| `show ip interface brief` | SVI nào up, port nào là routed |
| `show mac address-table count` | CAM table còn chỗ không |
| `show power inline` | PoE budget |
| `show processes cpu sorted` | CPU cao = nghi loop/storm |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `ip routing` | SVI up nhưng VLAN không thông nhau |
| Tưởng SVI down là do cấu hình sai | Thường là VLAN chưa có port nào up |
| Gán IP cho switchport | Phải `no switchport` trước |
| Đặt gateway ở lớp Access | Traffic đi lòng vòng, mất switch là mất gateway |
| Áp ACL phức tạp ở Core | Biến Core thành điểm nghẽn |
| Mua switch PoE không xem **PoE budget** | Không cấp đủ nguồn cho hết số port |

## 15. Homework + cập nhật PROGRESS

1. Trong Packet Tracer: làm đủ 4 bước ở mục 11.
2. Vẽ sơ đồ mạng công ty bạn, gán nhãn từng switch thuộc lớp nào.
3. Tra datasheet một switch Cisco bất kỳ (vd C9200-48P), tìm: số port, PoE budget,
   uplink, MAC table size, có stack được không.

```markdown
- [YYYY-MM-DD] Lesson 11 — Kiến trúc switch: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | L2 vs L3 switch, SVI, routed port, 3 lớp Access/Distribution/Core |
| 🔧 **Engineer** | `ip routing` bật tay; routed port cho uplink L3; đọc PoE budget khi lắp AP |
| 🏭 **Production** | CPU switch cao = loop/storm; CAM đầy = switch hoá hub; stacking để EtherChannel vắt 2 switch |

### 🔗 Liên kết

- ⬅️ [Lesson 10 — IPv6 giới thiệu](../00-foundation/lesson-10-ipv6-gioi-thieu.md)
- ➡️ [Lesson 12 — Cisco IOS CLI](./lesson-12-cisco-ios-cli.md)
- 🔜 SVI dùng để inter-VLAN routing ở [Lesson 14](./lesson-14-inter-vlan-routing.md)
- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md)
