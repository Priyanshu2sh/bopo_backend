from django.contrib import admin

from .models import AccountInfo, BopoAdmin, DeductSetting, Employee, EmployeeRole, MerchantCredential, Notification, Reducelimit, SecurityQuestion, Topup, UploadedFile

admin.site.register(Topup)
admin.site.register(BopoAdmin)
admin.site.register(MerchantCredential)
admin.site.register(Employee)
admin.site.register(Reducelimit)
admin.site.register(AccountInfo)
admin.site.register(UploadedFile)
admin.site.register(Notification)
admin.site.register(EmployeeRole)
admin.site.register(SecurityQuestion)
admin.site.register(DeductSetting)






