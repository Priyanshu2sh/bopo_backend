import random
from django.db import models
from django.utils.timezone import now

from django.contrib.auth import get_user_model

User = get_user_model()  


# class Corporate(models.Model):
#     """Corporate accounts that can register multiple corporate merchants"""
   
#     corporate_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
#     first_name = models.CharField(max_length=255, null=True, blank=True)
#     last_name = models.CharField(max_length=255, null=True, blank=True)
#     email = models.EmailField(unique=True, null=True, blank=True)
#     mobile = models.CharField(max_length=15, unique=True)
#     otp = models.IntegerField(null=True, blank=True)
#     pin = models.CharField(max_length=10)
#     security_question = models.CharField(max_length=255, null=True, blank=True)
#     answer = models.CharField(max_length=255, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     verified_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.first_name


class Merchant(models.Model):
    """Merchants can be linked to a Corporate (if corporate) or independent (if individual)"""
    
    # Define choices for user types
    USER_TYPE_CHOICES = [
        # ('corporate', 'Corporate'),
        ('individual', 'Individual'),
        ('customer', 'Customer'),
    ]

    # STATUS_CHOICES = [
    #     ('Active', 'Active'),
    #     ('Inactive', 'Inactive'),
    # ]
    
    # merchant_admin = models.ForeignKey(
    #     Corporate,
    #     on_delete=models.CASCADE,
    #     related_name="merchants",
    #     null=True,
    #     blank=True  # If linked to a corporate, this is required
    # )
    # Adding user_type with choices
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='individual'
    )
    merchant_id = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.IntegerField(null=True, blank=True)
    pin = models.IntegerField( blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gst = models.CharField(max_length=255, blank=True, null=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    register_shop_name = models.CharField(max_length=250, null=True, blank=True)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Inactive')
    pincode = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    select_state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
     
    # New fields added
    aadhaar_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True, unique=False) 
    pan_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.first_name if self.first_name else "Merchant"
    


class Customer(models.Model):
    customer_id = models.CharField(max_length=25, primary_key=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    age = models.IntegerField(null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True)
    pin = models.IntegerField(blank=True, null=True)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    aadhar_number = models.CharField(max_length=255, null=True, blank=True)
    pan = models.CharField(max_length=255, blank=True, null=True)
    # gst = models.CharField(max_length=255, blank=True, null=True)
    # legal_name = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    select_state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    # shop_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.first_name if self.first_name else "Customer"