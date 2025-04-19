from io import BytesIO
import json
import random
import string
from tkinter.font import Font
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
import openpyxl
from requests import Response
from rest_framework import status
from openpyxl.styles import Font



from accounts.models import Corporate, Customer, Merchant, Terminal
from accounts.views import generate_terminal_id
from bopo_award.models import CustomerPoints, History, MerchantPoints
from django.contrib.auth.hashers import check_password

# from django.contrib.auth import authenticate 
# from django.shortcuts import redirect
from .models import AccountInfo, BopoAdmin, Employee, MerchantCredential, MerchantLogin, Notification, Reducelimit, Topup, UploadedFile
from django.http import JsonResponse
from .models import State, City
from bopo_admin.models import Employee



# Create your views here.



# views.py

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from accounts.models import LoginAttempt  
# from django.contrib.auth.hashers import make_password

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         remember_me = request.POST.get('remember_me')
        
     
#         user = authenticate(request, username=username, password=password)

      
#         login_success = False

#         if user is not None:
#             login(request, user)  
#             login_success = True 
            
#             #
#             login_attempt = LoginAttempt(username=username, password=make_password(password), success=login_success)
#             login_attempt.save()

          
#             return redirect('home')

#         else:
           
#             login_attempt = LoginAttempt(username=username, password=make_password(password), success=login_success)
#             login_attempt.save()  

        
#             return render(request, 'bopo_admin/login.html', {'error_message': 'Invalid credentials'})

 
#     return render(request, 'bopo_admin/login.html')

from django.shortcuts import render, redirect
from .models import BopoAdmin
from django.contrib.auth.hashers import check_password

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Attempting to log in user: {username}")

        try:
            user = BopoAdmin.objects.get(username=username)
            if check_password(password, user.password):
                request.session['admin_id'] = user.id
                request.session['admin_name'] = user.username
                print("✅ Login successful, redirecting to /home/")
                return redirect('/home/')
            else:
                print("❌ Incorrect password")
                error_message = "Incorrect password"
        except BopoAdmin.DoesNotExist:
            print("❌ User does not exist")
            error_message = "User does not exist"

        return render(request, 'bopo_admin/login.html', {'error_message': error_message})

    return render(request, 'bopo_admin/login.html')

from django.contrib.auth import logout
def custom_logout_view(request):
    logout(request)
    return redirect('login') 


def home(request):
    # Calculate total projects and project progress
    total_projects = Corporate.objects.count()
    completed_projects = Corporate.objects.filter(status="Completed").count()  # Assuming a 'status' field exists
    project_progress = (completed_projects / total_projects * 100) if total_projects > 0 else 0

    # Calculate total merchants and merchant progress
    total_merchants = Merchant.objects.count()
    active_merchants = Merchant.objects.filter(status="Active").count()  # Assuming a 'status' field exists
    merchant_progress = (active_merchants / total_merchants * 100) if total_merchants > 0 else 0

    # Calculate total customers
    total_customers = Customer.objects.count()

    # Calculate total users (sum of customers, merchants, and corporates)
    total_users = total_customers + total_merchants + total_projects

     # Prepare data for the bar chart
    chart_data = {
        "projects": [total_projects, completed_projects],
        "merchants": [total_merchants, active_merchants],
        "customers": [total_customers],
    }

    # Add context for the dashboard
    context = {
        "title": "Welcome to Bopo Admin Dashboard",
        "description": "Manage merchants, customers, and projects efficiently.",
        "total_projects": total_projects,
        "project_progress": project_progress,
        "total_merchants": total_merchants,
        "merchant_progress": merchant_progress,
        "total_customers": total_customers,
        "total_users": total_users,
        "chart_data": chart_data,
    }
    return render(request, 'bopo_admin/home.html', context)

def about(request):
     return render(request, 'bopo_admin/about.html')

def merchant(request):
    return render(request, 'bopo_admin/Merchant/merchant.html')

def customer(request):
    customers = Customer.objects.all()
    return render(request, 'bopo_admin/Customer/customer.html', {'customers': customers})


from django.http import JsonResponse, Http404
from accounts.models import Customer  # Adjust this import to your actual model

def get_customer(request, customer_id):
    if request.method == "GET":
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            data = {
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "mobile": customer.mobile,
                "age": customer.age,
                "aadhar_number": customer.aadhar_number, 
                "address": customer.address,
                "city_id": customer.city,
                "state_id": customer.state,
                "pincode": customer.pincode,
                "gender": customer.gender,
                "pan": customer.pan,
            }
            return JsonResponse(data)
        except Customer.DoesNotExist:
            raise Http404("Customer does not exist")
        

from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Customer
from django.http import JsonResponse

def update_customer(request, customer_id):
    if request.method == "POST":
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # Update customer data from the form
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.mobile = request.POST.get('mobile')
        customer.age = request.POST.get('age')
        customer.aadhar_number = request.POST.get('aadhar_number')
        customer.address = request.POST.get('address')
        customer.state_id = request.POST.get("state")
        customer.city_id = request.POST.get("city")
        customer.pincode = request.POST.get('pincode')
        customer.gender = request.POST.get('gender')
        customer.pan = request.POST.get('pan')
        customer.save()

        # Return a success response
        return JsonResponse({
    "status": "success",
    "message": "Customer updated successfully"
})
    return JsonResponse({"message": "Invalid request"}, status=400)



# bopo_admin/views.py

from django.http import JsonResponse
from accounts.models import Customer


def delete_customer(request, customer_id):
    if request.method == 'DELETE':
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            customer.delete()
            return JsonResponse({'status': 'success', 'message': 'Customer deleted successfully.'})
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def merchant_list(request):
    return render(request, "bopo_admin/Merchant/merchant_list.html")

def corporate_list(request):
    corporates = Corporate.objects.all()
    corporate_data = []

    for corporate in corporates:
        # Fetch merchants linked to the corporate
        merchants = Merchant.objects.filter(corporate_id=corporate.corporate_id, user_type='corporate')
        corporate_data.append({
            "corporate": corporate,
            "merchants": merchants
        })

    return render(request, 'bopo_admin/Merchant/corporate_list.html', {
        "corporate_data": corporate_data
    })

def individual_list(request):
    merchants = Merchant.objects.filter(user_type='individual')  # Fetch only individual merchants
    merchant_points = MerchantPoints.objects.filter(merchant__in=merchants)  # Fetch points for these merchants

    # Create a mapping of merchant IDs to their actual points
    points_mapping = {mp.merchant.id: mp.points for mp in merchant_points}

    # Pass merchants and their points to the template
    return render(request, "bopo_admin/Merchant/individual_list.html", {
        "merchants": merchants,
        "points_mapping": points_mapping
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Merchant, Corporate
from django.http import JsonResponse
import random
import string

def add_merchant(request):
    if request.method == "POST":
        try:
            is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

            select_project = request.POST.get("select_project")
            project_type = request.POST.get("project_type")
            project_name = request.POST.get("project_name", "")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            aadhaar = request.POST.get("aadhaar")
            gst_number = request.POST.get("gst_number")
            shop_name = request.POST.get("shop_name")
            pan = request.POST.get("pan")
            address = request.POST.get("address")
            legal_name = request.POST.get("legal_name")
            pincode = request.POST.get("pincode")
            city_id = request.POST.get("city")
            state_id = request.POST.get("state")
            country = request.POST.get("country", "India")
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)



            # ✅ Unique field checks
            if Merchant.objects.filter(email=email).exists() or Corporate.objects.filter(email=email).exists():
                message = "Email is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            if Merchant.objects.filter(mobile=mobile).exists() or Corporate.objects.filter(mobile=mobile).exists():
                message = "Mobile number is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            if Merchant.objects.filter(aadhaar_number=aadhaar).exists() or Corporate.objects.filter(aadhaar=aadhaar).exists():
                message = "Aadhaar number is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            # if Merchant.objects.filter(pan_number=pan).exists():
            #     message = "PAN number is already registered."
            #     return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            # ✅ Corporate ID
            last_corporate = Corporate.objects.exclude(corporate_id=None).order_by("-corporate_id").first()
            new_corporate_id = 1 if not last_corporate else int(last_corporate.corporate_id[6:]) + 1
            corporate_id = f"CORP{new_corporate_id:06d}"

            if project_type == "Existing Project" and select_project:
                corporate = Corporate.objects.get(id=select_project)
                project_name = corporate.project_name
                project_id = corporate.project_id

                # ✅ Merchant ID
                project_abbr = project_name[:4].upper()
                random_number = ''.join(random.choices(string.digits, k=11))
                merchant_id = f"{project_abbr}{random_number}"

                Merchant.objects.create(
                    user_type='corporate',
                    merchant_id=merchant_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    mobile=mobile,
                    aadhaar_number=aadhaar,
                    gst_number=gst_number,
                    pan_number=pan,
                    shop_name=shop_name,
                    legal_name=legal_name,
                    address=address,
                    pincode=pincode,
                    state=state,
                    city=city,
                    country=country,
                    corporate_id=corporate.corporate_id,
                    project_name=project_name,
                    select_state=state,
                )
                
                merchant = Merchant.objects.get(merchant_id=merchant_id)
                # ✅ Create terminal for the new merchant
                terminal_id = generate_terminal_id()
                print('aaaa')
                while Terminal.objects.filter(terminal_id=terminal_id).exists():
                    terminal_id = generate_terminal_id()

                Terminal.objects.create(terminal_id=terminal_id, merchant_id=merchant)

            elif project_type == "New Project":
                if not project_name:
                    message = "Project name is required for new projects."
                    return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

                last_project = Corporate.objects.exclude(project_id=None).order_by("-project_id").first()
                new_project_id = 1 if not last_project else int(last_project.project_id[4:]) + 1
                project_id = f"PROJ{new_project_id:06d}"

                Corporate.objects.create(
                    select_project=select_project,
                    corporate_id=corporate_id,
                    project_name=project_name,
                    project_id=project_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    mobile=mobile,
                    aadhaar=aadhaar,
                    gst_number=gst_number,
                    pan=pan,
                    shop_name=shop_name,
                    legal_name=legal_name,
                    address=address,
                    pincode=pincode,
                    state=state,
                    city=city,
                    country=country,
                    role="admin"
                )
            else:
                message = "Invalid project type selected."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            success_message = "Merchant added successfully."
            return JsonResponse({"success": True, "message": success_message}) if is_ajax else redirect_with_success(success_message)

        except Exception as e:
            print("Error saving merchant:", e)
            return JsonResponse({"success": False, "message": "Something went wrong. Please check your inputs."})

    corporates = Corporate.objects.all()
    return render(request, "bopo_admin/Merchant/add_merchant.html", {"corporates": corporates})







def redirect_with_error(request, message):
    from django.contrib import messages
    messages.error(request, message)
    return redirect("add_merchant")

def redirect_with_success(request, message):
    from django.contrib import messages
    messages.success(request, message)
    return redirect("add_merchant")

# from django.http import JsonResponse
# from accounts.models import Corporate  # or whatever your model is named

# def edit_cop(request, corporate_id):
#     try:
#         merchant = Corporate.objects.get(id=corporate_id)
#         data = {
#             "customer_id": corporate.id,
#             "first_name": corporate.first_name,
#             "last_name": corporate.last_name,
#             "email": corporate.email,
#             "aadhaar": merchant.aadhaar,
#             "shop_name": merchant.shop_name,
#             "address": merchant.address,
#             "state": merchant.state.id if merchant.state else "",
#             "city": merchant.city.id if merchant.city else "",
#             "mobile": merchant.mobile,
#             "gst_number": merchant.gst_number,
#             "pan_number": merchant.pan_number,
#             "legal_name": merchant.legal_name,
#             "pincode": merchant.pincode,
#             "project_name": merchant.project.project_name if merchant.project else "",
#         }
#         return JsonResponse(data)
#     except Corporate.DoesNotExist:
#         return JsonResponse({'error': 'Corporate merchant not found'}, status=404)





# In your Django views.py
from django.http import JsonResponse
from accounts.models import Merchant,Corporate


def edit_copmerchant(request, merchant_id):
    try:
        # Fetch the merchant by ID
        merchant = Merchant.objects.get(id=merchant_id)
        
        
        # Prepare the data to return
        data = {
            'first_name': merchant.first_name,
            'last_name': merchant.last_name,
            'email': merchant.email,
            'aadhaar': merchant.aadhaar_number,
            'shop_name': merchant.shop_name,
            'address': merchant.address,
            'state': merchant.state,  
            'mobile': merchant.mobile,
            'gst_number': merchant.gst_number,
            'pan_number': merchant.pan_number,
            'legal_name': merchant.legal_name,
            'city': merchant.city,  
            'pincode': merchant.pincode,
            'project_name': merchant.project_name,  # Add project_name field
            
        }
        return JsonResponse(data)
    except Merchant.DoesNotExist:
        return JsonResponse({'error': 'Merchant not found'}, status=404)




    
from django.http import JsonResponse
from accounts.models import Merchant, Corporate

def update_copmerchant(request):
    if request.method == 'POST':
        # Extract the data from the request (Assuming data comes as form data)
        merchant_id = request.POST.get('merchant_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        aadhaar = request.POST.get('aadhaar')
        shop_name = request.POST.get('shop_name')
        address = request.POST.get('address')
        state = request.POST.get('state')
        mobile = request.POST.get('mobile')
        gst_number = request.POST.get('gst_number')
        pan_number = request.POST.get('pan')
        legal_name = request.POST.get('legal_name')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        project_name = request.POST.get('project_name')
        # select_project = request.POST.get('select_project')

        try:
            # Retrieve the merchant to update
            merchant = Merchant.objects.get(id=merchant_id)

            # Update the merchant fields
            merchant.first_name = first_name
            merchant.last_name = last_name
            merchant.email = email
            merchant.aadhaar_number = aadhaar
            merchant.shop_name = shop_name
            merchant.address = address
            merchant.state = state
            merchant.mobile = mobile
            merchant.gst_number = gst_number
            merchant.pan_number = pan_number
            merchant.legal_name = legal_name
            merchant.city = city
            merchant.pincode = pincode
            merchant.project_name = project_name
            # merchant.select_project = select_project

            # Save the updated merchant
            merchant.save()

            # Return a success response with the updated merchant data
            return JsonResponse({
                'success': True 
                })

        except Merchant.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Merchant not found.'})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


from django.http import JsonResponse
from accounts.models import Corporate, Merchant

def delete_corporate(request, id):
    if request.method == 'DELETE':
        try:
            Corporate.objects.get(id=id).delete()
            return JsonResponse({'success': True})
        except Corporate.DoesNotExist:
            return JsonResponse({'error': 'Corporate not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# def edit_individual(request, id):
#     merchant = get_object_or_404(Merchant, id=id)
#     return render(request, 'bopo_admin/Merchant/edit_individual.html', {'merchant': merchant})



from django.http import JsonResponse
from accounts.models import Merchant

def edit_merchants(request, merchant_id):
    merchant = get_object_or_404(Merchant, id=merchant_id)
    data = {
        "id": merchant.id,
        "first_name": merchant.first_name,
        "last_name": merchant.last_name,
        "email": merchant.email,
        "mobile": merchant.mobile,
        "shop_name": merchant.shop_name,
        "address": merchant.address,
        "aadhaar_number": merchant.aadhaar_number,
        "gst": merchant.gst,
        "pan_number": merchant.pan_number,
        "legal_name": merchant.legal_name,
        "state": merchant.state,
        "city": merchant.city,
        "pincode": merchant.pincode,
    }
    return JsonResponse(data)


from django.http import JsonResponse
from accounts.models import Merchant

def update_merchant(request): 
    if request.method == "POST":
        merchant_id = request.POST.get('merchant_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        aadhaar = request.POST.get("aadhaar")
        address = request.POST.get("address")
        state_id = request.POST.get("state")
        city_id = request.POST.get("city")
        mobile = request.POST.get("mobile")
        pan = request.POST.get("pan")
        pincode = request.POST.get("pincode")
        shop_name = request.POST.get("shop_name")
        country = request.POST.get("country", "India")
        select_state = request.POST.get("select_state")
        
        try:
            # Get the  merchant object by id
            merchant = Merchant.objects.get(id=merchant_id)
            
            # Update the  merchant object fields
            merchant.first_name= first_name
            merchant.last_name=last_name
            merchant.email = email
            merchant.aadhaar = aadhaar  # Corrected here
            merchant.address = address  # Corrected here
            merchant.state_id = state_id  # Corrected here
            merchant.city_id = city_id  # Corrected here
            merchant.mobile = mobile
            merchant.pan = pan
            merchant.pincode = pincode
            merchant.shop_name = shop_name
            merchant.country = country
            select_state=select_state,
            
            # Save the updated merchant object
            merchant.save()

            return JsonResponse({
            "success": True,
            "message": "Merchant updated successfully!"  # ✅ Important!
        })
        except Merchant.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Merchant not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from django.http import JsonResponse
from accounts.models import Merchant  # change this based on your model name


def delete_merchant(request, merchant_id):
    if request.method == "DELETE":
        try:
            merchant = Merchant.objects.get(id=merchant_id)
            merchant.delete()
            return JsonResponse({"success": True, "message": "Merchant deleted successfully."})
        except Merchant.DoesNotExist:
            return JsonResponse({"success": False, "message": "Merchant not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})



from accounts.models import Merchant
from django.shortcuts import render, redirect
from django.http import JsonResponse


def add_individual_merchant(request):
    if request.method == "POST":
        try:
            # Get data from the form
            merchant_id = request.POST.get("merchant_id")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            aadhaar_number = request.POST.get("aadhaar_number")
            gst = request.POST.get("gst")
            pan_number = request.POST.get("pan_number")
            shop_name = request.POST.get("shop_name")
            legal_name = request.POST.get("legal_name")
            address = request.POST.get("address")
            pincode = request.POST.get("pincode")
            state_id = request.POST.get("state")
            city_id = request.POST.get("city")
            country = request.POST.get("country", "India")

            # Fetch state and city from DB
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)

            # Uniqueness checks
            if Merchant.objects.filter(email=email).exists() or Corporate.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email ID already exists!"})

            if Merchant.objects.filter(mobile=mobile).exists() or Corporate.objects.filter(mobile=mobile).exists():
                return JsonResponse({"success": False, "message": "Mobile number already exists!"})

            if Merchant.objects.filter(aadhaar_number=aadhaar_number).exists():
                return JsonResponse({"success": False, "message": "Aadhaar number already exists!"})

            if Merchant.objects.filter(pan_number=pan_number).exists():
                return JsonResponse({"success": False, "message": "PAN number already exists!"})
            
            
             # 🔢 Generate unique merchant ID
            last_merchant = Merchant.objects.all().order_by('id').last()
            if last_merchant and last_merchant.merchant_id:
                try:
                    last_id = int(last_merchant.merchant_id.replace('MER', ''))
                    merchant_id = f"MER{last_id + 1:06d}"
                except ValueError:
                    merchant_id = "MER000001"
            else:
                merchant_id = "MER000001"

            # Save merchant to the database
            Merchant.objects.create(
                merchant_id=merchant_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile=mobile,
                aadhaar_number=aadhaar_number,
                gst=gst,
                pan_number=pan_number,
                shop_name=shop_name,
                legal_name=legal_name,
                address=address,
                pincode=pincode,
                state=state,
                city=city,
                country=country
            )

            return JsonResponse({'success': True, 'message': 'Merchant added successfully!'})

        except Exception as e:
            # Log the error for debugging purposes
            return JsonResponse({'success': False, 'message': f"An error occurred: {str(e)}"})

    return render(request, "bopo_admin/Merchant/add_individual_merchant.html")



def project_onboarding(request):
    return render(request, 'bopo_admin/project_onboarding.html')

def project_list(request):
    return render(request, 'bopo_admin/project_list.html')

def merchant_credentials(request):
    if request.method == "POST":
        project = request.POST.get("project")
        merchant_id = request.POST.get("merchant_id")
        merchant_name = request.POST.get("merchant_name")
        terminal_id = request.POST.get("terminal_id")

        # Save to database or perform any other action
        print('project:', project)
        print('merchant_id:', merchant_id)
        print('merchant_name:', merchant_name)
        print('terminal_id:', terminal_id)
       
        MerchantCredential.objects.create(
            
            project=project,
            merchant_id=merchant_id,
            merchant_name=merchant_name,
            terminal_id=terminal_id
            
        )
    return render(request, 'bopo_admin/Merchant/merchant_credentials.html')

def merchant_topup(request):
    if request.method == "POST":
        merchant = request.POST.get("merchant")
        merchant_id = request.POST.get("merchant_id")
        topup_amount = request.POST.get("topup_amount")
        transaction_id = request.POST.get("transaction_id")
        topup_points = request.POST.get("topup_points")
        payment_mode = request.POST.get("payment_mode")
        upi_id = request.POST.get("upi_id")
        transaction_date = request.POST.get("transaction_date")
        transaction_time = request.POST.get("transaction_time")
        print("topup_amount:", topup_amount)
        print("transaction_id :", transaction_id)
        print("topup_points :", topup_points)
        print("payment_mode :", payment_mode)

        # Save to database or perform any other action
        Topup.objects.create(
            merchant=merchant,
            merchant_id=merchant_id,
            topup_amount=topup_amount,
            transaction_id=transaction_id,
            topup_points=topup_points,
            payment_mode=payment_mode,
            upi_id=upi_id,
            transaction_date=transaction_date,
            transaction_time=transaction_time
        )

    # Fetch all merchants for the dropdown menu
    merchants = Merchant.objects.all()
    return render(request, 'bopo_admin/Merchant/merchant_topup.html', {"merchants": merchants})

def map_bonus_points(request):
    return render(request, 'bopo_admin/Merchant/map_bonus_points.html')

def merchant_limit_list(request):
    # Fetch the list of merchants from the database
    merchants = Merchant.objects.all()
    # Pass the list to the template context
    context = {
        'merchants': merchants
    }
    # Render the template with the context
    return render(request, 'bopo_admin/Merchant/merchant_limit_list.html', context)

    # return render(request, 'bopo_admin/Merchant/merchant_limit_list.html')

def reduce_limit(request):
    if request.method == "POST":
        project = request.POST.get("project")
        merchant = request.POST.get("merchant")
        current_limit = request.POST.get("current_limit")
        reduce_amount = request.POST.get("reduce_amount")
        transaction_id = request.POST.get("transaction_id")

        print('project:', project)
        print('merchant:', merchant)
        print('current_limit:', current_limit)
        print('reduce limit:', reduce_amount)
        print('transaction id:', transaction_id)

        # Save to database or perform any other action
        Reducelimit.objects.create(
            project=project,
            merchant=merchant,
            current_limit=current_limit,
            reduce_amount=reduce_amount,
            transaction_id=transaction_id
        )
    return render(request, 'bopo_admin/Merchant/reduce_limit.html')

# def merchant_status(request):
    # Fetch active merchants, ordered by legal name
    # merchants = Merchant.objects.filter(status='active').order_by('legal_name')

    # Pass the list to the template context
    # context = {
    #     'merchants': merchants
    # }

    # Render the template with the context
    # return render(request, 'bopo_admin/Merchant/merchant_status.html', context)
    
def merchant_status(request):
    merchants = Merchant.objects.all().order_by('merchant_id')
    corporates = Corporate.objects.all().order_by('project_name')

    context = {
        'merchants': merchants,
        'corporates': corporates,
    }

    return render(request, 'bopo_admin/Merchant/merchant_status.html', context)



# from django.http import JsonResponse
# from accounts.models import Merchant


# def update_merchant_status(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         merchant_id = data.get('id')
#         verified_at = data.get('verified_at')
        
#         try:
#             merchant = Merchant.objects.get(id=merchant_id)
#             merchant.verified_at = verified_at
#             merchant.save()
#             return JsonResponse({'success': True})
#         except Merchant.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Merchant not found'})

#     return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_merchants(request):
    project_id = request.GET.get('project_id')

    merchants = Merchant.objects.filter(project_id=project_id).values('merchant_id', 'first_name', 'last_name')
    print(list(merchants))
    return JsonResponse({'merchants': list(merchants)})

def login_page_info(request):
    if request.method == 'POST':
        sales_name = request.POST.get('sales_name')
        sales_number = request.POST.get('sales_number')
        sales_email = request.POST.get('sales_email')

        MerchantLogin.objects.create(
            sales_name=sales_name,
            sales_number=sales_number,
            sales_email=sales_email
        )
    return render(request, 'bopo_admin/Merchant/login_page_info.html')

def send_notifications(request):
    corporates = Corporate.objects.all()  # Fetch all projects from the Corporate table
    merchants = Merchant.objects.all()  # Fetch all merchants

    if request.method == "POST":
        project = request.POST.get("project")
        merchant = request.POST.get("merchant")
        notification_type = request.POST.get("notification_type")
        notification_title = request.POST.get("notification_title")
        description = request.POST.get("description")

        # Save the notification data to the database
        Notification.objects.create(
            project_id=project,
            merchant_id=merchant,
            notification_type=notification_type,
            title=notification_title,
            description=description
        )

        return render(request, 'bopo_admin/Merchant/send_notifications.html', {
            'corporates': corporates,
            'merchants': merchants,
            'message': 'Notification sent and stored successfully!'
        })

    return render(request, 'bopo_admin/Merchant/send_notifications.html', {
        'corporates': corporates,
        'merchants': merchants
    })

def received_offers(request):
    return render(request, 'bopo_admin/Merchant/received_offers.html')

def uploads(request):
    if request.method == "POST":
        file_type = request.POST.get("file_type")
        uploaded_file = request.FILES.get(file_type)

        if file_type and uploaded_file:
            UploadedFile.objects.create(file_type=file_type, file=uploaded_file)

    # Fetch uploaded files filtered by type
    privacy_policy_file = UploadedFile.objects.filter(file_type="privacy_policy").first()
    terms_conditions_file = UploadedFile.objects.filter(file_type="terms_conditions").first()
    user_guide_file = UploadedFile.objects.filter(file_type="user_guide").first()

    return render(request, 'bopo_admin/Merchant/uploads.html', {
        "privacy_policy_file": privacy_policy_file,
        "terms_conditions_file": terms_conditions_file,
        "user_guide_file": user_guide_file,
    })

def  modify_customer_details(request):
    return render(request, 'bopo_admin/Customer/modify_customer_details.html')

def  send_customer_notifications(request):
    return render(request, 'bopo_admin/Customer/send_customer_notifications.html')

def  customer_uploads(request):
    return render(request, 'bopo_admin/Customer/customer_uploads.html')


def add_customer(request): 
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        aadhar_number = request.POST.get('aadhaar') 
        pan = request.POST.get('pan')
        address = request.POST.get('address')
        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        pincode = request.POST.get('pincode')

        try:
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)
        except (State.DoesNotExist, City.DoesNotExist):
            return JsonResponse({"success": False, "message": "Invalid state or city selection."})

        # Validation checks
        if Customer.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email ID already exists!"})

        if Customer.objects.filter(mobile=mobile).exists():
            return JsonResponse({"success": False, "message": "Mobile number already exists!"})

        if Customer.objects.filter(aadhar_number=aadhar_number).exists():
            return JsonResponse({"success": False, "message": "Aadhaar number already exists!"})

        if Customer.objects.filter(pan=pan).exists():
            return JsonResponse({"success": False, "message": "PAN number already exists!"})

        # Save the customer
        Customer.objects.create(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            age=age,
            gender=gender,
            aadhar_number=aadhar_number,
            pan=pan,
            address=address,
            state=state,
            city=city,
            pincode=pincode,
        )

        return JsonResponse({"success": True, "message": "Customer added successfully!"})
    
    return render(request, 'bopo_admin/Customer/add_customer.html')


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'bopo_admin/Employee/employee_list.html', {'employees': employees})

from django.http import JsonResponse
from .models import Employee 
def get_employee(request, employee_id):
    try:
        # Get the employee by ID
        employee = Employee.objects.get(id=employee_id)
        
        # Return employee details as JSON
        employee_data = {
            'id': employee.id,
            'name': employee.name,
            'email': employee.email,
            'aadhaar': employee.aadhaar,
            'address': employee.address,
            'state': employee.state,
            'city': employee.city,
            'username': employee.username,
            'password': employee.password,
            'mobile': employee.mobile,
            'pan': employee.pan,
            'pincode': employee.pincode
        }
        
        return JsonResponse(employee_data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
from django.http import JsonResponse
from .models import Employee

def update_employee(request): 
    if request.method == "POST":
        employee_id = request.POST.get('employee_id')
        name = request.POST.get('employee_name')
        email = request.POST.get('email')
        aadhaar = request.POST.get("aadhaar")
        address = request.POST.get("address")
        state_id = request.POST.get("state")
        city_id = request.POST.get("city")
        mobile = request.POST.get("mobile")
        pan = request.POST.get("pan")
        pincode = request.POST.get("pincode")
        username = request.POST.get("username")
        password = request.POST.get("password")
        country = request.POST.get("country", "India")
        
        try:
            # Get the employee object by id
            employee = Employee.objects.get(id=employee_id)
            
            # Update the employee object fields
            employee.name = name
            employee.email = email
            employee.aadhaar = aadhaar  # Corrected here
            employee.address = address  # Corrected here
            employee.state_id = state_id  # Corrected here
            employee.city_id = city_id  # Corrected here
            employee.mobile = mobile
            employee.pan = pan
            employee.pincode = pincode
            employee.username = username
            employee.password = password
            employee.country = country
            
            # Save the updated employee object
            employee.save()

            return JsonResponse({'success': True})
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Employee not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


from django.http import JsonResponse
from .models import Employee

def delete_employee(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        employee.delete()
        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)


from django.http import JsonResponse
from django.shortcuts import render
from .models import Employee, State, City

def add_employee(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        name = request.POST.get("employee_name")
        email = request.POST.get("email")
        aadhaar = request.POST.get("aadhaar")
        address = request.POST.get("address")
        state_id = request.POST.get("state")
        city_id = request.POST.get("city")
        mobile = request.POST.get("mobile")
        pan = request.POST.get("pan")
        pincode = request.POST.get("pincode")
        username = request.POST.get("username")
        password = request.POST.get("password")
        country = request.POST.get("country", "India")
        # status = request.POST.get("status")

        if Employee.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email ID already exists!"})

        if Employee.objects.filter(mobile=mobile).exists():
            return JsonResponse({"success": False, "message": "Mobile number already exists!"})

        if Employee.objects.filter(aadhaar=aadhaar).exists():
            return JsonResponse({"success": False, "message": "Aadhaar number already exists!"})

        if Employee.objects.filter(pan=pan).exists():
            return JsonResponse({"success": False, "message": "PAN number already exists!"})

        try:
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)
        except (State.DoesNotExist, City.DoesNotExist):
            return JsonResponse({"success": False, "message": "Invalid state or city selection."})

        Employee.objects.create(
            employee_id=employee_id,
            name=name,
            email=email,
            aadhaar=aadhaar,
            address=address,
            state=state,
            city=city,
            mobile=mobile,
            pan=pan,
            pincode=pincode,
            username=username,
            password=password,
            country=country,
            # status=status
        )

        return JsonResponse({"success": True, "message": "Employee added successfully!"})

    return render(request, 'bopo_admin/Employee/add_employee.html')


def employee_role(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        role = request.POST.get("role")
        # Save to database or perform any other action
        # For example, you can create a Role model instance here
        BopoAdmin.objects.create(
            employee_id=employee_id,
            role=role
        )

    return render(request, 'bopo_admin/Employee/employee_role.html') 


def payment_details(request):
    if request.method == "POST":
        payment_id = request.POST.get("payment_id")
        amount = request.POST.get("amount")
        transaction_id = request.POST.get("transaction_id")
        transaction_date = request.POST.get("transaction_date")
        transaction_time = request.POST.get("transaction_time")

        # Save to database or perform any other action
        # For example, you can create a Payment model instance here
        BopoAdmin.objects.create(
            payment_id=payment_id,
            amount=amount,
            transaction_id=transaction_id,
            transaction_date=transaction_date,
            transaction_time=transaction_time
        )
    return render(request, 'bopo_admin/Payment/payment_details.html')


def account_info(request):
    account = AccountInfo.objects.first()  # Get the first account (modify as per your logic)
    
    if request.method == "POST":
        accountNumber = request.POST.get("accountNumber")
        payableTo = request.POST.get("payableTo")
        bankName = request.POST.get("bankName")
        city = request.POST.get("city")
        accountType = request.POST.get("accountType")
        ifscCode = request.POST.get("ifscCode")
        branchName = request.POST.get("branchName")
        pincode = request.POST.get("pincode")

        if account:
            # Update existing record
            account.accountNumber = accountNumber
            account.payableTo = payableTo
            account.bankName = bankName
            account.city = city
            account.accountType = accountType
            account.ifscCode = ifscCode
            account.branchName = branchName
            account.pincode = pincode
            account.save()
        else:
            # Create new record if none exists
            AccountInfo.objects.create(
                accountNumber=accountNumber,
                payableTo=payableTo,
                bankName=bankName,
                city=city,
                accountType=accountType,
                ifscCode=ifscCode,
                branchName=branchName,
                pincode=pincode
            )

        return JsonResponse({"message": "Account saved successfully!"})

    return render(request, "bopo_admin/Payment/account_info.html", {"account": account})

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
    

def export_projects(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Corporate Projects"

    # Add headers to the sheet
    headers = [
        "Corporate ID", "Project ID", "Project Name", "First Name", "Last Name",
        "Email", "Mobile", "Aadhaar", "GST Number", "PAN", "Shop Name",
        "Address", "City", "State", "Country", "Pincode", "Created At"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font =  Font(bold=True)

    # Fetch data from the Corporate table
    corporates = Corporate.objects.all()
    print("Total corporates:", corporates.count())

    if not corporates.exists():
        print("No data found in the Corporate table.")  # Debugging log

    # Add data to the Excel sheet
    for row_num, corporate in enumerate(corporates, 2):
        sheet.cell(row=row_num, column=1, value=corporate.corporate_id or "")
        sheet.cell(row=row_num, column=2, value=corporate.project_id or "")
        sheet.cell(row=row_num, column=3, value=corporate.project_name or "")
        sheet.cell(row=row_num, column=4, value=corporate.first_name or "")
        sheet.cell(row=row_num, column=5, value=corporate.last_name or "")
        sheet.cell(row=row_num, column=6, value=corporate.email or "")
        sheet.cell(row=row_num, column=7, value=corporate.mobile or "")
        sheet.cell(row=row_num, column=8, value=corporate.aadhaar or "")
        sheet.cell(row=row_num, column=9, value=corporate.gst_number or "")
        sheet.cell(row=row_num, column=10, value=corporate.pan or "")
        sheet.cell(row=row_num, column=11, value=corporate.shop_name or "")
        sheet.cell(row=row_num, column=12, value=corporate.address or "")
        sheet.cell(row=row_num, column=13, value=corporate.city or "")
        sheet.cell(row=row_num, column=14, value=corporate.state or "")
        sheet.cell(row=row_num, column=15, value=corporate.country or "")
        sheet.cell(row=row_num, column=16, value=corporate.pincode or "")
        sheet.cell(row=row_num, column=17, value=corporate.created_at.strftime("%Y-%m-%d %H:%M:%S") if corporate.created_at else "")

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Corporate_Projects.xlsx"'

    return response
 

def export_merchants(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Merchant Details"

    # Add headers to the sheet
    headers = [
        "Merchant ID", "User Type", "Project Name", "First Name", "Last Name",
        "Email", "Mobile", "Aadhaar", "GST Number", "PAN", "Shop Name",
        "Address", "City", "State", "Country", "Pincode", "Created At"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    # Fetch data from the Merchant table
    merchants = Merchant.objects.all()
    if not merchants.exists():
        print("No data found in the Merchant table.")  # Debugging log

    # Add data to the Excel sheet
    for row_num, merchant in enumerate(merchants, 2):
        sheet.cell(row=row_num, column=1, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=2, value=merchant.user_type or "")
        sheet.cell(row=row_num, column=3, value=merchant.project_name or "")
        sheet.cell(row=row_num, column=4, value=merchant.first_name or "")
        sheet.cell(row=row_num, column=5, value=merchant.last_name or "")
        sheet.cell(row=row_num, column=6, value=merchant.email or "")
        sheet.cell(row=row_num, column=7, value=merchant.mobile or "")
        sheet.cell(row=row_num, column=8, value=merchant.aadhaar_number or "")
        sheet.cell(row=row_num, column=9, value=merchant.gst_number or "")
        sheet.cell(row=row_num, column=10, value=merchant.pan_number or "")
        sheet.cell(row=row_num, column=11, value=merchant.shop_name or "")
        sheet.cell(row=row_num, column=12, value=merchant.address or "")
        sheet.cell(row=row_num, column=13, value=merchant.city or "")
        sheet.cell(row=row_num, column=14, value=merchant.state or "")
        sheet.cell(row=row_num, column=15, value=merchant.country or "")
        sheet.cell(row=row_num, column=16, value=merchant.pincode or "")
        sheet.cell(row=row_num, column=17, value=merchant.created_at.strftime("%Y-%m-%d %H:%M:%S") if merchant.created_at else "")

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Merchants_Projects.xlsx"'

    return response


def export_disabled_merchants(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Disabled Merchants"

    # Add headers to the sheet
    headers = [
        "Merchant ID", "User Type", "Project Name", "First Name", "Last Name",
        "Email", "Mobile", "Aadhaar", "GST Number", "PAN", "Shop Name",
        "Address", "City", "State", "Country", "Pincode", "Status", "Created At"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    # Fetch data for merchants with status "Inactive"
    disabled_merchants = Merchant.objects.filter(status="Inactive")
    if not disabled_merchants.exists():
        print("No disabled merchants found.")  # Debugging log

    # Add data to the Excel sheet
    for row_num, merchant in enumerate(disabled_merchants, 2):
        sheet.cell(row=row_num, column=1, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=2, value=merchant.user_type or "")
        sheet.cell(row=row_num, column=3, value=merchant.project_name or "")
        sheet.cell(row=row_num, column=4, value=merchant.first_name or "")
        sheet.cell(row=row_num, column=5, value=merchant.last_name or "")
        sheet.cell(row=row_num, column=6, value=merchant.email or "")
        sheet.cell(row=row_num, column=7, value=merchant.mobile or "")
        sheet.cell(row=row_num, column=8, value=merchant.aadhaar_number or "")
        sheet.cell(row=row_num, column=9, value=merchant.gst_number or "")
        sheet.cell(row=row_num, column=10, value=merchant.pan_number or "")
        sheet.cell(row=row_num, column=11, value=merchant.shop_name or "")
        sheet.cell(row=row_num, column=12, value=merchant.address or "")
        sheet.cell(row=row_num, column=13, value=merchant.city or "")
        sheet.cell(row=row_num, column=14, value=merchant.state or "")
        sheet.cell(row=row_num, column=15, value=merchant.country or "")
        sheet.cell(row=row_num, column=16, value=merchant.pincode or "")
        sheet.cell(row=row_num, column=17, value=merchant.status or "")
        sheet.cell(row=row_num, column=18, value=merchant.created_at.strftime("%Y-%m-%d %H:%M:%S") if merchant.created_at else "")

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Disabled_Merchants.xlsx"'

    return response

def export_project_wise_balance(request):
    return render(request, 'bopo_admin/Payment/reports.html') 

def export_merchant_wise_balance(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Merchant-Wise Balance"

    # Add headers to the sheet
    headers = [
        "Merchant ID", "Merchant Name", "Email", "Mobile", 
        "Available Points", "Status", "Created At"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    # Fetch data from the MerchantPoints table
    merchant_points = MerchantPoints.objects.select_related('merchant').all()
    if not merchant_points.exists():
        print("No merchant points found.")  # Debugging log

    # Add data to the Excel sheet
    for row_num, merchant_point in enumerate(merchant_points, 2):
        # total_points = getattr(merchant_point, "total_points", 0)
        # used_points = getattr(merchant_point, "used_points", 0)
        available_points = merchant_point.points

        merchant = merchant_point.merchant
        sheet.cell(row=row_num, column=1, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=2, value=f"{merchant.first_name} {merchant.last_name}" or "")
        sheet.cell(row=row_num, column=3, value=merchant.email or "")
        sheet.cell(row=row_num, column=4, value=merchant.mobile or "")
        # sheet.cell(row=row_num, column=5, value=merchant.project_name or "")
        # sheet.cell(row=row_num, column=6, value=total_points)
        # sheet.cell(row=row_num, column=7, value=used_points)
        sheet.cell(row=row_num, column=5, value=available_points)
        sheet.cell(row=row_num, column=6, value=merchant.status or "")
        sheet.cell(row=row_num, column=7, value=merchant.created_at.strftime("%Y-%m-%d %H:%M:%S") if merchant.created_at else "")

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Merchant_Wise_Balance.xlsx"'

    return response


def export_customer_wise_balance(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Customer-Wise Balance"

    # Add headers to the sheet
    headers = [
        "Customer ID", "Customer Name", "Email", "Mobile", 
        "Available Points", "Created At"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    # Fetch data from the CustomerPoints table
    customer_points = CustomerPoints.objects.select_related('customer').all()
    if not customer_points.exists():
        print("No customer points found.")  # Debugging log

    # Add data to the Excel sheet
    for row_num, customer_point in enumerate(customer_points, 2):
        available_points = customer_point.points

        customer = customer_point.customer
        sheet.cell(row=row_num, column=1, value=customer.customer_id or "")
        sheet.cell(row=row_num, column=2, value=f"{customer.first_name} {customer.last_name}" or "")
        sheet.cell(row=row_num, column=3, value=customer.email or "")
        sheet.cell(row=row_num, column=4, value=customer.mobile or "")
        sheet.cell(row=row_num, column=5, value=available_points)
        # sheet.cell(row=row_num, column=6, value=customer.status or "")
        sheet.cell(row=row_num, column=7, value=customer.created_at.strftime("%Y-%m-%d %H:%M:%S") if customer.created_at else "")

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Customer_wise_Balance.xlsx"'

    return response


    
def export_customer_transaction(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Customer Transaction History"

    # Add headers to the sheet
    headers = [
        "Customer ID", "Customer Name", "Email", "Mobile", 
        "Transaction Type", "Points"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    # Fetch data from the History table
    transactions = History.objects.select_related('customer').all()
    if not transactions.exists():
        print("No transaction history found.")  # Debugging log

    # Add data to the Excel sheet
    for row_num, transaction in enumerate(transactions, 2):
        customer = transaction.customer
        # sheet.cell(row=row_num, column=1, value=transaction.id or "")
        sheet.cell(row=row_num, column=1, value=customer.customer_id or "")
        sheet.cell(row=row_num, column=2, value=f"{customer.first_name} {customer.last_name}" or "")
        sheet.cell(row=row_num, column=3, value=customer.email or "")
        sheet.cell(row=row_num, column=4, value=customer.mobile or "")
        sheet.cell(row=row_num, column=5, value=transaction.transaction_type or "")
        sheet.cell(row=row_num, column=6, value=transaction.points or 0)
        # sheet.cell(row=row_num, column=8, value=transaction.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if transaction.transaction_date else "")
        # sheet.cell(row=row_num, column=9, value=transaction.description or "")

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Customer_Transaction_History.xlsx"'

    return response

def export_payment_dues(request):
    return render(request, 'bopo_admin/Payment/reports.html') 

def export_award_transaction(request):
    return render(request, 'bopo_admin/Payment/reports.html') 

def export_corporate_merchant(request):
    return render(request, 'bopo_admin/Payment/reports.html')


    
    


# Get all states
def get_states(request):
    states = State.objects.all().values('id', 'name')
    return JsonResponse(list(states), safe=False)

# Get cities for a given state
def get_cities(request, state_id):
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)