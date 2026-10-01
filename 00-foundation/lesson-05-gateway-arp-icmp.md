# LESSON 05 — Default Gateway · ARP · ICMP ⭐

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 02](./lesson-02-ipv4-va-subnetting.md), [Lesson 03](./lesson-03-ethernet-mac-frame.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích chính xác host quyết định "gửi thẳng hay gửi qua gateway" **bằng phép toán nào**
- [ ] Mô tả ARP từng bước, biết nó hỏi gì và ai trả lời
- [ ] Nói được vì sao ARP **không qua được router**
- [ ] Đọc ICMP và phân biệt *Time Exceeded* với *Destination Unreachable*
- [ ] Giải thích `traceroute` hoạt động thế nào — bằng TTL

## 2. Prerequisite

- Phép AND giữa IP và subnet mask *(Lesson 02 §5)*
- MAC, frame, switch flood *(Lesson 03)*
- Broadcast dừng ở router *(Lesson 04)*

---

## 3. Concept

### Default Gateway

**Default gateway** = địa chỉ IP của router trong subnet của bạn — nơi host gửi gói khi
**đích không nằm cùng subnet**.

```text
PC:  192.168.1.10/24
GW:  192.168.1.1          ← thường là first usable của subnet

Gửi tới 192.168.1.50  →  cùng subnet  →  gửi THẲNG
Gửi tới 8.8.8.8       →  khác subnet  →  gửi cho GATEWAY
```

> ⚠️ **Hiểu lầm kinh điển:** "gửi cho gateway" **không** có nghĩa là đổi IP đích.
> IP đích vẫn là `8.8.8.8`. Chỉ **MAC đích** là MAC của gateway.
> Đây là áp dụng trực tiếp quy tắc *"MAC đổi mỗi hop, IP giữ nguyên"*.

### ARP — Address Resolution Protocol

**ARP phân giải IP → MAC**, trong phạm vi **một broadcast domain**.

```text
Request  (broadcast):  "Ai có 192.168.1.1? Nói cho 192.168.1.10 biết."
Reply    (unicast)  :  "192.168.1.1 đang ở 00:1A:2B:3C:4D:5E."
```

| | Request | Reply |
|---|---|---|
| Dst MAC | `FF:FF:FF:FF:FF:FF` | MAC của người hỏi |
| Kiểu | **Broadcast** | **Unicast** |
| EtherType | `0x0806` | `0x0806` |

Kết quả lưu vào **ARP cache** — mặc định khoảng **4 giờ** trên Cisco IOS,
vài phút trên Windows/Linux.

### ICMP — Internet Control Message Protocol

ICMP là giao thức **báo lỗi và chẩn đoán** của tầng 3. Nó là **protocol number 1**, chạy
thẳng trên IP, **không có port**.

| Type | Code | Tên | Gặp khi |
|:---:|:---:|---|---|
| **8** | 0 | Echo Request | Bạn gõ `ping` |
| **0** | 0 | Echo Reply | Đích trả lời |
| **11** | 0 | **Time Exceeded** | TTL về 0 → nền tảng của `traceroute` |
| **3** | 0 | Net Unreachable | Router không có route |
| **3** | 1 | Host Unreachable | Tới được mạng nhưng không thấy host |
| **3** | 3 | Port Unreachable | Không có service nghe ở port đó (UDP) |
| **3** | 4 | Fragmentation Needed | Gói quá lớn, có cờ DF → **nền của lỗi MTU** |
| **3** | 13 | Administratively Prohibited | **ACL chặn** |

> 🔑 `Type 3 Code 13` là món quà cho người troubleshoot: nó nói thẳng
> *"có ACL đang chặn bạn"* thay vì để bạn đoán giữa timeout.

---

## 4. Why? — tại sao cần ARP

> **Nếu bỏ ARP, chỉ dùng IP thì sao?**

Vấn đề cốt lõi: **card mạng không hiểu IP.** Nó chỉ gửi và nhận frame theo MAC.

```text
Ứng dụng nói:        "gửi cho 192.168.1.50"
Card mạng cần biết:  "ghi MAC nào vào Dst MAC của frame?"
                      ↑
                   ARP lấp chỗ trống này
```

Ba lựa chọn thay thế, đều tệ hơn:

| Phương án | Vì sao không dùng |
|---|---|
| Khai báo tay IP↔MAC trên mọi máy | 300 máy = 300 bảng phải sửa mỗi lần đổi card |
| Nhúng MAC vào IP | IP phải đổi mỗi lần thay card mạng → mất hết ý nghĩa địa chỉ logic |
| Luôn broadcast mọi gói | Mạng chết vì broadcast |

ARP là **thương lượng tự động, đúng lúc cần, chỉ một lần rồi cache**.

> 🔧 Và đây là lý do ARP **không qua được router**: nó hỏi *"ai ở trên dây này"* —
> câu hỏi chỉ có nghĩa trong một broadcast domain. Máy ở mạng khác không thể trả lời,
> và không cần trả lời, vì bạn sẽ gửi cho router chứ không gửi thẳng cho nó.

---

## 5. How does it work?

### Quyết định cùng subnet hay khác subnet

Host làm **đúng một phép toán**, với chính mask của nó:

```text
B1.  IP_của_tôi    AND  mask_của_tôi  =  network_của_tôi
B2.  IP_đích       AND  mask_của_tôi  =  network_của_đích (theo góc nhìn của tôi)
B3.  Hai kết quả có bằng nhau không?
     ├─ BẰNG    → cùng subnet  → ARP tìm MAC của CHÍNH máy đích
     └─ KHÁC    → khác subnet  → ARP tìm MAC của DEFAULT GATEWAY
```

**Ví dụ:** PC `192.168.1.10/24` gửi tới `192.168.1.50`

```text
192.168.1.10 AND 255.255.255.0 = 192.168.1.0
192.168.1.50 AND 255.255.255.0 = 192.168.1.0      → BẰNG → gửi thẳng
```

Gửi tới `8.8.8.8`:

```text
8.8.8.8 AND 255.255.255.0 = 8.8.8.0  ≠  192.168.1.0  → gửi cho gateway
```

### Quy trình ARP đầy đủ

```text
1. PC muốn gửi gói tới 192.168.1.1
2. Tra ARP cache — có MAC của .1 không?
   ├─ CÓ   → dùng luôn, xong
   └─ KHÔNG ↓
3. Tạo ARP Request, Dst MAC = FF:FF:FF:FF:FF:FF  (broadcast)
4. Switch FLOOD ra mọi port cùng VLAN
5. Mọi máy nhận, mở ra xem "có phải hỏi IP của tôi không?"
   ├─ Không phải tôi → VỨT
   └─ Đúng tôi       → tạo ARP Reply, UNICAST về người hỏi
6. PC nhận Reply → lưu vào ARP cache → giờ mới gửi được gói thật
```

> 💡 Nhìn kỹ bước 6: **gói dữ liệu thật chưa đi được cho tới khi ARP xong.**
> Đây là lý do gói `ping` **đầu tiên** hay chậm hơn hẳn các gói sau — và vì sao
> nhiều người thấy `Request timed out` ở gói đầu rồi 4 gói sau bình thường.

### TTL và cơ chế traceroute

```text
traceroute 8.8.8.8

Gửi gói TTL=1  → router 1 giảm còn 0 → DROP + trả ICMP Time Exceeded
                 → ta biết router 1 là ai
Gửi gói TTL=2  → qua router 1 (còn 1) → router 2 giảm còn 0 → Time Exceeded
                 → ta biết router 2 là ai
Gửi gói TTL=3  → ... cứ thế
...đến khi tới đích → đích trả Echo Reply (hoặc Port Unreachable) → dừng
```

Toàn bộ `traceroute` chỉ là **lợi dụng TTL** để bắt từng router tự xưng tên.

---

## 6. Packet Flow

**Kịch bản:** PC-A `192.168.1.10/24` ping Server `10.0.0.50`, qua R1 và R2.

### Giai đoạn 1 — ARP (trong LAN của PC-A)

| # | Dst MAC | Src MAC | Nội dung |
|:---:|---|---|---|
| 1 | `FF:FF:FF:FF:FF:FF` | MAC-A | "Ai có `192.168.1.1`?" |
| 2 | MAC-A | MAC-R1 | "`192.168.1.1` ở `MAC-R1`" |

> PC-A **không bao giờ** ARP tìm `10.0.0.50`. Nó biết đích ở xa nên chỉ cần MAC của gateway.

### Giai đoạn 2 — ICMP đi qua các hop

| Hop | Dst MAC | Src MAC | Src IP | Dst IP | TTL |
|---|---|---|---|---|:---:|
| PC-A → R1 | MAC-R1 | MAC-A | 192.168.1.10 | 10.0.0.50 | 128 |
| R1 → R2 | MAC-R2 | MAC-R1-out | 192.168.1.10 | 10.0.0.50 | **127** |
| R2 → Server | MAC-Server | MAC-R2-out | 192.168.1.10 | 10.0.0.50 | **126** |

**Ba điều phải thấy rõ:**

1. **IP nguồn/đích không đổi** qua cả 3 hop
2. **MAC bị viết lại hoàn toàn** ở mỗi router
3. **Mỗi router làm ARP riêng** trong mạng của nó để tìm MAC của hop kế tiếp

---

## 7. Real-world Example

🏭 **Tình huống 1 — "Ping được IP nhưng không ping được tên"**

ARP và routing đều ổn, vấn đề ở **DNS** (Lesson 08). Đây là bài kiểm tra nhanh:
`ping 8.8.8.8` được mà `ping google.com` không được → **chắc chắn là DNS**, không phải mạng.

🏭 **Tình huống 2 — Ping một chiều**

Đã gặp ở Lesson 02: hai máy đặt mask lệch nhau. Máy A nghĩ cùng subnet nên ARP trực tiếp;
máy B nghĩ khác subnet nên gửi qua gateway. Kiểm chứng bằng `arp -a` ở cả hai máy.

🏭 **Tình huống 3 — Gratuitous ARP**

Khi một máy vừa lên hoặc vừa đổi IP, nó tự phát một ARP **hỏi chính IP của mình**.
Mục đích kép: (1) phát hiện xung đột IP, (2) báo cho switch/các máy cập nhật bảng.

Đây cũng là cơ chế **failover của HSRP/VRRP** (Phase 8): router dự phòng lên thay,
phát gratuitous ARP để mọi máy đổi sang MAC mới mà không phải đợi ARP cache hết hạn.

🏭 **Tình huống 4 — ARP spoofing**

Kẻ tấn công liên tục trả lời ARP sai: *"gateway ở MAC của tôi"*. Mọi máy tin, gửi traffic
cho hắn → man-in-the-middle. Phòng chống: **Dynamic ARP Inspection** (Lesson 37).

---

## 8. Cisco CLI

```cisco
! ───── Xem và quản lý ARP ─────
R1# show ip arp                          ! bảng ARP của router
R1# show ip arp 192.168.1.10             ! một entry cụ thể
R1# clear arp-cache                      ! xoá sạch, học lại

! Gán ARP tĩnh (hiếm dùng)
R1(config)# arp 192.168.1.50 001a.2b3c.4d5e arpa

! Đổi thời gian giữ ARP (mặc định 4 giờ = 14400 giây)
R1(config-if)# arp timeout 3600

! ───── Ping nâng cao ─────
R1# ping 8.8.8.8 source GigabitEthernet0/1    ! ping từ một source IP cụ thể
R1# ping 8.8.8.8 size 1500 df-bit             ! kiểm tra MTU, cấm phân mảnh
R1# ping 8.8.8.8 repeat 100                   ! gửi 100 gói
R1# traceroute 8.8.8.8

! ───── Default gateway ─────
! Trên ROUTER / L3 switch: dùng default route
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1

! Trên SWITCH L2 (chỉ để quản trị, switch không route)
SW1(config)# ip default-gateway 192.168.1.1
```

| Lệnh | Làm gì | Khác biệt platform |
|---|---|---|
| `show ip arp` | Bảng ARP | **NX-OS**: `show ip arp` giống nhau |
| `ip default-gateway` | Gateway cho **switch L2** | ⚠️ Chỉ có tác dụng khi `ip routing` **tắt** |
| `ip route 0.0.0.0 0.0.0.0` | Default route cho thiết bị **có routing** | Dùng cái này trên router và L3 switch |
| `ping ... source` | Chọn source IP | Cực kỳ hữu ích khi debug ACL/NAT |

> ⚠️ Nhầm lẫn phổ biến: dùng `ip default-gateway` trên **L3 switch đã bật `ip routing`**.
> Lệnh sẽ bị **bỏ qua im lặng**. Khi đã bật routing, phải dùng `ip route 0.0.0.0 0.0.0.0`.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip arp
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  192.168.1.1            -    0050.56aa.0001  ARPA   GigabitEthernet0/0
Internet  192.168.1.10           5    001a.2b3c.4d5e  ARPA   GigabitEthernet0/0
Internet  192.168.1.50          12    001a.2b3c.4d6f  ARPA   GigabitEthernet0/0
```

| Cột | Ý nghĩa | Bất thường |
|---|---|---|
| `Age (min)` | Phút kể từ lần cuối thấy | `-` = **IP của chính router** |
| `Hardware Addr` | MAC học được | Hai IP khác nhau **cùng một MAC** → nghi ARP spoofing hoặc có proxy ARP |
| `Interface` | Học được ở interface nào | Sai interface → đấu nhầm dây |
| Thiếu entry của một IP | Máy đó chưa nói gì, hoặc không tồn tại | |

```text
# output điển hình — tự verify trên lab của bạn
R1# traceroute 8.8.8.8
  1  192.168.1.1     1 msec  0 msec  0 msec
  2  203.0.113.1     8 msec  9 msec  8 msec
  3  * * *
  4  8.8.8.8        14 msec 13 msec 14 msec
```

> `* * *` **không** có nghĩa là đứt mạng. Thường chỉ là router đó được cấu hình
> **không trả ICMP Time Exceeded**. Nếu các hop **sau** nó vẫn trả lời thì đường đi vẫn thông.
> Chỉ lo khi `* * *` kéo dài tới hết.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Ping gateway fail | Sai VLAN / sai mask / cáp | `arp -a`, `show vlan brief` | Kiểm tra theo thứ tự L1→L2→L3 |
| `arp -a` thấy entry `incomplete` | Không ai trả lời ARP | `show vlan brief`, ping từ phía kia | Máy đích tắt, sai VLAN, hoặc sai subnet |
| Ping gateway OK, ping xa fail | Thiếu route (chiều đi hoặc **chiều về**) | `show ip route` ở **cả 2 đầu** | Thêm route còn thiếu |
| Ping được 1 chiều | Mask lệch, hoặc ACL một chiều | So mask 2 máy; `show access-lists` | Đồng bộ mask / sửa ACL |
| Gói đầu tiên timeout, các gói sau OK | **ARP đang chạy** — bình thường | `arp -a` trước và sau | Không phải lỗi |
| `traceroute` có `* * *` ở giữa | Router đó không trả ICMP | Xem các hop sau có trả lời không | Không phải lỗi nếu hop sau OK |
| Ping nhỏ OK, ping `size 1500` fail | **Vấn đề MTU** | `ping <ip> size 1500 df-bit` | Chỉnh MTU/MSS *(Phase 7)* |
| Nhận ICMP Type 3 Code 13 | **ACL đang chặn** | `show access-lists` | Sửa ACL |

---

## 11. LAB

🧪 **[LAB 02 — Bắt ARP + ICMP bằng Wireshark](../labs/lab02-arp-icmp-wireshark.md)**

## 12. Challenge

1. PC-A `192.168.1.10/24` ping `192.168.1.50`. Máy `.50` **không tồn tại**.
   Mô tả chính xác chuyện gì xảy ra trên dây, và `arp -a` sẽ hiện gì?
2. Vì sao PC **không** ARP tìm MAC của `8.8.8.8`? Nếu nó cố thì sao?
3. `traceroute` trả về 3 hop rồi `* * *` mãi tới hop 30. Nêu **3 khả năng** và cách phân biệt.
4. Máy A và máy B cùng subnet nhưng nằm ở **2 VLAN khác nhau** trên cùng switch.
   A ping B có được không? Giải thích bằng ARP.

<details>
<summary>Đáp án</summary>

**1.** PC-A gửi ARP Request broadcast, switch flood ra mọi port. **Không ai trả lời.**
PC-A thử lại vài lần (Windows ~3 lần) rồi bỏ cuộc. `arp -a` hiện entry với trạng thái
`incomplete` (Linux) hoặc không có entry nào (Windows). Gói ICMP **chưa bao giờ được gửi đi** —
nó chết ngay trong máy A vì không điền được Dst MAC.

**2.** Vì `8.8.8.8` **khác subnet** — phép AND cho ra network khác. ARP là câu hỏi
*"ai ở trên dây này"*, mà `8.8.8.8` không ở trên dây này. Nếu PC cố ARP, request là broadcast
nên **dừng ở router**, Google không bao giờ nhận được, và sẽ không có reply.

**3.** Ba khả năng:
| Khả năng | Phân biệt bằng |
|---|---|
| Các router sau không trả ICMP Time Exceeded | Nếu đích cuối vẫn ping được → đường thông, chỉ im lặng |
| Firewall chặn ICMP từ hop 4 trở đi | `telnet <đích> <port>` xem TCP có qua được không |
| Mạng đứt thật từ hop 4 | Cả `traceroute` lẫn `ping` đích đều fail |

**4.** **Không.** ARP Request của A là broadcast, switch chỉ flood **trong VLAN của A**.
B nằm VLAN khác nên không bao giờ nhận được request → không có reply → A không điền được
Dst MAC → gói không đi được. Cùng subnet IP **không đủ**; phải cùng **broadcast domain**.
Đây là bẫy kinh điển và là lý do VLAN mạnh đến vậy về mặt tách biệt.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | ARP phân giải gì→gì · request broadcast hay unicast · ICMP type 8/0/11/3 | ⬜ |
| **L2** Explain | Giải thích phép AND quyết định gửi thẳng hay qua gateway | ⬜ |
| **L3** Configure | Cấu hình gateway cho PC và default route cho router, verify bằng `traceroute` | ⬜ |
| **L4** Troubleshoot | Cho `arp -a` có entry incomplete → nêu 3 nguyên nhân | ⬜ |
| **L5** Design | Thiết kế quy ước gateway (first/last usable) cho công ty 10 VLAN, giải thích vì sao | ⬜ |

## 14. Summary

**Key concepts**

- Default gateway = router trong subnet của bạn, dùng khi đích **khác subnet**
- Host quyết định bằng **phép AND** giữa IP đích và **mask của chính mình**
- ARP: **IP → MAC**, request **broadcast**, reply **unicast**, chỉ trong 1 broadcast domain
- ⭐ **ARP không qua router** — gói đi xa chỉ cần MAC của gateway
- ICMP: protocol **1**, không có port. Type 8/0 = ping, 11 = Time Exceeded, 3 = Unreachable
- `traceroute` = lợi dụng **TTL** để bắt từng router tự xưng tên

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip arp` / `arp -a` | Kiểm tra IP↔MAC đã học |
| `clear arp-cache` | Ép học lại sau khi đổi thiết bị |
| `ping <ip> source <int>` | Debug ACL/NAT — ping từ đúng source |
| `ping <ip> size 1500 df-bit` | Kiểm tra MTU |
| `traceroute <ip>` | Gói chết ở hop nào |

**Common mistakes**

| Sai | Đúng |
|---|---|
| "ARP hỏi ra IP" | ARP hỏi ra **MAC**, từ IP đã biết |
| "Gửi cho gateway thì IP đích đổi thành IP gateway" | Chỉ **MAC đích** đổi |
| "PC phải ARP tìm MAC của server ở xa" | Chỉ cần MAC của **gateway** |
| "`* * *` trong traceroute là đứt mạng" | Thường chỉ là router không trả ICMP |
| Dùng `ip default-gateway` trên L3 switch đã bật routing | Phải dùng `ip route 0.0.0.0 0.0.0.0` |
| "Cùng subnet là ping được nhau" | Phải cùng **broadcast domain** nữa |

## 15. Homework + cập nhật PROGRESS

1. `arp -d *` (xoá cache, chạy as admin) rồi `ping` gateway. Bắt bằng Wireshark filter `arp`.
   Xác nhận request là broadcast, reply là unicast.
2. `tracert 8.8.8.8` — đếm số hop, giải thích `* * *` nếu có.
3. `ping 8.8.8.8 -f -l 1472` (Windows) — tìm MTU lớn nhất đi được mà không phân mảnh.
4. Giải thích cho người khác vì sao ARP không qua được router.

```markdown
- [YYYY-MM-DD] Lesson 05 — Gateway, ARP, ICMP: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | ARP request/reply, phép AND, ICMP type, cơ chế traceroute |
| 🔧 **Engineer** | `ping source`, `df-bit` để test MTU; đọc `arp -a` để tìm mask mismatch |
| 🏭 **Production** | Gratuitous ARP là nền của HSRP failover; ARP spoofing → cần DAI; ICMP Type 3 Code 13 tố cáo ACL |

### 🔗 Liên kết

- ⬅️ [Lesson 04 — Unicast/Broadcast/Multicast](./lesson-04-unicast-broadcast-multicast.md)
- ➡️ [Lesson 06 — TCP vs UDP](./lesson-06-tcp-udp-port.md)
- 🧪 [LAB 02](../labs/lab02-arp-icmp-wireshark.md)
- 🦈 [`cheatsheets/wireshark.md`](../cheatsheets/wireshark.md)
- 🧭 [`cheatsheets/troubleshooting-playbook.md`](../cheatsheets/troubleshooting-playbook.md)
