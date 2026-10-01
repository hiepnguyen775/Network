# 🧮 Subnetting Cheat Sheet (IPv4)

> **Mục tiêu:** tính Network / Broadcast / host range **trong đầu, dưới 30 giây**, không máy tính.
> File này để **tra lúc đang lab**, không phải để học thuộc. Kỹ năng chỉ đến từ việc làm đủ nhiều bài.

---

## 1. Bảng magic number — học thuộc bảng này trước

| CIDR | Subnet mask | Block size | Host usable | Dùng cho |
|:---:|---|:---:|:---:|---|
| `/24` | `255.255.255.0` | 256 | **254** | Một VLAN văn phòng cỡ vừa |
| `/25` | `255.255.255.128` | 128 | **126** | |
| `/26` | `255.255.255.192` | 64 | **62** | Phòng ban ~50 người |
| `/27` | `255.255.255.224` | 32 | **30** | Phòng ban nhỏ |
| `/28` | `255.255.255.240` | 16 | **14** | Nhóm server |
| `/29` | `255.255.255.248` | 8 | **6** | Nhóm thiết bị nhỏ |
| `/30` | `255.255.255.252` | 4 | **2** | **Link point-to-point** |
| `/31` | `255.255.255.254` | 2 | **2** ⚠️ | P2P — ngoại lệ RFC 3021, xem ghi chú dưới |
| `/32` | `255.255.255.255` | 1 | — | Host đơn / loopback |

### Prefix lớn hơn /24

| CIDR | Subnet mask | Số IP | Host usable |
|:---:|---|:---:|:---:|
| `/23` | `255.255.254.0` | 512 | 510 |
| `/22` | `255.255.252.0` | 1 024 | 1 022 |
| `/21` | `255.255.248.0` | 2 048 | 2 046 |
| `/20` | `255.255.240.0` | 4 096 | 4 094 |
| `/16` | `255.255.0.0` | 65 536 | 65 534 |

---

## 2. Ba công thức

```
Số host usable  =  2^(32 − prefix) − 2        ← trừ Network + Broadcast
Block size      =  256 − octet_mask            ← tại octet "thú vị"
Số subnet       =  2^(số bit mượn)
```

> ⚠️ Lỗi phổ biến nhất: quên trừ 2. `2^n` là **tổng số địa chỉ**, không phải số host gán được.
>
> ⚠️ **Ngoại lệ `/31`:** công thức cho ra `0`, nhưng **RFC 3021** bỏ quy ước network/broadcast
> trên link point-to-point nên cả 2 địa chỉ đều gán được → **2 host**. Chỉ áp dụng cho P2P link.

---

## 3. Quy trình tính nhanh — 4 bước

**Ví dụ: `192.168.10.100/26`**

| Bước | Làm gì | Kết quả |
|:---:|---|---|
| 1 | Đổi `/26` ra mask, tìm **octet thú vị** | `255.255.255.192` → octet 4 |
| 2 | Block size = `256 − 192` | **64** |
| 3 | Liệt kê mốc network: `0, 64, 128, 192` | `100` nằm trong `64 → 127` |
| 4 | Đọc ra 4 giá trị | |

```
Network   = 192.168.10.64
First host= 192.168.10.65
Last host = 192.168.10.126
Broadcast = 192.168.10.127
Usable    = 62
```

### Bảng mốc theo block size — nhẩm nhanh

| Block | Các mốc network ở octet cuối |
|:---:|---|
| 128 | 0, 128 |
| 64 | 0, 64, 128, 192 |
| 32 | 0, 32, 64, 96, 128, 160, 192, 224 |
| 16 | 0, 16, 32, 48, 64, 80, 96, 112, 128, … |
| 8 | 0, 8, 16, 24, 32, … |
| 4 | 0, 4, 8, 12, 16, … |

---

## 4. VLSM — chia theo nhu cầu, **lớn trước**

Sắp yêu cầu host **giảm dần**, cấp block vừa đủ:

| Phòng ban | Host cần | Prefix | Block | Dải cấp | Broadcast |
|---|:---:|:---:|:---:|---|---|
| Sales | 50 | `/26` | 64 | `10.0.0.0` – `.63` | `.63` |
| IT | 25 | `/27` | 32 | `10.0.0.64` – `.95` | `.95` |
| Kế toán | 12 | `/28` | 16 | `10.0.0.96` – `.111` | `.111` |
| Server | 6 | `/29` | 8 | `10.0.0.112` – `.119` | `.119` |
| WAN link 1 | 2 | `/30` | 4 | `10.0.0.120` – `.123` | `.123` |
| WAN link 2 | 2 | `/30` | 4 | `10.0.0.124` – `.127` | `.127` |

> **Quy tắc:** luôn cấp subnet **lớn trước** để tránh phân mảnh.
> Link point-to-point dùng `/30` (hoặc `/31` nếu thiết bị hỗ trợ).

---

## 5. Wildcard mask (dùng trong OSPF & ACL)

Wildcard = **nghịch đảo** subnet mask: `255.255.255.255 − subnet mask`

| Prefix | Subnet mask | Wildcard mask |
|:---:|---|---|
| `/24` | `255.255.255.0` | `0.0.0.255` |
| `/25` | `255.255.255.128` | `0.0.0.127` |
| `/26` | `255.255.255.192` | `0.0.0.63` |
| `/27` | `255.255.255.224` | `0.0.0.31` |
| `/28` | `255.255.255.240` | `0.0.0.15` |
| `/30` | `255.255.255.252` | `0.0.0.3` |
| `/32` | `255.255.255.255` | `0.0.0.0` *(host đơn)* |

Hai giá trị đặc biệt hay dùng:

```
host 192.168.1.10   ≡   192.168.1.10 0.0.0.0
any                 ≡   0.0.0.0 255.255.255.255
```

---

## 6. Dải IP private & đặc biệt

| Dải | Prefix | Dùng cho |
|---|---|---|
| `10.0.0.0` – `10.255.255.255` | `/8` | Private (RFC 1918) — doanh nghiệp lớn |
| `172.16.0.0` – `172.31.255.255` | `/12` | Private — hay bị nhớ nhầm là `/16` |
| `192.168.0.0` – `192.168.255.255` | `/16` | Private — gia đình, văn phòng nhỏ |
| `169.254.0.0` | `/16` | APIPA — **dấu hiệu DHCP hỏng** |
| `127.0.0.0` | `/8` | Loopback |
| `224.0.0.0` – `239.255.255.255` | `/4` | Multicast |

> 🏭 **Production:** thấy máy nhận IP `169.254.x.x` → DHCP không tới được.
> Kiểm tra theo thứ tự: cáp → VLAN của port → `ip helper-address` → DHCP pool còn IP không.

---

## 7. Bẫy hay gặp 🎓

| Bẫy | Đúng là |
|---|---|
| Số host = `2^n` | `2^n − 2` |
| Gán IP network hoặc broadcast cho host | Hai địa chỉ này **không gán được** |
| `/30` nghĩ là 4 host | Chỉ **2** host — vừa đủ một WAN link |
| `172.16.0.0/16` | Dải private là `172.16.0.0/12` (từ `172.16` đến `172.31`) |
| Gateway đặt tuỳ hứng mỗi subnet một kiểu | Thống nhất toàn hệ thống: luôn **first usable** hoặc luôn **last usable** |
| Dùng wildcard mask như subnet mask trong `network` của OSPF | Ngược nhau — xem mục 5 |

---

## 8. Tự luyện

> Mục tiêu Phase 0: **20 câu liên tiếp, đúng ≥ 18, trung bình < 30 giây/câu.**

Với mỗi địa chỉ dưới đây, tìm Network / First / Last / Broadcast / số host:

```
1.  192.168.1.77/26          6.  10.10.10.200/27
2.  172.16.45.130/25         7.  192.168.100.5/30
3.  10.0.5.33/28             8.  172.20.8.90/22
4.  192.168.200.19/29        9.  10.1.1.1/23
5.  172.31.99.250/24        10.  192.168.7.130/28
```

<details>
<summary>Đáp án</summary>

| # | Network | First | Last | Broadcast | Host |
|:---:|---|---|---|---|:---:|
| 1 | 192.168.1.64 | .65 | .126 | .127 | 62 |
| 2 | 172.16.45.128 | .129 | .254 | .255 | 126 |
| 3 | 10.0.5.32 | .33 | .46 | .47 | 14 |
| 4 | 192.168.200.16 | .17 | .22 | .23 | 6 |
| 5 | 172.31.99.0 | .1 | .254 | .255 | 254 |
| 6 | 10.10.10.192 | .193 | .222 | .223 | 30 |
| 7 | 192.168.100.4 | .5 | .6 | .7 | 2 |
| 8 | 172.20.8.0 | 172.20.8.1 | 172.20.11.254 | 172.20.11.255 | 1022 |
| 9 | 10.1.0.0 | 10.1.0.1 | 10.1.1.254 | 10.1.1.255 | 510 |
| 10 | 192.168.7.128 | .129 | .142 | .143 | 14 |

</details>
