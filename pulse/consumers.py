from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PulseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("[WS] Client connected")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[WS] Client disconnected: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(f"[WS] Received: {data}")

            response = {
                "value": data.get("value"),
                "status": "received"
            }
            await self.send(text_data=json.dumps(response))

        except json.JSONDecodeError:
            print(f"[WS] Invalid JSON: {text_data}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
