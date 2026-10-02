# LAB 40 — IPv6 addressing & quy hoạch

| | |
|---|---|
| **Phase** | 4 |
| **Lesson liên quan** | [Lesson 29 — Địa chỉ & quy hoạch IPv6](../04-ipv6/lesson-29-ipv6-dia-chi.md) |
| **Công cụ** | Giấy + Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Chia một `/48` thành các `/64` cho từng VLAN *(và hiểu vì sao luôn /64)*
- [ ] Tính **EUI-64** bằng tay rồi đối chiếu với IOS
- [ ] Nhận diện các loại địa chỉ: GUA, **link-local (fe80)**, ULA, multicast
- [ ] Tìm **solicited-node multicast** của một địa chỉ
- [ ] Rút gọn/giãn địa chỉ IPv6 đúng quy tắc

## 2. Prerequisite

- [Lesson 10](../00-foundation/lesson-10-ipv6-gioi-thieu.md) — IPv6 nhập môn
- [Lesson 29](../04-ipv6/lesson-29-ipv6-dia-chi.md) — subnetting, EUI-64, solicited-node

---

## 3. Topology

```text
   VLAN 10 ─┐
   VLAN 20 ─┼── R1 ── (các /64 từ một /48)
   VLAN 30 ─┘
```

Doanh nghiệp được cấp: **`2001:db8:acad::/48`**.

## 4. Kế hoạch địa chỉ (bạn điền)

| VLAN | Mục đích | Prefix /64 | Gateway *(::1)* |
|:---:|---|---|---|
| 10 | USER | `2001:db8:acad:0010::/64` | `2001:db8:acad:10::1` |
| 20 | SERVER | `2001:db8:acad:0020::/64` | `2001:db8:acad:20::1` |
| 30 | GUEST | `2001:db8:acad:____::/64` | `____` |
| 99 | MGMT | `2001:db8:acad:____::/64` | `____` |

---

## 5. Yêu cầu LAB

- [ ] Gán GUA + link-local cho 3 interface R1
- [ ] Bật EUI-64 trên một interface, tính tay rồi so sánh
- [ ] PC nhận GUA, ping được gateway và PC khác VLAN
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Bật IPv6 routing + gán địa chỉ

```cisco
R1(config)# ipv6 unicast-routing              ! BẮT BUỘC để router làm IPv6

R1(config)# interface Gi0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ipv6 address 2001:db8:acad:10::1/64
R1(config-subif)# ipv6 address fe80::1 link-local

R1(config)# interface Gi0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ipv6 address 2001:db8:acad:20::1/64
R1(config-subif)# ipv6 address fe80::1 link-local
```

> 🔑 `fe80::1` link-local **giống nhau** trên nhiều interface được — vì link-local
> chỉ có ý nghĩa **trong một link**. Đặt `fe80::1` cho mọi interface giúp gateway dễ nhớ.

### Bước 2 — EUI-64 tính tay ⭐

```cisco
R1(config)# interface Gi0/1
R1(config-if)# ipv6 address 2001:db8:acad:99::/64 eui-64
```

> 🔴 **DỰ ĐOÁN:** MAC của Gi0/1 là `00D0.BA12.3456`. Interface ID EUI-64 sẽ là gì?
> Tính tay **trước** khi xem `show ipv6 interface`.

**Quy trình EUI-64:**

```text
MAC:            00D0.BA12.3456
1. Chẻ đôi, chèn FFFE vào giữa:
                00D0.BA FF FE 12.3456
2. Lật bit thứ 7 của byte đầu (U/L bit):
   00 = 0000 0000 → lật bit 7 → 0000 0010 = 02
3. Interface ID:  02D0:BAFF:FE12:3456
→ Địa chỉ: 2001:db8:acad:99:02d0:baff:fe12:3456
```

| Bước | Kết quả của tôi |
|---|---|
| Chèn FFFE | |
| Lật U/L bit *(byte đầu)* | |
| Interface ID cuối | |

### Bước 3 — Solicited-node multicast

Với GUA `2001:db8:acad:10::1`:

```text
Solicited-node = ff02::1:ff + 24 bit cuối của địa chỉ
24 bit cuối của ::1 = 00:00:01
→ ff02::1:ff00:1
```

> 🔑 NDP *(thay ARP)* dùng solicited-node multicast để hỏi "ai có địa chỉ này" —
> thay vì broadcast như IPv4. Hiểu nó để đọc được LAB 41.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 interface brief
GigabitEthernet0/0.10  [up/up]
    FE80::1
    2001:DB8:ACAD:10::1
GigabitEthernet0/1     [up/up]
    FE80::2D0:BAFF:FE12:3456
    2001:DB8:ACAD:99:2D0:BAFF:FE12:3456      ← EUI-64 tự sinh
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ipv6 interface Gi0/0.10
  IPv6 is enabled, link-local address is FE80::1
  Joined group address(es):
    FF02::1          (all-nodes)
    FF02::2          (all-routers)
    FF02::1:FF00:1   (solicited-node của ::1)
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | Mỗi interface có **cả** GUA lẫn link-local | ✅ | |
| 2 | EUI-64 tính tay == IOS sinh | ✅ | |
| 3 | Thấy solicited-node trong joined groups | ✅ | |
| 4 | PC ping gateway `...::1` | ✅ | |
| 5 | PC ping PC khác VLAN | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Quên `ipv6 unicast-routing` ⭐

```cisco
R1(config)# no ipv6 unicast-routing
```

| | |
|---|---|
| PC khác VLAN còn ping được nhau không? | |
| Ping gateway *(cùng VLAN)* còn được không? | |
| Router có **forward** gói IPv6 giữa các interface không? | |
| Router có gửi **RA** cho SLAAC không *(ảnh hưởng LAB 41)*? | |

### Lỗi 2 — Dùng prefix khác /64 cho LAN

```cisco
R1(config)# interface Gi0/0.10
R1(config-subif)# ipv6 address 2001:db8:acad:10::1/80
```

| | |
|---|---|
| EUI-64 và SLAAC còn hoạt động không? | |
| Vì sao IPv6 LAN **gần như luôn** dùng /64? | |
| Interface ID cần đủ bao nhiêu bit? | |

### Lỗi 3 — Thiếu link-local

```text
Trên một interface chỉ gán GUA, xoá/không có link-local
(IOS thường tự sinh fe80 — thử gán GUA trước khi bật interface)
```

| | |
|---|---|
| Interface có tự sinh link-local không? | |
| Vì sao **mọi** interface IPv6 bắt buộc có link-local? | |
| NDP và OSPFv3 dùng địa chỉ nào để nói chuyện — GUA hay link-local? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Rút gọn: `2001:0db8:0000:0000:0000:ff00:0042:8329`. Và giãn lại `fe80::1`.
2. Vì sao IPv6 không cần NAT như IPv4? Điều này đổi cách quy hoạch thế nào?
3. GUA, ULA, link-local — mỗi loại dùng ở đâu? ULA giống gì trong IPv4?
4. Từ một `/48`, bạn có bao nhiêu `/64`? Vì sao con số đó "thoải mái vô hạn" so với IPv4?

<details>
<summary>Đáp án</summary>

**1.** Rút gọn `2001:0db8:0000:0000:0000:ff00:0042:8329`:
- Bỏ số 0 đầu mỗi nhóm: `2001:db8:0:0:0:ff00:42:8329`
- Thay chuỗi 0 dài nhất bằng `::`: **`2001:db8::ff00:42:8329`**

Giãn `fe80::1`:
- `::` = bù đủ 8 nhóm: `fe80:0000:0000:0000:0000:0000:0000:0001`

**2.** IPv6 có không gian khổng lồ *(2^128)* → **mỗi thiết bị một GUA thật**, không cần
chia sẻ IP → không cần NAT. Quy hoạch đổi hoàn toàn:
- Không "tiết kiệm IP" → mỗi LAN một /64 thoải mái *(không VLSM chi li như IPv4)*.
- Thiết kế theo **cấu trúc phân cấp** *(site/building/VLAN)* thay vì theo số host.
- End-to-end connectivity trở lại → bảo mật dựa vào **firewall**, không phải "NAT giấu".

**3.**

| Loại | Dải | Dùng ở đâu | Tương tự IPv4 |
|---|---|---|---|
| **GUA** | `2000::/3` | Định tuyến toàn cầu *(Internet)* | IP public |
| **ULA** | `fc00::/7` *(fd..)* | Nội bộ, không ra Internet | IP private `10/8`, `192.168` |
| **Link-local** | `fe80::/10` | Chỉ trong một link *(NDP, OSPFv3)* | APIPA `169.254` |

**4.** Từ `/48` → chia tới `/64` = `64-48 = 16 bit subnet` → **2^16 = 65.536** mạng /64.
Mỗi /64 chứa 2^64 ≈ **18 tỷ tỷ** địa chỉ host. So với IPv4 phải đếm từng host và lo cạn,
IPv6 cho bạn 65k mạng mỗi site, mỗi mạng nhiều hơn toàn bộ Internet IPv4 — nên quy hoạch
thiên về **gọn, dễ nhớ, phân cấp** thay vì tối ưu từng bit.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### EUI-64 — lời giải mẫu

```text
MAC 00D0.BA12.3456
→ chèn FFFE:   00D0:BAFF:FE12:3456
→ lật U/L bit: byte đầu 00 (0000 0000) → bit 7 lật → 0000 0010 = 02
→ Interface ID: 02D0:BAFF:FE12:3456
→ GUA đầy đủ:  2001:db8:acad:99:2d0:baff:fe12:3456
```

Mẹo kiểm tra U/L: nếu byte đầu MAC là số **chẵn** *(bit 7 = 0)*, sau khi lật thường
**+2**. `00→02`, `52→50`? Không — lật đúng bit 7: `00000000→00000010`. Luôn làm theo bit.

### Giải thích các lỗi BREAK

**Lỗi 1 — thiếu `ipv6 unicast-routing` ⭐:** Không có lệnh này, router chỉ là **host
IPv6** — ping cùng VLAN OK, nhưng **không forward** giữa các interface *(khác VLAN fail)*,
và **không gửi RA** → SLAAC của client chết. Đây là lệnh "bật router mode" của IPv6,
tương đương `ip routing` của IPv4 nhưng IPv6 **tắt mặc định**.

**Lỗi 2 — prefix khác /64:** EUI-64 và SLAAC **cần đúng 64 bit** interface ID. Với /80,
chỉ còn 48 bit cho interface ID → EUI-64 *(64 bit)* không vừa → SLAAC không chạy.
Vì thế LAN IPv6 **gần như luôn /64** — đây là ràng buộc thiết kế, không phải tuỳ chọn.

**Lỗi 3 — thiếu link-local:** IOS **tự sinh** link-local khi bật IPv6 trên interface
*(từ EUI-64 của MAC)* → gần như không thể thiếu. Link-local **bắt buộc** vì NDP
*(thay ARP)*, RA/RS, và **OSPFv3** đều dùng **link-local làm next-hop** — không phải GUA.
Một interface IPv6 không có link-local thì không nói chuyện được với hàng xóm.

### Bảng tổng kết

| Khái niệm | Điểm cốt lõi |
|---|---|
| `/64` cho LAN | EUI-64/SLAAC cần đúng 64 bit host |
| `ipv6 unicast-routing` | Bật router mode, mặc định TẮT |
| Link-local `fe80` | NDP/OSPFv3 next-hop; mọi interface bắt buộc có |
| Solicited-node | `ff02::1:ff` + 24 bit cuối — NDP dùng |
| GUA/ULA/LL | public / private / trong-link |

</details>

---

## 📝 Ghi chú & bài học rút ra

- EUI-64 tính tay của tôi có khớp IOS không? ___
- Lỗi 1 (unicast-routing) — tôi nhớ IPv6 tắt mặc định chưa? ___
- Vì sao LAN IPv6 luôn /64? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
