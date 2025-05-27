from datetime import date, datetime, timezone
from io import BytesIO
import json

import os
import random
import string
from sys import prefix
# from tkinter.font import Font
from django.db.models import Max
from django.http import FileResponse, HttpResponse, JsonResponse
from django.db.models.functions import Cast, Substr
from django.shortcuts import get_object_or_404, render
import openpyxl
from requests import Response
from rest_framework import status
from openpyxl.styles import Font
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from datetime import datetime



from accounts import models
from accounts.models import Corporate, Customer, Logo, Terminal
from accounts.views import generate_terminal_id
from accounts.models import Corporate, Customer, Merchant, Terminal
from accounts.views import generate_terminal_id
from bopo_award.models import AwardPoints, CashOut, CustomerPoints, Help, History, MerchantPoints, ModelPlan, PaymentDetails, SuperAdminPayment

# from django.contrib.auth import authenticate 
# from django.shortcuts import redirect
from .models import AccountInfo, BopoAdmin, DeductSetting, Employee, EmployeeRole, MerchantCredential, MerchantLogin, Notification, Reducelimit, SecurityQuestion, Topup, UploadedFile
from django.http import JsonResponse
from .models import State, City
from bopo_admin.models import Employee
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction




# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

# def login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 auth_login(request, user)
#                 return redirect('home')  # Redirect to home after successful login
#             else:
#                 error_message = 'Invalid login credentials'
#                 return render(request, 'login.html', {'error_message': error_message})
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html', {'form': form})

from django.contrib.auth import logout
def custom_logout_view(request):
    logout(request)
    return redirect('login')

def corporate_admin(request):
    corporates = Corporate.objects.all()
    corporate_data = []

    for corporate in corporates:
        # Fetch merchants linked to the corporate
        merchants = Merchant.objects.filter(corporate_id=corporate.corporate_id, user_type='corporate')
        corporate_data.append({
            "corporate": corporate,
            "merchants": merchants
        })

    return render(request, 'bopo_admin/Payment/corporate_admin.html', {
        "corporate_data": corporate_data
    })

# def profile(request):
#         return render(request, 'bopo_admin/profile.html')


# def dashboard(request):
#     print("User role in session:", request.session.get('user_role'))  # Debug line
#     user_role = request.session.get('user_role')
#     return render(request, 'base.html', {'user_role': user_role})


from django.shortcuts import render
from accounts.models import Merchant  # Replace `your_app` and `Merchant` with actual names

def terminals(request):
    merchants = Merchant.objects.all().order_by('merchant_id')
    return render(request, 'bopo_admin/Payment/terminals.html', {'merchants': merchants})

from django.http import JsonResponse
from accounts.models import Merchant, Terminal

def get_terminals(request, merchant_id):
    try:
        merchant = Merchant.objects.get(merchant_id=merchant_id)
    except Merchant.DoesNotExist:
        return JsonResponse({'error': 'Merchant not found'}, status=404)

    terminals = Terminal.objects.filter(merchant_id=merchant)

    terminal_data = [
        {'terminal_id': terminal.terminal_id, 'tid_pin': terminal.tid_pin, 'status': terminal.status }
        for terminal in terminals
    ]

    return JsonResponse({'terminals': terminal_data})

import random
import string
from django.http import JsonResponse
from accounts.models import Merchant, Terminal

def generate_terminal_id():
    """Generate a unique terminal ID."""
    return "TID" + ''.join(random.choices(string.digits, k=8))

def add_terminal(request, merchant_id):
    """Generate a new terminal and pin for the merchant."""
    try:
        merchant = Merchant.objects.get(merchant_id=merchant_id)
    except Merchant.DoesNotExist:
        return JsonResponse({'error': 'Merchant not found'}, status=404)

    # Generate unique terminal ID
    terminal_id = generate_terminal_id()
    while Terminal.objects.filter(terminal_id=terminal_id).exists():
        terminal_id = generate_terminal_id()  # Ensure it's unique

    # Generate a 4-digit PIN
    tid_pin = random.randint(1000, 9999)

    # Save terminal info to the database
    terminal = Terminal.objects.create(
        terminal_id=terminal_id,
        tid_pin=tid_pin,
        merchant_id=merchant
        
    )

    # Return the newly created terminal details
    return JsonResponse({'terminal_id': terminal.terminal_id, 'tid_pin': terminal.tid_pin, 'status':terminal.status})

# In views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def update_terminal_pin(request, merchant_id, terminal_id):
    if request.method == 'POST':
        body = json.loads(request.body)
        new_pin = body.get('tid_pin')

        try:
            # Validate that new_pin is a 4-digit number
            if not new_pin or not str(new_pin).isdigit() or len(str(new_pin)) != 4:
                return JsonResponse({'success': False, 'error': 'PIN must be a 4-digit number'})

            
            # Fetch the merchant by its ID
            merchant = Merchant.objects.get(merchant_id=merchant_id)
            
            # Now fetch the terminal by both merchant and terminal_id
            terminal = Terminal.objects.get(merchant_id=merchant, terminal_id=terminal_id)
            
            terminal.tid_pin = new_pin
            terminal.save()
            return JsonResponse({'success': True})
        except Merchant.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Merchant not found'})
        except Terminal.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Terminal not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


import json
from django.http import JsonResponse
from datetime import datetime
from accounts.models import Terminal

def toggle_terminal_status(request, terminal_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            is_active = data.get("is_active")

            # Lookup by terminal_id field, not id
            terminal = Terminal.objects.get(terminal_id=terminal_id)

            if is_active:
                terminal.status = "Active"
            else:
                terminal.status = "Inactive"

            terminal.save()

            return JsonResponse({"success": True, "status": terminal.status})
        except Terminal.DoesNotExist:
            return JsonResponse({"success": False, "error": "Terminal not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


from datetime import datetime, time, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    user = request.user

    # Get today's and yesterday's date (timezone aware)
    today_date = timezone.localdate()  # Asia/Kolkata date, thanks to your TIME_ZONE setting
    yesterday_date = today_date - timedelta(days=1)

    # Build timezone-aware datetime ranges for filtering
    start_today = timezone.make_aware(datetime.combine(today_date, time.min), timezone.get_current_timezone())
    end_today = timezone.make_aware(datetime.combine(today_date, time.max), timezone.get_current_timezone())

    start_yesterday = timezone.make_aware(datetime.combine(yesterday_date, time.min), timezone.get_current_timezone())
    end_yesterday = timezone.make_aware(datetime.combine(yesterday_date, time.max), timezone.get_current_timezone())

    # Total counts
    total_projects = Corporate.objects.count()
    # completed_projects = Corporate.objects.filter(status="Completed").count()
    active_projects = Corporate.objects.filter(status="Active").count()

    project_progress = (active_projects / total_projects * 100) if total_projects > 0 else 0

    total_merchants = Merchant.objects.count()
    active_merchants = Merchant.objects.filter(status="Active").count()
    merchant_progress = (active_merchants / total_merchants * 100) if total_merchants > 0 else 0

    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(status="Active").count() 
    total_users = total_customers + total_merchants + total_projects

    # Daily counts using range filter
    daily_projects = Corporate.objects.filter(created_at__range=(start_today, end_today)).count()
    daily_merchants = Merchant.objects.filter(created_at__range=(start_today, end_today)).count()
    daily_customers = Customer.objects.filter(created_at__range=(start_today, end_today)).count()

    # Yesterday counts using range filter
    yesterday_projects = Corporate.objects.filter(created_at__range=(start_yesterday, end_yesterday)).count()
    yesterday_merchants = Merchant.objects.filter(created_at__range=(start_yesterday, end_yesterday)).count()
    yesterday_customers = Customer.objects.filter(created_at__range=(start_yesterday, end_yesterday)).count()

    daily_project_growth = (
    ((daily_projects - yesterday_projects) / yesterday_projects * 100)
    if yesterday_projects > 0 else 0
    )
    daily_merchant_growth = (
        ((daily_merchants - yesterday_merchants) / yesterday_merchants * 100)
        if yesterday_merchants > 0 else 0
    )
    daily_customer_growth = (
        ((daily_customers - yesterday_customers) / yesterday_customers * 100)
        if yesterday_customers > 0 else 0
    )


    # Daily Total Users Growth
    daily_total_users = daily_projects + daily_merchants + daily_customers
    yesterday_total_users = yesterday_projects + yesterday_merchants + yesterday_customers

    daily_user_growth = (
        ((daily_total_users - yesterday_total_users) / yesterday_total_users * 100)
        if yesterday_total_users > 0 else 0
    )
        
    print("Today projects:", daily_projects)
    print("Yesterday projects:", yesterday_projects)
    print("Growth:", daily_project_growth)
    
    print("Today merchant:", daily_merchants)
    print("Yesterday merchant:", yesterday_merchants)
    print("Growth:", daily_merchant_growth)
    
    
    print("Today customer:", daily_customers)
    print("Yesterday customer:", yesterday_customers)
    print("Growth:", daily_customer_growth)


    print("Today users:", daily_total_users)
    print("Yesterday users:", yesterday_total_users)
    print("Growth:", daily_user_growth)
    
    # Chart data for bar graph
    chart_data = {
        "projects": [total_projects, active_projects],
        "merchants": [total_merchants, active_merchants],
        "customers": [total_customers, active_customers],
    }

    context = {
        "user": user,
        "title": "Welcome to Bopo Admin Dashboard",
        "description": "Manage merchants, customers, and projects efficiently.",

        # Total values
        "total_projects": total_projects,
        "project_progress": project_progress,
        "total_merchants": total_merchants,
        "merchant_progress": merchant_progress,
        "total_customers": total_customers,
        "total_users": total_users,

        # Daily values
        "daily_projects": daily_projects,
        "daily_merchants": daily_merchants,
        "daily_customers": daily_customers,

        # Daily growth
        "daily_project_growth": daily_project_growth,
        "daily_merchant_growth": daily_merchant_growth,
        "daily_customer_growth": daily_customer_growth,
        "daily_user_growth": daily_user_growth,

        # Chart data
        "chart_data": chart_data,
    }

    # Corporate admin dashboard data
    if user.role == 'corporate_admin':
        corporate = user.corporate

        # Merchants under corporate
        project_merchants = Merchant.objects.filter(project_name=corporate)

        total_project_merchants = project_merchants.count()
        active_project_merchants = project_merchants.filter(status="Active").count()

        project_merchant_progress = (
            (active_project_merchants / total_project_merchants * 100)
            if total_project_merchants > 0 else 0
        )

        daily_project_merchants = project_merchants.filter(created_at__range=(start_today, end_today)).count()
        yesterday_project_merchants = project_merchants.filter(created_at__range=(start_yesterday, end_yesterday)).count()
        daily_project_merchant_growth = (
            ((daily_project_merchants - yesterday_project_merchants) / yesterday_project_merchants * 100)
            if yesterday_project_merchants > 0 else 0
        )

        # Terminals under corporate
        project_terminals = Terminal.objects.filter(merchant_id__project_name=corporate)

        total_project_terminals = project_terminals.count()
        active_project_terminals = project_terminals.filter(status="Active").count()

        project_terminal_progress = (
            (active_project_terminals / total_project_terminals * 100)
            if total_project_terminals > 0 else 0
        )

        daily_project_terminals = project_terminals.filter(created_at__range=(start_today, end_today)).count()
        yesterday_project_terminals = project_terminals.filter(created_at__range=(start_yesterday, end_yesterday)).count()
        daily_project_terminal_growth = (
            ((daily_project_terminals - yesterday_project_terminals) / yesterday_project_terminals * 100)
            if yesterday_project_terminals > 0 else 0
        )

        # Total users = merchants + terminals
        total_users = total_project_merchants + total_project_terminals
        daily_total_users = daily_project_merchants + daily_project_terminals
        yesterday_total_users = yesterday_project_merchants + yesterday_project_terminals
        
        daily_project_merchant_growth = (
            ((daily_project_merchants - yesterday_project_merchants) / yesterday_project_merchants * 100)
            if yesterday_project_merchants > 0 else 0
        )
        daily_project_terminal_growth = (
            ((daily_project_terminals - yesterday_project_terminals) / yesterday_project_terminals * 100)
            if yesterday_project_terminals > 0 else 0
        )
        
        daily_user_growth = (
        ((daily_total_users - yesterday_total_users) / yesterday_total_users * 100)
        if yesterday_total_users > 0 else 0
        )


        print("Today terminals:", daily_project_terminals)
        print("Yesterday terminals:", yesterday_project_terminals)
        print("Growth:", daily_project_terminal_growth)
        
       
        print("Today users:", daily_total_users)
        print("Today users:", yesterday_total_users)
        

        chart_data = {
            "merchants": [total_project_merchants, active_project_merchants],
            "terminals": [total_project_terminals, active_project_terminals],
        }

        chart_labels = ["Merchants", "Terminals"]

        context.update({
            "total_merchants": total_project_merchants,
            "merchant_progress": project_merchant_progress,
            "daily_merchant_growth": daily_project_merchant_growth,

            "total_terminals": total_project_terminals,
            "terminal_progress": project_terminal_progress,
            "daily_terminal_growth": daily_project_terminal_growth,
            
            "active_terminals": active_project_terminals,
            
            "total_users": total_users,
            "daily_user_growth": daily_user_growth,

            "chart_data": chart_data,
            "chart_labels": chart_labels,
        })

        return render(request, 'bopo_admin/Corporate/corporate_dashboard.html', context)

    elif user.role == 'employee':
        employee = user.employee
        role_permissions = EmployeeRole.objects.get(employee=employee)
        context['role_permissions'] = role_permissions
        if (
            role_permissions.corporate_merchant or
            role_permissions.individual_merchant or
            role_permissions.merchant_send_credentials or
            role_permissions.merchant_limit or
            role_permissions.merchant_login_page_info or
            role_permissions.merchant_send_notification or
            role_permissions.merchant_received_offers
        ):
            context['merchant'] = True
        return render(request, 'bopo_admin/home.html', context)

    else:
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
from django.shortcuts import get_object_or_404

def get_customer(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)

    # Retrieve the state object by its name (if state is stored as a string)
    state_obj = State.objects.get(name=customer.state)  # Assuming state is a string, get State object by name

    # Retrieve cities based on selected state
    cities = City.objects.filter(state=state_obj)  # Now we use the State object

    # Convert cities to a dictionary for use in the frontend
    city_data = [{"id": city.id, "name": city.name} for city in cities]

    # Data to send to the frontend
    data = {
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "mobile": customer.mobile,
        "age": customer.age,
        "aadhar_number": customer.aadhar_number,
        "pin": customer.pin,
        "address": customer.address,
        "pincode": customer.pincode,
        "gender": customer.gender,
        "pan_number": customer.pan_number,
        "state": customer.state,  # Prefilled state (assuming it's a string or related field)
        "city": customer.city,    # Prefilled city (assuming it's a string or related field)
        "states": [{"id": state.id, "name": state.name} for state in State.objects.all()],  # List of all states
        "cities": city_data,  # List of cities filtered by the selected state
    }

    return JsonResponse(data)

# @csrf_exempt  
# def update_customer(request, customer_id):
#     if request.method == "POST":
#         try:
#             customer = Customer.objects.get(customer_id=customer_id)

#             email = request.POST.get('email')
#             mobile = request.POST.get('mobile')

#             # Basic validation (you can extend this as needed)
#             if not email or not mobile:
#                 return JsonResponse({'success': False, 'error': 'Email and Mobile are required'})

         
#             # Update only email and mobile
#             customer.email = email
#             customer.mobile = mobile
#             customer.save()

#             return JsonResponse({
#                 "success": True,
#                 "message": "Customer updated successfully!"
#             })

#         except Customer.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Customer not found'})

#     return JsonResponse({'success': False, 'error': 'Invalid request'})



@csrf_exempt
def update_customer(request, customer_id):
    if request.method == "POST":
        try:
            customer = Customer.objects.get(customer_id=customer_id)

            email = request.POST.get('email')
            mobile = request.POST.get('mobile')

            if not email or not mobile:
                return JsonResponse({'success': False, 'error': 'Email and Mobile are required'})

            # Check duplication in Customer (exclude current customer)
            if Customer.objects.filter(email=email).exclude(customer_id=customer_id).exists():
                return JsonResponse({"success": False, "message": "Email is already registered"})

            if Customer.objects.filter(mobile=mobile).exclude(customer_id=customer_id).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Check duplication in Corporate (no exclude needed here)
            if Corporate.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            if Corporate.objects.filter(mobile=mobile).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # If all checks pass, update
            customer.email = email
            customer.mobile = mobile
            customer.save()

            return JsonResponse({
                "success": True,
                "message": "Customer updated successfully!"
            })

        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


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


# def toggle_status(request, merchant_id):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             is_active = data.get("is_active")

#             merchant = Merchant.objects.get(id=merchant_id)

#             if is_active:
#                 merchant.status = "Active"
#                 merchant.verified_at = datetime.now()
#             else:
#                 merchant.status = "Inactive"
#                 merchant.verified_at = None

#             merchant.save()

#             return JsonResponse({"success": True, "status": merchant.status})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     return JsonResponse({"success": False, "error": "Invalid request"})


#main
# from django.utils import timezone

# def toggle_status(request, entity_type, entity_id):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             is_active = data.get("is_active")

#             if entity_type == "customer":
#                 instance = Customer.objects.get(customer_id=entity_id)
#             elif entity_type == "merchant":
#                 instance = Merchant.objects.get(merchant_id=entity_id)
#             elif entity_type == "corporate":
#                 instance = Corporate.objects.get(corporate_id=entity_id)
#             else:
#                 return JsonResponse({"success": False, "error": "Invalid entity type"})

#             instance.status = "Active" if is_active else "Inactive"
#             instance.verified_at = timezone.now() if is_active else None
#             instance.save()

#             return JsonResponse({"success": True, "status": instance.status})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     return JsonResponse({"success": False, "error": "Invalid request method"})


from django.views.decorators.http import require_POST

@require_POST
def toggle_status(request, entity_type, entity_id):
    try:
        data = json.loads(request.body)
        is_active = data.get("is_active")

        affected_ids = []

        if entity_type == "customer":
            instance = Customer.objects.get(customer_id=entity_id)

        elif entity_type == "merchant":
            instance = Merchant.objects.get(merchant_id=entity_id)

        elif entity_type == "corporate":
            instance = Corporate.objects.get(corporate_id=entity_id)
            related_merchants = Merchant.objects.filter(project_name=instance)

            if is_active:
                related_merchants.update(status="Active", verified_at=timezone.now())
            else:
                related_merchants.update(status="Inactive", verified_at=None)

            # Capture affected merchant IDs
            affected_ids = list(related_merchants.values_list("merchant_id", flat=True))
            print("Affected Merchant IDs:", affected_ids)

        else:
            return JsonResponse({"success": False, "error": "Invalid entity type"})

        instance.status = "Active" if is_active else "Inactive"
        instance.verified_at = timezone.now() if is_active else None
        instance.save()

        return JsonResponse({
            "success": True,
            "status": instance.status,
            "affected_merchants": affected_ids
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    
    
    
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

            # Extract form data
            select_project = request.POST.get("select_project")
            project_type = request.POST.get("project_type")
            project_name = request.POST.get("project_name", "")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            aadhaar_number = request.POST.get("aadhaar_number")
            pin = request.POST.get("pin")
            gst_number = request.POST.get("gst_number")
            shop_name = request.POST.get("shop_name")
            pan_number = request.POST.get("pan_number")
            address = request.POST.get("address")
            legal_name = request.POST.get("legal_name")
            pincode = request.POST.get("pincode")
            account_type = request.POST.get("account_type", "normal")
            city_id = request.POST.get("city")
            state_id = request.POST.get("state")
            country = request.POST.get("country", "India")
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)

            logo_file = request.FILES.get("logo")
            logo_instance = None

            if logo_file:
                print("Logo file received:", logo_file.name)  # Debugging line
                logo_instance = Logo.objects.create(logo=logo_file)
                print("Logo saved:", logo_instance.logo.url)  # Debugging line


            # Unique field checks for email, mobile, Aadhaar number, etc.
            if Merchant.objects.filter(email=email).exists() or Corporate.objects.filter(email=email).exists():
                message = "Email is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            if Merchant.objects.filter(mobile=mobile).exists() or Corporate.objects.filter(mobile=mobile).exists():
                message = "Mobile number is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            if Merchant.objects.filter(aadhaar_number=aadhaar_number).exists() or Corporate.objects.filter(aadhaar_number=aadhaar_number).exists():
                message = "Aadhaar number is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            # Corporate ID Generation Logic
            last_corporate = Corporate.objects.exclude(corporate_id=None).order_by("-corporate_id").first()
            new_corporate_id = 1 if not last_corporate else int(last_corporate.corporate_id[6:]) + 1
            corporate_id = f"CORP{new_corporate_id:06d}"

            # Handling Existing Project
            if project_type == "Existing Project" and select_project:
                corporate = Corporate.objects.get(id=select_project)
                project_name = corporate.project_name
                project_id = corporate.project_id

                # # Merchant ID Generation
                # project_abbr = project_name[:4].upper()
                # random_number = ''.join(random.choices(string.digits, k=11))
                # merchant_id = f"{project_abbr}{random_number}"
                
                prefix = "MID"
                merchant_id = f"{prefix}{''.join(random.choices(string.digits, k=11))}"
                # otp = random.randint(100000, 999999)

                # Create the Merchant instance
                merchant = Merchant.objects.create(
                    user_type='corporate',
                    merchant_id=merchant_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    mobile=mobile,
                    aadhaar_number=aadhaar_number,
                    pin=pin,
                    gst_number=gst_number,
                    pan_number=pan_number,
                    shop_name=shop_name,
                    legal_name=legal_name,
                    address=address,
                    pincode=pincode,
                    state=state,
                    city=city,
                    country=country,
                    corporate_id=corporate.corporate_id,
                    project_name=corporate,
                    logo=logo_instance  # Associate the logo with the merchant
                )

                merchant = Merchant.objects.get(merchant_id=merchant_id)

                # Terminal Generation Logic
                terminal_id = "TID" + ''.join(random.choices(string.digits, k=8))
                tid_pin = random.randint(1000, 9999)

                Terminal.objects.create(
                    terminal_id=terminal_id,
                    tid_pin=tid_pin,
                    merchant_id=merchant
                )

            elif project_type == "New Project":
                # Create New Project and Corporate Instance
                if not project_name:
                    message = "Project name is required for new projects."
                    return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

                # Project ID Generation
                last_project = Corporate.objects.exclude(project_id=None).order_by("-project_id").first()
                new_project_id = 1 if not last_project else int(last_project.project_id[4:]) + 1
                project_id = f"PROJ{new_project_id:06d}"

                corporate = Corporate.objects.create(
                    select_project=select_project,
                    corporate_id=corporate_id,
                    project_name=project_name,
                    project_id=project_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    mobile=mobile,
                    aadhaar_number=aadhaar_number,
                    pin=pin,
                    gst_number=gst_number,
                    pan_number=pan_number,
                    shop_name=shop_name,
                    legal_name=legal_name,
                    address=address,
                    pincode=pincode,
                    state=state,
                    city=city,
                    country=country,
                    role="admin",
                    account_type=account_type, 
                    logo=logo_instance  # Associate the logo with the new corporate account
                )

                # Create BopoAdmin user
                bopo_admin = BopoAdmin(username=corporate_id, role="corporate_admin", corporate=corporate)
                bopo_admin.set_password(pin)
                bopo_admin.save()

            else:
                message = "Invalid project type selected."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            success_message = "Merchant added successfully."
            return JsonResponse({"success": True, "message": success_message}) if is_ajax else redirect_with_success(success_message)

        except Exception as e:
            print("Error saving merchant:", e)
            return JsonResponse({"success": False, "message": "wrong from backend."})

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


def get_corporate(request, corporate_id):
    try:
        corporate = Corporate.objects.get(corporate_id=corporate_id)

        # Assuming state is a string, get the State object by name
        state_obj = State.objects.get(name=corporate.state)

        # Retrieve cities based on selected state
        cities = City.objects.filter(state=state_obj)

        # Convert cities to a dictionary for use in the frontend
        city_data = [{"id": city.id, "name": city.name} for city in cities]


        data = {
            'corporate_id': corporate.corporate_id,
            'project_name': corporate.project_name,
            # 'project_id': corporate.project_id,
            'first_name': corporate.first_name,
            'last_name': corporate.last_name,
            'email': corporate.email,
            'mobile': corporate.mobile,
            'aadhaar_number': corporate.aadhaar_number,
            'pin': corporate.pin,
            'gst_number': corporate.gst_number,
            'pan_number': corporate.pan_number,
            'shop_name': corporate.shop_name,
            'legal_name': corporate.legal_name,
            'address': corporate.address,
            'pincode': corporate.pincode,
            "state": corporate.state,  
            "city": corporate.city,   
            'country': corporate.country,
            "states": [{"id": state.id, "name": state.name} for state in State.objects.all()],  
            "cities": city_data,  
        }

        return JsonResponse(data)

    except Corporate.DoesNotExist:
        return JsonResponse({'error': 'Corporate not found'}, status=404)
    except State.DoesNotExist:
        return JsonResponse({'error': 'State not found'}, status=404)
    except City.DoesNotExist:
        return JsonResponse({'error': 'City not found'}, status=404)


# from django.http import JsonResponse
# from accounts.models import Corporate


# @csrf_exempt  
# def update_corporate(request, corporate_id):
#     if request.method == 'POST':
#         try:
#             corporate = Corporate.objects.get(corporate_id=corporate_id)

#             email = request.POST.get('email')
#             mobile = request.POST.get('mobile')
            
           
#             if email:
#                 corporate.email = email
#             if mobile:
#                 corporate.mobile = mobile

#             corporate.save()

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Email and mobile updated successfully!',
#                 'updatedCorporate': {
#                     'corporate_id': corporate.corporate_id,
#                     'email': corporate.email,
#                     'mobile': corporate.mobile,
#                 }
#             })

#         except Corporate.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Corporate not found'}, status=404)

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


from django.http import JsonResponse
from accounts.models import Corporate, Merchant, Customer
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  
def update_corporate(request, corporate_id):
    if request.method == 'POST':
        try:
            corporate = Corporate.objects.get(corporate_id=corporate_id)

            email = request.POST.get('email')
            mobile = request.POST.get('mobile')

            # Check duplicate email
            if email:
                if Corporate.objects.filter(email=email).exclude(corporate_id=corporate_id).exists():
                    return JsonResponse({"success": False, "message": "Email is already registered."})
                if Merchant.objects.filter(email=email).exists():
                    return JsonResponse({"success": False, "message": "Email is already registered."})
                if Customer.objects.filter(email=email).exists():
                    return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile
            if mobile:
                if Corporate.objects.filter(mobile=mobile).exclude(corporate_id=corporate_id).exists():
                    return JsonResponse({"success": False, "message": "Mobile number is already registered ."})
                if Merchant.objects.filter(mobile=mobile).exists():
                    return JsonResponse({"success": False, "message": "Mobile number is already registered."})
                if Customer.objects.filter(mobile=mobile).exists():
                    return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Update fields
            if email:
                corporate.email = email
            if mobile:
                corporate.mobile = mobile

            corporate.save()

            return JsonResponse({
                'success': True,
                'message': 'Email and mobile updated successfully!',
                'updatedCorporate': {
                    'corporate_id': corporate.corporate_id,
                    'email': corporate.email,
                    'mobile': corporate.mobile,
                }
            })

        except Corporate.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Corporate not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


from django.http import JsonResponse
from accounts.models import Merchant

def get_copmerchant(request, merchant_id):
    try:
        merchant = Merchant.objects.get(id=merchant_id)

        state_obj = State.objects.get(name=merchant.state)
        city_obj = City.objects.get(name=merchant.city)

        cities = City.objects.filter(state=state_obj)
        city_data = [{"id": city.id, "name": city.name} for city in cities]

        data = {
            'merchant_id': merchant.id,
            'first_name': merchant.first_name,
            'last_name': merchant.last_name,
            'email': merchant.email,
            'mobile': merchant.mobile,
            'aadhaar_number': merchant.aadhaar_number,
            'pan_number': merchant.pan_number,
            'gst_number': merchant.gst_number,
            'pin': merchant.pin,
            'legal_name': merchant.legal_name,
            'project_name': merchant.project_name.project_name if merchant.project_name else None,  # ✅ FIXED
            'shop_name': merchant.shop_name,
            'address': merchant.address,
            'pincode': merchant.pincode,
            "state": merchant.state,
            "city": merchant.city,
            'country': merchant.country,
            "states": [{"id": state.id, "name": state.name} for state in State.objects.all()],
            "cities": city_data,
        }

        return JsonResponse(data)

    except Merchant.DoesNotExist:
        return JsonResponse({'error': 'Merchant not found'}, status=404)
    except State.DoesNotExist:
        return JsonResponse({'error': 'State not found'}, status=404)
    except City.DoesNotExist:
        return JsonResponse({'error': 'City not found'}, status=404)



# from django.http import JsonResponse
# from accounts.models import Merchant, Corporate


# def update_copmerchant(request, merchant_id):
#     if request.method == "POST":
#         if not merchant_id:
#             return JsonResponse({'success': False, 'error': 'Missing merchant ID'}, status=400)

#         try:
#             merchant = Merchant.objects.get(id=merchant_id)

#             email = request.POST.get('email', '').strip()
#             mobile = request.POST.get('mobile', '').strip()

#             if email:
#                 merchant.email = email
#             if mobile:
#                 merchant.mobile = mobile

#             merchant.save()

#             return JsonResponse({
#                 "success": True,
#                 "message": "Email and mobile updated successfully!",
#                 "updatedMerchant": {
#                     "id": merchant.id,
#                     "email": merchant.email,
#                     "mobile": merchant.mobile,
#                 }
#             })

#         except Merchant.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Merchant not found'}, status=404)

#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)



def update_copmerchant(request, merchant_id):
    if request.method == "POST":
        if not merchant_id:
            return JsonResponse({'success': False, 'error': 'Missing merchant ID'}, status=400)

        try:
            merchant = Merchant.objects.get(id=merchant_id)

            email = request.POST.get('email', '').strip()
            mobile = request.POST.get('mobile', '').strip()

            # Check duplicate email in Merchant excluding current merchant
            if Merchant.objects.filter(email=email).exclude(id=merchant_id).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile in Merchant excluding current merchant
            if Merchant.objects.filter(mobile=mobile).exclude(id=merchant_id).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Check duplicate email in Corporate
            if Corporate.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile in Corporate
            if Corporate.objects.filter(mobile=mobile).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Update merchant email and mobile
            merchant.email = email
            merchant.mobile = mobile
            merchant.save()


            return JsonResponse({
                "success": True,
                "message": "Email and mobile updated successfully!",
                "updatedMerchant": {
                    "id": merchant.id,
                    "email": merchant.email,
                    "mobile": merchant.mobile,
                }
            })

        except Merchant.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Merchant not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# from django.http import JsonResponse
# from accounts.models import Merchant

# def get_copmerchant(request, merchant_id):
#     try:
#         merchant = Merchant.objects.get(id=merchant_id)

#         state_obj = State.objects.get(name=merchant.state)
#         city_obj = City.objects.get(name=merchant.city)

#         cities = City.objects.filter(state=state_obj)
#         city_data = [{"id": city.id, "name": city.name} for city in cities]

#         data = {
#             'merchant_id': merchant.id,
#             'first_name': merchant.first_name,
#             'last_name': merchant.last_name,
#             'email': merchant.email,
#             'mobile': merchant.mobile,
#             'aadhaar_number': merchant.aadhaar_number,
#             'pin': merchant.pin,
#             'pan_number': merchant.pan_number,
#             'gst_number': merchant.gst_number,
#             'legal_name': merchant.legal_name,
#             'project_name': merchant.project_name.project_name if merchant.project_name else None,  # ✅ FIXED
#             'shop_name': merchant.shop_name,
#             'address': merchant.address,
#             'pincode': merchant.pincode,
#             "state": merchant.state,
#             "city": merchant.city,
#             'country': merchant.country,
#             "states": [{"id": state.id, "name": state.name} for state in State.objects.all()],
#             "cities": city_data,
#         }

#         return JsonResponse(data)

#     except Merchant.DoesNotExist:
#         return JsonResponse({'error': 'Merchant not found'}, status=404)
#     except State.DoesNotExist:
#         return JsonResponse({'error': 'State not found'}, status=404)
#     except City.DoesNotExist:
#         return JsonResponse({'error': 'City not found'}, status=404)



# from django.http import JsonResponse
# from accounts.models import Merchant, Corporate

# def update_copmerchant(request):
#     if request.method == 'POST':
#         # Extract the data from the request (Assuming data comes as form data)
#         merchant_id = request.POST.get('merchant_id')
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         aadhaar = request.POST.get('aadhaar')
#         shop_name = request.POST.get('shop_name')
#         address = request.POST.get('address')
#         state = request.POST.get('state')
#         mobile = request.POST.get('mobile')
#         gst_number = request.POST.get('gst_number')
#         pan_number = request.POST.get('pan')
#         legal_name = request.POST.get('legal_name')
#         city = request.POST.get('city')
#         pincode = request.POST.get('pincode')
#         project_name = request.POST.get('project_name')
#         # select_project = request.POST.get('select_project')

#         try:
#             # Retrieve the merchant to update
#             merchant = Merchant.objects.get(id=merchant_id)

#             # Update the merchant fields
#             merchant.first_name = first_name
#             merchant.last_name = last_name
#             merchant.email = email
#             merchant.aadhaar_number = aadhaar
#             merchant.shop_name = shop_name
#             merchant.address = address
#             merchant.state = state
#             merchant.mobile = mobile
#             merchant.gst_number = gst_number
#             merchant.pan_number = pan_number
#             merchant.legal_name = legal_name
#             merchant.city = city
#             merchant.pincode = pincode
#             merchant.project_name = project_name
#             # merchant.select_project = select_project

#             # Save the updated merchant
#             merchant.save()

#             # Return a success response with the updated merchant data
#             return JsonResponse({
#                 'success': True 
#                 })

#         except Merchant.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Merchant not found.'})

#     else:
#         return JsonResponse({'success': False, 'message': 'Invalid request method.'})


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

    # Retrieve the state object by its name
    state_obj = State.objects.get(name=merchant.state)  # Assuming state is a string, get State object by name

    # Retrieve cities based on selected state
    cities = City.objects.filter(state=state_obj)  # Now we use the State object

    # Convert cities to a dictionary for use in the frontend
    city_data = [{"id": city.id, "name": city.name} for city in cities]
    

    # Data to send to the frontend
    data = {
        "id": merchant.id,
        "first_name": merchant.first_name,
        "last_name": merchant.last_name,
        "email": merchant.email,
        "mobile": merchant.mobile,
        "shop_name": merchant.shop_name,
        "address": merchant.address,
        "aadhaar_number": merchant.aadhaar_number,
        "pin": merchant.pin,
        "gst_number": merchant.gst_number,
        "pan_number": merchant.pan_number,
        "legal_name": merchant.legal_name,
        "state": merchant.state,
        "city": merchant.city,
        "pincode": merchant.pincode,
    }
    return JsonResponse(data)



# def update_merchant(request): 
#     if request.method == "POST":
#         merchant_id = request.POST.get('merchant_id')
#         email = request.POST.get('email')
#         mobile = request.POST.get('mobile')

#         try:
#             merchant = Merchant.objects.get(id=merchant_id)

#             # Update only email and mobile
#             merchant.email = email
#             merchant.mobile = mobile
#             merchant.save()

#             return JsonResponse({
#                 "success": True,
#                 "message": "Merchant updated successfully!"
#             })
#         except Merchant.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Merchant not found'})
#     return JsonResponse({'success': False, 'error': 'Invalid request'})



from django.http import JsonResponse
from accounts.models import Merchant, Corporate

def update_merchant(request): 
    if request.method == "POST":
        merchant_id = request.POST.get('merchant_id')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # Validate input
        if not merchant_id or not email or not mobile:
            return JsonResponse({'success': False, 'error': 'Merchant ID, email, and mobile are required.'})

        email = email.strip().lower()  # normalize email

        try:
            merchant = Merchant.objects.get(id=merchant_id)
            
            # Check duplicate email in Merchant excluding current merchant
            if Merchant.objects.filter(email=email).exclude(id=merchant_id).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile in Merchant excluding current merchant
            if Merchant.objects.filter(mobile=mobile).exclude(id=merchant_id).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Check duplicate email in Corporate
            if Corporate.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile in Corporate
            if Corporate.objects.filter(mobile=mobile).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Update merchant email and mobile
            merchant.email = email
            merchant.mobile = mobile
            merchant.save()

            return JsonResponse({
                "success": True,
                "message": "Merchant updated successfully!"
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
            # Get form data
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            aadhaar_number = request.POST.get("aadhaar_number")
            pin = request.POST.get("pin")
            gst_number = request.POST.get("gst_number")
            pan_number = request.POST.get("pan_number")
            shop_name = request.POST.get("shop_name")
            legal_name = request.POST.get("legal_name")
            address = request.POST.get("address")
            pincode = request.POST.get("pincode")
            state_id = request.POST.get("state")
            city_id = request.POST.get("city")
            country = request.POST.get("country", "India")

            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)

            # Uniqueness checks
            if Merchant.objects.filter(email=email).exists() or Corporate.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email ID already exists!"})
            if Merchant.objects.filter(mobile=mobile).exists():
                return JsonResponse({"success": False, "message": "Mobile number already exists!"})
            if Merchant.objects.filter(aadhaar_number=aadhaar_number).exists():
                return JsonResponse({"success": False, "message": "Aadhaar number already exists!"})
            if Merchant.objects.filter(pan_number=pan_number).exists():
                return JsonResponse({"success": False, "message": "PAN number already exists!"})

            # Generate merchant_id
            last_merchant = Merchant.objects.order_by('-id').first()
            next_id = 1 if not last_merchant else last_merchant.id + 1
            # merchant_id = f"MID{str(next_id).zfill(11)}"
            prefix = "MID"
            merchant_id = f"{prefix}{''.join(random.choices(string.digits, k=11))}"
            
            

            # Generate Terminal ID and TID PIN
            def generate_terminal_id():
                return "TID" + ''.join(random.choices(string.digits, k=8))

            terminal_id = generate_terminal_id()
            while Terminal.objects.filter(terminal_id=terminal_id).exists():
                terminal_id = generate_terminal_id()

            tid_pin = random.randint(1000, 9999)

            # ✅ Create the merchant
            merchant = Merchant.objects.create(
                merchant_id=merchant_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile=mobile,
                gst_number=gst_number,
                aadhaar_number=aadhaar_number,
                pin = pin,
                pan_number=pan_number,
                shop_name=shop_name,
                legal_name=legal_name,
                address=address,
                pincode=pincode,
                state=state,
                city=city,
                country=country,
            
            )

            # ✅ Save terminal info
            Terminal.objects.create(
                terminal_id=terminal_id,
                tid_pin=tid_pin,
                merchant_id=merchant
            )

            return JsonResponse({'success': True, 'message': 'Merchant added successfully!', 'merchant_id': merchant_id})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"An error occurred: {str(e)}"})

    return render(request, "bopo_admin/Merchant/add_individual_merchant.html")



def project_onboarding(request):
    return render(request, 'bopo_admin/project_onboarding.html')

def project_list(request):
    return render(request, 'bopo_admin/project_list.html')






# def merchant_credentials(request):
#     merchants = Merchant.objects.all().order_by('merchant_id')
#     corporates = Corporate.objects.all().order_by('project_name')

#     if request.method == 'POST':
#         project_id = request.POST.get('project')
#         merchant_id = request.POST.get('merchant_id')
#         terminal_id = request.POST.get('terminal_id_dropdown')

#         try:
#             merchant = Merchant.objects.get(merchant_id=merchant_id)
#             phone_number = merchant.mobile
#             if not phone_number.startswith('+'):
#                 phone_number = f'+91{phone_number}'

#            # Compose the SMS message
#             message_text = (
#                 f"Dear {merchant.first_name},\n\n"
#                 f"Your BOPO login credentials are as follows:\n"
#                 f"Merchant ID : {merchant_id}\n"
#                 f"Terminal ID : {terminal_id}\n\n"
#                 f"Please use these credentials to access your BOPO account.\n\n"
#                 f"Regards,\n"
#                 f"BOPO Support Team"
#             )
           
#             # Fetch Twilio credentials from Django settings
#             account_sid = settings.TWILIO_ACCOUNT_SID
#             auth_token = settings.TWILIO_AUTH_TOKEN
#             twilio_phone_number = settings.TWILIO_PHONE_NUMBER

#             # Send SMS using Twilio
#             client = Client(account_sid, auth_token)
#             client.messages.create(
#                 body=message_text,
#                 from_=twilio_phone_number,
#                 to=phone_number
#             )
           
#             messages.success(request, f"Credentials sent to {merchant.first_name} at {phone_number}")

#         except Merchant.DoesNotExist:
#             messages.error(request, "Merchant not found.")
#         except Exception as e:
#             messages.error(request, f"Error sending SMS: {str(e)}")
#             print("Sending SMS to:", phone_number)
#             print("merchnat id:", merchant_id)

#         return redirect('merchant_credentials')

#     context = {
#         'merchants': merchants,
#         'corporates': corporates,
#     }
#     return render(request, 'bopo_admin/Merchant/merchant_credentials.html', context)



from django.http import JsonResponse

def merchant_credentials(request):
    merchants = Merchant.objects.all().order_by('merchant_id')
    corporates = Corporate.objects.all().order_by('project_name')

    if request.method == 'POST':
        merchant_type = request.POST.get('merchant_type')
        project_id = request.POST.get('project')
        merchant_id = request.POST.get('merchant_id')

        try:
            # ✅ 1. Corporate Admin Logic — ONLY send Corporate ID and PIN
            if merchant_type == 'corporate_admin':
                if not project_id:
                    return JsonResponse({'status': 'error', 'message': 'Project ID is required for corporate admin'})

                corporate = Corporate.objects.get(project_id=project_id)
                phone_number = corporate.mobile
                if not phone_number.startswith('+'):
                    phone_number = f'+91{phone_number}'

                message_text = (
                    f"Dear {corporate.first_name},\n\n"
                    f"Your corporate credentials for project {project_id} are as follows:\n"
                    f"Corporate ID: {corporate.corporate_id}\n"
                    f"PIN: {corporate.pin}\n\n"
                    f"Regards,\nBOPO Support Team"
                )

                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                client.messages.create(
                    body=message_text,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=phone_number
                )

                return JsonResponse({'status': 'success', 'message': 'Corporate admin credentials sent successfully!'})

            # ✅ 2. Merchant Logic — for both corporate and individual merchants
            if not merchant_id:
                return JsonResponse({'status': 'error', 'message': 'Merchant ID is required for merchant credentials'})

            merchant = Merchant.objects.get(merchant_id=merchant_id)
            phone_number = merchant.mobile
            if not phone_number.startswith('+'):
                phone_number = f'+91{phone_number}'

            terminals = Terminal.objects.filter(merchant_id=merchant)
            if not terminals.exists():
                return JsonResponse({'status': 'error', 'message': f"No Terminal IDs found for Merchant ID {merchant_id}."})

            terminal_info = "\n".join(
                f"{terminal.terminal_id} (PIN: {terminal.tid_pin})"
                for terminal in terminals
            )

            message_text = (
                f"Dear {merchant.first_name},\n\n"
                f"Your BOPO login credentials:\n"
                f"Merchant ID: {merchant.merchant_id}\n"
                f"Merchant PIN: {merchant.pin}\n"
                f"Terminals:\n{terminal_info}\n\n"
                f"Regards,\nBOPO Support Team"
            )

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message_text,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )

            return JsonResponse({'status': 'success', 'message': 'Merchant credentials sent successfully!'})

        except Corporate.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Corporate not found'})
        except Merchant.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Merchant not found'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while sending credentials'})

    return render(request, 'bopo_admin/merchant/merchant_credentials.html', {
        'merchants': merchants,
        'corporates': corporates
    })


def get_corporate_admin(request):
    project_id = request.GET.get('project_id')
    print(f"Received project_id: {project_id}") 

    try:
        corporate = Corporate.objects.get(project_id=project_id)
        admin_name = f"{corporate.first_name} {corporate.last_name}"  # ✅ corrected field names

        return JsonResponse({'status': 'success', 'admin_name': admin_name})
    except Corporate.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Corporate admin not found'})


# For fetching individual merchants
def get_individual_merchants(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        merchants = Merchant.objects.filter(user_type='individual').order_by('merchant_id')
        merchant_data = [
            {
                'merchant_id': m.merchant_id,
                'first_name': m.first_name,
                'last_name': m.last_name
            } for m in merchants
        ]
        return JsonResponse({'merchants': merchant_data})
    return JsonResponse({'error': 'Invalid request'}, status=400)





def merchant_topup(request):
    if request.method == "POST":
        merchant_id = request.POST.get("merchant_id")
        topup_points = int(request.POST.get("topup_points") or 0)
        topup_amount = request.POST.get("topup_amount")
        transaction_id = request.POST.get("transaction_id")
        payment_mode = request.POST.get("payment_mode")
        upi_id = request.POST.get("upi_id") or None
        

        try:
            merchant_obj = Merchant.objects.get(merchant_id=merchant_id)

            try:
                # Get latest payment for the merchant
                latest_payment = PaymentDetails.objects.filter(merchant=merchant_obj).latest('id')
                paid_amount = int(latest_payment.paid_amount or 0)

                if int(topup_points) != int(paid_amount):
                    return render(request, 'bopo_admin/Merchant/merchant_topup.html', {
                        "merchants": Merchant.objects.all(),
                        "error": f"Top-Up Points ({topup_points}) must match Paid Amount ({paid_amount}). Transfer blocked."
                    })


            except PaymentDetails.DoesNotExist:
                return render(request, 'bopo_admin/Merchant/merchant_topup.html', {
                    "merchants": Merchant.objects.all(),
                    "error": "No payment details found for the selected merchant."
                })

            # Create Topup entry
            Topup.objects.create(
                merchant=merchant_obj,
                topup_amount=topup_amount,
                transaction_id=transaction_id,
                topup_points=topup_points,
                payment_mode=payment_mode,
                upi_id=upi_id,
                
            )

            # Update or create MerchantPoints
            points_obj, created = MerchantPoints.objects.get_or_create(
                merchant_id=merchant_obj.id,
                defaults={'points': topup_points}
            )
            if not created:
                points_obj.points += topup_points
                points_obj.save()

            return render(request, 'bopo_admin/Merchant/merchant_topup.html', {
                "merchants": Merchant.objects.all(),
                "success": "Top-up successful!"
            })

        except Merchant.DoesNotExist:
            return render(request, 'bopo_admin/Merchant/merchant_topup.html', {
                "merchants": Merchant.objects.all(),
                "error": "Merchant not found"
            })

    return render(request, 'bopo_admin/Merchant/merchant_topup.html', {
        "merchants": Merchant.objects.all()
    })

def get_payment_details(request):
    merchant_code = request.GET.get('merchant_id')

    try:
        merchant_obj = Merchant.objects.get(merchant_id__iexact=merchant_code.strip())
        latest_payment = PaymentDetails.objects.filter(merchant=merchant_obj).latest('id')

        return JsonResponse({
            "paid_amount": latest_payment.paid_amount,
            "transaction_id": latest_payment.transaction_id,
            "payment_mode": latest_payment.payment_mode,
        })

    except Merchant.DoesNotExist:
        return JsonResponse({"error": "Merchant not found"}, status=404)
    except PaymentDetails.DoesNotExist:
        return JsonResponse({"error": "No payment found for this merchant"}, status=404)




def get_merchant_details(request):
    merchant_id = request.GET.get('merchant_id')
    try:
        merchant = Merchant.objects.get(id=merchant_id)
        points_obj = MerchantPoints.objects.get(merchant=merchant)
        return JsonResponse({
            'merchant_code': merchant.merchant_id,
            'points': points_obj.points
        })
    except Merchant.DoesNotExist:
        return JsonResponse({'error': 'Merchant not found'}, status=404)
    except MerchantPoints.DoesNotExist:
        return JsonResponse({
            'merchant_code': merchant.merchant_id,
            'points': 0
        })  


def map_bonus_points(request):
    return render(request, 'bopo_admin/Merchant/map_bonus_points.html')

def merchant_limit_list(request):
    # Fetch all topups along with the merchant related to each topup
    topups = Topup.objects.select_related('merchant').all().order_by('-created_at')

    context = {
        'topups': topups
    }
    return render(request, 'bopo_admin/Merchant/merchant_limit_list.html', context)
    # return render(request, 'bopo_admin/Merchant/merchant_limit_list.html')
    
    
def get_current_limit(request):
    merchant_id = request.GET.get('merchant_id')
    if merchant_id:
        try:
            # Assuming 'merchant_id' is a ForeignKey to the 'Merchant' model
            merchant_points = MerchantPoints.objects.get(merchant__merchant_id=merchant_id)
            return JsonResponse({'current_limit': merchant_points.points})
        except MerchantPoints.DoesNotExist:
            return JsonResponse({'current_limit': 0})  # Return 0 if no points record found
    return JsonResponse({'current_limit': 0})  # Return 0 if no merchant_id is provided
    



# from bopo_award.models import CashOut

# def reduce_limit(request):
#     cashout_requests = CashOut.objects.select_related('user', 'store').all().order_by('-id')
#     return render(request, 'reduce_limit.html', {'cashout_requests': cashout_requests})


def get_merchants_by_project(request):
    project_id = request.GET.get('project_id')
    merchants = Merchant.objects.filter(project_name__project_id=project_id).values('merchant_id', 'first_name', 'last_name')
    return JsonResponse({'merchants': list(merchants)})


def merchant_status(request):
    merchants = Merchant.objects.all().order_by('merchant_id')
    corporates = Corporate.objects.all().order_by('project_name')

    context = {
        'merchants': merchants,
        'corporates': corporates,
        
    }

    return render(request, 'bopo_admin/Merchant/merchant_status.html', context)

def get_terminal_ids(request):
    merchant_code = request.GET.get('merchant_id')  # This is like 'MER000001'
    try:
        merchant = Merchant.objects.get(merchant_id=merchant_code)
        terminal_ids = Terminal.objects.filter(merchant_id=merchant.id).values_list('terminal_id', flat=True)
        return JsonResponse({'terminal_ids': list(terminal_ids)})
    except Merchant.DoesNotExist:
        return JsonResponse({'terminal_ids': []})

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

def send_sms(to_number, message_body):
    from twilio.rest import Client
    from django.conf import settings

    print("Initializing Twilio Client...")
    print("To:", to_number)
    print("Message:", message_body)
    print("TWILIO_ACCOUNT_SID:", settings.TWILIO_ACCOUNT_SID)
    print("TWILIO_PHONE_NUMBER:", settings.TWILIO_PHONE_NUMBER)

    try:
        # Add +91 if missing and ensure only digits
        if not to_number.startswith("+"):
            if to_number.startswith("0"):
                to_number = to_number[1:]  # remove leading 0
            to_number = "+91" + to_number

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print("SMS sent. SID:", message.sid)
        return message.sid
    except Exception as e:
        print(f"❌ Twilio SMS error: {str(e)}")
        return None

# def create_notification(project_id, merchant_id, customer_id, notification_type, title, description):
#     # print("Creating notification...")

#     project = None
#     merchant = None
#     customer = None

#     if project_id:
#         try:
#             project = Corporate.objects.get(project_id=project_id)
#         except Corporate.DoesNotExist:
#             project = None  # or handle error

#     if merchant_id:
#         try:
#             merchant = Merchant.objects.get(merchant_id=merchant_id)
#         except Merchant.DoesNotExist:
#             merchant = None

#     if customer_id:
#         try:
#             customer = Customer.objects.get(customer_id=customer_id)
#         except Customer.DoesNotExist:
#             customer = None

#     notification = Notification.objects.create(
#         project_id=project,
#         merchant_id=merchant,
#         customer_id=customer,
#         notification_type=notification_type,
#         title=title,
#         description=description
#     )

#     # Send WebSocket notification code unchanged
#     # Determine the group name dynamically
#     channel_layer = get_channel_layer()
#     if merchant:
#         group_name = f"merchant_{merchant.merchant_id}"
#     elif customer:
#         group_name = f"customer_{customer.customer_id}"
#     else:
#         # Optional: fallback group if no merchant/customer
#         group_name = "general_notifications"

#     async_to_sync(channel_layer.group_send)(
#         group_name,
#         {
#             "type": "send_notification",
#             "message": {
#                 "title": title,
#                 "description": description,
#                 "type": notification_type,
#                 "timestamp": str(notification.created_at),
#             }
#         }
#     )


# ##########################################################################################


import os
from firebase_admin import credentials, initialize_app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred_path = os.path.join(BASE_DIR, 'serviceAccountKey.json')

cred = credentials.Certificate(cred_path)
initialize_app(cred)


from firebase_admin import messaging

def send_fcm_notification(token, title, body, data=None):
    """
    Sends a push notification to a device using FCM.

    Args:
        token (str): The FCM device token.
        title (str): Notification title.
        body (str): Notification message/body.
        data (dict, optional): Additional data to send as key-value pairs.
    Returns:
        messaging.SendResponse or raises exception.
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data=data or {}
    )

    response = messaging.send(message)
    return response


from django.db.models import F

def create_notification(project_id, merchant_id, customer_id, notification_type, title, description, to_all_ind_merch, to_all_customer):
    print("Creating notification...")
    print(f"Project ID: {project_id}, Merchant ID: {merchant_id}, Customer ID: {customer_id}")
    print(f"To All Individual Merchants: {to_all_ind_merch}")

    project = Corporate.objects.filter(project_id=project_id).first() if project_id else None
    merchant = Merchant.objects.filter(merchant_id=merchant_id).first() if merchant_id else None
    customer = Customer.objects.filter(customer_id=customer_id).first() if customer_id else None

    # Helper to send push notification safely
    def send_push(token, title, body, data=None):
        if token:
            try:
                send_fcm_notification(token, title, body, data)
            except messaging.UnregisteredError:
                print("Token no longer valid. Removing from DB.")
                # Remove or deactivate token in DB (Customer or Merchant)
                if Customer.objects.filter(fcm_token=token).exists():
                    Customer.objects.filter(fcm_token=token).update(fcm_token=None)
                elif Merchant.objects.filter(fcm_token=token).exists():
                    Merchant.objects.filter(fcm_token=token).update(fcm_token=None)
            except Exception as e:
                print(f"Failed to send FCM notification: {e}")

    if to_all_customer:
        customers = Customer.objects.all()

        notification = Notification.objects.create(
            project_id=project,
            notification_type=notification_type,
            title=title,
            description=description
        )
        notification.customers.set(customers)

        for c in customers:
            Customer.objects.filter(customer_id=c.customer_id).update(
                unread_notification=F('unread_notification') + 1
            )

            notification_data = {
                'title': title,
                'description': description,
                'type': notification_type,
                'timestamp': str(notification.created_at)
            }

            unread_count = c.unread_notification + 1
            group_name = f"customer_{c.customer_id}"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "unread_count": unread_count,
                    "notification": notification_data
                }
            )
            
            # Send push notification via FCM
            send_push(c.fcm_token, title, description, notification_data)

        return

    if to_all_ind_merch:
        individual_merchants = Merchant.objects.filter(user_type='individual')

        notification = Notification.objects.create(
            project_id=project,
            notification_type=notification_type,
            title=title,
            description=description
        )
        notification.merchants.set(individual_merchants)

        for m in individual_merchants:
            Merchant.objects.filter(merchant_id=m.merchant_id).update(
                unread_notification=F('unread_notification') + 1
            )

            notification_data = {
                'title': title,
                'description': description,
                'type': notification_type,
                'timestamp': str(notification.created_at)
            }

            unread_count = m.unread_notification + 1
            group_name = f"merchant_{m.merchant_id}"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "unread_count": unread_count,
                    "notification": notification_data
                }
            )

            # Send push notification via FCM
            send_push(m.fcm_token, title, description, notification_data)

        return

    if merchant:
        notification = Notification.objects.create(
            project_id=project,
            notification_type=notification_type,
            title=title,
            description=description
        )
        notification.merchants.add(merchant)
        Merchant.objects.filter(merchant_id=merchant_id).update(
            unread_notification=F('unread_notification') + 1
        )

        notification_data = {
            'title': title,
            'description': description,
            'type': notification_type,
            'timestamp': str(notification.created_at)
        }

        unread_count = merchant.unread_notification + 1
        group_name = f"merchant_{merchant_id}"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "unread_count": unread_count,
                "notification": notification_data
            }
        )
        
        # Send push notification via FCM
        send_push(merchant.fcm_token, title, description, notification_data)

    elif project:
        merchants = Merchant.objects.filter(project_name=project)
        notification = Notification.objects.create(
            project_id=project,
            notification_type=notification_type,
            title=title,
            description=description
        )
        notification.merchants.set(merchants)

        for m in merchants:
            Merchant.objects.filter(merchant_id=m.merchant_id).update(
                unread_notification=F('unread_notification') + 1
            )

            notification_data = {
                'title': title,
                'description': description,
                'type': notification_type,
                'timestamp': str(notification.created_at)
            }

            unread_count = m.unread_notification + 1
            group_name = f"merchant_{m.merchant_id}"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "unread_count": unread_count,
                    "notification": notification_data
                }
            )

            # Send push notification via FCM
            send_push(m.fcm_token, title, description, notification_data)

    elif customer:
        notification = Notification.objects.create(
            project_id=project,
            notification_type=notification_type,
            title=title,
            description=description
        )
        notification.customers.add(customer)
        Customer.objects.filter(customer_id=customer_id).update(
            unread_notification=F('unread_notification') + 1
        )

        notification_data = {
            'title': title,
            'description': description,
            'type': notification_type,
            'timestamp': str(notification.created_at)
        }

        unread_count = customer.unread_notification + 1
        group_name = f"customer_{customer_id}"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "unread_count": unread_count,
                "notification": notification_data
            }
        )

        # Send push notification via FCM
        send_push(customer.fcm_token, title, description, notification_data)

    else:
        group_name = "general_notifications"
        unread_count = 0
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "unread_count": unread_count
            }
        )

def create_notification_view(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        project_id = request.POST.get("project_id") or None
        merchant_id = request.POST.get("merchant_id") or None
        customer_id = request.POST.get("customer_id") or None
        notification_type = request.POST.get("notification_type")
        title = request.POST.get("notification_title")
        description = request.POST.get("description")
        to_all_ind_merch = request.POST.get("to_all_ind_merch") == "true"
        to_all_customer = request.POST.get("to_all_customer") == "true"
        
        print(f"Project ID: {project_id}, Merchant ID: {merchant_id}, Customer ID: {customer_id}")


        # create_notification(
        #     project_id=project_id,
        #     merchant_id=merchant_id,
        #     customer_id=customer_id,
        #     notification_type=notification_type,
        #     title=title,
        #     description=description,
        #     to_all_ind_merch=to_all_ind_merch,
        #     to_all_customer=to_all_customer
        # )

        
        if customer_id:
            messages.success(request, "Notification sent successfully to customer.")
            return redirect('send_customer_notifications')
        else:
            messages.success(request, "Notification sent successfully to Merchant.")
            return redirect('send_notifications')

    messages.error(request, "Notification sent failed.")
    return redirect('send_notifications')




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def save_fcm_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            user_type = data.get("user_type")   # 'customer' or 'merchant'
            user_id = data.get("user_id")
            fcm_token = data.get("fcm_token")

            if not user_type or not user_id or not fcm_token:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            if user_type == "customer":
                customer = Customer.objects.filter(customer_id=user_id).first()
                if customer:
                    customer.fcm_token = fcm_token
                    customer.save()
                    return JsonResponse({"success": True, "message": "FCM token saved for customer"})
                else:
                    return JsonResponse({"success": False, "message": "Customer not found"}, status=404)

            elif user_type == "merchant":
                merchant = Merchant.objects.filter(merchant_id=user_id).first()
                if merchant:
                    merchant.fcm_token = fcm_token
                    merchant.save()
                    return JsonResponse({"success": True, "message": "FCM token saved for merchant"})
                else:
                    return JsonResponse({"success": False, "message": "Merchant not found"}, status=404)

            else:
                return JsonResponse({"success": False, "message": "Invalid user type"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)




# ###############################################333

def send_notifications(request): 
    corporates = Corporate.objects.all()

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        project = request.POST.get("project")  # May be None for individuals
        notification_type = request.POST.get("notification_type")
        notification_title = request.POST.get("notification_title")
        description = request.POST.get("description")

        message = (
            f"{notification_type}\n"
            f"Title: {notification_title}\n"
            f"Description: {description}"
        )

        # ✅ Send to a single merchant (corporate)
        if form_type == "single":
            merchant_id = request.POST.get("merchant")
            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id)

                Notification.objects.create(
                    project_id=project,
                    merchant_id=merchant_id,
                    notification_type=notification_type,
                    title=notification_title,
                    description=description
                )

                send_sms(merchant.mobile, message)

                return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                    'corporates': corporates,
                    'message': 'Notification sent to selected merchant.'
                })

            except Merchant.DoesNotExist:
                return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                    'corporates': corporates,
                    'message': 'Merchant not found.'
                })

        # ✅ Send to a single individual merchant
        elif form_type == "single_individual":
            merchant_id = request.POST.get("merchant")
            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id, user_type='individual')

                Notification.objects.create(
                    merchant_id=merchant_id,
                    notification_type=notification_type,
                    title=notification_title,
                    description=description
                )

                send_sms(merchant.mobile, message)

                return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                    'corporates': corporates,
                    'message': 'Notification sent to individual merchant.'
                })

            except Merchant.DoesNotExist:
                return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                    'corporates': corporates,
                    'message': 'Individual Merchant not found.'
                })

        # ✅ Send to all corporate merchants under a project
        elif form_type == "all":
            merchants = Merchant.objects.filter(project_name__project_id=project)

            if not merchants.exists():
                return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                    'corporates': corporates,
                    'message': 'No merchants found for selected project.'
                })

            failed_merchants = []

            for merchant in merchants:
                Notification.objects.create(
                    project_id=project,
                    merchant_id=merchant.merchant_id,
                    notification_type=notification_type,
                    title=notification_title,
                    description=description
                )

                try:
                    send_sms(merchant.mobile, message)
                except Exception as e:
                    failed_merchants.append((merchant.merchant_id, str(e)))

            msg = f"Notifications sent to {merchants.count()} merchants."
            if failed_merchants:
                msg += f" But failed for: {', '.join([m[0] for m in failed_merchants])}"

            return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                'corporates': corporates,
                'message': msg
            })

        # ✅ Send to all individual merchants
        elif form_type == "all_individual":
            merchants = Merchant.objects.filter(user_type='individual')

            if not merchants.exists():
                return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                    'corporates': corporates,
                    'message': 'No individual merchants found.'
                })

            failed_merchants = []

            for merchant in merchants:
                Notification.objects.create(
                    merchant_id=merchant.merchant_id,
                    notification_type=notification_type,
                    title=notification_title,
                    description=description
                )

                try:
                    send_sms(merchant.mobile, message)
                except Exception as e:
                    failed_merchants.append((merchant.merchant_id, str(e)))

            msg = f"Notifications sent to {merchants.count()} individual merchants."
            if failed_merchants:
                msg += f" But failed for: {', '.join([m[0] for m in failed_merchants])}"

            return render(request, 'bopo_admin/Merchant/send_notifications.html', {
                'corporates': corporates,
                'message': msg
            })

    return render(request, 'bopo_admin/Merchant/send_notifications.html', {
        'corporates': corporates
    })


def received_offers(request):
    return render(request, 'bopo_admin/Merchant/received_offers.html')






def uploads(request):
    if request.method == "POST":
        file_type = request.POST.get("file_type")
        uploaded_file = request.FILES.get(file_type)

        if file_type and uploaded_file:
            # Update if file_type exists, else create
            UploadedFile.objects.update_or_create(
                file_type=file_type,
                defaults={'file': uploaded_file}
            )
            messages.success(request, f"{file_type.replace('_', ' ').title()} uploaded successfully!")

    # Fetch existing files
    context = {
        "privacy_policy_file": UploadedFile.objects.filter(file_type="privacy_policy").first(),
        "terms_conditions_file": UploadedFile.objects.filter(file_type="terms_conditions").first(),
        "user_guide_file": UploadedFile.objects.filter(file_type="user_guide").first(),
    }

    return render(request, 'bopo_admin/Merchant/uploads.html', context)


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
        pin = request.POST.get('pin') 
        pan_number = request.POST.get('pan_number')
        address = request.POST.get('address')
        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        pincode = request.POST.get('pincode')
        country = request.POST.get("country", "India")

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

        if Customer.objects.filter(pan_number=pan_number).exists():
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
            pin=pin,
            pan_number=pan_number,
            address=address,
            state=state,
            city=city,
            pincode=pincode,
            country=country
        )

        return JsonResponse({"success": True, "message": "Customer added successfully!"})
    
    return render(request, 'bopo_admin/Customer/add_customer.html')


from accounts.models import Customer 
def send_notification_customer(request):
    if request.method == "POST":
        # Checkbox handling
        send_to_all = request.POST.get("send_to_all") == "on"
        customer_id = request.POST.get("customer_id")
        notification_type = request.POST.get("notification_type")
        notification_title = request.POST.get("notification_title")
        notification_description = request.POST.get("notification_description")

        message = (
            f"{notification_type}\n"
            f"Title: {notification_title}\n"
            f"Description: {notification_description}"
        )

        Notification.objects.create(
            notification_type=notification_type,
            title=notification_title,
            description=notification_description
        )

        if send_to_all:
            customers = Customer.objects.all()
            for customer in customers:
                send_sms(customer.mobile, message)
                print(f"[INFO] Notification sent to Customer ID: {customer.customer_id}, Mobile: {customer.mobile}")
            return render(request, 'bopo_admin/Customer/send_customer_notifications.html', {
                'customers': Customer.objects.all(),
                'message': 'Notification sent successfully to all customers!'
            })

        elif customer_id:
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                send_sms(customer.mobile, message)
                print(f"[INFO] Notification sent to single Customer ID: {customer.customer_id}, Mobile: {customer.mobile}")
                return render(request, 'bopo_admin/Customer/send_customer_notifications.html', {
                    'customers': Customer.objects.all(),
                    'message': 'Notification sent successfully to the selected customer!'
                })
            except Customer.DoesNotExist:
                print(f"[ERROR] Customer with ID {customer_id} not found.")
                return render(request, 'bopo_admin/Customer/send_customer_notifications.html', {
                    'customers': Customer.objects.all(),
                    'message': 'Customer not found.'
                })

    return render(request, 'bopo_admin/Customer/send_customer_notifications.html', {
        'customers': Customer.objects.all()
    })


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'bopo_admin/Employee/employee_list.html', {'employees': employees})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Employee, State, City

def get_employee(request, employee_id):
    # Corrected to use 'employee_id' instead of 'id'
    employee = get_object_or_404(Employee, employee_id=employee_id)

    # Retrieve the state object by its name
    state_obj = get_object_or_404(State, name=employee.state)  # Assuming state is a string, get State object by name

    # Retrieve cities based on the selected state
    cities = City.objects.filter(state=state_obj)  # Now we use the State object

    # Convert cities to a dictionary for use in the frontend
    city_data = [{"id": city.id, "name": city.name} for city in cities]

    # Data to send to the frontend
    data = {
        "id": employee.employee_id,  # Assuming employee_id is the identifier
        "name": employee.name,
        "email": employee.email,
        "mobile": employee.mobile,
        "address": employee.address,
        "aadhaar": employee.aadhaar,
        "pan": employee.pan,
        "pincode": employee.pincode,
        "state": employee.state,  # Assuming state is a string or related field
        "city": employee.city,
        "username": employee.username,
        "password": employee.password,
        "states": [{"id": state.id, "name": state.name} for state in State.objects.all()],  # List of all states
        "cities": city_data,  # List of cities filtered by state
    }

    return JsonResponse(data)


from django.http import JsonResponse
from .models import Employee


# def update_employee(request): 
#     if request.method == "POST":
#         employee_id = request.POST.get('employee_id')  # Keep 'employee_id'
#         name = request.POST.get('employee_name')
#         email = request.POST.get('email')
#         aadhaar = request.POST.get("aadhaar")
#         address = request.POST.get("address")
#         state_name = request.POST.get('state')
#         city_name = request.POST.get('city')
#         mobile = request.POST.get("mobile")
#         pan = request.POST.get("pan")
#         pincode = request.POST.get("pincode")
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         country = request.POST.get("country", "India")

#         try:
#             # Use employee_id instead of id
#             employee = Employee.objects.get(employee_id=employee_id)  # Fixed here
            
#             if not State.objects.filter(name=state_name).exists():
#                 return JsonResponse({'success': False, 'error': 'State not found'})

#             if not City.objects.filter(name=city_name).exists():
#                 return JsonResponse({'success': False, 'error': 'City not found'})

#             employee.name = name
#             employee.email = email
#             employee.aadhaar = aadhaar
#             employee.address = address
#             employee.state = state_name
#             employee.city = city_name
#             employee.mobile = mobile
#             employee.pan = pan
#             employee.pincode = pincode
#             employee.username = username
#             employee.password = password
#             employee.country = country

#             employee.save()

#             return JsonResponse({'status': 'success', 'message': 'Employee updated successfully'})
#         except Employee.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Employee not found'})
#         except (State.DoesNotExist, City.DoesNotExist):
#             return JsonResponse({'status': 'error', 'message': 'Invalid state or city'})
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@csrf_exempt  # Not needed if you pass CSRF token
def update_employee(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')  # Optional: encrypt if needed

        try:
            employee = Employee.objects.get(employee_id=employee_id)
            employee.email = email
            employee.mobile = mobile
            if password:
                employee.password = password  # Hash if necessary
            employee.save()
            return JsonResponse({'status': 'success'})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


from django.http import JsonResponse
from .models import Employee

def delete_employee(request, employee_id):
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        employee.delete()
        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)


from django.http import JsonResponse
from django.shortcuts import render
from .models import Employee, State, City

from django.db.models import Max
from django.db import IntegrityError
import re

def add_employee(request):
    if request.method == "POST":
        # Generate employee ID by finding the max employee_id and ensuring uniqueness
        last_employee = Employee.objects.filter(employee_id__startswith="EMP").aggregate(max_id=Max('employee_id'))['max_id']
        
        if last_employee:
            try:
                # Extract the numeric part from the last employee_id (e.g., 'EMP00000001' -> 1)
                last_number = int(re.sub(r'\D', '', last_employee))  # Removing non-numeric characters
            except ValueError:
                last_number = 10000000  # Default to a base number if the format is incorrect
        else:
            last_number = 10000000

        next_number = last_number + 1
        employee_id = f"EMP{next_number:06d}"  # Format employee_id with 8 digits, e.g., 'EMP00000001'

        # Check for uniqueness of the generated employee_id
        while Employee.objects.filter(employee_id=employee_id).exists():
            next_number += 1
            employee_id = f"EMP{next_number:06d}"  # Regenerate employee_id if the current one exists

        # Fetch POST data for employee
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

        # Validation checks
        if Employee.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email ID already exists!"})
        if Employee.objects.filter(mobile=mobile).exists():
            return JsonResponse({"success": False, "message": "Mobile number already exists!"})
        if Employee.objects.filter(aadhaar=aadhaar).exists():
            return JsonResponse({"success": False, "message": "Aadhaar number already exists!"})
        if Employee.objects.filter(pan=pan).exists():
            return JsonResponse({"success": False, "message": "PAN number already exists!"})

        # Fetch state and city objects
        try:
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)
        except (State.DoesNotExist, City.DoesNotExist):
            return JsonResponse({"success": False, "message": "Invalid state or city selection."})

        # Create employee record
        try:
            employee = Employee(
                employee_id=employee_id,
                name=name,
                email=email,
                aadhaar=aadhaar,
                address=address,
                state=state.name,
                city=city.name,
                mobile=mobile,
                pan=pan,
                pincode=pincode,
                username=username,
                password=password,
                country=country
            )
            employee.save()
        except IntegrityError as e:
            employee.delete()
            # Handle any integrity errors (shouldn't happen, but just in case)
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

        bopo_admin = BopoAdmin(username=username, role="employee", employee=employee)
        bopo_admin.set_password(password)  # Hash the password
        bopo_admin.save()
        return JsonResponse({"success": True, "message": "Employee added successfully!"})

    return render(request, 'bopo_admin/Employee/add_employee.html')


from django.contrib import messages

def assign_employee_role(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, "Employee not found.")
            return redirect('assign_employee_role')

        roles_data = {
            'corporate_merchant': 'Corporate Merchant' in request.POST.getlist('roles'),
            'individual_merchant': 'Individual Merchant' in request.POST.getlist('roles'),
            'terminals': 'terminals' in request.POST.getlist('roles'),
            'merchant_send_credentials': 'Merchant Send Credentials' in request.POST.getlist('roles'),
            'reduce_limit': 'reduce_limit' in request.POST.getlist('roles'),
            'merchant_limit': 'Merchant Limit' in request.POST.getlist('roles'),
            'merchant_login_page_info': 'Merchant Login Page-Info' in request.POST.getlist('roles'),
            'merchant_send_notification': 'Merchant Send Notification' in request.POST.getlist('roles'),
            'merchant_received_offers': 'Merchant Received Offers' in request.POST.getlist('roles'),
            'modify_customer_details': 'Modify Customer Details' in request.POST.getlist('roles'),
            'customer_send_notification': 'Customer Send Notification' in request.POST.getlist('roles'),
            'create_employee': 'Create Employee' in request.POST.getlist('roles'),
            'payment_details': 'Payment Details' in request.POST.getlist('roles'),
            'account_info': 'Account-Info' in request.POST.getlist('roles'),
            'reports': 'Reports' in request.POST.getlist('roles'),
            'deduct_amount': 'Deduct Amount' in request.POST.getlist('roles'),
            'superadmin_functionality': 'superadmin_functionality' in request.POST.getlist('roles'),

            'helpdesk_action': 'HelpDesk Action' in request.POST.getlist('roles'),
        }


        EmployeeRole.objects.update_or_create(
            employee=employee,
            defaults=roles_data
        )

        messages.success(request, "Roles successfully assigned.")

        # Instead of redirecting now, show the form again with the success message
        employees = Employee.objects.all()
        return render(request, 'bopo_admin/Employee/employee_role.html', {
            'employees': employees,
            'redirect_to_list': True  # Flag for JS redirect
        })

    else:
        employees = Employee.objects.all()
        return render(request, 'bopo_admin/Employee/employee_role.html', {'employees': employees})
    
    
    
    

def get_employee_roles(request):
    employee_id = request.GET.get('employee_id')
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        emp_roles = EmployeeRole.objects.get(employee=employee)

        roles = {
            'corporate_merchant': emp_roles.corporate_merchant,
            'individual_merchant': emp_roles.individual_merchant,
            'terminals': emp_roles.terminals,
            'merchant_send_credentials': emp_roles.merchant_send_credentials,
            'reduce_limit': emp_roles.reduce_limit,
            'merchant_limit': emp_roles.merchant_limit,
            'merchant_login_page_info': emp_roles.merchant_login_page_info,
            'merchant_send_notification': emp_roles.merchant_send_notification,
            'merchant_received_offers': emp_roles.merchant_received_offers,
            'modify_customer_details': emp_roles.modify_customer_details,
            'customer_send_notification': emp_roles.customer_send_notification,
            'create_employee': emp_roles.create_employee,
            'payment_details': emp_roles.payment_details,
            'account_info': emp_roles.account_info,
            'reports': emp_roles.reports,
            'deduct_amount': emp_roles.deduct_amount,
            'superadmin_functionality': emp_roles.superadmin_functionality,
            'helpdesk_action': emp_roles.helpdesk_action,
        }

        return JsonResponse({'roles': roles})
    except (Employee.DoesNotExist, EmployeeRole.DoesNotExist):
        return JsonResponse({'roles': {}}, status=404)

# def payment_details(request):
#     topups = PaymentDetails.objects.all().order_by('-created_at')  # or any custom ordering

#     if request.method == "POST":
#         # Handle any POST data if needed
#         pass

#     return render(request, 'bopo_admin/Payment/payment_details.html', {
#         'topups': topups
#     })




def payment_details(request):
    if request.method == "POST":
        payment_id = request.POST.get("payment_id")
        action = request.POST.get("action")

        if not payment_id or not action:
            return JsonResponse({"success": False, "message": "Missing payment ID or action."})

        payment = get_object_or_404(PaymentDetails, id=payment_id)

        if action == "approve":

            # Check if merchant has any other approved plan of DIFFERENT plan_type
            existing_payment = PaymentDetails.objects.filter(
                merchant=payment.merchant,
                status="approved"
            ).exclude(id=payment.id).first()

            if existing_payment and existing_payment.plan_type != payment.plan_type:
                return JsonResponse({
                    "success": False,
                    "message": f"Merchant already has an approved {existing_payment.plan_type} plan."
                })

            if payment.plan_type == "rental":
                validity = request.POST.get("validity")
                if not validity or not validity.isdigit() or int(validity) <= 0:
                    return JsonResponse({"success": False, "message": "Invalid rental validity provided."})

                payment.validity_days = int(validity)  # Assuming this field exists
                payment.status = "approved"
                payment.save()

                return JsonResponse({"success": True, "message": f"Rental plan approved for {validity} days."})

            # For prepaid or other plan types
            topup_value = payment.topup_amount
            if topup_value is None:
                return JsonResponse({"success": False, "message": "Top-up amount is invalid."})

            merchant = payment.merchant
            points_obj, created = MerchantPoints.objects.get_or_create(merchant=merchant, defaults={'points': 0})
            points_obj.points += float(topup_value)
            points_obj.save()

            payment.status = "approved"
            payment.save()

            return JsonResponse({"success": True, "message": "Payment approved successfully"})

        elif action == "reject":
            payment.status = "rejected"
            payment.save()
            return JsonResponse({"success": True, "message": "Payment has been rejected."})

        return JsonResponse({"success": False, "message": "Invalid action."})

    topups = PaymentDetails.objects.all().order_by('-created_at')
    return render(request, 'bopo_admin/Payment/payment_details.html', {'topups': topups})


# def account_info(request):
#     account = AccountInfo.objects.first()  # Get the first account (modify as per your logic)
    
#     if request.method == "POST":
#         accountNumber = request.POST.get("accountNumber")
#         payableTo = request.POST.get("payableTo")
#         bankName = request.POST.get("bankName")
#         city = request.POST.get("city")
#         accountType = request.POST.get("accountType")
#         ifscCode = request.POST.get("ifscCode")
#         branchName = request.POST.get("branchName")
#         pincode = request.POST.get("pincode")

#         if account:
#             # Update existing record
#             account.accountNumber = accountNumber
#             account.payableTo = payableTo
#             account.bankName = bankName
#             account.city = city
#             accountType = accountType
#             account.ifscCode = ifscCode
#             account.branchName = branchName
#             account.pincode = pincode
#             account.save()
#         else:
#             # Create new record if none exists
#             AccountInfo.objects.create(
#                 accountNumber=accountNumber,
#                 payableTo=payableTo,
#                 bankName=bankName,
#                 city=city,
#                 accountType=accountType,
#                 ifscCode=ifscCode,
#                 branchName=branchName,
#                 pincode=pincode
#             )

#         return JsonResponse({"message": "Account saved successfully!"})

#     return render(request, "bopo_admin/Payment/account_info.html", {"account": account})




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

        # Check required fields
        if not all([accountNumber, payableTo, bankName, city, accountType, ifscCode, branchName, pincode]):
            return JsonResponse({"status": "error", "message": "All fields are required."})

        try:
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

            return JsonResponse({"status": "success", "message": "Account saved successfully!"})
        except Exception as e:
          
            return JsonResponse({
                "status": "error",
                "message": "Failed to save account information. Please try again later."
            })

    # For GET request, render the template
    return render(request, "bopo_admin/Payment/account_info.html", {"account": account})


def reports(request):
    return render(request, 'bopo_admin/Payment/reports.html')


# def login_view(request):
#     # GET request (initial load or after auto logout)
#     if request.GET.get('inactive'):
#         error_message = "Your corporate account has been deactivated. Please contact the superadmin."
#         return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user_type = request.POST.get('user_type')
#         remember_me = request.POST.get('remember_me')  # Fetch the "remember me" checkbox

#         # Authenticate user
#         user = authenticate(request, username=username, password=password)

#         if user:
#             # Check corporate admin status
#             if user_type == "corporate_admin":
#                 try:
#                     corporate = Corporate.objects.get(corporate_id=username)
#                     if corporate.status == "Inactive":
#                         logout(request)
#                         request.session.flush()
#                         error_message = "Your corporate account is currently not active. Please reach out to the superadmin for assistance."
#                         return render(request, 'bopo_admin/login.html', {'error_message': error_message})
#                 except Corporate.DoesNotExist:
#                     error_message = "Corporate account not found."
#                     return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#             # Check employee permissions
#             elif user_type == "employee":
#                 role_permissions = EmployeeRole.objects.filter(employee=user.employee)
#                 if not role_permissions.exists():
#                     error_message = "You do not have permission to access this page."
#                     return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#             # Login the user
#             login(request, user)

#             # Set session expiry based on "remember me"
#             if remember_me:
#                request.session.set_expiry(2592000)  # 1 month

#             else:
#                 request.session.set_expiry(0)  # Session expires on browser close

#             request.session['user_type'] = user_type
#             return redirect('home')

#         else:
#             error_message = "Invalid credentials"
#             return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#     return render(request, 'bopo_admin/login.html')




from django.contrib.auth.models import User  # Replace with your custom User model if used

def login_view(request):
    if request.GET.get('inactive'):
        error_message = "Your corporate account has been deactivated. Please contact the superadmin."
        return render(request, 'bopo_admin/login.html', {'error_message': error_message})

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        if user:
            # ✅ Validate user type after successful authentication
            if user_type == "super_admin":
                if not user.is_superuser:
                    error_message = "You are not authorized as a Super Admin."
                    return render(request, 'bopo_admin/login.html', {'error_message': error_message})

            elif user_type == "corporate_admin":
                try:
                    corporate = Corporate.objects.get(corporate_id=username)
                    if corporate.status == "Inactive":
                        logout(request)
                        request.session.flush()
                        error_message = "Your corporate account is currently not active. Please contact to the superadmin."
                        return render(request, 'bopo_admin/login.html', {'error_message': error_message})
                except Corporate.DoesNotExist:
                    error_message = "Corporate account not found."
                    return render(request, 'bopo_admin/login.html', {'error_message': error_message})

            elif user_type == "employee":
                if not hasattr(user, 'employee'):
                    error_message = "This account is not registered as an employee."
                    return render(request, 'bopo_admin/login.html', {'error_message': error_message})
                role_permissions = EmployeeRole.objects.filter(employee=user.employee)
                if not role_permissions.exists():
                    error_message = "You do not have permission to access this page."
                    return render(request, 'bopo_admin/login.html', {'error_message': error_message})

            else:
                error_message = "Invalid user type."
                return render(request, 'bopo_admin/login.html', {'error_message': error_message})

            # ✅ Passed all checks, login
            login(request, user)
            request.session.set_expiry(2592000 if remember_me else 0)
            request.session['user_type'] = user_type
            return redirect('home')

        else:
            error_message = "Invalid credentials"
            return render(request, 'bopo_admin/login.html', {'error_message': error_message})

    return render(request, 'bopo_admin/login.html')


# def login_view(request):
#     # Debug: Print request method and query params
#     print("Request method:", request.method)
#     print("Query params:", request.GET)

#     # GET request (initial load or after auto logout)
#     if request.GET.get('inactive'):
#         error_message = "Your corporate account has been deactivated. Please contact the superadmin."
#         print("Corporate account inactive")
#         return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#     if request.method == 'POST':
#         # Get form values
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user_type = request.POST.get('user_type')
#         remember_me = request.POST.get('remember_me')

#         # Debug: Print form inputs
#         print("Username:", username)
#         print("User Type:", user_type)
#         print("Remember Me Checked:", remember_me)

#         # Authenticate user
#         user = authenticate(request, username=username, password=password)
#         print("Authenticated user:", user)

#         if user:
#             if user_type == "corporate_admin":
#                 try:
#                     corporate = Corporate.objects.get(corporate_id=username)
#                     print("Corporate found:", corporate)
#                     if corporate.status == "Inactive":
#                         logout(request)
#                         request.session.flush()
#                         error_message = "Your corporate account is currently not active. Please reach out to the superadmin for assistance."
#                         print("Corporate inactive, logging out.")
#                         return render(request, 'bopo_admin/login.html', {'error_message': error_message})
#                 except Corporate.DoesNotExist:
#                     error_message = "Corporate account not found."
#                     print("Corporate does not exist.")
#                     return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#             elif user_type == "employee":
#                 try:
#                     role_permissions = EmployeeRole.objects.filter(employee=user.employee)
#                     print("Employee role permissions found:", role_permissions)
#                     if not role_permissions.exists():
#                         error_message = "You do not have permission to access this page."
#                         print("No role permissions, access denied.")
#                         return render(request, 'bopo_admin/login.html', {'error_message': error_message})
#                 except Exception as e:
#                     error_message = "Error checking employee roles."
#                     print("Error checking employee roles:", str(e))
#                     return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#             # Login user
#             login(request, user)
#             print("User logged in:", user)

#             # Session expiry setup
#             if remember_me:
#                 request.session.set_expiry(2)  # 2 seconds for debug
#                 print("Session expiry set to 2 seconds for testing.")
#             else:
#                 request.session.set_expiry(0)
#                 print("Session will expire on browser close.")

#             request.session['user_type'] = user_type
#             print("Session user_type set to:", user_type)

#             return redirect('home')

#         else:
#             error_message = "Invalid credentials"
#             print("Authentication failed.")
#             return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#     print("Initial login page load (GET request).")
#     return render(request, 'bopo_admin/login.html')


from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import BadHeaderError


# def forgot_password(request):
    # print("Password reset view called") 
    # if request.method == "POST":
    #     email = request.POST.get('email')
    #     form = PasswordResetForm({'email': email})
    #     if form.is_valid():
    #         try:
    #             form.save(
    #                 request=request,
    #                 use_https=request.is_secure(),
    #                 email_template_name='bopo_admin/ForgotPass/password_reset_email.html',
    #                 subject_template_name='bopo_admin/ForgotPass/password_reset_subject.txt',
    #                 from_email='BOPO Team <006iipt@gmail.com>',
    #             )
    #             messages.success(request, "A password reset link has been sent to your email address.")
    #             return redirect('forgot_password')
    #         except BadHeaderError:
    #             return HttpResponse('Invalid header found.')
    #     else:
    #         messages.error(request, "No user is associated with this email address.")
    # else:
    #     form = PasswordResetForm()

    # return render(request, 'bopo_admin/ForgotPass/forgot_password.html', {'form': form})
    
from django.contrib.sites.shortcuts import get_current_site

def forgot_password(request):
    print("Password reset view called") 
    if request.method == "POST":
        email = request.POST.get('email')
        print(f"Email received: {email}")
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            print("Form is valid. Sending reset email...")
            try:
                current_site = get_current_site(request)   
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='bopo_admin/ForgotPass/password_reset_email.html',
                    subject_template_name='bopo_admin/ForgotPass/password_reset_subject.txt',
                    from_email='BOPO Team <006iipt@gmail.com>',
                    html_email_template_name=None,
                    extra_email_context={
                        'domain': current_site.domain,
                        'protocol': 'https' if request.is_secure() else 'http'
                    }
                )

                messages.success(request, "A password reset link has been sent to your email address.")
                return redirect('password_reset_done')  # ✅ Changed here
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        else:
            print("Form is invalid.")
            messages.error(request, "No user is associated with this email address.")
    else:
        form = PasswordResetForm()

    return render(request, 'bopo_admin/ForgotPass/forgot_password.html', {'form': form})

from django.contrib.auth.views import PasswordResetView
from django.conf import settings

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        domain_override = getattr(settings, 'DEFAULT_DOMAIN', '127.0.0.1:8000')
        form.save(
            use_https=self.request.is_secure(),
            from_email=self.from_email,
            email_template_name=self.email_template_name,
            subject_template_name=self.subject_template_name,
            request=self.request,
            domain_override=domain_override
        )
        return super().form_valid(form)


from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.models import AnonymousUser



# def profile(request):
#     if isinstance(request.user, AnonymousUser):
#         # If the user is not logged in (AnonymousUser), render a profile page without the edit form
#         return render(request, 'bopo_admin/profile.html', {'error_message': 'You must be logged in to edit your profile.'})

#     # If the user is logged in (authenticated)
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         user_type = request.POST.get('user_type')  # Getting user type from the form
#         password = request.POST.get('password')
#         email= request.POST.get('email')
#         mobile= request.POST.get('mobile')

#         user = request.user  # Assuming you are using the default user model
        
#         # Update the user's username and user type
#         user.username = username
#         user.user_type = user_type  # Updating user type
#         user.email = email
#         user.mobile = mobile
        
#         # If the password is provided, update it (hashed before saving)
#         if password:
#             user.password = make_password(password)

#         user.save()  # Save the updated user information

#         # Add a success message
#         success_message = "Profile updated successfully!"

#         # Redirect to profile page to see the changes
#         return render(request, 'bopo_admin/profile.html', {'success_message': success_message, 'user': user})

#     # If GET request, just render the profile page
#     return render(request, 'bopo_admin/profile.html', {'user': request.user})



@login_required
def profile(request):
    user = request.user

    context = {
        'user': user
    }

    if user.role == 'corporate_admin' and user.corporate:
        context['profile'] = user.corporate
        context['role'] = 'corporate_admin'

    elif user.role == 'employee' and user.employee:
        context['profile'] = user.employee
        context['role'] = 'employee'

    elif user.role == 'super_admin':
        context['role'] = 'super_admin'
        # No additional profile needed for super admin

    return render(request, 'bopo_admin/profile.html', context)


@login_required
def update_profile(request):
    user = request.user

    if request.method == 'POST':
        if user.role == 'corporate_admin' and user.corporate:
            profile = user.corporate
            profile.project_name = request.POST.get('project_name')
            profile.email = request.POST.get('email')
            profile.mobile = request.POST.get('mobile')
            profile.city = request.POST.get('city')
            profile.save()
            messages.success(request, "Corporate profile updated successfully!")

        elif user.role == 'employee' and user.employee:
            profile = user.employee
            profile.name = request.POST.get('name')
            profile.email = request.POST.get('email')
            profile.mobile = request.POST.get('mobile')
            profile.city = request.POST.get('city')
            profile.save()
            messages.success(request, "Employee profile updated successfully!")

        elif user.role == 'super_admin':
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.mobile = request.POST.get('mobile')
            user.city = request.POST.get('city')
            user.save()
            messages.success(request, "Super admin profile updated successfully!")

        return redirect('profile')

    return redirect('profile')

# from datetime import timedelta
# from django.utils import timezone

# def login(request):
#     if request.method == 'POST': 
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user_type = request.POST.get('user_type')
#         remember_me = request.POST.get('remember_me')  # Capture remember_me checkbox

#         try:
#             user = BopoAdmin.objects.get(username=username)

#             if check_password(password, user.password):
#                 request.session['admin_id'] = user.id
#                 request.session['user_type'] = user_type

#                 if remember_me:
#                     # Set session to expire in 7 days
#                     request.session.set_expiry(7 * 24 * 60 * 60)  # 7 days in seconds
#                 else:
#                     # Session expires when browser is closed
#                     request.session.set_expiry(0)

#                 return redirect('home')
#             else:
#                 error_message = "Incorrect password"
#         except BopoAdmin.DoesNotExist:
#             error_message = "User does not exist"

#         return render(request, 'bopo_admin/login.html', {'error_message': error_message})

#     return render(request, 'bopo_admin/login.html')
def export_projects(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Corporate Projects"

    # Add "Sr No." as the first column
    headers = [
        "Sr No.", "Corporate ID", "Project Name", "First Name", "Last Name",
        "Email", "Mobile", "Aadhaar Number", "GST Number", "PAN", "Shop Name",
        "Address", "City", "State", "Country", "Pincode", "Created At"
    ]

    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    corporates = Corporate.objects.all()

    for row_num, corporate in enumerate(corporates, 2):
        # Sr No.
        sheet.cell(row=row_num, column=1, value=row_num - 1)
        
        # Data columns shifted by 1
        sheet.cell(row=row_num, column=2, value=corporate.corporate_id or "")
        sheet.cell(row=row_num, column=3, value=corporate.project_name or "")
        sheet.cell(row=row_num, column=4, value=corporate.first_name or "")
        sheet.cell(row=row_num, column=5, value=corporate.last_name or "")
        sheet.cell(row=row_num, column=6, value=corporate.email or "")
        sheet.cell(row=row_num, column=7, value=corporate.mobile or "")
        sheet.cell(row=row_num, column=8, value=corporate.aadhaar_number or "")
        sheet.cell(row=row_num, column=9, value=corporate.gst_number or "")
        sheet.cell(row=row_num, column=10, value=corporate.pan_number or "")
        sheet.cell(row=row_num, column=11, value=corporate.shop_name or "")
        sheet.cell(row=row_num, column=12, value=corporate.address or "")
        sheet.cell(row=row_num, column=13, value=corporate.city or "")
        sheet.cell(row=row_num, column=14, value=corporate.state or "")
        sheet.cell(row=row_num, column=15, value=corporate.country or "")
        sheet.cell(row=row_num, column=16, value=corporate.pincode or "")
        sheet.cell(row=row_num, column=17, value=corporate.created_at.strftime("%Y-%m-%d %H:%M:%S") if corporate.created_at else "")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

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

    # Add headers to the sheet, including "Sr No."
    headers = [
        "Sr No.", "Merchant ID", "User Type", "Project Name", "First Name", "Last Name",
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
        sheet.cell(row=row_num, column=1, value=row_num - 1)  # Sr No.
        sheet.cell(row=row_num, column=2, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=3, value=merchant.user_type or "")
        sheet.cell(row=row_num, column=4, value=str(merchant.project_name) if merchant.project_name else "")
        sheet.cell(row=row_num, column=5, value=merchant.first_name or "")
        sheet.cell(row=row_num, column=6, value=merchant.last_name or "")
        sheet.cell(row=row_num, column=7, value=merchant.email or "")
        sheet.cell(row=row_num, column=8, value=merchant.mobile or "")
        sheet.cell(row=row_num, column=9, value=merchant.aadhaar_number or "")
        sheet.cell(row=row_num, column=10, value=merchant.gst_number or "")
        sheet.cell(row=row_num, column=11, value=merchant.pan_number or "")
        sheet.cell(row=row_num, column=12, value=merchant.shop_name or "")
        sheet.cell(row=row_num, column=13, value=merchant.address or "")
        sheet.cell(row=row_num, column=14, value=merchant.city or "")
        sheet.cell(row=row_num, column=15, value=merchant.state or "")
        sheet.cell(row=row_num, column=16, value=merchant.country or "")
        sheet.cell(row=row_num, column=17, value=merchant.pincode or "")
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
    response["Content-Disposition"] = 'attachment; filename="Merchants_Projects.xlsx"'

    return response

def export_disabled_merchants(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Disabled Merchants"

    # Add headers to the sheet, including "Sr No."
    headers = [
        "Sr No.", "Merchant ID", "User Type", "Project Name", "First Name", "Last Name",
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
        sheet.cell(row=row_num, column=1, value=row_num - 1)  # Sr No.
        sheet.cell(row=row_num, column=2, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=3, value=merchant.user_type or "")
        sheet.cell(row=row_num, column=4, value=str(merchant.project_name) if merchant.project_name else "")
        sheet.cell(row=row_num, column=5, value=merchant.first_name or "")
        sheet.cell(row=row_num, column=6, value=merchant.last_name or "")
        sheet.cell(row=row_num, column=7, value=merchant.email or "")
        sheet.cell(row=row_num, column=8, value=merchant.mobile or "")
        sheet.cell(row=row_num, column=9, value=merchant.aadhaar_number or "")
        sheet.cell(row=row_num, column=10, value=merchant.gst_number or "")
        sheet.cell(row=row_num, column=11, value=merchant.pan_number or "")
        sheet.cell(row=row_num, column=12, value=merchant.shop_name or "")
        sheet.cell(row=row_num, column=13, value=merchant.address or "")
        sheet.cell(row=row_num, column=14, value=merchant.city or "")
        sheet.cell(row=row_num, column=15, value=merchant.state or "")
        sheet.cell(row=row_num, column=16, value=merchant.country or "")
        sheet.cell(row=row_num, column=17, value=merchant.pincode or "")
        sheet.cell(row=row_num, column=18, value=merchant.status or "")
        sheet.cell(row=row_num, column=19, value=merchant.created_at.strftime("%Y-%m-%d %H:%M:%S") if merchant.created_at else "")

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

from django.db.models import Sum

def export_project_wise_balance(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Projects-Wise Balance"

    # Add headers (now including Sr No.)
    headers = [
        "Sr No.", "Corporate ID", "Project Name", "First Name", "Last Name",
        "Email", "Mobile", "Aadhaar Number", "GST Number", "PAN", "Shop Name",
        "Address", "City", "State", "Country", "Pincode", "Total Balance"
    ]

    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    corporates = Corporate.objects.all()

    for row_num, corporate in enumerate(corporates, 2):
        # Get merchants under this corporate project
        merchants = Merchant.objects.filter(project_name=corporate)
        total_points = MerchantPoints.objects.filter(merchant__in=merchants).aggregate(total=Sum('points'))['total'] or 0

        # Sr No.
        sheet.cell(row=row_num, column=1, value=row_num - 1)

        # Corporate Details
        sheet.cell(row=row_num, column=2, value=corporate.corporate_id or "")
        sheet.cell(row=row_num, column=3, value=corporate.project_name or "")
        sheet.cell(row=row_num, column=4, value=corporate.first_name or "")
        sheet.cell(row=row_num, column=5, value=corporate.last_name or "")
        sheet.cell(row=row_num, column=6, value=corporate.email or "")
        sheet.cell(row=row_num, column=7, value=corporate.mobile or "")
        sheet.cell(row=row_num, column=8, value=corporate.aadhaar_number or "")
        sheet.cell(row=row_num, column=9, value=corporate.gst_number or "")
        sheet.cell(row=row_num, column=10, value=corporate.pan_number or "")
        sheet.cell(row=row_num, column=11, value=corporate.shop_name or "")
        sheet.cell(row=row_num, column=12, value=corporate.address or "")
        sheet.cell(row=row_num, column=13, value=corporate.city or "")
        sheet.cell(row=row_num, column=14, value=corporate.state or "")
        sheet.cell(row=row_num, column=15, value=corporate.country or "")
        sheet.cell(row=row_num, column=16, value=corporate.pincode or "")
        # sheet.cell(row=row_num, column=17, value=corporate.created_at.strftime("%Y-%m-%d %H:%M:%S") if corporate.created_at else "")
        sheet.cell(row=row_num, column=17, value=total_points)

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Projects_Wise_Balance.xlsx"'

    return response

def export_merchant_wise_balance(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Merchant-Wise Balance"

    # Add headers to the sheet (including Sr No.)
    headers = [
        "Sr No.", "Merchant ID", "Merchant Name", "Email", "Mobile", 
        "Available Balance", "Status"
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
    for index, merchant_point in enumerate(merchant_points, start=1):
        row_num = index + 1  # Excel row (start from 2)
        available_points = merchant_point.points
        merchant = merchant_point.merchant

        sheet.cell(row=row_num, column=1, value=index)  # Sr No.
        sheet.cell(row=row_num, column=2, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=3, value=f"{merchant.first_name} {merchant.last_name}" or "")
        sheet.cell(row=row_num, column=4, value=merchant.email or "")
        sheet.cell(row=row_num, column=5, value=merchant.mobile or "")
        sheet.cell(row=row_num, column=6, value=available_points)
        sheet.cell(row=row_num, column=7, value=merchant.status or "")
        # sheet.cell(row=row_num, column=8, value=merchant.created_at.strftime("%Y-%m-%d %H:%M:%S") if merchant.created_at else "")

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

from django.contrib.auth.views import PasswordResetView
from django.contrib import messages


class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        messages.success(self.request, "A password reset link has been sent to your email address.")
        return super().form_valid(form)


# def export_customer_wise_balance(request):
#     # Create an Excel workbook and sheet
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active
#     sheet.title = "Customer-Wise Balance"

#     # Add headers to the sheet
#     headers = [
#         "Customer ID", "Customer Name", "Email", "Mobile", 
#         "Available Balance", "Created At"
#     ]
#     for col_num, header in enumerate(headers, 1):
#         cell = sheet.cell(row=1, column=col_num)
#         cell.value = header
#         cell.font = Font(bold=True)

#     # Fetch data from the CustomerPoints table
#     customer_points = CustomerPoints.objects.select_related('customer').all()
#     if not customer_points.exists():
#         print("No customer points found.")  # Debugging log

#     # Add data to the Excel sheet
#     for row_num, customer_point in enumerate(customer_points, 2):
#         available_points = customer_point.points

#         customer = customer_point.customer
#         sheet.cell(row=row_num, column=1, value=customer.customer_id or "")
#         sheet.cell(row=row_num, column=2, value=f"{customer.first_name} {customer.last_name}" or "")
#         sheet.cell(row=row_num, column=3, value=customer.email or "")
#         sheet.cell(row=row_num, column=4, value=customer.mobile or "")
#         sheet.cell(row=row_num, column=5, value=available_points)
#         # sheet.cell(row=row_num, column=6, value=customer.status or "")
#         sheet.cell(row=row_num, column=7, value=customer.created_at.strftime("%Y-%m-%d %H:%M:%S") if customer.created_at else "")

#     # Save the workbook to a BytesIO buffer
#     buffer = BytesIO()
#     workbook.save(buffer)
#     buffer.seek(0)

#     # Set the response to download the file
#     response = HttpResponse(
#         content=buffer,
#         content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
#     response["Content-Disposition"] = 'attachment; filename="Customer_wise_Balance.xlsx"'

#     return response

def export_customer_wise_balance(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Customer-Wise Balance"

    # Add headers (including Sr No.)
    headers = [
        "Sr No.", "Customer ID", "Customer Name", "Email", "Mobile",
        "Available Balance"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    customer_points = (
        CustomerPoints.objects
        .values(
            'customer__customer_id',
            'customer__first_name',
            'customer__last_name',
            'customer__email',
            'customer__mobile',
            # 'customer__created_at'
        )
        .annotate(total_points=Sum('points'))
    )

    for index, cp in enumerate(customer_points, start=1):
        row_num = index + 1
        sheet.cell(row=row_num, column=1, value=index)  # Sr No.
        sheet.cell(row=row_num, column=2, value=cp['customer__customer_id'] or "")
        sheet.cell(row=row_num, column=3, value=f"{cp['customer__first_name']} {cp['customer__last_name']}" or "")
        sheet.cell(row=row_num, column=4, value=cp['customer__email'] or "")
        sheet.cell(row=row_num, column=5, value=cp['customer__mobile'] or "")
        sheet.cell(row=row_num, column=6, value=cp['total_points'] or 0)
        # sheet.cell(row=row_num, column=7, value=cp['customer__created_at'].strftime("%Y-%m-%d %H:%M:%S") if cp['customer__created_at'] else "")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Customer_wise_Balance.xlsx"'

    return response


def export_customer_transaction(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Customer Transaction History"

    # Add headers (including Sr No.)
    headers = [
        "Sr No.", "Customer ID", "Customer Name", "Merchant ID", "Email", "Mobile", 
        "Transaction Type", "Points", "Transaction Date & Time"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    transactions = History.objects.select_related('customer').all()

    for index, transaction in enumerate(transactions, start=1):
        row_num = index + 1
        customer = transaction.customer
        merchant = transaction.merchant
        sheet.cell(row=row_num, column=1, value=index)  # Sr No.
        sheet.cell(row=row_num, column=2, value=customer.customer_id if customer else "")
        sheet.cell(row=row_num, column=3, value=f"{customer.first_name} {customer.last_name}" if customer else "")
        sheet.cell(row=row_num, column=4, value=merchant.merchant_id if merchant else "")
        sheet.cell(row=row_num, column=5, value=customer.email if customer else "")
        sheet.cell(row=row_num, column=6, value=customer.mobile if customer else "")
        sheet.cell(row=row_num, column=7, value=transaction.transaction_type or "")
        sheet.cell(row=row_num, column=8, value=transaction.points or 0)
        sheet.cell(
            row=row_num, column=9,
            value=transaction.created_at.strftime("%Y-%m-%d %H:%M:%S") if transaction.created_at else ""
        )

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Customer_Transaction_History.xlsx"'

    return response

def export_payment_dues(request):
    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    # Filter PaymentDetails with expiry_date in the last 7 days
    dues = PaymentDetails.objects.filter(expiry_date__range=(seven_days_ago, today)).select_related('merchant')

    # Create Excel workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Payment Dues - Last 7 Days"

    # Headers (added Sr No.)
    headers = [
        "Sr No.", "Merchant ID", "Merchant Name", "Mobile", "Email", 
        "Plan Type", "Validity (days)", "Expiry Date"
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    # Fill data (start serial number from 1)
    for index, due in enumerate(dues, start=1):
        row_num = index + 1
        merchant = due.merchant
        sheet.cell(row=row_num, column=1, value=index)  # Sr No.
        sheet.cell(row=row_num, column=2, value=merchant.merchant_id or "")
        sheet.cell(row=row_num, column=3,
            value=f"{merchant.first_name} {merchant.last_name}" if hasattr(merchant, 'first_name') and hasattr(merchant, 'last_name') else ""
        )
        sheet.cell(row=row_num, column=4, value=merchant.mobile if hasattr(merchant, 'mobile') else "")
        sheet.cell(row=row_num, column=5, value=merchant.email if hasattr(merchant, 'email') else "")
        sheet.cell(row=row_num, column=6, value=due.plan_type)
        # sheet.cell(row=row_num, column=7, value=due.payment_mode)
        # sheet.cell(row=row_num, column=8, value=due.paid_amount)
        sheet.cell(row=row_num, column=7, value=due.validity_days)
        sheet.cell(row=row_num, column=8, value=due.expiry_date.strftime("%Y-%m-%d") if due.expiry_date else "")

    # Return Excel as response
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Merchant_Payment_Dues.xlsx"'
    return response


def export_award_transaction(request):
    from openpyxl import Workbook
    from django.http import HttpResponse
    from bopo_award.models import MerchantPoints

    # Create an Excel workbook and sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Award Transactions"

    # Add headers to the sheet
    headers = ["Merchant ID", "Merchant Name", "Award Points", "Transaction Date"]
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Fetch award history from MerchantPoints table
    merchant_points = MerchantPoints.objects.all()

    # Add data to the sheet
    for row_num, merchant_point in enumerate(merchant_points, 2):
        sheet.cell(row=row_num, column=1, value=merchant_point.merchant.merchant_id if merchant_point.merchant else "")
        sheet.cell(row=row_num, column=2, value=f"{merchant_point.merchant.first_name} {merchant_point.merchant.last_name}" if merchant_point.merchant else "")
        sheet.cell(row=row_num, column=3, value=merchant_point.points)
        sheet.cell(row=row_num, column=4, value=merchant_point.updated_at.strftime("%Y-%m-%d %H:%M:%S") if merchant_point.updated_at else "")

    # Save the workbook to a BytesIO buffer
    from io import BytesIO
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Set the response to download the file
    response = HttpResponse(
        content=buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Award_Transactions.xlsx"'

    return response

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


def deduct_amount(request):
    if request.method == "POST":
        # Get form data
        user_id = request.POST.get("user_id")
        amount = float(request.POST.get("amount"))

        # Example logic (replace with your model logic)
        # Let's say you have a `UserBalance` model
        from .models import UserBalance
        try:
            user = UserBalance.objects.get(user_id=user_id)
            if user.balance >= amount:
                user.balance -= amount
                user.save()
                messages.success(request, f"₹{amount} deducted successfully!")
            else:
                messages.error(request, "Insufficient balance.")
        except UserBalance.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "bopo_admin/Superadmin/deduct_amount.html")

def superadmin_functionality(request):
    plans = ModelPlan.objects.all()
    return render(request, 'bopo_admin/Superadmin/superadmin_functionality.html' , {'plans': plans})
 




from django.shortcuts import redirect
from django.contrib import messages

def cash_out(request):
    if request.method == 'POST':
        merchant_id = request.POST.get('merchant_id')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        payment_date = request.POST.get('payment_date')

        # Save cash-out logic here
        # Example: CashOut.objects.create(...)
        messages.success(request, "Cash out recorded successfully.")
        return redirect('reduce_limit')  # Update with your actual page name


def helpdesk(request):
    help_requests = Help.objects.all()
    return render(request, 'bopo_admin/Helpdesk/helpdesk.html', {'help_requests': help_requests})

# def helpdesk_view(request):
#     filter_type = request.GET.get('filter', '')
#     help_requests = Help.objects.all()

#     now = timezone.now()

#     if filter_type == 'daily':
#         help_requests = help_requests.filter(created_at__date=now.date())
#     elif filter_type == 'weekly':
#         start_of_week = now - timedelta(days=now.weekday())  # Monday
#         help_requests = help_requests.filter(created_at__date__gte=start_of_week.date())
#     elif filter_type == 'monthly':
#         help_requests = help_requests.filter(created_at__month=now.month, created_at__year=now.year)
#     elif filter_type == 'yearly':
#         help_requests = help_requests.filter(created_at__year=now.year)

#     context = {
#         'help_requests': help_requests,
#         'filter_type': filter_type,
#     }
#     return render(request, 'bopo_admin/Helpdesk/helpdesk.html', context)

def reduce_limit(request):
    # Fetch cash-out records for merchants
    merchant_cash_outs = CashOut.objects.filter(user_category='merchant')
    
    # Fetch cash-out records for customers
    customer_cash_outs = CashOut.objects.filter(user_category='customer')

    return render(request, 'bopo_admin/Merchant/reduce_limit.html', {
        'merchant_cash_outs': merchant_cash_outs,
        'customer_cash_outs': customer_cash_outs,
    })
    
    
    
    

from django.db.models import Prefetch


def merchant_cash_outs_view(request):
    merchant_cash_outs = CashOut.objects.select_related(
        'merchant'
    ).prefetch_related(
        Prefetch('superadmin_payments', queryset=SuperAdminPayment.objects.all())
    )

    return render(request, 'bopo_admin/Merchant/merchant_cash_outs.html', {
        'merchant_cash_outs': merchant_cash_outs,
    })



from django.utils import timezone

def save_cash_out(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cashout_id = data.get('cashout_id')
            transaction_id = data.get('transaction_id')
            payment_method = data.get('payment_method')

            cashout = CashOut.objects.get(id=cashout_id)
   
            if cashout.status == 'paid':
                return JsonResponse({'status': 'error', 'message': 'This cash-out is already paid.'})

            # Mark cashout as paid
            cashout.status = 'paid'
            cashout.paid_at = timezone.now()
            cashout.save()



            SuperAdminPayment.objects.create(
                transaction_id=transaction_id,
                payment_method=payment_method,
                cashout=cashout
            )

            return JsonResponse({'status': 'success', 'message': 'Payment saved successfully'})
        except CashOut.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'CashOut not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



#     return render(request, 'bopo_admin/Superadmin/security_questions.html')

# def rental_plan(request):
#     return render(request, 'bopo_admin/Superadmin/rental_plan.html')

# def award_points(request):
#     return render(request, 'bopo_admin/Superadmin/award_points.html')

# def security_questions_view(request):
#     if request.method == 'GET':
#         questions = list(SecurityQuestion.objects.all().values('id', 'question'))
#         return JsonResponse(questions, safe=False)
    
#     elif request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             question_text = data.get('question', '').strip()
#             if question_text:
#                 question = SecurityQuestion.objects.create(question=question_text)
#                 return JsonResponse({'id': question.id, 'question': question.question})
#             return JsonResponse({'error': 'Invalid question'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.db.models import Count


@csrf_exempt
def add_security_question(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_text = data.get('question', '').strip()
        if question_text:
            question = SecurityQuestion.objects.create(question=question_text)
            return JsonResponse({'id': question.id, 'question': question.question})
        return JsonResponse({'error': 'Invalid question'}, status=400)


@csrf_exempt
def security_questions_view(request):
    if request.method == 'GET':
        questions = SecurityQuestion.objects.annotate(
            merchant_count=Count('merchants'),
            customer_count=Count('customers')
        )
        data = []
        for q in questions:
            is_taken = q.merchant_count > 0 or q.customer_count > 0
            data.append({
                'id': q.id,
                'question': q.question,
                'merchant_count': q.merchant_count + q.customer_count,
                'is_taken': is_taken,
                'can_delete': not is_taken,
                'can_edit': not is_taken,
            })
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_text = data.get('question', '').strip()
            if question_text:
                question = SecurityQuestion.objects.create(question=question_text)
                return JsonResponse({'id': question.id, 'question': question.question})
            return JsonResponse({'error': 'Invalid question'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def delete_security_question(request, question_id):
    if request.method == 'DELETE':
        try:
            question = SecurityQuestion.objects.get(id=question_id)
            if question.is_taken:
                return JsonResponse({'error': 'Cannot delete. Question already used.'}, status=400)
            question.delete()
            return JsonResponse({'message': 'Deleted successfully'})
        except SecurityQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_security_question(request, question_id):
    if request.method == 'PUT':
        try:
            question = SecurityQuestion.objects.get(id=question_id)
            if question.is_taken:
                return JsonResponse({'error': 'Cannot edit. Already in use.'}, status=400)
            data = json.loads(request.body)
            question_text = data.get('question', '').strip()
            if question_text:
                question.question = question_text
                question.save()
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'Invalid input'}, status=400)
        except SecurityQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# def get_deduct_amount(request):
#     try:
#         setting = DeductSetting.objects.get(id=1)
#         return JsonResponse({'deduct_amount': setting.deduct_percentage})
#     except DeductSetting.DoesNotExist:
#         return JsonResponse({'deduct_amount': 0})  # default if not set    


def get_deduct_amount(request):
    try:
        setting = DeductSetting.objects.get(id=1)
        return JsonResponse({
            # 'deduct_percentage': setting.deduct_percentage,
            'cust_merch': setting.cust_merch,
            'merch_merch': setting.merch_merch,
            'cust_cust': setting.cust_cust,
            'normal_global': setting.normal_global,
        })
    except DeductSetting.DoesNotExist:
        return JsonResponse({'message': 'Not set yet.'})

    
# def set_deduct_amount(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         deduct_amount = data.get('deduct_amount')

#         if deduct_amount is None or deduct_amount < 0:
#             return JsonResponse({'error': 'Invalid deduct amount.'}, status=400)

#         # Always store in ID=1 (single row)
#         setting, created = DeductSetting.objects.get_or_create(id=1)
#         setting.deduct_percentage = deduct_amount
#         setting.save()

#         return JsonResponse({'message': 'Deduct amount updated successfully.', 'deduct_percentage': setting.deduct_percentage})
    
#     return JsonResponse({'error': 'Invalid method.'}, status=405)

@csrf_exempt
def save_deduct_settings(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            cust_merch = data.get('deduct_customer_merchant')
            merch_merch = data.get('deduct_merchant_merchant')
            cust_cust = data.get('deduct_customer_customer')
            normal_global = data.get('deduct_no_usage_six_months')

            # Validate values (optional)
            for value in [cust_merch, merch_merch, cust_cust, normal_global]:
                if value is not None and (float(value) < 0 or float(value) > 100):
                    return JsonResponse({'error': 'Deduction values must be between 0 and 100.'}, status=400)

            # Save to DB (single row ID=1)
            setting, created = DeductSetting.objects.get_or_create(id=1)
            setting.cust_merch = cust_merch
            setting.merch_merch = merch_merch
            setting.cust_cust = cust_cust
            setting.normal_global = normal_global
            setting.save()

            return JsonResponse({'status': 'success','message': 'Deduct percentages saved successfully!.'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method.'}, status=405)

# def save_model_plan(request):
#     if request.method == "POST":
#         data = json.loads(request.body)

#         plan_validity = data.get("plan_validity")
#         plan_type = data.get("plan_type")
#         description = data.get("description")
        

#         if not all([plan_validity, plan_type, description]):
#             return JsonResponse({"error": "Missing fields"}, status=400)

#         plan, created = ModelPlan.objects.update_or_create(
#             plan_type=plan_type,
#             defaults={
#                 "plan_validity": plan_validity,
#                 "description": description
#             }
#         )
#         return JsonResponse({"message": "Model plan saved successfully."})
#     return JsonResponse({"error": "Invalid method"}, status=405)


def update_model_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plan_validity = data.get('plan_validity')
        plan_type = data.get('plan_type')
        description = data.get('description')

        try:
            # Assuming you are updating based on plan_type
            plan = ModelPlan.objects.filter(plan_type=plan_type).first()
            if plan:
                plan.plan_validity = plan_validity
                plan.description = description
                plan.save()
            else:
                ModelPlan.objects.create(
                    plan_validity=plan_validity,
                    plan_type=plan_type,
                    description=description
                )
            return JsonResponse({'success': True, 'message': 'Plan updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def model_plan_list(request):
    plans = ModelPlan.objects.all()
    print("Plans:", plans)  # Debugging log
    return render(request, 'bopo_admin/Superadmin/superadmin_functionality.html', {'plans': plans})

# def save_award_points(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         award_percentage = data.get('award_percentage')

#         try:
#             # Update the award percentage or create a new record if none exists
#             award, created = AwardPoints.objects.update_or_create(
#                 id=1,  # Assuming you only have one award entry, so use a fixed ID
#                 defaults={'percentage': award_percentage}
#             )
#             return JsonResponse({'success': True, 'message': 'Award points updated successfully.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})

#     return JsonResponse({'success': False, 'error': 'Invalid request'})


def get_award_point(request):
    award = AwardPoints.objects.first()
    return JsonResponse({'percentage': award.percentage if award else 0})


def update_award_point(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_percentage = int(data.get('percentage', 0))

        award, created = AwardPoints.objects.get_or_create(id=1)
        award.percentage = new_percentage
        award.save()
        return JsonResponse({'status': 'success', 'percentage': award.percentage})
    return JsonResponse({'status': 'error'}, status=400)

def save_superadmin_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transactionId')
            payment_method = data.get('paymentMethod')
            cash_out_id = data.get('cashOutId')

            # Ensure the transaction ID is unique
            if SuperAdminPayment.objects.filter(transaction_id=transaction_id).exists():
                return JsonResponse({"error": "Transaction ID already exists"}, status=400)

            cash_out_instance = CashOut.objects.get(id=cash_out_id)

            SuperAdminPayment.objects.create(
                transaction_id=transaction_id,
                payment_method=payment_method,
                cashout=cash_out_instance
            )

            # Optionally update CashOut status
            cash_out_instance.status = "Completed"
            cash_out_instance.save()

            return JsonResponse({"message": "Payment recorded successfully"}, status=201)

        except CashOut.DoesNotExist:
            return JsonResponse({"error": "CashOut record not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def resolve_help(request, help_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            help_obj = Help.objects.get(id=help_id)
            if help_obj.status != 'resolved':
                help_obj.status = 'resolved'
                help_obj.remark = request.POST.get('solution')  # Save remark
                help_obj.save()
                return JsonResponse({'success': True, 'message': 'Marked as Resolved with Remark'})
            else:
                return JsonResponse({'success': False, 'message': 'Already resolved'})
        except Help.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Help request not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

   
  
   
def merchant_list(request):
    merchants = Merchant.objects.filter(project_name=request.user.corporate_id)
    return render(request, 'bopo_admin/Corporate/merchant_list.html', {'merchants': merchants})

def corporate_terminals(request):
    user = request.user
    project_id = user.corporate_id  # Still coming from user

    # Use the correct field name in the filter
    merchants = Merchant.objects.filter(project_name_id=project_id)

    print("Project ID:", project_id)
    print("Merchants:", merchants)

    selected_merchant_id = request.GET.get('merchant_id')

    if selected_merchant_id:
        terminals = Terminal.objects.filter(merchant_id=selected_merchant_id)
    else:
        terminals = Terminal.objects.none()

    return render(request, 'bopo_admin/Corporate/corporate_terminals.html', {
        'merchants': merchants,
        'terminals': terminals
    })


def get_admin_merchant(request, merchant_id):
    # Get the merchant object or return 404 if not found
    merchant = get_object_or_404(Merchant, id=merchant_id)

    # Retrieve the state object by its name (merchant.state is a string, so use name)
    try:
        state_obj = State.objects.get(name=merchant.state)  # Now query by name
    except State.DoesNotExist:
        return JsonResponse({'error': f'State "{merchant.state}" not found'}, status=404)

    states = State.objects.all().order_by('name')
    state_data = [{"id": state.id, "name": state.name} for state in states]
    # Retrieve cities based on selected state
    cities = City.objects.filter(state=state_obj)  # Now we use the State object

    # Convert cities to a dictionary for use in the frontend
    city_data = [{"id": city.id, "name": city.name} for city in cities]

    # Data to send to the frontend
    data = {
        "id": merchant.id,
        "first_name": merchant.first_name,
        "last_name": merchant.last_name,
        "email": merchant.email,
        "mobile": merchant.mobile,
        "shop_name": merchant.shop_name,
        "address": merchant.address,
        "aadhaar_number": merchant.aadhaar_number,
        "pin": merchant.pin,
        "gst_number": merchant.gst_number,
        "pan_number": merchant.pan_number,
        "legal_name": merchant.legal_name,
        "state": merchant.state,
        "city": merchant.city,
        "pincode": merchant.pincode,
        "cities": city_data,  # Include cities data
        "states": state_data 
    }

    return JsonResponse(data)


def update_admin_merchant(request):
    if request.method == 'POST':
        merchant_id = request.POST.get('merchant_id')
        try:
            merchant = Merchant.objects.get(id=merchant_id)

            email = request.POST.get('email')
            mobile = request.POST.get('mobile')

            # Check duplicate email in Merchant (excluding current)
            if Merchant.objects.filter(email=email).exclude(id=merchant_id).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile in Merchant (excluding current)
            if Merchant.objects.filter(mobile=mobile).exclude(id=merchant_id).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Check duplicate email in Corporate
            if Corporate.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email is already registered."})

            # Check duplicate mobile in Corporate
            if Corporate.objects.filter(mobile=mobile).exists():
                return JsonResponse({"success": False, "message": "Mobile number is already registered."})

            # Save updated data
            merchant.email = email
            merchant.mobile = mobile
            merchant.save()

            return JsonResponse({'success': True, 'message': 'Merchant updated successfully'})
        
        except Merchant.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Merchant not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

        
def corporate_credentials(request):
    if request.method == 'POST':
        # Handle your form submission here
        pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAX call to fetch merchants
        project_id = request.user.corporate_id  # Assuming this is how project ID is tied
        merchants = Merchant.objects.filter(project_name=project_id).values('merchant_id', 'first_name', 'last_name')
        return JsonResponse({'merchants': list(merchants)})

    # Initial page load
    return render(request, 'bopo_admin/Corporate/corporate_credentials.html')

# def corporate_add_merchant(request):
#     if request.method == 'POST':
#         print('mobile' , request.POST.get('mobile'))
#         print('email' , request.POST.get('email'))
#         user = request.user
#         corporate=Corporate.objects.get(id=user.corporate.id)  
#         merchant = Merchant(
#         first_name=request.POST.get('first_name'),
#         last_name=request.POST.get('last_name'),
#         email=request.POST.get('email'),
#         mobile=request.POST.get('mobile'),
#         shop_name=request.POST.get('shop_name'),
#         legal_name=request.POST.get('legal_name'),
#         state=request.POST.get('state'),
#         city=request.POST.get('city'),
#         country=request.POST.get('country'),
#         pincode=request.POST.get('pincode'),
#         corporate_id=corporate.corporate_id,  # Save corporate_id as string
#         project_name=corporate,  
#         aadhaar_number=request.POST.get('aadhaar_number'),
#         gst_number=request.POST.get('gst_number'),
#         pan_number=request.POST.get('pan_number'),
#         address=request.POST.get('address'),
#         pin=request.POST.get('pin'),
#         user_type='corporate',
#         )
#         merchant.save()

#         return JsonResponse({'success': True, 'message': 'Merchant added successfully!'})

#     else:
#         states = State.objects.all().order_by('name')
#         state_data = [{"id": state.id, "name": state.name} for state in states]
#         return render(request, 'bopo_admin/Corporate/corporate_add_merchant.html', {'states': state_data})


def corporate_add_merchant(request):
    if request.method == "POST":
        try:
            is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

            # Extract form data
            select_project = request.POST.get("select_project")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            aadhaar_number = request.POST.get("aadhaar_number")
            pin = request.POST.get("pin")
            gst_number = request.POST.get("gst_number")
            shop_name = request.POST.get("shop_name")
            pan_number = request.POST.get("pan_number")
            address = request.POST.get("address")
            legal_name = request.POST.get("legal_name")
            pincode = request.POST.get("pincode")
            city_id = request.POST.get("city")
            state_id = request.POST.get("state")
            country = request.POST.get("country", "India")
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)

            # Unique field checks
            if Merchant.objects.filter(email=email).exists() or Corporate.objects.filter(email=email).exists():
                message = "Email is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            if Merchant.objects.filter(mobile=mobile).exists() or Corporate.objects.filter(mobile=mobile).exists():
                message = "Mobile number is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            if Merchant.objects.filter(aadhaar_number=aadhaar_number).exists() or Corporate.objects.filter(aadhaar_number=aadhaar_number).exists():
                message = "Aadhaar number is already registered."
                return JsonResponse({"success": False, "message": message}) if is_ajax else redirect_with_error(message)

            # Fetch the corporate ID of the logged-in user
            corporate = request.user.corporate  # Assuming user is a BopoAdmin and has a corporate field
            corporate_id = corporate.corporate_id  # Get the corporate_id associated with the logged-in user

            # Generate Merchant ID
            project_name = corporate.project_name  # Assuming this is the project name you want to associate
            project_abbr = project_name[:4].upper()
            random_number = ''.join(random.choices(string.digits, k=11))
            merchant_id = f"{project_abbr}{random_number}"

            # Create Merchant
            merchant = Merchant.objects.create(
                user_type='corporate',
                merchant_id=merchant_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile=mobile,
                aadhaar_number=aadhaar_number,
                pin=pin,
                gst_number=gst_number,
                pan_number=pan_number,
                shop_name=shop_name,
                legal_name=legal_name,
                address=address,
                pincode=pincode,
                state=state,
                city=city,
                country=country,
                corporate_id=corporate_id,  # Use the corporate_id here
                project_name=corporate  # Assign the corporate instance as project name
            )

            # Create Terminal
            terminal_id = "TID" + ''.join(random.choices(string.digits, k=8))
            tid_pin = random.randint(1000, 9999)

            Terminal.objects.create(
                terminal_id=terminal_id,
                tid_pin=tid_pin,
                merchant_id=merchant
            )

            success_message = "Merchant added successfully."
            return JsonResponse({"success": True, "message": success_message}) if is_ajax else redirect_with_success(success_message)

        except Exception as e:
            print("Error saving merchant:", e)
            return JsonResponse({"success": False, "message": "Something went wrong. Please check your inputs."})

    corporates = Corporate.objects.all()
    return render(request, "bopo_admin/Corporate/corporate_add_merchant.html", {"corporates": corporates})


def logo(request): 
    if request.user.role == 'corporate_admin':
        try:
            corporate = Corporate.objects.get(corporate_id=request.user.corporate_id)
            return render(request, 'bopo_admin/base.html', {'corporate': corporate})
        except Corporate.DoesNotExist:
            return render(request, 'bopo_admin/base.html', {'error': 'Corporate not found'})
    
    elif request.user.role in ['super_admin', 'employee']:
        logo = Logo.objects.first()
        return render(request, 'bopo_admin/base.html', {'logo': logo})


    else:  # Fallback case
        logo = Logo.objects.first()
        return render(request, 'bopo_admin/base.html', {'logo': logo})


# def upload_logo(request):
#     if request.method == 'POST' and request.FILES.get('logo'):
#         if request.user.role in ['super_admin', 'employee']:  # Allow both roles to update
#             logo_file = request.FILES['logo']
#             logo_obj, _ = Logo.objects.get_or_create(id=1)  # Super admin logo
#             logo_obj.logo = logo_file
#             logo_obj.save()
#             return JsonResponse({'success': True, 'url': logo_obj.logo.url})
    
#     return JsonResponse({'success': False})



def upload_logo(request):
    if request.method == 'POST' and request.FILES.get('logo'):
        if request.user.role in ['super_admin', 'employee']:  # Allow superadmins and employees to update the logo
            logo_file = request.FILES['logo']
            logo_obj, _ = Logo.objects.get_or_create(id=1)  # For simplicity, use the first logo or create one
            logo_obj.logo = logo_file
            logo_obj.save()
            return JsonResponse({'success': True, 'url': logo_obj.logo.url})

    return JsonResponse({'success': False})

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification_to_user(user_id, message):
    channel_layer = get_channel_layer()
    group_name = f"notifications_{user_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "notification": message
        }
    )


def trigger_notification(request):
    user_id = 2
    message = "You have a new transaction alert!"
    send_notification_to_user(user_id, message)
    return JsonResponse({"status": "Notification sent"})


def send_customer_credentials(request):
    customers = Customer.objects.all().order_by('customer_id')

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')

        try:
            if not customer_id:
                return JsonResponse({'status': 'error', 'message': 'Customer ID is required'})

            customer = Customer.objects.get(customer_id=customer_id)
            phone_number = customer.mobile
            if not phone_number.startswith('+'):
                phone_number = f'+91{phone_number}'

            message_text = (
                f"Dear {customer.first_name},\n\n"
                f"Your BOPO login credentials:\n"
                f"Customer ID: {customer.customer_id}\n"
                f"Customer PIN: {customer.pin}\n\n"
                f"Regards,\nBOPO Support Team"
            )

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message_text,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )

            return JsonResponse({'status': 'success', 'message': 'Customer credentials sent successfully!'})

        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while sending credentials'})

    return render(request, 'bopo_admin/Customer/send_customer_credentials.html', {
        'customers': customers
    })
    
    
    
    
def get_individual_merchants(request):
    merchants = Merchant.objects.filter(user_type='individual')
    data = {
        "merchants": [
            {
                "merchant_id": m.merchant_id,
                "first_name": m.first_name,
                "last_name": m.last_name,
            }
            for m in merchants
        ]
    }
    return JsonResponse(data)


def transaction_history(request):
    history_list = History.objects.select_related('customer', 'merchant').order_by('-created_at')
    merchant_cashouts = CashOut.objects.select_related('customer', 'merchant').prefetch_related('superadminpayment_set')\
    .filter(status__iexact='Paid')
    
    context = {
        'history_list': history_list,
        'merchant_cashouts': merchant_cashouts,
    }
    
    return render(request, 'bopo_admin/Helpdesk/history.html',context)

