from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Merchant)
admin.site.register(Customer)
admin.site.register(Corporate)

class TerminalAdmin(admin.ModelAdmin):
    list_display = ('terminal_id', 'tid_pin', 'merchant_id', 'is_admin', 'is_login', 'status', 'created_at')
    search_fields = ('terminal_id', 'status')
  
admin.site.register(Terminal, TerminalAdmin)

admin.site.register(Logo)
