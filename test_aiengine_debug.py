#!/usr/bin/env python
"""
Debug script to test the AI engine directly
"""
import os
from dotenv import load_dotenv
from account.aiengine import PreApprovalEngine

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"✅ API Key loaded: {api_key[:20]}..." if api_key else "❌ No API key found")

# Test data
user_input = {
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone": "98788",
    "property_zip": "88",
    "property_address": "123 Main Street, Anytown",
    "loan_purpose": "Purchase"
}

plaid_data = {
    "loan_application": {
        "annual_income": "250000.00",
        "purchase_price": "500000.00",
        "down_payment": "50000.00"
    },
    "total_balance": "$300000.00"
}

# Test the AI engine
print("\n🔍 Testing AI Engine...")
print(f"Annual Income: $250,000")
print(f"Purchase Price: $500,000")
print(f"Down Payment: $50,000 (10%)")
print(f"Liquid Assets: $300,000")
print(f"Expected: APPROVE (strong financials)")

try:
    engine = PreApprovalEngine(api_key, model='gpt-4')
    decision = engine.analyze(user_input, plaid_data)
    print(f"\n✅ Decision: {decision.upper()}")
    
    if decision.lower() == "approve":
        print("🎉 AI Engine is working correctly!")
    else:
        print("❌ Unexpected decision - check your OpenAI API key")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Check your OpenAI API key in .env file")
