from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ContactSerializer, LoanApplicationSerializer, PlaidLinkTokenSerializer, PlaidExchangeTokenSerializer
from .models import LoanApplication, BankAccount
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
import requests
import json

# Create your views here.

class ContactUsView(APIView):
    authentication_classes = []  # Disable CSRF for Swagger testing
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Contact With Us",
        operation_description="Fields: full_name, email, phone_number, subject, message",
        request_body=ContactSerializer,
        responses={
            201: openapi.Response("Message sent"),
            400: openapi.Response("Bad request (validation errors)")
        }
    )
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            subject = f"New Contact: {data.get('subject', 'No subject')} from {data.get('full_name') or 'Anonymous'}"
            message = f"""You received a new message from Contact form:\n\nName: {data.get('full_name')}\nPhone: {data.get('phone_number', '')}\nEmail: {data.get('email')}\nSubject: {data.get('subject')}\nMessage:\n{data.get('message')}"""
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            return Response({"message": "Your message has been sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoanApplicationCreateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Create Loan Application",
        request_body=LoanApplicationSerializer,
        responses={201: openapi.Response('Created'), 400: openapi.Response('Bad Request')}
    )
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save()
            # send email to app email with all fields
            message = (
                f"Name: {loan.full_name}\n"
                f"Email: {loan.email}\n"
                f"Phone: {loan.phone_number}\n"
                f"Property ZIP: {loan.property_zip_code}\n"
                f"Property Address: {loan.property_address}\n"
                f"Loan Purpose: {loan.loan_purpose}\n"
                f"Purchase Price: {loan.purchase_price}\n"
                f"Down Payment: {loan.down_payment}\n"
                f"Cash Out Amount: {loan.cash_out_amount if loan.cash_out_amount is not None else 'N/A'}\n"
                f"Annual Income: {loan.annual_income}\n"
            )
            subject = f"New Loan Application from {loan.full_name}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
            return Response({"id": loan.id, "message": "Loan application created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaidCreateLinkTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Create Plaid Link Token",
        request_body=PlaidLinkTokenSerializer,
        responses={200: openapi.Response('Link token created'), 400: openapi.Response('Bad Request')}
    )
    def post(self, request):
        serializer = PlaidLinkTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                loan_app = LoanApplication.objects.get(id=serializer.validated_data['loan_application_id'])
                
                # Plaid API call to create link token
                url = f"https://{settings.PLAID_ENV}.plaid.com/link/token/create"
                headers = {
                    'Content-Type': 'application/json',
                }
                data = {
                    'client_id': settings.PLAID_CLIENT_ID,
                    'secret': settings.PLAID_SECRET,
                    'client_name': 'Loan Application',
                    'country_codes': ['US'],
                    'language': 'en',
                    'user': {
                        'client_user_id': str(loan_app.id)
                    },
                    'products': ['transactions']
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(data))
                response_data = response.json()
                
                if response.status_code == 200:
                    return Response({
                        'link_token': response_data['link_token'],
                        'expiration': response_data['expiration']
                    })
                else:
                    return Response({'error': response_data}, status=400)
                    
            except LoanApplication.DoesNotExist:
                return Response({'error': 'Loan application not found'}, status=404)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response(serializer.errors, status=400)


class PlaidExchangeTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Exchange Plaid Public Token",
        request_body=PlaidExchangeTokenSerializer,
        responses={200: openapi.Response('Token exchanged and accounts retrieved'), 400: openapi.Response('Bad Request')}
    )
    def post(self, request):
        serializer = PlaidExchangeTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                loan_app = LoanApplication.objects.get(id=serializer.validated_data['loan_application_id'])
                
                # Exchange public token for access token
                url = f"https://{settings.PLAID_ENV}.plaid.com/item/public_token/exchange"
                headers = {'Content-Type': 'application/json'}
                data = {
                    'client_id': settings.PLAID_CLIENT_ID,
                    'secret': settings.PLAID_SECRET,
                    'public_token': serializer.validated_data['public_token']
                }
                
                exchange_response = requests.post(url, headers=headers, data=json.dumps(data))
                exchange_data = exchange_response.json()
                
                if exchange_response.status_code != 200:
                    return Response({'error': exchange_data}, status=400)
                
                access_token = exchange_data['access_token']
                item_id = exchange_data['item_id']
                
                # Get account information
                accounts_url = f"https://{settings.PLAID_ENV}.plaid.com/accounts/get"
                accounts_data = {
                    'client_id': settings.PLAID_CLIENT_ID,
                    'secret': settings.PLAID_SECRET,
                    'access_token': access_token
                }
                
                accounts_response = requests.post(accounts_url, headers=headers, data=json.dumps(accounts_data))
                accounts_result = accounts_response.json()
                
                if accounts_response.status_code != 200:
                    return Response({'error': accounts_result}, status=400)
                
                # Save access token and item ID to loan application
                loan_app.plaid_access_token = access_token
                loan_app.plaid_item_id = item_id
                loan_app.bank_connected = True
                loan_app.save()
                
                # Save bank accounts
                for account in accounts_result['accounts']:
                    BankAccount.objects.create(
                        loan_application=loan_app,
                        account_id=account['account_id'],
                        account_name=account['name'],
                        account_type=account['type'],
                        account_subtype=account['subtype'],
                        balance=account['balances']['current']
                    )
                
                # Send updated email with bank info
                bank_info = "\n".join([
                    f"Account: {acc['name']} ({acc['type']}) - Balance: ${acc['balances']['current']}"
                    for acc in accounts_result['accounts']
                ])
                
                message = (
                    f"UPDATED: Bank Account Connected\n\n"
                    f"Name: {loan_app.full_name}\n"
                    f"Email: {loan_app.email}\n"
                    f"Phone: {loan_app.phone_number}\n"
                    f"Property ZIP: {loan_app.property_zip_code}\n"
                    f"Property Address: {loan_app.property_address}\n"
                    f"Loan Purpose: {loan_app.loan_purpose}\n"
                    f"Purchase Price: {loan_app.purchase_price}\n"
                    f"Down Payment: {loan_app.down_payment}\n"
                    f"Cash Out Amount: {loan_app.cash_out_amount if loan_app.cash_out_amount is not None else 'N/A'}\n"
                    f"Annual Income: {loan_app.annual_income}\n\n"
                    f"BANK ACCOUNTS:\n{bank_info}\n"
                )
                
                subject = f"UPDATED: Bank Connected - {loan_app.full_name}"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
                
                return Response({
                    'message': 'Bank account connected successfully',
                    'accounts': accounts_result['accounts']
                })
                
            except LoanApplication.DoesNotExist:
                return Response({'error': 'Loan application not found'}, status=404)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response(serializer.errors, status=400)
