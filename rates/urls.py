from django.urls import path
from .views import ExchangeRateViewSet

urlpatterns = [
    path('', ExchangeRateViewSet.as_view({
        'get': 'list'
    }), name='exchange-rates'),
    path('websocket/', ExchangeRateViewSet.as_view({
        'get': 'websocket_info'
    }), name='exchange-rates-websocket'),
] 