from django.urls import path
from .views import  RegisterUserAPIView, LoginAPIView, VerifyOTPAPIView

urlpatterns = [
    # path('register-corporate/', RegisterCorporateAPIView.as_view(), name="register_corporate"),
    path('register-user/', RegisterUserAPIView.as_view(), name="register_merchant"),  
    path('login-user/', LoginAPIView.as_view(), name='login-user'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name="verify_otp"),

]
