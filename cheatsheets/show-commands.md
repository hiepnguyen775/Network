# 🔧 Show Commands Cheat Sheet (Cisco IOS)

> Nguyên tắc: **mỗi lệnh phải trả lời một giả thuyết.**
> Gõ lệnh mà không biết mình đang kiểm chứng điều gì = đang đoán mò.
>
> Mọi output trong file này là **output điển hình — tự verify trên lab của bạn**.

---

## 1. Bộ lệnh "mở màn" — gõ 3 lệnh này trước mọi thứ khác

| Lệnh | Trả lời câu hỏi |
|---|---|
| `show ip interface brief` | Interface nào up? IP đã đúng chưa? |
| `show running-config` | Cấu hình hiện tại thật sự là gì (không phải cái tôi nghĩ đã gõ) |
| `show cdp neighbors` / `show lldp neighbors` | Tôi đang nối với thiết bị nào, qua port nào |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip interface brief
Interface          IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0 192.168.1.1     YES manual up                    up
GigabitEthernet0/1 unassigned      YES unset  administratively down down
```

**Đọc gì:**

| `Status` / `Protocol` | Nghĩa là | Nghi ngờ |
|---|---|---|
| `up` / `up` | Bình thường | — |
| `administratively down` | Có người gõ `shutdown` | Thiếu `no shutdown` |
| `down` / `down` | Lỗi vật lý | Cáp, đầu kia down, sai loại cáp |
| `up` / `down` | L1 ok, L2 hỏng | Lệch encapsulation, thiếu clock rate (serial), keepalive |

---

## 2. Layer 2 — Switching

| Lệnh | Dùng khi | Nhìn gì |
|---|---|---|
| `show vlan brief` | Kiểm tra VLAN tồn tại chưa, port nào thuộc VLAN nào | Port có nằm đúng VLAN không |
| `show interfaces trunk` | Trunk không lên / VLAN không qua được | Mode, native VLAN, allowed VLAN |
| `show interfaces status` | Nhìn nhanh toàn bộ port | `connected` / `notconnect` / `err-disabled` |
| `show mac address-table` | Switch có học được MAC không | MAC xuất hiện ở đúng port? Nhảy port liên tục = loop |
| `show spanning-tree` | Nghi loop, port bị block | Ai là root, port role/state |
| `show spanning-tree vlan 10` | STP của riêng một VLAN | Root ID, cost, port role |
| `show etherchannel summary` | EtherChannel không bundle | Flag `(P)` = in port-channel; `(s)` hoặc `(D)` = có vấn đề |
| `show port-security interface fa0/1` | Port bị err-disabled | Violation count, mode |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces trunk
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1
Port        Vlans allowed on trunk
Gi0/1       1-4094
```

> ⚠️ `Native vlan` hai đầu phải **giống nhau**. Khác nhau → traffic rò giữa VLAN,
> và IOS sẽ log `%CDP-4-NATIVE_VLAN_MISMATCH`.

---

## 3. Layer 3 — Routing

| Lệnh | Dùng khi | Nhìn gì |
|---|---|---|
| `show ip route` | Luôn luôn | Route có tồn tại không, đến từ đâu, next-hop là ai |
| `show ip route 8.8.8.8` | Kiểm tra một đích cụ thể | Router thật sự chọn route nào |
| `show ip protocols` | Routing protocol chạy không đúng | Network statement, passive-interface, AD |
| `show ip ospf neighbor` | OSPF không hội tụ | State phải là `FULL` hoặc `2WAY` (với DROTHER) |
| `show ip ospf interface` | Neighbor không lên | Area, hello/dead timer, network type, cost |
| `show ip ospf` | Thông tin tổng | Router ID, số area, SPF count |
| `show ip arp` | Nghi ARP | IP ↔ MAC có đúng không |

### Đọc `show ip route` — ký tự đầu dòng

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route
Gateway of last resort is 203.0.113.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 203.0.113.1
      10.0.0.0/8 is variably subnetted, 3 subnets, 2 masks
C        10.1.1.0/24 is directly connected, GigabitEthernet0/0
L        10.1.1.1/32 is directly connected, GigabitEthernet0/0
O        10.2.2.0/24 [110/2] via 10.1.1.2, 00:05:21, GigabitEthernet0/0
```

| Ký tự | Nguồn route |
|:---:|---|
| `C` | Connected — interface up và có IP |
| `L` | Local — chính IP của interface (`/32`) |
| `S` | Static |
| `S*` | Static default route (`0.0.0.0/0`) |
| `O` | OSPF |
| `O IA` | OSPF inter-area |
| `O E1` / `O E2` | OSPF external (redistribute vào) |
| `D` | EIGRP |
| `B` | BGP |
| `R` | RIP |

**`[110/2]`** = `[Administrative Distance / Metric]`

### Administrative Distance — bảng phải thuộc

| Nguồn | AD |
|---|:---:|
| Connected | **0** |
| Static | **1** |
| eBGP | 20 |
| EIGRP (internal) | 90 |
| **OSPF** | **110** |
| RIP | 120 |
| EIGRP (external) | 170 |
| iBGP | 200 |
| Unknown / không dùng | 255 |

> **Thứ tự quyết định route:** `Longest prefix match` → `AD thấp nhất` → `Metric thấp nhất`.
> Longest prefix xét **trước** AD — đây là chỗ hay nhầm nhất.

---

## 4. Services

| Lệnh | Dùng khi |
|---|---|
| `show ip dhcp binding` | Kiểm tra DHCP đã cấp IP cho ai |
| `show ip dhcp pool` | Pool còn IP không, đã cấp bao nhiêu |
| `show ip nat translations` | NAT có dịch không, dịch thành gì |
| `show ip nat statistics` | Số lần hit, interface inside/outside |
| `show access-lists` | ACL có match không (số hit cạnh mỗi dòng) |
| `show ntp status` | Đồng hồ đã sync chưa |
| `show logging` | Xem syslog buffer trên thiết bị |
| `show clock` | Giờ thiết bị — ảnh hưởng tới log và chứng chỉ |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
tcp 203.0.113.5:1024   192.168.1.10:49152 8.8.8.8:443        8.8.8.8:443
```

---

## 5. Lệnh chẩn đoán chủ động

| Lệnh | Dùng khi |
|---|---|
| `ping 8.8.8.8` | Kiểm tra thông |
| `ping 8.8.8.8 source g0/1` | Kiểm tra từ một source IP cụ thể (rất hay dùng khi debug NAT/ACL) |
| `ping 8.8.8.8 size 1500 df-bit` | Kiểm tra MTU / phân mảnh |
| `traceroute 8.8.8.8` | Xem gói đi tới đâu thì chết |
| `debug ip ospf adj` | OSPF không lên neighbor ⚠️ |
| `undebug all` | **Luôn nhớ tắt debug** |

> ⚠️ `debug` tiêu tốn CPU thiết bị. Trên production, dùng có chủ đích và tắt ngay.
> Luôn `terminal monitor` nếu đang vào bằng SSH, nếu không sẽ không thấy output.

---

## 6. Lọc output — tiết kiệm rất nhiều thời gian

```cisco
show running-config | section ospf        ! chỉ phần OSPF
show running-config | include ip route    ! chỉ dòng chứa "ip route"
show ip route | exclude 0.0.0.0           ! bỏ dòng chứa chuỗi
show ip interface brief | include up      ! chỉ interface đang up
show running-config | begin interface     ! từ "interface" trở xuống
```

---

## 7. Lưu & khôi phục cấu hình

```cisco
copy running-config startup-config    ! hoặc viết tắt: wr
show startup-config
reload                                 ! khởi động lại
```

> 🏭 **Production:** `wr` xong mới rời máy. Rất nhiều sự cố "tự nhiên mất cấu hình"
> thực ra là mất điện sau khi ai đó quên lưu.

---

## 8. Khác biệt platform

| Việc | IOS / IOS-XE | NX-OS |
|---|---|---|
| Xem interface | `show ip interface brief` | `show ip interface brief` |
| Bật feature | *(mặc định có)* | `feature ospf`, `feature interface-vlan`… |
| Xem VLAN | `show vlan brief` | `show vlan brief` |
| Lưu config | `copy run start` | `copy run start` |
| Default interface state | `shutdown` (switch port: no shut) | `shutdown` trên L3, tuỳ platform |

> NX-OS **bắt buộc bật feature** trước khi dùng — gõ lệnh OSPF mà chưa `feature ospf`
> thì IOS báo lỗi syntax, rất dễ tưởng là gõ sai.
