from django.core.management.base import BaseCommand

from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from bopo_award.models import CustomerPoints, GlobalPoints, History

class Command(BaseCommand):
    help = 'Expire CustomerPoints older than 6 months and transfer to GlobalPoints'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        six_months_ago = now - timedelta(days=180)

        expired_entries = CustomerPoints.objects.filter(
            updated_at__lt=six_months_ago,
            points__gt=0
        )

        for expired in expired_entries:
            customer = expired.customer
            merchant = expired.merchant
            original_points = expired.points

            with transaction.atomic():
                expired.points = 0
                expired.save(update_fields=['points', 'updated_at'])

                global_point_entry, created = GlobalPoints.objects.get_or_create(
                    customer=customer,
                    defaults={'points': original_points}
                )
                if not created:
                    global_point_entry.points += original_points
                    global_point_entry.save(update_fields=['points', 'updated_at'])

                History.objects.create(
                    customer=customer,
                    merchant=merchant,
                    points=original_points,
                    transaction_type='expired'
                )

        self.stdout.write(self.style.SUCCESS('Expired CustomerPoints successfully.'))
