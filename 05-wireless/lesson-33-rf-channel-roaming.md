# LESSON 33 — RF cơ bản · Băng tần · Kênh · Roaming

> 📌 Lesson giải thích **vì sao Wi-Fi chậm** — và gần như mọi lần người dùng kêu
> "wifi yếu", câu trả lời nằm trong lesson này.

| | |
|---|---|
| **Phase** | 5 — Wireless |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 32](./lesson-32-wlan-ap-wlc.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Giải thích vì sao 2.4 GHz **chỉ có 3 kênh không chồng lấn**
- [ ] Phân biệt **co-channel** và **adjacent-channel interference**
- [ ] Đọc **RSSI** và **SNR**, biết ngưỡng nào là "tốt"
- [ ] Hiểu channel width và vì sao **rộng hơn không phải lúc nào cũng tốt hơn**
- [ ] Giải thích roaming và **client mới là bên quyết định**

## 2. Prerequisite

- SSID/BSSID, kiến trúc WLC *(Lesson 32)*
- Wi-Fi là half-duplex, dùng chung môi trường *(Lesson 32)*

---

## 3. Concept

### Ba băng tần

| | **2.4 GHz** | **5 GHz** | **6 GHz** *(Wi-Fi 6E)* |
|---|---|---|---|
| Tầm phủ | **Xa nhất**, xuyên tường tốt | Trung bình | **Ngắn nhất** |
| Số kênh không chồng lấn | **Chỉ 3** | ~20+ *(tuỳ quốc gia, DFS)* | Nhiều nhất |
| Nhiễu | ⚠️ **Rất đông** | Ít | **Gần như sạch** |
| Tốc độ | Thấp nhất | Cao | Cao nhất |
| Thiết bị hỗ trợ | Mọi thiết bị | Hầu hết | Chỉ thiết bị mới |

> 🔑 **Nguồn nhiễu 2.4 GHz** không chỉ là Wi-Fi: **lò vi sóng**, Bluetooth,
> điện thoại không dây, camera analog, thiết bị y tế. Đây là băng tần **ISM dùng chung**
> cho mọi thiết bị không cần giấy phép.

### Vì sao 2.4 GHz chỉ có 3 kênh

```text
2.4 GHz có 14 kênh (Việt Nam dùng 1–13), mỗi kênh cách nhau 5 MHz.
NHƯNG mỗi kênh cần 20 MHz độ rộng!

Kênh 1:  2401 ──────── 2423 MHz
Kênh 2:       2406 ──────── 2428      ← CHỒNG LẤN kênh 1
Kênh 3:            2411 ──────── 2433 ← CHỒNG LẤN
...
Kênh 6:                      2426 ──────── 2448  ← KHÔNG chồng kênh 1 ✅
...
Kênh 11:                              2451 ──────── 2473 ← KHÔNG chồng kênh 6 ✅
```

```text
  ┌───1───┐       ┌───6───┐       ┌──11───┐
──┴───────┴───────┴───────┴───────┴───────┴──
        chỉ 1, 6, 11 là KHÔNG đè nhau
```

> ⭐ **Chỉ dùng kênh 1, 6, 11 ở 2.4 GHz.** Dùng kênh 3 hay 9 nghĩa là bạn đè lên
> **cả hai** kênh lân cận — tệ hơn nhiều so với dùng chung kênh với ai đó.

### Hai loại nhiễu — phân biệt rất quan trọng

| | **Co-Channel Interference (CCI)** | **Adjacent-Channel Interference (ACI)** |
|---|---|---|
| Khi nào | Hai AP **cùng kênh** | Hai AP **kênh chồng lấn một phần** (vd 1 và 3) |
| Thiết bị làm gì | **Lịch sự chờ nhau** (CSMA/CA) | **Không nhận ra nhau** → phát đè |
| Hậu quả | Chậm — chia sẻ airtime | **Hỏng gói, phải truyền lại** |
| Mức độ | ⚠️ Không tốt | ❌ **Tệ hơn nhiều** |

> 🔑 Đây là nghịch lý quan trọng nhất của RF:
> **Dùng chung kênh 1 với hàng xóm TỐT HƠN dùng kênh 3.**
>
> Cùng kênh → thiết bị "nghe thấy" nhau và nhường nhau.
> Kênh chồng một phần → chúng **không giải mã được** tín hiệu của nhau, chỉ thấy
> "nhiễu nền" và cứ phát đè lên.

### Channel width — rộng hơn không phải lúc nào cũng tốt

| Width | Tốc độ | Số kênh khả dụng | Nên dùng ở |
|:---:|---|:---:|---|
| **20 MHz** | Cơ bản | Nhiều nhất | ⭐ **2.4 GHz — LUÔN LUÔN** |
| **40 MHz** | ~2× | Một nửa | 5 GHz, mật độ trung bình |
| **80 MHz** | ~4× | 1/4 | 5 GHz, mật độ thấp |
| **160 MHz** | ~8× | Rất ít | Chỉ 6 GHz, môi trường sạch |

> ⚠️ **Ở 2.4 GHz, LUÔN dùng 20 MHz.** Dùng 40 MHz chiếm gần như toàn bộ phổ
> → đè lên chính các AP khác của bạn → tệ hơn hẳn.

> 🔑 Đánh đổi: **rộng hơn = nhanh hơn cho một client, nhưng ít kênh hơn = nhiều
> co-channel interference hơn**. Ở môi trường đông AP, **80 MHz có thể CHẬM HƠN 40 MHz**.

### RSSI và SNR — hai con số phải đọc được

| Chỉ số | Là gì | Đơn vị |
|---|---|---|
| **RSSI** | **Cường độ** tín hiệu nhận được | dBm *(số âm)* |
| **Noise floor** | Mức nhiễu nền | dBm *(số âm)* |
| **SNR** | **RSSI − Noise floor** — tín hiệu nổi hơn nhiễu bao nhiêu | dB |

**Thang đánh giá:**

| RSSI | Chất lượng | Dùng được cho |
|---|---|---|
| −30 đến −50 dBm | **Xuất sắc** | Mọi thứ |
| −50 đến −60 dBm | **Tốt** | Video, thoại |
| −60 đến −67 dBm | **Chấp nhận** | ⭐ Ngưỡng thiết kế cho VoIP |
| −67 đến −70 dBm | Yếu | Chỉ duyệt web |
| Dưới −70 dBm | **Kém** | Chập chờn |

| SNR | Chất lượng |
|---|---|
| > 40 dB | Xuất sắc |
| 25–40 dB | **Tốt** |
| **> 20 dB** | ⭐ Ngưỡng tối thiểu cho dữ liệu |
| **> 25 dB** | ⭐ Ngưỡng tối thiểu cho **thoại** |
| < 15 dB | Không dùng được |

> 🔑 **SNR quan trọng hơn RSSI.** Tín hiệu mạnh (−45 dBm) nhưng nhiễu nền cũng cao
> (−50 dBm) → SNR chỉ 5 dB → **không dùng được**. Tín hiệu yếu hơn (−65 dBm)
> nhưng nền sạch (−95 dBm) → SNR 30 dB → **chạy tốt**.

> 💡 Hiểu dBm: đây là thang **logarit**. Mỗi **−3 dBm** = công suất **giảm một nửa**.
> Chênh lệch từ −50 xuống −60 dBm là **giảm 10 lần** công suất.

### Roaming — client quyết định, không phải AP

```text
1. Client đang kết nối AP1, RSSI giảm dần khi di chuyển
2. Client tự quét tìm AP khác cùng SSID
3. Khi tìm được AP2 có tín hiệu tốt hơn ĐỦ NGƯỠNG (thường chênh 5–10 dB)
   → client tự quyết định chuyển
4. Client gửi Reassociation Request tới AP2
5. Xác thực lại (nhanh nếu có cơ chế fast roaming)
6. WLC chuyển session sang AP2
```

> ⭐ **Điểm quan trọng nhất: AP KHÔNG đẩy client đi. CLIENT tự quyết định.**
>
> Hệ quả: một client "cứng đầu" (sticky client) có thể bám AP cũ ở −80 dBm
> trong khi có AP khác ở −45 dBm ngay cạnh. Bạn **không ép được** nó —
> chỉ có thể tạo điều kiện (giảm công suất AP, bật band steering).

### Ba cơ chế fast roaming

| Cơ chế | Chuẩn | Làm gì |
|---|---|---|
| **802.11r** | Fast BSS Transition | Trao khoá trước khi roam → chuyển < 50 ms |
| **802.11k** | Neighbor Report | AP **gợi ý** cho client danh sách AP lân cận |
| **802.11v** | BSS Transition Management | AP **đề nghị** client chuyển sang AP khác |

> 🏭 Ba chuẩn này quan trọng với **VoIP Wi-Fi** — roaming chậm quá 150 ms là rớt cuộc gọi.
> Nhưng một số thiết bị cũ **không tương thích** với 802.11r và sẽ không kết nối được.
> Giải pháp: tạo SSID riêng cho thoại có bật 802.11r.

---

## 4. Why?

> **Vì sao "tăng công suất AP" thường làm mọi thứ tệ hơn?**

```text
Tăng công suất AP:
  ✅ Client NGHE AP rõ hơn
  ❌ AP vẫn KHÔNG nghe client rõ hơn    ← công suất client không đổi!
  ❌ Vùng phủ rộng ra → đè lên AP khác → tăng co-channel interference
  ❌ Client ở xa bám AP lâu hơn → truyền ở tốc độ thấp → chiếm airtime
```

> ⭐ **Wi-Fi là giao tiếp hai chiều.** Công suất AP chỉ quyết định chiều đi;
> chiều về phụ thuộc công suất của **client** (điện thoại ~15 dBm, AP có thể 20+ dBm).
>
> Thiết kế đúng: **nhiều AP, công suất THẤP** — không phải ít AP công suất cao.

> **Vì sao nên ưu tiên 5 GHz?**

| | 2.4 GHz | 5 GHz |
|---|---|---|
| Kênh | 3 | 20+ |
| Nhiễu ngoài Wi-Fi | Lò vi sóng, Bluetooth… | Gần như không |
| Mật độ AP có thể triển khai | Thấp | Cao |

**Band steering**: WLC "đẩy" client hỗ trợ 5 GHz sang 5 GHz bằng cách trì hoãn
trả lời probe ở 2.4 GHz. Để 2.4 GHz cho thiết bị cũ và IoT.

---

## 5. How does it work? — vì sao một client yếu làm chậm cả nhóm

```text
AP có 10 client:
  9 client gần, truyền ở 400 Mbps
  1 client xa, truyền ở 6 Mbps

Để gửi 1 MB dữ liệu:
  Client nhanh:  1 MB ÷ 400 Mbps ≈ 0.02 giây
  Client chậm:   1 MB ÷ 6 Mbps   ≈ 1.33 giây   ← chiếm airtime GẤP 65 LẦN

Trong 1.33 giây đó, 9 client kia PHẢI CHỜ.
```

> ⭐ Đây gọi là **"slow client problem"** hay **airtime unfairness**.
> Một thiết bị cũ ở góc phòng có thể làm chậm cả văn phòng.

**Hai cách xử lý:**

| Cách | Làm gì |
|---|---|
| **Minimum data rate** | Tắt các tốc độ thấp (1, 2, 5.5, 11 Mbps) → client quá yếu **không kết nối được**, buộc phải roam sang AP gần hơn |
| **Airtime fairness** | WLC chia **thời gian** đều thay vì chia **lượt gửi** |

---

## 6. Packet Flow — CSMA/CA

```text
1. Client muốn gửi → LẮNG NGHE kênh
2. Kênh bận?  → chờ ngẫu nhiên (backoff) rồi nghe lại
3. Kênh rảnh? → chờ thêm một khoảng (DIFS) cho chắc
4. Gửi frame
5. CHỜ ACK từ AP
   ├─ Có ACK   → xong
   └─ Không ACK → coi như va chạm → backoff dài hơn, gửi LẠI
```

> 🔑 **Vì sao Wi-Fi dùng CA (tránh) chứ không CD (phát hiện) như Ethernet:**
> thiết bị không dây **không thể vừa phát vừa nghe** trên cùng tần số —
> tín hiệu của chính nó át hết. Nên nó phải **né trước** thay vì phát hiện sau.

> ⚠️ Mỗi frame đều cần **ACK**. Đây là overhead lớn và là một lý do nữa
> khiến throughput thực chỉ bằng ~50–60% tốc độ vật lý.

---

## 7. Real-world Example

🏭 **Kế hoạch kênh cho một tầng 6 AP**

```text
2.4 GHz — chỉ 3 kênh, phải lặp lại:
    AP1(1)   AP2(6)   AP3(11)
    AP4(1)   AP5(6)   AP6(11)
    → đặt AP cùng kênh CÁCH XA NHAU nhất có thể

5 GHz — nhiều kênh, không phải lặp:
    AP1(36)  AP2(40)  AP3(44)
    AP4(48)  AP5(149) AP6(153)
```

> 🔧 Với WLC, **RRM (Radio Resource Management)** tự làm việc này và tự điều chỉnh
> khi môi trường thay đổi. Nhưng bạn vẫn cần hiểu nguyên lý để kiểm tra RRM làm đúng.

🏭 **Sự cố: "Wi-Fi phòng họp rất tệ khi đông người"**

| Nguyên nhân | Chẩn đoán |
|---|---|
| Quá nhiều client trên một AP | WLC → số client/AP |
| Thiết kế theo diện tích, không theo mật độ | Đếm người vs số AP |
| Dùng 40 MHz ở 2.4 GHz | Kiểm tra channel width |
| Một laptop cũ kéo chậm cả phòng | WLC → xem data rate từng client |

Cách sửa: thêm AP cho phòng họp, **giảm công suất** mỗi AP, bật **minimum data rate**,
đảm bảo 5 GHz được ưu tiên.

🏭 **Sticky client — vấn đề không có giải pháp hoàn hảo**

Nhân viên đi từ tầng 1 lên tầng 2, điện thoại vẫn bám AP tầng 1 ở −78 dBm
dù AP tầng 2 ở −45 dBm.

| Giảm nhẹ | Cách |
|---|---|
| Giảm công suất AP | Vùng phủ nhỏ hơn → client buộc phải roam sớm hơn |
| Bật **802.11v** | AP **đề nghị** client chuyển *(client có thể từ chối)* |
| **Minimum data rate** | Client quá yếu bị ngắt → buộc kết nối lại với AP tốt hơn |
| Cập nhật driver/firmware client | Nhiều vấn đề roaming là do phía client |

> ⚠️ Không có cách nào **ép** client roam. Chuẩn 802.11 đặt quyền quyết định ở client,
> và đó là điều bạn phải chấp nhận khi thiết kế.

---

## 8. Cisco CLI

> 💡 RF chủ yếu cấu hình trên **WLC qua GUI**. Phần quan trọng với bạn là
> **đo đạc và chẩn đoán**.

**Trên WLC (CLI):**

```text
(WLC) > show ap config general <AP-name>
(WLC) > show ap channel <AP-name>
(WLC) > show ap auto-rf 802.11a <AP-name>
(WLC) > show client detail <MAC>
(WLC) > config 802.11a channel ap <AP-name> 36
(WLC) > config 802.11a txpower ap <AP-name> 3
(WLC) > config 802.11b 11gsupport enable
```

**Trên máy tính — đo đạc thực tế:**

```powershell
# Windows — xem RSSI, kênh, BSSID của các mạng xung quanh
netsh wlan show networks mode=bssid

# Windows — thông tin kết nối hiện tại
netsh wlan show interfaces

# Linux
sudo iw dev wlan0 scan | grep -E "SSID|signal|freq|DS Parameter"
iw dev wlan0 link

# macOS
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I
```

```text
# output điển hình — tự chạy trên máy bạn
C:\> netsh wlan show interfaces
    SSID                   : CTY-NHANVIEN
    BSSID                  : 00:1a:2b:3c:4d:50
    Radio type             : 802.11ax
    Band                   : 5 GHz
    Channel                : 44
    Signal                 : 82%
    Receive rate (Mbps)    : 866
    Transmit rate (Mbps)   : 866
```

> 🔧 **`Signal` dạng %** của Windows không phải dBm. Quy đổi thô:
> `100% ≈ −50 dBm`, `50% ≈ −75 dBm`, `0% ≈ −100 dBm`.
> Muốn số chính xác, dùng công cụ khảo sát chuyên dụng.

---

## 9. Verification

```text
# output điển hình — tự verify trên WLC của bạn
(WLC) > show ap auto-rf 802.11a AP-TANG1-01
Number Of Slots.................................. 2
AP Name.......................................... AP-TANG1-01
  Channel Assignment
    Current Channel Average Energy................ -78 dBm
    Previous Channel Average Energy............... -80 dBm
    Channel Change Count.......................... 3
  Transmit Power
    Current Tx Power Level........................ 3
    Recommended Tx Power Level.................... 3
  Noise Information
    Noise Profile................................. PASSED
    Channel 36.................................... -92 dBm
    Channel 40.................................... -91 dBm
  Interference Information
    Interference Profile.......................... PASSED
  Load Information
    Load Profile.................................. PASSED
    Receive Utilization........................... 12 %
    Transmit Utilization.......................... 18 %
    Channel Utilization........................... 34 %
    Attached Clients.............................. 22 clients
```

**Đọc gì:**

| Field | Ý nghĩa | Ngưỡng cảnh báo |
|---|---|---|
| `Noise` | Nhiễu nền | **Trên −85 dBm** → môi trường nhiễu |
| **`Channel Utilization`** | ⭐ Kênh bận bao nhiêu % | **> 50%** → nghẽn, cần thêm AP |
| `Attached Clients` | Số client | **> 30** → quá tải |
| `Channel Change Count` | RRM đổi kênh mấy lần | Tăng liên tục → môi trường bất ổn |
| `Tx Power Level` | 1 = cao nhất, 8 = thấp nhất | Mức 1 ở mọi AP → có thể đang thiếu AP |

> 🔑 **`Channel Utilization` là chỉ số quan trọng nhất** để biết Wi-Fi có nghẽn hay không.
> Nó tính cả traffic của bạn **và** của hàng xóm trên cùng kênh.

```text
# output điển hình — tự verify trên WLC của bạn
(WLC) > show client detail 00:11:22:33:44:55
Client MAC Address............................... 00:11:22:33:44:55
AP Name.......................................... AP-TANG1-01
Channel.......................................... 44
Radio Type....................................... 802.11ax
Signal Strength.................................. -58 dBm
Signal to Noise Ratio............................ 34 dB
Data Rate........................................ 866.0 Mbps
```

| Chỉ số | Giá trị này | Đánh giá |
|---|---|---|
| `Signal Strength: -58 dBm` | Tốt | ✅ |
| `SNR: 34 dB` | Tốt | ✅ |
| `Data Rate: 866 Mbps` | Cao | ✅ |

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Cách kiểm chứng | Cách sửa |
|---|---|---|---|
| Wi-Fi chậm khi đông người | **Channel utilization cao** | `show ap auto-rf` | Thêm AP, giảm công suất, dùng 5 GHz |
| Tín hiệu mạnh nhưng vẫn chậm | **SNR thấp** — nhiễu nền cao | `show client detail` xem SNR | Tìm nguồn nhiễu, đổi kênh |
| 2.4 GHz rất tệ, 5 GHz ổn | Nhiễu từ thiết bị không phải Wi-Fi | Spectrum analyzer | Chuyển client sang 5 GHz, band steering |
| Client bám AP xa ở tín hiệu yếu | **Sticky client** | `show client detail` xem RSSI | Giảm công suất AP, bật 802.11v, min data rate |
| Rớt cuộc gọi khi đi lại | **Roaming chậm** | Đo thời gian roam | Bật **802.11r** (SSID riêng cho thoại) |
| Dùng kênh 3, 9 | **Adjacent-channel interference** | `netsh wlan show networks mode=bssid` | Chỉ dùng **1, 6, 11** |
| Một laptop cũ làm chậm cả phòng | **Slow client problem** | WLC xem data rate từng client | Bật minimum data rate |
| Tăng công suất AP mà càng tệ | Nghe một chiều + tăng CCI | So RSSI client báo cáo | **Giảm** công suất, **thêm** AP |
| 40 MHz ở 2.4 GHz | Chiếm hết phổ | WLC xem channel width | Đổi về **20 MHz** |

---

## 11. LAB

🧪 **Bài khảo sát thực tế** *(làm trên máy thật — có giá trị hơn mô phỏng)*

### Bài 1 — Khảo sát môi trường

```powershell
netsh wlan show networks mode=bssid > wifi-survey.txt
```

Điền bảng:

| SSID | BSSID | Kênh | Băng tần | Signal |
|---|---|:---:|:---:|:---:|
| | | | | |

**Câu hỏi:**
- Có bao nhiêu mạng ở 2.4 GHz? Chúng dùng kênh nào?
- Có mạng nào dùng kênh **khác 1, 6, 11** không? *(= đang gây ACI)*
- Kênh nào đông nhất?

### Bài 2 — Đo tín hiệu theo khoảng cách

```powershell
netsh wlan show interfaces
```

Đo ở 4 vị trí, ghi lại `Signal` và `Receive rate`:

| Vị trí | Signal (%) | ≈ RSSI | Receive rate |
|---|:---:|:---:|:---:|
| Cạnh AP | | | |
| Cách 5 m | | | |
| Qua 1 tường | | | |
| Qua 2 tường | | | |

**Câu hỏi:** tốc độ giảm bao nhiêu lần qua mỗi bức tường?

### Bài 3 — Quan sát roaming

Vừa `ping -t` gateway vừa đi từ phòng này sang phòng khác.
Ghi lại: BSSID có đổi không? Mất bao nhiêu gói khi roam?

### Bài 4 — Nhiễu từ lò vi sóng

Bật lò vi sóng, đứng gần, chạy `ping -t` tới gateway qua **2.4 GHz**.
Quan sát độ trễ và mất gói. Lặp lại trên **5 GHz** → so sánh.

## 12. Challenge

1. Hàng xóm dùng kênh 1 rất mạnh. Bạn nên chọn kênh 1, 3, hay 6? Giải thích.
2. Client A: RSSI −45 dBm, noise −50 dBm. Client B: RSSI −65 dBm, noise −95 dBm.
   Ai có kết nối tốt hơn? Tính SNR.
3. Vì sao tăng công suất AP thường không giải quyết được vấn đề vùng phủ?
4. Phòng họp 40 người, 1 AP, `Channel Utilization 85%`. Nêu 3 cách xử lý theo
   thứ tự ưu tiên.

<details>
<summary>Đáp án</summary>

**1.** Chọn **kênh 6** *(hoặc 11)* — tức là **kênh không chồng lấn với kênh 1**.

Nếu buộc phải chọn giữa 1 và 3:

| Chọn | Hậu quả |
|---|---|
| **Kênh 1** *(cùng hàng xóm)* | **CCI** — hai mạng "nghe thấy" nhau, lịch sự nhường nhau qua CSMA/CA. Chậm nhưng **hoạt động được** |
| **Kênh 3** | **ACI** — hai mạng không giải mã được nhau, chỉ thấy nhiễu nền → **phát đè lên nhau** → hỏng gói, phải truyền lại liên tục |

👉 **Cùng kênh tốt hơn kênh chồng lấn một phần.** Đây là điều trái trực giác nhưng rất quan trọng.

**2.**

| Client | RSSI | Noise | **SNR** | Đánh giá |
|---|---|---|:---:|---|
| **A** | −45 dBm | −50 dBm | **5 dB** | ❌ **Không dùng được** |
| **B** | −65 dBm | −95 dBm | **30 dB** | ✅ **Tốt** |

**Client B tốt hơn nhiều**, dù tín hiệu yếu hơn 20 dBm.

Lý do: tín hiệu của A chỉ nổi hơn nhiễu **5 dB** — gần như chìm trong nhiễu,
không giải mã được. B có tín hiệu yếu hơn nhưng môi trường **sạch**, tín hiệu
nổi rõ hơn nhiễu 30 dB.

👉 **SNR quan trọng hơn RSSI.**

**3.** Vì **Wi-Fi là giao tiếp hai chiều**:

```text
Tăng công suất AP → client nghe AP rõ hơn
                  → NHƯNG AP vẫn không nghe client rõ hơn
                     (công suất điện thoại ~15 dBm, không đổi)
```

Kết quả: client ở xa **thấy** vạch sóng đầy nhưng **không gửi được** dữ liệu ổn định —
giao tiếp một chiều.

Thêm hai tác hại: vùng phủ rộng ra → **đè lên AP khác** (tăng CCI); và client xa
**bám AP lâu hơn** → truyền ở tốc độ thấp → chiếm airtime.

👉 Giải pháp đúng: **nhiều AP công suất thấp**, không phải ít AP công suất cao.

**4.** Theo thứ tự ưu tiên:

| # | Cách | Vì sao thứ tự này |
|:---:|---|---|
| **1** | **Thêm AP** cho phòng họp, **giảm công suất** tất cả AP | Giải quyết gốc: chia 40 client ra nhiều AP. Giảm công suất để các AP không đè nhau |
| **2** | Ép dùng **5 GHz** (band steering), đảm bảo channel width **20–40 MHz** | Nhiều kênh hơn → ít co-channel interference |
| **3** | Bật **minimum data rate**, tắt tốc độ thấp (1/2/5.5/11 Mbps) | Loại bỏ slow client kéo chậm cả nhóm |

Không nên: tăng công suất AP hiện có *(làm tệ hơn)*, hoặc thêm SSID *(tốn airtime)*.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 3 kênh 2.4 GHz · ngưỡng RSSI/SNR · CCI vs ACI | ⬜ |
| **L2** Explain | Giải thích vì sao tăng công suất AP không giúp vùng phủ | ⬜ |
| **L3** Configure | Lập kế hoạch kênh cho 6 AP ở cả 2 băng tần | ⬜ |
| **L4** Troubleshoot | "Wi-Fi chậm khi đông người" → nêu quy trình chẩn đoán | ⬜ |
| **L5** Design | Thiết kế RF cho một tầng văn phòng: số AP, kênh, công suất, width | ⬜ |

## 14. Summary

**Key concepts**

- ⭐ **2.4 GHz chỉ có 3 kênh không chồng lấn: 1, 6, 11**
- ⭐ **CCI (cùng kênh) TỐT HƠN ACI (kênh chồng một phần)** — cùng kênh thì nhường nhau
- Ở **2.4 GHz luôn dùng 20 MHz**; rộng hơn = nhanh hơn nhưng ít kênh hơn
- **RSSI** = cường độ *(dBm, số âm)* · **SNR** = RSSI − noise *(dB)*
- ⭐ **SNR quan trọng hơn RSSI**. Ngưỡng: dữ liệu > 20 dB, thoại > 25 dB
- Thiết kế VoIP: RSSI tốt hơn **−67 dBm**
- Mỗi **−3 dBm** = công suất giảm **một nửa**
- ⭐ **Client quyết định roam, không phải AP** → sticky client không ép được
- Fast roaming: **802.11r** (khoá) · **802.11k** (gợi ý) · **802.11v** (đề nghị)
- ⭐ **Tăng công suất AP thường làm tệ hơn** — Wi-Fi hai chiều, client không mạnh lên
- **Slow client problem**: một client yếu chiếm airtime gấp hàng chục lần
- Chỉ số quan trọng nhất để đo nghẽn: **Channel Utilization** *(> 50% là có vấn đề)*

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `netsh wlan show networks mode=bssid` | Khảo sát kênh, BSSID xung quanh |
| `netsh wlan show interfaces` | RSSI, kênh, tốc độ của kết nối hiện tại |
| `show ap auto-rf 802.11a <ap>` | ⭐ Noise, utilization, số client |
| `show client detail <mac>` | RSSI, SNR, data rate của một client |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Dùng kênh 3, 9 ở 2.4 GHz | **ACI** — tệ hơn dùng chung kênh |
| Dùng 40 MHz ở 2.4 GHz | Chiếm hết phổ, đè lên chính AP của mình |
| Tăng công suất để phủ xa hơn | Giao tiếp một chiều + tăng CCI |
| Chỉ nhìn RSSI, bỏ qua SNR | Tín hiệu mạnh trong môi trường nhiễu vẫn không dùng được |
| Nghĩ AP có thể ép client roam | **Client quyết định** |
| Bỏ qua slow client | Một thiết bị cũ làm chậm cả văn phòng |
| Thiết kế theo diện tích | Phòng họp đông người Wi-Fi tệ |

## 15. Homework + cập nhật PROGRESS

1. Làm cả 4 bài khảo sát ở mục 11 — đặc biệt **bài 4 (lò vi sóng)**, nó cho bạn
   cảm nhận trực tiếp về nhiễu 2.4 GHz.
2. Khảo sát văn phòng/nhà bạn: vẽ sơ đồ AP và kênh chúng đang dùng. Có AP nào
   dùng kênh ngoài 1/6/11 không?
3. Tính: nếu RSSI giảm từ −50 xuống −65 dBm, công suất giảm bao nhiêu lần?

```markdown
- [YYYY-MM-DD] Lesson 33 — RF, kênh, roaming: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | 3 kênh 2.4 GHz, băng tần, CCI vs ACI, roaming, ngưỡng RSSI/SNR |
| 🔧 **Engineer** | Kế hoạch kênh; 20 MHz ở 2.4; đọc Channel Utilization; minimum data rate |
| 🏭 **Production** | Nhiều AP công suất thấp; sticky client không ép được; slow client kéo chậm cả nhóm |

### 🔗 Liên kết

- ⬅️ [Lesson 32 — WLAN, AP, WLC](./lesson-32-wlan-ap-wlc.md)
- ➡️ [Lesson 34 — Bảo mật Wi-Fi](./lesson-34-bao-mat-wifi.md)
- 🔜 RF design sâu: [`CCNP-Encor` Module 07A](https://github.com/hiepnguyen775/CCNP-Encor)
