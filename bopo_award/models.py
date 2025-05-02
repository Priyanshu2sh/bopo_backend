from django.db import models
from accounts.models import Corporate, Customer, Merchant, Terminal  # Import Customer and Merchant
from django.utils.timezone import now

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
    created_at = models.DateTimeField(auto_now_add=True)

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
    

class PaymentDetails(models.Model):
    
    PLAN_CHOICES = [
        ('prepaid', 'Prepaid'),
        ('rental', 'Rental'),
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
    plan_type = models.CharField(max_length=255, null=True, blank=True, choices=PLAN_CHOICES,  help_text='Select plan type: Prepaid or Rental')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
     # Property to return the top-up value
    @property
    def topup_amount(self):
        return self.paid_amount
    
    

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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, null=True, blank=True)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Help Request - {self.customer} / {self.merchant} / {self.terminal}"
    
    
class ModelPlan(models.Model):
    # merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    plan_validity = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

class CashOut(models.Model):
    user_category = models.CharField(max_length=200, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField()
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
  


