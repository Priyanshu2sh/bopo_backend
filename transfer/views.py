from venv import logger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Customer, Merchant

from .models import Transfers
from .serializers import TransferSerializer
from django.shortcuts import get_object_or_404

class RedeemAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id', "").strip()
        customer_mobile = request.data.get('customer_mobile', "").strip()
        merchant_id = request.data.get('merchant_id', "").strip()
        merchant_mobile = request.data.get('merchant_mobile', "").strip()
        points = int(request.data.get('points', 0))

        if points <= 0:
            return Response({"error": "Points must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch or create Customer
        customer = None
        if customer_id:
            customer = Customer.objects.filter(customer_id=customer_id).first()
        elif customer_mobile:
            customer = Customer.objects.filter(mobile=customer_mobile).first()

        if not customer and customer_mobile:
            customer = Customer.objects.create(
                customer_id=f"CUST{customer_mobile[-6:]}",  # Generate unique ID
                mobile=customer_mobile
            )
            logger.info(f"New customer created: {customer.customer_id}")

        if not customer:
            return Response({"error": "Customer not found or could not be created."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch or create Merchant
        merchant = None
        if merchant_id:
            merchant = Merchant.objects.filter(merchant_id=merchant_id).first()
        elif merchant_mobile:
            merchant = Merchant.objects.filter(mobile=merchant_mobile).first()

        if not merchant and merchant_mobile:
            merchant_id_generated = f"M{merchant_mobile[-6:]}"  # Generate unique ID
            print(merchant_id_generated)
            merchant = Merchant.objects.create(
                merchant_id=merchant_id_generated,
                mobile=merchant_mobile
            )
            logger.info(f"New merchant created: {merchant.merchant_id}")

        if not merchant:
            return Response({"error": "Merchant not found or could not be created."}, status=status.HTTP_400_BAD_REQUEST)

        # Apply 5% deduction
        deducted_points = int(points * 0.95)

        # Create transaction
        transfer = Transfers.objects.create(
            customer_id=customer,
            merchant_id=merchant,
            points=deducted_points,
            transaction_type='redeem'
        )

        # ** Ensure merchant_id is always included in response **
        return Response({
            "customer_id": customer.customer_id,
            "customer_mobile": customer.mobile,
            "merchant_id": merchant.merchant_id,  # ** Now always included **
            "merchant_mobile": merchant.mobile,
            "points": deducted_points,
            "transaction_type": "redeem",
            "created_at": transfer.created_at
        }, status=status.HTTP_201_CREATED)


class AwardAPIView(APIView):
    def post(self, request):
        merchant_id = request.data.get('merchant_id', "").strip()
        merchant_mobile = request.data.get('merchant_mobile', "").strip()
        customer_id = request.data.get('customer_id', "").strip()
        customer_mobile = request.data.get('customer_mobile', "").strip()
        points = int(request.data.get('points', 0))

        if points <= 0:
            return Response({"error": "Points must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch or create Merchant
        merchant = None
        if merchant_id:
            merchant = Merchant.objects.filter(merchant_id=merchant_id).first()
        elif merchant_mobile:
            merchant = Merchant.objects.filter(mobile=merchant_mobile).first()

        if not merchant and merchant_mobile:
            merchant_id_generated = f"M{merchant_mobile[-6:]}"  # Generate unique ID
            merchant = Merchant.objects.create(
                merchant_id=merchant_id_generated,
                mobile=merchant_mobile
            )
            logger.info(f"New merchant created: {merchant.merchant_id}")

        if not merchant:
            return Response({"error": "Merchant not found or could not be created."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch or create Customer
        customer = None
        if customer_id:
            customer = Customer.objects.filter(customer_id=customer_id).first()
        elif customer_mobile:
            customer = Customer.objects.filter(mobile=customer_mobile).first()

        if not customer and customer_mobile:
            customer = Customer.objects.create(
                customer_id=f"CUST{customer_mobile[-6:]}",  # Generate unique ID
                mobile=customer_mobile
            )
            logger.info(f"New customer created: {customer.customer_id}")

        if not customer:
            return Response({"error": "Customer not found or could not be created."}, status=status.HTTP_400_BAD_REQUEST)

        # Create transaction (No deduction for awards)
        transfer = Transfers.objects.create(
            customer_id=customer,
            merchant_id=merchant,
            points=points,
            transaction_type='award'
        )

        return Response({
            "customer_id": customer.customer_id,
            "customer_mobile": customer.mobile,
            "merchant_id": merchant.merchant_id,  # ** Now always included **
            "merchant_mobile": merchant.mobile,
            "points": points,
            "transaction_type": "award",
            "created_at": transfer.created_at
        }, status=status.HTTP_201_CREATED)
    

class CustomerPointsAPIView(APIView):
    """API to fetch all stored points for a given customer_id"""

    def get(self, request, customer_id):
        customer = Customer.objects.filter(customer_id=customer_id).first()

        if not customer:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all transactions related to this customer
        transactions = Transfers.objects.filter(customer_id=customer)

        if not transactions.exists():
            return Response({
                "customer_id": customer_id,
                "total_received": 0,
                "total_redeemed": 0,
                "net_points": 0,
                "transactions": []
            }, status=status.HTTP_200_OK)

        # Compute points summary
        total_received = sum(t.points for t in transactions if t.transaction_type == "award")
        total_redeemed = sum(t.points for t in transactions if t.transaction_type == "redeem")
        net_points = total_received - total_redeemed

        # Prepare response data
        response_data = {
            "customer_id": customer_id,
            "total_received": total_received,
            "total_redeemed": total_redeemed,
            "net_points": net_points,
            "transactions": [
                {
                    "id": t.id,
                    "merchant_id": t.merchant_id.merchant_id,
                    "points": t.points,
                    "transaction_type": t.transaction_type,
                    "created_at": t.created_at
                }
                for t in transactions
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)