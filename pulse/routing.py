from django.urls import re_path
from pulse import consumers

websocket_urlpatterns = [
    re_path(r'ws/stream/$', consumers.PulseConsumer.as_asgi()),
]
