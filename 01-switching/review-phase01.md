# MODULE REVIEW — Phase 1: Switching

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Số lesson** | 7 (11 → 17) |
| **Thời lượng dự kiến** | 3 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 1 trong 10 câu

1. Switch chuyển frame bằng **ASIC + CAM table** → nhanh hơn router; traffic bình thường
   không chạm CPU switch.
2. **L2 switch** ở access, **L3 switch** ở distribution/core, **router** để ra WAN.
3. **VLAN** chia một switch vật lý thành nhiều broadcast domain logic — nó **tạo ranh giới**,
   và chính vì thế **tạo nhu cầu routing**.
4. **Trunk 802.1Q** chở nhiều VLAN bằng tag 4 byte; **native VLAN** là VLAN duy nhất không tag.
5. **Inter-VLAN routing**: Router-on-a-Stick (có nút cổ chai) hoặc **SVI trên L3 switch** (chuẩn).
6. `ip routing` phải **bật tay** trên L3 switch — quên là VLAN không thông nhau.
7. **Frame Ethernet không có TTL** → loop L2 gây broadcast storm làm sập mạng trong vài giây.
8. **STP** biến topology có vòng thành cây không vòng; luôn **chỉ định root bridge**,
   đừng để MAC ngẫu nhiên quyết định.
9. **RSTP** hội tụ dưới 1 giây; **PortFast luôn đi kèm BPDU Guard**.
10. **EtherChannel** gộp link để STP không block — nhưng **một luồng chỉ đi trên một link**.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| CAM table / ASIC | Tra MAC bằng phần cứng → wire-speed | 11 |
| SVI | Interface ảo đại diện VLAN, là gateway của VLAN đó | 11 |
| `no switchport` | Biến port switch thành interface L3 có IP riêng | 11 |
| Access/Distribution/Core | Access nối thiết bị · Distribution route+ACL · Core chỉ tốc độ | 11 |
| running vs startup | RAM vs NVRAM — gõ xong phải `wr` | 12 |
| `vlan.dat` | VLAN **không** nằm trong startup-config | 12 |
| VLAN | Chia broadcast domain bằng phần mềm | 13 |
| 802.1Q tag | 4 byte, chèn giữa Src MAC và EtherType, VLAN ID 12 bit | 13 |
| Native VLAN | VLAN duy nhất không tag trên trunk — hai đầu phải khớp | 13 |
| Router-on-a-Stick | 1 trunk + subinterface; có **nút cổ chai** | 14 |
| `encapsulation dot1Q` | Gắn subinterface với VLAN, gõ **trước** `ip address` | 14 |
| Bridge ID | `priority (bội 4096) + VLAN ID + MAC` | 15 |
| Root/Designated/Blocked | 3 bước bầu chọn của STP | 15 |
| Proposal/Agreement | Cơ chế làm RSTP nhanh — hỏi thay vì chờ | 16 |
| BPDU Guard vs Root Guard | Chống *có* BPDU vs chống BPDU *quá tốt* | 16 |
| EtherChannel | Nhiều link vật lý → một link logic, STP không block | 17 |
| Load balancing theo luồng | Một `(src,dst)` luôn đi một link | 17 |
| Port Security sticky | Học MAC rồi ghi vào config | 17 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `ip routing` | **Đầu tiên** trên L3 switch | 11 |
| `no switchport` | Tạo routed port | 11 |
| `show power inline` | PoE budget còn bao nhiêu | 11 |
| `copy run start` / `wr` | **Luôn trước khi rời máy** | 12 |
| `do show ...` | Xem nhanh trong config mode | 12 |
| `interface range gi1/0/1 - 24` | Sửa nhiều port một lúc | 12 |
| `show interfaces status` | Nhìn nhanh toàn bộ port | 12 |
| `show vlan brief` | VLAN tồn tại chưa, port nào thuộc đâu | 13 |
| `show interfaces trunk` | Debug trunk — đọc đủ **4 bảng** | 13 |
| `interface vlan N` + `ip address` | Tạo SVI | 14 |
| `encapsulation dot1Q N [native]` | Subinterface cho RoAS | 14 |
| `show spanning-tree vlan N` | Root ở đâu, port nào block | 15 |
| `spanning-tree vlan N root primary` | **Chỉ định root** | 15 |
| `spanning-tree mode rapid-pvst` | Bật RSTP | 16 |
| `spanning-tree portfast` + `bpduguard enable` | Port nối PC | 16 |
| `spanning-tree guard root` | Port hướng xuống access | 16 |
| `show interfaces status err-disabled` | Port nào tắt, vì sao | 16 |
| `channel-group 1 mode active` | EtherChannel LACP | 17 |
| `show etherchannel summary` | Đọc flag `(P)`/`(s)`/`(I)` | 17 |
| `switchport port-security` | Giới hạn MAC trên port | 17 |

## 4. Common Mistakes

| Sai lầm | Vì sao hay sai | Cách tránh |
|---|---|---|
| Quên `ip routing` trên L3 switch | SVI vẫn up, ping gateway vẫn được | Kiểm tra `show ip route` có nội dung |
| SVI `down/down` tưởng do cấu hình | Thực ra VLAN chưa có port nào up | `show vlan brief` |
| Quên `wr` | Mọi thứ đang chạy bình thường | Thói quen: verify xong là `wr` |
| `write erase` mà VLAN vẫn còn | VLAN ở `vlan.dat`, không ở NVRAM | `delete flash:vlan.dat` |
| Quên `switchport mode access/trunk` | Port `dynamic auto` vẫn chạy được | Luôn chốt cứng mode |
| Native VLAN lệch hai đầu | Trunk vẫn "lên" | `show interfaces trunk`, xem log CDP |
| Quên `no shutdown` interface vật lý (RoAS) | Subinterface nhìn config đúng hết | Interface vật lý phải up trước |
| Để root bridge bầu mặc định | Mạng vẫn chạy, chỉ chậm khó hiểu | Luôn `root primary`/`secondary` |
| Tắt STP vì "không có vòng" | Thấy thừa | Một dây cắm nhầm là sập mạng |
| PortFast không kèm BPDU Guard | Thấy không cần | Coi như một lệnh hai dòng |
| PortFast trên port nối switch | Nhầm port | **Loop tức thì** |
| Nhầm BPDU Guard với Root Guard | Tên giống nhau | BPDU Guard = access · Root Guard = trunk xuống |
| Hai đầu EtherChannel cùng `passive` | Nhìn config thấy đối xứng đẹp | Phải có ít nhất một bên chủ động |
| Mong một luồng dùng hết băng thông channel | Trực giác sai | Một luồng = một link |
| Port Security `maximum 1` ở port có IP phone | Quên phone cũng có MAC | Để `maximum 2` |

## 5. Interview Questions

1. **Q:** VLAN giải quyết vấn đề gì? Nếu không có VLAN thì sao?
   **A:** Chia **broadcast domain** mà không cần mua thêm switch/router và kéo dây riêng.
   Không có VLAN: một broadcast domain khổng lồ (mạng chậm, sự cố lan rộng), không có
   ranh giới bảo mật (không có hop L3 nào để đặt ACL), và phải bị trói vào vị trí vật lý.

2. **Q:** Trunk đã lên, VLAN 20 nằm trong allowed list, nhưng PC hai đầu VLAN 20 không
   ping được nhau. Lần ra sao?
   **A:** Đọc đủ **4 bảng** của `show interfaces trunk`: (1) trunk có `trunking` không,
   native VLAN khớp chưa; (2) VLAN 20 có trong `allowed`; (3) VLAN 20 có **tồn tại**
   trên switch kia không; (4) STP có đang **block** VLAN 20 trên trunk đó không.
   Sau đó mới kiểm tra IP/mask của PC.

3. **Q:** Vì sao loop ở L2 nguy hiểm hơn loop ở L3?
   **A:** Gói IP có **TTL** — chạy vòng 255 lần rồi tự chết. Frame Ethernet **không có TTL**
   → chạy vòng vĩnh viễn và nhân lên theo cấp số nhân → broadcast storm làm sập mạng
   trong vài giây.

4. **Q:** Khi nào dùng Router-on-a-Stick, khi nào dùng SVI?
   **A:** SVI gần như luôn tốt hơn: route bằng ASIC ở wire-speed, không nghẽn.
   RoAS có **nút cổ chai** — traffic inter-VLAN đi lên rồi xuống cùng một link.
   Dùng RoAS khi: chi nhánh nhỏ đã có sẵn router + switch L2, hoặc cần tính năng
   chỉ router có (NAT, IPsec VPN, QoS sâu).

5. **Q:** EtherChannel 4 × 1 Gbps. Copy một file giữa 2 máy đạt tối đa bao nhiêu?
   **A:** **1 Gbps**. Load balancing băm theo **luồng**, một cặp `(src, dst)` luôn đi trên
   **một** link vật lý. 4 Gbps là tổng thông lượng khi có nhiều luồng khác nhau.

6. **Q:** Phân biệt BPDU Guard và Root Guard.
   **A:** **BPDU Guard** đặt ở port access, kích hoạt khi nhận **bất kỳ** BPDU nào
   (nghĩa là có switch cắm vào port người dùng), đưa port vào `err-disabled` —
   **không tự hồi**. **Root Guard** đặt ở port trunk hướng xuống access, kích hoạt khi
   nhận BPDU **tốt hơn** root hiện tại, đưa port vào `root-inconsistent` — **tự hồi**
   khi BPDU xấu ngừng.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | VLAN mới tạo không thông giữa 2 switch | Ping fail, trunk vẫn up | `show interfaces trunk` bảng 3 | VLAN chưa tạo trên switch thứ hai |
| 2 | PC ping được gateway, không ping VLAN khác | — | `show ip route` trống | Quên `ip routing` |
| 3 | Mạng treo, đèn nháy đồng loạt | Mọi thứ đứng | `show processes cpu sorted` | Loop L2 → broadcast storm |
| 4 | Traffic đi đường vòng khó hiểu | Chậm nhưng vẫn chạy | `show spanning-tree root` | Root bridge nằm ở switch access |
| 5 | PC đợi 30 giây mới có IP | DHCP timeout | `show spanning-tree interface` | Thiếu PortFast |
| 6 | Port đột nhiên chết sau khi user cắm gì đó | Mất mạng một người | `show interfaces status err-disabled` | BPDU Guard — có switch lạ |
| 7 | EtherChannel không bundle | Port `(s)` suspended | So `show run interface` hai đầu | Lệch native VLAN / allowed VLAN |
| 8 | Reboot switch xong mất cấu hình | Về mặc định | `show startup-config` trống | Quên `wr` |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa sang Phase 2.

### Phần A — Lý thuyết (10 câu)

1. VLAN giải quyết vấn đề gì? Kể **hai** thứ duy nhất chia nhỏ được broadcast domain.
2. Access port và trunk port khác nhau thế nào? Tag 802.1Q dài bao nhiêu byte, chèn ở đâu?
3. Native VLAN là gì? Hai đầu trunk đặt khác nhau thì chuyện gì xảy ra?
4. Kể **4 bảng** của `show interfaces trunk` và mỗi bảng trả lời câu hỏi gì.
5. So sánh Router-on-a-Stick và SVI: tốc độ, nút cổ chai, khi nào dùng cái nào.
6. Vì sao loop L2 nguy hiểm hơn loop L3?
7. Bridge ID gồm những phần nào? Priority mặc định là bao nhiêu và đặt được giá trị nào?
8. Kể 3 bước bầu chọn của STP theo đúng thứ tự, và tiêu chí của từng bước.
9. RSTP nhanh hơn STP nhờ **3** thay đổi nào?
10. Phân biệt BPDU Guard và Root Guard: đặt ở đâu, kích hoạt khi nào, có tự hồi không.

### Phần B — Cấu hình & đọc output (6 câu)

11. Viết lệnh tạo VLAN 20 tên `KETOAN`, gán port Gi1/0/5 vào đó, kèm PortFast + BPDU Guard.
12. Viết **đủ** cấu hình Router-on-a-Stick cho VLAN 10 và VLAN 99 (native), trên Gi0/0.
13. Viết lệnh chỉ định SW-CORE1 làm root chính và SW-CORE2 làm root phụ cho VLAN 1–100.
14. Cho output: `Root ID Priority 24586`. Giải thích con số 24586 đến từ đâu.
15. Trong `show etherchannel summary`, port hiện `(s)`. Nghĩa là gì? Kể 4 tham số cần so sánh.
16. Viết cấu hình EtherChannel LACP trunk 2 port, allowed VLAN 10,20,99.

### Phần C — Tình huống (4 câu)

17. Trunk `trunking`, VLAN 30 trong `allowed`, nhưng PC hai đầu VLAN 30 không ping được nhau.
    Nêu **3 nguyên nhân** còn lại và lệnh kiểm chứng từng cái.
18. L3 switch, SVI VLAN 10 và 20 đều `up/up`, PC ping được gateway của mình nhưng không
    ping được VLAN kia. Nguyên nhân phổ biến nhất? Kiểm chứng thế nào?
19. Port Gi1/0/8 vào `err-disabled`. Nêu **3 nguyên nhân** có thể và cách phân biệt.
20. EtherChannel 2 × 1 Gbps giữa 2 switch. Bạn copy file 10 GB và chỉ đạt ~950 Mbps.
    Có phải lỗi không? Giải thích.

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Cấu hình & đọc output | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20** | ✅ Sang [Phase 2 — Routing](../02-routing/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai, làm lại sau 3 ngày |
| < 12 | ❌ Học lại Phase 1 |

> ⚠️ Sai **câu 6, 8, hoặc 18** thì dù tổng điểm cao vẫn phải ôn lại —
> ba câu đó đo đúng phần cốt lõi của Phase 1.

### Yêu cầu bổ sung để qua phase

- [ ] Dựng lab 2 switch + 3 VLAN + trunk + L3 switch inter-VLAN trong **dưới 20 phút**,
      **không nhìn tài liệu**
- [ ] Đã làm LAB 10 → 15, **mỗi lab có mục BREAK điền đầy đủ**
- [ ] Cho một `show spanning-tree` bất kỳ → nói ra root ở đâu, port nào block, **vì sao**

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
