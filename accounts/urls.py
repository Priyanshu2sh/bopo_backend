from django.urls import path
from .views import CreateTerminalAPIView, RegisterUserAPIView, LoginAPIView, RequestMobileChangeAPIView, RequestPinChangeAPIView,  VerifyMobileChangeAPIView, VerifyOTPAPIView, FetchAllUsersAPIView, VerifyPinChangeAPIView, VerifySecurityQuestionAPIView

urlpatterns = [
    # path('register-corporate/', RegisterCorporateAPIView.as_view(), name="register_corporate"),
    path('create-terminal/', CreateTerminalAPIView.as_view(), name='create-terminal'),
    path('register-user/', RegisterUserAPIView.as_view(), name="register_merchant"),  
    path('customers/', RegisterUserAPIView.as_view(), name='customer-list'),
    path('login-user/', LoginAPIView.as_view(), name='login-user'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name="verify_otp"),
    path('fetch-users/', FetchAllUsersAPIView.as_view(), name='fetch-users'),

    path('request-mobile-change/', RequestMobileChangeAPIView.as_view(), name='request-mobile-change'),
    path('verify-mobile-change/', VerifyMobileChangeAPIView.as_view(), name='verify-mobile-change'),
    path('request-pin-change/',RequestPinChangeAPIView.as_view(), name='request-pin-change'),
    path('verify-pin-otp/', VerifyPinChangeAPIView.as_view(), name='verify-pin-otp'),
    path('verify-pin-security/', VerifySecurityQuestionAPIView.as_view(), name='verify-pin-security'),
    

    # path('security-question/', SecurityQueAPIView.as_view(), name='add_security_question'),
    # path('security-question/<int:id>/', SecurityQueAPIView.as_view(), name='get_security_question_by_id'),
]
