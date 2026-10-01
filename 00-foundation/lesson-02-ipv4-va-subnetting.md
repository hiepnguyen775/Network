# LESSON 02 — IPv4 · Subnet Mask · Subnetting ⭐

> 📌 **Lesson mẫu.** Đây là lesson **quan trọng nhất của cả CCNA**.
> Không có kỹ năng nào trong network mà bạn dùng nhiều bằng subnetting.

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~4 giờ + luyện tập hằng ngày |
| **Prerequisite** | [Lesson 01](./lesson-01-osi-va-tcp-ip.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích được subnet mask làm gì, bằng lời, không dùng công thức
- [ ] Tính Network / Broadcast / First / Last / số host của bất kỳ `/x` **trong đầu, < 30 giây**
- [ ] Chia VLSM cho một công ty thật, không lãng phí và không chồng lấn
- [ ] Chuyển đổi giữa subnet mask và wildcard mask không cần nghĩ
- [ ] Nhìn IP `169.254.x.x` là biết ngay chuyện gì đang xảy ra

## 2. Prerequisite

- Lesson 01: OSI, IP nằm ở L3
- Biết đếm nhị phân tới 255 *(sẽ ôn lại ở §3)*

---

## 3. Concept

### IPv4 — 32 bit, chia 4 octet

```text
192  .  168  .  10   .  100
 │       │      │       │
11000000.10101000.00001010.01100100     ← 32 bit
```

Mỗi octet = 8 bit = 0 → 255. Giá trị từng vị trí bit:

| Bit | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Giá trị** | **128** | **64** | **32** | **16** | **8** | **4** | **2** | **1** |

> 💡 Chỉ cần thuộc hàng này. `192` = 128+64 → `11000000`. `224` = 128+64+32 → `11100000`.

### Subnet mask — đường kẻ chia IP làm hai phần

Mỗi IP gồm **phần mạng** và **phần host**. Subnet mask nói cho thiết bị biết đường kẻ nằm ở đâu:

```text
IP      192.168.10.100   →  11000000.10101000.00001010.01100100
Mask    255.255.255.0    →  11111111.11111111.11111111.00000000
                             └──── phần MẠNG ────────┘└─ HOST ─┘
```

- Bit mask **= 1** → vị trí đó thuộc **phần mạng**
- Bit mask **= 0** → vị trí đó thuộc **phần host**

**CIDR** `/24` chỉ là cách viết tắt: "có 24 bit 1 ở đầu".

### Ba địa chỉ đặc biệt trong mỗi subnet

| Loại | Phần host | Gán cho PC được? |
|---|---|:---:|
| **Network address** | toàn bộ bit = **0** | ❌ Đại diện cả subnet |
| **Broadcast address** | toàn bộ bit = **1** | ❌ Gửi tới mọi host trong subnet |
| **Host usable** | ở giữa | ✅ |

→ Vì vậy số host dùng được là `2^n − 2`, **không phải** `2^n`.

---

## 4. Why? — tại sao phải subnet

> **Nếu không subnet thì sao?**

Một công ty 300 máy đặt tất cả vào `10.0.0.0/8`. Hệ quả:

| Vấn đề | Cụ thể |
|---|---|
| **Broadcast domain khổng lồ** | Mọi ARP, DHCP, broadcast đi tới **tất cả** máy. Mạng chậm dần theo số máy. |
| **Không tách biệt được** | Máy khách trong phòng họp nhìn thấy server kế toán. Không có chỗ nào để đặt ACL. |
| **Không khoanh vùng được sự cố** | Một máy nhiễm virus phát broadcast → cả công ty chết, không cô lập được. |
| **Lãng phí địa chỉ** | `/8` cho 300 máy = phí 16 triệu địa chỉ. |

Subnetting cho bạn:

```text
10.0.1.0/24   → Sales      (có thể đặt ACL riêng)
10.0.2.0/24   → Kế toán    (chặn truy cập từ Sales)
10.0.3.0/24   → Server     (chỉ IT vào được)
10.0.99.0/24  → Management (tách hẳn, chỉ IT)
10.0.4.0/30   → WAN link   (đúng 2 IP, không phí)
```

Mỗi subnet = một **broadcast domain** riêng = một **ranh giới chính sách** riêng.

> 🔧 **Engineer:** subnet không chỉ để tiết kiệm IP. Nó là **đơn vị cơ bản của thiết kế mạng** —
> VLAN, ACL, routing, QoS, giám sát đều lấy subnet làm ranh giới. Chia subnet sai thì mọi thứ
> phía sau đều phải chắp vá.

---

## 5. How does it work?

### Thiết bị dùng subnet mask để làm gì?

Khi PC muốn gửi gói tới một IP đích, nó làm **đúng một phép toán**:

```text
1. IP của tôi      AND  mask của tôi   =  network của tôi
2. IP đích         AND  mask của tôi   =  network của đích (theo góc nhìn của tôi)
3. Hai kết quả giống nhau?
   ├─ CÓ   → cùng subnet  → ARP tìm MAC của chính máy đích, gửi thẳng
   └─ KHÔNG → khác subnet → ARP tìm MAC của DEFAULT GATEWAY, gửi cho router
```

**Ví dụ:** PC `192.168.10.100/26` muốn gửi tới `192.168.10.200`.

```text
100 → 01100100  AND  mask /26 (11000000 ở octet cuối) = 01000000 = 64
200 → 11001000  AND  mask /26                          = 11000000 = 192
64 ≠ 192  →  KHÁC subnet  →  gửi cho gateway
```

Dù hai địa chỉ **trông giống nhau** ở 3 octet đầu, chúng ở hai subnet khác nhau.

> ⚠️ 🏭 Đây là nguồn gốc của một sự cố kinh điển: hai máy đặt sai mask, một máy `/24`
> một máy `/26`. Máy A nghĩ cùng subnet nên gửi thẳng; máy B nghĩ khác subnet nên gửi qua router.
> **Kết quả: ping được một chiều.** Triệu chứng rất khó hiểu nếu không biết cơ chế này.

---

## 6. Packet Flow — subnet quyết định điều gì

| Tình huống | PC ARP tìm MAC của ai | Gói đi qua router? |
|---|---|:---:|
| Đích **cùng subnet** | MAC của **chính máy đích** | ❌ |
| Đích **khác subnet** | MAC của **default gateway** | ✅ |

**Điểm mấu chốt:** trong cả hai trường hợp, **IP đích trong header không bao giờ đổi** —
chỉ MAC đích là khác nhau. Subnet mask không nằm trong gói tin; nó chỉ tồn tại trong
**quyết định của host gửi**.

---

## 7. Real-world Example

Thiết kế IP cho một công ty 4 phòng ban, được cấp `10.0.0.0/24`:

| Phòng ban | Host cần | Lý do chọn prefix |
|---|:---:|---|
| Sales | 50 | `/26` cho 62 host — `/27` chỉ 30, không đủ |
| IT | 25 | `/27` cho 30 host — vừa đủ, có dư 5 |
| Kế toán | 12 | `/28` cho 14 host |
| WAN link | 2 | `/30` cho đúng 2 host |

> 🔧 Luôn cộng thêm **~30% dự phòng tăng trưởng**. Phòng 50 người hôm nay có thể 70 người
> sang năm. Đổi subnet đang chạy là việc đau đớn — phải đổi DHCP, ACL, route, firewall rule.

---

## 8. Cisco CLI

```cisco
! Gán IP cho interface router
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip address 10.0.0.1 255.255.255.192     ! /26
R1(config-if)# no shutdown

! SVI trên L3 switch
SW1(config)# interface vlan 10
SW1(config-if)# ip address 10.0.1.1 255.255.255.0
SW1(config-if)# no shutdown

! Dùng wildcard mask trong OSPF — NGƯỢC với subnet mask
R1(config)# router ospf 1
R1(config-router)# network 10.0.0.0 0.0.0.63 area 0    ! /26 → wildcard 0.0.0.63
```

| Lệnh | Làm gì | Khác biệt platform |
|---|---|---|
| `ip address <ip> <mask>` | Gán IP + mask | IOS/IOS-XE giống nhau |
| `no shutdown` | Bật interface | Router mặc định **shutdown**; switch port mặc định **không** |
| `network <ip> <wildcard> area N` | Chọn interface tham gia OSPF | NX-OS: cấu hình OSPF **trên interface**, không dùng `network` |

> ⚠️ **Lỗi phổ biến nhất ở đây:** gõ subnet mask thay vì wildcard mask trong `network`.
> IOS **nhận lệnh bình thường, không báo lỗi gì** — nhưng OSPF chạy sai interface.

---

## 9. Verification

```cisco
show ip interface brief
show ip interface GigabitEthernet0/0
show ip route connected
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet address is 10.0.0.1/26
  Broadcast address is 255.255.255.255
  MTU 1500 bytes
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route connected
      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.0.0.0/26 is directly connected, GigabitEthernet0/0
L        10.0.0.1/32 is directly connected, GigabitEthernet0/0
```

**Đọc gì:**

| Dòng | Ý nghĩa | Bất thường |
|---|---|---|
| `Internet address is 10.0.0.1/26` | IP + prefix đã gán | Prefix khác với thiết kế → sai mask |
| `C 10.0.0.0/26` | Subnet của interface | Subnet khác dự kiến → tính sai network |
| `L 10.0.0.1/32` | Chính IP của router | Luôn là `/32`, luôn đi kèm `C` |
| `line protocol is up` | L2 ok | `down` → kiểm tra cáp, encapsulation |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Ping gateway fail, dù IP "nhìn đúng" | Mask lệch → thật ra khác subnet | `show ip int brief`, `ipconfig` | Đồng bộ mask hai đầu |
| **Ping được một chiều** | Hai đầu mask khác nhau | So prefix ở cả hai máy | Sửa mask |
| PC nhận `169.254.x.x` | APIPA — DHCP không tới | `show ip dhcp pool`, kiểm tra VLAN port | Sửa VLAN / `ip helper-address` |
| OSPF không chạy trên interface | Dùng subnet mask thay wildcard | `show ip protocols` | Đổi sang wildcard mask |
| Hai subnet chồng lấn nhau | Chia VLSM không kiểm tra lại | Vẽ lại dải trên giấy | Chia lại từ đầu, lớn trước |

---

## 11. LAB

🧪 **[LAB 01 — VLSM cho công ty 4 phòng ban](../labs/lab01-vlsm-cong-ty-4-phong-ban.md)**

## 12. Challenge

> Tự làm hết rồi mới mở đáp án.

**A. Tính nhanh** — Network / First / Last / Broadcast / số host:

```
1. 172.16.45.130/25
2. 10.0.5.33/28
3. 192.168.200.19/29
4. 172.20.8.90/22
```

**B. Tư duy:**

5. Vì sao `/31` tồn tại dù công thức nói nó có 0 host usable?
6. Công ty có `192.168.1.0/24`, cần **6 subnet** đều nhau. Dùng prefix nào? Mỗi subnet mấy host?
7. Máy A `10.0.0.5/24`, máy B `10.0.0.200/26`. A ping B có được không? B ping A có được không?
   Giải thích **từng chiều**.

<details>
<summary>Đáp án</summary>

**A.**

| # | Network | First | Last | Broadcast | Host |
|:---:|---|---|---|---|:---:|
| 1 | 172.16.45.128 | .129 | .254 | .255 | 126 |
| 2 | 10.0.5.32 | .33 | .46 | .47 | 14 |
| 3 | 192.168.200.16 | .17 | .22 | .23 | 6 |
| 4 | 172.20.8.0 | 172.20.8.1 | 172.20.11.254 | 172.20.11.255 | 1022 |

**5.** RFC 3021 — trên link **point-to-point** không cần network/broadcast address, nên cả 2 địa chỉ
đều dùng được làm host. Tiết kiệm 50% IP so với `/30` khi có nhiều link WAN.

**6.** 6 subnet → cần mượn 3 bit (`2^3 = 8 ≥ 6`) → **`/27`**, mỗi subnet **30 host**.
Dải: `.0`, `.32`, `.64`, `.96`, `.128`, `.160` *(còn dư 2 subnet)*.

**7.** Đây là bẫy mask mismatch:
- **A (`/24`) ping B:** A tính `10.0.0.200 AND /24 = 10.0.0.0` = network của A → A nghĩ **cùng subnet**,
  ARP trực tiếp tìm MAC của B. B trả lời ARP → gói tới được B.
- **B (`/26`) ping A:** B tính `10.0.0.5 AND /26 = 10.0.0.0`, còn network của B là
  `10.0.0.192` → B nghĩ **khác subnet**, gửi cho default gateway.
- **Kết quả:** nếu có router làm gateway và có route, có thể vẫn thông nhưng đường đi bất đối xứng.
  Nếu không có gateway → B không gửi được, A gửi được nhưng không có reply. **Triệu chứng: ping một chiều.**

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Bảng magic number `/24`→`/30` · công thức số host · 3 dải private | ⬜ |
| **L2** Explain | Giải thích subnet mask cho người không biết IT trong 3 phút | ⬜ |
| **L3** Configure | Gán IP + mask cho 4 interface router theo một IP plan cho trước | ⬜ |
| **L4** Troubleshoot | Cho 2 máy ping một chiều → tìm ra mask mismatch | ⬜ |
| **L5** Design | Chia VLSM cho công ty 6 phòng ban + 3 WAN link từ một `/23` | ⬜ |

## 14. Summary

**Key concepts**

- Subnet mask chia IP thành phần mạng + phần host; `/x` = số bit 1
- Host usable = `2^(32−prefix) − 2` — **luôn trừ 2**
- Block size = `256 − octet_mask`
- VLSM: cấp **lớn trước**, tránh phân mảnh
- Wildcard mask = **nghịch đảo** subnet mask, dùng trong OSPF và ACL
- Thiết bị dùng mask để quyết định: gửi thẳng hay gửi qua gateway

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip address <ip> <mask>` | Gán IP cho interface |
| `show ip interface brief` | Kiểm tra IP + trạng thái |
| `show ip route connected` | Xem subnet nào đang trực tiếp kết nối |

**Common mistakes**

| Sai | Đúng |
|---|---|
| Số host = `2^n` | `2^n − 2` |
| `172.16.0.0/16` là dải private | `172.16.0.0/**12**` (từ 172.16 → 172.31) |
| Dùng subnet mask trong `network` của OSPF | Phải dùng **wildcard mask** |
| Chia VLSM từ nhỏ đến lớn | **Lớn trước**, nếu không sẽ phân mảnh |
| Gán IP network/broadcast cho PC | Hai địa chỉ này không gán được |
| Tính subnetting bằng máy tính | Đề thi và lab thật không cho — phải nhẩm |

## 15. Homework + cập nhật PROGRESS

**Homework**

1. Làm **10 bài tự luyện** trong [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md#8-tự-luyện), bấm giờ.
2. Mỗi ngày 10 câu subnetting trong 2 tuần tới — **đây là bài tập quan trọng nhất của cả Phase 0**.
3. Chia VLSM cho công ty bạn đang làm (hoặc tưởng tượng 6 phòng ban) từ một `/23`.

**Dán dòng này vào `PROGRESS.md`:**

```markdown
- [YYYY-MM-DD] Lesson 02 — IPv4 & Subnetting: DONE | cần ôn lại <điểm yếu của bạn>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Tính nhanh không máy tính; VLSM; wildcard mask; dải private |
| 🔧 **Engineer** | Thiết kế IP plan có dự phòng tăng trưởng; subnet là ranh giới của VLAN/ACL/route |
| 🏭 **Production** | Mask mismatch → ping một chiều. Đổi subnet đang chạy rất đắt — thiết kế đúng ngay từ đầu. `169.254.x.x` = DHCP hỏng. |

### 🔗 Liên kết

- ⬅️ Lesson trước: [`lesson-01-osi-va-tcp-ip.md`](./lesson-01-osi-va-tcp-ip.md)
- 🧮 Cheatsheet: [`subnetting.md`](../cheatsheets/subnetting.md)
- 🧪 Lab: [`lab01-vlsm-cong-ty-4-phong-ban.md`](../labs/lab01-vlsm-cong-ty-4-phong-ban.md)
- 🃏 Flashcard: [`00-foundation.md`](../flashcards/00-foundation.md)
