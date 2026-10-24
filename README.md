# Báo Cáo Thực Hành CoAP với Python & aiocoap

## 1. Môi trường & Giao thức sử dụng
- Giao thức: CoAP (chạy trên UDP), cổng mặc định `5683`.
- Ngôn ngữ lập trình: Python 3.10+ (đã kiểm thử trên Python 3.12 và 3.14).
- Thư viện CoAP: `aiocoap` (v0.4.17+).
- Cài đặt thư viện:
```
python -m pip install aiocoap
```
- Lưu ý: cả 3 bài dùng chung cổng 5683, cần dừng server của bài trước (Ctrl + C) trước khi chạy server của bài sau.

## 2. Bài 1: Ứng dụng gửi và nhận thông điệp CoAP cơ bản

### Mục tiêu & Mô tả
| Thông số | Giá trị |
|---|---|
| Giao thức | CoAP (chạy trên nền UDP) |
| Địa chỉ mặc định | 127.0.0.1 / localhost |
| Cổng (Port) | 5683 |
| URI Tài nguyên | `coap://localhost:5683/iot/lab/message` |
| Phương thức hỗ trợ | GET, POST |

Phương thức GET:
- Trả về thông điệp chào mừng từ Server: `Xin chao tu CoAP Server` (hoặc thông điệp gần nhất nhận được).
- Phản hồi mã CoAP `2.05 Content`.

Phương thức POST:
- Client gửi thông điệp gồm Họ tên, Mã sinh viên và lời chào: `Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A`
- Server in ra nội dung và thời điểm nhận (`Time: HH:MM:SS`), sau đó phản hồi mã CoAP `2.04 Changed` với payload `Server da nhan thong diep`.

### Cách chạy
Bước 1: Khởi động CoAP Server (Terminal 1)
```
python bai1/coap_server_bai1.py
```
Tùy chọn:
- `--port <cổng>`: Chỉ định cổng CoAP (mặc định 5683).
- `--host <IP>`: Chỉ định IP giao diện cần bind (mặc định lắng nghe cả 127.0.0.1 và ::1).

Bước 2: Chạy CoAP Client (Terminal 2)

Chạy mặc định với thông tin mẫu:
```
python bai1/coap_client_bai1.py
```
Chạy với thông tin sinh viên cụ thể:
```
python bai1/coap_client_bai1.py --name "Nguyen Van A" --id "B23DCCN001"
```
Chạy chế độ tương tác gửi nhiều tin nhắn liên tiếp (Gợi ý mở rộng):
```
python bai1/coap_client_bai1.py --interactive
```
Kiểm tra xử lý lỗi khi truy cập tài nguyên không tồn tại (Gợi ý mở rộng):
```
python bai1/coap_client_bai1.py --test-not-found
```

### Kết quả chạy thực tế
Terminal 1: CoAP Server
```
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
Terminal 2: CoAP Client
```
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
Minh chứng tính năng mở rộng:

Kiểm tra tài nguyên không tồn tại (`--test-not-found`):
```
[Kiem tra mo rong] Gui GET toi tai nguyen khong ton tai:
Sending GET request...
URI: coap://localhost:5683/iot/lab/invalid_path
Response:
Code: 4.04 Not Found
Payload:
```
Xử lý khi Server không hoạt động / Timeout:
```
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

## 3. Bài 2: Cảm biến nhiệt độ và độ ẩm bằng CoAP

### Mục tiêu & Mô tả
Đã triển khai yêu cầu chính và đủ 5 gợi ý mở rộng:
- Server mô phỏng `sensor01`, `sensor02`, `sensor03`, cập nhật độc lập mỗi 3 giây: nhiệt độ 20–40°C, độ ẩm 30–80%.
- Mỗi thiết bị có URI `coap://127.0.0.1:5683/iot/lab/<device_id>/data` (UDP). GET trả mã `2.05 Content`, Content-Format 50 (`application/json`).
- JSON gồm `device_id`, `temperature`, `humidity`, `timestamp` (thời gian cập nhật cảm biến, ISO 8601 có múi giờ).
- Client chọn thiết bị bằng `--device`, GET mỗi 3 giây; cảnh báo khi nhiệt độ > 35°C hoặc độ ẩm < 40%; in thời điểm nhận và trạng thái bình thường nếu không có cảnh báo.
- Dữ liệu hợp lệ được ghi nối tiếp vào `bai2/sensor_data.csv`, không ghi đè dữ liệu cũ. Các cột: `device_id,temperature,humidity,timestamp,received_at,response_ms`.
- Thống kê mỗi lượt và khi dừng: số GET đã gửi, số phản hồi nhận được, thời gian phản hồi trung bình (ms). Trung bình tính trên mọi phản hồi CoAP nhận được, kể cả phản hồi lỗi; không tính timeout/lỗi kết nối. Chưa có phản hồi thì hiển thị `N/A`.
- Client báo lỗi khi server không phản hồi sau 5 giây hoặc trả dữ liệu không hợp lệ, rồi tiếp tục giám sát; chỉ ghi dữ liệu hợp lệ vào CSV.

### Cách chạy (Windows)
Mở terminal tại thư mục gốc repo. Dừng server Bài 1 trước vì dùng chung cổng 5683.

Cài môi trường (một lần):
```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install aiocoap
```
Terminal 1 — chạy server cho cả 3 cảm biến:
```
.\.venv\Scripts\python.exe -u bai2/sensor_server_bai2.py
```
Terminal 2 — chọn cảm biến cần giám sát:
```
.\.venv\Scripts\python.exe -u bai2/monitor_client_bai2.py --device sensor02
```
Có thể chọn `sensor01`, `sensor02`, `sensor03`; mặc định là `sensor01`.

Nhấn Ctrl+C tại từng terminal để dừng; client in thống kê tổng kết. Mỗi lần chạy lại, bộ đếm bắt đầu từ 0 và CSV tiếp tục được ghi nối tiếp.

### Kết quả chạy thực tế
Windows, Python 3.14.2, aiocoap 0.4.17. Trích output client chọn `sensor02`:
```
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

## 4. Bài 3: Hệ thống giám sát và điều khiển đèn thông minh (CoAP Observe)
### Mục tiêu & Mô tả
Làm quen với PUT và cơ chế Observe của CoAP để server chủ động thông báo khi trạng thái thay đổi.
- URI tài nguyên: `coap://127.0.0.1:5683/iot/lab/light01/status` (trạng thái ban đầu `OFF`).
- Server (`light_server_bai3.py`): hỗ trợ GET, PUT và Observe.
  - GET: trả `{"device_id": "light01", "status": "ON"}`.
  - PUT: nhận `{"device_id": "light01", "command": "ON"}` (hoặc `OFF`), phản hồi `2.04 Changed`. Lệnh sai trả `4.00 Bad Request`, sai `device_id` trả `4.04 Not Found`.
  - Observe: chỉ thông báo cho các client đang đăng ký khi trạng thái thực sự thay đổi. Mỗi lần đổi trạng thái được ghi vào `light_log.txt`.
- Controller (`light_controller_bai3.py`): nhập lệnh `ON`, `OFF`, `STATUS`, `EXIT`.
- Monitor (`light_monitor_bai3.py`): đăng ký Observe, nhận trạng thái ban đầu và tự động nhận thông báo khi đèn đổi trạng thái (không dùng vòng lặp GET).

### Cách chạy
Khởi chạy Server trước, sau đó chạy Monitor và Controller:
1. Smart Light Server (Terminal 1):
```
python -u bai3/light_server_bai3.py
```
2. Monitoring Client (Terminal 2):
```
python -u bai3/light_monitor_bai3.py
```
3. Controller Client (Terminal 3):
```
python -u bai3/light_controller_bai3.py
```
Trong Terminal 3 nhập lần lượt `STATUS`, `ON`, `ON`, `OFF`, `EXIT` và quan sát Terminal 2. Nhấn Ctrl + C để dừng Server và Monitor.

Chạy trên hai máy khác nhau: truyền IP của máy server làm tham số, ví dụ `python bai3/light_server_bai3.py 192.168.1.10`, và `python bai3/light_monitor_bai3.py 192.168.1.10` (Controller tương tự). Cần mở UDP 5683 trên tường lửa.

### Kết quả chạy thực tế
Smart Light Server (`light_server_bai3.py`):
```
CoAP Smart Light Server started...
Resource: /iot/lab/light01/status
New Observe registration received
PUT request received:
Device: light01
Command: ON
Light state changed: OFF -> ON
Notify observers: ON
PUT request received:
Device: light01
Command: ON
Light state unchanged: ON
GET request received: /iot/lab/light01/status
PUT request received:
Device: light01
Command: OFF
Light state changed: ON -> OFF
Notify observers: OFF
```
Monitoring Client (`light_monitor_bai3.py`):
```
Registering CoAP Observe...
Observe registration successful
[20:31:05] Initial State
Device: light01
Status: OFF
[20:31:20] State Updated
Device: light01
Status: ON
[20:31:41] State Updated
Device: light01
Status: OFF
```
Controller Client (`light_controller_bai3.py`):
```
Light Controller - Server: coap://127.0.0.1:5683/iot/lab/light01/status
Nhap lenh (ON/OFF/STATUS/EXIT): ON
Sending PUT request...
Response Code: 2.04 Changed
Da bat den light01
Nhap lenh (ON/OFF/STATUS/EXIT): ON
Sending PUT request...
Response Code: 2.04 Changed
Den light01 da o trang thai ON san roi
Nhap lenh (ON/OFF/STATUS/EXIT): STATUS
Sending GET request...
Response:
{"device_id": "light01", "status": "ON"}
Nhap lenh (ON/OFF/STATUS/EXIT): OFF
Sending PUT request...
Response Code: 2.04 Changed
Da tat den light01
Nhap lenh (ON/OFF/STATUS/EXIT): EXIT
Tam biet!
```
File nhật ký (`light_log.txt`):
```
2026-10-24 20:31:20 light01: OFF -> ON
2026-10-24 20:31:41 light01: ON -> OFF
```
(Lưu ý: lệnh `ON` lần thứ hai khi đèn đã `ON` vẫn được phản hồi `2.04 Changed` nhưng Monitor không nhận thông báo, phản ánh đúng cơ chế Observe chỉ gửi khi trạng thái thay đổi.)

## 5. Tổng kết danh mục file nộp bài
| Bài | File chương trình | Vai trò |
|---|---|---|
| Bài 1 | `bai1/coap_server_bai1.py` | CoAP Server xử lý GET, POST tại `/iot/lab/message` |
| | `bai1/coap_client_bai1.py` | Client gửi GET, POST và hiển thị phản hồi |
| Bài 2 | `bai2/sensor_server_bai2.py` | Mô phỏng 3 cảm biến, cập nhật mỗi 3 giây, trả JSON |
| | `bai2/monitor_client_bai2.py` | GET định kỳ, cảnh báo ngưỡng, ghi CSV và thống kê |
| Bài 3 | `bai3/light_server_bai3.py` | Smart Light Server hỗ trợ GET, PUT, Observe |
| | `bai3/light_controller_bai3.py` | Điều khiển đèn bằng lệnh ON, OFF, STATUS |
| | `bai3/light_monitor_bai3.py` | Giám sát trạng thái đèn bằng CoAP Observe |
| Tài liệu | `README.md` | Báo cáo môi trường, cách chạy và kết quả |