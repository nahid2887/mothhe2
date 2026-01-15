try:
    from plaid.api import plaid_api
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.accounts_get_request import AccountsGetRequest
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.country_code import CountryCode
    from plaid.model.products import Products
    from .plaid_utils import get_plaid_client
    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False
    print("Plaid SDK not available. Install with: pip install plaid-python")

from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PlaidService:
    def __init__(self):
        if not PLAID_AVAILABLE:
            self.client = None
            return
        # Use the working Plaid client from plaid_utils
        try:
            self.client = get_plaid_client()
        except Exception as e:
            logger.error(f"Failed to initialize Plaid client: {e}")
            self.client = None

    def create_link_token(self, user_id, user_name=None):
        """Create a link token for Plaid Link"""
        if not PLAID_AVAILABLE or not self.client:
            raise Exception("Plaid SDK not available. Install with: pip install plaid-python")
        try:
            # Use products that are enabled on the production account
            from django.conf import settings
            # Use only assets product (single flow requirement)
            products_list = [Products('assets')]
                
            request = LinkTokenCreateRequest(
                products=products_list,
                client_name="Mortgage Application",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=str(user_id))
            )
            response = self.client.link_token_create(request)
            return response['link_token']
        except Exception as e:
            logger.error(f"Error creating link token: {e}")
            raise

    def exchange_public_token(self, public_token):
        """Exchange public token for access token"""
        if not PLAID_AVAILABLE or not self.client:
            raise Exception("Plaid SDK not available. Install with: pip install plaid-python")
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            return {
                'access_token': response['access_token'],
                'item_id': response['item_id']
            }
        except Exception as e:
            logger.error(f"Error exchanging public token: {e}")
            raise

    def get_accounts(self, access_token):
        """Get account information"""
        if not PLAID_AVAILABLE or not self.client:
            raise Exception("Plaid SDK not available. Install with: pip install plaid-python")
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            return response['accounts']
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            raise

    def get_transactions(self, access_token, start_date=None, end_date=None):
        """Get transactions for the past 30 days or specified date range"""
        if not PLAID_AVAILABLE or not self.client:
            raise Exception("Plaid SDK not available. Install with: pip install plaid-python")
        try:
            if not start_date:
                start_date = datetime.now().date() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now().date()
            
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date
            )
            response = self.client.transactions_get(request)
            return response['transactions']
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise

    def create_sandbox_public_token(self, institution_id="ins_3", initial_products=None):
        """Create a sandbox public token for testing"""
        if not PLAID_AVAILABLE or not self.client:
            raise Exception("Plaid SDK not available. Install with: pip install plaid-python")
        try:
            from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
            from plaid.model.products import Products
            
            if initial_products is None:
                initial_products = [Products('transactions'), Products('auth')]
            
            request = SandboxPublicTokenCreateRequest(
                institution_id=institution_id,
                initial_products=initial_products
            )
            response = self.client.sandbox_public_token_create(request)
            return {
                'public_token': response['public_token'],
                'account_id': response['account_id'] if 'account_id' in response else None
            }
        except Exception as e:
            logger.error(f"Error creating sandbox public token: {e}")
            raise
