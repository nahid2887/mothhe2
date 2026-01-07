# Plaid Integration Testing Guide

## API Endpoints for Testing in Postman

### Base URL: http://127.0.0.1:8000/api/

## Step 1: Create Loan Application
**POST** `/loan-application/`

**Request Body:**
```json
{
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "555-1234567",
    "property_zip_code": "12345",
    "property_address": "123 Main St, Anytown, USA",
    "annual_income": "75000.00",
    "purchase_price": "400000.00",
    "down_payment": "80000.00",
    "loan_purpose": "Purchase",
    "cash_out_amount": "0.00"
}
```

**Expected Response:**
```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "plaid_link_token": "link-sandbox-xxxxxx-xxxx-xxxx",
    "message": "Loan application created successfully. Use the plaid_link_token to connect your bank account."
}
```

## Step 2: Connect Bank Account with Plaid
**POST** `/plaid/connect/`

**Request Body:**
```json
{
    "public_token": "public-sandbox-xxxxxx-xxxx-xxxx",
    "loan_application_id": 1
}
```

**Expected Response (with real bank data):**
```json
{
    "loan_application": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "555-1234567",
        "property_zip_code": "12345",
        "property_address": "123 Main St, Anytown, USA",
        "annual_income": "75000.00",
        "purchase_price": "400000.00",
        "down_payment": "80000.00",
        "loan_purpose": "Purchase",
        "created_at": "2025-09-03T11:50:00Z"
    },
    "bank_accounts": [
        {
            "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
            "name": "Plaid Checking",
            "official_name": "Plaid Gold Standard 0% Interest Checking",
            "type": "depository",
            "subtype": "checking",
            "current_balance": 100.0,
            "available_balance": 100.0,
            "currency": "USD"
        },
        {
            "account_id": "dVzbVMLjrxTnLjX4G66XUp5GLklm4oiZy88yK",
            "name": "Plaid Saving",
            "official_name": "Plaid Silver Standard 0.1% Interest Saving",
            "type": "depository",
            "subtype": "savings",
            "current_balance": 210.0,
            "available_balance": 210.0,
            "currency": "USD"
        }
    ],
    "total_balance": "$310.00",
    "recent_transactions": [
        {
            "transaction_id": "lPNjeW1nR6CDn5okmGQ6hEpMo4lLNoSrzqDje",
            "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
            "amount": 5.4,
            "date": "2025-09-01",
            "name": "Starbucks",
            "merchant_name": "Starbucks",
            "category": ["Food and Drink", "Restaurants", "Coffee Shop"]
        }
    ],
    "plaid_connected": true,
    "message": "Bank account connected successfully!"
}
```

## Step 3: Get Complete Application Data
**GET** `/loan-application/{loan_id}/`

This will return the loan application with connected bank data.

## Plaid Sandbox Test Data

### Test Bank Credentials:
- **Institution**: Any bank (Chase, Bank of America, etc.)
- **Username**: `user_good`
- **Password**: `pass_good`

### What you'll see in Sandbox:
- **Checking Account**: Usually ~$100 balance
- **Savings Account**: Usually ~$200 balance  
- **Credit Card**: Usually with some balance
- **Recent Transactions**: Sample transactions with real-looking data

### Sandbox Limitations:
- Data is simulated but realistic
- Transactions are generated automatically
- Account balances are preset
- Institution names are real but data is fake

## Testing Flow:

1. **Create Loan Application** → Get `plaid_link_token`
2. **Use Plaid Link** (frontend) → Get `public_token`
3. **Connect Bank Account** → Exchange token and get bank data
4. **View Complete Data** → See loan application + bank information

## Postman Testing Tips:

1. Start with Step 1 to create a loan application
2. Copy the `plaid_link_token` from the response
3. For testing purposes, you can simulate Step 2 with a mock `public_token`
4. Or use the Plaid Link demo to get a real `public_token`

## Frontend Integration:
You would use the `plaid_link_token` with Plaid Link JavaScript library to let users connect their real bank accounts.
