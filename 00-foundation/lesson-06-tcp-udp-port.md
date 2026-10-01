# LESSON 06 — TCP vs UDP · Port · 3-way Handshake ⭐

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 01](./lesson-01-osi-va-tcp-ip.md), [Lesson 05](./lesson-05-gateway-arp-icmp.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Phân biệt TCP/UDP không bằng định nghĩa mà bằng **khi nào dùng cái nào**
- [ ] Mô tả 3-way handshake và 4-way close, nói rõ seq/ack đổi thế nào
- [ ] Giải thích **port để làm gì** — và vì sao một máy chạy được nhiều service
- [ ] Đọc TCP flag trong Wireshark, phân biệt *drop* và *reject*
- [ ] Thuộc bảng port cần nhớ

## 2. Prerequisite

- L4 = Transport, PDU là segment *(Lesson 01)*
- ICMP là L3, không có port *(Lesson 05)*

---

## 3. Concept

### Port — con số phân biệt ứng dụng

IP đưa gói **tới đúng máy**. Port đưa dữ liệu **tới đúng chương trình** trên máy đó.

```text
Server 10.0.0.50 chạy đồng thời:
  :80    → web server
  :443   → web server (HTTPS)
  :22    → SSH
  :3306  → MySQL

Không có port → một máy chỉ chạy được một dịch vụ.
```

Port là số **16 bit** → `0` – `65535`.

| Dải | Tên | Dùng cho |
|---|---|---|
| `0 – 1023` | **Well-known** | Dịch vụ chuẩn (80, 443, 22, 53…). Trên Linux cần quyền root để mở |
| `1024 – 49151` | Registered | Ứng dụng đăng ký (3306 MySQL, 8080…) |
| `49152 – 65535` | **Ephemeral** | Port tạm máy client tự chọn khi mở kết nối |

### Socket — cặp 4 giá trị

Một kết nối được định danh duy nhất bởi:

```text
(Source IP, Source Port, Destination IP, Destination Port)

192.168.1.10 : 51234   →   10.0.0.50 : 443
192.168.1.10 : 51235   →   10.0.0.50 : 443    ← kết nối KHÁC, cùng máy, cùng server
```

> 💡 Đây là cách một trình duyệt mở 6 kết nối song song tới cùng một web server:
> **source port khác nhau**. Và đó cũng chính là cơ chế **PAT** dùng để nhiều máy
> dùng chung một IP public (Lesson 09).

### TCP vs UDP

| | **TCP** | **UDP** |
|---|---|---|
| Kiểu | Connection-oriented | Connectionless |
| Thiết lập | **3-way handshake** | Gửi thẳng, không chào hỏi |
| Tin cậy | ACK, retransmit, sắp đúng thứ tự | Không đảm bảo gì |
| Kiểm soát luồng | Có (window size) | Không |
| Header | **20 byte** (có option thì hơn) | **8 byte** |
| Tốc độ | Chậm hơn, overhead cao | Nhanh, nhẹ |
| Dùng cho | Web, mail, file, SSH, BGP | DNS, DHCP, NTP, SNMP, VoIP, streaming, game |

### Header — nhìn vào là hiểu vì sao

```text
TCP header (20 byte tối thiểu)
┌───────────────┬───────────────┐
│  Source Port  │   Dest Port   │   ← 4 byte
├───────────────┴───────────────┤
│       Sequence Number         │   ← 4 byte  (đánh số byte dữ liệu)
├───────────────────────────────┤
│    Acknowledgment Number      │   ← 4 byte  (đã nhận tới đâu)
├──────┬────────┬───────────────┤
│ Offs │ Flags  │  Window Size  │   ← flow control
├──────┴────────┼───────────────┤
│   Checksum    │ Urgent Ptr    │
└───────────────┴───────────────┘

UDP header (8 byte)
┌───────────────┬───────────────┐
│  Source Port  │   Dest Port   │
├───────────────┼───────────────┤
│    Length     │   Checksum    │
└───────────────┴───────────────┘
```

> 🔑 **12 byte chênh lệch đó chính là "độ tin cậy".** Seq, Ack, Window — ba thứ cho phép
> TCP phát hiện mất gói, gửi lại, và điều tiết tốc độ. UDP không có → nhẹ hơn nhưng không biết gì.

### TCP Flags

| Flag | Nghĩa | Thấy khi |
|---|---|---|
| `SYN` | Synchronize — mở kết nối | Bước 1, 2 của handshake |
| `ACK` | Acknowledge — xác nhận | Hầu hết mọi gói sau bước 1 |
| `FIN` | Finish — đóng lịch sự | Kết thúc bình thường |
| `RST` | **Reset** — đóng đột ngột | **Bị từ chối** — không có service, hoặc firewall reject |
| `PSH` | Push — đẩy lên ứng dụng ngay | Dữ liệu tương tác (SSH gõ phím) |
| `URG` | Urgent | Hiếm gặp |

---

## 4. Why? — tại sao cần cả hai

> **Nếu chỉ có TCP thì sao?**

| Vấn đề | Giải thích |
|---|---|
| **Gọi thoại / video sẽ tệ đi** | TCP gửi lại gói mất. Nhưng với thoại, một gói âm thanh đến **muộn 2 giây** còn vô dụng hơn là mất hẳn. Thà nghe rè 0.02 giây còn hơn nghe trễ. |
| **DNS sẽ chậm gấp 3** | Một truy vấn DNS chỉ cần 1 gói hỏi + 1 gói đáp. Dùng TCP phải handshake 3 bước trước → 3 lần round-trip cho một việc nhỏ. |
| **DHCP không chạy được** | Client chưa có IP thì không thiết lập nổi kết nối TCP. |

> **Nếu chỉ có UDP thì sao?**

Tải một file 1 GB, mất 1 gói ở giữa → file hỏng, không ai biết, không ai sửa.
Mọi ứng dụng sẽ phải **tự viết lại cơ chế tin cậy** — tức là tự viết lại TCP, mỗi nơi một kiểu.

**Kết luận:**

> **TCP khi dữ liệu phải ĐÚNG. UDP khi dữ liệu phải ĐÚNG GIỜ.**

---

## 5. How does it work?

### 3-way handshake

```text
Client                              Server
   │                                   │
   │────── SYN, Seq=x ────────────────▶│   "Tôi muốn kết nối, tôi đánh số từ x"
   │                                   │
   │◀───── SYN-ACK, Seq=y, Ack=x+1 ────│   "OK, tôi đánh số từ y, đã nhận x"
   │                                   │
   │────── ACK, Seq=x+1, Ack=y+1 ─────▶│   "Xác nhận"
   │                                   │
   │════════ ĐÃ KẾT NỐI ═══════════════│
```

Vì sao phải **3** bước chứ không phải 2: cả hai bên đều cần (a) công bố số thứ tự ban đầu
của mình, và (b) được bên kia xác nhận. Hai bước chỉ đủ cho một chiều.

### 4-way close

```text
Client ───── FIN ─────▶ Server      "Tôi gửi xong rồi"
Client ◀──── ACK ────── Server      "Biết rồi"
Client ◀──── FIN ────── Server      "Tôi cũng gửi xong"
Client ───── ACK ─────▶ Server      "Biết rồi"
```

Bốn bước vì TCP là **song công**: mỗi chiều đóng độc lập. Một bên có thể đã hết dữ liệu
trong khi bên kia vẫn còn gửi.

### Sliding window — kiểm soát luồng

`Window Size` trong header nói: *"tôi còn chỗ nhận bao nhiêu byte nữa"*.
Bên gửi không được gửi quá con số đó khi chưa nhận ACK.

```text
Window lớn  → gửi nhiều, nhanh, nhưng mất gói thì phải gửi lại nhiều
Window nhỏ  → an toàn, chậm
Window = 0  → "dừng lại, tôi đang quá tải"
```

> 🔧 Thấy `TCP Window Full` hoặc `TCP ZeroWindow` trong Wireshark = **bên nhận đang nghẽn**,
> không phải mạng chậm. Đây là chỗ phân biệt "chậm do mạng" và "chậm do server".

---

## 6. Packet Flow

**Kịch bản:** PC mở `https://10.0.0.50`

| # | Hướng | L4 | Chi tiết |
|:---:|---|---|---|
| 1 | PC → Server | TCP | `SYN`, Src port **51234**, Dst port **443** |
| 2 | Server → PC | TCP | `SYN, ACK`, Src 443, Dst 51234 |
| 3 | PC → Server | TCP | `ACK` — kết nối mở |
| 4 | PC → Server | TLS | Client Hello *(bên trong TCP)* |
| … | | | trao đổi dữ liệu |
| n | PC → Server | TCP | `FIN` → `ACK` → `FIN` → `ACK` |

**Điểm đáng chú ý:** source port `51234` do PC **tự chọn ngẫu nhiên** trong dải ephemeral.
Server trả lời về đúng port đó. Nếu PC mở tab thứ hai, nó chọn port khác —
cùng IP, cùng server, cùng port 443, nhưng là **kết nối riêng biệt**.

---

## 7. Real-world Example

🏭 **Đọc triệu chứng từ TCP flag:**

| Thấy gì | Kết luận | Hành động |
|---|---|---|
| `SYN` rồi im lặng, lặp lại 3 lần, timeout | Firewall **DROP** (im lặng) | Kiểm tra ACL/firewall giữa đường |
| `SYN` → `RST` ngay lập tức | **Không có service nghe** ở port đó, hoặc firewall **REJECT** | Kiểm tra service có chạy không |
| Handshake OK rồi đứt giữa chừng | Ứng dụng lỗi, hoặc timeout session | Xem log ứng dụng |
| Nhiều `TCP Retransmission` | **Mất gói** trên đường | Kiểm tra lỗi interface, băng thông |
| `TCP ZeroWindow` | **Bên nhận quá tải** | Vấn đề ở server, không phải mạng |

> 🔑 Phân biệt **drop** và **reject** là kỹ năng rất thực tế:
> *drop* = treo đến khi timeout (~30 giây, user kêu "web load mãi");
> *reject* = báo lỗi ngay (user kêu "không kết nối được"). Hai triệu chứng, hai hướng điều tra.

🏭 **Vì sao VoIP dùng UDP:** gói thoại đến muộn là rác. Codec thà nội suy một khoảng trống
20 ms còn hơn chờ gói cũ. Chất lượng thoại phụ thuộc **jitter** và **độ trễ**, không phụ thuộc
tỷ lệ mất gói nhỏ.

---

## 8. Cisco CLI

```cisco
! ───── Xem kết nối TCP đang có trên thiết bị ─────
R1# show tcp brief
R1# show tcp brief all

! ───── Kiểm tra một port có mở không (từ router) ─────
R1# telnet 10.0.0.50 443
! Kết nối được  → port mở
! "Connection refused"       → có máy, không có service  (RST)
! "Destination unreachable"  → không tới được            (ICMP)
! Treo rồi timeout           → bị DROP im lặng

! ───── ACL theo port (xem kỹ ở Lesson 36) ─────
R1(config)# access-list 110 permit tcp any host 10.0.0.50 eq 443
R1(config)# access-list 110 permit udp any any eq 53
R1(config)# access-list 110 deny   ip any any log

! ───── Xem socket đang mở trên chính thiết bị ─────
R1# show control-plane host open-ports
```

| Lệnh | Làm gì | Ghi chú |
|---|---|---|
| `show tcp brief` | Liệt kê kết nối TCP của router | Chủ yếu là SSH/BGP |
| `telnet <ip> <port>` | **Test port** nhanh nhất, không cần cài gì | Dùng cả trên router lẫn PC |
| `eq 443` trong ACL | Khớp port | `eq` = bằng, `gt` = lớn hơn, `range` = khoảng |

**Trên máy tính:**

```powershell
# Windows
netstat -ano | findstr :443
Test-NetConnection 10.0.0.50 -Port 443

# Linux
ss -tlnp
nc -zv 10.0.0.50 443
```

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show tcp brief
TCB       Local Address          Foreign Address        (state)
6B2F1C0   192.168.1.1.22         192.168.1.10.51234     ESTAB
6B2F3A8   192.168.1.1.179        10.0.0.2.49152         ESTAB
```

| Cột | Ý nghĩa |
|---|---|
| `Local Address` | `IP.port` của router — `.22` = SSH, `.179` = BGP |
| `Foreign Address` | `IP.port` của phía bên kia — port cao = ephemeral |
| `(state)` | `ESTAB` = đang kết nối; `LISTEN` = đang chờ; `TIMEWAIT` = vừa đóng |

**Trong Wireshark:**

```text
# dạng điển hình — tự bắt trên máy bạn
No.  Source        Destination   Proto  Info
1    192.168.1.10  10.0.0.50     TCP    51234 → 443 [SYN] Seq=0 Win=64240
2    10.0.0.50     192.168.1.10  TCP    443 → 51234 [SYN, ACK] Seq=0 Ack=1
3    192.168.1.10  10.0.0.50     TCP    51234 → 443 [ACK] Seq=1 Ack=1
```

Filter hữu ích:

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0     chỉ gói mở kết nối
tcp.flags.reset == 1                          bị từ chối
tcp.analysis.retransmission                   mất gói
tcp.analysis.zero_window                      bên nhận nghẽn
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Ping được, web không vào | Port bị chặn, hoặc service chết | `telnet <ip> 443` | Mở ACL / khởi động service |
| "Connection refused" | Service không chạy → `RST` | `ss -tlnp` trên server | Bật service |
| Web "load mãi" rồi timeout | Firewall **drop im lặng** | Wireshark: thấy `SYN` lặp lại | Mở firewall |
| Tải file chậm, ping bình thường | Mất gói → retransmit | `tcp.analysis.retransmission` | Kiểm tra lỗi interface |
| Chậm nhưng không mất gói | `ZeroWindow` — server nghẽn | `tcp.analysis.zero_window` | Vấn đề ở server |
| DNS chậm bất thường | UDP bị drop, fallback sang TCP | Wireshark lọc `dns` | Kiểm tra firewall UDP/53 |
| Ứng dụng đứt sau vài phút không dùng | Firewall hết session timeout | Log firewall | Bật TCP keepalive |

---

## 11. LAB

🧪 **[LAB 03 — TCP 3-way handshake vs UDP](../labs/lab03-tcp-udp-wireshark.md)**

## 12. Challenge

1. Một trình duyệt mở 6 kết nối tới cùng `10.0.0.50:443`. Chúng khác nhau ở đâu?
   Server phân biệt bằng cách nào?
2. Vì sao DNS dùng **cả** UDP và TCP? Khi nào chuyển sang TCP?
3. Bạn `telnet 10.0.0.50 443` và bị treo 30 giây rồi timeout. Bạn `telnet 10.0.0.50 80`
   thì "Connection refused" ngay. **Hai kết quả này nói lên điều gì khác nhau?**
4. Vì sao đóng TCP cần 4 bước mà mở chỉ cần 3?

<details>
<summary>Đáp án</summary>

**1.** Khác nhau ở **source port** (ephemeral, mỗi kết nối một số).
Server phân biệt bằng **socket 4 giá trị** `(SrcIP, SrcPort, DstIP, DstPort)` — ba giá trị
giống nhau, chỉ SrcPort khác là đủ để thành kết nối riêng.

**2.** UDP/53 cho truy vấn thường — nhanh, 1 gói đi 1 gói về. Chuyển sang **TCP/53** khi:
(a) câu trả lời **vượt 512 byte** (cờ TC — truncated — được bật), hoặc (b) **zone transfer**
giữa các DNS server. Chặn nhầm TCP/53 ở firewall gây lỗi rất khó tìm vì phần lớn truy vấn vẫn chạy.

**3.** Hai hành vi firewall khác nhau:
| Kết quả | Nghĩa |
|---|---|
| Treo rồi timeout (port 443) | Gói `SYN` bị **DROP im lặng** — thường là firewall giữa đường |
| "Connection refused" ngay (port 80) | Nhận được `RST` → gói **tới được máy đích**, nhưng **không có service** nghe ở port 80 |

Suy ra: máy đích **tồn tại và tới được**; vấn đề ở port 443 nằm trên đường đi, không phải ở máy.

**4.** Vì TCP **song công** — hai chiều độc lập. Mở kết nối có thể gộp `SYN` và `ACK` của
server vào **một gói** (`SYN-ACK`) nên chỉ cần 3. Khi đóng, bên nhận `FIN` có thể **vẫn còn
dữ liệu chưa gửi xong**, nên nó `ACK` trước, gửi nốt, rồi mới `FIN` sau → không gộp được.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 bước handshake · header TCP/UDP bao nhiêu byte · port 22/53/80/443/67-68 | ⬜ |
| **L2** Explain | Giải thích vì sao VoIP dùng UDP cho người không biết IT | ⬜ |
| **L3** Configure | Viết ACL cho phép HTTPS và DNS, chặn còn lại | ⬜ |
| **L4** Troubleshoot | Phân biệt drop và reject từ triệu chứng, nêu hướng điều tra mỗi loại | ⬜ |
| **L5** Design | Chọn TCP hay UDP cho 5 ứng dụng cho trước, giải thích từng cái | ⬜ |

## 14. Summary

**Key concepts**

- Port 16 bit: well-known `0–1023`, registered, **ephemeral `49152–65535`**
- Socket = `(SrcIP, SrcPort, DstIP, DstPort)` — định danh duy nhất một kết nối
- TCP: 3-way handshake `SYN → SYN-ACK → ACK`, đóng 4 bước
- TCP header **20 byte**, UDP header **8 byte** — chênh lệch chính là độ tin cậy
- ⭐ **TCP khi dữ liệu phải ĐÚNG, UDP khi dữ liệu phải ĐÚNG GIỜ**
- `RST` ngay = không có service / reject · im lặng rồi timeout = **drop**
- `ZeroWindow` = bên nhận nghẽn, **không phải** mạng chậm

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `telnet <ip> <port>` | Test port nhanh nhất, không cần cài gì |
| `show tcp brief` | Kết nối TCP trên thiết bị Cisco |
| `netstat -ano` / `ss -tlnp` | Xem port đang mở trên máy |
| `tcp.flags.syn==1 && tcp.flags.ack==0` | Lọc gói mở kết nối trong Wireshark |

**Common mistakes**

| Sai | Đúng |
|---|---|
| "DNS chỉ dùng UDP" | Dùng **cả hai** — TCP khi reply > 512 byte hoặc zone transfer |
| "ICMP có port" | ICMP là **L3**, không có port |
| Nhầm drop với reject | Treo = drop · `RST` ngay = reject |
| "Chậm là do mạng" | `ZeroWindow` chỉ ra bên nhận nghẽn |
| Nghĩ 6 tab trình duyệt dùng chung 1 kết nối | Mỗi kết nối một **source port** riêng |

## 15. Homework + cập nhật PROGRESS

1. Wireshark: mở một trang web, lọc `tcp.flags.syn==1 && tcp.flags.ack==0`.
   Đếm trang đó mở bao nhiêu kết nối TCP.
2. `telnet google.com 443` và `telnet google.com 12345` — so sánh hai kết quả, giải thích.
3. `netstat -ano` (Windows) — tìm 3 port đang LISTEN trên máy bạn, tra xem service nào.
4. Học thuộc bảng port trong [`cheatsheets/ports-va-protocols.md`](../cheatsheets/ports-va-protocols.md#1-port-phải-thuộc-lòng).

```markdown
- [YYYY-MM-DD] Lesson 06 — TCP/UDP & Port: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 3-way handshake, header size, dải port, TCP vs UDP dùng cho gì |
| 🔧 **Engineer** | `telnet <ip> <port>` để test; đọc flag để phân biệt drop/reject |
| 🏭 **Production** | `ZeroWindow` = server nghẽn; retransmission cao = lỗi vật lý; firewall timeout làm đứt session dài |

### 🔗 Liên kết

- ⬅️ [Lesson 05 — Gateway, ARP, ICMP](./lesson-05-gateway-arp-icmp.md)
- ➡️ [Lesson 07 — VLSM nâng cao](./lesson-07-vlsm-va-ip-plan.md)
- 🔌 [`cheatsheets/ports-va-protocols.md`](../cheatsheets/ports-va-protocols.md)
- 🦈 [`cheatsheets/wireshark.md`](../cheatsheets/wireshark.md)
