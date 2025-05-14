"""
ASGI config for bopo_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import bopo_admin.routing
import django

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bopo_backend.settings')
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        bopo_admin.routing.websocket_urlpatterns
    )
})

# bopo_backend/asgi.py

# import os
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bopo_backend.settings')
# django.setup()   # <-- THIS IS THE KEY

# # Now safely import things that touch models
# import bopo_admin.routing

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack

# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             bopo_admin.routing.websocket_urlpatterns
#         )
#     ),
# })
