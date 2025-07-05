from django.contrib import admin
from .models import *
# Register your models here.
# admin.site.register(CustomerPoints)
# admin.site.register(MerchantPoints)
admin.site.register(CustomerToCustomer),
admin.site.register(MerchantToMerchant)

