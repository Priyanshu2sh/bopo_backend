# awards/admin.py
# from django.contrib import admin
# from .models import TransferPoint

# admin.site.register(TransferPoint)


from django.contrib import admin
from .models import CustomerPoints, MerchantPoints

# class TransferPointAdmin(admin.ModelAdmin):
#     list_display = ('customer_id', 'merchant_id', 'points', 'transaction_type', 'created_at')
#     list_filter = ('transaction_type', 'created_at')
#     search_fields = ('customer_id', 'merchant_id')
#     ordering = ('-created_at',)  # Show latest transactions first

# admin.site.register(TransferPoint, TransferPointAdmin)


class CustomerPointsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'merchant', 'points', 'created_at')
    search_fields = ('customer__id', 'merchant__id')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

class MerchantPointsAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'points', 'created_at')
    search_fields = ('merchant__id',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(CustomerPoints, CustomerPointsAdmin)
admin.site.register(MerchantPoints, MerchantPointsAdmin)

