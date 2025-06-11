import re
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Literal paths or path patterns
        self.exempt_urls = [
            re.compile(r'^/api/'),  # ✅ Exempt all API routes
            re.compile(r'^/bopo_admin/login/$'),
            re.compile(r'^/bopo_admin/logout/$'),
            re.compile(r'^/bopo_admin/forgot-password/$'),
            re.compile(r'^/bopo_admin/forgot-password/done/$'),
            re.compile(r'^/bopo_admin/reset/done/$'),
            re.compile(r'^/admin/login/'),
            re.compile(r'^/favicon.ico$'),
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/.well-known/'),
            re.compile(r'^/bopo_admin/reset/.+/.+/'),
        ]

    def __call__(self, request):
        path = request.path_info
        print(f"[Middleware] Checking path: {path}")

        # Skip auth check for exempt URLs
        if any(pattern.match(path) for pattern in self.exempt_urls):
            print(f"[Middleware] Exempted: {path}")
            return self.get_response(request)

        if not request.user.is_authenticated:
            print(f"[Middleware] Redirecting to login")
            return redirect('/bopo_admin/login/')  # Avoid using reverse() here if route not named

        return self.get_response(request)
