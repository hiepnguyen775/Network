# LESSON 08 — DNS · DHCP (DORA)

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 04](./lesson-04-unicast-broadcast-multicast.md), [Lesson 06](./lesson-06-tcp-udp-port.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Mô tả 4 bước **DORA** kèm địa chỉ nguồn/đích của từng bước
- [ ] Giải thích **vì sao DHCP cần relay** — bằng kiến thức broadcast, không học thuộc
- [ ] Cấu hình router làm DHCP server **và** DHCP relay, verify
- [ ] Mô tả quá trình phân giải DNS đệ quy, biết record type cơ bản
- [ ] Phân biệt dứt khoát "lỗi mạng" và "lỗi DNS" chỉ bằng 2 lệnh ping

## 2. Prerequisite

- Broadcast dừng ở router *(Lesson 04)*
- UDP, port 53 và 67/68 *(Lesson 06)*
- APIPA `169.254.x.x` *(Lesson 02)*

---

## 3. Concept

### DHCP — Dynamic Host Configuration Protocol

DHCP cấp tự động cho máy: **IP · subnet mask · default gateway · DNS server** (và nhiều
tuỳ chọn khác như NTP, domain name, TFTP server).

| Vai trò | Port |
|---|:---:|
| **Server** | UDP **67** |
| **Client** | UDP **68** |

### DORA — 4 bước

| Bước | Tên | Ai gửi | Src IP | Dst IP | Kiểu |
|:---:|---|---|---|---|---|
| **D** | **Discover** | Client | `0.0.0.0` | `255.255.255.255` | Broadcast |
| **O** | **Offer** | Server | IP server | broadcast *(hoặc unicast)* | |
| **R** | **Request** | Client | `0.0.0.0` | `255.255.255.255` | Broadcast |
| **A** | **ACK** | Server | IP server | client | |

> 🔑 Nhìn `Src IP = 0.0.0.0` ở bước D và R là hiểu ngay **vì sao DHCP cần relay**:
> client **chưa có IP**, phải dùng broadcast — mà broadcast thì **dừng ở router** (Lesson 04).

**Vì sao cần cả R sau khi đã có O?** Vì có thể có **nhiều DHCP server** cùng trả lời.
Bước Request là lúc client công bố *"tôi chọn offer của server X"* — các server khác
nghe thấy và thu hồi offer của mình.

### Lease — thuê có thời hạn

```text
T0        T1 = 50% lease              T2 = 87.5%            T3 = 100%
│──────────│──────────────────────────│─────────────────────│
           ↑                          ↑                     ↑
     xin gia hạn              xin gia hạn                 hết hạn
     (unicast tới             (broadcast tới               → bỏ IP,
      server cũ)               mọi server)                   DORA lại
```

Lease mặc định trên Cisco IOS là **1 ngày**. Văn phòng hay để 8 giờ; Wi-Fi khách để 1–2 giờ
để IP quay vòng nhanh.

### DNS — Domain Name System

DNS phân giải **tên → IP**. Port **53**, dùng **cả UDP và TCP**.

| Khi nào | Giao thức |
|---|---|
| Truy vấn thường | **UDP/53** |
| Reply > 512 byte (cờ TC bật) | Chuyển sang **TCP/53** |
| Zone transfer giữa các DNS server | **TCP/53** |

### Record type cần biết

| Record | Trỏ tới | Ví dụ |
|---|---|---|
| **A** | IPv4 | `web.cty.vn → 10.0.1.50` |
| **AAAA** | IPv6 | `web.cty.vn → 2001:db8::50` |
| **CNAME** | Tên khác (bí danh) | `www → web.cty.vn` |
| **MX** | Mail server | `cty.vn → mail.cty.vn` (có priority) |
| **NS** | Name server của zone | |
| **PTR** | **IP → tên** (reverse lookup) | Dùng trong log, chống spam |
| **TXT** | Văn bản tự do | SPF, DKIM, xác thực domain |
| **SRV** | Dịch vụ + port | Active Directory dùng nhiều |

---

## 4. Why?

### Vì sao cần DHCP

> **Nếu gán IP tay cho mọi máy thì sao?**

| Vấn đề | Thực tế |
|---|---|
| **Không scale** | 300 máy = 300 lần gõ tay, mỗi lần 4 thông số |
| **Xung đột IP** | Hai người cùng gán `.50` → cả hai mất mạng, rất khó tìm |
| **Laptop di chuyển** | Sang tầng khác (VLAN khác) là phải gõ lại |
| **Đổi DNS server** | Phải đi từng máy |
| Thiết bị không có màn hình | Điện thoại IP, camera, máy in — gán tay thế nào? |

DHCP làm tất cả tự động và **tập trung**: đổi DNS server cho cả công ty = sửa **một dòng**.

### Vì sao cần DNS

> **Nếu chỉ dùng IP thì sao?**

| Vấn đề | Thực tế |
|---|---|
| Không ai nhớ nổi | `142.250.x.x` vs `google.com` |
| **Server đổi IP là chết hết** | Mọi client đã hardcode IP phải sửa |
| Không làm được load balancing | DNS trả nhiều A record, xoay vòng |
| Không chuyển sang CDN được | CDN hoạt động bằng cách trả IP gần bạn nhất |

> 🔧 Giá trị lớn nhất của DNS không phải "dễ nhớ" — mà là **một lớp gián tiếp**.
> Đổi IP server, đổi nhà cung cấp, chuyển sang cloud… client không cần biết gì.

---

## 5. How does it work?

### DHCP Relay — mấu chốt của lesson này

```text
VLAN 20 (10.0.20.0/24)                VLAN 10 (10.0.10.0/24)
   PC ──── SW ──── R1 (SVI) ──────────── DHCP Server 10.0.10.50
                     │
                     └── ip helper-address 10.0.10.50

1. PC broadcast Discover (Src 0.0.0.0, Dst 255.255.255.255)
2. R1 nhận trên SVI VLAN 20. Bình thường → VỨT (broadcast không qua router)
3. NHƯNG có ip helper-address →
     R1 đổi gói thành UNICAST tới 10.0.10.50
     và ĐIỀN giaddr = 10.0.20.1 (IP của SVI nhận gói)
4. Server nhìn giaddr = 10.0.20.1 → biết phải cấp IP từ pool 10.0.20.0/24
5. Server trả lời unicast về R1 → R1 chuyển tiếp xuống PC
```

> 🔑 **`giaddr` (gateway address) là linh hồn của DHCP relay.** Không có nó, server
> không biết client ở subnet nào và sẽ cấp IP sai pool.

### Phân giải DNS — đệ quy

```text
PC hỏi: "www.example.com ở đâu?"

PC ──▶ DNS resolver (thường là router hoặc DNS công ty)
         │ Có trong cache? ──▶ trả lời ngay, xong
         │ Không có ↓
         ├──▶ Root server (.)        : "hỏi server của .com"
         ├──▶ TLD server (.com)      : "hỏi ns1.example.com"
         ├──▶ Authoritative server   : "www.example.com = 93.184.x.x"
         └──▶ trả về PC + LƯU CACHE theo TTL của record
```

Lần đầu có thể mất 100–300 ms. Các lần sau lấy từ cache: **< 1 ms**.

### Thứ tự phân giải tên trên máy tính

```text
1. File hosts        (C:\Windows\System32\drivers\etc\hosts  /  /etc/hosts)
2. Cache DNS cục bộ
3. DNS server được cấu hình (thường do DHCP cấp)
```

> 🔧 Thứ tự này rất hữu dụng khi debug: sửa file `hosts` để **ép** một tên trỏ về IP bạn
> muốn, kiểm tra xem vấn đề nằm ở DNS hay ở ứng dụng.

---

## 6. Packet Flow

**Kịch bản:** PC mới bật ở VLAN 20, DHCP server nằm VLAN 10.

| # | Gói | Src IP | Dst IP | Src MAC | Dst MAC | Ghi chú |
|:---:|---|---|---|---|---|---|
| 1 | Discover | `0.0.0.0` | `255.255.255.255` | MAC-PC | `FF:FF:FF:FF:FF:FF` | Switch flood trong VLAN 20 |
| 2 | *(relay)* | `10.0.20.1` | `10.0.10.50` | MAC-R1 | MAC-SRV | R1 đổi thành **unicast**, điền `giaddr` |
| 3 | Offer | `10.0.10.50` | `10.0.20.1` | MAC-SRV | MAC-R1 | Về relay trước |
| 4 | *(relay)* | `10.0.20.1` | broadcast VLAN 20 | MAC-R1 | `FF:FF:...` | R1 chuyển xuống PC |
| 5 | Request | `0.0.0.0` | `255.255.255.255` | MAC-PC | `FF:FF:...` | Lặp lại đường như D |
| 6 | ACK | `10.0.10.50` | → PC | | | PC có IP, gắn mask + GW + DNS |

Sau đó PC mới **ARP tìm gateway** (Lesson 05) rồi mới ra được Internet.

---

## 7. Real-world Example

🏭 **Rogue DHCP server** — sự cố kinh điển:

Một nhân viên cắm router Wi-Fi cá nhân vào mạng công ty. Router đó bật DHCP sẵn.
Máy nào xin IP mà nhận được Offer của nó trước sẽ lấy IP sai, gateway sai → **mất mạng**.

Triệu chứng: *"một số máy mất mạng, một số vẫn bình thường, bật tắt lại thì khác nhau"* —
vì phụ thuộc server nào trả lời nhanh hơn.

Cách chặn: **DHCP Snooping** (Lesson 37) — chỉ cho DHCP reply đi từ port `trust`.

🏭 **"Ping được IP, không ping được tên"**

Bài kiểm tra 10 giây tách bạch mạng và DNS:

```text
ping 8.8.8.8        OK   →  mạng và routing TỐT
ping google.com     FAIL →  lỗi DNS, KHÔNG phải lỗi mạng
```

Không có bài test nào tiết kiệm thời gian bằng cặp lệnh này.

🏭 **DNS cache gây hiểu nhầm**

Vừa đổi A record của website nhưng vẫn vào IP cũ → đang dùng cache, chưa hết TTL.
Xoá cache: `ipconfig /flushdns` (Windows) / `resolvectl flush-caches` (Linux).

> 🔧 Trước khi chuyển server, **giảm TTL của record xuống 300 giây trước vài ngày** —
> để khi cắt chuyển, cả thế giới cập nhật trong 5 phút thay vì 24 giờ.

---

## 8. Cisco CLI

```cisco
! ═══════ ROUTER LÀM DHCP SERVER ═══════
! 1. Loại trừ các IP KHÔNG được cấp (gateway, server, máy in...)
R1(config)# ip dhcp excluded-address 10.0.20.1 10.0.20.49
R1(config)# ip dhcp excluded-address 10.0.20.250 10.0.20.254

! 2. Tạo pool
R1(config)# ip dhcp pool VLAN20-USERS
R1(dhcp-config)# network 10.0.20.0 255.255.255.0
R1(dhcp-config)# default-router 10.0.20.1
R1(dhcp-config)# dns-server 10.0.10.50 8.8.8.8
R1(dhcp-config)# domain-name cty.local
R1(dhcp-config)# lease 0 8 0                ! ngày giờ phút → 8 giờ
R1(dhcp-config)# exit

! Gán IP cố định theo MAC (reservation)
R1(config)# ip dhcp pool PRINTER
R1(dhcp-config)# host 10.0.20.20 255.255.255.0
R1(dhcp-config)# client-identifier 0100.1a2b.3c4d.5e

! ═══════ DHCP RELAY (server ở nơi khác) ═══════
R1(config)# interface vlan 20
R1(config-if)# ip helper-address 10.0.10.50
R1(config-if)# ip helper-address 10.0.10.51     ! có thể khai nhiều server

! ═══════ DNS TRÊN THIẾT BỊ CISCO ═══════
R1(config)# ip domain-lookup                    ! cho phép router phân giải tên
R1(config)# ip name-server 10.0.10.50 8.8.8.8
R1(config)# ip domain-name cty.local
R1(config)# ip host web-server 10.0.1.50        ! bản ghi tĩnh trên router

! Tắt tra DNS khi gõ nhầm lệnh — RẤT NÊN BẬT trong lab
R1(config)# no ip domain-lookup
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `ip dhcp excluded-address` | Chặn cấp các IP đã dùng | **Phải khai TRƯỚC khi tạo pool**, nếu không có thể đã cấp mất |
| `network` trong pool | Dải sẽ cấp | Phải khớp subnet của interface |
| `default-router` | Gateway gửi cho client | Quên dòng này → client có IP nhưng **không ra được ngoài** |
| `ip helper-address` | Biến broadcast DHCP thành unicast | Đặt trên **interface phía client** (SVI của VLAN đó) |
| `no ip domain-lookup` | Tắt tra DNS khi gõ sai lệnh | Không có nó, gõ nhầm lệnh là router treo ~30 giây |

> ⚠️ **`ip helper-address` đặt sai chỗ** là lỗi phổ biến nhất. Nó phải nằm trên interface
> **nhận gói Discover** (phía client), không phải phía server.

> **Khác biệt platform:** `ip helper-address` có trên IOS/IOS-XE. **NX-OS** dùng
> `ip dhcp relay address <ip>` và cần bật `feature dhcp` trước.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp binding
IP address       Client-ID/Hardware address   Lease expiration        Type
10.0.20.50       0100.1a2b.3c4d.5e            Oct 02 2026 08:14 AM    Automatic
10.0.20.51       0100.1a2b.3c4d.6f            Oct 02 2026 08:20 AM    Automatic
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip dhcp pool
Pool VLAN20-USERS :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 254
 Leased addresses               : 2
 Pending event                  : none
 1 subnet is currently in the pool
 Current index  IP address range              Leased addresses
 10.0.20.52     10.0.20.1 - 10.0.20.254       2
```

**Đọc gì:**

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `Leased addresses` | Đã cấp bao nhiêu | Gần bằng `Total` → **sắp hết pool** |
| `Lease expiration` | Khi nào hết hạn | Hết hạn hàng loạt cùng lúc → DORA đồng loạt |
| Không có binding nào | Chưa ai xin được IP | Kiểm tra VLAN, helper-address |

```cisco
! Kiểm tra DNS
R1# ping cty.local
R1# show hosts
```

**Trên máy tính:**

```powershell
ipconfig /all          # xem IP, DHCP server nào cấp, lease tới khi nào
ipconfig /release
ipconfig /renew        # ép DORA lại — xem bằng Wireshark filter: dhcp
ipconfig /flushdns
nslookup google.com
nslookup google.com 8.8.8.8     # hỏi thẳng một DNS server cụ thể
```

---

## 10. Troubleshooting

### DHCP

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Máy nhận `169.254.x.x` | Không tới được DHCP | `show ip dhcp pool` | Kiểm tra: cáp → VLAN port → `ip helper-address` → pool còn IP |
| Nhận IP nhưng **không ra được ngoài** | Thiếu `default-router` trong pool | `ipconfig /all` xem Gateway | Thêm `default-router` |
| Nhận IP nhưng không phân giải tên | Thiếu `dns-server` trong pool | `ipconfig /all` | Thêm `dns-server` |
| Xung đột IP | Quên `excluded-address` | `show ip dhcp conflict` | Khai excluded, `clear ip dhcp conflict *` |
| VLAN khác không nhận IP | Thiếu relay | `show run interface vlan X` | `ip helper-address <server>` |
| Máy nhận IP **sai dải** | **Rogue DHCP server** | Wireshark lọc `dhcp`, xem Src IP của Offer | DHCP Snooping *(Lesson 37)* |
| Hết IP đột ngột | Lease quá dài, hoặc pool nhỏ | `show ip dhcp pool` | Giảm lease / mở rộng pool |

### DNS

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| `ping 8.8.8.8` OK, `ping google.com` fail | **Lỗi DNS** | `nslookup google.com` | Kiểm tra DNS server trong `ipconfig /all` |
| Phân giải sai IP (IP cũ) | Cache chưa hết TTL | `ipconfig /displaydns` | `ipconfig /flushdns` |
| Một số tên được, một số không | DNS server thiếu record / forwarder sai | `nslookup <tên> <dns-khác>` | So sánh 2 DNS server |
| DNS rất chậm | UDP/53 bị drop, đang fallback TCP | Wireshark lọc `dns` | Mở UDP/53 trên firewall |
| Router treo 30 giây khi gõ sai lệnh | Router đang tra DNS cho chuỗi gõ nhầm | — | `no ip domain-lookup` |

---

## 11. LAB

🧪 **Bài lab của lesson này** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md), đánh số **LAB 05**)*

Yêu cầu tối thiểu:

- 2 VLAN, router làm DHCP server cho VLAN 10, **relay** cho VLAN 20
- PC hai VLAN đều nhận đúng IP, đúng gateway, đúng DNS
- Bắt trọn DORA bằng Wireshark, chỉ ra `Src IP = 0.0.0.0` ở Discover
- **BREAK bắt buộc:** (1) xoá `ip helper-address`, (2) xoá `default-router` khỏi pool,
  (3) quên `excluded-address` rồi tạo xung đột

## 12. Challenge

1. Pool cấu hình `network 10.0.20.0 255.255.255.0` nhưng SVI của VLAN 20 là
   `10.0.20.1/25`. Chuyện gì xảy ra?
2. Có **2 DHCP server** cùng phục vụ một VLAN. Client chọn cái nào? Cơ chế nào đảm bảo
   hai server không cấp trùng IP?
3. Vì sao bước **Request** vẫn là **broadcast** dù client đã biết IP của server từ bước Offer?
4. Công ty có 500 máy, lease 8 ngày, pool `/24`. Nêu vấn đề và cách sửa.

<details>
<summary>Đáp án</summary>

**1.** Router sẽ cấp IP trong dải `10.0.20.1 – 10.0.20.254` (theo `/24` của pool), nhưng
SVI chỉ `/25` nên subnet thật là `10.0.20.0 – 10.0.20.127`. Client nhận IP `10.0.20.200`
sẽ **khác subnet với gateway** → có IP nhưng không ping được gateway. Pool và interface
**phải cùng mask**.

**2.** Client thường chọn **Offer đến trước**. Hai server không tự biết nhau, nên:
- Nếu hai server cấu hình **cùng pool** → chắc chắn sẽ cấp trùng IP (thiết kế sai).
- Cách làm đúng: chia pool, mỗi server một nửa dải (vd server A cấp `.50–.149`,
  server B cấp `.150–.249`), hoặc dùng DHCP failover.

Bước **Request** broadcast chính là để server **không được chọn** biết mà thu hồi offer.

**3.** Vì Request phải cho **tất cả** DHCP server nghe thấy, không chỉ server được chọn.
Server bị từ chối cần biết để **giải phóng IP nó đã tạm giữ**. Nếu Request là unicast,
các server khác sẽ giữ IP treo cho tới khi hết timeout → lãng phí pool.

**4.** Vấn đề: `/24` chỉ có 254 IP cho **500 máy** — thiếu. Lease 8 ngày làm IP của máy
đã rời đi vẫn bị giữ rất lâu.

| Cách sửa | Đánh đổi |
|---|---|
| Giảm lease xuống 8–12 giờ | IP quay vòng nhanh, nhưng vẫn không đủ cho 500 máy đồng thời |
| **Chia thành 2+ VLAN**, mỗi VLAN một `/24` | ✅ Giải pháp đúng — vừa đủ IP vừa giảm broadcast domain |
| Mở rộng thành `/23` | Đủ IP nhưng broadcast domain 500 host là quá lớn |

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 4 bước DORA · port 67/68 · DNS dùng TCP khi nào · record A/CNAME/MX/PTR | ⬜ |
| **L2** Explain | Giải thích vì sao DHCP cần relay, dùng kiến thức broadcast | ⬜ |
| **L3** Configure | Cấu hình DHCP server + relay cho 2 VLAN, verify bằng `show ip dhcp binding` | ⬜ |
| **L4** Troubleshoot | Máy nhận `169.254.x.x` → nêu thứ tự 4 bước kiểm tra | ⬜ |
| **L5** Design | Thiết kế DHCP cho công ty 3 VLAN: pool, exclude, lease, reservation | ⬜ |

## 14. Summary

**Key concepts**

- **DORA**: Discover → Offer → Request → ACK. Server UDP **67**, client UDP **68**
- Discover và Request là **broadcast**, `Src IP = 0.0.0.0`
- ⭐ Broadcast dừng ở router → VLAN khác cần **`ip helper-address`**
- `giaddr` cho server biết client ở subnet nào
- Lease gia hạn ở **50%** (T1) và **87.5%** (T2)
- DNS port **53**, UDP cho query, **TCP** khi reply > 512 byte hoặc zone transfer
- Record: **A** (IPv4) · **AAAA** (IPv6) · **CNAME** (bí danh) · **MX** (mail) · **PTR** (ngược)
- ⭐ `ping 8.8.8.8` OK + `ping google.com` fail = **lỗi DNS, không phải lỗi mạng**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip dhcp binding` | Ai đang giữ IP nào |
| `show ip dhcp pool` | Pool còn bao nhiêu IP |
| `ip helper-address <ip>` | Relay DHCP qua router |
| `ip dhcp excluded-address` | Chặn cấp IP đã dùng |
| `no ip domain-lookup` | Tắt treo 30 giây khi gõ nhầm lệnh |
| `nslookup <tên> <dns>` | Hỏi thẳng một DNS server cụ thể |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `excluded-address` | DHCP cấp trùng IP gateway/server |
| Quên `default-router` trong pool | Có IP nhưng không ra được ngoài |
| Đặt `ip helper-address` phía server | Relay không hoạt động — phải đặt phía **client** |
| Pool mask khác interface mask | Client nhận IP khác subnet với gateway |
| Nghĩ DNS chỉ dùng UDP | Chặn TCP/53 gây lỗi khó tìm |
| Quên `no ip domain-lookup` trong lab | Mỗi lần gõ nhầm là treo 30 giây |

## 15. Homework + cập nhật PROGRESS

1. `ipconfig /release` + `/renew`, bắt bằng Wireshark filter `dhcp`.
   Chụp lại 4 gói DORA, chỉ ra Src/Dst IP từng gói.
2. `ipconfig /all` — ghi lại: DHCP server nào cấp, lease tới khi nào, DNS là gì.
3. `nslookup google.com` rồi `nslookup google.com 1.1.1.1` — so sánh kết quả.
4. Làm LAB 05 với đủ 3 lỗi BREAK.

```markdown
- [YYYY-MM-DD] Lesson 08 — DNS & DHCP: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | DORA + địa chỉ từng bước, port 67/68 và 53, helper-address, record type |
| 🔧 **Engineer** | Reservation theo MAC; chọn lease phù hợp; `nslookup` chỉ định DNS để so sánh |
| 🏭 **Production** | Rogue DHCP → cần DHCP Snooping; giảm TTL trước khi chuyển server; pool sắp hết là sự cố chờ xảy ra |

### 🔗 Liên kết

- ⬅️ [Lesson 07 — VLSM & IP Plan](./lesson-07-vlsm-va-ip-plan.md)
- ➡️ [Lesson 09 — NAT](./lesson-09-nat-private-public.md)
- 🔌 [`cheatsheets/ports-va-protocols.md`](../cheatsheets/ports-va-protocols.md)
- 🦈 [`cheatsheets/wireshark.md`](../cheatsheets/wireshark.md)
