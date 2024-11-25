from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from market.views import OrderViewSet, TransactionViewSet
from wallet.views import WalletViewSet
from rates.views import ExchangeRateViewSet
from news.views import NewsArticleViewSet
from support.views import SupportTicketViewSet
from .views import HomeView

schema_view = get_schema_view(
    openapi.Info(
        title="Crypto Exchange API",
        default_version='v1',
        description="API complète pour la plateforme d'échange de cryptomonnaies",
        terms_of_service="https://www.cryptoexchange.com/terms/",
        contact=openapi.Contact(email="contact@cryptoexchange.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'rates', ExchangeRateViewSet, basename='rate')
router.register(r'news', NewsArticleViewSet, basename='news')
router.register(r'support', SupportTicketViewSet, basename='support')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('authentication.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    path('api/v1/rates/', include('rates.urls')),
    path('api/v1/news/', include('news.urls')),
    path('api/v1/orders/', include('market.urls')),
    path('api/v1/wallet/', include('wallet.urls')),
    path('', HomeView.as_view(), name='home'),
]
