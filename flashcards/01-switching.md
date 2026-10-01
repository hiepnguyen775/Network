# 🃏 Flashcards — Phase 1: Switching

> Che phần **A**, trả lời thành tiếng trước khi xem.
> **Nhịp ôn:** ngày 1 → ngày 3 → ngày 7 → ngày 21.

---

## 🔹 Switch & MAC table

**Q:** Switch học MAC address bằng cách nào?
**A:** Đọc **source MAC** của frame đi vào, ghi vào MAC table kèm port và timer (mặc định 300 giây).

**Q:** Switch làm gì khi không biết destination MAC?
**A:** **Flood** ra tất cả port trong cùng VLAN, trừ port nhận.

**Q:** MAC một địa chỉ nhảy qua lại giữa 2 port liên tục nghĩa là gì?
**A:** Gần như chắc chắn có **loop L2**, hoặc ai đó cắm nhầm dây.

---

## 🔹 VLAN

**Q:** VLAN sinh ra để giải quyết vấn đề gì?
**A:** Chia nhỏ **broadcast domain** mà không cần mua thêm switch vật lý; kèm theo đó là tách biệt bảo mật và linh hoạt về vị trí.

**Q:** Hai PC khác VLAN muốn nói chuyện với nhau cần gì?
**A:** Một thiết bị **L3** — router (Router-on-a-Stick) hoặc **L3 switch** (SVI).

**Q:** Access port và trunk port khác nhau thế nào?
**A:** Access chở **một** VLAN và gửi frame **không tag**. Trunk chở **nhiều** VLAN và **tag 802.1Q**.

**Q:** 802.1Q tag nằm ở đâu trong frame, dài bao nhiêu?
**A:** Chèn vào **giữa** Source MAC và EtherType, dài **4 byte** (chứa VLAN ID 12 bit → tối đa 4094 VLAN).

**Q:** Native VLAN là gì?
**A:** VLAN duy nhất trên trunk được truyền **không tag**. Mặc định là VLAN 1.

**Q:** Native VLAN mismatch gây hậu quả gì?
**A:** Traffic của VLAN native đầu này **rò sang** VLAN khác ở đầu kia. IOS cảnh báo `%CDP-4-NATIVE_VLAN_MISMATCH`.

**Q:** Trunk lên rồi nhưng VLAN 20 không qua được — xem gì?
**A:** `show interfaces trunk` → cột **Vlans allowed on trunk**.

---

## 🔹 Inter-VLAN routing

**Q:** Router-on-a-Stick là gì?
**A:** Một interface vật lý của router chia thành nhiều **subinterface**, mỗi subinterface gắn một VLAN (`encapsulation dot1Q <vlan>`), nối với switch bằng trunk.

**Q:** Khi nào dùng L3 switch (SVI) thay vì Router-on-a-Stick?
**A:** Khi cần **hiệu năng** — SVI route bằng ASIC ở tốc độ wire-speed; Router-on-a-Stick bị nghẽn ở một link vật lý.

**Q:** SVI cần gì để `up/up`?
**A:** VLAN phải **tồn tại và active**, và có **ít nhất một port up** thuộc VLAN đó (hoặc trunk cho VLAN đó).

---

## 🔹 STP

**Q:** STP sinh ra để giải quyết vấn đề gì?
**A:** Chống **loop L2**. Không có STP, một vòng lặp gây broadcast storm làm sập cả mạng trong vài giây.

**Q:** Vì sao loop L2 nguy hiểm hơn loop L3?
**A:** Frame Ethernet **không có TTL** — gói chạy vòng mãi mãi, nhân lên theo cấp số nhân.

**Q:** Root bridge được bầu dựa trên gì?
**A:** **Bridge ID** thấp nhất = `Priority (mặc định 32768 + VLAN ID)` + `MAC address`.

**Q:** Làm sao để chỉ định root bridge thay vì để bầu ngẫu nhiên?
**A:** `spanning-tree vlan <id> root primary`, hoặc đặt priority thấp (`spanning-tree vlan 10 priority 4096`).

**Q:** Các port role của STP?
**A:** **Root port** (đường tốt nhất về root), **Designated port** (forward cho segment), **Blocked/Non-designated**.

**Q:** RSTP nhanh hơn STP ở điểm nào?
**A:** Hội tụ trong **vài giây** thay vì 30–50 giây, nhờ cơ chế proposal/agreement và các port state rút gọn.

**Q:** PortFast dùng ở đâu? Rủi ro gì?
**A:** Dùng ở **access port nối PC**, cho port lên forwarding ngay. Rủi ro: ai cắm switch vào đó → loop. Vì vậy luôn đi kèm **BPDU Guard**.

**Q:** BPDU Guard làm gì?
**A:** Nếu port có PortFast nhận được BPDU → **err-disable** port ngay.

---

## 🔹 EtherChannel & Port Security

**Q:** EtherChannel dùng để làm gì?
**A:** Gộp nhiều link vật lý thành **một link logic** — tăng băng thông và dự phòng, mà STP chỉ thấy **một** link nên không block.

**Q:** LACP và PAgP khác nhau thế nào?
**A:** **LACP** là chuẩn mở (IEEE 802.3ad), mode `active`/`passive`. **PAgP** là của Cisco, mode `desirable`/`auto`.

**Q:** EtherChannel không bundle — nguyên nhân hay gặp?
**A:** Hai đầu lệch về: speed/duplex, VLAN allowed, access/trunk mode, hoặc mode LACP cả hai đều `passive`.

**Q:** Port Security mặc định làm gì khi vi phạm?
**A:** Mode `shutdown` → port vào **err-disabled**, phải `shutdown` + `no shutdown` để khôi phục.

**Q:** Ba violation mode của Port Security?
**A:** `protect` (drop im lặng) · `restrict` (drop + log + counter) · `shutdown` (err-disable, **mặc định**).

---

## 🔹 Lệnh phải thuộc

| Mục đích | Lệnh |
|---|---|
| Xem VLAN và port | `show vlan brief` |
| Xem trunk | `show interfaces trunk` |
| Xem trạng thái port | `show interfaces status` |
| Xem MAC table | `show mac address-table` |
| Xem STP | `show spanning-tree [vlan N]` |
| Xem EtherChannel | `show etherchannel summary` |
| Gán VLAN cho port | `switchport mode access` + `switchport access vlan 10` |
| Tạo trunk | `switchport mode trunk` + `switchport trunk native vlan 99` |

---

## 📊 Theo dõi ôn tập

| Lần ôn | Ngày | Số câu sai | Câu cần ôn lại |
|:---:|---|:---:|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
