# awards/admin.py
# from django.contrib import admin
# from .models import TransferPoint

# admin.site.register(TransferPoint)


from django.contrib import admin


from .models import AwardPoints, BankDetail, CashOut, CustomerPoints, CustomerToCustomer, GlobalPoints, Help, History, MerchantPoints, MerchantToMerchant, ModelPlan, PaymentDetails, SuperAdminPayment

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

class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'paid_amount', 'transaction_id',  'payment_mode', 'created_at')
    search_fields = ('transaction_id', 'merchant__id')  # or 'merchant__name' if available
    list_filter = ('payment_mode', 'created_at')
    ordering = ('-created_at',)

admin.site.register(PaymentDetails, PaymentDetailsAdmin)

class BankDetailAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'customer', 'account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'branch', 'created_at')
    search_fields = ('merchant__id', 'customer__id', 'account_holder_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
admin.site.register(BankDetail, BankDetailAdmin)

class CustomerToCustomerAdmin(admin.ModelAdmin):
    list_display = ('sender_customer', 'receiver_customer', 'merchant', 'points', 'created_at')
    search_fields = ('sender_customer', 'receiver_customer')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
admin.site.register(CustomerToCustomer, CustomerToCustomerAdmin)

class MerchantToMerchantAdmin(admin.ModelAdmin):
    list_display = ('sender_merchant', 'receiver_merchant', 'points', 'created_at')
    search_fields = ('sender_merchant', 'receiver_merchants')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
admin.site.register(MerchantToMerchant, MerchantToMerchantAdmin)

admin.site.register(Help)
admin.site.register(History)
admin.site.register(ModelPlan)
admin.site.register(CashOut)
admin.site.register(AwardPoints)

class GlobalPointsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points')
admin.site.register(GlobalPoints, GlobalPointsAdmin)

admin.site.register(SuperAdminPayment)



