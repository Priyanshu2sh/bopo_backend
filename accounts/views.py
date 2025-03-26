import logging
import string
from twilio.rest import Client
from django.core.mail import send_mail
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from bopo_backend import settings
from .models import Corporate, Merchant, Terminal
from .serializers import CorporateSerializer, MerchantSerializer, TerminalSerializer

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


class RegisterCorporateAPIView(APIView):
    """ API to register a Corporate account and send OTP """

    def post(self, request):
        mobile = request.data.get("mobile")

        if not mobile:
            return Response({"error": "Mobile number is required."}, status=status.HTTP_400_BAD_REQUEST)

        otp = random.randint(100000, 999999)

        try:
            corporate = Corporate.objects.get(mobile=mobile)

            if corporate.verified_at:
                return Response({"message": "Corporate is already registered and verified.", "user_id": corporate.id}, status=status.HTTP_400_BAD_REQUEST)

            corporate.otp = otp
            corporate.save()
            message = "Corporate exists but not verified. OTP resent successfully."

        except Corporate.DoesNotExist:
            serializer = CorporateSerializer(data=request.data)
            if serializer.is_valid():
                corporate = serializer.save()
                corporate.otp = otp
                corporate.save()
                message = "Corporate registered & OTP sent successfully."
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if OTPService.send_sms_otp(mobile, otp):
            return Response({"message": message, "user_id": corporate.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "OTP sending failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterMerchantAPIView(APIView):
    """ API to register a Merchant and generate Merchant ID """

    def post(self, request):
        mobile = request.data.get("mobile")
        user_type = request.data.get("user_type")
        project_name = request.data.get("project_name")  # Pass project name in request

        if not mobile:
            return Response({"error": "Mobile number is required."}, status=status.HTTP_400_BAD_REQUEST)

        if user_type not in ["corporate", "individual", "customer"]:
            return Response({"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        if not project_name or len(project_name) < 4:
            return Response({"error": "Project name must be at least 4 characters."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate Merchant ID (First 4 chars of project + 11-digit random number)
        project_abbr = project_name[:4].upper()  # Take first 4 chars and uppercase
        random_number = ''.join(random.choices(string.digits, k=11))  # Generate 11-digit number
        merchant_id = f"{project_abbr}{random_number}"  # Concatenate

        otp = random.randint(100000, 999999)

        try:
            merchant = Merchant.objects.get(mobile=mobile)

            if merchant.verified_at:
                return Response({"message": "Merchant is already registered and verified.", "merchant_id": merchant.merchant_id}, status=status.HTTP_400_BAD_REQUEST)

            merchant.otp = otp
            merchant.save()
            message = "Merchant exists but not verified. OTP resent successfully."

        except Merchant.DoesNotExist:
            # Save new merchant with generated merchant_id
            serializer = MerchantSerializer(data=request.data)
            if serializer.is_valid():
                merchant = serializer.save(merchant_id=merchant_id, otp=otp)  # Save merchant ID
                merchant.save()
                message = "Merchant registered & OTP sent successfully."
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if OTPService.send_sms_otp(mobile, otp):
            return Response({"message": message, "merchant_id": merchant.merchant_id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "OTP sending failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    """ API to register a Merchant and send OTP """

    def post(self, request):
        mobile = request.data.get("mobile")
        user_type = request.data.get("user_type")

        if not mobile:
            return Response({"error": "Mobile number is required."}, status=status.HTTP_400_BAD_REQUEST)

        if user_type not in ["corporate", "individual", "customer"]:
            return Response({"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        otp = random.randint(100000, 999999)

        try:
            merchant = Merchant.objects.get(mobile=mobile)

            if merchant.verified_at:
                return Response({"message": "Merchant is already registered and verified.", "user_id": merchant.id}, status=status.HTTP_400_BAD_REQUEST)

            merchant.otp = otp
            merchant.save()
            message = "Merchant exists but not verified. OTP resent successfully."

        except Merchant.DoesNotExist:
            serializer = MerchantSerializer(data=request.data)
            if serializer.is_valid():
                merchant = serializer.save()
                merchant.otp = otp
                merchant.save()
                message = "Merchant registered & OTP sent successfully."
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if OTPService.send_sms_otp(mobile, otp):
            return Response({"message": message, "user_id": merchant.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "OTP sending failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginAPIView(APIView):
    """ API for User login using Mobile and PIN """

    def post(self, request):
        mobile = request.data.get("mobile")
        user_type = request.data.get("user_type")  # Either 'corporate' or 'merchant'
        pin = request.data.get("pin")
        logger.info(f"Login attempt for mobile: {mobile}, type: {user_type}")

        if not mobile or not user_type or not pin:
            return Response({"error": "Mobile, Register Type, and PIN are required."}, status=status.HTTP_400_BAD_REQUEST)

        if user_type not in ["corporate", "merchant"]:
            return Response({"error": "Invalid register type. Must be 'corporate' or 'merchant'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if user_type == "corporate":
                user = Corporate.objects.get(mobile=mobile)
            else:
                user = Merchant.objects.get(mobile=mobile)

            if user.pin != pin:
                logger.warning(f"Invalid PIN for user {mobile}")
                return Response({"error": "Invalid PIN entered."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.verified_at:
                user.verified_at = now()
                user.save()

            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "user_type": user_type
            }, status=status.HTTP_200_OK)

        except (Corporate.DoesNotExist, Merchant.DoesNotExist):
            logger.warning(f"Login failed: No user found for {mobile} with type {user_type}")
            return Response({"error": "Invalid User ID or Register Type"}, status=status.HTTP_400_BAD_REQUEST)

    """ API for User login using User ID, Register Type, and PIN """

    def post(self, request):
        mobile = request.data.get("mobile")
        user_type = request.data.get("user_type")  # Either 'corporate' or 'merchant'
        pin = request.data.get("pin")

        if not mobile or not user_type or not pin:
            return Response({"error": "User ID, Register Type, and PIN are required."}, status=status.HTTP_400_BAD_REQUEST)

        if user_type not in ["corporate", "merchant"]:
            return Response({"error": "Invalid register type. Must be 'corporate' or 'merchant'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if user_type == "corporate":
                user = Corporate.objects.get(id=mobile)
            else:
                user = Merchant.objects.get(id=mobile)

            if user.pin != pin:
                return Response({"error": "Invalid PIN entered."}, status=status.HTTP_400_BAD_REQUEST)

            # Verify user if not already verified
            if not user.verified_at:
                user.verified_at = now()
                user.save()

            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "user_type": user_type
            }, status=status.HTTP_200_OK)

        except (Corporate.DoesNotExist, Merchant.DoesNotExist):
            return Response({"error": "Invalid User ID or Register Type"}, status=status.HTTP_400_BAD_REQUEST)

    """ API for Merchant or Corporate Login using ID and PIN """

    def post(self, request):
        mobile = request.data.get("mobile")
        pin = request.data.get("pin")

        if not mobile or not pin:
            return Response({"error": "User ID and PIN are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check in Corporate table
        try:
            user = Corporate.objects.get(id=mobile, pin=pin)
            user_type = "corporate"
        except Corporate.DoesNotExist:
            # Check in Merchant table
            try:
                user = Merchant.objects.get(id=mobile, pin=pin)
                user_type = "merchant"
            except Merchant.DoesNotExist:
                return Response({"error": "Invalid User ID or PIN"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify user if not already verified
        if not user.verified_at:
            user.verified_at = now()
            user.save()

        return Response({
            "message": "Login successful",
            "mobile": user.id,
            "user_type": user_type
        }, status=status.HTTP_200_OK)




class RegisterTerminalAPIView(APIView):
    """ API to register a Terminal """
    
    def post(self, request):
        serializer = TerminalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class MerchantLoginAPIView(APIView):
#     """ API for Merchant login using Merchant ID and PIN """
    
#     def post(self, request):
#         merchant_id = request.data.get('merchant_id')
#         pin = request.data.get('pin')

#         try:
#             merchant = Merchant.objects.get(id=merchant_id, pin=pin)
#         except Merchant.DoesNotExist:
#             return Response({"error": "Invalid Merchant ID or PIN"}, status=status.HTTP_400_BAD_REQUEST)

#         if not merchant.verified_at:
#             merchant.verified_at = now()
#             merchant.save()

#         return Response({"message": "Login successful", "merchant_id": merchant.id}, status=status.HTTP_200_OK)


class VerifyOTPAPIView(APIView):
    """ API to verify OTP for Corporate or Merchant """

    def post(self, request):
        user_id = request.data.get('merchant_id')
        otp = request.data.get('otp')

        if not user_id or not otp:
            return Response({"error": "User ID and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        user_type = None

        # Try to fetch user from Corporate
        try:
            user = Corporate.objects.get(id=user_id)
            user_type = "corporate"
        except Corporate.DoesNotExist:
            # Try to fetch user from Merchant if not found in Corporate
            try:
                user = Merchant.objects.get(id=user_id)
                user_type = "merchant"
            except Merchant.DoesNotExist:
                return Response({"error": "Invalid User ID or OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP
        if str(user.otp) == str(otp):
            user.verified_at = now()
            user.otp = None  # Clear OTP after successful verification
            user.save()

            response_data = {
                "message": "User verified successfully.",
                "user_id": user.id,
                "user_type": user_type,
            }

            if user_type == "merchant":
                response_data["user_id"] = user.id  # Include merchant_id for merchants

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP entered."}, status=status.HTTP_400_BAD_REQUEST)

    """ API to verify OTP for Corporate or Merchant """

    def post(self, request):
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')

        try:
            user = Corporate.objects.get(id=user_id)
        except Corporate.DoesNotExist:
            try:
                user = Merchant.objects.get(id=user_id)
            except Merchant.DoesNotExist:
                return Response({"error": "Invalid User ID or OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if str(user.otp) == str(otp):
            user.verified_at = now()
            user.otp = None
            user.save()
            return Response({"message": "User verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP entered."}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from .models import User
from .serializers import UserSerializer
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
