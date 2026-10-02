# LAB 32 — NAT nâng cao

> 📦 **LAB 06 đã dạy gì — lab này thêm gì:** LAB 06 làm PAT cơ bản + 1 static NAT.
> Lab này đi xa hơn: **port forwarding nhiều dịch vụ**, **dual-WAN NAT** *(route-map)*,
> và bẫy **NAT order vs VPN**.

| | |
|---|---|
| **Phase** | 3 |
| **Lesson liên quan** | [Lesson 27 — NAT nâng cao](../03-services/lesson-27-nat-nang-cao.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~3 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Port forward **nhiều dịch vụ** *(web :80, mail :25, SSH :2222)* trên 1 IP public
- [ ] Dual-WAN: NAT ra **đúng** IP tuỳ interface đi ra *(route-map)*
- [ ] Hiểu **thứ tự xử lý** NAT ↔ routing ↔ ACL ↔ VPN
- [ ] Debug bằng `show ip nat translations` + `debug ip nat`
- [ ] Tự gây & sửa 3 lỗi NAT nâng cao

## 2. Prerequisite

- [Lesson 27](../03-services/lesson-27-nat-nang-cao.md) — port forwarding, dual-WAN
- [LAB 06](lab06-pat-static-nat.md) — PAT + static NAT cơ bản
- [LAB 21](lab21-static-default-floating.md) — floating static *(cho failover)*

---

## 3. Topology

```text
                    ISP-A 203.0.113.1 (WAN1)
                   /
   LAN ── R1 ──────┤
   10.0.0.0/24     \
   WEB .80          ISP-B 198.51.100.1 (WAN2)
   MAIL .25
```

| Device | Interface | IP | Vai trò |
|---|---|---|---|
| R1 | Gi0/0 | `10.0.0.1/24` | inside |
| R1 | Gi0/1 | `203.0.113.2/30` | outside WAN1 |
| R1 | Gi0/2 | `198.51.100.2/30` | outside WAN2 |
| WEB | `10.0.0.80` | — | HTTP/HTTPS |
| MAIL | `10.0.0.25` | — | SMTP |

## 4. IP Addressing Table

| Device | IP | Dịch vụ |
|---|---|---|
| WEB | `10.0.0.80/24` | TCP 80, 443 |
| MAIL | `10.0.0.25/24` | TCP 25 |
| PC-SSH | `10.0.0.10/24` | đích SSH :2222 |
| ISP-A Lo0 | `8.8.8.8` | "Internet" A |
| ISP-B Lo0 | `9.9.9.9` | "Internet" B |

---

## 5. Yêu cầu LAB

- [ ] 3 port forward hoạt động từ ngoài qua `203.0.113.2`
- [ ] PAT cho LAN ra Internet
- [ ] Dual-WAN: traffic ra WAN2 được NAT bằng `198.51.100.2` *(không phải .113.2)*
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Nền + PAT cơ bản

```cisco
R1(config)# interface Gi0/0
R1(config-if)# ip nat inside
R1(config)# interface Gi0/1
R1(config-if)# ip nat outside
R1(config)# interface Gi0/2
R1(config-if)# ip nat outside

R1(config)# access-list 1 permit 10.0.0.0 0.0.0.255
R1(config)# ip nat inside source list 1 interface Gi0/1 overload
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

### Bước 2 — Port forwarding nhiều dịch vụ ⭐

```cisco
! Web
R1(config)# ip nat inside source static tcp 10.0.0.80 80  203.0.113.2 80
R1(config)# ip nat inside source static tcp 10.0.0.80 443 203.0.113.2 443
! Mail
R1(config)# ip nat inside source static tcp 10.0.0.25 25  203.0.113.2 25
! SSH tới PC nội bộ qua cổng lạ (ẩn cổng thật)
R1(config)# ip nat inside source static tcp 10.0.0.10 22  203.0.113.2 2222
```

> 🔑 Nhiều static PAT **cùng 1 IP public**, phân biệt bằng **port**. Từ ngoài:
> `:80`→WEB, `:25`→MAIL, `:2222`→PC-SSH:22. Một IP public phục vụ nhiều server.

### Bước 3 — Dual-WAN NAT bằng route-map ⭐

> 🔴 **DỰ ĐOÁN:** nếu chỉ có một dòng `... interface Gi0/1 overload`, khi traffic
> định tuyến ra **Gi0/2 (WAN2)**, nó được NAT bằng IP nào? Có ra ngoài được không?

Vấn đề: `ip nat ... interface Gi0/1` chỉ NAT khi ra Gi0/1. Ra Gi0/2 → không match →
gói mang IP private → chết. Giải pháp **route-map** gắn NAT theo interface ra:

```cisco
R1(config)# route-map WAN1 permit 10
R1(config-route-map)# match ip address 1
R1(config-route-map)# match interface Gi0/1
R1(config)# route-map WAN2 permit 10
R1(config-route-map)# match ip address 1
R1(config-route-map)# match interface Gi0/2

R1(config)# ip nat inside source route-map WAN1 interface Gi0/1 overload
R1(config)# ip nat inside source route-map WAN2 interface Gi0/2 overload
```

> 🔑 Giờ gói ra Gi0/1 được NAT thành `203.0.113.2`, ra Gi0/2 thành `198.51.100.2`.
> **Đúng IP theo đúng đường ra** — bắt buộc khi dual-WAN.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat translations
Pro  Inside global        Inside local      Outside local   Outside global
tcp  203.0.113.2:80       10.0.0.80:80      ---             ---
tcp  203.0.113.2:443      10.0.0.80:443     ---             ---
tcp  203.0.113.2:25       10.0.0.25:25      ---             ---
tcp  203.0.113.2:2222     10.0.0.10:22      ---             ---
tcp  203.0.113.2:1024     10.0.0.10:49800   8.8.8.8:80      8.8.8.8:80
```

```text
# output điển hình — debug thấy quá trình dịch
R1# debug ip nat
NAT*: s=10.0.0.10->203.0.113.2, d=8.8.8.8 [1]
NAT*: s=8.8.8.8, d=203.0.113.2->10.0.0.10 [1]
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | Ngoài → `203.0.113.2:80` → WEB | ✅ | |
| 2 | Ngoài → `203.0.113.2:2222` → PC-SSH:22 | ✅ | |
| 3 | LAN ra Internet qua WAN1 | ✅ `203.0.113.2` | |
| 4 | Traffic định tuyến ra WAN2 → NAT `198.51.100.2` | ✅ | |
| 5 | 4 static PAT trong bảng, cùng IP khác port | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Dual-WAN không có route-map ⭐

```cisco
R1(config)# no ip nat inside source route-map WAN2 interface Gi0/2 overload
! Buộc traffic ra WAN2 (vd đổi default route sang Gi0/2)
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1
```

| | |
|---|---|
| LAN ping `9.9.9.9` qua WAN2: được không? | |
| `debug ip nat` có thấy dịch không? | |
| Gói ra Gi0/2 mang IP gì → vì sao ISP-B drop reply? | |
| Vì sao `... interface Gi0/1` không giúp traffic ra Gi0/2? | |

### Lỗi 2 — Hai static PAT trùng port

```cisco
R1(config)# ip nat inside source static tcp 10.0.0.25 80 203.0.113.2 80
! đã có WEB :80 → 10.0.0.80
```

| | |
|---|---|
| IOS nhận lệnh không, hay báo lỗi? | |
| Từ ngoài gõ `:80` → vào WEB hay MAIL? | |
| Một (IP public, port) ánh xạ được mấy đích? | |

### Lỗi 3 — ACL NAT trùng dải port-forward

```cisco
! ACL 1 permit cả 10.0.0.80 → static NAT và dynamic PAT "đánh nhau"
! Quan sát: WEB vừa có static map vừa match ACL dynamic
```

| | |
|---|---|
| WEB khởi tạo kết nối RA Internet: dùng bản dịch nào? | |
| Static NAT và dynamic PAT, cái nào ưu tiên cho `10.0.0.80`? | |
| Có nên exclude server khỏi ACL dynamic không? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Vẽ **thứ tự xử lý** một gói đi từ inside ra outside: routing, NAT, ACL theo thứ tự nào?
   Và gói từ outside vào inside?
2. Bạn có VPN site-to-site **và** NAT ra Internet trên cùng router. Làm sao để traffic
   đi VPN **không** bị NAT?
3. Dual-WAN active/active vs active/backup khác nhau thế nào về NAT?
4. Từ ngoài không vào được `:2222` dù cấu hình đúng. Nêu 3 nguyên nhân cần kiểm tra.

<details>
<summary>Đáp án</summary>

**1.** Thứ tự xử lý *(quan trọng cho mọi bài NAT)*:

```text
INSIDE → OUTSIDE:
  1. ACL inbound (trên interface inside)
  2. Routing (quyết định interface ra)
  3. NAT inside-to-outside (dịch source)
  4. ACL outbound (trên interface outside)

OUTSIDE → INSIDE:
  1. ACL inbound (trên interface outside)   ← ACL thấy IP PUBLIC
  2. NAT outside-to-inside (dịch dest về IP private)
  3. Routing
  4. ACL outbound (trên interface inside)
```

Điểm bẫy *(như LAB 61)*: ACL inbound trên WAN chạy **trước** NAT → phải khớp **IP public**.

**2.** Dùng **ACL deny** để loại traffic VPN khỏi NAT:

```cisco
! Giả sử LAN 10.0.0.0/24, remote site 10.1.0.0/24 qua VPN
ip access-list extended NAT-LIST
 deny   ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255   ! VPN traffic: KHÔNG NAT
 permit ip 10.0.0.0 0.0.0.255 any                   ! còn lại: NAT ra Internet
!
ip nat inside source list NAT-LIST interface Gi0/1 overload
```

Nguyên lý: traffic tới remote site **match deny** → không NAT → đi vào tunnel với
IP private thật *(VPN cần IP private hai đầu để định tuyến)*. Nếu NAT nó, hai site
không thấy nhau. Đây là lỗi "VPN up nhưng không ping được" kinh điển.

**3.**

| | Active/Active | Active/Backup |
|---|---|---|
| NAT | Cần **route-map 2 chiều** *(mỗi WAN một IP)* | Chủ yếu 1 WAN; khi failover đổi sang IP WAN kia |
| Cấu hình | Phức tạp, cân bằng tải | Đơn giản hơn, dùng floating static/IP SLA |
| Phiên đang chạy | Chia theo đường | Khi chuyển WAN, **phiên NAT cũ chết** *(IP đổi)* |

Lưu ý: khi failover sang WAN khác, **IP public đổi** → mọi kết nối TCP đang mở **đứt**
*(vì inside global thay đổi)*. Không tránh được trừ khi có BGP + IP riêng.

**4.** Ba nguyên nhân `:2222` không vào:

```text
1. Static PAT sai: show ip nat translations — có dòng 203.0.113.2:2222 → 10.0.0.10:22?
2. ACL inbound trên WAN chặn: có permit tcp any host 203.0.113.2 eq 2222 chưa?
   (nhớ: ACL khớp IP PUBLIC + port PUBLIC 2222)
3. PC-SSH không chạy SSH / sai gateway: PC có mở :22? gateway trỏ về R1?
```

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — dual-WAN thiếu route-map ⭐:** `ip nat ... interface Gi0/1` chỉ dịch khi gói
ra **Gi0/1**. Khi default route đẩy traffic ra **Gi0/2**, gói **không match** rule nào →
giữ nguyên `10.0.0.x` → ISP-B nhận gói IP private → **drop reply** *(không route được
IP private)*. `debug ip nat` **không thấy** dịch. Phải dùng **route-map match interface**
để mỗi đường ra có NAT riêng.

**Lỗi 2 — trùng port:** Một cặp `(IP public, port)` chỉ ánh xạ tới **một** đích.
IOS **từ chối** map thứ hai `203.0.113.2:80` *(đã dùng cho WEB)* hoặc ghi đè gây lỗi.
Muốn cả WEB và MAIL cùng :80 ra ngoài → cần **IP public thứ hai** hoặc **port khác**.

**Lỗi 3 — static vs dynamic:** Với `10.0.0.80`, **static NAT luôn thắng** dynamic PAT.
Khi WEB chủ động ra Internet, nó dùng bản dịch static `203.0.113.2:80` *(IP public cố
định)* thay vì PAT động. Thường **nên** exclude server khỏi ACL dynamic để tránh nhầm
lẫn và giữ IP ra ngoài ổn định.

### Thứ tự xử lý — ghi nhớ

```text
inside→outside:  ACL-in → route → NAT → ACL-out
outside→inside:  ACL-in (IP public!) → NAT → route → ACL-out
VPN + NAT:       deny VPN-traffic trong ACL NAT → không dịch
```

### Bảng tổng kết

| Kỹ thuật | Lệnh then chốt | Dùng khi |
|---|---|---|
| Port forward đa dịch vụ | nhiều `static tcp ... port` | 1 IP public, nhiều server |
| Dual-WAN NAT | `route-map match interface` | 2 đường Internet |
| VPN không NAT | `deny` trong ACL NAT | có VPN + Internet chung router |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Thứ tự NAT/route/ACL tôi vẽ lại được chưa? ___
- Lỗi 1 (dual-WAN) — vì sao cần route-map? ___
- "VPN không NAT" — tôi hiểu vì sao deny chứ không permit? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
