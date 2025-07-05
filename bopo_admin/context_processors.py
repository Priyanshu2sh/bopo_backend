from .models import EmployeeRole

def employee_permissions(request):
    if request.user.is_authenticated and hasattr(request.user, 'employee'):
        try:
            role_permissions = EmployeeRole.objects.get(employee=request.user.employee)
            merchant = any([
                role_permissions.corporate_merchant,
                role_permissions.individual_merchant,
                role_permissions.merchant_send_credentials,
                role_permissions.merchant_limit,
                role_permissions.merchant_login_page_info,
                role_permissions.merchant_send_notification,
                role_permissions.merchant_received_offers,
            ])
            return {
                'role_permissions': role_permissions,
                'merchant': merchant,
            }
        except EmployeeRole.DoesNotExist:
            pass
    return {}
