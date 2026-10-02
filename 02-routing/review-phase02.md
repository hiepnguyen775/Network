# MODULE REVIEW — Phase 2: Routing

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Số lesson** | 7 (18 → 24) |
| **Thời lượng dự kiến** | 3 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 2 trong 10 câu

1. Router nhận frame → đọc Dst IP → tra RIB → giảm TTL → **tạo frame mới** → gửi.
2. `C` = subnet của interface, **`L` = IP của chính router, luôn `/32`** để phân biệt
   "gói cho tôi" và "gói qua tôi".
3. ⭐ Thứ tự chọn route: **Longest Prefix Match → AD → Metric**. Prefix xét **trước** AD.
4. **AD** so sánh giữa các nguồn; **Metric** so sánh trong cùng protocol.
5. Static route **không vào bảng** nếu next-hop không reachable; **floating static**
   (AD cao) làm backup.
6. Static chỉ biết **interface local down** — không biết lỗi ở xa → cần IP SLA + track.
7. **Distance Vector** tin lời láng giềng kể; **Link-State** tự nhìn bản đồ tự tính.
8. OSPF: 7 state, dừng ở **FULL** (hoặc **2-WAY giữa 2 DROTHER — bình thường**).
9. ⭐ Kẹt **EXSTART/EXCHANGE = MTU mismatch**; kẹt **INIT = một chiều không thông**.
10. **Area là ranh giới của LSA flooding và SPF**; mọi area phải chạm **Area 0**.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| RIB vs FIB | Bảng logic (`show ip route`) vs bảng phần cứng (`show ip cef`) | 18 |
| `C` và `L` | Subnet vs chính IP router (`/32`) | 18 |
| Recursive lookup | Next-hop phải reachable, nếu không route không vào bảng | 19 |
| Floating static | AD cao hơn → chỉ vào bảng khi route chính mất | 19 |
| `Null0` | Vứt gói — chặn traffic, chống loop khi summarize | 19 |
| Longest prefix match | Prefix dài nhất thắng, **trước cả AD** | 20 |
| ECMP | Cùng prefix + AD + metric → chia tải | 20 |
| Distance Vector | Trao đổi **bảng định tuyến**, hội tụ chậm | 21 |
| Link-State | Trao đổi **thông tin link**, tự chạy SPF | 21 |
| Split horizon | Không quảng bá route ngược hướng đã học | 21 |
| 6 thứ phải khớp | subnet · area · hello/dead · auth · MTU · không passive | 22 |
| DR/BDR | Giảm adjacency từ `N(N−1)/2` xuống `2(N−2)+1` | 22 |
| Cost | `reference bandwidth / bandwidth`, cộng interface **đi ra** | 22, 23 |
| LSDB | Bản đồ area — **mọi router phải giống hệt nhau** | 23 |
| LSA 1/2/3 | Router (mọi router) · Network (**chỉ DR**) · Summary (**chỉ ABR**) | 23 |
| ABR | Có chân ở Area 0 **và** area khác; dịch Type 1/2 → Type 3 | 24 |
| Summarization | Gom route **và cách ly sự bất ổn** giữa các area | 24 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `show ip route <ip>` | ⭐ Router **thật sự** chọn route nào | 18, 20 |
| `show ip route connected/static/ospf` | Lọc theo nguồn | 18 |
| `show ip cef <ip>` | Data plane thấy gì | 18 |
| `ip route <net> <mask> <nh> [AD] name X` | Static / floating static | 19 |
| `ip route <net> <mask> Null0` | Vứt traffic | 19 |
| `show ip protocols` | Protocol nào chạy, quảng bá gì, AD | 20, 21 |
| `router ospf 1` + `router-id` | Cấu hình OSPF | 22 |
| `network <ip> 0.0.0.0 area N` | ⭐ Khai từng interface, rõ ràng nhất | 22 |
| `passive-interface default` + `no passive-interface <int>` | An toàn mặc định | 22 |
| `auto-cost reference-bandwidth 100000` | **Mọi router** phải giống nhau | 22 |
| `show ip ospf neighbor` | ⭐ Đầu tiên khi debug OSPF | 22 |
| `show ip ospf interface <int>` | ⭐ Area, Network Type, Cost, Timer cùng lúc | 22 |
| `ip ospf network point-to-point` | Bỏ bầu DR trên link 2 router | 22 |
| `show ip ospf database [router <id>]` | Bản đồ area, cost từng link | 23 |
| `ip ospf cost N` | Ép cost mà không ảnh hưởng thứ khác | 23 |
| `area N range <net> <mask>` | Summarize — **chỉ trên ABR** | 24 |
| `show ip ospf` | Có phải ABR, SPF chạy mấy lần, số LSA | 23, 24 |

## 4. Common Mistakes

| Sai lầm | Vì sao hay sai | Cách tránh |
|---|---|---|
| "AD xét trước longest prefix match" | Trực giác sai | **Prefix dài hơn luôn thắng** |
| So metric OSPF với metric RIP | Cùng gọi là "metric" | Khác đơn vị — đó là lý do AD tồn tại |
| Static trỏ next-hop không tồn tại | IOS **không báo lỗi** | Luôn `show ip route <net>` sau khi gõ |
| Chỉ xem routing table một đầu | Quên chiều về | Ping một chiều → xem **cả hai** |
| Exit-interface trên link Ethernet | Trên serial thì không sao | Dùng next-hop hoặc fully specified |
| Floating static quên đặt AD | Nhìn config thấy đối xứng | Cả hai vào bảng → ECMP ngoài ý muốn |
| Dùng subnet mask thay wildcard trong `network` | Hai thứ trông giống nhau | OSPF/ACL dùng **wildcard** |
| Hoảng khi thấy `2WAY/DROTHER` | Tưởng là lỗi | **Bình thường** giữa 2 DROTHER |
| Không đặt Router ID | Mạng vẫn chạy | Interface down → Router ID đổi → reset neighbor |
| Quên `auto-cost reference-bandwidth` | Mạng vẫn chạy | Link 10G và 100M cùng cost 1 |
| reference-bandwidth lệch giữa router | Khó phát hiện | Cost bất đối xứng, traffic đi/về khác đường |
| Quên `passive-interface` | Không ai báo | Lộ topology; ai cũng giả router được |
| `area range` trên router không phải ABR | Lệnh được nhận | Không có tác dụng — bẫy im lặng |
| Area không chạm Area 0 | Nhìn sơ đồ thấy "có nối" | Route không lan ra ngoài |

## 5. Interview Questions

1. **Q:** Router chọn route theo thứ tự nào? Cho ví dụ chứng minh.
   **A:** **Longest prefix match → AD → Metric.** Ví dụ: `S 10.0.2.0/24 [1/0]` và
   `O 10.0.2.128/25 [110/2]`, gói tới `10.0.2.200` → chọn route **`/25` của OSPF**
   dù AD cao hơn, vì prefix dài hơn. AD chỉ xét khi cùng prefix length.

2. **Q:** OSPF neighbor kẹt ở EXSTART. Bạn kiểm tra gì?
   **A:** Gần như luôn là **MTU mismatch**. `show interfaces <int> | include MTU` ở
   cả hai đầu. Ở bước EXCHANGE hai router trao đổi gói DBD; MTU lệch → gói lớn không
   qua được → kẹt vĩnh viễn.

3. **Q:** DR/BDR sinh ra để làm gì?
   **A:** Giảm số adjacency trên link multi-access. Không có DR: `N(N−1)/2` adjacency
   (10 router = 45). Có DR: mọi router chỉ FULL với DR và BDR. Ngoài ra DR tạo
   **LSA Type 2** mô tả segment, giúp LSDB nhỏ hơn.

4. **Q:** Vì sao mọi OSPF area phải nối với Area 0?
   **A:** OSPF chống loop **trong** area bằng SPF (bản đồ đầy đủ). **Giữa** các area,
   router chỉ nhận LSA Type 3 — một "lời kể" kiểu distance vector, không có bản đồ.
   Topology hình sao quanh Area 0 đảm bảo không có vòng giữa các area.

5. **Q:** Floating static có phát hiện được mọi sự cố không?
   **A:** Không. Nó chỉ rút lui khi **interface local down** hoặc next-hop không
   reachable. ISP chết ở xa mà cáp vẫn up → route vẫn nằm trong bảng, traffic vào ngõ cụt.
   Giải pháp thật: **IP SLA + track**.

6. **Q:** Summarization trên ABR có lợi gì ngoài việc giảm số route?
   **A:** Lợi ích lớn nhất là **cách ly sự bất ổn**. Một subnet trong Area 1 flap →
   route tổng hợp **không đổi** → area khác không nhận LSA mới, **không phải chạy lại SPF**.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | Gõ static xong không thấy trong bảng | Lệnh được nhận | `show ip route <next-hop>` | Next-hop không reachable |
| 2 | Ping một chiều | Đi được, không có reply | `show ip route` **cả 2 đầu** | Thiếu route chiều về |
| 3 | Default route "không hoạt động" | Traffic không ra Internet | `show ip route 8.8.8.8` | Route khác khớp cụ thể hơn |
| 4 | OSPF không có neighbor | `show ip ospf neighbor` trống | `show ip protocols` | passive-interface, hoặc thiếu `network` |
| 5 | Neighbor kẹt INIT | Một bên thấy, bên kia không | `show access-lists` đầu kia | ACL chặn `224.0.0.5` |
| 6 | Neighbor kẹt EXSTART | Lặp lại không dứt | `show interfaces \| include MTU` | **MTU mismatch** |
| 7 | OSPF FULL nhưng không có route | Neighbor đẹp, route thiếu | `show ip protocols` | Thiếu `network` statement cho mạng đó |
| 8 | Traffic đi link chậm | Chậm khó hiểu | `show ip ospf database router <id>` | Cost sai, hoặc reference-bandwidth mặc định |
| 9 | Area X không được thấy từ ngoài | Một chiều thấy được | `show ip ospf \| include border` | Area không chạm Area 0 |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa sang Phase 3.

### Phần A — Lý thuyết (10 câu)

1. Kể 5 bước router xử lý một gói tin.
2. `C` và `L` khác nhau thế nào? Vì sao `L` luôn là `/32`?
3. Thứ tự 3 tiêu chí chọn route? Cho ví dụ chứng minh prefix xét trước AD.
4. AD của Connected / Static / EIGRP internal / OSPF / RIP / iBGP?
5. AD và Metric khác nhau ở điểm nào?
6. Distance Vector và Link-State khác nhau ở điểm cốt lõi nào?
7. Kể 7 OSPF neighbor state. Hai state kết thúc **hợp lệ** là gì?
8. Kể **6 thứ phải khớp** để OSPF lên neighbor.
9. DR/BDR bầu theo tiêu chí nào? Có preemption không?
10. LSA Type 1, 2, 3: ai tạo, chứa gì, lan tới đâu?

### Phần B — Cấu hình & tính toán (6 câu)

11. Viết floating static: default route chính qua `1.1.1.1`, backup qua `2.2.2.2`.
12. Viết cấu hình OSPF cho R1: Router ID `1.1.1.1`, loopback, bật OSPF trên
    `Gi0/1 (10.0.12.1)` vào area 0, passive mặc định.
13. Reference bandwidth mặc định. Tính cost của: link 10 Mbps, 100 Mbps, 1 Gbps, serial 1.544 Mbps.
14. Area 1 có `10.1.0.0/24` → `10.1.15.0/24`. Viết lệnh summarize gọn nhất.
15. Cho `O IA 10.2.0.0/16 [110/4]` — giải thích từng phần.
16. Viết lệnh bỏ bầu DR trên một link Ethernet chỉ có 2 router.

### Phần C — Tình huống (4 câu)

17. Cho bảng định tuyến sau, gói tới `10.5.5.200` đi đường nào? Vì sao?
    ```
    S*   0.0.0.0/0       [1/0]      via 203.0.113.1
    O    10.0.0.0/8      [110/10]   via 10.1.1.2
    S    10.5.5.0/24     [1/0]      via 10.1.1.4
    C    10.5.5.64/26    directly connected
    ```
18. OSPF neighbor kẹt EXSTART. Nêu nguyên nhân và 2 lệnh kiểm chứng.
19. R1 thấy neighbor ở state `INIT`. Giải thích chuyện gì đang xảy ra và nêu 2 nguyên nhân.
20. Bạn có link 1 Gbps và 10 Gbps song song, OSPF chia tải cả hai. Vì sao? Sửa thế nào?

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Cấu hình & tính toán | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20** | ✅ Sang [Phase 3 — Services](../03-services/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai, làm lại sau 3 ngày |
| < 12 | ❌ Học lại Phase 2 — đây là phase quan trọng nhất, đừng bỏ qua |

> ⚠️ Sai **câu 3, 8, hoặc 17** thì dù tổng điểm cao vẫn phải ôn lại.

### Yêu cầu bổ sung để qua phase

- [ ] Dựng OSPF 3 router, 2 area, hội tụ đúng, **không copy cấu hình**
- [ ] Cho một `show ip route` bất kỳ → giải thích được **từng dòng**
- [ ] Thuộc **9 bước troubleshoot OSPF không lên neighbor**, không nhìn tài liệu
- [ ] Đã làm LAB 20 → 24, mỗi lab có mục BREAK điền đầy đủ

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
