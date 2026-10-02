# Phase 5 — WIRELESS (mức CCNA)

> Phase nhẹ nhất về cấu hình, nhưng là phase bạn sẽ dùng nhiều nhất trong đời thực — vì user luôn kêu "wifi chậm".

| | |
|---|---|
| **Chủ đề** | WLAN · AP · WLC · SSID/BSSID · băng tần & kênh · WPA2/WPA3 |
| **Số lesson** | 3 |
| **Thời lượng** | ~1 tuần |
| **Công cụ lab** | Packet Tracer (có WLC mô phỏng ở mức cơ bản) |
| **Prerequisite** | Phase 1 (VLAN, trunk) |

---

## 🎯 Mục tiêu phase

- [ ] Giải thích được vì sao 2.4 GHz chỉ có **3 kênh không chồng lấn** và điều đó ảnh hưởng gì tới thiết kế văn phòng
- [ ] Phân biệt autonomous AP vs lightweight AP + WLC — và khi nào doanh nghiệp cần cái nào
- [ ] Nói đúng khác biệt WPA2 và WPA3, Personal và Enterprise
- [ ] Biết AP cần gì từ switch: trunk port, VLAN nào, PoE

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 32 | WLAN · AP · WLC · CAPWAP · local vs FlexConnect | [`lesson-32-wlan-ap-wlc.md`](./lesson-32-wlan-ap-wlc.md) | | ⬜ |
| 33 | **RF · băng tần · kênh · roaming** ⭐ | [`lesson-33-rf-channel-roaming.md`](./lesson-33-rf-channel-roaming.md) | | ⬜ |
| 34 | Bảo mật Wi-Fi: WPA2/WPA3 · PSK vs **802.1X** | [`lesson-34-bao-mat-wifi.md`](./lesson-34-bao-mat-wifi.md) | LAB 50 | ⬜ |

📝 **Kết thúc phase:** [`review-phase05.md`](./review-phase05.md) — tổng kết + Mini Exam 20 câu

> 🔧 Lesson 33 có **4 bài khảo sát trên máy thật** — làm được ngay không cần lab ảo.

---

## 🧪 Lab của phase

| Lab | Lesson | Nội dung | File |
|---|:---:|---|---|
| — | 33 | 4 bài khảo sát RF trên máy thật *(trong lesson)* | — |
| LAB 50 | 34 | WPA2-PSK + WPA2-Enterprise + ACL cô lập guest | [`../labs/lab50-bao-mat-wifi.md`](../labs/lab50-bao-mat-wifi.md) |

---

## 📶 Bảng kênh cần nhớ

| Băng tần | Kênh không chồng lấn | Đặc điểm |
|---|---|---|
| **2.4 GHz** | **1, 6, 11** (chỉ 3 kênh) | Xa hơn, xuyên tường tốt hơn, **rất đông** |
| **5 GHz** | ~20+ kênh (tuỳ DFS & quốc gia) | Nhanh hơn, tầm ngắn hơn, ít nhiễu |
| **6 GHz** (Wi-Fi 6E) | Nhiều nhất | Chỉ thiết bị mới hỗ trợ |

> 🏭 **Production:** gần như mọi vấn đề "wifi chậm" trong văn phòng đều quy về 3 thứ:
> **co-channel interference**, **đặt AP sai chỗ**, hoặc **quá nhiều client trên 1 AP** —
> không phải "đường truyền yếu".

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| Đặt channel width 40/80 MHz ở 2.4 GHz | Chiếm hết phổ, gây nhiễu cho chính mình |
| Tăng công suất AP để "phủ xa hơn" | Client vẫn yếu chiều về → kết nối một chiều, tệ hơn |
| Nghĩ nhiều AP = tốt hơn | Co-channel interference làm throughput tụt |
| Nhầm SSID với BSSID | SSID là **tên**, BSSID là **MAC của radio AP** |

---

## 🚪 Cổng ra phase

- [ ] Giải thích được toàn bộ đường đi của một client Wi-Fi tới server trong DC
- [ ] Thiết kế được sơ đồ kênh cho một tầng văn phòng 6 AP
- [ ] Mini Exam Phase 5 ≥ 80%

> 📖 Sâu hơn (CAPWAP, FlexConnect, roaming, RF design): [`CCNP-Encor` Module 07A/07B](https://github.com/hiepnguyen775/CCNP-Encor)
