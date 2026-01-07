# 🎯 Complete Terminal Workflow - WORKING EXAMPLE

## ✅ **Successfully Demonstrated Terminal Workflow:**

### **1. Setup & Start Server:**
```powershell
cd c:\mothyedward
C:/mothyedward/venv/Scripts/python.exe manage.py runserver
# ✅ Server running at: http://127.0.0.1:8000/
```

### **2. Create Users (Loan Applications):**
```powershell
# Create User X (John Doe) - loan_id: 2
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/loan-application/" -Method POST -ContentType "application/json" -Body '{"full_name": "John Doe", "email": "johndoe@example.com", "phone_number": "555-123-4567", "property_zip_code": "12345", "property_address": "123 Main St", "loan_purpose": "Purchase", "purchase_price": "300000", "down_payment": "60000", "annual_income": "80000"}'

# Create User Y (Jane Smith) - loan_id: 3  
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/loan-application/" -Method POST -ContentType "application/json" -Body '{"full_name": "Jane Smith", "email": "janesmith@example.com", "phone_number": "555-987-6543", "property_zip_code": "67890", "property_address": "456 Oak Ave", "loan_purpose": "Refinance", "purchase_price": "250000", "down_payment": "50000", "annual_income": "75000"}'
```

### **3. Check System Statistics:**
```powershell
# See all users in sandbox
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/sandbox/stats/" -Method GET; $response | ConvertTo-Json -Depth 5
```
**Result:** 3 users total, 0 connections initially

### **4. Get Sandbox Token for Testing:**
```powershell
# Get public token for testing
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/plaid/create-sandbox-token/" -Method POST; $response | ConvertTo-Json
```
**Result:** `"public_token": "public-sandbox-cd2df41b-2deb-4fd0-9268-d131db9a9154"`

### **5. Connect Bank Account:**
```powershell
# Connect John Doe's bank account (loan_id: 2)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/plaid/connect/" -Method POST -ContentType "application/json" -Body '{"public_token": "public-sandbox-cd2df41b-2deb-4fd0-9268-d131db9a9154", "loan_application_id": 2}'
```
**Result:** ✅ Bank connected successfully with multiple accounts and $213,535.80 total balance

### **6. View Individual Bank Details:**
```powershell
# User X with bank connection (John Doe - loan_id: 2)
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/user/2/bank-details/" -Method GET; $response | ConvertTo-Json -Depth 4

# User Y without bank connection (Jane Smith - loan_id: 3)  
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/user/3/bank-details/" -Method GET; $response | ConvertTo-Json -Depth 3
```

### **7. Final Statistics Check:**
```powershell
# Updated stats after connection
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/sandbox/stats/" -Method GET; $response | ConvertTo-Json -Depth 5
```

## 📊 **Final Results:**

### **Sandbox Summary:**
- **Total Users:** 3
- **Connected Users:** 1 (33.3% connection rate)
- **John Doe (loan_id=2):** ✅ Connected with 12 accounts, $213,535.80 total
- **Jane Smith (loan_id=3):** ❌ Not connected
- **Original User (loan_id=1):** ❌ Not connected

### **John Doe's Bank Accounts:**
1. **Plaid Checking:** $110.00
2. **Plaid Savings:** $210.00  
3. **Plaid CD:** $1,000.00
4. **Plaid Credit Card:** $410.00
5. **Plaid Money Market:** $43,200.00
6. **Plaid IRA:** $320.76
7. **Plaid 401k:** $23,631.98
8. **Plaid Student Loan:** $65,262.00
9. **Plaid Mortgage:** $56,302.06
10. **Plaid HSA:** $6,009.00
11. **Plaid Cash Management:** $12,060.00
12. **Plaid Business Credit Card:** $5,020.00

## 🎯 **Key Endpoints Working:**

| Endpoint | Method | Status | Purpose |
|----------|--------|--------|---------|
| `/api/loan-application/` | POST | ✅ | Create loan application |
| `/api/sandbox/stats/` | GET | ✅ | View all users & statistics |
| `/api/user/{loan_id}/bank-details/` | GET | ✅ | Individual user bank details |
| `/api/plaid/create-sandbox-token/` | POST | ✅ | Get test token |
| `/api/plaid/connect/` | POST | ✅ | Connect bank account |

## 🚀 **Your Application is Working Perfectly!**

Users can now:
- ✅ Create loan applications
- ✅ Connect their bank accounts  
- ✅ View their individual bank details by loan ID
- ✅ Admins can see sandbox statistics with all users

**Next Steps:** 
- Add more users to test the system
- Connect more bank accounts
- Use the individual bank details endpoints for your frontend
