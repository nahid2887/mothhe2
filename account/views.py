from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ContactSerializer, LoanApplicationSerializer, PlaidLinkSerializer
from .models import LoanApplication, PlaidConnection
from .plaid_service import PlaidService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import logging
from datetime import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io
import os
from dotenv import load_dotenv
from .aiengine import PreApprovalEngine

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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
        operation_summary="📝 Create Loan Application (Step 1 of 3)",
        operation_description="""
        Create a new loan application and receive a Plaid link token.
        
        **Step 1 - Create Application:**
        - User submits their loan information
        - API validates and stores the application
        - API generates a Plaid link_token
        - Returns plaid_ui_url for opening Plaid Link
        
        **What to do with the response:**
        1. Save the loan application ID (id field)
        2. Open the plaid_ui_url in a browser (or use the link_token with your own Plaid Link UI)
        3. User logs into their real bank account
        4. Proceed to Step 2: Exchange public token at /api/plaid/connect/
        
        **After this step:**
        - ✅ Loan application created
        - ✅ Ready for bank connection
        - ✅ Plaid UI link ready
        
        **Next:** Open plaid_ui_url and connect bank account
        """,
        request_body=LoanApplicationSerializer,
        responses={
            201: openapi.Response(
                "Loan application created successfully - Ready for Plaid Link",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=57, description='Loan Application ID - Use this for next steps'),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, example='Mr Kim'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@example.com'),
                        'plaid_link_token': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example='link-production-xxx...',
                            description="Link token for Plaid Link UI - Expires in 10 minutes"
                        ),
                        'plaid_ui_url': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='http://localhost:5173/plaid-link-page?token=link-xxx&loan_id=57',
                            description='Direct URL to open Plaid Link (ready to use in browser)'
                        ),
                        'user_input': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                'property_zip': openapi.Schema(type=openapi.TYPE_STRING),
                                'property_address': openapi.Schema(type=openapi.TYPE_STRING),
                                'loan_purpose': openapi.Schema(type=openapi.TYPE_STRING, example='Purchase'),
                                'purchase_price': openapi.Schema(type=openapi.TYPE_STRING, example='500000'),
                                'down_payment': openapi.Schema(type=openapi.TYPE_STRING, example='100000'),
                            }
                        ),
                        'instructions': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='Copy the plaid_ui_url and open it in your browser. Login to your bank to get the public token.'
                        ),
                    }
                )
            ),
            400: openapi.Response(
                'Bad Request - Validation errors',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'field': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save()
            
            # Send email notification
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
            
            # Prepare user_input data for response
            user_input = {
                "full_name": loan.full_name,
                "email": loan.email,
                "phone": loan.phone_number,
                "property_zip": loan.property_zip_code,
                "property_address": loan.property_address,
                "loan_purpose": loan.loan_purpose,
                "purchase_price": str(loan.purchase_price),
                "down_payment": str(loan.down_payment) if loan.down_payment else "$0"
            }
            
            # Create Plaid link token for step 2
            try:
                plaid_service = PlaidService()
                link_token = plaid_service.create_link_token(loan.id, loan.full_name)
                
                # Only create sandbox public token in non-production environments
                if settings.PLAID_ENV in ['sandbox', 'development']:
                    try:
                        public_token_data = plaid_service.create_sandbox_public_token()
                        public_token = public_token_data['public_token']
                        
                        # Save both tokens to the loan application
                        loan.plaid_link_token = link_token
                        loan.plaid_public_token = public_token
                        loan.save()
                        
                        return Response({
                            'id': loan.id,
                            'full_name': loan.full_name,
                            'email': loan.email,
                            'plaid_link_token': link_token,
                            'plaid_public_token': public_token,  # Only in sandbox/development
                            'user_input': user_input,
                            'message': f'Loan application created successfully. Environment: {settings.PLAID_ENV}. You can use plaid_public_token directly with /plaid/connect/ endpoint OR plaid_link_token with Plaid Link UI.'
                        }, status=status.HTTP_201_CREATED)
                        
                    except Exception as pub_e:
                        logger.warning(f"Could not create sandbox public token: {pub_e}")
                        # Fall back to link token only
                        loan.plaid_link_token = link_token
                        loan.save()
                        
                        return Response({
                            'id': loan.id,
                            'full_name': loan.full_name,
                            'email': loan.email,
                            'plaid_link_token': link_token,
                            'user_input': user_input,
                            'message': f'Loan application created successfully. Environment: {settings.PLAID_ENV}. Use the plaid_link_token with Plaid Link UI to get public token.'
                        }, status=status.HTTP_201_CREATED)
                else:
                    # Production environment - only provide link token
                    loan.plaid_link_token = link_token
                    loan.save()
                    
                    # Create URL with pre-filled link token
                    plaid_ui_url = f'http://localhost:5173/plaid-link-page?token={link_token}&loan_id={loan.id}'
                    
                    return Response({
                        'id': loan.id,
                        'full_name': loan.full_name,
                        'email': loan.email,
                        'plaid_link_token': link_token,
                        'plaid_ui_url': plaid_ui_url,
                        'user_input': user_input,
                        'message': f'Loan application created successfully. Environment: {settings.PLAID_ENV}. NEXT STEP: Open plaid_ui_url in browser to get public token.',
                        'instructions': 'Copy the plaid_ui_url and open it in your browser. Login to your bank to get the public token.'
                    }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error creating Plaid link token: {e}")
                return Response({
                    'id': loan.id,
                    'full_name': loan.full_name,
                    'email': loan.email,
                    'user_input': user_input,
                    'error': 'Loan application created but unable to generate Plaid link token'
                }, status=status.HTTP_201_CREATED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaidConnectView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="🏦 Connect Bank Account (Step 2 of 3)",
        operation_description="""
        Exchange Plaid public token for access token and retrieve bank information.
        
        **Step-by-Step Process:**
        1. User gets link_token from /api/loan-application/ endpoint
        2. User opens Plaid Link UI and logs into their bank
        3. Plaid returns a public_token
        4. Send public_token here to exchange for access_token
        5. API fetches real bank account data
        
        **What happens:**
        - Exchanges public token for secure access_token
        - Retrieves all connected bank accounts
        - Fetches account balances
        - Retrieves recent transactions
        - Stores connection for future use
        
        **Response includes:**
        - ✅ Loan application details
        - ✅ All connected bank accounts with types
        - ✅ Account balances (current and available)
        - ✅ Recent transactions
        - ✅ Total balance across all accounts
        """,
        request_body=PlaidLinkSerializer,
        responses={
            200: openapi.Response(
                "Bank account connected successfully - Ready for PDF generation",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'loan_application': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Loan application details',
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'annual_income': openapi.Schema(type=openapi.TYPE_STRING),
                                'purchase_price': openapi.Schema(type=openapi.TYPE_STRING),
                                'down_payment': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'bank_accounts': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'account_id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'type': openapi.Schema(type=openapi.TYPE_STRING, example='depository'),
                                    'subtype': openapi.Schema(type=openapi.TYPE_STRING, example='checking'),
                                    'current_balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'available_balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'currency': openapi.Schema(type=openapi.TYPE_STRING, example='USD'),
                                }
                            ),
                            description='List of all connected bank accounts'
                        ),
                        'total_balance': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='$10,500.00',
                            description='Total balance across all accounts'
                        ),
                        'recent_transactions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                            description='Recent transactions from connected accounts'
                        ),
                        'plaid_connected': openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=True,
                            description='Status of Plaid connection'
                        ),
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Success message with next steps'
                        ),
                    }
                )
            ),
            400: openapi.Response(
                "Bad Request - Invalid public token or missing parameters",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Loan application not found",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = PlaidLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        public_token = serializer.validated_data['public_token']
        loan_application_id = serializer.validated_data['loan_application_id']
        
        try:
            # Get loan application
            loan_application = get_object_or_404(LoanApplication, id=loan_application_id)
            plaid_service = PlaidService()
            
            # Exchange tokens
            token_data = plaid_service.exchange_public_token(public_token)
            access_token = token_data['access_token']
            item_id = token_data['item_id']
            
            # Store Plaid connection
            plaid_connection, created = PlaidConnection.objects.get_or_create(
                loan_application=loan_application,
                defaults={
                    'access_token': access_token,
                    'item_id': item_id
                }
            )
            
            if not created:
                plaid_connection.access_token = access_token
                plaid_connection.item_id = item_id
                plaid_connection.save()
            
            # Get accounts information
            accounts = plaid_service.get_accounts(access_token)
            
            # Format account data
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
                    'type': str(account['type']),
                    'subtype': str(account.get('subtype', '')),
                    'current_balance': float(current_balance),
                    'available_balance': float(available_balance),
                    'currency': balances.get('iso_currency_code', 'USD')
                }
                
                formatted_accounts.append(formatted_account)
                total_balance += current_balance
            
            # Prepare response with all information (transactions not available - product not authorized)
            response_data = {
                'loan_application': {
                    'id': loan_application.id,
                    'full_name': loan_application.full_name,
                    'email': loan_application.email,
                    'phone_number': loan_application.phone_number,
                    'property_zip_code': loan_application.property_zip_code,
                    'property_address': loan_application.property_address,
                    'annual_income': str(loan_application.annual_income),
                    'purchase_price': str(loan_application.purchase_price),
                    'down_payment': str(loan_application.down_payment),
                    'loan_purpose': loan_application.loan_purpose,
                    'cash_out_amount': str(loan_application.cash_out_amount) if loan_application.cash_out_amount else None,
                    'created_at': loan_application.created_at.isoformat() if hasattr(loan_application, 'created_at') else None
                },
                'bank_accounts': formatted_accounts,
                'total_balance': f"${total_balance:,.2f}",
                'plaid_connected': True,
                'message': 'Bank account connected successfully!'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error connecting to Plaid: {e}")
            return Response(
                {"error": f"Unable to connect bank account: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetLoanApplicationWithBankDataView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get Complete Application Data",
        operation_description="Get loan application with connected bank account information",
        responses={
            200: openapi.Response("Application data with bank information"),
            404: openapi.Response("Loan Application not found")
        }
    )
    def get(self, request, loan_id):
        try:
            loan_application = get_object_or_404(LoanApplication, id=loan_id)
            
            # Check if Plaid is connected
            try:
                plaid_connection = PlaidConnection.objects.get(loan_application=loan_application)
                plaid_service = PlaidService()
                
                # Get fresh account data
                accounts = plaid_service.get_accounts(plaid_connection.access_token)
                
                formatted_accounts = []
                total_balance = 0
                
                for account in accounts:
                    balances = account.get('balances', {})
                    current_balance = balances.get('current', 0) or 0
                    
                    formatted_account = {
                        'account_id': account['account_id'],
                        'name': account['name'],
                        'official_name': account.get('official_name', ''),
                        'type': account['type'],
                        'subtype': account.get('subtype', ''),
                        'current_balance': float(current_balance),
                        'available_balance': float(balances.get('available', 0) or 0),
                        'currency': balances.get('iso_currency_code', 'USD')
                    }
                    
                    formatted_accounts.append(formatted_account)
                    total_balance += current_balance
                
                response_data = {
                    'loan_application': {
                        'id': loan_application.id,
                        'full_name': loan_application.full_name,
                        'email': loan_application.email,
                        'phone_number': loan_application.phone_number,
                        'property_zip_code': loan_application.property_zip_code,
                        'property_address': loan_application.property_address,
                        'annual_income': str(loan_application.annual_income),
                        'purchase_price': str(loan_application.purchase_price),
                        'down_payment': str(loan_application.down_payment),
                        'loan_purpose': loan_application.loan_purpose,
                        'cash_out_amount': str(loan_application.cash_out_amount) if loan_application.cash_out_amount else None,
                        'created_at': loan_application.created_at.isoformat() if hasattr(loan_application, 'created_at') else None
                    },
                    'bank_accounts': formatted_accounts,
                    'total_balance': f"${total_balance:,.2f}",
                    'plaid_connected': True
                }
                
            except PlaidConnection.DoesNotExist:
                # No Plaid connection found
                response_data = {
                    'loan_application': {
                        'id': loan_application.id,
                        'full_name': loan_application.full_name,
                        'email': loan_application.email,
                        'phone_number': loan_application.phone_number,
                        'property_zip_code': loan_application.property_zip_code,
                        'property_address': loan_application.property_address,
                        'annual_income': str(loan_application.annual_income),
                        'purchase_price': str(loan_application.purchase_price),
                        'down_payment': str(loan_application.down_payment),
                        'loan_purpose': loan_application.loan_purpose,
                        'cash_out_amount': str(loan_application.cash_out_amount) if loan_application.cash_out_amount else None,
                        'created_at': loan_application.created_at.isoformat() if hasattr(loan_application, 'created_at') else None
                    },
                    'bank_accounts': [],
                    'total_balance': "$0.00",
                    'plaid_connected': False,
                    'message': 'No bank account connected yet'
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving loan application: {e}")
            return Response(
                {"error": "Unable to retrieve application data"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlaidTestPageView(APIView):
    """Serve HTML page for testing Plaid integration"""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.http import FileResponse
        import os
        
        html_path = os.path.join(settings.BASE_DIR, 'plaid_test.html')
        return FileResponse(open(html_path, 'rb'), content_type='text/html')


class LoanDecisionTestPageView(APIView):
    """Serve HTML page for testing Loan Decision PDF generation"""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.http import FileResponse
        import os
        
        html_path = os.path.join(settings.BASE_DIR, 'loan_decision_test.html')
        return FileResponse(open(html_path, 'rb'), content_type='text/html')


class CreateTestLoanView(APIView):
    """Create a test loan application for PDF generation testing"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Create Test Loan Application",
        operation_description="Creates a test loan application that can be used to test PDF generation",
        responses={
            201: openapi.Response("Test loan created", examples={
                "application/json": {
                    "message": "Test loan application created successfully",
                    "loan_id": 1,
                    "test_pdf_url": "/api/loan-decision-pdf/1/",
                    "applicant_info": {
                        "full_name": "John Smith",
                        "email": "john.smith@example.com",
                        "purchase_price": "$455,000",
                        "down_payment": "$100,000"
                    }
                }
            }),
            400: openapi.Response("Bad request")
        }
    )
    def post(self, request):
        try:
            # Create test loan application with the same data as aiengine.py
            loan_app = LoanApplication.objects.create(
                full_name="John Smith",
                email="tdankha@midlandfederal.com",
                phone_number="123-456-7890",
                property_zip="19104",
                property_address="123 Main St, Pennsylvania",
                loan_purpose="Purchase",
                purchase_price="$455,000",
                down_payment="$100,000"
            )

            return Response({
                "message": "Test loan application created successfully",
                "loan_id": loan_app.id,
                "test_pdf_url": f"/api/loan-decision-pdf/{loan_app.id}/",
                "applicant_info": {
                    "full_name": loan_app.full_name,
                    "email": loan_app.email,
                    "phone": loan_app.phone_number,
                    "property_address": loan_app.property_address,
                    "purchase_price": loan_app.purchase_price,
                    "down_payment": loan_app.down_payment
                },
                "instructions": {
                    "next_step": f"Visit /api/loan-decision-pdf/{loan_app.id}/ to generate PDF",
                    "test_page": "/api/loan-decision-test/ to use the web interface"
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating test loan: {e}")
            return Response({
                'error': 'Unable to create test loan application'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlaidLinkTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get Plaid Link Token",
        operation_description="Get link token to initialize Plaid Link for bank connection",
        manual_parameters=[
            openapi.Parameter(
                'loan_application_id',
                openapi.IN_QUERY,
                description="Loan Application ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                "Link token created",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'link_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'loan_application_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Loan Application not found")
        }
    )
    def get(self, request):
        loan_application_id = request.query_params.get('loan_application_id')
        
        if not loan_application_id:
            return Response(
                {"error": "loan_application_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            loan_application = get_object_or_404(LoanApplication, id=loan_application_id)
            plaid_service = PlaidService()
            link_token = plaid_service.create_link_token(loan_application.id, loan_application.full_name)
            
            return Response({
                'link_token': link_token,
                'loan_application_id': loan_application.id,
                'instructions': 'Use this link_token with Plaid Link to connect bank account'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creating link token: {e}")
            return Response(
                {"error": "Unable to create link token"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlaidConnectAndGetAllInfoView(APIView):
    """Connect Plaid and get BOTH loan application info AND bank account data"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Connect Bank & Get All User Info",
        operation_description="Exchange Plaid public token and get complete user data: loan application + bank accounts + balances + transactions",
        request_body=PlaidLinkSerializer,
        responses={
            200: openapi.Response("Complete user information"),
            400: openapi.Response("Bad Request"),
            404: openapi.Response("Loan Application not found")
        }
    )
    def post(self, request):
        serializer = PlaidLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        public_token = serializer.validated_data['public_token']
        loan_application_id = serializer.validated_data['loan_application_id']
        
        try:
            # Get loan application
            loan_application = get_object_or_404(LoanApplication, id=loan_application_id)
            plaid_service = PlaidService()
            
            # Exchange tokens
            token_data = plaid_service.exchange_public_token(public_token)
            access_token = token_data['access_token']
            item_id = token_data['item_id']
            
            # Store Plaid connection
            plaid_connection, created = PlaidConnection.objects.get_or_create(
                loan_application=loan_application,
                defaults={
                    'access_token': access_token,
                    'item_id': item_id
                }
            )
            
            if not created:
                plaid_connection.access_token = access_token
                plaid_connection.item_id = item_id
                plaid_connection.save()
            
            # Get accounts information from Plaid
            accounts = plaid_service.get_accounts(access_token)
            
            # Format bank account data
            bank_accounts = []
            total_balance = 0
            checking_balance = 0
            savings_balance = 0
            
            for account in accounts:
                balances = account.get('balances', {})
                current_balance = balances.get('current', 0) or 0
                available_balance = balances.get('available', 0) or 0
                
                account_info = {
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'official_name': account.get('official_name', ''),
                    'type': str(account['type']),
                    'subtype': str(account.get('subtype', '')),
                    'current_balance': float(current_balance),
                    'available_balance': float(available_balance),
                    'currency': balances.get('iso_currency_code', 'USD'),
                    'balance_formatted': f"${current_balance:,.2f}"
                }
                
                bank_accounts.append(account_info)
                total_balance += current_balance
                
                # Categorize balances
                if account.get('subtype') == 'checking':
                    checking_balance += current_balance
                elif account.get('subtype') == 'savings':
                    savings_balance += current_balance
            
            # Transactions not available - product not authorized
            transactions = []
            
            # COMPLETE RESPONSE WITH ALL INFORMATION
            complete_user_data = {
                'loan_application_info': {
                    'id': loan_application.id,
                    'full_name': loan_application.full_name,
                    'email': loan_application.email,
                    'phone_number': loan_application.phone_number,
                    'property_details': {
                        'zip_code': loan_application.property_zip_code,
                        'address': loan_application.property_address
                    },
                    'loan_details': {
                        'purpose': loan_application.loan_purpose,
                        'purchase_price': f"${float(loan_application.purchase_price):,.2f}",
                        'down_payment': f"${float(loan_application.down_payment):,.2f}",
                        'cash_out_amount': f"${float(loan_application.cash_out_amount):,.2f}" if loan_application.cash_out_amount else None,
                        'annual_income': f"${float(loan_application.annual_income):,.2f}"
                    },
                    'application_date': loan_application.created_at.isoformat()
                },
                'bank_account_info': {
                    'accounts': bank_accounts,
                    'financial_summary': {
                        'total_balance': f"${total_balance:,.2f}",
                        'checking_balance': f"${checking_balance:,.2f}",
                        'savings_balance': f"${savings_balance:,.2f}",
                        'account_count': len(bank_accounts)
                    },
                    'recent_transactions': transactions,
                    'plaid_connection_status': 'Successfully connected'
                },
                'analysis': {
                    'monthly_income': f"${float(loan_application.annual_income) / 12:,.2f}",
                    'debt_to_income_estimate': f"{(float(loan_application.purchase_price) * 0.004 / (float(loan_application.annual_income) / 12) * 100):.1f}%",
                    'down_payment_percentage': f"{(float(loan_application.down_payment) / float(loan_application.purchase_price) * 100):.1f}%",
                    'liquid_assets': f"${total_balance:,.2f}"
                },
                'status': 'complete_with_bank_data',
                'timestamp': datetime.now().isoformat()
            }
            
            return Response(complete_user_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error connecting to Plaid: {e}")
            return Response(
                {"error": f"Unable to connect bank account: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateSandboxPublicTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Create Sandbox Public Token",
        operation_description="Generate a sandbox public token for testing Plaid integration",
        responses={
            200: openapi.Response(
                "Public token created",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'public_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def post(self, request):
        try:
            plaid_service = PlaidService()
            result = plaid_service.create_sandbox_public_token()
            
            return Response({
                'public_token': result['public_token'],
                'message': 'Sandbox public token created successfully. Use this token with your loan application ID.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creating sandbox public token: {e}")
            return Response(
                {"error": f"Unable to create sandbox public token: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserBankDetailsView(APIView):
    """Get individual user's bank details by loan ID"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get User's Bank Details",
        operation_description="Get bank account details for a specific user by loan application ID",
        responses={
            200: openapi.Response(
                "User's bank details",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'loan_application_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'user_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'bank_accounts': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'total_balance': openapi.Schema(type=openapi.TYPE_STRING),
                        'plaid_connected': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                )
            ),
            404: openapi.Response("Loan Application not found"),
            500: openapi.Response("Server error")
        }
    )
    def get(self, request, loan_id):
        try:
            # Get loan application
            loan_application = get_object_or_404(LoanApplication, id=loan_id)
            
            # Check if user has connected bank account
            try:
                plaid_connection = PlaidConnection.objects.get(loan_application=loan_application)
                plaid_service = PlaidService()
                
                # Get fresh account data from Plaid
                accounts = plaid_service.get_accounts(plaid_connection.access_token)
                
                # Format bank account data
                formatted_accounts = []
                total_balance = 0
                checking_balance = 0
                savings_balance = 0
                
                for account in accounts:
                    balances = account.get('balances', {})
                    current_balance = balances.get('current', 0) or 0
                    available_balance = balances.get('available', 0) or 0
                    
                    account_info = {
                        'account_id': account['account_id'],
                        'name': account['name'],
                        'official_name': account.get('official_name', ''),
                        'type': str(account['type']),
                        'subtype': str(account.get('subtype', '')),
                        'current_balance': float(current_balance),
                        'available_balance': float(available_balance),
                        'currency': balances.get('iso_currency_code', 'USD'),
                        'balance_formatted': f"${current_balance:,.2f}"
                    }
                    
                    formatted_accounts.append(account_info)
                    total_balance += current_balance
                    
                    # Categorize balances by account type
                    if account.get('subtype') == 'checking':
                        checking_balance += current_balance
                    elif account.get('subtype') == 'savings':
                        savings_balance += current_balance
                
                return Response({
                    'loan_application_id': loan_application.id,
                    'user_name': loan_application.full_name,
                    'email': loan_application.email,
                    'bank_accounts': formatted_accounts,
                    'financial_summary': {
                        'total_balance': f"${total_balance:,.2f}",
                        'checking_balance': f"${checking_balance:,.2f}",
                        'savings_balance': f"${savings_balance:,.2f}",
                        'account_count': len(formatted_accounts)
                    },
                    'plaid_connected': True,
                    'message': f'Bank details for {loan_application.full_name}'
                }, status=status.HTTP_200_OK)
                
            except PlaidConnection.DoesNotExist:
                # No bank account connected
                return Response({
                    'loan_application_id': loan_application.id,
                    'user_name': loan_application.full_name,
                    'email': loan_application.email,
                    'bank_accounts': [],
                    'financial_summary': {
                        'total_balance': '$0.00',
                        'checking_balance': '$0.00',
                        'savings_balance': '$0.00',
                        'account_count': 0
                    },
                    'plaid_connected': False,
                    'message': f'No bank account connected for {loan_application.full_name}'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error retrieving bank details for loan_id={loan_id}: {e}")
            return Response({
                'error': 'Unable to retrieve bank details'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SandboxStatsView(APIView):
    """Get sandbox statistics - how many users are in the system"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get Sandbox Statistics",
        operation_description="Get counts of users, loan applications, and bank connections in the sandbox",
        responses={
            200: openapi.Response(
                "Sandbox statistics",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_loan_applications': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_plaid_connections': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'users_with_bank_connection': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'users_without_bank_connection': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            # Count total loan applications (users)
            total_loan_applications = LoanApplication.objects.count()
            
            # Count total Plaid connections
            total_plaid_connections = PlaidConnection.objects.count()
            
            # Count users with bank connections
            users_with_bank_connection = PlaidConnection.objects.values_list(
                'loan_application', flat=True
            ).distinct().count()
            
            # Calculate users without bank connections
            users_without_bank_connection = total_loan_applications - users_with_bank_connection
            
            # Get list of all users with their connection status
            all_users = []
            loan_applications = LoanApplication.objects.all()
            
            for loan_app in loan_applications:
                has_connection = PlaidConnection.objects.filter(
                    loan_application=loan_app
                ).exists()
                
                user_info = {
                    'loan_id': loan_app.id,
                    'name': loan_app.full_name,
                    'email': loan_app.email,
                    'has_bank_connection': has_connection,
                    'created_date': loan_app.created_at.strftime('%Y-%m-%d') if hasattr(loan_app, 'created_at') else 'N/A'
                }
                all_users.append(user_info)
            
            return Response({
                'sandbox_summary': {
                    'total_loan_applications': total_loan_applications,
                    'total_plaid_connections': total_plaid_connections,
                    'users_with_bank_connection': users_with_bank_connection,
                    'users_without_bank_connection': users_without_bank_connection,
                    'connection_rate': f"{(users_with_bank_connection / total_loan_applications * 100):.1f}%" if total_loan_applications > 0 else "0%"
                },
                'all_users': all_users,
                'instructions': {
                    'get_individual_bank_details': 'Use GET /api/user/{loan_id}/bank-details/ to see individual user bank information',
                    'example': 'For user X (loan_id=1): GET /api/user/1/bank-details/'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving sandbox stats: {e}")
            return Response({
                'error': 'Unable to retrieve sandbox statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Import the new flow views
from .flow_views import (
    Step1CreateLoanWithLinkTokenView,
    Step2ExchangeTokenGetAccountsView, 
    Step3GetCompleteDataView,
    QuickSandboxFlowView
)


class LoanDecisionPDFView(APIView):
    """
    Generate PDF document based on AI engine loan decision
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Generate Loan Decision PDF",
        operation_description="Generates approval or denial PDF based on AI engine analysis of loan application and Plaid data",
        responses={
            200: openapi.Response("PDF file", content=openapi.TYPE_FILE),
            404: openapi.Response("Loan application not found"),
            500: openapi.Response("Server error")
        }
    )
    def get(self, request, loan_id):
        try:
            # Get loan application
            loan_app = get_object_or_404(LoanApplication, id=loan_id)
            
            # Get Plaid connection and data
            plaid_connection = PlaidConnection.objects.filter(loan_application=loan_app).first()
            
            if not plaid_connection:
                # Use fallback data when no Plaid connection exists
                logger.warning(f"No Plaid connection found for loan {loan_id}, using fallback data")
                plaid_data = self._get_fallback_plaid_data(loan_app)
            else:
                # Get Plaid financial data
                plaid_service = PlaidService()
                try:
                    accounts_data = plaid_service.get_accounts(plaid_connection.access_token)
                    # Transactions and income products not authorized - skip
                    transactions_data = []
                    income_data = {}
                    
                    # Format data for AI engine
                    plaid_data = self._format_plaid_data(accounts_data, transactions_data, income_data, loan_app)
                    
                except Exception as e:
                    logger.error(f"Error fetching Plaid data: {e}")
                    # Use mock/fallback data when Plaid fails
                    plaid_data = self._get_fallback_plaid_data(loan_app)

            # Prepare user input for AI engine
            user_input = {
                "full_name": loan_app.full_name,
                "email": loan_app.email,
                "phone": loan_app.phone_number,
                "property_zip": loan_app.property_zip,
                "property_address": loan_app.property_address,
                "loan_purpose": loan_app.loan_purpose,
                "purchase_price": loan_app.purchase_price,
                "down_payment": loan_app.down_payment or "$0"
            }

            # Use AI engine to make decision
            try:
                logger.info(f"Making loan decision for {user_input['full_name']}")
                logger.info(f"Plaid data: {plaid_data}")
                
                # Use the real AI engine from aiengine.py
                engine = PreApprovalEngine(
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
                decision = engine.analyze(user_input, plaid_data)
                
                # Fallback logic if AI engine fails
                if decision not in ["approve", "disapprove"]:
                    down_payment_str = plaid_data.get('analysis', {}).get('down_payment_percentage', '0%')
                    down_payment_pct = float(down_payment_str.replace('%', ''))
                    decision = "approve" if down_payment_pct >= 20 else "disapprove"
                    
                logger.info(f"AI Decision: {decision}")
                
            except Exception as e:
                logger.error(f"AI Engine error: {e}")
                # Fallback to simple logic
                down_payment_str = plaid_data.get('analysis', {}).get('down_payment_percentage', '0%')
                down_payment_pct = float(down_payment_str.replace('%', ''))
                decision = "approve" if down_payment_pct >= 20 else "disapprove"

            # Generate PDF based on decision
            if decision == "approve":
                pdf_response = self._generate_simple_approval_pdf(user_input, plaid_data)
                # Send congratulations SMS (placeholder)
                self._send_congratulations_sms(user_input['phone'], user_input['full_name'])
            else:
                pdf_response = self._generate_simple_denial_pdf(user_input, plaid_data)
                # Send sorry SMS (placeholder)
                self._send_sorry_sms(user_input['phone'], user_input['full_name'])

            return pdf_response

        except Exception as e:
            logger.error(f"Error in LoanDecisionPDFView: {e}")
            return Response({
                'error': 'Unable to generate PDF'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_fallback_plaid_data(self, loan_app):
        """Generate fallback financial data when Plaid is unavailable"""
        try:
            # Use mock data similar to the aiengine.py example
            purchase_price_clean = float(loan_app.purchase_price.replace('$', '').replace(',', '')) if loan_app.purchase_price else 455000
            down_payment_clean = float(loan_app.down_payment.replace('$', '').replace(',', '')) if loan_app.down_payment else 100000
            
            # Mock financial data - similar to what's in aiengine.py
            mock_annual_income = 78000  # Reasonable income
            mock_monthly_income = mock_annual_income / 12
            mock_liquid_assets = 213535.80  # From aiengine.py example
            
            estimated_monthly_payment = (purchase_price_clean - down_payment_clean) * 0.005
            debt_to_income = (estimated_monthly_payment / mock_monthly_income * 100) if mock_monthly_income > 0 else 100
            down_payment_percentage = (down_payment_clean / purchase_price_clean * 100) if purchase_price_clean > 0 else 0

            return {
                "loan_details": {
                    "purpose": loan_app.loan_purpose or "Purchase",
                    "purchase_price": loan_app.purchase_price or "$455,000",
                    "down_payment": loan_app.down_payment or "$100,000",
                    "cash_out_amount": "$0",
                    "annual_income": f"${mock_annual_income:,.2f}"
                },
                "financial_summary": {
                    "total_balance": f"${mock_liquid_assets:,.2f}",
                    "checking_balance": "$50,000.00",
                    "savings_balance": f"${mock_liquid_assets - 50000:,.2f}",
                    "account_count": 3
                },
                "analysis": {
                    "monthly_income": f"${mock_monthly_income:,.2f}",
                    "debt_to_income_estimate": f"{debt_to_income:.1f}%",
                    "down_payment_percentage": f"{down_payment_percentage:.1f}%",
                    "liquid_assets": f"${mock_liquid_assets:,.2f}"
                }
            }
        except Exception as e:
            logger.error(f"Error creating fallback data: {e}")
            # Return minimal fallback data
            return {
                "loan_details": {
                    "purpose": "Purchase",
                    "purchase_price": "$455,000",
                    "down_payment": "$100,000",
                    "cash_out_amount": "$0",
                    "annual_income": "$78,000"
                },
                "financial_summary": {
                    "total_balance": "$213,535.80",
                    "checking_balance": "$50,000.00",
                    "savings_balance": "$163,535.80",
                    "account_count": 3
                },
                "analysis": {
                    "monthly_income": "$6,500.00",
                    "debt_to_income_estimate": "27.3%",
                    "down_payment_percentage": "22.0%",
                    "liquid_assets": "$213,535.80"
                }
            }

    def _format_plaid_data(self, accounts_data, transactions_data, income_data, loan_app):
        """Format Plaid data for AI engine"""
        try:
            # Calculate financial metrics
            total_balance = sum([acc.get('balances', {}).get('current', 0) for acc in accounts_data.get('accounts', [])])
            checking_balance = sum([acc.get('balances', {}).get('current', 0) for acc in accounts_data.get('accounts', []) if acc.get('subtype') == 'checking'])
            savings_balance = sum([acc.get('balances', {}).get('current', 0) for acc in accounts_data.get('accounts', []) if acc.get('subtype') == 'savings'])
            
            # Estimate income
            annual_income = 0
            monthly_income = 0
            if income_data and 'income' in income_data:
                income_streams = income_data['income'].get('income_streams', [])
                for stream in income_streams:
                    annual_income += stream.get('monthly_income_amount', 0) * 12
                    monthly_income += stream.get('monthly_income_amount', 0)

            # Use fallback income if none found
            if annual_income == 0:
                annual_income = 78000  # Default reasonable income
                monthly_income = annual_income / 12

            # Calculate debt-to-income ratio (simplified)
            purchase_price_clean = float(loan_app.purchase_price.replace('$', '').replace(',', '')) if loan_app.purchase_price else 0
            down_payment_clean = float(loan_app.down_payment.replace('$', '').replace(',', '')) if loan_app.down_payment else 0
            
            estimated_monthly_payment = (purchase_price_clean - down_payment_clean) * 0.005  # 0.5% monthly estimate
            debt_to_income = (estimated_monthly_payment / monthly_income * 100) if monthly_income > 0 else 100
            down_payment_percentage = (down_payment_clean / purchase_price_clean * 100) if purchase_price_clean > 0 else 0

            return {
                "loan_details": {
                    "purpose": loan_app.loan_purpose,
                    "purchase_price": loan_app.purchase_price,
                    "down_payment": loan_app.down_payment or "$0",
                    "cash_out_amount": "$0",
                    "annual_income": f"${annual_income:,.2f}"
                },
                "financial_summary": {
                    "total_balance": f"${total_balance:,.2f}",
                    "checking_balance": f"${checking_balance:,.2f}",
                    "savings_balance": f"${savings_balance:,.2f}",
                    "account_count": len(accounts_data.get('accounts', []))
                },
                "analysis": {
                    "monthly_income": f"${monthly_income:,.2f}",
                    "debt_to_income_estimate": f"{debt_to_income:.1f}%",
                    "down_payment_percentage": f"{down_payment_percentage:.1f}%",
                    "liquid_assets": f"${total_balance:,.2f}"
                }
            }
        except Exception as e:
            logger.error(f"Error formatting Plaid data: {e}")
            return self._get_fallback_plaid_data(loan_app)



    def _generate_simple_approval_pdf(self, user_input, plaid_data):
        """Generate professional approval PDF matching the exact format from the image"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.colors import Color
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Colors
            green_color = Color(0.2, 0.7, 0.5)  # Professional green
            dark_gray = Color(0.2, 0.2, 0.2)
            light_gray = Color(0.5, 0.5, 0.5)
            
            # Title - Congratulations John !
            p.setFont("Helvetica-Bold", 28)
            p.setFillColor(dark_gray)
            p.drawCentredText(width/2, height-80, f"Congratulations {user_input['full_name'].split()[0]} !")
            
            # Subtitle paragraph
            p.setFont("Helvetica", 12)
            p.setFillColor(dark_gray)
            subtitle_lines = [
                "Based on the personal financial information you provided, and the",
                "credit report we've pulled, we were able to approve you for a maximum purchase price",
                "of:"
            ]
            y_pos = height - 130
            for line in subtitle_lines:
                p.drawCentredText(width/2, y_pos, line)
                y_pos -= 18
            
            # Big amount - $250,000
            p.setFont("Helvetica-Bold", 48)
            p.setFillColor(green_color)
            p.drawCentredText(width/2, height-230, "$250,000")
            
            # Left side details
            left_x = 80
            y_start = height - 320
            
            # Left column
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(left_x, y_start, "$250,000")
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(left_x, y_start-12, "Maximum Loan Amount")
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(left_x, y_start-40, "Single Family")
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(left_x, y_start-52, "Property Type")
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(left_x, y_start-80, user_input['full_name'])
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(left_x, y_start-92, "Primary Borrower")
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(left_x, y_start-120, "11/29/2025")
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(left_x, y_start-132, "Pre-approval Expiration")
            
            # Right column
            right_x = width - 200
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(right_x, y_start, "Primary Residence")
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(right_x, y_start-12, "Property Use")
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(right_x, y_start-40, "Pennsylvania")
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(right_x, y_start-52, "Location")
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(dark_gray)
            p.drawString(right_x, y_start-80, "Borrower(s)")
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(right_x, y_start-92, "")
            
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(Color(0.2, 0.4, 0.8))  # Blue color for email
            p.drawString(right_x, y_start-120, user_input['email'])
            p.setFont("Helvetica", 9)
            p.setFillColor(light_gray)
            p.drawString(right_x, y_start-132, "Questions?")
            
            # Footer company info
            p.setFont("Helvetica", 8)
            p.setFillColor(light_gray)
            p.drawString(80, 120, "Midland Federal Savings and Loan Association | NMLS #446746")
            
            # Legal disclaimer
            disclaimer_y = 80
            disclaimer_text = [
                "This is not a commitment to lend, nor is it a formal clear to close. A formal clear to close will be contingent on the information provided being fully verified, satisfactory",
                "appraisal, clear title and underwriting approval. Loan terms are subject to change. Estimated monthly taxes and insurance are subject to change",
                "depending on your county and insurance provider. Loans with loan to value ratios over 80% will require Mortgage Insurance. This loan pre-approval letter is issued",
                "collectively to all co-borrowers included in the pre-approval application and subject to the successful completion of the loan process for all borrowers."
            ]
            
            p.setFont("Helvetica", 7)
            p.setFillColor(Color(0.4, 0.4, 0.4))
            for i, line in enumerate(disclaimer_text):
                p.drawString(80, disclaimer_y - (i * 10), line)
            
            p.save()
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="loan_approval_{user_input["full_name"].replace(" ", "_")}.pdf"'
            return response
            
        except Exception as e:
            logger.error(f"Error generating approval PDF: {e}")
            return HttpResponse(f"Approval: Congratulations {user_input['full_name']}! Your loan for $250,000 has been approved.", content_type='text/plain')

    def _generate_simple_denial_pdf(self, user_input, plaid_data):
        """Generate simple denial PDF using basic approach"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Title
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredText(width/2, height-100, "Loan Application Decision")
            
            # Main message
            p.setFont("Helvetica", 14)
            y_position = height - 180
            
            lines = [
                f"Dear {user_input['full_name']},",
                "",
                "Thank you for your interest in obtaining a mortgage loan with us.",
                "After careful review of your application and financial information,",
                "we regret to inform you that we are unable to approve your",
                "loan application at this time.",
                "",
                "APPLICATION STATUS: DECLINED",
                "",
                "Common reasons for loan denial may include:",
                "• Debt-to-income ratio exceeds lending guidelines",
                "• Insufficient down payment",
                "• Insufficient liquid assets for closing costs",
                "• Credit score below minimum requirements",
                "",
                "We encourage you to work on improving your financial profile",
                "and consider reapplying in the future.",
                "",
                f"Contact us at {user_input['email']} for more information.",
            ]
            
            for line in lines:
                if "DECLINED" in line:
                    p.setFont("Helvetica-Bold", 14)
                    p.setFillColorRGB(0.8, 0, 0)  # Red color
                elif line.startswith("•"):
                    p.setFont("Helvetica", 12)
                    p.setFillColorRGB(0, 0, 0)
                else:
                    p.setFont("Helvetica", 14)
                    p.setFillColorRGB(0, 0, 0)
                
                if line:  # Only draw non-empty lines
                    p.drawString(50, y_position, line)
                y_position -= 20
            
            p.save()
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="loan_denial_{user_input["full_name"].replace(" ", "_")}.pdf"'
            return response
            
        except Exception as e:
            logger.error(f"Error generating denial PDF: {e}")
            return HttpResponse(f"Denial: Sorry {user_input['full_name']}, your loan application was not approved at this time.", content_type='text/plain')

    def _send_congratulations_sms(self, phone, name):
        """Send congratulations SMS (placeholder implementation)"""
        # TODO: Implement SMS service (Twilio, AWS SNS, etc.)
        logger.info(f"Congratulations SMS sent to {phone} for {name}")
        print(f"🎉 SMS: Congratulations {name}! Your loan has been approved for $250,000!")

    def _send_sorry_sms(self, phone, name):
        """Send sorry SMS (placeholder implementation)"""
        # TODO: Implement SMS service (Twilio, AWS SNS, etc.)
        logger.info(f"Sorry SMS sent to {phone} for {name}")
        print(f"😔 SMS: Sorry {name}, your loan application was not approved at this time.")


class AILoanDecisionView(APIView):
    """
    Complete AI-powered loan decision endpoint that:
    1. Gets loan data from Plaid or from request body
    2. Runs it through AI engine
    3. Generates professional PDF
    4. Returns download response
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="AI Loan Decision (POST)",
        operation_description="Process loan decision using AI. Can use loan_id from database or provide custom data in request body for testing.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_input': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'property_zip': openapi.Schema(type=openapi.TYPE_STRING),
                        'property_address': openapi.Schema(type=openapi.TYPE_STRING),
                        'loan_purpose': openapi.Schema(type=openapi.TYPE_STRING),
                        'purchase_price': openapi.Schema(type=openapi.TYPE_STRING),
                        'down_payment': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
                'plaid_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'loan_details': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'financial_summary': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'analysis': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            }
        ),
        responses={
            200: openapi.Response("PDF file for loan decision"),
            400: openapi.Response("Bad request"),
            404: openapi.Response("Loan not found"),
            500: openapi.Response("Server error")
        }
    )
    def post(self, request, loan_id):
        try:
            # Check if custom data is provided in request body for testing
            request_user_input = request.data.get('user_input')
            request_plaid_data = request.data.get('plaid_data')
            
            if request_user_input and request_plaid_data:
                # Use custom data from request body (for Postman testing)
                user_input = request_user_input
                plaid_data = request_plaid_data
                loan = None  # We don't need loan object for custom data
                logger.info("Using custom data from request body for AI processing")
            else:
                # Use database lookup (original functionality)
                loan = LoanApplication.objects.get(id=loan_id)
                
                # Get Plaid connection and data
                plaid_connection = PlaidConnection.objects.filter(loan_application=loan).first()
                
                if not plaid_connection:
                    # Use fallback data when no Plaid connection exists
                    logger.warning(f"No Plaid connection found for loan {loan_id}, using fallback data")
                    plaid_data = self._get_fallback_plaid_data_for_ai(loan)
                else:
                    # Get Plaid financial data
                    plaid_service = PlaidService()
                    try:
                        accounts_data = plaid_service.get_accounts(plaid_connection.access_token)
                        # Transactions product not authorized - skip
                        transactions_data = []
                        
                        # Format data for AI engine
                        plaid_data = self._format_plaid_data_for_ai(accounts_data, transactions_data, loan)
                        
                    except Exception as e:
                        logger.error(f"Error fetching Plaid data: {e}")
                        # Use mock/fallback data when Plaid fails
                        plaid_data = self._get_fallback_plaid_data_for_ai(loan)

                if not plaid_data:
                    return Response({
                        'error': 'Unable to retrieve financial data',
                        'loan_id': loan_id
                    }, status=400)
                
                # Prepare user input for AI engine from database
                user_input = {
                    "full_name": loan.full_name,
                    "email": loan.email,
                    "phone": loan.phone_number,
                    "property_zip": loan.property_zip_code,
                    "property_address": loan.property_address,
                    "loan_purpose": loan.loan_purpose,
                    "purchase_price": str(loan.purchase_price),
                    "down_payment": str(loan.down_payment) if loan.down_payment else "$0"
                }

            # Use AI engine to make decision
            try:
                logger.info(f"Making loan decision for {user_input['full_name']}")
                logger.info(f"Plaid data: {plaid_data}")
                
                # Use the real AI engine from aiengine.py
                engine = PreApprovalEngine(
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
                decision = engine.analyze(user_input, plaid_data)
                
                # Fallback logic if AI engine fails
                if decision not in ["approve", "disapprove"]:
                    down_payment_str = plaid_data.get('analysis', {}).get('down_payment_percentage', '0%')
                    down_payment_pct = float(down_payment_str.replace('%', ''))
                    decision = "approve" if down_payment_pct >= 20 else "disapprove"
                    
                logger.info(f"AI Decision: {decision}")
                
            except Exception as e:
                logger.error(f"AI Engine error: {e}")
                # Fallback to simple logic
                down_payment_str = plaid_data.get('analysis', {}).get('down_payment_percentage', '0%')
                down_payment_pct = float(down_payment_str.replace('%', ''))
                decision = "approve" if down_payment_pct >= 20 else "disapprove"
            
            # For testing with custom data, return JSON response instead of PDF
            if request_user_input and request_plaid_data:
                # Return JSON response for Postman testing
                return Response({
                    'decision': decision,
                    'user_input': user_input,
                    'plaid_data': plaid_data,
                    'message': f'AI Decision: {decision}'
                }, status=200)
            
            # Generate PDF based on decision (only when using database loan)
            if decision == "approve":
                # Create a decision result object for the existing method
                decision_result = {
                    'approved': True,
                    'approved_amount': 250000,
                    'interest_rate': '4.5',
                    'loan_term': '30',
                    'monthly_payment': '1,200',
                    'confidence': 85
                }
                pdf_buffer = self._generate_approval_pdf(loan, decision_result)
                filename = f"loan_approval_{loan_id}.pdf"
                # Send approval SMS
                if loan:
                    self._send_approval_sms(loan, decision_result['approved_amount'])
            else:
                # Create a decision result object for denial
                decision_result = {
                    'approved': False,
                    'reasons': ['Insufficient income', 'High debt-to-income ratio'],
                    'confidence': 75
                }
                pdf_buffer = self._generate_denial_pdf(loan, decision_result)
                filename = f"loan_denial_{loan_id}.pdf"
                # Send denial SMS
                if loan:
                    self._send_denial_sms(loan)
            
            # Return PDF as download
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except LoanApplication.DoesNotExist:
            # If custom data was provided, this error shouldn't occur
            if request.data.get('user_input') and request.data.get('plaid_data'):
                return Response({
                    'error': 'Loan application not found, but you provided custom data. Please check your request format.',
                    'loan_id': loan_id
                }, status=400)
            return Response({
                'error': 'Loan application not found',
                'loan_id': loan_id
            }, status=404)
        except Exception as e:
            logger.error(f"Error in AILoanDecisionView: {e}")
            return Response({
                'error': f'Error processing loan decision: {str(e)}',
                'loan_id': loan_id
            }, status=500)

    def _get_fallback_plaid_data_for_ai(self, loan_app):
        """Generate fallback financial data when Plaid is unavailable"""
        try:
            # Use mock data similar to the aiengine.py example
            purchase_price_clean = float(str(loan_app.purchase_price).replace('$', '').replace(',', '')) if loan_app.purchase_price else 455000
            down_payment_clean = float(str(loan_app.down_payment).replace('$', '').replace(',', '')) if loan_app.down_payment else 100000
            
            # Mock financial data - similar to what's in aiengine.py
            mock_annual_income = 78000  # Reasonable income
            mock_monthly_income = mock_annual_income / 12
            mock_liquid_assets = 213535.80  # From aiengine.py example
            
            estimated_monthly_payment = (purchase_price_clean - down_payment_clean) * 0.005
            debt_to_income = (estimated_monthly_payment / mock_monthly_income * 100) if mock_monthly_income > 0 else 100
            down_payment_percentage = (down_payment_clean / purchase_price_clean * 100) if purchase_price_clean > 0 else 0

            return {
                "loan_details": {
                    "purpose": loan_app.loan_purpose or "Purchase",
                    "purchase_price": f"${purchase_price_clean:,.0f}",
                    "down_payment": f"${down_payment_clean:,.0f}",
                    "cash_out_amount": "$0",
                    "annual_income": f"${mock_annual_income:,.2f}"
                },
                "financial_summary": {
                    "total_balance": f"${mock_liquid_assets:,.2f}",
                    "checking_balance": "$50,000.00",
                    "savings_balance": f"${mock_liquid_assets - 50000:,.2f}",
                    "account_count": 3
                },
                "analysis": {
                    "monthly_income": f"${mock_monthly_income:,.2f}",
                    "debt_to_income_estimate": f"{debt_to_income:.1f}%",
                    "down_payment_percentage": f"{down_payment_percentage:.1f}%",
                    "liquid_assets": f"${mock_liquid_assets:,.2f}"
                }
            }
        except Exception as e:
            logger.error(f"Error creating fallback data: {e}")
            # Return minimal fallback data
            return {
                "loan_details": {
                    "purpose": "Purchase",
                    "purchase_price": "$455,000",
                    "down_payment": "$100,000",
                    "cash_out_amount": "$0",
                    "annual_income": "$78,000"
                },
                "financial_summary": {
                    "total_balance": "$213,535.80",
                    "checking_balance": "$50,000.00",
                    "savings_balance": "$163,535.80",
                    "account_count": 3
                },
                "analysis": {
                    "monthly_income": "$6,500.00",
                    "debt_to_income_estimate": "27.3%",
                    "down_payment_percentage": "22.0%",
                    "liquid_assets": "$213,535.80"
                }
            }

    def _format_plaid_data_for_ai(self, accounts_data, transactions_data, loan_app):
        """Format Plaid data for AI engine"""
        try:
            # Calculate financial metrics
            total_balance = sum([acc.get('balances', {}).get('current', 0) for acc in accounts_data])
            checking_balance = sum([acc.get('balances', {}).get('current', 0) for acc in accounts_data if acc.get('subtype') == 'checking'])
            savings_balance = sum([acc.get('balances', {}).get('current', 0) for acc in accounts_data if acc.get('subtype') == 'savings'])
            
            # Estimate income from transactions (simplified)
            annual_income = float(loan_app.annual_income) if loan_app.annual_income else 78000
            monthly_income = annual_income / 12

            # Calculate debt-to-income ratio (simplified)
            purchase_price_clean = float(str(loan_app.purchase_price).replace('$', '').replace(',', '')) if loan_app.purchase_price else 0
            down_payment_clean = float(str(loan_app.down_payment).replace('$', '').replace(',', '')) if loan_app.down_payment else 0
            
            estimated_monthly_payment = (purchase_price_clean - down_payment_clean) * 0.005  # 0.5% monthly estimate
            debt_to_income = (estimated_monthly_payment / monthly_income * 100) if monthly_income > 0 else 100
            down_payment_percentage = (down_payment_clean / purchase_price_clean * 100) if purchase_price_clean > 0 else 0

            return {
                "loan_details": {
                    "purpose": loan_app.loan_purpose,
                    "purchase_price": f"${purchase_price_clean:,.0f}",
                    "down_payment": f"${down_payment_clean:,.0f}",
                    "cash_out_amount": "$0",
                    "annual_income": f"${annual_income:,.2f}"
                },
                "financial_summary": {
                    "total_balance": f"${total_balance:,.2f}",
                    "checking_balance": f"${checking_balance:,.2f}",
                    "savings_balance": f"${savings_balance:,.2f}",
                    "account_count": len(accounts_data)
                },
                "analysis": {
                    "monthly_income": f"${monthly_income:,.2f}",
                    "debt_to_income_estimate": f"{debt_to_income:.1f}%",
                    "down_payment_percentage": f"{down_payment_percentage:.1f}%",
                    "liquid_assets": f"${total_balance:,.2f}"
                }
            }
        except Exception as e:
            logger.error(f"Error formatting Plaid data: {e}")
            return self._get_fallback_plaid_data_for_ai(loan_app)
    
    def _generate_approval_pdf(self, loan, decision_result):
        """Generate professional approval PDF matching exact format"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Colors
        green_color = colors.Color(0.2, 0.6, 0.2)  # Professional green
        dark_gray = colors.Color(0.2, 0.2, 0.2)
        light_gray = colors.Color(0.7, 0.7, 0.7)
        
        # Header with logo area
        p.setFillColor(colors.white)
        p.rect(50, height-100, width-100, 50, fill=1, stroke=1)
        
        # Company name/logo
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(dark_gray)
        p.drawString(60, height-75, "MOTHY EDWARD FINANCIAL")
        
        # Main title
        p.setFont("Helvetica-Bold", 24)
        p.setFillColor(dark_gray)
        p.drawString(60, height-150, "CONGRATULATIONS!")
        
        # Applicant name
        p.setFont("Helvetica-Bold", 18)
        p.drawString(60, height-180, f"{loan.full_name}")
        
        # Approval message
        p.setFont("Helvetica", 14)
        p.drawString(60, height-210, "Your loan application has been")
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(green_color)
        p.drawString(60, height-230, "APPROVED!")
        
        # Approved amount - large and prominent
        p.setFont("Helvetica-Bold", 32)
        p.setFillColor(green_color)
        approved_amount = decision_result.get('approved_amount', 250000)
        p.drawString(60, height-280, f"${approved_amount:,.2f}")
        
        # Reset color for details
        p.setFillColor(dark_gray)
        p.setFont("Helvetica", 12)
        
        # Loan details section
        y_pos = height - 330
        p.drawString(60, y_pos, "LOAN DETAILS:")
        y_pos -= 25
        p.drawString(70, y_pos, f"• Loan Purpose: {loan.loan_purpose}")
        y_pos -= 20
        p.drawString(70, y_pos, f"• Interest Rate: {decision_result.get('interest_rate', '4.5')}% APR")
        y_pos -= 20
        p.drawString(70, y_pos, f"• Term: {decision_result.get('loan_term', '30')} years")
        y_pos -= 20
        p.drawString(70, y_pos, f"• Monthly Payment: ${decision_result.get('monthly_payment', '1,200'):,}")
        
        # Next steps
        y_pos -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(60, y_pos, "NEXT STEPS:")
        p.setFont("Helvetica", 11)
        y_pos -= 20
        p.drawString(70, y_pos, "1. Review and sign loan documents")
        y_pos -= 15
        p.drawString(70, y_pos, "2. Schedule closing appointment")
        y_pos -= 15
        p.drawString(70, y_pos, "3. Provide any additional documentation")
        
        # Contact information
        y_pos -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(60, y_pos, "CONTACT US:")
        p.setFont("Helvetica", 11)
        y_pos -= 20
        p.drawString(70, y_pos, "Phone: (555) 123-4567")
        y_pos -= 15
        p.drawString(70, y_pos, "Email: support@mothyedward.com")
        
        # Footer disclaimer
        p.setFont("Helvetica", 8)
        p.setFillColor(light_gray)
        p.drawString(60, 60, "This pre-approval is subject to final underwriting and verification of information.")
        p.drawString(60, 50, "Terms and conditions may apply. Equal Housing Lender.")
        
        # AI decision confidence
        p.setFont("Helvetica", 9)
        p.setFillColor(colors.black)
        confidence = decision_result.get('confidence', 85)
        p.drawString(width-200, 30, f"AI Confidence Score: {confidence}%")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer
    
    def _generate_denial_pdf(self, loan, decision_result):
        """Generate professional denial PDF"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Colors
        red_color = colors.Color(0.8, 0.2, 0.2)
        dark_gray = colors.Color(0.2, 0.2, 0.2)
        light_gray = colors.Color(0.7, 0.7, 0.7)
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(dark_gray)
        p.drawString(60, height-75, "MOTHY EDWARD FINANCIAL")
        
        # Main title
        p.setFont("Helvetica-Bold", 20)
        p.setFillColor(red_color)
        p.drawString(60, height-150, "LOAN APPLICATION STATUS")
        
        # Applicant name
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(dark_gray)
        p.drawString(60, height-180, f"Dear {loan.full_name},")
        
        # Denial message
        p.setFont("Helvetica", 12)
        p.drawString(60, height-220, "We regret to inform you that your loan application")
        p.drawString(60, height-240, "cannot be approved at this time.")
        
        # Reasons
        y_pos = height - 280
        p.setFont("Helvetica-Bold", 12)
        p.drawString(60, y_pos, "REASONS FOR DECISION:")
        p.setFont("Helvetica", 11)
        
        reasons = decision_result.get('reasons', ['Insufficient income', 'High debt-to-income ratio'])
        for reason in reasons[:3]:  # Show up to 3 reasons
            y_pos -= 20
            p.drawString(70, y_pos, f"• {reason}")
        
        # Next steps
        y_pos -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(60, y_pos, "WHAT YOU CAN DO:")
        p.setFont("Helvetica", 11)
        y_pos -= 20
        p.drawString(70, y_pos, "• Improve your credit score")
        y_pos -= 15
        p.drawString(70, y_pos, "• Reduce existing debt")
        y_pos -= 15
        p.drawString(70, y_pos, "• Increase your income")
        y_pos -= 15
        p.drawString(70, y_pos, "• Reapply in 3-6 months")
        
        # Contact information
        y_pos -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(60, y_pos, "CONTACT US:")
        p.setFont("Helvetica", 11)
        y_pos -= 20
        p.drawString(70, y_pos, "Phone: (555) 123-4567")
        y_pos -= 15
        p.drawString(70, y_pos, "Email: support@mothyedward.com")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.setFillColor(light_gray)
        p.drawString(60, 60, "Equal Housing Lender. This decision is based on automated underwriting criteria.")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer
    
    def _send_approval_sms(self, loan, approved_amount):
        """Send approval SMS notification"""
        try:
            message = f"🎉 Congratulations {loan.full_name}! Your loan for ${approved_amount:,.2f} has been APPROVED! Check your email for details."
            # SMS implementation would go here
            print(f"SMS sent to {loan.phone_number}: {message}")
        except Exception as e:
            print(f"Failed to send approval SMS: {e}")
    
    def _send_denial_sms(self, loan):
        """Send denial SMS notification"""
        try:
            message = f"Hello {loan.full_name}, we regret to inform you that your loan application was not approved. Please check your email for details and next steps."
            # SMS implementation would go here
            print(f"SMS sent to {loan.phone_number}: {message}")
        except Exception as e:
            print(f"Failed to send denial SMS: {e}")


class BankDataAnalysisPDFView(APIView):
    """
    Generate PDF report from bank data and AI analysis
    Processes Plaid connection data through AI engine and generates downloadable PDF
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="🎯 Generate Bank Data Analysis PDF Report",
        operation_description="""
        Analyzes connected Plaid bank data using AI engine and generates a professional PDF report.
        
        **Workflow:**
        1. Requires a loan application with an active Plaid connection
        2. Fetches real-time bank account data from Plaid
        3. Processes financial data through AI PreApproval Engine
        4. Generates a formatted PDF report with:
           - Applicant Information
           - Loan Details
           - Connected Bank Accounts & Balances
           - AI Analysis Decision (APPROVED/PENDING)
        5. Returns downloadable PDF file
        
        **Requirements:**
        - Loan must exist (loan_application_id)
        - Loan must have active Plaid connection (public token exchanged)
        
        **Response:**
        - Content-Type: application/pdf
        - Filename: loan_analysis_{loan_id}.pdf
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'loan_application_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description="Loan Application ID (from /api/loan-application/ response)",
                    example=57
                ),
            },
            required=['loan_application_id']
        ),
        responses={
            200: openapi.Response(
                "PDF file generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    format='binary',
                    description='PDF file with loan analysis report'
                )
            ),
            400: openapi.Response(
                "Bad Request - Missing or invalid loan_application_id",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="loan_application_id is required")
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Loan not found or no Plaid connection",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="No Plaid connection found for this loan")
                    }
                )
            ),
            500: openapi.Response(
                "Server Error - Failed to generate PDF",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example="Failed to fetch Plaid data")
                    }
                )
            )
        }
    )
    def post(self, request):
        try:
            loan_id = request.data.get('loan_application_id')
            
            if not loan_id:
                return Response(
                    {'error': 'loan_application_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get loan application
            loan = get_object_or_404(LoanApplication, id=loan_id)
            
            # Get Plaid connection
            plaid_connection = PlaidConnection.objects.filter(loan_application=loan).first()
            
            if not plaid_connection:
                return Response(
                    {'error': 'No Plaid connection found for this loan'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Fetch Plaid data
            plaid_service = PlaidService()
            try:
                accounts = plaid_service.get_accounts(plaid_connection.access_token)
                # Transactions product not authorized - skip transaction fetching
                transactions = []
            except Exception as e:
                logger.error(f"Error fetching Plaid data: {e}")
                return Response(
                    {'error': f'Failed to fetch Plaid data: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Prepare data for AI analysis
            user_input = {
                'full_name': loan.full_name,
                'email': loan.email,
                'phone': loan.phone_number,
                'property_address': loan.property_address,
                'property_zip': loan.property_zip_code,
                'loan_purpose': loan.loan_purpose,
                'purchase_price': str(loan.purchase_price),
                'down_payment': str(loan.down_payment),
                'annual_income': str(loan.annual_income)
            }
            
            # Format Plaid data
            bank_accounts = []
            total_balance = 0
            
            for account in accounts:
                balance = account.get('balances', {}).get('current', 0) or 0
                total_balance += balance if balance else 0
                bank_accounts.append({
                    'account_id': account.get('account_id'),
                    'name': account.get('name'),
                    'type': account.get('type'),
                    'subtype': account.get('subtype'),
                    'balance': balance,
                    'currency': account.get('balances', {}).get('iso_currency_code', 'USD')
                })
            
            plaid_data = {
                'loan_application': {
                    'id': loan.id,
                    'full_name': loan.full_name,
                    'email': loan.email,
                    'annual_income': str(loan.annual_income),
                    'purchase_price': str(loan.purchase_price),
                    'down_payment': str(loan.down_payment),
                    'loan_purpose': loan.loan_purpose
                },
                'bank_accounts': bank_accounts,
                'total_balance': f"${total_balance:,.2f}",
                'transaction_count': len(transactions)
            }
            
            # Perform AI analysis
            try:
                engine = PreApprovalEngine(
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
                decision = engine.analyze(user_input, plaid_data)
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                decision = 'pending'
            
            # Generate PDF
            pdf_content = self._generate_analysis_pdf(user_input, plaid_data, decision)
            
            return HttpResponse(
                pdf_content,
                content_type='application/pdf',
                headers={'Content-Disposition': f'attachment; filename="loan_analysis_{loan.id}.pdf"'}
            )
            
        except Exception as e:
            logger.error(f"Error in BankDataAnalysisPDFView: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_analysis_pdf(self, user_input, plaid_data, decision):
        """Generate PDF report from analysis data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#007bff'),
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph('Loan Application Analysis Report', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Applicant Info
        elements.append(Paragraph('<b>Applicant Information</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"<b>Name:</b> {user_input.get('full_name', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Email:</b> {user_input.get('email', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Phone:</b> {user_input.get('phone', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Annual Income:</b> ${user_input.get('annual_income', '0')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Loan Details
        elements.append(Paragraph('<b>Loan Details</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"<b>Property Address:</b> {user_input.get('property_address', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Loan Purpose:</b> {user_input.get('loan_purpose', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Purchase Price:</b> ${user_input.get('purchase_price', '0')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Down Payment:</b> ${user_input.get('down_payment', '0')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Bank Information
        elements.append(Paragraph('<b>Connected Bank Accounts</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        for account in plaid_data.get('bank_accounts', []):
            elements.append(Paragraph(
                f"<b>{account.get('name', 'Unknown')} ({account.get('subtype', 'Account').upper()})</b><br/>"
                f"Balance: {account.get('currency', 'USD')} {account.get('balance', 0):,.2f}",
                styles['Normal']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            f"<b>Total Balance:</b> {plaid_data.get('total_balance', '$0.00')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # AI Decision - Fixed to support 'approve', 'approved', etc.
        decision_lower = str(decision).lower() if decision else 'pending'
        if decision_lower in ['approve', 'approved', 'yes', 'accept']:
            decision_color = colors.HexColor('#28a745')  # GREEN
            decision_text = 'APPROVED'
        elif decision_lower in ['pending', 'maybe', 'review']:
            decision_color = colors.HexColor('#ffc107')  # YELLOW
            decision_text = 'PENDING REVIEW'
        else:
            decision_color = colors.HexColor('#dc3545')  # RED
            decision_text = 'DISAPPROVED'
        
        decision_style = ParagraphStyle(
            'DecisionStyle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=decision_color,
            spaceAfter=10
        )
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f'<b>Status: {decision_text}</b>', decision_style))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            'This analysis is based on the applicant\'s financial data from connected bank accounts and income information.',
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


class GeneratePDFFromBankDataView(APIView):
    """Generate PDF directly from bank data without Plaid connection requirement"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="📄 Generate PDF from Bank Data (Direct)",
        operation_description="""
        Generate PDF report directly from bank data without requiring a Plaid connection.
        
        **📋 Use this endpoint:**
        - After connecting to bank via /api/plaid/connect/
        - Copy the exact response from /api/plaid/connect/ 
        - Send it here to generate PDF with AI analysis
        
        **⚙️ What it does:**
        1. Takes loan application data and bank account data
        2. Processes through AI PreApproval Engine for decision
        3. Generates professional PDF report
        4. Returns downloadable PDF file
        
        **📄 PDF Report Includes:**
        - Applicant Information (Name, Email, Phone)
        - Loan Details (Purpose, Price, Down Payment, Income)
        - Connected Bank Accounts (Names, Balances, Types)
        - AI Analysis Decision (APPROVED/PENDING/DENIED)
        
        **✅ Response:**
        - Content-Type: application/pdf
        - Filename: loan_analysis_{loan_id}.pdf
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'loan_application_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Loan Application ID (from /api/plaid/connect/ response)",
                    example=57
                ),
                'loan_application': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Complete loan application object from /api/plaid/connect/ response",
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            example=57,
                            description="Loan application ID"
                        ),
                        'full_name': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Mr Kim",
                            description="Applicant full name"
                        ),
                        'email': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="user@example.com",
                            description="Applicant email address"
                        ),
                        'phone_number': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="98788",
                            description="Applicant phone number"
                        ),
                        'property_zip_code': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="88",
                            description="Property ZIP code"
                        ),
                        'property_address': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="123 Main Street, Anytown",
                            description="Property address"
                        ),
                        'annual_income': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="75677.00",
                            description="Annual income (as string)"
                        ),
                        'purchase_price': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="788.00",
                            description="Property purchase price (as string)"
                        ),
                        'down_payment': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="76.00",
                            description="Down payment amount (as string)"
                        ),
                        'loan_purpose': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Purchase",
                            description="Loan purpose (Purchase/Refinance/etc)"
                        ),
                        'cash_out_amount': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="100.00",
                            description="Cash out amount if applicable (optional)"
                        ),
                    },
                    required=['id', 'full_name', 'email', 'annual_income', 'purchase_price', 'down_payment']
                ),
                'bank_accounts': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'account_id': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
                                description="Plaid account ID"
                            ),
                            'name': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="Business Enhanced Checking",
                                description="Account name"
                            ),
                            'official_name': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="Business Enhanced Checking",
                                description="Official account name from bank"
                            ),
                            'type': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="depository",
                                description="Account type (depository, credit, etc)"
                            ),
                            'subtype': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="checking",
                                description="Account subtype (checking, savings, etc)"
                            ),
                            'current_balance': openapi.Schema(
                                type=openapi.TYPE_NUMBER,
                                example=0,
                                description="Current balance in account"
                            ),
                            'available_balance': openapi.Schema(
                                type=openapi.TYPE_NUMBER,
                                example=0,
                                description="Available balance in account"
                            ),
                            'currency': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="USD",
                                description="Currency code"
                            ),
                        },
                        required=['account_id', 'name', 'type', 'subtype', 'current_balance', 'currency']
                    ),
                    description="Array of bank accounts from /api/plaid/connect/ response",
                    example=[{
                        "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
                        "name": "Business Enhanced Checking",
                        "official_name": "Business Enhanced Checking",
                        "type": "depository",
                        "subtype": "checking",
                        "current_balance": 0,
                        "available_balance": 0,
                        "currency": "USD"
                    }]
                ),
                'total_balance': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Total balance across all accounts (formatted with $ and commas)",
                    example="$0.00"
                ),
                'plaid_connected': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether Plaid is connected (optional, can omit)",
                    example=True
                ),
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Status message from /api/plaid/connect/ (optional, can omit)",
                    example="Bank account connected successfully!"
                ),
            },
            required=['loan_application_id', 'loan_application', 'bank_accounts', 'total_balance']
        ),
        responses={
            200: openapi.Response(
                "✅ PDF file generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    format='binary',
                    description='PDF file with loan analysis report'
                )
            ),
            400: openapi.Response(
                "Bad Request - Missing required fields",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Server Error - Failed to generate PDF",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request):
        """Generate PDF from direct bank data"""
        try:
            loan_id = request.data.get('loan_application_id')
            loan_data = request.data.get('loan_application')
            bank_accounts = request.data.get('bank_accounts', [])
            total_balance = request.data.get('total_balance', '$0.00')
            
            # Validate required fields
            if not all([loan_id, loan_data, bank_accounts]):
                return Response(
                    {'error': 'Missing required fields: loan_application_id, loan_application, bank_accounts'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare user input for AI engine
            user_input = {
                'full_name': loan_data.get('full_name', 'Unknown'),
                'email': loan_data.get('email', 'unknown@example.com'),
                'phone': loan_data.get('phone_number', 'N/A'),
                'property_address': loan_data.get('property_address', 'N/A'),
                'property_zip': loan_data.get('property_zip_code', 'N/A'),
                'loan_purpose': loan_data.get('loan_purpose', 'N/A'),
                'purchase_price': str(loan_data.get('purchase_price', '0')),
                'down_payment': str(loan_data.get('down_payment', '0')),
                'annual_income': str(loan_data.get('annual_income', '0'))
            }
            
            # Format Plaid data
            formatted_accounts = []
            for account in bank_accounts:
                formatted_accounts.append({
                    'account_id': account.get('account_id', 'N/A'),
                    'name': account.get('name', 'Unknown Account'),
                    'type': account.get('type', 'depository'),
                    'subtype': account.get('subtype', 'checking'),
                    'balance': account.get('current_balance', 0),
                    'currency': account.get('currency', 'USD')
                })
            
            plaid_data = {
                'loan_application': {
                    'id': loan_id,
                    'full_name': loan_data.get('full_name', 'Unknown'),
                    'email': loan_data.get('email', 'unknown@example.com'),
                    'annual_income': str(loan_data.get('annual_income', '0')),
                    'purchase_price': str(loan_data.get('purchase_price', '0')),
                    'down_payment': str(loan_data.get('down_payment', '0')),
                    'loan_purpose': loan_data.get('loan_purpose', 'N/A')
                },
                'bank_accounts': formatted_accounts,
                'total_balance': total_balance,
                'transaction_count': 0  # No transactions available
            }
            
            # Perform AI analysis
            try:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.error("OPENAI_API_KEY not found in environment!")
                    decision = 'pending'
                else:
                    engine = PreApprovalEngine(
                        openai_api_key=api_key
                    )
                    decision = engine.analyze(user_input, plaid_data)
                    logger.info(f"✅ AI Decision for loan {loan_id}: {decision}")
            except Exception as e:
                logger.error(f"❌ AI analysis failed: {str(e)}", exc_info=True)
                decision = 'pending'
                logger.info(f"Using default decision (pending) for loan {loan_id}")
            
            # Generate PDF
            pdf_content = self._generate_analysis_pdf(user_input, plaid_data, decision)
            
            return HttpResponse(
                pdf_content,
                content_type='application/pdf',
                headers={'Content-Disposition': f'attachment; filename="loan_analysis_{loan_id}.pdf"'}
            )
            
        except Exception as e:
            logger.error(f"Error in GeneratePDFFromBankDataView: {e}")
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_analysis_pdf(self, user_input, plaid_data, decision):
        """Generate PDF report from analysis data"""
        from reportlab.platypus import Image as RLImage, Table, TableStyle
        import os
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Logo and Title side by side
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=0,
            alignment=0
        )
        
        # Create header table with logo and title
        header_data = []
        if os.path.exists(logo_path):
            try:
                logo = RLImage(logo_path, width=1.2*inch, height=0.6*inch)
                title = Paragraph('Mortgage Pre-Approval', title_style)
                header_data = [[logo, title]]
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
                header_data = [['', Paragraph('Mortgage Pre-Approval', title_style)]]
        else:
            header_data = [['', Paragraph('Mortgage Pre-Approval', title_style)]]
        
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Compact styles
        app_style = ParagraphStyle('AppStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#333333'), spaceAfter=4)
        normal_compact = ParagraphStyle('NormalCompact', parent=styles['Normal'], fontSize=9, leading=11)
        
        # Applicant Information
        elements.append(Paragraph('APPLICANT INFORMATION', app_style))
        elements.append(Paragraph(f'<b>Name:</b> {user_input.get("full_name", "N/A")}', normal_compact))
        elements.append(Paragraph(f'<b>Email:</b> {user_input.get("email", "N/A")}', normal_compact))
        elements.append(Paragraph(f'<b>Phone:</b> {user_input.get("phone", "N/A")}', normal_compact))
        elements.append(Spacer(1, 0.1*inch))
        
        # Loan Details
        elements.append(Paragraph('LOAN DETAILS', app_style))
        elements.append(Paragraph(f'<b>Purpose:</b> {plaid_data["loan_application"].get("loan_purpose", "N/A")}', normal_compact))
        
        # Format prices
        try:
            purchase_price = float(plaid_data["loan_application"].get("purchase_price", "0"))
            elements.append(Paragraph(f'<b>Purchase Price:</b> ${purchase_price:,.2f}', normal_compact))
        except (ValueError, TypeError):
            elements.append(Paragraph(f'<b>Purchase Price:</b> {plaid_data["loan_application"].get("purchase_price", "N/A")}', normal_compact))
        
        try:
            down_payment = float(plaid_data["loan_application"].get("down_payment", "0"))
            elements.append(Paragraph(f'<b>Down Payment:</b> ${down_payment:,.2f}', normal_compact))
        except (ValueError, TypeError):
            elements.append(Paragraph(f'<b>Down Payment:</b> {plaid_data["loan_application"].get("down_payment", "N/A")}', normal_compact))
        
        try:
            annual_income = float(plaid_data["loan_application"].get("annual_income", "0"))
            elements.append(Paragraph(f'<b>Annual Income:</b> ${annual_income:,.2f}', normal_compact))
        except (ValueError, TypeError):
            elements.append(Paragraph(f'<b>Annual Income:</b> {plaid_data["loan_application"].get("annual_income", "N/A")}', normal_compact))
        
        elements.append(Spacer(1, 0.1*inch))
        
        # Bank Accounts
        elements.append(Paragraph('BANK ACCOUNTS', app_style))
        
        if plaid_data['bank_accounts']:
            for account in plaid_data['bank_accounts']:
                try:
                    balance = float(account.get("balance", 0) or 0)
                    account_text = f'<b>{account.get("name", "Unknown")}</b> ({account.get("subtype", "N/A").title()}): ${balance:,.2f}'
                except (ValueError, TypeError):
                    account_text = f'<b>{account.get("name", "Unknown")}</b> ({account.get("subtype", "N/A").title()}): {account.get("balance", "N/A")}'
                elements.append(Paragraph(account_text, normal_compact))
            elements.append(Paragraph(f'<b>Total Balance:</b> {plaid_data.get("total_balance", "$0.00")}', normal_compact))
        else:
            elements.append(Paragraph('No bank accounts connected', normal_compact))
        
        elements.append(Spacer(1, 0.15*inch))
        
        # Analysis Decision
        decision_lower = str(decision).lower() if decision else 'pending'
        decision_text = decision_lower.upper()
        
        # Color based on decision
        if decision_lower in ['approve', 'approved', 'yes', 'accept']:
            decision_color = colors.HexColor('#28a745')  # GREEN
        elif decision_lower in ['pending', 'maybe', 'review']:
            decision_color = colors.HexColor('#ffc107')  # YELLOW
        else:
            decision_color = colors.HexColor('#dc3545')  # RED
        
        decision_style = ParagraphStyle(
            'DecisionStyle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=decision_color,
            spaceAfter=10
        )
        elements.append(Paragraph(f'<b>Status: {decision_text}</b>', decision_style))
        
        elements.append(Spacer(1, 0.1*inch))
        
        # Disclaimer text (matching the Mortgage Pre-Approval style)
        disclaimer_style = ParagraphStyle(
            'DisclaimerStyle',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#666666'),
            alignment=0,
            leading=9
        )
        
        disclaimer_text = """This pre-approval letter is issued based on a preliminary review of the information provided by the applicant(s), including but not limited to credit, income(s), and asset(s). This letter is not a commitment, promise, or assurance of any type or in any form whatsoever of a commitment or guarantee that a loan will be approved or funded. Any such commitment would be subject to satisfaction of all lender's requirements and conditions. Final loan approval is subject to full underwriting, verification of all information, acceptable appraisal review, property title, lender final approval, and satisfaction of all lender requirements and conditions. Any change in the applicant's financial condition, credit profile, interest rates, loan programs, or market conditions may result in modification or withdrawal of this pre-approval without notice. The lender assumes no liability for any reliance placed on this letter."""
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        elements.append(Spacer(1, 0.1*inch))
        
        # Footer with lender info
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#333333'),
            alignment=0,
            leading=9
        )
        
        footer_text = """Midland Federal Savings and Loan Association NMLS#446746<br/>
Copyright © 2025 Midland Federal Savings and Loan Association.<br/>
8929 South Harlem Avenue Bridgeview, Illinois 60455"""
        
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

