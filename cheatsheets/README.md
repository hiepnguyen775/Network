# 📋 Cheatsheets

> **Dùng lúc đang lab, không phải lúc học.**
> Mục đích của cheatsheet là để bạn khỏi dừng mạch tư duy vì một chi tiết tra được.
> Nếu bạn phải mở cheatsheet để trả lời câu hỏi lý thuyết — nghĩa là chưa học xong phần đó.

---

| File | Nội dung | Dùng ở Phase |
|---|---|---|
| [`subnetting.md`](./subnetting.md) | Magic number, cách tính nhanh, VLSM, wildcard mask, bài tự luyện | 0, 2, 6 |
| [`ports-va-protocols.md`](./ports-va-protocols.md) | Port phải thuộc, protocol number, OSI, TCP vs UDP | 0, 3, 6 |
| [`show-commands.md`](./show-commands.md) | Lệnh `show` theo tầng + cách đọc output + bảng AD | 1 → 7 |
| [`troubleshooting-playbook.md`](./troubleshooting-playbook.md) | Cây quyết định, bảng triệu chứng → nghi ngờ, mẫu ghi sự cố | 1 → 7 |

---

## Ba bảng đáng thuộc nhất trong cả bộ

| Bảng | Ở đâu | Vì sao |
|---|---|---|
| **Magic number** `/24` → `/30` | [`subnetting.md`](./subnetting.md#1-bảng-magic-number--học-thuộc-bảng-này-trước) | Dùng mỗi ngày, trong thi và trong việc |
| **Administrative Distance** | [`show-commands.md`](./show-commands.md#administrative-distance--bảng-phải-thuộc) | Quyết định route nào thắng |
| **Port 22 / 53 / 67-68 / 80 / 443 / 161** | [`ports-va-protocols.md`](./ports-va-protocols.md#1-port-phải-thuộc-lòng) | Viết ACL mà tra port = chậm |

---

## Thêm cheatsheet mới

Đặt tên không dấu, chữ thường: `cheatsheets/ten-chu-de.md`, rồi thêm một dòng vào bảng trên.
