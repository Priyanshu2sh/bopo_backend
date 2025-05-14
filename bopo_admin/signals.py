from django.db.models.signals import post_save
from django.dispatch import receiver

from bopo_admin.views import send_notification_to_user
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        user_id = instance.user.id
        message = instance.message  # Assuming your Notification model has a `message` field
        send_notification_to_user(user_id, message)
