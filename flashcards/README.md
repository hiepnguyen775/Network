# 🃏 Flashcards

> 10 phút mỗi ngày ở đây có giá trị hơn 2 tiếng đọc lại lesson cuối tuần.

---

## Cách dùng đúng

| Làm | Đừng làm |
|---|---|
| Che đáp án, trả lời **thành tiếng** | Đọc lướt cả Q lẫn A rồi gật gù |
| Ôn theo nhịp **1 → 3 → 7 → 21 ngày** | Ôn dồn một lần trước khi thi |
| Ghi lại câu **sai** vào `PROGRESS.md` | Bỏ qua câu sai vì "lúc nữa nhớ ra" |
| Trả lời xong mới xem đáp án | Xem đáp án rồi tự nhủ "biết rồi" |

> ⚠️ Cảm giác *"à đúng rồi, mình biết mà"* khi nhìn đáp án **không phải là nhớ**.
> Chỉ tính là nhớ khi bạn **nói ra được trước** khi nhìn.

---

## 📚 Bộ thẻ

| File | Phase | Số thẻ | Chủ đề |
|---|:---:|:---:|---|
| [`00-foundation.md`](./00-foundation.md) | 0 | ~30 | OSI, MAC/IP, ARP, TCP/UDP, port, subnetting, DHCP/NAT |
| [`01-switching.md`](./01-switching.md) | 1 | ~25 | MAC table, VLAN, trunk, inter-VLAN, STP/RSTP, EtherChannel, port security |
| [`02-routing.md`](./02-routing.md) | 2 | ~28 | Routing table, AD/metric, static/floating, OSPF states, DR/BDR, area, LSA |
| *(03 → 07)* | 3–7 | — | Tạo khi học tới phase đó — gõ `flashcard` để AI sinh |

---

## Tạo bộ thẻ mới

Khi xong một phase, gõ **`flashcard`** cho AI mentor. Yêu cầu:

- Câu hỏi **ngắn**, một ý một thẻ
- Đáp án **chính xác**, không mơ hồ
- Ưu tiên câu hỏi dạng *"vì sao"* và *"khi nào dùng"*, không chỉ *"là gì"*
- Có bảng **lệnh phải thuộc** ở cuối
- Lưu vào `flashcards/NN-ten-phase.md`

---

## 🎯 Ba thẻ quan trọng nhất toàn bộ CCNA

Nếu chỉ nhớ được 3 thứ, nhớ 3 thứ này:

1. **MAC đổi mỗi hop, IP giữ nguyên** (trừ NAT) — gốc của mọi hiểu biết về packet flow.
2. **Longest prefix match → AD → Metric** — thứ tự router chọn đường.
3. **VLAN chia broadcast domain** — vì sao cần L3 để đi giữa các VLAN.
