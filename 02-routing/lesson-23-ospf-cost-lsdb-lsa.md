# LESSON 23 — OSPF: Cost · Router ID · LSDB · LSA ⭐

> 📌 Lesson 22 cho bạn *"làm sao để OSPF lên"*. Lesson này cho bạn *"OSPF thật sự
> nghĩ gì bên trong"* — đọc được LSDB là lúc OSPF thôi còn là hộp đen.

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 22](./lesson-22-ospf-single-area.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Tính được cost của một đường đi, và biết OSPF cộng cost ở đâu
- [ ] Giải thích **LSDB** là gì và vì sao mọi router trong area phải giống hệt nhau
- [ ] Nhận biết **LSA Type 1, 2, 3** — ai tạo, chứa gì, lan tới đâu
- [ ] Đọc `show ip ospf database` và hiểu mình đang nhìn gì
- [ ] Giải thích thuật toán SPF chạy thế nào (mức khái niệm)

## 2. Prerequisite

- OSPF neighbor, state, DR/BDR *(Lesson 22)*
- Cost = `reference bandwidth / bandwidth` *(Lesson 22)*

---

## 3. Concept

### Cost — cộng ở đâu

```text
Cost của một đường = TỔNG cost của các interface ĐI RA (outgoing) trên đường đó
```

```text
R1 ──Gi(cost 1)── R2 ──Se(cost 64)── R3 ──Gi(cost 1)── Mạng X

R1 tính cost tới mạng X:
  Gi ra R2   : 1
  Se ra R3   : 64
  Gi tới X   : 1
  ─────────────
  TỔNG       : 66
```

> ⚠️ **Chỉ cộng cost của interface ĐI RA**, không cộng interface nhận vào.
> Đây là chỗ hay tính nhầm.

### Đặt cost bằng tay

```cisco
! Cách 1 — đặt cost trực tiếp (ưu tiên cao nhất)
R1(config-if)# ip ospf cost 50

! Cách 2 — đổi bandwidth (ảnh hưởng cả QoS và các protocol khác)
R1(config-if)# bandwidth 64

! Cách 3 — đổi reference bandwidth (toàn cục, PHẢI giống nhau mọi router)
R1(config-router)# auto-cost reference-bandwidth 100000
```

> 🔧 Dùng **cách 1** khi chỉ muốn ảnh hưởng OSPF. `bandwidth` ảnh hưởng nhiều thứ khác
> (QoS, EIGRP metric, thống kê) nên dễ gây tác dụng phụ ngoài ý muốn.

### LSDB — Link-State Database

**LSDB** = cơ sở dữ liệu chứa **toàn bộ bản đồ** của một area.

```text
┌──────────────────────────────────────┐
│          LSDB của Area 0             │
│  (MỌI router trong area có bản SAO   │
│        GIỐNG HỆT NHAU)               │
│                                       │
│  R1: tôi nối R2 (cost 1), nối LAN A  │
│  R2: tôi nối R1 (cost 1), nối R3     │
│  R3: tôi nối R2, nối LAN B           │
└──────────────────────────────────────┘
          │
          ▼  mỗi router tự chạy
     Dijkstra (SPF)
          │
          ▼
   Cây đường đi ngắn nhất → routing table
```

> ⭐ **Nguyên lý cốt lõi của Link-State:**
> Mọi router trong cùng area có **LSDB giống hệt nhau**. Vì cùng dữ liệu đầu vào và
> cùng thuật toán, chúng tính ra kết quả **nhất quán** — không thể có routing loop.
>
> Nếu LSDB hai router khác nhau → mạng đang có vấn đề nghiêm trọng.

### LSA — viên gạch xây nên LSDB

**LSA** (Link-State Advertisement) = một mẩu thông tin về một phần của mạng.
LSDB là tập hợp mọi LSA.

### Ba loại LSA cần biết ở CCNA

| Type | Tên | **Ai tạo** | **Chứa gì** | **Lan tới đâu** |
|:---:|---|---|---|---|
| **1** | **Router LSA** | **Mọi router** | Các link của chính nó + cost | **Trong area** đó |
| **2** | **Network LSA** | **Chỉ DR** | Danh sách router trên segment multi-access | **Trong area** đó |
| **3** | **Summary LSA** | **Chỉ ABR** | Mạng ở area khác | **Sang area khác** |

| Type | Tên | Ai tạo | Ghi chú *(CCNA chỉ cần nhận biết)* |
|:---:|---|---|---|
| 4 | ASBR Summary | ABR | "Đường tới ASBR ở đâu" |
| 5 | External LSA | **ASBR** | Route từ ngoài redistribute vào |
| 7 | NSSA External | ASBR trong NSSA | Thay Type 5 trong area NSSA |

> 💡 Cách nhớ 3 loại chính:
> **Type 1** = *"tôi là ai, tôi nối với ai"*
> **Type 2** = *"segment này có những ai"* (do DR tổng hợp)
> **Type 3** = *"area bên kia có mạng gì"* (do ABR bắc cầu)

### Vì sao cần Type 2

Trên link multi-access (Ethernet) có 4 router: nếu mỗi router tự mô tả quan hệ với
3 router còn lại thì LSDB phình to.

Thay vào đó: **DR tạo một Type 2** mô tả *"segment này gồm R1, R2, R3, R4"*,
và mỗi router chỉ cần Type 1 nói *"tôi nối vào segment đó"*.

> 🔑 Đây là lý do thứ hai khiến DR tồn tại — không chỉ giảm adjacency,
> mà còn **giảm kích thước LSDB**.

### SPF — Dijkstra, mức khái niệm

```text
1. Đặt mình làm GỐC của cây
2. Lấy LSDB ra, dựng đồ thị: node = router, cạnh = link có cost
3. Lặp: luôn chọn node CHƯA xét có tổng cost NHỎ NHẤT
4. Từ node đó, cập nhật cost tới các node kề
5. Lặp tới khi hết node
6. Kết quả: cây đường đi ngắn nhất từ mình tới mọi đích
7. Nạp vào routing table
```

SPF chạy khi: **có LSA mới**, hoặc **có LSA thay đổi**. Không chạy định kỳ vô ích.

> ⚠️ SPF tốn CPU. Mạng lớn với LSDB khổng lồ → mỗi lần có thay đổi là mọi router
> phải tính lại. **Đây chính là lý do phải chia area** — giới hạn phạm vi SPF.

### LSA aging

| Giá trị | Ý nghĩa |
|---|---|
| **30 phút** | Router tự refresh LSA của mình (gửi lại dù không đổi gì) |
| **60 phút (MaxAge)** | LSA không được refresh → bị xoá khỏi LSDB |

---

## 4. Why?

> **Vì sao phải hiểu LSDB? Routing table không đủ sao?**

| Routing table cho bạn | LSDB cho bạn |
|---|---|
| **Kết quả** cuối cùng | **Dữ liệu thô** để ra kết quả đó |
| "Đi tới X qua Y" | "Vì sao lại là Y mà không phải Z" |
| Chỉ đường tốt nhất | **Mọi** đường router biết |

Khi route đi sai đường, routing table chỉ cho bạn thấy **triệu chứng**.
LSDB cho bạn thấy **nguyên nhân** — cost ở đâu sai, LSA nào thiếu, router nào không quảng bá.

> 🔧 Ở mức CCNA, bạn chỉ cần **đọc được** LSDB và nhận ra 3 loại LSA.
> Ở CCNP, bạn sẽ dùng nó để debug những vấn đề mà routing table không giải thích nổi.

---

## 5. How does it work? — LSA lan truyền

```text
1. Link R2–R3 chết
2. R2 và R3 mỗi bên tạo LSA Type 1 MỚI (sequence number tăng)
3. FLOOD ngay lập tức ra mọi interface OSPF (trừ nơi nhận được)
4. Router nhận LSA:
   ├─ Sequence MỚI hơn  → cập nhật LSDB, flood tiếp, gửi LSAck
   ├─ Sequence BẰNG     → chỉ gửi LSAck, không flood
   └─ Sequence CŨ hơn   → gửi lại LSA mới của mình cho bên kia
5. Sau vài trăm ms: MỌI router trong area có LSDB giống nhau
6. MỌI router chạy lại SPF
7. Routing table cập nhật
→ Tổng: vài giây
```

> 🔑 So với RIP (Lesson 21): RIP lan **kết quả đã tính** qua từng chặng, mỗi chặng 30 giây.
> OSPF **flood dữ kiện thô ngay lập tức**, rồi mỗi router tự tính. Đó là toàn bộ
> khác biệt về tốc độ hội tụ.

---

## 6. Packet Flow — LSA Type 1 chứa gì

```text
# dạng điển hình — tự xem bằng show ip ospf database router <id>
LS Type: Router Links
Link State ID: 1.1.1.1          ← Router ID của người tạo
Advertising Router: 1.1.1.1
Number of Links: 3

  Link 1: connected to a Transit Network
    Link ID: 10.0.12.2          ← địa chỉ interface của DR
    Metric: 1                   ← COST

  Link 2: connected to a Stub Network
    Link ID: 10.0.1.0           ← mạng LAN
    Link Data: 255.255.255.0
    Metric: 1

  Link 3: connected to another Router (point-to-point)
    Link ID: 3.3.3.3
    Metric: 64
```

| Loại link trong Type 1 | Nghĩa |
|---|---|
| **Transit Network** | Nối vào segment multi-access có DR |
| **Stub Network** | Mạng không có router nào khác (LAN người dùng) |
| **Point-to-point** | Nối trực tiếp một router khác |

---

## 7. Real-world Example

🏭 **Debug "route đi đường chậm"** — đúng việc LSDB sinh ra để làm

Triệu chứng: traffic đi qua link 100 Mbps thay vì link 1 Gbps song song.

```cisco
R1# show ip ospf database router 2.2.2.2
```

Nhìn cost của từng link trong LSA Type 1 của R2 → phát hiện ai đó đã đặt
`ip ospf cost 1` bằng tay trên link chậm, làm nó ngang bằng link nhanh.

Routing table chỉ nói *"đi qua R2"*. LSDB nói *"vì R2 khai cost sai"*.

🏭 **LSDB không đồng bộ — dấu hiệu nghiêm trọng**

```cisco
R1# show ip ospf database | include Router Link States
R2# show ip ospf database | include Router Link States
```

Nếu số LSA khác nhau giữa hai router **cùng area** → đang có vấn đề:
MTU mismatch (LSA lớn không qua được), link chập chờn, hoặc LSDB corrupt.

Cách xử lý: `clear ip ospf process` trên router nghi ngờ *(⚠️ gián đoạn tạm thời)*.

🏭 **Reference bandwidth — phải đồng bộ toàn mạng**

Một router đặt `auto-cost reference-bandwidth 100000`, các router khác để mặc định:

```text
R1 tính link 1G: cost 100
R2 tính link 1G: cost 1
```

→ Cost bất đối xứng → traffic đi một đường, về đường khác → rất khó debug,
và gây vấn đề với firewall stateful.

> 🔧 Quy tắc: `auto-cost reference-bandwidth` là **thông số toàn mạng**, không phải
> thông số per-router. Đổi thì đổi hết.

---

## 8. Cisco CLI

```cisco
! ───── Xem LSDB ─────
R1# show ip ospf database                      ! tổng quan mọi LSA
R1# show ip ospf database router               ! chỉ Type 1
R1# show ip ospf database network              ! chỉ Type 2
R1# show ip ospf database summary              ! chỉ Type 3
R1# show ip ospf database router 2.2.2.2       ! LSA Type 1 của một router cụ thể

! ───── Cost ─────
R1(config-if)# ip ospf cost 50                 ! đặt trực tiếp (ưu tiên nhất)
R1(config-if)# bandwidth 64                    ! đổi gián tiếp qua bandwidth
R1(config-router)# auto-cost reference-bandwidth 100000

! ───── Router ID ─────
R1(config-router)# router-id 1.1.1.1
R1# clear ip ospf process                      ! cần reset để Router ID mới có hiệu lực

! ───── Kiểm tra ─────
R1# show ip ospf                               ! Router ID, số lần chạy SPF
R1# show ip ospf interface brief
R1# show ip route ospf
```

| Lệnh | Cho biết |
|---|---|
| `show ip ospf database` | Toàn bộ bản đồ area — **so sánh giữa 2 router phải giống nhau** |
| `show ip ospf database router <id>` | Router đó khai báo link nào, cost bao nhiêu |
| `show ip ospf` | **SPF đã chạy bao nhiêu lần** — chạy liên tục = mạng không ổn định |
| `ip ospf cost N` | Ép cost mà không ảnh hưởng gì khác |

> ⚠️ Đổi `router-id` **không có hiệu lực ngay** — phải `clear ip ospf process`
> (gián đoạn mạng tạm thời) hoặc reload.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip ospf database

            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 0)

Link ID         ADV Router      Age    Seq#        Checksum Link count
1.1.1.1         1.1.1.1         412    0x80000005  0x00A2B1  3
2.2.2.2         2.2.2.2         389    0x80000007  0x003C21  4
3.3.3.3         3.3.3.3         401    0x80000004  0x00F1D2  2

                Net Link States (Area 0)

Link ID         ADV Router      Age    Seq#        Checksum
10.0.12.2       2.2.2.2         389    0x80000002  0x005A3E
```

**Đọc gì:**

| Cột | Ý nghĩa | Bất thường |
|---|---|---|
| `Router Link States` | **LSA Type 1** — mỗi router một dòng | Thiếu một router → nó chưa vào area |
| `Net Link States` | **LSA Type 2** — mỗi segment multi-access một dòng | `ADV Router` = **DR** của segment đó |
| `Link ID` (Type 1) | Router ID | |
| `Link ID` (Type 2) | IP interface của **DR** | |
| `Age` | Giây kể từ khi tạo | Gần **3600** mà không reset → LSA sắp hết hạn, bất thường |
| `Seq#` | Số thứ tự, tăng dần | Tăng **liên tục nhanh** → link chập chờn |
| `Link count` | Số link router đó khai | Khác với thực tế → cấu hình thiếu |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip ospf
 Routing Process "ospf 1" with ID 1.1.1.1
 Number of areas in this router is 1. 1 normal 0 stub 0 nssa
 Reference bandwidth unit is 100000 mbps
    Area BACKBONE(0)
        Number of interfaces in this area is 2
        SPF algorithm executed 7 times
        Number of LSA 4. Checksum Sum 0x02A1F3
```

| Dòng | Ý nghĩa | Bất thường |
|---|---|---|
| `Reference bandwidth unit is 100000 mbps` | Đã đổi reference bandwidth ✅ | Phải giống mọi router |
| `SPF algorithm executed 7 times` | Số lần tính lại | **Tăng liên tục** = mạng chập chờn |
| `Number of LSA 4` | Kích thước LSDB | So với router khác — phải **bằng nhau** |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Traffic đi đường chậm | Cost sai | `show ip ospf database router <id>` | Sửa `ip ospf cost` hoặc reference-bandwidth |
| Link 1G và 10G cùng được chọn | Cost mặc định đều = 1 | `show ip ospf interface \| include Cost` | `auto-cost reference-bandwidth 100000` **mọi router** |
| Cost khác nhau giữa 2 router cho cùng link | reference-bandwidth lệch | `show ip ospf \| include Reference` | Đồng bộ toàn mạng |
| `SPF executed` tăng liên tục | Link chập chờn, LSA liên tục đổi | `show ip ospf`, `show logging` | Tìm interface flap |
| Số LSA khác nhau giữa các router cùng area | LSDB không đồng bộ | `show ip ospf database` ở 2 router | Nghi MTU; `clear ip ospf process` |
| `Age` gần 3600 không reset | LSA không được refresh | `show ip ospf database` | Router tạo LSA có thể đã mất |
| Thiếu LSA Type 2 trên segment Ethernet | Chưa bầu được DR | `show ip ospf neighbor` | Kiểm tra priority, network type |
| Đổi `router-id` mà không có tác dụng | Chưa reset process | `show ip ospf` | `clear ip ospf process` |

---

## 11. LAB

🧪 **Phần mở rộng của [LAB 23](../labs/lab23-ospf-single-area.md)** — mục "Đọc LSDB".

Bài quan sát bổ sung:

1. Chạy `show ip ospf database` trên **mọi** router → đếm số LSA. Phải **bằng nhau**.
2. `show ip ospf database router <id>` của từng router → vẽ lại topology **chỉ từ LSDB**,
   không nhìn sơ đồ. So với sơ đồ thật.
3. Đặt `ip ospf cost 100` trên một link → quan sát:
   - LSA Type 1 của router đó thay đổi (`Seq#` tăng)
   - `SPF algorithm executed` tăng trên **mọi** router
   - Routing table đổi đường
4. `shutdown` một link → đo lại số LSA và số lần SPF chạy.

## 12. Challenge

```text
R1 ──Gi(1G)── R2 ──Se(1.544M)── R3
 │                                │
 └────────Gi(1G)──── R4 ──Gi(1G)──┘

Reference bandwidth: mặc định (100 Mbps)
```

1. Tính cost từ R1 tới R3 theo **cả hai** đường. Đường nào thắng?
2. Nếu đổi `auto-cost reference-bandwidth 100000` trên mọi router, cost thành bao nhiêu?
   Kết quả có đổi không?
3. Trên segment Ethernet R1–R2 có cả R5, R6. LSDB có bao nhiêu LSA Type 2 cho segment đó?
   Ai tạo?
4. Vì sao LSA Type 1 của R2 có `Link count` lớn hơn của R1?

<details>
<summary>Đáp án</summary>

**1.** Với reference bandwidth mặc định 100 Mbps:

| Interface | Bandwidth | Cost |
|---|---|:---:|
| Gi (1 Gbps) | 1000 Mbps | `100/1000 = 0.1` → **1** |
| Se (1.544 Mbps) | 1.544 Mbps | `100/1.544 ≈ 64.7` → **64** |

| Đường | Phép tính | Tổng cost |
|---|---|:---:|
| R1 → R2 → R3 | 1 (Gi) + 64 (Se) | **65** |
| R1 → R4 → R3 | 1 (Gi) + 1 (Gi) | **2** ← **THẮNG** |

**2.** Với reference bandwidth 100.000 Mbps:

| Interface | Cost mới |
|---|:---:|
| Gi (1 Gbps) | `100000/1000` = **100** |
| Se (1.544 Mbps) | `100000/1.544` ≈ **64766** |

| Đường | Tổng cost |
|---|:---:|
| Qua R2 | 100 + 64766 = **64866** |
| Qua R4 | 100 + 100 = **200** ← vẫn thắng |

**Kết quả không đổi** — vẫn chọn đường qua R4. Nhưng giờ OSPF **phân biệt được**
link 1G với link 10G (10G sẽ là cost 10), điều mà reference mặc định không làm được.

**3.** **Đúng một** LSA Type 2, do **DR của segment đó** tạo ra.

Type 2 mô tả *"segment multi-access này gồm những router nào"*. Mỗi segment chỉ có
một DR, nên chỉ có một Type 2. Trong `show ip ospf database`, `Link ID` của nó
chính là **IP interface của DR**.

**4.** Vì `Link count` đếm **số link mà router đó khai báo**, và R2 nối nhiều thứ hơn:

| Router | Các link |
|---|:---:|
| R1 | Gi tới R2 · Gi tới R4 · LAN của R1 → **3** |
| R2 | Gi tới R1 · Se tới R3 · LAN của R2 · *(nếu có thêm interface)* → **4+** |

`Link count` là cách nhanh để kiểm tra một router có khai đủ interface vào OSPF chưa.
Thiếu so với thực tế → có interface chưa được `network` statement bao phủ.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Công thức cost · LSA Type 1/2/3 ai tạo chứa gì · LSA aging | ⬜ |
| **L2** Explain | Giải thích vì sao LSDB giống nhau thì không thể có loop | ⬜ |
| **L3** Configure | Đặt cost bằng 3 cách, quan sát routing table đổi | ⬜ |
| **L4** Troubleshoot | Traffic đi đường chậm → dùng LSDB tìm cost sai | ⬜ |
| **L5** Design | Vẽ lại topology **chỉ từ `show ip ospf database`** | ⬜ |

## 14. Summary

**Key concepts**

- **Cost đường đi = tổng cost của các interface ĐI RA**
- Đặt cost: `ip ospf cost` ⭐ · `bandwidth` · `auto-cost reference-bandwidth`
- ⭐ **LSDB giống hệt nhau trong cùng area** → mọi router tính ra kết quả nhất quán → **không loop**
- **LSA Type 1** (Router) — mọi router tạo, trong area
- **LSA Type 2** (Network) — **chỉ DR** tạo, trong area
- **LSA Type 3** (Summary) — **chỉ ABR** tạo, sang area khác
- SPF (Dijkstra) chạy khi **có LSA thay đổi**, không chạy định kỳ
- LSA refresh **30 phút**, hết hạn **60 phút**
- ⚠️ `auto-cost reference-bandwidth` là **thông số toàn mạng** — phải đồng bộ

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip ospf database` | Xem bản đồ area; **so giữa các router phải giống nhau** |
| `show ip ospf database router <id>` | Router đó khai link nào, cost bao nhiêu |
| `show ip ospf` | Số lần SPF chạy, reference bandwidth, số LSA |
| `ip ospf cost N` | Ép cost, không ảnh hưởng thứ khác |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Cộng cả cost interface nhận vào | Tính sai cost |
| Đổi `bandwidth` thay vì `ip ospf cost` | Ảnh hưởng QoS và protocol khác |
| reference-bandwidth lệch giữa các router | Cost bất đối xứng, traffic đi/về khác đường |
| Nghĩ Type 2 do mọi router tạo | **Chỉ DR** tạo |
| Bỏ qua LSDB khi debug | Routing table chỉ cho triệu chứng, LSDB cho nguyên nhân |
| Đổi `router-id` mà không reset process | Không có hiệu lực |

## 15. Homework + cập nhật PROGRESS

1. Làm phần mở rộng LAB 23 — **vẽ lại topology chỉ từ LSDB**. Đây là bài tập
   có giá trị nhất của lesson.
2. Tính tay cost cho challenge mục 12, rồi kiểm chứng bằng `show ip route ospf`.
3. Đặt `ip ospf cost 500` trên một link, quan sát `Seq#` của LSA tăng và
   `SPF executed` tăng trên mọi router.

```markdown
- [YYYY-MM-DD] Lesson 23 — OSPF Cost, LSDB, LSA: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Công thức cost, LSA Type 1/2/3, đọc `show ip ospf database` |
| 🔧 **Engineer** | `ip ospf cost` thay vì `bandwidth`; so LSDB giữa các router khi debug |
| 🏭 **Production** | reference-bandwidth phải đồng bộ toàn mạng; `SPF executed` tăng liên tục = link flap |

### 🔗 Liên kết

- ⬅️ [Lesson 22 — OSPF single-area](./lesson-22-ospf-single-area.md)
- ➡️ [Lesson 24 — OSPF multi-area](./lesson-24-ospf-multi-area.md)
- 🔜 LSA Type 4/5/7, LSDB sâu: [`CCNP-Encor` Module 04A/04B](https://github.com/hiepnguyen775/CCNP-Encor)
