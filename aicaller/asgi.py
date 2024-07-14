import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from .consumers import AudioStreamConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aicaller.settings")

django_asgi_app = get_asgi_application()

# using multiple routing protocols.
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("audiostream/", AudioStreamConsumer.as_asgi()),
        ])
    )
})

'''
To use multiple routing protocols in your application. For example:
real time streaming app needs websockets to access the real time data.
Before using, need to install channels and daphne: pip install -U channels['daphne']

step1: Make changes in settings.py, 
    WSGI_APPLICATION = "aicaller.asgi.application",
    INSTALLED_APPS = [..., 'channels']
    
Step2: Run command: daphne -p 8000 aicaller.asgi:application
'''