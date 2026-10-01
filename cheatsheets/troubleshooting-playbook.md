# 🧭 Troubleshooting Playbook

> Quy tắc duy nhất: **không đoán mò.**
> Mỗi lệnh phải kiểm chứng **một giả thuyết cụ thể**. Nói giả thuyết ra trước khi gõ.

---

## 1. Thứ tự tầng — xương sống của mọi buổi debug

```
Physical → Interface → VLAN → IP → ARP → MAC table → Routing table → ACL → NAT → Application
```

Đi **từ dưới lên**. Người mới hay nhảy thẳng lên Application ("chắc server lỗi") và mất hàng giờ.

---

## 2. Quy trình 6 bước

| Bước | Làm gì | Câu hỏi tự đặt |
|:---:|---|---|
| 1 | **Xác định triệu chứng chính xác** | Ai không vào được cái gì? Từ bao giờ? Có bao giờ chạy chưa? |
| 2 | **Khoanh vùng** | Một máy hay cả VLAN? Một dịch vụ hay tất cả? Một chiều hay hai chiều? |
| 3 | **Đặt giả thuyết** | Nếu nguyên nhân là X, tôi sẽ thấy gì? |
| 4 | **Kiểm chứng bằng 1 lệnh** | Lệnh này loại trừ được giả thuyết nào? |
| 5 | **Sửa một thứ tại một thời điểm** | Sửa 3 thứ cùng lúc = không biết cái nào có tác dụng |
| 6 | **Ghi lại** | → [`SO-TAY-LOI.md`](../SO-TAY-LOI.md) |

> ⚠️ Bước 2 là bước tiết kiệm nhiều thời gian nhất và hay bị bỏ qua nhất.
> *"Một máy hỏng"* và *"cả VLAN hỏng"* dẫn tới hai hướng điều tra hoàn toàn khác nhau.

---

## 3. Cây quyết định: "PC1 không ping được PC2"

```text
PC1 ping chính nó (127.0.0.1)?
├─ FAIL → TCP/IP stack hỏng trên PC1 (hiếm) → kiểm tra driver/OS
└─ OK
   │
   PC1 ping IP của chính nó?
   ├─ FAIL → NIC chưa có IP, hoặc nhận APIPA 169.254.x.x → DHCP hỏng
   └─ OK
      │
      PC1 ping default gateway?
      ├─ FAIL → vấn đề trong CÙNG subnet:
      │         · cáp / port down?         show interfaces status
      │         · port đúng VLAN chưa?     show vlan brief
      │         · subnet mask hai bên?     ipconfig / show run int
      │         · ARP có resolve không?    arp -a / show ip arp
      └─ OK
         │
         PC1 ping PC2 (khác subnet)?
         ├─ FAIL → vấn đề ĐỊNH TUYẾN hoặc LỌC:
         │         · router có route đi?    show ip route
         │         · router có route VỀ?    (kiểm tra ở router đầu kia!)
         │         · ACL chặn?              show access-lists
         │         · NAT dịch sai?          show ip nat translations
         │         · default gateway PC2?   ipconfig trên PC2
         └─ OK → vấn đề ở tầng ứng dụng, không phải network
                  · DNS?        nslookup
                  · port?       telnet <ip> <port>
                  · firewall host? tắt thử tạm
```

> 🔑 **Ping được 1 chiều, fail chiều kia** → gần như luôn là **thiếu route chiều về**
> hoặc **ACL một chiều**. Phải kiểm tra routing table ở **cả hai đầu**.

---

## 4. Bảng triệu chứng → nghi ngờ đầu tiên

### Layer 1–2

| Triệu chứng | Nghi ngờ đầu tiên | Lệnh |
|---|---|---|
| Interface `down/down` | Cáp, đầu kia shutdown | `show interfaces status` |
| Interface `up/down` | Lệch encapsulation, clock rate (serial) | `show interfaces <int>` |
| Interface `err-disabled` | Port security violation, BPDU guard | `show interfaces status err-disabled` |
| Trunk không lên | Hai đầu khác mode, VLAN không allowed | `show interfaces trunk` |
| Ping chập chờn | Native VLAN mismatch, STP đang hội tụ | `show interfaces trunk`, `show spanning-tree` |
| Cả mạng chậm/treo | **Loop L2 — broadcast storm** | `show spanning-tree`, nhìn đèn port |
| MAC nhảy port liên tục | Có loop, hoặc cắm nhầm | `show mac address-table` |

### Layer 3

| Triệu chứng | Nghi ngờ đầu tiên | Lệnh |
|---|---|---|
| Ping gateway OK, ping xa fail | Thiếu route **chiều về** | `show ip route` ở **cả 2 đầu** |
| Ping IP OK, ping tên fail | DNS | `nslookup`, `show hosts` |
| Route biến mất | Interface down, hoặc route AD thấp hơn thắng | `show ip route`, `show ip protocols` |
| OSPF không lên neighbor | Area / subnet / timer / MTU / auth lệch | xem §5 |
| OSPF lên nhưng không có route | `network` statement sai wildcard, passive-interface | `show ip protocols` |
| Ping được 1 chiều | ACL, hoặc NAT thiếu chiều | `show access-lists`, `show ip nat translations` |
| Web không load nhưng ping OK | **MTU / MSS** qua tunnel | `ping <ip> size 1500 df-bit` |

### Services

| Triệu chứng | Nghi ngờ đầu tiên | Lệnh |
|---|---|---|
| Máy nhận IP `169.254.x.x` | DHCP không tới được | `show ip dhcp pool`, kiểm tra `ip helper-address` |
| DHCP cấp IP trùng với server | Quên `ip dhcp excluded-address` | `show running-config \| include excluded` |
| NAT không dịch | Sai `ip nat inside` / `outside`, ACL không match | `show ip nat statistics` |
| Không SSH được vào thiết bị | Thiếu RSA key, `transport input`, hoặc ACL chặn | `show ip ssh`, `show line vty 0 4` |
| Log sai thời gian | NTP chưa sync | `show ntp status`, `show clock` |

---

## 5. OSPF không lên neighbor — thứ tự kiểm tra

Học thuộc thứ tự này, nó tiết kiệm hàng giờ:

| # | Kiểm tra | Lệnh |
|:---:|---|---|
| 1 | Interface `up/up`? | `show ip interface brief` |
| 2 | Hai đầu **cùng subnet**? | `show running-config interface <int>` |
| 3 | **Area** có khớp? | `show ip ospf interface <int>` |
| 4 | **Hello / Dead timer** khớp? | `show ip ospf interface <int>` |
| 5 | **MTU** hai đầu khớp? | `show interfaces <int>` |
| 6 | **Authentication** khớp? | `show ip ospf interface <int>` |
| 7 | Interface có bị **passive**? | `show ip protocols` |
| 8 | **Router ID trùng nhau**? | `show ip ospf` |
| 9 | **Network type** khớp (broadcast/P2P)? | `show ip ospf interface <int>` |

> Neighbor kẹt ở `EXSTART`/`EXCHANGE` → gần như luôn là **MTU mismatch**.
> Kẹt ở `INIT` → một chiều không nhận được hello (ACL? passive?).

---

## 6. Những thứ kiểm tra trước khi đổ lỗi cho network

| Kiểm tra | Vì sao |
|---|---|
| Cáp có cắm đúng port không | Lỗi phổ biến nhất, và xấu hổ nhất khi phát hiện sau 2 tiếng |
| Firewall trên chính máy tính | Windows Firewall chặn ICMP mặc định ở nhiều profile |
| `copy run start` đã chạy chưa | "Tự nhiên mất cấu hình" = quên lưu + reload |
| Đồng hồ thiết bị | Sai giờ → chứng chỉ lỗi, log không correlate được |
| Có ai vừa đổi gì không | Sự cố xuất hiện ngay sau một thay đổi thì hãy bắt đầu từ đó |

---

## 7. Mẫu ghi nhận sự cố

Copy mẫu này mỗi khi debug — nó ép bạn suy nghĩ có cấu trúc:

```markdown
## Sự cố: <một câu>
- **Thời điểm bắt đầu:**
- **Phạm vi ảnh hưởng:** (1 máy / 1 VLAN / toàn site)
- **Thay đổi gần nhất trước đó:**

### Giả thuyết đã kiểm tra
| # | Giả thuyết | Lệnh kiểm chứng | Kết quả | Loại trừ? |
|---|---|---|---|---|
| 1 | | | | |

### Nguyên nhân gốc
### Cách sửa
### Cách phòng ngừa lần sau
```
