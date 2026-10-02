# LESSON 29 — IPv6: Địa chỉ & Quy hoạch ⭐

> 📦 **Phase 0 đã dạy gì — lesson này thêm gì**
>
> | [Lesson 10](../00-foundation/lesson-10-ipv6-gioi-thieu.md) *(giới thiệu)* | Lesson này *(làm chủ)* |
> |---|---|
> | Rút gọn địa chỉ, nhận diện loại | **Subnetting IPv6**, quy hoạch `/48` → `/64` |
> | Vì sao IPv6 bỏ broadcast/ARP | **EUI-64** tính tay, solicited-node multicast |
> | — | **Anycast**, địa chỉ đặc biệt, IPv6 trong header |

| | |
|---|---|
| **Phase** | 4 — IPv6 |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 10](../00-foundation/lesson-10-ipv6-gioi-thieu.md), [Lesson 07](../00-foundation/lesson-07-vlsm-va-ip-plan.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Rút gọn / mở rộng địa chỉ IPv6 không cần nghĩ
- [ ] **Subnet một `/48` thành các `/64`** — và hiểu vì sao dễ hơn IPv4 nhiều
- [ ] Tính **EUI-64** bằng tay từ một MAC address
- [ ] Giải thích **solicited-node multicast** và vì sao NDP hiệu quả hơn ARP
- [ ] Thiết kế IPv6 addressing plan cho một doanh nghiệp

## 2. Prerequisite

- Rút gọn IPv6, GUA/LLA/ULA/multicast *(Lesson 10)*
- Nguyên tắc IP plan, summarization *(Lesson 07)*

---

## 3. Concept

### Cấu trúc một Global Unicast Address

```text
2001:0db8:1234 : 5678 : 0000:0000:0000:0001
└──────┬─────┘   └─┬─┘   └────────┬────────┘
  Global Routing  Subnet      Interface ID
     Prefix         ID           64 bit
   (thường /48)   16 bit
```

| Phần | Ai cấp | Dài |
|---|---|---|
| **Global Routing Prefix** | ISP/RIR cấp cho bạn | Thường `/48` *(doanh nghiệp)* hoặc `/56` *(gia đình)* |
| **Subnet ID** | **Bạn tự chia** | 16 bit nếu được `/48` |
| **Interface ID** | SLAAC hoặc gán tay | **Luôn 64 bit** |

### Subnetting IPv6 — dễ hơn IPv4 rất nhiều

Được cấp `2001:db8:1234::/48`:

```text
Subnet ID = 16 bit  →  2^16 = 65.536 subnet /64
Mỗi /64   = 2^64 địa chỉ ≈ 18 tỷ tỷ host
```

```text
2001:db8:1234:0000::/64    ← subnet 0
2001:db8:1234:0001::/64    ← subnet 1
2001:db8:1234:0010::/64    ← subnet 16 (hex!)
2001:db8:1234:00ff::/64    ← subnet 255
```

> ⭐ **Không cần tính VLSM.** Mọi subnet đều là `/64`, và bạn có 65.536 cái.
> Toàn bộ nỗi đau subnetting IPv4 **biến mất** — thay vào đó bạn chỉ cần
> một **quy ước đánh số** dễ đọc.

> ⚠️ **Đừng subnet nhỏ hơn `/64`** cho mạng có host — SLAAC yêu cầu đúng 64 bit
> cho Interface ID. Ngoại lệ duy nhất: `/127` cho link point-to-point giữa router
> (RFC 6164), nơi không có host nào cần SLAAC.

### Quy ước đánh số — làm cho dễ đọc

Dùng **hex có nghĩa**, ánh xạ với VLAN ID:

```text
2001:db8:1234:0010::/64   →  VLAN 10   (hex 0010 = 16, nhưng ĐỌC như "VLAN 10")
2001:db8:1234:0020::/64   →  VLAN 20
2001:db8:1234:0099::/64   →  VLAN 99 — management
```

Hoặc chia theo site:

```text
2001:db8:1234:0000::/52   →  Hà Nội      (subnet 0000–0fff)
2001:db8:1234:1000::/52   →  Sài Gòn     (subnet 1000–1fff)
2001:db8:1234:2000::/52   →  Đà Nẵng
```

> 🔧 Mẹo thực tế: **dùng hex trông giống số thập phân** (`0010`, `0020`, `0099`)
> cho dễ đọc, dù về mặt toán học nó là 16, 32, 153. Bạn đang có 65.536 subnet —
> lãng phí vài cái để đổi lấy sự dễ đọc là hoàn toàn xứng đáng.

### EUI-64 — tính tay

Biến MAC 48 bit thành Interface ID 64 bit:

```text
MAC:        00:1A:2B:3C:4D:5E

Bước 1 — chia đôi, chèn FFFE vào giữa:
            001A:2B FF:FE 3C:4D5E
            → 001A:2BFF:FE3C:4D5E

Bước 2 — LẬT bit thứ 7 (từ trái) của byte đầu:
            00 = 0000 0000
                      ↑ bit thứ 7
            → 0000 0010 = 02

Kết quả:    021A:2BFF:FE3C:4D5E
```

Địa chỉ link-local sẽ là: `fe80::21a:2bff:fe3c:4d5e`

> 💡 Bit thứ 7 gọi là **U/L bit** (Universal/Local). MAC do nhà sản xuất cấp có bit này = 0
> (universal); lật thành 1 nghĩa là "địa chỉ này do local tạo ra". Đây là quy ước
> của IPv6, hơi ngược đời nhưng cứ nhớ **"lật bit thứ 7"**.

> ⚠️ **EUI-64 lộ MAC address** → theo dõi được người dùng khi họ đổi mạng.
> Vì vậy Windows/macOS/Linux hiện đại mặc định dùng **privacy extension** —
> Interface ID ngẫu nhiên, đổi định kỳ.

### Solicited-node multicast — vì sao NDP hiệu quả hơn ARP

```text
Địa chỉ unicast:            2001:db8:1234:10::1a2b:3c4d
                                                └──┬──┘
                                            24 bit CUỐI
Solicited-node multicast:   ff02::1:ff2b:3c4d
                            └────┬────┘└──┬──┘
                          prefix cố định  24 bit cuối của unicast
```

Khi R1 muốn tìm MAC của `2001:db8::1a2b:3c4d`, nó gửi NS tới
`ff02::1:ff2b:3c4d` — **chỉ máy nào có 24 bit cuối khớp mới xử lý**.

| | **ARP (IPv4)** | **NDP (IPv6)** |
|---|---|---|
| Gửi tới | **Broadcast** — mọi máy | **Solicited-node multicast** — rất ít máy |
| Ai bị làm phiền | **Tất cả** máy trong VLAN | Chỉ máy có 24 bit cuối khớp |
| Lọc ở đâu | Phần mềm (OS phải kiểm tra) | **Phần cứng** (card mạng lọc) |

> 🔑 Trong một VLAN 250 máy: ARP làm phiền **250 máy**; NDP thường chỉ làm phiền **1 máy**.
> Đây là cải tiến thật sự, không phải chỉ là đổi tên.

### Các địa chỉ đặc biệt cần nhớ

| Địa chỉ | Tên | Tương đương IPv4 |
|---|---|---|
| `::1/128` | Loopback | `127.0.0.1` |
| `::/128` | Unspecified | `0.0.0.0` |
| `::/0` | Default route | `0.0.0.0/0` |
| `fe80::/10` | **Link-local** | `169.254.0.0/16` |
| `fc00::/7` *(thực tế `fd00::/8`)* | **ULA** | RFC 1918 private |
| `2000::/3` | **GUA** | IP public |
| `ff00::/8` | **Multicast** | `224.0.0.0/4` |
| `ff02::1` | All nodes trên link | Broadcast |
| `ff02::2` | All routers trên link | — |
| `ff02::5` / `ff02::6` | OSPFv3 | `224.0.0.5/6` |
| `64:ff9b::/96` | NAT64 | — |

### Anycast — khái niệm mới

**Anycast** = cùng một địa chỉ gán cho **nhiều thiết bị**; gói đi tới **thiết bị gần nhất**
theo routing.

```text
3 DNS server ở 3 thành phố, cùng địa chỉ 2001:db8::53
→ Người ở Hà Nội tới server Hà Nội
→ Người ở Sài Gòn tới server Sài Gòn
```

> 💡 IPv4 cũng làm anycast được, nhưng IPv6 đưa nó thành khái niệm chính thức.
> Đây là cách `8.8.8.8` và `1.1.1.1` hoạt động — **một IP, hàng trăm máy chủ khắp thế giới**.

---

## 4. Why? — vì sao `/64` cho mọi thứ không phải lãng phí

> **Một `/64` có 18 tỷ tỷ địa chỉ cho một VLAN 50 máy. Phí quá?**

| Góc nhìn IPv4 | Góc nhìn IPv6 |
|---|---|
| Địa chỉ **khan hiếm** → tiết kiệm từng cái | Địa chỉ **thừa thãi** → tối ưu cho **sự đơn giản** |
| Tính VLSM mỗi lần thêm subnet | Luôn `/64`, không phải tính gì |
| Đổi subnet khi hết IP | Không bao giờ hết |

Con số thật: không gian IPv6 có **2^128** địa chỉ. Nếu cấp mỗi người trên Trái Đất
một `/48` (65.536 subnet), bạn mới dùng hết một phần **cực nhỏ** của không gian.

> 🔑 **IPv6 đánh đổi "tiết kiệm địa chỉ" lấy "đơn giản vận hành".**
> Đó là một quyết định thiết kế có chủ ý, không phải sơ suất.

---

## 5. How does it work? — một interface có bao nhiêu địa chỉ

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  IPv6 is enabled, link-local address is FE80::1
  Global unicast address(es):
    2001:DB8:1234:10::1, subnet is 2001:DB8:1234:10::/64
  Joined group address(es):
    FF02::1          ← all-nodes
    FF02::2          ← all-routers (vì đây là router)
    FF02::1:FF00:1   ← solicited-node của ::1
```

| Loại | Có mấy cái |
|---|---|
| **Link-local** | **Luôn có đúng 1** (tự sinh, bắt buộc) |
| **Global unicast** | 0, 1, hoặc **nhiều** |
| **Multicast group** | Nhiều — tự join theo vai trò |

> 🔑 Việc một interface có **nhiều địa chỉ IPv6 là bình thường**, không phải lỗi.
> Đây là khác biệt tư duy lớn so với IPv4 (một interface = một IP).

---

## 6. Packet Flow — IPv6 header gọn hơn

| | **IPv4 header** | **IPv6 header** |
|---|---|---|
| Kích thước | 20–60 byte *(thay đổi)* | **40 byte cố định** |
| Checksum | ✅ Có | ❌ **Bỏ** |
| Fragmentation | Router làm được | **Chỉ host nguồn** |
| Options | Trong header | Tách ra **extension header** |
| Trường TTL | `TTL` | Đổi tên thành **`Hop Limit`** |

> 🔑 **Vì sao bỏ checksum:** L2 (Ethernet FCS) đã kiểm lỗi, L4 (TCP/UDP checksum) cũng có.
> Tính lại checksum ở **mỗi hop** là lãng phí. Bỏ đi → router nhanh hơn.

> ⚠️ Hệ quả: IPv6 **phụ thuộc hoàn toàn** vào checksum của L4. UDP over IPv6
> **bắt buộc** phải có checksum (trong IPv4 thì tuỳ chọn).

---

## 7. Real-world Example

🏭 **IPv6 addressing plan cho doanh nghiệp 3 site**

Được ISP cấp `2001:db8:a1b2::/48`:

```text
2001:db8:a1b2:0000::/52   Hà Nội        (4096 subnet /64)
  2001:db8:a1b2:0010::/64   VLAN 10 — Sales
  2001:db8:a1b2:0020::/64   VLAN 20 — IT
  2001:db8:a1b2:0050::/64   VLAN 50 — Server
  2001:db8:a1b2:0090::/64   VLAN 90 — Guest
  2001:db8:a1b2:0099::/64   VLAN 99 — Management

2001:db8:a1b2:1000::/52   Sài Gòn
  2001:db8:a1b2:1010::/64   VLAN 10
  ...

2001:db8:a1b2:f000::/52   Hạ tầng dùng chung
  2001:db8:a1b2:f001::/127  WAN link 1
  2001:db8:a1b2:f002::/127  WAN link 2
  2001:db8:a1b2:ffff::1/128 Loopback R1
```

Lợi ích gom route: Hà Nội summarize thành **một** `2001:db8:a1b2:0000::/52`.

🏭 **Lỗi thiết kế: dùng ULA khi nên dùng GUA**

Nhiều người quen IPv4 private nên dùng `fd00::/8` cho nội bộ, rồi NAT ra GUA.

> ⚠️ **Đây là mang nỗi đau của IPv4 sang IPv6 một cách không cần thiết.**
> Bạn có `/48` = 65.536 subnet public **miễn phí**. Dùng GUA cho mọi thứ,
> và **dùng firewall để kiểm soát truy cập** — đó mới là cách IPv6 được thiết kế.
>
> ULA chỉ hợp lý cho: mạng thật sự không bao giờ ra Internet, hoặc mạng cần
> địa chỉ ổn định khi đổi ISP.

🏭 **Privacy extension gây khó cho quản trị**

Windows mặc định tạo địa chỉ tạm ngẫu nhiên, đổi mỗi ngày. Hậu quả: log firewall
ghi một IP, hôm sau máy đó đã có IP khác → **khó truy vết**.

```powershell
# Tắt privacy extension trên Windows (môi trường doanh nghiệp)
netsh interface ipv6 set global randomizeidentifiers=disabled
netsh interface ipv6 set privacy state=disabled
```

> 🔧 Đánh đổi: tắt privacy → dễ quản trị nhưng lộ MAC. Nhiều doanh nghiệp chọn
> **DHCPv6 stateful** thay vì SLAAC để vừa kiểm soát vừa không lộ MAC.

---

## 8. Cisco CLI

```cisco
! ═══════ BẬT IPv6 — BẮT BUỘC ═══════
R1(config)# ipv6 unicast-routing

! ═══════ GÁN ĐỊA CHỈ ═══════
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ipv6 address 2001:db8:1234:10::1/64          ! gán tay
R1(config-if)# ipv6 address 2001:db8:1234:10::/64 eui-64    ! tự sinh từ MAC
R1(config-if)# ipv6 address fe80::1 link-local               ! link-local dễ nhớ
R1(config-if)# ipv6 enable                                   ! chỉ link-local
R1(config-if)# no shutdown

! Anycast
R1(config-if)# ipv6 address 2001:db8::53/128 anycast

! ═══════ KIỂM TRA ═══════
R1# show ipv6 interface brief
R1# show ipv6 interface GigabitEthernet0/0
R1# show ipv6 neighbors
R1# ping ipv6 2001:db8:1234:10::2
R1# traceroute ipv6 2001:db8:1234:20::1
```

| Lệnh | Lưu ý |
|---|---|
| `ipv6 unicast-routing` | ⚠️ **Thiếu**: router không route IPv6 và **không gửi RA** |
| `eui-64` | Tiện trong lab, **lộ MAC** trong production |
| `ipv6 address fe80::1 link-local` | ⭐ Rất đáng làm — next-hop IPv6 thường là link-local |
| `ipv6 enable` | Chỉ bật link-local, không cần GUA |
| `anycast` | Gán cùng địa chỉ cho nhiều thiết bị |

**Trên máy tính:**

```powershell
# Windows
ipconfig /all
netsh interface ipv6 show address
ping -6 2001:db8::1
tracert -6 2001:db8::1

# Linux
ip -6 addr
ip -6 route
ping6 2001:db8::1
```

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 interface brief
GigabitEthernet0/0         [up/up]
    FE80::1
    2001:DB8:1234:10::1
GigabitEthernet0/1         [up/up]
    FE80::1
    2001:DB8:1234:F001::1
Loopback0                  [up/up]
    FE80::1
    2001:DB8:1234:FFFF::1
```

> 🔍 Chú ý: **cùng một `FE80::1` xuất hiện trên nhiều interface** — hoàn toàn bình thường.
> Link-local chỉ cần duy nhất **trong phạm vi một link**, không cần duy nhất toàn cục.
> Đó cũng là lý do route IPv6 có next-hop link-local **phải kèm tên interface**.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 neighbors
IPv6 Address                              Age Link-layer Addr State Interface
2001:DB8:1234:10::10                        0 001a.2b3c.4d5e  REACH Gi0/0
FE80::21A:2BFF:FE3C:4D5E                    0 001a.2b3c.4d5e  REACH Gi0/0
```

| State | Nghĩa |
|---|---|
| `REACH` | Vừa xác nhận, dùng được |
| `STALE` | Lâu chưa thấy, vẫn dùng nhưng sẽ kiểm tra lại |
| `DELAY` | Đang chờ trước khi gửi NS |
| `PROBE` | Đang gửi NS để kiểm tra |
| **`INCMP`** | **Chưa phân giải được** — tương đương `incomplete` của ARP |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Interface chỉ có `FE80::` | Chưa gán GUA | `show ipv6 interface brief` | `ipv6 address <addr>/64` |
| Router không route IPv6 | Quên `ipv6 unicast-routing` | `show run \| include unicast-routing` | Bật lệnh đó |
| `show ipv6 neighbors` hiện `INCMP` | NDP không phân giải được | Kiểm tra ACL ICMPv6 | **Không chặn ICMPv6** |
| Host không tự nhận địa chỉ | Router không gửi RA | `show ipv6 interface \| include RA` | `ipv6 unicast-routing` |
| Địa chỉ host đổi mỗi ngày | **Privacy extension** | `ipconfig /all` thấy "Temporary" | Tắt privacy, hoặc dùng DHCPv6 |
| Ping link-local fail | Thiếu chỉ định interface | — | `ping fe80::2%Gi0/0` hoặc `ping ipv6 fe80::2` rồi chọn interface |
| Subnet `/80` không có host nào tự cấu hình được | **SLAAC cần đúng `/64`** | `show ipv6 interface` | Đổi về `/64` |
| Gán 2 địa chỉ GUA, không biết dùng cái nào | Bình thường — chọn theo RFC 6724 | `show ipv6 interface` | Không phải lỗi |

---

## 11. LAB

🧪 **LAB 40 — IPv6 addressing & quy hoạch** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- Thiết kế addressing plan từ `2001:db8:a1b2::/48` cho 2 site × 4 VLAN + 2 WAN link
- Gán địa chỉ cho 2 router + 4 PC, ping được giữa các VLAN
- Dùng `eui-64` trên một interface → **tính tay trước**, rồi so với kết quả thật
- Đặt link-local `fe80::1` dễ nhớ trên mọi router
- **BREAK bắt buộc:** (1) quên `ipv6 unicast-routing` → quan sát host không nhận địa chỉ;
  (2) gán `/80` cho một VLAN → chứng minh SLAAC không chạy;
  (3) ping link-local **không** chỉ định interface → quan sát lỗi

## 12. Challenge

1. Rút gọn tối đa: `2001:0db8:0000:0000:00ab:0000:0000:1234`
2. MAC `AC:DE:48:23:45:67` → tính EUI-64 và địa chỉ link-local.
3. Bạn được cấp `2001:db8:cafe::/48`. Thiết kế subnet cho 3 site × 6 VLAN,
   sao cho mỗi site summarize được thành một prefix.
4. Địa chỉ `2001:db8::1a2b:3c4d` có solicited-node multicast là gì?

<details>
<summary>Đáp án</summary>

**1.** `2001:db8::ab:0:0:1234`

Giải thích: hai nhóm 0 đầu (vị trí 3–4) **dài hơn** hai nhóm 0 sau (vị trí 6–7),
nên `::` thay cho chuỗi dài hơn. Nhóm `00ab` → `ab`. Hai nhóm `0000` còn lại
rút thành `0:0` *(không được dùng `::` lần hai)*.

**2.** MAC `AC:DE:48:23:45:67`

```text
Bước 1 — chèn FFFE:    ACDE:48 FF:FE 23:4567  →  ACDE:48FF:FE23:4567
Bước 2 — lật bit 7 của byte đầu:
         AC = 1010 1100
                   ↑ bit thứ 7 (đang là 0)
            → 1010 1110 = AE

EUI-64:         AEDE:48FF:FE23:4567
Link-local:     fe80::aede:48ff:fe23:4567
```

**3.** Chia `/48` thành các `/52` cho từng site *(mỗi `/52` = 4096 subnet `/64`)*:

```text
2001:db8:cafe:0000::/52    Site 1
  2001:db8:cafe:0010::/64    VLAN 10
  2001:db8:cafe:0020::/64    VLAN 20
  2001:db8:cafe:0030::/64    VLAN 30
  2001:db8:cafe:0040::/64    VLAN 40
  2001:db8:cafe:0050::/64    VLAN 50
  2001:db8:cafe:0099::/64    VLAN 99 (mgmt)

2001:db8:cafe:1000::/52    Site 2   (cùng khuôn VLAN)
2001:db8:cafe:2000::/52    Site 3
2001:db8:cafe:f000::/52    Hạ tầng (WAN link /127, loopback /128)
```

Summarize: mỗi site **một route `/52`**. Còn thừa 12 `/52` cho site mới.

**4.** `2001:db8::1a2b:3c4d` → lấy **24 bit cuối** = `2b:3c4d`

```text
Solicited-node multicast = ff02::1:ff2b:3c4d
```

Công thức: `ff02::1:ff` + 24 bit cuối của địa chỉ unicast.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Cấu trúc GUA · prefix của LLA/ULA/multicast · `ff02::1`, `ff02::2`, `ff02::5` | ⬜ |
| **L2** Explain | Giải thích vì sao solicited-node multicast hiệu quả hơn broadcast | ⬜ |
| **L3** Configure | Gán GUA + link-local tuỳ chỉnh cho 2 router, ping được | ⬜ |
| **L4** Troubleshoot | Host không nhận địa chỉ → tìm ra thiếu `ipv6 unicast-routing` | ⬜ |
| **L5** Design | Thiết kế addressing plan từ một `/48` cho 3 site | ⬜ |

## 14. Summary

**Key concepts**

- GUA = **Global Routing Prefix (/48)** + **Subnet ID (16 bit)** + **Interface ID (64 bit)**
- ⭐ **Mọi subnet có host đều là `/64`** — không cần VLSM, có 65.536 subnet từ một `/48`
- `/127` cho WAN link point-to-point *(RFC 6164)*, `/128` cho loopback
- **EUI-64**: chèn `FFFE` vào giữa MAC, **lật bit thứ 7**
- ⚠️ EUI-64 lộ MAC → privacy extension, hoặc DHCPv6 stateful
- ⭐ **Solicited-node multicast** `ff02::1:ffXX:XXXX` = `ff02::1:ff` + 24 bit cuối
- Một interface có **nhiều địa chỉ IPv6** là bình thường
- Link-local **không cần duy nhất toàn cục** → route next-hop phải kèm interface
- IPv6 header **40 byte cố định**, **bỏ checksum**, chỉ host nguồn fragment
- ⭐ **Dùng GUA cho nội bộ**, kiểm soát bằng firewall — đừng mang NAT từ IPv4 sang

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ipv6 unicast-routing` | ⭐ **Luôn đầu tiên** |
| `ipv6 address <addr>/64` | Gán GUA |
| `ipv6 address fe80::1 link-local` | Link-local dễ nhớ |
| `show ipv6 interface brief` | Xem mọi địa chỉ đã gán |
| `show ipv6 neighbors` | Bảng NDP — tương đương `show ip arp` |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Subnet nhỏ hơn `/64` cho mạng host | SLAAC không chạy |
| Dùng ULA + NAT66 cho nội bộ | Mang nỗi đau IPv4 sang vô ích |
| Quên `ipv6 unicast-routing` | Không route, không gửi RA |
| Hoảng khi thấy nhiều địa chỉ trên 1 interface | Bình thường |
| Ping link-local không chỉ định interface | Không biết gửi ra đâu |
| Tiết kiệm địa chỉ như IPv4 | Mất đi sự đơn giản — không có lợi gì |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 40 với đủ 3 lỗi BREAK.
2. Tính EUI-64 cho MAC của chính máy bạn, rồi so với `fe80::` thật trong `ipconfig`.
   *(Nếu khác → máy đang dùng privacy extension.)*
3. Thiết kế addressing plan IPv6 cho công ty bạn từ một `/48` giả định.
4. Truy cập `test-ipv6.com` — công ty/nhà bạn đã có IPv6 chưa?

```markdown
- [YYYY-MM-DD] Lesson 29 — IPv6 địa chỉ & quy hoạch: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Rút gọn, loại địa chỉ, EUI-64, solicited-node multicast, `/64` |
| 🔧 **Engineer** | Quy ước đánh số dễ đọc; link-local `fe80::1`; summarize theo site |
| 🏭 **Production** | Dùng GUA không dùng NAT66; privacy extension gây khó truy vết; không chặn ICMPv6 |

### 🔗 Liên kết

- 📚 Nền tảng: [Lesson 10 — IPv6 giới thiệu](../00-foundation/lesson-10-ipv6-gioi-thieu.md)
- ➡️ [Lesson 30 — SLAAC, NDP, DHCPv6](./lesson-30-slaac-ndp-dhcpv6.md)
- 🧮 [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md)
