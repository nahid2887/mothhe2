#!/usr/bin/env python
"""
Test the exact payload being sent to the PDF endpoint
"""
import os
import sys
import django
from dotenv import load_dotenv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/c/mothyedward')
django.setup()

from account.aiengine import PreApprovalEngine

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"✅ API Key: {api_key[:30]}...")

# Exact payload from your request
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

print("\n🔍 Testing exact payload...")
print(f"Annual Income: {plaid_data['loan_application']['annual_income']}")
print(f"Purchase Price: {plaid_data['loan_application']['purchase_price']}")
print(f"Down Payment: {plaid_data['loan_application']['down_payment']}")
print(f"Total Balance: {plaid_data['total_balance']}")

try:
    engine = PreApprovalEngine(openai_api_key=api_key)
    decision = engine.analyze(user_input, plaid_data)
    print(f"\n✅ Decision: {decision.upper()}")
    
    if decision.lower() == "approve":
        print("🎉 This SHOULD show APPROVE in PDF!")
    else:
        print(f"⚠️  Decision is: {decision}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
