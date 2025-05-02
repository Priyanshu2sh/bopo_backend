from django.urls import path
from .views import AwardPointsAPIView,  BankDetailByUserAPIView, CashOutCreateAPIView, CheckPointsAPIView, CorporateProjectListAPIView, CustomerCashOutAPIView, CustomerPointsForPrepaidMerchantsAPIView, CustomerToCustomerTransferAPIView, HelpAPIView, MerchantCashOutAPIView, MerchantCustomerPointsAPIView, MerchantToMerchantTransferAPIView, PaymentDetailsListCreateAPIView, PaymentDetailsRetrieveUpdateDestroyAPIView, RedeemPointsAPIView, HistoryAPIView, TransferPointsMerchantToCustomerAPIView, UpdateCustomerProfileAPIView, UpdateMerchantProfileAPIView, CustomerMerchantPointsAPIView, MerchantPointsAPIView

urlpatterns = [
    path('award/', AwardPointsAPIView.as_view(), name='award-points'),
    path('redeem/', RedeemPointsAPIView.as_view(), name='redeem-points'),
    # path('transaction-history/', HistoryAPIView.as_view(), name='transaction-history'),
    path('transaction-history/<str:id>/<str:user_type>', HistoryAPIView.as_view(), name='transaction-history-id'),
    path('customer-transfer/', CustomerToCustomerTransferAPIView.as_view(), name='customer-transfer'),
    path('merchant-transfer/', MerchantToMerchantTransferAPIView.as_view(), name='merchant-to-merchant-transfer'),
    path('check-points/<str:id>', CheckPointsAPIView.as_view(), name='check-points'),
    path('update-customer-profile/<str:customer_id>/', UpdateCustomerProfileAPIView.as_view(), name='update-customer-profile'),
    path('update-merchant-profile/<str:merchant_id>/', UpdateMerchantProfileAPIView.as_view(), name='update-merchant-profile'),
    path('customer/', CustomerMerchantPointsAPIView.as_view(), name='customer_merchant_points'),
    path('merchant/', MerchantCustomerPointsAPIView.as_view(), name='merchant_customer_points'),
    path('merchant/<str:merchant_id>/', MerchantPointsAPIView.as_view(), name='merchant_points'),

    path('payment-details/', PaymentDetailsListCreateAPIView.as_view(), name='payment-list-create'),
    path('payment-details/<str:merchant_id>/', PaymentDetailsRetrieveUpdateDestroyAPIView.as_view(), name='payment-detail'),


    path("customer/profile/<str:customer_id>/", UpdateCustomerProfileAPIView.as_view()),
    path("merchant/profile/<str:merchant_id>/", UpdateMerchantProfileAPIView.as_view()),


    path('bank-details/<str:id>/<str:user_type>/', BankDetailByUserAPIView.as_view(), name='bank-detail-by-user'),

    
    path('help/', HelpAPIView.as_view(), name='help-api'),
    path('corporate-projects/', CorporateProjectListAPIView.as_view(), name='corporate-projects'),
    
    path('terminal-transfer-points/', TransferPointsMerchantToCustomerAPIView.as_view(), name='transfer-points'),
    # GET API
    path('customer-points/prepaid-merchants/', CustomerPointsForPrepaidMerchantsAPIView.as_view(), name='customer_points_prepaid_merchants'),
    path('cashout/create/', CashOutCreateAPIView.as_view(), name='cashout-create'),
    
    path('customer/cashout/', CustomerCashOutAPIView.as_view(), name='customer-cashout'),
    path('api/merchant/cashout/', MerchantCashOutAPIView.as_view(), name='merchant-cashout'),
]


