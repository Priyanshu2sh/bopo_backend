# myapp/routing.py
from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_type>\w+)_(?P<user_id>[\w\d]+)$', consumer.NotificationConsumer.as_asgi()),
]