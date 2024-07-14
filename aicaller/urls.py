from django.contrib import admin
from django.urls import path
from .views import VoiceHandler, VoiceProcesser
from .consumers import AudioStreamConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("voice/", VoiceHandler, name="voice"),
    path("process/", VoiceProcesser, name="processor"),
]
