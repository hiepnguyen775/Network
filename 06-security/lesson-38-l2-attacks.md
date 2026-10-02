# LESSON 38 — Tấn công Layer 2 & Phòng thủ tổng hợp

> 📌 Lesson tổng kết Phase 6. Nó gom mọi tấn công L2 vào một bức tranh, và cho bạn
> **một khối cấu hình chuẩn** áp được cho mọi access port.

| | |
|---|---|
| **Phase** | 6 — Security |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 13](../01-switching/lesson-13-vlan-va-trunk.md), [Lesson 16](../01-switching/lesson-16-rstp-portfast-bpduguard.md), [Lesson 17](../01-switching/lesson-17-etherchannel-port-security.md), [Lesson 37](./lesson-37-dhcp-snooping-dai.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Mô tả **6 tấn công L2** phổ biến và cách mỗi cái hoạt động
- [ ] Ánh xạ từng tấn công với **biện pháp phòng thủ** tương ứng
- [ ] Giải thích **VLAN hopping** bằng hai kỹ thuật: switch spoofing và double tagging
- [ ] Viết được **khối cấu hình chuẩn** cho access port
- [ ] Hiểu vì sao bảo mật L2 **không thể làm ở tầng khác**

## 2. Prerequisite

- VLAN, trunk, native VLAN, DTP *(Lesson 13)*
- BPDU Guard, Root Guard *(Lesson 16)*
- Port Security, MAC flooding *(Lesson 17)*
- DHCP Snooping, DAI, IPSG *(Lesson 37)*

---

## 3. Concept

### Bảng tổng hợp — tấn công ↔ phòng thủ

| # | Tấn công | Cách hoạt động | Phòng thủ |
|:---:|---|---|---|
| 1 | **MAC flooding** | Bơm hàng nghìn MAC giả → CAM table đầy → switch **flood như hub** → nghe lén | **Port Security** |
| 2 | **VLAN hopping** *(switch spoofing)* | Giả làm switch, dùng **DTP** để tự thương lượng thành trunk | **Tắt DTP**, chốt cứng mode |
| 3 | **VLAN hopping** *(double tagging)* | Gắn **2 tag**, lợi dụng native VLAN để nhảy VLAN | **Native VLAN rỗng**, không dùng VLAN 1 |
| 4 | **Rogue DHCP** | Cắm DHCP server giả → cấp gateway giả → MITM | **DHCP Snooping** |
| 5 | **ARP spoofing** | Gửi ARP Reply giả → chiếm vai trò gateway → MITM | **DAI** |
| 6 | **STP attack** | Gửi BPDU priority thấp → **cướp root bridge** → traffic đi qua mình | **BPDU Guard** + **Root Guard** |
| 7 | **CDP/LLDP recon** | Nghe CDP để biết model, IOS, IP thiết bị | **Tắt CDP** ở port người dùng |
| 8 | **DHCP starvation** | Gửi hàng nghìn Discover MAC giả → **vét cạn pool** | `ip dhcp snooping limit rate` |

### VLAN hopping — hai kỹ thuật

#### Kỹ thuật 1: Switch spoofing (lợi dụng DTP)

```text
1. Port switch để mặc định "dynamic auto" hoặc "dynamic desirable"
2. Kẻ tấn công cắm máy vào, chạy phần mềm giả làm switch
3. Gửi DTP frame: "tôi muốn làm trunk"
4. Switch đồng ý → port thành TRUNK
5. Kẻ tấn công giờ NHẬN ĐƯỢC TRAFFIC CỦA MỌI VLAN
```

**Phòng thủ:**

```cisco
interface range Gi1/0/1 - 44
 switchport mode access          ! chốt cứng
 switchport nonegotiate          ! TẮT DTP hoàn toàn
```

> ⭐ Đây là lý do quy tắc *"luôn chốt cứng `switchport mode access`"* từ
> [Lesson 13](../01-switching/lesson-13-vlan-va-trunk.md) không chỉ là chuyện vận hành —
> nó là **biện pháp bảo mật**.

#### Kỹ thuật 2: Double tagging

```text
Kẻ tấn công ở VLAN 1 (native), muốn gửi gói vào VLAN 20

1. Tạo frame với HAI tag:
      [tag ngoài: VLAN 1] [tag trong: VLAN 20] [payload]

2. Switch A nhận trên access port VLAN 1:
      - Gỡ tag ngoài (VLAN 1 = native → không tag khi ra trunk)
      - Đẩy ra trunk — frame giờ chỉ còn [tag VLAN 20]

3. Switch B nhận trên trunk:
      - Thấy tag VLAN 20 → đưa vào VLAN 20  ✅ TẤN CÔNG THÀNH CÔNG

→ Gói đã NHẢY từ VLAN 1 sang VLAN 20
```

> ⚠️ Tấn công này **chỉ một chiều** *(không nhận được reply)*, nhưng đủ để
> gửi lệnh tấn công, hoặc gây DoS vào VLAN khác.

**Phòng thủ:**

```cisco
! 1. Native VLAN là VLAN KHÔNG DÙNG, không có host nào
interface Gi1/0/48
 switchport trunk native vlan 999

! 2. KHÔNG dùng VLAN 1 cho bất cứ thứ gì
! 3. Bắt buộc tag cả native VLAN (nếu thiết bị hỗ trợ)
vlan dot1q tag native
```

> 🔑 Lệnh `vlan dot1q tag native` buộc **mọi** frame trên trunk đều có tag,
> kể cả native VLAN → **triệt tiêu hoàn toàn** double tagging.

### MAC flooding — chi tiết

```text
1. Kẻ tấn công chạy công cụ (macof, dsniff) bơm hàng nghìn frame
   với SOURCE MAC ngẫu nhiên
2. Switch học từng MAC vào CAM table
3. CAM table có giới hạn (8K–16K entry) → ĐẦY
4. Switch không học thêm được MAC THẬT nào nữa
5. Với mọi frame không biết đích → FLOOD ra mọi port
6. → Switch hoạt động như HUB → kẻ tấn công nghe được HẾT
```

**Phòng thủ:**

```cisco
switchport port-security
switchport port-security maximum 2
switchport port-security violation restrict
```

> 💡 Giới hạn **2 MAC/port** là đủ cho PC + IP phone, và chặn hoàn toàn MAC flooding
> *(vì kẻ tấn công cần hàng nghìn MAC)*.

### STP attack — cướp root bridge

```text
1. Kẻ tấn công gửi BPDU với priority RẤT THẤP (vd 0)
2. Mọi switch bầu lại → máy kẻ tấn công thành ROOT BRIDGE
3. Topology tính lại → traffic giữa các switch ĐI QUA máy đó
4. → MITM toàn mạng, hoặc DoS (máy đó không đủ sức chuyển tiếp)
```

**Phòng thủ:**

| Biện pháp | Đặt ở đâu | Làm gì |
|---|---|---|
| **BPDU Guard** | Port **access** | Nhận **bất kỳ** BPDU → `err-disabled` |
| **Root Guard** | Port **trunk hướng xuống** access | Nhận BPDU **tốt hơn** → `root-inconsistent` |

### CDP/LLDP — rò rỉ thông tin

```text
# output điển hình — kẻ tấn công chạy trên máy cắm vào port người dùng
Device ID: SW-ACCESS-T1
Platform: cisco WS-C2960X-48FPS-L
IOS Version: 15.2(7)E3
Management IP: 10.0.99.11
Native VLAN: 999
```

Chỉ cần cắm dây và nghe, kẻ tấn công biết: **model thiết bị, phiên bản IOS**
*(để tra lỗ hổng đã biết)*, **IP quản trị**, **native VLAN**.

```cisco
! Tắt CDP ở port người dùng
interface range Gi1/0/1 - 44
 no cdp enable
 no lldp transmit
 no lldp receive
```

> ⚠️ **Nhưng** CDP cần cho **IP phone** *(để nhận voice VLAN)*. Nếu có IP phone,
> giữ CDP nhưng tắt LLDP, hoặc chấp nhận đánh đổi.

---

## 4. Why?

> **Vì sao bảo mật L2 không thể làm ở tầng khác?**

```text
Mọi tấn công ở lesson này xảy ra TRONG CÙNG MỘT VLAN
     ↓
Traffic KHÔNG đi qua router hay firewall
     ↓
Chỉ có SWITCH mới nhìn thấy và chặn được
```

> ⭐ Firewall ở biên mạng, dù đắt tiền đến đâu, **hoàn toàn mù** với những gì
> xảy ra giữa hai máy trong cùng một broadcast domain.

> **Vì sao L2 dễ bị tấn công đến vậy?**

| Giao thức | Năm | Có xác thực? |
|---|:---:|:---:|
| Ethernet / MAC | 1980 | ❌ |
| ARP | 1982 | ❌ |
| STP | 1985 | ❌ *(có thể thêm nhưng ít dùng)* |
| DHCP | 1993 | ❌ |
| DTP | ~1995 | ❌ |

Tất cả được thiết kế khi mạng là **môi trường tin cậy** — mọi người trong cùng
một toà nhà, không có khái niệm kẻ thù bên trong.

> 🔑 **Chúng ta không sửa được các giao thức này** *(quá nhiều thiết bị phụ thuộc)*.
> Thay vào đó, ta **vá bằng tính năng của switch**: snooping, inspection, guard.

---

## 5. How does it work? — khối cấu hình chuẩn

> ⭐ Đây là sản phẩm quan trọng nhất của lesson. Áp dụng cho **mọi access port**
> trong doanh nghiệp.

```cisco
! ══════════════════════════════════════════════════════════
!  CẤU HÌNH TOÀN CỤC
! ══════════════════════════════════════════════════════════
! DHCP Snooping
ip dhcp snooping
ip dhcp snooping vlan 10,20,60,90
no ip dhcp snooping information option
ip dhcp snooping database flash:dhcp-snooping.db

! Dynamic ARP Inspection
ip arp inspection vlan 10,20,60,90
ip arp inspection validate src-mac dst-mac ip

! STP
spanning-tree mode rapid-pvst
spanning-tree portfast default
spanning-tree portfast bpduguard default
spanning-tree loopguard default

! Bắt buộc tag native VLAN — chống double tagging
vlan dot1q tag native

! Tự khôi phục port
errdisable recovery cause psecure-violation
errdisable recovery cause bpduguard
errdisable recovery cause arp-inspection
errdisable recovery cause dhcp-rate-limit
errdisable recovery interval 300

! ══════════════════════════════════════════════════════════
!  PORT NGƯỜI DÙNG  — khối chuẩn
! ══════════════════════════════════════════════════════════
interface range GigabitEthernet1/0/1 - 44
 description USER-PORT
 switchport mode access                       ! chống switch spoofing
 switchport access vlan 10
 switchport nonegotiate                       ! TẮT DTP
 switchport port-security                     ! chống MAC flooding
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip verify source                             ! IPSG — chống IP spoofing
 ip dhcp snooping limit rate 15               ! chống DHCP starvation
 spanning-tree portfast
 spanning-tree bpduguard enable               ! chống STP attack
 no cdp enable                                ! chống recon
 no shutdown

! ══════════════════════════════════════════════════════════
!  UPLINK  — trust nhưng vẫn bảo vệ
! ══════════════════════════════════════════════════════════
interface GigabitEthernet1/0/48
 description UPLINK-TO-DIST
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999             ! VLAN rỗng
 switchport trunk allowed vlan 10,20,60,90,99
 ip dhcp snooping trust                       ! ⭐ BẮT BUỘC
 ip arp inspection trust
 spanning-tree guard loop

! ══════════════════════════════════════════════════════════
!  PORT KHÔNG DÙNG  — tắt và cô lập
! ══════════════════════════════════════════════════════════
interface range GigabitEthernet1/0/45 - 47
 description UNUSED
 switchport mode access
 switchport access vlan 999                   ! VLAN "hố đen"
 shutdown
```

> 🔧 Lưu khối này vào `06-security/config-chuan-access-port.txt` và dùng cho
> mọi switch mới. Đây chính là *"config chuẩn"* đã nhắc tới từ
> [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md).

---

## 6. Packet Flow — double tagging từng bước

```text
Kẻ tấn công ở VLAN 1 (native của trunk), đích là VLAN 20

Frame gốc:
┌──────────┬──────────┬─────────────┬─────────────┬─────────┐
│ Dst MAC  │ Src MAC  │ tag VLAN 1  │ tag VLAN 20 │ payload │
└──────────┴──────────┴─────────────┴─────────────┴─────────┘

Tại SWITCH A (access port VLAN 1):
  - Nhận frame, coi như thuộc VLAN 1 (access port)
  - Đẩy ra trunk → VLAN 1 LÀ NATIVE → KHÔNG thêm tag
  - Nhưng tag VLAN 20 bên trong VẪN CÒN
┌──────────┬──────────┬─────────────┬─────────┐
│ Dst MAC  │ Src MAC  │ tag VLAN 20 │ payload │
└──────────┴──────────┴─────────────┴─────────┘

Tại SWITCH B (nhận trên trunk):
  - Thấy tag VLAN 20
  - → Đưa frame vào VLAN 20   ❌ ĐÃ NHẢY VLAN
```

**Vì sao `vlan dot1q tag native` triệt tiêu được:**

```text
Với lệnh đó, Switch A ĐẨY RA TRUNK VỚI CẢ TAG VLAN 1:
┌──────────┬──────────┬─────────────┬─────────────┬─────────┐
│ Dst MAC  │ Src MAC  │ tag VLAN 1  │ tag VLAN 20 │ payload │
└──────────┴──────────┴─────────────┴─────────────┴─────────┘

Switch B thấy tag ngoài = VLAN 1 → đưa vào VLAN 1 (đúng)
→ tag VLAN 20 chỉ là dữ liệu, không được xử lý
→ TẤN CÔNG THẤT BẠI ✅
```

---

## 7. Real-world Example

🏭 **Ba sự cố thật và nguyên nhân**

| Sự cố | Triệu chứng | Nguyên nhân | Lẽ ra phòng được bằng |
|---|---|---|---|
| Nhân viên cắm switch mini để có thêm cổng | Mạng chậm bất thường, có loop | Không có BPDU Guard | **BPDU Guard** |
| Khách cắm laptop vào ổ phòng họp, vào được server kế toán | Lộ dữ liệu | Port để VLAN production, không có cô lập | **VLAN guest + ACL** |
| "Một số máy mất mạng ngẫu nhiên" | Nhận IP sai dải | Router Wi-Fi cá nhân cắm vào mạng | **DHCP Snooping** |

🏭 **Thứ tự ưu tiên triển khai** — không làm được hết cùng lúc thì làm theo thứ tự này

| Ưu tiên | Biện pháp | Vì sao | Rủi ro gián đoạn |
|:---:|---|---|---|
| **1** | `switchport mode access` + `nonegotiate` | Chặn VLAN hopping, không có rủi ro | **Thấp** |
| **2** | **BPDU Guard** + PortFast | Chặn loop và STP attack | **Thấp** |
| **3** | **Port Security** `maximum 2` + `restrict` | Chặn MAC flooding | Thấp *(nếu dùng `restrict`)* |
| **4** | Tắt port không dùng + VLAN hố đen | Giảm bề mặt tấn công | Không |
| **5** | **DHCP Snooping** | Chặn rogue DHCP | ⚠️ **Trung bình** *(phải trust uplink)* |
| **6** | **DAI** | Chặn ARP spoofing | ⚠️ **Cao** *(cần binding table đầy)* |
| **7** | IPSG | Chặn IP spoofing | Trung bình |

> 🔧 Làm 1–4 trước — chúng gần như **không có rủi ro** và chặn được phần lớn tấn công.
> 5–7 cần chuẩn bị kỹ hơn *(xem [Lesson 37](./lesson-37-dhcp-snooping-dai.md))*.

🏭 **Bảo mật vật lý — thứ không có lệnh nào thay thế**

```text
Mọi biện pháp ở lesson này đều VÔ DỤNG nếu:
  - Tủ mạng không khoá  → ai cũng cắm được vào uplink (trust port!)
  - Có thể tiếp cận console  → password recovery (Lesson 12)
  - Ổ mạng ở khu vực công cộng không được tắt
```

> ⚠️ Password recovery **chỉ cần truy cập vật lý**. Khoá tủ mạng không phải
> chuyện phụ — nó là lớp phòng thủ đầu tiên.

---

## 8. Cisco CLI — kiểm tra & giám sát

```cisco
! ═══════ KIỂM TRA TỔNG THỂ ═══════
SW1# show interfaces status err-disabled
SW1# show errdisable recovery
SW1# show port-security
SW1# show ip dhcp snooping
SW1# show ip arp inspection
SW1# show ip verify source
SW1# show spanning-tree summary
SW1# show interfaces trunk
SW1# show cdp
SW1# show vlan dot1q tag native

! ═══════ TÌM THIẾT BỊ GÂY SỰ CỐ ═══════
SW1# show logging | include SECURITY|DAI|SNOOPING|SPANTREE
SW1# show mac address-table address 001a.2b3c.4d5e    ! MAC này ở port nào
SW1# show interfaces Gi1/0/9 status

! ═══════ KHÔI PHỤC PORT ═══════
SW1(config)# interface Gi1/0/9
SW1(config-if)# shutdown
SW1(config-if)# no shutdown
```

| Lệnh | Cho biết |
|---|---|
| `show interfaces status err-disabled` | ⭐ Port nào bị tắt và **vì sao** |
| `show logging \| include SECURITY\|DAI\|SNOOPING` | ⭐ Nhật ký mọi sự kiện bảo mật L2 |
| `show mac address-table address <mac>` | Truy ra **port vật lý** của thiết bị gây sự cố |
| `show vlan dot1q tag native` | Đã bật chống double tagging chưa |
| `show interfaces trunk` | Có port nào **vô tình thành trunk** không |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Gi1/0/9   USER-PORT          err-disabled bpduguard
Gi1/0/15  USER-PORT          err-disabled psecure-violation
```

| `Reason` | Nghĩa | Hành động |
|---|---|---|
| `bpduguard` | **Có switch cắm vào port người dùng** | Tìm và gỡ thiết bị |
| `psecure-violation` | MAC lạ vượt giới hạn | Xem `show port-security interface` |
| `arp-inspection` | Vượt rate limit DAI | Có thể là tấn công |
| `dhcp-rate-limit` | Vượt rate limit DHCP | Nghi **DHCP starvation** |
| `link-flap` | Cáp lỏng | Vấn đề vật lý |

```text
# output điển hình — log các sự kiện bảo mật
%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port Gi1/0/9 with BPDU Guard enabled. Disabling port.
%PORT_SECURITY-2-PSECURE_VIOLATION: Security violation on Gi1/0/15, caused by MAC 001a.2b3c.8888
%SW_DAI-4-DHCP_SNOOPING_DENY: 1 Invalid ARPs (Req) on Gi1/0/20, vlan 10
%DHCP_SNOOPING-5-DHCP_SNOOPING_UNTRUSTED_PORT: drop DHCPOFFER on untrusted port Gi1/0/25
```

> 🔑 Bốn dòng log này là **bốn tấn công khác nhau** đang bị chặn. Tập `grep`
> những chuỗi này trên syslog server là cách giám sát bảo mật L2 hiệu quả nhất.

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces trunk
Port        Mode     Encapsulation  Status        Native vlan
Gi1/0/48    on       802.1q         trunking      999
```

> ⚠️ Nếu thấy một **port người dùng** xuất hiện ở đây → nó đã **vô tình thành trunk**
> *(DTP)* → đó là lỗ hổng VLAN hopping đang mở.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Port người dùng xuất hiện trong `show interfaces trunk` | **DTP tự thương lượng** | `show interfaces trunk` | `switchport mode access` + `nonegotiate` |
| Mạng chậm bất thường, nhiều người kêu | **MAC flooding**, hoặc loop | `show mac address-table count` | Port Security; kiểm tra STP |
| Một số máy nhận IP sai dải | **Rogue DHCP** | `show logging \| include SNOOPING` | DHCP Snooping + trust đúng port |
| Traffic đi vòng khó hiểu | **STP attack** cướp root | `show spanning-tree root` | BPDU Guard + Root Guard |
| Người dùng báo mất mạng sau khi cắm gì đó | BPDU Guard / Port Security kích hoạt | `show interfaces status err-disabled` | Gỡ thiết bị, `shut`/`no shut` |
| Port bật-tắt lặp lại | `errdisable recovery` bật nhưng nguồn chưa xử lý | `show errdisable recovery`, `show logging` | Xử lý gốc trước |
| IP phone không nhận voice VLAN | Đã `no cdp enable` | `show cdp interface` | Bật lại CDP trên port có phone |
| Lệnh `vlan dot1q tag native` gây mất kết nối | Đầu kia chưa bật | `show vlan dot1q tag native` 2 đầu | Bật đồng thời cả hai đầu trunk |

---

## 11. LAB

🧪 **LAB 63 — Tấn công L2 và phòng thủ** → [`../labs/lab63-tan-cong-lop-2.md`](../labs/lab63-tan-cong-lop-2.md)

Yêu cầu tối thiểu:

- Dựng 2 switch + 1 router + 3 PC, 2 VLAN, trunk giữa switch
- **Tấn công 1 — switch spoofing**: để port ở `dynamic auto`, dùng PC giả làm switch
  *(trong Packet Tracer: cắm một switch vào port đó)* → quan sát port thành trunk
  → sửa bằng `switchport mode access` + `nonegotiate`
- **Tấn công 2 — rogue DHCP**: thêm router thứ hai làm DHCP giả → quan sát PC nhận IP sai
  → sửa bằng DHCP Snooping
- **Tấn công 3 — STP attack**: đặt priority 0 trên một switch "lạ" → quan sát root đổi
  → sửa bằng BPDU Guard + Root Guard
- Áp **khối cấu hình chuẩn** ở mục 5, chạy lại cả 3 tấn công → chứng minh đều bị chặn
- **BREAK bắt buộc:** (1) bật `vlan dot1q tag native` chỉ một đầu trunk → mất kết nối;
  (2) `no cdp enable` trên port có IP phone → phone mất voice VLAN;
  (3) `errdisable recovery` bật mà không xử lý nguồn → port bật-tắt lặp lại

## 12. Challenge

1. Giải thích double tagging từng bước. Vì sao nó chỉ hoạt động **một chiều**?
2. Port của bạn để `switchport mode dynamic auto`. Kẻ tấn công làm gì được?
   Viết 2 lệnh phòng thủ.
3. Công ty chỉ có ngân sách/thời gian làm **3 biện pháp**. Chọn 3 cái nào và vì sao?
4. Mọi biện pháp L2 đã bật đầy đủ. Còn lỗ hổng nào không có lệnh nào vá được?

<details>
<summary>Đáp án</summary>

**1.** Từng bước:

```text
1. Kẻ tấn công ở VLAN 1 (= native VLAN của trunk)
2. Tạo frame có HAI tag: [ngoài: VLAN 1][trong: VLAN 20]
3. Switch A (access port VLAN 1) nhận, đẩy ra trunk:
   - VLAN 1 là native → KHÔNG thêm tag khi ra trunk
   - Tag VLAN 20 bên trong vẫn còn
4. Switch B nhận trên trunk, thấy tag VLAN 20 → đưa vào VLAN 20 ✅
```

**Vì sao chỉ một chiều:** gói trả lời từ VLAN 20 là gói **bình thường một tag**.
Khi quay về, switch xử lý nó như gói VLAN 20 thông thường và **không có cơ chế nào**
đưa nó về VLAN 1 của kẻ tấn công.

Hệ quả: dùng được để **gửi lệnh tấn công** hoặc **DoS**, nhưng không đọc được dữ liệu.

**2.** Kẻ tấn công chạy phần mềm giả làm switch, gửi **DTP frame** đề nghị làm trunk.
Switch (ở `dynamic auto`) **đồng ý** → port thành trunk → kẻ tấn công **nhận được
traffic của mọi VLAN** trong `allowed list`.

```cisco
interface Gi1/0/5
 switchport mode access      ! chốt cứng, không thương lượng
 switchport nonegotiate      ! tắt hẳn DTP
```

**3.** Chọn 3 biện pháp có **tỷ lệ hiệu quả/rủi ro tốt nhất**:

| # | Biện pháp | Vì sao chọn |
|:---:|---|---|
| **1** | `switchport mode access` + `nonegotiate` trên mọi access port | Chặn **VLAN hopping**, **rủi ro gián đoạn gần như bằng 0**, chỉ cần gõ lệnh |
| **2** | **BPDU Guard** + PortFast | Chặn **STP attack** và **loop vô tình** — loop là sự cố hay xảy ra nhất trong thực tế |
| **3** | **Port Security** `maximum 2` + `violation restrict` | Chặn **MAC flooding**, và giới hạn người dùng tự ý cắm switch |

Không chọn DAI/IPSG vì chúng **rủi ro gián đoạn cao** và cần chuẩn bị kỹ
*(binding table, khai IP tĩnh)* — không hợp với "chỉ làm 3 cái".

**4.** **Bảo mật vật lý** — và nó không có lệnh nào vá được:

| Lỗ hổng | Vì sao không vá được bằng cấu hình |
|---|---|
| **Tủ mạng không khoá** | Ai cắm vào **uplink** *(trust port)* là bỏ qua mọi biện pháp |
| **Tiếp cận được console** | **Password recovery** chỉ cần truy cập vật lý → chiếm toàn quyền thiết bị |
| **Ổ mạng công cộng không tắt** | Port đang up ở VLAN production = ai cũng vào được |
| **Nhân viên nội bộ có ý đồ xấu** | Họ có credential hợp lệ |

Và một lỗ hổng khác: **thiết bị cũ không hỗ trợ** các tính năng này — switch unmanaged
hay switch đời cũ trong mạng làm vô hiệu mọi thiết kế.

> 🔑 Bài học: **bảo mật là nhiều lớp**. Cấu hình switch là một lớp; khoá tủ, kiểm soát
> ra vào, và quản lý vòng đời thiết bị là những lớp khác — không thay thế nhau được.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 6 tấn công L2 và biện pháp tương ứng · 2 kỹ thuật VLAN hopping | ⬜ |
| **L2** Explain | Giải thích double tagging và vì sao `dot1q tag native` triệt tiêu nó | ⬜ |
| **L3** Configure | Áp khối cấu hình chuẩn lên một switch access | ⬜ |
| **L4** Troubleshoot | Port người dùng thành trunk → tìm nguyên nhân và sửa | ⬜ |
| **L5** Design | Lập kế hoạch triển khai 7 biện pháp theo thứ tự rủi ro | ⬜ |

## 14. Summary

**Bảng tấn công ↔ phòng thủ — thuộc bảng này là xong lesson**

| Tấn công | Phòng thủ |
|---|---|
| MAC flooding | **Port Security** |
| VLAN hopping *(switch spoofing)* | `switchport mode access` + **`nonegotiate`** |
| VLAN hopping *(double tagging)* | **Native VLAN rỗng** + `vlan dot1q tag native` |
| Rogue DHCP | **DHCP Snooping** |
| DHCP starvation | `ip dhcp snooping limit rate` |
| ARP spoofing | **DAI** |
| IP spoofing | **IPSG** |
| STP attack | **BPDU Guard** + **Root Guard** |
| CDP/LLDP recon | `no cdp enable` ở port người dùng |

**Key concepts**

- ⭐ **Bảo mật L2 phải làm ở L2** — firewall ở biên mù với traffic trong cùng VLAN
- Mọi giao thức L2 *(Ethernet, ARP, STP, DHCP, DTP)* **không có xác thực** — thiết kế
  từ thời mạng là môi trường tin cậy
- **Double tagging chỉ một chiều** — không nhận được reply
- ⭐ Thứ tự triển khai theo **rủi ro gián đoạn**: mode access + nonegotiate → BPDU Guard →
  Port Security → tắt port thừa → DHCP Snooping → DAI → IPSG
- ⭐ **Bảo mật vật lý không có lệnh nào thay thế** — tủ mạng phải khoá

**Commands cần nhớ**

| Lệnh | Chống |
|---|---|
| `switchport mode access` + `switchport nonegotiate` | VLAN hopping |
| `vlan dot1q tag native` | Double tagging |
| `switchport port-security maximum 2` | MAC flooding |
| `spanning-tree bpduguard enable` | STP attack, loop |
| `ip dhcp snooping` + `trust` uplink | Rogue DHCP |
| `ip arp inspection vlan N` | ARP spoofing |
| `ip verify source` | IP spoofing |
| `no cdp enable` | Recon |
| `show interfaces status err-disabled` | ⭐ Giám sát |
| `show logging \| include SECURITY\|DAI\|SNOOPING` | ⭐ Nhật ký tấn công |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Để port ở `dynamic auto` | Kẻ tấn công tự thương lượng thành trunk |
| Dùng VLAN 1 làm native | Mở đường cho double tagging |
| Bật `dot1q tag native` một đầu | Mất kết nối trunk |
| `no cdp enable` trên port có IP phone | Phone mất voice VLAN |
| Bật DAI trước khi binding table đầy | Cả VLAN mất mạng |
| `errdisable recovery` mà không xử lý gốc | Port bật-tắt lặp lại |
| Làm hết cấu hình nhưng không khoá tủ mạng | Mọi biện pháp vô dụng |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 63: thực hiện **cả 3 tấn công**, rồi chứng minh khối cấu hình chuẩn chặn hết.
2. Lưu khối cấu hình chuẩn ở mục 5 vào `06-security/config-chuan-access-port.txt`.
3. Kiểm tra switch công ty: `show interfaces trunk` — có port người dùng nào
   vô tình thành trunk không?
4. Lập danh sách: công ty bạn đã bật **bao nhiêu trong 9 biện pháp** ở bảng tổng hợp?

```markdown
- [YYYY-MM-DD] Lesson 38 — L2 attacks & phòng thủ: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 6

Làm **[Mini Exam Phase 6](./review-phase06.md)** trước khi sang
[Phase 7 — WAN/VPN](../07-wan-vpn/README.md).

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 6 tấn công L2, 2 kỹ thuật VLAN hopping, biện pháp tương ứng |
| 🔧 **Engineer** | Khối cấu hình chuẩn; thứ tự triển khai theo rủi ro; giám sát qua log |
| 🏭 **Production** | L2 security không làm được ở tầng khác; bảo mật vật lý là lớp đầu tiên |

### 🔗 Liên kết

- ⬅️ [Lesson 37 — DHCP Snooping, DAI, IPSG](./lesson-37-dhcp-snooping-dai.md)
- 📝 [Mini Exam Phase 6](./review-phase06.md)
- ➡️ [Phase 7 — WAN/VPN](../07-wan-vpn/README.md)
- 📚 Port Security: [Lesson 17](../01-switching/lesson-17-etherchannel-port-security.md)
- 📚 BPDU/Root Guard: [Lesson 16](../01-switching/lesson-16-rstp-portfast-bpduguard.md)
