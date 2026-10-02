# LESSON 12 — Cisco IOS CLI

> 📌 Lesson "học nghề". Không có khái niệm mới nào khó — nhưng đây là lesson quyết định
> bạn gõ lệnh **thành phản xạ** hay vẫn phải tra tài liệu sau 6 tháng.

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~3 giờ (và gõ lại nhiều lần sau đó) |
| **Prerequisite** | [Lesson 11](./lesson-11-kien-truc-switch.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Di chuyển giữa các config mode mà không nghĩ
- [ ] Phân biệt **running-config** và **startup-config** — và hậu quả khi nhầm
- [ ] Cấu hình cơ bản một switch mới: hostname, IP quản trị, SSH, banner
- [ ] Dùng được `?`, Tab, phím tắt lịch sử — gõ nhanh gấp 3 lần
- [ ] Khôi phục được thiết bị khi quên mật khẩu

## 2. Prerequisite

- Biết SVI là gì, routed port là gì *(Lesson 11)*
- Biết SSH port 22, telnet port 23 *(Lesson 06)*

---

## 3. Concept

### Các chế độ CLI

```text
# sơ đồ chế độ CLI — dạng điển hình trên IOS
Switch>                         User EXEC        — xem được rất ít
   │ enable
Switch#                         Privileged EXEC  — xem được mọi thứ, chạy show/debug
   │ configure terminal
Switch(config)#                 Global config    — sửa cấu hình toàn cục
   │ interface gi1/0/1
Switch(config-if)#              Interface config
   │ exit
Switch(config)#
   │ line vty 0 15
Switch(config-line)#            Line config
   │ end  (hoặc Ctrl+Z)
Switch#
```

| Phím tắt | Tác dụng |
|---|---|
| `exit` | Lùi **một** cấp |
| `end` hoặc **`Ctrl+Z`** | Nhảy thẳng về Privileged EXEC |
| `do <lệnh>` | Chạy lệnh EXEC **ngay trong config mode** — vd `do show ip int brief` |

> 🔧 `do` là phím tắt tiết kiệm thời gian nhất của IOS. Không cần `end` rồi `conf t` lại.

### running-config vs startup-config

| | `running-config` | `startup-config` |
|---|---|---|
| Nằm ở | **RAM** | **NVRAM** |
| Mất khi mất điện? | **Có** ❌ | Không ✅ |
| Lệnh bạn vừa gõ nằm ở đâu? | Đây | Chưa |
| Xem bằng | `show running-config` | `show startup-config` |

```cisco
Switch# copy running-config startup-config      ! lưu lại
Switch# write memory                            ! viết tắt cũ, vẫn dùng được
Switch# wr                                      ! viết tắt của viết tắt
```

> ⚠️ **Rất nhiều sự cố "tự nhiên mất cấu hình" thực ra là quên `wr` rồi mất điện.**
> Thói quen: gõ xong, verify xong, **`wr` rồi mới rời máy**.

### Bốn công cụ gõ nhanh

| Công cụ | Cách dùng | Ví dụ |
|---|---|---|
| **`?`** | Xem lệnh/tham số khả dụng | `show ?` · `switchport mode ?` |
| **Tab** | Tự hoàn thành | `conf` + Tab → `configure` |
| **Viết tắt** | Gõ đủ ký tự để không nhập nhằng | `conf t` = `configure terminal`<br>`int gi1/0/1` = `interface GigabitEthernet1/0/1`<br>`sh ip int br` = `show ip interface brief` |
| **`\|`** | Lọc output | `show run \| section vlan` |

| Phím | Tác dụng |
|---|---|
| `↑` / `↓` | Lịch sử lệnh |
| `Ctrl+A` / `Ctrl+E` | Về đầu / cuối dòng |
| `Ctrl+C` | Huỷ lệnh đang gõ |
| `Ctrl+Shift+6` | **Ngắt** lệnh đang chạy (ping dài, traceroute) |
| `Ctrl+R` | Vẽ lại dòng đang gõ (khi log chen ngang) |

### Bộ lọc output

```cisco
show running-config | section ospf         ! cả khối cấu hình OSPF
show running-config | include ip route      ! chỉ dòng chứa chuỗi
show ip route | exclude 0.0.0.0             ! bỏ dòng chứa chuỗi
show ip interface brief | include up        ! chỉ interface đang up
show running-config | begin interface       ! từ chỗ này trở xuống
show mac address-table | count 001a         ! đếm số dòng khớp
```

---

## 4. Why? — vì sao CLI vẫn thống trị

> **Đã có giao diện web, vì sao network engineer vẫn dùng CLI?**

| Lý do | Giải thích |
|---|---|
| **Tự động hoá được** | Cấu hình là **text** → copy, diff, lưu vào Git, đẩy bằng Ansible |
| **Lặp lại chính xác** | 50 switch cùng một đoạn config — click chuột 50 lần thì sẽ sai |
| **Nhanh hơn nhiều** | Người quen gõ nhanh gấp nhiều lần click |
| **Luôn có khi mọi thứ hỏng** | Mạng chết, web UI không vào được — **console vẫn vào được** |
| **Chuẩn hoá** | Cú pháp IOS gần như không đổi suốt 20 năm |

> 🔧 Và đây là cầu nối sang Phase 9: **cấu hình là text** chính là tiền đề của
> Network Automation. Ansible/Netmiko về bản chất chỉ là "gõ CLI thay bạn".

---

## 5. How does it work? — cấu hình một switch mới từ số 0

### Bước 1 — Cơ bản

```cisco
Switch> enable
Switch# configure terminal

Switch(config)# hostname SW-ACCESS-T1
SW-ACCESS-T1(config)# no ip domain-lookup           ! tắt treo 30s khi gõ nhầm

! Mật khẩu
SW-ACCESS-T1(config)# enable secret Str0ngP@ss      ! MÃ HOÁ — dùng cái này
SW-ACCESS-T1(config)# service password-encryption   ! mã hoá các mật khẩu còn lại

! Banner cảnh báo (có giá trị pháp lý ở nhiều nơi)
SW-ACCESS-T1(config)# banner motd #
  CANH BAO: He thong rieng tu. Moi truy cap deu duoc ghi log.
#
```

> ⚠️ **`enable secret` chứ không phải `enable password`.**
> `enable password` lưu **plaintext** hoặc mã hoá type 7 (bẻ được trong vài giây).
> `enable secret` dùng hash. Nếu cả hai cùng tồn tại, IOS dùng `secret`.

### Bước 2 — IP quản trị

```cisco
! Trên switch L2: dùng SVI quản trị + default gateway
SW-ACCESS-T1(config)# interface vlan 99
SW-ACCESS-T1(config-if)# description MGMT
SW-ACCESS-T1(config-if)# ip address 10.0.99.11 255.255.255.0
SW-ACCESS-T1(config-if)# no shutdown
SW-ACCESS-T1(config-if)# exit
SW-ACCESS-T1(config)# ip default-gateway 10.0.99.1
```

> ⚠️ `ip default-gateway` **chỉ có tác dụng khi `ip routing` TẮT** (switch L2 thuần).
> Trên L3 switch đã bật routing, phải dùng `ip route 0.0.0.0 0.0.0.0 <next-hop>`.

### Bước 3 — SSH (và tắt telnet)

```cisco
SW-ACCESS-T1(config)# ip domain-name cty.local      ! BẮT BUỘC trước khi tạo key
SW-ACCESS-T1(config)# crypto key generate rsa modulus 2048
SW-ACCESS-T1(config)# ip ssh version 2

SW-ACCESS-T1(config)# username admin privilege 15 secret Str0ngP@ss

SW-ACCESS-T1(config)# line vty 0 15
SW-ACCESS-T1(config-line)# transport input ssh      ! CHỈ ssh — telnet bị tắt
SW-ACCESS-T1(config-line)# login local              ! xác thực bằng username local
SW-ACCESS-T1(config-line)# exec-timeout 10 0        ! tự thoát sau 10 phút
SW-ACCESS-T1(config-line)# exit

! Console cũng nên có mật khẩu
SW-ACCESS-T1(config)# line console 0
SW-ACCESS-T1(config-line)# login local
SW-ACCESS-T1(config-line)# logging synchronous      ! log không chen ngang dòng đang gõ
SW-ACCESS-T1(config-line)# exec-timeout 15 0
```

> 🔑 Thứ tự bắt buộc để SSH chạy: **hostname** (≠ "Switch") → **ip domain-name** →
> **crypto key generate rsa** → **username** → **transport input ssh** + **login local**.
> Thiếu bất kỳ bước nào là SSH không lên.

### Bước 4 — Interface

```cisco
SW-ACCESS-T1(config)# interface range GigabitEthernet1/0/1 - 24
SW-ACCESS-T1(config-if-range)# description USER-PORTS
SW-ACCESS-T1(config-if-range)# switchport mode access
SW-ACCESS-T1(config-if-range)# switchport access vlan 10
SW-ACCESS-T1(config-if-range)# spanning-tree portfast
SW-ACCESS-T1(config-if-range)# spanning-tree bpduguard enable
SW-ACCESS-T1(config-if-range)# no shutdown

! Tắt các port không dùng — thói quen bảo mật cơ bản
SW-ACCESS-T1(config)# interface range GigabitEthernet1/0/25 - 44
SW-ACCESS-T1(config-if-range)# description UNUSED
SW-ACCESS-T1(config-if-range)# switchport access vlan 999       ! VLAN "hố đen"
SW-ACCESS-T1(config-if-range)# shutdown
```

### Bước 5 — Lưu

```cisco
SW-ACCESS-T1# copy running-config startup-config
```

---

## 6. Packet Flow — không áp dụng

Lesson này về công cụ, không về đường đi gói tin.

Thay vào đó, một thứ đáng nhớ: **traffic quản trị (SSH) đi vào CPU switch**,
khác với traffic người dùng (đi qua ASIC). Vì vậy SSH chậm khi CPU switch cao —
và đó cũng là dấu hiệu chẩn đoán.

---

## 7. Real-world Example

🏭 **Quên mật khẩu enable — password recovery**

Xảy ra thường xuyên hơn bạn nghĩ (thiết bị cũ, người cũ nghỉ việc).
Quy trình trên Catalyst switch:

```text
1. Rút điện switch
2. Giữ nút MODE, cắm điện lại, giữ tới khi đèn SYST nháy
3. Vào chế độ switch:
     switch: flash_init
     switch: rename flash:config.text flash:config.old
     switch: boot
4. Switch khởi động KHÔNG có cấu hình → vào được enable
5. Khôi phục: copy flash:config.old running-config
6. Đổi mật khẩu, rồi: copy running-config startup-config
```

> ⚠️ Lưu ý nghề: quy trình này **yêu cầu truy cập vật lý**. Đó cũng là lý do
> tủ mạng phải khoá — ai cầm được thiết bị là chiếm được nó.

🏭 **Backup cấu hình — việc 5 phút tránh được thảm hoạ**

```cisco
! Backup ra TFTP server
SW1# copy running-config tftp://10.0.50.10/SW-ACCESS-T1-20261002.cfg

! Khôi phục
SW1# copy tftp://10.0.50.10/SW-ACCESS-T1-20261002.cfg running-config
```

> 🔧 Trong môi trường thật, nên tự động hoá việc này — và đó chính là bài học đầu tiên
> của repo [`Network-Automation`](https://github.com/hiepnguyen775/Network-Automation).

🏭 **`logging synchronous` — dòng config đáng giá nhất**

Không có nó, log của switch chen ngang giữa lúc bạn đang gõ:

```text
# output điển hình — tự verify trên lab của bạn
SW1(config)# interface gi1/0%LINK-3-UPDOWN: Interface Gi1/0/5, changed state to up
/1
```

Bạn không biết mình đã gõ tới đâu. Thêm `logging synchronous` vào `line console 0`
và `line vty 0 15` — IOS sẽ in lại dòng đang gõ sau mỗi log.

---

## 8. Cisco CLI — bảng tra nhanh

### Cấu hình

| Việc | Lệnh |
|---|---|
| Vào config | `configure terminal` (`conf t`) |
| Đặt tên | `hostname <ten>` |
| Mật khẩu enable | `enable secret <pass>` |
| Mã hoá mật khẩu còn lại | `service password-encryption` |
| Tắt tra DNS khi gõ nhầm | `no ip domain-lookup` |
| Tạo user | `username <ten> privilege 15 secret <pass>` |
| Tạo key SSH | `ip domain-name X` → `crypto key generate rsa modulus 2048` |
| Chỉ cho SSH | `line vty 0 15` → `transport input ssh` + `login local` |
| Nhiều interface một lúc | `interface range gi1/0/1 - 24` |
| Mô tả interface | `description <text>` |
| Bật interface | `no shutdown` |

### Kiểm tra

| Việc | Lệnh |
|---|---|
| Cấu hình đang chạy | `show running-config` |
| Cấu hình đã lưu | `show startup-config` |
| Phiên bản, uptime, model | `show version` |
| Interface tổng quan | `show ip interface brief` |
| Trạng thái port switch | `show interfaces status` |
| Láng giềng | `show cdp neighbors [detail]` |
| Ai đang đăng nhập | `show users` |
| Log trên thiết bị | `show logging` |
| Tài nguyên | `show processes cpu sorted` · `show memory statistics` |

### Khôi phục / dọn dẹp

```cisco
SW1# copy running-config startup-config      ! lưu
SW1# write erase                             ! XOÁ startup-config
SW1# delete flash:vlan.dat                   ! xoá VLAN database
SW1# reload                                  ! khởi động lại
```

> ⚠️ Reset switch về mặc định cần **cả hai**: `write erase` **và** `delete flash:vlan.dat`.
> VLAN **không** nằm trong `startup-config` mà nằm trong `vlan.dat` —
> đây là bẫy kinh điển khi dựng lại lab: xoá config rồi mà VLAN cũ vẫn còn.

### Khác biệt platform

| Việc | IOS / IOS-XE | NX-OS |
|---|---|---|
| Lưu cấu hình | `copy run start` | `copy run start` |
| Tạo user | `username X secret Y` | `username X password Y role network-admin` |
| Bật tính năng | *(có sẵn)* | `feature ssh`, `feature interface-vlan`… |
| Xoá dòng config | `no <lệnh>` | `no <lệnh>` |
| Tên interface | `GigabitEthernet1/0/1` | `Ethernet1/1` |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces status
Port      Name               Status       Vlan      Duplex  Speed Type
Gi1/0/1   USER-PORTS         connected    10        a-full  a-100 10/100/1000BaseTX
Gi1/0/2   USER-PORTS         notconnect   10          auto   auto 10/100/1000BaseTX
Gi1/0/25  UNUSED             disabled     999         auto   auto 10/100/1000BaseTX
Gi1/0/48  UPLINK-TO-DIST     connected    trunk     a-full  a-1000 10/100/1000BaseTX
```

| `Status` | Nghĩa |
|---|---|
| `connected` | Có thiết bị, link up |
| `notconnect` | Không có gì cắm, hoặc cáp hỏng |
| `disabled` | Đã `shutdown` bằng tay |
| `err-disabled` | **Switch tự tắt** — port security, BPDU guard, loop detect |

| Cột | Đọc gì |
|---|---|
| `Vlan` | Số = access port VLAN đó · `trunk` = trunk port |
| `Duplex`/`Speed` | `a-` = tự thương lượng. **`half` trên link 1G là bất thường** → nghi cáp hoặc ép cứng lệch |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show version
Cisco IOS Software, C2960X Software, Version 15.2(7)E3
SW1 uptime is 2 weeks, 3 days, 4 hours, 12 minutes
System returned to ROM by power-on
Configuration register is 0xF
```

> `System returned to ROM by power-on` = **vừa mất điện**. Đây là nơi kiểm chứng
> giả thuyết "thiết bị bị reboot ngoài ý muốn".

```cisco
! Kiểm tra SSH đã sẵn sàng chưa
SW1# show ip ssh
SW1# show crypto key mypubkey rsa
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| `crypto key generate rsa` báo lỗi | Chưa đặt `ip domain-name`, hoặc hostname vẫn là "Switch" | `show run \| include hostname\|domain` | Đặt cả hai rồi tạo key lại |
| SSH được nhưng bị từ chối đăng nhập | Thiếu `login local` hoặc chưa có `username` | `show run \| section line vty` | Thêm cả hai |
| Vẫn telnet được dù đã bật SSH | Thiếu `transport input ssh` | `show run \| section line vty` | Thêm dòng đó |
| Reload xong mất hết cấu hình | **Quên `wr`** | `show startup-config` trống | `copy run start` |
| Xoá config rồi mà VLAN cũ vẫn còn | VLAN nằm ở `vlan.dat` | `show vlan brief` | `delete flash:vlan.dat` rồi reload |
| Gõ nhầm lệnh → treo 30 giây | Router đang tra DNS | — | `no ip domain-lookup` |
| Log chen ngang khi đang gõ | Thiếu `logging synchronous` | — | Thêm vào `line console`/`vty` |
| Port `err-disabled` | Port security / BPDU guard kích hoạt | `show interfaces status err-disabled` | Xử lý nguyên nhân rồi `shutdown`/`no shutdown` |
| SSH chậm, gõ lag | CPU switch cao | `show processes cpu sorted` | Nghi loop/storm |

---

## 11. LAB

🧪 **LAB 10 — Cisco IOS CLI căn bản** *(tạo từ [`templates/LAB_TEMPLATE.md`](../templates/LAB_TEMPLATE.md), lưu thành `labs/lab10-cisco-ios-cli.md`)*

Yêu cầu tối thiểu: cấu hình switch mới từ số 0 (hostname, SSH, SVI quản trị, port range,
tắt port không dùng), backup config ra TFTP, rồi **BREAK**: (1) reload khi chưa `wr`;
(2) tạo RSA key khi chưa đặt `ip domain-name`; (3) `write erase` rồi kiểm tra VLAN còn không.

## 12. Challenge

1. Bạn gõ `enable password Cisco123` và `enable secret Cisco456`. Mật khẩu nào có tác dụng?
2. Switch mới nguyên hộp, bạn muốn SSH vào. Liệt kê **đủ** các bước theo đúng thứ tự.
3. Bạn `write erase` rồi `reload`. Khởi động lại thấy VLAN 10, 20 vẫn còn. Vì sao? Sửa thế nào?
4. Vì sao nên tắt (`shutdown`) các port không dùng và cho vào một VLAN riêng?

<details>
<summary>Đáp án</summary>

**1.** **`enable secret`** có tác dụng. Khi cả hai cùng tồn tại, IOS luôn ưu tiên `secret`
vì nó dùng hash (an toàn), còn `password` chỉ plaintext hoặc type-7 (bẻ được ngay).
Thực tế: **chỉ nên dùng `enable secret`**, xoá hẳn `enable password`.

**2.** Đủ 6 bước, đúng thứ tự:

```cisco
1. hostname SW1                              ! không được để tên mặc định "Switch"
2. ip domain-name cty.local                  ! bắt buộc, key sinh từ hostname.domain
3. crypto key generate rsa modulus 2048      ! tạo cặp khoá
4. username admin privilege 15 secret <pass> ! tài khoản để đăng nhập
5. line vty 0 15
     transport input ssh                     ! chỉ cho SSH
     login local                             ! xác thực bằng user local
6. (SVI quản trị + ip default-gateway để tới được từ xa)
```

Thiếu bước 1 hoặc 2 → lệnh ở bước 3 báo lỗi. Thiếu bước 4 hoặc `login local` →
SSH kết nối được nhưng không đăng nhập được.

**3.** Vì **VLAN không nằm trong `startup-config`** — chúng nằm trong file riêng
`flash:vlan.dat`. `write erase` chỉ xoá NVRAM. Sửa:

```cisco
SW1# write erase
SW1# delete flash:vlan.dat
SW1# reload
```

**4.** Hai lý do:

| Lý do | Giải thích |
|---|---|
| **Bảo mật** | Port đang up ở VLAN production = ai cắm dây vào cũng có mạng, không cần xác thực |
| **Giảm nhầm lẫn** | Port `disabled` + `description UNUSED` nói rõ cho người sau biết đây là port chưa dùng, không phải port hỏng |

Cho vào VLAN riêng (vd 999, không có SVI, không route đi đâu) là lớp phòng vệ thứ hai:
nếu ai đó lỡ `no shutdown`, port vẫn không nối vào mạng thật.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 4 config mode · running vs startup · `do` làm gì · `Ctrl+Shift+6` | ⬜ |
| **L2** Explain | Giải thích vì sao network engineer vẫn dùng CLI thay vì web UI | ⬜ |
| **L3** Configure | Cấu hình switch mới từ số 0: hostname, SSH, SVI quản trị, port range | ⬜ |
| **L4** Troubleshoot | SSH không lên → nêu 4 nguyên nhân theo thứ tự kiểm tra | ⬜ |
| **L5** Design | Viết một "config chuẩn" của công ty, áp dụng cho mọi switch access mới | ⬜ |

## 14. Summary

**Key concepts**

- 4 mode: `User EXEC` → `Privileged EXEC` → `Global config` → `Interface/Line config`
- ⭐ **`running-config` ở RAM, `startup-config` ở NVRAM** — gõ xong phải `wr`
- `do <lệnh>` chạy lệnh EXEC ngay trong config mode
- `enable secret` (hash) **chứ không** `enable password` (plaintext)
- SSH cần đủ: hostname → domain-name → RSA key → username → `transport input ssh` + `login local`
- ⭐ **VLAN nằm ở `vlan.dat`, không nằm trong `startup-config`**
- `logging synchronous` để log không chen ngang dòng đang gõ
- Port không dùng: `shutdown` + VLAN riêng + `description UNUSED`

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `copy run start` / `wr` | **Luôn gõ trước khi rời máy** |
| `do show ...` | Xem nhanh khi đang trong config mode |
| `interface range gi1/0/1 - 24` | Sửa nhiều port một lúc |
| `show interfaces status` | Nhìn nhanh toàn bộ port |
| `show run \| section <từ khoá>` | Lọc cấu hình |
| `no ip domain-lookup` | Tắt treo 30s khi gõ nhầm |
| `Ctrl+Shift+6` | Ngắt lệnh đang chạy |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `wr` | Mất cấu hình sau reload |
| Dùng `enable password` | Mật khẩu bẻ được trong vài giây |
| Quên `ip domain-name` trước khi tạo RSA key | Lệnh báo lỗi |
| Quên `transport input ssh` | Telnet vẫn mở, tưởng đã an toàn |
| `write erase` mà không xoá `vlan.dat` | VLAN cũ vẫn còn sau reload |
| Quên `no ip domain-lookup` | Mỗi lần gõ nhầm treo 30 giây |
| Để port không dùng ở trạng thái up, VLAN production | Lỗ hổng bảo mật vật lý |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 10 đầy đủ, kể cả mục BREAK.
2. Viết ra một "**config chuẩn**" của riêng bạn — đoạn cấu hình áp dụng cho **mọi**
   switch access mới. Lưu vào `01-switching/config-chuan-access-switch.txt`.
3. Luyện gõ: cấu hình một switch từ số 0 **không nhìn tài liệu**, bấm giờ.
   Mục tiêu: dưới 10 phút.

```markdown
- [YYYY-MM-DD] Lesson 12 — Cisco IOS CLI: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Các mode, running vs startup, cấu hình SSH đủ bước, `interface range` |
| 🔧 **Engineer** | Config chuẩn áp cho mọi switch; `logging synchronous`; backup config định kỳ |
| 🏭 **Production** | Quên `wr` = mất config; password recovery cần truy cập vật lý → khoá tủ mạng; cấu hình là text → tiền đề của automation |

### 🔗 Liên kết

- ⬅️ [Lesson 11 — Kiến trúc switch](./lesson-11-kien-truc-switch.md)
- ➡️ [Lesson 13 — VLAN & Trunk](./lesson-13-vlan-va-trunk.md)
- 🧪 LAB 10 — Cisco IOS CLI căn bản *(xem mục 11)*
- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md)
