# Complete API Workflow - Swagger Documentation

## 🚀 Full Loan Application to PDF Generation Flow

### Overview
This document shows the complete workflow across 3 API endpoints with all required data and expected responses.

---

## Step 1️⃣: Create Loan Application

### Endpoint
```
POST /api/loan-application/
```

### What It Does
- Creates a new loan application
- Generates a Plaid link token (valid for 10 minutes)
- Returns a ready-to-use Plaid UI URL
- Sends confirmation email

### Request Body
```json
{
  "full_name": "Mr Kim",
  "email": "user@example.com",
  "phone": "98788",
  "property_address": "123 Main Street",
  "property_zip": "88",
  "loan_purpose": "Purchase",
  "purchase_price": "500000",
  "down_payment": "100000"
}
```

### Success Response (201)
```json
{
  "id": 57,
  "full_name": "Mr Kim",
  "email": "user@example.com",
  "plaid_link_token": "link-production-590bc0e2-6078-4e37-b7b8-fa6696409d41",
  "plaid_ui_url": "http://127.0.0.1:8000/get_public_token_manual.html?token=link-production-590bc0e2-6078-4e37-b7b8-fa6696409d41&loan_id=57",
  "user_input": {
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone": "98788",
    "property_zip": "88",
    "property_address": "123 Main Street",
    "loan_purpose": "Purchase",
    "purchase_price": "500000",
    "down_payment": "100000"
  },
  "instructions": "Copy the plaid_ui_url and open it in your browser. Login to your bank to get the public token.",
  "message": "Loan application created successfully. Environment: production. NEXT STEP: Open plaid_ui_url in browser to get public token."
}
```

### What to Do Next
1. **Save the Loan ID:** `57` (you'll need this for the next steps)
2. **Open plaid_ui_url in browser** or use the link_token with your own Plaid implementation
3. **User logs into their bank** when Plaid Link opens
4. **Copy the public token** that Plaid returns

---

## Step 2️⃣: Connect Bank Account (Exchange Public Token)

### Endpoint
```
POST /api/plaid/connect/
```

### What It Does
- Exchanges the public token for a secure access token
- Retrieves all connected bank accounts
- Fetches real account balances
- Saves Plaid connection for future use
- Retrieves recent transactions

### Request Body
```json
{
  "public_token": "public-production-xxx...",
  "loan_application_id": 57
}
```

**Note:** The `public_token` comes from Plaid Link after user logs in. Get it by:
1. Opening the `plaid_ui_url` from Step 1
2. Clicking "Open Plaid & Get Public Token"
3. Logging into your real bank
4. Copying the token shown on the page

### Success Response (200)
```json
{
  "loan_application": {
    "id": 57,
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone_number": "98788",
    "property_zip_code": "88",
    "property_address": "123 Main Street",
    "annual_income": "75677.00",
    "purchase_price": "500000.00",
    "down_payment": "100000.00",
    "loan_purpose": "Purchase",
    "cash_out_amount": "100.00",
    "created_at": "2025-11-17T22:39:54.132478+00:00"
  },
  "bank_accounts": [
    {
      "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
      "name": "Business Enhanced Checking",
      "official_name": "Business Enhanced Checking",
      "type": "depository",
      "subtype": "checking",
      "current_balance": 25000,
      "available_balance": 24500,
      "currency": "USD"
    },
    {
      "account_id": "xyz123abc456",
      "name": "Savings Account",
      "official_name": "Premium Savings",
      "type": "depository",
      "subtype": "savings",
      "current_balance": 50000,
      "available_balance": 50000,
      "currency": "USD"
    }
  ],
  "total_balance": "$75,000.00",
  "recent_transactions": [
    {
      "transaction_id": "txn_123",
      "date": "2025-11-17",
      "amount": -500,
      "description": "AMAZON PURCHASE",
      "merchant_name": "Amazon.com"
    }
  ],
  "plaid_connected": true,
  "message": "Bank account connected successfully!"
}
```

### What to Do Next
1. **Verify the bank data** is correct
2. **Review total balance** ($75,000.00 in this example)
3. **Check the bank accounts** that were connected
4. **Proceed to Step 3** to generate the PDF report

---

## Step 3️⃣: Generate Bank Analysis PDF

### Endpoint
```
POST /api/bank-analysis-pdf/
```

### What It Does
- Analyzes the connected bank data
- Processes financial information through AI engine
- Generates a professional PDF report
- Returns downloadable PDF file

### Request Body
```json
{
  "loan_application_id": 57
}
```

### Success Response (200)
- **Content-Type:** `application/pdf`
- **File:** `loan_analysis_57.pdf`
- **Response:** Binary PDF file

### PDF Contents
The generated PDF includes:
- ✅ Applicant Information (Name, Email, Phone, Income)
- ✅ Loan Details (Address, Purpose, Purchase Price, Down Payment)
- ✅ Connected Bank Accounts with Balances
- ✅ Total Balance Summary
- ✅ Transaction Count
- ✅ AI Analysis Decision (APPROVED/PENDING)

---

## Error Handling

### Step 1 - Create Loan Application

**400 Bad Request**
```json
{
  "full_name": ["This field may not be blank."],
  "email": ["Enter a valid email address."]
}
```

---

### Step 2 - Connect Bank Account

**400 Bad Request - Invalid Public Token**
```json
{
  "error": "Invalid public token format"
}
```

**400 Bad Request - Missing Loan ID**
```json
{
  "error": "loan_application_id is required"
}
```

**404 Not Found - Loan doesn't exist**
```json
{
  "detail": "Not found."
}
```

---

### Step 3 - Generate PDF

**400 Bad Request - Missing loan_application_id**
```json
{
  "error": "loan_application_id is required"
}
```

**404 Not Found - No Plaid connection**
```json
{
  "error": "No Plaid connection found for this loan"
}
```

**500 Server Error - Plaid API failure**
```json
{
  "error": "Failed to fetch Plaid data: [specific error]"
}
```

---

## Complete cURL Examples

### 1. Create Loan Application
```bash
curl -X POST http://127.0.0.1:8000/api/loan-application/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone": "98788",
    "property_address": "123 Main Street",
    "property_zip": "88",
    "loan_purpose": "Purchase",
    "purchase_price": "500000",
    "down_payment": "100000"
  }'
```

### 2. Connect Bank Account
```bash
curl -X POST http://127.0.0.1:8000/api/plaid/connect/ \
  -H "Content-Type: application/json" \
  -d '{
    "public_token": "public-production-xxx...",
    "loan_application_id": 57
  }'
```

### 3. Generate PDF
```bash
curl -X POST http://127.0.0.1:8000/api/bank-analysis-pdf/ \
  -H "Content-Type: application/json" \
  -d '{
    "loan_application_id": 57
  }' \
  --output loan_analysis_57.pdf
```

---

## Access Swagger UI

To view all APIs with interactive testing:
```
http://127.0.0.1:8000/swagger/
```

## Postman Collection

Import this collection in Postman to test all endpoints:
- Plaid_Testing_Collection.postman_collection.json

---

## Key Points

✅ **Token Expiration:** Link tokens expire in 10 minutes
✅ **Bank Login:** Use your REAL bank credentials (not test credentials)
✅ **Security:** Public tokens are short-lived and single-use
✅ **Async Processing:** PDF generation uses AI for financial analysis
✅ **Error Recovery:** Each step can be retried if needed

