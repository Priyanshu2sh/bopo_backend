# bopo_admin/middleware.py


from django.shortcuts import redirect
from django.contrib.auth import logout

class CorporateStatusCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from accounts.models import Corporate

        if request.user.is_authenticated:
            user_type = request.session.get('user_type')
            if user_type == 'corporate_admin':
                try:
                    corporate = Corporate.objects.get(corporate_id=request.user.username)
                    if corporate.status == 'Inactive':
                        logout(request)
                        request.session.flush()
                        return redirect('/login/?inactive=1')  # Show custom error
                except Corporate.DoesNotExist:
                    pass
        return self.get_response(request)
