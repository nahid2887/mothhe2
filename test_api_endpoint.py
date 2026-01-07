#!/usr/bin/env python
"""
Test the API endpoint directly
"""
import requests
import json

url = "http://127.0.0.1:8000/api/generate-pdf-from-data/"

payload = {
    "loan_application_id": 57,
    "loan_application": {
      "full_name": "Mr Kim878",
      "email": "user@example.com",
      "phone_number": "98788",
      "property_zip_code": "88",
      "property_address": "123 Main Street, Anytown",
      "annual_income": "$250000.00",
      "purchase_price": "$500000.00",
      "down_payment": "$50000.00",
      "loan_purpose": "Purchase",
      "cash_out_amount": "$0.00"
    },
    "bank_accounts": [
      {
        "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
        "name": "Business Enhanced Checking",
        "official_name": "Business Enhanced Checking",
        "type": "depository",
        "subtype": "checking",
        "current_balance": 300000,
        "available_balance": 300000,
        "currency": "USD"
      }
    ],
    "total_balance": "$300000.00",
    "plaid_connected": True,
    "message": "Bank account connected successfully!"
}

print("🔍 Testing API endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\n✅ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        # Save PDF to file
        pdf_path = r'c:\mothyedward\api_response.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ PDF saved to: {pdf_path}")
        print(f"   File size: {len(response.content)} bytes")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
