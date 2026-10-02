# LESSON 26 — DNS trong doanh nghiệp

> 📦 **Phase 0 đã dạy gì — lesson này thêm gì**
>
> | [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md) *(khái niệm)* | Lesson này *(vận hành)* |
> |---|---|
> | Phân giải đệ quy, record A/CNAME/MX/PTR | **Zone**, forward vs reverse, authoritative vs recursive |
> | `ping IP được, ping tên không` = lỗi DNS | **Split-DNS**, forwarder, conditional forwarding |
> | `nslookup` cơ bản | **TTL strategy** khi chuyển server, debug DNS có phương pháp |
> | — | DNS trên IOS, DNS làm vector tấn công |

| | |
|---|---|
| **Phase** | 3 — Services |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md), [Lesson 06](../00-foundation/lesson-06-tcp-udp-port.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Phân biệt **authoritative** và **recursive** DNS server
- [ ] Giải thích forward zone và reverse zone, biết khi nào cần PTR
- [ ] Hiểu **split-DNS** và vì sao doanh nghiệp cần nó
- [ ] Dùng TTL đúng cách khi chuyển server
- [ ] Debug DNS theo phương pháp, không đoán mò

## 2. Prerequisite

- DNS port 53, UDP và TCP *(Lesson 06, 08)*
- Record type A/AAAA/CNAME/MX/PTR/TXT *(Lesson 08)*

---

## 3. Concept

### Hai vai trò của DNS server

| | **Authoritative** | **Recursive (Resolver)** |
|---|---|---|
| Nhiệm vụ | **Giữ dữ liệu gốc** của một zone | **Đi hỏi hộ** client rồi cache lại |
| Trả lời | "Tôi **là** nguồn sự thật về `cty.vn`" | "Để tôi đi hỏi giùm bạn" |
| Ví dụ | DNS của bạn cho `cty.vn`<br>Cloudflare/Route53 | `8.8.8.8`, `1.1.1.1`<br>DNS server nội bộ công ty |
| Client trỏ vào | ❌ Không | ✅ **Có** |

> ⚠️ **Rất nên tách hai vai trò.** Một server vừa authoritative vừa mở recursive cho
> cả Internet là lỗ hổng kinh điển — bị lợi dụng làm **DNS amplification attack**.

### Zone — forward và reverse

| | **Forward zone** | **Reverse zone** |
|---|---|---|
| Phân giải | **Tên → IP** | **IP → tên** |
| Record chính | `A`, `AAAA` | **`PTR`** |
| Tên zone | `cty.vn` | `10.0.10.in-addr.arpa` |
| Ai cần | Mọi người | Mail server, log, giám sát |

```text
Forward:   web.cty.vn        A     10.0.50.20
Reverse:   20.50.0.10.in-addr.arpa   PTR   web.cty.vn
                └──── IP VIẾT NGƯỢC ────┘
```

> 🔑 Reverse zone viết IP **ngược** vì DNS phân cấp từ **phải sang trái**.
> `cty.vn` → `.vn` là gốc, `cty` là nhánh. Với IP thì `10.` là gốc, `.20` là nhánh —
> nên phải đảo lại cho khớp cấu trúc cây.

> 🏭 **Vì sao PTR quan trọng:** nhiều **mail server từ chối nhận mail** từ IP không có
> PTR record hợp lệ. Nếu công ty bạn tự chạy mail server mà quên PTR, mail gửi đi
> sẽ vào spam hoặc bị reject thẳng.

### Split-DNS — khái niệm quan trọng nhất của lesson

**Cùng một tên, trả lời khác nhau tuỳ người hỏi từ đâu.**

```text
Người hỏi từ BÊN TRONG:        web.cty.vn  →  10.0.50.20   (IP nội bộ)
Người hỏi từ BÊN NGOÀI:        web.cty.vn  →  203.0.113.50 (IP public)
```

| Vì sao cần | Giải thích |
|---|---|
| **Hiệu năng** | Nhân viên truy cập server nội bộ **không phải đi vòng** ra Internet rồi quay lại |
| **Không phụ thuộc NAT hairpin** | Nhiều firewall không hỗ trợ truy cập IP public của chính mình từ bên trong |
| **Bảo mật** | Không lộ cấu trúc IP nội bộ ra ngoài |

Triển khai: DNS server nội bộ giữ zone `cty.vn` với IP nội bộ; DNS công cộng giữ
zone `cty.vn` với IP public. Hai bản ghi độc lập.

> ⚠️ Cái giá: **phải cập nhật hai nơi**. Quên một bên → "bên trong vào được,
> bên ngoài không" hoặc ngược lại. Đây là lỗi vận hành rất phổ biến.

### Forwarder và conditional forwarding

```text
DNS nội bộ:
  cty.local       →  tự trả lời (authoritative)
  mọi thứ khác    →  FORWARD tới 8.8.8.8
  partner.vn      →  CONDITIONAL FORWARD tới 10.9.9.9 (DNS của đối tác, qua VPN)
```

| | Dùng khi |
|---|---|
| **Forwarder** | Mặc định — đẩy mọi truy vấn ngoài cho một resolver công cộng |
| **Conditional forwarding** | Một domain cụ thể phải hỏi một server cụ thể — hay dùng với đối tác qua VPN, hoặc giữa các domain Active Directory |

### TTL — chiến lược khi chuyển server

```text
TRƯỚC khi chuyển (3–7 ngày):   giảm TTL của record xuống 300 giây
NGÀY chuyển:                    đổi A record sang IP mới
                                → cả thế giới cập nhật trong 5 PHÚT
SAU khi ổn định (vài ngày):     tăng TTL trở lại 3600+ giây
```

> 🔑 Nếu không giảm TTL trước, với TTL 86400 (1 ngày) thì sau khi đổi IP,
> **một số người vẫn vào IP cũ suốt 24 giờ** — và bạn không làm gì được.
>
> Đây là một trong những bài học vận hành đáng giá nhất của lesson này.

---

## 4. Why?

> **Vì sao doanh nghiệp cần DNS server riêng, không dùng thẳng 8.8.8.8?**

| Lý do | Giải thích |
|---|---|
| **Phân giải tên nội bộ** | `8.8.8.8` không biết `fileserver.cty.local` là gì |
| **Split-DNS** | Trả IP nội bộ cho người bên trong |
| **Cache tập trung** | 300 máy hỏi cùng một tên → 1 lần đi ra ngoài thay vì 300 |
| **Kiểm soát & lọc** | Chặn domain độc hại ngay ở tầng DNS |
| **Audit** | Biết máy nào truy cập domain nào — rất giá trị khi điều tra sự cố |
| **Active Directory** | AD **bắt buộc** cần DNS nội bộ với record SRV |

> ⚠️ Điểm yếu: DNS nội bộ chết = **cả công ty tưởng mất mạng**. Luôn có **2 DNS server**,
> và cấp cả hai qua DHCP.

---

## 5. How does it work? — truy vấn trong doanh nghiệp

```text
PC hỏi "web.cty.vn"
  │
  ▼
DNS nội bộ 10.0.50.10
  ├─ Có trong zone cty.vn?        → trả lời ngay (authoritative)  ✅
  ├─ Có trong cache?               → trả lời ngay
  └─ Không có ↓
       Forward tới 8.8.8.8
         └─ 8.8.8.8 đi hỏi root → TLD → authoritative
       ◀─ trả về
  Lưu cache theo TTL → trả cho PC
```

### Thứ tự phân giải trên máy client

```text
1. File hosts        (C:\Windows\System32\drivers\etc\hosts  /  /etc/hosts)
2. Cache DNS cục bộ   (ipconfig /displaydns)
3. DNS server #1      (do DHCP cấp)
4. DNS server #2      (nếu #1 không trả lời)
```

> 🔧 **Mẹo debug:** sửa file `hosts` để ép một tên trỏ về IP bạn muốn.
> Nếu ứng dụng chạy được → vấn đề ở DNS. Nếu vẫn hỏng → vấn đề ở ứng dụng/mạng.
> Nhớ xoá dòng đó sau khi test.

---

## 6. Packet Flow — khi nào DNS dùng TCP

| Tình huống | Giao thức |
|---|---|
| Truy vấn thường, reply < 512 byte | **UDP/53** |
| Reply **> 512 byte** → cờ `TC` (truncated) bật → client hỏi lại | **TCP/53** |
| **Zone transfer** (AXFR/IXFR) giữa các DNS server | **TCP/53** |
| DNSSEC *(chữ ký dài)* | Thường **TCP/53** |

> ⚠️ Firewall chỉ mở **UDP/53** là lỗi rất khó tìm: phần lớn truy vấn chạy bình thường,
> nhưng một số domain (nhiều record, có DNSSEC) **thỉnh thoảng** không phân giải được.
> Triệu chứng kiểu "lúc được lúc không" — luôn kiểm tra TCP/53.

---

## 7. Real-world Example

🏭 **Thiết kế DNS cho công ty 300 người**

```text
┌─────────────────────────────────────────────┐
│  DNS1 10.0.50.10   DNS2 10.0.50.11          │  ← nội bộ, authoritative cho cty.local
│  - Zone cty.local (forward)                  │     + recursive cho nhân viên
│  - Zone 10.in-addr.arpa (reverse)            │
│  - Forwarder → 8.8.8.8, 1.1.1.1              │
└──────────────┬──────────────────────────────┘
               │ DHCP cấp cả 2 cho client
               ▼
         300 máy nhân viên

┌─────────────────────────────────────────────┐
│  DNS công cộng (Cloudflare / nhà cung cấp)  │  ← authoritative cho cty.vn
│  - Zone cty.vn với IP PUBLIC                 │     (split-DNS)
└─────────────────────────────────────────────┘
```

🏭 **Sự cố kinh điển: "mạng chậm" hoá ra là DNS**

Triệu chứng: mở web mất 5–10 giây rồi mới load, nhưng load xong thì nhanh.

```text
DNS1 chết. Client hỏi DNS1 → timeout (~5 giây) → mới hỏi DNS2 → trả lời nhanh.
Mỗi tên miền mới = thêm 5 giây chờ.
```

> 🔧 Chẩn đoán: `nslookup google.com 10.0.50.10` — nếu timeout thì DNS1 đã chết.
> Người dùng mô tả là "mạng chậm", nhưng `ping 8.8.8.8` hoàn toàn bình thường.

🏭 **Lỗi split-DNS: quên cập nhật một bên**

Chuyển web server sang IP public mới. Cập nhật DNS công cộng, **quên** DNS nội bộ.
Kết quả: khách hàng vào được, **nhân viên thì không**. Hoặc ngược lại.

> 🔧 Quy trình: mỗi lần đổi IP của một dịch vụ có split-DNS, **checklist 2 mục** —
> zone ngoài và zone trong.

🏭 **DNS làm vector tấn công**

| Tấn công | Cách hoạt động | Phòng chống |
|---|---|---|
| **DNS amplification** | Gửi truy vấn giả danh nạn nhân tới resolver mở → resolver dội reply lớn vào nạn nhân | Không mở recursive ra Internet |
| **DNS tunneling** | Mã hoá dữ liệu vào tên miền để tuồn data ra ngoài, vượt firewall | Giám sát truy vấn bất thường (tên dài, tần suất cao) |
| **DNS spoofing/cache poisoning** | Bơm bản ghi giả vào cache resolver | DNSSEC, cập nhật phần mềm DNS |

---

## 8. Cisco CLI

```cisco
! ═══════ DNS CLIENT TRÊN THIẾT BỊ CISCO ═══════
R1(config)# ip domain-lookup                  ! cho phép router phân giải tên
R1(config)# ip name-server 10.0.50.10 10.0.50.11
R1(config)# ip domain-name cty.local

! Bản ghi tĩnh trên router (như file hosts)
R1(config)# ip host web-server 10.0.50.20
R1(config)# ip host backup-srv 10.0.50.21 10.0.50.22   ! nhiều IP

! ⚠️ TẮT tra DNS khi gõ nhầm lệnh — RẤT NÊN trong lab
R1(config)# no ip domain-lookup

! ═══════ ROUTER LÀM DNS SERVER NHỎ (chi nhánh) ═══════
R1(config)# ip dns server
R1(config)# ip host printer.cty.local 10.0.10.20

! ═══════ CẤP DNS QUA DHCP ═══════
R1(config)# ip dhcp pool VLAN10
R1(dhcp-config)# dns-server 10.0.50.10 10.0.50.11
R1(dhcp-config)# domain-name cty.local

! ═══════ KIỂM TRA ═══════
R1# show hosts
R1# ping web-server
R1# debug domain
R1# undebug all
```

| Lệnh | Lưu ý |
|---|---|
| `ip domain-lookup` | Mặc định **bật** — gõ nhầm lệnh là treo 30 giây |
| `no ip domain-lookup` | ⭐ Nên bật trong lab và cả nhiều môi trường production |
| `ip name-server` | Tối đa 6 server |
| `ip host` | Bản ghi tĩnh — hữu dụng khi DNS chưa sẵn sàng |
| `ip dns server` | Router làm DNS server đơn giản, chỉ cho chi nhánh nhỏ |

**Trên máy tính:**

```powershell
# Windows
nslookup web.cty.vn                    # dùng DNS mặc định
nslookup web.cty.vn 8.8.8.8            # hỏi THẲNG một server cụ thể
nslookup -type=MX cty.vn
nslookup -type=PTR 10.0.50.20
ipconfig /displaydns
ipconfig /flushdns

# Linux
dig web.cty.vn
dig @8.8.8.8 web.cty.vn
dig +short web.cty.vn
dig -x 10.0.50.20                      # reverse lookup
dig cty.vn MX
```

> 🔧 **`nslookup <tên> <server>` là lệnh debug DNS quan trọng nhất.**
> So kết quả giữa DNS nội bộ và DNS công cộng là ra ngay vấn đề nằm ở đâu.

---

## 9. Verification

```text
# output điển hình — tự verify trên máy bạn
C:\> nslookup web.cty.vn 10.0.50.10
Server:  dns1.cty.local
Address: 10.0.50.10

Name:    web.cty.vn
Address: 10.0.50.20          ← IP NỘI BỘ (split-DNS hoạt động ✅)

C:\> nslookup web.cty.vn 8.8.8.8
Server:  dns.google
Address: 8.8.8.8

Non-authoritative answer:
Name:    web.cty.vn
Address: 203.0.113.50        ← IP PUBLIC
```

**Đọc gì:**

| Dấu hiệu | Ý nghĩa |
|---|---|
| `Non-authoritative answer` | Server này **không giữ** zone đó, nó trả lời từ cache |
| Không có dòng đó | Server **authoritative** cho zone này |
| Hai server trả **IP khác nhau** | ✅ Split-DNS đang hoạt động đúng |
| `*** Request timed out` | DNS server đó không phản hồi |
| `Non-existent domain (NXDOMAIN)` | Tên **không tồn tại** — khác với timeout |

```text
# output điển hình — tự verify trên lab của bạn
R1# show hosts
Default domain is cty.local
Name/address lookup uses domain service
Name servers are 10.0.50.10, 10.0.50.11

Host                     Port  Flags      Age Type   Address(es)
web-server               None  (perm, OK)  0   IP    10.0.50.20
google.com               None  (temp, OK)  2   IP    142.250.x.x
```

| Flag | Nghĩa |
|---|---|
| `perm` | Bản ghi tĩnh do `ip host` |
| `temp` | Học được từ DNS, sẽ hết hạn |
| `OK` / `EX` | Còn hiệu lực / đã hết hạn |

---

## 10. Troubleshooting — quy trình 5 bước

> 🔴 Chạy đúng thứ tự này, đừng đoán.

| # | Bước | Lệnh | Nếu fail |
|:---:|---|---|---|
| 1 | Mạng có thông không? | `ping 8.8.8.8` | ❌ → **không phải lỗi DNS**, quay lại Phase 2 |
| 2 | DNS server có sống không? | `ping <dns-server>` | ❌ → server chết hoặc không tới được |
| 3 | Server có phân giải được không? | `nslookup <tên> <dns-server>` | ❌ → vấn đề ở server/zone |
| 4 | So với DNS công cộng | `nslookup <tên> 8.8.8.8` | Khác nhau → split-DNS hoặc record sai |
| 5 | Client đang dùng DNS nào? | `ipconfig /all` | Sai → sửa DHCP hoặc cấu hình tay |

### Bảng triệu chứng

| Triệu chứng | Giả thuyết | Cách sửa |
|---|---|---|
| `ping IP` OK, `ping tên` fail | **Lỗi DNS** | Chạy quy trình 5 bước |
| Web mở chậm 5–10 giây rồi mới load | DNS server #1 **chết**, đang timeout rồi fallback #2 | `nslookup <tên> <dns1>` |
| Trả về IP cũ sau khi đã đổi record | **Cache chưa hết TTL** | `ipconfig /flushdns`; lần sau giảm TTL trước |
| Một số tên được, một số không | Zone thiếu record, hoặc forwarder sai | So `nslookup` giữa 2 server |
| Bên trong vào được, bên ngoài không | **Split-DNS lệch** — quên cập nhật một zone | Cập nhật zone còn lại |
| Lúc được lúc không với vài domain | Firewall chặn **TCP/53** | Mở TCP/53 |
| Mail gửi đi bị reject/spam | Thiếu **PTR record** | Yêu cầu ISP tạo PTR cho IP public |
| Router treo 30 giây khi gõ nhầm lệnh | `ip domain-lookup` đang bật | `no ip domain-lookup` |
| Truy vấn DNS bất thường, tên rất dài | Nghi **DNS tunneling** | Giám sát, chặn resolver ngoài |

---

## 11. LAB

🧪 **LAB 31 — DNS trong doanh nghiệp** → [`../labs/lab31-dns-noi-bo.md`](../labs/lab31-dns-noi-bo.md)

Yêu cầu tối thiểu:

- Server DNS trong Packet Tracer với zone nội bộ, client phân giải được tên nội bộ
- Cấp DNS qua DHCP, verify bằng `ipconfig /all`
- Dùng `ip host` trên router làm bản ghi tĩnh, so với phân giải qua DNS server
- Trên máy thật: `nslookup` một tên với 3 server khác nhau, so kết quả và thời gian
- **BREAK bắt buộc:** (1) tắt DNS server → đo thời gian timeout của client;
  (2) cấp DNS sai qua DHCP → quan sát triệu chứng; (3) thêm dòng sai vào file `hosts`
  → chứng minh nó **thắng** DNS server

## 12. Challenge

1. `ping 8.8.8.8` OK, `ping google.com` fail, nhưng `nslookup google.com 8.8.8.8` **thành công**.
   Vấn đề ở đâu?
2. Bạn sắp chuyển web server sang IP mới sau 3 ngày. Làm gì **ngay bây giờ**?
3. Công ty có `web.cty.vn`. Nhân viên vào được, khách hàng báo không vào được.
   Nêu 2 nguyên nhân liên quan DNS.
4. Vì sao không nên để DNS server vừa authoritative vừa mở recursive ra Internet?

<details>
<summary>Đáp án</summary>

**1.** `nslookup ... 8.8.8.8` thành công → bản thân DNS **công cộng** phân giải được.
Nhưng `ping google.com` dùng **DNS được cấu hình trên máy** — và nó đang hỏng.

Nguyên nhân: DNS server mà client đang dùng (do DHCP cấp hoặc gán tay) không hoạt động,
hoặc không forward ra ngoài được.

Kiểm chứng: `ipconfig /all` xem DNS đang dùng là gì, rồi `nslookup google.com <dns-đó>`.

**2.** **Giảm TTL của A record xuống 300 giây — ngay hôm nay.**

Lý do: TTL hiện tại (giả sử 86400 = 1 ngày) phải **hết hạn** ở mọi resolver trên thế giới
thì giá trị TTL mới mới có hiệu lực. Giảm trước 3 ngày đảm bảo đến ngày chuyển,
mọi resolver đều đang dùng TTL 300.

Kết quả: cắt chuyển xong, cả thế giới cập nhật trong **5 phút** thay vì 24 giờ.
Sau khi ổn định vài ngày, tăng TTL lại để giảm tải DNS.

**3.** Hai nguyên nhân:

| # | Nguyên nhân | Kiểm chứng |
|:---:|---|---|
| 1 | **Split-DNS lệch** — zone nội bộ đã cập nhật IP mới, zone công cộng chưa | `nslookup web.cty.vn 8.8.8.8` từ bên ngoài |
| 2 | Zone công cộng đúng nhưng **A record trỏ IP public sai**, hoặc NAT/firewall chưa mở | `nslookup` từ ngoài + `telnet <ip-public> 443` |

**4.** Vì **DNS amplification attack**:

```text
1. Kẻ tấn công gửi truy vấn DNS nhỏ (~60 byte) tới resolver mở
2. GIẢ MẠO source IP = IP của nạn nhân
3. Resolver trả lời — reply có thể lớn gấp 50–100 lần
4. Toàn bộ reply dội vào NẠN NHÂN
5. Hàng nghìn resolver mở → DDoS khổng lồ
```

Server của bạn trở thành **vũ khí tấn công người khác**, và chính nó cũng bị quá tải.

Cách đúng: **tách vai trò** — authoritative server chỉ trả lời về zone của mình,
không recursive; recursive server chỉ phục vụ **IP nội bộ**.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Authoritative vs recursive · forward vs reverse zone · khi nào DNS dùng TCP | ⬜ |
| **L2** Explain | Giải thích split-DNS và vì sao doanh nghiệp cần | ⬜ |
| **L3** Configure | `ip name-server`, `ip host`, cấp DNS qua DHCP | ⬜ |
| **L4** Troubleshoot | Chạy đủ quy trình 5 bước cho một sự cố DNS | ⬜ |
| **L5** Design | Thiết kế DNS cho công ty có web public + file server nội bộ | ⬜ |

## 14. Summary

**Key concepts**

- **Authoritative** giữ dữ liệu gốc · **Recursive** đi hỏi hộ và cache
- ⚠️ Không để một server vừa authoritative vừa mở recursive ra Internet → **amplification**
- **Forward zone** tên→IP (`A`) · **Reverse zone** IP→tên (`PTR`, IP viết ngược)
- PTR cần cho **mail server** — thiếu là mail bị reject
- ⭐ **Split-DNS**: cùng tên, trả IP nội bộ cho người trong, IP public cho người ngoài
- ⭐ **Giảm TTL xuống 300s trước vài ngày** khi sắp chuyển server
- DNS dùng **TCP/53** khi reply > 512 byte, zone transfer, DNSSEC
- Thứ tự phân giải client: **hosts → cache → DNS#1 → DNS#2**
- Luôn cấp **2 DNS server** qua DHCP

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `nslookup <tên> <server>` | ⭐ So kết quả giữa các DNS server |
| `dig +short <tên>` / `dig -x <ip>` | Linux — gọn và mạnh hơn |
| `ipconfig /flushdns` | Xoá cache sau khi đổi record |
| `ipconfig /displaydns` | Xem cache hiện tại |
| `ip name-server` / `ip host` | DNS trên thiết bị Cisco |
| `no ip domain-lookup` | Tắt treo 30 giây khi gõ nhầm |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Chỉ mở UDP/53 trên firewall | Một số domain "lúc được lúc không" |
| Đổi IP mà không giảm TTL trước | Một phần thế giới vẫn vào IP cũ cả ngày |
| Quên cập nhật một bên của split-DNS | Trong vào được, ngoài không — hoặc ngược lại |
| Chỉ cấp 1 DNS server qua DHCP | DNS chết = cả công ty tưởng mất mạng |
| Nghĩ "mạng chậm" là lỗi mạng | 5 giây timeout DNS trông y hệt mạng chậm |
| Quên PTR cho mail server | Mail vào spam hoặc bị reject |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 31 với đủ 3 lỗi BREAK.
2. Chạy `nslookup google.com` với 3 server: DNS công ty, `8.8.8.8`, `1.1.1.1`.
   So kết quả và thời gian phản hồi.
3. `dig -x 8.8.8.8` (hoặc `nslookup -type=PTR 8.8.8.8`) — xem PTR của Google là gì.
4. Kiểm tra công ty bạn có dùng split-DNS không: so `nslookup <tên-web-công-ty>`
   từ trong và từ mạng 4G.

```markdown
- [YYYY-MM-DD] Lesson 26 — DNS doanh nghiệp: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Record type, forward/reverse zone, DNS dùng UDP và TCP khi nào |
| 🔧 **Engineer** | `nslookup <tên> <server>` để khoanh vùng; 2 DNS qua DHCP; `no ip domain-lookup` |
| 🏭 **Production** | TTL strategy khi chuyển server; split-DNS phải cập nhật 2 nơi; PTR cho mail; DNS là vector tấn công |

### 🔗 Liên kết

- ⬅️ [Lesson 25 — DHCP triển khai](./lesson-25-dhcp-trien-khai.md)
- 📚 Nền tảng: [Lesson 08 — DNS & DHCP](../00-foundation/lesson-08-dns-va-dhcp.md)
- ➡️ [Lesson 27 — NAT nâng cao](./lesson-27-nat-nang-cao.md)
