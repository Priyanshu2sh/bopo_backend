import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CustomerToCustomer, MerchantToMerchant
from accounts.models import Customer, Merchant
from .serializer import CustomerToCustomerSerializer, MerchantToMerchantSerializer

logger = logging.getLogger(__name__)

class CustomerToCustomerAPIView(APIView):

    def get(self, request):
        transfers = CustomerToCustomer.objects.all()
        serializer = CustomerToCustomerSerializer(transfers, many=True)
        return Response(serializer.data)

    def post(self, request):
        sender_id = request.data.get("sender_customer_id")
        receiver_id = request.data.get("receiver_customer_id")
        points = request.data.get("points")

        if not sender_id or not receiver_id or points is None:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            points = float(points)
            if points <= 0:
                return Response({"error": "Points must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid points value"}, status=status.HTTP_400_BAD_REQUEST)

        sender = get_object_or_404(Customer, customer_id=sender_id)
        receiver = get_object_or_404(Customer, customer_id=receiver_id)

        deducted_points = points * 0.95  # Apply 5% deduction

        transfer = CustomerToCustomer.objects.create(
            sender_customer=sender,
            receiver_customer=receiver,
            points=points,  # Save original points
            deducted_points=deducted_points  # ✅ Fix: Now deducted_points is set
        )

        serializer = CustomerToCustomerSerializer(transfer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MerchantToMerchantAPIView(APIView):

    def get(self, request):
        transfers = MerchantToMerchant.objects.all()
        serializer = MerchantToMerchantSerializer(transfers, many=True)
        return Response(serializer.data)

    def post(self, request):
        sender_id = request.data.get("sender_merchant_id")  # Correct key
        receiver_id = request.data.get("receiver_merchant_id")  # Correct key
        points = request.data.get("points")

        # ✅ Validate if all fields exist
        if not sender_id or not receiver_id or not points:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            points = int(points)  # Ensure it's an integer
            if points <= 0:
                return Response({"error": "Points must be a positive number"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid points value"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Get sender and receiver merchants
        sender = get_object_or_404(Merchant, merchant_id=sender_id)
        receiver = get_object_or_404(Merchant, merchant_id=receiver_id)

        # ✅ Calculate deduction (5%)
        deducted_points = int(points * 0.05)
        final_points = points - deducted_points

        # ✅ Create the transfer record
        transfer = MerchantToMerchant.objects.create(
            sender_merchant=sender,
            receiver_merchant=receiver,
            points=final_points,
            deducted_points=deducted_points
        )

        serializer = MerchantToMerchantSerializer(transfer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)