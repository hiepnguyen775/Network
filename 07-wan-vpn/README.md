# Phase 7 — WAN / ENTERPRISE

> Phase cuối trước Final Project. Mức CCNA yêu cầu **hiểu khái niệm** nhiều hơn cấu hình — nhưng đây là phần liên quan trực tiếp nhất tới công việc hạ tầng thật.

| | |
|---|---|
| **Chủ đề** | WAN concepts · VPN · GRE · IPsec · Site-to-Site · SD-WAN |
| **Số lesson** | 3 |
| **Thời lượng** | ~1.5 tuần |
| **Công cụ lab** | ⚠️ **GNS3 / EVE-NG** — Packet Tracer không mô phỏng đủ IPsec |
| **Prerequisite** | Phase 2 (routing), Phase 3 (NAT), Phase 6 (ACL) |

---

## 🎯 Mục tiêu phase

- [ ] Phân biệt được leased line / MPLS / Internet VPN — và chi phí, SLA, rủi ro của từng loại
- [ ] Giải thích được **vì sao GRE cần IPsec** và ngược lại, IPsec thuần thiếu gì
- [ ] Dựng được một tunnel Site-to-Site và verify nó đúng cách
- [ ] Nói được SD-WAN giải quyết vấn đề gì so với WAN truyền thống

---

## 📚 Danh sách lesson

| # | Lesson | File | 🧪 Lab | Trạng thái |
|:---:|---|---|:---:|:---:|
| 39 | WAN concepts: leased line · MPLS · Internet · dual-WAN & failover | — | | ⬜ |
| 40 | VPN fundamentals · GRE tunnel · IPsec (IKE, ESP, transform set) ⭐ | — | ✅ | ⬜ |
| 41 | Site-to-Site vs Remote Access · SD-WAN concepts | — | ✅ | ⬜ |

---

## 🔐 GRE vs IPsec — bảng phải hiểu

| | GRE | IPsec |
|---|---|---|
| Mã hoá | ❌ Không | ✅ Có |
| Chở được multicast / routing protocol | ✅ Có | ❌ Không (IPsec thuần) |
| Chở được giao thức non-IP | ✅ Có | ❌ Không |
| Dùng một mình trong production? | ❌ Không an toàn | ⚠️ Được, nhưng không chạy được OSPF qua tunnel |

> 👉 Vì vậy thực tế hay dùng **GRE over IPsec**: GRE lo việc chở routing protocol,
> IPsec lo việc mã hoá. Hiểu được chỗ này là hiểu được 80% thiết kế VPN doanh nghiệp.

---

## ⚠️ Bẫy hay gặp ở phase này

| Bẫy | Thực tế |
|---|---|
| Lab IPsec trên Packet Tracer | Không mô phỏng đủ — **phải** dùng GNS3/EVE-NG |
| Tunnel "up" nhưng không có traffic | `up/up` của tunnel GRE chỉ nghĩa là có route tới destination, không nghĩa là thông |
| Quên MTU/MSS qua tunnel | Gói lớn bị drop, triệu chứng: ping được nhưng web không load |
| NAT và IPsec đặt chung interface, không loại trừ traffic VPN | Traffic VPN bị NAT → tunnel không lên |
| Nghĩ SD-WAN là "VPN nhưng mới" | SD-WAN là **điều phối tập trung + chọn đường theo ứng dụng** |

---

## 🚪 Cổng ra phase

- [ ] Dựng GRE over IPsec giữa 2 site trên GNS3/EVE-NG, chạy OSPF qua tunnel
- [ ] Giải thích được toàn bộ quá trình thiết lập IKE Phase 1 / Phase 2
- [ ] Mini Exam Phase 7 ≥ 80%

---

## 🏁 Sau phase này

👉 **[FINAL CCNA PROJECT](../labs/README.md)** — tổng hợp toàn bộ Phase 0 → 7.
