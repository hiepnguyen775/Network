# LAB 13 — STP: bầu root, port role, và chuyện gì xảy ra khi link chết

| | |
|---|---|
| **Phase** | 1 |
| **Lesson liên quan** | [Lesson 15 — STP](../01-switching/lesson-15-stp.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~3 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] **Dự đoán trước** root bridge và port bị block, rồi kiểm chứng bằng lệnh
- [ ] Đọc `show spanning-tree` và giải thích **từng dòng**
- [ ] Chỉ định root bridge và **quan sát cây thay đổi**
- [ ] Tự đo thời gian hội tụ khi đứt link
- [ ] Tạo và quan sát một **broadcast storm** thật *(trong lab an toàn)*

## 2. Prerequisite

- [Lesson 15](../01-switching/lesson-15-stp.md) — Bridge ID, 3 bước bầu chọn, cost
- [LAB 11](./lab11-vlan-va-trunk.md) — trunk

---

## 3. Topology

```text
        SW1 ═══════════ SW2
         ║               ║
         ║               ║
        SW3 ═══════════ SW4

4 switch nối vòng, tất cả link là trunk 1 Gbps (GigabitEthernet).
PC-A nối SW1 Fa0/1 (VLAN 10), PC-B nối SW4 Fa0/1 (VLAN 10).
```

| Thiết bị | Model | Vai trò |
|---|---|---|
| SW1–SW4 | 2960 | Tạo vòng kín để STP có việc làm |
| PC-A, PC-B | PC-PT | Kiểm chứng kết nối + đo thời gian hội tụ |

> 💡 **Ghi lại MAC của 4 switch** trước khi bắt đầu (`show version` hoặc `show interfaces`)
> — bạn cần nó để dự đoán root bridge.

| Switch | MAC |
|---|---|
| SW1 | |
| SW2 | |
| SW3 | |
| SW4 | |

---

## 4. Yêu cầu LAB

- [ ] VLAN 10 trên cả 4 switch, trunk giữa tất cả các link
- [ ] **Dự đoán** root bridge và port block **trước khi** chạy `show spanning-tree`
- [ ] Chỉ định SW1 làm root, quan sát cây thay đổi
- [ ] Đo thời gian hội tụ khi rút một link *(STP cổ điển vs RSTP)*
- [ ] Hoàn thành mục **8. BREAK**

---

## 5. Step-by-step

### Bước 1 — Cấu hình cơ bản 4 switch

```cisco
! Làm trên cả SW1, SW2, SW3, SW4 (đổi hostname)
hostname SW1
no ip domain-lookup

vlan 10
 name SALES
exit

! Mọi link liên switch đều là trunk
interface range GigabitEthernet0/1 - 2
 switchport mode trunk
 switchport trunk allowed vlan 10
exit

! Port nối PC (chỉ SW1 và SW4)
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
exit
```

> ⚠️ **Chưa bật PortFast** ở bước này — ta cần thấy port đi qua Listening/Learning
> ở Bài 3. Sẽ bật ở phần BREAK.

### Bước 2 — DỰ ĐOÁN trước khi xem

> 🔴 **Làm bước này trước khi gõ `show spanning-tree`.** Đây là phần có giá trị nhất của lab.

Mọi switch để priority mặc định (32768 + VLAN 10 = 32778) → so **MAC thấp nhất**.

| Câu hỏi | Dự đoán của tôi |
|---|---|
| Switch nào là **root**? Vì sao? | |
| Root Port của SW2 là port nào? Cost bao nhiêu? | |
| Root Port của SW3? | |
| Root Port của SW4? *(tính cả 2 đường, so cost)* | |
| Port nào bị **BLOCK**? Trên switch nào? | |
| Nếu hoà cost, tiêu chí phá hoà là gì? | |

### Bước 3 — Kiểm chứng

```cisco
SW1# show spanning-tree vlan 10
SW2# show spanning-tree vlan 10
SW3# show spanning-tree vlan 10
SW4# show spanning-tree vlan 10
```

Điền bảng thực tế và **so với dự đoán**:

| Switch | Là root? | Root Port | Designated Port | Blocked Port |
|---|:---:|---|---|---|
| SW1 | | | | |
| SW2 | | | | |
| SW3 | | | | |
| SW4 | | | | |

| | |
|---|---|
| Dự đoán của tôi **đúng/sai** ở chỗ nào? | |
| Nếu sai, tôi hiểu nhầm điều gì? | |

### Bước 4 — Chỉ định root bridge

```cisco
SW1(config)# spanning-tree vlan 10 root primary
SW2(config)# spanning-tree vlan 10 root secondary
```

```cisco
SW1# show spanning-tree vlan 10 | include Priority
```

| Câu hỏi | Trả lời |
|---|---|
| Priority của SW1 sau lệnh `root primary`? | |
| Vì sao con số đó **không phải** 24576 chẵn? | |
| Cây có thay đổi không? Port block có đổi chỗ? | |

### Bước 5 — Đo thời gian hội tụ

```text
1. Từ PC-A: ping -t 192.168.10.20   (ping liên tục tới PC-B)
2. Rút link SW1–SW2
3. ĐẾM số gói "Request timed out" trước khi ping chạy lại
4. Mỗi gói ping ≈ 1 giây → đó là thời gian hội tụ
```

| Chế độ | Lệnh bật | Số gói mất | Thời gian hội tụ |
|---|---|:---:|:---:|
| STP cổ điển | `spanning-tree mode pvst` | | |
| **RSTP** | `spanning-tree mode rapid-pvst` | | |

> 💡 Chênh lệch con số này là lý do tồn tại của Lesson 16. Ghi lại số thật của bạn.

---

## 6. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW4# show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     0001.aaaa.0001
             Cost        8
             Port        1 (GigabitEthernet0/1)
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     0004.dddd.0004

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- ----
Gi0/1            Root FWD 4         128.1    P2p
Gi0/2            Altn BLK 4         128.2    P2p
```

**Đọc theo 4 bước:**

| # | Nhìn gì | Ở ví dụ này |
|:---:|---|---|
| 1 | `Root ID Address` vs `Bridge ID Address` | Khác nhau → SW4 **không** phải root |
| 2 | `Root ID Priority` | `24586 = 24576 + VLAN 10` → có người đặt `root primary` |
| 3 | `Root ID Cost: 8` | Cách root **2 link 1G** (4+4) |
| 4 | Cột `Role`/`Sts` | `Gi0/2` là `Altn BLK` → **đây là port bị block** |

---

## 7. Challenge

1. Đặt `spanning-tree vlan 10 priority 4096` trên **SW4**. Vẽ lại cây mới.
   Port nào bị block bây giờ?
2. Quay về mặc định, rồi đặt `spanning-tree vlan 10 cost 100` trên port SW4 nối SW2.
   Cây thay đổi thế nào? Vì sao?
3. Tạo thêm VLAN 20, đặt SW1 làm root VLAN 10 và SW2 làm root VLAN 20.
   Chạy `show spanning-tree` — có mấy cây? Lợi ích là gì?
4. Vì sao `Root ID Cost` của SW2 là **4** còn của SW4 là **8**?

<details>
<summary>Gợi ý câu 3</summary>

Đây là **PVST+ load balancing**. Mỗi VLAN có một cây riêng, root riêng, port block riêng.
Kết quả: cả hai uplink đều được dùng — VLAN 10 đi một đường, VLAN 20 đi đường kia,
thay vì một link nằm không hoàn toàn.

</details>

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Tắt STP → **broadcast storm**

> ⚠️ **Chỉ làm trong Packet Tracer.** Không bao giờ làm trên mạng thật.

```cisco
SW1(config)# no spanning-tree vlan 10
SW2(config)# no spanning-tree vlan 10
SW3(config)# no spanning-tree vlan 10
SW4(config)# no spanning-tree vlan 10
```

Rồi từ PC-A ping một IP **không tồn tại** trong VLAN 10 (để sinh ARP broadcast).

| | |
|---|---|
| Dự đoán | |
| Quan sát: đèn port? | |
| Quan sát: Packet Tracer có chậm lại không? | |
| `show processes cpu sorted` hiện gì | |
| Vì sao frame không tự chết như gói IP? | |
| Cách khắc phục khẩn cấp | |

> 🔑 Đây là bài học đắt giá nhất của lab. Bật lại STP ngay sau khi quan sát xong:
> `spanning-tree vlan 10` trên cả 4 switch.

### Lỗi 2 — Root bridge nằm sai chỗ

```cisco
! Đặt SW4 (switch "access" ở xa) làm root
SW4(config)# spanning-tree vlan 10 priority 4096
```

| | |
|---|---|
| Mạng còn chạy không? | |
| Đường đi từ PC-A tới PC-B thay đổi thế nào? | |
| Vì sao đây là lỗi **khó phát hiện**? | |
| Lệnh phát hiện | |

### Lỗi 3 — PortFast trên port nối switch

```cisco
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# spanning-tree portfast        ! port này nối SW2!
```

| | |
|---|---|
| IOS có cảnh báo gì không? *(đọc kỹ)* | |
| Chuyện gì xảy ra khi link vừa lên? | |
| Vì sao nguy hiểm | |

### Lỗi 4 *(tự chọn)* — Đổi timer chỉ trên một switch

```cisco
SW3(config)# spanning-tree vlan 10 hello-time 1
```

Timer có được áp dụng không? Vì sao?

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Bước 2–3 — Dự đoán và kết quả

Giả sử MAC: SW1 `0001.aaaa.0001` < SW2 `0002.bbbb.0002` < SW3 `0003.cccc.0003` < SW4 `0004.dddd.0004`

| Switch | Root? | Root Port | Lý do |
|---|:---:|---|---|
| **SW1** | ✅ **ROOT** | — | MAC thấp nhất, priority bằng nhau |
| SW2 | | Port nối SW1 | Cost 4 — trực tiếp |
| SW3 | | Port nối SW1 | Cost 4 — trực tiếp |
| SW4 | | Port nối **SW2** | Hoà cost 8 (qua SW2 hoặc SW3)<br>→ phá hoà bằng **BID láng giềng**:<br>SW2 (`bbbb`) < SW3 (`cccc`) |

**Port bị block:** port của **SW4 nối SW3** — nó không phải Root Port, cũng không phải
Designated Port (vì SW3 cost 4 < SW4 cost 8 nên SW3 thắng segment đó).

```text
             SW1 (ROOT)
          DP ║        ║ DP
         RP  ║        ║ RP
            SW2      SW3
          DP ║        ║ DP
         RP  ║        ✗ BLOCKED
            SW4 ──────┘
```

### Bước 4 — `root primary`

Priority sau lệnh: **24586** = `24576 + 10 (VLAN ID)`.

Con số không chẵn vì **Extended System ID** — Bridge ID luôn cộng thêm VLAN ID.
`root primary` đặt priority 24576 (hoặc thấp hơn root hiện tại 4096 nếu root hiện tại
đã dưới 24576).

Cây **không đổi** trong trường hợp này, vì SW1 vốn đã là root. Nhưng giờ nó là root
**một cách chủ động** — không phụ thuộc vào việc có switch nào MAC thấp hơn cắm vào.

### Bước 5 — Thời gian hội tụ tham khảo

| Chế độ | Số gói mất | Thời gian |
|---|:---:|:---:|
| `pvst` (802.1D) | ~30–50 | **30–50 giây** |
| `rapid-pvst` (802.1w) | 0–2 | **< 2 giây** |

### Challenge

**1.** SW4 priority 4096 → Bridge ID thấp nhất → **SW4 thành root**. Cây đảo ngược:
SW2 và SW3 giờ có Root Port hướng về SW4. **SW1** có 2 đường về SW4 (qua SW2 cost 8,
qua SW3 cost 8) → hoà → phá hoà bằng BID láng giềng: SW2 (`bbbb`) < SW3 (`cccc`) →
SW1 chọn port nối SW2, **port nối SW3 bị block**.

**2.** Cost 100 trên port SW4↔SW2 làm đường qua SW2 có cost `100 + 4 = 104`,
còn qua SW3 vẫn `4 + 4 = 8`. SW4 chuyển **Root Port sang port nối SW3**,
và **port nối SW2 bị block**. Đây là cách điều khiển đường đi mà không đổi root.

**3.** Có **2 cây độc lập** — `show spanning-tree` hiển thị riêng `VLAN0010` và `VLAN0020`,
mỗi cái có root riêng, port block riêng. Lợi ích: **load balancing** — traffic VLAN 10
đi qua SW1, VLAN 20 đi qua SW2, cả hai uplink đều được dùng thay vì một cái nằm không.

**4.** `Root ID Cost` là **tổng cost trên đường về root**:

| Switch | Đường về root (SW1) | Cost |
|---|---|:---:|
| SW2 | SW2 → SW1, một link 1G | **4** |
| SW4 | SW4 → SW2 → SW1, hai link 1G | **4 + 4 = 8** |

### Giải thích các lỗi BREAK

**Lỗi 1 — Broadcast storm:**

| Quan sát | Giải thích |
|---|---|
| Đèn port nháy đồng loạt, cùng nhịp | Frame đang chạy vòng, nhân lên |
| Packet Tracer chậm/treo | CPU máy bạn phải mô phỏng hàng nghìn frame/giây |
| CPU switch ~100% | Control plane quá tải |
| Mọi ping đều fail | Băng thông bị chiếm hết |

**Vì sao frame không tự chết:** frame Ethernet **không có trường TTL**. Gói IP có TTL,
mỗi router giảm 1, về 0 là drop. Frame L2 không có cơ chế nào tương tự → chạy vòng vĩnh viễn.

**Khắc phục khẩn cấp:** rút một link trong vòng → mạng hồi ngay. Sau đó mới bật lại STP
và điều tra.

**Lỗi 2 — Root sai chỗ:**

**Mạng vẫn chạy bình thường** — đó chính là điều nguy hiểm. PC-A vẫn ping được PC-B.
Nhưng đường đi giờ phải vòng qua SW4 (switch access ở xa) thay vì đi thẳng.

Khó phát hiện vì: không có lỗi, không có log, không có cảnh báo. Chỉ có "mạng hơi chậm"
mà không ai giải thích được.

**Lệnh phát hiện:** `show spanning-tree root` — nhìn vào cột Root ID,
so với thiết kế mong muốn.

**Lỗi 3 — PortFast trên trunk:**

IOS **có cảnh báo**:

```text
# output điển hình — tự verify trên lab của bạn
%Warning: portfast should only be enabled on ports connected to a single
host. Connecting hubs, concentrators, switches, bridges, etc... to this
interface when portfast is enabled, can cause temporary bridging loops.
Use with CAUTION
```

Khi link lên, port **forwarding ngay** mà chưa kịp trao đổi BPDU để tính cây →
trong khoảng thời gian đó có **loop tạm thời**. Với mạng lớn, "tạm thời" đủ để gây storm.

**Lỗi 4 — Timer trên switch không phải root:**

Timer **không được áp dụng**. Root bridge **phát timer** trong BPDU cho cả cây;
switch khác nhận và dùng timer của root, bỏ qua giá trị cấu hình cục bộ của mình.

Muốn đổi timer, phải đổi **trên root bridge** — và thực tế thì **đừng đổi**, hãy dùng RSTP.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Dự đoán của tôi sai ở chỗ nào? Tôi hiểu nhầm điều gì? ___
- Thời gian hội tụ thật tôi đo được: PVST ___ giây · RSTP ___ giây
- Thứ bất ngờ nhất khi tạo broadcast storm: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
