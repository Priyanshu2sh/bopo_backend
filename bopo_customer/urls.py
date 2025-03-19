from django.urls import path
from .views import customer_uploads, send_customer_notifications, modify_customer_details

urlpatterns = [
    path('modify_customer_details/', modify_customer_details, name='modify_customer_details'),  # Add this line
    path('send_customer_notifications/', send_customer_notifications, name='send_customer_notifications'),
    path('customer_uploads/', customer_uploads, name='customer_uploads'),
]
