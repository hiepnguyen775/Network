# 📐 Templates

Ba khuôn chuẩn của repo. **Đừng viết lesson/lab từ file trắng** — luôn copy từ đây để mọi file
trong repo có cùng cấu trúc, dễ đọc lại sau 3 tháng.

| Template | Dùng khi | Copy vào | Đặt tên |
|---|---|---|---|
| [`LESSON_TEMPLATE.md`](./LESSON_TEMPLATE.md) | Bắt đầu một lesson mới | `NN-phase/` | `lesson-NN-ten-khong-dau.md` |
| [`LAB_TEMPLATE.md`](./LAB_TEMPLATE.md) | Bắt đầu một LAB | `labs/` | `labNN-ten-khong-dau.md` |
| [`MODULE_REVIEW_TEMPLATE.md`](./MODULE_REVIEW_TEMPLATE.md) | Kết thúc một phase | `NN-phase/` | `review-phaseNN.md` |

---

## Lệnh copy nhanh

**PowerShell**

```powershell
Copy-Item templates\LESSON_TEMPLATE.md 00-foundation\lesson-01-osi-va-tcp-ip.md
Copy-Item templates\LAB_TEMPLATE.md    labs\lab11-vlan-va-trunk.md
```

**Bash / Git Bash**

```bash
cp templates/LESSON_TEMPLATE.md 00-foundation/lesson-01-osi-va-tcp-ip.md
cp templates/LAB_TEMPLATE.md    labs/lab11-vlan-va-trunk.md
```

---

## Nguyên tắc khi điền

1. **Mục 4 "Why?" của lesson và mục 8 "BREAK" của lab là bắt buộc.** Hai mục này là thứ phân biệt
   repo học thật với repo chép bài.
2. **Viết bằng lời của bạn.** Copy nguyên văn giải thích của AI vào file = không học được gì.
3. **Output `show` phải là output thật từ lab của bạn.** Output AI đưa chỉ để đối chiếu và phải
   giữ nguyên nhãn `# output điển hình — tự verify trên lab của bạn`.
4. **Xoá hết comment HTML hướng dẫn** (`<!-- ... -->`) khi bắt đầu viết thật.
