import re
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # URLs exempted from login requirement (make sure these names match your urls.py)
        exempt_urls = [
            reverse('login'),                    # e.g. '/bopo_admin/login/'
            reverse('logout'),                   # e.g. '/bopo_admin/logout/'
            reverse('forgot_password'),          # e.g. '/bopo_admin/forgot-password/'
            reverse('password_reset_done'),      # e.g. '/bopo_admin/forgot-password/done/'
            reverse('password_reset_complete'),  # e.g. '/bopo_admin/reset/done/'
            '/admin/login/',                     # Django admin login
            '/favicon.ico',                      # Favicon requests
        ]

        # Compile regex for exempt URLs, exact match with trailing slash
        self.exempt_urls = [re.compile(r'^{}$'.format(url)) for url in exempt_urls]

        # Also exempt static, media, well-known URLs, and reset URLs with dynamic parts
        self.exempt_urls += [
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/.well-known/'),
            re.compile(r'^/bopo_admin/reset/.+/.+/'),  # Your reset URLs pattern with prefix
        ]

    def __call__(self, request):
        path = request.path_info

        print(f"[Middleware] Checking path: {path}")  # Debug

        if not request.user.is_authenticated:
            # If path is NOT exempt, redirect to login page
            if not any(url.match(path) for url in self.exempt_urls):
                print(f"[Middleware] Redirecting to login")  # Debug
                return redirect(reverse('login'))

            else:
                print(f"[Middleware] Exempted: {path}")  # Debug

        response = self.get_response(request)
        return response
