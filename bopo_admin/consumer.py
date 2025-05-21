import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import F
from accounts.models import Merchant, Customer

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

        # Fetch both unread count and recent notifications
        unread_count = await self.get_unread_notification_count(self.user_type, self.user_id)
        notifications = await self.get_recent_notifications(self.user_type, self.user_id)
        
        # Send initial data
        await self.send(text_data=json.dumps({
            'unread_count': unread_count,
            # 'notifications': notifications
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        # Send both the new notification and updated unread count
        await self.send(text_data=json.dumps({
            'unread_count': event['unread_count'],
            'new_notification': event.get('notification')
        }))

    @sync_to_async
    def get_unread_notification_count(self, user_type, user_id):
        if user_type == "merchant":
            return Merchant.objects.filter(merchant_id=user_id).values_list('unread_notification', flat=True).first() or 0
        elif user_type == "customer":
            return Customer.objects.filter(customer_id=user_id).values_list('unread_notification', flat=True).first() or 0
        return 0

    @sync_to_async
    def get_recent_notifications(self, user_type, user_id, limit=5):
        from bopo_admin.models import Notification
        if user_type == "merchant":
            notifications = Notification.objects.filter(
                merchants__merchant_id=user_id
            ).order_by('-created_at')[:limit]
        elif user_type == "customer":
            notifications = Notification.objects.filter(
                customers__customer_id=user_id
            ).order_by('-created_at')[:limit]
        else:
            return []
        
        return [{
            'title': n.title,
            'description': n.description,
            'type': n.notification_type,
            'timestamp': str(n.created_at),
        } for n in notifications]

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from bopo_admin.models import Notification

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_type = self.scope["url_route"]["kwargs"]["user_type"]
#         self.user_id = self.scope["url_route"]["kwargs"]["user_id"]

#         self.group_name = f"{self.user_type}_{self.user_id}"

#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#         await self.accept()

#         notifications = await self.get_old_notifications(self.user_type, self.user_id)
#         for notif in notifications:
#             await self.send(text_data=json.dumps({
#                 'notification': {
#                     'title': notif.title,
#                     'description': notif.description,
#                     'type': notif.notification_type,
#                     'timestamp': str(notif.created_at),
#                 }
#             }))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         pass

#     async def send_notification(self, event):
#         message = event['message']
#         await self.send(text_data=json.dumps({'notification': message}))

#     @sync_to_async
#     def get_old_notifications(self, user_type, user_id):
#         if user_type == "merchant":
#             qs = Notification.objects.filter(merchant_id__merchant_id=user_id).order_by('-created_at')[:10]
#         elif user_type == "customer":
#             qs = Notification.objects.filter(customer_id__customer_id=user_id).order_by('-created_at')[:10]
#         else:
#             return []
#         return list(qs)
