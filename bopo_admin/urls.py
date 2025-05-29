from django.urls import path, include

from bopo_admin.forms import CustomPasswordResetForm
from .views import  CustomPasswordResetCompleteView, CustomPasswordResetConfirmView, create_notification_view, add_security_question, assign_employee_role, corporate_add_merchant, custom_logout_view, delete_security_question,  home, about, merchant,customer, project_onboarding,merchant_list,add_customer,add_merchant,project_list,merchant_credentials,merchant_topup,map_bonus_points,merchant_limit_list,reduce_limit,merchant_status,login_page_info, save_deduct_settings, save_superadmin_payment, security_questions_view,send_notifications,received_offers, toggle_status, update_security_question,uploads,modify_customer_details,send_customer_notifications,customer_uploads,employee_list,add_employee,payment_details,account_info,reports,corporate_list,individual_list,add_individual_merchant,get_states, get_cities,get_employee,delete_employee,edit_merchants,delete_merchant
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


# urlpatterns = [
    # path('/login', views.login, name='login'),        
# ]
from .views import home, about, merchant, customer, project_onboarding,merchant_list ,CustomPasswordResetView

urlpatterns = [
    # NEW (correct)
    path('login/', views.login_view, name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('merchant/', merchant, name='merchant'),
    path('customer/', customer, name='customer'), 
    path('project_onboarding/', project_onboarding, name='project_onboarding'),
    path('merchant/list/', merchant_list, name='merchant_list'),
    path('corporate/list/', corporate_list, name='corporate_list'),
    path('individual/list/', individual_list, name='individual_list'),
    
    

    
    path('merchant/add/', add_merchant, name='add_merchant'),
    path("individual/add/", add_individual_merchant, name="add_individual_merchant"),
    path('project/list', project_list, name='project_list'),
    path('merchant_credentials/', merchant_credentials, name='merchant_credentials'),
    path('merchant-topup/', merchant_topup, name='merchant_topup'),
    path('get-corporate-admin/', views.get_corporate_admin, name='get_corporate_admin'),

    path('map_bonus_points/', map_bonus_points, name='map_bonus_points'),
    path('merchant_limit_list/', merchant_limit_list, name='merchant_limit_list'),
    path('reduce_limit/', reduce_limit, name='reduce_limit'),
    path('merchant_status/', merchant_status, name='merchant_status'),
    path('login_page_info/', login_page_info, name='login_page_info'),
    path('send-notifications/', send_notifications, name='send_notifications'),
    path('received-offers/', received_offers, name='received_offers'),
    path('uploads/', uploads, name='uploads'),
    
    path('modify_customer_details/',modify_customer_details, name='modify_customer_details'),
    path('customer_uploads/',customer_uploads, name='customer_uploads'),
    path('add_customer/',add_customer, name='add_customer'),
    
    path('employee_list/',employee_list, name='employee_list'),
    path('employees/add/', add_employee, name='add_employee'),
    path('employee-role/',assign_employee_role, name='employee_role'),
    path('get-employee-roles/', views.get_employee_roles, name='get_employee_roles'),


    
    path('payment_details/', payment_details, name='payment_details'),
    path('account_info/', account_info, name='account_info'),
    path('reports/', reports, name='reports'),
    
    path('export-projects/', views.export_projects, name='export_projects'),
    path('export_merchants/', views.export_merchants, name='export_merchants'),
    path('export_disabled_merchants/', views.export_disabled_merchants, name='export_disabled_merchants'),
    path('export_project_wise_balance/', views.export_project_wise_balance, name='export_project_wise_balance'),
    path('export_merchant_wise_balance/', views.export_merchant_wise_balance, name='export_merchant_wise_balance'),
    path('export_customer_wise_balance/', views.export_customer_wise_balance, name='export_customer_wise_balance'),
    path('export_customer_transaction/', views.export_customer_transaction, name='export_customer_transaction'),
    path('export_payment_dues/', views.export_payment_dues, name='export_payment_dues'),
    path('export_award_transaction/', views.export_projects, name='export_award_transaction'),
    path('export_corporate_merchant/', views.export_projects, name='export_corporate_merchant'),
    path("get-merchant-details/", views.get_merchant_details, name="get_merchant_details"),
  
    
    path("get-states/", views.get_states, name="get_states"),
    path("get-cities/<int:state_id>/", views.get_cities, name="get_cities"),

    path('get-merchants/', views.get_merchants_by_project, name='get_merchants_by_project'),
    path('get-merchants/', views.get_merchants, name='get_merchants'),
    path('get-individual-merchants/', views.get_individual_merchants, name='get_individual_merchants'),

    

    path('get-employee/<str:employee_id>/', views.get_employee, name='get_employee'),
    path('update-employee/', views.update_employee, name='update_employee'),
    path('delete-employee/<str:employee_id>/', delete_employee, name='delete_employee'),
    
    path('edit-merchants/<int:merchant_id>/', views.edit_merchants, name='edit_merchants'),
    path('update-merchant/', views.update_merchant, name='update_merchant'),
    path('delete-merchant/<int:merchant_id>/', views.delete_merchant, name='delete_merchant'),
    
    
       
    # path('edit-copmerchant/<int:merchant_id>/', views.edit_copmerchant, name='edit_copmerchant'),
    path('get-corporate/<str:corporate_id>/', views.get_corporate, name='get_corporate'),
    path('get-copmerchant/<str:merchant_id>/', views.get_copmerchant, name='get_copmerchant'),
    path('update-corporate/<str:corporate_id>/', views.update_corporate, name='update_corporate'),
    path('update-copmerchant/<int:merchant_id>/', views.update_copmerchant, name='update_copmerchant'),

       
    
    
    # path('corporate_admin/', views.corporate_admin, name='corporate_admin'),
    path('terminals/', views.terminals, name='terminals'),
    path('get_terminals/<str:merchant_id>/', views.get_terminals, name='get_terminals'),
    path('add_terminal/<str:merchant_id>/', views.add_terminal, name='add_terminal'),
    path('update_terminal_pin/<str:merchant_id>/<str:terminal_id>/', views.update_terminal_pin, name='update_terminal_pin'),
    path('toggle-terminal-status/<str:terminal_id>/', views.toggle_terminal_status, name='toggle_terminal_status'),



    
    # path('security-questions/', views.security_questions, name='security_questions'),
    # path('rental-plan/', views.rental_plan, name='rental_plan'),
    # path('award-points/', views.award_points, name='award_points'),
    path('deduct-amount/', views.deduct_amount, name='deduct_amount'),
    path('superadmin_functionality/', views.superadmin_functionality, name='superadmin_functionality'),

    path('update-profile/', views.update_profile, name='update_profile'), 
    path('cash-out/', views.cash_out, name='cash_out'),
     path('merchant-cash-outs/', views.merchant_cash_outs_view, name='merchant_cash_outs'),

    path('get-individual-merchants/', views.get_individual_merchants, name='get_individual_merchants'),
    path('helpdesk/', views.helpdesk, name='helpdesk'),
    
    # path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='bopo_admin/ForgotPass/forgot_password.html',
        email_template_name='bopo_admin/ForgotPass/password_reset_email.html',
        subject_template_name='bopo_admin/ForgotPass/password_reset_subject.txt',
        success_url='/forgot-password/done/',
        form_class=CustomPasswordResetForm,
    ), name='forgot_password'),

    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='bopo_admin/ForgotPass/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # path(
    #     'forgot-password/',
    #     CustomPasswordResetView.as_view(
    #         template_name='bopo_admin/ForgotPass/forgot_password.html',
    #         email_template_name='bopo_admin/ForgotPass/password_reset_email.html',
    #         subject_template_name='bopo_admin/ForgotPass/password_reset_subject.txt',
    #         success_url='/password-reset/done/'
    #     ),
    #     name='forgot_password'
    # ),
    # path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
    #     template_name='bopo_admin/ForgotPass/password_reset_done.html'
    # ), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    #     template_name='bopo_admin/ForgotPass/password_reset_confirm.html'
    # ), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
    #     template_name='bopo_admin/ForgotPass/password_reset_complete.html'
    # ), name='password_reset_complete'),

    
    #  path('helpdesk/', views.helpdesk_view, name='helpdesk'),
    
    # path('api/security-questions/', views.get_security_questions, name='get_security_questions'),
    path('api/security-questions/', security_questions_view, name='security_questions'),
    path('api/security-questions/<int:question_id>/delete/', delete_security_question, name='delete_security_question'),
    path('api/security-questions/<int:question_id>/update/', update_security_question, name='update_security_question'),


    # path('delete-security-question/<int:question_id>/', views.delete_security_question, name='delete_security_question'),
    path('send_customer_notifications/', views.send_notification_customer, name='send_customer_notifications'),
    path('send_customer_notifications/', views.send_notification_customer, name='send_notification_customer'),
    
    # path('edit-corporate/<int:corporate_id>/', views.edit_corporate, name='edit_corporate'),
    # path('update_copmerchant/', views.update_merchant, name='update_copmerchant'),
    # path('edit-cop/<int:corporate_id>/', views.edit_copmerchant, name='edit_cop'),

    
    path('delete-corporate/<int:id>/', views.delete_corporate, name='delete_corporate'),

    # path('update-merchant-status/', update_merchant_status, name='update_merchant_status'),
    path("get-customer/<str:customer_id>/", views.get_customer, name="get_customer"),
    path('bopo_admin/update-customer/<str:customer_id>/', views.update_customer, name='update_customer'),
    path('delete-customer/<str:customer_id>/', views.delete_customer, name='delete_customer'),
    
    path('logout/', custom_logout_view, name='logout'),
    path('update-model-plan/', views.update_model_plan, name='update_model_plan'),
    # path('save-award-points/', views.save_award_points, name='save_award_points'),
    
    path('get-award-point/', views.get_award_point, name='get_award_point'),
    path('update-award-point/', views.update_award_point, name='update_award_point'),

    path('superadmin/payment/save/', save_superadmin_payment, name='save_superadmin_payment'),
    path('resolve-help/<int:help_id>/', views.resolve_help, name='resolve_help'),
    path('model-plans/list/', views.model_plan_list, name='model_plan_list'),


 
  
    # path('delete-merchant/<int:id>/', views.delete_merchant, name='delete_merchant'),



    
  
# path('individual/edit/<int:id>/', views.edit_individual_merchant, name='edit_individual'),
# path('individual/delete/<int:id>/', views.delete_individual_merchant, name='delete_individual'),

    

    path("get-terminal-ids/", views.get_terminal_ids, name="get_terminal_ids"),

    path('get-payment-details/', views.get_payment_details, name='get_payment_details'),
    path('toggle-status/<int:merchant_id>/', toggle_status, name='toggle_status'),
    path('toggle-status/<str:entity_type>/<str:entity_id>/', views.toggle_status, name='toggle_status'),


     path('deduct-amount/', views.deduct_amount, name='deduct_amount'),

    path('assign-employee-role/', assign_employee_role, name='assign_employee_role'),
    
    path('api/security-questions/', add_security_question, name='add_security_question'),
    path('api/get-deduct-amount/', views.get_deduct_amount, name='get_deduct_amount'),

    # path('api/set-deduct-amount/', set_deduct_amount, name='set_deduct_amount'),
    path('save-deduct-settings/', save_deduct_settings, name='save_deduct_settings'),
    
    path('get-current-limit/', views.get_current_limit, name='get_current_limit'),
    
    # path('save-model-plan/', views.save_model_plan, name='save-model-plan'),
    # path('get-model-plans/', views.get_model_plans, name='get_model_plans'),
    path('save-cash-out/', views.save_cash_out, name='save_cash_out'),
    
    
    
    
    path('get_admin_merchant/<str:merchant_id>/', views.get_admin_merchant, name='get_admin_merchant'),
    path('update_admin_merchant/', views.update_admin_merchant, name='update_admin_merchant'),
    path('corporate/add/', views.corporate_add_merchant, name='corporate_add_merchant'),
    
    path('merchant/list/', views.merchant_list, name='merchant_list'),
    path('corporate/terminals/', views.corporate_terminals, name='corporate_terminals'),
    path('corporate/credentials/', views.corporate_credentials, name='corporate_credentials'),
    path('logo/', views.logo, name='logo'),
    # path('upload_logo/', views.upload_logo, name='upload_logo'),
    path('upload-logo/',views.upload_logo, name='upload_logo'),
    path('send-customer-credentials/', views.send_customer_credentials, name='send_customer_credentials'),

    
 
    path('create_notification/', create_notification_view, name='create_notification'),
    path("transaction_history/", views.transaction_history, name="transaction_history"),
    



    path('api/save-fcm-token/', views.save_fcm_token, name='save_fcm_token'),



    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
