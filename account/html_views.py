from django.http import FileResponse
from django.conf import settings
import os

def serve_plaid_html(request):
    """Serve the get_public_token_manual.html file"""
    file_path = os.path.join(settings.BASE_DIR, 'get_public_token_manual.html')
    return FileResponse(open(file_path, 'rb'), content_type='text/html')

def serve_plaid_working_html(request):
    """Serve the plaid_working.html file"""
    file_path = os.path.join(settings.BASE_DIR, 'plaid_working.html')
    return FileResponse(open(file_path, 'rb'), content_type='text/html')
