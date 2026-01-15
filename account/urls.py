from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.ContactUsView.as_view(), name='contact'),
    path('loan-application/', views.LoanApplicationCreateView.as_view(), name='loan-application-create'),
    #path('loan-application/<int:loan_id>/', views.GetLoanApplicationWithBankDataView.as_view(), name='loan-application-detail'),
    path('plaid/link-token/', views.PlaidLinkTokenView.as_view(), name='plaid-link-token'),
    path('plaid/connect/', views.PlaidConnectView.as_view(), name='plaid-connect'),
    path('bank-analysis-pdf/', views.BankDataAnalysisPDFView.as_view(), name='bank-analysis-pdf'),
    path('generate-pdf-from-data/', views.GeneratePDFFromBankDataView.as_view(), name='generate-pdf-from-data'),
    #path('plaid/connect-all/', views.PlaidConnectAndGetAllInfoView.as_view(), name='plaid-connect-all'),
    #path('loan-decision-pdf/<int:loan_id>/', views.LoanDecisionPDFView.as_view(), name='loan-decision-pdf'),
    #path('loan-decision-test/', views.LoanDecisionTestPageView.as_view(), name='loan-decision-test-page'),
    #path('create-test-loan/', views.CreateTestLoanView.as_view(), name='create-test-loan'),
    #path('ai-loan-decision/<int:loan_id>/', views.AILoanDecisionView.as_view(), name='ai-loan-decision'),
    #path('plaid-test/', views.PlaidTestPageView.as_view(), name='plaid-test-page'),
    
    # Get public token for testing
    #path('plaid/create-sandbox-token/', views.CreateSandboxPublicTokenView.as_view(), name='create-sandbox-token'),
    
    # New endpoints for individual user bank details and sandbox stats
    path('user/<int:loan_id>/bank-details/', views.UserBankDetailsView.as_view(), name='user-bank-details'),
    path('sandbox/stats/', views.SandboxStatsView.as_view(), name='sandbox-stats'),
]
