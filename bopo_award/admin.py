# awards/admin.py
# from django.contrib import admin
# from .models import TransferPoint

# admin.site.register(TransferPoint)


from django.contrib import admin
from .models import TransferPoint

class TransferPointAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'merchant_id', 'points', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('customer_id', 'merchant_id')
    ordering = ('-created_at',)  # Show latest transactions first

admin.site.register(TransferPoint, TransferPointAdmin)


