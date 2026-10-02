# Phase 1 — SWITCHING

> Thế giới Layer 2. Đây là chỗ người làm infra hay chủ quan nhất — và cũng là chỗ gãy nhiều nhất trong thực tế.

| | |
|---|---|
| **Chủ đề** | VLAN · trunk 802.1Q · inter-VLAN · STP/RSTP · EtherChannel · port security |
| **Số lesson** | 7 |
| **Thời lượng** | ~3 tuần |
| **Công cụ lab** | Packet Tracer |
| **Prerequisite** | Phase 0 trọn vẹn (đặc biệt: MAC, broadcast domain, subnetting) |

---

## 🎯 Mục tiêu phase

- [ ] Dựng 2 switch + 2 VLAN + trunk + inter-VLAN routing **từ con số 0, không nhìn tài liệu**
- [ ] Giải thích được VLAN sinh ra để giải quyết vấn đề gì (gợi ý: broadcast domain + bảo mật + chi phí)
- [ ] Đọc được `show spanning-tree` và nói ra ai là root, port nào bị block, **vì sao**
- [ ] Tự tìm được lỗi native VLAN mismatch chỉ từ triệu chứng

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 11 | Kiến trúc switch · L2 vs L3 · mô hình phân lớp | [`lesson-11-kien-truc-switch.md`](./lesson-11-kien-truc-switch.md) | | ⬜ |
| 12 | Cisco IOS CLI: config mode, SSH, lưu config | [`lesson-12-cisco-ios-cli.md`](./lesson-12-cisco-ios-cli.md) | LAB 10 | ⬜ |
| 13 | VLAN · access · trunk 802.1Q · native VLAN ⭐ | [`lesson-13-vlan-va-trunk.md`](./lesson-13-vlan-va-trunk.md) | LAB 11 | ⬜ |
| 14 | Inter-VLAN routing: Router-on-a-Stick & SVI ⭐ | [`lesson-14-inter-vlan-routing.md`](./lesson-14-inter-vlan-routing.md) | LAB 12 | ⬜ |
| 15 | STP: vì sao cần, bầu root, port role ⭐ | [`lesson-15-stp.md`](./lesson-15-stp.md) | LAB 13 | ⬜ |
| 16 | RSTP · PortFast · BPDU Guard · Root Guard | [`lesson-16-rstp-portfast-bpduguard.md`](./lesson-16-rstp-portfast-bpduguard.md) | LAB 14 | ⬜ |
| 17 | EtherChannel (LACP) · Port Security | [`lesson-17-etherchannel-port-security.md`](./lesson-17-etherchannel-port-security.md) | LAB 15 | ⬜ |

📝 **Kết thúc phase:** [`review-phase01.md`](./review-phase01.md) — tổng kết + Mini Exam 20 câu

> ✅ **Phase 1 đã viết đầy đủ.** Đọc theo thứ tự 11 → 17, làm lab khi lesson bảo làm,
> rồi làm Mini Exam.

---

## 🧪 Lab của phase

| Lab | Lesson | Nội dung | File |
|---|:---:|---|---|
| LAB 10 | 12 | Cisco IOS CLI căn bản, SSH, backup config | *(tự tạo từ template)* |
| LAB 11 | 13 | VLAN & Trunk giữa 2 switch | [`lab11-vlan-va-trunk.md`](../labs/lab11-vlan-va-trunk.md) |
| LAB 12 | 14 | Inter-VLAN routing: RoAS **và** SVI | [`lab12-inter-vlan-routing.md`](../labs/lab12-inter-vlan-routing.md) |
| LAB 13 | 15 | STP: bầu root, port role, broadcast storm | [`lab13-stp.md`](../labs/lab13-stp.md) |
| LAB 14 | 16 | RSTP, PortFast, BPDU Guard — đo thời gian hội tụ | *(tự tạo từ template)* |
| LAB 15 | 17 | EtherChannel LACP + Port Security | *(tự tạo từ template)* |

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| "VLAN chỉ để chia mạng cho gọn" | VLAN chia **broadcast domain**. Hiểu sai chỗ này thì không hiểu nổi vì sao cần router để đi giữa VLAN. |
| Quên `switchport mode access` | Port ở `dynamic auto` → hành vi khó đoán, lab lúc chạy lúc không |
| Native VLAN hai đầu khác nhau | Traffic VLAN native "rò" sang VLAN khác — triệu chứng rất khó hiểu nếu không biết trước |
| Nghĩ trunk tự cho qua mọi VLAN | Phải kiểm tra `switchport trunk allowed vlan` |
| Bỏ qua STP vì "lab không có loop" | Production **luôn** có redundant link. Không hiểu STP = không dám đấu dây dự phòng. |
| Nghĩ Router-on-a-Stick và SVI là một | Khác nhau về hiệu năng và chỗ dùng — phải nói được khi nào chọn cái nào |

---

## 🚪 Cổng ra phase

- [ ] Dựng lab 2 switch + 3 VLAN + trunk + L3 switch inter-VLAN trong **dưới 20 phút**
- [ ] Làm BREAK đủ 5 lỗi L2 và tự tìm lại được hết
- [ ] Mini Exam Phase 1 ≥ 80%

---

## 🔗 Tài nguyên

- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md)
- 🧯 [`SO-TAY-LOI.md`](../SO-TAY-LOI.md) — mục "Layer 1–2"
- 🃏 [`flashcards/01-switching.md`](../flashcards/01-switching.md)
