import random
import time
import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Install websockets: pip install websockets")
    sys.exit(1)

WS_URL = "ws://localhost:8000/ws/stream/"
chaos_mode = False

async def send_data():
    global chaos_mode

    async with websockets.connect(WS_URL) as ws:
        print(f"Connected to {WS_URL}")
        print("Type 'chaos' + Enter to trigger a spike")
        print("-" * 40)

        while True:
            if chaos_mode:
                temp = 95.0
            else:
                temp = round(random.uniform(40.0, 50.0), 2)

            data = {"value": temp}
            await ws.send(json.dumps(data))

            response = await ws.recv()
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Sent: {temp} | Response: {response}")

            await asyncio.sleep(1)

def keyboard_listener():
    global chaos_mode
    while True:
        user_input = sys.stdin.readline().strip().lower()
        if user_input == 'chaos':
            chaos_mode = True
            print("[CHAOS] Spike triggered! Temp jumping to 95.0")
            time.sleep(3)
            chaos_mode = False
            print("[CHAOS] Normal mode resumed")

if __name__ == "__main__":
    import threading
    listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
    listener_thread.start()

    print("Data Generator Started")
    asyncio.run(send_data())
