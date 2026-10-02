# LESSON 16 — RSTP · PortFast · BPDU Guard · Root Guard

> 📌 Lesson 15 cho bạn STP cổ điển — hội tụ **50 giây**.
> Lesson này đưa con số đó xuống **dưới 1 giây**, và bảo vệ cây STP khỏi bị phá.

| | |
|---|---|
| **Phase** | 1 — Switching |
| **Thời lượng** | ~2.5 giờ |
| **Prerequisite** | [Lesson 15](./lesson-15-stp.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Giải thích RSTP nhanh hơn STP **nhờ cơ chế gì**, không chỉ nói "nó nhanh hơn"
- [ ] Ánh xạ được port role và port state của RSTP sang STP cổ điển
- [ ] Biết đặt PortFast ở đâu, **và vì sao bắt buộc đi kèm BPDU Guard**
- [ ] Phân biệt **BPDU Guard** và **Root Guard** — hai thứ rất hay bị nhầm
- [ ] Khôi phục được port `err-disabled`

## 2. Prerequisite

- Bridge ID, root/designated port, port state, BPDU *(Lesson 15)*
- Access port vs trunk port *(Lesson 13)*

---

## 3. Concept

### RSTP — IEEE 802.1w

**Rapid Spanning Tree Protocol** là STP được viết lại để hội tụ nhanh.
Nó **tương thích ngược** — RSTP và STP chạy chung được, nhưng khi đó đoạn mạng
có STP cổ điển sẽ tụt về tốc độ cũ.

| | **STP (802.1D)** | **RSTP (802.1w)** |
|---|---|---|
| Hội tụ khi đứt link | 30–50 giây | **< 1 giây** (thường vài trăm ms) |
| Port state | 5 (Blocking, Listening, Learning, Forwarding, Disabled) | **3** (Discarding, Learning, Forwarding) |
| Port role | Root, Designated, Blocked | Root, Designated, **Alternate**, **Backup** |
| Ai sinh BPDU | Chỉ root | **Mọi switch** gửi BPDU mỗi 2 giây |
| Mất BPDU bao lâu thì phản ứng | 20 giây (max age) | **3 × hello = 6 giây** |
| Cơ chế hội tụ | Chờ timer | **Proposal / Agreement** (bắt tay) |

### Vì sao RSTP nhanh — ba thay đổi

| # | Thay đổi | Hiệu quả |
|:---:|---|---|
| **1** | **Mọi switch tự sinh BPDU** (không chỉ chuyển tiếp của root) | Phát hiện mất láng giềng sau **6 giây** thay vì 20 |
| **2** | **Proposal/Agreement** — hai switch bắt tay trực tiếp để đồng ý ai forward | Không phải chờ Listening + Learning (30 giây) |
| **3** | **Alternate port có sẵn** — đã biết trước đường dự phòng | Link chết → chuyển sang **ngay lập tức**, không tính lại từ đầu |

> 🔑 Thay đổi **số 3** là then chốt. STP cổ điển khi đứt link phải **tính lại cả cây**.
> RSTP đã **giữ sẵn** một port Alternate biết rõ đường về root — chỉ việc mở nó ra.

### Port Role của RSTP

| Role | Nghĩa | State |
|---|---|---|
| **Root** | Đường tốt nhất về root bridge | Forwarding |
| **Designated** | Forward cho segment này | Forwarding |
| **Alternate** | **Đường dự phòng về root** *(qua switch khác)* | Discarding |
| **Backup** | Dự phòng cho chính segment này *(hiếm — chỉ khi dùng hub)* | Discarding |

> 💡 Phân biệt Alternate và Backup:
> **Alternate** = đường khác **tới root**. **Backup** = port thừa trên **cùng một segment**.
> Trong mạng hiện đại (không hub) gần như chỉ gặp Alternate.

### Port Type — RSTP phân loại link

| Type | Khi nào | Hành vi |
|---|---|---|
| **Point-to-point** | Link full-duplex giữa 2 switch | Dùng proposal/agreement → **nhanh** |
| **Edge** | Port nối thiết bị đầu cuối *(= PortFast)* | **Forwarding ngay**, không tham gia tính cây |
| **Shared** | Half-duplex *(hub)* | Tụt về hành vi STP cổ điển — chậm |

> ⚠️ Port half-duplex làm RSTP mất tác dụng. Đây là một lý do nữa để **không bao giờ
> ép half-duplex** trên switch hiện đại.

### PortFast

```cisco
SW1(config-if)# spanning-tree portfast
```

Cho port **nhảy thẳng vào Forwarding**, bỏ qua Listening/Learning.

| Có PortFast | Không có PortFast |
|---|---|
| PC cắm vào → có mạng **ngay** | Đợi **30 giây** mới forward |
| DHCP chạy được ngay | DHCP thường **timeout** trước khi port lên |

> ⚠️ **PortFast chỉ dùng cho port nối thiết bị đầu cuối** (PC, máy in, server, IP phone).
> Đặt nhầm lên port nối switch khác → **tạo loop tức thì**, vì port forward ngay
> mà chưa kịp tính STP.

### BPDU Guard — người bảo vệ của PortFast

```cisco
SW1(config-if)# spanning-tree bpduguard enable
```

**Logic:** port PortFast nối PC → PC **không bao giờ** gửi BPDU.
Nếu port đó **nhận được BPDU** → có switch cắm vào → **nguy cơ loop** → **tắt port ngay**
(`err-disabled`).

> ⭐ **PortFast và BPDU Guard luôn đi cặp.** Dùng PortFast mà không có BPDU Guard
> là tự mở cửa cho loop. Coi như một lệnh gồm hai dòng.

### Root Guard — bảo vệ vị trí root

```cisco
SW1(config-if)# spanning-tree guard root
```

**Logic:** port này **không được phép** dẫn tới root bridge. Nếu nhận BPDU "tốt hơn"
(Bridge ID thấp hơn root hiện tại) → port vào `root-inconsistent` (block),
**nhưng không tắt port**.

### BPDU Guard vs Root Guard — bảng phân biệt

| | **BPDU Guard** | **Root Guard** |
|---|---|---|
| Đặt ở đâu | Port **access** (nối PC) | Port **trunk** hướng xuống switch access |
| Kích hoạt khi | Nhận **bất kỳ** BPDU nào | Nhận BPDU **tốt hơn** root hiện tại |
| Hậu quả | Port **`err-disabled`** — chết hẳn | Port **`root-inconsistent`** — block tạm |
| Tự hồi phục? | ❌ Phải can thiệp *(hoặc bật errdisable recovery)* | ✅ **Tự mở lại** khi BPDU xấu ngừng |
| Chống gì | Ai đó cắm switch vào port người dùng | Switch lạ cướp vị trí root |

> 🔑 Cách nhớ: **BPDU Guard chống *có* BPDU. Root Guard chống BPDU *quá tốt*.**

### Loop Guard & BPDU Filter — bổ sung

| Tính năng | Chống gì |
|---|---|
| **Loop Guard** | Port **ngừng nhận** BPDU (do lỗi một chiều) mà lại chuyển sang forwarding → gây loop |
| **BPDU Filter** | **Không gửi và không nhận** BPDU trên port đó. ⚠️ **Rất nguy hiểm** — vô hiệu hoá STP, chỉ dùng khi thật sự hiểu |

---

## 4. Why?

> **Vì sao 50 giây là không chấp nhận được?**

| Ứng dụng | 50 giây gián đoạn nghĩa là |
|---|---|
| Cuộc gọi VoIP | **Rớt cuộc gọi** |
| Phiên SSH/RDP | Đứt session, mất việc đang làm |
| Kết nối database | Timeout, transaction rollback |
| Người dùng | "Mạng công ty lại sập rồi" |

> **Vì sao PortFast không bật mặc định cho mọi port?**

Vì switch **không biết** port nào nối PC, port nào nối switch khác. Bật nhầm trên port
uplink → loop ngay khi cắm. Cisco chọn mặc định an toàn, để bạn khai báo chủ động.

> **Vì sao Root Guard quan trọng?**

Bất kỳ ai cắm một switch cũ vào mạng — nếu switch đó có MAC thấp — nó **trở thành root**.
Toàn bộ traffic của công ty sẽ đi vòng qua con switch rẻ tiền đó. Mạng vẫn "chạy",
chỉ là chậm một cách khó hiểu.

---

## 5. How does it work? — Proposal/Agreement

Đây là cơ chế làm RSTP nhanh. Khi một link point-to-point vừa lên:

```text
SW-A (gần root hơn)                    SW-B
      │                                  │
      │──── BPDU: "Proposal" ───────────▶│   "Tôi muốn port này forwarding"
      │                                  │
      │                          SW-B: SYNC —
      │                          chặn tạm MỌI port designated khác
      │                          của nó (để chắc chắn không loop)
      │                                  │
      │◀─── BPDU: "Agreement" ───────────│   "OK, bạn forward đi"
      │                                  │
      │══ Cả hai FORWARDING ngay ════════│   < 1 giây
```

So với STP cổ điển: port phải nằm im qua Listening (15s) → Learning (15s)
**chỉ để chờ cho chắc**. RSTP thay việc *chờ* bằng việc *hỏi trực tiếp*.

> 🔑 Điểm tinh tế: bước **SYNC** là lý do cơ chế này an toàn. SW-B tự chặn các port
> khác của nó trước khi đồng ý — đảm bảo không có đường vòng nào mở ra cùng lúc.
> Quá trình này lan truyền từ root ra ngoài như một làn sóng.

---

## 6. Packet Flow — err-disabled do BPDU Guard

```text
1. Port Gi1/0/5 có PortFast + BPDU Guard, đang nối PC-A → Forwarding
2. Người dùng rút PC, cắm một switch mini để "có thêm cổng"
3. Switch mini gửi BPDU ra mọi port (mọi switch đều gửi BPDU)
4. Gi1/0/5 NHẬN được BPDU
5. BPDU Guard kích hoạt → port vào err-disabled NGAY
6. Log:
```

```text
# output điển hình — tự verify trên lab của bạn
%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port GigabitEthernet1/0/5 with BPDU Guard enabled. Disabling port.
%PM-4-ERR_DISABLE: bpduguard error detected on Gi1/0/5, putting Gi1/0/5 in err-disable state
```

```text
7. Port tắt hẳn. Người dùng mất mạng.
8. Phải có người xử lý — HOẶC bật errdisable recovery để tự mở lại sau N giây
```

> 🏭 Đây là hành vi **đúng như thiết kế**: thà một người mất mạng còn hơn cả công ty
> sập vì loop.

---

## 7. Real-world Example

🏭 **Cấu hình chuẩn cho port người dùng** — nên áp dụng cho mọi switch access:

```cisco
SW-ACC1(config)# interface range GigabitEthernet1/0/1 - 44
SW-ACC1(config-if-range)# description USER-PORT
SW-ACC1(config-if-range)# switchport mode access
SW-ACC1(config-if-range)# switchport access vlan 10
SW-ACC1(config-if-range)# spanning-tree portfast
SW-ACC1(config-if-range)# spanning-tree bpduguard enable
```

Hoặc bật toàn cục cho **mọi** access port (gọn hơn nhiều):

```cisco
SW-ACC1(config)# spanning-tree portfast default
SW-ACC1(config)# spanning-tree portfast bpduguard default
```

> 🔧 Hai dòng toàn cục này chỉ áp dụng cho port ở chế độ **access**, không áp dụng cho
> trunk — nên khá an toàn. Đây là cách nhiều doanh nghiệp làm.

🏭 **Errdisable recovery — giảm việc cho helpdesk**

```cisco
SW1(config)# errdisable recovery cause bpduguard
SW1(config)# errdisable recovery cause psecure-violation
SW1(config)# errdisable recovery interval 300        ! tự mở lại sau 5 phút
```

Port tự mở lại sau 5 phút. Nếu nguyên nhân vẫn còn → lại bị tắt. Người dùng rút switch
lạ ra là mạng tự hồi — không cần gọi IT.

> ⚠️ Đánh đổi: nếu nguyên nhân chưa được xử lý, port sẽ bật-tắt lặp lại.
> Phải **theo dõi log**, đừng bật rồi quên.

🏭 **Root Guard đặt ở đâu**

```cisco
! Trên switch DISTRIBUTION, ở các port hướng XUỐNG access
SW-DIST1(config)# interface range GigabitEthernet1/0/1 - 10
SW-DIST1(config-if-range)# description TO-ACCESS-SWITCHES
SW-DIST1(config-if-range)# spanning-tree guard root
```

Logic thiết kế: root bridge **phải** nằm ở core/distribution. Mọi BPDU tốt hơn đến từ
hướng access đều là bất thường → chặn.

> ⚠️ **Không** đặt Root Guard trên port hướng **lên** core — bạn sẽ tự chặn đường về root thật.

---

## 8. Cisco CLI

```cisco
! ═══════ BẬT RSTP — nên làm trên MỌI switch ═══════
SW1(config)# spanning-tree mode rapid-pvst

! ═══════ PORTFAST + BPDU GUARD ═══════
! Cách 1 — từng port
SW1(config)# interface GigabitEthernet1/0/5
SW1(config-if)# spanning-tree portfast
SW1(config-if)# spanning-tree bpduguard enable

! Cách 2 — toàn cục cho mọi access port (gọn hơn)
SW1(config)# spanning-tree portfast default
SW1(config)# spanning-tree portfast bpduguard default

! PortFast cho TRUNK (chỉ dùng với port nối server ảo hoá/hypervisor)
SW1(config-if)# spanning-tree portfast trunk

! ═══════ ROOT GUARD ═══════
SW1(config)# interface GigabitEthernet1/0/1
SW1(config-if)# spanning-tree guard root

! ═══════ LOOP GUARD ═══════
SW1(config)# spanning-tree loopguard default        ! toàn cục
SW1(config-if)# spanning-tree guard loop            ! từng port

! ═══════ ERRDISABLE RECOVERY ═══════
SW1(config)# errdisable recovery cause bpduguard
SW1(config)# errdisable recovery interval 300

! ═══════ KHÔI PHỤC PORT BẰNG TAY ═══════
SW1(config)# interface GigabitEthernet1/0/5
SW1(config-if)# shutdown
SW1(config-if)# no shutdown

! ═══════ KIỂM TRA ═══════
SW1# show spanning-tree summary
SW1# show spanning-tree interface Gi1/0/5 detail
SW1# show interfaces status err-disabled
SW1# show errdisable recovery
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `spanning-tree mode rapid-pvst` | Bật RSTP | **Nên bật mọi nơi**. NX-OS mặc định đã có |
| `spanning-tree portfast` | Forwarding ngay | ⚠️ **Chỉ** port nối thiết bị đầu cuối |
| `spanning-tree bpduguard enable` | Tắt port khi nhận BPDU | **Luôn đi kèm** PortFast |
| `spanning-tree guard root` | Chặn BPDU tốt hơn | Đặt ở port hướng **xuống** access |
| `spanning-tree portfast trunk` | PortFast trên trunk | Chỉ cho port nối hypervisor — **không** nối switch |
| `errdisable recovery cause X` | Tự mở lại port | Nhớ theo dõi log |

> **Khác biệt platform:** NX-OS dùng `spanning-tree port type edge` thay cho `portfast`,
> và `spanning-tree port type edge trunk` cho trunk. Mặc định NX-OS đã là Rapid-PVST+.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: VLAN0010, VLAN0030
EtherChannel misconfig guard      is enabled
Extended system ID                is enabled
Portfast Default                  is enabled
Portfast BPDU Guard Default       is enabled
Loopguard Default                 is disabled
UplinkFast                        is disabled
BackboneFast                      is disabled
```

**Đọc gì:** dòng `Switch is in rapid-pvst mode` xác nhận RSTP đang chạy.
Hai dòng `Portfast ... Default is enabled` xác nhận đã bật toàn cục.

```text
# output điển hình — tự verify trên lab của bạn
SW1# show spanning-tree vlan 10

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi1/0/1          Root FWD 4         128.1    P2p
Gi1/0/2          Altn BLK 4         128.2    P2p
Gi1/0/5          Desg FWD 4         128.5    P2p Edge
Gi1/0/6          Desg FWD 4         128.6    P2p Edge
```

| Cột `Type` | Nghĩa |
|---|---|
| `P2p` | Point-to-point — dùng proposal/agreement, hội tụ nhanh |
| `P2p Edge` | **PortFast đang bật** trên port này ✅ |
| `Shared` | Half-duplex — ⚠️ tụt về tốc độ STP cổ điển |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces status err-disabled
Port      Name               Status       Reason               Err-disabled Vlans
Gi1/0/5   USER-PORT          err-disabled bpduguard
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show errdisable recovery
ErrDisable Reason     Timer Status
-----------------     --------------
bpduguard             Enabled
psecure-violation     Enabled

Timer interval: 300 seconds

Interfaces that will be enabled at the next timeout:
Interface      Errdisable reason     Time left(sec)
Gi1/0/5        bpduguard             217
```

| Dấu hiệu | Chẩn đoán |
|---|---|
| `Reason: bpduguard` | **Có switch cắm vào port người dùng** |
| `Reason: psecure-violation` | Port Security — MAC lạ *(Lesson 17)* |
| `Reason: link-flap` | Cáp lỏng, link lên xuống liên tục |
| `root-inconsistent` trong `show spanning-tree` | **Root Guard** đã chặn một BPDU tốt hơn |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| PC đợi 30s mới có mạng | **Thiếu PortFast** | `show spanning-tree interface <int>` — không thấy `Edge` | `spanning-tree portfast` |
| PC không nhận được IP (DHCP timeout) | Cùng nguyên nhân trên | Như trên | Như trên |
| Port đột nhiên `err-disabled` sau khi user cắm gì đó | **BPDU Guard** kích hoạt | `show interfaces status err-disabled` | Gỡ thiết bị lạ, `shut`/`no shut` |
| Port `root-inconsistent` | **Root Guard** chặn BPDU tốt hơn | `show spanning-tree inconsistentports` | Tìm switch lạ vừa cắm vào |
| Hội tụ vẫn chậm dù đã bật RSTP | Có switch chạy STP cổ điển trong mạng | `show spanning-tree summary` trên mọi switch | Bật `rapid-pvst` ở tất cả |
| Port hiện `Shared` thay vì `P2p` | Đang chạy **half-duplex** | `show interfaces status` | Sửa duplex về full/auto |
| Bật PortFast trên uplink → mạng sập | **Loop** — PortFast trên port nối switch | `show spanning-tree` | Gỡ PortFast khỏi port đó ngay |
| Port bật-tắt lặp lại | `errdisable recovery` bật nhưng nguyên nhân chưa xử lý | `show errdisable recovery`, `show logging` | Xử lý gốc rồi mới bật recovery |

---

## 11. LAB

🧪 **LAB 14 — RSTP, PortFast, BPDU Guard — đo thời gian hội tụ** → [`../labs/lab14-rstp-bpduguard.md`](../labs/lab14-rstp-bpduguard.md)

Yêu cầu tối thiểu:

- 3 switch nối vòng, bật `rapid-pvst`, chỉ định root
- Bật PortFast + BPDU Guard trên port nối PC. Dùng **stopwatch** đo thời gian PC có mạng:
  trước và sau khi bật PortFast
- Rút một uplink, **bấm giờ** thời gian hội tụ. So sánh `pvst` và `rapid-pvst`
- Bật Root Guard trên port hướng xuống, rồi cắm một switch có priority thấp vào →
  quan sát `root-inconsistent`
- **BREAK bắt buộc:** (1) bật PortFast trên port trunk nối switch khác → quan sát loop;
  (2) cắm switch vào port có BPDU Guard → quan sát err-disabled rồi tự khôi phục;
  (3) ép một port về half-duplex → quan sát `Type` đổi thành `Shared`

## 12. Challenge

1. Vì sao RSTP phát hiện mất láng giềng sau **6 giây** mà STP cổ điển cần **20 giây**?
2. Bạn bật PortFast trên port nối một server VMware ESXi có nhiều VM. Có an toàn không?
   Nên dùng lệnh nào?
3. Một port đang `root-inconsistent`. Bạn rút thiết bị gây ra nó. Port có tự mở lại không?
   So sánh với port `err-disabled` do BPDU Guard.
4. Mạng đã bật `rapid-pvst` trên tất cả switch nhưng hội tụ vẫn mất ~30 giây. Nghi gì?

<details>
<summary>Đáp án</summary>

**1.** Vì **ai sinh BPDU** khác nhau:

| | STP cổ điển | RSTP |
|---|---|---|
| Ai tạo BPDU | **Chỉ root bridge**; switch khác chỉ chuyển tiếp | **Mọi switch** tự tạo, mỗi 2 giây |
| Mất bao lâu để biết láng giềng chết | Chờ hết **max age = 20 giây** | **3 × hello = 6 giây** |

RSTP coi BPDU như một **keepalive giữa hai láng giềng trực tiếp**, nên mất 3 cái liên tiếp
là biết ngay. STP phải chờ thông tin cũ từ root hết hạn.

**2.** **Không an toàn** nếu dùng `spanning-tree portfast` thường — port nối ESXi thường là
**trunk** (chở nhiều VLAN cho các VM), và PortFast thường chỉ áp dụng cho access port.

Dùng:

```cisco
SW1(config-if)# spanning-tree portfast trunk
SW1(config-if)# spanning-tree bpduguard enable
```

An toàn vì: vSwitch của ESXi **không gửi BPDU** và **không forward BPDU** giữa các uplink
theo mặc định — nó không tạo loop. BPDU Guard vẫn nên bật để phòng trường hợp ai đó
cấu hình sai hypervisor.

**3.** **Có, Root Guard tự mở lại.**

| | Root Guard | BPDU Guard |
|---|---|---|
| Trạng thái | `root-inconsistent` (block tạm) | `err-disabled` (tắt hẳn) |
| Khi nguyên nhân mất đi | **Tự động** về Forwarding | **Không** tự hồi |
| Cần can thiệp? | Không | `shut`/`no shut`, hoặc bật `errdisable recovery` |

Root Guard liên tục theo dõi BPDU; ngừng nhận BPDU tốt hơn thì mở lại. BPDU Guard
thì đưa port vào err-disable — một trạng thái cần hành động của con người (hoặc timer).

**4.** Ba khả năng, kiểm tra theo thứ tự:

| # | Nghi ngờ | Kiểm chứng |
|:---:|---|---|
| 1 | Có **một** switch (hoặc thiết bị non-Cisco) vẫn chạy STP cổ điển → cả đoạn mạng đó tụt về 802.1D | `show spanning-tree summary` trên **từng** switch |
| 2 | Link đang **half-duplex** → port type `Shared` → RSTP mất tác dụng | `show spanning-tree vlan X` xem cột `Type` |
| 3 | Thời gian "chậm" thực ra là **DHCP/ARP timeout** của client, không phải STP | Ping liên tục trong lúc rút link, đo đúng thời gian mất gói |

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 port state RSTP · 4 port role · BPDU Guard vs Root Guard | ⬜ |
| **L2** Explain | Giải thích proposal/agreement và vì sao nó thay được timer | ⬜ |
| **L3** Configure | Bật RSTP + PortFast + BPDU Guard + Root Guard đúng chỗ | ⬜ |
| **L4** Troubleshoot | Port `err-disabled` → tìm nguyên nhân và khôi phục | ⬜ |
| **L5** Design | Viết "config chuẩn STP" cho access switch và distribution switch | ⬜ |

## 14. Summary

**Key concepts**

- **RSTP (802.1w)**: hội tụ **< 1 giây** thay vì 30–50 giây
- Nhanh nhờ 3 thứ: mọi switch tự sinh BPDU · **proposal/agreement** · **Alternate port có sẵn**
- Port state RSTP: **Discarding → Learning → Forwarding** (3 thay vì 5)
- Port role: Root · Designated · **Alternate** (dự phòng về root) · Backup
- Port type: `P2p` (nhanh) · `P2p Edge` (PortFast) · `Shared` (half-duplex — chậm)
- **PortFast**: forwarding ngay — **chỉ** port nối thiết bị đầu cuối
- ⭐ **PortFast luôn đi kèm BPDU Guard** — coi như một lệnh hai dòng
- **BPDU Guard**: nhận *bất kỳ* BPDU → `err-disabled`, **không tự hồi**
- **Root Guard**: nhận BPDU *tốt hơn* → `root-inconsistent`, **tự hồi**
- `errdisable recovery` tự mở lại port sau N giây — nhớ theo dõi log

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `spanning-tree mode rapid-pvst` | **Bật ở mọi switch** |
| `spanning-tree portfast default` | PortFast cho mọi access port |
| `spanning-tree portfast bpduguard default` | BPDU Guard kèm theo |
| `spanning-tree guard root` | Port hướng **xuống** access |
| `spanning-tree portfast trunk` | Port nối hypervisor |
| `show spanning-tree summary` | Đang chạy mode nào, bật gì |
| `show interfaces status err-disabled` | Port nào bị tắt, vì sao |
| `shutdown` + `no shutdown` | Khôi phục err-disabled |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| PortFast trên port nối switch | **Loop tức thì** |
| PortFast mà không có BPDU Guard | Mở cửa cho loop |
| Root Guard trên port hướng **lên** core | Tự chặn đường về root thật |
| Nhầm BPDU Guard với Root Guard | Đặt sai chỗ, không bảo vệ được gì |
| Bật `errdisable recovery` rồi quên theo dõi | Port bật-tắt lặp lại, không ai biết |
| Để một switch chạy STP cổ điển | Cả đoạn mạng tụt về 50 giây |
| Bật `bpdufilter` vì thấy "gọn" | **Vô hiệu hoá STP** — rất nguy hiểm |

## 15. Homework + cập nhật PROGRESS

1. Làm LAB 14, **bấm giờ** thời gian hội tụ của `pvst` và `rapid-pvst` — ghi con số thật.
2. Trên switch lab: cắm một switch khác vào port có BPDU Guard. Quan sát log,
   rồi khôi phục port bằng cả 2 cách (tay và recovery timer).
3. Bổ sung đoạn STP vào "**config chuẩn**" bạn viết ở Lesson 12.

```markdown
- [YYYY-MM-DD] Lesson 16 — RSTP & STP Guards: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | RSTP state/role, PortFast, BPDU Guard vs Root Guard, proposal/agreement |
| 🔧 **Engineer** | `portfast default` + `bpduguard default` toàn cục; Root Guard hướng xuống; `errdisable recovery` |
| 🏭 **Production** | 50 giây gián đoạn = rớt VoIP/SSH; switch lạ cướp root làm traffic đi vòng âm thầm; half-duplex giết RSTP |

### 🔗 Liên kết

- ⬅️ [Lesson 15 — STP](./lesson-15-stp.md)
- ➡️ [Lesson 17 — EtherChannel & Port Security](./lesson-17-etherchannel-port-security.md)
- 🔜 Loop Guard, UDLD, MST: [`CCNP-Encor` Module 02](https://github.com/hiepnguyen775/CCNP-Encor)
