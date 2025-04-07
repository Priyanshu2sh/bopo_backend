from django.shortcuts import render

from accounts.models import Merchant
# from django.contrib.auth import authenticate 
# from django.shortcuts import redirect
from .models import BopoAdmin
from django.http import JsonResponse
from .models import State, City
from bopo_admin.models import Employee

# Create your views here.


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

def corporate_list(request):
    return render(request, 'bopo_admin/Merchant/corporate_list.html')

def individual_list(request):
    merchants = Merchant.objects.all()
    return render(request, "bopo_admin/Merchant/individual_list.html", {"merchants": merchants})


def add_merchant(request):
    return render(request, "bopo_admin/Merchant/add_merchant.html")

def add_individual_merchant(request):
    if request.method == "POST":
        merchant_id = request.POST.get("merchant_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        aadhaar_number = request.POST.get("aadhaar_number")
        gst_number = request.POST.get("gst_number")
        pan_number = request.POST.get("pan_number")
        shop_name = request.POST.get("shop_name")
        legal_name = request.POST.get("legal_name")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")
        state = request.POST.get("state")
        city = request.POST.get("city")
        country = request.POST.get("country", "India")  # Default to 'India' if empty

             

        # Save to database
        Merchant.objects.create(
            merchant_id=merchant_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            aadhaar_number=aadhaar_number,
            gst_number=gst_number,
            pan_number=pan_number,
            shop_name=shop_name,
            legal_name=legal_name,
            address=address,
            pincode=pincode,
            state=state,
            city=city,
            country=country
        )
        
    return render(request, "bopo_admin/Merchant/add_individual_merchant.html")

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

# def add_employee(request):
#     return render(request, 'bopo_admin/Employee/add_employee.html')

def add_employee(request):
    from bopo_admin.models import Employee  # Move import inside function
    if request.method == "POST":
        name = request.POST.get("employee_name")
        email = request.POST.get("email")
        aadhaar = request.POST.get("aadhaar")
        address = request.POST.get("address")
        state_id = request.POST.get("state")
        city_id = request.POST.get("city")
        mobile = request.POST.get("mobile")
        pan = request.POST.get("pan")
        pincode = request.POST.get("pincode")
        
        print(state_id)
        print(city_id)
        
        
        # Check if email, mobile, or aadhaar already exists
        if Employee.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email ID already exists!"}, status=400)

        if Employee.objects.filter(mobile=mobile).exists():
            return JsonResponse({"error": "Mobile number already exists!"}, status=400)

        if Employee.objects.filter(aadhaar=aadhaar).exists():
            return JsonResponse({"error": "Aadhaar number already exists!"}, status=400)
        
        if Employee.objects.filter(pan=pan).exists():
            return JsonResponse({"error": "Pan number already exists!"}, status=400)
        
        state = State.objects.get(id=state_id)
        city = City.objects.get(id=city_id)

        Employee.objects.create(
                name=name, email=email, aadhaar=aadhaar, address=address,
                state=state.name, city=city.name, mobile=mobile, pan=pan, pincode=pincode
            )
        
        return render(request, 'bopo_admin/Employee/add_employee.html', {'message': 'Employee added successfully!'})
        
    return render(request, 'bopo_admin/Employee/add_employee.html')

def employee_role(request):
    return render(request, 'bopo_admin/Employee/employee_role.html') 


def payment_details(request):
    return render(request, 'bopo_admin/Payment/payment_details.html')


def account_info(request):
    return render(request, 'bopo_admin/Payment/account_info.html') 

def reports(request):
    return render(request, 'bopo_admin/Payment/reports.html')

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
    
    


# Get all states
def get_states(request):
    states = State.objects.all().values('id', 'name')
    return JsonResponse(list(states), safe=False)

# Get cities for a given state
def get_cities(request, state_id):
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)