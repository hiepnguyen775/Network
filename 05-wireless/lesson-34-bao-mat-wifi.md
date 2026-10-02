# LESSON 34 — Bảo mật Wi-Fi: WPA2 · WPA3 · 802.1X

| | |
|---|---|
| **Phase** | 5 — Wireless |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 32](./lesson-32-wlan-ap-wlc.md), [Lesson 33](./lesson-33-rf-channel-roaming.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Nêu đúng thứ tự tiến hoá WEP → WPA → WPA2 → WPA3 và vấn đề từng đời
- [ ] Phân biệt **Personal (PSK)** và **Enterprise (802.1X)** — và khi nào dùng cái nào
- [ ] Mô tả **4-way handshake** và biết nó bị tấn công thế nào
- [ ] Giải thích 802.1X: ba vai trò **supplicant · authenticator · authentication server**
- [ ] Thiết kế bảo mật Wi-Fi cho một doanh nghiệp

## 2. Prerequisite

- SSID, BSSID, kiến trúc WLC *(Lesson 32)*
- Sóng đi khắp nơi — ai trong tầm cũng nghe được *(Lesson 32)*

---

## 3. Concept

### Vì sao Wi-Fi cần mã hoá — khác hẳn mạng có dây

| | Mạng có dây | Wi-Fi |
|---|---|---|
| Để nghe lén cần | **Truy cập vật lý** vào cáp/switch | Chỉ cần **ở trong tầm sóng** |
| Biên giới an ninh | Tường, cửa khoá | **Không có** |
| Ai cũng nghe được? | Không | **Có** — mọi frame bay trong không khí |

> ⭐ Đây là lý do **mã hoá là bắt buộc**, không phải tuỳ chọn. Mạng có dây có thể
> chạy không mã hoá vì có bảo vệ vật lý; Wi-Fi thì không có gì cả.

### Tiến hoá các chuẩn

| Chuẩn | Năm | Mã hoá | Trạng thái |
|---|:---:|---|---|
| **WEP** | 1997 | RC4, khoá tĩnh | ❌ **Bẻ trong vài phút** — tuyệt đối không dùng |
| **WPA** | 2003 | TKIP *(vá tạm cho WEP)* | ❌ Đã lỗi thời |
| **WPA2** | 2004 | **AES-CCMP** | ⚠️ Vẫn phổ biến, có lỗ hổng KRACK |
| **WPA3** | 2018 | **AES-GCMP + SAE** | ✅ **Nên dùng** |

> 🔑 **WEP sai ở đâu:** khoá tĩnh dùng chung, IV (initialization vector) chỉ 24 bit
> nên lặp lại rất nhanh. Bắt đủ gói là **tính ra được khoá** — không cần đoán mật khẩu.
> Công cụ bẻ WEP có từ 2001 và chạy trong vài phút.

### Personal vs Enterprise

| | **Personal (PSK)** | **Enterprise (802.1X)** |
|---|---|---|
| Xác thực bằng | **Một passphrase chung** | **Tài khoản riêng từng người** |
| Ai biết mật khẩu | Mọi người | Chỉ chủ tài khoản |
| Nhân viên nghỉ việc | ⚠️ **Phải đổi mật khẩu cho cả công ty** | ✅ Khoá một tài khoản |
| Truy vết "ai đã làm gì" | ❌ Không thể | ✅ Theo username |
| Gán VLAN theo người | ❌ | ✅ **Dynamic VLAN assignment** |
| Cần hạ tầng | Không | **RADIUS server** |
| Phù hợp | Nhà, quán cà phê, guest | ⭐ **Doanh nghiệp** |

> 🏭 Câu hỏi quyết định: *"Khi một nhân viên nghỉ việc, bạn làm gì?"*
> Với PSK, câu trả lời là **đổi mật khẩu rồi cấu hình lại 200 thiết bị**.
> Với 802.1X, là **vô hiệu hoá một tài khoản AD**.

### 4-way handshake (WPA2-PSK)

```text
Cả hai bên đã có PMK (Pairwise Master Key) — dẫn xuất từ passphrase + SSID

AP ──[1] ANonce ──────────────▶ Client
                                  │ Client tính PTK từ:
                                  │   PMK + ANonce + SNonce + 2 MAC
Client ──[2] SNonce + MIC ─────▶ AP
                                  │ AP cũng tính PTK, kiểm MIC
AP ──[3] GTK + MIC ────────────▶ Client
Client ──[4] ACK ──────────────▶ AP

→ Cả hai có PTK (khoá unicast) và GTK (khoá broadcast/multicast)
```

> ⚠️ **Passphrase KHÔNG bao giờ được truyền đi.** Nhưng kẻ tấn công bắt được
> 4-way handshake có thể **brute-force offline**: thử từng mật khẩu, tính PTK,
> so với MIC đã bắt được.
>
> Đây là lý do **mật khẩu Wi-Fi phải dài và ngẫu nhiên**. `congty2024` bị bẻ trong vài phút.

### KRACK và vì sao WPA3 ra đời

**KRACK** (2017) khai thác việc **ép client cài lại khoá** ở bước 3 của handshake,
làm reset bộ đếm nonce → có thể giải mã một phần traffic.

**WPA3 thay 4-way handshake bằng SAE** (Simultaneous Authentication of Equals,
còn gọi là Dragonfly):

| | WPA2-PSK | WPA3-SAE |
|---|---|---|
| Brute-force offline | ✅ **Làm được** | ❌ **Không thể** |
| Forward secrecy | ❌ Không | ✅ **Có** — bắt được traffic cũ cũng không giải mã được sau này |
| Mã hoá mạng mở | ❌ | ✅ **OWE** (Enhanced Open) |
| Mã hoá | AES-CCMP 128 | AES-GCMP 128/256 |

> ⭐ **Forward secrecy** là cải tiến lớn nhất: với WPA2, nếu kẻ tấn công lưu lại
> traffic mã hoá hôm nay và **sau này có được mật khẩu**, họ giải mã được toàn bộ.
> Với WPA3-SAE thì không.

### 802.1X — ba vai trò

```text
┌──────────┐      EAPOL       ┌──────────┐    RADIUS    ┌──────────────┐
│SUPPLICANT│ ◀──────────────▶ │AUTHENTI- │ ◀──────────▶ │AUTHENTICATION│
│ (client) │   qua không dây  │  CATOR   │  qua có dây  │    SERVER    │
│          │                  │ (AP/WLC) │              │   (RADIUS)   │
└──────────┘                  └──────────┘              └──────────────┘
                                                               │
                                                        ┌──────┴──────┐
                                                        │ AD / LDAP   │
                                                        └─────────────┘
```

| Vai trò | Là ai | Làm gì |
|---|---|---|
| **Supplicant** | Phần mềm trên client | Gửi thông tin xác thực |
| **Authenticator** | AP/WLC *(hoặc switch với mạng dây)* | **Chuyển tiếp** — không tự quyết định |
| **Authentication Server** | RADIUS *(ISE, NPS, FreeRADIUS)* | **Quyết định** cho vào hay không |

> 🔑 Authenticator **không biết mật khẩu** và **không tự quyết định** —
> nó chỉ là người gác cổng chuyển giấy tờ cho người có thẩm quyền.
> Đây là lý do 802.1X scale được: thêm 100 AP không cần cấu hình lại gì về tài khoản.

### Các phương thức EAP

| Phương thức | Client xác thực bằng | Server xác thực bằng | Thực tế |
|---|---|---|---|
| **PEAP-MSCHAPv2** | Username/password | Chứng chỉ server | ⭐ **Phổ biến nhất** — dễ triển khai |
| **EAP-TLS** | **Chứng chỉ client** | Chứng chỉ server | ✅ **An toàn nhất**, cần PKI |
| EAP-TTLS | Username/password | Chứng chỉ server | Giống PEAP |
| EAP-FAST | PAC file | PAC | Cisco, ít dùng |

> 🏭 **PEAP-MSCHAPv2** là lựa chọn mặc định ở hầu hết doanh nghiệp vì dùng luôn
> tài khoản Active Directory. **EAP-TLS** an toàn hơn nhưng cần triển khai PKI
> và quản lý chứng chỉ cho từng thiết bị.

> ⚠️ Với PEAP, client **phải kiểm tra chứng chỉ server**. Nếu không, kẻ tấn công
> dựng AP giả cùng SSID → client gửi thông tin đăng nhập cho họ (**evil twin attack**).

### Dynamic VLAN assignment

RADIUS trả về **VLAN** cùng với kết quả xác thực:

```text
Nhân viên IT  đăng nhập  →  RADIUS trả VLAN 30
Nhân viên Sales đăng nhập →  RADIUS trả VLAN 10
Khách          đăng nhập  →  RADIUS trả VLAN 90
```

Tất cả dùng **một SSID duy nhất** — nhưng được đặt vào VLAN khác nhau tuỳ danh tính.

> ⭐ Đây là giải pháp cho vấn đề "quá nhiều SSID" ở [Lesson 32](./lesson-32-wlan-ap-wlc.md):
> **một SSID, nhiều chính sách**.

---

## 4. Why?

> **Vì sao không dùng PSK cho doanh nghiệp?**

| Vấn đề | Chi tiết |
|---|---|
| **Mật khẩu lan truyền** | Ai cũng biết → nhân viên chia cho bạn bè, lưu trên điện thoại cá nhân |
| **Nghỉ việc = đổi mật khẩu cả công ty** | 200 thiết bị phải cấu hình lại |
| **Không truy vết được** | Log chỉ có MAC — không biết ai đang dùng |
| **Không phân quyền** | Mọi người vào cùng một VLAN |
| **Brute-force offline** | Bắt handshake rồi đoán mật khẩu ngoại tuyến |

> **Vì sao mạng khách (guest) vẫn dùng PSK được?**

Vì guest network **vốn đã bị cô lập hoàn toàn** — chỉ ra Internet, không vào được nội bộ.
Mật khẩu lộ cũng không gây hại nhiều. Thường kết hợp thêm **captive portal**.

> 🔧 Thiết kế thực tế: **nhân viên → WPA2/3-Enterprise · khách → WPA2-PSK + captive portal
> + VLAN cô lập · IoT → PSK riêng + VLAN riêng + ACL chặt**.

---

## 5. How does it work? — 802.1X từng bước

```text
1. Client kết nối SSID có 802.1X
2. AP mở "cổng điều khiển" — CHỈ cho EAPOL đi qua, chặn mọi thứ khác
3. AP gửi EAP-Request/Identity  → client
4. Client trả EAP-Response/Identity (username) → AP
5. AP ĐÓNG GÓI vào RADIUS Access-Request → gửi RADIUS server
6. RADIUS ↔ client trao đổi EAP (qua AP làm trung gian):
   - Server gửi chứng chỉ của mình → client KIỂM TRA
   - Client gửi credential qua tunnel TLS đã mã hoá
7. RADIUS kiểm tra với AD/LDAP
8. RADIUS trả Access-Accept (+ VLAN, + các thuộc tính khác)
   hoặc Access-Reject
9. AP MỞ cổng → client làm 4-way handshake để lấy khoá mã hoá
10. Client vào được mạng, được đặt vào đúng VLAN
```

> 🔑 Bước 2 là cốt lõi của 802.1X: **cổng bị khoá cho tới khi xác thực xong**.
> Trước đó client không gửi được DHCP, không ping được gì — chỉ có EAPOL.

---

## 6. Packet Flow — WPA2-PSK vs WPA2-Enterprise

| Bước | **WPA2-PSK** | **WPA2-Enterprise** |
|:---:|---|---|
| 1 | Probe / Auth / Association | Probe / Auth / Association |
| 2 | — | **802.1X/EAP với RADIUS** |
| 3 | PMK = từ passphrase + SSID | PMK = **do RADIUS sinh ra**, khác nhau mỗi client |
| 4 | **4-way handshake** | **4-way handshake** |
| 5 | Truyền dữ liệu | Truyền dữ liệu |

> 🔑 Khác biệt duy nhất là **nguồn gốc của PMK**. Với PSK, mọi client dùng chung
> một PMK dẫn xuất từ passphrase. Với Enterprise, **mỗi client có PMK riêng**
> do RADIUS sinh — nên biết mật khẩu của người này cũng không giải mã được traffic
> của người kia.

---

## 7. Real-world Example

🏭 **Thiết kế bảo mật Wi-Fi cho doanh nghiệp 200 người**

| SSID | Bảo mật | VLAN | Chính sách |
|---|---|:---:|---|
| `CTY-NV` | **WPA2/3-Enterprise** *(PEAP-MSCHAPv2 + AD)* | Động theo phòng ban | Đầy đủ quyền nội bộ |
| `CTY-GUEST` | **WPA2-PSK** + captive portal | 90 | **Chỉ Internet**, ACL chặn mọi dải nội bộ |
| `CTY-IOT` | **WPA2-PSK** *(mật khẩu riêng, dài)* | 70 | Chỉ ra server quản lý, chặn còn lại |

```cisco
! ACL cô lập VLAN guest (áp trên SVI VLAN 90)
ip access-list extended GUEST-ISOLATE
 deny   ip 10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255
 permit ip 10.0.90.0 0.0.0.255 any
```

🏭 **Evil twin attack — vì sao phải kiểm chứng chỉ server**

```text
1. Kẻ tấn công dựng AP giả, SSID giống hệt "CTY-NV", tín hiệu mạnh hơn
2. Client tự động kết nối (vì đã lưu SSID)
3. AP giả chạy RADIUS giả, gửi chứng chỉ TỰ KÝ
4. Nếu client KHÔNG kiểm tra chứng chỉ:
   → gửi username + password hash cho kẻ tấn công
5. Kẻ tấn công bẻ hash offline → có tài khoản AD
```

**Phòng chống:**

| Cách | Chi tiết |
|---|---|
| Bật **"Verify server certificate"** trên client | Và chỉ định đúng CA |
| Triển khai qua **GPO/MDM** | Người dùng không tự tắt được |
| Dùng **EAP-TLS** | Không có password để đánh cắp |

🏭 **PSK bị lộ — sự cố thường gặp nhất**

```text
Mật khẩu Wi-Fi nhân viên được chia sẻ qua chat nhóm
→ nhân viên cũ vẫn vào được sau khi nghỉ
→ khách tới chơi cũng vào mạng nội bộ
→ không ai biết ai đang dùng
```

Đây là lý do **nghiêm túc nhất** để chuyển sang 802.1X — không phải vì nó "an toàn hơn"
về mặt mật mã, mà vì nó cho bạn **danh tính và khả năng thu hồi**.

🏭 **WPA3 transition mode — cẩn thận**

```text
WPA3 Transition Mode: chấp nhận cả WPA2 và WPA3 trên cùng SSID
→ thiết bị cũ vẫn kết nối được
→ NHƯNG kẻ tấn công có thể ÉP client hạ xuống WPA2 (downgrade attack)
```

> 🔧 Transition mode là **giải pháp tạm** khi chuyển đổi. Khi mọi thiết bị đã hỗ trợ
> WPA3, chuyển sang **WPA3-only**.

---

## 8. Cisco CLI

> 💡 Cấu hình WLAN chủ yếu trên **WLC qua GUI**. Phần CLI quan trọng với bạn là
> **RADIUS trên thiết bị** và **ACL cô lập VLAN**.

```cisco
! ═══════ RADIUS SERVER ═══════
R1(config)# radius server ISE-01
R1(config-radius-server)# address ipv4 10.0.50.60 auth-port 1812 acct-port 1813
R1(config-radius-server)# key <shared-secret>
R1(config-radius-server)# exit

R1(config)# aaa new-model
R1(config)# aaa group server radius RADIUS-GROUP
R1(config-sg-radius)# server name ISE-01
R1(config-sg-radius)# exit

R1(config)# aaa authentication dot1x default group RADIUS-GROUP
R1(config)# aaa authorization network default group RADIUS-GROUP
R1(config)# aaa accounting dot1x default start-stop group RADIUS-GROUP

! ═══════ 802.1X TRÊN PORT CÓ DÂY (cùng nguyên lý) ═══════
SW1(config)# dot1x system-auth-control
SW1(config)# interface GigabitEthernet1/0/5
SW1(config-if)# switchport mode access
SW1(config-if)# authentication port-control auto
SW1(config-if)# dot1x pae authenticator
SW1(config-if)# authentication host-mode multi-domain    ! cho IP phone + PC
SW1(config-if)# spanning-tree portfast

! ═══════ ACL CÔ LẬP VLAN GUEST ═══════
SW1(config)# ip access-list extended GUEST-ISOLATE
SW1(config-ext-nacl)# deny   ip 10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255
SW1(config-ext-nacl)# permit ip 10.0.90.0 0.0.0.255 any
SW1(config)# interface vlan 90
SW1(config-if)# ip access-group GUEST-ISOLATE in

! ═══════ KIỂM TRA ═══════
SW1# show dot1x all
SW1# show authentication sessions
SW1# show aaa servers
SW1# test aaa group RADIUS-GROUP <user> <pass> new-code
```

**Trên WLC:**

```text
(WLC) > show wlan summary
(WLC) > show wlan <id>
(WLC) > show radius summary
(WLC) > show client detail <MAC>
```

| Lệnh | Lưu ý |
|---|---|
| `aaa new-model` | ⚠️ Bật là **đổi hành vi đăng nhập** — cẩn thận trên thiết bị đang chạy |
| `authentication port-control auto` | Bật 802.1X trên port |
| `host-mode multi-domain` | Cho phép IP phone **và** PC sau phone |
| `test aaa group ... new-code` | ⭐ Test RADIUS **không cần client thật** |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show authentication sessions interface GigabitEthernet1/0/5
            Interface:  GigabitEthernet1/0/5
          MAC Address:  0011.2233.4455
           IP Address:  10.0.30.57
            User-Name:  nguyen.van.a
               Status:  Authz Success
               Domain:  DATA
      Oper host mode:  multi-domain
    Oper control dir:  both
       Authorized By:  Authentication Server
         Vlan Policy:  30
      Session timeout:  N/A
         Idle timeout:  N/A
    Common Session ID:  0A003C0100000012
      Acct Session ID:  0x00000018
               Handle:  0x4C000013
Runnable methods list:
       Method   State
       dot1x    Authc Success
```

**Đọc gì:**

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `User-Name` | ⭐ **Danh tính** — thứ PSK không có | Trống → chưa xác thực |
| `Status: Authz Success` | Đã xác thực và cấp quyền ✅ | `Unauthorized` → bị từ chối |
| `Authorized By: Authentication Server` | RADIUS quyết định ✅ | `Guest VLAN` → xác thực thất bại |
| **`Vlan Policy: 30`** | ⭐ **Dynamic VLAN** từ RADIUS | Không có → RADIUS chưa trả VLAN |
| `dot1x Authc Success` | Phương thức dùng | `Failed` → sai credential hoặc chứng chỉ |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show aaa servers | include RADIUS|State
RADIUS: id 1, priority 1, host 10.0.50.60, auth-port 1812, acct-port 1813
     State: current UP, duration 84233s, previous duration 0s
```

> ⚠️ `State: current DOWN` → RADIUS không tới được. Kiểm tra: route, firewall
> (UDP **1812/1813**), và **shared secret** có khớp không.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Client không kết nối được, báo sai mật khẩu | Sai passphrase, hoặc sai EAP method | Log trên WLC/RADIUS | Kiểm tra cấu hình supplicant |
| Mọi client đều fail | **RADIUS không tới được** hoặc sai shared secret | `show aaa servers` | Mở UDP 1812/1813, kiểm tra key |
| Client xác thực OK nhưng không có IP | VLAN RADIUS trả về không tồn tại/không có DHCP | `show authentication sessions` xem `Vlan Policy` | Tạo VLAN, cấu hình DHCP |
| Client vào được nhưng sai VLAN | RADIUS không trả thuộc tính VLAN | Log RADIUS | Cấu hình policy trả `Tunnel-Private-Group-ID` |
| Một số thiết bị cũ không kết nối được | Không hỗ trợ WPA3, hoặc 802.11r | WLC → client log | Transition mode, hoặc SSID riêng |
| Client bị hỏi đăng nhập liên tục | Chứng chỉ server hết hạn / không tin cậy | Kiểm tra chứng chỉ RADIUS | Gia hạn chứng chỉ, đẩy CA qua GPO |
| Nghi có AP giả cùng SSID | **Evil twin** | WLC → Rogue AP detection | Bật rogue detection; buộc client verify cert |
| IP phone + PC cùng port không chạy | Thiếu `host-mode multi-domain` | `show authentication sessions` | Thêm lệnh đó |
| Guest vào được mạng nội bộ | ACL cô lập thiếu hoặc sai hướng | `show access-lists` | Sửa ACL trên SVI VLAN guest |

---

## 11. LAB

🧪 **LAB 50 — Bảo mật Wi-Fi** → [`../labs/lab50-bao-mat-wifi.md`](../labs/lab50-bao-mat-wifi.md)

Yêu cầu tối thiểu:

- Trong Packet Tracer: WLC + 2 SSID — một **WPA2-PSK** (guest), một **WPA2-Enterprise**
  (nhân viên, dùng RADIUS server của Packet Tracer)
- Guest vào VLAN 90, **ACL chặn** mọi dải nội bộ → verify bằng ping
- Nhân viên xác thực bằng username/password → vào VLAN 10
- **Trên máy thật**: bắt 4-way handshake bằng Wireshark *(filter `eapol`)*,
  đếm đủ 4 gói
- **BREAK bắt buộc:** (1) sai shared secret RADIUS → quan sát `show aaa servers` DOWN;
  (2) xoá ACL guest → chứng minh guest vào được nội bộ;
  (3) RADIUS trả VLAN không tồn tại → client xác thực OK nhưng không có IP

## 12. Challenge

1. Công ty 200 người dùng WPA2-PSK. Một nhân viên nghỉ việc. Phải làm gì?
   So với nếu dùng 802.1X.
2. Kẻ tấn công bắt được 4-way handshake của mạng WPA2-PSK. Họ làm được gì?
   Với WPA3-SAE thì sao?
3. Client kết nối được SSID Enterprise nhưng **không nhận được IP**.
   Nêu 3 nguyên nhân theo thứ tự kiểm tra.
4. Vì sao Enterprise an toàn hơn PSK về mặt **mã hoá**, không chỉ về quản lý?

<details>
<summary>Đáp án</summary>

**1.**

| | **WPA2-PSK** | **802.1X Enterprise** |
|---|---|---|
| Phải làm gì | **Đổi passphrase** trên WLC | **Vô hiệu hoá một tài khoản AD** |
| Ảnh hưởng | **Toàn bộ 200 thiết bị** phải nhập lại mật khẩu | Không ai khác bị ảnh hưởng |
| Thời gian | Vài ngày, helpdesk ngập việc | **30 giây** |
| Rủi ro nếu không làm | Nhân viên cũ vẫn vào được mạng | — |

Thực tế: vì quá phiền, **hầu như không ai đổi mật khẩu** khi có người nghỉ việc.
Đó là lỗ hổng thật sự của PSK.

**2.**

| | **WPA2-PSK** | **WPA3-SAE** |
|---|---|---|
| Bắt được handshake | ✅ | ✅ |
| **Brute-force offline** | ✅ **Làm được** — thử từng mật khẩu, tính PTK, so MIC | ❌ **Không thể** — SAE không cho phép |
| Nếu sau này có mật khẩu | **Giải mã được toàn bộ traffic cũ** đã lưu | ❌ **Forward secrecy** — không giải mã được |

Với WPA2-PSK, mật khẩu yếu như `congty2024` bị bẻ trong vài phút bằng từ điển.
WPA3-SAE buộc kẻ tấn công phải thử **trực tuyến** với AP — chậm và dễ bị phát hiện.

**3.** Thứ tự kiểm tra:

| # | Nguyên nhân | Kiểm chứng |
|:---:|---|---|
| 1 | **RADIUS trả VLAN không tồn tại** trên switch/WLC | `show authentication sessions` xem `Vlan Policy`, rồi `show vlan brief` |
| 2 | **VLAN đó không có DHCP** (thiếu pool hoặc thiếu `ip helper-address`) | `show ip dhcp pool`, `show run interface vlan X` |
| 3 | VLAN chưa được allowed trên trunk tới AP (FlexConnect) | `show interfaces trunk` |

**4.** Vì **mỗi client có PMK (Pairwise Master Key) riêng**.

```text
WPA2-PSK:
  PMK = PBKDF2(passphrase, SSID)
  → MỌI client dùng CHUNG một PMK
  → Ai biết passphrase + bắt được handshake của người khác
     → GIẢI MÃ ĐƯỢC traffic của người đó

WPA2-Enterprise:
  PMK do RADIUS sinh RIÊNG cho từng phiên, từng client
  → Biết mật khẩu của mình KHÔNG giúp giải mã traffic của người khác
```

Nói cách khác: với PSK, **đồng nghiệp có thể nghe lén traffic của bạn** nếu họ muốn —
họ có cùng mật khẩu. Với Enterprise thì không.

👉 Đây là lý do về **mã hoá** (không chỉ quản lý) khiến Enterprise bắt buộc
với mạng xử lý dữ liệu nhạy cảm.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | WEP/WPA/WPA2/WPA3 · 3 vai trò 802.1X · port RADIUS · các EAP method | ⬜ |
| **L2** Explain | Giải thích vì sao Enterprise an toàn hơn PSK **về mã hoá** | ⬜ |
| **L3** Configure | Cấu hình RADIUS + 802.1X + ACL cô lập guest | ⬜ |
| **L4** Troubleshoot | Client xác thực OK nhưng không có IP → tìm nguyên nhân | ⬜ |
| **L5** Design | Thiết kế bảo mật Wi-Fi cho công ty: SSID, VLAN, chính sách | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **Mã hoá là bắt buộc với Wi-Fi** — không có biên giới vật lý như mạng dây
- **WEP** bẻ trong vài phút *(IV 24 bit)* · **WPA2** = AES-CCMP · **WPA3** = AES-GCMP + SAE
- **Personal (PSK)** = mật khẩu chung · **Enterprise (802.1X)** = tài khoản riêng
- ⭐ **4-way handshake không truyền passphrase**, nhưng cho phép **brute-force offline**
- **WPA3-SAE** chống brute-force offline và có **forward secrecy**
- 802.1X 3 vai trò: **supplicant** · **authenticator** *(chỉ chuyển tiếp)* · **RADIUS**
- EAP: **PEAP-MSCHAPv2** *(phổ biến)* · **EAP-TLS** *(an toàn nhất, cần PKI)*
- ⚠️ Client **phải kiểm chứng chỉ server** — nếu không sẽ dính **evil twin**
- ⭐ **Dynamic VLAN assignment**: một SSID, nhiều VLAN tuỳ danh tính
- ⭐ Enterprise an toàn hơn cả về **mã hoá**: mỗi client một PMK riêng
- RADIUS: **UDP 1812** *(auth)* · **1813** *(accounting)*

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `radius server X` + `address ipv4 ... auth-port 1812` | Khai báo RADIUS |
| `authentication port-control auto` | Bật 802.1X trên port |
| `host-mode multi-domain` | IP phone + PC cùng port |
| `show authentication sessions` | ⭐ Ai đang đăng nhập, VLAN nào |
| `show aaa servers` | RADIUS UP hay DOWN |
| `test aaa group ... new-code` | ⭐ Test RADIUS không cần client thật |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Dùng PSK cho mạng nhân viên | Không truy vết được, nghỉ việc phải đổi cả công ty |
| Không kiểm chứng chỉ server ở client | **Evil twin** đánh cắp credential |
| Mật khẩu PSK ngắn/dễ đoán | Brute-force offline trong vài phút |
| Guest không có ACL cô lập | Khách vào được mạng nội bộ |
| Để WPA3 transition mode vĩnh viễn | Có thể bị **downgrade attack** |
| Quên `host-mode multi-domain` | IP phone + PC không cùng port được |
| RADIUS shared secret sai | Mọi client fail, khó đoán nguyên nhân |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 50 với đủ 3 lỗi BREAK.
2. Trên máy thật: Wireshark filter `eapol`, ngắt rồi kết nối lại Wi-Fi →
   bắt đủ **4 gói** của 4-way handshake.
3. Kiểm tra Wi-Fi công ty bạn đang dùng chuẩn gì:
   `netsh wlan show interfaces` → xem dòng `Authentication`.
4. Trên máy Windows: mở cài đặt Wi-Fi Enterprise, kiểm tra
   **"Verify the server's identity by validating the certificate"** có bật không.

```markdown
- [YYYY-MM-DD] Lesson 34 — Bảo mật Wi-Fi: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 5

Làm **[Mini Exam Phase 5](./review-phase05.md)** trước khi sang
[Phase 6 — Security](../06-security/README.md).

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | WPA2 vs WPA3, PSK vs Enterprise, 3 vai trò 802.1X, EAP method, port RADIUS |
| 🔧 **Engineer** | Dynamic VLAN; ACL cô lập guest; `test aaa` để kiểm tra RADIUS |
| 🏭 **Production** | PSK = không truy vết được; evil twin; mỗi client một PMK là lợi ích thật của Enterprise |

### 🔗 Liên kết

- ⬅️ [Lesson 33 — RF, kênh, roaming](./lesson-33-rf-channel-roaming.md)
- 📝 [Mini Exam Phase 5](./review-phase05.md)
- ➡️ [Phase 6 — Security](../06-security/README.md)
- 🔜 AAA, RADIUS vs TACACS+ chi tiết: [Lesson 35](../06-security/README.md)
