from django.urls import path
from .views import CustomerPointsAPIView, RedeemAPIView, AwardAPIView

urlpatterns = [
    path('redeem/', RedeemAPIView.as_view(), name='redeem'),
    path('award/', AwardAPIView.as_view(), name='award'),
    path("customer-points/<str:customer_id>/", CustomerPointsAPIView.as_view(), name="customer-points"),
]
