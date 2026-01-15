# 🏦 Multi-User Sandbox Banking System - Complete Guide

## 🎯 What's New: Individual User Bank Accounts

Your Django API now supports **multiple users** with their **individual bank account information**. Each user can have their own unique financial profile and bank data.

---

## 🚀 Quick Start: Create Multiple Test Users

### 1. Create All Test Users at Once
**POST** `http://127.0.0.1:8000/api/sandbox/create-multiple-users/`

**No Body Required** - This will automatically create 4 different users:

```json
{
    "message": "Successfully created 4 sandbox users with bank connections",
    "users": [
        {
            "loan_application_id": 1,
            "profile_name": "wealthy_user",
            "full_name": "Michael Johnson",
            "email": "michael.johnson@example.com",
            "annual_income": "$250,000.00",
            "total_bank_balance": "$15,420.00",
            "account_count": 3,
            "plaid_profile": "wealthy"
        },
        {
            "loan_application_id": 2,
            "profile_name": "average_user", 
            "full_name": "Sarah Smith",
            "email": "sarah.smith@example.com",
            "annual_income": "$85,000.00",
            "total_bank_balance": "$3,210.00",
            "account_count": 2,
            "plaid_profile": "good"
        },
        {
            "loan_application_id": 3,
            "profile_name": "first_time_buyer",
            "full_name": "David Chen", 
            "email": "david.chen@example.com",
            "annual_income": "$65,000.00",
            "total_bank_balance": "$890.00",
            "account_count": 2,
            "plaid_profile": "student"
        },
        {
            "loan_application_id": 4,
            "profile_name": "refinance_user",
            "full_name": "Jennifer Martinez",
            "email": "jennifer.martinez@example.com", 
            "annual_income": "$110,000.00",
            "total_bank_balance": "$7,650.00",
            "account_count": 3,
            "plaid_profile": "good"
        }
    ]
}
```

---

## 📊 View All Users with Bank Data

### 2. Get All Users Overview
**GET** `http://127.0.0.1:8000/api/users/all/`

```json
{
    "total_users": 4,
    "users_with_banks": 4,
    "users_without_banks": 0,
    "users": [
        {
            "loan_application_id": 1,
            "personal_info": {
                "full_name": "Michael Johnson",
                "email": "michael.johnson@example.com",
                "phone_number": "555-100-1001",
                "annual_income": "$250,000.00"
            },
            "property_info": {
                "address": "123 Beverly Hills Blvd, Beverly Hills, CA 90210",
                "zip_code": "90210",
                "purchase_price": "$1,200,000.00",
                "down_payment": "$240,000.00",
                "loan_purpose": "Purchase"
            },
            "bank_summary": {
                "total_balance": "$15,420.00",
                "checking_balance": "$8,200.00", 
                "savings_balance": "$7,220.00",
                "account_count": 3
            },
            "accounts": [
                {
                    "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
                    "name": "Plaid Checking",
                    "type": "depository",
                    "subtype": "checking",
                    "current_balance": 8200.0,
                    "balance_formatted": "$8,200.00"
                }
            ],
            "recent_transactions": [
                {
                    "date": "2025-09-08",
                    "name": "Starbucks",
                    "amount": "$5.40",
                    "type": "debit"
                }
            ],
            "plaid_connected": true,
            "created_at": "2025-09-09T10:15:00Z"
        }
    ]
}
```

---

## 🔍 Get Individual User's Complete Bank Info

### 3. Get Detailed User Bank Information
**GET** `http://127.0.0.1:8000/api/users/{loan_application_id}/bank-info/`

**Example:** `http://127.0.0.1:8000/api/users/1/bank-info/`

```json
{
    "user_info": {
        "loan_application_id": 1,
        "full_name": "Michael Johnson",
        "email": "michael.johnson@example.com",
        "phone_number": "555-100-1001"
    },
    "bank_accounts": [
        {
            "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
            "name": "Plaid Checking",
            "official_name": "Plaid Gold Standard 0% Interest Checking",
            "type": "depository",
            "subtype": "checking",
            "balances": {
                "current": 8200.0,
                "available": 8000.0,
                "current_formatted": "$8,200.00",
                "available_formatted": "$8,000.00"
            },
            "currency": "USD"
        },
        {
            "account_id": "dVzbVMLjrxTnLjX4G66XUp5GLklm4oiZy88yK",
            "name": "Plaid Saving",
            "official_name": "Plaid Silver Standard 0.1% Interest Saving",
            "type": "depository", 
            "subtype": "savings",
            "balances": {
                "current": 7220.0,
                "available": 7220.0,
                "current_formatted": "$7,220.00",
                "available_formatted": "$7,220.00"
            },
            "currency": "USD"
        }
    ],
    "transactions": [
        {
            "transaction_id": "lPNjeW1nR6CDn5okmGQ6hEpMo4lLNoSrzqDje",
            "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
            "amount": 5.4,
            "amount_formatted": "$5.40",
            "date": "2025-09-08",
            "name": "Starbucks",
            "merchant_name": "Starbucks",
            "category": ["Food and Drink", "Restaurants"],
            "type": "debit"
        }
    ],
    "financial_summary": {
        "total_balance": "$15,420.00",
        "account_count": 2,
        "transaction_count": 15
    },
    "connection_info": {
        "connected_at": "2025-09-09T10:15:00Z",
        "item_id": "eVBnVMp7zdTJLkRNr33Rs6zr7KNJqBFL9DrE6"
    }
}
```

---

## 🎭 User Profiles & Their Bank Characteristics

### 💰 Wealthy User (Michael Johnson)
- **Profile**: `wealthy`
- **Annual Income**: $250,000
- **Bank Balance**: $15,000-$20,000 typically
- **Accounts**: Checking, Savings, Investment
- **Institution**: Chase Bank (ins_3)

### 👤 Average User (Sarah Smith)  
- **Profile**: `good`
- **Annual Income**: $85,000
- **Bank Balance**: $3,000-$5,000 typically
- **Accounts**: Checking, Savings
- **Institution**: Bank of America (ins_1)

### 🎓 First-Time Buyer (David Chen)
- **Profile**: `student`
- **Annual Income**: $65,000  
- **Bank Balance**: $800-$1,500 typically
- **Accounts**: Checking, Savings (lower balances)
- **Institution**: Wells Fargo (ins_2)

### 🏠 Refinance User (Jennifer Martinez)
- **Profile**: `good`
- **Annual Income**: $110,000
- **Bank Balance**: $7,000-$10,000 typically
- **Accounts**: Checking, Savings, Money Market
- **Institution**: Bank of America (ins_1)

---

## 🔧 Manual User Creation

### 4. Create Single User with Specific Profile
**POST** `http://127.0.0.1:8000/api/plaid/create-sandbox-token/?user_profile=wealthy`

Available profiles: `wealthy`, `good`, `student`, `bad`

```json
{
    "public_token": "public-sandbox-xxxx-xxxx-xxxx",
    "user_profile": "wealthy",
    "message": "Sandbox public token created successfully for wealthy user profile."
}
```

Then use this `public_token` with existing endpoints to connect bank accounts.

---

## 📋 Complete API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sandbox/create-multiple-users/` | POST | Create 4 different test users with banks |
| `/api/users/all/` | GET | Get all users with bank summaries |
| `/api/users/{id}/bank-info/` | GET | Get detailed bank info for specific user |
| `/api/plaid/create-sandbox-token/?user_profile=X` | POST | Create token for specific profile |
| `/api/loan-application/{id}/` | GET | Get complete user+bank data (existing) |
| `/api/plaid/connect-all/` | POST | Connect new bank to existing user (existing) |

---

## 🧪 Testing Scenarios

### Scenario 1: Multi-User Dashboard
1. Create multiple users → `POST /api/sandbox/create-multiple-users/`
2. View all users → `GET /api/users/all/`
3. Click on specific user → `GET /api/users/{id}/bank-info/`

### Scenario 2: Individual User Management
1. Create loan application → `POST /api/loan-application/`
2. Get link token → `GET /api/plaid/link-token/?loan_application_id=X`
3. Connect bank account → `POST /api/plaid/connect-all/`
4. View user's bank info → `GET /api/users/{id}/bank-info/`

### Scenario 3: Different Financial Profiles
1. Create wealthy user token → `POST /api/plaid/create-sandbox-token/?user_profile=wealthy`
2. Create student user token → `POST /api/plaid/create-sandbox-token/?user_profile=student`
3. Compare their bank balances and account types

---

## 🎯 Key Features

✅ **Individual User Accounts** - Each user has separate bank connections  
✅ **Multiple Financial Profiles** - Wealthy, average, student, problematic users  
✅ **Realistic Bank Data** - Different institutions, balances, transaction patterns  
✅ **Complete User Overview** - See all users at once or drill down to individuals  
✅ **Sandbox Testing** - Safe environment with fake but realistic data  
✅ **Scalable Architecture** - Easy to add more users and profiles  

---

## 🔍 Database Structure

Each user gets:
- **LoanApplication** record (personal/property info)
- **PlaidConnection** record (access_token, item_id)
- **Individual bank accounts** via Plaid API
- **Individual transactions** via Plaid API

Users are completely separate - no shared data between them.

---

## 💡 Usage Tips

1. **Start with bulk creation**: Use `create-multiple-users` to get started quickly
2. **Use profile-specific tokens**: Different profiles give different bank characteristics  
3. **Individual user focus**: Each user can be managed independently
4. **Real-time data**: Bank balances and transactions are fetched fresh from Plaid
5. **Testing flexibility**: Mix and match different user types for comprehensive testing

---

Your multi-user sandbox banking system is now ready! 🎉
