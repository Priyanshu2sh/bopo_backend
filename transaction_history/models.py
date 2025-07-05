from django.db import models
from accounts.models import Customer, Merchant

class TransactionHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    customer_status = models.CharField(max_length=10)
    merchant_status = models.CharField(max_length=10)
    customer_point = models.FloatField()
    merchant_point = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def save(self, *args, **kwargs):
        # Calculate merchant_point based on customer_status and customer_point
        if self.customer_status == 'send' and self.merchant_status == 'receive':
            self.merchant_point = self.customer_point * 0.9  # Example calculation
        else:
            self.merchant_point = self.customer_point
        super().save(*args, **kwargs)
