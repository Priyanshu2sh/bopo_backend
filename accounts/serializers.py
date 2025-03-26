from rest_framework import serializers
from .models import Corporate, Merchant, Terminal

class CorporateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = Corporate
        fields = '__all__'


class MerchantSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = Merchant
        fields = '__all__'

class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'

    def validate(self, data):
        """
        Validate merchant_admin relationship:
        - If merchant is corporate, it should be linked to a Corporate
        - If merchant is individual, merchant_admin should be null
        """
        merchant_admin = data.get("merchant_admin")

        if merchant_admin is not None and not Corporate.objects.filter(id=merchant_admin.id).exists():
            raise serializers.ValidationError({"merchant_admin": "Corporate does not exist."})

        return data
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'mobile_number', 'pin', 'otp', 'created_at', 'verified_at']
        read_only_fields = ['otp', 'created_at', 'verified_at']
