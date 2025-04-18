from django.utils import timezone  

from django.db import models, transaction

from accounts.models import Merchant
from django.contrib.auth.hashers import make_password

# Create your models here.
class BopoAdmin(models.Model):
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=128)  # longer length for hashed passwords

    def save(self, *args, **kwargs):
        # Hash the password before saving if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
    
    
  
    
class AccountInfo(models.Model):
    accountNumber = models.CharField(max_length=200, blank=True, null=True)
    payableTo = models.CharField(max_length=200, blank=True, null=True)
    bankName = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    accountType = models.CharField(max_length=200, blank=True, null=True)
    ifscCode = models.CharField(max_length=200, blank=True, null=True)
    branchName = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.bankName if self.bankName else "Account Info"
    
class Topup(models.Model):
    # STATUS_CHOICES = [
    #     # ('Bank_Transfer', 'Bank_Transfer'),
    #     # ('Cash', 'Cash'),
    #     # ('Cheque', 'Cheque'),
    #     # ('Wallet', 'Wallet'),
    #     ('Upi', 'Upi'),
    #     ('Net_Banking', 'Net_Banking'),
    #     ('credit_card', 'credit_card'),
    #     ('debit_card', 'debit_card'),

    # ]
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    topup_amount = models.IntegerField()
    transaction_id = models.CharField(max_length=100)
    topup_points = models.IntegerField()
    payment_mode = models.CharField(max_length=50)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.merchant} - {self.transaction_id}"
    
class MerchantCredential(models.Model):
    # SELECT_OPTIONS = [
    #     ('Project 1', 'Project 1'),
    #     ('Project 2', 'Project 2'),
    # ]
    # SELECT_ID = [
    #     (' M001', 'M001'),
    #     ('M002', 'M002'),
    # ]
    # SELECT_TERMINALID = [
    #     ('T001', 'T001'),
    #     ('T002', 'T002'),
    # ]
    project = models.CharField(max_length=200 ,blank=True, null=True)
    merchant_id = models.CharField(max_length=200 ,blank=True, null=True)
    merchant_name = models.CharField(max_length=200, blank=True, null=True)
    terminal_id = models.CharField(max_length=200,blank=True, null=True)


# class Employee(models.Model):
#     employee_id = models.CharField(max_length=200, blank=True, null=True)
#     employee_name = models.CharField(max_length=200, blank=True, null=True)
#     username = models.CharField(max_length=200, blank=True, null=True)
#     email = models.CharField(max_length=200, blank=True, null=True)
#     password = models.CharField(max_length=200, blank=True, null=True)
#     aadhar = models.IntegerField( blank=True, null=True)
#     address = models.CharField(max_length=200, blank=True, null=True)
#     mobile = models.CharField(max_length=200, blank=True, null=True)
#     state = models.CharField(max_length=200, blank=True, null=True)
#     pan = models.CharField(max_length=200, blank=True, null=True)
#     city = models.CharField(max_length=200, blank=True, null=True)
#     pincode = models.CharField(max_length=200, blank=True, null=True)
#     country = models.CharField(max_length=200, blank=True, null=True)

#     def __str__(self):
#         return self.employee_name
    

class Reducelimit(models.Model):
    project = models.CharField(max_length=200, blank=True, null=True)
    merchant = models.CharField(max_length=200, blank=True, null=True)
    current_limit = models.CharField(max_length=200, blank=True, null=True)
    reduce_amount = models.IntegerField( blank=True, null=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.project
    

class MerchantLogin(models.Model):
    sales_name = models.CharField(max_length=200, blank=True, null=True)
    sales_number = models.IntegerField(blank=True, null=True)
    sales_email = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.sales_name

class UploadedFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_conditions', 'Terms & Conditions'),
        ('user_guide', 'User Guide'),
    ]

    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to=' ')  # This will go to: /uploads/documents/

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} - {self.file.name}"

class Notification(models.Model):
    project_id = models.CharField(max_length=20, null=True, blank=True)
    merchant_id = models.CharField(max_length=20, null=True, blank=True)
    notification_type = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification: {self.title} ({self.project_id})"
    

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
# STATUS_CHOICES = [
#         ('Active', 'Active'),
#         ('Inactive', 'Inactive'),
#     ]
    
class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    aadhaar = models.CharField(max_length=12, unique=True)
    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10, unique=True)
    pan = models.CharField(max_length=10, unique=True)
    pincode = models.CharField(max_length=6)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    # status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Inactive', null=False, blank=False)

    def __str__(self):
        return self.name
    

class UserBalance(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    balance = models.IntegerField()

    def __str__(self):
        return f"{self.user_id} - ₹{self.balance}"







