# LESSON 28 — NTP · Syslog · SNMP · QoS fundamentals

> 📌 Lesson về **management plane** — những dịch vụ không chở dữ liệu người dùng,
> nhưng thiếu chúng thì bạn **vận hành mù**.

| | |
|---|---|
| **Phase** | 3 — Services |
| **Thời lượng** | ~3 giờ |
| **Prerequisite** | [Lesson 06](../00-foundation/lesson-06-tcp-udp-port.md), [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Giải thích vì sao **NTP là nền móng** của mọi thứ còn lại
- [ ] Đọc syslog, hiểu **8 severity level** và chọn mức log phù hợp
- [ ] Phân biệt SNMP **polling** và **trap**, biết v2c khác v3 ở đâu
- [ ] Giải thích QoS giải quyết vấn đề gì và 3 mô hình xử lý
- [ ] Cấu hình bộ quản trị tối thiểu cho một thiết bị production

## 2. Prerequisite

- Port UDP 123, 514, 161/162 *(Lesson 06)*
- Cấu hình cơ bản thiết bị, `logging synchronous` *(Lesson 12)*

---

# PHẦN A — NTP

## 3A. Concept

**NTP** (Network Time Protocol) đồng bộ đồng hồ thiết bị. **UDP port 123**.

### Stratum — khoảng cách tới nguồn thời gian chuẩn

| Stratum | Là gì |
|:---:|---|
| **0** | Nguồn chuẩn: đồng hồ nguyên tử, GPS |
| **1** | Server nối trực tiếp stratum 0 |
| **2** | Server đồng bộ từ stratum 1 |
| … | Mỗi bậc cộng 1 |
| **16** | **Không đồng bộ** — không dùng được |

> 🔑 Stratum càng cao càng xa nguồn chuẩn → càng kém chính xác.
> Thiết bị chọn server có **stratum thấp nhất**.

### Vì sao NTP là nền móng

| Thiếu NTP → hỏng gì |
|---|
| **Syslog vô nghĩa** — không correlate được sự kiện giữa các thiết bị |
| **Chứng chỉ TLS lỗi** — "certificate not yet valid" dù chứng chỉ đúng |
| **Kerberos/AD hỏng** — lệch > 5 phút là không đăng nhập được |
| **Backup/scheduled job sai giờ** |
| **Điều tra sự cố bất khả thi** — không biết cái gì xảy ra trước |

> ⭐ **Đây là lý do NTP phải cấu hình TRƯỚC mọi thứ khác.**
> Một hệ thống log đẹp nhưng sai giờ thì vô dụng.

---

# PHẦN B — SYSLOG

## 3B. Concept

**Syslog** gửi thông điệp sự kiện từ thiết bị tới một server tập trung. **UDP 514**.

### Cấu trúc một dòng syslog Cisco

```text
# dòng syslog điển hình — tự verify trên lab của bạn
*Oct  2 14:23:51.123: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to down
└──────┬──────────┘  └────┬────┘ │ └──┬─┘  └──────────────────┬──────────────────┘
   timestamp         FACILITY  SEV  MNEMONIC              mô tả
```

| Phần | Nghĩa |
|---|---|
| **Facility** | Hệ thống con sinh ra log: `LINEPROTO`, `OSPF`, `SPANTREE`, `SYS` |
| **Severity** | Mức nghiêm trọng **0–7** |
| **Mnemonic** | Mã sự kiện cụ thể |

### 8 severity level — phải thuộc

| Số | Tên | Nghĩa | Ví dụ |
|:---:|---|---|---|
| **0** | Emergency | Hệ thống không dùng được | |
| **1** | Alert | Cần xử lý ngay | Nhiệt độ quá cao |
| **2** | Critical | Nghiêm trọng | Lỗi phần cứng |
| **3** | **Error** | Lỗi | Interface err-disabled |
| **4** | Warning | Cảnh báo | Native VLAN mismatch |
| **5** | **Notification** | Bình thường nhưng đáng chú ý | **Interface up/down** |
| **6** | Informational | Thông tin | ACL match, NAT |
| **7** | Debugging | Debug | Output của `debug` |

> 💡 Cách nhớ: **E**mergency **A**lert **C**ritical **E**rror **W**arning **N**otification
> **I**nformational **D**ebugging → *"Every Awesome Cisco Engineer Will Need Ice-cream Daily"*.

> 🔑 **Cấu hình mức N nghĩa là log mức 0 → N.** `logging trap 5` gửi severity 0–5.
> Đặt `7` trên production = ngập log, có thể làm nghẽn cả CPU lẫn đường truyền.

### Nên đặt mức nào

| Đích | Mức khuyến nghị | Vì sao |
|---|:---:|---|
| Console | **5** hoặc thấp hơn | Tránh spam màn hình khi đang gõ |
| Buffer (RAM thiết bị) | **6** | Đủ chi tiết để debug tại chỗ |
| Syslog server | **5–6** | Cân giữa chi tiết và dung lượng |
| Khi đang debug | 7 tạm thời | ⚠️ **Nhớ trả lại** |

---

# PHẦN C — SNMP

## 3C. Concept

**SNMP** (Simple Network Management Protocol) để **giám sát và quản lý** thiết bị.

| Vai trò | Port |
|---|---|
| **Polling** — NMS hỏi thiết bị | **UDP 161** |
| **Trap/Inform** — thiết bị chủ động báo | **UDP 162** |

### Polling vs Trap

| | **Polling** | **Trap** |
|---|---|---|
| Ai chủ động | **NMS hỏi** thiết bị | **Thiết bị báo** NMS |
| Tần suất | Định kỳ (vd 5 phút) | Khi **có sự kiện** |
| Dùng cho | Số liệu: băng thông, CPU, nhiệt độ | Sự kiện: interface down, cấu hình thay đổi |
| Nhược | Chậm phát hiện sự cố giữa 2 lần poll | Mất gói là mất luôn *(UDP)* |

> 💡 **Inform** giống trap nhưng **có xác nhận** (NMS phải ACK) → không mất.
> Đổi lại tốn tài nguyên hơn. Dùng cho sự kiện quan trọng.

### Phiên bản

| Version | Bảo mật | Nên dùng? |
|---|---|---|
| v1 | Community string, plaintext | ❌ Không |
| **v2c** | Community string, **plaintext** | ⚠️ Phổ biến nhưng **không an toàn** |
| **v3** | **Xác thực + mã hoá** (user/password) | ✅ **Nên dùng** |

> ⚠️ **SNMP v2c community string đi plaintext trên đường truyền.** Ai bắt được gói là
> đọc được. Community `public`/`private` mặc định là lỗ hổng kinh điển — bị quét tự động
> trên Internet hàng ngày.
>
> Nếu buộc dùng v2c: đổi community string, và **giới hạn bằng ACL** chỉ cho NMS truy cập.

### MIB và OID

```text
MIB = cuốn từ điển: "thiết bị có những thông tin gì"
OID = địa chỉ của một thông tin cụ thể

1.3.6.1.2.1.1.5.0        → sysName (tên thiết bị)
1.3.6.1.2.1.2.2.1.10.1   → ifInOctets của interface 1 (số byte nhận)
```

---

# PHẦN D — QoS FUNDAMENTALS

## 3D. Concept

**QoS** (Quality of Service) = quyết định **gói nào được ưu tiên** khi đường truyền nghẽn.

> ⚠️ QoS **không tạo ra băng thông**. Nó chỉ quyết định **ai bị hy sinh** khi thiếu.
> Nếu đường truyền luôn thừa, QoS không có tác dụng gì.

### Ba vấn đề QoS giải quyết

| Vấn đề | Nghĩa | Ảnh hưởng nhiều nhất tới |
|---|---|---|
| **Delay (latency)** | Thời gian gói đi từ A tới B | Thoại, game |
| **Jitter** | **Độ biến thiên** của delay | **Thoại** — tệ hơn cả delay |
| **Packet loss** | Mất gói | Thoại, video |

**Ngưỡng cho VoIP:**

| Chỉ số | Ngưỡng chấp nhận |
|---|---|
| Delay một chiều | **< 150 ms** |
| Jitter | **< 30 ms** |
| Packet loss | **< 1%** |

### Ba mô hình QoS

| Mô hình | Cách làm | Thực tế |
|---|---|---|
| **Best Effort** | Không làm gì — ai tới trước phục vụ trước | Mặc định |
| **IntServ** | Đặt chỗ trước băng thông (RSVP) | ❌ Không scale, hiếm dùng |
| **DiffServ** | **Đánh dấu** gói rồi xử lý theo nhóm | ✅ **Chuẩn thực tế** |

### Marking — đánh dấu gói

| Tầng | Trường | Giá trị |
|---|---|---|
| **L2** | CoS *(trong 802.1Q tag)* | 0–7 |
| **L3** | **DSCP** *(trong IP header)* | 0–63 |

**DSCP cần nhớ:**

| DSCP | Tên | Dùng cho |
|:---:|---|---|
| **46** | **EF** (Expedited Forwarding) | **Thoại** — ưu tiên cao nhất |
| 34 | AF41 | Video hội nghị |
| 26 | AF31 | Báo hiệu (signaling) |
| 18 | AF21 | Dữ liệu quan trọng |
| **0** | **BE** (Best Effort) | Mặc định |

> 🔑 **Nguyên tắc vàng: đánh dấu càng gần nguồn càng tốt** — lý tưởng là ngay tại
> access switch, nơi gói vừa vào mạng. Càng xa càng khó phân biệt.

### Bốn công cụ xử lý

| Công cụ | Làm gì | Khi vượt giới hạn |
|---|---|---|
| **Classification** | Phân loại gói vào nhóm | — |
| **Marking** | Gắn nhãn DSCP/CoS | — |
| **Queuing** | Xếp hàng theo ưu tiên | Gói ưu tiên thấp chờ lâu hơn |
| **Policing** | Giới hạn tốc độ | **DROP** gói vượt |
| **Shaping** | Giới hạn tốc độ | **ĐỆM** gói vượt rồi gửi sau |

> 🔑 **Policing vs Shaping** — câu hỏi kinh điển:
> **Policing drop** (nghiêm khắc, không tốn buffer, gây mất gói).
> **Shaping đệm** (mềm dẻo, tốn buffer, tăng delay).
>
> ISP thường **police**; bạn thường **shape** để khớp tốc độ ISP bán cho mình.

### Trust boundary

```text
IP Phone ──▶ Access Switch ──▶ ... ──▶ Core
   │              │
 đánh dấu      TIN (trust) nhãn của phone
 EF cho thoại  nhưng KHÔNG tin nhãn của PC cắm sau phone
```

> ⚠️ Nếu tin nhãn của PC, bất kỳ ai cũng có thể tự đánh dấu traffic của mình là **EF**
> và chiếm hết ưu tiên. **Trust boundary** là ranh giới nơi bạn ngừng tin nhãn từ bên ngoài.

---

## 4. Why? — vì sao gộp 4 chủ đề này vào một lesson

Vì chúng cùng thuộc **management plane** và **phụ thuộc lẫn nhau**:

```text
NTP  ──▶ cho Syslog và SNMP có timestamp đúng
          │
Syslog ──▶ ghi lại CHUYỆN GÌ đã xảy ra
SNMP  ──▶ đo SỐ LIỆU: bao nhiêu, bao lâu
          │
          ▼
    Giám sát & điều tra sự cố
          │
QoS  ◀────┘  dùng số liệu đó để biết nên ưu tiên gì
```

> 🏭 Một thiết bị production **chưa cấu hình xong** nếu thiếu: NTP, syslog về server
> tập trung, SNMP cho hệ thống giám sát. Ba thứ này nên nằm trong **"config chuẩn"**
> bạn viết ở [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md).

---

## 8. Cisco CLI

```cisco
! ═══════ NTP ═══════
R1(config)# ntp server 10.0.50.30 prefer
R1(config)# ntp server 1.vn.pool.ntp.org
R1(config)# clock timezone ICT 7                      ! Việt Nam UTC+7
R1(config)# service timestamps log datetime msec localtime show-timezone
R1(config)# service timestamps debug datetime msec localtime

! Router làm NTP server cho mạng nội bộ
R1(config)# ntp master 3

! Xác thực NTP (chống NTP giả)
R1(config)# ntp authenticate
R1(config)# ntp authentication-key 1 md5 <key>
R1(config)# ntp trusted-key 1
R1(config)# ntp server 10.0.50.30 key 1

! ═══════ SYSLOG ═══════
R1(config)# logging host 10.0.50.40
R1(config)# logging trap notifications          ! mức 5 → server
R1(config)# logging buffered 32768 informational ! mức 6 → RAM, 32KB
R1(config)# logging console notifications        ! mức 5 → console
R1(config)# logging source-interface Loopback0   ! log luôn từ 1 IP cố định
R1(config)# logging origin-id hostname

! ═══════ SNMP v2c (nếu buộc phải dùng) ═══════
R1(config)# access-list 10 permit 10.0.50.41      ! CHỈ NMS
R1(config)# snmp-server community Str0ngStr1ng RO 10
R1(config)# snmp-server location "DC1-Rack12"
R1(config)# snmp-server contact "it@cty.vn"
R1(config)# snmp-server host 10.0.50.41 version 2c Str0ngStr1ng
R1(config)# snmp-server enable traps

! ═══════ SNMP v3 — NÊN DÙNG ═══════
R1(config)# snmp-server group MONITOR v3 priv
R1(config)# snmp-server user nms-user MONITOR v3 auth sha <authpass> priv aes 128 <privpass>
R1(config)# snmp-server host 10.0.50.41 version 3 priv nms-user

! ═══════ QoS cơ bản ═══════
R1(config)# class-map match-all VOICE
R1(config-cmap)# match ip dscp ef
R1(config)# policy-map WAN-OUT
R1(config-pmap)# class VOICE
R1(config-pmap-c)#  priority percent 20              ! LLQ cho thoại
R1(config-pmap)# class class-default
R1(config-pmap-c)#  fair-queue
R1(config)# interface GigabitEthernet0/1
R1(config-if)# service-policy output WAN-OUT

! Trust boundary trên access switch
SW1(config-if)# mls qos trust device cisco-phone
SW1(config-if)# mls qos trust cos

! ═══════ KIỂM TRA ═══════
R1# show ntp status
R1# show ntp associations
R1# show clock detail
R1# show logging
R1# show snmp
R1# show policy-map interface GigabitEthernet0/1
```

| Lệnh | Lưu ý |
|---|---|
| `clock timezone ICT 7` | ⚠️ Thiếu → log hiện giờ UTC, lệch 7 tiếng |
| `service timestamps log datetime msec` | ⭐ Không có → log chỉ có uptime, vô dụng |
| `logging source-interface Loopback0` | Log luôn từ một IP cố định, dễ lọc trên server |
| `logging trap <mức>` | Gửi mức **0 → N** |
| `snmp-server community ... RO <acl>` | ⚠️ **Luôn kèm ACL** |
| `priority percent 20` | LLQ — hàng đợi ưu tiên tuyệt đối cho thoại |

> **Khác biệt platform:** NX-OS dùng `ntp server`, `logging server`, `snmp-server` tương tự
> nhưng QoS dùng MQC khác đôi chút. Catalyst đời mới bỏ `mls qos`, dùng
> `auto qos` hoặc MQC trực tiếp.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ntp status
Clock is synchronized, stratum 3, reference is 10.0.50.30
nominal freq is 250.0000 Hz, actual freq is 249.9989 Hz, precision is 2**18
reference time is E7A3B2C1.1F2E3D4C (14:23:51.121 ICT Thu Oct 2 2026)
clock offset is 1.2345 msec, root delay is 12.34 msec
```

| Dòng | Ý nghĩa | Bất thường |
|---|---|---|
| `Clock is synchronized` | ✅ Đã đồng bộ | **`unsynchronized`** → NTP chưa hoạt động |
| `stratum 3` | Cách nguồn chuẩn 3 bậc | **16** = không đồng bộ |
| `clock offset` | Lệch bao nhiêu ms | > vài trăm ms → có vấn đề |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ntp associations
  address         ref clock       st   when   poll reach  delay  offset   disp
*~10.0.50.30      .GPS.            2     23     64   377  1.234   0.123  0.456
 ~1.2.3.4         10.1.1.1         3    102   1024   177 24.567   2.345  1.234
 * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured
```

| Ký hiệu | Nghĩa |
|---|---|
| `*` | **Server đang được dùng** |
| `+` | Ứng viên dự phòng |
| `x` | **Falseticker** — giờ sai lệch, bị loại |
| `reach 377` | Octal `377` = 8/8 lần poll gần nhất đều thành công ✅ |
| `reach 0` | Không liên lạc được |

```text
# output điển hình — tự verify trên lab của bạn
R1# show logging
Syslog logging: enabled
    Console logging: level notifications, 142 messages logged
    Buffer logging: level informational, 1847 messages logged
    Trap logging: level notifications, 1203 message lines logged
        Logging to 10.0.50.40 (udp port 514, audit disabled, link up), 1203 message lines logged

Log Buffer (32768 bytes):
*Oct  2 14:23:51.123 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface Gi0/1, changed state to down
*Oct  2 14:23:55.871 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Gi0/1 from FULL to DOWN
```

> 🔑 Hai dòng log trên **kể một câu chuyện**: interface xuống trước (14:23:51),
> OSPF neighbor mất sau 4 giây (14:23:55). Nguyên nhân → hệ quả.
>
> **Không có NTP thì không đọc được câu chuyện này** khi so log giữa nhiều thiết bị.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| `show ntp status` → `unsynchronized` | Không tới được NTP server, hoặc UDP/123 bị chặn | `ping <ntp-server>`, `show ntp associations` | Mở UDP/123, kiểm tra server |
| Giờ lệch đúng 7 tiếng | Thiếu `clock timezone` | `show clock detail` | `clock timezone ICT 7` |
| Log không có ngày giờ, chỉ có uptime | Thiếu `service timestamps` | `show run \| include timestamps` | Thêm lệnh đó |
| Syslog server không nhận được gì | UDP/514 bị chặn, hoặc sai IP | `show logging` — dòng `Logging to` | Kiểm tra ACL, firewall |
| Console spam log khi đang gõ | `logging console` mức quá cao | `show logging` | `logging console notifications` + `logging synchronous` |
| NMS không poll được | Community/ACL sai | `show snmp`, `debug snmp packet` | Sửa community, mở ACL |
| Nhận cảnh báo SNMP giả | Dùng v2c, community bị lộ | — | Chuyển **v3** |
| Thoại rè, méo tiếng | **Jitter** cao | `show policy-map interface` | Cấu hình LLQ cho DSCP EF |
| Cấu hình QoS rồi vẫn nghẽn | QoS **không tạo ra băng thông** | `show interface` xem utilization | Nâng băng thông, hoặc shape đúng tốc độ ISP |
| PC tự đánh dấu EF chiếm ưu tiên | Sai **trust boundary** | `show mls qos interface` | Không trust port người dùng |

---

## 11. LAB

🧪 **LAB 33 — Management plane: NTP, Syslog, SNMP** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md))*

Yêu cầu tối thiểu:

- Router làm NTP master, 2 switch đồng bộ từ nó → `show ntp status` thấy `synchronized`
- Đặt `clock timezone` và `service timestamps` → log hiển thị đúng giờ Việt Nam
- Syslog server trong Packet Tracer nhận được log; `shutdown` một interface →
  quan sát dòng `%LINEPROTO-5-UPDOWN` xuất hiện trên server
- SNMP v2c với ACL giới hạn; thử poll từ IP **không** trong ACL → bị từ chối
- **BREAK bắt buộc:** (1) tắt NTP → so timestamp giữa 2 thiết bị, chứng minh không
  correlate được; (2) `logging console debugging` → quan sát console không dùng nổi;
  (3) bỏ ACL khỏi SNMP community → thử poll từ máy lạ

## 12. Challenge

1. Hai switch log cùng một sự cố nhưng timestamp lệch 3 phút. Hậu quả khi điều tra?
2. `logging trap 7` trên 50 thiết bị production. Nêu 2 hậu quả.
3. Vì sao SNMP v2c không nên dùng ra ngoài mạng quản trị? Nêu kịch bản tấn công.
4. QoS cấu hình đúng, LLQ cho thoại 20%, nhưng thoại vẫn rè. Nêu 3 nguyên nhân.

<details>
<summary>Đáp án</summary>

**1.** Bạn **không xác định được nguyên nhân và hệ quả**.

```text
SW1: 14:20:00  Interface down
SW2: 14:23:00  STP topology change
```

Lệch 3 phút → không biết STP đổi **vì** interface down, hay là hai sự kiện độc lập.
Với sự cố phức tạp qua 10 thiết bị, điều tra trở nên bất khả thi.

👉 Đây là lý do NTP phải cấu hình **trước** syslog.

**2.** Hai hậu quả:

| Hậu quả | Chi tiết |
|---|---|
| **Ngập log** | Mức 7 gồm cả output `debug`. 50 thiết bị × hàng nghìn dòng/phút → syslog server đầy đĩa trong vài giờ, và **log quan trọng bị chôn vùi** |
| **Tốn CPU + băng thông** | Sinh và gửi log tốn CPU thiết bị; trên WAN chậm có thể chiếm đáng kể băng thông |

Mức 7 chỉ bật **tạm thời** khi đang debug một thiết bị cụ thể, rồi trả lại ngay.

**3.** Vì **community string đi plaintext**.

Kịch bản tấn công:

```text
1. Kẻ tấn công bắt một gói SNMP trên đường truyền (hoặc đoán community mặc định
   "public"/"private" — bị quét tự động khắp Internet)
2. Có community RO → đọc được TOÀN BỘ cấu hình, bảng định tuyến, bảng ARP,
   danh sách interface → vẽ lại được topology mạng
3. Nếu là community RW → GHI được cấu hình: đổi route, tắt interface,
   thậm chí tải file config về
```

Phòng chống: dùng **v3** (auth + encrypt), hoặc nếu buộc dùng v2c thì
**đổi community + ACL chỉ cho NMS + chỉ RO + chỉ trong VLAN quản trị**.

**4.** Ba nguyên nhân:

| # | Nguyên nhân | Kiểm chứng |
|:---:|---|---|
| 1 | **Gói chưa được đánh dấu EF** — class-map không khớp gì | `show policy-map interface` xem counter của class VOICE |
| 2 | **Trust boundary sai** — switch không tin nhãn của IP phone, nhãn bị xoá về 0 | `show mls qos interface <int>` |
| 3 | **Nghẽn ở chỗ khác** — QoS chỉ áp trên WAN, nhưng nghẽn xảy ra ở uplink LAN, hoặc ở phía ISP *(QoS của bạn không điều khiển được chiều ISP → bạn)* | `show interface` utilization trên từng chặng |

Nguyên nhân thứ 3 là chỗ hay bị bỏ sót: **QoS chỉ kiểm soát được chiều ĐI RA của bạn**.
Chiều từ ISP về phải nhờ ISP cấu hình.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Port NTP/Syslog/SNMP · 8 severity · DSCP EF · stratum | ⬜ |
| **L2** Explain | Giải thích vì sao NTP là nền móng của syslog và SNMP | ⬜ |
| **L3** Configure | NTP + timezone + timestamps + syslog + SNMP v2c có ACL | ⬜ |
| **L4** Troubleshoot | `unsynchronized` → tìm nguyên nhân | ⬜ |
| **L5** Design | Viết "config quản trị chuẩn" cho mọi thiết bị của công ty | ⬜ |

## 14. Summary

**NTP**

- UDP **123**; stratum 0 (nguồn chuẩn) → 16 (không đồng bộ)
- ⭐ **Cấu hình NTP trước mọi thứ khác** — syslog, chứng chỉ, AD đều phụ thuộc
- `clock timezone ICT 7` + `service timestamps log datetime msec`

**Syslog**

- UDP **514**; 8 severity **0–7**, cấu hình mức N = gửi **0 → N**
- Nhớ: **E**mergency Alert Critical Error Warning Notification Informational Debugging
- Console mức 5, buffer 6, server 5–6. ⚠️ Mức 7 chỉ tạm thời

**SNMP**

- Polling **UDP 161** · Trap **UDP 162** · Inform = trap có xác nhận
- ⚠️ **v2c community plaintext** → luôn kèm **ACL**; nên dùng **v3**

**QoS**

- ⭐ QoS **không tạo ra băng thông** — chỉ quyết định ai bị hy sinh
- 3 vấn đề: **delay · jitter · loss**. VoIP: < 150ms, < 30ms jitter, < 1% loss
- **DiffServ** là chuẩn thực tế; **DSCP EF (46)** cho thoại
- ⭐ **Policing drop · Shaping đệm**
- **Đánh dấu càng gần nguồn càng tốt**; **trust boundary** để PC không tự nâng ưu tiên

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `ntp server <ip> prefer` + `clock timezone ICT 7` | ⭐ Luôn cấu hình đầu tiên |
| `service timestamps log datetime msec localtime` | Log có giờ thật |
| `logging host <ip>` + `logging trap notifications` | Syslog tập trung |
| `snmp-server community X RO <acl>` | ⚠️ Luôn kèm ACL |
| `show ntp status` / `show ntp associations` | Đã đồng bộ chưa |
| `show logging` | Mức log, server nào, log gần nhất |
| `show policy-map interface <int>` | QoS có khớp gì không |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Không cấu hình NTP | Log vô nghĩa, chứng chỉ lỗi, AD hỏng |
| Quên `clock timezone` | Log lệch 7 tiếng |
| Quên `service timestamps` | Log chỉ có uptime |
| `logging trap 7` trên production | Ngập log, chôn vùi thông tin quan trọng |
| SNMP v2c không ACL, community mặc định | Lộ toàn bộ cấu hình mạng |
| Nghĩ QoS giải quyết được thiếu băng thông | Nó chỉ chọn ai bị hy sinh |
| Trust nhãn QoS từ port người dùng | Ai cũng tự nâng mình lên EF |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 33 với đủ 3 lỗi BREAK.
2. Bổ sung khối **NTP + Syslog + SNMP** vào "config chuẩn" bạn viết ở Lesson 12.
3. Trên thiết bị công ty (nếu có quyền): `show ntp status`, `show logging` —
   NTP đã đồng bộ chưa? Log có gửi về server tập trung không?
4. Học thuộc 8 severity level.

```markdown
- [YYYY-MM-DD] Lesson 28 — NTP/Syslog/SNMP/QoS: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 3

Làm **[Mini Exam Phase 3](./review-phase03.md)** trước khi sang
[Phase 4 — IPv6](../04-ipv6/README.md).

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Port, 8 severity, SNMP version, DSCP EF, policing vs shaping |
| 🔧 **Engineer** | NTP trước tiên; `logging source-interface`; SNMP v3; trust boundary |
| 🏭 **Production** | Log sai giờ = không điều tra được; v2c community là lỗ hổng bị quét hàng ngày; QoS không điều khiển được chiều ISP→bạn |

### 🔗 Liên kết

- ⬅️ [Lesson 27 — NAT nâng cao](./lesson-27-nat-nang-cao.md)
- 📝 [Mini Exam Phase 3](./review-phase03.md)
- ➡️ [Phase 4 — IPv6](../04-ipv6/README.md)
- 🔜 QoS sâu: [`CCNP-Encor` Module 09](https://github.com/hiepnguyen775/CCNP-Encor)
