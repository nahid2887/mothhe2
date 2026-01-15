try:
    from plaid.api import plaid_api
    from plaid.configuration import Configuration, Environment
    from plaid.api_client import ApiClient
    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False

from django.conf import settings


def get_plaid_client():
    """Get configured Plaid API client"""
    if not PLAID_AVAILABLE:
        raise Exception("Plaid SDK not available. Install with: pip install plaid-python")
        
    if settings.PLAID_ENV == 'sandbox':
        host = Environment.Sandbox
    elif settings.PLAID_ENV == 'development':
        host = Environment.Development
    else:
        host = Environment.Production
    
    configuration = Configuration(
        host=host,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET
        }
    )
    
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)
