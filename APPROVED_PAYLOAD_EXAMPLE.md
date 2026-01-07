# ✅ Payload That Gets APPROVED

## 📋 POST Payload for Approval

This payload has **strong financial metrics** that should get **APPROVED** by the AI:

```json
{
  "loan_application_id": 100,
  "loan_application": {
    "id": 100,
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "phone_number": "555-123-4567",
    "property_zip_code": "10001",
    "property_address": "123 Park Avenue, New York, NY",
    "annual_income": "250000.00",
    "purchase_price": "500000.00",
    "down_payment": "100000.00",
    "loan_purpose": "Purchase",
    "cash_out_amount": "0.00"
  },
  "bank_accounts": [
    {
      "account_id": "plaid_acc_001",
      "name": "Premium Checking Account",
      "official_name": "Premium Checking Account",
      "type": "depository",
      "subtype": "checking",
      "current_balance": 150000,
      "available_balance": 145000,
      "currency": "USD"
    },
    {
      "account_id": "plaid_acc_002",
      "name": "Savings Account",
      "official_name": "High Yield Savings",
      "type": "depository",
      "subtype": "savings",
      "current_balance": 200000,
      "available_balance": 200000,
      "currency": "USD"
    },
    {
      "account_id": "plaid_acc_003",
      "name": "Money Market Account",
      "official_name": "Money Market Account",
      "type": "depository",
      "subtype": "money market",
      "current_balance": 100000,
      "available_balance": 100000,
      "currency": "USD"
    }
  ],
  "total_balance": "$450,000.00",
  "plaid_connected": true,
  "message": "Bank account connected successfully!"
}
```

---

## ✅ Why This Gets APPROVED

### 📊 Financial Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Annual Income** | $250,000 | ✅ Excellent |
| **Monthly Income** | $20,833 | ✅ Strong |
| **Purchase Price** | $500,000 | ✅ Reasonable |
| **Down Payment** | $100,000 (20%) | ✅ **Great** |
| **Loan Amount** | $400,000 | ✅ Manageable |
| **Debt-to-Income** | 19.2% | ✅ **Well Below 50%** |
| **Liquid Assets** | $450,000 | ✅ **Excellent** |
| **Est. Monthly Mortgage** | $2,500 | ✅ Easy to afford |

---

## 🎯 Approval Criteria Met

### ✅ Criteria 1: Debt-to-Income Ratio
```
Criteria: <= 50%
Calculation: ($400,000 × 0.5%) / $20,833 = 19.2%
Status: ✅ PASS (Well below limit)
```

### ✅ Criteria 2: Down Payment
```
Criteria: >= 3% of purchase price
Calculation: $100,000 / $500,000 = 20%
Status: ✅ PASS (Way above minimum)
```

### ✅ Criteria 3: Liquid Assets
```
Criteria: >= 1 month of estimated mortgage
Calculation: $450,000 vs $2,500 (1 month mortgage)
Status: ✅ PASS (180 months of coverage!)
```

---

## 🧪 How to Test

### Using cURL
```bash
curl -X POST http://127.0.0.1:8000/api/generate-pdf-from-data/ \
  -H "Content-Type: application/json" \
  -d '{
  "loan_application_id": 100,
  "loan_application": {
    "id": 100,
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "phone_number": "555-123-4567",
    "property_zip_code": "10001",
    "property_address": "123 Park Avenue, New York, NY",
    "annual_income": "250000.00",
    "purchase_price": "500000.00",
    "down_payment": "100000.00",
    "loan_purpose": "Purchase",
    "cash_out_amount": "0.00"
  },
  "bank_accounts": [
    {
      "account_id": "plaid_acc_001",
      "name": "Premium Checking Account",
      "official_name": "Premium Checking Account",
      "type": "depository",
      "subtype": "checking",
      "current_balance": 150000,
      "available_balance": 145000,
      "currency": "USD"
    },
    {
      "account_id": "plaid_acc_002",
      "name": "Savings Account",
      "official_name": "High Yield Savings",
      "type": "depository",
      "subtype": "savings",
      "current_balance": 200000,
      "available_balance": 200000,
      "currency": "USD"
    },
    {
      "account_id": "plaid_acc_003",
      "name": "Money Market Account",
      "official_name": "Money Market Account",
      "type": "depository",
      "subtype": "money market",
      "current_balance": 100000,
      "available_balance": 100000,
      "currency": "USD"
    }
  ],
  "total_balance": "$450,000.00",
  "plaid_connected": true,
  "message": "Bank account connected successfully!"
}' --output approved_loan.pdf
```

### Using Postman
1. **Method:** POST
2. **URL:** `http://127.0.0.1:8000/api/generate-pdf-from-data/`
3. **Body:** Copy the JSON above
4. **Send** → PDF downloads!

### Using Swagger UI
1. Go to: http://127.0.0.1:8000/swagger/
2. Find: **"Generate PDF from Bank Data (Direct)"**
3. Click: **Try it out**
4. Paste: The JSON above
5. Click: **Execute**
6. Result: PDF with **APPROVED** status! ✅

---

## 📄 Expected PDF Result

The generated PDF will show:

```
┌─────────────────────────────────┐
│   LOAN ANALYSIS REPORT          │
├─────────────────────────────────┤
│                                 │
│ APPLICANT INFORMATION           │
│ • Name: John Smith              │
│ • Email: john.smith@example.com │
│ • Phone: 555-123-4567           │
│                                 │
│ LOAN DETAILS                    │
│ • Purpose: Purchase             │
│ • Price: $500,000.00            │
│ • Down Payment: $100,000.00     │
│ • Annual Income: $250,000.00    │
│                                 │
│ BANK ACCOUNTS                   │
│ • Premium Checking: $150,000.00 │
│ • Savings Account: $200,000.00  │
│ • Money Market: $100,000.00     │
│                                 │
│ TOTAL BALANCE: $450,000.00      │
│                                 │
│ STATUS: ✅ APPROVE              │
│                                 │
└─────────────────────────────────┘
```

---

## 💰 Other Approval Scenarios

### Scenario 2: Moderate Income, Good Down Payment
```json
{
  "loan_application_id": 101,
  "loan_application": {
    "annual_income": "120000.00",
    "purchase_price": "300000.00",
    "down_payment": "60000.00"
  },
  "bank_accounts": [...],
  "total_balance": "$80,000.00"
}
```
✅ **Status:** Should APPROVE (20% down payment)

### Scenario 3: Lower Income, But Strong Assets
```json
{
  "loan_application_id": 102,
  "loan_application": {
    "annual_income": "80000.00",
    "purchase_price": "250000.00",
    "down_payment": "50000.00"
  },
  "bank_accounts": [...],
  "total_balance": "$150,000.00"
}
```
✅ **Status:** Should APPROVE (20% down + strong assets)

---

## ❌ Scenarios That Get DENIED

### Denied Example 1: Very Low Down Payment
```
Down Payment: 1% (Below 3% minimum)
Status: ❌ DENIED
```

### Denied Example 2: High Debt-to-Income
```
Annual Income: $50,000
Purchase Price: $500,000
Debt-to-Income: 80% (Way above 50%)
Status: ❌ DENIED
```

### Denied Example 3: No Liquid Assets
```
Liquid Assets: $0
Monthly Mortgage: $2,500
Asset Coverage: 0 months
Status: ❌ DENIED
```

---

## 🎉 Use the Approved Payload!

Copy the first payload and test it. You should get:
- ✅ PDF generates successfully
- ✅ PDF contains applicant info
- ✅ PDF shows **APPROVED** status
- ✅ File downloads as `approved_loan_100.pdf`

**Ready to test?** 🚀

