# from rest_framework import serializers
# from .models import TransferPoint

# class TransferPointSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TransferPoint
#         fields = ['customer_id', 'merchant_id', 'points', 'transaction_type', 'created_at']

#     def validate(self, data):
#         if data['transaction_type'] not in ['redeem', 'award']:
#             raise serializers.ValidationError("Invalid transaction type.")
#         return data

from rest_framework import serializers


from accounts.models import Customer, Merchant
from .models import BankDetail, CustomerPoints, MerchantPoints, History, PaymentDetails


class CustomerPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPoints
        fields = '__all__'

class MerchantPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantPoints
        fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction History API
    """

    class Meta:
        model = History
        fields = ['customer_id', 'merchant_id', 'points', 'transaction_type', 'created_at']


class PaymentDetailsSerializer(serializers.ModelSerializer):
    merchant = serializers.SlugRelatedField(
        queryset=Merchant.objects.all(),
        slug_field='merchant_id'  # Use your unique merchant code field
    )
    class Meta:
        model = PaymentDetails
        fields = ['merchant', 'paid_amount', 'transaction_id','topup_point', 'payment_mode', 'created_at']
        extra_kwargs = {'topup_point' :{'required':False}}

class BankDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Bank Details API
    
    """
    class Meta:
        model = BankDetail
        fields = ['account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'branch', 'created_at']
        extra_kwargs = {'account_holder_name': {'required': False}}
