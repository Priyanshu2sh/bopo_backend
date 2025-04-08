from django.contrib import admin

from .models import AccountInfo, Employee, MerchantCredential, Notification, Reducelimit, Topup, BopoAdmin, UploadedFile

admin.site.register(Topup)
admin.site.register(BopoAdmin)
admin.site.register(MerchantCredential)
admin.site.register(Employee)
admin.site.register(Reducelimit)
admin.site.register(AccountInfo)
admin.site.register(UploadedFile)
admin.site.register(Notification)

