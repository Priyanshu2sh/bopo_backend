import os
from dotenv import load_dotenv
from twilio.rest import Client

from django.core.exceptions import ObjectDoesNotExist
# from bopo.models import CustomerToCustomer

# Load environment variables from .env file
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_otp_to_mobile(mobile_number, otp):
    """Function to send OTP to the user's mobile number using Twilio"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=mobile_number
    )
    return message.sid



# def get_or_create_customer_points(customer_id):
#     try:
#         return CustomerToCustomer.objects.get(customer_id=customer_id)
#     except ObjectDoesNotExist:
#         return CustomerToCustomer.objects.create(customer_id=customer_id, customer_balance=0)

