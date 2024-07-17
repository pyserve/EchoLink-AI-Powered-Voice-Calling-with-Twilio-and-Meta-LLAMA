from django.contrib import admin
from django.urls import path
from .views import IncomingCallHandler, IncomingCallProcessor, OutgoingCallHandler, OutgoingCallProcessor
from .consumers import AudioStreamConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("inbounds/", IncomingCallHandler, name="incoming_calls"),
    path("inbounds-process/", IncomingCallProcessor, name="incoming_processor"),
    path("outbounds/<int:id>", OutgoingCallHandler, name="outgoing_calls"),
    path("outbounds-process/", OutgoingCallProcessor, name="outgoing_processor"),
]
