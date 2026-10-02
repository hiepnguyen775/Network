# LAB 50 — Bảo mật Wi-Fi

| | |
|---|---|
| **Phase** | 5 |
| **Lesson liên quan** | [Lesson 34 — Bảo mật Wi-Fi](../05-wireless/lesson-34-bao-mat-wifi.md) |
| **Công cụ** | Cisco Packet Tracer *(WLC + LAP + AAA)* |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Tạo 2 WLAN: **nhân viên (WPA2-Enterprise/802.1X)** và **khách (WPA2-PSK)**
- [ ] Mỗi SSID gắn **VLAN riêng** → cô lập traffic
- [ ] ACL cô lập: guest **không** vào mạng nội bộ, chỉ ra Internet
- [ ] Hiểu luồng **802.1X**: supplicant → authenticator → RADIUS
- [ ] Tự gây & sửa 3 lỗi Wi-Fi bảo mật

## 2. Prerequisite

- [Lesson 32](../05-wireless/lesson-32-wlan-ap-wlc.md) — WLC, CAPWAP, LAP
- [Lesson 34](../05-wireless/lesson-34-bao-mat-wifi.md) — WPA2/WPA3, PSK vs 802.1X
- [LAB 60](lab60-aaa-tacacs-radius.md) — RADIUS *(802.1X dùng RADIUS)*
- [LAB 61](lab61-acl.md) — ACL cô lập

---

## 3. Topology

```text
   Laptop-NV ))) ┌─────┐           VLAN 10 nhân viên
   Laptop-KH ))) │ LAP │~CAPWAP~ WLC ── SW-L3 ── R1 ── Internet
                 └─────┘                 │
                                      RADIUS 10.0.99.60
                                      (802.1X cho nhân viên)
```

| Thiết bị | Vai trò |
|---|---|
| WLC | Quản lý LAP, định nghĩa WLAN |
| LAP | Access point *(lightweight, qua CAPWAP)* |
| RADIUS | Xác thực 802.1X cho nhân viên |
| SW-L3 | Inter-VLAN + ACL cô lập |

## 4. VLAN / SSID plan

| SSID | Bảo mật | VLAN | Subnet | Truy cập |
|---|---|:---:|---|---|
| `CTY-NhanVien` | WPA2-Enterprise *(802.1X)* | 10 | `10.0.10.0/24` | nội bộ + Internet |
| `CTY-Khach` | WPA2-PSK | 90 | `10.0.90.0/24` | **chỉ** Internet |

---

## 5. Yêu cầu LAB

- [ ] Laptop nhân viên vào `CTY-NhanVien` bằng user/pass *(802.1X)*
- [ ] Laptop khách vào `CTY-Khach` bằng mật khẩu chung *(PSK)*
- [ ] Khách **không** ping được server/nhân viên nội bộ
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — WLC + CAPWAP

Cấu hình cơ bản WLC *(management interface, LAP join qua CAPWAP)*.

> 💡 Trong Packet Tracer: dùng **WLC 3504** + **LAP**. LAP tự join WLC khi cùng subnet
> management *(hoặc qua option 43 của DHCP)*.

### Bước 2 — WLAN khách (WPA2-PSK)

Trên WLC → WLANs → Create:

| Mục | Giá trị |
|---|---|
| Profile/SSID | `CTY-Khach` |
| VLAN/Interface | `guest` *(VLAN 90)* |
| Layer 2 Security | **WPA2 + PSK** |
| PSK | `Khach@2026` |

### Bước 3 — WLAN nhân viên (802.1X) ⭐

| Mục | Giá trị |
|---|---|
| Profile/SSID | `CTY-NhanVien` |
| VLAN/Interface | `staff` *(VLAN 10)* |
| Layer 2 Security | **WPA2 + 802.1X** |
| AAA Server | RADIUS `10.0.99.60` |

Cấu hình RADIUS trên WLC *(Security → RADIUS → Authentication)*: IP `10.0.99.60`,
shared secret khớp với server.

> 🔑 **Luồng 802.1X:**
> ```
> Laptop (supplicant) → LAP/WLC (authenticator) → RADIUS (authentication server)
>        EAP over LAN              RADIUS
> ```
> WLC **không** tự xác thực — nó chuyển tiếp tới RADIUS. Mỗi user một tài khoản riêng.

### Bước 4 — ACL cô lập guest

```cisco
! Trên SW-L3 (SVI VLAN 90)
SW-L3(config)# ip access-list extended GUEST-ISOLATE
SW-L3(config-ext-nacl)# permit udp 10.0.90.0 0.0.0.255 host 10.0.99.53 eq 53
SW-L3(config-ext-nacl)# deny   ip 10.0.90.0 0.0.0.255 10.0.0.0 0.0.255.255
SW-L3(config-ext-nacl)# permit ip 10.0.90.0 0.0.0.255 any
SW-L3(config)# interface vlan 90
SW-L3(config-if)# ip access-group GUEST-ISOLATE in
```

> 🔴 **DỰ ĐOÁN:** với ACL này, khách ping server nội bộ `10.0.10.80` được không?
> Ping `8.8.8.8` được không? Phân giải DNS được không?

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
WLC> show wlan summary
Number of WLANs.................................. 2
WLAN ID  WLAN Profile Name   SSID            Status  Security
1        CTY-NhanVien        CTY-NhanVien    Enabled [WPA2][802.1X]
2        CTY-Khach           CTY-Khach       Enabled [WPA2][PSK]
```

```text
# output điển hình — tự verify trên lab của bạn
WLC> show client summary
MAC Address       AP Name   WLAN   State         Protocol
00d0.ba11.1111    LAP01     1      Associated    802.11n
00d0.ba22.2222    LAP01     2      Associated    802.11n
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | NV vào `CTY-NhanVien` bằng user/pass | ✅ | |
| 2 | Khách vào `CTY-Khach` bằng PSK | ✅ | |
| 3 | NV nhận IP VLAN 10, khách VLAN 90 | ✅ | |
| 4 | Khách ping `8.8.8.8` | ✅ | |
| 5 | Khách ping `10.0.10.80` *(nội bộ)* | ❌ | |
| 6 | Khách phân giải DNS | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — RADIUS chết, 802.1X không vào được ⭐

```text
Tắt RADIUS server (hoặc sai shared secret trên WLC)
```

| | |
|---|---|
| Laptop NV còn kết nối `CTY-NhanVien` không? | |
| Khách *(PSK)* có bị ảnh hưởng không? Vì sao? | |
| Luồng 802.1X dừng ở bước nào? | |
| PSK và 802.1X — cái nào phụ thuộc server ngoài? | |

### Lỗi 2 — SSID guest gắn nhầm VLAN nội bộ

```text
Đổi interface của CTY-Khach từ VLAN 90 → VLAN 10 (staff)
```

| | |
|---|---|
| Khách nhận IP dải nào? | |
| ACL cô lập *(trên VLAN 90)* còn tác dụng với khách không? | |
| Khách giờ có vào được mạng nội bộ không? | |
| Vì sao "gắn đúng VLAN" là nền tảng của cô lập? | |

### Lỗi 3 — ACL guest đặt sai chiều / thiếu permit DNS

```cisco
SW-L3(config)# ip access-list extended GUEST-ISOLATE
SW-L3(config-ext-nacl)# no permit udp 10.0.90.0 0.0.0.255 host 10.0.99.53 eq 53
```

| | |
|---|---|
| Khách còn phân giải tên miền được không? | |
| Ping `8.8.8.8` *(bằng IP)* có được không? | |
| Mở `google.com` *(bằng tên)* có được không? | |
| Bài học về thứ tự permit DNS trước deny nội bộ? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. PSK vs 802.1X: nêu 3 khác biệt. Vì sao doanh nghiệp dùng 802.1X cho nhân viên?
2. Một nhân viên nghỉ việc. Với PSK và với 802.1X, bạn thu hồi quyền truy cập thế nào?
3. WPA2 vs WPA3: WPA3 giải quyết điểm yếu nào của WPA2-PSK?
4. "Guest ping được Internet nhưng không mở được web". Nguyên nhân thường gặp nhất?

<details>
<summary>Đáp án</summary>

**1.** Ba khác biệt:

| | WPA2-PSK | WPA2-802.1X (Enterprise) |
|---|---|---|
| Xác thực | **một mật khẩu chung** cho mọi người | **user/pass riêng** từng người *(qua RADIUS)* |
| Thu hồi | đổi PSK → **mọi người** phải nhập lại | xoá **một** user |
| Khoá mã hoá | dẫn xuất từ PSK chung | **riêng** mỗi phiên/người |

Doanh nghiệp dùng 802.1X vì: thu hồi được từng người, truy vết ai kết nối, khoá riêng
mỗi phiên *(lộ một tài khoản không lộ cả mạng)*.

**2.**
- **PSK:** phải **đổi mật khẩu chung** → thông báo cho **toàn bộ** nhân viên còn lại
  nhập lại → phiền, và trong lúc chưa đổi, người nghỉ vẫn vào được.
- **802.1X:** chỉ cần **vô hiệu hoá tài khoản** của người đó trên RADIUS/AD → tức thì,
  không ai khác bị ảnh hưởng. Đây là lý do lớn nhất chọn 802.1X.

**3.** WPA3 khắc phục điểm yếu WPA2-PSK:
- **SAE (Simultaneous Authentication of Equals)** thay 4-way handshake → chống **tấn công
  offline dictionary** *(bắt handshake rồi dò mật khẩu)*.
- **Forward secrecy:** lộ mật khẩu không giải mã được traffic đã bắt trước đó.
- Chống **KRACK** và brute-force tốt hơn.

**4.** Nguyên nhân phổ biến nhất: **ACL chặn DNS**. Guest ping IP được *(ICMP qua)*, nhưng
không phân giải tên → không mở được `google.com`. Thường do quên `permit udp ... eq 53`
hoặc đặt nó **sau** dòng deny nội bộ *(nếu DNS server ở trong dải bị deny)*. Luôn permit
DNS **trước** deny nội bộ.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — RADIUS chết ⭐:** 802.1X **phụ thuộc hoàn toàn** vào RADIUS — WLC chỉ là
"người chuyển tiếp". RADIUS chết → NV không xác thực được → **không vào** `CTY-NhanVien`.
Nhưng khách dùng **PSK** *(xác thực cục bộ trên WLC, không cần server)* → **không bị ảnh
hưởng**. Luồng 802.1X dừng ở bước "authenticator → authentication server". Bài học: 802.1X
mạnh nhưng **cần RADIUS dự phòng** *(nhiều server)* để không mất Wi-Fi khi server chết.

**Lỗi 2 — guest gắn nhầm VLAN ⭐:** Đổi SSID khách sang VLAN 10 → khách nhận IP `10.0.10.x`
*(dải nhân viên)*. ACL cô lập đặt trên **VLAN 90** → giờ **vô dụng** *(khách không còn ở
VLAN 90)*. Khách **vào thẳng mạng nội bộ** như nhân viên. Đây cho thấy: **gắn đúng VLAN
là nền tảng** — ACL chỉ bảo vệ nếu traffic thực sự đi qua đúng SVI.

**Lỗi 3 — thiếu permit DNS:** Khách ping `8.8.8.8` *(IP)* OK, nhưng mở `google.com` fail
vì truy vấn DNS tới `10.0.99.53` *(nội bộ)* bị dòng `deny ... 10.0.0.0/16` chặn. Phải
permit DNS **trước** dòng deny. Triệu chứng "ping IP được, mở web không" = kinh điển của
DNS bị chặn.

### Bảng tổng kết

| Thành phần | Vai trò | Bẫy |
|---|---|---|
| WPA2-PSK | Khách, xác thực cục bộ | đổi PSK = mọi người nhập lại |
| WPA2-802.1X | Nhân viên, qua RADIUS | RADIUS chết = mất Wi-Fi NV |
| VLAN mapping | Nền tảng cô lập | gắn sai VLAN = ACL vô dụng |
| ACL guest | Cô lập nội bộ | permit DNS trước deny |

</details>

---

## 📝 Ghi chú & bài học rút ra

- PSK vs 802.1X — khi nào dùng cái nào? ___
- Lỗi 2 (sai VLAN) — vì sao ACL thành vô dụng? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
