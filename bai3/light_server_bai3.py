"""Bai 3 - Chuong trinh 1: Smart Light CoAP Server (light01).

Tai nguyen: coap://localhost:5683/iot/lab/light01/status
Ho tro: GET, PUT (ON/OFF) va Observe.
"""
import asyncio
import json
import sys
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code, Message

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DEVICE_ID = "light01"
JSON_FORMAT = 50  # application/json
LOG_FILE = "light_log.txt"


def log_change(old, new):
    """Mo rong: ghi nhat ky thay doi trang thai ra file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {DEVICE_ID}: {old} -> {new}\n")


class LightStatus(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.status = "OFF"  # trang thai ban dau

    def _state_payload(self):
        return json.dumps({"device_id": DEVICE_ID, "status": self.status}).encode()

    async def add_observation(self, request, serverobservation):
        print("New Observe registration received", flush=True)
        await super().add_observation(request, serverobservation)

    async def render_get(self, request):
        if request.opt.observe is None:  # bo qua log khi server tu dong gui thong bao Observe
            print("GET request received: /iot/lab/light01/status", flush=True)
        return Message(payload=self._state_payload(), content_format=JSON_FORMAT)

    async def render_put(self, request):
        # Doc va kiem tra payload
        try:
            data = json.loads(request.payload.decode("utf-8"))
            device = data["device_id"]
            command = str(data["command"]).upper()
        except (ValueError, KeyError, TypeError, UnicodeDecodeError):
            print("PUT request received: payload khong hop le", flush=True)
            return Message(code=Code.BAD_REQUEST, payload=b"Payload khong hop le")

        print("PUT request received:", flush=True)
        print(f"Device: {device}", flush=True)
        print(f"Command: {command}", flush=True)

        if device != DEVICE_ID:
            return Message(code=Code.NOT_FOUND,
                           payload=f"Khong co thiet bi {device}".encode())
        if command not in ("ON", "OFF"):
            return Message(code=Code.BAD_REQUEST,
                           payload=f"Lenh khong hop le: {command}".encode())

        word = "bat" if command == "ON" else "tat"
        if command != self.status:
            old = self.status
            self.status = command
            print(f"Light state changed: {old} -> {self.status}", flush=True)
            log_change(old, self.status)
            print(f"Notify observers: {self.status}", flush=True)
            self.updated_state()  # gui thong bao Observe toi tat ca client dang theo doi
            text = f"Da {word} den {DEVICE_ID}"
        else:
            print(f"Light state unchanged: {self.status}", flush=True)
            text = f"Den {DEVICE_ID} da o trang thai {self.status} san roi"
        return Message(code=Code.CHANGED, payload=text.encode("utf-8"))


async def main():
    root = resource.Site()
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )
    root.add_resource(["iot", "lab", "light01", "status"], LightStatus())

    if sys.platform == "win32":
        host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
        await aiocoap.Context.create_server_context(root, bind=(host, 5683))
    else:
        await aiocoap.Context.create_server_context(root)
    print("CoAP Smart Light Server started...", flush=True)
    print("Resource: /iot/lab/light01/status", flush=True)
    await asyncio.get_running_loop().create_future()  # chay mai mai


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")