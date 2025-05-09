# import json
# from accounts.models import User
# from bopo_admin.models import Notification


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope['url_route']['kwargs']['user_id']
#         self.user = await self.get_user()

#         if self.user:
#             await self.accept()

#             # Create a unique group name based on the user ID
#             self.group_name = f"notifications_{self.user_id}"

#             # Add the user to the group
#             await self.channel_layer.group_add(self.group_name, self.channel_name)

#             # Send initial unread count
#             await self.send_unread_notifications_count()
#         else:
#             await self.close()

#     async def disconnect(self, close_code):
#         if self.user:
#             # Remove the user from the group
#             await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         if data.get("action") == "mark_as_read":
#             await self.mark_notifications_as_read()
#             await self.send_unread_notifications_count()

#     @database_sync_to_async
#     def get_user(self):
#         try:
#             return User.objects.get(id=self.user_id)
#         except User.DoesNotExist:
#             return None

#     @database_sync_to_async
#     def get_unread_notifications_count(self):
#         return Notification.objects.filter(user=self.user, is_read=False).count()

#     @database_sync_to_async
#     def mark_notifications_as_read(self):
#         Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)

#     async def send_unread_notifications_count(self):
#         count = await self.get_unread_notifications_count()
#         await self.send(text_data=json.dumps({
#             "unread_count": count
#         }))

#     async def send_unread_count(self, event):
#         """Send updated unread count to the frontend."""
#         await self.send(text_data=json.dumps({
#             "unread_count": event["unread_count"]
#         }))

#     async def mark_notifications_read(self, event):
#         """Handle mark_notifications_read event and send updated unread count."""
#         await self.send(text_data=json.dumps({
#             "unread_count": event["unread_count"]
# }))




# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from bopo_admin.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user = await self.get_user()

        if not self.user:
            await self.close()
            return

        await self.accept()
        self.group_name = f"notifications_{self.user_id}"
        
        # Add the user to their notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Send initial unread count
        await self.send_unread_count()

    async def disconnect(self, close_code):
        # Remove from group on disconnect
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get("action") == "mark_as_read":
                await self.mark_notifications_as_read()
                await self.send_unread_count()
        except json.JSONDecodeError:
            pass

    @database_sync_to_async
    def get_user(self):
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_unread_notifications_count(self):
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notifications_as_read(self):
        Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)

    async def send_unread_count(self):
        count = await self.get_unread_notifications_count()
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": count
        }))

    async def send_notification(self, event):
        """Handler for when a notification is sent to the group"""
        await self.send(text_data=json.dumps({
            "type": "notification",
            "notification": event["notification"]
        }))