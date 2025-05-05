from datetime import timedelta, timezone
import random
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import F
from django.db.models import Sum
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import CustomerSerializer, MerchantSerializer
from bopo_admin.models import DeductSetting
from django.db import transaction

from .serializers import BankDetailSerializer, CashOutSerializer, CorporateProjectSerializer, CustomerCashOutSerializer, HelpSerializer, MerchantCashOutSerializer, PaymentDetailsSerializer

from .models import AwardPoints, BankDetail, CashOut, CustomerToCustomer, Help, MerchantToMerchant, ModelPlan, PaymentDetails
from accounts.models import Corporate, Customer, Merchant, Terminal
from .models import CustomerPoints, CustomerToCustomer, MerchantPoints, History

class RedeemPointsAPIView(APIView):
    """
    API for Customer to Merchant point transfer (with dynamic deduction % based on Super Admin setting).
    """

    def post(self, request):
        customer_id = request.data.get('customer_id', '').strip()
        customer_mobile = request.data.get('customer_mobile', '').strip()
        merchant_id = request.data.get('merchant_id', '').strip()
        merchant_mobile = request.data.get('merchant_mobile', '').strip()
        pin = request.data.get('pin')
        points = int(request.data.get('points', 0))

        if points <= 0:
            return Response({'error': 'Points must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch customer
        try:
            if customer_id:
                customer = Customer.objects.get(customer_id__iexact=customer_id)
            elif customer_mobile:
                customer = Customer.objects.get(mobile=customer_mobile)
            else:
                return Response({'error': 'Customer ID or mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Validate customer's PIN
        if str(customer.pin) != str(pin):
            return Response({'error': 'Please enter the correct PIN.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch or create merchant
        merchant = None
        if merchant_id:
            try:
                merchant = Merchant.objects.get(merchant_id__iexact=merchant_id)
            except Merchant.DoesNotExist:
                return Response({'error': f'Merchant not found for ID {merchant_id}'}, status=status.HTTP_404_NOT_FOUND)
        elif merchant_mobile:
            merchant, created = Merchant.objects.get_or_create(
                mobile=merchant_mobile,
                defaults={'merchant_id': f"M{random.randint(100000, 999999)}"}
            )
        else:
            return Response({'error': 'Merchant ID or mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Check total available customer points
        total_customer_points = CustomerPoints.objects.filter(customer=customer).aggregate(total=Sum('points'))['total'] or 0

        if total_customer_points < points:
            return Response({'error': 'Insufficient points. Transfer not allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Deduct points across CustomerPoints entries
        points_to_deduct = points
        customer_point_entries = CustomerPoints.objects.filter(customer=customer).order_by('-points')

        for entry in customer_point_entries:
            if points_to_deduct <= 0:
                break
            if entry.points <= points_to_deduct:
                points_to_deduct -= entry.points
                entry.points = 0
            else:
                entry.points = F('points') - points_to_deduct
                points_to_deduct = 0
            entry.save(update_fields=['points'])

        # ✅ Fetch dynamic deduction percentage
        try:
            setting = DeductSetting.objects.get(id=1)
            deduct_percentage = setting.deduct_percentage
        except DeductSetting.DoesNotExist:
            deduct_percentage = 5.0  # fallback default deduction if setting is not found

        # ✅ Apply dynamic deduction
        deduction_factor = (100 - deduct_percentage) / 100  # example: 5% means 95%
        points_after_deduction = round(points * deduction_factor, 2)

        # ✅ Update or create MerchantPoints
        merchant_points, created = MerchantPoints.objects.get_or_create(
            merchant=merchant,
            defaults={'points': points_after_deduction}
        )
        if not created:
            merchant_points.points = F('points') + points_after_deduction
            merchant_points.save(update_fields=['points'])

        # ✅ Store transaction in history
        History.objects.create(
            customer=customer,
            merchant=merchant,
            points=points,
            transaction_type="redeem"
        )

        return Response({
            'message': f'Points redeemed successfully with {deduct_percentage}% deduction.',
            'merchant_id': merchant.merchant_id,
            'merchant_mobile': merchant.mobile
        }, status=status.HTTP_200_OK)
        
        
        
class AwardPointsAPIView(APIView):
    """
    API for Merchant to Customer point transfer (No deduction for rental plan merchants).
    Dynamically fetches % conversion from AwardPoints model (fallback: 10%)
    """

    def get_conversion_percentage(self):
        config = AwardPoints.objects.first()
        try:
            return float(config.percentage) if config and config.percentage > 0 else 10
        except:
            return 10  # fallback

    def generate_unique_customer_id(self):
        while True:
            customer_id = f"CUST{random.randint(100000, 999999)}"
            if not Customer.objects.filter(customer_id=customer_id).exists():
                return customer_id

    def generate_unique_pin(self):
        while True:
            pin = random.randint(1000, 9999)
            if not Customer.objects.filter(pin=pin).exists():
                return pin

    def get_merchant_plan_type(self, merchant):
        payment_detail = PaymentDetails.objects.filter(merchant=merchant).first()
        if payment_detail and payment_detail.plan_type:
            return payment_detail.plan_type.lower()
        return "prepaid"  # default to prepaid if no payment detail found

    def post(self, request):
        customer_id = request.data.get('customer_id')
        customer_mobile = request.data.get('customer_mobile')
        merchant_id = request.data.get('merchant_id')
        merchant_mobile = request.data.get('merchant_mobile')
        purchased_amt = request.data.get('purchased_amt')

        # Validate purchased_amt
        try:
            purchased_amt = float(purchased_amt)
        except (ValueError, TypeError):
            return Response({'error': 'Purchased amount must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

        if purchased_amt <= 0:
            return Response({'error': 'Purchased amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch conversion percentage from config
        conversion_percentage = self.get_conversion_percentage()
        points = int(purchased_amt * conversion_percentage / 100)

        # ✅ Fetch or create Customer
        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        elif customer_mobile:
            customer = Customer.objects.filter(mobile=customer_mobile).first()
            if not customer:
                # Create new customer
                new_customer_id = self.generate_unique_customer_id()
                new_pin = self.generate_unique_pin()
                customer = Customer.objects.create(
                    customer_id=new_customer_id,
                    mobile=customer_mobile,
                    pin=new_pin,
                    first_name='New',
                    last_name='Customer',
                    status='Active'
                )
        else:
            return Response({'error': 'Customer ID or mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch or create Merchant
        merchant = None
        if merchant_id:
            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
            except Merchant.DoesNotExist:
                return Response({'error': 'Merchant not found.'}, status=status.HTTP_404_NOT_FOUND)
        elif merchant_mobile:
            merchant, created = Merchant.objects.get_or_create(
                mobile=merchant_mobile,
                defaults={
                    'merchant_id': f"M{random.randint(100000, 999999)}",
                    'first_name': 'New',
                    'last_name': 'Merchant',
                    'status': 'Active'
                }
            )
        else:
            return Response({'error': 'Merchant ID or mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Check merchant's plan type
        plan_type = self.get_merchant_plan_type(merchant)

        if plan_type == "prepaid":
            # ✅ Check if merchant has enough points
            merchant_points = MerchantPoints.objects.filter(merchant=merchant).first()
            if not merchant_points or merchant_points.points < points:
                return Response({'error': 'Merchant does not have enough points to award'}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Deduct points from Merchant
            MerchantPoints.objects.filter(merchant=merchant).update(points=F('points') - points)

        # ✅ Update or create CustomerPoints
        customer_points, created = CustomerPoints.objects.get_or_create(
            customer=customer,
            merchant=merchant,
            defaults={'points': points}
        )
        if not created:
            CustomerPoints.objects.filter(customer=customer, merchant=merchant).update(points=F('points') + points)

        # ✅ Log transaction
        History.objects.create(
            customer=customer,
            merchant=merchant,
            points=points,
            transaction_type="award"
        )

        return Response({
            'message': 'Points awarded successfully',
            'merchant_id': merchant.merchant_id,
            'merchant_mobile': merchant.mobile,
            'customer_id': customer.customer_id,
            'customer_mobile': customer.mobile,
            'points_awarded': points,
            'conversion_percentage': conversion_percentage,
            'merchant_plan_type': plan_type
        }, status=status.HTTP_200_OK)     
              
class TransferPointsMerchantToCustomerAPIView(APIView):
    """
    API for transferring points from Merchant to Customer (NO deduction),
    with Terminal ID & PIN verification.
    """

    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')
        terminal_id = request.data.get('terminal_id')
        tid_pin = request.data.get('tid_pin')
        points = int(request.data.get('points', 0))

        # ✅ Validate input fields
        if not all([customer_id, merchant_id, terminal_id, tid_pin, points]):
            return Response({'error': 'All fields (customer_id, merchant_id, terminal_id, tid_pin, points) are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if points <= 0:
            return Response({'error': 'Points must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch customer
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Fetch merchant
        try:
            merchant = Merchant.objects.get(merchant_id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': 'Merchant not found.'}, status=status.HTTP_404_NOT_FOUND)

       # ✅ Validate Terminal (must belong to merchant and pin must match)
        terminal = Terminal.objects.filter(
            terminal_id=terminal_id,
            merchant_id=merchant.pk,
            tid_pin=tid_pin
        ).first()
        if not terminal:
            return Response({'error': 'Invalid Terminal ID or PIN for this merchant.'}, status=status.HTTP_403_FORBIDDEN)
        # ✅ Check merchant has sufficient points
        merchant_points = MerchantPoints.objects.filter(merchant=merchant).first()
        if not merchant_points or merchant_points.points < points:
            return Response({'error': 'Merchant does not have sufficient points to transfer.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Deduct points from Merchant
        MerchantPoints.objects.filter(merchant=merchant).update(points=F('points') - points)

        # ✅ Add points to Customer
        customer_points, created = CustomerPoints.objects.get_or_create(
            customer=customer,
            merchant=merchant,
            defaults={'points': points}
        )
        if not created:
            CustomerPoints.objects.filter(customer=customer, merchant=merchant).update(points=F('points') + points)

        # ✅ Log transaction
        History.objects.create(
            customer=customer,
            merchant=merchant,
            points=points,
            transaction_type="award"  # You can name it "transfer" if needed
        )

        return Response({
            'message': 'Points transferred successfully.',
            'merchant_id': merchant.merchant_id,
            'customer_id': customer.customer_id,
            'points_transferred': points,
            'terminal_id': terminal.terminal_id
        }, status=status.HTTP_200_OK)



class HistoryAPIView(APIView):
    """
    API to fetch transaction history including sender and receiver status.
    Also fetches the latest balance of points for customers and merchants.
    Supports filtering by customer_id or merchant_id.
    """

    def get(self, request, id, user_type):

        all_transactions = History.objects.all().order_by('-created_at')

        if user_type == 'customer':
            transactions = all_transactions.filter(customer__customer_id=id)
            
        elif user_type == 'merchant':
            transactions = all_transactions.filter(merchant__merchant_id=id)
        else:
            return Response({"error": "Invalid user_type"}, status=status.HTTP_400_BAD_REQUEST)

        transaction_data = []

        for transaction in transactions:
            data = {
                "customer_id": transaction.customer.customer_id if transaction.customer else None,
                "merchant_id": transaction.merchant.merchant_id if transaction.merchant else None,
                "points": transaction.points,
                "transaction_type": transaction.transaction_type,
                "sender_status": "Customer" if transaction.transaction_type == "redeem" else "Merchant",
                "receiver_status": "Merchant" if transaction.transaction_type == "redeem" else "Customer",
                "created_at": transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }

            # Add merchant info only for customer
            if user_type == 'customer' and transaction.merchant:
                data["merchant_name"] = f"{transaction.merchant.first_name} {transaction.merchant.last_name}"
                data["shop_name"] = transaction.merchant.shop_name

            # Add customer info only for merchant
            if user_type == 'merchant' and transaction.customer:
                data["customer_name"] = f"{transaction.customer.first_name} {transaction.customer.last_name}"

            transaction_data.append(data)

        response_data = {
            "transaction_history": transaction_data,
        }

        # Add balance details specific to user type
        if user_type == 'customer':
            customer_balances = {}
            customer_points = CustomerPoints.objects.filter(customer__customer_id=id).values(
                'merchant__merchant_id',
                'merchant__first_name',
                'merchant__last_name',
                'merchant__shop_name'
            ).annotate(total_points=Sum('points'))

            for cp in customer_points:
                merchant_id = cp['merchant__merchant_id']
                customer_balances[merchant_id] = {
                    "merchant_name": f"{cp['merchant__first_name']} {cp['merchant__last_name']}",
                    "shop_name": cp['merchant__shop_name'],
                    "total_points": cp['total_points']
                }

            response_data["customer_balances"] = customer_balances

        elif user_type == 'merchant':
            merchant_points = MerchantPoints.objects.filter(merchant__merchant_id=id).aggregate(
                total_points=Sum('points')
            )
            merchant_balance = merchant_points['total_points'] or 0
            response_data["merchant_balance"] = merchant_balance

        return Response(response_data, status=status.HTTP_200_OK)
 

class CustomerToCustomerTransferAPIView(APIView):
    """
    API for transferring points from one customer to another with dynamic deduction percentage (as set by Super Admin).
    """

    def post(self, request):
        sender_customer_id = request.data.get("sender_customer_id")
        receiver_customer_id = request.data.get("receiver_customer_id")
        merchant_id = request.data.get("merchant_id")
        points = int(request.data.get("points", 0))

        # Fetch sender, receiver, and merchant
        try:
            sender_customer = Customer.objects.get(customer_id=sender_customer_id)
            receiver_customer = Customer.objects.get(customer_id=receiver_customer_id)
            merchant = Merchant.objects.get(merchant_id=merchant_id)
        except Customer.DoesNotExist:
            return Response({"error": "Sender or receiver customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Merchant.DoesNotExist:
            return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch sender's total available points
        sender_points = CustomerPoints.objects.filter(
            customer=sender_customer, merchant=merchant
        ).aggregate(total=Sum('points'))['total'] or 0

        # Validate points
        if sender_points < points:
            return Response({
                "error": "Insufficient points for transfer",
                "available_points": sender_points,
                "requested_points": points
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch dynamic deduction percentage from the DeductSetting table
        try:
            setting = DeductSetting.objects.get(id=1)  # Assuming only one setting exists
            deduct_percentage = setting.deduct_percentage
        except DeductSetting.DoesNotExist:
            deduct_percentage = 5.0  # Default fallback if no setting found

        # Apply dynamic deduction
        deduction_factor = (100 - deduct_percentage) / 100  # e.g., 5% means 95%
        points_after_deduction = int(points * deduction_factor)

        # Deduct points from sender safely
        sender_entry, _ = CustomerPoints.objects.get_or_create(
            customer=sender_customer, merchant=merchant, defaults={"points": 0}
        )
        sender_entry.points = F('points') - points
        sender_entry.save(update_fields=['points'])
        sender_entry.refresh_from_db()

        # Add points to receiver safely
        receiver_entry, _ = CustomerPoints.objects.get_or_create(
            customer=receiver_customer, merchant=merchant, defaults={"points": 0}
        )
        receiver_entry.points = F('points') + points_after_deduction
        receiver_entry.save(update_fields=['points'])
        receiver_entry.refresh_from_db()

        # Save transaction record
        CustomerToCustomer.objects.create(
            sender_customer=sender_customer,
            receiver_customer=receiver_customer,
            merchant=merchant,
            points=points_after_deduction
        )

        return Response({
            "message": f"Points transferred successfully with {deduct_percentage}% deduction.",
            "points_transferred": points_after_deduction,
            "sender_balance": sender_entry.points,
            "receiver_balance": receiver_entry.points
        }, status=status.HTTP_200_OK)
        
        

class MerchantToMerchantTransferAPIView(APIView):
    """
    API for Merchant to Merchant point transfer.
    Only allowed if BOTH sender and receiver have valid plans (checked from the ModelPlan table).
    """

    def post(self, request):
        sender_merchant_id = request.data.get("sender_merchant_id")
        receiver_merchant_id = request.data.get("receiver_merchant_id")
        points = int(request.data.get("points", 0))

        if points <= 0:
            return Response({"error": "Points must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate both merchants
        try:
            sender_merchant = Merchant.objects.get(merchant_id=sender_merchant_id)
            receiver_merchant = Merchant.objects.get(merchant_id=receiver_merchant_id)
        except Merchant.DoesNotExist:
            return Response({"error": "Invalid sender or receiver merchant ID"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch LATEST PaymentDetails for both merchants (avoid MultipleObjectsReturned)
        sender_payment = PaymentDetails.objects.filter(merchant=sender_merchant).order_by('-created_at').first()
        receiver_payment = PaymentDetails.objects.filter(merchant=receiver_merchant).order_by('-created_at').first()

        if not sender_payment or not receiver_payment:
            return Response({"error": "Payment details not found for sender or receiver merchant."}, status=status.HTTP_404_NOT_FOUND)

        sender_plan = sender_payment.plan_type.lower()  # 'prepaid' or 'rental'
        receiver_plan = receiver_payment.plan_type.lower()

        # Only allow transfer if BOTH have valid plans from ModelPlan
        if sender_plan != "prepaid" and receiver_plan != "prepaid":
            return Response({"error": "Both sender and receiver have rental plans, so points cannot be transferred."},
                            status=status.HTTP_400_BAD_REQUEST)
        elif sender_plan != "prepaid":
            return Response({"error": "Sender has a rental plan, so cannot transfer points."},
                            status=status.HTTP_400_BAD_REQUEST)
        elif receiver_plan != "prepaid":
            return Response({"error": "Receiver merchant has a rental plan, so points cannot be transferred."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate that both merchants have a valid plan from ModelPlan
        current_date = timezone.now()

        try:
            sender_plan_info = ModelPlan.objects.get(plan_type=sender_payment.plan_type)
            receiver_plan_info = ModelPlan.objects.get(plan_type=receiver_payment.plan_type)
        except ModelPlan.DoesNotExist:
            return Response({"error": "Invalid plan type for one or both merchants."}, status=status.HTTP_404_NOT_FOUND)

        sender_plan_validity = sender_plan_info.plan_validity
        receiver_plan_validity = receiver_plan_info.plan_validity

        # Assuming the plan_validity field stores a string like "12 months", "24 months", etc.
        # Parse the validity period and calculate expiration date

        sender_expiry_date = current_date + timedelta(days=int(sender_plan_validity.split()[0]) * 30)  # Assuming months
        receiver_expiry_date = current_date + timedelta(days=int(receiver_plan_validity.split()[0]) * 30)  # Assuming months

        if sender_expiry_date < current_date:
            return Response({"error": "Sender's plan has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if receiver_expiry_date < current_date:
            return Response({"error": "Receiver's plan has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Both plans are valid → proceed with transfer
        sender_points = MerchantPoints.objects.filter(merchant=sender_merchant).first()
        if not sender_points:
            return Response({"error": "Sender has no points available"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch dynamic deduction %
        try:
            setting = DeductSetting.objects.get(id=1)
            deduct_percentage = setting.deduct_percentage
        except DeductSetting.DoesNotExist:
            deduct_percentage = 5.0  # default fallback

        deduction_factor = (100 - deduct_percentage) / 100
        points_after_deduction = int(points * deduction_factor)
        total_points_deducted = int(points * (1 + (deduct_percentage / 100)))

        if sender_points.points < total_points_deducted:
            return Response({"error": "Insufficient points after deduction for transfer"}, status=status.HTTP_400_BAD_REQUEST)

        # Perform transfer inside transaction (safety)
        with transaction.atomic():
            # Deduct from sender
            sender_points.points -= total_points_deducted
            sender_points.save()

            # Credit to receiver
            receiver_points, created = MerchantPoints.objects.get_or_create(
                merchant=receiver_merchant,
                defaults={"points": points_after_deduction}
            )
            if not created:
                receiver_points.points += points_after_deduction
                receiver_points.save()

            # Update transaction history
            merchant_transfer, created = MerchantToMerchant.objects.get_or_create(
                sender_merchant=sender_merchant,
                receiver_merchant=receiver_merchant,
                defaults={"points": points}
            )
            if not created:
                merchant_transfer.points = F("points") + points
                merchant_transfer.save()

        updated_sender_balance = int(MerchantPoints.objects.get(merchant=sender_merchant).points)
        updated_receiver_balance = int(MerchantPoints.objects.get(merchant=receiver_merchant).points)

        return Response(
            {
                "message": f"Points transferred successfully with {deduct_percentage}% deduction.",
                "sender_balance": updated_sender_balance,
                "receiver_balance": updated_receiver_balance
            },
            status=status.HTTP_200_OK
        )   
        
        
           
class CheckPointsAPIView(APIView):
    """
    API to check:
    - Total points available for a customer or merchant
    - How many points a customer has transferred to each merchant
    - How many points a merchant has received from customers
    - Remaining points of the customer or merchant
    """

    def get(self, request, id):
        if not id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the ID belongs to a Customer
        customer = Customer.objects.filter(customer_id=id).first()

        # Check if the ID belongs to a Merchant
        merchant = Merchant.objects.filter(merchant_id=id).first()

        if customer:
            # Fetch total available points for customer
            total_points = CustomerPoints.objects.filter(customer=customer).aggregate(total=Sum('points'))['total'] or 0

            # Fetch transfer history (Grouped by Merchant)
            transfer_history = {}
            customer_points = CustomerPoints.objects.filter(customer=customer)

            for cp in customer_points:
                merchant_id = cp.merchant.merchant_id
                transferred_points = cp.points

                transfer_history[merchant_id] = {
                    "transferred_points": transferred_points
                }

            response_data = {
                "customer_id": id,
                "total_points": total_points,
                "transfer_history": transfer_history
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif merchant:
            # Fetch total available points for merchant
            total_points = MerchantPoints.objects.filter(merchant=merchant).aggregate(total=Sum('points'))['total'] or 0

            # Fetch received history (Grouped by Customer)
            received_history = {}
            merchant_points = CustomerPoints.objects.filter(merchant=merchant)

            for mp in merchant_points:
                customer_id = mp.customer.customer_id
                received_points = mp.points

                received_history[customer_id] = {
                    "received_points": received_points
                }

            response_data = {
                "merchant_id": id,
                "total_points": total_points,
                "received_history": received_history
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid ID. No customer or merchant found.'}, status=status.HTTP_404_NOT_FOUND)
        


class UpdateCustomerProfileAPIView(APIView):
    """API to update customer profile"""


    def get(self, request, customer_id):
        """
        Get the profile of a specific customer using customer_id.
        """
        customer = get_object_or_404(Customer, customer_id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response({
            "message": "Customer profile fetched successfully.",
            "customer_id": customer.customer_id,
            "profile_data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # # ✅ Prevent re-updating profile
        # if customer.is_profile_updated:
        #     return Response({
        #         "message": "Customer profile has already been updated."
        #     }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomerSerializer(customer, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # ✅ Update the flag AFTER serializer.save()
            customer.is_profile_updated = True
            customer.save(update_fields=["is_profile_updated"])

            return Response({
                "message": "Customer profile updated successfully.",
                "customer_id": customer.customer_id,
                "updated_data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Validation error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class UpdateMerchantProfileAPIView(APIView):
    """API to update merchant profile"""
    
    def get(self, request, merchant_id):
        """
        Get the profile of a specific merchant using merchant_id.
        """
        merchant = get_object_or_404(Merchant, merchant_id=merchant_id)
        serializer = MerchantSerializer(merchant)
        return Response({
            "message": "Merchant profile fetched successfully.",
            "merchant_id": merchant.merchant_id,
            "profile_data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, merchant_id):
        """
        Partially update merchant details.
        Only the fields provided in the request will be updated.
        """
        merchant = get_object_or_404(Merchant, merchant_id=merchant_id)
        
        serializer = MerchantSerializer(merchant, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # ✅ Set is_profile_updated to True
            merchant.is_profile_updated = True
            merchant.save(update_fields=["is_profile_updated"])

            return Response({
                "message": "Merchant profile updated successfully.",
                "merchant_id": merchant.merchant_id,
                "updated_data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Validation error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class CustomerMerchantPointsAPIView(APIView):
    """
    API to fetch all merchant-wise points for a given customer with PIN validation.
    """

    def post(self, request):
        # Extract customer_id and pin from the request body
        customer_id = request.data.get("customer_id")
        pin = request.data.get("pin")

        # Validate customer_id and pin
        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
            return Response({"error": "Please enter the correct customer ID."}, status=status.HTTP_404_NOT_FOUND)

        if str(customer.pin) != str(pin):
            return Response({"error": "Please enter the correct PIN."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch points from CustomerPoints table grouped by merchants
        customer_points = CustomerPoints.objects.filter(customer=customer).values(
            "merchant__merchant_id", "merchant__shop_name", "points"
        )

        # Prepare response data
        merchant_points_data = [
            {
                "merchant_id": cp["merchant__merchant_id"],
                "merchant_name": cp["merchant__shop_name"],
                "points": cp["points"]
            }
            for cp in customer_points
        ]

        return Response({
            "customer_id": customer_id,
            "merchant_points": merchant_points_data
        }, status=status.HTTP_200_OK)
        
        
class MerchantCustomerPointsAPIView(APIView):
    """
    API to fetch all customer-wise points for a given merchant with PIN validation.
    """

    def post(self, request):
        merchant_id = request.data.get("merchant_id")
        pin = request.data.get("pin")

        # Validate merchant
        merchant = Merchant.objects.filter(merchant_id=merchant_id).first()
        if not merchant:
            return Response({"error": "Please enter the correct merchant ID."}, status=status.HTTP_404_NOT_FOUND)

        if str(merchant.pin) != str(pin):
            return Response({"error": "Please enter the correct PIN."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch customer points related to this merchant
        customer_points = CustomerPoints.objects.filter(merchant=merchant).values(
            "customer__customer_id", "customer__first_name", "customer__last_name", "points"
        )

        # Prepare response
        customer_points_data = [
            {
                "customer_id": cp["customer__customer_id"],
                "customer_name": f"{cp['customer__first_name']} {cp['customer__last_name']}".strip(),
                "points": cp["points"]
            }
            for cp in customer_points
        ]

        return Response({
            "merchant_id": merchant_id,
            "customer_points": customer_points_data
        }, status=status.HTTP_200_OK)


class MerchantPointsAPIView(APIView):
    """
    API to fetch all points for a given merchant from the MerchantPoints table.
    """

    def get(self, request, merchant_id):
        # Fetch the merchant
        merchant = get_object_or_404(Merchant, merchant_id=merchant_id)

        # Fetch points from MerchantPoints table
        merchant_points = MerchantPoints.objects.filter(merchant=merchant).values(
            "points", "created_at"
        )

        # Prepare response data
        points_data = [
            {
                "points": mp["points"],
                "created_at": mp["created_at"]
            }
            for mp in merchant_points
        ]

        return Response({
            "merchant_id": merchant_id,
            "points_data": points_data
        }, status=status.HTTP_200_OK)
    

# List all or create new payment
class PaymentDetailsListCreateAPIView(APIView):
    def get(self, request):
        payments = PaymentDetails.objects.all().order_by('-created_at')
        serializer = PaymentDetailsSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Payment send successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"errors": serializer.errors, "message": "Payment send failed."},
            status=status.HTTP_400_BAD_REQUEST
        )


class TerminalCustomerPointsAPIView(APIView):
    """
    API to fetch all customer-wise points for a given terminal (under merchant) with TID and PIN validation (PIN from Terminal).
    """
    
    def get(self, request):
        terminal_id = request.query_params.get('terminal_id')

        if not terminal_id:
            return Response({"error": "terminal_id is required as query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Validate Terminal and fetch associated Merchant
        terminal = Terminal.objects.select_related('merchant_id').filter(terminal_id=terminal_id).first()
        if not terminal:
            return Response({"error": "Terminal not found."}, status=status.HTTP_404_NOT_FOUND)

        merchant = terminal.merchant_id

        # Step 2: Calculate total customer points related to this merchant
        total_points = CustomerPoints.objects.filter(merchant=merchant).aggregate(total_points=Sum('points'))['total_points'] or 0

        return Response({
            "terminal_id": terminal.terminal_id,
            "merchant_id": merchant.merchant_id,
            "total_points": total_points
        }, status=status.HTTP_200_OK)
        
        
    def post(self, request):
        terminal_id = request.data.get('terminal_id')
        merchant_identifier = request.data.get('merchant_id')
        pin = request.data.get('tid_pin')   # <-- use tid_pin here

        if not terminal_id or not merchant_identifier or not pin:
            return Response(
                {"error": "terminal_id, merchant_id, and tid_pin are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 1: Validate Merchant
        try:
            merchant = Merchant.objects.get(merchant_id=merchant_identifier)
        except Merchant.DoesNotExist:
            return Response({"error": "Please enter the correct merchant ID."}, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Validate Terminal under Merchant
        terminal = Terminal.objects.filter(terminal_id=terminal_id, merchant_id=merchant.id).first()
        if not terminal:
            return Response({"error": "Terminal not found for this merchant."}, status=status.HTTP_404_NOT_FOUND)

        # Step 3: Validate PIN from Terminal
        if str(terminal.tid_pin) != str(pin):
            return Response({"error": "Please enter the correct Terminal PIN."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Fetch Customer Points related to this merchant
        customer_points = CustomerPoints.objects.filter(merchant=merchant).values(
            "customer__customer_id", "customer__first_name", "customer__last_name", "points"
        )

        customer_points_data = [
            {
                "customer_id": cp["customer__customer_id"],
                "customer_name": f"{cp['customer__first_name']} {cp['customer__last_name']}".strip(),
                "points": cp["points"]
            }
            for cp in customer_points
        ]

        return Response({
            "merchant_id": merchant.merchant_id,
            "terminal_id": terminal.terminal_id,
            "tid_pin": terminal.tid_pin,
            "customer_points": customer_points_data
        }, status=status.HTTP_200_OK)

# Retrieve, update, or delete a specific payment
class PaymentDetailsRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, merchant_id):
        # Try to find the Merchant based on the merchant_id string
        try:
            merchant = Merchant.objects.get(merchant_id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({"error": "Merchant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter the PaymentDetails by the Merchant's ID and order by newest first
        payments = PaymentDetails.objects.filter(merchant=merchant).order_by('-created_at')

        if not payments.exists():  # Better than `if not payments:`
            return Response({"error": "No payment details found for this merchant."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the list of payments
        serializer = PaymentDetailsSerializer(payments, many=True)
        return Response(serializer.data)


    def put(self, request, merchant_id):
        # Update the payment details using merchant_id (string) and pk in the request
        try:
            payment = PaymentDetails.objects.get(merchant_id=merchant_id, pk=request.data.get('pk'))
        except PaymentDetails.DoesNotExist:
            return Response({"error": "Payment detail not found for this merchant."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentDetailsSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, merchant_id):
        # Delete the payment details using merchant_id (string) and pk in the request
        try:
            payment = PaymentDetails.objects.get(merchant_id=merchant_id, pk=request.data.get('pk'))
        except PaymentDetails.DoesNotExist:
            return Response({"error": "Payment detail not found for this merchant."}, status=status.HTTP_404_NOT_FOUND)
        
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BankDetailByUserAPIView(APIView):
    """
    Retrieve, create, and update bank details by user type and ID.
    URL format: /api/bank-details/<id>/<user_type>/
    Example: /api/bank-details/1/merchant/ or /api/bank-details/2/customer/
    """
    permission_classes = []

    def get(self, request, id, user_type):
        if user_type == "merchant":
            try:
                merchant = Merchant.objects.get(merchant_id=id)
            except Merchant.DoesNotExist:
                return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)
            bank_details = BankDetail.objects.filter(merchant=merchant)

        elif user_type == "customer":
            try:
                customer = Customer.objects.get(customer_id=id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            bank_details = BankDetail.objects.filter(customer=customer)

        else:
            return Response({"error": "Invalid user_type. Must be 'merchant' or 'customer'."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not bank_details.exists():
            return Response({"message": "No bank details found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BankDetailSerializer(bank_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, id, user_type):
        data = request.data.copy()

        if user_type == "merchant":
            try:
                merchant = Merchant.objects.get(merchant_id=id)
            except Merchant.DoesNotExist:
                return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)
            data['merchant'] = merchant.id
            data['customer'] = None

        elif user_type == "customer":
            try:
                customer = Customer.objects.get(customer_id=id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            data['customer'] = customer.customer_id
            data['merchant'] = None

        else:
            return Response({"error": "Invalid user_type. Must be 'merchant' or 'customer'."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = BankDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Bank details added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id, user_type):
        data = request.data.copy()

        # Fetch existing bank details based on the user type and ID
        if user_type == "merchant":
            try:
                merchant = Merchant.objects.get(merchant_id=id)
                bank_detail = BankDetail.objects.get(merchant=merchant)
            except Merchant.DoesNotExist:
                return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)
            except BankDetail.DoesNotExist:
                return Response({"error": "Bank details not found for this merchant"}, status=status.HTTP_404_NOT_FOUND)
            
            # Use merchant database ID for updating
            data['merchant'] = merchant.id
            data['customer'] = None

        elif user_type == "customer":
            try:
                customer = Customer.objects.get(customer_id=id)
                bank_detail = BankDetail.objects.get(customer=customer)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            except BankDetail.DoesNotExist:
                return Response({"error": "Bank details not found for this customer"}, status=status.HTTP_404_NOT_FOUND)
            
            # Use customer database ID for updating
            data['customer'] = customer.id
            data['merchant'] = None

        else:
            return Response({"error": "Invalid user_type. Must be 'merchant' or 'customer'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Important: Partial update if not all fields are provided
        serializer = BankDetailSerializer(bank_detail, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Bank details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    
class HelpAPIView(APIView):
    """
    API View to handle Help requests (Customer, Merchant or Terminal)
    """

    def get(self, request):
        help_requests = Help.objects.all().order_by('-created_at')
        serializer = HelpSerializer(help_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        customer_id = data.get("customer")
        merchant_id = data.get("merchant")
        terminal_id = data.get("terminal")

        merchant = None  # we'll store merchant object here

        # Handle Customer (optional)
        if customer_id and customer_id != "null":
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                data["customer"] = customer.customer_id
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data["customer"] = None

        # Handle Merchant (optional)
        if merchant_id and merchant_id != "null":
            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
            except Merchant.DoesNotExist:
                try:
                    merchant = Merchant.objects.get(merchant_code=merchant_id)
                except Merchant.DoesNotExist:
                    return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)

            data["merchant"] = merchant.id
        else:
            data["merchant"] = None


        # Handle Terminal (optional)
        if terminal_id and terminal_id != "null":
            try:
                terminal = Terminal.objects.get(terminal_id=terminal_id)
                # Ensure terminal belongs to same merchant (if merchant is passed)
                if merchant_id and terminal.merchant_id.id != merchant.id:
                    return Response({"error": "Terminal does not belong to the specified merchant."}, status=status.HTTP_400_BAD_REQUEST)
                data["terminal"] = terminal.id
            except Terminal.DoesNotExist:
                return Response({"error": "Terminal not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data["terminal"] = None


        serializer = HelpSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Help request submitted successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CorporateProjectListAPIView(APIView):
    """
    API View to get all project names from Corporate table
    """
    def get(self, request):
        projects = Corporate.objects.all().values('project_name').distinct()
        serializer = CorporateProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustomerPointsForPrepaidMerchantsAPIView(APIView):
    """
    API to list CustomerPoints ONLY for merchants having 'prepaid' plan.
    """

    def get(self, request):
        # Step 1: Get all merchants having 'prepaid' plan
        prepaid_merchants_qs = PaymentDetails.objects.filter(plan_type__iexact='prepaid').values_list('merchant_id', flat=True).distinct()
        
        # Step 2: Get CustomerPoints where merchant IN prepaid_merchants
        customer_points_qs = CustomerPoints.objects.filter(merchant_id__in=prepaid_merchants_qs)

        # Step 3: Prepare response
        data = []
        for entry in customer_points_qs:
            data.append({
                "customer_id": entry.customer.customer_id,
                "merchant_id": entry.merchant.merchant_id,
                "points": entry.points,
                "created_at": entry.created_at
            })

        return Response({"customer_points": data}, status=status.HTTP_200_OK)
    

class CashOutCreateAPIView(APIView):
    def post(self, request):
        serializer = CashOutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cash out created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerCashOutAPIView(APIView):
    def post(self, request):
        serializer = CustomerCashOutSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            merchant_id = serializer.validated_data['merchant_id']
            amount = serializer.validated_data['amount']

            # Fetch customer & merchant by code (not id)
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({"message": "Invalid customer ID"}, status=status.HTTP_404_NOT_FOUND)

            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
            except Merchant.DoesNotExist:
                return Response({"message": "Invalid merchant ID"}, status=status.HTTP_404_NOT_FOUND)

            try:
                customer_points = CustomerPoints.objects.get(customer=customer, merchant=merchant)
            except CustomerPoints.DoesNotExist:
                return Response({"message": "No points found for this customer and merchant."}, status=status.HTTP_404_NOT_FOUND)

            current_points = customer_points.points

            if amount > current_points:
                return Response({"message": f"Your amount is greater than your points ({current_points})."}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                customer_points.points -= amount
                customer_points.save()

                CashOut.objects.create(
                    user_category='Customer',
                    customer=customer,
                    merchant=merchant,
                    amount=amount
                )

                return Response({"message": "Cashout successful and points deducted."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MerchantCashOutAPIView(APIView):
    def post(self, request):
        serializer = MerchantCashOutSerializer(data=request.data)
        if serializer.is_valid():
            merchant_id = serializer.validated_data['merchant_id']
            amount = serializer.validated_data['amount']

            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
            except Merchant.DoesNotExist:
                return Response({"message": "Invalid merchant ID"}, status=status.HTTP_404_NOT_FOUND)

            try:
                merchant_points = MerchantPoints.objects.get(merchant=merchant)
            except MerchantPoints.DoesNotExist:
                return Response({"message": "No points found for this merchant."}, status=status.HTTP_404_NOT_FOUND)

            current_points = merchant_points.points

            if amount > current_points:
                return Response({"message": f"Your amount is greater than your points ({current_points})."}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                merchant_points.points -= amount
                merchant_points.save()

                CashOut.objects.create(
                    user_category='merchant',
                    merchant=merchant,
                    amount=amount
                )

                return Response({"message": "Cashout successful and points deducted."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




