from django.db import models
from accounts.models import Customer, Merchant  # Import the Customer and Merchant models

class CustomerToCustomer(models.Model):
    sender_customer = models.ForeignKey(Customer, related_name="sent_transfers", on_delete=models.CASCADE)
    receiver_customer = models.ForeignKey(Customer, related_name="received_transfers", on_delete=models.CASCADE)
    points = models.FloatField()
    deducted_points = models.FloatField(null=True, blank=True)  # ✅ Fix: Allow NULL values
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.deducted_points:  # ✅ Ensure deducted points are always saved
            self.deducted_points = self.points * 0.95  # Apply 5% deduction
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender_customer} → {self.receiver_customer} ({self.points} Points, Deducted: {self.deducted_points})"

class MerchantToMerchant(models.Model):
    sender_merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='sent_merchants')
    receiver_merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='received_merchants')
    points = models.PositiveIntegerField()
    deducted_points = models.PositiveIntegerField()  # Stores deducted 5% points
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_merchant} → {self.receiver_merchant} ({self.points} Points, Deducted: {self.deducted_points})"
