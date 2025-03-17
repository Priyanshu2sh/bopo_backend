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
