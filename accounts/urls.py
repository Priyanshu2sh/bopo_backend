from django.urls import path
from .views import RegisterUser, VerifyOTP

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
]
