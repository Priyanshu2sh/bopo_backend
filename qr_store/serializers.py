from rest_framework import serializers
from .models import QRStore

class QRStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRStore
        fields = ['id', 'customer', 'merchant', 'qr_code']
