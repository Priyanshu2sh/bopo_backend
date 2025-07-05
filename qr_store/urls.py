from django.urls import path
from .views import GenerateQRCodeView, DecodeQRCodeView

urlpatterns = [
    path('generate_qr/', GenerateQRCodeView.as_view(), name='generate_qr'),
    path('decode_qr/', DecodeQRCodeView.as_view(), name='decode_qr'),
]
