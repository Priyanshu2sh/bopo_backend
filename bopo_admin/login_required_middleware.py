import re
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        exempt_paths = [
            '/portal/login/',
            '/portal/logout/',
            '/portal/forgot-password/',
            '/portal/forgot-password/done/',
            '/portal/reset/done/',
            '/portal/reset/invalid/',
            '/admin/login/',
            '/favicon.ico',
        ]

        # Match paths with or without trailing slashes
        self.exempt_urls = [re.compile(r'^{}[/]?$'.format(re.escape(path))) for path in exempt_paths]

        self.exempt_urls += [
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/.well-known/'),
            re.compile(r'^/portal/reset/.+/.+/'),
            re.compile(r'^/api/'),

        ]

    def __call__(self, request):
        path = request.path
        print(f"[Middleware] Checking path: {path}")

        if not request.user.is_authenticated:
            if not any(pattern.match(path) for pattern in self.exempt_urls):
                print(f"[Middleware] ❌ Not exempt: {path}, redirecting...")
                return redirect('/portal/login/')
            else:
                print(f"[Middleware] ✅ Exempted: {path}")

        return self.get_response(request)
