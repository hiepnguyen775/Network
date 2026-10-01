# LESSON NN — [TÊN TOPIC]

<!--
HƯỚNG DẪN DÙNG KHUÔN NÀY
- Copy file này vào thư mục phase tương ứng, đổi tên thành lesson-NN-ten-khong-dau.md
- AI dạy theo BEAT (xem MENTOR_PROMPT.md §6), KHÔNG đổ hết 15 phần một lần.
- Beat 1: phần 1–4 · Beat 2: 5–7 · Beat 3: 8–9 · Beat 4: 10–11 · Beat 5: 12–15
- Gõ "full" nếu muốn đọc liền mạch.
- Xoá hết comment HTML này khi bắt đầu viết thật.
-->

| | |
|---|---|
| **Phase** | NN — Tên phase |
| **Thời lượng** | ~N giờ |
| **Prerequisite** | Lesson NN |
| **Trạng thái** | ⬜ Chưa học · 🟨 Đang học · 🟩 Xong · 🔁 Cần ôn |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

Học xong tôi làm được gì? *(viết dạng động từ hành động: cấu hình được…, giải thích được…, tìm được lỗi…)*

- [ ]
- [ ]
- [ ]

## 2. Prerequisite

Cần biết gì trước — link tới lesson cũ nếu có.

## 3. Concept

Khái niệm, dạy như cho người mới hoàn toàn.

## 4. Why? — tại sao công nghệ này tồn tại

Vấn đề thực tế nó giải quyết. Câu hỏi phải trả lời được: **nếu không có nó thì sao?**

---

## 5. How does it work?

Flow từng bước + thành phần bên trong (header / field / table / state / timer / algorithm).

## 6. Packet Flow

Packet đi từ đâu → đâu. Qua **từng hop** ghi rõ:

| Hop | Src MAC | Dst MAC | Src IP | Dst IP | TTL | Ghi chú |
|---|---|---|---|---|---|---|
| | | | | | | |

> Nhắc lại: **MAC đổi mỗi hop, IP giữ nguyên** (trừ khi NAT).

## 7. Real-world Example

Liên hệ hạ tầng doanh nghiệp thật: dual-WAN, VPN site-to-site, HA, phòng server…

---

## 8. Cisco CLI

```cisco
! <lệnh>
```

Giải thích **từng dòng**. Ghi rõ nếu IOS / IOS-XE / NX-OS khác nhau:

| Lệnh | Làm gì | Khác biệt platform |
|---|---|---|
| | | |

## 9. Verification

```cisco
show ...
```

```text
# output điển hình — tự verify trên lab của bạn
```

**Đọc gì trong output này:**

| Dòng / field | Ý nghĩa | Bất thường trông như thế nào |
|---|---|---|
| | | |

---

## 10. Troubleshooting

Theo tầng: `Physical → Interface → VLAN → IP → ARP → MAC → Routing → ACL → NAT → App`

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Nếu đúng thì sửa thế nào |
|---|---|---|---|
| | | | |

## 11. LAB

Tạo từ [`LAB_TEMPLATE.md`](./LAB_TEMPLATE.md) → lưu vào `labs/labNN-ten.md`.

🧪 **LAB liên quan:** `labs/labNN-....md`

## 12. Challenge

Bài tương tự nhưng khác đề. **KHÔNG xem đáp án trước khi làm.**

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 5 câu lý thuyết ngắn | ⬜ |
| **L2** Explain | Tự giải thích lại bằng lời của mình | ⬜ |
| **L3** Configure | Một bài cấu hình | ⬜ |
| **L4** Troubleshoot | Topology có lỗi, tự tìm | ⬜ |
| **L5** Design | Requirement thực tế, tự thiết kế | ⬜ |

## 14. Summary

**Key concepts**

-

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| | |

**Common mistakes**

-

## 15. Homework + cập nhật PROGRESS

**Homework:**

-

**Dán dòng này vào `PROGRESS.md`:**

```markdown
- [YYYY-MM-DD] Lesson NN — <topic>: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | |
| 🔧 **Engineer** | |
| 🏭 **Production** | |

### 🔗 Liên kết

- Lesson trước: [`lesson-NN-...`](./lesson-NN-....md)
- Lesson sau: [`lesson-NN-...`](./lesson-NN-....md)
- Cheatsheet: [`cheatsheets/...`](../cheatsheets/)
- Flashcard: [`flashcards/NN-...`](../flashcards/)
