import random
from django.db import models
from django.utils.timezone import now

from django.db import transaction
from django.contrib.auth import get_user_model
from django.db import transaction

from bopo_admin.models import BopoAdmin, SecurityQuestion



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
    pin = models.IntegerField(null=True, blank=True)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    logo = models.ForeignKey('Logo', on_delete=models.SET_NULL, null=True, blank=True, related_name='corporates')
    account_type = models.CharField(max_length=20, choices=[('global', 'Global'), ('normal', 'Normal')], default='normal')


    
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

    REFERENCE_CHOICES = [
        ('Sales', 'Sales'),
        ('Social Media', 'Social Media'),
        ('News Paper', 'News Paper'),
        ('Other', 'Other'),
    ]
    
    # PLAN_CHOICES = [
    #     ('prepaid', 'Prepaid'),
    #     ('rental', 'Rental'),
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
    
    
    
    merchant_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    PLAN_CHOICES = [
        ('prepaid', 'Prepaid'),
        ('rental', 'Rental'),
    ]
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='prepaid')
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=False, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.IntegerField(null=True, blank=True)
    new_mobile_otp = models.IntegerField(null=True, blank=True)
    pin = models.IntegerField(unique=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    reference = models.CharField(max_length=200, choices=REFERENCE_CHOICES, null=True, blank=True)
    employee_id = models.ForeignKey('bopo_admin.Employee', to_field='employee_id', on_delete=models.CASCADE, null=True, blank=True)
    # plan_type = models.CharField(max_length=255, null=True, blank=True, choices=PLAN_CHOICES,  help_text='Select plan type: Prepaid or Rental')
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    shop_name = models.CharField(max_length=255, null=True, blank=True)
    is_profile_updated = models.BooleanField(default=False)
    security_question_fk = models.ForeignKey(SecurityQuestion, on_delete=models.SET_NULL, null=True, blank=True, related_name='merchants')
    answer = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Active')
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
    logo = models.ForeignKey('Logo', on_delete=models.SET_NULL, null=True, blank=True, related_name='merchants')

  
    def save(self, *args, **kwargs):
        if self.security_question_fk:
            self.security_question_fk.is_taken = True
            self.security_question_fk.save()
        super(Merchant, self).save(*args, **kwargs)


    def __str__(self):
        return self.first_name if self.first_name else "Merchant"
    
    
class Terminal(models.Model):
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
     
    terminal_id = models.CharField(max_length=20, unique=True)
    tid_pin = models.IntegerField(unique=True)
    merchant_id = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='terminals')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Active')
    
   

class Customer(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
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
    new_mobile_otp = models.IntegerField(null=True, blank=True)
    pin = models.IntegerField(null=True, blank=True)
    security_question_fk = models.ForeignKey(SecurityQuestion, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers') 
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    logo = models.ForeignKey('Logo', on_delete=models.SET_NULL, null=True, blank=True, related_name='customer')

    def save(self, *args, **kwargs):
        # Generate customer ID if not already set
        if not self.customer_id:
            with transaction.atomic():
                last_cust = Customer.objects.select_for_update().order_by('-created_at').first()
                if last_cust and last_cust.customer_id:
                    try:
                        last_id = int(last_cust.customer_id.replace('CUST', ''))
                    except ValueError:
                        last_id = 0
                    self.customer_id = f"CUST{last_id + 1:06d}"
                else:
                    self.customer_id = "CUST0000001"

        # Mark security question as taken
        if self.security_question_fk:
            self.security_question_fk.is_taken = True
            self.security_question_fk.save()

        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.mobile
    
class SecurityQue(models.Model):
    security_question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return self.security_question

  


class Logo(models.Model):
    logo = models.ImageField(upload_to='logos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Logo {self.id}"



