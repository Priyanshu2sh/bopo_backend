import logging
import string
from twilio.rest import Client
from django.core.mail import send_mail
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.utils.timezone import now
from bopo_backend import settings
from .models import  Customer, Merchant
from .serializers import   CustomerSerializer, MerchantSerializer

logger = logging.getLogger(__name__)

class OTPService:
    """ Helper class to handle OTP sending via Twilio """
    
    @staticmethod
    def send_sms_otp(mobile_number, otp):
        """ Sends OTP via SMS using Twilio """
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP for verification is {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=f'+91{mobile_number}'
            )
            print(f"✅ SMS sent successfully: {message.sid}")
            return True
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

        return Response({"message": message, "user_type": "customer", "customer_id": customer.customer_id},
                        status=status.HTTP_200_OK)

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
        if user_type not in ["corporate", "individual"]:
            return Response({"message": "Invalid user type.", "user_type": "merchant", "merchant_id": None},
                            status=status.HTTP_400_BAD_REQUEST)

        if not project_name or len(project_name) < 4:
            return Response({"message": "Project name must be at least 4 characters."}, status=status.HTTP_400_BAD_REQUEST)

        project_abbr = project_name[:4].upper()
        random_number = ''.join(random.choices(string.digits, k=11))
        merchant_id = f"{project_abbr}{random_number}"
        otp = random.randint(100000, 999999)

        try:
            merchant = Merchant.objects.get(mobile=mobile)
            if merchant.verified_at:
                return Response(
                    {"message": "Merchant is already registered and verified.", "user_type": "merchant",
                     "merchant_id": merchant_id},
                    status=status.HTTP_400_BAD_REQUEST
                )

            merchant.otp = otp
            merchant.save()
            message = "Merchant exists but not verified. OTP resent successfully."

        except Merchant.DoesNotExist:
            serializer = MerchantSerializer(data={**request.data, "merchant_id": merchant_id, "otp": otp})
            if serializer.is_valid():
                merchant = serializer.save()
                message = "Merchant registered & OTP sent successfully."
            else:
                return Response({"message": "Validation error", "errors": serializer.errors, "user_type": "merchant",
                                 "merchant_id": None}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": message, "user_type": "merchant", "merchant_id": merchant_id},
                        status=status.HTTP_200_OK)

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
    """API for Customer, Merchant, and Corporate Login"""

    def post(self, request):
        try:
            mobile = request.data.get("mobile")  # Used for Customers & Corporate
            merchant_id = request.data.get("merchant_id")  # Used for Merchants
            pin = request.data.get("pin")  # 🔹 Keep it as an integer

            logger.info(f"Login attempt - Mobile: {mobile}, Merchant ID: {merchant_id}")

            if pin is None:
                return Response({"error": "PIN is required."}, status=status.HTTP_400_BAD_REQUEST)

            if not mobile and not merchant_id:
                return Response({"error": "Either mobile or merchant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            user_category = None

            # ✅ Check if user is a Merchant
            if merchant_id:
                merchant = Merchant.objects.filter(merchant_id=merchant_id).first()
                if merchant:
                    logger.info(f"Merchant found: {merchant.merchant_id}")

                    # 🔹 Ensure PIN comparison is correct
                    if isinstance(merchant.pin, int):  # If PIN is stored as an integer
                        stored_pin = merchant.pin
                    else:
                        stored_pin = int(merchant.pin)  # Convert to integer if needed

                    if stored_pin == int(pin):  # ✅ Compare integer values
                        user = merchant
                        user_category = "merchant"
                    else:
                        logger.warning("Invalid PIN for merchant")

            # ✅ Check if user is a Customer
            if mobile and not user:  # Prevents checking customer if merchant is already found
                customer = Customer.objects.filter(mobile=mobile).first()
                if customer:
                    logger.info(f"Customer found: {customer.customer_id}")

                    # 🔹 Ensure PIN comparison is correct
                    if isinstance(customer.pin, int):
                        stored_pin = customer.pin
                    else:
                        stored_pin = int(customer.pin)  

                    if stored_pin == int(pin):  # ✅ Compare integer values
                        user = customer
                        user_category = "customer"
                    else:
                        logger.warning("Invalid PIN for customer")

            # ✅ Check if user is a Corporate
            # if mobile and not user:  # Prevents checking corporate if customer is already found
            #     corporate = Corporate.objects.filter(mobile=mobile).first()
            #     if corporate:
            #         logger.info(f"Corporate user found: {corporate.id}")

            #         # 🔹 Ensure PIN comparison is correct
            #         if isinstance(corporate.pin, int):
            #             stored_pin = corporate.pin
            #         else:
            #             stored_pin = int(corporate.pin)  

            #         if stored_pin == int(pin):  # ✅ Compare integer values
            #             user = corporate
            #             user_category = "corporate"
            #         else:
            #             logger.warning("Invalid PIN for corporate")

            # ❌ If no valid user found
            if not user:
                logger.warning("Invalid credentials")
                return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Prepare successful response
            response_data = {
                "message": "Login successful",
                "user_category": user_category,
            }

            # Include appropriate ID field
            if user_category == "merchant":
                response_data["merchant_id"] = user.merchant_id
            elif user_category == "customer":
                response_data["customer_id"] = user.customer_id
            # elif user_category == "corporate":
            #     response_data["corporate_id"] = user.id

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
            customer_id = request.data.get("customer_id")
            merchant_id = request.data.get("merchant_id")
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
            user.otp = None  # Clear OTP after successful verification
            user.status = "Active"
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
        


