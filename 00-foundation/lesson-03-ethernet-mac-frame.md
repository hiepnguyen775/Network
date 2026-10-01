# LESSON 03 — Ethernet · MAC Address · Frame · Switch học MAC thế nào

| | |
|---|---|
| **Phase** | 0 — Foundation |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 01](./lesson-01-osi-va-tcp-ip.md) |
| **Trạng thái** | ⬜ Chưa học |
| **Ngày hoàn thành** | — |

---

## 1. Mục tiêu

- [ ] Đọc được một MAC address và nói ra 6 byte đó nghĩa là gì
- [ ] Vẽ được cấu trúc frame Ethernet và nói từng field để làm gì
- [ ] Giải thích được **switch học MAC bằng cách nào** — và học từ field nào
- [ ] Nói được switch làm gì khi **không biết** destination MAC
- [ ] Nhận ra dấu hiệu của loop L2 chỉ từ bảng MAC

## 2. Prerequisite

- L2 = Data Link, PDU là **frame** *(Lesson 01)*
- MAC chỉ có ý nghĩa trong một đoạn mạng, đổi ở mỗi hop *(Lesson 01 §6)*

---

## 3. Concept

### Ethernet là gì

**Ethernet** là bộ chuẩn (IEEE 802.3) quy định cách các thiết bị trong một mạng LAN gửi dữ liệu
cho nhau trên cùng một môi trường truyền: đóng gói ra sao, địa chỉ thế nào, xử lý va chạm ra sao.

Nó thống trị LAN gần như tuyệt đối. Token Ring, FDDI từng cạnh tranh — đều chết.

### MAC Address — 48 bit, 6 byte

```text
00:1A:2B:3C:4D:5E
└────┬────┘ └───┬───┘
   OUI        Serial
 3 byte đầu   3 byte sau
 "hãng nào"   "con số thứ mấy"
```

| Phần | Dài | Ý nghĩa |
|---|:---:|---|
| **OUI** (Organizationally Unique Identifier) | 3 byte | IEEE cấp cho từng hãng. `00:50:56` = VMware, `00:0C:29` = VMware, `FC:FB:FB` = Cisco |
| **Serial** | 3 byte | Hãng tự đánh số từng card |

Cách viết khác nhau tuỳ nền tảng — **cùng một địa chỉ**:

```text
00:1A:2B:3C:4D:5E      Linux, Wireshark
00-1A-2B-3C-4D-5E      Windows
001a.2b3c.4d5e         Cisco IOS   ← nhóm 4 ký tự, dấu chấm
```

### Hai MAC đặc biệt

| MAC | Tên | Nghĩa |
|---|---|---|
| `FF:FF:FF:FF:FF:FF` | **Broadcast** | Gửi cho **mọi** thiết bị trong broadcast domain |
| Bit thấp nhất của byte đầu = 1 | **Multicast** | Gửi cho một nhóm. VD `01:00:5E:...` = IPv4 multicast |

### Frame Ethernet II — cấu trúc

```text
┌──────────┬──────────┬───────────┬──────────────────┬───────┐
│ Dst MAC  │ Src MAC  │ EtherType │     Payload      │  FCS  │
│  6 byte  │  6 byte  │  2 byte   │  46 – 1500 byte  │ 4 byte│
└──────────┴──────────┴───────────┴──────────────────┴───────┘
```

| Field | Dài | Để làm gì |
|---|:---:|---|
| **Destination MAC** | 6 B | Ai nhận — switch đọc field này để quyết định chuyển đi đâu |
| **Source MAC** | 6 B | Ai gửi — **switch học từ field này** ⭐ |
| **EtherType** | 2 B | Payload là gì: `0x0800` = IPv4, `0x0806` = ARP, `0x86DD` = IPv6, `0x8100` = có tag VLAN |
| **Payload** | 46–1500 B | Dữ liệu thật — thường là một IP packet |
| **FCS** | 4 B | Checksum. Sai → frame bị **drop im lặng**, không báo lỗi lên trên |

> 📏 **MTU 1500** chính là giới hạn payload này. Gói IP lớn hơn phải phân mảnh.
> Nhớ con số 1500 — nó quay lại ám ảnh bạn ở Phase 7 (VPN/tunnel).

> ⚠️ **Destination đứng TRƯỚC source.** Lý do rất thực tế: switch chỉ cần đọc 6 byte đầu
> là đã biết chuyển đi đâu, không cần đợi hết frame. Đây là nền của *cut-through switching*.

---

## 4. Why? — tại sao cần MAC khi đã có IP

> **Nếu bỏ MAC, chỉ dùng IP thì sao?**

| Vấn đề | Giải thích |
|---|---|
| **IP có thể đổi, MAC thì không** | Máy nhận DHCP hôm nay `.10`, mai `.20`. MAC gắn cứng vào card. Lớp dưới cần một định danh ổn định. |
| **IP là địa chỉ logic, MAC là địa chỉ vật lý** | IP nói *"máy đó ở mạng nào"*. MAC nói *"card nào trên dây này"*. Hai câu hỏi khác nhau. |
| **Không phải mọi thứ đều chạy IP** | Ethernet còn chở ARP, IPv6, PPPoE, STP... EtherType tồn tại chính vì vậy. |
| **Switch phải quyết định rất nhanh** | Tra MAC table bằng ASIC ở wire-speed. Nếu phải mở IP header ra đọc thì chậm hơn nhiều. |

Cách nhớ:

> **IP trả lời "đi tới đâu" (toàn hành trình). MAC trả lời "đưa cho ai bây giờ" (một chặng).**

---

## 5. How does it work? — Switch học MAC

Switch khi mới bật có **MAC table rỗng**. Nó học dần qua 3 hành vi:

### Ba hành vi của switch

| Hành vi | Khi nào | Switch làm gì |
|---|---|---|
| **Learning** | Mọi frame đi vào | Đọc **source MAC**, ghi `(MAC, port, VLAN)` vào bảng |
| **Forwarding** | Biết destination MAC | Chuyển **đúng một port** |
| **Flooding** | Không biết destination MAC, hoặc là broadcast/multicast | Gửi ra **mọi port cùng VLAN**, trừ port nhận |

### Diễn biến từng bước

```text
Topology:   PC-A (Fa0/1)  ──  SW1  ──  (Fa0/2) PC-B

Bước 1 — PC-A gửi frame đầu tiên cho PC-B
  SW1 đọc SOURCE MAC = MAC-A, đi vào Fa0/1
  → HỌC:  MAC-A → Fa0/1
  SW1 tra DESTINATION MAC = MAC-B → chưa có trong bảng
  → FLOOD ra mọi port trừ Fa0/1

Bước 2 — PC-B trả lời
  SW1 đọc SOURCE MAC = MAC-B, đi vào Fa0/2
  → HỌC:  MAC-B → Fa0/2
  SW1 tra DESTINATION = MAC-A → ĐÃ BIẾT ở Fa0/1
  → FORWARD đúng một port

Từ đây trở đi: mọi frame A↔B đi thẳng, không flood nữa.
```

> 🔑 **Điểm mấu chốt dễ nhầm:** switch học từ **source MAC**, nhưng chuyển dựa trên
> **destination MAC**. Nó chỉ biết một máy tồn tại **sau khi máy đó đã nói**.
> Máy im lặng hoàn toàn thì switch không bao giờ biết — mọi frame gửi tới nó đều bị flood.

### Aging — bảng tự dọn

Mỗi entry có timer **mặc định 300 giây** (5 phút). Mỗi lần thấy lại MAC đó, timer reset.
Hết giờ không thấy → xoá entry.

Vì sao cần: máy được chuyển sang port khác, hoặc rút đi, bảng phải tự sửa.

---

## 6. Packet Flow

PC-A `192.168.1.10` ping PC-B `192.168.1.20` — **cùng subnet**, qua một switch.

| # | Frame | Dst MAC | Src MAC | EtherType | Ghi chú |
|:---:|---|---|---|---|---|
| 1 | ARP Request | `FF:FF:FF:FF:FF:FF` | MAC-A | `0x0806` | Broadcast — "ai có .20?" |
| 2 | ARP Reply | MAC-A | MAC-B | `0x0806` | **Unicast** — chỉ trả lời người hỏi |
| 3 | ICMP Echo Request | MAC-B | MAC-A | `0x0800` | Giờ mới gửi được ping |
| 4 | ICMP Echo Reply | MAC-A | MAC-B | `0x0800` | |

**So sánh với Lesson 01 (khác subnet):** ở đó PC-A ARP tìm MAC của **gateway**, và MAC bị
router viết lại ở mỗi hop. Ở đây **không có router**, nên MAC giữ nguyên suốt đường.

> 💡 Đây là cách phân biệt nhanh *switching* và *routing*:
> **switch không bao giờ sửa frame header; router luôn tạo frame header mới.**

---

## 7. Real-world Example

🏭 Một tình huống thật trong phòng server:

> *"Hai máy ảo trên cùng host Proxmox ping nhau rất nhanh, nhưng ping ra switch vật lý thì chậm."*

Giải thích bằng kiến thức lesson này: traffic giữa 2 VM cùng host **không ra khỏi host** —
vSwitch của hypervisor xử lý ở RAM, học MAC đúng như switch vật lý nhưng không có dây.
Ra switch vật lý mới có độ trễ của cáp + xử lý ASIC.

🏭 Một tình huống khác — **MAC flapping**:

```text
# output điển hình — tự verify trên lab của bạn
%SW_MATM-4-MACFLAP_NOTIF: Host 001a.2b3c.4d5e in vlan 10 is flapping between port Gi0/1 and port Gi0/2
```

Switch thấy **cùng một MAC** lúc ở port này, lúc ở port kia. Gần như luôn là:
**có loop L2**, hoặc ai đó cắm hai đầu dây vào cùng một switch.

---

## 8. Cisco CLI

```cisco
! Xem bảng MAC
SW1# show mac address-table

! Xem MAC của một VLAN
SW1# show mac address-table vlan 10

! Tìm một MAC cụ thể
SW1# show mac address-table address 001a.2b3c.4d5e

! Đổi thời gian aging (mặc định 300 giây)
SW1(config)# mac address-table aging-time 600

! Gán cứng một MAC vào port (static entry)
SW1(config)# mac address-table static 001a.2b3c.4d5e vlan 10 interface Gi0/5

! Xoá bảng để học lại từ đầu — rất hay dùng khi debug
SW1# clear mac address-table dynamic
```

| Lệnh | Kiểm tra gì | Khác biệt platform |
|---|---|---|
| `show mac address-table` | Switch đã học được gì | IOS/IOS-XE giống nhau; **NX-OS**: `show mac address-table` cũng dùng được |
| `clear mac address-table dynamic` | Ép học lại | Dùng khi nghi bảng bị sai sau khi đổi dây |
| `mac address-table static` | Cố định một MAC vào port | Ít dùng; thường thay bằng Port Security |

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show mac address-table
          Mac Address Table
-------------------------------------------
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
  10    001a.2b3c.4d5e    DYNAMIC     Fa0/1
  10    001a.2b3c.4d6f    DYNAMIC     Fa0/2
  10    0050.56aa.bb01    DYNAMIC     Gi0/1
  20    0050.56aa.bb02    STATIC      Gi0/1
Total Mac Addresses for this criterion: 4
```

**Đọc gì trong output này:**

| Cột | Ý nghĩa | Bất thường trông như thế nào |
|---|---|---|
| `Vlan` | MAC này thuộc VLAN nào | Cùng MAC ở 2 VLAN là bình thường; tra cứu theo cặp `(VLAN, MAC)` |
| `Mac Address` | Định dạng Cisco `xxxx.xxxx.xxxx` | 3 ký tự đầu tra được hãng |
| `Type` | `DYNAMIC` = tự học · `STATIC` = gán tay | `STATIC` mà bạn không gán → ai đó đã cấu hình |
| `Ports` | Học được ở port nào | **Nhiều MAC trên một port** = port đó là uplink/trunk, hoặc có switch khác cắm vào |
| Tổng số | Số entry | Tăng vọt bất thường → nghi **MAC flooding attack** |

> 🔧 Mẹo thực chiến: muốn biết **máy X đang cắm ở port nào**, lấy MAC của nó rồi
> `show mac address-table address <mac>`. Đây là cách nhanh nhất lần ra vị trí vật lý của một máy.

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| Switch không học được MAC của một máy | Port down, sai VLAN, máy chưa gửi gì | `show interfaces status`, `show vlan brief` | Kiểm tra cáp, gán đúng VLAN |
| Một MAC nhảy qua lại 2 port | **Loop L2** hoặc cắm nhầm | `show mac address-table`, log `MACFLAP` | Tìm và rút dây thừa; kiểm tra STP |
| Bảng MAC đầy bất thường, mạng chậm | **MAC flooding attack** | `show mac address-table count` | Bật **Port Security** *(Lesson 17)* |
| Đổi dây xong máy vẫn không thông | Bảng còn entry cũ, chưa hết aging | `clear mac address-table dynamic` | Xoá bảng, hoặc đợi 300 giây |
| Mọi frame đều bị flood | Switch hoạt động như hub — bảng bị xoá liên tục | `show mac address-table count` | Nghi loop hoặc tấn công |

---

## 11. LAB

🧪 **LAB 02 — Bắt ARP + ICMP bằng Wireshark** *(cũng dùng cho Lesson 05)*

Phần của lesson này: trong Packet Tracer, dựng 1 switch + 3 PC cùng VLAN. Quan sát
`show mac address-table` **trước và sau** khi ping. Chứng minh:

1. Bảng rỗng trước khi có traffic
2. Sau ping đầu tiên, có đủ 2 entry
3. `clear mac address-table dynamic` làm bảng rỗng lại

## 12. Challenge

> Tự trả lời trước khi mở đáp án.

1. PC-A gửi frame tới một MAC **chưa từng xuất hiện** trong mạng. Switch làm gì?
   Nếu không ai trả lời thì entry đó có vào bảng MAC không?
2. Switch có **3 port**, cắm PC-A, PC-B và một switch khác (SW2) có 10 PC phía sau.
   Sau một lúc, bảng MAC của SW1 có bao nhiêu entry? Phân bố trên mấy port?
3. Vì sao frame tối thiểu là **64 byte** (payload tối thiểu 46)? Nếu dữ liệu chỉ có 10 byte thì sao?

<details>
<summary>Đáp án</summary>

**1.** Switch **flood** ra mọi port cùng VLAN trừ port nhận. Nếu không ai trả lời →
**không có entry nào được thêm cho MAC đích đó**, vì switch chỉ học từ **source MAC** của
frame đi vào. Nó không học từ destination. Mỗi lần A gửi cho MAC đó đều sẽ flood lại.

**2.** Khoảng **12 entry**: MAC-A ở port 1, MAC-B ở port 2, và **cả 10 MAC phía sau SW2 đều
nằm trên cùng port 3**. Đây là dấu hiệu nhận biết port uplink: nhiều MAC chung một port.

**3.** 64 byte là do cơ chế **phát hiện va chạm (CSMA/CD)** thời Ethernet dùng chung môi trường:
frame phải đủ dài để máy gửi vẫn đang truyền khi va chạm vọng về. Dữ liệu ngắn hơn 46 byte
sẽ được **padding** thêm số 0 cho đủ. Ngày nay full-duplex không còn va chạm, nhưng kích thước
tối thiểu vẫn giữ để tương thích.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | 5 field của frame Ethernet · MAC bao nhiêu byte · EtherType của IPv4/ARP · aging time | ⬜ |
| **L2** Explain | Giải thích 3 hành vi learning/forwarding/flooding cho người mới | ⬜ |
| **L3** Configure | Xem MAC table, thêm static entry, xoá bảng động | ⬜ |
| **L4** Troubleshoot | Cho log MACFLAP → nêu 2 nguyên nhân và cách xác minh | ⬜ |
| **L5** Design | Nhìn `show mac address-table` của switch lạ → vẽ lại topology | ⬜ |

## 14. Summary

**Key concepts**

- MAC = 48 bit = 6 byte: 3 byte OUI (hãng) + 3 byte serial
- Frame Ethernet II: `Dst MAC | Src MAC | EtherType | Payload | FCS`
- **Switch học từ SOURCE MAC, chuyển theo DESTINATION MAC** ⭐
- Không biết đích → **flood** ra mọi port cùng VLAN trừ port nhận
- Aging mặc định **300 giây**
- MAC table tra cứu theo cặp `(VLAN, MAC)`

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show mac address-table` | Switch đã học được gì, máy nào ở port nào |
| `show mac address-table address <mac>` | Tìm máy X đang cắm ở port nào |
| `clear mac address-table dynamic` | Ép học lại sau khi đổi dây |

**Common mistakes**

| Sai | Đúng |
|---|---|
| "Switch học từ destination MAC" | Học từ **source** |
| "Switch biết mọi máy trong mạng" | Chỉ biết máy **đã từng gửi gì đó** |
| "Nhiều MAC trên 1 port là lỗi" | Bình thường — đó là **uplink/trunk** |
| Quên rằng FCS sai thì frame bị drop **im lặng** | Không có thông báo lỗi nào lên tầng trên |

## 15. Homework + cập nhật PROGRESS

1. Trên máy bạn: `ipconfig /all` (Windows) hoặc `ip link` (Linux) — tìm MAC của card mạng,
   tra 3 byte đầu xem là hãng nào.
2. `arp -a` — liệt kê các MAC máy bạn đang biết. Giải thích vì sao có MAC của gateway.
3. Trong Packet Tracer: dựng 1 switch + 3 PC, chứng minh đủ 3 điều ở mục LAB.

```markdown
- [YYYY-MM-DD] Lesson 03 — Ethernet & MAC: DONE | cần ôn lại <điểm yếu của bạn>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | Cấu trúc frame, MAC 48 bit, learning/forwarding/flooding, EtherType |
| 🔧 **Engineer** | Dùng MAC table để lần ra vị trí vật lý của máy; nhận ra port uplink |
| 🏭 **Production** | MAC flapping = loop; bảng MAC đầy = nghi tấn công; đổi dây xong nhớ `clear` |

### 🔗 Liên kết

- ⬅️ [Lesson 02 — IPv4 & Subnetting](./lesson-02-ipv4-va-subnetting.md)
- ➡️ [Lesson 04 — Unicast / Broadcast / Multicast](./lesson-04-unicast-broadcast-multicast.md)
- 🔧 [`cheatsheets/show-commands.md`](../cheatsheets/show-commands.md#2-layer-2--switching)
- 🃏 [`flashcards/00-foundation.md`](../flashcards/00-foundation.md)
