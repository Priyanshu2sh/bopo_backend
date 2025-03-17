import random
from django.db import models
from django.utils.timezone import now

class Corporate(models.Model):
    """Corporate accounts that can register multiple corporate merchants"""
   
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.IntegerField(null=True, blank=True)
    pin = models.CharField(max_length=10)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.first_name


class Merchant(models.Model):
    """Merchants can be linked to a Corporate (if corporate) or independent (if individual)"""
    
    # Define choices for user types
    USER_TYPE_CHOICES = [
        ('corporate', 'Corporate'),
        ('individual', 'Individual'),
        ('customer', 'Customer'),
    ]
    
    merchant_admin = models.ForeignKey(
        Corporate,
        on_delete=models.CASCADE,
        related_name="merchants",
        null=True,
        blank=True  # If linked to a corporate, this is required
    )
    # Adding user_type with choices
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='individual'
    )
    merchant_id = models.CharField(max_length=15, unique=True, null=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.IntegerField(null=True, blank=True)
    pin = models.CharField(max_length=10)
    security_question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.first_name if self.first_name else "Merchant"


class Terminal(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="terminals")
    pin = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Terminal for {self.merchant.first_name} - {self.id}"
