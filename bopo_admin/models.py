from django.utils import timezone  

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password


# Create your models here.
class BopoAdminManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # handles hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class BopoAdmin(AbstractBaseUser, PermissionsMixin):
    USER_ROLES = (
        ('super_admin', 'Super Admin'),
        ('corporate_admin', 'Corporate Admin'),
        ('employee', 'Employee'),
    )

    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=USER_ROLES)  # <- Add this field
    employee = models.ForeignKey('bopo_admin.Employee', on_delete=models.CASCADE, null=True, blank=True)
    corporate = models.ForeignKey('accounts.Corporate', on_delete=models.CASCADE, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = BopoAdminManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

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
    merchant = models.ForeignKey('accounts.Merchant', on_delete=models.CASCADE)
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
    file = models.FileField(upload_to='uploads/documents/')


    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} - {self.file.name}"

class Notification(models.Model):
    project_id = models.CharField(max_length=20, null=True, blank=True)
    merchant_id = models.CharField(max_length=20, null=True, blank=True)
    customer_id = models.CharField(max_length=20, null=True, blank=True)
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
    employee_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    aadhaar = models.CharField(max_length=12, unique=True)
    address = models.TextField()
    role = models.CharField(max_length=20, default='employee')
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
    
class EmployeeRole(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    corporate_merchant = models.BooleanField(default=False)
    individual_merchant = models.BooleanField(default=False)
    merchant_send_credentials = models.BooleanField(default=False)
    merchant_limit = models.BooleanField(default=False)
    merchant_login_page_info = models.BooleanField(default=False)
    merchant_send_notification = models.BooleanField(default=False)
    merchant_received_offers = models.BooleanField(default=False)
    modify_customer_details = models.BooleanField(default=False)
    customer_send_notification = models.BooleanField(default=False)
    create_employee = models.BooleanField(default=False)
    payment_details = models.BooleanField(default=False)
    account_info = models.BooleanField(default=False)
    reports = models.BooleanField(default=False)
    deduct_amount = models.BooleanField(default=False)
    helpdesk_action = models.BooleanField(default=False)

    def __str__(self):
        return f"Roles for {self.employee.employee_id}"
    

class UserBalance(models.Model):

    deduction_amount = models.FloatField(default=0.0)  # Default to 5%
    
class SecurityQuestion(models.Model):
    question = models.CharField(max_length=255)
    ans = models.CharField(max_length=200)
    is_taken = models.BooleanField(default=False)  # Add the is_taken field

    def __str__(self):
        return self.question


class DeductSetting(models.Model):
    # deduct_percentage = models.FloatField(default=5.0)  # Default 5% if not set
    cust_merch = models.FloatField(default=5.0, null=True, blank=True)  
    # merch_cust = models.FloatField(default=5.0, null=True, blank=True)
    merch_merch = models.FloatField(default=5.0, null=True, blank=True)
    cust_cust = models.FloatField(default=5.0, null=True, blank=True)
    normal_global = models.FloatField(default=5.0, null=True, blank=True)
    # expire_cust_global = models.FloatField(default=5.0, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f"Deduct {self.deduct_percentage}%"


    







