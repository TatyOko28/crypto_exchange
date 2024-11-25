from django.urls import path
from .views import NewsArticleViewSet

urlpatterns = [
    path('', NewsArticleViewSet.as_view({
        'get': 'list'
    }), name='news-list'),
    path('<int:pk>/', NewsArticleViewSet.as_view({
        'get': 'retrieve'
    }), name='news-detail'),
] 