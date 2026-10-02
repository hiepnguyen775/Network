# LAB 72 — Site-to-site mở rộng + khảo sát remote access

> ⚠️ **Phần A dựng trên GNS3/EVE-NG** *(IPsec/GRE thật)*. Phần B là **khảo sát**
> *(không cần cấu hình đầy đủ trong lab)* — hiểu kiến trúc là đủ cho CCNA.

| | |
|---|---|
| **Phase** | 7 |
| **Lesson liên quan** | [Lesson 41 — Site-to-Site vs Remote Access · SD-WAN](../07-wan-vpn/lesson-41-site-to-site-sdwan.md) |
| **Công cụ** | **GNS3/EVE-NG** + máy thật *(client VPN)* |
| **Thời lượng** | ~4 giờ |
| **Độ khó** | ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Mở rộng VPN thành **hub-and-spoke 3 site** *(1 hub, 2 spoke)*
- [ ] Hiểu **spoke-to-spoke** đi qua hub vs trực tiếp *(DMVPN khái niệm)*
- [ ] So sánh **site-to-site** và **remote access VPN**
- [ ] Khảo sát kiến trúc **SD-WAN** và nó giải quyết gì
- [ ] Tự gây & sửa 3 lỗi topo hub-and-spoke

## 2. Prerequisite

- [Lesson 41](../07-wan-vpn/lesson-41-site-to-site-sdwan.md) — hub-spoke, remote access, SD-WAN
- [LAB 71](lab71-gre-ipsec.md) — GRE over IPsec *(nền tảng)*

## 3. Topology

```text
                      HUB (HQ)
                   10.0.0.0/24
                  /            \
            Tunnel1          Tunnel2
            /                      \
     SPOKE-1 (CN1)           SPOKE-2 (CN2)
     10.0.1.0/24             10.0.2.0/24

   Spoke-to-spoke mặc định đi QUA hub.
```

## 4. IP Addressing Table

| Device | WAN (public) | LAN | Tunnel |
|---|---|---|---|
| HUB | `203.0.113.1/30` | `10.0.0.1/24` | `10.255.0.1` *(Tunnel tới mỗi spoke)* |
| SPOKE-1 | `198.51.100.1/30` | `10.0.1.1/24` | `10.255.0.2` |
| SPOKE-2 | `192.0.2.1/30` | `10.0.2.1/24` | `10.255.0.3` |

---

## 5. Yêu cầu LAB

- [ ] Phần A: 2 tunnel GRE/IPsec từ hub tới 2 spoke, OSPF toàn mạng
- [ ] Chứng minh spoke-to-spoke traffic đi **qua hub**
- [ ] Phần B: khảo sát remote access + SD-WAN *(viết so sánh)*
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Phần A — Hub-and-spoke

```cisco
! ══ HUB: 2 tunnel, mỗi cái tới một spoke ══
interface Tunnel1
 ip address 10.255.0.1 255.255.255.0
 tunnel source Gi0/0
 tunnel destination 198.51.100.1          ! SPOKE-1
 tunnel protection ipsec profile VPN-PROF
interface Tunnel2
 ip address 10.255.0.1 255.255.255.0       ! (dùng DMVPN thì chung 1 mGRE)
 tunnel source Gi0/0
 tunnel destination 192.0.2.1             ! SPOKE-2
 tunnel protection ipsec profile VPN-PROF

! ══ SPOKE-1: 1 tunnel về hub ══
interface Tunnel1
 ip address 10.255.0.2 255.255.255.0
 tunnel source Gi0/0
 tunnel destination 203.0.113.1           ! HUB
 tunnel protection ipsec profile VPN-PROF
```

> 💡 Cấu hình IPsec profile giống LAB 71. Với nhiều spoke, **DMVPN** *(mGRE + NHRP)*
> là cách scale — một interface mGRE thay cho N tunnel tĩnh. CCNA chỉ cần **hiểu khái
> niệm DMVPN**, không cần cấu hình đầy đủ.

### Bước 2 — OSPF và spoke-to-spoke

```cisco
! Mọi router: OSPF area 0 trên tunnel + LAN
router ospf 1
 network 10.255.0.0 0.0.0.255 area 0
 network 10.0.X.0 0.0.0.255 area 0
```

> 🔴 **DỰ ĐOÁN:** SPOKE-1 `10.0.1.10` ping SPOKE-2 `10.0.2.10`. Traffic đi đường nào?
> Trực tiếp spoke↔spoke, hay **vòng qua hub**? `traceroute` để kiểm chứng.

### Phần B — Khảo sát (viết, không cấu hình)

Hoàn thành bảng so sánh ở mục **9. Challenge câu 2 và 3**. Đọc tài liệu Cisco về:
- **Remote access VPN** *(AnyConnect/SSL-VPN)*: nhân viên làm việc từ xa.
- **SD-WAN** *(vManage/vSmart/vEdge)*: quản lý tập trung, chọn đường theo ứng dụng.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
HUB# show ip ospf neighbor
Neighbor ID     Pri   State      Dead Time   Address        Interface
2.2.2.2           0   FULL/  -   00:00:33    10.255.0.2     Tunnel1
3.3.3.3           0   FULL/  -   00:00:36    10.255.0.3     Tunnel2
```

```text
# output điển hình — spoke-to-spoke đi QUA hub (2 hop tunnel)
SPOKE-1# traceroute 10.0.2.10
  1  10.255.0.1   (HUB tunnel)      5 ms     ← qua hub
  2  10.0.2.10    (SPOKE-2 LAN)     9 ms
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | Hub thấy 2 OSPF neighbor *(2 spoke)* | ✅ | |
| 2 | SPOKE-1 ping HUB LAN | ✅ | |
| 3 | SPOKE-1 ping SPOKE-2 LAN | ✅ | |
| 4 | traceroute spoke→spoke đi qua hub | ✅ | |
| 5 | Phần B: bảng so sánh hoàn thành | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Hub chết, spoke-to-spoke đứt ⭐

```text
Shutdown interface WAN của HUB
```

| | |
|---|---|
| SPOKE-1 còn ping SPOKE-2 không? | |
| Vì sao mất hub = mất **toàn bộ** liên lạc giữa spoke? | |
| Đây là nhược điểm gì của hub-and-spoke thuần? | |
| DMVPN Phase 2/3 giải quyết thế nào? | |

### Lỗi 2 — OSPF network type trên tunnel

```text
Tunnel mặc định là point-to-point; thử để mạng hub-spoke như broadcast
và quan sát DR/BDR bầu sai
```

| | |
|---|---|
| Spoke có nhìn thấy route của spoke khác không? | |
| Vì sao hub-and-spoke cần cẩn thận với OSPF network type? | |
| `point-to-multipoint` giúp gì? | |

### Lỗi 3 — Overlap subnet giữa 2 site

```text
Đổi LAN SPOKE-2 thành 10.0.1.0/24 (TRÙNG SPOKE-1)
```

| | |
|---|---|
| OSPF báo gì? Route nào thắng? | |
| HUB biết gửi `10.0.1.0/24` tới spoke nào? | |
| Vì sao quy hoạch IP không trùng là bắt buộc cho VPN đa site? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Hub-and-spoke thuần vs DMVPN: DMVPN giải quyết vấn đề gì về spoke-to-spoke và scale?
2. **Site-to-site** vs **remote access** VPN — điền bảng so sánh.
3. SD-WAN giải quyết điểm đau nào của WAN truyền thống? Nêu 3 lợi ích.
4. Công ty có 50 chi nhánh. Hub-spoke tĩnh có gì bất tiện? Giải pháp?

<details>
<summary>Đáp án</summary>

**1.** Hub-and-spoke thuần:
- Spoke-to-spoke **luôn qua hub** → hub thành nút thắt cổ chai + điểm chết đơn *(SPOF)*.
- Mỗi spoke mới = thêm tunnel tĩnh trên hub → **không scale**.

**DMVPN** *(mGRE + NHRP + IPsec)*:
- **Phase 2/3:** spoke-to-spoke tạo tunnel **trực tiếp động** *(không qua hub)* nhờ NHRP
  phân giải địa chỉ → giảm tải hub, giảm độ trễ.
- **mGRE:** một interface cho **mọi** spoke → thêm spoke không đụng cấu hình hub → scale.

**2.**

| | Site-to-Site | Remote Access |
|---|---|---|
| Kết nối | **mạng ↔ mạng** *(2 router/firewall)* | **một người dùng ↔ mạng** |
| Ai khởi tạo | thiết bị *(luôn-on)* | client phần mềm *(khi cần)* |
| Xác thực | PSK/cert giữa thiết bị | user login *(+ MFA)* |
| Dùng khi | nối 2 văn phòng cố định | nhân viên làm từ xa, laptop |
| Công nghệ | IPsec/GRE, DMVPN | SSL-VPN *(AnyConnect)*, IKEv2 |

**3.** SD-WAN giải quyết điểm đau WAN truyền thống:
- **Quản lý tập trung:** đẩy chính sách tới hàng trăm site từ một dashboard *(vManage)*,
  thay vì SSH từng router.
- **Chọn đường theo ứng dụng (application-aware):** voice đi đường độ trễ thấp, backup đi
  đường rẻ — tự động theo chất lượng đo được *(không như routing tĩnh)*.
- **Dùng nhiều loại đường:** MPLS + Internet + 4G cùng lúc, failover/load-balance thông
  minh → giảm chi phí *(bớt phụ thuộc MPLS đắt)*.
- Bonus: **zero-touch provisioning** — cắm thiết bị mới, tự tải cấu hình.

**4.** 50 chi nhánh với hub-spoke tĩnh:
- Hub cần **50 tunnel** cấu hình tay → cực kỳ nặng, dễ sai.
- Spoke mới = sửa hub mỗi lần.
- Spoke-to-spoke qua hub → trễ + tải hub.

Giải pháp: **DMVPN** *(scale bằng mGRE/NHRP)* hoặc **SD-WAN** *(quản lý tập trung,
zero-touch)*. Với 50+ site, SD-WAN thường là lựa chọn hiện đại.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Phần A — spoke-to-spoke qua hub

`traceroute` từ SPOKE-1 tới SPOKE-2 cho thấy **2 hop tunnel**: SPOKE-1 → HUB → SPOKE-2.
Với hub-and-spoke tĩnh, spoke **không có tunnel trực tiếp** tới nhau → mọi traffic phải
vòng qua hub. Đây là lý do DMVPN Phase 2/3 ra đời.

### Giải thích các lỗi BREAK

**Lỗi 1 — hub chết ⭐:** Spoke chỉ có tunnel **tới hub**, không tới nhau. Hub chết →
không spoke nào liên lạc được với spoke khác *(và cả hub)*. Đây là **SPOF** *(single
point of failure)* của hub-and-spoke thuần. Giảm thiểu: **dual-hub** *(2 hub dự phòng)*
hoặc DMVPN với tunnel spoke-to-spoke trực tiếp.

**Lỗi 2 — OSPF network type:** Tunnel GRE mặc định **point-to-point** — tốt cho từng
cặp. Nếu dùng một mạng chung kiểu broadcast *(mGRE)*, OSPF bầu DR/BDR, và spoke có thể
**không thấy route của spoke khác** nếu DR không phải hub, hoặc next-hop không đúng.
`ip ospf network point-to-multipoint` xử lý đúng topo hub-spoke: hub quảng bá route của
mọi spoke, next-hop được viết lại hợp lý.

**Lỗi 3 — overlap subnet:** Hai site cùng `10.0.1.0/24` → OSPF nhận **hai LSA cùng prefix**
→ hub không biết gửi `10.0.1.0/24` tới spoke nào *(chọn metric thấp hơn, spoke kia thành
"vô hình")*. VPN đa site **bắt buộc** quy hoạch IP **không trùng** — đây là lý do IP plan
tập trung *(như Final Project)* quan trọng.

### Bảng tổng kết

| Khái niệm | Điểm cốt lõi |
|---|---|
| Hub-and-spoke thuần | spoke-to-spoke qua hub; hub là SPOF; không scale |
| DMVPN | mGRE+NHRP → spoke-to-spoke động, scale |
| Site-to-site vs RA | mạng↔mạng vs người↔mạng |
| SD-WAN | quản lý tập trung + app-aware + multi-transport |
| IP không trùng | bắt buộc cho VPN đa site |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Spoke-to-spoke đi qua hub — tôi traceroute chứng minh chưa? ___
- Site-to-site vs remote access — khi nào dùng cái nào? ___
- SD-WAN giải quyết điểm đau gì? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
