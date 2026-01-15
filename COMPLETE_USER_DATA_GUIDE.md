# 🏦 COMPLETE USER DATA API - Testing Guide

## What You Get: Loan Application + Bank Account Data

Your Django API now returns BOTH loan application info AND bank account details when a user connects their Plaid account.

---

## 📋 API Endpoints:

### 1. Create Loan Application (Step 1)
**POST** `http://127.0.0.1:8000/api/loan-application/`

**Body:**
```json
{
    "full_name": "John Smith",
    "email": "john.smith@example.com", 
    "phone_number": "555-123-4567",
    "property_zip_code": "10003",
    "property_address": "10003 Broadway Road, New York, NY 10003",
    "annual_income": "85000.00",
    "purchase_price": "450000.00", 
    "down_payment": "90000.00",
    "loan_purpose": "Purchase"
}
```

**Response:**
```json
{
    "id": 1,
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "plaid_link_token": "link-sandbox-af1a0811-xxxx-xxxx",
    "message": "Loan application created successfully. Use the plaid_link_token to connect your bank account."
}
```

---

### 2. Connect Bank Account & Get ALL Info (Step 2)
**POST** `http://127.0.0.1:8000/api/plaid/connect-all/`

**Body:**
```json
{
    "public_token": "public-sandbox-xxxxx-xxxx-xxxx",
    "loan_application_id": 1
}
```

**Complete Response (Loan + Bank Data):**
```json
{
    "loan_application_info": {
        "id": 1,
        "full_name": "John Smith",
        "email": "john.smith@example.com", 
        "phone_number": "555-123-4567",
        "property_details": {
            "zip_code": "10003",
            "address": "10003 Broadway Road, New York, NY 10003"
        },
        "loan_details": {
            "purpose": "Purchase",
            "purchase_price": "$450,000.00",
            "down_payment": "$90,000.00",
            "annual_income": "$85,000.00"
        },
        "application_date": "2025-09-03T12:00:00Z"
    },
    "bank_account_info": {
        "accounts": [
            {
                "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
                "name": "Plaid Checking",
                "official_name": "Plaid Gold Standard 0% Interest Checking",
                "type": "depository",
                "subtype": "checking",
                "current_balance": 100.0,
                "available_balance": 100.0,
                "currency": "USD",
                "balance_formatted": "$100.00"
            },
            {
                "account_id": "dVzbVMLjrxTnLjX4G66XUp5GLklm4oiZy88yK",
                "name": "Plaid Saving", 
                "official_name": "Plaid Silver Standard 0.1% Interest Saving",
                "type": "depository",
                "subtype": "savings",
                "current_balance": 210.0,
                "available_balance": 210.0,
                "currency": "USD",
                "balance_formatted": "$210.00"
            }
        ],
        "financial_summary": {
            "total_balance": "$310.00",
            "checking_balance": "$100.00", 
            "savings_balance": "$210.00",
            "account_count": 2
        },
        "recent_transactions": [
            {
                "transaction_id": "lPNjeW1nR6CDn5okmGQ6hEpMo4lLNoSrzqDje",
                "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
                "amount": 5.4,
                "amount_formatted": "$5.40",
                "date": "2025-09-01",
                "name": "Starbucks",
                "merchant_name": "Starbucks",
                "category": ["Food and Drink", "Restaurants", "Coffee Shop"],
                "type": "debit"
            }
        ],
        "plaid_connection_status": "Successfully connected"
    },
    "analysis": {
        "monthly_income": "$7,083.33",
        "debt_to_income_estimate": "25.4%", 
        "down_payment_percentage": "20.0%",
        "liquid_assets": "$310.00"
    },
    "status": "complete_with_bank_data",
    "timestamp": "2025-09-03T12:00:00Z"
}
```

---

## 🧪 Testing in Postman:

### Your Plaid Sandbox Configuration:
- **Client ID**: 689eb34eb4d18e0022963556
- **Environment**: sandbox 
- **Test User**: John Smith, Jane Doe (10003 Broadway Road, NY)

### Test Credentials:
- **Username**: `user_good`
- **Password**: `pass_good`
- **Institution**: Any bank (Chase, Bank of America, etc.)

---

## 🚀 Complete Testing Workflow:

1. **Create Loan Application** → Get `plaid_link_token`
2. **Use Plaid Link** (frontend) → Get `public_token` 
3. **Connect Bank & Get All Info** → Get complete user data

### Sample Test Data:
```json
{
    "full_name": "Jane Doe",
    "email": "jane.doe@test.com",
    "phone_number": "555-987-6543", 
    "property_zip_code": "10003",
    "property_address": "456 Test Avenue, New York, NY 10003",
    "annual_income": "95000.00",
    "purchase_price": "500000.00",
    "down_payment": "100000.00", 
    "loan_purpose": "Purchase"
}
```

---

## ✅ What You Get:

- ✅ **Complete Loan Application Data** - All form fields
- ✅ **Bank Account Details** - Account names, types, balances
- ✅ **Financial Summary** - Total balance, checking/savings breakdown
- ✅ **Recent Transactions** - Last 15 transactions with details
- ✅ **Financial Analysis** - DTI ratio, down payment %, liquid assets
- ✅ **Formatted Data** - Currency formatting, percentages

Perfect for loan underwriting and financial analysis!
