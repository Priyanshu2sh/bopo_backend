from django.db import models
from django.forms import ValidationError
from accounts.models import Corporate, Customer, Merchant, Terminal  # Import Customer and Merchant
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from datetime import timedelta, date

# class TransferPoint(models.Model):
#     TRANSACTION_TYPES = (
#         ('redeem', 'Redeem'),
#         ('award', 'Award'),
#     )

#     customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Reference to Customer model
#     merchant_id = models.ForeignKey(Merchant, on_delete=models.CASCADE)  # Reference to Merchant model
#     points = models.PositiveIntegerField()
#     transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.transaction_type}: {self.customer_id} → {self.merchant_id} ({self.points} points)"
    
class CustomerPoints(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    points = models.IntegerField()
    corporate_id = models.ForeignKey(Corporate, on_delete=models.CASCADE, null=True, blank=True)  # Reference to Corporate model
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'merchant')  # Ensures unique customer-merchant pair

class MerchantPoints(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)



class History(models.Model):
    TRANSACTION_TYPES = (
        ('redeem', 'Redeem'),
        ('award', 'Award'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.transaction_type} - {self.points} points"
    

class CustomerToCustomer(models.Model):
    sender_customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name="sent_transfers_award"  # <-- Change related_name
    )
    receiver_customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name="received_transfers_award"  # <-- Change related_name
    )
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    points = models.IntegerField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.sender_customer.customer_id} -> {self.receiver_customer.customer_id}: {self.points} Points"
    

class MerchantToMerchant(models.Model):
    sender_merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="sent_transfers")
    receiver_merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="received_transfers")
    points = models.IntegerField()
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('sender_merchant', 'receiver_merchant')  # Ensures unique sender-receiver pair

    def __str__(self):
        return f"{self.sender_merchant.merchant_id} -> {self.receiver_merchant.merchant_id}: {self.points} points"
    
    
class GlobalPoints(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    points = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    
    
    

class PaymentDetails(models.Model):
    
    # PLAN_CHOICES = [
    #     ('prepaid', 'Prepaid'),
    #     ('rental', 'Rental'),
    # ] 
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    paid_amount = models.IntegerField()
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_mode = models.CharField(max_length=255, choices=[
        ('UPI', 'UPI'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Net Banking', 'Net Banking'),
    ])
    plan_type = models.ForeignKey('bopo_award.ModelPlan', on_delete=models.SET_NULL, null=True, blank=True)
     
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, null=True, blank=True, choices=STATUS_CHOICES)
    validity_days = models.PositiveIntegerField(null=True, blank=True, help_text="Validity in days (for rental plans)")
    expiry_date = models.DateField(null=True, blank=True, editable=False)
    
    def clean(self):
        existing = PaymentDetails.objects.filter(merchant=self.merchant).exclude(id=self.id)
        if existing.exists():
            existing_plan = existing.first().plan_type
            if existing_plan != self.plan_type:
                raise ValidationError(f"This merchant already has a '{existing_plan}' plan. Duplicate plan types are not allowed.")

    def save(self, *args, **kwargs):
        self.clean()  # Run the validation
    
     # Property to return the top-up value
    @property
    def topup_amount(self):
        return self.paid_amount
    
    def save(self, *args, **kwargs):
        if self.plan_type == 'rental' and self.validity_days:
            self.expiry_date = date.today() + timedelta(days=self.validity_days)
        elif self.plan_type == 'prepaid':
            self.validity_days = 360  # Prepaid plans always have 360 days validity
            self.expiry_date = date.today() + timedelta(days=self.validity_days)
        else:
            self.expiry_date = None  # Clear expiry if not rental or prepaid
        super().save(*args, **kwargs)
    
    

class BankDetail(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255, unique=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    branch = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    

class Help(models.Model):
    STATUS_CHOICES = [
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, null=True, blank=True)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, null=True, blank=True, choices=STATUS_CHOICES,  default='pending' )
    

    def __str__(self):
        return f"Help Request - {self.customer} / {self.merchant} / {self.terminal}"
    
    
class ModelPlan(models.Model):
    
    plan_validity = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.plan_type} - {self.id} "
    

class CashOut(models.Model):
    user_category = models.CharField(max_length=200, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField()
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
 

class AwardPoints(models.Model):
    percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.percentage}% of purchase amount awarded to customer"
    


class SuperAdminPayment(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50)
    cashout = models.ForeignKey(CashOut, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

