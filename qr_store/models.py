import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from accounts.models import Customer, Merchant

class QRStore(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate QR content
        if self.customer:
            qr_content = f"customer_id:{self.customer.id}"
        elif self.merchant:
            qr_content = f"merchant_id:{self.merchant.id}"
        else:
            raise ValueError("Either customer or merchant must be provided.")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        # Save QR code image
        img = qr.make_image(fill="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.qr_code.save(f"qr_{self.customer.id if self.customer else self.merchant.id}.png", ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)
