# LAB 60 — AAA với TACACS+ và RADIUS

> ⚠️ **Lỗi BREAK 1 và 3 làm bạn MẤT QUYỀN vào thiết bị.** Chỉ làm trong lab.
> Trên thiết bị thật, luôn giữ một phiên SSH đang mở khi thử nghiệm AAA.

| | |
|---|---|
| **Phase** | 6 |
| **Lesson liên quan** | [Lesson 35 — CIA, AAA, RADIUS vs TACACS+](../06-security/lesson-35-cia-aaa-radius-tacacs.md) |
| **Công cụ** | Cisco Packet Tracer *(có AAA server)* |
| **Thời lượng** | ~2 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Triển khai AAA theo **đúng quy trình an toàn 5 bước**
- [ ] Chứng minh `local` fallback cứu bạn khi AAA server chết
- [ ] Tạo user `helpdesk` privilege 5 chỉ chạy được `show`/`ping`
- [ ] Dùng `test aaa` để kiểm tra **trước khi** áp dụng
- [ ] Tự gây ra và tự khôi phục tình huống "mất quyền vào thiết bị"

## 2. Prerequisite

- [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md) — `username`, `privilege`, SSH
- [Lesson 35](../06-security/lesson-35-cia-aaa-radius-tacacs.md) — AAA, RADIUS vs TACACS+

---

## 3. Topology

```text
   PC-ADMIN                            AAA Server
  10.0.30.10                           10.0.50.60
       │                                    │
      SW1 ─────────── R1 ─────────────────  │
                   (thiết bị cần             │
                    bảo vệ)  ────────────────┘
```

| Thiết bị | Model gợi ý | Vai trò |
|---|---|---|
| R1 | ISR 2911 | Thiết bị cần bảo vệ bằng AAA |
| SW1 | 2960 | Nối các thành phần |
| AAA Server | **Server-PT** → tab **AAA** | RADIUS/TACACS+ server |
| PC-ADMIN | PC-PT | Máy kỹ sư SSH vào R1 |

## 4. IP Addressing Table

| Device | Interface | IP | Mask | Gateway |
|---|---|---|---|---|
| R1 | Gi0/0 *(LAN admin)* | `10.0.30.1` | `/24` | — |
| R1 | Gi0/1 *(tới server)* | `10.0.50.1` | `/24` | — |
| AAA Server | Fa0 | `10.0.50.60` | `/24` | `10.0.50.1` |
| PC-ADMIN | Fa0 | `10.0.30.10` | `/24` | `10.0.30.1` |

> 💡 Packet Tracer hỗ trợ **RADIUS** đầy đủ trên Server-PT (tab AAA).
> TACACS+ có hỗ trợ cơ bản. Lab này dùng **RADIUS** cho phần thực hành,
> và nêu rõ chỗ nào TACACS+ sẽ khác.

---

## 5. Yêu cầu LAB

- [ ] Tạo user local **trước** khi `aaa new-model`
- [ ] AAA authentication có `local` fallback
- [ ] Console dùng **method riêng**
- [ ] User `admin` → privilege 15; user `helpdesk` → privilege 5
- [ ] `test aaa` thành công trước khi áp dụng
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Cấu hình AAA Server

Trên Server-PT → tab **Services** → **AAA**:

| Mục | Giá trị |
|---|---|
| Service | **On** |
| Network Device Name | `R1` |
| Client IP | `10.0.50.1` |
| Secret | `Str0ngSecret` |
| ServerType | **Radius** |

Thêm User:

| Username | Password |
|---|---|
| `admin` | `AdminP@ss` |
| `helpdesk` | `HelpP@ss` |

### Bước 2 — Quy trình an toàn 5 bước ⭐

> 🔴 **Làm đúng thứ tự này.** Đây là bài học quan trọng nhất của lab.

```cisco
! ══ BƯỚC 1: TẠO USER LOCAL TRƯỚC — luôn luôn ══
R1(config)# username admin-local privilege 15 secret L0calBackup

! ══ BƯỚC 2: bật AAA và cấu hình CÓ FALLBACK ══
R1(config)# aaa new-model

R1(config)# radius server AAA-SRV
R1(config-radius-server)# address ipv4 10.0.50.60 auth-port 1645 acct-port 1646
R1(config-radius-server)# key Str0ngSecret
R1(config-radius-server)# exit

R1(config)# aaa group server radius RAD-GROUP
R1(config-sg-radius)# server name AAA-SRV
R1(config-sg-radius)# exit

!                                              ↓↓↓↓↓ DÂY AN TOÀN
R1(config)# aaa authentication login default group RAD-GROUP local
R1(config)# aaa authorization exec default group RAD-GROUP local

! ══ Console dùng METHOD RIÊNG — đường cứu ══
R1(config)# aaa authentication login CONSOLE local
R1(config)# line console 0
R1(config-line)# login authentication CONSOLE
R1(config-line)# logging synchronous
R1(config-line)# exit

! ══ SSH ══
R1(config)# ip domain-name cty.local
R1(config)# crypto key generate rsa modulus 1024
R1(config)# ip ssh version 2
R1(config)# line vty 0 15
R1(config-line)# transport input ssh
R1(config-line)# exit
```

> ⚠️ Packet Tracer dùng **port 1645/1646** *(RADIUS cũ)*, không phải 1812/1813.
> Trên thiết bị thật dùng **1812/1813**.

```cisco
! ══ BƯỚC 3: TEST TRƯỚC KHI TIN ══
R1# test aaa group RAD-GROUP admin AdminP@ss legacy
```

| Kết quả | Ý nghĩa |
|---|---|
| `User was successfully authenticated` | ✅ Đi tiếp |
| `User rejected` | ❌ Sai user/pass — kiểm tra server |
| `No authoritative response` | ❌ Không tới được server, hoặc **sai secret** |

```text
══ BƯỚC 4: MỞ PHIÊN SSH THỨ HAI để thử — ĐỪNG ĐÓNG phiên đang mở
══ BƯỚC 5: chỉ khi phiên mới vào được mới gõ `wr`
```

### Bước 3 — Privilege level cho helpdesk

```cisco
R1(config)# privilege exec level 5 show
R1(config)# privilege exec level 5 ping
R1(config)# privilege exec level 5 traceroute
R1(config)# enable secret level 5 L3vel5P@ss
```

Trên AAA server, cấu hình để user `helpdesk` nhận privilege 5.

> 💡 Packet Tracer **không** hỗ trợ trả về privilege level qua RADIUS attribute.
> Để mô phỏng, tạo thêm user local: `username helpdesk privilege 5 secret HelpP@ss`
> và tạm dùng `aaa authentication login default local` để thử.

Kiểm chứng từ PC-ADMIN:

```cisco
ssh -l helpdesk 10.0.30.1
R1> show ip interface brief        ← phải ĐƯỢC
R1> ping 10.0.50.60                ← phải ĐƯỢC
R1> configure terminal             ← phải BỊ TỪ CHỐI
```

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show aaa servers
RADIUS: id 1, priority 1, host 10.0.50.60, auth-port 1645, acct-port 1646
     State: current UP, duration 1842s, previous duration 0s
     Authen: request 12, timeouts 0
             Response: accept 11, reject 1, error 0
```

```text
# output điển hình — tự verify trên lab của bạn
R1# test aaa group RAD-GROUP admin AdminP@ss legacy
Attempting authentication test to server-group RAD-GROUP using radius
User was successfully authenticated.
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show users
    Line       User       Host(s)              Idle       Location
*  2 vty 0     admin      idle                 00:00:00   10.0.30.10

R1# show privilege
Current privilege level is 15
```

**Bảng kiểm chứng:**

| Việc | Mong đợi | Thực tế |
|---|---|---|
| `test aaa` với `admin` | Success | |
| `test aaa` với user sai | Rejected | |
| SSH bằng `admin` → `show privilege` | 15 | |
| SSH bằng `helpdesk` → `show privilege` | 5 | |
| `helpdesk` gõ `configure terminal` | Bị từ chối | |
| `show aaa servers` | `State: current UP` | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — AAA không có `local` fallback ⭐

> 🔴 **Đây là lỗi quan trọng nhất của lab.** Nó mô phỏng sự cố thật đã làm
> nhiều công ty mất quyền vào toàn bộ thiết bị.

```cisco
! Bỏ từ khoá "local"
R1(config)# aaa authentication login default group RAD-GROUP

! Giờ "giết" AAA server: tắt service AAA trên Server-PT (Service = Off)
```

| | |
|---|---|
| Thử SSH từ PC-ADMIN: kết quả? | |
| Thông báo lỗi là gì? | |
| Console có vào được không? **Vì sao?** | |
| Nếu console **cũng** dùng method default thì sao? | |

**Khôi phục:**

```cisco
! Vào bằng CONSOLE (nhờ có method riêng)
R1> enable
R1# configure terminal
R1(config)# aaa authentication login default group RAD-GROUP local
```

| | |
|---|---|
| Bài học rút ra | |

### Lỗi 2 — Sai shared secret

```cisco
R1(config)# radius server AAA-SRV
R1(config-radius-server)# key SaiSecret
```

| | |
|---|---|
| `test aaa group RAD-GROUP admin AdminP@ss legacy` → kết quả? | |
| `show aaa servers` → State là gì? | |
| Thông báo có nói rõ "sai secret" không? | |
| Làm sao phân biệt **sai secret** với **không tới được server**? | |

### Lỗi 3 — `aaa new-model` khi chưa có user local ⭐

> ⚠️ Lưu cấu hình hiện tại trước (`copy run flash:backup.cfg`) để khôi phục dễ hơn.

```cisco
! Xoá hết user local
R1(config)# no username admin-local
R1(config)# no username helpdesk

! Tắt AAA server trên Server-PT

! Giờ thoát và đăng nhập lại
R1# exit
```

| | |
|---|---|
| Có vào lại được không? | |
| Qua console thì sao? | |
| Khôi phục bằng cách nào? | |

> 🔧 Nếu kẹt hoàn toàn: dùng **password recovery** *(Lesson 12)* —
> trong Packet Tracer là `Ctrl+C` lúc boot để vào ROMMON, rồi
> `confreg 0x2142` + `reload` để bỏ qua startup-config.

### Lỗi 4 *(tự chọn)* — Thiếu `aaa authorization exec`

```cisco
R1(config)# no aaa authorization exec default group RAD-GROUP local
```

SSH vào bằng `admin`, rồi:

| | |
|---|---|
| `show privilege` hiện level mấy? | |
| Vì sao không vào thẳng level 15? | |
| Cần gõ gì để lên 15? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Viết **quy trình 5 bước** triển khai AAA an toàn bằng lời của bạn.
2. Công ty cần: kỹ sư SSH vào switch, nhân viên 802.1X Wi-Fi.
   Dùng giao thức nào cho việc nào? Viết cấu hình khung cho cả hai.
3. Bạn muốn helpdesk chạy được `clear counters` nhưng **không** được `clear ip route`.
   Privilege level làm được không? Giải pháp nào làm được?
4. `show aaa servers` hiện `State: current DOWN`. Nêu 3 nguyên nhân và cách phân biệt.

<details>
<summary>Đáp án</summary>

**1.** Quy trình 5 bước:

```text
1. TẠO user local privilege 15  ← trước mọi thứ
2. Cấu hình AAA, LUÔN có "local" ở cuối mỗi dòng authentication
   + console dùng method riêng (login authentication CONSOLE)
3. test aaa group ... → xác nhận server trả lời
4. MỞ PHIÊN SSH THỨ HAI thử đăng nhập — GIỮ phiên cũ đang mở
5. Chỉ khi phiên mới vào được mới `copy run start`
```

Bonus: trên thiết bị production, thêm `reload in 10` trước bước 2 làm lưới an toàn.

**2.**

| Việc | Giao thức | Vì sao |
|---|---|---|
| Kỹ sư SSH vào thiết bị | **TACACS+** | Tách Authorization → kiểm soát **từng lệnh**; mã hoá toàn bộ payload; TCP 49 |
| Nhân viên 802.1X Wi-Fi | **RADIUS** | Chuẩn mở, mọi AP/WLC hỗ trợ; UDP nhẹ, chịu được hàng nghìn phiên |

```cisco
! TACACS+ cho quản trị thiết bị
tacacs server ISE-TAC
 address ipv4 10.0.50.60
 key <secret>
aaa group server tacacs+ TAC-GROUP
 server name ISE-TAC
aaa authentication login default group TAC-GROUP local
aaa authorization commands 15 default group TAC-GROUP local
aaa accounting commands 15 default start-stop group TAC-GROUP

! RADIUS cho 802.1X
radius server ISE-RAD
 address ipv4 10.0.50.60 auth-port 1812 acct-port 1813
 key <secret>
aaa authentication dot1x default group radius
aaa authorization network default group radius
```

**3.** **Privilege level KHÔNG làm được.**

Lý do: privilege level phân cấp theo **bậc thang** — bạn gán lệnh vào một level,
và level cao hơn **tự động có mọi quyền của level thấp hơn**. Nhưng `clear counters`
và `clear ip route` đều bắt đầu bằng `clear`, và việc tách riêng hai lệnh con
rất khó quản lý khi số lệnh tăng lên.

Về kỹ thuật bạn *có thể* viết:

```cisco
privilege exec level 5 clear counters
```

— nhưng cách này không scale: mỗi lệnh phải khai riêng, và phải làm trên
**từng thiết bị**.

**Giải pháp đúng: TACACS+ command authorization**

```cisco
aaa authorization commands 15 default group TAC-GROUP local
```

Rồi trên TACACS+ server, viết policy cho nhóm `helpdesk`:

```text
permit  clear counters
deny    clear ip route
permit  show .*
deny    .*
```

Ưu điểm: quản lý **tập trung**, đổi quyền không cần đụng vào thiết bị,
và biểu diễn được quy tắc phức tạp.

**4.** Ba nguyên nhân, phân biệt như sau:

| # | Nguyên nhân | Cách phân biệt |
|:---:|---|---|
| 1 | **Không tới được server** *(route/firewall)* | `ping 10.0.50.60` → fail |
| 2 | **Sai shared secret** | `ping` **OK**, nhưng `test aaa` trả `No authoritative response`. Server có nhận gói nhưng không giải mã được |
| 3 | **Service trên server tắt / sai port** | `ping` OK; `telnet <server> 1812` *(hoặc 49 với TACACS+)* không kết nối được |

> 🔑 Điểm khó: **sai secret và không tới được server cho thông báo gần giống nhau**.
> Dùng `ping` để tách bạch: ping được mà vẫn fail → gần như chắc chắn là **secret**.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — thiếu `local`:**

| Quan sát | Giải thích |
|---|---|
| SSH: `% Authentication failed` hoặc treo rồi timeout | R1 hỏi RADIUS, không ai trả lời → **không có phương án dự phòng** → từ chối |
| Console: **vào được** ✅ | Nhờ `login authentication CONSOLE` dùng method `local` riêng |
| Nếu console cũng dùng default | **Mất quyền hoàn toàn** → phải password recovery |

**Bài học:** `local` ở cuối là **một từ** ngăn cách giữa "sự cố nhỏ" và
"phải chạy tới chỗ cắm console trên 40 thiết bị".

**Lỗi 2 — sai secret:**

```text
# output điển hình — tự verify trên lab của bạn
R1# test aaa group RAD-GROUP admin AdminP@ss legacy
No authoritative response from any server.
```

| Dấu hiệu | Giải thích |
|---|---|
| `show aaa servers` → `State: current DOWN` sau vài lần thử | Router không nhận được phản hồi hợp lệ |
| Thông báo **không nói rõ** "sai secret" | Đây là chủ ý bảo mật — không tiết lộ nguyên nhân |
| `ping 10.0.50.60` vẫn **OK** | ⭐ Đây là cách phân biệt với lỗi mạng |

**Lỗi 3 — `aaa new-model` không có user local:**

| Quan sát | Giải thích |
|---|---|
| SSH fail, console cũng fail *(nếu không có method riêng)* | Không có nguồn xác thực nào |
| Khôi phục | **Password recovery** — Packet Tracer: `Ctrl+C` lúc boot → `confreg 0x2142` → `reload` → router bỏ qua startup-config |

Sau khi vào được:

```cisco
R1# copy startup-config running-config
R1(config)# username admin-local privilege 15 secret L0calBackup
R1(config)# aaa authentication login default group RAD-GROUP local
R1(config)# config-register 0x2102
R1# copy running-config startup-config
```

**Lỗi 4 — thiếu `aaa authorization exec`:**

| Quan sát | Giải thích |
|---|---|
| `show privilege` → **level 1** | Authentication *(anh là ai)* thành công, nhưng **Authorization** *(anh được level mấy)* không chạy → mặc định level 1 |
| Phải gõ `enable` + enable secret để lên 15 | Dùng cơ chế enable truyền thống thay vì AAA |

👉 Bài học: **Authentication và Authorization là hai việc khác nhau.**
Đăng nhập được ≠ có quyền.

### Bảng tổng kết

| Dòng cấu hình | Nếu thiếu thì sao |
|---|---|
| `username admin-local privilege 15 secret X` | Mất quyền ngay khi bật AAA |
| `... group RAD-GROUP **local**` | Server chết = mất quyền toàn bộ |
| `login authentication CONSOLE` *(line console)* | Mất đường cứu cuối cùng |
| `aaa authorization exec default ...` | Đăng nhập vào level 1, không phải 15 |
| `test aaa` trước khi `wr` | Phát hiện lỗi khi đã quá muộn |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Lỗi 1 làm tôi hiểu ra điều gì? ___
- Tôi phân biệt "sai secret" với "không tới được server" bằng cách nào? ___
- Quy trình 5 bước của riêng tôi: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
