# 🏦 Complete API Workflow Guide

## Your Current Status:
✅ **Step 1 Completed**: Loan Application Created
- Loan ID: 1
- User: "string" 
- Email: "Fw2pTxtWt2ZKoEH@ALShisOfFxAv.mqyo"
- Plaid Link Token: "link-sandbox-db3bc402-7880-4cd8-a423-5d975bde43c2"

## 📋 **Complete Workflow Steps:**

### **Step 1: Create Loan Application** ✅ DONE
```http
POST /api/loan-application/
```
**Response:** You got loan ID and plaid_link_token

---

### **Step 2: Connect Bank Account** ⏳ NEXT STEP
Use your plaid_link_token to connect bank account:

```http
POST /api/plaid/connect/
Content-Type: application/json

{
    "public_token": "public-sandbox-xxxxx",  // Get this from Plaid Link
    "loan_application_id": 1
}
```

**How to get public_token:**
1. Use your `plaid_link_token` with Plaid Link SDK/Widget
2. User completes bank authentication 
3. Plaid returns a `public_token`
4. Send that public_token to your API

---

### **Step 3: View Individual Bank Details** 
After connecting bank, users can view their details:

```http
GET /api/user/1/bank-details/
```

**Response Example:**
```json
{
    "loan_application_id": 1,
    "user_name": "string",
    "email": "Fw2pTxtWt2ZKoEH@ALShisOfFxAv.mqyo",
    "bank_accounts": [
        {
            "account_id": "xxx",
            "name": "Chase Checking",
            "current_balance": 5000.00,
            "balance_formatted": "$5,000.00"
        }
    ],
    "financial_summary": {
        "total_balance": "$5,000.00",
        "account_count": 1
    },
    "plaid_connected": true
}
```

---

### **Step 4: View Sandbox Statistics**
See all users in your system:

```http
GET /api/sandbox/stats/
```

**Response Example:**
```json
{
    "sandbox_summary": {
        "total_loan_applications": 2,
        "users_with_bank_connection": 1,
        "users_without_bank_connection": 1,
        "connection_rate": "50.0%"
    },
    "all_users": [
        {
            "loan_id": 1,
            "name": "string",
            "email": "Fw2pTxtWt2ZKoEH@ALShisOfFxAv.mqyo",
            "has_bank_connection": true
        },
        {
            "loan_id": 2,
            "name": "User Y",
            "email": "usery@example.com",
            "has_bank_connection": false
        }
    ]
}
```

## 🎯 **Your Available Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/loan-application/` | POST | Create loan (Step 1) ✅ |
| `/api/plaid/connect/` | POST | Connect bank (Step 2) |
| `/api/user/{loan_id}/bank-details/` | GET | Individual bank details |
| `/api/sandbox/stats/` | GET | System statistics |
| `/api/plaid/create-sandbox-token/` | POST | Get test public token |

## 🧪 **For Testing (Sandbox Mode):**

If you want to test without Plaid Link widget, you can:

1. **Get a sandbox public token:**
```http
POST /api/plaid/create-sandbox-token/
```

2. **Use that token to connect:**
```http
POST /api/plaid/connect/
{
    "public_token": "public-sandbox-xxxxx",  // From step 1
    "loan_application_id": 1
}
```

## 📱 **User Experience:**
- **User X (loan_id=1)**: Can see their bank details at `/api/user/1/bank-details/`
- **User Y (loan_id=2)**: Can see their bank details at `/api/user/2/bank-details/`
- **Admin**: Can see all users at `/api/sandbox/stats/`

## 🔄 **Next Action Required:**
You need to connect a bank account to see actual bank details. Use either:
- Real Plaid Link integration with your plaid_link_token
- OR sandbox public token for testing
