# LAB 10 — Cisco IOS CLI căn bản

| | |
|---|---|
| **Phase** | 1 |
| **Lesson liên quan** | [Lesson 12 — Cisco IOS CLI](../01-switching/lesson-12-cisco-ios-cli.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~1.5 giờ |
| **Độ khó** | ⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Di chuyển thành thạo giữa các **chế độ** IOS *(user → privileged → global → interface)*
- [ ] Đặt hostname, banner, mật khẩu *(enable secret, console, vty)*
- [ ] Cấu hình **SSH** và vô hiệu hoá Telnet
- [ ] Phân biệt `running-config` vs `startup-config` và **backup** ra TFTP
- [ ] Hiểu vì sao `copy run start` là thói quen sống còn

## 2. Prerequisite

- [Lesson 12](../01-switching/lesson-12-cisco-ios-cli.md) — chế độ IOS, SSH, lưu config
- Không cần kiến thức trước — đây là lab nền tảng của Phase 1

---

## 3. Topology

```text
   PC-ADMIN ───── SW1 ───── R1 ───── TFTP-SERVER
   10.0.0.10   (quản trị)          10.0.0.200
   (SSH client)
```

| Thiết bị | Vai trò |
|---|---|
| SW1 | Switch thực hành CLI |
| R1 | Router thực hành CLI |
| PC-ADMIN | Máy kỹ sư, SSH vào thiết bị |
| TFTP-SERVER | Server-PT bật TFTP để nhận backup |

## 4. IP Addressing Table

| Device | Interface | IP | Mask |
|---|---|---|---|
| SW1 | Vlan1 | `10.0.0.2` | `/24` |
| R1 | Gi0/0 | `10.0.0.1` | `/24` |
| PC-ADMIN | Fa0 | `10.0.0.10` | `/24` |
| TFTP-SERVER | Fa0 | `10.0.0.200` | `/24` |

---

## 5. Yêu cầu LAB

- [ ] SSH được từ PC-ADMIN vào cả SW1 và R1, Telnet **bị từ chối**
- [ ] `enable secret` mã hoá *(không phải `enable password`)*
- [ ] `service password-encryption` bật
- [ ] Backup `running-config` của R1 lên TFTP server
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Làm quen các chế độ

```cisco
Switch> enable                         ! user → privileged
Switch# configure terminal             ! → global config
Switch(config)# hostname SW1           ! đổi tên
SW1(config)# interface vlan 1          ! → interface config
SW1(config-if)# exit                   ! lùi một cấp
SW1(config)# end                       ! về thẳng privileged
SW1# show running-config               ! xem config đang chạy (RAM)
```

> 🔑 Nhận biết chế độ qua **dấu nhắc**:
> `>` = user · `#` = privileged · `(config)#` = global · `(config-if)#` = interface.

### Bước 2 — Hostname, banner, mật khẩu

```cisco
SW1(config)# enable secret Enable@123         ! mã hoá MD5 — DÙNG CÁI NÀY
SW1(config)# banner motd #Canh bao: chi nguoi duoc phep#

SW1(config)# line console 0
SW1(config-line)# password Con@123
SW1(config-line)# login
SW1(config-line)# logging synchronous
SW1(config-line)# exec-timeout 10 0
SW1(config-line)# exit

SW1(config)# service password-encryption      ! mã hoá mọi password type-7
```

> ⚠️ **`enable secret` vs `enable password`:** `secret` băm không thể đảo ngược;
> `password` chỉ mã hoá yếu *(type-7, crack trong vài giây)*. Luôn dùng `secret`.

### Bước 3 — Cấu hình SSH ⭐

```cisco
SW1(config)# ip domain-name cty.local          ! BẮT BUỘC để sinh key
SW1(config)# username admin privilege 15 secret Admin@123
SW1(config)# crypto key generate rsa modulus 1024
SW1(config)# ip ssh version 2

SW1(config)# line vty 0 15
SW1(config-line)# transport input ssh          ! CHỈ ssh, cấm telnet
SW1(config-line)# login local                  ! xác thực bằng username local
SW1(config-line)# exec-timeout 5 0
```

> 🔑 Ba thứ **bắt buộc** để SSH chạy: `hostname` *(khác "Switch")* + `ip domain-name`
> + `crypto key generate rsa`. Thiếu một trong ba → key không sinh được.

Kiểm chứng từ PC-ADMIN *(Desktop → Command Prompt)*:

```cisco
PC> ssh -l admin 10.0.0.2         ← phải vào được
PC> telnet 10.0.0.2               ← phải BỊ TỪ CHỐI
```

### Bước 4 — running vs startup, backup ⭐

```cisco
SW1# show running-config          ! config đang chạy — trong RAM, mất khi reload
SW1# show startup-config          ! config lúc khởi động — trong NVRAM, bền
SW1# copy running-config startup-config    ! LƯU LẠI  (viết tắt: wr)
```

> 🔴 **DỰ ĐOÁN:** bạn đổi hostname rồi **reload mà KHÔNG `wr`**. Sau khi bật lại,
> hostname là gì?

Backup lên TFTP *(trên R1)*:

```cisco
R1# copy running-config tftp:
Address or name of remote host []? 10.0.0.200
Destination filename [r1-confg]? r1-backup.cfg
```

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip ssh
SSH Enabled - version 2.0
Authentication timeout: 120 secs; Authentication retries: 3
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show running-config | include transport input
 transport input ssh
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show running-config | include enable
enable secret 5 $1$mERr$9cTjUIEqN6LbQ0yR5l.Hd/
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | SSH từ PC-ADMIN vào SW1 | ✅ | |
| 2 | Telnet vào SW1 | ❌ Bị từ chối | |
| 3 | `show ip ssh` | version 2.0 | |
| 4 | enable hiển thị dạng băm | `secret 5 $...` | |
| 5 | password console sau `service password-encryption` | dạng `7 ...` | |
| 6 | File backup xuất hiện trên TFTP server | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — SSH không sinh được key ⭐

```cisco
! Xoá domain-name rồi thử sinh key
SW1(config)# no ip domain-name cty.local
SW1(config)# crypto key generate rsa modulus 1024
```

| | |
|---|---|
| IOS báo lỗi gì? | |
| Ba điều kiện bắt buộc để sinh RSA key là gì? | |
| Nếu hostname vẫn là "Switch" thì sao? | |

### Lỗi 2 — Quên `wr` rồi reload

```cisco
SW1(config)# hostname SW1-TEST
SW1(config)# exit
SW1# reload          ! KHÔNG gõ wr
```

| | |
|---|---|
| Sau reload, hostname là gì? | |
| Vì sao thay đổi "biến mất"? | |
| running-config nằm ở đâu, startup-config nằm ở đâu? | |

### Lỗi 3 — `login` trên vty nhưng không có nguồn xác thực

```cisco
SW1(config)# line vty 0 15
SW1(config-line)# login              ! yêu cầu password nhưng KHÔNG đặt password
SW1(config-line)# no login local
```

| | |
|---|---|
| SSH/Telnet vào: thông báo gì? *(gợi ý: "password required, but none set")* | |
| Khác gì giữa `login` và `login local`? | |
| Sửa thế nào? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Liệt kê **thứ tự** di chuyển từ `SW1(config-if)#` về `SW1#` bằng ít lệnh nhất.
2. Bạn muốn mọi người thấy `running-config` nhưng **không** thấy password rõ.
   Lệnh nào? Nó có bảo vệ được `enable secret` không?
3. Sau khi `erase startup-config` rồi `reload`, thiết bị hỏi gì? Config nào còn lại?
4. Phân biệt `copy run start`, `copy run tftp`, `copy start run`. Mỗi lệnh dùng khi nào?

<details>
<summary>Đáp án</summary>

**1.** `end` *(một lệnh, nhảy thẳng về privileged từ bất kỳ chế độ con nào)*.
So với `exit` phải gõ nhiều lần để lùi từng cấp. `Ctrl+Z` tương đương `end`.

**2.** `service password-encryption` — mã hoá mọi password **type-7** *(console, vty,
`enable password`)* trong config.

**Không** bảo vệ thêm cho `enable secret`: `secret` vốn đã băm **type-5 (MD5)** hoặc
mạnh hơn, không bị ảnh hưởng bởi lệnh này. Lưu ý type-7 **crack được dễ dàng** —
nó chỉ chống nhìn-qua-vai, không chống kẻ có file config. Mật khẩu thật sự an toàn
phải là `secret`.

**3.** Thiết bị khởi động không có startup-config → hỏi **"Would you like to enter
the initial configuration dialog? [yes/no]"** *(setup wizard)*.

Config còn lại: **không có gì** trong NVRAM. running-config là mặc định nhà máy.
Nếu trước đó chưa `wr`, mọi thứ mất sạch.

**4.**

| Lệnh | Hướng | Dùng khi |
|---|---|---|
| `copy run start` | RAM → NVRAM | **Lưu** thay đổi để sống sót qua reload *(dùng thường xuyên nhất)* |
| `copy run tftp` | RAM → server | **Backup** config ra ngoài |
| `copy start run` | NVRAM → RAM | Nạp lại config đã lưu **mà không reload** — lưu ý nó **merge** chứ không ghi đè |

> ⚠️ `copy start run` **merge** vào running hiện tại *(không xoá cái đang có)*.
> Để nạp "sạch" phải reload. Đây là bẫy hay gặp.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — không sinh được key ⭐:**

```text
SW1(config)# crypto key generate rsa
% Please define a domain-name first.
```

RSA key dùng **FQDN** *(hostname.domain-name)* làm định danh. Thiếu `ip domain-name`
→ không có FQDN → từ chối sinh. Ba điều kiện:
1. `hostname` khác mặc định "Switch"/"Router"
2. `ip domain-name <tên>`
3. `crypto key generate rsa` với modulus ≥ 768 *(nên ≥ 1024 cho SSHv2)*

Nếu hostname vẫn là "Switch", một số IOS vẫn sinh được *(dùng "Switch" làm host)*
nhưng khuyến nghị đổi trước.

**Lỗi 2 — quên `wr`:**

| Quan sát | Giải thích |
|---|---|
| Sau reload hostname quay về "SW1" *(giá trị đã `wr` trước đó)* | Thiết bị nạp **startup-config** từ NVRAM lúc boot |
| Thay đổi "SW1-TEST" biến mất | Nó chỉ nằm trong **running-config (RAM)** — RAM mất khi tắt điện |

```text
running-config  → RAM     → mất khi reload
startup-config  → NVRAM   → bền, nạp lúc boot
copy run start  → chép RAM sang NVRAM
```

👉 Đây là lý do thói quen `wr` sau mỗi thay đổi quan trọng là **sống còn**.

**Lỗi 3 — `login` không password:**

```text
% Password required, but none set
[Connection closed]
```

| Lệnh | Nghĩa |
|---|---|
| `login` | Xác thực bằng **password đặt trên line** *(`password ...`)* — thiếu password = không ai vào được |
| `login local` | Xác thực bằng **username/password trong database local** |

Sửa: hoặc đặt `password X` kèm `login`, hoặc dùng `login local` + có `username`.
Với SSH **bắt buộc** `login local` *(SSH cần username)*.

### Bảng tổng kết

| Việc | Lệnh | Ghi nhớ |
|---|---|---|
| Về privileged nhanh | `end` / `Ctrl+Z` | Một phát |
| Lưu config | `copy run start` / `wr` | Sau mọi thay đổi |
| Backup | `copy run tftp:` | Ra ngoài thiết bị |
| Bật SSH | hostname + domain + rsa key + `transport input ssh` + `login local` | Đủ 5 bước |
| Mật khẩu enable | `enable secret` | Không dùng `enable password` |

</details>

---

## 📝 Ghi chú & bài học rút ra

- 5 bước bật SSH tôi tự nhớ: ___
- Lỗi 2 (quên wr) — running vs startup tôi phân biệt được chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
