# BÁO CÁO THỰC HÀNH BUỔI 3 - LẬP TRÌNH PYTHON VỚI GIAO THỨC CoAP

## 1. Thông tin sinh viên
- **Họ và tên**: [Điền họ và tên]
- **Mã sinh viên**: [Điền mã sinh viên]
- **Lớp**: [Điền lớp]
- **Môn học**: Thực hành Internet of Things (IoT)

---

## 2. Môi trường và Thư viện
- **Hệ điều hành**: Windows / Linux / macOS
- **Phiên bản Python**: Python 3.10+ (Đã kiểm thử trên Python 3.12)
- **Thư viện chính**: `aiocoap` (v0.4.17+)

### Cài đặt thư viện:
```bash
pip install aiocoap
```

---

## 3. Cấu trúc thư mục dự án
```text
PTIT_TH_IOT_B3/
├── bai1/
│   ├── coap_server_bai1.py      # CoAP Server bài 1
│   └── coap_client_bai1.py      # CoAP Client bài 1
├── bai2/                         # (Các bài tiếp theo)
├── bai3/
├── .gitignore
└── README.md
```

---

## 4. Bài 1: Ứng dụng gửi và nhận thông điệp CoAP cơ bản

### 4.1. Mô tả tài nguyên
| Thông số | Giá trị |
| :--- | :--- |
| **Giao thức** | CoAP (chạy trên nền UDP) |
| **Địa chỉ mặc định** | `127.0.0.1` / `localhost` |
| **Cổng (Port)** | `5683` |
| **URI Tài nguyên** | `coap://localhost:5683/iot/lab/message` |
| **Phương thức hỗ trợ** | `GET`, `POST` |

- **Phương thức GET**:
  - Trả về thông điệp chào mừng từ Server: `Xin chao tu CoAP Server` (hoặc thông điệp gần nhất nhận được).
  - Phản hồi mã CoAP `2.05 Content`.
- **Phương thức POST**:
  - Client gửi thông điệp gồm Họ tên, Mã sinh viên và lời chào:
    `Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A`
  - Server in ra nội dung và thời điểm nhận (`Time: HH:MM:SS`), sau đó phản hồi mã CoAP `2.04 Changed` với payload `Server da nhan thong diep`.

### 4.2. Hướng dẫn chạy chương trình

#### Bước 1: Khởi động CoAP Server (Terminal 1)
```bash
python bai1/coap_server_bai1.py
```
*Tùy chọn:*
- `--port <cổng>`: Chỉ định cổng CoAP (mặc định 5683).
- `--host <IP>`: Chỉ định IP giao diện cần bind (mặc định lắng nghe cả `127.0.0.1` và `::1`).

#### Bước 2: Chạy CoAP Client (Terminal 2)
Chạy mặc định với thông tin mẫu:
```bash
python bai1/coap_client_bai1.py
```

Chạy với thông tin sinh viên cụ thể:
```bash
python bai1/coap_client_bai1.py --name "Nguyen Van A" --id "B23DCCN001"
```

Chạy chế độ tương tác gửi nhiều tin nhắn liên tiếp (Gợi ý mở rộng):
```bash
python bai1/coap_client_bai1.py --interactive
```

Kiểm tra xử lý lỗi khi truy cập tài nguyên không tồn tại (Gợi ý mở rộng):
```bash
python bai1/coap_client_bai1.py --test-not-found
```

---

### 4.3. Kết quả chạy thực tế (Log minh chứng)

#### Terminal 1: CoAP Server
```text
CoAP Server
CoAP Server started on port 5683
URI: coap://localhost:5683/iot/lab/message
Nhan Ctrl+C de dung server.
----------------------------------------
GET request received: /iot/lab/message
POST request received:
Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
Time: 20:14:46
```

#### Terminal 2: CoAP Client
```text
CoAP Client
Sending GET request...
URI: coap://localhost:5683/iot/lab/message
Response:
Code: 2.05 Content
Payload: Xin chao tu CoAP Server
----------------------------------------
Sending POST request...
Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
Response:
Code: 2.04 Changed
Payload: Server da nhan thong diep
----------------------------------------
```

#### Minh chứng tính năng mở rộng:
1. **Kiểm tra tài nguyên không tồn tại (`--test-not-found`)**:
```text
[Kiem tra mo rong] Gui GET toi tai nguyen khong ton tai:
Sending GET request...
URI: coap://localhost:5683/iot/lab/invalid_path
Response:
Code: 4.04 Not Found
Payload: 
```

2. **Xử lý khi Server không hoạt động / Timeout**:
```text
CoAP Client
Sending GET request...
URI: coap://localhost:5684/iot/lab/message
[Loi] Gui GET that bai: Network error: NetworkError
----------------------------------------
Sending POST request...
Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
[Loi] Yeu cau POST bi timeout - Server khong phan hoi.
----------------------------------------
```

---

### 4.4. Đánh giá hoàn thành Bài 1
- [x] Khởi tạo và chạy được CoAP Server lắng nghe trên cổng 5683.
- [x] Định nghĩa đúng URI tài nguyên `/iot/lab/message`.
- [x] Xử lý chính xác phương thức GET (trả về mã 2.05 Content).
- [x] Xử lý chính xác phương thức POST (nhận nội dung, hiển thị payload, thời gian nhận, phản hồi 2.04 Changed).
- [x] Client gửi thành công cả GET và POST, hiển thị đúng định dạng.
- [x] Triển khai đầy đủ các gợi ý mở rộng: lưu payload gần nhất, kiểm tra 4.04 Not Found, xử lý lỗi timeout khi Server ngắt kết nối.
- [x] Tương thích tốt trên Windows và Linux/macOS.
