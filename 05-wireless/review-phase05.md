# MODULE REVIEW — Phase 5: Wireless

| | |
|---|---|
| **Phase** | 5 — Wireless |
| **Số lesson** | 3 (32 → 34) |
| **Thời lượng dự kiến** | 1 tuần |
| **Ngày hoàn thành** | — |

---

## 1. Summary — Phase 5 trong 8 câu

1. 802.11 là công nghệ **Layer 2** — từ L3 trở lên giống hệt mạng có dây.
2. ⭐ Wi-Fi **half-duplex, dùng chung môi trường** → throughput thực ~50–60% con số quảng cáo.
3. **SSID** = tên · **BSSID** = MAC radio · **ESS** = nhiều AP cùng SSID; một AP có
   `số SSID × số băng tần` BSSID.
4. **Local mode** đưa traffic về tận WLC; **FlexConnect** cho chi nhánh — xuống thẳng switch.
5. ⭐ **2.4 GHz chỉ có 3 kênh không chồng lấn: 1, 6, 11.** CCI tốt hơn ACI.
6. ⭐ **SNR quan trọng hơn RSSI**; thiết kế VoIP cần RSSI > −67 dBm, SNR > 25 dB.
7. ⭐ **Client quyết định roam, không phải AP**; tăng công suất AP thường làm tệ hơn.
8. ⭐ **PSK không truy vết được**; Enterprise cho mỗi client một **PMK riêng** —
   an toàn hơn cả về quản lý lẫn mã hoá.

## 2. Key Concepts

| Concept | Một câu | Lesson |
|---|---|:---:|
| CSMA/CA | Né tránh va chạm, vì không thể vừa phát vừa nghe | 32 |
| SSID / BSSID / BSS / ESS | Tên / MAC radio / 1 AP+client / nhiều AP cùng SSID | 32 |
| CAPWAP | Control UDP **5246** · Data UDP **5247** | 32 |
| Local mode vs FlexConnect | Về WLC vs xuống thẳng switch tại chỗ | 32 |
| DHCP Option 43 | Cách phổ biến nhất để AP tìm WLC — và hay sai nhất | 32 |
| Thiết kế theo mật độ | ~25 client/AP, **không** theo diện tích | 32 |
| 3 kênh 2.4 GHz | **1, 6, 11** — duy nhất không chồng lấn | 33 |
| CCI vs ACI | Cùng kênh (nhường nhau) vs chồng một phần (phát đè) | 33 |
| RSSI / SNR | Cường độ (dBm) / tín hiệu nổi hơn nhiễu (dB) | 33 |
| Channel width | Rộng hơn = nhanh hơn nhưng ít kênh hơn | 33 |
| Slow client problem | Một client yếu chiếm airtime gấp hàng chục lần | 33 |
| Roaming | **Client quyết định**; 802.11r/k/v hỗ trợ | 33 |
| 4-way handshake | Không truyền passphrase, nhưng cho brute-force offline | 34 |
| WPA3-SAE | Chống brute-force offline + **forward secrecy** | 34 |
| 802.1X 3 vai trò | Supplicant · Authenticator *(chỉ chuyển tiếp)* · RADIUS | 34 |
| Dynamic VLAN | Một SSID, nhiều VLAN tuỳ danh tính | 34 |
| Evil twin | AP giả + RADIUS giả → đánh cắp credential | 34 |

## 3. Commands

| Lệnh | Dùng khi | Lesson |
|---|---|:---:|
| `show power inline` | PoE budget còn bao nhiêu | 32 |
| `show cdp neighbors detail` | AP đã lên chưa, model gì, IP nào | 32 |
| `option 43 hex f104.XXXX.XXXX` | Chỉ WLC cho AP | 32 |
| `netsh wlan show networks mode=bssid` | ⭐ Khảo sát kênh, BSSID xung quanh | 33 |
| `netsh wlan show interfaces` | RSSI, kênh, tốc độ hiện tại | 33 |
| `show ap auto-rf 802.11a <ap>` | ⭐ Noise, **Channel Utilization**, số client | 33 |
| `show client detail <mac>` | RSSI, SNR, data rate của một client | 33 |
| `radius server X` + `address ipv4 ...` | Khai báo RADIUS | 34 |
| `authentication port-control auto` | Bật 802.1X trên port | 34 |
| `show authentication sessions` | ⭐ Ai đang đăng nhập, VLAN nào | 34 |
| `show aaa servers` | RADIUS UP hay DOWN | 34 |
| `test aaa group ... new-code` | ⭐ Test RADIUS không cần client thật | 34 |

## 4. Common Mistakes

| Sai lầm | Hậu quả |
|---|---|
| Thiết kế theo diện tích | Phòng họp đông người Wi-Fi tệ |
| Tạo 8 SSID | Mất 20–25% throughput vì beacon |
| Local mode cho chi nhánh qua WAN | Traffic chạy vòng, mất WAN = mất Wi-Fi |
| Tính sai hex Option 43 | AP không join, lỗi khó hiểu |
| Không kiểm tra PoE budget | Cắm thêm AP là không lên nguồn |
| Dùng kênh 3, 9 ở 2.4 GHz | **ACI** — tệ hơn dùng chung kênh |
| Dùng 40 MHz ở 2.4 GHz | Chiếm hết phổ, đè lên chính AP của mình |
| Tăng công suất để phủ xa hơn | Giao tiếp một chiều + tăng CCI |
| Chỉ nhìn RSSI, bỏ qua SNR | Tín hiệu mạnh trong môi trường nhiễu vẫn vô dụng |
| Nghĩ AP ép được client roam | Client quyết định |
| Dùng PSK cho mạng nhân viên | Không truy vết, nghỉ việc phải đổi cả công ty |
| Không kiểm chứng chỉ server ở client | **Evil twin** đánh cắp credential |
| Guest không có ACL cô lập | Khách vào được mạng nội bộ |
| Để WPA3 transition mode vĩnh viễn | Downgrade attack |

## 5. Interview Questions

1. **Q:** Vì sao 2.4 GHz chỉ có 3 kênh không chồng lấn?
   **A:** Có 13–14 kênh nhưng mỗi kênh cách nhau **5 MHz**, trong khi mỗi kênh cần
   **20 MHz** độ rộng. Chỉ các kênh cách nhau ≥ 4 bậc mới không đè nhau → **1, 6, 11**.

2. **Q:** Dùng chung kênh với hàng xóm hay dùng kênh lệch một chút — cái nào tốt hơn?
   **A:** **Dùng chung kênh tốt hơn.** Cùng kênh → **CCI**, hai mạng nghe thấy nhau và
   nhường nhau qua CSMA/CA (chậm nhưng chạy được). Kênh chồng một phần → **ACI**,
   hai mạng không giải mã được nhau, chỉ thấy nhiễu nền và **phát đè** → hỏng gói.

3. **Q:** Client A có RSSI −45 dBm, noise −50. Client B có RSSI −65, noise −95. Ai tốt hơn?
   **A:** **Client B.** SNR của A = 5 dB *(không dùng được)*, của B = 30 dB *(tốt)*.
   **SNR quan trọng hơn RSSI** — tín hiệu mạnh mà nhiễu cũng mạnh thì vẫn vô dụng.

4. **Q:** Vì sao tăng công suất AP thường không giải quyết được vùng phủ?
   **A:** Wi-Fi là giao tiếp **hai chiều**. Tăng công suất AP chỉ làm client **nghe** AP
   rõ hơn, nhưng AP vẫn không nghe client rõ hơn (công suất điện thoại không đổi).
   Thêm nữa, vùng phủ rộng ra → đè lên AP khác → tăng CCI. Giải pháp đúng là
   **nhiều AP công suất thấp**.

5. **Q:** Nhân viên nghỉ việc. Với WPA2-PSK và với 802.1X, bạn làm gì?
   **A:** PSK: **đổi passphrase** → 200 thiết bị phải cấu hình lại → thực tế hầu như
   không ai làm. 802.1X: **vô hiệu hoá một tài khoản AD**, 30 giây, không ai khác
   bị ảnh hưởng.

6. **Q:** Enterprise an toàn hơn PSK về mặt mã hoá như thế nào?
   **A:** Với PSK, **mọi client dùng chung một PMK** dẫn xuất từ passphrase → đồng nghiệp
   biết mật khẩu có thể giải mã traffic của nhau. Với Enterprise, **RADIUS sinh PMK riêng
   cho từng client từng phiên** → không ai giải mã được của ai.

## 6. Troubleshooting Cases

| # | Tình huống | Triệu chứng | Cách lần ra | Nguyên nhân |
|:---:|---|---|---|---|
| 1 | AP không lên nguồn | Đèn không sáng | `show power inline` | Hết PoE budget |
| 2 | AP có nguồn, không join WLC | Không thấy trên WLC | `show cdp neighbors`, ping WLC | Option 43 sai |
| 3 | Chi nhánh Wi-Fi chậm bất thường | Mọi thứ chậm | Xem AP mode trên WLC | Local mode qua WAN |
| 4 | Wi-Fi chậm khi đông người | Giờ cao điểm tệ | `show ap auto-rf` → Channel Utilization | Thiếu AP / 2.4 GHz nghẽn |
| 5 | Tín hiệu đầy vạch nhưng chậm | Vạch sóng tốt | `show client detail` → SNR | SNR thấp, nhiễu nền cao |
| 6 | Rớt cuộc gọi khi đi lại | VoIP không ổn định | Đo thời gian roam | Chưa bật 802.11r |
| 7 | Mọi client Enterprise fail | Không ai vào được | `show aaa servers` | RADIUS DOWN / sai shared secret |
| 8 | Xác thực OK nhưng không có IP | Có `Authz Success` | `show authentication sessions` → `Vlan Policy` | VLAN RADIUS trả về không tồn tại |
| 9 | Guest vào được mạng nội bộ | — | `show access-lists` | Thiếu ACL cô lập |

## 7. Mini Exam — 20 câu

> Làm **không mở tài liệu**. **< 80% thì quay lại ôn**, chưa sang Phase 6.

### Phần A — Lý thuyết (10 câu)

1. Phân biệt SSID, BSSID, BSS, ESS. Một AP phát 2 SSID trên 2 băng tần có mấy BSSID?
2. CAPWAP có mấy tunnel, port nào, chở gì?
3. Local mode và FlexConnect khác nhau thế nào? Chi nhánh qua WAN nên dùng cái nào, vì sao?
4. Vì sao 2.4 GHz chỉ có 3 kênh không chồng lấn? Kể tên 3 kênh đó.
5. CCI và ACI khác nhau thế nào? Cái nào tệ hơn, vì sao?
6. RSSI và SNR là gì? Ngưỡng nào cho dữ liệu, ngưỡng nào cho thoại?
7. Vì sao tăng công suất AP thường làm mọi thứ tệ hơn?
8. Ai quyết định roaming — AP hay client? Kể 3 chuẩn fast roaming và mỗi cái làm gì.
9. Phân biệt WPA2-Personal và WPA2-Enterprise ở **4 khía cạnh**.
10. Kể 3 vai trò của 802.1X và mỗi vai trò làm gì.

### Phần B — Tính toán & cấu hình (6 câu)

11. Công ty 150 người. Cần bao nhiêu AP? Dựa trên tiêu chí nào?
12. Lập kế hoạch kênh 2.4 GHz cho 6 AP trên một tầng.
13. Tính Option 43 hex cho WLC `10.0.99.20`.
14. Viết cấu hình port switch cho AP ở **FlexConnect** (VLAN mgmt 99, SSID VLAN 10 và 90).
15. Viết cấu hình RADIUS server `10.0.50.60` và bật 802.1X trên `Gi1/0/5`
    cho IP phone + PC.
16. Viết ACL cô lập VLAN guest `10.0.90.0/24` khỏi mọi dải `10.0.0.0/16`.

### Phần C — Tình huống (4 câu)

17. Phòng họp 40 người, 1 AP, Channel Utilization 85%. Nêu 3 cách xử lý theo thứ tự ưu tiên.
18. Client RSSI −45 dBm, noise −50 dBm. Kết nối có tốt không? Tính SNR và giải thích.
19. Kẻ tấn công bắt được 4-way handshake WPA2-PSK. Họ làm được gì?
    Với WPA3-SAE thì khác thế nào?
20. Client Enterprise xác thực thành công nhưng không nhận được IP.
    Nêu 3 nguyên nhân theo thứ tự kiểm tra.

---

### Bảng chấm

| Phần | Nội dung | Điểm |
|---|---|:---:|
| A | Lý thuyết | /10 |
| B | Tính toán & cấu hình | /6 |
| C | Tình huống | /4 |
| | **Tổng** | **/20** |

| Kết quả | Quyết định |
|---|---|
| **≥ 16/20** | ✅ Sang [Phase 6 — Security](../06-security/README.md) |
| 12–15 | ⚠️ Ôn lại lesson của các câu sai |
| < 12 | ❌ Học lại Phase 5 |

> ⚠️ Sai **câu 5, 7, hoặc 18** thì dù tổng điểm cao vẫn phải ôn lại —
> ba câu đó đo đúng phần RF mà phần lớn người học bỏ qua.

### Yêu cầu bổ sung để qua phase

- [ ] Giải thích được vì sao 2.4 GHz chỉ có 3 kênh và ảnh hưởng tới thiết kế văn phòng
- [ ] Đã **khảo sát Wi-Fi thật** bằng `netsh wlan show networks mode=bssid`,
      tìm được AP dùng kênh ngoài 1/6/11
- [ ] Thiết kế được sơ đồ kênh cho một tầng 6 AP
- [ ] Đã làm LAB 50, có mục BREAK điền đầy đủ

---

## 🧱 Mục chuyển sang *Điểm yếu cần ôn* trong PROGRESS.md

-
-
