# LESSON 40 — VPN · GRE · IPsec ⭐

> ⚠️ **Packet Tracer không mô phỏng đầy đủ IPsec.** Lab lesson này phải làm trên
> **GNS3 hoặc EVE-NG**.

| | |
|---|---|
| **Phase** | 7 — WAN / Enterprise |
| **Thời lượng** | ~4 giờ |
| **Prerequisite** | [Lesson 27](../03-services/lesson-27-nat-nang-cao.md), [Lesson 36](../06-security/lesson-36-acl.md), [Lesson 39](./lesson-39-wan-concepts.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Giải thích **GRE cần IPsec** và **IPsec thiếu gì** so với GRE
- [ ] Mô tả IKE Phase 1 và Phase 2 — mỗi phase thương lượng gì
- [ ] Phân biệt **transport mode** và **tunnel mode**, **AH** và **ESP**
- [ ] Cấu hình GRE over IPsec site-to-site và verify
- [ ] Troubleshoot VPN theo thứ tự, không đoán mò

## 2. Prerequisite

- NAT và vì sao phải loại trừ traffic VPN *(Lesson 27)*
- ACL, wildcard mask *(Lesson 36)*
- MTU và MSS *(Lesson 39)*

---

## 3. Concept

### VPN là gì

**VPN** (Virtual Private Network) = tạo một **đường hầm riêng tư** chạy xuyên qua
một mạng công cộng *(thường là Internet)*.

| Loại | Dùng cho |
|---|---|
| **Site-to-Site** | Nối hai văn phòng — người dùng không biết gì |
| **Remote Access** | Nhân viên từ nhà/quán cà phê vào mạng công ty |

### GRE — đường hầm không mã hoá

**GRE** (Generic Routing Encapsulation) bọc một gói vào trong một gói IP khác.

```text
Gói gốc:        [ IP: 10.0.1.5 → 10.1.1.5 ][ payload ]
Sau khi bọc GRE:
[ IP mới: 203.0.113.1 → 198.51.100.1 ][ GRE ][ IP gốc ][ payload ]
   └── IP PUBLIC của 2 router ────┘          └── vẫn nguyên ──┘
```

| GRE làm được | GRE **không** làm được |
|---|---|
| ✅ Chở **multicast** *(→ chạy được OSPF/EIGRP qua tunnel)* | ❌ **Mã hoá** |
| ✅ Chở giao thức **non-IP** | ❌ Xác thực |
| ✅ Tạo topology logic độc lập với vật lý | ❌ Toàn vẹn dữ liệu |

### IPsec — mã hoá nhưng thiếu thứ khác

| IPsec làm được | IPsec **không** làm được |
|---|---|
| ✅ **Mã hoá** *(Confidentiality)* | ❌ Chở **multicast** |
| ✅ **Xác thực** *(Authentication)* | ❌ Chở giao thức non-IP |
| ✅ **Toàn vẹn** *(Integrity)* | ❌ → **Không chạy được OSPF/EIGRP qua tunnel** |
| ✅ Chống phát lại *(Anti-replay)* | |

### ⭐ Vì sao kết hợp: GRE over IPsec

```text
GRE   lo việc CHỞ  (multicast, routing protocol, non-IP)
IPsec lo việc BẢO VỆ (mã hoá, xác thực, toàn vẹn)

→ GRE over IPsec = chở được mọi thứ VÀ an toàn
```

> ⭐ Đây là câu trả lời cho câu hỏi phỏng vấn kinh điển:
> *"Vì sao không dùng IPsec một mình?"* → Vì **IPsec không chở được multicast**,
> nên **routing protocol không chạy qua tunnel được** — bạn phải khai static route
> cho mọi mạng ở xa, không scale.

### Hai thành phần của IPsec

| | **AH** (Authentication Header) | **ESP** (Encapsulating Security Payload) |
|---|---|---|
| Protocol number | **51** | **50** |
| Mã hoá | ❌ **Không** | ✅ **Có** |
| Xác thực + toàn vẹn | ✅ *(cả IP header)* | ✅ *(không gồm IP header ngoài)* |
| Qua NAT được? | ❌ **KHÔNG** — hash gồm IP header, NAT làm hỏng | ✅ Có *(với NAT-T)* |
| Thực tế | ⚠️ Gần như **không dùng** | ⭐ **Dùng ESP** |

> 🔑 **AH không qua được NAT** là lý do nó gần như tuyệt chủng. Mọi triển khai hiện đại
> dùng **ESP**, thường kèm **NAT-T** *(NAT Traversal — bọc ESP vào UDP 4500)*.

### Transport mode vs Tunnel mode

| | **Transport mode** | **Tunnel mode** |
|---|---|---|
| Bảo vệ gì | **Chỉ payload** | **Toàn bộ gói gốc** *(cả IP header)* |
| IP header mới | ❌ Không thêm | ✅ Thêm IP header mới |
| Dùng khi | Hai host nói chuyện trực tiếp · **GRE over IPsec** | **Site-to-site** thuần IPsec |

> 💡 Với **GRE over IPsec**, dùng **transport mode** là đủ — vì GRE đã thêm IP header rồi,
> không cần IPsec thêm một lớp nữa *(tiết kiệm 20 byte mỗi gói)*.

### IKE — thương lượng khoá

**IKE** (Internet Key Exchange) làm hai việc, qua **UDP 500** *(và UDP 4500 nếu có NAT-T)*.

#### Phase 1 — xây đường hầm quản lý (ISAKMP SA)

Thương lượng **5 thứ** — phải khớp cả hai đầu:

| # | Tham số | Lựa chọn phổ biến |
|:---:|---|---|
| 1 | **Encryption** | AES-256 |
| 2 | **Hash** | SHA-256 |
| 3 | **Authentication** | **Pre-shared key** *(PSK)* hoặc chứng chỉ RSA |
| 4 | **DH group** | 14 *(2048 bit)* trở lên |
| 5 | **Lifetime** | 86400 giây |

> 💡 Cách nhớ 5 tham số: **HAGLE** — **H**ash, **A**uthentication, **G**roup,
> **L**ifetime, **E**ncryption.

| Chế độ Phase 1 | Số gói | Đặc điểm |
|---|:---:|---|
| **Main mode** | 6 | An toàn hơn, giấu danh tính |
| **Aggressive mode** | 3 | Nhanh hơn, **lộ danh tính** |

#### Phase 2 — xây đường hầm dữ liệu (IPsec SA)

Thương lượng:

| Tham số | Nội dung |
|---|---|
| **Transform set** | Thuật toán mã hoá + hash cho dữ liệu |
| **Mode** | Transport hoặc Tunnel |
| **Proxy ACL** *(crypto ACL)* | **Traffic nào được đi vào tunnel** |
| Lifetime | 3600 giây |
| PFS | Perfect Forward Secrecy *(tuỳ chọn)* |

> ⭐ **Crypto ACL phải đối xứng ngược nhau** ở hai đầu:
> ```
> Site A: permit ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255
> Site B: permit ip 10.1.0.0 0.0.0.255 10.0.0.0 0.0.0.255
> ```
> Không đối xứng → **Phase 2 không lên**.

---

## 4. Why?

> **Vì sao không dùng leased line thay vì VPN qua Internet?**

| | Leased line / MPLS | VPN qua Internet |
|---|---|---|
| Chi phí | 💰💰💰 | 💰 *(rẻ hơn nhiều lần)* |
| Băng thông | Cố định, thường thấp | Cao hơn với cùng giá tiền |
| Triển khai | Vài tuần | **Vài giờ** |
| SLA | ✅ Cao | ❌ Best effort |
| Bảo mật | Cách ly vật lý | **Mã hoá** |
| Linh hoạt | Khó đổi | Thêm site rất nhanh |

> 🏭 Xu hướng rõ ràng: **doanh nghiệp chuyển từ MPLS sang Internet + VPN/SD-WAN.**
> Đổi lại SLA kém hơn — bù bằng **dual-WAN** *(Lesson 39)*.

> **Vì sao VPN qua NAT khó?**

```text
IPsec bảo vệ tính TOÀN VẸN của gói
   ↓
NAT SỬA ĐỔI gói (đổi IP, đổi port)
   ↓
→ Kiểm tra toàn vẹn THẤT BẠI
```

Giải pháp: **NAT-T** (NAT Traversal) — tự động phát hiện có NAT trên đường,
bọc gói ESP vào **UDP 4500** để NAT xử lý được như gói UDP thường.

---

## 5. How does it work? — tunnel lên từng bước

```text
1. Traffic khớp CRYPTO ACL → kích hoạt tunnel

2. IKE PHASE 1 (UDP 500)
   - Thương lượng HAGLE
   - Trao đổi khoá Diffie-Hellman
   - Xác thực nhau (PSK hoặc chứng chỉ)
   → ISAKMP SA được tạo (đường hầm QUẢN LÝ, hai chiều)

3. IKE PHASE 2 (chạy BÊN TRONG đường hầm Phase 1)
   - Thương lượng transform set
   - Thống nhất crypto ACL
   → IPsec SA được tạo (đường hầm DỮ LIỆU, MỖI CHIỀU MỘT SA)

4. Dữ liệu chạy, được mã hoá bằng ESP

5. Hết lifetime → thương lượng lại (rekey)
```

> 🔑 Chú ý: **Phase 1 tạo 1 SA hai chiều; Phase 2 tạo 2 SA, mỗi chiều một cái.**
> Vì vậy `show crypto ipsec sa` luôn hiển thị cả `inbound` và `outbound`.

### Vấn đề MTU — rất hay gặp

```text
Gói gốc:                    1500 byte
+ GRE header:               +24  = 1524
+ IPsec ESP (tunnel mode):  +~56 = 1580   ⚠️ VƯỢT MTU 1500!
```

**Hậu quả:** gói bị phân mảnh hoặc **drop im lặng** → triệu chứng đặc trưng:
**ping được, SSH được, nhưng web có ảnh lớn thì treo**.

**Sửa — hai dòng bắt buộc trên interface Tunnel:**

```cisco
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360
```

> ⭐ `ip tcp adjust-mss` là dòng **quan trọng nhất** — nó sửa trường MSS trong gói
> TCP SYN, buộc hai đầu thoả thuận gói nhỏ hơn ngay từ đầu. Không có nó, PMTUD
> phải làm việc, và PMTUD thường bị ACL chặn *(Lesson 36)*.

---

## 6. Packet Flow — gói đi qua GRE over IPsec

```text
PC A (10.0.0.5) → PC B (10.1.0.5)

1. PC A gửi: [IP 10.0.0.5 → 10.1.0.5][payload]
2. Router A: route table nói đi qua Tunnel0
3. GRE BỌC:  [IP 203.0.113.1 → 198.51.100.1][GRE][IP gốc][payload]
4. Khớp crypto ACL → IPsec MÃ HOÁ:
   [IP ngoài][ESP][█ GRE + IP gốc + payload đã mã hoá █][ESP trailer]
5. ⚠️ NAT: phải LOẠI TRỪ traffic này (Lesson 27)
6. Gửi qua Internet — ai bắt được chỉ thấy ESP giữa 2 IP public
7. Router B: giải mã ESP → gỡ GRE → [IP 10.0.0.5 → 10.1.0.5]
8. Route tới PC B
```

> 🔑 Bước 5 là lỗi phổ biến nhất khi triển khai VPN. Nếu traffic VPN bị NAT,
> source IP đổi thành IP public → **không khớp crypto ACL** → không được mã hoá →
> gửi thẳng ra Internet → tunnel không lên.

---

## 7. Real-world Example

🏭 **Cấu hình GRE over IPsec đầy đủ — hai site**

```cisco
! ══════════ ROUTER A (trụ sở, WAN 203.0.113.1) ══════════

! ───── Phase 1 ─────
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 86400
crypto isakmp key MyStr0ngK3y address 198.51.100.1

! ───── Phase 2 ─────
crypto ipsec transform-set TS-AES esp-aes 256 esp-sha256-hmac
 mode transport                       ! GRE đã có IP header rồi

crypto ipsec profile IPSEC-PROFILE
 set transform-set TS-AES

! ───── GRE Tunnel ─────
interface Tunnel0
 description VPN-TOI-CHI-NHANH-SG
 ip address 10.255.0.1 255.255.255.252
 ip mtu 1400                          ! ⚠️ BẮT BUỘC
 ip tcp adjust-mss 1360               ! ⚠️ BẮT BUỘC
 tunnel source GigabitEthernet0/1
 tunnel destination 198.51.100.1
 tunnel protection ipsec profile IPSEC-PROFILE

! ───── Routing qua tunnel ─────
router ospf 1
 network 10.255.0.1 0.0.0.0 area 0    ! OSPF chạy QUA tunnel — nhờ GRE
 network 10.0.0.0 0.0.0.255 area 0

! ───── LOẠI TRỪ traffic VPN khỏi NAT ─────
ip access-list extended NAT-ACL
 deny   ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255    ! ⚠️ ĐẶT TRƯỚC
 permit ip 10.0.0.0 0.0.0.255 any
ip nat inside source list NAT-ACL interface GigabitEthernet0/1 overload
```

Router B cấu hình đối xứng: đổi IP tunnel thành `10.255.0.2`,
`tunnel destination 203.0.113.1`, và NAT-ACL đảo ngược hai dải.

> 🔑 Dùng **`tunnel protection ipsec profile`** *(cách hiện đại)* thay vì
> `crypto map` *(cách cũ)*. Nó gọn hơn nhiều và không cần crypto ACL riêng —
> IPsec tự bảo vệ mọi thứ đi qua tunnel.

🏭 **Ba lỗi phổ biến nhất khi triển khai VPN**

| # | Lỗi | Triệu chứng | Sửa |
|:---:|---|---|---|
| **1** | **Không loại trừ traffic VPN khỏi NAT** | Tunnel không lên, hoặc lên rồi không có traffic | `deny` trong NAT-ACL, đặt **trước** `permit` |
| **2** | **Quên `ip tcp adjust-mss`** | Ping được, SSH được, **web có ảnh treo** | `ip mtu 1400` + `ip tcp adjust-mss 1360` |
| **3** | **ACL trên WAN chặn UDP 500 / ESP** | Phase 1 không lên | Permit UDP 500, UDP 4500, protocol 50 |

```cisco
! ACL trên WAN phải cho VPN đi qua
ip access-list extended TU-INTERNET
 permit udp host 198.51.100.1 any eq 500      ! IKE
 permit udp host 198.51.100.1 any eq 4500     ! NAT-T
 permit esp host 198.51.100.1 any             ! ESP = protocol 50
 ...
```

🏭 **VPN và dual-WAN — vấn đề ít ai nghĩ tới**

```text
VPN peer cấu hình: tunnel source Gi0/1 (WAN1)
→ WAN1 chết, traffic chuyển sang WAN2
→ NHƯNG tunnel vẫn gắn với IP của WAN1
→ VPN KHÔNG LÊN LẠI
```

Giải pháp:

| Cách | Chi tiết |
|---|---|
| `tunnel source Loopback0` | Dùng loopback làm nguồn — nhưng cần ISP route tới loopback *(hiếm)* |
| **Hai tunnel, hai peer** | Tunnel0 qua WAN1, Tunnel1 qua WAN2, dùng routing để chọn |
| **DMVPN / SD-WAN** | Giải pháp đúng cho nhiều site — học ở CCNP |

---

## 8. Cisco CLI

```cisco
! ═══════ PHASE 1 (ISAKMP) ═══════
R1(config)# crypto isakmp policy 10
R1(config-isakmp)# encryption aes 256
R1(config-isakmp)# hash sha256
R1(config-isakmp)# authentication pre-share
R1(config-isakmp)# group 14
R1(config-isakmp)# lifetime 86400
R1(config)# crypto isakmp key <key> address <peer-ip>

! ═══════ PHASE 2 ═══════
R1(config)# crypto ipsec transform-set TS esp-aes 256 esp-sha256-hmac
R1(cfg-crypto-trans)# mode transport          ! hoặc tunnel
R1(config)# crypto ipsec profile IPSEC-PROFILE
R1(ipsec-profile)# set transform-set TS
R1(ipsec-profile)# set pfs group14             ! tuỳ chọn, an toàn hơn

! ═══════ GRE TUNNEL + IPsec (cách hiện đại) ═══════
R1(config)# interface Tunnel0
R1(config-if)# ip address 10.255.0.1 255.255.255.252
R1(config-if)# ip mtu 1400
R1(config-if)# ip tcp adjust-mss 1360
R1(config-if)# tunnel source GigabitEthernet0/1
R1(config-if)# tunnel destination 198.51.100.1
R1(config-if)# tunnel protection ipsec profile IPSEC-PROFILE
R1(config-if)# keepalive 10 3                 ! phát hiện tunnel chết

! ═══════ IPsec THUẦN (cách cũ — crypto map) ═══════
R1(config)# ip access-list extended VPN-TRAFFIC
R1(config-ext-nacl)# permit ip 10.0.0.0 0.0.0.255 10.1.0.0 0.0.0.255
R1(config)# crypto map CMAP 10 ipsec-isakmp
R1(config-crypto-map)# set peer 198.51.100.1
R1(config-crypto-map)# set transform-set TS
R1(config-crypto-map)# match address VPN-TRAFFIC
R1(config)# interface GigabitEthernet0/1
R1(config-if)# crypto map CMAP

! ═══════ KIỂM TRA ═══════
R1# show crypto isakmp sa
R1# show crypto ipsec sa
R1# show crypto session
R1# show interface Tunnel0
R1# show ip route | include Tunnel

! ═══════ DEBUG (cẩn thận trên production) ═══════
R1# debug crypto isakmp
R1# debug crypto ipsec
R1# clear crypto isakmp
R1# clear crypto sa
R1# undebug all
```

| Lệnh | Lưu ý |
|---|---|
| `tunnel protection ipsec profile` | ⭐ Cách hiện đại — gọn hơn `crypto map` |
| `mode transport` | Dùng với GRE *(tiết kiệm 20 byte)* |
| `ip mtu 1400` + `ip tcp adjust-mss 1360` | ⭐ **Bắt buộc** — quên là web treo |
| `keepalive 10 3` | Tunnel tự down khi peer chết |
| `set pfs group14` | Perfect Forward Secrecy — khoá cũ lộ không giải mã được phiên mới |
| `clear crypto sa` | ⚠️ Ngắt tunnel tạm thời |

> **Khác biệt platform:** ASA firewall dùng cú pháp hoàn toàn khác
> *(`crypto ikev1 policy`, `tunnel-group`, `crypto map`)*. IOS-XE hỗ trợ cả
> IKEv1 và **IKEv2** *(`crypto ikev2 proposal` — hiện đại hơn, nên dùng)*.

---

## 9. Verification — theo đúng thứ tự

> 🔴 **Luôn kiểm tra Phase 1 trước Phase 2.** Phase 2 không thể lên nếu Phase 1 chưa lên.

```text
# output điển hình — tự verify trên lab của bạn
R1# show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id status
198.51.100.1    203.0.113.1     QM_IDLE           1001 ACTIVE
```

| `state` | Nghĩa |
|---|---|
| **`QM_IDLE`** | ✅ **Phase 1 ĐÃ LÊN**, đang chờ Quick Mode |
| `MM_NO_STATE` | ❌ Phase 1 **thất bại** — sai PSK, hoặc tham số không khớp |
| `MM_KEY_EXCH` | Đang trao đổi khoá — kẹt ở đây = sai PSK |
| `AG_INIT_EXCH` | Aggressive mode đang chạy |

```text
# output điển hình — tự verify trên lab của bạn
R1# show crypto ipsec sa | include pkts|peer|local ident|remote ident
   local  ident (addr/mask/prot/port): (10.0.0.0/255.255.255.0/0/0)
   remote ident (addr/mask/prot/port): (10.1.0.0/255.255.255.0/0/0)
   current_peer 198.51.100.1 port 500
    #pkts encaps: 18422, #pkts encrypt: 18422, #pkts digest: 18422
    #pkts decaps: 18390, #pkts decrypt: 18390, #pkts verify: 18390
```

**Đọc 4 con số này — đây là kỹ năng debug VPN quan trọng nhất:**

| Con số | Nghĩa | Chẩn đoán |
|---|---|---|
| `#pkts encaps` **tăng** | Đang **gửi** traffic vào tunnel ✅ | |
| `#pkts decaps` **tăng** | Đang **nhận** traffic từ tunnel ✅ | |
| `encaps` tăng, **`decaps` = 0** | ⚠️ Gửi được, **không nhận được** | Đầu kia không gửi về, hoặc ACL/firewall chặn chiều về |
| `encaps` = 0 | ⚠️ **Không có traffic nào vào tunnel** | Crypto ACL không khớp, hoặc routing sai, hoặc **NAT chưa loại trừ** |
| Cả hai = 0 | Tunnel lên nhưng chưa có traffic | Thử ping qua tunnel |

```text
# output điển hình — tự verify trên lab của bạn
R1# show crypto session
Interface: Tunnel0
Session status: UP-ACTIVE
Peer: 198.51.100.1 port 500
  Session ID: 0
  IKEv1 SA: local 203.0.113.1/500 remote 198.51.100.1/500 Active
  IPSEC FLOW: permit 47 host 203.0.113.1 host 198.51.100.1
        Active SAs: 2, origin: crypto map
```

> 🔧 `show crypto session` là lệnh **tổng quan nhanh nhất** — một dòng cho biết
> tunnel UP hay DOWN.

---

## 10. Troubleshooting — thứ tự 6 bước

> 🔴 Làm đúng thứ tự này. Đừng nhảy bước.

| # | Kiểm tra | Lệnh | Nếu fail |
|:---:|---|---|---|
| 1 | **Hai peer có ping được nhau không?** *(IP public)* | `ping <peer-ip>` | Vấn đề định tuyến/WAN — chưa phải VPN |
| 2 | **ACL/firewall có cho UDP 500, 4500, ESP không?** | `show access-lists` | Permit 3 thứ đó |
| 3 | **Phase 1 lên chưa?** | `show crypto isakmp sa` → `QM_IDLE` | Kiểm tra HAGLE + PSK hai đầu |
| 4 | **Phase 2 lên chưa?** | `show crypto ipsec sa` | Kiểm tra transform-set + crypto ACL đối xứng |
| 5 | **Có traffic vào tunnel không?** | `#pkts encaps` tăng? | Kiểm tra routing + **NAT exclusion** |
| 6 | **Có nhận được không?** | `#pkts decaps` tăng? | Kiểm tra chiều về ở đầu kia |

### Bảng triệu chứng

| Triệu chứng | Nguyên nhân phổ biến nhất |
|---|---|
| `MM_NO_STATE` | **Sai pre-shared key**, hoặc tham số Phase 1 không khớp |
| Phase 1 OK, Phase 2 không lên | **Crypto ACL không đối xứng**, hoặc transform-set lệch |
| Tunnel UP nhưng `encaps = 0` | **Traffic bị NAT**, hoặc routing không trỏ qua tunnel |
| `encaps` tăng, `decaps = 0` | Đầu kia chặn ESP, hoặc ACL chiều về |
| Ping được, **web có ảnh treo** | ⭐ **Thiếu `ip tcp adjust-mss`** |
| OSPF không lên qua tunnel | Dùng IPsec thuần *(không multicast)* → cần **GRE** |
| Tunnel lên rồi rớt định kỳ | Lifetime lệch, hoặc đường WAN chập chờn |
| Sau failover WAN, VPN không lên lại | `tunnel source` gắn với interface đã chết |

---

## 11. LAB

🧪 **LAB 71 — GRE over IPsec site-to-site** → [`../labs/lab71-gre-ipsec.md`](../labs/lab71-gre-ipsec.md)
> ⚠️ **Phải làm trên GNS3/EVE-NG** — Packet Tracer không mô phỏng đủ IPsec.

Yêu cầu tối thiểu:

- 2 router "site", 1 router giả lập "Internet" ở giữa, mỗi site có 1 LAN
- **Bước 1**: dựng **GRE tunnel thuần** → ping LAN-to-LAN được → chạy OSPF qua tunnel
  → chứng minh **GRE chở được multicast**
- **Bước 2**: thêm **IPsec protection** → verify Phase 1 `QM_IDLE`, Phase 2 có SA
- **Bước 3**: bắt gói trên "Internet" → chứng minh **chỉ thấy ESP**, không đọc được nội dung
- **BREAK bắt buộc:** (1) sai PSK một đầu → quan sát `MM_NO_STATE`;
  (2) không loại trừ NAT → quan sát `encaps = 0`;
  (3) bỏ `ip tcp adjust-mss` → tải file lớn qua tunnel, quan sát treo;
  (4) thử IPsec **thuần** (không GRE) → chứng minh OSPF không lên

## 12. Challenge

1. Vì sao không dùng IPsec một mình cho site-to-site? Nêu hậu quả cụ thể.
2. `show crypto isakmp sa` hiện `QM_IDLE` nhưng LAN hai bên không ping được nhau,
   và `#pkts encaps = 0`. Nêu 2 nguyên nhân.
3. VPN chạy tốt, ping OK, SSH OK, nhưng tải file lớn thì treo. Nguyên nhân? Sửa thế nào?
4. Dual-WAN + VPN: WAN1 chết, traffic chuyển WAN2 nhưng VPN không lên lại. Vì sao?

<details>
<summary>Đáp án</summary>

**1.** Vì **IPsec không chở được multicast**.

```text
Routing protocol (OSPF, EIGRP) dùng MULTICAST:
  OSPF → 224.0.0.5
  EIGRP → 224.0.0.10

IPsec thuần chỉ chở UNICAST
→ OSPF/EIGRP KHÔNG chạy được qua tunnel
```

**Hậu quả cụ thể:** bạn phải khai **static route cho mọi mạng ở xa**, trên **mọi site**.
Với 10 site × 5 subnet mỗi site = 45 static route trên mỗi router, và phải sửa tay
mỗi khi thêm subnet. **Không scale**.

GRE chở được multicast → routing protocol chạy được → route tự học, tự hội tụ.

**2.** Hai nguyên nhân, kiểm tra theo thứ tự:

| # | Nguyên nhân | Kiểm chứng | Sửa |
|:---:|---|---|---|
| **1** | **Traffic VPN bị NAT** | `show ip nat translations \| include 10.1.0` | `deny` trong NAT-ACL, đặt **trước** `permit`, rồi `clear ip nat translation *` |
| **2** | **Routing không trỏ qua tunnel** | `show ip route 10.1.0.0` | Thêm route qua Tunnel0, hoặc kiểm tra OSPF qua tunnel |

`#pkts encaps = 0` nghĩa là **không có gói nào được đưa vào tunnel** — vấn đề nằm
**trước** IPsec, ở tầng routing hoặc NAT.

**3.** Nguyên nhân: **MTU/MSS**.

```text
Gói gốc 1500 + GRE 24 + IPsec ~56 = ~1580 byte  >  MTU 1500
→ phải phân mảnh, hoặc bị drop
→ Ping (gói nhỏ) OK ✅
→ SSH (gói nhỏ) OK ✅
→ Tải file / web có ảnh (gói 1500) → TREO ❌
```

Sửa:

```cisco
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360
```

`ip tcp adjust-mss` quan trọng nhất — nó sửa MSS trong gói TCP SYN, buộc hai đầu
thoả thuận gói nhỏ ngay từ đầu, **không phụ thuộc PMTUD** *(vốn hay bị ACL chặn)*.

**4.** Vì `tunnel source GigabitEthernet0/1` **gắn cứng với WAN1**.

```text
WAN1 chết → Gi0/1 down → tunnel source không còn → Tunnel0 DOWN
Traffic chuyển sang WAN2 (route đã đổi)
NHƯNG tunnel vẫn cố dùng IP của Gi0/1 → không lên lại
```

Ba giải pháp:

| Giải pháp | Đánh đổi |
|---|---|
| `tunnel source Loopback0` | Cần ISP route tới loopback — hiếm khi có |
| **Hai tunnel**: Tunnel0 qua WAN1, Tunnel1 qua WAN2 | Dùng routing/track để chọn. Phức tạp hơn nhưng khả thi |
| **DMVPN** hoặc **SD-WAN** | ⭐ Giải pháp đúng cho nhiều site — học ở CCNP |

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | AH vs ESP · protocol number · UDP 500/4500 · HAGLE · transport vs tunnel | ⬜ |
| **L2** Explain | Giải thích vì sao cần **cả** GRE và IPsec | ⬜ |
| **L3** Configure | Dựng GRE over IPsec hai site, chạy OSPF qua tunnel | ⬜ |
| **L4** Troubleshoot | Chạy đủ 6 bước troubleshoot cho một VPN không lên | ⬜ |
| **L5** Design | Thiết kế VPN cho 1 trụ sở + 3 chi nhánh, có dual-WAN | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **GRE chở được multicast** *(→ routing protocol chạy qua tunnel)* nhưng **không mã hoá**
- ⭐ **IPsec mã hoá** nhưng **không chở được multicast**
- ⭐ → **GRE over IPsec**: GRE lo việc chở, IPsec lo việc bảo vệ
- **ESP** *(protocol 50)* dùng thực tế · **AH** *(51)* không qua được NAT, đã tuyệt chủng
- **NAT-T**: bọc ESP vào **UDP 4500** để qua NAT
- **IKE Phase 1** *(UDP 500)*: thương lượng **HAGLE**, tạo ISAKMP SA *(1 SA hai chiều)*
- **IKE Phase 2**: transform set + crypto ACL, tạo IPsec SA *(2 SA, mỗi chiều một)*
- **Crypto ACL phải đối xứng ngược** ở hai đầu
- **Transport mode** dùng với GRE · **Tunnel mode** cho IPsec thuần
- ⭐ **`ip mtu 1400` + `ip tcp adjust-mss 1360`** — quên là web treo
- ⭐ **Phải loại trừ traffic VPN khỏi NAT**
- ACL trên WAN phải permit **UDP 500, UDP 4500, ESP (protocol 50)**

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `crypto isakmp policy` + `crypto isakmp key` | Phase 1 |
| `crypto ipsec transform-set` + `crypto ipsec profile` | Phase 2 |
| `tunnel protection ipsec profile X` | ⭐ Cách hiện đại |
| `ip mtu 1400` + `ip tcp adjust-mss 1360` | ⭐ **Bắt buộc** |
| `show crypto isakmp sa` | ⭐ Phase 1 — tìm `QM_IDLE` |
| `show crypto ipsec sa` | ⭐ Phase 2 — đọc `#pkts encaps/decaps` |
| `show crypto session` | Tổng quan nhanh |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Không loại trừ traffic VPN khỏi NAT | Tunnel không lên, hoặc `encaps = 0` |
| Quên `ip tcp adjust-mss` | Ping được, **web có ảnh treo** |
| ACL WAN chặn UDP 500 / ESP | Phase 1 không lên |
| Crypto ACL không đối xứng | Phase 2 không lên |
| Dùng IPsec thuần rồi mong OSPF chạy | IPsec không chở multicast |
| PSK khác nhau hai đầu | `MM_NO_STATE` |
| `tunnel source` gắn interface WAN1 | VPN không lên lại sau failover |
| Dùng AH | Không qua được NAT |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 71 trên GNS3/EVE-NG với đủ 4 lỗi BREAK.
2. Bắt gói trên "Internet" bằng Wireshark → chụp lại màn hình chứng minh
   **chỉ thấy ESP**, không đọc được nội dung.
3. Học thuộc **6 bước troubleshoot VPN** — viết ra giấy không nhìn.
4. Tính: gói 1500 byte + GRE + IPsec tunnel mode = bao nhiêu byte? Vượt MTU bao nhiêu?

```markdown
- [YYYY-MM-DD] Lesson 40 — VPN, GRE, IPsec: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | GRE vs IPsec, AH vs ESP, IKE 2 phase, HAGLE, transport vs tunnel |
| 🔧 **Engineer** | `tunnel protection` thay `crypto map`; MTU/MSS; 6 bước troubleshoot |
| 🏭 **Production** | NAT exclusion là lỗi số 1; MSS gây "web treo"; VPN + dual-WAN cần thiết kế riêng |

### 🔗 Liên kết

- ⬅️ [Lesson 39 — WAN concepts & failover](./lesson-39-wan-concepts.md)
- ➡️ [Lesson 41 — Site-to-Site vs Remote Access, SD-WAN](./lesson-41-site-to-site-sdwan.md)
- 📚 NAT exclusion: [Lesson 27](../03-services/lesson-27-nat-nang-cao.md)
- 🔜 DMVPN, FlexVPN: [`CCNP-Encor` Module 08](https://github.com/hiepnguyen775/CCNP-Encor)
