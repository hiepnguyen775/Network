# 🌐 Network Mentor

> **Lộ trình tự học Network: Fundamentals → CCNA 200-301 → CCNP → Automation**, vận hành bằng một AI mentor theo prompt chuẩn.

![Mục tiêu](https://img.shields.io/badge/M%E1%BB%A5c%20ti%C3%AAu-CCNA%20200--301-1f6feb)
![Phase](https://img.shields.io/badge/Phase-0%20%E2%86%92%209-8957e5)
![Lab](https://img.shields.io/badge/Lab-Packet%20Tracer%20%7C%20GNS3%20%7C%20EVE--NG-2da44e)
![Ngôn ngữ](https://img.shields.io/badge/Ng%C3%B4n%20ng%E1%BB%AF-Ti%E1%BA%BFng%20Vi%E1%BB%87t-d29922)
![Nội dung](https://img.shields.io/badge/N%E1%BB%99i%20dung-41%2F41%20lesson-2da44e)

---

## 📑 Mục lục

1. [Repo này là gì — và không phải gì](#1-repo-này-là-gì--và-không-phải-gì)
2. [Bắt đầu trong 5 phút](#2-bắt-đầu-trong-5-phút)
3. [Vòng lặp học](#3-vòng-lặp-học)
4. [Cấu trúc repo](#4-cấu-trúc-repo)
5. [Lộ trình 10 phase](#5-lộ-trình-10-phase)
6. [Quy ước đặt tên file](#6-quy-ước-đặt-tên-file)
7. [Nguyên tắc tự học](#7-nguyên-tắc-tự-học)
8. [Môi trường lab](#8-môi-trường-lab)
9. [Quan hệ với 2 repo anh em](#9-quan-hệ-với-2-repo-anh-em)
10. [FAQ](#10-faq)

---

## 1. Repo này là gì — và không phải gì

| | |
|---|---|
| ✅ **Là** | Một **bộ tài liệu tự học hoàn chỉnh** — mở ra đọc là học được, không cần thầy, không cần hỏi ai. Mỗi lesson đủ 15 phần: concept → vì sao → packet flow → CLI → verify → troubleshoot → lab → kiểm tra. |
| ✅ **Là** | Nơi lưu **kết quả học của bạn** — lab đã làm, lỗi đã gặp, tiến độ. |
| ✅ **Có thêm** | [`MENTOR_PROMPT.md`](./MENTOR_PROMPT.md) — **tuỳ chọn**. Khi bí một chỗ, dán nó vào AI để được giảng riêng chỗ đó. Không bắt buộc. |
| ❌ **Không phải** | Bộ đề thi / dump. Mục tiêu là **làm được việc**, cái chứng chỉ là hệ quả. |

> **Đọc theo thứ tự [`ROADMAP.md`](./ROADMAP.md).** Hết Phase 0 → Phase 1 → … → Final Project.

---

## 2. Bắt đầu trong 5 phút

```text
1. Cài Cisco Packet Tracer (netacad.com, miễn phí) + Wireshark.
2. Mở 00-foundation/README.md  →  đọc lesson-01  →  lesson-02  →  ...
3. Tới mục "11. LAB" thì DỪNG ĐỌC, mở Packet Tracer làm lab.
   Làm xong nhớ mục BREAK — phá rồi tự sửa.
4. Hết lesson: ghi 1 dòng vào PROGRESS.md, tick ROADMAP.md, commit.
5. Hết phase: làm review-phaseNN.md (mini exam). Dưới 80% thì học lại.
```

**Chỉ cần đọc theo thứ tự.** Không có bước nào bắt buộc phải hỏi AI.

### Khi bí — tuỳ chọn, không bắt buộc

Dán [`MENTOR_PROMPT.md`](./MENTOR_PROMPT.md) + [`PROGRESS.md`](./PROGRESS.md) vào AI (Claude / ChatGPT / Gemini)
để được giảng riêng chỗ đang kẹt, hoặc chấm bài tập. Các lệnh dùng được:

| Gõ | Tác dụng |
|---|---|
| `full` | Xuất cả lesson một mạch, không chia beat |
| `chậm lại` | Cắt beat nhỏ hơn nữa |
| `lab` | Nhảy thẳng vào phần LAB của lesson hiện tại |
| `ôn` | Spaced repetition các mục yếu đang ghi trong `PROGRESS.md` |
| `check` | Làm Knowledge Check L1 → L5 cho topic vừa học |
| `sâu hơn` | Đào xuống tầng 🔧 Engineer / 🏭 Production |
| `tóm tắt` | Chốt topic hiện tại thành Summary + Commands + Common Mistakes |
| `packet` | Mô tả lại packet flow của topic hiện tại, từng hop, từng header |
| `sai rồi` | Phản bác AI — buộc nó kiểm tra lại và dẫn nguồn, không vội nhận sai |
| `flashcard` | Sinh bộ thẻ ghi nhớ cho phase vừa xong |
| `mini exam` | Sinh bài kiểm tra cuối phase (15–20 câu) |

> Bảng đầy đủ nằm trong [`MENTOR_PROMPT.md`](./MENTOR_PROMPT.md#6-nhịp--độ-dài-chống-loãng--đọc-kỹ) — hai bảng luôn phải khớp nhau.

---

## 3. Vòng lặp học

```text
LEARN → UNDERSTAND → CONFIGURE → VERIFY → BREAK → TROUBLESHOOT → EXPLAIN → DESIGN → AUTOMATE
  ↑                                                                                     │
  └──────────────────────────── spaced repetition ──────────────────────────────────────┘
```

**Bước quan trọng nhất và hay bị bỏ qua nhất là `BREAK`.** Cấu hình chạy được chưa chứng minh bạn hiểu —
chỉ khi bạn **cố tình phá nó rồi tự tìm lại được nguyên nhân**, kiến thức mới thành của bạn.

Đích đến:

> *"Nhìn một topology, hiểu traffic flow, cấu hình được, verify được, tìm được lỗi, và giải thích tại sao network hoạt động hoặc không."*

---

## 4. Cấu trúc repo

```text
network-mentor/
├── MENTOR_PROMPT.md        ⭐ Prompt điều khiển AI mentor — file quan trọng nhất
├── check.py                Script kiểm tra nhất quán repo — chạy: python check.py
├── ROADMAP.md              Lộ trình 10 phase, tick tiến độ
├── PROGRESS.md             Nhật ký học + điểm yếu (state cho AI đọc)
├── SO-TAY-LOI.md           Sổ tay lỗi: triệu chứng → nguyên nhân → cách sửa
│
├── assessment/             Ngân hàng câu hỏi đánh giá đầu vào & theo phase
├── templates/              Khung chuẩn: LESSON / LAB / MODULE REVIEW
├── labs/                   Mỗi LAB một file (labNN-ten.md) + INDEX
├── flashcards/             Thẻ ghi nhớ nhanh theo phase
├── cheatsheets/            Bảng tra nhanh: subnetting, show commands, ports...
│
├── 00-foundation/          OSI/TCP-IP, IP, subnetting, ARP, TCP/UDP, DNS/DHCP, NAT
├── 01-switching/           VLAN, trunk, inter-VLAN, STP/RSTP, EtherChannel, port security
├── 02-routing/             Static/default/floating, AD & metric, OSPF single/multi-area
├── 03-services/            DHCP, DNS, NAT/PAT, NTP, Syslog, SNMP, SSH, QoS
├── 04-ipv6/                Address types, SLAAC, DHCPv6, ND, OSPFv3
├── 05-wireless/            WLAN, AP/WLC, SSID, băng tần, WPA2/WPA3
├── 06-security/            AAA, ACL, DHCP snooping, DAI, L2 attacks
├── 07-wan-vpn/             WAN, GRE, IPsec, Site-to-Site VPN, SD-WAN
├── 08-ccnp/                → trỏ sang repo CCNP-Encor
└── 09-automation/          → trỏ sang repo Network-Automation
```

| Thư mục / file | Dùng khi nào |
|---|---|
| [`MENTOR_PROMPT.md`](./MENTOR_PROMPT.md) | Đầu **mỗi** phiên học — luôn dán file này |
| [`PROGRESS.md`](./PROGRESS.md) | Dán kèm prompt; cập nhật **cuối mỗi buổi** |
| [`ROADMAP.md`](./ROADMAP.md) | Tick `[x]` khi đã học chắc một mục |
| [`SO-TAY-LOI.md`](./SO-TAY-LOI.md) | Mỗi lần lab lỗi → ghi lại ngay, đừng tin trí nhớ |
| [`assessment/`](./assessment/) | Đầu vào + kiểm tra cuối mỗi phase |
| [`templates/`](./templates/) | Mỗi khi bắt đầu lesson mới hoặc lab mới |
| [`cheatsheets/`](./cheatsheets/) | Lúc **đang lab**, cần tra nhanh — không phải lúc học |
| [`flashcards/`](./flashcards/) | 10 phút ôn mỗi ngày, lúc chờ / trước khi ngủ |

---

## 5. Lộ trình 10 phase

| Phase | Thư mục | Nội dung chính | Chứng chỉ |
|:---:|---|---|---|
| **0** | [`00-foundation/`](./00-foundation/) | OSI, TCP/IP, IPv4, **subnetting** ⭐, ARP, TCP/UDP, DNS/DHCP/NAT | CCNA |
| **1** | [`01-switching/`](./01-switching/) | VLAN, trunk 802.1Q, inter-VLAN, STP/RSTP, EtherChannel, port security | CCNA |
| **2** | [`02-routing/`](./02-routing/) | Static/default/floating, AD & metric, **OSPF** single → multi-area | CCNA |
| **3** | [`03-services/`](./03-services/) | DHCP, DNS, NAT/PAT, NTP, Syslog, SNMP, SSH, QoS cơ bản | CCNA |
| **4** | [`04-ipv6/`](./04-ipv6/) | Address types, SLAAC, DHCPv6, Neighbor Discovery, OSPFv3 | CCNA |
| **5** | [`05-wireless/`](./05-wireless/) | WLAN, AP/WLC, SSID, băng tần & kênh, WPA2/WPA3 | CCNA |
| **6** | [`06-security/`](./06-security/) | AAA, ACL std/ext, DHCP snooping, DAI, L2 attacks | CCNA |
| **7** | [`07-wan-vpn/`](./07-wan-vpn/) | WAN, GRE, IPsec, Site-to-Site VPN, SD-WAN concepts | CCNA |
| 🏁 | [`labs/`](./labs/) | **FINAL CCNA PROJECT** — network cho công ty 100–300 users | CCNA |
| **8** | [`08-ccnp/`](./08-ccnp/) | BGP, redistribution, route-map, FHRP, HA, design → *repo riêng* | CCNP |
| **9** | [`09-automation/`](./09-automation/) | REST/YAML, Python, Netmiko, Ansible, NETCONF → *repo riêng* | — |

Chi tiết từng mục + checkbox tiến độ: **[`ROADMAP.md`](./ROADMAP.md)**

> ✅ **Phase 0 → 7 đã viết đầy đủ: 41/41 lesson + 8 mini exam.**
> Mỗi phase kết thúc bằng `review-phaseNN.md` — tổng kết, bảng lỗi hay gặp,
> câu hỏi phỏng vấn, và **Mini Exam 20 câu** có ngưỡng 80% để qua phase.

---

## 6. Quy ước đặt tên file

Giữ repo sạch bằng 4 quy ước duy nhất:

| Loại | Mẫu tên | Ví dụ |
|---|---|---|
| Lesson | `<phase>/lesson-NN-ten-khong-dau.md` | `00-foundation/lesson-02-ipv4-va-subnetting.md` |
| Lab | `labs/labNN-ten-khong-dau.md` | `labs/lab11-vlan-va-trunk.md` |
| Flashcard | `flashcards/NN-ten-phase.md` | `flashcards/01-switching.md` |
| Cheatsheet | `cheatsheets/ten-chu-de.md` | `cheatsheets/subnetting.md` |

Quy tắc chung: **không dấu, chữ thường, nối bằng gạch ngang, số thứ tự 2 chữ số.**

Số LAB được cấp theo **dải riêng cho từng phase** (P0 `01–09`, P1 `10–19`, …) —
xem [`labs/README.md`](./labs/README.md#-quy-ước-đánh-số-lab).

### Kiểm tra repo còn nhất quán không

Sau mỗi buổi học, khi anh thêm lesson/lab mới:

```bash
python check.py
```

Script bắt 8 loại lỗi mà đọc bằng mắt rất khó thấy: link gãy, output quên dán nhãn,
số LAB trùng hoặc sai dải, số lesson lệch giữa ROADMAP/README/PROGRESS, bảng lệnh
hai nơi không khớp, assessment sai số câu, đặt tên file sai quy ước.
Thêm `-v` để xem cả những mục đã đạt.

---

## 7. Nguyên tắc tự học

1. **Hiểu *tại sao công nghệ này tồn tại* trước khi học cấu hình nó.**
   VLAN sinh ra để giải quyết vấn đề gì? Chưa trả lời được thì chưa nên gõ `switchport mode access`.

2. **Mỗi LAB bắt buộc có bước BREAK.** Phá rồi tự sửa. Không có BREAK = lab chưa xong.

3. **Phân biệt 3 tầng kiến thức** trong mọi topic:

   | Tầng | Nghĩa |
   |---|---|
   | 🎓 **Exam** | Cần để qua bài thi |
   | 🔧 **Engineer** | Cần để triển khai & vận hành thật |
   | 🏭 **Production** | Cái thực sự gãy trong doanh nghiệp |

4. **Output lab là của bạn.** AI không chạy được thiết bị — mọi `show` output AI đưa ra chỉ là
   *điển hình để minh hoạ*, và phải được dán nhãn. Số liệu thật chỉ đến từ lab của bạn.

5. **Không nhảy cóc.** Thiếu prerequisite thì quay lại học nền, kể cả khi thấy "mất thời gian".

6. **Ghi lỗi ngay khi gặp** vào [`SO-TAY-LOI.md`](./SO-TAY-LOI.md). Lỗi không ghi là lỗi sẽ gặp lại.

---

## 8. Môi trường lab

| Công cụ | Dùng cho | Ghi chú |
|---|---|---|
| **Cisco Packet Tracer** | Phase 0 → 6, phần lớn CCNA | Nhẹ nhất, miễn phí qua Cisco NetAcad. Ưu tiên cho người mới. |
| **GNS3 / EVE-NG / CML** | Phase 7+ (VPN/IPsec), NETCONF, nâng cao | Packet Tracer **không mô phỏng đủ** các phần này |
| **Wireshark** | Soi ARP, ICMP, DHCP, DNS, TCP handshake, VLAN tag, OSPF | Bắt buộc có — "nhìn thấy gói tin" là bước nhảy về hiểu biết. Hướng dẫn: [`cheatsheets/wireshark.md`](./cheatsheets/wireshark.md) |
| **Cisco DevNet Sandbox** | Thiết bị thật, miễn phí, qua mạng | Khi máy không đủ RAM dựng lab nặng |

Khai báo môi trường của bạn trong [`PROGRESS.md`](./PROGRESS.md) để AI đưa lab phù hợp.

---

## 9. Quan hệ với 2 repo anh em

Repo này **tập trung mảng CCNA (Phase 0 → 7)**. Hai phase cuối đã có repo riêng chuyên sâu hơn,
nên ở đây chỉ giữ roadmap + link, **không viết lại nội dung**:

| Phase | Repo chuyên sâu | Trạng thái |
|---|---|---|
| **8 — CCNP Enterprise** | [`CCNP-Encor`](https://github.com/hiepnguyen775/CCNP-Encor) | Phủ 100% blueprint ENCOR 350-401 |
| **9 — Network Automation** | [`Network-Automation`](https://github.com/hiepnguyen775/Network-Automation) | Zero → Production, Module 00–12 + Capstone |

Thứ tự khuyến nghị: **Network Mentor (Phase 0–7) → CCNP-Encor → Network-Automation.**

---

## 10. FAQ

<details>
<summary><b>Tôi đã biết chút networking rồi, có phải làm Assessment không?</b></summary>

<br>

Có. Assessment không phải để chấm điểm, mà để AI **biết chỗ nào bỏ qua được**. Người đã làm infra
thường mạnh phần IP/DNS/DHCP nhưng yếu STP, OSPF states, hoặc subnetting tốc độ. Bỏ 20 phút
để tiết kiệm vài tuần học sai chỗ.

</details>

<details>
<summary><b>AI quên mất tôi đang học tới đâu?</b></summary>

<br>

Đó chính là lý do có `PROGRESS.md`. Chat không có trí nhớ dài hạn — repo này **là** trí nhớ của nó.
Luôn dán kèm `PROGRESS.md` ở đầu phiên.

</details>

<details>
<summary><b>AI đưa ra output <code>show</code> — tin được không?</b></summary>

<br>

**Không, và nó phải tự khai báo điều đó.** Mọi output trong repo/chat phải có nhãn
`# output điển hình — tự verify trên lab của bạn`. Nếu AI đưa output mà không dán nhãn, hãy nhắc nó.
Con số thật chỉ đến từ thiết bị thật.

</details>

<details>
<summary><b>Bao lâu thì xong CCNA?</b></summary>

<br>

Với nền IT/hệ thống sẵn có và **8–10 giờ/tuần**: Phase 0–7 khoảng **17 tuần**, cộng **1–2 tuần**
cho Final CCNA Project → **tổng ~18–20 tuần**. Chi tiết từng phase ở [`ROADMAP.md`](./ROADMAP.md#-tổng-quan-thời-lượng).
Ai hứa 6 tuần là đang bán khoá học.

</details>

<details>
<summary><b>Có cần học thuộc lệnh không?</b></summary>

<br>

Không học thuộc — nhưng phải **gõ đủ nhiều lần để quen tay**. Khác nhau ở chỗ: thuộc lòng thì quên
sau 2 tuần; gõ trong lab 20 lần thì nhớ bằng phản xạ. Cheatsheet ở đây để tra *lúc đang lab*,
không phải để học thuộc.

</details>

<details>
<summary><b>Tôi lỡ bỏ học 3 tuần, quay lại thế nào?</b></summary>

<br>

Dán `MENTOR_PROMPT.md` + `PROGRESS.md` và gõ **`ôn`**. AI sẽ kéo lại các mục trong phần
*Điểm yếu cần ôn* trước, rồi mới đi tiếp. Đừng bỏ qua bước này — học tiếp trên nền đã quên
là cách nhanh nhất để tắc ở Phase 2.

</details>

---

<div align="center">

**Bắt đầu tại 👉 [`MENTOR_PROMPT.md`](./MENTOR_PROMPT.md)**

*Không học thuộc để thi — học để nhìn vào network và hiểu được nó.*

</div>
