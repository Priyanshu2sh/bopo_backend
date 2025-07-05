import qrcode
import io
import base64
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Customer, Merchant
from PIL import Image

class GenerateQRCodeView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')

        if customer_id:
            user = get_object_or_404(Customer, customer_id=customer_id)
            user_type = "customer"
            user_id = customer_id
        elif merchant_id:
            user = get_object_or_404(Merchant, merchant_id=merchant_id)
            user_type = "merchant"
            user_id = merchant_id
        else:
            return JsonResponse({'error': 'customer_id or merchant_id is required'}, status=400)

        # ✅ Generate QR Code storing user_id
        qr = qrcode.make(user_id)
        qr_io = io.BytesIO()
        qr.save(qr_io, format='PNG')
        qr_data = base64.b64encode(qr_io.getvalue()).decode()

        # ✅ Store QR code in the database
        user.qrstore = qr_data  # Assuming `qrstore` is a field in Customer/Merchant model
        user.save()

        return JsonResponse({
            'qr_code': qr_data,
            'user_type': user_type,
            'user_id': user_id
        })

class DecodeQRCodeView(APIView):
    def post(self, request):
        base64_qr = request.data.get('qr_code')

        if not base64_qr:
            return JsonResponse({'error': 'QR code is required'}, status=400)

        try:
            qr_image_data = base64.b64decode(base64_qr)
            image = Image.open(io.BytesIO(qr_image_data))

            response = HttpResponse(content_type="image/png")
            image.save(response, "PNG")
            return response

        except Exception as e:
            return JsonResponse({'error': f'Failed to decode QR code: {str(e)}'}, status=500)
