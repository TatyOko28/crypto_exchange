from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from rates.consumers import RatesConsumer

websocket_urlpatterns = [
    re_path(r'ws/rates/$', RatesConsumer.as_asgi()),
] 