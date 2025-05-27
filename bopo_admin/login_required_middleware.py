from django.shortcuts import redirect
from django.urls import reverse
import re

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # URLs exempted from login requirement
        exempt_urls = [
            reverse('login'),   # '/login/'
            reverse('logout'),  # '/logout/'
            reverse('forgot_password'),
            '/admin/login/',    # Django admin login URL
        ]

        # Compile regex for exempt URLs
        self.exempt_urls = [re.compile('^' + url) for url in exempt_urls]
        # Also exempt static, media, and well-known URLs
        self.exempt_urls += [
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/.well-known/'),
               ]

    def __call__(self, request):
        path = request.path_info

        if not request.user.is_authenticated:
            # If path is NOT exempt, redirect to login page
            if not any(url.match(path) for url in self.exempt_urls):
                return redirect(reverse('login'))

        response = self.get_response(request)
        return response
