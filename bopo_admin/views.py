from django.shortcuts import render

def home(request):
   return render(request, 'bopo_admin/home.html')

def about(request):
     return render(request, 'bopo_admin/about.html')

def merchant(request):
    return render(request, 'bopo_admin/Merchant/merchant.html')

def customer(request):
    return render(request, 'bopo_admin/Customer/customer.html')

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

def send_notifications(request):
    return render(request, 'bopo_admin/Merchant/send_notifications.html')

def received_offers(request):
    return render(request, 'bopo_admin/Merchant/received_offers.html')

def  uploads(request):
    return render(request, 'bopo_admin/Merchant/uploads.html')



def  modify_customer_details(request):
    return render(request, 'bopo_admin/Customer/modify_customer_details.html')

def  send_customer_notifications(request):
    return render(request, 'bopo_admin/Customer/send_customer_notifications.html')

def  customer_uploads(request):
    return render(request, 'bopo_admin/Customer/customer_uploads.html')

def  add_customer(request):
    return render(request, 'bopo_admin/Customer/add_customer.html')



def employee_list(request):
    return render(request, 'bopo_admin/Employee/employee_list.html')

def add_employee(request):
    return render(request, 'bopo_admin/Employee/add_employee.html')