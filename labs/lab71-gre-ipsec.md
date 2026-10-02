# LAB 71 — GRE over IPsec site-to-site

> ⚠️ **PHẢI làm trên GNS3/EVE-NG** *(IOSv / CSR1000v)* — Packet Tracer **không** mô phỏng
> đủ IPsec. Nếu chưa dựng được GNS3, đọc để hiểu, làm sau.

| | |
|---|---|
| **Phase** | 7 |
| **Lesson liên quan** | [Lesson 40 — VPN · GRE over IPsec · IKE](../07-wan-vpn/lesson-40-vpn-gre-ipsec.md) |
| **Công cụ** | **GNS3/EVE-NG** *(IOSv/CSR)* + Wireshark |
| **Thời lượng** | ~4 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Dựng **GRE tunnel** nối 2 site qua "Internet"
- [ ] Bọc GRE bằng **IPsec** *(mã hoá)* và hiểu vì sao cần cả hai
- [ ] Nắm **IKE 2 phase**: Phase 1 *(ISAKMP SA)* và Phase 2 *(IPsec SA)*
- [ ] Chạy **OSPF qua tunnel** *(GRE cho phép multicast, IPsec thuần thì không)*
- [ ] Bắt gói Wireshark: thấy ESP mã hoá, không đọc được payload
- [ ] Tự gây & sửa 3 lỗi VPN

## 2. Prerequisite

- [Lesson 40](../07-wan-vpn/lesson-40-vpn-gre-ipsec.md) — GRE, IPsec, IKE
- [LAB 23](lab23-ospf-single-area.md) — OSPF *(chạy qua tunnel)*
- Biết dựng lab GNS3/EVE-NG cơ bản

## 3. Topology

```text
   LAN-A                                        LAN-B
 10.0.1.0/24                                  10.0.2.0/24
     │                                            │
    R1 ──── 203.0.113.1 ~~~ Internet ~~~ 198.51.100.1 ──── R2
     │         (Gi0/0)      (ISP)         (Gi0/0)          │
     └── Tunnel0 10.255.255.1/30 ═══════ 10.255.255.2/30 ──┘
                    GRE over IPsec
```

## 4. IP Addressing Table

| Device | Interface | IP |
|---|---|---|
| R1 | Gi0/0 *(WAN)* | `203.0.113.1/30` |
| R1 | Gi0/1 *(LAN-A)* | `10.0.1.1/24` |
| R1 | Tunnel0 | `10.255.255.1/30` |
| R2 | Gi0/0 *(WAN)* | `198.51.100.1/30` |
| R2 | Gi0/1 *(LAN-B)* | `10.0.2.1/24` |
| R2 | Tunnel0 | `10.255.255.2/30` |
| ISP | — | nối 2 WAN, route public |

---

## 5. Yêu cầu LAB

- [ ] GRE tunnel up, ping qua tunnel IP
- [ ] IPsec bảo vệ tunnel, `show crypto ipsec sa` có gói mã hoá
- [ ] OSPF neighbor hình thành **qua tunnel**, LAN-A ping LAN-B
- [ ] Wireshark trên đoạn Internet: chỉ thấy **ESP**, không đọc được nội dung
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Kết nối WAN cơ bản

```cisco
! R1
interface Gi0/0
 ip address 203.0.113.1 255.255.255.252
ip route 0.0.0.0 0.0.0.0 203.0.113.2
! R2
interface Gi0/0
 ip address 198.51.100.1 255.255.255.252
ip route 0.0.0.0 0.0.0.0 198.51.100.2
! Xác nhận R1 ping được 198.51.100.1 (qua ISP) TRƯỚC khi làm tunnel
```

### Bước 2 — GRE tunnel

```cisco
! R1
interface Tunnel0
 ip address 10.255.255.1 255.255.255.252
 tunnel source Gi0/0
 tunnel destination 198.51.100.1
! R2
interface Tunnel0
 ip address 10.255.255.2 255.255.255.252
 tunnel source Gi0/0
 tunnel destination 203.0.113.1
```

> 🔴 **DỰ ĐOÁN:** lúc này ping `10.255.255.2` từ R1 được không? Traffic qua tunnel
> đã **mã hoá** chưa? Wireshark thấy gì?

### Bước 3 — IPsec bảo vệ tunnel ⭐

```cisco
! ══ Phase 1 (IKE/ISAKMP) — thiết lập kênh quản lý an toàn ══
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 3600
crypto isakmp key MySecretKey address 198.51.100.1    ! (R2: address 203.0.113.1)

! ══ Phase 2 (IPsec) — bảo vệ dữ liệu thật ══
crypto ipsec transform-set TS esp-aes 256 esp-sha256-hmac
 mode transport                                       ! transport cho GRE

crypto ipsec profile GRE-PROTECT
 set transform-set TS

! ══ Gắn IPsec vào tunnel ══
interface Tunnel0
 tunnel mode gre ip
 tunnel protection ipsec profile GRE-PROTECT
```

> 🔑 **Vì sao GRE + IPsec, không chỉ IPsec?**
> - **IPsec thuần** không chuyển được **multicast/broadcast** → OSPF *(dùng multicast)*
>   không chạy qua IPsec thuần.
> - **GRE** bọc mọi loại traffic *(gồm multicast)* thành unicast → OSPF chạy được.
> - Nhưng GRE **không mã hoá** → bọc GRE trong IPsec để vừa chạy routing vừa bảo mật.
>
> **IKE 2 phase:** Phase 1 dựng kênh an toàn để thương lượng *(ISAKMP SA)*; Phase 2
> dùng kênh đó thoả thuận khoá cho dữ liệu thật *(IPsec SA)*.

### Bước 4 — OSPF qua tunnel

```cisco
! R1
router ospf 1
 network 10.255.255.0 0.0.0.3 area 0      ! tunnel
 network 10.0.1.0 0.0.0.255 area 0        ! LAN-A
! R2: network 10.255.255.0 + 10.0.2.0
```

> ⚠️ **Đừng** quảng bá mạng WAN public `203.0.113.0` vào OSPF — chỉ tunnel + LAN.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst              src              state          conn-id status
198.51.100.1     203.0.113.1      QM_IDLE           1001 ACTIVE
```

```text
# output điển hình — tự verify trên lab của bạn
R1# show crypto ipsec sa | include encaps|decaps|pkts
    #pkts encaps: 420, #pkts encrypt: 420, #pkts digest: 420
    #pkts decaps: 418, #pkts decrypt: 418, #pkts verify: 418
```

```text
# output điển hình — OSPF neighbor qua tunnel
R1# show ip ospf neighbor
Neighbor ID     Pri   State      Dead Time   Address         Interface
2.2.2.2           0   FULL/  -   00:00:34    10.255.255.2    Tunnel0
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | GRE tunnel up, ping `10.255.255.2` | ✅ | |
| 2 | ISAKMP SA `QM_IDLE / ACTIVE` | ✅ *(Phase 1 xong)* | |
| 3 | `#pkts encrypt` tăng | ✅ *(Phase 2 mã hoá)* | |
| 4 | OSPF neighbor FULL qua Tunnel0 | ✅ | |
| 5 | LAN-A `10.0.1.x` ping LAN-B `10.0.2.x` | ✅ | |
| 6 | Wireshark đoạn Internet: chỉ thấy **ESP** | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Pre-shared key không khớp ⭐

```cisco
R2(config)# crypto isakmp key SaiKey address 203.0.113.1
```

| | |
|---|---|
| `show crypto isakmp sa` — state dừng ở đâu? *(gợi ý: MM_NO_STATE)* | |
| Phase 1 hay Phase 2 fail? | |
| GRE tunnel có "up" không *(tunnel up ≠ IPsec up)*? | |
| Ping qua tunnel được không? | |

### Lỗi 2 — Transform-set / policy mismatch

```cisco
R2(config)# crypto ipsec transform-set TS esp-3des esp-md5-hmac   ! khác R1
```

| | |
|---|---|
| Phase 1 có lên không? Phase 2? | |
| `show crypto ipsec sa` có #pkts encrypt tăng không? | |
| Hai đầu cần khớp những gì ở Phase 2? | |

### Lỗi 3 — OSPF không chạy vì IPsec thuần (bỏ GRE)

```text
Thử cấu hình IPsec thuần (crypto map, không GRE), rồi bật OSPF
```

| | |
|---|---|
| OSPF neighbor có hình thành không? | |
| Vì sao OSPF *(multicast 224.0.0.5)* không qua được IPsec thuần? | |
| GRE giải quyết điều này thế nào? | |
| Nếu chỉ cần định tuyến tĩnh thì có cần GRE không? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Giải thích IKE Phase 1 vs Phase 2: mỗi phase tạo ra gì, bảo vệ gì?
2. `mode transport` vs `mode tunnel` trong IPsec — khi nào dùng cái nào với GRE?
3. Wireshark bắt được gói ESP — bạn đọc được gì, không đọc được gì? Vì sao vẫn an toàn?
4. Tunnel up nhưng LAN-A không ping được LAN-B. Nêu 3 chỗ kiểm tra theo thứ tự.

<details>
<summary>Đáp án</summary>

**1.** IKE 2 phase:

| | Phase 1 (ISAKMP/IKE SA) | Phase 2 (IPsec SA) |
|---|---|---|
| Mục đích | Dựng **kênh quản lý** an toàn giữa 2 peer | Thoả thuận khoá cho **dữ liệu thật** |
| Thương lượng | encryption, hash, DH group, auth | transform-set, proxy ACL, PFS |
| Kết quả | **1 ISAKMP SA** 2 chiều | **2 IPsec SA** *(mỗi chiều một)* |
| Chế độ | Main/Aggressive mode | Quick mode |

Phase 1 làm **một lần**, tạo kênh để Phase 2 thương lượng nhanh và an toàn. Phase 2 SA
hết hạn thường xuyên hơn *(rekey)*.

**2.**

| | transport | tunnel |
|---|---|---|
| Mã hoá | chỉ **payload** *(giữ IP header gốc)* | **toàn bộ gói** *(thêm IP header mới)* |
| Dùng với GRE | **transport** — GRE đã có header riêng, không cần thêm | — |
| Dùng không GRE | — | **tunnel** — site-to-site IPsec thuần |

Với **GRE over IPsec** dùng `mode transport` vì GRE đã bọc gói *(có IP header ngoài)* —
IPsec chỉ cần bảo vệ payload GRE, không cần header mới → tiết kiệm overhead.

**3.** Wireshark trên đoạn Internet thấy:
- **Đọc được:** IP header ngoài *(src/dst = IP public 2 router)*, protocol = **ESP (50)**,
  SPI.
- **KHÔNG đọc được:** payload *(GRE + IP gốc + dữ liệu LAN)* — đã mã hoá AES.

Vẫn an toàn vì kẻ nghe chỉ biết "hai IP này đang nói chuyện VPN" nhưng **không biết nội
dung** — không thấy LAN IP, không thấy dữ liệu, không sửa được *(HMAC phát hiện)*.

**4.** Tunnel up nhưng LAN không thông:

```text
1. IPsec thật sự mã hoá chưa? show crypto ipsec sa → #pkts encrypt tăng?
   (tunnel "up" có thể chỉ là GRE up, IPsec chưa)
2. Routing: LAN-A có route tới 10.0.2.0/24 qua tunnel chưa?
   show ip route → OSPF neighbor FULL? network statement đủ chưa?
3. ACL/NAT: có NAT nuốt traffic LAN-to-LAN không? (phải DENY VPN traffic khỏi NAT)
   firewall chặn ESP/UDP500/4500?
```

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Bước 2 — GRE chưa mã hoá

Sau Bước 2 *(chỉ GRE)*, ping `10.255.255.2` **được**, nhưng Wireshark trên Internet thấy
**GRE protocol 47** với payload **đọc được** *(IP gốc + dữ liệu rõ)*. GRE chỉ **đóng gói**,
không mã hoá. Đây là lý do Bước 3 bọc IPsec.

### Giải thích các lỗi BREAK

**Lỗi 1 — PSK sai ⭐:** Phase 1 dùng pre-shared key để xác thực peer. Key khác nhau →
Phase 1 **fail** → `show crypto isakmp sa` kẹt ở `MM_NO_STATE` *(main mode chưa xong)*.
Không có Phase 1 → không Phase 2 → IPsec không bảo vệ. GRE tunnel có thể hiện "up"
*(line protocol)* nhưng traffic **không mã hoá được** → thực tế không qua *(hoặc qua
không bảo vệ tuỳ cấu hình)*. Bài học: **tunnel up ≠ VPN up**.

**Lỗi 2 — transform-set mismatch:** Phase 1 vẫn lên *(dùng isakmp policy, khớp)*, nhưng
Phase 2 **fail** vì hai đầu đề xuất bộ mã hoá khác nhau *(AES-SHA256 vs 3DES-MD5)* →
không có IPsec SA chung → `#pkts encrypt` = 0. Phase 2 cần khớp: **encryption, hash,
(PFS group nếu có)**.

**Lỗi 3 — IPsec thuần không qua OSPF:** OSPF gửi hello tới **multicast 224.0.0.5**.
IPsec thuần *(crypto map + proxy ACL)* chỉ bảo vệ **unicast** khớp ACL → **bỏ qua
multicast** → OSPF hello không được đóng gói → **không có neighbor**. GRE bọc multicast
thành **unicast** giữa 2 tunnel endpoint → OSPF chạy. Nếu chỉ dùng **static route** thì
IPsec thuần đủ *(không cần GRE)* — GRE cần khi muốn **routing protocol động** qua VPN.

### Bảng tổng kết

| Thành phần | Vai trò |
|---|---|
| GRE | Đóng gói mọi traffic *(gồm multicast)* → cho phép OSPF |
| IPsec | Mã hoá + toàn vẹn + xác thực |
| IKE Phase 1 | Kênh quản lý an toàn *(ISAKMP SA)* |
| IKE Phase 2 | Khoá cho dữ liệu *(IPsec SA)* |
| `mode transport` | Dùng với GRE *(tiết kiệm header)* |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Vì sao cần GRE **và** IPsec, không chỉ một? ___
- Lỗi 1 (PSK sai) — "tunnel up ≠ VPN up" tôi hiểu chưa? ___
- IKE Phase 1 vs Phase 2 tôi phân biệt được chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
