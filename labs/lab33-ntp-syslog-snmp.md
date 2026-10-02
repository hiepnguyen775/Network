# LAB 33 — Management plane: NTP, Syslog, SNMP

| | |
|---|---|
| **Phase** | 3 |
| **Lesson liên quan** | [Lesson 28 — NTP · Syslog · SNMP · QoS](../03-services/lesson-28-ntp-syslog-snmp-qos.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Đồng bộ thời gian toàn mạng bằng **NTP** *(và hiểu vì sao nó sống còn)*
- [ ] Gửi log tập trung về **Syslog server**, đọc severity level
- [ ] Cấu hình **SNMP** read-only và kéo thông tin từ NMS
- [ ] Hiểu vì sao sai giờ làm **mọi log vô dụng**
- [ ] Tự gây & sửa 3 lỗi management plane

## 2. Prerequisite

- [Lesson 28](../03-services/lesson-28-ntp-syslog-snmp-qos.md) — NTP, Syslog, SNMP
- [LAB 10](lab10-cisco-ios-cli.md) — CLI, line config

---

## 3. Topology

```text
   R1 ─── SW1 ─── R2
    │      │
   NTP   SYSLOG + SNMP(NMS)
  server  10.0.0.100
 10.0.0.1
```

| Thiết bị | Vai trò |
|---|---|
| R1 | NTP server *(master)* + thiết bị được quản lý |
| R2, SW1 | NTP client, gửi syslog, chạy SNMP agent |
| MGMT | Server-PT: Syslog + SNMP NMS `10.0.0.100` |

## 4. IP Addressing Table

| Device | IP |
|---|---|
| R1 | `10.0.0.1/24` |
| R2 | `10.0.0.2/24` |
| SW1 | `10.0.0.3/24` |
| MGMT *(Syslog+SNMP)* | `10.0.0.100/24` |

---

## 5. Yêu cầu LAB

- [ ] R2 và SW1 đồng bộ giờ với R1 *(stratum hợp lý)*
- [ ] Log của R2 xuất hiện trên Syslog server với **timestamp đúng**
- [ ] NMS đọc được sysName, interface của R2 qua SNMP
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — NTP

```cisco
! ══ R1 làm NTP master ══
R1(config)# ntp master 3                  ! stratum 3
R1(config)# clock timezone ICT 7          ! giờ VN (UTC+7)

! ══ R2 & SW1 làm client ══
R2(config)# ntp server 10.0.0.1
R2(config)# clock timezone ICT 7
R2(config)# service timestamps log datetime msec localtime    ! log có giờ
R2(config)# service timestamps debug datetime msec localtime
```

> 🔑 `service timestamps log datetime` cực kỳ quan trọng: không có nó, log chỉ có
> **uptime** *(vd `*00:14:22`)* thay vì ngày giờ thật → không đối chiếu được giữa
> các thiết bị.

Đợi vài phút cho đồng bộ, rồi:

```cisco
R2# show ntp associations
R2# show ntp status
R2# show clock
```

### Bước 2 — Syslog tập trung

```cisco
R2(config)# logging host 10.0.0.100          ! gửi log về server
R2(config)# logging trap informational       ! mức 6 trở lên
R2(config)# logging source-interface Gi0/0
```

> 🔴 **DỰ ĐOÁN:** bạn gõ `shutdown` rồi `no shutdown` một interface trên R2.
> Log gì xuất hiện trên Syslog server? Severity mấy?

Tạo sự kiện:

```cisco
R2(config)# interface Gi0/0
R2(config-if)# shutdown
R2(config-if)# no shutdown
```

**8 mức severity** *(nhớ: "Every Awesome Cisco Engineer Will Need Icecream Daily")*:

| # | Mức | Ví dụ |
|:---:|---|---|
| 0 | Emergency | hệ thống sập |
| 1 | Alert | cần hành động ngay |
| 2 | Critical | lỗi nghiêm trọng |
| 3 | Error | interface lỗi |
| 4 | Warning | cấu hình đáng ngờ |
| 5 | Notification | **link up/down** |
| 6 | Informational | sự kiện bình thường |
| 7 | Debugging | debug output |

### Bước 3 — SNMP read-only

```cisco
R2(config)# snmp-server community CTYro RO           ! community read-only
R2(config)# snmp-server location "DC-HN-Rack12"
R2(config)# snmp-server contact "noc@cty.local"
R2(config)# snmp-server host 10.0.0.100 version 2c CTYro
R2(config)# snmp-server enable traps
```

> ⚠️ `RO` = chỉ đọc. **Không** dùng `RW` *(read-write)* trừ khi thật cần — RW cho
> phép sửa cấu hình qua SNMP, rất nguy hiểm nếu community bị lộ. Và SNMPv2c gửi
> community **không mã hoá** → production nên dùng **SNMPv3**.

Trên NMS *(Server-PT → SNMP, hoặc PC với MIB browser)*: query sysName, ifTable.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R2# show ntp status
Clock is synchronized, stratum 4, reference is 10.0.0.1
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz
```

```text
# output điển hình — tự verify trên lab của bạn
R2# show ntp associations
  address         ref clock       st   when   poll reach  delay
*~10.0.0.1        127.127.1.1      3     24     64   377   1.00
 * sys.peer (đồng bộ), ~ configured
```

```text
# output điển hình — log link up/down trên Syslog server (severity 5)
Oct 02 2026 14:32:07.123 ICT: %LINK-3-UPDOWN: Interface GigabitEthernet0/0,
   changed state to down
Oct 02 2026 14:32:10.456 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface
   GigabitEthernet0/0, changed state to up
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | `show ntp status` R2 | "Clock is synchronized" | |
| 2 | `show clock` R1, R2, SW1 khớp nhau | ✅ | |
| 3 | R2 stratum = R1 stratum + 1 | ✅ *(4 = 3+1)* | |
| 4 | Log link up/down về Syslog, có timestamp thật | ✅ | |
| 5 | NMS đọc được sysName của R2 | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Sai giờ làm log vô dụng ⭐

```cisco
! Bỏ NTP, đặt giờ sai lệch trên R2
R2(config)# no ntp server 10.0.0.1
R2# clock set 03:00:00 1 Jan 2020
! Tạo một sự kiện link down
```

| | |
|---|---|
| Timestamp của log R2 trên Syslog là gì? | |
| Khi đối chiếu với log R1 *(giờ đúng)*, có ghép được timeline không? | |
| Vì sao điều tra sự cố bảo mật cần giờ đồng bộ? | |
| Một thiết bị lệch giờ ảnh hưởng điều tra thế nào? | |

### Lỗi 2 — logging trap level quá thấp/cao

```cisco
R2(config)# logging trap emergencies      ! chỉ mức 0
```

| | |
|---|---|
| Log link up/down *(mức 5)* có còn gửi về server không? | |
| Vì sao? | |
| Nếu đặt `logging trap debugging` *(mức 7)* thì sao — tốt hay hại? | |
| Mức nào hợp lý cho production? | |

### Lỗi 3 — SNMP community sai / dùng RW

```cisco
R2(config)# snmp-server community CTYrw RW     ! read-write, nguy hiểm
! NMS query bằng community SAI "public"
```

| | |
|---|---|
| NMS dùng community `public` có đọc được không? | |
| Vì sao community phải khớp? | |
| Rủi ro của `RW` community bị lộ là gì? | |
| SNMPv2c gửi community dạng gì trên dây? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Giải thích `stratum` trong NTP. Vì sao stratum càng cao càng "xa nguồn chuẩn"?
2. `logging buffered`, `logging console`, `logging host` — ba cái khác nhau thế nào?
3. Vì sao SNMPv3 an toàn hơn v2c? Nêu 3 cải tiến.
4. Một router "log ngập console không gõ lệnh được". Nguyên nhân và cách sửa.

<details>
<summary>Đáp án</summary>

**1.** **Stratum** = số bậc cách nguồn thời gian chuẩn *(đồng hồ nguyên tử/GPS)*.
- Stratum 0 = nguồn chuẩn *(GPS, atomic)*.
- Stratum 1 = server nối trực tiếp stratum 0.
- Mỗi bậc đồng bộ thêm +1. Stratum càng cao → càng xa nguồn → **độ chính xác giảm dần**
  *(tích luỹ sai số qua mỗi bậc)*. Thiết bị chọn đồng bộ với **stratum thấp nhất** sẵn có.

**2.**

| Lệnh | Log đi đâu | Bền? |
|---|---|---|
| `logging buffered` | **RAM** của thiết bị *(xem bằng `show logging`)* | Mất khi reload |
| `logging console` | Ra **màn hình console** | Không lưu |
| `logging host` | Gửi về **Syslog server** *(UDP 514)* | ✅ Lưu tập trung, bền |

Production: **logging host** là quan trọng nhất *(tập trung, giữ lâu)*; `logging console`
nên **tắt** hoặc hạ mức *(xem Challenge 4)*.

**3.** SNMPv3 cải tiến so với v2c:

| | v2c | v3 |
|---|---|---|
| Xác thực | community *(mật khẩu rõ)* | username + **auth** *(MD5/SHA)* |
| Mã hoá | **không** | **có** *(DES/AES — privacy)* |
| Toàn vẹn | không đảm bảo | có *(chống sửa gói)* |

→ v3 có **authentication + encryption + integrity**; v2c gửi community **plaintext** →
ai bắt gói là thấy. Production bắt buộc v3.

**4.** Nguyên nhân: `logging console` ở mức cao *(debug/informational)* + đang có nhiều
sự kiện → log **tràn ra console** chen vào lệnh đang gõ.

Sửa:
```cisco
R2(config)# no logging console          ! tắt hẳn log ra console
! hoặc hạ mức:
R2(config)# logging console warnings    ! chỉ mức 4 trở lên
! và bật để lệnh không bị log cắt ngang:
R2(config)# line console 0
R2(config-line)# logging synchronous
```

`logging synchronous` tự in lại dòng lệnh đang gõ sau mỗi log → không bị "nuốt chữ".

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — sai giờ ⭐:** Log R2 mang timestamp **2020** trong khi R1 là **2026**.
Khi gom log về một Syslog server để điều tra, **không thể dựng timeline**: sự kiện trên
R2 và R1 không xếp đúng thứ tự thời gian. Với điều tra bảo mật *(ai tấn công, lúc nào,
lan thế nào)*, một thiết bị lệch giờ **phá hỏng toàn bộ chuỗi sự kiện** — đây là lý do
NTP là nền tảng của mọi hệ thống log/SIEM.

**Lỗi 2 — trap level:** `logging trap emergencies` *(0)* → chỉ gửi log mức 0.
Link up/down là mức **5** > 0 → **không gửi** → server mất sự kiện quan trọng.
Ngược lại `debugging` *(7)* gửi **mọi thứ** kể cả debug → **ngập** server, khó lọc,
tốn băng thông. Production thường dùng **`informational` (6)** hoặc **`notifications` (5)**
— đủ chi tiết mà không ngập.

> 🔑 `logging trap X` nghĩa là "gửi mức X **và thấp hơn về số**" *(nghiêm trọng hơn)*.
> Mức 6 = gửi 0–6, bỏ 7.

**Lỗi 3 — SNMP community:** Community như **mật khẩu** — NMS phải gửi đúng chuỗi mới
được trả lời. `public` ≠ `CTYro` → bị từ chối im lặng. `RW` bị lộ = kẻ xấu **sửa được
cấu hình** qua SNMP *(đổi route, tắt interface, thậm chí tải config)*. v2c gửi community
**plaintext** trên UDP → bắt gói là đọc được → bắt buộc v3 ở môi trường thật.

### Bảng tổng kết

| Dịch vụ | Vai trò | Lệnh verify | Bẫy |
|---|---|---|---|
| NTP | Đồng bộ giờ | `show ntp status/associations` | sai giờ = log vô dụng |
| Syslog | Log tập trung | `show logging` | trap level sai = mất log |
| SNMP | Giám sát | NMS query | RW/v2c = rủi ro bảo mật |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Vì sao NTP là nền tảng cho mọi log? ___
- Lỗi 2 (trap level) — "gửi mức X và thấp hơn" tôi hiểu đúng chưa? ___
- SNMPv3 hơn v2c ở 3 điểm nào? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
