import random
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import F
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import CustomerSerializer, MerchantSerializer
from bopo_admin.models import DeductSetting

from .serializers import BankDetailSerializer, CorporateProjectSerializer, HelpSerializer, PaymentDetailsSerializer

from .models import BankDetail, CustomerToCustomer, Help, MerchantToMerchant, PaymentDetails
from accounts.models import Corporate, Customer, Merchant
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
    API for Merchant to Customer point transfer (No deduction).
    """

    def post(self, request):
        customer_id = request.data.get('customer_id')
        customer_mobile = request.data.get('customer_mobile')
        merchant_id = request.data.get('merchant_id')
        merchant_mobile = request.data.get('merchant_mobile')
        points = int(request.data.get('points', 0))

        if points <= 0:
            return Response({'error': 'Points must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch customer
        try:
            if customer_id:
                customer = Customer.objects.get(customer_id=customer_id)
            elif customer_mobile:
                customer = Customer.objects.get(mobile=customer_mobile)
            else:
                return Response({'error': 'Customer ID or mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Fetch or create merchant
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
            'merchant_mobile': merchant.mobile
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
    API for transferring points from one customer to another (5% deduction).
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

        # Debugging logs
        print(f"Sender: {sender_customer.customer_id}, Available Points: {sender_points}")
        print(f"Receiver: {receiver_customer.customer_id}")
        print(f"Merchant: {merchant.merchant_id}")
        print(f"Requested Transfer: {points}")

        # Validate points
        if sender_points < points:
            return Response({
                "error": "Insufficient points for transfer",
                "available_points": sender_points,
                "requested_points": points
            }, status=status.HTTP_400_BAD_REQUEST)

        # Apply 5% deduction
        points_after_deduction = int(points * 0.95)

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

        # Save transaction
        CustomerToCustomer.objects.create(
            sender_customer=sender_customer,
            receiver_customer=receiver_customer,
            merchant=merchant,
            points=points_after_deduction
        )

        return Response({
            "message": "Points transferred successfully",
            "points_transferred": points_after_deduction,
            "sender_balance": sender_entry.points,
            "receiver_balance": receiver_entry.points
        }, status=status.HTTP_200_OK)
   
class MerchantToMerchantTransferAPIView(APIView):
    """
    API for Merchant to Merchant point transfer (5% deduction).
    """

    def post(self, request):
        sender_merchant_id = request.data.get("sender_merchant_id")
        receiver_merchant_id = request.data.get("receiver_merchant_id")
        points = int(request.data.get("points", 0))

        if points <= 0:
            return Response({"error": "Points must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender_merchant = Merchant.objects.get(merchant_id=sender_merchant_id)
            receiver_merchant = Merchant.objects.get(merchant_id=receiver_merchant_id)
        except Merchant.DoesNotExist:
            return Response({"error": "Invalid sender or receiver merchant ID"}, status=status.HTTP_404_NOT_FOUND)

        sender_points = MerchantPoints.objects.filter(merchant=sender_merchant).first()

        if not sender_points or sender_points.points < points * 1.05:
            return Response({"error": "Insufficient points for transfer"}, status=status.HTTP_400_BAD_REQUEST)

        # Apply deduction
        points_after_deduction = points * 0.95

        # Deduct from sender
        MerchantPoints.objects.filter(merchant=sender_merchant).update(points=F("points") - points * 1.05)

        # Credit to receiver
        receiver_points, created = MerchantPoints.objects.get_or_create(
            merchant=receiver_merchant,
            defaults={"points": points_after_deduction}
        )

        if not created:
            MerchantPoints.objects.filter(merchant=receiver_merchant).update(points=F("points") + points_after_deduction)

        # Update or create transaction history
        merchant_transfer, created = MerchantToMerchant.objects.get_or_create(
            sender_merchant=sender_merchant,
            receiver_merchant=receiver_merchant,
            defaults={"points": points}
        )

        if not created:
            merchant_transfer.points = F("points") + points
            merchant_transfer.save()

        updated_sender_balance = MerchantPoints.objects.get(merchant=sender_merchant).points
        updated_receiver_balance = MerchantPoints.objects.get(merchant=receiver_merchant).points

        return Response(
            {
                "message": "Points transferred successfully",
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve, update, or delete a specific payment
class PaymentDetailsRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, pk):
        payment = get_object_or_404(PaymentDetails, pk=pk)
        serializer = PaymentDetailsSerializer(payment)
        return Response(serializer.data)

    def put(self, request, pk):
        payment = get_object_or_404(PaymentDetails, pk=pk)
        serializer = PaymentDetailsSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payment = get_object_or_404(PaymentDetails, pk=pk)
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
            data['customer'] = customer.customer_id
            data['merchant'] = None

        else:
            return Response({"error": "Invalid user_type. Must be 'merchant' or 'customer'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update bank details if found
        serializer = BankDetailSerializer(bank_detail, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Bank details updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class HelpAPIView(APIView):
    """
    API View to handle Help requests
    """

    def get(self, request):
        help_requests = Help.objects.all().order_by('-created_at')
        serializer = HelpSerializer(help_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        customer_id = data.get("customer")
        merchant_id = data.get("merchant")

        if customer_id and customer_id != "null":
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                data["customer"] = customer.customer_id
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data["customer"] = None

        if merchant_id and merchant_id != "null":
            try:
                merchant = Merchant.objects.get(merchant_id=merchant_id)
                data["merchant"] = merchant.id
            except Merchant.DoesNotExist:
                return Response({"error": "Merchant not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data["merchant"] = None

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
