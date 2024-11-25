from django.urls import path
from .views import WalletViewSet, WalletTransactionViewSet

urlpatterns = [
    # Wallet endpoints
    path('', WalletViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    }), name='wallet-detail'),
    
    # Wallet transactions
    path('transactions/', WalletTransactionViewSet.as_view({
        'get': 'list'
    }), name='wallet-transactions'),
] 