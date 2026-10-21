"""
Chương trình 1: CoAP Server - Bài 1
Mô tả: Khởi tạo CoAP Server cung cấp tài nguyên /iot/lab/message
Hỗ trợ:
  - GET: Trả về thông điệp chào mừng (hoặc thông điệp gần nhất nhận được)
  - POST: Nhận thông điệp từ Client, hiển thị nội dung và thời gian nhận,
          sau đó phản hồi xác nhận.
"""

import sys
import asyncio
import argparse
import datetime
import aiocoap
import aiocoap.resource as resource

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class MessageResource(resource.Resource):
    """
    Tài nguyên /iot/lab/message
    """
    def __init__(self, initial_message: str = "Xin chao tu CoAP Server"):
        super().__init__()
        self.message = initial_message

    async def render_get(self, request):
        print("GET request received: /iot/lab/message", flush=True)
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=self.message.encode("utf-8")
        )

    async def render_post(self, request):
        payload_text = request.payload.decode("utf-8", errors="replace")
        recv_time = datetime.datetime.now().strftime("%H:%M:%S")

        print("POST request received:", flush=True)
        print(f"Payload: {payload_text}", flush=True)
        print(f"Time: {recv_time}", flush=True)

        # Gợi ý mở rộng: Lưu lại thông điệp POST gần nhất
        self.message = payload_text

        # Trả về phản hồi xác nhận
        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload="Server da nhan thong diep".encode("utf-8")
        )


async def start_server(host: str = None, port: int = 5683):
    # Khởi tạo cây tài nguyên (Site)
    root = resource.Site()
    msg_resource = MessageResource()
    root.add_resource(["iot", "lab", "message"], msg_resource)

    servers = []

    try:
        if host:
            # Nếu người dùng chỉ định host cụ thể
            srv = await aiocoap.Context.create_server_context(root, bind=(host, port))
            servers.append(srv)
        else:
            # Mặc định: Lắng nghe trên cả IPv4 và IPv6 loopback (127.0.0.1 và ::1)
            # Điều này giúp hỗ trợ cả truy cập qua 'localhost' và '127.0.0.1' trên mọi hệ điều hành (kể cả Windows)
            try:
                srv_v4 = await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", port))
                servers.append(srv_v4)
            except Exception as e:
                print(f"[Cảnh báo] Không thể bind IPv4 127.0.0.1: {e}")

            try:
                srv_v6 = await aiocoap.Context.create_server_context(root, bind=("::1", port))
                servers.append(srv_v6)
            except Exception as e:
                # Có thể một số máy tắt IPv6
                pass

        if not servers:
            print("[Lỗi] Không thể khởi động CoAP Server trên cổng đã chọn.")
            return

        print("CoAP Server", flush=True)
        print(f"CoAP Server started on port {port}", flush=True)
        print(f"URI: coap://localhost:{port}/iot/lab/message", flush=True)
        print("Nhan Ctrl+C de dung server.\n" + "-" * 40, flush=True)

        # Giữ server chạy vô hạn cho đến khi có tín hiệu dừng
        await asyncio.get_running_loop().create_future()

    except asyncio.CancelledError:
        pass
    finally:
        print("\nDang dung CoAP Server...")
        for srv in servers:
            await srv.shutdown()
        print("CoAP Server da dung.")


def main():
    parser = argparse.ArgumentParser(description="CoAP Server - Bai 1")
    parser.add_argument("--host", type=str, default=None, help="Dia chi IP can bind (mac dinh: 127.0.0.1 va ::1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP (mac dinh: 5683)")
    args = parser.parse_args()

    try:
        asyncio.run(start_server(host=args.host, port=args.port))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
