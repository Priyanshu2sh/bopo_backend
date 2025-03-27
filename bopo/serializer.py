from rest_framework import serializers
from .models import CustomerToCustomer, MerchantToMerchant

class CustomerToCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerToCustomer
        fields = '__all__'

    def create(self, validated_data):
        points = validated_data.get('points')
        deducted_points = int(points * 0.05)  # 5% deduction
        validated_data['deducted_points'] = deducted_points
        return super().create(validated_data)

class MerchantToMerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantToMerchant
        fields = '__all__'

    def create(self, validated_data):
        points = validated_data.get('points')
        deducted_points = int(points * 0.05)  # 5% deduction
        validated_data['deducted_points'] = deducted_points
        return super().create(validated_data)
