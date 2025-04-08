from django.db import models
from accounts.models import Customer, Merchant  # Import Customer and Merchant
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'merchant')  # Ensures unique customer-merchant pair

class MerchantPoints(models.Model):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE)
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