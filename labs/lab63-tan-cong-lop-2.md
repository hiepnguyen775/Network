# LAB 63 — Tấn công L2 và phòng thủ

> ⚠️ **Lab này bạn ĐÓNG VAI attacker để hiểu kẻ tấn công nghĩ gì.**
> Chỉ làm trong lab của mình. Tấn công mạng thật là phạm pháp.

| | |
|---|---|
| **Phase** | 6 |
| **Lesson liên quan** | [Lesson 38 — Tổng hợp tấn công L2](../06-security/lesson-38-l2-attacks.md) |
| **Công cụ** | Cisco Packet Tracer *(+ ghi chú Kali/yersinia cho máy thật)* |
| **Thời lượng** | ~3 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

Với **từng** tấn công: thực hiện → quan sát hậu quả → phòng thủ → xác nhận chặn được.

- [ ] **Tấn công 1:** MAC flooding *(CAM table overflow)* → Port Security
- [ ] **Tấn công 2:** VLAN hopping *(double tagging / DTP)* → tắt DTP + native VLAN
- [ ] **Tấn công 3:** STP manipulation *(giả root bridge)* → BPDU Guard + Root Guard
- [ ] Viết được **checklist hardening switch** của riêng mình

## 2. Prerequisite

- [Lesson 15](../01-switching/lesson-15-stp.md) — STP, root election
- [Lesson 17](../01-switching/lesson-17-etherchannel-port-security.md) — Port Security
- [Lesson 11](../01-switching/lesson-11-kien-truc-switch.md) — CAM table
- [Lesson 38](../06-security/lesson-38-l2-attacks.md) — 3 tấn công này

---

## 3. Topology

```text
                    ┌──────── SW-ROOT ────────┐
                    │  (muốn là root bridge)   │
                    │ Gi0/1            Gi0/2    │
                    └───┬──────────────────┬───┘
                        │                  │
                   ┌────┴─────┐      ┌──────┴────┐
                   │ SW-ACCESS│      │ SW-ATTACK │
                   │ Fa0/1-10 │      │ (giả lập) │
                   └────┬─────┘      └─────┬─────┘
                   PC-USER            ATTACKER-PC
                                     (Fa0/5 SW-ACCESS)
```

| Thiết bị | Vai trò |
|---|---|
| SW-ROOT | Switch lõi, phải là root bridge |
| SW-ACCESS | Switch tầng truy cập, nơi cắm user & attacker |
| ATTACKER-PC | Máy tấn công *(Fa0/5 trên SW-ACCESS)* |
| PC-USER | Nạn nhân *(Fa0/1)* |

## 4. Chuẩn bị nền

```cisco
! ══ SW-ROOT ══
hostname SW-ROOT
spanning-tree vlan 1,10 priority 0        ! ép làm root

! ══ SW-ACCESS ══
hostname SW-ACCESS
vlan 10
 name USER
interface range Fa0/1 - 10
 switchport mode access
 switchport access vlan 10
```

---

## 5. Yêu cầu LAB

- [ ] Mỗi tấn công: ghi lại **bằng chứng thành công** khi chưa phòng thủ
- [ ] Mỗi tấn công: cấu hình phòng thủ và **xác nhận chặn được**
- [ ] Hoàn thành mục **8. BREAK**
- [ ] Viết checklist hardening ở mục Challenge

---

## 6. Step-by-step

### 🔴 Tấn công 1 — MAC Flooding

**Nguyên lý:** CAM table *(bảng MAC)* của switch có giới hạn. Attacker bơm hàng nghìn
MAC giả → bảng đầy → switch chuyển sang **fail-open**: flood mọi frame ra mọi cổng
*(biến switch thành hub)* → attacker nghe được traffic của người khác.

> 🔴 **DỰ ĐOÁN:** khi CAM table đầy, switch sẽ (a) drop frame mới, hay
> (b) flood ra mọi cổng? Chọn trước khi làm.

**Thực hiện** *(Packet Tracer mô phỏng giới hạn; máy thật dùng `macof`)*:

```text
# Trên máy thật (Kali):
macof -i eth0 -n 100000
```

Trong Packet Tracer, mô phỏng bằng cách tạo nhiều PC gửi traffic với MAC khác nhau,
rồi quan sát `show mac address-table count`.

| Quan sát | Ghi lại |
|---|---|
| `show mac address-table count` trước | |
| ... sau khi flood | |
| Traffic PC-USER → gateway có bị flood ra Fa0/5 *(attacker)* không? | |

**Phòng thủ — Port Security:**

```cisco
SW-ACCESS(config)# interface range Fa0/1 - 10
SW-ACCESS(config-if-range)# switchport mode access
SW-ACCESS(config-if-range)# switchport port-security
SW-ACCESS(config-if-range)# switchport port-security maximum 3
SW-ACCESS(config-if-range)# switchport port-security violation restrict
SW-ACCESS(config-if-range)# switchport port-security mac-address sticky
SW-ACCESS(config-if-range)# switchport port-security aging time 60
SW-ACCESS(config-if-range)# switchport port-security aging type inactivity
```

| Kiểm chứng | Mong đợi |
|---|---|
| Flood lại | Cổng chặn sau MAC thứ 4 |
| `show port-security interface Fa0/5` | `SecurityViolation Count` tăng |
| CAM table không bị tràn | ✅ |

> 💡 **`restrict` vs `shutdown` vs `protect`:**
> - `protect` — drop im lặng, **không** đếm, **không** log *(khó phát hiện)*
> - `restrict` — drop + đếm + log *(khuyến nghị cho access port)*
> - `shutdown` — err-disable cổng *(an toàn nhất nhưng user mất mạng, cần can thiệp)*

### 🔴 Tấn công 2 — VLAN Hopping

Hai biến thể:

**2a. Switch Spoofing (DTP):** attacker giả làm switch, thương lượng trunk →
thấy **mọi VLAN**.

```text
# Máy thật: yersinia -> DTP -> enable trunking
```

**2b. Double Tagging:** attacker gắn **2 thẻ 802.1Q**. Switch đầu bóc thẻ ngoài
*(= native VLAN)*, switch thứ hai forward theo thẻ trong → gói nhảy sang VLAN khác.
**Một chiều**, nhưng đủ để tấn công.

> 🔴 **DỰ ĐOÁN:** Double tagging chỉ hoạt động khi native VLAN của trunk **bằng**
> VLAN của attacker. Đúng hay sai? Vì sao?

Kiểm tra lỗ hổng:

```cisco
SW-ACCESS# show interfaces Fa0/5 switchport | include Negotiation|Mode
! Nếu thấy "Negotiation of Trunking: On" → LỖ HỔNG
```

**Phòng thủ:**

```cisco
! Access port — tắt DTP, ép access tĩnh
SW-ACCESS(config)# interface range Fa0/1 - 10
SW-ACCESS(config-if-range)# switchport mode access
SW-ACCESS(config-if-range)# switchport nonegotiate

! Trunk — ép tĩnh, native VLAN KHÔNG dùng, chỉ cho VLAN cần thiết
SW-ACCESS(config)# interface Gi0/1
SW-ACCESS(config-if)# switchport mode trunk
SW-ACCESS(config-if)# switchport nonegotiate
SW-ACCESS(config-if)# switchport trunk native vlan 999
SW-ACCESS(config-if)# switchport trunk allowed vlan 10,20
SW-ACCESS(config)# vlan 999
SW-ACCESS(config-vlan)# name UNUSED-NATIVE

! Cổng chưa dùng — tắt + nhốt vào VLAN chết
SW-ACCESS(config)# interface range Fa0/11 - 24
SW-ACCESS(config-if-range)# switchport mode access
SW-ACCESS(config-if-range)# switchport access vlan 999
SW-ACCESS(config-if-range)# shutdown
```

| Kiểm chứng | Mong đợi |
|---|---|
| `show interfaces Fa0/5 switchport` → Negotiation | `Off` |
| Attacker thử DTP | Không lên trunk được |
| Native VLAN trên trunk | `999` *(không user nào dùng)* |

### 🔴 Tấn công 3 — STP Manipulation (giả root bridge)

**Nguyên lý:** attacker gửi BPDU với **priority rất thấp** → thắng bầu cử root →
traffic toàn mạng định tuyến lại đi qua máy attacker → MitM toàn switch domain.

> 🔴 **DỰ ĐOÁN:** priority mặc định là 32768. Attacker gửi priority 0.
> Ai thành root? Traffic giữa SW-ROOT và SW-ACCESS giờ đi đường nào?

```text
# Máy thật: yersinia -> STP -> Claiming Root Role
```

Quan sát trước phòng thủ:

```cisco
SW-ACCESS# show spanning-tree vlan 10
! Root ID đổi sang MAC của attacker → topology bị bẻ cong
```

**Phòng thủ:**

```cisco
! BPDU Guard — mọi access port: nhận BPDU = err-disable NGAY
SW-ACCESS(config)# interface range Fa0/1 - 10
SW-ACCESS(config-if-range)# spanning-tree portfast
SW-ACCESS(config-if-range)# spanning-tree bpduguard enable

! Bật toàn cục cho mọi PortFast port
SW-ACCESS(config)# spanning-tree portfast default
SW-ACCESS(config)# spanning-tree portfast bpduguard default

! Root Guard — trên cổng hướng XUỐNG switch khác: cấm chúng thành root
SW-ROOT(config)# interface range Gi0/1 - 2
SW-ROOT(config-if-range)# spanning-tree guard root
```

| Kiểm chứng | Mong đợi |
|---|---|
| Attacker gửi BPDU trên Fa0/5 | Cổng `err-disabled` ngay |
| `show spanning-tree vlan 10` | Root vẫn là **SW-ROOT** |
| `show interfaces status err-disabled` | Fa0/5 xuất hiện |
| Log | `%SPANTREE-2-BLOCK_BPDUGUARD` |

**Khôi phục cổng err-disable:**

```cisco
SW-ACCESS(config)# errdisable recovery cause bpduguard
SW-ACCESS(config)# errdisable recovery interval 300
! hoặc thủ công: shutdown / no shutdown trên cổng
```

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW-ACCESS# show port-security interface Fa0/5
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Restrict
Maximum MAC Addresses      : 3
Total MAC Addresses        : 3
Sticky MAC Addresses       : 3
Last Source Address:Vlan   : 00AA.BBCC.1234:10
Security Violation Count   : 847
```

```text
# output điển hình — tự verify trên lab của bạn
SW-ACCESS# show interfaces Fa0/5 switchport
Name: Fa0/5
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Negotiation of Trunking: Off
Access Mode VLAN: 10 (USER)
```

```text
# output điển hình — tự verify trên lab của bạn
SW-ACCESS# show spanning-tree vlan 10
VLAN0010
  Root ID    Priority    0
             Address     00D0.ROOT.0001        ← vẫn là SW-ROOT, không phải attacker
             This bridge is the root? no
```

```text
# output điển hình — sau khi BPDU Guard bắt được tấn công
SW-ACCESS# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Fa0/5                        err-disabled bpduguard

%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port Fa0/5 with BPDU Guard enabled.
Disabling port.
%PM-4-ERR_DISABLE: bpduguard error detected on Fa0/5, putting Fa0/5 in err-disable state
```

**Bảng kiểm chứng tổng hợp:**

| # | Tấn công | Phòng thủ | Bằng chứng chặn được |
|:---:|---|---|---|
| 1 | MAC flood | Port Security | `Security Violation Count` tăng, CAM không tràn |
| 2a | DTP spoof | `switchport nonegotiate` | `Negotiation: Off`, không lên trunk |
| 2b | Double tag | native VLAN 999 | Gói không nhảy VLAN |
| 3 | Giả root | BPDU Guard | Fa0/5 `err-disabled`, root không đổi |
| 3 | Giả root *(uplink)* | Root Guard | Cổng `root-inconsistent` |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — BPDU Guard trên cổng uplink ⭐

```cisco
! Bật nhầm BPDU Guard trên cổng NỐI SWITCH
SW-ACCESS(config)# interface Gi0/1
SW-ACCESS(config-if)# spanning-tree bpduguard enable
```

| | |
|---|---|
| Cổng Gi0/1 vào trạng thái gì? *(gợi ý: SW-ROOT gửi BPDU hợp lệ qua đây)* | |
| Toàn mạng còn thông không? | |
| Vì sao BPDU Guard **chỉ** nên bật trên access port? | |
| Trên uplink nên dùng gì thay thế? | |

### Lỗi 2 — Port Security `maximum 1` cho cổng có IP phone

```cisco
SW-ACCESS(config)# interface Fa0/1
SW-ACCESS(config-if)# switchport port-security maximum 1
! Fa0/1 có: IP Phone + PC cắm sau phone (2 MAC)
```

| | |
|---|---|
| Cổng vào trạng thái gì khi PC sau phone gửi traffic? | |
| Vì sao 1 là quá ít cho cổng có điện thoại? | |
| Giá trị `maximum` hợp lý là bao nhiêu? Vì sao? | |

### Lỗi 3 — Native VLAN mismatch

```cisco
! SW-ROOT giữ native VLAN 1, SW-ACCESS đổi sang 999
SW-ROOT(config)# interface Gi0/1
SW-ROOT(config-if)# switchport trunk native vlan 1
```

| | |
|---|---|
| Có log gì xuất hiện trên cả hai switch? | |
| VLAN 1 và VLAN 999 traffic có bị trộn không? | |
| Rủi ro bảo mật của native VLAN mismatch là gì? | |

### Lỗi 4 — err-disable không tự hồi

```cisco
! Attacker đã bị BPDU Guard chặn, Fa0/5 err-disabled
! Attacker rút máy, cắm PC thật vào — vẫn không có mạng
```

| | |
|---|---|
| Vì sao PC thật vẫn không vào được dù attacker đã đi? | |
| Hai cách đưa cổng trở lại hoạt động là gì? | |
| Cấu hình nào giúp tự hồi sau 5 phút? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. **Viết checklist hardening switch** hoàn chỉnh cho một access switch
   *(gom mọi thứ lab này + Port Security + DHCP Snooping/DAI từ LAB 62)*.
2. Root Guard và BPDU Guard khác nhau thế nào? Mỗi cái đặt ở cổng nào?
3. Công ty bị "mạng lúc nhanh lúc chậm, có lúc thấy traffic lạ".
   Nghi MAC flooding. Dùng lệnh nào để xác nhận? Dấu hiệu gì khẳng định?
4. Vì sao đặt native VLAN = một VLAN **không ai dùng** lại chống được double tagging?

<details>
<summary>Đáp án</summary>

**1. Checklist hardening access switch:**

```cisco
! ═══ CỔNG ACCESS (user) ═══
interface range Fa0/1 - 24
 switchport mode access
 switchport access vlan 10
 switchport nonegotiate                       ! chống VLAN hopping (DTP)
 switchport port-security                     ! chống MAC flood + starvation
 switchport port-security maximum 3
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 spanning-tree portfast                       ! lên forwarding nhanh
 spanning-tree bpduguard enable               ! chống giả root
 ip verify source                             ! IPSG (cần DHCP Snooping)

! ═══ CỔNG TRUNK (uplink) ═══
interface Gi0/1
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999             ! native = VLAN chết
 switchport trunk allowed vlan 10,20,30       ! chỉ VLAN cần thiết
 spanning-tree guard root                     ! uplink không được thành root
 ip dhcp snooping trust
 ip arp inspection trust

! ═══ TOÀN CỤC ═══
spanning-tree portfast bpduguard default
ip dhcp snooping
ip dhcp snooping vlan 10,20,30
ip arp inspection vlan 10,20,30
errdisable recovery cause bpduguard
errdisable recovery cause psecure-violation
errdisable recovery interval 300
vlan 999
 name UNUSED-NATIVE

! ═══ CỔNG CHƯA DÙNG ═══
interface range Fa0/25 - 48
 switchport mode access
 switchport access vlan 999
 shutdown
```

**2.**

| | **BPDU Guard** | **Root Guard** |
|---|---|---|
| Đặt ở | **Access port** *(xuống PC)* | **Uplink/downlink port** *(xuống switch khác)* |
| Kích hoạt khi | Nhận **bất kỳ** BPDU nào | Nhận BPDU **tốt hơn** root hiện tại |
| Hành động | `err-disabled` cổng | `root-inconsistent` *(block, nhưng tự hồi khi hết BPDU xấu)* |
| Dùng khi | Cổng user **không bao giờ** nên có switch | Cổng nối switch nhưng **không được phép** thành root |

Nguyên tắc: *BPDU Guard bảo vệ nơi không nên có BPDU; Root Guard bảo vệ nơi có BPDU
nhưng không được là root.*

**3.** Xác nhận MAC flooding:

```cisco
show mac address-table count
```

| Dấu hiệu khẳng định | |
|---|---|
| Số MAC gần sát **giới hạn phần cứng** *(vd 8000/8192)* | CAM sắp/đã tràn |
| `show mac address-table` có **hàng nghìn MAC ngẫu nhiên** trên **một cổng** | Dấu hiệu `macof` |
| Nhiều MAC cùng trỏ về **một cổng access** | Bất thường — access port chỉ nên có 1-2 MAC |
| Wireshark thấy traffic của **máy khác** đến cổng mình | Switch đang fail-open *(flood)* |

Khẳng định chắc chắn: **nhiều nghìn MAC lạ dồn về một cổng**. PC bình thường không
tạo quá vài MAC.

**4.** Double tagging hoạt động như sau:

```text
Attacker gửi frame:  [Thẻ ngoài VLAN 1][Thẻ trong VLAN 20][data]
SW1 nhận trên access port VLAN 1 (= native):
  → bóc thẻ ngoài (vì khớp native, native KHÔNG được gắn thẻ khi qua trunk)
  → forward qua trunk, chỉ còn [Thẻ trong VLAN 20]
SW2 nhận: thấy thẻ VLAN 20 → gửi vào VLAN 20
  → GÓI ĐÃ NHẢY từ VLAN 1 sang VLAN 20
```

Mấu chốt: tấn công chỉ chạy khi **VLAN của attacker = native VLAN của trunk**,
vì chỉ native VLAN mới bị **bóc thẻ** khi đi qua trunk.

Đặt native VLAN = **999 (không ai dùng)**:

```text
Attacker ở VLAN 10 (access), native trunk = 999
→ Thẻ ngoài của attacker (VLAN 10) KHÔNG khớp native (999)
→ SW1 KHÔNG bóc thẻ ngoài khi qua trunk → giữ nguyên 2 thẻ
→ hoặc frame bị xử lý sai → tấn công thất bại
```

Vì **không máy người dùng nào ở VLAN 999**, không ai có thể đặt thẻ ngoài khớp native
→ double tagging bị vô hiệu hoá.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các tấn công

**Tấn công 1 — vì sao flooding ăn được:** CAM table hữu hạn *(vài nghìn entry)*.
Khi đầy, switch **không drop** mà **fail-open** = flood unknown-unicast ra mọi cổng
cùng VLAN. Lúc đó switch hoạt động như hub → attacker sniff được mọi thứ.
Port Security chặn tận gốc: giới hạn số MAC học được **trên mỗi cổng** nên attacker
không bơm được nghìn MAC từ một cổng.

**Tấn công 2 — vì sao hopping ăn được:**
- *DTP:* mặc định cổng ở `dynamic auto/desirable` → attacker giả switch, thương lượng
  thành trunk → thấy mọi VLAN. `switchport nonegotiate` + `mode access` giết DTP.
- *Double tag:* lợi dụng native VLAN bị bóc thẻ. Đặt native = VLAN chết → hết đường.

**Tấn công 3 — vì sao giả root ăn được:** STP tin **mọi BPDU**. Priority thấp nhất
thắng. Attacker gửi priority 0 → thành root → bẻ cong đường đi → MitM.
BPDU Guard: access port **không bao giờ** nên nhận BPDU → nhận là shut ngay.

### Giải thích các lỗi BREAK

**Lỗi 1 — BPDU Guard trên uplink ⭐:**

| Quan sát | Giải thích |
|---|---|
| Gi0/1 `err-disabled` ngay | SW-ROOT gửi BPDU **hợp lệ** qua uplink; BPDU Guard không phân biệt bạn/thù — thấy BPDU là shut |
| Mạng mất đường lên lõi | Uplink chết |

**Vì sao chỉ dùng ở access:** access port *(xuống PC)* không bao giờ nên thấy BPDU.
Uplink *(xuống switch)* **phải** trao đổi BPDU để STP chạy. Trên uplink dùng
**Root Guard** — cho phép BPDU nhưng cấm đầu kia thành root.

**Lỗi 2 — maximum 1 với IP phone:**

Cổng có điện thoại IP mang **2 MAC**: của phone *(voice VLAN)* và của PC cắm sau phone
*(data VLAN)*. `maximum 1` → MAC thứ hai = vi phạm → cổng chặn/err-disable.
Giá trị hợp lý: **`maximum 3`** *(phone + PC + chút dư)*. Cisco khuyến nghị 2-3 cho
cổng có điện thoại.

**Lỗi 3 — native VLAN mismatch:**

```text
# output điển hình — tự verify trên lab của bạn
%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on
GigabitEthernet0/1 (1), with SW-ACCESS GigabitEthernet0/1 (999).
```

Một đầu coi frame không-thẻ là VLAN 1, đầu kia coi là VLAN 999 → traffic **rò rỉ**
giữa hai VLAN. Đây vừa là lỗi vận hành vừa là **lỗ hổng bảo mật** *(VLAN leak)*.
Hai đầu trunk **phải** cùng native VLAN.

**Lỗi 4 — err-disable không tự hồi:**

Cổng ở `err-disabled` **không tự bật lại** dù nguyên nhân đã hết — đây là chủ ý
*(bắt admin kiểm tra)*. PC thật cắm vào vẫn chết.

Hai cách:
```cisco
! Thủ công
interface Fa0/5
 shutdown
 no shutdown

! Tự động sau 5 phút
errdisable recovery cause bpduguard
errdisable recovery interval 300
```

### Bảng tổng kết — tấn công ↔ phòng thủ

| Tấn công | Khai thác lỗ hổng | Phòng thủ chính | Verify |
|---|---|---|---|
| MAC flooding | CAM table hữu hạn, fail-open | Port Security | `show port-security` |
| Switch spoofing | DTP auto-negotiate | `switchport nonegotiate` + `mode access` | `show interfaces switchport` |
| Double tagging | native VLAN bị bóc thẻ | native = VLAN chết | `show interfaces trunk` |
| STP root giả | STP tin mọi BPDU | BPDU Guard *(access)* + Root Guard *(uplink)* | `show spanning-tree` |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Tấn công nào làm tôi "ồ hoá ra dễ vậy"? ___
- Checklist hardening của riêng tôi *(link / dán vào đây)*: ___
- Lỗi 1 (BPDU Guard sai chỗ) — tôi nhớ quy tắc access vs uplink chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
