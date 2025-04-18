from rest_framework import serializers
from .models import  Corporate, Customer,  Merchant, Terminal
from .models import User

class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = ['id', 'terminal_id', 'merchant_id', 'created_at']
        read_only_fields = ['terminal_id', 'created_at']

class CorporateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = Corporate
        fields = '__all__'
        extra_kwargs = {'otp': {'required' :False}, 'security_question': {'required' :False}, 'answer':{'required':False}, 'role':{'required':False},
                        'pin': {'required':False}, 'project_name':{'required': False}, 'select_project':{'required': False}, 'project_name':{'required':False}}


class MerchantSerializer(serializers.ModelSerializer):

    merchant_id = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True) 
    class Meta:
        model = Merchant
        fields = '__all__'
        extra_kwargs = {'project_id' :{'required':False},'age' :{'required':False}, 'aadhar_number': {'required':False}, 'pan_number': {'required':False}, 'legal_name': {'required':False},
                        'pincode': {'required':False}, 'address': {'required':False}, 'state': {'required':False}, 'country': {'required':False}, 'city': {'required':False}, 'corporate_id': {'required':False}, 
                        'shop_name':{'required':False},'gst_number':{'required':False}, 'project_name':{'required':False}}

class CustomerSerializer(serializers.ModelSerializer):
   
    customer_id = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {'age' :{'required':False}, 'aadhar_number': {'required':False}, 'pan_number': {'required':False}, 'gender':{'required':False}, 'project_name':{'required':False},
                        'pincode': {'required':False}, 'address': {'required':False}, 'select_state': {'required':False}, 'country': {'required':False},}



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'mobile_number', 'pin', 'otp', 'created_at', 'verified_at']
        read_only_fields = ['otp', 'created_at', 'verified_at']




