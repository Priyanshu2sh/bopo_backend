from django.urls import path, include
from .views import home, about, merchant,customer, project_onboarding,merchant_list,add_merchant,project_list,merchant_credentials,merchant_topup,map_bonus_points,merchant_limit_list,reduce_limit,merchant_status,login_page_info,send_notifications,received_offers,uploads,modify_customer_details,send_customer_notifications,customer_uploads,add_customer,employee_list,add_employee,payment_details,employee_role,account_info

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('merchant/', merchant, name='merchant'),
    path('customer/', customer, name='customer'), 
    path('project_onboarding/', project_onboarding, name='project_onboarding'),
    path('merchant/list/', merchant_list, name='merchant_list'),
    path('merchant/add/', add_merchant, name='add_merchant'),
    path('project/list', project_list, name='project_list'),
    path('merchant_credentials/', merchant_credentials, name='merchant_credentials'),
    path('merchant-topup/', merchant_topup, name='merchant_topup'),
    
    path('map_bonus_points/', map_bonus_points, name='map_bonus_points'),
    path('merchant_limit_list/', merchant_limit_list, name='merchant_limit_list'),
    path('reduce_limit/', reduce_limit, name='reduce_limit'),
    path('merchant_status/', merchant_status, name='merchant_status'),
    path('login_page_info/', login_page_info, name='login_page_info'),
    path('send-notifications/', send_notifications, name='send_notifications'),
    path('received-offers/', received_offers, name='received_offers'),
    path('uploads/', uploads, name='uploads'),
    
    path('modify_customer_details/',modify_customer_details, name='modify_customer_details'),
    path('send_customer_notifications/',send_customer_notifications, name='send_customer_notifications'),
    path('customer_uploads/',customer_uploads, name='customer_uploads'),
    path('add_customer/',add_customer, name='add_customer'),
    
    path('employee_list/',employee_list, name='employee_list'),
    path('employees/add/', add_employee, name='add_employee'),
    path('employee-role/',employee_role, name='employee_role'),
    
    path('payment_details/', payment_details, name='payment_details'),
    path('account_info/', account_info, name='account_info'),
    
    
   


  
]
