from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
   return render(request, 'bopo_admin/home.html')

def about(request):
     return render(request, 'bopo_admin/about.html')

def merchant(request):
    return render(request, 'bopo_admin/merchant.html')

def customer(request):
    return render(request, 'bopo_admin/customer.html')

def merchant_list(request):
    return render(request, 'bopo_admin/merchant_list.html')
 
def project_onboarding(request):
    return render(request, 'bopo_admin/project_onboarding.html')

 
 