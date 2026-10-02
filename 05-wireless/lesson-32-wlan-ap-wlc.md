# LESSON 32 — WLAN · AP · WLC · Kiến trúc Wi-Fi

| | |
|---|---|
| **Phase** | 5 — Wireless |
| **Thời lượng** | ~2 giờ |
| **Prerequisite** | [Lesson 13](../01-switching/lesson-13-vlan-va-trunk.md), [Lesson 04](../00-foundation/lesson-04-unicast-broadcast-multicast.md) |
| **Trạng thái** | ⬜ Chưa học |

---

## 1. Mục tiêu

- [ ] Phân biệt SSID · BSSID · ESS · BSS — bốn khái niệm hay bị nhầm
- [ ] Giải thích kiến trúc **autonomous** vs **lightweight + WLC**
- [ ] Mô tả **CAPWAP** và hai tunnel của nó
- [ ] Biết AP cần gì từ switch: VLAN, trunk hay access, PoE
- [ ] Phân biệt **local mode** và **FlexConnect**, biết khi nào dùng cái nào

## 2. Prerequisite

- VLAN, trunk, access port *(Lesson 13)*
- Broadcast domain *(Lesson 04)*
- PoE budget *(Lesson 11)*

---

## 3. Concept

### Wi-Fi về bản chất là gì

**802.11 là một công nghệ Layer 2** — nó thay thế dây Ethernet bằng sóng vô tuyến.
Từ L3 trở lên, mọi thứ **giống hệt** mạng có dây.

| | Ethernet có dây | Wi-Fi (802.11) |
|---|---|---|
| Môi trường truyền | Cáp — **riêng cho từng máy** | Sóng — **DÙNG CHUNG** |
| Song công | **Full-duplex** | **Half-duplex** — không thể vừa gửi vừa nhận |
| Chống va chạm | CSMA/CD *(phát hiện)* | **CSMA/CA** *(né tránh)* |
| Bảo mật vật lý | Phải cắm dây | **Ai trong tầm sóng cũng nghe được** |

> ⭐ Hai hệ quả quan trọng:
> 1. **Wi-Fi luôn half-duplex và dùng chung môi trường** → băng thông *thực tế* chỉ
>    khoảng **50–60%** con số quảng cáo, và **chia cho mọi client** trên cùng kênh.
> 2. **Sóng đi khắp nơi** → bảo mật phải làm bằng mã hoá, không thể dựa vào vị trí vật lý.

### Bốn khái niệm phải phân biệt

| Khái niệm | Là gì | Ví dụ |
|---|---|---|
| **SSID** | **Tên** mạng Wi-Fi mà người dùng thấy | `CTY-NHANVIEN` |
| **BSSID** | **MAC của radio AP** phát SSID đó | `00:1a:2b:3c:4d:50` |
| **BSS** | Một AP + các client của nó | Vùng phủ của một AP |
| **ESS** | **Nhiều AP cùng SSID**, client roam được giữa chúng | Cả toà nhà |

```text
SSID "CTY-NHANVIEN"  ──┬── AP1  BSSID 00:1a:2b:3c:4d:50  (tầng 1)
   (một tên)           ├── AP2  BSSID 00:1a:2b:3c:4e:60  (tầng 2)
                       └── AP3  BSSID 00:1a:2b:3c:4f:70  (tầng 3)
                       └──────── ESS ────────────────────┘
```

> 💡 **Một AP có nhiều BSSID** — mỗi SSID × mỗi băng tần = một BSSID riêng.
> AP phát 3 SSID trên cả 2.4 và 5 GHz → **6 BSSID**.

> 🔧 Đây là lý do nên **giới hạn số SSID**: mỗi SSID tốn beacon riêng (gửi ~10 lần/giây),
> ăn vào thời gian phát sóng. **Quá 3–4 SSID là lãng phí rõ rệt.**

### Hai kiến trúc

| | **Autonomous AP** | **Lightweight AP + WLC** |
|---|---|---|
| Cấu hình ở đâu | **Từng AP một** | **Tập trung tại WLC** |
| AP tự xử lý | Mọi thứ | Chỉ radio *(ở local mode)* |
| Thêm AP mới | Cấu hình tay | **Cắm vào là tự join WLC** |
| Roaming | Kém — client phải xác thực lại | **Mượt** — WLC điều phối |
| Quản lý RF | Không | **RRM** — tự chỉnh kênh và công suất |
| Phù hợp | 1–3 AP, quán cà phê | ⭐ **Doanh nghiệp** |

> 🏭 Thực tế: trên ~5 AP là nên dùng WLC. Dưới đó, autonomous hoặc
> "cloud-managed" (Meraki, Aruba Instant) đơn giản hơn.

### CAPWAP — giao thức giữa AP và WLC

**CAPWAP** (Control And Provisioning of Wireless Access Points) tạo **hai tunnel** giữa
mỗi AP và WLC:

| Tunnel | Port | Chở gì |
|---|:---:|---|
| **Control** | **UDP 5246** | Cấu hình, quản lý, trạng thái — **luôn mã hoá (DTLS)** |
| **Data** | **UDP 5247** | **Traffic của người dùng** — mã hoá tuỳ chọn |

```text
Client ──802.11──▶ AP ══CAPWAP tunnel══▶ WLC ──▶ mạng có dây
                        (qua hạ tầng
                         có dây)
```

> ⭐ **Điểm gây bất ngờ nhất:** ở **local mode**, **toàn bộ** traffic người dùng
> đi qua tunnel CAPWAP **về tận WLC** rồi mới ra mạng — kể cả khi hai client
> ngồi cạnh nhau cùng một AP!
>
> Hệ quả: WLC trở thành **nút cổ chai** và là **điểm chết đơn lẻ** nếu không có HA.

### Local mode vs FlexConnect

| | **Local mode** | **FlexConnect** |
|---|---|---|
| Traffic người dùng | **Về WLC** qua CAPWAP | **Xuống thẳng** switch tại chỗ |
| Dùng ở đâu | Cùng site với WLC | **Chi nhánh** — WLC ở trụ sở |
| Mất liên lạc WLC | AP ngừng phục vụ | AP **vẫn chạy** *(standalone)* |
| Băng thông WAN | Tốn nhiều | Tiết kiệm |
| Chính sách tập trung | ✅ Tối đa | ⚠️ Hạn chế hơn |

> 🏭 Quy tắc: **AP cùng site với WLC → local mode. AP ở chi nhánh qua WAN → FlexConnect.**
> Dùng local mode cho chi nhánh nghĩa là mọi traffic Wi-Fi của chi nhánh phải chạy
> qua WAN về trụ sở rồi quay lại — lãng phí và chậm.

### AP cần gì từ switch

| Yêu cầu | Chi tiết |
|---|---|
| **PoE** | AP Wi-Fi 6 thường cần **PoE+ (30W)**, một số cần **PoE++ (60W)** |
| **Port mode** | **Local mode** → access port (VLAN management)<br>**FlexConnect** → **trunk** (chở nhiều VLAN SSID) |
| **VLAN** | AP cần một VLAN quản trị để nói chuyện với WLC |
| **Băng thông uplink** | AP Wi-Fi 6 có thể vượt 1 Gbps → cần **multi-gig** uplink |

> ⚠️ Lỗi hay gặp: cấu hình port AP là **trunk** khi dùng **local mode**.
> Không sai nghiêm trọng nhưng không cần thiết — ở local mode mọi VLAN đã đi
> trong tunnel CAPWAP rồi.

---

## 4. Why?

> **Vì sao Wi-Fi doanh nghiệp cần WLC, không chỉ cắm vài AP?**

| Vấn đề khi không có WLC | WLC giải quyết |
|---|---|
| 30 AP = 30 lần cấu hình, dễ lệch | **Một chỗ** cấu hình, đẩy xuống tất cả |
| Các AP tự chọn kênh → đè nhau | **RRM** tự phân kênh và công suất |
| Roaming đứt kết nối | WLC điều phối, giữ session |
| Không biết AP nào quá tải | Dashboard tập trung, thống kê client |
| Không phát hiện được rogue AP | **Rogue detection** tự động |
| Thêm AP mới phải cấu hình tay | **Zero-touch** — cắm vào là chạy |

> **Vì sao Wi-Fi luôn chậm hơn con số quảng cáo?**

| Lý do | Chi tiết |
|---|---|
| **Half-duplex** | Không thể vừa gửi vừa nhận |
| **CSMA/CA overhead** | Phải "xin phép" trước khi phát |
| **Dùng chung** | 20 client cùng AP → chia nhau băng thông |
| **Tốc độ quảng cáo là tốc độ vật lý** | Throughput thực tế ~50–60% |
| Client xa AP → tốc độ tự giảm | Một client yếu **kéo chậm cả nhóm** |

> 🔑 Hiện tượng cuối gọi là **"slow client problem"**: một máy ở xa truyền ở 6 Mbps
> chiếm thời gian phát sóng lâu hơn nhiều so với máy gần truyền ở 400 Mbps.
> Giải pháp: đặt **minimum data rate**, loại bỏ tốc độ thấp.

---

## 5. How does it work? — AP join WLC

```text
1. AP được cấp nguồn (PoE), nhận IP qua DHCP
2. AP TÌM WLC bằng một trong các cách:
   ├─ DHCP Option 43  (phổ biến nhất)
   ├─ DNS: phân giải CISCO-CAPWAP-CONTROLLER.<domain>
   ├─ Broadcast trong cùng subnet
   └─ Đã lưu địa chỉ WLC từ lần trước
3. AP gửi CAPWAP Discovery Request
4. WLC trả Discovery Response
5. AP chọn WLC, thiết lập DTLS cho tunnel control (UDP 5246)
6. AP JOIN — WLC kiểm tra, có thể đẩy firmware mới (AP reboot)
7. WLC đẩy cấu hình: SSID, kênh, công suất, chính sách
8. AP bắt đầu phát sóng
```

> ⚠️ **DHCP Option 43** là cách phổ biến nhất và cũng là **chỗ hay hỏng nhất**.
> Nó mã hoá địa chỉ WLC ở dạng hex — gõ sai một ký tự là AP không join được,
> và thông báo lỗi rất khó hiểu.

---

## 6. Packet Flow — client vào mạng qua Wi-Fi

```text
1. AP gửi BEACON (~10 lần/giây) quảng bá SSID
2. Client gửi PROBE REQUEST  → AP trả PROBE RESPONSE
3. AUTHENTICATION (802.11 — chỉ là bước hình thức ở WPA2/3)
4. ASSOCIATION — client gắn vào BSSID cụ thể
5. XÁC THỰC THẬT:
   ├─ WPA2-PSK      → 4-way handshake với passphrase
   └─ WPA2-Enterprise → 802.1X/EAP với RADIUS server
6. Client có khoá mã hoá → bắt đầu truyền dữ liệu
7. DHCP → client nhận IP (giống hệt mạng có dây)
8. Traffic đi qua CAPWAP tunnel về WLC (local mode)
```

> 🔑 Bước 3 và 5 khác nhau: **"Authentication" ở bước 3 là di sản của WEP** và gần như
> rỗng ở WPA2/3. Xác thực thật nằm ở bước 5. Đây là chỗ gây nhầm lẫn khi đọc tài liệu.

---

## 7. Real-world Example

🏭 **Thiết kế Wi-Fi cho văn phòng 3 tầng, 200 người**

```text
                    ┌─── WLC (HA cặp) ───┐
                    │   trong phòng server │
                    └──────────┬───────────┘
                               │ (CAPWAP qua hạ tầng có dây)
         ┌─────────────────────┼─────────────────────┐
      SW-T1                 SW-T2                 SW-T3
    (PoE+)                 (PoE+)                 (PoE+)
    6 AP                   6 AP                   6 AP
```

| Hạng mục | Quyết định | Vì sao |
|---|---|---|
| Số AP | ~6/tầng *(1 AP / ~25 người)* | Mật độ, không phải diện tích |
| Mode | **Local mode** | WLC cùng site |
| Port AP | Access port, VLAN 99 (mgmt) | Local mode không cần trunk |
| SSID | **3 cái**: nhân viên, khách, IoT | Quá nhiều SSID là lãng phí |
| PoE | PoE+ 30W/AP → **180W/tầng** | Kiểm tra PoE budget của switch |
| Uplink | 10G từ switch tầng lên core | 18 AP Wi-Fi 6 có thể vượt 1 Gbps |

🏭 **Lỗi thiết kế kinh điển: đếm theo diện tích thay vì mật độ**

Phòng họp 50 m² nhưng chứa 40 người trong cuộc họp → **một AP không đủ**,
dù về diện tích thì thừa sức phủ.

> 🔧 Quy tắc thực tế: **thiết kế theo số client đồng thời**, không theo mét vuông.
> Khoảng **25–30 client/AP** cho văn phòng; **15–20** cho khu vực mật độ cao.

🏭 **Chi nhánh dùng local mode — sai lầm tốn tiền**

Chi nhánh 20 người ở Đà Nẵng, WLC ở Hà Nội, AP để **local mode**.
Hậu quả: nhân viên Đà Nẵng in tài liệu ra máy in **ngay cạnh mình** —
traffic chạy Đà Nẵng → Hà Nội → Đà Nẵng.

```text
Sửa: chuyển AP sang FlexConnect + local switching
→ traffic xuống thẳng switch tại chỗ
→ tiết kiệm WAN, giảm độ trễ, và AP vẫn chạy khi mất WAN
```

---

## 8. Cisco CLI

> 💡 WLC chủ yếu cấu hình qua **GUI**. CLI dưới đây là phần **trên switch** —
> thứ bạn thật sự phải làm với tư cách network engineer.

```cisco
! ═══════ PORT CHO AP — LOCAL MODE (access port) ═══════
SW1(config)# interface GigabitEthernet1/0/10
SW1(config-if)# description AP-TANG1-01
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 99          ! VLAN quản trị AP
SW1(config-if)# spanning-tree portfast
SW1(config-if)# power inline auto                   ! bật PoE

! ═══════ PORT CHO AP — FLEXCONNECT (trunk) ═══════
SW1(config)# interface GigabitEthernet1/0/11
SW1(config-if)# description AP-CHI-NHANH-01
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk native vlan 99     ! VLAN quản trị AP
SW1(config-if)# switchport trunk allowed vlan 99,10,90
SW1(config-if)# spanning-tree portfast trunk

! ═══════ DHCP OPTION 43 — chỉ WLC cho AP ═══════
SW1(config)# ip dhcp pool AP-MGMT
SW1(dhcp-config)# network 10.0.99.0 255.255.255.0
SW1(dhcp-config)# default-router 10.0.99.1
SW1(dhcp-config)# option 43 hex f104.0a00.6314      ! = f1 04 + 10.0.99.20 dạng hex

! ═══════ KIỂM TRA ═══════
SW1# show power inline
SW1# show cdp neighbors detail           ! AP Cisco hiện qua CDP
SW1# show mac address-table interface Gi1/0/10
```

### Giải mã Option 43

```text
f1 04 0a 00 63 14
│  │  └────┬────┘
│  │    10.0.99.20  (mỗi octet thành hex: 10=0a, 0=00, 99=63, 20=14)
│  └── độ dài: 4 byte (1 địa chỉ IP)
└── type f1 = Cisco WLC

Hai WLC: f1 08 0a00 6314 0a00 6315
         (độ dài 08 = 2 địa chỉ)
```

> ⚠️ Đây là chỗ sai nhiều nhất khi triển khai. Tính sai hex = AP không tìm thấy WLC
> và thông báo lỗi rất mơ hồ. **Luôn kiểm tra lại bằng cách đổi ngược hex sang decimal.**

---

## 9. Verification

```text
# output điển hình — tự verify trên lab của bạn
SW1# show power inline
Available:370.0(w)  Used:150.0(w)  Remaining:220.0(w)

Interface Admin  Oper       Power   Device              Class Max
--------- ------ ---------- ------- ------------------- ----- ----
Gi1/0/10  auto   on         30.0    AIR-AP3802I-S-K9    4     30.0
Gi1/0/11  auto   on         30.0    AIR-AP3802I-S-K9    4     30.0
Gi1/0/12  auto   off        0.0     n/a                 n/a   30.0
```

| Cột | Ý nghĩa | Bất thường |
|---|---|---|
| `Remaining` | PoE budget còn lại | Gần 0 → không cắm thêm AP được |
| `Oper: on` | Đang cấp nguồn ✅ | `off` với AP đã cắm → hết budget hoặc lỗi |
| `Class 4` | PoE+ *(30W)* | Class 3 = PoE 15.4W |
| `Device` | Model AP | Trống → switch không nhận diện được |

```text
# output điển hình — tự verify trên lab của bạn
SW1# show cdp neighbors detail
Device ID: AP-TANG1-01
Entry address(es):
  IP address: 10.0.99.51
Platform: cisco AIR-AP3802I-S-K9,  Capabilities: Trans-Bridge
Interface: GigabitEthernet1/0/10,  Port ID (outgoing port): GigabitEthernet0
```

> 🔧 `show cdp neighbors detail` là cách nhanh nhất xác nhận **AP đã lên, đã có IP**,
> và biết AP đó là model gì — trước cả khi vào WLC.

**Trên WLC (GUI hoặc CLI):**

```text
# output điển hình — tự verify trên WLC của bạn
(WLC) > show ap summary
Number of APs.................................... 18
AP Name          Slots  AP Model      Ethernet MAC       Location    IP Address
AP-TANG1-01      2      AIR-AP3802I   00:1a:2b:3c:4d:50  Tang 1      10.0.99.51
AP-TANG1-02      2      AIR-AP3802I   00:1a:2b:3c:4d:60  Tang 1      10.0.99.52

(WLC) > show client summary
Number of Clients................................ 143
```

---

## 10. Troubleshooting

| Triệu chứng | Giả thuyết | Lệnh kiểm chứng | Cách sửa |
|---|---|---|---|
| AP không lên nguồn | **Hết PoE budget** hoặc sai class | `show power inline` | Tắt PoE port không dùng, nâng switch |
| AP có nguồn nhưng không join WLC | **Option 43 sai**, hoặc không tới được WLC | `show cdp neighbors`, ping WLC từ VLAN AP | Kiểm tra lại hex Option 43 |
| AP join rồi rớt liên tục | MTU trên đường CAPWAP, hoặc WLC quá tải | Log trên WLC | Kiểm tra MTU, số AP trên WLC |
| Client thấy SSID nhưng không kết nối được | Sai passphrase, hoặc RADIUS lỗi | Log WLC | Kiểm tra xác thực *(Lesson 34)* |
| Client kết nối được nhưng không có IP | DHCP không tới VLAN của SSID | `show ip dhcp pool` | Kiểm tra VLAN mapping, helper |
| Wi-Fi chậm dù ít người | Nhiễu, kênh chồng lấn, slow client | WLC → RF dashboard | Xem [Lesson 33](./lesson-33-rf-channel-roaming.md) |
| Chi nhánh Wi-Fi chậm bất thường | **Local mode qua WAN** | Xem AP mode trên WLC | Chuyển **FlexConnect** |
| Mất WLC → cả Wi-Fi chết | Local mode, không có HA | — | WLC HA pair, hoặc FlexConnect |
| Phòng họp đông người thì Wi-Fi tệ | Thiết kế theo **diện tích** thay vì mật độ | Đếm client/AP trên WLC | Thêm AP, giảm công suất mỗi AP |

---

## 11. LAB

🧪 **Bài quan sát** *(Packet Tracer mô phỏng WLC ở mức cơ bản)*

1. Trong Packet Tracer: thêm một **WLC 3504** và 2 **AP lightweight**, nối qua switch.
   Cấu hình DHCP cấp IP cho AP, quan sát AP tự join WLC.
2. Tạo một WLAN trên WLC, gán VLAN. Kết nối một laptop không dây → nhận IP.
3. Trên switch: `show power inline` xem AP tiêu thụ bao nhiêu W.
4. **Trên máy thật**: liệt kê các mạng Wi-Fi xung quanh và BSSID của chúng:

```powershell
# Windows
netsh wlan show networks mode=bssid

# Linux
sudo iw dev wlan0 scan | grep -E "SSID|signal|freq"

# macOS
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s
```

Đếm: có bao nhiêu SSID? Có SSID nào xuất hiện với **nhiều BSSID** không (= ESS)?

## 12. Challenge

1. Một AP phát 3 SSID trên cả 2.4 và 5 GHz. Có bao nhiêu BSSID?
2. Công ty 200 người trong 1500 m². Cần bao nhiêu AP? Dựa trên tiêu chí nào?
3. Chi nhánh 15 người, WLC ở trụ sở cách 800 km, đường WAN 20 Mbps.
   Chọn local mode hay FlexConnect? Giải thích bằng số liệu.
4. Vì sao không nên tạo 8 SSID dù WLC hỗ trợ tới 16?

<details>
<summary>Đáp án</summary>

**1.** **6 BSSID.** Mỗi SSID × mỗi radio (băng tần) = một BSSID riêng.
`3 SSID × 2 băng tần = 6`.

Đây là lý do một AP duy nhất có thể xuất hiện 6 lần trong kết quả quét `netsh wlan show networks mode=bssid`.

**2.** Tính theo **mật độ client**, không theo diện tích:

```text
200 người / 25 client mỗi AP  ≈  8 AP  (tối thiểu)
```

Nhưng còn phải xét:
- **Phân bố**: phòng họp đông người cần thêm AP riêng
- **Vật cản**: tường bê tông, tủ kim loại
- **Băng tần**: ưu tiên 5 GHz → tầm ngắn hơn → cần nhiều AP hơn

👉 Thực tế cho 200 người: **10–14 AP**, và phải khảo sát tại chỗ (site survey) để
xác định vị trí.

**3.** **FlexConnect**, rõ ràng.

Tính thử với local mode:

```text
15 người, giả sử mỗi người dùng trung bình 2 Mbps
→ 30 Mbps traffic Wi-Fi
→ TOÀN BỘ phải chạy qua WAN 20 Mbps về Hà Nội rồi quay lại
→ WAN NGHẼN NGAY, kể cả khi họ chỉ truy cập máy in cạnh bàn
```

Thêm nữa: **mất WAN = mất Wi-Fi hoàn toàn** ở local mode.
Với FlexConnect, AP vẫn phục vụ client khi WAN đứt.

**4.** Vì **mỗi SSID tốn thời gian phát sóng (airtime)**:

```text
Mỗi SSID gửi BEACON ~10 lần/giây, trên MỖI băng tần
8 SSID × 2 băng tần × 10 beacon/giây = 160 beacon/giây
→ chiếm đáng kể airtime mà KHÔNG chở dữ liệu nào
```

Beacon còn được gửi ở **tốc độ thấp nhất** (để client xa cũng nghe được),
nên mỗi cái chiếm airtime lâu hơn gói dữ liệu bình thường.

Hệ quả: 8 SSID có thể làm giảm **20–25%** throughput khả dụng.

> 🔧 Quy tắc: **tối đa 3–4 SSID**. Cần phân biệt nhiều nhóm người dùng hơn thì
> dùng **802.1X + dynamic VLAN assignment** — một SSID, nhiều VLAN tuỳ danh tính.

</details>

---

## 13. Knowledge Check

| Cấp | Nội dung | Xong? |
|:---:|---|:---:|
| **L1** Recall | SSID vs BSSID vs BSS vs ESS · port CAPWAP · PoE class | ⬜ |
| **L2** Explain | Giải thích vì sao Wi-Fi chậm hơn con số quảng cáo | ⬜ |
| **L3** Configure | Cấu hình port switch cho AP ở cả local mode và FlexConnect | ⬜ |
| **L4** Troubleshoot | AP không join WLC → nêu 3 nguyên nhân theo thứ tự | ⬜ |
| **L5** Design | Thiết kế Wi-Fi cho văn phòng 3 tầng: số AP, mode, SSID, PoE | ⬜ |

## 14. Summary

**Key concepts**

- 802.11 là công nghệ **Layer 2** — từ L3 trở lên giống hệt mạng có dây
- ⭐ Wi-Fi **half-duplex, dùng chung môi trường** → throughput thực ~50–60% con số quảng cáo
- **SSID** = tên · **BSSID** = MAC radio · **BSS** = 1 AP + client · **ESS** = nhiều AP cùng SSID
- Một AP có **nhiều BSSID**: `số SSID × số băng tần`
- **CAPWAP**: control **UDP 5246** *(luôn mã hoá)* · data **UDP 5247**
- ⭐ **Local mode**: traffic về tận WLC — kể cả giữa 2 client cùng AP
- ⭐ **FlexConnect**: traffic xuống thẳng switch tại chỗ — dùng cho **chi nhánh**
- AP cần **PoE+ (30W)**; local mode → access port, FlexConnect → trunk
- **DHCP Option 43** là cách phổ biến nhất để AP tìm WLC — và hay sai nhất
- ⭐ Thiết kế theo **mật độ client** (~25/AP), không theo diện tích
- **Tối đa 3–4 SSID** — mỗi SSID tốn airtime cho beacon

**Commands cần nhớ**

| Lệnh | Dùng khi |
|---|---|
| `show power inline` | PoE budget còn bao nhiêu |
| `show cdp neighbors detail` | AP đã lên chưa, model gì, IP nào |
| `switchport access vlan 99` + `power inline auto` | Port AP local mode |
| `switchport mode trunk` | Port AP FlexConnect |
| `option 43 hex f104.XXXX.XXXX` | Chỉ WLC cho AP |
| `netsh wlan show networks mode=bssid` | Quét Wi-Fi xung quanh |

**Common mistakes**

| Sai | Hậu quả |
|---|---|
| Thiết kế theo diện tích | Phòng họp đông người Wi-Fi tệ |
| Tạo 8 SSID | Mất 20–25% throughput vì beacon |
| Local mode cho chi nhánh qua WAN | Traffic chạy vòng, WAN nghẽn, mất WAN = mất Wi-Fi |
| Tính sai hex Option 43 | AP không join, lỗi khó hiểu |
| Không kiểm tra PoE budget | Cắm thêm AP là không lên nguồn |
| Nhầm BSSID với SSID | Hiểu sai khi đọc log và khảo sát |

## 15. Homework + cập nhật PROGRESS

1. Làm bài quan sát mục 11, kể cả phần quét Wi-Fi trên máy thật.
2. Đếm số AP ở văn phòng/nhà bạn. Tính tỷ lệ client/AP.
3. Tính Option 43 hex cho WLC có IP `192.168.1.100`.
4. Tìm hiểu công ty bạn dùng kiến trúc nào: autonomous, WLC, hay cloud-managed?

```markdown
- [YYYY-MM-DD] Lesson 32 — WLAN, AP, WLC: DONE | cần ôn lại <điểm yếu>
```

---

### 🧭 Phân tầng kiến thức

| Tầng | Nội dung |
|---|---|
| 🎓 **Exam** | SSID/BSSID/BSS/ESS, CAPWAP port, autonomous vs lightweight, local vs FlexConnect |
| 🔧 **Engineer** | Port AP đúng mode; PoE budget; Option 43; giới hạn số SSID |
| 🏭 **Production** | Thiết kế theo mật độ; chi nhánh dùng FlexConnect; WLC cần HA |

### 🔗 Liên kết

- ⬅️ [Phase 4 — IPv6](../04-ipv6/README.md)
- ➡️ [Lesson 33 — RF, kênh, roaming](./lesson-33-rf-channel-roaming.md)
- 🔜 Sâu hơn: [`CCNP-Encor` Module 07B — CAPWAP, FlexConnect, Roaming](https://github.com/hiepnguyen775/CCNP-Encor)
