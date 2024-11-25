from django.urls import path
from .views import SupportTicketViewSet

urlpatterns = [
    path('tickets/', SupportTicketViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='support-tickets'),
    path('tickets/<int:pk>/', SupportTicketViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    }), name='support-ticket-detail'),
    path('tickets/<int:pk>/respond/', SupportTicketViewSet.as_view({
        'post': 'respond'
    }), name='support-ticket-respond'),
] 