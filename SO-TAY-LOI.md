# 🧯 SỔ TAY LỖI

> Mỗi lần lab hỏng, ghi vào đây **ngay lúc đó** — đừng tin trí nhớ.
> Lỗi được ghi lại là lỗi bạn sẽ nhận ra trong 30 giây ở lần sau; lỗi không ghi là lỗi mất 2 tiếng.

---

## Cách ghi

Mỗi lỗi một dòng trong bảng. Cột **Nguyên nhân gốc** là cột quan trọng nhất —
nếu bạn không điền được nó, nghĩa là bạn mới *làm cho nó chạy lại*, chưa *hiểu vì sao nó hỏng*.

```markdown
| 2026-10-05 | 1 | PC1 không ping được PC2 cùng VLAN | show vlan brief | Port Fa0/2 nằm VLAN 1, không phải VLAN 10 | switchport access vlan 10 | Gán VLAN xong phải verify, đừng tin là đã gõ |
```

---

## 📋 Bảng lỗi

| Ngày | Phase | Triệu chứng | Lệnh đã dùng để tìm | Nguyên nhân gốc | Cách sửa | Bài học |
|---|:---:|---|---|---|---|---|
| | | | | | | |

---

## 🔁 Lỗi kinh điển — biết trước để đỡ mất thời gian

Danh sách này **không thay thế** việc bạn tự gặp lỗi. Nó để bạn đối chiếu sau khi đã vật lộn.

### Layer 1–2

| Triệu chứng | Nghi ngờ đầu tiên | Lệnh kiểm chứng |
|---|---|---|
| Interface `down/down` | Cáp, hoặc đầu kia shutdown | `show interfaces status` |
| Interface `up/down` | Lệch encapsulation / clock rate (serial) | `show interfaces <int>` |
| Trunk không lên | Hai đầu không cùng mode, hoặc VLAN không allowed | `show interfaces trunk` |
| Ping lúc được lúc không | Native VLAN mismatch, hoặc STP đang hội tụ | `show interfaces trunk`, `show spanning-tree` |
| Cả mạng chậm/treo | Loop L2 — broadcast storm | `show spanning-tree`, đèn port nháy loạn |
| MAC học sai port | Có loop, hoặc ai đó cắm nhầm | `show mac address-table` |

### Layer 3

| Triệu chứng | Nghi ngờ đầu tiên | Lệnh kiểm chứng |
|---|---|---|
| Ping gateway OK, ping xa fail | Thiếu route chiều **về** | `show ip route` ở cả 2 đầu |
| Ping IP được, ping tên fail | DNS | `show hosts`, `nslookup` |
| Route biến mất | Interface down, hoặc AD route khác thắng | `show ip route`, `show ip protocols` |
| OSPF không lên neighbor | Area / subnet / hello-dead timer / MTU / authentication lệch | `show ip ospf neighbor`, `show ip ospf interface` |
| OSPF lên nhưng không có route | `network` statement sai wildcard, hoặc interface passive | `show ip protocols` |
| Ping được 1 chiều | ACL, hoặc NAT thiếu chiều | `show access-lists`, `show ip nat translations` |

### Hay sai do thói quen

| Sai lầm | Hậu quả |
|---|---|
| Quên `no shutdown` | Interface không bao giờ lên — mất 20 phút để nhận ra |
| Quên `copy running-config startup-config` | Reload là mất sạch cấu hình |
| Nhầm wildcard mask với subnet mask trong OSPF/ACL | Lệnh nhận nhưng hành vi sai hoàn toàn |
| ACL implicit `deny any` ở cuối | Chặn luôn thứ không định chặn |
| Đặt ACL sai hướng (`in` vs `out`) | Không có tác dụng, hoặc chặn nhầm |
| Subnet mask lệch giữa 2 đầu link | Hai đầu "thấy" khác subnet → không ping được |
| Default gateway của PC trỏ sai | Trong subnet thì OK, ra ngoài thì chết |

---

## 🧭 Quy tắc troubleshoot của riêng tôi

> Viết lại bằng chữ của bạn sau mỗi phase — đây là thứ phân biệt người làm được việc và người học thuộc.

1. *(ví dụ)* Luôn `show ip interface brief` trước khi làm bất cứ gì khác.
2.
3.
