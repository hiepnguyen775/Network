# 🦈 Wireshark Cheat Sheet

> Wireshark là công cụ biến network từ **trừu tượng** thành **nhìn thấy được**.
> Đọc được gói tin là bước nhảy lớn nhất về hiểu biết trong Phase 0 — và là thứ
> phân biệt người học thuộc với người hiểu.

---

## 1. Hai loại filter — nhầm chỗ này là mất thời gian nhất

| | **Capture filter** | **Display filter** |
|---|---|---|
| Đặt lúc nào | **Trước** khi bắt | **Sau** khi đã bắt |
| Cú pháp | BPF — `host`, `port`, `net` | Wireshark — `ip.addr`, `tcp.port` |
| Gói không khớp | **Mất luôn**, không lấy lại được | Vẫn còn, chỉ bị ẩn |
| Ô nhập | Màn hình khởi động, ô *"…using this filter"* | Thanh xanh ngay trên danh sách gói |
| Khi nào dùng | Mạng quá đông, bắt lâu | **Mặc định dùng cái này** |

```text
Capture filter (BPF):     host 192.168.1.10 and icmp
Display filter:           ip.addr == 192.168.1.10 && icmp
```

> ⚠️ Người mới hay gõ `ip.addr == 10.0.0.1` vào ô capture filter → Wireshark báo đỏ.
> Hai ngôn ngữ **khác nhau hoàn toàn**. Khi đang học, cứ bắt tất rồi lọc bằng display filter.

---

## 2. Display filter cần thuộc

### Theo giao thức

```text
arp                     ARP request/reply
icmp                    ping, traceroute, unreachable
dhcp                    DHCP (Wireshark ≥ 3.0; bản cũ dùng: bootp)
dns                     truy vấn và trả lời DNS
tcp                     mọi gói TCP
udp                     mọi gói UDP
ospf                    OSPF hello, LSA
vlan                    frame có tag 802.1Q
stp                     BPDU của spanning-tree
cdp                     Cisco Discovery Protocol
```

### Theo địa chỉ & port

```text
ip.addr == 192.168.1.10          nguồn HOẶC đích là IP này
ip.src  == 192.168.1.10          chỉ nguồn
ip.dst  == 8.8.8.8               chỉ đích
eth.addr == 00:1a:2b:3c:4d:5e    theo MAC
tcp.port == 443                  nguồn hoặc đích port 443
udp.port == 53                   DNS
ip.ttl < 5                       TTL thấp — gói sắp chết
vlan.id == 10                    chỉ VLAN 10
```

### Kết hợp

```text
&&   hoặc  and          ||   hoặc  or          !   hoặc  not

ip.addr == 10.0.0.5 && icmp
dns && !ip.addr == 8.8.8.8
tcp.port == 80 || tcp.port == 443
```

### Lọc TCP handshake & vấn đề

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0     chỉ gói SYN (mở kết nối)
tcp.flags.reset == 1                          RST — bị từ chối
tcp.flags.fin == 1                            FIN — đóng kết nối
tcp.analysis.flags                            Wireshark tự đánh dấu bất thường
tcp.analysis.retransmission                   gói phải gửi lại → mất gói
```

---

## 3. Đọc từng giao thức — nhìn gì

### ARP — *"ai có IP này?"*

```text
# dạng điển hình — tự bắt trên máy bạn
1  Broadcast   ARP  Who has 192.168.1.1?  Tell 192.168.1.10
2  Unicast     ARP  192.168.1.1 is at 00:1a:2b:3c:4d:5e
```

| Nhìn gì | Ý nghĩa |
|---|---|
| Request gửi tới `ff:ff:ff:ff:ff:ff` | ARP request là **broadcast** |
| Reply là **unicast** | Chỉ trả lời cho người hỏi |
| Hỏi IP gateway dù đích ở xa | ✅ Đúng — host chỉ cần MAC của hop kế tiếp |
| Hỏi mãi không ai trả lời | Đích không tồn tại, sai VLAN, hoặc **sai subnet mask** |

> 💡 Đây là cách **nhìn thấy** quy tắc *"MAC đổi mỗi hop, IP giữ nguyên"*.

### ICMP — ping & traceroute

| Type | Tên | Gặp khi |
|:---:|---|---|
| 8 | Echo Request | Bạn `ping` |
| 0 | Echo Reply | Đích trả lời |
| 11 | **Time Exceeded** | TTL về 0 — đây là cơ chế của `traceroute` |
| 3 | **Destination Unreachable** | Không có route, hoặc bị ACL chặn |

```text
icmp.type == 11        chỉ xem gói Time Exceeded
icmp.type == 3         chỉ xem Destination Unreachable
```

### DHCP — xem DORA bằng mắt

```text
dhcp
```

| Bước | Gói | Src IP | Dst IP |
|:---:|---|---|---|
| **D** | Discover | `0.0.0.0` | `255.255.255.255` |
| **O** | Offer | DHCP server | broadcast hoặc unicast |
| **R** | Request | `0.0.0.0` | `255.255.255.255` |
| **A** | ACK | DHCP server | client |

> 🔑 Nhìn `Src IP = 0.0.0.0` ở bước Discover là hiểu ngay **vì sao DHCP cần relay**:
> client chưa có IP, gói là broadcast → router không chuyển tiếp broadcast.

### TCP 3-way handshake

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

```text
# dạng điển hình — tự bắt trên máy bạn
1  Client → Server   [SYN]      Seq=0
2  Server → Client   [SYN, ACK] Seq=0 Ack=1
3  Client → Server   [ACK]      Seq=1 Ack=1
```

| Thấy gì | Kết luận |
|---|---|
| Đủ 3 bước | Kết nối mở thành công |
| `SYN` rồi im lặng, lặp lại | Firewall **drop** → timeout |
| `SYN` rồi `RST` ngay | Không có service nghe ở port đó, hoặc firewall **reject** |

### DNS

```text
dns
```

Nhìn: `Standard query` → `Standard query response`. Cột `Time` cho biết DNS chậm hay nhanh.
`No such name (NXDOMAIN)` = tên không tồn tại.

### VLAN tag 802.1Q

```text
vlan
vlan.id == 10
```

> ⚠️ **Rất hay bị hụt:** card mạng của PC thường **gỡ tag VLAN trước khi Wireshark thấy**.
> Muốn nhìn được tag thật, phải bắt trên **trunk port qua SPAN/port-mirror**, hoặc bắt
> trong Packet Tracer / GNS3. Không thấy tag không có nghĩa là trunk hỏng.

---

## 4. Ba thao tác đáng giá nhất

| Thao tác | Đường dẫn | Dùng để |
|---|---|---|
| **Follow TCP Stream** | Chuột phải gói → *Follow* → *TCP Stream* | Xem toàn bộ hội thoại của một kết nối, dạng text |
| **Conversations** | *Statistics* → *Conversations* | Ai nói chuyện với ai nhiều nhất — tìm máy phát broadcast bất thường |
| **Protocol Hierarchy** | *Statistics* → *Protocol Hierarchy* | Mạng này đang chạy gì, tỷ lệ bao nhiêu |

Hai tuỳ chỉnh nên bật ngay từ đầu:

- *View* → *Time Display Format* → **Seconds Since Previous Displayed Packet**
  → nhìn ra ngay chỗ nào bị chậm/timeout.
- *Edit* → *Preferences* → *Appearance* → *Columns*: thêm cột **VLAN** và **TTL**.

---

## 5. Bắt ở đâu mới thấy được cái mình cần

| Muốn xem | Bắt ở đâu |
|---|---|
| Traffic của chính máy bạn | Card mạng của máy — đơn giản nhất |
| Traffic của máy khác | Phải **SPAN / port-mirror** trên switch |
| Tag VLAN trên trunk | SPAN của trunk port, hoặc lab ảo |
| Broadcast/ARP cả VLAN | Bất kỳ port nào trong VLAN đó |

> ⚠️ Switch **không** flood unicast đã học sang port khác — cắm Wireshark vào một port trống
> sẽ **không** thấy traffic giữa hai máy khác. Đây là lý do SPAN tồn tại.
> (Hub thì thấy hết — nhưng hub đã tuyệt chủng.)

---

## 6. Bẫy hay gặp

| Bẫy | Thực tế |
|---|---|
| Gõ display filter vào ô capture filter | Hai cú pháp khác nhau — ô đỏ là sai cú pháp |
| Dùng `=` thay vì `==` | Display filter cần `==` |
| `bootp` không chạy | Wireshark ≥ 3.0 đổi thành `dhcp` |
| Không thấy VLAN tag | NIC đã gỡ tag — cần SPAN hoặc lab ảo |
| Không thấy traffic máy khác | Switch không flood — cần SPAN |
| Bắt cả tiếng rồi mới lọc | File vài GB, mở rất chậm — dùng capture filter khi đã biết cần gì |
| Thấy `TCP Retransmission` là hoảng | Vài gói là bình thường; **tỷ lệ cao** mới là vấn đề |

---

## 7. Bài tự luyện cho Phase 0

| # | Bài | Filter | Phải trả lời được |
|:---:|---|---|---|
| 1 | Xoá ARP cache (`arp -d *`) rồi ping gateway | `arp` | Request gửi tới MAC nào? Reply là broadcast hay unicast? |
| 2 | Ping một IP không tồn tại cùng subnet | `arp` | Vì sao chỉ thấy request, không có reply? |
| 3 | `ipconfig /release` + `/renew` | `dhcp` | Src IP của Discover là gì? Vì sao? |
| 4 | Mở một trang web | `tcp.flags.syn==1 && tcp.flags.ack==0` | Đếm được bao nhiêu kết nối TCP? |
| 5 | `nslookup google.com` | `dns` | Query mất bao nhiêu ms? Dùng UDP hay TCP? |
| 6 | `tracert 8.8.8.8` | `icmp` | TTL của gói đầu tiên là bao nhiêu? Ai trả lời Time Exceeded? |

> Làm xong 6 bài này, bạn đã *nhìn thấy* gần như toàn bộ lý thuyết Phase 0.

---

## 🔗 Liên kết

- 🔌 [`ports-va-protocols.md`](./ports-va-protocols.md) — port & protocol number để viết filter
- 🧭 [`troubleshooting-playbook.md`](./troubleshooting-playbook.md) — dùng capture để kiểm chứng giả thuyết
- 📁 [`../00-foundation/`](../00-foundation/) — LAB 02 và LAB 03 của Phase 0 dùng Wireshark
