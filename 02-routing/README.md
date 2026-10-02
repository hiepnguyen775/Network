# Phase 2 — ROUTING

> Trái tim của CCNA. Phase này quyết định bạn có thật sự "hiểu network" hay chỉ biết cắm dây.

| | |
|---|---|
| **Chủ đề** | Routing table · static/default/floating · AD & metric · **OSPF** single → multi-area |
| **Số lesson** | 7 |
| **Thời lượng** | ~3 tuần |
| **Công cụ lab** | Packet Tracer (GNS3 nếu muốn sâu hơn) |
| **Prerequisite** | Phase 0 + Phase 1 |

---

## 🎯 Mục tiêu phase

- [ ] Đọc `show ip route` và giải thích **mọi ký tự** ở đầu dòng
- [ ] Nói được vì sao route A thắng route B — theo đúng thứ tự: longest prefix → AD → metric
- [ ] Dựng OSPF multi-area, và khi neighbor không lên thì biết lần theo thứ tự nào
- [ ] Phân biệt được *route không có* và *route có nhưng sai hướng*

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 18 | Router hoạt động thế nào · routing table · RIB/FIB | [`lesson-18-router-va-routing-table.md`](./lesson-18-router-va-routing-table.md) | LAB 20 | ⬜ |
| 19 | Static · default · **floating static** | [`lesson-19-static-default-route.md`](./lesson-19-static-default-route.md) | LAB 21 | ⬜ |
| 20 | AD · Metric · **Longest Prefix Match** ⭐ | [`lesson-20-ad-metric-longest-prefix.md`](./lesson-20-ad-metric-longest-prefix.md) | LAB 22 | ⬜ |
| 21 | Dynamic routing — bức tranh chung · RIP | [`lesson-21-dynamic-routing-rip.md`](./lesson-21-dynamic-routing-rip.md) | | ⬜ |
| 22 | OSPF single-area: state, DR/BDR ⭐ | [`lesson-22-ospf-single-area.md`](./lesson-22-ospf-single-area.md) | LAB 23 | ⬜ |
| 23 | OSPF Cost · LSDB · LSA Type 1/2/3 ⭐ | [`lesson-23-ospf-cost-lsdb-lsa.md`](./lesson-23-ospf-cost-lsdb-lsa.md) | LAB 23 | ⬜ |
| 24 | OSPF multi-area · ABR · summarization | [`lesson-24-ospf-multi-area.md`](./lesson-24-ospf-multi-area.md) | LAB 24 | ⬜ |

📝 **Kết thúc phase:** [`review-phase02.md`](./review-phase02.md) — tổng kết + Mini Exam 20 câu

> ✅ **Phase 2 đã viết đầy đủ.** Đây là phase quan trọng nhất của CCNA — đừng lướt.

---

## 🧪 Lab của phase

| Lab | Lesson | Nội dung | File |
|---|:---:|---|---|
| LAB 20 | 18 | Routing table cơ bản, `C`/`L`, interface down | *(tự tạo từ template)* |
| LAB 21 | 19 | Static · default · floating static failover | *(tự tạo từ template)* |
| LAB 22 | 20 | Thứ tự chọn route, longest prefix match, ECMP | *(tự tạo từ template)* |
| LAB 23 | 22, 23 | **OSPF single-area: neighbor, DR/BDR, đọc LSDB** | [`lab23-ospf-single-area.md`](../labs/lab23-ospf-single-area.md) |
| LAB 24 | 24 | OSPF multi-area & summarization | *(tự tạo từ template)* |

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| Nhầm **wildcard mask** với subnet mask trong `network` statement | Lệnh được nhận nhưng OSPF không chạy đúng interface |
| Ping được 1 chiều, kết luận "mạng hỏng" | Gần như luôn là thiếu route **chiều về** — phải kiểm tra routing table ở cả hai đầu |
| Nghĩ AD thấp = tốt hơn luôn | AD chỉ so **giữa các nguồn route**; longest prefix match xét **trước** AD |
| OSPF lên neighbor rồi coi như xong | Lên neighbor ≠ có route. Phải kiểm tra `show ip protocols`, passive-interface |
| Không hiểu DR/BDR, cứ để mặc định | Trên multi-access link nó quyết định ai trao đổi LSA với ai — hỏng là mất route |
| Học OSPF mà không vẽ topology ra giấy | LSDB là cái cây. Không vẽ thì không thấy cây. |

---

## 🧭 Thứ tự troubleshoot OSPF không lên neighbor

Học thuộc thứ tự này — nó tiết kiệm hàng giờ:

```
1. Interface có up/up không?             show ip interface brief
2. Hai đầu cùng subnet chưa?             show running-config interface
3. Area có khớp không?                   show ip ospf interface
4. Hello / Dead timer khớp chưa?         show ip ospf interface
5. MTU hai đầu có khớp?                  show interfaces
6. Authentication khớp chưa?             show ip ospf interface
7. Interface có bị passive không?        show ip protocols
8. Router ID có trùng nhau không?        show ip ospf
```

---

## 🚪 Cổng ra phase

- [ ] Dựng OSPF 3 router, 2 area, hội tụ đúng, **không copy cấu hình**
- [ ] Cho một `show ip route` bất kỳ → giải thích được từng dòng
- [ ] Mini Exam Phase 2 ≥ 80%

---

## 🔗 Tài nguyên

- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md)
- 🧯 [`SO-TAY-LOI.md`](../SO-TAY-LOI.md) — mục "Layer 3"
- 🃏 [`flashcards/02-routing.md`](../flashcards/02-routing.md)
- 📖 Sâu hơn ở CCNP: [`CCNP-Encor` Module 04A/04B](https://github.com/hiepnguyen775/CCNP-Encor)
