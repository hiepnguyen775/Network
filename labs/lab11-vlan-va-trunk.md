# LAB 11 — VLAN & Trunk giữa 2 switch

| | |
|---|---|
| **Phase** | 1 |
| **Lesson liên quan** | [Lesson 13 — VLAN & Trunk](../01-switching/lesson-13-vlan-va-trunk.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Dựng 2 VLAN trải trên 2 switch, nối bằng trunk
- [ ] Chứng minh PC **cùng VLAN** ping được nhau dù khác switch
- [ ] Chứng minh PC **khác VLAN** không ping được nhau dù cùng switch
- [ ] Đọc thành thạo **4 bảng** của `show interfaces trunk`
- [ ] Tự tìm ra 3 lỗi L2 kinh điển từ triệu chứng

## 2. Prerequisite

- [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md) — CLI, config mode
- [Lesson 13](../01-switching/lesson-13-vlan-va-trunk.md) — VLAN, trunk, native VLAN

---

## 3. Topology

```text
   PC-A            PC-C                PC-B            PC-D
 VLAN 10         VLAN 20             VLAN 10         VLAN 20
 .10/24          .10/24              .11/24          .11/24
    │               │                   │               │
   Fa0/1          Fa0/3               Fa0/1          Fa0/3
    └──── SW1 ─────┘                   └──── SW2 ─────┘
            │ Gi0/1                             │ Gi0/1
            └═══════════ TRUNK ═════════════════┘
```

| Thiết bị | Model gợi ý |
|---|---|
| SW1, SW2 | 2960 |
| PC-A → PC-D | PC-PT |

## 4. IP Addressing Table

| Device | Switch | Port | VLAN | IP | Mask |
|---|---|---|:---:|---|---|
| PC-A | SW1 | Fa0/1 | 10 | `192.168.10.10` | `255.255.255.0` |
| PC-C | SW1 | Fa0/3 | 20 | `192.168.20.10` | `255.255.255.0` |
| PC-B | SW2 | Fa0/1 | 10 | `192.168.10.11` | `255.255.255.0` |
| PC-D | SW2 | Fa0/3 | 20 | `192.168.20.11` | `255.255.255.0` |

> Lab này **chưa có router** — PC không cần default gateway. Mục đích là chứng minh
> VLAN tách biệt ở L2, chưa làm inter-VLAN routing *(để dành LAB 12)*.

---

## 5. Yêu cầu LAB

- [ ] VLAN 10 (`SALES`) và VLAN 20 (`KETOAN`) tồn tại trên **cả hai** switch
- [ ] Trunk giữa SW1–SW2, native VLAN đổi sang **999**, allowed chỉ `10,20,999`
- [ ] PC-A ping được PC-B *(cùng VLAN 10, khác switch)* ✅
- [ ] PC-A **không** ping được PC-C *(khác VLAN, cùng switch)* ✅ *(đây là kết quả đúng)*
- [ ] `show interfaces trunk` hiển thị đúng 4 bảng
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### SW1

```cisco
enable
configure terminal
hostname SW1
no ip domain-lookup

! Tạo VLAN
vlan 10
 name SALES
vlan 20
 name KETOAN
vlan 999
 name NATIVE-UNUSED
exit

! Access port
interface FastEthernet0/1
 description PC-A
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
exit

interface FastEthernet0/3
 description PC-C
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
exit

! Trunk
interface GigabitEthernet0/1
 description TRUNK-TO-SW2
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,999
exit

end
copy running-config startup-config
```

### SW2

Làm **giống hệt**, chỉ đổi `hostname SW2` và description.

> 💡 Đây là chỗ thấy giá trị của "config chuẩn" ở Lesson 12 — cùng một đoạn, áp cho
> nhiều switch.

### PC

Gán IP theo bảng mục 4. Không điền default gateway.

---

## 7. Verification

```cisco
SW1# show vlan brief
SW1# show interfaces trunk
SW1# show interfaces FastEthernet0/1 switchport
SW1# show mac address-table
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show vlan brief
VLAN Name              Status    Ports
---- ----------------- --------- -------------------------------
1    default           active    Fa0/2, Fa0/4, Fa0/5, ...
10   SALES             active    Fa0/1
20   KETOAN            active    Fa0/3
999  NATIVE-UNUSED     active
```

> 🔍 **Gi0/1 không xuất hiện** ở bảng này — bình thường, trunk port không thuộc VLAN nào.

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces trunk
Port        Mode     Encapsulation  Status        Native vlan
Gi0/1       on       802.1q         trunking      999

Port        Vlans allowed on trunk
Gi0/1       10,20,999

Port        Vlans allowed and active in management domain
Gi0/1       10,20,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       10,20,999
```

### Bảng kiểm chứng

| Từ | Tới | Kết quả mong đợi | Thực tế |
|---|---|---|---|
| PC-A | PC-B | ✅ Ping được *(cùng VLAN 10)* | |
| PC-C | PC-D | ✅ Ping được *(cùng VLAN 20)* | |
| PC-A | PC-C | ❌ **Không** ping được *(khác VLAN)* | |
| PC-A | PC-D | ❌ **Không** ping được | |

> 🔑 Hai dòng cuối **thất bại là ĐÚNG**. Nếu ping được, nghĩa là VLAN chưa tách biệt —
> kiểm tra lại port có đúng VLAN không.

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

> Với mỗi lỗi: **dự đoán trước** → tạo lỗi → quan sát → tự tìm bằng lệnh
> (không nhìn lại chỗ mình vừa sửa).

### Lỗi 1 — Sai VLAN access

```cisco
SW2(config)# interface FastEthernet0/1
SW2(config-if)# switchport access vlan 20     ! PC-B lẽ ra phải ở VLAN 10
```

| | |
|---|---|
| Dự đoán | |
| Triệu chứng quan sát được | |
| Lệnh đã dùng để tìm | |
| Nguyên nhân gốc | |
| Cách sửa | |

### Lỗi 2 — Native VLAN mismatch

```cisco
SW2(config)# interface GigabitEthernet0/1
SW2(config-if)# switchport trunk native vlan 1     ! SW1 đang là 999
```

| | |
|---|---|
| Dự đoán | |
| **Log xuất hiện trên console** | |
| Lệnh đã dùng để tìm | |
| Vì sao đây vừa là lỗi vận hành vừa là lỗ hổng bảo mật | |
| Cách sửa | |

### Lỗi 3 — VLAN không nằm trong allowed list

```cisco
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# switchport trunk allowed vlan 10,999     ! bỏ VLAN 20
```

| | |
|---|---|
| Dự đoán | |
| VLAN nào còn thông, VLAN nào đứt | |
| **Bảng nào** trong `show interfaces trunk` lộ ra lỗi | |
| Cách sửa | |

### Lỗi 4 *(tự chọn)* — Quên tạo VLAN trên switch thứ hai

```cisco
SW2(config)# no vlan 20
```

Trunk vẫn `trunking`, VLAN 20 vẫn trong `allowed`. **Bảng nào** lộ ra vấn đề?

> Mỗi lỗi tìm ra → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Thêm PC-E vào SW1 Fa0/5, **không cấu hình VLAN** cho port đó. PC-E thuộc VLAN nào?
   Nó ping được ai?
2. Đổi `switchport mode trunk` trên SW2 thành `switchport mode dynamic auto`.
   Trunk còn lên không? Vì sao? *(Gợi ý: SW1 vẫn là `trunk`)*
3. Làm sao chứng minh bằng **Simulation mode** rằng frame của VLAN 10 có tag khi đi qua
   trunk, còn frame của VLAN 999 thì không?
4. Nếu bỏ hẳn VLAN 999 và để native VLAN = 1 ở cả hai đầu, mạng có chạy không?
   Vậy vì sao vẫn nên đổi?

<details>
<summary>Đáp án</summary>

**1.** PC-E thuộc **VLAN 1** (VLAN mặc định của mọi port chưa cấu hình).
Nó chỉ ping được thiết bị khác cũng đang ở VLAN 1. Vì VLAN 1 **không** nằm trong
`allowed vlan` của trunk, nó thậm chí không sang được SW2.

👉 Đây chính là lý do nên: (a) **không dùng VLAN 1 cho production**, và
(b) tắt + gán VLAN "hố đen" cho port không dùng.

**2.** **Trunk vẫn lên.** `dynamic auto` chấp nhận thành trunk nếu đầu kia chủ động
(`trunk` hoặc `dynamic desirable`). SW1 đang chốt cứng `trunk` → DTP thương lượng thành công.

**Nhưng không nên để vậy**: nếu ai đó đổi SW1 về `dynamic auto` nữa, cả hai cùng thụ động
→ trunk tụt về **access VLAN 1** → mất kết nối giữa các VLAN mà không có cảnh báo rõ ràng.
Luôn chốt cứng mode.

**3.** Trong Packet Tracer bật **Simulation mode**, lọc chỉ ICMP:

- Ping PC-A → PC-B (VLAN 10). Bấm vào gói tin khi nó **đang trên trunk**,
  xem tab *Inbound/Outbound PDU Details* → thấy trường **802.1Q** với VLAN ID = 10.
- Nếu có thiết bị ở VLAN 999 (native), gói của nó đi qua trunk sẽ **không có** trường 802.1Q.

**4.** **Mạng vẫn chạy bình thường.** Vẫn nên đổi vì hai lý do:

| Lý do | Giải thích |
|---|---|
| **Bảo mật** | VLAN 1 là VLAN mặc định của mọi port. Để native = VLAN 1 làm tấn công **VLAN hopping (double tagging)** dễ hơn |
| **Vận hành** | Port nào quên cấu hình sẽ tự rơi vào VLAN 1. Nếu VLAN 1 cũng là native của trunk, một sơ suất nhỏ thành đường rò. Dùng VLAN 999 không có host nào thì traffic native rỗng |

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

| # | Triệu chứng | Lệnh phát hiện | Nguyên nhân | Bảng/field lộ ra |
|:---:|---|---|---|---|
| 1 | PC-A không ping được PC-B, nhưng PC-B **ping được PC-D** | `show vlan brief` trên SW2 | Fa0/1 nằm VLAN 20 thay vì 10 | Cột `Ports` của VLAN 20 có Fa0/1 |
| 2 | Ping chập chờn; **log CDP cảnh báo** | `show interfaces trunk` | Native VLAN lệch | Cột `Native vlan`: SW1=999, SW2=1 |
| 3 | VLAN 10 thông, **VLAN 20 đứt** | `show interfaces trunk` | VLAN 20 bị loại khỏi allowed | **Bảng 2** `Vlans allowed on trunk` |
| 4 | VLAN 20 đứt, allowed vẫn có 20 | `show interfaces trunk` | VLAN 20 chưa tạo trên SW2 | **Bảng 3** `Vlans allowed and active` — thiếu 20 |

**Log của lỗi 2:**

```text
# output điển hình — tự verify trên lab của bạn
%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (999), with SW2 GigabitEthernet0/1 (1).
```

**Vì sao native VLAN mismatch vừa là lỗi vận hành vừa là lỗ hổng:**
SW1 gửi frame VLAN 999 **không tag** (vì là native của nó); SW2 nhận frame không tag
và gán vào **VLAN 1**. Traffic "rơi" từ VLAN này sang VLAN kia — phá vỡ sự tách biệt
mà VLAN sinh ra để đảm bảo.

### Cách phân biệt 4 bảng của `show interfaces trunk`

| Bảng | Trả lời | VLAN thiếu ở đây nghĩa là |
|:---:|---|---|
| 1 | Trunk có lên không? Native VLAN? | `Status` ≠ `trunking` → mode hai đầu lệch |
| 2 | VLAN nào được **cho phép**? | Thêm vào `switchport trunk allowed vlan` |
| 3 | VLAN nào **tồn tại** trên switch? | **Chưa tạo VLAN** trên switch này |
| 4 | VLAN nào đang **forward**? | **STP đang block** |

> Lần theo 4 bảng từ trên xuống là biết chính xác VLAN chết ở tầng nào.
> Đây là kỹ thuật đọc output giá trị nhất của Phase 1.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Lỗi nào khó tìm nhất? Vì sao? ___
- Bảng nào trong `show interfaces trunk` hữu dụng nhất với tôi? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
