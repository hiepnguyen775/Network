# LAB 12 — Inter-VLAN Routing: Router-on-a-Stick và SVI

| | |
|---|---|
| **Phase** | 1 |
| **Lesson liên quan** | [Lesson 14 — Inter-VLAN Routing](../01-switching/lesson-14-inter-vlan-routing.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Triển khai **cả hai** cách: Router-on-a-Stick và SVI
- [ ] Chứng minh TTL giảm 1 → bằng chứng đã qua L3
- [ ] Tự chứng minh **nút cổ chai** của RoAS bằng số liệu
- [ ] Tìm được 3 lỗi inter-VLAN kinh điển từ triệu chứng

## 2. Prerequisite

- [LAB 11](./lab11-vlan-va-trunk.md) — đã làm xong
- [Lesson 14](../01-switching/lesson-14-inter-vlan-routing.md)

---

# PHẦN A — Router-on-a-Stick

## 3A. Topology

```text
                   R1 (Router 2911)
                    │ Gi0/0  (TRUNK)
                    │   .10 → 192.168.10.1
                    │   .20 → 192.168.20.1
                    │   .99 → 192.168.99.1 (native)
                    │
                   SW1 Gi0/1
                  ╱        ╲
             Fa0/1          Fa0/3
            VLAN 10        VLAN 20
             PC-A           PC-C
         192.168.10.10  192.168.20.10
```

## 4A. IP Addressing

| Device | Interface | VLAN | IP | Mask | Gateway |
|---|---|:---:|---|---|---|
| R1 | Gi0/0 | — | *(không IP)* | — | — |
| R1 | Gi0/0.10 | 10 | `192.168.10.1` | `/24` | — |
| R1 | Gi0/0.20 | 20 | `192.168.20.1` | `/24` | — |
| R1 | Gi0/0.99 | 99 *(native)* | `192.168.99.1` | `/24` | — |
| PC-A | Fa0 | 10 | `192.168.10.10` | `/24` | `192.168.10.1` |
| PC-C | Fa0 | 20 | `192.168.20.10` | `/24` | `192.168.20.1` |

## 5A. Cấu hình

### SW1

```cisco
hostname SW1
no ip domain-lookup

vlan 10
 name SALES
vlan 20
 name KETOAN
vlan 99
 name NATIVE
exit

interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
exit

interface FastEthernet0/3
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
exit

! Port nối ROUTER phải là TRUNK
interface GigabitEthernet0/1
 description TRUNK-TO-ROUTER
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,99
exit
```

### R1

```cisco
hostname R1
no ip domain-lookup

! Interface VẬT LÝ: không IP, nhưng PHẢI no shutdown
interface GigabitEthernet0/0
 description TRUNK-TO-SW1
 no shutdown
exit

interface GigabitEthernet0/0.10
 description GW-VLAN10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
exit

interface GigabitEthernet0/0.20
 description GW-VLAN20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
exit

interface GigabitEthernet0/0.99
 description GW-VLAN99-NATIVE
 encapsulation dot1Q 99 native
 ip address 192.168.99.1 255.255.255.0
exit

end
copy running-config startup-config
```

> ⚠️ Hai chỗ dễ sai nhất: **quên `no shutdown` Gi0/0**, và **quên từ khoá `native`**
> trên subinterface 99.

## 6A. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip interface brief
Interface                  IP-Address      OK? Method Status    Protocol
GigabitEthernet0/0         unassigned      YES unset  up        up
GigabitEthernet0/0.10      192.168.10.1    YES manual up        up
GigabitEthernet0/0.20      192.168.20.1    YES manual up        up
GigabitEthernet0/0.99      192.168.99.1    YES manual up        up
```

| Kiểm chứng | Lệnh | Kết quả mong đợi |
|---|---|---|
| PC-A → gateway của mình | `ping 192.168.10.1` | ✅ |
| PC-A → gateway VLAN 20 | `ping 192.168.20.1` | ✅ |
| PC-A → PC-C | `ping 192.168.20.10` | ✅ |
| PC-A → PC-C, số hop | `tracert 192.168.20.10` | **1 hop** |

---

# PHẦN B — SVI trên L3 switch

## 3B. Topology

```text
            SW-L3 (Switch 3560)
            ip routing
            Vlan10 → 192.168.10.1
            Vlan20 → 192.168.20.1
              ╱            ╲
          Fa0/1            Fa0/3
         VLAN 10          VLAN 20
          PC-A             PC-C
```

> Xoá router khỏi topology. Thay 2960 bằng **3560** (L3 switch).

## 5B. Cấu hình

```cisco
hostname SW-L3
no ip domain-lookup

ip routing                       ! ⭐ BẮT BUỘC — hay bị quên nhất

vlan 10
 name SALES
vlan 20
 name KETOAN
exit

interface vlan 10
 description GW-VLAN10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
exit

interface vlan 20
 description GW-VLAN20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
exit

interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
exit

interface FastEthernet0/3
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
exit

end
copy running-config startup-config
```

## 6B. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW-L3# show ip route
      192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.10.0/24 is directly connected, Vlan10
L        192.168.10.1/32 is directly connected, Vlan10
C        192.168.20.0/24 is directly connected, Vlan20
L        192.168.20.1/32 is directly connected, Vlan20
```

Cùng bảng kiểm chứng như Phần A. `tracert` vẫn phải thấy **1 hop**.

---

## 7. So sánh hai cách — điền sau khi làm cả hai

| Tiêu chí | Router-on-a-Stick | SVI |
|---|---|---|
| Số thiết bị cần | | |
| Số dòng cấu hình | | |
| `tracert` thấy mấy hop | | |
| Thời gian ping trung bình *(ping 100 gói)* | | |
| Link nào chở traffic inter-VLAN | | |

> 💡 Chạy `ping 192.168.20.10 -n 100` từ PC-A ở cả hai cấu hình, ghi lại **Average** —
> đây là số liệu thật của bạn, không phải lý thuyết.

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Quên `ip routing` *(Phần B)*

```cisco
SW-L3(config)# no ip routing
```

| | |
|---|---|
| Dự đoán | |
| PC-A ping gateway của mình: | |
| PC-A ping gateway VLAN 20: | |
| PC-A ping PC-C: | |
| Lệnh phát hiện | |
| Vì sao ping gateway của mình **vẫn được**? | |

### Lỗi 2 — Quên `no shutdown` interface vật lý *(Phần A)*

```cisco
R1(config)# interface GigabitEthernet0/0
R1(config-if)# shutdown
```

| | |
|---|---|
| Dự đoán | |
| Bao nhiêu subinterface bị ảnh hưởng? | |
| `show ip interface brief` hiện gì | |
| Bài học | |

### Lỗi 3 — Port nối router vẫn là access *(Phần A)*

```cisco
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# switchport mode access
```

| | |
|---|---|
| Dự đoán | |
| VLAN nào còn thông? | |
| Lệnh phát hiện | |
| Vì sao kết quả lại như vậy | |

### Lỗi 4 *(tự chọn)* — Sai VLAN ID trong `encapsulation`

```cisco
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)# encapsulation dot1Q 30      ! VLAN 30 không tồn tại
```

Subinterface vẫn `up/up`. Vì sao VLAN 20 lại đứt?

> Mỗi lỗi tìm ra → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Thêm VLAN 30 (`192.168.30.0/24`) vào cấu hình SVI. Liệt kê **đủ** các bước cần làm.
2. Ở Phần A, đo thử: copy file giữa PC-A và PC-C đi qua link trunk mấy lần?
   Vì sao điều này tạo nút cổ chai?
3. Với cấu hình SVI, PC-A ping được PC-C nhưng **không ra được Internet**
   (giả sử có router biên ở `192.168.99.2`). Thiếu gì? Viết lệnh.
4. Trong Simulation mode, bắt gói ICMP từ PC-A tới PC-C. Ở chặng nào MAC thay đổi?
   IP có thay đổi không? TTL?

<details>
<summary>Đáp án</summary>

**1.** Bốn bước:

```cisco
SW-L3(config)# vlan 30
SW-L3(config-vlan)# name <ten>
SW-L3(config)# interface vlan 30
SW-L3(config-if)# ip address 192.168.30.1 255.255.255.0
SW-L3(config-if)# no shutdown
SW-L3(config)# interface FastEthernet0/5
SW-L3(config-if)# switchport mode access
SW-L3(config-if)# switchport access vlan 30
```

Lưu ý: SVI VLAN 30 sẽ **`down/down`** cho tới khi có **ít nhất một port up** thuộc VLAN 30.

**2.** Gói đi qua link trunk **2 lần**: một lần đi **lên** router (tagged VLAN 10),
một lần đi **xuống** từ router (tagged VLAN 20).

Nút cổ chai: link 1 Gbps thực chất chỉ phục vụ được ~**500 Mbps** traffic inter-VLAN,
vì mỗi luồng tiêu tốn băng thông **hai lần**. Càng nhiều VLAN và càng nhiều traffic
liên-VLAN, link này càng nghẽn. Với SVI, traffic **không rời khỏi switch** — route trong ASIC.

**3.** Thiếu **default route** trên L3 switch:

```cisco
SW-L3(config)# ip route 0.0.0.0 0.0.0.0 192.168.99.2
```

L3 switch biết các subnet `connected` của nó, nhưng không biết gì về thế giới bên ngoài.
*(Và router biên cũng cần route ngược về `192.168.10.0/24`, `192.168.20.0/24`.)*

**4.**

| Chặng | Src/Dst MAC | Src/Dst IP | TTL |
|---|---|---|:---:|
| PC-A → SW/R | `MAC-A` → **`MAC-gateway`** | `192.168.10.10` → `192.168.20.10` | 128 |
| SW/R → PC-C | **`MAC-gateway`** → `MAC-C` | `192.168.10.10` → `192.168.20.10` | **127** |

- **MAC thay đổi** ở thiết bị L3 — đúng quy tắc "MAC đổi mỗi hop"
- **IP không đổi** suốt đường
- **TTL giảm 1** — bằng chứng đã qua một hop L3

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — Quên `ip routing`:**

| Ping | Kết quả | Vì sao |
|---|---|---|
| PC-A → `192.168.10.1` | ✅ **Được** | Cùng subnet với PC-A — **không cần route**, chỉ cần L2 |
| PC-A → `192.168.20.1` | ❌ Fail | Khác subnet → cần switch route — mà routing đang tắt |
| PC-A → PC-C | ❌ Fail | Như trên |

**Lệnh phát hiện:** `show ip route` → trống hoặc báo lỗi. Hoặc
`show run | include ip routing` → không thấy dòng nào.

> 🔑 Chi tiết "ping được gateway của mình nhưng không ping được gateway VLAN kia"
> là **dấu hiệu đặc trưng** của lỗi này. Nhớ nó, nó sẽ tiết kiệm cho bạn rất nhiều thời gian.

**Lỗi 2 — Quên `no shutdown` Gi0/0:**

**Tất cả 3 subinterface** đều down. Subinterface **kế thừa trạng thái của interface vật lý** —
vật lý down thì logic cũng down, dù `show run` nhìn hoàn toàn đúng.

```text
# output điển hình — tự verify trên lab của bạn
GigabitEthernet0/0      unassigned  YES unset  administratively down  down
GigabitEthernet0/0.10   192.168.10.1 YES manual administratively down down
GigabitEthernet0/0.20   192.168.20.1 YES manual administratively down down
```

**Bài học:** với RoAS, luôn kiểm tra interface **vật lý** trước khi nghi ngờ subinterface.

**Lỗi 3 — Port nối router là access:**

Port access chỉ chở **một** VLAN và gửi frame **không tag**. Router nhận frame không tag
→ đẩy vào subinterface **native** (`.99`).

Kết quả: chỉ VLAN nào trùng với VLAN của access port mới có thể thông — và ngay cả vậy
cũng rất rối. Thực tế: **cả VLAN 10 lẫn 20 đều đứt**.

**Lệnh phát hiện:** `show interfaces trunk` trên SW1 → **không có port nào** trong danh sách.

**Lỗi 4 — Sai VLAN ID trong `encapsulation`:**

Subinterface `Gi0/0.20` giờ gắn với **VLAN 30**, không phải VLAN 20. Nó vẫn `up/up`
vì interface vật lý up — IOS không kiểm tra VLAN 30 có tồn tại trên switch hay không.

Frame của VLAN 20 tới router → **không có subinterface nào nhận** → bị drop.
PC-C mất gateway → không ping được gì ngoài VLAN của mình.

**Lệnh phát hiện:** `show run interface Gi0/0.20` → thấy `encapsulation dot1Q 30`.
Hoặc `show vlans` trên router.

> 🔑 Đây là loại lỗi tệ nhất: **cấu hình nhìn đúng, interface up, không có log lỗi nào.**
> Chỉ có cách đối chiếu từng VLAN ID với thiết kế.

### Bảng so sánh — kết quả tham khảo

| Tiêu chí | Router-on-a-Stick | SVI |
|---|---|---|
| Số thiết bị | 2 (router + switch L2) | **1** (L3 switch) |
| Số dòng cấu hình | ~25 | ~18 |
| `tracert` | 1 hop | 1 hop |
| Ping trung bình *(Packet Tracer)* | ~1–2 ms | **< 1 ms** |
| Link chở traffic inter-VLAN | Trunk SW↔R — **đi qua 2 lần** | Không có — route nội bộ ASIC |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Lỗi nào khó tìm nhất? ___
- Con số ping trung bình của RoAS vs SVI trên máy tôi: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
