from django.urls import path
from .views import RegisterCorporateAPIView, RegisterMerchantAPIView, RegisterTerminalAPIView, UserLoginAPIView, VerifyOTPAPIView

urlpatterns = [
    path('register-corporate/', RegisterCorporateAPIView.as_view(), name="register_corporate"),
    path('register-merchant/', RegisterMerchantAPIView.as_view(), name="register_merchant"),
    path('register-terminal/', RegisterTerminalAPIView.as_view(), name='register-terminal'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name="verify_otp"),
]
