# Quick Start: Generate PDF from Bank Data

## Step-by-Step Guide

### 1. Make Sure Server is Running
```bash
python manage.py runserver 127.0.0.1:8000
```

### 2. Create a Loan Application

**In Postman:**
```
POST http://127.0.0.1:8000/api/loan-application/
Content-Type: application/json

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

**Save the response - you'll get:**
```json
{
  "id": 57,
  "plaid_link_token": "link-production-xxx",
  "plaid_ui_url": "http://127.0.0.1:8000/get_public_token_manual.html?..."
}
```

### 3. Connect Bank Account

1. Copy the `plaid_ui_url` from the response
2. Open it in your browser
3. Click "Open Plaid & Get Public Token"
4. Login to your REAL bank (Chase, Bank of America, etc.)
5. After successful login, click "Copy JSON for Postman"

### 4. Exchange Public Token

**In Postman:**
```
POST http://127.0.0.1:8000/api/plaid/connect/
Content-Type: application/json

{
  "public_token": "public-production-xxx",
  "loan_application_id": 57
}
```

**You'll get:**
```json
{
  "loan_application": {...},
  "bank_accounts": [...],
  "total_balance": "$10,500.00",
  "plaid_connected": true
}
```

### 5. Generate PDF Report ✨

**In Postman:**
```
POST http://127.0.0.1:8000/api/bank-analysis-pdf/
Content-Type: application/json

{
  "loan_application_id": 57
}
```

**Response:**
- Click "Send"
- Look for the download icon or "Save Response to File"
- The PDF will be downloaded as `loan_analysis_57.pdf`

---

## What's in the PDF?

✅ Applicant Information (Name, Email, Phone, Income)
✅ Loan Details (Address, Purpose, Purchase Price, Down Payment)
✅ Connected Bank Accounts with Balances
✅ Total Balance Summary
✅ AI Analysis Status (APPROVED/PENDING)

---

## Download PDF via Browser

Instead of Postman, you can also use this HTML:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Download Loan PDF</title>
</head>
<body>
    <h1>Download Loan Analysis PDF</h1>
    <input type="number" id="loanId" placeholder="Enter Loan ID" value="57">
    <button onclick="downloadPDF()">Download PDF</button>

    <script>
        function downloadPDF() {
            const loanId = document.getElementById('loanId').value;
            
            fetch('http://127.0.0.1:8000/api/bank-analysis-pdf/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ loan_application_id: parseInt(loanId) })
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `loan_analysis_${loanId}.pdf`;
                a.click();
            })
            .catch(error => alert('Error: ' + error));
        }
    </script>
</body>
</html>
```

---

## Troubleshooting

**Error: "No Plaid connection found"**
- Make sure you completed Step 4 (Exchange Public Token)
- Check the loan_application_id is correct

**Error: "Failed to fetch Plaid data"**
- Your bank connection might be expired
- Try connecting again with a new public token

**PDF is blank or incomplete**
- Check that all data was saved in Step 4
- Verify the loan has bank accounts connected

---

## What Happens Next?

The data flows through the AI PreApproval Engine which analyzes:
- Debt-to-Income ratio
- Down payment percentage
- Liquid assets
- Income verification

The AI decides: ✅ APPROVED or ⏳ PENDING REVIEW
