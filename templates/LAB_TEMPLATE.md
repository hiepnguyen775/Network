# LAB NN — [Tên LAB]

<!--
Copy file này vào labs/ , đổi tên thành labNN-ten-khong-dau.md
Mục 8 (BREAK) là BẮT BUỘC. Không làm BREAK = lab chưa xong.
Xoá comment này khi bắt đầu viết.
-->

| | |
|---|---|
| **Phase** | NN |
| **Lesson liên quan** | [`lesson-NN-...`](../NN-phase/lesson-NN-....md) |
| **Công cụ** | Packet Tracer / GNS3 / EVE-NG |
| **Thời lượng** | ~N giờ |
| **Độ khó** | ⭐ / ⭐⭐ / ⭐⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm · 🟨 Đang làm · 🟩 Xong (đã BREAK) |
| **Ngày làm** | — |

---

## 1. Mục tiêu

Tôi sẽ **chứng minh được** điều gì sau lab này?

- [ ]
- [ ]

## 2. Prerequisite

Kiến thức và lab cần có trước.

## 3. Topology

```text
        PC1                 PC2
         |                   |
        SW1 ============== SW2        (trunk)
         |                   |
         +------- R1 --------+
                  |
                Server
```

| Thiết bị | Model gợi ý | Vai trò |
|---|---|---|
| | | |

## 4. IP Addressing Table

| Device | Interface | IP | Mask | Gateway | VLAN |
|---|---|---|---|---|---|
| | | | | | |

> Nếu lab có VLSM, ghi rõ cách chia ở đây — **chia trước, cấu hình sau**.

## 5. Yêu cầu LAB

- [ ]
- [ ]
- [ ]

---

## 6. Step-by-step

> Ghi lại **những gì bạn thật sự đã làm**, kể cả bước làm sai rồi quay lại.

1.
2.
3.

## 7. Verification

```cisco
show ip interface brief
show vlan brief
show interfaces trunk
show mac address-table
show ip route
show ip ospf neighbor
```

```text
# output điển hình để tham chiếu — dán output THẬT từ lab của bạn vào đây
```

**Bằng chứng lab chạy đúng:**

- [ ] `ping` từ ___ tới ___ thành công
- [ ] `show ...` hiển thị ___

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

Cố tình tạo lỗi rồi tự tìm lại. Làm **ít nhất 3** lỗi:

- [ ] Wrong subnet mask
- [ ] Wrong VLAN / trunk mismatch / native VLAN mismatch
- [ ] OSPF network statement sai wildcard
- [ ] Wrong default gateway trên PC
- [ ] Interface `shutdown`
- [ ] ACL đặt sai hướng

| # | Lỗi đã tạo | Triệu chứng quan sát được | Lệnh đã dùng để tìm | Nguyên nhân | Cách sửa |
|:---:|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

> Mỗi lỗi tìm ra → chép sang [`SO-TAY-LOI.md`](../SO-TAY-LOI.md).

## 9. Challenge

Bài biến thể — tự làm, chưa xem đáp án.

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

```cisco
! cấu hình đầy đủ
```

</details>

---

## 📝 Ghi chú & bài học rút ra

- Mất nhiều thời gian nhất ở bước: ___
- Lần sau tôi sẽ làm khác ở chỗ: ___
- Thứ tôi tưởng mình hiểu nhưng thật ra chưa: ___
