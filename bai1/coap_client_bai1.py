"""
Chương trình 2: CoAP Client - Bài 1
Mô tả: Kết nối tới CoAP Server, thực hiện yêu cầu GET và POST
- GET: Nhận thông điệp chào mừng từ Server
- POST: Gửi thông điệp chứa Họ tên sinh viên, Mã sinh viên, Lời chào
- Gợi ý mở rộng:
  + Gửi nhiều thông điệp POST liên tiếp (interactive mode)
  + Xử lý lỗi timeout khi Server không hoạt động
  + Xử lý lỗi tài nguyên không tồn tại (4.04 Not Found)
"""

import sys
import asyncio
import argparse
import aiocoap

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def send_get(context, uri: str):
    """Gửi yêu cầu GET tới URI chỉ định"""
    print("Sending GET request...", flush=True)
    print(f"URI: {uri}", flush=True)
    try:
        request = aiocoap.Message(code=aiocoap.GET, uri=uri)
        response = await asyncio.wait_for(context.request(request).response, timeout=5.0)
        print("Response:", flush=True)
        print(f"Code: {response.code}", flush=True)
        print(f"Payload: {response.payload.decode('utf-8', errors='replace')}", flush=True)
        return response
    except asyncio.TimeoutError:
        print("[Loi] Yeu cau GET bi timeout - Server khong phan hoi.", flush=True)
    except Exception as e:
        print(f"[Loi] Gui GET that bai: {e}", flush=True)
    return None


async def send_post(context, uri: str, payload_text: str):
    """Gửi yêu cầu POST tới URI chỉ định"""
    print("Sending POST request...", flush=True)
    print(f"Payload: {payload_text}", flush=True)
    try:
        request = aiocoap.Message(
            code=aiocoap.POST,
            uri=uri,
            payload=payload_text.encode("utf-8")
        )
        response = await asyncio.wait_for(context.request(request).response, timeout=5.0)
        print("Response:", flush=True)
        print(f"Code: {response.code}", flush=True)
        print(f"Payload: {response.payload.decode('utf-8', errors='replace')}", flush=True)
        return response
    except asyncio.TimeoutError:
        print("[Loi] Yeu cau POST bi timeout - Server khong phan hoi.", flush=True)
    except Exception as e:
        print(f"[Loi] Gui POST that bai: {e}", flush=True)
    return None


async def run_client(host: str, port: int, student_name: str, student_id: str, interactive: bool, test_not_found: bool):
    base_uri = f"coap://{host}:{port}/iot/lab/message"

    print("CoAP Client", flush=True)
    try:
        context = await aiocoap.Context.create_client_context()
    except Exception as e:
        print(f"[Loi] Khong the tao Client context: {e}", flush=True)
        return

    try:
        # 1. Thực hiện yêu cầu GET
        await send_get(context, base_uri)
        print("-" * 40, flush=True)

        # 2. Thực hiện yêu cầu POST
        default_payload = f"Xin chao tu CoAP Client - {student_id} - {student_name}"
        await send_post(context, base_uri, default_payload)
        print("-" * 40, flush=True)

        # 3. Mở rộng: Kiểm tra thử nghiệm tài nguyên không tồn tại nếu được yêu cầu
        if test_not_found:
            not_found_uri = f"coap://{host}:{port}/iot/lab/invalid_path"
            print("[Kiem tra mo rong] Gui GET toi tai nguyen khong ton tai:", flush=True)
            await send_get(context, not_found_uri)
            print("-" * 40, flush=True)

        # 4. Mở rộng: Chế độ tương tác gửi nhiều thông điệp POST
        if interactive:
            print("\n[Che do mo rong] Nhap thong diep POST gui lien tiep (hoac go 'exit' de thoat):", flush=True)
            loop = asyncio.get_running_loop()
            while True:
                msg = await loop.run_in_executor(None, input, "Nhap noi dung POST: ")
                msg = msg.strip()
                if not msg or msg.lower() == "exit":
                    break
                await send_post(context, base_uri, msg)
                print("Kiem tra lai du lieu tren Server qua GET:", flush=True)
                await send_get(context, base_uri)
                print("-" * 40, flush=True)

    finally:
        await context.shutdown()


def main():
    parser = argparse.ArgumentParser(description="CoAP Client - Bai 1")
    parser.add_argument("--host", type=str, default="localhost", help="Dia chi CoAP Server (mac dinh: localhost)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP Server (mac dinh: 5683)")
    parser.add_argument("--name", type=str, default="Nguyen Van A", help="Ho ten sinh vien")
    parser.add_argument("--id", type=str, default="B23DCCN001", help="Ma sinh vien")
    parser.add_argument("--interactive", action="store_true", help="Bat che do gui nhieu message lien tiep")
    parser.add_argument("--test-not-found", action="store_true", help="Kiem tra truy cap tai nguyen khong ton tai")
    args = parser.parse_args()

    try:
        asyncio.run(
            run_client(
                host=args.host,
                port=args.port,
                student_name=args.name,
                student_id=args.id,
                interactive=args.interactive,
                test_not_found=args.test_not_found
            )
        )
    except KeyboardInterrupt:
        print("\nClient da dung.")


if __name__ == "__main__":
    main()
