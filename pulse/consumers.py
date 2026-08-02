from channels.generic.websocket import AsyncWebsocketConsumer
import json
from pulse.ml_brain import predict

class PulseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("[WS] Client connected")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[WS] Client disconnected: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            value = data.get("value")
            print(f"[WS] Received: {value}")

            prediction = predict(value)
            is_anomaly = prediction == -1

            response = {
                "value": value,
                "is_anomaly": is_anomaly
            }
            print(f"[ML] {value} -> {'Anomaly' if is_anomaly else 'Normal'}")

            await self.send(text_data=json.dumps(response))

        except json.JSONDecodeError:
            print(f"[WS] Invalid JSON: {text_data}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
