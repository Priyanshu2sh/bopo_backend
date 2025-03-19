from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
   return render(request, 'bopo_admin/home.html')

def about(request):
     return render(request, 'bopo_admin/about.html')

def merchant(request):
    return render(request, 'bopo_admin/Merchant/merchant.html')

def customer(request):
    return render(request, 'bopo_admin/customer.html')

def merchant_list(request):
    return render(request, "bopo_admin/Merchant/merchant_list.html")

def add_merchant(request):
    return render(request, "bopo_admin/Merchant/add_merchant.html")

def project_onboarding(request):
    return render(request, 'bopo_admin/project_onboarding.html')

def project_list(request):
    return render(request, 'bopo_admin/project_list.html')

def merchant_credentials(request):
    return render(request, 'bopo_admin/Merchant/merchant_credentials.html')

def merchant_topup(request):
    return render(request, 'bopo_admin/Merchant/merchant_topup.html')

def map_bonus_points(request):
    return render(request, 'bopo_admin/Merchant/map_bonus_points.html')

def merchant_limit_list(request):
    return render(request, 'bopo_admin/Merchant/merchant_limit_list.html')

def reduce_limit(request):
    return render(request, 'bopo_admin/Merchant/reduce_limit.html')

def merchant_status(request):
    return render(request, 'bopo_admin/Merchant/merchant_status.html')

def login_page_info(request):
    return render(request, 'bopo_admin/Merchant/login_page_info.html')