# LAB 03 — TCP 3-way Handshake vs UDP

| | |
|---|---|
| **Phase** | 0 |
| **Lesson liên quan** | [Lesson 06 — TCP vs UDP](../00-foundation/lesson-06-tcp-udp-port.md) |
| **Công cụ** | **Wireshark trên máy thật** |
| **Thời lượng** | ~1.5 giờ |
| **Độ khó** | ⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Nhìn thấy đủ 3 gói handshake và đọc được seq/ack đổi thế nào
- [ ] Chứng minh UDP **không** có handshake
- [ ] Phân biệt **drop** và **reject** bằng gói tin thật, không bằng lý thuyết
- [ ] Chứng minh nhiều kết nối tới cùng server được phân biệt bằng **source port**

## 2. Prerequisite

- [Lesson 06](../00-foundation/lesson-06-tcp-udp-port.md) — TCP/UDP, port, flag
- [`cheatsheets/wireshark.md`](../cheatsheets/wireshark.md)

## 3. Chuẩn bị

Chạy trên máy thật. Không cần dựng topology.

---

## 4. Yêu cầu LAB

- [ ] Bắt trọn 3-way handshake, điền bảng seq/ack
- [ ] Bắt DNS query/response (UDP) và chỉ ra nó **không** có handshake
- [ ] Tạo được tình huống `RST` và tình huống timeout, phân biệt hai cái
- [ ] Đếm số kết nối TCP một trang web mở ra
- [ ] Hoàn thành mục **8. BREAK**

---

## 5. Step-by-step

### Bài 1 — 3-way handshake

```text
Filter:  tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Mở trình duyệt vào một trang bất kỳ. Dừng bắt gói. Chọn một gói SYN,
chuột phải → **Follow → TCP Stream**, rồi quay lại xem 3 gói đầu.

| # | Hướng | Flags | Seq | Ack | Src Port | Dst Port |
|:---:|---|---|---|---|---|---|
| 1 | Client → Server | | | | | |
| 2 | Server → Client | | | | | |
| 3 | Client → Server | | | | | |

**Câu hỏi:**

- Seq của gói 1 là bao nhiêu? *(Wireshark hiển thị seq tương đối, mặc định bắt đầu từ 0)*
- Ack của gói 2 bằng seq gói 1 cộng mấy? **Vì sao?**
- Source port nằm trong dải nào? Nó được chọn thế nào?

### Bài 2 — UDP không có handshake

```text
Filter:  dns
```

```powershell
ipconfig /flushdns
nslookup github.com
```

| # | Hướng | Giao thức | Src Port | Dst Port | Info |
|:---:|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

**Câu hỏi:** có bao nhiêu gói cho **một** truy vấn? So với TCP cần mấy gói chỉ để *bắt đầu*?

### Bài 3 — Drop vs Reject

```text
Filter:  tcp
```

Chạy lần lượt và quan sát:

```powershell
# A. Port chắc chắn mở
Test-NetConnection google.com -Port 443

# B. Port chắc chắn đóng trên máy tồn tại (thử trên chính máy bạn)
Test-NetConnection 127.0.0.1 -Port 9999

# C. Port bị firewall drop (thử một IP public, port lạ)
Test-NetConnection 8.8.8.8 -Port 9999
```

| Trường hợp | Gói thấy trong Wireshark | Thời gian phản hồi | Kết luận |
|---|---|---|---|
| A | | | |
| B | | | |
| C | | | |

> 🔑 Đây là bài quan trọng nhất của lab. Phân biệt được drop và reject
> tiết kiệm cho bạn hàng giờ debug sau này.

### Bài 4 — Nhiều kết nối, một server

```text
Filter:  tcp.flags.syn == 1 && tcp.flags.ack == 0 && ip.dst == <IP của trang web>
```

Mở một trang web lớn (báo, thương mại điện tử).

| Số gói SYN đếm được | |
|---|---|
| Các Dst Port | |
| Các Src Port | |

**Câu hỏi:** Dst Port giống hay khác nhau? Src Port giống hay khác nhau?
Server phân biệt các kết nối này bằng gì?

### Bài 5 — Đóng kết nối

```text
Filter:  tcp.flags.fin == 1 || tcp.flags.reset == 1
```

Mở rồi đóng một trang web. Đếm số gói FIN và RST.

**Câu hỏi:** trình duyệt hiện đại đóng kết nối bằng `FIN` (lịch sự) hay `RST` (đột ngột)?
Vì sao?

---

## 6. Verification

- [ ] Bài 1: thấy đủ `SYN` → `SYN,ACK` → `ACK`
- [ ] Bài 2: DNS chỉ 2 gói, không có SYN
- [ ] Bài 3: trường hợp B có `RST`, trường hợp C chỉ có `SYN` lặp lại
- [ ] Bài 4: nhiều SYN, cùng Dst Port, khác Src Port
- [ ] Bài 5: đếm được FIN/RST

---

## 7. BREAK → Troubleshooting ⚠️ BẮT BUỘC

| # | Cố tình làm sai | Dự đoán | Quan sát | Giải thích |
|:---:|---|---|---|---|
| 1 | Chặn port 443 ra ngoài bằng Windows Firewall, rồi mở web | | | |
| 2 | Đổi DNS server của máy sang IP không tồn tại (vd `10.99.99.99`), rồi `nslookup` | | | |
| 3 | `nslookup google.com` rồi `ping google.com` — khi DNS hỏng, triệu chứng khác nhau thế nào? | | | |

**Với mỗi lỗi, phải trả lời:**

- Gói nào xuất hiện / không xuất hiện trong Wireshark?
- Người dùng sẽ mô tả triệu chứng này như thế nào?
- Nếu chỉ nghe mô tả của người dùng, bạn sẽ kiểm tra gì đầu tiên?

> ⚠️ Nhớ khôi phục firewall và DNS sau khi làm xong.
> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 8. Challenge

1. Tìm một gói có cờ `PSH`. Nó xuất hiện khi nào, và vì sao?
2. Filter `tcp.analysis.retransmission` — mạng bạn có gói nào bị gửi lại không?
   Tỷ lệ bao nhiêu % là đáng lo?
3. Mở `Statistics → Conversations → TCP`. Kết nối nào truyền nhiều byte nhất?
   Nó đi tới đâu?
4. Vì sao Wireshark hiển thị `Seq=0` cho gói SYN đầu tiên trong khi TCP thật dùng
   số ngẫu nhiên lớn?

<details>
<summary>Đáp án</summary>

**1.** `PSH` yêu cầu bên nhận đẩy dữ liệu lên ứng dụng **ngay** thay vì chờ đầy buffer.
Hay thấy ở traffic tương tác: SSH (mỗi phím gõ), hoặc gói cuối của một HTTP response.

**2.** Dưới **0.5%** là bình thường trên mạng Internet. Trên **2–3%** thường gây chậm rõ rệt
và nên điều tra: lỗi interface, băng thông đầy, hoặc Wi-Fi nhiễu.

**3.** Thường là video/streaming hoặc cập nhật hệ điều hành. Đây là cách nhanh nhất
để trả lời câu hỏi *"ai đang ngốn băng thông"*.

**4.** Wireshark mặc định bật **relative sequence numbers** để dễ đọc. Tắt ở
*Edit → Preferences → Protocols → TCP → bỏ tick "Relative sequence numbers"*
sẽ thấy số thật (ISN ngẫu nhiên). Số ngẫu nhiên là **biện pháp bảo mật** — nếu đoán được ISN,
kẻ tấn công có thể chèn gói giả vào kết nối đang chạy.

</details>

---

## 9. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

**Bài 1:**

| # | Flags | Seq | Ack | Giải thích |
|:---:|---|:---:|:---:|---|
| 1 | `SYN` | 0 | — | Client công bố số thứ tự ban đầu |
| 2 | `SYN, ACK` | 0 | **1** | Ack = seq client **+1** — xác nhận đã nhận SYN |
| 3 | `ACK` | 1 | **1** | Client xác nhận SYN của server |

Ack = seq + 1 vì cờ `SYN` **được tính là 1 byte** trong không gian sequence,
dù nó không mang dữ liệu nào.

Source port nằm trong dải **ephemeral** `49152–65535`, do OS chọn (thường ngẫu nhiên
để chống đoán).

**Bài 2:** DNS chỉ **2 gói** — 1 query + 1 response. TCP cần **3 gói chỉ để bắt đầu**,
chưa truyền byte dữ liệu nào. Đây chính là lý do DNS chọn UDP.

**Bài 3:**

| TH | Gói thấy | Thời gian | Kết luận |
|---|---|---|---|
| A | `SYN` → `SYN,ACK` → `ACK` | < 100 ms | Port **mở** |
| B | `SYN` → **`RST, ACK`** | Tức thì | **Reject** — máy tồn tại, không có service |
| C | `SYN` lặp lại 2–3 lần, không có gì về | ~20–30 giây | **Drop** — firewall nuốt im lặng |

**Bài 4:** Nhiều gói SYN (thường 4–10 với trang web lớn). **Dst Port giống nhau** (443).
**Src Port khác nhau** hoàn toàn. Server phân biệt bằng **socket 4 giá trị** —
chỉ cần Src Port khác là đã thành kết nối riêng biệt.

**Bài 5:** Trình duyệt hiện đại thường dùng `FIN` để đóng lịch sự (cho phép server dọn
tài nguyên sạch sẽ), nhưng cũng hay thấy `RST` khi đóng tab đột ngột hoặc khi
kết nối bị huỷ giữa chừng.

**BREAK:**

| # | Quan sát | Triệu chứng người dùng | Kiểm tra đầu tiên |
|:---:|---|---|---|
| 1 | Chỉ thấy `SYN` lặp lại, không có `SYN,ACK` | *"Web load mãi rồi lỗi"* | `telnet <host> 443` — treo hay refuse? |
| 2 | Gói DNS gửi tới `10.99.99.99`, **không có response** | *"Vào web nào cũng không được"* | `ping 8.8.8.8` vs `ping google.com` |
| 3 | `nslookup` fail ngay với lỗi DNS; `ping google.com` báo *"could not find host"* — **không có gói ICMP nào được gửi** | *"Mất mạng"* | Cặp lệnh `ping 8.8.8.8` + `ping google.com` |

Điểm mấu chốt của lỗi 3: khi DNS hỏng, `ping google.com` **thất bại trước khi gửi gói nào**.
Người dùng báo "mất mạng" nhưng mạng hoàn toàn bình thường.

</details>

---

## 📝 Ghi chú & bài học rút ra

- Thứ bất ngờ nhất: ___
- Bài drop-vs-reject giúp tôi hiểu ra: ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
