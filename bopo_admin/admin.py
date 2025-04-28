from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AccountInfo, BopoAdmin, Employee, EmployeeRole, MerchantCredential, Notification, Reducelimit, Topup, UploadedFile

class BopoAdminAdmin(UserAdmin):
    model = BopoAdmin
    list_display = ['username', 'role', 'corporate', 'is_staff']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('role', 'corporate', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'corporate', 'is_staff', 'is_superuser')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(BopoAdmin, BopoAdminAdmin)
admin.site.register(Topup)
admin.site.register(MerchantCredential)
admin.site.register(Employee)
admin.site.register(Reducelimit)
admin.site.register(AccountInfo)
admin.site.register(UploadedFile)
admin.site.register(Notification)
admin.site.register(EmployeeRole)


