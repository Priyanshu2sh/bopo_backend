from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Customer, Merchant
from .models import TransferPoint
from .serializers import TransferPointSerializer
from django.db.models import Sum
from django.shortcuts import get_object_or_404

class RedeemAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')
        points = int(request.data.get('points', 0))

        if points <= 0:
            return Response({"error": "Points must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the actual Customer and Merchant instances
        customer = get_object_or_404(Customer, customer_id=customer_id)
        merchant = get_object_or_404(Merchant, merchant_id=merchant_id)

        deducted_points = int(points * 0.95)  # Apply 5% deduction

        transfer = TransferPoint.objects.create(
            customer_id=customer,
            merchant_id=merchant,
            points=deducted_points,
            transaction_type='redeem'
        )

        serializer = TransferPointSerializer(transfer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AwardAPIView(APIView):
    def post(self, request):
        merchant_id = request.data.get('merchant_id')
        customer_id = request.data.get('customer_id')
        points = int(request.data.get('points', 0))

        if points <= 0:
            return Response({"error": "Points must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the actual Customer and Merchant instances
        customer = get_object_or_404(Customer, customer_id=customer_id)
        merchant = get_object_or_404(Merchant, merchant_id=merchant_id)

        transfer = TransferPoint.objects.create(
            customer_id=customer,
            merchant_id=merchant,
            points=points,  # No deduction for award
            transaction_type='award'
        )

        serializer = TransferPointSerializer(transfer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class CustomerPointsAPIView(APIView):
    """
    API to retrieve all points stored for a particular customer_id.
    """

    def get(self, request, customer_id):
        try:
            # Fetch total points received by the customer
            received_points = TransferPoint.objects.filter(
                customer_id=customer_id,
                transaction_type="award"  # Customer receives points when awarded
            ).aggregate(total_received=Sum("points"))["total_received"] or 0

            # Fetch total points spent (redeemed) by the customer
            redeemed_points = TransferPoint.objects.filter(
                customer_id=customer_id,
                transaction_type="redeem"  # Customer spends points when redeeming
            ).aggregate(total_redeemed=Sum("points"))["total_redeemed"] or 0

            # Calculate net points stored for the customer
            net_points = received_points - redeemed_points

            # Fetch all transactions involving this customer
            transactions = TransferPoint.objects.filter(customer_id=customer_id).values(
                "id", "merchant_id", "points", "transaction_type", "created_at"
            )

            return Response({
                "customer_id": customer_id,
                "total_received": received_points,
                "total_redeemed": redeemed_points,
                "net_points": net_points,
                "transactions": list(transactions)  # List of all transactions
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
