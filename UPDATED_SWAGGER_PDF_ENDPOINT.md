# 📄 Updated Swagger: Generate PDF from Bank Data

## 🎯 New Swagger Schema

The Swagger documentation has been updated with the **exact format** you provided.

---

## 📋 Request Format

### ✅ Copy-Paste Ready Example

Copy the exact response from `/api/plaid/connect/` and send it here:

```json
{
  "loan_application_id": 57,
  "loan_application": {
    "id": 57,
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone_number": "98788",
    "property_zip_code": "88",
    "property_address": "string",
    "annual_income": "75677.00",
    "purchase_price": "788.00",
    "down_payment": "76.00",
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
      "current_balance": 0,
      "available_balance": 0,
      "currency": "USD"
    }
  ],
  "total_balance": "$0.00",
  "plaid_connected": true,
  "message": "Bank account connected successfully!"
}
```

---

## 🔑 Required Fields

**MUST include:**
- ✅ `loan_application_id` - The ID number
- ✅ `loan_application` - Complete application object
- ✅ `bank_accounts` - Array of bank accounts
- ✅ `total_balance` - Total balance string

**Optional (can include but not required):**
- ✅ `plaid_connected` - Boolean
- ✅ `message` - Status message
- ✅ `recent_transactions` - Transaction array

---

## 🔗 Endpoint

**POST** `/api/generate-pdf-from-data/`

---

## 📊 Response

- **Status:** 200 OK
- **Content-Type:** application/pdf
- **Filename:** `loan_analysis_57.pdf`

The PDF automatically downloads with your report inside!

---

## 📖 Complete Workflow Example

### 1️⃣ Create Loan Application
```bash
curl -X POST http://127.0.0.1:8000/api/loan-application/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone_number": "98788",
    "property_zip_code": "88",
    "property_address": "string",
    "annual_income": "75677.00",
    "purchase_price": "788.00",
    "down_payment": "76.00",
    "loan_purpose": "Purchase",
    "cash_out_amount": "100.00"
  }'
```

**Response includes:** `loan_id = 57`

---

### 2️⃣ Connect Bank via Plaid
```bash
curl -X POST http://127.0.0.1:8000/api/plaid/connect/ \
  -H "Content-Type: application/json" \
  -d '{
    "public_token": "public-sandbox-xxx...",
    "loan_application_id": 57
  }'
```

**Response:** Bank account data (the JSON you showed me)

---

### 3️⃣ Generate PDF
**Copy the entire response from Step 2** and send it here:

```bash
curl -X POST http://127.0.0.1:8000/api/generate-pdf-from-data/ \
  -H "Content-Type: application/json" \
  -d '{
    "loan_application_id": 57,
    "loan_application": { ... },
    "bank_accounts": [ ... ],
    "total_balance": "$0.00",
    "plaid_connected": true,
    "message": "Bank account connected successfully!"
  }' --output loan_analysis_57.pdf
```

**Result:** PDF downloads! 🎉

---

## 🧪 Test in Swagger UI

1. Go to: http://127.0.0.1:8000/swagger/
2. Find: **"Generate PDF from Bank Data (Direct)"**
3. Click: **Try it out**
4. Paste: The JSON above
5. Click: **Execute**
6. Download: PDF appears automatically!

---

## 📋 Swagger Schema Updates

### Field Descriptions Added
- ✅ All fields now have examples
- ✅ All fields have descriptions
- ✅ Required fields marked clearly
- ✅ Optional fields documented

### New Fields Added
- ✅ `official_name` - Bank official account name
- ✅ `property_zip_code` - Property ZIP
- ✅ `property_address` - Property address
- ✅ `created_at` - Creation timestamp
- ✅ `plaid_connected` - Boolean flag
- ✅ `message` - Status message

### Better Documentation
- ✅ Emoji indicators for clarity
- ✅ Step-by-step workflow explanation
- ✅ What PDF includes listed
- ✅ Usage examples provided

---

## 🎨 PDF Report Contents

The generated PDF includes:

```
┌─────────────────────────────┐
│   LOAN ANALYSIS REPORT      │
├─────────────────────────────┤
│                             │
│ APPLICANT INFORMATION       │
│ • Name: Mr Kim              │
│ • Email: user@example.com   │
│ • Phone: 98788              │
│                             │
│ LOAN DETAILS                │
│ • Purpose: Purchase         │
│ • Price: $788.00            │
│ • Down Payment: $76.00      │
│ • Annual Income: $75677.00  │
│                             │
│ BANK ACCOUNTS               │
│ • Business Enhanced Check.  │
│   Type: Checking            │
│   Balance: $0.00            │
│                             │
│ TOTAL BALANCE: $0.00        │
│                             │
│ STATUS: PENDING ⏳          │
│                             │
└─────────────────────────────┘
```

---

## 🚀 Quick Reference

| Step | Endpoint | Method | Purpose |
|------|----------|--------|---------|
| 1 | `/api/loan-application/` | POST | Create loan app |
| 2 | `/api/plaid/connect/` | POST | Connect bank |
| 3 | `/api/generate-pdf-from-data/` | POST | Generate PDF |

---

## ✅ What's Updated

- ✅ Swagger schema completely updated
- ✅ Exact format from your data shown
- ✅ All fields documented with examples
- ✅ Required vs optional fields marked
- ✅ Better descriptions and emojis
- ✅ Copy-paste ready examples

---

## 📚 Access Updated Swagger

Go to: **http://127.0.0.1:8000/swagger/**

Look for: **"Generate PDF from Bank Data (Direct)"**

It now shows the exact format you need! ✅

---

## 💡 Pro Tips

1. **Copy-Paste Method:** Get response from `/api/plaid/connect/` → Copy → Paste in PDF endpoint
2. **Optional Fields:** You can omit `plaid_connected`, `message`, `recent_transactions`
3. **Test Anytime:** Use dummy data to test PDF generation
4. **Multiple Accounts:** Works with single or multiple bank accounts

---

## 🎉 Ready to Use!

The endpoint is now fully documented with the exact format you provided.

Test it now in Swagger UI: http://127.0.0.1:8000/swagger/ 

Look for **"📄 Generate PDF from Bank Data (Direct)"** endpoint!

