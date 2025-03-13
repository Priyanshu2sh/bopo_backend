from django.db import models

# Create your models here.
import random
from django.db import models
from django.utils.timezone import now

class User(models.Model):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    pin = models.CharField(max_length=6)
    otp = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        self.otp = str(random.randint(100000, 999999))
        self.save()
