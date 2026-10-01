# LAB 02 — Bắt ARP + ICMP bằng Wireshark

| | |
|---|---|
| **Phase** | 0 |
| **Lesson liên quan** | [Lesson 05 — Gateway, ARP, ICMP](../00-foundation/lesson-05-gateway-arp-icmp.md) |
| **Công cụ** | **Wireshark trên máy thật** (+ Packet Tracer chế độ Simulation để đối chiếu) |
| **Thời lượng** | ~1.5 giờ |
| **Độ khó** | ⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] **Nhìn thấy** ARP request là broadcast và reply là unicast — không phải tin vào sách
- [ ] Chứng minh PC ARP tìm MAC **gateway** khi đích ở xa, không tìm MAC của đích
- [ ] Đọc ICMP type/code và nhận ra Time Exceeded trong traceroute
- [ ] Chứng minh TTL giảm đúng 1 mỗi hop

## 2. Prerequisite

- [Lesson 03](../00-foundation/lesson-03-ethernet-mac-frame.md) — frame, MAC
- [Lesson 05](../00-foundation/lesson-05-gateway-arp-icmp.md) — ARP, ICMP, TTL
- [`cheatsheets/wireshark.md`](../cheatsheets/wireshark.md) — display filter

## 3. Topology

Lab này chạy trên **máy thật của bạn** — không cần dựng gì:

```text
   Máy bạn ──── Switch/Router nhà ──── ISP ──── Internet (8.8.8.8)
   (Wireshark)      (gateway)
```

## 4. Chuẩn bị

| Việc | Windows | Linux |
|---|---|---|
| Xem IP + gateway | `ipconfig` | `ip addr` + `ip route` |
| Xem ARP cache | `arp -a` | `ip neigh` |
| Xoá ARP cache | `arp -d *` *(chạy as Administrator)* | `sudo ip -s neigh flush all` |

Ghi lại trước khi bắt đầu:

| | Giá trị |
|---|---|
| IP máy bạn | |
| Subnet mask | |
| Default gateway | |
| MAC máy bạn | |

---

## 5. Yêu cầu LAB

- [ ] Bắt được **cặp ARP request/reply** đầy đủ, chỉ ra Dst MAC của từng gói
- [ ] Chứng minh ping ra Internet **không** sinh ARP cho IP đích
- [ ] Bắt được ICMP Echo Request/Reply, đọc được type và code
- [ ] Bắt được ICMP **Time Exceeded** trong traceroute
- [ ] Hoàn thành mục **8. BREAK**

---

## 6. Step-by-step

### Bài 1 — ARP trong LAN

```powershell
# 1. Mở Wireshark, chọn card mạng đang dùng, bấm Start
# 2. Đặt display filter:  arp
# 3. Xoá ARP cache (as Administrator)
arp -d *
# 4. Ping gateway
ping 192.168.1.1
```

**Điền vào bảng:**

| Gói | Src MAC | Dst MAC | Nội dung Info |
|---|---|---|---|
| ARP Request | | | |
| ARP Reply | | | |

**Câu hỏi:**

- Dst MAC của Request là gì? Nó là loại địa chỉ gì?
- Dst MAC của Reply là gì? Vì sao khác Request?

### Bài 2 — ARP khi đích ở xa

```powershell
arp -d *
ping 8.8.8.8
```

Vẫn giữ filter `arp`.

**Câu hỏi quan trọng nhất của lab này:**

- Có gói ARP nào hỏi về `8.8.8.8` không?
- Nếu không, máy bạn ARP hỏi IP nào? **Vì sao?**

> 💡 Đây là chỗ chứng minh bằng mắt điều Lesson 05 nói: PC chỉ cần MAC của **gateway**.

### Bài 3 — ICMP

Đổi filter sang `icmp`, chạy lại `ping 8.8.8.8`.

| Gói | Type | Code | Tên | TTL |
|---|:---:|:---:|---|:---:|
| Đi | | | | |
| Về | | | | |

- TTL của gói **đi** là bao nhiêu? *(Windows 128, Linux 64)*
- TTL của gói **về** là bao nhiêu? **Chênh lệch nói lên điều gì?**

### Bài 4 — Traceroute và Time Exceeded

```powershell
tracert 8.8.8.8
```

Giữ filter `icmp`, hoặc dùng `icmp.type == 11`.

| Hop | IP trả lời | ICMP type | TTL của gói ĐI |
|:---:|---|:---:|:---:|
| 1 | | | |
| 2 | | | |
| 3 | | | |

- TTL của gói đi ở hop 1, 2, 3 lần lượt là bao nhiêu?
- Ai gửi ICMP Time Exceeded về?

### Bài 5 — Đối chiếu trong Packet Tracer

Dựng: 2 PC + 1 switch + 1 router + 1 server ở subnet khác.
Bật **Simulation mode**, lọc chỉ ARP và ICMP, ping từ PC1 sang server.

Quan sát và ghi lại: gói ARP **toả ra mọi port** của switch (broadcast),
nhưng **không qua router**.

---

## 7. Verification

- [ ] Bài 1: thấy đủ 2 gói, Request có Dst MAC `ff:ff:ff:ff:ff:ff`
- [ ] Bài 2: **không có** gói ARP nào hỏi `8.8.8.8`
- [ ] Bài 3: đọc được type 8 và type 0
- [ ] Bài 4: thấy ICMP type 11 từ các router trung gian
- [ ] Bài 5: thấy ARP dừng ở router trong Packet Tracer

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

| # | Cố tình làm sai | Dự đoán trước khi làm | Quan sát thực tế | Giải thích |
|:---:|---|---|---|---|
| 1 | Ping một IP **cùng subnet nhưng không tồn tại** (vd `.250`) | | | |
| 2 | Đổi default gateway của máy sang IP không tồn tại, rồi ping `8.8.8.8` | | | |
| 3 | Đổi subnet mask máy từ `/24` sang `/16`, rồi ping một IP `10.x` ngoài LAN | | | |

**Với mỗi lỗi, phải trả lời:**

- Gói ICMP có **rời khỏi máy** không? *(nhìn Wireshark)*
- `arp -a` hiện gì?
- Triệu chứng người dùng thấy là gì?

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

⚠️ **Nhớ khôi phục lại cấu hình mạng ban đầu sau khi làm xong lỗi 2 và 3.**

---

## 9. Challenge

1. Lọc `arp` rồi để Wireshark chạy 10 phút không làm gì. Vẫn có gói ARP không? Từ đâu ra?
2. Tìm một gói **Gratuitous ARP** (ARP hỏi chính IP của người gửi). Ai gửi? Để làm gì?
3. `ping 8.8.8.8 -f -l 1472` (Windows) rồi tăng dần kích thước. Tìm ngưỡng bắt đầu lỗi.
   Con số đó + 28 bằng bao nhiêu? Vì sao là 28?

<details>
<summary>Gợi ý câu 3</summary>

28 byte = **20 byte IP header + 8 byte ICMP header**. Nếu `1472 + 28 = 1500` là ngưỡng
thì MTU đường truyền của bạn là 1500 — chuẩn Ethernet. Nếu ngưỡng thấp hơn (vd 1452),
bạn đang đi qua **PPPoE hoặc tunnel** làm giảm MTU.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

**Bài 1 — ARP:**

| Gói | Src MAC | Dst MAC | Loại |
|---|---|---|---|
| Request | MAC máy bạn | `ff:ff:ff:ff:ff:ff` | **Broadcast** |
| Reply | MAC gateway | MAC máy bạn | **Unicast** |

Reply là unicast vì gateway **đã biết** MAC của người hỏi — nó đọc được từ trường
Source MAC của chính gói Request. Không cần broadcast lần nữa.

**Bài 2 — không có ARP cho `8.8.8.8`.**
Máy ARP hỏi **IP của default gateway**. Lý do: phép AND cho thấy `8.8.8.8` khác subnet
→ máy biết phải đưa gói cho router, nên chỉ cần MAC của router. Nó thậm chí không
quan tâm `8.8.8.8` ở đâu.

**Bài 3 — ICMP:**

| Gói | Type | Code | Tên |
|---|:---:|:---:|---|
| Đi | **8** | 0 | Echo Request |
| Về | **0** | 0 | Echo Reply |

TTL đi = 128 (Windows) hoặc 64 (Linux). TTL về thường ~`64 − số hop` hoặc `128 − số hop`
tuỳ hệ điều hành của máy đích. **Chênh lệch cho biết gói đã đi qua bao nhiêu router.**

**Bài 4 — traceroute:** TTL của gói đi lần lượt là **1, 2, 3**. Router thứ N nhận gói có
TTL=N, giảm còn 0, drop gói và gửi về **ICMP type 11 (Time Exceeded)** — chính nhờ đó
ta biết router đó là ai.

**BREAK:**

| # | Quan sát | Giải thích |
|:---:|---|---|
| 1 | Chỉ thấy ARP Request lặp lại, **không có Reply**. Gói ICMP **không bao giờ rời máy**. `arp -a` không có entry (hoặc `incomplete`) | Không điền được Dst MAC thì frame không tạo được. Gói chết **trong máy bạn**. |
| 2 | Có ARP Request hỏi gateway "ma", không ai trả lời. ICMP không rời máy. | Cùng cơ chế lỗi 1 — chỉ khác là lần này nạn nhân là gateway. |
| 3 | Máy **không ARP gateway** nữa mà ARP thẳng IP đích (vì `/16` làm nó tưởng cùng subnet). Không ai trả lời. | Mask sai → quyết định sai ngay từ phép AND. Đây chính là cơ chế của "ping một chiều". |

</details>

---

## 📝 Ghi chú & bài học rút ra

- Thứ bất ngờ nhất khi nhìn gói thật: ___
- Thứ tôi tưởng mình hiểu nhưng thật ra chưa: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
