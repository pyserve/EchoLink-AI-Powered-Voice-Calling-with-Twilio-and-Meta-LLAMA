from django.urls import path
from .consumers import AudioStreamConsumer

url_patterns = [
    path("audiostream/", AudioStreamConsumer.as_asgi())
]