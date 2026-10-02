# MODULE REVIEW — Phase 4: IPv6

| | |
|---|---|
| **Phase** | 4 — IPv6 |
| **Số lesson** | 3 (29 → 31) |
| **Thời lượng dự kiến** | 1.5 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 4 trong 8 câu

1. GUA = **Global Routing Prefix (/48)** + **Subnet ID (16 bit)** + **Interface ID (64 bit)**.
2. ⭐ **Mọi subnet có host đều là `/64`** — không cần VLSM, một `/48` cho 65.536 subnet.
3. **Solicited-node multicast** làm NDP chỉ làm phiền 1 máy, trong khi ARP làm phiền cả VLAN.
4. **NDP chạy trên ICMPv6**: NS/NA thay ARP, RS/RA thay gateway discovery.
5. ⭐ **SLAAC**: host tự có địa chỉ chỉ cần một router phát RA — **không cần server nào**.
6. Cờ **M** = địa chỉ từ DHCPv6; cờ **O** = thông tin khác từ DHCPv6.
7. ⭐ **Default gateway IPv6 là địa chỉ link-local của router**, không phải GUA.
8. ⚠️ **Chặn ICMPv6 = giết chết mạng IPv6**; **IPv6 nửa vời còn tệ hơn không có IPv6**.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| Cấu trúc GUA | Prefix /48 + Subnet ID 16 bit + Interface ID 64 bit | 29 |
| `/64` cho mọi thứ | SLAAC yêu cầu đúng 64 bit — đừng subnet nhỏ hơn | 29 |
| EUI-64 | Chèn `FFFE` vào giữa MAC, **lật bit thứ 7** | 29 |
| Solicited-node multicast | `ff02::1:ff` + 24 bit cuối của địa chỉ unicast | 29 |
| Anycast | Một địa chỉ, nhiều máy, gói tới cái gần nhất | 29 |
| Header IPv6 | **40 byte cố định**, bỏ checksum, chỉ host nguồn fragment | 29 |
| NDP 5 gói | RS(133) RA(134) NS(135) NA(136) Redirect(137) | 30 |
| SLAAC | Host tự ghép prefix (từ RA) + Interface ID | 30 |
| Cờ M / O | Địa chỉ từ DHCPv6 / thông tin khác từ DHCPv6 | 30 |
| DAD | Kiểm tra trùng **trước khi dùng** địa chỉ | 30 |
| `Router Lifetime = 0` | Cấp prefix nhưng **không** làm gateway | 30 |
| RA Guard | Chống rogue RA — bắt buộc trong production | 30 |
| PMTUD | IPv6 không fragment ở router → phải permit `packet-too-big` | 30 |
| Next-hop link-local | **Phải kèm tên interface** | 31 |
| OSPFv3 | Cấu hình **trên interface**, peer bằng **link-local**, `ff02::5` | 31 |
| Router ID OSPFv3 | 32 bit — **bắt buộc đặt tay** nếu không có IPv4 | 31 |
| Dual-stack | Hai ngăn xếp độc lập, không trộn lẫn | 31 |
| Happy Eyeballs | Thử IPv6 trước, ~250ms không được thì fallback IPv4 | 31 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `ipv6 unicast-routing` | ⭐ **Luôn đầu tiên** — thiếu là không route và không gửi RA | 29 |
| `ipv6 address <addr>/64` | Gán GUA | 29 |
| `ipv6 address fe80::1 link-local` | Link-local dễ nhớ | 29 |
| `show ipv6 interface brief` | Xem mọi địa chỉ đã gán | 29 |
| `show ipv6 neighbors` | Bảng NDP — tương đương `show ip arp` | 29 |
| `ipv6 nd managed-config-flag` / `other-config-flag` | Bật cờ M / O | 30 |
| `ipv6 nd ra lifetime 0` | Không làm default gateway | 30 |
| `ipv6 nd raguard attach-policy` | ⭐ Chống rogue RA | 30 |
| `show ipv6 interface <int> \| include Hosts use` | ⭐ Biết ngay chế độ SLAAC/DHCPv6 | 30 |
| `ipv6 route <prefix> <int> FE80::X` | Static next-hop link-local | 31 |
| `ipv6 router ospf 1` + `router-id` | ⭐ Router ID bắt buộc | 31 |
| `ipv6 ospf 1 area 0` *(trên interface)* | Bật OSPFv3 | 31 |
| `show ipv6 ospf neighbor` / `interface <int>` | Debug OSPFv3 | 31 |
| `ping -6 2606:4700:4700::1111` | Test IPv6 ra Internet | 31 |

## 4. Common Mistakes

| Sai lầm | Hậu quả |
|---|---|
| Subnet nhỏ hơn `/64` cho mạng host | SLAAC không chạy |
| Dùng ULA + NAT66 cho nội bộ | Mang nỗi đau IPv4 sang vô ích |
| Quên `ipv6 unicast-routing` | Không route, **không gửi RA** |
| Dùng `::` hai lần trong một địa chỉ | Địa chỉ không hợp lệ |
| Hoảng khi thấy nhiều địa chỉ trên 1 interface | Hoàn toàn bình thường |
| Chặn hết ICMPv6 | **Giết chết** NDP, SLAAC, DAD, PMTUD |
| Quên permit `packet-too-big` | Web có nội dung lớn bị treo |
| Bật DHCPv6 stateful mà quên cờ M | Host vẫn dùng SLAAC |
| Không bật RA Guard | Một máy bật ICS là chiếm gateway cả VLAN |
| Tìm gateway IPv6 trong dải GUA | Gateway là **link-local** |
| Không đặt Router ID trên router IPv6-only | OSPFv3 **không khởi động** |
| Static link-local thiếu tên interface | Route không vào bảng |
| Thấy OSPFv3 FULL là yên tâm | GUA có thể khác prefix → không forward được |
| Để IPv6 nửa vời | "Mạng chậm" khó chẩn đoán |

## 5. Interview Questions

1. **Q:** Vì sao IPv6 bỏ ARP? Cái gì thay thế và nó tốt hơn ở điểm nào?
   **A:** ARP dựa trên **broadcast**, mà IPv6 không có broadcast. Thay bằng **NDP**
   (NS/NA) chạy trên ICMPv6, gửi tới **solicited-node multicast** `ff02::1:ffXX:XXXX`.
   Tốt hơn vì: chỉ máy có 24 bit cuối khớp mới xử lý (thay vì cả 250 máy),
   và card mạng **lọc ở phần cứng** nên CPU không bị làm phiền.

2. **Q:** Giải thích SLAAC. Nó thay thế gì của IPv4?
   **A:** Host tự sinh link-local → DAD → gửi RS tới `ff02::2` → router trả RA chứa prefix
   → host ghép `prefix + Interface ID` thành GUA → DAD lần nữa. Default gateway là
   **link-local của router gửi RA**. Nó thay thế DHCP — **không cần server nào cả**.

3. **Q:** Phân biệt SLAAC, DHCPv6 stateless, DHCPv6 stateful.
   **A:** Qua **2 cờ trong RA**: M (Managed = địa chỉ) và O (Other = thông tin khác).
   SLAAC thuần (0,0): địa chỉ và DNS đều từ RA. Stateless (0,1): địa chỉ từ SLAAC,
   DNS từ DHCPv6. Stateful (1,1): cả hai từ DHCPv6.
   Kiểm tra bằng `show ipv6 interface | include Hosts use`.

4. **Q:** Vì sao chặn ICMPv6 nguy hiểm hơn chặn ICMP ở IPv4?
   **A:** Ở IPv4, ICMP chỉ là tiện ích chẩn đoán — chặn thì mất `ping` nhưng mạng vẫn chạy.
   Ở IPv6, ICMPv6 **chở cả NDP, RS/RA, DAD, PMTUD** — tức là thành phần vận hành bắt buộc.
   Chặn hết = không phân giải được MAC, không nhận được prefix, gói lớn bị drop im lặng.

5. **Q:** Hai router OSPFv3 lên FULL nhưng ping GUA của nhau không được. Vì sao?
   **A:** GUA hai đầu **khác prefix**. OSPFv3 peer bằng **link-local** nên vẫn lên FULL,
   nhưng forward gói thật bằng GUA thì hai router không cùng subnet.
   Lỗi này **không xảy ra ở OSPFv2** vì OSPFv2 yêu cầu cùng subnet mới lên neighbor.

6. **Q:** Người dùng báo "web chậm" nhưng `ping 8.8.8.8` chỉ 20ms. Nêu nguyên nhân
   liên quan IPv6.
   **A:** **IPv6 nửa vời** + Happy Eyeballs. Máy có địa chỉ IPv6 nhưng đường ra Internet
   IPv6 hỏng. Trình duyệt thử IPv6 trước → timeout → mới fallback IPv4 → mỗi tên miền
   mới thêm vài trăm ms tới vài giây. `ping 8.8.8.8` chỉ test IPv4 nên bình thường.
   Kiểm chứng: `ping -6 2606:4700:4700::1111`.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | Host chỉ có link-local | Không có GUA | `show ipv6 interface \| include advertisements` | Router không gửi RA |
| 2 | Host có GUA, không có gateway | Ping LAN được, ra ngoài fail | `show run int \| include ra lifetime` | `ra lifetime 0` |
| 3 | Ping fail, NDP `INCMP` | Không phân giải được | Kiểm tra ACL ICMPv6 | Chặn `nd-ns`/`nd-na` |
| 4 | Ping OK, web lớn treo | Trang text được, ảnh không | Kiểm tra ACL | Chặn `packet-too-big` |
| 5 | Host lấy sai gateway | Mất mạng, hoặc bị nghe lén | Wireshark `icmpv6.type==134` | **Rogue RA** |
| 6 | OSPFv3 không chạy | Không neighbor, không log | `show ipv6 ospf` | **Thiếu Router ID** |
| 7 | OSPFv3 FULL, không ping được | Neighbor đẹp | `show ipv6 interface brief` 2 đầu | GUA khác prefix |
| 8 | "Mạng chậm", ping IPv4 bình thường | Web load lâu | `ping -6` tới một IPv6 công cộng | IPv6 nửa vời |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa sang Phase 5.

### Phần A — Lý thuyết (10 câu)

1. Cấu trúc một Global Unicast Address gồm những phần nào, mỗi phần bao nhiêu bit?
2. Vì sao mọi subnet IPv6 có host đều là `/64`? Ngoại lệ duy nhất là gì?
3. Kể 5 loại gói NDP kèm ICMPv6 type, và mỗi loại thay thế gì của IPv4.
4. Mô tả SLAAC từng bước, từ lúc interface bật tới khi có GUA đầy đủ.
5. Cờ M và O trong RA quyết định gì? Kẻ bảng 3 chế độ.
6. DAD là gì, chạy khi nào, khác gratuitous ARP ở điểm nào?
7. Default gateway IPv6 của một host là loại địa chỉ gì? Vì sao?
8. Kể 4 thứ hỏng khi chặn hết ICMPv6.
9. OSPFv3 khác OSPFv2 ở **5 điểm** nào?
10. Happy Eyeballs là gì? Vì sao "IPv6 nửa vời" gây triệu chứng mạng chậm?

### Phần B — Tính toán & cấu hình (6 câu)

11. Rút gọn tối đa: `2001:0db8:0000:0000:0abc:0000:0000:0001`
12. MAC `00:50:56:A1:B2:C3` → tính EUI-64 và địa chỉ link-local.
13. Địa chỉ `2001:db8::dead:beef` có solicited-node multicast là gì?
14. Viết cấu hình bật OSPFv3 area 0 trên `Gi0/1`, Router ID `1.1.1.1`.
15. Viết static route IPv6 tới `2001:db8:20::/64` qua next-hop link-local `fe80::2`
    trên `Gi0/1`.
16. Viết cấu hình DHCPv6 stateful: pool cấp địa chỉ + DNS, bật cờ M và O.

### Phần C — Tình huống (4 câu)

17. Host có GUA nhưng `ipconfig` không hiện Default Gateway IPv6. Nguyên nhân? Sửa thế nào?
18. Bạn áp ACL IPv6 lên interface WAN và cả mạng IPv6 chết. Nêu 3 dòng `permit`
    tối thiểu phải có.
19. Router chỉ chạy IPv6, bật OSPFv3 nhưng không có neighbor và không có log lỗi rõ ràng.
    Vì sao?
20. Hai router OSPFv3 FULL nhưng ping GUA không được. Giải thích, và nói vì sao
    lỗi này không gặp ở OSPFv2.

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Tính toán & cấu hình | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20** | ✅ Sang [Phase 5 — Wireless](../05-wireless/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai |
| < 12 | ❌ Học lại Phase 4 |

> ⚠️ Sai **câu 4, 8, hoặc 20** thì dù tổng điểm cao vẫn phải ôn lại.

### Yêu cầu bổ sung để qua phase

- [ ] Giải thích được vì sao IPv6 **không có ARP** và cái gì thay thế
- [ ] Bắt được RA/NS/NA trong Wireshark và đọc hiểu cờ M/O
- [ ] Dựng OSPFv3 2 router, ping được bằng GUA
- [ ] Đã làm LAB 40 → 42, mỗi lab có mục BREAK điền đầy đủ

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
