from django.shortcuts import render
# from django.contrib.auth import authenticate 
# from django.shortcuts import redirect
from .models import BopoAdmin

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

 
 
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = BopoAdmin.objects.get(username=username)
        if user.password != password:
            error_message = "Incorrect password"
            return render(request, 'bopo_admin/login.html', {'error_message': error_message})
        
        return render(request, 'bopo_admin/login.html')
    # return redirect()
    else:
        return render(request, 'bopo_admin/login.html')