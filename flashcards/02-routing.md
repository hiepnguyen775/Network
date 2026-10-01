# 🃏 Flashcards — Phase 2: Routing

> Che phần **A**, trả lời thành tiếng trước khi xem.
> **Nhịp ôn:** ngày 1 → ngày 3 → ngày 7 → ngày 21.

---

## 🔹 Routing table

**Q:** Router quyết định chọn route theo thứ tự nào?
**A:** **1. Longest prefix match → 2. Administrative Distance thấp nhất → 3. Metric thấp nhất.**
Longest prefix xét **trước** AD — đây là chỗ hay nhầm nhất.

**Q:** `C` và `L` trong `show ip route` khác nhau thế nào?
**A:** `C` = Connected, cả subnet của interface. `L` = Local, chính IP của interface, luôn là `/32`.

**Q:** `[110/2]` nghĩa là gì?
**A:** `[Administrative Distance / Metric]` — 110 là AD của OSPF.

**Q:** AD của Connected / Static / OSPF / EIGRP internal / RIP?
**A:** **0 / 1 / 110 / 90 / 120**.

**Q:** AD dùng để làm gì?
**A:** So sánh **độ tin cậy giữa các nguồn route khác nhau** khi cùng học được một đích với cùng prefix length.

**Q:** Metric dùng để làm gì?
**A:** So sánh **trong cùng một routing protocol** — đường nào tốt hơn.

---

## 🔹 Static route

**Q:** Cú pháp static route cơ bản?
**A:** `ip route <network> <mask> <next-hop | exit-interface>`

**Q:** Default route viết thế nào?
**A:** `ip route 0.0.0.0 0.0.0.0 <next-hop>` — khớp mọi đích, prefix ngắn nhất nên luôn thua các route cụ thể hơn.

**Q:** Floating static route là gì, dùng khi nào?
**A:** Static route được đặt **AD cao hơn** route chính (vd `ip route 0.0.0.0 0.0.0.0 1.1.1.1 **200**`),
chỉ vào bảng khi route chính biến mất → làm **backup** cho dual-WAN.

**Q:** Static route trỏ next-hop và trỏ exit-interface khác nhau gì?
**A:** Trỏ exit-interface trên **link multi-access** (Ethernet) buộc router phải ARP cho **mọi** đích →
tốn tài nguyên. Trên link point-to-point thì không sao.

---

## 🔹 OSPF — cơ chế

**Q:** OSPF là loại routing protocol gì?
**A:** **Link-state**, IGP, dùng thuật toán **Dijkstra (SPF)**, chuẩn mở, protocol number **89**.

**Q:** OSPF Router ID được chọn thế nào?
**A:** 1. `router-id` cấu hình tay → 2. IP cao nhất của **loopback** → 3. IP cao nhất của interface active.

**Q:** Vì sao nên đặt Router ID bằng loopback?
**A:** Loopback **không bao giờ down** → Router ID ổn định, không đổi khi một interface vật lý chết.

**Q:** OSPF cost tính thế nào (mặc định)?
**A:** `cost = reference bandwidth (100 Mbps) / bandwidth của interface`.
Vì vậy mọi link ≥ 100 Mbps đều cost = 1 → cần chỉnh `auto-cost reference-bandwidth`.

**Q:** DR / BDR sinh ra để làm gì?
**A:** Trên link **multi-access** (Ethernet), tránh việc N router phải peer đầy đủ với nhau
(N×(N−1)/2 adjacency). Tất cả chỉ peer với DR và BDR.

**Q:** DR/BDR được bầu thế nào?
**A:** **Priority cao nhất** thắng (mặc định 1, priority 0 = không tham gia);
hoà thì **Router ID cao nhất** thắng. **Không có preemption** — DR đã bầu rồi thì giữ nguyên.

**Q:** Loại link nào **không** bầu DR/BDR?
**A:** **Point-to-point**.

---

## 🔹 OSPF — states & troubleshoot

**Q:** Các OSPF neighbor state theo thứ tự?
**A:** `Down → Init → 2-Way → ExStart → Exchange → Loading → Full`.

**Q:** State bình thường cuối cùng là gì?
**A:** **`FULL`** — trừ giữa hai DROTHER trên multi-access thì dừng ở **`2-WAY`** (và đó là bình thường).

**Q:** Neighbor kẹt ở `EXSTART` / `EXCHANGE` — nghi gì đầu tiên?
**A:** **MTU mismatch** giữa hai đầu.

**Q:** Neighbor kẹt ở `INIT` — nghi gì?
**A:** Một chiều không nhận được hello — ACL chặn, hoặc interface bị `passive`.

**Q:** 6 thứ phải khớp để OSPF lên neighbor?
**A:** **Cùng subnet · Area ID · Hello/Dead timer · Authentication · MTU · Không bị passive**
(và Router ID phải **khác** nhau).

**Q:** OSPF lên `FULL` rồi mà vẫn không có route — xem gì?
**A:** `show ip protocols` → `network` statement sai wildcard, hoặc interface bị `passive-interface`.

**Q:** Hello / Dead timer mặc định của OSPF trên Ethernet?
**A:** Hello **10** giây, Dead **40** giây (= 4 × hello).

---

## 🔹 OSPF — area & LSA

**Q:** Area 0 là gì, vì sao bắt buộc?
**A:** **Backbone area**. Mọi area khác phải nối trực tiếp với area 0 — để tránh routing loop
giữa các area (OSPF chỉ chống loop *trong* một area bằng SPF).

**Q:** ABR và ASBR khác nhau thế nào?
**A:** **ABR** nối giữa các area OSPF. **ASBR** nối OSPF với thế giới bên ngoài (redistribute).

**Q:** LSA Type 1 / 2 / 3 là gì? (mức CCNA)
**A:** **Type 1** Router LSA (trong area) · **Type 2** Network LSA (do DR tạo trên multi-access) ·
**Type 3** Summary LSA (do ABR bơm giữa các area).

**Q:** `O IA` trong routing table nghĩa là gì?
**A:** OSPF **Inter-Area** — route học từ area khác, qua ABR.

---

## 🔹 Lệnh phải thuộc

| Mục đích | Lệnh |
|---|---|
| Xem routing table | `show ip route` |
| Xem router chọn route nào cho 1 đích | `show ip route 8.8.8.8` |
| Xem protocol đang chạy | `show ip protocols` |
| Xem neighbor OSPF | `show ip ospf neighbor` |
| Xem area/timer/cost của interface | `show ip ospf interface <int>` |
| Xem Router ID, số area | `show ip ospf` |
| Debug adjacency | `debug ip ospf adj` → **nhớ `undebug all`** |

---

## 📊 Theo dõi ôn tập

| Lần ôn | Ngày | Số câu sai | Câu cần ôn lại |
|:---:|---|:---:|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
