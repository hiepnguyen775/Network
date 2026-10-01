# LESSON 07 — VLSM nâng cao · Thiết kế IP Plan

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 02](./lesson-02-ipv4-va-subnetting.md) — subnetting phải thành phản xạ trước |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Chia VLSM cho 8–10 nhu cầu khác nhau mà **không chồng lấn, không phân mảnh**
- [ ] Giải thích vì sao phải **cấp lớn trước** — bằng ví dụ cụ thể, không học thuộc
- [ ] Thiết kế IP plan có **dự phòng tăng trưởng** và có chỗ cho VLAN mới
- [ ] Biết route summarization là gì và vì sao IP plan tốt làm nó khả thi
- [ ] Viết được một tài liệu `ip-plan.md` bàn giao được cho người khác

## 2. Prerequisite

- Magic number, block size, tính Network/Broadcast trong đầu *(Lesson 02)*
- Subnet = một broadcast domain *(Lesson 04)*

---

## 3. Concept

### VLSM là gì

**VLSM** (Variable Length Subnet Mask) = dùng **nhiều độ dài prefix khác nhau** trong cùng
một dải địa chỉ, mỗi subnet to vừa đúng nhu cầu của nó.

```text
KHÔNG VLSM (cố định /26 cho mọi thứ):
  Sales     50 host  →  /26 (62)   ✅ vừa
  IT        25 host  →  /26 (62)   ⚠️ phí 37 địa chỉ
  WAN link   2 host  →  /26 (62)   ❌ phí 60 địa chỉ!

CÓ VLSM:
  Sales     50 host  →  /26 (62)
  IT        25 host  →  /27 (30)
  WAN link   2 host  →  /30 (2)    ✅ không phí gì
```

### Quy tắc vàng: cấp LỚN trước

Subnet `/26` chỉ bắt đầu được ở **bội số của 64**: `.0`, `.64`, `.128`, `.192`.
Subnet `/28` chỉ bắt đầu ở bội số của 16. Đây là ràng buộc toán học, không phải quy ước.

**Cấp sai thứ tự:**

```text
Kế toán /28 trước  →  chiếm .0 → .15
Sales   /26 sau    →  KHÔNG thể bắt đầu ở .16 (không phải bội số 64)
                   →  phải nhảy lên .64
                   →  PHÍ .16 → .63  =  48 địa chỉ bỏ không
```

**Cấp đúng thứ tự:**

```text
Sales   /26 trước  →  .0   → .63
Kế toán /28 sau    →  .64  → .79     ✅ khít
```

> 🔑 Đây là lý do duy nhất của quy tắc "lớn trước". Không phải mẹo — là hệ quả của
> việc subnet phải căn theo bội số của block size.

---

## 4. Why? — tại sao IP plan quan trọng hơn bạn tưởng

> **Nếu chia bừa, sau này sửa thì sao?**

| Phải sửa gì | Mức độ đau |
|---|---|
| DHCP pool trên router/server | Dễ |
| IP tĩnh của server, máy in, camera | Phải vào từng thiết bị |
| ACL ở mọi firewall và router | Rất dễ sót một dòng → sự cố bảo mật |
| Static route, OSPF network statement | Phải đồng bộ nhiều thiết bị |
| NAT rule | Dễ sót |
| Tài liệu, monitoring, backup script | Luôn bị quên |

> 🏭 Đổi subnet của một VLAN đang chạy trong doanh nghiệp là việc **phải làm ngoài giờ,
> có kế hoạch rollback**. Chia đúng ngay từ đầu rẻ hơn rất nhiều lần.

Ngoài ra, IP plan tốt cho bạn thứ này **miễn phí**:

### Route summarization

```text
Chia lộn xộn:                      Chia có quy hoạch:
10.0.3.0/24  Hà Nội                10.1.0.0/24  ─┐
10.0.7.0/24  Hà Nội                10.1.1.0/24   ├─ Hà Nội  → gom thành 10.1.0.0/22
10.0.2.0/24  Sài Gòn               10.1.2.0/24   │
10.0.9.0/24  Hà Nội                10.1.3.0/24  ─┘
                                   10.2.0.0/24  ─┐
→ không gom được                   10.2.1.0/24   ├─ Sài Gòn → gom thành 10.2.0.0/22
→ bảng định tuyến phình to                       ┘
```

Gom route (summarization) làm bảng định tuyến nhỏ lại, hội tụ nhanh hơn, và một sự cố
ở chi nhánh không làm rung chuyển cả mạng. Bạn học sâu ở Phase 2 và CCNP — nhưng
**nó chỉ khả thi nếu IP plan được quy hoạch từ đầu**.

---

## 5. How does it work? — Quy trình 6 bước

### Bước 1 — Liệt kê nhu cầu, cộng dự phòng

| Nhu cầu | Hiện tại | +30% dự phòng | Prefix cần |
|---|:---:|:---:|:---:|
| Sales | 50 | 65 | `/25` (126) |
| IT | 25 | 33 | `/26` (62) |
| Kế toán | 12 | 16 | `/27` (30) |
| Server | 20 | 26 | `/27` (30) |
| Guest | 40 | 52 | `/26` (62) |
| Management | 10 | 13 | `/28` (14) |
| WAN link × 2 | 2 | 2 | `/30` × 2 |

> 📏 **Dự phòng bao nhiêu?** 30% là con số thực tế cho văn phòng. Với VLAN server hoặc
> IoT/camera đang mở rộng, cân nhắc 50–100%. Với WAN link point-to-point: **0%** — nó
> không bao giờ cần hơn 2 địa chỉ.

### Bước 2 — Sắp xếp giảm dần

```text
/25 (Sales) → /26 (IT) → /26 (Guest) → /27 (Kế toán) → /27 (Server)
→ /28 (Mgmt) → /30 (WAN1) → /30 (WAN2)
```

### Bước 3 — Cấp tuần tự từ địa chỉ thấp

Giả sử được cấp `10.0.0.0/23` (512 địa chỉ):

| VLAN | Tên | Prefix | Network | Dải host | Broadcast |
|:---:|---|:---:|---|---|---|
| 10 | SALES | `/25` | `10.0.0.0` | `.1` – `.126` | `.127` |
| 20 | IT | `/26` | `10.0.0.128` | `.129` – `.190` | `.191` |
| 30 | GUEST | `/26` | `10.0.0.192` | `.193` – `.254` | `.255` |
| 40 | KETOAN | `/27` | `10.0.1.0` | `.1` – `.30` | `.31` |
| 50 | SERVER | `/27` | `10.0.1.32` | `.33` – `.62` | `.63` |
| 99 | MGMT | `/28` | `10.0.1.64` | `.65` – `.78` | `.79` |
| — | WAN1 | `/30` | `10.0.1.80` | `.81` – `.82` | `.83` |
| — | WAN2 | `/30` | `10.0.1.84` | `.85` – `.86` | `.87` |

**Còn trống:** `10.0.1.88` → `10.0.1.255` = **168 địa chỉ** cho VLAN mới sau này.

### Bước 4 — Quy ước gán địa chỉ trong subnet

Thống nhất **toàn hệ thống**, không mỗi nơi một kiểu:

| Vị trí | Dùng cho |
|---|---|
| `.1` (first usable) | **Gateway** (SVI / router) |
| `.2` – `.9` | Thiết bị hạ tầng: HSRP standby, switch management |
| `.10` – `.49` | **Server, máy in, camera** — IP tĩnh |
| `.50` – `.(last-10)` | **DHCP pool** |
| 10 địa chỉ cuối | Dự trữ / thiết bị tạm |

### Bước 5 — Ánh xạ VLAN ID ↔ subnet

Chọn quy ước giúp nhìn IP là đoán ra VLAN:

```text
VLAN 10  →  10.0.10.0/24
VLAN 20  →  10.0.20.0/24
VLAN 99  →  10.0.99.0/24
```

> 🔧 Quy ước này chỉ dùng được khi dải đủ rộng (một `/16`). Với `/23` chật như ví dụ trên
> thì không áp dụng được — đó là một lý do nữa để **xin dải rộng ngay từ đầu**.

### Bước 6 — Viết tài liệu

Một IP plan chỉ nằm trong đầu bạn là IP plan **đã mất**. Xem mẫu ở mục 11.

---

## 6. Packet Flow — IP plan ảnh hưởng gì

IP plan không xuất hiện trong gói tin, nhưng nó quyết định **gói đi qua đâu**:

| Thiết kế | Hệ quả với traffic |
|---|---|
| Server cùng VLAN với user | Traffic **không** qua L3 → nhanh, nhưng **không có chỗ đặt ACL** |
| Server tách VLAN riêng | Mọi truy cập đi qua SVI → **có điểm kiểm soát** |
| Guest cùng dải với nội bộ | Không summarize được, ACL phải liệt kê từng IP |
| Guest tách hẳn một block | Một dòng ACL `deny 10.0.0.192/26 → any internal` là xong |

> 🔑 **Subnet là ranh giới chính sách.** Thiết kế IP plan chính là thiết kế trước
> *chỗ nào bạn sẽ đặt được luật*.

---

## 7. Real-world Example

🏭 **Mẫu quy hoạch cho doanh nghiệp nhiều chi nhánh** — dùng `10.0.0.0/8`:

```text
10. X . Y . Z /24
    │   │   └── host
    │   └────── VLAN / mục đích
    └────────── mã site

10.1.x.x  →  Trụ sở Hà Nội      →  gom: 10.1.0.0/16
10.2.x.x  →  Chi nhánh Sài Gòn  →  gom: 10.2.0.0/16
10.3.x.x  →  Chi nhánh Đà Nẵng  →  gom: 10.3.0.0/16
10.99.x.x →  Hạ tầng dùng chung (WAN link, loopback)
```

Trong mỗi site:

```text
10.1.10.0/24  →  VLAN 10  User tầng 1
10.1.20.0/24  →  VLAN 20  User tầng 2
10.1.50.0/24  →  VLAN 50  Server
10.1.90.0/24  →  VLAN 90  Guest
10.1.99.0/24  →  VLAN 99  Management
```

Lợi ích rõ ngay:

| Việc | Nhờ quy hoạch này |
|---|---|
| Route tới Sài Gòn | **1 dòng**: `10.2.0.0/16` thay vì 15 dòng |
| ACL chặn Guest mọi site | `10.x.90.0/24` — nhìn là biết |
| Thêm site mới | Lấy `10.4.0.0/16`, copy khuôn VLAN |
| Nhìn IP đoán vị trí | `10.2.50.17` = Sài Gòn, server |

🏭 **Loopback cho thiết bị** — thói quen rất đáng có:

```text
10.99.0.1/32  R1-HN
10.99.0.2/32  R2-HN
10.99.0.11/32 R1-SG
```

Loopback không bao giờ down → dùng làm **OSPF Router ID**, điểm SSH quản trị,
và source của syslog/SNMP. Bạn sẽ cảm ơn nó ở Phase 2.

---

## 8. Cisco CLI

```cisco
! ───── Gán IP cho SVI (L3 switch) ─────
SW1(config)# interface vlan 10
SW1(config-if)# description GW-SALES
SW1(config-if)# ip address 10.0.0.1 255.255.255.128     ! /25
SW1(config-if)# no shutdown

! ───── WAN link /30 ─────
R1(config)# interface GigabitEthernet0/2
R1(config-if)# description WAN-TO-R2
R1(config-if)# ip address 10.0.1.81 255.255.255.252
R1(config-if)# no shutdown

! ───── Loopback ─────
R1(config)# interface Loopback0
R1(config-if)# ip address 10.99.0.1 255.255.255.255

! ───── Kiểm tra chồng lấn: IOS tự từ chối ─────
R1(config-if)# ip address 10.0.0.5 255.255.255.128
% 10.0.0.0 overlaps with GigabitEthernet0/0

! ───── Summarization (xem sâu ở Phase 2) ─────
R1(config)# ip route 10.2.0.0 255.255.0.0 10.0.1.82      ! 1 dòng cho cả site SG
```

| Lệnh | Làm gì | Ghi chú |
|---|---|---|
| `description` | Ghi chú interface | **Luôn đặt** — người sau (và chính bạn 6 tháng nữa) cần nó |
| `interface Loopback0` | Tạo loopback | Không bao giờ down; dùng làm Router ID |
| IOS báo `overlaps` | Chặn chồng lấn **trên cùng router** | ⚠️ Không chặn được chồng lấn giữa **các router khác nhau** |

> ⚠️ IOS chỉ phát hiện chồng lấn trong phạm vi **một thiết bị**. Hai router khác nhau cùng
> cấu hình `10.0.0.0/24` thì không ai báo gì — chỉ khi routing chạy mới vỡ lở. Vì vậy
> **tài liệu IP plan là lớp phòng vệ duy nhất**.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip interface brief
Interface      IP-Address      OK? Method Status    Protocol
Vlan10         10.0.0.1        YES manual up        up
Vlan20         10.0.0.129      YES manual up        up
Vlan99         10.0.1.65       YES manual up        up
GigabitEthernet0/2  10.0.1.81  YES manual up        up
Loopback0      10.99.0.1       YES manual up        up
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip route connected
      10.0.0.0/8 is variably subnetted, 10 subnets, 5 masks
C        10.0.0.0/25    is directly connected, Vlan10
L        10.0.0.1/32    is directly connected, Vlan10
C        10.0.0.128/26  is directly connected, Vlan20
L        10.0.0.129/32  is directly connected, Vlan20
C        10.0.1.80/30   is directly connected, GigabitEthernet0/2
C        10.99.0.1/32   is directly connected, Loopback0
```

**Đọc gì:**

| Dấu hiệu | Ý nghĩa |
|---|---|
| `variably subnetted, N subnets, M masks` | `M > 1` = **VLSM đang hoạt động** |
| Prefix đúng như thiết kế | Nếu lệch → gán sai mask |
| Thiếu một `C` | SVI down (VLAN chưa có port up) hoặc interface shutdown |

### Tự kiểm tra IP plan — 5 câu

- [ ] Có subnet nào **chồng lấn** không? *(vẽ trục số, tô từng khoảng)*
- [ ] Mỗi subnet có **đủ host + dự phòng** chưa?
- [ ] Có **khoảng trống** cho VLAN mới không?
- [ ] Gateway đặt **nhất quán** (luôn first usable) chưa?
- [ ] Các subnet cùng site có **gom được** thành một route không?

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| IOS báo `overlaps` | Hai interface cùng router chồng dải | `show ip interface brief` | Chia lại |
| Hai site ping nhau lúc được lúc không | **Chồng lấn giữa các router** | So IP plan 2 site | Đánh số lại một site |
| Hết IP trong một VLAN | Không tính dự phòng | `show ip dhcp pool` | Mở rộng prefix (phải đổi mask mọi máy) |
| Bảng route phình to | Không summarize được do chia lộn xộn | `show ip route \| count` | Quy hoạch lại theo site |
| Máy mới không có IP | DHCP pool hết | `show ip dhcp pool` | Mở rộng pool trong subnet hiện có |
| Mất SSH vào switch sau khi đổi IP | Quên đổi `ip default-gateway` / route | Console vào | Sửa qua console |

---

## 11. LAB

🧪 **[LAB 04 — Thiết kế IP plan cho doanh nghiệp](../labs/lab04-ip-plan-doanh-nghiep.md)** — chia VLSM 9 nhu cầu từ một `/23`

### Mẫu tài liệu `ip-plan.md` cần nộp

```markdown
# IP PLAN — <Tên công ty>
Dải được cấp: 10.0.0.0/23      Ngày: YYYY-MM-DD      Người lập: ...

## 1. Bảng subnet
| VLAN | Tên | Prefix | Network | Gateway | Dải DHCP | Broadcast | Host tối đa | Dùng thực tế |

## 2. Quy ước gán địa chỉ
.1 = gateway · .2-.9 = hạ tầng · .10-.49 = tĩnh · .50+ = DHCP

## 3. Dải còn trống
10.0.1.88 – 10.0.1.255 (168 địa chỉ)

## 4. Lịch sử thay đổi
| Ngày | Thay đổi | Người |
```

## 12. Challenge

1. Được cấp `192.168.1.0/24`. Cần: 60, 30, 25, 12, 5 host và 3 WAN link `/30`.
   Chia VLSM đầy đủ. **Có đủ không?**
2. Công ty 3 chi nhánh, mỗi chi nhánh 5 VLAN ~50 host. Thiết kế dải từ `172.16.0.0/16`
   sao cho **mỗi chi nhánh gom được thành 1 route**.
3. Đang dùng `10.0.0.0/24` cho một VLAN 200 user. Công ty mua thêm công ty khác,
   VLAN đó phải lên 400 user. Nêu **2 phương án** và đánh đổi của từng cái.
4. Vì sao WAN link point-to-point **không cần** dự phòng tăng trưởng?

<details>
<summary>Đáp án</summary>

**1.** Sắp giảm dần rồi cấp:

| Nhu cầu | Prefix | Network | Dải |
|---|:---:|---|---|
| 60 host | `/26` | `192.168.1.0` | `.1` – `.62` |
| 30 host | `/27` | `192.168.1.64` | `.65` – `.94` |
| 25 host | `/27` | `192.168.1.96` | `.97` – `.126` |
| 12 host | `/28` | `192.168.1.128` | `.129` – `.142` |
| 5 host | `/29` | `192.168.1.144` | `.145` – `.150` |
| WAN 1 | `/30` | `192.168.1.152` | `.153` – `.154` |
| WAN 2 | `/30` | `192.168.1.156` | `.157` – `.158` |
| WAN 3 | `/30` | `192.168.1.160` | `.161` – `.162` |

**Đủ**, còn trống `.164` → `.255` = 92 địa chỉ. Lưu ý: 25 host phải dùng `/27` chứ không
phải `/28` (14 host) — đây là chỗ hay tính nhầm.

**2.** Cấp mỗi chi nhánh một `/19` hoặc `/20`:

```text
172.16.0.0/20   → Chi nhánh A   (gồm 172.16.0.0/24 … 172.16.15.0/24)
172.16.16.0/20  → Chi nhánh B
172.16.32.0/20  → Chi nhánh C
```

Mỗi chi nhánh dùng 5 `/24` trong block của mình, còn thừa 11 `/24` để mở rộng.
Router lõi chỉ cần **3 route** thay vì 15.

**3.** Hai phương án:

| Phương án | Cách làm | Đánh đổi |
|---|---|---|
| **Mở rộng** `/24` → `/23` | Đổi mask trên gateway + mọi máy | Phải đổi mask toàn bộ; broadcast domain 500 host là **quá lớn** |
| **Tách thêm VLAN mới** | Giữ `/24` cũ, thêm VLAN + subnet mới cho 200 user mới | Cần inter-VLAN routing và ACL mới, nhưng broadcast domain vẫn lành mạnh |

👉 Phương án 2 tốt hơn gần như luôn. Phương án 1 chỉ chữa được triệu chứng "hết IP"
mà tạo ra bệnh nặng hơn là "broadcast domain khổng lồ".

**4.** Vì point-to-point theo định nghĩa là **đúng 2 thiết bị** — không bao giờ có thiết bị
thứ ba cắm vào một WAN link. Dùng `/30` (hoặc `/31`) là tối ưu vĩnh viễn. Cấp `/24` cho
WAN link là lãng phí 252 địa chỉ mà không bao giờ dùng tới.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Quy tắc cấp lớn trước · vì sao `/26` chỉ bắt đầu ở bội số 64 | ⬜ |
| **L2** Explain | Giải thích summarization và vì sao nó cần IP plan tốt | ⬜ |
| **L3** Configure | Gán IP cho 5 SVI + 2 WAN link + 1 loopback theo plan | ⬜ |
| **L4** Troubleshoot | Hai site ping chập chờn → phát hiện chồng lấn dải | ⬜ |
| **L5** Design | Thiết kế IP plan đầy đủ cho công ty 3 site, viết `ip-plan.md` | ⬜ |

## 14. Summary

**Key concepts**

- VLSM = nhiều prefix khác nhau trong cùng một dải, mỗi subnet vừa đủ
- ⭐ **Cấp lớn trước** — vì subnet phải căn theo bội số block size
- Dự phòng ~30% cho VLAN user, 0% cho WAN link
- Quy ước gán: `.1` gateway · `.10-.49` tĩnh · `.50+` DHCP — **thống nhất toàn hệ thống**
- Quy hoạch theo site → **summarization** → bảng route nhỏ, hội tụ nhanh
- Loopback `/32` cho thiết bị: Router ID, SSH, syslog source
- **Subnet là ranh giới chính sách** — thiết kế IP plan là thiết kế chỗ đặt ACL

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip route connected` | Xác nhận subnet đúng như thiết kế |
| `show ip interface brief` | Nhìn tổng thể IP đã gán |
| `description <text>` | Ghi chú interface — luôn đặt |

**Common mistakes**

| Sai | Đúng |
|---|---|
| Cấp nhỏ trước | **Lớn trước**, nếu không sẽ phân mảnh |
| Cấp `/24` cho WAN link | `/30` là đủ vĩnh viễn |
| Không chừa chỗ cho VLAN mới | Luôn để trống ≥ 20% dải |
| Gateway lúc `.1` lúc `.254` | Thống nhất một kiểu |
| 25 host → chọn `/28` | `/28` chỉ 14 host — phải `/27` |
| IP plan chỉ nằm trong đầu | Viết `ip-plan.md`, commit vào repo |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 04 đầy đủ, nộp kèm file `ip-plan.md`.
2. Vẽ IP plan hiện tại của công ty bạn (hoặc nhà bạn) lên giấy. Tìm xem có chỗ nào
   lãng phí hoặc không gom route được.
3. Challenge câu 2 — thiết kế 3 chi nhánh từ `172.16.0.0/16`, viết ra đầy đủ.

```markdown
- [YYYY-MM-DD] Lesson 07 — VLSM & IP Plan: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Chia VLSM đúng thứ tự, tính prefix từ số host, không chồng lấn |
| 🔧 **Engineer** | Quy ước gán địa chỉ; loopback; `description` mọi interface; chừa chỗ mở rộng |
| 🏭 **Production** | Đổi subnet đang chạy rất đắt; IOS không phát hiện chồng lấn giữa các thiết bị → tài liệu là lớp phòng vệ duy nhất |

### 🔗 Liên kết

- ⬅️ [Lesson 06 — TCP/UDP & Port](./lesson-06-tcp-udp-port.md)
- ➡️ [Lesson 08 — DNS & DHCP](./lesson-08-dns-va-dhcp.md)
- 🧮 [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md)
- 🧪 [LAB 04](../labs/lab04-ip-plan-doanh-nghiep.md)
