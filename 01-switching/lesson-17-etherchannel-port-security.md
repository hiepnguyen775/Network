# LESSON 17 — EtherChannel · Port Security

> 📌 Lesson cuối Phase 1. Hai chủ đề độc lập nhưng cùng một tinh thần:
> **làm cho hạ tầng L2 vừa nhanh hơn, vừa an toàn hơn.**

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 13](./lesson-13-vlan-va-trunk.md), [Lesson 15](./lesson-15-stp.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích EtherChannel giải quyết **hai** vấn đề cùng lúc — băng thông và STP
- [ ] Cấu hình EtherChannel bằng LACP, phân biệt với PAgP và static
- [ ] Liệt kê các tham số **phải khớp** giữa hai đầu, và vì sao
- [ ] Hiểu load balancing của EtherChannel **không chia đều từng gói**
- [ ] Cấu hình Port Security và chọn đúng violation mode

## 2. Prerequisite

- Trunk, VLAN, allowed VLAN *(Lesson 13)*
- STP block port để chống loop *(Lesson 15)*
- `err-disabled` và cách khôi phục *(Lesson 16)*

---

# PHẦN A — ETHERCHANNEL

## 3A. Concept

### Vấn đề

Hai switch nối nhau bằng 1 link 1 Gbps. Cần thêm băng thông → cắm thêm dây.

```text
         SW1                      SW1
          ║ 1G                 ║║║║ 4 × 1G
          ║           →        ║║║║
         SW2                      SW2

Kết quả nếu KHÔNG có EtherChannel:
STP thấy 4 đường song song → LOOP → block 3 đường
→ vẫn chỉ dùng được 1 Gbps, 3 sợi dây nằm không.
```

### Giải pháp

**EtherChannel** gộp nhiều link vật lý thành **một link logic** (`Port-channel`).

```text
STP chỉ nhìn thấy MỘT interface → không có loop → KHÔNG block gì
→ dùng được cả 4 Gbps.
```

> ⭐ Đây là điểm quan trọng nhất: EtherChannel giải quyết **hai** vấn đề cùng lúc —
> tăng băng thông **và** làm STP không block link dự phòng.

### Ba giao thức

| | **LACP** | **PAgP** | **Static (ON)** |
|---|---|---|---|
| Chuẩn | **IEEE 802.3ad** — mở | Cisco độc quyền | Không có giao thức |
| Mode | `active` / `passive` | `desirable` / `auto` | `on` |
| Thương lượng | ✅ Có | ✅ Có | ❌ Không |
| Phát hiện cấu hình sai | ✅ | ✅ | ❌ **Nguy hiểm** |
| Dùng khi | ⭐ **Mặc định nên dùng** | Toàn thiết bị Cisco đời cũ | Tránh |

### Bảng tổ hợp mode — phải thuộc

**LACP:**

| SW1 | SW2 | Kết quả |
|---|---|---|
| `active` | `active` | ✅ Lên |
| `active` | `passive` | ✅ Lên |
| `passive` | `passive` | ❌ **Không lên** — không ai chủ động |

**PAgP:**

| SW1 | SW2 | Kết quả |
|---|---|---|
| `desirable` | `desirable` | ✅ Lên |
| `desirable` | `auto` | ✅ Lên |
| `auto` | `auto` | ❌ **Không lên** |

> 💡 Nhớ: **phải có ít nhất một bên chủ động** (`active` / `desirable`).
> Hai bên cùng thụ động thì không ai mở lời.

> ⚠️ **Không trộn LACP với PAgP** ở hai đầu — channel sẽ không bao giờ lên.

### Tham số phải khớp trên MỌI port trong channel

| Tham số | Vì sao |
|---|---|
| **Speed** và **duplex** | Link không đồng nhất thì không gộp được |
| **Chế độ** access hay trunk | Không trộn được |
| **VLAN** (access) hoặc **allowed VLAN + native VLAN** (trunk) | Lệch là channel không lên |
| **Giao thức** LACP/PAgP/on | Phải giống nhau cả 2 đầu |

> ⚠️ Đây là nguyên nhân số 1 của "EtherChannel không bundle". IOS sẽ đưa port không khớp
> vào trạng thái `suspended` hoặc không cho vào channel.

### Load balancing — điểm hay hiểu sai

EtherChannel **không** chia đều từng gói tin. Nó dùng một **thuật toán băm (hash)**
trên các trường của gói để chọn link:

```cisco
SW1(config)# port-channel load-balance src-dst-ip
```

| Thuật toán | Băm theo | Phù hợp khi |
|---|---|---|
| `src-mac` | MAC nguồn | Nhiều client → một server |
| `dst-mac` | MAC đích | Một server → nhiều client |
| `src-dst-ip` | **IP nguồn + đích** | ⭐ Phổ biến nhất, phân bố tốt |
| `src-dst-port` | Cả port L4 | Phân bố tốt nhất *(nếu switch hỗ trợ)* |

> ⚠️ **Hệ quả thực tế rất quan trọng:**
> **Một luồng dữ liệu đơn lẻ luôn đi trên MỘT link vật lý.**
>
> EtherChannel 4 × 1 Gbps **không** cho bạn một kết nối 4 Gbps. Nó cho bạn
> **tổng thông lượng 4 Gbps chia cho nhiều luồng khác nhau**. Copy một file lớn
> giữa hai máy vẫn tối đa 1 Gbps.
>
> Người mới rất hay thất vọng ở chỗ này — và nó là câu hỏi phỏng vấn kinh điển.

---

## 4A. Why?

> **Vì sao không dùng một link 10G thay vì 4 link 1G?**

| | 4 × 1G EtherChannel | 1 × 10G |
|---|---|---|
| Băng thông tổng | 4 Gbps | 10 Gbps |
| Một luồng đơn tối đa | **1 Gbps** | **10 Gbps** |
| Đứt một dây | Mất 25%, **không gián đoạn** | **Mất hết** |
| Chi phí | Dùng port có sẵn | Cần module/switch hỗ trợ 10G |

> 🔧 Hai thứ khác mục đích: **EtherChannel ưu tiên dự phòng**, **link tốc độ cao
> ưu tiên thông lượng một luồng**. Thực tế hay kết hợp: **2 × 10G EtherChannel**.

> 🏭 Giá trị lớn nhất của EtherChannel trong production không phải băng thông —
> mà là **đứt một sợi dây không ai nhận ra**. STP không phải tính lại, không có
> giây gián đoạn nào.

---

## 5A. CLI — EtherChannel

```cisco
! ═══════ LACP — cách nên dùng ═══════
SW1(config)# interface range GigabitEthernet1/0/47 - 48
SW1(config-if-range)# description ETHERCHANNEL-TO-SW2
SW1(config-if-range)# switchport mode trunk
SW1(config-if-range)# switchport trunk allowed vlan 10,20,99
SW1(config-if-range)# channel-group 1 mode active        ! ← LACP active
SW1(config-if-range)# exit

! IOS tự tạo interface Port-channel1 — cấu hình chung đặt ở đây
SW1(config)# interface Port-channel1
SW1(config-if)# description UPLINK-TO-SW2
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20,99

! ═══════ ĐẦU KIA ═══════
SW2(config)# interface range GigabitEthernet1/0/47 - 48
SW2(config-if-range)# switchport mode trunk
SW2(config-if-range)# switchport trunk allowed vlan 10,20,99
SW2(config-if-range)# channel-group 1 mode active

! ═══════ LOAD BALANCING ═══════
SW1(config)# port-channel load-balance src-dst-ip

! ═══════ KIỂM TRA ═══════
SW1# show etherchannel summary
SW1# show etherchannel 1 port-channel
SW1# show interfaces Port-channel1
SW1# show etherchannel load-balance
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `channel-group 1 mode active` | Thêm port vào channel bằng LACP | Số `1` là cục bộ — hai đầu **không cần** trùng |
| `interface Port-channel1` | Cấu hình chung cho cả channel | **Sửa ở đây**, không sửa từng port |
| `port-channel load-balance` | Chọn thuật toán băm | Toàn cục, không theo từng channel |

> ⚠️ **Thứ tự rất quan trọng:** cấu hình trunk/VLAN **trước** rồi mới `channel-group`,
> hoặc cấu hình trên `Port-channel` sau khi tạo. Sửa từng port sau khi đã vào channel
> dễ gây lệch tham số → port bị `suspended`.

> **Khác biệt platform:** NX-OS dùng `interface port-channel 1` và `channel-group 1 mode active`
> tương tự, nhưng cần `feature lacp` trước.

## 6A. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show etherchannel summary
Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator

Number of channel-groups in use: 1
Number of aggregators:           1

Group  Port-channel  Protocol    Ports
------+-------------+-----------+-----------------------------------------
1      Po1(SU)         LACP      Gi1/0/47(P)  Gi1/0/48(P)
```

**Đọc flag — đây là kỹ năng chính của phần này:**

| Flag | Nghĩa | Hành động |
|---|---|---|
| `Po1(SU)` | **S**=Layer2, **U**=in use → ✅ channel đang hoạt động | — |
| `Gi1/0/47(P)` | **P** = đã **bundled** vào channel ✅ | — |
| `(I)` | **stand-alone** — port không vào được channel | Kiểm tra mode LACP hai đầu |
| `(s)` | **suspended** — tham số **không khớp** | So speed/duplex/VLAN/trunk hai đầu |
| `(D)` | **down** | Kiểm tra cáp, `no shutdown` |
| `Po1(SD)` | Channel **down** | Không port nào bundled |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show etherchannel load-balance
EtherChannel Load-Balancing Configuration:
        src-dst-ip
```

---

# PHẦN B — PORT SECURITY

## 3B. Concept

**Port Security** giới hạn **MAC address nào** được phép dùng một port switch.

| Mục đích | Chống gì |
|---|---|
| Giới hạn số MAC trên một port | Ai đó cắm switch mini để chia cổng |
| Khoá MAC cụ thể | Người lạ cắm laptop vào ổ mạng phòng họp |
| Chống **MAC flooding** | Tấn công làm đầy CAM table *(Lesson 11)* |

### Ba cách học MAC

| Cách | Lệnh | Đặc điểm |
|---|---|---|
| **Static** | `switchport port-security mac-address <mac>` | Gõ tay, chính xác nhất, tốn công |
| **Dynamic** | *(mặc định)* | Học tự động, **mất khi reboot** |
| **Sticky** ⭐ | `switchport port-security mac-address sticky` | Học tự động rồi **ghi vào running-config** → `wr` là giữ được |

> 🔧 **Sticky** là lựa chọn thực tế nhất: cắm đúng máy vào, switch học, `wr`,
> từ đó port khoá cứng vào máy đó.

### Ba violation mode

| Mode | Drop traffic | Ghi log/SNMP | Tăng counter | Tắt port |
|---|:---:|:---:|:---:|:---:|
| `protect` | ✅ | ❌ | ❌ | ❌ |
| `restrict` | ✅ | ✅ | ✅ | ❌ |
| **`shutdown`** *(mặc định)* | ✅ | ✅ | ✅ | ✅ **err-disabled** |

> ⚠️ **Mặc định là `shutdown`** — một MAC lạ là port chết, người dùng mất mạng
> cho tới khi có người sửa. Mạnh tay nhưng rất hay gây phiền.
>
> 🔧 Thực tế nhiều nơi dùng **`restrict`**: vẫn chặn, vẫn có log để điều tra,
> nhưng không làm sập cổng của người dùng hợp lệ khi có sự cố nhỏ.

---

## 4B. Why?

> **Nếu không có Port Security thì sao?**

| Rủi ro | Kịch bản |
|---|---|
| Ai cắm cũng có mạng | Khách vào phòng họp, cắm dây, vào thẳng VLAN nội bộ |
| Người dùng tự "mở rộng" mạng | Cắm switch mini để có thêm cổng → mất kiểm soát, dễ gây loop |
| **MAC flooding attack** | Kẻ tấn công bơm hàng nghìn MAC giả → CAM table đầy → switch **flood mọi thứ** như hub → nghe lén được traffic |

> 🔑 Giải thích tấn công MAC flooding: CAM table có giới hạn (vd 8000 entry).
> Bơm đầy nó bằng MAC giả → switch không còn chỗ học MAC thật → với mọi frame nó
> **không biết đích ở đâu** → **flood ra mọi port** → kẻ tấn công nghe được hết.
>
> Port Security giới hạn số MAC mỗi port → tấn công này không thực hiện được.

---

## 5B. CLI — Port Security

```cisco
SW1(config)# interface GigabitEthernet1/0/5
SW1(config-if)# switchport mode access                      ! BẮT BUỘC trước
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport port-security                    ! bật
SW1(config-if)# switchport port-security maximum 2          ! cho phép 2 MAC (PC + IP phone)
SW1(config-if)# switchport port-security mac-address sticky ! học rồi ghi vào config
SW1(config-if)# switchport port-security violation restrict ! chặn + log, không tắt port
SW1(config-if)# switchport port-security aging time 60      ! MAC học được hết hạn sau 60 phút
SW1(config-if)# switchport port-security aging type inactivity

! Khoá cứng một MAC cụ thể
SW1(config-if)# switchport port-security mac-address 001a.2b3c.4d5e

! ═══════ KIỂM TRA ═══════
SW1# show port-security
SW1# show port-security interface GigabitEthernet1/0/5
SW1# show port-security address

! ═══════ KHÔI PHỤC khi err-disabled ═══════
SW1(config-if)# shutdown
SW1(config-if)# no shutdown
! hoặc bật tự động:
SW1(config)# errdisable recovery cause psecure-violation
SW1(config)# errdisable recovery interval 300
```

| Lệnh | Lưu ý |
|---|---|
| `switchport mode access` | ⚠️ **Bắt buộc trước** — Port Security không bật được trên port `dynamic` |
| `maximum 2` | Để **2** nếu có IP phone (phone + PC nối sau phone) |
| `sticky` | Nhớ `wr` sau khi học xong, nếu không reboot là mất |
| `violation restrict` | Thực tế hay dùng hơn `shutdown` |
| `aging type inactivity` | Chỉ hết hạn khi MAC **im lặng**, không phải theo đồng hồ |

## 6B. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show port-security interface GigabitEthernet1/0/5
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Restrict
Aging Time                 : 60 mins
Aging Type                 : Inactivity
Maximum MAC Addresses      : 2
Total MAC Addresses        : 1
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 1
Last Source Address:Vlan   : 001a.2b3c.4d5e:10
Security Violation Count   : 0
```

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `Port Status: Secure-up` | Đang hoạt động bình thường | `Secure-shutdown` = đã err-disabled |
| `Security Violation Count` | Số lần vi phạm | **Tăng dần** → có ai đó đang cắm máy lạ |
| `Last Source Address` | MAC gây vi phạm gần nhất | Tra OUI để biết hãng thiết bị |
| `Sticky MAC Addresses` | Đã học và ghi vào config | Phải `wr` để giữ |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show port-security
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
                (Count)       (Count)     (Count)
---------------------------------------------------------------------------
    Gi1/0/5          2            1               0            Restrict
    Gi1/0/6          1            1               3            Restrict
```

> `Gi1/0/6` có **3 lần vi phạm** — đáng điều tra: ai đang cắm thiết bị lạ vào cổng đó?

---

## 7. Real-world Example

🏭 **Cross-stack EtherChannel — thiết kế đáng tiền nhất ở access layer**

```text
         SW-DIST1       SW-DIST2
            ║ ╲          ╱ ║
            ║  ╲        ╱  ║
            ║   ╲      ╱   ║
         ┌──╨────╨────╨────╨──┐
         │  SW-ACC1 + SW-ACC2  │  ← 2 switch vật lý, 1 STACK
         │   (một thiết bị logic) │
         └─────────────────────┘
```

EtherChannel gồm **1 port từ mỗi switch trong stack**, lên **2 switch distribution khác nhau**.
Kết quả: chết **bất kỳ** một switch nào, uplink vẫn chạy, **không có giây gián đoạn nào**,
STP không phải tính lại.

🏭 **Port Security cho ổ mạng phòng họp / khu vực công cộng**

```cisco
SW1(config)# interface range GigabitEthernet1/0/40 - 44
SW1(config-if-range)# description MEETING-ROOM
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport access vlan 90          ! VLAN GUEST
SW1(config-if-range)# switchport port-security
SW1(config-if-range)# switchport port-security maximum 1
SW1(config-if-range)# switchport port-security violation restrict
SW1(config-if-range)# spanning-tree portfast
SW1(config-if-range)# spanning-tree bpduguard enable
```

Kết hợp ba lớp: **VLAN guest** (không vào được nội bộ) + **Port Security** (một máy một cổng)
+ **BPDU Guard** (không cắm switch được).

🏭 **Bẫy: Port Security và máy ảo**

Server chạy hypervisor có **nhiều MAC** (mỗi VM một MAC) đi qua **một** port vật lý.
Đặt `maximum 1` → VM thứ hai bật lên là port chết.

👉 Với port nối hypervisor: tăng `maximum` cho đủ, hoặc **không dùng Port Security**
và bảo vệ bằng cách khác (802.1X, kiểm soát truy cập vật lý).

---

## 10. Troubleshooting

### EtherChannel

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Channel không lên, port `(I)` stand-alone | Hai đầu đều `passive`/`auto` | `show etherchannel summary` | Đổi một bên sang `active`/`desirable` |
| Port `(s)` suspended | **Tham số không khớp** | So `show run interface` hai đầu | Đồng bộ speed/duplex/mode/VLAN |
| Channel lên nhưng chỉ dùng 1 link | Load balancing băm vào cùng link | `show etherchannel load-balance` | Đổi sang `src-dst-ip` hoặc `src-dst-port` |
| Copy file không nhanh hơn | **Một luồng = một link** — đúng thiết kế | — | Không phải lỗi; cần link tốc độ cao hơn |
| STP vẫn block một link | Channel chưa lên, STP thấy nhiều link riêng lẻ | `show etherchannel summary` | Sửa channel trước |
| Thêm port vào channel làm channel sập | Port mới lệch tham số | `show etherchannel summary` | Cấu hình port giống hệt trước khi thêm |

### Port Security

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Port `err-disabled`, reason `psecure-violation` | MAC lạ vượt `maximum` | `show port-security interface <int>` | Gỡ thiết bị lạ, `shut`/`no shut` |
| Không bật được Port Security | Port đang `dynamic auto` | `show run interface <int>` | `switchport mode access` trước |
| Người dùng đổi máy là mất mạng | Sticky MAC đã khoá máy cũ | `show port-security address` | `clear port-security sticky interface <int>` |
| Reboot xong Port Security mất hết MAC | Sticky chưa `wr` | `show startup-config` | `copy run start` |
| Server ảo hoá mất mạng khi bật VM thứ 2 | `maximum` quá nhỏ | `show port-security interface <int>` | Tăng `maximum` hoặc bỏ Port Security |
| `Violation Count` tăng liên tục | Có người đang cắm thiết bị lạ | `show port-security`, xem `Last Source Address` | Tra OUI, kiểm tra vật lý |

---

## 11. LAB

🧪 **LAB 15 — EtherChannel LACP + Port Security** → [`../labs/lab15-etherchannel-portsec.md`](../labs/lab15-etherchannel-portsec.md)

Yêu cầu tối thiểu:

- 2 switch nối bằng **2 link**, tạo EtherChannel LACP, verify `(SU)` và `(P)`
- Chứng minh STP **không block** link nào sau khi channel lên
- Rút một dây trong channel → chứng minh **không mất gói** *(ping liên tục trong lúc rút)*
- Bật Port Security `maximum 1`, `violation restrict` trên port nối PC
- **BREAK bắt buộc:** (1) đặt native VLAN lệch một đầu channel → quan sát `(s)` suspended;
  (2) hai đầu cùng `passive` → channel không lên; (3) đổi MAC của PC (hoặc cắm PC khác)
  → quan sát violation counter tăng và port bị chặn

## 12. Challenge

1. Bạn tạo EtherChannel 4 × 1 Gbps giữa hai switch, rồi copy một file 10 GB từ server
   sang client. Tốc độ tối đa đạt được là bao nhiêu? Vì sao?
2. SW1 đặt `channel-group 1 mode active`, SW2 đặt `channel-group 2 mode active`.
   Channel có lên không?
3. Port Security `maximum 1`, `violation shutdown`. Người dùng cắm IP phone, rồi cắm PC
   vào cổng của phone. Chuyện gì xảy ra? Sửa thế nào?
4. Vì sao `violation protect` ít được dùng dù nó "nhẹ nhàng" nhất?

<details>
<summary>Đáp án</summary>

**1.** Tối đa **1 Gbps**. EtherChannel băm theo luồng — một cặp `(src, dst)` **luôn đi trên
một link vật lý duy nhất**. 4 Gbps là **tổng thông lượng** khi có **nhiều luồng khác nhau**,
không phải tốc độ của một luồng.

Muốn một luồng nhanh hơn: cần link tốc độ cao hơn (10G), không phải nhiều link 1G.

**2.** **Có, channel vẫn lên.** Số `channel-group` là **cục bộ của từng switch** — nó chỉ
quyết định tên `Port-channel1` hay `Port-channel2` trên thiết bị đó. Hai đầu không cần trùng.

Cái **phải** trùng là: giao thức (LACP), mode tương thích (`active`/`passive`), và các
tham số lớp 2 (speed, duplex, trunk/access, VLAN).

*(Tuy vậy, thực tế nên đặt trùng số cho dễ đọc và dễ troubleshoot.)*

**3.** IP phone có MAC riêng, PC phía sau có MAC riêng → **2 MAC trên một port**.
Vượt `maximum 1` → `violation shutdown` → port vào **err-disabled** → **cả phone lẫn PC
đều mất mạng**.

Sửa:

```cisco
SW1(config-if)# switchport port-security maximum 2        ! phone + PC
! hoặc chính xác hơn, nếu dùng voice VLAN:
SW1(config-if)# switchport port-security maximum 1 vlan access
SW1(config-if)# switchport port-security maximum 1 vlan voice
```

**4.** Vì `protect` **im lặng** — nó drop traffic nhưng **không log, không đếm, không báo ai cả**.

Hậu quả: có người đang cắm thiết bị lạ, traffic bị chặn, nhưng **không ai biết**.
Người dùng báo "máy tôi không vào mạng được" và bạn không có manh mối nào trong log.

`restrict` làm đúng việc đó **cộng thêm log và counter** — cùng mức độ nhẹ nhàng nhưng
để lại dấu vết điều tra. Vì vậy `restrict` gần như luôn là lựa chọn tốt hơn `protect`.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Mode LACP/PAgP · flag `(P)`/`(s)`/`(I)` · 3 violation mode | ⬜ |
| **L2** Explain | Giải thích vì sao một luồng không dùng được hết băng thông channel | ⬜ |
| **L3** Configure | Tạo EtherChannel LACP trunk + Port Security sticky | ⬜ |
| **L4** Troubleshoot | Port `(s)` suspended → nêu 4 tham số cần so sánh | ⬜ |
| **L5** Design | Thiết kế uplink dự phòng cho 1 switch access: dùng gì, vì sao | ⬜ |

## 14. Summary

**EtherChannel**

- Gộp nhiều link vật lý → **một link logic** → STP không block
- **LACP** (chuẩn mở) ⭐ · PAgP (Cisco) · Static `on` (tránh)
- `active`+`active` ✅ · `active`+`passive` ✅ · `passive`+`passive` ❌
- Phải khớp: **speed, duplex, access/trunk, VLAN, native VLAN, giao thức**
- Flag: `(P)` bundled ✅ · `(s)` suspended = lệch tham số · `(I)` stand-alone = mode sai
- ⭐ **Load balancing theo LUỒNG, không theo gói** — một luồng = một link
- Số `channel-group` là cục bộ, hai đầu không cần trùng

**Port Security**

- Giới hạn **MAC nào** được dùng port; chống MAC flooding và cắm thiết bị lạ
- Học MAC: static · dynamic · **sticky** ⭐ *(nhớ `wr`)*
- Violation: `protect` (im lặng) · **`restrict`** (chặn + log) ⭐ · `shutdown` (mặc định, err-disable)
- ⚠️ Phải `switchport mode access` **trước** khi bật
- ⚠️ Port nối hypervisor có nhiều MAC — cẩn thận với `maximum`

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `channel-group 1 mode active` | Tạo EtherChannel LACP |
| `show etherchannel summary` | Đọc flag, chẩn đoán channel |
| `port-channel load-balance src-dst-ip` | Chọn thuật toán băm |
| `switchport port-security` | Bật Port Security |
| `switchport port-security mac-address sticky` | Học rồi ghi vào config |
| `show port-security interface <int>` | Trạng thái, violation count |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Hai đầu cùng `passive`/`auto` | Channel không bao giờ lên |
| Trộn LACP với PAgP | Channel không lên |
| Lệch native VLAN/allowed VLAN | Port `(s)` suspended |
| Mong một luồng đạt tốc độ cả channel | Hiểu sai cơ chế — một luồng = một link |
| Bật Port Security khi port còn `dynamic` | Lệnh bị từ chối |
| Sticky mà quên `wr` | Reboot là mất hết |
| `maximum 1` trên port có IP phone hoặc hypervisor | Port chết khi có MAC thứ hai |
| Dùng `protect` | Chặn nhưng không để lại dấu vết nào |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 15 đầy đủ, kể cả 3 lỗi BREAK.
2. Trong lab EtherChannel: ping liên tục rồi **rút một dây** — đếm số gói mất.
   So sánh với việc rút dây khi **không** có EtherChannel.
3. Bổ sung đoạn Port Security vào "**config chuẩn**" bạn viết ở Lesson 12.

```markdown
- [YYYY-MM-DD] Lesson 17 — EtherChannel & Port Security: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 1

Trước khi sang [Phase 2 — Routing](../02-routing/README.md), làm
**[Mini Exam Phase 1](./review-phase01.md)**. Dưới 80% thì quay lại ôn.

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Bảng mode LACP/PAgP, flag `show etherchannel summary`, 3 violation mode |
| 🔧 **Engineer** | Dùng LACP không dùng static; `src-dst-ip`; sticky + `restrict`; cross-stack EtherChannel |
| 🏭 **Production** | Đứt dây trong channel = không gián đoạn; Port Security hỏng khi gặp hypervisor; `protect` không để lại dấu vết điều tra |

### 🔗 Liên kết

- ⬅️ [Lesson 16 — RSTP & Guards](./lesson-16-rstp-portfast-bpduguard.md)
- 📝 [Mini Exam Phase 1](./review-phase01.md)
- ➡️ [Phase 2 — Routing](../02-routing/README.md)
- 🔜 Sâu hơn: [`CCNP-Encor` Module 02](https://github.com/hiepnguyen775/CCNP-Encor)
