from django.urls import path, include
from .views import edit_individual, home, about, merchant,customer, project_onboarding,merchant_list,add_customer,add_merchant,project_list,merchant_credentials,merchant_topup,map_bonus_points,merchant_limit_list,reduce_limit,merchant_status,login_page_info,send_notifications,received_offers,uploads,modify_customer_details,send_customer_notifications,customer_uploads,employee_list,add_employee,payment_details,employee_role,account_info,reports,corporate_list,individual_list,add_individual_merchant,get_states, get_cities,delete_employee
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('/login', views.login, name='login'),        
]
from .views import home, about, merchant, customer, project_onboarding,merchant_list

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('merchant/', merchant, name='merchant'),
    path('customer/', customer, name='customer'), 
    path('project_onboarding/', project_onboarding, name='project_onboarding'),
    path('merchant/list/', merchant_list, name='merchant_list'),
    path('corporate/list/', corporate_list, name='corporate_list'),
    path('individual/list/', individual_list, name='individual_list'),
    path('individual/edit/<int:id>/', edit_individual, name='edit_individual'),
    

    
    path('merchant/add/', add_merchant, name='add_merchant'),
    path("individual/add/", add_individual_merchant, name="add_individual_merchant"),
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
    path('reports/', reports, name='reports'),
    
    path('export-projects/', views.export_projects, name='export_projects'),
    path('export_merchants/', views.export_merchants, name='export_merchants'),
    path('export_disabled_merchants/', views.export_disabled_merchants, name='export_disabled_merchants'),
    path('export_project_wise_balance/', views.export_projects, name='export_project_wise_balance'),
    path('export_merchant_wise_balance/', views.export_merchant_wise_balance, name='export_merchant_wise_balance'),
    path('export_customer_wise_balance/', views.export_customer_wise_balance, name='export_customer_wise_balance'),
    path('export_customer_transaction/', views.export_customer_transaction, name='export_customer_transaction'),
    path('export_payment_dues/', views.export_projects, name='export_payment_dues'),
    path('export_award_transaction/', views.export_projects, name='export_award_transaction'),
    path('export_corporate_merchant/', views.export_projects, name='export_corporate_merchant'),
    path("get-merchant-details/", views.get_merchant_details, name="get_merchant_details"),
  
    
    path("get-states/", views.get_states, name="get_states"),
    path("get-cities/<int:state_id>/", views.get_cities, name="get_cities"),

    path('get-merchants/', views.get_merchants_by_project, name='get_merchants_by_project'),
    path('get-merchants/', views.get_merchants, name='get_merchants'),
    

    path('get-employee/<int:employee_id>/', views.get_employee, name='get_employee'),
    path('update-employee/', views.update_employee, name='update_employee'),
    path('delete-employee/<int:employee_id>/', delete_employee, name='delete_employee'),
    
  
# path('individual/edit/<int:id>/', views.edit_individual_merchant, name='edit_individual'),
# path('individual/delete/<int:id>/', views.delete_individual_merchant, name='delete_individual'),

    

    path("get-terminal-ids/", views.get_terminal_ids, name="get_terminal_ids"),

    path('get-payment-details/', views.get_payment_details, name='get_payment_details'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
