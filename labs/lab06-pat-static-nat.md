# LAB 06 — PAT ra Internet + static NAT cho server

| | |
|---|---|
| **Phase** | 0 |
| **Lesson liên quan** | [Lesson 09 — NAT · private vs public IP](../00-foundation/lesson-09-nat-private-public.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Cấu hình **PAT (NAT overload)** cho cả LAN ra Internet bằng **1 IP public**
- [ ] Đọc `show ip nat translations` và chỉ ra **port global khác nhau** giữa các máy
- [ ] Cấu hình **static NAT** cho server nội bộ → truy cập được từ ngoài
- [ ] Hiểu đúng thứ tự **inside/outside** và vai trò ACL
- [ ] Tự gây & sửa 3 lỗi NAT phổ biến

## 2. Prerequisite

- [Lesson 09](../00-foundation/lesson-09-nat-private-public.md) — NAT, PAT, inside/outside
- [LAB 04](lab04-ip-plan-doanh-nghiep.md) — IP plan
- ACL cơ bản *(hoặc xem trước [Lesson 36](../06-security/lesson-36-acl.md))*

---

## 3. Topology

```text
   LAN 10.0.0.0/24                      "Internet"
   PC1 10.0.0.10                        ISP 203.0.113.1
   PC2 10.0.0.11          ┌─────┐       Server ngoài 8.8.8.8
   SRV 10.0.0.80 ─────────┤ R1  ├──────────────
              (inside)    └─────┘   (outside)
                      Gi0/0        Gi0/1
                   10.0.0.1     203.0.113.2/30
                   ip nat inside  ip nat outside
```

## 4. IP Addressing Table

| Device | Interface | IP | Vai trò |
|---|---|---|---|
| R1 | Gi0/0 | `10.0.0.1/24` | `ip nat inside` |
| R1 | Gi0/1 | `203.0.113.2/30` | `ip nat outside` |
| PC1 | Fa0 | `10.0.0.10/24`, GW `10.0.0.1` | client |
| PC2 | Fa0 | `10.0.0.11/24`, GW `10.0.0.1` | client |
| SRV | Fa0 | `10.0.0.80/24`, GW `10.0.0.1` | web server nội bộ |
| ISP | Gi0/0 · Lo0 | `203.0.113.1/30` · `8.8.8.8/32` | "Internet" |

> 💡 ISP chỉ cần một static route về dải public `203.0.113.0/30` *(connected)* —
> **không** biết gì về `10.0.0.0/24`. Đó chính là lý do cần NAT.

---

## 5. Yêu cầu LAB

- [ ] PC1 và PC2 ping/truy cập được `8.8.8.8` qua **PAT**
- [ ] `show ip nat translations` cho thấy cả hai dùng chung `203.0.113.2` nhưng **khác port**
- [ ] Từ ISP, truy cập web SRV qua `203.0.113.3` *(static NAT)* hoặc `203.0.113.2:8080`
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Nền: định tuyến (chưa NAT)

```cisco
! ══ R1 ══
interface Gi0/0
 ip address 10.0.0.1 255.255.255.0
 no shutdown
interface Gi0/1
 ip address 203.0.113.2 255.255.255.252
 no shutdown
ip route 0.0.0.0 0.0.0.0 203.0.113.1

! ══ ISP ══
interface Gi0/0
 ip address 203.0.113.1 255.255.255.252
interface Loopback0
 ip address 8.8.8.8 255.255.255.255
```

> 🔴 **DỰ ĐOÁN:** PC1 ping `8.8.8.8` bây giờ *(chưa NAT)*. Được hay không?
> Gói **đi** tới được không? Gói **về** thì sao?

```text
Dự đoán: _______________
Lý do:   _______________
```

Thử thật → thường **fail**. Lý do ở phần Solution.

### Bước 2 — PAT (NAT overload)

```cisco
R1(config)# interface Gi0/0
R1(config-if)# ip nat inside
R1(config)# interface Gi0/1
R1(config-if)# ip nat outside

! ACL chọn traffic được NAT
R1(config)# access-list 1 permit 10.0.0.0 0.0.0.255

! Overload = PAT: nhiều IP private → 1 IP của interface outside
R1(config)# ip nat inside source list 1 interface Gi0/1 overload
```

Từ PC1 và PC2: ping `8.8.8.8`, hoặc mở `http://8.8.8.8`.

### Bước 3 — Quan sát bảng NAT ⭐

```cisco
R1# show ip nat translations
```

> 🔑 Cho PC1 **và** PC2 cùng truy cập `8.8.8.8` một lúc, rồi đọc bảng.
> Tìm cho ra: cả hai dùng chung `Inside global = 203.0.113.2`,
> nhưng **port khác nhau**. Đó chính là chữ **P** trong PAT —
> phân biệt phiên bằng **port**.

### Bước 4 — Static NAT cho server

Hai cách cho server nội bộ hiện ra Internet:

```cisco
! Cách A — Static NAT 1:1 (cần IP public riêng)
R1(config)# ip nat inside source static 10.0.0.80 203.0.113.3

! Cách B — Static PAT / port forwarding (tiết kiệm IP public)
R1(config)# ip nat inside source static tcp 10.0.0.80 80 203.0.113.2 8080
```

> ⚠️ Nếu dùng Cách A, nhớ ISP phải route `203.0.113.3` về R1 *(hoặc R1 làm proxy-arp)*.
> Trong lab, thêm `ip route 203.0.113.3 255.255.255.255 203.0.113.2` trên ISP.

Bật HTTP trên SRV *(Services → HTTP)*. Từ ISP:

```cisco
ISP> ... truy cập http://203.0.113.3      (Cách A)
ISP> ... truy cập http://203.0.113.2:8080 (Cách B)
```

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat translations
Pro  Inside global         Inside local       Outside local     Outside global
icmp 203.0.113.2:1         10.0.0.10:1        8.8.8.8:1         8.8.8.8:1
icmp 203.0.113.2:2         10.0.0.11:1        8.8.8.8:1         8.8.8.8:1
tcp  203.0.113.2:1024      10.0.0.10:49152    8.8.8.8:80        8.8.8.8:80
tcp  203.0.113.3:80        10.0.0.80:80       ---               ---
```

> 🔑 Đọc kỹ: hai dòng icmp đầu — **cùng `203.0.113.2`**, khác port `:1`/`:2`.
> Đó là PAT đang phân biệt PC1 và PC2 bằng port.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat statistics
Total active translations: 4 (1 static, 3 dynamic; 3 extended)
Outside interfaces: GigabitEthernet0/1
Inside interfaces:  GigabitEthernet0/0
Hits: 128  Misses: 4
Dynamic mappings:
-- Inside Source
access-list 1 interface GigabitEthernet0/1 refcount 3
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | PC1 ping `8.8.8.8` | ✅ | |
| 2 | PC2 ping `8.8.8.8` | ✅ | |
| 3 | Bảng NAT: PC1 & PC2 chung IP global, khác port | ✅ | |
| 4 | ISP → `http://203.0.113.3` *(hoặc :8080)* | ✅ | |
| 5 | `Hits` tăng khi có traffic | ✅ | |
| 6 | `show ip nat statistics` — 1 static + dynamic | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Thiếu `ip nat inside` ⭐

```cisco
R1(config)# interface Gi0/0
R1(config-if)# no ip nat inside
```

PC1 ping `8.8.8.8`.

| | |
|---|---|
| Ping được không? | |
| `show ip nat translations` — có entry mới không? | |
| `Hits` có tăng không? | |
| Vì sao NAT không chạy dù đã có lệnh `ip nat inside source`? | |

### Lỗi 2 — ACL sai dải

```cisco
R1(config)# no access-list 1
R1(config)# access-list 1 permit 10.0.99.0 0.0.0.255   ! dải KHÔNG tồn tại
```

| | |
|---|---|
| PC1 ping `8.8.8.8`: kết quả? | |
| `show ip nat translations`: có entry cho `10.0.0.10` không? | |
| Gói của PC1 có **khớp** ACL 1 không? Nên NAT có áp dụng? | |
| Không được NAT thì gói ra Internet mang IP gì → vì sao fail? | |

### Lỗi 3 — Bỏ `overload`, pool 1 IP

```cisco
R1(config)# no ip nat inside source list 1 interface Gi0/1 overload
R1(config)# ip nat pool P1 203.0.113.2 203.0.113.2 netmask 255.255.255.252
R1(config)# ip nat inside source list 1 pool P1
```

Cho PC1 và PC2 **cùng lúc** truy cập `8.8.8.8`.

| | |
|---|---|
| PC nào ra được, PC nào không? | |
| `show ip nat translations`: bao nhiêu entry? | |
| Vì sao chỉ 1 máy ra được tại một thời điểm? | |
| `overload` thêm điều gì mà pool-không-overload không có? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Hai PC cùng mở `https://8.8.8.8`. Bảng NAT có bao nhiêu entry? Khác nhau ở cột nào?
2. Vì sao `ip nat inside source list 1 pool PUBLIC` *(không overload)* với pool 1 IP
   chỉ cho **một** máy ra Internet tại một thời điểm?
3. Bạn cấu hình NAT đầy đủ nhưng `show ip nat translations` rỗng, `Hits: 0`.
   Nêu **3 nguyên nhân** theo thứ tự nên kiểm tra.
4. Vì sao nói "NAT không phải firewall"? Nêu một tình huống NAT **không** bảo vệ được.

<details>
<summary>Đáp án</summary>

**1.** Mỗi phiên HTTPS = **một** entry *(5-tuple riêng)*. Hai PC = **2 entry** TCP.
Chúng khác nhau ở:
- **Inside local** *(10.0.0.10 vs 10.0.0.11)* — IP thật
- **Inside global port** *(vd :1024 vs :1025)* — cùng IP public, **khác port**

Nếu một PC mở nhiều tab → mỗi kết nối TCP là một entry riêng nữa.

**2.** Không `overload` = NAT **1:1 động**: mỗi IP private chiếm **trọn** một IP public
trong pool, **không** dùng port để chia sẻ. Pool chỉ 1 IP → chỉ 1 máy được gán tại
một thời điểm. Máy thứ hai gặp pool cạn → gói bị drop *(hoặc chờ máy đầu nhả)*.

`overload` bổ sung **tầng port**: mọi máy dùng chung 1 IP, phân biệt bằng port nguồn →
một IP phục vụ hàng nghìn phiên.

**3.** Thứ tự kiểm tra:

```text
1. ip nat inside / outside có đúng interface chưa?
   → show ip nat statistics xem "Inside/Outside interfaces"
   (Lỗi phổ biến nhất: gán nhầm hoặc thiếu hẳn)

2. ACL có khớp dải nguồn không?
   → show access-lists 1 — đúng subnet LAN chưa?
   → Gói từ PC có match ACL không?

3. Có route ra ngoài không + route VỀ cho IP public?
   → PC phải tới được interface outside trước khi NAT xảy ra
   → ISP phải route IP public về R1 (với static NAT)
```

Nguyên tắc: **inside interface → outside interface → ACL match → có route**.
NAT chỉ xảy ra khi gói **đi từ** inside **ra** outside *(hoặc ngược lại với static)*.

**4.** NAT **ẩn** IP nội bộ và tạo trạng thái, nhưng:
- Nó **không lọc** traffic theo chính sách — chỉ dịch địa chỉ.
- Với PAT, kết nối **do nội bộ khởi tạo** vẫn mở đường về tự do → malware trên PC
  nội bộ gọi ra C2 server **không bị NAT chặn**.
- Static NAT / port forwarding **mở thẳng** cổng vào server nội bộ → ai cũng tới được.

Tình huống NAT không bảo vệ: PC nội bộ dính malware, tự kết nối ra `evil.com:443`.
NAT vui vẻ tạo entry và chuyển tiếp — vì **kết nối đi ra** luôn được phép.
Chỉ **firewall/IPS** mới chặn theo chính sách.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Bước 1 — vì sao chưa NAT thì fail

```text
PC1 gửi:  Src=10.0.0.10  Dst=8.8.8.8
→ R1 route ra Gi0/1, gói TỚI được ISP (ISP có route về 203.0.113.0/30)
→ ISP xử lý, gửi reply:  Src=8.8.8.8  Dst=10.0.0.10
→ ISP KHÔNG có route tới 10.0.0.0/24 (IP private, không định tuyến trên Internet)
→ reply bị DROP
```

Gói **đi** tới nơi, gói **về** lạc đường. Đây chính là vấn đề NAT sinh ra để giải quyết:
đổi `10.0.0.10` thành `203.0.113.2` để Internet biết đường trả lời.

### Giải thích các lỗi BREAK

**Lỗi 1 — thiếu `ip nat inside` ⭐:**

| Quan sát | Giải thích |
|---|---|
| Ping fail, bảng NAT rỗng, Hits không tăng | NAT **không được kích hoạt** trên luồng |
| Dù có `ip nat inside source` | Lệnh đó chỉ **định nghĩa quy tắc** — NAT chỉ chạy khi gói đi **từ interface `inside` sang `outside`** |

NAT cần **cả ba**: một interface `inside`, một interface `outside`, và một rule.
Thiếu nhãn interface = router không biết "chiều nào cần dịch".

**Lỗi 2 — ACL sai dải:**

| Quan sát | Giải thích |
|---|---|
| Ping fail, không entry cho `10.0.0.10` | Gói PC1 **không khớp** `access-list 1 permit 10.0.99.0` |
| Không khớp ACL → **không NAT** | Gói giữ nguyên `Src=10.0.0.10` ra Internet → reply lạc *(như Bước 1)* |

ACL trong NAT trả lời câu hỏi *"traffic nào được dịch?"*. Sai dải = đúng máy nhưng
không bao giờ được NAT.

**Lỗi 3 — bỏ overload:**

| Quan sát | Giải thích |
|---|---|
| Chỉ 1 PC ra được | Pool 1 IP, NAT 1:1 → IP public bị **một** máy chiếm trọn |
| Bảng NAT chỉ 1 entry dynamic | Máy thứ hai không có IP để gán |
| Thêm `overload` → cả hai ra được | Port cho phép chia sẻ cùng 1 IP |

👉 Đây là lý do mọi router gia đình/doanh nghiệp đều dùng **PAT (overload)** —
một IP public phục vụ cả LAN.

### Bảng tổng kết

| Thành phần | Vai trò | Thiếu/sai thì sao |
|---|---|---|
| `ip nat inside` | Đánh dấu chiều vào | NAT không kích hoạt |
| `ip nat outside` | Đánh dấu chiều ra | NAT không kích hoạt |
| `access-list` | Chọn traffic được dịch | Sai dải = không NAT |
| `overload` | Chia sẻ IP bằng port | Pool cạn, chỉ 1 máy ra |
| route 2 chiều | Gói đi & về tới nơi | Reply lạc đường |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Bảng NAT: PC1 và PC2 khác nhau ở cột nào? ___
- Lỗi 1 (thiếu nhãn interface) — tôi hiểu NAT cần đủ 3 thứ chưa? ___
- "NAT không phải firewall" — tình huống tôi tự nghĩ ra: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
