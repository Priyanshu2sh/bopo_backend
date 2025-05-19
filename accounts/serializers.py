from rest_framework import serializers
from .models import  Corporate, Customer, Logo,  Merchant, Terminal
from .models import User
import base64
import uuid
from django.core.files.base import ContentFile

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
        extra_kwargs = {'otp': {'required' :False},'is_profile_updated':{'required' : False}, 'security_question': {'required' :False}, 'answer':{'required':False}, 'role':{'required':False},
                        'pin': {'required':False}, 'project_name':{'required': False}, 'select_project':{'required': False}, 'project_name':{'required':False}}

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  # format: data:image/png
            ext = format.split('/')[-1]
            file_name = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=file_name)
        return super().to_internal_value(data)

class MerchantSerializer(serializers.ModelSerializer):

    merchant_id = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True) 
    logo_data = Base64ImageField(required=False)  # ✅ Allow read and write
    logo = serializers.SerializerMethodField()     # ✅ Returns base64 in response
    class Meta:
        model = Merchant
        fields = '__all__'
        extra_kwargs = {'project_id' :{'required':False},'age' :{'required':False}, 'aadhar_number': {'required':False}, 'pan_number': {'required':False}, 'legal_name': {'required':False}, 'gender':{'required':False}, 'project_name':{'required':False},
                        'pincode': {'required':False}, 'is_profile_updated':{'required' : False}, 'address': {'required':False}, 'state': {'required':False}, 'country': {'required':False}, 'city': {'required':False}, 'corporate_id': {'required':False}, 
                        'shop_name':{'required':False}, 'plan-type':{'required': False}, 'gst_number':{'required':False}, 'project_name':{'required':False}, 'employee_id':{'required':False} }

    def get_logo(self, obj):
        """
        Return base64-encoded image for the logo field in the response.
        """
        if obj.logo and obj.logo.logo:
            try:
                with obj.logo.logo.open('rb') as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except Exception:
                return None
        return None

    def create(self, validated_data):
        logo_data = validated_data.pop('logo_data', None)
        if logo_data:
            logo_instance = Logo.objects.create(logo=logo_data)
            validated_data['logo'] = logo_instance
        return super().create(validated_data)

    def update(self, instance, validated_data):
        logo_data = validated_data.pop('logo_data', None)
        if logo_data:
            logo_instance = Logo.objects.create(logo=logo_data)
            validated_data['logo'] = logo_instance
        return super().update(instance, validated_data)
    

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

# class ChangeMobileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChangeMobile
#         fields = ['customer', 'merchant', 'new_mobile', 'new_mobile_otp', 'created_at', 'verified_at']
#         read_only_fields = ['otp', 'created_at', 'verified_at']
#         extra_kwargs = {
#             'customer': {'required': False, 'allow_null': True},
#             'merchant': {'required': False, 'allow_null': True}
#         }



