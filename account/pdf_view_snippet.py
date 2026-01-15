
class GeneratePDFFromBankDataView(APIView):
    """Generate PDF directly from bank data without Plaid connection requirement"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="📄 Generate PDF from Bank Data (Direct)",
        operation_description="""
        Generate PDF report directly from bank data without requiring a Plaid connection.
        
        **Use this when:**
        - You have already fetched bank data from /api/plaid/connect/
        - You want to generate PDF from the bank data response
        - You need to test PDF generation with dummy data
        
        **What it does:**
        1. Takes loan application data and bank account data
        2. Processes through AI PreApproval Engine for decision
        3. Generates professional PDF report
        4. Returns downloadable PDF
        
        **Response:**
        - Content-Type: application/pdf
        - Filename: loan_analysis_{loan_id}.pdf
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'loan_application_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Loan Application ID",
                    example=57
                ),
                'loan_application': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Loan application data from /api/plaid/connect/ response",
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                        'annual_income': openapi.Schema(type=openapi.TYPE_STRING),
                        'purchase_price': openapi.Schema(type=openapi.TYPE_STRING),
                        'down_payment': openapi.Schema(type=openapi.TYPE_STRING),
                        'loan_purpose': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
                'bank_accounts': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'account_id': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'type': openapi.Schema(type=openapi.TYPE_STRING),
                            'subtype': openapi.Schema(type=openapi.TYPE_STRING),
                            'current_balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'available_balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'currency': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    description="Bank accounts data from /api/plaid/connect/ response"
                ),
                'total_balance': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Total balance (formatted as $X,XXX.XX)",
                    example="$10,500.00"
                )
            },
            required=['loan_application_id', 'loan_application', 'bank_accounts', 'total_balance']
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
                    raise ValueError('OPENAI_API_KEY environment variable not set')
                engine = PreApprovalEngine(
                    openai_api_key=api_key
                )
                decision = engine.analyze(user_input, plaid_data)
                logger.info(f"AI Decision for loan {loan_id}: {decision}")
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
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
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph('LOAN ANALYSIS REPORT', title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Applicant Information
        app_style = ParagraphStyle('AppStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#333333'))
        elements.append(Paragraph('APPLICANT INFORMATION', app_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(f'<b>Name:</b> {user_input.get("full_name", "N/A")}', styles['Normal']))
        elements.append(Paragraph(f'<b>Email:</b> {user_input.get("email", "N/A")}', styles['Normal']))
        elements.append(Paragraph(f'<b>Phone:</b> {user_input.get("phone", "N/A")}', styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Loan Details
        elements.append(Paragraph('LOAN DETAILS', app_style))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(f'<b>Purpose:</b> {plaid_data["loan_application"].get("loan_purpose", "N/A")}', styles['Normal']))
        elements.append(Paragraph(f'<b>Purchase Price:</b> ${plaid_data["loan_application"].get("purchase_price", "0"):,.2f}', styles['Normal']))
        elements.append(Paragraph(f'<b>Down Payment:</b> ${plaid_data["loan_application"].get("down_payment", "0"):,.2f}', styles['Normal']))
        elements.append(Paragraph(f'<b>Annual Income:</b> ${plaid_data["loan_application"].get("annual_income", "0"):,.2f}', styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Bank Accounts
        elements.append(Paragraph('BANK ACCOUNTS', app_style))
        elements.append(Spacer(1, 0.1*inch))
        
        if plaid_data['bank_accounts']:
            for account in plaid_data['bank_accounts']:
                account_text = f'<b>{account.get("name", "Unknown")}</b> ({account.get("subtype", "N/A").title()}): ${account.get("balance", 0):,.2f}'
                elements.append(Paragraph(account_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f'<b>Total Balance:</b> {plaid_data.get("total_balance", "$0.00")}', styles['Normal']))
        else:
            elements.append(Paragraph('No bank accounts connected', styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Analysis Decision
        decision_text = decision.upper() if decision else 'PENDING'
        decision_color = colors.HexColor('#28a745') if decision in ['approved', 'yes'] else (colors.HexColor('#ffc107') if decision in ['pending', 'maybe'] else colors.HexColor('#dc3545'))
        
        decision_style = ParagraphStyle(
            'DecisionStyle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=decision_color,
            spaceAfter=20
        )
        elements.append(Paragraph(f'<b>Status: {decision_text}</b>', decision_style))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            'This analysis is based on the applicant\'s financial data from connected bank accounts.',
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
