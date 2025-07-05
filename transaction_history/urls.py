from django.urls import path
from .views import TransactionHistoryView

urlpatterns = [
    path('transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
]
