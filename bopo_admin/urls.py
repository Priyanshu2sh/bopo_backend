from django.urls import path
from .views import home, about, merchant, customer, project_onboarding,merchant_list,add_merchant,project_list

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('merchant/', merchant, name='merchant'),
    path('customer/', customer, name='customer'), 
    path('project_onboarding/', project_onboarding, name='project_onboarding'),
    path('merchant/list/', merchant_list, name='merchant_list'),
    path('merchant/add/', add_merchant, name='add_merchant'),
    path('project/list', project_list, name='project_list'),
  
]
