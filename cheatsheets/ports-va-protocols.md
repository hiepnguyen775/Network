# 🔌 Ports & Protocols Cheat Sheet

> Phần này **phải thuộc**. Nó xuất hiện trong đề thi, trong ACL, và trong mọi buổi troubleshoot.

---

## 1. Port phải thuộc lòng

| Port | Protocol | Dịch vụ | Ghi chú |
|:---:|:---:|---|---|
| **20 / 21** | TCP | FTP (data / control) | 20 là data, 21 là control |
| **22** | TCP | **SSH** | SCP, SFTP cũng dùng 22 |
| **23** | TCP | Telnet | ⚠️ Không mã hoá — không dùng trong production |
| **25** | TCP | SMTP | Gửi mail |
| **53** | **TCP + UDP** | **DNS** | UDP cho query, TCP cho zone transfer & reply lớn |
| **67 / 68** | UDP | **DHCP** | 67 = server, 68 = client |
| **69** | UDP | TFTP | Hay dùng để backup config thiết bị |
| **80** | TCP | HTTP | |
| **110** | TCP | POP3 | |
| **123** | UDP | **NTP** | |
| **143** | TCP | IMAP | |
| **161 / 162** | UDP | **SNMP** / SNMP trap | 161 = query, 162 = trap |
| **179** | TCP | BGP | |
| **389** | TCP/UDP | LDAP | |
| **443** | TCP | **HTTPS** | |
| **445** | TCP | SMB | File sharing Windows |
| **514** | UDP | **Syslog** | |
| **636** | TCP | LDAPS | |
| **3389** | TCP | RDP | |

### Nhóm dễ nhầm

| | |
|---|---|
| **53 dùng cả TCP và UDP** | Chặn nhầm TCP/53 → zone transfer và reply lớn chết |
| **67 vs 68** | Nhớ: **server lớn hơn client**… không, ngược lại: **67 = server**, 68 = client |
| **161 vs 162** | 161 là NMS **hỏi** thiết bị; 162 là thiết bị **chủ động báo** (trap) |
| **20 vs 21** | 21 là nơi bạn gõ lệnh, 20 là nơi file chạy qua |

---

## 2. Protocol number (dùng trong ACL, không phải port)

| Số | Protocol | Gặp ở đâu |
|:---:|---|---|
| **1** | **ICMP** | `permit icmp any any` |
| **6** | **TCP** | |
| **17** | **UDP** | |
| 47 | GRE | Tunnel |
| 50 | ESP | IPsec — phần mã hoá dữ liệu |
| 51 | AH | IPsec — chỉ xác thực |
| 89 | OSPF | Chạy trực tiếp trên IP, **không dùng port** |
| 112 | VRRP | |

> ⚠️ **OSPF không có port.** Nó là protocol số 89 chạy thẳng trên IP.
> Nếu ACL chặn IP mà không permit protocol 89 → OSPF chết, dù "không chặn port nào".

---

## 3. Multicast address hay gặp

| Địa chỉ | Dùng cho |
|---|---|
| `224.0.0.5` | OSPF — tất cả router |
| `224.0.0.6` | OSPF — DR/BDR |
| `224.0.0.9` | RIPv2 |
| `224.0.0.10` | EIGRP |
| `224.0.0.102` | HSRPv2 / GLBP |
| `ff02::1` | IPv6 — tất cả node trên link |
| `ff02::2` | IPv6 — tất cả router trên link |
| `ff02::5` | OSPFv3 |

---

## 4. OSI model — dùng để khoanh vùng lỗi, không để đọc thuộc

| Tầng | Tên | Đơn vị dữ liệu | Thiết bị | Ví dụ |
|:---:|---|---|---|---|
| **7** | Application | Data | — | HTTP, DNS, DHCP, SMTP |
| **6** | Presentation | Data | — | TLS/SSL, mã hoá, nén, JPEG |
| **5** | Session | Data | — | Quản lý phiên |
| **4** | Transport | **Segment** (TCP) / Datagram (UDP) | Firewall L4 | TCP, UDP, **port** |
| **3** | Network | **Packet** | **Router**, L3 switch | **IP**, ICMP, OSPF |
| **2** | Data Link | **Frame** | **Switch**, bridge, NIC | Ethernet, **MAC**, 802.1Q, ARP* |
| **1** | Physical | **Bit** | Hub, cáp, repeater | Cáp đồng/quang, tín hiệu |

\* ARP nằm vắt giữa L2–L3: nó dùng IP để hỏi ra MAC, đóng gói trong frame Ethernet.

**Cách nhớ (dưới lên):** *Please Do Not Throw Sausage Pizza Away.*

> 🔧 **Giá trị thực của OSI:** khi mạng hỏng, đi từ **tầng 1 lên**. Cáp trước, IP sau,
> ứng dụng cuối cùng. Người mới hay nhảy thẳng lên tầng 7 ("chắc server lỗi") và mất hàng giờ.

---

## 5. TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Kiểu kết nối | Connection-oriented | Connectionless |
| Độ tin cậy | Có ACK, retransmit, sắp thứ tự | Không đảm bảo gì |
| Thiết lập | **3-way handshake** | Gửi thẳng |
| Header | 20 byte (có option thì hơn) | **8 byte** |
| Tốc độ / overhead | Chậm hơn, nặng hơn | Nhanh, nhẹ |
| Dùng cho | Web, mail, file, SSH, BGP | DNS query, DHCP, NTP, SNMP, VoIP, streaming |

### TCP 3-way handshake

```text
Client                         Server
   |-------- SYN ------------->|   "tôi muốn kết nối, seq = x"
   |<------ SYN-ACK -----------|   "ok, seq = y, ack = x+1"
   |-------- ACK ------------->|   "xác nhận, ack = y+1"
   |====== đã kết nối =========|
```

Đóng kết nối: `FIN → ACK → FIN → ACK` (4 bước).

### TCP flag hay gặp khi đọc Wireshark

| Flag | Nghĩa |
|---|---|
| `SYN` | Mở kết nối |
| `ACK` | Xác nhận |
| `FIN` | Đóng kết nối một cách lịch sự |
| `RST` | **Đóng đột ngột** — thường là firewall chặn hoặc không có service lắng nghe |
| `PSH` | Đẩy dữ liệu lên ứng dụng ngay |

> 🏭 Thấy `RST` ngay sau `SYN` → gần như chắc chắn: **không có dịch vụ nào nghe ở port đó**,
> hoặc **firewall chặn theo kiểu reject** (khác với drop im lặng = timeout).
