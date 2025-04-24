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


from accounts.models import Corporate, Customer, Merchant
from bopo_admin.models import EmployeeRole
from .models import BankDetail, CustomerPoints, Help, MerchantPoints, History, PaymentDetails


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
        fields = ['merchant', 'paid_amount', 'transaction_id', 'payment_mode', 'created_at']
        

class BankDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Bank Details API
    
    """
    class Meta:
        model = BankDetail
        fields = ['merchant','customer', 'account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'branch', 'created_at']
        extra_kwargs = {'account_holder_name': {'required': False}}


class HelpSerializer(serializers.ModelSerializer):
    """
    Serializer for Help API
    """
    class Meta:
        model = Help
        fields = ['customer', 'merchant', 'issue_description', 'created_at']
        extra_kwargs = {'customer':{'required': False}, 'merchant':{'required': False}}


class CorporateProjectSerializer(serializers.ModelSerializer):
    """
    Serializer to return only project_name from Corporate
    """
    class Meta:
        model = Corporate
        fields = ['project_name']

class EmployeeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRole
        fields = '__all__'