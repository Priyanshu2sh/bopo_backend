from django.urls import path
from .views import RegisterUserAPIView, LoginAPIView, VerifyOTPAPIView, FetchAllUsersAPIView

urlpatterns = [
    # path('register-corporate/', RegisterCorporateAPIView.as_view(), name="register_corporate"),
    path('register-user/', RegisterUserAPIView.as_view(), name="register_merchant"),  
    path('customers/', RegisterUserAPIView.as_view(), name='customer-list'),
    path('login-user/', LoginAPIView.as_view(), name='login-user'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name="verify_otp"),
    path('fetch-users/', FetchAllUsersAPIView.as_view(), name='fetch-users'),
]
