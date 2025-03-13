from rest_framework import serializers
from .models import User
from django.utils.timezone import now

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'mobile_number', 'pin', 'created_at', 'verified_at']
        extra_kwargs = {'pin': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.generate_otp()  # Generate OTP after user registration
        return user


# class OTPVerifySerializer(serializers.Serializer):
#     mobile_number = serializers.CharField()
#     otp = serializers.CharField()

#     def validate(self, data):
#         mobile_number = data.get("mobile_number")
#         otp = data.get("otp")

#         try:
#             user = User.objects.get(mobile_number=mobile_number)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Mobile number not found.")

#         # Check if OTP matches
#         if user.otp != otp:
#             raise serializers.ValidationError("Invalid OTP.")

#         # Mark user as verified and clear OTP
#         user.verified_at = now()
#         user.otp = None  # Clear OTP after successful verification
#         user.save()

#         return {"message": "OTP Verified Successfully"}
class OTPVerifySerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(mobile_number=data['mobile_number'])
            print(f"Stored OTP: {user.otp}, Entered OTP: {data['otp']}")  # Debugging
            if user.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid mobile number.")

        user.verified_at = now()  # Mark as verified
        user.otp = None  # Clear OTP after successful verification
        user.save()
        return {"message": "OTP Verified Successfully"}
