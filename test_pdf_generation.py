#!/usr/bin/env python
"""
Standalone test - generate PDF directly without Django server
"""
import os
import sys
from dotenv import load_dotenv

# Add path
sys.path.insert(0, '/c/mothyedward')

# Load environment variables
load_dotenv()

# Import after setting path
from account.aiengine import PreApprovalEngine
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key: {api_key[:30]}...")

# Exact payload
user_input = {
    'full_name': 'Mr Kim',
    'email': 'user@example.com',
    'phone': '98788',
    'property_address': '123 Main Street, Anytown',
    'property_zip': '88',
    'loan_purpose': 'Purchase',
    'purchase_price': '$500000.00',
    'down_payment': '$50000.00',
    'annual_income': '$250000.00'
}

plaid_data = {
    'loan_application': {
        'id': 57,
        'full_name': 'Mr Kim',
        'email': 'user@example.com',
        'annual_income': '$250000.00',
        'purchase_price': '$500000.00',
        'down_payment': '$50000.00',
        'loan_purpose': 'Purchase'
    },
    'bank_accounts': [
        {
            'account_id': '5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj',
            'name': 'Business Enhanced Checking',
            'type': 'depository',
            'subtype': 'checking',
            'balance': 300000,
            'currency': 'USD'
        }
    ],
    'total_balance': '$300000.00',
    'transaction_count': 0
}

# Get AI decision
print("\n🔍 Getting AI decision...")
engine = PreApprovalEngine(openai_api_key=api_key)
decision = engine.analyze(user_input, plaid_data)
print(f"✅ AI Decision: {decision}")

# Generate PDF
print("\n📄 Generating PDF...")
buffer = io.BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=letter)
elements = []
styles = getSampleStyleSheet()

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

# Decision logic (NEW FIX)
decision_lower = str(decision).lower() if decision else 'pending'
decision_text = decision_lower.upper()

if decision_lower in ['approve', 'approved', 'yes', 'accept']:
    decision_color = colors.HexColor('#28a745')  # GREEN
elif decision_lower in ['pending', 'maybe', 'review']:
    decision_color = colors.HexColor('#ffc107')  # YELLOW
else:
    decision_color = colors.HexColor('#dc3545')  # RED

print(f"Decision: {decision_lower}")
print(f"Decision Text: {decision_text}")
print(f"Color: {decision_color.hexval if hasattr(decision_color, 'hexval') else decision_color}")

decision_style = ParagraphStyle(
    'DecisionStyle',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=decision_color,
    spaceAfter=20
)
elements.append(Paragraph(f'<b>Status: {decision_text}</b>', decision_style))

doc.build(elements)
buffer.seek(0)

# Save to file
output_path = r'c:\mothyedward\test_loan_analysis.pdf'
with open(output_path, 'wb') as f:
    f.write(buffer.getvalue())

print(f"\n✅ PDF saved to: {output_path}")
print(f"   Status should show: {decision_text} in {'GREEN' if decision_lower in ['approve', 'approved', 'yes', 'accept'] else 'RED' if decision_lower not in ['pending', 'maybe', 'review'] else 'YELLOW'}")
