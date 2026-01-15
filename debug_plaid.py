#!/usr/bin/env python3
"""
Debug script to test Plaid token validation
"""

def validate_token_type(token):
    """Validate if token is the correct type"""
    print(f"Token received: {token[:50]}...")
    
    if token.startswith('link-sandbox-'):
        return False, "LINK TOKEN (sandbox) - Use this with Plaid Link UI first"
    elif token.startswith('link-'):
        return False, "LINK TOKEN - Use this with Plaid Link UI first"
    elif token.startswith('public-sandbox-'):
        return True, "PUBLIC TOKEN (sandbox) - Correct for token exchange"
    elif token.startswith('public-'):
        return True, "PUBLIC TOKEN - Correct for token exchange"
    else:
        return False, f"UNKNOWN TOKEN TYPE - Starts with: {token[:10]}..."

# Test with sample tokens
if __name__ == "__main__":
    # Test tokens
    test_tokens = [
        "link-sandbox-1234567890abcdef",
        "public-sandbox-1234567890abcdef", 
        "link-development-1234567890abcdef",
        "public-development-1234567890abcdef"
    ]
    
    for token in test_tokens:
        is_valid, message = validate_token_type(token)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"{status}: {message}")
        print()