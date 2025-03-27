from django.urls import path
from .views import CustomerToCustomerAPIView, MerchantToMerchantAPIView

urlpatterns = [
    path('customer-to-customer/', CustomerToCustomerAPIView.as_view(), name='customer-to-customer'),
    path('merchant-to-merchant/', MerchantToMerchantAPIView.as_view(), name='merchant-to-merchant'),
]
