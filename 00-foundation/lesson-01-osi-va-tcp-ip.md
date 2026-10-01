# LESSON 01 — Network là gì · Mô hình OSI & TCP/IP

> 📌 **Đây là lesson mẫu.** Nó cho thấy một lesson "đạt chuẩn" của repo này trông như thế nào.
> Các lesson sau bạn tự viết từ [`templates/LESSON_TEMPLATE.md`](../templates/LESSON_TEMPLATE.md)
> trong lúc học với AI mentor.

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | Không |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích được network là gì bằng một câu, không dùng từ chuyên ngành
- [ ] Kể được 7 tầng OSI từ dưới lên và **dùng được** chúng để khoanh vùng lỗi
- [ ] Nói đúng PDU của từng tầng (bit / frame / packet / segment)
- [ ] Giải thích encapsulation bằng hình ảnh "bỏ thư vào phong bì"
- [ ] Ánh xạ được OSI ↔ TCP/IP và biết vì sao thực tế dùng TCP/IP

## 2. Prerequisite

Không. Đây là lesson đầu tiên.

---

## 3. Concept

**Network** = hai hoặc nhiều thiết bị **trao đổi dữ liệu** với nhau theo một bộ quy tắc chung.

Chỉ cần ba thứ:

| Thành phần | Vai trò | Ví dụ |
|---|---|---|
| **Thiết bị đầu cuối** | Nơi sinh ra và tiêu thụ dữ liệu | PC, điện thoại, server |
| **Môi trường truyền** | Đường dữ liệu chạy qua | Cáp đồng, cáp quang, sóng vô tuyến |
| **Quy tắc (protocol)** | Thoả thuận để hai bên hiểu nhau | TCP/IP, Ethernet, HTTP |

Phân loại theo phạm vi:

| Loại | Phạm vi | Ai sở hữu đường truyền |
|---|---|---|
| **LAN** | Một toà nhà, một văn phòng | Bạn |
| **WAN** | Giữa các thành phố, quốc gia | Nhà cung cấp dịch vụ |
| **MAN** | Trong một thành phố | Thường là ISP |

### Mô hình OSI — 7 tầng

| # | Tầng | PDU | Thiết bị tiêu biểu | Ví dụ giao thức |
|:---:|---|---|---|---|
| **7** | Application | Data | — | HTTP, DNS, DHCP, SMTP |
| **6** | Presentation | Data | — | TLS/SSL, mã hoá, nén, JPEG |
| **5** | Session | Data | — | Quản lý phiên làm việc |
| **4** | Transport | **Segment** / Datagram | Firewall L4 | TCP, UDP, **port** |
| **3** | Network | **Packet** | **Router**, L3 switch | **IP**, ICMP, OSPF |
| **2** | Data Link | **Frame** | **Switch**, NIC | Ethernet, **MAC**, 802.1Q |
| **1** | Physical | **Bit** | Hub, cáp, repeater | Tín hiệu điện/quang |

**Cách nhớ (dưới lên):** *Please Do Not Throw Sausage Pizza Away.*

### Mô hình TCP/IP — cái thực tế đang chạy

| TCP/IP (4 tầng) | Gộp từ OSI |
|---|---|
| Application | 7 + 6 + 5 |
| Transport | 4 |
| Internet | 3 |
| Network Access | 2 + 1 |

---

## 4. Why? — tại sao cần mô hình phân tầng

> **Câu hỏi phải trả lời: nếu không có nó thì sao?**

Nếu không phân tầng, mỗi ứng dụng phải tự lo **mọi thứ**: từ mã hoá tín hiệu điện trên cáp,
tới tìm đường qua Internet, tới mã hoá dữ liệu. Đổi từ cáp đồng sang Wi-Fi là phải viết lại
trình duyệt.

Phân tầng mang lại 3 thứ:

| Lợi ích | Nghĩa thực tế |
|---|---|
| **Thay thế độc lập** | Đổi Wi-Fi ↔ cáp (L1/L2) mà HTTP (L7) không cần biết |
| **Chia việc** | Hãng làm NIC lo L1–2; hãng làm router lo L3; lập trình viên lo L7 |
| **Khoanh vùng lỗi** ⭐ | Đây mới là giá trị bạn dùng hằng ngày |

> 🔧 **Giá trị thật của OSI với người đi làm không phải để đọc vanh vách 7 tầng.**
> Nó là **bộ khung để hỏi đúng câu hỏi theo thứ tự**:
> *Cáp có cắm không (L1) → port có up không (L2) → IP đúng chưa (L3) → port có mở không (L4)
> → service có chạy không (L7)?*
>
> Người mới hay nhảy thẳng lên L7 ("chắc server lỗi") và mất 2 tiếng cho một sợi cáp lỏng.

---

## 5. How does it work? — Encapsulation

Dữ liệu đi **xuống** từng tầng ở máy gửi, mỗi tầng **bọc thêm một lớp header**:

```text
Máy GỬI — Encapsulation (đi xuống)

L7  [ Data ]
L4  [ TCP header │ Data ]                           → Segment
L3  [ IP header  │ TCP header │ Data ]              → Packet
L2  [ Eth header │ IP │ TCP │ Data │ Eth trailer ]  → Frame
L1  101000110101110010100011...                     → Bit
```

Ở máy nhận, quá trình ngược lại — **decapsulation**: mỗi tầng bóc header của mình rồi đưa
phần còn lại lên tầng trên.

### Mỗi header chứa gì, để làm gì

| Tầng | Header chứa | Trả lời câu hỏi |
|---|---|---|
| L4 TCP/UDP | Source port, Dest port, seq, flag | *Giao cho **ứng dụng nào** trên máy đó?* |
| L3 IP | Source IP, Dest IP, TTL, protocol | *Đi tới **máy nào** trên toàn thế giới?* |
| L2 Ethernet | Source MAC, Dest MAC, EtherType | *Chặng tiếp theo là **thiết bị nào** trên dây này?* |

> 💡 Hình ảnh dễ nhớ: **bỏ thư vào phong bì**.
> L7 là nội dung thư. L4 ghi "gửi cho phòng Kế toán" (port). L3 ghi địa chỉ nhà (IP).
> L2 ghi "đưa cho bác bảo vệ ở cổng" (MAC của hop kế tiếp).
> Địa chỉ nhà **không đổi** suốt hành trình; người cầm thư thì **đổi liên tục**.

---

## 6. Packet Flow

PC1 (`192.168.1.10`) mở web tới Server (`10.0.0.50`), đi qua R1 và R2.

| Hop | Src MAC | Dst MAC | Src IP | Dst IP | TTL | Ghi chú |
|---|---|---|---|---|:---:|---|
| PC1 → SW1 | `PC1` | `R1-G0/0` | 192.168.1.10 | 10.0.0.50 | 128 | PC ARP tìm MAC **gateway**, không phải MAC server |
| SW1 → R1 | `PC1` | `R1-G0/0` | 192.168.1.10 | 10.0.0.50 | 128 | Switch **không đổi gì** — nó chỉ chuyển frame |
| R1 → R2 | `R1-G0/1` | `R2-G0/0` | 192.168.1.10 | 10.0.0.50 | **127** | R1 **viết lại MAC**, giảm TTL |
| R2 → Server | `R2-G0/1` | `Server` | 192.168.1.10 | 10.0.0.50 | **126** | MAC cuối cùng mới là MAC server |

### Ba điều rút ra — đây là cốt lõi của cả Phase 0

1. **IP nguồn/đích giữ nguyên suốt hành trình** (trừ khi có NAT).
2. **MAC nguồn/đích bị viết lại ở mỗi router** — MAC chỉ có ý nghĩa *trong một đoạn mạng*.
3. **Switch không xuất hiện trong bảng trên** vì nó không sửa gì ở L2 header — nó chỉ đọc
   destination MAC và chuyển đi. Đó là lý do switch "trong suốt" với L3.

> ⚠️ Người mới hay nghĩ "PC1 phải biết MAC của Server để gửi". **Sai.**
> PC1 chỉ cần MAC của **default gateway**. Nó thậm chí không biết Server tồn tại ở đâu.

---

## 7. Real-world Example

🏭 Một sự cố thật rất hay gặp: *"Nhân viên không vào được ứng dụng nội bộ."*

Áp dụng OSI từ dưới lên:

| Tầng | Kiểm tra | Lệnh |
|:---:|---|---|
| L1 | Đèn port có sáng? Cáp cắm đúng? | `show interfaces status` |
| L2 | Port có đúng VLAN? Switch có học MAC của máy đó? | `show vlan brief`, `show mac address-table` |
| L3 | Máy có IP đúng? Ping được gateway? Có route tới server? | `ipconfig`, `ping`, `show ip route` |
| L4 | Port ứng dụng có mở? ACL có chặn? | `telnet <ip> <port>`, `show access-lists` |
| L7 | Service có chạy? DNS phân giải đúng? | `nslookup`, kiểm tra trên server |

Đi đúng thứ tự này, **80% sự cố kết thúc ở L1–L3** trong vòng 10 phút.
Nhảy thẳng lên L7 thì 10 phút đó thành 2 tiếng.

---

## 8. Cisco CLI

Lesson này chưa cấu hình gì — nhưng làm quen 3 lệnh định vị:

```cisco
show version                  ! thiết bị gì, IOS phiên bản nào, uptime
show ip interface brief       ! interface nào có IP, interface nào up
show cdp neighbors            ! đang nối với thiết bị nào, qua port nào
```

| Lệnh | Kiểm tra gì | Khác biệt platform |
|---|---|---|
| `show version` | Model, IOS version, uptime, register | Giống nhau IOS/IOS-XE; NX-OS format khác |
| `show ip interface brief` | IP + status/protocol của mọi interface | Giống nhau |
| `show cdp neighbors` | Láng giềng Cisco | NX-OS: cần `feature cdp`; thiết bị không-Cisco dùng `show lldp neighbors` |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show cdp neighbors
Device ID    Local Intrfce    Holdtme   Capability   Platform   Port ID
SW1          Gig 0/0           145        S I        WS-C2960   Gig 0/1
R2           Gig 0/1           132        R B        ISR4331    Gig 0/0
```

**Đọc gì trong output này:**

| Field | Ý nghĩa | Bất thường trông như thế nào |
|---|---|---|
| `Device ID` | Hostname của láng giềng | Tên lạ → có thiết bị không mong muốn trong mạng |
| `Local Intrfce` | Port **của tôi** đang nối | Khác với sơ đồ → đấu nhầm dây |
| `Capability` | `R`=Router, `S`=Switch, `I`=IGMP, `B`=Bridge | Switch xuất hiện ở port lẽ ra nối PC |
| `Holdtme` | Giây còn lại trước khi coi là mất | Giảm dần không reset → link chập chờn |

> 🏭 **Production:** CDP tiện nhưng rò rỉ thông tin thiết bị. Trên port nối ra ngoài
> hoặc nối tới người dùng, thường tắt bằng `no cdp enable`.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Nếu đúng thì sửa |
|---|---|---|---|
| Không thấy láng giềng nào | CDP bị tắt, hoặc link down | `show cdp`, `show ip int brief` | `cdp run` / `cdp enable`, kiểm tra cáp |
| Thấy láng giềng ở port không mong đợi | Đấu nhầm dây | `show cdp neighbors detail` | Đấu lại theo sơ đồ |
| Láng giềng là thiết bị non-Cisco | CDP là của Cisco | `show lldp neighbors` | Bật `lldp run` |

---

## 11. LAB

🧪 Lesson này chưa cần lab thiết bị. Thay vào đó, làm **bài tập giấy**:

Vẽ lại bằng tay đường đi của gói tin từ laptop của bạn tới `google.com`,
ghi rõ ở mỗi hop: Src/Dst MAC, Src/Dst IP, TTL. Kiểm chứng bằng:

```powershell
arp -a                 # MAC của gateway
tracert google.com     # số hop thật
```

## 12. Challenge

> Không xem đáp án trước khi tự trả lời.

1. PC1 và PC2 **cùng subnet**, nối qua 1 switch. Bảng packet flow sẽ khác bảng ở §6 thế nào?
2. Nếu ai đó set TTL = 1 ở PC1, gói tin đi được tới đâu? Bạn sẽ thấy gì khi `ping`?
3. Vì sao switch **không** giảm TTL, còn router thì có?

<details>
<summary>Gợi ý (mở sau khi đã nghĩ ít nhất 5 phút)</summary>

1. Chỉ **một dòng** — PC1 ARP trực tiếp tìm MAC của PC2, không qua gateway. MAC đích là MAC PC2 ngay từ đầu, TTL không đổi.
2. Tới router đầu tiên là TTL về 0 → router drop và trả `ICMP Time Exceeded`. Đây chính là **cơ chế của traceroute**.
3. Vì TTL nằm trong **IP header (L3)**. Switch là thiết bị L2 — nó không mở IP header ra đọc, nên không chạm vào TTL.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 7 tầng OSI từ dưới lên · PDU của L2/L3/L4 · cái gì đổi mỗi hop | ⬜ |
| **L2** Explain | Giải thích encapsulation cho người không biết IT trong 2 phút | ⬜ |
| **L3** Configure | *(chưa áp dụng ở lesson này)* | — |
| **L4** Troubleshoot | Cho triệu chứng "không vào được web nội bộ" → nêu thứ tự kiểm tra theo tầng | ⬜ |
| **L5** Design | Thiết kế quy trình debug 5 bước cho helpdesk công ty bạn, theo mô hình OSI | ⬜ |

## 14. Summary

**Key concepts**

- Network = thiết bị + môi trường truyền + protocol
- OSI 7 tầng: dùng để **khoanh vùng lỗi**, không phải để đọc thuộc
- PDU: bit → frame → packet → segment
- Encapsulation: mỗi tầng bọc thêm header trả lời một câu hỏi khác nhau
- ⭐ **MAC đổi mỗi hop, IP giữ nguyên** — nền tảng của mọi thứ phía sau

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show version` | Xác định thiết bị và IOS |
| `show ip interface brief` | Lệnh đầu tiên khi debug bất cứ gì |
| `show cdp neighbors` | Xác định topology thật so với sơ đồ |

**Common mistakes**

| Sai | Đúng |
|---|---|
| "PC phải biết MAC của server" | PC chỉ cần MAC của **default gateway** |
| "Switch giảm TTL" | TTL ở L3, switch là L2 — không chạm vào |
| Học thuộc OSI mà không dùng được | Dùng OSI như **thứ tự kiểm tra**, từ dưới lên |
| Nhảy thẳng lên L7 khi debug | 80% sự cố nằm ở L1–L3 |

## 15. Homework + cập nhật PROGRESS

**Homework**

1. Vẽ tay bảng packet flow PC → SW → R1 → R2 → Server, **không nhìn lại lesson**.
2. Học thuộc bảng OSI 7 tầng + PDU.
3. Chạy `tracert 8.8.8.8`, đếm số hop, giải thích vì sao có hop `* * *`.

**Dán dòng này vào `PROGRESS.md`:**

```markdown
- [YYYY-MM-DD] Lesson 01 — OSI & TCP/IP: DONE | cần ôn lại <điểm yếu của bạn>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Thứ tự 7 tầng, PDU mỗi tầng, thiết bị thuộc tầng nào, OSI ↔ TCP/IP |
| 🔧 **Engineer** | Dùng OSI làm thứ tự debug; biết mỗi header trả lời câu hỏi gì |
| 🏭 **Production** | 80% sự cố nằm ở L1–L3. CDP/LLDP là công cụ dựng lại topology thật khi tài liệu đã lỗi thời. |

### 🔗 Liên kết

- ➡️ Lesson sau: [`lesson-02-ipv4-va-subnetting.md`](./lesson-02-ipv4-va-subnetting.md)
- 🔌 Cheatsheet: [`ports-va-protocols.md`](../cheatsheets/ports-va-protocols.md)
- 🃏 Flashcard: [`00-foundation.md`](../flashcards/00-foundation.md)
- 🧭 Playbook: [`troubleshooting-playbook.md`](../cheatsheets/troubleshooting-playbook.md)
