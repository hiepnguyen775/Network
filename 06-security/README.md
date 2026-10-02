# Phase 6 — SECURITY FUNDAMENTALS

> Không phải "học hack". Đây là phần bạn sẽ bị hỏi nhiều nhất khi làm việc thật: *"chặn được cái này không?"*

| | |
|---|---|
| **Chủ đề** | CIA · AAA · RADIUS/TACACS+ · ACL · DHCP Snooping · DAI · L2 attacks |
| **Số lesson** | 4 |
| **Thời lượng** | ~2 tuần |
| **Công cụ lab** | Packet Tracer |
| **Prerequisite** | Phase 1 (L2), Phase 2 (routing), Phase 3 (NAT) |

---

## 🎯 Mục tiêu phase

- [ ] Viết được ACL chặn **đúng** thứ cần chặn mà không chặn nhầm
- [ ] Biết đặt ACL ở interface nào, hướng nào — **và nói được vì sao**
- [ ] Giải thích được DHCP Snooping chặn tấn công gì, và vì sao DAI phải dựa vào nó
- [ ] Phân biệt Authentication / Authorization / Accounting bằng ví dụ, không bằng định nghĩa

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 35 | CIA Triad · AAA · **RADIUS vs TACACS+** | [`lesson-35-cia-aaa-radius-tacacs.md`](./lesson-35-cia-aaa-radius-tacacs.md) | LAB 60 | ⬜ |
| 36 | **Access Control List (ACL)** ⭐ | [`lesson-36-acl.md`](./lesson-36-acl.md) | LAB 61 | ⬜ |
| 37 | DHCP Snooping · **DAI** · IP Source Guard | [`lesson-37-dhcp-snooping-dai.md`](./lesson-37-dhcp-snooping-dai.md) | LAB 62 | ⬜ |
| 38 | **Tấn công L2 & phòng thủ tổng hợp** | [`lesson-38-l2-attacks.md`](./lesson-38-l2-attacks.md) | LAB 63 | ⬜ |

📝 **Kết thúc phase:** [`review-phase06.md`](./review-phase06.md) — tổng kết + Mini Exam 20 câu

> ⭐ Lesson 38 có **khối cấu hình chuẩn** cho access port — sản phẩm quan trọng nhất
> của cả phase, áp dụng được ngay cho mọi switch.

---

## 🧪 Lab của phase

| Lab | Lesson | Nội dung | File |
|---|:---:|---|---|
| LAB 60 | 35 | AAA với TACACS+ và RADIUS, fallback local | *(tự tạo từ template)* |
| LAB 61 | 36 | ACL standard và extended, debug bằng counter | *(tự tạo từ template)* |
| LAB 62 | 37 | DHCP Snooping, DAI, IPSG — đúng thứ tự | *(tự tạo từ template)* |
| LAB 63 | 38 | 3 tấn công L2 và chứng minh phòng thủ chặn được | *(tự tạo từ template)* |

---

## 🧱 Quy tắc ACL phải thuộc

| Quy tắc | Giải thích |
|---|---|
| Xử lý **từ trên xuống**, dừng ở dòng khớp đầu tiên | Thứ tự dòng quyết định tất cả |
| Cuối ACL luôn có **implicit `deny any`** ẩn | Quên dòng `permit` cuối = chặn sạch |
| **Standard ACL** chỉ lọc theo **source IP** | Đặt **gần đích** |
| **Extended ACL** lọc source + dest + protocol + port | Đặt **gần nguồn** |
| Một interface, một hướng, **một ACL** | Không chồng nhiều ACL cùng chiều |
| Wildcard mask **ngược** với subnet mask | `/24` → wildcard `0.0.0.255` |

> ⚠️ Nhầm wildcard mask là lỗi số 1 ở phase này. IOS **nhận lệnh** nhưng hành vi sai hoàn toàn —
> không có thông báo lỗi nào cả.

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| Đặt ACL sai hướng (`in` vs `out`) | Không có tác dụng, hoặc chặn nhầm chiều |
| Áp ACL lên interface rồi mất luôn SSH vào thiết bị | Luôn kiểm tra ACL có chặn chính traffic quản trị không |
| Bật DAI mà chưa có DHCP Snooping binding | Mọi ARP bị drop → mất mạng toàn VLAN |
| Quên `ip dhcp snooping trust` ở uplink | Switch chặn luôn DHCP server thật |
| Port Security `shutdown` mặc định | Một máy cắm nhầm → port err-disabled, người dùng mất mạng tới khi có người sửa tay |

---

## 🚪 Cổng ra phase

- [ ] Viết Extended ACL cho một yêu cầu bằng tiếng Việt, áp đúng chỗ, verify đúng
- [ ] Dựng lab rogue DHCP → chứng minh DHCP Snooping chặn được
- [ ] Mini Exam Phase 6 ≥ 80%

> 📖 Sâu hơn: [`CCNP-Encor` Module 10 — Security](https://github.com/hiepnguyen775/CCNP-Encor)
