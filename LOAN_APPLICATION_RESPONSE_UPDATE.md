# Loan Application API Response Update

## Endpoint
`POST /account/loan-application/`

## Description
The loan application creation endpoint now returns the complete `user_input` data in the response format required for the AI engine.

## Request Body Example
```json
{
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "phone_number": "123-456-7890",
    "property_zip_code": "19104",
    "property_address": "123 Main St, Pennsylvania",
    "loan_purpose": "Purchase",
    "purchase_price": "455000",
    "down_payment": "100000",
    "cash_out_amount": null,
    "annual_income": "78000"
}
```

## Response Format
```json
{
    "id": 1,
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "plaid_link_token": "link-sandbox-12345...",
    "user_input": {
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "123-456-7890",
        "property_zip": "19104",
        "property_address": "123 Main St, Pennsylvania",
        "loan_purpose": "Purchase",
        "purchase_price": "455000",
        "down_payment": "100000"
    },
    "message": "Loan application created successfully. Use the plaid_link_token to connect your bank account."
}
```

## Key Changes
1. Added `user_input` object to the response
2. The `user_input` format matches exactly what the AI engine expects
3. Field names are mapped correctly (e.g., `phone_number` → `phone`, `property_zip_code` → `property_zip`)
4. Values are converted to strings as expected by the AI engine
5. Updated Swagger documentation to reflect the new response structure

## Usage
- Create a loan application using this endpoint
- Extract the `user_input` from the response
- Use this `user_input` directly with the AI loan decision endpoint
- No need to reformat the data between API calls
