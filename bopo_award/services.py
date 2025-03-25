# awards/services.py
from decimal import Decimal
from django.db import transaction
from .models import TransferPoint, PointsBalance

@transaction.atomic
def transfer_points(customer, merchant, points, transfer_type):
    points = Decimal(points)
    charge = points * Decimal('0.05')  # 5% charge
    total_deduct = points + charge

    # Get or create PointsBalance for customer and merchant
    customer_balance, _ = PointsBalance.objects.get_or_create(customer=customer)
    merchant_balance, _ = PointsBalance.objects.get_or_create(merchant=merchant)

    # Log the current points balance for debugging
    print(f"Customer Balance: {customer_balance.points}")
    print(f"Merchant Balance: {merchant_balance.points}")
    print(f"Points to Transfer: {points}")
    print(f"Charge: {charge}")
    print(f"Total Deduct: {total_deduct}")

    if transfer_type == 'redeem':  # Customer to Merchant
        if customer_balance.points >= total_deduct:
            customer_balance.points -= total_deduct
            merchant_balance.points += points
            customer_balance.save()
            merchant_balance.save()
            TransferPoint.objects.create(customer=customer, merchant=merchant, points=points, transfer_type='redeem')
            return {"status": "success", "message": "Points redeemed successfully"}
        else:
            return {"status": "error", "message": "Insufficient points"}

    elif transfer_type == 'award':  # Merchant to Customer
        if merchant_balance.points >= total_deduct:
            merchant_balance.points -= total_deduct
            customer_balance.points += points
            merchant_balance.save()
            customer_balance.save()
            TransferPoint.objects.create(customer=customer, merchant=merchant, points=points, transfer_type='award')
            return {"status": "success", "message": "Points awarded successfully"}
        else:
            return {"status": "error", "message": "Insufficient points"}

    return {"status": "error", "message": "Invalid transfer type"}