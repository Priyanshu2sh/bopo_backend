from rest_framework import serializers
from .models import TransactionHistory

class TransactionHistorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = TransactionHistory
        fields = '__all__'

    def create(self, validated_data):
        return TransactionHistory.objects.create(**validated_data)
