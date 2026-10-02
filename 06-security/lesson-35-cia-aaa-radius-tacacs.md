# LESSON 35 — CIA Triad · AAA · RADIUS vs TACACS+

| | |
|---|---|
| **Phase** | 6 — Security |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md), [Lesson 34](../05-wireless/lesson-34-bao-mat-wifi.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Giải thích **CIA Triad** và ví dụ tấn công vào từng trụ cột
- [ ] Phân biệt **Authentication · Authorization · Accounting** bằng ví dụ, không bằng định nghĩa
- [ ] So sánh **RADIUS** và **TACACS+** — và biết dùng cái nào khi nào
- [ ] Cấu hình AAA trên thiết bị Cisco, **có phương án dự phòng**
- [ ] Hiểu privilege level và role-based access

## 2. Prerequisite

- Cấu hình SSH, `username ... privilege 15` *(Lesson 12)*
- 802.1X và vai trò RADIUS *(Lesson 34)*

---

## 3. Concept

### CIA Triad — ba trụ cột của bảo mật

| Trụ cột | Nghĩa | Tấn công điển hình | Bảo vệ bằng |
|---|---|---|---|
| **C** — Confidentiality | Chỉ người được phép đọc được | Nghe lén, đánh cắp dữ liệu | **Mã hoá**, ACL, phân quyền |
| **I** — Integrity | Dữ liệu không bị sửa đổi | Man-in-the-middle, sửa gói | **Hash**, chữ ký số, checksum |
| **A** — Availability | Hệ thống luôn sẵn sàng | **DoS/DDoS**, phá hạ tầng | Dự phòng, HA, rate-limit |

> 🔑 Ba trụ cột này **đánh đổi lẫn nhau**. Mã hoá mạnh (C) làm chậm hệ thống (A).
> Xác thực nhiều lớp (C) làm giảm trải nghiệm. Thiết kế bảo mật là **chọn điểm cân bằng**,
> không phải tối đa hoá một trụ cột.

> 🏭 Người làm network hay quên **A (Availability)**. Nhưng với mạng doanh nghiệp,
> *"mạng sập"* gây thiệt hại ngay lập tức và rõ ràng hơn *"dữ liệu bị đọc trộm"*.

### AAA — ba chữ A

| | Câu hỏi nó trả lời | Ví dụ |
|---|---|---|
| **Authentication** | **"Anh là ai?"** | Đăng nhập bằng username/password |
| **Authorization** | **"Anh được làm gì?"** | Được chạy `show` nhưng không được `configure terminal` |
| **Accounting** | **"Anh đã làm gì?"** | Log: lúc 14:23 user `nva` gõ lệnh `shutdown` trên `Gi0/1` |

> 💡 Cách nhớ bằng ví dụ đời thường: vào toà nhà văn phòng.
> **Authentication** = quẹt thẻ ở cổng. **Authorization** = thẻ của bạn mở được
> tầng 3 nhưng không mở được phòng server. **Accounting** = hệ thống ghi lại
> bạn vào lúc mấy giờ, qua cửa nào.

> ⭐ Rất nhiều người chỉ nghĩ tới chữ A đầu. Nhưng **Accounting** mới là thứ
> cứu bạn khi có sự cố: *"Ai đã tắt interface đó lúc 2 giờ sáng?"*

### RADIUS vs TACACS+ — bảng phải thuộc

| | **RADIUS** | **TACACS+** |
|---|---|---|
| Chuẩn | **Mở** (RFC 2865) | **Cisco** độc quyền |
| Giao thức | **UDP** 1812/1813 | **TCP 49** |
| Mã hoá | **Chỉ mã hoá password** | **Mã hoá TOÀN BỘ payload** |
| Gộp AAA | **Authentication + Authorization GỘP** | **Tách riêng cả 3** |
| Command authorization | ❌ Không làm được *(thực tế)* | ✅ **Từng lệnh một** |
| Dùng cho | **Truy cập mạng**: 802.1X, VPN, Wi-Fi | **Quản trị thiết bị**: SSH vào router/switch |
| Đa nền tảng | ✅ Mọi hãng | ⚠️ Chủ yếu Cisco |

> ⭐ **Quy tắc chọn:**
> **RADIUS cho người dùng vào mạng. TACACS+ cho kỹ sư vào thiết bị.**
>
> Lý do: TACACS+ **tách Authorization riêng** nên kiểm soát được **từng lệnh** —
> cho phép junior chạy `show` nhưng không cho `reload`. RADIUS gộp Auth+Authz
> nên không làm được việc này.

> 🔑 Khác biệt **TCP vs UDP** cũng quan trọng: TACACS+ dùng **TCP** → biết chắc gói đã tới,
> phù hợp với quản trị. RADIUS dùng **UDP** → nhanh, nhẹ, chịu được khối lượng lớn
> khi hàng nghìn người đăng nhập Wi-Fi.

### Privilege Level

| Level | Mặc định cho phép |
|:---:|---|
| **0** | 5 lệnh: `disable`, `enable`, `exit`, `help`, `logout` |
| **1** | **User EXEC** — các lệnh `show` cơ bản, `ping` |
| **2–14** | Tuỳ chỉnh — bạn tự gán lệnh |
| **15** | **Privileged EXEC** — toàn quyền |

```cisco
! Tạo level 5 chỉ cho xem và ping
R1(config)# privilege exec level 5 show running-config
R1(config)# privilege exec level 5 show ip route
R1(config)# privilege exec level 5 ping
R1(config)# username helpdesk privilege 5 secret <pass>
R1(config)# enable secret level 5 <pass-level-5>
```

> ⚠️ Privilege level có **hạn chế lớn**: nó phân cấp theo bậc thang, không theo vai trò.
> Level 10 tự động có mọi quyền của level 1–9. Không làm được *"cho A quyền X,
> cho B quyền Y, hai bên không liên quan"*.
>
> Giải pháp tốt hơn: **TACACS+ command authorization** hoặc **RBAC** *(trên IOS-XE/NX-OS)*.

---

## 4. Why?

> **Vì sao không dùng tài khoản local trên từng thiết bị?**

| Vấn đề | Chi tiết |
|---|---|
| **Không scale** | 50 thiết bị × 10 kỹ sư = 500 tài khoản phải quản |
| **Nghỉ việc = phải xoá 50 lần** | Sót một thiết bị là còn đường vào |
| **Đổi mật khẩu = sửa 50 lần** | Thực tế: không ai đổi |
| **Không có accounting tập trung** | Log nằm rải rác, không correlate được |
| **Không phân quyền linh hoạt** | Chỉ có privilege level thô sơ |

> ⭐ Nhưng **phải luôn giữ một tài khoản local dự phòng**:

```cisco
! Nếu AAA server chết, vẫn vào được bằng tài khoản local
R1(config)# aaa authentication login default group tacacs+ local
!                                                   ↑        ↑
!                                            thử TACACS+ trước, fallback local
```

> ⚠️ **Đây là dòng quan trọng nhất của lesson.** Cấu hình AAA mà quên `local` ở cuối:
> TACACS+ server chết → **không ai vào được thiết bị nào** → phải chạy tới chỗ cắm console.
> Đã có những sự cố lớn vì đúng lỗi này.

---

## 5. How does it work? — luồng xác thực

```text
Kỹ sư SSH vào R1

1. R1 nhận yêu cầu đăng nhập
2. R1 hỏi TACACS+ server (TCP 49): "user nva, password XXX — đúng không?"
   ├─ Server UP   → trả Accept/Reject
   └─ Server DOWN → R1 fallback sang tài khoản LOCAL   ← nhờ từ khoá "local"
3. Đăng nhập thành công → AUTHORIZATION:
   R1 hỏi: "user nva được chạy privilege level mấy?"
   → server trả: level 15 (hoặc 1, hoặc 5...)
4. Mỗi lệnh gõ (nếu bật command authorization):
   R1 hỏi: "nva được chạy lệnh 'reload' không?"
   → server trả: Permit / Deny
5. ACCOUNTING: mọi lệnh được gửi về server để lưu log
```

> 🔑 Bước 4 chỉ **TACACS+ làm được**. Đây là lý do nó tồn tại dù RADIUS phổ biến hơn.

---

## 6. Packet Flow — vì sao TACACS+ an toàn hơn

```text
RADIUS Access-Request:
┌────────────────────────────────────────┐
│ Username: nva          ← PLAINTEXT ⚠️  │
│ NAS-IP: 10.0.1.1       ← PLAINTEXT     │
│ Password: [đã mã hoá]  ← chỉ cái này   │
│ Service-Type: ...      ← PLAINTEXT     │
└────────────────────────────────────────┘

TACACS+ packet:
┌────────────────────────────────────────┐
│ ████████████████████████████████████   │
│ ████ TOÀN BỘ ĐÃ MÃ HOÁ ████████████   │
│ ████████████████████████████████████   │
└────────────────────────────────────────┘
```

> ⚠️ Với RADIUS, kẻ bắt được gói đọc được **username, IP thiết bị, loại dịch vụ** —
> đủ để vẽ bản đồ ai quản trị thiết bị nào. Chỉ password được bảo vệ.

---

## 7. Real-world Example

🏭 **Thiết kế AAA cho doanh nghiệp**

```text
┌──────────── ISE / ACS ────────────┐
│  TACACS+  →  kỹ sư SSH vào thiết bị │
│  RADIUS   →  802.1X Wi-Fi/dây, VPN  │
└─────────────────┬──────────────────┘
                  │
    ┌─────────────┴─────────────┐
 Switch/Router             AP/WLC/VPN
 (TACACS+)                  (RADIUS)
```

| Nhóm người dùng | Giao thức | Quyền |
|---|---|---|
| Network Engineer | TACACS+ | Privilege 15, full |
| Helpdesk | TACACS+ | Chỉ `show`, `ping`, `clear counters` |
| Nhân viên | RADIUS | 802.1X Wi-Fi + dây, dynamic VLAN |
| Nhà thầu | RADIUS | VLAN hạn chế, hết hạn theo ngày |

🏭 **Sự cố kinh điển: mất quyền vào toàn bộ thiết bị**

```text
1. Kỹ sư cấu hình AAA, gõ:
      aaa authentication login default group tacacs+
   (QUÊN từ khoá "local" ở cuối)
2. Đẩy cấu hình xuống 40 switch
3. Vài tháng sau, TACACS+ server gặp sự cố
4. → KHÔNG AI vào được 40 switch
5. → Phải cắm console từng con một
```

**Cấu hình đúng:**

```cisco
aaa authentication login default group tacacs+ local
aaa authentication enable default group tacacs+ enable
username admin-local privilege 15 secret <strong-pass>
```

> 🔧 Thêm một lớp an toàn nữa: luôn chừa một **line console** không qua AAA,
> hoặc bật `aaa authentication login CONSOLE local` rồi áp cho `line console 0`.

🏭 **Accounting — bằng chứng khi có sự cố**

```text
# output điển hình — log TACACS+ trên server
Oct 02 2026 14:23:51  nguyen.van.a  10.0.99.11  cmd=interface Gi0/1
Oct 02 2026 14:23:55  nguyen.van.a  10.0.99.11  cmd=shutdown
Oct 02 2026 14:24:10  nguyen.van.a  10.0.99.11  cmd=no shutdown
```

> 🔑 Không có accounting, câu hỏi *"ai làm sập mạng lúc 14:23?"* **không có câu trả lời**.
> Đây là lý do accounting quan trọng không kém authentication.

---

## 8. Cisco CLI

```cisco
! ═══════ BẬT AAA ═══════
R1(config)# aaa new-model          ! ⚠️ Đổi hành vi đăng nhập NGAY LẬP TỨC

! ═══════ TẠO TÀI KHOẢN LOCAL DỰ PHÒNG — LÀM TRƯỚC TIÊN ═══════
R1(config)# username admin-local privilege 15 secret <strong-pass>

! ═══════ TACACS+ SERVER ═══════
R1(config)# tacacs server ISE-01
R1(config-server-tacacs)# address ipv4 10.0.50.60
R1(config-server-tacacs)# key <shared-secret>
R1(config-server-tacacs)# exit
R1(config)# aaa group server tacacs+ TAC-GROUP
R1(config-sg-tacacs+)# server name ISE-01
R1(config-sg-tacacs+)# exit

! ═══════ RADIUS SERVER ═══════
R1(config)# radius server ISE-RAD
R1(config-radius-server)# address ipv4 10.0.50.60 auth-port 1812 acct-port 1813
R1(config-radius-server)# key <shared-secret>

! ═══════ AUTHENTICATION ═══════
R1(config)# aaa authentication login default group TAC-GROUP local
R1(config)# aaa authentication enable default group TAC-GROUP enable
R1(config)# aaa authentication dot1x default group radius

! Line console dùng riêng (an toàn khi AAA hỏng)
R1(config)# aaa authentication login CONSOLE local
R1(config)# line console 0
R1(config-line)# login authentication CONSOLE

! ═══════ AUTHORIZATION ═══════
R1(config)# aaa authorization exec default group TAC-GROUP local
R1(config)# aaa authorization commands 15 default group TAC-GROUP local
R1(config)# aaa authorization config-commands

! ═══════ ACCOUNTING ═══════
R1(config)# aaa accounting exec default start-stop group TAC-GROUP
R1(config)# aaa accounting commands 15 default start-stop group TAC-GROUP

! ═══════ PRIVILEGE LEVEL TUỲ CHỈNH ═══════
R1(config)# privilege exec level 5 show
R1(config)# privilege exec level 5 ping
R1(config)# privilege exec level 5 traceroute
R1(config)# username helpdesk privilege 5 secret <pass>

! ═══════ KIỂM TRA ═══════
R1# show aaa servers
R1# show tacacs
R1# test aaa group TAC-GROUP <user> <pass> legacy
R1# show privilege
R1# show users
R1# debug aaa authentication
R1# undebug all
```

| Lệnh | Lưu ý |
|---|---|
| `aaa new-model` | ⚠️ **Đổi hành vi đăng nhập ngay** — tạo user local **trước** khi gõ |
| `... group TAC-GROUP local` | ⭐ **Từ khoá `local` ở cuối là dây an toàn** |
| `aaa authorization commands 15` | Kiểm soát **từng lệnh** — chỉ TACACS+ làm được |
| `aaa accounting commands 15` | Ghi log mọi lệnh privilege 15 |
| `test aaa group ... legacy` | ⭐ **Test trước khi áp dụng** — không cần đăng xuất |
| `login authentication CONSOLE` | Console dùng method riêng → cứu khi AAA hỏng |

> ⚠️ **Quy trình an toàn khi triển khai AAA:**
> 1. Tạo user local privilege 15
> 2. Cấu hình AAA **có `local` ở cuối**
> 3. Chạy `test aaa group ...` để xác nhận server trả lời
> 4. **Mở một phiên SSH thứ hai** và thử đăng nhập — **đừng đóng phiên đang mở**
> 5. Chỉ khi phiên mới vào được mới `wr`

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show aaa servers
TACACS+: id 1, priority 1, host 10.0.50.60, auth-port 49
     State: current UP, duration 84233s, previous duration 0s
     Authen: request 142, timeouts 0, failover 0, retransmission 0
             Response: accept 138, reject 4, error 0
     Author: request 138, timeouts 0
     Account: request 1203, timeouts 0
```

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `State: current UP` | Server sống ✅ | **DOWN** → kiểm tra route, TCP 49, shared secret |
| `timeouts` | Số lần không phản hồi | Tăng → mạng tới server không ổn định |
| `reject` | Số lần từ chối | Tăng bất thường → có người thử sai mật khẩu |
| `failover` | Số lần chuyển sang server dự phòng | > 0 → server chính có vấn đề |

```text
# output điển hình — tự verify trên lab của bạn
R1# test aaa group TAC-GROUP nguyen.van.a MyP@ss legacy
Attempting authentication test to server-group TAC-GROUP using tacacs+
User was successfully authenticated.
```

> 🔧 `test aaa` là cách **duy nhất an toàn** để kiểm tra AAA trước khi áp dụng.
> Không cần đăng xuất, không rủi ro mất quyền.

```text
# output điển hình — tự verify trên lab của bạn
R1# show users
    Line       User       Host(s)              Idle       Location
*  2 vty 0     nguyen.van.a idle               00:00:00   10.0.30.45
   3 vty 1     helpdesk   idle                 00:12:33   10.0.30.78

R1# show privilege
Current privilege level is 15
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| **Không đăng nhập được vào thiết bị nào** | AAA server chết + **thiếu `local`** | Console vào xem `show run \| include aaa auth` | Thêm `local` ở cuối; tạm thời console |
| `show aaa servers` → DOWN | Không tới được, hoặc sai shared secret | `ping <server>`, `telnet <server> 49` | Mở TCP 49, kiểm tra key |
| Đăng nhập được nhưng vào thẳng level 1 | Thiếu `aaa authorization exec` | `show privilege` | Thêm authorization |
| Gõ lệnh bị từ chối dù privilege 15 | `aaa authorization commands` chặn | Log TACACS+ | Sửa policy trên server |
| Accounting không có log | Thiếu `aaa accounting` | `show run \| include accounting` | Thêm lệnh |
| Một số lệnh config không chạy được | Thiếu `aaa authorization config-commands` | — | Thêm lệnh đó |
| 802.1X fail nhưng SSH OK | Dùng nhầm TACACS+ cho dot1x | `show run \| include dot1x` | 802.1X phải dùng **RADIUS** |
| Sau `aaa new-model` mất quyền ngay | Chưa tạo user local | Console | **Luôn tạo user local trước** |

---

## 11. LAB

🧪 **LAB 60 — AAA với TACACS+ và RADIUS** → [`../labs/lab60-aaa-tacacs-radius.md`](../labs/lab60-aaa-tacacs-radius.md)

Yêu cầu tối thiểu:

- Tạo user local privilege 15 **trước**, rồi mới `aaa new-model`
- Cấu hình AAA authentication **có `local` fallback**
- Tạo user `helpdesk` privilege 5 chỉ chạy được `show`/`ping` → verify bị từ chối khi
  gõ `configure terminal`
- Bật accounting, gõ vài lệnh, kiểm tra log trên server
- **BREAK bắt buộc:** (1) cấu hình AAA **không có `local`** rồi tắt server →
  chứng minh mất quyền vào thiết bị *(và khôi phục bằng console)*;
  (2) sai shared secret → `show aaa servers` DOWN;
  (3) `aaa new-model` khi chưa có user local → quan sát hậu quả

> ⚠️ Làm lỗi BREAK 1 và 3 **chỉ trong lab**. Trên thiết bị thật, luôn giữ một
> phiên SSH đang mở khi thử nghiệm AAA.

## 12. Challenge

1. Giải thích AAA bằng ví dụ **toà nhà văn phòng** cho người không làm IT.
2. Công ty cần: kỹ sư SSH vào switch, và nhân viên xác thực 802.1X vào Wi-Fi.
   Dùng giao thức nào cho việc nào? Vì sao?
3. Bạn muốn helpdesk được chạy `show` và `clear counters` nhưng **không** được
   `reload` hay `configure terminal`. Nêu 2 cách và đánh giá từng cách.
4. Một kỹ sư gõ `aaa authentication login default group tacacs+` rồi `wr`.
   Ba tháng sau server chết. Chuyện gì xảy ra và làm sao khôi phục?

<details>
<summary>Đáp án</summary>

**1.**

| Chữ A | Ở toà nhà | Trên thiết bị mạng |
|---|---|---|
| **Authentication** | Quẹt thẻ ở cổng — *"anh là ai?"* | Nhập username/password SSH |
| **Authorization** | Thẻ mở được tầng 3, không mở được phòng server — *"anh được vào đâu?"* | Được chạy `show` nhưng không được `reload` |
| **Accounting** | Hệ thống ghi: 14:23 anh A vào cửa B — *"anh đã làm gì?"* | Log: 14:23 user `nva` gõ `shutdown` trên `Gi0/1` |

**2.**

| Việc | Giao thức | Vì sao |
|---|---|---|
| Kỹ sư SSH vào switch | **TACACS+** | Tách Authorization riêng → kiểm soát **từng lệnh**; mã hoá **toàn bộ** payload; TCP đáng tin |
| Nhân viên 802.1X Wi-Fi | **RADIUS** | Chuẩn mở, mọi hãng AP/WLC hỗ trợ; UDP nhẹ, chịu được hàng nghìn phiên; gộp Auth+Authz là đủ cho việc này |

**3.** Hai cách:

| Cách | Cấu hình | Đánh giá |
|---|---|---|
| **Privilege level** | `privilege exec level 5 show` + `username helpdesk privilege 5` | ✅ Đơn giản, không cần server<br>❌ Phân cấp **bậc thang** — khó làm quyền phức tạp; phải cấu hình trên **từng thiết bị** |
| **TACACS+ command authorization** ⭐ | `aaa authorization commands 15 default group TAC-GROUP local` + policy trên server | ✅ Linh hoạt, quản lý **tập trung**, đổi quyền không cần đụng thiết bị<br>❌ Cần server, phụ thuộc server |

Thực tế: doanh nghiệp có AAA server → dùng TACACS+. Mạng nhỏ → privilege level.

**4.**

```text
Chuyện gì xảy ra:
  Thiếu "local" ở cuối → khi TACACS+ chết, thiết bị KHÔNG CÓ phương án dự phòng
  → mọi nỗ lực SSH đều fail
  → nếu line console cũng dùng method default → KHÔNG VÀO ĐƯỢC BẰNG CÁCH NÀO CẢ
```

**Khôi phục:**

| Tình huống | Cách |
|---|---|
| Console dùng method riêng *(`login authentication CONSOLE local`)* | ✅ Cắm console, đăng nhập bằng user local |
| Console cũng dùng default | ❌ Phải **password recovery** *(Lesson 12)* — rút điện, vào ROMMON, bỏ qua startup-config |

**Phòng ngừa:**

```cisco
aaa authentication login default group tacacs+ local    ! ← local ở cuối
aaa authentication login CONSOLE local                  ! ← method riêng cho console
line console 0
 login authentication CONSOLE
username admin-local privilege 15 secret <strong>
```

Và luôn làm theo quy trình: `test aaa` → mở phiên SSH thứ hai kiểm tra → mới `wr`.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | CIA 3 trụ cột · 3 chữ A · port TACACS+/RADIUS · privilege level | ⬜ |
| **L2** Explain | Giải thích AAA bằng ví dụ đời thường | ⬜ |
| **L3** Configure | Cấu hình AAA đầy đủ **có fallback local** | ⬜ |
| **L4** Troubleshoot | Mất quyền vào thiết bị → khôi phục và sửa gốc | ⬜ |
| **L5** Design | Thiết kế AAA cho công ty: nhóm nào, giao thức nào, quyền gì | ⬜ |

## 14. Summary

**Key concepts**

- **CIA**: Confidentiality *(mã hoá)* · Integrity *(hash)* · Availability *(dự phòng)*
- **AAA**: Authentication *"anh là ai"* · Authorization *"được làm gì"* · Accounting *"đã làm gì"*
- ⭐ **RADIUS cho người dùng vào mạng · TACACS+ cho kỹ sư vào thiết bị**
- RADIUS: **UDP 1812/1813**, chỉ mã hoá password, gộp Auth+Authz, chuẩn mở
- TACACS+: **TCP 49**, mã hoá **toàn bộ**, tách cả 3 A, **command authorization**
- ⭐ **Luôn có `local` ở cuối** câu lệnh AAA — dây an toàn khi server chết
- Luôn tạo **user local privilege 15 trước** khi `aaa new-model`
- Console nên dùng **method riêng** để cứu khi AAA hỏng
- Privilege level phân cấp **bậc thang** — hạn chế; TACACS+ linh hoạt hơn
- ⭐ **Accounting là thứ trả lời "ai đã làm gì"** khi có sự cố

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `username admin-local privilege 15 secret X` | ⭐ **Trước** khi bật AAA |
| `aaa authentication login default group X local` | ⭐ Có fallback |
| `aaa authorization commands 15 default group X local` | Kiểm soát từng lệnh |
| `aaa accounting commands 15 default start-stop group X` | Ghi log mọi lệnh |
| `test aaa group X <user> <pass> legacy` | ⭐ Test an toàn |
| `show aaa servers` | Server UP hay DOWN |
| `show privilege` / `show users` | Mình đang ở level nào, ai đang đăng nhập |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `local` ở cuối | AAA server chết = **mất quyền vào mọi thiết bị** |
| `aaa new-model` khi chưa có user local | Mất quyền **ngay lập tức** |
| Console dùng chung method với vty | Không còn đường cứu |
| Dùng TACACS+ cho 802.1X | 802.1X phải dùng **RADIUS** |
| Không bật accounting | Sự cố xảy ra không biết ai gây ra |
| Chỉ dựa vào privilege level | Không làm được quyền phức tạp |
| Không `test aaa` trước khi áp dụng | Phát hiện lỗi khi đã quá muộn |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 60 với đủ 3 lỗi BREAK — đặc biệt lỗi 1 *(mất quyền rồi khôi phục bằng console)*.
2. Viết ra **quy trình 5 bước** triển khai AAA an toàn của riêng bạn, lưu vào
   `06-security/quy-trinh-trien-khai-aaa.md`.
3. Kiểm tra thiết bị công ty: `show run | include aaa authentication` —
   có `local` ở cuối không?

```markdown
- [YYYY-MM-DD] Lesson 35 — CIA, AAA, RADIUS vs TACACS+: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | CIA, 3 chữ A, bảng RADIUS vs TACACS+, port, privilege level |
| 🔧 **Engineer** | `local` fallback; console method riêng; `test aaa` trước khi áp dụng |
| 🏭 **Production** | Quên `local` = mất quyền toàn hệ thống; accounting là bằng chứng khi có sự cố |

### 🔗 Liên kết

- ⬅️ [Phase 5 — Wireless](../05-wireless/README.md)
- ➡️ [Lesson 36 — ACL](./lesson-36-acl.md)
- 📚 802.1X chi tiết: [Lesson 34](../05-wireless/lesson-34-bao-mat-wifi.md)
