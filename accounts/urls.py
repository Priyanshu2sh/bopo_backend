from django.urls import path
from .views import RegisterAPIView, OTPVerifyAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-otp/', OTPVerifyAPIView.as_view(), name='verify-otp'),
]
