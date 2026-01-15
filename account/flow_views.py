# Complete Plaid Integration Flow - Step by Step
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from .models import LoanApplication, PlaidConnection
from .plaid_service import PlaidService
from .serializers import LoanApplicationSerializer, PlaidLinkSerializer
import logging

logger = logging.getLogger(__name__)


class Step1CreateLoanWithLinkTokenView(APIView):
    """Step 1: Create loan application and get link token"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="STEP 1: Create Loan + Get Link Token",
        operation_description="Creates loan application and returns Plaid link token for bank connection",
        request_body=LoanApplicationSerializer,
        responses={
            201: openapi.Response(
                "Success",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'step': openapi.Schema(type=openapi.TYPE_STRING, default="1"),
                        'loan_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'link_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'next_step': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save()
            
            try:
                plaid_service = PlaidService()
                link_token = plaid_service.create_link_token(loan.id, loan.full_name)
                
                return Response({
                    'step': '1',
                    'loan_id': loan.id,
                    'link_token': link_token,
                    'message': 'Loan application created successfully!',
                    'next_step': 'Use link_token with Plaid Link to get public_token, then call Step 2'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error creating link token: {e}")
                return Response({
                    'step': '1',
                    'loan_id': loan.id,
                    'error': f'Loan created but link token failed: {str(e)}'
                }, status=status.HTTP_201_CREATED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Step2ExchangeTokenGetAccountsView(APIView):
    """Step 2: Exchange public_token for access_token and get account info"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="STEP 2: Exchange Token + Get Accounts",
        operation_description="Exchange public_token for access_token and retrieve bank accounts",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'loan_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'public_token': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['loan_id', 'public_token']
        ),
        responses={
            200: openapi.Response(
                "Success",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'step': openapi.Schema(type=openapi.TYPE_STRING, default="2"),
                        'loan_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'accounts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'next_step': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def post(self, request):
        loan_id = request.data.get('loan_id')
        public_token = request.data.get('public_token')
        
        if not loan_id or not public_token:
            return Response({
                'error': 'loan_id and public_token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            loan = get_object_or_404(LoanApplication, id=loan_id)
            plaid_service = PlaidService()
            
            # Exchange public token for access token
            token_data = plaid_service.exchange_public_token(public_token)
            access_token = token_data['access_token']
            item_id = token_data['item_id']
            
            # Save Plaid connection
            plaid_connection, created = PlaidConnection.objects.get_or_create(
                loan_application=loan,
                defaults={
                    'access_token': access_token,
                    'item_id': item_id
                }
            )
            
            if not created:
                plaid_connection.access_token = access_token
                plaid_connection.item_id = item_id
                plaid_connection.save()
            
            # Get accounts
            accounts = plaid_service.get_accounts(access_token)
            
            return Response({
                'step': '2',
                'loan_id': loan_id,
                'access_token': access_token,
                'accounts': accounts,
                'message': 'Access token obtained and accounts retrieved successfully!',
                'next_step': 'Call Step 3 to get complete loan + bank data'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in step 2: {e}")
            return Response({
                'error': f'Step 2 failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Step3GetCompleteDataView(APIView):
    """Step 3: Get complete loan application + bank account data"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="STEP 3: Get Complete Loan + Bank Data",
        operation_description="Get complete loan application with all bank account information and balances",
        responses={
            200: openapi.Response(
                "Complete Data",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'step': openapi.Schema(type=openapi.TYPE_STRING, default="3"),
                        'loan_application': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'bank_accounts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'total_balance': openapi.Schema(type=openapi.TYPE_STRING),
                        'transactions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    }
                )
            )
        }
    )
    def get(self, request, loan_id):
        try:
            loan = get_object_or_404(LoanApplication, id=loan_id)
            plaid_connection = get_object_or_404(PlaidConnection, loan_application=loan)
            
            plaid_service = PlaidService()
            
            # Get accounts with fresh data
            accounts = plaid_service.get_accounts(plaid_connection.access_token)
            
            # Format accounts and calculate total balance
            formatted_accounts = []
            total_balance = 0
            
            for account in accounts:
                balances = account.get('balances', {})
                current_balance = balances.get('current', 0) or 0
                available_balance = balances.get('available', 0) or 0
                
                formatted_account = {
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'official_name': account.get('official_name', ''),
                    'type': account['type'],
                    'subtype': account.get('subtype', ''),
                    'current_balance': float(current_balance),
                    'available_balance': float(available_balance),
                    'currency': balances.get('iso_currency_code', 'USD')
                }
                
                formatted_accounts.append(formatted_account)
                total_balance += current_balance
            
            # Get transactions
            try:
                transactions = plaid_service.get_transactions(plaid_connection.access_token)
                formatted_transactions = []
                
                for transaction in transactions[:10]:  # Last 10 transactions
                    formatted_transactions.append({
                        'transaction_id': transaction['transaction_id'],
                        'account_id': transaction['account_id'],
                        'amount': float(transaction['amount']),
                        'date': transaction['date'],
                        'name': transaction['name'],
                        'category': transaction.get('category', [])
                    })
                    
            except Exception as e:
                logger.warning(f"Could not fetch transactions: {e}")
                formatted_transactions = []
            
            # Complete response
            return Response({
                'step': '3',
                'loan_application': {
                    'id': loan.id,
                    'full_name': loan.full_name,
                    'email': loan.email,
                    'phone_number': loan.phone_number,
                    'property_zip_code': loan.property_zip_code,
                    'property_address': loan.property_address,
                    'annual_income': str(loan.annual_income),
                    'purchase_price': str(loan.purchase_price),
                    'down_payment': str(loan.down_payment),
                    'loan_purpose': loan.loan_purpose,
                    'cash_out_amount': str(loan.cash_out_amount) if loan.cash_out_amount else None,
                    'created_at': loan.created_at.isoformat() if hasattr(loan, 'created_at') else None
                },
                'bank_accounts': formatted_accounts,
                'total_balance': f"${total_balance:,.2f}",
                'transactions': formatted_transactions,
                'message': 'Complete loan and bank data retrieved successfully!'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in step 3: {e}")
            return Response({
                'error': f'Step 3 failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickSandboxFlowView(APIView):
    """Quick Sandbox Flow: Create everything at once for testing"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="QUICK SANDBOX: Complete Flow",
        operation_description="Creates loan, generates sandbox public token, and returns all data in one call",
        request_body=LoanApplicationSerializer,
        responses={
            201: openapi.Response(
                "Complete Sandbox Data",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'loan_application': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'bank_accounts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'total_balance': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def post(self, request):
        try:
            # Step 1: Create loan
            serializer = LoanApplicationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            loan = serializer.save()
            
            # Step 2: Create sandbox public token
            plaid_service = PlaidService()
            sandbox_response = plaid_service.create_sandbox_public_token()
            public_token = sandbox_response['public_token']
            
            # Step 3: Exchange for access token
            token_data = plaid_service.exchange_public_token(public_token)
            access_token = token_data['access_token']
            item_id = token_data['item_id']
            
            # Step 4: Save connection
            PlaidConnection.objects.create(
                loan_application=loan,
                access_token=access_token,
                item_id=item_id
            )
            
            # Step 5: Get accounts and format data
            accounts = plaid_service.get_accounts(access_token)
            
            formatted_accounts = []
            total_balance = 0
            
            for account in accounts:
                balances = account.get('balances', {})
                current_balance = balances.get('current', 0) or 0
                
                formatted_account = {
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'type': account['type'],
                    'current_balance': float(current_balance),
                    'currency': balances.get('iso_currency_code', 'USD')
                }
                
                formatted_accounts.append(formatted_account)
                total_balance += current_balance
            
            return Response({
                'loan_application': {
                    'id': loan.id,
                    'full_name': loan.full_name,
                    'email': loan.email,
                    'annual_income': str(loan.annual_income),
                    'loan_purpose': loan.loan_purpose,
                },
                'bank_accounts': formatted_accounts,
                'total_balance': f"${total_balance:,.2f}",
                'message': 'Complete sandbox flow executed successfully!'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Quick sandbox flow error: {e}")
            return Response({
                'error': f'Sandbox flow failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
