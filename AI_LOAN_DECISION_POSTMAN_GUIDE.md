# AI Loan Decision API - Postman Testing Guide

## Endpoint
`POST /account/ai-loan-decision/{loan_id}/`

## Description
The AI Loan Decision endpoint now supports POST method and can accept custom data for testing purposes. You can either:
1. Use an existing loan_id and let the system fetch data from the database
2. Provide custom `user_input` and `plaid_data` in the request body for testing

## Method 1: Using Database Loan (loan_id required)
**URL:** `POST http://localhost:8000/account/ai-loan-decision/1/`
**Body:** Empty or minimal data
The system will fetch loan data from the database using the loan_id.

## Method 2: Custom Data Testing (for Postman)
**URL:** `POST http://localhost:8000/account/ai-loan-decision/999/`
**Headers:** 
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "user_input": {
        "full_name": "John Smith",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "property_zip": "19104",
        "property_address": "123 Main St, Pennsylvania",
        "loan_purpose": "Purchase",
        "purchase_price": "$455,000",
        "down_payment": "$100,000"
    },
    "plaid_data": {
        "loan_details": {
            "purpose": "Purchase",
            "purchase_price": "$455,000",
            "down_payment": "$100,000",
            "cash_out_amount": "$1,000",
            "annual_income": "$78,000"
        },
        "financial_summary": {
            "total_balance": "$213,535.80",
            "checking_balance": "$50,000.00",
            "savings_balance": "$163,535.80",
            "account_count": 3
        },
        "analysis": {
            "monthly_income": "$6,500.00",
            "debt_to_income_estimate": "15.3%",
            "down_payment_percentage": "22.0%",
            "liquid_assets": "$213,535.80"
        }
    }
}
```

## Expected Response (for custom data testing)
```json
{
    "decision": "approve",
    "user_input": {
        "full_name": "John Smith",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "property_zip": "19104",
        "property_address": "123 Main St, Pennsylvania",
        "loan_purpose": "Purchase",
        "purchase_price": "$455,000",
        "down_payment": "$100,000"
    },
    "plaid_data": {
        // ... same plaid_data as provided
    },
    "message": "AI Decision: approve"
}
```

## Testing with Different Scenarios

### Scenario 1: High Income, Good Down Payment (Should Approve)
```json
{
    "user_input": {
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "phone": "555-123-4567",
        "property_zip": "90210",
        "property_address": "456 Beverly Hills, CA",
        "loan_purpose": "Purchase",
        "purchase_price": "$500,000",
        "down_payment": "$100,000"
    },
    "plaid_data": {
        "loan_details": {
            "annual_income": "$120,000"
        },
        "analysis": {
            "monthly_income": "$10,000.00",
            "debt_to_income_estimate": "25.0%",
            "down_payment_percentage": "20.0%",
            "liquid_assets": "$250,000.00"
        }
    }
}
```

### Scenario 2: Low Income, Small Down Payment (Should Disapprove)
```json
{
    "user_input": {
        "full_name": "Bob Wilson",
        "email": "bob@example.com",
        "phone": "555-987-6543",
        "property_zip": "12345",
        "property_address": "789 Small Town, TX",
        "loan_purpose": "Purchase",
        "purchase_price": "$300,000",
        "down_payment": "$10,000"
    },
    "plaid_data": {
        "loan_details": {
            "annual_income": "$35,000"
        },
        "analysis": {
            "monthly_income": "$2,916.67",
            "debt_to_income_estimate": "45.0%",
            "down_payment_percentage": "3.3%",
            "liquid_assets": "$15,000.00"
        }
    }
}
```

## Notes
- When using custom data (Method 2), the response is JSON instead of PDF
- When using database loan (Method 1), the response is a PDF file
- The AI engine (`aiengine.py`) receives the exact data format shown above
- The loan_id in the URL can be any number when using custom data - it's not used for lookup
