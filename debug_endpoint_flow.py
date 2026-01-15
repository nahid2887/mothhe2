#!/usr/bin/env python
"""
Debug the exact flow in the endpoint
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/c/mothyedward')
django.setup()

from dotenv import load_dotenv
from account.aiengine import PreApprovalEngine
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key: {api_key[:30]}...")

# Exact data from the request
user_input = {
    'full_name': 'Mr Kim878',
    'email': 'user@example.com',
    'phone': '98788',
    'property_address': '123 Main Street, Anytown',
    'property_zip': '88',
    'loan_purpose': 'Purchase',
    'purchase_price': '$500000.00',
    'down_payment': '$50000.00',
    'annual_income': '$250000.00'
}

# Format data exactly as the endpoint does
formatted_accounts = [
    {
        'account_id': '5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj',
        'name': 'Business Enhanced Checking',
        'type': 'depository',
        'subtype': 'checking',
        'balance': 300000,
        'currency': 'USD'
    }
]

plaid_data = {
    'loan_application': {
        'id': 57,
        'full_name': 'Mr Kim878',
        'email': 'user@example.com',
        'annual_income': '$250000.00',
        'purchase_price': '$500000.00',
        'down_payment': '$50000.00',
        'loan_purpose': 'Purchase'
    },
    'bank_accounts': formatted_accounts,
    'total_balance': '$300000.00',
    'transaction_count': 0
}

print("\n🔍 Simulating endpoint logic...")
print(f"User Input: {user_input}")
print(f"Plaid Data: {plaid_data}")

# Try the exact endpoint logic
try:
    api_key_from_env = os.getenv('OPENAI_API_KEY')
    if not api_key_from_env:
        print("❌ OPENAI_API_KEY not found in environment!")
        decision = 'pending'
    else:
        print(f"✅ API Key found: {api_key_from_env[:30]}...")
        engine = PreApprovalEngine(
            openai_api_key=api_key_from_env
        )
        decision = engine.analyze(user_input, plaid_data)
        print(f"✅ AI Decision: {decision}")
        logger.info(f"✅ AI Decision for loan 57: {decision}")
except Exception as e:
    print(f"❌ AI analysis failed: {str(e)}")
    import traceback
    traceback.print_exc()
    decision = 'pending'
    logger.info(f"Using default decision (pending) for loan 57")

print(f"\n📊 Final decision: {decision}")

# Now test the PDF rendering with this decision
print("\n🎨 Testing PDF rendering with this decision...")

decision_lower = str(decision).lower() if decision else 'pending'
if decision_lower in ['approve', 'approved', 'yes', 'accept']:
    decision_color = '#28a745'  # GREEN
    decision_text = 'APPROVED'
elif decision_lower in ['pending', 'maybe', 'review']:
    decision_color = '#ffc107'  # YELLOW
    decision_text = 'PENDING REVIEW'
else:
    decision_color = '#dc3545'  # RED
    decision_text = 'DISAPPROVED'

print(f"Decision: {decision_lower}")
print(f"Decision Text: {decision_text}")
print(f"Color: {decision_color}")
print(f"\n✅ PDF will show: {decision_text} in color {decision_color}")
