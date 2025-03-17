from rest_framework import serializers
from .models import Project, Merchant

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = '__all__'

    def validate_mobile_number(self, value):
        """Ensure mobile number has 10 digits"""
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value