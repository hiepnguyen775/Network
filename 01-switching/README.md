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
| 11 | Switch hoạt động thế nào · MAC table · collision vs broadcast domain | — | | ⬜ |
| 12 | Cisco IOS CLI: config modes, interface, speed/duplex, lưu config | — | ✅ | ⬜ |
| 13 | VLAN · access port · trunk 802.1Q · native VLAN ⭐ | [`lesson-13-vlan-va-trunk.md`](./lesson-13-vlan-va-trunk.md) | ✅ | ⬜ |
| 14 | Inter-VLAN routing: Router-on-a-Stick và L3 Switch (SVI) ⭐ | — | ✅ | ⬜ |
| 15 | STP: vì sao cần, root election, port roles/states ⭐ | — | ✅ | ⬜ |
| 16 | RSTP · PortFast · BPDU Guard | — | ✅ | ⬜ |
| 17 | EtherChannel (LACP/PAgP) · Port Security | — | ✅ | ⬜ |

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
