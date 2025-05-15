import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from bopo_admin.models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_type = self.scope["url_route"]["kwargs"]["user_type"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]

        self.group_name = f"{self.user_type}_{self.user_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        notifications = await self.get_old_notifications(self.user_type, self.user_id)
        for notif in notifications:
            await self.send(text_data=json.dumps({
                'notification': {
                    'title': notif.title,
                    'description': notif.description,
                    'type': notif.notification_type,
                    'timestamp': str(notif.created_at),
                }
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'notification': message}))

    @sync_to_async
    def get_old_notifications(self, user_type, user_id):
        if user_type == "merchant":
            qs = Notification.objects.filter(merchant_id__merchant_id=user_id).order_by('-created_at')[:10]
        elif user_type == "customer":
            qs = Notification.objects.filter(customer_id__customer_id=user_id).order_by('-created_at')[:10]
        else:
            return []
        return list(qs)
