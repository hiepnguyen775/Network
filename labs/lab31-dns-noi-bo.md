# LAB 31 — DNS trong doanh nghiệp

> 📦 **Phase 0 (lesson 08) đã dạy gì — lab này thêm gì:** Phase 0 dạy DNS là gì
> *(phân giải tên → IP)*. Lab này triển khai **DNS nội bộ**: tạo bản ghi A/CNAME,
> so sánh `nslookup`, hiểu **TTL** và **split-DNS**.

| | |
|---|---|
| **Phase** | 3 |
| **Lesson liên quan** | [Lesson 26 — DNS doanh nghiệp](../03-services/lesson-26-dns-doanh-nghiep.md) |
| **Công cụ** | Cisco Packet Tracer + máy thật *(nslookup)* |
| **Thời lượng** | ~1.5 giờ |
| **Độ khó** | ⭐⭐ |
| **Trạng thái** | ⬜ Chưa làm |
| **Ngày làm** | — |

---

## 1. Mục tiêu

- [ ] Dựng **DNS server nội bộ** với bản ghi A và CNAME
- [ ] Dùng `nslookup` phân giải tên và **đọc** kết quả *(server trả lời, TTL)*
- [ ] Hiểu **split-DNS**: cùng tên, trong/ngoài trả IP khác nhau
- [ ] Thấy ảnh hưởng của **TTL** tới cache
- [ ] Tự gây & sửa 3 lỗi DNS phổ biến

## 2. Prerequisite

- [Lesson 08](../00-foundation/lesson-08-dns-va-dhcp.md) — DNS cơ bản
- [Lesson 26](../03-services/lesson-26-dns-doanh-nghiep.md) — zone, split-DNS, TTL
- [LAB 05](lab05-dhcp-server-relay.md) — DHCP đẩy `dns-server`

---

## 3. Topology

```text
   PC1 ── SW1 ── R1 ── DNS-INT  10.0.99.53  (nội bộ)
   PC2             │
                   └──── "Internet" ── DNS-EXT 8.8.8.8
```

| Thiết bị | Vai trò |
|---|---|
| DNS-INT | Server-PT bật DNS, chứa zone `cty.local` |
| PC1, PC2 | Client, dns-server = `10.0.99.53` *(qua DHCP)* |
| WEB | `10.0.99.80` — đích của `web.cty.local` |

## 4. IP Addressing Table

| Device | IP | Ghi chú |
|---|---|---|
| R1 Gi0/0 | `10.0.10.1/24` | GW LAN |
| R1 Gi0/1 | `10.0.99.1/24` | GW server |
| DNS-INT | `10.0.99.53/24` | DNS nội bộ |
| WEB | `10.0.99.80/24` | web server |
| PC1/PC2 | DHCP, dns = `10.0.99.53` | — |

---

## 5. Yêu cầu LAB

- [ ] `web.cty.local` phân giải ra `10.0.99.80` từ PC
- [ ] CNAME `portal.cty.local` → `web.cty.local`
- [ ] `nslookup` chỉ ra đúng server trả lời
- [ ] Hoàn thành mục **8. BREAK** với đủ 3 lỗi

---

## 6. Step-by-step

### Bước 1 — Dựng DNS nội bộ

Trên DNS-INT *(Services → DNS → On)*, thêm bản ghi:

| Name | Type | Detail |
|---|---|---|
| `web.cty.local` | A | `10.0.99.80` |
| `portal.cty.local` | CNAME | `web.cty.local` |
| `mail.cty.local` | A | `10.0.99.25` |

### Bước 2 — Client trỏ DNS nội bộ

Đảm bảo PC có `dns-server = 10.0.99.53` *(qua DHCP hoặc gán tay)*.

### Bước 3 — Phân giải và đọc nslookup ⭐

> 🔴 **DỰ ĐOÁN:** `nslookup portal.cty.local` trả về gì? Một dòng hay hai?
> Vì sao CNAME lại hiện thêm tên khác?

```cisco
PC> nslookup web.cty.local
PC> nslookup portal.cty.local
PC> ping web.cty.local
```

### Bước 4 — Split-DNS (khái niệm + mô phỏng)

Split-DNS: cùng tên `web.cty.local`, client **nội bộ** nhận IP private `10.0.99.80`,
client **Internet** nhận IP public `203.0.113.80`.

```text
Nội bộ  → DNS-INT  → web.cty.local = 10.0.99.80   (IP nội bộ, nhanh)
Ngoài   → DNS-EXT  → web.cty.local = 203.0.113.80 (IP public, qua NAT)
```

> 💡 Packet Tracer khó mô phỏng đầy đủ split-DNS. Hiểu nguyên lý: **cùng tên,
> hai view khác nhau tuỳ nguồn truy vấn**. Lợi ích: nội bộ đi đường tắt, không
> vòng ra Internet rồi NAT ngược vào *(hairpin NAT)*.

---

## 7. Verification

```text
# output điển hình — tự verify trên lab của bạn
PC> nslookup web.cty.local
Server:  DNS-INT
Address: 10.0.99.53

Name:    web.cty.local
Address: 10.0.99.80
```

```text
# output điển hình — CNAME hiện cả alias lẫn tên thật
PC> nslookup portal.cty.local
Server:  DNS-INT
Address: 10.0.99.53

Name:    web.cty.local
Address: 10.0.99.80
Aliases: portal.cty.local
```

**Bảng kiểm chứng:**

| # | Kiểm tra | Mong đợi | Thực tế |
|:---:|---|---|---|
| 1 | `nslookup web.cty.local` → `10.0.99.80` | ✅ | |
| 2 | `nslookup portal.cty.local` → trỏ về web | ✅ *(Aliases)* | |
| 3 | `ping web.cty.local` thành công | ✅ | |
| 4 | Server trả lời là `10.0.99.53` | ✅ | |

---

## 8. BREAK → Troubleshooting ⚠️ BẮT BUỘC

### Lỗi 1 — Client trỏ sai DNS server ⭐

```text
Đổi DNS của PC1 thành 8.8.8.8 (DNS ngoài)
```

| | |
|---|---|
| `nslookup web.cty.local` từ PC1: kết quả? | |
| Vì sao DNS ngoài **không** phân giải được `cty.local`? | |
| `ping 10.0.99.80` *(bằng IP)*: có được không? | |
| Kết luận: lỗi ở DNS hay ở kết nối mạng? | |

### Lỗi 2 — CNAME trỏ tới tên không tồn tại

```text
Sửa portal.cty.local CNAME → web2.cty.local (không có bản ghi A)
```

| | |
|---|---|
| `nslookup portal.cty.local`: thông báo gì? | |
| CNAME có tự tạo được đích không? | |
| Thứ tự phân giải CNAME → A diễn ra thế nào? | |

### Lỗi 3 — TTL quá cao sau khi đổi IP

```text
Đặt TTL bản ghi web = 86400 (1 ngày)
PC phân giải web → cache 10.0.99.80
Đổi A record web → 10.0.99.81
PC phân giải lại ngay
```

| | |
|---|---|
| PC nhận IP cũ hay mới? Vì sao? | |
| Bao lâu PC mới thấy IP mới *(nếu không xoá cache)*? | |
| `ipconfig /flushdns` làm gì? | |
| Trước khi đổi IP server quan trọng, nên làm gì với TTL? | |

> Mỗi phát hiện → chép sang [`../SO-TAY-LOI.md`](../SO-TAY-LOI.md).

---

## 9. Challenge

1. Người dùng báo "vào `web.cty.local` không được nhưng vào bằng IP thì được".
   Chẩn đoán theo thứ tự.
2. Vì sao doanh nghiệp dùng split-DNS thay vì để nội bộ truy cập qua IP public?
3. A record và CNAME: khi nào bắt buộc dùng A, khi nào nên dùng CNAME?
4. TTL nên đặt cao hay thấp? Nêu đánh đổi, và chiến lược khi sắp migrate server.

<details>
<summary>Đáp án</summary>

**1.** Thứ tự chẩn đoán:

```text
1. ping <IP server>          → OK?  (loại trừ lỗi mạng/định tuyến)
   - nếu ping IP được mà tên không được → gần như chắc chắn lỗi DNS
2. nslookup web.cty.local    → server nào trả lời? có kết quả không?
   - "can't find" / timeout → client trỏ sai DNS, hoặc thiếu bản ghi
3. Kiểm tra DNS client đang dùng:  ipconfig /all → DNS Servers = ?
   - sai server → sửa DHCP/gán tay
4. Trên DNS server: bản ghi A của web còn không?
5. ipconfig /flushdns  → loại trừ cache cũ
```

**2.** Split-DNS cho nội bộ trả **IP private** → traffic đi **thẳng** tới server trong LAN.
Nếu để nội bộ dùng IP public, gói phải: ra tới router biên → **NAT ngược vào** *(hairpin/
NAT loopback)* → quay lại server. Vòng vo, tốn tài nguyên router, và nhiều router **không
hỗ trợ** hairpin → nội bộ không vào được server của chính mình. Split-DNS tránh toàn bộ.

**3.**

| | A record | CNAME |
|---|---|---|
| Trỏ tới | **IP** trực tiếp | **tên khác** *(alias)* |
| Bắt buộc A | Tên gốc của một host, bản ghi ở **đỉnh zone** *(apex, `cty.local`)* | — |
| Nên CNAME | `www`, `portal`, `shop`... trỏ về một host chung | Đổi IP một chỗ *(A record)*, mọi alias theo luôn |

Lưu ý: **không** đặt CNAME ở apex zone *(RFC cấm)* — dùng A/ALIAS.

**4.** Đánh đổi:

| TTL | Ưu | Nhược |
|---|---|---|
| **Cao** *(vd 1 ngày)* | Ít truy vấn, nhẹ DNS server, nhanh | Đổi IP mất **cả ngày** mới lan hết |
| **Thấp** *(vd 300s)* | Đổi IP lan nhanh | Nhiều truy vấn hơn |

Chiến lược migrate: **hạ TTL xuống thấp** *(300s)* **trước** ngày migrate vài ngày →
đến lúc đổi IP, client cập nhật trong 5 phút → xong rồi **nâng TTL lại**.

</details>

---

## 10. Solution

<details>
<summary>Mở sau khi đã tự làm xong</summary>

### Giải thích các lỗi BREAK

**Lỗi 1 — sai DNS server ⭐:** DNS ngoài *(8.8.8.8)* **không có** zone `cty.local`
→ trả "can't find / NXDOMAIN". Nhưng `ping 10.0.99.80` *(IP)* vẫn OK → chứng tỏ
**mạng tốt, chỉ DNS sai**. Đây là cách phân biệt kinh điển: **tên fail + IP OK = lỗi DNS**.

**Lỗi 2 — CNAME trỏ tên không tồn tại:** CNAME chỉ là "bí danh" — nó **không tạo** đích.
Phân giải `portal` → CNAME `web2` → tra tiếp A của `web2` → **không có** → NXDOMAIN.
Chuỗi phân giải: CNAME phải dẫn tới một tên **có A record** cuối cùng.

**Lỗi 3 — TTL cao:** Sau khi phân giải, client **cache** kết quả trong `TTL` giây.
TTL 86400 → client giữ IP cũ `10.0.99.80` **cả ngày** dù server đã đổi sang `.81`.
`ipconfig /flushdns` xoá cache ngay → phân giải lại nhận IP mới. Bài học: **hạ TTL
trước khi migrate**.

### Bảng tổng kết

| Triệu chứng | Nguyên nhân | Kiểm tra |
|---|---|---|
| Tên fail, IP OK | Lỗi DNS *(sai server / thiếu bản ghi)* | `nslookup`, `ipconfig /all` |
| CNAME NXDOMAIN | Đích CNAME không có A | kiểm tra chuỗi CNAME→A |
| Đổi IP không ăn | TTL cache cao | `ipconfig /flushdns`, hạ TTL |

</details>

---

## 📝 Ghi chú & bài học rút ra

- "Tên fail + IP OK = lỗi DNS" — tôi đã kiểm chứng chưa? ___
- Lỗi 3 (TTL) — chiến lược hạ TTL trước migrate tôi hiểu chưa? ___
- Lỗi đã chép sang `SO-TAY-LOI.md`: ⬜
