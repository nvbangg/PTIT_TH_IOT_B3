import argparse
import asyncio
import csv
from datetime import datetime
import json
import math
from pathlib import Path

import aiocoap

CSV_FIELDS = ["device_id", "temperature", "humidity", "timestamp", "received_at", "response_ms"]


def parse_data(response, device):
    if response.code != aiocoap.CONTENT:
        raise ValueError(f"CoAP {response.code}")
    if response.opt.content_format != 50:
        raise ValueError("Server khong tra ve application/json")
    data = json.loads(response.payload.decode("utf-8"))
    if not isinstance(data, dict) or data.get("device_id") != device:
        raise ValueError("Sai ma thiet bi")
    datetime.fromisoformat(data["timestamp"])
    for field in ("temperature", "humidity"):
        if type(data[field]) not in (int, float) or not math.isfinite(data[field]):
            raise ValueError(f"{field} khong hop le")
    return data


def display_data(data, received_at):
    temperature, humidity = data["temperature"], data["humidity"]
    print(f"[{received_at[11:19]}] Received sensor data")
    print(f"Device: {data['device_id']}")
    print(f"Temperature: {temperature} C")
    print(f"Humidity: {humidity} %")
    print(f"Timestamp: {data['timestamp']}")
    if temperature > 35:
        print("CANH BAO: Nhiet do cao")
    if humidity < 40:
        print("CANH BAO: Do am thap")
    if temperature <= 35 and humidity >= 40:
        print("Trang thai: Binh thuong")


def display_stats(get_count, response_count, total_ms):
    average = f"{total_ms / response_count:.3f} ms" if response_count else "N/A"
    print(f"GET: {get_count} | Responses: {response_count} | Avg response: {average}")


async def main(device="sensor01"):
    output = Path(__file__).with_name("sensor_data.csv")
    context = await aiocoap.Context.create_client_context(transports=["simple6"])
    uri = f"coap://127.0.0.1:5683/iot/lab/{device}/data"
    get_count = response_count = 0
    total_ms = 0.0
    loop = asyncio.get_running_loop()
    try:
        with output.open("a+", newline="", encoding="utf-8") as logfile:
            logfile.seek(0)
            header = next(csv.reader(logfile), None)
            if header is not None and header != CSV_FIELDS:
                raise ValueError("CSV da ton tai nhung khong dung dinh dang")
            if header is not None:
                with output.open("rb") as existing:
                    existing.seek(-1, 2)
                    if existing.read(1) not in (b"\n", b"\r"):
                        logfile.write("\n")
            logfile.seek(0, 2)
            writer = csv.writer(logfile)
            if header is None:
                writer.writerow(CSV_FIELDS)
                logfile.flush()
            print(f"Monitoring: {uri}")
            print(f"CSV: {output}")
            while True:
                request = aiocoap.Message(code=aiocoap.GET, uri=uri)
                started = loop.time()
                get_count += 1
                try:
                    response = await asyncio.wait_for(
                        context.request(request).response, timeout=5
                    )
                    response_ms = (loop.time() - started) * 1000
                    response_count += 1
                    total_ms += response_ms
                    received_at = datetime.now().astimezone().isoformat(timespec="seconds")
                    data = parse_data(response, device)
                except asyncio.TimeoutError:
                    print("Loi: Server khong phan hoi sau 5 giay")
                except (aiocoap.error.Error, OSError) as error:
                    print(f"Loi ket noi: {error}")
                except (ValueError, KeyError, TypeError) as error:
                    print(f"Loi du lieu: {error}")
                else:
                    writer.writerow([data[field] for field in CSV_FIELDS[:4]]
                                    + [received_at, round(response_ms, 3)])
                    logfile.flush()
                    display_data(data, received_at)
                display_stats(get_count, response_count, total_ms)
                print("-" * 30)
                await asyncio.sleep(max(0, 3 - (loop.time() - started)))
    finally:
        print("Tong ket:")
        display_stats(get_count, response_count, total_ms)
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Giam sat cam bien CoAP va luu CSV")
    parser.add_argument("--device", choices=["sensor01", "sensor02", "sensor03"], default="sensor01")
    args = parser.parse_args()
    try:
        asyncio.run(main(args.device))
    except KeyboardInterrupt:
        print("\nKet thuc Monitoring Client")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Loi: {error}\n")
