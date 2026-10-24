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
├── bai2/
│   ├── sensor_server_bai2.py    # Cảm biến cập nhật mỗi 3 giây
│   └── monitor_client_bai2.py   # Giám sát, CSV và thống kê
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

---

## 5. Bài 2: Cảm biến nhiệt độ và độ ẩm bằng CoAP

Đã triển khai yêu cầu chính và đủ 5 gợi ý mở rộng:

- Server mô phỏng `sensor01`, `sensor02`, `sensor03`, cập nhật độc lập mỗi 3 giây: nhiệt độ 20–40°C, độ ẩm 30–80%.
- Mỗi thiết bị có URI `coap://127.0.0.1:5683/iot/lab/<device_id>/data` (UDP). GET trả mã `2.05 Content`, Content-Format `50` (`application/json`).
- JSON gồm `device_id`, `temperature`, `humidity`, `timestamp` (thời gian cập nhật cảm biến, ISO 8601 có múi giờ).
- Client chọn thiết bị bằng `--device`, GET mỗi 3 giây; cảnh báo khi nhiệt độ > 35°C hoặc độ ẩm < 40%; in thời điểm nhận và trạng thái bình thường nếu không có cảnh báo.
- Dữ liệu hợp lệ được ghi nối tiếp vào `bai2/sensor_data.csv`, không ghi đè dữ liệu cũ. Các cột: `device_id,temperature,humidity,timestamp,received_at,response_ms`.
- Thống kê mỗi lượt và khi dừng: số GET đã gửi, số phản hồi nhận được, thời gian phản hồi trung bình (ms). Trung bình tính trên mọi phản hồi CoAP nhận được, kể cả phản hồi lỗi; không tính timeout/lỗi kết nối. Chưa có phản hồi thì hiển thị `N/A`.
- Client báo lỗi khi server không phản hồi sau 5 giây hoặc trả dữ liệu không hợp lệ, rồi tiếp tục giám sát; chỉ ghi dữ liệu hợp lệ vào CSV.

### Cách chạy (Windows)

Mở terminal tại thư mục gốc repo. Dừng server Bài 1 trước vì dùng chung cổng `5683`.

1. Cài môi trường (một lần):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install aiocoap
   ```
2. Terminal 1 — chạy server cho cả 3 cảm biến:
   ```powershell
   .\.venv\Scripts\python.exe -u bai2/sensor_server_bai2.py
   ```
3. Terminal 2 — chọn cảm biến cần giám sát:
   ```powershell
   .\.venv\Scripts\python.exe -u bai2/monitor_client_bai2.py --device sensor02
   ```
   Có thể chọn `sensor01`, `sensor02`, `sensor03`; mặc định là `sensor01`.
4. Nhấn `Ctrl+C` tại từng terminal để dừng; client in thống kê tổng kết. Mỗi lần chạy lại, bộ đếm bắt đầu từ 0 và CSV tiếp tục được ghi nối tiếp.

### Kết quả chạy thực tế

Windows, Python `3.14.2`, `aiocoap 0.4.17`. Trích output client chọn `sensor02`:

```text
[11:28:48] Received sensor data
Device: sensor02
Temperature: 39.3 C
Humidity: 42.9 %
Timestamp: 2026-10-24T11:28:46+07:00
CANH BAO: Nhiet do cao
GET: 1 | Responses: 1 | Avg response: 4.249 ms
------------------------------
[11:28:51] Received sensor data
Device: sensor02
Temperature: 28.0 C
Humidity: 73.4 %
Timestamp: 2026-10-24T11:28:49+07:00
Trang thai: Binh thuong
GET: 2 | Responses: 2 | Avg response: 3.585 ms
------------------------------
```
