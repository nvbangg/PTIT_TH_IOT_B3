"""Bai 3 - Chuong trinh 2: Light Controller Client.

Lenh: ON, OFF, STATUS, EXIT
Cach chay: python light_controller_bai3.py [dia_chi_server]
"""
import asyncio
import json
import sys

import aiocoap
from aiocoap import Code, Message
from aiocoap.error import Error as CoapError

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
URI = f"coap://{HOST}:5683/iot/lab/light01/status"
JSON_FORMAT = 50
TIMEOUT = 5  # giay


async def send(ctx, request):
    """Gui request, tra ve response hoac None neu loi/timeout."""
    try:
        return await asyncio.wait_for(ctx.request(request).response, TIMEOUT)
    except asyncio.TimeoutError:
        print(f"Loi: Server khong phan hoi sau {TIMEOUT}s (timeout).")
    except (CoapError, OSError) as e:
        print(f"Loi giao tiep: {e!r}")
    return None


async def main():
    ctx = await aiocoap.Context.create_client_context()
    print(f"Light Controller - Server: {URI}")

    while True:
        cmd = await asyncio.to_thread(input, "Nhap lenh (ON/OFF/STATUS/EXIT): ")
        cmd = cmd.strip().upper()

        if cmd == "EXIT":
            print("Tam biet!")
            break

        if cmd in ("ON", "OFF"):
            print("Sending PUT request...")
            payload = json.dumps({"device_id": "light01", "command": cmd}).encode()
            req = Message(code=Code.PUT, uri=URI, payload=payload,
                          content_format=JSON_FORMAT)
            resp = await send(ctx, req)
            if resp:
                print(f"Response Code: {resp.code}")
                print(resp.payload.decode("utf-8", "replace"))

        elif cmd == "STATUS":
            print("Sending GET request...")
            resp = await send(ctx, Message(code=Code.GET, uri=URI))
            if resp:
                print("Response:")
                print(resp.payload.decode("utf-8", "replace"))

        else:
            print("Lenh khong hop le. Chi chap nhan: ON, OFF, STATUS, EXIT")

    await ctx.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nExit.")
