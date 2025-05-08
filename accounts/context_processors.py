# accounts/context_processors.py

from .models import Logo

def logo_context(request):
    return {'logo': Logo.objects.first()}
