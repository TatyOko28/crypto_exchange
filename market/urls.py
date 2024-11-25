from django.urls import path
from .views import OrderViewSet, TransactionViewSet

urlpatterns = [
    # Order endpoints
    path('orders/', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('orders/<int:pk>/', OrderViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='order-detail'),
    path('orders/<int:pk>/execute/', OrderViewSet.as_view({'put': 'execute'}), name='order-execute'),
    
    # Transaction endpoints
    path('transactions/', TransactionViewSet.as_view({'get': 'list'}), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionViewSet.as_view({'get': 'retrieve'}), name='transaction-detail'),
] 