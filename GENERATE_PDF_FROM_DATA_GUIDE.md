# 📄 Generate PDF from Bank Data

## Overview

You now have a new API endpoint that generates a PDF directly from bank data **without requiring a Plaid connection**. This is perfect for:

- ✅ Testing PDF generation with dummy/test data
- ✅ Generating PDFs after getting bank data from `/api/plaid/connect/`
- ✅ Manual PDF generation workflows

---

## New Endpoint

**POST** `/api/generate-pdf-from-data/`

---

## How to Use It

### Step 1: Get Bank Data

First, connect to your bank via Plaid and get this response:

```json
{
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

### Step 2: Send to PDF Generation Endpoint

Take that exact data and send it to the new endpoint:

**POST** `/api/generate-pdf-from-data/`

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
    "cash_out_amount": "100.00"
  },
  "bank_accounts": [
    {
      "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
      "name": "Business Enhanced Checking",
      "type": "depository",
      "subtype": "checking",
      "current_balance": 0,
      "available_balance": 0,
      "currency": "USD"
    }
  ],
  "total_balance": "$0.00"
}
```

### Step 3: Download PDF

Response:
- **Status:** 200 OK
- **Content-Type:** application/pdf
- **Filename:** `loan_analysis_57.pdf`

The PDF will automatically download with the analysis report inside!

---

## Complete Workflow

### Using cURL (Terminal)

```bash
curl -X POST http://127.0.0.1:8000/api/generate-pdf-from-data/ \
  -H "Content-Type: application/json" \
  -d '{
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
      "loan_purpose": "Purchase"
    },
    "bank_accounts": [
      {
        "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
        "name": "Business Enhanced Checking",
        "type": "depository",
        "subtype": "checking",
        "current_balance": 0,
        "available_balance": 0,
        "currency": "USD"
      }
    ],
    "total_balance": "$0.00"
  }' --output loan_analysis.pdf
```

### Using Postman

1. Create new **POST** request
2. URL: `http://127.0.0.1:8000/api/generate-pdf-from-data/`
3. Body: Select **raw** → **JSON** → Paste the JSON above
4. Click **Send**
5. PDF will download automatically

### Using Python

```python
import requests
import json

url = "http://127.0.0.1:8000/api/generate-pdf-from-data/"

data = {
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
        "loan_purpose": "Purchase"
    },
    "bank_accounts": [
        {
            "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
            "name": "Business Enhanced Checking",
            "type": "depository",
            "subtype": "checking",
            "current_balance": 0,
            "available_balance": 0,
            "currency": "USD"
        }
    ],
    "total_balance": "$0.00"
}

response = requests.post(url, json=data)

# Save PDF
with open("loan_analysis.pdf", "wb") as f:
    f.write(response.content)

print("PDF saved successfully!")
```

### Using JavaScript (Browser)

```javascript
const data = {
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
        "loan_purpose": "Purchase"
    },
    "bank_accounts": [
        {
            "account_id": "5wze81omExtjBKjob51Zukxwqd1OQmi4dOVxj",
            "name": "Business Enhanced Checking",
            "type": "depository",
            "subtype": "checking",
            "current_balance": 0,
            "available_balance": 0,
            "currency": "USD"
        }
    ],
    "total_balance": "$0.00"
};

fetch('http://127.0.0.1:8000/api/generate-pdf-from-data/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => response.blob())
.then(blob => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'loan_analysis_57.pdf';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
});
```

---

## What the PDF Contains

The generated PDF includes:

✅ **Applicant Information**
- Name
- Email
- Phone

✅ **Loan Details**
- Purpose
- Purchase Price
- Down Payment
- Annual Income

✅ **Bank Accounts**
- Account names and types
- Current balances
- Total balance

✅ **AI Analysis Decision**
- APPROVED (Green)
- PENDING (Yellow)
- DENIED (Red)

---

## 3-Step Complete Workflow

### Step 1: Create Loan Application
```bash
POST /api/loan-application/
```
Response includes `loan_application_id: 57`

### Step 2: Connect Bank Account
```bash
POST /api/plaid/connect/
```
Response includes bank data

### Step 3: Generate PDF
```bash
POST /api/generate-pdf-from-data/
```
Send the bank data from Step 2 + get PDF!

---

## Error Handling

### Missing Required Fields
```json
{
  "error": "Missing required fields: loan_application_id, loan_application, bank_accounts"
}
```

**Solution:** Make sure all required fields are present in the request

### Server Error
```json
{
  "error": "Failed to generate PDF: [error details]"
}
```

**Solution:** Check the error message and Django logs

---

## API Documentation

Access the full API documentation at:

- **Swagger UI:** http://127.0.0.1:8000/swagger/
- **ReDoc:** http://127.0.0.1:8000/redoc/

Look for **"Generate PDF from Bank Data (Direct)"** endpoint

---

## Testing

### Quick Test with Swagger UI

1. Go to http://127.0.0.1:8000/swagger/
2. Find **"Generate PDF from Bank Data (Direct)"** endpoint
3. Click **Try it out**
4. Paste the JSON above
5. Click **Execute**
6. Click **Download file** to get PDF

---

## Summary

✅ New endpoint created: `/api/generate-pdf-from-data/`  
✅ Takes bank data from `/api/plaid/connect/`  
✅ Generates professional PDF with AI analysis  
✅ Works with dummy/test data  
✅ No Plaid connection required for PDF generation  
✅ Fully documented in Swagger UI  

**Ready to test!** 🎉

