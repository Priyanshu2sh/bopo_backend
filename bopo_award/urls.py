# from django.urls import path
# from .views import CustomerPointsAPIView, RedeemAPIView, AwardAPIView

# urlpatterns = [
#     path('redeem/', RedeemAPIView.as_view(), name='redeem'),
#     path('award/', AwardAPIView.as_view(), name='award'),
#     path("customer-points/<str:customer_id>/", CustomerPointsAPIView.as_view(), name="customer-points"),
# ]



from django.urls import path
from .views import AwardPointsAPIView, CheckPointsAPIView, CustomerToCustomerTransferAPIView, MerchantToMerchantTransferAPIView, RedeemPointsAPIView, HistoryAPIView, UpdateCustomerProfileAPIView, UpdateMerchantProfileAPIView

urlpatterns = [
    path('award/', AwardPointsAPIView.as_view(), name='award-points'),
    path('redeem/', RedeemPointsAPIView.as_view(), name='redeem-points'),
    path('transaction-history/', HistoryAPIView.as_view(), name='transaction-history'),
    path('transaction-history/<str:id>/<str:user_type>', HistoryAPIView.as_view(), name='transaction-history-id'),
    path('customer-transfer/', CustomerToCustomerTransferAPIView.as_view(), name='customer-transfer'),
    path('merchant-transfer/', MerchantToMerchantTransferAPIView.as_view(), name='merchant-to-merchant-transfer'),
    path('check-points/<str:id>', CheckPointsAPIView.as_view(), name='check-points'),
    path('update-customer-profile/<str:customer_id>/', UpdateCustomerProfileAPIView.as_view(), name='update-customer-profile'),
    path('update-merchant-profile/<str:merchant_id>/', UpdateMerchantProfileAPIView.as_view(), name='update-merchant-profile'),


]


