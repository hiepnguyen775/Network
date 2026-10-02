# LESSON 15 — Spanning Tree Protocol (STP) ⭐

> 📌 Lesson khó nhất Phase 1. Nếu chỉ học thuộc "STP chống loop" thì chưa đủ —
> phải **đọc được `show spanning-tree` và nói ra ai là root, port nào bị block, vì sao**.

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~4 giờ |
| **Prerequisite** | [Lesson 04](../00-foundation/lesson-04-unicast-broadcast-multicast.md), [Lesson 13](./lesson-13-vlan-va-trunk.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích vì sao loop L2 **nguy hiểm hơn** loop L3 — bằng một câu
- [ ] Mô tả quy trình bầu root bridge, root port, designated port theo đúng thứ tự
- [ ] Đọc `show spanning-tree` và chỉ ra root, port role, port state, **vì sao**
- [ ] Chỉ định root bridge thay vì để bầu ngẫu nhiên
- [ ] Tính được đường đi của traffic khi một link chết

## 2. Prerequisite

- Broadcast được switch **flood** ra mọi port cùng VLAN *(Lesson 04)*
- Frame Ethernet **không có TTL** *(Lesson 03)*
- Trunk, VLAN *(Lesson 13)*

---

## 3. Concept

### Vấn đề: loop L2

```text
        SW1 ═══════════ SW2
         ║               ║
         ║               ║
        SW3 ═══════════ SW4
          (vòng kín — có dự phòng)
```

Một PC gửi **một** frame broadcast. Không có STP:

```text
SW1 flood ra 2 hướng  →  SW2 và SW3 mỗi con flood tiếp  →  SW4 nhận 2 bản,
flood tiếp  →  quay lại SW1  →  SW1 flood lại  →  ...

Số frame:  1 → 2 → 4 → 8 → 16 → ... (nhân lên MÃI MÃI)
```

> ⭐ **Vì sao loop L2 chết người còn loop L3 thì không:**
> Gói IP có **TTL** — chạy vòng 255 lần rồi tự chết. Frame Ethernet **không có trường TTL**.
> Nó chạy vòng **vĩnh viễn** và nhân lên theo cấp số nhân.
>
> Kết quả trong vài giây: CPU switch 100%, đèn port nháy đồng loạt, MAC table loạn,
> **cả mạng chết**. Đây gọi là **broadcast storm**.

### Giải pháp: STP

**STP (IEEE 802.1D)** tự động **chặn (block)** một số port để biến topology vật lý có vòng
thành **cây logic không vòng**. Khi một link chết, STP mở lại port đã block.

```text
        SW1 ═══════════ SW2
         ║               ║
         ║               ✗ ← port bị BLOCK
        SW3 ═══════════ SW4

Vẫn có dự phòng vật lý, nhưng logic thì không còn vòng.
```

### Bridge ID — cơ sở của mọi quyết định

```text
┌──────────────┬──────────────┬─────────────────┐
│  Priority    │ Extended     │   MAC Address   │
│   4 bit      │ System ID    │     48 bit      │
│              │  12 bit      │                 │
└──────────────┴──────────────┴─────────────────┘
   = bội số 4096      = VLAN ID
```

- **Priority** mặc định **32768**, chỉ đặt được theo bội số của **4096**
- **Extended System ID** = VLAN ID → Bridge ID thực tế = `priority + VLAN ID`
- VD: priority 32768 ở VLAN 10 → Bridge ID hiển thị **32778**

> 💡 Nhớ nhanh: **thấy số lẻ như 32778, 32788 là priority 32768 cộng VLAN ID.**

### Ba bước bầu chọn — thứ tự bắt buộc

| Bước | Bầu gì | Phạm vi | Tiêu chí |
|:---:|---|---|---|
| **1** | **Root Bridge** | Toàn mạng (mỗi VLAN một root) | **Bridge ID thấp nhất** |
| **2** | **Root Port (RP)** | **Mỗi switch** non-root có đúng 1 | Đường về root có **cost thấp nhất** |
| **3** | **Designated Port (DP)** | **Mỗi segment** có đúng 1 | Port có cost về root thấp nhất trên segment đó |

Port còn lại → **Blocked** (non-designated).

### Khi hoà — tiêu chí phá hoà, theo thứ tự

```text
1. Root path cost thấp nhất
2. Bridge ID của LÁNG GIỀNG gửi BPDU thấp nhất
3. Port priority của láng giềng thấp nhất
4. Port ID của láng giềng thấp nhất
```

> ⚠️ Chú ý: tiêu chí 2–4 xét **của láng giềng**, không phải của chính mình.
> Đây là chỗ hay sai nhất khi làm bài tập.

### STP Cost theo tốc độ

| Tốc độ | Cost (802.1D-1998) |
|---|:---:|
| 10 Mbps | 100 |
| 100 Mbps | **19** |
| 1 Gbps | **4** |
| 10 Gbps | **2** |

Root path cost = **tổng cost của các link trên đường về root**.

### Port State — STP cổ điển

| State | Học MAC? | Chuyển frame? | Thời gian |
|---|:---:|:---:|---|
| **Blocking** | ❌ | ❌ | 20 giây *(max age)* |
| **Listening** | ❌ | ❌ | 15 giây *(forward delay)* |
| **Learning** | ✅ | ❌ | 15 giây *(forward delay)* |
| **Forwarding** | ✅ | ✅ | — |
| *Disabled* | — | — | Port shutdown |

> ⏱ **Tổng thời gian hội tụ STP cổ điển: 30–50 giây.**
> Đây là lý do PC cắm vào mạng phải đợi lâu mới có IP (DHCP timeout trước khi port
> forwarding) — và là lý do **PortFast** ra đời (Lesson 16).

### BPDU

**BPDU** (Bridge Protocol Data Unit) = gói switch dùng để nói chuyện STP với nhau.
Root bridge gửi mỗi **2 giây** (hello time). Switch khác nhận, cập nhật, chuyển tiếp.

Không nhận được BPDU trong **20 giây** (max age) → coi như đường tới root đã chết → bầu lại.

---

## 4. Why? — vì sao vẫn phải có redundant link

> **Nếu không nối dự phòng thì có cần STP không?**

Không cần. Nhưng bạn sẽ có một mạng mà **đứt một sợi dây là mất cả tầng**.

| | Không dự phòng | Có dự phòng + STP |
|---|---|---|
| Đứt một uplink | Mất cả switch đó | STP mở port backup, **tự khôi phục** |
| Thay switch | Phải cắt mạng | Chuyển traffic sang đường kia trước |
| Rủi ro loop | Không có | Có — **STP lo** |

> 🔧 Nói cách khác: **STP là cái giá phải trả để có dự phòng.**
> Không ai muốn STP; người ta muốn **redundancy**, và STP là điều kiện để có nó an toàn.

> 🏭 Và đây là lý do **không bao giờ tắt STP** trên switch production, kể cả khi
> "chắc chắn không có vòng nào". Một sợi dây cắm nhầm là đủ để sập cả công ty.

---

## 5. How does it work? — ví dụ đầy đủ

```text
Topology:            SW1 ═══(1G)═══ SW2
                      ║              ║
                     (1G)           (1G)
                      ║              ║
                     SW3 ═══(1G)═══ SW4

Bridge ID (giả định, VLAN 1):
  SW1: 32769 + MAC aaaa.aaaa.aaaa   ← thấp nhất
  SW2: 32769 + MAC bbbb.bbbb.bbbb
  SW3: 32769 + MAC cccc.cccc.cccc
  SW4: 32769 + MAC dddd.dddd.dddd   ← cao nhất
```

### Bước 1 — Bầu Root Bridge

Mọi switch priority bằng nhau (32769) → **so MAC** → **SW1 có MAC thấp nhất → ROOT**.

> ⚠️ Chú ý điều này: để mặc định, root bridge được chọn theo **MAC thấp nhất** — tức là
> thường là **switch cũ nhất** trong mạng. Hoàn toàn ngẫu nhiên về mặt thiết kế.

### Bước 2 — Bầu Root Port (mỗi switch non-root)

| Switch | Đường về root | Cost | Root Port |
|---|---|:---:|---|
| SW2 | Trực tiếp SW1 | 4 | Port nối SW1 |
| SW3 | Trực tiếp SW1 | 4 | Port nối SW1 |
| SW4 | Qua SW2: 4+4 = 8<br>Qua SW3: 4+4 = 8 | 8 | **Hoà** → phá hoà bằng Bridge ID láng giềng:<br>SW2 (bbbb) < SW3 (cccc) → **chọn port nối SW2** |

### Bước 3 — Bầu Designated Port (mỗi segment)

| Segment | Ứng viên | Thắng |
|---|---|---|
| SW1–SW2 | SW1 (cost 0, root) | **SW1** — mọi port của root đều là DP |
| SW1–SW3 | SW1 | **SW1** |
| SW2–SW4 | SW2 (cost 4) vs SW4 (cost 8) | **SW2** |
| SW3–SW4 | SW3 (cost 4) vs SW4 (cost 8) | **SW3** |

### Kết quả

```text
             SW1 (ROOT)
          DP ║        ║ DP
             ║        ║
         RP  ║        ║ RP
            SW2      SW3
          DP ║        ║ DP
             ║        ║
         RP  ║        ✗ BLOCKED   ← port SW4 nối SW3
            SW4 ─────┘
```

Port của **SW4 nối SW3** bị block. Nó là port duy nhất không phải RP cũng không phải DP.

### Khi link SW1–SW2 chết

```text
1. SW2 không nhận BPDU từ SW1 nữa
2. Sau 20 giây (max age) → SW2 coi đường đó đã mất
3. Tính lại: SW2 giờ phải đi qua SW4 → SW3 → SW1, cost = 4+4+4 = 12
4. SW4 thấy đường qua SW2 giờ cost cao hơn → mở lại port nối SW3
5. Qua Listening (15s) → Learning (15s) → Forwarding

Tổng: ~50 giây mạng gián đoạn.
```

> ⏱ **50 giây là rất lâu** với người dùng. Đây chính là động lực sinh ra **RSTP**
> (Lesson 16) — hội tụ dưới 1 giây.

---

## 6. Packet Flow — BPDU

| Trường | Giá trị |
|---|---|
| Dst MAC | `01:80:C2:00:00:00` *(multicast dành riêng cho STP)* |
| Src MAC | MAC của port gửi |
| Chu kỳ | **2 giây** (hello time) |
| Hướng đi | Root gửi ra; switch khác nhận ở RP, chuyển tiếp ra DP |

BPDU chứa: **Root Bridge ID** · **Root Path Cost** · **Sender Bridge ID** · **Port ID** ·
các timer (hello, max age, forward delay).

> 🔑 Switch không "hỏi" nhau — nó chỉ **nghe BPDU và tự suy ra** vị trí của mình trong cây.
> Mọi switch đều nhận cùng một thông tin và tính ra cùng một kết quả. STP là thuật toán
> **phân tán, không có bộ điều phối trung tâm**.

---

## 7. Real-world Example

🏭 **Root bridge nằm nhầm chỗ — lỗi thiết kế phổ biến nhất**

Để mặc định, root bridge = switch có MAC thấp nhất = thường là **switch access cũ nhất**
ở một góc nào đó. Hậu quả:

```text
Thiết kế mong muốn:            Thực tế khi để mặc định:

  Core (root)                    SW-ACC-T3 (root — switch cũ ở tầng 3)
   ╱    ╲                              ╲
Dist1  Dist2                          Core
  │      │                            ╱   ╲
Access Access                     Dist1   Dist2
                                    │       │
→ traffic đi thẳng              → traffic đi VÒNG qua tầng 3
```

Traffic giữa hai tầng phải đi vòng lên switch access ở tầng 3 rồi quay xuống.
Mạng vẫn "chạy", chỉ là chậm một cách khó hiểu.

**Luôn chỉ định root bridge bằng tay:**

```cisco
SW-CORE1(config)# spanning-tree vlan 1-100 root primary      ! root chính
SW-CORE2(config)# spanning-tree vlan 1-100 root secondary    ! root dự phòng
```

🏭 **Broadcast storm — nhận biết trong 10 giây**

| Dấu hiệu | Ý nghĩa |
|---|---|
| **Đèn port nháy đồng loạt, cùng nhịp** | Frame đang chạy vòng |
| Không SSH được vào switch | CPU 100% |
| `show processes cpu` — CPU rất cao | Control plane quá tải |
| Mọi thứ chậm/đứng, kể cả máy cùng VLAN | Băng thông bị chiếm hết |

**Xử lý khẩn cấp:** rút uplink dự phòng → mạng hồi lại → rồi mới điều tra.

🏭 **PVST+ — mỗi VLAN một cây**

Cisco chạy **PVST+** (Per-VLAN Spanning Tree Plus): **mỗi VLAN có một instance STP riêng**,
root riêng, port block riêng.

Lợi ích: load balancing — VLAN 10 root ở SW-CORE1, VLAN 20 root ở SW-CORE2 →
cả hai uplink đều được dùng thay vì một cái nằm không.

```cisco
SW-CORE1(config)# spanning-tree vlan 10,30,50 root primary
SW-CORE2(config)# spanning-tree vlan 20,40,60 root primary
```

Cái giá: nhiều VLAN = nhiều instance = tốn CPU/RAM switch. Đó là lý do **MST** ra đời
(gom nhiều VLAN vào một instance) — bạn học ở CCNP.

---

## 8. Cisco CLI

```cisco
! ═══════ XEM ═══════
SW1# show spanning-tree
SW1# show spanning-tree vlan 10
SW1# show spanning-tree root
SW1# show spanning-tree interface Gi1/0/1
SW1# show spanning-tree summary

! ═══════ CHỈ ĐỊNH ROOT BRIDGE ═══════
! Cách 1 — macro (IOS tự tính priority phù hợp)
SW1(config)# spanning-tree vlan 1-100 root primary
SW2(config)# spanning-tree vlan 1-100 root secondary

! Cách 2 — đặt priority thủ công (bội số 4096)
SW1(config)# spanning-tree vlan 10 priority 4096
SW2(config)# spanning-tree vlan 10 priority 8192

! ═══════ ĐIỀU KHIỂN ĐƯỜNG ĐI ═══════
SW1(config)# interface GigabitEthernet1/0/1
SW1(config-if)# spanning-tree vlan 10 cost 10          ! đổi cost → đổi đường
SW1(config-if)# spanning-tree vlan 10 port-priority 64  ! phá hoà trên cùng switch

! ═══════ CHẾ ĐỘ STP ═══════
SW1(config)# spanning-tree mode pvst          ! PVST+ (mặc định Cisco)
SW1(config)# spanning-tree mode rapid-pvst    ! RSTP — NÊN DÙNG (Lesson 16)
SW1(config)# spanning-tree mode mst           ! MST (CCNP)

! ═══════ TIMER — hiếm khi nên đổi ═══════
SW1(config)# spanning-tree vlan 10 hello-time 2
SW1(config)# spanning-tree vlan 10 forward-time 15
SW1(config)# spanning-tree vlan 10 max-age 20
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `root primary` | Đặt priority **24576** (hoặc thấp hơn root hiện tại 4096) | Macro — IOS tính giúp |
| `root secondary` | Đặt priority **28672** | Root dự phòng |
| `priority <N>` | Đặt tay | Chỉ nhận **bội số 4096** |
| `cost <N>` trên interface | Đổi đường đi về root | Ảnh hưởng **chính switch này** |
| `port-priority <N>` | Phá hoà khi 2 port cùng switch về cùng láng giềng | Hiếm dùng |

> ⚠️ **Đổi timer là việc nguy hiểm.** Nếu đổi, phải đổi **trên root bridge** — root
> phát timer cho cả cây. Đổi lệch nhau gây hội tụ sai. Thực tế: đừng đổi, dùng RSTP thay.

> **Khác biệt platform:** PVST+ và Rapid-PVST+ là **của Cisco**. Switch hãng khác dùng
> STP/RSTP/MST chuẩn IEEE. Nối Cisco với non-Cisco → dùng **MST** hoặc để VLAN 1 làm
> cầu nối. NX-OS mặc định đã là **Rapid-PVST+**.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW2# show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol ieee
  Root ID    Priority    24586
             Address     aaaa.aaaa.aaaa
             Cost        4
             Port        1 (GigabitEthernet1/0/1)
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     bbbb.bbbb.bbbb
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- ----
Gi1/0/1          Root FWD 4         128.1    P2p
Gi1/0/2          Desg FWD 4         128.2    P2p
Gi1/0/3          Altn BLK 4         128.3    P2p
```

**Đọc output này theo 4 bước:**

| # | Nhìn gì | Ở đây cho biết |
|:---:|---|---|
| 1 | `Root ID Address` vs `Bridge ID Address` | Khác nhau → **switch này KHÔNG phải root** |
| 2 | `Root ID Priority 24586` | `24576 + 10` → ai đó đã đặt `root primary` ✅ |
| 3 | `Root ID Cost 4` | Cách root **một link 1G** |
| 4 | Cột `Role` / `Sts` | Thấy ngay port nào làm gì |

| `Role` | Nghĩa | `Sts` |
|---|---|---|
| `Root` | Đường về root | `FWD` |
| `Desg` | Designated — forward cho segment | `FWD` |
| `Altn` | Alternate — **đường dự phòng về root** | `BLK` |
| `Back` | Backup — dự phòng cho segment (hiếm) | `BLK` |

> 🔑 **Nếu `Root ID Address` = `Bridge ID Address`** → switch này **chính là root**,
> và mọi port của nó đều là `Desg FWD`.

```text
# output điển hình — tự verify trên lab của bạn
SW1# show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: VLAN0010, VLAN0030
...
Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0010                      0         0        0          4          4
VLAN0020                      1         0        0          3          4
```

> Cột `Blocking` cho biết **có bao nhiêu port đang bị chặn** ở mỗi VLAN.
> `Blocking = 0` ở mọi VLAN trong một mạng **có vòng** là dấu hiệu đáng ngờ.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Mạng treo, đèn port nháy đồng loạt | **Broadcast storm** do loop | `show processes cpu sorted` | Rút link dự phòng ngay, rồi điều tra STP |
| Root bridge là switch access ở góc nhà | Để mặc định, MAC thấp nhất thắng | `show spanning-tree root` | `spanning-tree vlan X root primary` trên core |
| Traffic đi đường vòng khó hiểu | Root nằm sai chỗ | `show spanning-tree vlan X` | Chỉ định lại root |
| Mạng gián đoạn ~50 giây mỗi lần đứt link | STP cổ điển | `show spanning-tree summary` | Chuyển sang `rapid-pvst` *(Lesson 16)* |
| PC đợi rất lâu mới có IP | Port qua 30–50s Listening/Learning | `show spanning-tree interface <int>` | Bật **PortFast** *(Lesson 16)* |
| Port bất ngờ bị block | Có switch mới cắm vào, BPDU tốt hơn | `show spanning-tree` xem Root ID đổi chưa | Bật **Root Guard** *(Lesson 16)* |
| Root bridge **đổi** liên tục | Có thiết bị lạ phát BPDU | `show spanning-tree root` theo dõi | Root Guard + BPDU Guard |
| MAC flapping trong log | Loop L2 | `show mac address-table` | Kiểm tra STP, tìm dây thừa |
| Hai switch non-Cisco không hiểu nhau về STP | PVST+ là của Cisco | `show spanning-tree summary` | Dùng MST, hoặc chuẩn hoá VLAN 1 |

---

## 11. LAB

🧪 **[LAB 13 — STP: bầu root, port role, và chuyện gì xảy ra khi link chết](../labs/lab13-stp.md)**

## 12. Challenge

> Dùng topology ở mục 5. Tự làm trước khi mở đáp án.

1. Nếu bạn đặt `spanning-tree vlan 1 priority 4096` trên **SW4**, điều gì xảy ra?
   Vẽ lại cây mới và chỉ ra port nào bị block.
2. Trong output `show spanning-tree` ở mục 9, vì sao `Root ID Priority` là **24586**
   chứ không phải 24576?
3. Mạng có 4 switch nối vòng, tất cả link 1 Gbps. Bạn muốn traffic giữa SW2 và SW4
   **không** đi qua SW1. Nêu 2 cách làm.
4. Vì sao không nên để `Blocking = 0` ở mọi VLAN trong một mạng có redundant link?

<details>
<summary>Đáp án</summary>

**1.** SW4 (priority 4096) có Bridge ID **thấp nhất** → **SW4 trở thành root**.
Cây đảo ngược hoàn toàn:

```text
            SW4 (ROOT mới)
         DP ║        ║ DP
            ║        ║
        RP  ║        ║ RP
           SW2      SW3
         DP ║        ║ DP
            ║        ║
        RP  ║        ✗ BLOCKED
           SW1 ──────┘
```

Giờ **SW1** (root cũ) có một port bị block. Tính lại: SW1 về SW4 qua SW2 cost 8,
qua SW3 cũng cost 8 → hoà → phá hoà bằng Bridge ID láng giềng: SW2 (bbbb) < SW3 (cccc)
→ SW1 chọn port nối SW2 làm RP, **port nối SW3 bị block**.

👉 Bài học: đặt priority là cách **duy nhất** để kiểm soát topology. Để mặc định
nghĩa là giao quyết định cho địa chỉ MAC ngẫu nhiên.

**2.** Vì **Extended System ID**: Bridge ID = `priority + VLAN ID`.
`spanning-tree vlan 10 root primary` đặt priority **24576**, cộng VLAN ID **10**
→ hiển thị **24586**. Tương tự, mặc định 32768 ở VLAN 10 hiển thị 32778.

**3.** Hai cách:

| Cách | Lệnh | Cơ chế |
|---|---|---|
| **Đổi cost** | Trên SW2 và SW4: `spanning-tree vlan 1 cost 100` ở port nối SW1 | Làm đường qua SW1 "đắt" hơn → STP chọn đường khác |
| **Đổi root** | Đặt SW3 làm root primary | Đổi hẳn hình dạng cây |

Cách 1 chính xác hơn khi chỉ muốn chỉnh một đoạn. Cách 2 thay đổi toàn mạng.

**4.** Vì `Blocking = 0` trong mạng **có vòng vật lý** nghĩa là **STP không block gì cả** —
tức là nó **không nhìn thấy vòng**. Hai khả năng, đều nguy hiểm:

- STP đã bị **tắt** trên một switch nào đó → loop sẽ xảy ra
- Topology thật ra **không có vòng** → nghĩa là **không có dự phòng**, đứt dây là mất mạng

Cả hai đều đáng điều tra. Mạng khoẻ mạnh có redundancy **phải** có ít nhất một port blocked.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Bridge ID gồm gì · cost 1G/100M · 4 port state · BPDU gửi mỗi mấy giây | ⬜ |
| **L2** Explain | Giải thích vì sao loop L2 nguy hiểm hơn loop L3 | ⬜ |
| **L3** Configure | Chỉ định root primary/secondary, đổi cost để điều khiển đường đi | ⬜ |
| **L4** Troubleshoot | Cho `show spanning-tree` → nói ra root ở đâu, port nào block, vì sao | ⬜ |
| **L5** Design | Thiết kế STP cho 2 core + 4 access, có load balancing giữa các VLAN | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **Frame Ethernet không có TTL** → loop L2 nhân frame vô hạn → broadcast storm
- STP biến topology có vòng thành **cây logic không vòng**, giữ dự phòng vật lý
- **Bridge ID** = `priority (bội số 4096) + VLAN ID + MAC`
- Ba bước: **Root Bridge** (BID thấp nhất) → **Root Port** (mỗi switch 1) →
  **Designated Port** (mỗi segment 1). Còn lại → **Blocked**
- Phá hoà: cost → **BID láng giềng** → port priority láng giềng → port ID láng giềng
- Cost: 10G=2 · 1G=4 · 100M=19 · 10M=100
- State: Blocking (20s) → Listening (15s) → Learning (15s) → Forwarding = **30–50 giây**
- BPDU tới `01:80:C2:00:00:00`, mỗi **2 giây**
- ⭐ **Luôn chỉ định root bridge** — để mặc định là giao cho MAC ngẫu nhiên quyết định
- **PVST+** = mỗi VLAN một cây → load balancing được

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show spanning-tree vlan N` | Xem root, port role, port state |
| `show spanning-tree root` | Ai là root của từng VLAN |
| `show spanning-tree summary` | Tổng quan, đếm port blocking |
| `spanning-tree vlan N root primary` | **Chỉ định root** |
| `spanning-tree vlan N root secondary` | Root dự phòng |
| `spanning-tree vlan N cost <N>` | Điều khiển đường đi |
| `spanning-tree mode rapid-pvst` | Chuyển sang RSTP |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Để root bầu mặc định | Root là switch cũ nhất ở góc nhà, traffic đi vòng |
| Tắt STP vì "không có vòng" | Một dây cắm nhầm là sập mạng |
| Nghĩ priority đặt được số bất kỳ | Chỉ bội số **4096** |
| Quên Extended System ID khi đọc priority | 32778 = 32768 + VLAN 10 |
| Phá hoà bằng BID **của mình** | Phải dùng BID **của láng giềng** |
| Đổi timer trên switch không phải root | Root phát timer cho cả cây |
| Thấy `Blocking = 0` mà yên tâm | Có thể đang không có dự phòng, hoặc STP đã tắt |

## 15. Homework + cập nhật PROGRESS

1. Làm [LAB 13](../labs/lab13-stp.md) đầy đủ, kể cả mục BREAK.
2. Trên lab 4 switch: **dự đoán trước** ai sẽ là root và port nào block,
   rồi mới chạy `show spanning-tree` để kiểm chứng. Làm 3 lần với priority khác nhau.
3. Vẽ sơ đồ mạng công ty bạn, chạy `show spanning-tree root` trên một switch,
   đánh dấu root bridge nằm ở đâu. Nó có đúng chỗ không?

```markdown
- [YYYY-MM-DD] Lesson 15 — STP: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Bridge ID, 3 bước bầu chọn, tiêu chí phá hoà, cost, port state, đọc `show spanning-tree` |
| 🔧 **Engineer** | Luôn chỉ định root primary/secondary; dùng cost để điều khiển đường; PVST+ load balancing |
| 🏭 **Production** | Không bao giờ tắt STP; nhận biết storm trong 10 giây; root sai chỗ làm traffic đi vòng âm thầm |

### 🔗 Liên kết

- ⬅️ [Lesson 14 — Inter-VLAN Routing](./lesson-14-inter-vlan-routing.md)
- ➡️ [Lesson 16 — RSTP, PortFast, BPDU Guard](./lesson-16-rstp-portfast-bpduguard.md)
- 🧪 [LAB 13](../labs/lab13-stp.md)
- 🔜 Học sâu (MST, các loại Guard): [`CCNP-Encor` Module 02](https://github.com/hiepnguyen775/CCNP-Encor)
