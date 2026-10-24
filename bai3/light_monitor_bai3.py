"""Bai 3 - Chuong trinh 3: Light Monitoring Client (CoAP Observe).

Dang ky Observe, KHONG dung vong lap GET dinh ky.
Cach chay: python light_monitor_bai3.py [dia_chi_server]  (Ctrl+C de thoat)
"""
import asyncio
import json
import sys
from datetime import datetime

import aiocoap
from aiocoap import Code, Message
from aiocoap.error import Error as CoapError

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
URI = f"coap://{HOST}:5683/iot/lab/light01/status"
TIMEOUT = 5


def show(title, response):
    now = datetime.now().strftime("%H:%M:%S")
    try:
        data = json.loads(response.payload.decode("utf-8"))
        device, status = data["device_id"], data["status"]
    except (ValueError, KeyError):
        print(f"[{now}] Payload khong hop le: {response.payload!r}", flush=True)
        return
    print(f"[{now}] {title}", flush=True)
    print(f"Device: {device}", flush=True)
    print(f"Status: {status}", flush=True)


async def main():
    ctx = await aiocoap.Context.create_client_context()
    print("Registering CoAP Observe...", flush=True)

    request = Message(code=Code.GET, uri=URI, observe=0)  # observe=0 -> dang ky
    pr = ctx.request(request)

    try:
        first = await asyncio.wait_for(pr.response, TIMEOUT)
    except asyncio.TimeoutError:
        print(f"Loi: Server khong phan hoi sau {TIMEOUT}s (timeout).")
        return
    except (CoapError, OSError) as e:
        print(f"Loi ket noi: {e!r}")
        return

    print("Observe registration successful", flush=True)
    show("Initial State", first)

    # Cho server tu day thong bao moi khi trang thai thay doi
    try:
        async for notification in pr.observation:
            show("State Updated", notification)
    except CoapError as e:
        print(f"Observe bi ngat: {e!r}")
    else:
        print("Server ket thuc Observe.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung giam sat.")
