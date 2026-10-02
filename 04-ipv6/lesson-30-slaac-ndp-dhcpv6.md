# LESSON 30 — SLAAC · NDP · ICMPv6 · DHCPv6 ⭐

| | |
|---|---|
| **Phase** | 4 — IPv6 |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 29](./lesson-29-ipv6-dia-chi.md), [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Mô tả **5 loại gói NDP** và mỗi loại thay thế gì của IPv4
- [ ] Giải thích SLAAC từng bước — host tự có địa chỉ **không cần server nào**
- [ ] Phân biệt SLAAC · DHCPv6 stateless · DHCPv6 stateful qua **2 cờ M và O**
- [ ] Giải thích **DAD** và vì sao IPv6 phát hiện trùng địa chỉ tốt hơn IPv4
- [ ] Nói được chính xác **chặn ICMPv6 thì hỏng gì**

## 2. Prerequisite

- Link-local, solicited-node multicast, `ff02::1`/`ff02::2` *(Lesson 29)*
- ARP hoạt động thế nào *(Lesson 05)*

---

## 3. Concept

### NDP — 5 loại gói, đều là ICMPv6

| ICMPv6 Type | Tên | Viết tắt | Thay thế gì của IPv4 |
|:---:|---|---|---|
| **133** | Router Solicitation | **RS** | — *(mới)* |
| **134** | Router Advertisement | **RA** | — *(mới)* |
| **135** | Neighbor Solicitation | **NS** | **ARP Request** |
| **136** | Neighbor Advertisement | **NA** | **ARP Reply** |
| **137** | Redirect | — | ICMP Redirect |

> ⭐ **Toàn bộ NDP chạy trên ICMPv6.** Đây là lý do chặn ICMPv6 giết chết mạng IPv6 —
> khác hẳn IPv4 nơi ICMP chỉ là tiện ích chẩn đoán.

### Bốn chức năng của NDP

| Chức năng | Gói dùng | IPv4 làm bằng gì |
|---|---|---|
| **Phân giải địa chỉ** (IPv6 → MAC) | NS / NA | ARP |
| **Tìm router** | RS / RA | Gán tay / DHCP option 3 |
| **Tự cấu hình địa chỉ** (SLAAC) | RA | DHCP |
| **Phát hiện trùng địa chỉ** (DAD) | NS | Gratuitous ARP |
| *(bonus)* Phát hiện láng giềng chết (NUD) | NS / NA | *(không có)* |

### SLAAC — từng bước

```text
1. Interface bật IPv6
   → TỰ SINH link-local: fe80:: + Interface ID
2. DAD: gửi NS hỏi chính địa chỉ link-local của mình
   → không ai trả lời → địa chỉ an toàn
3. Gửi RS tới ff02::2 ("all routers")  — "có router nào không?"
4. Router trả RA (hoặc tự phát RA mỗi ~200 giây):
   "prefix ở đây là 2001:db8:1234:10::/64, tôi là default gateway"
5. Host ghép:  prefix (64 bit)  +  Interface ID (64 bit)  =  GUA đầy đủ
6. DAD lần nữa cho địa chỉ GUA vừa tạo
7. Default gateway = địa chỉ LINK-LOCAL của router gửi RA
```

> 🔑 Bước 7 rất quan trọng: **default gateway IPv6 là địa chỉ link-local của router**,
> không phải GUA. Đây là chỗ người quen IPv4 hay bất ngờ.

> ⭐ **Host có địa chỉ mà không cần server nào cả** — chỉ cần một router phát RA.
> Đây là khác biệt lớn nhất so với IPv4.

### Hai cờ trong RA — quyết định tất cả

| Cờ | Tên | Nghĩa khi bật |
|:---:|---|---|
| **M** | Managed Address Configuration | "Lấy **địa chỉ** từ DHCPv6" |
| **O** | Other Configuration | "Lấy **thông tin khác** (DNS…) từ DHCPv6" |

### Ba chế độ — bảng phải thuộc

| Chế độ | M | O | Địa chỉ từ đâu | DNS từ đâu | Cần DHCPv6 server? |
|---|:---:|:---:|---|---|:---:|
| **SLAAC thuần** | 0 | 0 | **SLAAC** | RA *(option RDNSS)* | ❌ **Không** |
| **SLAAC + DHCPv6 stateless** | 0 | **1** | **SLAAC** | **DHCPv6** | ✅ Có |
| **DHCPv6 stateful** | **1** | 1 | **DHCPv6** | DHCPv6 | ✅ Có |

> 🔑 Cách nhớ: **M = aMa chỉ** *(Managed = địa chỉ do DHCP quản lý)*,
> **O = thông tin Other**.

> 🏭 Thực tế: **SLAAC thuần** đơn giản nhất và đủ cho hầu hết mạng.
> Doanh nghiệp cần kiểm soát/truy vết thì dùng **DHCPv6 stateful**.

### DAD — Duplicate Address Detection

```text
1. Host vừa tạo một địa chỉ (link-local hoặc GUA)
2. Đánh dấu địa chỉ đó là "tentative" — CHƯA dùng được
3. Gửi NS tới solicited-node multicast của CHÍNH địa chỉ đó
   Src = :: (unspecified — vì chưa có địa chỉ hợp lệ)
4. Chờ ~1 giây:
   ├─ Không ai trả lời  → địa chỉ DUY NHẤT → chuyển sang "preferred" ✅
   └─ Có NA trả về      → TRÙNG → không dùng được, báo lỗi
```

> 💡 So với IPv4: gratuitous ARP cũng phát hiện trùng, nhưng **sau khi đã gán IP**.
> DAD làm **trước khi dùng** — an toàn hơn.

### Vòng đời một địa chỉ SLAAC

```text
Tentative  →  Preferred  →  Deprecated  →  Invalid
   (DAD)      (dùng bình     (còn dùng      (bỏ)
               thường)        cho kết nối
                              cũ, không mở
                              kết nối mới)
```

RA mang hai thời gian: **Valid Lifetime** và **Preferred Lifetime**.
Khi đổi prefix, router giảm lifetime của prefix cũ → host chuyển dần sang prefix mới
mà **không đứt kết nối đang mở**.

---

## 4. Why?

> **Vì sao IPv6 cần SLAAC khi đã có DHCP?**

| Vấn đề của DHCP | SLAAC giải quyết |
|---|---|
| Cần **server** — một thiết bị nữa phải cài, bảo trì, HA | Chỉ cần **router** đã có sẵn |
| Server chết = không ai có IP | Router chết thì mạng cũng chết rồi |
| Thiết bị IoT nhỏ phải cài DHCP client | SLAAC đơn giản hơn nhiều |
| Mạng tạm (lab, sự cố) phải dựng server | Cắm router là chạy |

> **Vậy khi nào vẫn cần DHCPv6?**

| Nhu cầu | Vì sao SLAAC không đủ |
|---|---|
| **Truy vết** — biết máy nào dùng IP nào | SLAAC không có bản ghi tập trung |
| **Reservation** — gán IP cố định theo thiết bị | SLAAC không gán được |
| Cấp **nhiều option** (NTP, TFTP, domain search) | RA chỉ cấp được prefix + DNS *(RDNSS)* |
| Chính sách bảo mật yêu cầu kiểm soát địa chỉ | — |

---

## 5. How does it work? — NS/NA thay ARP

```text
R1 (2001:db8:10::1) muốn gửi tới PC (2001:db8:10::1a2b:3c4d)

1. Tra NDP cache — có MAC chưa?
   ├─ CÓ   → dùng luôn
   └─ KHÔNG ↓
2. Tính solicited-node multicast của đích:
      2001:db8:10::1a2b:3c4d  →  24 bit cuối = 2b:3c4d
      →  ff02::1:ff2b:3c4d
3. Gửi NS tới ff02::1:ff2b:3c4d
      (chỉ máy có 24 bit cuối khớp mới xử lý — khác ARP broadcast!)
4. PC nhận, thấy hỏi mình → trả NA UNICAST về R1, kèm MAC của mình
5. R1 lưu vào NDP cache → gửi dữ liệu
```

> 🔑 So với ARP *(Lesson 05)*: ARP broadcast **làm phiền cả 250 máy** trong VLAN;
> NS multicast thường chỉ làm phiền **1 máy**, và card mạng lọc **ở phần cứng**.

---

## 6. Packet Flow — RA chứa gì

```text
# dạng điển hình — bắt bằng Wireshark filter: icmpv6.type == 134
Internet Control Message Protocol v6
    Type: Router Advertisement (134)
    Cur hop limit: 64
    Flags: 0x00
        0... .... = Managed address configuration: Not set   ← cờ M
        .0.. .... = Other configuration: Not set              ← cờ O
    Router lifetime (s): 1800
    ICMPv6 Option (Prefix information : 2001:db8:1234:10::/64)
        Prefix Length: 64
        Flag: 0xc0  (On-link, Autonomous)
        Valid Lifetime: 2592000
        Preferred Lifetime: 604800
    ICMPv6 Option (Source link-layer address : 00:1a:2b:3c:4d:5e)
    ICMPv6 Option (Recursive DNS Server : 2001:db8::53)       ← RDNSS
```

| Trường | Ý nghĩa |
|---|---|
| **Flags M / O** | Quyết định dùng SLAAC hay DHCPv6 |
| `Router lifetime` | **0 = router này KHÔNG phải default gateway** |
| `Prefix information` | Prefix để host ghép địa chỉ |
| Flag `Autonomous` | Cho phép dùng prefix này cho SLAAC |
| `RDNSS` | DNS server — cho phép SLAAC thuần không cần DHCPv6 |

> 💡 **RDNSS** (RFC 8106) là thứ làm SLAAC thuần trở nên khả thi. Trước khi có nó,
> RA không cấp được DNS nên bắt buộc phải có DHCPv6 stateless.
> Windows hỗ trợ RDNSS từ Windows 10.

---

## 7. Real-world Example

🏭 **Rogue RA — mối nguy lớn nhất của IPv6**

Trong IPv4, rogue DHCP server cần cố ý cài đặt. Trong IPv6, **bất kỳ máy nào phát RA
cũng trở thành gateway** của cả link — không cần cấu hình gì.

```text
Một máy Windows bật "Internet Connection Sharing"
   → tự phát RA
   → mọi máy trong VLAN lấy nó làm default gateway
   → traffic đi qua máy đó → mất mạng hoặc bị nghe lén
```

**Phòng chống — RA Guard trên switch:**

```cisco
SW1(config)# ipv6 nd raguard policy HOST-PORT
SW1(config-nd-raguard)# device-role host
SW1(config)# interface range Gi1/0/1 - 44
SW1(config-if-range)# ipv6 nd raguard attach-policy HOST-PORT
```

> 🔧 RA Guard với IPv6 quan trọng y như DHCP Snooping với IPv4 —
> và **nguy hiểm hơn** vì rogue RA dễ xảy ra **vô tình**.

🏭 **Chặn ICMPv6 — lỗi kinh điển của người quen IPv4**

```cisco
! ❌ SAI — sẽ giết chết mạng IPv6
ipv6 access-list CHAN-ICMP
 deny icmp any any
 permit ipv6 any any
```

Hậu quả:

| Hỏng | Vì sao |
|---|---|
| **NDP** (NS/NA) | Không phân giải được IPv6 → MAC → **không ping được ai** |
| **SLAAC** (RS/RA) | Host không nhận prefix → không có địa chỉ, không có gateway |
| **DAD** | Không phát hiện được trùng địa chỉ |
| **PMTUD** | Không nhận "Packet Too Big" → gói lớn bị drop **im lặng**, web treo |

```cisco
! ✅ ĐÚNG — permit các ICMPv6 thiết yếu trước
ipv6 access-list AN-TOAN
 permit icmp any any nd-ns         ! Neighbor Solicitation
 permit icmp any any nd-na         ! Neighbor Advertisement
 permit icmp any any router-solicitation
 permit icmp any any router-advertisement
 permit icmp any any packet-too-big
 permit icmp any any echo-reply
 deny   ipv6 any any log
```

🏭 **PMTUD và vì sao nó quan trọng hơn ở IPv6**

IPv4: router có thể **phân mảnh** gói quá lớn. IPv6: router **không fragment** —
nó gửi về `ICMPv6 Packet Too Big` (Type 2) và **host nguồn** phải tự thu nhỏ gói.

Chặn `packet-too-big` → host không biết phải thu nhỏ → gói lớn bị drop im lặng.
Triệu chứng: **ping được, web nhỏ load được, web có ảnh lớn thì treo**.

> 🔧 Đây là lý do `permit icmp any any packet-too-big` phải có trong **mọi** ACL IPv6.

---

## 8. Cisco CLI

```cisco
! ═══════ SLAAC — mặc định, chỉ cần bật routing ═══════
R1(config)# ipv6 unicast-routing
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ipv6 address 2001:db8:1234:10::1/64
R1(config-if)# ipv6 address fe80::1 link-local
! Router tự phát RA → host tự SLAAC

! Cấp DNS qua RA (RDNSS) — cho SLAAC thuần
R1(config-if)# ipv6 nd ra dns server 2001:db8::53

! ═══════ ĐIỀU KHIỂN RA ═══════
R1(config-if)# ipv6 nd ra interval 100          ! chu kỳ gửi RA (giây)
R1(config-if)# ipv6 nd ra lifetime 1800         ! 0 = KHÔNG làm default gateway
R1(config-if)# ipv6 nd prefix 2001:db8:1234:10::/64 2592000 604800
R1(config-if)# no ipv6 nd ra suppress           ! đảm bảo có gửi RA
R1(config-if)# ipv6 nd ra suppress              ! TẮT RA trên interface này

! ═══════ DHCPv6 STATELESS (M=0, O=1) ═══════
R1(config)# ipv6 dhcp pool STATELESS-POOL
R1(config-dhcpv6)# dns-server 2001:db8::53
R1(config-dhcpv6)# domain-name cty.local
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ipv6 dhcp server STATELESS-POOL
R1(config-if)# ipv6 nd other-config-flag        ! bật cờ O

! ═══════ DHCPv6 STATEFUL (M=1, O=1) ═══════
R1(config)# ipv6 dhcp pool STATEFUL-POOL
R1(config-dhcpv6)# address prefix 2001:db8:1234:10::/64 lifetime 172800 86400
R1(config-dhcpv6)# dns-server 2001:db8::53
R1(config-dhcpv6)# domain-name cty.local
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ipv6 dhcp server STATEFUL-POOL
R1(config-if)# ipv6 nd managed-config-flag      ! bật cờ M
R1(config-if)# ipv6 nd other-config-flag        ! bật cờ O

! ═══════ DHCPv6 RELAY ═══════
R1(config-if)# ipv6 dhcp relay destination 2001:db8:50::10

! ═══════ RA GUARD (trên switch) ═══════
SW1(config)# ipv6 nd raguard policy HOST-PORT
SW1(config-nd-raguard)# device-role host
SW1(config-if)# ipv6 nd raguard attach-policy HOST-PORT

! ═══════ KIỂM TRA ═══════
R1# show ipv6 interface GigabitEthernet0/0
R1# show ipv6 neighbors
R1# show ipv6 dhcp pool
R1# show ipv6 dhcp binding
R1# debug ipv6 nd
R1# undebug all
```

| Lệnh | Lưu ý |
|---|---|
| `ipv6 unicast-routing` | ⚠️ **Thiếu → router KHÔNG gửi RA** → host không SLAAC được |
| `ipv6 nd managed-config-flag` | Bật cờ **M** → dùng DHCPv6 stateful |
| `ipv6 nd other-config-flag` | Bật cờ **O** → lấy DNS từ DHCPv6 |
| `ipv6 nd ra lifetime 0` | Router **không** làm default gateway *(vẫn cấp prefix)* |
| `ipv6 nd ra suppress` | Tắt RA — dùng trên interface không có host |
| `ipv6 nd raguard` | ⭐ Chống rogue RA |

> **Khác biệt platform:** NX-OS cần `feature dhcp`; cú pháp RA tương tự nhưng
> một số lệnh nằm trong `ipv6 nd` khác đôi chút.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  IPv6 is enabled, link-local address is FE80::1
  Global unicast address(es):
    2001:DB8:1234:10::1, subnet is 2001:DB8:1234:10::/64
  Joined group address(es):
    FF02::1
    FF02::2
    FF02::1:FF00:1
  MTU is 1500 bytes
  ND DAD is enabled, number of DAD attempts: 1
  ND reachable time is 30000 milliseconds
  ND advertised reachable time is 0 milliseconds
  ND advertised retransmit interval is 0 milliseconds
  ND router advertisements are sent every 200 seconds
  ND router advertisements live for 1800 seconds
  Hosts use stateless autoconfig for addresses.
```

**Đọc gì:**

| Dòng | Ý nghĩa | Bất thường |
|---|---|---|
| `Joined group FF02::2` | Thiết bị này là **router** | Thiếu → `ipv6 unicast-routing` chưa bật |
| `ND DAD is enabled` | DAD đang chạy ✅ | |
| `router advertisements are sent every 200 seconds` | Đang gửi RA ✅ | Không có dòng này → RA bị suppress |
| **`Hosts use stateless autoconfig`** | **M=0, O=0** → SLAAC thuần | |
| `Hosts use DHCP to obtain other config` | **O=1** → stateless DHCPv6 |
| `Hosts use DHCP to obtain routable addresses` | **M=1** → stateful DHCPv6 |

> 🔑 Dòng cuối cùng cho biết ngay chế độ đang chạy — không cần đọc cờ thủ công.

```text
# output điển hình — tự verify trên máy bạn
C:\> ipconfig /all
   IPv6 Address. . . . . . . . . . . : 2001:db8:1234:10:a1b2:c3d4:e5f6:7890(Preferred)
   Temporary IPv6 Address. . . . . . : 2001:db8:1234:10:f1e2:d3c4:b5a6:9780(Preferred)
   Link-local IPv6 Address . . . . . : fe80::a1b2:c3d4:e5f6:7890%12(Preferred)
   Default Gateway . . . . . . . . . : fe80::1%12
```

| Dòng | Ý nghĩa |
|---|---|
| `IPv6 Address` | Địa chỉ ổn định từ SLAAC |
| **`Temporary IPv6 Address`** | **Privacy extension** — đổi định kỳ, dùng cho kết nối đi ra |
| `Default Gateway: fe80::1%12` | ⭐ Gateway là **link-local** của router, `%12` là chỉ số interface |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Host chỉ có link-local, không có GUA | Router không gửi RA | `show ipv6 interface \| include advertisements` | `ipv6 unicast-routing` |
| Host có GUA nhưng **không có default gateway** | `ipv6 nd ra lifetime 0` | `show run interface <int>` | Đặt lifetime > 0 |
| Host không nhận DNS | SLAAC thuần, chưa cấu hình RDNSS | `show run \| include ra dns` | `ipv6 nd ra dns server <ip>` hoặc bật cờ O |
| Ping fail, `show ipv6 neighbors` hiện `INCMP` | NDP bị chặn | Kiểm tra ACL ICMPv6 | Permit `nd-ns`, `nd-na` |
| Ping nhỏ OK, web có ảnh lớn thì treo | **PMTUD hỏng** | Kiểm tra ACL | Permit `packet-too-big` |
| Host lấy sai gateway IPv6 | **Rogue RA** | Wireshark `icmpv6.type==134`, xem Src | Bật **RA Guard** |
| DAD báo trùng địa chỉ | Hai thiết bị cùng địa chỉ | `show ipv6 interface` thấy `DUPLICATE` | Đổi địa chỉ một bên |
| Địa chỉ host đổi mỗi ngày, khó truy vết | **Privacy extension** | `ipconfig /all` thấy "Temporary" | Tắt privacy, hoặc dùng DHCPv6 stateful |
| Bật DHCPv6 stateful mà host vẫn SLAAC | Chưa bật cờ **M** | `show ipv6 interface \| include Hosts use` | `ipv6 nd managed-config-flag` |

---

## 11. LAB

🧪 **LAB 41 — SLAAC, NDP, DHCPv6** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- Router phát RA, PC tự nhận GUA bằng **SLAAC thuần** → `ipconfig /all` xác nhận
- Bắt bằng Wireshark: **RS (133), RA (134), NS (135), NA (136)** — đọc cờ M/O trong RA
- Chuyển sang **DHCPv6 stateless** (bật cờ O) → quan sát `Hosts use DHCP to obtain other config`
- Chuyển sang **DHCPv6 stateful** (bật cờ M) → `show ipv6 dhcp binding` có entry
- **BREAK bắt buộc:** (1) `ipv6 nd ra suppress` → host không có GUA;
  (2) `ipv6 nd ra lifetime 0` → có GUA nhưng **không có gateway**;
  (3) ACL chặn hết ICMPv6 → chứng minh mạng IPv6 chết hoàn toàn

## 12. Challenge

1. Host có GUA đầy đủ nhưng `ping` ra ngoài fail, `ipconfig` cho thấy
   **không có default gateway**. Nguyên nhân?
2. Bạn muốn router cấp prefix cho SLAAC nhưng **không** làm default gateway
   (vì có router khác đảm nhiệm). Làm sao?
3. Phân biệt bằng **một lệnh** xem mạng đang chạy SLAAC thuần, stateless hay stateful.
4. ACL IPv6 của bạn chặn hết ICMPv6 trừ `echo-request/reply`. Ping được, nhưng
   mở một số website thì treo. Vì sao?

<details>
<summary>Đáp án</summary>

**1.** Router đang gửi RA với **`Router Lifetime = 0`**.

RA có hai vai trò độc lập:
- Cấp **prefix** để host làm SLAAC → host vẫn có GUA ✅
- Tuyên bố mình là **default gateway** → điều khiển bởi `Router Lifetime`

`lifetime 0` nghĩa là *"dùng prefix của tôi đi, nhưng đừng gửi gói cho tôi"*.

Kiểm chứng: `show run interface <int> | include ra lifetime`, hoặc Wireshark
xem trường `Router lifetime` trong gói RA.

**2.** Chính là `ipv6 nd ra lifetime 0`:

```cisco
R1(config-if)# ipv6 nd ra lifetime 0
```

Đây là tình huống thật khi có nhiều router trên một link và bạn muốn **chỉ một router**
làm gateway, nhưng vẫn muốn router kia cấp thông tin prefix.

**3.** Một lệnh duy nhất:

```cisco
R1# show ipv6 interface GigabitEthernet0/0 | include Hosts use
```

| Output | Chế độ |
|---|---|
| `Hosts use stateless autoconfig for addresses.` | **SLAAC thuần** (M=0, O=0) |
| `Hosts use DHCP to obtain other configuration.` | **DHCPv6 stateless** (M=0, O=1) |
| `Hosts use DHCP to obtain routable addresses.` | **DHCPv6 stateful** (M=1) |

**4.** Vì **PMTUD bị chặn**.

```text
1. Web server gửi gói 1500 byte
2. Trên đường có một link MTU 1400 (tunnel, PPPoE...)
3. Router IPv6 KHÔNG fragment được → nó gửi về
   ICMPv6 Type 2 "Packet Too Big"
4. ACL của bạn CHẶN gói đó
5. Server không bao giờ biết phải thu nhỏ gói
6. → Gói lớn bị drop IM LẶNG mãi mãi
```

Triệu chứng đặc trưng: **ping được** (gói nhỏ), **trang text load được**,
nhưng **trang có ảnh/file lớn thì treo** rồi timeout.

Sửa: luôn có dòng này trong mọi ACL IPv6:

```cisco
permit icmp any any packet-too-big
```

👉 Đây là khác biệt lớn với IPv4, nơi router tự fragment được nên chặn ICMP
ít gây hậu quả hơn.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 5 loại gói NDP + ICMPv6 type · cờ M/O · 3 chế độ | ⬜ |
| **L2** Explain | Giải thích SLAAC từng bước, không nhìn tài liệu | ⬜ |
| **L3** Configure | Cấu hình cả 3 chế độ, verify bằng `Hosts use` | ⬜ |
| **L4** Troubleshoot | Host có GUA không có gateway → tìm ra `ra lifetime 0` | ⬜ |
| **L5** Design | Chọn chế độ cho 3 kịch bản: văn phòng, guest Wi-Fi, server farm | ⬜ |

## 14. Summary

**Key concepts**

- **NDP chạy trên ICMPv6**: RS (133) · RA (134) · NS (135) · NA (136) · Redirect (137)
- NS/NA thay **ARP**; RS/RA thay **DHCP option gateway**; SLAAC thay **DHCP**
- ⭐ **SLAAC: host tự có địa chỉ chỉ cần một router phát RA** — không cần server
- ⭐ **Default gateway IPv6 là địa chỉ LINK-LOCAL của router**
- Cờ **M** = lấy địa chỉ từ DHCPv6 · cờ **O** = lấy thông tin khác từ DHCPv6
- 3 chế độ: **SLAAC thuần** (0,0) · **stateless** (0,1) · **stateful** (1,1)
- **DAD** kiểm tra trùng **trước khi dùng** — an toàn hơn gratuitous ARP
- `Router Lifetime = 0` → cấp prefix nhưng **không làm gateway**
- ⚠️ **Rogue RA** dễ xảy ra vô tình → bắt buộc có **RA Guard**
- ⚠️ **Luôn permit `packet-too-big`** trong ACL IPv6 — nếu không PMTUD chết

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ipv6 unicast-routing` | ⭐ Thiếu là **không gửi RA** |
| `ipv6 nd managed-config-flag` / `other-config-flag` | Bật cờ M / O |
| `ipv6 nd ra lifetime 0` | Không làm default gateway |
| `ipv6 nd ra suppress` | Tắt RA |
| `ipv6 nd raguard attach-policy` | ⭐ Chống rogue RA |
| `show ipv6 interface <int> \| include Hosts use` | ⭐ Biết ngay chế độ nào đang chạy |
| `show ipv6 neighbors` | Bảng NDP |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Chặn hết ICMPv6 | **Giết chết** NDP, SLAAC, DAD, PMTUD |
| Quên permit `packet-too-big` | Web có nội dung lớn bị treo |
| Quên `ipv6 unicast-routing` | Router không gửi RA, host không có địa chỉ |
| Bật DHCPv6 stateful mà quên cờ M | Host vẫn dùng SLAAC |
| Không bật RA Guard | Một máy Windows bật ICS là chiếm gateway cả VLAN |
| Tìm gateway IPv6 trong dải GUA | Gateway là **link-local** |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 41 với đủ 3 lỗi BREAK.
2. Wireshark trên máy thật, filter `icmpv6.type==134` — bắt một gói RA của router nhà bạn,
   đọc cờ M/O và Router Lifetime.
3. `ipconfig /all` — tìm `Default Gateway` IPv6. Nó là link-local hay GUA?
4. Viết một ACL IPv6 "an toàn tối thiểu" cho interface WAN, không làm chết mạng.

```markdown
- [YYYY-MM-DD] Lesson 30 — SLAAC, NDP, DHCPv6: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 5 gói NDP, cờ M/O, 3 chế độ, DAD, SLAAC từng bước |
| 🔧 **Engineer** | `show ipv6 interface \| include Hosts use`; RDNSS cho SLAAC thuần; `ra lifetime 0` |
| 🏭 **Production** | Rogue RA → RA Guard bắt buộc; ACL IPv6 phải permit NDP + packet-too-big; privacy extension vs truy vết |

### 🔗 Liên kết

- ⬅️ [Lesson 29 — IPv6 địa chỉ & quy hoạch](./lesson-29-ipv6-dia-chi.md)
- ➡️ [Lesson 31 — IPv6 routing & OSPFv3](./lesson-31-ipv6-routing-ospfv3.md)
- 📚 So sánh với ARP: [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md)
