import asyncio
from datetime import datetime
import json
import random

import aiocoap
from aiocoap import resource


class SensorResource(resource.Resource):
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.update()

    def update(self):
        self.data = {
            "device_id": self.device_id,
            "temperature": round(random.uniform(20, 40), 1),
            "humidity": round(random.uniform(30, 80), 1),
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        }

    async def render_get(self, request):
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=json.dumps(self.data).encode("utf-8"),
            content_format=50,  # application/json
            max_age=3,
        )


async def main():
    sensors = [SensorResource(f"sensor{number:02}") for number in range(1, 4)]
    site = resource.Site()
    for sensor in sensors:
        site.add_resource(["iot", "lab", sensor.device_id, "data"], sensor)
    context = await aiocoap.Context.create_server_context(
        site, bind=("127.0.0.1", 5683), transports=["simplesocketserver"]
    )
    print("Sensor Server: coap://127.0.0.1:5683/iot/lab/{sensor01,sensor02,sensor03}/data")
    try:
        while True:
            for sensor in sensors:
                print("Sensor data:", json.dumps(sensor.data))
            await asyncio.sleep(3)
            for sensor in sensors:
                sensor.update()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKet thuc Sensor Server")
