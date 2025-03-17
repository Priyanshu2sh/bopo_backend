import random
from django.db import models
from django.utils.timezone import now

class User(models.Model):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    pin = models.CharField(max_length=4)  # Assuming a 4-digit PIN
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        self.otp = str(random.randint(100000, 999999))
        self.save()
