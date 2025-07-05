from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.models import Customer, Merchant
from .models import TransactionHistory
from .serializers import TransactionHistorySerializer

class TransactionHistoryView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TransactionHistorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                transaction = serializer.save()
                return Response(
                    {
                        "message": "Transaction recorded successfully!",
                        "transaction": TransactionHistorySerializer(transaction).data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, *args, **kwargs):
        customer_id = request.query_params.get('customer_id')
        merchant_id = request.query_params.get('merchant_id')

        if customer_id:
            transactions = TransactionHistory.objects.filter(customer_id=customer_id)
        elif merchant_id:
            transactions = TransactionHistory.objects.filter(merchant_id=merchant_id)
        else:
            return Response(
                {"error": "Please provide a customer_id or merchant_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TransactionHistorySerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    