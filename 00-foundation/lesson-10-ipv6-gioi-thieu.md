# LESSON 10 — IPv6: Giới thiệu

> 📌 Lesson **cuối Phase 0**. Mục tiêu ở đây chỉ là *làm quen và hiểu vì sao* —
> học sâu (SLAAC, NDP, OSPFv3) ở [Phase 4](../04-ipv6/README.md).

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~1.5 giờ |
| **Prerequisite** | [Lesson 02](./lesson-02-ipv4-va-subnetting.md), [Lesson 05](./lesson-05-gateway-arp-icmp.md), [Lesson 09](./lesson-09-nat-private-public.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Rút gọn và mở rộng một địa chỉ IPv6 không cần nghĩ
- [ ] Nhìn địa chỉ là nói ngay loại nào: GUA / Link-local / ULA / Multicast
- [ ] Giải thích **vì sao IPv6 bỏ broadcast** và **bỏ ARP** — cái gì thay thế
- [ ] Nói được IPv6 thay đổi gì với NAT và với thiết kế mạng
- [ ] Bật IPv6 cơ bản trên router và verify

## 2. Prerequisite

- Nhị phân, prefix, subnet *(Lesson 02)*
- ARP và vì sao nó dùng broadcast *(Lesson 05)*
- Vì sao NAT tồn tại *(Lesson 09)*

---

## 3. Concept

### Vì sao 128 bit

| | IPv4 | IPv6 |
|---|---|---|
| Độ dài | **32 bit** | **128 bit** |
| Số địa chỉ | ~4,3 tỷ | ~340 **undecillion** (3,4 × 10³⁸) |
| Viết | Thập phân, 4 octet | **Hex**, 8 nhóm 4 ký tự |
| Phân cách | Dấu chấm `.` | Dấu hai chấm `:` |

```text
2001:0db8:0000:0000:0000:ff00:0042:8329
└──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘
 8 nhóm × 4 ký tự hex × 4 bit = 128 bit
```

### Hai quy tắc rút gọn

**Quy tắc 1 — bỏ số 0 ở đầu mỗi nhóm:**

```text
2001:0db8:0000:0000:0000:ff00:0042:8329
2001:db8:0:0:0:ff00:42:8329
```

**Quy tắc 2 — thay một chuỗi nhóm-toàn-0 liên tiếp bằng `::`:**

```text
2001:db8:0:0:0:ff00:42:8329
2001:db8::ff00:42:8329
```

> ⚠️ **`::` chỉ được dùng MỘT LẦN** trong một địa chỉ. Nếu dùng hai lần,
> không thể suy ra mỗi chỗ thay bao nhiêu nhóm.
>
> `2001::25de::cade` → **SAI**.

**Luyện tập nhanh:**

| Đầy đủ | Rút gọn |
|---|---|
| `2001:0db8:0000:0000:0000:0000:0000:0001` | `2001:db8::1` |
| `fe80:0000:0000:0000:0204:61ff:fe9d:f156` | `fe80::204:61ff:fe9d:f156` |
| `0000:0000:0000:0000:0000:0000:0000:0001` | `::1` *(loopback)* |
| `0000:0000:0000:0000:0000:0000:0000:0000` | `::` *(unspecified)* |

### Các loại địa chỉ — nhìn là biết

| Loại | Prefix | Tương đương IPv4 | Ghi chú |
|---|---|---|---|
| **Global Unicast (GUA)** | `2000::/3`<br>*(thực tế hay thấy `2001:`)* | IP public | Định tuyến được toàn cầu |
| **Link-local (LLA)** | **`fe80::/10`** | `169.254.x.x` (APIPA) | ⭐ **Mọi interface IPv6 LUÔN có một cái**, tự sinh |
| **Unique Local (ULA)** | `fc00::/7`<br>*(thực tế `fd00::/8`)* | Private RFC 1918 | Nội bộ, không route ra Internet |
| **Multicast** | **`ff00::/8`** | `224.0.0.0/4` | Thay thế hẳn broadcast |
| **Loopback** | `::1` | `127.0.0.1` | |
| **Unspecified** | `::` | `0.0.0.0` | |

> 🔑 **Link-local là thứ khác biệt lớn nhất so với IPv4.** Nó tự sinh ngay khi interface
> bật IPv6, không cần cấu hình, không cần DHCP. Và **next-hop của route IPv6 thường
> chính là địa chỉ link-local** — không phải GUA. Người mới rất hay bất ngờ chỗ này.

### Multicast cần nhớ

| Địa chỉ | Nghĩa |
|---|---|
| `ff02::1` | **Tất cả node** trên link — thay cho broadcast |
| `ff02::2` | **Tất cả router** trên link |
| `ff02::5` | Tất cả router OSPFv3 |
| `ff02::1:ffXX:XXXX` | **Solicited-node** — dùng cho NDP |

### Cấu trúc địa chỉ GUA

```text
2001:0db8:1234 : 5678 : 0000:0000:0000:0001
└──────┬─────┘   └─┬─┘   └────────┬────────┘
   Global          Subnet      Interface ID
   Routing          ID           (64 bit)
   Prefix         (16 bit)
   (48 bit)
```

> 📏 **Mọi subnet IPv4 "bình thường" đều là `/64`.** Không phải vì luật, mà vì SLAAC
> yêu cầu đúng 64 bit cho Interface ID. Đừng subnet nhỏ hơn `/64` cho mạng có host.
> Với `/48` được cấp, bạn có **65.536 subnet `/64`** — thoải mái không cần tính toán.

---

## 4. Why?

### Vì sao cần IPv6

| Vấn đề của IPv4 | IPv6 giải quyết |
|---|---|
| **Hết địa chỉ** — cạn từ 2011 | 340 undecillion địa chỉ |
| **Phải NAT** → phá end-to-end | Đủ địa chỉ public cho mọi thiết bị → **không cần NAT** |
| Header phức tạp, có checksum | Header **cố định 40 byte**, bỏ checksum (L2 và L4 đã có) |
| Router phải phân mảnh gói | **Chỉ host nguồn** phân mảnh → router nhẹ hơn |
| Broadcast làm phiền mọi máy | Chỉ dùng **multicast** có phạm vi |
| Cấu hình cần DHCP | **SLAAC** — host tự sinh địa chỉ từ RA |

### Vì sao IPv6 bỏ broadcast

Broadcast buộc **mọi** máy xử lý rồi mới vứt (Lesson 04). IPv6 thay bằng multicast
có phạm vi hẹp:

```text
IPv4: "Ai có 192.168.1.1?"  → broadcast → 250 máy đều bị đánh thức
IPv6: NDP gửi tới solicited-node multicast → chỉ máy có hậu tố khớp mới xử lý
```

Card mạng lọc multicast **ở phần cứng** → CPU của 249 máy kia không bị làm phiền.

### Vì sao IPv6 bỏ ARP

Vì ARP dựa trên **broadcast**, mà IPv6 không có broadcast. Thay thế là **NDP**
(Neighbor Discovery Protocol), chạy trên **ICMPv6**:

| Chức năng | IPv4 | IPv6 (NDP) |
|---|---|---|
| Tìm MAC từ IP | ARP Request/Reply | **NS / NA** (Neighbor Solicitation/Advertisement) |
| Tìm router | *(gán tay / DHCP)* | **RS / RA** (Router Solicitation/Advertisement) |
| Tự cấu hình địa chỉ | DHCP | **SLAAC** (từ thông tin trong RA) |
| Phát hiện trùng địa chỉ | Gratuitous ARP | **DAD** (Duplicate Address Detection) |

> ⚠️ **Hệ quả thực tế rất quan trọng:** chặn sạch ICMPv6 bằng ACL "cho an toàn" sẽ
> **giết chết mạng IPv6** — vì NDP, RA, DAD đều chạy trên ICMPv6. Với IPv4 bạn có thể
> chặn ICMP mà mạng vẫn chạy; với IPv6 thì **không**.

---

## 5. How does it work? — SLAAC tóm tắt

```text
1. Interface bật IPv6
   → tự sinh LINK-LOCAL (fe80::...) ngay lập tức
2. Chạy DAD: gửi NS hỏi chính địa chỉ mình → không ai trả lời → địa chỉ an toàn
3. Gửi RS (Router Solicitation) tới ff02::2 — "có router nào không?"
4. Router trả RA (Router Advertisement): "prefix ở đây là 2001:db8:1::/64"
5. Host tự ghép:  prefix (64 bit)  +  Interface ID (64 bit)  =  địa chỉ GUA đầy đủ
6. Router gửi RA cũng chính là default gateway → host lấy luôn
```

Interface ID 64 bit được sinh theo một trong hai cách:

| Cách | Mô tả | Vấn đề |
|---|---|---|
| **EUI-64** | Lấy MAC 48 bit, chèn `FFFE` vào giữa, lật bit thứ 7 | Lộ MAC → **theo dõi được người dùng** |
| **Privacy extension** | Sinh ngẫu nhiên, đổi định kỳ | Mặc định trên Windows/macOS/Linux hiện đại |

> 💡 Điều đáng nhớ nhất về SLAAC: **host có địa chỉ mà không cần server nào cả.**
> Chỉ cần một router phát RA. Đây là lý do nhiều mạng IPv6 không chạy DHCPv6.

---

## 6. Packet Flow — so sánh trực tiếp

**Kịch bản:** PC-A muốn gửi gói cho PC-B cùng link.

| Bước | IPv4 | IPv6 |
|:---:|---|---|
| 1 | ARP Request → **broadcast** `FF:FF:FF:FF:FF:FF` | NS → **multicast** `ff02::1:ffXX:XXXX` |
| 2 | **Mọi** máy trong VLAN nhận và xử lý | **Chỉ** máy có hậu tố khớp xử lý |
| 3 | ARP Reply (unicast) | NA (unicast) |
| 4 | Gửi dữ liệu | Gửi dữ liệu |

**Khác biệt cốt lõi:** bước 2. IPv4 làm phiền tất cả, IPv6 chỉ làm phiền đúng máy cần.

---

## 7. Real-world Example

🏭 **"Tắt IPv6 cho đỡ rắc rối"** — thói quen phổ biến và thường sai

Nhiều quản trị viên tắt IPv6 trên Windows vì "không dùng". Hậu quả:
Windows và nhiều ứng dụng (đặc biệt Active Directory, Exchange) **được thiết kế với
giả định IPv6 bật**. Microsoft khuyến cáo **không tắt**. Nếu không muốn dùng,
hãy không cấp địa chỉ — đừng tắt stack.

🏭 **Rogue RA — mối nguy ít người biết**

Trong IPv4, rogue DHCP server là mối nguy quen thuộc. Trong IPv6 còn dễ hơn: **bất kỳ máy
nào phát RA cũng trở thành gateway** của cả link, không cần cấu hình gì. Một máy Windows
bật Internet Connection Sharing có thể vô tình chiếm quyền.

Phòng chống: **RA Guard** trên switch (tương tự DHCP Snooping).

🏭 **Dual-stack là thực tế hiện nay**

Gần như không ai chạy IPv6-only. Mô hình phổ biến: **dual-stack** — thiết bị có cả IPv4
và IPv6, ứng dụng ưu tiên IPv6 nếu có (thuật toán Happy Eyeballs). Nghĩa là bạn phải
troubleshoot **cả hai**, và một sự cố IPv6 có thể biểu hiện như "web chậm" dù IPv4 hoàn toàn ổn.

---

## 8. Cisco CLI

```cisco
! ═══════ 1. Bật routing IPv6 — BẮT BUỘC, hay bị quên ═══════
R1(config)# ipv6 unicast-routing

! ═══════ 2. Gán địa chỉ ═══════
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ipv6 address 2001:db8:1::1/64              ! gán tay
R1(config-if)# ipv6 address 2001:db8:1::/64 eui-64        ! tự sinh host ID từ MAC
R1(config-if)# ipv6 address fe80::1 link-local            ! đặt link-local dễ nhớ
R1(config-if)# no shutdown

! Bật IPv6 chỉ với link-local (không cần GUA)
R1(config-if)# ipv6 enable

! ═══════ 3. Static route IPv6 ═══════
R1(config)# ipv6 route 2001:db8:2::/64 2001:db8:12::2
R1(config)# ipv6 route ::/0 2001:db8:12::2                ! default route

! ═══════ 4. Kiểm tra ═══════
R1# show ipv6 interface brief
R1# show ipv6 interface GigabitEthernet0/0
R1# show ipv6 route
R1# show ipv6 neighbors                                    ! ~ "show ip arp" của IPv6
R1# ping ipv6 2001:db8:2::1
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `ipv6 unicast-routing` | Bật định tuyến IPv6 **toàn cục** | ⚠️ **Thiếu dòng này**: router không route IPv6 và **không gửi RA** → host không SLAAC được |
| `ipv6 address ... eui-64` | Tự sinh 64 bit cuối từ MAC | Tiện trong lab, lộ MAC trong production |
| `ipv6 address fe80::1 link-local` | Đặt link-local dễ nhớ | Rất đáng làm — next-hop IPv6 thường là link-local |
| `show ipv6 neighbors` | Bảng NDP | Tương đương `show ip arp` |

> **Khác biệt platform:** IOS/IOS-XE như trên. **NX-OS** cần `feature ospfv3` cho OSPFv3,
> và một số lệnh `show` có format khác. Trên NX-OS, IPv6 routing bật theo VRF.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 interface brief
GigabitEthernet0/0         [up/up]
    FE80::1
    2001:DB8:1::1
GigabitEthernet0/1         [up/up]
    FE80::1
    2001:DB8:12::1
```

> 🔍 Chú ý: **mỗi interface có ÍT NHẤT 2 địa chỉ** — một link-local (`FE80::`) và
> một hoặc nhiều GUA. Đây là bình thường, không phải lỗi cấu hình.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 route
C   2001:DB8:1::/64 [0/0]
     via GigabitEthernet0/0, directly connected
L   2001:DB8:1::1/128 [0/0]
     via GigabitEthernet0/0, receive
S   2001:DB8:2::/64 [1/0]
     via FE80::2, GigabitEthernet0/1
S   ::/0 [1/0]
     via 2001:DB8:12::2
```

> 🔑 Nhìn dòng `via FE80::2` — **next-hop là địa chỉ link-local**, và bắt buộc phải
> kèm theo tên interface (vì link-local không duy nhất toàn cục). Đây là điểm khác
> biệt rõ nhất so với routing table IPv4.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 neighbors
IPv6 Address          Age Link-layer Addr State Interface
2001:DB8:1::10          0 001a.2b3c.4d5e  REACH Gi0/0
FE80::21A:2BFF:FE3C:4D5E 0 001a.2b3c.4d5e REACH Gi0/0
```

| State | Nghĩa |
|---|---|
| `REACH` | Vừa xác nhận, dùng được |
| `STALE` | Lâu chưa thấy, vẫn dùng nhưng sẽ kiểm tra lại |
| `INCMP` | **Chưa phân giải được** — tương đương `incomplete` của ARP |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Host không tự nhận địa chỉ IPv6 | Quên `ipv6 unicast-routing` → router không gửi RA | `show run \| include unicast-routing` | Bật dòng đó |
| Router không route IPv6 | Cùng nguyên nhân trên | `show ipv6 route` trống | `ipv6 unicast-routing` |
| Interface chỉ có `FE80::` | Chưa gán GUA, hoặc chỉ `ipv6 enable` | `show ipv6 interface brief` | Gán `ipv6 address` |
| Ping IPv6 fail, `show ipv6 neighbors` hiện `INCMP` | NDP không phân giải được | Kiểm tra ACL ICMPv6 | **Không chặn ICMPv6** |
| Mạng IPv6 chết sau khi áp ACL | **Chặn nhầm ICMPv6** | `show access-lists` | Permit ICMPv6 (NS/NA/RS/RA) |
| Host lấy sai gateway IPv6 | **Rogue RA** | `show ipv6 neighbors`, Wireshark lọc `icmpv6.type==134` | Bật **RA Guard** |
| Web chậm bất thường, IPv4 vẫn ổn | Dual-stack: đang thử IPv6 rồi mới fallback | Tắt IPv6 trên máy để thử | Sửa đường IPv6, đừng tắt vĩnh viễn |

---

## 11. LAB

🧪 **Bài làm quen** *(nhẹ — lab đầy đủ nằm ở Phase 4)*

1. Trên máy bạn: `ipconfig` (Windows) hoặc `ip -6 addr` (Linux).
   Tìm địa chỉ bắt đầu bằng `fe80::` — đó là link-local, tự sinh, bạn chưa từng cấu hình nó.
2. `ping -6 ::1` — loopback IPv6.
3. Trong Packet Tracer: 2 router nối nhau, gán GUA `/64` mỗi bên, ping được nhau.
   Bật `ipv6 unicast-routing` rồi xem `show ipv6 route` thay đổi thế nào.
4. Wireshark lọc `icmpv6` trên mạng thật — tìm gói **RA** (type 134), xem prefix được quảng bá.

## 12. Challenge

1. Rút gọn tối đa: `2001:0db8:0000:0000:0abc:0000:0000:1234`
2. Mở rộng đầy đủ: `fe80::1`
3. Vì sao `2001::25de::cade` là **sai**?
4. Vì sao subnet IPv6 cho mạng có host gần như luôn là `/64`, dù `/127` hay `/112` hợp lệ?
5. Một ACL IPv6 chặn hết ICMPv6 "cho an toàn". Kể **3 thứ** sẽ hỏng.

<details>
<summary>Đáp án</summary>

**1.** `2001:db8::abc:0:0:1234`

Giải thích: hai nhóm 0 đầu (vị trí 3–4) dài hơn hai nhóm 0 sau (vị trí 6–7), nên `::`
thay cho chuỗi dài hơn. Nhóm `0abc` bỏ số 0 đầu thành `abc`; hai nhóm `0000` còn lại
rút thành `0:0` (không được dùng `::` lần hai).

**2.** `fe80:0000:0000:0000:0000:0000:0000:0001`

**3.** Vì `::` xuất hiện **hai lần**. Địa chỉ phải đủ 128 bit; với hai chỗ `::` không thể
biết mỗi chỗ thay bao nhiêu nhóm 0 — có nhiều cách diễn giải khác nhau nên nhập nhằng.

**4.** Vì **SLAAC yêu cầu đúng 64 bit cho Interface ID**. Prefix dài hơn `/64` làm SLAAC
không hoạt động, host không tự sinh địa chỉ được. `/127` chỉ dùng cho **link point-to-point
giữa router** (RFC 6164), nơi không có host nào cần SLAAC.

**5.** Ba thứ hỏng (chọn 3 trong số này):

| Hỏng | Vì sao |
|---|---|
| **NDP** (NS/NA) | Không phân giải được IPv6 → MAC → **không ping được ai** |
| **SLAAC** (RS/RA) | Host không nhận được prefix → không có địa chỉ, không có gateway |
| **DAD** | Không phát hiện được trùng địa chỉ |
| **PMTUD** | Không nhận được "Packet Too Big" → gói lớn bị drop im lặng, web treo |

Khác biệt cốt lõi với IPv4: ICMP ở IPv4 chỉ là tiện ích chẩn đoán, chặn được;
ICMPv6 là **thành phần vận hành bắt buộc** của IPv6.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | IPv6 bao nhiêu bit · prefix của LLA/ULA/multicast · `ff02::1` và `ff02::2` | ⬜ |
| **L2** Explain | Giải thích vì sao IPv6 bỏ ARP và bỏ broadcast, cái gì thay thế | ⬜ |
| **L3** Configure | Bật `ipv6 unicast-routing`, gán GUA cho 2 router, ping được nhau | ⬜ |
| **L4** Troubleshoot | Host không nhận địa chỉ IPv6 → nêu nguyên nhân phổ biến nhất | ⬜ |
| **L5** Design | Được cấp một `/48` — chia subnet cho công ty 20 VLAN, 3 site | ⬜ |

## 14. Summary

**Key concepts**

- IPv6 = **128 bit**, viết hex, 8 nhóm 4 ký tự
- Rút gọn: bỏ số 0 đầu nhóm · `::` thay chuỗi nhóm-0 — **chỉ dùng một lần**
- GUA `2000::/3` · **Link-local `fe80::/10`** · ULA `fd00::/8` · Multicast `ff00::/8`
- ⭐ **Mọi interface IPv6 luôn có link-local** — và next-hop route thường là link-local
- ⭐ **Không có broadcast** → dùng multicast (`ff02::1`, `ff02::2`)
- ⭐ **Không có ARP** → dùng **NDP** chạy trên **ICMPv6**
- **SLAAC**: host tự sinh địa chỉ từ RA, không cần DHCP server
- Subnet cho host luôn là **`/64`** (SLAAC yêu cầu)
- Đủ địa chỉ → **không cần NAT** → khôi phục mô hình end-to-end

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ipv6 unicast-routing` | **Luôn làm đầu tiên** — thiếu là không gì chạy |
| `ipv6 address <addr>/64` | Gán GUA |
| `show ipv6 interface brief` | Xem địa chỉ đã gán |
| `show ipv6 neighbors` | Bảng NDP — tương đương `show ip arp` |
| `show ipv6 route` | Routing table IPv6 |

**Common mistakes**

| Sai | Đúng |
|---|---|
| Dùng `::` hai lần | Chỉ **một lần** |
| Quên `ipv6 unicast-routing` | Router không route và **không gửi RA** |
| Chặn hết ICMPv6 bằng ACL | **Giết chết** NDP, SLAAC, DAD, PMTUD |
| Subnet nhỏ hơn `/64` cho mạng host | SLAAC không chạy |
| Tắt hẳn IPv6 trên Windows | Microsoft khuyến cáo không tắt |
| Nghĩ next-hop IPv6 phải là GUA | Thường là **link-local** + tên interface |

## 15. Homework + cập nhật PROGRESS

1. `ipconfig` / `ip -6 addr` — tìm địa chỉ `fe80::` trên máy bạn. Bạn chưa từng cấu hình nó.
2. Kiểm tra nhà/công ty bạn đã có IPv6 chưa: truy cập `test-ipv6.com`.
3. Rút gọn 5 địa chỉ IPv6 tự nghĩ ra, rồi mở rộng lại để kiểm tra.
4. Làm bài LAB làm quen ở mục 11.

```markdown
- [YYYY-MM-DD] Lesson 10 — IPv6 giới thiệu: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 0

Trước khi sang [Phase 1 — Switching](../01-switching/README.md), làm
**[Mini Exam Phase 0](./review-phase00.md)**. Dưới 80% thì quay lại ôn, đừng đi tiếp.

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Rút gọn địa chỉ, nhận diện loại, NDP thay ARP, multicast thay broadcast, `/64` |
| 🔧 **Engineer** | Đặt link-local dễ nhớ (`fe80::1`); hiểu next-hop là link-local |
| 🏭 **Production** | Không chặn ICMPv6; không tắt stack IPv6 trên Windows; cảnh giác rogue RA → RA Guard; dual-stack phải debug cả hai |

### 🔗 Liên kết

- ⬅️ [Lesson 09 — NAT](./lesson-09-nat-private-public.md)
- 📝 [Mini Exam Phase 0](./review-phase00.md)
- ➡️ [Phase 1 — Switching](../01-switching/README.md)
- 🔜 Học sâu: [Phase 4 — IPv6](../04-ipv6/README.md)
