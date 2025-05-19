from datetime import timezone
import logging
import string
import requests
from twilio.rest import Client
from django.core.mail import send_mail
from twilio.http.http_client import TwilioHttpClient
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from random import randint
from django.shortcuts import get_object_or_404
import mimetypes
import base64
from django.core.files.storage import default_storage
from rest_framework import status
from django.utils.timezone import now
from bopo_backend import settings

from .models import  Customer, Logo, Merchant, Terminal, User, Corporate
from .serializers import   CustomerSerializer, MerchantSerializer,  TerminalSerializer, UserSerializer



logger = logging.getLogger(__name__)

def generate_terminal_id():
    return 'TID' + ''.join(random.choices(string.digits, k=8))

class CreateTerminalAPIView(APIView):
    def post(self, request):
        merchant_id = request.data.get('merchant_id')
        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': 'Merchant not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Keep generating until unique terminal_id is found
        terminal_id = generate_terminal_id()
        while Terminal.objects.filter(terminal_id=terminal_id).exists():
            terminal_id = generate_terminal_id()

        terminal = Terminal.objects.create(terminal_id=terminal_id, merchant_id=merchant)
        serializer = TerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OTPService:
    """ Helper class to handle OTP sending via Twilio """

    @staticmethod
    def send_sms_otp(mobile_number, otp):
        """ Sends OTP via SMS using Twilio """
        try:
            if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
                raise ValueError("Twilio credentials are not configured in settings.")

            # ✅ Set timeout explicitly
            http_client = TwilioHttpClient()
            http_client.session = requests.Session()
            http_client.session.request = lambda *args, **kwargs: requests.request(*args, timeout=5, **kwargs)

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, http_client=http_client)
            message = client.messages.create(
                body=f'Your OTP for verification is {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=f'+91{mobile_number}'
            )
            print(f"✅ SMS sent successfully: {message.sid}")
            return True
        except requests.exceptions.Timeout:
            print(f"❌ Twilio request timed out.")
            return False
        except Exception as e:
            print(f"❌ Failed to send OTP via SMS: {e}")
            return False


# class RegisterCorporateAPIView(APIView):
#     """API to register a Corporate account and send OTP"""

#     def post(self, request):
#         mobile = request.data.get("mobile")

#         if not mobile:
#             return Response({"error": "Mobile number is required."}, status=status.HTTP_400_BAD_REQUEST)

#         otp = random.randint(100000, 999999)

#         try:
#             corporate = Corporate.objects.get(mobile=mobile)

#             if corporate.verified_at:
#                 return Response(
#                     {"message": "Corporate is already registered and verified.", "corporate_id": corporate.corporate_id},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             corporate.otp = otp
#             corporate.save()
#             message = "Corporate exists but not verified. OTP resent successfully."

#         except Corporate.DoesNotExist:
#             # ✅ Generate unique corporate_id
#             last_corporate = Corporate.objects.exclude(corporate_id=None).order_by("-corporate_id").first()

#             if last_corporate and last_corporate.corporate_id:
#                 try:
#                     new_id = int(last_corporate.corporate_id[4:]) + 1  # Extract number and increment
#                 except ValueError:
#                     new_id = 1  # In case corporate_id is corrupted
#             else:
#                 new_id = 1  # First corporate account

#             corporate_id = f"CORP{new_id:06d}"  # Format: CORP000001, CORP000002, etc.

#             # ✅ Store new corporate data
#             corporate_data = request.data.copy()
#             corporate_data["corporate_id"] = corporate_id
#             corporate_data["otp"] = otp

#             serializer = CorporateSerializer(data=corporate_data)
#             if serializer.is_valid():
#                 corporate = serializer.save()
#                 message = "Corporate registered & OTP sent successfully."
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         # ✅ Send OTP
#         if OTPService.send_sms_otp(mobile, otp):
#             return Response({"message": message, "corporate_id": corporate.corporate_id}, status=status.HTTP_200_OK)

#         return Response({"error": "OTP sending failed."}, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserAPIView(APIView):
    """API to register, update, and delete a Merchant or Customer"""

     

    def post(self, request):
        """Handles customer or merchant registration"""
        mobile = request.data.get("mobile")
        user_type = request.data.get("user_type")
        project_name = request.data.get("project_name", "")
        user_category = request.data.get("user_category")

        # Validate mobile number
        if not mobile:
            return Response({"message": "Mobile number is required.", "user_type": None, "customer_id": None},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate user category
        if user_category not in ["customer", "merchant"]:
            return Response({"message": "Invalid user category.", "user_type": None, "customer_id": None},
                            status=status.HTTP_400_BAD_REQUEST)

        if user_category == "customer":
            return self.register_customer(request)

        return self.register_merchant(request, mobile, user_type, project_name)

    def put(self, request):
        """Handles updating customer or merchant details"""
        user_category = request.data.get("user_category")
        mobile = request.data.get("mobile")

        if user_category == "customer":
            return self.update_customer(request, mobile)
        elif user_category == "merchant":
            return self.update_merchant(request, mobile)
        else:
            return Response({"message": "Invalid user category."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Handles deleting a customer or merchant"""
        user_category = request.data.get("user_category")
        mobile = request.data.get("mobile")

        if user_category == "customer":
            return self.delete_customer(request, mobile)
        elif user_category == "merchant":
            return self.delete_merchant(request, mobile)
        else:
            return Response({"message": "Invalid user category."}, status=status.HTTP_400_BAD_REQUEST)

    def register_customer(self, request):
        """Handles customer registration with OTP verification"""
        mobile = request.data.get("mobile")

        if not mobile:
            return Response({"message": "Mobile number is required.", "user_type": "customer", "customer_id": None},
                            status=status.HTTP_400_BAD_REQUEST)

        otp = random.randint(100000, 999999)

        try:
            customer = Customer.objects.get(mobile=mobile)

            if customer.verified_at:
                return Response({"message": "Customer is already registered and verified.",
                                 "user_type": "customer", "customer_id": customer.customer_id},
                                status=status.HTTP_400_BAD_REQUEST)

            customer.otp = otp
            customer.save()
            message = "Customer exists but not verified. OTP resent successfully."

        except Customer.DoesNotExist:
            last_customer = Customer.objects.order_by("-customer_id").first()
            new_customer_id = 1 if not last_customer else int(last_customer.customer_id[4:]) + 1
            customer_id = f"CUST{new_customer_id:06d}"

            serializer = CustomerSerializer(data={**request.data, "customer_id": customer_id, "otp": otp})
            if serializer.is_valid():
                age = request.data.get("age")
                if age is None:
                    request.data["age"] = None 
                customer = serializer.save()
                message = "Customer registered & OTP sent successfully."
            else:
                return Response({"message": "Validation error", "errors": serializer.errors, "user_type": "customer",
                                 "customer_id": None}, status=status.HTTP_400_BAD_REQUEST)

        # Send OTP via SMS
        if OTPService.send_sms_otp(mobile, otp):
            return Response({"message": message, "user_type": "customer", "user_id": customer.customer_id},
                            status=status.HTTP_200_OK)
        else:
            return Response({"message": "Failed to send OTP.", "user_type": "customer", "customer_id": None},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

    def update_customer(self, request, mobile):
        """Update customer details"""
        customer = get_object_or_404(Customer, mobile=mobile)

        if customer.verified_at:
            return Response({"message": "Verified customers cannot be updated."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer updated successfully.", "customer_id": customer.customer_id},
                            status=status.HTTP_200_OK)
        return Response({"message": "Update failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete_customer(self, request, mobile):
        """Delete a customer if not verified"""
        customer = get_object_or_404(Customer, mobile=mobile)

        if customer.verified_at:
            return Response({"message": "Verified customers cannot be deleted."}, status=status.HTTP_400_BAD_REQUEST)

        customer.delete()
        return Response({"message": "Customer deleted successfully."}, status=status.HTTP_200_OK)
    

    def register_merchant(self, request, mobile, user_type, project_name):
        """Handles merchant registration"""

        if user_type != "individual":
            return Response({
                "message": "Invalid user type, only individual merchant can register here",
                "user_type": "merchant",
                "merchant_id": None
            }, status=status.HTTP_400_BAD_REQUEST)

        prefix = "MID"
        merchant_id = f"{prefix}{''.join(random.choices(string.digits, k=12))}"
        otp = random.randint(100000, 999999)

        terminal_id, tid_pin = self._generate_terminal_info()

        try:
            merchant = Merchant.objects.get(mobile=mobile)
            if merchant.verified_at:
                return Response({
                    "message": "Merchant is already registered and verified.",
                    "user_type": "merchant",
                    "user_id": merchant.merchant_id
                }, status=status.HTTP_400_BAD_REQUEST)

            merchant.otp = otp
            merchant.save()
            message = "Merchant exists but not verified. OTP resent successfully."

        except Merchant.DoesNotExist:
            serializer = MerchantSerializer(data={
                **request.data,
                "merchant_id": merchant_id,
                "otp": otp
            })
            if serializer.is_valid():
                merchant = serializer.save()
                message = "Merchant registered & OTP sent successfully."
            else:
                return Response({
                    "message": "Validation error",
                    "errors": serializer.errors,
                    "user_type": "merchant",
                    "merchant_id": None
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Save terminal info
        Terminal.objects.create(
            terminal_id=terminal_id,
            tid_pin=tid_pin,
            merchant_id=merchant
        )

        # ✅ Send OTP
        if OTPService.send_sms_otp(mobile, otp):
            return Response({
                "message": message,
                "user_type": "merchant",
                "user_id": merchant.merchant_id,
                "terminal_id": terminal_id,
                "tid_pin": tid_pin
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Failed to send OTP.",
                "user_type": "merchant",
                "user_id": merchant.merchant_id,
                "terminal_id": terminal_id,
                "tid_pin": tid_pin
            }, status=status.HTTP_400_BAD_REQUEST)
            
    def _generate_terminal_info(self):
        """Generates a unique terminal ID and PIN"""
        tid_prefix = "TID"
        
        while True:
            tid_number = random.randint(10000001, 99999999)
            terminal_id = f"{tid_prefix}{tid_number}"
            if not Terminal.objects.filter(terminal_id=terminal_id).exists():
                break

        while True:
            tid_pin = random.randint(1000, 9999)
            if not Terminal.objects.filter(tid_pin=tid_pin).exists():
                break

        return terminal_id, tid_pin



            
            
    def update_merchant(self, request, mobile):
        """Update merchant details"""
        merchant = get_object_or_404(Merchant, mobile=mobile)

        if merchant.verified_at:
            return Response({"message": "Verified merchants cannot be updated."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MerchantSerializer(merchant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Merchant updated successfully.", "merchant_id": merchant.merchant_id},
                            status=status.HTTP_200_OK)
        return Response({"message": "Update failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete_merchant(self, request, mobile):
        """Delete a merchant if not verified"""
        merchant = get_object_or_404(Merchant, mobile=mobile)

        if merchant.verified_at:
            return Response({"message": "Verified merchants cannot be deleted."}, status=status.HTTP_400_BAD_REQUEST)

        merchant.delete()
        return Response({"message": "Merchant deleted successfully."}, status=status.HTTP_200_OK)



class LoginAPIView(APIView):
    """API for Customer, Merchant, and Terminal Login"""
    
    def generate_otp(self):
        """Generate a 6-digit OTP."""
        return randint(100000, 999999)
    
    def send_otp(self, mobile, otp):
        """Send OTP to the user's mobile number."""
        # Replace with your SMS service integration
        try:
            # Example of sending OTP via SMS (replace with actual API)
            message = f"Your OTP is {otp}. Please use this to verify your account."
            # For example, send the OTP via SMS to the user's mobile number
            send_mail(
                'OTP Verification',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [mobile],
                fail_silently=False,
            )
            logger.info(f"OTP sent to {mobile}")
        except Exception as e:
            logger.error(f"Error sending OTP to {mobile}: {e}")
            return False
        return True
    
    def get_logo_base64(self, logo_instance):
        try:
            if logo_instance and logo_instance.logo and default_storage.exists(logo_instance.logo.name):
                with default_storage.open(logo_instance.logo.name, 'rb') as logo_file:
                    logo_data = logo_file.read()
                # Detect the image type based on file extension
                ext = logo_instance.logo.name.split('.')[-1].lower()
                mime_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                return f"data:{mime_type};base64,{logo_base64}"
        except Exception as e:
            logger.error(f"Error encoding logo to base64: {e}")
        return None

    
    @staticmethod
    def is_customer_profile_complete(customer):
        required_fields = [
            customer.first_name,
            customer.last_name,
            customer.mobile,
            customer.age,
            customer.gender,
            customer.pin,
            customer.pan_number,
            customer.address,
            customer.city,
            customer.country,
            customer.state,
            customer.pincode
        ]
        return all(required_fields)
    
    @staticmethod
    def is_merchant_profile_complete(merchant):
        required_fields = [
            merchant.first_name,
            merchant.last_name,
            merchant.mobile,
            merchant.pin,
            merchant.aadhaar_number,
            merchant.pan_number,
            merchant.shop_name,
            merchant.address,
            merchant.city,
            merchant.state,
            merchant.pincode
        ]
        return all(required_fields)

    def post(self, request):
        try:
            identifier = request.data.get("mobile") or request.data.get("merchant_id") or request.data.get("terminal_id")
            pin = request.data.get("pin") or request.data.get("tid_pin")
            user_category = request.data.get("user_category")
            otp = request.data.get("otp")  # OTP entered by user

            logger.info(f"Login attempt - Identifier: {identifier}, User Category: {user_category}")

            if not identifier or not pin or not user_category:
                return Response({
                    "error": "Identifier, PIN, and user_category are required."
                }, status=status.HTTP_400_BAD_REQUEST)

            response_data = {}

            if user_category == "customer":
                user = Customer.objects.filter(mobile=str(identifier)).first()
                if not user or str(user.status).strip().lower() != "active":
                    return Response({"error": "Invalid credentials or inactive account."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if user is verified
                if not user.verified_at:
                    if not otp:
                        # Generate and send OTP if not provided
                        otp = self.generate_otp()
                        user.otp = otp
                        user.save(update_fields=["otp"])
                        self.send_otp(user.mobile, otp)
                        return Response({"message": "OTP sent to your registered mobile number."}, status=status.HTTP_200_OK)
                    else:
                        # Validate OTP if provided
                        if str(user.otp) != str(otp):
                            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                        # OTP is valid, mark as verified
                        user.verified_at = timezone.now()
                        user.save(update_fields=["verified_at"])

                if not user.pin or str(user.pin) != str(pin):
                    return Response({"error": "Invalid PIN."}, status=status.HTTP_400_BAD_REQUEST)
                
                # ----> Always assign Logo with ID = 1 for customers
                logo_instance = Logo.objects.filter(id=1).first()
                if logo_instance:
                    user.logo = logo_instance
                    user.save(update_fields=["logo"])

                logo = request.build_absolute_uri(user.logo.logo.url) if user.logo and user.logo.logo else None
                logo_base64 = self.get_logo_base64(user.logo) if user.logo else None

                response_data = {
                    "message": "Login successful",
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "pin": user.pin,
                    "user_category": "customer",
                    "customer_id": user.customer_id,
                    "is_profile_updated": self.is_customer_profile_complete(user),
                    "logo": logo,
                    "logo_base64": logo_base64
                }

            elif user_category == "merchant":
                # Merchant login flow (same as customer with OTP validation)
                if str(identifier).isdigit() and len(str(identifier)) == 10:
                    user = Merchant.objects.filter(mobile=str(identifier)).first()
                else:
                    user = Merchant.objects.filter(merchant_id=identifier).first()

                if not user or str(user.status).strip().lower() != "active":
                    return Response({"error": "Invalid credentials or inactive account."}, status=status.HTTP_400_BAD_REQUEST)

                if not user.verified_at and user.user_type != "corporate":
                    if not otp:
                        # Generate and send OTP if not provided
                        otp = self.generate_otp()
                        user.otp = otp
                        user.save(update_fields=["otp"])
                        self.send_otp(user.mobile, otp)
                        return Response({"message": "OTP sent to your registered mobile number."}, status=status.HTTP_200_OK)
                    else:
                        # Validate OTP if provided
                        if str(user.otp) != str(otp):
                            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                        # OTP is valid, mark as verified
                        user.verified_at = timezone.now()
                        user.save(update_fields=["verified_at"])

                if not user.pin or str(user.pin) != str(pin):
                    return Response({"error": "Invalid PIN."}, status=status.HTTP_400_BAD_REQUEST)

                if not user.logo:
                    default_logo = Logo.objects.filter(id=1).first()
                    if default_logo:
                        user.logo = default_logo
                        user.save(update_fields=["logo"])

                logo = request.build_absolute_uri(user.logo.logo.url) if user.logo and user.logo.logo else None
                logo_base64 = self.get_logo_base64(user.logo) if user.logo else None

                response_data = {
                    "message": "Login successful",
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "pin": user.pin,
                    "user_category": "merchant",
                    "merchant_id": user.merchant_id,
                    "is_profile_updated": user.is_profile_updated,
                    "user_type": user.user_type,
                    "logo": logo,
                    "logo_base64": logo_base64
                }

                if user.user_type == "corporate":
                    response_data["corporate_id"] = user.corporate_id if user.corporate_id else None

            elif user_category == "terminal":
                terminal = Terminal.objects.filter(terminal_id=identifier).first()
                if not terminal:
                    return Response({"error": "Invalid Terminal ID."}, status=status.HTTP_400_BAD_REQUEST)

                if not terminal.tid_pin or str(terminal.tid_pin) != str(pin):
                    return Response({"error": "Invalid Terminal PIN."}, status=status.HTTP_400_BAD_REQUEST)

                response_data = {
                    "message": "Login successful",
                    "user_category": "terminal",
                    "terminal_id": terminal.terminal_id,
                    "tid_pin": terminal.tid_pin,
                    "merchant_id": terminal.merchant_id.merchant_id  # Assuming ForeignKey to Merchant
                }

            else:
                return Response({"error": "Invalid user category."}, status=status.HTTP_400_BAD_REQUEST)

            logger.info("Login successful")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

class VerifyOTPAPIView(APIView):
    """API to verify OTP for Customer or Merchant"""

    def post(self, request):
        try:
            otp = request.data.get("otp")
            customer_id = request.data.get("user_id")
            merchant_id = request.data.get("user_id")
            user_category = request.data.get("user_category", "").strip().lower()

            logger.info(f"Received OTP verification request: {request.data}")

            if not otp:
                return Response({"error": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST)

            if not user_category:
                return Response({"error": "User category is required."}, status=status.HTTP_400_BAD_REQUEST)

            if user_category == "customer" and not customer_id:
                return Response({"error": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            elif user_category == "merchant" and not merchant_id:
                return Response({"error": "Merchant ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            if user_category == "customer":
                user = Customer.objects.filter(customer_id=customer_id).first()
            elif user_category == "merchant":
                user = Merchant.objects.filter(merchant_id=merchant_id).first()

            if not user:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Log stored OTP for debugging
            logger.info(f"Stored OTP for {user_category} ({customer_id or merchant_id}): {user.otp}")
            logger.info(f"Received OTP: {otp}")

            # Check if OTP is already verified
            if user.otp is None:
                return Response({
                    "error": "OTP already verified.",
                    "status": user.status,
                    "message": "Your account is already active."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate OTP
            if str(user.otp) != str(otp):
                return Response({
                    "error": "Invalid OTP.",
                    "status": user.status,
                    "message": "Please request a new OTP."
                }, status=status.HTTP_400_BAD_REQUEST)

            # ✅ OTP is correct: Activate user
            user.verified_at = now()
            user.otp = None
            user.status = "Active"

            # ✅ Update is_profile_updated only for customers
            if user_category == "customer":
                user.is_profile_updated = True

            user.save()

            response_data = {
                "message": "User verified successfully.",
                "user_category": user_category,
                "status": "Active",
            }

            if user_category == "merchant":
                response_data["merchant_id"] = user.merchant_id
            elif user_category == "customer":
                response_data["customer_id"] = user.customer_id

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
# from .models import User
# from .serializers import UserSerializer
from .utils import send_otp_to_mobile

class RegisterUser(APIView):
    def post(self, request):
        data = request.data
        mobile_number = data.get("mobile_number")

        # Check if user already exists
        user = User.objects.filter(mobile_number=mobile_number).first()

        if user:
            user.generate_otp()
            send_otp_to_mobile(user.mobile_number, user.otp)
            request.session["mobile_number"] = user.mobile_number  # Store mobile number in session
            return Response({"message": "User already registered. OTP resent to mobile."}, status=status.HTTP_200_OK)

        # If user does not exist, create a new one
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_otp()
            send_otp_to_mobile(user.mobile_number, user.otp)
            request.session["mobile_number"] = user.mobile_number  # Store mobile number in session
            return Response({"message": "User registered successfully. OTP sent to mobile."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    def post(self, request):
        mobile_number = request.session.get("mobile_number")  # Retrieve from session
        otp = request.data.get("otp")

        if not mobile_number:
            return Response({"error": "No mobile number found. Please register first."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(mobile_number=mobile_number, otp=otp)
            user.verified_at = now()
            user.otp = None  # Clear OTP after verification
            
            user.save()
            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

class AddMerchantAPIView(APIView):
    """API to handle merchant form submission and generate corporate and project IDs"""

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = request.POST
            mobile = data.get("mobile")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            project_type = data.get("project_type")
            project_name = data.get("project_name", "")
            select_project = data.get("select_project", "")

            # Validate required fields
            if not mobile or not first_name or not last_name or not project_type:
                return JsonResponse({"error": "Missing required fields."}, status=400)

            # Generate corporate ID
            last_corporate = Merchant.objects.exclude(corporate_id=None).order_by("-corporate_id").first()
            new_corporate_id = 1 if not last_corporate else int(last_corporate.corporate_id[4:]) + 1
            corporate_id = f"CORP{new_corporate_id:06d}"

            # Determine project name and generate project ID if it's a new project
            if project_type == "Existing Project" and select_project:
                project_name = select_project
                project_id = None  # No new project ID for existing projects
            elif project_type == "New Project":
                if not project_name:
                    return JsonResponse({"error": "Project name is required for new projects."}, status=400)

                # Generate project ID
                last_project = Corporate.objects.exclude(project_id=None).order_by("-project_id").first()
                new_project_id = 1 if not last_project else int(last_project.project_id[4:]) + 1
                project_id = f"PROJ{new_project_id:06d}"
            else:
                return JsonResponse({"error": "Invalid project type."}, status=400)

            # Save merchant to the database
            merchant_data = {
                "mobile": mobile,
                "first_name": first_name,
                "last_name": last_name,
                "corporate_id": corporate_id,
                "project_name": project_name,
                "project_id": project_id,  # Include project ID if it's a new project
                # Add other fields as needed
            }
            serializer = MerchantSerializer(data=merchant_data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({
                    "message": "Merchant added successfully.",
                    "corporate_id": corporate_id,
                    "project_id": project_id
                }, status=201)
            else:
                return JsonResponse({"error": "Validation error.", "details": serializer.errors}, status=400)

        except Exception as e:
            logger.error(f"Error adding merchant: {str(e)}", exc_info=True)
            return JsonResponse({"error": "Internal Server Error"}, status=500)

class FetchAllUsersAPIView(APIView):
    """API to fetch all users or specific user types via query params"""

    def get(self, request):
        user_type = request.query_params.get('user_type')  # can be 'customer', 'merchant', 'corporate'

        all_users = []

        if user_type == 'customer' or user_type is None:
            customers = Customer.objects.all()
            customer_data = [
                {
                    # "user_type": "customer",
                    "user_id": customer.customer_id,
                    "mobile": customer.mobile,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "email": customer.email,
                    "address": customer.address,
                    "created_at": customer.created_at,
                }
                for customer in customers
            ]
            all_users += customer_data

        if user_type == 'merchant' or user_type is None:
            merchants = Merchant.objects.filter(user_type__iexact='individual')
            merchant_data = [
                {
                    # "user_type": "merchant",
                    "user_id": merchant.merchant_id,
                    "mobile": merchant.mobile,
                    "first_name": merchant.first_name,
                    "last_name": merchant.last_name,
                    "email": merchant.email,
                    "shop_name": merchant.shop_name,
                    "address": merchant.address,
                    # "corporate_id": merchant.corporate.corporate_id if merchant.corporate else None,
                    "created_at": merchant.created_at,
                }
                for merchant in merchants
            ]
            all_users += merchant_data

        if user_type == 'corporate' or user_type is None:
            merchants = Merchant.objects.filter(user_type__iexact='corporate')
            merchant_data = [
                {
                    # "user_type": "corporate",
                     "user_id": merchant.merchant_id,
                    "mobile": merchant.mobile,
                    "first_name": merchant.first_name,
                    "last_name": merchant.last_name,
                    "email": merchant.email,
                    "shop_name": merchant.shop_name,
                    "address": merchant.address,
                    "corporate_id": merchant.corporate.corporate_id if merchant.corporate else None,
                    "created_at": merchant.created_at,
                }
                for merchant in merchants
            ]
            all_users += merchant_data

        return Response({"users": all_users}, status=status.HTTP_200_OK)
    
    
    
class RequestMobileChangeAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer')
        merchant_id = request.data.get('merchant')
        new_mobile = request.data.get('new_mobile')
        pin = request.data.get('pin')
        security_question = request.data.get('security_question')
        answer = request.data.get('answer')

        if not new_mobile:
            return Response({'error': 'New mobile number is required'}, status=status.HTTP_400_BAD_REQUEST)

        new_mobile_otp = str(random.randint(100000, 999999))  # Generate OTP

        try:
            if customer_id:
                customer = Customer.objects.get(customer_id=customer_id)
                if (pin and customer.pin == int(pin)) or (
                    security_question and answer and
                    customer.security_question == security_question and customer.answer == answer
                ):
                    customer.new_mobile_otp = new_mobile_otp
                    customer.save()
                else:
                    return Response({'error': 'PIN or Security Question/Answer does not match for customer'},
                                    status=status.HTTP_400_BAD_REQUEST)

            elif merchant_id:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
                if (pin and merchant.pin == int(pin)) or (
                    security_question and answer and
                    merchant.security_question == security_question and merchant.answer == answer
                ):
                    merchant.new_mobile_otp = new_mobile_otp
                    merchant.save()
                else:
                    return Response({'error': 'PIN or Security Question/Answer does not match for merchant'},
                                    status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Either customer or merchant ID must be provided'},
                                status=status.HTTP_400_BAD_REQUEST)

        except (Customer.DoesNotExist, Merchant.DoesNotExist):
            return Response({'error': 'Invalid customer or merchant ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Send OTP via SMS
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your BOPO OTP is: {new_mobile_otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=f'+91{new_mobile}'
            )
        except Exception as e:
            return Response({'error': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'OTP sent successfully',
            'new_mobile': new_mobile,
            'otp': new_mobile_otp  # Optional: useful for debugging, hide in production
        }, status=status.HTTP_201_CREATED)



class VerifyMobileChangeAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')
        new_mobile = request.data.get('new_mobile')
        new_mobile_otp_input = request.data.get('new_mobile_otp')

        if not new_mobile or not new_mobile_otp_input:
            return Response({'error': 'new_mobile and otp are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if customer_id:
                customer = Customer.objects.get(customer_id=customer_id)
                if customer.new_mobile_otp == new_mobile_otp_input:
                    customer.mobile = new_mobile
                    customer.new_mobile_otp = None  # clear OTP
                    customer.save()
                    return Response({'message': 'Mobile number updated successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP for customer'}, status=status.HTTP_400_BAD_REQUEST)

            elif merchant_id:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
                if merchant.new_mobile_otp == new_mobile_otp_input:
                    merchant.mobile = new_mobile
                    merchant.new_mobile_otp = None  # clear OTP
                    merchant.save()
                    return Response({'message': 'Mobile number updated successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP for merchant'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'customer or merchant ID must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        except (Customer.DoesNotExist, Merchant.DoesNotExist):
            return Response({'error': 'Invalid customer or merchant ID'}, status=status.HTTP_400_BAD_REQUEST)
        

class RequestPinChangeAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')
        new_pin = request.data.get('new_pin')

        if not new_pin:
            return Response({'error': 'New PIN is required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))  # Generate OTP

        try:
            if customer_id:
                customer = Customer.objects.get(customer_id=customer_id)
                customer.pin = new_pin  # Save new pin temporarily
                customer.otp = otp
                customer.save()

                mobile_number = customer.mobile

            elif merchant_id:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
                merchant.pin = new_pin  # Save new pin temporarily
                merchant.otp = otp
                merchant.save()

                mobile_number = merchant.mobile

            else:
                return Response({'error': 'Either customer_id or merchant_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Send OTP
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your BOPO OTP to update PIN is: {otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=f'+91{mobile_number}'
            )

            return Response({'message': 'OTP sent successfully to your registered mobile.'}, status=status.HTTP_200_OK)

        except (Customer.DoesNotExist, Merchant.DoesNotExist):
            return Response({'error': 'Invalid customer or merchant ID.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class VerifyPinChangeAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')
        mobile = request.data.get('mobile')  # required mobile input
        otp = request.data.get('otp')

        if not mobile or not otp:
            return Response({'error': 'Mobile and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if customer_id:
                customer = Customer.objects.get(customer_id=customer_id)
                if customer.mobile == mobile and customer.otp == otp:
                    customer.pin = customer.pin  # save the new pin
                    customer.otp = None
                    customer.save()
                    return Response({'message': 'PIN updated successfully for customer.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP or mobile number for customer.'}, status=status.HTTP_400_BAD_REQUEST)

            elif merchant_id:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
                if merchant.mobile == mobile and merchant.otp == otp:
                    merchant.pin = merchant.pin
                    merchant.otp = None
                    merchant.save()
                    return Response({'message': 'PIN updated successfully for merchant.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP or mobile number for merchant.'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': 'Either customer_id or merchant_id must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        except (Customer.DoesNotExist, Merchant.DoesNotExist):
            return Response({'error': 'Invalid customer or merchant ID.'}, status=status.HTTP_400_BAD_REQUEST)
