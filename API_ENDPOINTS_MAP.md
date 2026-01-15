# API Endpoints Map & Reference

## 📍 Quick Reference Guide

### All Available Endpoints

| # | Endpoint | Method | Purpose | Status |
|---|----------|--------|---------|--------|
| 1️⃣ | `/api/loan-application/` | POST | Create loan & get link token | ✅ Production Ready |
| 2️⃣ | `/api/plaid/connect/` | POST | Connect bank account | ✅ Production Ready |
| 3️⃣ | `/api/bank-analysis-pdf/` | POST | Generate PDF report | ✅ Production Ready |
| 📄 | `/swagger/` | GET | Interactive API documentation | ✅ Available |
| 📄 | `/redoc/` | GET | ReDoc API documentation | ✅ Available |

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Create Loan Application                            │
│ POST /api/loan-application/                                │
│ Input: Applicant info, Property, Loan details             │
│ Output: loan_id, link_token, plaid_ui_url               │
│ Status: 201 Created                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Open Plaid Link & Connect Bank                     │
│ Browser: Open plaid_ui_url                                 │
│ User: Login to real bank account                           │
│ Output: public_token from Plaid                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2b: Exchange Public Token                             │
│ POST /api/plaid/connect/                                   │
│ Input: public_token, loan_application_id                  │
│ Output: bank_accounts, balances, transactions            │
│ Status: 200 OK                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Generate PDF Report                                │
│ POST /api/bank-analysis-pdf/                               │
│ Input: loan_application_id                                │
│ Output: PDF file (loan_analysis_XX.pdf)                  │
│ Status: 200 OK (application/pdf)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Detailed Endpoint Reference

### Endpoint 1: Create Loan Application

**Purpose:** Initialize loan application and get Plaid integration credentials

**URL:**
```
POST http://127.0.0.1:8000/api/loan-application/
```

**Required Fields:**
- `full_name` (string)
- `email` (string)
- `property_address` (string)
- `property_zip` (string)
- `loan_purpose` (string: "Purchase" | "Refinance" | "Cash-Out")
- `purchase_price` (decimal)
- `down_payment` (decimal)

**Optional Fields:**
- `phone` (string)
- `annual_income` (decimal)
- `cash_out_amount` (decimal)

**Response Fields:**
- `id` - Loan Application ID (save this!)
- `plaid_link_token` - Token for Plaid Link UI
- `plaid_ui_url` - Ready-to-use URL for browser
- `user_input` - Echo of submitted data
- `instructions` - What to do next

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/loan-application/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "property_address": "123 Main St",
    "property_zip": "12345",
    "loan_purpose": "Purchase",
    "purchase_price": "500000",
    "down_payment": "100000"
  }'
```

---

### Endpoint 2: Exchange Public Token for Bank Data

**Purpose:** Convert public token to access token and retrieve bank information

**URL:**
```
POST http://127.0.0.1:8000/api/plaid/connect/
```

**Required Fields:**
- `public_token` (string) - From Plaid Link
- `loan_application_id` (integer) - From Step 1 response

**Response Fields:**
- `loan_application` - Updated loan data
- `bank_accounts` - Array of connected accounts
  - `account_id` - Unique account identifier
  - `name` - Account name
  - `type` - Account type (depository, credit, etc.)
  - `subtype` - Account subtype (checking, savings, etc.)
  - `current_balance` - Current available balance
  - `available_balance` - Available balance
  - `currency` - Currency code (USD, etc.)
- `total_balance` - Sum of all accounts
- `recent_transactions` - Latest transactions
- `plaid_connected` - Boolean status
- `message` - Success message

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/plaid/connect/ \
  -H "Content-Type: application/json" \
  -d '{
    "public_token": "public-production-...",
    "loan_application_id": 57
  }'
```

---

### Endpoint 3: Generate Bank Analysis PDF

**Purpose:** Create professional PDF report with AI financial analysis

**URL:**
```
POST http://127.0.0.1:8000/api/bank-analysis-pdf/
```

**Required Fields:**
- `loan_application_id` (integer) - Must have active Plaid connection

**Response:**
- `Content-Type: application/pdf`
- File name: `loan_analysis_{id}.pdf`

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/bank-analysis-pdf/ \
  -H "Content-Type: application/json" \
  -d '{"loan_application_id": 57}' \
  --output loan_analysis_57.pdf
```

**PDF Contents:**
- Applicant name, email, phone, income
- Property address, loan purpose
- Loan amount, down payment
- All connected bank accounts and balances
- AI analysis decision

---

## 🔐 Security Notes

- ✅ All endpoints allow unauthenticated access (AllowAny)
- ✅ Public tokens are single-use and short-lived
- ✅ Access tokens stored securely in database
- ✅ No sensitive data stored in URLs
- ✅ Bank credentials never stored (Plaid handles login)

---

## 🧪 Testing

### View Interactive Swagger UI
```
http://127.0.0.1:8000/swagger/
```
- Try out all endpoints
- See request/response schemas
- Test with real data

### View ReDoc Documentation
```
http://127.0.0.1:8000/redoc/
```
- Clean read-only documentation
- Perfect for sharing with clients

---

## 🐛 Common Issues & Solutions

### Issue: "Plaid SDK not available"
**Solution:** Install plaid-python
```bash
pip install plaid-python
```

### Issue: "No Plaid connection found"
**Solution:** Make sure Step 2 was completed successfully

### Issue: "Invalid public token"
**Solution:** Get a fresh public token from Plaid Link

### Issue: PDF is blank
**Solution:** Ensure loan has connected bank accounts

---

## 📈 Data Flow

```
User Application
       │
       ▼
POST /api/loan-application/
       │
       ├─→ Django: Save loan
       ├─→ Plaid SDK: Create link_token
       ├─→ Email: Send confirmation
       │
       ▼
Response: { id, link_token, plaid_ui_url }
       │
       ▼
Browser: Open plaid_ui_url
       │
       ▼
Plaid Link UI
       │
       ├─→ User selects bank
       ├─→ User logs in (Plaid handles this)
       │
       ▼
Plaid: Generate public_token
       │
       ▼
POST /api/plaid/connect/
       │
       ├─→ Plaid SDK: Exchange public_token → access_token
       ├─→ Plaid SDK: Get accounts, balances, transactions
       ├─→ Django: Save access_token and data
       │
       ▼
Response: { bank_accounts, total_balance, transactions }
       │
       ▼
POST /api/bank-analysis-pdf/
       │
       ├─→ Django: Fetch Plaid data
       ├─→ AI Engine: Analyze financial data
       ├─→ ReportLab: Generate PDF
       │
       ▼
Response: PDF file for download
```

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f` Django console output
2. Review documentation in `/SWAGGER_API_WORKFLOW.md`
3. Test endpoints in Swagger UI: `/swagger/`
4. Check bank connection status in `/api/user/{id}/bank-details/`

