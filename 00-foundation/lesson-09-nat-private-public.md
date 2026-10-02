# LESSON 09 — NAT · Private vs Public IP

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 02](./lesson-02-ipv4-va-subnetting.md), [Lesson 06](./lesson-06-tcp-udp-port.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Phân biệt dải private và public, nói được vì sao private không route được trên Internet
- [ ] Giải thích **PAT phân biệt các kết nối bằng gì** — và liên hệ với socket ở Lesson 06
- [ ] Phân biệt static NAT / dynamic NAT / PAT và biết khi nào dùng cái nào
- [ ] Hiểu 4 thuật ngữ `inside local / inside global / outside local / outside global`
- [ ] Nói được vì sao NAT phá vỡ mô hình end-to-end và hệ quả thực tế

## 2. Prerequisite

- Dải private RFC 1918 *(Lesson 02)*
- Socket 4 giá trị, ephemeral port *(Lesson 06)*
- Router quyết định route theo IP đích *(Lesson 05)*

---

## 3. Concept

### Private vs Public

| Loại | Dải | Đặc điểm |
|---|---|---|
| **Private** (RFC 1918) | `10.0.0.0/8`<br>`172.16.0.0/12`<br>`192.168.0.0/16` | Dùng tự do trong nội bộ. **Router Internet vứt bỏ** gói có IP private |
| **Public** | Phần còn lại | IANA/RIR cấp, định tuyến được toàn cầu, **phải mua** |
| CGNAT | `100.64.0.0/10` | ISP dùng để NAT nhiều lần — không phải private, không phải public |

> 🔑 Đây là lý do tồn tại của NAT: nhà bạn có 20 thiết bị dùng IP private,
> nhưng ISP chỉ cấp **một** IP public.

### Ba kiểu NAT

| Kiểu | Ánh xạ | Dùng khi |
|---|---|---|
| **Static NAT** | 1 private ↔ 1 public, **cố định** | Server nội bộ cần truy cập từ ngoài vào |
| **Dynamic NAT** | N private ↔ pool M public, cấp tạm | Hiếm dùng — vẫn cần nhiều IP public |
| **PAT** *(NAT Overload)* | **N private ↔ 1 public**, phân biệt bằng **port** | **99% trường hợp thực tế** |

### PAT hoạt động thế nào

```text
NAT table trên router:

Inside Local          Inside Global          Outside
10.0.0.10 : 51234  →  203.0.113.5 : 1024  →  8.8.8.8 : 443
10.0.0.11 : 49800  →  203.0.113.5 : 1025  →  8.8.8.8 : 443
10.0.0.10 : 51235  →  203.0.113.5 : 1026  →  1.1.1.1 : 443
                      └── cùng 1 IP public, KHÁC PORT ──┘
```

Gói trả về `203.0.113.5:1025` → router tra bảng → biết là của `10.0.0.11:49800`.

> 💡 Đây chính là **socket 4 giá trị** ở Lesson 06 được dùng lại. Port nguồn không chỉ
> phân biệt ứng dụng trên một máy — nó còn phân biệt **máy nào** sau NAT.
> Về lý thuyết một IP public gánh được ~64.000 kết nối đồng thời.

### Bốn thuật ngữ Cisco — bảng phải thuộc

| Thuật ngữ | Nghĩa | Ví dụ |
|---|---|---|
| **Inside Local** | IP thật của máy nội bộ | `10.0.0.10` |
| **Inside Global** | IP nội bộ **sau khi NAT**, nhìn từ ngoài | `203.0.113.5` |
| **Outside Local** | IP máy ngoài, nhìn từ bên trong | `8.8.8.8` |
| **Outside Global** | IP thật của máy ngoài | `8.8.8.8` |

Cách nhớ:

> **Inside/Outside** = máy đó thuộc *bên trong* hay *bên ngoài*.
> **Local/Global** = đang nhìn địa chỉ đó *từ trong* hay *từ ngoài*.

*(Outside Local thường bằng Outside Global — chúng chỉ khác nhau khi có NAT ở cả hai đầu.)*

---

## 4. Why?

> **Nếu không có NAT thì sao?**

| Vấn đề | Thực tế |
|---|---|
| **Hết IPv4** | Chỉ có ~4.3 tỷ địa chỉ IPv4. Đã cạn từ 2011. Không có NAT thì Internet đã dừng mở rộng từ lâu. |
| **Chi phí** | Mỗi IP public phải thuê. 300 máy = 300 IP = rất đắt. |
| **Lộ cấu trúc nội bộ** | Không NAT thì mọi máy nội bộ đều có địa chỉ định tuyến được từ Internet. |

Và một lợi ích **phụ** hay bị hiểu nhầm thành lợi ích chính:

> ⚠️ **NAT không phải firewall.** Nó *vô tình* chặn kết nối từ ngoài vào vì không có
> entry trong bảng NAT — nhưng đó là **tác dụng phụ**, không phải cơ chế bảo mật.
> NAT không kiểm tra nội dung, không lọc theo luật, không ghi log như firewall.
> Đừng bao giờ nói "có NAT rồi nên an toàn".

### Cái giá của NAT

| Vấn đề | Giải thích |
|---|---|
| **Phá vỡ end-to-end** | Máy ngoài không chủ động kết nối vào máy trong được (trừ khi port forwarding) |
| **Khó với P2P, VoIP, game** | Phải dùng STUN/TURN/ICE để "đục lỗ" qua NAT |
| **Khó truy vết** | Log phía server chỉ thấy IP public chung — muốn biết máy nào phải đối chiếu log NAT |
| **Phá một số giao thức** | IPsec AH, FTP active, SIP cần xử lý đặc biệt (NAT traversal, ALG) |

> 🔧 Đây là một trong những lý do IPv6 ra đời: đủ địa chỉ cho mọi thiết bị → **không cần NAT**.

---

## 5. How does it work?

### Khái niệm inside / outside interface

Router phải biết hướng nào là trong, hướng nào là ngoài:

```text
        10.0.0.0/24                      203.0.113.0/30
   PC ──────────── [Gi0/0]  R1  [Gi0/1] ──────────── Internet
                  ip nat inside      ip nat outside
```

> ⚠️ **Gán sai hai dòng này là lỗi số 1 với NAT.** Router sẽ **im lặng không NAT gì cả**,
> không báo lỗi. Gói ra ngoài vẫn mang IP private và bị ISP vứt.

### Luồng gói qua PAT

```text
ĐI RA (inside → outside):
1. Gói tới router: Src 10.0.0.10:51234 → Dst 8.8.8.8:443
2. Router kiểm tra: vào từ interface "inside", ra interface "outside"?  ✓
3. Src IP có khớp ACL/route-map của NAT không?  ✓
4. Tạo entry trong NAT table, chọn một port global còn trống
5. GHI LẠI header: Src 203.0.113.5:1024 → Dst 8.8.8.8:443
6. Gửi đi

ĐI VỀ (outside → inside):
7. Gói về: Src 8.8.8.8:443 → Dst 203.0.113.5:1024
8. Router tra NAT table theo (IP global, port global)
9. GHI LẠI header: Dst 10.0.0.10:51234
10. Chuyển vào trong
```

> 🔑 **Thứ tự quan trọng:** router **route trước, NAT sau** với gói đi ra;
> và **NAT trước, route sau** với gói đi vào. Chi tiết này giải thích vì sao
> ACL đôi khi khớp IP private, đôi khi khớp IP public — bạn gặp lại ở Phase 6.

### Timeout của NAT entry

| Loại | Mặc định |
|---|---|
| TCP | 24 giờ |
| UDP | 5 phút |
| ICMP | 1 phút |
| TCP sau khi thấy `RST`/`FIN` | 1 phút |

Bảng NAT đầy → kết nối mới bị từ chối. Trên thiết bị nhỏ, đây là nguyên nhân thật của
*"mạng chậm vào giờ cao điểm"*.

---

## 6. Packet Flow

**Kịch bản:** PC `10.0.0.10` truy cập `https://8.8.8.8`, router NAT ra `203.0.113.5`.

| Vị trí | Src IP:Port | Dst IP:Port | Ghi chú |
|---|---|---|---|
| PC → R1 | `10.0.0.10:51234` | `8.8.8.8:443` | IP private |
| **Trong R1** | — | — | Route ra Gi0/1, rồi **NAT** |
| R1 → Internet | `203.0.113.5:1024` | `8.8.8.8:443` | ⭐ **Src đã bị ghi lại** |
| Internet → R1 | `8.8.8.8:443` | `203.0.113.5:1024` | Server trả lời IP public |
| **Trong R1** | — | — | **NAT ngược** theo bảng |
| R1 → PC | `8.8.8.8:443` | `10.0.0.10:51234` | ⭐ **Dst đã bị ghi lại** |

**So với Lesson 01:** ở đó ta nói *"IP giữ nguyên suốt hành trình"*.
**NAT chính là ngoại lệ duy nhất của quy tắc đó** — và đó là lý do nó đáng một lesson riêng.

---

## 7. Real-world Example

🏭 **Port forwarding — mở server ra Internet**

Công ty có web server nội bộ `10.0.1.50:80`, muốn người ngoài vào được qua
`203.0.113.5:80`. Đây là **static NAT theo port**:

```cisco
R1(config)# ip nat inside source static tcp 10.0.1.50 80 203.0.113.5 80
```

Từ đây mọi gói tới `203.0.113.5:80` được chuyển thẳng vào `10.0.1.50:80`.

> ⚠️ Mở cổng ra Internet là quyết định bảo mật, không phải quyết định mạng.
> Luôn đi kèm ACL giới hạn nguồn và theo dõi log.

🏭 **Dual-WAN + NAT**

Có 2 đường Internet, mỗi đường một IP public. Phải có **2 cấu hình NAT**, mỗi cái gắn
với một interface outside, và route-map quyết định traffic nào đi đường nào.
Lỗi hay gặp: failover sang WAN2 nhưng NAT vẫn dùng IP của WAN1 → đứt hết.

🏭 **NAT và VPN đánh nhau**

Site-to-Site VPN giữa `10.0.0.0/24` và `10.1.0.0/24`. Nếu không loại trừ,
traffic đi VPN cũng bị NAT thành IP public → **tunnel không lên**.
Cách sửa: ACL của NAT phải `deny` traffic đi VPN **trước** khi `permit` phần còn lại.
Bạn gặp lại ở Phase 7.

---

## 8. Cisco CLI

```cisco
! ═══════ 1. Khai báo hướng — BẮT BUỘC, làm trước mọi thứ ═══════
R1(config)# interface GigabitEthernet0/0
R1(config-if)# ip nat inside
R1(config-if)# exit
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip nat outside
R1(config-if)# exit

! ═══════ 2. PAT — dùng luôn IP của interface outside (phổ biến nhất) ═══════
R1(config)# access-list 1 permit 10.0.0.0 0.0.0.255
R1(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload
!                                                                    ↑ PAT

! ═══════ 3. PAT với pool IP public ═══════
R1(config)# ip nat pool PUBLIC 203.0.113.5 203.0.113.6 netmask 255.255.255.252
R1(config)# ip nat inside source list 1 pool PUBLIC overload

! ═══════ 4. STATIC NAT — server ra Internet ═══════
R1(config)# ip nat inside source static 10.0.1.50 203.0.113.10

! Static NAT theo port (port forwarding)
R1(config)# ip nat inside source static tcp 10.0.1.50 80 203.0.113.5 80
R1(config)# ip nat inside source static tcp 10.0.1.50 443 203.0.113.5 443

! ═══════ 5. Loại trừ traffic đi VPN khỏi NAT ═══════
R1(config)# ip access-list extended NAT-ACL
R1(config-ext-nacl)# deny   ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255    ! traffic VPN
R1(config-ext-nacl)# permit ip 10.0.0.0 0.0.0.255 any                   ! còn lại thì NAT
R1(config)# ip nat inside source list NAT-ACL interface Gi0/1 overload

! ═══════ 6. Chỉnh timeout ═══════
R1(config)# ip nat translation timeout 3600
R1(config)# ip nat translation udp-timeout 300
```

| Lệnh / từ khoá | Làm gì | Lưu ý |
|---|---|---|
| `ip nat inside` / `ip nat outside` | Khai hướng | **Thiếu = NAT im lặng không chạy** |
| `overload` | Bật **PAT** | Không có từ này = dynamic NAT, hết IP là hết kết nối |
| `interface Gi0/1` trong lệnh NAT | Dùng IP của interface làm global | Tiện khi IP WAN là DHCP/PPPoE |
| `ip nat inside source static` | Ánh xạ cố định | Dùng cho server |
| `deny` trong NAT-ACL | **Loại trừ** khỏi NAT | Thứ tự dòng rất quan trọng |

> **Khác biệt platform:** cú pháp trên là IOS/IOS-XE. **NX-OS** cần `feature nat` và
> dùng `ip nat inside source list ... pool ... overload` với cú pháp hơi khác.
> ASA firewall dùng mô hình `object network` + `nat (inside,outside)` hoàn toàn khác.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat translations
Pro  Inside global        Inside local        Outside local      Outside global
tcp  203.0.113.5:1024     10.0.0.10:51234     8.8.8.8:443        8.8.8.8:443
tcp  203.0.113.5:1025     10.0.0.11:49800     8.8.8.8:443        8.8.8.8:443
udp  203.0.113.5:1026     10.0.0.10:53012     8.8.8.8:53         8.8.8.8:53
---  203.0.113.10         10.0.1.50           ---                ---
```

Dòng cuối không có port và không có outside → đó là **static NAT**.

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat statistics
Total active translations: 3 (1 static, 2 dynamic; 2 extended)
Outside interfaces: GigabitEthernet0/1
Inside interfaces:  GigabitEthernet0/0
Hits: 1523  Misses: 4
Dynamic mappings:
-- Inside Source
[Id: 1] access-list 1 interface GigabitEthernet0/1 refcount 2
```

**Đọc gì:**

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `Outside/Inside interfaces` | Đã khai hướng chưa | **Trống** → quên `ip nat inside/outside` |
| `Hits` | Số gói được NAT | Không tăng → ACL không khớp |
| `Misses` | Gói cần NAT nhưng chưa có entry | Tăng vọt → bảng NAT đầy |
| `Total active translations` | Số entry hiện có | Gần giới hạn thiết bị → nghẽn |

```cisco
! Xoá bảng NAT khi debug
R1# clear ip nat translation *

! Debug (CẨN THẬN trên production — tốn CPU)
R1# debug ip nat
R1# undebug all
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| PC không ra được Internet, ping gateway OK | **Quên `ip nat inside/outside`** | `show ip nat statistics` — xem dòng interfaces | Khai hướng cho cả 2 interface |
| `show ip nat translations` **rỗng** | ACL không khớp dải nội bộ | `show access-lists` | Sửa ACL / wildcard mask |
| `Hits: 0` dù có traffic | ACL sai, hoặc sai interface | `show ip nat statistics` | Kiểm tra lại cả 2 |
| Một số máy ra được, số khác không | Dynamic NAT hết IP trong pool | `show ip nat statistics` | Thêm `overload` → thành PAT |
| Ra Internet được nhưng **VPN không lên** | Traffic VPN bị NAT | `show ip nat translations` thấy IP peer | `deny` traffic VPN trong NAT-ACL |
| Server nội bộ không truy cập được từ ngoài | Thiếu static NAT, hoặc ACL chặn | `show ip nat translations` | Thêm static NAT + mở ACL |
| Giờ cao điểm mạng chậm, ngoài giờ bình thường | **Bảng NAT đầy** | `show ip nat statistics` | Giảm timeout UDP/ICMP; nâng thiết bị |
| Sau khi failover WAN, mất Internet | NAT vẫn trỏ interface WAN cũ | `show run \| include nat` | Cấu hình NAT cho cả 2 WAN + route-map |

---

## 11. LAB

🧪 **LAB 06 — PAT ra Internet + static NAT cho server** → [`../labs/lab06-pat-static-nat.md`](../labs/lab06-pat-static-nat.md)

Yêu cầu tối thiểu:

- LAN `10.0.0.0/24`, router NAT ra một IP public giả lập, PC ping được "Internet"
- `show ip nat translations` hiện đúng entry, chỉ ra port global khác nhau giữa 2 PC
- Thêm static NAT cho một server nội bộ, truy cập được từ phía ngoài
- **BREAK bắt buộc:** (1) xoá `ip nat inside`, (2) sửa ACL thành dải sai,
  (3) bỏ `overload` rồi cho 3 PC cùng ra Internet với pool chỉ 1 IP

## 12. Challenge

1. Hai PC cùng mở `https://8.8.8.8`. Bảng NAT có bao nhiêu entry? Chúng khác nhau ở cột nào?
2. Vì sao `ip nat inside source list 1 pool PUBLIC` (không có `overload`) mà pool chỉ có
   1 IP thì chỉ **một** máy ra Internet được tại một thời điểm?
3. Bạn cấu hình NAT đầy đủ nhưng `show ip nat translations` rỗng và `Hits: 0`.
   Nêu **3 nguyên nhân** theo thứ tự nên kiểm tra.
4. Vì sao nói "NAT không phải firewall"? Nêu một tình huống NAT **không** bảo vệ được bạn.

<details>
<summary>Đáp án</summary>

**1.** **2 entry**. Giống nhau: `Inside global` (cùng IP public), `Outside local`,
`Outside global` (`8.8.8.8:443`). Khác nhau: `Inside local` (IP:port của từng PC) và
**port của `Inside global`** — đây chính là thứ cho phép router phân biệt gói trả về.

**2.** Không có `overload` = **dynamic NAT thuần**, ánh xạ **1 private ↔ 1 public**.
Pool 1 IP → chỉ cấp được cho 1 máy; máy thứ hai không có IP nào để mượn → bị từ chối
cho tới khi entry đầu hết timeout. `overload` chính là từ khoá bật PAT (phân biệt bằng port),
cho phép hàng nghìn máy dùng chung 1 IP.

**3.** Thứ tự kiểm tra:

| # | Nguyên nhân | Lệnh |
|:---:|---|---|
| 1 | **Chưa khai `ip nat inside` / `ip nat outside`** — phổ biến nhất | `show ip nat statistics`, xem dòng `Inside/Outside interfaces` |
| 2 | **ACL không khớp** dải nội bộ (sai wildcard mask) | `show access-lists`, xem counter có tăng không |
| 3 | Gói **không đi qua** đúng cặp interface (route sai) | `show ip route`, `traceroute` |

**4.** Vì NAT **không kiểm tra nội dung, không lọc theo luật, không ghi log như firewall**.
Nó chỉ ghi lại header. Tình huống NAT không bảo vệ được:

- Máy nội bộ **chủ động** kết nối ra một server độc hại → NAT tạo entry, đường về mở toang.
  Malware hoạt động đúng theo cách này.
- Port forwarding: ngay khi bạn mở `203.0.113.5:3389` vào máy nội bộ, cả Internet
  có thể gõ cửa RDP đó. NAT không chặn gì cả.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 dải private · 3 kiểu NAT · 4 thuật ngữ inside/outside local/global | ⬜ |
| **L2** Explain | Giải thích PAT phân biệt kết nối bằng gì, liên hệ socket | ⬜ |
| **L3** Configure | Cấu hình PAT + static NAT, verify bằng `show ip nat translations` | ⬜ |
| **L4** Troubleshoot | NAT không chạy, `Hits: 0` → nêu thứ tự 3 bước kiểm tra | ⬜ |
| **L5** Design | Thiết kế NAT cho công ty dual-WAN có VPN site-to-site | ⬜ |

## 14. Summary

**Key concepts**

- Private RFC 1918: `10/8` · `172.16/12` · `192.168/16` — **không route được trên Internet**
- **Static NAT** cho server · **Dynamic NAT** hiếm dùng · **PAT (`overload`)** cho 99% trường hợp
- ⭐ PAT phân biệt bằng **source port** — chính là socket 4 giá trị của Lesson 06
- `Inside Local` = IP thật bên trong · `Inside Global` = sau khi NAT
- ⭐ **NAT là ngoại lệ duy nhất của quy tắc "IP giữ nguyên suốt hành trình"**
- ⚠️ **NAT không phải firewall** — nó không lọc, không kiểm tra nội dung
- Traffic đi VPN phải được **loại trừ** khỏi NAT

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ip nat inside` / `ip nat outside` | **Luôn làm đầu tiên** |
| `ip nat inside source list 1 interface Gi0/1 overload` | PAT cơ bản |
| `ip nat inside source static <local> <global>` | Server ra Internet |
| `show ip nat translations` | Xem ai đang được NAT thành gì |
| `show ip nat statistics` | Hits/Misses, đã khai hướng chưa |
| `clear ip nat translation *` | Reset khi debug |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `ip nat inside/outside` | NAT **im lặng không chạy**, không báo lỗi |
| Quên `overload` | Chỉ một máy ra được Internet |
| ACL sai wildcard mask | `Hits: 0`, bảng NAT rỗng |
| Không loại trừ traffic VPN | Tunnel không lên |
| "Có NAT rồi nên an toàn" | NAT không phải firewall |
| Failover WAN mà không đổi NAT | Mất Internet sau khi chuyển đường |

## 15. Homework + cập nhật PROGRESS

1. Trên router nhà bạn: tìm IP public (`curl ifconfig.me` hoặc tra Google "what is my ip"),
   so với IP máy bạn (`ipconfig`). Giải thích chênh lệch.
2. Mở 3 tab trình duyệt tới cùng một trang. Giải thích vì sao server phân biệt được 3 tab
   dù chúng đi ra cùng một IP public.
3. Làm LAB 06 với đủ 3 lỗi BREAK.

```markdown
- [YYYY-MM-DD] Lesson 09 — NAT: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 3 kiểu NAT, 4 thuật ngữ, cú pháp PAT, dải private |
| 🔧 **Engineer** | Loại trừ traffic VPN; static NAT cho server; đọc bảng NAT để truy vết |
| 🏭 **Production** | Bảng NAT đầy = "chậm giờ cao điểm"; NAT ≠ firewall; dual-WAN cần 2 cấu hình NAT |

### 🔗 Liên kết

- ⬅️ [Lesson 08 — DNS & DHCP](./lesson-08-dns-va-dhcp.md)
- ➡️ [Lesson 10 — IPv6 giới thiệu](./lesson-10-ipv6-gioi-thieu.md)
- 🔜 Học sâu ở [Phase 3 — Services](../03-services/README.md)
- 🧮 [`cheatsheets/subnetting.md`](../cheatsheets/subnetting.md#6-dải-ip-private--đặc-biệt)
