from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from pulse.ml_brain import predict
from pulse.models import AnomalyEvent


@sync_to_async
def save_anomaly(value, severity):
    AnomalyEvent.objects.create(
        sensor_reading=value,
        severity_score=severity
    )


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

            if is_anomaly:
                severity = int((value - 50) / 5)
                await save_anomaly(value, severity)
                print(f"[DB] Saved anomaly: {value}°C (severity: {severity})")

            response = {
                "value": value,
                "is_anomaly": is_anomaly
            }
            print(f"[ML] {value} -> {'Anomaly' if is_anomaly else 'Normal'}")

            await self.send(text_data=json.dumps(response))

        except json.JSONDecodeError:
            print(f"[WS] Invalid JSON: {text_data}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
