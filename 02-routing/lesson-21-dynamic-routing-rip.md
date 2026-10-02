# LESSON 21 — Dynamic Routing: bức tranh chung · RIP

> 📌 Lesson "bản đồ". Nó không dạy bạn cấu hình gì nhiều — nó cho bạn **khung tư duy**
> để hiểu OSPF ở 3 lesson tiếp theo không bị lạc.

| | |
|---|---|
| **Phase** | 2 — Routing |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 19](./lesson-19-static-default-route.md), [Lesson 20](./lesson-20-ad-metric-longest-prefix.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Phân loại routing protocol theo 3 trục: IGP/EGP · Distance Vector/Link-State · Classful/Classless
- [ ] Giải thích **Distance Vector** và **Link-State** khác nhau ở điểm cốt lõi nào
- [ ] Hiểu **routing loop** xảy ra thế nào và các cơ chế chống loop
- [ ] Biết RIP đủ để **nhận ra** nó, và hiểu vì sao nó không còn được dùng
- [ ] Nói được convergence là gì và vì sao nó quan trọng

## 2. Prerequisite

- AD, metric, longest prefix match *(Lesson 20)*
- Static route và giới hạn của nó *(Lesson 19)*

---

## 3. Concept

### Phân loại — 3 trục

#### Trục 1: Phạm vi

| | **IGP** (Interior Gateway Protocol) | **EGP** (Exterior Gateway Protocol) |
|---|---|---|
| Dùng ở | **Trong một tổ chức** (autonomous system) | **Giữa các tổ chức** / ISP |
| Mục tiêu | Tìm đường **nhanh nhất** | Thực thi **chính sách** |
| Ví dụ | RIP, OSPF, EIGRP, IS-IS | **BGP** |

#### Trục 2: Thuật toán

| | **Distance Vector** | **Link-State** |
|---|---|---|
| Router biết gì | Chỉ biết *"mạng X cách tôi N hop, qua láng giềng Y"* | **Toàn bộ bản đồ** mạng (LSDB) |
| Ví von | Hỏi đường từng người | Có **bản đồ** trong tay |
| Trao đổi gì | **Cả bảng định tuyến** của mình | **Thông tin về link** của mình |
| Tần suất | Định kỳ (RIP: 30 giây) | Chỉ khi **có thay đổi** |
| Tính đường | Dùng bảng của láng giềng | Tự chạy **Dijkstra (SPF)** trên bản đồ |
| Hội tụ | **Chậm** | **Nhanh** |
| Tốn CPU/RAM | Ít | Nhiều hơn |
| Ví dụ | **RIP**, IGRP | **OSPF**, IS-IS |

> 💡 EIGRP là **hybrid** (advanced distance vector) — dùng thuật toán DUAL, giữ
> thông tin về láng giềng nhưng không có bản đồ đầy đủ như OSPF.

> 🔑 **Câu phân biệt cốt lõi:**
> Distance Vector *"tin lời láng giềng kể"*. Link-State *"tự nhìn bản đồ rồi tự tính"*.

#### Trục 3: Có gửi subnet mask không

| | **Classful** | **Classless** |
|---|---|---|
| Gửi subnet mask trong update | ❌ Không | ✅ **Có** |
| Hỗ trợ VLSM / CIDR | ❌ | ✅ |
| Ví dụ | RIPv1, IGRP *(đã chết)* | **RIPv2, OSPF, EIGRP, BGP** |

> ⚠️ Classful protocol **không dùng được VLSM** — tức là không dùng được trong bất kỳ
> mạng hiện đại nào. Đây là lý do RIPv1 và IGRP tuyệt chủng.

### Convergence — hội tụ

**Convergence** = thời gian để **mọi router** trong mạng cùng có thông tin đúng và nhất quán
sau một thay đổi (link chết, router mới lên...).

| Protocol | Thời gian hội tụ điển hình |
|---|---|
| RIP | **Vài phút** 😱 |
| OSPF | **Vài giây** |
| EIGRP | **Dưới 1 giây** (nếu có feasible successor) |

Trong thời gian chưa hội tụ: gói tin có thể bị drop, chạy vòng, hoặc đi đường kém.

### Routing loop — vấn đề kinh điển của Distance Vector

```text
A ──── B ──── C ──── mạng X

1. Link C–X chết
2. C biết X đã mất
3. NHƯNG B chưa biết, và B vẫn quảng bá "tôi tới X được, 2 hop"
4. C nghe B, tưởng B có đường khác → cài route X via B
5. B gửi gói tới X cho C, C gửi lại cho B...
6. Metric tăng dần: 2 → 3 → 4 → ... (count to infinity)
```

### Các cơ chế chống loop của Distance Vector

| Cơ chế | Cách hoạt động |
|---|---|
| **Max hop count** | RIP coi 16 hop = không tới được → giới hạn thiệt hại |
| **Split horizon** | **Không quảng bá route ngược lại hướng đã học được nó** |
| **Route poisoning** | Khi mạng chết, quảng bá nó với metric 16 (vô cực) thay vì im lặng |
| **Poison reverse** | Gửi ngược lại route đã nhận, kèm metric 16 |
| **Holddown timer** | Sau khi nghe tin xấu, **không tin tin tốt** về mạng đó trong N giây |
| **Triggered update** | Gửi update **ngay** khi có thay đổi, không chờ hết 30 giây |

> 🔑 **Link-State không cần hầu hết các cơ chế này** — vì mỗi router có bản đồ đầy đủ
> và tự tính đường, nó không bao giờ "tin nhầm lời kể" của láng giềng.
> Đó là ưu thế lớn nhất của OSPF.

### RIP — đủ để nhận ra, không cần thuộc

| Đặc điểm | RIPv2 |
|---|---|
| Loại | Distance Vector, classless |
| Metric | **Hop count** |
| Max hop | **15** (16 = unreachable) |
| AD | **120** |
| Update | Mỗi **30 giây**, multicast `224.0.0.9` |
| Port | **UDP 520** |
| Hỗ trợ VLSM | ✅ (v2) |

```cisco
R1(config)# router rip
R1(config-router)# version 2
R1(config-router)# no auto-summary          ! BẮT BUỘC, nếu không nó tự gom về classful
R1(config-router)# network 10.0.0.0
R1(config-router)# passive-interface GigabitEthernet0/0
```

> ⚠️ `network 10.0.0.0` trong RIP nhận **địa chỉ classful** — nó bật RIP trên **mọi**
> interface thuộc `10.x.x.x`. Không có wildcard mask như OSPF.

---

## 4. Why?

> **Vì sao RIP chết?**

| Giới hạn | Hậu quả |
|---|---|
| **Max 15 hop** | Mạng doanh nghiệp lớn vượt ngưỡng → không tới được |
| **Metric chỉ là hop count** | Đường 1 hop qua link 2 Mbps **thắng** đường 2 hop qua link 10 Gbps 🤦 |
| **Update định kỳ 30 giây** | Tốn băng thông liên tục dù không có gì thay đổi |
| **Hội tụ vài phút** | Không chấp nhận được |
| Không có khái niệm area | Không scale |

> 🔑 Lỗi chí mạng nhất là **metric = hop count**. Nó bỏ qua hoàn toàn băng thông,
> độ trễ, và tải — những thứ thực sự quyết định đường nào tốt.

> **Vậy học RIP để làm gì?**

| Lý do | |
|---|---|
| **Có trong đề CCNA** | Ở mức khái niệm — biết nó là gì, vì sao không dùng |
| **Hiểu Distance Vector** | Để thấy rõ OSPF giải quyết vấn đề gì |
| **Vẫn gặp trong thiết bị cũ** | Một số hệ thống legacy, thiết bị không-Cisco rẻ tiền |

> ❌ **Không cần** thuộc timer của RIP, không cần giỏi cấu hình RIP.
> Dồn sức cho OSPF — đó mới là thứ bạn sẽ dùng.

---

## 5. How does it work? — so sánh trực tiếp

### Distance Vector (RIP) khi link chết

```text
T+0s    Link chết
T+0s    Router kề bên biết ngay
T+30s   Láng giềng kế tiếp nghe update đầu tiên
T+60s   Lan tiếp một bậc
...
T+180s  Holddown timer hết, mạng ổn định
→ Hội tụ: VÀI PHÚT
```

### Link-State (OSPF) khi link chết

```text
T+0s      Link chết
T+0s      Router phát LSA báo thay đổi — FLOOD ngay lập tức ra toàn area
T+~1s     Mọi router trong area nhận được LSA
T+~1-5s   Mỗi router tự chạy SPF trên LSDB mới → ra đường mới
→ Hội tụ: VÀI GIÂY
```

> 🔑 Khác biệt cốt lõi: RIP **lan truyền kết quả đã tính** (chậm, qua từng chặng).
> OSPF **lan truyền dữ kiện thô** (nhanh, flood ngay) rồi **mỗi router tự tính**.

---

## 6. Packet Flow — không áp dụng

Thay vào đó, bảng tham chiếu các địa chỉ và port của routing protocol:

| Protocol | Multicast | Protocol/Port | AD |
|---|---|---|:---:|
| RIPv2 | `224.0.0.9` | **UDP 520** | 120 |
| OSPFv2 | `224.0.0.5` / `224.0.0.6` | **IP protocol 89** *(không có port)* | 110 |
| EIGRP | `224.0.0.10` | **IP protocol 88** | 90 / 170 |
| BGP | *(unicast)* | **TCP 179** | 20 / 200 |

> ⚠️ OSPF và EIGRP chạy **thẳng trên IP**, không có port. ACL chặn theo port sẽ không
> ảnh hưởng chúng — nhưng ACL chặn `ip any any` thì giết chúng ngay.

---

## 7. Real-world Example

🏭 **Chọn routing protocol cho doanh nghiệp — bảng quyết định thật**

| Tình huống | Chọn | Vì sao |
|---|---|---|
| Chi nhánh 1 đường ra (stub) | **Static** | Không có gì để tính |
| Doanh nghiệp 1 site, < 10 router | **OSPF single-area** | Chuẩn mở, đủ dùng, dễ tìm người biết |
| Doanh nghiệp nhiều site, nhiều router | **OSPF multi-area** | Chia area để scale |
| Toàn Cisco, muốn hội tụ cực nhanh | EIGRP | Nhanh nhất, nhưng khoá vào Cisco |
| Kết nối với ISP, có nhiều ISP | **BGP** | Duy nhất làm được chính sách định tuyến |
| Data center hiện đại | BGP (EVPN/VXLAN) | Xu hướng mới |

> 🔧 Trong thực tế Việt Nam: **OSPF** là lựa chọn phổ biến nhất cho mạng nội bộ doanh nghiệp,
> **BGP** cho kết nối ISP / multi-homing. RIP gần như không còn thấy.

🏭 **Passive-interface — thói quen bắt buộc**

```cisco
R1(config-router)# passive-interface GigabitEthernet0/0    ! interface nối PC
```

Interface nối **người dùng** không cần gửi hello/update routing — không có router nào ở đó.
Gửi ra chỉ: tốn băng thông, và **lộ thông tin topology** cho bất kỳ ai cắm máy vào.

> 🔧 Nhiều nơi làm ngược lại cho an toàn: `passive-interface default` rồi
> `no passive-interface` cho đúng các interface nối router.

---

## 8. Cisco CLI

```cisco
! ───── RIPv2 (chỉ để nhận biết, không dùng thật) ─────
R1(config)# router rip
R1(config-router)# version 2
R1(config-router)# no auto-summary
R1(config-router)# network 10.0.0.0
R1(config-router)# network 192.168.1.0
R1(config-router)# passive-interface GigabitEthernet0/0
R1(config-router)# default-information originate    ! quảng bá default route

! ───── Kiểm tra ─────
R1# show ip protocols
R1# show ip route rip
R1# show ip rip database
R1# debug ip rip                 ! ⚠️ tốn CPU, nhớ undebug all

! ───── Gỡ bỏ ─────
R1(config)# no router rip
```

| Lệnh | Làm gì | Lưu ý |
|---|---|---|
| `version 2` | Bật RIPv2 | Thiếu → chạy v1, **không hỗ trợ VLSM** |
| `no auto-summary` | Tắt tự gom về classful | ⚠️ **Bắt buộc** — quên là mạng loạn |
| `network 10.0.0.0` | Bật RIP trên mọi interface thuộc `10.x` | **Classful** — không có wildcard |
| `passive-interface` | Không gửi update ra interface này | Vẫn **quảng bá** mạng đó |
| `default-information originate` | Quảng bá default route cho láng giềng | |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip protocols
Routing Protocol is "rip"
  Sending updates every 30 seconds, next due in 12 seconds
  Invalid after 180 seconds, hold down 180, flushed after 240
  Redistributing: rip
  Default version control: send version 2, receive version 2
  Automatic network summarization is not in effect
  Maximum path: 4
  Routing for Networks:
    10.0.0.0
  Passive Interface(s):
    GigabitEthernet0/0
  Distance: (default is 120)
```

**Đọc gì:**

| Dòng | Ý nghĩa | Bất thường |
|---|---|---|
| `Sending updates every 30 seconds` | Chu kỳ update | — |
| `Invalid after 180, hold down 180, flushed after 240` | Các timer — tổng cộng rất chậm | Đây là lý do RIP hội tụ chậm |
| `send version 2, receive version 2` | Đang chạy v2 ✅ | Nếu là v1 → không hỗ trợ VLSM |
| `Automatic network summarization is not in effect` | Đã `no auto-summary` ✅ | Nếu "is in effect" → **thiếu lệnh** |
| `Routing for Networks` | Mạng nào được quảng bá | Thiếu → route không lan |
| `Passive Interface(s)` | Interface không gửi update | |

```text
# output điển hình — tự verify trên lab của bạn
R1# show ip route rip
R     192.168.2.0/24 [120/1] via 10.0.12.2, 00:00:08, GigabitEthernet0/1
R     192.168.3.0/24 [120/2] via 10.0.12.2, 00:00:08, GigabitEthernet0/1
```

`[120/2]` = AD 120, **metric 2 hop**.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Subnet `/26`, `/30` không lan được | Đang chạy **RIPv1** (classful) | `show ip protocols` | `version 2` |
| Route bị gom thành `/8`, `/16` sai | Quên `no auto-summary` | `show ip protocols` | Thêm lệnh đó |
| Một mạng không được quảng bá | Thiếu `network` statement | `show ip protocols` | Thêm `network` |
| Mạng ở xa 16 hop không tới được | Vượt **max hop count** | `show ip route rip` | Đổi sang OSPF |
| Hội tụ rất chậm sau khi link chết | Timer của RIP | `show ip protocols` | Đổi sang OSPF/EIGRP |
| Route đi đường chậm dù có đường nhanh hơn | Metric = **hop count**, bỏ qua băng thông | `show ip route rip` | Đổi sang OSPF |
| Update RIP gửi ra port người dùng | Thiếu `passive-interface` | `show ip protocols` | Thêm passive |

---

## 11. LAB

🧪 **Bài quan sát ngắn** *(không cần lab đầy đủ — RIP chỉ ở mức khái niệm)*

1. Dựng 3 router nối chuỗi, chạy RIPv2 trên tất cả. Verify route lan hết.
2. Chạy `debug ip rip` trên R2 trong 60 giây — **đếm** số update nhận được.
   Tính xem mỗi phút tốn bao nhiêu gói dù mạng không có gì thay đổi.
3. Quên `no auto-summary` trên một router có subnet `/26` → quan sát route bị gom sai.
4. `shutdown` một link, **bấm giờ** thời gian route biến mất khỏi bảng ở router xa nhất.
   Ghi lại con số — so với OSPF ở LAB 23.
5. Gỡ RIP (`no router rip`) — lesson sau ta dùng OSPF.

## 12. Challenge

1. Mạng có đường A (1 hop, link 2 Mbps) và đường B (3 hop, toàn link 10 Gbps).
   RIP chọn đường nào? OSPF chọn đường nào? Vì sao khác nhau?
2. Giải thích **split horizon** bằng một câu, và vì sao OSPF không cần nó.
3. Vì sao `no auto-summary` lại bắt buộc với RIPv2?
4. Mạng doanh nghiệp có 20 router nối chuỗi. RIP có dùng được không?

<details>
<summary>Đáp án</summary>

**1.**

| Protocol | Chọn | Vì sao |
|---|---|---|
| **RIP** | **Đường A** (1 hop) | Metric = hop count. 1 < 3 → thắng. **Hoàn toàn bỏ qua** việc link chỉ 2 Mbps |
| **OSPF** | **Đường B** | Cost = `100 Mbps / bandwidth`. Link 10G cost rất thấp; link 2 Mbps cost = `100/2 = 50` rất cao |

Đây là ví dụ rõ nhất về lý do RIP chết: nó chọn đường **chậm hơn 5000 lần** chỉ vì đường đó
ít hop hơn.

**2.** **Split horizon:** *"không quảng bá một route ngược lại chính hướng mà tôi đã học được nó"*.

OSPF không cần vì nó **không quảng bá route** — nó quảng bá **thông tin về link** (LSA),
và mỗi router **tự tính đường** từ bản đồ đầy đủ. Không có chuyện "tin nhầm lời kể"
nên không có loại loop này.

**3.** Vì mặc định RIP **tự gom** (auto-summarize) route về **ranh giới classful** khi
quảng bá qua biên giới lớp mạng khác.

Ví dụ: bạn có `10.0.1.0/24` và `10.0.2.0/24`. Qua biên giới, RIP quảng bá thành
`10.0.0.0/8` — **mất hết thông tin subnet**. Router bên kia tưởng bạn có cả `10.x.x.x`,
gửi nhầm traffic. `no auto-summary` giữ nguyên prefix thật.

**4.** **Không.** Hai lý do:

| Vấn đề | Chi tiết |
|---|---|
| **Max 15 hop** | Router thứ 16 trở đi **không tới được** |
| **Hội tụ** | 20 router nối chuỗi: tin tức lan qua từng chặng, mỗi chặng tới 30 giây → hội tụ có thể mất **5–10 phút** |

Với 20 router, OSPF multi-area là lựa chọn đúng.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | IGP vs EGP · DV vs LS · AD và multicast của RIP/OSPF/EIGRP | ⬜ |
| **L2** Explain | Giải thích Distance Vector vs Link-State bằng ví von của bạn | ⬜ |
| **L3** Configure | Cấu hình RIPv2 3 router, verify lan route | ⬜ |
| **L4** Troubleshoot | Subnet `/26` không lan → tìm ra RIPv1 hoặc auto-summary | ⬜ |
| **L5** Design | Chọn protocol cho 4 kịch bản mạng, giải thích từng cái | ⬜ |

## 14. Summary

**Key concepts**

- **IGP** (trong tổ chức): RIP, OSPF, EIGRP · **EGP** (giữa tổ chức): **BGP**
- ⭐ **Distance Vector** tin lời láng giềng kể · **Link-State** tự nhìn bản đồ tự tính
- **Classless** (có gửi mask) mới dùng được VLSM — RIPv1/IGRP đã chết
- Chống loop của DV: max hop · **split horizon** · route poisoning · holddown · triggered update
- Link-State **không cần** hầu hết cơ chế này
- RIP: metric **hop count**, max **15**, AD **120**, update **30 giây**, `224.0.0.9`, UDP 520
- ⭐ RIP chết vì **metric hop count bỏ qua băng thông** và hội tụ vài phút
- OSPF/EIGRP chạy **thẳng trên IP** (protocol 89 / 88), không có port

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show ip protocols` | ⭐ Protocol nào chạy, quảng bá gì, AD bao nhiêu |
| `router rip` + `version 2` + `no auto-summary` | Cấu hình RIP tối thiểu |
| `passive-interface <int>` | Không gửi update ra port người dùng |
| `show ip route rip` | Route học từ RIP |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Quên `version 2` | Chạy v1, không hỗ trợ VLSM |
| Quên `no auto-summary` | Route bị gom sai về classful |
| Nghĩ RIP vẫn dùng được cho mạng vừa | Max 15 hop, hội tụ vài phút |
| So metric giữa RIP và OSPF | Không so được |
| Quên `passive-interface` | Lộ topology, tốn băng thông |

## 15. Homework + cập nhật PROGRESS

1. Làm bài quan sát mục 11, **ghi lại con số** thời gian hội tụ của RIP.
2. Vẽ bảng so sánh Distance Vector vs Link-State bằng lời của bạn, không nhìn lesson.
3. Trả lời: mạng công ty bạn đang dùng protocol gì? Nếu không biết, hỏi hoặc
   chạy `show ip protocols` trên một router.

```markdown
- [YYYY-MM-DD] Lesson 21 — Dynamic Routing & RIP: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Phân loại 3 trục, cơ chế chống loop, thông số RIP, AD các protocol |
| 🔧 **Engineer** | `passive-interface` mọi port người dùng; chọn đúng protocol theo quy mô |
| 🏭 **Production** | RIP vẫn gặp ở thiết bị legacy; `no auto-summary` là lỗi kinh điển; OSPF là mặc định thực tế |

### 🔗 Liên kết

- ⬅️ [Lesson 20 — AD, Metric, Longest Prefix](./lesson-20-ad-metric-longest-prefix.md)
- ➡️ [Lesson 22 — OSPF single-area](./lesson-22-ospf-single-area.md)
- 🔜 BGP: [`CCNP-Encor` Module 05A/05B](https://github.com/hiepnguyen775/CCNP-Encor)
