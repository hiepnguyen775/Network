# LESSON 41 — Site-to-Site vs Remote Access · SD-WAN

> 📌 Lesson cuối cùng của cả chương trình CCNA. Sau lesson này là
> **Final CCNA Project**.

| | |
|---|---|
| **Phase** | 7 — WAN / Enterprise |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 39](./lesson-39-wan-concepts.md), [Lesson 40](./lesson-40-vpn-gre-ipsec.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Phân biệt **Site-to-Site** và **Remote Access VPN** — kiến trúc, use case
- [ ] Hiểu các kiểu triển khai remote access: IPsec client, **SSL VPN**, ZTNA
- [ ] Giải thích **split tunnel** vs **full tunnel** và đánh đổi của từng cái
- [ ] Mô tả vấn đề của **hub-and-spoke** và giải pháp **DMVPN**
- [ ] Giải thích **SD-WAN** giải quyết vấn đề gì so với WAN truyền thống

## 2. Prerequisite

- Loại WAN, SLA, dual-WAN *(Lesson 39)*
- GRE over IPsec, IKE 2 phase *(Lesson 40)*

---

## 3. Concept

### Site-to-Site vs Remote Access

| | **Site-to-Site** | **Remote Access** |
|---|---|---|
| Nối ai với ai | **Mạng ↔ Mạng** | **Một người ↔ Mạng** |
| Ai khởi tạo | **Router** *(luôn-on)* | **Phần mềm client** trên máy người dùng |
| Người dùng có biết? | ❌ Hoàn toàn trong suốt | ✅ Phải bật VPN client |
| Xác thực | Pre-shared key / chứng chỉ **thiết bị** | **Tài khoản người dùng** *(+ MFA)* |
| Số lượng | Vài — hàng chục tunnel | Hàng trăm — hàng nghìn phiên |
| Luôn kết nối | ✅ | ❌ Bật khi cần |

### Remote Access — ba thế hệ

| | **IPsec client** | **SSL VPN** | **ZTNA** *(Zero Trust)* |
|---|---|---|---|
| Giao thức | IPsec | **TLS** *(TCP 443)* | TLS + policy engine |
| Cần cài gì | Client riêng *(AnyConnect…)* | Client **hoặc trình duyệt** | Agent nhẹ / không cần |
| Qua firewall/NAT | ⚠️ Hay bị chặn | ✅ **Dễ** *(cổng 443 ai cũng mở)* | ✅ Dễ |
| Cấp quyền gì | **Vào cả mạng** | Vào cả mạng, hoặc từng ứng dụng | ⭐ **Từng ứng dụng, theo danh tính** |
| Xu hướng | Giảm dần | ⭐ Phổ biến hiện nay | **Đang lên** |

> ⭐ **Vì sao SSL VPN thắng IPsec client:** nó chạy trên **TCP 443** — cổng mà
> **mọi** khách sạn, quán cà phê, mạng công cộng đều mở. IPsec *(UDP 500, ESP)*
> hay bị chặn, và người dùng không hiểu vì sao "VPN ở nhà chạy, ở quán không chạy".

> 💡 **ZTNA** là bước tiếp theo: thay vì *"vào được mạng rồi muốn làm gì thì làm"*,
> nó cấp quyền **từng ứng dụng một**, kiểm tra liên tục danh tính + trạng thái thiết bị.
> Nguyên lý: **"never trust, always verify"**.

### Split tunnel vs Full tunnel

```text
FULL TUNNEL                        SPLIT TUNNEL
Laptop ──┐                         Laptop ──┬── traffic nội bộ ──▶ VPN
         │ TẤT CẢ traffic                   │
         ▼                                  └── traffic Internet ──▶ thẳng ra ISP
       VPN ──▶ công ty ──▶ Internet
```

| | **Full tunnel** | **Split tunnel** |
|---|---|---|
| Traffic Internet đi đâu | **Qua công ty** | **Thẳng ra ISP** |
| Băng thông công ty | ⚠️ Gánh hết | ✅ Chỉ traffic nội bộ |
| Trải nghiệm người dùng | Chậm *(xem YouTube cũng qua công ty)* | ✅ Nhanh |
| Kiểm soát & lọc | ✅ **Mọi traffic đều qua firewall công ty** | ❌ Không thấy traffic Internet |
| Rủi ro | Thấp | ⚠️ Máy nhiễm có thể là cầu nối vào mạng công ty |

> 🏭 Thực tế: **split tunnel phổ biến hơn** vì trải nghiệm tốt hơn nhiều,
> đặc biệt khi cả công ty làm việc từ xa. Bù lại bằng **EDR trên máy người dùng**
> và **ZTNA** thay vì dựa vào việc "ép mọi thứ qua firewall".

### Hub-and-Spoke và vấn đề của nó

```text
          ┌─── HUB (trụ sở) ───┐
          │                     │
    ┌─────┴─────┐         ┌─────┴─────┐
  Spoke A     Spoke B   Spoke C    Spoke D

Spoke A muốn nói với Spoke B
→ traffic phải đi A → HUB → B
→ "hairpinning" / "tromboning"
```

| Vấn đề | Chi tiết |
|---|---|
| **Độ trễ gấp đôi** | Hai chi nhánh cạnh nhau vẫn phải vòng qua trụ sở |
| **Hub là nút cổ chai** | Mọi traffic inter-site đi qua một chỗ |
| **Hub chết = mọi site mất liên lạc** | Điểm chết đơn lẻ |

### Full mesh và vấn đề của nó

```text
Số tunnel = n × (n−1) / 2

5 site  → 10 tunnel
10 site → 45 tunnel
20 site → 190 tunnel   😱
```

Mỗi tunnel phải cấu hình tay ở **cả hai đầu**. Thêm một site → phải sửa **mọi** site khác.

### DMVPN — giải pháp

**DMVPN** (Dynamic Multipoint VPN) cho phép spoke **tự động tạo tunnel trực tiếp**
với nhau khi cần, mà **chỉ cấu hình một lần** trên mỗi spoke.

```text
Bình thường:  Spoke A ──▶ HUB ──▶ Spoke B   (qua hub)

Khi có nhiều traffic A↔B:
              Spoke A ═══════════▶ Spoke B   (tunnel TRỰC TIẾP, tự tạo)
```

| Thành phần | Vai trò |
|---|---|
| **mGRE** *(multipoint GRE)* | Một interface tunnel nói chuyện với **nhiều** peer |
| **NHRP** *(Next Hop Resolution Protocol)* | Spoke hỏi hub: *"IP public của spoke B là gì?"* |
| **IPsec** | Mã hoá |

> 💡 Ở CCNA chỉ cần biết **DMVPN tồn tại và giải quyết vấn đề gì**.
> Cấu hình chi tiết ở [`CCNP-Encor` Module 08](https://github.com/hiepnguyen775/CCNP-Encor).

### SD-WAN

**SD-WAN** (Software-Defined WAN) tách **control plane** khỏi **data plane** của mạng WAN —
giống cách SDN làm với mạng LAN.

```text
┌──────────── CONTROL PLANE (tập trung) ────────────┐
│  vManage (quản lý)  vSmart (chính sách)           │
│  vBond (điều phối kết nối)                         │
└────────────────────┬───────────────────────────────┘
                     │ điều khiển
     ┌───────────────┼───────────────┐
  Edge HN         Edge SG         Edge ĐN
  (MPLS+FTTH)    (FTTH+4G)      (FTTH+4G)
     └────── data plane: tunnel tự động ──────┘
```

| SD-WAN làm được gì | Chi tiết |
|---|---|
| **Chọn đường theo ứng dụng** | VoIP đi MPLS *(ổn định)*, backup đi Internet *(rẻ)* |
| **Đo chất lượng liên tục** | Latency, jitter, loss từng đường — chuyển khi suy giảm |
| **Zero-touch provisioning** | Cắm thiết bị ở chi nhánh mới → tự tải cấu hình |
| **Chính sách tập trung** | Đổi một lần, áp cho 100 site |
| **Mã hoá tự động** | Không cần cấu hình IPsec tay cho từng cặp |

> ⭐ **Khác biệt cốt lõi với WAN truyền thống:**
> WAN truyền thống chọn đường theo **đích đến** *(routing table)*.
> SD-WAN chọn đường theo **ứng dụng + chất lượng đường thời gian thực**.

> 🏭 Ví dụ cụ thể: cuộc gọi Teams đang đi đường FTTH, hệ thống phát hiện jitter tăng
> lên 45 ms → **tự chuyển sang MPLS** giữa cuộc gọi, người dùng không biết gì.
> WAN truyền thống không làm được — nó chỉ biết đường còn sống hay chết.

---

## 4. Why?

> **Vì sao doanh nghiệp chuyển sang SD-WAN?**

| Vấn đề của WAN truyền thống | SD-WAN giải quyết |
|---|---|
| MPLS **rất đắt** | Dùng Internet rẻ + đảm bảo chất lượng bằng phần mềm |
| Thêm site mới mất **vài tuần** | Zero-touch — **vài giờ** |
| Cấu hình từng router một | Chính sách **tập trung** |
| Chỉ biết đường **sống/chết** | Đo **chất lượng** liên tục |
| Không phân biệt ứng dụng | Chọn đường **theo từng ứng dụng** |
| Traffic SaaS *(Microsoft 365)* phải vòng qua trụ sở | **Local breakout** — ra thẳng Internet tại chi nhánh |

> 🔑 **Local breakout** là lợi ích lớn mà ít người nói tới: với WAN truyền thống,
> nhân viên chi nhánh dùng Microsoft 365 → traffic chạy chi nhánh → trụ sở → Internet →
> Microsoft → và ngược lại. SD-WAN cho phép ra **thẳng Internet tại chi nhánh**,
> vẫn giữ được kiểm soát chính sách.

> **Vì sao không phải ai cũng dùng SD-WAN?**

| Rào cản | Chi tiết |
|---|---|
| **Chi phí ban đầu** | Thiết bị + license không rẻ |
| **Khoá vào nhà cung cấp** | Cisco, VMware, Fortinet… — khó chuyển đổi |
| **Phức tạp hơn khi debug** | Nhiều lớp trừu tượng |
| Mạng nhỏ **không cần** | 2–3 site thì VPN thủ công là đủ |

> 🔧 Ngưỡng thực tế: từ khoảng **10 site trở lên**, SD-WAN bắt đầu đáng tiền.

---

## 5. How does it work? — so sánh ba mô hình

| Tiêu chí | **Hub-and-Spoke** | **DMVPN** | **SD-WAN** |
|---|---|---|---|
| Cấu hình khi thêm site | Sửa ở hub | **Chỉ sửa ở spoke mới** | **Zero-touch** |
| Spoke-to-spoke | Qua hub | **Trực tiếp** *(động)* | Trực tiếp |
| Chọn đường | Routing table | Routing table | **Theo ứng dụng + chất lượng** |
| Quản lý | Từng thiết bị | Từng thiết bị | **Tập trung** |
| Chi phí | Thấp | Thấp | Cao |
| Phù hợp | < 5 site | 5–50 site | ⭐ > 10 site, nhiều ứng dụng |

---

## 6. Packet Flow — remote access SSL VPN

```text
1. Nhân viên mở AnyConnect, nhập URL công ty
2. Kết nối TLS tới VPN gateway qua TCP 443
3. Xác thực: username + password + MFA (OTP/push)
4. Gateway kiểm tra posture (máy có antivirus? OS vá chưa?)
5. Gateway cấp:
   - Một IP ảo từ pool VPN
   - Danh sách route cần đi qua tunnel (split tunnel)
   - DNS server nội bộ
6. Máy tạo interface ảo, cài route
7. Traffic tới mạng nội bộ → đi qua tunnel
   Traffic Internet → đi thẳng (split tunnel)
```

> 🔑 Bước 4 — **posture check** — là thứ phân biệt VPN doanh nghiệp với VPN cá nhân.
> Máy không đạt chuẩn *(thiếu bản vá, không có antivirus)* bị từ chối hoặc
> đưa vào **quarantine VLAN**.

---

## 7. Real-world Example

🏭 **Thiết kế VPN cho công ty 3 site + nhân viên làm từ xa**

```text
                    ┌─── Trụ sở Hà Nội ───┐
                    │  VPN Gateway (SSL)   │◀── 50 nhân viên remote
                    │  Dual-WAN            │
                    └──────────┬───────────┘
                     Site-to-Site VPN (GRE over IPsec)
              ┌────────────────┼────────────────┐
        ┌─────┴─────┐                     ┌─────┴─────┐
        │ CN Sài Gòn│                     │ CN Đà Nẵng│
        └───────────┘                     └───────────┘
```

| Thành phần | Giải pháp | Vì sao |
|---|---|---|
| Nối 3 site | **GRE over IPsec** | 3 site — chưa cần DMVPN/SD-WAN |
| Routing giữa site | **OSPF qua tunnel** | Tự hội tụ, không phải khai static |
| Nhân viên remote | **SSL VPN + MFA** | TCP 443 qua được mọi mạng |
| Tunnel mode | **Split tunnel** | Trải nghiệm tốt, giảm tải WAN trụ sở |
| Dự phòng | Dual-WAN + IP SLA | *(Lesson 39)* |

🏭 **Khi nào nên nâng lên DMVPN hoặc SD-WAN**

| Dấu hiệu | Giải pháp |
|---|---|
| Thêm site thứ 6, 7, 8… — cấu hình tay bắt đầu mệt | **DMVPN** |
| Chi nhánh phàn nàn Microsoft 365 chậm *(vòng qua trụ sở)* | **SD-WAN** *(local breakout)* |
| VoIP giữa chi nhánh kém, phải qua hub | DMVPN *(spoke-to-spoke)* hoặc SD-WAN |
| Muốn dùng Internet rẻ nhưng vẫn đảm bảo chất lượng | **SD-WAN** |
| Mỗi lần đổi chính sách phải sửa 15 router | **SD-WAN** |

🏭 **Sự cố: full tunnel làm nghẽn đường WAN khi cả công ty WFH**

```text
Trước dịch: 10 người dùng VPN, full tunnel → không vấn đề
Khi WFH:    200 người dùng VPN, full tunnel
            → mọi traffic Internet của 200 người đi QUA trụ sở
            → đường WAN 200 Mbps của trụ sở NGHẼN HOÀN TOÀN
            → kể cả người ngồi tại văn phòng cũng chậm
```

**Sửa:** chuyển sang **split tunnel** cho traffic Internet thông thường,
giữ full tunnel chỉ cho nhóm xử lý dữ liệu nhạy cảm.

🏭 **Lỗi thiết kế: VPN trỏ IP public của một WAN**

Đã nói ở [Lesson 40](./lesson-40-vpn-gre-ipsec.md) — khi WAN1 chết, VPN không lên lại.
Với remote access cũng vậy: nếu DNS của VPN gateway trỏ IP của WAN1,
nhân viên không kết nối được dù WAN2 đang sống.

> 🔧 Sửa: dùng **DNS với nhiều A record**, hoặc dịch vụ DNS có health check
> tự đổi bản ghi khi một IP chết.

---

## 8. Cisco CLI

> 💡 Site-to-Site đã có ở [Lesson 40](./lesson-40-vpn-gre-ipsec.md).
> Phần này là **remote access** và các lệnh kiểm tra.

```cisco
! ═══════ REMOTE ACCESS — IPsec (EzVPN, cách cũ) ═══════
R1(config)# aaa new-model
R1(config)# aaa authentication login VPN-AUTH local
R1(config)# aaa authorization network VPN-GROUP local
R1(config)# username vpnuser secret <pass>

R1(config)# ip local pool VPN-POOL 10.99.0.10 10.99.0.100

R1(config)# crypto isakmp client configuration group NHANVIEN
R1(config-isakmp-group)# key <group-key>
R1(config-isakmp-group)# pool VPN-POOL
R1(config-isakmp-group)# dns 10.0.50.10
R1(config-isakmp-group)# domain cty.local
R1(config-isakmp-group)# acl SPLIT-TUNNEL        ! split tunnel

! ACL định nghĩa mạng nào đi qua tunnel
R1(config)# ip access-list standard SPLIT-TUNNEL
R1(config-std-nacl)# permit 10.0.0.0 0.0.255.255   ! chỉ mạng nội bộ

! ═══════ KIỂM TRA ═══════
R1# show crypto session
R1# show crypto isakmp sa
R1# show crypto ipsec sa
R1# show ip local pool VPN-POOL
R1# show users

! ═══════ XEM TUNNEL SITE-TO-SITE ═══════
R1# show interface Tunnel0
R1# show ip route | include Tunnel
R1# show ip ospf neighbor               ! OSPF qua tunnel
```

> ⚠️ **SSL VPN** *(AnyConnect)* trên Cisco thường chạy trên **ASA/FTD firewall**
> hoặc **IOS-XE với WebVPN**, cấu hình chủ yếu qua **GUI**. Ở CCNA chỉ cần hiểu
> kiến trúc, không cần thuộc cú pháp.

**SD-WAN** cấu hình hoàn toàn qua **vManage GUI** — không có CLI truyền thống.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show crypto session
Interface: Tunnel0
Session status: UP-ACTIVE
Peer: 198.51.100.1 port 500
  Session ID: 0
  IKEv1 SA: local 203.0.113.1/500 remote 198.51.100.1/500 Active
  IPSEC FLOW: permit 47 host 203.0.113.1 host 198.51.100.1
        Active SAs: 2

Interface: Virtual-Access1
Session status: UP-ACTIVE
Peer: 42.117.x.x port 4500
  Username: vpnuser                          ← remote access
  IKEv1 SA: local 203.0.113.1/4500 remote 42.117.x.x/4500 Active
```

| Dấu hiệu | Ý nghĩa |
|---|---|
| `Interface: Tunnel0` | **Site-to-site** tunnel |
| `Interface: Virtual-Access1` | **Remote access** — mỗi phiên một virtual interface |
| `Username:` | ⭐ Chỉ remote access mới có — site-to-site xác thực bằng thiết bị |
| `port 4500` | Đang dùng **NAT-T** *(có NAT trên đường)* |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip local pool VPN-POOL
 Pool           Begin           End             Free  In use
 VPN-POOL       10.99.0.10      10.99.0.100       83      8
```

> 🔧 `In use` cho biết có bao nhiêu người đang kết nối VPN.
> `Free` gần 0 → **pool sắp hết**, nhân viên mới không vào được.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Cách kiểm chứng | Cách sửa |
|---|---|---|---|
| VPN chạy ở nhà, **không chạy ở quán cà phê** | Mạng đó chặn UDP 500/ESP | Thử cả 2 mạng | Chuyển sang **SSL VPN** *(TCP 443)* |
| Cả công ty WFH → đường WAN nghẽn | **Full tunnel** | `show interface` utilization | Chuyển **split tunnel** |
| Kết nối VPN được nhưng không vào được server nội bộ | Split tunnel ACL thiếu mạng đó | `route print` trên máy client | Thêm mạng vào ACL split tunnel |
| Nhân viên mới không kết nối được | **Pool VPN hết IP** | `show ip local pool` | Mở rộng pool |
| VPN rớt khi đổi Wi-Fi/4G | IP client đổi | — | Bật tính năng roaming của client |
| Spoke-to-spoke chậm | Traffic đi vòng qua hub | `traceroute` giữa 2 spoke | **DMVPN** hoặc SD-WAN |
| Microsoft 365 ở chi nhánh chậm | Traffic vòng qua trụ sở | `traceroute` tới Microsoft | **Local breakout** / SD-WAN |
| WAN1 chết, remote access không vào được | DNS trỏ IP của WAN1 | `nslookup vpn.cty.vn` | DNS nhiều A record + health check |

---

## 11. LAB

🧪 **LAB 72 — Site-to-site mở rộng + khảo sát remote access** → [`../labs/lab72-hub-spoke-remote.md`](../labs/lab72-hub-spoke-remote.md)

**Phần A — Hub-and-spoke 3 site** *(GNS3/EVE-NG)*

- Mở rộng LAB 71 thành 3 site: 1 hub + 2 spoke, mỗi spoke một tunnel về hub
- Chạy OSPF qua tunnel → verify mọi LAN thông nhau
- **Chứng minh hairpinning**: `traceroute` từ Spoke A sang Spoke B →
  thấy gói đi qua hub
- Đo độ trễ Spoke A ↔ Spoke B, so với Spoke A ↔ Hub

**Phần B — Khảo sát thực tế** *(không cần lab)*

1. Nếu công ty bạn có VPN: kiểm tra đang dùng **IPsec client hay SSL VPN**?
2. `route print` (Windows) khi đang bật VPN → **split tunnel hay full tunnel**?
   *(Có default route `0.0.0.0` qua interface VPN không?)*
3. Thử kết nối VPN từ mạng 4G và từ Wi-Fi công cộng → có khác nhau không?

**BREAK bắt buộc:** (1) tắt tunnel hub→spoke B, quan sát spoke A mất liên lạc với B
dù hai spoke vẫn có Internet; (2) sai split tunnel ACL → client không vào được một
mạng nội bộ cụ thể.

## 12. Challenge

1. Công ty 12 chi nhánh, hiện dùng hub-and-spoke. Chi nhánh phàn nàn gọi VoIP
   giữa các chi nhánh bị rè. Nêu nguyên nhân và 2 giải pháp.
2. Cả công ty chuyển sang WFH, đường WAN trụ sở nghẽn hoàn toàn. Nguyên nhân?
   Sửa thế nào? Đánh đổi là gì?
3. Nhân viên báo "VPN ở nhà chạy, ở khách sạn không chạy". Nguyên nhân?
   Giải pháp dài hạn?
4. SD-WAN khác WAN truyền thống ở điểm **cốt lõi** nào? Cho một ví dụ cụ thể.

<details>
<summary>Đáp án</summary>

**1.** Nguyên nhân: **hairpinning** — traffic VoIP giữa 2 chi nhánh phải đi
`Spoke A → Hub → Spoke B`, làm **độ trễ gấp đôi** và thêm jitter. VoIP cần
latency < 150 ms và jitter < 30 ms *(Lesson 28)* — đi vòng rất dễ vượt ngưỡng.

Hai giải pháp:

| Giải pháp | Chi tiết |
|---|---|
| **DMVPN** | Spoke tự tạo tunnel **trực tiếp** với nhau khi có traffic — chỉ cấu hình một lần trên mỗi spoke |
| **SD-WAN** | Tunnel full-mesh tự động + chọn đường theo chất lượng cho từng ứng dụng |

Với 12 chi nhánh, full mesh thủ công cần `12×11/2 = 66` tunnel — không khả thi.

**2.** Nguyên nhân: **full tunnel** — mọi traffic Internet của nhân viên remote
*(YouTube, Google, Facebook…)* đều đi **qua đường WAN của trụ sở** rồi mới ra Internet.
200 người × traffic Internet = nghẽn hoàn toàn.

Sửa: chuyển sang **split tunnel** — chỉ traffic tới mạng nội bộ đi qua VPN.

**Đánh đổi:**

| Mất gì | Bù bằng cách nào |
|---|---|
| Không còn thấy/lọc được traffic Internet của nhân viên | **EDR** trên máy người dùng |
| Máy nhiễm có thể là cầu nối vào mạng công ty | **Posture check** trước khi cho vào VPN |
| Mất khả năng áp chính sách duyệt web tập trung | DNS filtering trên máy client, hoặc **ZTNA** |

**3.** Nguyên nhân: khách sạn/mạng công cộng **chặn UDP 500 và ESP (protocol 50)** —
nhiều firewall chỉ mở các cổng web thông dụng.

| Giải pháp | Hiệu quả |
|---|---|
| Bật **NAT-T** *(UDP 4500)* | Giúp một phần — nhưng UDP 4500 cũng có thể bị chặn |
| ⭐ **Chuyển sang SSL VPN** *(TCP 443)* | **Giải pháp dài hạn** — cổng 443 gần như luôn mở ở mọi mạng |
| ZTNA | Cũng chạy TLS 443, còn cấp quyền chi tiết hơn |

**4.** Khác biệt cốt lõi:

```text
WAN truyền thống:  chọn đường theo ĐÍCH ĐẾN (routing table)
                   → chỉ biết đường còn sống hay chết

SD-WAN:            chọn đường theo ỨNG DỤNG + CHẤT LƯỢNG ĐƯỜNG thời gian thực
                   → biết đường đang tốt hay đang kém
```

**Ví dụ cụ thể:**

```text
Công ty có 2 đường: MPLS (ổn định, đắt) và FTTH (nhanh, rẻ, biến động)

WAN truyền thống:
  - Route table nói "đi FTTH" → MỌI thứ đi FTTH
  - FTTH jitter tăng lên 45 ms → cuộc gọi Teams rè
  - Router KHÔNG BIẾT GÌ, vẫn đẩy traffic qua FTTH

SD-WAN:
  - Đo liên tục: FTTH jitter 45 ms, MPLS jitter 8 ms
  - Nhận ra traffic này là Teams (ứng dụng thoại)
  - TỰ CHUYỂN cuộc gọi sang MPLS GIỮA CUỘC GỌI
  - Backup và tải file vẫn đi FTTH (rẻ, không cần ổn định)
  → Người dùng không biết gì đã xảy ra
```

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | Site-to-site vs remote access · SSL VPN port · split vs full tunnel | ⬜ |
| **L2** Explain | Giải thích SD-WAN khác WAN truyền thống ở điểm cốt lõi | ⬜ |
| **L3** Configure | Mở rộng site-to-site thành 3 site hub-and-spoke | ⬜ |
| **L4** Troubleshoot | "VPN ở nhà chạy, ở khách sạn không" → nguyên nhân và giải pháp | ⬜ |
| **L5** Design | Thiết kế VPN cho công ty 12 chi nhánh + 200 nhân viên remote | ⬜ |

## 14. Summary

**Key concepts**

- **Site-to-Site**: mạng↔mạng, router khởi tạo, trong suốt với người dùng
- **Remote Access**: người↔mạng, client khởi tạo, xác thực theo **tài khoản + MFA**
- ⭐ **SSL VPN thắng IPsec client** vì chạy **TCP 443** — qua được mọi mạng công cộng
- **ZTNA**: cấp quyền **từng ứng dụng**, "never trust, always verify"
- ⭐ **Split tunnel**: traffic Internet đi thẳng — trải nghiệm tốt, giảm tải WAN
- **Full tunnel**: mọi traffic qua công ty — kiểm soát tốt, nhưng nghẽn khi đông người
- **Hub-and-spoke** gây **hairpinning** — spoke-to-spoke đi vòng qua hub
- **Full mesh** cần `n(n−1)/2` tunnel — không scale
- **DMVPN** = mGRE + NHRP + IPsec → spoke tự tạo tunnel trực tiếp
- ⭐ **SD-WAN chọn đường theo ỨNG DỤNG + CHẤT LƯỢNG**, không chỉ theo đích đến
- **Local breakout**: chi nhánh ra thẳng Internet cho SaaS, không vòng qua trụ sở
- Ngưỡng thực tế: **> 10 site** thì SD-WAN đáng tiền

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show crypto session` | ⭐ Tổng quan mọi VPN — cả site-to-site lẫn remote access |
| `show ip local pool VPN-POOL` | Còn bao nhiêu IP cho người dùng remote |
| `ip local pool` + `crypto isakmp client configuration group` | Remote access IPsec |
| `acl SPLIT-TUNNEL` trong group | Định nghĩa mạng nào đi qua tunnel |
| `route print` *(trên client)* | Split tunnel hay full tunnel |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Full tunnel khi cả công ty WFH | Đường WAN trụ sở nghẽn hoàn toàn |
| Dùng IPsec client cho nhân viên hay đi công tác | Không kết nối được ở khách sạn/quán |
| Split tunnel ACL thiếu một mạng nội bộ | Nhân viên không vào được server đó |
| Hub-and-spoke với nhiều site có VoIP | Hairpinning làm rè cuộc gọi |
| Full mesh thủ công từ 6 site trở lên | Không quản nổi |
| DNS VPN gateway trỏ IP của một WAN | WAN đó chết là không ai kết nối được |
| Pool VPN quá nhỏ | Nhân viên mới không vào được |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 72: cả Phần A *(lab)* và Phần B *(khảo sát thực tế)*.
2. Chạy `route print` khi đang bật VPN công ty → xác định split hay full tunnel.
3. Vẽ sơ đồ VPN hiện tại của công ty bạn, chỉ ra điểm yếu *(hairpinning? SPOF?)*.
4. Trả lời: công ty bạn có bao nhiêu site? SD-WAN có đáng tiền không?

```markdown
- [YYYY-MM-DD] Lesson 41 — Site-to-Site, Remote Access, SD-WAN: DONE | cần ôn lại <điểm yếu>
```

---

## 🎉 Hết Phase 7 — và hết toàn bộ phần lý thuyết CCNA

```text
Phase 0 ✅  Phase 1 ✅  Phase 2 ✅  Phase 3 ✅
Phase 4 ✅  Phase 5 ✅  Phase 6 ✅  Phase 7 ✅
                     ↓
         📝 Mini Exam Phase 7
                     ↓
         🏁 FINAL CCNA PROJECT
```

1. Làm **[Mini Exam Phase 7](./review-phase07.md)**
2. Rồi bắt tay vào **[FINAL CCNA PROJECT](../labs/README.md#-final-ccna-project)** —
   thiết kế và triển khai network cho công ty 100–300 users, dùng **mọi thứ** bạn đã học.

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Site-to-site vs remote access, split vs full tunnel, SD-WAN khái niệm |
| 🔧 **Engineer** | Chọn SSL VPN cho người hay di chuyển; split tunnel cho WFH quy mô lớn |
| 🏭 **Production** | Hairpinning làm rè VoIP; full tunnel nghẽn WAN khi WFH; local breakout cho SaaS |

### 🔗 Liên kết

- ⬅️ [Lesson 40 — VPN, GRE, IPsec](./lesson-40-vpn-gre-ipsec.md)
- 📝 [Mini Exam Phase 7](./review-phase07.md)
- 🏁 [FINAL CCNA PROJECT](../labs/README.md#-final-ccna-project)
- 🔜 DMVPN, SD-WAN chi tiết: [`CCNP-Encor` Module 08](https://github.com/hiepnguyen775/CCNP-Encor)
