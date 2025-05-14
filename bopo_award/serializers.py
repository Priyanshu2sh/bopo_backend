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
from .models import BankDetail, CashOut, CustomerPoints, GlobalPoints, Help, MerchantPoints, History, ModelPlan, PaymentDetails, SuperAdminPayment
from .models import BankDetail, CashOut, CustomerPoints, Help, MerchantPoints, History, PaymentDetails, SuperAdminPayment


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
        fields = ['merchant', 'paid_amount', 'transaction_id', 'payment_mode', 'plan_type', 'created_at']
        

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
        
        
class CashOutSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(required=False, allow_null=True)
    merchant_id = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CashOut
        fields = ['id', 'user_category', 'customer_id', 'merchant_id', 'amount', 'created_at']
        # read_only_fields = ['id', 'created_at']

    def validate_customer_id(self, value):
        if value:
            try:
                customer = Customer.objects.get(customer_id=value)
                return customer
            except Customer.DoesNotExist:
                raise serializers.ValidationError("Invalid customer_id")
        return None

    def validate_merchant_id(self, value):
        if value:
            try:
                merchant = Merchant.objects.get(merchant_id=value)
                return merchant
            except Merchant.DoesNotExist:
                raise serializers.ValidationError("Invalid merchant_id")
        return None
    
class CustomerCashOutSerializer(serializers.Serializer):
    customer_id = serializers.CharField()
    merchant_id = serializers.CharField()
    amount = serializers.IntegerField()

class MerchantCashOutSerializer(serializers.Serializer):
    merchant_id = serializers.CharField()
    amount = serializers.IntegerField()
    
class SuperAdminPaymentSerializer(serializers.Serializer):
    """
    Serializer for Super Admin Payment API
    """
    class Meta:
        model = SuperAdminPayment
        fields = ['transaction_id', 'payment_method', 'cashout', 'created_at']
        
class GlobalPointsSerializer(serializers.Serializer):
    """
    Serializer for Global Points API
    """
    class Meta:
        model = GlobalPoints
        fields = '__all__'