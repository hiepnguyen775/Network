# LESSON 13 — VLAN · Access Port · Trunk 802.1Q · Native VLAN ⭐

> 📌 **Lesson mẫu.** Đây là lesson đầu tiên bạn thật sự gõ lệnh trên switch —
> và là nền của toàn bộ thiết kế mạng doanh nghiệp.

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | Lesson 11 (MAC table, broadcast domain), Lesson 12 (Cisco CLI) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích được VLAN sinh ra để giải quyết vấn đề gì — không dùng từ "chia mạng cho gọn"
- [ ] Cấu hình access port và trunk port, verify bằng `show`
- [ ] Mô tả được 802.1Q làm gì với frame, tag nằm ở đâu, dài bao nhiêu
- [ ] Giải thích native VLAN và hậu quả khi hai đầu đặt khác nhau
- [ ] Tự tìm được lỗi "PC cùng VLAN không ping được nhau"

## 2. Prerequisite

- Switch học MAC bằng source MAC của frame đi vào *(Lesson 11)*
- Broadcast domain là gì *(Lesson 11)*
- Vào được config mode, lưu được config *(Lesson 12)*

---

## 3. Concept

### VLAN là gì

**VLAN (Virtual LAN)** = chia một switch vật lý thành **nhiều switch logic độc lập**.

Port thuộc VLAN 10 và port thuộc VLAN 20 **không thể nói chuyện với nhau ở L2**, dù nằm trên
cùng một con switch, cắm cạnh nhau.

```text
        SWITCH VẬT LÝ (1 con)
┌───────────────────────────────────┐
│  VLAN 10          VLAN 20         │
│  ┌─────────┐      ┌─────────┐     │
│  │ Fa0/1   │      │ Fa0/3   │     │   ← hai "switch ảo"
│  │ Fa0/2   │      │ Fa0/4   │     │     hoàn toàn tách biệt
│  └─────────┘      └─────────┘     │
└───────────────────────────────────┘
      PC-A, PC-B        PC-C, PC-D

PC-A ↔ PC-B : ✅ nói chuyện được (cùng VLAN)
PC-A ↔ PC-C : ❌ không, trừ khi có thiết bị L3
```

### Access port vs Trunk port

| | **Access port** | **Trunk port** |
|---|---|---|
| Chở bao nhiêu VLAN | **Một** | **Nhiều** |
| Frame có tag không | **Không tag** | **Có tag 802.1Q** (trừ native VLAN) |
| Nối với | PC, máy in, AP (thường) | Switch khác, router, server ảo hoá |
| Lệnh | `switchport mode access` | `switchport mode trunk` |

### 802.1Q — tag trông thế nào

```text
Frame thường:
[ Dst MAC │ Src MAC │ EtherType │ Payload │ FCS ]

Frame có tag 802.1Q:
[ Dst MAC │ Src MAC │ 802.1Q TAG │ EtherType │ Payload │ FCS ]
                     └─ 4 byte ─┘
                        ├─ TPID 2 byte = 0x8100
                        └─ TCI  2 byte: Priority(3) + DEI(1) + VLAN ID(12 bit)
```

- VLAN ID dài **12 bit** → `0` đến `4095`, dùng được **1 → 4094**
- Tag được **chèn vào giữa** Source MAC và EtherType — không phải thêm ở đầu frame

### Native VLAN

Trên trunk, **đúng một VLAN** được truyền **không tag** — đó là **native VLAN** (mặc định VLAN 1).

Lý do tồn tại: tương thích ngược với thiết bị không hiểu 802.1Q.

---

## 4. Why? — tại sao cần VLAN

> **Nếu không có VLAN thì sao?**

Một công ty 200 máy, tất cả trên cùng một switch stack, không VLAN:

| Vấn đề | Cụ thể |
|---|---|
| **Một broadcast domain khổng lồ** | Mọi ARP/DHCP/broadcast đi tới cả 200 máy. Mạng chậm dần. |
| **Không có ranh giới bảo mật** | Máy khách ở phòng họp nằm cùng L2 với server kế toán. Không có chỗ nào đặt ACL — ACL là L3, mà ở đây không có hop L3 nào. |
| **Bị trói vào vị trí vật lý** | Muốn tách phòng Kế toán phải **mua switch riêng và kéo dây riêng**. |
| **Sự cố lan toàn bộ** | Một máy nhiễm virus phát broadcast → cả công ty chết. |

VLAN giải quyết cả bốn bằng phần mềm, không tốn một mét cáp nào:

| Nhu cầu | VLAN cho bạn |
|---|---|
| Chia broadcast domain | Mỗi VLAN = 1 broadcast domain |
| Tách biệt bảo mật | Muốn đi giữa VLAN **bắt buộc** qua L3 → có chỗ đặt ACL |
| Linh hoạt vị trí | Nhân viên kế toán ngồi tầng 3 vẫn vào VLAN kế toán |
| Giảm chi phí | Một switch phục vụ nhiều "mạng" |

> 🔧 **Engineer — câu đáng nhớ nhất của lesson này:**
> VLAN **tạo ra ranh giới**, nhưng chính vì thế nó **tạo ra nhu cầu routing**.
> Chia VLAN mà quên thiết kế inter-VLAN routing là dựng tường rồi quên làm cửa.

---

## 5. How does it work?

### Switch xử lý frame thế nào

```text
Frame đi VÀO access port (VLAN 10):
  1. Switch ghi nhận: "frame này thuộc VLAN 10"
  2. Học source MAC vào MAC table, GẮN KÈM VLAN 10
  3. Tra destination MAC — chỉ trong phạm vi VLAN 10
  4. Không thấy → flood, nhưng CHỈ ra các port thuộc VLAN 10

Frame đi RA trunk port:
  5. Chèn tag 802.1Q với VLAN ID = 10
  6. (Nếu VLAN 10 là native VLAN → KHÔNG chèn tag)

Frame đi VÀO trunk port ở switch kế tiếp:
  7. Đọc tag → biết thuộc VLAN 10 → gỡ tag
  8. Tiếp tục xử lý trong phạm vi VLAN 10
```

> 💡 Mấu chốt: **MAC table của switch có cột VLAN.** Cùng một MAC có thể tồn tại ở hai VLAN
> khác nhau mà không xung đột, vì switch tra cứu theo cặp `(VLAN, MAC)`.

### Vì sao native VLAN mismatch nguy hiểm

```text
SW1 (native VLAN 1)  ←──trunk──→  SW2 (native VLAN 99)

SW1 gửi frame của VLAN 1  → KHÔNG tag (vì là native của nó)
SW2 nhận frame KHÔNG tag  → gán vào VLAN 99 (native của nó)

→ Traffic VLAN 1 "rơi" sang VLAN 99.
```

Đây vừa là lỗi hoạt động, vừa là **lỗ hổng bảo mật** (VLAN hopping). IOS phát hiện qua CDP
và log cảnh báo:

```text
# output điển hình — tự verify trên lab của bạn
%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1), with SW2 GigabitEthernet0/1 (99).
```

---

## 6. Packet Flow

PC-A (VLAN 10, trên SW1) ping PC-B (VLAN 10, trên SW2), qua trunk.

| Bước | Ở đâu | Chuyện gì xảy ra |
|:---:|---|---|
| 1 | PC-A | Đích cùng subnet → ARP tìm MAC của PC-B |
| 2 | SW1 access port | Frame vào, gắn nhãn VLAN 10, học MAC PC-A vào `(VLAN 10, MAC-A)` |
| 3 | SW1 | Chưa biết MAC-B → flood **chỉ trong VLAN 10** + ra trunk |
| 4 | SW1 trunk out | **Chèn tag 802.1Q, VLAN ID = 10** |
| 5 | SW2 trunk in | Đọc tag → VLAN 10 → **gỡ tag** |
| 6 | SW2 | Flood trong VLAN 10 → PC-B nhận, trả lời ARP |
| 7 | — | Hai switch giờ đã học đủ MAC, các frame sau đi unicast thẳng |

**Src/Dst IP và MAC không đổi suốt đường** — vì không có router nào ở đây. Switch chỉ thêm
và gỡ tag, không chạm vào IP header.

> So sánh với Lesson 01: ở đó MAC đổi vì **có router**. Ở đây không có router, nên MAC giữ nguyên.
> Đây là khác biệt giữa **switching** và **routing**.

---

## 7. Real-world Example

🏭 Thiết kế VLAN điển hình của một văn phòng:

| VLAN | Tên | Subnet | Ghi chú |
|:---:|---|---|---|
| 10 | SALES | `10.0.10.0/24` | |
| 20 | KETOAN | `10.0.20.0/24` | ACL chặn từ VLAN 10, 50 |
| 30 | IT | `10.0.30.0/24` | VLAN duy nhất vào được VLAN 99 |
| 40 | SERVER | `10.0.40.0/24` | |
| 50 | GUEST | `10.0.50.0/24` | Chỉ ra Internet, chặn mọi VLAN nội bộ |
| 60 | VOICE | `10.0.60.0/24` | Voice VLAN cho IP phone |
| **99** | **MGMT** | `10.0.99.0/24` | Quản trị switch/AP — tách riêng |

Hai quy ước nên theo từ đầu:

1. **Không dùng VLAN 1 cho bất cứ thứ gì.** Nó là VLAN mặc định của mọi port —
   một port quên cấu hình sẽ tự rơi vào đó.
2. **Đổi native VLAN sang một VLAN không dùng** (vd 999), thống nhất trên mọi trunk.

---

## 8. Cisco CLI

```cisco
! ───── 1. Tạo VLAN ─────
SW1(config)# vlan 10
SW1(config-vlan)# name SALES
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name KETOAN
SW1(config-vlan)# exit

! ───── 2. Access port (nối PC) ─────
SW1(config)# interface range FastEthernet0/1 - 10
SW1(config-if-range)# switchport mode access          ! chốt cứng là access
SW1(config-if-range)# switchport access vlan 10       ! gán VLAN
SW1(config-if-range)# spanning-tree portfast          ! lên forwarding ngay
SW1(config-if-range)# spanning-tree bpduguard enable  ! chống cắm switch vào
SW1(config-if-range)# exit

! ───── 3. Trunk port (nối switch khác) ─────
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# switchport trunk encapsulation dot1q  ! chỉ switch cũ cần dòng này
SW1(config-if)# switchport mode trunk                 ! chốt cứng là trunk
SW1(config-if)# switchport trunk native vlan 999      ! đổi native, 2 đầu phải giống
SW1(config-if)# switchport trunk allowed vlan 10,20,99 ! chỉ cho VLAN cần thiết
SW1(config-if)# exit

SW1# copy running-config startup-config
```

### Giải thích từng dòng

| Lệnh | Làm gì | Vì sao quan trọng |
|---|---|---|
| `switchport mode access` | Chốt cứng là access | Không gõ → port ở `dynamic auto`, có thể tự thành trunk → lab lúc chạy lúc không |
| `switchport access vlan 10` | Gán port vào VLAN 10 | Nếu VLAN chưa tồn tại, IOS mới tự tạo |
| `spanning-tree portfast` | Bỏ qua listening/learning | PC không phải chờ 30 giây mới có mạng |
| `spanning-tree bpduguard enable` | Err-disable nếu nhận BPDU | Ai cắm switch vào port người dùng → chặn ngay, chống loop |
| `switchport mode trunk` | Chốt cứng là trunk | Tương tự access — tránh DTP tự thương lượng |
| `switchport trunk native vlan 999` | Đổi native VLAN | **Hai đầu phải giống nhau** |
| `switchport trunk allowed vlan ...` | Giới hạn VLAN qua trunk | Mặc định cho qua **tất cả** 1–4094 — nên thu hẹp |

### Khác biệt platform

| | IOS (switch cũ, 2960 trở về trước) | IOS-XE / switch mới | NX-OS |
|---|---|---|---|
| `switchport trunk encapsulation dot1q` | **Bắt buộc** (có ISL để chọn) | Không có lệnh này (chỉ dot1q) | Không có |
| Tạo VLAN | `vlan 10` | `vlan 10` | `vlan 10` |
| SVI | Mặc định có | Mặc định có | Cần `feature interface-vlan` |

> ⚠️ Gõ `switchport trunk encapsulation dot1q` trên switch mới sẽ báo **invalid input** —
> đó là bình thường, không phải bạn gõ sai.

---

## 9. Verification

```cisco
show vlan brief
show interfaces trunk
show interfaces FastEthernet0/1 switchport
show mac address-table
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show vlan brief
VLAN Name          Status    Ports
---- ------------- --------- -------------------------------
1    default       active    Fa0/11, Fa0/12, Fa0/13
10   SALES         active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
20   KETOAN        active    Fa0/5, Fa0/6
999  NATIVE-UNUSED active
```

> 🔍 Chú ý: **trunk port không xuất hiện trong `show vlan brief`** — nó không "thuộc" VLAN nào.
> Người mới hay hoảng khi không thấy Gi0/1 ở đây. Đó là bình thường.

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces trunk
Port    Mode    Encapsulation  Status     Native vlan
Gi0/1   on      802.1q         trunking   999

Port    Vlans allowed on trunk
Gi0/1   10,20,99

Port    Vlans allowed and active in management domain
Gi0/1   10,20,99

Port    Vlans in spanning tree forwarding state and not pruned
Gi0/1   10,20,99
```

**Đọc 4 bảng này theo thứ tự — đây là cách debug trunk hiệu quả nhất:**

| Bảng | Trả lời câu hỏi | Nếu VLAN thiếu ở đây |
|:---:|---|---|
| 1 | Trunk có lên không? Native VLAN là gì? | `Status` ≠ `trunking` → mode hai đầu lệch |
| 2 | VLAN nào được **cho phép**? | Thiếu → thêm vào `switchport trunk allowed vlan` |
| 3 | VLAN nào **tồn tại** trên switch? | Có ở bảng 2 mà thiếu ở đây → **chưa tạo VLAN** |
| 4 | VLAN nào đang **forward**? | Có ở bảng 3 mà thiếu ở đây → **STP đang block** |

> Đây là một trong những kỹ thuật đọc output giá trị nhất của Phase 1.
> Lần theo 4 bảng từ trên xuống, bạn biết chính xác VLAN chết ở tầng nào.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| 2 PC cùng VLAN, cùng switch, không ping được | Port không nằm đúng VLAN | `show vlan brief` | `switchport access vlan 10` |
| 2 PC cùng VLAN, khác switch, không ping được | Trunk không lên, hoặc VLAN không allowed | `show interfaces trunk` (4 bảng) | Sửa mode / `allowed vlan` |
| Trunk `Status: not-trunking` | Hai đầu lệch mode | `show interfaces <int> switchport` | Chốt cứng `mode trunk` cả hai đầu |
| VLAN có trong `allowed` nhưng không thông | Chưa `vlan 10` trên switch kia | `show vlan brief` ở cả hai | Tạo VLAN |
| Log `%CDP-4-NATIVE_VLAN_MISMATCH` | Native VLAN hai đầu khác | `show interfaces trunk` | Đồng bộ native VLAN |
| PC có mạng chập chờn khi vừa cắm | Chờ STP, thiếu PortFast | `show spanning-tree interface` | `spanning-tree portfast` |
| Port `err-disabled` sau khi cắm thiết bị | BPDU Guard đã chặn | `show interfaces status err-disabled` | Gỡ thiết bị, `shutdown` + `no shutdown` |

---

## 11. LAB

🧪 **LAB 11 — VLAN & Trunk giữa 2 switch** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu: 2 switch, 4 PC, 2 VLAN, 1 trunk, native VLAN đổi sang 999,
và **bắt buộc BREAK 3 lỗi**: sai VLAN access · native VLAN mismatch · VLAN không allowed trên trunk.

## 12. Challenge

> Tự trả lời trước khi mở đáp án.

1. Trunk `Status: trunking`, VLAN 10 nằm trong `allowed`, nhưng PC-A (VLAN 10, SW1) vẫn không
   ping được PC-B (VLAN 10, SW2). Kể **3 nguyên nhân** còn lại và lệnh kiểm chứng từng cái.
2. Vì sao nên đổi native VLAN sang một VLAN **không dùng** thay vì giữ VLAN 1?
3. Một server ảo hoá cần nhận traffic của 5 VLAN trên một card mạng. Port switch nối tới nó
   nên cấu hình thế nào? Vì sao không dùng access port?

<details>
<summary>Đáp án</summary>

**1.** Ba nguyên nhân còn lại:

| Nguyên nhân | Lệnh |
|---|---|
| VLAN 10 chưa được **tạo** trên SW2 | `show vlan brief` trên SW2 — xem bảng 3 của `show interfaces trunk` |
| STP đang **block** VLAN 10 trên trunk đó | `show spanning-tree vlan 10` — xem bảng 4 |
| PC đặt sai IP/mask → thật ra khác subnet | `ipconfig` trên cả 2 PC |

**2.** Hai lý do:
- **Bảo mật:** VLAN 1 là VLAN mặc định của mọi port. Giữ native = VLAN 1 làm cho tấn công
  VLAN hopping (double tagging) dễ hơn.
- **Vận hành:** port quên cấu hình tự rơi vào VLAN 1. Nếu VLAN 1 cũng là native của trunk,
  một sơ suất nhỏ thành lỗ hổng. Dùng VLAN 999 không có host nào thì traffic native rỗng.

**3.** Dùng **trunk port**, allowed đúng 5 VLAN đó. Access port chỉ chở được **một** VLAN
không tag — server sẽ không phân biệt được traffic thuộc VLAN nào. Hypervisor (ESXi, Proxmox)
đọc tag 802.1Q và phân phối cho đúng VM/vSwitch tương ứng.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | VLAN ID bao nhiêu bit · tag dài bao nhiêu byte · native VLAN mặc định | ⬜ |
| **L2** Explain | Giải thích vì sao VLAN tạo ra nhu cầu routing | ⬜ |
| **L3** Configure | Dựng 2 switch, 3 VLAN, 1 trunk, native 999, allowed đúng VLAN | ⬜ |
| **L4** Troubleshoot | Cho lab có 3 lỗi L2 ẩn → tìm hết trong 20 phút | ⬜ |
| **L5** Design | Thiết kế sơ đồ VLAN cho công ty 150 người, 3 tầng, có guest và voice | ⬜ |

## 14. Summary

**Key concepts**

- VLAN = chia một switch vật lý thành nhiều switch logic, mỗi VLAN là **một broadcast domain**
- Access port: 1 VLAN, không tag. Trunk port: nhiều VLAN, có tag 802.1Q
- Tag 802.1Q: **4 byte**, chèn giữa Src MAC và EtherType, VLAN ID **12 bit** (1–4094)
- Native VLAN: VLAN duy nhất không tag trên trunk — **hai đầu phải giống nhau**
- MAC table tra cứu theo cặp `(VLAN, MAC)`
- ⭐ VLAN **tạo ranh giới** → chính nó **tạo nhu cầu inter-VLAN routing**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show vlan brief` | VLAN tồn tại chưa, port nào thuộc VLAN nào |
| `show interfaces trunk` | Debug trunk — đọc đủ **4 bảng** |
| `show interfaces <int> switchport` | Chi tiết một port: mode, native, allowed |
| `switchport mode access` + `switchport access vlan N` | Cấu hình access |
| `switchport mode trunk` + `switchport trunk native vlan N` | Cấu hình trunk |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `switchport mode access/trunk` | Port ở `dynamic auto` → hành vi khó đoán |
| Native VLAN hai đầu khác nhau | Traffic rò giữa VLAN + lỗ hổng bảo mật |
| Quên tạo VLAN trên switch thứ hai | Trunk lên bình thường nhưng VLAN không thông |
| Để `allowed vlan` mặc định (tất cả) | Broadcast không cần thiết đi khắp trunk |
| Hoảng vì không thấy trunk port trong `show vlan brief` | Bình thường — trunk không thuộc VLAN nào |
| Dùng VLAN 1 cho production | Port quên cấu hình rơi vào đúng VLAN đang chạy thật |

## 15. Homework + cập nhật PROGRESS

**Homework**

1. Làm LAB 11 đầy đủ, **bao gồm 3 lỗi BREAK**.
2. Vẽ sơ đồ VLAN cho công ty bạn đang làm (hoặc tưởng tượng), kèm subnet từng VLAN.
3. Giải thích cho một đồng nghiệp không làm network: *"VLAN là gì và vì sao công ty cần nó"* — trong 3 phút.

**Dán dòng này vào `PROGRESS.md`:**

```markdown
- [YYYY-MM-DD] Lesson 13 — VLAN & Trunk: DONE | cần ôn lại <điểm yếu của bạn>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Access vs trunk; 802.1Q tag 4 byte; VLAN ID 12 bit; native VLAN; đọc `show vlan brief` và `show interfaces trunk` |
| 🔧 **Engineer** | Chốt cứng mode (không để DTP); thu hẹp `allowed vlan`; PortFast + BPDU Guard trên port người dùng |
| 🏭 **Production** | Không dùng VLAN 1; native VLAN = VLAN rỗng; quy ước đánh số VLAN thống nhất toàn công ty; trunk tới hypervisor phải allowed đúng VLAN của VM |

### 🔗 Liên kết

- ⬅️ Lesson trước: Lesson 12 — Cisco IOS CLI
- ➡️ Lesson sau: Lesson 14 — Inter-VLAN Routing (Router-on-a-Stick & SVI)
- 🔧 Cheatsheet: [`show-commands.md`](../cheatsheets/show-commands.md#2-layer-2--switching)
- 🃏 Flashcard: [`01-switching.md`](../flashcards/01-switching.md)
- 🧯 Sổ tay lỗi: [`SO-TAY-LOI.md`](../SO-TAY-LOI.md)
