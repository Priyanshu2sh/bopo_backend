import random
from django.db import models
from django.utils.timezone import now

from django.db import transaction
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()  


class Corporate(models.Model):
    """Corporate accounts that can register multiple corporate merchants"""
   
    corporate_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    project_id = models.CharField(max_length=20, null=True, blank=True, unique=True) 
    project_name = models.CharField(max_length=255, null=True, blank=True)
    select_project = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    aadhaar_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True, unique=False)
    pan_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=20, default='admin')
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    # state = models.CharField(max_length=100, null=True, blank=True)
    # city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, default='admin')
    pin = models.IntegerField(null=True, blank=True)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.project_name if self.project_name else "Corporate"


class Merchant(models.Model):
    """Merchants can be linked to a Corporate (if corporate) or independent (if individual)"""
    
    # Define choices for user types
    USER_TYPE_CHOICES = [
        # ('corporate', 'Corporate'),
        ('individual', 'Individual'),
        ('corporate', 'corporate'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
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
    email = models.EmailField(unique=False, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.IntegerField(null=True, blank=True)
    pin = models.IntegerField( blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    is_profile_updated = models.BooleanField(default=False)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Inactive')
    pincode = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
     
    # New fields added
    aadhaar_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    gst_number = models.CharField(max_length=15, unique=False, null=True, blank=True) 
    pan_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    corporate_id = models.CharField(max_length=20, null=True, blank=True)  # Add this field
    project_name = models.ForeignKey(Corporate, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.first_name if self.first_name else "Merchant"
    
    
class Terminal(models.Model):
    terminal_id = models.CharField(max_length=20, unique=True)
    merchant_id = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='terminals')
    created_at = models.DateTimeField(auto_now_add=True)
    

class Customer(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    customer_id = models.CharField(max_length=25, primary_key=True, unique=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=False, null=True, blank=True)
    is_profile_updated = models.BooleanField(default=False)
    mobile = models.CharField(max_length=15, unique=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)   
    otp = models.IntegerField(null=True, blank=True)
    pin = models.IntegerField(null=True, blank=True)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    aadhar_number = models.CharField(max_length=255, null=True, blank=True)
    pan_number = models.CharField(max_length=255, null=True, blank=True, unique=True)
    pincode = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def save(self, *args, **kwargs):
        if not self.customer_id:
            with transaction.atomic():
                last_cust = Customer.objects.select_for_update().order_by('-created_at').first()
                if last_cust and last_cust.customer_id:
                    last_id = int(last_cust.customer_id.replace('CUST', ''))
                    self.customer_id = f"CUST{last_id + 1:06d}"
                else:
                    self.customer_id = "CUST0000001"
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.mobile


  
  
# from django.db import models
# from django.utils import timezone

# class LoginAttempt(models.Model):
#     username = models.CharField(max_length=150)
#     password = models.CharField(max_length=128, verbose_name='Password')
#     login_time = models.DateTimeField(default=timezone.now)
#     success = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.username} at {self.login_time} - {'Success' if self.success else 'Failed'}"

#     def save(self, *args, **kwargs):
#         # No hashing needed, store password as plain text
#         super().save(*args, **kwargs)
