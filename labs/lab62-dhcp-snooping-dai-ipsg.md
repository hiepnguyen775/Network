# LAB 62 — DHCP Snooping, DAI, IPSG

| | |
|---|---|
| **Phase** | 6 |
| **Lesson liên quan** | [Lesson 37 — DHCP Snooping · DAI · IPSG](../06-security/lesson-37-dhcp-snooping-dai.md) |
| **Công cụ** | Cisco Packet Tracer |
| **Thời lượng** | ~2.5 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Tự dựng **rogue DHCP server** và chứng kiến nó cướp client
- [ ] Chặn nó bằng **DHCP Snooping** với khái niệm trust/untrust
- [ ] Hiểu **binding table** là nền móng cho DAI và IPSG
- [ ] Chặn **ARP spoofing** bằng DAI
- [ ] Chặn **IP spoofing** bằng IP Source Guard
- [ ] Hiểu vì sao thứ tự triển khai là **Snooping → DAI → IPSG**

## 2. Prerequisite

- [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md) — DHCP DORA
- [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md) — ARP
- [Lesson 37](../06-security/lesson-37-dhcp-snooping-dai.md) — 3 cơ chế này
- LAB 05 *(DHCP server + relay — Phase 0)* nếu đã làm

---

## 3. Topology

```text
         ┌──────────────── SW1 ────────────────┐
         │   Gi0/1      Fa0/1   Fa0/2   Fa0/3  │
         │  (uplink)                           │
         └─────┬─────────┬───────┬───────┬─────┘
               │         │       │       │
              R1      PC-GOOD  ATTACKER  PC-VICTIM
         (DHCP server)
         10.0.10.1
                      ↑ cổng này cắm cả rogue DHCP
                        lẫn công cụ ARP spoof
```

| Thiết bị | Cổng SW1 | Vai trò |
|---|---|---|
| R1 | Gi0/1 | DHCP server hợp pháp + gateway |
| PC-GOOD | Fa0/1 | Client bình thường |
| ATTACKER *(Server-PT)* | Fa0/2 | Rogue DHCP + ARP spoof |
| PC-VICTIM | Fa0/3 | Nạn nhân |

## 4. IP Addressing Table

| Device | Interface | IP | Ghi chú |
|---|---|---|---|
| R1 | Gi0/0 | `10.0.10.1/24` | Gateway thật + DHCP server |
| SW1 | Vlan10 | `10.0.10.2/24` | Quản trị |
| PC-GOOD | Fa0 | **DHCP** | — |
| PC-VICTIM | Fa0 | **DHCP** | — |
| ATTACKER | Fa0 | `10.0.10.66/24` *(static)* | Rogue DHCP phát dải giả |

**DHCP pool hợp pháp (R1):**

```cisco
ip dhcp excluded-address 10.0.10.1 10.0.10.9
ip dhcp pool LAN-10
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 10.0.50.10
 lease 0 12
```

**Rogue pool (ATTACKER — Server-PT → Services → DHCP):**

| Mục | Giá trị |
|---|---|
| Pool Name | `ROGUE` |
| Default Gateway | **`10.0.10.66`** ← chính attacker |
| DNS Server | `10.0.10.66` |
| Start IP | `10.0.10.200` |
| Subnet Mask | `255.255.255.0` |
| Max Users | `50` |
| Service | **On** |

---

## 5. Yêu cầu LAB

- [ ] Phase A: **chứng minh tấn công thành công** khi chưa có phòng thủ
- [ ] Phase B: DHCP Snooping chặn rogue, binding table có đủ entry
- [ ] Phase C: DAI chặn ARP giả
- [ ] Phase D: IPSG chặn IP giả
- [ ] Hoàn thành mục **8. BREAK** với đủ 4 lỗi

---

## 6. Step-by-step

### Phase A — Tấn công khi chưa phòng thủ ⚠️

> 🔴 **DỰ ĐOÁN trước:** PC-VICTIM gõ `ipconfig /renew`. Nó sẽ nhận IP từ ai —
> R1 hay ATTACKER? Dựa vào đâu?

```text
Dự đoán của tôi: _______________
Lý do:            _______________
```

Bật rogue DHCP trên ATTACKER, rồi trên PC-VICTIM:

```cisco
PC> ipconfig /release
PC> ipconfig /renew
PC> ipconfig /all
```

| Quan sát | Ghi lại |
|---|---|
| IP nhận được | |
| Default Gateway | |
| DNS Server | |
| Nhận từ server nào? | |

> 💡 Chạy lại vài lần. Kết quả có thể **khác nhau mỗi lần** —
> đó chính là bản chất của cuộc đua này.

**Vì sao nguy hiểm:** nếu client nhận gateway = `10.0.10.66`, **mọi traffic ra ngoài
đi qua máy attacker**. Đây là Man-in-the-Middle hoàn chỉnh mà nạn nhân không hề biết.

### Phase B — DHCP Snooping

```cisco
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 10

! CHỈ cổng tới DHCP server hợp pháp mới là TRUST
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# ip dhcp snooping trust
SW1(config-if)# exit

! Giới hạn tốc độ DHCP trên cổng user → chống DHCP starvation
SW1(config)# interface range FastEthernet0/1 - 24
SW1(config-if-range)# ip dhcp snooping limit rate 10
SW1(config-if-range)# exit

! Packet Tracer / nhiều IOS cần tắt option 82 khi switch không phải relay
SW1(config)# no ip dhcp snooping information option
```

> ⚠️ **Mặc định MỌI cổng là untrusted.** Nếu quên trust cổng uplink,
> **toàn bộ mạng mất DHCP** — xem Lỗi 1.

Thử lại từ PC-VICTIM:

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| `ipconfig /renew` | Nhận IP từ **R1** *(gateway `10.0.10.1`)* | |
| Lặp lại 5 lần | Lần nào cũng từ R1 | |
| `show ip dhcp snooping binding` | Có entry cho PC-GOOD và PC-VICTIM | |

```cisco
SW1# show ip dhcp snooping
SW1# show ip dhcp snooping binding
```

> 🔑 **Binding table là nền móng.** DAI và IPSG đều tra bảng này.
> Không có nó, hai cơ chế sau vô nghĩa.

### Phase C — Dynamic ARP Inspection (DAI)

> 🔴 **DỰ ĐOÁN trước:** nếu bạn bật DAI mà **chưa** có binding table
> cho một máy IP tĩnh, chuyện gì xảy ra với máy đó?

```cisco
SW1(config)# ip arp inspection vlan 10

! Cổng uplink phải TRUST (giống DHCP Snooping)
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# ip arp inspection trust
SW1(config-if)# exit

! Giới hạn tốc độ ARP trên cổng user
SW1(config)# interface range FastEthernet0/1 - 24
SW1(config-if-range)# ip arp inspection limit rate 15
```

**Xử lý máy IP tĩnh** *(R1, SW1, server — không đi qua DHCP nên không có binding)*:

```cisco
SW1(config)# arp access-list TIN-CAY
SW1(config-arp-nacl)# permit ip host 10.0.10.1 mac host 0001.0001.0001
SW1(config-arp-nacl)# exit
SW1(config)# ip arp inspection filter TIN-CAY vlan 10
```

> 💡 Thay `0001.0001.0001` bằng MAC thật của R1 Gi0/0
> *(lấy bằng `show interfaces gi0/0 | include bia`)*.

**Thử tấn công:** từ ATTACKER, gửi ARP reply giả claim `10.0.10.1`
*(Packet Tracer: dùng chế độ Simulation, tạo gói ARP thủ công, hoặc đặt
IP của ATTACKER = `10.0.10.1` để tạo xung đột)*.

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| ARP giả từ ATTACKER | Bị **drop** | |
| `show ip arp inspection statistics` | Cột `Drop` tăng | |
| Có log `%SW_DAI-4-DHCP_SNOOPING_DENY` | ✅ | |
| PC-GOOD vẫn ping được R1 | ✅ | |

### Phase D — IP Source Guard

```cisco
SW1(config)# interface range FastEthernet0/1 - 24
SW1(config-if-range)# ip verify source port-security
```

> `ip verify source` *(không có `port-security`)* chỉ kiểm tra **IP**.
> Thêm `port-security` thì kiểm tra **cả IP lẫn MAC** — chặt hơn.
> Cần bật `switchport port-security` trên cổng đó.

**Thử:** trên PC-VICTIM, đổi từ DHCP sang IP tĩnh `10.0.10.99`
*(IP này không có trong binding table)*.

| Kiểm chứng | Mong đợi | Thực tế |
|---|---|---|
| PC-VICTIM với IP `10.0.10.99` ping R1 | ❌ Bị drop | |
| `show ip verify source` | Cổng Fa0/3 có binding | |
| Đổi lại về DHCP | ✅ Ping lại được | |

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip dhcp snooping
Switch DHCP snooping is enabled
DHCP snooping is configured on following VLANs: 10
Insertion of option 82 is disabled
Interface              Trusted    Rate limit (pps)
-----------------      -------    ----------------
GigabitEthernet0/1     yes        unlimited
FastEthernet0/1        no         10
FastEthernet0/2        no         10
FastEthernet0/3        no         10
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip dhcp snooping binding
MacAddress          IpAddress        Lease(sec)  Type           VLAN  Interface
------------------  ---------------  ----------  -------------  ----  ---------------
00:0A:00:0A:00:0A   10.0.10.10       43198       dhcp-snooping   10   FastEthernet0/1
00:0C:00:0C:00:0C   10.0.10.11       43200       dhcp-snooping   10   FastEthernet0/3
Total number of bindings: 2
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip arp inspection statistics vlan 10
 Vlan      Forwarded        Dropped     DHCP Drops      ACL Drops
 ----      ---------        -------     ----------      ---------
   10             84              7              7              0
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show ip verify source
Interface  Filter-type  Filter-mode  IP-address      Mac-address        Vlan
---------  -----------  -----------  --------------  -----------------  ----
Fa0/1      ip-mac       active       10.0.10.10      00:0A:00:0A:00:0A   10
Fa0/3      ip-mac       active       10.0.10.11      00:0C:00:0C:00:0C   10
```

```text
# output điển hình — log khi DAI chặn ARP giả
%SW_DAI-4-DHCP_SNOOPING_DENY: 1 Invalid ARPs (Res) on Fa0/2, vlan 10.
([000c.000c.000c/10.0.10.1/ffff.ffff.ffff/10.0.10.11/09:14:22 UTC])
```

**Bảng kiểm chứng tổng hợp:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | *(Phase A)* Rogue DHCP cướp được client | ✅ *(chứng minh nguy cơ)* | |
| 2 | Sau Snooping: client luôn nhận từ R1 | ✅ | |
| 3 | `show ip dhcp snooping binding` ≥ 2 entry | ✅ | |
| 4 | ARP giả bị drop, cột `Dropped` tăng | ✅ | |
| 5 | PC đổi sang IP tĩnh lạ → mất mạng | ✅ | |
| 6 | PC quay lại DHCP → có mạng | ✅ | |
| 7 | PC-GOOD hoạt động bình thường suốt lab | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Quên trust cổng uplink ⭐

> 🔴 Đây là sự cố thật phổ biến nhất khi triển khai DHCP Snooping.

```cisco
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# no ip dhcp snooping trust
```

Từ PC-GOOD: `ipconfig /release` rồi `ipconfig /renew`.

| | |
|---|---|
| Nhận được IP không? | |
| IP nhận được là gì? *(gợi ý: `169.254.x.x`?)* | |
| `show ip dhcp snooping binding` — có entry mới không? | |
| **Vì sao** gói từ R1 bị chặn? | |
| Nếu lỗi này xảy ra lúc 2h sáng ở công ty 500 máy, hậu quả? | |

### Lỗi 2 — Bật DAI nhưng chưa có binding

```cisco
! Xoá binding của PC-GOOD
SW1# clear ip dhcp snooping binding *
```

Từ PC-GOOD: `arp -d *` rồi `ping 10.0.10.1`.

| | |
|---|---|
| Ping được không? | |
| `show ip arp inspection statistics` — Dropped tăng bao nhiêu? | |
| Lý do: ARP của PC-GOOD sai ở chỗ nào? | |
| Khôi phục bằng cách nào? | |

### Lỗi 3 — Máy IP tĩnh gặp DAI

```cisco
! Gỡ ARP ACL cho thiết bị tĩnh
SW1(config)# no ip arp inspection filter TIN-CAY vlan 10
```

Đặt PC-GOOD về IP tĩnh `10.0.10.50`, rồi ping R1.

| | |
|---|---|
| Ping được không? | |
| Vì sao máy IP tĩnh "vô tội" lại bị chặn? | |
| Hai cách khắc phục là gì? | |

### Lỗi 4 — Bật DAI/IPSG mà quên DHCP Snooping ⭐

```cisco
SW1(config)# no ip dhcp snooping
! DAI và IPSG vẫn đang bật
```

| | |
|---|---|
| Toàn mạng còn hoạt động không? | |
| `show ip dhcp snooping binding` trả về gì? | |
| **Vì sao** mất Snooping lại làm hỏng cả DAI lẫn IPSG? | |
| Thứ tự triển khai đúng là gì? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Mạng có 3 switch nối tầng: SW-ACCESS → SW-DIST → R1 *(DHCP server)*.
   Cổng nào trên switch nào phải `trust`? Vẽ sơ đồ và giải thích.
2. Một server IP tĩnh `10.0.50.20` nằm sau switch đã bật DAI. Nêu **hai** cách
   cho nó hoạt động, và cách nào an toàn hơn.
3. Sau khi reload switch, toàn bộ client mất mạng ~1 phút rồi tự hồi phục.
   Nguyên nhân? Cấu hình gì giải quyết được?
4. Attacker gửi hàng nghìn DHCP Discover với MAC ngẫu nhiên để làm cạn pool.
   DHCP Snooping chặn được không? Cấu hình nào mới chặn được?

<details>
<summary>Đáp án</summary>

**1.**

```text
         Fa0/1              Gi0/1            Gi0/1
PC ───── SW-ACCESS ──Gi0/2──SW-DIST ──Gi0/2── R1 (DHCP)
         untrust     TRUST   TRUST    TRUST   ↑ nguồn
```

Quy tắc: **trust mọi cổng nằm trên đường đi tới DHCP server hợp pháp**;
untrust mọi cổng hướng về phía người dùng.

| Switch | Cổng | Trust? | Vì sao |
|---|---|:---:|---|
| SW-ACCESS | Fa0/1 *(xuống PC)* | ❌ | Hướng user — nguồn tấn công |
| SW-ACCESS | Gi0/2 *(lên SW-DIST)* | ✅ | Trên đường tới DHCP server |
| SW-DIST | Gi0/1 *(xuống SW-ACCESS)* | ✅ | Gói DHCP Offer từ R1 đi xuống qua đây |
| SW-DIST | Gi0/2 *(lên R1)* | ✅ | Trực tiếp tới DHCP server |

> ⚠️ Lưu ý điểm dễ sai: **SW-DIST Gi0/1 vẫn phải trust**. Nếu untrust,
> gói Offer từ R1 đi xuống SW-ACCESS sẽ bị chính SW-DIST drop.

**2.** Hai cách:

| Cách | Cấu hình | An toàn? |
|---|---|---|
| **A. ARP ACL** ⭐ | `arp access-list TIN-CAY` + `permit ip host 10.0.50.20 mac host <MAC>` rồi `ip arp inspection filter TIN-CAY vlan 50` | ✅ **An toàn hơn** — ràng buộc **đúng cặp IP↔MAC**. Attacker giả IP đó nhưng MAC khác vẫn bị chặn |
| **B. Trust cổng** | `interface Gi0/5` + `ip arp inspection trust` | ❌ **Kém an toàn** — bỏ qua kiểm tra **toàn bộ** cổng đó. Ai cắm vào cổng này *(hoặc server bị chiếm quyền)* đều ARP spoof tự do |

**Cách A an toàn hơn** và là lựa chọn đúng cho server. Cách B chỉ nên dùng cho
**cổng uplink giữa các switch**, nơi bạn kiểm soát cả hai đầu.

Kèm theo nên cấu hình static binding cho IPSG:

```cisco
ip source binding 0050.0050.0050 vlan 50 10.0.50.20 interface GigabitEthernet0/5
```

**3.** Nguyên nhân: **binding table nằm trong RAM, mất khi reload**.

```text
Switch reload
→ binding table rỗng
→ DAI drop mọi ARP (không máy nào có binding)
→ IPSG drop mọi IP
→ Client mất mạng
→ Lease DHCP hết / client renew → binding dựng lại dần
→ Mạng tự hồi phục
```

Giải quyết: lưu binding table vào bộ nhớ bền *(hoặc TFTP)*:

```cisco
ip dhcp snooping database flash:dhcp-snooping.db
ip dhcp snooping database write-delay 60
ip dhcp snooping database timeout 300
```

Sau reload, switch nạp lại binding từ file → không có khoảng chết.

**4.** **Không, DHCP Snooping một mình không chặn được DHCP starvation.**

Lý do: Snooping chỉ kiểm tra **gói DHCP server-side** *(Offer, ACK)* đến từ cổng
untrusted. Discover từ client là **hợp lệ** — attacker gửi bao nhiêu Discover
cũng không vi phạm nguyên tắc trust/untrust.

Hai cấu hình chặn được:

```cisco
! 1. Giới hạn tốc độ DHCP — chặn flood
interface range FastEthernet0/1 - 24
 ip dhcp snooping limit rate 10

! 2. Port Security — chặn MAC giả (gốc rễ của starvation)
interface range FastEthernet0/1 - 24
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
```

Trong đó **Port Security là biện pháp gốc**: starvation dựa vào việc giả **nhiều MAC
khác nhau** trên cùng một cổng. Giới hạn 2 MAC/cổng thì attacker chỉ xin được 2 IP.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Phase A — vì sao rogue thắng

DHCP là **cuộc đua**: client gửi Discover **broadcast**, mọi DHCP server trong VLAN
đều nghe thấy và đều gửi Offer. Client lấy **Offer đến trước**.

Attacker cùng VLAN, thường gần hơn R1 về số hop → **thắng phần lớn các lần**.
Không có cơ chế nào trong DHCP để client biết server nào "hợp pháp" —
đó chính là lỗ hổng mà DHCP Snooping vá.

### Giải thích các lỗi BREAK

**Lỗi 1 — quên trust uplink ⭐:**

| Quan sát | Giải thích |
|---|---|
| Client nhận `169.254.x.x` *(APIPA)* hoặc không IP | Không nhận được Offer nào |
| Binding table không có entry mới | Không DORA nào hoàn tất |
| Có log `%DHCP_SNOOPING-5-DHCP_SNOOPING_UNTRUSTED_PORT` | Switch báo đúng nguyên nhân |

**Vì sao:** mặc định **mọi cổng là untrusted**. Trên cổng untrusted, switch
drop các gói **server-side**: `OFFER`, `ACK`, `NAK`, `LEASEQUERY`.
Gi0/1 là nơi Offer của R1 đi vào → bị drop ngay.

**Hậu quả thực tế:** sau một reload lúc 2h sáng, lease hết hạn dần trong ngày,
client mất mạng **rải rác** — rất khó chẩn đoán vì không mất đồng loạt.
Đây là lý do luôn kiểm tra `show ip dhcp snooping` ngay sau khi bật.

**Lỗi 2 — DAI không có binding:**

```text
PC-GOOD gửi ARP: "10.0.10.1 là ai? Tôi là 10.0.10.10 / MAC 000A.000A.000A"
→ DAI tra binding table cho cổng Fa0/1
→ RỖNG → không chứng minh được 10.0.10.10 thuộc về cổng này
→ DROP
```

DAI **mặc định từ chối** cái nó không chứng minh được. Khôi phục: cho client
`ipconfig /renew` → DORA mới → binding mới → ARP được chấp nhận.

**Lỗi 3 — máy IP tĩnh:**

Máy IP tĩnh **không bao giờ đi qua DHCP** → DHCP Snooping không có cớ nào tạo binding
→ DAI thấy ARP "không có nguồn gốc" → drop. Máy hoàn toàn vô tội nhưng bị chặn.

Hai cách khắc phục: **ARP ACL** *(an toàn)* hoặc **trust cổng** *(tiện nhưng yếu)* —
xem Challenge 2.

**Lỗi 4 — tắt Snooping ⭐:**

```text
         ┌─────────────────────────────┐
         │   DHCP Snooping             │  ← tạo ra binding table
         │   ↓ sinh ra ↓               │
         │   BINDING TABLE             │
         │   ↓ được tra bởi ↓          │
         │   DAI        IPSG           │
         └─────────────────────────────┘
```

DAI và IPSG **không có nguồn dữ liệu riêng** — cả hai chỉ là "người tra bảng".
Tắt Snooping → bảng rỗng → DAI drop mọi ARP, IPSG drop mọi IP → **toàn mạng chết**.

**Thứ tự triển khai đúng:**

```text
1. DHCP Snooping  ← bật trước, trust uplink, đợi binding table đầy
2. Kiểm tra: show ip dhcp snooping binding có đủ client chưa
3. Xử lý máy IP tĩnh: ip source binding + arp access-list
4. DAI            ← bật, theo dõi statistics vài ngày
5. IPSG           ← bật cuối cùng, chặt nhất
```

> Bật ngược thứ tự = tự gây sự cố toàn mạng.

### Bảng tổng kết

| Cơ chế | Chặn tấn công gì | Dựa vào | Lệnh verify |
|---|---|---|---|
| **DHCP Snooping** | Rogue DHCP *(MitM)* | trust/untrust port | `show ip dhcp snooping` |
| **DAI** | ARP spoofing *(MitM)* | binding table | `show ip arp inspection statistics` |
| **IPSG** | IP spoofing | binding table | `show ip verify source` |
| **Port Security** | MAC flooding, DHCP starvation | MAC/cổng | `show port-security` |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Phase A: rogue DHCP thắng mấy lần trên 5? Vì sao? ___
- Lỗi 1 (quên trust uplink) — triệu chứng tôi sẽ nhận ra là gì? ___
- Tôi hiểu vì sao binding table là trung tâm của cả 3 cơ chế chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
