from rest_framework import serializers
from .models import  Customer,  Merchant
from .models import User

# class CorporateSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
#     class Meta:
#         model = Corporate
#         fields = '__all__'


class MerchantSerializer(serializers.ModelSerializer):

    merchant_id = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = Merchant
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
   
   customer_id = serializers.CharField()
   email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
   class Meta:
       model = Customer
       fields = '__all__'
       extra_kwargs = {'age' :{'required':False}, 'aadhar_number': {'required':False}, 'pan': {'required':False}, 'gst': {'required':False},
                       'legal_name': {'required':False}, 'pincode': {'required':False}, 'address': {'required':False}, 'select_state': {'required':False}, 'country': {'required':False},
                       'shop_name': {'required':False},}



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'mobile_number', 'pin', 'otp', 'created_at', 'verified_at']
        read_only_fields = ['otp', 'created_at', 'verified_at']




