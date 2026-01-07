# Bank Data Analysis & PDF Generation API

## Overview
This API processes Plaid bank connection data through an AI engine and generates a professional PDF report.

## Endpoint: Generate Bank Analysis PDF

### URL
```
POST /api/bank-analysis-pdf/
```

### Description
Analyzes connected bank data using the AI PreApproval Engine and generates a downloadable PDF report.

### Request Body
```json
{
  "loan_application_id": 57
}
```

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| loan_application_id | integer | Yes | The ID of the loan application with connected Plaid account |

### Success Response (200)
- **Content-Type**: `application/pdf`
- **Response**: PDF file for download
- **Filename**: `loan_analysis_57.pdf`

### Error Responses

**400 Bad Request**
```json
{
  "error": "loan_application_id is required"
}
```

**404 Not Found**
```json
{
  "error": "No Plaid connection found for this loan"
}
```

**500 Server Error**
```json
{
  "error": "Failed to fetch Plaid data: [error details]"
}
```

---

## Complete Workflow

### Step 1: Create Loan Application
```bash
curl -X POST http://127.0.0.1:8000/api/loan-application/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Mr Kim",
    "email": "user@example.com",
    "phone": "98788",
    "property_address": "123 Main St",
    "property_zip": "88",
    "loan_purpose": "Purchase",
    "purchase_price": "500000",
    "down_payment": "100000"
  }'
```

**Response:**
```json
{
  "id": 57,
  "full_name": "Mr Kim",
  "email": "user@example.com",
  "plaid_link_token": "link-production-xxx...",
  "plaid_ui_url": "http://127.0.0.1:8000/get_public_token_manual.html?token=link-production-xxx...&loan_id=57"
}
```

### Step 2: Connect Bank Account
1. Open the `plaid_ui_url` from Step 1 response
2. Click "Open Plaid & Get Public Token"
3. Login to your real bank account in the Plaid popup
4. Copy the public token when ready

### Step 3: Exchange Public Token
```bash
curl -X POST http://127.0.0.1:8000/api/plaid/connect/ \
  -H "Content-Type: application/json" \
  -d '{
    "public_token": "public-production-xxx...",
    "loan_application_id": 57
  }'
```

**Response:**
```json
{
  "loan_application": {...},
  "bank_accounts": [...],
  "total_balance": "$10,500.00",
  "plaid_connected": true
}
```

### Step 4: Generate PDF Report
```bash
curl -X POST http://127.0.0.1:8000/api/bank-analysis-pdf/ \
  -H "Content-Type: application/json" \
  -d '{
    "loan_application_id": 57
  }' \
  --output loan_analysis_57.pdf
```

---

## PDF Report Contents

The generated PDF includes:

1. **Applicant Information**
   - Full Name
   - Email
   - Phone Number
   - Annual Income

2. **Loan Details**
   - Property Address
   - Loan Purpose
   - Purchase Price
   - Down Payment

3. **Connected Bank Accounts**
   - Account Name
   - Account Type
   - Current Balance
   - Currency

4. **Summary**
   - Total Balance across all accounts
   - Transaction Count
   - AI Analysis Status (APPROVED/PENDING REVIEW)

---

## Example Usage in Python

```python
import requests
import json

# Step 1: Create Loan Application
loan_response = requests.post(
    'http://127.0.0.1:8000/api/loan-application/',
    headers={'Content-Type': 'application/json'},
    json={
        "full_name": "Mr Kim",
        "email": "user@example.com",
        "phone": "98788",
        "property_address": "123 Main St",
        "property_zip": "88",
        "loan_purpose": "Purchase",
        "purchase_price": "500000",
        "down_payment": "100000"
    }
)

loan_data = loan_response.json()
loan_id = loan_data['id']
print(f"Loan created: {loan_id}")
print(f"Plaid UI: {loan_data['plaid_ui_url']}")

# Step 2: User manually connects bank and gets public token
# (Open the plaid_ui_url in browser)

# Step 3: Exchange public token
connect_response = requests.post(
    'http://127.0.0.1:8000/api/plaid/connect/',
    headers={'Content-Type': 'application/json'},
    json={
        "public_token": "public-production-xxx...",
        "loan_application_id": loan_id
    }
)

print(f"Connected: {connect_response.status_code}")

# Step 4: Generate PDF
pdf_response = requests.post(
    'http://127.0.0.1:8000/api/bank-analysis-pdf/',
    headers={'Content-Type': 'application/json'},
    json={"loan_application_id": loan_id}
)

if pdf_response.status_code == 200:
    with open(f'loan_analysis_{loan_id}.pdf', 'wb') as f:
        f.write(pdf_response.content)
    print(f"PDF saved: loan_analysis_{loan_id}.pdf")
else:
    print(f"Error: {pdf_response.text}")
```

---

## Example Usage in JavaScript/Fetch

```javascript
async function generateLoanPDF(loanId) {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/bank-analysis-pdf/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loan_application_id: loanId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `loan_analysis_${loanId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('Error generating PDF:', error);
    }
}

// Usage
generateLoanPDF(57);
```

---

## Notes

- The AI engine analyzes the financial data to make an approval/disapproval decision
- The PDF is generated with professional formatting
- Bank data is fetched from Plaid in real-time
- Ensure the loan has an active Plaid connection before generating the PDF
- The PDF includes sensitive financial information - handle securely
