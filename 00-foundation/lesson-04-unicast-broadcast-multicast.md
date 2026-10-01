# LESSON 04 — Unicast · Broadcast · Multicast · Broadcast Domain

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~1.5 giờ |
| **Prerequisite** | [Lesson 03](./lesson-03-ethernet-mac-frame.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Phân biệt 3 kiểu gửi và nói được **khi nào dùng cái nào**
- [ ] Nhận ra địa chỉ broadcast / multicast chỉ bằng cách nhìn, ở cả L2 và L3
- [ ] Giải thích **broadcast domain** là gì và cái gì chia nhỏ nó
- [ ] Nói được vì sao broadcast domain quá lớn làm mạng chậm
- [ ] Hiểu vì sao đây là lý do **VLAN tồn tại** — nền cho Phase 1

## 2. Prerequisite

- Switch flood khi không biết destination MAC *(Lesson 03)*
- `FF:FF:FF:FF:FF:FF` là broadcast MAC *(Lesson 03)*
- Network address và broadcast address của một subnet *(Lesson 02)*

---

## 3. Concept

### Ba kiểu gửi

| Kiểu | Gửi cho | Hình dung |
|---|---|---|
| **Unicast** | **Một** máy cụ thể | Gọi điện cho một người |
| **Broadcast** | **Tất cả** máy trong broadcast domain | Loa phát thanh cả toà nhà |
| **Multicast** | **Một nhóm** đã đăng ký | Kênh truyền hình — ai bật mới nhận |

### Nhận diện bằng cách nhìn địa chỉ

| | Unicast | Broadcast | Multicast |
|---|---|---|---|
| **MAC (L2)** | `00:1A:2B:...` | `FF:FF:FF:FF:FF:FF` | `01:00:5E:xx:xx:xx` (IPv4)<br>`33:33:xx:xx:xx:xx` (IPv6) |
| **IPv4 (L3)** | `192.168.1.10` | `192.168.1.255` *(broadcast của subnet)*<br>`255.255.255.255` *(limited)* | `224.0.0.0` → `239.255.255.255` |
| **IPv6** | `2001:db8::1` | **không có** | `ff00::/8` |

> 💡 Mẹo nhận diện multicast MAC: **bit thấp nhất của byte đầu = 1**.
> `01` → `00000001` → bit cuối là 1 → multicast. `00` → unicast. `FF` → tất cả bit 1 → broadcast.

### Hai loại broadcast IPv4

| Loại | Địa chỉ | Router có chuyển tiếp? |
|---|---|---|
| **Directed broadcast** | `192.168.1.255` — broadcast của một subnet cụ thể | Mặc định **không** (từ IOS 12.0) |
| **Limited broadcast** | `255.255.255.255` | **Không bao giờ** — luôn dừng ở router |

> 🔑 Câu quan trọng nhất của lesson này: **router KHÔNG chuyển tiếp broadcast.**
> Đây là lý do DHCP cần relay, và là lý do broadcast domain kết thúc ở interface router.

### Địa chỉ multicast cần nhớ

| Địa chỉ | Dùng cho |
|---|---|
| `224.0.0.1` | Tất cả host trong subnet |
| `224.0.0.2` | Tất cả router trong subnet |
| `224.0.0.5` | **OSPF** — tất cả router OSPF |
| `224.0.0.6` | **OSPF** — DR/BDR |
| `224.0.0.9` | RIPv2 |
| `224.0.0.10` | EIGRP |
| `224.0.0.102` | HSRPv2 / GLBP |

---

## 4. Why? — tại sao cần cả 3 kiểu

> **Nếu chỉ có unicast thì sao?**

Giả sử một router OSPF muốn gửi hello cho 20 router khác trên cùng đoạn mạng.

| Chỉ có unicast | Có multicast |
|---|---|
| Phải gửi **20 bản** giống hệt nhau | Gửi **1 bản** tới `224.0.0.5` |
| Phải **biết trước** IP của cả 20 router | Không cần biết ai đang nghe |
| Thêm router mới → phải cấu hình lại tay | Router mới tự join nhóm, tự nhận |

> **Nếu chỉ có broadcast thì sao?**

| Vấn đề | Giải thích |
|---|---|
| **Mọi máy đều phải xử lý** | Card mạng nhận → ngắt CPU → OS kiểm tra → phần lớn là "không phải việc của tôi" rồi vứt. Lãng phí CPU của **tất cả** máy. |
| **Không ai lọc được** | Khác multicast, máy không thể "không đăng ký" broadcast. |
| **Không scale** | 500 máy trong một broadcast domain = mỗi ARP làm 500 máy giật mình. |

Vì vậy: **unicast** cho hội thoại riêng, **multicast** cho nhóm, **broadcast** chỉ dùng khi
*chưa biết mình phải nói với ai* — như ARP ("ai có IP này?") và DHCP Discover ("có server nào không?").

---

## 5. How does it work? — Broadcast Domain

### Định nghĩa

> **Broadcast domain** = tập hợp các thiết bị mà một frame broadcast sẽ tới được.

### Thiết bị nào làm gì

| Thiết bị | Với broadcast | Kết quả |
|---|---|---|
| **Hub** | Lặp ra mọi port | 1 collision domain, 1 broadcast domain |
| **Switch** | **Flood** ra mọi port cùng VLAN | Mỗi port = 1 collision domain; **mỗi VLAN = 1 broadcast domain** |
| **Router** | **Chặn lại** | Mỗi interface = biên của một broadcast domain |

```text
          ┌─────── 1 broadcast domain ────────┐
          │                                    │
   PC ── SW1 ══════ SW2 ── PC                 │
          │                                    │
          └────────── R1 (chặn) ───────────────┘
                       │
          ┌─────── broadcast domain KHÁC ──────┐
                      PC ── SW3 ── PC
```

### Cái gì chia nhỏ broadcast domain

Chỉ có **hai** thứ:

1. **Router** (hoặc L3 switch) — ranh giới vật lý/logic
2. **VLAN** — ranh giới logic trong cùng một switch ⭐

> Đây chính là cầu nối sang Phase 1. VLAN ra đời để chia nhỏ broadcast domain
> **mà không cần mua thêm router và kéo thêm dây**.

### Broadcast domain quá lớn thì sao

| Số máy | Hệ quả |
|:---:|---|
| ~50 | Không cảm nhận được |
| ~250 | Bắt đầu thấy nền broadcast đáng kể |
| 500+ | CPU máy yếu bị ảnh hưởng; sự cố lan rộng; khó khoanh vùng |

Nguồn broadcast thường xuyên trong mạng thật: **ARP**, **DHCP**, NetBIOS/mDNS (phát hiện
máy in, chia sẻ file), và các giao thức khám phá của ứng dụng.

> 🏭 Quy tắc thiết kế thực tế: **giữ mỗi VLAN dưới ~250 host** (tức là một `/24`).
> Không phải vì `/24` thiêng liêng, mà vì đó là kích thước broadcast domain còn chịu được.

---

## 6. Packet Flow

**Kịch bản:** PC-A broadcast ARP trong mạng có 2 switch và 1 router.

| # | Ở đâu | Chuyện gì xảy ra |
|:---:|---|---|
| 1 | PC-A | Tạo frame: Dst MAC = `FF:FF:FF:FF:FF:FF`, Dst IP = `192.168.1.255` |
| 2 | SW1 | Thấy destination broadcast → **flood** ra mọi port cùng VLAN trừ port nhận |
| 3 | SW2 (qua trunk/uplink) | Nhận được → tiếp tục flood trong VLAN đó |
| 4 | Mọi PC trong VLAN | Card mạng **nhận**, đẩy lên OS, OS kiểm tra "có phải hỏi tôi không?" |
| 5 | PC đúng đích | Trả lời bằng **unicast** |
| 6 | **R1** | Nhận frame broadcast → **vứt bỏ, không chuyển tiếp** ⛔ |

**Rút ra:** broadcast đi hết VLAN, qua bao nhiêu switch cũng được, nhưng **dừng lại ở router**.

> ⚠️ Chú ý bước 4: **mọi** máy đều tốn CPU để xử lý rồi mới vứt. Đó là cái giá của broadcast.
> Với multicast, card mạng lọc ngay ở phần cứng nếu không đăng ký nhóm đó — không làm phiền CPU.

---

## 7. Real-world Example

🏭 **Tình huống 1 — "Mạng tự nhiên chậm vào mỗi sáng 8h"**

Cả công ty bật máy cùng lúc → đồng loạt DHCP Discover (broadcast) + ARP (broadcast) +
dò máy in (broadcast). Nếu toàn bộ 300 máy nằm **một broadcast domain**, đó là một cơn bão nhỏ.

Cách sửa: chia VLAN theo tầng/phòng ban → mỗi VLAN ~100 máy → nền broadcast giảm 3 lần.

🏭 **Tình huống 2 — Broadcast storm**

Có loop L2 và STP bị tắt. Một frame broadcast chạy vòng tròn, **nhân lên theo cấp số nhân**
vì frame Ethernet **không có TTL**. Trong vài giây: CPU switch 100%, đèn port nháy đồng loạt,
cả mạng chết.

Đây là lý do STP tồn tại — bạn sẽ học ở Lesson 15.

🏭 **Tình huống 3 — Cái lợi của multicast**

Hệ thống camera IP phát video. Nếu dùng unicast, 10 người xem = 10 luồng video chiếm băng thông.
Dùng multicast = **1 luồng** trên mỗi đoạn mạng, ai đăng ký thì nhận.

---

## 8. Cisco CLI

```cisco
! Đếm số broadcast nhận được trên một interface
SW1# show interfaces GigabitEthernet0/1 counters

! Xem thống kê interface, có mục broadcast
SW1# show interfaces GigabitEthernet0/1

! Giới hạn broadcast để chống storm — rất đáng bật ở production
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# storm-control broadcast level 1.00
SW1(config-if)# storm-control action shutdown

! Kiểm tra storm-control
SW1# show storm-control broadcast

! (Trên router) bật chuyển tiếp directed broadcast — MẶC ĐỊNH TẮT, hiếm khi nên bật
R1(config-if)# ip directed-broadcast
```

| Lệnh | Làm gì | Ghi chú |
|---|---|---|
| `storm-control broadcast level 1.00` | Drop broadcast khi vượt 1% băng thông port | Con số 1% là điểm khởi đầu hợp lý cho port người dùng |
| `storm-control action shutdown` | Err-disable port khi vượt ngưỡng | Thay cho `trap` nếu muốn cô lập hẳn |
| `ip directed-broadcast` | Cho router chuyển directed broadcast | ⚠️ Từng bị lợi dụng cho tấn công **Smurf** — để tắt |

> **Khác biệt platform:** `storm-control` có trên switch Catalyst (IOS/IOS-XE).
> NX-OS dùng cú pháp tương tự nhưng mức ngưỡng cấu hình khác — kiểm tra tài liệu nền tảng.

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show interfaces GigabitEthernet0/1 counters broadcast
Port            InBcast         OutBcast
Gi0/1            142033           98221
```

```text
# output điển hình — tự verify trên lab của bạn
SW1# show storm-control broadcast
Interface  Filter State   Upper        Lower        Current
---------  -------------  -----------  -----------  ----------
Gi0/1      Forwarding     1.00%        1.00%        0.12%
Gi0/2      Blocking       1.00%        1.00%        3.45%   ← đang bị chặn
```

**Đọc gì:**

| Field | Ý nghĩa | Bất thường |
|---|---|---|
| `InBcast` | Số broadcast nhận vào | Tăng hàng nghìn/giây → nghi storm |
| `Filter State: Forwarding` | Dưới ngưỡng, bình thường | — |
| `Filter State: Blocking` | **Đang vượt ngưỡng**, switch đang drop | Tìm nguồn phát: loop? máy lỗi? |
| `Current` | Tỷ lệ broadcast hiện tại | Bình thường < 0.5% ở port người dùng |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Cả mạng chậm/treo đột ngột | **Broadcast storm** do loop | `show interfaces counters`, nhìn đèn port | Rút dây thừa; kiểm tra `show spanning-tree` |
| CPU switch 100% | Storm, hoặc quá nhiều broadcast | `show processes cpu sorted` | Chia VLAN; bật `storm-control` |
| Mạng chậm vào giờ cao điểm | Broadcast domain quá lớn | Đếm host trong VLAN | Chia nhỏ VLAN |
| Port bị `err-disabled` | `storm-control action shutdown` đã kích hoạt | `show interfaces status err-disabled` | Tìm nguồn storm rồi `shutdown`/`no shutdown` |
| PC ở VLAN khác không nhận DHCP | Router chặn broadcast — **đúng như thiết kế** | — | Cấu hình `ip helper-address` *(Lesson 08)* |

---

## 11. LAB

🧪 **Bài quan sát** *(gộp vào LAB 02 với Wireshark)*

1. Trong Packet Tracer dựng: 1 switch, 4 PC cùng VLAN. Bật chế độ **Simulation**.
2. Từ PC1 ping PC4. Quan sát gói ARP **toả ra mọi port** — đó là broadcast.
3. Thêm 1 router giữa 2 switch. Lặp lại — chứng minh broadcast **không qua được router**.
4. Trên máy thật, mở Wireshark lọc `eth.dst == ff:ff:ff:ff:ff:ff`, để chạy 5 phút.
   Đếm xem mạng của bạn có bao nhiêu broadcast/phút và từ đâu ra.

## 12. Challenge

1. Một switch 24 port, **không chia VLAN**. Có bao nhiêu collision domain? Bao nhiêu broadcast domain?
2. Vẫn switch đó nhưng chia 3 VLAN. Câu trả lời đổi thế nào?
3. Vì sao IPv6 **bỏ hẳn** broadcast? Nó thay bằng gì, và lợi ở chỗ nào?
4. Mạng có 2 switch nối nhau và 1 router. Switch A có 2 VLAN, switch B có 2 VLAN
   (cùng VLAN ID, nối bằng trunk). Tổng cộng bao nhiêu broadcast domain?

<details>
<summary>Đáp án</summary>

**1.** **24 collision domain** (mỗi port một cái, do switch full-duplex) và
**1 broadcast domain** (tất cả port ở VLAN 1 mặc định).

**2.** Collision domain **vẫn 24** — VLAN không ảnh hưởng tới collision domain.
Broadcast domain thành **3**. Đây là điểm người mới hay nhầm lẫn nhất giữa hai khái niệm.

**3.** IPv6 thay broadcast bằng **multicast** có phạm vi cụ thể: `ff02::1` (tất cả node),
`ff02::2` (tất cả router). Lợi: máy **không quan tâm** thì card mạng lọc ngay ở phần cứng,
không làm phiền CPU. Broadcast thì mọi máy buộc phải xử lý rồi mới vứt.

**4.** **2 broadcast domain** — mỗi VLAN là một, và trunk nối chúng xuyên qua 2 switch.
Số switch không làm tăng số broadcast domain; chỉ **VLAN** và **router** mới làm việc đó.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 kiểu gửi · MAC broadcast · dải multicast IPv4 · `224.0.0.5` là gì | ⬜ |
| **L2** Explain | Giải thích vì sao router chặn broadcast, và hệ quả với DHCP | ⬜ |
| **L3** Configure | Bật `storm-control` trên một port, verify | ⬜ |
| **L4** Troubleshoot | Mạng treo, đèn port nháy đồng loạt → nêu giả thuyết và cách xác minh | ⬜ |
| **L5** Design | Công ty 400 máy → chia bao nhiêu broadcast domain, theo tiêu chí gì | ⬜ |

## 14. Summary

**Key concepts**

- **Unicast** 1→1 · **Broadcast** 1→tất cả trong domain · **Multicast** 1→nhóm đăng ký
- Nhận diện: MAC `FF:FF:FF:FF:FF:FF` = broadcast; byte đầu có bit cuối = 1 → multicast
- IPv4 multicast: `224.0.0.0` – `239.255.255.255`
- ⭐ **Router KHÔNG chuyển tiếp broadcast** — đây là biên của broadcast domain
- Chỉ **VLAN** và **router** chia nhỏ broadcast domain; thêm switch thì không
- Switch: mỗi port = 1 collision domain, mỗi **VLAN** = 1 broadcast domain
- Frame Ethernet **không có TTL** → loop L2 gây broadcast storm

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show interfaces <int> counters` | Đếm broadcast, nghi storm |
| `storm-control broadcast level 1.00` | Chặn storm ở port người dùng |
| `show storm-control broadcast` | Port nào đang bị chặn |

**Common mistakes**

| Sai | Đúng |
|---|---|
| Nhầm collision domain với broadcast domain | VLAN chia broadcast domain, **không** đổi collision domain |
| "Thêm switch là chia được broadcast domain" | Không — switch chỉ mở rộng nó |
| "`255.255.255.255` router sẽ chuyển tiếp" | Không bao giờ |
| Nghĩ multicast cũng làm phiền mọi máy như broadcast | Card mạng lọc multicast ở phần cứng |

## 15. Homework + cập nhật PROGRESS

1. Mở Wireshark trên máy bạn, lọc `eth.dst == ff:ff:ff:ff:ff:ff`, chạy 5 phút.
   Ghi lại: bao nhiêu gói? giao thức gì? từ máy nào?
2. Đếm số máy trong VLAN văn phòng bạn đang dùng. So với ngưỡng ~250.
3. Vẽ sơ đồ mạng công ty bạn, khoanh tròn từng broadcast domain.

```markdown
- [YYYY-MM-DD] Lesson 04 — Unicast/Broadcast/Multicast: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 3 kiểu gửi, nhận diện địa chỉ, broadcast domain vs collision domain, router chặn broadcast |
| 🔧 **Engineer** | Giữ VLAN dưới ~250 host; bật `storm-control` ở port người dùng |
| 🏭 **Production** | Broadcast storm làm sập mạng trong vài giây; `ip directed-broadcast` phải để tắt (tấn công Smurf) |

### 🔗 Liên kết

- ⬅️ [Lesson 03 — Ethernet & MAC](./lesson-03-ethernet-mac-frame.md)
- ➡️ [Lesson 05 — Default Gateway, ARP, ICMP](./lesson-05-gateway-arp-icmp.md)
- 🔜 Nền cho [Lesson 13 — VLAN & Trunk](../01-switching/lesson-13-vlan-va-trunk.md)
- 🦈 [`cheatsheets/wireshark.md`](../cheatsheets/wireshark.md)
