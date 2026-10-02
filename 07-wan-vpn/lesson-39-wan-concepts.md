# LESSON 39 — WAN Concepts · Dual-WAN & Failover

| | |
|---|---|
| **Phase** | 7 — WAN / Enterprise |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 19](../02-routing/lesson-19-static-default-route.md), [Lesson 27](../03-services/lesson-27-nat-nang-cao.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Phân biệt các loại kết nối WAN: leased line · MPLS · Internet VPN · broadband
- [ ] Hiểu các thuật ngữ **CE · PE · CPE · demarc · last mile**
- [ ] Đọc được **SLA** của nhà cung cấp và biết con số nào quan trọng
- [ ] Thiết kế dual-WAN với failover **thật sự hoạt động**
- [ ] Giải thích vì sao floating static **không đủ** và cần IP SLA + track

## 2. Prerequisite

- Static route, floating static *(Lesson 19)*
- NAT cho dual-WAN *(Lesson 27)*
- AD và cách route được chọn *(Lesson 20)*

---

## 3. Concept

### Các loại kết nối WAN

| Loại | Băng thông | SLA | Chi phí | Dùng khi |
|---|---|---|---|---|
| **Leased line** *(kênh riêng)* | Cố định, đối xứng | ✅ **Cao nhất** | 💰💰💰 | Kết nối trọng yếu, ngân hàng |
| **MPLS L3VPN** | Cố định | ✅ Cao | 💰💰💰 | Nhiều chi nhánh, cần QoS end-to-end |
| **Metro Ethernet** | 10M–10G | ✅ Cao | 💰💰 | Trong cùng thành phố |
| **Internet + VPN** | Biến động | ⚠️ Thấp | 💰 | ⭐ Phổ biến nhất hiện nay |
| **Broadband** *(FTTH, cáp quang dân dụng)* | **Bất đối xứng** | ❌ Best effort | 💰 | Chi nhánh nhỏ, backup |
| **4G/5G** | Biến động | ❌ | 💰 | Backup, trạm di động |

> 🏭 Xu hướng thực tế: **MPLS đang bị thay dần bằng Internet + VPN/SD-WAN** —
> rẻ hơn nhiều lần, băng thông cao hơn, đổi lại SLA kém hơn.
> Thiết kế hiện đại: **2 đường Internet từ 2 ISP khác nhau + SD-WAN**.

### Thuật ngữ — vẽ ra là hiểu

```text
       MẠNG CỦA BẠN          │  NHÀ CUNG CẤP
                              │
   LAN ── [CE/CPE] ── demarc ─┼─ last mile ── [PE] ── MPLS/Internet core
          router của bạn      │              router của ISP
                         ranh giới
                      trách nhiệm
```

| Thuật ngữ | Nghĩa |
|---|---|
| **CPE** *(Customer Premises Equipment)* | Thiết bị **đặt tại chỗ bạn** — router, modem |
| **CE** *(Customer Edge)* | **Router của bạn** nối ra ISP |
| **PE** *(Provider Edge)* | **Router của ISP** nối tới bạn |
| **Demarcation point** *(demarc)* | **Ranh giới trách nhiệm** — bên này là bạn, bên kia là ISP |
| **Last mile** | Đoạn từ ISP tới chỗ bạn — thường là chỗ hỏng nhiều nhất |

> 🔧 **Demarc rất quan trọng khi báo sự cố.** Lỗi trước demarc = ISP chịu trách nhiệm;
> sau demarc = bạn. Luôn biết demarc nằm ở đâu *(thường là ODF/patch panel trong tủ mạng)*.

### MPLS — hiểu ở mức CCNA

**MPLS** chuyển gói theo **nhãn (label)** thay vì tra bảng định tuyến ở mỗi hop.

| Mô hình | Ai quản lý routing | Đặc điểm |
|---|---|---|
| **L3VPN** | **ISP** tham gia routing với bạn | Bạn chỉ cần peering với PE; ISP lo phần còn lại |
| **L2VPN** *(VPLS, pseudowire)* | **Bạn** tự lo | ISP chỉ chở frame — như một sợi dây dài |

> 💡 Ở CCNA chỉ cần biết: **MPLS L3VPN = ISP tham gia định tuyến với bạn**,
> thường chạy BGP hoặc OSPF giữa CE và PE. Chi tiết ở CCNP/CCIE.

### SLA — đọc hợp đồng

| Chỉ số | Nghĩa | Con số thực tế |
|---|---|---|
| **Uptime** | % thời gian hoạt động | 99.5% = **44 giờ** mất/năm<br>99.9% = **8.8 giờ**<br>99.99% = **53 phút** |
| **Latency** | Độ trễ cam kết | Trong nước < 30 ms |
| **Packet loss** | Mất gói | < 0.1% |
| **Jitter** | Biến thiên độ trễ | < 20 ms *(quan trọng cho VoIP)* |
| **MTTR** | **Thời gian khắc phục** trung bình | ⭐ 4 giờ · 8 giờ · NBD |

> ⭐ **MTTR quan trọng hơn uptime.** Uptime 99.9% nghe hay, nhưng nếu MTTR là
> "ngày làm việc tiếp theo" thì một sự cố chiều thứ Sáu = **mất mạng tới thứ Hai**.
>
> Khi đọc hợp đồng, hỏi: *"đứt lúc 2 giờ sáng Chủ nhật thì bao lâu có người tới?"*

### Dual-WAN — ba mô hình

| Mô hình | Cách hoạt động | Ưu / Nhược |
|---|---|---|
| **Active/Standby** | WAN1 chạy, WAN2 chờ | ✅ Đơn giản · ❌ Phí một đường |
| **Active/Active** *(load sharing)* | Cả hai cùng chạy | ✅ Tận dụng · ❌ Phức tạp với NAT/firewall stateful |
| **Policy-based** | Traffic A đi WAN1, traffic B đi WAN2 | ✅ Linh hoạt · ❌ Cấu hình phức tạp |

> 🏭 Thực tế phổ biến: **Active/Standby** cho mạng vừa và nhỏ *(đơn giản, dễ debug)*;
> **SD-WAN** cho mạng lớn *(tự động chọn đường theo chất lượng từng ứng dụng)*.

### Vì sao floating static KHÔNG đủ

```text
ip route 0.0.0.0 0.0.0.0 203.0.113.1          ! WAN1, AD 1
ip route 0.0.0.0 0.0.0.0 198.51.100.1 200     ! WAN2, AD 200
```

| Tình huống | Floating static có phát hiện không? |
|---|:---:|
| Cáp bị rút → interface down | ✅ **Có** |
| Router ISP chết → cáp vẫn up | ❌ **KHÔNG** |
| Upstream của ISP đứt | ❌ **KHÔNG** |
| ISP hoạt động nhưng mất gói 50% | ❌ **KHÔNG** |

> ⭐ **Floating static chỉ biết interface local down.** Trong 4 tình huống trên,
> **3 cái nó mù hoàn toàn** — traffic vẫn đi vào ngõ cụt.
>
> Đây là lý do cần **IP SLA + track**.

### IP SLA + Track — failover thật

```text
1. Router PING liên tục một IP bên ngoài qua WAN1 (vd 8.8.8.8)
2. Gắn một "track object" vào kết quả ping
3. Static route chỉ TỒN TẠI khi track object UP
4. Ping fail liên tục → track DOWN → route bị gỡ
5. → Floating static của WAN2 vào bảng → traffic chuyển
```

```cisco
! Định nghĩa phép đo
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
 frequency 5                        ! ping mỗi 5 giây
ip sla schedule 1 life forever start-time now

! Gắn track vào phép đo
track 1 ip sla 1 reachability

! Route chỉ sống khi track UP
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 1
ip route 0.0.0.0 0.0.0.0 198.51.100.1 200
```

> 🔑 Từ khoá **`track 1`** ở cuối dòng route là toàn bộ sự khác biệt.
> Không có nó, route sống mãi cho tới khi interface down.

> ⚠️ Chọn IP đích để ping cẩn thận: **đừng ping gateway của ISP** *(nó luôn sống
> dù upstream đứt)*. Ping một IP **ngoài Internet** như `8.8.8.8` hoặc `1.1.1.1`.
> Tốt nhất: ping **2 đích khác nhau** và dùng `track ... list boolean or`.

---

## 4. Why?

> **Vì sao không dùng một đường Internet thật khoẻ thay vì hai đường?**

| Rủi ro của một đường | Hai đường giải quyết |
|---|---|
| ISP gặp sự cố → **mất mạng hoàn toàn** | Còn đường kia |
| Đứt cáp quang biển *(rất hay xảy ra ở VN)* | ISP khác có thể đi hướng khác |
| Bảo trì theo lịch của ISP | Chuyển sang đường còn lại |

> ⚠️ **Quan trọng: hai đường phải từ HAI ISP KHÁC NHAU**, và lý tưởng là đi
> **hai hướng cáp vật lý khác nhau**. Hai đường từ cùng một ISP, cùng một sợi cáp
> vào toà nhà → **đứt cùng lúc**.

> 🔧 Câu hỏi nên hỏi nhà cung cấp: *"đường của các anh đi theo tuyến cáp nào?"*
> Nếu cả hai ISP đều thuê chung một tuyến, bạn **không có dự phòng thật**.

---

## 5. How does it work? — failover từng bước

```text
Trạng thái bình thường:
  IP SLA 1 ping 8.8.8.8 qua WAN1 → OK mỗi 5 giây
  track 1 → UP
  show ip route: S* 0.0.0.0/0 [1/0] via 203.0.113.1

ISP1 gặp sự cố (cáp vẫn up):
  T+0s    Ping bắt đầu fail
  T+5s    Fail lần 2
  T+10s   Fail lần 3 → track 1 chuyển DOWN
  T+10s   Route AD 1 bị GỠ khỏi bảng
  T+10s   Route AD 200 (WAN2) VÀO bảng
  T+10s   clear ip nat translation (nếu có EEM script)
  → Traffic chuyển sang WAN2

ISP1 hồi phục:
  Ping OK → track UP → route AD 1 quay lại → traffic về WAN1
```

> ⚠️ Bước `clear ip nat translation` rất quan trọng *(đã học ở [Lesson 27](../03-services/lesson-27-nat-nang-cao.md))* —
> các kết nối đang mở vẫn mang entry NAT với IP của WAN1 đã chết.
> Tự động hoá bằng **EEM script**:

```cisco
event manager applet WAN-FAILOVER
 event track 1 state down
 action 1.0 cli command "enable"
 action 2.0 cli command "clear ip nat translation *"
 action 3.0 syslog msg "WAN1 DOWN - da chuyen sang WAN2, da clear NAT"
```

---

## 6. Packet Flow — không áp dụng

Lesson này về **thiết kế và dịch vụ**, không về xử lý gói cụ thể.

Thay vào đó, bảng tham chiếu nhanh:

| Loại WAN | Thiết bị đầu cuối tại chỗ bạn | Giao thức hay dùng với ISP |
|---|---|---|
| Leased line / Metro-E | Router *(Ethernet handoff)* | Static route, hoặc BGP |
| MPLS L3VPN | Router CE | **BGP** *(phổ biến)*, OSPF, static |
| Internet FTTH | Modem/ONT + router | **PPPoE** hoặc DHCP |
| 4G/5G | Router có SIM | DHCP |

---

## 7. Real-world Example

🏭 **Thiết kế WAN cho doanh nghiệp 3 site**

```text
                    ┌─── Trụ sở Hà Nội ───┐
                    │  WAN1: FTTH ISP-A    │
                    │  WAN2: FTTH ISP-B    │
                    │  (IP SLA + track)    │
                    └──────────┬───────────┘
                               │ VPN site-to-site qua Internet
              ┌────────────────┼────────────────┐
     ┌────────┴────────┐              ┌─────────┴────────┐
     │ Chi nhánh SG     │              │ Chi nhánh ĐN     │
     │ WAN1: FTTH       │              │ WAN1: FTTH       │
     │ WAN2: 4G backup  │              │ WAN2: 4G backup  │
     └──────────────────┘              └──────────────────┘
```

| Quyết định | Vì sao |
|---|---|
| Trụ sở 2 FTTH từ **2 ISP khác nhau** | Chống sự cố một nhà cung cấp |
| Chi nhánh dùng **4G làm backup** | Rẻ, không phụ thuộc hạ tầng cáp cùng tuyến |
| VPN qua Internet thay vì MPLS | Chi phí thấp hơn nhiều lần |
| IP SLA + track ở mọi site | Failover thật, không chỉ khi rút cáp |

🏭 **Sự cố: "có 2 đường mà vẫn mất mạng"**

```text
Công ty mua 2 đường từ CÙNG một ISP để "tiết kiệm"
→ Cả hai đi chung một sợi cáp vào toà nhà
→ Thợ đào đường cắt cáp
→ MẤT CẢ HAI ĐƯỜNG CÙNG LÚC
```

> 🔧 Bài học: **dự phòng phải độc lập ở mọi tầng** — khác ISP, khác tuyến cáp,
> khác thiết bị, khác nguồn điện. Dự phòng mà chung một điểm hỏng thì không phải dự phòng.

🏭 **Sự cố: failover không hoạt động khi cần nhất**

```text
Cấu hình chỉ có floating static.
ISP1 bị lỗi định tuyến upstream — cáp vẫn up, interface vẫn up.
→ Route AD 1 VẪN NẰM TRONG BẢNG
→ Toàn bộ traffic đi vào ngõ cụt
→ "Có backup mà không chuyển"
```

Sửa: thêm IP SLA + track như mục 3.

🏭 **Đọc SLA — câu hỏi nên hỏi nhà cung cấp**

| Câu hỏi | Vì sao quan trọng |
|---|---|
| **MTTR là bao lâu?** Kể cả ngoài giờ, cuối tuần? | Quan trọng hơn uptime |
| Đường của các anh đi tuyến cáp nào? | Kiểm tra dự phòng có thật không |
| Có cam kết băng thông hay chỉ "tối đa"? | FTTH dân dụng thường là "up to" |
| Băng thông **đối xứng** hay bất đối xứng? | Upload thấp làm chết VPN và video call |
| Có IP tĩnh không? | Cần cho VPN site-to-site và server |

---

## 8. Cisco CLI

```cisco
! ═══════ IP SLA — PHÉP ĐO ═══════
R1(config)# ip sla 1
R1(config-ip-sla)# icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
R1(config-ip-sla-echo)# frequency 5          ! ping mỗi 5 giây
R1(config-ip-sla-echo)# threshold 1000       ! ms — vượt là coi như kém
R1(config-ip-sla-echo)# timeout 2000
R1(config)# ip sla schedule 1 life forever start-time now

! Đo thêm một đích thứ hai (tránh phụ thuộc một IP)
R1(config)# ip sla 2
R1(config-ip-sla)# icmp-echo 1.1.1.1 source-interface GigabitEthernet0/1
R1(config-ip-sla-echo)# frequency 5
R1(config)# ip sla schedule 2 life forever start-time now

! ═══════ TRACK ═══════
R1(config)# track 1 ip sla 1 reachability
R1(config)# track 2 ip sla 2 reachability

! Kết hợp: UP nếu MỘT TRONG HAI còn sống
R1(config)# track 10 list boolean or
R1(config-track)# object 1
R1(config-track)# object 2
R1(config-track)# delay down 10 up 30        ! chống nhấp nháy

! ═══════ ROUTE GẮN TRACK ═══════
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 10
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 200

! ═══════ EEM — tự động clear NAT khi failover ═══════
R1(config)# event manager applet WAN-FAILOVER
R1(config-applet)# event track 10 state down
R1(config-applet)# action 1.0 cli command "enable"
R1(config-applet)# action 2.0 cli command "clear ip nat translation *"
R1(config-applet)# action 3.0 syslog msg "WAN1 DOWN - chuyen sang WAN2"

! ═══════ PPPoE (FTTH dân dụng) ═══════
R1(config)# interface GigabitEthernet0/1
R1(config-if)# pppoe enable group global
R1(config-if)# pppoe-client dial-pool-number 1
R1(config)# interface Dialer1
R1(config-if)# ip address negotiated
R1(config-if)# ip mtu 1492                   ! ⚠️ PPPoE giảm MTU
R1(config-if)# encapsulation ppp
R1(config-if)# dialer pool 1
R1(config-if)# ppp authentication chap callin
R1(config-if)# ppp chap hostname <user>
R1(config-if)# ppp chap password <pass>
R1(config-if)# ip tcp adjust-mss 1452        ! ⚠️ RẤT QUAN TRỌNG

! ═══════ KIỂM TRA ═══════
R1# show ip sla statistics
R1# show ip sla summary
R1# show track
R1# show ip route | include 0.0.0.0
R1# show pppoe session
```

| Lệnh | Lưu ý |
|---|---|
| `ip sla schedule 1 life forever start-time now` | ⚠️ **Thiếu dòng này IP SLA không chạy** |
| `track N ip sla N reachability` | Gắn track vào phép đo |
| `delay down 10 up 30` | Chống nhấp nháy — chờ 10s mới báo down, 30s mới báo up |
| `ip route ... track N` | ⭐ Từ khoá làm nên tất cả |
| `ip mtu 1492` + `ip tcp adjust-mss 1452` | ⭐ **Bắt buộc với PPPoE** |

> ⚠️ **PPPoE giảm MTU từ 1500 xuống 1492** *(8 byte header PPPoE)*. Không chỉnh MSS →
> gói lớn bị drop im lặng → triệu chứng **"ping được, web nhỏ được, web có ảnh thì treo"**
> *(giống lỗi PMTUD ở [Lesson 30](../04-ipv6/lesson-30-slaac-ndp-dhcpv6.md))*.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip sla statistics
IPSLAs Latest Operation Statistics

IPSLA operation id: 1
        Latest RTT: 18 milliseconds
Latest operation start time: 14:23:51 ICT Thu Oct 2 2026
Latest operation return code: OK
Number of successes: 1842
Number of failures: 3
Operation time to live: Forever
```

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `return code: OK` | Ping thành công ✅ | `Timeout` → đường có vấn đề |
| `Latest RTT` | Độ trễ hiện tại | Tăng đột ngột → đường kém |
| `Number of failures` | Số lần fail | Tăng dần → đường chập chờn |

```text
# output điển hình — tự verify trên lab của bạn
R1# show track
Track 10
  List boolean or
  Boolean OR is Up
    1 changes, last change 02:14:33
  object 1 Up
  object 2 Up
  Tracked by:
    STATIC-IP-ROUTING 0
```

| Field | Ý nghĩa |
|---|---|
| `Boolean OR is Up` | Ít nhất một object còn sống ✅ |
| `1 changes, last change 02:14:33` | Đã chuyển trạng thái 1 lần, cách đây 2 giờ |
| `Tracked by: STATIC-IP-ROUTING` | Route đang dùng track này |

```text
# output điển hình — khi WAN1 bình thường
R1# show ip route | include 0.0.0.0
S*    0.0.0.0/0 [1/0] via 203.0.113.1

# output điển hình — sau khi track DOWN
R1# show ip route | include 0.0.0.0
S*    0.0.0.0/0 [200/0] via 198.51.100.1      ← đã chuyển sang backup
```

> 🔑 Nhìn con số **AD trong `[200/0]`** là biết ngay đang chạy đường backup.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| **"Có backup mà không chuyển"** | Chỉ có floating static, interface vẫn up | `show ip route \| include 0.0.0.0` | Thêm **IP SLA + track** |
| IP SLA không chạy | Thiếu `ip sla schedule` | `show ip sla summary` | Thêm dòng schedule |
| Track luôn DOWN | Đích ping không reachable, hoặc sai source interface | `show ip sla statistics` | Kiểm tra đích, source |
| Track nhấp nháy liên tục | Đường chập chờn, chưa có delay | `show track` xem số `changes` | `delay down 10 up 30` |
| Failover xong vẫn mất mạng vài phút | Entry NAT cũ còn IP WAN chết | `show ip nat translations` | EEM `clear ip nat translation *` |
| Chuyển sang WAN2 nhưng không ra được | NAT chưa cấu hình cho WAN2 | `show ip nat statistics` | Route-map cho từng WAN *(Lesson 27)* |
| PPPoE: ping được nhưng web treo | **MTU/MSS** | `ping <ip> size 1500 df-bit` | `ip mtu 1492` + `ip tcp adjust-mss 1452` |
| Mất cả hai đường cùng lúc | Chung tuyến cáp / chung ISP | Hỏi nhà cung cấp | Đổi một đường sang ISP khác |
| Failover hoạt động nhưng VPN đứt | VPN peer gắn với IP WAN1 | `show crypto isakmp sa` | Cấu hình VPN cho cả 2 WAN *(Lesson 40)* |

---

## 11. LAB

🧪 **LAB 70 — Dual-WAN với IP SLA + track** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- 1 router với 2 interface WAN nối 2 "ISP" giả lập, mỗi ISP nối tới một "Internet server"
- Cấu hình floating static → `shutdown` WAN1 → quan sát chuyển sang WAN2
- **Chứng minh giới hạn**: giữ interface WAN1 **up** nhưng `shutdown` interface phía ISP1
  → quan sát route **không chuyển** → traffic vào ngõ cụt
- Thêm **IP SLA + track** → lặp lại thử nghiệm → chứng minh giờ đã chuyển đúng
- **BREAK bắt buộc:** (1) quên `ip sla schedule` → SLA không chạy;
  (2) ping gateway ISP thay vì IP ngoài Internet → track vẫn UP dù upstream đứt;
  (3) failover xong không clear NAT → kết nối cũ chết

## 12. Challenge

1. Công ty mua 2 đường Internet "để có dự phòng" nhưng vẫn mất mạng hoàn toàn khi
   thợ đào đường cắt cáp. Nêu 2 nguyên nhân có thể.
2. Floating static đã cấu hình đúng, nhưng khi ISP1 lỗi định tuyến upstream
   (cáp vẫn up) thì không chuyển đường. Vì sao? Sửa thế nào?
3. Bạn cấu hình IP SLA ping gateway của ISP1 (`203.0.113.1`). Có vấn đề gì?
4. SLA của ISP ghi "uptime 99.9%". Bạn nên hỏi thêm gì trước khi ký?

<details>
<summary>Đáp án</summary>

**1.** Hai nguyên nhân:

| # | Nguyên nhân | Chi tiết |
|:---:|---|---|
| **1** | **Hai đường từ cùng một ISP** | Dù là 2 hợp đồng riêng, chúng có thể đi chung hạ tầng |
| **2** | **Hai ISP khác nhau nhưng chung tuyến cáp** vào toà nhà | ISP nhỏ thường thuê lại hạ tầng của ISP lớn |

👉 Dự phòng phải **độc lập ở mọi tầng**: khác ISP, khác tuyến cáp vật lý,
khác thiết bị, khác nguồn điện. Hỏi nhà cung cấp *"đường của các anh đi tuyến nào"*
trước khi ký.

**2.** Vì **floating static chỉ phản ứng khi interface local down**.

```text
ISP1 lỗi upstream → cáp giữa bạn và ISP1 VẪN UP
→ interface Gi0/1 vẫn up/up
→ route AD 1 VẪN NẰM TRONG BẢNG
→ traffic vẫn đi WAN1 → vào ngõ cụt
```

Sửa: thêm **IP SLA + track**:

```cisco
ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/1
 frequency 5
ip sla schedule 1 life forever start-time now
track 1 ip sla 1 reachability
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 1
```

**3.** Vấn đề: **gateway của ISP gần như luôn sống**, kể cả khi upstream của họ đứt.

```text
Bạn ──── [PE của ISP1] ──── X đứt ở đây ──── Internet
         ping tới đây       │
         VẪN OK ✅          │
                     nhưng không ra được Internet ❌
```

→ Track vẫn UP → route không chuyển → **thất bại đúng lúc cần nhất**.

Sửa: ping một IP **ngoài Internet** (`8.8.8.8`, `1.1.1.1`), và tốt nhất là **2 đích**
kết hợp bằng `track ... list boolean or` để tránh phụ thuộc một dịch vụ.

**4.** Các câu hỏi quan trọng hơn con số uptime:

| Câu hỏi | Vì sao |
|---|---|
| **MTTR bao lâu? Kể cả 2 giờ sáng Chủ nhật?** | ⭐ Uptime 99.9% nhưng MTTR "ngày làm việc tiếp theo" = sự cố thứ Sáu mất mạng tới thứ Hai |
| Uptime tính thế nào? Theo tháng hay theo năm? | 99.9%/năm = 8.8 giờ; nếu mất liền 8 giờ một lần thì vẫn "đạt SLA" |
| Đền bù ra sao khi vi phạm? | Thường chỉ miễn phí vài ngày — không bù được thiệt hại kinh doanh |
| **Đường đi tuyến cáp nào?** | Để biết dự phòng có thật không |
| Băng thông cam kết hay "up to"? | FTTH dân dụng thường không cam kết |
| Đối xứng hay bất đối xứng? | Upload thấp làm chết VPN, video call, backup lên cloud |

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | CE/PE/CPE/demarc · các loại WAN · chỉ số SLA | ⬜ |
| **L2** Explain | Giải thích vì sao floating static không đủ cho failover thật | ⬜ |
| **L3** Configure | Cấu hình IP SLA + track + floating static | ⬜ |
| **L4** Troubleshoot | "Có backup mà không chuyển" → tìm nguyên nhân | ⬜ |
| **L5** Design | Thiết kế WAN cho công ty 3 site: loại đường, dự phòng, SLA cần gì | ⬜ |

## 14. Summary

**Key concepts**

- WAN: **leased line** *(SLA cao, đắt)* · **MPLS** *(ISP tham gia routing)* ·
  **Internet + VPN** ⭐ *(phổ biến nhất)* · **4G/5G** *(backup)*
- **CPE/CE** = thiết bị của bạn · **PE** = của ISP · **demarc** = ranh giới trách nhiệm
- ⭐ **MTTR quan trọng hơn uptime** — hỏi "đứt lúc 2 giờ sáng thì bao lâu có người"
- ⭐ **Floating static chỉ biết interface local down** — mù với lỗi ở xa
- ⭐ **IP SLA + track** = failover thật: ping liên tục, route chỉ sống khi ping OK
- ⚠️ **Đừng ping gateway ISP** — nó luôn sống. Ping IP ngoài Internet, tốt nhất 2 đích
- `delay down 10 up 30` chống nhấp nháy
- Failover xong phải **`clear ip nat translation`** → tự động hoá bằng **EEM**
- ⚠️ **PPPoE giảm MTU 1492** → bắt buộc `ip tcp adjust-mss 1452`
- ⭐ **Dự phòng phải độc lập ở mọi tầng** — khác ISP, khác tuyến cáp

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip sla 1` + `icmp-echo <ip> source-interface X` | Định nghĩa phép đo |
| `ip sla schedule 1 life forever start-time now` | ⚠️ **Thiếu là SLA không chạy** |
| `track 1 ip sla 1 reachability` | Gắn track |
| `ip route 0.0.0.0 0.0.0.0 <nh> track 1` | ⭐ Route chỉ sống khi track UP |
| `track 10 list boolean or` | Kết hợp nhiều phép đo |
| `show ip sla statistics` / `show track` | Kiểm tra |
| `ip tcp adjust-mss 1452` | ⭐ Bắt buộc với PPPoE |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Chỉ dùng floating static | Không chuyển khi lỗi ở xa |
| Ping gateway ISP làm phép đo | Track luôn UP dù upstream đứt |
| Quên `ip sla schedule` | IP SLA không bao giờ chạy |
| Không có `delay` | Track nhấp nháy, route đổi liên tục |
| Failover không clear NAT | Kết nối cũ chết, "đợi vài phút mới được" |
| Quên `ip tcp adjust-mss` với PPPoE | Web có ảnh lớn bị treo |
| Hai đường cùng ISP / cùng tuyến cáp | Đứt cùng lúc — không phải dự phòng |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 70 với đủ 3 lỗi BREAK — đặc biệt bài "chứng minh giới hạn của floating static".
2. Tìm hiểu công ty bạn: có mấy đường WAN? Từ ISP nào? Có dùng IP SLA không?
3. Nếu có quyền truy cập router biên: `show ip sla summary` và `show track` —
   failover có được cấu hình thật không?
4. Tính: SLA 99.5% nghĩa là mất bao nhiêu giờ mỗi năm?

```markdown
- [YYYY-MM-DD] Lesson 39 — WAN concepts & failover: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Các loại WAN, CE/PE/demarc, chỉ số SLA, dual-WAN |
| 🔧 **Engineer** | IP SLA + track; chọn đích ping đúng; `delay` chống nhấp nháy; MSS cho PPPoE |
| 🏭 **Production** | MTTR quan trọng hơn uptime; dự phòng phải độc lập mọi tầng; EEM clear NAT |

### 🔗 Liên kết

- ⬅️ [Phase 6 — Security](../06-security/README.md)
- ➡️ [Lesson 40 — VPN, GRE, IPsec](./lesson-40-vpn-gre-ipsec.md)
- 📚 Floating static: [Lesson 19](../02-routing/lesson-19-static-default-route.md)
- 📚 NAT dual-WAN: [Lesson 27](../03-services/lesson-27-nat-nang-cao.md)
