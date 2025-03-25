from rest_framework import serializers
from .models import TransferPoint

class TransferPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferPoint
        fields = ['customer_id', 'merchant_id', 'points', 'transaction_type', 'created_at']

    def validate(self, data):
        if data['transaction_type'] not in ['redeem', 'award']:
            raise serializers.ValidationError("Invalid transaction type.")
        return data
