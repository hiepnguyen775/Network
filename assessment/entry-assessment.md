# 📝 ENTRY ASSESSMENT — Network Knowledge

> **Mục đích:** không phải chấm điểm, mà để AI biết **chỗ nào bỏ qua được** và **chỗ nào phải dạy kỹ**.
> Bỏ 20–30 phút ở đây tiết kiệm vài tuần học sai chỗ.

---

## Luật chơi

| | |
|---|---|
| ⏱ | ~25 phút, làm một mạch |
| 📵 | **Không Google, không mở tài liệu, không máy tính** |
| 🤷 | Không biết thì ghi **"không biết"** — trung thực quan trọng hơn điểm |
| 📦 | Làm **từng cụm 5–7 câu**, AI chấm từng cụm rồi mới đưa cụm tiếp |
| ❌ | AI **không được** đưa đáp án trước khi bạn trả lời hết một cụm |

---

## CỤM 1 — Nền tảng & OSI *(5 câu)*

1. Mô hình OSI có mấy tầng? Kể tên từ **dưới lên**.
2. MAC address và IP address nằm ở tầng nào? Switch và router hoạt động ở tầng nào?
3. Khi gói tin đi qua một router, **cái gì thay đổi và cái gì giữ nguyên** trong header?
4. Collision domain và broadcast domain khác nhau thế nào? Switch ảnh hưởng tới từng cái ra sao?
5. Encapsulation là gì? Kể tên PDU ở tầng 2, 3, 4.

---

## CỤM 2 — IPv4 & Subnetting *(5 câu)*

6. `192.168.10.100/26` → Network, Broadcast, First host, Last host, số host usable?
7. `/28` có subnet mask là gì? Block size bao nhiêu? Bao nhiêu host dùng được?
8. Ba dải IP private theo RFC 1918 là gì? *(ghi đúng cả prefix)*
9. Một máy nhận IP `169.254.12.33`. Điều này cho bạn biết gì? Bạn kiểm tra gì đầu tiên?
10. Công ty cần chia cho 4 phòng: 50, 25, 12, 2 host từ dải `10.0.0.0/24`.
    Chia VLSM thế nào? *(ghi prefix và dải của từng phòng)*

---

## CỤM 3 — Switching & VLAN *(5 câu)*

11. VLAN sinh ra để **giải quyết vấn đề gì**? Nếu không có VLAN thì sao?
12. Access port và trunk port khác nhau thế nào? 802.1Q làm gì với frame?
13. Native VLAN là gì? Hai đầu trunk đặt native VLAN khác nhau thì chuyện gì xảy ra?
14. Hai PC ở hai VLAN khác nhau muốn nói chuyện cần gì? Kể **hai** cách triển khai và khác biệt.
15. STP sinh ra để giải quyết vấn đề gì? Vì sao loop ở L2 nguy hiểm hơn loop ở L3?

---

## CỤM 4 — Routing *(5 câu)*

16. Router quyết định chọn route nào theo **thứ tự** nào? *(3 tiêu chí)*
17. Administrative Distance là gì? AD của Connected / Static / OSPF / RIP?
18. Default route viết thế nào? Vì sao nó luôn thua các route cụ thể hơn?
19. Floating static route là gì? Dùng trong tình huống thực tế nào?
20. OSPF neighbor phải khớp **những gì** mới lên được? Kể càng nhiều càng tốt.

---

## CỤM 5 — Services & Transport *(5 câu)*

21. TCP khác UDP ở những điểm cốt lõi nào? Mỗi loại dùng cho dịch vụ gì?
22. TCP 3-way handshake gồm mấy bước, tên từng bước?
23. DHCP có 4 bước, tên là gì? DHCP Discover là unicast hay broadcast — và hệ quả?
24. PC ở VLAN 20 không nhận được IP từ DHCP server ở VLAN 10. Vì sao? Sửa thế nào?
25. NAT/PAT giải quyết vấn đề gì? PAT phân biệt các kết nối bằng gì?

---

## CỤM 6 — Đọc output & Troubleshooting *(5 câu)*

26. Wildcard mask của `/26` là gì? Nó dùng ở đâu, khác subnet mask chỗ nào?
27. Trong `show ip route`, dòng `O 10.2.2.0/24 [110/2] via 10.1.1.2` — giải thích **từng phần**.
28. Kể 5 lệnh `show` bạn gõ **đầu tiên** khi một mạng Cisco có vấn đề, và mỗi lệnh trả lời câu hỏi gì.
29. `show ip interface brief` hiện `up / down` — nghĩa là gì? Bạn nghi ngờ gì?
30. PC1 ping được gateway nhưng không ping được server ở subnet khác.
    Mô tả **quy trình** bạn lần ra nguyên nhân — từng bước, từng lệnh, từng giả thuyết.

---

## 📊 Bảng chấm *(AI điền sau khi chấm)*

| Cụm | Chủ đề | Điểm | Phân loại gap |
|:---:|---|:---:|---|
| 1 | Nền tảng & OSI | /5 | |
| 2 | IPv4 & Subnetting | /5 | |
| 3 | Switching & VLAN | /5 | |
| 4 | Routing | /5 | |
| 5 | Services & Transport | /5 | |
| 6 | Đọc output & Troubleshooting | /5 | |
| | **Tổng** | **/30** | |

**Phân loại gap:**

| Loại | Nghĩa | Cách xử lý |
|---|---|---|
| `chưa biết` | Chưa gặp bao giờ | Dạy bình thường từ đầu |
| `biết mơ hồ` | Trả lời gần đúng, thiếu chiều sâu | Dạy nhanh phần concept, tập trung vào lab |
| `hiểu sai` ⚠️ | Tin vào một điều sai | **Ưu tiên cao nhất** — phải tháo gỡ trước, nếu không sẽ sai dây chuyền |

---

## 🧭 Thang tham chiếu

| Điểm | Nghĩa | Lộ trình gợi ý |
|:---:|---|---|
| **0–10** | Nền còn mỏng | Học đầy đủ Phase 0 → 7, không bỏ mục nào |
| **11–18** | Có nền, nhiều lỗ hổng | Phase 0 học chọn lọc theo gap, Phase 1–2 học kỹ |
| **19–25** | Khá vững | Lướt Phase 0, dồn sức Phase 1–2 và 6–7 |
| **26–30** | Sẵn sàng | Ôn nhanh Phase 0–7 rồi làm Final Project, tính chuyện thi sớm |

> ⚠️ Điểm cao mà **sai câu 16, 20, hoặc 30** vẫn phải học kỹ Phase 2 —
> ba câu đó đo đúng thứ phân biệt người hiểu network và người thuộc lệnh.

---

## Sau khi chấm xong

1. AI phân loại gap và đề xuất **roadmap cá nhân hoá**.
2. Bạn dán kết quả + roadmap vào [`../PROGRESS.md`](../PROGRESS.md), mục *Kết quả Entry Assessment*.
3. Mọi mục `hiểu sai` và `chưa biết` → thêm vào bảng *Điểm yếu cần ôn*.
4. Commit, rồi bắt đầu Lesson 1.
