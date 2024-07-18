from django.contrib import admin
from django.urls import path
from .views import InboundCalls, OutboundsCalls
from .consumers import AudioStreamConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("inbounds/", InboundCalls.as_view(), name="incoming_calls"),
    path("outbounds/<int:id>", OutboundsCalls.as_view(), name="outgoing_calls"),
]
