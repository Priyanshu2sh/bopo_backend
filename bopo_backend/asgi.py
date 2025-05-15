import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bopo_backend.settings')
django.setup()  # Make sure Django is fully setup before importing app modules

# Import your routing after setup
import bopo_admin.routing

# Get Django's default ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bopo_admin.routing.websocket_urlpatterns
        )
    ),
})
