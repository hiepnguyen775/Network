# MODULE REVIEW — Phase 7: WAN / Enterprise

> 🏁 **Phase cuối cùng.** Qua được mini exam này là xong toàn bộ phần lý thuyết CCNA.

| | |
|---|---|
| **Phase** | 7 — WAN / Enterprise |
| **Số lesson** | 3 (39 → 41) |
| **Thời lượng dự kiến** | 1.5 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 7 trong 8 câu

1. WAN hiện đại: **Internet + VPN** đang thay dần MPLS — rẻ hơn nhiều, bù SLA bằng dual-WAN.
2. ⭐ **MTTR quan trọng hơn uptime** khi đọc SLA.
3. ⭐ **Floating static chỉ biết interface local down** — cần **IP SLA + track** cho
   failover thật.
4. ⭐ **GRE chở được multicast** *(→ routing protocol)* nhưng không mã hoá;
   **IPsec mã hoá** nhưng không chở multicast → kết hợp **GRE over IPsec**.
5. **IKE Phase 1** thương lượng **HAGLE**; **Phase 2** thương lượng transform set +
   crypto ACL.
6. ⭐ Hai lỗi VPN phổ biến nhất: **không loại trừ NAT** và **quên `ip tcp adjust-mss`**.
7. **SSL VPN (TCP 443)** thắng IPsec client vì qua được mọi mạng công cộng.
8. ⭐ **SD-WAN chọn đường theo ứng dụng + chất lượng**, không chỉ theo đích đến.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| CE / PE / CPE / demarc | Thiết bị bạn / ISP / ranh giới trách nhiệm | 39 |
| MTTR | Thời gian khắc phục — quan trọng hơn uptime | 39 |
| IP SLA + track | Ping liên tục; route chỉ sống khi ping OK | 39 |
| `delay down 10 up 30` | Chống track nhấp nháy | 39 |
| PPPoE MTU | 1492 — bắt buộc `ip tcp adjust-mss 1452` | 39 |
| GRE | Chở multicast + non-IP, **không mã hoá** | 40 |
| IPsec | Mã hoá + xác thực, **không chở multicast** | 40 |
| ESP vs AH | ESP (50) qua NAT được · AH (51) không | 40 |
| NAT-T | Bọc ESP vào UDP 4500 để qua NAT | 40 |
| HAGLE | Hash · Auth · Group · Lifetime · Encryption *(Phase 1)* | 40 |
| Crypto ACL | Phải **đối xứng ngược** ở hai đầu | 40 |
| `ip tcp adjust-mss` | ⭐ Quên là web có ảnh lớn bị treo | 40 |
| Site-to-site vs Remote access | Mạng↔mạng vs người↔mạng | 41 |
| SSL VPN | TCP 443 — qua được mọi mạng công cộng | 41 |
| Split vs Full tunnel | Internet đi thẳng vs qua công ty | 41 |
| Hairpinning | Spoke-to-spoke đi vòng qua hub | 41 |
| DMVPN | mGRE + NHRP + IPsec → spoke tự tạo tunnel trực tiếp | 41 |
| SD-WAN | Chọn đường theo **ứng dụng + chất lượng thời gian thực** | 41 |
| Local breakout | Chi nhánh ra thẳng Internet cho SaaS | 41 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `ip sla 1` + `icmp-echo <ip> source-interface X` | Định nghĩa phép đo | 39 |
| `ip sla schedule 1 life forever start-time now` | ⚠️ Thiếu là SLA không chạy | 39 |
| `track 1 ip sla 1 reachability` | Gắn track | 39 |
| `ip route 0.0.0.0 0.0.0.0 <nh> track 1` | ⭐ Route sống khi track UP | 39 |
| `track 10 list boolean or` | Kết hợp nhiều phép đo | 39 |
| `show ip sla statistics` / `show track` | Kiểm tra failover | 39 |
| `crypto isakmp policy` + `crypto isakmp key` | Phase 1 | 40 |
| `crypto ipsec transform-set` + `profile` | Phase 2 | 40 |
| `tunnel protection ipsec profile X` | ⭐ Cách hiện đại | 40 |
| `ip mtu 1400` + `ip tcp adjust-mss 1360` | ⭐ **Bắt buộc trên tunnel** | 40 |
| `show crypto isakmp sa` | ⭐ Phase 1 — tìm `QM_IDLE` | 40 |
| `show crypto ipsec sa` | ⭐ Đọc `#pkts encaps/decaps` | 40 |
| `show crypto session` | Tổng quan mọi VPN | 40, 41 |
| `show ip local pool VPN-POOL` | Còn bao nhiêu IP cho remote user | 41 |
| `route print` *(client)* | Split tunnel hay full tunnel | 41 |

## 4. Common Mistakes

| Sai lầm | Hậu quả |
|---|---|
| Chỉ dùng floating static | Không chuyển khi lỗi ở xa |
| Ping gateway ISP làm phép đo | Track luôn UP dù upstream đứt |
| Quên `ip sla schedule` | IP SLA không bao giờ chạy |
| Failover không clear NAT | Kết nối cũ chết, "đợi vài phút mới được" |
| Hai đường cùng ISP / cùng tuyến cáp | Đứt cùng lúc — không phải dự phòng |
| **Không loại trừ traffic VPN khỏi NAT** | Tunnel không lên, `encaps = 0` |
| **Quên `ip tcp adjust-mss`** | Ping được, **web có ảnh treo** |
| ACL WAN chặn UDP 500 / ESP | Phase 1 không lên |
| Crypto ACL không đối xứng | Phase 2 không lên |
| Dùng IPsec thuần rồi mong OSPF chạy | IPsec không chở multicast |
| `tunnel source` gắn interface WAN1 | VPN không lên lại sau failover |
| Full tunnel khi cả công ty WFH | Đường WAN trụ sở nghẽn |
| IPsec client cho người hay đi công tác | Không kết nối được ở khách sạn |
| Hub-and-spoke với nhiều site có VoIP | Hairpinning làm rè cuộc gọi |

## 5. Interview Questions

1. **Q:** Floating static đã cấu hình, nhưng ISP1 lỗi upstream (cáp vẫn up) thì
   không chuyển đường. Vì sao?
   **A:** Floating static **chỉ phản ứng khi interface local down**. Cáp còn up →
   interface up → route AD 1 vẫn trong bảng → traffic vào ngõ cụt.
   Sửa bằng **IP SLA + track**: ping liên tục một IP ngoài Internet, route chỉ sống
   khi ping OK.

2. **Q:** Vì sao không dùng IPsec một mình cho site-to-site?
   **A:** **IPsec không chở được multicast** → OSPF/EIGRP không chạy qua tunnel →
   phải khai static route cho mọi mạng ở xa trên mọi site, không scale.
   **GRE** chở được multicast nên kết hợp **GRE over IPsec**.

3. **Q:** VPN chạy tốt, ping OK, SSH OK, nhưng tải file lớn thì treo. Nguyên nhân?
   **A:** **MTU/MSS**. Gói 1500 + GRE 24 + IPsec ~56 = ~1580 > MTU 1500 → bị drop.
   Gói nhỏ (ping, SSH) vẫn qua được. Sửa: `ip mtu 1400` + **`ip tcp adjust-mss 1360`**
   trên interface Tunnel.

4. **Q:** `show crypto isakmp sa` hiện `QM_IDLE` nhưng `#pkts encaps = 0`. Nghĩa là gì?
   **A:** Phase 1 đã lên, nhưng **không có gói nào được đưa vào tunnel**. Hai nguyên nhân:
   (1) **traffic VPN bị NAT** → không khớp crypto ACL; (2) **routing không trỏ qua tunnel**.
   Vấn đề nằm **trước** IPsec, ở tầng routing hoặc NAT.

5. **Q:** Nhân viên báo "VPN ở nhà chạy, ở khách sạn không". Vì sao?
   **A:** Mạng khách sạn chặn **UDP 500 và ESP (protocol 50)**. Giải pháp dài hạn:
   chuyển sang **SSL VPN (TCP 443)** — cổng mà mọi mạng công cộng đều mở.

6. **Q:** SD-WAN khác WAN truyền thống ở điểm cốt lõi nào?
   **A:** WAN truyền thống chọn đường theo **đích đến** *(routing table)* — chỉ biết
   đường sống hay chết. SD-WAN chọn đường theo **ứng dụng + chất lượng đường thời gian thực** —
   ví dụ tự chuyển cuộc gọi Teams từ FTTH sang MPLS **giữa cuộc gọi** khi jitter tăng.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | "Có backup mà không chuyển" | WAN1 lỗi, traffic vẫn đi WAN1 | `show ip route \| include 0.0.0.0` | Chỉ có floating static |
| 2 | Track luôn UP dù ISP có vấn đề | Failover không kích hoạt | `show ip sla statistics` | Ping gateway ISP |
| 3 | Failover xong vẫn mất mạng vài phút | "Đợi một lúc mới được" | `show ip nat translations` | Entry NAT cũ |
| 4 | Phase 1 không lên, `MM_NO_STATE` | Tunnel down | `show crypto isakmp sa` | Sai PSK hoặc HAGLE lệch |
| 5 | Phase 1 OK, Phase 2 không lên | `show crypto ipsec sa` trống | So crypto ACL 2 đầu | ACL không đối xứng |
| 6 | Tunnel UP nhưng `encaps = 0` | Không có traffic | `show ip nat translations` | Traffic bị NAT |
| 7 | `encaps` tăng, `decaps = 0` | Một chiều | Kiểm tra ACL đầu kia | Đầu kia chặn ESP |
| 8 | Ping được, web có ảnh treo | Tải file lớn fail | `ping size 1500 df-bit` | Thiếu `ip tcp adjust-mss` |
| 9 | Cả công ty WFH → WAN nghẽn | Mọi thứ chậm | `show interface` utilization | Full tunnel |
| 10 | VoIP giữa chi nhánh rè | Jitter cao | `traceroute` giữa 2 spoke | Hairpinning qua hub |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa làm Final Project.

### Phần A — Lý thuyết (10 câu)

1. Kể 4 loại kết nối WAN và đặc điểm từng loại. Loại nào phổ biến nhất hiện nay, vì sao?
2. CE, PE, CPE, demarc là gì? Vì sao demarc quan trọng khi báo sự cố?
3. Kể 5 chỉ số SLA. Chỉ số nào quan trọng nhất và vì sao?
4. Vì sao floating static không đủ cho failover? Giải pháp là gì?
5. GRE làm được gì mà IPsec không làm được, và ngược lại?
6. Kể 5 tham số thương lượng ở IKE Phase 1 *(gợi ý: HAGLE)*.
7. Phase 2 thương lượng những gì? Crypto ACL phải thoả điều kiện gì?
8. AH và ESP khác nhau thế nào? Vì sao AH gần như không được dùng?
9. Split tunnel và full tunnel khác nhau thế nào? Nêu 2 ưu 2 nhược của split tunnel.
10. SD-WAN khác WAN truyền thống ở điểm cốt lõi nào? Cho một ví dụ cụ thể.

### Phần B — Cấu hình (6 câu)

11. Viết cấu hình IP SLA ping `8.8.8.8` qua `Gi0/1` mỗi 5 giây + track + floating static.
12. Viết EEM script tự `clear ip nat translation` khi track 10 down.
13. Viết cấu hình IKE Phase 1: AES-256, SHA-256, PSK, DH group 14, lifetime 86400.
14. Viết cấu hình interface Tunnel0 GRE over IPsec, kèm **2 dòng MTU/MSS bắt buộc**.
15. Viết NAT-ACL loại trừ traffic VPN giữa `10.0.0.0/24` và `10.1.0.0/24`.
16. Viết ACL trên WAN cho phép VPN đi qua *(3 dòng cần thiết)*.

### Phần C — Tình huống (4 câu)

17. Công ty mua 2 đường Internet "để dự phòng" nhưng vẫn mất mạng hoàn toàn khi
    thợ đào đường cắt cáp. Nêu 2 nguyên nhân.
18. `show crypto isakmp sa` hiện `QM_IDLE`, `#pkts encaps = 0`. Nêu 2 nguyên nhân
    theo thứ tự kiểm tra.
19. VPN chạy tốt, ping và SSH OK, nhưng tải file lớn qua tunnel thì treo.
    Nguyên nhân và cách sửa.
20. Công ty 12 chi nhánh dùng hub-and-spoke, VoIP giữa các chi nhánh bị rè.
    Nguyên nhân và 2 giải pháp.

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Cấu hình | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20** | ✅ Bắt tay vào **[FINAL CCNA PROJECT](../labs/README.md#-final-ccna-project)** |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai |
| < 12 | ❌ Học lại Phase 7 |

> ⚠️ Sai **câu 4, 5, hoặc 19** thì dù tổng điểm cao vẫn phải ôn lại.

### Yêu cầu bổ sung để qua phase

- [ ] Dựng được **GRE over IPsec** giữa 2 site trên GNS3/EVE-NG, chạy OSPF qua tunnel
- [ ] Giải thích được toàn bộ quá trình thiết lập **IKE Phase 1 và Phase 2**
- [ ] Thuộc **6 bước troubleshoot VPN**, không nhìn tài liệu
- [ ] Đã làm LAB 70 → 72, mỗi lab có mục BREAK điền đầy đủ

---

## 🏁 Sau mini exam này

```text
Bạn đã học xong 41 lesson, 8 phase, toàn bộ blueprint CCNA 200-301.

          ↓

🏁 FINAL CCNA PROJECT
   Thiết kế + triển khai network cho công ty 100–300 users
   → labs/README.md

          ↓

🎓 Đăng ký thi CCNA 200-301

          ↓

➡️  CCNP-Encor   (Phase 8)
➡️  Network-Automation (Phase 9)
```

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
