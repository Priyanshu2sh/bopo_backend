from django.urls import path
from .views import NotificationListAPIView, cron_trigger_global_point_deduction

from .views import AwardPointsAPIView,  BankDetailByUserAPIView, CashOutCreateAPIView, CheckPointsAPIView, CorporateGlobalMerchantAPIView, CorporateProjectListAPIView, CorporateRedeemAPIView, CustomerCashOutAPIView, CustomerPointsForPrepaidMerchantsAPIView, CustomerToCustomerTransferAPIView, GetGlobalCustomerPointsAPIView, GetPrepaidMerchantAPIView, GlobalRedeemPointsAPIView, HelpAPIView, MerchantCashOutAPIView, MerchantCustomerPointsAPIView, MerchantToMerchantTransferAPIView, PaymentDetailsListCreateAPIView, PaymentDetailsRetrieveUpdateDestroyAPIView, RedeemPointsAPIView, HistoryAPIView, SecurityQuestionAPIView, TerminalCustomerPointsAPIView, TransferPointsMerchantToCustomerAPIView, UpdateCustomerProfileAPIView, UpdateMerchantProfileAPIView, CustomerMerchantPointsAPIView, MerchantPointsAPIView, cron_trigger_global_point_deduction

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
     path('terminal-customer-points/', TerminalCustomerPointsAPIView.as_view(), name='terminal-customer-points'),

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
    
    path('corporate/redeem/', CorporateRedeemAPIView.as_view(), name='corporate-redeem'),
    
    path("global-redeem/", GlobalRedeemPointsAPIView.as_view(), name="global-redeem"),
    path('get-GlobalCustomerPoints/', GetGlobalCustomerPointsAPIView.as_view(), name='get_global_customer_points'),
    path('getPrepaidMerchants/', GetPrepaidMerchantAPIView.as_view(), name='get_prepaid_merchants'),
    path('get-sequerity-ques/', SecurityQuestionAPIView.as_view(), name='get_sequerity_ques'),
    path('get-corporate-global-merchant/', CorporateGlobalMerchantAPIView.as_view(), name='get_corporate_global_merchant'),
    
    path('get-history/', HistoryAPIView.as_view(), name='get-history-id'),
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    
     path('cron-deduct-global/', cron_trigger_global_point_deduction, name='cron_deduct_global'),
    
    
]


