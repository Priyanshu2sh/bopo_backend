from rest_framework import serializers
from .models import Transfers

class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfers
        fields = ['customer_id', 'merchant_id', 'points', 'transaction_type', 'created_at']

    def validate(self, data):
        if data['transaction_type'] not in ['redeem', 'award']:
            raise serializers.ValidationError("Invalid transaction type.")
        return data
    


