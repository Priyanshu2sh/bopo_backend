from django.db import models
from accounts.models import Customer, Merchant  # Import Customer and Merchant

class Transfers(models.Model):
    TRANSACTION_TYPES = (
        ('redeem', 'Redeem'),
        ('award', 'Award'),
    )

    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Reference to Customer model
    merchant_id = models.ForeignKey(Merchant, on_delete=models.CASCADE)  # Reference to Merchant model
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.customer_id} → {self.merchant_id} ({self.points} points)"
    


