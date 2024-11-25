from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('verify-email/', UserViewSet.as_view({'post': 'verify_email'}), name='verify-email'),
    path('security-code/set/', UserViewSet.as_view({'post': 'set_security_code'}), name='set-security-code'),
    path('upload-kyc/', UserViewSet.as_view({'post': 'upload_kyc'}), name='upload-kyc'),
    path('token/', UserViewSet.as_view({'post': 'token'}), name='token'),
    path('token/refresh/', UserViewSet.as_view({'post': 'token_refresh'}), name='token-refresh'),
] 